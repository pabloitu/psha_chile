"""C14 step 1: the Riedel-Hornig catalogue summarized, matched to the frozen catalogue for 2017-2021 and used as a
depth benchmark of Potin / CSN web, GCCEL, ISC-EHB L1 / L2 and ISC. Tables in tables/, figures in figs/."""
import numpy as np
import pandas as pd

import depth as D

# settings
TAB, FIG = D.HERE / "tables", D.HERE / "figs"
T0, T1 = "2017-01-01", "2022-01-01"
Z_BINS, Z_LAB = [70.0, 150.0], ["0–70 km", "70–150 km", "150–300 km"]
X_BINS = [100.0, 200.0, 300.0, 400.0]
X_LAB = ["0–100 km", "100–200 km", "200–300 km", "300–400 km", "> 400 km"]
LAT_BINS = np.arange(-44.0, -16.0, 2.0)
REFS = {"Potin / CSN web": ("potin", "csn"), "GCCEL": ("gccel",), "ISC-EHB L1": ("ehb1",), "ISC-EHB L2": ("ehb2",),
        "ISC": ("isc",)}


def summary(r):
    rows = [("events", len(r)), ("first day", r.Date.min()), ("last day", r.Date.max()),
            ("events with Ml", int(r.Ml.notna().sum())), ("Ml range", f"{r.Ml.min():.2f}–{r.Ml.max():.2f}"),
            ("Ml ≥ 2.5 (their Mc)", int((r.Ml >= 2.5).sum())), ("Ml ≥ 3", int((r.Ml >= 3).sum())), ("Ml ≥ 4", int((r.Ml >= 4).sum())),
            ("latitude", f"{r.Lat.min():.2f} to {r.Lat.max():.2f}"), ("depth", f"{r.z.min():.1f}–{r.z.max():.1f} km")]
    for q in (5, 25, 50, 75, 95):
        rows.append((f"depth error, {q} % (km)", round(float(np.percentile(r.sig, q)), 2)))
    rows.append(("depth error ≤ 5 km", int((r.sig <= 5).sum())))
    rows.append(("depth error ≤ 5 km, Ml ≥ 2.5", int(((r.sig <= 5) & (r.Ml >= 2.5)).sum())))
    for k, v in r.Type.value_counts().items():
        rows.append((f"type {k}", int(v)))
    z = pd.cut(r.z, [0, 70, 150, 300, 400], right=False)
    for k, g in r.groupby(z, observed=True):
        rows.append((f"median depth error, depth {k}", round(float(g.sig.median()), 2)))
    e = D.east_km(r.Lon, r.Lat) > 0
    rows.append(("median depth error, east of the Chile border", round(float(r.sig[e].median()), 2)))
    rows.append(("median depth error, in Chile", round(float(r.sig[~e].median()), 2)))
    return pd.DataFrame(rows, columns=["quantity", "value"])


def source_depths(ids):
    """Measured depths of the source records linked to the events ids: one column per benchmark source."""
    l = pd.read_csv(D.LINKS, usecols=["event_id", "src", "src_id", "origin_id"], low_memory=False)
    l = l[l.event_id.isin(ids) & l.src.isin(["potin", "csn", "gccel", "iscehb", "isc"])]
    out = pd.DataFrame(index=pd.Index(ids, name="event_id"))
    for s, f in (("potin", "potin_2026-11-10"), ("csn", "csn_2026-11-10"), ("gccel", "gccel_2026-11-11"),
                 ("iscehb", "iscehb_2026-11-10"), ("isc", "isc_2026-11-10")):
        e = pd.read_csv(D.SRC / f"{f}_events.csv", low_memory=False, dtype={"src_id": str, "origin_id": str})
        x = l[l.src == s].astype({"src_id": str, "origin_id": str}).merge(e, on=["src_id", "origin_id"])
        x = x[x.depth.notna() & (x.depth_fixed != True)]  # noqa: E712
        if s == "isc":
            x = x[x.agency == "ISC"]
        if s == "iscehb":
            for q in ("L1", "L2"):
                out["ehb" + q[1]] = x[x.depth_quality == q].groupby("event_id").depth.first()
            continue
        out[s] = x.groupby("event_id").depth.first()
    return out


def stats(x, key):
    q = x[key].dropna()
    if len(q) < 5:
        return {"n": len(q), "median": np.nan, "nmad": np.nan, "p16": np.nan, "p84": np.nan}
    return {"n": len(q), "median": q.median(), "nmad": 1.4826 * (q - q.median()).abs().median(),
            "p16": q.quantile(0.16), "p84": q.quantile(0.84)}


def benchmark(m):
    """Depth differences (source − Riedel-Hornig, km) by depth, distance from the trench, the flat slab and the
    side of the Chile border."""
    m = m.copy()
    m["zb"] = np.array(Z_LAB)[np.digitize(m.r_z, Z_BINS)]
    m["xb"] = np.array(X_LAB)[np.digitize(m.x_trench, X_BINS)]
    m["flat"] = (m.r_lat >= D.FLAT[0]) & (m.r_lat <= D.FLAT[1])
    m["side"] = np.where(m.east > 0, "east of the border", "in Chile")
    rows = []
    for name, keys in REFS.items():
        m["dz"] = m[list(keys)].bfill(axis=1).iloc[:, 0] - m.r_z
        groups = [("all", "all", m)]
        groups += [("depth", k, g) for k, g in m.groupby("zb")]
        groups += [("trench distance", k, g) for k, g in m.groupby("xb")]
        groups += [("flat slab 27–33° S, depth", k, g) for k, g in m[m.flat].groupby("zb")]
        groups += [("outside the flat slab, depth", k, g) for k, g in m[~m.flat].groupby("zb")]
        groups += [("side of the border, depth ≥ 70 km", k, g) for k, g in m[m.r_z >= 70].groupby("side")]
        groups += [("flat slab, side of the border, depth ≥ 70 km", k, g) for k, g in m[m.flat & (m.r_z >= 70)].groupby("side")]
        groups += [("north of 27° S, side of the border, depth ≥ 70 km", k, g)
                   for k, g in m[(m.r_lat > D.FLAT[1]) & (m.r_z >= 70)].groupby("side")]
        for split, k, g in groups:
            rows.append({"source": name, "split": split, "group": k, **stats(g, "dz")})
    return pd.DataFrame(rows)


def by_lat(m):
    rows = []
    for name, keys in REFS.items():
        dz = m[list(keys)].bfill(axis=1).iloc[:, 0] - m.r_z
        for lo in LAT_BINS:
            for side in ("in Chile", "east of the border"):
                k = (m.r_lat >= lo) & (m.r_lat < lo + 2) & (m.r_z >= 70) & ((m.east > 0) == (side != "in Chile"))
                rows.append({"source": name, "lat": f"{-lo - 2:.0f}–{-lo:.0f}° S", "side": side,
                             **stats(pd.DataFrame({"dz": dz[k]}), "dz")})
    return pd.DataFrame(rows)


def rates(c, m):
    """Match rate of the catalogue events of 2017-2021 inside the area of Riedel-Hornig, by depth and latitude."""
    k = (c.t >= D.C.tsec([T0])[0]) & (c.t < D.C.tsec([T1])[0]) & (c.lat <= -18) & (c.lat >= -43) & c.mw.notna()
    x = c[k].assign(matched=c.event_id[k].isin(m.event_id))
    x["mb"] = pd.cut(x.mw, [0, 3.5, 4.5, 10], right=False, labels=["Mw < 3.5", "Mw 3.5–4.4", "Mw ≥ 4.5"])
    x["zb"] = np.where(x.depth_kind == "measured", np.array(Z_LAB + ["> 300 km"])[np.digitize(x.depth, Z_BINS + [300.0])], "no measured depth")
    x["lb"] = pd.cut(x.lat, np.r_[LAT_BINS, -16.0], right=False)
    rows = []
    for col in ("mb", "zb", "lb"):
        for k, g in x.groupby(col, observed=True):
            rows.append({"by": {"mb": "magnitude", "zb": "depth", "lb": "latitude"}[col], "group": str(k), "events": len(g),
                         "matched": int(g.matched.sum()), "rate": round(g.matched.mean(), 3)})
    return pd.DataFrame(rows)


def locations(m):
    """Epicentre and depth of the catalogue and of Riedel-Hornig against GCCEL, on events GCCEL has."""
    x = m[m.gccel.notna()].copy()
    rows = []
    for name, la, lo, z in (("catalogue", "lat", "lon", "depth"), ("Riedel-Hornig", "r_lat", "r_lon", "r_z")):
        e = D.hav(x[la], x[lo], x.g_lat, x.g_lon)
        rows.append({"location": name, "n": len(x), "epicentre to GCCEL, median km": np.median(e) if len(x) else np.nan,
                     "depth − GCCEL, median km": np.median(x[z] - x.gccel) if len(x) else np.nan,
                     "depth − GCCEL, nmad km": 1.4826 * np.median(np.abs((x[z] - x.gccel) - np.median(x[z] - x.gccel))) if len(x) else np.nan})
    return pd.DataFrame(rows)


def fig_bench(m):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import palette
    palette.apply()
    fig, axs = plt.subplots(2, 2, figsize=(13, 9.5), layout="constrained")
    cols = dict(zip(REFS, palette.SERIES))
    for ax, (title, sel) in zip(axs.flat, (("Flat slab, 27–33° S", m.flat), ("Outside the flat slab", ~m.flat))):
        for name, keys in REFS.items():
            dz = m[list(keys)].bfill(axis=1).iloc[:, 0] - m.r_z
            k = sel & dz.notna()
            if k.sum() < 20:
                continue
            ax.scatter(m.r_z[k], dz[k], s=4, color=cols[name], alpha=0.25, lw=0, rasterized=True)
            zb = np.arange(0, 301, 20)
            med = [np.median(dz[k & (m.r_z >= a) & (m.r_z < a + 20)]) if (k & (m.r_z >= a) & (m.r_z < a + 20)).sum() >= 10 else np.nan for a in zb]
            ax.plot(zb + 10, med, color=cols[name], lw=2, label=f"{name} ({k.sum():,})")
        ax.axhline(0, color="0.3", lw=0.8)
        ax.set(xlim=(0, 300), ylim=(-80, 60), xlabel="Riedel-Hornig depth [km]", ylabel="depth − Riedel-Hornig [km]", title=title)
        ax.legend(loc="lower left", fontsize=9)
    for ax, keys, name in zip(axs[1], (("potin", "csn"), ("ehb1", "isc")), ("Potin / CSN web", "ISC-EHB L1, ISC")):
        dz = m[list(keys)].bfill(axis=1).iloc[:, 0] - m.r_z
        k = dz.notna() & (m.r_z >= 70)
        sc = ax.scatter(m.east[k], dz[k], c=m.r_lat[k], s=5, cmap="viridis", alpha=0.5, lw=0, rasterized=True)
        xb = np.arange(-200, 301, 25)
        for lab, sel, ls in (("north of 27° S", m.r_lat > D.FLAT[1], "--"), ("27–33° S", m.flat, "-")):
            med = [np.median(dz[k & sel & (m.east >= a) & (m.east < a + 25)]) if (k & sel & (m.east >= a) & (m.east < a + 25)).sum() >= 10 else np.nan for a in xb]
            ax.plot(xb + 12.5, med, color="k", ls=ls, lw=1.8, label=f"median, {lab}")
        ax.axvline(0, color="0.4", lw=0.8, ls=":")
        ax.axhline(0, color="0.3", lw=0.8)
        ax.set(xlim=(-200, 300), ylim=(-80, 60), xlabel="distance east of the Chile border [km]", ylabel="depth − Riedel-Hornig [km]",
               title=f"{name}, Riedel-Hornig depth ≥ 70 km")
        ax.legend(loc="lower left", fontsize=9)
        fig.colorbar(sc, ax=ax, label="latitude [°]", shrink=0.8)
    fig.suptitle("Depths against Riedel-Hornig et al. (2026), matched events 2017–2021", x=0.01, ha="left")
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "bench_depths.png", dpi=150)
    plt.close(fig)


def main():
    TAB.mkdir(exist_ok=True)
    r = D.riedel()
    summary(r).to_csv(TAB / "rh_summary.csv", index=False)
    c = D.catalog()
    k = (c.t >= D.C.tsec([T0])[0] - 60) & (c.t < D.C.tsec([T1])[0] + 60)
    x = c[k].reset_index(drop=True)
    ia, ib = D.match(x.t.to_numpy(), x.lat.to_numpy(), x.lon.to_numpy(), r.t.to_numpy(), r.Lat.to_numpy(), r.Lon.to_numpy())
    m = x.iloc[ia][["event_id", "time", "lon", "lat", "mw", "depth", "depth_sigma", "depth_src", "depth_kind", "loc_src"]].reset_index(drop=True)
    q = r.iloc[ib].reset_index(drop=True)
    m[["rh_id", "r_lat", "r_lon", "r_z", "r_sig", "r_ml", "r_type"]] = q[["id", "Lat", "Lon", "z", "sig", "Ml", "Type"]].to_numpy()
    m = m.astype({"r_lat": float, "r_lon": float, "r_z": float, "r_sig": float, "r_ml": float})
    m["dt"], m["dd"] = q.t.to_numpy() - x.t.to_numpy()[ia], D.hav(m.lat, m.lon, m.r_lat, m.r_lon)
    m = m.join(source_depths(m.event_id), on="event_id")
    g = pd.read_csv(D.SRC / "gccel_2026-11-11_events.csv")
    l = pd.read_csv(D.LINKS, usecols=["event_id", "src", "origin_id"], low_memory=False)
    l = l[l.src == "gccel"].merge(g[["origin_id", "lat", "lon"]], on="origin_id").groupby("event_id")[["lat", "lon"]].first()
    m = m.join(l.rename(columns={"lat": "g_lat", "lon": "g_lon"}), on="event_id")
    m["x_trench"], _ = D.C.trench_side(m.r_lon, m.r_lat, D.C.TRENCH)
    m["east"] = D.east_km(m.r_lon, m.r_lat)
    m["top"] = D.slab_at(m.r_lon, m.r_lat)[0]
    m["flat"] = (m.r_lat >= D.FLAT[0]) & (m.r_lat <= D.FLAT[1])
    m.to_csv(TAB / "rh_matched.csv", index=False)
    rates(c, m).to_csv(TAB / "rh_match_rates.csv", index=False)
    benchmark(m).round(2).to_csv(TAB / "rh_benchmark.csv", index=False)
    by_lat(m).round(2).to_csv(TAB / "rh_benchmark_lat.csv", index=False)
    locations(m).round(2).to_csv(TAB / "rh_locations_gccel.csv", index=False)
    fig_bench(m)


if __name__ == "__main__":
    main()
