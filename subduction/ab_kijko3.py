# ab_kijko.py
"""
Subduction interface a–b estimation with three estimators:

1. Kijko–Smit / Taroni (multi-period completeness, on years)
2. Aki–Utsu (last completeness period only)
3. Weichert (1980) (multi-period, on years, unequal completeness)

All configuration comes from AB_CONFIG in subduction.config, where:
  - max_depth_km is typically wired to GEOMETRY_CONFIG.z_bottom_locked
  - depth_column gives the depth field in the catalog (e.g. "depth")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, List, Dict

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import minimize

from subduction.config import AB_CONFIG, ABConfig, SegmentConfig



DEBUG_KS = False
DEBUG_WEICHERT = False
DEBUG_AKI = False


# ---------------------------------------------------------------------------
# 1. Catalog loading (years, optional depth filter)
# ---------------------------------------------------------------------------

def load_interface_catalog(
    cat_path: str | Path,
    only_mainshocks: bool = True,
    max_depth_km: Optional[float] = None,
    depth_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load declustered slab-interface catalog.

    Expects at least:
        - time_iso (str, ISO like "1513-01-01T00:00:00")
        - mag (float)
        - latitude (float)
        - is_mainshock (bool, optional)
        - depth column (optional, if depth filtering is requested)

    Returns DataFrame with (at least):
        - mag (float)
        - year (int)
        - latitude (float)
        - time_iso (for reference)
      plus any original columns.
    """
    df = pd.read_csv(cat_path)

    if only_mainshocks and "is_mainshock" in df.columns:
        df = df[df["is_mainshock"] == True].copy()

    df["time_iso"] = df["time_iso"].astype(str)
    df["year"] = df["time_iso"].str.slice(0, 4).astype(int)
    df["mag"] = df["mag"].astype(float)

    if "latitude" not in df.columns:
        raise ValueError("Catalog must contain a 'latitude' column for segmentation")

    # Optional depth filter (wired via AB_CONFIG)
    if max_depth_km is not None and depth_column is not None:
        if depth_column not in df.columns:
            raise ValueError(
                f"Requested depth filtering on column '{depth_column}', "
                f"but this column is not present in the catalog."
            )
        df = df[df[depth_column] <= max_depth_km].copy()

    return df


def subset_catalog_by_segment(df: pd.DataFrame, seg: SegmentConfig) -> pd.DataFrame:
    """
    Filter catalog by latitude segment.
    """
    df_seg = df.copy()
    if seg.lat_min is not None:
        df_seg = df_seg[df_seg["latitude"] >= seg.lat_min]
    if seg.lat_max is not None:
        df_seg = df_seg[df_seg["latitude"] <= seg.lat_max]
    return df_seg


# ---------------------------------------------------------------------------
# 2. Completeness helpers
# ---------------------------------------------------------------------------

def build_completeness_table_from_mc_summary(
    mc_df: pd.DataFrame,
) -> np.ndarray:
    """
    Build a magnitude-level completeness table from an MC summary like:

        start_iso, end_iso, N, Mc, b, Years

    Strategy:
        - For each unique Mc, take the earliest start_year
        - Return table [[Mc_i, start_year_i], ...] sorted by Mc ascending

    This matches the "magnitude-level" convention:
        - column 0: completeness magnitude Mc_i
        - column 1: year after which M >= Mc_i is complete
    """
    mc_df = mc_df.copy()
    mc_df["start_iso"] = mc_df["start_iso"].astype(str)
    mc_df["start_year"] = mc_df["start_iso"].str.slice(0, 4).astype(int)

    grp = (
        mc_df.groupby("Mc", as_index=False)["start_year"]
        .min()
        .rename(columns={"start_year": "year"})
    )

    grp = grp.sort_values("Mc")
    completeness_table = grp[["Mc", "year"]].to_numpy(float)
    return completeness_table


def get_last_period_from_mc_summary(mc_df: pd.DataFrame) -> Tuple[float, int]:
    """
    Extract (Mc_last, year_last) from the *original* MC summary,
    i.e. the last row when sorted by start_iso.

    This is useful for Aki using the last completeness period only.
    """
    mc_df = mc_df.sort_values("start_iso")
    last_row = mc_df.iloc[-1]
    Mc_last = float(last_row["Mc"])
    year_last = int(str(last_row["start_iso"])[:4])
    return Mc_last, year_last


# ---------------------------------------------------------------------------
# 3. Kijko–Taroni estimator (multi-period, magnitude-level completeness)
# ---------------------------------------------------------------------------

def estimate_b_kijko_taroni_years(
    magnitudes: np.ndarray,
    years: np.ndarray,
    completeness_table: np.ndarray,
    last_year: Optional[int | float] = None,
    delta_m: float = 0.1,
    b_parameter: str = "b_value",
) -> Tuple[float, float, float, float, int, float, float]:
    """
    Kijko & Smit / Taroni-style b-value and a-value for unequal
    completeness periods, using magnitude-level completeness.

    completeness_table:
        (N, 2) array:
            col 0: completeness magnitudes (Mc_i)
            col 1: completeness years (year_i)

    For each level i:
        - use all events with year >= year_i and M >= Mc_i
        - compute β_i from Aki ML for that subcatalog
        - combine β_i with weights N_i / sum N_i

    Returns
    -------
    b_parameter, std_b_parameter, rate_at_mc0, a_val, ncomplete, mc0, year0
    """
    mags = np.asarray(magnitudes, dtype=float)
    yrs = np.asarray(years, dtype=float)
    comp = np.asarray(completeness_table, dtype=float)

    if comp.shape[1] != 2:
        raise ValueError("completeness_table must have shape (N, 2)")

    # Sort by Mc ascending
    idx_sort = np.argsort(comp[:, 0])
    comp = comp[idx_sort]
    completeness_magnitudes = comp[:, 0]
    completeness_years = comp[:, 1]

    if last_year is None:
        last_year = float(np.max(yrs))
    else:
        last_year = float(last_year)

    if DEBUG_KS:
        print("\n[DEBUG KS] completeness_table (Mc, year):")
        for mc_i, yc in zip(completeness_magnitudes, completeness_years):
            print(f"  Mc={mc_i:.2f}, year={int(yc)}")
        print(f"[DEBUG KS] years range in catalog: {yrs.min()} – {yrs.max()}")
        print(f"[DEBUG KS] magnitudes range: {mags.min():.2f} – {mags.max():.2f}")

    level_info: List[dict] = []

    for i, (mc_i, yc) in enumerate(zip(completeness_magnitudes, completeness_years)):
        mask = (yrs >= yc) & (mags >= mc_i)
        Ni = int(mask.sum())
        if Ni == 0:
            if DEBUG_KS:
                print(f"[DEBUG KS] level {i}: Mc={mc_i:.2f}, year={int(yc)} -> N=0 (skipped)")
            level_info.append(dict(index=i, mc=mc_i, year=yc, N=0))
            continue

        sub_m = mags[mask]
        mean_M = float(sub_m.mean())
        m_shift = mc_i - delta_m * 0.5
        denom = mean_M - m_shift
        if denom <= 0:
            raise ValueError(
                f"[KS] Denominator <= 0 at level {i}: "
                f"mean_M={mean_M:.3f}, mc_i={mc_i:.3f}, delta_m={delta_m}"
            )
        beta_i = 1.0 / denom

        info = dict(
            index=i,
            mc=mc_i,
            year=yc,
            N=Ni,
            mean_M=mean_M,
            beta_i=beta_i,
        )
        level_info.append(info)

        if DEBUG_KS:
            print(
                f"[DEBUG KS] level {i}: Mc={mc_i:.2f}, year={int(yc)}, "
                f"N={Ni}, mean_M={mean_M:.3f}, beta_i={beta_i:.5f}"
            )

    valid_levels = [info for info in level_info if info.get("N", 0) > 0]
    if len(valid_levels) == 0:
        raise ValueError("No complete levels for Kijko–Taroni estimation")

    Ntotal = sum(info["N"] for info in valid_levels)

    # Combine β_i with weights N_i / N_total
    sum_term = 0.0
    for info in valid_levels:
        Ni = info["N"]
        beta_i = info["beta_i"]
        sum_term += (Ni / Ntotal) / beta_i

    beta = 1.0 / sum_term
    std_beta = beta / np.sqrt(Ntotal)

    if b_parameter == "b_value":
        b = beta / np.log(10.0)
        std_b = std_beta / np.log(10.0)
    else:
        b = beta
        std_b = std_beta

    # Lowest completeness magnitude actually used
    mc0 = min(info["mc"] for info in valid_levels)
    year0 = min(info["year"] for info in valid_levels)

    # Rate at M >= mc0
    denominator_rate = 0.0
    for info in valid_levels:
        mc_i = info["mc"]
        yc = info["year"]
        Ti = last_year - yc
        denominator_rate += Ti * np.exp(-beta * (mc_i - mc0))

    rate_at_mc0 = Ntotal / denominator_rate

    # a-value at M=0, consistent with GR: log10 λ(M>=M) = a - b M
    # => a = log10 λ(M>=mc0) + b * mc0
    a_val = np.log10(rate_at_mc0) + b * mc0

    if DEBUG_KS:
        print("[DEBUG KS] valid levels used:", len(valid_levels))
        print(f"[DEBUG KS] Ntotal = {Ntotal}")
        print(f"[DEBUG KS] beta   = {beta:.5f}")
        print(f"[DEBUG KS] b      = {b:.5f}")
        print(f"[DEBUG KS] rate_at_mc0 (per year) = {rate_at_mc0:.5f}")
        print(f"[DEBUG KS] mc0 = {mc0:.2f}, year0 = {int(year0)}")
        print(f"[DEBUG KS] a (per year at M=0) = {a_val:.5f}")

    return float(b), float(std_b), float(rate_at_mc0), float(a_val), int(Ntotal), float(mc0), float(year0)


def estimate_ab_kijko_taroni_from_catalog(
    df_cat: pd.DataFrame,
    completeness_table: np.ndarray,
    delta_m: float = 0.1,
    b_parameter: str = "b_value",
) -> dict:
    """
    Convenience wrapper for Kijko–Smit / Taroni estimator.
    """
    mags = df_cat["mag"].to_numpy(float)
    years = df_cat["year"].to_numpy(int)

    last_year = years.max()

    b, std_b, rate_at_mc0, a_val, ncomplete, mc0, year0 = estimate_b_kijko_taroni_years(
        magnitudes=mags,
        years=years,
        completeness_table=completeness_table,
        last_year=last_year,
        delta_m=delta_m,
        b_parameter=b_parameter,
    )

    T_eff = float(last_year - year0)

    return dict(
        a=float(a_val),
        b=float(b),
        std_b=float(std_b),
        mc0=float(mc0),
        year0=int(year0),
        rate_at_mc0=float(rate_at_mc0),
        last_year=int(last_year),
        T_eff=T_eff,
        delta_m=float(delta_m),
        ncomplete=int(ncomplete),
    )


# ---------------------------------------------------------------------------
# 4. Aki–Utsu estimator (last completeness period only)
# ---------------------------------------------------------------------------

def estimate_ab_aki_last_period(
    df_cat: pd.DataFrame,
    Mc_ref: float,
    year_ref: int,
    delta_m: float = 0.1,
) -> Optional[dict]:
    """
    Aki–Utsu maximum-likelihood b-value using *only* the last
    completeness period: year >= year_ref and M >= Mc_ref.

    Returns None if there are no events in that period.
    """
    df_period = df_cat[(df_cat["year"] >= year_ref) & (df_cat["mag"] >= Mc_ref)].copy()
    if df_period.empty:
        if DEBUG_AKI:
            print("[DEBUG AKI] No events in last completeness period.")
        return None

    mags = df_period["mag"].to_numpy(float)
    N = len(mags)
    mbar = mags.mean()

    m_shift = Mc_ref - delta_m * 0.5
    denom = mbar - m_shift
    if denom <= 0:
        raise ValueError(
            f"[AKI] Denominator <= 0: mbar={mbar:.3f}, Mc_ref={Mc_ref:.3f}, delta_m={delta_m}"
        )

    # Aki (1965) / Utsu (1966) ML b-value:
    # b = log10(e) / (mbar - (Mc_ref - ΔM/2))
    b = np.log10(np.e) / denom
    std_b = b / np.sqrt(N)

    last_year = int(df_cat["year"].max())
    T_eff = float(last_year - year_ref)

    # Rate at M_ref: N events above Mc_ref over T_eff
    if T_eff > 0:
        rate_at_Mref = N / T_eff
    else:
        rate_at_Mref = float("nan")

    # a-value at M=0: log10 λ(M>=M) = a - b M
    # => a = log10 λ(M>=Mc_ref) + b * Mc_ref
    if rate_at_Mref > 0:
        a_val = np.log10(rate_at_Mref) + b * Mc_ref
    else:
        a_val = float("nan")

    if DEBUG_AKI:
        print("\n[DEBUG AKI] Last period:")
        print(f"  Mc_ref   = {Mc_ref:.2f}")
        print(f"  year_ref = {year_ref}")
        print(f"  N        = {N}")
        print(f"  mbar     = {mbar:.3f}")
        print(f"  b        = {b:.5f}")
        print(f"  std_b    = {std_b:.5f}")
        print(f"  T_eff    = {T_eff:.2f}")
        print(f"  rate_at_Mref (per year) = {rate_at_Mref:.5f}")
        print(f"  a (per year at M=0)     = {a_val:.5f}")

    return dict(
        a=float(a_val),
        b=float(b),
        std_b=float(std_b),
        Mc_ref=float(Mc_ref),
        year_ref=int(year_ref),
        rate_at_Mref=float(rate_at_Mref),
        last_year=last_year,
        T_eff=T_eff,
        delta_m=float(delta_m),
        N=int(N),
    )


# ---------------------------------------------------------------------------
# 5. Weichert (1980) estimator (on years, no datetime64)
# ---------------------------------------------------------------------------

def _beta_to_b_value(beta: float) -> float:
    return beta / np.log(10.0)


def estimate_b_weichert_years(
    magnitudes: np.ndarray,
    years: np.ndarray,
    completeness_table: np.ndarray,
    mag_max: int | float,
    last_year: int | float | None = None,
    delta_m: float = 0.1,
    b_parameter: str = "b_value",
) -> Tuple[float, float, float, float, float]:
    """
    Weichert (1980) GR estimation for unequal completeness periods,
    using calendar years instead of datetimes.

    completeness_table:
        magnitude-level completeness [[Mc_i, year_i], ...]
    """
    magnitudes = np.asarray(magnitudes, dtype=float)
    years = np.asarray(years, dtype=float)

    assert len(magnitudes) == len(years), "magnitudes and years must have same length"
    assert completeness_table.shape[1] == 2, "completeness_table must have shape (N, 2)"
    assert np.all(np.ediff1d(completeness_table[:, 0]) >= 0), \
        "magnitudes in completeness table not in ascending order"
    assert delta_m > 0, "delta_m must be positive"
    assert b_parameter in {"b_value", "beta"}, "b_parameter must be 'b_value' or 'beta'"

    if last_year is None:
        last_year = float(np.max(years))
    else:
        last_year = float(last_year)

    completeness_table_magnitudes = completeness_table[:, 0]
    completeness_table_years = completeness_table[:, 1]

    # Round magnitudes to the magnitude grid
    mags_rounded = np.round(magnitudes / delta_m) * delta_m

    if DEBUG_WEICHERT:
        print("\n[DEBUG WEICHERT] completeness_table (Mc, year):")
        for mc_i, yc in zip(completeness_table_magnitudes, completeness_table_years):
            print(f"  Mc={mc_i:.2f}, year={int(yc)}")
        print(f"[DEBUG WEICHERT] years range: {years.min()} – {years.max()}")
        print(f"[DEBUG WEICHERT] mags range (rounded): {mags_rounded.min():.2f} – {mags_rounded.max():.2f}")

    # Determine completeness start year for each magnitude (similar logic to statseis)
    insertion_indices = np.searchsorted(completeness_table_magnitudes, mags_rounded)
    completeness_starts = np.array(
        [
            (
                completeness_table_years[idx - 1]
                if idx not in (0, len(completeness_table_years))
                else {
                    0: -1,
                    len(completeness_table_years): completeness_table_years[-1],
                }[idx]
            )
            for idx in insertion_indices
        ]
    )

    # Filter events inside completeness window
    idxcomp = (completeness_starts > 0) & (years - completeness_starts >= 0)
    if not np.any(idxcomp):
        raise ValueError("No complete events for Weichert estimation")

    df_events = pd.DataFrame(
        {
            "mag": mags_rounded[idxcomp],
            "completeness_start": completeness_starts[idxcomp],
        }
    )

    # Bin edges for pd.cut (left-closed, right-open)
    mag_bins = np.arange(
        completeness_table_magnitudes[0],
        mag_max + delta_m * 1.01,
        delta_m,
    )

    cut_result = pd.cut(df_events["mag"], bins=mag_bins, right=False)

    # Drop events that fell outside bins (NaN intervals)
    mask_valid = cut_result.notna()
    df_events = df_events[mask_valid].copy()
    cut_valid = cut_result[mask_valid]

    # Extract left edges of intervals
    mag_left_edges = np.array([iv.left for iv in cut_valid])

    df_events["mag_left_edge"] = mag_left_edges

    # Group by magnitude bin and completeness start
    complete_events = (
        df_events.groupby(["mag_left_edge", "completeness_start"])
        .size()
        .to_frame("num")
        .reset_index()
    )

    if complete_events.empty:
        raise ValueError("No complete events in magnitude bins for Weichert estimation")

    mag_left = complete_events["mag_left_edge"].to_numpy(float)
    comp_start = complete_events["completeness_start"].to_numpy(float)
    num = complete_events["num"].to_numpy(float)

    if DEBUG_WEICHERT:
        print("[DEBUG WEICHERT] complete_events (first 10 rows):")
        print(complete_events.head(10))
        print(f"[DEBUG WEICHERT] total complete events counted = {int(num.sum())}")

    # Objective function (Weichert 1980)
    def _obj(beta: float) -> float:
        magbins = mag_left + delta_m * 0.5
        nom = np.sum((last_year - comp_start) * magbins * np.exp(-beta * magbins))
        denom = np.sum((last_year - comp_start) * np.exp(-beta * magbins))
        left = nom / denom
        right = np.sum(num * magbins) / np.sum(num)
        return abs(left - right)

    beta0 = np.log(10.0)
    solution = minimize(
        _obj,
        beta0,
        method="Nelder-Mead",
        options={"maxiter": 5000, "disp": False},
        tol=1e5 * np.finfo(float).eps,
    )
    beta = float(solution.x[0])

    magbins = mag_left + delta_m * 0.5

    # Rate at lower magnitude of completeness (leftmost mag bin)
    weichert_multiplier = np.sum(np.exp(-beta * magbins)) / np.sum(
        (last_year - comp_start) * np.exp(-beta * magbins)
    )
    rate_at_lmc = np.sum(num) * weichert_multiplier

    # a-value at M=0: a = log10(rate_at_Mc0) + b * Mc0
    mc0 = float(mag_left.min())
    if b_parameter == "b_value":
        b = _beta_to_b_value(beta)
    else:
        b = beta
    a_val = np.log10(rate_at_lmc) + b * mc0

    # Uncertainty in beta and rate (Weichert 1980)
    nominator = (
        np.sum(
            (last_year - comp_start)
            * np.exp(-beta * magbins)
        )
        ** 2
    )
    denominator_term1 = (
        np.sum(
            (last_year - comp_start)
            * magbins
            * np.exp(-beta * magbins)
        )
        ** 2
    )
    denominator_term2 = np.sqrt(nominator) * np.sum(
        (last_year - comp_start)
        * (magbins ** 2)
        * np.exp(-beta * magbins)
    )
    var_beta = (
        -(1.0 / np.sum(num))
        * nominator
        / (denominator_term1 - denominator_term2)
    )
    std_beta = float(np.sqrt(var_beta))

    if b_parameter == "b_value":
        std_b = _beta_to_b_value(std_beta)
    else:
        std_b = std_beta

    std_rate_at_lmc = rate_at_lmc / np.sqrt(np.sum(num))

    if DEBUG_WEICHERT:
        print("[DEBUG WEICHERT] beta   =", beta)
        print("[DEBUG WEICHERT] b      =", b)
        print("[DEBUG WEICHERT] rate_at_lmc (per year) =", rate_at_lmc)
        print("[DEBUG WEICHERT] mc0    =", mc0)
        print("[DEBUG WEICHERT] a      =", a_val)
        print("[DEBUG WEICHERT] std_b  =", std_b)
        print("[DEBUG WEICHERT] std_rate_at_lmc =", std_rate_at_lmc)

    return float(b), float(std_b), float(rate_at_lmc), float(std_rate_at_lmc), float(a_val)


def estimate_ab_weichert_from_catalog(
    df_cat: pd.DataFrame,
    completeness_table: np.ndarray,
    delta_m: float = 0.1,
    mag_max: Optional[float] = None,
    b_parameter: str = "b_value",
) -> dict:
    """
    Convenience wrapper for Weichert (1980) estimator.
    """
    mags = df_cat["mag"].to_numpy(float)
    years = df_cat["year"].to_numpy(int)

    if mag_max is None:
        mag_max = float(np.ceil(np.max(mags) / delta_m) * delta_m)

    b, std_b, rate_at_lmc, std_rate_at_lmc, a_val = estimate_b_weichert_years(
        magnitudes=mags,
        years=years,
        completeness_table=completeness_table,
        mag_max=mag_max,
        last_year=None,
        delta_m=delta_m,
        b_parameter=b_parameter,
    )

    mc0 = float(completeness_table[:, 0].min())
    year0 = float(completeness_table[completeness_table[:, 0].argmin(), 1])
    last_year = int(np.max(years))
    T_eff = float(last_year - year0)

    return dict(
        a=float(a_val),
        b=float(b),
        std_b=float(std_b),
        mc0=mc0,
        year0=int(year0),
        rate_at_mc0=float(rate_at_lmc),
        std_rate_at_mc0=float(std_rate_at_lmc),
        last_year=last_year,
        T_eff=T_eff,
        delta_m=float(delta_m),
    )


# ---------------------------------------------------------------------------
# 6. Diagnostics plots
# ---------------------------------------------------------------------------

def plot_magnitude_time(
    df: pd.DataFrame,
    mc0: Optional[float] = None,
    completeness_table: Optional[np.ndarray] = None,
    ax: Optional[plt.Axes] = None,
    title: str = "Magnitude–time diagram",
) -> plt.Axes:
    """
    Scatter plot of magnitude vs year for the given catalog.
    Optionally:
      - horizontal line at mc0
      - vertical lines at completeness years.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 4))

    ax.scatter(df["year"], df["mag"], s=15)

    if mc0 is not None:
        ax.axhline(mc0, linestyle="--", color="k")
        ax.text(
            df["year"].min(),
            mc0,
            f" Mc0 = {mc0:.2f}",
            va="bottom",
        )

    if completeness_table is not None:
        yrs = completeness_table[:, 1]
        for y in yrs:
            ax.axvline(y, linestyle=":", color="grey", alpha=0.5)

    ax.set_xlabel("Year")
    ax.set_ylabel("Magnitude")
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.3)

    return ax


def compute_cumulative_mfd(
    magnitudes: np.ndarray,
    T_years: float,
    mmin: float,
    delta_m: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute cumulative MFD from magnitudes with duration T_years.

    Returns:
        mag_edges   (edges of bins)
        cum_counts  (N(M >= M_i))
        cum_rates   (N/T_years)
    """
    mags = np.asarray(magnitudes, dtype=float)
    mags = mags[mags >= mmin - 1e-8]

    if len(mags) == 0:
        raise ValueError("No events above mmin for MFD")

    mmax_obs = mags.max()
    mag_edges = np.arange(mmin, mmax_obs + delta_m * 1.0001, delta_m)

    counts, _ = np.histogram(mags, bins=mag_edges)
    cum_counts = np.cumsum(counts[::-1])[::-1]
    cum_rates = cum_counts / T_years

    return mag_edges, cum_counts, cum_rates


def plot_cumulative_mfd(
    mag_edges: np.ndarray,
    cum_rates: np.ndarray,
    a: float,
    b: float,
    label_data: str = "Observed",
    label_model: str = "GR (primary)",
    ax: Optional[plt.Axes] = None,
    title: str = "Cumulative MFD (rates per year)",
    extra_models: Optional[List[Tuple[str, float, float]]] = None,
) -> plt.Axes:
    """
    Plot observed cumulative MFD (log10 rate) and one or more GR models.

    extra_models: list of (label, a_extra, b_extra)
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    m_centers = 0.5 * (mag_edges[:-1] + mag_edges[1:])

    ax.plot(
        m_centers,
        np.log10(cum_rates),
        marker="o",
        linestyle="none",
        label=label_data,
    )

    # Primary GR model
    m_model = np.linspace(m_centers.min(), m_centers.max(), 100)
    log10_lambda_model = a - b * m_model
    ax.plot(m_model, log10_lambda_model, linestyle="-", label=label_model)

    # Extra GR models
    if extra_models:
        for label_extra, a_extra, b_extra in extra_models:
            log10_lambda_extra = a_extra - b_extra * m_model
            ax.plot(m_model, log10_lambda_extra, linestyle="--", label=label_extra)

    ax.set_xlabel("Magnitude")
    ax.set_ylabel("log10 λ(M ≥ M)")
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.3)
    ax.legend()

    return ax


def plot_multi_period_mfds(
    df_seg: pd.DataFrame,
    ks_res: dict,
    completeness_table: np.ndarray,
    Mmin_hazard: float,
    delta_m: float,
    mfd_period_count: int,
    seg_name: str,
    out_path: Path,
) -> None:
    """
    Extra diagnostic: compare cumulative MFDs for several completeness
    periods, going backwards from the most recent completeness row.

    Same idea as before, but we keep KS a,b as primary GR.
    """
    if mfd_period_count <= 0:
        return

    # completeness_table is Mc ascending; we want most recent levels at the end
    rows = completeness_table[::-1][:mfd_period_count]
    rows = rows[::-1]

    a = ks_res["a"]
    b = ks_res["b"]

    period_results = []

    for Mc_i, year_i in rows:
        year_i = int(year_i)
        df_period = df_seg[df_seg["year"] >= year_i].copy()
        if df_period.empty:
            continue

        mags = df_period["mag"].to_numpy(float)
        mags_haz = mags[mags >= Mmin_hazard - 1e-8]
        if len(mags_haz) == 0:
            continue

        # For plotting we approximate using the same T_eff for all periods:
        last_year = int(df_seg["year"].max())
        T_years = float(last_year - year_i)

        mag_edges, _, cum_rates = compute_cumulative_mfd(
            magnitudes=mags_haz,
            T_years=T_years,
            mmin=Mmin_hazard,
            delta_m=delta_m,
        )

        period_results.append(
            dict(
                Mc=float(Mc_i),
                year_start=year_i,
                mag_edges=mag_edges,
                cum_rates=cum_rates,
            )
        )

    if not period_results:
        return

    fig, ax = plt.subplots(figsize=(6, 6))

    for res in period_results:
        mag_edges = res["mag_edges"]
        cum_rates = res["cum_rates"]
        m_centers = 0.5 * (mag_edges[:-1] + mag_edges[1:])

        label = f"obs year ≥ {res['year_start']} (Mc ≥ {res['Mc']:.1f})"
        ax.plot(
            m_centers,
            np.log10(cum_rates),
            marker="o",
            linestyle="none",
            label=label,
        )

    # GR model (KS/Taroni)
    m_min_model = min(r["mag_edges"][0] for r in period_results)
    m_max_model = max(r["mag_edges"][-1] for r in period_results)
    m_model = np.linspace(m_min_model, m_max_model, 200)
    log10_lambda_model = a - b * m_model
    ax.plot(m_model, log10_lambda_model, linestyle="-", label="GR (KS/Taroni)")

    ax.set_xlabel("Magnitude")
    ax.set_ylabel("log10 λ(M ≥ M)")
    ax.set_title(
        f"{seg_name}: cumulative MFD\n"
        f"multi completeness periods (Mmin={Mmin_hazard:.1f})"
    )
    ax.grid(True, linestyle=":", alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 7. Config-driven main
# ---------------------------------------------------------------------------
def run_ab_from_config(cfg: ABConfig = AB_CONFIG) -> Path:
    """
    Run a–b estimation for all segments given in ABConfig using:

      - Kijko–Smit / Taroni (multi-period)  [PRIMARY]
      - Aki (last completeness period)      [diagnostic only]
      - Weichert (multi-period)             [diagnostic only]

    JSON output is simplified and only contains the primary
    Kijko–Taroni parameters (a, b, std_b, mc0, year0, etc.)
    plus hazard_params for each segment.
    """
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Load full catalog (with depth filter wired to geometry)
    df_cat_full = load_interface_catalog(
        cfg.catalog_path,
        only_mainshocks=True,
        max_depth_km=cfg.max_depth_km,
        depth_column=cfg.depth_column,
    )

    # 2) Load MC summary and build completeness tables
    mc_df = pd.read_csv(cfg.mc_summary_path, sep="\t")
    mc_df = mc_df.sort_values("start_iso")
    completeness_table = build_completeness_table_from_mc_summary(mc_df)
    Mc_last, year_last = get_last_period_from_mc_summary(mc_df)

    print("Kijko–Taroni magnitude-level completeness (Mc, year):")
    print(completeness_table)

    results_all: Dict[str, list] = {"segments": []}

    for idx_seg, seg in enumerate(cfg.segments):
        seg_name = seg.segment_id
        print(f"\n=== Segment {idx_seg} / {seg_name} ===")

        df_seg = subset_catalog_by_segment(df_cat_full, seg)
        if df_seg.empty:
            print("  Segment has no events, skipping.")
            continue

        delta_m = cfg.delta_m

        # --- 3a) KS/Taroni (PRIMARY) ---
        ks_res = estimate_ab_kijko_taroni_from_catalog(
            df_seg,
            completeness_table=completeness_table,
            delta_m=delta_m,
            b_parameter="b_value",
        )
        print("  Kijko–Taroni results:")
        for k, v in ks_res.items():
            print(f"    {k}: {v}")

        # --- 3b) Aki last period (diagnostic only, NOT written to JSON) ---
        aki_last_res = estimate_ab_aki_last_period(
            df_seg,
            Mc_ref=Mc_last,
            year_ref=year_last,
            delta_m=delta_m,
        )
        if aki_last_res is None:
            print("  Aki (last period) results: no events in last period")
        else:
            print("  Aki (last period) results:")
            for k, v in aki_last_res.items():
                print(f"    {k}: {v}")

        # --- 3c) Weichert (diagnostic only, NOT written to JSON) ---
        try:
            weichert_res = estimate_ab_weichert_from_catalog(
                df_seg,
                completeness_table=completeness_table,
                delta_m=delta_m,
                mag_max=None,
                b_parameter="b_value",
            )
            print("  Weichert results:")
            for k, v in weichert_res.items():
                print(f"    {k}: {v}")
        except Exception as exc:  # noqa: BLE001
            print(f"  Weichert estimation failed: {exc}")
            weichert_res = None

        # --- 4) Hazard Mmin (using KS/Taroni as primary model) ---
        mc0 = ks_res["mc0"]
        Mmin_hazard = max(cfg.hazard_mref, mc0)

        a_ks = ks_res["a"]
        b_ks = ks_res["b"]
        lambda_Mmin = 10.0 ** (a_ks - b_ks * Mmin_hazard)

        year0 = ks_res["year0"]
        df_mfd = df_seg[df_seg["year"] >= year0].copy()

        mags_haz = df_mfd["mag"].to_numpy(float)
        mags_haz = mags_haz[mags_haz >= Mmin_hazard - 1e-8]
        if len(mags_haz) == 0:
            print(
                "  No events above Mmin_hazard in completeness period, "
                "skipping MFD plot."
            )
            T_anchor = None
            N_Mmin = 0
        else:
            mmax_obs = mags_haz.max()
            mag_edges_haz = np.arange(
                Mmin_hazard, mmax_obs + delta_m * 1.0001, delta_m
            )
            counts_haz, _ = np.histogram(mags_haz, bins=mag_edges_haz)
            cum_counts_haz = np.cumsum(counts_haz[::-1])[::-1]

            N_Mmin = int(cum_counts_haz[0])
            T_anchor = N_Mmin / lambda_Mmin  # anchor KS line at Mmin

        # --- 5) Store results for this segment (JSON: ONLY KS/T fields + hazard) ---
        seg_results = {
            "name": seg_name,
            "lat_min": seg.lat_min,
            "lat_max": seg.lat_max,
            # Flatten all Kijko–Taroni parameters at top level:
            #   a, b, std_b, mc0, year0, rate_at_mc0, last_year, T_eff, delta_m, ncomplete
            **ks_res,
            "hazard_params": {
                "Mmin_hazard": float(Mmin_hazard),
                "lambda_Mmin": float(lambda_Mmin),
                "T_anchor_Mmin": float(T_anchor) if T_anchor is not None else None,
                "N_events_Mmin": N_Mmin,
            },
        }
        results_all["segments"].append(seg_results)

        # --- 6) Plots ONLY for segment 0 (diagnostics) ---
        if idx_seg == 0:
            # 6a) Magnitude–time plot
            fig1, ax1 = plt.subplots(figsize=(9, 4))
            plot_magnitude_time(
                df_seg,
                mc0=ks_res["mc0"],
                completeness_table=completeness_table,
                ax=ax1,
                title=f"{seg_name}: slab interface mainshocks (completeness)",
            )
            fig1.tight_layout()
            fig1.savefig(cfg.output_dir / f"{seg_name}_magtime.png", dpi=200)
            plt.close(fig1)

            # 6b) Cumulative MFD from last completeness period only
            #     (so the plot window matches the period used for Aki / “recent hazard”)
            # Use last completeness year_ref, Mc_ref for the diagnostics window
            if aki_last_res is not None:
                year_plot = aki_last_res["year_ref"]
                Mmin_plot = max(Mmin_hazard, aki_last_res["Mc_ref"])
            else:
                year_plot = year0
                Mmin_plot = Mmin_hazard

            df_mfd_last = df_seg[df_seg["year"] >= year_plot].copy()
            mags_haz_last = df_mfd_last["mag"].to_numpy(float)
            mags_haz_last = mags_haz_last[mags_haz_last >= Mmin_plot - 1e-8]

            if len(mags_haz_last) > 0 and T_anchor is not None:
                mag_edges, _, cum_rates = compute_cumulative_mfd(
                    magnitudes=mags_haz_last,
                    T_years=T_anchor,
                    mmin=Mmin_plot,
                    delta_m=delta_m,
                )

                extra_models: List[Tuple[str, float, float]] = []
                if aki_last_res is not None:
                    extra_models.append(
                        ("GR (Aki last period)", aki_last_res["a"], aki_last_res["b"])
                    )
                if weichert_res is not None:
                    extra_models.append(
                        ("GR (Weichert)", weichert_res["a"], weichert_res["b"])
                    )

                fig2, ax2 = plt.subplots(figsize=(6, 6))
                plot_cumulative_mfd(
                    mag_edges=mag_edges,
                    cum_rates=cum_rates,
                    a=a_ks,
                    b=b_ks,
                    label_data=(
                        f"Observed {seg_name} "
                        f"(year ≥ {year_plot}, M≥{Mmin_plot:.1f})"
                    ),
                    label_model="GR (KS/Taroni)",
                    ax=ax2,
                    title=(
                        f"{seg_name}: cumulative MFD\n"
                        f"Mmin={Mmin_plot:.1f}, KS vs Aki vs Weichert"
                    ),
                    extra_models=extra_models,
                )
                fig2.tight_layout()
                fig2.savefig(
                    cfg.output_dir
                    / f"{seg_name}_mfd_Mmin{Mmin_plot:.1f}.png",
                    dpi=200,
                )
                plt.close(fig2)

            # 6c) Multi-period MFDs from completeness table (still anchored to KS)
            multi_mfd_path = cfg.output_dir / (
                f"{seg_name}_mfd_Mmin{Mmin_hazard:.1f}_multi_periods.png"
            )
            plot_multi_period_mfds(
                df_seg=df_seg,
                ks_res=ks_res,
                completeness_table=completeness_table,
                Mmin_hazard=Mmin_hazard,
                delta_m=delta_m,
                mfd_period_count=cfg.mfd_period_count,
                seg_name=seg_name,
                out_path=multi_mfd_path,
            )

    # 7) Serialize all segments to JSON (ONLY KS/T parameters + hazard_params)
    json_path = cfg.output_dir / "subduction_ab_results.json"
    with json_path.open("w") as f:
        json.dump(results_all, f, indent=2)

    print(f"\nSerialized a–b results to {json_path}")
    print(f"Plots saved in {cfg.output_dir}")

    return json_path


if __name__ == "__main__":
    from subduction import config_seg, config_seg_2segs

    # out_json = run_ab_from_config()
    # out_json = run_ab_from_config(config_seg_2segs.AB_CONFIG)
    out_json = run_ab_from_config(config_seg.AB_CONFIG)

    print(f"a–b results written to {out_json}")
