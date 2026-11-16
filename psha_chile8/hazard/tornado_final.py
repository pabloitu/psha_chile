# One-at-a-time sensitivity per family (hazard/jobs.py ROWS), adapted from psha_chile7 hazard/tornado_final.py. Two
# numbers per row and city: the change of the family's own PGA 475 yr, and the change of the combined PGA 475 yr (the
# references of the families that have run, combined in rate space, the row in place of its family's reference). The
# base of a row is its family reference or the row named in ROWS. Without t_cr_ref the combination is interface +
# in-slab and every output says "without the crustal family".
# Outputs: hazard/out/tornado_if_is/ (interface + in-slab, the S5a numbers) and hazard/out/tornado/ (every family that
# has a reference): tornado.csv, bars.csv, summary.txt, heatmap.png, bars_<city>.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import palette
from pituplots.style.axes import darkgrid
from hazard import combine, post
from hazard import config as hc
from hazard import jobs as J

RUNS = {"tornado_if_is": ["interface", "inslab"], "tornado": ["interface", "inslab", "crustal"]}
IMT = "PGA"
POE = 0.002105
MIN = 5.0
VMAX = 50.0
XMAX = 100.0
REF = {"interface": "t_if_ref", "inslab": "t_is_ref", "crustal": "t_cr_ref"}
NAME = {"interface": "interface", "inslab": "in-slab", "crustal": "crustal"}
COL = {"interface": palette.CLASS_COLOR["interface"], "inslab": palette.CLASS_COLOR["intraslab_intermediate"],
       "crustal": palette.CLASS_COLOR["forearc"]}
FAMS, NOTE, BOTH = list(REF), "", ""


def names(fams):
    global FAMS, NOTE, BOTH
    FAMS = fams
    NOTE = "" if "crustal" in fams else "without the crustal family"
    BOTH = " + ".join(NAME[f] for f in fams)


def curves(job, cache):
    if job not in cache:
        try:
            r = post.load(job)
            cache[job] = post.mean(r, IMT)
            cache["lv"] = r["imtls"][IMT]
        except (SystemExit, FileNotFoundError, KeyError) as e:
            print(f"[skip] {job}: {e}")
            cache[job] = None
    return cache[job]


def table(fams, cache):
    ref = {f: curves(REF[f], cache) for f in fams}
    ref = {f: v for f, v in ref.items() if v is not None}
    if not {"interface", "inslab"} <= set(ref):
        raise SystemExit("interface or in-slab reference missing")
    names(list(ref))
    lv = cache["lv"]
    rt = {f: combine.rate(v) for f, v in ref.items()}
    rows = []
    for job, (fam, axis, lab, base) in J.ROWS.items():
        if fam not in ref:
            continue
        c = curves(job, cache) if "skip" not in J.JOBS[job] else None
        b = ref[fam] if base is None else curves(base, cache)
        if c is None or b is None:
            continue
        oth = sum(rt[f] for f in ref if f != fam)
        for s, name in enumerate(hc.CITIES):
            x0, x = post.iml(b[s], lv, POE), post.iml(c[s], lv, POE)
            y0 = post.iml(1 - np.exp(-(combine.rate(b[s]) + oth[s])), lv, POE)
            y = post.iml(1 - np.exp(-(combine.rate(c[s]) + oth[s])), lv, POE)
            if not np.isfinite(y0):
                continue
            rows.append({"site": name, "family": fam, "axis": axis, "row": lab, "job": job, "base": base or REF[fam],
                         "iml_base_family": x0, "iml_family": x, "family_pct": 100 * (x / x0 - 1),
                         "iml_base_combined": y0, "iml_combined": y, "combined_pct": 100 * (y / y0 - 1)})
    return pd.DataFrame(rows)


def bars(t):
    out = []
    for (site, fam, axis), g in t.groupby(["site", "family", "axis"], sort=False):
        r = {"site": site, "family": fam, "axis": axis}
        for k in ("family", "combined"):
            v = g[f"{k}_pct"].dropna()
            if v.empty:
                r.update({f"{k}_{x}": np.nan for x in ("lo", "hi", "row_lo", "row_hi", "range", "amax")})
                continue
            r.update({f"{k}_lo": min(v.min(), 0.0), f"{k}_hi": max(v.max(), 0.0),
                      f"{k}_row_lo": g.loc[v.idxmin(), "row"], f"{k}_row_hi": g.loc[v.idxmax(), "row"]})
            r[f"{k}_range"] = r[f"{k}_hi"] - r[f"{k}_lo"]
            r[f"{k}_amax"] = max(-r[f"{k}_lo"], r[f"{k}_hi"])
        out.append(r)
    return pd.DataFrame(out)


def label(fam, axis):
    return f"{NAME[fam]}: {axis}"


def fig_city(t, b, site, path):
    g = b[b.site == site].sort_values("combined_amax")
    f, ax = plt.subplots(figsize=(10, 0.42 * len(g) + 1.6), layout="constrained")
    for i, (_, r) in enumerate(g.iterrows()):
        ax.barh(i + 0.17, r.family_hi - r.family_lo, left=r.family_lo, height=0.32, color=COL[r.family], alpha=0.35)
        ax.barh(i - 0.17, r.combined_hi - r.combined_lo, left=r.combined_lo, height=0.32, color=COL[r.family])
        q = t[(t.site == site) & (t.family == r.family) & (t.axis == r.axis)]
        for _, x in q.iterrows():
            ax.plot(x.combined_pct, i - 0.17, "o", color="k", ms=3)
        if len(q) > 1:
            lo, hi = q.combined_pct.idxmin(), q.combined_pct.idxmax()
            for k, ha, dx in ((lo, "right", -5), (hi, "left", 5)):
                ax.annotate(q.loc[k, "row"], (q.loc[k, "combined_pct"], i - 0.17), xytext=(dx, -3),
                            textcoords="offset points", ha=ha, va="center", fontsize=7, color="0.3")
    ax.axvline(0, color="k", lw=0.8)
    ax.axvspan(-MIN, MIN, color="0.5", alpha=0.12, lw=0)
    lim = min(XMAX, max(MIN, np.nanmax(g[["family_amax", "combined_amax"]].to_numpy())) * 1.15 + 1)
    ax.set_xlim(-lim, lim)
    for i, (_, r) in enumerate(g.iterrows()):
        for k, y in (("family", i + 0.17), ("combined", i - 0.17)):
            for v in (r[f"{k}_lo"], r[f"{k}_hi"]):
                if abs(v) > lim:
                    ax.text(np.sign(v) * lim * 0.98, y, f"{v:+.0f} %", ha="right" if v > 0 else "left",
                            va="center", fontsize=8, color="0.15")
    ax.set_ylim(-0.7, len(g) - 0.3)
    ax.set_yticks(range(len(g)))
    ax.set_yticklabels([label(a, x) for a, x in zip(g.family, g.axis)])
    ax.set_xlabel(f"Change of {IMT} 475 yr (%)" + (f", {NOTE}" if NOTE else ""))
    darkgrid(ax)
    ax.legend(handles=[Patch(color="0.35", label=BOTH),
                       Patch(color="0.35", alpha=0.35, label="family alone")],
              loc="lower right", frameon=True, fontsize=9)
    ax.text(0.01, 0.99, f"{site}", transform=ax.transAxes, ha="left", va="top", fontsize=12)
    f.savefig(path, dpi=200, facecolor="white")
    plt.close(f)


def fig_heat(b, path):
    names = [n for n in hc.CITIES if n in set(b.site)]
    fig, axs = plt.subplots(1, 2, figsize=(18, 0.38 * b.groupby(["family", "axis"]).ngroups + 3), layout="constrained",
                            sharey=True)
    b = b.assign(key=[label(f, a) for f, a in zip(b.family, b.axis)])
    order = b.groupby("key").combined_amax.max().sort_values(ascending=False).index
    for ax, k, txt in zip(axs, ("family", "combined"), ("family alone", BOTH)):
        m = b.pivot_table(index="key", columns="site", values=f"{k}_amax").reindex(index=order, columns=names)
        im = ax.imshow(np.minimum(m.to_numpy(), VMAX), cmap="Reds", vmin=0, vmax=VMAX, aspect="auto")
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                v = m.iat[i, j]
                if np.isfinite(v):
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8,
                            color="white" if v > 0.6 * VMAX else "black", fontweight="bold" if v >= MIN else "normal")
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_yticks(range(len(m)))
        ax.set_yticklabels(m.index)
        ax.text(0.0, 1.01, txt, transform=ax.transAxes, ha="left", va="bottom", fontsize=12)
        for s in ax.spines.values():
            s.set_visible(False)
    cb = fig.colorbar(im, ax=axs, shrink=0.5)
    cb.set_label(f"largest |change| of {IMT} 475 yr (%), scale capped at {VMAX:.0f}" + (f", {NOTE}" if NOTE else ""))
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


def main():
    palette.apply()
    cache = {}
    for k, fams in RUNS.items():
        one(hc.OUT / k, fams, cache)


def one(OUT, fams, cache):
    OUT.mkdir(parents=True, exist_ok=True)
    t = table(fams, cache)
    t.to_csv(OUT / "tornado.csv", index=False)
    b = bars(t)
    b.to_csv(OUT / "bars.csv", index=False)
    top = b.groupby(["family", "axis"], sort=False).agg(
        combined_range=("combined_range", "max"), combined_amax=("combined_amax", "max"),
        family_range=("family_range", "max"), family_amax=("family_amax", "max"),
        city=("combined_amax", lambda x: b.loc[x.idxmax(), "site"]))
    top["verdict"] = np.where(top.combined_amax >= MIN, ">= 5 %", "< 5 %")
    top = top.sort_values("combined_amax", ascending=False)
    lines = [f"S5 tornado, {IMT} 475 yr" + (f", {NOTE}." if NOTE else "."),
             f"Reference {BOTH} PGA (g): " + ", ".join(
                 f"{s} {v:.3f}" for s, v in t[t.base.isin(REF.values())].groupby("site", sort=False).iml_base_combined.first().items()),
             "", f"Axes ranked by the largest |change| of the {BOTH} PGA over the cities "
             f"(family = the family's own PGA); verdict on the {BOTH} number:",
             top.round(1).to_string(), "",
             f"Cities left out ({BOTH} PGA 475 yr below the lowest level, 0.005 g): " + ", ".join(
                 n for n in hc.CITIES if n not in set(t.site)) or "none", "", "Rows defined and skipped: " + ", ".join(
                 f"{n} ({J.JOBS[n]['skip']})" for n in J.ROWS if "skip" in J.JOBS[n]),
             "Rows without a finished calc: " + (", ".join(
                 n for n in J.ROWS if J.ROWS[n][0] in FAMS and "skip" not in J.JOBS[n] and n not in set(t.job))
                                                 or "none")]
    (OUT / "summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    fig_heat(b, OUT / "heatmap.png")
    for s in t.site.unique():
        fig_city(t, b, s, OUT / f"bars_{s.replace(' ', '_')}.png")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
