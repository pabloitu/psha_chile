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
DATE = "2026-11-15"
DB, CLS = "A", "arc"
PSI = 0.8
DEPTHS = (10.0, 20.0)
# UCERF3 plausibility filters (Milner et al. 2013, Table T1)
JUMP_KM, AZ_JUNCTION, AZ_TOTAL, AZ_CUM, RAKE_CUM = 5.0, 60.0, 60.0, 560.0, 180.0
# only main traces link (Pablo, 15 Nov): slip rate at least MIN_SR mm/yr; in A that is GEM's class 1-5 mm/yr (3.0),
# the secondary traces (class 0.1-1, 0.5 mm/yr) rupture alone
MIN_SR = 1.0
# classes whose faults enter the quick estimate (the Liquine-Ofqui traces south of 46.3 S are classed Patagonia)
CLASSES_LINK = ("arc", "patagonia")
# SHERIFS (Chartier et al. 2017): slip increment, number of top bins for the anchor
DSR, NTOP = 0.01, 3
SEED = 1


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
        hi = F.R.on_grid(F.R.leonard(a, float(s.rake[max(c, key=lambda k: s.L[k])])))
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
    host = {k: [i for i, q in enumerate(src) if q["lo"] - 1e-9 <= m[k] <= q["hi"] + 1e-9] for k in kb}
    left = dict(budget)
    rate = np.zeros((len(src), nb))
    nms = {f: 0.0 for f in budget}
    target = None
    topk = kb[-NTOP:]
    open_ = np.ones(len(kb), bool)
    while open_.any():
        p = wmo * open_
        k = kb[rng.choice(len(kb), p=p / p.sum())]
        cand = [i for i in host[k] if all(left[f] > 1e-12 for f in src[i]["members"])]
        if not cand:
            open_[list(kb).index(k)] = False
            continue
        i = cand[rng.integers(len(cand))]
        d = min(DSR, min(left[f] for f in src[i]["members"]))
        dr = F.R.MU * src[i]["area"] * d * 1e-3 / F.R.m0(m[k])
        if target is not None and rate[:, k].sum() + dr > target[k]:
            for f in src[i]["members"]:
                nms[f] += d
        else:
            rate[i, k] += dr
        for f in src[i]["members"]:
            left[f] -= d
        if target is None and any(left[f] <= 1e-12 for i2 in set(sum((host[t] for t in topk), [])) for f in src[i2]["members"]):
            r = rate[:, topk].sum(axis=0)
            if len(r) == NTOP:
                r[0] = min(r[0], 2 * r[1:].mean())
            gl = g[-len(topk):]
            lvl = np.mean(r / gl)
            target = np.zeros(nb)
            target[kb] = lvl * g
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
        a.set_title(f"depth {z:g} km, ψ {PSI}")
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


if __name__ == "__main__":
    main()
