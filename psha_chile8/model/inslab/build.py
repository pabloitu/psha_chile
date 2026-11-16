"""S2: in-slab source model for OpenQuake (tasks/S2_inslab.md).

Point sources on the C14 cells (grid `data/inslab_grid_01_2026-11-15.csv` where Slab2 has a top). Per class (shallow,
intermediate, Jujuy nest) and declustering option: the 2-D pattern from the declustered complete events, smoothed with
the Helmstetter et al. (2007) kernel over the class domain, n calibrated on a train/test split; scaled to the B11 fit
of the class (tapered and cut shapes, (a, b) variants); depths from C14 (three hypocentres or one). Writes tables/,
nrml/ (one file per class and branch, branches.json, the logic-tree fragment) and the figures of figs_s2.py.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "fits"))
import gr as G  # noqa: E402
import is_smooth as S  # noqa: E402

DATE = "2026-11-16"
# NRML files of a run in their own folder (15 Nov: nrml/; 16 Nov one file per class: nrml/2026-11-16/), figures dated
RUN = "2026-11-16b"
TAB, NR = HERE / "tables", HERE / "nrml" / RUN

# inputs (A9 catalogue)
CAT = ROOT / "catalog/frozen/2026-11-16/catalog_2026-11-16.csv"
FITS = ROOT / "fits/tables/fits_2026-11-16.csv"
DEPTH = TAB / "depth_cells_2026-11-16.csv"
DECL = {"gk": ROOT / "catalog/declustered/gk_family_2026-11-16.csv", "nn": ROOT / "catalog/declustered/nn_family_2026-11-16.csv"}
DECL_W = {"gk": 0.5, "nn": 0.5}

# pattern: completeness table of DECISIONS (events complete in their period), train before SPLIT, test from SPLIT
TABLE = [(5.0, 1976), (5.2, 1964), (7.0, 1905), (7.5, 1830), (8.0, 1500)]
SPLIT = 2010.0
# the curve is scored on all candidates; n is chosen from N_MIN up (Pablo, 16 Nov: n 1 and 3 kept for analysis,
# the intermediate class would pick 1)
CANDIDATES = (1, 3, 5, 10, 15, 25, 50, 100)
N_MIN = 5
# a class with fewer test events (sum of class weights) takes the n of the in-slab family
MIN_TEST = 20.0

# classes and their domains on the cells: shallow and intermediate are smoothed over all in-slab cells and added (the
# 50 km slab-top line of catalog/classify.py only splits the events for the fits; two domains left a 20 % trough along
# it; Pablo, 16 Nov); the Jujuy nest over its region of classify.NEST (0.8° of 66.9° W, 24.0° S, longitude scaled
# by cos(lat))
NEST = dict(lon=-66.9, lat=-24.0, radius_deg=0.8)


def nest_r(lon, lat):
    return np.hypot((np.asarray(lon) - NEST["lon"]) * np.cos(np.radians(lat)), np.asarray(lat) - NEST["lat"])


CLASSES = {"intraslab_shallow": dict(short="shallow", domain=lambda g: g.top.notna()),
           "intraslab_intermediate": dict(short="intermediate", domain=lambda g: g.top.notna()),
           "jujuy_nest": dict(short="nest", domain=lambda g: nest_r(g.lon, g.lat) <= NEST["radius_deg"])}

# MFDs (DECISIONS, Statistics and In-slab): both shapes; (a, b) variants at the 5th / 95th percentile of the rate at the
# controlling magnitude (8.8, at most Mmax - 0.3, as the interface), weights as the interface; the tapered list ends at
# Mmax + TAPER_PAD and its last bin carries the rate of the line above it (DECISIONS, Statistics); sources from Mw 5.5
# (bin centre), as the interface (Pablo, 15 Nov)
SHAPES = ("taper", "trunc")
AB = {"p05": 0.185, "ml": 0.63, "p95": 0.185}
AB_M, TAPER_PAD, M_MIN = 8.8, 0.2, 5.5
LAYERS = ("l3", "l1")
# reference tree: tapered, maximum-likelihood (a, b), three hypocentres; the other options carry weight 0 (tornado)
TREE = dict(shape="taper", ab="ml", layers="l3")

# source files (Pablo, 16 Nov): shallow and intermediate as one point source per cell with the summed MFD, the nest
# its own source; a cell of a summed group is dropped when its rate above M_MIN is below DROP of the group total of the
# branch, unless it lies within GUARD_KM of an in-slab event of Mw >= GUARD_M (in-slab weight >= 0.5)
GROUPS = {"slab": dict(classes=("intraslab_shallow", "intraslab_intermediate"), drop=1e-8),
          "nest": dict(classes=("jujuy_nest",), drop=0.0)}
GUARD_KM, GUARD_M = 50.0, 7.0

# Mmax pad (DECISIONS, Statistics: a tornado factor, 0.0 and 0.4 against 0.2, Kagan corner; ML rows): the reference
# branch only, weight 0
PADS = {"pad00": ROOT / "fits/tables/fits_2026-11-16f_pad00.csv", "pad04": ROOT / "fits/tables/fits_2026-11-16f_pad04.csv"}
PAD_BRANCH = dict(shape="taper", ab="ml", layers="l3")

# ruptures (psha_chile7 intraslab/config.py; DECISIONS, In-slab)
TRT, MSR, ASPECT = "Subduction IntraSlab", "StrasserIntraslab", 1.0
NPD = [(0.5, 180.0, 60.0, -90.0), (0.5, 0.0, 30.0, 90.0)]
REF_M = (5.5, 6.0, 7.0, 7.5, 8.0)


# pattern
def cells():
    g = pd.read_csv(DEPTH)
    for c, s in CLASSES.items():
        g["dom_" + s["short"]] = np.asarray(s["domain"](g))
    return g


def events():
    """In-slab events of the frozen catalogue with their class weights, completeness year `yc` and flag, and
    declustering flags."""
    d = G.load(CAT, mlow=4.45)
    d = d[d.w_inslab > 0].copy()
    yr = np.full(len(d), np.inf)
    for m, y in sorted(TABLE):
        yr[d.mw.to_numpy() >= m - 1e-6] = y
    d["yc"], d["comp"] = yr, d.t.to_numpy() >= yr
    for k, f in DECL.items():
        x = pd.read_csv(f, usecols=["event_id", "mainshock"])
        d[k] = d.event_id.map(x.set_index("event_id").mainshock).fillna(False).astype(bool)
    return d.reset_index(drop=True)


def calibration(ev, g):
    """Log-likelihood against n per class, declustering option and the in-slab family; the n chosen per class."""
    rows, pick = [], {}
    for k in DECL:
        e = ev[ev[k] & ev.comp]
        units = {c: (e.assign(w=e["W_" + c]), g["dom_" + s["short"]].to_numpy()) for c, s in CLASSES.items()}
        units["family"] = (e.assign(w=e.w_inslab), g[[f"dom_{s['short']}" for s in CLASSES.values()]].any(axis=1).to_numpy())
        for u, (x, dom) in units.items():
            x = x[x.w > 0]
            tr, te = x[x.t < SPLIT], x[x.t >= SPLIT]
            # training events as rates: each weight over its completeness period up to the split (test events share
            # one period, 2010 to today)
            tw = tr.assign(w=tr.w / (SPLIT - tr.yc))
            for n, ll in S.calibrate(tw, te, g.lon[dom].to_numpy(), g.lat[dom].to_numpy(), CANDIDATES):
                rows.append(dict(decl=k, unit=u, n=n, loglik=ll, n_train=tr.w.sum(), n_test=te.w.sum()))
    t = pd.DataFrame(rows)
    for (k, u), q in t.groupby(["decl", "unit"]):
        # the first local maximum from small n (a second maximum at large n is ignored; Pablo, 16 Nov)
        r = q[q.n >= N_MIN]
        t.loc[q.index, "best"] = q.n == S.first_max(r.n, r.loglik)
        t.loc[q.index, "best_all"] = q.n == S.first_max(q.n, q.loglik)
        t.loc[q.index, "dll"] = q.loglik - q.loglik.max()
    for k in DECL:
        fam = int(t[(t.decl == k) & (t.unit == "family") & t.best].n.iloc[0])
        for c in CLASSES:
            q = t[(t.decl == k) & (t.unit == c)]
            own = int(q[q.best].n.iloc[0])
            pick[(c, k)] = own if q.n_test.iloc[0] >= MIN_TEST else fam
    return t, pick


def patterns(ev, g, pick):
    """Pattern of every class and declustering option on all its complete declustered events up to today, each with
    its class weight over its completeness period (a rate), normalised to 1 over its domain (0 outside)."""
    P = pd.DataFrame(index=g.index)
    for k in DECL:
        for c, s in CLASSES.items():
            e = ev[ev[k] & ev.comp & (ev["W_" + c] > 0)]
            dom = g["dom_" + s["short"]].to_numpy()
            h = S.bandwidth(e.lon, e.lat, pick[(c, k)])
            f = np.zeros(len(g))
            f[dom] = S.field(e.lon, e.lat, e["W_" + c] / (G.tend(ev) - e.yc), h, g.lon[dom], g.lat[dom])
            P[f"p_{s['short']}_{k}"] = f / f.sum()
    return P


# MFDs
def fits(path=FITS):
    x = pd.read_csv(path)
    return {(r.unit, r.shape): r for r in x[x.unit.isin(list(CLASSES))].itertuples()}


def mfd(r, ab="ml"):
    """
    Fit and binned list of one class, shape and (a, b) variant.

    The variant pair is the expected (a, b) given the rate at the controlling magnitude at its percentile, from the
    bootstrap covariance of (a, b) (fits/run.py, interface rows); the corner of the tapered line is kept.

    Returns
    -------
    f : dict of gr (shape, b, rate, m_lo, mmax, corner)
    c, n : arrays
        Bin centres from M_MIN (min_mag is the first centre) and yearly rates, differences of the fitted line at
        the bin edges; the last bin of the tapered list also takes the rate above it.
    """
    sh, mx = r.shape, r.mmax + G.DM / 2
    f = dict(shape=sh, b=r.b, rate=r.rate_mlo, m_lo=r.m_lo, mmax=mx, corner=r.corner if sh == "taper" else None)
    if ab != "ml":
        mc = min(AB_M, r.mmax - 0.3)
        C = np.array([[r.var_a, r.cov_ab], [r.cov_ab, r.var_b]])
        v = np.array([1.0, -(mc - G.DM / 2)])
        da, db = stats.norm.ppf(int(ab[1:]) / 100) * (C @ v) / np.sqrt(v @ C @ v)
        a, b = r.a + da, r.b + db
        n = 10 ** (a - b * r.m_lo)
        f.update(b=b, rate=n * (1 - 10 ** (-b * (mx - r.m_lo))) if sh == "trunc" else n, a=a, mc=mc)
    top = round(r.mmax, 1) if sh == "trunc" else round(r.mmax + TAPER_PAD, 1)
    c = np.round(M_MIN + G.DM * np.arange(int(round((top - M_MIN) / G.DM)) + 1), 2)
    n = f["rate"] * (G.surv(f, c - G.DM / 2) - G.surv(f, c + G.DM / 2))
    n[-1] = f["rate"] * G.surv(f, c[-1] - G.DM / 2)
    return f, c, n


def hypo(g, layers):
    """Hypocentre depths and weights per cell: three (weights renormalised and rounded to 0.001, summing to 1) or
    the one-layer median."""
    if layers == "l1":
        return g[["h_one"]].to_numpy(), np.ones((len(g), 1))
    w = g[["w1", "w2", "w3"]].to_numpy()
    w = np.round(w / w.sum(1, keepdims=True), 3)
    w[:, 2] = np.round(1 - w[:, 0] - w[:, 1], 3)
    return g[["h1", "h2", "h3"]].to_numpy(), w


def branches():
    rows = []
    for k, wk in DECL_W.items():
        for sh in SHAPES:
            for ab, wa in AB.items():
                for ly in LAYERS:
                    bid = f"{k}_{sh}_{ab}_{ly}"
                    tree = sh == TREE["shape"] and ab == TREE["ab"] and ly == TREE["layers"]
                    rows.append(dict(id=bid, files=[f"is_{q}_{bid}.xml" for q in GROUPS], decl=k, shape=sh,
                                     ab=ab, layers=ly, tree=tree, weight=wk if tree else 0.0,
                                     w_factor=dict(decl=wk, ab=wa), pad="pad02"))
    for q in PADS:
        for k, wk in DECL_W.items():
            bid = f"{k}_{PAD_BRANCH['shape']}_{PAD_BRANCH['ab']}_{PAD_BRANCH['layers']}_{q}"
            rows.append(dict(id=bid, files=[f"is_{g}_{bid}.xml" for g in GROUPS], decl=k, shape=PAD_BRANCH["shape"],
                             ab=PAD_BRANCH["ab"], layers=PAD_BRANCH["layers"], tree=False, weight=0.0,
                             w_factor=dict(decl=wk, ab=AB[PAD_BRANCH["ab"]]), pad=q))
    return pd.DataFrame(rows)


# NRML
HEAD = '<?xml version="1.0" encoding="utf-8"?>\n<nrml xmlns:gml="http://www.opengis.net/gml" xmlns="http://openquake.org/xmlns/nrml/0.4">\n'
NPS = "".join(f'<nodalPlane probability="{p}" strike="{s}" dip="{d}" rake="{r}"/>' for p, s, d, r in NPD)


def point(sid, lon, lat, usd, lsd, h, w, c0, rates):
    hd = "".join(f'<hypoDepth probability="{p:.3f}" depth="{z:.2f}"/>' for p, z in zip(w, h))
    return (f'<pointSource id="{sid}" name="{sid}" tectonicRegion="{TRT}">\n<pointGeometry><gml:Point><gml:pos>{lon:.3f} {lat:.3f}'
            f'</gml:pos></gml:Point><upperSeismoDepth>{usd:.2f}</upperSeismoDepth><lowerSeismoDepth>{lsd:.2f}</lowerSeismoDepth>'
            f'</pointGeometry>\n<magScaleRel>{MSR}</magScaleRel><ruptAspectRatio>{ASPECT}</ruptAspectRatio>\n'
            f'<incrementalMFD minMag="{c0:.2f}" binWidth="{G.DM:.2f}"><occurRates>{rates}</occurRates></incrementalMFD>\n'
            f'<nodalPlaneDist>{NPS}</nodalPlaneDist>\n<hypoDepthDist>{hd}</hypoDepthDist>\n</pointSource>\n')


def logic_tree(path, br):
    """Source-model logic-tree fragment: one sourceModel branch set, each branch its source files."""
    s = "".join(f'<logicTreeBranch branchID="is_{b.id}"><uncertaintyModel>{" ".join(b.files)}</uncertaintyModel>'
                f"<uncertaintyWeight>{b.weight}</uncertaintyWeight></logicTreeBranch>\n" for b in br.itertuples())
    path.write_text(HEAD + '<logicTree logicTreeID="lt_inslab">\n<logicTreeBranchingLevel branchingLevelID="bl_is">\n'
                    '<logicTreeBranchSet uncertaintyType="sourceModel" branchSetID="bs_is">\n' + s
                    + "</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n</logicTree>\n</nrml>\n")


def guard(g, ev):
    """Cells within GUARD_KM of an in-slab event of Mw >= GUARD_M with in-slab weight >= 0.5."""
    e = ev[(ev.mw >= GUARD_M - 1e-6) & (ev.w_inslab >= 0.5)]
    d = cKDTree(S.xyz(e.lon.to_numpy(), e.lat.to_numpy())).query(S.xyz(g.lon.to_numpy(), g.lat.to_numpy()))[0]
    return d * 6371.0 <= GUARD_KM


def write(g, P, F, br, ev):
    """
    NRML files of every branch: one point source per cell and group, the MFD the sum of the class lists of the group.

    Returns the summed lists per class and branch (all cells, for the rate tables), the cells kept per group and
    branch with the rate removed, and the class shares of the summed groups per cell (above M_MIN and in the Mw 7.0
    bin). Also writes the per-cell bin rates per class (gzip csv per declustering option, shape and (a, b)).
    """
    NR.mkdir(parents=True, exist_ok=True)
    (TAB / "bins").mkdir(exist_ok=True)
    H = {ly: hypo(g, ly) for ly in LAYERS}
    keep_g = guard(g, ev)
    tot, drop, share = {}, [], []
    sets = [(k, sh, ab, "", F, LAYERS) for k in DECL for sh in SHAPES for ab in AB]
    sets += [(k, PAD_BRANCH["shape"], PAD_BRANCH["ab"], f"_{q}", fits(f), (PAD_BRANCH["layers"],))
             for q, f in PADS.items() for k in DECL]
    for k, sh, ab, pad, Fs, lays in sets:
        out, R = [], {}
        for c, s in CLASSES.items():
            f, cc, n = mfd(Fs[(c, sh)], ab)
            p = P[f"p_{s['short']}_{k}"].to_numpy()
            R[c] = (cc, p[:, None] * n[None, :])
            on = p > 0
            if not pad:
                tot[(c, k, sh, ab)] = (cc, R[c][1].sum(0), f, int(on.sum()))
                out.append(pd.DataFrame(R[c][1][on], columns=[f"{x:.2f}" for x in cc]).assign(
                    lon=g.lon.to_numpy()[on], lat=g.lat.to_numpy()[on], cls=s["short"]))
        if not pad:
            x = pd.concat(out)
            x[["cls", "lon", "lat"] + [q for q in x.columns if q[0].isdigit()]].to_csv(
                TAB / "bins" / f"rates_{k}_{sh}_{ab}_{DATE}.csv.gz", index=False, float_format="%.5e")
        for q, gr in GROUPS.items():
            cc = max((R[c][0] for c in gr["classes"]), key=len)
            part = {c: np.pad(R[c][1], ((0, 0), (0, len(cc) - len(R[c][0])))) for c in gr["classes"]}
            Rq = sum(part.values())
            n55 = Rq.sum(1)
            on = (n55 > 0) & ((n55 >= gr["drop"] * n55.sum()) | keep_g)
            drop.append(dict(group=q, decl=k, shape=sh, ab=ab, pad=pad.lstrip("_") or "pad02", cells=int((n55 > 0).sum()),
                             kept=int(on.sum()), dropped=int(((n55 > 0) & ~on).sum()), removed=float(n55[~on].sum() / n55.sum()),
                             m_top=float(cc[-1]),
                             **{f"N5.5_{CLASSES[c]['short']}": float(part[c][on].sum()) for c in gr["classes"]},
                             **{f"N7_{CLASSES[c]['short']}": float(part[c][on][:, cc > 6.95].sum()) for c in gr["classes"]},
                             **{f"N8_{CLASSES[c]['short']}": float(part[c][on][:, cc > 7.95].sum()) for c in gr["classes"]}))
            if len(gr["classes"]) > 1 and not pad:
                b7 = int(np.argmin(np.abs(cc - 7.0)))
                sh_ = pd.DataFrame({"lon": g.lon, "lat": g.lat, "kept": on, "decl": k, "shape": sh, "ab": ab})
                for c in gr["classes"]:
                    sh_[f"{CLASSES[c]['short']}_m5.5"] = part[c].sum(1) / np.where(n55 > 0, n55, 1)
                    sh_[f"{CLASSES[c]['short']}_m7"] = part[c][:, b7] / np.where(Rq[:, b7] > 0, Rq[:, b7], 1)
                share.append(sh_[n55 > 0])
            txt = [" ".join(f"{v:.5e}" for v in row) for row in Rq[on]]
            idx = np.flatnonzero(on)
            for ly in lays:
                h, w = H[ly]
                bid = f"{k}_{sh}_{ab}_{ly}{pad}"
                src = [point(f"is{q[:2]}{j:05d}", g.lon[i], g.lat[i], g.usd[i], g.lsd[i], h[i], w[i], cc[0], txt[j])
                       for j, i in enumerate(idx)]
                (NR / f"is_{q}_{bid}.xml").write_text(HEAD + f'<sourceModel name="in-slab {q} {bid}">\n'
                                                      + "".join(src) + "</sourceModel>\n</nrml>\n")
    logic_tree(NR / "source_lt_inslab.xml", br[br.tree])
    j = dict(date=DATE, run=RUN, trt=TRT, msr=MSR, aspect=ASPECT, nodal_planes=NPD, min_mag=M_MIN, max_distance_km=500,
             pointsource_distance_km=100, groups={q: list(v["classes"]) for q, v in GROUPS.items()},
             drop=dict(fraction={q: v["drop"] for q, v in GROUPS.items()}, guard_km=GUARD_KM, guard_m=GUARD_M), tree=TREE,
             factors=dict(decl=DECL_W, shape=list(SHAPES), ab=AB, layers=list(LAYERS), pad=["pad02"] + list(PADS)),
             pads={q: str(f.relative_to(ROOT)) for q, f in PADS.items()},
             branches=json.loads(br.to_json(orient="records")))
    (NR / "branches.json").write_text(json.dumps(j, indent=1))
    return tot, pd.DataFrame(drop), pd.concat(share, ignore_index=True)


# tables
def N_ge(r, m):
    """N(>= m) of a fits row, m a bin centre."""
    return float(r.rate_mlo * G.surv(mfd(r)[0], m - G.DM / 2))


def rate_tables(tot, br):
    r, e = [], []
    for (c, k, sh, ab), (cc, n, f, nsrc) in tot.items():
        o = dict(cls=c, decl=k, shape=sh, ab=ab, b=f["b"], corner=f["corner"], m_top=cc[-1], sources=nsrc,
                 moment=float((n * G.moment(cc)).sum()))
        o.update({f"N{m:g}": float(n[cc > m - G.DM / 2].sum()) for m in REF_M})
        o.update({f"fit_N{m:g}": float(f["rate"] * G.surv(f, m - G.DM / 2)) for m in REF_M})
        r.append(o)
        edges = cc - G.DM / 2
        lst = np.cumsum(n[::-1])[::-1]
        fit = f["rate"] * G.surv(f, edges)
        e.append(dict(cls=c, decl=k, shape=sh, ab=ab, edges=len(edges), max_rel=float(np.max(np.abs(lst / fit - 1))),
                      moment_above_top=float(f["rate"] * G.surv(f, cc[-1] + G.DM / 2) * G.moment(cc[-1]) / (n * G.moment(cc)).sum())))
    return pd.DataFrame(r), pd.DataFrame(e)


def south(g, P, F, lat=-36.0, dz=5.0):
    """N(>= 5) per 5 km of hypocentre depth south of lat (reference shape, both declustering options at 0.5), one
    layer against three."""
    s = (g.lat < lat).to_numpy()
    n5 = sum(DECL_W[k] * sum(P[f"p_{q['short']}_{k}"].to_numpy() * N_ge(F[(c, "taper")], 5.0) for c, q in CLASSES.items())
             for k in DECL)
    bins = np.arange(0, 200 + dz, dz)
    out = {}
    for ly in LAYERS:
        h, w = hypo(g, ly)
        out[ly] = np.histogram(h[s].ravel(), bins, weights=(w[s] * n5[s, None]).ravel())[0]
    t = pd.DataFrame({"depth_from": bins[:-1], "depth_to": bins[1:], "N5_three": out["l3"], "N5_one": out["l1"]})
    t["diff"] = t.N5_three - t.N5_one
    return t[(t.N5_three > 0) | (t.N5_one > 0)]


def nest_depths(ev, g):
    """Depths of the nest events with a measured depth against the C14 zone of the nest cells."""
    e = ev[(ev.W_jujuy_nest > 0) & (ev.depth_kind == "measured")]
    z = g[g.dom_nest]
    q = lambda x: np.percentile(x, [5, 25, 50, 75, 95])
    return pd.DataFrame({"what": ["nest events depth", "cell slab top", "cell lower depth"],
                         **{f"p{p}": v for p, v in zip((5, 25, 50, 75, 95), np.array([q(e.depth), q(z.top), q(z.lsd)]).T)},
                         "n": [len(e), len(z), len(z)]})


def run():
    pd.set_option("display.width", 250, "display.max_columns", 40)
    TAB.mkdir(exist_ok=True)
    g, ev = cells(), events()
    cal, pick = calibration(ev, g)
    cal.round(3).to_csv(TAB / f"calibration_{DATE}.csv", index=False)
    print(cal.pivot_table(index=["decl", "unit"], columns="n", values="dll").round(1).to_string())
    print("n chosen:", pick)
    P = patterns(ev, g, pick)
    pat = pd.concat([g[["lon", "lat", "top"] + [f"dom_{s['short']}" for s in CLASSES.values()]], P], axis=1)
    pat.to_csv(TAB / f"pattern_{DATE}.csv", index=False, float_format="%.6e")
    sums = pd.DataFrame([dict(column=c, domain_sum=P[c][g["dom_" + c.split("_")[1]]].sum(), outside=P[c][~g["dom_" + c.split("_")[1]]].sum(),
                              cells=int((P[c] > 0).sum())) for c in P.columns])
    sums.to_csv(TAB / f"pattern_sums_{DATE}.csv", index=False)
    print(sums.to_string(index=False))
    pd.DataFrame([dict(cls=c, decl=k, n=n, events=float(ev[ev[k] & ev.comp]["W_" + c].sum())) for (c, k), n in pick.items()]).to_csv(
        TAB / f"kernel_n_{DATE}.csv", index=False)
    F = fits()
    br = branches()
    tot, drop, share = write(g, P, F, br, ev)
    drop.to_csv(TAB / f"drop_{RUN}.csv", index=False)
    share.to_csv(TAB / f"class_share_{DATE}.csv", index=False, float_format="%.5f")
    print(drop[["group", "decl", "shape", "ab", "cells", "kept", "dropped", "removed"]].to_string(index=False))
    rt, ec = rate_tables(tot, br)
    rt.to_csv(TAB / f"rates_{DATE}.csv", index=False)
    ec.to_csv(TAB / f"edge_check_{DATE}.csv", index=False)
    print(rt[["cls", "decl", "shape", "ab", "b", "m_top", "sources", "N5.5", "N6", "N7", "N7.5", "N8"]].round(5).to_string(index=False))
    print("edge check, max relative difference:", ec.max_rel.max())
    south(g, P, F).round(5).to_csv(TAB / f"south36_layers_{DATE}.csv", index=False)
    nest_depths(ev, g).round(1).to_csv(TAB / f"nest_depths_{DATE}.csv", index=False)
    print(f"{len(br)} branches, {len(br) * len(GROUPS)} files in {NR}")


if __name__ == "__main__":
    run()
