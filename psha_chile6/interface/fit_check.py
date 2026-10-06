# Fit diagnostics of the catalog-based sources, before any hazard run.
# Reads catalog.csv directly (full catalog, as the rates use) with each model's
# config (family, BBOX, HIST_CUTOFF, SEG_BOUNDS, completeness tables, Mmax).
# Per subset: completeness recomputed with the method of the approved tables
# (lib.mc: KS test with b fixed, per window, outliers dropped, reverse running
# maximum; the s02_mc / s01_mc steps), masking of short-term aftershock
# incompleteness, Weichert fits over a wide range of fit floors, fitted vs
# observed N(>=M) with Poisson intervals, spread of the rate at the controlling
# magnitude from bootstrap (a, b) pairs, b-equality tests, b-positive, and a
# rate with borrowed b where sigma_b is too large.
# Outputs in outputs/fits/: csv tables, one figure per subset, one summary
# figure per model, and rates.csv (the fitted N(>=M) per subset).
#
# python fit_check.py [interface|intraslab|crustal ...]

import json
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize_scalar

import paths
import run
from lib import cat, gr, mc
from lib.dc import hav
from variants import VARIANTS

# settings
MODELS = ["interface", "intraslab", "crustal"]
REF = {"interface": "mmin55", "intraslab": "ref", "crustal": "ref"}
TABLE = "ks"                 # completeness for the fits: "ks" (recomputed, method of the config tables) or "config"
# subsets whose windows are too sparse for KS before the modern network keep the config table
TABLE_BY_SUB = {"intraarc": "config", "patagonia_crustal": "config"}
MASK_M = 7.5                 # triggers of short-term aftershock incompleteness
MASK_FROM = 1960
FLOORS = {"interface": (5.0, 7.2), "intraslab": (4.6, 7.0), "crustal": (4.4, 6.6)}
# reference fit floor per subset; missing ones take MMIN_FIT(_BY_CLASS) of the config
FLOOR_REF = {"seg0_full": 5.8, "seg1_south": 5.8, "seg2": 6.0, "seg3": 5.8, "seg4_north": 5.8,
             "intra_slab": 5.7, "slab_deep": 6.0, "deep_nest": 5.6,
             "forearc": 5.5, "intraarc": 4.6, "backarc": 5.5, "patagonia_crustal": 4.5}
HIST_END = 1900              # windows ending by then keep the config (hand-set historical) Mc
B_ERR_MAX = 0.2
CHECK_M = {"interface": [6.0, 7.0, 7.5, 8.0], "intraslab": [6.0, 6.5, 7.0, 7.5],
           "crustal": [5.5, 6.0, 6.5, 7.0]}
CTRL = {"interface": 8.8, "intraslab": 7.3, "crustal": 6.5}
CORNER = 9.6
N_BOOT = 300
FALLBACK = {"intraarc": "forearc", "backarc": "forearc", "patagonia_crustal": "forearc", "unclassified": "forearc"}
TESTS = {"intraslab": [["intra_slab", "slab_deep"]],
         "crustal": [["forearc", "intraarc"], ["forearc", "intraarc", "backarc", "patagonia_crustal"]]}
BPOS_D = 0.2
OUT = paths.ROOT / "outputs" / "fits"
RNG = np.random.default_rng(42)


# subsets

def subsets(model, c):
    """
    Subsets fitted per model with their events and fit settings.

    Returns
    -------
    dict
        name -> dict(df, floor, mmax, table key); the interface segments share
        the full-margin table, crustal classes are read natively (no CLASS_MAP).
    """
    fam = cat.family(c.CAT, c.FAMILY, None if model == "crustal" else c.CLASS_MAP)
    out = {}
    if model == "interface":
        b = c.SEG_BOUNDS
        fam = fam[fam["latitude"].between(b[0], b[-1])].reset_index(drop=True)
        out[c.FULL_ID] = {"df": fam, "floor": c.MMIN_FIT, "mmax": max(c.MMAX.values()), "tab": c.FULL_ID}
        for i, s in enumerate(c.SEG_IDS):
            d = fam[(fam["latitude"] >= b[i]) & (fam["latitude"] < b[i + 1])].reset_index(drop=True)
            out[s] = {"df": d, "floor": c.MMIN_FIT, "mmax": c.MMAX[s], "tab": c.FULL_ID}
        return out
    lo, hi, la, ha = c.BBOX
    fam = fam[fam["longitude"].between(lo, hi) & fam["latitude"].between(la, ha)]
    fam = cat.exclude(fam, getattr(c, "EXCLUDE", {}))
    big = fam[(fam["mag"] >= 7.0) & fam["class"].isin(["intraarc", "patagonia_crustal"])]
    if len(big):
        print("intraarc and patagonia_crustal events M >= 7 kept:\n"
              + big[["class", "time_iso", "mag", "latitude", "longitude", "depth"]].to_string(index=False))
    ks = list(c.CLASSES) if model == "intraslab" else [k for k in paths.FAMILIES["crustal"] if k in set(fam["class"])]
    for k in ks:
        d = fam[fam["class"] == k]
        cut = c.HIST_CUTOFF_BY_CLASS.get(k, c.HIST_CUTOFF)
        if cut:
            d = d[d["year"] >= cut]
        mo = getattr(c, "MMAX_OVERRIDE", {}).get(k)
        out[k] = {"df": d.reset_index(drop=True), "floor": c.MMIN_FIT_BY_CLASS.get(k, c.MMIN_FIT),
                  "mmax": mo if mo else round(d["mag"].max() + c.MMAX_PAD, 2), "tab": k}
    return out


def cfg_table(model, c, k):
    t = c.COMPLETENESS if model == "interface" else c.COMPLETENESS.get(k) or c.COMPLETENESS.get(FALLBACK.get(k))
    return sorted(t) if t else []


def mc_at(table, t):
    """Mc of a (Mc, since) table at time t: the lowest Mc complete since t or earlier."""
    v = [m for m, y in table if y <= t]
    return min(v) if v else np.inf


# completeness

def windows(model, c, df, te):
    if model == "interface":
        return [(y0, y1 if y1 else int(np.ceil(te))) for y0, y1 in c.MC_WINDOWS]
    k = df["class"].iloc[0]
    y0 = c.HIST_CUTOFF_BY_CLASS.get(k, c.HIST_CUTOFF) or df["year"].min()
    return mc.regular(y0, te, c.WINDOW_YEARS_BY_CLASS.get(k, c.WINDOW_YEARS))


def ks_table(model, c, df, te, cfg):
    """
    Completeness recomputed on this catalog with the method of the config tables.

    KS test per window with b fixed (MC_B_FIXED, seismostats), sparse windows get
    MC_HIST_FLOOR, low outliers dropped (MC_OUTLIER_DROP), steps from the reverse
    running maximum (lib.mc). Config rows older than the first step (hand-set
    historical steps) are kept.

    Returns
    -------
    table : list of (Mc, since)
    win : DataFrame, one row per window with Mc (KS), MAXC+0.2 and the config Mc
    """
    wins = windows(model, c, df, te)
    old = [x for x in wins if x[1] <= HIST_END]
    w = mc.table(df, [x for x in wins if x[1] > HIST_END], c)
    if old:
        h = pd.DataFrame([{"y0": y0, "y1": y1, "n": int(df["year"].between(y0, y1, "left").sum()),
                           "mc": mc_at(cfg, y0), "how": "config"} for y0, y1 in old])
        w = pd.concat([h, w], ignore_index=True)
    w = mc.outliers(w, c.MC_OUTLIER_DROP)
    t = mc.propose(w[np.isfinite(w["mc"])]) if (w["how"] == "ks").any() else []
    mx = []
    for r in w.itertuples():
        m = df.loc[(df["year"] >= r.y0) & (df["year"] < r.y1), "mag"].to_numpy()
        if len(m) >= 10:
            v, cnt = np.unique(np.round(np.round(m / c.DM) * c.DM, 6), return_counts=True)
            mx.append(round(v[np.argmax(cnt)] + 0.2, 2))
        else:
            mx.append(np.nan)
    w = w.assign(mc_maxc=mx, mc_config=[mc_at(cfg, y) for y in w["y0"]])
    return sorted(t), w


def mbs(sc, span=0.5):
    """Lowest floor whose b agrees within its sigma with the mean b of the next
    span magnitude units (b-stability, Cao and Gao 2002)."""
    r = sc.drop_duplicates("floor").sort_values("floor")
    for x in r.itertuples():
        nxt = r[(r["floor"] > x.floor + 1e-6) & (r["floor"] <= x.floor + span + 1e-6)]
        if len(nxt) >= 3 and abs(x.b - nxt["b"].mean()) <= x.b_err:
            return x.floor
    return np.nan


def mask(df, trig, table):
    """Events inside the short-term incompleteness of an M >= MASK_M trigger:
    Mc(t) = M - 4.5 - 0.75 log10(t days) (Helmstetter et al. 2006) above the
    table's Mc, within a subsurface rupture length (Wells and Coppersmith 1994)."""
    out = np.zeros(len(df), bool)
    for tr in trig.itertuples():
        mc = mc_at(table, tr.year)
        if not np.isfinite(mc):
            continue
        tday = 10 ** ((tr.mag - 4.5 - mc) / 0.75)
        dt = (df["year"].to_numpy() - tr.year) * 365.25
        near = hav(df["longitude"].to_numpy(), df["latitude"].to_numpy(), tr.longitude, tr.latitude) \
            <= 10 ** (-2.57 + 0.62 * tr.mag)
        out |= (dt > 0) & (dt <= tday) & near
    return out


# fits

def obs(df, table, te, grid):
    """Observed N(>=M) per year from complete events and a 90 % Poisson interval."""
    df = df[gr.complete(df, table)]
    m = df["mag"].to_numpy()
    w = 1.0 / (te - gr.since(m, table))
    r, lo, hi, n = [], [], [], []
    for g in grid:
        k = m >= g - 1e-6
        x, q = w[k].sum(), int(k.sum())
        tg = te - float(gr.since(np.array([g]), table)[0])
        r.append(x)
        n.append(q)
        lo.append(x * stats.chi2.ppf(0.05, 2 * q) / 2 / q if q else 0.0)
        hi.append(x * stats.chi2.ppf(0.95, 2 * q + 2) / 2 / q if q else 3.0 / tg)
    return np.array(r), np.array(lo), np.array(hi), np.array(n)


def tap(b, mmin, mmax, m, corner=CORNER):
    """N(>=m) per unit rate at mmin, tapered GR with its own corner, cut at mmax."""
    be = 2.0 * b / 3.0
    f = lambda x: (gr.m0(mmin) / gr.m0(x)) ** be * np.exp((gr.m0(mmin) - gr.m0(x)) / gr.m0(corner))
    n = (f(np.asarray(m, float)) - f(mmax)) / (1.0 - f(mmax))
    return np.where(np.asarray(m) > mmax, 0.0, np.clip(n, 0, None))


def model_n(form, b, rate, mmin, mmax, m):
    if form == "tapered":
        return rate * tap(b, mmin, mmax, m)
    return rate * gr.cum("tgr", b, mmin, mmax, m)


def floor_scan(df, table, te, dm, mmax, model, forms):
    rows = []
    chk = CHECK_M[model]
    o, lo, hi, n = obs(df, table, te, chk)
    lo_f, hi_f = FLOORS[model]
    mc = df.loc[gr.complete(df, table), "mag"].to_numpy()
    for fl in np.round(np.arange(lo_f, hi_f + 1e-6, 0.1), 2):
        try:
            w = gr.weichert(mc, table, te, fl, dm, nboot=100)
        except ValueError:
            continue
        if not np.isfinite(w["b"]):
            continue
        for f in forms:
            r = {"floor": fl, "form": f, "b": w["b"], "b_err": w["b_err"], "n": w["n"], "rate": w["rate"]}
            for g, x, a, z, q in zip(chk, o, lo, hi, n):
                v = float(model_n(f, w["b"], w["rate"], fl, mmax, [g])[0])
                r[f"fo_{g}"] = v / x if x > 0 else np.nan
                r[f"in_{g}"] = bool(a <= v <= z)
                r[f"nobs_{g}"] = q
            rows.append(r)
    return pd.DataFrame(rows)


def spread(df, table, te, dm, floor, mmax, mc_ctrl, form):
    """Rate at the controlling magnitude from bootstrap Weichert fits (the (a, b) cloud)."""
    m = df.loc[gr.complete(df, table), "mag"].to_numpy()
    m = m[m >= floor - 1e-6]
    v = []
    for _ in range(N_BOOT):
        w = gr.weichert(RNG.choice(m, len(m)), table, te, floor, dm)
        if np.isfinite(w["b"]):
            v.append(float(model_n(form, w["b"], w["rate"], floor, mmax, [mc_ctrl])[0]))
    q = np.percentile(v, [16, 50, 84]) if v else [np.nan] * 3
    return {"m_ctrl": mc_ctrl, "p16": q[0], "p50": q[1], "p84": q[2], "ratio_84_16": q[2] / q[0] if q[0] else np.nan}


def ll_bins(m, table, te, floor, dm, beta):
    m = m[m >= floor - 1e-6]
    nb = int(np.floor((m.max() - floor) / dm + 1e-6)) + 1
    lo = floor + dm * np.arange(nb)
    t = te - gr.since(lo, table)
    n = np.bincount(np.floor((m - floor) / dm + 1e-6).astype(int), minlength=nb)
    lw = np.log(t) - beta * (lo + dm / 2)
    return float((n * (lw - np.log(np.exp(lw).sum()))).sum())


def btest(groups, sub, tabs, te, dm):
    """Likelihood-ratio test of one b against one b per subset (Weichert likelihood)."""
    rows = []
    for g in groups:
        g = [k for k in g if k in sub]
        if len(g) < 2:
            continue
        fl0 = max(sub[k]["floor"] for k in g)
        for fl in (fl0 - 0.2, fl0, fl0 + 0.2):
            ms = [sub[k]["df"]["mag"].to_numpy() for k in g]
            ms = [x[gr.complete(sub[k]["df"], tabs[k])] for x, k in zip(ms, g)]
            try:
                f = [lambda be, x=x, k=k: -ll_bins(x, tabs[k], te, fl, dm, be) for x, k in zip(ms, g)]
                sep = [minimize_scalar(fi, bounds=(0.5, 5), method="bounded") for fi in f]
                pool = minimize_scalar(lambda be: sum(fi(be) for fi in f), bounds=(0.5, 5), method="bounded")
            except (ValueError, ZeroDivisionError):
                continue
            lr = 2 * (pool.fun - sum(s.fun for s in sep))
            if not np.isfinite(lr):
                continue
            rows.append({"group": "+".join(g), "floor": round(fl, 2),
                         "b_each": " / ".join(f"{s.x / gr.LN10:.3f}" for s in sep),
                         "b_pooled": pool.x / gr.LN10, "lr": lr, "p": stats.chi2.sf(lr, len(g) - 1)})
    return pd.DataFrame(rows)


def bpos(df, dm, d=BPOS_D):
    """b-positive (van der Elst 2021) from positive magnitude differences of
    consecutive events, all magnitudes, no completeness needed."""
    m = df.sort_values("year")["mag"].to_numpy()
    x = np.diff(m)
    x = x[x >= d - 1e-6]
    return 1.0 / (gr.LN10 * (x.mean() - (d - dm / 2))) if len(x) > 20 else np.nan


# figures

def fig_subset(name, s, table, cfg, win, sc, te, model, forms, path):
    df, fl, mx, al, mk = s["df"], s["floor"], s["mmax"], s["all"], s["mk"]
    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    a = ax[0, 0]
    y0 = 1500 if model == "interface" else 1900
    k = (al["year"] >= y0).to_numpy()
    a.scatter(al.loc[k, "year"], al.loc[k, "mag"], s=3, c="0.6", lw=0)
    if mk.any():
        a.scatter(al.loc[mk, "year"], al.loc[mk, "mag"], s=8, c="#d62728", marker="x", lw=0.6,
                  label=f"masked ({mk.sum()})")
    tt = np.linspace(y0, te, 800)
    a.step(tt, [mc_at(table, t) for t in tt], c="#1f77b4", lw=1.8, label=f"table used ({TABLE})")
    a.step(tt, [mc_at(cfg, t) for t in tt], c="#ff7f0e", lw=1.2, ls="--", label="config table")
    for how, cc, lab in (("ks", "k", "Mc per window (KS)"), ("floor", "0.6", "sparse window (floor)"),
                         ("config", "#ff7f0e", "historical (config)")):
        ok = (win["how"] == how) & ~win.get("outlier", False) & np.isfinite(win["mc"])
        if ok.any():
            a.errorbar((win.loc[ok, "y0"] + win.loc[ok, "y1"]) / 2, win.loc[ok, "mc"],
                       xerr=(win.loc[ok, "y1"] - win.loc[ok, "y0"]) / 2, fmt="o", c=cc, ms=4, lw=0.8, label=lab)
    ok = win["mc_maxc"].notna()
    a.plot((win.loc[ok, "y0"] + win.loc[ok, "y1"]) / 2, win.loc[ok, "mc_maxc"], "v", c="#9467bd", ms=4,
           label="MAXC+0.2")
    a.axhline(fl, c="#2ca02c", lw=0.8, ls=":", label=f"fit floor {fl}")
    a.set(xlabel="year", ylabel="M", title=f"{name}: magnitude-time and completeness",
          ylim=(max(df["mag"].min(), 3.5), df["mag"].max() + 0.2))
    a.legend(fontsize=7, loc="upper left")

    a = ax[0, 1]
    g = np.round(np.arange(np.floor(min(table)[0] * 10) / 10, df["mag"].max() + 0.05, 0.1), 2)
    o, lo, hi, n = obs(df, table, te, g)
    ok = o > 0
    a.errorbar(g[ok], o[ok], yerr=[o[ok] - lo[ok], hi[ok] - o[ok]], fmt="o", c="k", ms=3, lw=0.7,
               label="observed, 90 % Poisson")
    mm = np.linspace(fl, mx, 200)
    ref = sc[np.isclose(sc["floor"], fl)]
    for f, ls in zip(forms, ("-", "--")):
        r = ref[ref["form"] == f]
        if len(r):
            r = r.iloc[0]
            a.plot(mm, model_n(f, r["b"], r["rate"], fl, mx, mm), c="#d62728", ls=ls, lw=1.6,
                   label=f"{f}, floor {fl}: b {r['b']:.2f}±{r['b_err']:.2f}")
    for d, cc in ((-0.2, "0.5"), (0.4, "0.3")):
        r = sc[(np.isclose(sc["floor"], round(fl + d, 2))) & (sc["form"] == forms[0])]
        if len(r):
            r = r.iloc[0]
            m2 = np.linspace(r["floor"], mx, 200)
            a.plot(m2, model_n(forms[0], r["b"], r["rate"], r["floor"], mx, m2), c=cc, lw=0.8,
                   label=f"floor {r['floor']}: b {r['b']:.2f}")
    a.axvline(fl, c="#2ca02c", lw=0.8, ls=":")
    mo = df["mag"].max()
    a.axvline(mo, c="0.3", lw=1.0, ls="--", label=f"M max obs {mo:.1f}")
    a.legend(fontsize=7)
    a.set(yscale="log", xlabel="M", ylabel="N(>=M) per year", title="frequency-magnitude",
          ylim=(lo[ok & (lo > 0)].min() / 5 if (ok & (lo > 0)).any() else None, None))
    a.legend(fontsize=7)

    a = ax[1, 0]
    r = sc[sc["form"] == forms[0]]
    a.plot(r["floor"], r["b"], "o-", c="#1f77b4", ms=3)
    a.fill_between(r["floor"], r["b"] - r["b_err"], r["b"] + r["b_err"], color="#1f77b4", alpha=0.2)
    a.axvline(fl, c="#2ca02c", lw=0.8, ls=":")
    a.set(xlabel="fit floor", ylabel="b (Weichert, ±1 sigma)", title="b stability")
    b2 = a.twinx()
    b2.bar(r["floor"], r["n"], width=0.07, color="0.8", alpha=0.6)
    b2.set_ylabel("n above floor", color="0.5")
    a.set_zorder(b2.get_zorder() + 1)
    a.patch.set_visible(False)

    a = ax[1, 1]
    cols = plt.cm.viridis(np.linspace(0, 0.85, len(CHECK_M[model])))
    for g, cc in zip(CHECK_M[model], cols):
        for f, ls in zip(forms, ("-", "--")):
            r = sc[sc["form"] == f]
            if f"fo_{g}" in r and r[f"fo_{g}"].notna().any():
                a.plot(r["floor"], r[f"fo_{g}"], ls=ls, c=cc, marker="o", ms=2,
                       label=f"M{g} {f} (n={int(r[f'nobs_{g}'].iloc[0])})")
        o1, lo1, hi1, _ = obs(df, table, te, [g])
        if o1[0] > 0:
            a.axhspan(lo1[0] / o1[0], hi1[0] / o1[0], color=cc, alpha=0.08)
    a.axhline(1, c="k", lw=0.8)
    a.axvline(fl, c="#2ca02c", lw=0.8, ls=":")
    a.set(yscale="log", xlabel="fit floor", ylabel="fitted / observed N(>=M)",
          title="fitted / observed (bands: 90 % Poisson)")
    a.legend(fontsize=6, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def fig_summary(model, sub, tabs, fits, te, forms, path):
    ks = list(sub)
    nc = min(3, len(ks))
    nr = int(np.ceil(len(ks) / nc))
    fig, ax = plt.subplots(nr, nc, figsize=(5 * nc, 3.8 * nr), squeeze=False)
    for a, k in zip(ax.ravel(), ks):
        s, t = sub[k], tabs[k]
        if not (fits["sub"] == k).any():
            a.set_title(f"{k}: no fit")
            continue
        g = np.round(np.arange(np.floor(min(t)[0] * 10) / 10, s["df"]["mag"].max() + 0.05, 0.1), 2)
        o, lo, hi, _ = obs(s["df"], t, te, g)
        ok = o > 0
        a.errorbar(g[ok], o[ok], yerr=[o[ok] - lo[ok], hi[ok] - o[ok]], fmt="o", c="k", ms=2.5, lw=0.6)
        mm = np.linspace(s["floor"], s["mmax"], 200)
        r = fits[(fits["sub"] == k) & np.isclose(fits["floor"], s["floor"])]
        txt = []
        for f, ls in zip(forms, ("-", "--")):
            x = r[r["form"] == f]
            if len(x):
                x = x.iloc[0]
                a.plot(mm, model_n(f, x["b"], x["rate"], s["floor"], s["mmax"], mm), c="#d62728", ls=ls)
                txt.append(f"{f}: b {x['b']:.2f}±{x['b_err']:.2f}, n {int(x['n'])}")
        a.axvline(s["floor"], c="#2ca02c", lw=0.8, ls=":")
        mo = s["df"]["mag"].max()
        a.axvline(mo, c="0.3", lw=1.0, ls="--")
        txt.append(f"M max obs {mo:.1f}, Mmax {s['mmax']:.1f}")
        a.set(yscale="log", title=k, xlabel="M", ylabel="N(>=M)/yr",
              ylim=(lo[ok & (lo > 0)].min() / 5 if (ok & (lo > 0)).any() else None, None))
        a.text(0.97, 0.97, "\n".join(txt), transform=a.transAxes, ha="right", va="top", fontsize=7)
    for a in ax.ravel()[len(ks):]:
        a.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


# main

def main(models):
    OUT.mkdir(parents=True, exist_ok=True)
    trig = cat.load(paths.CATALOG)
    trig = trig[(trig["mag"] >= MASK_M) & (trig["year"] >= MASK_FROM)]
    pd.set_option("display.width", 200)
    for model in models:
        c = run.config(model, VARIANTS[model][REF[model]])
        te = c.T_END or float(cat.load(paths.CATALOG)["year"].max())
        od = OUT / model
        od.mkdir(exist_ok=True)
        forms = ["tgr", "tapered"] if model == "interface" else ["tgr"]
        sub = subsets(model, c)
        wins, tabs, fits, spr, ext = [], {}, [], [], []
        for k, s in sub.items():
            cfg = cfg_table(model, c, k)
            if s["tab"] != k:
                tabs[k] = tabs[s["tab"]]
            else:
                t, w = ks_table(model, c, s["df"], te, cfg)
                wins.append(w.assign(sub=k))
                tabs[k] = t if TABLE_BY_SUB.get(k, TABLE) == "ks" and t else cfg
            mk = mask(s["df"], trig, tabs[k])
            s["all"], s["mk"] = s["df"], mk
            s["df"] = s["df"][~mk].reset_index(drop=True)
            s["floor"] = FLOOR_REF.get(k, s["floor"])
            mn = min(tabs[k])[0]
            if s["floor"] < mn - 1e-6:
                s["floor"] = round(np.ceil(mn * 10 - 1e-6) / 10, 2)
            sc = floor_scan(s["df"], tabs[k], te, c.DM, s["mmax"], model, forms).assign(sub=k)
            ext.append({"sub": k, "n_all": len(s["df"]) + int(mk.sum()), "masked": int(mk.sum()),
                        "floor": s["floor"], "mmax": s["mmax"], "b_pos": bpos(s["df"], c.DM),
                        "n_floor": int((s["df"].loc[gr.complete(s["df"], tabs[k]), "mag"] >= s["floor"] - 1e-6).sum()),
                        "mbs_floor": mbs(sc[sc["form"] == forms[0]]) if "floor" in sc else np.nan})
            if "floor" not in sc or not np.isclose(sc["floor"], s["floor"]).any():
                print(f"[no fit] {model}/{k}: fewer than 10 complete events above every floor tried")
                continue
            fits.append(sc)
            for f in forms:
                spr.append({"sub": k, "form": f, **spread(s["df"], tabs[k], te, c.DM, s["floor"], s["mmax"],
                                                           min(CTRL[model], round(s["mmax"] - 0.3, 1)), f)})
            fig_subset(k, s, tabs[k], cfg, wins[-1] if s["tab"] == k else next(x for x in wins if x["sub"].iloc[0] == s["tab"]),
                       sc, te, model, forms, od / f"{k}.png")
        if not fits:
            print(f"[no fit] {model}: no subset could be fitted")
            continue
        fits = pd.concat(fits, ignore_index=True)
        bor = []
        for k, s in sub.items():
            r = fits[(fits["sub"] == k) & np.isclose(fits["floor"], s["floor"]) & (fits["form"] == forms[0])]
            d = FALLBACK.get(k)
            if d not in sub or (len(r) and r["b_err"].iloc[0] <= B_ERR_MAX):
                continue
            rd = fits[(fits["sub"] == d) & np.isclose(fits["floor"], sub[d]["floor"]) & (fits["form"] == forms[0])]
            if not len(rd):
                continue
            m = s["df"].loc[gr.complete(s["df"], tabs[k]), "mag"].to_numpy()
            try:
                w = gr.weichert(m, tabs[k], te, s["floor"], c.DM, b=rd["b"].iloc[0])
            except ValueError:
                continue
            if w["n"]:
                bor.append({"sub": k, "form": "tgr_borrowed", "floor": s["floor"], "b": w["b"], "b_err": np.nan,
                            "n": w["n"], "rate": w["rate"], "from": d})
        if bor:
            fits = pd.concat([fits, pd.DataFrame(bor)], ignore_index=True)
        wins = pd.concat(wins, ignore_index=True)
        spr, ext = pd.DataFrame(spr), pd.DataFrame(ext)
        bt = btest(TESTS.get(model, []), sub, tabs, te, c.DM)
        g = np.round(np.arange(5.0, 9.51, 0.5), 1)
        rates = []
        for k, s in sub.items():
            r = fits[(fits["sub"] == k) & np.isclose(fits["floor"], s["floor"])]
            for x in r.itertuples():
                rates.append({"sub": k, "form": x.form, "floor": x.floor, "b": x.b, "rate_floor": x.rate,
                              **{f"N{m}": float(model_n(x.form, x.b, x.rate, x.floor, s["mmax"], [m])[0]) for m in g}})
        rates = pd.DataFrame(rates)
        for n, t in (("mc_windows", wins), ("fits", fits), ("spread", spr), ("subsets", ext), ("btest", bt),
                     ("rates", rates)):
            t.to_csv(od / f"{n}.csv", index=False)
        (od / "tables.json").write_text(json.dumps({k: [list(r) for r in sorted(t)] for k, t in tabs.items()}))
        fig_summary(model, sub, tabs, fits, te, forms, OUT / f"{model}_summary.png")

        print(f"\n######## {model}  (table {TABLE}, t_end {te:.2f})")
        print("\nMc per window: KS (b fixed, how = ks / floor, outliers flagged), MAXC+0.2 and the config table")
        print(wins[["sub", "y0", "y1", "n", "mc", "how", "outlier", "mc_maxc", "mc_config"]].round(2)
              .to_string(index=False))
        print(f"\ncompleteness tables recomputed (KS, as s02_mc / s01_mc); used: {TABLE}, "
              f"config for {[k for k in TABLE_BY_SUB if k in sub]}")
        for k in tabs:
            if sub[k]["tab"] == k:
                print(f"    {k!r}: {tabs[k]},")
        print("\nsubsets: events, masked by aftershock incompleteness, fit floor, Mmax, b-positive, "
              "b-stability floor (suggestion)")
        print(ext.round(3).to_string(index=False))
        cols = ["sub", "form", "floor", "b", "b_err", "n"] + [f"fo_{m}" for m in CHECK_M[model]] \
            + [f"in_{m}" for m in CHECK_M[model]]
        ref = pd.concat([fits[(fits["sub"] == k) & np.isclose(fits["floor"], s["floor"])] for k, s in sub.items()])
        cols += [f"nobs_{m}" for m in CHECK_M[model]]
        print("\nfits at the reference floor: fitted / observed N(>=M), in = inside the 90 % Poisson interval")
        print(ref[cols].round(3).to_string(index=False))
        print("\nfloor scan: fitted / observed at the largest check magnitudes")
        top = CHECK_M[model][-2:]
        t = fits[fits["form"] == "tgr"].assign(
            bs=lambda x: x["b"].map("{:.2f}".format) + "±" + x["b_err"].map("{:.2f}".format) + " (" + x["n"].astype(str) + ")")
        print("b ± sigma (n above floor) per floor")
        print(t.pivot(index="sub", columns="floor", values="bs").reindex(list(dict.fromkeys(t["sub"]))).fillna("")
              .to_string())
        print(fits.pivot_table(index=["sub", "form"], columns="floor", values=[f"fo_{m}" for m in top], sort=False)
              .round(2).to_string())
        print(f"\nrate at the controlling magnitude from bootstrap (a, b): branch if p84/p16 > ~1.3")
        print(spr.round(5).to_string(index=False))
        if bor:
            print(f"\nrate with borrowed b (sigma_b > {B_ERR_MAX} at the reference floor)")
            print(pd.DataFrame(bor).round(4).to_string(index=False))
        if len(bt):
            print("\nb-equality (likelihood ratio, one b vs one per subset); p < 0.05 = different")
            print(bt.round(3).to_string(index=False))
        print(f"\nwrote {od}/*.csv, *.png and {OUT / f'{model}_summary.png'}")


if __name__ == "__main__":
    main(sys.argv[1:] or MODELS)
