# GMM check for the final logic tree, no source model involved: the candidate
# models per tectonic region evaluated at the site profile of hazard/config.py.
#   gmm_table.csv          per model: spectral period range, required site, rupture
#                          and distance parameters, total sigma at the scenarios
#   gr_<family>.png        for the slides: median PGA and the ratio of each model to the tree
#                          (geometric mean, equal weights) against Rrup; grey band = controlling
#                          distances of the campaign disaggregation
#   gf_<family>.png        backup: median PGA and SA(1.0), tree models and candidates left out
#   gmm_ratio.csv          ratio to the tree at the controlling distances
# Outputs: outputs/hazard/_gmm_final/. Run: python hazard/gmm_final.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

from openquake.hazardlib import valid
from openquake.hazardlib.contexts import simple_cmaker

import paths
from hazard import config as hc
from hazard.logic_tree import GMM_FINAL, GMM_EXTRA
from hazard.post import set_style

OUT = paths.OUT / "hazard" / "_gmm_final"
IMTS = ["PGA", "SA(1.0)"]
RRUP = np.logspace(1, np.log10(500), 60)
# scenarios per region: label, mag, hypocentre depth, ztor, rake, dip, width
SCEN = {
    "Subduction Interface": [("M8.8, ztor 10 km", 8.8, 25.0, 10.0, 90.0, 18.0, 150.0),
                             ("M7.5, ztor 15 km", 7.5, 25.0, 15.0, 90.0, 18.0, 60.0)],
    "Subduction IntraSlab": [("M7.3, hypocentre 60 km", 7.3, 60.0, 50.0, -90.0, 60.0, 30.0),
                             ("M7.3, hypocentre 100 km", 7.3, 100.0, 90.0, -90.0, 60.0, 30.0)],
    "Active Shallow Crust": [("M7.0, strike-slip", 7.0, 10.0, 0.0, 180.0, 90.0, 15.0),
                             ("M6.5, reverse", 6.5, 10.0, 2.0, 90.0, 45.0, 15.0)],
}
FILE = {"Subduction Interface": "interface", "Subduction IntraSlab": "intraslab", "Active Shallow Crust": "crustal"}
CTRL = {"Subduction Interface": (30.0, 70.0), "Subduction IntraSlab": (55.0, 90.0)}
COLOR = {"AbrahamsonGulerce2020": "#2166ac", "ParkerEtAl2020": "#e0641e", "KuehnEtAl2020": "#2e8b57",
         "MontalvaEtAl2017": "#a50f15", "AbrahamsonEtAl2015": "#7f7f7f",
         "AbrahamsonEtAl2014": "#2166ac", "BooreEtAl2014": "#e0641e", "CampbellBozorgnia2014": "#2e8b57",
         "ChiouYoungs2014": "#a50f15"}
SHORT = {"AbrahamsonGulerce2020": "AG20", "ParkerEtAl2020": "Parker et al. (2020)",
         "KuehnEtAl2020": "Kuehn et al. (2020)", "MontalvaEtAl2017": "Montalva et al. (2017)",
         "AbrahamsonEtAl2015": "BC Hydro (2016)",
         "AbrahamsonEtAl2014": "ASK14", "BooreEtAl2014": "BSSA14", "CampbellBozorgnia2014": "CB14",
         "ChiouYoungs2014": "CY14"}


def spec(name, kw):
    return f"[{name}]" + "".join(f"\n{k} = {v!r}".replace("'", '"') for k, v in kw.items())


def stem(name):
    for k in COLOR:
        if name.startswith(k):
            return k
    return name


def periods(g):
    for a in ("COEFFS", "COEFFS_SITE") + tuple(dir(g)):
        t = getattr(g, a, None)
        if hasattr(t, "sa_coeffs"):
            return sorted(i.period for i in t.sa_coeffs)
    return []


def evaluate(g, imts, mag, zhyp, ztor, rake, dip, width, rrup):
    """Median (g) and total sigma per IMT of one GMM along rrup."""
    cm = simple_cmaker([g], imts)
    n = len(rrup)
    ctx = cm.new_ctx(n)
    rjb = np.sqrt(np.maximum(rrup ** 2 - ztor ** 2, 0.0))
    vals = {"mag": mag, "hypo_depth": zhyp, "ztor": ztor, "rrup": rrup, "rhypo": np.sqrt(rrup ** 2 + (zhyp - ztor) ** 2),
            "rjb": rjb, "rx": rjb, "ry0": 0.0, "vs30": hc.VS30, "vs30measured": hc.VS30_MEASURED,
            "z1pt0": hc.Z1PT0, "z2pt5": hc.Z2PT5, "backarc": False,
            "sids": np.arange(n), "occurrence_rate": 1.0, "width": width, "rake": rake, "dip": dip}
    for k, v in vals.items():
        if k in ctx.dtype.names:
            ctx[k] = v
    m, s, _, _ = cm.get_mean_stds([ctx])
    return np.exp(m[0]), s[0]


def main():
    set_style()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, rat = [], []
    for trt, scens in SCEN.items():
        cands = [(n, w, kw, True) for n, w, kw in GMM_FINAL[trt]] + [(n, 0.0, kw, False) for n, kw in GMM_EXTRA.get(trt, [])]
        f, axs = plt.subplots(len(IMTS), len(scens), figsize=(16, 9), sharex=True, sharey="row")
        g, gr = plt.subplots(2, len(scens), figsize=(16, 9), sharex=True, sharey="row", gridspec_kw={"height_ratios": [3, 2]})
        for j, (lab, mag, zhyp, ztor, rake, dip, width) in enumerate(scens):
            rr = RRUP[RRUP >= max(ztor, RRUP[0])]        # a surface site is at least ztor away
            res = {}
            for n, w, kw, inn in cands:
                m, sig = evaluate(valid.gsim(spec(n, kw)), IMTS, mag, zhyp, ztor, rake, dip, width, rr)
                res[n] = (m, sig, w, inn, kw)
            ws = np.array([r[2] for r in res.values() if r[3]])
            ref = np.exp(sum(w * np.log(r[0][0]) for w, r in zip(ws, [r for r in res.values() if r[3]])) / ws.sum())
            for n, (m, sig, w, inn, kw) in res.items():
                k = stem(n)
                for i, imt in enumerate(IMTS):
                    axs[i, j].loglog(rr, m[i], color=COLOR[k], lw=2.2 if inn else 1.2, ls="-" if inn else "--",
                                     label=SHORT[k] + ("" if inn else " (not in the tree)"))
                if inn:
                    gr[0, j].loglog(rr, m[0], color=COLOR[k], lw=2.5, label=SHORT[k])
                    gr[1, j].semilogx(rr, m[0] / ref, color=COLOR[k], lw=2.5)
                    if trt in CTRL and CTRL[trt][1] > rr[0]:
                        c = np.array(CTRL[trt])
                        rc = np.sqrt(c[0] * c[1])
                        rat.append({"trt": trt, "scenario": lab, "gmm": n, "Rrup_km": rc,
                                    "ratio_to_tree": float(np.interp(rc, rr, m[0] / ref))})
                per = periods(valid.gsim(spec(n, kw)))
                i100 = int(np.argmin(np.abs(rr - 100)))
                rows.append({"trt": trt, "gmm": n, "kwargs": kw, "weight": w, "in_tree": inn, "scenario": lab,
                             "T_min": per[0] if per else np.nan, "T_max": per[-1] if per else np.nan,
                             "site": " ".join(sorted(valid.gsim(spec(n, kw)).REQUIRES_SITES_PARAMETERS)),
                             "rupture": " ".join(sorted(valid.gsim(spec(n, kw)).REQUIRES_RUPTURE_PARAMETERS)),
                             "distance": " ".join(sorted(valid.gsim(spec(n, kw)).REQUIRES_DISTANCES)),
                             **{f"median_{imt}_100km_g": m[i][i100] for i, imt in enumerate(IMTS)},
                             **{f"sigma_{imt}_100km": sig[i][i100] for i, imt in enumerate(IMTS)},
                             **{f"median_{imt}_500km_g": m[i][-1] for i, imt in enumerate(IMTS)}})
            axs[0, j].set_title(lab, fontsize=14)
            gr[0, j].set_title(lab, fontsize=14)
            axs[-1, j].set_xlabel("Rupture distance $[km]$", fontsize=14)
            gr[-1, j].set_xlabel("Rupture distance $[km]$", fontsize=14)
            gr[1, j].axhline(1.0, color="k", lw=0.8)
            gr[1, j].set_yscale("log")
            gr[1, j].set_yticks([0.5, 0.7, 1.0, 1.4, 2.0])
            gr[1, j].set_yticklabels(["0.5", "0.7", "1", "1.4", "2"])
            gr[1, j].set_ylim(0.4, 2.5)
            gr[1, j].yaxis.set_minor_formatter(NullFormatter())
            if trt in CTRL and CTRL[trt][1] > rr[0]:
                for a in (gr[0, j], gr[1, j]):
                    a.axvspan(*CTRL[trt], color="0.35", alpha=0.18, lw=0)
        for i, imt in enumerate(IMTS):
            axs[i, 0].set_ylabel(f"Median {imt} $[g]$", fontsize=14)
            axs[i, 0].set_ylim(1e-4, 3)
        gr[0, 0].set_ylabel("Median PGA $[g]$", fontsize=14)
        gr[0, 0].set_ylim(1e-3, 3)
        gr[1, 0].set_ylabel("Ratio to the tree", fontsize=14)
        for a in list(axs.ravel()) + list(gr.ravel()):
            a.grid(axis="both", which="major", linewidth=1)
            a.grid(axis="both", which="minor", linewidth=0.4)
        axs[0, 0].legend(loc="lower left", frameon=True)
        gr[0, 0].legend(loc="lower left", frameon=True)
        sub = f"Vs30 {hc.VS30:g} m/s ({'measured' if hc.VS30_MEASURED else 'inferred'})"
        note = "; grey band: controlling distances" if trt in CTRL else ""
        f.suptitle(f"{trt}, {sub}", fontsize=16)
        g.suptitle(f"{trt}, {sub}{note}", fontsize=16)
        f.tight_layout()
        g.tight_layout()
        f.savefig(OUT / f"gf_{FILE[trt]}.png", dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
        g.savefig(OUT / f"gr_{FILE[trt]}.png", dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
        plt.close(f)
        plt.close(g)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "gmm_table.csv", index=False)
    r = pd.DataFrame(rat)
    r.to_csv(OUT / "gmm_ratio.csv", index=False)
    print(r.pivot_table(index=["trt", "scenario"], columns="gmm", values="ratio_to_tree", sort=False).round(2).to_string())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
