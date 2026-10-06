# In-slab smoothing variants against the rest of the model, per city: the in-slab
# curve of each variant (the reference is SMOOTH_EVENTS "all"), the interface and
# crustal reference curves, and the total with the reference and with "window_T". The
# psha_chile5 in-slab curve (dashed grey) shows where the campaign stood.
# Outputs: outputs/s1/10_smoothing.png, 10_smoothing_<city>.png, printed PGA table

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
from hazard.post import load, iml

# settings
INSLAB = {"all (ref)": ("c_is_ref", "#c44e52", 2.2), "window_T": ("c_is_smooth_window_T", "#dd8452", 1.6),
          "old weights": ("c_is_smooth_complete", "0.3", 1.2)}
OTHER = {"interface": ("c_if_ref", "#4c72b0"), "crustal": ("c_cr_ref", "#55a868")}
PREV = paths.PREV / "outputs" / "hazard" / hc.SITE
XLIM, YLIM = (0.02, 4.0), (1e-5, 1e-1)
OUT = paths.OUT / "s1"


def mean(job, root=None):
    try:
        r = load(job, root=root)
    except (SystemExit, FileNotFoundError) as e:
        print(f"[skip] {job}: {e}")
        return None
    m = list(r["imtls"]).index("PGA")
    return {"c": np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :]), "lv": r["imtls"]["PGA"],
            "names": r["names"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ins = {k: mean(j) for k, (j, _, _) in INSLAB.items()}
    oth = {k: mean(j) for k, (j, _) in OTHER.items()}
    old = mean("c_is_ref", PREV)
    r0 = oth["interface"]
    lv, names = r0["lv"], r0["names"]
    at = lambda x, n: x["c"][x["names"].index(n)]
    tot = lambda x, n: 1 - (1 - at(x, n)) * (1 - at(oth["interface"], n)) * (1 - at(oth["crustal"], n))
    poes = {round(-hc.INV_TIME / np.log(1 - p)): p for p in hc.POES}

    def draw(ax, n):
        for k, (_, col) in OTHER.items():
            ax.loglog(lv, at(oth[k], n), color=col, lw=2.2, label=f"{k} (ref)")
        if old is not None:
            ax.loglog(old["lv"], at(old, n), color="0.6", lw=1.2, ls="--", label="in-slab psha_chile5")
        for k, (_, col, lw) in INSLAB.items():
            if ins[k] is not None:
                ax.loglog(lv, at(ins[k], n), color=col, lw=lw, label=f"in-slab {k}")
        for k, ls in (("all (ref)", "-"), ("window_T", ":")):
            if ins[k] is not None:
                ax.loglog(lv, tot(ins[k], n), color="k", lw=1.8, ls=ls, label=f"total, in-slab {k}")
        for rp, p in poes.items():
            ax.axhline(p, color="0.6", lw=0.6, ls=":")
            ax.text(XLIM[0] * 1.1, p * 1.15, f"{rp} yr", fontsize=6, color="0.4")
        ax.set_xlim(*XLIM)
        ax.set_ylim(*YLIM)
        ax.grid(alpha=0.3, which="both", lw=0.3)

    rows = []
    for n in names:
        for rp, p in poes.items():
            row = {"site": n, "rp": rp, "interface alone": iml(at(oth["interface"], n), lv, p)}
            for k, x in ins.items():
                if x is not None:
                    row[f"in-slab {k}"] = iml(at(x, n), lv, p)
                    row[f"total {k}"] = iml(tot(x, n), lv, p)
            rows.append(row)
    t = pd.DataFrame(rows).set_index(["site", "rp"])
    t.round(3).to_csv(OUT / "10_smoothing.csv")
    print("PGA (g) at the return period: interface alone, in-slab alone per variant")
    print(t[["interface alone"] + [c for c in t.columns if c.startswith("in-slab")]].round(3).to_string())
    print("\nPGA (g) of the total per in-slab variant")
    print(t[[c for c in t.columns if c.startswith("total")]].round(3).to_string())

    ncol = (len(names) + 1) // 2
    f, axs = plt.subplots(2, ncol, figsize=(3.4 * ncol, 7.2), sharex=True, sharey=True, squeeze=False)
    for ax, n in zip(axs.ravel(), names):
        draw(ax, n)
        ax.set_title(n.replace("_", " "), fontsize=9)
    for ax in axs[-1]:
        ax.set_xlabel("PGA (g)")
    for ax in axs[:, 0]:
        ax.set_ylabel("annual probability of exceedance")
    h, l = axs[0][0].get_legend_handles_labels()
    f.legend(h, l, loc="lower center", ncol=5, fontsize=7, frameon=False)
    f.suptitle(f"in-slab smoothing variants against the interface and crustal references, {hc.SITE}", fontsize=10)
    f.tight_layout(rect=(0, 0.06, 1, 1))
    f.savefig(OUT / "10_smoothing.png", dpi=300)
    plt.close(f)
    for n in names:
        f, ax = plt.subplots(figsize=(7, 5.4))
        draw(ax, n)
        ax.set_title(n.replace("_", " "), fontsize=10)
        ax.set_xlabel("PGA (g)")
        ax.set_ylabel("annual probability of exceedance")
        ax.legend(fontsize=7, loc="lower left")
        f.tight_layout()
        f.savefig(OUT / f"10_smoothing_{n}.png", dpi=300)
        plt.close(f)
    print(f"\nwrote {OUT}/10_smoothing*.png")


if __name__ == "__main__":
    main()
