# s03_cap_ssm_mmax.py
# Fault handoff: inside the fault-buffer union, zero every smoothed bin whose
# lower edge is >= C.CAP_MAG. Outside the buffers nothing changes. With
# CAP_MAG=6.0 the background keeps its last bin at 5.9-6.0 and the fault
# model (first bin center 6.05) owns everything above -> no shared bins,
# no hole.

from __future__ import annotations

from pathlib import Path

import pandas as pd

import ssm_config as C
from s02_fault_buffers import load_union, cell_mask


def bin_cols(df: pd.DataFrame) -> list[tuple[str, float, float]]:
    out = []
    for c in df.columns:
        if c.startswith("rate_M"):
            lo, hi = c[6:].split("_")
            out.append((c, float(lo), float(hi)))
    out.sort(key=lambda x: x[1])
    if not out:
        raise ValueError("[bin_cols] no rate_M columns found")
    return out


def cap_grid(ssm_csv: Path, union_geojson: Path, out_csv: Path,
             cap_mag: float) -> pd.DataFrame:
    """
    Cap the smoothed Mmax at cap_mag inside the buffer union.

    Returns the capped grid (same columns plus 'in_fault_buffer').
    """
    df = pd.read_csv(ssm_csv)
    capped_cols = [c for c, lo, _ in bin_cols(df) if lo >= cap_mag - 1e-6]
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
          f"({100 * removed / total:.1f}% of the national background)")
    print(f"[cap_grid] wrote {out_csv.resolve()}")
    return df


def main():
    # read the total SSM grid from s01, cap it inside the s02 buffers, and
    # write the grid that s04 turns into point sources
    cap_grid(ssm_csv=C.SSM_GRID, union_geojson=C.BUFFERS_UNION,
             out_csv=C.SSM_GRID_CAPPED, cap_mag=C.CAP_MAG)


if __name__ == "__main__":
    main()
