from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from cat_no_mech_handler.parsers.tools import _sf, filter_df
from cat_no_mech_handler import paths

# -------------------- CONFIG --------------------
# Spatial / magnitude filters (adjust as needed).
# NOTE: By default we do *not* filter by time for this catalog.
LAT_MIN, LAT_MAX = -58.0, -16.0
LON_MIN, LON_MAX = -80.0, -65.0
MAG_MIN = 4.0  # default mag filter on the homogenized 'magnitude' column

# -------------------- OUTPUT SCHEMA --------------------
FIELDS = [
    "id",
    "time_iso",
    "longitude",
    "latitude",
    "depth",
    "mag",
    "mag_type",
    "lon_error",
    "lat_error",
    "depth_error",
    "mag_error",
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
    "source",
]

# -------------------- SPECIAL HARDCODED MECHANISMS --------------------
# Replace "PUT_EVENT_ID_HERE" with the actual event id string from your catalog.
SPECIAL_MECHS: Dict[str, tuple[float, float, float, float, float, float]] = {
    # id : (strike1, dip1, rake1, strike2, dip2, rake2)
    "890": (10.0, 17.0, 105.0, 170.0, 79.0, 90.0),
}


# -------------------- PARSE ONE ROW --------------------
def _build_time_iso(row: pd.Series) -> Optional[str]:
    """Build ISO time string from year / month / day / hour / minute / second.

    Returns
    -------
    str or None
        Time as 'YYYY-MM-DDTHH:MM:SS' (no timezone), or None if it cannot be built.
    """
    try:
        year = int(row["year"])
        month = int(row["month"])
        day = int(row["day"])
        hour = int(row["hour"])
        minute = int(row["minute"])
        # second might be stored as '0', '30', etc.
        sec_raw = str(row["second"])
        sec = int(float(sec_raw)) if sec_raw not in ("", "nan", "NaN") else 0
        dt = datetime(year, month, day, hour, minute, sec)
        return dt.isoformat(timespec="seconds")
    except Exception:
        return None


def _select_magnitude(row: pd.Series) -> tuple[Optional[float], Optional[str], Optional[float]]:
    """Select preferred magnitude and its type for the integrated catalog.

    For this catalog we *always* take the homogenized `magnitude` column.
    If it is missing, the event should be discarded.

    mag_type is set to 'mw' for all retained events.
    """
    # magnitude and mag_unc are already stripped in prepare_integrated
    mag_val = _sf(row.get("magnitude"))
    mag_unc = _sf(row.get("mag_unc"))

    if mag_val is not None:
        # Treat integrated magnitude as Mw-like
        return mag_val, "mw", mag_unc

    # No usable magnitude: caller should discard the event.
    return None, None, mag_unc


def parse_integrated_row(row: pd.Series) -> Dict[str, Any] | None:
    """Parse one row of the integrated seismic catalog into the standard schema.

    Returns
    -------
    dict or None
        Parsed record, or None if the event should be discarded
        (e.g., missing homogenized magnitude).
    """
    # Event id (string, stripped) – we need this early for special cases
    eid_raw = row.get("id")
    eid = str(eid_raw).strip() if eid_raw is not None else None

    # Time
    time_iso = _build_time_iso(row)

    # Location & depth
    lon = _sf(row.get("longitude"))
    lat = _sf(row.get("latitude"))
    depth = _sf(row.get("depth"))

    # Errors (wire directly from *_Error fields)
    lon_error = _sf(row.get("longitudeError"))
    lat_error = _sf(row.get("latitudeError"))
    depth_error = _sf(row.get("depthError"))

    # Magnitude and uncertainty
    mag, mag_type, mag_error = _select_magnitude(row)
    # If no homogenized magnitude -> drop this event
    if mag is None:
        return None

    # --- Focal mechanism (strike/dip/rake) ---
    # default: read from row
    s1 = _sf(row.get("strike1"))
    d1 = _sf(row.get("dip1"))
    r1 = _sf(row.get("rake1"))
    s2 = _sf(row.get("strike2"))
    d2 = _sf(row.get("dip2"))
    r2 = _sf(row.get("rake2"))

    # override with hard-coded mechanism if this event is in SPECIAL_MECHS
    if eid is not None and eid in SPECIAL_MECHS:
        s1, d1, r1, s2, d2, r2 = SPECIAL_MECHS[eid]

    # Moment tensor components not provided -> keep blank (None)
    Mrr = Mtt = Mpp = Mrt = Mrp = Mtp = None

    # Source
    source_raw = row.get("catalog")
    source = str(source_raw).strip() if source_raw is not None else None

    return dict(
        id=eid,
        time_iso=time_iso,
        longitude=lon,
        latitude=lat,
        depth=depth,
        mag=mag,
        mag_type=mag_type,
        lon_error=lon_error,
        lat_error=lat_error,
        depth_error=depth_error,
        mag_error=mag_error,
        strike1=s1,
        dip1=d1,
        rake1=r1,
        strike2=s2,
        dip2=d2,
        rake2=r2,
        Mrr=Mrr,
        Mtt=Mtt,
        Mpp=Mpp,
        Mrt=Mrt,
        Mrp=Mrp,
        Mtp=Mtp,
        source=source,
    )


# -------------------- DRIVER --------------------
def build_csv_from_catalog(
    input_catalog: pd.DataFrame,
    out_path: str | bytes | None,
    time_min: Optional[pd.Timestamp] = None,
) -> None:
    """Convert the integrated seismic catalog to the standard CSV format.

    Parameters
    ----------
    input_catalog : DataFrame
        Raw integrated catalog with columns:
        id;catalog;latitude;latitudeError;longitude;longitudeError;depth;depthError;
        year;month;day;hour;minute;second;Mw;Ms;Mb;Ml;Md;Mc;M;mag_unc;Mo_escalar;
        strike1;dip1;rake1;strike2;dip2;rake2;magnitude;general_remarks;obs_depth;
        relocated;reference
    out_path : str or bytes or None
        Output CSV path. If None, nothing is written to disk.
    time_min : pandas.Timestamp, optional
        If provided, this is passed to `filter_df` to enable optional time filtering.
        By default (None), no time filter is applied.
    """
    rows: List[Dict[str, Any]] = []
    failed: List[str] = []
    total = len(input_catalog)

    for i, row in input_catalog.iterrows():
        eid = str(row["id"]).strip()
        # print(f"[INTEGRATED] parsing {i + 1}/{total} id: {eid}")
        try:
            rec = parse_integrated_row(row)
        except Exception as exc:
            # print(f"[INTEGRATED] failed parsing id {eid}: {exc}")
            failed.append(eid)
            continue

        # rec can be None if magnitude is missing -> discard event
        if rec is None:
            failed.append(eid)
            continue

        rows.append(rec)

    df = pd.DataFrame(rows, columns=FIELDS)

    if not df.empty:
        filter_kwargs: Dict[str, Any] = dict(
            lon_min=LON_MIN,
            lon_max=LON_MAX,
            lat_min=LAT_MIN,
            lat_max=LAT_MAX,
            mag_min=MAG_MIN,
        )
        # Only filter by time if explicitly requested
        if time_min is not None:
            filter_kwargs["time_min"] = time_min

        df = filter_df(df, **filter_kwargs)

        df = df.sort_values("time_iso").reset_index(drop=True)

    if not df.empty and out_path:
        df.to_csv(out_path, index=False)

    print(
        f"[INTEGRATED] wrote {out_path} with {len(df)} rows "
        f"(from {total} rows; failed {len(failed)})"
    )


def prepare_integrated(
    in_path: str | bytes,
    out_path: str | bytes,
    time_min: Optional[str | pd.Timestamp] = None,
) -> None:
    """Convenience wrapper to read the raw CSV (semicolon-delimited) and build the output.

    Parameters
    ----------
    in_path : str or bytes
        Path to the raw integrated catalog (semicolon-delimited CSV).
    out_path : str or bytes
        Path to the standardized output CSV.
    time_min : str or pandas.Timestamp, optional
        Optional minimum time for filtering (e.g. '1900-01-01T00:00:00').
        If None, no time filter is applied.
    """
    # Read everything as string; numeric conversion is handled row-wise via _sf
    inputcat = pd.read_csv(in_path, sep=";", dtype=str)

    # --- strip leading/trailing whitespace from ALL string cells ---
    inputcat = inputcat.applymap(lambda v: v.strip() if isinstance(v, str) else v)

    tmin_ts: Optional[pd.Timestamp]
    if isinstance(time_min, str):
        tmin_ts = pd.to_datetime(time_min, utc=True, errors="coerce")
    else:
        tmin_ts = time_min

    build_csv_from_catalog(inputcat, out_path, time_min=tmin_ts)


if __name__ == "__main__":
    prepare_integrated(paths.rawcat_integrated, paths.cat_integrated)
