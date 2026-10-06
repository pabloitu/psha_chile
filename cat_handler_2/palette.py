# One palette and one set of display names for every figure of the catalog,
# forecast and hazard work. Interface blues, in-slab reds (light above a 50 km
# slab top, dark below, brown for the deep nest), crustal oranges, excluded
# greys. Import from here; do not restate colours in a figure script.

CLASS = {
    "slab_interface": "#2166ac", "patagonia_interface": "#4393c3",
    "intra_slab": "#f0505a", "slab_deep": "#a50f15", "deep_nest": "#6b3d1a",
    "forearc": "#ffb000", "intraarc": "#2e8b57", "backarc": "#c9a227", "patagonia_crustal": "#8c510a",
    "outer_rise": "#a6a6a6", "deep_unknown": "#4d4d4d", "unclassified": "#c8c8c8", "unresolved": "#7f7f7f",
}
FAMILY = {"interface": "#2166ac", "in-slab": "#a50f15", "crustal": "#e0641e", "excluded": "#7f7f7f"}
NAME = {
    "slab_interface": "interface", "patagonia_interface": "Antarctic interface",
    "intra_slab": "in-slab (slab top < 50 km)", "slab_deep": "in-slab (slab top >= 50 km)", "deep_nest": "deep nest",
    "forearc": "forearc", "intraarc": "intra-arc", "backarc": "backarc", "patagonia_crustal": "Patagonia crustal",
    "outer_rise": "outer rise", "deep_unknown": "below the plate", "unclassified": "no slab model", "unresolved": "unresolved",
}
# drawing order (higher on top)
ZORDER = {"deep_unknown": 2, "unclassified": 2, "backarc": 3, "patagonia_crustal": 3, "outer_rise": 3, "intraarc": 3, "forearc": 3,
          "unresolved": 3, "deep_nest": 4, "slab_deep": 4, "intra_slab": 4, "patagonia_interface": 5, "slab_interface": 5}
DEPTH_STATUS = {"relocated_cabello": "#1f77b4", "relocated_potin": "#17becf", "free": "#2ca02c", "filled": "#98df8a",
                "fixed": "#ff7f0e", "missing": "#7f7f7f", "assigned": "#9467bd"}


# figure style shared by the slide figures: Ubuntu font (DejaVu Sans where it
# is not installed), open spines, left-aligned titles, frameless legends
RC = {"font.family": ["Ubuntu", "DejaVu Sans"], "font.size": 12, "axes.titlesize": 13, "axes.titlelocation": "left",
      "axes.titleweight": "medium", "axes.titlepad": 10, "axes.labelsize": 12, "axes.spines.top": False, "axes.spines.right": False,
      "axes.linewidth": 0.8, "xtick.labelsize": 11, "ytick.labelsize": 11, "xtick.direction": "out", "ytick.direction": "out",
      "legend.fontsize": 10, "legend.frameon": False, "legend.handletextpad": 0.6, "legend.labelspacing": 0.5,
      "figure.dpi": 100, "savefig.facecolor": "white", "axes.edgecolor": "0.25", "xtick.color": "0.25", "ytick.color": "0.25",
      "axes.labelcolor": "0.15", "text.color": "0.15"}


def apply(size=None):
    """Set the shared rcParams; size scales the fonts (14 for a single-panel slide)."""
    import logging
    import matplotlib
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    rc = dict(RC)
    if size:
        for k in ("font.size", "axes.titlesize", "axes.labelsize", "legend.fontsize", "xtick.labelsize", "ytick.labelsize"):
            rc[k] = size + (1 if k == "axes.titlesize" else 0) - (2 if k in ("legend.fontsize", "xtick.labelsize", "ytick.labelsize") else 0)
    matplotlib.rcParams.update(rc)
