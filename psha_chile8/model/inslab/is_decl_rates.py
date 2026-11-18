"""In-slab tornado rows for the rate convention (Pablo, 16 Nov): the reference branch (tapered, ML (a, b), three
layers, one source per cell, nest separate) with the rates and b of the declustered fits instead of the full
catalogue, each with the pattern of its own declustering method. As the interface rows of S1: fits_declustered,
methods gk_family / nn_family, table full (completeness table of the full catalogue), b option own. Written to their
own folder nrml/<RUN>/ with a branches.json and a tornado block; the reference row is is_ref of nrml/2026-11-16c/.
"""
import json

import numpy as np
import pandas as pd

import build as B

# settings
RUN = "2026-11-16d"
FITS_DC = B.FITS_DC
METHODS = B.DECL_M
TABLE, B_OPTION = "full", "own"
SH, AB, LY = "taper", "ml", "l3"
REF_RUN, REF = "2026-11-16c", f"{B.DC}_taper_ml_l3"
D = B.OUT / "nrml" / RUN


def fits_dc(method):
    x = pd.read_csv(FITS_DC)
    x = x[(x.method == method) & (x.table == TABLE) & (x.b_option == B_OPTION) & x.unit.isin(list(B.CLASSES))]
    return {(r.unit, r.shape): r for r in x.itertuples()}


def run():
    D.mkdir(parents=True, exist_ok=True)
    g, ev = B.cells(), B.events()
    P = pd.read_csv(B.TAB / f"pattern_{B.DATE}.csv")
    h, w = B.hypo(g, LY)
    keep_g = B.guard(g, ev)
    npd, shr = pd.read_csv(B.NPD_TAB), pd.read_csv(B.SHARE)
    rows, br = [], []
    for k, m in METHODS.items():
        F = fits_dc(m)
        npl = dict(zip(B.GROUPS, B.npd_cells(g, npd, shr, k, SH, AB)))
        bid = f"{k}_{SH}_{AB}_{LY}_rate{k}"
        R = {}
        for c, s in B.CLASSES.items():
            f, cc, n = B.mfd(F[(c, SH)], AB)
            R[c] = (cc, P[f"p_{s['short']}_{k}"].to_numpy()[:, None] * n[None, :], F[(c, SH)])
        for q, gr in B.GROUPS.items():
            cc = max((R[c][0] for c in gr["classes"]), key=len)
            part = {c: np.pad(R[c][1], ((0, 0), (0, len(cc) - len(R[c][0])))) for c in gr["classes"]}
            Rq = sum(part.values())
            n55 = Rq.sum(1)
            on = (n55 > 0) & ((n55 >= gr["drop"] * n55.sum()) | keep_g)
            for c in gr["classes"]:
                r = R[c][2]
                rows.append(dict(branch=bid, group=q, cls=c, method=m, b=r.b, mmax=r.mmax, corner=r.corner, kept=int(on.sum()),
                                 dropped=int(((n55 > 0) & ~on).sum()), N55=float(part[c][on].sum()),
                                 N7=float(part[c][on][:, cc > 6.95].sum()), N8=float(part[c][on][:, cc > 7.95].sum()),
                                 N55_fit=B.N_ge(r, 5.5), N7_fit=B.N_ge(r, 7.0)))
            txt = [" ".join(f"{v:.5e}" for v in row) for row in Rq[on]]
            pq = npl[q] if q == "slab" else np.full(len(g), npl[q], dtype=object)
            src = [B.point(f"is{q[:2]}{j:05d}", g.lon[i], g.lat[i], g.usd[i], g.lsd[i], h[i], w[i], cc[0], txt[j], pq[i])
                   for j, i in enumerate(np.flatnonzero(on))]
            (D / f"is_{q}_{bid}.xml").write_text(B.HEAD + f'<sourceModel name="in-slab {q} {bid}">\n' + "".join(src)
                                                 + "</sourceModel>\n</nrml>\n")
        br.append(dict(id=bid, files=[f"is_{q}_{bid}.xml" for q in B.GROUPS], decl=k, shape=SH, ab=AB, layers=LY, tree=False,
                       weight=0.0, pad="pad02", rates=f"declustered {m}"))
    t = pd.DataFrame(rows)
    t.to_csv(B.TAB / f"decl_rates_{RUN}.csv", index=False)
    lab = {"gk": "rates and b of the Gardner–Knopoff declustered catalogue, Gardner–Knopoff pattern",
           "nn": "rates and b of the nearest-neighbour declustered catalogue, nearest-neighbour pattern"}
    j = dict(date=B.DATE, run=RUN, trt=B.TRT, msr=B.MSR, aspect=B.ASPECT, trial=B.TRIAL, nodal_planes=dict(table=str(B.NPD_TAB.relative_to(B.ROOT)), shares=str(B.SHARE.relative_to(B.ROOT))), min_mag=B.M_MIN,
             max_distance_km=500, pointsource_distance_km=100, fits=str(FITS_DC.relative_to(B.ROOT)),
             fit_rows=dict(methods=METHODS, table=TABLE, b_option=B_OPTION), branches=br,
             reference=dict(run=REF_RUN, id=REF, row="is_ref", note=f"full-catalogue rates, {B.DC} pattern"),
             tornado={f"is_rate_{b['decl']}": dict(label=lab[b["decl"]], branches=[dict(id=b["id"], files=b["files"], weight=1.0)])
                      for b in br})
    (D / "branches.json").write_text(json.dumps(j, indent=1))
    return t


def check():
    """OpenQuake parser read of the new files against the table."""
    import oqcheck as O
    t = pd.read_csv(B.TAB / f"decl_rates_{RUN}.csv")
    rows = []
    for f in sorted(D.glob("is_*.xml")):
        n, n55, n7, m0, bad_w, bad_h = O.read_one(f)[1:]
        q = t[(t.branch == f.stem.split("_", 2)[2]) & (t.group == f.stem.split("_")[1])]
        rows.append(dict(file=f.name, sources=n, m_first=m0, weights_not_1=bad_w, hypo_outside=bad_h, N55_oq=n55,
                         dN55=n55 / q.N55.sum() - 1, dN7=n7 / q.N7.sum() - 1))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    t = run()
    print(t.round(5).to_string(index=False))
    x = check()
    print(x.to_string(index=False))
    x.to_csv(B.TAB / f"oqread_{RUN}.csv", index=False)
