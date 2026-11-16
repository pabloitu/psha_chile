"""Fagnano multi-fault row (Pablo, 16 Nov): the measured Magallanes–Fagnano traces as separate faults, the strict
UCERF3 rupture set (rupset.py) and the SHERIFS partition with the Patagonia target, against the joined system source
of the model. Patagonia count test as arc.py. Writes tables/mf_fagnano_<DATE>.csv and figs/<DATE>/mf_fagnano.png."""
import numpy as np
import pandas as pd
from scipy import stats

import arc
import background as BG
import faults as F
import join as J
import multifault as MF
import rupset as R
import gr

# settings
DATE = F.DATE
CLS = "patagonia"
JUMP = 15.0
THICK = (10.0, 20.0)
PSIS = (0.6, 0.8, 1.0)
SEEDS = tuple(range(1, 11))


def main():
    s, rr, _ = F.load("A", split_system=True)
    sj, rj, _ = F.load("A")
    pat = (s.cls == CLS).to_numpy()
    sp = s[pat].reset_index(drop=True)
    b = F.bvals()[CLS]
    fit = J.fits()[(CLS, "taper")]
    n, T = arc.observed(CLS)
    k0 = int(round((F.R.MMIN - J.CENTRES[0]) / 0.1))
    s6, s7 = J.CENTRES >= 5.95, J.CENTRES >= 6.95
    o6 = float(n[s6].sum())
    d = gr.load(BG.CAT, mlow=6.95)
    te = gr.tend(gr.load(BG.CAT))
    w = d[f"W_{CLS}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), b)
    hist = {M: (float(w[(d.mw.to_numpy() >= M - 0.05) & (d.t.to_numpy() >= y)].sum()), te - y) for M, y in MF.HIST}
    R.JUMP_KM, R.MIN_SR = JUMP, 0.0
    rows, keep = [], {}
    for z in THICK:
        rups, sub = R.ruptures(sp, z, main_only=False)
        ch = [tuple(r["faults"]) for r in R.scenarios(rups)]
        for ps in PSIS:
            MF.PSI = ps
            j = [i for i, (p, zz, _) in enumerate(F.BR) if p == ps and zz == z]
            wj = F.W[j] / F.W[j].sum()
            joined = np.zeros(J.CENTRES.size)
            joined[k0:k0 + F.NB] = (rj[(sj.cls == CLS).to_numpy()][:, j] * wj[None, :, None]).sum(axis=(0, 1))[:J.CENTRES.size - k0]
            for sd in SEEDS:
                src, mx, rate, nms = MF.run(z, sp, ch, b, np.random.default_rng(sd))
                tot = np.zeros(J.CENTRES.size)
                tot[k0:k0 + F.NB] = rate.sum(axis=0)[:J.CENTRES.size - k0]
                for lab, r in (("sherifs", tot), ("joined", joined)):
                    bg = J.background(fit, r)
                    e6 = float(((r + bg)[s6] * T[s6]).sum())
                    hx = {M: float((r + bg)[J.CENTRES >= M - 0.05].sum() * T_) for M, (o, T_) in hist.items()}
                    rows.append(dict(model=lab, thickness=z, psi=ps, seed=sd, scenarios=len(ch), N6=float(r[s6].sum()),
                                     N7=float(r[s7].sum()), mmax=float(J.CENTRES[r > 0].max()) if (r > 0).any() else np.nan,
                                     nms_share=float(nms.sum() / MF.budget(sp, z).sum()) if lab == "sherifs" else np.nan,
                                     exp6=e6, obs6=o6, p6=float(stats.poisson.cdf(round(o6), e6)),
                                     **{f"exp{M:g}_hist": e for M, e in hx.items()},
                                     **{f"obs{M:g}_hist": o for M, (o, _) in hist.items()},
                                     **{f"p{M:g}_hist": float(1 - stats.poisson.cdf(round(hist[M][0]) - 1, e)) for M, e in hx.items()}))
                    if lab == "joined" and sd > 1:
                        rows.pop()
                keep[(z, ps, sd)] = (tot, joined)
    t = pd.DataFrame(rows)
    t.round(5).to_csv(F.HERE / "tables" / f"mf_fagnano_{DATE}.csv", index=False)
    g = t.groupby(["model", "thickness", "psi"]).mean(numeric_only=True)
    with pd.option_context("display.width", 250):
        print(f"{len(sp)} Patagonia faults split ({int((sp.sr_used >= 5).sum())} Fagnano traces); observed Patagonia Mw>=6 since 1976 {o6:.2f}; "
              f"hist: {{7: {hist[7.0][0]:.2f}, 7.5: {hist[7.5][0]:.2f}}}")
        print(g[["scenarios", "N6", "N7", "mmax", "nms_share", "exp6", "p6", "exp7_hist", "p7_hist", "exp7.5_hist", "p7.5_hist"]].round(3).to_string())
    figure(keep, fit, n, T)
    return t


def figure(keep, fit, n, T):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import sys
    sys.path.insert(0, str(F.ROOT))
    import palette as P
    from pituplots.style.axes import darkgrid
    P.apply()
    m = J.CENTRES
    ok = (n > 0) & (T > 0)
    pos = lambda r: np.where(r > 0, r, np.nan)
    f, ax = plt.subplots(1, 2, figsize=(11, 5.2), sharey=True, layout="constrained")
    for a, z in zip(ax, THICK):
        a.plot(m, pos(fit), color="0.55", lw=3, label="catalogue fit")
        for c, ps in zip(P.SERIES, PSIS):
            r = np.array([keep[(z, ps, sd)][0] for sd in SEEDS])
            tot = r + np.array([J.background(fit, x) for x in r])
            a.fill_between(m, pos(tot.min(0)), pos(tot.max(0)), color=c, alpha=0.2, lw=0)
            a.plot(m, pos(tot.mean(0)), color=c, lw=1.8, label=f"traces + SHERIFS + background, ψ {ps:g}")
            jo = keep[(z, ps, 1)][1]
            a.plot(m, pos(jo + J.background(fit, jo)), color=c, lw=1.2, ls="--", label=f"joined system + background, ψ {ps:g}")
        a.plot(m[ok], (n / np.where(T > 0, T, 1))[ok], "o", ms=5, color="steelblue", mec="k", mew=0.4, label="observed 1976–2026")
        from figs_s3 import old_events
        d = gr.load(BG.CAT, mlow=4.45)
        a.plot(m, pos(old_events(d, CLS, F.bvals()[CLS], m)), "D", ms=6, mfc="white", mec="darkred", mew=1.2, zorder=7,
               label="Mw ≥ 7 since 1905 (≥ 7.5 since 1830), not in the fit")
        a.axvline(5.95, color="0.6", lw=0.8, ls=":")
        darkgrid(a)
        a.set_yscale("log")
        a.set_ylim(1e-5, 1)
        a.set_xlim(4.9, 8.4)
        a.set_xlabel("Mw (0.1 bins)")
        a.set_title(f"thickness {z:g} km", fontsize=11)
    ax[0].set_ylabel("events per year in the bin")
    ax[0].legend(fontsize=7.5, loc="lower left", frameon=False)
    f.suptitle("Crustal Patagonia, database A: Magallanes–Fagnano as separate traces with multi-fault ruptures (SHERIFS)\n"
               "against the joined system source (band: 10 seeds)", x=0.01, ha="left", fontsize=11)
    f.savefig(F.HERE / "figs" / DATE / "mf_fagnano.png", dpi=150)
    plt.close(f)


if __name__ == "__main__":
    main()
