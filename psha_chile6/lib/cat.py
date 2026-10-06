import datetime
import hashlib

import numpy as np
import pandas as pd

import paths


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
    df = pd.read_csv(path, low_memory=False, dtype={"id": str, "dup_ids": str})
    df["year"] = [decyear(str(s)) for s in df["time_iso"]]
    df = df[np.isfinite(df["year"]) & df["mag"].notna()]
    if cls is not None and "class" in df.columns:
        df = df[df["class"].isin(np.atleast_1d(cls))]
    if bbox is not None:
        lo, hi, la, ha = bbox
        df = df[df["longitude"].between(lo, hi) & df["latitude"].between(la, ha)]
    return df.reset_index(drop=True)


def family(path, fam, cmap=None):
    """
    Events of one source family of catalog.csv.

    Parameters
    ----------
    path : Path
        catalog.csv of cat_handler_2.
    fam : str
        Key of paths.FAMILIES (interface, in-slab, crustal).
    cmap : dict, optional
        Class -> class the model reads it as (classes without a source of their own).
    """
    df = load(path)
    cls = paths.FAMILIES[fam]
    bad = df.loc[df["class"].isin(cls) != df["family"].eq(fam), "class"].unique()
    if len(bad):
        raise SystemExit(f"{path}: family column and params.FAMILIES disagree on {list(bad)}; rerun classify")
    df = df[df["class"].isin(cls)].copy()
    df["class"] = df["class"].replace(cmap or {})
    return df.reset_index(drop=True)


def exclude(df, rules):
    """Drop events per class by date (time_iso prefix) or by box and minimum magnitude;
    report what was dropped or not found."""
    out = np.zeros(len(df), bool)
    for k, rs in (rules or {}).items():
        for d in rs:
            m = (df["class"] == k).to_numpy().copy()
            if isinstance(d, dict):
                lo, hi, la, ha = d["box"]
                m &= (df["longitude"].between(lo, hi) & df["latitude"].between(la, ha)
                      & (df["mag"] >= d.get("mmin", -9))).to_numpy()
            else:
                m &= df["time_iso"].astype(str).str.startswith(d).to_numpy()
            if not m.any():
                print(f"[exclude] {k} {d}: no event found")
            for r in df[m].itertuples():
                print(f"[exclude] {k} {r.time_iso} M{r.mag} {r.latitude:.2f} {r.longitude:.2f}")
            out |= m
    return df[~out].reset_index(drop=True)


def resolve(df, ids):
    """Event ids for Cabello row ids, including rows merged into an event (dup_ids)."""
    k = {}
    if "dup_ids" in df:
        k = {m: e for e, d in zip(df["id"], df["dup_ids"].fillna("")) for m in d.split(";") if m}
    k.update({e: e for e in df["id"]})
    return [k.get(str(i), str(i)) for i in ids]


def fingerprint(path, df):
    return {"path": str(path),
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()[:16],
            "n": int(len(df)),
            "years": [round(float(df["year"].min()), 2), round(float(df["year"].max()), 2)],
            "mags": [float(df["mag"].min()), float(df["mag"].max())]}
