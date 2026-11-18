"""epicentres of the final catalogue coloured by depth, north and south panels side by side; one figure for
Mw >= 4.5 and one for Mw >= 6.5."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "catalog")]
from plots import colors as C
from plots import maps as M

# settings
RUN = "2026-11-17g"
CAT = ROOT / "catalog" / "frozen" / RUN / f"catalog_{RUN}.csv"
OUT = ROOT / "catalog" / "FIGURES" / "maps"
CMAP = "pp.pt_sea"
WIDTH = 4.2
PANELS = [(4.5, 1.0, (4.5, 5.5, 6.5, 7.5, 8.5)), (6.5, 1.0, (6.5, 7.5, 8.5, 9.5))]

C.apply()
OUT.mkdir(parents=True, exist_ok=True)
c = pd.read_csv(CAT, low_memory=False)
c = c[c.in_domain & (c.mw >= 4.45)].sort_values("mw")
c["col"] = C.depth_color(c.depth, CMAP)
e = C.DEPTH_EDGES
hz = M.color_handles(C.depth_colors(CMAP) + [C.NODATA],
                     [f"{a}–{b}" for a, b in zip(e[:-2], e[1:-1])] + [f"> {e[-2]}", "unknown"])
for m0, k, leg in PANELS:
    x = c[c.mw >= m0 - 0.05]
    w, h = M.panel_size(M.halves()[0][1], WIDTH)
    fig = plt.figure(figsize=(2 * w + 0.9, h + 1.3), layout="constrained")
    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.02, wspace=0.0, hspace=0.0)
    for i, (h, ext) in enumerate(M.halves()):
        ax = M.domain_map(fig, (1, 2, i + 1), ext, labels="left" if i == 0 else "right")
        ax.scatter(x.lon, x.lat, s=M.size(x.mw, k), c=x.col, alpha=M.ALPHA if m0 < 6 else 0.8,
                   edgecolors="none" if m0 < 6 else "0.2", linewidths=0.3, transform=M.PC, zorder=3, rasterized=True)
    fig.axes[0].text(0.03, 0.985, f"Mw ≥ {m0:g}, {len(x):,} events", transform=fig.axes[0].transAxes, va="top",
                     fontsize=10, zorder=5)
    fig.legend(handles=hz, loc="outside lower left", ncol=4, title="depth (km)", columnspacing=0.8)
    fig.legend(handles=M.size_handles(leg, k), loc="outside lower right", ncol=len(leg), title="Mw", columnspacing=1.6, handletextpad=1.3)
    fig.savefig(OUT / f"positions_m{int(m0 * 10)}.png", dpi=150)
