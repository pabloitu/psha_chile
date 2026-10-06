# Diagnostics of the dedup stage. Writes results/cat_handler_2/check/:
#   pairs.png        dt vs distance of every cross-agency pair in the wide
#                    windows, merged or not, with the merge windows drawn
#   summary.png      Cabello rows vs events after the merge, by magnitude and
#                    year; what the merged groups are made of; which magnitude
#                    each group kept and which it dropped
#   groups.pdf       one panel per merged group with kept M >= GAL_M and per
#                    near miss with M >= GAL_M_NEAR: map around the kept event,
#                    rows with agency, time offset, magnitude, depth
#   near_misses.csv  unmerged cross-agency pairs close in time and space
#   locate.png       depth status by magnitude, the Potin shifts of CSN rows,
#                    depth histograms before and after, the filled depths
#   filled_large_change.csv  filled depths that moved more than 60 km
#   mech.png         mechanism coverage by magnitude and year, agreement between
#                    sources (Kagan angle), match distances
#   mech_disagree.csv  events whose sources differ by more than KAGAN_MAX
#   classify.png     classes by magnitude, deciding rules, depth relative to the
#                    slab top per class, transitions from the old classification
#   class_changes.csv  events M >= 5.5 whose class differs from the old one
#   map.png          final classes in map view, M >= 5.5; black rings: class set by
#                    hand in overrides.csv; labels: largest per panel (MAP_LABEL_*)
#   sections.pdf     one page per transect perpendicular to the trench, north to
#                    south (config SECTION_*): events between the two bounds
#                    projected onto the transect; plate (Slab2 top to top + thk),
#                    interface band (Nazca) or footprint (Antarctic); labels by
#                    class family (LABEL_M); a locator map on the right
#   sections_map.png every transect and its bounds

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

from cat_handler_2 import build as B
from cat_handler_2 import classify as K
from cat_handler_2 import config as C
from cat_handler_2 import sources as S

OUT = C.OUT / "check"
MBINS = [C.MMIN, 4.5, 5.5, 10]
GAL_M, GAL_M_NEAR = 6.0, 5.5
NEAR_DT, NEAR_KM = 30.0, 100.0
KAGAN_MAX = 60.0


def pairs_all(r):
    """Every pair within the wide windows, from DUP_FROM, both orders removed; merged if in the same group."""
    y = r[r["year"] >= C.DUP_FROM]
    p = S.pairs(y, y, C.WIDE_DT, C.WIDE_KM, C.WIDE_DM, ta="th", tb="th", xa=("lon_h", "lat_h"), xb=("lon_h", "lat_h"))
    p = p[p["ia"] < p["ib"]].copy()
    i, j = y.index[p["ia"]], y.index[p["ib"]]
    p["ia"], p["ib"] = i, j
    p["cross"] = r.loc[i, "agency"].to_numpy() != r.loc[j, "agency"].to_numpy()
    p["merged"] = r.loc[i, "grp"].to_numpy() == r.loc[j, "grp"].to_numpy()
    p["m"] = np.fmax(r.loc[i, "mag"].to_numpy(), r.loc[j, "mag"].to_numpy())
    return p[p["m"] > C.MMIN].reset_index(drop=True)


def figures(r, ev, p):

    q = p[p["cross"]]
    fig, ax = plt.subplots(2, 3, figsize=(15, 9))
    for k in range(3):
        lo, hi = MBINS[k], MBINS[k + 1]
        s = q[(q["m"] > lo) & (q["m"] <= hi)] if k == 0 else q[(q["m"] >= lo) & (q["m"] < hi)]
        a = ax[0, k]
        for mg, c in ((False, "0.6"), (True, "tab:red")):
            u = s[s["merged"] == mg]
            a.scatter(u["dt"], u["dkm"], s=3 if len(u) > 2000 else 8, c=c, alpha=0.4, lw=0,
                      label=f"{'merged' if mg else 'not merged'} ({len(u)})")
        for dt, km, dm, _ in C.DUP_RULES:
            a.plot([0, dt, dt], [km, km, 0], "k", lw=1)
            a.text(dt, km, f" |dM| <= {dm}", fontsize=8, va="bottom")
        a.plot([0, C.DUP_TIGHT_DT, C.DUP_TIGHT_DT], [C.DUP_TIGHT_KM, C.DUP_TIGHT_KM, 0], "k:", lw=1)
        bg = ((s["dt"] > C.WIDE_DT / 2) & (s["dkm"] <= C.DUP_KM)).sum() * C.DUP_DT / (C.WIDE_DT / 2)
        a.set(xlim=(0, C.WIDE_DT), ylim=(0, C.WIDE_KM), xlabel="dt (s)", ylabel="distance (km)",
              title=f"cross-agency pairs, M {lo}-{hi}\nchance pairs expected in the merge window: {bg:.1f}")
        a.legend(loc="upper right", fontsize=8)
        a = ax[1, k]
        w = s[(s["dt"] <= C.DUP_RULES[0][0]) & (s["dkm"] <= C.DUP_RULES[0][1])]
        a.hist([w.loc[w["merged"], "dm"].abs(), w.loc[~w["merged"], "dm"].abs()], bins=np.arange(0, C.WIDE_DM + 0.1, 0.1),
               color=["tab:red", "0.6"], label=["merged", "not merged"], stacked=True)
        a.axvline(C.DUP_RULES[0][2], c="k", lw=1)
        a.set(xlabel=f"|dM| of pairs within {C.DUP_RULES[0][0]:.0f} s and {C.DUP_RULES[0][1]:.0f} km", ylabel="pairs")
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "pairs.png", dpi=110)
    plt.close(fig)



AGC = {"CSN-improved": "#1b9e77", "ISC": "#d95f02", "USGS": "#7570b3", "GCMT": "#e7298a",
       "ISC-GEM": "#66a61e", "CERESIS-GEM": "#a6761d"}


def summary(r, ev, grp):
    k = r[r["mag"] > C.MMIN]
    mb = np.arange(4.0, 8.01, 0.25)
    fig, ax = plt.subplots(2, 3, figsize=(16, 9.5))

    a = ax[0, 0]
    n0 = np.histogram(k["mag"], mb)[0]
    n1 = np.histogram(ev["mag"], mb)[0]
    c = mb[:-1] + 0.125
    a.bar(c, n0, width=0.23, color="0.75", label="Cabello rows")
    a.bar(c, n1, width=0.13, color="tab:red", label="events after the merge")
    a.set(yscale="log", xlabel="magnitude (row / kept event)", ylabel="count per 0.25 bin",
          title="rows before vs events after, per magnitude bin")
    b = a.twinx()
    b.plot(c, 100 * (1 - n1 / np.maximum(n0, 1)), "k.-")
    b.set(ylabel="fewer events than rows (%)", ylim=(0, 50))
    a.legend(loc="upper right")

    a = ax[0, 1]
    for d, lab, col in ((k, "Cabello rows", "0.5"), (ev, "events after the merge", "tab:red")):
        m = np.sort(d["mag"].to_numpy())[::-1]
        a.semilogy(m, np.arange(1, len(m) + 1), c=col, label=f"{lab} ({len(m)})")
    b = a.twinx()
    ms = np.arange(4.0, 8.01, 0.1)
    b.plot(ms, [(ev["mag"] >= m).sum() / max((k["mag"] >= m).sum(), 1) for m in ms], "k--", lw=1)
    b.set(ylabel="N(>= M) after / before (dashed)", ylim=(0.6, 1.02))
    a.set(xlabel="magnitude", ylabel="N(>= M)", title="cumulative counts")
    a.legend(loc="lower left")

    a = ax[0, 2]
    yb = np.arange(1960, 2031, 5)
    for m0, col in ((C.MMIN, "0.4"), (5.0, "tab:blue"), (5.5, "tab:red"), (6.0, "k")):
        n0 = np.histogram(k.loc[k["mag"] > m0, "year"] if m0 == C.MMIN else k.loc[k["mag"] >= m0, "year"], yb)[0]
        n1 = np.histogram(ev.loc[ev["mag"] > m0, "year"] if m0 == C.MMIN else ev.loc[ev["mag"] >= m0, "year"], yb)[0]
        a.plot(yb[:-1] + 2.5, np.where(n0 > 0, 100 * (1 - n1 / np.maximum(n0, 1)), np.nan), "o-", ms=3, c=col,
               label=(f"M > {m0}" if m0 == C.MMIN else f"M >= {m0}"))
    a.set(xlabel="year", ylabel="fewer events than rows (%)", title="by 5-year bin (counts above the cut)")
    a.legend()

    m = grp[grp["n_rows"] > 1].copy()
    m["combo"] = m.groupby("grp")["agency"].transform(lambda s: " + ".join(sorted(s)))
    gg = m.drop_duplicates("grp")
    top = gg["combo"].value_counts().index[:7]
    gg = gg.assign(combo=np.where(gg["combo"].isin(top), gg["combo"], "other"))
    t = pd.crosstab(pd.cut(gg["mag_kept"], mb[::2]), gg["combo"])
    a = ax[1, 0]
    t.plot.bar(stacked=True, ax=a, width=0.8, cmap="tab10")
    a.set(yscale="log", xlabel="kept magnitude", ylabel="merged groups", title="agencies in the merged groups")
    a.set_xticklabels([f"{i.left:.1f}" for i in t.index], rotation=0)
    a.legend(fontsize=7)

    a = ax[1, 1]
    o = m[~m["kept"]]
    for ag, s in o.groupby("agency"):
        a.scatter(s["mag_kept"], s["mag"], s=4, alpha=0.5, c=AGC.get(ag, "0.5"), label=f"{ag} ({len(s)})")
    kk = m[m["kept"] & (m["mag"] != m["mag_kept"])]
    a.scatter(kk["mag_kept"], kk["mag"], s=6, marker="x", c="k", lw=0.6, label=f"location row, magnitude replaced ({len(kk)})")
    a.plot([4, 9], [4, 9], "k", lw=0.8)
    a.set(xlim=(3.9, 9), ylim=(3, 9), xlabel="magnitude kept (Cabello, from the GCMT / ISC-GEM / native-Mw row)",
          ylabel="Cabello magnitude of the other row", title="magnitudes dropped by the merge")
    a.legend(fontsize=7, markerscale=3)

    a = ax[1, 2]
    gg = m[m["kept"]]
    ev2 = ev[ev["n_rows"] > 1]
    for col, lab, ls in (("mag_src", "magnitude from", "-"), ("loc_src", "location from", "--")):
        t = pd.crosstab(pd.cut(ev2["mag"], mb[::2]), ev2[col], normalize="index")
        for ag in t.columns:
            a.plot(mb[:-1:2][:len(t)] + 0.25, t[ag].to_numpy(), ls=ls, marker="o", ms=3, c=AGC.get(ag, "0.5"),
                   label=f"{lab} {ag}")
    a.set(xlabel="kept magnitude", ylabel="share of merged events", title="source of magnitude (solid) and location (dashed)")
    a.legend(fontsize=6, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "summary.png", dpi=110)
    plt.close(fig)


def gallery(r, grp, p):
    nb = pd.concat([p[["ia", "ib"]], p[["ib", "ia"]].set_axis(["ia", "ib"], axis=1)]).groupby("ia")["ib"].agg(list)
    idx = pd.Series(r.index, index=r["id"])
    cs = []
    for _, s in grp[grp["mag_kept"] >= GAL_M].groupby("grp", sort=False):
        fl = [f for f in ("loose", "same_agency") if s[f].iloc[0]] + (["n>2"] if len(s) > 2 else [])
        cs.append(("merged", idx[s.loc[s["kept"], "id"].iloc[0]], idx[s["id"]].tolist(), fl, s["mag_kept"].iloc[0]))
    nm = p[p["cross"] & ~p["merged"] & (p["dt"] <= NEAR_DT) & (p["dkm"] <= NEAR_KM) & (p["m"] >= GAL_M_NEAR)]
    for _, w in nm.sort_values("m", ascending=False).iterrows():
        a, b = int(w["ia"]), int(w["ib"])
        c = a if r.at[a, "mag"] >= r.at[b, "mag"] else b
        fl = [f for f, v in (("dt", w["dt"] > C.DUP_RULES[0][0]), ("dist", w["dkm"] > C.DUP_RULES[0][1]),
                             ("dM", abs(w["dm"]) > C.DUP_RULES[0][2])) if v]
        cs.append(("near miss", c, [a, b], fl, w["m"]))
    with PdfPages(OUT / "groups.pdf") as pdf:
        for k0 in range(0, len(cs), 12):
            fig, ax = plt.subplots(3, 4, figsize=(17, 12.5))
            for a, (kind, c, mem, fl, mk) in zip(ax.ravel(), cs[k0:k0 + 12]):
                la0, lo0, t0 = r.at[c, "lat_h"], r.at[c, "lon_h"], r.at[c, "th"]
                oth = [j for i in mem for j in nb.get(i, []) if j not in mem]
                R = 60.0
                for grp_, filled in ((oth, False), (mem, True)):
                    for n, i in enumerate(grp_):
                        xk = (r.at[i, "lon_h"] - lo0) * 111.32 * np.cos(np.radians(la0))
                        yk = (r.at[i, "lat_h"] - la0) * 110.57
                        if filled:
                            R = max(R, 1.3 * max(abs(xk), abs(yk)))
                        col = AGC.get(r.at[i, "agency"], "0.5")
                        a.scatter(xk, yk, s=60 if filled else 18, c=col if filled else "none", edgecolors="k" if i == c else col,
                                  linewidths=2 if i == c else 1, zorder=3 if filled else 2)
                for rr, ls in ((C.DUP_TIGHT_KM, ":"), (C.DUP_RULES[0][1], "-")):
                    a.add_patch(plt.Circle((0, 0), rr, fill=False, ls=ls, color="0.6", lw=0.8))
                a.set(xlim=(-R, R), ylim=(-R, R), aspect="equal")
                a.tick_params(labelsize=7)
                lines = [f"{'*' if i == c else ' '}{r.at[i, 'agency'][:8]:8s} M{r.at[i, 'mag']:.1f} "
                         f"{r.at[i, 'depth'] if pd.notna(r.at[i, 'depth']) else float('nan'):5.0f}km "
                         f"{r.at[i, 'th'] - t0:+5.1f}s" for i in mem]
                a.text(0.02, 0.02, "\n".join(lines), transform=a.transAxes, fontsize=7, family="monospace", va="bottom",
                       bbox={"fc": "w", "alpha": 0.8, "lw": 0})
                a.set_title(f"{kind} {r.at[c, 'time_iso'][:19]}  M{mk:.1f}" + (f"  [{', '.join(fl)}]" if fl else ""), fontsize=9,
                            color="tab:red" if kind == "near miss" or fl else "k")
            for a in ax.ravel()[len(cs[k0:k0 + 12]):]:
                a.axis("off")
            fig.legend(handles=[plt.Line2D([], [], marker="o", ls="", c=v, label=k) for k, v in AGC.items()],
                       loc="upper right", ncol=6, fontsize=8, frameon=False)
            fig.suptitle("km from the * row (hypocentres; GCMT at its PDE hypocentre); rings 30 and 50 km; "
                         "hollow: other events within 60 s and 150 km; GCMT depth is the centroid", fontsize=10, x=0.35)
            fig.tight_layout(rect=(0, 0, 1, 0.97))
            pdf.savefig(fig)
            plt.close(fig)
    return len(cs)


def locate_fig(ev):
    fig, ax = plt.subplots(2, 2, figsize=(13, 9.5))
    mb = np.arange(4.0, 8.01, 0.5)
    t = pd.crosstab(pd.cut(ev["mag"], mb), ev["depth_status"], normalize="index")
    order = [c for c in ("relocated_cabello", "relocated_potin", "free", "filled", "assigned", "fixed", "missing") if c in t]
    n = pd.cut(ev["mag"], mb).value_counts().sort_index()
    t[order].plot.bar(stacked=True, ax=ax[0, 0], width=0.85, cmap="tab10")
    ax[0, 0].set_xticklabels([f"{i.left:.1f}\n({n[i]})" for i in t.index], rotation=0)
    ax[0, 0].set(xlabel="magnitude (events)", ylabel="share", title="depth status after locate")
    ax[0, 0].legend(fontsize=8)

    r = ev[ev["depth_status"] == "relocated_potin"]
    dh = S.hav(r["lon_orig"], r["lat_orig"], r["longitude"], r["latitude"])
    a = ax[0, 1]
    a.hist(dh, bins=np.arange(0, 31, 1), color="tab:blue", alpha=0.7, label=f"epicentre shift ({len(r)})")
    a.hist((r["depth"] - r["depth_orig"]).abs(), bins=np.arange(0, 31, 1), histtype="step", color="k", label="|depth shift|")
    a.set(xlabel="km", ylabel="events", title="CSN rows relocated here with Potin")
    b = a.inset_axes([0.55, 0.3, 0.42, 0.35])
    b.scatter(r["potin_dt"], r["potin_dkm"], s=2, alpha=0.3)
    b.set(xlabel="match dt (s)", ylabel="match km", xlim=(0, C.POT_DT), ylim=(0, C.POT_KM))
    b.tick_params(labelsize=7)
    a.legend()

    a = ax[1, 0]
    s = ev[ev["mag"] >= 4.5]
    a.hist(s["depth_orig"].dropna(), bins=np.arange(0, 81, 1), color="0.7", label="before")
    a.hist(s["depth"].dropna(), bins=np.arange(0, 81, 1), histtype="step", color="tab:red", lw=1.5, label="after")
    a.set(yscale="log", xlabel="depth (km)", ylabel="events, M >= 4.5", title="depths 0-80 km before and after")
    a.legend()

    a = ax[1, 1]
    f = ev[ev["depth_status"] == "filled"]
    for src, u in f.groupby("depth_src"):
        a.scatter(u["depth_orig"] + np.random.default_rng(0).uniform(-1, 1, len(u)), u["depth"], s=8, alpha=0.6,
                  c=AGC.get(src, {"potin": "k", "gcmt": "#e7298a"}.get(src, "0.5")), label=f"{src} ({len(u)})")
    a.set(xlabel="fixed or missing depth (km, jittered)", ylabel="depth taken (km)", title="filled depths by source")
    big = f[(f["depth"] - f["depth_orig"]).abs() > 60]
    big[["id", "agency", "time_iso", "mag", "depth_orig", "depth", "depth_src", "potin_id", "potin_dt", "potin_dkm",
         "lon_orig", "lat_orig", "longitude", "latitude"]].to_csv(OUT / "filled_large_change.csv", index=False)
    a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "locate.png", dpi=110)
    plt.close(fig)


def kagan(a, b):
    """
    Kagan angle (deg) between double couples given as (strike, dip, rake) arrays of shape (n, 3).
    """
    def frame(s):
        f, d, l = np.radians(s).T
        n = np.stack([-np.sin(d) * np.sin(f), np.sin(d) * np.cos(f), -np.cos(d)], 1)
        u = np.stack([np.cos(l) * np.cos(f) + np.sin(l) * np.cos(d) * np.sin(f),
                      np.cos(l) * np.sin(f) - np.sin(l) * np.cos(d) * np.cos(f), -np.sin(l) * np.sin(d)], 1)
        t, p = (n + u) / np.sqrt(2), (n - u) / np.sqrt(2)
        return np.stack([t, p, np.cross(t, p)], 2)
    r1, r2 = frame(np.asarray(a, float)), frame(np.asarray(b, float))
    ang = []
    for dg in ([1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]):
        m = np.einsum("nij,nkj->nik", r1 * np.array(dg), r2)
        ang.append(np.degrees(np.arccos(np.clip((np.trace(m, axis1=1, axis2=2) - 1) / 2, -1, 1))))
    return np.min(ang, axis=0)


def mech_fig(ev, g, an):
    fig, ax = plt.subplots(2, 2, figsize=(13, 9.5))
    mb = np.arange(4.0, 8.01, 0.5)
    src = ev["mech_src"].fillna("none")
    t = pd.crosstab(pd.cut(ev["mag"], mb), src, normalize="index")
    order = [c for c in C.MECH_ORDER + ["none"] if c in t]
    n = pd.cut(ev["mag"], mb).value_counts().sort_index()
    t[order].plot.bar(stacked=True, ax=ax[0, 0], width=0.85, color=["tab:blue", "tab:pink", "tab:green", "tab:brown", "0.85"][:len(order)])
    ax[0, 0].set_xticklabels([f"{i.left:.1f}\n({n[i]})" for i in t.index], rotation=0)
    ax[0, 0].set(xlabel="magnitude (events)", ylabel="share", title="mechanism source")
    ax[0, 0].legend(fontsize=8)

    a = ax[0, 1]
    yb = np.arange(1900, 2031, 5)
    for m0, col in ((5.0, "tab:blue"), (5.5, "tab:red"), (6.0, "k"), (7.0, "tab:green")):
        s = ev[ev["mag"] >= m0]
        f = s.groupby(pd.cut(s["year"], yb), observed=False)["mech_src"].apply(lambda v: v.notna().mean() if len(v) else np.nan)
        a.plot(yb[:-1] + 2.5, f.to_numpy(), "o-", ms=3, c=col, label=f"M >= {m0}")
    a.set(xlabel="year", ylabel="share with a mechanism", title="coverage by 5-year bin")
    a.legend()

    gi = pd.Series(np.arange(len(g)), index=g["id"])
    ai = pd.Series(np.arange(len(an)), index=an["id"])
    sd = lambda d, idx, col: d[["strike1", "dip1", "rake1"]].to_numpy(float)[ev[col].map(idx).to_numpy()[m].astype(int)]
    rows = []
    a = ax[1, 0]
    for lab, col_a, d_a, i_a, col_b, d_b, i_b, c in (("ANSS vs GCMT", "anss_id", an, ai, "gcmt_id", g, gi, "tab:blue"),):
        m = ev[col_a].map(i_a).notna().to_numpy() & ev[col_b].map(i_b).notna().to_numpy()
        kg = kagan(sd(d_a, i_a, col_a), sd(d_b, i_b, col_b))
        a.hist(kg, bins=np.arange(0, 121, 5), color=c, alpha=0.7, label=f"{lab} ({m.sum()})")
        rows.append(ev.loc[m].assign(kagan=kg.round(1), pair=lab))
    cm = ev["mech_src"].eq("cabello").to_numpy() & ev["gcmt_id"].map(gi).notna().to_numpy()
    if cm.any():
        m = cm
        kg = kagan(ev.loc[m, ["strike1", "dip1", "rake1"]].to_numpy(float), sd(g, gi, "gcmt_id"))
        a.hist(kg, bins=np.arange(0, 121, 5), histtype="step", color="tab:green", lw=1.5, label=f"Cabello vs GCMT ({m.sum()})")
        rows.append(ev.loc[m].assign(kagan=kg.round(1), pair="Cabello vs GCMT"))
    a.axvline(KAGAN_MAX, c="k", lw=1)
    a.set(yscale="log", xlabel="Kagan angle (deg)", ylabel="events", title="agreement of sources for the same event")
    a.legend()
    kk = pd.concat(rows)
    kk[kk["kagan"] > KAGAN_MAX][["id", "agency", "time_iso", "mag", "depth", "pair", "kagan", "mech_src", "anss_id", "gcmt_id",
                                 "anss_dt", "anss_km", "gcmt_dt", "gcmt_km"]].sort_values("mag", ascending=False).to_csv(
        OUT / "mech_disagree.csv", index=False)

    a = ax[1, 1]
    for s, col in (("anss", "tab:blue"), ("gcmt", "tab:pink"), ("gem", "tab:brown")):
        a.scatter(ev[f"{s}_dt"], ev[f"{s}_km"], s=4, alpha=0.4, c=col, label=f"{s} ({int(ev[f'{s}_dt'].notna().sum())} matched here)")
    a.set(xlabel="match dt (s)", ylabel="match distance (km)", title="matches made in the mech stage")
    a.legend(fontsize=8, markerscale=3)
    fig.tight_layout()
    fig.savefig(OUT / "mech.png", dpi=110)
    plt.close(fig)


def classify_fig(ev):
    fig, ax = plt.subplots(2, 2, figsize=(14, 10))
    order = ["slab_interface", "intra_slab", "slab_deep", "forearc", "intraarc", "backarc", "patagonia_crustal", "patagonia_interface", "outer_rise",
             "deep_nest", "deep_unknown", "unclassified", "unresolved"]
    mb = np.arange(4.0, 8.01, 0.5)
    t = pd.crosstab(pd.cut(ev["mag"], mb), ev["class"])
    t = t[[c for c in order if c in t]]
    t.plot.bar(stacked=True, ax=ax[0, 0], width=0.85, cmap="tab10")
    ax[0, 0].set(yscale="log", xlabel="magnitude", ylabel="events", title="classes by magnitude")
    ax[0, 0].set_xticklabels([f"{i.left:.1f}" for i in t.index], rotation=0)
    ax[0, 0].legend(fontsize=7)

    a = ax[0, 1]
    names = ev["cls_rule"].value_counts().index
    for m0, c, off in ((C.MMIN, "0.6", -0.2), (5.5, "tab:red", 0.2)):
        v = ev.loc[ev["mag"] >= m0, "cls_rule"].value_counts().reindex(names).fillna(0)
        a.barh(np.arange(len(names)) + off, v.to_numpy(), height=0.4, color=c, label=f"M >= {m0}")
    a.set_yticks(np.arange(len(names)), names, fontsize=8)
    a.set(xscale="log", xlabel="events", title="deciding rule (see classify.py)")
    a.legend()

    a = ax[1, 0]
    for c in ("slab_interface", "intra_slab", "slab_deep", "forearc"):
        v = ev.loc[ev["class"] == c, "dz"].dropna()
        a.hist(v, bins=np.arange(-80, 121, 2), histtype="step", lw=1.5, label=f"{c} ({len(v)})")
    a.axvline(0, c="k", lw=0.8)
    a.set(xlabel="depth - Slab2 top (km), depth known", ylabel="events", title="position relative to the slab top")
    a.legend(fontsize=8)

    a = ax[1, 1]
    if C.OLD_CLASSIFIED.exists():
        o = pd.read_csv(C.OLD_CLASSIFIED, usecols=["id", "class"], dtype={"id": str}, low_memory=False)
        m = ev[["id", "class", "mag", "time_iso", "depth", "depth_status", "mech_src", "cls_rule"]].merge(
            o.rename(columns={"class": "old"}), on="id", how="left")
        m["old"] = m["old"].fillna("(not in old)")
        tt = pd.crosstab(m["old"], m["class"])
        a.imshow(np.log10(tt.to_numpy() + 1), cmap="Blues", aspect="auto")
        a.set_xticks(range(len(tt.columns)), tt.columns, rotation=60, ha="right", fontsize=7)
        a.set_yticks(range(len(tt.index)), tt.index, fontsize=7)
        for (i, j), v in np.ndenumerate(tt.to_numpy()):
            if v:
                a.text(j, i, v, ha="center", va="center", fontsize=6)
        a.set(xlabel="new class", ylabel="old class", title="old -> new, same Cabello id (all magnitudes)")
        tt.to_csv(OUT / "class_transitions.csv")
        m[(m["old"] != m["class"]) & (m["mag"] >= 5.5)].sort_values("mag", ascending=False).to_csv(
            OUT / "class_changes.csv", index=False)
    else:
        a.text(0.5, 0.5, f"no old classification at\n{C.OLD_CLASSIFIED}", ha="center", transform=a.transAxes)
    fig.tight_layout()
    fig.savefig(OUT / "classify.png", dpi=110)
    plt.close(fig)


STYLE = {"deep_unknown": ("k", 2), "unclassified": ("0.6", 2), "backarc": ("olive", 3), "patagonia_crustal": ("tab:olive", 3), "patagonia_interface": ("mediumseagreen", 5), "outer_rise": ("tab:purple", 3), "intraarc": ("tab:brown", 3),
         "forearc": ("tab:orange", 4), "slab_interface": ("tab:green", 5), "slab_deep": ("tab:red", 6),
         "intra_slab": ("tab:blue", 7), "deep_nest": ("magenta", 8), "unresolved": ("cyan", 9)}


def trench_frame(line, step=2.0):
    """Trench densified every ~step km: lon, lat, along-trench km, unit tangent (east, north) smoothed over +/-30 km."""
    n = max(int(S.hav(*line.coords[0], *line.coords[-1]) / step) * 3, 50)
    p = [line.interpolate(f, normalized=True) for f in np.linspace(0, 1, n)]
    lo, la = np.array([q.x for q in p]), np.array([q.y for q in p])
    s = np.r_[0, np.cumsum(S.hav(lo[:-1], la[:-1], lo[1:], la[1:]))]
    w = max(1, int(np.searchsorted(s, 30.0)))
    i0, i1 = np.clip(np.arange(n) - w, 0, n - 1), np.clip(np.arange(n) + w, 0, n - 1)
    te, tn = (lo[i1] - lo[i0]) * np.cos(np.radians(la)), la[i1] - la[i0]
    h = np.hypot(te, tn)
    return lo, la, s, te / h, tn / h


def trenches():
    import geopandas as gpd
    import shapely
    nz = shapely.line_merge(shapely.union_all(gpd.read_file(C.TRENCH_SHP).to_crs(4326).geometry.values))
    if nz.geom_type != "LineString":
        nz = max(nz.geoms, key=lambda g: g.length)
    an, _ = K.footprint()
    return {"nazca": nz, "antarctic": an}


def transects():
    """
    Sections north to south. Each: label, family, trench point (lon0, lat0), landward
    unit vector u (east, north) perpendicular to the trench, half-width across (km).

    Nazca: one per SECTION_LATS, bounded by the lines parallel to the transect
    through the points 1 deg north and south of its trench point. Antarctic: every
    2 x SECTION_HALF_KM along the trench, bounded SECTION_HALF_KM either side
    (the trench turns east-west there, where a north-south offset has no width).
    """
    out = []
    for fam, line in trenches().items():
        lo, la, s, te, tn = trench_frame(line)
        if fam == "nazca":
            js = [int(np.argmin(np.abs(la - v))) for v in C.SECTION_LATS if la.min() <= v <= la.max() and v > C.SOUTH_LAT]
        else:
            js = [min(int(np.searchsorted(s, v)), len(s) - 1) for v in np.arange(C.SECTION_HALF_KM, s[-1], 2 * C.SECTION_HALF_KM)]
        for j in js:
            u = np.array([tn[j], -te[j]])
            pe, pn = lo[j] + 0.5 * u[0] / np.cos(np.radians(la[j])), la[j] + 0.5 * u[1]
            if K.seaward(line, np.array([pe]), np.array([pn]))[0]:
                u = -u
            half = C.SECTION_HALF_KM * abs(u[0]) if fam == "nazca" else C.SECTION_HALF_KM
            out.append({"fam": fam, "lon0": lo[j], "lat0": la[j], "u": u, "half": half})
    out.sort(key=lambda t: -t["lat0"])
    for i, t in enumerate(out):
        t["label"] = f"{'N' if t['fam'] == 'nazca' else 'A'}{i + 1:02d}"
    return out


def proj(t, lon, lat):
    """Distance along the transect (landward positive) and across it, km."""
    e = (np.asarray(lon) - t["lon0"]) * 111.195 * np.cos(np.radians(t["lat0"]))
    n = (np.asarray(lat) - t["lat0"]) * 111.195
    u = t["u"]
    return e * u[0] + n * u[1], -e * u[1] + n * u[0]


def unproj(t, x, y):
    u = t["u"]
    e, n = x * u[0] - y * u[1], x * u[1] + y * u[0]
    return t["lon0"] + e / (111.195 * np.cos(np.radians(t["lat0"]))), t["lat0"] + n / 111.195


def outline(a, t, color, lw):
    x0, x1 = C.SECTION_X[t["fam"]]
    for y, ls in ((0, "-"), (t["half"], "--"), (-t["half"], "--")):
        a.plot(*unproj(t, np.array([x0, x1]), np.array([y, y])), color=color, lw=lw, ls=ls)


def family(c):
    return "interface" if c in ("slab_interface", "patagonia_interface") else (
        "in-slab" if c in ("intra_slab", "slab_deep", "deep_nest") else "other")


def labels(a, e, xcol, ycol, nmax=None, sep=None):
    """
    Label events above LABEL_M of their family next to their marker, avoiding overlaps
    (set the axis limits first). With nmax and sep: largest first, at most nmax, none
    within sep (data units) of one already labelled.
    """
    m = [r["mag"] >= C.LABEL_M[family(r["class"])] for _, r in e.iterrows()]
    e = e[np.array(m, bool)] if len(e) else e
    if nmax is not None and len(e):
        keep = []
        for i, r in e.sort_values("mag", ascending=False).iterrows():
            if all(np.hypot(r[xcol] - e.at[j, xcol], r[ycol] - e.at[j, ycol]) > sep for j in keep):
                keep.append(i)
            if len(keep) == nmax:
                break
        e = e.loc[keep]
    fig = a.figure
    k = 72.0 / fig.dpi
    placed = []
    for _, r in e.sort_values(ycol).iterrows():
        t = f"{r['time_iso'][:4]} M{r['mag']:.1f}"
        px, py = a.transData.transform((r[xcol], r[ycol])) * k
        w, h = 4.2 * len(t), 8
        for dx, dy in ((5, 3), (5, -11), (-5 - w, 3), (-5 - w, -11), (5, 14), (5, -22), (-5 - w, 14), (-5 - w, -22), (5, 25), (5, -33)):
            bx, by = px + dx, py + dy
            if all(bx > q[0] + q[2] or bx + w < q[0] or by > q[1] + q[3] or by + h < q[1] for q in placed):
                break
        placed.append((bx, by, w, h))
        a.annotate(t, (r[xcol], r[ycol]), xytext=(dx, dy), textcoords="offset points", fontsize=6.5,
                   arrowprops={"arrowstyle": "-", "lw": 0.4, "color": "0.3"}, zorder=20)


def locator(a, ev, ts, t=None):
    for line in trenches().values():
        a.plot(*line.xy, "k-", lw=0.8)
    e5 = ev[ev["mag"] >= 5.5]
    a.scatter(e5["longitude"], e5["latitude"], s=1, c="0.75", lw=0)
    for tt in ts:
        if t is None:
            outline(a, tt, "0.5", 0.5)
            a.text(tt["lon0"] - 1.0, tt["lat0"], tt["label"], fontsize=7, ha="right", va="center")
    if t is not None:
        outline(a, t, "tab:red", 1.0)
    a.set(xlim=(-84, -58), ylim=(-60, -10), aspect=1 / np.cos(np.radians(35)))
    a.tick_params(labelsize=7)


def sections(ev):
    sl, _ = K.slab()
    ts = transects()
    with PdfPages(OUT / "sections.pdf") as pdf:
        for t in ts:
            x, y = proj(t, ev["longitude"].to_numpy(), ev["latitude"].to_numpy())
            x0, x1 = C.SECTION_X[t["fam"]]
            m = (np.abs(y) <= t["half"]) & (x >= x0) & (x <= x1)
            if not m.any():
                continue
            e = ev[m].assign(x=x[m])
            sx, sy = proj(t, sl["lon"].to_numpy(), sl["lat"].to_numpy())
            sm = (np.abs(sy) <= t["half"]) & (sx >= x0) & (sx <= x1)
            n = sl[sm].assign(x=sx[sm], bot=lambda d: d["dep"] + d["thk"])
            fig = plt.figure(figsize=(19, 12))
            gs = fig.add_gridspec(2, 2, width_ratios=[4, 1])
            ax = [fig.add_subplot(gs[0, 0])]
            ax.append(fig.add_subplot(gs[1, 0], sharex=ax[0]))
            locator(fig.add_subplot(gs[:, 1]), ev, ts, t)
            for a, lab in ((ax[0], f"all, M > {C.MMIN}"), (ax[1], "M >= 5.5")):
                a.axvline(0, c="k", lw=0.8)
                if len(n):
                    g = n.groupby(pd.cut(n["x"], np.arange(x0, x1 + 10, 10)), observed=True).agg(
                        x=("x", "median"), top_lo=("dep", "min"), top_hi=("dep", "max"), bot_lo=("bot", "min"), bot_hi=("bot", "max"),
                        top=("dep", "median"))
                    a.fill_between(g["x"], g["top_lo"], g["bot_hi"], color="0.45", alpha=0.18, lw=0, zorder=0,
                                   label="plate (Slab2 top to top + thk)")
                    a.fill_between(g["x"], g["top_lo"], g["top_hi"], color="0.35", alpha=0.45, lw=0, zorder=1, label="Slab2 top")
                    a.plot(g["x"], g["bot_lo"], "-", color="tab:cyan", lw=1.0, zorder=1, label="plate bottom")
                    a.plot(g["x"], g["bot_hi"], "-", color="tab:cyan", lw=0.6, alpha=0.5, zorder=1)
                    w = g[g["top"] < C.IF_MAX_TOP]
                    a.fill_between(w["x"], w["top"] - C.IF_TOL["free"], w["top"] + C.IF_TOL["free"], color="tab:green", alpha=0.08,
                                   label=f"interface band +/-{C.IF_TOL['free']:.0f} km")
                if t["fam"] == "antarctic":
                    a.add_patch(plt.Rectangle((0, 0), C.PAT_WIDTH_KM, C.PAT_MAX_Z, color="mediumseagreen", alpha=0.1,
                                              label="patagonia_interface footprint"))
                sub = e if lab.startswith("all") else e[e["mag"] >= 5.5]
                xs = sub["x"].to_numpy()
                unk = sub["depth_status"].isin(C.UNKNOWN_DEPTH).to_numpy()
                sz = 3 if len(sub) > 3000 else (6 if len(sub) > 500 else 14 * (sub["mag"].to_numpy() - 4.5) ** 2)
                for c, (col, zo) in STYLE.items():
                    kk = (sub["class"] == c).to_numpy()
                    if kk.any():
                        for sel, face in ((kk & ~unk, col), (kk & unk, "none")):
                            a.scatter(xs[sel], sub["depth"].to_numpy()[sel], s=sz if np.isscalar(sz) else sz[sel], facecolors=face,
                                      edgecolors=col, lw=0.8 if face == "none" else 0, alpha=0.7, zorder=zo + 2,
                                      label=f"{c} ({int(kk.sum())})" if face != "none" else None)
                a.set(xlim=(x0, x1), ylim=(300, -5), ylabel="depth (km)",
                      title=f"{t['label']}: {t['fam']} trench at {t['lat0']:.1f} deg, {lab}; "
                            f"{2 * t['half']:.0f} km wide; hollow: depth unknown")
                a.legend(fontsize=7, ncol=4, loc="lower left")
                if lab == "M >= 5.5":
                    labels(a, sub.assign(d=sub["depth"]), "x", "d")
            ax[1].set_xlabel(f"km along the transect from the {t['fam']} trench, perpendicular to it (negative seaward)")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
    fig, a = plt.subplots(figsize=(9, 16))
    locator(a, ev, ts)
    a.set_title("sections as in sections.pdf, north to south: transect (solid) and bounds (dashed)", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sections_map.png", dpi=110)
    plt.close(fig)


GROUPS = {"interface": ["slab_interface", "patagonia_interface"], "in-slab": ["intra_slab", "slab_deep", "deep_nest"],
          "crustal": ["forearc", "intraarc", "backarc", "patagonia_crustal"],
          "other": ["outer_rise", "deep_unknown", "unclassified", "unresolved"]}


def map_fig(ev):
    import geopandas as gpd
    tr = gpd.read_file(C.TRENCH_SHP).to_crs(4326)
    an, fp = K.footprint()
    e = ev[ev["mag"] >= 5.5]
    fig, ax = plt.subplots(1, 4, figsize=(18, 13), sharey=True)
    for a, (g, cl) in zip(ax, GROUPS.items()):
        tr.plot(ax=a, color="k", lw=0.8)
        a.plot(*an.xy, color="k", lw=0.8, ls="--")
        gpd.GeoSeries([fp]).plot(ax=a, color="mediumseagreen", alpha=0.12)
        for c in cl:
            s = e[e["class"] == c]
            a.scatter(s["longitude"], s["latitude"], s=3 * 2.2 ** (s["mag"] - 5.5), c=STYLE[c][0], alpha=0.6, lw=0,
                      label=f"{c} ({len(s)})")
        o = e[e["class"].isin(cl) & e["cls_rule"].eq("override")]
        a.scatter(o["longitude"], o["latitude"], s=60, facecolors="none", edgecolors="k", lw=1.2,
                  label=f"class set by hand, overrides.csv ({len(o)})")
        a.set(xlim=(-80, -62), ylim=(-59, -12), aspect="equal",
              title=f"{g}, M >= 5.5")
        labels(a, e[e["class"].isin(cl)], "longitude", "latitude", C.MAP_LABEL_N, C.MAP_LABEL_DEG)
        a.legend(fontsize=7, loc="lower left")
    fig.suptitle("solid: Nazca trench; dashed: Antarctic trench (Bird 2003); green: patagonia_interface footprint; "
                 f"labels: up to {C.MAP_LABEL_N} per panel, largest first, {C.MAP_LABEL_DEG:g} deg apart (interface M >= {C.LABEL_M['interface']}, "
                 f"in-slab M >= {C.LABEL_M['in-slab']}, others M >= {C.LABEL_M['other']})", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUT / "map.png", dpi=110)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    x, g = S.cabello(), S.gcmt()
    x, _ = B.pre_overrides(x)
    ev, grp, info, r = B.dedup(x, g)
    p = pairs_all(r)
    figures(r, ev, p)
    q = p[p["cross"] & ~p["merged"] & (p["dt"] <= NEAR_DT) & (p["dkm"] <= NEAR_KM)]
    k = ["id", "agency", "time_iso", "longitude", "latitude", "depth", "mag"]
    nm = pd.concat([r.loc[q["ia"], k].reset_index(drop=True).add_suffix("_a"), r.loc[q["ib"], k].reset_index(drop=True).add_suffix("_b"),
                    q[["dt", "dkm", "dz", "dm", "m"]].round(2).reset_index(drop=True)], axis=1).sort_values("m", ascending=False)
    nm.to_csv(OUT / "near_misses.csv", index=False)
    summary(r, ev, grp)
    el = B.locate(ev, r, S.potin(), g)[0]
    locate_fig(el)
    an = S.anss()
    em = B.mech(el, r, g, an, S.gem())[0]
    mech_fig(em, g, an)
    ec = B.post_overrides(B.classify(em)[0])[0]
    classify_fig(ec)
    sections(ec)
    map_fig(ec)
    n = gallery(r, grp, p)
    cr = p[p["cross"]]
    bg = ((cr["dt"] > C.WIDE_DT / 2) & (cr["dkm"] <= C.DUP_KM)).sum() * C.DUP_DT / (C.WIDE_DT / 2)
    print(f"cross-agency pairs in the wide windows: {len(cr)}, merged {int(cr['merged'].sum())}; "
          f"near misses ({NEAR_DT:.0f} s, {NEAR_KM:.0f} km): {len(q)}, M >= 5: {int((q['m'] >= 5).sum())}; "
          f"chance pairs expected inside the merge window: {bg:.1f}; panels in groups.pdf: {n}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()