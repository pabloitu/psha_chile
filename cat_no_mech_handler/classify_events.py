# classify_catalogs.py (updated)
from __future__ import annotations

import os
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Iterable, List

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
from scipy.spatial import cKDTree

from cat_no_mech_handler import paths

# ---- Tunables ----
INTRA_ARC_SHALLOW_MAX = 40.0
DEEP_SLAB_TOL = 15.0
SUBDUCTION_CLASSIFY_MAX_SLAB_DEPTH = 50.0
INTERFACE_DEPTH_TOL = 11            # buffer for relocated or “no-error-info” cases
STRICT_INTERFACE_DEPTH_TOL = 15.0   # treat explicit 0 depth_error as poorly constrained
BACKARC_MAX_DEPTH = 70
SLAB_QUERY_MAXDIST_KM = 15.0
SLAB_DEPTH_IS_POSITIVE_DOWN = False

CONV_AZIMUTH_DEG = 78.0
NORM_CONE_DEG = 35.0
SLIP_CONE_DEG = 90.0

# Raw internal classes (used by the logic)
RAW_CLASSES: List[str] = [
    "intraarc_shallow",
    "intraarc_deep",
    "slab_interface",
    "intra_slab",
    "slab_deep",
    "outer_rise",
    "forearc",
    "backarc",
    "unclassified",
]

# Final classes we will actually use / write out
FINAL_CLASSES: List[str] = [
    "intraarc",        # merge of intraarc_shallow + intraarc_deep
    "slab_interface",
    "intra_slab",
    "slab_deep",
    "outer_rise",
    "forearc",
    "unclassified",    # includes backarc + any leftovers
]

SUBDUCTION_CLASSES = {"slab_interface", "intra_slab", "slab_deep", "forearc"}

# ---- Slab grid ----
@dataclass
class SlabGrid:
    tree: cKDTree
    lon: np.ndarray
    lat: np.ndarray
    depth: np.ndarray   # km, +down
    strike: np.ndarray  # deg
    dip: np.ndarray     # deg


def _lon0360_to_180(x: float) -> float:
    x = float(x)
    return x - 360.0 if x > 180.0 else x


def _read_xyz(p: str) -> pd.DataFrame:
    df = pd.read_csv(p, header=None, names=["lon", "lat", "val"])
    df["lon"] = df["lon"].astype(float).apply(_lon0360_to_180)
    df["lat"] = df["lat"].astype(float)
    return df


def load_slab_xyz(depth_path: str, strike_path: str, dip_path: str) -> SlabGrid:
    dep = _read_xyz(depth_path)
    st = _read_xyz(strike_path)
    di = _read_xyz(dip_path)

    if not SLAB_DEPTH_IS_POSITIVE_DOWN:
        dep["val"] = -dep["val"]

    df = dep.merge(st, on=["lon", "lat"], how="outer", suffixes=("_dep", "_st"))
    df = df.merge(di, on=["lon", "lat"], how="outer")
    df.rename(columns={"val": "val_dip"}, inplace=True)
    df = df.dropna(subset=["val_dep", "val_st", "val_dip"], how="any")

    lon = df["lon"].to_numpy(float)
    lat = df["lat"].to_numpy(float)
    depth = df["val_dep"].to_numpy(float)
    strike = (df["val_st"].to_numpy(float) % 360.0)
    dip = df["val_dip"].to_numpy(float)

    return SlabGrid(
        tree=cKDTree(np.c_[lon, lat]),
        lon=lon,
        lat=lat,
        depth=depth,
        strike=strike,
        dip=dip,
    )

# ---- Simple geo helpers ----
def _haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def query_slab(
    grid: SlabGrid, lon: float, lat: float, maxdist_km: float
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if np.isnan(lon) or np.isnan(lat):
        return (None, None, None)
    _, idx = grid.tree.query(np.array([lon, lat]), k=1)
    if idx is None:
        return (None, None, None)
    if _haversine_km(lon, lat, grid.lon[idx], grid.lat[idx]) > maxdist_km:
        return (None, None, None)
    return float(grid.depth[idx]), float(grid.strike[idx]), float(grid.dip[idx])


def load_union(path: str):
    if not os.path.exists(path):
        return None
    gdf = gpd.read_file(path).to_crs(epsg=4326)
    return unary_union(gdf.geometry)


def is_west_of_trench(lon: float, lat: float, trench_line) -> bool:
    if trench_line is None or np.isnan(lon) or np.isnan(lat):
        return False
    pt = Point(lon, lat)
    nearest = trench_line.interpolate(trench_line.project(pt))
    return float(lon) < float(nearest.x)


def is_east_of_polygon(lon: float, lat: float, polygon) -> bool:
    if polygon is None or np.isnan(lon) or np.isnan(lat):
        return False
    boundary = polygon.boundary
    pt = Point(lon, lat)
    nearest = boundary.interpolate(boundary.project(pt))
    return float(lon) > float(nearest.x)

# ---- Focal-mechanism cones (ENU-consistent) ----
def _deg2rad(x: float) -> float:
    return math.radians(float(x))


def _clamp(x: float) -> float:
    return max(-1.0, min(1.0, float(x)))


def _angle_between(a: np.ndarray, b: np.ndarray, oriented: bool = False) -> float:
    """Angle (deg) between vectors a and b. If oriented=False, uses |dot| (0..90 symmetry)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return float("nan")
    a = a / na
    b = b / nb
    dot = float(np.dot(a, b))
    if not oriented:
        dot = abs(dot)
    return math.degrees(math.acos(_clamp(dot)))


def _strike_dip_axes(
    strike_deg: float, dip_deg: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    ENU coordinates: X=East, Y=North, Z=Up.
    strike: azimuth clockwise from North (0..360).
    dip: angle from horizontal (0..90), dipping to right of strike.

    Returns:
      u_s : unit along-strike (horizontal, ENU)
      u_d : unit down-dip   (tilted downward; negative Up component)
      n   : unit plane normal, chosen upward (positive Up where possible)
    """
    th = _deg2rad(strike_deg)
    di = _deg2rad(dip_deg)

    # Along-strike: horizontal direction (east, north, up)
    u_s = np.array([math.sin(th), math.cos(th), 0.0], dtype=float)

    # Down-dip: strike+90° direction in map, tilted down by dip
    u_d = np.array(
        [
            math.cos(th) * math.cos(di),   # East
            -math.sin(th) * math.cos(di),  # North
            -math.sin(di),                 # Up (negative = downward)
        ],
        dtype=float,
    )

    # Upward-pointing plane normal (right-hand: u_d × u_s)
    n = np.cross(u_d, u_s)

    def _unit(v):
        nv = np.linalg.norm(v)
        return v / nv if nv > 0 else v

    u_s = _unit(u_s)
    u_d = _unit(u_d)
    n = _unit(n)
    return u_s, u_d, n


def _plane_normal(strike_deg: float, dip_deg: float) -> np.ndarray:
    _, _, n = _strike_dip_axes(strike_deg, dip_deg)
    return n


def _slip_vector(strike_deg: float, dip_deg: float, rake_deg: float) -> np.ndarray:
    """Unit slip vector in ENU; rake measured in the fault plane from strike toward down-dip."""
    u_s, u_d, _ = _strike_dip_axes(strike_deg, dip_deg)
    ra = _deg2rad(rake_deg)
    v = math.cos(ra) * u_s + math.sin(ra) * u_d
    nv = np.linalg.norm(v)
    return v / nv if nv > 0 else v


def _expected_slip_on_plane(
    strike_deg: float, dip_deg: float, conv_az_deg: float
) -> np.ndarray | None:
    """
    Project far-field convergence azimuth (horizontal) onto the fault plane.
    conv_az_deg: azimuth clockwise from North.
    """
    az = _deg2rad(conv_az_deg)
    v_conv = np.array([math.sin(az), math.cos(az), 0.0], dtype=float)  # ENU
    n = _plane_normal(strike_deg, dip_deg)
    v_proj = v_conv - np.dot(v_conv, n) * n
    nv = np.linalg.norm(v_proj)
    if nv < 1e-12:
        return None
    return v_proj / nv


def _geom_cone_ok(
    strike: float,
    dip: float,
    slab_strike: float,
    slab_dip: float,
    norm_cone_deg: float,
) -> bool:
    """Normal-vs-normal cone test (unoriented, i.e., 0..90 symmetry)."""
    if any(pd.isna(v) for v in (strike, dip, slab_strike, slab_dip)):
        return False
    n_ev = _plane_normal(strike, dip)
    n_sl = _plane_normal(slab_strike, slab_dip)
    ang = _angle_between(n_ev, n_sl, oriented=False)
    return ang <= float(norm_cone_deg)


def _slip_cone_ok(
    strike: float,
    dip: float,
    rake: float,
    conv_az_deg: float,
    slip_cone_deg: float,
) -> bool:
    """Slip-vs-convergence (projected) cone test (oriented: do not abs(dot))."""
    s_obs = _slip_vector(strike, dip, rake)
    s_exp = _expected_slip_on_plane(strike, dip, conv_az_deg)
    if s_exp is None:
        return False
    ang = _angle_between(s_obs, s_exp, oriented=True)
    return ang <= float(slip_cone_deg)


def interface_mech_ok_cone(
    row: pd.Series,
    slab_strike: float,
    slab_dip: float,
    conv_az_deg: float,
    norm_cone_deg: float,
    slip_cone_deg: float,
    id_: str | None = None,
) -> bool:
    """True if EITHER nodal plane passes the normal-cone AND slip-cone tests."""
    s1, d1, r1 = row.get("strike1"), row.get("dip1"), row.get("rake1")
    s2, d2, r2 = row.get("strike2"), row.get("dip2"), row.get("rake2")

    ok = False
    if all(v is not None and not pd.isna(v) for v in (s1, d1, r1)):
        ok |= _geom_cone_ok(s1, d1, slab_strike, slab_dip, norm_cone_deg) and _slip_cone_ok(
            s1, d1, r1, conv_az_deg, slip_cone_deg
        )

    if all(v is not None and not pd.isna(v) for v in (s2, d2, r2)):
        ok |= _geom_cone_ok(s2, d2, slab_strike, slab_dip, norm_cone_deg) and _slip_cone_ok(
            s2, d2, r2, conv_az_deg, slip_cone_deg
        )

    return bool(ok)


def _has_mechanism(row: pd.Series) -> bool:
    """Return True if at least one full nodal plane is present."""
    s1, d1, r1 = row.get("strike1"), row.get("dip1"), row.get("rake1")
    s2, d2, r2 = row.get("strike2"), row.get("dip2"), row.get("rake2")

    if all(v is not None and not pd.isna(v) for v in (s1, d1, r1)):
        return True
    if all(v is not None and not pd.isna(v) for v in (s2, d2, r2)):
        return True
    return False

# ---- Depth-based logic helpers ----
def _is_relocated(row: pd.Series) -> bool:
    for c in ("lon_error", "lat_error", "depth_error"):
        v = row.get(c)
        if isinstance(v, str) and v.strip().lower() == "relocated":
            return True
    return False


def _numeric_errors(row: pd.Series) -> tuple[float, float, float]:
    # Preserve strings like "relocated"; return NaN for non-numeric
    le = pd.to_numeric(pd.Series([row.get("lon_error")]), errors="coerce").iloc[0]
    la = pd.to_numeric(pd.Series([row.get("lat_error")]), errors="coerce").iloc[0]
    de = pd.to_numeric(pd.Series([row.get("depth_error")]), errors="coerce").iloc[0]
    return (
        float(le) if pd.notna(le) else np.nan,
        float(la) if pd.notna(la) else np.nan,
        float(de) if pd.notna(de) else np.nan,
    )


def _ellipse_mask(
    lon_nodes: np.ndarray,
    lat_nodes: np.ndarray,
    lon0: float,
    lat0: float,
    lon_err: float,
    lat_err: float,
) -> np.ndarray:
    if not (np.isfinite(lon_err) and np.isfinite(lat_err)) or (
        lon_err <= 0 and lat_err <= 0
    ):
        return np.zeros_like(lon_nodes, dtype=bool)
    dx = (lon_nodes - lon0) / max(lon_err, 1e-12)
    dy = (lat_nodes - lat0) / max(lat_err, 1e-12)
    return (dx * dx + dy * dy) <= 1.0

# ---- Row classification (depth-first, then kinematics if mech exists) ----
def classify_row(row: pd.Series, intra_poly, trench_line, slab: SlabGrid) -> tuple[str, float | None]:
    """
    Return (raw_class, sub_depth), where:
      - raw_class is one of RAW_CLASSES
      - sub_depth is the slab depth at the projected location (or NaN if not used)
    """
    lon = pd.to_numeric(pd.Series([row.get("longitude")]), errors="coerce").iloc[0]
    lat = pd.to_numeric(pd.Series([row.get("latitude")]), errors="coerce").iloc[0]
    dep = pd.to_numeric(pd.Series([row.get("depth")]), errors="coerce").iloc[0]

    lon = float(lon) if pd.notna(lon) else np.nan
    lat = float(lat) if pd.notna(lat) else np.nan
    dep = float(dep) if pd.notna(dep) else np.nan

    slab_depth, slab_strike, slab_dip = query_slab(slab, lon, lat, SLAB_QUERY_MAXDIST_KM)

    # Intra-arc polygon domain
    in_intra = (
        intra_poly is not None
        and np.isfinite(lon)
        and np.isfinite(lat)
        and intra_poly.contains(Point(lon, lat))
    )

    # ---- Intra-arc domain (independent of mechanisms) ----
    if in_intra and np.isfinite(dep):
        if slab_depth is None:
            if dep <= INTRA_ARC_SHALLOW_MAX:
                return "intraarc_shallow", np.nan
            if dep <= 90.0:
                return "intraarc_deep", np.nan
            return "slab_deep", np.nan
        else:
            if dep >= slab_depth - DEEP_SLAB_TOL:
                return "slab_deep", slab_depth
            if dep <= INTRA_ARC_SHALLOW_MAX:
                return "intraarc_shallow", np.nan
            return "intraarc_deep", np.nan

    # Outer rise / backarc
    if is_west_of_trench(lon, lat, trench_line):
        return "outer_rise", np.nan

    if (not in_intra) and is_east_of_polygon(lon, lat, intra_poly) and np.isfinite(dep) and dep < BACKARC_MAX_DEPTH:
        return "backarc", np.nan

    # If outside slab or depth unknown
    if (slab_depth is None) or (not np.isfinite(dep)):
        return "unclassified", np.nan

    # ---- Subduction domain depth-first classification ----
    relocated = _is_relocated(row)
    lon_err, lat_err, dep_err = _numeric_errors(row)
    has_mech = _has_mechanism(row)

    if slab_depth < SUBDUCTION_CLASSIFY_MAX_SLAB_DEPTH:
        # Shallow slab

        # 1) Relocated → strict small buffer
        if relocated:
            if dep <= slab_depth - INTERFACE_DEPTH_TOL:
                return "forearc", slab_depth
            if dep >= slab_depth + INTERFACE_DEPTH_TOL:
                return "intra_slab", slab_depth
            # ambiguous (inside buffer) → interface zone

        else:
            # 2) Numeric errors → ellipse sampling of slab depths
            if np.isfinite(dep_err) and dep_err > 0:
                mask = _ellipse_mask(slab.lon, slab.lat, lon, lat, lon_err, lat_err)
                if mask.any():
                    min_slab = float(np.nanmin(slab.depth[mask]))
                    max_slab = float(np.nanmax(slab.depth[mask]))
                else:
                    # Fallback: if ellipse hits nothing, use nearest-node depth
                    min_slab = max_slab = float(slab_depth) if slab_depth is not None else np.nan

                # Only do the depth gates if we actually have slab values
                if np.isfinite(min_slab) and (dep + dep_err < min_slab - INTERFACE_DEPTH_TOL):
                    return "forearc", slab_depth
                if np.isfinite(max_slab) and (dep - dep_err > max_slab + INTERFACE_DEPTH_TOL):
                    return "intra_slab", slab_depth

                # otherwise ambiguous → interface zone

            # 3) Explicit zero error → poorly constrained → strict buffer
            elif np.isfinite(dep_err) and dep_err == 0.0:
                if dep <= slab_depth - STRICT_INTERFACE_DEPTH_TOL:
                    return "forearc", slab_depth
                if dep >= slab_depth + STRICT_INTERFACE_DEPTH_TOL:
                    return "intra_slab", slab_depth
                # ambiguous → interface zone

            # 4) No error info at all → default depth gate
            else:
                if dep <= slab_depth - STRICT_INTERFACE_DEPTH_TOL:
                    return "forearc", slab_depth
                if dep >= slab_depth + STRICT_INTERFACE_DEPTH_TOL:
                    return "intra_slab", slab_depth
                # ambiguous → interface zone

        # ---- At this point we are in the "interface buffer" region ----
        if has_mech:
            # Use kinematics when available
            if interface_mech_ok_cone(
                row,
                slab_strike=slab_strike,
                slab_dip=slab_dip,
                conv_az_deg=CONV_AZIMUTH_DEG,
                norm_cone_deg=NORM_CONE_DEG,
                slip_cone_deg=SLIP_CONE_DEG,
                id_=row.get("id"),
            ):
                return "slab_interface", slab_depth
            # Mechanism exists but is not interface-like: fall back to depth relation
            return ("forearc" if dep < slab_depth else "intra_slab"), slab_depth
        else:
            # *** NEW: ambiguous in depth AND no focal mechanism → still treat as interface ***
            return "slab_interface", slab_depth

    else:
        # Deep-slab domain
        if dep >= slab_depth - DEEP_SLAB_TOL:
            return "slab_deep", slab_depth
        if dep < slab_depth - DEEP_SLAB_TOL:
            return "forearc", slab_depth

    # Fallback (should rarely be hit)
    return ("forearc" if dep < slab_depth else "intra_slab"), slab_depth

# ---- Catalog driver ----
def _coerce_numeric(df: pd.DataFrame, cols: Iterable[str]) -> None:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


def _map_raw_to_final(raw_class: str) -> str:
    """Collapse raw classes to final classes we actually use."""
    if raw_class in ("intraarc_shallow", "intraarc_deep"):
        return "intraarc"
    if raw_class in ("slab_interface", "intra_slab", "slab_deep", "outer_rise", "forearc"):
        return raw_class
    # everything else (backarc, unclassified, oddballs) → unclassified
    return "unclassified"

def _upsert_special_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the catalog contains the corrected 2010-03-11 events:

    - id='85308'  : replace if present, otherwise insert
    - id='85308b' : insert if missing

    Only columns that exist in `df` are used; others are ignored.
    Ordering is restored by time_iso (and id if present).
    """
    records = [
        {
            "id": "85308b",
            "time_iso": "2010-03-11T14:55:35",
            "longitude": -71.891,
            "latitude": -34.290,
            "depth": 11.3,
            "mag": 6.9,
            "mag_type": "mw",
            "lon_error": 0.01,
            "lat_error": 0.01,
            "depth_error": 0.3,
            "mag_error": np.nan,
            "strike1": 144.0,
            "dip1": 55.0,
            "rake1": -90.0,
            "strike2": 324.0,
            "dip2": 35.0,
            "rake2": -90.0,
            "Mrr": np.nan,
            "Mtt": np.nan,
            "Mpp": np.nan,
            "Mrt": np.nan,
            "Mrp": np.nan,
            "Mtp": np.nan,
            "source": "CSN-improved",
            "dups": "",
            # class_raw, sub_depth, class will be recomputed later if present
        },
        {
            "id": "85308",
            "time_iso": "2010-03-11T14:55:35",
            "longitude": -71.79,
            "latitude": -34.32,
            "depth": 16.3,
            "mag": 7.0,
            "mag_type": "mw",
            "lon_error": 0.01,
            "lat_error": 0.01,
            "depth_error": 0.3,
            "mag_error": np.nan,
            "strike1": 16.0,
            "dip1": 6.0,
            "rake1": -53.0,
            "strike2": 159.0,
            "dip2": 86.0,
            "rake2": -93.0,
            "Mrr": -5.9e18,
            "Mtt": 2.4e17,
            "Mpp": 5.66e18,
            "Mrt": -1.27e19,
            "Mrp": 3.2e19,
            "Mtp": 2.7e17,
            "source": "CSN-improved",
            "dups": "",
        },
    ]

    # Only keep columns that actually exist in df
    rec_df = pd.DataFrame(records)
    rec_df = rec_df[[c for c in rec_df.columns if c in df.columns]]

    # Upsert by id
    for _, row in rec_df.iterrows():
        evid = row["id"]
        mask = (df["id"].astype(str) == str(evid)) if "id" in df.columns else None

        if mask is not None and mask.any():
            # Replace existing rows
            for col in row.index:
                df.loc[mask, col] = row[col]
        else:
            # Insert new row, matching df columns
            new_row = {col: (row[col] if col in row.index else np.nan) for col in df.columns}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Restore ordering by time (and id if present)
    if "time_iso" in df.columns:
        if "id" in df.columns:
            df = df.sort_values(["time_iso", "id"], kind="mergesort", ignore_index=True)
        else:
            df = df.sort_values("time_iso", kind="mergesort", ignore_index=True)

    return df

def classify_catalog(
    in_csv: str,
    out_csv_all: str,
    intra_poly,
    trench_line,
    slab: SlabGrid,
) -> pd.DataFrame:
    """
    Classify events in in_csv; write a single full catalog to out_csv_all
    with both raw and final classes, and return the DataFrame.
    """
    os.makedirs(os.path.dirname(out_csv_all) or ".", exist_ok=True)
    df = pd.read_csv(in_csv)
    df = _upsert_special_events(df)
    # Do NOT coerce lon_error/lat_error/depth_error — we need the string "relocated"
    numeric_cols = [
        "longitude",
        "latitude",
        "depth",
        "strike1",
        "dip1",
        "rake1",
        "strike2",
        "dip2",
        "rake2",
        "Mrr",
        "Mtt",
        "Mpp",
        "Mrt",
        "Mrp",
        "Mtp",
    ]
    _coerce_numeric(df, numeric_cols)

    raw_classes: list[str] = []
    subdeps: list[float | None] = []
    for _, row in df.iterrows():
        cls_raw, sd = classify_row(row, intra_poly, trench_line, slab)
        raw_classes.append(cls_raw)
        subdeps.append(sd)

    df["class_raw"] = raw_classes
    df["sub_depth"] = subdeps
    df["class"] = df["class_raw"].map(_map_raw_to_final)

    # --- POST-PROCESSING OVERRIDE: all intra_slab events before 1930 → slab_interface ---
    years = pd.to_datetime(df["time_iso"], utc=True, errors="coerce").dt.year
    mask_old_intraslab = (
            (df["class_raw"] == "intra_slab") &
            years.notna() &
            (years < 1930)
    )
    df.loc[mask_old_intraslab, "class_raw"] = "slab_interface"
    df.loc[mask_old_intraslab, "class"] = "slab_interface"
    # --- MANUAL OVERRIDE for specific 2010-03-11 events ---
    if "id" in df.columns:
        override = {
            "85308b": {
                "class_raw": "forearc",
                "class": "forearc",
                "sub_depth": 29.9671802521,
            },
            "85308": {
                "class_raw": "forearc",
                "class": "forearc",
                "sub_depth": 29.9671802521,
            },
        }
        for evid, vals in override.items():
            mask = df["id"].astype(str) == evid
            for col, val in vals.items():
                if col in df.columns:
                    df.loc[mask, col] = val
    # quick summary
    print(
        "Raw class totals: "
        + ", ".join(f"{c}={int((df['class_raw'] == c).sum())}" for c in RAW_CLASSES)
    )
    print(
        "Final class totals: "
        + ", ".join(f"{c}={int((df['class'] == c).sum())}" for c in FINAL_CLASSES)
    )

    df.to_csv(out_csv_all, index=False)
    print(f"[OK] wrote combined classified catalog: {out_csv_all} ({len(df)} rows)")

    return df


def write_per_class_catalogs(df: pd.DataFrame) -> None:
    """
    Split df into per-class catalogs and write to paths.cat_{class}
    for classes in FINAL_CLASSES.
    """
    for cls in FINAL_CLASSES:
        attr_name = f"cat_{cls}"
        if not hasattr(paths, attr_name):
            print(f"[WARN] paths.{attr_name} not defined; skipping write for class '{cls}'")
            continue
        out_path = getattr(paths, attr_name)
        df_cls = df[df["class"] == cls].copy()
        os.makedirs(os.path.dirname(str(out_path)) or ".", exist_ok=True)
        df_cls.to_csv(out_path, index=False)
        print(f"[OK] wrote {cls}: {out_path} ({len(df_cls)} rows)")


def main() -> None:
    intra_poly = load_union(str(paths.intraarc_shp))
    trench_line = load_union(str(paths.trench_shp))
    slab = load_slab_xyz(
        str(paths.slab_depth),
        str(paths.slab_strike),
        str(paths.slab_dip),
    )

    # Classify the relocated integrated catalog
    df_all = classify_catalog(
        in_csv=str(paths.cat_integrated_relocated),
        out_csv_all=str(paths.cat_classified),
        intra_poly=intra_poly,
        trench_line=trench_line,
        slab=slab,
    )

    # Write separate CSVs per final class
    write_per_class_catalogs(df_all)


if __name__ == "__main__":
    main()
