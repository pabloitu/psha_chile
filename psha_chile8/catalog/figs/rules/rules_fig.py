# The order of sources per property and period (catalogue rules of the final catalogue), one row: Mw, epicentre, depth
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pituplots import use_theme

OUT = Path(__file__).resolve().parents[2] / "FIGURES" / "rules"
RULES = [("Mw", [("before 1904", [("Ruiz and\nMadariaga 2018", "lit"), ("Cabello\net al. 2025", "hist")]),
                 ("1904–1975", [("Ruiz and\nMadariaga 2018", "lit"), ("Centennial Mw", "best"), ("ISC-GEM\ndirect Mw", "best"),
                                ("Centennial Ms,\nmB converted", "glob"), ("ISC-GEM\nproxy Mw", "glob")]),
                 ("1976–", [("GCMT\n(Mw ≥ 5.4)", "best"), ("W-phase,\nregional Mw", "best"), ("GCMT < 5.4,\nlowered", "best"),
                            ("Ruiz and\nMadariaga 2018", "lit"), ("Ms, ML, mb\nconverted", "glob")])]),
         ("epicentre", [("before 1904", [("Cabello\net al. 2025", "hist")]),
                        ("1904–1963", [("Centennial,\nrelocated", "best"), ("ISC-GEM", "glob"), ("ISC", "glob")]),
                        ("1964–, outside\nthe network", [("GCCEL", "best"), ("ISC-EHB L1/L2", "best"), ("ISC", "glob"), ("ComCat", "glob")]),
                        ("1982–, inside\nthe network", [("Potin et al.\n2024, CSN", "local"), ("GCCEL", "best"), ("ISC-EHB L1/L2", "best"),
                                                        ("ISC", "glob")])]),
         ("depth", [("before 1904", [("not measured", "hist")]),
                    ("1904–1963", [("Centennial\nfree depth", "best"), ("ISC-GEM\nquality A, B", "best")]),
                    ("1964–, outside the\nnetwork, offshore", [("GCCEL", "best"), ("ISC-EHB L1/L2", "best"), ("ISC", "glob"),
                                                               ("ComCat", "glob")]),
                    ("1982–, inside\nthe network", [("Potin et al.\n2024, CSN", "local"), ("GCCEL", "best"), ("ISC-EHB L1/L2", "best"),
                                                    ("ISC", "glob")])])]
KIND = {"lit": ("#e3defa", "#6250d6", "review paper"), "best": ("#cfeee2", "#1baf7a", "measured moment or calibrated"),
        "local": ("#fbdccf", "#eb6834", "local network"), "glob": ("#cde2fb", "#2a78d6", "global catalogue or converted"),
        "hist": ("#e6e5df", "#8a897f", "historical")}

use_theme("slides")
fig, axs = plt.subplots(1, 3, figsize=(16, 5.4), gridspec_kw=dict(wspace=0.05, width_ratios=[3, 4, 4]))
bh, gap = 0.78, 0.2
for ax, (prop, cols) in zip(axs, RULES):
    ax.set_xlim(0, len(cols))
    ax.set_ylim(-5 * (bh + gap) - 0.2, 1.9)
    ax.axis("off")
    ax.text(0.02, 1.85, prop, fontsize=14, color="0.15", va="top")
    for i, (per, boxes) in enumerate(cols):
        ax.text(i + 0.5, 0.95, per, fontsize=8.8, color="0.4", ha="center", va="center", linespacing=1.1)
        for k, (lab, kind) in enumerate(boxes):
            fc, ec, _ = KIND[kind]
            y = 0.35 - (k + 1) * (bh + gap)
            ax.add_patch(FancyBboxPatch((i + 0.04, y), 0.92, bh, boxstyle="round,pad=0,rounding_size=0.06", fc=fc, ec=ec, lw=1.0))
            ax.text(i + 0.5, y + bh / 2, lab, fontsize=8.0, ha="center", va="center", color="0.15", linespacing=1.05)
h = [FancyBboxPatch((0, 0), 1, 1, fc=v[0], ec=v[1]) for v in KIND.values()]
fig.legend(h, [v[2] for v in KIND.values()], loc="lower center", ncol=5, fontsize=10, bbox_to_anchor=(0.5, -0.02))
OUT.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT / "catalog_rules.png", dpi=200, bbox_inches="tight", pad_inches=0.08, facecolor="white")
