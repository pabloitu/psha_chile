"""A9: crustal weight outside the crustal grid (cells of 0.1°), on the frozen catalogue 2026-11-16b."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CAT = ROOT / "catalog" / "frozen" / "2026-11-16b" / "catalog_2026-11-16b.csv"
GRID = ROOT / "data" / "crustal_grid_01_2026-11-15.csv"
W = ["w_interface", "w_inslab", "w_crustal", "w_outer_rise"]


def inside(lon, lat, grid=GRID):
    """True where the point falls in a cell of the grid (cell centres, half-width 0.05°)."""
    g = pd.read_csv(grid)
    cells = set(zip(np.round(g.lon * 10).astype(int), np.round(g.lat * 10).astype(int)))
    i, j = np.round(np.asarray(lon, float) * 10).astype(int), np.round(np.asarray(lat, float) * 10).astype(int)
    return np.array([q in cells for q in zip(i, j)])


def main():
    g = pd.read_csv(GRID)
    print("grid cells", len(g), "lon", g.lon.min(), g.lon.max(), "lat", g.lat.min(), g.lat.max())
    c = pd.read_csv(CAT, low_memory=False)
    c = c[c.in_domain & (c.mw >= 4.5) & (c.w_crustal > 0)].reset_index(drop=True)
    c["ins"], c["yr"] = inside(c.lon, c.lat), c.time.str[:4].astype(int)
    rows = []
    for cl, x in c.groupby("sub_crustal"):
        r = dict(cls=cl)
        for lab, k in (("Mw>=4.5 all", x.mw >= 4.5), ("Mw>=5 from 1976", (x.mw >= 5) & (x.yr >= 1976)), ("Mw>=6 all", x.mw >= 6), ("Mw>=7 all", x.mw >= 7)):
            r[lab] = f"{x.w_crustal[k].sum():.1f} -> {x.w_crustal[k & x.ins].sum():.1f}"
        w1 = x[x.w_crustal > 1 - 1e-9]
        r["max w1"] = f"{w1.mw.max()} -> {w1.mw[w1.ins].max()}"
        r["max any"] = f"{x.mw.max()} -> {x.mw[x.ins].max()}"
        rows.append(r)
    pd.set_option("display.width", 220)
    print(pd.DataFrame(rows).to_string(index=False))
    out = c[~c.ins]
    print("\nleave, Mw >= 6.5:")
    print(out[out.mw >= 6.5].sort_values("time")[["event_id", "time", "mw", "lon", "lat", "depth", "sub_crustal"] + W + ["rule"]].to_string(index=False))
    print("\nleave by class and side:", out.groupby("sub_crustal").apply(lambda y: pd.Series({"n": len(y), "lon min": y.lon.min(), "lon max": y.lon.max(), "lat min": y.lat.min(), "lat max": y.lat.max()}), include_groups=False).round(2).to_string())
    out.sort_values("time")[["event_id", "time", "mw", "lon", "lat", "depth", "sub_crustal"] + W + ["rule"]].to_csv(Path(__file__).parent / "grid_events.csv", index=False)
    for cl in ("forearc", "arc", "patagonia"):
        y = out[(out.sub_crustal == cl) & (out.mw >= 5.5)].sort_values("mw", ascending=False).head(8)
        print("\n", cl, "largest leaving:\n", y[["time", "mw", "lon", "lat", "depth", "w_crustal", "rule"]].to_string(index=False))


if __name__ == "__main__":
    main()
