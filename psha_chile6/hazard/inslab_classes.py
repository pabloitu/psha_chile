# S1: the in-slab change split by class (intra_slab, slab_deep, deep_nest), from the
# class-only jobs of both trees (c_is_<class>), no new runs. Hazard: PGA with one class
# on the new catalog and everything else old (rates add, so the split is exact), and
# the exceedance rate of each class at the old total PGA, new / old. Sources: the
# regional fit of each class (ssm/classes.csv) and the model and catalog rates within
# 150 km of each city (intraslab/check_rates.py, check/rates.csv), new / old.
# Outputs: outputs/s1/09_hazard.csv, 09_rates.csv, 09_fits.csv, 09_inslab.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
from hazard import config as hc
from hazard import logic_tree as lt
from hazard.post import load, iml

# settings
HAZ = {"old": paths.PREV / "outputs" / "hazard" / hc.SITE, "new": hc.OUT_ROOT}
SRC = {"old": paths.PREV / "outputs" / "intraslab" / "ref", "new": paths.OUT / "intraslab" / "ref"}
CLASSES = ["intra_slab", "slab_deep", "deep_nest"]
MAGS = [5.0, 6.0, 7.0, 7.5]
COLORS = {"in-slab": "#8c1c13", "intra_slab": "#dd8452", "slab_deep": "#c44e52", "deep_nest": "#8172b3"}
OUT = paths.OUT / "s1"


def mean(job, root):
    r = load(job, root=root)
    m = list(r["imtls"]).index("PGA")
    return np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :]), r


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rate = lambda p: -np.log(1 - np.clip(p, 0, 1 - 1e-12))
    fam = {v: {f: mean(f"c_{lt.SHORT[f]}_ref", r)[0] for f in lt.FAMS} for v, r in HAZ.items()}
    cls = {v: {k: mean(f"c_is_{k}", r)[0] for k in CLASSES} for v, r in HAZ.items()}
    r0 = mean("c_if_ref", HAZ["old"])[1]
    lv, names, poes = r0["imtls"]["PGA"], r0["names"], hc.POES
    for v in HAZ:
        s = 1 - np.prod([1 - cls[v][k] for k in CLASSES], axis=0)
        ok = fam[v]["intraslab"] > 1e-6
        print(f"[check] {v}: classes summed vs c_is_ref, max rel. difference "
              f"{np.max(np.abs(s[ok] / fam[v]['intraslab'][ok] - 1)):.1e}")

    # hazard
    rows = []
    for s, site in enumerate(names):
        for p in poes:
            rp = round(-hc.INV_TIME / np.log(1 - p))

            def pga(new):
                sv = [1 - fam["old"][f][s] for f in lt.FAMS if f != "intraslab"]
                sv += [1 - cls["new" if k in new else "old"][k][s] for k in CLASSES]
                return iml(1 - np.prod(sv, axis=0), lv, p)

            x0 = pga(())
            row = {"site": site, "return_period": rp, "pga_old": x0, "in-slab": 100 * (pga(tuple(CLASSES)) / x0 - 1)}
            for k in CLASSES:
                row[k] = 100 * (pga((k,)) / x0 - 1)
                at = {v: rate(np.exp(np.interp(np.log(x0), np.log(lv), np.log(np.maximum(cls[v][k][s], 1e-30)))))
                      for v in HAZ}
                row[f"{k} rate new/old"] = at["new"] / at["old"] if at["old"] > 0 else np.nan
                row[f"{k} share old"] = 100 * at["old"] / rate(p)
            rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "09_hazard.csv", index=False)
    for rp, g in t.groupby("return_period"):
        print(f"\nPGA change %, {rp} yr: all in-slab classes new, then one class new (everything else old)")
        print(g.set_index("site")[["pga_old", "in-slab"] + CLASSES].round(2).to_string())
        print(f"\nexceedance rate of each class at the old {rp} yr PGA: share of the old total %, and new / old")
        print(g.set_index("site")[[f"{k} {x}" for k in CLASSES for x in ("share old", "rate new/old")]]
              .round(2).to_string())

    # regional fits
    fits = []
    for v, d in SRC.items():
        c = pd.read_csv(d / "ssm" / "classes.csv").set_index("class")
        mm = float([k for k in c.columns if k.startswith("rate_M")][0][6:])
        for k in CLASSES:
            q, b, u = c.loc[k, f"rate_M{mm:g}"], c.loc[k, "b_used"], c.loc[k, "mmax"]
            fits.append({"class": k, "ver": v, "n": c.loc[k, "n_complete"], "b": b, "mmax": u,
                         **{f"N{m:g}": q * max(10 ** (-b * (m - mm)) - 10 ** (-b * (u - mm)), 0) for m in MAGS}})
    f = pd.DataFrame(fits)
    f.to_csv(OUT / "09_fits.csv", index=False)
    w = f.pivot(index="class", columns="ver").reindex(CLASSES)
    s = pd.DataFrame(index=w.index)
    for x in ("n", "b", "mmax"):
        s[x] = [f"{a:.3g} / {b:.3g}" for a, b in zip(w[(x, "old")], w[(x, "new")])]
    for m in MAGS:
        s[f"N>={m:g} new/old"] = (w[(f"N{m:g}", "new")] / w[(f"N{m:g}", "old")]).round(2)
    print("\nregional fit per class, old / new (n = complete events above the fit floor)")
    print(s.to_string())

    # model and catalog near the cities
    miss = [str(d / "check" / "rates.csv") for d in SRC.values() if not (d / "check" / "rates.csv").exists()]
    if miss:
        print(f"\n[skip] rates near the cities: run intraslab/check_rates.py ({miss})")
    else:
        r = pd.read_csv(SRC["old"] / "check" / "rates.csv").merge(
            pd.read_csv(SRC["new"] / "check" / "rates.csv"), on=["site", "class", "M"], suffixes=("_old", "_new"))
        r["model new/old"] = r["model_new"] / r["model_old"].replace(0, np.nan)
        r["obs new/old"] = r["obs_new"] / r["obs_old"].replace(0, np.nan)
        r.to_csv(OUT / "09_rates.csv", index=False)
        for m in (5.5, 6.5):
            x = r[(r["M"] == m) & r["class"].isin(CLASSES)]
            p = x.pivot_table(index="site", columns="class", values=["model new/old", "obs new/old"], sort=False,
                              dropna=False)
            n = x.pivot_table(index="site", columns="class", values=["n_obs_old", "n_obs_new"], sort=False,
                              dropna=False)
            print(f"\nN(>={m:g}) within 150 km per class, new / old: model, catalog (n_obs old -> new)")
            out = pd.DataFrame(index=p.index)
            for k in [k for k in CLASSES if ("model new/old", k) in p.columns]:
                out[k] = [f"{a:5.2f}  {b:5.2f}  ({o:.0f}->{e:.0f})" for a, b, o, e in
                          zip(p[("model new/old", k)], p[("obs new/old", k)], n[("n_obs_old", k)], n[("n_obs_new", k)])]
            print(out.reindex([c for c in hc.CITIES if c in out.index]).to_string())

    # figure
    rps = sorted(t["return_period"].unique())
    fig, axs = plt.subplots(len(rps), 1, figsize=(11, 3.4 * len(rps)), sharex=True, squeeze=False)
    parts = ["in-slab"] + CLASSES
    for ax, rp in zip(axs[:, 0], rps):
        g = t[t["return_period"] == rp]
        i = np.arange(len(g))
        for j, k in enumerate(parts):
            ax.bar(i + (j - 1.5) * 0.2, g[k], 0.2, color=COLORS[k], label="all in-slab" if k == "in-slab" else f"{k} alone")
        ax.axhline(0, color="k", lw=0.6)
        ax.set_ylabel(f"PGA change %, {rp} yr")
        ax.grid(axis="y", alpha=0.3)
        ax.set_xticks(i, [x.replace("_", " ") for x in g["site"]], rotation=30, ha="right")
    axs[0, 0].legend(fontsize=8, ncol=4)
    axs[0, 0].set_title("in-slab classes on catalog.csv, everything else as in psha_chile5", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "09_inslab.png", dpi=300)
    plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
