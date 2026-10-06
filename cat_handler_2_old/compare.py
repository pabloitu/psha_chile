# Old classified catalog (cat_no_mech_handler) against the new catalog.csv, on
# common ground: Cabello magnitude above MMIN on both sides (mag_cabello, so the
# Ruiz and Madariaga magnitudes do not move events between bins), the time span
# and the lon/lat box the old catalog covers, and classes grouped into the source
# families the hazard model reads. The old catalog still holds duplicates; its
# rows are also counted after mapping each row to the new event it was merged
# into, so the dedup and the classification effects are shown apart.
# Writes results/cat_handler_2/compare/: compare.txt, compare.png, changes.csv

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cat_handler_2 import config as C

OUT = C.OUT / "compare"
FAMILY = {"slab_interface": "interface", "patagonia_interface": "interface",
          "intra_slab": "in-slab", "slab_deep": "in-slab", "deep_nest": "in-slab",
          "forearc": "crustal", "intraarc": "crustal", "backarc": "crustal", "patagonia_crustal": "crustal",
          "unclassified": "crustal", "south_crustal": "crustal",
          "outer_rise": "excluded", "deep_unknown": "excluded", "unresolved": "excluded"}
FAMS = ["interface", "in-slab", "crustal", "excluded"]
MB = [3.9, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 10.0]


def main(old_path=None, new_path=None):
    OUT.mkdir(parents=True, exist_ok=True)
    old = pd.read_csv(old_path or C.OLD_CLASSIFIED, dtype={"id": str}, low_memory=False)
    new = pd.read_csv(new_path or C.OUT / "catalog.csv", dtype={"id": str}, low_memory=False)
    new["m0"] = new["mag_cabello"] if "mag_cabello" in new else new["mag"]
    old["m0"] = old["mag"]
    for d in (old, new):
        d["year"] = pd.to_numeric(d["time_iso"].astype(str).str[:4], errors="coerce")
        d["family"] = d["class"].map(FAMILY).fillna("excluded")

    y0, y1 = max(old["year"].min(), new["year"].min()), min(old["year"].max(), new["year"].max())
    box = (old["longitude"].min(), old["longitude"].max(), old["latitude"].min(), old["latitude"].max())
    common = lambda d: d[(d["m0"] > C.MMIN) & d["year"].between(y0, y1) & d["longitude"].between(*box[:2])
                         & d["latitude"].between(*box[2:])].copy()
    o, n = common(old), common(new)

    kept = {m: k for k, ids in zip(new["id"], new["dup_ids"].fillna("")) for m in ids.split(";") if m}
    kept.update({k: k for k in new["id"]})
    o["new_id"] = o["id"].map(kept)
    od = o.dropna(subset=["new_id"]).drop_duplicates("new_id")

    t = ["# old classified catalog vs new catalog.csv",
         f"common ground: Cabello magnitude > {C.MMIN}, years {y0:.0f}-{y1:.0f}, "
         f"lon {box[0]:.2f} to {box[1]:.2f}, lat {box[2]:.2f} to {box[3]:.2f}",
         f"old rows {len(o)} (of {len(old)}); old rows found in the new catalog {o['new_id'].notna().sum()}, "
         f"as {len(od)} distinct new events (the rest of the old rows were duplicates); new events {len(n)} (of {len(new)})",
         "",
         "## events per family (old rows / old after dedup / new)"]
    rows = []
    for lo_, hi in zip(MB[:-1], MB[1:]):
        r = {"M": f"{lo_}-{hi}"}
        for f in FAMS:
            r[f] = "{} / {} / {}".format(*(int(((d["m0"] > lo_) & (d["m0"] <= hi) & (d["family"] == f)).sum()) for d in (o, od, n)))
        rows.append(r)
    t += [pd.DataFrame(rows).to_string(index=False), ""]

    j = od.merge(n[["id", "class", "family", "cls_rule", "mag", "m0", "time_iso", "latitude", "longitude", "depth", "depth_status"]],
                 left_on="new_id", right_on="id", suffixes=("_old", ""))
    for m0 in (C.MMIN, 5.5):
        s = j[j["m0"] > m0] if m0 == C.MMIN else j[j["m0"] >= m0]
        t += [f"## family moves, same events, M {'>' if m0 == C.MMIN else '>='} {m0} (rows old, columns new)",
              pd.crosstab(s["family_old"], s["family"], margins=True).to_string(), ""]
    ch = j[(j["family_old"] != j["family"]) & (j["m0"] >= 5.5)]
    t += [f"## M >= 5.5 events whose family changed: {len(ch)}; by the rule that decided the new class"]
    for (a, b), s in ch.groupby(["family_old", "family"]):
        t.append(f"{a} -> {b} ({len(s)}): " + ", ".join(f"{r} {v}" for r, v in s["cls_rule"].value_counts().items()))
    t.append("")
    lost = o[o["new_id"].isna()]
    t += ["## old rows without a new event (above the cut in the old catalog)",
          f"{len(lost)}: rows merged into an event whose chosen magnitude is at or below the cut, or ids absent from "
          f"the new build (manual rows such as 85308b); by old class: {lost['class'].value_counts().to_dict()}", ""]
    ch[["id", "time_iso", "mag", "m0", "latitude", "longitude", "depth", "depth_status", "class_old", "class", "family_old",
        "family", "cls_rule"]].sort_values("m0", ascending=False).to_csv(OUT / "changes.csv", index=False)

    fig, ax = plt.subplots(1, 3, figsize=(17, 5))
    for a, f in zip(ax, FAMS[:3]):
        for d, lab, st in ((o, "old rows", ":"), (od, "old after dedup", "--"), (n, "new", "-")):
            m = np.sort(d.loc[d["family"] == f, "m0"].to_numpy())[::-1]
            a.semilogy(m, np.arange(1, len(m) + 1), st, label=f"{lab} ({len(m)})")
        a.set(xlabel="Cabello magnitude", ylabel="N(>= M)", title=f"{f}, common ground")
        a.legend()
    fig.tight_layout()
    fig.savefig(OUT / "compare.png", dpi=110)
    plt.close(fig)
    (OUT / "compare.txt").write_text("\n".join(t) + "\n")
    print("\n".join(t))


if __name__ == "__main__":
    main(*sys.argv[1:3])