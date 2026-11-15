"""Fault database B (D16b, step 2): the MASCSN26 faults in Chile plus the cleaned GEM faults outside Chile.

MASCSN rows: trace, dip, rake and depths of the NRML; slip rate = the FaultQuake input slip restored per fault
(mascsn.py), with its seismogenic thickness, scaling relation and Tmean as `t_fq`, `scr_fq`, `tmean_fq`; their Mmax,
b and moment rate kept as `mmax_mascsn`, `b_mascsn`, `mo_mascsn`. GEM rows: the Argentine and Peruvian rows of
database A, unchanged, except those that lie within OVER_KM of a MASCSN trace over more than half their length.
Magallanes–Fagnano: MASCSN traces west of the border, GEM AR-0056 east of it; the main trace takes the GPS slip
rate of DECISIONS. Writes data/faults/faults_B_<DATE>.gpkg (layer `faults`) and .csv, and tables/dbB_*_<DATE>.csv.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box

import db
import geo
import mascsn
from curate import FAGNANO_SR, FAGNANO_SRC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data"
TAB = HERE / "tables"

# settings
DATE = "2026-11-15"
A = DATA / "faults" / f"faults_gem_extra_{DATE}.shp"
REST = TAB / f"mascsn_restored_{DATE}.csv"
CHILE = DATA / f"chile_outline_{DATE}.shp"
OUT = DATA / "faults" / f"faults_B_{DATE}"
# a GEM trace is replaced by a MASCSN trace that lies within OVER_KM of it over more than OVER_FRAC of its length
OVER_KM, OVER_FRAC = 5.0, 0.5
# Magallanes–Fagnano: south of SOUTH the traces are cut at the border (68° 36' 38" W, as in A); the MASCSN traces
# within OVER_KM of the main trace of A over more than half their length are the main trace and take the GPS rate
SOUTH = -52.0
# system names of A (Maldonado et al. 2021 names) for the Table 17 systems found by the Figure 35 boxes
T17_SYSTEM = {"SFA": "Atacama", "TEW": "East–West", "FTA": "Central Coastal Forearc",
              "SFR": "Western Andean Thrust Front", "SFLO": "Liquiñe–Ofqui", "SFM": "Magallanes–Fagnano"}
SRC_REF = ("MASCSN26 crustal fault sources (Bravo Sagua et al. 2026, Modelo Probabilístico de Amenaza Sísmica para "
           "Chile Continental v1.1, CSN; github.com/frabravo/MASCSN26, commit 73b5a8d, SCC 1 file)")
COLS = ["fid", "gem_id", "gem_flt", "system", "sys_src", "name", "kin", "rake", "kin_src", "dip", "dip_dir", "vertical",
        "dip_txt", "dip_src", "sr", "sr_lo", "sr_hi", "sr_kind", "sr_txt", "sr_src", "z_top", "z_bot", "z_src", "length",
        "src", "src_ref", "chaf_ids", "chaf_act", "dup_of", "note", "mascsn_id", "mmax_mascsn", "b_mascsn", "mo_mascsn",
        "sr_mascsn", "t_fq", "scr_fq", "tmean_fq", "fq_how", "geometry"]


def kin(rake):
    """Kinematics of a rake: the nearest of the eight kinds of db.RAKE."""
    k = {v: n for n, v in db.RAKE.items() if n.split("-")[0] in ("dextral", "sinistral", "reverse", "normal")
         and not n.startswith(("reverse-", "normal-"))}
    return k[min(k, key=lambda v: abs((rake - v + 180) % 360 - 180))]


def build():
    a = gpd.read_file(A).to_crs("EPSG:4326")
    a["vertical"] = a.vertical.astype(bool)
    r = pd.read_csv(REST)
    g = mascsn.read(mascsn.SCC1)[["id", "geometry"]]
    m = gpd.GeoDataFrame(r.merge(g, on="id"), crs="EPSG:4326")
    chile = gpd.read_file(CHILE).to_crs("EPSG:4326").union_all()
    log = []

    # MASCSN traces in Chile: cut at the border in Tierra del Fuego
    west = box(-180, -90, db.BORDER, 0)
    keep = []
    for i, x in m.iterrows():
        g0 = x.geometry
        if g0.bounds[1] < SOUTH:
            gc = g0.intersection(west)
            if gc.is_empty:
                log.append((f"MASCSN-{x.id}", x["name"], "dropped: east of the border (GEM AR-0056 there)", geo.length(g0), 0.0))
                continue
            if not gc.equals(g0):
                log.append((f"MASCSN-{x.id}", x["name"], "cut at the border", geo.length(g0), geo.length(gc)))
                m.at[i, "geometry"] = gc
        keep.append(i)
    m = m.loc[keep].copy()
    m["in_chile"] = [float(x.intersection(chile.buffer(0.3)).length / x.length) for x in m.geometry]

    # Magallanes–Fagnano main trace
    fa = a[a.system == "Magallanes–Fagnano"]
    ta = geo.tree(fa.geometry.union_all())
    m["fag_share"] = [geo.near(x, ta, OVER_KM) if x.bounds[1] < SOUTH else 0.0 for x in m.geometry]
    main = m.fag_share > OVER_FRAC

    rows = []
    for i, x in m.iterrows():
        L = geo.length(x.geometry)
        k = kin(x.rake)
        az = geo.azimuth(x.geometry)
        sysn = db.SYSTEMS.get(x.chaf_sys, "") if isinstance(x.chaf_sys, str) and x.chaf_sys else T17_SYSTEM.get(x.t17, "")
        if x.t17_src == "name":
            sysn = T17_SYSTEM[x.t17]
        if x.t17 == "SFM":
            sysn = "Magallanes–Fagnano"
        ssrc = {"name": "name (MASCSN)", "Figure": "MASCSN26 Figure 35 box (p. 76)"}.get(str(x.t17_src).split(" ")[0], x.t17_src)
        d = {"fid": f"MASCSN-{x.id}", "gem_id": None, "gem_flt": None, "system": sysn, "sys_src": ssrc if sysn else "none",
             "name": x["name"] if isinstance(x["name"], str) else "unnamed", "kin": k, "rake": x.rake,
             "kin_src": "MASCSN26 rake (kinematics: nearest kind)", "dip": x.dip,
             "dip_dir": np.nan if x.dip >= 90 else (az + 90) % 360, "vertical": bool(x.dip >= 90), "dip_txt": None,
             "dip_src": "MASCSN26 NRML (dip to the right of the trace)", "sr": x.slip, "sr_lo": np.nan, "sr_hi": np.nan,
             "sr_kind": "restored", "sr_txt": None,
             "sr_src": f"FaultQuake input slip restored from the MASCSN26 rates ({x.how}; mascsn.py)",
             "z_top": x.z_top, "z_bot": x.z_bot, "z_src": "MASCSN26 NRML", "length": L, "src": "MASCSN26",
             "src_ref": SRC_REF, "chaf_ids": x.chaf_ids if isinstance(x.chaf_ids, str) else "",
             "chaf_act": x.chaf_act if isinstance(x.chaf_act, str) else "", "note": "",
             "mascsn_id": int(x.id), "mmax_mascsn": x.mmax, "b_mascsn": x.b, "mo_mascsn": x.mo, "sr_mascsn": x.slip,
             "t_fq": x["T"], "scr_fq": x.scr, "tmean_fq": x.tmean, "fq_how": x.how,
             "geometry": x.geometry}
        notes = []
        if abs(L - x.L) > 0.05:
            notes.append(f"cut at the border {db.BORDER}° (territory rule): {x.L:.1f} -> {L:.1f} km")
        if main[i]:
            d.update(sr=FAGNANO_SR[0], sr_lo=FAGNANO_SR[1], sr_hi=FAGNANO_SR[2], sr_kind="measured", sr_txt="4.4-6.8",
                     sr_src=FAGNANO_SRC)
            notes.append(f"Magallanes–Fagnano main trace: GPS rate of DECISIONS; MASCSN gives {x.slip:.2f} mm/yr")
        elif x.t17 == "SFM":
            notes.append("Magallanes–Fagnano, beside the main trace: MASCSN slip kept (open: double counts the GPS rate?)")
        if x.in_chile < 0.5:
            notes.append(f"only {x.in_chile:.0%} of the trace within 0.3° of Chile")
        d["note"] = "; ".join(notes)
        rows.append(d)
    b = gpd.GeoDataFrame(rows, crs="EPSG:4326")

    # GEM outside Chile: Argentine and Peruvian rows of A, unless a MASCSN trace covers them
    o = a[a.fid.str.startswith(("AR-", "PE-"))].copy()
    tm = geo.tree(b.geometry.union_all())
    o["share_mascsn"] = [geo.near(x, tm, OVER_KM) for x in o.geometry]
    o["in_chile"] = [float(x.intersection(chile).length / x.length) for x in o.geometry]
    for x in o[o.share_mascsn > OVER_FRAC].itertuples():
        log.append((x.fid, x.name, f"dropped: {x.share_mascsn:.0%} within {OVER_KM:.0f} km of a MASCSN trace", x.length, 0.0))
    chk = a[~a.fid.str.startswith(("AR-", "PE-"))]
    chk_out = [(f, float(g.intersection(chile.buffer(0.3)).length / g.length)) for f, g in zip(chk.fid, chk.geometry)]
    o = o[o.share_mascsn <= OVER_FRAC]
    o = o.assign(mascsn_id=np.nan, mmax_mascsn=np.nan, b_mascsn=np.nan, mo_mascsn=np.nan, sr_mascsn=np.nan, t_fq=np.nan,
                 scr_fq="", tmean_fq=np.nan, fq_how="")
    b = pd.concat([b, o[COLS]], ignore_index=True)
    b = gpd.GeoDataFrame(b, geometry="geometry", crs="EPSG:4326")
    b[["t_fq", "tmean_fq"]] = b[["t_fq", "tmean_fq"]].astype(float)

    # duplicates within B, flag only (as D16: within 2 km over more than half of the shorter trace)
    trees = [geo.tree(x) for x in b.geometry]
    dup = []
    for i in range(len(b)):
        for j in range(i + 1, len(b)):
            if b.geometry[i].distance(b.geometry[j]) > 0.05:
                continue
            s, l = (i, j) if b["length"][i] <= b["length"][j] else (j, i)
            f = geo.near(b.geometry[s], trees[l], db.DUP_KM)
            if f > db.DUP_FRAC:
                dup.append((b.fid[s], b.fid[l], f))
    b["dup_of"] = [";".join(l for s, l, f in dup if s == x) for x in b.fid]

    log = pd.DataFrame(log, columns=["fid", "name", "what", "km_before", "km_after"])
    o.drop(columns="geometry").to_csv(TAB / f"dbB_gem_outside_{DATE}.csv", index=False)
    return b[COLS], log, o, pd.DataFrame(chk_out, columns=["fid", "share_in_chile"])


def main():
    b, log, o, chk = build()
    b.to_file(OUT.with_suffix(".gpkg"), layer="faults", driver="GPKG", layer_options={"FID": "gpkg_fid"})
    b.drop(columns="geometry").to_csv(OUT.with_suffix(".csv"), index=False)
    log.to_csv(TAB / f"dbB_changes_{DATE}.csv", index=False)
    print(f"{len(b)} faults written to {OUT}.gpkg / .csv: {b.src.value_counts().to_dict()}")
    print(f"km: {b.groupby('src').length.sum().round(0).to_dict()}")
    print(log.round(1).to_string(index=False))
    print("GEM rows outside Chile kept:", len(o), "; share of their length inside Chile, max", o.in_chile.max().round(2))
    print("A rows with CL/CHAF ids lying mostly outside Chile:", chk[chk.share_in_chile < 0.5].to_string(index=False))
    print(b[b.system == "Magallanes–Fagnano"][["fid", "name", "length", "sr", "sr_mascsn", "note"]].round(2).to_string(index=False))
    print(b.sr_kind.value_counts().to_string())
    print("duplicates flagged:", b[b.dup_of != ""][["fid", "dup_of"]].to_string(index=False))


if __name__ == "__main__":
    main()
