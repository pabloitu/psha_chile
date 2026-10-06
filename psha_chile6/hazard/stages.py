# Stage curves (FINAL_PLAN 2b): the mean PGA hazard curve per city at each stage
# from the psha_chile5 reference to the final forecast, one panel per city, and
# the PGA table at the return periods. Stages are family jobs combined in rate
# space (as hazard/tornado.py); a stage whose jobs are not run yet is skipped.
# Outputs: outputs/stages/stages.png, stages_<city>.png, stages.csv

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

# settings: label -> (root, job suffix); the S1 port of 29 Sep was overwritten by later runs
OLD = paths.PREV / "outputs" / "hazard" / hc.SITE
STAGES = {"psha_chile5 reference (campaign)": (OLD, "ref"),
          "30 Sep catalog, campaign settings": (hc.OUT_ROOT, "stage_camp"),
          "+ full-catalog rates, equal pattern weights": (hc.OUT_ROOT, "stage_conv"),
          "+ tables, floors, pooled b, tapered, crustal classes (final forecast)": (hc.OUT_ROOT, "ref"),
          "full logic tree, mean": (paths.OUT / "hazard" / (hc.SITE + "_final"), "final")}
COLORS = ["0.5", "#dd8452", "#8172b3", "#c44e52", "k"]
IMT = "PGA"
XLIM, YLIM = (0.02, 4.0), (1e-5, 1e-1)
OUT = paths.OUT / "stages"
W, H, DPI = 13.33, 7.5, 300


def mean(job, root):
    try:
        r = load(job, root=root)
    except (SystemExit, FileNotFoundError) as e:
        print(f"[skip] {job} in {root}: {e}")
        return None
    m = list(r["imtls"]).index(IMT)
    return {"c": np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :]), "lv": r["imtls"][IMT], "names": r["names"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tot, names, lv = {}, None, None
    for lab, (root, suf) in STAGES.items():
        fams = [mean(f"c_{lt.SHORT[f]}_{suf}", root) for f in lt.FAMS]
        if any(x is None for x in fams):
            print(f"[skip] stage '{lab}': jobs missing")
            continue
        tot[lab] = 1 - np.prod([1 - x["c"] for x in fams], axis=0)
        names, lv = fams[0]["names"], fams[0]["lv"]
    if not tot:
        raise SystemExit("no stage complete; run hazard/run_all.sh")
    poes = {round(-hc.INV_TIME / np.log(1 - p)): p for p in hc.POES}
    rows = []
    for lab, t in tot.items():
        for s, name in enumerate(names):
            rows.append({"stage": lab, "site": name, **{f"PGA_{rp}": iml(t[s], lv, p) for rp, p in poes.items()}})
    tab = pd.DataFrame(rows)
    tab.to_csv(OUT / "stages.csv", index=False)
    piv = tab.pivot(index="site", columns="stage", values=f"PGA_{min(poes)}")[list(tot)]
    piv = piv.reindex([s for s in hc.CITIES if s in piv.index])
    print(f"PGA (g) at {min(poes)} yr per stage\n" + piv.round(3).to_string())
    print("\nchange from the campaign reference, %")
    print((100 * (piv.div(piv.iloc[:, 0], axis=0) - 1)).round(1).to_string())

    def draw(ax, s, name):
        for (lab, t), col in zip(tot.items(), COLORS):
            ax.loglog(lv, t[s], color=col, lw=2.2 if lab == list(tot)[-1] else 1.5, label=lab)
        for rp, p in poes.items():
            ax.axhline(p, color="0.6", lw=0.6, ls=":")
            ax.text(XLIM[0] * 1.1, p * 1.15, f"{rp} yr", fontsize=8, color="0.4")
        ax.set(xlim=XLIM, ylim=YLIM, title=name.replace("_", " ").title())
        ax.grid(alpha=0.3, which="both", lw=0.3)

    n = len(names)
    nc = 5
    nr = int(np.ceil(n / nc))
    f, axs = plt.subplots(nr, nc, figsize=(W, H), sharex=True, sharey=True, squeeze=False)
    for i, name in enumerate(names):
        draw(axs.ravel()[i], i, name)
    for a in axs.ravel()[n:]:
        a.axis("off")
    axs[0, 0].legend(fontsize=8, loc="lower left")
    f.supxlabel("PGA (g)")
    f.supylabel("annual probability of exceedance")
    f.tight_layout()
    f.savefig(OUT / "stages.png", dpi=DPI)
    plt.close(f)
    for i, name in enumerate(names):
        f, a = plt.subplots(figsize=(W, H))
        draw(a, i, name)
        a.set(xlabel="PGA (g)", ylabel="annual probability of exceedance")
        a.legend(fontsize=10, loc="lower left")
        f.tight_layout()
        f.savefig(OUT / f"stages_{name}.png", dpi=DPI)
        plt.close(f)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
