# Rerun each stage of the current catalog chain unchanged, each from the
# on-disk input of that stage, and diff its output against the on-disk file:
#   merge     cat_handler.merge_catalogs          gcmt + anss + gem -> cat_merged
#   enrich    get_moment_and_relocate             integrated + mechanisms -> cat_integrated_relocated
#   classify  classify_events                     -> cat_classified, cat_<class>
#   potin     the Potin relocation the enrich step computes but does not write,
#             classified, against the reference classified catalog
# Outputs (out/<stage>/): the stage files, diff_events.csv; out/diff.txt, out/inputs.json

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / "out"
CAMP = REPO / "psha_chile5" / "outputs"
TOL = 1e-6
KEY = ["time_iso", "mag", "depth", "class"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    df = pd.read_csv(p, dtype={"id": str}, low_memory=False)
    df["id"] = df["id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return df


def diff(a, b):
    """
    Event-level diff of two catalogs matched by id.

    Numbers are compared to TOL where both sides parse as numbers, text
    otherwise, so "relocated" in an error column compares as text.

    Parameters
    ----------
    a, b : DataFrame
        Reference and new catalog, id as str.

    Returns
    -------
    ev : DataFrame
        One row per id present in one catalog only or with any changed field.
    info : dict
        Duplicated ids, columns present on one side, changes per field,
        class transitions of the matched events.
    """
    dup = {n: sorted(d.loc[d["id"].duplicated(keep=False), "id"].unique()) for n, d in (("ref", a), ("new", b))}
    ia, ib = set(a["id"]), set(b["id"])
    cols = [c for c in a.columns if c in b.columns and c != "id"]
    m = a.drop_duplicates("id").merge(b.drop_duplicates("id"), on="id", suffixes=("_a", "_b"))
    ch = {}
    for f in cols:
        x, y = m[f + "_a"], m[f + "_b"]
        xn, yn = pd.to_numeric(x, errors="coerce"), pd.to_numeric(y, errors="coerce")
        xs, ys = x.fillna("").astype(str).str.strip(), y.fillna("").astype(str).str.strip()
        num = (xn.notna() & yn.notna()).to_numpy()
        ch[f] = np.where(num, (xn - yn).abs().to_numpy() > TOL, (xs != ys).to_numpy())
    ch = pd.DataFrame(ch, index=m.index)
    hit = ch.any(axis=1)

    rows = []
    for _, r in m[hit].iterrows():
        f = [k for k in cols if ch.at[r.name, k]]
        rows.append({"id": r["id"], "kind": "changed", **{k: r.get(k + "_b") for k in KEY[:3]},
                     "class_ref": r.get("class_a"), "class_new": r.get("class_b"),
                     "fields": ";".join(f),
                     "detail": ";".join(f"{k}:{r[k + '_a']}->{r[k + '_b']}" for k in f if k not in ("class", "class_raw"))})
    for n, d, ids in (("ref_only", a, ia - ib), ("new_only", b, ib - ia)):
        for _, r in d[d["id"].isin(ids)].iterrows():
            rows.append({"id": r["id"], "kind": n, **{k: r.get(k) for k in KEY[:3]},
                         "class_ref": r.get("class") if n == "ref_only" else None,
                         "class_new": r.get("class") if n == "new_only" else None,
                         "fields": "", "detail": ""})
    ev = pd.DataFrame(rows, columns=["id", "kind"] + KEY[:3] + ["class_ref", "class_new", "fields", "detail"])
    ev = ev.sort_values(["kind", "mag"], ascending=[True, False], ignore_index=True)
    info = {"n": (len(a), len(b)), "dup": dup, "only": (len(ia - ib), len(ib - ia)),
            "cols_ref_only": [c for c in a.columns if c not in b.columns],
            "cols_new_only": [c for c in b.columns if c not in a.columns],
            "per_field": ch.sum().loc[lambda s: s > 0].sort_values(ascending=False),
            "moves": pd.crosstab(m["class_a"], m["class_b"]) if "class_a" in m else None}
    return ev, info


def report(title, info, ev, mmin=5.5):
    t = [f"## {title}",
         f"rows ref / new: {info['n'][0]} / {info['n'][1]}",
         f"ids only in ref / new: {info['only'][0]} / {info['only'][1]}",
         f"duplicated ids ref: {info['dup']['ref'][:20]} new: {info['dup']['new'][:20]}",
         f"columns only in ref: {info['cols_ref_only']}  only in new: {info['cols_new_only']}",
         "changed values per field:", info["per_field"].to_string() if len(info["per_field"]) else "  none"]
    mv = info["moves"]
    if mv is not None:
        off = mv.copy()
        for k in set(off.index) & set(off.columns):
            off.loc[k, k] = 0
        t += ["class moves (rows ref, columns new), off-diagonal:",
              off.loc[off.sum(axis=1) > 0, off.sum(axis=0) > 0].to_string() if off.values.sum() else "  none"]
    big = ev[pd.to_numeric(ev["mag"], errors="coerce") >= mmin]
    t += [f"events with M >= {mmin} in the diff: {len(big)}",
          big.drop(columns="detail").to_string(index=False) if len(big) else "", ""]
    return "\n".join(t)


STAGES = ["merge", "enrich", "classify", "potin"]
MERGE_PREF = {"anss": 0, "gcmt": 1, "gem": 2}


def classify(ce, P, src, od):
    arc = ce.load_union(str(P.intraarc_shp))
    tr = ce.load_union(str(P.trench_shp))
    thk = str(P.slab_thk) if hasattr(P, "slab_thk") else None
    slab = ce.load_slab_xyz(str(P.slab_depth), str(P.slab_strike), str(P.slab_dip), thk)
    df = ce.classify_catalog(str(src), str(od / "cat_classified.csv"), arc, tr, slab)
    for k in ce.FINAL_CLASSES:
        df[df["class"] == k].to_csv(od / f"cat_{k}.csv", index=False)


def errs(p):
    d = pd.read_csv(p, low_memory=False, usecols=["depth_error"])["depth_error"].astype(str).str.strip().str.lower()
    return f"depth_error: relocated {int((d == 'relocated').sum())}, default {int((d == 'default').sum())}, of {len(d)}"


def main():
    sys.path.insert(0, str(REPO))
    from cat_no_mech_handler import paths as P
    from cat_no_mech_handler import classify_events as ce
    from cat_no_mech_handler import get_moment_and_relocate as gm

    OUT.mkdir(exist_ok=True)
    thk = P.slab_thk if hasattr(P, "slab_thk") else None
    src = {"integrated": P.cat_integrated, "gcmt": P.cat_gcmt, "anss": P.cat_anss, "gem": P.cat_gem,
           "merged": P.cat_merged, "potin": P.cat_potin, "relocated": P.cat_integrated_relocated,
           "classified": P.cat_classified, "slab_depth": P.slab_depth, "slab_thk": thk,
           "intraarc": P.intraarc_shp, "trench": P.trench_shp}
    (OUT / "inputs.json").write_text(json.dumps(
        {k: {"path": str(v), "sha256": sha(v) if v and Path(v).exists() else None} for k, v in src.items()}, indent=1))
    t = ["# reproduction of the catalog chain, stage by stage", ""]
    for st in STAGES:
        od = OUT / st
        od.mkdir(exist_ok=True)
        if st == "merge":
            from cat_handler import merge_catalogs as mg
            mg.merge_and_label({"gcmt": str(P.cat_gcmt), "anss": str(P.cat_anss), "gem": str(P.cat_gem)},
                               str(od / "cat_merged.csv"), str(od / "cat_full.csv"), 120.0, 80.0, 0.8, MERGE_PREF)
            ref, new = P.cat_merged, od / "cat_merged.csv"
        elif st == "enrich":
            gm.enrich_and_relocate_integrated(str(P.cat_integrated), str(P.cat_merged), str(P.cat_potin),
                                              str(od / "cat_integrated_relocated.csv"))
            ref, new = P.cat_integrated_relocated, od / "cat_integrated_relocated.csv"
        elif st == "classify":
            classify(ce, P, P.cat_integrated_relocated, od)
            ref, new = P.cat_classified, od / "cat_classified.csv"
        else:
            filled = gm.attach_mt_from_catalog(pd.read_csv(P.cat_integrated), pd.read_csv(P.cat_merged))
            gm.relocate_with_potin_df(filled, pd.read_csv(P.cat_potin)).to_csv(od / "cat_integrated_potin.csv", index=False)
            classify(ce, P, od / "cat_integrated_potin.csv", od)
            ref, new = P.cat_classified, od / "cat_classified.csv"
        ev, info = diff(read(ref), read(new))
        ev.to_csv(od / "diff_events.csv", index=False)
        t += [report(f"{st}: {ref} vs out/{st}/{Path(new).name}", info, ev)]
        if st in ("enrich", "potin"):
            t += [f"on disk   {errs(P.cat_integrated_relocated)}",
                  f"rerun     {errs(od / ('cat_integrated_relocated.csv' if st == 'enrich' else 'cat_integrated_potin.csv'))}", ""]

    a = read(P.cat_classified)
    ev, info = diff(a[a["class"] == "slab_interface"], read(P.cat_slab_interface))
    ev.to_csv(OUT / "diff_interface_file.csv", index=False)
    t += [report("reference combined file, slab_interface rows vs cat_slab_interface.csv", info, ev)]
    fp = [f"{f.relative_to(CAMP)}: {json.loads(f.read_text()).get('sha256')}"
          for f in sorted(CAMP.glob("*/ref/decluster/input.json"))]
    t += ["## inputs read by the psha_chile5 reference runs (sha256[:16])", *fp,
          f"cat_classified.csv on disk: {sha(P.cat_classified)[:16]}",
          f"cat_slab_interface.csv on disk: {sha(P.cat_slab_interface)[:16]}"]
    (OUT / "diff.txt").write_text("\n".join(t) + "\n")
    print("\n".join(t))


if __name__ == "__main__":
    STAGES = sys.argv[1:] or STAGES
    main()
