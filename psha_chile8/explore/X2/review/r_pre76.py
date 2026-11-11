import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
X2 = HERE.parent
sys.path.insert(0, str(X2)); sys.path.insert(0, str(X2.parent / "X1"))
import x2_fit as xf, x1_stats as xs
L, W, R, a = xf.load()
F = json.load(open(X2 / "cache" / "fits_x2.json"))["inv-lin W"]
base = xf.build(F, W, R, a, L, "W", "wmean").mw.to_numpy()
own = xf.build(F, W, R, a, L, "W", "wmean", proxy_only=True).mw.to_numpy()
gem = W["ISC-GEM Mw"].to_numpy(float)
yr = a.yr.to_numpy()
alt = base.copy()
k = (yr < 1976) & np.isfinite(own) & (np.isnan(gem) | (gem < 6.0))
alt[k] = own[k]
d = (yr >= 1964) & (yr < 1976) & np.isfinite(gem) & np.isfinite(own)
print("1964-75 events with ISC-GEM and own proxy:", d.sum())
for lo in (5.0, 5.5, 6.0):
    kk = d & (gem >= lo) & (gem < lo + 0.5)
    print(f"ISC-GEM {lo}-{lo+.5}: median own - ISC-GEM {np.median(own[kk]-gem[kk]):+.2f} (n={kk.sum()})")
t = a.t.to_numpy() / 86400
for nm, m in (("recommended (ISC-GEM first)", base), ("own inverse proxies below ISC-GEM 6", alt)):
    mm = np.round(m / 0.1) * 0.1
    ok = np.isfinite(mm) & (mm >= 3.5) & (yr >= 1964)
    dep = np.zeros(len(mm), bool)
    dep[ok] = xs.gk_flags(t[ok], a.lat.to_numpy()[ok], a.lon.to_numpy()[ok], mm[ok])
    out = []
    for y0, y1 in ((1964, 1976), (1976, 1990), (1990, 2000), (2000, 2011), (2011, 2027)):
        p = ok & ~dep & (yr >= y0) & (yr < y1)
        out.append(f"{y0}-{y1-1}: " + " ".join(f"{(p & (mm >= q - 1e-9)).sum()/(y1-y0):.1f}" for q in (5.0, 5.5, 6.0)))
    print(nm, "| decl rate/yr M>=5.0 5.5 6.0 |", " ; ".join(out))
