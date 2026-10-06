# Which events should draw the in-slab pattern, and with which weights: a
# retrospective spatial test in the spirit of Helmstetter et al. (2007) and Hiemer et
# al. (2014). For each SMOOTH_EVENTS mode the pattern of a class is built from the
# events before SPLIT (same fit, completeness, kernel and weights as s02, with the
# catalog ending at SPLIT) and scored on the complete events of M >= TARGET_M after
# SPLIT: Poisson log-likelihood per cell with the forecast scaled to the observed
# number (CSEP S-test), as gain per event over a uniform forecast. Higher is better.
# TARGETS repeats the score on target sets without the great-earthquake sequences,
# whose aftershocks outlast the gk74 windows (point-source radius ~120 km at M8.8).
# Outputs: outputs/intraslab/<tag>/check/pattern_test.csv
#   python intraslab/pattern_test.py

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.special import gammaln

import run
from lib import cat, gr, smooth
from variants import VARIANTS
from intraslab.s02_ssm import domain, fit, pattern

# settings
MODES = ["complete", "window", "window_T", "all", "period"]
CLASSES = ["intra_slab", "slab_deep"]
SPLITS = [2000, 2005, 2010]
TARGET_M = 5.0
# target sets: name -> (end year or None, [(t0, t1, lat_min, lat_max) removed])
SEQ = [(2010.15, 2012.2, -39.0, -32.5), (2014.2, 2015.25, -21.5, -18.5), (2015.7, 2016.7, -32.5, -29.5)]
TARGETS = {"all": (None, []), "no Maule, Iquique, Illapel": (None, SEQ), "before 2010": (2010.15, [])}


def xyz(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def main():
    c = run.config("intraslab", VARIANTS["intraslab"]["ref"])
    cells = domain(c)
    glon, glat = cells["lon"].to_numpy(), cells["lat"].to_numpy()
    tree = cKDTree(xyz(glon, glat))
    rows = []
    for k in CLASSES:
        s = cat.load(c.OUT / "decluster" / f"cat_dc_{k}_{c.PATTERN_DC}.csv", bbox=c.BBOX)
        steps = c.COMPLETENESS[k]
        kp = {"N_NEIGHBORS": c.N_NEIGHBORS, "MIN_KERNEL_KM": c.MIN_KERNEL_KM, "MAX_DIST_KM": c.MAX_DIST_KM,
              "KERNEL_POWER": c.KERNEL_POWER, "KERNEL": c.KERNEL, **c.KERNEL_BY_CLASS.get(k, {})}
        for (sp, (tn, (end, cut))) in [(a, b) for a in SPLITS for b in TARGETS.items()]:
            tr = s[s["year"] < sp].reset_index(drop=True)
            tg = s[(s["year"] >= sp) & (s["mag"] >= TARGET_M - 1e-6)]
            tg = tg[gr.complete(tg, steps)]
            if end:
                tg = tg[tg["year"] < end]
            for t0, t1, a, b in cut:
                tg = tg[~(tg["year"].between(t0, t1) & tg["latitude"].between(a, b))]
            n = np.bincount(tree.query(xyz(tg["longitude"].to_numpy(), tg["latitude"].to_numpy()))[1],
                            minlength=len(glon)).astype(float)
            nt = n.sum()
            if nt < 5:
                continue
            w = fit(k, tr, c, sp)
            ll = lambda p: float((-nt * p + n * np.log(nt * p) - gammaln(n + 1)).sum())
            ll_u = ll(np.full(len(glon), 1.0 / len(glon)))
            for mode in MODES:
                c.SMOOTH_EVENTS = mode
                try:
                    ev, wt = pattern(k, tr, w, w["b"], c, sp)
                except SystemExit as e:
                    print(f"[skip] {k} {sp} {mode}: {e}")
                    continue
                elon, elat = ev["longitude"].to_numpy(), ev["latitude"].to_numpy()
                h = smooth.kernel(elon, elat, kp["N_NEIGHBORS"], kp["MIN_KERNEL_KM"])
                f = smooth.field(elon, elat, wt, h, glon, glat, kp["KERNEL_POWER"], kp["MAX_DIST_KM"], kp["KERNEL"])
                p = 0.99 * f / f.sum() + 0.01 / len(f)
                g = ll(p)
                rows.append({"class": k, "targets": tn, "split": sp, "mode": mode, "n_train": len(ev), "n_target": int(nt),
                             "max_weight_pct": 100 * wt.max() / wt.sum(), "ll": g,
                             "gain_per_event": float(np.exp((g - ll_u) / nt))})
    t = pd.DataFrame(rows)
    od = c.OUT / "check"
    od.mkdir(parents=True, exist_ok=True)
    t.round(4).to_csv(od / "pattern_test.csv", index=False)
    print(f"gain per target event over a uniform forecast (targets: complete M>={TARGET_M:g} after the split)")
    for tn in TARGETS:
        x = t[t["targets"] == tn]
        print(f"\ntargets: {tn}")
        print(x.pivot_table(index=["class", "split", "n_target"], columns="mode", values="gain_per_event")
              [[m for m in MODES if m in set(x["mode"])]].round(3).to_string())
    print(f"\nwrote {od / 'pattern_test.csv'}")


if __name__ == "__main__":
    main()
