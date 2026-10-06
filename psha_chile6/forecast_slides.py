# Presentation figures of the forecast (completeness, rates, b, Mmax, patterns),
# redrawn for slides from what fit_check.py, pattern_test.py and check_rates.py
# wrote. 16:9, dpi 300, fixed names in outputs/forecast_slides/; one caption per
# figure in FORECAST_final.md. The maps need the declustered catalogs of s00.
#   python fit_check.py; python forecast_slides.py

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import fit_check as fc
import paths
import run
from hazard import config as hc
from lib import cat, gr, smooth
from variants import VARIANTS

# settings
FITS = paths.ROOT / "outputs" / "fits"
OUT = paths.ROOT / "outputs" / "forecast_slides"
CHECK = paths.ROOT / "outputs" / "intraslab" / "ref" / "check"
W, H, DPI = 13.33, 7.5, 300
MODELS = ["interface", "intraslab", "crustal"]
SKIP = {"unclassified"}
N_BOOT = 500
LABEL = {"seg0_full": "Full margin", "seg1_south": "Segment 45.6-37 S", "seg2": "Segment 37-32 S",
         "seg3": "Segment 32-26 S", "seg4_north": "Segment 26-17.6 S", "intra_slab": "In-slab, slab top < 50 km",
         "slab_deep": "In-slab, slab top >= 50 km", "deep_nest": "Jujuy deep nest", "forearc": "Forearc",
         "intraarc": "Intra-arc", "backarc": "Back-arc", "patagonia_crustal": "Patagonia", "unclassified": "Unclassified"}
FAMILY = {"interface": "Interface", "intraslab": "In-slab", "crustal": "Crustal background"}
MODE = {"all": "equal weights (reference)", "complete": "magnitude-step weights (campaign)",
        "window": "completeness window", "window_T": "completeness window / length (Hiemer 2014)",
        "period": "since 1990 only"}
VARIANT = {"ref": "equal weights (reference)", "smooth_complete": "magnitude-step weights (campaign)",
           "smooth_window_T": "completeness window / length"}
C_MAIN, C_ALT, C_FLOOR, C_OBS = "#c44e52", "0.45", "#2ca02c", "k"
plt.rcParams.update({"font.size": 13, "axes.titlesize": 15, "axes.labelsize": 14, "legend.fontsize": 11,
                     "xtick.labelsize": 12, "ytick.labelsize": 12, "figure.titlesize": 17})


# data

def load(model):
    c = run.config(model, VARIANTS[model][fc.REF[model]])
    te = c.T_END or float(cat.load(paths.CATALOG)["year"].max())
    sub = fc.subsets(model, c)
    d = FITS / model
    tj = d / "tables.json"
    tabs = {k: [tuple(r) for r in v] for k, v in json.loads(tj.read_text()).items()} if tj.exists() else {}
    for k, s in sub.items():
        s["floor"] = fc.FLOOR_REF.get(k, s["floor"])
        tabs.setdefault(k, fc.cfg_table(model, c, s["tab"]))
    fits = pd.read_csv(d / "fits.csv")
    win = pd.read_csv(d / "mc_windows.csv")
    bt = pd.read_csv(d / "btest.csv") if (d / "btest.csv").stat().st_size > 1 else pd.DataFrame()
    ks = [k for k in sub if k not in SKIP and (fits["sub"] == k).any()]
    return c, te, sub, tabs, fits, win, bt, ks


def ref_row(fits, k, fl, form="tgr"):
    r = fits[(fits["sub"] == k) & np.isclose(fits["floor"], fl) & (fits["form"] == form)]
    return r.iloc[0] if len(r) else None


def panels(n, title):
    nc = min(n, 3)
    nr = int(np.ceil(n / nc))
    f, ax = plt.subplots(nr, nc, figsize=(W, H), squeeze=False)
    for a in ax.ravel()[n:]:
        a.axis("off")
    f.suptitle(title)
    return f, ax.ravel()[:n]


def save(f, name):
    f.tight_layout()
    f.savefig(OUT / name, dpi=DPI)
    plt.close(f)
    print(f"wrote {name}")


def steps_line(a, table, t0, t1, **kw):
    tt = np.linspace(t0, t1, 600)
    a.step(tt, [fc.mc_at(table, t) for t in tt], where="post", **kw)


# figures

def fig_mt(model, d):
    c, te, sub, tabs, fits, win, bt, ks = d
    ks = [k for k in ks if sub[k]["tab"] == k]
    f, ax = panels(len(ks), f"{FAMILY[model]}: magnitude-time and completeness")
    t0 = 1850 if model == "interface" else 1900
    for a, k in zip(ax, ks):
        df = sub[k]["df"]
        m = df["year"] >= t0
        a.scatter(df.loc[m, "year"], df.loc[m, "mag"], s=2, c="0.55", lw=0)
        steps_line(a, tabs[k], t0, te, c="#1f77b4", lw=2.2, label="completeness")
        a.axhline(sub[k]["floor"], c=C_FLOOR, lw=1.2, ls=":", label=f"fit floor M{sub[k]['floor']}")
        a.set(title=LABEL[k], xlabel="year", ylabel="Mw", xlim=(t0, te + 1), ylim=(max(df["mag"].min(), 4.0), df["mag"].max() + 0.3))
    ax[0].legend(loc="upper left")
    save(f, f"fc01_mt_{model}.png")


def fig_mct(model, d):
    c, te, sub, tabs, fits, win, bt, ks = d
    ks = [k for k in ks if sub[k]["tab"] == k]
    f, ax = panels(len(ks), f"{FAMILY[model]}: magnitude of completeness per time window")
    for a, k in zip(ax, ks):
        w = win[(win["sub"] == k) & (win["y1"] > 1900)]
        x = (w["y0"] + w["y1"]) / 2
        e = (w["y1"] - w["y0"]) / 2
        ok = (w["how"] == "ks") & ~w.get("outlier", pd.Series(False, index=w.index)).astype(bool)
        a.errorbar(x[ok], w.loc[ok, "mc"], xerr=e[ok], fmt="o", c="k", ms=6, lw=1, label="KS test (b = 1)")
        a.plot(x, w["mc_maxc"], "v", c="#9467bd", ms=7, label="max. curvature + 0.2")
        steps_line(a, tabs[k], 1900, te, c="#1f77b4", lw=2.2, label="adopted table")
        a.set(title=LABEL[k], xlabel="year", ylabel="Mc", xlim=(1900, te + 1), ylim=(3.8, 7.8))
    ax[0].legend(loc="upper right")
    save(f, f"fc02_mct_{model}.png")


def fig_fmd(model, d):
    c, te, sub, tabs, fits, win, bt, ks = d
    forms = ["tgr", "tapered"] if model == "interface" else ["tgr"]
    f, ax = panels(len(ks), f"{FAMILY[model]}: frequency-magnitude distributions and fits")
    for a, k in zip(ax, ks):
        s, t = sub[k], tabs[k]
        g = np.round(np.arange(np.floor(min(t)[0] * 10) / 10, s["df"]["mag"].max() + 0.05, 0.1), 2)
        o, lo, hi, _ = fc.obs(s["df"], t, te, g)
        ok = o > 0
        a.errorbar(g[ok], o[ok], yerr=[o[ok] - lo[ok], hi[ok] - o[ok]], fmt="o", c=C_OBS, ms=3.5, lw=0.8,
                   label="observed, 90 % Poisson")
        mm = np.linspace(s["floor"], s["mmax"], 200)
        txt = []
        for form, ls in zip(forms, ("-", "--")):
            r = ref_row(fits, k, s["floor"], form)
            if r is not None:
                a.plot(mm, fc.model_n(form, r["b"], r["rate"], s["floor"], s["mmax"], mm), c=C_MAIN, ls=ls, lw=2,
                       label="truncated GR" if form == "tgr" else f"tapered GR, corner {fc.CORNER}")
                if form == "tgr":
                    txt.append(f"b = {r['b']:.2f} ± {r['b_err']:.2f}  (n = {int(r['n'])})")
        mo = s["df"]["mag"].max()
        a.axvline(s["floor"], c=C_FLOOR, ls=":", lw=1.2)
        a.axvline(mo, c="0.3", ls="--", lw=1)
        txt.append(f"floor {s['floor']}, max obs {mo:.1f}, Mmax {s['mmax']:.1f}")
        a.text(0.97, 0.97, "\n".join(txt), transform=a.transAxes, ha="right", va="top", fontsize=11)
        a.set(yscale="log", title=LABEL[k], xlabel="Mw", ylabel="N(≥M) per year",
              ylim=(lo[ok & (lo > 0)].min() / 5 if (ok & (lo > 0)).any() else None, None))
    ax[0].legend(loc="lower left")
    save(f, f"fc03_fmd_{model}.png")


def fig_bfloor(model, d):
    c, te, sub, tabs, fits, win, bt, ks = d
    f, a = plt.subplots(figsize=(W, H))
    cols = plt.cm.tab10(np.arange(len(ks)))
    for k, cc in zip(ks, cols):
        r = fits[(fits["sub"] == k) & (fits["form"] == "tgr")].sort_values("floor")
        a.plot(r["floor"], r["b"], "o-", c=cc, ms=4, lw=1.8, label=LABEL[k])
        a.fill_between(r["floor"], r["b"] - r["b_err"], r["b"] + r["b_err"], color=cc, alpha=0.12)
        x = ref_row(fits, k, sub[k]["floor"])
        if x is not None:
            a.plot(sub[k]["floor"], x["b"], "*", c=cc, ms=18, mec="k")
    a.set(xlabel="fit floor (Mw)", ylabel="b (Weichert, ± 1 sigma)", ylim=(0.4, 1.9),
          title=f"{FAMILY[model]}: b against fit floor (star: adopted floor)")
    a.legend(ncol=2)
    save(f, f"fc04_bfloor_{model}.png")


def fig_fitobs(model, d):
    c, te, sub, tabs, fits, win, bt, ks = d
    top = fc.CHECK_M[model][-2:]
    f, ax = panels(len(ks), f"{FAMILY[model]}: fitted / observed N(≥M) against fit floor")
    for a, k in zip(ax, ks):
        r = fits[(fits["sub"] == k) & (fits["form"] == "tgr")].sort_values("floor")
        for g, cc in zip(top, ("#1f77b4", C_MAIN)):
            if f"fo_{g}" not in r or r[f"fo_{g}"].isna().all():
                continue
            n = int(r[f"nobs_{g}"].iloc[0])
            a.plot(r["floor"], r[f"fo_{g}"], "o-", c=cc, ms=3.5, lw=1.8, label=f"M{g} ({n} obs.)")
            o, lo, hi, _ = fc.obs(sub[k]["df"], tabs[k], te, [g])
            if o[0] > 0:
                a.axhspan(lo[0] / o[0], hi[0] / o[0], color=cc, alpha=0.1)
        a.axhline(1, c="k", lw=0.8)
        a.axvline(sub[k]["floor"], c=C_FLOOR, ls=":", lw=1.2)
        a.set(yscale="log", title=LABEL[k], xlabel="fit floor", ylabel="fitted / observed", ylim=(0.1, 10))
        a.legend(loc="upper left", fontsize=10)
    save(f, f"fc05_fitobs_{model}.png")


def boot(s, table, te, dm, form, mc):
    m = s["df"].loc[gr.complete(s["df"], table), "mag"].to_numpy()
    m = m[m >= s["floor"] - 1e-6]
    bs, ns = [], []
    rng = np.random.default_rng(1)
    for _ in range(N_BOOT):
        w = gr.weichert(rng.choice(m, len(m)), table, te, s["floor"], dm)
        if np.isfinite(w["b"]):
            bs.append(w["b"])
            ns.append(float(fc.model_n(form, w["b"], w["rate"], s["floor"], s["mmax"], [mc])[0]))
    return np.array(bs), np.array(ns)


def fig_spread(model, d):
    c, te, sub, tabs, fits, win, bt, ks = d
    form = "tapered" if model == "interface" else "tgr"
    f, ax = panels(len(ks), f"{FAMILY[model]}: bootstrap (a, b) and the rate at the controlling magnitude")
    for a, k in zip(ax, ks):
        s = sub[k]
        mc = min(fc.CTRL[model], round(s["mmax"] - 0.3, 1))
        b, n = boot(s, tabs[k], te, c.DM, form, mc)
        if not len(b):
            continue
        a.scatter(b, n, s=6, c="0.6", lw=0)
        for p, cc in ((5, "#1f77b4"), (16, "#9467bd"), (50, "k"), (84, "#9467bd"), (95, "#1f77b4")):
            q = np.percentile(n, p)
            i = np.argmin(abs(n - q))
            a.plot(b[i], n[i], "o", c=cc, ms=9, mec="k", label=f"{p}th" if k == ks[0] else None)
        r = np.percentile(n, 84) / np.percentile(n, 16)
        a.set(yscale="log", title=LABEL[k], xlabel="b", ylabel=f"N(≥M{mc}) per year")
        a.text(0.97, 0.97, f"p84 / p16 = {r:.2f}", transform=a.transAxes, ha="right", va="top", fontsize=11)
    ax[0].legend(loc="lower left", fontsize=10)
    save(f, f"fc06_abspread_{model}.png")


def fig_btest(d):
    c, te, sub, tabs, fits, win, bt, ks = d
    f, (a, b) = plt.subplots(1, 2, figsize=(W, H), gridspec_kw={"width_ratios": [2, 1]})
    for k, cc in (("intra_slab", "#1f77b4"), ("slab_deep", C_MAIN)):
        r = fits[(fits["sub"] == k) & (fits["form"] == "tgr")].sort_values("floor")
        a.plot(r["floor"], r["b"], "o-", c=cc, lw=1.8, ms=4, label=LABEL[k])
        a.fill_between(r["floor"], r["b"] - r["b_err"], r["b"] + r["b_err"], color=cc, alpha=0.15)
    if len(bt):
        t = bt[bt["group"] == "intra_slab+slab_deep"]
        a.plot(t["floor"], t["b_pooled"], "D", c="k", ms=9, label="pooled b")
        b.bar(t["floor"].astype(str), t["p"], color="0.6")
        b.axhline(0.05, c=C_MAIN, ls="--", label="p = 0.05")
        b.set(ylim=(0, 1), xlabel="common fit floor", ylabel="p (likelihood ratio, one b vs two)")
        b.legend()
    a.set(xlabel="fit floor", ylabel="b (Weichert, ± 1 sigma)", ylim=(0.4, 1.9), xlim=(5.0, 6.6))
    a.legend()
    f.suptitle("In-slab: one b for both classes is not rejected")
    save(f, "fc09_btest_inslab.png")


def fig_pattern_test():
    p = CHECK / "pattern_test.csv"
    if not p.exists():
        print(f"[skip] {p} missing: run intraslab/pattern_test.py")
        return
    t = pd.read_csv(p)
    if "targets" not in t:
        t["targets"] = "all"
    tg = list(dict.fromkeys(t["targets"]))
    ks = list(dict.fromkeys(t["class"]))
    f, ax = plt.subplots(len(ks), len(tg), figsize=(W, H), squeeze=False, sharey="row")
    for i, k in enumerate(ks):
        for j, g in enumerate(tg):
            a = ax[i, j]
            for m, x in t[(t["class"] == k) & (t["targets"] == g)].groupby("mode", sort=False):
                a.plot(x["split"], x["gain_per_event"], "o-", lw=2.4 if m == "all" else 1.4,
                       c=C_MAIN if m == "all" else None, label=MODE.get(m, m))
            a.set(title=f"{LABEL.get(k, k)}\ntargets: {g}", xlabel="split year", ylabel="gain per event" if j == 0 else "")
    ax[0, 0].legend(fontsize=9)
    f.suptitle("In-slab pattern: retrospective spatial test, gain over a uniform forecast (higher is better)")
    save(f, "fc07_pattern_test.png")


def fig_maps(model):
    c = run.config(model, VARIANTS[model][fc.REF[model]])
    dc = c.OUT / "decluster"
    ks = [k for k in c.CLASSES if (dc / f"cat_dc_{k}_{c.DC_METHOD}.csv").exists()
          and (dc / f"cat_dc_{k}_{c.PATTERN_DC}.csv").exists()]
    if not ks:
        print(f"[skip] maps {model}: no declustered catalogs in {dc}; run run.py for {model}")
        return
    te = json.loads((dc / "input.json").read_text())["t_end"]
    if model == "intraslab":
        from intraslab.s02_ssm import domain, fit, pattern
    else:
        from crustal.s02_ssm import domain, fit
    g = domain(c)
    glon, glat = g["lon"].to_numpy(), g["lat"].to_numpy()
    f, ax = plt.subplots(1, len(ks), figsize=(W, H), squeeze=False)
    for a, k in zip(ax[0], ks):
        s = cat.load(dc / f"cat_dc_{k}_{c.DC_METHOD}.csv", bbox=c.BBOX)
        pc = cat.load(dc / f"cat_dc_{k}_{c.PATTERN_DC}.csv", bbox=c.BBOX)
        w = fit(k, s, c, te)
        if model == "intraslab":
            ev, wt = pattern(k, pc, w, w["b"], c, te)
        else:
            ev = pc[gr.complete(pc, c.COMPLETENESS[k])]
            wt = np.ones(len(ev))
        kp = {"N_NEIGHBORS": c.N_NEIGHBORS, "MIN_KERNEL_KM": c.MIN_KERNEL_KM, "KERNEL_POWER": c.KERNEL_POWER,
              "MAX_DIST_KM": c.MAX_DIST_KM, "KERNEL": getattr(c, "KERNEL", "power"), **c.KERNEL_BY_CLASS.get(k, {})}
        el, ea = ev["longitude"].to_numpy(), ev["latitude"].to_numpy()
        h = smooth.kernel(el, ea, kp["N_NEIGHBORS"], kp["MIN_KERNEL_KM"])
        z = smooth.field(el, ea, wt, h, glon, glat, kp["KERNEL_POWER"], kp["MAX_DIST_KM"], kp["KERNEL"])
        z = z / z.sum()
        v = np.log10(np.maximum(z, z[z > 0].max() * 1e-4))
        im = a.scatter(glon, glat, c=v, s=3, marker="s", cmap="magma_r", lw=0)
        a.scatter(el, ea, s=1.5, c="#1f77b4", lw=0, alpha=0.5)
        for x, y in hc.CITIES.values():
            a.plot(x, y, "^", c="k", ms=5)
        a.set(title=LABEL.get(k, k), xlabel="lon", ylabel="lat" if a is ax[0, 0] else "", aspect="equal",
              xlim=(glon.min(), glon.max()), ylim=(glat.min(), glat.max()))
        f.colorbar(im, ax=a, shrink=0.7, label="log10 share of the class rate")
    f.suptitle(f"{FAMILY[model]}: smoothed spatial pattern (declustered catalog, equal weights)")
    save(f, f"fc08_maps_{model}.png")


def fig_concepcion():
    p = CHECK / "rates_compare.csv"
    if not p.exists():
        print(f"[skip] {p} missing: run check_rates.compare(['ref', 'smooth_complete', 'smooth_window_T'])")
        return
    t = pd.read_csv(p)
    t = t[t["M"] == 5.5]
    vs = [v for v in VARIANT if v in set(t["variant"])]
    sites = [s for s in hc.CITIES if s in set(t["site"])]
    f, a = plt.subplots(figsize=(W, H))
    x = np.arange(len(sites))
    wd = 0.8 / max(len(vs), 1)
    for i, v in enumerate(vs):
        r = t[t["variant"] == v].set_index("site").reindex(sites)
        a.bar(x + (i - (len(vs) - 1) / 2) * wd, r["ratio"], wd, label=VARIANT[v],
              color=C_MAIN if v == "ref" else plt.cm.Greys(0.4 + 0.25 * i))
    a.axhline(1, c="k", lw=0.8)
    a.set_xticks(x, [s.replace("_", " ").title() for s in sites], rotation=30, ha="right")
    a.set(yscale="log", ylabel="model / catalog, N(≥5.5) within 150 km",
          title="In-slab rate near each city: pattern weights (Concepcion 2.5-3.3 with the campaign weights)")
    a.legend()
    save(f, "fc10_concepcion.png")


# main

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        if not (FITS / model / "fits.csv").exists():
            print(f"[skip] {model}: run fit_check.py first")
            continue
        d = load(model)
        for fn in (fig_mt, fig_mct, fig_fmd, fig_bfloor, fig_fitobs, fig_spread):
            fn(model, d)
        if model == "intraslab":
            fig_btest(d)
    fig_pattern_test()
    for model in ("intraslab", "crustal"):
        fig_maps(model)
    fig_concepcion()


if __name__ == "__main__":
    main()
