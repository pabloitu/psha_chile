# fault_buffers.py
# Down-dip-aware fault buffer polygons for capping the smoothed crustal model.
# Inside any buffer, the smoothed-cell Mmax is capped at CAP_MAG (fault handoff).

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
import shapely.affinity
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union, transform
from pyproj import Transformer, CRS


@dataclass
class BufferConfig:
    faults_shp: Path = Path("../data/active_faults/crustal_faults_chile_updated.shp")
    margin_km: float = 10.0
    cap_mag: float = 6.0
    fallback_dip: float = 60.0
    fallback_usd: float = 0.0
    fallback_lsd: float = 20.0
    out_dir: Path = Path(".")
    per_fault_geojson: str = "fault_buffers.geojson"
    union_geojson: str = "fault_buffers_union.geojson"

    def __post_init__(self):
        self.faults_shp = Path(self.faults_shp)
        self.out_dir = Path(self.out_dir)


# geometry helpers

def local_transformers(lon0: float, lat0: float):
    aeqd = CRS.from_proj4(f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=m")
    fwd = Transformer.from_crs("EPSG:4326", aeqd, always_xy=True).transform
    inv = Transformer.from_crs(aeqd, "EPSG:4326", always_xy=True).transform
    return fwd, inv


def downdip_width_km(dip: float, usd: float, lsd: float) -> float:
    """
    Horizontal extent (km) of the surface projection of the dipping plane.

    Parameters
    ----------
    dip : float
        Dip angle in degrees (0 < dip <= 90).
    usd, lsd : float
        Upper / lower seismogenic depth in km.

    Returns
    -------
    float
        (lsd - usd) / tan(dip); 0 for vertical faults.
    """
    if dip >= 90.0:
        return 0.0
    return max(lsd - usd, 0.0) / math.tan(math.radians(dip))


def fault_polygon(trace, w_h_km: float, margin_km: float,
                  dip_dir: float | None = None):
    """
    Buffer polygon of one fault in WGS84.

    Symmetric by default (dip direction unknown from the shapefile): the trace
    is buffered by w_h + margin on both sides. If dip_dir (azimuth, degrees) is
    given, the down-dip projection is applied on that side only and the margin
    on both sides.
    """
    if isinstance(trace, MultiLineString):
        parts = [fault_polygon(g, w_h_km, margin_km, dip_dir) for g in trace.geoms]
        return unary_union(parts)

    c = trace.centroid
    fwd, inv = local_transformers(c.x, c.y)
    line_m = transform(fwd, trace)
    w = w_h_km * 1000.0
    m = margin_km * 1000.0

    if dip_dir is None or w == 0.0:
        poly_m = line_m.buffer(w + m, cap_style="round")
    else:
        az = math.radians(dip_dir)
        dx, dy = w * math.sin(az), w * math.cos(az)
        shifted = shapely.affinity.translate(line_m, xoff=dx, yoff=dy)
        hull = MultiLineString([line_m, shifted]).convex_hull
        poly_m = hull.buffer(m, cap_style="round")

    return transform(inv, poly_m)


# main builders

CARDINAL_AZ = {
    "N": 0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5,
    "E": 90.0, "ESE": 112.5, "SE": 135.0, "SSE": 157.5,
    "S": 180.0, "SSW": 202.5, "SW": 225.0, "WSW": 247.5,
    "W": 270.0, "WNW": 292.5, "NW": 315.0, "NNW": 337.5,
}


def parse_dip_dir(v) -> float | None:
    """Azimuth in degrees from a numeric value or a compass string ('S', 'NE');
    None if missing/unparseable (buffer falls back to symmetric)."""
    if v is None:
        return None
    if isinstance(v, (int, float, np.floating)):
        return float(v) % 360.0 if np.isfinite(v) else None
    s = str(v).strip().upper()
    if s in CARDINAL_AZ:
        return CARDINAL_AZ[s]
    try:
        return float(s) % 360.0
    except ValueError:
        return None

def read_faults(cfg: BufferConfig) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(cfg.faults_shp)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    def val(row, col, fb):
        v = row.get(col, None)
        return fb if v is None or not np.isfinite(v) or v <= 0 else float(v)

    dips, usds, lsds = [], [], []
    for _, r in gdf.iterrows():
        dips.append(val(r, "dip", cfg.fallback_dip))
        usds.append(max(0.0, float(r.get("upp_sd", cfg.fallback_usd) or 0.0)))
        lsds.append(val(r, "low_sd", cfg.fallback_lsd))
    gdf["dip_eff"], gdf["usd_eff"], gdf["lsd_eff"] = dips, usds, lsds
    return gdf


def build_buffers(cfg: BufferConfig | None = None,
                  margin_km: float | None = None) -> gpd.GeoDataFrame:
    """
    Build per-fault buffer polygons (WGS84).

    Returns
    -------
    GeoDataFrame
        One row per fault with fields id_seg, name, w_h_km, margin_km and the
        buffer polygon geometry. The dissolved union is available via
        `unary_union(gdf.geometry)`.
    """
    cfg = cfg or BufferConfig()
    margin = cfg.margin_km if margin_km is None else margin_km
    gdf = read_faults(cfg)
    has_dipdir = "dip_dir" in gdf.columns

    rows = []
    n_sided = 0
    for _, r in gdf.iterrows():
        w_h = downdip_width_km(r["dip_eff"], r["usd_eff"], r["lsd_eff"])
        dd = parse_dip_dir(r.get("dip_dir")) if has_dipdir else None
        n_sided += dd is not None
        poly = fault_polygon(r.geometry, w_h, margin, dd)
        rows.append({
            "id_seg": r.get("id_seg"),
            "name": r.get("name"),
            "dip": r["dip_eff"],
            "w_h_km": round(w_h, 2),
            "margin_km": margin,
            "dip_dir_az": dd,
            "sided": dd is not None,
            "geometry": poly,
        })
    out = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    print(f"[build_buffers] {len(out)} fault polygons, margin={margin:.1f} km, "
          f"sided={n_sided}, symmetric={len(out) - n_sided}")
    return out


def write_buffers(gdf: gpd.GeoDataFrame, cfg: BufferConfig) -> tuple[Path, Path]:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    p_faults = cfg.out_dir / cfg.per_fault_geojson
    p_union = cfg.out_dir / cfg.union_geojson
    gdf.to_file(p_faults, driver="GeoJSON")
    union = unary_union(gdf.geometry)
    gpd.GeoDataFrame({"cap_mag": [BufferConfig.cap_mag]}, geometry=[union],
                     crs="EPSG:4326").to_file(p_union, driver="GeoJSON")
    print(f"[write_buffers] wrote {p_faults.resolve()}")
    print(f"[write_buffers] wrote {p_union.resolve()}")
    return p_faults, p_union


def load_union(path: Path):
    return unary_union(gpd.read_file(path).geometry)


def cell_mask(lons: np.ndarray, lats: np.ndarray, union) -> np.ndarray:
    """Boolean mask: True where the cell center falls inside the buffer union."""
    shapely.prepare(union)
    return shapely.contains_xy(union, np.asarray(lons, float), np.asarray(lats, float))


def margin_sensitivity(ssm_csv: Path, cfg: BufferConfig,
                       margins=(0.0, 5.0, 10.0, 15.0, 20.0),
                       mag_from: float = 6.0) -> pd.DataFrame:
    """
    Background N(M>=mag_from) removed by the cap as a function of buffer margin.
    """
    df = pd.read_csv(ssm_csv)
    cols = [c for c in df.columns if c.startswith("rate_M")
            and float(c.split("_M")[1].split("_")[0]) >= mag_from - 1e-6]
    n_tot = df[cols].to_numpy().sum()

    rows = []
    for m in margins:
        union = unary_union(build_buffers(cfg, margin_km=m).geometry)
        inside = cell_mask(df["lon"].to_numpy(), df["lat"].to_numpy(), union)
        removed = df.loc[inside, cols].to_numpy().sum()
        rows.append({"margin_km": m, "n_cells_inside": int(inside.sum()),
                     "removed_N_ge_%.1f" % mag_from: removed,
                     "fraction_of_total": removed / n_tot})
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    return out


def main():
    cfg = BufferConfig()
    gdf = build_buffers(cfg)
    write_buffers(gdf, cfg)


if __name__ == "__main__":
    main()