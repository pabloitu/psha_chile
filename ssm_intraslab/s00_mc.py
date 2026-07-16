# s00_mc.py
# Per-class magnitude of completeness, cumulative-from-present.
#
# For each candidate start year t, Mc is estimated on the class catalog over
# [t, present]. Reading the resulting curve gives directly the pairs Weichert
# needs: for each Mc, the earliest year from which it holds -> T = present - t.
# A rolling Mc per time bin is plotted alongside as a diagnostic of when the
# network improved (it is not used to build the table).
#
# The mc_window / tc_years columns stamped on the catalog are NOT used here or
# anywhere downstream: this script replaces them.
#
# Output: figures/mc_<class>.png and mc_candidates_<class>.csv per class.
# Read the steps off the cumulative curve and write them into
# ssm_config.COMPLETENESS.

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import ssm_config as C
from ssm_lib import load_catalog

MC_METHOD = "ks"            # "ks" (SeismoStats, robust) or "maxc" (fast, biased
                            # low on mixed-completeness catalogs: see s00 docstring)
MAXC_CORR = 0.2
DM = 0.1
MIN_EVENTS_MC = 30          # below this a window gets no Mc
START_YEARS = list(range(1900, 2021, 5))
ROLL_BIN_YEARS = 10


def mc_maxc(mags: np.ndarray, dm: float = DM) -> float:
    """Maximum-curvature Mc + correction (Wiemer & Wyss 2000)."""
    if len(mags) < MIN_EVENTS_MC:
        return np.nan
    edges = np.arange(np.floor(mags.min() / dm) * dm,
                      mags.max() + dm, dm)
    n, _ = np.histogram(mags, bins=edges)
    if not n.any():
        return np.nan
    return float(edges[int(np.argmax(n))] + MAXC_CORR)


def mc_ks(mags: np.ndarray, dm: float = DM) -> float:
    """KS-based Mc (SeismoStats), fixed b=1; NaN if it does not converge."""
    if len(mags) < MIN_EVENTS_MC:
        return np.nan
    try:
        from seismostats.analysis import estimate_mc_ks
        from seismostats.utils import bin_to_precision
        m = bin_to_precision(np.round(mags / dm) * dm, dm)
        best, _ = estimate_mc_ks(magnitudes=m, delta_m=dm, p_value_pass=0.1,
                                 stop_when_passed=True, n=5000, verbose=False,
                                 b_value=1.0)
        return np.nan if best is None else float(best)
    except Exception as e:
        print(f"[mc_ks] failed: {e}")
        return np.nan


def mc_of(mags: np.ndarray) -> float:
    """
    Mc of one sample. KS is the default: MAXC takes the mode of the
    magnitude histogram, which on a cumulative [t, present] window is
    dominated by the recent, low-Mc part of the catalog, so it returns a
    near-constant (too low) Mc for every start year and hides the history.
    """
    return mc_maxc(mags) if MC_METHOD == "maxc" else mc_ks(mags)


def year_of(cat: pd.DataFrame) -> np.ndarray:
    return pd.to_datetime(cat["time_iso"], utc=True, errors="coerce").dt.year.to_numpy()


def cumulative_mc(cat: pd.DataFrame, years: np.ndarray) -> pd.DataFrame:
    """Mc estimated on [t, present] for each candidate start year t."""
    y = year_of(cat)
    y_max = int(np.nanmax(y))
    rows = []
    for t in START_YEARS:
        m = cat.loc[y >= t, "mag"].to_numpy(float)
        rows.append({"start_year": t, "n_events": len(m), "mc": mc_of(m),
                     "T_years": y_max - t + 1})
    return pd.DataFrame(rows)


def rolling_mc(cat: pd.DataFrame) -> pd.DataFrame:
    """Mc per fixed time bin (diagnostic only: shows when the network improved)."""
    y = year_of(cat)
    y0, y1 = int(np.nanmin(y)), int(np.nanmax(y))
    y0 = max(y0, START_YEARS[0])
    rows = []
    for t in range(y0, y1 + 1, ROLL_BIN_YEARS):
        m = cat.loc[(y >= t) & (y < t + ROLL_BIN_YEARS), "mag"].to_numpy(float)
        rows.append({"bin_start": t, "n_events": len(m), "mc": mc_of(m)})
    return pd.DataFrame(rows)


def candidate_table(cum: pd.DataFrame) -> pd.DataFrame:
    """
    For each distinct Mc on the cumulative curve, the earliest start year that
    still achieves it -> the (Mc, since_year, T) rows to put in COMPLETENESS.
    """
    ok = cum.dropna(subset=["mc"])
    rows = []
    for mc in sorted(ok["mc"].unique()):
        sub = ok[ok["mc"] <= mc + 1e-9]
        t = int(sub["start_year"].min())
        rows.append({"mc": mc, "since_year": t,
                     "T_years": int(ok.loc[ok["start_year"] == t,
                                           "T_years"].iloc[0]),
                     "n_events": int(ok.loc[ok["start_year"] == t,
                                            "n_events"].iloc[0])})
    return pd.DataFrame(rows).sort_values("mc")


def plot_class(name: str, cum: pd.DataFrame, roll: pd.DataFrame, png):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(cum["start_year"], cum["mc"], "o-", color="steelblue", lw=2,
            label="Mc over [t, present]  <- read the table off this")
    ax.plot(roll["bin_start"] + ROLL_BIN_YEARS / 2, roll["mc"], "s--",
            color=".6", ms=4, lw=1,
            label=f"rolling Mc ({ROLL_BIN_YEARS}-yr bins, diagnostic)")
    ax.set_xlabel("start year t")
    ax.set_ylabel("Mc")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax2 = ax.twinx()
    ax2.plot(cum["start_year"], cum["n_events"], ":", color="indianred", lw=1)
    ax2.set_ylabel("N events in [t, present]", color="indianred")
    ax2.set_yscale("log")
    ax.set_title(f"{name}: Mc(t), method={MC_METHOD}")
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[plot_class] wrote {png}")


def main():
    # 1) per class: Mc on [t, present] for a range of start years, plus a
    #    rolling Mc per time bin as a diagnostic
    for name, spec in C.CLASSES.items():
        print(f"\n===== {name} =====")
        cat = load_catalog(spec["catalog"], bbox=C.BBOX, region=spec.get("region"))
        cum = cumulative_mc(cat, year_of(cat))
        roll = rolling_mc(cat)
        plot_class(name, cum, roll, C.FIG / f"mc_{name}.png")

        # 2) candidate steps: earliest year achieving each Mc. These are the
        #    rows to copy into ssm_config.COMPLETENESS after eyeballing the plot
        cand = candidate_table(cum)
        cand.to_csv(C.OUT / f"mc_candidates_{name}.csv", index=False)
        print(cum.to_string(index=False))
        print("\ncandidate steps (Mc, since_year, T):")
        print(cand.to_string(index=False))
        print(f'\n  "{name}": [' + ", ".join(
            f"({r.mc:.1f}, {r.since_year})" for r in cand.itertuples()) + "],")

    print("\n[main] read the steps off figures/mc_<class>.png and write the "
          "ones you trust into ssm_config.COMPLETENESS")


if __name__ == "__main__":
    main()
