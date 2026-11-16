"""The arc bulge: the fault model of each variant against the observed arc earthquakes.

Fault count test: the number of arc events of Mw >= 6 the model expects inside the completeness table (faults of the
branch plus the background after the join, rates times the observation time of each bin) against the weighted count
observed there (class weight times the magnitude-error count, as the fit). For every branch of the fault tree the
Poisson probability of observing that few events; the weight of the branches that pass (p >= 0.05). Also the scale
of the fault moment that would match the observed count (the effective psi).

Writes tables/arc_test_<DATE>.csv, tables/arc_branches_<DATE>.csv and figs/arc_test_<DATE>.png.
"""
import sys

import numpy as np
import pandas as pd
from scipy import stats

import background as BG
import faults as F
import join as J
import gr  # noqa: E402

TAB, FIG = F.HERE / "tables", F.HERE / "figs"

# settings
DATE = "2026-11-16e"
CLS = "arc"
BANDS = ((6.0, 9.9), (6.0, 6.9), (7.0, 9.9))
P_PASS = 0.05


def observed(cls=CLS):
    """Weighted counts and observation times per bin on J.CENTRES (class cls, full catalogue)."""
    d = gr.load(BG.CAT, mlow=BG.MMIN)
    te = gr.tend(gr.load(BG.CAT))
    yr, T = gr.table_years(BG.TABLE, te)
    k = gr.kbin(d.mw)
    w = d[f"W_{cls}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), F.bvals()[cls])
    ok = (w > 0) & (d.t.to_numpy() >= yr[k])
    n = np.bincount(k[ok], w[ok], minlength=yr.size)
    c = gr.centres()
    s = c >= BG.MMIN - 1e-6
    return J.on(c[s], n[s]), J.on(c[s], T[s])


def main():
    ft, fc = J.fits(), J.fault_classes()
    n, T = observed()
    rows, brs = [], []
    for v in F.VARIANTS:
        fm, fb = fc[(v, CLS)]
        bg = J.background(ft[(CLS, "taper")], fm)
        for lo, hi in BANDS:
            s = (J.CENTRES >= lo - 1e-6) & (J.CENTRES <= hi + 1e-6)
            obs = float(n[s].sum())
            e_br = (fb[:, s] + bg[s]) * T[s]
            e = e_br.sum(axis=1)
            p = stats.poisson.cdf(np.round(obs), e)
            ef, eb = float((F.W @ fb[:, s] * T[s]).sum()), float((bg[s] * T[s]).sum())
            rows.append(dict(variant=v, band=f"{lo:.1f}–{hi:.1f}" if hi < 9 else f"≥ {lo:.1f}", observed=obs,
                             fit=float((ft[(CLS, "taper")][s] * T[s]).sum()), expected=float(F.W @ e),
                             faults=ef, background=eb, exp_lo=float(e.min()), exp_hi=float(e.max()),
                             p_mean=float(stats.poisson.cdf(np.round(obs), F.W @ e)),
                             weight_pass=float(F.W[p >= P_PASS].sum()), psi_eff=max(obs - eb, 0) / ef * 0.8 if ef > 0 else np.nan))
            if lo == 6.0 and hi > 9:
                for j, (ps, z, k) in enumerate(F.BR):
                    brs.append(dict(variant=v, psi=ps, depth=z, shape=k, weight=F.W[j], expected=e[j], p=p[j]))
    t, b = pd.DataFrame(rows), pd.DataFrame(brs)
    t.round(4).to_csv(TAB / f"arc_test_{DATE}.csv", index=False)
    b.round(5).to_csv(TAB / f"arc_branches_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        print(t.round(3).to_string(index=False))
        for v in F.VARIANTS:
            x = b[b.variant == v]
            print(v, "passing branches:", [f"{r.psi:g} {r.depth:g} {r.shape}" for r in x[x.p >= P_PASS].itertuples()])
    figure(t, b)
    bulge_figure()
    bulge_figure(("A_cm", "B_cm", "Bmm_cm"), "classmax", "fault Mmax = class maximum (7.9)")


def figure(t, b):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(F.ROOT))
    import palette as P
    P.apply()
    vs = list(F.VARIANTS)
    f, ax = plt.subplots(2, 3, figsize=(15, 8.5), sharex=True)
    edges = np.logspace(0, np.log10(b.expected.max() * 1.2), 30)
    for a, v in zip(ax.T.ravel(), vs):
        x = b[b.variant == v]
        r = t[(t.variant == v) & (t.band == "≥ 6.0")].iloc[0]
        a.hist(x.expected, bins=edges, weights=x.weight, color=P.SERIES[0], alpha=0.75, label="fault tree branches (weight)")
        lo, hi = stats.poisson.ppf([0.05, 0.95], r.observed)
        a.axvspan(max(lo, 0.5), hi, color="0.88", zorder=0, label="Poisson 5–95 % of the observed count")
        a.axvline(r.observed, color="k", lw=2, label="observed (weighted)")
        a.axvline(r.fit, color="k", lw=1, ls="--", label="catalogue fit")
        a.set_xscale("log")
        a.set_title(f"{F.NAMES[v]}\n{r.weight_pass:.0%} of the tree passes", fontsize=11)
    for a in ax[1]:
        a.set_xlabel("arc events of Mw ≥ 6 expected inside the completeness table")
    ax[0, 0].legend(fontsize=8.5, loc="upper left")
    f.tight_layout()
    f.savefig(FIG / f"arc_test_{DATE}.png", dpi=160)
    plt.close(f)



def bulge_figure(variants=("A", "B", "Bmm"), tag="leonard", title="fault Mmax by Leonard (2014)"):
    """The arc join, one panel per fault database: rates per 0.1 bin of the catalogue fit, the faults (weighted mean
    of the tree), the background after the join and their sum, with the observed rates inside the completeness table."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(F.ROOT))
    import palette as P
    P.apply()
    ft, fc = J.fits(), J.fault_classes()
    n, T = observed()
    m = J.CENTRES
    ok = (n > 0) & (T > 0)
    fit = ft[(CLS, "taper")]
    f, ax = plt.subplots(1, len(variants), figsize=(5.4 * len(variants), 5.2), sharey=True)
    for a, v in zip(ax, variants):
        fm = fc[(v, CLS)][0]
        bg = J.background(fit, fm)
        a.plot(m, np.where(fit > 0, fit, np.nan), color="0.55", lw=2.5, label="catalogue fit")
        a.plot(m, np.where(fm > 0, fm, np.nan), color=P.SERIES[1], lw=2, marker="o", ms=3, label="faults")
        a.plot(m, np.where(bg > 0, bg, np.nan), color=P.CLASS_COLOR[CLS], lw=2, marker="o", ms=3, label="background")
        a.plot(m, np.where(bg + fm > 0, bg + fm, np.nan), color="k", lw=1.2, ls="--", label="faults + background")
        a.plot(m[ok], (n / np.where(T > 0, T, 1))[ok], "s", color="k", mfc="white", ms=5, label="observed")
        a.axvline(5.95, color="0.75", lw=0.8)
        a.set_yscale("log")
        a.set_xlim(4.9, 8.6)
        a.set_ylim(1e-5, 1)
        a.set_xlabel("Mw (0.1 bins)")
        a.set_title(F.NAMES[v].replace(", class-maximum Mmax", ""))
    ax[0].set_ylabel("events per year in the bin")
    ax[0].legend(fontsize=9, loc="lower left")
    f.suptitle(f"Crustal arc: catalogue fit, faults and background, {title}", x=0.06, ha="left")
    f.tight_layout()
    f.savefig(FIG / f"arc_join_{tag}_{DATE}.png", dpi=160)
    plt.close(f)


if __name__ == "__main__":
    main()
