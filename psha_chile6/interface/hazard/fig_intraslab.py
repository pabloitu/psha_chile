# Figures on the intraslab contribution at the cities.
#   fig_intraslab_split.png  hazard share per source, reference vs classmask
#                            (classes smoothed only on their own Slab2 domain), 475 and 2475 yr
#   fig_intraslab_rates.png  in-slab rate near each city, model vs catalog, by depth
#                            and by magnitude (no GMM)
# Inputs: _contrib/<split>/contributions.csv from post.py, check/*.csv from
# intraslab/check_rates.py. Outputs: <hazard OUT_ROOT>/_contrib/figures/

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
CONTRIB = hc.OUT_ROOT / "_contrib"
SPLITS = [("full_classes", "reference"), ("full_cm_classes", "classmask")]
CHECK = paths.OUT / "intraslab" / "ref" / "check"
OUT = CONTRIB / "figures"
PARTS = {"Interface": "#4c72b0", "intra_slab": "#dd8452", "slab_deep": "#c44e52",
         "deep_nest": "#8172b3", "Crustal": "#55a868"}
SHALLOW = "0-70"
M_RATIO = [6.0, 6.5]


def fig_split(tabs, path):
    sites = list(hc.CITIES)
    rps = sorted(tabs[0][1]["return_period"].unique())
    f, axs = plt.subplots(1, len(rps), figsize=(6.5 * len(rps), 0.62 * len(sites) + 1.8), sharey=True)
    h = 0.38
    for ax, rp in zip(np.atleast_1d(axs), rps):
        base = None
        for j, (lab, t) in enumerate(tabs):
            t = t[t["return_period"] == rp].set_index("site").loc[sites]
            y = np.arange(len(sites)) + (j - 0.5) * h
            left = np.zeros(len(sites))
            for p, col in PARTS.items():
                v = t[p].fillna(0).to_numpy() if p in t else np.zeros(len(sites))
                ax.barh(y, v, h * 0.95, left=left, color=col, alpha=1.0 if j == 0 else 0.6,
                        edgecolor="white", lw=0.5, label=p if j == 0 else None)
                left += v
            g = t["iml_total"].to_numpy()
            for i, yy in enumerate(y):
                txt = f"{g[i]:.2f} g" + (f" ({100 * (g[i] / base[i] - 1):+.1f} %)" if base is not None else "")
                ax.text(101, yy, txt, va="center", fontsize=7)
            base = g if base is None else base
        ax.set_xlim(0, 100)
        ax.set_yticks(np.arange(len(sites)))
        ax.set_yticklabels([s.replace("_", " ") for s in sites])
        ax.set_xlabel("share of exceedance rate at the city PGA (%)")
        ax.set_title(f"PGA {rp} yr: upper bar {tabs[0][0]}, lower (faded) bar {tabs[1][0]}", fontsize=10)
        ax.grid(axis="x", alpha=0.3)
    np.atleast_1d(axs)[0].invert_yaxis()
    np.atleast_1d(axs)[0].legend(loc="lower center", bbox_to_anchor=(1.0, 1.06), ncol=len(PARTS), fontsize=8,
                                 frameon=False)
    f.tight_layout()
    f.savefig(path, dpi=250, bbox_inches="tight")
    plt.close(f)


def fig_rates(dep, rat, path):
    sites = [s for s in hc.CITIES if rat[(rat["site"] == s) & (rat["class"] == "total")]["n_obs"].max() > 0]
    d = dep[dep["class"] != "deep_nest"].copy()
    d["zone"] = np.where(d["band"] == SHALLOW, "shallow", "deep")
    d = d.groupby(["site", "zone"])[["model", "obs", "n_obs"]].sum()
    f, axs = plt.subplots(1, 3, figsize=(15, 0.5 * len(sites) + 2.2), sharey=True)
    y = np.arange(len(sites))
    zl = {"shallow": f"hypocentre < {SHALLOW.split('-')[1]} km", "deep": f"hypocentre >= {SHALLOW.split('-')[1]} km"}
    for ax, z in zip(axs[:2], ("shallow", "deep")):
        t = d.xs(z, level="zone").reindex(sites).fillna(0)
        ax.barh(y - 0.2, t["model"], 0.38, color="0.35", label="model")
        ax.barh(y + 0.2, t["obs"], 0.38, color="#c44e52", label="catalog")
        for yy, n in zip(y, t["n_obs"]):
            ax.text(0, yy + 0.2, f" n={int(n)}", va="center", fontsize=7, color="white")
        ax.set_title(f"in-slab N(>=5.5)/yr within 150 km, {zl[z]}", fontsize=10)
        ax.set_xlabel("events / yr")
        ax.grid(axis="x", alpha=0.3)
    axs[0].legend(fontsize=8)
    ax = axs[2]
    r = rat[rat["class"] == "total"]
    for i, m in enumerate(M_RATIO):
        t = r[np.isclose(r["M"], m)].set_index("site").reindex(sites)
        n = t["n_obs"].to_numpy(float)
        ok = n > 0
        lo = t["model"] / (t["obs"] * (1 + 1 / np.sqrt(np.where(ok, n, 1))))
        hi = t["model"] / (t["obs"] * np.clip(1 - 1 / np.sqrt(np.where(ok, n, 1)), 0.1, None))
        yy = y + (i - 0.5) * 0.3
        ax.errorbar(t["ratio"][ok], yy[ok], xerr=[(t["ratio"] - lo)[ok], (hi - t["ratio"])[ok]], fmt="o",
                    ms=5, capsize=2, label=f"M>={m}")
        for a, b, c in zip(t["ratio"][ok], yy[ok], n[ok]):
            ax.text(a, b - 0.12, f"{int(c)}", fontsize=6, ha="center", va="bottom")
    ax.axvline(1, color="k", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 10)
    ax.set_title("model / catalog, all in-slab classes (bars: +/-1 sqrt(n))", fontsize=10)
    ax.set_xlabel("ratio")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    axs[0].set_yticks(y)
    axs[0].set_yticklabels([s.replace("_", " ") for s in sites])
    axs[0].invert_yaxis()
    f.tight_layout()
    f.savefig(path, dpi=250, bbox_inches="tight")
    plt.close(f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tabs = [(lab, pd.read_csv(CONTRIB / sp / "contributions.csv")) for sp, lab in SPLITS
            if (CONTRIB / sp / "contributions.csv").exists()]
    if len(tabs) < len(SPLITS):
        print(f"[skip] fig_intraslab: {[sp for sp, _ in SPLITS if not (CONTRIB / sp / 'contributions.csv').exists()]} not run")
        return
    fig_split(tabs, OUT / "fig_intraslab_split.png")
    fig_rates(pd.read_csv(CHECK / "depth.csv"), pd.read_csv(CHECK / "rates.csv"), OUT / "fig_intraslab_rates.png")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()