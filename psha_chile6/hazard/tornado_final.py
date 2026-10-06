# Final one-at-a-time sensitivity (hazard/logic_tree.py TORN, AXES_T). Each row changed one
# family on the reference; the families combine exactly in rate space, so every row gives the
# full-model PGA at the target PoE. Effect = change of PGA against the reference, or against
# the axis' base row (coupling against the geodetic row, segment Mmax against the segmented row).
# Outputs: outputs/hazard/rock800_tornado/_tornado/
#   tornado.csv              site, family, axis, row, set, iml_ref, iml, rel_pct
#   bars.csv                 per site and axis: lo, hi, range, rows at the ends, set, paper label
#   summary.txt              axes ranked by their largest range, verdict (>= 5 % at some city), per set
#   t_<city>.png             collaborator figure: every axis, one bar per axis, dots per row
#   t_overview.png           collaborator heat map: largest |change| per axis and city
#   paper_<city>.png         presentation figure (16:9): set C only, paper labels, grouped by family
#   paper_overview.png       presentation heat map: set C, paper labels
# Run: TORNADO=1 python hazard/tornado_final.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import paths
from hazard import config as hc
from hazard import logic_tree as lt
from hazard import post

OUT = hc.OUT_ROOT / "_tornado"
IMT = "PGA"
POE = 0.002105
MIN = 5.0
FAM = {"interface": "interface", "intraslab": "in-slab", "crustal": "crustal"}
COL = {**{k: paths.palette.FAMILY[v] for k, v in FAM.items()}, "all": "0.35"}
SHORT = {**lt.SHORT, "all": "all"}


def curves(job, cache):
    """Mean curve (sites, levels) of one job at IMT, or None when the calc is missing."""
    if job not in cache:
        try:
            r = post.load(job)
        except SystemExit as e:
            print(f"[skip] {job}: {e}")
            cache[job] = None
            return None
        m = list(r["imtls"]).index(IMT)
        cache[job] = {"mean": np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :].astype(float)),
                      "lv": r["imtls"][IMT], "names": r["names"]}
    return cache[job]


def rate(p):
    return -np.log(1 - np.clip(p, 0, 1 - 1e-12))


def table():
    cache = {}
    ref = {f: curves(f"t_{lt.SHORT[f]}_ref", cache) for f in lt.TORN}
    miss = [f for f, r in ref.items() if r is None]
    if miss:
        raise SystemExit(f"no reference run for {miss}; run TORNADO=1 bash hazard/run_all.sh")
    names, lv = ref["interface"]["names"], ref["interface"]["lv"]
    rt = {f: rate(r["mean"]) for f, r in ref.items()}
    rows = []
    for fam, axis, rws, st, paper, base in lt.AXES_T:
        fams = list(lt.TORN) if fam == "all" else [fam]
        if base is None:
            tb = {f: rt[f] for f in fams}
        else:
            cb = curves(f"t_{lt.SHORT[fam]}_{base}", cache)
            if cb is None:
                continue
            tb = {fam: rate(cb["mean"])}
        for row in rws:
            cs = {f: curves(f"t_{lt.SHORT[f]}_{row}", cache) for f in fams}
            if any(c is None for c in cs.values()):
                continue
            for s, name in enumerate(names):
                r0 = sum(tb[f][s] if f in tb else rt[f][s] for f in lt.TORN)
                r1 = sum(rate(cs[f]["mean"][s]) if f in cs else rt[f][s] for f in lt.TORN)
                x0, x = post.iml(1 - np.exp(-r0), lv, POE), post.iml(1 - np.exp(-r1), lv, POE)
                rows.append({"site": name, "family": fam, "axis": axis, "row": row, "set": st, "paper": paper or "",
                             "base": base or "", "iml_ref": x0, "iml": x, "rel_pct": 100 * (x / x0 - 1)})
    return pd.DataFrame(rows), names


def bars(t):
    out = []
    for (site, fam, axis), g in t.groupby(["site", "family", "axis"], sort=False):
        lo, hi = g.loc[g["rel_pct"].idxmin()], g.loc[g["rel_pct"].idxmax()]
        out.append({"site": site, "family": fam, "axis": axis, "set": g["set"].iloc[0], "paper": g["paper"].iloc[0],
                    "iml_ref": g["iml_ref"].iloc[0], "lo": min(lo["rel_pct"], 0.0), "hi": max(hi["rel_pct"], 0.0),
                    "row_lo": lo["row"], "row_hi": hi["row"]})
    b = pd.DataFrame(out)
    b["range"] = b["hi"] - b["lo"]
    b["amax"] = np.maximum(-b["lo"], b["hi"])
    return b


LABEL = {"gmm_ag": "AG20", "gmm_pk": "Parker", "gmm_ku": "Kuehn", "gmm_mv": "Montalva", "gmm_ask": "ASK14",
         "gmm_bssa": "BSSA14", "gmm_cb": "CB14", "gmm_cy": "CY14", "seg": "segmented", "geo": "geodetic",
         "geo_lo": "0.7", "geo_hi": "0.9", "ab_p05": "5th", "ab_p95": "95th", "tgr": "truncated",
         "corner_lo": "9.1", "corner_hi": "10.1", "mmax_m02": "-0.2", "mmax_p02": "+0.2", "mmax_area": "area",
         "ztop5": "5 km", "zbot60": "60 km", "msr_tmg": "Thingbaijam", "msr_ah": "Allen & Hayes", "asp20": "2",
         "floor_m02": "-0.2", "floor_p02": "+0.2", "mc_m01": "-0.1", "mc_p01": "+0.1", "pad0": "0", "pad04": "0.4",
         "b_separate": "separate", "nn10": "10", "nn50": "50", "classmask": "cut", "nofaults": "no faults",
         "only_al1": "AL-I", "only_al2": "AL-II", "only_al3": "AL-III", "only_yc": "YC", "only_tap": "tapered", "only_hyb": "hybrid",
         "multi05": "f = 0.5",
         "only_mobs": "observed", "only_mwc": "WC94", "only_mleo": "Leonard", "only_phi060": "0.6", "only_phi100": "1.0",
         "depth10": "10 km", "depth30": "30 km", "msr_leonard": "Leonard", "cap65": "6.5", "margin0": "0", "margin10": "10 km",
         "mmax75": "7.5", "backarc_borrow": "borrowed", "patagonia_own": "own", "intraarc_floor50": "5.0",
         "no_exclude": "off", "trunc25": "2.5", "trunc40": "4.0"}


def label(row):
    return LABEL.get(row, row)


def fig_city(t, b, site, path, sets, labels, title, size, fs):
    g = b[(b["site"] == site) & b["set"].isin(sets)].copy()
    if not len(g):
        return
    g["name"] = [labels.get((f, a), a) for f, a in zip(g["family"], g["axis"])]
    g = g.sort_values("range")
    f, ax = plt.subplots(figsize=size)
    for i, (_, r) in enumerate(g.iterrows()):
        ax.barh(i, r["hi"] - r["lo"], left=r["lo"], height=0.6, color=COL[r["family"]], alpha=0.8)
        q = t[(t["site"] == site) & (t["family"] == r["family"]) & (t["axis"] == r["axis"])]
        for x, h in q.groupby(q["rel_pct"].round(1)):
            ax.plot(x, i, "o", color="k", ms=4)
            ax.annotate(", ".join(label(v) for v in h["row"]), (x, i), xytext=(0, 7), textcoords="offset points",
                        ha="center", fontsize=fs - 3)
    ax.axvline(0, color="k", lw=0.8)
    ax.axvspan(-MIN, MIN, color="0.5", alpha=0.12, lw=0)
    lim = max(MIN, g["amax"].max()) * 1.25 + 1
    ax.set_xlim(-lim, lim)
    ax.set_yticks(range(len(g)))
    ax.set_yticklabels(g["name"], fontsize=fs - 1)
    ax.set_xlabel(f"Change of {IMT} 475 yr against the reference $[\\%]$", fontsize=fs)
    ax.set_title(f"{title}: reference {g['iml_ref'].iloc[0]:.2f} g", fontsize=fs + 2)
    fams = {k: v for k, v in {**FAM, "all": "all families"}.items() if k in set(g["family"])}
    ax.legend(handles=[Patch(color=COL[k], alpha=0.8, label=v) for k, v in fams.items()], loc="lower right",
              frameon=True, fontsize=fs - 2)
    f.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(f)


def fig_overview(b, names, path, sets, labels, title, size, fs):
    g = b[b["set"].isin(sets)].copy()
    g["key"] = [labels.get((f, a), f"{SHORT[f]}: {a}") for f, a in zip(g["family"], g["axis"])]
    m = g.pivot_table(index="key", columns="site", values="amax").reindex(columns=names)
    m = m.loc[m.max(axis=1).sort_values(ascending=False).index]
    f, ax = plt.subplots(figsize=size)
    im = ax.imshow(m.to_numpy(), cmap="Reds", vmin=0, vmax=max(20.0, np.nanmax(m.to_numpy())), aspect="auto")
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.iat[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=fs - 2, color="white" if v > 15 else "black")
    ax.grid(False)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([n.replace("_", " ").title() for n in names], rotation=45, ha="right", fontsize=fs - 1)
    ax.set_yticks(range(len(m)))
    ax.set_yticklabels(m.index, fontsize=fs - 1)
    ax.set_title(title, fontsize=fs + 2)
    cb = f.colorbar(im, ax=ax, shrink=0.6)
    cb.set_label(f"largest change of {IMT} 475 yr (%)", fontsize=fs - 1)
    f.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(f)


def main():
    post.set_style()
    OUT.mkdir(parents=True, exist_ok=True)
    t, names = table()
    t.to_csv(OUT / "tornado.csv", index=False)
    b = bars(t)
    b.to_csv(OUT / "bars.csv", index=False)

    top = b.groupby(["set", "family", "axis"], sort=False).agg(range_max=("range", "max"), amax=("amax", "max"),
                                                                city=("range", lambda x: b.loc[x.idxmax(), "site"]))
    top["verdict"] = np.where(top["range_max"] >= MIN, ">= 5 %", "< 5 %")
    top = top.sort_values("range_max", ascending=False)
    lines = [f"reference PGA 475 yr (g): " + ", ".join(f"{n} {v:.3f}" for n, v in b.groupby('site', sort=False)['iml_ref'].first().items()),
             "", "axes ranked by the largest range over the cities (set A criterion, B collaborators, C paper):",
             top.round(1).to_string(), "", "rows missing (no finished calc):"]
    done = {(f, r) for f, r in zip(t["family"], t["row"])}
    miss = [f"t_{SHORT[f]}_{r}" for f, _, rs, *_ in lt.AXES_T for r in rs if (f, r) not in done]
    lines.append(", ".join(miss) if miss else "none")
    (OUT / "summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    labels_all = {(f, a): f"{SHORT[f]}: {a}" for f, a, *_ in lt.AXES_T}
    labels_paper = {(f, a): p for f, a, _, _, p, _ in lt.AXES_T if p}
    for name in names:
        city = name.replace("_", " ").title()
        fig_city(t, b, name, OUT / f"t_{name}.png", ("A", "B", "C"), labels_all, city, (12, 14), 11)
        fig_city(t, b, name, OUT / f"paper_{name}.png", ("C",), labels_paper, city, (16, 9), 15)
    fig_overview(b, names, OUT / "t_overview.png", ("A", "B", "C"), labels_all, f"Largest change of {IMT} 475 yr, every axis", (18, 16), 11)
    fig_overview(b, names, OUT / "paper_overview.png", ("C",), labels_paper, f"Largest change of {IMT} 475 yr", (16, 9), 14)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
