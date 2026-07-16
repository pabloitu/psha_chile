# ssm_lib.py
# Shared primitives for the crustal SSM pipeline: catalog io, completeness,
# Weichert (a, b), adaptive-kernel smoothing, truncated-GR binning, grid io,
# rasters and standard figures. No paths or parameters live here.

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# catalog

def load_catalog(path: Path, bbox=None, region=None,
                 only_mainshocks=True) -> pd.DataFrame:
    df = pd.read_csv(path)
    n0 = len(df)
    if only_mainshocks and "is_mainshock" in df.columns:
        df = df[df["is_mainshock"] == True]
    for box in (bbox, region):
        if box is not None:
            lo, hi, la, ha = box
            df = df[(df["longitude"] >= lo) & (df["longitude"] <= hi)
                    & (df["latitude"] >= la) & (df["latitude"] <= ha)]
    print(f"[load_catalog] {Path(path).name}: {n0} -> {len(df)} "
          f"(mainshocks, bbox{', region' if region else ''})")
    return df.reset_index(drop=True)


def completeness_steps(steps_cfg: list, present_year: int) -> pd.DataFrame:
    """
    Completeness table from explicit (Mc, since_year) steps (s00_mc.py).

    Returns a frame with mc_window / tc_years columns (period = present_year -
    since_year + 1), sorted by Mc, so that magnitude M is observed for the
    period of the lowest Mc <= M.
    """
    if not steps_cfg:
        raise ValueError("[completeness_steps] empty COMPLETENESS for this "
                         "class: run s00_mc.py and fill ssm_config.COMPLETENESS")
    df = pd.DataFrame(sorted(steps_cfg), columns=["mc_window", "since_year"])
    df["tc_years"] = present_year - df["since_year"] + 1
    if not df["tc_years"].is_monotonic_increasing:
        print("[completeness_steps] WARNING: period does not increase with Mc; "
              "check the steps")
    return df


def obs_periods(mags: np.ndarray, steps: pd.DataFrame) -> np.ndarray:
    mc = steps["mc_window"].to_numpy()
    tc = steps["tc_years"].to_numpy()
    idx = np.searchsorted(mc, mags + 1e-9) - 1
    return np.where(idx >= 0, tc[np.clip(idx, 0, len(tc) - 1)], np.nan)


def usable_windows(cat: pd.DataFrame, steps: pd.DataFrame, mc_min: float,
                   min_events: int, name: str) -> pd.DataFrame:
    """
    Keep only completeness steps this class can actually support.

    Events are counted in the magnitude band each step owns, i.e. between its
    Mc and the next step's Mc. A band with < min_events cannot constrain the
    fit but does carry weight through 1/t, so it is dropped and reported.
    """
    mcs = steps["mc_window"].to_numpy()
    keep, drop = [], []
    for i, s_ in steps.iterrows():
        hi = mcs[i + 1] if i + 1 < len(mcs) else np.inf
        if hi <= mc_min + 1e-9:
            continue                      # band lies entirely below the fit floor
        lo = max(float(s_["mc_window"]), mc_min)   # clip, do not drop
        n = int(((cat["mag"] >= lo) & (cat["mag"] < hi)).sum())
        (keep if n >= min_events else drop).append(
            {"mc_window": lo, "tc_years": s_["tc_years"], "n": n})
    if drop:
        print(f"[usable_windows] {name}: dropping {len(drop)} window(s) with "
              f"< {min_events} events: "
              + ", ".join(f"Mc{d['mc_window']:.1f}(n={d['n']})" for d in drop))
    print(f"[usable_windows] {name}: {len(keep)} usable window(s)")
    return pd.DataFrame(keep) if keep else pd.DataFrame(
        columns=["mc_window", "tc_years", "n"])


def completeness_audit(cat: pd.DataFrame, steps: pd.DataFrame,
                       name: str) -> pd.DataFrame:
    """
    Events and implied rate per completeness step (counted in the magnitude
    band the step owns). A band whose implied rate is out of line with its
    neighbours means the chosen Mc/since_year is optimistic there.
    """
    mcs = steps["mc_window"].to_numpy()
    rows = []
    for i, s in steps.iterrows():
        hi = mcs[i + 1] if i + 1 < len(mcs) else np.inf
        n = int(((cat["mag"] >= s["mc_window"]) & (cat["mag"] < hi)).sum())
        width = (hi - s["mc_window"]) if np.isfinite(hi) else np.nan
        rows.append({"mc_window": s["mc_window"], "since_year": s["since_year"],
                     "tc_years": s["tc_years"], "band_hi": hi, "n_events": n,
                     "rate_per_yr": n / s["tc_years"],
                     "rate_per_yr_per_mag": n / s["tc_years"] / width
                     if np.isfinite(width) and width > 0 else np.nan})
    df = pd.DataFrame(rows)
    print(f"[completeness_audit] {name}:")
    print(df.to_string(index=False))

    # GR requires the per-unit-magnitude band rate to fall as magnitude rises
    # (raw band rates are not comparable across unequal band widths)
    r = df["rate_per_yr_per_mag"].to_numpy()
    fin = np.isfinite(r)
    rr = r[fin]
    bad = np.nonzero(rr[1:] > rr[:-1] * 1.30)[0]   # >30% rise = inconsistent
    if len(bad):
        mcs_bad = df.loc[fin, "mc_window"].to_numpy()
        print(f"[completeness_audit] WARNING: {name} band-rate density rises "
              "with magnitude at Mc "
              + ", ".join(f"{mcs_bad[i + 1]:.1f}" for i in bad)
              + " -> a since_year there is likely too early; revisit "
                "COMPLETENESS")
    dup = df["since_year"].duplicated(keep=False)
    if dup.any():
        print(f"[completeness_audit] note: {name} steps "
              + ", ".join(f"Mc{m:.1f}" for m in df.loc[dup, "mc_window"])
              + " share a since_year; redundant (harmless), keep the lowest Mc")
    return df


# weichert (a, b)

def _beta_ml(ctr, n, t) -> float:
    N = n.sum()
    beta = 1.5
    for _ in range(200):
        w = t * np.exp(-beta * ctr)
        f = (w * ctr).sum() / w.sum() - (n * ctr).sum() / N
        d = -((w * ctr**2).sum() / w.sum() - ((w * ctr).sum() / w.sum())**2)
        step = f / d
        beta -= step
        if abs(step) < 1e-10:
            break
    return beta


def weichert(mags: np.ndarray, periods: np.ndarray, mmin: float, dm: float,
             n_boot: int = 200, seed: int = 0) -> dict:
    """
    Weichert (1980) ML (a, b) for unequal observation periods.

    b_err is a nonparametric bootstrap standard deviation, not b/sqrt(N):
    with few events in the long (historical) windows the analytic error is
    optimistic, and the bootstrap reflects how much the estimate leans on
    those sparse brackets.

    Returns dict: b, b_err, rate_mmin (annual N(M>=mmin)), a, N, and the
    binned n, t, ctr used.
    """
    edges = np.arange(mmin, mags.max() + dm + 1e-9, dm)
    ctr = edges[:-1] + dm / 2.0
    n = np.histogram(mags, bins=edges)[0].astype(float)
    t = np.array([np.median(periods[(mags >= lo) & (mags < hi)])
                  if ((mags >= lo) & (mags < hi)).any() else np.nan
                  for lo, hi in zip(edges[:-1], edges[1:])])
    for i in range(len(t)):
        if np.isnan(t[i]):
            prev = t[:i][~np.isnan(t[:i])]
            t[i] = prev[-1] if len(prev) else np.nan
    ok = ~np.isnan(t)
    ctr, n, t = ctr[ok], n[ok], t[ok]
    N = n.sum()
    if N < 10:
        print(f"[weichert] WARNING: only {int(N)} events; estimate is weak")

    # effective anchor: the lower edge of the first populated bin. When a
    # class's lowest complete magnitude sits above the nominal mmin (e.g.
    # backarc Mc 5.3 vs MC_MIN_FIT 5.0), the ML rate refers to that edge,
    # not to mmin; anchoring at mmin would inflate the class rate.
    mmin_eff = float(ctr[0] - dm / 2.0)
    if mmin_eff > mmin + 1e-9:
        print(f"[weichert] rate anchored at M>={mmin_eff:.2f} "
              f"(no complete data down to {mmin:.2f})")

    beta = _beta_ml(ctr, n, t)
    b = beta / math.log(10.0)
    w = np.exp(-beta * ctr)
    rate_mmin = N * w.sum() / (t * w).sum()
    a = math.log10(rate_mmin) + b * mmin_eff

    # bootstrap b (resample events, rebin, refit)
    rng = np.random.default_rng(seed)
    m_ok = mags[np.isin(np.digitize(mags, edges) - 1,
                        np.nonzero(ok)[0])] if len(mags) else mags
    bs = []
    for _ in range(n_boot):
        mm = rng.choice(m_ok, size=len(m_ok), replace=True)
        nn = np.histogram(mm, bins=edges)[0].astype(float)[ok]
        if nn.sum() < 5 or (nn > 0).sum() < 2:
            continue
        try:
            bs.append(_beta_ml(ctr, nn, t) / math.log(10.0))
        except (ZeroDivisionError, FloatingPointError):
            continue
    b_err = float(np.std(bs)) if len(bs) > 10 else b / math.sqrt(N)

    return {"b": b, "b_err": b_err, "a": a, "rate_mmin": rate_mmin,
            "mmin": mmin_eff, "N": int(N), "n": n, "t": t, "ctr": ctr,
            "n_windows": int((n > 0).sum())}


# distances / kernels (great-circle, spherical law of cosines)

R_EARTH = 6371.0


def gc_dist(lon1, lat1, lon2, lat2) -> np.ndarray:
    """Great-circle distance (km), haversine (stable at short range)."""
    lon1, lat1, lon2, lat2 = map(np.deg2rad, (lon1, lat1, lon2, lat2))
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * R_EARTH * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def pairwise_dist(lon, lat) -> np.ndarray:
    return gc_dist(lon[:, None], lat[:, None], lon[None, :], lat[None, :])


def point_to_grid_dist(lon0, lat0, lon, lat) -> np.ndarray:
    return gc_dist(lon0, lat0, np.asarray(lon), np.asarray(lat))


def event_weights(cat: pd.DataFrame, steps: pd.DataFrame, b: float,
                  mc_min: float) -> np.ndarray:
    """
    Per-event rate weight from the explicit completeness steps:
    1/T(M) * 10^(b (Mc(M) - mc_min)), where T(M) and Mc(M) come from the step
    the event's magnitude falls in. Events below the lowest Mc get weight 0.
    """
    mags = cat["mag"].to_numpy(float)
    per = obs_periods(mags, steps)
    mc_ev = obs_mc(mags, steps)
    w = np.zeros(len(mags))
    ok = np.isfinite(per) & (per > 0) & np.isfinite(mc_ev)
    w[ok] = 1.0 / per[ok] * 10.0 ** (b * (mc_ev[ok] - mc_min))
    if (~ok).any():
        print(f"[event_weights] {int((~ok).sum())} events below the lowest Mc "
              "get zero weight")
    return w


def obs_mc(mags: np.ndarray, steps: pd.DataFrame) -> np.ndarray:
    """Mc of the completeness step each magnitude falls in."""
    mc = steps["mc_window"].to_numpy()
    idx = np.searchsorted(mc, mags + 1e-9) - 1
    return np.where(idx >= 0, mc[np.clip(idx, 0, len(mc) - 1)], np.nan)


def adaptive_kernel(cat: pd.DataFrame, n_neighbors: int,
                    min_kernel_km: float) -> np.ndarray:
    lon = cat["longitude"].to_numpy(float)
    lat = cat["latitude"].to_numpy(float)
    if len(lon) < 2:
        raise ValueError("[adaptive_kernel] need >= 2 events")
    d = np.sort(pairwise_dist(lon, lat), axis=1)
    k = min(n_neighbors, len(lon) - 1)
    return np.maximum(d[:, k], min_kernel_km)


def smooth_field(cat: pd.DataFrame, grid: pd.DataFrame, weights: np.ndarray,
                 kernel_km: np.ndarray, power: float,
                 max_dist_km: float) -> np.ndarray:
    """
    Kernel-smoothed annual rate field on the grid: per event,
    K = 1/(r^2 + d^2)^p normalized to 1 over reachable cells, scaled by the
    event weight; summed over events. Returns rates (n_cells,).
    """
    lon_g = grid["lon"].to_numpy(float)
    lat_g = grid["lat"].to_numpy(float)
    rates = np.zeros(len(grid))
    lon_e = cat["longitude"].to_numpy(float)
    lat_e = cat["latitude"].to_numpy(float)
    for i in range(len(cat)):
        r = point_to_grid_dist(lon_e[i], lat_e[i], lon_g, lat_g)
        m = r <= max_dist_km
        if not m.any():
            continue
        k = 1.0 / (r[m] ** 2 + kernel_km[i] ** 2) ** power
        s = k.sum()
        if s > 0 and np.isfinite(s):
            rates[m] += k * (weights[i] / s)
    return rates


# truncated GR on shared bins

def mag_edges(mmin: float, mmax_global: float, dm: float) -> np.ndarray:
    n = int(math.ceil((mmax_global - mmin) / dm - 1e-9))
    return np.round(mmin + dm * np.arange(n + 1), 6)


def tgr_bins(shape: np.ndarray, rate_mmin: float, b: float, edges: np.ndarray,
             mmax: float) -> np.ndarray:
    """
    Per-cell incremental rates on shared bin edges for a truncated GR:
    total N(>=mmin) = rate_mmin distributed spatially by `shape` (normalized),
    truncated at this class's mmax (bins above are zero).

    Returns (n_cells, n_bins).
    """
    s = shape / shape.sum()
    lam = s * rate_mmin
    mmin = edges[0]
    lo, hi = edges[:-1], edges[1:]
    f_lo = 10.0 ** (b * (mmin - np.minimum(lo, mmax)))
    f_hi = 10.0 ** (b * (mmin - np.minimum(hi, mmax)))
    f_hi[hi >= mmax - 1e-9] = 10.0 ** (b * (mmin - mmax))
    f_lo[lo >= mmax - 1e-9] = 10.0 ** (b * (mmin - mmax))
    binfrac = np.maximum(f_lo - f_hi, 0.0)
    return lam[:, None] * binfrac[None, :]


# grid io / rasters

def bin_col(lo: float, hi: float) -> str:
    return f"rate_M{lo:.1f}_{hi:.1f}"


def write_mfd_grid(grid: pd.DataFrame, rates_bins: np.ndarray,
                   edges: np.ndarray, out_csv: Path,
                   depth: float = 0.0) -> pd.DataFrame:
    df = grid[["lon", "lat"]].copy()
    df["depth"] = depth
    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        df[bin_col(lo, hi)] = rates_bins[:, i]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"[write_mfd_grid] wrote {out_csv} "
          f"({len(df)} cells, {rates_bins.shape[1]} bins, "
          f"total {rates_bins.sum():.4f} /yr)")
    return df


def write_raster(grid: pd.DataFrame, values: np.ndarray, out_tif: Path):
    import rasterio
    from rasterio.transform import from_origin
    lons, lats = grid["lon"].to_numpy(), grid["lat"].to_numpy()
    ulon, ulat = np.sort(np.unique(lons)), np.sort(np.unique(lats))
    dx, dy = np.median(np.diff(ulon)), np.median(np.diff(ulat))
    nc = int(round((ulon[-1] - ulon[0]) / dx)) + 1
    nr = int(round((ulat[-1] - ulat[0]) / dy)) + 1
    arr = np.full((nr, nc), np.nan)
    col = np.round((lons - ulon[0]) / dx).astype(int)
    row = np.round((ulat[-1] - lats) / dy).astype(int)
    arr[row, col] = values
    out_tif.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_tif, "w", driver="GTiff", height=nr, width=nc,
                       count=1, dtype=arr.dtype, crs="EPSG:4326",
                       transform=from_origin(ulon[0] - dx / 2, ulat[-1] + dy / 2,
                                             dx, dy), nodata=np.nan) as dst:
        dst.write(arr, 1)
    print(f"[write_raster] wrote {out_tif}")


def safe_log10(v: np.ndarray) -> np.ndarray:
    out = np.full_like(v, np.nan, dtype=float)
    m = (v > 0) & np.isfinite(v)
    out[m] = np.log10(v[m])
    return out


# figures

def plot_class_fit(wch: dict, mags: np.ndarray, periods: np.ndarray,
                   dm: float, title: str, png: Path):
    """Observed cumulative rates (completeness-corrected) vs the Weichert GR."""
    edges = np.arange(wch["mmin"], mags.max() + dm + 1e-9, dm)
    n = np.histogram(mags, bins=edges)[0].astype(float)
    t = np.array([np.median(periods[(mags >= lo) & (mags < hi)])
                  if ((mags >= lo) & (mags < hi)).any() else np.nan
                  for lo, hi in zip(edges[:-1], edges[1:])])
    for i in range(len(t)):
        if np.isnan(t[i]):
            prev = t[:i][~np.isnan(t[:i])]
            t[i] = prev[-1] if len(prev) else np.nan
    inc = np.where(np.isfinite(t) & (t > 0), n / t, np.nan)
    cumr = np.nancumsum(inc[::-1])[::-1]
    m = np.arange(wch["mmin"], mags.max() + dm, dm)
    gr = wch["rate_mmin"] * 10.0 ** (-wch["b"] * (m - wch["mmin"]))

    fig, ax = plt.subplots(figsize=(5.5, 4))
    ok = np.isfinite(cumr) & (cumr > 0)
    ax.plot(edges[:-1][ok], cumr[ok], "k.", label="catalog (Weichert periods)")
    ax.plot(m, gr, color="seagreen",
            label=f"b={wch['b']:.2f}±{wch['b_err']:.2f}, "
                  f"N(≥{wch['mmin']:.1f})={wch['rate_mmin']:.3f}/yr")
    ax.set_yscale("log")
    ax.set_xlabel("M")
    ax.set_ylabel("N(>=M) (/yr)")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[plot_class_fit] wrote {png}")


def plot_total_mfd(per_class: dict[str, np.ndarray], edges: np.ndarray,
                   png: Path):
    """Per-class and total incremental/cumulative MFDs of the superposed SSM."""
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    total = None
    for name, rb in per_class.items():
        r = rb.sum(axis=0)
        total = r if total is None else total + r
        for A, y in zip(ax, (r, np.cumsum(r[::-1])[::-1])):
            m = y > 0
            A.step(edges[:-1][m], y[m], where="post", lw=1, label=name)
    for A, y in zip(ax, (total, np.cumsum(total[::-1])[::-1])):
        m = y > 0
        A.step(edges[:-1][m], y[m], where="post", lw=2, color="k", label="total")
        A.set_yscale("log")
        A.set_xlabel("M")
        A.grid(alpha=0.3)
    ax[0].set_ylabel("incremental rate (/yr)")
    ax[1].set_ylabel("cumulative rate N(>=M) (/yr)")
    ax[0].legend(fontsize=8)
    fig.suptitle("SSM crustal: per-class superposition")
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[plot_total_mfd] wrote {png}")


def plot_rate_map(grid: pd.DataFrame, values: np.ndarray, title: str,
                  png: Path):
    fig, ax = plt.subplots(figsize=(5, 9))
    v = safe_log10(values)
    m = np.isfinite(v)
    ax.scatter(grid.loc[~m, "lon"], grid.loc[~m, "lat"], s=1, c=".9")
    sc = ax.scatter(grid.loc[m, "lon"], grid.loc[m, "lat"], s=3, c=v[m],
                    cmap="magma_r")
    plt.colorbar(sc, ax=ax, label="log10 rate (/yr/cell)")
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[plot_rate_map] wrote {png}")