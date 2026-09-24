# In-slab smoothed seismicity by per-class superposition: each class is fit
# on its own complete declustered events, smoothed on the slab domain, and
# given its own truncated GR; the total grid is the per-bin sum.
# Outputs: ssm/grid_{class}.csv, ssm/grid_total.csv, ssm/classes.csv,
#          ssm/b_stability.csv, ssm/kernel_cv.csv (KERNEL_CV), figures/s02_*.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cat, cfg, gr, smooth
from intraslab import config


def domain(c):
    """Grid cells inside BBOX with a slab node nearby, optionally masked by slab-top depth."""
    g = pd.read_csv(c.GRID_CSV)[["lon", "lat"]]
    lo, hi, la, ha = c.BBOX
    g = g[g["lon"].between(lo, hi) & g["lat"].between(la, ha)].reset_index(drop=True)
    g["slab_km"], dist = smooth.slab_top(g["lon"].to_numpy(), g["lat"].to_numpy(), c.SLAB_XYZ)
    keep = dist <= c.MAX_SLAB_DIST_KM
    print(f"grid: {len(g)} cells in bbox, {int((~keep).sum())} without slab within "
          f"{c.MAX_SLAB_DIST_KM} km")
    if c.MASK_ZTOP is not None:
        m = keep & (g["slab_km"] < c.MASK_ZTOP)
        print(f"mask: {int(m.sum())} cells with slab top < {c.MASK_ZTOP} km removed")
        keep &= ~m
    return g[keep].reset_index(drop=True)


def fit(k, s, c, te, floor=None, nboot=0, b=None):
    floor = c.MMIN_FIT_BY_CLASS.get(k, c.MMIN_FIT) if floor is None else floor
    steps = c.COMPLETENESS[k]
    comp = s[gr.complete(s, steps)]
    w = gr.weichert(comp["mag"], steps, te, max(floor, min(x[0] for x in steps)), c.DM, nboot, b=b)
    w["comp"] = comp
    return w


def mmax_of(k, s, c):
    if k in c.MMAX_OVERRIDE:
        return float(c.MMAX_OVERRIDE[k])
    m = float(s["mag"].max()) + c.MMAX_PAD
    if m > c.MMAX_SANITY:
        top = ", ".join(f"M{r.mag:.1f}@{r.year:.0f} z{r.depth:.0f}" for r in s.nlargest(5, "mag").itertuples())
        raise SystemExit(f"{k}: Mmax {m:.2f} > MMAX_SANITY {c.MMAX_SANITY} ({top}); "
                         "check the class or set MMAX_OVERRIDE")
    return m


def pattern_events(k, s, w, c):
    """Events that draw the spatial pattern of a class and their weights (rate at the fit floor)."""
    steps = c.COMPLETENESS[k]
    ev = w["comp"] if c.SMOOTH_EVENTS == "floor" else s[gr.complete(s, steps)].reset_index(drop=True)
    return ev


def cross_validate(k, ev, wt, b, c, te, glon, glat):
    """
    Kernel settings of a class by time-block cross-validation.

    The complete period is cut into KERNEL_CV_BLOCK-year blocks; for every
    setting of KERNEL_CV_GRID the pattern is built from all blocks but one and
    the held-out events are scored by the mean spatial log-likelihood of the
    cell they fall in (pattern mixed with 1 % uniform). Returns the best
    setting and the table of all scores.
    """
    import itertools
    from scipy.spatial import cKDTree

    xyz = lambda lo, la: np.column_stack([np.cos(np.radians(la)) * np.cos(np.radians(lo)),
                                          np.cos(np.radians(la)) * np.sin(np.radians(lo)),
                                          np.sin(np.radians(la))])
    elon, elat, yr = ev["longitude"].to_numpy(), ev["latitude"].to_numpy(), ev["year"].to_numpy()
    cell = cKDTree(xyz(glon, glat)).query(xyz(elon, elat))[1]
    y0 = np.nanmin(gr.since(ev["mag"].to_numpy(), c.COMPLETENESS[k]))
    blk = np.floor((yr - y0) / c.KERNEL_CV_BLOCK).astype(int)
    test = [i for i in np.unique(blk) if (blk == i).sum() >= c.KERNEL_CV_MIN]
    if len(test) < 2:
        print(f"[warn] {k}: too few blocks for cross-validation, keeping the config kernel")
        return None, pd.DataFrame()
    rows, grid = [], c.KERNEL_CV_GRID
    for kind, nn, dmax in itertools.product(grid["KERNEL"], grid["N_NEIGHBORS"], grid["MAX_DIST_KM"]):
        ll, n = 0.0, 0
        for i in test:
            tr = blk != i
            h = smooth.kernel(elon[tr], elat[tr], nn, c.MIN_KERNEL_KM)
            f = smooth.field(elon[tr], elat[tr], wt[tr], h, glon, glat, c.KERNEL_POWER, dmax, kind)
            p = 0.99 * f / f.sum() + 0.01 / len(f)
            ll += np.log(p[cell[~tr]]).sum()
            n += int((~tr).sum())
        rows.append({"class": k, "kernel": kind, "n_neighbors": nn, "max_dist_km": dmax, "ll_per_event": ll / n,
                     "n_test": n, "n_blocks": len(test)})
    t = pd.DataFrame(rows)
    best = t.loc[t["ll_per_event"].idxmax()]
    print(f"{k}: kernel {best['kernel']}, {int(best['n_neighbors'])} neighbours, cut-off {best['max_dist_km']:g} km "
          f"(ll/event {best['ll_per_event']:.3f}; worst {t['ll_per_event'].min():.3f}, {len(t)} settings, "
          f"{len(test)} blocks)")
    return {"KERNEL": best["kernel"], "N_NEIGHBORS": int(best["n_neighbors"]), "MAX_DIST_KM": float(best["max_dist_km"])}, t


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "ssm"
    od.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)
    te = c.T_END or json.loads((c.OUT / "decluster" / "input.json").read_text())["t_end"]
    missing = [k for k in c.CLASSES if k not in c.COMPLETENESS]
    if missing:
        raise SystemExit(f"no COMPLETENESS for {missing}")

    cells = domain(c)
    cats = {k: cat.load(c.OUT / "decluster" / f"cat_dc_{k}_{c.DC_METHOD}.csv", bbox=c.BBOX)
            for k in c.CLASSES}
    own = [k for k in c.CLASSES if k not in c.B_SOURCE]
    fits = {k: fit(k, cats[k], c, te, nboot=c.N_BOOT) for k in own}
    weak = [f"{k} (n={w['n']})" for k, w in fits.items() if not np.isfinite(w["b"])]
    if weak:
        raise SystemExit(f"too few complete events above the fit floor for {weak}; "
                         "revise COMPLETENESS or MMIN_FIT_BY_CLASS, borrow b via B_SOURCE, or drop the class")
    b_use = {k: fits[k]["b"] for k in own}
    for k, src in c.B_SOURCE.items():
        if k not in cats:
            continue
        donors = [src] if isinstance(src, str) else list(src)
        b_use[k] = (fits[donors[0]]["b"] if len(donors) == 1 and donors[0] in fits else
                    fit(donors[0], pd.concat([cats[d] for d in donors]), c, te)["b"])
        fits[k] = fit(k, cats[k], c, te, b=b_use[k])
        if not fits[k]["n"]:
            raise SystemExit(f"{k}: no complete events above the fit floor, even with b borrowed")
        print(f"{k}: b {b_use[k]:.3f} from {'+'.join(donors)}, rate from its own {fits[k]['n']} events")
    mmax = {k: mmax_of(k, s, c) for k, s in cats.items()}

    stab = []
    for k in own:
        s = cats[k]
        f0 = fits[k]["mmin"]
        for fl in np.round(np.arange(f0 - 0.5, f0 + 1.05, 0.1), 2):
            if fl < min(x[0] for x in c.COMPLETENESS[k]) - 1e-6:
                continue
            w = fit(k, s, c, te, fl)
            stab.append({"class": k, "floor": fl, "b": w["b"], "n": w["n"]})
    stab = pd.DataFrame(stab, columns=["class", "floor", "b", "n"])
    stab.round(4).to_csv(od / "b_stability.csv", index=False)

    e = smooth.edges(c.MMIN, max(mmax.values()), c.DM)
    glon, glat = cells["lon"].to_numpy(), cells["lat"].to_numpy()
    per, info, cvs = {}, [], []
    for k, s in cats.items():
        w, b = fits[k], b_use[k]
        steps = c.COMPLETENESS[k]
        comp = w["comp"]
        rate = w["rate"] * 10 ** (-b * (c.MMIN - w["mmin"]))
        kp = {"N_NEIGHBORS": c.N_NEIGHBORS, "MIN_KERNEL_KM": c.MIN_KERNEL_KM, "MAX_DIST_KM": c.MAX_DIST_KM,
              "KERNEL_POWER": c.KERNEL_POWER, "KERNEL": c.KERNEL, **c.KERNEL_BY_CLASS.get(k, {})}
        ev = pattern_events(k, s, w, c)
        wt = 10 ** (b * (gr.mc_of(ev["mag"], steps) - w["mmin"])) / (te - gr.since(ev["mag"], steps))
        elon, elat = ev["longitude"].to_numpy(), ev["latitude"].to_numpy()
        z0, z1 = c.MASK_BY_CLASS.get(k, (None, None))
        on = ((cells["slab_km"] >= (z0 if z0 is not None else -np.inf))
              & (cells["slab_km"] < (z1 if z1 is not None else np.inf))).to_numpy()
        if c.KERNEL_CV:
            best, t = cross_validate(k, ev, wt, b, c, te, glon[on], glat[on])
            if best:
                kp.update(best)
            cvs.append(t)
        h = smooth.kernel(elon, elat, kp["N_NEIGHBORS"], kp["MIN_KERNEL_KM"])
        shape = np.zeros(len(cells))
        shape[on] = smooth.field(elon, elat, wt, h, glon[on], glat[on], kp["KERNEL_POWER"], kp["MAX_DIST_KM"],
                                 kp["KERNEL"])
        if not on.all():
            print(f"{k}: smoothed onto {int(on.sum())} of {len(on)} cells (slab top {z0}-{z1} km)")
        if shape.sum() <= 0:
            raise RuntimeError(f"{k}: empty field")
        rb = smooth.tgr_bins(shape, rate, b, e, mmax[k])
        exp = rate * (1 - 10 ** (-b * (mmax[k] - c.MMIN)))
        if abs(rb.sum() / exp - 1) > 1e-9:
            raise RuntimeError(f"{k}: binned total {rb.sum()} != {exp}")
        per[k] = rb
        smooth.write(cells, rb, e, od / f"grid_{k}.csv")

        mt = np.arange(w["mmin"], s["mag"].max() + 1e-6, 0.1)
        obs = gr.obs_cum(comp, steps, te, mt)
        mod = rate * np.clip(10 ** (-b * (mt - c.MMIN)) - 10 ** (-b * (mmax[k] - c.MMIN)), 0, None)
        big = mt >= min(s["mag"].max(), mmax[k]) - 0.3
        info.append({"class": k, "n_complete": w["n"], "floor": w["mmin"], "b_fit": w["b"],
                     "b_err": w["b_err"], "b_used": b, "rate_floor": w["rate"],
                     f"rate_M{c.MMIN}": rate, "mmax": mmax[k], "n_pattern": len(ev), "kernel": kp["KERNEL"],
                     "n_neighbors": kp["N_NEIGHBORS"], "max_dist_km": kp["MAX_DIST_KM"],
                     "kernel_med_km": float(np.median(h)),
                     "model_obs_floor": mod[0] / obs[0],
                     "model_obs_top": mod[big][0] / obs[big][0] if big.any() and obs[big][0] > 0 else np.nan})
        if w["b_err"] > c.B_ERR_WARN or not 0.5 <= w["b"] <= 1.5:
            print(f"[warn] {k}: b {w['b']:.3f} +/- {w['b_err']:.3f}")

        f, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.5))
        a1.semilogy(mt, obs, "ko", ms=4, label="observed (complete, 1/T)")
        a1.semilogy(mt, np.maximum(mod, 1e-8), "C0", lw=2, label=f"model b={b:.2f} Mmax={mmax[k]:.1f}")
        a1.axvline(w["mmin"], color="crimson", ls="--", lw=0.8)
        a1.set_xlabel("M")
        a1.set_ylabel("N(>=M)/yr")
        a1.legend(fontsize=8)
        st = stab[stab["class"] == k]
        a2.plot(st["floor"], st["b"], "o-")
        a2.axvline(w["mmin"], color="crimson", ls="--", lw=0.8)
        a2.set_xlabel("fit floor")
        a2.set_ylabel("b")
        f.suptitle(k)
        f.tight_layout()
        f.savefig(c.FIG / f"s02_fit_{k}.png", dpi=200)
        plt.close(f)

    tot = sum(per.values())
    smooth.write(cells, tot, e, od / "grid_total.csv")
    tab = pd.DataFrame(info)
    tab["frac_of_total"] = tab[f"rate_M{c.MMIN}"] / tab[f"rate_M{c.MMIN}"].sum()
    tab.to_csv(od / "classes.csv", index=False)
    if cvs:
        pd.concat([t for t in cvs if len(t)], ignore_index=True).round(4).to_csv(od / "kernel_cv.csv", index=False)
    print(tab.round(4).to_string(index=False))

    # one colour scale for all panels
    top = np.log10(tot.sum(axis=1).max())
    f, axs = plt.subplots(1, len(per) + 1, figsize=(3.5 * (len(per) + 1), 8), sharey=True)
    for ax, (k, rb) in zip(axs, list(per.items()) + [("total", tot)]):
        v = rb.sum(axis=1)
        sc = ax.scatter(glon, glat, c=np.log10(np.maximum(v, 1e-12)), s=2, cmap="magma_r",
                        vmin=top - 4, vmax=top)
        ax.set_aspect("equal")
        ax.set_title(f"{k}: log10 N(>={c.MMIN})", fontsize=9)
    f.colorbar(sc, ax=axs, shrink=0.5)
    f.savefig(c.FIG / "s02_maps.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s02")


if __name__ == "__main__":
    main()