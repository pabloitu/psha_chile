"""C8: CAT check figures and the D-MAG-12 acceptance tests, and the comparison with psha_chile8 17g.

Usage: python -m psha9.catalog.figs run_dir
"""
import json
import sys
import zlib

import cartopy.crs as ccrs
import matplotlib
import numba as nb
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
from scipy.optimize import brentq
from scipy.stats import chi2

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import magnitude as G
from .match import CFG, ROOT, tsec, year

K = CFG["checks"]
PC, MERC = ccrs.PlateCarree(), ccrs.Mercator()
DM = 0.1
GROUP = {"shallow": "#b0b0b0", "deep": "#6e6e6e", "below 150 km": "#1e1e1e", "all": "#4a4a4a", "no depth": "#2a78b5"}
NAME = {"GUC ML": "CSN ML", "SJA ML": "INPRES ML"}
plt.rcParams.update({"font.family": "Ubuntu", "font.size": 7, "axes.facecolor": "#eaeaf2", "axes.edgecolor": "none",
                     "axes.grid": True, "grid.color": "white", "axes.axisbelow": True})


# statistics
@nb.njit(cache=True)
def gk(t, la, lo, m):
    """Gardner and Knopoff (1974) windows; t in days; True for dependent events."""
    n = len(t)
    order = np.argsort(-m)
    dep = np.zeros(n, np.bool_)
    ts = np.argsort(t)
    tsorted = t[ts]
    for i in order:
        if dep[i]:
            continue
        M = m[i]
        T = 10 ** (0.032 * M + 2.7389) if M >= 6.5 else 10 ** (0.5409 * M - 0.547)
        L = 10 ** (0.1238 * M + 0.983)
        for jj in range(np.searchsorted(tsorted, t[i]), np.searchsorted(tsorted, t[i] + T)):
            j = ts[jj]
            if j == i or dep[j] or m[j] > M:
                continue
            p1, p2 = np.radians(la[i]), np.radians(la[j])
            a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo[j] - lo[i]) / 2) ** 2
            if 2 * 6371.0 * np.arcsin(np.sqrt(min(a, 1.0))) <= L:
                dep[j] = True
    return dep


def aki(m, mc):
    k = m >= mc - 1e-9
    return np.log10(np.e) / (m[k].mean() - (mc - DM / 2)) if k.sum() >= 2 else np.nan


def trunc_b(m, lo, hi):
    """b of a Gutenberg-Richter law doubly truncated to [lo, hi), binned magnitudes."""
    x = m[(m >= lo - 1e-9) & (m < hi - 1e-9)]
    c = np.round(np.arange(lo, hi - 1e-9, DM), 2)
    f = lambda beta: np.sum(c * np.exp(-beta * c)) / np.exp(-beta * c).sum() - x.mean()
    try:
        return (brentq(f, 0.01, 10) / np.log(10), len(x)) if len(x) >= 20 else (np.nan, len(x))
    except ValueError:
        return np.nan, len(x)


def band(n, p=K["band"]):
    """Interval of the Poisson mean compatible with an observed count n (Garwood)."""
    return (chi2.ppf((1 - p) / 2, 2 * n) / 2 if n else 0.0), chi2.ppf((1 + p) / 2, 2 * n + 2) / 2


def acceptance(c):
    """
    D-MAG-12 tests 1-3 and 5 on the catalogue c (earthquakes in the 17g domain): b over the fit floors, the declustered
    M >= 5.5 rate per period, N >= 7 and N 6.5-7 predicted from a fit on 5.0-6.5, and combs or heaps at 4.5-5.5.
    Returns the test rows and the b, rate and histogram tables for the figure.
    """
    m = np.round(c.mw.to_numpy(float) + 1e-9, 1)
    yr, t = c.yr.to_numpy(float), c.t.to_numpy(float) / 86400
    ok = np.isfinite(m) & np.isfinite(t) & (yr >= K["y0"])
    dep = np.zeros(len(m), bool)
    k = ok & (m >= K["decl_m"])
    dep[k] = gk(t[k], c.lat.to_numpy(float)[k], c.lon.to_numpy(float)[k], m[k])
    rows, B = [], {}
    add = lambda test, sub, q, v, lim=None, p=None: rows.append(
        {"test": test, "subset": sub, "quantity": q, "value": v, "limit": lim, "passed": p})
    show = np.round(np.arange(4.3, 6.51, 0.1), 1)
    fl = np.round(np.arange(K["floors"][0], K["floors"][1] + 1e-9, 0.1), 1)
    for y0 in K["b_periods"]:
        for decl in (False, True):
            x = m[ok & (yr >= y0) & ~(dep & decl)]
            b = np.array([aki(x, f) for f in show])
            lab = f"{y0} on, {'declustered' if decl else 'full'}"
            B[lab] = b
            r = float(np.ptp(b[np.isin(show, fl)]))
            add(1, lab, f"b range over floors {fl[0]}–{fl[-1]}", r, f"<= {K['b_range']}", r <= K["b_range"])
    P = K["periods"]
    keep = ok & ~dep
    rate = {}
    for q in K["rate_m"]:
        n = np.array([(keep & (yr >= a) & (yr < b) & (m >= q - 1e-9)).sum() for a, b in P])
        r = n / np.array([min(b, yr.max()) - a for a, b in P])
        rate[q] = (r, n)
        d = float(np.abs(r / r.mean() - 1).max())
        tol = K["rate_tol"] if q == 5.5 else None
        add(2, "declustered", f"M >= {q} rate, largest departure from the mean", d, tol, d <= tol if tol else None)
    big = {}
    x = m[ok & (yr >= P[0][0])]
    for lo in K["fit_lo"]:
        b, n = trunc_b(x, lo, K["fit_hi"])
        p7 = n * 10 ** (-b * (7.0 - lo)) / (1 - 10 ** (-b * (K["fit_hi"] - lo)))
        for q, pred, obs in (("N >= 7", p7, int((x >= 7 - 1e-9).sum())),
                             ("N 6.5–7", p7 * (10 ** (0.5 * b) - 1), int(((x >= 6.5 - 1e-9) & (x < 7 - 1e-9)).sum()))):
            a, z = band(obs)
            big[(lo, q)] = (obs, pred, a, z)
            add(3, f"full, fit {lo}–{K['fit_hi']} from {P[0][0]}, b {b:.2f}", f"{q}: observed {obs}, predicted",
                pred, f"{a:.1f} to {z:.1f}", bool(a <= pred <= z))
    hb = np.round(np.arange(K["hist"][0], K["hist"][1] + 1e-9, 0.1), 1)
    H = {}
    for a, b in P:
        n = np.array([((np.abs(m - q) < 1e-6) & ok & (yr >= a) & (yr < b)).sum() for q in hb])
        H[f"{a}–{'today' if b > 2090 else b - 1}"] = n
        g = np.sqrt(n[:-2] * n[2:])
        zz = (n[1:-1] - g) / np.sqrt(1.5 * np.maximum(g, 1))
        kk = hb[1:-1] >= K["hist_from"] - 1e-9
        v = float(np.abs(zz[kk]).max())
        add(5, f"{a}–{b - 1}", f"largest |z| of a bin against its neighbours (at {hb[1:-1][kk][np.argmax(np.abs(zz[kk]))]:.1f})",
            v, f"<= {K['hist_z']}", v <= K["hist_z"])
    return pd.DataFrame(rows), show, B, rate, big, hb, H


def regional(M, F, e):
    """
    D-MAG-12 test 4: each scale's native value converted with its relation, minus the regional Mw of the same event
    (GUC Mwr, CSN web Mw, NEIC Mwr, first found), per 0.25 bin of the regional Mw. In-sample: these pairs also enter
    the fits (psha_chile8 held them out by time block).
    """
    W = M[M.scale.isin(K["regional"])].pivot(index="event_id", columns="scale", values="mag")
    reg = pd.Series(G.first([(c, W[c].to_numpy()) for c in K["regional"] if c in W])[0], index=W.index)
    a = e.set_index("event_id")
    bins = K["reg_bins"]
    rows = []
    for sc in K["scales"]:
        p = M[(M.scale == sc) & M.event_id.isin(reg.index)].join(a[["z", "yr"]], on="event_id")
        conv = G.convert(F[sc], p.mag.to_numpy(float), p.z.to_numpy(float), p.yr.to_numpy(float))[0]
        y = p.event_id.map(reg).to_numpy(float)
        for lo, hi in zip(bins[:-1], bins[1:]):
            k = (y >= lo) & (y < hi) & np.isfinite(conv)
            med = float(np.median((conv - y)[k])) if k.sum() >= K["reg_n"] else np.nan
            use = lo >= K["reg_from"] - 1e-9 and np.isfinite(med)
            rows.append({"test": 4, "subset": sc, "quantity": f"median converted − regional, {lo}–{hi} (n {int(k.sum())})",
                         "value": med, "limit": f"|.| <= {K['reg_tol']}" if use else None,
                         "passed": bool(abs(med) <= K["reg_tol"]) if use else None, "lo": lo})
    return pd.DataFrame(rows)


# figures
def save(fig, f):
    fig.savefig(f, dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_relations(run, M, R, F, e):
    """Reference Mw against the native magnitude with the relation per depth group (as psha_chile8: native on x);
    dashed, the all-depth relation of events without a depth. Below, converted − reference Mw against the reference
    Mw, median per 0.2 bin. Surface-wave relations only to sw_z (the deeper part is never used)."""
    sc = [s for s in K["scales"] if s in F]
    fig, ax = plt.subplots(2, len(sc), figsize=(1.75 * len(sc), 3.8))
    P = M[M.scale.isin(sc)].join(R[R.fit][["y"]], on="event_id", how="inner").join(e.set_index("event_id")[["z", "yr"]], on="event_id")
    yy = np.linspace(3.8, 8.0, 50)
    bb = np.arange(4.0, 7.6, 0.2)
    for i, s in enumerate(sc):
        p, f = P[P.scale == s], F[s]
        sw = bool(__import__("re").match(G.C["sw"], s))
        g = G.groups(f["split"], p.z.to_numpy(float), p.yr.to_numpy(float))
        conv = G.convert(f, p.mag.to_numpy(float), p.z.to_numpy(float), p.yr.to_numpy(float))[0]
        for q, part in f["parts"].items():
            if sw and q in ("deep", "below 150 km"):
                continue
            col = GROUP.get(q, GROUP["all"])
            ax[0, i].plot(G.pl(part["p"], yy), yy, color=col, lw=1.4, ls="--" if q == "no depth" else "-", zorder=3)
            if q == "no depth":
                continue
            k = (g == q) & np.isfinite(p.z.to_numpy(float))
            y = p.y.to_numpy()[k]
            ax[0, i].scatter(p.mag[k], y, s=1.5, color=col, alpha=0.25, lw=0)
            r = conv[k] - y
            md = [np.median(r[(y >= a) & (y < a + 0.2)]) if ((y >= a) & (y < a + 0.2)).sum() >= 10 else np.nan for a in bb]
            ax[1, i].scatter(y, r, s=1.5, color=col, alpha=0.2, lw=0)
            ax[1, i].plot(bb + 0.1, md, color=col, lw=1.4)
        ax[0, i].plot(yy, yy, color="k", lw=0.5, ls=":")
        ax[0, i].text(0.04, 0.94, NAME.get(s, s), transform=ax[0, i].transAxes, va="top")
        ax[0, i].set(xlim=(3.0, 8.0), ylim=(3.8, 8.0), xlabel="native magnitude")
        ax[1, i].axhline(0, color="k", lw=0.6)
        ax[1, i].set(ylim=(-1, 1), xlim=(3.8, 8.0), xlabel="reference Mw")
    ax[0, 0].set_ylabel("reference Mw")
    ax[1, 0].set_ylabel("converted − reference Mw")
    h = [plt.Line2D([], [], color=v, lw=1.4, ls="--" if k == "no depth" else "-", label=k) for k, v in GROUP.items()]
    fig.legend(handles=h, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.05))
    fig.tight_layout()
    save(fig, run / "figs" / "mw_relations.png")


def fig_acceptance(run, show, B, rate, big, hb, H, reg):
    fig, ax = plt.subplots(1, 4, figsize=(9.5, 2.3))
    for k, b in B.items():
        ax[0].plot(show, b, marker="o", ms=2, lw=1, label=k)
    ax[0].axvspan(*K["floors"], color="w", alpha=0.6, zorder=0)
    ax[0].set(xlabel="fit floor Mw", ylabel="b (Aki)")
    ax[0].legend(frameon=False, fontsize=5)
    P = K["periods"]
    x = np.arange(len(P))
    for j, (q, (r, n)) in enumerate(rate.items()):
        ax[1].bar(x + 0.38 * j - 0.19, r / r.mean(), 0.36, label=f"M ≥ {q}")
    ax[1].axhspan(1 - K["rate_tol"], 1 + K["rate_tol"], color="w", alpha=0.7, zorder=0)
    ax[1].set_xticks(x, [f"{a}–{'' if b > 2090 else b - 1}" for a, b in P], fontsize=5)
    ax[1].set(ylabel="declustered rate / mean")
    ax[1].legend(frameon=False, fontsize=5)
    for j, ((lo, q), (obs, pred, a, z)) in enumerate(big.items()):
        ax[2].errorbar(j, obs, yerr=[[obs - a], [z - obs]], fmt="o", color="k", ms=3, lw=0.8)
        ax[2].plot(j, pred, "D", color="#c0141c", ms=4)
    ax[2].set_xticks(range(len(big)), [f"{q}\nfit from {lo}" for lo, q in big], fontsize=5)
    ax[2].set(ylabel="count from 1976")
    for k, n in H.items():
        ax[3].plot(hb, n, marker="o", ms=2, lw=0.8, label=k)
    ax[3].set_yscale("log")
    ax[3].set(xlabel="Mw (0.1 bins)", ylabel="events")
    ax[3].legend(frameon=False, fontsize=5)
    save(fig, run / "figs" / "mw_acceptance.png")
    fig, a = plt.subplots(figsize=(3.4, 2.3))
    for sc, g in reg.groupby("subset"):
        a.plot(g.lo + 0.125, g.value, marker="o", ms=3, lw=1, label=NAME.get(sc, sc))
    a.axhspan(-K["reg_tol"], K["reg_tol"], color="w", alpha=0.7, zorder=0)
    a.set(xlabel="regional Mw", ylabel="median converted − regional Mw")
    a.legend(frameon=False, fontsize=5, ncol=2)
    save(fig, run / "figs" / "mw_converted_vs_regional.png")


def fig_csn(run, out, W):
    """The CSN regional Mw values left out (D-MAG-06) against the median of the event's other moment magnitudes."""
    fig, ax = plt.subplots(figsize=(3.2, 3.0))
    for d, col, lab in ((False, "#999999", "kept (fewer than 2 others)"), (True, "#c0141c", "left out")):
        x = out[out.dropped == d]
        ax.scatter(x.others, x.mag, s=10, color=col, edgecolor="w", lw=0.3, label=f"{lab} ({len(x)})")
    v = np.array([3.5, 8])
    ax.plot(v, v, "k", lw=0.6)
    ax.fill_between(v, v - 0.3, v + 0.3, color="w", alpha=0.7, zorder=0)
    ax.set(xlabel="median of the other moment magnitudes", ylabel="CSN regional Mw", xlim=v, ylim=v)
    ax.legend(frameon=False, fontsize=5, loc="upper left")
    save(fig, run / "figs" / "mw_csn_outliers.png")


def basemap(ax, ext, px=1600):
    with rasterio.open(ROOT / K["basemap"]) as r:
        w = from_bounds(ext[0], ext[2], ext[1], ext[3], r.transform).intersection(rasterio.windows.Window(0, 0, r.width, r.height))
        n = max(1, int(w.height / px))
        a = r.read([1, 2, 3, 4], window=w, out_shape=(4, int(w.height / n), int(w.width / n)), resampling=Resampling.average)
        b = rasterio.windows.bounds(w, r.transform)
    ax.imshow(np.moveaxis(a, 0, -1), extent=[b[0], b[2], b[1], b[3]], transform=PC, origin="upper", zorder=0)


def fig_map(run, c):
    """Events of Mw >= 4.5 by Mw, north and south panels; M >= 7 in red."""
    c = c[c.mw >= 4.45].sort_values("mw")
    fig = plt.figure(figsize=(6.9, 6.4))
    for i, ext in enumerate([(-76.5, -63, -36, -15.5), (-76.5, -63, -56.5, -36)]):
        ax = fig.add_axes([0.04 + 0.49 * i, 0.08, 0.45, 0.9], projection=MERC)
        ax.set_extent(ext, crs=PC)
        basemap(ax, ext)
        g = ax.gridlines(draw_labels=True, lw=0.2, color="w", alpha=0.6)
        g.top_labels = g.right_labels = False
        col = np.where(c.mw >= 7, "#c0141c", np.where(c.mw >= 6, "#e8a33d", "#4682b4"))
        ax.scatter(c.lon, c.lat, s=2 * 3.5 ** (c.mw - 4.5), c=col, alpha=0.55, lw=0.15, edgecolor="#333", transform=PC, zorder=3)
    h = [plt.scatter([], [], s=2 * 3.5 ** (m - 4.5), color=k, label=l, alpha=0.6)
         for m, k, l in ((5, "#4682b4", "Mw 4.5–6"), (6.5, "#e8a33d", "6–7"), (7.5, "#c0141c", "≥ 7"))]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False)
    save(fig, run / "figs" / "map_mw.png")


# comparison with 17g
def compare(run, c):
    """Counts by period and Mw band in the 17g domain, and the events of Mw >= 7 whose Mw, location or depth
    changed against 17g."""
    o = pd.read_csv(ROOT / CFG["compare"], low_memory=False)
    o = o[o.in_domain]
    n = c[c.in_domain_17g & c.nonquake.eq("")]
    per, bd = K["compare_periods"], K["bands"]
    cut = lambda d: pd.crosstab(pd.cut(year(tsec(d.time)), per, right=False, labels=[f"{a}–{b - 1}" for a, b in zip(per, per[1:])]),
                                pd.cut(d.mw, bd, right=False, labels=[f"{a}–{b}" for a, b in zip(bd, bd[1:])]))
    t = pd.concat({"17g": cut(o), run.name: cut(n)}, axis=1)
    j = o.merge(n, on="event_id", how="outer", suffixes=("_17g", ""), indicator=True)
    big = j[(j.mw_17g >= 6.95) | (j.mw >= 6.95)].copy()
    big["dmw"] = (big.mw - big.mw_17g).round(2)
    big["dkm"] = (111.2 * np.hypot(big.lat - big.lat_17g, (big.lon - big.lon_17g) * np.cos(np.radians(big.lat)))).round(1)
    big["dz"] = (big.depth - big.depth_17g).round(1)
    asg = big.depth_src_17g.eq("assigned") & big.depth.isna()
    ch = big[(big.dmw.abs() > 0.01) | (big.dkm > 0.5) | (big.dz.abs() > 0.5) | (big._merge != "both")
             | ((big.depth.isna() != big.depth_17g.isna()) & ~asg)]
    cols = ["event_id", "_merge", "time", "lat", "lon", "depth", "depth_17g", "dz", "dkm", "mw_17g", "mw", "dmw", "mw_kind_17g",
            "mw_kind", "mw_type", "mw_flags"]
    ch = ch[cols].sort_values("event_id")
    t.to_csv(run / "compare_17g_counts.csv")
    ch.to_csv(run / "compare_17g_m7_changed.csv", index=False)
    fig, ax = plt.subplots(1, len(bd) - 1, figsize=(9, 2.0))
    for i, b in enumerate(t["17g"].columns):
        x = np.arange(len(t))
        ax[i].bar(x - 0.2, t[("17g", b)], 0.4, color="#999999", label="17g")
        ax[i].bar(x + 0.2, t[(run.name, b)], 0.4, color="#4682b4", label=run.name)
        ax[i].set_xticks(x, t.index, rotation=90, fontsize=5)
        ax[i].text(0.04, 0.94, f"Mw {b}", transform=ax[i].transAxes, va="top")
    ax[0].legend(frameon=False, fontsize=5, loc="center left")
    save(fig, run / "figs" / "compare_17g_counts.png")
    return t, ch


def fig_m7(out, ch, name):
    """Events of Mw >= 7 that changed against 17g: old against new Mw (left), and epicentre shift against depth
    change (right), marked by what changed. No classes before classification."""
    ch = ch[ch._merge == "both"].copy()
    yr = ch.time.str[:4].astype(int)
    why = np.where((ch.dmw.abs() > 0.01) & ch.mw_type.eq("mB"), "Mw: Abe mB rule",
                   np.where(ch.dmw.abs() > 0.01, "Mw: other source", np.where(ch.dkm > 0.5, "epicentre", "depth only")))
    col = {"Mw: Abe mB rule": "#c0141c", "Mw: other source": "#e8a33d", "epicentre": "#2a78b5", "depth only": "#7a7a7a"}
    fig, ax = plt.subplots(1, 2, figsize=(6.9, 3.0))
    # values on the 0.1 grid: spread within ±0.03 for display only, fixed per event
    j = np.array([(zlib.crc32(i.encode()) / 2 ** 32 - 0.5) * 0.06 for i in ch.event_id])
    k2 = np.array([(zlib.crc32((i + "y").encode()) / 2 ** 32 - 0.5) * 0.06 for i in ch.event_id])
    for k, c in col.items():
        m = why == k
        ax[0].scatter(ch.mw_17g[m] + j[m], ch.mw[m] + k2[m], s=16, color=c, edgecolor="w", lw=0.4,
                      label=f"{k} ({m.sum()})", zorder=3)
        ax[1].scatter(ch.dkm[m], ch.dz.fillna(0)[m], s=18, color=c, edgecolor="w", lw=0.4, zorder=3)
    v = np.array([6.3, 8.0])
    ax[0].plot(v, v, "k", lw=0.6)
    ax[0].axhline(7.0, color="#999999", lw=0.6, ls=":")
    ax[0].set(xlim=v, ylim=v, xlabel="Mw, 17g", ylabel=f"Mw, {name}")
    ax[0].legend(frameon=False, fontsize=5.5, loc="upper left")
    for x, y, t in zip(ch.dkm, ch.dz.fillna(0), yr):
        if x > 0.5 or abs(y) > 15:
            ax[1].annotate(str(t), (x, y), fontsize=5, xytext=(3, 2), textcoords="offset points")
    ax[1].axhline(0, color="k", lw=0.6)
    ax[1].set(xlabel="epicentre shift (km)", ylabel="depth change (km; 0 where one is unknown)")
    fig.tight_layout()
    save(fig, out)


def main(run):
    run = ROOT / run
    (run / "figs").mkdir(exist_ok=True)
    c = pd.read_csv(run / "catalog.csv", low_memory=False)
    c["nonquake"] = c.nonquake.fillna("")
    c["t"] = tsec(c.time)
    c["yr"] = year(c.t)
    M = pd.read_csv(run / "magnitudes.csv", dtype=str).assign(mag=lambda d: d.mag.astype(float))
    F = json.load(open(run / "relations.json"))
    e = pd.DataFrame({"event_id": c.event_id, "z": c.depth, "yr": c.yr})
    R, _, W = G.reference(M)
    fig_relations(run, M, R, F, e)
    q = c[c.in_domain_17g & c.nonquake.eq("")]
    T, show, B, rate, big, hb, H = acceptance(q)
    reg = regional(M, F, e)
    T = pd.concat([T, reg[reg.limit.notna()].drop(columns="lo")], ignore_index=True)
    T.to_csv(run / "acceptance.csv", index=False)
    fig_acceptance(run, show, B, rate, big, hb, H, reg)
    fig_csn(run, pd.read_csv(run / "mw_reference_outliers.csv"), W)
    fig_map(run, q)
    t, ch = compare(run, c)
    fig_m7(run / "figs" / "compare_17g_m7_changed.png", ch, run.name)
    print(T[T.passed.notna()].groupby("test").passed.agg(["sum", "size"]))
    print(t.to_string())
    print("Mw >= 7 changed against 17g:", len(ch))


if __name__ == "__main__":
    main(sys.argv[1])
