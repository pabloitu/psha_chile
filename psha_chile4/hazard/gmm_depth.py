# In-slab GMMs against depth, no source model: median PGA and sigma for a site
# directly above the hypocentre and at fixed rupture distance, from 30 to 200 km.
# The fixed-distance panel isolates each model's depth term (where it stops growing).
# Output: outputs/hazard/_gmm/gmm_depth.png, gmm_depth.csv

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from openquake.hazardlib import valid
from openquake.hazardlib.contexts import simple_cmaker

import paths
from hazard import config as hc

# settings
GMMS = {"AG20 SAM": '[AbrahamsonGulerce2020SSlab]\nregion = "SAM"',
        "Parker SA_S": '[ParkerEtAl2020SSlab]\nregion = "SA"\nsaturation_region = "SA_S"',
        "Montalva17": "[MontalvaEtAl2017SSlab]",
        "Kuehn20 SAM": '[KuehnEtAl2020SSlab]\nregion = "SAM"'}
MAGS = [6.5, 7.0, 7.5, 8.0]
DEPTHS = np.arange(30.0, 201.0, 5.0)     # hypocentre, km
R_FIX = 120.0                            # rupture distance of the depth-term panel, km
DZ = 5.0                                 # hypocentre - ztor, km (as in s03 for M7)
OUT = paths.OUT / "hazard" / "_gmm"


def median(gs, mag, hypo, rrup, rhypo):
    """Median PGA (g) and total sigma (ln) per GMM for arrays of hypocentre depth and distances."""
    cm = simple_cmaker(list(gs.values()), ["PGA"])
    n = len(hypo)
    ctx = cm.new_ctx(n)
    ctx["mag"] = mag
    ctx["hypo_depth"] = hypo
    ctx["ztor"] = np.maximum(hypo - DZ, 0.0)
    ctx["rrup"] = rrup
    ctx["rhypo"] = rhypo
    ctx["vs30"] = hc.VS30
    ctx["backarc"] = False
    ctx["sids"] = np.arange(n)
    ctx["occurrence_rate"] = 1.0
    mean, sig, _, _ = cm.get_mean_stds([ctx])
    return {k: (np.exp(mean[i, 0]), sig[i, 0]) for i, k in enumerate(gs)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    gs = {k: valid.gsim(v) for k, v in GMMS.items()}
    rows = []
    f, axs = plt.subplots(1, 3, figsize=(16, 5))
    for j, m in enumerate(MAGS):
        above = median(gs, m, DEPTHS, np.maximum(DEPTHS - DZ, 1.0), DEPTHS)
        fixed = median(gs, m, DEPTHS, np.full(len(DEPTHS), R_FIX), np.full(len(DEPTHS), R_FIX))
        for i, k in enumerate(gs):
            for z, a, s, b in zip(DEPTHS, above[k][0], above[k][1], fixed[k][0]):
                rows.append({"gmm": k, "M": m, "hypo_km": z, "pga_above": a, "sigma": s, "pga_rfix": b})
            if m in (7.0, 8.0):
                ls = "-" if m == 8.0 else "--"
                axs[0].semilogy(DEPTHS, above[k][0], ls, color=f"C{i}", label=f"{k}" if m == 8.0 else None)
                axs[1].semilogy(DEPTHS, fixed[k][0] / fixed[k][0][DEPTHS == 60.0], ls, color=f"C{i}")
            if m == 7.0:
                axs[2].plot(DEPTHS, above[k][1], color=f"C{i}")
    for ax in axs:
        for z in (67, 80, 120):
            ax.axvline(z, color="0.7", lw=0.6, ls=":")
        ax.axvspan(100, 130, color="#c44e52", alpha=0.08)
        ax.set_xlabel("hypocentre depth (km)")
        ax.grid(alpha=0.3)
    axs[0].set_title("median PGA, site above the hypocentre\nsolid M8.0, dashed M7.0", fontsize=10)
    axs[0].set_ylabel(f"PGA (g), vs30 {hc.VS30:g}")
    axs[0].legend(fontsize=8)
    axs[1].set_title(f"depth term: median at Rrup = Rhypo = {R_FIX:g} km, relative to 60 km depth\n"
                     "solid M8.0, dashed M7.0", fontsize=10)
    axs[1].set_ylabel("ratio to 60 km")
    axs[2].set_title("total sigma (ln), M7.0, site above (AG20 sigma varies with Rrup)", fontsize=10)
    axs[2].set_ylabel("sigma")
    f.suptitle("in-slab GMMs vs depth; shaded = slab_deep depths (100-130 km); "
               "dotted = depth-term caps 67 (Parker), 80 (Kuehn), 120 km (Montalva)", fontsize=10)
    f.tight_layout()
    f.savefig(OUT / "gmm_depth.png", dpi=220)
    plt.close(f)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "gmm_depth.csv", index=False)
    print(t[t["hypo_km"].isin([60, 110, 150])].pivot_table(index=["M", "hypo_km"], columns="gmm",
                                                            values="pga_above", sort=False).round(3).to_string())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()