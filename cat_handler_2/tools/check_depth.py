# Depth and relocation check of the integrated catalog, before any fix:
#   1. agency default depths per source, period and magnitude
#   2. integrated vs Potin: is the integrated catalog already relocated with Potin?
#   3. default-depth events: alternative depths in the source catalogs and Potin
# Outputs (out/depth/): report.txt, potin_pairs.csv, default_alternatives.csv

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / "out" / "depth"
DD = [0.0, 10.0, 33.0, 35.0]
SUS = DD + [5.0, 12.0, 15.0]
DT, DKM, DM = 60.0, 100.0, 0.8
YRS = [1500, 1964, 1982, 2000, 2010, 2030]


def epoch(s):
    t = pd.to_datetime(s, utc=True, errors="coerce")
    return np.where(t.notna(), t.astype("int64", copy=False) / 1e9, np.nan) if len(t) else np.array([])


def hav(lo1, la1, lo2, la2):
    p = np.pi / 180
    a = np.sin((la2 - la1) * p / 2) ** 2 + np.cos(la1 * p) * np.cos(la2 * p) * np.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def pairs(a, b):
    """
    Every pair (event of a, event of b) within DT seconds, DKM km and DM magnitude units.

    Returns
    -------
    DataFrame
        ia, ib (positional), dt s, dkm, dz km (b minus a), dm.
    """
    ta, tb = epoch(a["time_iso"]), epoch(b["time_iso"])
    o = np.argsort(np.where(np.isfinite(tb), tb, np.inf))
    ts = tb[o]
    lo = np.searchsorted(ts, ta - DT, "left")
    hi = np.searchsorted(ts, ta + DT, "right")
    hi = np.where(np.isfinite(ta), hi, lo)
    n = np.maximum(hi - lo, 0)
    ia = np.repeat(np.arange(len(a)), n)
    ib = o[np.concatenate([np.arange(l, l + k) for l, k in zip(lo, n)])] if n.sum() else np.array([], int)
    f = lambda d, c: pd.to_numeric(d[c], errors="coerce").to_numpy(float)
    la, lb = (f(a, "longitude"), f(a, "latitude"), f(a, "depth"), f(a, "mag")), \
             (f(b, "longitude"), f(b, "latitude"), f(b, "depth"), f(b, "mag"))
    p = pd.DataFrame({"ia": ia, "ib": ib, "dt": np.abs(tb[ib] - ta[ia]),
                      "dkm": hav(la[0][ia], la[1][ia], lb[0][ib], lb[1][ib]),
                      "dz": lb[2][ib] - la[2][ia], "dm": np.abs(lb[3][ib] - la[3][ia])})
    return p[(p["dkm"] <= DKM) & ~(p["dm"] > DM)].reset_index(drop=True)


def main():
    sys.path.insert(0, str(REPO))
    from cat_no_mech_handler import paths as P
    OUT.mkdir(parents=True, exist_ok=True)

    a = pd.read_csv(P.cat_integrated, dtype={"id": str}, low_memory=False)
    a["z"] = pd.to_numeric(a["depth"], errors="coerce")
    a["m"] = pd.to_numeric(a["mag"], errors="coerce")
    a["yr"] = pd.to_numeric(a["time_iso"].astype(str).str[:4], errors="coerce")
    a["dd"] = a["z"].isin(DD)
    a["per"] = pd.cut(a["yr"], YRS, right=False)
    t = ["# depth and relocation check of the integrated catalog", f"{P.cat_integrated}: {len(a)} events", ""]

    if Path(P.rawcat_integrated).exists():
        cols = pd.read_csv(P.rawcat_integrated, nrows=0).columns.tolist()
        t += ["## columns of the raw integrated catalog", ", ".join(cols), ""]

    b = a[a["m"] >= 5.5]
    t += ["## 1. agency default depths", "share of events at 0 / 10 / 33 / 35 km by source (all, M >= 5.5):",
          pd.DataFrame({"n": a.groupby("source").size(), "dd": a.groupby("source")["dd"].sum(),
                        "n55": b.groupby("source").size(), "dd55": b.groupby("source")["dd"].sum()}
                       ).fillna(0).astype(int).sort_values("n", ascending=False).to_string(), "",
          "default depth by value and period, M >= 5.5:",
          pd.crosstab(b.loc[b["dd"], "per"], b.loc[b["dd"], "z"], margins=True).to_string(), "",
          "most frequent depths overall (a spike not in the list is another default):",
          a["z"].value_counts().head(12).to_string(), ""]

    pt = pd.read_csv(P.cat_potin, dtype={"id": str}, low_memory=False)
    py = pd.to_numeric(pt["time_iso"].astype(str).str[:4], errors="coerce")
    p = pairs(a, pt).sort_values(["ia", "dt", "dkm"]).drop_duplicates("ia")
    p["source"] = a["source"].to_numpy()[p["ia"]]
    p["same"] = (p["dkm"] < 1.0) & (p["dz"].abs() < 0.5)
    p.assign(id=a["id"].to_numpy()[p["ia"]], potin_id=pt["id"].to_numpy()[p["ib"]],
             mag=a["m"].to_numpy()[p["ia"]], depth=a["z"].to_numpy()[p["ia"]]
             ).drop(columns=["ia", "ib"]).to_csv(OUT / "potin_pairs.csv", index=False)
    g = p.groupby("source")
    win = a["yr"].between(py.min(), py.max())
    t += ["## 2. integrated vs Potin (nearest in time within 60 s, 100 km, 0.8 units)",
          f"Potin: {len(pt)} events, {py.min():.0f}-{py.max():.0f}; integrated events in that window: {int(win.sum())}",
          pd.DataFrame({"n_window": a[win].groupby("source").size(), "matched": g.size(),
                        "identical": g["same"].sum(), "med_dkm": g["dkm"].median().round(2),
                        "med_abs_dz": g["dz"].apply(lambda s: s.abs().median()).round(2),
                        "over_20km": g["dkm"].apply(lambda s: int((s > 20).sum()))}
                       ).fillna(0).sort_values("n_window", ascending=False).to_string(),
          "identical = epicentre within 1 km and depth within 0.5 km: the integrated location already is Potin's",
          f"Potin events matched by more than one integrated event: {int(p['ib'].duplicated().sum())}", ""]

    alt = []
    d = a[a["dd"]].reset_index()
    cands = [("potin", pt)]
    if Path(P.cat_full).exists():
        cf = pd.read_csv(P.cat_full, dtype={"id": str}, low_memory=False)
        cands += [(s, cf[cf["source"] == s]) for s in cf["source"].dropna().unique()]
    for s, c in cands:
        q = pairs(d, c.reset_index(drop=True))
        alt.append(pd.DataFrame({"id": d["id"].to_numpy()[q["ia"]], "mag": d["m"].to_numpy()[q["ia"]],
                                 "yr": d["yr"].to_numpy()[q["ia"]], "depth": d["z"].to_numpy()[q["ia"]],
                                 "src": d["source"].to_numpy()[q["ia"]], "alt": s,
                                 "alt_id": c["id"].to_numpy()[q["ib"]], "alt_depth": d["z"].to_numpy()[q["ia"]] + q["dz"].to_numpy(),
                                 "dt": q["dt"].round(1).to_numpy(), "dkm": q["dkm"].round(1).to_numpy()}))
    al = pd.concat(alt, ignore_index=True)
    al["free"] = al["alt_depth"].notna() & ~al["alt_depth"].round(1).isin(SUS)
    al.sort_values(["mag", "id"], ascending=[False, True]).to_csv(OUT / "default_alternatives.csv", index=False)
    ok = al[al["free"]].groupby("id")["alt"].agg(lambda s: ",".join(sorted(set(s))))
    d["has_free"] = d["id"].isin(ok.index)
    d["mb"] = pd.cut(d["m"], [0, 4.5, 5.5, 6.5, 10], right=False)
    t += ["## 3. default-depth events: another catalog gives a depth that is not a default",
          f"(alternatives from potin and cat_full sources; depths {SUS} count as fixed)",
          pd.crosstab([d["per"], d["mb"]], d["has_free"], margins=True).to_string(), "",
          "which catalog supplies the free depth (events):",
          al[al["free"]].drop_duplicates(["id", "alt"])["alt"].value_counts().to_string(), ""]

    (OUT / "report.txt").write_text("\n".join(t) + "\n")
    print("\n".join(t))


if __name__ == "__main__":
    main()
