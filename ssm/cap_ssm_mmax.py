# cap_ssm_mmax.py
# Post-process the smoothed-seismicity MFD grid: inside the fault-buffer union,
# zero all bins with lower edge >= cap_mag (default 6.0). Outside, untouched.
# The capped CSV feeds create_crustal_point_source_model.py unchanged (bin
# columns are preserved; trailing zero bins are trimmed at source-build time).

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fault_buffers import load_union, cell_mask


def bin_cols(df: pd.DataFrame) -> list[tuple[str, float, float]]:
    out = []
    for c in df.columns:
        if c.startswith("rate_M"):
            lo, hi = c[6:].split("_")
            out.append((c, float(lo), float(hi)))
    out.sort(key=lambda x: x[1])
    if not out:
        raise ValueError("[cap_ssm_mmax] no rate_M columns found")
    return out


def cap_grid(ssm_csv: Path, union_geojson: Path, out_csv: Path,
             cap_mag: float = 6.0) -> pd.DataFrame:
    """
    Cap smoothed-cell Mmax at cap_mag inside the fault-buffer union.

    Parameters
    ----------
    ssm_csv : Path
        Grid written by ssm_crustal.write_ssm_mfd_csv (lon, lat, rate_M*).
    union_geojson : Path
        Dissolved buffer union from fault_buffers.write_buffers.
    out_csv : Path
        Capped grid; same columns plus 'in_fault_buffer'.
    cap_mag : float
        Bins with lower edge >= cap_mag are zeroed inside buffers. With
        cap_mag=6.0 the background keeps its last bin at 5.9-6.0 and the
        fault models (Mmin bin center 6.05) take over from 6.0 up.

    Returns
    -------
    DataFrame
        The capped grid.
    """
    df = pd.read_csv(ssm_csv)
    cols = bin_cols(df)
    capped_cols = [c for c, lo, _ in cols if lo >= cap_mag - 1e-6]
    if not capped_cols:
        raise ValueError(f"[cap_grid] no bins with lower edge >= {cap_mag}")

    union = load_union(union_geojson)
    inside = cell_mask(df["lon"].to_numpy(), df["lat"].to_numpy(), union)

    removed = df.loc[inside, capped_cols].to_numpy().sum()
    total = df[capped_cols].to_numpy().sum()

    df["in_fault_buffer"] = inside
    df.loc[inside, capped_cols] = 0.0

    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    print(f"[cap_grid] cells inside buffers: {inside.sum()} / {len(df)}")
    print(f"[cap_grid] capped bins (lower edge >= {cap_mag}): {len(capped_cols)}")
    print(f"[cap_grid] N(M>={cap_mag}) removed: {removed:.5f} /yr "
          f"({100 * removed / total:.1f}% of national background M>={cap_mag})")
    print(f"[cap_grid] wrote {out_csv.resolve()}")
    return df


def main():
    cap_grid(
        ssm_csv=Path("ssm_crustal_outputs/ssm_mfd_grid.csv"),
        union_geojson=Path("fault_buffers_union.geojson"),
        out_csv=Path("ssm_crustal_outputs/ssm_mfd_grid_capped.csv"),
        cap_mag=6.0,
    )


if __name__ == "__main__":
    main()