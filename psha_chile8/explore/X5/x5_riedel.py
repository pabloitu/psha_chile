"""X5: our events matched to the catalogue of Riedel-Hornig et al. (2026; Zenodo 10.5281/zenodo.15284376), which has
local depths and a class per event. Read-only use of data/riedel_hornig_2026-11-14."""
import numpy as np
import pandas as pd

import x5_lib as X

FILE = X.HERE / "data" / "riedel_hornig_2026-11-14" / "Riedel-Hornig_et_al_Primary_Catalogue.csv"
DT, DD, ML_MIN = 15.0, 100.0, 3.0
TYPE = {"Interplate": "interface", "Interface": "interface", "Intraslab": "in-slab", "Crustal": "crustal", "Outerrise": "outer rise", "NC": "not classified"}


def read():
    r = pd.read_csv(FILE)
    r = r[r.Ml >= ML_MIN].reset_index(drop=True)
    r["t"] = (pd.to_datetime(r.Date + "T" + r.Time, errors="coerce") - pd.Timestamp("1900-01-01")).dt.total_seconds()
    r["z"] = -r.Dep
    r["cls_r"] = r.Type.map(TYPE)
    return r.dropna(subset=["t"]).sort_values("t").reset_index(drop=True)


def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def match(g, r=None):
    """For every event of g the closest Riedel-Hornig event within DT s and DD km (time and distance scaled by the
    windows): columns r_z, r_sig, r_lat, r_lon, r_ml, r_cls, r_dt, r_dd; NaN where there is none."""
    r = read() if r is None else r
    t = (pd.to_datetime(g.time, errors="coerce") - pd.Timestamp("1900-01-01")).dt.total_seconds().to_numpy()
    out = pd.DataFrame(index=g.index, columns=["r_z", "r_sig", "r_lat", "r_lon", "r_ml", "r_cls", "r_dt", "r_dd"], dtype=object)
    rt = r.t.to_numpy()
    for i in np.flatnonzero((t >= rt[0] - DT) & (t <= rt[-1] + DT) & X.m45(g)):
        a, b = np.searchsorted(rt, [t[i] - DT, t[i] + DT])
        if b > a:
            c = r.iloc[a:b]
            dd = hav(g.lat.iloc[i], g.lon.iloc[i], c.Lat.to_numpy(), c.Lon.to_numpy())
            s = np.abs(c.t.to_numpy() - t[i]) / DT + dd / DD
            j = int(np.argmin(s))
            if dd[j] <= DD:
                q = c.iloc[j]
                out.iloc[i] = [q.z, q.Dep_Error, q.Lat, q.Lon, q.Ml, q.cls_r, q.t - t[i], dd[j]]
    for c in ("r_z", "r_sig", "r_lat", "r_lon", "r_ml", "r_dt", "r_dd"):
        out[c] = pd.to_numeric(out[c])
    return out
