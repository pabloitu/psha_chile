from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from seismostats.utils.binning import bin_to_precision, binning_test
from seismostats.analysis.estimate_mc import estimate_mc_ks, estimate_mc_maxc
from seismostats.analysis.bvalue.positive import BPositiveBValueEstimator
from seismostats.analysis.bvalue.more_positive import BMorePositiveBValueEstimator

from cat_no_mech_handler_backarc import paths

# --------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------
DELTA_M = 0.1            # magnitude binning for KS method
P_VALUE_PASS = 0.1        # KS p-value threshold
MIN_EVENTS_PER_WIN = 50   # skip windows with too few events

CAT_IN_MC = Path(paths.cat_classified)
# CAT_IN_MC = Path(paths.cat_classified).with_name("cat_classified_mainshocks.csv")

CAT_OUT = Path(paths.cat_full_mc)
MC_SUMMARY_TXT = paths.MC_SUMMARY
MC_FILTER_SUMMARY_TXT = paths.MC_FILTER_SUMMARY
MC_PLOT_DIR = CAT_OUT.parent / "mc_plots_ks"
# NEW: summary of original vs filtered counts
# Fixed time windows (ISO strings). Last end will be replaced by catalog max.
FIXED_WINDOWS = [
    ("1513-01-01T00:00:00", "1900-01-01T00:00:00"),
    ("1900-01-01T00:00:00", "1950-01-01T00:00:00"),
    ("1950-01-01T00:00:00", "1976-01-01T00:00:00"),
    ("1976-01-01T00:00:00", "1986-01-01T00:00:00"),
    ("1986-01-01T00:00:00", "1997-01-01T00:00:00"),

    ("1997-01-01T00:00:00", "2002-01-01T00:00:00"),
    ("2001-01-01T00:00:00", "2007-01-01T00:00:00"),
    ("2007-01-01T00:00:00", "2010-01-01T00:00:00"),
    ("2010-01-01T00:00:00", "2013-01-01T00:00:00"),
    ("2014-01-01T00:00:00", "2016-01-01T00:00:00"),  # end = max time in catalog (allowed classes)
    ("2016-01-01T00:00:00", None),
    # end = max time in catalog (allowed classes)

    # ("2018-01-01T00:00:00", None),  # end = max time in catalog (allowed classes)
]

# Classes to use for Mc estimation
ALLOWED_CLASSES = {
    # "intraarc",
    "slab_interface",
    # "intra_slab",
    # "slab_deep",
    # "forearc",
}
# Ignore completely: outer_rise, unclassified, and anything else
MC_CLASSES = {
"full": paths.cat_full_mc,
"backarc": paths.cat_backarc_mc,
"intraarc": paths.cat_intraarc_mc,
"slab_interface": paths.cat_slab_interface_mc,
"intra_slab": paths.cat_intra_slab_mc,
"slab_deep": paths.cat_slab_deep_mc,
"outer_rise": paths.cat_outer_rise_mc,
"forearc": paths.cat_forecarc_mc,
"unclassified": paths.cat_unclassified_mc
}

def _iso_to_datetime(s: str) -> datetime:
    """Parse ISO date string (without timezone) into a Python datetime."""
    s = str(s)
    if s.endswith("Z"):
        s = s[:-1]
    # works for 'YYYY-MM-DD' and 'YYYY-MM-DDTHH:MM:SS'
    return datetime.fromisoformat(s)


@dataclass
class IntervalResult:
    label: str
    start_iso: str
    end_iso: str
    n_events: int
    mc: float | None
    best_b: float | None
    years: float
    mcs_tested: List[float]
    p_values: List[float]


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def _build_intervals(df: pd.DataFrame) -> List[Tuple[str, str, str]]:
    """Return list of (label, start_iso, end_iso) using FIXED_WINDOWS.

    The last end_iso is replaced by the max time_iso in the FILTERED catalog.
    """
    tmax_iso = str(df["time_iso"].max())  # lexicographic OK for ISO strings
    intervals: List[Tuple[str, str, str]] = []
    for i, (start_iso, end_iso) in enumerate(FIXED_WINDOWS, start=1):
        if end_iso is None:
            end_iso = tmax_iso
        label = f"win{i}"
        intervals.append((label, start_iso, end_iso))
    return intervals


def _gr_a_value(mags: np.ndarray, mc: float, b: float) -> float:
    """
    Estimate a-value from events above Mc:

      log10 N(M>=m) = a - b m
      => a ≈ log10 N(M>=Mc) + b * Mc
    """
    sel = mags[~np.isnan(mags)]
    sel = sel[sel >= mc - DELTA_M / 2]
    if sel.size == 0:
        return float("nan")
    n = sel.size
    return math.log10(n) + b * mc


# --------------------------------------------------------------------
# Main computation
# --------------------------------------------------------------------
def compute_mc_over_time(
    delta_m: float = DELTA_M,
    p_value_pass: float = P_VALUE_PASS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estimate Mc per fixed time window using KS method.

    - Uses only ALLOWED_CLASSES for the Mc estimation.
    - Ignores outer_rise and unclassified completely for estimation.
    - Assigns Mc and Tc to *all* events in the catalog based on time windows.
    - Enforces that Mc cannot increase with time: Mc_i >= Mc_{i+1}.

    Returns
    -------
    df_all : DataFrame
        Full catalog with added columns:
        - mc_window
        - tc_years
        - mc_window_index
    mc_df : DataFrame
        Per-window summary with:
        - window_index, label, start_iso, end_iso, n_events,
          mc, b_value, duration_years, mcs_tested, p_values
    """
    # --- load full catalog ---
    df_all = pd.read_csv(CAT_IN_MC)
    # Keep times as strings but add a convenience column
    df_all["time"] = df_all["time_iso"].astype(str)

    # --- filter to allowed classes for Mc estimation ---
    mask_allowed = df_all["class"].isin(ALLOWED_CLASSES)
    df_est = df_all[mask_allowed].copy()

    # Drop NaN magnitudes for Mc estimation
    df_est = df_est[pd.notna(df_est["mag"])].copy()

    # Build intervals from the filtered catalog
    intervals = _build_intervals(df_est)

    results: list[dict[str, Any]] = []

    # We no longer assign mc_per_event inside the loop; we'll do it
    # AFTER making Mc monotonic in time.
    for iw, (label, start_iso, end_iso) in enumerate(intervals):
        mask_win = (df_est["time"] >= start_iso) & (df_est["time"] < end_iso)
        mags = df_est.loc[mask_win, "mag"].to_numpy(float)

        n_events = mags.size
        if n_events < MIN_EVENTS_PER_WIN:
            best_mc = np.nan
            best_b = np.nan
            p_vals: list[float] = []
            mcs_tested: list[float] = []
        else:
            # Round magnitudes to delta_m grid for KS method
            mags_binned = np.round(mags / delta_m) * delta_m
            mags_binned = bin_to_precision(mags_binned, delta_m)

            # Optional sanity check on binning
            if not binning_test(mags_binned, delta_m, check_larger_binning=False):
                print(f"[{label}] WARN: magnitudes not perfectly binned; KS result may be off.")

            # KS-based Mc, with fixed b = 1 (more stable)
            best_mc, mc_info = estimate_mc_ks(
                magnitudes=mags_binned,
                delta_m=delta_m,
                p_value_pass=p_value_pass,
                stop_when_passed=True,
                n=5000,
                verbose=False,
                b_value=1.0,                    # <--- fixed b for KS
                b_method=BPositiveBValueEstimator,  # not used when b_value is given
            )

            if best_mc is None:
                best_mc = np.nan
                best_b = np.nan
            else:
                best_b = mc_info.get("best_b_value", np.nan)

            p_vals = mc_info.get("p_values", [])
            mcs_tested = mc_info.get("mcs_tested", [])

        # Duration in years using Python datetime (handles 1500+)
        t_start = _iso_to_datetime(start_iso)
        t_end = _iso_to_datetime(end_iso)
        delta = t_end - t_start
        dt_years = delta.days / 365.25 + delta.seconds / (365.25 * 86400.0)

        results.append(
            dict(
                window_index=iw,
                label=label,
                start_iso=start_iso,
                end_iso=end_iso,
                n_events=n_events,
                mc=best_mc,
                b_value=best_b,
                duration_years=dt_years,
                mcs_tested=mcs_tested,
                p_values=p_vals,
            )
        )

    # ------------------------------------------------------------------
    # Build window summary table
    # ------------------------------------------------------------------
    mc_df = pd.DataFrame(results)

    # ------------------------------------------------------------------
    # Enforce: Mc cannot increase with time
    # Mc(t_{i+1}) <= Mc(t_i). If it increases, clamp to previous.
    # ------------------------------------------------------------------
    last_mc = np.inf
    for i in range(len(mc_df)):
        mc_val = mc_df.loc[i, "mc"]
        if pd.isna(mc_val):
            # Do not change last_mc; just leave NaN
            continue
        if last_mc is np.inf:
            # first valid Mc
            last_mc = mc_val
        else:
            if mc_val > last_mc:
                # clamp to previous (non-increasing in time)
                mc_df.loc[i, "mc"] = last_mc
            else:
                last_mc = mc_val

    # ------------------------------------------------------------------
    # Assign Mc and Tc to *all* events in the full catalog
    # ------------------------------------------------------------------
    df_all["mc_window"] = np.nan
    df_all["tc_years"] = np.nan
    df_all["mc_window_index"] = -1

    for _, row in mc_df.iterrows():
        mc_val = row["mc"]
        start_iso = row["start_iso"]
        end_iso = row["end_iso"]
        win_idx = int(row["window_index"])
        yrs = float(row["duration_years"])

        # Apply to all events in that time window
        mask_win_all = (df_all["time"] >= start_iso) & (df_all["time"] < end_iso)

        df_all.loc[mask_win_all, "mc_window"] = mc_val
        df_all.loc[mask_win_all, "tc_years"] = yrs
        df_all.loc[mask_win_all, "mc_window_index"] = win_idx

    # ------------------------------------------------------------------
    # Write out catalog with Mc information
    # ------------------------------------------------------------------
    df_all.to_csv(paths.cat_full_mc, index=False)
    print(f"[OK] wrote catalog with Mc info: {paths.cat_full_mc} ({len(df_all)} rows)")

    # ------------------------------------------------------------------
    # Print and write summary table (using monotonic Mc)
    # ------------------------------------------------------------------
    header = "start_iso\tend_iso\tN\tMc\tb\tYears"
    print(header)
    lines = [header]
    for _, row in mc_df.iterrows():
        mc_val = row["mc"]
        b_val = row["b_value"]

        if isinstance(mc_val, (float, int)) and not math.isnan(mc_val):
            mc_str = f"{mc_val:.3f}"
        else:
            mc_str = "NaN"

        if isinstance(b_val, (float, int)) and not math.isnan(b_val):
            b_str = f"{b_val:.3f}"
        else:
            b_str = "NaN"

        yrs_str = f"{row['duration_years']:.2f}"
        line = (
            f"{row['start_iso']}\t{row['end_iso']}\t"
            f"{int(row['n_events'])}\t{mc_str}\t{b_str}\t{yrs_str}"
        )
        print(line)
        lines.append(line)

    MC_SUMMARY_TXT.parent.mkdir(parents=True, exist_ok=True)
    with open(MC_SUMMARY_TXT, "w") as f:
        f.write("\n".join(lines))
    print(f"[OK] wrote Mc summary: {MC_SUMMARY_TXT}")

    return df_all, mc_df

# --------------------------------------------------------------------
# Plotting: MFD + GR and Mc vs p-value
# --------------------------------------------------------------------

def _plot_mfd_and_gr_for_interval(df: pd.DataFrame, res: IntervalResult) -> None:
    """Plot cumulative log10 MFD and GR line for a single interval,
    including magnitudes below Mc to visualize the curvature."""
    label = res.label
    start_iso = res.start_iso
    end_iso = res.end_iso
    mc = res.mc
    b = res.best_b

    if mc is None or b is None or math.isnan(mc) or math.isnan(b):
        print(f"[{label}] skip MFD plot (no Mc/b).")
        return

    # Filter events for this window *and* allowed classes (same as Mc estimation)
    mask = (
        (df["time_iso"] >= start_iso) &
        (df["time_iso"] < end_iso) &
        (df["class"].isin(ALLOWED_CLASSES))
    )

    mags = df.loc[mask, "mag"].to_numpy(float)
    mags = mags[~np.isnan(mags)]

    if mags.size == 0:
        print(f"[{label}] no magnitudes for plotting.")
        return

    # ----- DATA MFD RANGE: from min(mag) up to max(mag) -----
    m_min_data = float(np.nanmin(mags))
    m_max = float(np.nanmax(mags)) + 0.001

    # Snap min to the DELTA_M grid (downwards)
    m_min_data = math.floor(m_min_data / DELTA_M) * DELTA_M
    m_grid_data = bin_to_precision(
        np.arange(m_min_data, m_max + 3 * DELTA_M / 2, DELTA_M),
        DELTA_M,
    )

    # DATA: cumulative N(M >= m)
    Ns = []
    for m in m_grid_data:
        Ns.append((mags >= m - DELTA_M / 2).sum())
    Ns = np.array(Ns, dtype=float)

    # ----- GR MODEL RANGE: only from Mc upwards -----
    m_grid_gr = m_grid_data[m_grid_data >= mc - 1e-6]
    if m_grid_gr.size == 0:
        print(f"[{label}] no bins >= Mc for GR line, skipping GR.")
        m_grid_gr = None

    a_val = _gr_a_value(mags, mc, b)
    if m_grid_gr is not None:
        N_gr = 10.0 ** (a_val - b * m_grid_gr)

    # ----- PLOT -----
    fig, ax = plt.subplots(figsize=(6, 4))

    with np.errstate(divide="ignore", invalid="ignore"):
        # Data: log10 N(M>=m) over full range, including below Mc
        ax.plot(
            m_grid_data,
            np.log10(Ns),
            "o-",
            label="Data (log10 N≥M)",
        )

        if m_grid_gr is not None:
            ax.plot(
                m_grid_gr,
                np.log10(N_gr),
                "-",
                label=f"GR fit (b={b:.2f}, Mc={mc:.2f})",
            )

    # vertical line at Mc to visually mark the cutoff
    ax.axvline(mc, color="r", linestyle="--", alpha=0.7, label="Mc")

    ax.set_xlabel("Magnitude")
    ax.set_ylabel("log10 N(M ≥ m)")
    ax.set_title(f"{label}: {start_iso} – {end_iso}")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend()

    MC_PLOT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MC_PLOT_DIR / f"{label}_mfd.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[{label}] wrote MFD+GR plot (with M < Mc included) -> {out_path}")


def _plot_pvalues_for_interval(res: IntervalResult) -> None:
    """Plot p-value vs candidate Mc for a single interval."""
    label = res.label
    if not res.mcs_tested or not res.p_values:
        print(f"[{label}] no p-values to plot.")
        return

    mcs = np.array(res.mcs_tested, dtype=float)
    pvals = np.array(res.p_values, dtype=float)

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(mcs, pvals, "o-", label="KS p-value")
    if res.mc is not None and not math.isnan(res.mc):
        ax.axvline(res.mc, color="r", linestyle="--", label=f"Mc={res.mc:.2f}")
    ax.axhline(P_VALUE_PASS, color="k", linestyle=":", label=f"p_thr={P_VALUE_PASS}")

    ax.set_xlabel("Candidate Mc")
    ax.set_ylabel("KS p-value")
    ax.set_title(label)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend()

    MC_PLOT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MC_PLOT_DIR / f"{label}_pvals.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[{label}] wrote Mc vs p-value plot -> {out_path}")

def plot_mag_time_with_mc(mc_df: pd.DataFrame) -> None:
    """
    Make a magnitude–time plot (CSEP) and overlay Mc as horizontal segments
    for each time window, using the per-window summary DataFrame (mc_df).
    """
    from csep.plots import plot_magnitude_versus_time
    from cat_no_mech_handler.parsers import read_csep

    # 1) Load catalog and make the base magnitude–time plot
    catalog = read_csep.load_csep(paths.cat_integrated_relocated)
    ax = plot_magnitude_versus_time(catalog, show=False, figsize=(12, 6))

    # 2) Overlay Mc per window as horizontal line segments
    for _, row in mc_df.iterrows():
        mc = row["mc"]
        if pd.isna(mc):
            continue

        start_iso = row["start_iso"]
        end_iso = row["end_iso"]

        t_start = _iso_to_datetime(start_iso)
        t_end = _iso_to_datetime(end_iso)

        ax.hlines(
            y=float(mc),
            xmin=t_start,
            xmax=t_end,
            colors="red",
            linestyles="--",
            linewidth=2,
            label=None,
        )

    # Add a legend entry for Mc (only once)
    ax.plot([], [], "r--", linewidth=2, label="Mc (per window)")

    ax.set_title("Magnitude vs Time with Mc windows")
    ax.legend()

    MC_PLOT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MC_PLOT_DIR / "mag_time_with_mc.png"
    ax.figure.tight_layout()
    ax.figure.savefig(out_path, dpi=200)
    print(f"[PLOT] wrote magnitude–time + Mc plot -> {out_path}")


def make_plots(df: pd.DataFrame, mc_df: pd.DataFrame) -> None:
    """Create all MFD+GR and Mc-vs-p plots for all intervals."""
    for _, row in mc_df.iterrows():
        res = IntervalResult(
            label=row["label"],
            start_iso=row["start_iso"],
            end_iso=row["end_iso"],
            n_events=int(row["n_events"]),
            mc=float(row["mc"]) if not pd.isna(row["mc"]) else None,
            best_b=float(row["b_value"]) if not pd.isna(row["b_value"]) else None,
            years=float(row["duration_years"]),
            mcs_tested=row["mcs_tested"] if isinstance(row["mcs_tested"], list) else [],
            p_values=row["p_values"] if isinstance(row["p_values"], list) else [],
        )
        _plot_mfd_and_gr_for_interval(df, res)
        _plot_pvalues_for_interval(res)

def write_class_catalogs(df_all: pd.DataFrame) -> None:
    """
    Write one catalog per tectonic class to paths.FINAL_CATALOGS.

    - Uses df_all with columns:
        - 'class', 'mag', 'mc_window'
    - For each class, removes events with magnitude below Mc(window)
      (where Mc is known). Events in windows with unknown Mc are kept.
    """
    out_dir = Path(paths.FINAL_CATALOGS)
    out_dir.mkdir(parents=True, exist_ok=True)

    classes = df_all["class"].dropna().unique()

    for cls in classes:
        df_cls = df_all[df_all["class"] == cls].copy()

        if df_cls.empty:
            continue

        # Keep events where:
        # - mc_window is NaN (no Mc: we don't know, so keep), OR
        # - mag >= mc_window
        mc_vals = df_cls["mc_window"]
        mag_vals = df_cls["mag"]

        mask_mc_known = ~mc_vals.isna()
        mask_keep = (~mask_mc_known) | (mag_vals >= mc_vals)

        df_cls_filtered = df_cls[mask_keep].copy()

        out_path = MC_CLASSES[cls]
        df_cls_filtered.to_csv(out_path, index=False)

        print(
            f"[OK] wrote class catalog {cls!r}: "
            f"{len(df_cls_filtered)} events (from {len(df_cls)}) -> {out_path}"
        )
def summarize_filtered_catalog() -> None:
    """
    Re-read original and Mc-processed catalogs and write a summary:

    - Original number of events in the catalog vs filtered number.
    - Same per time window (all classes).
    - Same per class (overall).
    - Same per class and time window.

    Uses:
        - CAT_IN_MC           (original classified catalog)
        - paths.cat_full_mc  (catalog with mc_window, mc_window_index)
        - MC_SUMMARY_TXT      (time-window definitions)
    """
    # --- read catalogs ---
    df_orig = pd.read_csv(CAT_IN_MC)
    df_proc = pd.read_csv(paths.cat_full_mc)

    # --- read window summary (start/end per window) ---
    win_df = pd.read_csv(MC_SUMMARY_TXT, sep="\t")

    # ensure we have mc_window_index as integer
    win_idx = df_proc["mc_window_index"].fillna(-1).astype(int).to_numpy()

    # define "kept" events: like write_class_catalogs
    mag_vals = pd.to_numeric(df_proc["mag"], errors="coerce")
    mc_vals = pd.to_numeric(df_proc["mc_window"], errors="coerce")

    mask_mc_known = mc_vals.notna()
    keep_mask = (~mask_mc_known) | (mag_vals >= mc_vals)

    # --- TOTAL CATALOG ---
    n_orig_total = len(df_orig)
    n_filt_total = int(keep_mask.sum())

    lines: list[str] = []
    lines.append("=== TOTAL CATALOG ===")
    lines.append(f"original_events\t{n_orig_total}")
    lines.append(f"filtered_events\t{n_filt_total}")
    lines.append("")

    # --- PER TIME WINDOW (all classes) ---
    lines.append("=== PER TIME WINDOW (all classes) ===")
    lines.append("window_index\tstart_iso\tend_iso\tN_orig\tN_filtered")

    for i in range(len(win_df)):
        start_iso = str(win_df.loc[i, "start_iso"])
        end_iso = str(win_df.loc[i, "end_iso"])

        mask_win = (win_idx == i)
        n_orig = int(mask_win.sum())
        n_filt = int((mask_win & keep_mask.to_numpy()).sum())

        lines.append(f"{i}\t{start_iso}\t{end_iso}\t{n_orig}\t{n_filt}")
    lines.append("")

    # --- PER CLASS (overall) ---
    lines.append("=== PER CLASS (overall) ===")
    lines.append("class\tN_orig\tN_filtered")

    classes = sorted(df_proc["class"].dropna().unique())
    for cls in classes:
        mask_cls = (df_proc["class"] == cls)
        n_orig_cls = int(mask_cls.sum())
        n_filt_cls = int((mask_cls & keep_mask).sum())
        lines.append(f"{cls}\t{n_orig_cls}\t{n_filt_cls}")
    lines.append("")

    # --- PER CLASS AND TIME WINDOW ---
    lines.append("=== PER CLASS AND TIME WINDOW ===")
    lines.append("class\twindow_index\tstart_iso\tend_iso\tN_orig\tN_filtered")

    for cls in classes:
        mask_cls = (df_proc["class"] == cls)
        for i in range(len(win_df)):
            start_iso = str(win_df.loc[i, "start_iso"])
            end_iso = str(win_df.loc[i, "end_iso"])

            mask_win = (win_idx == i)
            sel = mask_cls & mask_win
            n_orig = int(sel.sum())
            if n_orig == 0:
                continue  # skip empty combos to keep file compact
            n_filt = int((sel & keep_mask).sum())
            lines.append(f"{cls}\t{i}\t{start_iso}\t{end_iso}\t{n_orig}\t{n_filt}")

    text = "\n".join(lines)

    # print to stdout
    print("\n[MC FILTER SUMMARY]")
    print(text)

    # write to file
    MC_FILTER_SUMMARY_TXT.parent.mkdir(parents=True, exist_ok=True)
    with open(MC_FILTER_SUMMARY_TXT, "w") as f:
        f.write(text + "\n")

    print(f"[OK] wrote Mc filtering summary: {MC_FILTER_SUMMARY_TXT}")

# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main() -> None:
    df_all, mc_df = compute_mc_over_time()
    make_plots(df_all, mc_df)
    plot_mag_time_with_mc(mc_df)
    write_class_catalogs(df_all)
    summarize_filtered_catalog()   # <- NEW
if __name__ == "__main__":
    main()
