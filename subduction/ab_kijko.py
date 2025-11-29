"""
Subduction interface a–b estimation with Kijko & Smit (2012),
supporting latitude segments and a hazard Mmin (default 5.5).

Features
--------
- Load declustered slab-interface catalog (catalog)
- Build completeness table from MC_SUMMARY (Mc, start_year)
- For each latitude segment:
    * Estimate a, b with Kijko–Smit (unequal completeness periods)
    * Derive hazard parameters for Mmin_hazard = max(5.5, mc0)
    * Save:
        - magnitude–time plot (segment 0 only)
        - cumulative MFD plot anchored at Mmin_hazard (segment 0 only)
- Serialize results to JSON for later use in the subduction source model.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from cat_no_mech_handler import paths as cat_paths

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

# Hazard minimum magnitude (for modeling, MFDs, etc.)
MREF_HAZARD = 5.5

# Output directory for plots + JSON
OUTPUT_DIR = Path("subduction_ab_results")

# Latitude-based segments (placeholders for future).
# For now we just use a full patch as seg0.
# Later you can add more segments like:
# {"name": "seg1_north", "lat_min": -20.0, "lat_max": -15.0}
SEGMENTS = [
    # For now: one full-patch segment matching geometry segment_01
    {"name": "segment_01", "lat_min": None, "lat_max": None},
]



# ---------------------------------------------------------------------------
# 1. Catalog loading (years only)
# ---------------------------------------------------------------------------

def load_interface_catalog(
    cat_path: str | Path,
    only_mainshocks: bool = True,
) -> pd.DataFrame:
    """
    Load declustered slab-interface catalog.

    Expects at least:
        - time_iso (str, ISO like "1513-01-01T00:00:00")
        - mag (float)
        - latitude (float)
        - is_mainshock (bool, optional)

    Returns DataFrame with:
        - mag (float)
        - year (int)
        - latitude (float)
        - time_iso (for reference)
    """
    df = pd.read_csv(cat_path)

    if only_mainshocks and "is_mainshock" in df.columns:
        df = df[df["is_mainshock"] == True].copy()

    df["time_iso"] = df["time_iso"].astype(str)
    df["year"] = df["time_iso"].str.slice(0, 4).astype(int)

    df["mag"] = df["mag"].astype(float)

    if "latitude" not in df.columns:
        raise ValueError("Catalog must contain a 'latitude' column for segmentation")

    return df


def subset_catalog_by_segment(df: pd.DataFrame, seg: dict) -> pd.DataFrame:
    """
    Filter catalog by latitude segment.
    seg must contain 'lat_min' and 'lat_max' (or None).
    """
    df_seg = df.copy()
    if seg["lat_min"] is not None:
        df_seg = df_seg[df_seg["latitude"] >= seg["lat_min"]]
    if seg["lat_max"] is not None:
        df_seg = df_seg[df_seg["latitude"] <= seg["lat_max"]]
    return df_seg


# ---------------------------------------------------------------------------
# 2. Build Kijko–Smit completeness table from MC_SUMMARY
# ---------------------------------------------------------------------------

@dataclass
class KSSummary:
    completeness_table: np.ndarray  # shape (N, 2): [Mc_i, year_i]
    mc0: float                      # lowest completeness magnitude
    year0: int                      # completeness year for mc0
    last_year: int                  # last year in the catalog


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

    Returns:
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


# ---------------------------------------------------------------------------
# 5. Main: iterate segments, save plots for seg0, serialize JSON
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Load full catalog
    CATALOG_PATH = cat_paths.cat_slab_interface_dc
    df_cat_full = load_interface_catalog(CATALOG_PATH, only_mainshocks=True)

    # 2) Load MC summary and build completeness table
    mc_df = pd.read_csv(cat_paths.MC_SUMMARY, sep="\t")
    mc_df = mc_df.sort_values("start_iso")
    completeness_table = build_completeness_table_from_mc_summary(mc_df)

    print("Kijko–Smit completeness table (Mc, year):")
    print(completeness_table)

    results_all = {"segments": []}

    for idx_seg, seg in enumerate(SEGMENTS):
        seg_name = seg["name"]
        print(f"\n=== Segment {idx_seg} / {seg_name} ===")

        df_seg = subset_catalog_by_segment(df_cat_full, seg)
        if df_seg.empty:
            print("  Segment has no events, skipping.")
            continue

        # 3) KS a–b for this segment
        delta_m = 0.1
        ks_res = estimate_ab_kijko_smit_from_catalog(
            df_seg,
            completeness_table=completeness_table,
            delta_m=delta_m,
            b_parameter="b_value",
        )

        print("  KS results:")
        for k, v in ks_res.items():
            print(f"    {k}: {v}")

        # 4) Hazard Mmin: use earthquakes above 5.5 (or mc0 if higher)
        mc0 = ks_res["mc0"]
        Mmin_hazard = max(MREF_HAZARD, mc0)

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
            print("  No events above Mmin_hazard in completeness period, skipping MFD plot.")
            T_anchor = None
        else:
            # counts at M >= Mmin_hazard
            # We'll compute cumulative MFD and anchor to λ(Mmin_hazard)
            mmax_obs = mags_haz.max()
            mag_edges_haz = np.arange(Mmin_hazard, mmax_obs + delta_m * 1.0001, delta_m)
            counts_haz, _ = np.histogram(mags_haz, bins=mag_edges_haz)
            cum_counts_haz = np.cumsum(counts_haz[::-1])[::-1]

            N_Mmin = cum_counts_haz[0]
            T_anchor = N_Mmin / lambda_Mmin  # years, for plotting only

        # 5) Store results for this segment (for later subduction model)
        seg_results = {
            "segment_id": seg_name,   # <--- NEW, matches geometry segment_id
            "name": seg_name,         # keep name for readability
            "lat_min": seg["lat_min"],
            "lat_max": seg["lat_max"],
            "ks_results": ks_res,
            "hazard_params": {
                "Mmin_hazard": float(Mmin_hazard),
                "lambda_Mmin": float(lambda_Mmin),
                "T_anchor_Mmin": float(T_anchor) if T_anchor is not None else None,
                "N_events_Mmin": int(N_Mmin) if T_anchor is not None else 0,
            },
        }
        results_all["segments"].append(seg_results)

        # 6) Plots ONLY for segment 0 (m0)
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
            fig1.savefig(OUTPUT_DIR / f"{seg_name}_magtime.png", dpi=200)
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
                fig2.savefig(OUTPUT_DIR / f"{seg_name}_mfd_Mmin{Mmin_hazard:.1f}.png", dpi=200)
                plt.close(fig2)

    # 7) Serialize all segments to JSON
    json_path = OUTPUT_DIR / "subduction_ab_results.json"
    with json_path.open("w") as f:
        json.dump(results_all, f, indent=2)

    print(f"\nSerialized a–b results to {json_path}")
    print(f"Plots saved in {OUTPUT_DIR}")
