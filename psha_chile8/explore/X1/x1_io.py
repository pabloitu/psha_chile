"""Shared inputs of the X1 exploration: frozen source tables, geometry (Slab2, trench, coast, arc), regions."""
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parent
SRC = ROOT / "catalog" / "sources"
DATE = "2026-11-10"
CACHE = HERE / "cache"
FIG = HERE / "figs"
TAB = HERE / "tables"
for d in (CACHE, FIG, TAB):
    d.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT))
import palette  # noqa: E402

SOURCES = ["isc", "iscgem", "iscehb", "csn_isc", "comcat", "gcmt", "centennial", "potin", "csn"]
NAME = {"isc": "ISC Bulletin", "iscgem": "ISC-GEM", "iscehb": "ISC-EHB", "csn_isc": "CSN in ISC", "comcat": "ComCat",
        "gcmt": "GCMT", "centennial": "Centennial", "potin": "Potin et al.", "csn": "CSN web", "cabello": "Cabello et al.",
        "rm2018": "Ruiz & Madariaga"}
PERIODS = [(-1e9, 1964, "< 1964"), (1964, 1976, "1964–1975"), (1976, 2000, "1976–1999"), (2000, 2015, "2000–2014"),
           (2015, 1e9, "2015 on")]
MBANDS = [(-9, 5, "M < 5"), (5, 6, "5–6"), (6, 7, "6–7"), (7, 99, "M ≥ 7")]
KM = 111.195
T0 = np.datetime64("1900-01-01T00:00:00", "ms")


def tsec(s):
    """Seconds since 1900 from ISO strings, partial dates allowed (numpy, so years before 1677 work)."""
    s = pd.Series(s, dtype=object).fillna("NaT").astype(str).str.replace("Z", "", regex=False)
    out = np.full(len(s), np.nan)
    for i, v in enumerate(s.to_numpy()):
        try:
            out[i] = (np.datetime64(v, "ms") - T0) / np.timedelta64(1, "s")
        except ValueError:
            pass
    return out


def tsec_fast(s):
    t = pd.to_datetime(pd.Series(s), format="ISO8601", errors="coerce", utc=True).dt.tz_localize(None)
    v = (t - pd.Timestamp("1900-01-01")).dt.total_seconds().to_numpy()
    bad = np.isnan(v) & pd.Series(s).notna().to_numpy()
    if bad.any():
        v[bad] = tsec(pd.Series(s)[bad])
    return v


def year(t):
    return 1900 + t / (365.2425 * 86400)


def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def label(x, bins):
    out = np.full(len(x), None, dtype=object)
    for lo, hi, nm in bins:
        out[(x >= lo) & (x < hi)] = nm
    return out


def events(src, all_origins=False):
    f = SRC / f"{src}_{DATE}_events.csv"
    e = pd.read_csv(f, low_memory=False, dtype={"src_id": str, "origin_id": str})
    if not all_origins:
        if src == "gcmt":
            e = e[~e.prime.astype(bool)]
        else:
            e = e[e.prime.astype(bool)]
        e = e.drop_duplicates("src_id")
    e = e.reset_index(drop=True)
    e["t"] = tsec_fast(e.time)
    return e


def mags(src):
    m = pd.read_csv(SRC / f"{src}_{DATE}_mags.csv", low_memory=False, dtype={"src_id": str})
    m["mag"] = pd.to_numeric(m.mag, errors="coerce")
    return m


def save(df, name):
    df.to_csv(CACHE / f"{name}.csv.gz", index=False)


def load(name, **kw):
    f = CACHE / f"{name}.csv.gz"
    return pd.read_csv(f, low_memory=False, **kw) if f.exists() else None


# geometry
@lru_cache(None)
def slab():
    from scipy.interpolate import RegularGridInterpolator
    g = {}
    for k in ("dep", "thk", "dip"):
        a = pd.read_csv(REPO / f"data/slab_2.0/sam_slab2_{k}_02.23.18.xyz", header=None, names=["x", "y", "z"])
        xs, ys = np.unique(a.x), np.unique(a.y)
        z = a.pivot(index="y", columns="x", values="z").reindex(index=ys, columns=xs).to_numpy()
        g[k] = RegularGridInterpolator((ys, xs), z, bounds_error=False, fill_value=np.nan)
    return g


def slab_at(lon, lat):
    """Slab2 top depth (km, positive down), thickness (km) and dip (deg) at the epicentres."""
    g = slab()
    p = np.c_[lat, np.mod(lon, 360)]
    return -g["dep"](p), g["thk"](p), g["dip"](p)


@lru_cache(None)
def shapes():
    """Trench, land and arc geometries (lists of shapely geometries, lon / lat)."""
    import cartopy.io.shapereader as shp
    from shapely.geometry import box
    bb = box(-82, -60, -58, -14)
    rd = lambda f: [g for g in shp.Reader(str(f)).geometries()]  # noqa: E731
    tr = rd(REPO / "data/shapefiles/sam_nazca_trench.shp")
    land = [g.intersection(bb) for g in rd(Path.home() / ".local/share/cartopy/shapefiles/natural_earth/physical/"
                                           "ne_10m_land.shp") if g.intersects(bb)]
    arc = rd(REPO / "data/intraarc.shp")
    return tr, land, arc


def utm(lon, lat):
    from pyproj import Transformer
    tf = Transformer.from_crs(4326, 32719, always_xy=True)
    return tf.transform(lon, lat)


def setting(lon, lat):
    """Trench distance (km, + landward), and a setting label: outer rise, offshore, coast, forearc, arc, backarc."""
    import shapely
    import shapely.ops
    tr, land, arc = shapes()
    x, y = utm(np.asarray(lon, float), np.asarray(lat, float))
    pts = shapely.points(x, y)
    tl = shapely.ops.transform(lambda a, b: utm(np.asarray(a), np.asarray(b)), shapely.union_all(tr))
    dt = shapely.distance(pts, tl) / 1e3
    # landward side: east of the trench line at the same northing
    tc = np.array(shapely.get_coordinates(tl))
    o = np.argsort(tc[:, 1])
    xt = np.interp(y, tc[o, 1], tc[o, 0])
    sgn = np.where(x >= xt, 1.0, -1.0)
    lg = shapely.ops.transform(lambda a, b: utm(np.asarray(a), np.asarray(b)), shapely.union_all(land))
    ag = shapely.ops.transform(lambda a, b: utm(np.asarray(a), np.asarray(b)), shapely.union_all(arc))
    shapely.prepare(lg)
    shapely.prepare(ag)
    onl = shapely.contains(lg, pts)
    dc = shapely.distance(pts, shapely.boundary(lg)) / 1e3
    ina = shapely.contains(ag, pts)
    # east of the arc: further east than the arc polygon at that northing
    ac = np.array(shapely.get_coordinates(shapely.boundary(ag)))
    yb = np.round(ac[:, 1] / 2e4)
    east = pd.Series(ac[:, 0]).groupby(yb).max()
    xe = np.interp(y, east.index.to_numpy() * 2e4, east.to_numpy(), left=np.nan, right=np.nan)
    lab = np.where(sgn < 0, "outer rise", np.where(~onl & (dc > 20), "offshore",
                   np.where(dc <= 20, "coast", np.where(ina, "arc", np.where(x > xe, "backarc", "forearc")))))
    lab = np.where(ina & onl, "arc", lab)
    return sgn * dt, lab


def latband(lat, w=2.0):
    lo = np.floor(np.asarray(lat) / w) * w
    return np.array([f"{-l - w:.0f}–{-l:.0f}°S" if np.isfinite(l) else None for l in lo], dtype=object)


def fig_setup():
    import matplotlib
    matplotlib.use("Agg")
    palette.apply()
    import matplotlib.pyplot as plt
    return plt


def savefig(fig, name, caption=None):
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    if caption:
        with open(HERE / "cache" / "figlog.tsv", "a") as f:
            f.write(f"{name}.png\t{caption}\n")


def tstr(t):
    """ISO strings from seconds since 1900 (works before 1677)."""
    t = np.atleast_1d(np.asarray(t, float))
    out = np.full(len(t), "", dtype=object)
    k = np.isfinite(t)
    out[k] = np.datetime_as_string(T0 + (t[k] * 1000).astype("int64").astype("timedelta64[ms]"), unit="s")
    return out
