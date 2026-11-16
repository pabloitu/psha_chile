"""In-slab tornado files (C15 feedback, Pablo 16 Nov): nrml/<RUN>/ holds every file of nrml/<SRC>/ byte for byte, plus
three weight-0 branches made from the reference gk_taper_ml_l3 with one choice changed and everything else (rates,
source ids, upper and lower depths, nodal planes) left as it is:

- one layer: the hypocentre of every cell at h_one of the C15 table (top + 0.243 x Slab2 thickness);
- lower depth 0.65: the lower seismogenic depth of the C15 table, the reference hypocentres kept;
- rupture scaling AllenHayesIntraslab instead of StrasserIntraslab.

branches.json gets the new branches and a tornado block (one row per choice, the rest at the reference), as the
interface files of S1.
"""
import hashlib
import json
import re
import shutil

import numpy as np
import pandas as pd

import build as B

# settings
SRC, RUN = "2026-11-16b", "2026-11-16c"
REF = "gk_taper_ml_l3"
ONE = B.TAB / "depth_cells_2026-11-16d.csv"
LSD = B.TAB / "depth_cells_lsd065_2026-11-16d.csv"
MSR_ALT = "AllenHayesIntraslab"
VARIANTS = {"l1c15": "one layer at top + 0.243 x thickness (C15)", "lsd065": "lower depth top + 0.65 x thickness (C15)",
            "ah": "rupture scaling AllenHayesIntraslab"}
D_SRC, D = B.HERE / "nrml" / SRC, B.HERE / "nrml" / RUN
SOURCE = re.compile(r'<pointSource id="[^"]+".*?</pointSource>\n', re.S)


def sha(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()


def variant(txt, tag, cell, one, lsd):
    """The reference file text with one choice changed in every point source."""
    def edit(m):
        s = m.group(0)
        lon, lat = re.search(r"<gml:pos>([^<]+)</gml:pos>", s).group(1).split()
        i = cell[(lon, lat)]
        if tag == "l1c15":
            return re.sub(r"<hypoDepthDist>.*?</hypoDepthDist>",
                          f'<hypoDepthDist><hypoDepth probability="1.000" depth="{one[i]:.2f}"/></hypoDepthDist>', s)
        if tag == "lsd065":
            return re.sub(r"<lowerSeismoDepth>[^<]+</lowerSeismoDepth>", f"<lowerSeismoDepth>{lsd[i]:.2f}</lowerSeismoDepth>", s)
        return s.replace(f"<magScaleRel>{B.MSR}</magScaleRel>", f"<magScaleRel>{MSR_ALT}</magScaleRel>")
    out = SOURCE.sub(edit, txt)
    return out.replace(f'<sourceModel name="in-slab ', f'<sourceModel name="in-slab {tag} ', 1)


def run():
    D.mkdir(parents=True, exist_ok=True)
    for f in sorted(D_SRC.iterdir()):
        shutil.copy2(f, D / f.name)
        assert sha(f) == sha(D / f.name)
    g = pd.read_csv(B.DEPTH)
    cell = {(f"{x:.3f}", f"{y:.3f}"): i for i, (x, y) in enumerate(zip(g.lon, g.lat))}
    one, lsd = pd.read_csv(ONE), pd.read_csv(LSD)
    assert np.allclose(one[["lon", "lat"]], g[["lon", "lat"]]) and np.allclose(lsd[["lon", "lat"]], g[["lon", "lat"]])
    j = json.loads((D_SRC / "branches.json").read_text())
    ref = next(b for b in j["branches"] if b["id"] == REF)
    for tag, label in VARIANTS.items():
        bid = f"{REF}_{tag}"
        files = [f.replace(REF, bid) for f in ref["files"]]
        for f, f0 in zip(files, ref["files"]):
            (D / f).write_text(variant((D_SRC / f0).read_text(), tag, cell, one.h_one.to_numpy(), lsd.lsd.to_numpy()))
        j["branches"].append(dict(ref, id=bid, files=files, tree=False, weight=0.0, variant=tag, label=label))
    rows = {"is_ref": ("reference: tapered, ML (a, b), Gardner–Knopoff pattern, three layers, lower depth 0.475, Strasser", REF),
            "is_ab_p05": ("(a, b) 5th percentile", "gk_taper_p05_l3"), "is_ab_p95": ("(a, b) 95th percentile", "gk_taper_p95_l3"),
            "is_decl_nn": ("nearest-neighbour pattern", "nn_taper_ml_l3"), "is_shape_cut": ("cut at Mmax", "gk_trunc_ml_l3"),
            "is_mmax_pad00": ("Mmax = largest observed event (no pad)", "gk_taper_ml_l3_pad00"),
            "is_mmax_pad04": ("Mmax = largest observed event + 0.4", "gk_taper_ml_l3_pad04")}
    rows.update({f"is_{t}": (lab, f"{REF}_{t}") for t, lab in VARIANTS.items()})
    ids = {b["id"]: b for b in j["branches"]}
    j["tornado"] = {k: dict(label=lab, branches=[dict(id=b, files=ids[b]["files"], weight=1.0)]) for k, (lab, b) in rows.items()}
    j.update(run=RUN, source_run=SRC, variants=VARIANTS, variant_inputs=dict(l1c15=ONE.name, lsd065=LSD.name),
             note="C14 one-layer branches (*_l1, per-cell median) are kept but superseded by l1c15 for the tornado")
    (D / "branches.json").write_text(json.dumps(j, indent=1))
    return j


def check():
    """The new files against the reference: same source ids and rate lists (as text), one change each; OpenQuake
    parser read of the reference and the three variants."""
    import oqcheck as O
    ref = {f: (D / f).read_text() for f in (f"is_slab_{REF}.xml", f"is_nest_{REF}.xml")}
    rows = []
    for tag in [""] + [f"_{t}" for t in VARIANTS]:
        for grp in ("slab", "nest"):
            f = D / f"is_{grp}_{REF}{tag}.xml"
            t, t0 = f.read_text(), ref[f"is_{grp}_{REF}.xml"]
            n, n55, n7, m0, bad_w, bad_h = O.read_one(f)[1:]
            rows.append(dict(file=f.name, sources=n, N55_oq=n55, N7_oq=n7, weights_not_1=bad_w, hypo_outside=bad_h,
                             same_ids=re.findall(r'pointSource id="([^"]+)"', t) == re.findall(r'pointSource id="([^"]+)"', t0),
                             same_rates=re.findall(r"<occurRates>([^<]+)</occurRates>", t) == re.findall(r"<occurRates>([^<]+)</occurRates>", t0),
                             same_usd=re.findall(r"<upperSeismoDepth>([^<]+)<", t) == re.findall(r"<upperSeismoDepth>([^<]+)<", t0),
                             same_lsd=re.findall(r"<lowerSeismoDepth>([^<]+)<", t) == re.findall(r"<lowerSeismoDepth>([^<]+)<", t0),
                             same_hypo=re.findall(r"<hypoDepthDist>.*?</hypoDepthDist>", t) == re.findall(r"<hypoDepthDist>.*?</hypoDepthDist>", t0),
                             msr=sorted(set(re.findall(r"<magScaleRel>([^<]+)<", t)))))
    x = pd.DataFrame(rows)
    rt = pd.read_csv(B.TAB / f"drop_{SRC}.csv")
    q = rt[(rt.decl == "gk") & (rt["shape"] == "taper") & (rt.ab == "ml") & (rt["pad"] == "pad02")].set_index("group")
    x["N55_table"] = [q.loc[f.split("_")[1]].filter(like="N5.5_").sum() for f in x.file]
    x["dN55"] = x.N55_oq / x.N55_table - 1
    same = all(sha(f) == sha(D / f.name) for f in D_SRC.iterdir() if f.name != "branches.json")
    return x, same


if __name__ == "__main__":
    run()
    x, same = check()
    pd.set_option("display.width", 250)
    print(x.to_string(index=False))
    print("files of", SRC, "byte-identical in", RUN, ":", same)
    x.to_csv(B.TAB / f"oqread_{RUN}.csv", index=False)
