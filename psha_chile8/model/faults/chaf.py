"""What the GEM fault database lacks: comparison with CHAF (plan D16, step 2; exploration, nothing is added).

Matches the CHAF strands (Maldonado et al. 2021) to the clean database at 1, 2 and 5 km, compares the systems, joins
the CHAF strands without a match into faults and ranks them. Writes tables/match_<DATE>.csv, tables/systems_<DATE>.csv,
tables/missing_<DATE>.csv (ranked), tables/added_moment_<DATE>.csv and figs/gem_chaf_map.png.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist

import db as D
import geo

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "tables", HERE / "figs"
ROOT = HERE.parents[1]

# settings
DATE = "2026-11-15"
DB = ROOT / "data" / "faults" / f"faults_{DATE}.gpkg"
CAT = ROOT / "catalog" / "frozen" / "2026-11-14" / "catalog_2026-11-14c.csv"
MATCH = (1.0, 2.0, 5.0)
GAP = 5.0                    # strands of one system closer than this join into one fault
WIDTH = 20.0                 # km, rupture width for the magnitude of a full rupture
EQ = dict(mw=5.5, w=0.5, km=10.0)   # crustal events near a fault: Mw, crustal class weight, distance
TOP = 20
MU = 3.0e10
# the 14 cities of DECISIONS (Hazard runs); coordinates as psha_chile7/hazard/config.py
CITIES = {"Iquique": (-70.1357, -20.2133), "Antofagasta": (-70.4000, -23.6500), "Calama": (-68.9333, -22.4667),
          "Copiapó": (-70.3314, -27.3668), "La Serena": (-71.2519, -29.9027), "Valparaíso": (-71.6127, -33.0472),
          "Santiago centro": (-70.6693, -33.4489), "Santiago Peñalolén": (-70.52, -33.46),
          "Concepción": (-73.0503, -36.8269), "Pucón": (-71.9600, -39.2822), "Puerto Montt": (-72.9423, -41.4693),
          "Hornopirén": (-72.4706, -41.9662), "Puerto Aysén": (-72.7020, -45.4028),
          "Puerto Williams": (-67.6096, -54.9336)}
KEY = ("Santiago centro", "Valparaíso", "Concepción")
SENSE = {"reverse": 90.0, "normal": -90.0, "dextral": 180.0, "sinistral": 0.0}


def rake(senses):
    """Rake of the main sense of a group of strands (first term of an oblique sense), None if no strand has one."""
    s = [str(x).split("-")[0].lower() for x in senses if x]
    return SENSE[max(set(s), key=s.count)] if s else None


def mags(L, rk):
    """Median Mw of a full rupture L x WIDTH: Wells and Coppersmith (1994) and Leonard (2014, interplate)."""
    from openquake.hazardlib.scalerel.leonard2014 import Leonard2014_Interplate
    from openquake.hazardlib.scalerel.wc1994 import WC1994
    a = L * WIDTH
    return WC1994().get_median_mag(a, rk), Leonard2014_Interplate().get_median_mag(a, rk)


def pga(mw, rk, rjb):
    """Median PGA (g) of BSSA14 on rock (Vs30 800) at Joyner–Boore distances rjb."""
    from openquake.hazardlib.contexts import simple_cmaker
    from openquake.hazardlib.gsim.boore_2014 import BooreEtAl2014
    cm = simple_cmaker([BooreEtAl2014()], ["PGA"])
    c = cm.new_ctx(len(rjb))
    c["mag"], c["rake"], c["rjb"], c["rrup"], c["vs30"] = mw, 90.0 if rk is None else rk, rjb, rjb, 800.0
    return np.exp(cm.get_mean_stds([c])[0][0, 0])


def groups(ch):
    """Join strands of one system whose traces come closer than GAP km; returns a group label per strand."""
    pts, lab = [], []
    for k, g in enumerate(ch.geometry):
        p = geo.dense(g, 0.5)[0]
        pts.append(p)
        lab.append(np.full(len(p), k))
    pts, lab = np.vstack(pts), np.concatenate(lab)
    pr = cKDTree(geo.xyz(pts)).query_pairs(GAP, output_type="ndarray")
    a, b = lab[pr[:, 0]], lab[pr[:, 1]]
    sy = ch.F_system.values
    k = (a != b) & (sy[a] == sy[b])
    n = len(ch)
    m = coo_matrix((np.ones(k.sum()), (a[k], b[k])), shape=(n, n))
    return connected_components(m, directed=False)[1]


def main():
    import matplotlib
    matplotlib.use("Agg")
    TAB.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    gem = gpd.read_file(DB, layer="faults")
    ch = D.read(D.CHAF)
    ch["L"] = ch.geometry.apply(geo.length)

    # matching at 1, 2, 5 km
    rows = []
    for d in MATCH:
        m = D.match(ch, gem, d=d)
        ch[f"seg{d:g}"] = m.seg
        for a in D.ACT + ["all"]:
            k = (ch.activity == a) if a != "all" else np.ones(len(ch), bool)
            ok = k & (m.seg >= 0)
            rows.append({"km": d, "activity": a, "strands": int(k.sum()), "matched": int(ok.sum()),
                         "km_strands": ch.L[k].sum(), "km_matched": ch.L[ok].sum(),
                         "gem_segments_hit": int(m.seg[ok].nunique())})
    mt = pd.DataFrame(rows)
    mt.to_csv(TAB / f"match_{DATE}.csv", index=False)
    print(mt.round(1).to_string(index=False))

    # GEM segments with no CHAF strand near them (inside the CHAF latitudes)
    cov = [geo.near(g, ch.geometry.union_all(), 2.0) for g in gem.geometry]
    gem["on_chaf"] = cov
    inside = gem.geometry.centroid.y.between(-47.8, -19.3) & gem.geometry.centroid.x.between(-76, -68.5)

    # system against system (2 km)
    gem["sys"] = gem.system.fillna("").replace("", "(none)")
    s = ch[ch["seg2"] >= 0].assign(gsys=lambda x: gem.sys.values[x["seg2"].values])
    st = s.pivot_table(index="F_system", columns="gsys", values="L", aggfunc="sum", fill_value=0.0)
    tot = ch.groupby("F_system").L.sum()
    st.insert(0, "CHAF km", tot.reindex(st.index))
    st = st.reindex(tot.index, fill_value=0.0)
    st["CHAF km"] = tot
    st["matched %"] = 100 * (st.drop(columns="CHAF km").sum(axis=1)) / tot
    st.index = [f"{D.SYSTEMS.get(i, i)} ({i})" for i in st.index]
    st.to_csv(TAB / f"systems_{DATE}.csv")
    print(st.round(0).to_string())
    gs = gem[inside].groupby("sys").apply(lambda x: pd.Series({"segments": len(x), "km": x["length"].sum(),
                                                                "km_on_chaf": (x["length"] * x.on_chaf).sum()}))
    gs.to_csv(TAB / f"gem_on_chaf_{DATE}.csv")
    print(gs.round(0).to_string())

    # unmatched strands joined into faults
    u = ch[ch["seg2"] < 0].reset_index(drop=True)
    u["grp"] = groups(u)
    cat = pd.read_csv(CAT, usecols=["event_id", "time", "lon", "lat", "depth", "mw", "w_crustal"])
    cat = cat[(cat.mw >= EQ["mw"]) & (cat.w_crustal >= EQ["w"])].reset_index(drop=True)
    cx = cKDTree(geo.xyz(cat[["lon", "lat"]].values))
    cities = np.array(list(CITIES.values()))
    out = []
    for k, x in u.groupby("grp"):
        p = np.vstack([geo.dense(g, 0.5)[0] for g in x.geometry])
        q = geo.xyz(p)
        span = pdist(q[np.linspace(0, len(q) - 1, min(len(q), 3000)).astype(int)]).max() if len(q) > 1 else x.L.sum()
        span = max(span, x.L.max())
        rk = rake(x.sense)
        wc, le = mags(span, rk)
        t = cKDTree(q)
        dc = t.query(geo.xyz(cities))[0]
        g = pga(le, rk, np.sqrt(np.maximum(dc, 0.0) ** 2))
        near = sorted({i for h in cx.query_ball_point(q, EQ["km"]) for i in h})
        e = cat.iloc[near].sort_values("mw", ascending=False)
        act = next(a for a in D.ACT if (x.activity == a).any())
        sysn = x.F_system.iloc[0]
        nm = x.assign(n=x.F_name.fillna(x.FT_name).fillna("").str.rstrip("*")).groupby("n").L.sum().sort_values()
        c = x.geometry.union_all().centroid
        nm = " / ".join(n for n in nm.index[::-1][:3] if n) or f"unnamed, {abs(c.y):.1f}° S {abs(c.x):.1f}° W"
        out.append({"grp": k, "name": nm, "system": D.SYSTEMS.get(sysn, sysn),
                    "sys": sysn, "activity": act, "strands": len(x),
                    "proved_km": x.L[x.activity == "Proved"].sum(), "probable_km": x.L[x.activity == "Probable"].sum(),
                    "possible_km": x.L[x.activity == "Possible"].sum(), "km_strands": x.L.sum(), "km_span": span,
                    "sense": "/".join(sorted({str(v) for v in x.sense if v})), "rake": rk,
                    "mw_wc94": wc, "mw_leonard14": le,
                    "city": list(CITIES)[int(np.argmin(dc))], "km_city": dc.min(),
                    **{f"km_{n.split()[0].lower()}": dc[list(CITIES).index(n)] for n in KEY},
                    "pga_city": list(CITIES)[int(np.argmax(g))], "pga_g": g.max(),
                    "eq_n": len(e), "eq": "; ".join(f"{r.time[:10]} Mw {r.mw:.1f}" for r in e.head(4).itertuples()),
                    "eq_max": e.mw.max() if len(e) else np.nan,
                    "slip": "; ".join(sorted({str(v) for v in x.slip_rate if v})),
                    "throw": "; ".join(sorted({str(v) for v in x.throw_rate if v})),
                    "paleo": "; ".join(sorted({str(v) for v in x.paleo_ev if v})),
                    "refs": "; ".join(sorted({str(v) for v in x.refs if v}))[:400],
                    "chaf_ids": ";".join(map(str, x.F_id)), "lon": c.x, "lat": c.y})
    ms = pd.DataFrame(out)
    ms["act_rank"] = ms.activity.map({a: i for i, a in enumerate(D.ACT)})
    ms = ms.sort_values(["act_rank", "pga_g"], ascending=[True, False]).drop(columns="act_rank").reset_index(drop=True)
    ms.insert(0, "rank", np.arange(1, len(ms) + 1))
    ms.to_csv(TAB / f"missing_{DATE}.csv", index=False)
    u.drop(columns="geometry").to_csv(TAB / f"unmatched_strands_{DATE}.csv", index=False)
    print(len(u), "unmatched strands in", len(ms), "faults")
    print(ms.head(30)[["rank", "name", "system", "activity", "strands", "km_span", "mw_leonard14", "city", "km_city",
                       "pga_g", "eq_n", "eq_max"]].round(2).to_string(index=False))

    # what the top faults could add: moment rate with the slip-rate rule the model would need
    w = (gem.z_bot - gem.z_top) / np.sin(np.radians(gem.dip))
    gem["mo"] = MU * gem["length"] * 1e3 * w * 1e3 * gem.sr * 1e-3
    med = gem[gem.system.fillna("") != ""].groupby("system").sr.median()
    top = ms.head(TOP).copy()
    top["sr_rule"] = top.system.map(med).fillna(0.5)
    top["sr_rule_src"] = np.where(top.system.isin(med.index), "median GEM sr of the system", "class 0.1–1 (0.5)")
    top["mo"] = MU * top.km_span * 1e3 * WIDTH * 1e3 * top.sr_rule * 1e-3
    lat = lambda y: np.select([y > -27, y > -38], ["north of 27° S", "27–38° S"], "south of 38° S")
    gem["region"] = lat(gem.geometry.centroid.y)
    top["region"] = lat(top.lat)
    am = pd.DataFrame({"gem_mo": gem.groupby("region").mo.sum(), "added_mo": top.groupby("region").mo.sum()}).fillna(0)
    am["ratio"] = am.added_mo / am.gem_mo
    am.loc["all"] = [am.gem_mo.sum(), am.added_mo.sum(), am.added_mo.sum() / am.gem_mo.sum()]
    am.to_csv(TAB / f"added_moment_{DATE}.csv")
    top[["rank", "name", "system", "km_span", "sr_rule", "sr_rule_src", "mo", "region"]].to_csv(
        TAB / f"added_top_{DATE}.csv", index=False)
    print(am.to_string())
    import figs
    gem = gem.drop(columns=["mo", "region"])
    figs.gem_chaf(gem, ch, ms, CITIES, FIG / "gem_chaf_map.png")


if __name__ == "__main__":
    main()
