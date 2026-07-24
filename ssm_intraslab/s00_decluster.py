# s00_decluster.py
# Decluster the slab classes inside this pipeline, from the classified
# catalog directly (single upstream input; the catalog handler's mc/dc
# files are not used). Classes are declustered SEPARATELY: GK windows act
# on epicenters and must not link deep and shallow populations.
# Methods: gk74 (fs=DC_FS), gk74_sym (fs=1.0, reproduces upstream),
# uhrhammer, gruenthal. Removed events >= DC_MPROT go to a review table
# with their cluster parent; DC_KEEP_IDS forces them back after review.
# Outputs: <OUT>/decluster/cat_dc_{class}_{method}.csv
#          <OUT>/decluster/decluster_summary.csv, removed_large.csv
#          <OUT>/figures/s00_decluster_{class}.png
#
# requires in ssm_config:
#   CAT_CLASSIFIED  path to cat_classified.csv
#   CLASSES         ["intra_slab", "slab_deep"]
#   OUT_DIR, FIG_DIR
#   DC_METHODS = ["gk74", "gk74_sym", "uhrhammer", "gruenthal"]
#   DC_METHOD = "gk74"; DC_FS = 0.1; DC_FROM_YEAR = 1900
#   DC_MPROT = 7.0; DC_KEEP_IDS = []

import datetime
import hashlib

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ssm_config as C

DC_DIR = C.OUT_DIR / "decluster"


def decyear(s):
    # string-slice parse: pd.to_datetime bottoms out at 1677 and the
    # catalog starts 1513
    try:
        y, mo, d = int(s[:4]), int(s[5:7]), int(s[8:10])
        doy = datetime.date(y, mo, d).timetuple().tm_yday
        return y + (doy - 1) / 365.25
    except (ValueError, TypeError):
        return np.nan


def load_classified():
    df = pd.read_csv(C.CAT_CLASSIFIED)
    df["year"] = [decyear(str(s)) for s in df["time_iso"]]
    df = df[np.isfinite(df["year"]) & df["mag"].notna()].reset_index(drop=True)
    rep = {"sha256": hashlib.sha256(C.CAT_CLASSIFIED.read_bytes()).hexdigest()[:16],
           "n_total": len(df)}
    for cl in C.CLASSES:
        sub = df[df["class"] == cl]
        rep[cl] = (f"{len(sub)} events, {sub['year'].min():.0f}-"
                   f"{sub['year'].max():.1f}, M{sub['mag'].min():.1f}-"
                   f"{sub['mag'].max():.1f}")
    print(f"[input] {C.CAT_CLASSIFIED}")
    for k, v in rep.items():
        print(f"  {k}: {v}")
    return df


def windows(m, method):
    """
    Space (km) and time (days) windows per magnitude. gk74 per Teng &
    Baker parametrization; uhrhammer and gruenthal per van Stiphout
    et al. (2010).
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


def haversine(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = (np.sin((lat1 - lat2) * p / 2) ** 2
         + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon1 - lon2) * p / 2) ** 2)
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def gk_type1(t_days, mags, lons, lats, method, fs):
    """
    GK type-1: seeds in descending magnitude order; unassigned events in
    the seed's space-time window join its cluster.
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

    rem = df.loc[idx][~df.loc[idx, "is_mainshock"]
                      & (df.loc[idx, "mag"] >= C.DC_MPROT)]
    rows = []
    for _, r in rem.iterrows():
        cl = df[(df["cluster_id"] == r["cluster_id"]) & df["is_mainshock"]]
        p = cl.iloc[0] if len(cl) else r
        rows.append({"method": method, "id": r.get("id"),
                     "year": round(r["year"], 2), "mag": r["mag"],
                     "lat": round(r["latitude"], 2),
                     "depth": round(r.get("depth", np.nan), 1),
                     "parent_id": p.get("id"),
                     "parent_year": round(p["year"], 2),
                     "parent_mag": p["mag"],
                     "dt_days": round((r["year"] - p["year"]) * 365.25, 1),
                     "d_km": round(haversine(r["longitude"], r["latitude"],
                                             p["longitude"], p["latitude"]), 1)})

    if C.DC_KEEP_IDS and "id" in df.columns:
        forced = df["id"].astype(str).isin([str(x) for x in C.DC_KEEP_IDS])
        df.loc[forced, "is_mainshock"] = True
    return df, pd.DataFrame(rows)


def main():
    DC_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_classified()
    summary, reviews = [], []
    for cl in C.CLASSES:
        cat = df[df["class"] == cl].reset_index(drop=True)
        yr = np.arange(C.DC_FROM_YEAR, int(cat["year"].max()) + 2)
        n_pre = np.histogram(cat[cat["year"] >= C.DC_FROM_YEAR]["year"],
                             bins=np.append(yr, yr[-1] + 1))[0]

        fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
        a1.semilogy(yr, np.maximum(n_pre, 0.5), "k", drawstyle="steps-post",
                    label=f"input ({len(cat)})")
        for method in C.DC_METHODS:
            out, rev = run_method(cat, method)
            dc = out[out["is_mainshock"]]
            dc.drop(columns=["year"]).to_csv(
                DC_DIR / f"cat_dc_{cl}_{method}.csv", index=False)
            rev.insert(0, "class", cl)
            reviews.append(rev)
            summary.append({"class": cl, "method": method, "n_in": len(out),
                            "n_main": len(dc),
                            "frac_removed": round(1 - len(dc) / max(len(out), 1), 3),
                            "n_M7_main": int((dc["mag"] >= 7.0).sum()),
                            "n_M7_removed": len(rev)})
            n_dc = np.histogram(dc["year"], bins=np.append(yr, yr[-1] + 1))[0]
            lw = 2 if method == C.DC_METHOD else 1
            a1.semilogy(yr, np.maximum(n_dc, 0.5), drawstyle="steps-post",
                        lw=lw, label=method)
            a2.plot(yr, np.where(n_pre > 0, 1 - n_dc / np.maximum(n_pre, 1), 0),
                    drawstyle="steps-post", lw=lw)
        a1.legend(fontsize=8)
        a1.set_ylabel("events/yr")
        a2.set_ylabel("fraction removed")
        a2.set_xlabel("year")
        a1.set_title(f"{cl} declustering (bold = '{C.DC_METHOD}')")
        fig.tight_layout()
        fig.savefig(C.FIG_DIR / f"s00_decluster_{cl}.png", dpi=200)
        plt.close(fig)

    tab = pd.DataFrame(summary)
    tab.to_csv(DC_DIR / "decluster_summary.csv", index=False)
    rev = pd.concat(reviews, ignore_index=True)
    rev.to_csv(DC_DIR / "removed_large.csv", index=False)
    print("\n" + tab.to_string(index=False))
    print(f"\nremoved M>={C.DC_MPROT}: {len(rev)} -> removed_large.csv "
          "(review, then fill DC_KEEP_IDS)")
    if len(rev):
        print(rev.to_string(index=False))


if __name__ == "__main__":
    main()