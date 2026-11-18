"""Colour maps and categorical palettes for the figures.

`palettes.json` is copied from pituPLOTS (`src/pituplots/style/palettes.json`, 17 Nov 2026), with the source of
every map; pituPLOTS is not a dependency. Colour maps are registered with matplotlib as `pp.<name>` and
`pp.<name>_r`. Sequential and point maps run light (low values) to dark (high values), except `hawaii`.
"""
import json
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap, to_hex

from palette import BAND, CLASS, CLASS_COLOR, CLASS_NAME, FAMILY_COLOR, INK, SERIES, apply

DATA = json.loads(Path(__file__).with_name("palettes.json").read_text())
GROUPS = ("sequential", "points", "diverging", "rainbow")
OTHER = DATA["other"]
NODATA = "#9a9a9a"
# depth classes (km): crust, interface, intermediate depth and deep (pituPLOTS edges, with a last bin to 700 km)
DEPTH_EDGES = (0, 20, 40, 70, 120, 200, 300, 700)

for g in GROUPS:
    for k, v in DATA[g].items():
        cm = LinearSegmentedColormap.from_list(f"pp.{k}", v["colors"], N=256)
        cm.set_bad((0, 0, 0, 0))
        for c in (cm, cm.reversed()):
            if c.name not in matplotlib.colormaps:
                matplotlib.colormaps.register(c)


def colormaps(group=None):
    """Names of the registered colour maps (`pp.<name>`), all or one group."""
    return [f"pp.{k}" for g in GROUPS if group in (None, g) for k in DATA[g]]


def palette(name, n=None):
    """Hex colours of a categorical palette; more than it holds raises, since repeated colours break the legend."""
    c = list(DATA["categorical"][name]["colors"])
    if n is not None and n > len(c):
        raise ValueError(f"{name} has {len(c)} colours, {n} requested")
    return c[:n]


def source(name):
    """Where a colour map or palette comes from, for captions."""
    k = name.removeprefix("pp.").removesuffix("_r")
    return next(DATA[g][k]["source"] for g in (*GROUPS, "categorical") if k in DATA[g])


def depth_colors(cmap="pp.pt_sea", edges=DEPTH_EDGES):
    """One hex colour per depth class, sampled from the colour map at the class centres."""
    n = len(edges) - 1
    return [to_hex(c) for c in matplotlib.colormaps[cmap]((np.arange(n) + 0.5) / n)]


def depth_color(z, cmap="pp.pt_sea", edges=DEPTH_EDGES):
    """Hex colour of each depth (km); NODATA where the depth is unknown."""
    z = np.asarray(z, float)
    c = np.array(depth_colors(cmap, edges))
    k = np.clip(np.digitize(z, edges[1:-1]), 0, len(c) - 1)
    return np.where(np.isnan(z), NODATA, c[k])


def depth_norm(cmap="pp.pt_sea", edges=DEPTH_EDGES):
    """Discrete colour map and norm of the depth classes, for colour bars."""
    return matplotlib.colormaps[cmap].resampled(len(edges) - 1), BoundaryNorm(edges, len(edges) - 1)
