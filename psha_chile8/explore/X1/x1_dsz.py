"""X1 tier 5: preview of A7 — two-plane test of in-slab seismicity by 1° latitude band."""
import time

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

import x1_io as io

# settings
LAT = (-40.0, -18.0)
ZR = [(40, 80), (80, 120), (120, 200)]
DWIN = (-15.0, 60.0)
MIN_N = 60
MIN_W = 0.15
MIN_SEP = 8.0
DBIC = 10.0
SECTIONS = [-20.0, -23.0, -27.0, -31.0, -33.5, -37.0]
MMIN = {"Potin": 0.0, "Potin M ≥ 3": 3.0}


def datasets():
    w = io.load("loc_wide_baseline", index_col=0)
    lv = io.load("locvariants")
    d = {}
    for nm, s, mmin in (("Potin", "potin", 0.0), ("Potin M ≥ 3", "potin", 3.0), ("ISC-EHB L1", "ehb1", 0.0),
                        ("ISC-EHB L1+L2", "ehb2", 0.0)):
        if s == "ehb2":
            k = (w.ehb1_lat.notna() | w.ehb2_lat.notna())
            x = pd.DataFrame({"lat": w.ehb1_lat.fillna(w.ehb2_lat), "lon": w.ehb1_lon.fillna(w.ehb2_lon),
                              "z": w.ehb1_z.fillna(w.ehb2_z), "md": w.md})[k]
        else:
            k = w[f"{s}_lat"].notna() & (w[f"{s}_unk"] != True)  # noqa: E712
            if s == "potin":
                k &= (w.md.fillna(0) >= mmin)
            x = pd.DataFrame({"lat": w[f"{s}_lat"], "lon": w[f"{s}_lon"], "z": w[f"{s}_z"], "md": w.md})[k]
        d[nm] = x
    for loc in ("L-a", "L-b 44°S"):
        c = lv[(lv["match"] == "baseline") & (lv["loc"] == loc) & ~lv.unk.astype(bool)]
        d[f"catalog {loc}"] = pd.DataFrame({"lat": c.lat, "lon": c.lon, "z": c.z, "md": c.md}).set_index(c.ev)
    for nm, x in d.items():
        s, th, dip = io.slab_at(x.lon.to_numpy(), x.lat.to_numpy())
        x["dv"] = x.z.to_numpy() - s
        x["dn"] = x.dv * np.cos(np.radians(np.nan_to_num(dip)))
        x["thk"] = th
        d[nm] = x[(x.lat >= LAT[0]) & (x.lat <= LAT[1]) & np.isfinite(x.dv)]
    return d


def two_planes(v):
    """BIC of one against two Gaussian components; separation and weights of the two-component fit."""
    v = np.asarray(v, float).reshape(-1, 1)
    g1 = GaussianMixture(1, random_state=0).fit(v)
    g2 = GaussianMixture(2, random_state=0, n_init=5).fit(v)
    mu = g2.means_.ravel()
    o = np.argsort(mu)
    sd = np.sqrt(g2.covariances_.ravel())[o]
    w = g2.weights_[o]
    dbic = g1.bic(v) - g2.bic(v)
    two = (dbic > DBIC) & (w.min() >= MIN_W) & (mu[o][1] - mu[o][0] >= MIN_SEP) & (mu[o][1] - mu[o][0] > sd.max())
    return {"dbic": dbic, "mu1": mu[o][0], "mu2": mu[o][1], "sd1": sd[0], "sd2": sd[1], "w1": w[0], "w2": w[1],
            "sep": mu[o][1] - mu[o][0], "two": bool(two)}


def run():
    T0 = time.time()
    D = datasets()
    rows = []
    for nm, x in D.items():
        for dist in ("dn", "dv"):
            for shift in (-5.0, 0.0, 5.0):
                for lat in np.arange(LAT[1], LAT[0], -1.0):
                    for z0, z1 in ZR:
                        k = (x.lat <= lat) & (x.lat > lat - 1) & (x.z >= z0) & (x.z < z1)
                        v = x[dist][k] - shift
                        v = v[(v >= DWIN[0]) & (v <= DWIN[1])]
                        r = {"data": nm, "dist": dist, "slab_shift": shift, "lat": lat - 0.5, "zr": f"{z0}–{z1}",
                             "n": len(v)}
                        if len(v) >= MIN_N:
                            r.update(two_planes(v.to_numpy()))
                        rows.append(r)
    R = pd.DataFrame(rows)
    R.to_csv(io.TAB / "t5_two_plane_tests.csv", index=False)
    print("tests", round(time.time() - T0), flush=True)
    plt = io.fig_setup()
    fig_hist(plt, D)
    fig_strip(plt, R)
    fig_sections(plt, D["Potin"])
    print("tier 5 done", round(time.time() - T0), flush=True)


def fig_hist(plt, D):
    x = D["Potin"]
    lats = np.arange(LAT[1], LAT[0], -1.0)
    fig, ax = plt.subplots(len(ZR), 1, figsize=(16, 10), layout="constrained", sharex=True)
    for a, (z0, z1) in zip(ax, ZR):
        for i, lat in enumerate(lats):
            k = (x.lat <= lat) & (x.lat > lat - 1) & (x.z >= z0) & (x.z < z1)
            v = x.dn[k]
            v = v[(v >= DWIN[0]) & (v <= DWIN[1])]
            if len(v) < 20:
                continue
            h, e = np.histogram(v, bins=np.arange(DWIN[0], DWIN[1] + 2.5, 2.5))
            h = h / h.max() * 0.9
            a.fill_between(e[:-1] + 1.25, i, i + h, step="mid", color="#4393c3", alpha=0.8, lw=0)
            a.text(DWIN[1] + 1, i + 0.2, f"{len(v)}", fontsize=7, color="0.4")
        a.set_yticks(np.arange(len(lats)) + 0.4, [f"{-l + 0.5:.1f}°S" for l in lats], fontsize=7)
        a.set_title(f"depth {z0}–{z1} km", fontsize=11)
        a.axvline(0, color="0.3", lw=0.7)
    ax[-1].set_xlabel("distance below the Slab2 top, normal to the slab [km]")
    fig.suptitle("Is in-slab seismicity in one or two layers? Potin et al., per 1° band (normalised histograms, "
                 "counts at right)", x=0.01, ha="left")
    io.savefig(fig, "t5_dslab_histograms", "Histograms of the slab-normal distance below the Slab2 top per 1° band "
               "and depth range, Potin events")


def fig_strip(plt, R):
    R = R[(R.dist == "dn") & (R.slab_shift == 0.0)]
    data = ["Potin", "Potin M ≥ 3", "ISC-EHB L1", "ISC-EHB L1+L2", "catalog L-a", "catalog L-b 44°S"]
    fig, ax = plt.subplots(1, len(data), figsize=(3.2 * len(data), 9), layout="constrained", sharey=True)
    for a, nm in zip(ax, data):
        x = R[R.data == nm]
        for j, zr in enumerate([f"{a_}–{b_}" for a_, b_ in ZR]):
            y = x[x.zr == zr]
            for _, r in y.iterrows():
                if r.n < MIN_N:
                    col, txt = "#f4f4f4", ""
                elif r.two:
                    col, txt = "#e0641e", f"{r.sep:.0f}"
                else:
                    col, txt = "#9ecae1", ""
                a.add_patch(plt.Rectangle((j, r.lat - 0.5), 1, 1, color=col, ec="white", lw=0.5))
                if txt:
                    a.text(j + 0.5, r.lat, txt, ha="center", va="center", fontsize=7)
        a.set_xlim(0, len(ZR))
        a.set_ylim(LAT[0], LAT[1])
        a.set_xticks(np.arange(len(ZR)) + 0.5, [f"{a_}–{b_}" for a_, b_ in ZR], fontsize=8)
        a.set_title(nm, fontsize=10)
        a.set_xlabel("depth range [km]")
    ax[0].set_ylabel("latitude [°]")
    fig.suptitle("Where does a two-component mixture win? Orange: two planes (number = separation in km), blue: one, "
                 "grey: < 60 events", x=0.01, ha="left")
    io.savefig(fig, "t5_two_plane_strip", "Latitude × depth range: bands where a two-component Gaussian mixture of "
               "the distance below the slab top beats one component (BIC), per dataset")


def fig_sections(plt, x):
    import shapely
    from pituplots.io import read_slab2
    from pituplots.sections import add_slab, profiles_from_line, project
    tr, _, _ = io.shapes()
    line = shapely.union_all(tr)
    top = read_slab2(io.REPO / "data/slab_2.0/sam_slab2_dep_02.23.18.xyz")
    thk = read_slab2(io.REPO / "data/slab_2.0/sam_slab2_thk_02.23.18.xyz")
    prof = profiles_from_line(line, SECTIONS, width=100, side=(-60, -30), length=(-60, 400))
    fig, ax = plt.subplots(len(SECTIONS), 1, figsize=(13, 3.5 * len(SECTIONS)), layout="constrained")
    for a, p, lat in zip(ax, prof, SECTIONS):
        u, v = project(x.lon.to_numpy(), x.lat.to_numpy(), p)
        k = (np.abs(v) <= 50) & (u >= -60) & (u <= 400)
        sc = a.scatter(u[k], x.z.to_numpy()[k], c=np.clip(x.dn.to_numpy()[k], -20, 60), cmap="turbo", s=2, lw=0,
                       vmin=-20, vmax=60)
        add_slab(a, p, top, thk)
        a.set_xlim(-60, 400)
        a.set_ylim(250, -5)
        a.set_aspect(0.5)
        a.set_title(f"{-lat:.1f}°S, ±50 km ({k.sum()} Potin events)", fontsize=11)
        a.set_ylabel("depth [km]")
    plt.colorbar(sc, ax=ax, shrink=0.3, label="distance below slab top [km]")
    ax[-1].set_xlabel("distance from the trench [km]")
    fig.suptitle("Where do events sit relative to the Slab2 top? Potin et al., coloured by slab-normal distance",
                 x=0.01, ha="left")
    io.savefig(fig, "t5_sections_dslab", "Trench-normal sections at six latitudes, Potin events coloured by distance "
               "below the Slab2 top")


if __name__ == "__main__":
    run()
