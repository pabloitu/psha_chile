"""Mmax pad tornado rows (DECISIONS, 16 Nov; orchestrator): the crustal reference branches rebuilt with the class Mmax
pad 0.0 and 0.4 against 0.2, through the background shapes (fits tables _pad00 / _pad04), the join and the class-Mmax
cap of the multi-fault ruptures; and the single faults with Leonard + 0.0 / 0.2 / 0.4 (FAULT_PAD). Reports per class
and system the background N(>= 6, 7), the fault share of the fit, the multi-fault Mmax and rates and the large-event
checks. Writes tables/pad_rows_<DATE>.csv. No files until build.py reads the rows.
"""
import numpy as np
import pandas as pd
from scipy import stats

import arc
import background as BG
import faults as F
import join as J
import multifault as MF
import gr

# settings
DATE = F.DATE
PADS = (0.0, 0.2, 0.4)
FPADS = (0.0, 0.2, 0.4)
REF = dict(db="A", jump=15.0, z=20.0, psi=0.8)
SEEDS = tuple(range(1, 11))


def checks(c, tot, fit, b):
    """Expected counts of class c in the windows of arc.observed and MF.HIST for the fault + background MFD."""
    n, T = arc.observed(c)
    bg = J.background(fit, tot)
    r = tot + bg
    s6 = J.CENTRES >= 5.95
    o6, e6 = float(n[s6].sum()), float((r[s6] * T[s6]).sum())
    d = gr.load(BG.CAT, mlow=6.95)
    te = gr.tend(gr.load(BG.CAT))
    w = d[f"W_{c}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), b)
    out = dict(obs6=o6, exp6=e6, p6=float(stats.poisson.cdf(round(o6), e6)), bg_N6=float(bg[s6].sum()),
               bg_N7=float(bg[J.CENTRES >= 6.95].sum()), fit_N6=float(fit[s6].sum()), fit_N7=float(fit[J.CENTRES >= 6.95].sum()),
               faults_N6=float(tot[s6].sum()), faults_N7=float(tot[J.CENTRES >= 6.95].sum()),
               share6=float(tot[s6].sum() / max(fit[s6].sum(), 1e-12)), mmax_faults=float(J.CENTRES[tot > 0].max()) if (tot > 0).any() else np.nan)
    for M, y in MF.HIST:
        o = float(w[(d.mw.to_numpy() >= M - 0.05) & (d.t.to_numpy() >= y)].sum())
        e = float(r[J.CENTRES >= M - 0.05].sum() * (te - y))
        out[f"obs{M:g}_hist"], out[f"exp{M:g}_hist"], out[f"p{M:g}_hist"] = o, e, float(1 - stats.poisson.cdf(round(o) - 1, e))
    return out


def main():
    import geopandas as gpd
    gpd.options.io_engine = "fiona"
    rows = []
    for pad in PADS:
        BG.set_pad(pad)
        fits = {c: J.on(*BG.mfd(c, "taper")) for c in F.CLASSES}
        bv = F.bvals()
        for fpad in FPADS:
            if fpad and pad != 0.2:
                continue
            F.FAULT_PAD = fpad
            s, rr, _ = F.load(REF["db"])
            j = [i for i, (p, z, _) in enumerate(F.BR) if p == REF["psi"] and z == REF["z"]]
            k0 = int(round((F.R.MMIN - J.CENTRES[0]) / 0.1))
            seg = {c: np.zeros(J.CENTRES.size) for c in F.CLASSES}
            for c in F.CLASSES:
                seg[c][k0:k0 + F.NB] = rr[(s.cls == c).to_numpy()][:, j].mean(axis=1).sum(axis=0)[:J.CENTRES.size - k0]
            for c in F.CLASSES:
                rows.append(dict(pad=pad, fault_pad=fpad, system="segmented", cls=c, **checks(c, seg[c], fits[c], bv[c])))
            if fpad:
                continue
            # multi-fault reference: LOFS by SHERIFS (strict set), the other faults as the mean of the shapes
            sysn = gpd.read_file(F.DBS["A"]["file"]).set_index("fid")["system"]
            isl = s.fid.map(sysn).eq(MF.LOFS).to_numpy()
            sl = s[isl].reset_index(drop=True)
            MF.MIN_SR, MF.PSI = MF.MAIN_SR["A"], REF["psi"]
            ch = MF.strict(sl, REF["jump"])
            rate = None
            for sd in SEEDS:
                src, _, r, _ = MF.run(REF["z"], sl, ch, bv["arc"], np.random.default_rng(sd))
                rate = r if rate is None else rate + r
            rate /= len(SEEDS)
            mf = {c: np.zeros(J.CENTRES.size) for c in F.CLASSES}
            for c in F.CLASSES:
                mf[c][k0:k0 + F.NB] = rr[(s.cls == c).to_numpy() & ~isl][:, j].mean(axis=1).sum(axis=0)[:J.CENTRES.size - k0]
            for q, r in zip(src, rate):
                c = sl.cls[max(q["members"], key=lambda f: sl.L[f])]
                mf[c][k0:k0 + F.NB] += r[:J.CENTRES.size - k0]
            lin = [q for q, r in zip(src, rate) if len(q["members"]) > 1 and r.sum() > 0]
            for c in F.CLASSES:
                rows.append(dict(pad=pad, fault_pad=0.0, system="multi-fault", cls=c, scenarios=len(ch), scenarios_with_rate=len(lin),
                                 mmax_scenarios=max((q["hi"] for q in lin), default=np.nan), **checks(c, mf[c], fits[c], bv[c])))
    F.FAULT_PAD = 0.0
    BG.set_pad(0.2)
    t = pd.DataFrame(rows)
    t.round(5).to_csv(F.HERE / "tables" / f"pad_rows_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        c = ["pad", "fault_pad", "system", "cls", "fit_N6", "bg_N6", "bg_N7", "faults_N6", "faults_N7", "share6", "mmax_faults",
             "exp6", "obs6", "p6", "exp7_hist", "obs7_hist", "p7_hist", "exp7.5_hist", "p7.5_hist"]
        print(t[c].round(3).to_string(index=False))
    return t


if __name__ == "__main__":
    main()
