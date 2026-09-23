# Tables and figures from one OpenQuake classical calculation built by
# hazard/build.py. Set JOB (and CALC_ID if build.json has none) and run,
# or fill COMPARE to overlay several runs, or CONTRIB for family contributions.
# Outputs: outputs/hazard/<JOB>/post/
#   curves.csv       mean and 16/50/84 % weighted quantiles per site, IMT, level
#   imls.csv         same at the target PoEs
#   axes.csv         conditional mean IML per logic-tree branch value
#   branches.csv     IML at the target PoEs per source branch (GMMs collapsed)
#   figures/         <city>_<imt>.png (model), <city>_<imt>_branches.png (source branches),
#                    UHS when SA is present, axis sensitivity, maps for grids

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from hazard import config as hc
from lib.nrml import trt_id

# settings
JOB = "ref"
CALC_ID = None          # None -> build.json "calc_id"
QUANTILES = (0.025, 0.16, 0.5, 0.84, 0.975)   # first and last bound the envelope
XLIMS = (1e-2, 3.0)
YLIMS = (1e-5, 2.0)
COLORS = ["darkred", "steelblue", "darkgreen", "darkorange", "purple", "saddlebrown", "teal", "olive"]
MAX_ENVELOPES = 4       # branch figures draw envelopes only up to this many branches

# comparison of runs: (job, calc_id, label). When not empty, post.py only draws
# the overlay figures and compare.csv, e.g.
# COMPARE = [("faults", 31, "With faults"), ("nofaults", 32, "No faults")]
COMPARE = []

# contribution of each part to a combined run: one or more splits, each with a
# name (output folder _contrib/<name>), the total and the parts as (job, calc_id, label).
# Rates (-ln(1 - PoE)) of independent sources add, so each part's share at the
# total's IML is exact with one branch per family and approximate otherwise.
# "total": None builds the total as the sum of the part rates (same job settings).
# calc_id None -> read from the job's build.json (written by hazard/run_all.sh)
# All splits are also collected in _contrib/summary.csv.
IF_, CR_ = ("interface", None, "Interface"), ("crustal", None, "Crustal")
CONTRIB = [
    # campaign reference: full GMM tree per region, sum of the three family runs
    {"name": "full_ref", "total": None,
     "parts": [("c_if_ref", None, "Interface"), ("c_is_ref", None, "Intraslab"), ("c_cr_ref", None, "Crustal")]},
    {"name": "full_vs760", "total": None,
     "parts": [("c_if_vs760", None, "Interface"), ("c_is_vs760", None, "Intraslab"),
               ("c_cr_vs760", None, "Crustal")]},
    {"name": "full_iftree", "total": None,
     "parts": [("c_if_tree", None, "Interface"), ("c_is_ref", None, "Intraslab"), ("c_cr_ref", None, "Crustal")]},
    {"name": "all", "total": ("all", None, "All"),
     "parts": [IF_, ("intraslab", None, "Intraslab"), CR_]},
    {"name": "all_classes", "total": ("all", None, "All"),
     "parts": [IF_, ("is_intra_slab", None, "intra_slab"), ("is_slab_deep", None, "slab_deep"),
               ("is_deep_nest", None, "deep_nest"), CR_]},
    {"name": "all_cm_classes", "total": ("all_cm", None, "All classmask"),
     "parts": [IF_, ("cm_intra_slab", None, "intra_slab"), ("cm_slab_deep", None, "slab_deep"),
               ("cm_deep_nest", None, "deep_nest"), CR_]},
    # one GMM changed at a time, AG20 elsewhere
    {"name": "gmm_slab_pk", "total": None,
     "parts": [IF_, ("intraslab_pk", None, "Intraslab"), CR_]},
    {"name": "gmm_slab_mv", "total": None,
     "parts": [IF_, ("intraslab_mv", None, "Intraslab"), CR_]},
    {"name": "gmm_inter_pk", "total": None,
     "parts": [("interface_pk", None, "Interface"), ("intraslab", None, "Intraslab"), CR_]},
    {"name": "gmm_inter_ku", "total": None,
     "parts": [("interface_ku", None, "Interface"), ("intraslab", None, "Intraslab"), CR_]},
]
AXIS_NAMES = {"if": ["geometry", "rate", "mfd"], "is": ["model"], "cr": ["phi", "mmax", "mfd"]}


def load(job, calc_id=None):
    """
    Read curves, realization weights and branch paths from the datastore.

    Returns
    -------
    dict
        curves (sites, rlzs, imts, levels), w (rlzs), imtls, lon, lat,
        names (sites), src (source branch per rlz), axes (DataFrame of
        branch values per rlz), info (build.json).
    """
    from openquake.commonlib.datastore import read
    hd = hc.OUT_ROOT / job
    info = json.loads((hd / "build.json").read_text())
    cid = calc_id or info.get("calc_id")
    if cid is None:
        raise SystemExit(f"set CALC_ID or calc_id in {hd / 'build.json'}")
    ds = read(int(cid))
    lt = ds["full_lt"]
    rl = lt.get_realizations()
    trts = list(lt.gsim_lt.values)
    if "hcurves-rlzs" not in ds:
        raise SystemExit("no hcurves-rlzs in the datastore: set INDIVIDUAL_RLZS = True and rerun")
    rl = sorted(rl, key=lambda x: x.ordinal)
    hc_ = ds["hcurves-rlzs"][:][:, [x.ordinal for x in rl]]
    stats = ds["hcurves-stats"][:] if "hcurves-stats" in ds else None
    r = {"curves": hc_, "imtls": {k: np.asarray(v) for k, v in ds["oqparam"].imtls.items()},
         "lon": ds["sitecol"].lons, "lat": ds["sitecol"].lats, "info": info, "calc_id": int(cid),
         "description": ds["oqparam"].description}
    w = [x.weight[-1] if np.ndim(x.weight) else x.weight for x in rl]
    r["w"] = np.array(w, float) / np.sum(w)
    ds.close()
    if stats is not None:
        mean = np.einsum("r,srml->sml", r["w"], hc_)
        ok = stats[:, 0] > 1e-8
        err = np.max(np.abs(mean[ok] / stats[:, 0][ok] - 1)) if ok.any() else 0.0
        print(f"[check] mean from realizations vs OpenQuake mean: max rel. difference {err:.2e}")
        if err > 1e-3:
            raise RuntimeError("realization curves, weights and OpenQuake mean disagree; do not trust branch plots")
    if r["description"] != info["description"]:
        print(f"[warn] calc {cid} description '{r['description']}' != build '{info['description']}'")

    bmap = info.get("branch_map", {})
    rows, src = [], []
    for x in rl:
        sp = bmap.get(x.sm_lt_path[0], x.sm_lt_path[0])
        src.append(sp)
        row = {}
        for part in sp.split("_x_"):
            fam, var, inner = part.split("-", 2)
            row[f"{fam}:variant"] = var
            for name, tok in zip(AXIS_NAMES.get(fam, []), inner.split("__")):
                row[f"{fam}:{name}"] = tok
        for t, g in zip(trts, x.gsim_rlz.value):
            row[f"gmm:{trt_id(t)}"] = type(g).__name__
        rows.append(row)
    ax = pd.DataFrame(rows)
    r["axes"] = ax[[k for k in ax.columns if ax[k].nunique() > 1]]
    r["src"] = np.array(src)

    st = pd.read_csv(hd / "sites.csv")
    names = info.get("site_names") or [f"s{i:05d}" for i in range(len(st))]
    d2 = [(st["lon"] - a) ** 2 + (st["lat"] - b) ** 2 for a, b in zip(r["lon"], r["lat"])]
    idx = [int(np.argmin(x)) for x in d2]
    off = max(float(np.sqrt(x.min())) for x in d2)
    if len(st) != len(r["lon"]) or off > 0.01:
        raise SystemExit(f"calc {cid} has {len(r['lon'])} sites but {hd / 'sites.csv'} has {len(st)} "
                         f"(largest offset {off:.3f} deg): the job folder was rebuilt after this calc. "
                         "Use the calc run from the current job, or rebuild with the old site list.")
    r["names"] = [names[i] for i in idx]
    return r


def wquant(c, w, q):
    """Weighted quantiles across realizations; c (rlzs, levels)."""
    o = np.argsort(c, axis=0)
    cs = np.cumsum(w[o], axis=0) - 0.5 * w[o]
    s = np.take_along_axis(c, o, axis=0)
    return np.array([[np.interp(qq, cs[:, j], s[:, j]) for j in range(c.shape[1])] for qq in q])


def iml(curve, lv, poe):
    ok = curve > 0
    if ok.sum() < 2 or not curve[ok].min() <= poe <= curve[ok].max():
        return np.nan
    return float(np.exp(np.interp(np.log(poe), np.log(curve[ok][::-1]), np.log(lv[ok][::-1]))))


def tables(r):
    cr, ir, ar = [], [], []
    poes = r["info"]["poes"]
    for m, (imt, lv) in enumerate(r["imtls"].items()):
        for s, name in enumerate(r["names"]):
            c = r["curves"][s, :, m, :]
            mean = r["w"] @ c
            qs = wquant(c, r["w"], QUANTILES)
            for j, l in enumerate(lv):
                cr.append({"site": name, "lon": r["lon"][s], "lat": r["lat"][s], "imt": imt, "iml": l,
                           "mean": mean[j], **{f"q{100 * q:g}": qs[k, j] for k, q in enumerate(QUANTILES)}})
            for p in poes:
                base = iml(mean, lv, p)
                ir.append({"site": name, "lon": r["lon"][s], "lat": r["lat"][s], "imt": imt, "poe": p,
                           "return_period": round(-hc.INV_TIME / np.log(1 - p)), "mean": base,
                           **{f"q{100 * q:g}": iml(qs[k], lv, p) for k, q in enumerate(QUANTILES)}})
                for col in r["axes"]:
                    for v, g in r["axes"].groupby(col).groups.items():
                        k = np.asarray(g)
                        cc = np.average(c[k], axis=0, weights=r["w"][k])
                        x = iml(cc, lv, p)
                        ar.append({"site": name, "imt": imt, "poe": p, "axis": col, "value": v,
                                   "weight": r["w"][k].sum(), "iml": x, "rel": x / base - 1})
    return pd.DataFrame(cr), pd.DataFrame(ir), pd.DataFrame(ar)


def set_style():
    try:
        import seaborn as sns
        sns.set_style("darkgrid", {"ytick.left": True, "xtick.bottom": True, "axes.facecolor": ".9",
                                   "font.family": "Ubuntu"})
    except ImportError:
        plt.style.use("ggplot")


def draw(ax, lv, c, w, color, label, env=True):
    """Weighted mean and envelope of realization curves c (rlzs, levels)."""
    ax.loglog(lv, w @ c / w.sum(), color=color, ls="-", lw=2, label=label)
    if env and len(w) > 1:
        q = wquant(c, w / w.sum(), (QUANTILES[0], QUANTILES[-1]))
        ax.fill_between(lv, q[0], q[1], color=color, alpha=0.3, lw=0)


def finish(ax, imt, title, poes, path, env=True):
    """Limits, target PoE lines, grids, legend and save, as in hazard.plot_pointcurves."""
    ax.set_xlim(XLIMS)
    ax.set_ylim(YLIMS)
    ax.set_title(title, fontsize=16)
    for p in poes:
        pct = 100 * (1 - (1 - p) ** (50 / hc.INV_TIME))
        ax.axhline(p, linestyle="--", linewidth=0.8, color="black")
        ax.text(XLIMS[0] * 1.1, p * 1.1, f"{pct:.0f}% in 50 yr.", fontsize=12)
    ax.set_xlabel(f"{imt} $[g]$", fontsize=14)
    ax.set_ylabel(f"Probability of exceedance - {hc.INV_TIME:g} years", fontsize=14)
    ax.tick_params(which="major", axis="y", length=8, color="gray", width=0.5)
    ax.tick_params(which="minor", axis="y", length=4, color="gray", width=0.5)
    ax.grid(axis="both", which="major", linewidth=1)
    ax.grid(axis="both", which="minor", linewidth=0.4)
    h, lab = ax.get_legend_handles_labels()
    lo = 100 * (QUANTILES[-1] - QUANTILES[0])
    extra = [Line2D([0], [0], color="black", lw=0.5, label="Mean")]
    if env:
        extra.insert(0, Patch(facecolor="0.8", edgecolor="none", alpha=0.5, label=f"{lo:g}% envelope"))
    h += extra
    lab += [x.get_label() for x in extra]
    u = dict(zip(lab, h))
    ax.legend(list(u.values()), list(u.keys()), loc="best", frameon=True)
    ax.get_figure().savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(ax.get_figure())


def fig_curves(r, pd_, name, s):
    """Full model: mean and envelope over all realizations, one figure per IMT."""
    for m, (imt, lv) in enumerate(r["imtls"].items()):
        f, ax = plt.subplots(figsize=(7, 5.5))
        draw(ax, lv, r["curves"][s, :, m, :], r["w"], COLORS[0], "Model")
        finish(ax, imt, name.replace("_", " ").title(), r["info"]["poes"], pd_ / f"{name}_{imt}.png")


def labels(src):
    """Short branch labels: tokens shared by every branch are dropped."""
    tok = [b.replace("_x_", "|").replace("__", "|").split("|") for b in src]
    n = max(len(t) for t in tok)
    tok = [t + [""] * (n - len(t)) for t in tok]
    keep = [j for j in range(n) if len({t[j] for t in tok}) > 1]
    return {b: " ".join(t[j] for j in keep if t[j]) or b for b, t in zip(src, tok)}


def by_branch(r):
    """Weighted mean curve per source branch (collapsed over GMMs): {branch: (weight, curves s,m,l)}."""
    out = {}
    for b in dict.fromkeys(r["src"]):
        k = r["src"] == b
        out[b] = (r["w"][k].sum(), np.einsum("r,srml->sml", r["w"][k] / r["w"][k].sum(), r["curves"][:, k]))
    return out


def fig_branches(r, pd_, name, s):
    """One mean (and envelope over GMMs) per source branch, one figure per IMT."""
    bs = list(dict.fromkeys(r["src"]))
    if len(bs) < 2:
        return
    lab = labels(bs)
    for m, (imt, lv) in enumerate(r["imtls"].items()):
        f, ax = plt.subplots(figsize=(7, 5.5))
        for i, b in enumerate(bs):
            k = r["src"] == b
            draw(ax, lv, r["curves"][s, k, m, :], r["w"][k], COLORS[i % len(COLORS)],
                 f"{lab[b]} (w={r['w'][k].sum():.3g})", env=len(bs) <= MAX_ENVELOPES)
        finish(ax, imt, name.replace("_", " ").title(), r["info"]["poes"], pd_ / f"{name}_{imt}_branches.png")


def compare(runs):
    """Overlay the mean and envelope of several runs per city and IMT; IMLs and ratios to the first run."""
    out = hc.OUT_ROOT / "_compare" / "_vs_".join(j for j, _, _ in runs)
    out.mkdir(parents=True, exist_ok=True)
    rs = [(lab, load(j, cid)) for j, cid, lab in runs]
    names = [n for n in rs[0][1]["names"] if all(n in r["names"] for _, r in rs)]
    rows = []
    for imt, lv in rs[0][1]["imtls"].items():
        for name in names:
            f, ax = plt.subplots(figsize=(7, 5.5))
            for i, (lab, r) in enumerate(rs):
                s, m = r["names"].index(name), list(r["imtls"]).index(imt)
                c = r["curves"][s, :, m, :]
                draw(ax, r["imtls"][imt], c, r["w"], COLORS[i % len(COLORS)], lab)
                for p in r["info"]["poes"]:
                    rows.append({"site": name, "imt": imt, "poe": p, "return_period": round(-hc.INV_TIME / np.log(1 - p)),
                                 "run": lab, "iml": iml(r["w"] @ c, r["imtls"][imt], p)})
            finish(ax, imt, name.replace("_", " ").title(), rs[0][1]["info"]["poes"], out / f"{name}_{imt}.png")
    t = pd.DataFrame(rows)
    piv = t.pivot_table(index=["site", "imt", "return_period"], columns="run", values="iml")[[l for _, _, l in runs]]
    for lab in piv.columns[1:]:
        piv[f"{lab} / {piv.columns[0]}"] = piv[lab] / piv[piv.columns[0]]
    piv.to_csv(out / "compare.csv")
    print(piv.round(4).to_string())
    print(f"wrote {out}")


def contrib(spec):
    """Total curve with its family parts, share of each part at the total's target IMLs, sum check."""
    rate = lambda p: -np.log(1 - np.clip(p, 0, 1 - 1e-12))
    parts = [(lab, load(j, cid)) for j, cid, lab in spec["parts"]]
    if spec["total"]:
        tj, tc, tl = spec["total"]
        tot = load(tj, tc)
    else:
        tj, tl, tot = None, "Sum of parts", parts[0][1]
        for lab, r in parts:
            if any(not np.allclose(r["imtls"][k], v) for k, v in tot["imtls"].items()):
                raise SystemExit(f"{lab}: intensity levels differ from {parts[0][0]}; rates cannot be summed")
    out = hc.OUT_ROOT / "_contrib" / (spec.get("name") or tj)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for m, (imt, lv) in enumerate(tot["imtls"].items()):
        for s, name in enumerate(tot["names"]):
            if tj:
                mt = tot["w"] @ tot["curves"][s, :, m, :]
            else:
                mt = 1 - np.exp(-sum(rate(r["w"] @ r["curves"][r["names"].index(name), :, m, :])
                                     for _, r in parts))
            f, ax = plt.subplots(figsize=(7, 5.5))
            ax.loglog(lv, mt, color="black", lw=2.5, label=tl)
            summed = np.zeros_like(mt)
            for i, (lab, r) in enumerate(parts):
                c = r["w"] @ r["curves"][r["names"].index(name), :, list(r["imtls"]).index(imt), :]
                summed += rate(c)
                ax.loglog(r["imtls"][imt], c, color=COLORS[i % len(COLORS)], lw=2, label=lab)
                for p in tot["info"]["poes"]:
                    x = iml(mt, lv, p)
                    share = rate(np.exp(np.interp(np.log(x), np.log(lv), np.log(np.maximum(c, 1e-30))))) / rate(p)
                    rows.append({"site": name, "imt": imt, "return_period": round(-hc.INV_TIME / np.log(1 - p)),
                                 "iml_total": x, "part": lab, "share_pct": 100 * share})
            ax.loglog(lv, 1 - np.exp(-summed), color="gray", lw=1, ls="--", label="sum of parts")
            finish(ax, imt, name.replace("_", " ").title(), tot["info"]["poes"], out / f"{name}_{imt}.png", env=False)
            ok = mt > 1e-6
            err = np.max(np.abs((1 - np.exp(-summed[ok])) / mt[ok] - 1)) if ok.any() else 0
            if err > 0.05:
                print(f"[check] {name} {imt}: sum of parts differs from total by up to {100 * err:.0f} %")
    t = pd.DataFrame(rows)
    piv = t.pivot_table(index=["site", "imt", "return_period"], columns="part", values="share_pct")
    piv = piv[[lab for _, _, lab in spec["parts"]]]
    piv["sum"] = piv.sum(axis=1)
    piv.insert(0, "iml_total", t.groupby(["site", "imt", "return_period"])["iml_total"].first())
    piv.to_csv(out / "contributions.csv")
    print(piv.round(3).to_string())
    print(f"wrote {out}")
    return piv


def fig_uhs(ir, pd_, name):
    t = ir[(ir["site"] == name) & ir["imt"].str.startswith(("PGA", "SA"))].copy()
    t["T"] = [0.0 if i == "PGA" else float(i[3:-1]) for i in t["imt"]]
    if t["T"].nunique() < 2:
        return
    f, ax = plt.subplots(figsize=(5, 4))
    for i, (rp, g) in enumerate(t.sort_values("T").groupby("return_period")):
        ax.plot(g["T"], g["mean"], "o-", color=COLORS[i % len(COLORS)], lw=2, label=f"{rp} yr")
        ax.fill_between(g["T"], g[f"q{100 * QUANTILES[0]:g}"], g[f"q{100 * QUANTILES[-1]:g}"], color=COLORS[i % len(COLORS)], alpha=0.3, lw=0)
    ax.set_xlabel("period (s)")
    ax.set_ylabel("Sa (g)")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_title(f"{name}: uniform hazard spectra", fontsize=16)
    f.tight_layout()
    f.savefig(pd_ / f"uhs_{name}.png", dpi=200)
    plt.close(f)


def fig_axes(ar, pd_):
    if ar.empty:
        return
    for (imt, p), g in ar.groupby(["imt", "poe"]):
        sites = list(dict.fromkeys(g["site"]))
        axes = list(dict.fromkeys(g["axis"]))
        f, axs = plt.subplots(1, len(sites), figsize=(3 * len(sites), 0.5 * len(axes) + 1.5),
                              sharey=True, squeeze=False)
        for ax, s in zip(axs[0], sites):
            for i, a in enumerate(axes):
                h = g[(g["site"] == s) & (g["axis"] == a)]
                ax.hlines(i, 100 * h["rel"].min(), 100 * h["rel"].max(), color="0.5", lw=3)
                for _, x in h.iterrows():
                    ax.plot(100 * x["rel"], i, "o", ms=4)
                    ax.annotate(str(x["value"]), (100 * x["rel"], i), fontsize=5, rotation=45,
                                xytext=(2, 4), textcoords="offset points")
            ax.axvline(0, color="k", lw=0.8)
            ax.set_title(s, fontsize=9)
            ax.set_xlabel("% vs mean")
        axs[0][0].set_yticks(range(len(axes)))
        axs[0][0].set_yticklabels(axes, fontsize=8)
        rp = round(-hc.INV_TIME / np.log(1 - p))
        f.suptitle(f"branch sensitivity, {imt}, {rp} yr")
        f.tight_layout()
        f.savefig(pd_ / f"axes_{imt}_{rp}yr.png", dpi=200)
        plt.close(f)


def fig_maps(ir, pd_):
    for (imt, rp), g in ir.groupby(["imt", "return_period"]):
        f, ax = plt.subplots(figsize=(5, 9))
        sc = ax.scatter(g["lon"], g["lat"], c=g["mean"], s=6, cmap="viridis")
        f.colorbar(sc, label=f"{imt} (g)")
        ax.set_aspect("equal")
        ax.set_title(f"mean {imt}, {rp} yr")
        f.tight_layout()
        f.savefig(pd_ / f"map_{imt}_{rp}yr.png", dpi=200)
        plt.close(f)


def main():
    set_style()
    if CONTRIB:
        sps, ts = [CONTRIB] if isinstance(CONTRIB, dict) else CONTRIB, []
        for sp in sps:
            try:
                ts.append(contrib(sp).reset_index().assign(split=sp.get("name") or sp["total"][0]))
            except SystemExit as e:
                print(f"[skip] split {sp.get('name')}: {e}")
        sps = [sp for sp in sps if (sp.get("name") or sp["total"][0]) in {x["split"].iloc[0] for x in ts}]
        t = pd.concat(ts, ignore_index=True)
        t.to_csv(hc.OUT_ROOT / "_contrib" / "summary.csv", index=False)
        print("\nPGA at the target PoE per split")
        print(t.pivot_table(index=["site", "return_period"], columns="split", values="iml_total",
                            sort=False)[[sp.get("name") or sp["total"][0] for sp in sps]].round(3).to_string())
        return
    if COMPARE:
        compare(COMPARE)
        return
    r = load(JOB, CALC_ID)
    out = hc.OUT_ROOT / JOB / "post"
    fd = out / "figures"
    fd.mkdir(parents=True, exist_ok=True)
    cr, ir, ar = tables(r)
    cr.to_csv(out / "curves.csv", index=False)
    ir.to_csv(out / "imls.csv", index=False)
    ar.to_csv(out / "axes.csv", index=False)
    print(f"calc {r['calc_id']}: {len(r['names'])} sites, {len(r['w'])} realizations, "
          f"axes {list(r['axes'].columns)}")
    print(ir.round(4).head(20).to_string(index=False))

    bb = by_branch(r)
    lab = labels(list(bb))
    rows = []
    for b, (wb, c) in bb.items():
        for m, (imt, lv) in enumerate(r["imtls"].items()):
            for s, name in enumerate(r["names"]):
                for p in r["info"]["poes"]:
                    rows.append({"branch": b, "label": lab[b], "weight": wb, "site": name, "imt": imt,
                                 "poe": p, "return_period": round(-hc.INV_TIME / np.log(1 - p)),
                                 "iml": iml(c[s, m], lv, p)})
    bt = pd.DataFrame(rows)
    bt.to_csv(out / "branches.csv", index=False)
    print(bt.pivot_table(index=["site", "imt", "return_period"], columns="label", values="iml").round(4).to_string())

    if r["info"]["sites"] == "cities":
        for s, name in enumerate(r["names"]):
            fig_curves(r, fd, name, s)
            fig_branches(r, fd, name, s)
            fig_uhs(ir, fd, name)
        fig_axes(ar, fd)
    else:
        fig_maps(ir, fd)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()