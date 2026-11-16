import numpy as np, pandas as pd, shapely
import classify as C

g = C.geoms(C.ARC)
print("arc polygon bounds", np.round(shapely.bounds(g), 3))
ymin = shapely.bounds(g)[1]
c = pd.read_csv("merged/catalog_2026-11-14c.csv", low_memory=False)
z = C.arc_zone(c.lon, c.lat)
top = C.slab_at(c.lon.to_numpy(float), c.lat.to_numpy(float))[0]
def cls(lat, z, top, s):
    return np.where((lat < s) | (np.isnan(top) & (lat < C.GAP_LAT) & (z != "arc")), "patagonia", z)
a, b = cls(c.lat.to_numpy(), z, top, C.SOUTH_LAT), cls(c.lat.to_numpy(), z, top, ymin)
k = c.in_domain & (c.mw >= 5) & (c.w_crustal > 0) & (a != b)
x = c[k].assign(now=a[k], new=b[k]).sort_values("mw", ascending=False)
pd.set_option("display.width", 220)
print(len(x), "events of Mw >= 5 with crustal weight change; weight", x.w_crustal.sum().round(2))
print(x[["event_id", "time", "lon", "lat", "mw", "depth", "w_crustal", "rule", "now", "new"]].to_string(index=False))
k4 = c.in_domain & (c.mw >= 4.5) & (c.w_crustal > 0) & (a != b)
print("Mw >= 4.5:", k4.sum(), c.w_crustal[k4].sum().round(2), pd.crosstab(a[k4], b[k4]).to_string())
f = pd.read_csv("../model/crustal/tables/fault_sources_2026-11-15.csv")
print(list(f.columns))
band = c.in_domain & (c.lat < C.SOUTH_LAT) & (c.lat >= ymin)
print("in the band, all Mw:", band.sum(), "| Mw>=4.5:", (band & (c.mw >= 4.5)).sum(), "| zone:", pd.Series(z[band & (c.mw >= 4.5)]).value_counts().to_dict())
print(c[band & (c.mw >= 4.5)][["time", "lon", "lat", "mw", "depth", "w_crustal", "w_interface", "sub_crustal", "rule"]].assign(zone=z[band & (c.mw >= 4.5)]).sort_values("mw", ascending=False).head(15).to_string(index=False))
ka = band & (a != b)
print("any Mw changing:", ka.sum(), "largest", c.mw[ka].max(), "with Mw", c.mw[ka].notna().sum())
fz = C.arc_zone(f.lon, f.lat); ft = C.slab_at(f.lon.to_numpy(float), f.lat.to_numpy(float))[0]
fa, fb = cls(f.lat.to_numpy(), fz, ft, C.SOUTH_LAT), cls(f.lat.to_numpy(), fz, ft, ymin)
print("table class equals rule now:", (fa == f.cls).mean())
print(f[fa != fb].assign(new=fb[fa != fb])[["db", "fid", "name", "cls", "new", "L", "sr", "mmax20", "N6", "lon", "lat"]].round(4).to_string(index=False))
s = f[(f.lat < -45.5)].assign(zone=fz[f.lat < -45.5])
print(s[["db", "fid", "name", "cls", "zone", "lon", "lat", "L"]].round(2).to_string(index=False))
