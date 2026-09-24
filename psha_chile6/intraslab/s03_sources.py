# Point sources from the in-slab grids. Depths per cell from the Slab2 top and
# thickness (see depths()): by default the hypocentre and the lower seismogenic
# depth at the median and 95 % depth of the in-slab catalog below the slab top,
# as fractions of the thickness (intraslab/depth_profile.py). The total grid is the
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


def depths(c, df):
    """
    Hypocentre, upper and lower seismogenic depth (km) of each grid cell.

    Parameters
    ----------
    c : config
        BAND "catalog" (default): upper depth at the Slab2 top, hypocentre and
        lower depth from the in-slab catalog, as fractions of the Slab2
        thickness (CATALOG_DEPTH "frac") or in km by slab-top regime ("regime",
        lower depth capped at the thickness). BAND "plate": top to top +
        thickness; BAND "rule": HALF_THICK and LSD_EXTRA around the hypocentre,
        which is at top + thickness / 2 (HYPO "mid") or top + DEPTH_OFFSET.
    df : pandas.DataFrame
        Grid cells with lon, lat and slab_km.

    Returns
    -------
    tuple of numpy.ndarray
        hypo, usd, lsd, thickness (None when not read)
    """
    top = df["slab_km"].to_numpy()
    need = c.BAND in ("catalog", "plate") or c.HYPO == "mid"
    thk = smooth.slab_node(df["lon"].to_numpy(), df["lat"].to_numpy(), c.SLAB_THK)[0] if need else None
    if c.BAND == "catalog":
        if c.CATALOG_DEPTH == "frac":
            hypo, lsd = top + c.FRAC[0] * thk, top + c.FRAC[1] * thk
        else:
            lim = sorted(c.REGIME)
            dz = np.array([c.REGIME[next(k for k in lim if z < k)] for z in top])
            lsd = top + np.minimum(dz[:, 1], thk)
            hypo = np.minimum(top + dz[:, 0], (top + lsd) / 2)
        return hypo, top, lsd, thk
    hypo = top + thk / 2 if c.HYPO == "mid" else top + c.DEPTH_OFFSET
    if c.BAND == "plate":
        return hypo, top, top + thk, thk
    ht = np.array([next(h for lim, h in c.HALF_THICK if z < lim) for z in hypo])
    usd = np.maximum(hypo - ht, top if c.USD_AT_SLAB_TOP else 0.0)
    return hypo, usd, hypo + ht + c.LSD_EXTRA, thk


def write(c, grid, path, name):
    """Point sources of one grid csv; returns hypocentre depths and N(>=Mmin)."""
    df, rb, e = smooth.read(grid)
    dm = round(e[1] - e[0], 6)
    hypo, usd, lsd, thk = depths(c, df)
    bad = (lsd <= hypo) | (usd > hypo)
    if bad.any():
        raise RuntimeError(f"{name}: {bad.sum()} cells with the hypocentre outside the band "
                           f"(Slab2 thickness there {np.nanmin(thk[bad]) if thk is not None else '-'} km)")

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
          f"hypo {hypo[on].min():.0f}-{hypo[on].max():.0f} km"
          + (f", Slab2 thickness {thk[on].min():.0f}-{thk[on].max():.0f} km "
             f"({(thk[on] < 30).sum()} cells < 30 km)" if thk is not None else ""))
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