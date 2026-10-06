# S1 (CONTEXT_sources.md): the catalog effect on the source models. The reference
# of each model built on catalog.csv here against the same reference built on the
# campaign catalogs in psha_chile5, read from the two output trees; no refit.
# Outputs in outputs/s1/:
#   01_counts.csv     model input, mainshocks and complete events per subset and M bin
#   01_coverage.csv   family events of catalog.csv the models do not read, and why
#   01_unused_m7.csv  those of M >= 7, one row each
#   02_mt_<model>.png magnitude-time by depth_status with the completeness steps; grey
#                     crosses are family events the model does not read
#   03_fits.csv       b, rate, Mmax, fitted and observed N(>=M) per subset
#   03_fmd_<model>.png  FMD (top) and b against fit floor (bottom), old and new
#   04_cities.csv     catalog N(>=M) within R_KM of each city per family
#   04_inslab.csv     in-slab model / catalog per city (intraslab/check_rates.py, both runs)

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
import run
from lib import cat, gr
from lib.dc import hav
from variants import VARIANTS
from hazard import config as hc

# settings
REF = {"interface": "mmin55", "intraslab": "ref", "crustal": "ref"}
FAM = {"interface": "interface", "intraslab": "in-slab", "crustal": "crustal"}
ROOTS = {"old": paths.PREV / "outputs", "new": paths.OUT}
BINS = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 10.0]
MAGS = [6.0, 7.0, 7.5, 8.0]
CITY_MAGS = [5.5, 6.0, 7.0]
R_KM = 150.0
OUT = paths.OUT / "s1"
DS = {"relocated_cabello": "#1f4e9c", "relocated_potin": "#4c9be8", "free": "#2ca25f", "filled": "#a1d99b",
      "fixed": "#e6550d", "missing": "#bdbdbd", "assigned": "#9e4f9e"}


def used(d, model):
    """Model input from a run's config.json, and why each other family event is not read."""
    df = cat.family(d["CAT"], d["FAMILY"], d["CLASS_MAP"]) if d.get("FAMILY") else cat.load(d["CAT"])
    why = np.full(len(df), "", object)
    if model == "interface":
        b = d["SEG_BOUNDS"]
        why[~df["latitude"].between(b[0], b[-1]).to_numpy()] = "outside SEG_BOUNDS"
        return df, why
    k = df["class"].to_numpy()
    why[~np.isin(k, list(d["CLASSES"]))] = "class not fitted"
    cut = np.array([d.get("HIST_CUTOFF_BY_CLASS", {}).get(x, d["HIST_CUTOFF"]) or -np.inf for x in k])
    why[(why == "") & (df["year"].to_numpy() < cut)] = "before HIST_CUTOFF"
    if isinstance(d["CLASSES"], dict):
        for x, box in d["CLASSES"].items():
            if box:
                lo, hi, la, ha = box
                ins = df["longitude"].between(lo, hi) & df["latitude"].between(la, ha)
                why[(why == "") & (k == x) & ~ins.to_numpy()] = "outside class box"
    lo, hi, la, ha = d["BBOX"]
    ins = (df["longitude"].between(lo, hi) & df["latitude"].between(la, ha)).to_numpy()
    why[(why == "") & ~ins] = "outside BBOX"
    return df, why


def mains(out, d, model):
    m = d["DC_METHOD"]
    if model == "interface":
        return cat.load(out / "decluster" / f"cat_dc_{m}.csv")
    return pd.concat([cat.load(out / "decluster" / f"cat_dc_{k}_{m}.csv", bbox=d["BBOX"]).assign(**{"class": k})
                      for k in d["CLASSES"]], ignore_index=True)


def subsets(df, d, model):
    """(name, mask, completeness steps, fit floor) per fitted subset."""
    if model == "interface":
        b = d["SEG_BOUNDS"]
        seg = pd.cut(df["latitude"], bins=b, labels=d["SEG_IDS"], right=False).astype(str).to_numpy()
        yield d["FULL_ID"], df["latitude"].between(b[0], b[-1]).to_numpy(), d["COMPLETENESS"], d["MMIN_FIT"]
        for s in d["SEG_IDS"]:
            yield s, seg == s, d["COMPLETENESS"], d["MMIN_FIT"]
        return
    for k in d["CLASSES"]:
        yield k, (df["class"] == k).to_numpy(), d["COMPLETENESS"][k], d["MMIN_FIT_BY_CLASS"].get(k, d["MMIN_FIT"])


def fitted(out, d, model):
    """Subset -> (b, b_err, n, Mmax, N(>=m) function) from the run's own fit tables."""
    r = {}
    if model == "interface":
        t = pd.read_csv(out / "ab" / "compare.csv")
        for x in t[t["est"] == "weichert"].itertuples():
            r[x.seg] = (x.b, x.b_err, x.n, np.nan, lambda m, a=x.a, b=x.b: 10 ** (a - b * np.asarray(m)))
        return r
    t = pd.read_csv(out / "ssm" / "classes.csv")
    mm = d["MMIN"]
    for x in t.to_dict("records"):
        f = (lambda m, q=x[f"rate_M{mm}"], b=x["b_used"], u=x["mmax"]:
             q * np.clip(10 ** (-b * (np.asarray(m) - mm)) - 10 ** (-b * (u - mm)), 0, None))
        r[x["class"]] = (x["b_used"], x["b_err"], x["n_complete"], x["mmax"], f)
    return r


def stab(out, model):
    t = pd.read_csv(out / ("ab" if model == "interface" else "ssm") / "b_stability.csv")
    return t.rename(columns={"seg": "sub", "class": "sub", "b_w": "b"})[["sub", "floor", "b"]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    counts, cover, unused, fits, cities = [], [], [], [], []
    for model, v in REF.items():
        tag = run.config(model, VARIANTS[model][v]).TAG
        runs = {}
        for ver, root in ROOTS.items():
            out = root / model / tag
            d = json.loads((out / "config.json").read_text())["config"]
            js = json.loads((out / "decluster" / "input.json").read_text())
            te = d["T_END"] or js.get("t_end", js["years"][1])
            df, why = used(d, model)
            mn = mains(out, d, model)
            runs[ver] = (out, d, te, df[why == ""], mn)
            skip = df[why != ""]
            if ver == "new":
                x = df.assign(why=why)[why != ""]
                for (k, w), g in x.groupby(["class", "why"]):
                    cover.append({"model": model, "class": k, "why": w, "n": len(g), "n_M5.5": int((g["mag"] >= 5.5).sum()),
                                  "n_M7": int((g["mag"] >= 7).sum()), "mmax": g["mag"].max()})
                unused.append(x[x["mag"] >= 7].assign(model=model))

            # counts, fits and FMD points per subset
            ft = fitted(out, d, model)
            for s, m, steps, fl in subsets(runs[ver][3], d, model):
                ms = next(q for q in subsets(mn, d, model) if q[0] == s)[1]
                a, e = runs[ver][3][m], mn[ms]
                cp = e[gr.complete(e, steps)]
                for st, g in (("input", a), ("mainshocks", e), ("complete", cp), ("fit", cp[cp["mag"] >= fl - 1e-6])):
                    h = np.histogram(g["mag"], BINS)[0]
                    counts.append({"model": model, "sub": s, "ver": ver, "stage": st,
                                   **{f"{lo:g}-{hi:g}": n for lo, hi, n in zip(BINS[:-1], BINS[1:], h)}})
                b, be, n, mx, f = ft.get(s, (np.nan,) * 4 + (lambda q: np.nan * np.asarray(q),))
                ob = gr.obs_cum(cp, steps, te, MAGS)
                fits.append({"model": model, "sub": s, "ver": ver, "n_fit": n, "floor": fl, "b": b, "b_err": be,
                             "mmax": mx, "mmax_obs": e["mag"].max(),
                             **{f"fit_M{q:g}": y for q, y in zip(MAGS, f(MAGS))},
                             **{f"obs_M{q:g}": y for q, y in zip(MAGS, ob)}})

            # catalog rates near the cities, complete mainshocks of the fitted subsets
            ev = []
            for s, m, steps, fl in subsets(mn, d, model):
                if model == "interface" and s != d["FULL_ID"]:
                    continue
                e = mn[m]
                e = e[gr.complete(e, steps)]
                ev.append(e.assign(w=1.0 / (te - gr.since(e["mag"].to_numpy(), steps))))
            ev = pd.concat(ev, ignore_index=True)
            for city, (x, y) in hc.CITIES.items():
                e = ev[hav(x, y, ev["longitude"].to_numpy(), ev["latitude"].to_numpy()) <= R_KM]
                for q in CITY_MAGS:
                    k = e["mag"] >= q - 1e-6
                    cities.append({"site": city, "family": FAM[model], "M": q, "ver": ver,
                                   "rate": e.loc[k, "w"].sum(), "n": int(k.sum())})

        # figures
        out, d, te, a, mn = runs["new"]
        subs = list(subsets(a, d, model))
        f, axs = plt.subplots(len(subs), 2, figsize=(12, 2.6 * len(subs)), squeeze=False,
                              gridspec_kw={"width_ratios": [1, 1.6]})
        for (s, m, steps, fl), (a1, a2) in zip(subs, axs):
            g = a[m]
            x = skip if model == "interface" else skip[skip["class"] == s]
            for ax in (a1, a2):
                ax.plot(x["year"], x["mag"], "x", ms=3, color="0.5", label=f"not read {len(x)}")
            for k, col in DS.items():
                x = g[g["depth_status"] == k]
                a1.plot(x["year"], x["mag"], ".", ms=3, color=col)
                a2.plot(x["year"], x["mag"], ".", ms=1.5, color=col, label=f"{k} {len(x)}")
            st = sorted(steps, key=lambda q: q[1])
            yy, mc = [q[1] for q in st] + [te], [q[0] for q in st] + [st[-1][0]]
            for ax in (a1, a2):
                ax.step(yy, mc, where="post", color="k", lw=1)
                ax.grid(alpha=0.3)
            a1.set_xlim(min(1900, g["year"].min(), x["year"].min() if len(x) else 1900) - 10, 1965)
            a1.set_ylim(6.0, 9.7)
            a2.set_xlim(1960, te + 1)
            a2.set_ylim(3.9, 9.7)
            a1.set_ylabel(f"{s}\nM")
            a2.legend(fontsize=6, ncol=4, markerscale=4, loc="upper left")
        axs[-1][0].set_xlabel("year")
        axs[-1][1].set_xlabel("year")
        f.suptitle(f"{model}: model input from catalog.csv by depth_status; line = completeness steps", fontsize=10)
        f.tight_layout()
        f.savefig(OUT / f"02_mt_{model}.png", dpi=300)
        plt.close(f)

        t = pd.DataFrame(fits)
        bs = {ver: stab(r[0], model) for ver, r in runs.items()}
        f, axs = plt.subplots(2, len(subs), figsize=(3.3 * len(subs), 7), squeeze=False)
        for i, (s, *_) in enumerate(subs):
            a1, a2 = axs[0][i], axs[1][i]
            for ver, sty in (("old", dict(color="0.55", ls="--")), ("new", dict(color="C0", ls="-"))):
                out_, d_, te_, _, mn_ = runs[ver]
                q = next((x for x in subsets(mn_, d_, model) if x[0] == s), None)
                if q is None:
                    continue
                e = mn_[q[1]]
                cp = e[gr.complete(e, q[2])]
                gm = np.arange(min(x[0] for x in q[2]), max(e["mag"].max(), 6) + 0.05, 0.1)
                ob = gr.obs_cum(cp, q[2], te_, gm)
                a1.semilogy(gm, np.where(ob > 0, ob, np.nan), "o", ms=3, mfc="none" if ver == "old" else sty["color"],
                            color=sty["color"])
                r = t[(t["model"] == model) & (t["sub"] == s) & (t["ver"] == ver)].iloc[0]
                ft = fitted(out_, d_, model).get(s)
                if ft:
                    y = ft[4](gm)
                    a1.semilogy(gm, np.where(y > 0, y, np.nan), lw=1.5, label=f"{ver} b={r['b']:.2f} n={r['n_fit']:.0f}", **sty)
                x = bs[ver][bs[ver]["sub"] == s]
                a2.plot(x["floor"], x["b"], marker="o", ms=3, label=ver, **sty)
                a1.axvline(q[3], color=sty["color"], lw=0.6, ls=":")
            a1.set_title(s, fontsize=9)
            a1.set_ylim(1e-4, None)
            a1.set_xlabel("M")
            a1.legend(fontsize=6)
            a1.grid(alpha=0.3)
            a2.set_xlabel("fit floor")
            a2.grid(alpha=0.3)
        axs[0][0].set_ylabel("N(>=M)/yr, complete mainshocks")
        axs[1][0].set_ylabel("b")
        axs[1][0].legend(fontsize=7)
        f.suptitle(f"{model}: psha_chile5 (grey, hollow) vs catalog.csv (blue)", fontsize=10)
        f.tight_layout()
        f.savefig(OUT / f"03_fmd_{model}.png", dpi=300)
        plt.close(f)

    # tables
    pd.DataFrame(counts).to_csv(OUT / "01_counts.csv", index=False)
    pd.DataFrame(cover).round(2).to_csv(OUT / "01_coverage.csv", index=False)
    u = pd.concat(unused, ignore_index=True)
    u[["model", "id", "time_iso", "mag", "longitude", "latitude", "depth", "depth_status", "class", "cls_rule",
       "why"]].sort_values(["model", "mag"], ascending=[True, False]).to_csv(OUT / "01_unused_m7.csv", index=False)
    ex = cat.load(paths.CATALOG)
    ex = ex[ex["family"] == "excluded"].groupby("class")["mag"].agg(
        n="size", n55=lambda m: int((m >= 5.5).sum()), n7=lambda m: int((m >= 7).sum()), mmax="max")
    t = pd.DataFrame(fits)
    t.round(5).to_csv(OUT / "03_fits.csv", index=False)
    ct = pd.DataFrame(cities)
    ct.to_csv(OUT / "04_cities.csv", index=False)

    c = pd.DataFrame(counts)
    c["M>=5.5"] = c[[k for k in c.columns if k[:1].isdigit() and float(k.split("-")[0]) >= 5.5]].sum(axis=1)
    c["M>=7"] = c[[k for k in c.columns if k[:1].isdigit() and float(k.split("-")[0]) >= 7.0]].sum(axis=1)
    p = c.pivot_table(index=["model", "sub"], columns=["stage", "ver"], values=["M>=5.5", "M>=7"], sort=False)
    print("\nevents per subset: input, mainshocks, complete, complete above the fit floor (old / new)")
    print(p[[(v, s, w) for v in ("M>=5.5", "M>=7") for s in ("input", "mainshocks", "complete", "fit")
             for w in ("old", "new")]].astype(int).to_string())
    print("\nfamily events of catalog.csv not read by a model")
    print(pd.DataFrame(cover).round(2).to_string(index=False))
    print("\nexcluded family (in no model by construction)")
    print(ex.to_string())
    print("\nunused M >= 7")
    print(u[["model", "time_iso", "mag", "class", "depth_status", "why"]].to_string(index=False))

    k = ["model", "sub"]
    w = t.pivot_table(index=k, columns="ver", values=["b", "b_err", "n_fit", "mmax", "mmax_obs"] +
                      [f"{a}_M{q:g}" for a in ("fit", "obs") for q in MAGS], sort=False)
    print("\nb, Mmax and N(>=M) per year, old / new; fit / obs is the fitted over the observed rate")
    s = pd.DataFrame(index=w.index)
    for x in ("b", "b_err", "n_fit", "mmax_obs", "mmax"):
        s[x] = [f"{a:.3g} / {b:.3g}" for a, b in zip(w[(x, "old")], w[(x, "new")])]
    for q in MAGS:
        s[f"fit/obs M{q:g}"] = [f"{a:.2f} / {b:.2f}" for a, b in zip(
            w[(f"fit_M{q:g}", "old")] / w[(f"obs_M{q:g}", "old")].replace(0, np.nan),
            w[(f"fit_M{q:g}", "new")] / w[(f"obs_M{q:g}", "new")].replace(0, np.nan))]
    print(s.to_string())

    p = ct.pivot_table(index=["site", "family"], columns=["M", "ver"], values="rate", sort=False)
    n = ct.pivot_table(index=["site", "family"], columns=["M", "ver"], values="n", sort=False)
    s = pd.DataFrame(index=p.index)
    for q in CITY_MAGS:
        s[f"M{q:g} new/old"] = [f"{b / a:5.2f} ({m:.0f}/{o:.0f})" if a > 0 else f"  -   ({m:.0f}/{o:.0f})"
                                for a, b, o, m in zip(p[(q, "old")], p[(q, "new")], n[(q, "old")], n[(q, "new")])]
    print(f"\ncatalog N(>=M) within {R_KM:g} km, complete mainshocks: new / old (n new / n old)")
    print(s.to_string())

    # in-slab model / catalog near the cities, from intraslab/check_rates.py of both runs
    tag = run.config("intraslab", VARIANTS["intraslab"]["ref"]).TAG
    ps = {v: r / "intraslab" / tag / "check" / "rates.csv" for v, r in ROOTS.items()}
    miss = [str(x) for x in ps.values() if not x.exists()]
    if miss:
        print(f"\n[skip] in-slab model / catalog: run intraslab/check_rates.py first ({miss})")
        return
    r = pd.read_csv(ps["old"]).merge(pd.read_csv(ps["new"]), on=["site", "class", "M"], suffixes=("_old", "_new"))
    r.to_csv(OUT / "04_inslab.csv", index=False)
    r = r[r["class"] == "total"]
    print(f"\nin-slab model / catalog within {R_KM:g} km, old / new (n_obs old / new)")
    s = pd.DataFrame({f"M{q:g}": [f"{a:5.2f} / {b:5.2f} ({m}/{o})" for a, b, m, o in
                                  r[r["M"] == q][["ratio_old", "ratio_new", "n_obs_old", "n_obs_new"]].to_numpy()]
                      for q in (5.5, 6.0, 6.5)}, index=r[r["M"] == 5.5]["site"].to_numpy())
    print(s.to_string())
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
