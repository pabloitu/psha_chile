# Declustered vs full catalog: which fit reproduces the observed large-event
# rates. Reads the a-b tables of the interface reference (declustered, gk74)
# and of the raw variant (full catalog), and the in-slab class tables, and
# puts the fitted N(>=M) next to the observed one.
# Outputs: outputs/completeness/convention.csv, convention.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
import run
from variants import VARIANTS

# settings
RUNS = {"declustered": "mmin55", "full catalog": "c_raw"}
OUT = paths.OUT / "completeness"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, fits = [], {}
    for lab, v in RUNS.items():
        c = run.build("interface", VARIANTS["interface"][v])
        t = pd.read_csv(c.OUT / "ab" / "compare.csv")
        mags = [x for x in t.columns if x.startswith("M")]
        for seg, g in t.groupby("seg", sort=False):
            w = g[g["est"] == "weichert"].iloc[0]
            o = g[g["est"] == "observed"].iloc[0]
            fits.setdefault(seg, {})[lab] = (w, o)
            for m in mags:
                rows.append({"family": "interface", "set": seg, "catalog": lab, "b": w["b"], "M": float(m[1:]),
                             "fitted": w[m], "observed": o[m], "ratio": w[m] / o[m] if o[m] > 0 else np.nan})
    for lab, v in (("declustered", "ref"), ("full catalog", "raw")):
        c = run.build("intraslab", VARIANTS["intraslab"][v])
        t = pd.read_csv(c.OUT / "ssm" / "classes.csv")
        for _, r in t.iterrows():
            rows.append({"family": "intraslab", "set": r["class"], "catalog": lab, "b": r["b_used"], "M": np.nan,
                         "fitted": np.nan, "observed": np.nan, "ratio": r["model_obs_top"]})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "convention.csv", index=False)
    p = t[t["family"] == "interface"].pivot_table(index=["set", "M"], columns="catalog", values="ratio", sort=False)
    print("interface: fitted / observed N(>=M)")
    print(p.round(2).to_string())
    q = t[t["family"] == "intraslab"].pivot_table(index="set", columns="catalog", values="ratio", sort=False)
    print("\nin-slab: model / observed at the top magnitude bins (s02 check)")
    print(q.round(2).to_string())

    f, axs = plt.subplots(1, len(fits), figsize=(3.2 * len(fits), 3.6), sharey=True, squeeze=False)
    for ax, (seg, d) in zip(axs[0], fits.items()):
        for j, (lab, (w, o)) in enumerate(d.items()):
            ms = [float(m[1:]) for m in w.index if m.startswith("M")]
            ax.semilogy(ms, [w[f"M{m}"] for m in ms], "-", color=f"C{j}", label=f"{lab}, b {w['b']:.2f}")
            ax.semilogy(ms, [o[f"M{m}"] for m in ms], "o", color=f"C{j}", mfc="none")
        ax.set_title(seg, fontsize=9)
        ax.set_xlabel("M")
        ax.grid(alpha=0.3, which="both")
    axs[0][0].set_ylabel("N(>=M) per yr")
    axs[0][0].legend(fontsize=7)
    f.suptitle("interface: fitted (lines) and observed (circles) rates, declustered vs full catalog", fontsize=10)
    f.tight_layout()
    f.savefig(OUT / "convention.png", dpi=300)
    plt.close(f)
    print(f"\nwrote {OUT / 'convention.csv'} and convention.png")


if __name__ == "__main__":
    main()
