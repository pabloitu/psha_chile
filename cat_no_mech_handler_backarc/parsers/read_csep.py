import csv
from typing import List, Tuple, Optional

from csep.core.catalogs import CSEPCatalog
from csep.utils.time_utils import strptime_to_utc_epoch

from cat_handler import paths


def _parse_time_iso(dt_string: str) -> int:
    """Parse ISO time string to UTC epoch (int seconds)."""
    if not dt_string:
        raise ValueError("Empty time string")
    # try with fractional seconds first, then without
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return strptime_to_utc_epoch(dt_string, format=fmt)
        except Exception:
            pass
    raise ValueError(
        "Supported time-string formats are '%Y-%m-%dT%H:%M:%S.%f' "
        "and '%Y-%m-%dT%H:%M:%S'"
    )


def load_csep(
    fname: str,
    catalog_id: Optional[int] = None,
) -> CSEPCatalog:
    """Load a standardized catalog CSV into a pyCSEP CSEPCatalog.

    The input file is expected to have the header (which is skipped):

        id,time_iso,longitude,latitude,depth,mag,...

    Only the first six columns are used, in this order:

        id, time_iso, lon, lat, depth, mag

    Parameters
    ----------
    fname : str
        Path to the standardized catalog CSV (e.g. paths.cat_integrated).
    catalog_id : int, optional
        Optional catalog id to attach to the CSEPCatalog.

    Returns
    -------
    CSEPCatalog
        pyCSEP catalog with events stored as
        (event_id, origin_time, latitude, longitude, depth, magnitude)
    """
    events: List[Tuple[str, int, float, float, float, float]] = []

    with open(fname, "r", newline="") as f:
        reader = csv.reader(f, delimiter=",")
        # ---- DO NOT READ HEADER AS DATA ----
        header = next(reader, None)  # skip header line unconditionally

        for i, line in enumerate(reader):
            # skip completely empty lines
            if not line or all((not c.strip() for c in line)):
                continue

            # unpack the columns we care about
            event_id_raw = line[0]
            time_iso = line[1]
            lon_str = line[2]
            lat_str = line[3]
            depth_str = line[4]
            mag_str = line[5]

            # basic sanity: need time, lon, lat, mag
            if not (time_iso and lon_str and lat_str and mag_str):
                # skip incomplete records for pyCSEP
                continue

            origin_time = _parse_time_iso(time_iso)
            lon = float(lon_str)
            lat = float(lat_str)
            depth = float(depth_str) if depth_str else 0.0
            magnitude = float(mag_str)

            # event id: fall back to row index if blank
            event_id = event_id_raw.strip()
            if not event_id:
                event_id = str(i)

            events.append((event_id, origin_time, lat, lon, depth, magnitude))

    return CSEPCatalog(data=events, catalog_id=catalog_id)


