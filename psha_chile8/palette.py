# One palette and one figure style for the catalog, fit and hazard figures of psha_chile8.
# Started from cat_handler_2/palette.py; class colours and display names come back with
# the new class names (A7). Import from here; do not restate colours in a figure script.

# magnitude bands of the catalog profiles, light to dark
BAND = {"M < 4": "#d9d9d9", "4–5": "#9ecae1", "5–6": "#4292c6", "6–7": "#08519c", "M ≥ 7": "#e6550d",
        "no magnitude": "#ffffff"}
# qualitative series (sources, magnitude types)
SERIES = ["#2166ac", "#e0641e", "#2e8b57", "#a50f15", "#c9a227", "#6a3d9a", "#4393c3", "#8c510a", "#f0505a",
          "#7f7f7f", "#1b9e77", "#e7298a"]
INK = "0.15"

RC = {"font.family": ["Ubuntu", "DejaVu Sans"], "font.size": 12, "axes.titlesize": 13, "axes.titlelocation": "left",
      "axes.titleweight": "medium", "axes.titlepad": 10, "axes.labelsize": 12, "axes.spines.top": False,
      "axes.spines.right": False, "axes.linewidth": 0.8, "xtick.labelsize": 11, "ytick.labelsize": 11,
      "xtick.direction": "out", "ytick.direction": "out", "legend.fontsize": 10, "legend.frameon": False,
      "legend.handletextpad": 0.6, "legend.labelspacing": 0.5, "figure.dpi": 100, "savefig.facecolor": "white",
      "axes.edgecolor": "0.25", "xtick.color": "0.25", "ytick.color": "0.25", "axes.labelcolor": INK,
      "text.color": INK}


def apply(size=None):
    """Set the shared rcParams; size scales the fonts (14 for a single-panel slide)."""
    import logging
    import matplotlib
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    rc = dict(RC)
    if size:
        for k in ("font.size", "axes.titlesize", "axes.labelsize", "legend.fontsize", "xtick.labelsize",
                  "ytick.labelsize"):
            rc[k] = size + (1 if k == "axes.titlesize" else 0) - (
                2 if k in ("legend.fontsize", "xtick.labelsize", "ytick.labelsize") else 0)
    matplotlib.rcParams.update(rc)
