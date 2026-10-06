# Trench-normal cross-sections of the classified catalog with the Slab2 top and
# bottom (top + thickness) surfaces. Each section passes through a point, runs
# down-dip (Slab2 strike near the trench + 90), and projects the events within
# HALF_WIDTH km along strike onto it.
# Outputs: outputs/intraslab/ref/check/sections/
#   section_<name>.png   depth vs distance along the section, events by class
#   sections_map.png     the section lines and swaths on a map
#   sections.csv         projected events: distance, offset, depth, slab top, thickness

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cat, cfg, smooth
from intraslab import config
from intraslab.s03_sources import depths
from hazard import config as hc

# settings
SECTIONS = {k: hc.CITIES[k] for k in ("iquique", "antofagasta", "valparaiso", "santiago_centro", "concepcion")
            if k in hc.CITIES}
HALF_WIDTH = 25.0                   # km along strike on each side of the section
S_RANGE = (-250.0, 650.0)           # km along the section, negative = trenchward of the point
Z_MAX = 300.0
MMIN = 4.0
STRIKE_DEPTH = 40.0                 # strike taken from Slab2 nodes shallower than this, near the trench
STRIKE_DLAT = 0.3
MAXDIST_KM = 15.0                   # slab node within this distance, as in the classifier
KM = 111.2
COLORS = {"slab_interface": "#4c72b0", "intra_slab": "#dd8452", "slab_deep": "#c44e52", "deep_nest": "#8172b3",
          "forearc": "#55a868", "intraarc_shallow": "#937860", "intraarc_deep": "#da8bc3", "backarc": "#8c8c8c",
          "outer_rise": "#ccb974", "deep_unknown": "k", "unclassified": "0.75"}


def downdip(lat, strike_path):
    """Down-dip azimuth (deg) at a latitude: circular mean of the Slab2 strike near the trench + 90."""
    s = pd.read_csv(strike_path, header=None, names=["lon", "lat", "val"]).dropna()
    d = pd.read_csv(config.SLAB_XYZ, header=None, names=["lon", "lat", "dep"]).dropna()
    s = s.merge(d, on=["lon", "lat"])
    s = s[(np.abs(s["lat"] - lat) <= STRIKE_DLAT) & (-s["dep"] <= STRIKE_DEPTH)]
    a = np.radians(s["val"].to_numpy())
    return (np.degrees(np.arctan2(np.sin(a).mean(), np.cos(a).mean())) + 90.0) % 360.0


def frame(lon0, lat0, az):
    """Functions (lon, lat) -> (s, t) km along and across the section, and s -> (lon, lat)."""
    ux, uy = np.sin(np.radians(az)), np.cos(np.radians(az))
    kx = KM * np.cos(np.radians(lat0))

    def st(lon, lat):
        x, y = (np.asarray(lon) - lon0) * kx, (np.asarray(lat) - lat0) * KM
        return x * ux + y * uy, -x * uy + y * ux

    def ll(s, t=0.0):
        return lon0 + (s * ux - t * uy) / kx, lat0 + (s * uy + t * ux) / KM

    return st, ll


def surface(ll, s, t=0.0):
    """Slab2 top and thickness along a line; NaN where no node is within MAXDIST_KM."""
    lon, lat = ll(s, t)
    top, d = smooth.slab_top(lon, lat, config.SLAB_XYZ)
    thk = smooth.slab_node(lon, lat, config.SLAB_THK)[0]
    top = np.where(d <= MAXDIST_KM, top, np.nan)
    return top, np.where(np.isfinite(top), thk, np.nan)


def main():
    c = cfg.load(config)
    od = c.OUT / "check" / "sections"
    od.mkdir(parents=True, exist_ok=True)
    ev = cat.load(c.CAT, bbox=c.BBOX)
    ev = ev[ev["mag"] >= MMIN].reset_index(drop=True)
    cls = ev["class"].fillna("unclassified") if "class" in ev else pd.Series("unclassified", index=ev.index)
    s_line = np.arange(S_RANGE[0], S_RANGE[1] + 1, 5.0)
    out, lines = [], {}
    for name, (lon0, lat0) in SECTIONS.items():
        az = downdip(lat0, c.SLAB_STR)
        st, ll = frame(lon0, lat0, az)
        s, t = st(ev["longitude"], ev["latitude"])
        m = (np.abs(t) <= HALF_WIDTH) & (s >= S_RANGE[0]) & (s <= S_RANGE[1])
        g = ev[m].assign(s=s[m], t=t[m], cls=cls[m])
        top, _ = smooth.slab_top(g["longitude"].to_numpy(), g["latitude"].to_numpy(), c.SLAB_XYZ)
        g["top"] = top
        g["thk"] = smooth.slab_node(g["longitude"].to_numpy(), g["latitude"].to_numpy(), c.SLAB_THK)[0]
        g["dz"] = g["depth"] - g["top"]
        out.append(g.assign(section=name, azimuth=az))
        lines[name] = (ll(np.array(S_RANGE)), az)

        f, ax = plt.subplots(figsize=(11, 4.6))
        for k in [k for k in COLORS if k in set(g["cls"])] + [k for k in set(g["cls"]) if k not in COLORS]:
            x = g[g["cls"] == k]
            ax.scatter(x["s"], x["depth"], s=2 + 3 * (x["mag"] - MMIN) ** 2, color=COLORS.get(k, "0.5"),
                       alpha=0.6, lw=0, label=f"{k} {len(x)}")
        for tt, ls, lw in ((0.0, "-", 1.4), (-HALF_WIDTH, ":", 0.8), (HALF_WIDTH, ":", 0.8)):
            top, thk = surface(ll, s_line, tt)
            ax.plot(s_line, top, "k", ls=ls, lw=lw, label="Slab2 top" if tt == 0 else None)
            ax.plot(s_line, top + thk, "0.4", ls=ls, lw=lw, label="top + thickness" if tt == 0 else None)
        top, thk = surface(ll, s_line)
        lo, la = ll(s_line)
        ok = np.isfinite(top)
        hz, _, lz, _ = depths(c, pd.DataFrame({"lon": lo[ok], "lat": la[ok], "slab_km": top[ok]}))
        ax.plot(s_line[ok], hz, color="#c44e52", lw=1.4, ls="--", label="model hypocentre")
        ax.plot(s_line[ok], lz, color="#c44e52", lw=1.0, ls="-.", label="model lower depth")
        ax.axhline(0, color="k", lw=0.6)
        ax.plot([0], [0], "k^", ms=9, clip_on=False)
        ax.annotate(name.replace("_", " "), (0, 0), fontsize=8, xytext=(5, 4), textcoords="offset points")
        ax.set_xlim(*S_RANGE)
        ax.set_ylim(Z_MAX, -5)
        ax.set_aspect("equal")
        ax.set_xlabel(f"distance along section km, azimuth {az:.0f}")
        ax.set_ylabel("depth km")
        ax.set_title(f"{name.replace('_', ' ')}: events M>={MMIN:g} within {HALF_WIDTH:g} km of the section; "
                     "dotted = Slab2 at the swath edges", fontsize=9)
        ax.legend(fontsize=6, ncol=2, loc="lower left", markerscale=1.5)
        ax.grid(alpha=0.3)
        f.tight_layout()
        f.savefig(od / f"section_{name}.png", dpi=300)
        plt.close(f)

    t = pd.concat(out, ignore_index=True)
    t[["section", "azimuth", "s", "t", "longitude", "latitude", "depth", "mag", "cls", "top", "thk", "dz"]].to_csv(
        od / "sections.csv", index=False)

    f, ax = plt.subplots(figsize=(5, 8))
    ax.scatter(ev["longitude"], ev["latitude"], s=0.5, color="0.7")
    for name, ((lo, la), az) in lines.items():
        ax.plot(lo, la, "k", lw=1.2)
        _, ll = frame(*SECTIONS[name], az)
        for tt in (-HALF_WIDTH, HALF_WIDTH):
            a, b = ll(np.array(S_RANGE), tt)
            ax.plot(a, b, "k", lw=0.5, ls=":")
        ax.plot(*SECTIONS[name], "k^", ms=6)
        ax.annotate(name.replace("_", " "), SECTIONS[name], fontsize=7, xytext=(5, 3), textcoords="offset points")
    ax.set_aspect(1 / np.cos(np.radians(-30)))
    ax.set_xlabel("lon")
    ax.set_ylabel("lat")
    ax.set_title(f"sections and {2 * HALF_WIDTH:g} km swaths", fontsize=9)
    f.tight_layout()
    f.savefig(od / "sections_map.png", dpi=300)
    plt.close(f)
    print(t.groupby(["section", "cls"]).size().unstack(fill_value=0).to_string())
    print(f"\nwrote {od}")


if __name__ == "__main__":
    main()