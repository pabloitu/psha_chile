# Census of the classifier branches on a classified catalog: error regime,
# mechanism, slab-top domain, agency default depths, the pre-1930 rule and
# the units of the location errors. Reads out/classify/cat_classified.csv by
# default, or the file given; writes audit.txt, audit_events.csv next to it.

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
DD = [0.0, 10.0, 33.0, 35.0]
ZCUT = 50.0
MMIN = 5.5
PLANE = [("strike1", "dip1", "rake1"), ("strike2", "dip2", "rake2")]
SLAB = ["slab_interface", "intra_slab", "slab_deep", "forearc"]


def tag(df):
    """
    Branch labels per event, recomputed from the columns the classifier reads.

    reg: relocated / numeric (depth_error > 0) / zero / none, the four depth
    gates of the shallow-slab domain; dom: no_slab / shallow / deep by the
    sub_depth the classifier wrote; dd: agency default depth, not relocated,
    no mechanism; dz: depth minus slab top.
    """
    e = df[["lon_error", "lat_error", "depth_error"]].astype(str).apply(lambda s: s.str.strip().str.lower())
    de = pd.to_numeric(df["depth_error"], errors="coerce")
    rel = (e == "relocated").any(axis=1)
    reg = np.select([rel, de > 0, de == 0], ["relocated", "numeric", "zero"], "none")
    mech = np.zeros(len(df), bool)
    for p in PLANE:
        mech |= df[list(p)].apply(pd.to_numeric, errors="coerce").notna().all(axis=1).to_numpy()
    z = pd.to_numeric(df["depth"], errors="coerce")
    sd = pd.to_numeric(df["sub_depth"], errors="coerce")
    dom = np.select([sd.isna(), sd < ZCUT], ["no_slab", "shallow"], "deep")
    yr = pd.to_numeric(df["time_iso"].astype(str).str[:4], errors="coerce")
    return df.assign(reg=reg, mech=mech, dom=dom, dz=z - sd, year=yr,
                     dd=z.isin(DD) & ~rel & ~mech, m=pd.to_numeric(df["mag"], errors="coerce"))


def main(p=None):
    p = Path(p or OUT / "classify" / "cat_classified.csv")
    df = tag(pd.read_csv(p, dtype={"id": str}, low_memory=False))
    big = df[df["m"] >= MMIN]
    sub = df[df["class"].isin(SLAB)]
    t = ["# classifier branch census", f"{len(df)} events, {len(big)} with M >= {MMIN}", ""]

    t += ["## class by depth-error regime (all / M >= %.1f)" % MMIN,
          pd.crosstab(df["class"], df["reg"], margins=True).to_string(), "",
          pd.crosstab(big["class"], big["reg"], margins=True).to_string(), ""]

    t += ["## subduction classes by slab-top domain (all)",
          pd.crosstab(sub["class"], sub["dom"], margins=True).to_string(), ""]

    s = df[(df["class"] == "slab_interface") & (df["dom"] == "shallow")]
    t += ["## interface: decided by the mechanism cone vs by the band without a mechanism",
          pd.crosstab(s["m"] >= MMIN, s["mech"], rownames=[f"M>={MMIN}"], colnames=["mechanism"]).to_string(), ""]

    s = df[(df["class"] == "slab_deep") & (df["dom"] == "deep") & df["dz"].between(-15, 0, inclusive="left")]
    t += [f"## slab_deep above the slab top (deep domain, dz in [-15, 0)): {len(s)} events, "
          f"{int((s['m'] >= MMIN).sum())} with M >= {MMIN}",
          pd.crosstab(pd.cut(s["dz"], [-15, -10, -5, 0], right=False), s["mech"]).to_string() if len(s) else "", ""]

    s = df[df["dd"]]
    t += [f"## agency default depths {DD}, not relocated, no mechanism: {len(s)} events",
          pd.crosstab(s["depth"], s["class"], margins=True).to_string() if len(s) else "",
          f"subduction domain, slab top < {ZCUT:.0f} km, classed intra_slab or forearc: "
          f"{int((s['class'].isin(['intra_slab', 'forearc']) & (s['dom'] == 'shallow')).sum())} "
          f"({int((s['class'].isin(['intra_slab', 'forearc']) & (s['dom'] == 'shallow') & (s['m'] >= MMIN)).sum())} "
          f"with M >= {MMIN})", ""]

    s = df[(df["year"] < 1930) & (df["class"] == "slab_interface") & (df["dz"] >= 11)]
    t += [f"## pre-1930 rule, approximate (interface, before 1930, 11 km or more below the slab top): {len(s)}",
          s.loc[s["m"] >= 7, ["id", "time_iso", "m", "depth", "dz"]].to_string(index=False) if (s["m"] >= 7).any() else "none with M >= 7", ""]

    t += ["## location-error values (numeric only; the ellipse test reads lon/lat errors as degrees)"]
    for c in ("lon_error", "lat_error", "depth_error"):
        v = pd.to_numeric(df[c], errors="coerce").dropna()
        t.append(f"{c}: n {len(v)}, quantiles 5/50/95/99 % "
                 + " / ".join(f"{q:.3g}" for q in v.quantile([0.05, 0.5, 0.95, 0.99])) if len(v) else f"{c}: none")
    if "source" in df.columns:
        v = df.assign(le=pd.to_numeric(df["lon_error"], errors="coerce")).dropna(subset=["le"])
        t.append(v.groupby("source")["le"].describe()[["count", "50%", "max"]].to_string())

    cols = ["id", "time_iso", "m", "longitude", "latitude", "depth", "sub_depth", "dz", "class", "reg", "mech", "dom", "dd"]
    df.loc[df["class"].isin(SLAB + ["deep_unknown", "deep_nest"]), cols].to_csv(p.parent / "audit_events.csv", index=False)
    (p.parent / "audit.txt").write_text("\n".join(t) + "\n")
    print("\n".join(t))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
