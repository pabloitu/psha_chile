"""B9: completeness in space. Mc on a 0.5 degree grid for the interface and the in-slab family, from 1990 and from
2010 (events within RADIUS, at least NMIN), and Mc per region and network period. Writes cache/space_*.csv."""
import time

import numpy as np
import pandas as pd

import b9_lib as L

STEP, RADIUS, NMIN = 0.5, 150.0, 60
STARTS = [1990, 2010]
FAM = {"interface": ["interface", "antarctic_interface"], "in-slab": ["intraslab_shallow", "intraslab_intermediate", "jujuy_nest"],
       "crustal": ["forearc", "arc", "backarc", "patagonia"]}
WINDOWS = [(1964, 1976), (1976, 1990), (1990, 2000), (2000, 2007), (2007, 2012), (2012, 2027)]


def run():
    d = L.load()
    t, m, lon, lat = (d[c].to_numpy() for c in ("t", "mw", "lon", "lat"))
    rows, reg = [], []
    for fam, cs in FAM.items():
        w = sum(d["W_" + c].to_numpy() for c in cs)
        for y0 in STARTS:
            s = (t >= y0) & (w > 0)
            for la in np.arange(-56, -16.9, STEP):
                for lo in np.arange(-77, -64.9, STEP):
                    near = np.where(s)[0]
                    near = near[np.abs(lat[near] - la) < 1.6]
                    near = near[L.km(lo, la, lon[near], lat[near]) <= RADIUS]
                    n = w[near].sum()
                    if n < NMIN:
                        continue
                    mm, ww = m[near], w[near]
                    mc = L.mc_bstab(mm, ww, nmin=30)
                    rows.append(dict(fam=fam, start=y0, lon=lo, lat=la, n=n, maxc=L.mc_maxc(mm, ww), bstab=mc,
                                     b=L.tinti(mm, ww, mc if np.isfinite(mc) else 5.0)[0],
                                     ratio=ww[mm < 4.95].sum() / max(ww[(mm >= 4.95) & (mm < 5.45)].sum(), 1e-9)))
        for rn, (a, b) in L.REG.items():
            for p, q in WINDOWS:
                s = (t >= p) & (t < q) & (lat >= a) & (lat < b) & (w > 0)
                n = w[s].sum()
                r = dict(fam=fam, region=rn, start=p, end=q, n=n,
                         n45=w[s & (m < 4.95)].sum(), n50=w[s & (m >= 4.95) & (m < 5.45)].sum(), n55=w[s & (m >= 5.45)].sum())
                if n >= 50:
                    r.update(maxc=L.mc_maxc(m[s], w[s]), bstab=L.mc_bstab(m[s], w[s], nmin=30),
                             ks=L.mc_ks(m[s], w[s], nmin=30, rng=np.random.default_rng(4)))
                reg.append(r)
        print(fam, flush=True)
    pd.DataFrame(rows).to_csv(L.CACHE / "space_grid.csv", index=False)
    pd.DataFrame(reg).to_csv(L.CACHE / "space_regions.csv", index=False)


if __name__ == "__main__":
    t0 = time.time()
    run()
    print(f"{time.time() - t0:.0f} s")
