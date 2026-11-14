"""X5: the cluster families of x5_ace.py (mechanism only) on the nodal planes and against depth."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import x5_ace as A
import x5_lib as X

sys.path.insert(0, str(X.ROOT))
from palette import CLASS_COLOR  # noqa: E402

FAM = {"tight thrust": CLASS_COLOR["interface"], "broad reverse": "#e6a100", "normal": CLASS_COLOR["intraslab_shallow"], "noise": "0.6"}
OUT = Path(__file__).parent / "figs" / "ace.png"


def main():
    x, P = A.data()
    F = pd.read_csv(X.TAB / "x5_ace_mech_families.csv")
    lab, n = F.family.to_numpy(), len(F)
    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, ax = plt.subplots(1, 3, figsize=(17, 5.8), gridspec_kw={"width_ratios": [1.3, 0.8, 0.9]})
    a = ax[0]
    for k in ("noise", "normal", "broad reverse", "tight thrust"):
        q = np.r_[lab == k, lab == k]
        a.scatter(P[q, 0], P[q, 1], s=10, color=FAM[k], alpha=0.7, lw=0, label=f"{k} ({(lab == k).sum()})")
    a.set(xlim=(-180, 180), ylim=(-180, 180), xticks=np.arange(-180, 181, 60), yticks=np.arange(-180, 181, 45),
          xlabel="Strike of the nodal plane − strike of Slab2 (°)", ylabel="Rake (°)", title="1. Families found in the nodal planes")
    a.grid(color="0.88", lw=0.6)
    a.legend(loc="lower right", frameon=False, fontsize=10, markerscale=2)
    a = ax[1]
    b = np.arange(-45, 70.1, 5)
    for k in ("tight thrust", "broad reverse", "normal"):
        a.hist(F.d[lab == k].clip(-45, 70), bins=b, histtype="step", lw=2.2, color=FAM[k], density=True, orientation="horizontal")
    a.axhspan(-15, 15, color=CLASS_COLOR["interface"], alpha=0.1, lw=0)
    a.axhline(0, color="k", lw=1.2)
    a.set(ylim=(70, -45), xlabel="Share of the family (density)", ylabel="Depth − Slab2 surface (km)", title="2. Depth of each family")
    a = ax[2]
    a.scatter(F.m.clip(upper=4.95), F["tight thrust"], s=9, color="0.3", alpha=0.5, lw=0)
    a.axvline(1, color="k", lw=1.5)
    a.set(xlim=(0, 5), ylim=(-0.02, 1.02), xlabel="Misfit m to the interface mechanism (ellipse edge at 1)",
          ylabel="Probability of the tight thrust family", title="3. Against the ellipse")
    f.suptitle(f"Clusters of nodal planes after Specht et al. (2017), {n} events over the shallow slab", fontsize=13)
    f.tight_layout(rect=(0, 0, 1, 0.95))
    f.savefig(OUT, dpi=160)


if __name__ == "__main__":
    main()
