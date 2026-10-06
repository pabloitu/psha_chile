# Preliminary full model at the cities from the PRELIM jobs (PRELIM=1 bash
# hazard/run_all.sh): family curves with their epistemic envelopes, the full
# model with and without faults, and the family shares of the exceedance rate.
#   pr_curves_<city>.png    interface, in-slab, crustal (with faults) and the full model:
#                           mean and 95 % envelope over realizations (post.py style)
#   pr_faults_<city>.png    full model with and without faults, mean and envelope
#   pr_shares.png           family share of the rate at the mean PGA 475 per city; in-slab split
#   pr_summary.csv          PGA 475 mean and fractiles, with / without faults, shares
#   pr_check.txt            fractile method (exact enumeration or Monte Carlo noise),
#                           and the sampled all-family job (c_all_final_sample) if it ran
# Run: PRELIM=1 python hazard/prelim.py

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

OUT = hc.OUT_ROOT / "_prelim"
FAM = [("c_if_final", "interface", "interface"), ("c_is_final", "in-slab", "in-slab"), ("c_cr_final", "crustal", "crustal")]
CLASSES = [("c_is_final_intra_slab", "intra_slab"), ("c_is_final_slab_deep", "slab_deep"), ("c_is_final_deep_nest", "deep_nest")]
NOFAULT = "c_cr_final_nofaults"
SAMPLED = "c_all_final_sample"
IMT = "PGA"
POE = 0.002105
ENV = (Q[0], Q[-1])     # the envelope of post.finish (2.5-97.5 %)
COL = paths.palette.FAMILY
CCOL = paths.palette.CLASS


def part(r, imt=IMT):
    m = list(r["imtls"]).index(imt)
    return r["curves"][:, :, [m], :], r["w"]


def main():
    post.set_style()
    OUT.mkdir(parents=True, exist_ok=True)
    fam = {lab: post.load(j) for j, lab, _ in FAM}
    names = fam["interface"]["names"]
    lv = fam["interface"]["imtls"][IMT]
    parts = [part(fam[lab]) for _, lab, _ in FAM]
    tot_m = combine.mean(parts)
    tot_q = combine.quantiles(parts, Q)
    nof = post.load(NOFAULT)
    parts_nf = parts[:2] + [part(nof)]
    nf_m, nf_q = combine.mean(parts_nf), combine.quantiles(parts_nf, Q)
    cls = {k: post.load(j) for j, k in CLASSES if (hc.OUT_ROOT / j / "build.json").exists()}

    n = int(np.prod([len(p[1]) for p in parts]))
    log = [f"[check] fractiles: exact enumeration of {n} combinations of family realizations" if n <= 5e6 else
           "[check] Monte Carlo noise of the fractiles (two independent runs): "
           + ", ".join(f"{k}: {e:.3g}" for k, e in combine.convergence(parts, q=ENV))]
    rows, sh = [], []
    for s, name in enumerate(names):
        title = name.replace("_", " ").title()
        f, ax = plt.subplots(figsize=(7, 5.5))
        for _, lab, key in FAM:
            r = fam[lab]
            c = r["curves"][r["names"].index(name), :, list(r["imtls"]).index(IMT), :]
            draw(ax, lv, c, r["w"], COL[key], lab)
        ax.loglog(lv, tot_m[s, 0], color="k", lw=2.5, label="Full model")
        ax.fill_between(lv, tot_q[0, s, 0], tot_q[-1, s, 0], color="k", alpha=0.15, lw=0)
        finish(ax, IMT, title, [POE], OUT / f"pr_curves_{name}.png")

        f, ax = plt.subplots(figsize=(7, 5.5))
        ax.loglog(lv, tot_m[s, 0], color=COL["crustal"], lw=2.5, label="With faults")
        ax.fill_between(lv, tot_q[0, s, 0], tot_q[-1, s, 0], color=COL["crustal"], alpha=0.3, lw=0)
        ax.loglog(lv, nf_m[s, 0], color="0.3", lw=2, ls="--", label="Without faults")
        ax.fill_between(lv, nf_q[0, s, 0], nf_q[-1, s, 0], color="0.3", alpha=0.2, lw=0)
        finish(ax, IMT, f"{title}: faults", [POE], OUT / f"pr_faults_{name}.png")

        x = post.iml(tot_m[s, 0], lv, POE)
        xn = post.iml(nf_m[s, 0], lv, POE)
        row = {"site": name, "pga475_mean": x, "pga475_nofaults": xn, "faults_pct": 100 * (x / xn - 1),
               **{f"q{100 * q:g}": post.iml(tot_q[i, s, 0], lv, POE) for i, q in enumerate(Q)}}
        rt = combine.rate(POE)
        for _, lab, key in FAM:
            r = fam[lab]
            c = r["w"] @ r["curves"][r["names"].index(name), :, list(r["imtls"]).index(IMT), :]
            share = combine.rate(np.exp(np.interp(np.log(x), np.log(lv), np.log(np.maximum(c, 1e-30))))) / rt
            row[f"share_{key}"] = 100 * share
            sh.append({"site": name, "part": key, "share": 100 * share})
        for k, r in cls.items():
            c = r["w"] @ r["curves"][r["names"].index(name), :, list(r["imtls"]).index(IMT), :]
            share = combine.rate(np.exp(np.interp(np.log(x), np.log(lv), np.log(np.maximum(c, 1e-30))))) / rt
            row[f"share_{k}"] = 100 * share
            sh.append({"site": name, "part": k, "share": 100 * share})
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "pr_summary.csv", index=False)
    print(t.round(3).to_string(index=False))

    # shares: families stacked, in-slab classes stacked beside them
    st = pd.DataFrame(sh)
    f, ax = plt.subplots(figsize=(12, 6.5))
    xs = np.arange(len(names))
    bot = np.zeros(len(names))
    for _, lab, key in FAM:
        v = st[st["part"] == key].set_index("site").loc[names, "share"].values
        ax.bar(xs - 0.2, v, 0.38, bottom=bot, color=COL[key], label=lab)
        bot += v
    if cls:
        bot = np.zeros(len(names))
        for _, k in CLASSES:
            if k in cls:
                v = st[st["part"] == k].set_index("site").loc[names, "share"].values
                ax.bar(xs + 0.2, v, 0.38, bottom=bot, color=CCOL[k], label=paths.palette.NAME[k])
                bot += v
    ax.set_xticks(xs)
    ax.set_xticklabels([n.replace("_", " ").title() for n in names], rotation=30, ha="right", fontsize=12)
    ax.set_ylabel("Share of the exceedance rate at the mean PGA 475 yr (%)", fontsize=14)
    ax.set_title("Families (left bars) and in-slab classes (right bars)", fontsize=16)
    ax.legend(ncol=3, loc="upper right", frameon=True)
    f.savefig(OUT / "pr_shares.png", dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(f)

    # the sampled all-family job, if it ran: OpenQuake's fractiles against the combiner
    if (hc.OUT_ROOT / SAMPLED / "build.json").exists():
        try:
            sm = post.load(SAMPLED)
            c, w = part(sm)
            q = post.wquant(c[:, :, 0, :].transpose(1, 0, 2).reshape(len(w), -1), w, Q)
            q = q.reshape(len(Q), len(names), -1)
            ok = tot_q[:, :, 0, :] > 1e-5
            err = np.max(np.abs(q[ok] / tot_q[:, :, 0, :][ok] - 1))
            log.append(f"[check] sampled all-family job ({len(w)} samples) vs combiner: "
                       f"max relative difference of the fractiles {err:.3g} (PoE > 1e-5)")
        except SystemExit as e:
            log.append(f"[skip] {SAMPLED}: {e}")
    (OUT / "pr_check.txt").write_text("\n".join(log) + "\n")
    print("\n".join(log))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
