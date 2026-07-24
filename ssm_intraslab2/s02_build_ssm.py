# ssm_intraslab/s02_build_ssm.py
# In-slab smoothed-seismicity model by per-class superposition.
#
# Each class is smoothed from its OWN declustered catalog and scaled by its
# OWN Weichert (a, b) and Mmax; the total SSM is the per-bin sum of the class
# fields. Domain membership is a property of the events, not of the cells, so
# the total field is continuous across class boundaries (no seams).
#
# Classes come from ssm_config.CLASSES. deep_nest (the Jujuy cluster) is fit
# separately so its recurrence does not contaminate the distributed slab
# statistics: it carries its own Mmax and its own (a, b), and its kernel is
# widened via KERNEL_BY_CLASS so the adaptive bandwidth does not collapse
# onto the cluster and spike the field.
#
# Completeness comes from ssm_config.COMPLETENESS, hand-approved from s01_mc.
# Weichert (1980) handles the unequal observation periods.
#
# Guards (keep them):
#   [mmax]  hard stop when a class Mmax exceeds MMAX_SANITY without an
#           override — the 1575-style intruder check at build time, not in
#           the hazard maps
#   observed-vs-model MFD overlay per class — the validation that would have
#           caught the 1.83-slope episode when it happened
#   rate check assert — the binned field must total the truncated-GR
#           expectation

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ssm_config as C
from ssm_lib import (load_catalog, completeness_steps, obs_periods, weichert,
                     completeness_audit, usable_windows, event_weights,
                     adaptive_kernel, smooth_field, mag_edges, tgr_bins,
                     write_mfd_grid, write_raster, safe_log10, plot_class_fit,
                     plot_total_mfd, plot_rate_map)


def class_mmax(name: str, cat: pd.DataFrame) -> float:
    """Mmax for one class, with the sanity guard.

    Mmax is observed maximum plus MMAX_PAD, per class, so a misclassified
    large event sets the top of that class's MFD off a depth nobody
    measured. MMAX_SANITY stops the build instead: the global in-slab
    record is Chiapas 2017 M8.2, so anything above that plus a pad needs
    an explicit MMAX_OVERRIDE entry and a reason.

    Parameters
    ----------
    name : str
        Class name as used in C.CLASSES.
    cat : pandas.DataFrame
        That class's declustered catalog.

    Returns
    -------
    float
        Mmax, magnitude units.
    """
    if name in C.MMAX_OVERRIDE:
        m = float(C.MMAX_OVERRIDE[name])
        print(f"[mmax] {name}: OVERRIDE {m:.2f} "
              f"(observed {cat['mag'].max():.2f})")
        return m
    m = float(cat["mag"].max()) + C.MMAX_PAD
    if m > C.MMAX_SANITY:
        top = cat.nlargest(5, "mag")
        print(f"[mmax] {name}: top events")
        for r in top.itertuples():
            yr = getattr(r, "year", np.nan)
            dep = getattr(r, "depth", np.nan)
            print(f"    M{r.mag:.1f} @ {yr:.0f} z{dep:.0f} km")
        raise SystemExit(
            f"[mmax] {name}: Mmax {m:.2f} exceeds MMAX_SANITY "
            f"{C.MMAX_SANITY:.2f}. The largest event is M{cat['mag'].max():.1f} "
            "— check it is really in this class before continuing. If it is, "
            f'set MMAX_OVERRIDE["{name}"] with a reason.')
    return m


def kernel_params(name: str) -> dict:
    """Kernel settings for one class: config default, per-class override.

    A spatially concentrated class (a deep nest) collapses the adaptive
    bandwidth onto its own cluster density and spikes the smoothed field,
    so C.KERNEL_BY_CLASS can raise the floor or change the neighbour count
    for that class alone.

    Parameters
    ----------
    name : str
        Class name as used in C.CLASSES.

    Returns
    -------
    dict
        N_NEIGHBORS, MIN_KERNEL_KM, KERNEL_POWER, MAX_EVENT_GRID_DIST_KM.
    """
    p = {"N_NEIGHBORS": C.N_NEIGHBORS,
         "MIN_KERNEL_KM": C.MIN_KERNEL_KM,
         "KERNEL_POWER": C.KERNEL_POWER,
         "MAX_EVENT_GRID_DIST_KM": C.MAX_EVENT_GRID_DIST_KM}
    p.update(getattr(C, "KERNEL_BY_CLASS", {}).get(name, {}))
    return p


def fit_floor(name: str) -> float:
    """Weichert fit floor for one class, with per-class override."""
    return getattr(C, "MC_MIN_FIT_BY_CLASS", {}).get(name, C.MC_MIN_FIT)


def fit_class(name: str, cat: pd.DataFrame, mmin: float = None) -> dict:
    """Weichert (a, b) for one class catalog.

    Prints the completeness audit, then keeps only the windows the class
    can support (C.MIN_EVENTS_PER_WINDOW). b_err is bootstrapped, so a
    class leaning on sparse windows shows a large error here rather than
    an optimistic b/sqrt(N).
    """
    mmin = fit_floor(name) if mmin is None else mmin
    steps = completeness_steps(C.COMPLETENESS[name], C.PRESENT_YEAR)
    completeness_audit(cat, steps, name)
    use = usable_windows(cat, steps, mmin, C.MIN_EVENTS_PER_WINDOW, name)
    if len(use) == 0:
        raise ValueError(f"[fit_class] {name}: no usable completeness window; "
                         "pool it with another class via B_SOURCE and set "
                         "its rate from a coarser window")
    sel = cat[cat["mag"] >= mmin]
    per = obs_periods(sel["mag"].to_numpy(), use)
    good = np.isfinite(per)
    wch = weichert(sel.loc[good, "mag"].to_numpy(), per[good],
                   mmin=mmin, dm=C.DM)
    wch["mags_fit"] = sel.loc[good, "mag"].to_numpy()
    wch["per_fit"] = per[good]
    wch["n_win_used"] = len(use)
    wch["mmin_fit"] = mmin
    print(f"[fit_class] {name}: N={wch['N']} in {len(use)} window(s), "
          f"mmin_fit={mmin:.2f}, "
          f"b={wch['b']:.3f}+/-{wch['b_err']:.3f} (bootstrap), "
          f"rate(M>={wch['mmin']:.2f})={wch['rate_mmin']:.4f}/yr")
    if wch["b_err"] > C.B_ERR_WARN:
        print(f"[fit_class] WARNING: {name} b_err={wch['b_err']:.3f} > "
              f"{C.B_ERR_WARN}; consider borrowing/pooling b via B_SOURCE")
    if not 0.5 <= wch["b"] <= 1.5:
        print(f"[fit_class] WARNING: {name} b={wch['b']:.3f} is outside "
              "0.5-1.5 — check the completeness table and the fit floor "
              "against figures/s02_bstab_*.png and s02_mfd_obs_*.png")
    return wch


def b_stability(name: str, cat: pd.DataFrame, floors: np.ndarray) -> pd.DataFrame:
    """b as a function of the fit floor.

    The diagnostic for choosing MC_MIN_FIT: a floor inside the complete
    range gives a stable b, while a floor below completeness drags b up
    because the missing small events steepen the apparent slope. Look for
    the plateau.
    """
    rows = []
    for m in floors:
        try:
            w = fit_class(name, cat, mmin=float(m))
            rows.append({"mmin_fit": m, "b": w["b"], "b_err": w["b_err"],
                         "N": w["N"]})
        except Exception:
            rows.append({"mmin_fit": m, "b": np.nan, "b_err": np.nan, "N": 0})
    return pd.DataFrame(rows)


def plot_b_stability(name: str, tab: pd.DataFrame, path):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ok = tab.dropna(subset=["b"])
    ax.errorbar(ok["mmin_fit"], ok["b"], yerr=ok["b_err"], fmt="o-", ms=4,
                lw=1.2, capsize=3, color="tab:blue")
    ax.axhline(1.0, color="0.6", lw=0.8, ls=":")
    ax.axvline(fit_floor(name), color="crimson", lw=1.2, ls="--",
               label=f"MC_MIN_FIT = {fit_floor(name):.2f}")
    for _, r in ok.iterrows():
        ax.annotate(f"{int(r['N'])}", (r["mmin_fit"], r["b"]), fontsize=6,
                    textcoords="offset points", xytext=(0, 7), ha="center")
    ax.set_xlabel("fit floor (magnitude)")
    ax.set_ylabel("b")
    ax.legend(fontsize=8)
    ax.set_title(f"{name}: b vs fit floor (labels = N in fit)")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_obs_vs_model(name: str, cat: pd.DataFrame, rb: np.ndarray,
                      edges: np.ndarray, wch: dict, mmax: float, path):
    """Observed completeness-corrected MFD against the model MFD.

    THE validation for this pipeline. The model curve is the summed field
    (what the hazard actually sees); the observed points are counts over
    each magnitude's usable period. If the model sits above the
    observations at the low end, or the slopes disagree, the fit or the
    completeness table is wrong — this is the figure that would have
    caught the 1.83-slope episode at build time.
    """
    steps = completeness_steps(C.COMPLETENESS[name], C.PRESENT_YEAR)
    mags = cat["mag"].to_numpy()
    per = obs_periods(mags, steps)
    centers = 0.5 * (edges[:-1] + edges[1:])

    obs_m, obs_r = [], []
    for e in np.arange(edges[0], min(mmax, mags.max()) + 1e-9, 5 * C.DM):
        s = (mags >= e) & np.isfinite(per)
        if s.sum() < 3:
            continue
        # each event counts once per year it could have been observed
        obs_m.append(e)
        obs_r.append(np.sum(1.0 / per[s]))

    model_cum = np.cumsum(rb.sum(axis=0)[::-1])[::-1]

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.semilogy(centers, np.maximum(model_cum, 1e-8), "-", lw=2,
                color="tab:blue", label="model N(>=M)")
    if obs_m:
        ax.semilogy(obs_m, obs_r, "o", ms=5, color="k",
                    label="observed (completeness-corrected)")
    ax.axvline(wch["mmin_fit"], color="crimson", lw=1, ls="--",
               label=f"fit floor {wch['mmin_fit']:.2f}")
    ax.axvline(mmax, color="0.5", lw=1, ls=":", label=f"Mmax {mmax:.2f}")
    ax.set_xlabel("M")
    ax.set_ylabel("N(>=M) per year")
    ax.set_ylim(1e-5, None)
    ax.legend(fontsize=8)
    ax.set_title(f"{name}: observed vs model MFD "
                 f"(b={wch['b']:.3f}, N={wch['N']})")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)

    # numeric version of the same check
    if obs_m:
        i = np.argmin(np.abs(centers - obs_m[0]))
        ratio = model_cum[i] / max(obs_r[0], 1e-12)
        flag = "" if 0.5 <= ratio <= 2.0 else "  <-- CHECK"
        print(f"[mfd_check] {name}: model/observed at M{obs_m[0]:.1f} = "
              f"{ratio:.2f}{flag}")


def cat_year(cat):
    """Decimal year per event, derived from time_iso when absent.

    load_catalog returns the declustered file as written, which may or may
    not carry a year column. Parsing is by string slice, not
    pd.to_datetime, which bottoms out at 1677-09-21.

    Parameters
    ----------
    cat : pandas.DataFrame
        Class catalog with a year or time_iso column.

    Returns
    -------
    numpy.ndarray
        Decimal years, NaN where unparseable.
    """
    if "year" in cat.columns:
        return pd.to_numeric(cat["year"], errors="coerce").to_numpy(float)
    if "time_iso" not in cat.columns:
        return np.full(len(cat), np.nan)
    return pd.to_numeric(cat["time_iso"].astype(str).str[:4],
                         errors="coerce").to_numpy(float)


def fit_by_epoch(name, cat):
    """Fit (a, b) on each completeness epoch separately.

    The pooled Weichert fit weights every band by its own observation
    period, so a short recent band with a large count can dominate the
    slope while constraining nothing above its own magnitude range. This
    refits each epoch alone — each is internally consistent (one Mc, one
    duration), so disagreement between them localises the problem to a
    band rather than leaving it in the pooled result.

    Parameters
    ----------
    name : str
        Class name.
    cat : pandas.DataFrame
        Declustered class catalog.

    Returns
    -------
    pandas.DataFrame
        One row per epoch: mc, since_year, n, b, b_err, rate at mc, and
        the b implied between this epoch's threshold and the next.
    """
    cfg = sorted(C.COMPLETENESS[name], key=lambda s: s[1])
    yr = cat_year(cat)
    mg = cat["mag"].to_numpy(float)
    rows = []
    for mc, y0 in cfg:
        sel = (yr >= y0) & (mg >= mc - 1e-9) & np.isfinite(yr)
        sub = cat[sel]
        dur = max(C.PRESENT_YEAR - y0 + 1, 1)
        row = {"mc": mc, "since_year": y0, "years": dur, "n": len(sub),
               "rate_at_mc": len(sub) / dur, "b": np.nan, "b_err": np.nan}
        if len(sub) >= C.MIN_EVENTS_PER_WINDOW:
            try:
                per = np.full(len(sub), float(dur))
                w = weichert(sub["mag"].to_numpy(), per, mmin=mc, dm=C.DM,
                             n_boot=100)
                row["b"], row["b_err"] = w["b"], w["b_err"]
            except Exception as e:
                row["note"] = str(e)[:40]
        rows.append(row)
    t = pd.DataFrame(rows).sort_values("mc").reset_index(drop=True)

    # cumulative rate implied by each epoch, and the b between thresholds:
    # this is the quantity that must be consistent across epochs
    t["b_to_next"] = np.nan
    for i in range(len(t) - 1):
        r0, r1 = t.loc[i, "rate_at_mc"], t.loc[i + 1, "rate_at_mc"]
        dm_ = t.loc[i + 1, "mc"] - t.loc[i, "mc"]
        if r0 > 0 and r1 > 0 and dm_ > 0:
            t.loc[i, "b_to_next"] = np.log10(r0 / r1) / dm_
    return t


def plot_epoch_fits(name, tab, b_pooled, path):
    """Per-epoch b and the b implied between epochs, against the pooled fit.

    An epoch whose own b, or whose step to the next epoch, sits far from
    the others is the band driving the pooled result. A b implied between
    thresholds above ~1.5 is not physical and marks a completeness step
    that is too low.
    """
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    ok = tab.dropna(subset=["b"])
    if len(ok):
        a1.errorbar(ok["mc"], ok["b"], yerr=ok["b_err"], fmt="o", ms=6,
                    capsize=3, color="tab:blue", label="epoch fit")
        for _, r in ok.iterrows():
            a1.annotate(f"{int(r['since_year'])}\nn={int(r['n'])}",
                        (r["mc"], r["b"]), fontsize=6, ha="center",
                        textcoords="offset points", xytext=(0, 10))
    a1.axhline(b_pooled, color="crimson", lw=1.5, ls="--",
               label=f"pooled b = {b_pooled:.2f}")
    a1.axhspan(0.8, 1.2, color="0.85", zorder=0, label="typical 0.8-1.2")
    a1.set_xlabel("epoch Mc")
    a1.set_ylabel("b fitted on that epoch alone")
    a1.legend(fontsize=8)
    a1.set_title(f"{name}: b per completeness epoch")

    bn = tab.dropna(subset=["b_to_next"])
    if len(bn):
        lab = [f"{r['mc']:.1f}->{tab.loc[i + 1, 'mc']:.1f}"
               for i, r in bn.iterrows()]
        cols = ["crimson" if v > 1.5 else "tab:blue" for v in bn["b_to_next"]]
        a2.bar(range(len(bn)), bn["b_to_next"], color=cols)
        a2.set_xticks(range(len(bn)))
        a2.set_xticklabels(lab, fontsize=8)
    a2.axhline(1.0, color="k", lw=0.8, ls=":")
    a2.axhline(1.5, color="crimson", lw=1, ls="--",
               label="1.5 = not physical above")
    a2.set_ylabel("b implied between thresholds")
    a2.legend(fontsize=8)
    a2.set_title("b between adjacent completeness thresholds\n"
                 "(red = the step driving the pooled fit)")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def check_large_event_consistency(name, cat, wch, b_use, mmax, out):
    """Is the fitted b consistent with how often the largest events occur?

    The fit is anchored on small events, but the model must also reproduce
    the observed occurrence of the large ones. Extrapolating the fitted
    rate to the largest observed magnitude gives a predicted recurrence;
    if the catalog contains several such events in far less time, b is too
    steep. For slab_deep this is the Chillan test: two M8.0 events in ~120
    years cannot be reconciled with a recurrence of centuries.

    Parameters
    ----------
    name : str
        Class name.
    cat : pandas.DataFrame
        Declustered class catalog.
    wch : dict
        Weichert result, for the anchor rate and magnitude.
    b_use, mmax : float
        b applied to the class, and its Mmax.
    out : list
        Lines appended for the audit.
    """
    m_obs = float(cat["mag"].max())
    yr = cat_year(cat)
    yr = yr[np.isfinite(yr)]
    if not len(yr):
        return
    span = float(yr.max() - yr.min() + 1)
    thr = m_obs - 0.3
    n_big = int((cat["mag"] >= thr).sum())
    pred = wch["rate_mmin"] * 10 ** (-b_use * (thr - wch["mmin"]))
    if pred <= 0:
        return
    t_pred, t_obs = 1 / pred, span / max(n_big, 1)
    ratio = t_pred / t_obs
    line = (f"[large] {name}: M>={thr:.1f} observed {n_big} in {span:.0f} yr "
            f"(1 per {t_obs:.0f} yr); model b={b_use:.2f} predicts 1 per "
            f"{t_pred:.0f} yr — ratio {ratio:.1f}")
    print(line)
    out.append(line)
    if ratio > 3:
        msg = (f"[large] WARNING: {name} model under-predicts its own "
               f"largest events by {ratio:.0f}x. b={b_use:.2f} is too steep "
               "for the observed record — check the low completeness bands "
               f"in figures/s02_epochs_{name}.png")
        print(msg)
        out.append(msg)
    elif ratio < 0.33:
        msg = (f"[large] WARNING: {name} model over-predicts its largest "
               f"events by {1 / ratio:.0f}x — b={b_use:.2f} may be too flat")
        print(msg)
        out.append(msg)


def positive_estimators(name, cat):
    """b-positive and a-more-positive cross-check (van der Elst 2021, 2023).

    These estimate b and the rate from successive-magnitude differences,
    with no completeness table: the detection threshold is taken as the
    previous event's magnitude, so transient incompleteness after a large
    aftershock sequence cancels. USGS uses b-positive operationally in the
    2023 NSHM. If these return ~1.0 for a class where Weichert on the
    hand-built table gives something steeper, the table — not the
    seismicity — was driving the pooled fit.

    b-positive still sees baseline network incompleteness, so it is fed
    the catalog above the class fit floor. a-more-positive needs a b-value
    and returns log10(N over the window); it is converted to an annual
    rate anchored at MMIN_FORECAST for comparison with Weichert.

    Parameters
    ----------
    name : str
        Class name.
    cat : pandas.DataFrame
        Declustered class catalog with mag and (year or time_iso).

    Returns
    -------
    dict
        b_pos, b_pos_err, rate_pos (annual N>=MMIN_FORECAST), n_used, or
        NaNs with a note if seismostats is missing or the class is thin.
    """
    out = {"b_pos": np.nan, "b_pos_err": np.nan, "rate_pos": np.nan,
           "n_used": 0, "note": ""}
    try:
        from seismostats.analysis import (BPositiveBValueEstimator,
                                          AMorePositiveAValueEstimator)
    except ImportError:
        out["note"] = "seismostats not installed"
        return out

    mc = fit_floor(name)
    yr = cat_year(cat)
    ok = np.isfinite(yr) & (cat["mag"].to_numpy() >= mc - 1e-9)
    m = cat["mag"].to_numpy()[ok]
    t = yr[ok]
    order = np.argsort(t)
    m, t = m[order], t[order]
    # seismostats checks magnitudes lie on the delta_m grid; catalog
    # magnitudes are sometimes off-grid (rounding in the source catalogs),
    # which raises "Magnitudes are not binned correctly". Snap to the grid.
    m = np.round(m / C.DM) * C.DM
    if len(m) < 20:
        out["note"] = f"only {len(m)} events >= {mc}"
        return out
    span = max(float(t.max() - t.min()), 1.0)

    try:
        bp = BPositiveBValueEstimator()
        b = float(bp.calculate(m, mc=mc, delta_m=C.DM, times=t))
        # bootstrap the b-positive error over event resamples
        rng = np.random.default_rng(0)
        bs = []
        for _ in range(200):
            i = np.sort(rng.integers(0, len(m), len(m)))
            try:
                bs.append(float(BPositiveBValueEstimator().calculate(
                    m[i], mc=mc, delta_m=C.DM, times=t[i])))
            except Exception:
                continue
        b_err = float(np.std(bs)) if len(bs) > 10 else np.nan

        amp = AMorePositiveAValueEstimator()
        a_log = float(amp.calculate(m, mc=mc, delta_m=C.DM, times=t,
                                    b_value=b))
        # a_log = log10(N >= mc over the window); to annual N >= MMIN_FORECAST
        rate_mc = 10 ** a_log / span
        rate = rate_mc * 10 ** (b * (mc - C.MMIN_FORECAST))
        out.update(b_pos=b, b_pos_err=b_err, rate_pos=rate, n_used=len(m))
    except Exception as e:
        out["note"] = str(e)[:60]
    return out


def kijko_smit(name, cat):
    """Kijko-Smit (2012) combined Aki-Utsu b over completeness periods.

    Aki-Utsu b per completeness period, combined as a weighted harmonic
    mean. Carried only as a comparison column: it is erratic at high fit
    floors because a thin period gives an unstable per-period estimate,
    and it was rejected as the primary estimator in the interface pipeline
    for that reason. Reported so the comparison is on the record.
    """
    cfg = sorted(C.COMPLETENESS[name], key=lambda s: s[1])
    yr = cat_year(cat)
    mg = cat["mag"].to_numpy()
    num = den = 0.0
    n_tot = 0
    for i, (mc, y0) in enumerate(cfg):
        hi = cfg[i + 1][0] if i + 1 < len(cfg) else np.inf
        sel = np.isfinite(yr) & (yr >= y0) & (mg >= mc - 1e-9)
        mm = mg[sel]
        if len(mm) < C.MIN_EVENTS_PER_WINDOW:
            continue
        mbar = mm.mean()
        if mbar <= mc:
            continue
        b_i = np.log10(np.e) / (mbar - (mc - C.DM / 2))
        n_i = len(mm)
        num += n_i
        den += n_i / b_i
        n_tot += n_i
    if den <= 0 or n_tot < 10:
        return np.nan
    return num / den


def plot_method_compare(name, weic, ks, pos, obs_mfd, path):
    """All estimators side by side, with the observed MFD.

    The point of the figure: Weichert and Kijko-Smit both need the
    hand-built completeness table; b-positive/a-positive do not. Agreement
    across all of them is strong assurance; a lone Weichert outlier points
    at the table.
    """
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))

    labels, bs, errs, cols = [], [], [], []
    labels.append("Weichert")
    bs.append(weic["b"]); errs.append(weic["b_err"]); cols.append("tab:blue")
    if np.isfinite(ks):
        labels.append("Kijko-Smit"); bs.append(ks); errs.append(0)
        cols.append("tab:orange")
    if np.isfinite(pos["b_pos"]):
        labels.append("b-positive"); bs.append(pos["b_pos"])
        errs.append(pos["b_pos_err"] if np.isfinite(pos["b_pos_err"]) else 0)
        cols.append("tab:green")
    a1.bar(range(len(bs)), bs, yerr=errs, color=cols, capsize=4)
    a1.axhspan(0.8, 1.2, color="0.85", zorder=0)
    a1.axhline(1.0, color="k", lw=0.8, ls=":")
    a1.set_xticks(range(len(labels)))
    a1.set_xticklabels(labels, fontsize=9)
    a1.set_ylabel("b")
    a1.set_title(f"{name}: b by method\n(grey = table-free; needs no completeness)")

    # observed MFD with each method's GR line
    mc_ref = weic["mmin"]
    if obs_mfd is not None:
        mm, nn = obs_mfd
        a2.semilogy(mm, nn, "ko", ms=5, label="observed (compl-corrected)")
    xs = np.linspace(C.MMIN_FORECAST, weic.get("mmax", 8.2), 50)
    a2.semilogy(xs, weic["rate_mmin"] * 10 ** (-weic["b"] * (xs - mc_ref)),
                "-", color="tab:blue", lw=2, label=f"Weichert b={weic['b']:.2f}")
    if np.isfinite(pos["rate_pos"]):
        a2.semilogy(xs, pos["rate_pos"] * 10 ** (-pos["b_pos"] *
                    (xs - C.MMIN_FORECAST)), "--", color="tab:green", lw=2,
                    label=f"b-positive b={pos['b_pos']:.2f}")
    a2.set_xlabel("M")
    a2.set_ylabel("N(>=M) per year")
    a2.legend(fontsize=8)
    a2.set_title("MFD: table-based vs table-free")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def build_class(name: str, cat: pd.DataFrame, wch: dict, b_use: float,
                grid: pd.DataFrame, edges: np.ndarray,
                b_from_name: str = "") -> tuple[np.ndarray, dict]:
    """Smoothed field for one class, scaled to its truncated-GR rates.

    b_use may differ from wch['b'] when the class borrows a b (C.B_SOURCE);
    the activity rate is always re-anchored with b_use so the observed
    N(M >= fit floor) is preserved.
    """
    rate_fc = wch["rate_mmin"] * 10.0 ** (b_use * (wch["mmin"] - C.MMIN_FORECAST))
    mmax = class_mmax(name, cat)

    steps = completeness_steps(C.COMPLETENESS[name], C.PRESENT_YEAR)
    w = event_weights(cat, steps, b=(C.B_COMPLETENESS or b_use),
                      mc_min=wch["mmin_fit"])
    kp = kernel_params(name)
    kern = adaptive_kernel(cat, kp["N_NEIGHBORS"], kp["MIN_KERNEL_KM"])
    shape = smooth_field(cat, grid, w, kern, kp["KERNEL_POWER"],
                         kp["MAX_EVENT_GRID_DIST_KM"])
    if shape.sum() <= 0:
        raise ValueError(f"[build_class] empty field for class {name}")

    rb = tgr_bins(shape, rate_fc, b_use, edges, mmax)

    # rate check: the binned field must total the truncated-GR expectation
    exp = rate_fc * (1 - 10.0 ** (-b_use * (mmax - C.MMIN_FORECAST)))
    assert abs(rb.sum() - exp) / exp < 1e-9, (rb.sum(), exp)
    print(f"[build_class] {name}: b_used={b_use:.3f} "
          f"N(M>={C.MMIN_FORECAST})={rate_fc:.4f}/yr Mmax={mmax:.2f} "
          f"kernel_med={np.median(kern):.0f} km "
          f"(n_nb={kp['N_NEIGHBORS']}, floor={kp['MIN_KERNEL_KM']:.0f} km)"
          "  rate check OK")

    info = {"class": name, "n_events": len(cat), "n_fit": wch["N"],
            "n_windows_used": wch.get("n_win_used", np.nan),
            "mmin_fit": wch["mmin_fit"],
            "b_fit": wch["b"], "b_err": wch["b_err"], "b_used": b_use,
            "b_borrowed_from": b_from_name,
            "rate_mcfit": wch["rate_mmin"], "rate_forecast": rate_fc,
            "mmax": mmax, "kernel_med_km": float(np.median(kern)),
            "kernel_n_nb": kp["N_NEIGHBORS"],
            "kernel_floor_km": kp["MIN_KERNEL_KM"]}
    return rb, info


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)
    C.FIG.mkdir(parents=True, exist_ok=True)

    missing = [n for n in C.CLASSES if n not in C.COMPLETENESS]
    if missing:
        raise SystemExit(f"[main] no COMPLETENESS entry for {missing} — "
                         "paste the s01_mc proposal into ssm_config first")

    # 1) grid, restricted to the model bbox
    grid = pd.read_csv(C.GRID_CSV)
    lo, hi, la, ha = C.BBOX
    grid = grid[(grid["lon"] >= lo) & (grid["lon"] <= hi)
                & (grid["lat"] >= la) & (grid["lat"] <= ha)].reset_index(drop=True)
    print(f"[main] grid: {len(grid)} cells inside bbox")

    # 2) load every class catalog once (declustered mainshocks, bbox, region)
    cats = {n: load_catalog(s["catalog"], bbox=C.BBOX, region=s.get("region"))
            for n, s in C.CLASSES.items()}
    for n, c in cats.items():
        print(f"[main] {n}: {len(c)} mainshocks, M{c['mag'].min():.1f}-"
              f"{c['mag'].max():.1f}")

    # 3) fit (a, b) per class BEFORE building fields, so a class can borrow
    #    another class's b (C.B_SOURCE) for its MFD shape
    fits = {n: fit_class(n, c) for n, c in cats.items()}

    # b-stability per class: the diagnostic for the fit floor. Cheap enough
    # to run every time and it is the evidence for whatever MC_MIN_FIT ends
    # up in the config.
    if getattr(C, "B_STABILITY", True):
        for n, c in cats.items():
            f0 = fit_floor(n)
            floors = np.round(np.arange(f0 - 0.5, f0 + 1.1, 0.1), 2)
            tab = b_stability(n, c, floors)
            tab.to_csv(C.OUT / f"s02_bstab_{n}.csv", index=False)
            plot_b_stability(n, tab, C.FIG / f"s02_bstab_{n}.png")

    b_used, b_from = {}, {}
    for n in cats:
        src = C.B_SOURCE.get(n)
        if src is None:
            b_used[n], b_from[n] = fits[n]["b"], ""
            continue
        donors = [src] if isinstance(src, str) else list(src)
        if len(donors) == 1:
            b_used[n] = fits[donors[0]]["b"]
        else:
            # pooled fit: b from the donors' catalogs together (rate stays local)
            pooled = pd.concat([cats[d] for d in donors], ignore_index=True)
            b_used[n] = fit_class("+".join(donors), pooled)["b"]
        b_from[n] = "+".join(donors)
        print(f"[main] {n}: using b={b_used[n]:.3f} from {b_from[n]} "
              f"(own fit {fits[n]['b']:.3f}+/-{fits[n]['b_err']:.3f}); "
              "rate stays local")

    # 4) shared magnitude bins from MMIN_FORECAST to the largest class Mmax,
    #    so all class fields can be summed bin by bin. class_mmax runs here
    #    too, so the guard fires before any smoothing work.
    mmax_by = {n: class_mmax(n, c) for n, c in cats.items()}
    edges = mag_edges(C.MMIN_FORECAST, max(mmax_by.values()), C.DM)
    print(f"[main] shared bins {edges[0]:.2f}-{edges[-1]:.2f} "
          f"({len(edges) - 1} bins of {C.DM})")

    # 5) per-class smoothing + truncated GR; write grid, map, raster each
    per_class, infos, total = {}, [], None
    method_rows = []
    for n, cat in cats.items():
        print(f"\n===== class: {n} =====")
        rb, info = build_class(n, cat, fits[n], b_used[n], grid, edges,
                               b_from[n])
        per_class[n], total = rb, (rb.copy() if total is None else total + rb)
        infos.append(info)
        plot_class_fit(fits[n], fits[n]["mags_fit"], fits[n]["per_fit"], C.DM,
                       f"{n}: Weichert fit", C.FIG / f"s02_fit_{n}.png")
        plot_obs_vs_model(n, cat, rb, edges, fits[n], mmax_by[n],
                          C.FIG / f"s02_mfd_obs_{n}.png")
        if getattr(C, "EPOCH_FITS", True):
            et = fit_by_epoch(n, cat)
            et.insert(0, "class", n)
            et.to_csv(C.OUT / f"s02_epochs_{n}.csv", index=False)
            plot_epoch_fits(n, et, b_used[n], C.FIG / f"s02_epochs_{n}.png")
            print(f"[epochs] {n}:")
            print(et.to_string(index=False))
            bad = et.dropna(subset=["b_to_next"])
            for _, r in bad[bad["b_to_next"] > 1.5].iterrows():
                print(f"[epochs] {n}: step Mc{r['mc']:.1f} (since "
                      f"{int(r['since_year'])}) implies b={r['b_to_next']:.2f} "
                      "to the next threshold — not physical, that band is "
                      "claiming more completeness than it has")
        check_large_event_consistency(n, cat, fits[n], b_used[n],
                                      mmax_by[n], [])
        if getattr(C, "METHOD_COMPARE", True):
            ks_b = kijko_smit(n, cat)
            pos = positive_estimators(n, cat)
            obs = None
            try:
                steps = completeness_steps(C.COMPLETENESS[n], C.PRESENT_YEAR)
                per = obs_periods(cat["mag"].to_numpy(), steps)
                mm = np.arange(fits[n]["mmin"], mmax_by[n], 5 * C.DM)
                nn = [np.sum(1.0 / per[(cat["mag"].to_numpy() >= e)
                                       & np.isfinite(per)]) for e in mm]
                keep = [i for i, v in enumerate(nn) if v > 0]
                obs = (mm[keep], np.array(nn)[keep]) if keep else None
            except Exception:
                pass
            plot_method_compare(n, fits[n], ks_b, pos, obs,
                                C.FIG / f"s02_methods_{n}.png")
            method_rows.append({
                "class": n, "b_weichert": round(fits[n]["b"], 3),
                "b_weichert_err": round(fits[n]["b_err"], 3),
                "b_kijko_smit": round(ks_b, 3) if np.isfinite(ks_b) else np.nan,
                "b_positive": round(pos["b_pos"], 3)
                if np.isfinite(pos["b_pos"]) else np.nan,
                "b_positive_err": round(pos["b_pos_err"], 3)
                if np.isfinite(pos["b_pos_err"]) else np.nan,
                "rate_weichert": round(fits[n]["rate_mmin"], 4),
                "rate_positive": round(pos["rate_pos"], 4)
                if np.isfinite(pos["rate_pos"]) else np.nan,
                "n_positive": pos["n_used"], "note": pos["note"]})
            print(f"[methods] {n}: Weichert b={fits[n]['b']:.2f}, "
                  f"Kijko-Smit b={ks_b:.2f}, b-positive b={pos['b_pos']:.2f}"
                  + (f" ({pos['note']})" if pos["note"] else ""))
        write_mfd_grid(grid, rb, edges, C.OUT / f"ssm_mfd_grid_{n}.csv")
        plot_rate_map(grid, rb.sum(axis=1), f"{n}: N(M>={C.MMIN_FORECAST}) /yr",
                      C.FIG / f"s02_map_{n}.png")
        write_raster(grid, safe_log10(rb.sum(axis=1)),
                     C.OUT / f"ssm_log10_rate_{n}.tif")

    # 6) superposition -> total SSM (this file feeds s03)
    assert np.allclose(total, sum(per_class.values())), "superposition mismatch"
    write_mfd_grid(grid, total, edges, C.SSM_GRID)
    plot_rate_map(grid, total.sum(axis=1),
                  f"total: N(M>={C.MMIN_FORECAST}) /yr",
                  C.FIG / "s02_map_total.png")
    write_raster(grid, safe_log10(total.sum(axis=1)),
                 C.OUT / "ssm_log10_rate_total.tif")
    plot_total_mfd(per_class, edges, C.FIG / "s02_mfd_superposition.png")

    # 7) summary table: what every class contributed
    summ = pd.DataFrame(infos)
    summ["frac_of_total"] = summ["rate_forecast"] / summ["rate_forecast"].sum()
    summ.to_csv(C.OUT / "ssm_class_summary.csv", index=False)
    if method_rows:
        mc_df = pd.DataFrame(method_rows)
        mc_df.to_csv(C.OUT / "ssm_method_comparison.csv", index=False)
        print("\n[methods] estimator comparison:")
        print(mc_df.to_string(index=False))
    print("\n[main] class summary:")
    print(summ.to_string(index=False))
    print(f"[main] total N(M>={C.MMIN_FORECAST}) = "
          f"{summ['rate_forecast'].sum():.4f} /yr; grid total (to Mmax) = "
          f"{total.sum():.4f} /yr")
    print(f"[main] SSM grid -> {C.SSM_GRID.resolve()}")
    print(f"[main] READ figures/s02_mfd_obs_*.png before trusting any of this")


if __name__ == "__main__":
    main()