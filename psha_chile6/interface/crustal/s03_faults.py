# Active-fault sources and fault buffers. Faults with usable attributes get
# one simple-fault source per branch (PHI x MMAX x MFD, plus the reference);
# the same faults, and only those, define the buffers where s04 caps the
# smoothed seismicity at CAP_MAG.
# Outputs: faults/faults.csv, faults/buffers.geojson, faults/branches.csv,
#          nrml/faults__{phi}__{mmax}__{mfd}.xml, nrml/faults__reference.xml

import math

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
import shapely.affinity
from shapely.geometry import LineString, MultiLineString
from shapely.ops import transform, unary_union
from pyproj import CRS, Transformer

from lib import cfg, gr, nrml
from crustal import config

RAKE = {"reverse": 90.0, "normal": -90.0, "dextral": 180.0, "sinistral": 0.0,
        "dextral-reverse": 135.0, "sinistral-reverse": 45.0,
        "dextral-normal": -135.0, "sinistral-normal": -45.0}
CARDINAL = {"N": 0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5, "E": 90.0, "ESE": 112.5, "SE": 135.0,
            "SSE": 157.5, "S": 180.0, "SSW": 202.5, "SW": 225.0, "WSW": 247.5, "W": 270.0,
            "WNW": 292.5, "NW": 315.0, "NNW": 337.5}


def azimuth(v):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return None
    s = str(v).strip().upper()
    if s in CARDINAL:
        return CARDINAL[s]
    try:
        return float(s) % 360.0
    except ValueError:
        return None


def bearing(p, q):
    lo1, la1, lo2, la2 = map(math.radians, (*p, *q))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return math.degrees(math.atan2(y, x)) % 360.0


def length_km(xy):
    lon, lat = np.radians(np.array(xy)).T
    a = np.sin(np.diff(lat) / 2) ** 2 + np.cos(lat[:-1]) * np.cos(lat[1:]) * np.sin(np.diff(lon) / 2) ** 2
    return float((2 * 6371.0 * np.arcsin(np.sqrt(a))).sum())


def read(c):
    """
    Fault records usable as sources.

    A fault is kept if it has dip, depths, slip rate and max_mag, positive
    slip, lsd > usd, 0 < dip <= 90 and max_mag above FAULT_MMIN. With
    ORIENT_BY_DIP_DIR the trace is reversed when dip_dir contradicts the
    right-hand rule OpenQuake applies to simple faults.

    Returns
    -------
    DataFrame
        id, name, coords, L, dip, dip_az, rake, usd, lsd, slip, b, m_obs, flipped.
    """
    g = gpd.read_file(c.FAULTS_SHP)
    g = g.set_crs("EPSG:4326") if g.crs is None else g.to_crs("EPSG:4326")
    f = c.FIELDS
    num = lambda r, k: (None if f.get(k) not in r or r[f[k]] is None or
                        (isinstance(r[f[k]], float) and not np.isfinite(r[f[k]])) else float(r[f[k]]))
    rows, skip, flips = [], [], 0
    for i, r in g.iterrows():
        sid = str(r.get(f["id"]) or f"flt_{i:04d}").strip()
        geo = r.geometry
        xy = ([p for part in geo.geoms for p in part.coords] if isinstance(geo, MultiLineString)
              else list(geo.coords) if geo is not None else [])
        xy = [(float(x), float(y)) for x, y, *_ in xy]
        dip, usd, lsd, slip, mo = (num(r, k) for k in ("dip", "usd", "lsd", "slip", "max_mag"))
        if len(xy) < 2 or None in (dip, usd, lsd, slip, mo):
            skip.append((sid, "missing trace or attribute"))
            continue
        if slip <= 0 or lsd <= usd or not 0 < dip <= 90:
            skip.append((sid, "invalid slip/depth/dip"))
            continue
        if mo <= c.FAULT_MMIN + c.DM / 2:
            skip.append((sid, f"max_mag {mo} <= first fault bin"))
            continue
        dd = azimuth(r.get(f["dip_dir"])) if f["dip_dir"] in r else None
        flip = False
        if c.ORIENT_BY_DIP_DIR and dd is not None and dip < 90:
            right = (bearing(xy[0], xy[-1]) + 90.0) % 360.0
            if abs((right - dd + 180.0) % 360.0 - 180.0) > 90.0:
                xy, flip = xy[::-1], True
                flips += 1
        rows.append({"id": sid, "name": str(r.get(f["name"]) or sid).strip(), "coords": xy, "L": length_km(xy),
                     "dip": dip, "dip_az": dd, "usd": usd, "lsd": lsd, "slip": slip, "m_obs": mo,
                     "b": num(r, "b") or c.DEFAULT_B,
                     "rake": RAKE.get(str(r.get(f["rup_type"], "")).strip().lower(), c.DEFAULT_RAKE),
                     "flipped": flip})
    print(f"faults: {len(rows)} used, {len(skip)} skipped, {flips} traces reversed to match dip_dir")
    for s in skip:
        print(f"  skip {s[0]}: {s[1]}")
    return pd.DataFrame(rows)


def buffers(df, margin):
    """Surface projection of each dipping plane (down-dip side when dip_az is known) plus margin."""
    polys = []
    for r in df.itertuples():
        line = LineString(r.coords)
        c0 = line.centroid
        crs = CRS.from_proj4(f"+proj=aeqd +lat_0={c0.y} +lon_0={c0.x} +units=m")
        fwd = Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform
        inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True).transform
        lm = transform(fwd, line)
        w = 0.0 if r.dip >= 90 else 1000.0 * (r.lsd - r.usd) / math.tan(math.radians(r.dip))
        if r.dip_az is None or w == 0.0:
            pm = lm.buffer(w + 1000.0 * margin)
        else:
            az = math.radians(r.dip_az)
            sh = shapely.affinity.translate(lm, xoff=w * math.sin(az), yoff=w * math.cos(az))
            pm = MultiLineString([lm, sh]).convex_hull.buffer(1000.0 * margin)
        polys.append(transform(inv, pm))
    return gpd.GeoDataFrame({"id": df["id"], "name": df["name"]}, geometry=polys, crs="EPSG:4326")


def mmax_of(r, mode, c):
    """Mmax on the bin-centre grid above FAULT_MMIN: max_mag + MMAX_ADD, or the WC1994 median."""
    if mode == "mobs":
        m = r.m_obs + c.MMAX_ADD
    else:
        from openquake.hazardlib.scalerel.wc1994 import WC1994
        m = WC1994().get_median_mag(r.L * (r.lsd - r.usd) / math.sin(math.radians(r.dip)), r.rake)
    lo = c.FAULT_MMIN + c.DM / 2
    return lo + c.DM * max(math.ceil(round((m - lo) / c.DM, 6)), 1)


def mfd(r, phi, mmax, kind, c):
    """
    Incremental rates from FAULT_MMIN for one fault.

    tgr and tap are scaled so the discrete moment equals phi * mu * L * W * slip
    (moment at bin lower edges when M0_AT_EDGE). al1, al2, al3 (Anderson &
    Luco 1983) and yc (Youngs & Coppersmith 1985) come from the OpenQuake hmtk.

    Returns
    -------
    array
        Rates for bins starting at FAULT_MMIN.
    """
    w = (r.lsd - r.usd) / math.sin(math.radians(r.dip))
    lo = c.FAULT_MMIN + c.DM / 2
    if kind in ("tgr", "tap"):
        from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
        from openquake.hazardlib.mfd.tapered_gr_mfd import TaperedGRMFD
        # OpenQuake rounds min/max to the nearest bin edge (half to even), so pass
        # edges: bin centres sit exactly halfway and round either way
        e0, e1 = c.FAULT_MMIN, mmax + c.DM / 2
        m = (TruncatedGRMFD(e0, e1, c.DM, 4.0, r.b) if kind == "tgr" else
             TaperedGRMFD(e0, e1 + c.TAPER_PAD, mmax, c.DM, 4.0, r.b, c.M0_C))
        mags, rates = map(np.array, zip(*m.get_annual_occurrence_rates()))
        top = mmax if kind == "tgr" else mmax + c.TAPER_PAD
        if abs(mags[0] - lo) > 1e-6 or abs(mags[-1] - top) > 1e-6:
            raise RuntimeError(f"{r.id}/{kind}: bins {mags[0]}-{mags[-1]} != {lo}-{top}")
        mom = (rates * gr.m0(mags - (c.DM / 2 if c.M0_AT_EDGE else 0.0), c.M0_C)).sum()
        rates = rates * phi * c.MU * r.L * 1e3 * w * 1e3 * r.slip * 1e-3 / mom
    else:
        if r.b >= 1.5:
            raise ValueError(f"{r.id}: b = {r.b} >= 1.5 is invalid for {kind}")
        conf = {"Model_Type": {"al1": "First", "al2": "Second", "al3": "Third"}.get(kind), "Model_Weight": 1.0,
                "MFD_spacing": c.DM, "Minimum_Magnitude": lo, "Maximum_Magnitude": mmax,
                "Maximum_Magnitude_Uncertainty": None, "b_value": [r.b, 0.0]}
        if kind == "yc":
            from openquake.hmtk.faults.mfd.youngs_coppersmith import YoungsCoppersmithExponential
            m = YoungsCoppersmithExponential()
            m.setUp(conf)
            m.mmax = mmax
            m0_, _, rates = m.get_mfd(phi * r.slip, r.L * w, shear_modulus=c.MU / 1e9)
        else:
            from openquake.hmtk.faults.mfd.anderson_luco_area_mmax import AndersonLucoAreaMmax
            m = AndersonLucoAreaMmax()
            m.setUp(conf)
            m.mmax = mmax
            m0_, _, rates = m.get_mfd(phi * r.slip, w, shear_modulus=c.MU / 1e9,
                                      disp_length_ratio=c.DISP_LENGTH_RATIO)
        if abs(m0_ - lo) > 1e-6:
            raise RuntimeError(f"{r.id}/{kind}: first bin {m0_} != {lo}")
        rates = np.maximum(np.asarray(rates, float), 0.0)
    return rates


def branches(c):
    for p, (phi, wp) in c.PHI.items():
        for mm, wm in c.MMAX.items():
            for k, wk in c.MFD.items():
                yield f"{p}__{mm}__{k}", phi, mm, k, wp * wm * wk


def main(c=None):
    c = c or cfg.load(config)
    fd, nd = c.OUT / "faults", c.OUT / "nrml"
    fd.mkdir(parents=True, exist_ok=True)
    nd.mkdir(parents=True, exist_ok=True)

    df = read(c)
    df.drop(columns=["coords"]).to_csv(fd / "faults.csv", index=False)
    bf = buffers(df, c.BUFFER_MARGIN_KM)
    bf.to_file(fd / "buffers.geojson", driver="GeoJSON")
    gpd.GeoDataFrame({"cap_mag": [c.CAP_MAG]}, geometry=[unary_union(bf.geometry)],
                     crs="EPSG:4326").to_file(fd / "union.geojson", driver="GeoJSON")

    rows = []
    todo = list(branches(c)) + [("reference", 1.0, "mgeo", "tgr", c.W_REFERENCE)]
    for bid, phi, mm, k, w in todo:
        d = df.copy()
        if bid == "reference":
            d["usd"], d["lsd"] = c.ZONE_DEPTH
        srcs, n, mom, target = [], 0.0, 0.0, 0.0
        for r in d.itertuples():
            mx = mmax_of(r, mm, c)
            rt = mfd(r, phi, mx, k, c)
            ctr = c.FAULT_MMIN + c.DM * (np.arange(len(rt)) + 0.5)
            n += rt.sum()
            mom += (rt * gr.m0(ctr - (c.DM / 2 if c.M0_AT_EDGE else 0.0), c.M0_C)).sum()
            target += phi * c.MU * r.L * 1e3 * (r.lsd - r.usd) / math.sin(math.radians(r.dip)) * 1e3 * r.slip * 1e-3
            srcs.append(nrml.simple_fault(r.id, r.name, r.coords, r.usd, r.lsd, r.dip, r.rake, c.TRT,
                                          nrml.mfd(rt, c.FAULT_MMIN, c.DM), c.FAULT_MSR, c.FAULT_ASPECT))
        fn = f"faults__{bid}.xml"
        nrml.model(nd / fn, f"crustal faults {bid}", srcs)
        rows.append({"id": bid, "file": fn, "weight": w, "n_sources": len(srcs),
                     f"N{c.FAULT_MMIN}": n, "moment_ratio": mom / target})
    tab = pd.DataFrame(rows)
    tab.to_csv(fd / "branches.csv", index=False)
    print(tab.round(4).to_string(index=False))
    cfg.snapshot(c, "s03")


if __name__ == "__main__":
    main()