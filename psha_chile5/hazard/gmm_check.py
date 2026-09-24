# GMMs of the logic tree evaluated on their own, no source model involved.
#   g1_depth_mag.png   depth and magnitude scaling of the in-slab GMMs
#   g2_scenarios.png   median PGA of the controlling scenarios per city, and the
#                      distance in sigmas from each median to the city PGA; the
#                      scenarios are the per-region means of the disaggregation
#   g3_attenuation.png median PGA against distance for those scenarios
#   g4_depth.png       median PGA against hypocentre depth, fixed distance and
#                      site above the hypocentre
# Outputs: outputs/hazard/_gmm/

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory as blend

from openquake.hazardlib import valid
from openquake.hazardlib.contexts import simple_cmaker

from hazard import config as hc

# settings
SLAB = {"AG20": ('[AbrahamsonGulerce2020SSlab]\nregion = "SAM"', "#4c72b0"),
        "Parker": ('[ParkerEtAl2020SSlab]\nregion = "SA"\nsaturation_region = "SA_S"', "#dd8452"),
        "Montalva17": ("[MontalvaEtAl2017SSlab]", "#c44e52")}
INTER = {"AG20": ('[AbrahamsonGulerce2020SInter]\nregion = "SAM"', "#4c72b0"),
         "Parker": ('[ParkerEtAl2020SInter]\nregion = "SA"\nsaturation_region = "SA_S"', "#dd8452"),
         "Kuehn20": ('[KuehnEtAl2020SInter]\nregion = "SAM"', "#55a868")}
# cities and return period of the scenario figure; scenarios come from the
# disaggregation (hazard/disagg.py): mean M and Rrup per region, city PGA
SITES = {"Iquique": "iquique", "Santiago": "santiago_centro"}
RP = 475
DISAGG = hc.OUT_ROOT / "_disagg"
SLAB_ZMAX = 130.0                   # in-slab hypocentre: Rrup, capped here (event below the city)
IF_ZHYP, IF_ZTOR = 25.0, 15.0       # interface hypocentre and top of rupture


def scenarios():
    """
    City PGA, disaggregation mean epsilon and the two controlling scenarios per city.

    Returns
    -------
    dict
        city -> (pga, mean_eps, [(label, gmm set, M, hypocentre, ztor, Rrup, share), ...])
    """
    a = pd.read_csv(DISAGG / "disagg_summary.csv")
    t = pd.read_csv(DISAGG / "disagg_trt_summary.csv")
    out = {}
    for city, site in SITES.items():
        if site not in set(a["site"]):
            continue
        r = a[(a["site"] == site) & (a["return_period"] == RP)].iloc[0]
        sc = []
        for trt, gset, kind in (("Subduction IntraSlab", SLAB, "in-slab"), ("Subduction Interface", INTER, "interface")):
            x = t[(t["site"] == site) & (t["return_period"] == RP) & (t["trt"] == trt)].iloc[0]
            m, rr = round(x["mean_M"], 1), round(x["mean_R"])
            z, zt = (min(rr, SLAB_ZMAX), min(rr, SLAB_ZMAX) - 10) if kind == "in-slab" else (IF_ZHYP, IF_ZTOR)
            sc.append((f"{kind} M{m:.1f}, Rrup {rr} km\n{x['share']:.0f} % of the hazard", gset, m, z, zt, rr,
                       x["share"]))
        out[city] = (r["iml"], r["mean_eps"], sc)
    return out


DEPTHS = np.arange(40.0, 181.0, 5.0)
MAGS = np.arange(6.5, 8.51, 0.1)
R_FIX = 120.0
MMAX_SD = 8.2                       # slab_deep Mmax of the source model
REPI = np.logspace(0, np.log10(400), 40)
OUT = hc.OUT_ROOT / "_gmm"


def med(gmm, mag, zhyp, ztor, rrup):
    """Median PGA (g) and total sigma of one GMM; one of the inputs may be an array."""
    g = valid.gsim(gmm)
    cm = simple_cmaker([g], ["PGA"])
    n = max(np.size(mag), np.size(zhyp), np.size(rrup))
    ctx = cm.new_ctx(n)
    vals = {"mag": mag, "hypo_depth": zhyp, "ztor": ztor, "rrup": rrup, "rhypo": rrup,
            "rjb": np.maximum(np.asarray(rrup) - 10, 0), "vs30": hc.VS30, "backarc": False,
            "sids": np.arange(n), "occurrence_rate": 1.0, "z1pt0": hc.Z1PT0, "z2pt5": hc.Z2PT5,
            "width": 40.0, "rake": 90.0, "dip": 30.0}
    for k, v in vals.items():
        if k in ctx.dtype.names:
            ctx[k] = v
    m, s, _, _ = cm.get_mean_stds([ctx])
    return np.exp(m[0, 0]), s[0, 0]


def fig_depth_mag(path):
    f, axs = plt.subplots(1, 2, figsize=(10.5, 4.2))
    for k, (g, col) in SLAB.items():
        r = med(g, 7.5, DEPTHS, DEPTHS - 10, np.full(len(DEPTHS), R_FIX))[0]
        r = r / r[DEPTHS == 60.0]
        axs[0].plot(DEPTHS, r, color=col, lw=1.8, label=k)
        axs[0].annotate(f"{r[-1]:.2f}", (DEPTHS[-1], r[-1]), color=col, fontsize=8,
                        xytext=(3, -2), textcoords="offset points")
        m = med(g, MAGS, 110.0, 100.0, np.full(len(MAGS), R_FIX))[0]
        m = m / m[np.isclose(MAGS, 7.0)]
        axs[1].plot(MAGS, m, color=col, lw=1.8, label=k)
        axs[1].annotate(f"{m[-1]:.1f}", (MAGS[-1], m[-1]), color=col, fontsize=8,
                        xytext=(3, -2), textcoords="offset points")
    axs[0].axhline(1, color="k", lw=0.7)
    axs[0].axvspan(100, 130, color="0.88", zorder=0)
    axs[0].text(115, 0.03, "slab_deep", fontsize=8, color="0.35", ha="center", va="bottom",
                transform=blend(axs[0].transData, axs[0].transAxes))
    axs[0].set_xlabel("hypocentre depth km")
    axs[0].set_ylabel("PGA / PGA(60 km)")
    axs[0].set_title("depth, M7.5", fontsize=9)
    axs[0].legend(fontsize=8, loc="upper left")
    axs[1].axhline(1, color="k", lw=0.7)
    axs[1].axvspan(MMAX_SD, MAGS[-1], color="0.88", zorder=0)
    axs[1].text((MMAX_SD + MAGS[-1]) / 2, 0.03, f"> Mmax {MMAX_SD:g}", fontsize=8, color="0.35",
                ha="center", va="bottom", transform=blend(axs[1].transData, axs[1].transAxes))
    axs[1].set_xlabel("M")
    axs[1].set_ylabel("PGA / PGA(M7.0)")
    axs[1].set_title("magnitude, hypocentre 110 km", fontsize=9)
    for ax in axs:
        ax.grid(alpha=0.3)
        ax.margins(x=0.10)
    f.suptitle(f"in-slab GMMs, Rrup = Rhypo = {R_FIX:g} km, vs30 {hc.VS30:g}", fontsize=10)
    f.tight_layout()
    f.savefig(path, dpi=300)
    plt.close(f)


def fig_scenarios(path, cities):
    f, axs = plt.subplots(1, len(cities), figsize=(5.6 * len(cities), 4.8), sharey=True, squeeze=False)
    rows = []
    for ax, (city, (target, eps_d, scen)) in zip(axs[0], cities.items()):
        x, ticks, names = 0, [], []
        for lab, gset, m, z, zt, r, sh in scen:
            x0 = x
            for k, (g, col) in gset.items():
                mu, sg = med(g, m, z, zt, np.array([r]))
                mu, sg = float(mu[0]), float(sg[0])
                e = np.log(target / mu) / sg
                ax.bar(x, mu, 0.78, color=col)
                ax.errorbar(x - 0.15, mu, yerr=[[mu - mu * np.exp(-sg)], [mu * np.exp(sg) - mu]],
                            color="0.3", capsize=3, lw=1)
                ax.plot([x + 0.15, x + 0.15], [mu, target], color="k", lw=1, ls=(0, (3, 2)))
                ax.text(x + 0.15, (mu + target) / 2, f"{e:.1f}$\\sigma$", fontsize=8, ha="center",
                        va="center", bbox={"fc": "white", "ec": "none", "pad": 1})
                rows.append({"city": city, "scenario": lab.replace("\n", " "), "gmm": k, "median_g": mu,
                             "sigma": sg, "eps_to_target": e, "target_g": target})
                ticks.append(x)
                names.append(k)
                x += 1
            ax.text((x0 + x - 1) / 2, 0.97, lab, fontsize=8, ha="center", va="top",
                    transform=blend(ax.transData, ax.transAxes))
            if x < len(scen) * (len(gset) + 1) - 1:
                ax.axvline(x, color="0.85", lw=0.8)
            x += 1
        ax.axhline(target, color="k", lw=1.2, ls="--")
        ax.annotate(f"PGA {RP} yr {target:.2f} g", (x - 1.4, target), fontsize=8, ha="right", va="bottom",
                    xytext=(0, 2), textcoords="offset points")
        ax.set_xticks(ticks)
        ax.set_xticklabels(names, fontsize=8, rotation=30, ha="right")
        ax.set_ylim(0, max(1.5, target * 1.3))
        ax.set_title(f"{city}, disaggregation mean epsilon {eps_d:.2f}", fontsize=10)
        ax.grid(axis="y", alpha=0.3)
    axs[0][0].set_ylabel("median PGA g")
    f.suptitle(f"controlling scenarios from the disaggregation, {RP} yr, vs30 {hc.VS30:g}; "
               "whisker +/-1 sigma, dashed = distance to the city PGA", fontsize=10)
    f.tight_layout()
    f.savefig(path, dpi=300)
    plt.close(f)
    return pd.DataFrame(rows)


def fig_attenuation(path, cities):
    f, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, (lab, gset, m, z, zt, _, _) in zip(axs, next(iter(cities.values()))[2]):
        for k, (g, col) in gset.items():
            rr = np.sqrt(REPI ** 2 + zt ** 2)
            mu, sg = med(g, m, z, zt, rr)
            ax.loglog(REPI, mu, color=col, lw=2, label=k)
            if k == "AG20":
                ax.fill_between(REPI, mu * np.exp(-sg), mu * np.exp(sg), color=col, alpha=0.12)
        ax.set_title(lab.split("\n")[0], fontsize=9)
        ax.set_xlabel("Repi km")
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8)
    axs[0].set_ylabel("median PGA g")
    axs[0].set_ylim(1e-2, 3)
    f.suptitle(f"controlling scenarios, band = +/-1 sigma of AG20, vs30 {hc.VS30:g}", fontsize=10)
    f.tight_layout()
    f.savefig(path, dpi=300)
    plt.close(f)


def fig_depth(path, mag=7.5):
    f, axs = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    for k, (g, col) in SLAB.items():
        a = med(g, mag, DEPTHS, DEPTHS - 10, np.full(len(DEPTHS), R_FIX))[0]
        b = med(g, mag, DEPTHS, DEPTHS - 10, DEPTHS - 10)[0]
        axs[0].semilogy(DEPTHS, a, color=col, lw=1.8, label=k)
        axs[1].semilogy(DEPTHS, b, color=col, lw=1.8, label=k)
    for ax, t in zip(axs, (f"Rrup = Rhypo = {R_FIX:g} km", "site above the hypocentre")):
        ax.axvspan(100, 130, color="0.88", zorder=0)
        ax.text(115, 0.03, "slab_deep", fontsize=8, color="0.35", ha="center", va="bottom",
                transform=blend(ax.transData, ax.transAxes))
        ax.set_xlabel("hypocentre depth km")
        ax.set_title(t, fontsize=9)
        ax.grid(alpha=0.3, which="both")
    axs[0].set_ylabel("median PGA g")
    axs[0].legend(fontsize=8)
    f.suptitle(f"in-slab GMMs, M{mag:g}, vs30 {hc.VS30:g}", fontsize=10)
    f.tight_layout()
    f.savefig(path, dpi=300)
    plt.close(f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig_depth_mag(OUT / "g1_depth_mag.png")
    fig_depth(OUT / "g4_depth.png")
    if not (DISAGG / "disagg_trt_summary.csv").exists():
        print(f"[skip] gmm_check scenarios: run hazard/disagg.py first")
        return
    cities = scenarios()
    if not cities:
        print("[skip] gmm_check scenarios: none of the cities in the disaggregation")
        return
    t = fig_scenarios(OUT / "g2_scenarios.png", cities)
    fig_attenuation(OUT / "g3_attenuation.png", cities)
    t.to_csv(OUT / "gmm_scenarios.csv", index=False)
    print(t.round(2).to_string(index=False))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()