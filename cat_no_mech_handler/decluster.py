from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from cat_no_mech_handler import paths


CAT_IN = Path(paths.cat_classified)

IN_CAT_CLASSES_PATH = {
    "intraarc": paths.cat_intraarc_mc,
    "slab_interface": paths.cat_slab_interface_mc,
    "intra_slab": paths.cat_intra_slab_mc,
    "slab_deep": paths.cat_slab_deep_mc,
    "outer_rise": paths.cat_outer_rise_mc,
    "forearc": paths.cat_forecarc_mc,
    "unclassified": paths.cat_unclassified_mc
    }

OUT_CAT_CLASSES_PATH = {
    "intraarc": paths.cat_intraarc_dc,
    "slab_interface": paths.cat_slab_interface_dc,
    "intra_slab": paths.cat_intra_slab_dc,
    "slab_deep": paths.cat_slab_deep_dc,
    "outer_rise": paths.cat_outer_rise_dc,
    "forearc": paths.cat_forearc_dc,
    "unclassified": paths.cat_unclassified_dc
    }
CAT_MERGED_DC = paths.cat_merged_dc


DECLUSTERED_DIR = Path(paths.DECLUSTERED_CATALOGS)

DECLUSTER_FROM_ISO = "1900-01-01T00:00:00"
MIN_MAG_FOR_DECLUSTER = 0.0
DECLUST_SUMMARY_TXT = DECLUSTERED_DIR / "declustering_summary.txt"


def _iso_to_datetime64(s: str) -> np.datetime64:
    """Safe conversion of ISO string to numpy datetime64 (post-1900)."""
    return np.datetime64(pd.to_datetime(s, utc=True))


def haversine_km(lon1: np.ndarray, lat1: np.ndarray,
                 lon2: float, lat2: float) -> np.ndarray:
    """
    Great-circle distance (km) between (lon1, lat1) array and one point (lon2, lat2).
    All longitudes/latitudes in degrees.
    """
    R = 6371.0
    lon1_rad = np.radians(lon1)
    lat1_rad = np.radians(lat1)
    lon2_rad = math.radians(lon2)
    lat2_rad = math.radians(lat2)

    dlon = lon1_rad - lon2_rad
    dlat = lat1_rad - lat2_rad

    a = (np.sin(dlat / 2.0) ** 2 +
         np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2)
    c = 2.0 * np.arcsin(np.sqrt(a))
    return R * c


def gk74_windows(magnitude: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gardner & Knopoff (1974)-style distance and time windows.

    Using the parametrisation (e.g. Teng & Baker 2019):

      log10 L = 0.1238 M + 0.983          (L in km)
      log10 T = 0.032 M + 2.7389,   if M >= 6.5
              = 0.5409 M - 0.547,   otherwise  (T in days)
    """
    m = np.asarray(magnitude, dtype=float)
    log10_L = 0.1238 * m + 0.983
    L = 10.0 ** log10_L

    log10_T_high = 0.032 * m + 2.7389
    log10_T_low = 0.5409 * m - 0.547
    log10_T = np.where(m >= 6.5, log10_T_high, log10_T_low)
    T_days = 10.0 ** log10_T

    return L, T_days


@dataclass
class GKResult:
    mainshock_flags: np.ndarray  # bool array, length N
    cluster_ids: np.ndarray      # int array, cluster index per event


# --------------------------------------------------------------------
# Gardner & Knopoff Type-1 declustering (stand-alone)
# --------------------------------------------------------------------

def gardner_knopoff_type1(
    times: np.ndarray,
    mags: np.ndarray,
    lons: np.ndarray,
    lats: np.ndarray,
    fs_time_prop: float = 0.1,
) -> GKResult:
    """
    Gardner & Knopoff (1974) Type-1 declustering.
    """
    n = len(mags)
    if not (len(times) == len(lons) == len(lats) == n):
        raise ValueError("times, mags, lons, lats must have the same length")

    mags = mags.astype(float)
    lons = lons.astype(float)
    lats = lats.astype(float)

    # Pre-compute space/time windows from magnitudes
    space_windows_km, time_windows_days = gk74_windows(mags)

    # Cluster ids and flags
    cluster_ids = np.zeros(n, dtype=int)
    mainshock_flags = np.ones(n, dtype=bool)
    cluster_id = 1

    # Sort by magnitude (desc) then time (asc). Use indices.
    order = np.lexsort((times, -mags))

    # Convert times to float days relative to some origin for efficiency
    t0 = times.min()
    t_days = (times - t0).astype("timedelta64[s]").astype(float) / 86400.0

    for idx in order:
        if cluster_ids[idx] != 0:
            # Already assigned to a cluster as dependent event
            continue

        # Time window for this potential mainshock
        tw = time_windows_days[idx]
        dt_days = t_days - t_days[idx]
        # Candidate events within [ -tw*fs, +tw ] days
        in_time = (dt_days >= -tw * fs_time_prop) & (dt_days <= tw)

        # Only consider events not yet assigned to any cluster
        candidates = np.where(in_time & (cluster_ids == 0))[0]
        if candidates.size == 0:
            cluster_ids[idx] = cluster_id
            mainshock_flags[idx] = True
            cluster_id += 1
            continue

        # Distances (km) for these candidates from the seed event
        d_km = haversine_km(lons[candidates], lats[candidates],
                            lons[idx], lats[idx])

        inside_space = d_km <= space_windows_km[idx]
        cluster_members = candidates[inside_space]

        # Assign cluster id
        cluster_ids[cluster_members] = cluster_id
        # All members in this window are dependents except the seed itself
        mainshock_flags[cluster_members] = False
        mainshock_flags[idx] = True
        cluster_id += 1

    return GKResult(mainshock_flags=mainshock_flags, cluster_ids=cluster_ids)


def _run_gk_on_dataframe(
    df: pd.DataFrame,
    fs_time_prop: float = 1.0,
) -> pd.DataFrame:
    """
    Run Gardner-Knopoff declustering on a *single* catalog DataFrame.

    - Only declusters events with time >= DECLUSTER_FROM_ISO
      and magnitude >= MIN_MAG_FOR_DECLUSTER.
    - Adds/overwrites two columns: 'is_mainshock', 'cluster_id'.
    - Returns the modified DataFrame.
    """
    required = {"time_iso", "mag", "longitude", "latitude"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Catalog must have columns {required}, missing: {', '.join(missing)}"
        )

    df = df.copy()
    df["time_dt"] = pd.to_datetime(df["time_iso"], errors="coerce", utc=True)

    t_min = pd.Timestamp(DECLUSTER_FROM_ISO, tz="UTC")
    mask_decl = (
        (df["time_dt"] >= t_min)
        & df["mag"].notna()
        & (df["mag"].astype(float) >= MIN_MAG_FOR_DECLUSTER)
    )

    sub = df.loc[mask_decl].copy()
    print(f"[GK] Events in this file: {len(df)}; to decluster: {len(sub)}")

    if len(sub) > 0:
        times = sub["time_dt"].values.astype("datetime64[s]")
        mags = sub["mag"].to_numpy(float)
        lons = sub["longitude"].to_numpy(float)
        lats = sub["latitude"].to_numpy(float)

        gk_res = gardner_knopoff_type1(
            times, mags, lons, lats, fs_time_prop=fs_time_prop
        )

        is_mainshock_full = np.ones(len(df), dtype=bool)
        cluster_ids_full = np.zeros(len(df), dtype=int)

        idx_sub = np.where(mask_decl.to_numpy())[0]
        is_mainshock_full[idx_sub] = gk_res.mainshock_flags
        cluster_ids_full[idx_sub] = gk_res.cluster_ids
    else:
        is_mainshock_full = np.ones(len(df), dtype=bool)
        cluster_ids_full = np.zeros(len(df), dtype=int)

    df["is_mainshock"] = is_mainshock_full
    df["cluster_id"] = cluster_ids_full

    return df


def decluster_single_class_catalog(
    in_path: Path,
    out_path: Path,
    fs_time_prop: float = 1.0,
) -> Path:
    """
    Decluster a single *class-specific* catalog CSV and write a '_dc' version
    into FINAL_CATALOGS/declustered.

    Returns
    -------
    Path
        Output CSV path (e.g. declustered/slab_interface_dc.csv).
    """
    print(f"[CLASS-GK] Reading class catalog: {in_path}")
    df = pd.read_csv(in_path)

    df_dc = _run_gk_on_dataframe(df, fs_time_prop=fs_time_prop)

    # Ensure declustered directory exists
    DECLUSTERED_DIR.mkdir(parents=True, exist_ok=True)

    # Write ONLY mainshocks into declustered folder
    df_main = df_dc[df_dc["is_mainshock"]].copy()
    df_main.to_csv(out_path, index=False)

    print(
        f"[CLASS-GK] Wrote declustered class catalog (mainshocks only): "
        f"{out_path} ({len(df_main)} rows)"
    )



# --------------------------------------------------------------------
# Top-level driver: decluster full catalog (not per-class)
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# Decluster all class catalogs and merge
# --------------------------------------------------------------------
def decluster_all_class_catalogs(fs_time_prop: float = 1.0) -> list[Path]:
    """
    Loop over all CSV catalogs in `paths.FINAL_CATALOGS` and decluster each one.

    - Skips files whose stem already ends with '_dc'.
    - Writes declustered mainshock catalogs into FINAL_CATALOGS/declustered.
    """

    csv_files = IN_CAT_CLASSES_PATH
    for cls, path in csv_files.items():
        decluster_single_class_catalog(path, OUT_CAT_CLASSES_PATH[cls],
                                       fs_time_prop=fs_time_prop)


def merge_declustered_class_catalogs(cat_classes_dc) -> tuple[Path | None, Path | None]:
    """
    Merge all *_dc.csv class catalogs in FINAL_CATALOGS/declustered into a single file
    for quick visualization in QGIS.

    Produces:
    - all_classes_dc.csv      : all declustered class catalogs (already mainshocks only)
    - all_classes_dc_main.csv : same as above (kept for consistency)
    """

    # dc_files = sorted(cat_dir.glob("*_dc.csv"))


    dfs = []
    for cls, cls_cat_path in cat_classes_dc.items():
        print(f"[MERGE] Adding {cls}: {cls_cat_path}")
        df = pd.read_csv(cls_cat_path)
        dfs.append(df)

    merged = pd.concat(dfs, ignore_index=True)

    # Optional: sort by time for nicer inspection
    if "time_iso" in merged.columns:
        merged = merged.sort_values("time_iso")


    merged.to_csv(CAT_MERGED_DC, index=False)
    print(f"[MERGE] Wrote merged declustered catalog (all events): {CAT_MERGED_DC} ({len(merged)} rows)")



# --------------------------------------------------------------------
# Summary: total / clustered / mainshocks (merged + per class)
# --------------------------------------------------------------------

def summarize_declustered_class_catalogs() -> None:
    """
    Print and write a summary with:
    - For the merged catalog: total events, clustered events, mainshocks.
    - For each class catalog: same three numbers.

    Uses:
      - original class catalogs in DECLUSTERED_DIR (no _dc suffix)
      - declustered mainshock catalogs *_dc.csv in DECLUSTERED_DIR
    """


    lines: list[str] = []
    lines.append("=== DECLUSTERING SUMMARY ===")
    lines.append("")

    total_all = 0
    main_all = 0

    lines.append("=== PER CLASS ===")
    lines.append("class_file\tN_total\tN_mainshocks\tN_clustered")

    # for base in base_files:
    for cls, in_path in IN_CAT_CLASSES_PATH.items():

        base_df = pd.read_csv(in_path)
        n_total = len(base_df)

        dc_path = OUT_CAT_CLASSES_PATH[cls]
        if not dc_path.exists():
            print(f"[SUMMARY] WARNING: declustered file missing for {base}: {dc_path}")
            n_main = 0
        else:
            dc_df = pd.read_csv(dc_path)
            n_main = len(dc_df)

        n_cluster = n_total - n_main
        total_all += n_total
        main_all += n_main

        lines.append(f"{cls}\t{n_total}\t{n_main}\t{n_cluster}")

    lines.append("")
    lines.append("=== MERGED (ALL CLASSES) ===")
    n_total_all = total_all
    n_main_all = main_all
    n_cluster_all = n_total_all - n_main_all
    lines.append(f"total_events\t{n_total_all}")
    lines.append(f"mainshocks\t{n_main_all}")
    lines.append(f"clustered_events\t{n_cluster_all}")

    text = "\n".join(lines)

    print("\n[DECLUSTERING SUMMARY]")
    print(text)

    with open(DECLUST_SUMMARY_TXT, "w") as f:
        f.write(text + "\n")

    print(f"[OK] Wrote declustering summary: {DECLUST_SUMMARY_TXT}")


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main() -> None:

    # Decluster all class catalogs with symmetric fore-/aftershock windows
    decluster_all_class_catalogs(fs_time_prop=1.0)
    # Merge them for QGIS visualization
    merge_declustered_class_catalogs(OUT_CAT_CLASSES_PATH)
    # Summarize counts
    summarize_declustered_class_catalogs()


if __name__ == "__main__":
    main()
