# s02_fault_buffers.py
# Down-dip-aware fault buffer polygons. Inside any buffer the smoothed-cell
# Mmax is capped at C.CAP_MAG (s03), so the fault model owns M >= CAP_MAG
# there. Buffer = surface projection of the dipping plane + margin.

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
import shapely.affinity
from shapely.geometry import MultiLineString
from shapely.ops import unary_union, transform
from pyproj import Transformer, CRS

import ssm_config as C


@dataclass
class BufferConfig:
    faults_shp: Path = C.FAULTS_SHP
    margin_km: float = C.BUFFER_MARGIN_KM
    cap_mag: float = C.CAP_MAG
    fallback_dip: float = 60.0
    fallback_usd: float = 0.0
    fallback_lsd: float = 20.0
    per_fault_geojson: Path = C.BUFFERS_GEOJSON
    union_geojson: Path = C.BUFFERS_UNION

    def __post_init__(self):
        for f in ("faults_shp", "per_fault_geojson", "union_geojson"):
            setattr(self, f, Path(getattr(self, f)))


# geometry helpers

def local_transformers(lon0: float, lat0: float):
    aeqd = CRS.from_proj4(f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=m")
    fwd = Transformer.from_crs("EPSG:4326", aeqd, always_xy=True).transform
    inv = Transformer.from_crs(aeqd, "EPSG:4326", always_xy=True).transform
    return fwd, inv


def downdip_width_km(dip: float, usd: float, lsd: float) -> float:
    """
    Horizontal extent (km) of the surface projection of the dipping plane:
    (lsd - usd) / tan(dip); 0 for vertical faults.
    """
    if dip >= 90.0:
        return 0.0
    return max(lsd - usd, 0.0) / math.tan(math.radians(dip))


def fault_polygon(trace, w_h_km: float, margin_km: float,
                  dip_dir: float | None = None):
    """
    Buffer polygon of one fault (WGS84). With dip_dir the down-dip projection
    is applied on that side only; without it the buffer is symmetric.
    """
    if isinstance(trace, MultiLineString):
        return unary_union([fault_polygon(g, w_h_km, margin_km, dip_dir)
                            for g in trace.geoms])
    c = trace.centroid
    fwd, inv = local_transformers(c.x, c.y)
    line_m = transform(fwd, trace)
    w, m = w_h_km * 1000.0, margin_km * 1000.0
    if dip_dir is None or w == 0.0:
        poly_m = line_m.buffer(w + m, cap_style="round")
    else:
        az = math.radians(dip_dir)
        shifted = shapely.affinity.translate(line_m, xoff=w * math.sin(az),
                                             yoff=w * math.cos(az))
        poly_m = MultiLineString([line_m, shifted]).convex_hull.buffer(
            m, cap_style="round")
    return transform(inv, poly_m)


CARDINAL_AZ = {"N": 0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5, "E": 90.0,
               "ESE": 112.5, "SE": 135.0, "SSE": 157.5, "S": 180.0,
               "SSW": 202.5, "SW": 225.0, "WSW": 247.5, "W": 270.0,
               "WNW": 292.5, "NW": 315.0, "NNW": 337.5}


def parse_dip_dir(v) -> float | None:
    """Azimuth from a number or a compass string ('S', 'NE'); None if absent."""
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
    gdf = gdf.set_crs("EPSG:4326") if gdf.crs is None else gdf.to_crs("EPSG:4326")

    def val(row, col, fb):
        v = row.get(col, None)
        return fb if v is None or not np.isfinite(v) or v <= 0 else float(v)

    gdf["dip_eff"] = [val(r, "dip", cfg.fallback_dip) for _, r in gdf.iterrows()]
    gdf["usd_eff"] = [max(0.0, float(r.get("upp_sd", cfg.fallback_usd) or 0.0))
                      for _, r in gdf.iterrows()]
    gdf["lsd_eff"] = [val(r, "low_sd", cfg.fallback_lsd) for _, r in gdf.iterrows()]
    return gdf


def build_buffers(cfg: BufferConfig | None = None,
                  margin_km: float | None = None) -> gpd.GeoDataFrame:
    """One buffer polygon per fault (WGS84), with the fields used downstream."""
    cfg = cfg or BufferConfig()
    margin = cfg.margin_km if margin_km is None else margin_km
    gdf = read_faults(cfg)
    has_dd = "dip_dir" in gdf.columns

    rows, n_sided = [], 0
    for _, r in gdf.iterrows():
        w_h = downdip_width_km(r["dip_eff"], r["usd_eff"], r["lsd_eff"])
        dd = parse_dip_dir(r.get("dip_dir")) if has_dd else None
        n_sided += dd is not None
        rows.append({"id_seg": r.get("id_seg"), "name": r.get("name"),
                     "dip": r["dip_eff"], "w_h_km": round(w_h, 2),
                     "margin_km": margin, "dip_dir_az": dd,
                     "sided": dd is not None,
                     "geometry": fault_polygon(r.geometry, w_h, margin, dd)})
    out = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    print(f"[build_buffers] {len(out)} polygons, margin={margin:.1f} km, "
          f"sided={n_sided}, symmetric={len(out) - n_sided}")
    return out


def write_buffers(gdf: gpd.GeoDataFrame, cfg: BufferConfig) -> tuple[Path, Path]:
    cfg.per_fault_geojson.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(cfg.per_fault_geojson, driver="GeoJSON")
    union = unary_union(gdf.geometry)
    gpd.GeoDataFrame({"cap_mag": [cfg.cap_mag]}, geometry=[union],
                     crs="EPSG:4326").to_file(cfg.union_geojson, driver="GeoJSON")
    print(f"[write_buffers] wrote {cfg.per_fault_geojson.resolve()}")
    print(f"[write_buffers] wrote {cfg.union_geojson.resolve()}")
    return cfg.per_fault_geojson, cfg.union_geojson


def load_union(path: Path):
    return unary_union(gpd.read_file(path).geometry)


def cell_mask(lons: np.ndarray, lats: np.ndarray, union) -> np.ndarray:
    """True where the point falls inside the (prepared) polygon/union."""
    shapely.prepare(union)
    return shapely.contains_xy(union, np.asarray(lons, float),
                               np.asarray(lats, float))


def margin_sensitivity(ssm_csv: Path, cfg: BufferConfig,
                       margins=(0.0, 5.0, 10.0, 15.0, 20.0),
                       mag_from: float | None = None) -> pd.DataFrame:
    """Background N(M>=mag_from) that the cap would remove, vs buffer margin."""
    mag_from = C.CAP_MAG if mag_from is None else mag_from
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
                     "removed_N": removed, "fraction_of_total": removed / n_tot})
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    return out


def main():
    # 1) one buffer polygon per fault: surface projection of the dipping
    #    plane (sided when dip_dir is known) plus C.BUFFER_MARGIN_KM
    cfg = BufferConfig()
    gdf = build_buffers(cfg)

    # 2) write per-fault polygons (QGIS / later attribution) and the dissolved
    #    union that s03 uses to decide which cells get capped
    write_buffers(gdf, cfg)

    # 3) how much background rate the cap will remove as a function of the
    #    margin: if this keeps growing, the margin needs a defended value
    if C.SSM_GRID.exists():
        print("\n[main] margin sensitivity (needs s01 output):")
        margin_sensitivity(C.SSM_GRID, cfg)


if __name__ == "__main__":
    main()
