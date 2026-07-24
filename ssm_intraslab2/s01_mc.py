# ssm_intraslab/s01_mc.py
# Completeness per slab class on the UNDECLUSTERED classified catalog
# (detection is a network property; declustered catalogs inherit the
# algorithm's deletions as fake incompleteness — the Mc=6.1@2010 episode).
# Regular windows: one historical block HIST_START_YEAR -> REGULAR_FROM,
# then WINDOW_YEARS steps, so there is no hand-drawn epoch list to drift.
# KS per window (fast settings), per class, in parallel. The proposal is
# pasted BY HAND into ssm_config.COMPLETENESS after reading the figures.
#
# For slab_deep most windows are expected to FLOOR (n < MC_MIN_EVENTS).
# That is honest, not a failure — but it means the proposal for that class
# is mostly floor values and needs hand judgment. Everything below that
# says "floor" is there to make that judgment possible.
#
# Outputs
#   mc/s01_mc_windows.csv               per-window Mc, n, method, coverage
#   mc/s01_mc_completeness_proposal.txt paste target
#   mc/s01_mc_audit.txt                 band-rate audit + floor accounting
#   figures/s01_mc_magtime_{class}.png       Mc steps over the catalog
#   figures/s01_mc_fmd_windows_{class}.png   per-window FMD with Mc marked
#   figures/s01_mc_fmd_proposed_{class}.png  FMD of the proposed table
#   figures/s01_mc_window_counts_{class}.png n per window + floor flags
#   figures/s01_mc_stability_{class}.png     Mc vs window length
#   figures/s01_mc_map_complete_{class}.png  spatial completeness check
#
# requires in ssm_config (in addition to s00's keys):
#   WINDOW_YEARS, REGULAR_FROM, HIST_START_YEAR, DELTA_M, MC_P_VALUE,
#   MC_MIN_EVENTS, MC_B_FIXED, MC_KS_N, MC_MAX_SAMPLE, MC_HIST_FLOOR,
#   PRESENT_YEAR, BBOX

from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from seismostats.analysis.estimate_mc import estimate_mc_ks

import ssm_config as C
from s00_decluster import load_classified, decyear

MC_DIR = C.OUT_DIR / "mc"
COL = {"intra_slab": "tab:blue", "slab_deep": "tab:red"}
STAB_FACTORS = getattr(C, "MC_STAB_FACTORS", [0.5, 1.0, 2.0])


def class_window(cl):
    """Window length for a class: per-class override, else the global."""
    return getattr(C, "WINDOW_YEARS_BY_CLASS", {}).get(cl, C.WINDOW_YEARS)


def class_start(cl):
    """First year of the window sequence.

    With a historical cutoff there is no pre-cutoff data, so the windows
    start there and no historical block is built. Without one, the block
    runs HIST_START_YEAR -> REGULAR_FROM as before.
    """
    cut = getattr(C, "HIST_CUTOFF_BY_CLASS", {}).get(
        cl, getattr(C, "HIST_CUTOFF", None))
    return cut if cut is not None else C.HIST_START_YEAR


def build_windows(y_max, window_years=None, start=None):
    """Historical block then regular steps; the last short window is
    merged into the previous one if it is under half a step. When start
    is at or after REGULAR_FROM the historical block is omitted."""
    w = window_years or C.WINDOW_YEARS
    y0 = int(C.HIST_START_YEAR if start is None else start)
    first = max(int(C.REGULAR_FROM), y0)
    edges = list(range(first, int(y_max) + 1, int(w))) or [first]
    if int(y_max) + 1 - edges[-1] < w / 2 and len(edges) > 1:
        edges.pop()
    ys = ([y0] if y0 < first else []) + edges + [int(np.ceil(y_max))]
    return list(zip(ys[:-1], ys[1:]))


def mc_one(mags):
    """KS Mc for one window. Returns (mc, n_used) with mc None on failure."""
    mags = np.round(np.round(mags / C.DELTA_M) * C.DELTA_M, 6)
    if C.MC_MAX_SAMPLE and len(mags) > C.MC_MAX_SAMPLE:
        mags = np.random.default_rng(42).choice(mags, C.MC_MAX_SAMPLE,
                                                replace=False)
    vals, cnt = np.unique(mags, return_counts=True)
    m0 = max(vals[np.argmax(cnt)] - 0.2, vals[0])
    mcs = np.round(np.arange(m0, vals[-1] - 0.5, C.DELTA_M), 6)
    if not len(mcs):
        return None, len(mags)
    mc, _ = estimate_mc_ks(mags, delta_m=C.DELTA_M, mcs_test=mcs,
                           p_value_pass=C.MC_P_VALUE, b_value=C.MC_B_FIXED,
                           n=C.MC_KS_N)
    return mc, len(mags)


def _win_job(args):
    cl, y0, y1, m = args
    n = len(m)
    if n < C.MC_MIN_EVENTS:
        return (cl, y0, y1, n, n, C.MC_HIST_FLOOR, "floor",
                float(np.max(m)) if n else np.nan)
    mc, n_used = mc_one(m)
    return (cl, y0, y1, n, n_used,
            mc if mc is not None else np.nan,
            "ks" if mc is not None else "ks_failed",
            float(np.max(m)))


def run_windows(df, cl, window_years=None):
    """Run KS on every window of one class. Returns the window table."""
    cat = df[df["class"] == cl]
    w = window_years or class_window(cl)
    jobs = []
    for y0, y1 in build_windows(cat["year"].max(), w, class_start(cl)):
        m = cat[(cat["year"] >= y0) & (cat["year"] < y1)]["mag"].to_numpy()
        jobs.append((cl, y0, y1, m))
    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(_win_job, jobs))
    return pd.DataFrame(rows, columns=["class", "y0", "y1", "n", "n_used",
                                       "mc", "how", "mmax_win"])


def flag_outliers(tab, drop=None, span=2):
    """Mark windows whose KS Mc sits far below their neighbours.

    The proposal takes a reverse running maximum, so a single window with
    a spuriously low Mc becomes a permanent floor for every later window —
    one bad estimate contaminates decades. This flags such windows so they
    can be excluded from the proposal rather than setting the floor.

    Only downward excursions are flagged. A genuine Mc increase (network
    degradation: stations closing, a deployment ending) is a real thing
    the table must be able to express, and it is not an outlier against
    its neighbours in the same way — it persists.

    Parameters
    ----------
    tab : pandas.DataFrame
        Window table with columns y0, mc, how.
    drop : float or None
        How far below the local median counts as suspect, magnitude
        units. Defaults to C.MC_OUTLIER_DROP.
    span : int
        Number of windows either side used for the local median.

    Returns
    -------
    pandas.DataFrame
        Copy of tab with an is_outlier column and mc_neighbour, the local
        median it was compared against.
    """
    drop = getattr(C, "MC_OUTLIER_DROP", 0.4) if drop is None else drop
    t = tab.sort_values("y0").reset_index(drop=True).copy()
    t["mc_neighbour"] = np.nan
    t["is_outlier"] = False
    if drop is None:
        return t
    ks = t["how"] == "ks"
    idx = np.where(ks)[0]
    for k in idx:
        near = [j for j in idx if j != k and abs(j - k) <= span]
        if len(near) < 2:
            continue
        med = float(np.median(t.loc[near, "mc"]))
        t.loc[k, "mc_neighbour"] = med
        if t.loc[k, "mc"] < med - drop:
            t.loc[k, "is_outlier"] = True
    return t


def propose_steps(tab, use_flags=True):
    """Cumulative-from-present completeness steps.

    Magnitude M is complete since the earliest window from which Mc <= M
    holds through to the present — a reverse running maximum over the
    per-window Mc, so a single bad recent window cannot open up an early
    epoch. Windows flagged as outliers are excluded first: the running
    max cannot step back up, so a spuriously low Mc would otherwise pin
    the table for every later window.

    Parameters
    ----------
    tab : pandas.DataFrame
        Window table with columns y0 and mc, optionally is_outlier.
    use_flags : bool
        Exclude windows marked is_outlier.

    Returns
    -------
    list of tuple
        (Mc, since_year) steps, oldest first.
    """
    t = tab.dropna(subset=["mc"]).sort_values("y0")
    if use_flags and "is_outlier" in t.columns:
        t = t[~t["is_outlier"]]
    if not len(t):
        return []
    mc_eff = np.maximum.accumulate(t["mc"].to_numpy()[::-1])[::-1]
    steps, last = [], None
    for y0, mc in zip(t["y0"], mc_eff):
        if mc != last:
            steps.append((round(float(mc), 1), int(y0)))
            last = mc
    return steps


def cum_counts(mags, edges):
    return np.array([(mags >= e).sum() for e in edges], float)


def complete_mask(cat, steps):
    """Boolean mask of events above the completeness table."""
    keep = np.zeros(len(cat), bool)
    yr = cat["year"].to_numpy()
    mg = cat["mag"].to_numpy()
    steps = sorted(steps, key=lambda s: s[1])
    for i, (mc, y0) in enumerate(steps):
        y1 = steps[i + 1][1] if i + 1 < len(steps) else np.inf
        keep |= (yr >= y0) & (yr < y1) & (mg >= mc - 1e-9)
    return keep


def audit_steps(steps, cat, y_end, label, out):
    """Band-rate audit: with a correct table, the rate density per
    magnitude band should not increase toward larger magnitudes."""
    steps = sorted(steps)
    prev = None
    for i, (mc, y0) in enumerate(steps):
        hi = steps[i + 1][0] if i + 1 < len(steps) else 11.0
        n = ((cat["mag"] >= mc) & (cat["mag"] < hi) & (cat["year"] >= y0)).sum()
        r = n / (y_end - y0 + 1) / max(hi - mc, C.DELTA_M)
        if prev is not None and r > 1.3 * prev:
            msg = (f"[audit:{label}] band {mc}-{hi} rate density rises "
                   f"{prev:.3g} -> {r:.3g} (>30%) — step likely too low")
            print(msg)
            out.append(msg)
        prev = r


def fig_magtime(cl, cat, tab, steps):
    """Magnitude-time with the window Mc, the proposed table, and an
    annual-count panel. Pre-REGULAR_FROM events are drawn distinctly:
    they carry the historical block and are the ones most likely to be
    misclassified or depth-defaulted."""
    fig, (ax, ar) = plt.subplots(2, 1, figsize=(12, 7), sharex=True,
                                 gridspec_kw={"height_ratios": [3, 1]})
    hist = cat[cat["year"] < C.REGULAR_FROM]
    inst = cat[cat["year"] >= C.REGULAR_FROM]
    ax.plot(inst["year"], inst["mag"], ".", ms=2, alpha=0.3, color="gray")
    if len(hist):
        ax.plot(hist["year"], hist["mag"], "o", ms=5, mfc="none",
                color="crimson", mew=1.2,
                label=f"pre-{C.REGULAR_FROM} ({len(hist)})")
    for _, r in tab.iterrows():
        if np.isfinite(r["mc"]):
            flagged = bool(r.get("is_outlier", False))
            ls = "-" if r["how"] == "ks" else ":"
            ax.hlines(r["mc"], r["y0"], r["y1"],
                      color="0.6" if flagged else "crimson", ls=ls, lw=2)
            if flagged:
                ax.plot(0.5 * (r["y0"] + r["y1"]), r["mc"], "x", ms=9,
                        mew=2, color="k", zorder=6)
        ax.axvline(r["y0"], color="k", lw=0.3, alpha=0.3)
    ss = sorted(steps, key=lambda s: s[1])
    for i, (mc, y0) in enumerate(ss):
        y1 = ss[i + 1][1] if i + 1 < len(ss) else C.PRESENT_YEAR
        ax.hlines(mc, y0, y1, color="k", lw=2.5, zorder=5)
    ax.set_ylabel("M")
    ax.set_ylim(3.0, 10)
    if len(hist):
        ax.legend(fontsize=8, loc="upper left")
    ax.set_title(f"{cl}: KS Mc per {class_window(cl)}-yr window "
                 "(red solid=KS, red dotted=floor, grey x=outlier excluded, "
                 "black=proposed table)")

    yrs = np.arange(int(cat["year"].min()), int(cat["year"].max()) + 2)
    n = np.histogram(cat["year"], bins=np.append(yrs, yrs[-1] + 1))[0]
    ar.semilogy(yrs, np.maximum(n, 0.5), drawstyle="steps-post",
                color=COL.get(cl, "tab:blue"), lw=0.8)
    ar.set_xlabel("year")
    ar.set_ylabel("events/yr")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s01_mc_magtime_{cl}.png", dpi=200)
    plt.close(fig)


def fig_fmd_windows(cl, cat, tab):
    """Per-window FMD with the KS Mc marked — the plot that shows whether
    a window's Mc sits at the actual roll-off or has been pushed up by the
    KS over-rejection at large n."""
    t = tab.reset_index(drop=True)
    n = len(t)
    ncol = 4
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.2 * ncol, 2.6 * nrow),
                             squeeze=False)
    edges = np.arange(3.0, 9.5, C.DELTA_M)
    for k, r in t.iterrows():
        ax = axes[k // ncol][k % ncol]
        m = cat[(cat["year"] >= r["y0"]) & (cat["year"] < r["y1"])]["mag"]
        if len(m):
            ax.semilogy(edges, np.maximum(cum_counts(m.to_numpy(), edges), 0.5),
                        ".", ms=3, color=COL.get(cl, "tab:blue"))
        if np.isfinite(r["mc"]):
            ax.axvline(r["mc"], color="crimson",
                       ls="-" if r["how"] == "ks" else ":", lw=1.5)
        flagged = bool(r.get("is_outlier", False))
        if flagged and np.isfinite(r.get("mc_neighbour", np.nan)):
            ax.axvline(r["mc_neighbour"], color="k", ls="--", lw=1.2)
        ax.set_title(f"{int(r['y0'])}-{int(r['y1'])}  n={int(r['n'])} "
                     f"{r['how']}" + ("  OUTLIER" if flagged else ""),
                     fontsize=7,
                     color="crimson" if flagged else "black")
        ax.tick_params(labelsize=6)
        ax.set_ylim(0.5, None)
    for k in range(n, nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")
    fig.suptitle(f"{cl}: per-window FMD, N(>=M), KS Mc in red", fontsize=10)
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s01_mc_fmd_windows_{cl}.png", dpi=180)
    plt.close(fig)


def fig_fmd_proposed(cl, cat, steps):
    """FMD of the events the proposed table declares complete, plotted as
    time-normalized rates, with a b=1 reference. If the proposal is sane
    the points sit on a line; a bend at the low end means a step is too
    low, an offset between epochs means a step is misdated."""
    fig, ax = plt.subplots(figsize=(7, 5))
    edges = np.arange(3.5, 9.0, C.DELTA_M)
    y_end = C.PRESENT_YEAR
    ss = sorted(steps, key=lambda s: s[1])

    keep = complete_mask(cat, steps)
    sub = cat[keep]
    # per-epoch rates, each normalized by its own usable duration
    for i, (mc, y0) in enumerate(ss):
        y1 = ss[i + 1][1] if i + 1 < len(ss) else y_end
        dur = max(y1 - y0, 1e-6)
        m = cat[(cat["year"] >= y0) & (cat["year"] < y1)
                & (cat["mag"] >= mc - 1e-9)]["mag"].to_numpy()
        if len(m) < 3:
            continue
        e = edges[edges >= mc - 1e-9]
        ax.semilogy(e, cum_counts(m, e) / dur, "o", ms=3, alpha=0.6,
                    label=f"{int(y0)}-{int(y1)} Mc={mc}")

    # the pooled curve the rate fit will actually see
    tot = np.zeros(len(edges))
    for i, (mc, y0) in enumerate(ss):
        y1 = ss[i + 1][1] if i + 1 < len(ss) else y_end
        m = cat[(cat["year"] >= y0) & (cat["year"] < y1)
                & (cat["mag"] >= mc - 1e-9)]["mag"].to_numpy()
        # each magnitude bin gets the duration over which it is complete
        for j, e in enumerate(edges):
            if e >= mc - 1e-9 and len(m):
                tot[j] += (m >= e).sum() / max(y_end - y0, 1e-6)
    ax.semilogy(edges, np.maximum(tot, 1e-6), "k-", lw=1.5,
                label="completeness-weighted")

    if len(ss):
        m_ref = ss[-1][0]
        r_ref = max(tot[np.argmin(np.abs(edges - m_ref))], 1e-6)
        ax.semilogy(edges, r_ref * 10 ** (-1.0 * (edges - m_ref)), "k--",
                    lw=0.8, label="b = 1 reference")
    ax.set_xlabel("M")
    ax.set_ylabel("N(>=M) per year")
    ax.set_ylim(1e-4, None)
    ax.legend(fontsize=7)
    ax.set_title(f"{cl}: FMD under the proposed completeness table "
                 f"({int(keep.sum())} events)")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s01_mc_fmd_proposed_{cl}.png", dpi=200)
    plt.close(fig)


def fig_window_counts(cl, tab):
    """n per window with the floor threshold — the direct read on how much
    of this class's table is estimated and how much is assumed."""
    fig, ax = plt.subplots(figsize=(10, 4))
    x = tab["y0"].to_numpy()
    w = (tab["y1"] - tab["y0"]).to_numpy()
    colors = ["crimson" if h != "ks" else COL.get(cl, "tab:blue")
              for h in tab["how"]]
    ax.bar(x, np.maximum(tab["n"], 0.5), width=w * 0.9, align="edge",
           color=colors, alpha=0.8)
    ax.axhline(C.MC_MIN_EVENTS, color="k", ls="--", lw=1,
               label=f"MC_MIN_EVENTS = {C.MC_MIN_EVENTS}")
    if C.MC_MAX_SAMPLE:
        ax.axhline(C.MC_MAX_SAMPLE, color="0.4", ls=":", lw=1,
                   label=f"MC_MAX_SAMPLE = {C.MC_MAX_SAMPLE}")
    ax.set_yscale("log")
    ax.set_xlabel("window start year")
    ax.set_ylabel("events in window")
    ax.legend(fontsize=8)
    n_floor = int((tab["how"] != "ks").sum())
    ax.set_title(f"{cl}: window sizes — {n_floor}/{len(tab)} floored "
                 "(red = floor/failed)")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s01_mc_window_counts_{cl}.png", dpi=200)
    plt.close(fig)


def fig_stability(cl, df, tabs_by_w):
    """Mc(t) under different window lengths. A step that survives halving
    and doubling the window is a network change; one that moves with the
    window is a sampling artifact and should not become a step."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for w, tab in tabs_by_w.items():
        t = tab[tab["how"] == "ks"]
        ax.step(t["y0"], t["mc"], where="post", lw=1.5,
                label=f"{int(w)}-yr windows (n_ks={len(t)})")
    ax.set_xlabel("year")
    ax.set_ylabel("KS Mc")
    ax.legend(fontsize=8)
    ax.set_title(f"{cl}: Mc stability vs window length "
                 "(floored windows omitted)")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s01_mc_stability_{cl}.png", dpi=200)
    plt.close(fig)


def fig_map_complete(cl, cat, steps):
    """Where the complete events are. Completeness is estimated nationally
    per class but detection is regional — a table that leaves the far south
    or the deep north empty is a table that will bias the smoothed field."""
    lon0, lon1, lat0, lat1 = C.BBOX
    keep = complete_mask(cat, steps)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 7))
    a1.plot(cat["longitude"], cat["latitude"], ".", ms=1.5, alpha=0.15,
            color="0.7", label=f"all ({len(cat)})")
    a1.plot(cat[keep]["longitude"], cat[keep]["latitude"], ".", ms=2,
            alpha=0.5, color=COL.get(cl, "tab:blue"),
            label=f"complete ({int(keep.sum())})")
    a1.set_xlim(lon0, lon1)
    a1.set_ylim(lat0, lat1)
    a1.set_aspect(1 / np.cos(np.radians(0.5 * (lat0 + lat1))))
    a1.set_xlabel("lon")
    a1.set_ylabel("lat")
    a1.legend(fontsize=8, markerscale=4, loc="lower left")
    a1.set_title(f"{cl}: events above the proposed table")

    lat_bins = np.arange(np.floor(lat0), np.ceil(lat1) + 1, 1.0)
    n_all = np.histogram(cat["latitude"], bins=lat_bins)[0]
    n_ok = np.histogram(cat[keep]["latitude"], bins=lat_bins)[0]
    ctr = 0.5 * (lat_bins[:-1] + lat_bins[1:])
    a2.barh(ctr, n_all, height=0.9, color="0.85", label="all")
    a2.barh(ctr, n_ok, height=0.9, color=COL.get(cl, "tab:blue"),
            label="complete")
    a2.set_ylim(lat0, lat1)
    a2.set_xscale("log")
    a2.set_xlabel("events")
    a2.set_ylabel("lat")
    a2.legend(fontsize=8)
    a2.set_title("per-degree latitude counts")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s01_mc_map_complete_{cl}.png", dpi=200)
    plt.close(fig)


def fig_historical(cl, cat, out):
    """Pre-REGULAR_FROM events: are they real, or catalog artifacts?

    Deep historical events are intrinsically suspect — a 200-300 km event
    located before instrumental recording has no depth constraint, so its
    depth is whatever the catalog compiler defaulted to. Three reads here:
    depth values (defaults show as spikes), magnitude-time (a flat line of
    identical magnitudes is a compiler convention), and the source column
    if the catalog carries one.
    """
    hist = cat[cat["year"] < C.REGULAR_FROM]
    cut = class_start(cl)
    if not len(hist):
        out.append(f"[historical] {cl}: no pre-{C.REGULAR_FROM} events "
                   f"(cutoff {cut}) — historical block absent by construction")
        return
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    (a1, a2), (a3, a4) = axes

    a1.plot(cat["year"], cat["mag"], ".", ms=2, alpha=0.2, color="0.7")
    a1.plot(hist["year"], hist["mag"], "o", ms=5, color="crimson",
            label=f"pre-{C.REGULAR_FROM} ({len(hist)})")
    a1.axvline(C.REGULAR_FROM, color="k", lw=1, ls="--")
    a1.axvline(1677, color="tab:orange", lw=1, ls=":",
               label="1677 (pandas floor)")
    a1.set_xlabel("year")
    a1.set_ylabel("M")
    a1.legend(fontsize=8)
    a1.set_title(f"{cl}: magnitude vs time, historical highlighted")

    a2.plot(hist["year"], hist["depth"], "o", ms=5, color="crimson")
    a2.set_xlabel("year")
    a2.set_ylabel("depth (km)")
    a2.invert_yaxis()
    a2.set_title("historical events: depth vs year")

    # depth-value spikes = compiler defaults, not measurements
    vc = hist["depth"].round(1).value_counts().head(12)
    a3.barh([str(v) for v in vc.index], vc.to_numpy(), color="crimson")
    a3.set_xlabel("count")
    a3.set_ylabel("depth (km)")
    a3.set_title("most common historical depth values")

    a4.hist(cat["depth"], bins=30, color="0.85", label="all")
    a4.hist(hist["depth"], bins=30, color="crimson", alpha=0.8,
            label=f"pre-{C.REGULAR_FROM}")
    a4.set_xlabel("depth (km)")
    a4.set_ylabel("count")
    a4.legend(fontsize=8)
    a4.set_title("depth distribution")

    fig.tight_layout()
    fig.savefig(C.FIG_DIR / f"s01_mc_historical_{cl}.png", dpi=200)
    plt.close(fig)

    # the table, so the events can be looked up one by one
    cols = [c for c in ["id", "year", "mag", "latitude", "longitude", "depth",
                        "class", "source", "catalog", "mag_type", "time_iso"]
            if c in hist.columns]
    tab = hist[cols].sort_values("year")
    tab.to_csv(MC_DIR / f"s01_mc_historical_{cl}.csv", index=False)

    out.append(f"[historical] {cl}: {len(hist)} events before "
               f"{C.REGULAR_FROM}, {int((hist['year'] < 1677).sum())} before 1677")
    top = vc.head(3)
    frac = top.sum() / len(hist)
    out.append(f"[historical] {cl}: most common depths "
               + ", ".join(f"{d} km x{n}" for d, n in top.items())
               + f" = {100 * frac:.0f}% of historical events")
    if frac > 0.5 and len(hist) > 5:
        msg = (f"[warn] {cl}: over half the historical events share a few "
               "exact depth values — these look like catalog defaults, not "
               "measurements. Depth-based classification cannot be trusted "
               "for them (feeds the pre-1930 policy decision).")
        print(msg)
        out.append(msg)
    if "source" in hist.columns:
        out.append(f"[historical] {cl}: sources "
                   + ", ".join(f"{s}={n}" for s, n
                               in hist["source"].value_counts().items()))


def load_declustered():
    """Per-class declustered catalogs from s00, concatenated.

    s00 writes one file per class and method; this reassembles them into
    the same shape load_classified returns, so the window machinery does
    not care which basis it is given.

    Returns
    -------
    pandas.DataFrame or None
        Rows with year, mag and class; None if the files are missing.
    """
    dc_dir = C.OUT_DIR / "decluster"
    parts = []
    for cl in C.CLASSES:
        p = dc_dir / f"cat_dc_{cl}_{C.DC_METHOD}.csv"
        if not p.exists():
            print(f"[dc] missing {p} — run s00_decluster first")
            return None
        d = pd.read_csv(p)
        if "year" not in d.columns:
            d["year"] = [decyear(str(s)) for s in d["time_iso"]]
        d["class"] = cl
        parts.append(d)
    df = pd.concat(parts, ignore_index=True)
    return df[np.isfinite(df["year"]) & df["mag"].notna()].reset_index(drop=True)


def fig_mc_basis(cl, tab_un, tab_dc, path):
    """Per-window Mc on the undeclustered vs declustered catalog.

    Mc is estimated on the UNdeclustered catalog because detection is a
    network property, but the rates are fitted on the DEclustered one. In
    windows containing a large aftershock sequence the two bases disagree
    badly: the sequence supplies many well-recorded small events, so the
    undeclustered roll-off drops, and the table then claims a completeness
    the declustered catalog cannot support. This figure shows where that
    happens — the windows where the curves separate are the ones driving
    the fit.
    """
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                                 gridspec_kw={"height_ratios": [2, 1]})
    for tab, lab, c in [(tab_un, "undeclustered", "tab:blue"),
                        (tab_dc, "declustered", "tab:red")]:
        t = tab[tab["how"] == "ks"]
        a1.step(t["y0"], t["mc"], where="post", lw=1.8, color=c, label=lab)
        a1.plot(t["y0"], t["mc"], "o", ms=4, color=c)
    a1.set_ylabel("KS Mc")
    a1.legend(fontsize=9)
    a1.set_title(f"{cl}: Mc basis comparison "
                 "(gaps = floored windows, omitted)")

    m = tab_un[["y0", "n", "mc"]].merge(tab_dc[["y0", "n", "mc"]], on="y0",
                                        suffixes=("_un", "_dc"))
    m["d_mc"] = m["mc_dc"] - m["mc_un"]
    m["frac_dep"] = 1 - m["n_dc"] / m["n_un"].clip(lower=1)
    a2.bar(m["y0"], m["d_mc"], width=8, align="edge", color="0.5",
           label="Mc(dc) - Mc(undc)")
    a2b = a2.twinx()
    a2b.plot(m["y0"] + 4, m["frac_dep"], "k.-", lw=1, ms=5,
             label="fraction removed by declustering")
    a2.axhline(0, color="k", lw=0.8)
    a2.set_xlabel("window start year")
    a2.set_ylabel("dMc")
    a2b.set_ylabel("frac. dependent")
    a2b.set_ylim(0, 1)
    h1, l1 = a2.get_legend_handles_labels()
    h2, l2 = a2b.get_legend_handles_labels()
    a2.legend(h1 + h2, l1 + l2, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return m


def main():
    MC_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_classified()
    y_end = float(np.ceil(df["year"].max()))
    audit = [f"# s01_mc audit — catalog ends {y_end:.0f}, "
             f"PRESENT_YEAR = {C.PRESENT_YEAR}"]
    if abs(y_end - C.PRESENT_YEAR) > 1.5:
        msg = (f"[warn] catalog end {y_end:.0f} vs PRESENT_YEAR "
               f"{C.PRESENT_YEAR} — rates use PRESENT_YEAR, check the offset")
        print(msg)
        audit.append(msg)

    # Mc basis: undeclustered by default (detection is a network property),
    # but the rates are fitted on the declustered catalog, so a window
    # containing a big aftershock sequence can hand the table a
    # completeness the fit cannot support. MC_COMPARE_BASIS runs both and
    # shows where they disagree; MC_ON_DECLUSTERED picks which one is used.
    df_dc = None
    if getattr(C, "MC_COMPARE_BASIS", True) or getattr(C, "MC_ON_DECLUSTERED", False):
        df_dc = load_declustered()
        if df_dc is None:
            print("[dc] basis comparison skipped")

    tabs, proposals, tabs_dc = {}, {}, {}
    for cl in C.CLASSES:
        cat = df[df["class"] == cl]
        if not len(cat):
            print(f"[skip] {cl}: no events")
            continue
        top = cat.nlargest(5, "mag")
        line = (f"[top events] {cl}: "
                + ", ".join(f"M{r.mag:.1f}@{r.year:.0f}(z{r.depth:.0f})"
                            for r in top.itertuples()))
        print(line)
        audit.append(line)
        if float(top["mag"].max()) + C.MMAX_PAD > C.MMAX_SANITY:
            msg = (f"[warn] {cl}: M_obs {top['mag'].max():.1f} + pad exceeds "
                   f"MMAX_SANITY {C.MMAX_SANITY} — classification intruder?")
            print(msg)
            audit.append(msg)

        tab_un = flag_outliers(run_windows(df, cl))
        tab_dc = None
        if df_dc is not None and (df_dc["class"] == cl).any():
            tab_dc = flag_outliers(run_windows(df_dc, cl))
            tabs_dc[cl] = tab_dc
            m = fig_mc_basis(cl, tab_un, tab_dc,
                             C.FIG_DIR / f"s01_mc_basis_{cl}.png")
            m.insert(0, "class", cl)
            big = m[m["d_mc"].abs() >= 0.3]
            line = (f"[basis] {cl}: median dMc(dc-undc) = "
                    f"{m['d_mc'].median():+.2f}, "
                    f"{len(big)}/{len(m)} windows differ by >=0.3")
            print(line)
            audit.append(line)
            for _, r in big.iterrows():
                line = (f"[basis] {cl}: {int(r['y0'])} Mc {r['mc_un']:.1f} -> "
                        f"{r['mc_dc']:.1f} (dc removed "
                        f"{100 * r['frac_dep']:.0f}% of {int(r['n_un'])})")
                print(line)
                audit.append(line)

        use_dc = getattr(C, "MC_ON_DECLUSTERED", False) and tab_dc is not None
        tabs[cl] = tab_dc if use_dc else tab_un

    basis = ("DECLUSTERED" if getattr(C, "MC_ON_DECLUSTERED", False)
             else "undeclustered")
    line = f"[basis] proposals below are estimated on the {basis} catalog"
    print(line)
    audit.append(line)

    if not tabs:
        raise SystemExit("no classes with events — check CAT_CLASSIFIED")

    full = pd.concat(tabs.values(), ignore_index=True)
    full.to_csv(MC_DIR / "s01_mc_windows.csv", index=False)
    if tabs_dc:
        pd.concat(tabs_dc.values(), ignore_index=True).to_csv(
            MC_DIR / "s01_mc_windows_declustered.csv", index=False)

    txt = ["# PROPOSAL from s01_mc — read figures/s01_mc_*.png, EDIT BY HAND,",
           "# then paste into ssm_config.COMPLETENESS. Steps: (Mc, since_year).",
           "# Floored windows carry MC_HIST_FLOOR, not an estimate: any step",
           "# derived only from floored windows is an assumption, not a result.",
           "COMPLETENESS = {"]

    for cl, tab in tabs.items():
        cat = df[df["class"] == cl]
        steps = propose_steps(tab)
        proposals[cl] = steps

        # what the flagging changed: if excluding a window moves the table,
        # that window was carrying a decade of completeness on its own
        out = tab[tab["is_outlier"]]
        if len(out):
            for _, r in out.iterrows():
                line = (f"[outlier] {cl}: window {int(r['y0'])}-{int(r['y1'])} "
                        f"Mc={r['mc']:.1f} vs neighbours {r['mc_neighbour']:.1f} "
                        f"(n={int(r['n'])}) — EXCLUDED from the proposal")
                print(line)
                audit.append(line)
            raw = propose_steps(tab, use_flags=False)
            if raw != steps:
                line = (f"[outlier] {cl}: table WITH the flagged window(s) "
                        f"would be {raw}")
                print(line)
                audit.append(line)
                print(f"[outlier] {cl}: check figures/s01_mc_fmd_windows_{cl}"
                      ".png for those windows before accepting either")
            else:
                audit.append(f"[outlier] {cl}: flagging did not change the table")

        n_floor = int((tab["how"] != "ks").sum())
        n_fail = int((tab["how"] == "ks_failed").sum())
        floor_years = tab[tab["how"] != "ks"]["y0"].tolist()
        line = (f"[floors] {cl}: {n_floor}/{len(tab)} windows floored "
                f"({n_fail} KS failures) at {C.MC_HIST_FLOOR}; "
                f"start years {floor_years}")
        print(line)
        audit.append(line)
        if n_floor > 0.5 * len(tab):
            msg = (f"[warn] {cl}: over half the windows are floored — the "
                   "proposal is mostly assumption; widen this class via "
                   f"WINDOW_YEARS_BY_CLASS['{cl}'] (now {class_window(cl)}) "
                   "or accept a coarse table")
            print(msg)
            audit.append(msg)

        audit_steps(steps, cat, y_end, cl, audit)
        keep = complete_mask(cat, steps)
        line = (f"[proposal] {cl}: {steps}  -> {int(keep.sum())}/{len(cat)} "
                f"events complete ({100 * keep.mean():.1f}%)")
        print(line)
        audit.append(line)
        if steps and steps[-1][0] > C.MC_MIN_FIT:
            msg = (f"[warn] {cl}: lowest step {steps[-1][0]} is above "
                   f"MC_MIN_FIT {C.MC_MIN_FIT} — the rate fit floor is "
                   "below the completeness table")
            print(msg)
            audit.append(msg)

        txt.append(f'    "{cl}": {steps},')

        fig_magtime(cl, cat, tab, steps)
        fig_historical(cl, cat, audit)
        fig_fmd_windows(cl, cat, tab)
        fig_fmd_proposed(cl, cat, steps)
        fig_window_counts(cl, tab)
        fig_map_complete(cl, cat, steps)

        w0 = class_window(cl)
        tabs_by_w = {}
        for f in STAB_FACTORS:
            w = max(int(round(w0 * f)), 1)
            tabs_by_w[w] = tab if w == w0 else run_windows(df, cl, w)
        fig_stability(cl, df, tabs_by_w)

    txt.append("}")
    (MC_DIR / "s01_mc_completeness_proposal.txt").write_text("\n".join(txt) + "\n")
    (MC_DIR / "s01_mc_audit.txt").write_text("\n".join(audit) + "\n")

    print(f"\nwrote {MC_DIR} and figures/s01_mc_*.png")
    print("NEXT: read the figures, edit the proposal, paste into "
          "ssm_config.COMPLETENESS")


if __name__ == "__main__":
    main()