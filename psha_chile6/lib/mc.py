from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def ks(m, dm, p, b, nsim, cap, floor, nmin):
    """KS Mc for one window; windows with fewer than nmin events get the floor."""
    if len(m) < nmin:
        return floor, "floor"
    from seismostats.analysis.estimate_mc import estimate_mc_ks
    m = np.round(np.round(np.asarray(m) / dm) * dm, 6)
    if cap and len(m) > cap:
        m = np.random.default_rng(42).choice(m, cap, replace=False)
    v, cnt = np.unique(m, return_counts=True)
    start = max(v[np.argmax(cnt)] - 0.2, v[0])
    mcs = np.round(np.arange(start, v[-1] - 0.5, dm), 6)
    if not len(mcs):
        return np.nan, "ks_failed"
    mc, _ = estimate_mc_ks(m, delta_m=dm, mcs_test=mcs, p_value_pass=p, b_value=b, n=nsim)
    return (mc, "ks") if mc is not None else (np.nan, "ks_failed")


def _job(a):
    return ks(*a)


def regular(y_start, y_end, step, hist_from=None):
    """Windows: optional historical block hist_from -> y_start, then fixed steps."""
    e = list(range(int(y_start), int(np.ceil(y_end)), int(step)))
    if len(e) > 1 and np.ceil(y_end) - e[-1] < step / 2:
        e.pop()
    e = ([int(hist_from)] if hist_from is not None and hist_from < y_start else []) + e
    return list(zip(e, e[1:] + [int(np.ceil(y_end))]))


def table(df, wins, c):
    """
    KS Mc per window, in parallel.

    Returns
    -------
    DataFrame
        y0, y1, n, mc, how.
    """
    ms = [df[(df["year"] >= y0) & (df["year"] < y1)]["mag"].to_numpy() for y0, y1 in wins]
    args = [(m, c.DM, c.MC_P_VALUE, c.MC_B_FIXED, c.MC_KS_N, c.MC_MAX_SAMPLE,
             c.MC_HIST_FLOOR, c.MC_MIN_EVENTS) for m in ms]
    with ProcessPoolExecutor() as ex:
        res = list(ex.map(_job, args))
    return pd.DataFrame([{"y0": y0, "y1": y1, "n": len(m), "mc": mc, "how": how}
                         for (y0, y1), m, (mc, how) in zip(wins, ms, res)])


def outliers(t, drop, span=2):
    """
    Flag KS windows whose Mc sits more than drop below the median of their
    neighbours. The reverse running maximum in propose would otherwise turn
    one low estimate into a floor for every later window.
    """
    t = t.sort_values("y0").reset_index(drop=True).copy()
    t["outlier"] = False
    if drop is None:
        return t
    idx = np.where(t["how"] == "ks")[0]
    for k in idx:
        near = [j for j in idx if j != k and abs(j - k) <= span]
        if len(near) >= 2 and t.loc[k, "mc"] < np.median(t.loc[near, "mc"]) - drop:
            t.loc[k, "outlier"] = True
    return t


def propose(t):
    """Steps (Mc, since_year): reverse running maximum over window Mc."""
    t = t.dropna(subset=["mc"]).sort_values("y0")
    if "outlier" in t:
        t = t[~t["outlier"]]
    if not len(t):
        return []
    eff = np.maximum.accumulate(t["mc"].to_numpy()[::-1])[::-1]
    steps, last = [], None
    for y0, mc in zip(t["y0"], eff):
        if mc != last:
            steps.append((round(float(mc), 1), int(y0)))
            last = mc
    return steps


def fig(df, t, steps, t_end, path, title):
    f, (ax, ar) = plt.subplots(2, 1, figsize=(11, 6), sharex=True,
                               gridspec_kw={"height_ratios": [3, 1]})
    ax.plot(df["year"], df["mag"], ".", ms=2, alpha=0.3, color="gray")
    for _, r in t.iterrows():
        if np.isfinite(r["mc"]):
            col = "0.6" if r.get("outlier", False) else "crimson"
            ax.hlines(r["mc"], r["y0"], r["y1"], color=col, lw=2,
                      ls="-" if r["how"] == "ks" else ":")
    s = sorted(steps, key=lambda x: x[1])
    for i, (mc, y0) in enumerate(s):
        ax.hlines(mc, y0, s[i + 1][1] if i + 1 < len(s) else t_end, color="k", lw=2.5)
    ax.set_ylim(3, 10)
    ax.set_ylabel("M")
    ax.set_title(title + " (red = window KS, dotted = floor, grey = outlier, black = proposal)",
                 fontsize=9)
    y = np.arange(int(df["year"].min()), int(df["year"].max()) + 2)
    ar.semilogy(y[:-1], np.maximum(np.histogram(df["year"], bins=y)[0], 0.5),
                drawstyle="steps-post", lw=0.8)
    ar.set_xlabel("year")
    ar.set_ylabel("events/yr")
    f.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    f.savefig(path, dpi=200)
    plt.close(f)
