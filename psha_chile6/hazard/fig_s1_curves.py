# S1: mean PGA hazard curves per city and tectonic class, psha_chile5 (dashed) against
# psha_chile6 (solid): interface, the three in-slab classes, crustal and the total
# (families combined in rate space). EXTRA overlays the total of other runs of this
# tree, e.g. a classification variant: family -> job, the rest at the reference.
# Outputs: outputs/s1/08_curves.png, 08_curves_<city>.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
from hazard import config as hc
from hazard import logic_tree as lt
from hazard.post import load

# settings
ROOTS = {"old": paths.PREV / "outputs" / "hazard" / hc.SITE, "new": hc.OUT_ROOT}
PARTS = {"interface": ("c_if_ref", "#4c72b0"), "intra_slab": ("c_is_intra_slab", "#dd8452"),
         "slab_deep": ("c_is_slab_deep", "#c44e52"), "deep_nest": ("c_is_deep_nest", "#8172b3"),
         "crustal": ("c_cr_ref", "#55a868")}
EXTRA = {"rates gk74": {"interface": "c_if_rate_gk74", "intraslab": "c_is_rate_gk74", "crustal": "c_cr_rate_gk74"},
         "in-slab window_T": {"intraslab": "c_is_smooth_window_T"}, "crustal window_T": {"crustal": "c_cr_smooth_window_T"},
         "if AG20": {"interface": "c_if_gmm_ag"}, "if Parker": {"interface": "c_if_gmm_pk"},
         "if Kuehn": {"interface": "c_if_gmm_ku"}}
IMT = "PGA"
XLIM, YLIM = (0.02, 4.0), (1e-5, 1e-1)
OUT = paths.OUT / "s1"


def mean(job, root):
    try:
        r = load(job, root=root)
    except (SystemExit, FileNotFoundError) as e:
        print(f"[skip] {job} in {root}: {e}")
        return None
    m = list(r["imtls"]).index(IMT)
    return {"c": np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :]), "lv": r["imtls"][IMT], "names": r["names"]}


def total(fams):
    return 1 - np.prod([1 - x["c"] for x in fams], axis=0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cur = {v: {k: mean(j, r) for k, (j, _) in PARTS.items()} for v, r in ROOTS.items()}
    fam = {v: [mean(f"c_{lt.SHORT[f]}_ref", r) for f in lt.FAMS] for v, r in ROOTS.items()}
    ext = {}
    for k, jobs in EXTRA.items():
        ext[k] = [mean(jobs[f], hc.OUT_ROOT) if f in jobs else x for f, x in zip(lt.FAMS, fam["new"])]
    names, lv = fam["new"][0]["names"], fam["new"][0]["lv"]
    poes = {round(-hc.INV_TIME / np.log(1 - p)): p for p in hc.POES}

    def draw(ax, s, name):
        for v, ls, lw in (("old", "--", 1.0), ("new", "-", 1.6)):
            for k, (_, col) in PARTS.items():
                x = cur[v][k]
                if x is not None:
                    ax.loglog(x["lv"], x["c"][x["names"].index(name)], color=col, ls=ls, lw=lw,
                              label=k if v == "new" else None)
            if all(x is not None for x in fam[v]):
                ax.loglog(lv, total(fam[v])[fam[v][0]["names"].index(name)], color="k", ls=ls, lw=lw + 0.8, label="total" if v == "new" else None)
        for i, (k, fs) in enumerate(ext.items()):
            if all(x is not None for x in fs):
                ax.loglog(lv, total(fs)[fs[0]["names"].index(name)], color=f"C{i + 6}", lw=1.6, ls="-.", label=f"total {k}")
        for rp, p in poes.items():
            ax.axhline(p, color="0.6", lw=0.6, ls=":")
            ax.text(XLIM[0] * 1.1, p * 1.15, f"{rp} yr", fontsize=6, color="0.4")
        ax.set_xlim(*XLIM)
        ax.set_ylim(*YLIM)
        ax.set_title(name.replace("_", " "), fontsize=9)
        ax.grid(alpha=0.3, which="both", lw=0.3)

    f, axs = plt.subplots(2, (len(names) + 1) // 2, figsize=(3.3 * ((len(names) + 1) // 2), 7), sharex=True,
                          sharey=True, squeeze=False)
    for s, (ax, name) in enumerate(zip(axs.ravel(), names)):
        draw(ax, s, name)
    for ax in axs[-1]:
        ax.set_xlabel(f"{IMT} (g)")
    for ax in axs[:, 0]:
        ax.set_ylabel("annual probability of exceedance")
    h, l = axs[0][0].get_legend_handles_labels()
    f.legend(h, l, loc="lower center", ncol=len(l), fontsize=8, frameon=False)
    f.suptitle(f"{IMT}, {hc.SITE}: psha_chile5 dashed, psha_chile6 (catalog.csv) solid", fontsize=10)
    f.tight_layout(rect=(0, 0.04, 1, 1))
    f.savefig(OUT / "08_curves.png", dpi=300)
    plt.close(f)

    for s, name in enumerate(names):
        f, ax = plt.subplots(figsize=(6.5, 5))
        draw(ax, s, name)
        ax.set_title(f"{name.replace('_', ' ')}: psha_chile5 dashed, psha_chile6 solid", fontsize=9)
        ax.set_xlabel(f"{IMT} (g)")
        ax.set_ylabel("annual probability of exceedance")
        ax.legend(fontsize=7, loc="lower left")
        f.tight_layout()
        f.savefig(OUT / f"08_curves_{name}.png", dpi=300)
        plt.close(f)
    from hazard.post import iml
    rows = {}
    for lab, fs in [("old", fam["old"]), ("new", fam["new"])] + list(ext.items()):
        if all(x is not None for x in fs):
            t = total(fs)
            rows[lab] = {(n, rp): iml(t[fs[0]["names"].index(n)], lv, p) for n in names for rp, p in poes.items()}
    print(f"\n{IMT} (g) of the total")
    print(__import__("pandas").DataFrame(rows).round(3).to_string())
    print(f"wrote {OUT}/08_curves*.png")


if __name__ == "__main__":
    main()
