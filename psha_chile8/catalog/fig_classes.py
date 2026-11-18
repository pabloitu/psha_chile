"""epicentres of the final catalogue coloured by tectonic class (palette.CLASS), north and south panels side by
side; one figure for Mw >= 4.5 and one for Mw >= 6.5. An event takes the sub-class of the class with weight 1, else
"shared between classes"."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "catalog")]
from plots import colors as C
from plots import maps as M

# settings
RUN = "2026-11-17g"
CAT = ROOT / "catalog" / "frozen" / RUN / f"catalog_{RUN}.csv"
OUT = ROOT / "catalog" / "FIGURES" / "maps"
WIDTH = 4.2
PANELS = [(4.5, 1.0, (4.5, 5.5, 6.5, 7.5, 8.5)), (6.5, 1.0, (6.5, 7.5, 8.5, 9.5))]
ORDER = ["interface", "antarctic_interface", "intraslab_shallow", "intraslab_intermediate", "jujuy_nest", "forearc", "arc",
         "backarc", "patagonia", "outside", "outer_rise", "split"]

C.apply()
OUT.mkdir(parents=True, exist_ok=True)
name, col = C.CLASS_NAME, C.CLASS_COLOR
c = pd.read_csv(CAT, low_memory=False)
c = c[c.in_domain & (c.mw >= 4.45)].sort_values("mw")
c["lab"] = np.select([c.cls == "interface", c.cls == "in-slab", c.cls == "crustal", c.cls == "outer rise", c.cls == "unclassified"],
                     [c.sub_interface, c.sub_inslab, c.sub_crustal, "outer_rise", "unclassified"], "split")
for m0, k, leg in PANELS:
    x = c[c.mw >= m0 - 0.05]
    w, h = M.panel_size(M.halves()[0][1], WIDTH)
    fig = plt.figure(figsize=(2 * w + 0.9, h + 1.7), layout="constrained")
    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.02, wspace=0.0, hspace=0.0)
    for i, (h, ext) in enumerate(M.halves()):
        ax = M.domain_map(fig, (1, 2, i + 1), ext, labels="left" if i == 0 else "right")
        ax.scatter(x.lon, x.lat, s=M.size(x.mw, k), c=x.lab.map(col), alpha=M.ALPHA if m0 < 6 else 0.85,
                   edgecolors="none" if m0 < 6 else "0.2", linewidths=0.3, transform=M.PC, zorder=3, rasterized=True)
    fig.axes[0].text(0.03, 0.985, f"Mw ≥ {m0:g}, {len(x):,} events", transform=fig.axes[0].transAxes, va="top",
                     fontsize=10, zorder=5)
    n = x.lab.value_counts()
    keys = [o for o in ORDER if n.get(o, 0)]
    hc = M.color_handles([col[o] for o in keys], [f"{name[o]} ({n[o]:,})" for o in keys])
    fig.legend(handles=hc, loc="outside lower center", ncol=3, title="class", columnspacing=0.8, fontsize=9)
    fig.axes[1].legend(handles=M.size_handles(leg, k), loc="lower left", title="Mw", labelspacing=1.4, handletextpad=1.3,
                       borderpad=1.0)
    fig.savefig(OUT / f"classes_m{int(m0 * 10)}.png", dpi=150)
