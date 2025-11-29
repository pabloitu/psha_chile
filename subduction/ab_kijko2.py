# ab_kijko.py
"""
Subduction interface a–b estimation with Kijko & Smit (2012),
supporting latitude segments and a hazard Mmin (default 5.5).

Now uses AB_CONFIG from subduction.config, where:
  - max_depth_km is wired to GEOMETRY_CONFIG.z_bottom_locked
  - depth_column is set to "depth"
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, List, Dict

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from subduction.config import AB_CONFIG, ABConfig, SegmentConfig


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

    Returns DataFrame with:
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

    # Optional depth filter (now wired via AB_CONFIG)
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
# 2. Build Kijko–Smit completeness table from MC_SUMMARY
# ---------------------------------------------------------------------------

def build_completeness_table_from_mc_summary(
    mc_df: pd.DataFrame,
) -> np.ndarray:
    """
    Build a Kijko–Smit completeness table from an MC summary like:

        start_iso, end_iso, N, Mc, b, Years

    Strategy:
        - For each unique Mc, take the earliest start_year
        - Return table [[Mc_i, start_year_i], ...] sorted by Mc ascending

    This matches the KS convention:
        - column 0: lower edge of magnitude bin
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


# ---------------------------------------------------------------------------
# 3. Kijko–Smit implementation (on years)
# ---------------------------------------------------------------------------

def estimate_b_kijko_smit_years(
    magnitudes: np.ndarray,
    years: np.ndarray,
    completeness_table: np.ndarray,
    last_year: Optional[int | float] = None,
    delta_m: float = 0.1,
    b_parameter: str = "b_value",
) -> Tuple[float, float, float, float]:
    """
    Kijko & Smit (2012) b-value and a-value for unequal completeness periods,
    operating directly on numerical years (no datetime64).

    Args:
        magnitudes:
            1D array of magnitudes.
        years:
            1D array of integer (or float) years, same length as magnitudes.
        completeness_table:
            Nx2 array:
                col 0: completeness magnitudes (Mc_i, ascending)
                col 1: completeness years (year_i)
        last_year:
            Last year of observation. If None, uses max(years).
        delta_m:
            Magnitude bin width (0.1).
        b_parameter:
            'b_value' (G–R b) or 'beta' (exponential rate parameter).

    Returns
    -------
        b_parameter, std_b_parameter, rate_at_lmc, a_val

        where:
          - rate_at_lmc: rate at lowest completeness magnitude
          - a_val: log10(rate at M=0) in G–R law
    """
    mags = np.asarray(magnitudes, dtype=float)
    years = np.asarray(years, dtype=float)
    comp = np.asarray(completeness_table, dtype=float)

    assert comp.shape[1] == 2, "completeness_table must have shape (N, 2)"

    if last_year is None:
        last_year = float(np.max(years))
    else:
        last_year = float(last_year)

    completeness_magnitudes = comp[:, 0]
    completeness_years = comp[:, 1]

    # Ensure magnitudes ascending
    if not np.all(np.diff(completeness_magnitudes) >= -1e-8):
        raise ValueError("completeness_table magnitudes must be ascending")

    # Determine, for each event, which completeness level applies
    insertion_indices = np.searchsorted(-completeness_years, -years)

    # Subcatalogues and number of complete events
    sub_catalogues: list[np.ndarray] = []
    ncomplete = 0
    for idx in range(len(completeness_magnitudes)):
        mc_i = completeness_magnitudes[idx]
        subcat = mags[(insertion_indices == idx) & (mags > mc_i)]
        sub_catalogues.append(subcat)
        ncomplete += len(subcat)

    if ncomplete == 0:
        raise ValueError("No complete events for Kijko–Smit estimation")

    # Eq. (7) of Kijko & Smit (2012)
    estimator_terms = []
    for mc_i, subcat_mags in zip(completeness_magnitudes, sub_catalogues):
        if len(subcat_mags) == 0:
            continue
        # β_i = 1 / (mean(M) - Mc_i); Aki-style for each subcatalog
        sub_beta = 1.0 / (np.mean(subcat_mags) - mc_i)
        estimator_terms.append((len(subcat_mags) / ncomplete) / sub_beta)

    beta = 1.0 / np.sum(estimator_terms)

    # Std dev of β (Eq. 8)
    std_beta = beta / np.sqrt(ncomplete)

    if b_parameter == "b_value":
        b = beta / np.log(10.0)
        std_b = std_beta / np.log(10.0)
    else:
        b = beta
        std_b = std_beta

    # Rate at lowest completeness magnitude Mc0 (Eq. 10)
    mc0 = completeness_magnitudes[0]
    denominator_rate = 0.0
    for mc_i, yc in zip(completeness_magnitudes, completeness_years):
        denominator_rate += (last_year - yc) * np.exp(-beta * (mc_i - mc0))

    rate_at_lmc = ncomplete / denominator_rate

    # a-value for GR at M=0 (same convention as seismostats)
    a_val = np.log10(rate_at_lmc) + (beta / np.log(10.0)) * (
        mc0 + delta_m * 0.5
    )

    return float(b), float(std_b), float(rate_at_lmc), float(a_val)


def estimate_ab_kijko_smit_from_catalog(
    df_cat: pd.DataFrame,
    completeness_table: np.ndarray,
    delta_m: float = 0.1,
    b_parameter: str = "b_value",
) -> dict:
    """
    Compute a, b, etc from a catalog and a KS completeness table.

    df_cat:
        Segment catalog (slab interface, mainshocks, etc.)
        Must contain:
            - mag
            - year

    completeness_table:
        Nx2 array [[Mc_i, year_i], ...] from build_completeness_table_from_mc_summary.

    Returns:
        dict with:
            - a           (GR a-value at M=0)
            - b
            - std_b
            - mc0         (lowest completeness magnitude)
            - year0       (completeness year for mc0)
            - rate_at_mc0 (rate at lowest completeness magnitude)
            - last_year   (max year in segment catalog)
            - T_eff       (effective time span year0–last_year)
            - delta_m
    """
    mags = df_cat["mag"].to_numpy(float)
    years = df_cat["year"].to_numpy(int)

    last_year = years.max()

    b, std_b, rate_at_lmc, a_val = estimate_b_kijko_smit_years(
        magnitudes=mags,
        years=years,
        completeness_table=completeness_table,
        last_year=last_year,
        delta_m=delta_m,
        b_parameter=b_parameter,
    )

    mc0 = float(completeness_table[0, 0])
    year0 = int(completeness_table[0, 1])
    T_eff = float(last_year - year0)

    return dict(
        a=float(a_val),
        b=float(b),
        std_b=float(std_b),
        mc0=mc0,
        year0=year0,
        rate_at_mc0=float(rate_at_lmc),
        last_year=int(last_year),
        T_eff=T_eff,
        delta_m=float(delta_m),
    )


# ---------------------------------------------------------------------------
# 4. Diagnostics plots (year-based)
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
    label_model: str = "GR (Kijko–Smit)",
    ax: Optional[plt.Axes] = None,
    title: str = "Cumulative MFD (rates per year)",
) -> plt.Axes:
    """
    Plot observed cumulative MFD (log10 rate) and GR model using (a, b).
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

    # GR model: log10 λ(M>=M) = a - b M
    m_model = np.linspace(m_centers.min(), m_centers.max(), 100)
    log10_lambda_model = a - b * m_model
    ax.plot(m_model, log10_lambda_model, linestyle="-", label=label_model)

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

    For each selected row i in completeness_table (Mc_i, year_i):
      - use all events with year >= year_i and M >= Mmin_hazard
      - anchor to the same λ(Mmin_hazard) from KS (so curves meet GR at Mmin)
      - plot all observed MFDs + GR line.

    Saves a single PNG to out_path.
    """
    if mfd_period_count <= 0:
        return

    # completeness_table is Mc ascending (from build_completeness_table_from_mc_summary)
    # We want the last mfd_period_count rows, i.e. most recent completeness periods.
    rows = completeness_table[::-1][:mfd_period_count]  # take from end
    rows = rows[::-1]  # restore chronological order from older -> newer

    a = ks_res["a"]
    b = ks_res["b"]
    lambda_Mmin = 10.0 ** (a - b * Mmin_hazard)

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

        # counts at M >= Mmin_hazard
        mmax_obs = mags_haz.max()
        mag_edges_haz = np.arange(
            Mmin_hazard, mmax_obs + delta_m * 1.0001, delta_m
        )
        counts_haz, _ = np.histogram(mags_haz, bins=mag_edges_haz)
        cum_counts_haz = np.cumsum(counts_haz[::-1])[::-1]
        N_Mmin = cum_counts_haz[0]

        # Anchor this period at the same GR rate at Mmin
        T_anchor = N_Mmin / lambda_Mmin  # years

        mag_edges, _, cum_rates = compute_cumulative_mfd(
            magnitudes=mags_haz,
            T_years=T_anchor,
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

    # Plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # Overlay observed cumulative MFDs
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

    # GR model: same as before
    # Use a reasonable mag range based on all periods
    m_min_model = min(r["mag_edges"][0] for r in period_results)
    m_max_model = max(r["mag_edges"][-1] for r in period_results)
    m_model = np.linspace(m_min_model, m_max_model, 200)
    log10_lambda_model = a - b * m_model
    ax.plot(m_model, log10_lambda_model, linestyle="-", label="GR (Kijko–Smit)")

    ax.set_xlabel("Magnitude")
    ax.set_ylabel("log10 λ(M ≥ M)")
    ax.set_title(
        f"{seg_name}: cumulative MFD\n"
        f"multi completeness periods (anchored at Mmin={Mmin_hazard:.1f})"
    )
    ax.grid(True, linestyle=":", alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Config-driven main: iterate segments, save plots for seg0, serialize JSON
# ---------------------------------------------------------------------------
def run_ab_from_config(cfg: ABConfig = AB_CONFIG) -> Path:
    """
    Run Kijko–Smit a–b estimation for all segments given in ABConfig.

    Returns
    -------
    Path
        Path to the written JSON file with all segment results.
    """
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Load full catalog (with depth filter wired to geometry)
    df_cat_full = load_interface_catalog(
        cfg.catalog_path,
        only_mainshocks=True,
        max_depth_km=cfg.max_depth_km,
        depth_column=cfg.depth_column,
    )

    # 2) Load MC summary and build completeness table
    mc_df = pd.read_csv(cfg.mc_summary_path, sep="\t")
    mc_df = mc_df.sort_values("start_iso")
    completeness_table = build_completeness_table_from_mc_summary(mc_df)

    print("Kijko–Smit completeness table (Mc, year):")
    print(completeness_table)

    results_all: Dict[str, list] = {"segments": []}

    for idx_seg, seg in enumerate(cfg.segments):
        seg_name = seg.segment_id
        print(f"\n=== Segment {idx_seg} / {seg_name} ===")

        df_seg = subset_catalog_by_segment(df_cat_full, seg)
        if df_seg.empty:
            print("  Segment has no events, skipping.")
            continue

        # 3) KS a–b for this segment
        delta_m = cfg.delta_m
        ks_res = estimate_ab_kijko_smit_from_catalog(
            df_seg,
            completeness_table=completeness_table,
            delta_m=delta_m,
            b_parameter="b_value",
        )

        print("  KS results:")
        for k, v in ks_res.items():
            print(f"    {k}: {v}")

        # 4) Hazard Mmin: use earthquakes above hazard_mref (or mc0 if higher)
        mc0 = ks_res["mc0"]
        Mmin_hazard = max(cfg.hazard_mref, mc0)

        # Rate at Mmin_hazard from GR: λ(M≥Mmin) = 10^(a - b * Mmin)
        a = ks_res["a"]
        b = ks_res["b"]
        lambda_Mmin = 10.0 ** (a - b * Mmin_hazard)

        # For MFD diagnostics we still use the complete period wrt mc0
        year0 = ks_res["year0"]
        df_mfd = df_seg[df_seg["year"] >= year0].copy()

        # Observed mags for hazard Mmin
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
            # counts at M >= Mmin_hazard
            # We'll compute cumulative MFD and anchor to λ(Mmin_hazard)
            mmax_obs = mags_haz.max()
            mag_edges_haz = np.arange(
                Mmin_hazard, mmax_obs + delta_m * 1.0001, delta_m
            )
            counts_haz, _ = np.histogram(mags_haz, bins=mag_edges_haz)
            cum_counts_haz = np.cumsum(counts_haz[::-1])[::-1]

            N_Mmin = int(cum_counts_haz[0])
            T_anchor = N_Mmin / lambda_Mmin  # years, for plotting only

        # 5) Store results for this segment (for later subduction model)
        seg_results = {
            "name": seg_name,
            "lat_min": seg.lat_min,
            "lat_max": seg.lat_max,
            "ks_results": ks_res,
            "hazard_params": {
                "Mmin_hazard": float(Mmin_hazard),
                "lambda_Mmin": float(lambda_Mmin),
                "T_anchor_Mmin": float(T_anchor) if T_anchor is not None else None,
                "N_events_Mmin": N_Mmin,
            },
        }
        results_all["segments"].append(seg_results)

        # 6) Plots ONLY for segment 0 (seg0_full)
        if idx_seg == 0:
            # 6a) Magnitude–time plot
            fig1, ax1 = plt.subplots(figsize=(9, 4))
            plot_magnitude_time(
                df_seg,
                mc0=mc0,
                completeness_table=completeness_table,
                ax=ax1,
                title=f"{seg_name}: slab interface mainshocks (KS completeness)",
            )
            fig1.tight_layout()
            fig1.savefig(cfg.output_dir / f"{seg_name}_magtime.png", dpi=200)
            plt.close(fig1)

            # 6b) Cumulative MFD anchored at Mmin_hazard
            if T_anchor is not None:
                mag_edges, _, cum_rates = compute_cumulative_mfd(
                    magnitudes=mags_haz,
                    T_years=T_anchor,
                    mmin=Mmin_hazard,
                    delta_m=delta_m,
                )

                fig2, ax2 = plt.subplots(figsize=(6, 6))
                plot_cumulative_mfd(
                    mag_edges=mag_edges,
                    cum_rates=cum_rates,
                    a=a,
                    b=b,
                    label_data=(
                        f"Observed {seg_name} (year ≥ {year0}, M≥{Mmin_hazard:.1f})"
                    ),
                    label_model="GR (Kijko–Smit)",
                    ax=ax2,
                    title=(
                        f"{seg_name}: cumulative MFD\n"
                        f"anchored at Mmin={Mmin_hazard:.1f}"
                    ),
                )
                fig2.tight_layout()
                fig2.savefig(
                    cfg.output_dir
                    / f"{seg_name}_mfd_Mmin{Mmin_hazard:.1f}.png",
                    dpi=200,
                )
                plt.close(fig2)

    # 7) Serialize all segments to JSON (same structure as before)
    json_path = cfg.output_dir / "subduction_ab_results.json"
    with json_path.open("w") as f:
        json.dump(results_all, f, indent=2)

    print(f"\nSerialized a–b results to {json_path}")
    print(f"Plots saved in {cfg.output_dir}")

    return json_path


if __name__ == "__main__":
    out_json = run_ab_from_config()
    print(f"a–b results written to {out_json}")
