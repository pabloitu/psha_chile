"""C8: check figures of the classification, the band measurement (Q-69) and the comparison with psha_chile8 17g.

Usage: python -m psha9.catalog.class_figs run_dir
"""
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import classify as C
from .figs import MERC, PC, basemap, save
from .match import CFG, ROOT

K = CFG["class_checks"]
# class colours and names of psha_chile8 palette.py (D-FIG-01), until FIG ports it to psha9.common.plots
CLASS = {"interface": ("interface", "#4682b4"), "antarctic_interface": ("Antarctic interface", "#9dc3e0"),
         "intraslab_shallow": ("in-slab, shallow", "#b23a3a"), "intraslab_intermediate": ("in-slab, intermediate depth", "#7f1d1d"),
         "jujuy_nest": ("Jujuy nest", "#4a0f0f"), "deep_focus": ("in-slab, deep focus", "#8c7b75"),
         "forearc": ("crustal, forearc", "#e8c21c"), "arc": ("crustal, arc", "#5e7a2a"), "backarc": ("crustal, backarc", "#a3b81f"),
         "patagonia": ("crustal, Patagonia", "#6b4423"), "outside": ("crustal, outside the area", "#c8cdbf"),
         "outer_rise": ("outer rise", "#85638e"), "split": ("shared between classes", "#9e9e9e"),
         "non_earthquake": ("non-earthquake", "#111111")}
FAMILY = {"interface": "#4682b4", "in-slab": "#7f1d1d", "crustal": "#5e7a2a", "outer rise": "#85638e"}
WCOL = dict(zip(FAMILY, C.COLS))


def show(o):
    """One label per event: the sub-class of the class with weight 1, else split."""
    return np.select([o.cls == "interface", o.cls == "in-slab", o.cls == "crustal", o.cls == "outer rise", o.cls == "non-earthquake"],
                     [o.sub_interface, o.sub_inslab, o.sub_crustal, "outer_rise", "non_earthquake"], "split")


def rsd(v):
    return 1.4826 * np.median(np.abs(v - np.median(v)))


# band around the slab top (Q-69)
def band(c):
    """
    Offset and width of the interface band from interface-like thrusts (mechanism misfit <= 1) with a measured depth
    over the slab top down to interface.top: d = depth − Slab2 top.

    Per subset: offset = median of d; spread = robust sd of d; width w = sqrt(spread² − mean σ²), the spread with the
    depth errors removed; 5th and 95th percentiles from a bootstrap over events.

    Returns the table and the events (with `best`, the calibrated and depth-phase depths).
    """
    k = (c.mw >= K["m_min"] - 0.05) & c.depth_kind.eq("measured") & ~c.sea & c.top.le(C.SI["top"]) & c.mech_m.le(1) & c.nonquake.eq("")
    x = c[k].assign(best=lambda d: d.depth_src.isin(K["best"]))
    seg = K["segments"]
    sub = [("all", x.lat < 90)] + [(f"{-a:g}–{-b:g}° S", (x.lat <= a) & (x.lat > b)) for a, b in zip(seg[:-1], seg[1:])] + [
        ("Mw < 5.5", x.mw < 5.45), ("Mw ≥ 5.5", x.mw >= 5.45), ("before 2000", x.time.str[:4].astype(int) < 2000),
        ("from 2000", x.time.str[:4].astype(int) >= 2000), ("slab top ≤ 20 km", x.top <= 20), ("slab top 20–40 km", (x.top > 20) & (x.top <= 40)),
        ("slab top 40–60 km", x.top > 40), ("offshore", x.offshore.astype(bool)), ("onshore", ~x.offshore.astype(bool))]
    rng, rows = np.random.default_rng(1), []
    for dep, kb in (("best depths", x.best), ("all depths", x.lat < 90)):
        for name, q in sub:
            y = x[q & kb]
            if len(y) < 15:
                continue
            d, s2 = y.d.to_numpy(), (y.depth_sigma.to_numpy() ** 2)
            w = lambda dd, ss: np.sqrt(max(rsd(dd) ** 2 - ss.mean(), 0.0))
            j = rng.integers(0, len(y), (K["n_boot"], len(y)))
            bo, bw = np.median(d[j], 1), np.array([w(d[i], s2[i]) for i in j])
            rows.append({"depths": dep, "subset": name, "n": len(y), "offset": np.median(d), "offset_p05": np.percentile(bo, 5),
                         "offset_p95": np.percentile(bo, 95), "spread": rsd(d), "median_sigma": np.median(np.sqrt(s2)), "w": w(d, s2),
                         "w_p05": np.percentile(bw, 5), "w_p95": np.percentile(bw, 95), "within_15": np.mean(np.abs(d) <= 15),
                         "p05_d": np.percentile(d, 5), "p95_d": np.percentile(d, 95)})
    return pd.DataFrame(rows).round(2), x


def fig_band(run, t, x):
    fig, ax = plt.subplots(1, 3, figsize=(9.2, 2.7))
    b = np.arange(-50, 51, 2.5)
    col = CLASS["interface"][1]
    ax[0].hist(x.d, b, color=col, alpha=0.45, label=f"interface-like thrusts, all depths ({len(x)})")
    ax[0].hist(x.d[x.best], b, color="#08306b", label=f"calibrated or depth-phase depths ({int(x.best.sum())})")
    for s in (-1, 1):
        ax[0].axvline(C.SI["offset"] + s * C.SI["w"], color="k", lw=0.8, ls="--")
    ax[0].set(xlabel="depth − Slab2 top (km; positive below)", ylabel="events")
    ax[0].set_ylim(0, 1.3 * ax[0].get_ylim()[1])
    ax[0].legend(frameon=False, fontsize=5, loc="upper left")
    y = x[x.best]
    ax[1].scatter(y.top, y.d, s=2 * 3.5 ** (y.mw - 4.5), color="#08306b", alpha=0.5, lw=0)
    e = np.arange(0, 61, 10.0)
    md = [y.d[(y.top > a) & (y.top <= a + 10)].median() if ((y.top > a) & (y.top <= a + 10)).sum() >= 10 else np.nan for a in e[:-1]]
    ax[1].plot(e[:-1] + 5, md, color="#e6550d", lw=1.5, marker="o", ms=3)
    for s in (-1, 1):
        ax[1].axhline(C.SI["offset"] + s * C.SI["w"], color="k", lw=0.8, ls="--")
    ax[1].set(xlabel="Slab2 top at the epicentre (km)", ylabel="depth − Slab2 top (km)", ylim=(45, -45))
    q = t[(t.depths == "best depths")].reset_index(drop=True)
    yy = np.arange(len(q))[::-1]
    ax[2].errorbar(q.offset, yy, xerr=[q.offset - q.offset_p05, q.offset_p95 - q.offset], fmt="o", ms=3, color="#e6550d", lw=1, label="offset (median)")
    ax[2].barh(yy, 4 * q.w, left=q.offset - 2 * q.w, height=0.5, color=col, alpha=0.45, label="offset ± 2 w")
    for s in (-1, 1):
        ax[2].axvline(C.SI["offset"] + s * C.SI["w"], color="k", lw=0.8, ls="--")
    ax[2].set_yticks(yy, [f"{a} ({n})" for a, n in zip(q.subset, q.n)], fontsize=5)
    ax[2].set(xlabel="depth − Slab2 top (km)", xlim=(-30, 30))
    ax[2].legend(frameon=False, fontsize=5, loc="lower right")
    fig.tight_layout()
    save(fig, run / "figs" / "class_band.png")


# check figures
def fig_map(run, c):
    """Events of Mw >= 4.5 by class (the sub-class of the weight-1 class; shared events grey), north and south
    panels, with the western edge and the crustal area."""
    c = c[c.mw >= K["m_min"] - 0.05].assign(show=lambda d: show(d)).sort_values("mw")
    sh = C.shapes()
    ar = np.array(sh["area"].exterior.coords)
    fig = plt.figure(figsize=(6.9, 6.6))
    for i, ext in enumerate([(-76.5, -63, -36, -15.5), (-76.5, -63, -56.5, -36)]):
        ax = fig.add_axes([0.04 + 0.49 * i, 0.12, 0.45, 0.87], projection=MERC)
        ax.set_extent(ext, crs=PC)
        basemap(ax, ext)
        g = ax.gridlines(draw_labels=True, lw=0.2, color="w", alpha=0.6)
        g.top_labels = g.right_labels = False
        ax.plot(sh["edge"][:, 0], sh["edge"][:, 1], color="k", lw=0.8, transform=PC, zorder=2)
        ax.plot(ar[:, 0], ar[:, 1], color="#5e7a2a", lw=0.6, transform=PC, zorder=2)
        ax.scatter(c.lon, c.lat, s=2 * 3.5 ** (c.mw - 4.5), c=c.show.map(lambda k: CLASS[k][1]), alpha=0.55, lw=0.15, edgecolor="#333",
                   transform=PC, zorder=3)
    n = c.show.value_counts()
    h = [plt.scatter([], [], s=14, color=v[1], label=f"{v[0]} ({n[k]:,})") for k, v in CLASS.items() if k in n]
    h += [plt.Line2D([], [], color="k", lw=0.8, label="western edge"), plt.Line2D([], [], color="#5e7a2a", lw=0.6, label="crustal area")]
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False, fontsize=5.5)
    save(fig, run / "figs" / "class_map.png")


def fig_depth(run, c):
    """Q-46: depth below the slab top per range of slab-top depth: summed class weights, weight-1 events only, and
    the events with a mechanism (interface-like or not). Measured depths, Mw >= 4.5, not outer rise."""
    x = c[(c.mw >= K["m_min"] - 0.05) & c.depth_kind.eq("measured") & c.top.notna() & ~c.sea & c.nonquake.eq("")]
    tops, b = K["tops"], np.arange(-60, 101, 5.0)
    fam = [f for f in FAMILY if f != "outer rise"]
    fig, ax = plt.subplots(3, len(tops) - 1, figsize=(9.5, 5.0), sharex=True)
    for j, (a, z) in enumerate(zip(tops[:-1], tops[1:])):
        y = x[(x.top > a) & (x.top <= z)]
        ax[0, j].hist([y.d] * 3, b, weights=[y[WCOL[f]] for f in fam], stacked=True, color=[FAMILY[f] for f in fam], label=fam)
        one = y[y.cls != "split"]
        ax[1, j].hist([one.d] * 3, b, weights=[one[WCOL[f]] for f in fam], stacked=True, color=[FAMILY[f] for f in fam])
        m = y[y.mech_m.notna()]
        ax[2, j].hist([m.d[m.mech_m <= 1], m.d[m.mech_m > 1]], b, stacked=True, color=[FAMILY["interface"], "#999999"],
                      label=["interface-like mechanism", "other mechanism"])
        ax[0, j].text(0.04, 0.94, f"slab top {a}–{z} km", transform=ax[0, j].transAxes, va="top")
        for r in range(3):
            ax[r, j].axvline(0, color="k", lw=0.6)
        ax[2, j].set_xlabel("depth − Slab2 top (km)")
    for r, lab in enumerate(("summed weights", "weight-1 events", "events with a mechanism")):
        ax[r, 0].set_ylabel(lab)
    h = ax[0, 0].get_legend_handles_labels()[0] + ax[2, 0].get_legend_handles_labels()[0][1:]
    fig.legend(h, fam + ["other mechanism"], loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout()
    save(fig, run / "figs" / "class_depth.png")


def fig_shares(run, c, tab):
    """Class shares of the events without a measured depth: the bins (slab top, latitude, magnitude) as stacked
    bars, with the number of classified events behind each and of events that take the shares."""
    fig, ax = plt.subplots(1, tab.slab_top.nunique(), figsize=(9.0, 2.8), sharey=True)
    nd = c[(c.rule == "nodepth_share") & (c.mw >= K["m_min"] - 0.05)]
    for a, (top, t) in zip(ax, tab.groupby("slab_top", sort=False)):
        t = t.reset_index(drop=True)
        y, left = np.arange(len(t))[::-1], np.zeros(len(t))
        for f, col in (("interface", FAMILY["interface"]), ("inslab", FAMILY["in-slab"]), ("crustal", FAMILY["crustal"])):
            a.barh(y, t[f].fillna(0), left=left, color=col, height=0.75, label=f.replace("inslab", "in-slab"))
            left += t[f].fillna(0).to_numpy()
        for yy, r in zip(y, t.itertuples()):
            a.text(1.02, yy, f"{r.n_used}{'*' if r.borrowed else ''}", va="center", fontsize=5)
        a.set_yticks(y, t.lat + ", " + t.mag, fontsize=5)
        a.set(xlim=(0, 1.15), xlabel="share")
        a.text(0.02, 1.02, f"slab top {top}", transform=a.transAxes)
        a.grid(False)
    ax[0].legend(frameon=False, fontsize=5, ncol=3, loc="lower left", bbox_to_anchor=(0, -0.35))
    fig.text(0.99, -0.08, f"right of the bars: classified events used (*: borrowed from other bins); {len(nd)} events of Mw ≥ {K['m_min']} take these shares",
             ha="right", fontsize=5)
    save(fig, run / "figs" / "class_shares.png")


# comparison with 17g
def compare(run, c):
    """Class totals by family and Mw band in the 17g domain (each catalogue with its own Mw; and the events in both
    with the new Mw, which shows the classification alone), and the events of Mw >= 4.5 whose class changed (another
    weight-1 class, or a weight changed by 0.2 or more)."""
    o = pd.read_csv(ROOT / C.S["compare"], low_memory=False)
    o = o[o.in_domain & (o.mw >= K["m_min"] - 0.05)]
    n = c[c.in_domain_17g & (c.mw >= K["m_min"] - 0.05)]
    bd = K["bands"]
    lab = [f"{a}–{b}" if b < 10 else f"≥ {a}" for a, b in zip(bd, bd[1:])]
    tot = lambda d, cols: d.groupby(pd.cut(d.mw + 0.05, bd, right=False, labels=lab), observed=False)[cols].sum()
    cols = C.COLS[:4]
    t = pd.concat({"17g": tot(o, cols), run.name: tot(n, cols)}, axis=1).round(1)
    j = o.merge(n, on="event_id", suffixes=("_17g", ""))
    same = pd.concat({"17g": tot(j, [k + "_17g" for k in cols]).set_axis(cols, axis=1), run.name: tot(j, cols)}, axis=1).round(1)
    same[("events", "n")] = j.groupby(pd.cut(j.mw + 0.05, bd, right=False, labels=lab), observed=False).size()
    t[("17g", "events")] = o.groupby(pd.cut(o.mw + 0.05, bd, right=False, labels=lab), observed=False).size()
    t[(run.name, "events")] = n.groupby(pd.cut(n.mw + 0.05, bd, right=False, labels=lab), observed=False).size()
    dw = np.abs(j[cols].to_numpy() - j[[k + "_17g" for k in cols]].to_numpy()).max(1)
    ch = j[(j.cls != j.cls_17g) | (dw >= 0.2)].assign(dw=dw[(j.cls != j.cls_17g) | (dw >= 0.2)].round(2))
    ch["dkm"] = (111.2 * np.hypot(ch.lat - ch.lat_17g, (ch.lon - ch.lon_17g) * np.cos(np.radians(ch.lat)))).round(1)
    ch = ch[["event_id", "time", "lat", "lon", "mw", "dkm", "depth_17g", "depth", "top", "cls_17g", "cls", "rule_17g", "rule", "dw"]
            + [k + s for k in cols for s in ("_17g", "")]].sort_values("mw", ascending=False)
    t.to_csv(run / "compare_17g_classes.csv")
    same.to_csv(run / "compare_17g_classes_same_events.csv")
    ch.to_csv(run / "compare_17g_class_changed.csv", index=False)
    fig, ax = plt.subplots(1, 2, figsize=(6.9, 2.4), gridspec_kw={"width_ratios": [1.3, 1]})
    x = np.arange(len(lab))
    for i, (f, col) in enumerate(FAMILY.items()):
        r = 100 * (same[(run.name, WCOL[f])] / same[("17g", WCOL[f])] - 1).loc[lab]
        ax[0].bar(x + 0.2 * i - 0.3, r, 0.2, color=col, label=f)
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_xticks(x, [f"Mw {a}" for a in lab])
    ax[0].set(ylabel=f"summed weight, {run.name} against 17g (%)\nsame events, new Mw")
    ax[0].legend(frameon=False, fontsize=5, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.32))
    m = pd.crosstab(ch.cls_17g, ch.cls)
    order = [k for k in ["interface", "in-slab", "crustal", "outer rise", "split"] if k in m.index or k in m.columns]
    m = m.reindex(index=order, columns=order, fill_value=0)
    ax[1].imshow(m, cmap="Greys", vmax=m.to_numpy().max() * 1.5)
    for (a, b), v in np.ndenumerate(m.to_numpy()):
        ax[1].text(b, a, v, ha="center", va="center", fontsize=6, color="#c0141c" if a != b else "#555")
    ax[1].set_xticks(range(len(order)), order, fontsize=5)
    ax[1].set_yticks(range(len(order)), order, fontsize=5)
    ax[1].set(xlabel=run.name, ylabel="17g")
    ax[1].grid(False)
    save(fig, run / "figs" / "compare_17g_classes.png")
    return t, same, ch


def main(run):
    run = ROOT / run
    (run / "figs").mkdir(exist_ok=True)
    c = pd.read_csv(run / "catalog.csv", low_memory=False).merge(pd.read_csv(run / "class_geometry.csv"), on="event_id")
    c["nonquake"] = c.nonquake.fillna("")
    for k in ("sub_interface", "sub_inslab", "sub_crustal"):
        c[k] = c[k].fillna("")
    tab = pd.read_csv(run / "class_shares.csv").fillna({"borrowed": ""})
    t, x = band(c)
    t.to_csv(run / "class_band.csv", index=False)
    fig_band(run, t, x)
    fig_map(run, c[c.in_box])
    fig_depth(run, c)
    fig_shares(run, c, tab)
    tt, ev, ch = compare(run, c)
    pd.set_option("display.width", 250, "display.max_columns", 40)
    print(t.to_string())
    print(tt.to_string())
    print(ev.to_string())
    print("class changed against 17g:", len(ch), "| Mw >= 5.5:", int((ch.mw >= 5.45).sum()), "| Mw >= 7:", int((ch.mw >= 6.95).sum()))


if __name__ == "__main__":
    main(sys.argv[1])
