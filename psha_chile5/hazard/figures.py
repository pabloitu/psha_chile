# Presentation figures from what is already on disk.
#   f01_curves.png/.csv mean hazard curve per city with 16-84 % band and the
#                       three family curves, 475 and 2475 yr marked; f01b: in-slab classes
#   f02_contrib.png     contribution per family and per in-slab class, both RPs
#   f03_sources.png     map of the source model: interface traces, in-slab and
#                       crustal smoothed rates, faults, cities
#   f05_truncation.png  PGA against truncation level and the curves per level
#   f06_declustering.png/.csv  curves per city, declustered vs full catalog
# Outputs: outputs/hazard/_pres/

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import re

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
from hazard import config as hc
from hazard.post import load, iml
from lib import smooth

# settings
TOTAL = "disagg"                      # job of the full model (any classical/disagg job)
FAMS = [("c_if_ref", "Interface", "#4c72b0", "-"), ("c_is_ref", "Intraslab", "#c44e52", "-"),
        ("c_cr_ref", "Crustal", "#55a868", "-")]
DOMAINS = FAMS[:1] + [("c_is_intra_slab", "intra_slab", "#dd8452", "--"),
                      ("c_is_slab_deep", "slab_deep", "#c44e52", "--"),
                      ("c_is_deep_nest", "deep_nest", "#8172b3", "--")] + FAMS[2:]
CONTRIB = hc.OUT_ROOT / "_contrib" / "full_ref" / "contributions.csv"
CLASSES = hc.OUT_ROOT / "_contrib" / "full_classes" / "contributions.csv"
GRIDS = [(paths.OUT / "intraslab" / "ref" / "ssm" / "grid_total.csv", "in-slab", "Reds"),
         (paths.OUT / "crustal" / "ref" / "ssm" / "grid_total.csv", "crustal", "Greens")]
IF_NRML = paths.OUT / "interface" / "mmin_haz-5.5" / "nrml"
FAULT_NRML = paths.OUT / "crustal" / "ref" / "nrml"     # fault traces are read from the first xml here
IMT = "PGA"
SECTION_SITES = ("iquique", "santiago_centro")
TRUNC = {2.0: "tr20", 2.5: "tr25", 3.0: "ref", 4.0: "tr40"}   # truncation level: job suffix
TRUNC_SITES = ("santiago_centro", "iquique", "concepcion")
SECTION_DLAT = 0.75
OUT = hc.OUT_ROOT / "_pres"


def mean_curve(job, imt=IMT):
    r = load(job)
    m = list(r["imtls"]).index(imt)
    return r, np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :]), np.asarray(r["imtls"][imt])


def fig_curves(path, fams=None):
    fams = fams or FAMS
    r, tot, lv = mean_curve(TOTAL)
    q = np.quantile(r["curves"][:, :, list(r["imtls"]).index(IMT), :], [0.16, 0.84], axis=1)
    fam = []
    for job, lab, col, ls in fams:
        try:
            fam.append((lab, col, ls, mean_curve(job)[1]))
        except (SystemExit, FileNotFoundError) as e:
            print(f"[skip] {job}: not run ({e})")
    sites = r["info"]["site_names"]
    n = len(sites)
    f, axs = plt.subplots(2, (n + 1) // 2, figsize=(2.9 * ((n + 1) // 2), 7), sharex=True, sharey=True,
                          squeeze=False)
    for ax, s in zip(axs.ravel(), range(n)):
        ax.fill_between(lv, np.maximum(q[0, s], 1e-8), np.maximum(q[1, s], 1e-8), color="0.8", label="16-84 %")
        for lab, col, ls, c in fam:
            ax.loglog(lv, np.maximum(c[s], 1e-8), color=col, ls=ls, lw=1.2, label=lab)
        ax.loglog(lv, np.maximum(tot[s], 1e-8), "k", lw=2, label="total")
        for p in hc.POES:
            ax.axhline(p, color="0.6", lw=0.6, ls=":")
            x = iml(tot[s], lv, p)
            ax.plot([x], [p], "ko", ms=3)
            ax.annotate(f"{x:.2f} g", (x, p), fontsize=6, xytext=(2, 3), textcoords="offset points")
        ax.set_title(sites[s].replace("_", " "), fontsize=9)
        ax.set_ylim(1e-4, 1)
        ax.set_xlim(lv[0], lv[-1])
        ax.grid(alpha=0.3, which="both")
    axs[0][0].legend(fontsize=6)
    for ax in axs[-1]:
        ax.set_xlabel(f"{IMT} (g)")
    for ax in axs[:, 0]:
        ax.set_ylabel(f"annual PoE (Vs30 {hc.VS30:g})")
    f.suptitle("mean hazard curves, full source and GMM tree", fontsize=11)
    f.tight_layout()
    f.savefig(path, dpi=220)
    plt.close(f)
    rows = [{"site": sites[s], "domain": "total", "level": x, "poe": y} for s in range(n) for x, y in zip(lv, tot[s])]
    for lab, _, _, c in fam:
        rows += [{"site": sites[s], "domain": lab, "level": x, "poe": y} for s in range(n) for x, y in zip(lv, c[s])]
    pd.DataFrame(rows).to_csv(Path(path).with_suffix(".csv"), index=False)


def fig_contrib(path):
    if not CONTRIB.exists():
        print(f"[skip] {CONTRIB} missing")
        return
    a = pd.read_csv(CONTRIB)
    parts = [("Interface", "#4c72b0"), ("Intraslab", "#c44e52"), ("Crustal", "#55a868")]
    b = pd.read_csv(CLASSES) if CLASSES.exists() else None
    if b is not None:
        parts = [("Interface", "#4c72b0"), ("intra_slab", "#dd8452"), ("slab_deep", "#c44e52"),
                 ("deep_nest", "#8172b3"), ("Crustal", "#55a868")]
    sites = [s for s in hc.CITIES if s in set(a["site"])]
    rps = sorted(a["return_period"].unique())
    f, axs = plt.subplots(1, len(rps), figsize=(5.6 * len(rps), 0.45 * len(sites) + 2), sharey=True)
    for ax, rp in zip(np.atleast_1d(axs), rps):
        t = a[a["return_period"] == rp].set_index("site").loc[sites]
        if b is not None:
            cl = b[b["return_period"] == rp].set_index("site").loc[sites]
            for k in ("intra_slab", "slab_deep", "deep_nest"):
                t[k] = cl[k]
        y, left = np.arange(len(sites)), np.zeros(len(sites))
        for k, col in parts:
            v = t[k].fillna(0).to_numpy()
            ax.barh(y, v, 0.72, left=left, color=col, edgecolor="white", lw=0.5, label=k)
            left += v
        for yy, g in zip(y, t["iml_total"]):
            ax.text(101, yy, f"{g:.2f} g", va="center", fontsize=7)
        ax.set_xlim(0, 100)
        ax.set_xlabel("share of the exceedance rate (%)")
        ax.set_title(f"{IMT} {rp} yr", fontsize=10)
        ax.grid(axis="x", alpha=0.3)
    a0 = np.atleast_1d(axs)[0]
    a0.set_yticks(np.arange(len(sites)))
    a0.set_yticklabels([s.replace("_", " ") for s in sites])
    a0.invert_yaxis()
    a0.legend(fontsize=7, loc="lower left")
    f.suptitle("share of the exceedance rate per source", fontsize=11)
    f.tight_layout()
    f.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(f)


def traces(d, tag, ncol):
    """(lon, lat) of every fault trace in the first nrml file of d that has tag."""
    out = []
    for f in sorted(d.glob("*.xml")) if d.exists() else []:
        t = f.read_text()
        for blk in re.findall(rf"<{tag}>.*?</gml:posList>", t, re.S):
            v = np.array(re.findall(r"-?\d+\.?\d*", blk.split("<gml:posList>")[1]), float)
            out.append(v.reshape(-1, ncol)[:, :2])
        if out:
            break
    return out


def fig_sources(path):
    f, axs = plt.subplots(1, 3, figsize=(12, 9), sharey=True)
    for ax, (g, lab, cmap) in zip(axs[1:], GRIDS):
        if not Path(g).exists():
            ax.text(0.5, 0.5, f"{lab}: missing", ha="center", transform=ax.transAxes)
            continue
        df, rb, e = smooth.read(g)
        v = rb.sum(axis=1)
        top = np.log10(v.max())
        s = ax.scatter(df["lon"], df["lat"], c=np.log10(np.maximum(v, 1e-12)), s=2, cmap=cmap,
                       vmin=top - 3, vmax=top)
        f.colorbar(s, ax=ax, shrink=0.5, label=f"log10 N(>={e[0]:.1f})/yr per cell")
        ax.set_title(f"{lab} smoothed rates", fontsize=10)
    tr = traces(IF_NRML, "faultTopEdge", 3)
    for t in tr:
        axs[0].plot(t[:, 0], t[:, 1], "-", color="#4c72b0", lw=1.2)
    axs[0].set_title(f"interface: {len(tr)} source top edges", fontsize=10)
    fl = traces(FAULT_NRML, "simpleFaultGeometry", 2)
    for t in fl:
        axs[2].plot(t[:, 0], t[:, 1], "-", color="0.2", lw=0.6)
    axs[2].set_title(f"crustal smoothed rates and {len(fl)} faults", fontsize=10)
    for ax in axs:
        for n, (x, y) in hc.CITIES.items():
            ax.plot(x, y, "k^", ms=5)
            ax.annotate(n.replace("_", " "), (x, y), fontsize=6, xytext=(4, -2), textcoords="offset points")
        ax.set_aspect("equal")
        ax.set_xlabel("lon")
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("lat")
    f.suptitle("source model", fontsize=11)
    f.tight_layout()
    f.savefig(path, dpi=200)
    plt.close(f)


def fig_section(path, sites=SECTION_SITES, dlat=SECTION_DLAT):
    """Depth section per city: in-slab sources at their Slab2 depth, interface profile."""
    sites = [x for x in sites if x in hc.CITIES]
    f, axs = plt.subplots(1, len(sites), figsize=(6.2 * len(sites), 5), sharey=True)
    ifp = traces(IF_NRML, "faultTopEdge", 3) + traces(IF_NRML, "faultBottomEdge", 3)
    edges = []
    for f_ in sorted(IF_NRML.glob("*.xml")) if IF_NRML.exists() else []:
        t = f_.read_text()
        for blk in re.findall(r"<(?:faultTopEdge|intermediateEdge|faultBottomEdge)>.*?</gml:posList>", t, re.S):
            edges.append(np.array(re.findall(r"-?\d+\.?\d*", blk.split("<gml:posList>")[1]),
                                  float).reshape(-1, 3))
        if edges:
            break
    for ax, site in zip(np.atleast_1d(axs), sites):
        x0, y0 = hc.CITIES[site]
        for g, lab, col in ((GRIDS[0][0], "in-slab", "Reds"), (GRIDS[1][0], "crustal", "Greens")):
            if not Path(g).exists():
                continue
            df, rb, e = smooth.read(g)
            m = np.abs(df["lat"] - y0) <= dlat
            z = df["slab_km"] + 7.5 if "slab_km" in df else np.full(len(df), 10.0)
            v = np.log10(np.maximum(rb.sum(axis=1), 1e-12))
            sc = ax.scatter(df["lon"][m], z[m], c=v[m], s=14, cmap=col, vmin=v.max() - 3, vmax=v.max())
            if lab == "in-slab":
                f.colorbar(sc, ax=ax, shrink=0.7, label=f"log10 N(>={e[0]:.1f})/yr per cell")
        for v in edges:
            m = np.abs(v[:, 1] - y0) <= dlat
            if m.sum() > 1:
                ax.plot(v[m, 0], v[m, 2], "-", color="#4c72b0", lw=2)
        ax.plot([x0], [0], "k^", ms=10, clip_on=False)
        ax.annotate(site.replace("_", " "), (x0, 0), fontsize=9, xytext=(6, 2), textcoords="offset points")
        for r in (50, 100, 150):
            a = np.linspace(0, np.pi, 100)
            ax.plot(x0 + r * np.cos(a) / (111 * np.cos(np.radians(y0))), r * np.sin(a), "0.7", lw=0.6, ls=":")
            ax.annotate(f"{r} km", (x0 - r / (111 * np.cos(np.radians(y0))), 0), fontsize=6, color="0.5")
        ax.set_xlabel("longitude")
        ax.set_title(f"{site.replace('_', ' ')}: sources within {dlat:g} deg of latitude", fontsize=10)
        ax.grid(alpha=0.3)
    a0 = np.atleast_1d(axs)[0]
    a0.set_ylabel("depth (km)")
    a0.set_ylim(250, -5)
    f.suptitle("cross sections: where the model puts earthquakes below each city", fontsize=11)
    f.tight_layout()
    f.savefig(path, dpi=220)
    plt.close(f)


def total(suffix):
    """Mean curve (sites, levels) of the full model from the three family jobs c_<fam>_<suffix>."""
    sv, lv = None, None
    for f in ("if", "is", "cr"):
        r, c, lv = mean_curve(f"c_{f}_{suffix}")
        sv = (1 - c) if sv is None else sv * (1 - c)
    return r, 1 - sv, lv


def fig_trunc(path):
    """PGA against truncation level per city, and the curves of the first city."""
    runs = {}
    for t, suf in TRUNC.items():
        try:
            runs[t] = total(suf)
        except (SystemExit, FileNotFoundError) as e:
            print(f"[skip] truncation {t}: {e}")
    if len(runs) < 2:
        return
    r0 = next(iter(runs.values()))[0]
    names = r0["info"]["site_names"]
    sites = [x for x in TRUNC_SITES if x in names]
    ts = sorted(runs)
    f, axs = plt.subplots(1, 2, figsize=(10.5, 4.2))
    for i, site in enumerate(sites):
        s = names.index(site)
        for p, ls in zip(hc.POES, ("-", "--")):
            y = [iml(runs[t][1][s], runs[t][2], p) for t in ts]
            axs[0].plot(ts, y, ls, marker="o", ms=4, color=f"C{i}",
                        label=site.replace("_", " ") if ls == "-" else None)
    axs[0].axvline(3.0, color="0.5", lw=0.7, ls=":")
    axs[0].set_xticks(ts)
    axs[0].set_xlabel("truncation level, sigma")
    axs[0].set_ylabel("PGA g")
    axs[0].set_title("solid 475 yr, dashed 2475 yr", fontsize=9)
    axs[0].legend(fontsize=8)
    s = names.index(sites[0])
    for j, t in enumerate(ts):
        _, c, lv = runs[t]
        axs[1].loglog(lv, np.maximum(c[s], 1e-8), color=plt.get_cmap("viridis")(j / (len(ts) - 1)),
                      lw=2.2 if t == 3.0 else 1.3, label=f"{t:g}")
    for p in hc.POES:
        axs[1].axhline(p, color="0.6", lw=0.6, ls=":")
    axs[1].set_xlim(0.1, 4)
    axs[1].set_ylim(1e-4, 1e-1)
    axs[1].set_xlabel("PGA g")
    axs[1].set_ylabel("annual PoE")
    axs[1].set_title(sites[0].replace("_", " "), fontsize=9)
    axs[1].legend(title="truncation", fontsize=8, title_fontsize=8)
    for ax in axs:
        ax.grid(alpha=0.3, which="both")
    f.suptitle(f"truncation of the GMM distribution, full model, vs30 {hc.VS30:g}", fontsize=10)
    f.tight_layout()
    f.savefig(path, dpi=300)
    plt.close(f)




def fig_rows(path, rows, title, fams=("if", "is", "cr")):
    """
    Hazard curves per city for several full-model rows (suffix per row), total
    solid and one family dotted, with the PGA at the target PoEs written to a csv.
    """
    runs = {}
    for lab, suf in rows.items():
        try:
            runs[lab] = total(suf)
        except (SystemExit, FileNotFoundError) as e:
            print(f"[skip] {lab}: {e}")
    if len(runs) < 2:
        return
    names = next(iter(runs.values()))[0]["info"]["site_names"]
    n = len(names)
    f, axs = plt.subplots(2, (n + 1) // 2, figsize=(2.9 * ((n + 1) // 2), 7), sharex=True, sharey=True,
                          squeeze=False)
    out = []
    for s_, (ax, site) in enumerate(zip(axs.ravel(), names)):
        for j, (lab, (r, c, lv)) in enumerate(runs.items()):
            ax.loglog(lv, np.maximum(c[s_], 1e-8), color=f"C{j}", lw=1.8, label=lab)
            for fam in fams:
                try:
                    _, cf, _ = mean_curve(f"c_{fam}_{rows[lab]}")
                    ax.loglog(lv, np.maximum(cf[s_], 1e-8), color=f"C{j}", lw=0.8, ls=":")
                except (SystemExit, FileNotFoundError):
                    pass
            out += [{"site": site, "row": lab, "return_period": round(-hc.INV_TIME / np.log(1 - p)),
                     "PGA": iml(c[s_], lv, p)} for p in hc.POES]
        for p in hc.POES:
            ax.axhline(p, color="0.6", lw=0.6, ls=":")
        ax.set_xlim(0.05, 4)
        ax.set_ylim(1e-4, 1e-1)
        ax.set_title(site.replace("_", " "), fontsize=9)
        ax.grid(alpha=0.3, which="both")
    axs[0][0].legend(fontsize=7)
    for ax in axs[-1]:
        ax.set_xlabel("PGA g")
    for ax in axs[:, 0]:
        ax.set_ylabel("annual PoE")
    f.suptitle(f"{title}; solid total, dotted families", fontsize=10)
    f.tight_layout()
    f.savefig(path, dpi=300)
    plt.close(f)
    t = pd.DataFrame(out)
    t.to_csv(Path(path).with_suffix(".csv"), index=False)
    piv = t.pivot_table(index=["site", "return_period"], columns="row", values="PGA", sort=False)
    ref = list(rows)[0]
    for lab in list(rows)[1:]:
        piv[f"{lab} %"] = 100 * (piv[lab] / piv[ref] - 1)
    print(f"\n{title}")
    print(piv.round(3).to_string())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig_curves(OUT / "f01_curves.png")
    fig_curves(OUT / "f01b_curves_domains.png", DOMAINS)
    fig_contrib(OUT / "f02_contrib.png")
    fig_sources(OUT / "f03_sources.png")
    fig_section(OUT / "f04_sections.png")
    fig_trunc(OUT / "f05_truncation.png")
    fig_rows(OUT / "f06_declustering.png", {"declustered (gk74)": "ref", "full catalog": "raw"},
             "declustered vs full catalog, full model")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()