# ssm_intraslab/s00_decluster.py
# Decluster the slab classes inside this pipeline, from the classified
# catalog directly (single upstream input; the catalog handler's mc/dc
# files are not used). Classes are declustered SEPARATELY: GK windows act
# on epicenters and must not link deep and shallow populations.
# Methods: gk74 (fs=DC_FS), gk74_sym (fs=1.0, reproduces upstream),
# uhrhammer, gruenthal. Removed events >= DC_MPROT go to a review table
# with their cluster parent; DC_KEEP_IDS forces them back after review.
#
# Outputs
#   decluster/cat_dc_{class}_{method}.csv
#   decluster/s00_decluster_summary.csv
#   decluster/s00_decluster_removed_large.csv
#   decluster/s00_decluster_input_report.txt
#   figures/s00_decluster_rates_{class}.png
#   figures/s00_decluster_catalog_map_{class}.png
#   figures/s00_decluster_depth_{class}.png
#   figures/s00_decluster_class_overview.png
#
# requires in ssm_config:
#   CAT_CLASSIFIED, CLASSES, OUT_DIR, FIG_DIR, BBOX
#   DC_METHODS, DC_METHOD, DC_FS, DC_FROM_YEAR, DC_MPROT, DC_KEEP_IDS

import datetime
import hashlib

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ssm_config as C

DC_DIR = C.OUT_DIR / "decluster"
COL = {"intra_slab": "tab:blue", "slab_deep": "tab:red"}


def decyear(s):
    # string-slice parse: pd.to_datetime bottoms out at 1677-09-21 and the
    # catalog starts 1513. Never replace this with pd.to_datetime.
    try:
        y, mo, d = int(s[:4]), int(s[5:7]), int(s[8:10])
        doy = datetime.date(y, mo, d).timetuple().tm_yday
        return y + (doy - 1) / 365.25
    except (ValueError, TypeError):
        return np.nan


def class_cutoff(cl):
    """First year kept for a class: per-class override, else the global."""
    return getattr(C, "HIST_CUTOFF_BY_CLASS", {}).get(
        cl, getattr(C, "HIST_CUTOFF", None))


def apply_cutoff(df, lines, dropped_path=None):
    """Drop pre-instrumental events per class.

    Pre-cutoff locations are macroseismic, so depth — the quantity the
    slab classification keys on — is unconstrained. A large historical
    event surviving into a slab class sets Mmax = M_obs + pad off that
    unconstrained depth; the Chilean historical giants are almost
    certainly interface. Dropped events are written out, not discarded
    silently: the file is the evidence for the register entry.

    Parameters
    ----------
    df : pandas.DataFrame
        Classified catalog with year and class columns.
    lines : list
        Report lines, appended in place.
    dropped_path : Path or None
        Where to write the dropped-event table.

    Returns
    -------
    pandas.DataFrame
        Catalog with pre-cutoff events of each class removed.
    """
    keep = pd.Series(True, index=df.index)
    dropped = []
    for cl in C.CLASSES:
        cut = class_cutoff(cl)
        if cut is None:
            lines.append(f"  [cutoff] {cl}: none — all events kept")
            continue
        m = (df["class"] == cl) & (df["year"] < cut)
        keep &= ~m
        sub = df[m]
        lines.append(f"  [cutoff] {cl}: drop {int(m.sum())} events before {cut}")
        if len(sub):
            big = sub.nlargest(5, "mag")
            lines.append("    largest dropped: " + ", ".join(
                f"M{r.mag:.1f}@{r.year:.0f}(z{r.depth:.0f})"
                for r in big.itertuples()))
            n_big = int((sub["mag"] >= 7.5).sum())
            if n_big:
                lines.append(f"    ^ {n_big} of these are M>=7.5 — the ones "
                             "that would have set Mmax")
            dropped.append(sub.assign(cutoff=cut))
    if dropped and dropped_path is not None:
        cols = [c for c in ["id", "year", "mag", "latitude", "longitude",
                            "depth", "class", "cutoff", "source", "mag_type",
                            "time_iso"] if c in dropped[0].columns]
        pd.concat(dropped)[cols].sort_values(["class", "year"]).to_csv(
            dropped_path, index=False)
    return df[keep].reset_index(drop=True)


def load_classified(report_path=None, dropped_path=None):
    """Load the classified catalog, apply the historical cutoff, and print
    the input fingerprint.

    Parameters
    ----------
    report_path : Path or None
        If given, the fingerprint block is also written here so any
        downstream run can be matched to the exact input file.
    dropped_path : Path or None
        Where to write the events removed by the historical cutoff.

    Returns
    -------
    pandas.DataFrame
        Rows with finite decimal year and magnitude, post-cutoff.
    """
    raw = pd.read_csv(C.CAT_CLASSIFIED)
    df = raw.copy()
    df["year"] = [decyear(str(s)) for s in df["time_iso"]]
    bad_time = int((~np.isfinite(df["year"])).sum())
    bad_mag = int(df["mag"].isna().sum())
    df = df[np.isfinite(df["year"]) & df["mag"].notna()].reset_index(drop=True)

    lines = [f"[input] {C.CAT_CLASSIFIED}",
             f"  sha256: {hashlib.sha256(C.CAT_CLASSIFIED.read_bytes()).hexdigest()}",
             f"  rows_raw: {len(raw)}  dropped_bad_time: {bad_time}  "
             f"dropped_bad_mag: {bad_mag}  rows_used: {len(df)}"]

    if "class" in df.columns:
        for cl, n in df["class"].value_counts().items():
            mark = "  <- used" if cl in C.CLASSES else ""
            lines.append(f"  class {cl}: {n}{mark}")

    for cl in C.CLASSES:
        sub = df[df["class"] == cl]
        if not len(sub):
            lines.append(f"  {cl}: EMPTY — check the classifier")
            continue
        pre = int((sub["year"] < 1900).sum())
        lines.append(
            f"  {cl}: {len(sub)} events, {sub['year'].min():.0f}-"
            f"{sub['year'].max():.1f}, M{sub['mag'].min():.1f}-"
            f"{sub['mag'].max():.1f}, z{sub['depth'].min():.0f}-"
            f"{sub['depth'].max():.0f} km, {pre} pre-1900")
        if pre:
            hist = sub[sub["year"] < 1900]
            vc = hist["depth"].round(1).value_counts().head(3)
            lines.append("    pre-1900 depths: " + ", ".join(
                f"{d} km x{n}" for d, n in vc.items())
                + f"  (M{hist['mag'].min():.1f}-{hist['mag'].max():.1f})")
            if vc.sum() > 0.5 * len(hist) and len(hist) > 5:
                lines.append("    ^ depth values repeat — likely catalog "
                             "defaults, so depth-based class assignment is "
                             "unconstrained for these events")
        # 1575-style intruder check: the pre-1677 events are the ones the
        # upstream timestamp bug used to leak into the wrong class
        old = sub[sub["year"] < 1677].nlargest(5, "mag")
        if len(old):
            lines.append("    pre-1677: " + ", ".join(
                f"M{r.mag:.1f}@{r.year:.0f}(z{r.depth:.0f})"
                for r in old.itertuples()))

    df = apply_cutoff(df, lines, dropped_path)
    lines.append(f"  rows after cutoff: {len(df)}")
    cuts = [class_cutoff(cl) for cl in C.CLASSES]
    cuts = [c for c in cuts if c is not None]
    if cuts and C.DC_FROM_YEAR > min(cuts):
        lines.append(f"  [warn] DC_FROM_YEAR {C.DC_FROM_YEAR} is later than "
                     f"the earliest cutoff {min(cuts)} — events between them "
                     "pass through undeclustered")
    for cl in C.CLASSES:
        sub = df[df["class"] == cl]
        if not len(sub):
            lines.append(f"  {cl}: EMPTY after cutoff")
            continue
        lines.append(
            f"  {cl}: {len(sub)} events, {sub['year'].min():.0f}-"
            f"{sub['year'].max():.1f}, M{sub['mag'].min():.1f}-"
            f"{sub['mag'].max():.1f}  -> Mmax input "
            f"{sub['mag'].max() + C.MMAX_PAD:.1f}")

    txt = "\n".join(lines)
    print(txt)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(txt + "\n")
    return df


def windows(m, method):
    """Space (km) and time (days) windows per magnitude.

    gk74 per Teng & Baker parametrization; uhrhammer and gruenthal per
    van Stiphout et al. (2010).
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
    """GK type-1: seeds in descending magnitude order; unassigned events
    inside the seed's space-time window join its cluster."""
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
                     "parent_depth": round(p.get("depth", np.nan), 1),
                     "dt_days": round((r["year"] - p["year"]) * 365.25, 1),
                     "d_km": round(haversine(r["longitude"], r["latitude"],
                                             p["longitude"], p["latitude"]), 1)})

    if C.DC_KEEP_IDS and "id" in df.columns:
        forced = df["id"].astype(str).isin([str(x) for x in C.DC_KEEP_IDS])
        n_forced = int((forced & ~df["is_mainshock"]).sum())
        df.loc[forced, "is_mainshock"] = True
        if n_forced:
            print(f"  [{method}] DC_KEEP_IDS restored {n_forced} events")
    return df, pd.DataFrame(rows)


def fig_rates(cl, cat, dcs, yr, n_pre):
    """Annual counts and removed fraction, input vs every method."""
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    a1.semilogy(yr, np.maximum(n_pre, 0.5), "k", drawstyle="steps-post",
                label=f"input ({len(cat)})")
    for method, dc in dcs.items():
        n_dc = np.histogram(dc["year"], bins=np.append(yr, yr[-1] + 1))[0]
        lw = 2 if method == C.DC_METHOD else 1
        a1.semilogy(yr, np.maximum(n_dc, 0.5), drawstyle="steps-post",
                    lw=lw, label=f"{method} ({len(dc)})")
        a2.plot(yr, np.where(n_pre > 0, 1 - n_dc / np.maximum(n_pre, 1), 0),
                drawstyle="steps-post", lw=lw)
    a1.legend(fontsize=8)
    a1.set_ylabel("events/yr")
    a2.set_ylabel("fraction removed")
    a2.set_ylim(0, 1)
    a2.set_xlabel("year")
    a1.set_title(f"{cl} declustering (bold = '{C.DC_METHOD}')")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s00_decluster_rates_{cl}.png", dpi=200)
    plt.close(fig)


def fig_map(cl, cat, dc, removed):
    """Map of the class: kept vs removed, plus the M>=DC_MPROT removals.

    This is the domain check — an intra_slab cloud sitting on the trench
    or a slab_deep cloud in the forearc is a classification problem, not
    a declustering one, and it must be caught before Mc is estimated.
    """
    lon0, lon1, lat0, lat1 = C.BBOX
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 8), sharey=True)

    rem = cat[~cat.index.isin(dc.index)]
    a1.plot(rem["longitude"], rem["latitude"], ".", ms=2, alpha=0.25,
            color="0.7", label=f"removed ({len(rem)})")
    a1.plot(dc["longitude"], dc["latitude"], ".", ms=2, alpha=0.5,
            color=COL.get(cl, "tab:blue"), label=f"mainshocks ({len(dc)})")
    big = dc[dc["mag"] >= 7.0]
    a1.plot(big["longitude"], big["latitude"], "k*", ms=9,
            label=f"M>=7 kept ({len(big)})")
    if len(removed):
        a1.plot(removed["lon"], removed["lat"], "rx", ms=9, mew=2,
                label=f"M>={C.DC_MPROT} removed ({len(removed)})")
    a1.set_xlim(lon0, lon1)
    a1.set_ylim(lat0, lat1)
    a1.set_aspect(1 / np.cos(np.radians(0.5 * (lat0 + lat1))))
    a1.set_xlabel("lon")
    a1.set_ylabel("lat")
    a1.legend(fontsize=7, loc="lower left")
    a1.set_title(f"{cl} — map ({C.DC_METHOD})")

    sc = a2.scatter(dc["depth"], dc["latitude"], c=dc["mag"], s=4,
                    cmap="viridis", vmin=4, vmax=8)
    a2.set_xlabel("depth (km)")
    a2.set_title(f"{cl} — depth vs latitude")
    a2.invert_xaxis()
    fig.colorbar(sc, ax=a2, label="M", shrink=0.6)
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s00_decluster_catalog_map_{cl}.png", dpi=200)
    plt.close(fig)


def fig_depth(cl, cat, dc):
    """Depth histogram and depth-vs-time — does declustering bias depth?

    It should not: if the removed population is systematically shallower
    or deeper than the kept one, the GK windows are linking across the
    slab rather than within a class.
    """
    rem = cat[~cat.index.isin(dc.index)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    bins = np.arange(0, max(cat["depth"].max(), 100) + 10, 10)
    a1.hist(cat["depth"], bins=bins, color="0.8", label="input")
    a1.hist(dc["depth"], bins=bins, histtype="step", lw=1.5,
            color=COL.get(cl, "tab:blue"), label="mainshocks")
    a1.set_xlabel("depth (km)")
    a1.set_ylabel("count")
    a1.legend(fontsize=8)
    a1.set_title(f"{cl} — depth distribution")

    a2.plot(cat["year"], cat["depth"], ".", ms=2, alpha=0.2, color="0.7")
    a2.plot(dc["year"], dc["depth"], ".", ms=2, alpha=0.5,
            color=COL.get(cl, "tab:blue"))
    a2.set_xlabel("year")
    a2.set_ylabel("depth (km)")
    a2.invert_yaxis()
    a2.set_title(f"{cl} — depth vs time")

    med_in = cat["depth"].median()
    med_dc = dc["depth"].median()
    a1.axvline(med_in, color="0.5", lw=0.8)
    a1.axvline(med_dc, color="k", lw=0.8, ls="--")
    print(f"  [{cl}] median depth input {med_in:.1f} km -> "
          f"mainshocks {med_dc:.1f} km"
          + ("  (SHIFT > 5 km, check class separation)"
             if abs(med_in - med_dc) > 5 else ""))
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s00_decluster_depth_{cl}.png", dpi=200)
    plt.close(fig)


def fig_overview(df, dcs_by_class):
    """One figure showing the two classes together — the separation the
    whole per-class treatment rests on."""
    lon0, lon1, lat0, lat1 = C.BBOX
    fig, axes = plt.subplots(1, 3, figsize=(14, 7))
    a1, a2, a3 = axes

    for cl in C.CLASSES:
        dc = dcs_by_class[cl]
        a1.plot(dc["longitude"], dc["latitude"], ".", ms=2, alpha=0.4,
                color=COL.get(cl, None), label=cl)
        a2.plot(dc["depth"], dc["latitude"], ".", ms=2, alpha=0.4,
                color=COL.get(cl, None))
        a3.plot(dc["year"], dc["mag"], ".", ms=2, alpha=0.4,
                color=COL.get(cl, None))
    a1.set_xlim(lon0, lon1)
    a1.set_ylim(lat0, lat1)
    a1.set_aspect(1 / np.cos(np.radians(0.5 * (lat0 + lat1))))
    a1.set_xlabel("lon")
    a1.set_ylabel("lat")
    a1.legend(fontsize=8, markerscale=4)
    a1.set_title("mainshock epicenters by class")
    a2.set_xlabel("depth (km)")
    a2.set_ylabel("lat")
    a2.invert_xaxis()
    a2.set_title("depth vs latitude")
    a3.set_xlabel("year")
    a3.set_ylabel("M")
    a3.set_title("magnitude vs time")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "s00_decluster_class_overview.png", dpi=200)
    plt.close(fig)


def main():
    DC_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_classified(DC_DIR / "s00_decluster_input_report.txt",
                         DC_DIR / "s00_decluster_dropped_historical.csv")
    summary, reviews, dcs_by_class = [], [], {}

    for cl in C.CLASSES:
        cat = df[df["class"] == cl].reset_index(drop=True)
        if not len(cat):
            print(f"[skip] {cl}: no events")
            continue
        yr = np.arange(C.DC_FROM_YEAR, int(cat["year"].max()) + 2)
        n_pre = np.histogram(cat[cat["year"] >= C.DC_FROM_YEAR]["year"],
                             bins=np.append(yr, yr[-1] + 1))[0]

        dcs, rev_this = {}, None
        for method in C.DC_METHODS:
            out, rev = run_method(cat, method)
            dc = out[out["is_mainshock"]]
            dc.drop(columns=["year"]).to_csv(
                DC_DIR / f"cat_dc_{cl}_{method}.csv", index=False)
            dcs[method] = dc
            rev.insert(0, "class", cl)
            reviews.append(rev)
            if method == C.DC_METHOD:
                rev_this = rev
            summary.append({"class": cl, "method": method, "n_in": len(out),
                            "n_main": len(dc),
                            "frac_removed": round(1 - len(dc) / max(len(out), 1), 3),
                            "n_M7_main": int((dc["mag"] >= 7.0).sum()),
                            "n_M7_removed": len(rev),
                            "mmax_main": round(float(dc["mag"].max()), 1),
                            "median_depth_main": round(float(dc["depth"].median()), 1)})

        ref = dcs[C.DC_METHOD]
        dcs_by_class[cl] = ref
        fig_rates(cl, cat, dcs, yr, n_pre)
        fig_map(cl, cat, ref, rev_this if rev_this is not None else pd.DataFrame())
        fig_depth(cl, cat, ref)

    if len(dcs_by_class) > 1:
        fig_overview(df, dcs_by_class)

    tab = pd.DataFrame(summary)
    tab.to_csv(DC_DIR / "s00_decluster_summary.csv", index=False)
    rev = pd.concat(reviews, ignore_index=True) if reviews else pd.DataFrame()
    rev.to_csv(DC_DIR / "s00_decluster_removed_large.csv", index=False)

    print("\n" + tab.to_string(index=False))
    print(f"\nremoved M>={C.DC_MPROT}: {len(rev)} -> "
          "s00_decluster_removed_large.csv (review, then fill DC_KEEP_IDS)")
    if len(rev):
        print(rev[rev["method"] == C.DC_METHOD].to_string(index=False))
    print(f"\nwrote {DC_DIR} and figures/s00_decluster_*.png")


if __name__ == "__main__":
    main()