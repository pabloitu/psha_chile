from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Dict

import numpy as np
import pandas as pd

from cat_no_mech_handler import paths

# ---------------- Config ----------------
TIME_TOL_S: float = 60.0   # time matching window (seconds)
MAG_TOL: float   = 0.8     # magnitude tolerance (different scales)
DEFAULT_DEPTH = 33.0

# ---------------- Schema ----------------
FIELDS: List[str] = [
    "id", "time_iso", "longitude", "latitude", "depth", "mag", "mag_type",
    "lon_error", "lat_error", "depth_error", "mag_error",
    "strike1", "dip1", "rake1", "strike2", "dip2", "rake2",
    "Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp",
    "source", "dups",
]

MOMENT_FIELDS = ("Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp")
SDR_FIELDS    = ("strike1", "dip1", "rake1", "strike2", "dip2", "rake2")

# Known default depth(s); used only as a label when relocation fails.
DEFAULT_DEPTHS = {DEFAULT_DEPTH}
_ATOL = 1e-6

def _is_default_depth(x) -> bool:
    try:
        xv = float(x)
    except Exception:
        return False
    return any(abs(xv - d) <= _ATOL for d in DEFAULT_DEPTHS)

# One known default mechanism; append more tuples if you discover them
_DEFAULT_MECHS = [(0.0, 45.0, 90.0, 180.0, 45.0, 90.0)]

def _is_default_mech_from_values(vals: Dict[str, Any]) -> bool:
    """Check if SDR tuple matches any known default mechanism pattern."""
    try:
        s1, d1, r1, s2, d2, r2 = (float(vals.get(k)) for k in SDR_FIELDS)
    except Exception:
        return False

    def n(a: float) -> float:
        return (a % 360.0)

    for S1, D1, R1, S2, D2, R2 in _DEFAULT_MECHS:
        if (
            abs(n(s1) - n(S1)) <= _ATOL and
            abs(d1 - D1) <= _ATOL and
            abs(r1 - R1) <= _ATOL and
            abs(n(s2) - n(S2)) <= _ATOL and
            abs(d2 - D2) <= _ATOL and
            abs(r2 - R2) <= _ATOL
        ):
            return True
    return False

# -------------- Helpers -----------------
def _finite(x: Any) -> bool:
    try:
        return np.isfinite(float(x))
    except Exception:
        return False

def _to_epoch(series: pd.Series) -> np.ndarray:
    """Return seconds since epoch (float), NaN if invalid."""
    ts = pd.to_datetime(series, utc=True, errors="coerce")
    out = np.full(len(series), np.nan, dtype="float64")
    mask = ts.notna()
    if mask.any():
        try:
            out[mask.to_numpy()] = (ts[mask].view("int64") // 10**9).astype(float)
        except Exception:
            out[mask.to_numpy()] = (ts[mask].astype("int64") // 10**9).astype(float)
    return out

def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Great-circle distance (km). Returns inf if any input non-finite."""
    if not all(_finite(v) for v in (lon1, lat1, lon2, lat2)):
        return float("inf")
    R = 6371.0
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl   = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def _ensure_error_object_dtype(df: pd.DataFrame) -> None:
    """Allow writing the string 'relocated' in error columns."""
    for c in ("lon_error", "lat_error", "depth_error"):
        if c in df.columns:
            df[c] = df[c].astype(object)

def _ensure_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Make sure all unified fields exist (unused set to NaN)."""
    for c in FIELDS:
        if c not in df.columns:
            df[c] = np.nan
    return df

# -------------- Matching core --------------
def _best_match_index(
    t0: float,
    m0: float | None,
    lon0: float | None,
    lat0: float | None,
    pot_epochs: np.ndarray,
    pot_mags: np.ndarray,
    pot_lons: np.ndarray,
    pot_lats: np.ndarray,
    time_tol_s: float,
    mag_tol: float
) -> Optional[int]:
    """
    Find best candidate index based on:
    1) |Δt| <= time_tol_s
    2) |ΔM| <= mag_tol OR potin_mag is NaN OR merged_mag is NaN
    Choose by min |Δt|, then min |ΔM| (NaN treated as +inf), then min distance.
    Returns index or None if no candidate.
    """
    if not np.isfinite(t0):
        return None

    # Time window via searchsorted
    left = np.searchsorted(pot_epochs, t0 - time_tol_s, side="left")
    right = np.searchsorted(pot_epochs, t0 + time_tol_s, side="right")
    if left >= right:
        return None

    cand_idxs = np.arange(left, right)

    # Magnitude tolerance
    pm = pot_mags[cand_idxs]
    if m0 is None or not np.isfinite(m0):
        mag_ok = np.ones_like(pm, dtype=bool)  # accept all if merged mag unknown
        dmag = np.full_like(pm, np.inf, dtype=float)
    else:
        with np.errstate(invalid="ignore"):
            dmag = np.abs(pm - m0)
        mag_ok = np.isnan(pm) | (dmag <= mag_tol)

    if not mag_ok.any():
        return None

    cand_idxs = cand_idxs[mag_ok]
    if cand_idxs.size == 0:
        return None

    # Ranking within candidates
    dt = np.abs(pot_epochs[cand_idxs] - t0)

    # For tie-breaks: use |ΔM| with NaN treated as +inf
    dmag_c = dmag[mag_ok]
    dmag_c = np.where(np.isfinite(dmag_c), dmag_c, np.inf)

    # Final tie-break: distance
    if lon0 is None or lat0 is None or not all(_finite(v) for v in (lon0, lat0)):
        dist = np.full_like(dt, np.inf, dtype=float)
    else:
        lon_c = pot_lons[cand_idxs]
        lat_c = pot_lats[cand_idxs]
        dist = np.array(
            [haversine_km(lon0, lat0, lo, la) for lo, la in zip(lon_c, lat_c)],
            dtype=float,
        )

    # rank by (|Δt|, |ΔM|, distance)
    order = np.lexsort((dist, dmag_c, dt))
    return int(cand_idxs[order[0]])

# -------------- Step 1: attach MT / SDR to integrated --------------
def attach_mt_from_catalog(
    integrated: pd.DataFrame,
    mt_catalog: pd.DataFrame,
    time_tol_s: float = TIME_TOL_S,
    mag_tol: float = MAG_TOL,
) -> pd.DataFrame:
    """
    Fill missing moment tensor / nodal-plane info in `integrated` using `mt_catalog`
    (paths.cat_merged), based on time/mag/space matching.

    Only fills gaps; never overwrites existing values.
    Skips known default mechanisms.
    """
    integrated = _ensure_fields(integrated.copy())
    mt_catalog = _ensure_fields(mt_catalog.copy())

    # --- Precompute epochs & arrays for MT catalog (sorted by time) ---
    mt_epochs = _to_epoch(mt_catalog["time_iso"])
    order = np.argsort(np.where(np.isfinite(mt_epochs), mt_epochs, np.inf))
    mt_catalog = mt_catalog.iloc[order].reset_index(drop=True)
    mt_epochs = mt_epochs[order].astype(float)

    mt_mags = pd.to_numeric(mt_catalog["mag"], errors="coerce").to_numpy(dtype=float)
    mt_lons = pd.to_numeric(mt_catalog["longitude"], errors="coerce").to_numpy(dtype=float)
    mt_lats = pd.to_numeric(mt_catalog["latitude"],  errors="coerce").to_numpy(dtype=float)

    # --- Integrated arrays ---
    int_epochs = _to_epoch(integrated["time_iso"])
    int_mags   = pd.to_numeric(integrated["mag"], errors="coerce").to_numpy(dtype=float)
    int_lons   = pd.to_numeric(integrated["longitude"], errors="coerce").to_numpy(dtype=float)
    int_lats   = pd.to_numeric(integrated["latitude"],  errors="coerce").to_numpy(dtype=float)

    # We'll work on numpy object arrays for direct assignment
    for field in MOMENT_FIELDS + SDR_FIELDS:
        if field not in integrated.columns:
            integrated[field] = np.nan

    # Stats for sanity checks later
    n_events = len(integrated)
    n_matched = 0
    n_filled_mt = 0
    n_filled_sdr = 0

    for i in range(n_events):
        t0   = int_epochs[i]
        m0   = int_mags[i] if np.isfinite(int_mags[i]) else None
        lon0 = int_lons[i] if np.isfinite(int_lons[i]) else None
        lat0 = int_lats[i] if np.isfinite(int_lats[i]) else None

        j = _best_match_index(
            t0, m0, lon0, lat0,
            mt_epochs, mt_mags, mt_lons, mt_lats,
            time_tol_s=time_tol_s, mag_tol=mag_tol
        )
        if j is None:
            continue

        n_matched += 1
        mt_row = mt_catalog.iloc[j]

        # Check MT completeness
        has_full_mt = all(_finite(mt_row.get(k)) for k in MOMENT_FIELDS)

        # Check SDR completeness and avoid default mechanisms
        sdr_vals = {k: mt_row.get(k) for k in SDR_FIELDS}
        has_full_sdr = all(_finite(sdr_vals[k]) for k in SDR_FIELDS)
        is_default_sdr = _is_default_mech_from_values(sdr_vals) if has_full_sdr else False

        # Fill MT only if complete
        if has_full_mt:
            for k in MOMENT_FIELDS:
                val_int = integrated.at[i, k]
                if not _finite(val_int) and _finite(mt_row.get(k)):
                    integrated.at[i, k] = mt_row.get(k)
                    n_filled_mt += 1

        # Fill SDR only if complete and non-default
        if has_full_sdr and not is_default_sdr:
            for k in SDR_FIELDS:
                val_int = integrated.at[i, k]
                if not _finite(val_int) and _finite(sdr_vals[k]):
                    integrated.at[i, k] = sdr_vals[k]
                    n_filled_sdr += 1

    print(
        f"[MT FILL] integrated events: {n_events}, "
        f"matched in MT catalog: {n_matched}, "
        f"MT fields filled: {n_filled_mt}, "
        f"SDR fields filled: {n_filled_sdr}"
    )

    return integrated

# -------------- Step 2: relocation using POTIN --------------
def relocate_with_potin_df(
    catalog: pd.DataFrame,
    potin: pd.DataFrame,
    time_tol_s: float = TIME_TOL_S,
    mag_tol: float = MAG_TOL,
    default_depth: float = DEFAULT_DEPTH,
) -> pd.DataFrame:
    """
    Relocate `catalog` using `potin` (POTIN catalog) in memory, returning a new DataFrame.
    Logic is equivalent to your original `relocate_with_potin`, but generalized.
    """
    merged = _ensure_fields(catalog.copy())
    potin  = _ensure_fields(potin.copy())

    # Allow string in error fields
    _ensure_error_object_dtype(merged)

    # Precompute epochs & arrays for POTIN (sorted by time)
    potin_epochs = _to_epoch(potin["time_iso"])
    order = np.argsort(np.where(np.isfinite(potin_epochs), potin_epochs, np.inf))
    potin = potin.iloc[order].reset_index(drop=True)
    potin_epochs = potin_epochs[order].astype(float)

    potin_mags = pd.to_numeric(potin["mag"], errors="coerce").to_numpy(dtype=float)
    potin_lons = pd.to_numeric(potin["longitude"], errors="coerce").to_numpy(dtype=float)
    potin_lats = pd.to_numeric(potin["latitude"],  errors="coerce").to_numpy(dtype=float)
    potin_deps = pd.to_numeric(potin["depth"],     errors="coerce").to_numpy(dtype=float)

    # Prepare merged vectors
    merged_epochs = _to_epoch(merged["time_iso"])
    merged_mags   = pd.to_numeric(merged["mag"], errors="coerce").to_numpy(dtype=float)
    merged_lons   = pd.to_numeric(merged["longitude"], errors="coerce").to_numpy(dtype=float)
    merged_lats   = pd.to_numeric(merged["latitude"],  errors="coerce").to_numpy(dtype=float)
    merged_deps   = pd.to_numeric(merged["depth"],  errors="coerce").to_numpy(dtype=float)

    lon_new  = merged["longitude"].to_numpy(dtype=object)
    lat_new  = merged["latitude"].to_numpy(dtype=object)
    dep_new  = merged["depth"].to_numpy(dtype=object)

    lon_err  = merged["lon_error"].to_numpy(dtype=object)
    lat_err  = merged["lat_error"].to_numpy(dtype=object)
    dep_err  = merged["depth_error"].to_numpy(dtype=object)

    n_updated = 0
    n_default_labeled = 0

    for i in range(len(merged)):
        t0   = merged_epochs[i]
        m0   = merged_mags[i] if np.isfinite(merged_mags[i]) else None
        lon0 = merged_lons[i] if np.isfinite(merged_lons[i]) else None
        lat0 = merged_lats[i] if np.isfinite(merged_lats[i]) else None

        j = _best_match_index(
            t0, m0, lon0, lat0,
            potin_epochs, potin_mags, potin_lons, potin_lats,
            time_tol_s=time_tol_s, mag_tol=mag_tol
        )
        if j is None:
            # mark depth as 'default' if it equals DEFAULT_DEPTH (within tolerance)
            if _is_default_depth(merged_deps[i]):
                dep_err[i] = "default"
                n_default_labeled += 1
            continue

        # Update coordinates to relocated
        lon_new[i] = potin_lons[j]
        lat_new[i] = potin_lats[j]
        dep_new[i] = potin_deps[j]

        # Mark errors as 'relocated'
        lon_err[i] = "relocated"
        lat_err[i] = "relocated"
        dep_err[i] = "relocated"

        n_updated += 1

    merged["longitude"]   = lon_new
    merged["latitude"]    = lat_new
    merged["depth"]       = dep_new
    merged["lon_error"]   = lon_err
    merged["lat_error"]   = lat_err
    merged["depth_error"] = dep_err

    print(
        f"[RELOC] relocated {n_updated} / {len(merged)} events, "
        f"depths flagged as default (no match): {n_default_labeled}"
    )

    return merged

# -------------- Pipeline wrapper --------------
def enrich_and_relocate_integrated(
    integrated_csv: str,
    mt_csv: str,
    potin_csv: str,
    out_csv: str,
    time_tol_s: float = TIME_TOL_S,
    mag_tol: float = MAG_TOL,
    default_depth: float = DEFAULT_DEPTH,
) -> None:
    """Full pipeline:
    1) read integrated (no MT),
    2) attach MT/SDR from merged MT catalog,
    3) relocate using POTIN,
    4) write to out_csv.
    """
    # 1) Load
    integrated = pd.read_csv(integrated_csv)
    mt_cat     = pd.read_csv(mt_csv)
    potin_cat  = pd.read_csv(potin_csv)

    # 2) Fill MT / SDR gaps
    integrated_filled = attach_mt_from_catalog(
        integrated,
        mt_cat,
        time_tol_s=time_tol_s,
        mag_tol=mag_tol,
    )

    # 3) Relocate using POTIN
    relocated = relocate_with_potin_df(
        integrated_filled,
        potin_cat,
        time_tol_s=time_tol_s,
        mag_tol=mag_tol,
        default_depth=default_depth,
    )

    # 4) Save
    integrated_filled.to_csv(out_csv, index=False)
    print(
        f"[PIPELINE] wrote {out_csv}  ({len(relocated)} rows)  "
        f"(time_tol_s={time_tol_s}, mag_tol={mag_tol})"
    )

def main() -> None:
    """
    Assumptions (adjust if your paths module uses different names):

    - Integrated input: paths.cat_integrated
    - MT catalog (with mechanisms): paths.cat_merged
    - POTIN catalog: paths.cat_potin
    - Output (integrated + MT + relocation): paths.cat_integrated_relocated
    """
    enrich_and_relocate_integrated(
        integrated_csv=str(paths.cat_integrated),           # <-- adjust if needed
        mt_csv=str(paths.cat_merged),
        potin_csv=str(paths.cat_potin),
        out_csv=str(paths.cat_integrated_relocated),        # <-- adjust if needed
        time_tol_s=TIME_TOL_S,
        mag_tol=MAG_TOL,
        default_depth=DEFAULT_DEPTH,
    )

if __name__ == "__main__":
    main()
