# Hazard curves of one city from the family jobs: interface, in-slab, crustal and the full model,
# mean and the band between the 2.5 and 97.5 % curves (exact combination, hazard/combine.py).
# Output: <tree>/_curves/curves_<city>_PGA.png and .csv. Run: LEVEL2=1 python hazard/curves_city.py ensenada

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
from hazard import combine, post
from hazard.post import draw, finish, QUANTILES as Q

FAM = [("c_if_final", "interface", "interface"), ("c_is_final", "in-slab", "in-slab"), ("c_cr_final", "crustal", "crustal")]
IMT = "PGA"


def main(city):
    post.set_style()
    fam = [(post.load(j), lab, key) for j, lab, key in FAM]
    names = fam[0][0]["names"]
    if city not in names:
        raise SystemExit(f"{city} is not a site of this tree: {names}")
    s = names.index(city)
    lv = fam[0][0]["imtls"][IMT]
    parts = [(r["curves"][:, :, [list(r["imtls"]).index(IMT)], :].astype(float), r["w"]) for r, _, _ in fam]
    m = combine.mean(parts)[s, 0]
    q = combine.exact(parts, (Q[0], 0.5, Q[-1]))[:, s, 0]
    f, ax = plt.subplots(figsize=(7, 5.5))
    tab = {"PGA_g": lv, "total_mean": m, "total_q2.5": q[0], "total_q50": q[1], "total_q97.5": q[2]}
    for (r, lab, key), (c, w) in zip(fam, parts):
        draw(ax, lv, c[s, :, 0, :], w, paths.palette.FAMILY[key], lab)
        tab[f"{key}_mean"] = (w / w.sum()) @ c[s, :, 0, :]
    ax.loglog(lv, m, color="k", lw=2.5, label="Full model")
    ax.fill_between(lv, q[0], q[2], color="k", alpha=0.15, lw=0)
    out = hc.OUT_ROOT / "_curves"
    out.mkdir(parents=True, exist_ok=True)
    finish(ax, IMT, city.replace("_", " ").title(), hc.POES, out / f"curves_{city}_{IMT}.png")
    pd.DataFrame(tab).to_csv(out / f"curves_{city}_{IMT}.csv", index=False)
    for p in hc.POES:
        print(f"{city}: PGA at PoE {p:g}: mean {post.iml(m, lv, p):.3f} g, 2.5-97.5 % {post.iml(q[0], lv, p):.3f}-{post.iml(q[2], lv, p):.3f} g")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ensenada")
