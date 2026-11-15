"""MASCSN26 crustal fault sources: the method that built them, and their inputs restored per fault (D16b, step 1).

MASCSN26 (Bravo Sagua et al. 2026, v1.1, §8.3) publishes its faults only as NRML: 130 simple faults, 0-12 km,
incremental MFDs from `minMag` 6.0 in 0.1 bins. The rates were made with FaultQuake (faultquake.py): Mmax from the
conflated scaling-relation pdfs, Tmean = M0(Mmax) / (mu V L_eff W) rounded to whole years with M0 = 10^(1.5 M + 9.1),
L_eff = min(L, LAR) (aspect-ratio length of Pace and Peruzza 2002), W = T / sin(dip) with T the seismogenic thickness
of their database (not the 12 km of the NRML), and a truncated GR on the points 6.0..Mmax balanced to M0(Mmax) / Tmean.

Per source: Mmax (last point), b (slope), Tmean (M0(Mmax) over the moment rate, a whole number for every source),
and the FaultQuake inputs that reproduce them: scaling relation, thickness T and slip rate V (`invert`). Writes
tables/mascsn_restored_<DATE>.csv, tables/mascsn_systems_<DATE>.csv, figs/mascsn_slip_systems.png and the
rebuilt model nrml/mascsn26_rebuilt_scc{10,075,05}_<DATE>.xml.
"""
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, box

import db
import faultquake as F
import geo

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"
TAB, FIG, NRML = HERE / "tables", HERE / "figs", HERE / "nrml"

# settings
DATE = "2026-11-15"
SCC1 = DATA / "faults" / "mascsn26" / f"mascsn26_faults_scc1_{DATE}.xml"
SCC05 = DATA / "faults" / "mascsn26" / f"mascsn26_faults_scc05_{DATE}.xml"
MU = 3.0e10
# FaultQuake inputs searched: thickness T (km) on a 0.5 km grid; slip V with at most ND decimals; scaling relations
# WC94 in this order of preference: the kind of the rake first, then strike-slip, all, reverse, normal
TS = np.arange(5.0, 40.01, 0.5)
ND = 2
# below the aspect-ratio cap only V x T is fixed and the database length is not ours: Tmean within TM_TOL (relative)
TM_TOL = 0.02
# Table 17 of the report (p. 77): system, kinematics, slip rate range (mm/yr)
T17 = {"SFA": ("Atacama", "normal", 0.06, 0.07), "TEW": ("Transversales Este-Oeste", "reverse", 0.4, 0.4),
       "SFR": ("San Ramón", "reverse", 0.5, 0.5), "FTA": ("Transversales Noroeste", "normal", 0.5, 0.5),
       "SFLO": ("Liquiñe-Ofqui", "dextral", 4.0, 12.0), "SFM": ("Magallanes", "sinistral", 6.0, 7.0)}
# CHAF systems (Maldonado et al. 2021) that are Table 17 systems; FTA is the Central Coastal Forearc system (Pichilemu,
# named in the Table 17 note); the other CHAF systems have no row in Table 17
CHAF_T17 = {"ATFS": "SFA", "EWFS": "TEW", "WATF": "SFR", "CFTF": "FTA", "LOFS": "SFLO"}
# boxes of Figure 35 (p. 76), read by eye: lon0, lon1, lat0, lat1
FIG35 = {"TEW": (-71.0, -68.0, -21.6, -18.0), "SFA": (-71.2, -69.4, -29.5, -21.6), "FTA": (-72.5, -71.0, -35.6, -32.4),
         "SFR": (-70.9, -70.2, -34.2, -33.0), "SFLO": (-74.6, -71.0, -46.8, -37.8), "SFM": (-76.0, -64.0, -56.0, -52.0)}
NAME = {"San Ramon": "SFR"}
CHAF = DATA / f"chaf_pangea_v1_{DATE}.shp"


def read(f):
    """
    Simple-fault sources of a MASCSN NRML file.

    Returns
    -------
    GeoDataFrame
        id, name, dip, rake, z_top, z_bot, msr, m0 (first point), bw, rates (array), geometry.
    """
    ns = {"n": "http://openquake.org/xmlns/nrml/0.5", "gml": "http://www.opengis.net/gml"}
    out = []
    for s in ET.parse(f).getroot().iter(f"{{{ns['n']}}}simpleFaultSource"):
        g = s.find("n:simpleFaultGeometry", ns)
        m = s.find("n:incrementalMFD", ns)
        xy = np.array(g.find(".//gml:posList", ns).text.split(), float).reshape(-1, 2)
        out.append({"id": int(s.get("id")), "name": s.get("name"), "dip": float(g.find("n:dip", ns).text),
                    "rake": float(s.find("n:rake", ns).text), "z_top": float(g.find("n:upperSeismoDepth", ns).text),
                    "z_bot": float(g.find("n:lowerSeismoDepth", ns).text), "msr": s.find("n:magScaleRel", ns).text,
                    "m0": float(m.get("minMag")), "bw": float(m.get("binWidth")),
                    "rates": np.array(m.find("n:occurRates", ns).text.split(), float), "geometry": LineString(xy)})
    return gpd.GeoDataFrame(out, crs="EPSG:4326")


def kind(rake):
    """WC94 kind of a rake: R, N (within 20° of pure dip slip), S (within 20° of pure strike slip), A otherwise."""
    a = (rake + 180) % 360 - 180
    if abs(abs(a) - 90) <= 20:
        return "R" if a > 0 else "N"
    return "S" if min(abs(a), 180 - abs(a)) <= 20 else "A"


def restore(f):
    """
    Mmax, b, moment rate and Tmean of every source.

    Returns
    -------
    GeoDataFrame
        The sources with L (km), nbin, mmax, b, mo (N m / yr, FaultQuake M0 at the points), tmean (years, a whole number
        in FaultQuake), tm_frac (distance of M0(Mmax) / mo from the nearest whole number), N6, N65, N7 (per year, at
        the magnitudes as OpenQuake reads them).
    """
    s = read(f)
    s["L"] = s.geometry.apply(geo.length)
    s["nbin"] = s.rates.apply(len)
    mags = [np.round(r.m0 + r.bw * np.arange(r.nbin), 6) for r in s.itertuples()]
    s["mmax"] = [m[-1] for m in mags]
    s["b"] = [-np.polyfit(m, np.log10(r), 1)[0] if len(m) > 1 else np.nan for m, r in zip(mags, s.rates)]
    s["mo"] = [(r * F.m0(m)).sum() for m, r in zip(mags, s.rates)]
    t = F.m0(s.mmax) / s.mo
    s["tmean"], s["tm_frac"] = np.round(t), np.abs(t - np.round(t))
    for k, M in (("N6", 6.0), ("N65", 6.5), ("N7", 7.0)):
        s[k] = [r[m >= M - 1e-6].sum() for m, r in zip(mags, s.rates)]
    return s


def systems(s):
    """
    Table 17 system of each source, first that applies: (1) the name; (2) the CHAF system with the largest length of
    strands matched to the trace (db.match: more than half of the strand within 2 km); (3) the boxes of Figure 35.
    """
    ch = gpd.read_file(CHAF).to_crs("EPSG:4326")
    m = db.match(ch, s)
    ch = ch.join(m)
    ch["L"] = ch.geometry.apply(geo.length)
    rows = []
    for i, r in s.iterrows():
        c = ch[ch.seg == i]
        w = c.groupby("F_system").L.sum()
        top = w.idxmax() if len(w) else ""
        act = next((a for a in db.ACT if (c.activity == a).any()), "")
        mid = r.geometry.interpolate(0.5, normalized=True)
        bx = next((k for k, e in FIG35.items() if box(e[0], e[2], e[1], e[3]).contains(mid)), "")
        if r["name"] in NAME:
            t, src = NAME[r["name"]], "name"
        elif top in CHAF_T17:
            t, src = CHAF_T17[top], f"CHAF {top} (matched strands)"
        elif top:
            t, src = "", f"CHAF {top} (matched strands; no Table 17 row)"
        elif bx:
            t, src = bx, "Figure 35 box"
        else:
            t, src = "", "none"
        rows.append({"t17": t, "t17_src": src, "chaf_sys": top, "chaf_ids": ";".join(map(str, c.F_id)), "chaf_act": act,
                     "chaf_km": float(c.L.sum()), "fig35": bx})
    return pd.DataFrame(rows, index=s.index)


def slip(x, scr, T):
    """Slip rate (mm/yr) that gives the moment rate of source x with scaling relation scr and thickness T."""
    W = T / math.sin(math.radians(x.dip))
    Le = min(x.L, F.lar(scr, W))
    return F.m0(x.mmax) / x.tmean / (MU * Le * 1e3 * W * 1e3) * 1e3, Le < x.L


def candidates(x, Ts=TS, tol=0.0):
    """
    FaultQuake inputs that reproduce Mmax and Tmean of source x: every (scaling relation, T) with the same Mmax, the
    slip rate with the fewest decimals (at most ND) whose Tmean is within tol (relative) of the published one.

    Returns
    -------
    list of tuple
        (decimals, preference of the relation, scr, T, V, capped).
    """
    out = []
    for p, scr in enumerate(dict.fromkeys(["WC94-" + kind(x.rake), "WC94-S", "WC94-A", "WC94-R", "WC94-N"])):
        for T in Ts:
            if abs(F.mmax(scr, x.L, x.dip, T) - x.mmax) > 1e-6:
                continue
            V, cap = slip(x, scr, T)
            for nd in range(1, ND + 1):
                Vr = round(V, nd)
                if Vr > 0 and abs(F.tmean(x.mmax, Vr, x.L, x.dip, T, scr) - x.tmean) <= max(tol * x.tmean, 0):
                    out.append((nd, p, scr, T, Vr, cap))
                    break
    return out


def invert(s):
    """
    FaultQuake inputs of every source, in two passes.

    1. Exact: Tmean reproduced exactly; preferred are slip rates with fewer decimals, the scaling relation of the
       rake, whole-km thickness, then the thickness nearest 12 km. Above the aspect-ratio cap (`capped`) the moment
       does not depend on the length, so V and T are both fixed.
    2. Below the cap only V x T is fixed and our trace length is not their database length: the thickness is the most
       common T of the capped exact solutions of the same system, and V the slip with the fewest decimals whose Tmean
       is within TM_TOL; if that T cannot give the Mmax, the best pass-1 or tolerant solution is kept.

    Returns
    -------
    DataFrame
        scr, T, V, capped, how ("exact, capped", "exact", "system T", "tolerant", "none") per source.
    """
    rows = {}
    for i, x in s.iterrows():
        c = sorted(candidates(x), key=lambda v: (v[0], v[1], v[3] % 1 != 0, abs(v[3] - 12)))
        if c and c[0][5] and c[0][0] == 1:
            rows[i] = dict(scr=c[0][2], T=c[0][3], V=c[0][4], capped=True, how="exact, capped")
        elif c:
            rows[i] = dict(scr=c[0][2], T=c[0][3], V=c[0][4], capped=c[0][5], how="exact")
    grp = s.t17.where(s.t17 != "", s.chaf_sys)
    ok = pd.DataFrame(rows).T
    mode = {g: ok.loc[[j for j in ok.index if grp[j] == g and ok.loc[j, "how"] == "exact, capped"], "T"].mode()
            for g in grp.unique()}
    for i, x in s.iterrows():
        if i in rows and rows[i]["how"] == "exact, capped":
            continue
        m = mode.get(grp[i])
        if m is not None and len(m):
            c = sorted(candidates(x, Ts=[float(m.iloc[0])], tol=TM_TOL), key=lambda v: (v[0], v[1]))
            if c:
                rows[i] = dict(scr=c[0][2], T=c[0][3], V=c[0][4], capped=c[0][5], how="system T")
                continue
        if i in rows:
            continue
        c = sorted(candidates(x, tol=TM_TOL), key=lambda v: (v[0], v[1], v[3] % 1 != 0, abs(v[3] - 12)))
        rows[i] = (dict(scr=c[0][2], T=c[0][3], V=c[0][4], capped=c[0][5], how="tolerant") if c else
                   dict(scr="", T=np.nan, V=np.nan, capped=False, how="none"))
    return pd.DataFrame(rows).T.reindex(s.index)


def forward(s):
    """FaultQuake run on the restored inputs: Mmax, Tmean and the largest relative difference to the published rates."""
    out = []
    for x in s.itertuples():
        if not x.scr:
            out.append((np.nan, np.nan, np.nan))
            continue
        mx = F.mmax(x.scr, x.L, x.dip, x.T)
        tm = F.tmean(mx, x.V, x.L, x.dip, x.T, x.scr)
        m, r = F.rates(mx, tm, x.b if np.isfinite(x.b) else 1.0)
        d = np.abs(r / x.rates - 1).max() if len(r) == len(x.rates) else np.inf
        out.append((mx, tm, d))
    return pd.DataFrame(out, columns=["mmax_fq", "tmean_fq", "rate_diff"], index=s.index)


def write(s, scc, out):
    """
    The rebuilt fault model as NRML: geometry, rake and depths of the published file, rates of the FaultQuake run on
    the restored inputs times scc, `minMag` 6.0 as MASCSN wrote it (FaultQuake's first point, read by OpenQuake as the
    first bin centre).
    """
    from xml.sax.saxutils import quoteattr
    L = ['<?xml version="1.0" encoding="utf-8"?>',
         '<nrml xmlns="http://openquake.org/xmlns/nrml/0.5" xmlns:gml="http://www.opengis.net/gml">',
         f'    <sourceModel name="MASCSN26 faults rebuilt with FaultQuake, SCC {scc:g}">',
         '        <sourceGroup rup_interdep="indep" src_interdep="indep" tectonicRegion="Active Shallow Crust">']
    for x in s.itertuples():
        m, r = F.rates(x.mmax_fq, x.tmean_fq, x.b if np.isfinite(x.b) else 1.0)
        pos = "\n".join(f"                            {a} {b}" for a, b in x.geometry.coords)
        L += [f'            <simpleFaultSource id="{x.id}" name={quoteattr(str(x.name))}>',
              '                <simpleFaultGeometry>', '                    <gml:LineString>',
              '                        <gml:posList>', pos, '                        </gml:posList>',
              '                    </gml:LineString>', f'                    <dip>{x.dip}</dip>',
              f'                    <upperSeismoDepth>{x.z_top}</upperSeismoDepth>',
              f'                    <lowerSeismoDepth>{x.z_bot}</lowerSeismoDepth>', '                </simpleFaultGeometry>',
              f'                <rake>{x.rake}</rake>', f'                <magScaleRel>{x.msr}</magScaleRel>',
              '                <ruptAspectRatio>1.0</ruptAspectRatio>',
              f'                <incrementalMFD binWidth="0.1" minMag="{m[0]:.1f}">',
              f'                    <occurRates>{" ".join(repr(float(v)) for v in r * scc)}</occurRates>',
              '                </incrementalMFD>', '            </simpleFaultSource>']
    L += ['        </sourceGroup>', '    </sourceModel>', '</nrml>']
    out.write_text("\n".join(L) + "\n")


def main():
    TAB.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    s = restore(SCC1)
    s = s.join(systems(s))
    print(f"{len(s)} sources; points from {s.m0.unique()} step {s.bw.unique()}; NRML depths {s.z_top.unique()}-"
          f"{s.z_bot.unique()} km; scaling {s.msr.unique()}")
    print(f"Tmean = M0(Mmax) / moment rate: largest distance from a whole number {s.tm_frac.max():.1e} years")

    # the published rates rebuilt with FaultQuake from Mmax, b and the whole-number Tmean
    d = [np.abs(F.rates(x.mmax, x.tmean, x.b if np.isfinite(x.b) else 1.0)[1] / x.rates - 1).max() for x in s.itertuples()]
    s["fq_rebuild"] = d
    h = read(SCC05)
    half = max(np.abs(x / (0.5 * y) - 1).max() for x, y in zip(h.rates, s.rates))
    print(f"FaultQuake TruncatedGR from (Mmax, b, Tmean): largest |rebuilt / published - 1| {max(d):.1e}")
    print(f"SCC 0.5 / (0.5 x SCC 1) - 1: largest {half:.1e} (the SCC 0.5 file is the SCC 1 file halved, not a new "
          f"FaultQuake run, which would round Tmean / 0.5 again)")

    s = s.join(invert(s))
    s = s.join(forward(s))
    s["V"] = s.V.astype(float)
    s["T"] = s["T"].astype(float)
    s["slip_lw"] = s.mo / (MU * s.L * 1e3 * 12e3 / np.sin(np.radians(s.dip))) * 1e3
    print(s.how.value_counts().to_string())
    ex = s[s.how != "none"]
    print(f"forward FaultQuake runs on the restored inputs: Mmax equal {np.isclose(ex.mmax_fq, ex.mmax).sum()} of "
          f"{len(ex)}; Tmean equal {(ex.tmean_fq == ex.tmean).sum()}; rates within 1e-9 {(ex.rate_diff < 1e-9).sum()}, "
          f"within 2 % {(ex.rate_diff < 0.02).sum()}")

    # against Table 17
    s["t17_name"] = s.t17.map(lambda t: T17[t][0] if t else "")
    s["t17_lo"] = s.t17.map(lambda t: T17[t][2] if t else np.nan)
    s["t17_hi"] = s.t17.map(lambda t: T17[t][3] if t else np.nan)
    s["slip"] = s.V
    s["vs_t17"] = np.where(s.t17 == "", "", np.where(s.slip < s.t17_lo * 0.995, "below",
                                                     np.where(s.slip > s.t17_hi * 1.005, "above", "inside")))
    cols = ["id", "name", "t17", "t17_name", "t17_src", "chaf_sys", "chaf_act", "chaf_ids", "L", "dip", "rake", "z_top",
            "z_bot", "nbin", "mmax", "b", "mo", "tmean", "scr", "T", "V", "capped", "how", "mmax_fq", "tmean_fq",
            "rate_diff", "slip", "slip_lw", "t17_lo", "t17_hi", "vs_t17", "N6", "N65", "N7", "fq_rebuild"]
    out = s[cols].copy()
    out["lon_mid"] = [g.interpolate(0.5, normalized=True).x for g in s.geometry]
    out["lat_mid"] = [g.interpolate(0.5, normalized=True).y for g in s.geometry]
    out.round(6).to_csv(TAB / f"mascsn_restored_{DATE}.csv", index=False)

    g = s.groupby(s.t17.replace("", "none"))
    sy = pd.DataFrame({"sources": g.size(), "km": g.L.sum(),
                       "T": g["T"].agg(lambda v: ", ".join(f"{t:g}" for t in sorted(set(v.dropna())))),
                       "V": g.V.agg(lambda v: ", ".join(f"{t:g}" for t in sorted(set(v.dropna())))),
                       "t17_lo": g.t17_lo.first(), "t17_hi": g.t17_hi.first(),
                       "inside": g.vs_t17.apply(lambda v: (v == "inside").sum()),
                       "below": g.vs_t17.apply(lambda v: (v == "below").sum()),
                       "above": g.vs_t17.apply(lambda v: (v == "above").sum()),
                       "b": g.b.agg(lambda v: ", ".join(f"{x:.2f}" for x in sorted(set(np.round(v.dropna(), 2))))),
                       "mmax": g.mmax.agg(lambda v: f"{v.min():.1f}-{v.max():.1f}"), "mo": g.mo.sum()})
    sy.to_csv(TAB / f"mascsn_systems_{DATE}.csv")
    with pd.option_context("display.width", 250, "display.max_colwidth", 80):
        print(sy.to_string())
        print(s[["id", "name", "t17", "chaf_sys", "L", "dip", "mmax", "tmean", "scr", "T", "V", "capped", "how",
                 "rate_diff"]].sort_values(["t17", "chaf_sys", "L"]).round(4).to_string(index=False))

    # rebuilt model, the three SCC branches of the MASCSN logic tree (the repository has SCC 1 and 0.5 only)
    NRML.mkdir(exist_ok=True)
    for scc in (1.0, 0.75, 0.5):
        write(s, scc, NRML / f"mascsn26_rebuilt_scc{str(scc).replace('.', '')}_{DATE}.xml")
    r = read(NRML / f"mascsn26_rebuilt_scc10_{DATE}.xml")
    print(f"rebuilt SCC 1 file read back: largest |rebuilt / published - 1| "
          f"{max(np.abs(a / b - 1).max() for a, b in zip(r.rates, s.rates)):.4f}")

    import figs_b
    figs_b.slip_systems(s, T17, FIG / "mascsn_slip_systems.png")


if __name__ == "__main__":
    main()
