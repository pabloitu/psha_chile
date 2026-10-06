import numpy as np
import pandas as pd


def windows(m, method):
    """
    Space (km) and time (days) windows. gk74 in the Teng & Baker form;
    uhrhammer and gruenthal as in van Stiphout et al. (2012).
    """
    m = np.asarray(m, float)
    if method in ("gk74", "gk74_sym"):
        L = 10 ** (0.1238 * m + 0.983)
        T = 10 ** np.where(m >= 6.5, 0.032 * m + 2.7389, 0.5409 * m - 0.547)
    elif method == "uhrhammer":
        L = np.exp(-1.024 + 0.804 * m)
        T = np.exp(-2.87 + 1.235 * m)
    elif method == "gruenthal":
        L = np.exp(1.77 + np.sqrt(np.maximum(0.037 + 1.02 * m, 0)))
        T = np.where(m >= 6.5, 10 ** (2.8 + 0.024 * m),
                     np.abs(np.exp(-3.95 + np.sqrt(np.maximum(0.62 + 17.32 * m, 0)))))
    else:
        raise ValueError(method)
    return L, T


def hav(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = (np.sin((lat1 - lat2) * p / 2) ** 2
         + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon1 - lon2) * p / 2) ** 2)
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def gk(t, m, lon, lat, method, fs):
    """
    Window declustering, type 1: seeds in descending magnitude; unassigned
    events inside the seed window join its cluster.

    Returns
    -------
    main : bool array
    cid : int array
    """
    L, T = windows(m, method)
    cid = np.zeros(len(m), int)
    main = np.ones(len(m), bool)
    k = 1
    for i in np.lexsort((t, -m)):
        if cid[i]:
            continue
        dt = t - t[i]
        j = np.where((dt >= -T[i] * fs) & (dt <= T[i]) & (cid == 0))[0]
        if j.size:
            j = j[hav(lon[j], lat[j], lon[i], lat[i]) <= L[i]]
            cid[j] = k
            main[j] = False
        cid[i] = k
        main[i] = True
        k += 1
    return main, cid


def run(df, method, fs, y0, keep=(), mprot=7.0):
    """
    Decluster one catalog. Events before y0 pass through as mainshocks;
    method "none" keeps every event (the full catalog).

    Returns
    -------
    out : DataFrame
        Input plus is_mainshock and cluster_id.
    rev : DataFrame
        Removed events with M >= mprot and their cluster parent.
    """
    if method == "none":
        return df.assign(is_mainshock=True, cluster_id=0), pd.DataFrame(
            columns=["method", "id", "year", "mag", "lat", "depth", "parent_id", "parent_year", "parent_mag",
                     "dt_days", "d_km"])
    fs = 1.0 if method == "gk74_sym" else fs
    sub = df[df["year"] >= y0]
    idx = sub.index.to_numpy()
    main, cid = gk((sub["year"].to_numpy() - y0) * 365.25, sub["mag"].to_numpy(),
                   sub["longitude"].to_numpy(), sub["latitude"].to_numpy(), method, fs)
    out = df.copy()
    out["is_mainshock"] = True
    out["cluster_id"] = 0
    out.loc[idx, "is_mainshock"] = main
    out.loc[idx, "cluster_id"] = cid

    rows = []
    rem = out.loc[idx][~out.loc[idx, "is_mainshock"] & (out.loc[idx, "mag"] >= mprot)]
    for _, r in rem.iterrows():
        p = out[(out["cluster_id"] == r["cluster_id"]) & out["is_mainshock"]].iloc[0]
        rows.append({"method": method, "id": r.get("id"), "year": round(r["year"], 2),
                     "mag": r["mag"], "lat": round(r["latitude"], 2),
                     "depth": r.get("depth", np.nan), "parent_id": p.get("id"),
                     "parent_year": round(p["year"], 2), "parent_mag": p["mag"],
                     "dt_days": round((r["year"] - p["year"]) * 365.25, 1),
                     "d_km": round(float(hav(r["longitude"], r["latitude"],
                                             p["longitude"], p["latitude"])), 1)})
    if len(keep) and "id" in out.columns:
        out.loc[out["id"].astype(str).isin([str(x) for x in keep]), "is_mainshock"] = True
    return out, pd.DataFrame(rows)
