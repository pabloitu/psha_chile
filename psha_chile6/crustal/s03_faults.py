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

    A fault is kept if it has dip, depths and slip rate, positive slip,
    lsd > usd, 0 < dip <= 90 and, when max_mag is given, max_mag above
    FAULT_MMIN (a missing max_mag gives m_obs NaN: the area-based Mmax of
    Leonard is used in the observed branch). With
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
    rows, skip, flips, nomax = [], [], 0, []
    for i, r in g.iterrows():
        sid = str(r.get(f["id"]) or f"flt_{i:04d}").strip()
        geo = r.geometry
        xy = ([p for part in geo.geoms for p in part.coords] if isinstance(geo, MultiLineString)
              else list(geo.coords) if geo is not None else [])
        xy = [(float(x), float(y)) for x, y, *_ in xy]
        dip, usd, lsd, slip, mo = (num(r, k) for k in ("dip", "usd", "lsd", "slip", "max_mag"))
        if len(xy) < 2 or None in (dip, usd, lsd, slip):
            skip.append((sid, "missing trace or attribute"))
            continue
        if slip <= 0 or lsd <= usd or not 0 < dip <= 90:
            skip.append((sid, "invalid slip/depth/dip"))
            continue
        if mo is not None and mo <= 0:
            mo = None
        if mo is not None and mo <= c.FAULT_MMIN + c.DM / 2:
            skip.append((sid, f"max_mag {mo} <= first fault bin"))
            continue
        if mo is None:
            nomax.append(sid)
            mo = float("nan")
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
    print(f"faults: {len(rows)} used, {len(skip)} skipped, {flips} traces reversed to match dip_dir, "
          f"{len(nomax)} without max_mag (Leonard area Mmax in the observed branch): {' '.join(nomax)}")
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
    """
    Mmax on the bin-centre grid above FAULT_MMIN: mobs = max_mag + MMAX_ADD (Leonard when max_mag is
    missing); mwc / mgeo = WC1994 median from the fault area; mleo = Leonard (2010, 2014) interplate.
    """
    area = r.L * (r.lsd - r.usd) / math.sin(math.radians(r.dip))
    if mode == "mobs" and not np.isfinite(r.m_obs):
        mode = "mleo"
    if mode == "mobs":
        m = r.m_obs + c.MMAX_ADD
    elif mode == "mleo":
        from openquake.hazardlib.scalerel.leonard2014 import Leonard2014_Interplate
        m = Leonard2014_Interplate().get_median_mag(area, r.rake)
    else:
        from openquake.hazardlib.scalerel.wc1994 import WC1994
        m = WC1994().get_median_mag(area, r.rake)
    lo = c.FAULT_MMIN + c.DM / 2
    return lo + c.DM * max(math.ceil(round((m - lo) / c.DM, 6)), 1)


def shape(kind, b, lo, mmax, dm, c=None, r=0.5, sig=0.12):
    """
    Unscaled incremental rates of one MFD shape between the bin centres lo and mmax (step dm);
    the cut sits at the top edge mmax + dm / 2. Returns (centres, rates).
    """
    top = mmax + dm / 2
    e = np.round(lo - dm / 2 + dm * np.arange(int(round((top - lo + dm / 2) / dm)) + 1), 6)
    bb = b * math.log(10.0)
    d = np.clip(top - e, 0.0, None)
    if kind == "al1":
        cum = np.exp(bb * d)
    elif kind == "al2":
        cum = np.exp(bb * d) - 1.0
    elif kind == "al3":
        cum = np.exp(bb * d) - 1.0 - bb * d
    elif kind == "hyb":
        # Gaussian characteristic centred 2 sigma below Mmax, cut at +-2 sigma, moment share r;
        # truncated GR below it with 1 - r (r = 1 when no bin lies below the characteristic part)
        m0 = lambda x: 10 ** (1.5 * x + 9.05)
        ctr = e[:-1] + dm / 2
        mc = mmax - 2 * sig
        wc = np.where(np.abs(ctr - mc) <= 2 * sig + 1e-9, np.exp(-0.5 * ((ctr - mc) / sig) ** 2), 0.0)
        wg = np.where(ctr < mc - 2 * sig - 1e-9, 10 ** (-b * ctr), 0.0)
        if wg.sum() == 0:
            r = 1.0
        nu = r * wc / (wc * m0(ctr)).sum()
        if r < 1:
            nu += (1 - r) * wg / (wg * m0(ctr)).sum()
        return ctr, nu
    elif kind == "yc":
        # exponential density below top - 0.5, a box of width 0.5 at the density of the exponential
        # one magnitude unit below the box (Youngs and Coppersmith 1985)
        bx = top - 0.5
        f = lambda m: np.exp(-bb * m)
        cum = (f(e) - f(bx)) / bb + 0.5 * f(bx - 1.0)          # cumulative above e for e below the box
        inbox = e >= bx - 1e-9
        cum[inbox] = (top - e[inbox]) * f(bx - 1.0)
    else:
        raise ValueError(kind)
    cum[-1] = 0.0
    return e[:-1] + dm / 2, np.maximum(cum[:-1] - cum[1:], 0.0)


def moment(r, phi, c):
    """phi * mu * L * W * slip of one fault record (N m / yr)."""
    w = (r.lsd - r.usd) / math.sin(math.radians(r.dip))
    return phi * c.MU * r.L * 1e3 * w * 1e3 * r.slip * 1e-3


def mfd(r, phi, mmax, kind, c, lo=None, target=None):
    """
    Incremental rates for one fault, from the bin centre lo (FAULT_MMIN + DM / 2 by default) to
    mmax, scaled so the discrete moment at the bin centres (lower edges when M0_AT_EDGE) equals
    target (phi * mu * L * W * slip by default).

    Shapes: al1, al2, al3 (Anderson and Luco 1983), yc (Youngs and Coppersmith 1985 characteristic,
    al2 where Mmax < lo + 0.6), tap (tapered GR, corner Mmax, extended by TAPER_PAD; al2 where
    Mmax < lo + 0.2), hyb
    (Gaussian characteristic with HYB_R of the moment over a truncated GR).

    Returns
    -------
    array
        Rates for bins starting at lo.
    """
    target = moment(r, phi, c) if target is None else target
    lo = c.FAULT_MMIN + c.DM / 2 if lo is None else lo
    if kind == "tap" and mmax - lo >= 2 * c.DM - 1e-9:
        from openquake.hazardlib.mfd.tapered_gr_mfd import TaperedGRMFD
        e0, e1 = lo - c.DM / 2, mmax + c.DM / 2
        m = TaperedGRMFD(e0, e1 + c.TAPER_PAD, mmax, c.DM, 4.0, r.b, c.M0_C)
        mags, rates = map(np.array, zip(*m.get_annual_occurrence_rates()))
        if abs(mags[0] - lo) > 1e-6 or abs(mags[-1] - (mmax + c.TAPER_PAD)) > 1e-6:
            raise RuntimeError(f"{r.id}/tap: bins {mags[0]}-{mags[-1]} != {lo}-{mmax + c.TAPER_PAD}")
    else:
        # yc needs an exponential bin below its 0.5 box and tap two bins up to its corner: al2 otherwise
        small = (kind == "yc" and mmax - lo < 0.6 - 1e-9) or (kind == "tap" and mmax - lo < 2 * c.DM - 1e-9)
        mags, rates = shape("al2" if small else kind, r.b, lo, mmax, c.DM,
                            r=getattr(c, "HYB_R", 0.5), sig=getattr(c, "HYB_SIG", 0.12))
    rates = np.maximum(np.asarray(rates, float), 0.0)
    mom = (rates * gr.m0(mags - (c.DM / 2 if c.M0_AT_EDGE else 0.0), c.M0_C)).sum()
    return rates * target / mom


def pairs(df, c):
    """
    Pairs of faults whose traces extend each other: the end of one within LINK_KM of the start of
    the other (both traces dip to the right of their direction, so this is the same dip side),
    strikes within LINK_STRIKE, rakes within LINK_RAKE.

    Returns
    -------
    list of (i, j)
        Row positions; the joined trace runs i then j.
    """
    from lib.dc import hav
    rows = list(df.itertuples())
    out = []
    for i, a in enumerate(rows):
        for j, b in enumerate(rows):
            if i == j:
                continue
            if float(hav(a.coords[-1][0], a.coords[-1][1], b.coords[0][0], b.coords[0][1])) > c.LINK_KM:
                continue
            ds = abs((bearing(a.coords[0], a.coords[-1]) - bearing(b.coords[0], b.coords[-1]) + 180.0) % 360.0 - 180.0)
            dr = abs((a.rake - b.rake + 180.0) % 360.0 - 180.0)
            if ds <= c.LINK_STRIKE and dr <= c.LINK_RAKE:
                out.append((i, j))
    return out


def joined(a, b):
    """One fault record for the pair a then b: joined trace, summed length, length-weighted dip and b."""
    from types import SimpleNamespace
    L = a.L + b.L
    ra, rb = math.radians(a.rake), math.radians(b.rake)
    rake = math.degrees(math.atan2(a.L * math.sin(ra) + b.L * math.sin(rb), a.L * math.cos(ra) + b.L * math.cos(rb)))
    return SimpleNamespace(id=f"{a.id}:{b.id}", name=f"{a.name} + {b.name}", coords=list(a.coords) + list(b.coords), L=L,
                           dip=(a.L * a.dip + b.L * b.dip) / L, usd=(a.usd + b.usd) / 2, lsd=(a.lsd + b.lsd) / 2,
                           slip=(a.L * a.slip + b.L * b.slip) / L, b=(a.L * a.b + b.L * b.b) / L, rake=rake, m_obs=float("nan"))


def write(df, c, nd, fd=None):
    """
    Write the branch files. Each branch holds every single fault and, with FAULT_F > 0, one joined
    source per pair that has magnitude bins above the larger member Mmax; members then keep
    1 - FAULT_F of their moment and each pair receives FAULT_F of its members' moment, shared when
    a member sits in several pairs.

    Returns
    -------
    (DataFrame, DataFrame)
        The branch table (id, file, weight, n_sources, N(>= FAULT_MMIN), moment_ratio) and the pair
        table (per branch: members, Mmax, recurrence of the pair's Mmax event against the faster
        member's own Mmax event).
    """
    pr = pairs(df, c) if c.FAULT_F > 0 else []
    cnt = np.zeros(len(df))
    for i, j in pr:
        cnt[i] += 1
        cnt[j] += 1
    rows, prow = [], []
    todo = list(branches(c)) + [("reference", 1.0, "mwc", "al2", c.W_REFERENCE)]
    for bid, phi, mm, k, w in todo:
        d = df.copy()
        if bid == "reference" and c.FAULT_DEPTH is None:
            d["usd"], d["lsd"] = c.ZONE_DEPTH
        recs = list(d.itertuples())
        mx = [mmax_of(r, mm, c) for r in recs]
        act = []
        for i, j in pr:
            jr = joined(recs[i], recs[j])
            mj = mmax_of(jr, "mleo" if mm == "mobs" else mm, c)
            lo = max(mx[i], mx[j]) + c.DM
            if lo <= mj + 1e-9:
                act.append((i, j, jr, mj, lo))
        cc = np.zeros(len(df))
        for i, j, *_ in act:
            cc[i] += 1
            cc[j] += 1
        srcs, n, mom, target, top = [], 0.0, 0.0, 0.0, {}
        for q, r in enumerate(recs):
            md = moment(r, phi, c)
            tg = md * (1 - c.FAULT_F) if cc[q] > 0 else md
            rt = mfd(r, phi, mx[q], k, c, target=tg)
            ctr = c.FAULT_MMIN + c.DM * (np.arange(len(rt)) + 0.5)
            n += rt.sum()
            mom += (rt * gr.m0(ctr - (c.DM / 2 if c.M0_AT_EDGE else 0.0), c.M0_C)).sum()
            target += md
            top[q] = rt[np.argmin(np.abs(ctr - mx[q]))]
            srcs.append(nrml.simple_fault(r.id, r.name, r.coords, r.usd, r.lsd, r.dip, r.rake, c.TRT,
                                          nrml.mfd(rt, c.FAULT_MMIN, c.DM, 0.0), c.FAULT_MSR, c.FAULT_ASPECT))
        for i, j, jr, mj, lo in act:
            tg = c.FAULT_F * (moment(recs[i], phi, c) / cc[i] + moment(recs[j], phi, c) / cc[j])
            rt = mfd(jr, phi, mj, k, c, lo=lo, target=tg)
            ctr = lo + c.DM * np.arange(len(rt))
            n += rt.sum()
            mom += (rt * gr.m0(ctr - (c.DM / 2 if c.M0_AT_EDGE else 0.0), c.M0_C)).sum()
            srcs.append(nrml.simple_fault(jr.id, jr.name, jr.coords, jr.usd, jr.lsd, jr.dip, jr.rake, c.TRT,
                                          nrml.mfd(rt, lo - c.DM / 2, c.DM, 0.0), c.FAULT_MSR, c.FAULT_ASPECT))
            fast = i if recs[i].slip >= recs[j].slip else j
            tj = 1.0 / rt[np.argmin(np.abs(ctr - mj))] if rt[np.argmin(np.abs(ctr - mj))] > 0 else float("inf")
            tf = 1.0 / top[fast] if top[fast] > 0 else float("inf")
            prow.append({"branch": bid, "pair": jr.id, "L_km": round(jr.L, 1), "mmax_members": max(mx[i], mx[j]), "mmax_pair": mj,
                         "T_pair_mmax_yr": round(tj), "T_faster_member_mmax_yr": round(tf), "pair_shorter": tj < tf})
        fn = f"faults__{bid}.xml"
        nrml.model(nd / fn, f"crustal faults {bid}", srcs)
        rows.append({"id": bid, "file": fn, "weight": w, "n_sources": len(srcs), "n_pairs": len(act),
                     f"N{c.FAULT_MMIN}": n, "moment_ratio": mom / target})
    tab, pt = pd.DataFrame(rows), pd.DataFrame(prow)
    if fd is not None:
        tab.to_csv(fd / "branches.csv", index=False)
        pt.to_csv(fd / "pairs.csv", index=False)
    return tab, pt


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

    if c.FAULT_DEPTH is not None:
        df["usd"], df["lsd"] = c.FAULT_DEPTH
    tab, pt = write(df, c, nd, fd)
    print(tab.round(4).to_string(index=False))
    if len(pt):
        sel = pt[pt["branch"].str.endswith("__al2") & pt["branch"].str.startswith("phi080")]
        print(f"pairs (FAULT_F {c.FAULT_F}): {pt['pair'].nunique()} pairs; phi080 / al2 branches:")
        print(sel.to_string(index=False))
        print(f"  pairs whose Mmax event recurs faster than the faster member's: {int(pt['pair_shorter'].sum())} of {len(pt)} branch rows")
    elif c.FAULT_F > 0:
        print(f"pairs (FAULT_F {c.FAULT_F}): none active")
    cfg.snapshot(c, "s03")


if __name__ == "__main__":
    main()