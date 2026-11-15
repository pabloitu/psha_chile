"""Fault database A against B (D16b, step 3): rates per crustal class against the catalogue fits, faults in one and
not the other, faults near the cities.

A: data/faults/faults_gem_extra_<DATE>.shp. B: data/faults/faults_B_<DATE>.gpkg. Both with the rules of DECISIONS
(rates.py); B also with our MFD rules on the MASCSN moment budget (their thickness and length cap, `budget`), and as
published (MASCSN rates times the mean SCC 0.75); GEM rows of B always with our rules. Magallanes–
Fagnano: one system source per database (DECISIONS), the traces of the main trace joined; the other traces alone.
Class of a source: forearc / arc / backarc from its midpoint and the arc polygon, Patagonia by the rule of A7
(catalog/classify.py). Writes tables/d16b_*_<DATE>.csv and figs/faults_A_B_map.png.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

import geo
import mascsn
import rates as R
from chaf import CITIES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "catalog"))
sys.path.insert(0, str(ROOT / "fits"))
TAB, FIG = HERE / "tables", HERE / "figs"

# settings
DATE = "2026-11-15"
A = ROOT / "data" / "faults" / f"faults_gem_extra_{DATE}.shp"
B = ROOT / "data" / "faults" / f"faults_B_{DATE}.gpkg"
FITS = ROOT / "fits" / "tables" / f"fits_{DATE}b.csv"
CLASSES = ("forearc", "arc", "backarc", "patagonia")
# b of each crustal class: B11 tapered fits (Patagonia takes the forearc b)
SHAPE_B = "taper"
NEAR_KM = 50.0
SAME_KM, SAME_FRAC = 5.0, 0.5
PANELS = {"Northern Chile (18.8–24.6° S)": (-71.0, -68.4, -24.6, -18.8),
          "Santiago and Valparaíso (32.4–34.6° S)": (-72.0, -69.8, -34.6, -32.4),
          "Concepción and Arauco (36.4–38.6° S)": (-74.2, -72.2, -38.6, -36.4),
          "Liquiñe–Ofqui (38–47° S)": (-75.6, -71.0, -47.2, -38.0)}


def classes(lon, lat):
    import classify as K
    z = K.arc_zone(lon, lat)
    top = K.slab_at(np.asarray(lon, float), np.asarray(lat, float))[0]
    pat = (np.asarray(lat) < K.SOUTH_LAT) | (np.isnan(top) & (np.asarray(lat) < K.GAP_LAT) & (z != "arc"))
    return np.where(pat, "patagonia", z)


def budget(x):
    """MASCSN moment budget of MASCSN rows (FaultQuake: mu sr min(L, LAR) T / sin dip, their T and scaling relation),
    N m / yr, on the trace as kept in B (cut traces with their kept length)."""
    import faultquake as F
    out = 0.0
    for y in x.itertuples():
        W = float(y.t_fq) / np.sin(np.radians(y.dip))
        out += R.MU * float(y.sr) * 1e-3 * min(float(y.length), F.lar(y.scr_fq, W)) * 1e3 * W * 1e3
    return out


def sources(f, b, pub=None, mm=False):
    """
    One row per fault source of a database: the Magallanes–Fagnano main trace joined into one system source (rows
    with sr_kind 'measured' in that system), every other row alone.

    Returns
    -------
    DataFrame
        fid, name, cls, L, dip, rake, sr, mmax10, mmax20, rates (our rules), pub (published rates, or None) and, with
        mm, mm (our MFD rules with the MASCSN moment budget on the MASCSN rows, our rules on the GEM rows).
    """
    f = f.copy()
    mid = [g.interpolate(0.5, normalized=True) for g in f.geometry]
    f["lon"], f["lat"] = [p.x for p in mid], [p.y for p in mid]
    f["cls"] = classes(f.lon, f.lat)
    sysk = (f.system == "Magallanes–Fagnano") & (f.sr_kind == "measured")
    groups = [[i] for i in f.index[~sysk]] + ([list(f.index[sysk])] if sysk.any() else [])
    rows = []
    for g in groups:
        x = f.loc[g]
        L = x["length"].sum()
        sr = (x.sr * x["length"]).sum() / L
        dip = float(np.average(x.dip, weights=x["length"]))
        rake = float(x.rake.iloc[np.argmax(x["length"].values)])
        cls = x.cls.iloc[np.argmax(x["length"].values)]
        r, m10, m20 = R.source(L, dip, rake, sr, b[cls])
        p = pub(x) if pub else None
        q = None
        if mm:
            m, g = x[x.src == "MASCSN26"], x[x.src != "MASCSN26"]
            Lg = g["length"].sum()
            sg = (g.sr * g["length"]).sum() / Lg if Lg > 0 else 0.0
            q = R.source(L, dip, rake, sg, b[cls], fixed=budget(m), Lsr=Lg)[0]
        rows.append({"fid": "+".join(x.fid) if len(g) > 1 else x.fid.iloc[0],
                     "name": "Magallanes–Fagnano system" if len(g) > 1 else x["name"].iloc[0], "cls": cls, "L": L,
                     "dip": dip, "rake": rake, "sr": sr, "mmax10": m10, "mmax20": m20, "lon": x.lon.mean(),
                     "lat": x.lat.mean(), "rates": r, "pub": p, "mm": q, "geometry": x.geometry.union_all()})
    return pd.DataFrame(rows)


def table(srcs, fits):
    """N(>= 6, 6.5, 7) and moment rate (M >= 6) per class and domain-wide for every fault model and the fits."""
    import gr
    out = []
    for cl in CLASSES + ("all",):
        for k, s in srcs.items():
            col = "pub" if k.endswith("published") else "mm" if "MASCSN moment" in k else "rates"
            v = s if cl == "all" else s[s.cls == cl]
            r = np.sum([x for x in v[col]], axis=0) if len(v) else np.zeros(40)
            out.append({"class": cl, "model": k, "sources": len(v), "N6": R.n_ge(r, 6.0), "N65": R.n_ge(r, 6.5),
                        "N7": R.n_ge(r, 7.0), "mo": R.moment(r)})
        for sh in ("taper", "trunc"):
            ff = fits[fits["shape"] == sh]
            ff = ff[ff.unit.isin(CLASSES)] if cl == "all" else ff[ff.unit == cl]
            c = gr.centres()
            n = {k: 0.0 for k in ("N6", "N65", "N7", "mo")}
            for f in ff.itertuples():
                d = {"rate": f.rate_mlo, "m_lo": f.m_lo, "b": f.b, "shape": sh, "mmax": f.mmax, "corner": f.corner}
                q = gr.rates(d)
                n["N6"] += float(gr.n_ge(d, 6.0))
                n["N65"] += float(gr.n_ge(d, 6.5))
                n["N7"] += float(gr.n_ge(d, 7.0))
                n["mo"] += float((q[c >= 6.0 - 1e-6] * gr.moment(c[c >= 6.0 - 1e-6])).sum())
            out.append({"class": cl, "model": f"catalogue fit, {'tapered' if sh == 'taper' else 'cut at Mmax'}",
                        "sources": len(ff), **n})
    t = pd.DataFrame(out)
    fit = t[t.model == "catalogue fit, tapered"].set_index("class")
    t["faults_over_fit6"] = [r.N6 / fit.loc[r["class"], "N6"] if not r.model.startswith("catalogue") else np.nan
                             for _, r in t.iterrows()]
    return t


def main():
    TAB.mkdir(exist_ok=True)
    a = gpd.read_file(A).to_crs("EPSG:4326")
    b = gpd.read_file(B, layer="faults")
    fits = pd.read_csv(FITS)
    bb = {c: float(fits[(fits.unit == c) & (fits["shape"] == SHAPE_B)].b.iloc[0]) for c in CLASSES}
    print("b per class:", bb)

    # published MASCSN rates (SCC 1 file), scaled by the share of the trace kept for cut traces
    ms = mascsn.read(mascsn.SCC1).set_index("id")
    L0 = ms.geometry.apply(geo.length)

    def pub(x):
        r = np.zeros(40)
        for y in x[x.src == "MASCSN26"].itertuples():
            s = ms.loc[int(y.mascsn_id)]
            r += R.published(s.m0 + 0.1 * np.arange(len(s.rates)), s.rates * y.length / L0[int(y.mascsn_id)])
        g = x[x.src != "MASCSN26"]
        if len(g):
            L = g["length"].sum()
            r += R.source(L, float(np.average(g.dip, weights=g["length"])), g.rake.iloc[0], (g.sr * g["length"]).sum() / L,
                          bb[g.cls.iloc[0]])[0]
        return r

    sa = sources(a, bb)
    sb = sources(b, bb, pub, mm=True)
    allp = sources(gpd.GeoDataFrame({"fid": [f"MASCSN-{i}" for i in ms.index], "name": ms["name"].fillna("unnamed"),
                                     "system": "", "sr_kind": "restored", "length": L0.values, "sr": 1.0,
                                     "dip": ms.dip, "rake": ms.rake, "src": "MASCSN26", "mascsn_id": ms.index},
                                    geometry=ms.geometry.values, crs="EPSG:4326").reset_index(drop=True), bb, pub)
    t = table({"A (GEM, D16), our rules": sa, "B (MASCSN26 + GEM outside Chile), our rules": sb,
               "B, MASCSN moment, our MFD rules": sb, "B, as published": sb, "MASCSN26 file, all 130 sources, as published": allp}, fits)
    t.round(6).to_csv(TAB / f"d16b_class_table_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        print(t.round(4).to_string(index=False))

    # per source, both databases
    def per(s, k):
        return pd.DataFrame({"db": k, "fid": s.fid, "name": s.name, "class": s.cls, "length": s.L, "dip": s.dip,
                             "sr": s.sr, "mmax10": s.mmax10, "mmax20": s.mmax20,
                             "N6": [R.n_ge(r, 6.0) for r in s.rates], "N65": [R.n_ge(r, 6.5) for r in s.rates],
                             "N7": [R.n_ge(r, 7.0) for r in s.rates], "mo": [R.moment(r) for r in s.rates],
                             "N6_pub": [R.n_ge(r, 6.0) if r is not None else np.nan for r in s.pub],
                             "N6_mm": [R.n_ge(r, 6.0) if r is not None else np.nan for r in s.mm],
                             "lon": s.lon, "lat": s.lat})
    pa, pb = per(sa, "A"), per(sb, "B")
    pd.concat([pa, pb]).round(6).to_csv(TAB / f"d16b_sources_{DATE}.csv", index=False)

    # faults in one database and not the other: less than half of the trace within 5 km of the other database
    ta = geo.tree(a.geometry.union_all())
    tb = geo.tree(b.geometry.union_all())
    a["in_other"] = [geo.near(g, tb, SAME_KM) for g in a.geometry]
    b["in_other"] = [geo.near(g, ta, SAME_KM) for g in b.geometry]
    one = []
    for k, f, s, o in (("A", a, sa, "B"), ("B", b, sb, "A")):
        for x in f[f.in_other <= SAME_FRAC].itertuples():
            r = s[s.fid.str.split("+").apply(lambda v: x.fid in v)].iloc[0]
            share = x.length / r.L
            one.append({"only_in": k, "fid": x.fid, "name": x.name, "system": x.system, "class": r.cls, "length": x.length,
                        "share_in_other": x.in_other, "sr": x.sr, "mmax10": r.mmax10, "mmax20": r.mmax20,
                        "N6": R.n_ge(r.rates, 6.0) * share, "N7": R.n_ge(r.rates, 7.0) * share,
                        "lon": r.lon, "lat": r.lat})
    one = pd.DataFrame(one).sort_values(["only_in", "N6"], ascending=[True, False])
    one.round(5).to_csv(TAB / f"d16b_only_{DATE}.csv", index=False)
    print(one.groupby("only_in").agg(n=("fid", "size"), km=("length", "sum"), N6=("N6", "sum")).round(4))
    print(one.head(25).round(4).to_string(index=False))
    print(one[one.only_in == "B"].head(25).round(4).to_string(index=False))

    # cities: summed fault N(>= 6) within NEAR_KM of the trace, and the largest contributor
    rows = []
    for c, (lon, lat) in CITIES.items():
        d = {"city": c}
        for k, s, col in (("A", sa, "rates"), ("B", sb, "rates"), ("B_mm", sb, "mm"), ("B_pub", sb, "pub")):
            dist = np.array([geo.dist_km(g, lon, lat, step=0.5) for g in s.geometry])
            n = np.array([R.n_ge(r, 6.0) for r in s[col]])
            k_ = dist <= NEAR_KM
            d[f"N6_{k}"] = n[k_].sum()
            d[f"n_{k}"] = int(k_.sum())
            j = np.argmax(np.where(k_, n, -1))
            d[f"top_{k}"] = f"{s.name.iloc[j]} ({dist[j]:.0f} km, {n[j]:.4f})" if k_.any() else ""
        rows.append(d)
    ct = pd.DataFrame(rows)
    ct["B_over_A"] = ct.N6_B / ct.N6_A.replace(0, np.nan)
    ct.round(5).to_csv(TAB / f"d16b_cities_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_colwidth", 60):
        print(ct.round(4).to_string(index=False))

    import figs_b
    figs_b.map_ab(a[a.in_other <= SAME_FRAC], b[b.in_other <= SAME_FRAC], b[b.in_other > SAME_FRAC], CITIES, PANELS,
                  FIG / "faults_A_B_map.png")


if __name__ == "__main__":
    main()
