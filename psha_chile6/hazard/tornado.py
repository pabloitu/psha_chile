# One-at-a-time sensitivity of the city PGA to every campaign axis in
# hazard/logic_tree.py (CAMP, CAMP_GMM, AXES).
# Each row changed one family (all three for family "all"); the others stay at
# their reference. Mean curves
# of the three families combine exactly because the logic tree is a product:
#   1 - P_total(x) = prod_f (1 - P_f(x))
# so every row gives the full-model PGA at the target PoE without a full run.
# Outputs: outputs/hazard/_tornado/
#   tornado.csv          PGA and change per site, return period, axis, row
#   tornado_<site>.png   bars sorted by the 475-yr range; filled 475, outline 2475
#   overview.png         largest |change| per axis and city, both return periods

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from hazard import config as hc
from hazard import logic_tree as lt
from hazard.post import load, iml

# settings
OUT = hc.OUT_ROOT / "_tornado"
COLORS = {"interface": "#4c72b0", "intraslab": "#c44e52", "crustal": "#55a868", "all": "0.4"}
SHORT = {**lt.SHORT, "all": "all"}
MIN_RANGE = 1.0     # % ; axes below this at every city are left out of the overview


def curves(job, cache):
    """Mean curves (sites, imts, levels) of a job, None if it has no finished calc."""
    if job not in cache:
        try:
            r = load(job)
        except (SystemExit, FileNotFoundError) as e:
            print(f"[skip] {job}: {e}")
            cache[job] = None
            return None
        cache[job] = {"mean": np.einsum("r,srml->sml", r["w"], r["curves"]), "imtls": r["imtls"],
                      "names": r["names"], "poes": r["info"]["poes"]}
    return cache[job]


def table():
    cache = {}
    ref = {f: curves(f"c_{lt.SHORT[f]}_ref", cache) for f in lt.CAMP}
    miss = [f for f, r in ref.items() if r is None]
    if miss:
        raise SystemExit(f"no reference run for {miss}; run hazard/run_all.sh")
    r0 = ref["interface"]
    for f, r in ref.items():
        if r["names"] != r0["names"] or any(not np.allclose(r["imtls"][k], v) for k, v in r0["imtls"].items()):
            raise SystemExit(f"c_{lt.SHORT[f]}_ref: sites or levels differ from the interface reference")
    surv = {f: 1 - r["mean"] for f, r in ref.items()}
    tot = 1 - np.prod(list(surv.values()), axis=0)
    rows = []
    for m, (imt, lv) in enumerate(r0["imtls"].items()):
        for s, name in enumerate(r0["names"]):
            for p in r0["poes"]:
                rp = round(-hc.INV_TIME / np.log(1 - p))
                x0 = iml(tot[s, m], lv, p)
                for fam, ax, rs in lt.AXES:
                    fams = list(lt.CAMP) if fam == "all" else [fam]
                    for row in rs:
                        cs = [curves(f"c_{lt.SHORT[f]}_{row}", cache) for f in fams]
                        if any(c is None for c in cs):
                            continue
                        sv = {**{g: surv[g][s, m] for g in surv}, **{f: 1 - c["mean"][s, m] for f, c in zip(fams, cs)}}
                        x = iml(1 - np.prod(list(sv.values()), axis=0), lv, p)
                        rows.append({"site": name, "imt": imt, "return_period": rp, "family": fam, "axis": ax,
                                     "row": row, "iml_ref": x0, "iml": x, "rel_pct": 100 * (x / x0 - 1)})
    return pd.DataFrame(rows)


def bars(t):
    """Range per axis: low and high change (reference counts as 0) and the rows that set them."""
    out = []
    for (site, imt, rp, fam, ax), g in t.groupby(["site", "imt", "return_period", "family", "axis"], sort=False):
        lo, hi = g.loc[g["rel_pct"].idxmin()], g.loc[g["rel_pct"].idxmax()]
        out.append({"site": site, "imt": imt, "return_period": rp, "family": fam, "axis": ax,
                    "iml_ref": g["iml_ref"].iloc[0], "lo": min(lo["rel_pct"], 0.0), "hi": max(hi["rel_pct"], 0.0),
                    "row_lo": lo["row"], "row_hi": hi["row"]})
    b = pd.DataFrame(out)
    b["range"] = b["hi"] - b["lo"]
    return b


def fig_site(b, site, imt, path):
    g = b[(b["site"] == site) & (b["imt"] == imt)]
    rps = sorted(g["return_period"].unique())
    g0 = g[g["return_period"] == rps[0]].sort_values("range")
    order = list(g0["family"] + " | " + g0["axis"])
    f, ax = plt.subplots(figsize=(8.5, 0.34 * len(order) + 1.6))
    for k, rp in enumerate(rps):
        h = g[g["return_period"] == rp]
        h = h.set_index(h["family"] + " | " + h["axis"]).reindex(order)
        y = np.arange(len(order)) + (0.18 if k == 0 else -0.18)
        col = [COLORS[x] for x in h["family"]]
        ax.barh(y, h["hi"] - h["lo"], 0.34, left=h["lo"], color=col if k == 0 else "none",
                edgecolor=col, lw=1.2)
        if k == 0:
            for yy, (_, r) in zip(y, h.iterrows()):
                if r["hi"] > 0.5:
                    ax.text(r["hi"], yy, f" {r['row_hi']}", va="center", fontsize=6)
                if r["lo"] < -0.5:
                    ax.text(r["lo"], yy, f"{r['row_lo']} ", va="center", ha="right", fontsize=6)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels([f"{SHORT[o.split(' | ')[0]]}: {o.split(' | ')[1]}" for o in order], fontsize=8)
    ax.set_xlabel(f"change of {imt} vs reference (%)")
    ref = ", ".join(f"{rp} yr {g[g['return_period'] == rp]['iml_ref'].iloc[0]:.2f} g" for rp in rps)
    ax.set_title(f"{site.replace('_', ' ')}: reference {ref}\nfilled {rps[0]} yr, outline {rps[-1]} yr",
                 fontsize=10)
    ax.legend(handles=[Patch(color=c, label=k) for k, c in COLORS.items()], fontsize=7, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    f.tight_layout()
    f.savefig(path, dpi=220)
    plt.close(f)


def fig_overview(b, imt, path):
    g = b[b["imt"] == imt].copy()
    g["key"] = g["family"] + " | " + g["axis"]
    g["amax"] = np.maximum(-g["lo"], g["hi"])
    keep = g.groupby("key")["amax"].max()
    keep = keep[keep >= MIN_RANGE].sort_values(ascending=False).index
    sites = [s for s in hc.CITIES if s in set(g["site"])]
    rps = sorted(g["return_period"].unique())
    f, axs = plt.subplots(1, len(rps), figsize=(1.0 * len(sites) * len(rps) + 5, 0.32 * len(keep) + 2),
                          sharey=True)
    for ax, rp in zip(np.atleast_1d(axs), rps):
        m = g[g["return_period"] == rp].pivot_table(index="key", columns="site", values="amax").reindex(
            index=keep, columns=sites)
        im = ax.imshow(m.to_numpy(), cmap="Reds", vmin=0, vmax=max(20.0, np.nanmax(m.to_numpy())), aspect="auto")
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                v = m.iat[i, j]
                if np.isfinite(v):
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6,
                            color="white" if v > 15 else "black")
        ax.set_xticks(range(len(sites)))
        ax.set_xticklabels([s.replace("_", " ") for s in sites], rotation=60, ha="right", fontsize=7)
        ax.set_title(f"largest |change| of {imt}, {rp} yr (%)", fontsize=10)
    a0 = np.atleast_1d(axs)[0]
    a0.set_yticks(range(len(keep)))
    a0.set_yticklabels([f"{SHORT[k.split(' | ')[0]]}: {k.split(' | ')[1]}" for k in keep], fontsize=7)
    f.colorbar(im, ax=axs, shrink=0.6)
    f.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t = table()
    t.to_csv(OUT / "tornado.csv", index=False)
    b = bars(t)
    b.to_csv(OUT / "bars.csv", index=False)
    for imt in b["imt"].unique():
        for site in b["site"].unique():
            fig_site(b, site, imt, OUT / f"tornado_{site}_{imt}.png")
        fig_overview(b, imt, OUT / f"overview_{imt}.png")
    b0 = b[b["return_period"] == b["return_period"].min()]
    top = b0.sort_values("range", ascending=False).groupby("site", sort=False).head(3)
    print(f"three largest axes per city, {b0['return_period'].iloc[0]} yr (% change of the city value)")
    print(top.set_index(["site", "family", "axis"]).loc[[s for s in hc.CITIES if s in set(top["site"])]]
          [["lo", "hi", "row_lo", "row_hi"]].round(1).to_string())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()