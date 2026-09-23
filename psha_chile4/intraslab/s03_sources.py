# Point sources from the in-slab grids: hypocentre at the Slab2 top of the cell
# plus DEPTH_OFFSET, seismogenic bounds by depth regime (upper bound not above
# the slab top when USD_AT_SLAB_TOP). The total grid is the
# model; each class is also written alone for class-split hazard runs (weight 0
# in branches.json, selected by id in hazard/logic_tree.py). Rates are checked
# against the grids bin by bin.
# Outputs: nrml/intraslab.xml, nrml/intraslab_{class}.xml, nrml/branches.json,
#          figures/s03_depths.png

import json

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cfg, nrml, smooth
from intraslab import config


def write(c, grid, path, name):
    """Point sources of one grid csv; returns hypocentre depths and N(>=Mmin)."""
    df, rb, e = smooth.read(grid)
    dm = round(e[1] - e[0], 6)
    hypo = df["slab_km"].to_numpy() + c.DEPTH_OFFSET
    ht = np.array([next(h for lim, h in c.HALF_THICK if z < lim) for z in hypo])
    usd = np.maximum(hypo - ht, df["slab_km"].to_numpy() if c.USD_AT_SLAB_TOP else 0.0)
    lsd = hypo + ht + c.LSD_EXTRA

    srcs, tot = [], np.zeros(rb.shape[1])
    on = np.where(rb.sum(axis=1) > 0)[0]
    for i in on:
        r = rb[i, : np.nonzero(rb[i] > 0)[0].max() + 1]
        tot[: len(r)] += r
        srcs.append(nrml.point(f"is_{len(srcs):05d}", df.at[i, "lon"], df.at[i, "lat"], usd[i],
                               lsd[i], hypo[i], c.TRT, nrml.mfd(r, e[0], dm), c.MSR, c.ASPECT, c.NPD))
    if not np.allclose(tot, rb.sum(axis=0), rtol=1e-10, atol=0):
        raise RuntimeError(f"{name}: point-source rates differ from the grid")
    nrml.model(path, name, srcs)
    print(f"{name}: {len(srcs)} point sources, N(>={e[0]}) = {tot.sum():.4f}/yr, "
          f"hypo {hypo[on].min():.0f}-{hypo[on].max():.0f} km")
    return df, hypo


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "nrml"
    od.mkdir(parents=True, exist_ok=True)
    df, hypo = write(c, c.OUT / "ssm" / "grid_total.csv", od / "intraslab.xml", "intraslab")
    br = [{"id": "is", "file": "intraslab.xml", "weight": 1.0}]
    for k in c.CLASSES:
        write(c, c.OUT / "ssm" / f"grid_{k}.csv", od / f"intraslab_{k}.xml", f"intraslab_{k}")
        br.append({"id": f"is_{k}", "file": f"intraslab_{k}.xml", "weight": 0.0})
    (od / "branches.json").write_text(json.dumps(br))

    f, ax = plt.subplots(figsize=(6, 9))
    sc = ax.scatter(df["lon"], df["lat"], c=hypo, s=3, cmap="viridis_r")
    f.colorbar(sc, label="hypocentre depth km")
    ax.set_aspect("equal")
    f.savefig(c.FIG / "s03_depths.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s03")


if __name__ == "__main__":
    main()