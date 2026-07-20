# s01_decluster.py
# Decluster the classified interface catalog (full margin, unsegmented;
# segments enter at the rate step) inside this pipeline.
# Input is the pre-Mc-filter, pre-decluster class catalog: the upstream
# *_mc.csv files have events below the national per-epoch Mc deleted,
# which is circular for our Mc estimation and starves GK of the small
# aftershocks that define clusters.
# GK type-1 algorithm ported from cat_no_mech_handler/decluster.py (fixed
# behavior preserved), with selectable space-time windows:
#   gk74       Gardner & Knopoff (1974), foreshock fraction DC_FS
#   gk74_sym   same windows, symmetric foreshocks (reproduces upstream)
#   uhrhammer  Uhrhammer (1986)
#   gruenthal  Gruenthal, as in van Stiphout et al. (2010)
# Every removed event >= DC_MPROT is written to removed_large.csv with its
# cluster parent; DC_KEEP_IDS forces events back to mainshock after review.
# Outputs: outputs/decluster/cat_dc_<method>.csv (+ summary, review table)
#          figures/s01_decluster_removal.png

import datetime

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sub_config as C

DC_DIR = C.OUT_DIR / "decluster"


def _decyear(s):
    try:
        y, mo, d = int(s[:4]), int(s[5:7]), int(s[8:10])
        doy = datetime.date(y, mo, d).timetuple().tm_yday
        return y + (doy - 1) / 365.25
    except (ValueError, TypeError):
        return np.nan


def windows(m, method):
    """
    Space (km) and time (days) windows per magnitude for each method.
    gk74 per Teng & Baker parametrization (as upstream); uhrhammer and
    gruenthal per van Stiphout et al. (2010).
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
        T = np.where(m >= 6.5,
                     10 ** (2.8 + 0.024 * m),
                     np.abs(np.exp(-3.95 + np.sqrt(np.maximum(0.62 + 17.32 * m, 0)))))
    else:
        raise ValueError(method)
    return L, T


def haversine(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = (np.sin((lat1 - lat2) * p / 2) ** 2
         + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon1 - lon2) * p / 2) ** 2)
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def gk_type1(t_days, mags, lons, lats, method, fs):
    """
    GK type-1 declustering: seeds taken in descending magnitude order,
    unassigned events inside the seed's space-time window join its cluster.

    Returns
    -------
    main : bool array, cluster parent flags
    cid : int array, cluster id per event
    """
    n = len(mags)
    L, T = windows(mags, method)
    cid = np.zeros(n, int)
    main = np.ones(n, bool)
    k = 1
    for i in np.lexsort((t_days, -mags)):
        if cid[i]:
            continue
        dt = t_days - t_days[i]
        cand = np.where((dt >= -T[i] * fs) & (dt <= T[i]) & (cid == 0))[0]
        if cand.size:
            d = haversine(lons[cand], lats[cand], lons[i], lats[i])
            members = cand[d <= L[i]]
            cid[members] = k
            main[members] = False
        cid[i] = k
        main[i] = True
        k += 1
    return main, cid


def run_method(df, method):
    fs = 1.0 if method == "gk74_sym" else C.DC_FS
    sub = df[df["year"] >= C.DC_FROM_YEAR]
    idx = sub.index.to_numpy()
    t_days = (sub["year"].to_numpy() - C.DC_FROM_YEAR) * 365.25

    main, cid = gk_type1(t_days, sub["mag"].to_numpy(),
                         sub["longitude"].to_numpy(),
                         sub["latitude"].to_numpy(), method, fs)

    df = df.copy()
    df["is_mainshock"] = True
    df["cluster_id"] = 0
    df.loc[idx, "is_mainshock"] = main
    df.loc[idx, "cluster_id"] = cid

    # large-event review table: removed >= DC_MPROT with cluster parent
    rem = df.loc[idx][~df.loc[idx, "is_mainshock"]
                      & (df.loc[idx, "mag"] >= C.DC_MPROT)]
    rows = []
    for _, r in rem.iterrows():
        cl = df[(df["cluster_id"] == r["cluster_id"]) & df["is_mainshock"]]
        p = cl.iloc[0] if len(cl) else r
        rows.append({"method": method, "id": r.get("id"), "year": round(r["year"], 2),
                     "mag": r["mag"], "lat": round(r["latitude"], 2),
                     "parent_id": p.get("id"), "parent_year": round(p["year"], 2),
                     "parent_mag": p["mag"],
                     "dt_days": round((r["year"] - p["year"]) * 365.25, 1),
                     "d_km": round(haversine(r["longitude"], r["latitude"],
                                             p["longitude"], p["latitude"]), 1)})

    # keep-list override
    if C.DC_KEEP_IDS and "id" in df.columns:
        forced = df["id"].astype(str).isin([str(x) for x in C.DC_KEEP_IDS])
        df.loc[forced, "is_mainshock"] = True

    return df, pd.DataFrame(rows)


def main():
    DC_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(C.CAT_INTERFACE)
    df["year"] = [_decyear(str(s)) for s in df["time_iso"]]
    df = df[np.isfinite(df["year"]) & df["mag"].notna()].reset_index(drop=True)
    print(f"input: {len(df)} events, {df['year'].min():.0f}-{df['year'].max():.1f}, "
          f"M{df['mag'].min():.1f}-{df['mag'].max():.1f}")

    summary, reviews, per_year = [], [], {}
    yr = np.arange(C.DC_FROM_YEAR, int(df["year"].max()) + 2)
    for method in C.DC_METHODS:
        out, rev = run_method(df, method)
        dc = out[out["is_mainshock"]]
        dc.drop(columns=["year"]).to_csv(DC_DIR / f"cat_dc_{method}.csv", index=False)
        reviews.append(rev)
        n7 = (dc["mag"] >= 7.0).sum()
        summary.append({"method": method, "n_in": len(out), "n_main": len(dc),
                        "frac_removed": round(1 - len(dc) / len(out), 3),
                        "n_M7_main": int(n7), "n_M7_removed": len(rev)})
        per_year[method] = np.histogram(dc["year"], bins=np.append(yr, yr[-1] + 1))[0]

    tab = pd.DataFrame(summary)
    tab.to_csv(DC_DIR / "decluster_summary.csv", index=False)
    rev = pd.concat(reviews, ignore_index=True)
    rev.to_csv(DC_DIR / "removed_large.csv", index=False)
    print(tab.to_string(index=False))
    print(f"\nremoved M>={C.DC_MPROT}: {len(rev)} entries -> removed_large.csv "
          "(review, then fill DC_KEEP_IDS)")
    if len(rev):
        print(rev.to_string(index=False))

    n_pre = np.histogram(df[df["year"] >= C.DC_FROM_YEAR]["year"],
                         bins=np.append(yr, yr[-1] + 1))[0]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    a1.semilogy(yr, np.maximum(n_pre, 0.5), "k", drawstyle="steps-post",
                label=f"input ({len(df)})")
    for method in C.DC_METHODS:
        lw = 2 if method == C.DC_METHOD else 1
        a1.semilogy(yr, np.maximum(per_year[method], 0.5), drawstyle="steps-post",
                    lw=lw, label=method)
        a2.plot(yr, np.where(n_pre > 0, 1 - per_year[method] / np.maximum(n_pre, 1), 0),
                drawstyle="steps-post", lw=lw)
    a1.legend(fontsize=8)
    a1.set_ylabel("events/yr")
    a2.set_ylabel("fraction removed")
    a2.set_xlabel("year")
    a1.set_title(f"declustering variants (bold = DC_METHOD '{C.DC_METHOD}')")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "s01_decluster_removal.png", dpi=200)


if __name__ == "__main__":
    main()