# compare_interface_intraslab_mfd.py
# MFD comparison: subduction interface branches (per segment and full
# margin, from the sub_interface pipeline) vs the intraslab gridded model
# summed over the cells that fall INSIDE each interface segment's surface
# projection. Quantifies how much in-slab rate sits on top of each
# interface source region.
# Place at the repository top; edit the three paths below.
# Outputs: figures in OUT_DIR + a totals table printed and saved.

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
from openquake.hazardlib.gsim.abrahamson_gulerce_2020 import AbrahamsonGulerce2020SSlab
print(AbrahamsonGulerce2020SSlab.REQUIRES_DISTANCES)

# REPLACE THESE THREE PATHS
SUB_OUT = Path("sub_interface/outputs_z60_mcf56_mmin6")                      # interface pipeline
# outputs
SLAB_GRID = Path("ssm_intraslab/ssm_intraslab_outputs/ssm_mfd_grid_intra_slab.csv")
OUT_DIR = Path("mfd_comparison")

MMIN_HAZ = 6.5
BIN_W = 0.1
FULL_ID = "seg0_full"


def m0(m):
    return 10 ** (1.5 * np.asarray(m, float) + 9.05)


def cum_shape(form, b, mmin, mmax, grid):
    # copy of sub_interface/s04_rates.cum_shape (both forms truncated at mmax)
    if form == "tgr":
        n = ((10 ** (-b * grid) - 10 ** (-b * mmax))
             / (10 ** (-b * mmin) - 10 ** (-b * mmax)))
        return np.clip(n, 0, None)
    beta = 2.0 * b / 3.0

    def tap(m):
        return ((m0(mmin) / m0(m)) ** beta
                * np.exp((m0(mmin) - m0(m)) / m0(mmax)))

    n = (tap(grid) - tap(mmax)) / (1.0 - tap(mmax))
    return np.where(grid > mmax, 0.0, np.clip(n, 0, None))


def outline(edges):
    top = [(n["lon"], n["lat"]) for n in edges[0]["nodes"]]
    bot = [(n["lon"], n["lat"]) for n in edges[-1]["nodes"]]
    return Polygon(top + bot[::-1])


def load_regions():
    segs = json.loads((SUB_OUT / "geometry" / "segments.json").read_text())
    glob = json.loads((SUB_OUT / "geometry" / "global_geometry.json").read_text())
    regions = {sid: outline(s["edges"]) for sid, s in segs.items()}
    regions[FULL_ID] = outline(glob["edges"])
    return regions


def load_slab():
    df = pd.read_csv(SLAB_GRID)
    rc = [c for c in df.columns if c.startswith("rate_")]
    lo = np.array([float(c.split("_")[1].lstrip("M")) for c in rc])
    return df, rc, lo


def slab_cum(df, rc, lo, poly):
    """Cumulative intraslab MFD summed over grid cells inside poly."""
    pp = prep(poly)
    inside = np.array([pp.contains(Point(x, y))
                       for x, y in zip(df["lon"], df["lat"])])
    inc = df.loc[inside, rc].sum().to_numpy()
    cum = inc[::-1].cumsum()[::-1]
    return lo, cum, int(inside.sum())


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bp = pd.read_csv(SUB_OUT / "rates" / "branch_params.csv")
    regions = load_regions()
    slab, rc, lo = load_slab()
    slab_total = slab[rc].sum().sum()

    ids = [s for s in regions if s != FULL_ID] + [FULL_ID]
    rows = []
    fig, axes = plt.subplots(1, len(ids), figsize=(3.4 * len(ids), 4.4),
                             sharey=True)
    for ax, sid in zip(np.atleast_1d(axes), ids):
        sub = bp[bp["seg"] == sid]
        mmax = sub["mmax"].iloc[0]
        grid = np.arange(MMIN_HAZ, mmax + 0.05, 0.05)

        wsum = sub["weight"].sum()
        ens = np.zeros_like(grid)
        for _, r in sub.iterrows():
            n = r["lam_mmin"] * cum_shape(r["form"], r["b"], MMIN_HAZ,
                                          r["mmax"], grid)
            ens += r["weight"] / wsum * n
            col = "steelblue" if r["rate_model"] == "seismic" else "darkorange"
            ax.semilogy(grid, np.maximum(n, 1e-9), color=col, lw=0.7,
                        alpha=0.5)
        ax.semilogy(grid, np.maximum(ens, 1e-9), "k", lw=2.2,
                    label="interface weighted mean")

        mg, cum, ncell = slab_cum(slab, rc, lo, regions[sid])
        ax.semilogy(mg, np.maximum(cum, 1e-9), color="seagreen", lw=2.2,
                    label=f"intraslab in polygon ({ncell} cells)")

        lam_i = {m: float(np.interp(m, grid, ens)) for m in (6.5, 7.0)}
        lam_s = {m: float(cum[mg >= m - 1e-6][0]) if (mg >= m - 1e-6).any()
                 else 0.0 for m in (6.5, 7.0)}
        rows.append({"region": sid, "cells": ncell,
                     "iface_M6.5": round(lam_i[6.5], 4),
                     "slab_M6.5": round(lam_s[6.5], 4),
                     "ratio_M6.5": round(lam_s[6.5] / lam_i[6.5], 2),
                     "iface_M7.0": round(lam_i[7.0], 4),
                     "slab_M7.0": round(lam_s[7.0], 4),
                     "ratio_M7.0": round(lam_s[7.0] / lam_i[7.0], 2)})

        ax.axvline(MMIN_HAZ, color="gray", lw=0.5, ls="--")
        ax.set_ylim(1e-5, 30)
        ax.set_xlim(4.7, 9.7)
        ax.set_title(sid, fontsize=9)
        ax.set_xlabel("M")
        ax.legend(fontsize=6, loc="lower left")
    np.atleast_1d(axes)[0].set_ylabel("N(>=M) /yr")
    fig.suptitle("interface branches (blue=seismic, orange=geodetic) vs "
                 "intraslab summed over the segment surface projection",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "mfd_interface_vs_intraslab.png", dpi=200)

    tab = pd.DataFrame(rows)
    tab.to_csv(OUT_DIR / "mfd_totals.csv", index=False)
    print(tab.to_string(index=False))
    in_full = tab.loc[tab["region"] == FULL_ID, "slab_M6.5"].iloc[0]
    print(f"\nintraslab total lambda(all cells, M>=4.9) = {slab_total:.2f}/yr; "
          f"share inside the interface footprint (M>=6.5) = {in_full:.3f}/yr")
    print(f"wrote {OUT_DIR}")


if __name__ == "__main__":
    main()