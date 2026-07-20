# s03_ab.py
# a-b estimation on the internally declustered interface catalog.
# Gated on the hand-approved sub_config.COMPLETENESS (full-catalog steps,
# applied to every segment). Weichert and Kijko-Smit run side by side on
# the same completeness table; AB_ESTIMATOR in config picks the one used
# downstream after the team reviews the comparison.
# Outputs: outputs/ab/ab_results.json        per-segment parameters (both)
#          outputs/ab/ab_compare.csv         b, b_err, implied rates table
#          outputs/ab/ab_sensitivity.csv     b per decluster variant
#          figures/s03_mfd.png               observed MFD + both fits

import datetime
import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sub_config as C

AB_DIR = C.OUT_DIR / "ab"
LN10 = np.log(10.0)


def _decyear(s):
    try:
        y, mo, d = int(s[:4]), int(s[5:7]), int(s[8:10])
        doy = datetime.date(y, mo, d).timetuple().tm_yday
        return y + (doy - 1) / 365.25
    except (ValueError, TypeError):
        return np.nan


# completeness machinery

def steps_sorted():
    return sorted(C.COMPLETENESS, key=lambda s: s[1])  # by since_year


def y_start(m):
    """Completeness start year for magnitude m (largest step mc <= m)."""
    best = None
    for mc, y0 in C.COMPLETENESS:
        if m >= mc - 1e-9 and (best is None or mc > best[0]):
            best = (mc, y0)
    return best[1] if best else None


def complete_subset(df, y_end):
    keep = []
    for m, y in zip(df["mag"], df["year"]):
        y0 = y_start(m)
        keep.append(y0 is not None and y >= y0 and y <= y_end)
    return df[np.array(keep)]


# estimators

def weichert(df, y_end, mref, mmin_fit=None):
    """
    Weichert (1980) ML fit for unequal observation periods.

    Bins of DELTA_M from max(lowest completeness step, mmin_fit); each bin
    observed over T(m) = y_end - y_start(m). Newton iteration on beta.

    Returns
    -------
    b, lam : float
        b-value and annual rate of M >= mref.
    """
    m_lo = min(mc for mc, _ in C.COMPLETENESS)
    if mmin_fit is not None:
        m_lo = max(m_lo, mmin_fit)
    df = df[df["mag"] >= m_lo - 1e-9]
    m_hi = df["mag"].max() + C.DELTA_M
    edges = np.arange(m_lo, m_hi + C.DELTA_M, C.DELTA_M)
    mi = edges[:-1] + C.DELTA_M / 2
    ti = np.array([y_end - y_start(m) for m in mi], float)
    ni = np.zeros(len(mi))
    for m in df["mag"]:
        k = int((m - m_lo) / C.DELTA_M + 1e-9)
        if 0 <= k < len(ni):
            ni[k] += 1

    n = ni.sum()
    if n < 10:
        return np.nan, np.nan
    mbar = (ni * mi).sum() / n
    beta = 1.0 * LN10
    for _ in range(100):
        w = ti * np.exp(-beta * mi)
        s1, s2, s3 = w.sum(), (w * mi).sum(), (w * mi ** 2).sum()
        f = s2 / s1 - mbar
        dfdb = (s2 / s1) ** 2 - s3 / s1
        step = f / dfdb
        beta -= step
        if abs(step) < 1e-9:
            break
    b = beta / LN10
    lam_edge = n * np.exp(-beta * mi).sum() / (ti * np.exp(-beta * mi)).sum()
    lam = lam_edge * 10 ** (-b * (mref - edges[0]))
    return b, lam


def kijko_smit(df, y_end, mref, mmin_fit=None):
    """
    Kijko & Smit (2012) combined Aki-Utsu estimator over completeness
    periods, with Poisson ML activity rate at mref given b. mmin_fit
    raises the effective Mc of periods below it.
    """
    st = steps_sorted()
    ys = [y0 for _, y0 in st] + [y_end]
    ns, betas, tis, mcs = [], [], [], []
    for (mc, y0), y1 in zip(st, ys[1:]):
        if mmin_fit is not None:
            mc = max(mc, mmin_fit)
        sub = df[(df["year"] >= y0) & (df["year"] < y1)
                 & (df["mag"] >= mc - 1e-9)]
        if len(sub) < 5:
            continue
        mmean = sub["mag"].mean()
        betas.append(1.0 / (mmean - (mc - C.DELTA_M / 2)))
        ns.append(len(sub))
        tis.append(y1 - y0)
        mcs.append(mc)
    if not ns:
        return np.nan, np.nan
    ns = np.array(ns, float)
    beta = ns.sum() / (ns / np.array(betas)).sum()
    b = beta / LN10
    lam = ns.sum() / (np.array(tis) * 10 ** (-b * (np.array(mcs) - mref))).sum()
    return b, lam


def boot_b(df, y_end, fn, nb):
    bs = []
    for _ in range(nb):
        bb, _ = fn(df.sample(len(df), replace=True), y_end, C.MMIN_HAZ,
                   C.MMIN_FIT)
        if np.isfinite(bb):
            bs.append(bb)
    return float(np.std(bs)) if bs else np.nan


def obs_cum_rates(df, y_end, grid):
    t = np.array([y_end - y_start(m) for m in df["mag"]], float)
    w = 1.0 / t
    return np.array([w[df["mag"].to_numpy() >= m - 1e-9].sum() for m in grid])


def fit_segment(df, y_end):
    r = {"n_complete": int(len(df)),
         "mmax_obs": float(df["mag"].max()) if len(df) else np.nan}
    for name, fn in (("weichert", weichert), ("kijko_smit", kijko_smit)):
        b, lam = fn(df, y_end, C.MMIN_HAZ, C.MMIN_FIT)
        r[name] = {"b": b, "b_err": boot_b(df, y_end, fn, C.N_BOOT),
                   "a": np.log10(lam) + b * C.MMIN_HAZ if lam > 0 else np.nan,
                   "rate_mmin": lam,
                   "rates": {f"M{m}": lam * 10 ** (-b * (m - C.MMIN_HAZ))
                             for m in C.AB_REF_MAGS}}
        if r[name]["b_err"] > C.B_ERR_WARN:
            print(f"  [warn] {name} b_err={r[name]['b_err']:.3f} "
                  f"> {C.B_ERR_WARN} (n={len(df)})")
    return r


def load_dc(method):
    df = pd.read_csv(C.OUT_DIR / "decluster" / f"cat_dc_{method}.csv")
    df["year"] = [_decyear(str(s)) for s in df["time_iso"]]
    df = df[np.isfinite(df["year"]) & df["mag"].notna()]
    df = df[(df["latitude"] >= C.SEG_BOUNDS[0])
            & (df["latitude"] <= C.SEG_BOUNDS[-1])]
    df["seg"] = pd.cut(df["latitude"], bins=C.SEG_BOUNDS, labels=C.SEG_IDS,
                       right=False)
    return df.reset_index(drop=True)


def main():
    if not C.COMPLETENESS:
        raise SystemExit("sub_config.COMPLETENESS is empty — review the s02 "
                         "proposal, paste the approved steps, rerun.")
    AB_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_dc(C.DC_METHOD)
    y_end = float(np.ceil(df["year"].max()))
    print(f"catalog: {len(df)} mainshocks in lat span, y_end={y_end:.0f}, "
          f"steps={C.COMPLETENESS}")

    res, rows = {}, []
    for sid in [C.FULL_ID] + C.SEG_IDS:
        sub = df if sid == C.FULL_ID else df[df["seg"] == sid]
        comp = complete_subset(sub, y_end)
        print(f"{sid}: {len(comp)}/{len(sub)} complete events")
        r = fit_segment(comp, y_end)
        lo = C.SEG_BOUNDS[0] if sid == C.FULL_ID else C.SEG_BOUNDS[C.SEG_IDS.index(sid)]
        hi = C.SEG_BOUNDS[-1] if sid == C.FULL_ID else C.SEG_BOUNDS[C.SEG_IDS.index(sid) + 1]
        r["lat_min"], r["lat_max"] = lo, hi
        res[sid] = r
        for est in ("weichert", "kijko_smit"):
            e = r[est]
            rows.append({"seg": sid, "est": est, "n": r["n_complete"],
                         "b": round(e["b"], 3), "b_err": round(e["b_err"], 3),
                         "a": round(e["a"], 3),
                         **{k: round(v, 5) for k, v in e["rates"].items()}})

    # observed rates at reference mags for the comparison table
    for sid in [C.FULL_ID] + C.SEG_IDS:
        sub = df if sid == C.FULL_ID else df[df["seg"] == sid]
        comp = complete_subset(sub, y_end)
        obs = obs_cum_rates(comp, y_end, np.array(C.AB_REF_MAGS, float))
        rows.append({"seg": sid, "est": "observed", "n": len(comp),
                     "b": np.nan, "b_err": np.nan, "a": np.nan,
                     **{f"M{m}": round(o, 5)
                        for m, o in zip(C.AB_REF_MAGS, obs)}})

    tab = pd.DataFrame(rows)
    tab.to_csv(AB_DIR / "ab_compare.csv", index=False)
    print("\n" + tab.to_string(index=False))

    meta = {"dc_method": C.DC_METHOD, "estimator_chosen": C.AB_ESTIMATOR,
            "completeness": C.COMPLETENESS, "y_end": y_end,
            "mmin_haz": C.MMIN_HAZ}
    (AB_DIR / "ab_results.json").write_text(
        json.dumps({"meta": meta, "segments": res}, indent=2, default=float))

    # decluster sensitivity (b only, no bootstrap)
    sens = []
    for method in C.DC_METHODS:
        d = load_dc(method)
        ye = float(np.ceil(d["year"].max()))
        for sid in [C.FULL_ID] + C.SEG_IDS:
            sub = d if sid == C.FULL_ID else d[d["seg"] == sid]
            comp = complete_subset(sub, ye)
            bw, lw = weichert(comp, ye, C.MMIN_HAZ, C.MMIN_FIT)
            bk, lk = kijko_smit(comp, ye, C.MMIN_HAZ, C.MMIN_FIT)
            sens.append({"method": method, "seg": sid, "n": len(comp),
                         "b_w": round(bw, 3), "b_ks": round(bk, 3),
                         "M7.5_w": round(lw * 10 ** (-bw * (7.5 - C.MMIN_HAZ)), 5)})
    sens = pd.DataFrame(sens)
    sens.to_csv(AB_DIR / "ab_sensitivity.csv", index=False)
    print("\ndecluster sensitivity:\n"
          + sens.pivot(index="seg", columns="method", values="b_w").round(3).to_string())

    # b stability vs fit floor (pooled + segments, both estimators)
    floors = np.round(np.arange(min(mc for mc, _ in C.COMPLETENESS),
                                C.MMIN_HAZ + 0.01, 0.2), 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, fn, ttl in ((ax1, weichert, "weichert"),
                        (ax2, kijko_smit, "kijko_smit")):
        for sid in [C.FULL_ID] + C.SEG_IDS:
            sub = df if sid == C.FULL_ID else df[df["seg"] == sid]
            comp = complete_subset(sub, y_end)
            bs = [fn(comp, y_end, C.MMIN_HAZ, f)[0] for f in floors]
            ax.plot(floors, bs, "o-", ms=3,
                    lw=2 if sid == C.FULL_ID else 1, label=sid)
        ax.set_xlabel("fit floor Mmin")
        ax.set_title(ttl)
        ax.grid(alpha=0.3)
    ax1.set_ylabel("b")
    ax1.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "s03_b_stability.png", dpi=200)

    # figures: observed cumulative MFD + both fits per segment
    ids = [C.FULL_ID] + C.SEG_IDS
    fig, axes = plt.subplots(1, len(ids), figsize=(3.2 * len(ids), 4),
                             sharey=True)
    for ax, sid in zip(np.atleast_1d(axes), ids):
        sub = df if sid == C.FULL_ID else df[df["seg"] == sid]
        comp = complete_subset(sub, y_end)
        grid = np.arange(min(mc for mc, _ in C.COMPLETENESS),
                         comp["mag"].max() + 0.05, 0.1)
        ax.semilogy(grid, np.maximum(obs_cum_rates(comp, y_end, grid), 1e-6),
                    "k.", ms=4, label="observed")
        r = res[sid]
        for est, col in (("weichert", "C0"), ("kijko_smit", "C3")):
            e = r[est]
            lam = e["rate_mmin"] * 10 ** (-e["b"] * (grid - C.MMIN_HAZ))
            ax.semilogy(grid, lam, col,
                        label=f"{est} b={e['b']:.2f}±{e['b_err']:.2f}")
        ax.axvline(C.MMIN_HAZ, color="gray", lw=0.5, ls="--")
        ax.set_ylim(1e-5, 1e3)
        ax.set_title(f"{sid} (n={r['n_complete']})", fontsize=9)
        ax.set_xlabel("M")
        ax.legend(fontsize=6)
    np.atleast_1d(axes)[0].set_ylabel("N(>=M) /yr")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "s03_mfd.png", dpi=200)
    print(f"\nwrote {AB_DIR}")


if __name__ == "__main__":
    main()