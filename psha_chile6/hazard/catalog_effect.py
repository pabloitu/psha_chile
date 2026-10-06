# S1 (CONTEXT_sources.md): hazard of the reference rebuilt on catalog.csv against
# the campaign reference (psha_chile5, frozen). From the family-only reference jobs
# of both trees: the total at each city and return period, its change, the change
# from each family alone (that family new, the others old; families combine exactly
# in rate space), the family shares, and the in-slab class shares where the
# c_is_<class> jobs exist in both trees.
# Outputs: outputs/s1/05_hazard.csv, 05_shares.csv, 05_hazard.png

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
from hazard import logic_tree as lt
from hazard.post import load, iml

# settings
ROOTS = {"old": paths.PREV / "outputs" / "hazard" / hc.SITE, "new": hc.OUT_ROOT}
CLASSES = ["intra_slab", "slab_deep", "deep_nest"]
OUT = paths.OUT / "s1"
COLORS = {"total": "k", "interface": "#4c72b0", "intraslab": "#c44e52", "crustal": "#55a868"}


def mean(job, root):
    r = load(job, root=root)
    return {"mean": np.einsum("r,srml->sml", r["w"], r["curves"]), "imtls": r["imtls"], "names": r["names"],
            "poes": r["info"]["poes"], "calc": r["calc_id"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rate = lambda p: -np.log(1 - np.clip(p, 0, 1 - 1e-12))
    fam = {v: {f: mean(f"c_{lt.SHORT[f]}_ref", r) for f in lt.FAMS} for v, r in ROOTS.items()}
    cls = {}
    for v, r in ROOTS.items():
        try:
            cls[v] = {k: mean(f"c_is_{k}", r) for k in CLASSES}
        except (SystemExit, FileNotFoundError) as e:
            print(f"[skip] in-slab class shares ({v}): {e}")
    r0 = fam["old"]["interface"]
    for v, fs in {**fam, **cls}.items():
        for k, r in fs.items():
            if r["names"] != r0["names"] or any(not np.allclose(r["imtls"][i], x) for i, x in r0["imtls"].items()):
                raise SystemExit(f"{v} {k}: sites or levels differ from the old interface reference")
    for v, fs in fam.items():
        print(f"{v}: " + ", ".join(f"{f} calc {r['calc']}" for f, r in fs.items()))

    surv = {v: {f: 1 - r["mean"] for f, r in fs.items()} for v, fs in fam.items()}
    tot = {v: 1 - np.prod(list(s.values()), axis=0) for v, s in surv.items()}
    rows, sh = [], []
    for m, (imt, lv) in enumerate(r0["imtls"].items()):
        for s, name in enumerate(r0["names"]):
            for p in hc.POES:
                rp = round(-hc.INV_TIME / np.log(1 - p))
                x = {v: iml(tot[v][s, m], lv, p) for v in tot}
                row = {"site": name, "imt": imt, "return_period": rp, "old": x["old"], "new": x["new"],
                       "total": 100 * (x["new"] / x["old"] - 1)}
                for f in lt.FAMS:
                    sv = [surv["new" if g == f else "old"][g][s, m] for g in lt.FAMS]
                    row[f] = 100 * (iml(1 - np.prod(sv, axis=0), lv, p) / x["old"] - 1)
                rows.append(row)
                for v in tot:
                    at = lambda c: rate(np.exp(np.interp(np.log(x[v]), np.log(lv), np.log(np.maximum(c, 1e-30)))))
                    for f, r in fam[v].items():
                        sh.append({"site": name, "imt": imt, "return_period": rp, "ver": v, "part": f,
                                   "share_pct": 100 * at(r["mean"][s, m]) / rate(p)})
                    for k, r in cls.get(v, {}).items():
                        sh.append({"site": name, "imt": imt, "return_period": rp, "ver": v, "part": k,
                                   "share_pct": 100 * at(r["mean"][s, m]) / rate(p)})
    t, sh = pd.DataFrame(rows), pd.DataFrame(sh)
    t.to_csv(OUT / "05_hazard.csv", index=False)
    sh.to_csv(OUT / "05_shares.csv", index=False)

    for imt in r0["imtls"]:
        a = t[t["imt"] == imt].pivot_table(index="site", columns="return_period",
                                            values=["old", "new", "total"] + lt.FAMS, sort=False)
        print(f"\n{imt} (g): old, new, change % and the change from each family alone")
        print(a.reindex(columns=["old", "new", "total"] + lt.FAMS, level=0).round(3).to_string())
        b = sh[sh["imt"] == imt].pivot_table(index=["site", "return_period"], columns=["part", "ver"],
                                             values="share_pct", sort=False)
        print(f"\n{imt}: share of the total rate at the city's own total, % (old / new)")
        c = pd.DataFrame(index=b.index)
        for k in dict.fromkeys(b.columns.get_level_values(0)):
            c[k] = [f"{o:4.0f} / {n:4.0f}" for o, n in zip(b[(k, "old")], b[(k, "new")])]
        print(c.to_string())

    imt = list(r0["imtls"])[0]
    rps = sorted(t["return_period"].unique())
    f, axs = plt.subplots(len(rps), 1, figsize=(11, 3.4 * len(rps)), sharex=True, squeeze=False)
    parts = ["total"] + lt.FAMS
    for ax, rp in zip(axs[:, 0], rps):
        x = t[(t["imt"] == imt) & (t["return_period"] == rp)]
        i = np.arange(len(x))
        for j, k in enumerate(parts):
            ax.bar(i + (j - 1.5) * 0.2, x[k], 0.2, color=COLORS[k], label=k if k == "total" else f"{k} alone")
        ax.axhline(0, color="k", lw=0.6)
        ax.set_ylabel(f"{imt} change %, {rp} yr")
        ax.grid(axis="y", alpha=0.3)
        ax.set_xticks(i, [s.replace("_", " ") for s in x["site"]], rotation=30, ha="right")
    axs[0, 0].legend(fontsize=8, ncol=4)
    axs[0, 0].set_title("catalog.csv against the campaign catalogs, same source models (psha_chile6 vs psha_chile5)",
                        fontsize=10)
    f.tight_layout()
    f.savefig(OUT / "05_hazard.png", dpi=300)
    plt.close(f)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
