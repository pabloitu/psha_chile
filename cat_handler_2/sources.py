# Readers of the frozen input catalogs and the event matching between them.
# cabello() keeps only the rows south of config.LAT_MAX.
# Each reader returns one row per event with id (str), t (s since 1970, valid
# before 1677), time_iso, longitude, latitude, depth, mag, plus the source's
# own columns.

import numpy as np
import pandas as pd

from cat_handler_2 import config as C

N_NORTH = 0
SDR = ["strike1", "dip1", "rake1", "strike2", "dip2", "rake2"]
MT = ["Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp"]


def stamp(df, y="year", mo="month", d="day", h="hour", mi="minute", s="second"):
    base = (df[y].astype(int).astype(str).str.zfill(4) + "-" + df[mo].clip(1).astype(int).astype(str).str.zfill(2)
            + "-" + df[d].clip(1).astype(int).astype(str).str.zfill(2) + "T" + df[h].astype(int).astype(str).str.zfill(2)
            + ":" + df[mi].astype(int).astype(str).str.zfill(2))
    t = np.array(base, dtype="datetime64[m]") + (df[s].astype(float).to_numpy() * 1000).round().astype("timedelta64[ms]")
    return t


def finish(df, t):
    t = np.asarray(t, dtype="datetime64[ms]")
    df["t"] = t.astype("int64") / 1000.0
    df["time_iso"] = np.datetime_as_string(t, unit="s")
    return df


def cabello():
    d = pd.read_csv(C.CABELLO, sep=";", low_memory=False)
    d = d.rename(columns={"catalog": "agency", "Mw": "Mw_native", "depthError": "depth_error",
                          "latitudeError": "lat_error", "longitudeError": "lon_error"})
    d["id"] = d["id"].astype(str)
    d["mag"] = d["magnitude"]
    for c in SDR:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    global N_NORTH
    N_NORTH = int((d["latitude"] > C.LAT_MAX).sum())
    d = d[d["latitude"] <= C.LAT_MAX].reset_index(drop=True)
    return finish(d, stamp(d))


def potin():
    d = pd.read_csv(C.POTIN).rename(columns={"#": "id", "magnitude": "mag"})
    d["id"] = "potin:" + d["id"].astype(str)
    return finish(d, stamp(d, s="seconds"))


def gcmt():
    """
    Chile-region events of the GCMT ndk files.

    Returns
    -------
    DataFrame
        t, time_iso, longitude, latitude, depth: PDE hypocentre;
        ct, c_lon, c_lat, c_depth, c_dtype (FREE / FIX / BDY): centroid;
        mag: Mw from the scalar moment; SDR and MT columns.
    """
    rows = []
    for p in C.GCMT:
        L = p.read_text().splitlines()
        for i in range(0, len(L) - 4, 5):
            l1, l2, l3, l4, l5 = L[i:i + 5]
            c, f, h = l3.split(), l5.split(), l1[4:].split()
            lat, lon = float(c[3]), float(c[5])
            if not (C.BOX[0] <= lat <= C.BOX[1] and C.BOX[2] <= lon <= C.BOX[3]):
                continue
            hh, mm, ss = h[1].split(":")
            t = np.datetime64(h[0].replace("/", "-") + "T" + hh + ":" + mm, "ms") + np.timedelta64(round(float(ss) * 1000), "ms")
            e, m = int(l4.split()[0]), l4.split()[1:]
            rows.append({"id": "gcmt:" + l2.split()[0], "_t": t, "_ct": t + np.timedelta64(round(float(c[1]) * 1000), "ms"),
                         "longitude": float(h[3]), "latitude": float(h[2]), "depth": float(h[4]),
                         "c_lon": lon, "c_lat": lat, "c_depth": float(c[7]), "c_dtype": c[9],
                         "mag": round(2 / 3 * np.log10(float(f[-7]) * 10 ** e) - 10.7, 2),
                         **dict(zip(MT, (float(m[k]) * 10 ** e for k in range(0, 12, 2)))),
                         **dict(zip(SDR, map(float, f[-6:])))})
    d = pd.DataFrame(rows)
    d["ct"] = d.pop("_ct").to_numpy().astype("datetime64[ms]").astype("int64") / 1000.0
    return finish(d, d.pop("_t").to_numpy())


def anss():
    d = pd.read_csv(C.ANSS, low_memory=False)
    d = d[d["latitude"].between(*C.BOX[:2]) & d["longitude"].between(*C.BOX[2:])].copy()
    d["id"] = "anss:" + d["id"].astype(str)
    return finish(d, pd.to_datetime(d["time_iso"]).to_numpy())


def gem():
    d = pd.read_csv(C.GEM)
    d["id"] = "gem:" + d["id"].astype(str)
    return finish(d, np.array(d["time_iso"], dtype="datetime64[ms]"))


# matching


def hav(lo1, la1, lo2, la2):
    p = np.pi / 180
    a = np.sin((la2 - la1) * p / 2) ** 2 + np.cos(la1 * p) * np.cos(la2 * p) * np.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def pairs(a, b, dt, dkm, dm=np.inf, ta="t", tb="t", xa=("longitude", "latitude"), xb=("longitude", "latitude")):
    """
    All pairs (row of a, row of b) within dt seconds, dkm km and dm magnitude units.

    A missing magnitude never excludes a pair. Time and location columns can be
    chosen per side, e.g. the GCMT centroid.

    Returns
    -------
    DataFrame
        ia, ib (positions in a and b), dt, dkm, dz (b - a), dm (b - a).
    """
    t1, t2 = a[ta].to_numpy(float), b[tb].to_numpy(float)
    o = np.argsort(np.where(np.isfinite(t2), t2, np.inf), kind="stable")
    s = t2[o]
    lo = np.searchsorted(s, t1 - dt, "left")
    n = np.where(np.isfinite(t1), np.searchsorted(s, t1 + dt, "right") - lo, 0)
    ia = np.repeat(np.arange(len(a)), n)
    ib = o[(np.repeat(lo - np.cumsum(n) + n, n) + np.arange(n.sum())).astype(int)] if n.sum() else np.zeros(0, int)
    f = lambda d, c: pd.to_numeric(d[c], errors="coerce").to_numpy(float)
    q = pd.DataFrame({"ia": ia, "ib": ib, "dt": np.abs(t2[ib] - t1[ia]),
                      "dkm": hav(f(a, xa[0])[ia], f(a, xa[1])[ia], f(b, xb[0])[ib], f(b, xb[1])[ib]),
                      "dz": f(b, "depth")[ib] - f(a, "depth")[ia], "dm": f(b, "mag")[ib] - f(a, "mag")[ia]})
    return q[(q["dkm"] <= dkm) & ~(q["dm"].abs() > dm)].reset_index(drop=True)


def one_to_one(q, dt, dkm):
    """Keep the best pair per row of either side, best = smallest dt/DT + dkm/DKM, greedily."""
    q = q.assign(score=q["dt"] / dt + q["dkm"] / dkm).sort_values("score")
    ua, ub, keep = set(), set(), []
    for k, i, j in zip(q.index, q["ia"], q["ib"]):
        if i not in ua and j not in ub:
            keep.append(k)
            ua.add(i)
            ub.add(j)
    return q.loc[keep].sort_values("ia").reset_index(drop=True)
