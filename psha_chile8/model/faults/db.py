"""Clean crustal fault database (plan D16, step 1).

Reads the frozen copy of the fault file of the model (`crustal_faults_chile_updated`: 156 segments of the GEM SARA
release and 4 rows added by hand), keeps only properties of the faults, gives every value its source, flags
duplicates, and matches every segment to the strands of CHAF (Maldonado et al. 2021) that lie on it. Writes
data/faults/faults_<DATE>.gpkg (layer `faults`, EPSG:4326), data/faults/faults_<DATE>.csv (no geometry) and
tables/d16_changes_<DATE>.csv, tables/d16_duplicates_<DATE>.csv, tables/d16_hand_rows_<DATE>.csv.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

import geo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data"
TAB = HERE / "tables"

# settings
DATE = "2026-11-15"
IN = "2026-11-15"
UPD = DATA / f"crustal_faults_chile_updated_{IN}.shp"
SARA = DATA / f"sara_active_faults_{IN}.shp"
CHAF = DATA / f"chaf_pangea_v1_{IN}.shp"
OUT = DATA / "faults" / f"faults_{DATE}"
# duplicates: traces within DUP_KM over more than DUP_FRAC of the shorter one
DUP_KM, DUP_FRAC = 2.0, 0.5
# CHAF strand on a GEM trace: within MATCH_KM over more than MATCH_FRAC of the strand
MATCH_KM, MATCH_FRAC = 2.0, 0.5
# area-source fields of the GEM release, not properties of the fault
AREA = ["id_area", "min_mag", "max_mag", "a_val", "b_val", "usd", "lsd"]
# slip-rate activity classes of the GEM release (mm/yr); any other range is a range of the source
CLASSES = [(0.01, 0.1), (0.1, 1.0), (1.0, 5.0)]
# rake from the kinematics, Aki and Richards convention; oblique kinds halfway between their two terms
RAKE = {"reverse": 90.0, "normal": -90.0, "sinistral": 0.0, "dextral": 180.0,
        "sinistral-reverse": 45.0, "dextral-reverse": 135.0, "sinistral-normal": -45.0, "dextral-normal": -135.0,
        "reverse-sinistral": 45.0, "reverse-dextral": 135.0, "normal-sinistral": -45.0, "normal-dextral": -135.0}
CARDINAL = {"N": 0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5, "E": 90.0, "ESE": 112.5, "SE": 135.0, "SSE": 157.5,
            "S": 180.0, "SSW": 202.5, "SW": 225.0, "WSW": 247.5, "W": 270.0, "WNW": 292.5, "NW": 315.0, "NNW": 337.5}
# open dip classes of the GEM release and the value GEM gives them
OPEN_DIP = {">60": 72.0, "<45": 37.0, "<30": 20.0}
ACT = ["Proved", "Probable", "Possible"]
# CHAF systems (Maldonado et al. 2021, Table 1)
SYSTEMS = {"ATFS": "Atacama", "CAFS": "Central Andean", "CCFS": "Cachet", "CDFS": "Caldera",
           "CFTF": "Central Coastal Forearc", "CdSF": "Cordillera de la Sal", "EWFS": "East–West", "EXFS": "Exploradores",
           "LAFS": "Lanalhue", "LLFS": "Lago Laja", "LOFS": "Liquiñe–Ofqui", "LOTF": "Liquiñe–Ofqui Transverse",
           "LVFS": "Los Vilos–Puerto Aldea", "SFFS": "South-Central Coastal Forearc", "SMFS": "Santa María",
           "SdAF": "Salar de Atacama", "WATF": "Western Andean Thrust Front", "not assigned": "not assigned"}
# systems named by the GEM fault ID (one GEM fault, segments named after the branches)
# faults added from CHAF (Pablo, 15 Nov): one simplified trace (geo.trace) through the strands of the CHAF names given,
# leaving out the strands already on a GEM trace and those dipping to the sides given (antithetic strands); kinematics
# and dip direction from the strands (Valparaíso and Quintay give no dip direction: SW as the parallel Laguna Verde and
# Marga-Marga faults); Santa María: only its reverse strand (the other CHAF strands are short normal faults on the island); dip 72 (GEM's value for the forearc faults, class ">60"), depths 0-20 km and
# slip rate 0.5 (class 0.1-1) as the similar GEM forearc faults
ADD = {"Mejillones, northern section": dict(names=("Mejillones", "Sistema de Fallas Mejillones"), skip_dip=("W", "NW")),
       "Valparaíso": dict(names=("Valparaiso",), side="SW"),
       "Quintay": dict(names=("Quintay",), kin="normal", side="SW",
                       kin_src="as the parallel Laguna Verde and Marga-Marga faults"),
       "Santa María": dict(names=("Santa Maria (SMFS)",), kin="reverse",
                           kin_src="CHAF Santa Maria (SMFS) strand; blind reverse splay (Jara-Muñoz et al. 2017)")}
ADD_SR = (0.5, 0.1, 1.0)
ADD_DIP = 72.0
# hand rows whose trace is extended to all strands of their CHAF name (Pablo, 15 Nov)
EXTEND = {"Marga Marga": ("Marga-Marga",), "Laguna Verde": ("Laguna Verde",)}
# Magallanes–Fagnano, one trace per section: each national database inside its own country, cut at the
# Chile–Argentina border in Tierra del Fuego, 68° 36' 38" W (Pablo, 15 Nov)
BORDER = -68.6106
GEM_SYSTEM = {"CL-006": "Liquiñe–Ofqui", "CL-056": "Magallanes–Fagnano", "AR-0056": "Magallanes–Fagnano"}


def read(f):
    g = gpd.read_file(f)
    return g.set_crs("EPSG:4326") if g.crs is None else g.to_crs("EPSG:4326")


def bounds(t):
    """Lower and upper value of a text such as '0.1-1', '1.0-5.0', '0.3 0.5', '45a60', '0.4' (None if no number)."""
    if t is None or (isinstance(t, float) and np.isnan(t)):
        return None
    v = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(t))]
    if not v:
        return None
    return min(v), max(v)


def match(chaf, gem, d=MATCH_KM, frac=MATCH_FRAC):
    """
    CHAF strands that lie on GEM traces.

    A strand matches a GEM segment when more than `frac` of its length lies within `d` km of the segment
    trace; a strand that matches several segments goes to the one it follows over the largest share.

    Returns
    -------
    DataFrame
        One row per CHAF strand: index of chaf, `seg` (index of gem or -1), `share` (largest share).
    """
    trees = [geo.tree(g) for g in gem.geometry]
    cen = np.array([[g.centroid.x, g.centroid.y] for g in gem.geometry])
    out = []
    for i, g in chaf.geometry.items():
        c = g.centroid
        k = np.flatnonzero(np.hypot(cen[:, 0] - c.x, cen[:, 1] - c.y) < 3.0)
        s = np.array([geo.near(g, trees[j], d) for j in k]) if len(k) else np.zeros(0)
        j = int(np.argmax(s)) if len(s) else -1
        ok = j >= 0 and s[j] > frac
        out.append({"i": i, "seg": int(gem.index[k[j]]) if ok else -1, "share": float(s[j]) if j >= 0 else 0.0})
    return pd.DataFrame(out).set_index("i")


def build():
    """
    The clean database as a GeoDataFrame, with the tables of what changed, duplicates and the rows added by hand.
    """
    u = read(UPD)
    sara = read(SARA)
    chaf = read(CHAF)
    assert not set(u.columns) - set(sara.columns)
    hand = u["id_seg"].isna()

    rows, chg = [], []
    cn = chaf.F_name.fillna("").str.rstrip("*")
    for i, r in u.iterrows():
        g = r.geometry
        if hand[i] and r["name"] in EXTEND:
            L0 = geo.length(g)
            g = geo.trace(chaf.geometry[cn.isin(EXTEND[r["name"]])])
            chg.append((r["name"], "geometry", f"{L0:.1f} km", f"{geo.length(g):.1f} km, CHAF strands {', '.join(EXTEND[r['name']])}"))
        d = {"fid": r.id_seg, "gem_id": r.id_seg, "gem_flt": r.id_flt, "name": r["name"], "src": "SARA",
             "src_ref": "GEM SARA active faults (sara-active-faults release)", "note": ""}
        notes = []

        # kinematics and rake
        k = None if r.rup_type in (None, "None") else str(r.rup_type).strip().lower()
        d["kin_src"] = "SARA"
        if k is None and not hand[i]:
            sib = sara[(sara.id_flt == r.id_flt) & (sara.dips == r.dips) & ~sara.rup_type.isin([None, "None"])]
            if len(sib):
                k = sib.rup_type.mode().iloc[0]
                d["kin_src"] = f"rule: GEM siblings of {r.id_flt} with dip {r.dips} ({', '.join(sib.id_seg)})"
            else:
                k = "reverse"
                d["kin_src"] = "assumed: reverse (none in SARA, no sibling; old model default rake 90)"
            chg.append((r.id_seg, "kin", "missing", k))
        d["kin"], d["rake"] = k, RAKE.get(k, np.nan) if k else np.nan

        # dip: the number given, the midpoint of a given range, GEM's value for an open class
        t = None if r.dips in (None, "None") else str(r.dips).strip()
        b = bounds(t) if t and t not in OPEN_DIP else None
        if t in OPEN_DIP:
            dip, ds = OPEN_DIP[t], "SARA class value"
        elif b:
            dip, ds = (b[0] + b[1]) / 2, "SARA dips text" + (" (midpoint)" if b[0] != b[1] else "")
        else:
            dip, ds = float(r.dip), "SARA dip" if not hand[i] else "hand row"
        if not hand[i] and abs(dip - float(r.dip)) > 0.01:
            chg.append((r.id_seg, "dip", r.dip, dip))
        dd = None if r.dip_dir is None else str(r.dip_dir).strip().upper()
        d["dip"], d["dip_txt"], d["dip_src"] = dip, t, ds
        d["dip_dir"] = CARDINAL.get(dd, np.nan)
        d["vertical"] = dd == "VERTICAL" or dip >= 90.0
        if dd == "VERTICAL" and dip < 90:
            notes.append(f"dip_dir VERTICAL with dip {dip}")
        if np.isfinite(d["dip_dir"]):
            a = geo.azimuth(g)
            off = abs((d["dip_dir"] - a + 90) % 180 - 90)
            if off < 30:
                notes.append(f"dip direction {dd} within {off:.0f}° of the trace azimuth {a:.0f}°")

        # slip rate
        st = None if r.slip_rates in (None, "None") else str(r.slip_rates).strip()
        b = bounds(st)
        d["sr"], d["sr_txt"] = float(r.slip_rate), st
        d["sr_lo"], d["sr_hi"] = (b if b and b[0] < b[1] else (np.nan, np.nan))
        if b and b[0] < b[1]:
            d["sr_kind"] = "class" if b in CLASSES else "range"
        else:
            d["sr_kind"] = "measured"
        d["sr_src"] = "SARA" if not hand[i] else "hand row"

        # depths as given
        d["z_top"], d["z_bot"] = float(r.upp_sd), float(r.low_sd)
        d["z_src"] = "SARA" if not hand[i] else "hand row"

        d["length"] = geo.length(g)
        if not hand[i] and abs(d["length"] - r.len_st) > 0.01 * d["length"]:
            chg.append((r.id_seg, "length", r.len_st, d["length"]))
        if hand[i] and r["name"] in EXTEND:
            notes.append(f"trace extended to the CHAF strands {', '.join(EXTEND[r['name']])} (D16)")
        if hand[i]:
            d["kin_src"], d["dip_src"] = "hand row", "hand row" + (" (midpoint)" if "midpoint" in ds else "")
        d["note"] = "; ".join(notes)
        d["geometry"] = g
        rows.append(d)

    # faults added from CHAF
    trees = [geo.tree(x["geometry"]) for x in rows]
    for nm, a in ADD.items():
        x = chaf[cn.isin(a["names"])]
        x = x[[max(geo.near(g, t, MATCH_KM) for t in trees) <= MATCH_FRAC for g in x.geometry]]
        x = x[~x.dipdir.fillna("").str.upper().isin(a.get("skip_dip", ()))]
        g = geo.trace(x.geometry, step=a.get("step", 2.0))
        L = x.assign(L=x.geometry.apply(geo.length))
        sense = L.dropna(subset=["sense"]).groupby(L.sense.str.split("-").str[0].str.lower()).L.sum()
        k = a.get("kin") or (sense.idxmax() if len(sense) else "normal")
        side = L.assign(dipdir=a["side"]) if a.get("side") else L.dropna(subset=["dipdir"])
        side = side.assign(az=side.dipdir.str.upper().map(CARDINAL)).dropna(subset=["az"])
        az = geo.azimuth(g)
        dd = np.nan
        if len(side):
            m = np.degrees(np.arctan2((side.L * np.sin(np.radians(side.az))).sum(), (side.L * np.cos(np.radians(side.az))).sum()))
            dd = min(((az + 90) % 360, (az - 90) % 360), key=lambda v: abs((v - m + 180) % 360 - 180))
        top = L.sort_values("L").iloc[-1]
        refs = "; ".join(sorted({str(v) for v in x.refs if v}))
        rows.append({"fid": f"CHAF-{top.F_id}", "gem_id": None, "gem_flt": None, "name": nm,
                     "src": "CHAF strands, simplified trace (added D16)", "src_ref": f"CHAF {', '.join(a['names'])}: {refs}",
                     "kin": k, "rake": RAKE[k], "kin_src": a.get("kin_src", "CHAF strands (main sense by length)"),
                     "dip": ADD_DIP, "dip_txt": None, "dip_src": "rule: GEM value of the forearc faults (class >60)",
                     "dip_dir": dd, "vertical": False,
                     "sr": ADD_SR[0], "sr_lo": ADD_SR[1], "sr_hi": ADD_SR[2], "sr_kind": "class", "sr_txt": "0.1-1",
                     "sr_src": "rule: class of the similar GEM forearc faults (0.1-1, 0.5)",
                     "z_top": 0.0, "z_bot": 20.0, "z_src": "rule: as the GEM rows", "length": geo.length(g),
                     "note": f"{len(x)} CHAF strands ({x.activity.value_counts().to_dict()}); dip direction perpendicular to "
                             f"the trace on the side " + (f"{a['side']} of the parallel faults" if a.get("side") else "of the strands"), "geometry": g})
        chg.append((nm, "added", "", f"{geo.length(g):.1f} km from {len(x)} CHAF strands"))

    db = gpd.GeoDataFrame(rows, crs="EPSG:4326")

    # systems: GEM fault ID, then the CHAF strands on the trace
    m = match(chaf, db)
    chaf = chaf.join(m)
    for i in db.index:
        s = chaf[chaf.seg == i]
        db.loc[i, "chaf_ids"] = ";".join(str(x) for x in s.F_id)
        db.loc[i, "chaf_act"] = next((a for a in ACT if (s.activity == a).any()), "")
        pre = next((p for p in GEM_SYSTEM if str(db.loc[i, "gem_flt"]).startswith(p)), None)
        if pre:
            db.loc[i, ["system", "sys_src"]] = GEM_SYSTEM[pre], f"GEM fault {pre}"
        elif re.match(r"(Sistema de fallas|Zona de falla|Grupo de fallas) ", str(db.loc[i, "name"])):
            db.loc[i, ["system", "sys_src"]] = re.sub(r"^\S+ de fallas? ", "", db.loc[i, "name"]), "GEM fault name"
        elif len(s):
            w = s.assign(L=s.geometry.apply(geo.length)).groupby("F_system").L.sum()
            db.loc[i, ["system", "sys_src"]] = SYSTEMS.get(w.idxmax(), w.idxmax()), f"CHAF {w.idxmax()} (matched strands)"
        else:
            db.loc[i, ["system", "sys_src"]] = "", "none"

    # rows added by hand: traced to the CHAF strand that covers most of the trace
    hr = []
    for i in np.flatnonzero(hand):
        g = db.geometry.iloc[i]
        c = chaf[chaf.geometry.distance(g) < 0.1]
        on = c[[geo.near(x, g, MATCH_KM) > MATCH_FRAC for x in c.geometry]]
        cover = geo.near(g, on.geometry.union_all(), MATCH_KM) if len(on) else 0.0
        t = on.assign(s=[geo.near(g, x, MATCH_KM) for x in on.geometry]).sort_values("s").iloc[-1] if len(on) else None
        f = lambda k: t[k] if t is not None and t[k] is not None else ""
        hr.append({"name": db.loc[i, "name"], "length": db.loc[i, "length"], "chaf_ids": ";".join(map(str, on.F_id)),
                   "trace_on_chaf": cover, "chaf_id": f("F_id"), "chaf_name": f("F_name"), "chaf_system": f("F_system"),
                   "chaf_refs": f("refs"), "chaf_slip": f("slip_rate"), "chaf_throw": f("throw_rate"),
                   "chaf_dip": f("dip"), "chaf_dipdir": f("dipdir"), "chaf_sense": f("sense")})
        if t is None or cover <= MATCH_FRAC:
            db.loc[i, ["fid", "src"]] = f"HAND-{i:03d}", "hand row, origin not traced"
            continue
        db.loc[i, ["fid", "src", "src_ref"]] = f"CHAF-{t.F_id}", "hand row on CHAF strands", f"CHAF {t.F_name}: {t.refs}"
        db.loc[i, ["system", "sys_src"]] = SYSTEMS.get(t.F_system, t.F_system), f"CHAF {t.F_system}"
        if not db.loc[i, "kin"] and t.sense:
            k = str(t.sense).lower()
            db.loc[i, ["kin", "rake", "kin_src"]] = k, RAKE[k], f"CHAF {t.F_id}"
        rate = t.slip_rate or t.throw_rate
        if rate:
            db.loc[i, ["sr_kind", "sr_src"]] = "measured", f"hand row; CHAF {t.F_id}: {'slip' if t.slip_rate else 'throw'} rate {rate} ({t.refs})"
    hr = pd.DataFrame(hr)

    # duplicates and overlaps (none removed unless exact)
    dup, trees = [], [geo.tree(g) for g in db.geometry]
    for i in range(len(db)):
        for j in range(i + 1, len(db)):
            if db.geometry.iloc[i].distance(db.geometry.iloc[j]) > 0.05:
                continue
            a, b = (i, j) if db["length"].iloc[i] <= db["length"].iloc[j] else (j, i)
            s = geo.near(db.geometry.iloc[a], trees[b], DUP_KM)
            if s > DUP_FRAC:
                dup.append({"short": db.fid.iloc[a], "long": db.fid.iloc[b], "share_of_short": s,
                            "exact": db.geometry.iloc[a].equals(db.geometry.iloc[b]),
                            "len_short": db["length"].iloc[a], "len_long": db["length"].iloc[b]})
    dup = pd.DataFrame(dup, columns=["short", "long", "share_of_short", "exact", "len_short", "len_long"])
    drop = set(dup.loc[dup.exact, "short"])
    db["dup_of"] = [";".join(dup.loc[dup.short == f, "long"]) for f in db.fid]
    db = db[~db.fid.isin(drop)].reset_index(drop=True)

    # one trace per section of Magallanes–Fagnano
    from shapely.geometry import box
    for i in db.index[db.system == "Magallanes–Fagnano"]:
        g0 = db.geometry[i]
        g = g0.intersection(box(-180, -90, BORDER, 0) if db.fid[i].startswith("CL") else box(BORDER, -90, 0, 0))
        if g.equals(g0):
            continue
        L0 = db.loc[i, "length"]
        db.at[i, "geometry"] = g
        db.loc[i, "length"] = geo.length(g)
        db.loc[i, "note"] = "; ".join(x for x in (db.loc[i, "note"], f"cut at the border {BORDER}° (territory rule): "
                                                   f"{L0:.1f} -> {db.loc[i, 'length']:.1f} km") if x)
        chg.append((db.fid[i], "geometry", f"{L0:.1f} km", f"{db.loc[i, 'length']:.1f} km, cut at the border"))

    cols = ["fid", "gem_id", "gem_flt", "system", "sys_src", "name", "kin", "rake", "kin_src", "dip", "dip_dir",
            "vertical", "dip_txt", "dip_src", "sr", "sr_lo", "sr_hi", "sr_kind", "sr_txt", "sr_src", "z_top", "z_bot",
            "z_src", "length", "src", "src_ref", "chaf_ids", "chaf_act", "dup_of", "note", "geometry"]
    chg = pd.DataFrame(chg, columns=["fid", "field", "old", "new"])
    return db[cols], chg, dup, hr, chaf


def main():
    TAB.mkdir(exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    db, chg, dup, hr, chaf = build()
    db.to_file(OUT.with_suffix(".gpkg"), layer="faults", driver="GPKG", layer_options={"FID": "gpkg_fid"})
    db.drop(columns="geometry").to_csv(OUT.with_suffix(".csv"), index=False)
    # shapefile of GEM alone; GEM with the added faults was edited by Pablo and is rebuilt by curate.py
    shp = db.assign(vertical=db.vertical.astype(int))
    shp[shp.src == "SARA"].to_file(OUT.parent / f"faults_gem_{DATE}.shp", encoding="UTF-8")
    chg.to_csv(TAB / f"d16_changes_{DATE}.csv", index=False)
    dup.to_csv(TAB / f"d16_duplicates_{DATE}.csv", index=False)
    hr.to_csv(TAB / f"d16_hand_rows_{DATE}.csv", index=False)
    print(f"{len(db)} rows written to {OUT}.gpkg / .csv")
    print(db.sr_kind.value_counts().to_string())
    print(chg.groupby("field").size().to_string())
    print(dup.round(2).to_string(index=False))
    print(hr.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
