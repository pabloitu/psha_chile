"""X1 deeper pass on the surprises: censored conversion pairs (M9), Potin depths under the flat slab, two-plane
test without the interface band, Valdivia foreshock magnitude."""
import json

import numpy as np
import pandas as pd

import x1_dsz as Z
import x1_io as io
import x1_mag as M
import x1_stats as S

# settings
FRAC = 0.8
PROXY = ["ISC mb", "NEIC mb", "GUC ML", "GUC MD", "GUC md", "SJA MW", "SJA ML", "ISC MS", "GFZ M", "NEIC Mwr", "GFZ mb",
         "VAO mb", "MOS mb", "BJI mB", "IDC mb"]


def censor_cut(W, sc, ref):
    """Lowest native value from which at least FRAC of the events carrying it also have a GCMT Mw."""
    v = W[sc].dropna()
    has = ref.reindex(v.index).notna()
    b = np.round(v * 10) / 10
    f = has.groupby(b).mean()
    n = has.groupby(b).size()
    f = f[n >= 10]
    ok = f[f >= FRAC]
    return float(ok.index.min()) if len(ok) else np.nan, f


def m9(store, sig):
    s = store
    W, R, at = s["W"], s["R"], s["attrs"]
    rows, F9 = [], []
    curves = {}
    for sc in PROXY:
        if sc not in W:
            continue
        xc, f = censor_cut(W, sc, R.gcmt)
        curves[sc] = f
        ev = W[sc].dropna().index.intersection(R.gcmt.dropna().index)
        x, y = W.loc[ev, sc].to_numpy(), R.gcmt[ev].to_numpy()
        k = x >= (xc if np.isfinite(xc) else -9)
        if k.sum() < M.MIN_PAIRS:
            rows.append({"scale": sc, "x_cut": xc, "n_above": int(k.sum()), "note": "too few pairs above the cut"})
            continue
        r = M.fit(x[k], y[k], "linear", "CSQ", sig.get(sc, 0.25), sig.get("GCMT Mw", 0.1), eqerr=True)
        r0 = M.fit(x, y, "linear", "CSQ", sig.get(sc, 0.25), sig.get("GCMT Mw", 0.1), eqerr=True)
        e0 = M.choose_fit(M.json_fits["baseline"], sc, "CSQ η(TC) + eq. error")
        rows.append({"scale": sc, "x_cut": xc, "n_all": len(x), "n_above": int(k.sum()), "a": r["p"][0], "b": r["p"][1],
                     "se": r["se"], "b_all_pairs": r0["p"][1], "M0_form": e0["form"] if e0 else None,
                     **{f"M9({q})": r["p"][0] + r["p"][1] * q for q in (3.5, 4.0, 4.5, 5.0)},
                     **{f"M0({q})": M.predict(e0, np.array([q]), np.array([ev[0]]), at)[0][0] if e0 else np.nan
                        for q in (3.5, 4.0, 4.5, 5.0)}})
        F9.append({"scale": sc, "method": "CSQ η(TC) + eq. error", "form": "linear", "split": "none", "complete": True,
                   "n": int(k.sum()), "aic": 0, "bic": 0, "sx": sig.get(sc, 0.25), "sy": sig.get("GCMT Mw", 0.1),
                   "parts": [{"group": "all", "n": int(k.sum()), "p": list(r["p"]), "se": r["se"], "sigma": r["sigma"],
                              "xmin": float(x.min()) - 5, "xmax": float(x.max()), "res_slope_t": 0}]})
    pd.DataFrame(rows).to_csv(io.TAB / "t6_m9_censoring_cut.csv", index=False)
    other = [f for f in M.json_fits["baseline"] if f["scale"] not in {g["scale"] for g in F9}]
    return F9 + other, curves


def main():
    o = io.load("origins", dtype={"sid": str})
    labs = io.load("labels")
    lab = labs["baseline"].to_numpy()
    L = M.long_table(o, lab)
    at = M.event_attrs("baseline")
    at = at[~at.index.duplicated()]
    W = M.wide(L, L.scale.unique())
    R, off = M.refs(W)
    sig = pd.read_csv(io.TAB / "t3_sigma_per_scale.csv", index_col=0).sigma.to_dict()
    M.json_fits = json.load(open(io.CACHE / "fits.json"))
    store = {"W": W, "R": R, "attrs": at}
    F9, curves = m9(store, sig)
    MW = io.load("mw_variants")
    rm = pd.Series(dtype=float)
    b = MW[(MW["match"] == "baseline") & (MW.variant == "M0") & (MW.how == "RM18")].set_index("ev").mw
    rm = b
    m9v = M.build_mw(L, R, at, F9, sig, rm, pd.Series(dtype=float), "M0").assign(match="baseline", variant="M9")
    MW = pd.concat([MW[MW.variant != "M9"], m9v], ignore_index=True)
    MW.to_csv(io.CACHE / "mw_variants.csv.gz", index=False)
    # b against floor for M0, M2, M9
    lv = io.load("locvariants")
    c = lv[(lv["match"] == "baseline") & (lv["loc"] == "L-a")].set_index("ev")
    c = c[~c.index.duplicated()]
    out, hist = [], []
    for v in ("M0", "M2", "M6", "M9"):
        mw = MW[(MW["match"] == "baseline") & (MW.variant == v)].set_index("ev")
        d = c.join(mw[["mw", "sig"]], how="inner")
        d = d[np.isfinite(d.mw)]
        d["m"] = np.round(d.mw / S.DM) * S.DM
        k = (d.yr >= 2000) & (d.yr < 2015)
        h = d.m[k].value_counts().sort_index()
        hist.append(pd.DataFrame({"variant": v, "m": h.index, "n": h.values}))
        for fam in S.FAMILIES:
            x = d[S.family_mask(d, fam)]
            m, yr = x.m.to_numpy(), x.yr.to_numpy()
            mcs = [S.mc_maxc(m[(yr >= y0) & (yr < y1)]) for y0, y1 in S.WINDOWS]
            tab = S.ctable(mcs)
            for fl in S.FLOORS:
                bb, sb, rate, n = S.weichert(m, yr, tab, fl)
                out.append({"variant": v, "family": fam, "floor": fl, "b": bb, "sb": sb, "n": n, "table": str(tab),
                            "bpos": S.bpos(m[yr >= 1964], np.arange((yr >= 1964).sum()) * 0 + yr[yr >= 1964], fl)})
    B = pd.DataFrame(out)
    B.to_csv(io.TAB / "t6_b_floor_M9.csv", index=False)
    H = pd.concat(hist)
    plt = io.fig_setup()
    fig, ax = plt.subplots(1, 3, figsize=(18, 5.5), layout="constrained")
    for i, (sc, f) in enumerate(list(curves.items())[:8]):
        ax[0].plot(f.index, f.values, "o-", ms=3, color=io.palette.SERIES[i], label=sc)
    ax[0].axhline(FRAC, color="0.5", ls=":")
    ax[0].set_xlabel("native magnitude")
    ax[0].set_ylabel("share of events with a GCMT Mw")
    ax[0].set_title("Where are the GCMT pairs censored?", fontsize=11)
    ax[0].legend(fontsize=8)
    for i, v in enumerate(("M0", "M2", "M6", "M9")):
        h = H[H.variant == v]
        ax[1].step(h.m, h.n, where="mid", color=io.palette.SERIES[i], label=v)
    ax[1].set_yscale("log")
    ax[1].set_xlim(3.5, 6.5)
    ax[1].set_xlabel("Mw (0.1 bins), 2000–2014")
    ax[1].set_title("Do the conversions pile events into a few bins?", fontsize=11)
    ax[1].legend(fontsize=8)
    for i, v in enumerate(("M0", "M2", "M6", "M9")):
        x = B[(B.variant == v) & (B.family == "interface band")]
        ax[2].plot(x.floor, x.b, color=io.palette.SERIES[i], label=f"{v} Weichert")
        ax[2].plot(x.floor, x.bpos, ":", color=io.palette.SERIES[i])
    ax[2].set_ylim(0.6, 1.8)
    ax[2].set_xlabel("fit floor Mw")
    ax[2].set_ylabel("b, interface band (dotted b-positive)")
    ax[2].set_title("Does fitting above the censoring cut flatten b(floor)?", fontsize=11)
    ax[2].legend(fontsize=8)
    fig.suptitle("Censored GCMT pairs bend the low end of the conversions: M9 fits only above the native value where "
                 "≥ 80 % of events have GCMT", x=0.01, ha="left")
    io.savefig(fig, "t6_censoring_m9", "GCMT match share per native value, converted-Mw histograms and b(floor) for "
               "M0, M2, M6 and M9 (fit above the censoring cut)")
    potin_flat(plt)
    dsz_noband(plt)
    print("deep done")


def potin_flat(plt):
    w = io.load("loc_wide_baseline", index_col=0)
    rows = []
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.5), layout="constrained")
    for i, (lo, hi) in enumerate(((-34, -30), (-24, -20), (-30, -26))):
        k = w.potin_lat.between(lo, hi) & w.ehb1_z.notna() & (w.ehb1_unk != True) & w.potin_z.notna()  # noqa: E712
        x = w[k]
        d = x.potin_z - x.ehb1_z
        b = (x.ehb1_z // 20) * 20 + 10
        g = d.groupby(b).agg(["median", "size"])
        g = g[g["size"] >= 5]
        ax[0].plot(g.index, g["median"], "o-", color=io.palette.SERIES[i], label=f"{-hi}–{-lo}°S")
        for z, r in g.iterrows():
            rows.append({"band": f"{-hi}–{-lo}°S", "ehb_depth": z, "n": int(r["size"]), "potin_minus_ehb": r["median"]})
    ax[0].axhline(0, color="0.4", lw=0.7)
    ax[0].set_xlabel("ISC-EHB L1 depth [km] (20 km bins)")
    ax[0].set_ylabel("median Potin − ISC-EHB L1 depth [km]")
    ax[0].set_title("Does the Potin depth offset grow with depth under the flat slab?", fontsize=11)
    ax[0].legend()
    x = w[w.potin_lat.between(-33, -30) & w.potin_z.between(80, 250)]
    sl, _, _ = io.slab_at(x.potin_lon.to_numpy(), x.potin_lat.to_numpy())
    ax[1].hist(x.potin_z - sl, bins=np.arange(-40, 100, 2.5), color="#a50f15", alpha=0.7, label="Potin")
    y = w[w.ehb1_lat.between(-33, -30) & w.ehb1_z.between(80, 250)]
    sl2, _, _ = io.slab_at(y.ehb1_lon.to_numpy(), y.ehb1_lat.to_numpy())
    ax[1].hist(y.ehb1_z - sl2, bins=np.arange(-40, 100, 2.5), color="#2166ac", alpha=0.7, label="ISC-EHB L1")
    ax[1].set_xlabel("depth below the Slab2 top [km], 30–33°S, depth 80–250 km")
    ax[1].set_title("Where are intermediate-depth events relative to Slab2 at 30–33°S?", fontsize=11)
    ax[1].legend()
    fig.suptitle("Potin et al. depths under the Pampean flat slab", x=0.01, ha="left")
    io.savefig(fig, "t6_potin_flat_slab", "Potin minus ISC-EHB L1 depth against depth in three latitude bands, and "
               "depth below the Slab2 top at 30–33°S for both catalogs")
    pd.DataFrame(rows).to_csv(io.TAB / "t6_potin_flat_slab.csv", index=False)


def dsz_noband(plt):
    D = Z.datasets()
    rows = []
    for nm in ("Potin", "Potin M ≥ 3", "catalog L-a"):
        x = D[nm]
        s = x.z - x.dv
        for excl in ("none", "slab top < 50 km", "dn < 10 km"):
            for lat in np.arange(Z.LAT[1], Z.LAT[0], -1.0):
                for z0, z1 in Z.ZR:
                    k = (x.lat <= lat) & (x.lat > lat - 1) & (x.z >= z0) & (x.z < z1)
                    if excl == "slab top < 50 km":
                        k &= s >= 50
                    v = x.dn[k]
                    v = v[(v >= Z.DWIN[0]) & (v <= Z.DWIN[1])]
                    if excl == "dn < 10 km":
                        v = v[v >= 10]
                    r = {"data": nm, "excl": excl, "lat": lat - 0.5, "zr": f"{z0}–{z1}", "n": len(v)}
                    if len(v) >= Z.MIN_N:
                        r.update(Z.two_planes(v.to_numpy()))
                    rows.append(r)
    R = pd.DataFrame(rows)
    R.to_csv(io.TAB / "t6_two_plane_exclusions.csv", index=False)
    fig, ax = plt.subplots(1, 3, figsize=(11, 9), layout="constrained", sharey=True)
    for a, excl in zip(ax, ("none", "slab top < 50 km", "dn < 10 km")):
        x = R[(R.data == "Potin") & (R.excl == excl)]
        for j, zr in enumerate([f"{a_}–{b_}" for a_, b_ in Z.ZR]):
            for _, r in x[x.zr == zr].iterrows():
                col = "#f4f4f4" if r.n < Z.MIN_N else ("#e0641e" if r.get("two") is True else "#9ecae1")
                a.add_patch(plt.Rectangle((j, r.lat - 0.5), 1, 1, color=col, ec="white", lw=0.5))
                if r.n >= Z.MIN_N and r.get("two") is True:
                    a.text(j + 0.5, r.lat, f"{r.sep:.0f}", ha="center", va="center", fontsize=7)
        a.set_xlim(0, 3)
        a.set_ylim(Z.LAT[0], Z.LAT[1])
        a.set_xticks([0.5, 1.5, 2.5], [f"{a_}–{b_}" for a_, b_ in Z.ZR], fontsize=8)
        a.set_title(f"Potin, excluded: {excl}", fontsize=10)
    fig.suptitle("Do the 40–80 km two-plane detections survive without the interface?", x=0.01, ha="left")
    io.savefig(fig, "t6_two_plane_exclusions", "Two-plane test for Potin events with no exclusion, excluding cells "
               "with a slab top shallower than 50 km, and excluding events within 10 km of the slab top")


if __name__ == "__main__":
    main()
