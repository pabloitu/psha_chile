"""A9: events on the Scotia–Antarctic boundary classed as crustal Patagonia. Rule tested: an event without a slab whose
nearest boundary is the SC/AN boundary of PB2002 (Bird 2003), nearer than the AN\\SA trench and the Magallanes–Fagnano
system, is not crustal. Run from catalog/ with PYTHONPATH=.:.."""
import json

import cartopy.io.shapereader as shp
import numpy as np
import pandas as pd
import shapely
import shapely.ops

import classify as C

CAT = C.HERE / "frozen" / "2026-11-16" / "catalog_2026-11-16.csv"
PB = C.HERE.parent / "data" / "pb2002_antarctic_trench_2026-11-15.geojson"
FAULTS = C.HERE.parent / "data" / "faults" / "faults_gem_extra_2026-11-15.shp"
MF = ("CL-056b", "CL-056c", "CL-056d", "AR-0056a", "AR-0056b", "AR-0056d", "AR-0056g")
W = ["w_interface", "w_inslab", "w_crustal", "w_outer_rise"]


def km(geom, lon, lat):
    g = shapely.ops.transform(lambda a, b: C.utm(np.asarray(a), np.asarray(b)), geom)
    return shapely.distance(shapely.points(*C.utm(np.asarray(lon, float), np.asarray(lat, float))), g) / 1e3


def lines():
    pb = {f["properties"]["Name"]: shapely.geometry.shape(f["geometry"]) for f in json.load(open(PB))["features"]}
    r = shp.Reader(str(FAULTS))
    rec = list(r.records())
    key = next(k for k in rec[0].attributes if any(str(q.attributes[k]) in MF for q in rec))
    mf = shapely.union_all([q.geometry for q in rec if str(q.attributes[key]) in MF])
    return pb["SC/AN"], pb["AN\\SA"], mf


def main():
    c = pd.read_csv(CAT, low_memory=False)
    c = c[c.in_domain & (c.mw >= 4.5)].reset_index(drop=True)
    sc, an, mf = lines()
    c["d_sc"], c["d_an"], c["d_mf"] = (km(q, c.lon, c.lat).round(0) for q in (sc, an, mf))
    pat = (c.sub_crustal == "patagonia") & (c.w_crustal > 0)
    out = pat & (c.d_sc < c.d_an) & (c.d_sc < c.d_mf)
    pd.set_option("display.width", 220)
    cols = ["event_id", "time", "mw", "lon", "lat", "depth"] + W + ["rule", "rake1", "d_sc", "d_an", "d_mf"]
    print("leave the crustal classes:", out.sum())
    print(c[out].sort_values("time")[cols].round(2).to_string(index=False))
    c[out].sort_values("time")[cols].to_csv(C.HERE.parent / "explore" / "A9" / "scotia_events.csv", index=False)
    print("\nstay in Patagonia south of 50° S:")
    print(c[pat & ~out & (c.lat < -50)].sort_values("lat")[["time", "mw", "lon", "lat", "rule", "d_sc", "d_an", "d_mf"]].to_string(index=False))
    yr = c.time.str[:4].astype(int)
    for lab, k in (("crustal table (Mw 5.0 from 1976)", yr >= 1976), ("all years", yr > 0)):
        print("\n" + lab)
        for m in (5, 6, 7):
            a, b = c.w_crustal[pat & k & (c.mw >= m)].sum(), c.w_crustal[pat & ~out & k & (c.mw >= m)].sum()
            print(f"  Mw >= {m}: {a:.0f} -> {b:.0f}")
    print("largest Patagonia event left:", c.mw[pat & ~out].max(), "| largest leaving:", c.mw[out].max())
    q = c[(c.sub_interface == "antarctic_interface") & (c.lat < -52.07)]
    print("Antarctic interface south of 52.07 S:", len(q), "largest", q.mw.max(), "| nearest boundary SC/AN:", (q.d_sc <= q.d_an).sum())


if __name__ == "__main__":
    main()
