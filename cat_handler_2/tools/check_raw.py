# Checks on the raw catalogs, before building cat_handler_2:
#   1. Potin relocation already in Cabello, and CSN events it left unrelocated
#   2. cross-catalog duplicates inside Cabello
#   3. fixed depths of M >= MREV events and free depths elsewhere (Potin, GCMT FREE, ANSS)
#   4. mechanisms of M >= MREV events since 1976 (Cabello, GCMT)
#   5. Cabello's own event-level remarks and references
# Outputs (out/raw/): report.txt, duplicates.csv, fixed_depths.csv, remarks.csv, gcmt_chile.csv

import sys
from pathlib import Path

import numpy as np
import pandas as pd

import check_depth as ck

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / "out" / "raw"
CAT = REPO / "data" / "catalogs"
MREV = 5.5
DUP_DT, DUP_KM = 10.0, 30.0
FIXED = {"USGS": [0, 10, 33, 35], "ISC": [0, 10, 33, 35], "ISC-GEM": [10, 15, 25, 35],
         "GCMT": [12, 15], "CERESIS-GEM": [33], "CSN-improved": [0, 10, 33, 35]}
BOX = (-60, -10, -82, -60)
RANK = {"GCMT": 0, "ISC-GEM": 1, "USGS": 2, "ISC": 3, "CSN-improved": 4, "CERESIS-GEM": 5}


def iso(d, sec="second"):
    s = d[sec].clip(0, 59.99).astype(float)
    return (d["year"].astype(str).str.zfill(4) + "-" + d["month"].clip(1).astype(str).str.zfill(2) + "-"
            + d["day"].clip(1).astype(str).str.zfill(2) + "T" + d["hour"].astype(str).str.zfill(2) + ":"
            + d["minute"].astype(str).str.zfill(2) + ":" + s.map(lambda v: f"{v:05.2f}"))


def gcmt(paths):
    """
    Chile-region events of GCMT ndk files, with the centroid depth flag.

    Returns
    -------
    DataFrame
        name, time_iso (PDE hypocentre time), hypocentre and centroid location,
        depth = centroid depth, dtype FREE / FIX / BDY, mag = Mw from M0,
        strike1 ... rake2.
    """
    rows = []
    for p in paths:
        L = Path(p).read_text().splitlines()
        for i in range(0, len(L) - 4, 5):
            l1, l2, l3, l4, l5 = L[i:i + 5]
            c, f, h = l3.split(), l5.split(), l1[4:].split()
            lat, lon = float(c[3]), float(c[5])
            if not (BOX[0] <= lat <= BOX[1] and BOX[2] <= lon <= BOX[3]):
                continue
            m0 = float(f[-7]) * 10 ** int(l4.split()[0])
            rows.append({"name": l2.split()[0], "time_iso": h[0].replace("/", "-") + "T" + h[1].replace(":60", ":59.9"),
                         "hlat": float(h[2]), "hlon": float(h[3]), "hdep": float(h[4]),
                         "latitude": lat, "longitude": lon, "depth": float(c[7]), "dtype": c[9],
                         "mag": round(2 / 3 * np.log10(m0) - 10.7, 2),
                         **dict(zip(["strike1", "dip1", "rake1", "strike2", "dip2", "rake2"], map(int, f[-6:])))})
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(CAT / "Integrated_Seismic_Catalog_complete.csv", sep=";", low_memory=False)
    d["time_iso"], d["mag"] = iso(d), d["magnitude"]
    p = pd.read_csv(CAT / "CHILE_SEISMICITY_RELOCATED.csv")
    p["second"] = p["seconds"]
    p["time_iso"], p["mag"] = iso(p), p["magnitude"]
    G = gcmt([CAT / "gcmt_jan76_dec20.txt", CAT / "gcmt_jan21_aug25.txt"])
    G.to_csv(OUT / "gcmt_chile.csv", index=False)
    a = pd.read_csv(CAT / "ANSS.csv")
    a["time_iso"] = a["time"].str[:23]
    t = ["# raw catalog checks", f"Cabello {len(d)}, Potin {len(p)} ({int(p['mag'].notna().sum())} with magnitude), "
         f"GCMT Chile region {len(G)}, ANSS {len(a)} (M >= {a['mag'].min()})", ""]

    # 1 relocation
    r = d[d["relocated"] == "Relocated_Potin"].reset_index(drop=True)
    q = ck.pairs(r, p).sort_values(["ia", "dt"]).drop_duplicates("ia")
    same = (q["dkm"] < 1) & (q["dz"].abs() < 0.5)
    n = d[(d["catalog"] == "CSN-improved") & (d["relocated"] != "Relocated_Potin") & (d["year"] <= 2020)].reset_index(drop=True)
    q2 = ck.pairs(n, p).sort_values(["ia", "dt"]).drop_duplicates("ia")
    used = set(q.loc[same, "ib"])
    t += ["## 1. Potin in Cabello", pd.crosstab(d["catalog"], d["relocated"].fillna("-")).to_string(),
          f"Relocated_Potin rows matched to Potin: {len(q)} of {len(r)}, identical {int(same.sum())}",
          f"CSN rows not relocated, up to 2020: {len(n)}; with a Potin counterpart {len(q2)} "
          f"(median {q2['dkm'].median():.1f} km, {q2['dt'].median():.0f} s), of which {int(q2['ib'].isin(used).sum())} "
          f"use a Potin event already taken; M >= 4: {int((n['mag'].to_numpy()[q2['ia']] >= 4).sum())}", ""]

    # 2 duplicates
    x = d[d["year"] >= 1900].reset_index(drop=True)
    q = ck.pairs(x, x)
    q = q[(q["ia"] < q["ib"]) & (q["dt"] <= DUP_DT) & (q["dkm"] <= DUP_KM)]
    ca, cb = x["catalog"].to_numpy()[q["ia"]], x["catalog"].to_numpy()[q["ib"]]
    q = q[ca != cb]
    drop = set()
    for i, j in zip(q["ia"], q["ib"]):
        if i not in drop and j not in drop:
            drop.add(j if RANK[x.at[i, "catalog"]] <= RANK[x.at[j, "catalog"]] else i)
    x["dup"] = x.index.isin(drop)
    k = ["id", "catalog", "time_iso", "latitude", "longitude", "depth", "mag", "relocated"]
    dp = pd.concat([x.loc[q["ia"], k].reset_index(drop=True).add_suffix("_a"),
                    x.loc[q["ib"], k].reset_index(drop=True).add_suffix("_b"),
                    q[["dt", "dkm", "dz", "dm"]].round(2).reset_index(drop=True)], axis=1)
    dp["m"] = dp[["mag_a", "mag_b"]].max(axis=1)
    dp.sort_values("m", ascending=False).to_csv(OUT / "duplicates.csv", index=False)
    bins = [0, 4, 4.5, 5, 5.5, 6.5, 10]
    t += [f"## 2. cross-catalog pairs within {DUP_DT:.0f} s, {DUP_KM:.0f} km, {ck.DM} units (from 1900): {len(q)}",
          pd.crosstab(pd.Series([" / ".join(sorted(v)) for v in zip(dp["catalog_a"], dp["catalog_b"])], name="pair"),
                      pd.cut(dp["m"], bins, right=False).rename("M").reset_index(drop=True)).to_string(), "",
          "events that would be removed (one per pair, lower-ranked catalog):",
          "\n".join(f"M >= {m}: {int(x.loc[x['mag'] >= m, 'dup'].sum())} of {int((x['mag'] >= m).sum())}" for m in (4.5, 5, 5.5, 6, 6.5, 7)),
          f"M >= {MREV} by period:", pd.crosstab(pd.cut(x["year"], [1900, 1964, 1982, 2000, 2010, 2030], right=False),
                                                x["dup"].where(x["mag"] >= MREV)).to_string(), ""]

    # 3 fixed depths
    s = x[(x["mag"] >= MREV) & ~x["dup"]].reset_index(drop=True)
    fx = s.apply(lambda r: r["depth"] in FIXED.get(r["catalog"], []), axis=1) | s["obs_depth"].notna()
    f = s[fx].reset_index(drop=True)
    alt = []
    for nm, c in (("potin", p), ("gcmt_free", G[G["dtype"] == "FREE"].reset_index(drop=True)), ("anss", a)):
        q = ck.pairs(f, c)
        z = f["depth"].to_numpy()[q["ia"]] + q["dz"].to_numpy()
        ok = ~np.isin(np.round(z), [0, 10, 12, 15, 33, 35])
        alt.append(pd.DataFrame({"i": q["ia"][ok], "alt": nm, "alt_depth": np.round(z[ok], 1)}))
    al = pd.concat(alt).groupby("i").agg(alt=("alt", lambda v: ",".join(sorted(set(v)))), alt_depth=("alt_depth", "median"))
    f = f.join(al)
    f[k + ["obs_depth", "alt", "alt_depth"]].sort_values("mag", ascending=False).to_csv(OUT / "fixed_depths.csv", index=False)
    per = pd.cut(f["year"], [1900, 1964, 1976, 1982, 2000, 2010, 2030], right=False)
    t += [f"## 3. M >= {MREV}, duplicates removed: {len(s)} events, {len(f)} at a fixed depth {FIXED} or assigned (obs_depth)",
          pd.crosstab(per, f["catalog"], margins=True).to_string(), "", "with a free depth elsewhere:",
          pd.crosstab(per, f["alt"].notna(), margins=True).to_string(),
          f["alt"].str.split(",").explode().value_counts().to_string(), "",
          "most frequent depths by catalog, M >= %.1f:" % MREV,
          "\n".join(f"{c}: {g['depth'].round(1).value_counts().head(6).to_dict()}" for c, g in s.groupby("catalog")), ""]

    # 4 mechanisms
    m = s[s["year"] >= 1976].reset_index(drop=True)
    has = pd.to_numeric(m["strike1"], errors="coerce").notna()
    q = ck.pairs(m, G)
    m["gcmt"] = m.index.isin(q["ia"])
    t += [f"## 4. mechanisms, M >= {MREV} since 1976 (duplicates removed): {len(m)}",
          f"in Cabello {int(has.sum())} (catalogs {m.loc[has, 'catalog'].value_counts().to_dict()}), "
          f"GCMT match {int(m['gcmt'].sum())}, GCMT only {int((~has & m['gcmt']).sum())}, none {int((~has & ~m['gcmt']).sum())}",
          f"none by catalog: {m.loc[~has & ~m['gcmt'], 'catalog'].value_counts().to_dict()}",
          f"GCMT centroid depth flags, M >= {MREV}: {G.loc[G['mag'] >= MREV, 'dtype'].value_counts().to_dict()}",
          f"ANSS.csv mechanism columns: {[c for c in a.columns if c.lower() in ('strike', 'mrr', 'np1', 'mrt')] or 'none'}", ""]

    # 5 remarks
    rm = d[d["general_remarks"].notna() | d["reference"].notna()]
    rm[k + ["general_remarks", "reference"]].to_csv(OUT / "remarks.csv", index=False)
    t += ["## 5. Cabello remarks and references", pd.crosstab(rm["general_remarks"].fillna("-"), rm["reference"].fillna("-")).to_string()]

    (OUT / "report.txt").write_text("\n".join(t) + "\n")
    print("\n".join(t))


if __name__ == "__main__":
    main()
