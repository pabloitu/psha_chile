"""CAT build, steps C1-C6: matched events, locations, depths, Mw with σ, mechanisms, overrides last.

Usage: python -m psha9.catalog.build [out_dir]
"""
import datetime
import json
import sys

import numpy as np
import pandas as pd
import yaml

from . import locate, magnitude, match
from .match import CFG, ROOT, year

# property of the overrides file -> columns also set
ALSO = {"mw": {"mw_kind": "a6", "mw_src": "a6"}, "depth": {"depth_kind": "measured", "depth_src": "a6"},
        "lon": {"loc_src": "a6"}, "lat": {"loc_src": "a6"}, "strike1": {"mech_src": "a6"}}
COL = {"exists": "a6_exists", "class_hint": "a6_class_hint"}


def overrides(d, props, flag):
    """
    Accepted rows of the overrides file for the properties `props`, applied to d (one row per event, D-CAT-17).
    The value replaces the column's, the row's sigma goes to <column>_sigma where d has it, the columns of ALSO are
    set and the flag a6_<property> added. Returns the table and the rows applied.
    """
    o = pd.read_csv(ROOT / CFG["inputs"]["overrides"], dtype=str)
    o = o[(o.status == "accepted") & o.property.isin(props) & o.event_id.isin(d.event_id)]
    d = d.copy()
    at = pd.Series(d.index, index=d.event_id)
    for r in o.itertuples():
        j, c = at[r.event_id], COL.get(r.property, r.property)
        if c not in d:
            d[c] = None
        num = pd.api.types.is_numeric_dtype(d[c])
        d.loc[j, c] = (float(r.new_value) if pd.notna(r.new_value) else np.nan) if num else r.new_value
        if c + "_sigma" in d and pd.notna(r.sigma):
            d.loc[j, c + "_sigma"] = float(r.sigma)
        for k, v in ALSO.get(r.property, {}).items():
            if k in d:
                d.loc[j, k] = v
        old = d.loc[j, flag]
        d.loc[j, flag] = f"{old};a6_{r.property}" if isinstance(old, str) and old else f"a6_{r.property}"
    return d, o


def added(o, cat):
    """
    Events that only the overrides file has (D-CAT-20): accepted rows with exists = true and an event id no source has.
    Built from their time, lon, lat, mw (with sigma) and class_hint rows; no depth.
    """
    o = o[o.status.eq("accepted")]
    ids = o.event_id[o.property.eq("exists") & o.new_value.str.lower().eq("true") & ~o.event_id.isin(cat.event_id)]
    rows = []
    for i in ids.unique():
        v = o[o.event_id == i].set_index("property")
        rows.append({"event_id": i, "time": v.new_value["time"], "lon": float(v.new_value["lon"]),
                     "lat": float(v.new_value["lat"]), "loc_src": "a6", "depth_kind": "unknown", "nonquake": "",
                     "a6_class_hint": v.new_value.get("class_hint"), "mw": float(v.new_value["mw"]),
                     "mw_sigma": float(v.sigma["mw"]), "mw_kind": "a6", "mw_src": "a6",
                     "loc_flags": "a6_added", "mw_flags": "a6_added"})
    return pd.DataFrame(rows, columns=cat.columns)


def cabello_unmatched(cat):
    """Cabello events from 1904 on (a check list only, D-CAT-02) of M >= m with no event of the catalogue within the
    window; and whether one lies within the wide window (often Cabello's local date or time)."""
    w = CFG["cabello_check"]
    e = pd.read_csv(match.table("cabello", "events"), low_memory=False, dtype={"src_id": str})
    m = pd.read_csv(match.table("cabello", "mags"), low_memory=False, dtype={"src_id": str})
    e["m"] = e.src_id.map(m[m.mag_type == "magnitude"].set_index("src_id").mag)
    e["t"] = match.tsec(e.time)
    x = e[(year(e.t) >= CFG["read"]["cabello_before"]) & (e.m >= w["m"])].reset_index(drop=True)
    c = cat[cat.lat.notna()]
    ct = match.tsec(c.time)
    args = (x.t.to_numpy(), x.lat.to_numpy(), x.lon.to_numpy(), ct, c.lat.to_numpy(), c.lon.to_numpy())
    near = lambda t, d: np.isin(np.arange(len(x)), match.near(*args, t, d)[0])
    x["wide"] = near(w["wide_t"], w["d"])
    x = x[~near(w["t"], w["d"])]
    return x[["src_id", "time", "lat", "lon", "depth", "m", "agency", "reference", "wide"]].sort_values("m", ascending=False)


def inside(d, b):
    return d.lat.between(*b["lat"]) & d.lon.between(*b["lon"])


def main(out=None):
    out = ROOT / "runs" / "catalog" / CFG["run"] if out is None else ROOT / out
    if (out / "run.yaml").exists():
        raise SystemExit(f"{out} exists; a run is never edited")
    out.mkdir(parents=True, exist_ok=True)
    ov = CFG["overrides"]

    # C1-C2
    m = match.run()
    e, L = m["events"], m["links"]
    # C3 and the location overrides (the conversions use the final depth)
    loc, dflt, R = locate.run(e, L)
    loc, o1 = overrides(loc, ov["locate"], "loc_flags")
    gone = loc.event_id[loc.a6_exists.astype(str).str.lower().eq("false")] if "a6_exists" in loc else loc.event_id[:0]
    loc = loc[~loc.event_id.isin(gone)].reset_index(drop=True)
    # C4 and the Mw overrides, last
    x = pd.DataFrame({"event_id": loc.event_id, "z": loc.depth, "yr": year(match.tsec(loc.time))})
    mg = magnitude.run(x, L[L.event_id.isin(x.event_id)])
    mw, o2 = overrides(mg["mw"], ov["magnitude"], "mw_flags")
    cat = loc.merge(mw, on="event_id", how="left")
    new = added(pd.read_csv(ROOT / CFG["inputs"]["overrides"], dtype=str), cat)
    cat = pd.concat([cat, new], ignore_index=True)
    # C6 non-earthquakes; D-CAT-06 final cut on the chosen location (Ruiz and Madariaga events are not cut)
    cat["nonquake"] = cat.nonquake.fillna("")
    rm = set(L.event_id[L.src == "rm2018"])
    cat["in_box"] = inside(cat, CFG["box"])
    # events whose origins all come from unlisted agencies have no usable location (D-CAT-08): listed apart
    noloc = cat[cat.lat.isna()]
    cut = cat[~cat.in_box & cat.lat.notna() & ~cat.event_id.isin(rm)]
    cat = cat[(cat.in_box | cat.event_id.isin(rm)) & cat.lat.notna()].copy()
    cat["in_domain_17g"] = inside(cat, CFG["domain_17g"])
    cat = cat.sort_values("time", kind="stable").reset_index(drop=True)

    files = {"catalog": cat, "links": L, "events_matched": e.drop(columns="t"), "dropped_records": m["dropped"],
             "windows": m["windows"], "merges": m["merges"], "rm_matches": m["rm_matches"], "rm_missing": m["rm_missing"],
             "outside_box": cut[["event_id", "time", "lat", "lon", "depth", "mw", "loc_src"]],
             "no_location": noloc[["event_id", "mw"]].merge(e[["event_id", "time", "lat", "lon", "sources", "mmax"]], on="event_id"),
             "removed_exists_false": pd.DataFrame({"event_id": gone}), "added_events": new, "defaults": dflt,
             "overrides_applied": pd.concat([o1, o2]), "relations": magnitude.rel_table(mg["F"]),
             "mw_offsets": mg["offsets"].round(3), "mw_reference_outliers": mg["outliers"],
             "abe_pairs": mg["abe_pairs"] if mg["abe_pairs"] is not None else pd.DataFrame(),
             "magnitudes": mg["M"], "cabello_unmatched": cabello_unmatched(cat)}
    for k, d in files.items():
        d.to_csv(out / f"{k}.csv", index=False)
    json.dump(mg["F"], open(out / "relations.json", "w"), default=float)
    run = {"date": datetime.date.today().isoformat(), "reads": {k: v for k, v in CFG["inputs"].items()},
           "priority_by_sigma": mg["priority_fit"],
           "abe_offset": mg["abe"], "settings": CFG}
    (out / "run.yaml").write_text(yaml.safe_dump(run, sort_keys=False, allow_unicode=True))
    k = cat.mw >= 4.45
    print("events", len(cat), "| Mw >= 4.5:", int(k.sum()), "in the 17g domain:", int((k & cat.in_domain_17g).sum()),
          "| outside the box:", len(cut), "| no usable location:", len(noloc), "| non-earthquakes:", int(cat.nonquake.ne("").sum()))
    print("Mw kinds (>= 4.5):", cat[k].mw_kind.value_counts().to_dict())
    return out


if __name__ == "__main__":
    print(main(sys.argv[1] if len(sys.argv) > 1 else None))
