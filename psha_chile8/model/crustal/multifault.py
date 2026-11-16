"""Multi-fault ruptures, quick estimate (WORKPLAN_multifault.md): rupture set by the UCERF3 plausibility filters
(Milner et al. 2013, Table T1), Leonard (2014) magnitudes, and the moment partition of SHERIFS (Chartier et al.
2017, 2019), reimplemented. Whole faults of the database are the units.

Simplifications of the quick estimate: jump distance between the surface traces (most arc faults are near vertical);
no Coulomb filter; no sinistral / dextral azimuth reversal. Writes tables/mf_<tag>_<DATE>.csv and
figs/mf_<tag>_<DATE>.png.
"""
import math
import sys

import numpy as np
import pandas as pd
from shapely.geometry import LineString

import faults as F
import join as J

sys.path.insert(0, str(F.ROOT / "model" / "faults"))
import geo  # noqa: E402

TAB, FIG = F.HERE / "tables", F.HERE / "figs"

# settings
DATE = "2026-11-16e"
DB, CLS = "A", "arc"
PSI = 0.8
DEPTHS = (10.0, 20.0)
# UCERF3 plausibility filters (Milner et al. 2013, Table T1)
JUMP_KM, AZ_JUNCTION, AZ_TOTAL, AZ_CUM, RAKE_CUM = 5.0, 60.0, 60.0, 560.0, 180.0
# only main traces link (Pablo, 15 Nov): slip rate at least MIN_SR mm/yr; in A that is GEM's class 1-5 mm/yr (3.0),
# the secondary traces (class 0.1-1, 0.5 mm/yr) rupture alone
MIN_SR = 1.0
# main-trace slip rate per database: in B the MASCSN rows start at 2 mm/yr, main traces from 3 (15 Nov)
MAIN_SR = {"A": 1.0, "B": 3.0, "Bmm": 3.0}
# classes whose faults enter the quick estimate (the Liquine-Ofqui traces south of 46.3 S are classed Patagonia)
CLASSES_LINK = ("arc", "patagonia")
# SHERIFS (Chartier et al. 2017): slip increment, number of top bins for the anchor
DSR, NTOP = 0.01, 3
SEED = 1
# Liquine-Ofqui run (Pablo, 16 Nov): the main traces of system LOFS link, every other fault keeps its single-fault
# rates (six shapes, Leonard); depth 10 km (Sielfeld et al. 2019); chain Mmax capped at the class Mmax
LOFS = "Liquiñe–Ofqui"
LOFS_DEPTH = 10.0
# depths and jumps of the jump-distance study (Pablo, 16 Nov)
DEPTHS_LOFS = (10.0, 20.0)
JUMPS_STUDY = (5.0, 10.0, 15.0, 20.0)
# large-event check before 1976, out of the fit: the historical steps of the B11 table (table_2026-11-16)
HIST = ((7.0, 1905.0), (7.5, 1830.0))
PSIS = (0.6, 0.8, 1.0)
# jump distance of the multi-fault branch: 15 km (Pablo, 16 Nov); 5 and 10 km kept as the quick-estimate comparison
JUMP_LOFS = 15.0
JUMPS = (5.0, 10.0, 15.0)
SEEDS = tuple(range(1, 11))
# rupture set: "strict" = the UCERF3 path rules on 5 km subsections merged to whole-fault scenarios (rupset.py,
# Pablo, 16 Nov); "chains" = the earlier whole-fault chains. Scenarios above the class Mmax are dropped.
RUPSET = "strict"


def adiff(a, b):
    return (b - a + 180.0) % 360.0 - 180.0


def links(s):
    """Pairs of main faults (slip rate >= MIN_SR) whose traces come within JUMP_KM (exact distance between the traces in
    UTM 19S), with the closest points (lon, lat) on each."""
    from pyproj import Transformer
    from shapely.ops import nearest_points, transform
    to = Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True).transform
    back = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True).transform
    g = [transform(to, LineString(t)) for t in s.trace]
    main = (s.sr >= MIN_SR).to_numpy()
    out = {}
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            if not (main[i] and main[j]) or g[i].distance(g[j]) > JUMP_KM * 1e3:
                continue
            a, b = nearest_points(g[i], g[j])
            pa, pb = np.array(back(a.x, a.y)), np.array(back(b.x, b.y))
            out[(i, j)] = (pa, pb)
            out[(j, i)] = (pb, pa)
    return out


def direction(t, p_in, p_out):
    """Azimuth of a fault traversed from the end nearer p_in to the end nearer p_out (p None: its far end)."""
    t = np.asarray(t)
    e = [t[0], t[-1]]
    d = lambda p, q: math.hypot((p[0] - q[0]) * math.cos(math.radians(q[1])), p[1] - q[1])
    if p_in is not None:
        a = e[0] if d(e[0], p_in) <= d(e[-1], p_in) else e[-1]
    else:
        a = e[0] if d(e[-1], p_out) <= d(e[0], p_out) else e[-1]
    b = e[-1] if a is e[0] else e[0]
    return geo.GEOD.inv(a[0], a[1], b[0], b[1])[0] % 360.0


def chains(s, lk):
    """Linear chains of two or more faults that pass the azimuth and rake filters of UCERF3."""
    nb = {}
    for i, j in lk:
        nb.setdefault(i, []).append(j)
    out = []

    def walk(path, azs, cum, rk):
        i = path[-1]
        for j in nb.get(i, []):
            if j in path:
                continue
            p_i, p_j = lk[(i, j)]
            prev = lk[(path[-2], i)][1] if len(path) > 1 else None
            az_i = direction(s.trace[i], prev, p_i)
            az_j = direction(s.trace[j], p_j, None)
            dj = abs(adiff(az_i, az_j))
            if dj > AZ_JUNCTION:
                continue
            a2 = azs[:-1] + [az_i, az_j]
            if abs(adiff(a2[0], az_j)) > AZ_TOTAL:
                continue
            c2 = cum + dj
            r2 = rk + abs(adiff(s.rake[i], s.rake[j]))
            if c2 > AZ_CUM or r2 > RAKE_CUM:
                continue
            out.append(tuple(path + [j]))
            walk(path + [j], a2, c2, r2)

    for i in range(len(s)):
        walk([i], [0.0], 0.0, 0.0)
    uniq = {}
    for c in out:
        uniq.setdefault(frozenset(c), c)
    return list(uniq.values())


def sources(s, ch, z):
    """Single faults and chains with their area (m2), members and the bins they host (on the grid of rates.py)."""
    W = z / np.sin(np.radians(s.dip.to_numpy()))
    A = s.L.to_numpy() * W
    mx = np.array([F.R.on_grid(F.R.leonard(a, r)) for a, r in zip(A, s.rake)])
    src = [dict(members=(i,), area=A[i] * 1e6, lo=F.R.MMIN, hi=mx[i]) for i in range(len(s))]
    for c in ch:
        a = A[list(c)].sum()
        big = max(c, key=lambda k: s.L[k])
        hi = F.R.on_grid(F.R.leonard(a, float(s.rake[big])))
        if hi > F.class_mmax(s.cls[big]) + 1e-9:
            continue
        lo = round(max(mx[list(c)]) + F.R.DM, 2)
        if hi >= lo - 1e-9:
            src.append(dict(members=tuple(c), area=a * 1e6, lo=lo, hi=hi))
    return src, mx


def components(n, src):
    p = list(range(n))

    def f(x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    for q in src:
        for k in q["members"][1:]:
            p[f(k)] = f(q["members"][0])
    return np.array([f(i) for i in range(n)])


def partition(src, budget, b, rng):
    """
    SHERIFS moment partition (Chartier et al. 2017, section 2, step 4) on one fault system.

    budget: slip-rate budget per fault (mm/yr). Returns the rate per source and bin (dict), the NMS slip per fault
    (mm/yr) and the bins.
    """
    nb = F.NB
    m = F.R.MMIN + F.R.DM * np.arange(nb)
    top = max(q["hi"] for q in src)
    kb = np.arange(nb)[(m <= top + 1e-9)]
    g = 10 ** (-b * m[kb])
    g = g / g.sum()
    wmo = g * F.R.m0(m[kb])
    wmo = wmo / wmo.sum()
    host = {k: np.array([i for i, q in enumerate(src) if q["lo"] - 1e-9 <= m[k] <= q["hi"] + 1e-9], int) for k in kb}
    fk = list(budget)
    loc = {f: n for n, f in enumerate(fk)}
    mem = [np.array([loc[f] for f in q["members"]]) for q in src]
    left = np.array([budget[f] for f in fk], float)
    of = [[] for _ in fk]
    for n, x in enumerate(mem):
        for f in x:
            of[f].append(n)
    alive = np.array([(left[x] > 1e-12).all() for x in mem])
    topf = {f for t in kb[-NTOP:] for n in host[t] for f in mem[n]}
    hit = any(left[f] <= 1e-12 for f in topf)
    rate = np.zeros((len(src), nb))
    col = np.zeros(nb)
    nms = np.zeros(len(fk))
    target = None
    topk = kb[-NTOP:]
    open_ = np.ones(len(kb), bool)
    while open_.any():
        p = wmo * open_
        k = kb[rng.choice(len(kb), p=p / p.sum())]
        cand = host[k][alive[host[k]]]
        if not cand.size:
            open_[list(kb).index(k)] = False
            continue
        i = cand[rng.integers(len(cand))]
        x = mem[i]
        d = min(DSR, left[x].min())
        dr = F.R.MU * src[i]["area"] * d * 1e-3 / F.R.m0(m[k])
        if target is not None and col[k] + dr > target[k]:
            nms[x] += d
        else:
            rate[i, k] += dr
            col[k] += dr
        left[x] -= d
        for f in x[left[x] <= 1e-12]:
            alive[of[f]] = False
            hit = hit or f in topf
        if target is None and hit:
            r = rate[:, topk].sum(axis=0)
            if len(r) == NTOP:
                r[0] = min(r[0], 2 * r[1:].mean())
            gl = g[-len(topk):]
            lvl = np.mean(r / gl)
            target = np.zeros(nb)
            target[kb] = lvl * g
    nms = {f: float(nms[loc[f]]) for f in fk}
    return rate, nms


def budget(s, z):
    """Slip-rate budget per fault (mm/yr): psi times the slip rate; for the MASCSN-moment variant the slip that
    carries the fault's moment (MASCSN FaultQuake budget plus our rules on GEM rows) over our area L x z / sin(dip)."""
    W = z / np.sin(np.radians(s.dip.to_numpy())) * 1e3
    mo = F.R.MU * s.Lsr.to_numpy() * 1e3 * W * s.sr_used.to_numpy() * 1e-3 + s.fixed.to_numpy()
    return PSI * mo / (F.R.MU * s.L.to_numpy() * 1e3 * W) * 1e3


def run(z, s, ch, b, rng):
    src, mx = sources(s, ch, z)
    comp = components(len(s), src)
    rate = np.zeros((len(src), F.NB))
    nms = np.zeros(len(s))
    for c in np.unique(comp):
        fs = np.where(comp == c)[0]
        idx = [i for i, q in enumerate(src) if comp[q["members"][0]] == c]
        sub = [src[i] for i in idx]
        bb = budget(s, z)
        bud = {int(f): float(bb[f]) for f in fs}
        r, n = partition(sub, bud, b, rng)
        rate[idx] = r
        for f, v in n.items():
            nms[f] = v
    return src, mx, rate, nms


def main(tag="A_arc_quick"):
    s, rr, _ = F.load(DB)
    keep = s.cls.isin(CLASSES_LINK).to_numpy()
    s, rr = s[keep].reset_index(drop=True), rr[keep]
    # the target b of the arc for every system of the quick estimate (Patagonia, forearc b, differs by 0.02)
    b = F.bvals()[CLS]
    lk = links(s)
    ch = chains(s, lk)
    print(f"{len(s)} faults ({', '.join(CLASSES_LINK)}), {int((s.sr >= MIN_SR).sum())} main, {len(lk) // 2} links "
          f"within {JUMP_KM} km, {len(ch)} chains pass the filters")
    rng = np.random.default_rng(SEED)
    ft = J.fits()
    import arc
    from scipy import stats
    n, T = arc.observed()
    fit = ft[(CLS, "taper")]
    k = int(round((F.R.MMIN - J.CENTRES[0]) / 0.1))
    sel = J.CENTRES >= 5.95
    isarc = (s.cls == CLS).to_numpy()
    rows, mfds = [], {}
    for z in DEPTHS:
        src, mx, rate, nms = run(z, s, ch, b, rng)
        # class of a rupture: that of its longest member
        ia = np.array([isarc[max(q["members"], key=lambda f: s.L[f])] for q in src])
        lin = np.array([len(q["members"]) > 1 for q in src])
        tot = np.zeros(J.CENTRES.size)
        tot[k:k + F.NB] = rate[ia].sum(axis=0)[:J.CENTRES.size - k]
        bg = J.background(fit, tot)
        e = float(((tot + bg)[sel] * T[sel]).sum())
        obs = float(n[sel].sum())
        L = max((sum(s.L[list(q["members"])]) for i, q in enumerate(src) if lin[i] and rate[i].sum() > 0), default=0)
        bud = budget(s, z)[isarc]
        rows.append(dict(depth=z, faults=int(isarc.sum()), chains=int((lin & ia).sum()),
                         chains_with_rate=int(((rate.sum(1) > 0) & lin & ia).sum()), longest_km=L,
                         mmax_single=float(mx[isarc].max()), mmax_chain=max((q["hi"] for i, q in enumerate(src) if lin[i] and ia[i]), default=np.nan),
                         N6=float(tot[sel].sum()), N7=float(tot[J.CENTRES >= 6.95].sum()), N75=float(tot[J.CENTRES >= 7.45].sum()),
                         share_linked_N6=float(rate[lin & ia].sum() / rate[ia].sum()),
                         nms_share=float(nms[isarc].sum() / bud.sum()), nms_max=float((nms[isarc] / bud).max()),
                         expected=e, observed=obs, p=float(stats.poisson.cdf(round(obs), e)), fit_N6=float(fit[sel].sum())))
        mfds[z] = (tot, rate[ia], [q for q, a in zip(src, ia) if a], nms)
    t = pd.DataFrame(rows)
    t.round(5).to_csv(TAB / f"mf_{tag}_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        print(t.round(3).to_string(index=False))
    figure(mfds, fit, n, T, tag, rr[isarc], s)
    return t, mfds, s, ch


def figure(mfds, fit, n, T, tag, rr, s):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(F.ROOT))
    import palette as P
    P.apply()
    m = J.CENTRES
    ok = (n > 0) & (T > 0)
    k = int(round((F.R.MMIN - m[0]) / 0.1))
    f, ax = plt.subplots(1, len(mfds), figsize=(6 * len(mfds), 5.2), sharey=True)
    for a, (z, (tot, rate, src, nms)) in zip(np.atleast_1d(ax), mfds.items()):
        j = [i for i, (p, zz, sh) in enumerate(F.BR) if p == PSI and zz == z]
        old = np.zeros(m.size)
        old[k:k + F.NB] = rr[:, j].sum(axis=0).mean(axis=0)[:m.size - k]
        lin = [i for i, q in enumerate(src) if len(q["members"]) > 1]
        sl = np.zeros(m.size)
        sl[k:k + F.NB] = rate[lin].sum(axis=0)[:m.size - k]
        bg = J.background(fit, tot)
        a.plot(m, np.where(fit > 0, fit, np.nan), color="0.55", lw=2.5, label="catalogue fit")
        a.plot(m, np.where(old > 0, old, np.nan), color=P.SERIES[1], lw=1.5, ls="--", label="faults alone (Leonard, mean of shapes)")
        a.plot(m, np.where(tot > 0, tot, np.nan), color=P.SERIES[1], lw=2.2, marker="o", ms=3, label="faults with multi-fault ruptures")
        a.plot(m, np.where(sl > 0, sl, np.nan), color=P.SERIES[5], lw=1.5, label="of which multi-fault")
        a.plot(m, np.where(bg > 0, bg, np.nan), color=P.CLASS_COLOR[CLS], lw=2, label="background")
        a.plot(m[ok], (n / np.where(T > 0, T, 1))[ok], "s", color="k", mfc="white", ms=5, label="observed")
        a.set_yscale("log")
        a.set_xlim(4.9, 8.6)
        a.set_ylim(1e-5, 1)
        a.set_xlabel("Mw (0.1 bins)")
        a.set_title(f"thickness {z:g} km, ψ {PSI}")
    np.atleast_1d(ax)[0].set_ylabel("events per year in the bin")
    np.atleast_1d(ax)[0].legend(fontsize=8.5, loc="lower left")
    f.suptitle(f"Crustal arc, database {DB}: multi-fault ruptures (quick estimate)", x=0.06, ha="left")
    f.tight_layout()
    f.savefig(FIG / f"mf_{tag}_{DATE}.png", dpi=160)
    plt.close(f)


def qgis(tag="A"):
    """Shapefiles for QGIS (folder qgis/): the faults with whether they may link and their group, the jumps between
    linked faults, and every chain that passes the filters with its length and Mmax at 10 and 20 km."""
    import geopandas as gpd
    from shapely.geometry import MultiLineString
    s, _, _ = F.load(DB)
    lk = links(s)
    ch = chains(s, lk)
    src = {z: sources(s, ch, z)[0] for z in DEPTHS}
    grp = components(len(s), [dict(members=c) for c in ch])
    nin = np.zeros(len(s), int)
    for c in ch:
        nin[list(c)] += 1
    size = pd.Series(grp).map(pd.Series(grp).value_counts()).to_numpy()
    d = F.HERE / "qgis"
    d.mkdir(exist_ok=True)
    fl = gpd.GeoDataFrame({"fid": s.fid, "name": s["name"].str[:60], "cls": s.cls, "sr": s.sr_used, "len_km": s.L.round(1),
                           "main": (s.sr >= MIN_SR).astype(int), "group": np.where(size > 1, grp, -1),
                           "n_chains": nin, "mmax10": s.mmax10, "mmax20": s.mmax20},
                          geometry=[LineString(t) for t in s.trace], crs="EPSG:4326")
    fl.to_file(d / f"mf_{tag}_faults_{DATE}.shp")
    jp = gpd.GeoDataFrame([dict(a=s.fid[i], b=s.fid[j], km=round(float(geo.GEOD.inv(p[0][0], p[0][1], p[1][0], p[1][1])[2]) / 1e3, 2))
                           for (i, j), p in lk.items() if i < j],
                          geometry=[LineString([p[0], p[1]]) for (i, j), p in lk.items() if i < j], crs="EPSG:4326")
    pairs = {frozenset((c[k], c[k + 1])) for c in ch for k in range(len(c) - 1)}
    jp["used"] = [int(frozenset((i, j)) in pairs) for (i, j) in lk if i < j]
    jp.to_file(d / f"mf_{tag}_jumps_{DATE}.shp")
    rows, geoms = [], []
    for c in ch:
        hi = {z: next((q["hi"] for q in src[z] if q["members"] == tuple(c)), np.nan) for z in DEPTHS}
        rows.append(dict(n_faults=len(c), members="+".join(s.fid[k] for k in c)[:250], len_km=round(float(s.L[list(c)].sum()), 1),
                         group=int(grp[c[0]]), mmax10=hi[10.0], mmax20=hi[20.0]))
        geoms.append(MultiLineString([s.trace[k] for k in c]))
    cg = gpd.GeoDataFrame(rows, geometry=geoms, crs="EPSG:4326").sort_values("len_km", ascending=False)
    cg.to_file(d / f"mf_{tag}_chains_{DATE}.shp")
    print(f"{int(fl.main.sum())} main faults of {len(fl)}, {len(jp)} jumps, {len(cg)} chains, "
          f"{len(set(grp[size > 1]))} groups; longest chain {cg.len_km.max():.0f} km ({cg.iloc[0].members})")
    print(cg.groupby("group").agg(chains=("len_km", "size"), longest=("len_km", "max"), mmax20=("mmax20", "max")).to_string())
    return fl, jp, cg


def strict(sl, jk):
    """Whole-fault scenarios of the strict UCERF3 rupture set at jump jk (rupset.py), as tuples of fault indices."""
    import rupset as R
    R.JUMP_KM, R.MIN_SR = jk, MIN_SR
    rups, _ = R.ruptures(sl, LOFS_DEPTH, main_only=MIN_SR > 0)
    return [tuple(r["faults"]) for r in R.scenarios(rups)]


def lofs(db="A", jumps=JUMPS, depths=(LOFS_DEPTH,), splays=False, tag=None):
    """Liquine-Ofqui multi-fault branch: SHERIFS on the LOFS faults of database A (main traces link), the other arc
    faults with their single-fault rates (branch psi and depth, weighted mean of the shapes). Arc count test per
    jump distance, depth, psi and seed (Mw >= 6 since 1976), and the large-event check before 1976 (HIST). Writes tables/mf_<tag>_<DATE>.csv (one row per run) and figs/mf_<tag>_<DATE>.png."""
    global PSI, JUMP_KM, MIN_SR
    tag = tag or (f"{db}_lofs_splays" if splays else f"{db}_lofs")
    MIN_SR = 0.0 if splays else MAIN_SR[db]
    import geopandas as gpd
    import arc
    from scipy import stats
    gpd.options.io_engine = "fiona"
    s, rr, _ = F.load(db)
    sysn = gpd.read_file(F.DBS[db]["file"]).set_index("fid")["system"]
    isl = s.fid.map(sysn).eq(LOFS).to_numpy()
    isarc = (s.cls == CLS).to_numpy()
    sl = s[isl].reset_index(drop=True)
    b = F.bvals()[CLS]
    fit = J.fits()[(CLS, "taper")]
    n, T = arc.observed()
    k0 = int(round((F.R.MMIN - J.CENTRES[0]) / 0.1))
    s6, s7 = J.CENTRES >= 5.95, J.CENTRES >= 6.95
    o6, o7 = float(n[s6].sum()), float(n[s7].sum())
    import gr
    import background as BG
    d = gr.load(BG.CAT, mlow=6.95)
    wa = d.W_arc.to_numpy() * gr.magw(d.mw_sigma.to_numpy(), b)
    te = gr.tend(gr.load(BG.CAT))
    hist = {M: (float(wa[(d.mw.to_numpy() >= M - 0.05) & (d.t.to_numpy() >= y)].sum()), te - y) for M, y in HIST}
    la = (sl.cls == CLS).to_numpy()
    rows, keep = [], {}
    for jk, z in [(a, c) for a in jumps for c in depths]:
        JUMP_KM = jk
        ch = chains(sl, links(sl)) if RUPSET == "chains" else strict(sl, jk)
        for ps in PSIS:
            PSI = ps
            j = [i for i, (p, zz, _) in enumerate(F.BR) if p == ps and zz == z]
            w = F.W[j] / F.W[j].sum()
            other = np.zeros(J.CENTRES.size)
            other[k0:k0 + F.NB] = (rr[isarc & ~isl][:, j] * w[None, :, None]).sum(axis=(0, 1))[:J.CENTRES.size - k0]
            for sd in SEEDS:
                src, mx, rate, nms = run(z, sl, ch, b, np.random.default_rng(sd))
                ia = np.array([la[max(q["members"], key=lambda f: sl.L[f])] for q in src])
                lin = np.array([len(q["members"]) > 1 for q in src])
                lo = np.zeros(J.CENTRES.size)
                lo[k0:k0 + F.NB] = rate[ia].sum(axis=0)[:J.CENTRES.size - k0]
                tot = lo + other
                bg = J.background(fit, tot)
                e6, e7 = float(((tot + bg)[s6] * T[s6]).sum()), float(((tot + bg)[s7] * T[s7]).sum())
                used = (rate.sum(1) > 0) & lin
                bud = budget(sl, z)
                hx = {M: (float((tot + bg)[J.CENTRES >= M - 0.05].sum() * T_), o) for M, (o, T_) in hist.items()}
                rows.append(dict(jump=jk, depth=z, psi=ps, seed=sd, chains=len(ch), chains_used=int(used.sum()),
                                 longest_km=max((float(sl.L[list(q["members"])].sum()) for q, u in zip(src, used) if u), default=0.0),
                                 mmax=float(max(q["hi"] for q, r in zip(src, rate) if r.sum() > 0)),
                                 N6=float(tot[s6].sum()), N7=float(tot[s7].sum()), N6_lofs=float(lo[s6].sum()),
                                 N6_other=float(other[s6].sum()), linked_N6=float(rate[lin & ia].sum() / max(rate[ia].sum(), 1e-30)),
                                 nms_share=float(nms.sum() / bud.sum()), nms_max=float((nms / bud).max()),
                                 exp6=e6, obs6=o6, p6=float(stats.poisson.cdf(round(o6), e6)),
                                 exp7=e7, obs7=o7, p7=float(1 - stats.poisson.cdf(round(o7) - 1, e7)),
                                 **{f"exp{M:g}_hist": e for M, (e, o) in hx.items()},
                                 **{f"obs{M:g}_hist": o for M, (e, o) in hx.items()},
                                 **{f"p{M:g}_hist": float(1 - stats.poisson.cdf(round(o) - 1, e)) for M, (e, o) in hx.items()}))
                keep[(jk, z, ps, sd)] = tot
    t = pd.DataFrame(rows)
    t.round(5).to_csv(TAB / f"mf_{tag}_{DATE}.csv", index=False)
    np.savez_compressed(TAB / f"mf_{tag}_mfd_{DATE}.npz", centres=J.CENTRES,
                        **{f"j{jk:g}_z{z:g}_psi{ps:g}": np.array([keep[(jk, z, ps, sd)] for sd in SEEDS])
                           for jk in jumps for z in depths for ps in PSIS})
    g = t.groupby(["jump", "depth", "psi"]).agg(exp6=("exp6", "mean"), exp6_sd=("exp6", "std"), p6=("p6", "mean"),
                                        exp7=("exp7", "mean"), p7=("p7", "mean"), N6_lofs=("N6_lofs", "mean"),
                                        N6_other=("N6_other", "mean"), linked=("linked_N6", "mean"),
                                        nms=("nms_share", "mean"), nms_max=("nms_max", "max"), longest=("longest_km", "max"),
                                        mmax=("mmax", "max"), chains=("chains", "first"),
                                        exp7_hist=("exp7_hist", "mean"), p7_hist=("p7_hist", "mean"),
                                        exp75_hist=("exp7.5_hist", "mean"), p75_hist=("p7.5_hist", "mean"))
    with pd.option_context("display.width", 250):
        print(f"{len(sl)} LOFS faults, {int((sl.sr >= MIN_SR).sum())} main; observed arc Mw>=6 {o6:.2f}, Mw>=7 {o7:.2f}; "
              f"fit {float((fit[s6] * T[s6]).sum()):.2f}")
        print("before 1976 (HIST):", {M: round(o, 2) for M, (o, _) in hist.items()})
        print(g.round(3).to_string())
    if len(depths) == 1:
        lofs_figure({(a, p, s_): v for (a, z, p, s_), v in keep.items()}, fit, n, T, tag, jumps, db)
    return t, g


def lofs_figure(keep, fit, n, T, tag, jumps, db):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(F.ROOT))
    import palette as P
    P.apply()
    m = J.CENTRES
    ok = (n > 0) & (T > 0)
    f, ax = plt.subplots(1, len(jumps), figsize=(5.4 * len(jumps) + 1, 5.2), sharey=True, squeeze=False)
    ax = ax[0]
    for a, jk in zip(ax, jumps):
        a.plot(m, np.where(fit > 0, fit, np.nan), color="0.55", lw=2.5, label="catalogue fit")
        for c, ps in zip(P.SERIES, PSIS):
            r = np.array([keep[(jk, ps, sd)] for sd in SEEDS])
            mu = r.mean(axis=0)
            a.fill_between(m, np.where(r.min(0) > 0, r.min(0), np.nan), np.where(r.max(0) > 0, r.max(0), np.nan), color=c, alpha=0.2, lw=0)
            a.plot(m, np.where(mu > 0, mu, np.nan), color=c, lw=2, label=f"faults, ψ {ps:g}")
        a.plot(m[ok], (n / np.where(T > 0, T, 1))[ok], "s", color="k", mfc="white", ms=5, label="observed")
        a.set_yscale("log")
        a.set_xlim(4.9, 8.4)
        a.set_ylim(1e-5, 1)
        a.set_xlabel("Mw (0.1 bins)")
        a.set_title(f"jump ≤ {jk:g} km")
    ax[0].set_ylabel("events per year in the bin")
    ax[0].legend(fontsize=9, loc="lower left")
    f.suptitle(f"Crustal arc, {F.DBS[db]['name']}: Liquiñe–Ofqui multi-fault ruptures, thickness 10 km (band: 10 seeds)", x=0.06, ha="left")
    f.tight_layout()
    f.savefig(FIG / f"mf_{tag}_{DATE}.png", dpi=160)
    plt.close(f)


if __name__ == "__main__":
    # all rows on the strict rupture set (Pablo, 16 Nov)
    lofs("A", JUMPS, DEPTHS_LOFS)
    lofs("A", JUMPS, DEPTHS_LOFS, splays=True)
    for d in ("B", "Bmm"):
        lofs(d, (JUMP_LOFS,), DEPTHS_LOFS)
