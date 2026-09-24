# Decluster each slab class separately after the historical cutoff.
# Outputs: decluster/cat_dc_{class}_{method}.csv, summary.csv,
#          removed_large.csv, dropped_historical.csv, input.json,
#          figures/s00_classes.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cat, cfg, dc
from intraslab import config


def load(c):
    """Classified catalog for CLASSES, cut at the historical cutoff per class."""
    df = cat.load(c.CAT)
    if "class" not in df.columns:
        raise SystemExit(f"{c.CAT} has no class column")
    df = df[df["class"].isin(c.CLASSES)].reset_index(drop=True)
    cut = np.array([c.HIST_CUTOFF_BY_CLASS.get(k, c.HIST_CUTOFF) or -np.inf for k in df["class"]])
    drop = df[df["year"] < cut]
    return df[df["year"] >= cut].reset_index(drop=True), drop


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "decluster"
    od.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)

    df, drop = load(c)
    raw = cat.load(c.CAT)
    fp = cat.fingerprint(c.CAT, raw)
    fp["t_end"] = float(raw["year"].max())
    (od / "input.json").write_text(json.dumps(fp, indent=1))
    drop.to_csv(od / "dropped_historical.csv", index=False)
    print(json.dumps(fp))
    for k in c.CLASSES:
        s, d = df[df["class"] == k], drop[drop["class"] == k]
        if not len(s):
            raise SystemExit(f"class {k} is empty in {c.CAT}")
        print(f"{k}: {len(s)} events {s['year'].min():.0f}-{s['year'].max():.0f} "
              f"M{s['mag'].min():.1f}-{s['mag'].max():.1f}, dropped pre-cutoff {len(d)}"
              + (f" (largest M{d['mag'].max():.1f})" if len(d) else ""))

    summ, revs, mains = [], [], {}
    for k in c.CLASSES:
        s = df[df["class"] == k].reset_index(drop=True)
        for m in c.DC_METHODS:
            out, rev = dc.run(s, m, c.DC_FS, c.DC_FROM_YEAR, c.DC_KEEP_IDS, c.DC_MPROT)
            mn = out[out["is_mainshock"]]
            mn.drop(columns=["year"]).to_csv(od / f"cat_dc_{k}_{m}.csv", index=False)
            revs.append(rev.assign(**{"class": k}))
            summ.append({"class": k, "method": m, "n_in": len(out), "n_main": len(mn),
                         "frac_removed": round(1 - len(mn) / len(out), 3),
                         "n_M7_removed": len(rev), "mmax_main": float(mn["mag"].max()),
                         "median_depth_in": float(s["depth"].median()),
                         "median_depth_main": float(mn["depth"].median())})
            if m == c.DC_METHOD:
                mains[k] = mn
    tab = pd.DataFrame(summ)
    tab.to_csv(od / "summary.csv", index=False)
    pd.concat(revs, ignore_index=True).to_csv(od / "removed_large.csv", index=False)
    print(tab.round(3).to_string(index=False))

    f, axs = plt.subplots(1, 3, figsize=(14, 7))
    for k, mn in mains.items():
        axs[0].plot(mn["longitude"], mn["latitude"], ".", ms=2, alpha=0.4, label=k)
        axs[1].plot(mn["depth"], mn["latitude"], ".", ms=2, alpha=0.4)
        axs[2].plot(mn["year"], mn["mag"], ".", ms=2, alpha=0.4)
    axs[0].set_xlim(c.BBOX[0], c.BBOX[1])
    axs[0].set_ylim(c.BBOX[2], c.BBOX[3])
    axs[0].legend(markerscale=4, fontsize=8)
    axs[0].set_title(f"mainshocks ({c.DC_METHOD})")
    axs[1].invert_xaxis()
    axs[1].set_xlabel("depth km")
    axs[2].set_xlabel("year")
    axs[2].set_ylabel("M")
    f.tight_layout()
    f.savefig(c.FIG / "s00_classes.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s00", {"input": fp})


if __name__ == "__main__":
    main()
