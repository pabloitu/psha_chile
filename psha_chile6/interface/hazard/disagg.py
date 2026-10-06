# Disaggregation of the full model at the cities: what magnitude, distance and
# epsilon produce the 475 and 2475 yr PGA.
# Reads the CSVs exported by the disaggregation job (hazard/run_all.sh runs it
# with --exports csv when build.json has "disagg").
# Outputs: outputs/hazard/_disagg/
#   disagg_<site>_<rp>.png   M-R bars coloured by epsilon, with the M and R margins
#   disagg_trt_<rp>.png      contribution by tectonic region, all cities
#   disagg_eps.png           epsilon distribution per city and rp, by TRT, truncation marked
#   disagg_summary.csv       mean M, R, epsilon and TRT shares per site and rp
#   disagg_trt_summary.csv   share, mean M, R and epsilon per site, rp and TRT

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hazard import config as hc

# settings
JOB = "disagg"
IMT = "PGA"
OUT = hc.OUT_ROOT / "_disagg"
EPS_SITES = ("santiago_centro", "iquique", "concepcion")
TRT_SHORT = {"Subduction Interface": "interface", "Subduction IntraSlab": "in-slab", "Active Shallow Crust": "crustal"}
TRT_COLORS = {"Subduction Interface": "#4c72b0", "Subduction IntraSlab": "#c44e52",
              "Active Shallow Crust": "#55a868"}


DIMS = ("imt", "iml", "poe", "mag", "dist", "eps", "trt", "lon", "lat", "site", "return_period")


def read(kind):
    """
    Concatenate the per-site CSVs of one disaggregation output.

    The site comes from the comment header (lon, lat); the contribution column is
    "mean" for a stats export and "rlz*" otherwise, and is renamed to "w".
    """
    import re

    hd = hc.OUT_ROOT / JOB
    fs = sorted(hd.rglob(f"{kind}-*.csv"))
    if not fs:
        raise SystemExit(f"no {kind} csv under {hd}; rerun the disagg job with --exports csv")
    out = []
    for f in fs:
        txt = f.read_text().split("\n")
        n = next(i for i, l in enumerate(txt) if not l.startswith("#"))
        head = " ".join(txt[:n])
        d = pd.read_csv(f, skiprows=n)
        for k in ("lon", "lat"):
            m = re.search(rf"(?<![a-z_]){k}=(-?[\d.]+)", head)
            d[k] = float(m.group(1)) if m else np.nan
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    val = [c for c in d.columns if c not in DIMS]
    if not val:
        raise SystemExit(f"{kind}: no contribution column in {fs[0].name}")
    d = d.rename(columns={val[0]: "w"})
    if len(val) > 1:
        print(f"[warn] {kind}: using column {val[0]} of {val}")
    sites = {(round(x, 2), round(y, 2)): n for n, (x, y) in hc.CITIES.items()}
    d["site"] = [sites.get((round(x, 2), round(y, 2)), f"{x:.2f},{y:.2f}") for x, y in zip(d["lon"], d["lat"])]
    d["return_period"] = [round(-hc.INV_TIME / np.log(1 - p)) for p in d["poe"]]
    if "trt" in d:
        d["trt"] = d["trt"].astype(str).str.strip()
    return d[d["imt"] == IMT]


def fig_mre(d, site, rp, path):
    """M-R bars stacked by epsilon, the traditional disaggregation plot."""
    g = d[(d["site"] == site) & (d["return_period"] == rp)]
    if not len(g) or g["w"].sum() <= 0:
        return
    iml = g["iml"].iloc[0]
    g = g.assign(pct=100 * g["w"] / g["w"].sum())
    eps = np.sort(g["eps"].unique())
    cmap = plt.get_cmap("RdYlBu_r", len(eps))
    f, axs = plt.subplots(2, 2, figsize=(10, 7), gridspec_kw={"height_ratios": [1, 2.2],
                                                             "width_ratios": [2.4, 1]})
    ax = axs[1][0]
    dm = np.diff(np.sort(g["mag"].unique()))
    w = (dm.min() if len(dm) else 0.25) * 0.9
    bot = {}
    for i, e in enumerate(eps):
        h = g[g["eps"] == e].groupby("mag")["pct"].sum()
        b = np.array([bot.get(m, 0.0) for m in h.index])
        ax.bar(h.index, h.to_numpy(), w, bottom=b, color=cmap(i / max(len(eps) - 1, 1)),
               edgecolor="none", label=f"{e:+.1f}")
        bot.update({m: v for m, v in zip(h.index, b + h.to_numpy())})
    ax.set_xlabel("magnitude")
    ax.set_ylabel("contribution (%)")
    ax.legend(title="epsilon", fontsize=7, title_fontsize=7, ncol=2)
    ax.grid(alpha=0.3)

    ar = axs[1][1]
    hr = g.groupby("dist")["pct"].sum()
    dd = np.diff(np.sort(g["dist"].unique()))
    ar.barh(hr.index, hr.to_numpy(), (dd.min() if len(dd) else 20) * 0.9, color="0.5")
    ar.set_xlabel("contribution (%)")
    ar.set_ylabel("rupture distance (km)")
    ar.grid(alpha=0.3)

    am = axs[0][0]
    p = g.pivot_table(index="dist", columns="mag", values="pct", aggfunc="sum").fillna(0)
    im = am.imshow(p.to_numpy(), origin="lower", aspect="auto", cmap="Reds",
                   extent=[p.columns.min() - w / 2, p.columns.max() + w / 2, p.index.min(), p.index.max()])
    am.set_ylabel("distance (km)")
    f.colorbar(im, ax=am, label="%")
    axs[0][1].axis("off")
    mw = float((g["mag"] * g["pct"]).sum() / 100)
    rw = float((g["dist"] * g["pct"]).sum() / 100)
    ew = float((g["eps"] * g["pct"]).sum() / 100)
    axs[0][1].text(0, 0.5, f"mean M {mw:.2f}\nmean R {rw:.0f} km\nmean eps {ew:+.2f}", fontsize=10, va="center")
    f.suptitle(f"{site.replace('_', ' ')}: disaggregation of {IMT} = {iml:.2f} g, {rp} yr", fontsize=11)
    f.tight_layout()
    f.savefig(path, dpi=220)
    plt.close(f)


def fig_trt(t, rp, path):
    sites = [s for s in hc.CITIES if s in set(t["site"])]
    g = t[t["return_period"] == rp]
    f, axs = plt.subplots(1, 2, figsize=(13, 0.45 * len(sites) + 2.4), sharey=True)
    y = np.arange(len(sites))
    sh = g.groupby(["site", "trt"])["w"].sum().unstack(fill_value=0.0).reindex(sites)
    sh = 100 * sh.div(sh.sum(axis=1), axis=0)
    left = np.zeros(len(sites))
    for trt in sh.columns:
        axs[0].barh(y, sh[trt], 0.7, left=left, color=TRT_COLORS.get(trt, "0.6"), label=trt)
        left += sh[trt].to_numpy()
    axs[0].set_xlim(0, 100)
    axs[0].set_xlabel("contribution (%)")
    axs[0].set_title(f"by tectonic region, {rp} yr", fontsize=10)
    axs[0].legend(fontsize=7, loc="lower right")
    for trt, sub in g.groupby("trt"):
        m = sub.groupby(["site", "mag"])["w"].sum().reset_index()
        mw = m.groupby("site").apply(lambda x: (x["mag"] * x["w"]).sum() / x["w"].sum(),
                                     include_groups=False).reindex(sites)
        r = sub.groupby(["site", "dist"])["w"].sum().reset_index()
        rw = r.groupby("site").apply(lambda x: (x["dist"] * x["w"]).sum() / x["w"].sum(),
                                     include_groups=False).reindex(sites)
        axs[1].scatter(rw, y, s=18 + 2 * (mw - 5) ** 2, color=TRT_COLORS.get(trt, "0.6"), label=trt)
        for yy, a, b in zip(y, rw, mw):
            if np.isfinite(a):
                axs[1].text(a, yy + 0.22, f"M{b:.1f}", fontsize=6, ha="center")
    axs[1].set_xlabel("mean rupture distance (km)")
    axs[1].set_title("mean distance and magnitude per region", fontsize=10)
    axs[1].grid(alpha=0.3)
    axs[0].set_yticks(y)
    axs[0].set_yticklabels([s.replace("_", " ") for s in sites])
    axs[0].invert_yaxis()
    f.tight_layout()
    f.savefig(path, dpi=220)
    plt.close(f)


def fig_eps(d, path, te=None, sites=EPS_SITES, trunc=3.0):
    """Epsilon distribution of the hazard per city and return period, stacked by TRT when te is given."""
    rps = sorted(d["return_period"].unique())
    sites = [x for x in sites if x in set(d["site"])]
    f, axs = plt.subplots(1, len(sites), figsize=(3.6 * len(sites), 3.6), sharey=True, squeeze=False)
    for ax, site in zip(axs[0], sites):
        for j, rp in enumerate(rps):
            g = d[(d["site"] == site) & (d["return_period"] == rp)]
            e = g.groupby("eps")["w"].sum()
            tot = e.sum()
            de = np.diff(e.index).min()
            x = e.index + (j - 0.5) * de * 0.42
            if te is None:
                ax.bar(x, 100 * e.to_numpy() / tot, de * 0.4, color=("0.55", "#c44e52")[j], label=f"{rp} yr")
                continue
            h = te[(te["site"] == site) & (te["return_period"] == rp)]
            h = h.groupby(["trt", "eps"])["w"].sum().unstack(0).reindex(e.index).fillna(0.0)
            h = 100 * h / h.to_numpy().sum()
            bot = np.zeros(len(h))
            for trt in [t for t in TRT_COLORS if t in h]:
                ax.bar(x, h[trt], de * 0.4, bottom=bot, color=TRT_COLORS[trt], alpha=(0.55, 1.0)[j],
                       edgecolor="white", lw=0.3, label=f"{TRT_SHORT[trt]} {rp} yr" if site == sites[0] else None)
                bot += h[trt].to_numpy()
        ax.axvline(trunc, color="k", lw=1, ls="--")
        ax.set_xlabel("epsilon")
        ax.set_title(site.replace("_", " "), fontsize=9)
        ax.grid(axis="y", alpha=0.3)
    axs[0][0].set_ylabel("contribution %")
    axs[0][0].legend(fontsize=6 if te is not None else 8, loc="upper left")
    lab = "left bar 475 yr, right bar 2475 yr" if te is not None else ""
    f.suptitle(f"{IMT} disaggregation by epsilon; dashed = truncation {trunc:g}; {lab}".rstrip("; "), fontsize=10)
    f.tight_layout()
    f.savefig(path, dpi=300)
    plt.close(f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = read("Mag_Dist_Eps")
    t = read("TRT_Mag_Dist")
    try:
        te = read("TRT_Mag_Dist_Eps")
    except SystemExit:
        te = None
        print("[skip] no TRT_Mag_Dist_Eps export: epsilon not split by TRT")
    rows, trows = [], []
    for rp in sorted(d["return_period"].unique()):
        for site in [s for s in hc.CITIES if s in set(d["site"])]:
            g = d[(d["site"] == site) & (d["return_period"] == rp)]
            w = g["w"].to_numpy()
            if w.sum() <= 0:
                continue
            fig_mre(d, site, rp, OUT / f"disagg_{site}_{rp}.png")
            r = {"site": site, "return_period": rp, "iml": g["iml"].iloc[0],
                 "mean_M": (g["mag"] * w).sum() / w.sum(), "mean_R": (g["dist"] * w).sum() / w.sum(),
                 "mean_eps": (g["eps"] * w).sum() / w.sum()}
            gt = t[(t["site"] == site) & (t["return_period"] == rp)]
            s = gt.groupby("trt")["w"].sum()
            rows.append({**r, **{k: 100 * v / s.sum() for k, v in s.items()}})
            for trt, x in gt.groupby("trt"):
                w = x["w"].to_numpy()
                if w.sum() > 0:
                    r2 = {"site": site, "return_period": rp, "trt": trt, "share": 100 * w.sum() / s.sum(),
                          "mean_M": (x["mag"] * w).sum() / w.sum(), "mean_R": (x["dist"] * w).sum() / w.sum()}
                    if te is not None:
                        y = te[(te["site"] == site) & (te["return_period"] == rp) & (te["trt"] == trt)]
                        if y["w"].sum() > 0:
                            r2["mean_eps"] = (y["eps"] * y["w"]).sum() / y["w"].sum()
                    trows.append(r2)
        fig_trt(t, rp, OUT / f"disagg_trt_{rp}.png")
    fig_eps(d, OUT / "disagg_eps.png", te)
    tab = pd.DataFrame(rows)
    tab.to_csv(OUT / "disagg_summary.csv", index=False)
    pd.DataFrame(trows).to_csv(OUT / "disagg_trt_summary.csv", index=False)
    print(tab.round(2).to_string(index=False))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()