# Point sources from the smoothed grid, capped at CAP_MAG inside the fault
# buffers (bins with lower edge >= CAP_MAG removed there), plus the uncapped
# baseline. Each fault branch pairs the capped points with its fault file;
# "nofaults" is the uncapped points alone.
# Outputs: nrml/points_capped.xml, nrml/points_all.xml, nrml/branches.json,
#          ssm/grid_capped.csv, figures/s04_cap.png

import json

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cfg, nrml, smooth
from crustal import config


def points(df, rb, e, c, path, name, tag):
    dm = round(e[1] - e[0], 6)
    srcs = []
    for i in np.where(rb.sum(axis=1) > 0)[0]:
        r = rb[i, : np.nonzero(rb[i] > 0)[0].max() + 1]
        srcs.append(nrml.point(f"{tag}_{len(srcs):05d}", df.at[i, "lon"], df.at[i, "lat"], c.USD, c.LSD,
                               c.HYPO_DEPTH, c.TRT, nrml.mfd(r, e[0], dm), c.MSR, c.ASPECT, c.NPD))
    nrml.model(path, name, srcs)
    return len(srcs)


def main(c=None):
    c = c or cfg.load(config)
    nd = c.OUT / "nrml"
    nd.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)
    df, rb, e = smooth.read(c.OUT / "ssm" / "grid_total.csv")
    union = gpd.read_file(c.OUT / "faults" / "union.geojson").geometry.iloc[0]
    shapely.prepare(union)
    inside = shapely.contains_xy(union, df["lon"].to_numpy(), df["lat"].to_numpy())

    cap = e[:-1] >= c.CAP_MAG - 1e-6
    rc = rb.copy()
    rc[np.ix_(inside, cap)] = 0.0
    removed = rb[np.ix_(inside, cap)].sum()
    print(f"cells in buffers: {int(inside.sum())}/{len(df)}; N(>={c.CAP_MAG}) removed {removed:.5f}/yr "
          f"({100 * removed / max(rb[:, cap].sum(), 1e-12):.1f} % of the background)")
    smooth.write(df.assign(in_buffer=inside), rc, e, c.OUT / "ssm" / "grid_capped.csv")

    n1 = points(df, rc, e, c, nd / "points_capped.xml", "crustal smoothed, capped", "crc")
    n2 = points(df, rb, e, c, nd / "points_all.xml", "crustal smoothed, uncapped", "cru")
    print(f"point sources: {n1} capped, {n2} uncapped")

    fb = pd.read_csv(c.OUT / "faults" / "branches.csv")
    wf = fb["weight"].sum()
    br = [{"id": r["id"], "files": ["points_capped.xml", r["file"]],
           "weight": (1 - c.W_NOFAULTS) * r["weight"] / wf if wf else 0.0} for _, r in fb.iterrows()]
    br.append({"id": "nofaults", "files": ["points_all.xml"], "weight": c.W_NOFAULTS if wf else 1.0})
    if abs(sum(b["weight"] for b in br) - 1) > 1e-6:
        raise RuntimeError("crustal branch weights do not sum to 1")
    (nd / "branches.json").write_text(json.dumps(br, indent=1))
    print(pd.DataFrame(br)[["id", "weight"]].to_string(index=False))

    f, ax = plt.subplots(figsize=(6, 9))
    v = rb[:, cap].sum(axis=1)
    ax.scatter(df["lon"], df["lat"], c=np.log10(np.maximum(v, 1e-9)), s=2, cmap="magma_r")
    ax.scatter(df.loc[inside, "lon"], df.loc[inside, "lat"], s=1, c="cyan", alpha=0.4)
    gpd.GeoSeries([union]).boundary.plot(ax=ax, color="k", lw=0.5)
    ax.set_aspect("equal")
    ax.set_title(f"background N(>={c.CAP_MAG}) and capped cells (cyan)", fontsize=9)
    f.tight_layout()
    f.savefig(c.FIG / "s04_cap.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s04")


if __name__ == "__main__":
    main()