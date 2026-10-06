# Interface Mmax by moment-rate closure and the corner magnitude, from the interface build
# (rates/closure.csv, rates/branches.csv of the reference variant).
# Per segment and for the full margin: catalog moment rate, geodetic budget chi mu A v, the Mmax at
# which the seismic rate (fitted a, b, tapered MFD) releases the budget (Avouac-type closure),
# the area-based Mmax (Thingbaijam et al. 2017) and the historical value of the forecast; plus the
# corner against Bird and Kagan (2004), subduction zones: 9.58 (+0.48 / -0.46), beta 0.64 +- 0.04.
# Outputs: outputs/interface/<variant>/rates/mmax_check.csv, figures/mmax_check.png
# Run: python hazard/mmax_check.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import brentq

import run
from lib import gr
from hazard.post import set_style
from variants import VARIANTS

VARIANT = "mmin55"
BK = {"corner": 9.58, "lo": 9.58 - 0.46, "hi": 9.58 + 0.48, "beta": 0.64, "beta_sd": 0.04}
GRID = np.arange(8.0, 10.51, 0.1)


def closing_mmax(lam, b, mmin, m0c, corner, target):
    """Mmax at which the tapered MFD with rate lam at mmin releases the moment target (None if never)."""
    f = lambda m: lam * gr.mpr("tapered", b, mmin, m, m0c, corner=corner) - target
    try:
        return round(brentq(f, mmin + 0.5, 11.0), 2)
    except ValueError:
        return None


def main(variant=VARIANT):
    set_style()
    c = run.config("interface", VARIANTS["interface"][variant])
    cl = pd.read_csv(c.OUT / "rates" / "closure.csv")
    bp = pd.read_csv(c.OUT / "rates" / "branches.csv", keep_default_na=False)
    bp = bp[(bp["rate"] == "seismic") & (bp["form"] == "tapered")].set_index("seg")
    rows = []
    for _, r in cl.iterrows():
        s = bp.loc[r["seg"]]
        chi = r["chi_assumed"]
        geo = r["m0_full_coupling"] * chi
        mclose = closing_mmax(s["lam"], s["b"], c.MMIN_HAZ, c.M0_C, c.CORNER, geo)
        rows.append({"segment": r["seg"], "b": round(s["b"], 3), "N(>=5.5)/yr": round(s["lam"], 3),
                     "M0 catalog (N m/yr)": r["m0_catalog"], "chi": chi, "M0 geodetic": geo,
                     "catalog / geodetic": round(r["m0_catalog"] / geo, 3), "chi effective": r["chi_effective"],
                     "Mmax historical": r["mmax"], "Mmax area (Thingbaijam)": round(r["mmax_thingbaijam"], 2),
                     "Mmax closing the budget": mclose,
                     "N(>=8) at Mmax historical": round(s["lam"] * float(gr.cum("tapered", s["b"], c.MMIN_HAZ, r["mmax"], 8.0, c.M0_C, c.CORNER)), 4)})
    t = pd.DataFrame(rows)
    t.to_csv(c.OUT / "rates" / "mmax_check.csv", index=False)
    pd.set_option("display.width", 220)
    print(t.to_string(index=False))
    print(f"\ncorner: model {c.CORNER}; Bird and Kagan (2004) subduction {BK['corner']} ({BK['lo']:.2f}-{BK['hi']:.2f}, 95 %), "
          f"beta {BK['beta']} +- {BK['beta_sd']} (b {1.5 * BK['beta']:.2f} +- {1.5 * BK['beta_sd']:.2f}); "
          f"fitted b full margin {bp.loc[c.FULL_ID, 'b']:.3f}")
    inside = BK["lo"] <= c.CORNER <= BK["hi"]
    print("corner inside the Bird and Kagan interval" if inside else "corner OUTSIDE the Bird and Kagan interval")

    f, axs = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(t))
    axs[0].bar(x - 0.2, t["M0 catalog (N m/yr)"], 0.4, color="#2166ac", label="catalog")
    axs[0].bar(x + 0.2, t["M0 geodetic"], 0.4, color="0.5", label="geodetic at the assumed coupling")
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(t["segment"], rotation=30, ha="right", fontsize=12)
    axs[0].set_ylabel("Moment rate $[N\\,m/yr]$", fontsize=14)
    axs[0].set_title("Moment budget", fontsize=16)
    axs[0].legend(frameon=True)
    for col, mk, lab in (("Mmax historical", "s", "historical (forecast)"), ("Mmax area (Thingbaijam)", "o", "area, Thingbaijam et al. (2017)"),
                         ("Mmax closing the budget", "^", "closes the geodetic budget")):
        axs[1].plot(x, t[col], mk, ms=10, label=lab)
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(t["segment"], rotation=30, ha="right", fontsize=12)
    axs[1].set_ylabel("$M_{max}$", fontsize=14)
    axs[1].set_title("Maximum magnitude", fontsize=16)
    axs[1].legend(frameon=True)
    f.savefig(c.FIG / "mmax_check.png", dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(f)
    print(f"wrote {c.OUT / 'rates' / 'mmax_check.csv'} and {c.FIG / 'mmax_check.png'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else VARIANT)
