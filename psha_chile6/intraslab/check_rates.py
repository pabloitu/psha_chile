# Model vs catalog rates of the in-slab classes around each city, no GMM.
# Model: per-class grids from s02, cells within R_KM of the city, hypocentre
# depths from s03 (depths()). Catalog: complete declustered events
# of the class within R_KM, each weighted 1/T(M).
# Outputs: outputs/intraslab/<tag>/check/rates.csv, depth.csv,
#          figures/check_rates.png; with COMPARE also ref/check/rates_compare.csv

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import run
from lib import cat, gr, smooth
from lib.dc import hav
from variants import VARIANTS
from hazard import config as hc
from intraslab.s03_sources import depths

# settings
VARIANT = "ref"
COMPARE = ["ref", "cls_m5", "cls_p5", "cls_fix", "mc_lo", "mc_hi", "raw", "smooth_cv"]   # variants of the compare table
R_KM = 150.0
MAGS = [5.0, 5.5, 6.0, 6.5, 7.0]
BANDS = [0, 70, 100, 150, 700]      # hypocentre depth bands, km
M_DEPTH = 5.5                       # depth table counts N(>=M_DEPTH)


def main(variant=VARIANT):
    c = run.build("intraslab", VARIANTS["intraslab"][variant])
    od = c.OUT / "check"
    od.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)
    te = c.T_END or json.loads((c.OUT / "decluster" / "input.json").read_text())["t_end"]

    # model grids and complete catalogs per class
    g, ev = {}, {}
    for k in c.CLASSES:
        df, rb, e = smooth.read(c.OUT / "ssm" / f"grid_{k}.csv")
        g[k] = (df, rb, e[:-1], depths(c, df)[0])
        s = cat.load(c.OUT / "decluster" / f"cat_dc_{k}_{c.DC_METHOD}.csv", bbox=c.BBOX)
        s = s[gr.complete(s, c.COMPLETENESS[k])].reset_index(drop=True)
        s["w"] = 1.0 / (te - gr.since(s["mag"].to_numpy(), c.COMPLETENESS[k]))
        ev[k] = s

    rows, dep, curves = [], [], {}
    for city, (x, y) in hc.CITIES.items():
        for k in c.CLASSES:
            df, rb, lo, hz = g[k]
            near = hav(x, y, df["lon"].to_numpy(), df["lat"].to_numpy()) <= R_KM
            s = ev[k]
            s = s[hav(x, y, s["longitude"].to_numpy(), s["latitude"].to_numpy()) <= R_KM]
            for m in MAGS:
                mod = rb[near][:, lo >= m - 1e-6].sum()
                ok = s["mag"] >= m - 1e-6
                rows.append({"site": city, "class": k, "M": m, "model": mod, "obs": s.loc[ok, "w"].sum(),
                             "n_obs": int(ok.sum())})
            mz = rb[:, lo >= M_DEPTH - 1e-6].sum(axis=1)
            ok = s["mag"] >= M_DEPTH - 1e-6
            for a, b in zip(BANDS[:-1], BANDS[1:]):
                im = near & (hz >= a) & (hz < b)
                io = ok & (s["depth"] >= a) & (s["depth"] < b)
                dep.append({"site": city, "class": k, "band": f"{a}-{b}", "model": mz[im].sum(),
                            "obs": s.loc[io, "w"].sum(), "n_obs": int(io.sum())})
            cm = rb[near].sum(axis=0)[::-1].cumsum()[::-1]
            curves[city, k] = (lo, cm, gr.obs_cum(s, c.COMPLETENESS[k], te, lo) if len(s) else 0 * lo)

    # tables: per class and total
    t = pd.DataFrame(rows)
    tot = t.groupby(["site", "M"], sort=False)[["model", "obs", "n_obs"]].sum().reset_index()
    t = pd.concat([t, tot.assign(**{"class": "total"})], ignore_index=True)
    t["ratio"] = t["model"] / t["obs"].replace(0, np.nan)
    t.to_csv(od / "rates.csv", index=False)
    d = pd.DataFrame(dep)
    d.to_csv(od / "depth.csv", index=False)

    print(f"\nmodel / catalog, N(>=M) within {R_KM:g} km (n_obs in brackets)")
    t["cell"] = [f"{r:5.2f} ({n})" if np.isfinite(r) else f"  -   ({n})" for r, n in zip(t["ratio"], t["n_obs"])]
    print(t.pivot_table(index=["site", "class"], columns="M", values="cell", aggfunc="first", sort=False)
          .to_string())
    for col in ("model", "obs"):
        f = d.pivot_table(index=["site", "class"], columns="band", values=col, sort=False)
        f = f[[f"{a}-{b}" for a, b in zip(BANDS[:-1], BANDS[1:])]]
        print(f"\n{col}: share of N(>={M_DEPTH}) per hypocentre band, km")
        print(f.div(f.sum(axis=1), axis=0).round(2).to_string())

    # figure: one panel per city
    n = len(hc.CITIES)
    f, axs = plt.subplots(2, (n + 1) // 2, figsize=(3.2 * ((n + 1) // 2), 7), sharex=True, sharey=True,
                          squeeze=False)
    for ax, city in zip(axs.ravel(), hc.CITIES):
        for i, k in enumerate(c.CLASSES):
            lo, cm, ob = curves[city, k]
            if cm.max() <= 0:
                continue
            ax.semilogy(lo, np.where(cm > 0, cm, np.nan), color=f"C{i}", lw=1.5, label=k)
            ax.semilogy(lo, np.where(ob > 0, ob, np.nan), "o", color=f"C{i}", ms=3)
        ax.set_title(city, fontsize=9)
        ax.set_xlim(MAGS[0], None)
        ax.grid(alpha=0.3)
    axs[0][0].set_ylim(1e-4, None)
    axs[0][0].legend(fontsize=7)
    for ax in axs[-1]:
        ax.set_xlabel("M")
    for ax in axs[:, 0]:
        ax.set_ylabel(f"N(>=M)/yr within {R_KM:g} km")
    f.suptitle(f"intraslab {c.TAG}: model (lines) vs complete declustered catalog (dots)")
    f.tight_layout()
    f.savefig(c.FIG / "check_rates.png", dpi=200)
    plt.close(f)
    print(f"\nwrote {od} and {c.FIG / 'check_rates.png'}")
    return t


def compare(variants=COMPARE, mags=(5.5, 6.0)):
    """Model / catalog ratio of the total in-slab rate per city for several variants, at two magnitudes."""
    import io, contextlib
    out = []
    for v in variants:
        if v not in VARIANTS["intraslab"]:
            print(f"[skip] {v}: not in variants.py")
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            t = main(v)
        t = t[(t["class"] == "total") & t["M"].isin(mags)]
        out.append(t[["site", "M", "ratio", "n_obs"]].assign(variant=v))
    t = pd.concat(out, ignore_index=True)
    c = run.config("intraslab", {})
    t.to_csv(c.OUT / "check" / "rates_compare.csv", index=False)
    for m in mags:
        print(f"\nmodel / catalog N(>={m}) within {R_KM:g} km per variant (n_obs)")
        p = t[t["M"] == m].pivot_table(index="site", columns="variant", values="ratio", sort=False)[
            [v for v in variants if v in set(t["variant"])]]
        p["n_obs"] = t[(t["M"] == m) & (t["variant"] == variants[0])].set_index("site")["n_obs"]
        print(p.reindex([s for s in hc.CITIES if s in p.index]).round(2).to_string())
    print(f"\nwrote {c.OUT / 'check' / 'rates_compare.csv'}")


if __name__ == "__main__":
    main()
    if COMPARE:
        compare()