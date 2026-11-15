"""S4: OpenQuake sources of the crustal model, every branch.

Background: one point source per grid cell, the MFD the sum over the four classes of pattern x class list (classes
share depths, nodal planes and scaling, so the sum is the same hazard as one source per class and cell); one file per
fault database (the join), fit shape and declustering option, and the no-faults files (full fit). Depths 0-30 km,
hypocentre 10 km, two nodal planes (strike 0 and 180, dip 60, reverse), WC1994, aspect 1 (psha_chile7).
Faults: simple-fault sources, one file per database and fault branch (psi x depth x shape), 0 to the depth of the
branch, WC1994, aspect 2 (psha_chile7); the Magallanes–Fagnano main trace one joined source.
Logic-tree fragments: per database and fit shape, sourceModel = the background of the two declustering options
(0.5 / 0.5), extendModel = the 36 fault branches; no-faults per shape. Writes nrml/ and nrml/branches.json and
tables/rates_<DATE>.csv (rates per file and source, for the OpenQuake check).
"""
import json

import numpy as np
import pandas as pd

import background as BG
import faults as F
import join as J
import nrml as X

NR, TAB = F.HERE / "nrml", F.HERE / "tables"

# settings
DATE = "2026-11-15"
TRT = "Active Shallow Crust"
PT = dict(usd=0.0, lsd=30.0, hypo=10.0, msr="WC1994", aspect=1.0,
          npd=[(0.5, 0.0, 60.0, 90.0), (0.5, 180.0, 60.0, 90.0)])
# Leonard (2014) for the fault ruptures, as for the fault Mmax (Pablo, 15 Nov; psha_chile7 had WC1994)
FLT = dict(usd=0.0, msr="Leonard2014_Interplate", aspect=2.0)
SHAPE_W = {"taper": 1.0, "trunc": 0.0}
TAG = {**{v: v for v in F.VARIANTS}, "none": "nofaults"}


def bkey(p, z, k):
    return f"psi{int(round(p * 100)):03d}_z{int(z):02d}_{k}"


def background(rows):
    mfd = pd.read_csv(TAB / f"background_mfd_{DATE}.csv")
    pats = {m: pd.read_csv(TAB / f"pattern_{m}_{DATE}.csv") for m in BG.DECL}
    files = []
    for db in TAG:
        for sh in BG.SHAPES:
            r = np.zeros((len(BG.CLASSES), J.CENTRES.size))
            for i, c in enumerate(BG.CLASSES):
                x = mfd[(mfd.db == db) & (mfd["shape"] == sh) & (mfd.cls == c)]
                r[i, np.rint((x.mag - J.CENTRES[0]) / 0.1).astype(int)] = x.rate
            for m in BG.DECL:
                p = pats[m]
                cell = p[list(BG.CLASSES)].to_numpy() @ r
                top = np.nonzero(cell.sum(0) > 0)[0].max() + 1
                fn = f"cr_bg_{TAG[db]}_{sh}_{m}.xml"
                srcs = []
                for j in range(len(p)):
                    q = cell[j, :top]
                    q = q[:np.nonzero(q > 0)[0].max() + 1]
                    i = f"bg{j:05d}"
                    srcs.append(X.point(i, p.lon[j], p.lat[j], PT["usd"], PT["lsd"], PT["hypo"], TRT,
                                        X.mfd(J.CENTRES[0], q), PT["msr"], PT["aspect"], PT["npd"]))
                    rows.append(dict(file=fn, source=i, N5=q.sum(), N6=q[J.CENTRES[:len(q)] >= 5.95].sum(),
                                     m_top=J.CENTRES[len(q) - 1]))
                X.model(NR / fn, f"crustal background, faults {db}, {sh}, {m}", srcs)
                files.append(dict(file=fn, kind="background", db=db, shape=sh, decl=m, n_sources=len(srcs),
                                  N5=cell.sum(), N6=cell[:, J.CENTRES >= 5.95].sum()))
                print(fn, len(srcs), round(cell.sum(), 4))
    return files


def faults(rows):
    files = []
    for base in F.DBS:
        s, r0, r1 = F.load(base)
        for db, rr in ((base, r0), (base + "_cm", r1)):
            for j, (p, z, k) in enumerate(F.BR):
                fn = f"cr_flt_{db}_{bkey(p, z, k)}.xml"
                srcs = []
                for i, q in s.iterrows():
                    r = rr[i, j]
                    r = r[:np.nonzero(r > 0)[0].max() + 1]
                    sid = "MF_system" if q.system else X.sid(q.fid)
                    srcs.append(X.simple_fault(f"f_{sid}", q["name"], q.trace, FLT["usd"], z, q.dip, q.rake, TRT,
                                               X.mfd(F.R.MMIN, r), FLT["msr"], FLT["aspect"]))
                    rows.append(dict(file=fn, source=f"f_{sid}", N5=r.sum(), N6=r.sum(),
                                     m_top=F.R.MMIN + 0.1 * (len(r) - 1), mo=F.moment(r)))
                X.model(NR / fn, f"crustal faults {db}, {bkey(p, z, k)}", srcs)
                files.append(dict(file=fn, kind="faults", db=db, psi=p, depth=z, fshape=k, weight=float(F.W[j]),
                                  n_sources=len(srcs), N6=float(rr[:, j].sum())))
    return files


def trees(files):
    f = pd.DataFrame(files)
    lts = []
    for db in F.VARIANTS:
        fl = f[(f.kind == "faults") & (f.db == db)]
        for sh in BG.SHAPES:
            bg = f[(f.kind == "background") & (f.db == db) & (f["shape"] == sh)]
            name = f"lt_crustal_{db}_{sh}.xml"
            X.logic_tree(NR / name, [("sourceModel", [(f"bg_{m}", [x], BG.W_DECL[m]) for m, x in zip(bg.decl, bg.file)]),
                                     ("extendModel", [(f"f{j:02d}", [x], w) for j, (x, w) in enumerate(zip(fl.file, fl.weight))])])
            lts.append(dict(file=name, db=db, shape=sh, weight_shape=SHAPE_W[sh]))
    for sh in BG.SHAPES:
        bg = f[(f.kind == "background") & (f.db == "none") & (f["shape"] == sh)]
        name = f"lt_crustal_nofaults_{sh}.xml"
        X.logic_tree(NR / name, [("sourceModel", [(f"bg_{m}", [x], BG.W_DECL[m]) for m, x in zip(bg.decl, bg.file)])])
        lts.append(dict(file=name, db="none", shape=sh, weight_shape=SHAPE_W[sh]))
    return lts


def main():
    NR.mkdir(exist_ok=True)
    rows = []
    files = background(rows) + faults(rows)
    lts = trees(files)
    pd.DataFrame(rows).to_csv(TAB / f"rates_{DATE}.csv", index=False, float_format="%.6e")
    out = dict(date=DATE, trt=TRT, min_mag=dict(background=float(J.CENTRES[0]), faults=F.R.MMIN), point=PT, fault=FLT,
               max_distance_km=300,
               note=("Fault-database weights are not decided (tornado factor, DECISIONS); the tree takes the tapered fit "
                     "(shape weight 1, cut at Mmax 0) as S1. Background files hold the four classes summed per cell."),
               factors=dict(db=list(F.VARIANTS) + ["none"], shape=SHAPE_W, decl=BG.W_DECL,
                            psi={str(k): v for k, v in F.R.PSI.items()}, depth={str(k): v for k, v in F.R.DEPTH.items()},
                            fshape={k: 1 / 6 for k in F.R.SHAPES}),
               trees=lts, files=files)
    (NR / "branches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
