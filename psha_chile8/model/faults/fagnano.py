"""Magallanes–Fagnano system (plan D16, step 3).

Segments of the clean database, overlap of the Chilean (CL-056) and Argentine (AR-0056) traces, the proposed single
trace, slip rate from GPS, Mmax, one system source against separate segments, and the segments near Puerto Williams.
Writes tables/fagnano_segments_<DATE>.csv, tables/fagnano_overlap_<DATE>.csv, tables/fagnano_rates_<DATE>.csv and
figs/fagnano_segments.png.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

import db as D
import geo

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "tables", HERE / "figs"
ROOT = HERE.parents[1]

# settings
DATE = "2026-11-15"
DB = ROOT / "data" / "faults" / f"faults_{DATE}.gpkg"
CAT = ROOT / "catalog" / "frozen" / "2026-11-14" / "catalog_2026-11-14c.csv"
FITS = ROOT / "fits" / "tables" / "fits_2026-11-15.csv"
SYSTEM = "Magallanes–Fagnano"
UTM = "EPSG:32719"
OVER_KM = 5.0
BOX = (-74.0, -64.0, -55.5, -52.5)
CITY = (-67.6096, -54.9336)
BORDER = D.BORDER
# rule for one trace per section: "territory" (each national database inside its own country) or "detail"
RULE = "territory"
# slip rate from GPS (mm/yr), REPORT_D16.md section 3: preferred = rate on the fault of the preferred model of the latest
# GPS study read in full (Mendoza et al. 2015, Table 3, segments 5.8-6.0); low and high = lowest and highest central
# value of the GPS studies (Mendoza et al. 2011, 4.4; Mendoza et al. 2015, Model 1, 6.8)
SR = (5.9, 4.4, 6.8)
WIDTH = 20.0           # km, z 0-20 km on a vertical fault (database depths)
RAKE = 0.0             # sinistral
MU = 3.0e10
PSI = 0.8              # middle branch of the aseismic coefficient (DECISIONS)
MMIN, DM = 6.0, 0.1


def mmax(area):
    from openquake.hazardlib.scalerel.leonard2014 import Leonard2014_Interplate
    from openquake.hazardlib.scalerel.wc1994 import WC1994
    return WC1994().get_median_mag(area, RAKE), Leonard2014_Interplate().get_median_mag(area, RAKE)


def rates(L, mx, b, sr=SR[0]):
    """
    Truncated Gutenberg–Richter rates of one source, balanced to the moment rate psi mu L W s.

    Returns
    -------
    (array, array)
        Bin centres from MMIN + DM / 2 to the bin that holds mx, and incremental annual rates.
    """
    top = MMIN + DM * max(int(np.ceil(round((mx - MMIN) / DM, 6))), 1)
    m = np.round(np.arange(MMIN + DM / 2, top, DM), 3)
    e = np.r_[m - DM / 2, top]
    n = 10 ** (-b * e) - 10 ** (-b * top)
    inc = n[:-1] - n[1:]
    mo = PSI * MU * L * 1e3 * WIDTH * 1e3 * sr * 1e-3
    return m, inc * mo / (inc * 10 ** (1.5 * m + 9.05)).sum()


def main():
    import matplotlib
    matplotlib.use("Agg")
    import figs
    TAB.mkdir(exist_ok=True)
    f = gpd.read_file(DB, layer="faults")
    s = f[f.system == SYSTEM].reset_index(drop=True)
    # the overlap is measured on the traces as released (the database carries them cut at the border)
    sara = D.read(D.SARA).set_index("id_seg")
    s["geometry"] = sara.geometry.loc[s.gem_id].values
    s["length"] = s.geometry.apply(geo.length)
    full = s[["fid", "geometry"]].copy()
    u = s.to_crs(UTM)

    # overlap of Chilean and Argentine traces within OVER_KM
    cl, ar = u[u.fid.str.startswith("CL")], u[u.fid.str.startswith("AR")]
    rows, ov = [], []
    for i, a in cl.iterrows():
        for j, b in ar.iterrows():
            pa = a.geometry.intersection(b.geometry.buffer(OVER_KM * 1e3))
            if pa.length < 1.0:
                continue
            pb = b.geometry.intersection(a.geometry.buffer(OVER_KM * 1e3))
            rows.append({"cl": a.fid, "ar": b.fid, "cl_km": a.geometry.length / 1e3, "ar_km": b.geometry.length / 1e3,
                         "cl_over_km": pa.length / 1e3, "ar_over_km": pb.length / 1e3,
                         "cl_share": pa.length / a.geometry.length, "ar_share": pb.length / b.geometry.length,
                         "median_gap_km": np.median([pa.interpolate(t, normalized=True).distance(b.geometry)
                                                     for t in np.linspace(0, 1, 50)]) / 1e3,
                         "cl_vertices_per_10km": 1e4 * len(a.geometry.coords) / a.geometry.length,
                         "ar_vertices_per_10km": 1e4 * len(b.geometry.coords) / b.geometry.length,
                         "lon_mid": gpd.GeoSeries([pa], crs=UTM).to_crs(4326).iloc[0].centroid.x})
            ov.append(gpd.GeoSeries([pa], crs=UTM).to_crs(4326).iloc[0])
    o = pd.DataFrame(rows)
    # one trace per section. detail: where two traces overlap, a segment more than half of whose length lies on a
    # more detailed trace (vertices per km) of the other database is dropped. territory: each national database is kept
    # inside its own country, cut at the border
    drop = set()
    for r in o.itertuples():
        if r.cl_vertices_per_10km >= r.ar_vertices_per_10km and r.ar_share > 0.5:
            drop.add(r.ar)
        if r.ar_vertices_per_10km > r.cl_vertices_per_10km and r.cl_share > 0.5:
            drop.add(r.cl)
    from shapely.geometry import box
    west, east = box(-180, -90, BORDER, 0), box(BORDER, -90, 0, 0)
    s["cut"] = [g.intersection(west if f.startswith("CL") else east) for f, g in zip(s.fid, s.geometry)]
    s["km_territory"] = [geo.length(g) if not g.is_empty else 0.0 for g in s.cut]
    s["km_detail"] = np.where(s.fid.isin(drop), 0.0, s["length"])
    s["keep"] = s[f"km_{RULE}"] > 0
    if RULE == "territory":
        s["geometry"] = s.cut
        s["length"] = s.km_territory
    s = s[s["length"] > 0].drop(columns="cut").reset_index(drop=True) if RULE == "territory" else s.drop(columns="cut")
    s["km_city"] = [geo.dist_km(g, *CITY) for g in s.geometry]
    s["vertices_per_10km"] = [10 * len(np.vstack(geo.lines(g))) / L for g, L in zip(s.geometry, s["length"])]
    o.to_csv(TAB / f"fagnano_overlap_{DATE}.csv", index=False)
    s.drop(columns="geometry").to_csv(TAB / f"fagnano_segments_{DATE}.csv", index=False)
    print(s[["fid", "name", "length", "kin", "dip", "sr", "vertices_per_10km", "km_city", "keep"]].round(1).to_string(index=False))
    print(o.round(2).to_string(index=False))
    print("kept km by rule:", {r: round(float(s[f"km_{r}"].sum()), 1) for r in ("territory", "detail")})
    figs.fagnano(full, s[s.keep], ov, CITY, BORDER, FIG / "fagnano_segments.png")

    # Mmax: the system (kept traces), against the observed maximum
    k = s[s.keep]
    Ls = k["length"].sum()
    p = np.vstack(geo.lines(k.geometry.union_all()))
    w, e = p[np.argmin(p[:, 0])], p[np.argmax(p[:, 0])]
    span = geo.GEOD.inv(w[0], w[1], e[0], e[1])[2] / 1e3
    c = pd.read_csv(CAT, usecols=["time", "lon", "lat", "mw", "mw_src", "w_crustal"])
    c = c[c.lon.between(*BOX[:2]) & c.lat.between(*BOX[2:]) & (c.w_crustal >= 0.5)]
    obs = c.mw.max()
    out = {"segments kept": len(k), "length kept (sum, km)": Ls, "length dropped (km)": s.loc[~s.keep, "length"].sum(),
           "end-to-end (km)": span, "area (km2)": Ls * WIDTH,
           "Mmax WC94 (system)": mmax(Ls * WIDTH)[0], "Mmax Leonard14 (system)": mmax(Ls * WIDTH)[1],
           "Mmax Leonard14 (end-to-end)": mmax(span * WIDTH)[1],
           "observed max (frozen catalogue)": obs,
           "observed events Mw>=6.5": "; ".join(f"{t[:10]} {m}" for t, m in zip(c[c.mw >= 6.5].time, c[c.mw >= 6.5].mw))}
    for kk, v in out.items():
        print(f"{kk}: {v if isinstance(v, str) else round(v, 2)}")

    # one system source against separate segments, truncated GR balanced to the GPS slip rate
    fit = pd.read_csv(FITS)
    b = float(fit[(fit.unit == "patagonia") & (fit["shape"] == "trunc")].b.iloc[0])
    rr = []
    for name, grp in (("one system source", [(Ls, mmax(Ls * WIDTH)[1])]),
                      ("separate segments", [(L, mmax(L * WIDTH)[1]) for L in k["length"]])):
        for sr, lab in zip(SR, ("preferred", "low", "high")):
            n65 = n7 = 0.0
            for L, mx in grp:
                m, r = rates(L, mx, b, sr)
                n65 += r[m > 6.5].sum()
                n7 += r[m > 7.0].sum()
            rr.append({"model": name, "sr": lab, "sr_mm": sr, "sources": len(grp),
                       "mmax_range": f"{min(x[1] for x in grp):.2f}–{max(x[1] for x in grp):.2f}",
                       "N_ge_6.5": n65, "N_ge_7": n7, "T_6.5_yr": 1 / n65, "T_7_yr": 1 / n7 if n7 else np.inf})
    rr = pd.DataFrame(rr)
    rr.attrs["b"] = b
    rr.to_csv(TAB / f"fagnano_rates_{DATE}.csv", index=False)
    pd.Series(out).to_csv(TAB / f"fagnano_mmax_{DATE}.csv", header=["value"])
    print(f"b = {b:.3f} (Patagonia, forearc b)")
    print(rr.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
