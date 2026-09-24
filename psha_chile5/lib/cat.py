import datetime
import hashlib

import numpy as np
import pandas as pd


def decyear(s):
    # string slicing on purpose: pandas timestamps stop at 1677 and the
    # catalogs start in 1513
    try:
        y, mo, d = int(s[:4]), int(s[5:7]), int(s[8:10])
        return y + (datetime.date(y, mo, d).timetuple().tm_yday - 1) / 365.25
    except (ValueError, TypeError):
        return np.nan


def load(path, cls=None, bbox=None):
    """
    Read a catalog csv.

    Required columns: time_iso, mag, longitude, latitude, depth.
    Optional: id, class. Rows without a parseable date or magnitude are
    dropped.

    Parameters
    ----------
    path : Path
    cls : str or list of str, optional
        Keep only these values of the class column (ignored if absent).
    bbox : tuple, optional
        (lon_min, lon_max, lat_min, lat_max).
    """
    df = pd.read_csv(path, low_memory=False)
    df["year"] = [decyear(str(s)) for s in df["time_iso"]]
    df = df[np.isfinite(df["year"]) & df["mag"].notna()]
    if cls is not None and "class" in df.columns:
        df = df[df["class"].isin(np.atleast_1d(cls))]
    if bbox is not None:
        lo, hi, la, ha = bbox
        df = df[df["longitude"].between(lo, hi) & df["latitude"].between(la, ha)]
    return df.reset_index(drop=True)


def fingerprint(path, df):
    return {"path": str(path),
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()[:16],
            "n": int(len(df)),
            "years": [round(float(df["year"].min()), 2), round(float(df["year"].max()), 2)],
            "mags": [float(df["mag"].min()), float(df["mag"].max())]}
