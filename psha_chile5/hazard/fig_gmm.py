# GMM comparison at the cities from post.py's _contrib/summary.csv.
# Each split puts one region on a single GMM, the others on their tree; "full_ref" is the tree everywhere.
#   fig_gmm_pga.png    PGA per city and split, ratio to the reference, 475 and 2475 yr
#   fig_gmm_share.png  intraslab share of the exceedance rate per slab GMM
#   gmm_compare.csv    PGA, ratio and intraslab share per city, split, return period
# Run hazard/run_all.sh first (jobs intraslab_pk, intraslab_mv, interface_pk, interface_ku).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
from hazard import config as hc

# settings
SUMMARY = hc.OUT_ROOT / "_contrib" / "summary.csv"
OUT = hc.OUT_ROOT / "_contrib" / "figures"
REF = "full_ref"
SPLITS = {"full_ref": ("GMM tree", "0.3"),
          "gmm_slab_ag": ("slab AG20", "#f2b27a"), "gmm_slab_pk": ("slab Parker", "#dd8452"),
          "gmm_slab_mv": ("slab Montalva", "#c44e52"),
          "gmm_inter_ag": ("interface AG20", "#9ab6d9"), "gmm_inter_pk": ("interface Parker", "#4c72b0"),
          "gmm_inter_ku": ("interface Kuehn", "#8172b3")}
SLAB = ["full_ref", "gmm_slab_ag", "gmm_slab_pk", "gmm_slab_mv"]


def table():
    t = pd.read_csv(SUMMARY)
    t = t[t["split"].isin(SPLITS)].copy()
    miss = [s for s in SPLITS if s not in set(t["split"])]
    if miss:
        raise SystemExit(f"[skip] fig_gmm: splits {miss} not in {SUMMARY}")
    ref = t[t["split"] == REF].set_index(["site", "return_period"])["iml_total"]
    t["ratio"] = t["iml_total"].to_numpy() / ref.loc[list(zip(t["site"], t["return_period"]))].to_numpy()
    return t


def fig_pga(t, path):
    sites = [s for s in hc.CITIES if s in set(t["site"])]
    rps = sorted(t["return_period"].unique())
    n = len(SPLITS)
    h = 0.8 / n
    f, axs = plt.subplots(1, len(rps), figsize=(6 * len(rps), 0.55 * len(sites) + 1.8), sharey=True)
    for ax, rp in zip(np.atleast_1d(axs), rps):
        for j, (sp, (lab, col)) in enumerate(SPLITS.items()):
            g = t[(t["split"] == sp) & (t["return_period"] == rp)].set_index("site").reindex(sites)
            y = np.arange(len(sites)) + (j - (n - 1) / 2) * h
            ax.barh(y, 100 * (g["ratio"] - 1), h * 0.95, color=col, label=lab)
            if sp == REF:
                for yy, v in zip(y, g["iml_total"]):
                    ax.text(0, yy, f" {v:.2f} g", va="center", fontsize=6)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title(f"PGA {rp} yr: change vs the GMM tree (%)", fontsize=10)
        ax.set_xlabel("% change of PGA")
        ax.grid(axis="x", alpha=0.3)
    a0 = np.atleast_1d(axs)[0]
    a0.set_yticks(np.arange(len(sites)))
    a0.set_yticklabels([s.replace("_", " ") for s in sites])
    a0.invert_yaxis()
    a0.legend(fontsize=7, loc="lower left")
    f.tight_layout()
    f.savefig(path, dpi=250, bbox_inches="tight")
    plt.close(f)


def fig_share(t, path):
    sites = [s for s in hc.CITIES if s in set(t["site"])]
    rps = sorted(t["return_period"].unique())
    n = len(SLAB)
    h = 0.8 / n
    f, axs = plt.subplots(1, len(rps), figsize=(5.5 * len(rps), 0.55 * len(sites) + 1.8), sharey=True)
    for ax, rp in zip(np.atleast_1d(axs), rps):
        for j, sp in enumerate(SLAB):
            g = t[(t["split"] == sp) & (t["return_period"] == rp)].set_index("site").reindex(sites)
            y = np.arange(len(sites)) + (j - (n - 1) / 2) * h
            ax.barh(y, g["Intraslab"], h * 0.95, color=SPLITS[sp][1], label=SPLITS[sp][0])
        ax.set_xlim(0, 100)
        ax.set_title(f"intraslab share of the exceedance rate, PGA {rp} yr", fontsize=10)
        ax.set_xlabel("%")
        ax.grid(axis="x", alpha=0.3)
    a0 = np.atleast_1d(axs)[0]
    a0.set_yticks(np.arange(len(sites)))
    a0.set_yticklabels([s.replace("_", " ") for s in sites])
    a0.invert_yaxis()
    a0.legend(fontsize=7, loc="lower right")
    f.tight_layout()
    f.savefig(path, dpi=250, bbox_inches="tight")
    plt.close(f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not SUMMARY.exists():
        print(f"[skip] fig_gmm: no {SUMMARY}")
        return
    try:
        t = table()
    except SystemExit as e:
        print(e)
        return
    t[["site", "return_period", "split", "iml_total", "ratio", "Interface", "Intraslab", "Crustal"]].to_csv(
        OUT.parent / "gmm_compare.csv", index=False)
    fig_pga(t, OUT / "fig_gmm_pga.png")
    fig_share(t, OUT / "fig_gmm_share.png")
    for col, fmt in (("iml_total", "PGA (g)"), ("Intraslab", "intraslab share (%)")):
        print(f"\n{fmt}")
        print(t.pivot_table(index=["site", "return_period"], columns="split", values=col, sort=False)
              [list(SPLITS)].round(2).to_string())
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()