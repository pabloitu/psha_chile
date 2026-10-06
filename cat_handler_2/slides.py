# Presentation figures and the hand-off note of the catalog step, written from
# the run outputs (prepare/, catalog_base.csv, catalog.csv, the old classified
# catalog, the hand-decision CSVs). Run prepare, classify and check first.
# Writes results/cat_handler_2/slides/: 01_pipeline.png .. 12_patagonia.png,
# sections/secNN_<lat>.png (one per transect of sections.pdf), numbers.json,
# and CATALOG_final.md in this package.

import json
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

from cat_handler_2 import check as K
from cat_handler_2 import compare as CP
from cat_handler_2 import config as C
from cat_handler_2 import sources as S

OUT = C.OUT / "slides"
SIZE = (10, 5.6)
DPI = 300
MB = [3.9, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 10.0]
from cat_handler_2 import palette as PAL

FAMC, CLSC, STATC, NAME = PAL.FAMILY, PAL.CLASS, PAL.DEPTH_STATUS, PAL.NAME
CITY_OFF = {"Valparaiso": (-8, 7, "right"), "Santiago": (8, 7, "left")}
# slide sections: extent from the trench (km, negative seaward), depth (km),
# vertical exaggeration; the locator is the whole margin, full height at the right
SLIDE_XMIN, SLIDE_XMAX, SLIDE_ZMAX = -80, 400, 200
SLIDE_VE = 1.6
PAL.apply()


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=DPI)
    plt.close(fig)


def fam_of(cls):
    f = {c: k for k, cs in C.FAMILIES.items() for c in cs}
    return cls.map(f).fillna("excluded")


def basemap(a, lat=(-58.5, -16.5), lon=(-80, -62), cities=True, trench=True, legend=False):
    if trench:
        for name, line in K.trenches().items():
            a.plot(*line.xy, "k-" if name == "nazca" else "k--", lw=1, label="Nazca trench" if name == "nazca" else "Antarctic trench (Bird 2003)")
        _, fp = K.K.footprint()
        a.fill(*fp.exterior.xy, color=CLSC["patagonia_interface"], alpha=0.25, lw=0, label="Antarctic interface band (150 km)")
    if cities:
        for n, (x, y) in C.CITIES.items():
            a.plot(x, y, "k^", ms=5)
            dx, dy, ha = CITY_OFF.get(n, (4, -2, "left"))
            a.annotate(n, (x, y), fontsize=8, xytext=(dx, dy), textcoords="offset points", ha=ha)
    if legend:
        a.legend(fontsize=8, loc="lower left")
    a.set(xlim=lon, ylim=lat, aspect=1 / np.cos(np.radians(np.mean(lat))))
    a.tick_params(labelsize=9)


# figures
def pipeline(n):
    fig, a = plt.subplots(figsize=SIZE)
    a.set(xlim=(0, 10), ylim=(0, 5.6))
    a.axis("off")
    xs = [0.2, 2.7, 5.2, 7.7]
    boxes = [("Cabello et al. (2025)\nintegrated catalog", f"{n['cab_rows']:,} rows\nsouth of {-C.LAT_MAX:.0f} S, M > {C.MMIN}", xs[0], 3.4),
             ("dedup\none row per earthquake", f"{n['events']:,} events\n{n['dup_frac']:.0%} of rows were copies", xs[1], 3.4),
             ("locate\nPotin, depth status", f"{n['potin']:,} relocated here\n{n['filled']:,} depths filled", xs[2], 3.4),
             ("mech\nfocal mechanisms", f"ANSS > GCMT > GEM > Cabello\n{n['with_mech']:,} events, {n['mech_55']:.0%} of M >= 5.5", xs[3], 3.4),
             ("catalog_base.csv", f"{n['events']:,} events\n{n['mag_over']} magnitudes from\nRuiz & Madariaga (2018)", xs[1], 0.6),
             ("classify.py, params.py\nclass_overrides.csv", f"M >= 5.5: interface {n['f55']['interface']}\nin-slab {n['f55']['in-slab']}, "
              f"crustal {n['f55']['crustal']}", xs[2], 0.6),
             ("catalog.csv", f"{n['events']:,} events\n{n['n_class']} classes, 4 families", xs[3], 0.6)]
    for title, txt, x, y in boxes:
        a.add_patch(FancyBboxPatch((x, y), 2.1, 1.6, boxstyle="round,pad=0.05", fc=FAMC["interface"] if "catalog" in title else "#eef3f8",
                                   alpha=0.15 if "catalog" in title else 1, ec="0.3"))
        a.text(x + 1.05, y + 1.3, title, ha="center", va="center", fontsize=10.5, weight="bold")
        a.text(x + 1.05, y + 0.55, txt, ha="center", va="center", fontsize=9.5)
    for x in xs[:3]:
        a.annotate("", (x + 2.5, 4.2), (x + 2.15, 4.2), arrowprops={"arrowstyle": "->", "lw": 1.5})
    for x in xs[1:3]:
        a.annotate("", (x + 2.5, 1.4), (x + 2.15, 1.4), arrowprops={"arrowstyle": "->", "lw": 1.5})
    a.annotate("", (3.75, 2.25), (8.75, 3.35), arrowprops={"arrowstyle": "->", "lw": 1.5, "connectionstyle": "angle,angleA=0,angleB=90"})
    a.text(0.2, 1.4, "frozen sources:\nCabello, Potin (2024),\nGCMT, ANSS ComCat, GEM;\noverrides.csv, additions.csv", fontsize=9.5, va="center")
    a.text(5, 5.35, "cat_handler_2: sources -> catalog_base -> catalog", ha="center", fontsize=13, weight="bold")
    save(fig, "01_pipeline.png")


def duplicates(ev, grp):
    fig, ax = plt.subplots(1, 2, figsize=SIZE)
    bins = np.arange(3.9, 8.6, 0.5)
    extra = grp[~grp["kept"]].groupby(pd.cut(grp.loc[~grp["kept"], "mag_kept"], bins), observed=False).size()
    evn = ev.groupby(pd.cut(ev["mag"], bins), observed=False).size()
    frac = (extra / (evn + extra)).fillna(0)
    ctr = bins[:-1] + 0.25
    ax[0].bar(ctr, frac, width=0.45, color="tab:blue")
    for x, f, e in zip(ctr, frac, evn + extra):
        ax[0].text(x, f + 0.01, f"{e:,}", ha="center", fontsize=8)
    ax[0].set(xlabel="Cabello magnitude", ylabel="share of rows that were copies", title="duplicate rows by magnitude (rows on top)")
    by = grp[grp["mag_kept"] >= 5.5].groupby("grp")["agency"].agg(lambda s: " + ".join(sorted(s))).value_counts().head(8)
    ax[1].barh(by.index[::-1], by.values[::-1], color="tab:gray")
    ax[1].set(title="what a merged group is made of (M >= 5.5)", xlabel="groups")
    ax[1].tick_params(axis="y", labelsize=8)
    save(fig, "02_duplicates.png")
    return frac


def depth_status(el):
    fig, ax = plt.subplots(1, 2, figsize=SIZE, sharey=True)
    bins = np.arange(0, 301, 5)
    z0 = pd.to_numeric(el["depth_orig"], errors="coerce")
    z1 = pd.to_numeric(el["depth"], errors="coerce")
    ax[0].hist(z0.dropna(), bins=bins, color="0.6")
    ax[0].set(title="depth as read (Cabello)", xlabel="depth (km)", ylabel="events", xlim=(0, 300))
    for v in sorted(set(v for vals in C.FIXED_DEPTHS.values() for v in vals)):
        ax[0].axvline(v, color="tab:red", lw=0.6, ls=":")
    st = ["relocated_cabello", "relocated_potin", "free", "filled", "fixed", "assigned", "missing"]
    ax[1].hist([z1[el["depth_status"] == s].dropna() for s in st], bins=bins, stacked=True, color=[STATC[s] for s in st],
               label=[f"{s} ({int((el['depth_status'] == s).sum()):,})" for s in st])
    ax[1].set(title="after locate, by depth status", xlabel="depth (km)", xlim=(0, 300))
    ax[1].legend(fontsize=8)
    save(fig, "03_depth_status.png")
    return el["depth_status"].value_counts(normalize=True).round(3).to_dict()


def magnitudes(grp):
    g = grp[grp["gcmt_id"].notna() | grp["agency"].eq("GCMT")]
    ref = grp[grp["agency"] == "GCMT"].groupby("grp")["mag"].first()
    d = grp[grp["agency"] != "GCMT"].assign(gcmt=lambda x: x["grp"].map(ref)).dropna(subset=["gcmt"])
    fig, ax = plt.subplots(1, 3, figsize=SIZE, sharey=True)
    off = {}
    for a, ag in zip(ax, ("CSN-improved", "USGS", "ISC")):
        s = d[d["agency"] == ag]
        off[ag] = round(float((s["mag"] - s["gcmt"]).median()), 2)
        a.scatter(s["gcmt"], s["mag"], s=8, alpha=0.4, lw=0)
        a.plot([4.5, 9], [4.5, 9], "k-", lw=0.8)
        a.plot([4.5, 9], [4.5 + off[ag], 9 + off[ag]], "r--", lw=1)
        a.set(title=f"{ag.replace('-improved', '')}: median {off[ag]:+.2f} (n={len(s)})", xlabel="GCMT Mw", xlim=(4.5, 9), ylim=(4.5, 9))
    ax[0].set_ylabel("Cabello Mw of the agency row")
    fig.suptitle("the same earthquake, Cabello Mw by agency against its GCMT Mw", fontsize=12)
    save(fig, "04_magnitudes.png")
    return off


def mechanisms(em):
    fig = plt.figure(figsize=SIZE)
    a = fig.add_subplot(1, 2, 1)
    bins = np.arange(3.9, 9.1, 0.5)
    src = ["anss", "gcmt", "gem", "cabello"]
    tot = em.groupby(pd.cut(em["mag"], bins), observed=False).size()
    bottom = np.zeros(len(tot))
    for s, col in zip(src, ("tab:blue", "tab:orange", "tab:green", "tab:gray")):
        v = (em[em["mech_src"] == s].groupby(pd.cut(em.loc[em["mech_src"] == s, "mag"], bins), observed=False).size() / tot).fillna(0).to_numpy()
        a.bar(bins[:-1] + 0.25, v, width=0.45, bottom=bottom, color=col, label=f"{s} ({int((em['mech_src'] == s).sum()):,})")
        bottom += v
    a.set(xlabel="magnitude", ylabel="share of events with a mechanism", ylim=(0, 1), title="mechanism coverage by source")
    a.legend(loc="upper left")
    b = fig.add_subplot(1, 2, 2)
    basemap(b, cities=False)
    try:
        from obspy.imaging.beachball import beach
        e = em[(em["mag"] >= 6) & em["strike1"].notna()]
        for _, r in e.iterrows():
            b.add_collection(beach([r["strike1"], r["dip1"], r["rake1"]], xy=(r["longitude"], r["latitude"]),
                                   width=0.12 * (r["mag"] - 5), facecolor="tab:red" if r["mech_src"] == "anss" else "tab:blue",
                                   linewidth=0.3, zorder=3))
        b.set_title(f"M >= 6 with a mechanism ({len(e)}; red ANSS, blue other)", fontsize=11)
    except ImportError:
        b.set_title("obspy not available: no beachballs", fontsize=11)
    save(fig, "05_mechanisms.png")
    return {"with_mech": int(em["mech_src"].notna().sum()),
            "M>=5.5": round(float(em.loc[em["mag"] >= 5.5, "mech_src"].notna().mean()), 3),
            "by_source": em["mech_src"].value_counts().to_dict()}


def map_families(ev):
    fig, ax = plt.subplots(1, 4, figsize=SIZE, sharey=True)
    for a, f in zip(ax, ("interface", "in-slab", "crustal", "excluded")):
        basemap(a, legend=f == "interface")
        e = ev[ev["family"] == f]
        s = e[e["mag"] < 5.5]
        a.scatter(s["longitude"], s["latitude"], s=1, c=FAMC[f], alpha=0.3, lw=0)
        s = e[e["mag"] >= 5.5]
        a.scatter(s["longitude"], s["latitude"], s=6 * (s["mag"] - 4.5) ** 2, c=FAMC[f], alpha=0.7, lw=0.3, edgecolors="k")
        n55 = format(int((e["mag"] >= 5.5).sum()), ",").replace(",", " ")
        a.set_title(f"{f.capitalize()}, {n55} (M >= 5.5)", fontsize=11)
    save(fig, "06_map_families.png")


def map_decisions(ev):
    fig, ax = plt.subplots(1, 2, figsize=SIZE, sharey=True)
    basemap(ax[0], cities=False)
    o = ev[ev["cls_rule"] == "override"]
    ax[0].scatter(o["longitude"], o["latitude"], s=60, facecolors="none", edgecolors="k", lw=1.2, label=f"class set by hand ({len(o)})")
    m = ev[ev["mag_src"] == "override"]
    ax[0].scatter(m["longitude"], m["latitude"], s=25, marker="s", c="tab:red", lw=0, label=f"magnitude from the paper ({len(m)})")
    t = ev[ev["override"].fillna("").str.len() > 0]
    ax[0].scatter(t["longitude"], t["latitude"], s=40, marker="*", c="tab:blue", lw=0, label=f"row fixed or added ({len(t)})")
    for _, r in o.iterrows():
        ax[0].annotate(f"{r['time_iso'][:4]} M{r['mag']:.1f}", (r["longitude"], r["latitude"]), fontsize=7, xytext=(4, 2), textcoords="offset points")
    ax[0].legend(fontsize=8, loc="lower left")
    ax[0].set_title("hand decisions", fontsize=11)
    basemap(ax[1], cities=False)
    u = ev[ev["class"] == "unresolved"]
    unk = u["depth_status"].isin(C.UNKNOWN_DEPTH)
    ax[1].scatter(u.loc[unk, "longitude"], u.loc[unk, "latitude"], s=4 + 4 * (u.loc[unk, "mag"] - 3.9) ** 2, c="tab:cyan", lw=0, alpha=0.7,
                  label=f"unknown depth, no slab test ({int(unk.sum())})")
    ax[1].scatter(u.loc[~unk, "longitude"], u.loc[~unk, "latitude"], s=4 + 4 * (u.loc[~unk, "mag"] - 3.9) ** 2, c="tab:purple", lw=0, alpha=0.7,
                  label=f"real depth, no class fits ({int((~unk).sum())})")
    ax[1].legend(fontsize=8, loc="lower left")
    ax[1].set_title(f"unresolved: in no family ({len(u):,}, {int((u['mag'] >= 5.5).sum())} M >= 5.5)", fontsize=11)
    save(fig, "07_map_decisions.png")


def counts_old_new(o, od, n):
    fig, ax = plt.subplots(1, 3, figsize=SIZE, sharey=True)
    labs = [f"{a}-{b}" for a, b in zip(MB[:-1], MB[1:])]
    tab = {}
    for a, f in zip(ax, ("interface", "in-slab", "crustal")):
        rows = []
        for d, lab, col in ((o, "campaign rows", "0.75"), (od, "campaign, deduplicated", "0.45"), (n, "new", FAMC[f])):
            v = d[d["family"] == f].groupby(pd.cut(d["m0"], MB, right=True), observed=False).size().to_numpy()
            rows.append(v)
        x = np.arange(len(labs))
        for k, (v, lab, col) in enumerate(zip(rows, ("campaign rows", "campaign, deduplicated", "new"), ("0.75", "0.45", FAMC[f]))):
            a.bar(x + (k - 1) * 0.27, v, width=0.27, color=col, label=lab)
        a.set(xticks=x, xticklabels=labs, yscale="log", title=f, xlabel="Cabello magnitude")
        a.tick_params(axis="x", rotation=45, labelsize=9)
        tab[f] = {l: [int(v[i]) for v in rows] for i, l in enumerate(labs)}
    ax[0].set_ylabel("events (common ground)")
    ax[0].legend(fontsize=8)
    save(fig, "08_counts_old_new.png")
    return tab


def moves(j):
    s = j[j["m0"] >= 5.5]
    fams = ["interface", "in-slab", "crustal", "excluded"]
    ct = pd.crosstab(s["family_old"], s["family"]).reindex(index=fams, columns=fams, fill_value=0)
    fig, a = plt.subplots(figsize=SIZE)
    a.imshow(np.where(np.eye(4, dtype=bool), np.nan, ct.to_numpy()), cmap="Oranges")
    for i, fo in enumerate(fams):
        for k, fn in enumerate(fams):
            v = ct.loc[fo, fn]
            if i == k:
                a.text(k, i, f"{v}\nkept", ha="center", va="center", fontsize=11, color="0.4")
            elif v:
                r = s[(s["family_old"] == fo) & (s["family"] == fn)]["cls_rule"].value_counts().head(2)
                a.text(k, i, f"{v}\n" + ", ".join(f"{q} {c}" for q, c in r.items()), ha="center", va="center", fontsize=8.5)
    a.set(xticks=range(4), xticklabels=fams, yticks=range(4), yticklabels=fams, xlabel="new family", ylabel="campaign family",
          title="family moves of the same events, M >= 5.5, with the deciding rules")
    save(fig, "09_moves.png")
    return ct


def mt_family(ev):
    fig, ax = plt.subplots(3, 1, figsize=SIZE, sharex=True)
    for a, f in zip(ax, ("interface", "in-slab", "crustal")):
        e = ev[(ev["family"] == f) & (ev["year"] >= 1900)]
        for s, col in STATC.items():
            k = e[e["depth_status"] == s]
            a.scatter(k["year"], k["mag"], s=2 + 2 * (k["mag"] - 4) ** 2, c=col, lw=0, alpha=0.6, label=s if f == "interface" else None)
        a.set(ylabel="M", ylim=(3.9, 9.7), title=f, xlim=(1900, 2023))
    ax[0].legend(fontsize=7, ncol=4, loc="upper left")
    ax[2].set_xlabel("year")
    save(fig, "10_mt_family.png")


def large_events(ev, rm):
    e = ev[ev["mag"] >= 7].copy()
    agree = rm.dropna(subset=["id"]).set_index("id")["agree"]
    e["agree"] = e["id"].map(agree).fillna("")
    fig, a = plt.subplots(figsize=SIZE)
    order = ["slab_interface", "patagonia_interface", "intra_slab", "slab_deep", "forearc", "intraarc", "backarc", "patagonia_crustal",
             "outer_rise", "unresolved", "deep_unknown", "unclassified"]
    order = [c for c in order if c in set(e["class"])]
    for i, c in enumerate(order):
        k = e[e["class"] == c]
        a.scatter(k["year"], [i] * len(k), s=10 * (k["mag"] - 6) ** 2, c=CLSC.get(c, "0.5"), alpha=0.7, lw=0)
        r = k[k["agree"] == "yes"]
        a.scatter(r["year"], [i] * len(r), s=10 * (r["mag"] - 6) ** 2, facecolors="none", edgecolors="k", lw=1)
        r = k[k["agree"] == "no"]
        a.scatter(r["year"], [i] * len(r), s=10 * (r["mag"] - 6) ** 2, facecolors="none", edgecolors="tab:red", lw=1.5)
    for _, r in e[e["mag"] >= 8.5].iterrows():
        a.annotate(f"{r['time_iso'][:4]} M{r['mag']:.1f}", (r["year"], order.index(r["class"])), fontsize=7, xytext=(0, 8),
                   textcoords="offset points", ha="center")
    a.set(yticks=range(len(order)), yticklabels=[f"{NAME[c]} ({int((e['class'] == c).sum())})" for c in order], xlabel="year",
          title=f"M >= 7 ({len(e)}): ring = same class as Ruiz & Madariaga (2018), red ring = differs")
    a.tick_params(axis="y", labelsize=9)
    save(fig, "11_large_events.png")
    return {"n": len(e), "agree": int((e["agree"] == "yes").sum()), "differ": int((e["agree"] == "no").sum())}


def patagonia(ev):
    fig, ax = plt.subplots(1, 2, figsize=SIZE, gridspec_kw={"width_ratios": [1.1, 1]})
    basemap(ax[0], lat=(-58.5, -43.5), lon=(-78.5, -63))
    e = ev[ev["latitude"] < C.SOUTH_LAT + 2.5]
    for c in ("patagonia_interface", "patagonia_crustal", "outer_rise", "slab_interface", "intraarc", "unresolved", "unclassified"):
        k = e[e["class"] == c]
        if len(k):
            ax[0].scatter(k["longitude"], k["latitude"], s=4 + 5 * (k["mag"] - 3.9) ** 2, c=CLSC.get(c, "0.5"), lw=0, alpha=0.7,
                          label=f"{NAME[c]} ({len(k)})")
    ax[0].axhline(C.SOUTH_LAT, color="k", lw=0.6, ls=":")
    ax[0].legend(fontsize=7, loc="lower left")
    ax[0].set_title(f"south of the triple junction ({-C.SOUTH_LAT:.2f} S): Antarctic trench, {C.PAT_WIDTH_KM:.0f} km footprint", fontsize=10)
    s = e[(e["latitude"] < C.SOUTH_LAT)]
    ax[1].scatter(s["dist_an"], s["depth"], s=4 + 5 * (s["mag"] - 3.9) ** 2, c=[CLSC.get(c, "0.5") for c in s["class"]], lw=0, alpha=0.7)
    ax[1].add_patch(plt.Rectangle((0, 0), C.PAT_WIDTH_KM, C.PAT_MAX_Z, color="mediumseagreen", alpha=0.15))
    ax[1].axvline(0, color="k", lw=0.8)
    for _, r in s[s["mag"] >= 6.5].iterrows():
        ax[1].annotate(f"{r['time_iso'][:4]} M{r['mag']:.1f}", (r["dist_an"], r["depth"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax[1].set(xlim=(-150, 450), ylim=(120, -5), xlabel="km from the Antarctic trench (all events south of the junction)", ylabel="depth (km)",
              title="footprint: 150 km landward, 60 km deep")
    save(fig, "12_patagonia.png")
    return s["class"].value_counts().to_dict()


def section_pngs(ev):
    d = OUT / "sections"
    d.mkdir(exist_ok=True)
    sl, _ = K.K.slab()
    ts = K.transects()
    n = 0
    for t in ts:
        fig, _ = K.section_page(t, ev, sl, ts)
        if fig is None:
            continue
        fig.savefig(d / f"sec{t['label'][1:]}_{abs(t['lat0']):.1f}S.png", dpi=DPI)
        plt.close(fig)
        n += 1
    return n


def changes_since(cat):
    """Class changes of the same events against CATALOG_PREV, by cause (real depth > CRUSTAL_MAX_Z, unknown depth, other)."""
    o = pd.read_csv(C.CATALOG_PREV, dtype={"id": str}, low_memory=False)
    j = cat.merge(o[["id", "class"]], on="id", suffixes=("", "_old"))
    z = pd.to_numeric(j["depth"], errors="coerce")
    known = ~j["depth_status"].isin(C.UNKNOWN_DEPTH) & z.notna()
    j["why"] = np.where(known & (z > C.CRUSTAL_MAX_Z), f"real depth > {C.CRUSTAL_MAX_Z:.0f} km", np.where(~known, "unknown depth", "other"))
    mv = j[j["class"] != j["class_old"]]
    g = mv.groupby(["class_old", "class"]).agg(n=("id", "size"), n55=("mag", lambda m: int((m >= 5.5).sum())),
                                              n7=("mag", lambda m: int((m >= 7).sum()))).sort_values("n", ascending=False)
    return {"common": len(j), "moved": len(mv), "moved_55": int((mv["mag"] >= 5.5).sum()), "moved_7": int((mv["mag"] >= 7).sum()),
            "by_cause": mv["why"].value_counts().to_dict(),
            "pairs": {f"{a} -> {b}": [int(r["n"]), int(r["n55"]), int(r["n7"])] for (a, b), r in g.head(15).iterrows()}}


def slide_sections(ev, rm):
    """One slide per transect of sections.pdf: the M >= 5.5 panel only, the cities inside the section at the
    surface, M >= 7 labelled with the paper's names where known, legend outside, locator inset; a small
    all-events version (_all) for backup. Saved tight around the content."""
    d = OUT / "sections_slide"
    d.mkdir(exist_ok=True)
    sl, _ = K.K.slab()
    ts = K.transects()
    names = rm.dropna(subset=["id"]).drop_duplicates("id").set_index("id")["name"] if "name" in rm else pd.Series(dtype=str)
    PAL.apply(14)
    n = 0
    for t in ts:
        x0, x1 = SLIDE_XMIN, min(SLIDE_XMAX, C.SECTION_X[t["fam"]][1])
        x, y = K.proj(t, ev["longitude"].to_numpy(), ev["latitude"].to_numpy())
        m = (np.abs(y) <= t["half"]) & (x >= x0) & (x <= x1)
        if not m.any():
            continue
        e = ev[m].assign(x=x[m])
        sx, sy = K.proj(t, sl["lon"].to_numpy(), sl["lat"].to_numpy())
        sm = (np.abs(sy) <= t["half"]) & (sx >= x0) & (sx <= x1)
        g = sl[sm].assign(x=sx[sm], bot=lambda q: q["dep"] + q["thk"]).groupby(pd.cut(sx[sm], np.arange(x0, x1 + 11, 10)), observed=True).agg(
            x=("x", "median"), top=("dep", "median"), top_lo=("dep", "min"), top_hi=("dep", "max"), bot=("bot", "median"))
        cities = []
        for city, (clo, cla) in C.CITIES.items():
            cx, cy = K.proj(t, clo, cla)
            if abs(cy) <= t["half"] and x0 <= cx <= x1:
                cities.append((city, cx))
        for suffix, sub, small in (("", e[e["mag"] >= 5.5], False), ("_all", e, True)):
            fig = plt.figure(figsize=SIZE)
            w = 0.53
            h = SLIDE_VE * SLIDE_ZMAX / (x1 - x0) * w * SIZE[0] / SIZE[1]
            a = fig.add_axes([0.08, 0.12, w, h])
            if len(g):
                a.fill_between(g["x"], g["top_lo"], g["bot"], color="0.5", alpha=0.16, lw=0, zorder=0, label="subducting plate (Slab2)")
                a.fill_between(g["x"], g["top_lo"], g["top_hi"], color="0.3", alpha=0.45, lw=0, zorder=1, label="Slab2 top")
            if t["fam"] == "antarctic":
                a.add_patch(plt.Rectangle((0, 0), C.PAT_WIDTH_KM, C.PAT_MAX_Z, color=CLSC["patagonia_interface"], alpha=0.15, lw=0,
                                          label="Antarctic interface footprint"))
            a.axvline(0, c="0.35", lw=0.8, ls=(0, (4, 3)), zorder=1)
            sub = sub.sort_values("mag")
            unk = sub["depth_status"].isin(C.UNKNOWN_DEPTH).to_numpy()
            mg = sub["mag"].to_numpy()
            sz = 4 if small else 7 * (mg - 4.5) ** 2
            big = mg >= 6.5
            for c in PAL.ZORDER:
                kk = (sub["class"] == c).to_numpy()
                if not kk.any():
                    continue
                for sel, face, al, zo in ((kk & ~unk & ~big, CLSC[c], 0.7, 3), (kk & ~unk & big, CLSC[c], 1.0, 8),
                                          (kk & unk & ~big, "none", 0.8, 4), (kk & unk & big, "none", 1.0, 9)):
                    if sel.any():
                        a.scatter(sub["x"][sel], sub["depth"][sel], s=sz if np.isscalar(sz) else sz[sel], facecolors=face, edgecolors=CLSC[c],
                                  lw=0.3 if face != "none" else 0.9, alpha=al, zorder=zo,
                                  label=f"{NAME[c]} ({int(kk.sum())})" if (face != "none" and al < 1) else None)
            a.scatter([], [], facecolors="none", edgecolors="0.2", s=40, label="hollow: depth unknown")
            a.annotate("trench", (0, 0), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=10, color="0.35",
                       annotation_clip=False)
            for city, cx in cities:
                a.plot(cx, 0, "^", color="0.15", ms=9, clip_on=False, zorder=20)
                dx, dy, ha = CITY_OFF.get(city, (0, 7, "center")) if len(cities) > 1 else (0, 7, "center")
                a.annotate(city, (cx, 0), xytext=(dx, dy + 3), textcoords="offset points", ha=ha, fontsize=11, annotation_clip=False)
            a.set(xlim=(x0, x1), ylim=(SLIDE_ZMAX, 0), xlabel="distance from the trench (km)", ylabel="depth (km)")
            a.set_aspect(SLIDE_VE, adjustable="box", anchor="SW")
            a.set_xticks(np.arange(0, x1 + 1, 100))
            a.set_yticks(np.arange(0, SLIDE_ZMAX + 1, 50))
            if not small:
                K.labels(a, sub, "x", "depth", nmax=8, sep=12, mmin=7.0, fontsize=9,
                         text=lambda r: f"{names[r['id']]}, M{r['mag']:.1f}" if r["id"] in names else f"{r['time_iso'][:4]} M{r['mag']:.1f}")
            fig.canvas.draw()
            pos = a.get_window_extent().transformed(fig.transFigure.inverted())
            fig.text(pos.x0, pos.y1 + 0.075, f"{-t['lat0']:.0f}\u00b0S, " + ("all magnitudes" if small else "M \u2265 5.5"),
                     fontsize=15, weight="medium", va="bottom")
            hh, ll = a.get_legend_handles_labels()
            gx = pos.x1 + 0.03
            fig.legend(hh, ll, loc="upper left", bbox_to_anchor=(gx, pos.y1 + 0.075), fontsize=9.5, borderaxespad=0,
                       labelspacing=0.35, handlelength=1.4)
            top = pos.y1 + 0.075
            ins = fig.add_axes([0.99 - 0.19, pos.y0, 0.19, top - pos.y0])
            K.locator(ins, ev, ts, t)
            ins.set(xlim=(-79, -63), ylim=(-58.5, -16.5), xticks=[], yticks=[], aspect=1 / np.cos(np.radians(37.5)))
            ins.set_anchor("NE")
            for city, (clo, cla) in C.CITIES.items():
                ins.plot(clo, cla, "^", color="0.15", ms=3, zorder=6)
            for sp in ins.spines.values():
                sp.set_visible(True)
                sp.set_color("0.4")
                sp.set_linewidth(0.8)
            fig.savefig(d / f"sec{t['label'][1:]}_{abs(t['lat0']):.0f}S{suffix}.png", dpi=DPI, bbox_inches="tight", pad_inches=0.2)
            plt.close(fig)
        n += 1
    PAL.apply()
    return n


# hand-off note
def handoff(n):
    lines = ["# The catalog of psha_chile: hand-off", "",
             f"Status {pd.Timestamp.today():%Y-%m-%d}. Code: `cat_handler_2` (README.md, DECISIONS.md, CONTEXT.md), commit `{n['commit']}`; "
             f"final `catalog.csv` written {n['catalog_date']}. Figures for the presentation: `results/cat_handler_2/slides/`.", "",
             "## Pipeline", "",
             "| stage | count |", "|---|---|",
             f"| Cabello rows south of {-C.LAT_MAX:.0f} S with M > {C.MMIN} | {n['cab_rows']:,} |",
             f"| earthquakes after removing cross-agency copies | {n['events']:,} ({n['dup_frac']:.0%} of rows were copies) |",
             f"| CSN rows relocated with Potin here (besides Cabello's own) | {n['potin']:,} |",
             f"| default or missing depths filled (group, Potin, GCMT) | {n['filled']:,} of {n['fixed_or_missing']:,} |",
             f"| events with a focal mechanism | {n['with_mech']:,} ({n['mech_55']:.0%} of M >= 5.5) |",
             f"| magnitudes taken from Ruiz and Madariaga (2018) | {n['mag_over']} |",
             f"| `catalog_base.csv` | {n['events']:,} events |",
             f"| `catalog.csv`: classified, {n['n_class']} classes in 4 families | {n['events']:,} events |", "",
             "## Key numbers", "",
             "**Duplicates.** Share of Cabello rows that were copies of another agency's row, by magnitude: "
             + ", ".join(f"{k}: {v:.0%}" for k, v in n["dup_by_mag"].items()) + ".", "",
             "**Depth status** (share of events): " + ", ".join(f"{k} {v:.1%}" for k, v in n["depth_status"].items())
             + ". The classifier trusts relocated, free and filled depths only.", "",
             "**Mechanisms.** " + ", ".join(f"{k} {v:,}" for k, v in n["mech"]["by_source"].items()) + ".", "",
             "**Magnitudes.** Cabello's Mw for the same earthquake, by agency, against the GCMT Mw (median): "
             + ", ".join(f"{k.replace('-improved', '')} {v:+.2f}" for k, v in n["mag_offsets"].items())
             + ". Events present only as ISC rows carry an Mw about 0.3 low (DECISIONS 32).", "",
             "**Counts per family and magnitude bin** (campaign rows / campaign deduplicated / new, common ground: "
             f"Cabello magnitude, {n['common']}):", "",
             "| M | interface | in-slab | crustal |", "|---|---|---|---|"]
    for lab in next(iter(n["counts"].values())):
        lines.append(f"| {lab} | " + " | ".join(" / ".join(str(v) for v in n["counts"][f][lab]) for f in ("interface", "in-slab", "crustal")) + " |")
    ct = n["moves"]
    lines += ["", "**Family moves at M >= 5.5** (rows campaign, columns new):", "",
              "| | " + " | ".join(ct["columns"]) + " |", "|---|" + "---|" * len(ct["columns"])]
    for r, vals in zip(ct["index"], ct["data"]):
        lines.append(f"| {r} | " + " | ".join(str(v) for v in vals) + " |")
    lines += ["", f"**M >= 7 events:** {n['large']['n']}; against Ruiz and Madariaga (2018): {n['large']['agree']} same class, "
              f"{n['large']['differ']} different (check/review_rm.csv).", "",
              "## Hand decisions", "", "| file | id | field | value | reason |", "|---|---|---|---|---|"]
    for f, d in (("overrides.csv", n["hand"]["overrides"]), ("class_overrides.csv", n["hand"]["class"]), ("additions.csv", n["hand"]["additions"])):
        for r in d:
            lines.append(f"| {f} | {r['id']} | {r.get('field', 'class' if f.startswith('class') else 'event')} | {r.get('value', r.get('class', r.get('magnitude', '')))} | {str(r.get('reason', ''))[:90]} |")
    lines += ["", "## Changes after 29 Sep 2026", "",
              f"- North limit: Cabello rows north of {-C.LAT_MAX:.0f} S dropped before anything else ({n['north_dropped']:,} rows; DECISIONS 2).",
              f"- Crustal depth cap {C.CRUSTAL_MAX_Z:.0f} km and unknown depths to the slab family; the neighbour vote removed (DECISIONS 18, 21, 22, 33, 34)."]
    if n.get("prev"):
        pv = n["prev"]
        lines += [f"  Against the catalog of 29 Sep (`catalog_v1.csv`, {pv['common']} events in both): {pv['moved']} events changed class "
                  f"({pv['moved_55']} at M >= 5.5, {pv['moved_7']} at M >= 7). By cause: " +
                  "; ".join(f"{k} {v}" for k, v in pv["by_cause"].items()) + ".", "",
                  "| old class -> new class | all | M >= 5.5 | M >= 7 |", "|---|---|---|---|"]
        lines += [f"| {k} | {v[0]} | {v[1]} | {v[2]} |" for k, v in pv["pairs"].items()]
    else:
        lines += ["  (`results/cat_handler_2/catalog_v1.csv`, the copy of the 29 Sep catalog, was not found: no counts.)"]
    lines += ["", "## Open", "",
              "- In-slab Mmax: Santiago 1647 M8.4 is now the largest in-slab event; whether historical events count for Mmax is a source-model decision (DECISIONS 31).",
              "- Cabello magnitudes are agency-dependent; ISC-only events about 0.3 low (DECISIONS 32).",
              "- Historical M >= 7 still unresolved: 1687, 1850, 1870 (DECISIONS 29); paper events absent from Cabello (DECISIONS 30).",
              f"- Crustal events deeper than {C.CRUSTAL_MAX_Z:.0f} km kept by hand: {n['exceptions']} (`crustal_exceptions.csv`, DECISIONS 34); "
              "events above the deep slab between 30 and 70 km are unresolved (rule deep_mid, lever FOREARC_MAX_Z).", "",
              "## Figures (results/cat_handler_2/slides/)", "",
              "- `01_pipeline.png`: the two steps of the catalog build, sources to catalog_base to catalog, with the counts at each stage.",
              "- `02_duplicates.png`: share of Cabello rows that duplicate another agency's row, by magnitude; what the merged groups are made of.",
              "- `03_depth_status.png`: depth histogram as read (dotted: the agency default depths) and after relocation and filling, by depth status.",
              "- `04_magnitudes.png`: Cabello's Mw of the CSN, USGS and ISC rows against the GCMT Mw of the same earthquake, with the median offsets.",
              "- `05_mechanisms.png`: share of events with a focal mechanism by source and magnitude; beachballs of the M >= 6 events.",
              "- `06_map_families.png`: the four source families in map view, M >= 5.5 enlarged, with the cities and both trenches.",
              "- `07_map_decisions.png`: the hand decisions (class, magnitude, row fixes) and the unresolved events, which enter no family.",
              "- `08_counts_old_new.png`: events per family and magnitude bin, campaign catalog (rows and deduplicated) against the new catalog.",
              "- `09_moves.png`: family moves of the same events at M >= 5.5 between the campaign and the new classification, with the deciding rules.",
              "- `10_mt_family.png`: magnitude against time per family since 1900, coloured by depth status.",
              "- `11_large_events.png`: the M >= 7 events by class through time; rings mark agreement with Ruiz and Madariaga (2018).",
              "- `12_patagonia.png`: south of the triple junction: Antarctic trench, the 150 km interface footprint and the Patagonian classes, in map and section.",
              f"- `sections/secNN_<lat>S.png`: the {n['n_sections']} transects of sections.pdf, one PNG each, with their locator map.",
              f"- `sections_slide/secNN_<lat>S.png`: slide version of every transect ({n['n_slide_sections']}): M >= 5.5, the cities of the section at the surface, M >= 7 named; `_all` for backup."]
    (C.HERE / "CATALOG_final.md").write_text("\n".join(lines) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rd = lambda f: pd.read_csv(f, dtype={"id": str}, low_memory=False)
    pj = json.loads((C.PREP / "prepare.json").read_text())
    cj = json.loads((C.OUT / "classify.json").read_text())
    ev, grp, el, em = rd(C.PREP / "01_dedup.csv"), rd(C.PREP / "01_dedup_groups.csv"), rd(C.PREP / "02_locate.csv"), rd(C.PREP / "03_mech.csv")
    cat = rd(C.OUT / "catalog.csv")
    cat["family"] = fam_of(cat["class"])
    n = {"cab_rows": pj["read"][f"cabello_M>{C.MMIN}"], "events": len(cat), "potin": pj["locate"]["csn_relocated_here"],
         "fixed_or_missing": pj["locate"]["fixed_or_missing"],
         "filled": sum(v for k, v in pj["locate"].items() if k.startswith("filled_")),
         "with_mech": pj["mech"]["with_mech"], "mech_55": pj["mech"]["M>=5.5"]["with_mech"] / pj["mech"]["M>=5.5"]["events"],
         "mag_over": pj["magnitudes"]["mag_overrides"], "n_class": int(cat["class"].nunique()),
         "f55": cat.loc[cat["mag"] >= 5.5, "family"].value_counts().to_dict()}
    n["dup_frac"] = 1 - len(ev) / (len(ev) + int((grp["n_rows"] - 1)[grp["kept"]].sum()))
    pipeline(n)
    n["dup_by_mag"] = {f"{k.left:.1f}-{k.right:.1f}": float(v) for k, v in duplicates(ev, grp).items()}
    n["depth_status"] = depth_status(el)
    n["mag_offsets"] = magnitudes(grp)
    n["mech"] = mechanisms(em)
    map_families(cat)
    map_decisions(cat)
    old = rd(C.OLD_CLASSIFIED)
    new = cat.copy()
    new["m0"] = new["mag_cabello"] if "mag_cabello" in new else new["mag"]
    old["m0"] = old["mag"]
    for d in (old, new):
        d["year"] = pd.to_numeric(d["time_iso"].astype(str).str[:4], errors="coerce")
        d["family"] = d["class"].map(CP.FAMILY).fillna("excluded")
    y0, y1 = max(old["year"].min(), new["year"].min()), min(old["year"].max(), new["year"].max())
    box = (old["longitude"].min(), old["longitude"].max(), old["latitude"].min(), old["latitude"].max())
    common = lambda d: d[(d["m0"] > C.MMIN) & d["year"].between(y0, y1) & d["longitude"].between(*box[:2]) & d["latitude"].between(*box[2:])].copy()
    o, nn = common(old), common(new)
    kept = {m: k for k, ids in zip(new["id"], new["dup_ids"].fillna("")) for m in ids.split(";") if m}
    kept.update({k: k for k in new["id"]})
    o["new_id"] = o["id"].map(kept)
    od = o.dropna(subset=["new_id"]).drop_duplicates("new_id")
    n["common"] = f"years {y0:.0f}-{y1:.0f}, lon {box[0]:.1f} to {box[1]:.1f}, lat {box[2]:.1f} to {box[3]:.1f}"
    n["counts"] = counts_old_new(o, od, nn)
    j = od.merge(nn[["id", "class", "family", "cls_rule", "m0"]], left_on="new_id", right_on="id", suffixes=("_old", ""))
    ct = moves(j)
    n["moves"] = {"index": list(ct.index), "columns": list(ct.columns), "data": ct.to_numpy().tolist()}
    mt_family(cat)
    rm = pd.read_csv(K.OUT / "review_rm.csv", dtype={"id": str}) if (K.OUT / "review_rm.csv").exists() else pd.DataFrame(columns=["id", "agree"])
    n["large"] = large_events(cat, rm)
    n["patagonia"] = patagonia(cat)
    n["n_sections"] = section_pngs(cat)
    n["n_slide_sections"] = slide_sections(cat, rm)
    n["exceptions"] = cj.get("crustal_deeper_than_max_z", {}).get("events", 0)
    n["hand"] = {"overrides": pd.read_csv(C.OVERRIDES, dtype=str).to_dict("records") if C.OVERRIDES.exists() else [],
                 "class": pd.read_csv(C.CLASS_OVERRIDES, dtype=str).to_dict("records") if C.CLASS_OVERRIDES.exists() else [],
                 "additions": pd.read_csv(C.ADDITIONS, dtype=str).to_dict("records") if C.ADDITIONS.exists() else []}
    n["north_dropped"] = pj["read"].get("cabello_rows_north_dropped", 0)
    try:
        n["commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=C.ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        n["commit"] = "not a git checkout"
    n["catalog_date"] = pd.Timestamp((C.OUT / "catalog.csv").stat().st_mtime, unit="s").strftime("%Y-%m-%d %H:%M")
    n["prev"] = changes_since(cat) if C.CATALOG_PREV.exists() else None
    (OUT / "numbers.json").write_text(json.dumps(n, indent=1, default=str))
    handoff(n)
    print(f"-> {OUT} ({n['n_sections']} section PNGs), {C.HERE / 'CATALOG_final.md'}")


if __name__ == "__main__":
    main()