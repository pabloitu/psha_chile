from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from cat_no_mech_handler import paths as cat_paths
from seismostats.analysis.bvalue.utsu import UtsuBValueEstimator
from seismostats.utils.binning import bin_to_precision

# ---------- Mc windows ----------


@dataclass
class McSelection:
    """
    Combined Mc information for a set of windows.

    Attributes
    ----------
    indices : list[int]
        Row indices of MC_SUMMARY used in this selection.
    start_iso, end_iso : str
        Combined time span: [start_iso, end_iso).
    mc : float
        Single completeness threshold (max Mc across selected windows).
    years : float
        Total duration in years (sum of Years for the selected rows).
    """
    indices: list[int]
    start_iso: str
    end_iso: str
    mc: float
    years: float

    @property
    def start(self) -> pd.Timestamp:
        return pd.to_datetime(self.start_iso, utc=True)

    @property
    def end(self) -> pd.Timestamp:
        return pd.to_datetime(self.end_iso, utc=True)


def read_mc(path: Path) -> pd.DataFrame:
    """
    Read MC_SUMMARY into a DataFrame.

    Expected columns:
        start_iso  end_iso  N  Mc  b  Years
    """
    path = Path(path)
    df = pd.read_csv(
        path,
        sep=r"\s+",
        engine="python",
        comment="#",
    )
    df.columns = [c.strip() for c in df.columns]

    expected = ["start_iso", "end_iso", "N", "Mc", "b", "Years"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(
            f"[read_mc] Missing columns {missing} in {path}. "
            f"Got columns: {list(df.columns)}"
        )

    print(f"[read_mc] Read {len(df)} Mc windows from {path}")
    print(df)
    return df


def pick_windows(mc_df: pd.DataFrame, start_index: int = -7) -> McSelection:
    """
    Combine all Mc windows from start_index to the last row.

    Example with start_index=-7:
      uses rows -7, -6, -5, -4, -3, -2, -1 (last 7 windows).

    The combined completeness is:
      mc = max(Mc of selected rows)
    The combined time span is:
      [start_iso of first, end_iso of last)
    The total duration is:
      years = sum(Years of selected rows)
    """
    n = len(mc_df)
    if n == 0:
        raise ValueError("[pick_windows] Empty Mc table.")

    # Convert negative index to positive
    if start_index < 0:
        start_idx = n + start_index
    else:
        start_idx = start_index

    if start_idx < 0 or start_idx >= n:
        raise IndexError(
            f"[pick_windows] start_index {start_index} out of range for {n} rows."
        )

    rows = mc_df.iloc[start_idx:]
    indices = list(range(start_idx, n))

    start_iso = str(rows.iloc[0]["start_iso"])
    end_iso = str(rows.iloc[-1]["end_iso"])
    mc = float(rows["Mc"].max())
    years = float(rows["Years"].sum())

    print("[pick_windows] Using Mc windows:")
    print(rows[["start_iso", "end_iso", "Mc", "Years"]])

    sel = McSelection(
        indices=indices,
        start_iso=start_iso,
        end_iso=end_iso,
        mc=mc,
        years=years,
    )

    print(
        f"[pick_windows] Combined: {sel.start_iso}–{sel.end_iso}, "
        f"mc={sel.mc:.2f}, years={sel.years:.2f}, indices={sel.indices}"
    )
    return sel


# ---------- Catalog loading and merging ----------


def _load_one_catalog_for_mfd(
    path: Path,
    mc_sel: McSelection,
    *,
    mmin: float,
    only_mainshocks: bool = True,
    label: str,
) -> pd.DataFrame:
    """
    Load one declustered catalog and filter it for MFD estimation.

    Filters:
      - time in [mc_sel.start, mc_sel.end)
      - if only_mainshocks: is_mainshock == True (if column exists)
      - mag >= mmin
    """
    path = Path(path)
    df = pd.read_csv(path)
    before = len(df)

    if "time_iso" not in df.columns:
        raise ValueError(
            f"[_load_one_catalog_for_mfd] 'time_iso' missing in {path}"
        )
    if "mag" not in df.columns:
        raise ValueError(
            f"[_load_one_catalog_for_mfd] 'mag' missing in {path}"
        )

    # Robust datetime parsing: very old dates become NaT and then get dropped
    df["time_iso"] = pd.to_datetime(
        df["time_iso"], utc=True, errors="coerce"
    )

    n_nat = df["time_iso"].isna().sum()
    if n_nat > 0:
        print(
            f"[_load_one_catalog_for_mfd] {path.name}: "
            f"{n_nat} rows have NaT time (likely very old dates); "
            "they will be excluded by the time filter."
        )

    mask_time = (df["time_iso"] >= mc_sel.start) & (df["time_iso"] < mc_sel.end)
    df = df[mask_time]

    if only_mainshocks and "is_mainshock" in df.columns:
        df = df[df["is_mainshock"] == True]

    df = df[df["mag"] >= mmin]

    after = len(df)
    print(
        f"[_load_one_catalog_for_mfd] {path.name} ({label}): "
        f"{before} rows -> {after} after time [{mc_sel.start_iso}–{mc_sel.end_iso}), "
        f"mainshocks={only_mainshocks}, mag>= {mmin:.2f}"
    )

    df = df.copy()
    df["class"] = label
    return df.reset_index(drop=True)


def load_mfd_catalog(
    mc_sel: McSelection,
    *,
    mmin: float | None = None,
    only_mainshocks: bool = True,
    catalogs: Sequence[Path] | None = None,
    labels: Sequence[str] | None = None,
    outdir: Path = Path("mfd_outputs"),
) -> pd.DataFrame:
    """
    Load and merge declustered catalogs for MFD estimation.

    Default catalogs (if not given):
      - cat_paths.cat_intra_slab_dc  -> 'intra_slab'
      - cat_paths.cat_slab_deep_dc   -> 'slab_deep'

    Filters:
      - time in [mc_sel.start, mc_sel.end)
      - if only_mainshocks: is_mainshock == True
      - mag >= mmin (defaults to mc_sel.mc)
    """
    if mmin is None:
        mmin = mc_sel.mc

    # Defaults: intra_slab + slab_deep
    if catalogs is None or labels is None:
        catalogs = [cat_paths.cat_intraarc_dc, cat_paths.cat_forearc_dc, cat_paths.cat_unclassified_dc]
        labels = ["intraarc", "forearc", "unclassified"]

    if len(catalogs) != len(labels):
        raise ValueError("[load_mfd_catalog] catalogs and labels must have same length.")

    dfs = []
    for path, label in zip(catalogs, labels):
        df_one = _load_one_catalog_for_mfd(
            path=path,
            mc_sel=mc_sel,
            mmin=mmin,
            only_mainshocks=only_mainshocks,
            label=label,
        )
        dfs.append(df_one)

    df_all = pd.concat(dfs, ignore_index=True)
    df_all = df_all.sort_values("time_iso").reset_index(drop=True)

    print(
        f"[load_mfd_catalog] Merged MFD catalog: {len(df_all)} events "
        f"in combined window {mc_sel.start_iso}–{mc_sel.end_iso}, "
        f"mmin={mmin:.2f}, classes={set(df_all['class'])}"
    )

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_csv = outdir / f"mfd_catalog_merged_mcidx{mc_sel.indices[0]}.csv"
    cols = ["time_iso", "mag", "class"]
    extra = [c for c in ["id", "longitude", "latitude"] if c in df_all.columns]
    df_all[cols + extra].to_csv(out_csv, index=False)
    print(f"[load_mfd_catalog] Wrote merged MFD catalog to {out_csv}")

    return df_all


# ---------- a, b estimation ----------


def estimate_ab(
    df: pd.DataFrame,
    mc_sel: McSelection,
    *,
    mmin_forecast: float = 4.9,
    delta_m: float = 0.1,
) -> dict:
    """
    Estimate b and a for a combined Mc window selection.

    Steps:
      - estimate b using UtsuBValueEstimator on magnitudes >= mc_sel.mc
      - compute lambda(M >= mc_sel.mc) = N / mc_sel.years
      - extrapolate to mmin_forecast using GR with that b
      - compute a for that rate and b:

            log10 λ(M>=M) = a - b M
            => a = log10 λ(M>=Mmin) + b * Mmin
    """
    mags = df["mag"].to_numpy(dtype=float)
    mags = bin_to_precision(mags, delta_m)
    if mags.size == 0:
        raise ValueError("[estimate_ab] No events in catalog for this selection.")

    mc_used = mc_sel.mc

    # 1) b-value (single completeness level) using Utsu method
    est = UtsuBValueEstimator()

    est.calculate(magnitudes=mags, mc=mc_used, delta_m=delta_m)
    b = est.b_value

    # 2) rate above Mc: N / T
    N = len(mags)
    T = mc_sel.years
    lambda_mc = N / T

    # 3) extrapolate rate to forecast Mmin = 4.9 (may be < Mc)
    mmin = mmin_forecast
    lambda_mmin = lambda_mc * 10.0 ** (b * (mc_used - mmin))

    # 4) a-value (this "a" is the GR a such that log10 λ(M>=M) = a - b M)
    a = np.log10(lambda_mmin) + b * mmin

    print("[estimate_ab] Results:")
    print(f"  mc_used         = {mc_used:.2f}")
    print(f"  b               = {b:.3f}")
    print(f"  N (M>=mc_used)  = {N}")
    print(f"  T (years)       = {T:.2f}")
    print(f"  lambda(M>=Mc)   = {lambda_mc:.4f} /yr")
    print(f"  Mmin_forecast   = {mmin:.2f}")
    print(f"  lambda(M>=Mmin) = {lambda_mmin:.4f} /yr")
    print(f"  a               = {a:.3f}")

    return {
        "a": a,
        "b": b,
        "lambda_mc": lambda_mc,
        "lambda_mmin": lambda_mmin,
        "mc_used": mc_used,
        "mmin_forecast": mmin,
        "N": N,
        "T_years": T,
    }


# ---------- Cumulative MFD (for goodness-of-fit) ----------


def build_mfd_curve(
    df: pd.DataFrame,
    ab: dict,
    *,
    mc_sel: McSelection,
    delta_m: float = 0.1,
) -> pd.DataFrame:
    """
    Build observed and GR model cumulative MFD for plotting / QA.

    - Observed: N_obs(M >= m) from the catalog (df["mag"])
    - Model:   N_gr(M >= m) = λ(M>=m) * T, where
               λ(M>=m) = 10^(a - b m) with (a,b) from `ab`

    Returns a DataFrame with columns:
      - m          : magnitude values
      - N_obs      : observed cumulative counts
      - N_gr       : model cumulative counts
      - log10_Nobs : log10 N_obs (NaN where N_obs == 0)
      - log10_Ngr  : log10 N_gr
    """
    mags = df["mag"].to_numpy(dtype=float)
    if mags.size == 0:
        raise ValueError("[build_mfd_curve] Empty catalog.")

    mc_used = ab.get("mc_used", mc_sel.mc)
    a = ab["a"]
    b = ab["b"]
    T = ab.get("T_years", mc_sel.years)

    mmax = mags.max()
    mmin = mc_used
    m_vals = np.arange(mmin, mmax + 1e-6, delta_m)

    N_obs = np.array([(mags >= m).sum() for m in m_vals])
    lambda_gr = 10.0 ** (a - b * m_vals)
    N_gr = lambda_gr * T

    with np.errstate(divide="ignore"):
        log10_Nobs = np.where(N_obs > 0, np.log10(N_obs), np.nan)
        log10_Ngr = np.where(N_gr > 0, np.log10(N_gr), np.nan)

    mfd_df = pd.DataFrame(
        {
            "m": m_vals,
            "N_obs": N_obs,
            "N_gr": N_gr,
            "log10_Nobs": log10_Nobs,
            "log10_Ngr": log10_Ngr,
        }
    )

    return mfd_df


def plot_mfd(
    mfd_df: pd.DataFrame,
    *,
    outdir: Path = Path("mfd_outputs"),
    filename: str = "mfd_cumulative.png",
) -> None:
    """
    Quick cumulative MFD plot: log10 N(M>=m) vs m, data vs GR.

    Writes a PNG; you can also inspect the CSV from build_mfd_curve in QGIS
    or elsewhere if you prefer.
    """
    import matplotlib.pyplot as plt  # local import

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_png = outdir / filename

    m = mfd_df["m"].to_numpy()
    logN_obs = mfd_df["log10_Nobs"].to_numpy()
    logN_gr = mfd_df["log10_Ngr"].to_numpy()

    plt.figure()
    plt.step(m, logN_obs, where="post", label="Observed", linewidth=1.5)
    plt.plot(m, logN_gr, label="GR fit", linewidth=1.5)

    plt.xlabel("Magnitude M")
    plt.ylabel("log10 N(M ≥ M)")
    plt.title("Cumulative MFD (Observed vs GR)")
    plt.grid(True, which="both", linestyle=":")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()

    print(f"[plot_mfd] Wrote {out_png}")


# ---------- Quick test / example ----------


if __name__ == "__main__":
    # 1) Read Mc summary and build combined window (-7..-1)
    mc_df = read_mc(cat_paths.MC_SUMMARY)
    mc_sel = pick_windows(mc_df, start_index=-5)

    # 2) Load merged MFD catalog (intra_slab + slab_deep),
    #    using mmin = mc_sel.mc for completeness
    df_mfd = load_mfd_catalog(
        mc_sel,
        mmin=mc_sel.mc,
        only_mainshocks=True,
    )

    # 3) Estimate a, b and rates, with forecast Mmin = 4.9
    ab = estimate_ab(df_mfd, mc_sel, mmin_forecast=4.9, delta_m=0.1)

    # 4) Build and plot cumulative MFD for goodness-of-fit
    Path("mfd_crustal_outputs").mkdir(exist_ok=True)
    mfd_df = build_mfd_curve(df_mfd, ab, mc_sel=mc_sel, delta_m=0.1)
    mfd_df.to_csv("mfd_crustal_outputs/mfd_curve.csv", index=False)
    print("[__main__] Wrote mfd_crustal_outputs/mfd_curve.csv")

    plot_mfd(mfd_df, outdir=Path("mfd_crustal_outputs"), filename="mfd_cumulative.png")
