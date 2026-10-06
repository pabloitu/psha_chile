# Analyses of the final run (FINAL=1) from the family jobs c_if_final, c_is_final, c_cr_final and
# c_cr_final_nofaults: the families combine exactly in rate space, the fractiles by exact
# enumeration of the joint tree (hazard/combine.py). Outputs in outputs/hazard/rock800_final/_report/:
#   fr_summary.csv            city, IMT, PoE: mean, median, 5 / 95 %, family shares, faults effect
#   fr_curves_<city>_<imt>.png  hazard curves per regime with their 95 % envelopes and the full model
#   fr_curves_grid_<imt>.png  the fourteen cities on one page
#   fr_uhs_<city>.png         uniform hazard spectra, 475 and 2475 yr, mean and 5-95 %, per-regime UHS
#   fr_uhs_grid.png           the fourteen UHS on one page
#   fr_uhs_shape.png          UHS at 475 yr normalised by PGA: the spectral shape by controlling regime
#   fr_shares_period.png      family share of the 475-yr hazard against period, per city
#   fr_epistemic.png, .csv    95 % band of PGA 475 per city and the share of the epistemic variance
#                             (ln IML) carried by each family
#   fr_return_periods.csv     return period of PGA 0.2, 0.3, 0.4 and 0.6 g per city (mean curve)
#   fr_campaign.png, .csv     PGA 475 of the campaign (psha_chile5) against the final mean and band
# Run: FINAL=1 python hazard/final_report.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import paths
from hazard import config as hc
from hazard import combine, post
from hazard.post import draw, finish, iml, wquant

OUT = hc.OUT_ROOT / "_report"
FAM = [("c_if_final", "interface"), ("c_is_final", "in-slab"), ("c_cr_final", "crustal")]
NOFAULT = "c_cr_final_nofaults"
COL = paths.palette.FAMILY
POES = {"475 yr": 0.002105, "2475 yr": 0.000404}
PERIOD = {"PGA": 0.0, "SA(0.1)": 0.1, "SA(0.2)": 0.2, "SA(0.5)": 0.5, "SA(1.0)": 1.0, "SA(2.0)": 2.0}
LEVELS = (0.2, 0.3, 0.4, 0.6)
CURVE_IMTS = ("PGA", "SA(1.0)")
# PGA 475 yr of the sensitivity campaign (psha_chile5, findings_rock800.md), rock800
CAMPAIGN = {"iquique": 1.20, "antofagasta": 1.39, "copiapo": 1.07, "valparaiso": 1.51, "santiago_centro": 0.88,
            "santiago_penalolen": 0.81, "concepcion": 1.42, "pucon": 0.54, "puerto_montt": 0.63, "puerto_aysen": 0.48}


def rate(p):
    return -np.log(1 - np.clip(p, 0, 1 - 1e-12))


def imls(c, lv, p):
    """IML at PoE p of every curve in c (..., levels); NaN where the curve does not reach p."""
    flat = c.reshape(-1, c.shape[-1])
    return np.array([iml(x, lv, p) for x in flat]).reshape(c.shape[:-1])


def title(name):
    return name.replace("_", " ").title()


def load():
    fam = {lab: post.load(j) for j, lab in FAM}
    nof = post.load(NOFAULT) if (hc.OUT_ROOT / NOFAULT / "build.json").exists() else None
    imts = [k for k in fam["interface"]["imtls"] if k in PERIOD]
    return fam, nof, imts


def parts_of(fam, imt):
    return [(r["curves"][:, :, [list(r["imtls"]).index(imt)], :].astype(float), r["w"]) for r in fam.values()]


def family_mean(r, imt):
    m = list(r["imtls"]).index(imt)
    return np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :].astype(float))


def summary(fam, nof, imts, names):
    rows, uhs = [], {}
    for imt in imts:
        lv = fam["interface"]["imtls"][imt]
        parts = parts_of(fam, imt)
        mean = combine.mean(parts)[:, 0]
        q = combine.exact(parts, (0.05, 0.5, 0.95))[:, :, 0]
        fm = {lab: family_mean(r, imt) for lab, r in fam.items()}
        nf = combine.mean(parts[:2] + [(nof["curves"][:, :, [list(nof["imtls"]).index(imt)], :].astype(float), nof["w"])])[:, 0] if nof else None
        for pl, p in POES.items():
            for s, name in enumerate(names):
                x = iml(mean[s], lv, p)
                r = {"site": name, "imt": imt, "T": PERIOD[imt], "poe": p, "return_period": pl, "mean": x,
                     "q5": iml(q[0, s], lv, p), "q50": iml(q[1, s], lv, p), "q95": iml(q[2, s], lv, p)}
                if np.isfinite(x):
                    rt = {lab: float(np.exp(np.interp(np.log(x), np.log(lv), np.log(np.maximum(rate(fm[lab][s]), 1e-300))))) for lab in fam}
                    tot = sum(rt.values())
                    r.update({f"share_{lab}": v / tot for lab, v in rt.items()})
                if nf is not None:
                    xn = iml(nf[s], lv, p)
                    r["pga_nofaults"] = xn
                    r["faults_pct"] = 100 * (x / xn - 1) if np.isfinite(xn) and xn > 0 else np.nan
                rows.append(r)
        uhs[imt] = {"mean": mean, "q": q, "lv": lv, "fam": fm}
    return pd.DataFrame(rows), uhs


def fig_curves(fam, names, imt, s, path, ax=None, small=False):
    lv = fam["interface"]["imtls"][imt]
    parts = parts_of(fam, imt)
    m = combine.mean(parts)[s, 0]
    q = combine.exact([(c[[s]], w) for c, w in parts], (0.025, 0.975))[:, 0, 0]
    own = ax is None
    if own:
        f, ax = plt.subplots(figsize=(8, 6.5))
    for (c, w), lab in zip(parts, fam):
        draw(ax, lv, c[s, :, 0, :], w, COL[lab], lab, env=not small)
    ax.loglog(lv, m, color="k", lw=2.5, label="Full model")
    ax.fill_between(lv, q[0], q[1], color="k", alpha=0.15, lw=0)
    if own:
        finish(ax, imt, title(names[s]), list(POES.values()), path)
    else:
        ax.set_xlim(post.XLIMS)
        ax.set_ylim(post.YLIMS)
        for p in POES.values():
            ax.axhline(p, ls="--", lw=0.6, color="k")
        ax.set_title(title(names[s]), fontsize=11)
        ax.tick_params(labelsize=8)


def fig_curves_grid(fam, names, imt, path):
    n = len(names)
    cols = 5 if n > 12 else 4
    rows = int(np.ceil(n / cols))
    f, axs = plt.subplots(rows, cols, figsize=(3.6 * cols, 3.2 * rows), sharex=True, sharey=True)
    for s, ax in enumerate(axs.ravel()):
        if s < n:
            fig_curves(fam, names, imt, s, None, ax=ax, small=True)
        else:
            ax.axis("off")
    axs.ravel()[0].legend(handles=[Line2D([0], [0], color=COL[k], lw=2, label=k) for k in fam] + [Line2D([0], [0], color="k", lw=2.5, label="Full model")],
                          fontsize=8, loc="lower left", frameon=True)
    f.supxlabel(f"{imt} $[g]$", fontsize=13)
    f.supylabel(f"Probability of exceedance - {hc.INV_TIME:g} years", fontsize=13)
    f.tight_layout()
    f.savefig(path, dpi=250, bbox_inches="tight", facecolor="white")
    plt.close(f)


def uhs_of(uhs, imts, s, p, key="mean"):
    return np.array([iml(uhs[i][key][s] if key == "mean" else uhs[i]["q"][key, s], uhs[i]["lv"], p) for i in imts])


def fig_uhs(uhs, fam, imts, names, s, path, ax=None):
    T = np.array([PERIOD[i] for i in imts])
    x = np.where(T == 0, 0.03, T)
    own = ax is None
    if own:
        f, ax = plt.subplots(figsize=(8, 6))
    for (pl, p), (c, ls) in zip(POES.items(), (("k", "-"), ("0.4", "--"))):
        m = uhs_of(uhs, imts, s, p)
        lo, hi = uhs_of(uhs, imts, s, p, 0), uhs_of(uhs, imts, s, p, 2)
        ax.plot(x, m, color=c, ls=ls, lw=2.5, marker="o", ms=4, label=f"full model, {pl}")
        ax.fill_between(x, lo, hi, color=c, alpha=0.15, lw=0)
        for lab in fam:
            fm = np.array([iml(uhs[i]["fam"][lab][s], uhs[i]["lv"], p) for i in imts])
            ax.plot(x, fm, color=COL[lab], ls=ls, lw=1.3, label=f"{lab} alone" if pl == "475 yr" else None)
    ax.set_xscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(["PGA" if t == 0 else f"{t:g}" for t in T], fontsize=9 if own else 7)
    ax.set_title(title(names[s]), fontsize=14 if own else 11)
    if own:
        ax.set_xlabel("Period $[s]$", fontsize=13)
        ax.set_ylabel("Spectral acceleration $[g]$", fontsize=13)
        ax.legend(frameon=True, fontsize=10)
        f.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(f)


def fig_uhs_grid(uhs, fam, imts, names, path):
    n = len(names)
    cols = 5 if n > 12 else 4
    rows = int(np.ceil(n / cols))
    f, axs = plt.subplots(rows, cols, figsize=(3.6 * cols, 3.2 * rows), sharey=True)
    for s, ax in enumerate(axs.ravel()):
        if s < n:
            fig_uhs(uhs, fam, imts, names, s, None, ax=ax)
            ax.tick_params(labelsize=8)
        else:
            ax.axis("off")
    axs.ravel()[0].legend(handles=[Line2D([0], [0], color="k", lw=2.5, label="full, 475 yr"), Line2D([0], [0], color="0.4", ls="--", lw=2.5, label="full, 2475 yr")]
                          + [Line2D([0], [0], color=COL[k], lw=1.3, label=f"{k} alone") for k in fam], fontsize=7, frameon=True)
    f.supxlabel("Period $[s]$", fontsize=13)
    f.supylabel("Spectral acceleration $[g]$", fontsize=13)
    f.tight_layout()
    f.savefig(path, dpi=250, bbox_inches="tight", facecolor="white")
    plt.close(f)


def fig_uhs_shape(uhs, imts, names, lead, path):
    T = np.array([PERIOD[i] for i in imts])
    x = np.where(T == 0, 0.03, T)
    f, ax = plt.subplots(figsize=(9, 6))
    for s, name in enumerate(names):
        m = uhs_of(uhs, imts, s, POES["475 yr"])
        if not np.isfinite(m[0]) or m[0] <= 0:
            continue
        ax.plot(x, m / m[0], color=COL[lead[s]], lw=1.8, marker="o", ms=3, alpha=0.85)
        ax.annotate(title(name), (x[-1], m[-1] / m[0]), xytext=(4, 0), textcoords="offset points", fontsize=8, va="center")
    ax.set_xscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(["PGA" if t == 0 else f"{t:g}" for t in T])
    ax.set_xlabel("Period $[s]$", fontsize=13)
    ax.set_ylabel("SA / PGA at 475 yr", fontsize=13)
    ax.set_title("Uniform hazard spectra normalised by PGA, coloured by the leading regime", fontsize=14)
    ax.legend(handles=[Line2D([0], [0], color=COL[k], lw=2, label=f"{k} leads at PGA") for k in COL if k != "excluded"], frameon=True)
    f.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(f)


def fig_shares(t, names, imts, path):
    g = t[t["return_period"] == "475 yr"]
    fams = [c.replace("share_", "") for c in t.columns if c.startswith("share_")]
    n = len(names)
    cols = 5 if n > 12 else 4
    rows = int(np.ceil(n / cols))
    f, axs = plt.subplots(rows, cols, figsize=(3.4 * cols, 2.8 * rows), sharey=True)
    for s, ax in enumerate(axs.ravel()):
        if s >= n:
            ax.axis("off")
            continue
        h = g[g["site"] == names[s]].set_index("imt").reindex(imts)
        bottom = np.zeros(len(imts))
        for lab in fams:
            v = 100 * h[f"share_{lab}"].fillna(0).to_numpy()
            ax.bar(range(len(imts)), v, bottom=bottom, color=COL[lab], label=lab)
            bottom += v
        ax.set_xticks(range(len(imts)))
        ax.set_xticklabels(["PGA" if PERIOD[i] == 0 else f"{PERIOD[i]:g} s" for i in imts], fontsize=7, rotation=45)
        ax.set_title(title(names[s]), fontsize=10)
        ax.set_ylim(0, 100)
    axs.ravel()[0].legend(fontsize=7, frameon=True, loc="lower left")
    f.supylabel("Share of the 475-yr hazard (%)", fontsize=12)
    f.suptitle("Which regime controls the hazard, by period", fontsize=14)
    f.tight_layout()
    f.savefig(path, dpi=250, bbox_inches="tight", facecolor="white")
    plt.close(f)


def epistemic(fam, names, imt="PGA", p=0.002105):
    """
    Per city: PGA at p of the mean and the 5 / 50 / 95 % curves, and the share of the weighted
    variance of ln IML over the joint tree carried by each family (the family's realizations varied
    with the others at their mean curve; shares normalised to the sum).
    """
    lv = fam["interface"]["imtls"][imt]
    parts = parts_of(fam, imt)
    rt = [(rate(c[:, :, 0, :]), w) for c, w in parts]
    rows = []
    for s, name in enumerate(names):
        tot = 1 - np.exp(-sum(np.einsum("r,rl->l", w, r[s]) for r, w in rt))
        x = iml(tot, lv, p)
        var = {}
        for k, lab in enumerate(fam):
            others = sum(np.einsum("r,rl->l", w, r[s]) for j, (r, w) in enumerate(rt) if j != k)
            cur = 1 - np.exp(-(rt[k][0][s] + others))
            xi = imls(cur, lv, p)
            ok = np.isfinite(xi) & (xi > 0)
            w = rt[k][1][ok]
            lx = np.log(xi[ok])
            mu = w @ lx / w.sum()
            var[lab] = float(w @ (lx - mu) ** 2 / w.sum())
        tv = sum(var.values())
        q = combine.exact([(c[[s]], w) for c, w in parts], (0.05, 0.5, 0.95))[:, 0, 0]
        rows.append({"site": name, "mean": x, "q5": iml(q[0], lv, p), "q50": iml(q[1], lv, p), "q95": iml(q[2], lv, p),
                     **{f"var_{lab}": v for lab, v in var.items()},
                     **{f"varshare_{lab}": v / tv if tv > 0 else np.nan for lab, v in var.items()}})
    t = pd.DataFrame(rows)
    t["q95_over_q5"] = t["q95"] / t["q5"]
    t["mean_over_median"] = t["mean"] / t["q50"]
    return t


def fig_epistemic(t, names, path):
    f, axs = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.2, 1]})
    x = np.arange(len(names))
    ax = axs[0]
    ax.errorbar(x, t["mean"], yerr=[t["mean"] - t["q5"], t["q95"] - t["mean"]], fmt="o", color="k", capsize=3, label="mean, 5-95 %")
    ax.plot(x, t["q50"], "s", color="0.5", ms=5, label="median")
    ax.set_xticks(x)
    ax.set_xticklabels([title(n) for n in names], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("PGA 475 yr $[g]$", fontsize=13)
    ax.set_title("Epistemic band of the final tree", fontsize=14)
    ax.legend(frameon=True)
    ax = axs[1]
    bottom = np.zeros(len(names))
    for lab in COL:
        if f"varshare_{lab}" not in t:
            continue
        v = 100 * t[f"varshare_{lab}"].fillna(0).to_numpy()
        ax.bar(x, v, bottom=bottom, color=COL[lab], label=lab)
        bottom += v
    ax.set_xticks(x)
    ax.set_xticklabels([title(n) for n in names], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Share of the variance of ln PGA (%)", fontsize=13)
    ax.set_title("Which regime carries the epistemic uncertainty", fontsize=14)
    ax.set_ylim(0, 100)
    ax.legend(frameon=True, loc="lower right")
    f.tight_layout()
    f.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(f)


def return_periods(fam, names, imt="PGA"):
    lv = fam["interface"]["imtls"][imt]
    mean = combine.mean(parts_of(fam, imt))[:, 0]
    rows = []
    for s, name in enumerate(names):
        r = {"site": name}
        for g in LEVELS:
            ok = mean[s] > 0
            pe = float(np.exp(np.interp(np.log(g), np.log(lv[ok]), np.log(mean[s][ok])))) if lv[ok].min() <= g <= lv[ok].max() else np.nan
            r[f"T at {g:g} g (yr)"] = round(-hc.INV_TIME / np.log(1 - pe)) if np.isfinite(pe) and 0 < pe < 1 else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def fig_campaign(t, path):
    g = t[(t["imt"] == "PGA") & (t["return_period"] == "475 yr")].set_index("site")
    c = pd.DataFrame({"campaign": CAMPAIGN})
    c = c.join(g[["mean", "q5", "q95"]], how="inner")
    c["change_pct"] = 100 * (c["mean"] / c["campaign"] - 1)
    f, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(c))
    ax.bar(x - 0.2, c["campaign"], 0.4, color="0.6", label="sensitivity campaign (psha_chile5)")
    ax.bar(x + 0.2, c["mean"], 0.4, color="#2166ac", label="final tree mean")
    ax.errorbar(x + 0.2, c["mean"], yerr=[c["mean"] - c["q5"], c["q95"] - c["mean"]], fmt="none", ecolor="k", capsize=3, label="5-95 %")
    for i, v in enumerate(c["change_pct"]):
        ax.text(x[i] + 0.2, c["q95"].iloc[i] * 1.03, f"{v:+.0f}%", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([title(n) for n in c.index], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("PGA 475 yr $[g]$", fontsize=13)
    ax.set_title("From the campaign reference to the final model", fontsize=14)
    ax.legend(frameon=True)
    f.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(f)
    return c


def main():
    post.set_style()
    OUT.mkdir(parents=True, exist_ok=True)
    fam, nof, imts = load()
    names = fam["interface"]["names"]
    t, uhs = summary(fam, nof, imts, names)
    t.to_csv(OUT / "fr_summary.csv", index=False)
    for imt in CURVE_IMTS:
        if imt not in imts:
            continue
        for s in range(len(names)):
            fig_curves(fam, names, imt, s, OUT / f"fr_curves_{names[s]}_{imt}.png")
        fig_curves_grid(fam, names, imt, OUT / f"fr_curves_grid_{imt}.png")
    if len(imts) > 1:
        for s in range(len(names)):
            fig_uhs(uhs, fam, imts, names, s, OUT / f"fr_uhs_{names[s]}.png")
        fig_uhs_grid(uhs, fam, imts, names, OUT / "fr_uhs_grid.png")
        g = t[(t["return_period"] == "475 yr") & (t["imt"] == "PGA")].set_index("site")
        lead = [max(fam, key=lambda lab: g.loc[n, f"share_{lab}"]) if n in g.index and np.isfinite(g.loc[n, "share_interface"]) else "interface" for n in names]
        fig_uhs_shape(uhs, imts, names, lead, OUT / "fr_uhs_shape.png")
        fig_shares(t, names, imts, OUT / "fr_shares_period.png")
    e = epistemic(fam, names)
    e.to_csv(OUT / "fr_epistemic.csv", index=False)
    fig_epistemic(e, names, OUT / "fr_epistemic.png")
    return_periods(fam, names).to_csv(OUT / "fr_return_periods.csv", index=False)
    c = fig_campaign(t, OUT / "fr_campaign.png")
    c.to_csv(OUT / "fr_campaign.csv")
    pd.set_option("display.width", 220)
    g = t[t["return_period"] == "475 yr"].pivot_table(index="site", columns="imt", values="mean").reindex(names)[imts]
    print("mean SA at 475 yr (g):\n" + g.round(3).to_string())
    print("\nPGA 475 yr: band and variance shares:\n" + e[["site", "mean", "q5", "q95", "q95_over_q5"] + [c for c in e if c.startswith("varshare_")]].round(3).to_string(index=False))
    print("\ncampaign against final:\n" + c.round(3).to_string())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
