"""Kernel diagnostic (S3, after Pablo's question): the calibration of background.py repeated with the Gaussian kernel
(K = exp(-r^2 / 2 d^2), the same adaptive bandwidth) next to Helmstetter's power law, and on the full catalogue
(complete events, not declustered) next to the two declustering options. Nothing in the model changes; the chosen n
stays that of background.py. Writes tables/calibration_kernels_<DATE>.csv and figs/kernel_calibration_<DATE>.png.
"""
import numpy as np
import pandas as pd

import background as BG
import smooth as S

# settings
DATE = "2026-11-16e"
KINDS = {"power": "Helmstetter power law", "gauss": "Gaussian"}
OPTIONS = {"gk": "Gardner–Knopoff", "nn": "nearest neighbour", "full": "full catalogue"}
NS = BG.CANDS


def main():
    d, g = BG.events(), BG.grid()
    d["keep_full"] = True
    gl, ga = g.lon.to_numpy(), g.lat.to_numpy()
    rows = []
    for m in OPTIONS:
        for c in list(BG.CLASSES) + ["crustal"]:
            tr, ts = BG.sel(d, c, m, t1=BG.SPLIT), BG.sel(d, c, m, t0=BG.SPLIT)
            idx = S.cells(gl, ga, ts[0], ts[1])
            uni = S.loglik(np.ones(len(g)), idx, ts[2])
            for k in KINDS:
                for n, ll in S.calibrate(tr, ts, gl, ga, NS, kind=k):
                    rows.append(dict(option=m, unit=c, kernel=k, n=n, loglik=ll, gain_uniform=ll - uni,
                                     train=tr[2].sum(), test=ts[2].sum()))
    t = pd.DataFrame(rows)
    ref = t[(t.kernel == "power") & (t.n == 5)].set_index(["option", "unit"]).loglik
    t["d_vs_power5"] = t.loglik - ref.loc[list(zip(t.option, t.unit))].to_numpy()
    t.round(4).to_csv(BG.TAB / f"calibration_kernels_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        print(t.pivot_table(index=["unit", "option", "kernel"], columns="n", values="d_vs_power5").round(1).to_string())
        b = t.loc[t.groupby(["unit", "option", "kernel"]).loglik.idxmax()]
        print(b[["unit", "option", "kernel", "n", "d_vs_power5", "gain_uniform", "train", "test"]].round(1).to_string(index=False))
    figure(t)


def figure(t):
    import sys
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(BG.ROOT))
    import palette as P
    P.apply()
    units = list(BG.CLASSES) + ["crustal"]
    f, ax = plt.subplots(1, len(units), figsize=(19, 4.6))
    for a, u in zip(ax, units):
        for i, m in enumerate(OPTIONS):
            for k, ls in (("power", "-"), ("gauss", "--")):
                x = t[(t.unit == u) & (t.option == m) & (t.kernel == k)]
                a.plot(x.n, x.gain_uniform, ls, marker="o", ms=3.5, color=P.SERIES[i],
                       label=f"{OPTIONS[m]}, {KINDS[k]}")
        a.axvspan(4.5, 100, color="0.95", zorder=0)
        a.set_xscale("log")
        a.set_xticks(NS)
        a.set_xticklabels([str(n) for n in NS], fontsize=8)
        a.set_title(P.CLASS_NAME.get(u, "crustal, all classes"), fontsize=11)
        a.set_xlabel("n (neighbour of the bandwidth)")
    ax[0].set_ylabel("log-likelihood gain over a uniform map")
    ax[-1].legend(fontsize=8, loc="lower left")
    f.tight_layout()
    f.savefig(BG.FIG / f"kernel_calibration_{DATE}.png", dpi=160)
    plt.close(f)


if __name__ == "__main__":
    main()
