# s04_rates.py
# Rate parameters for every source-model end-branch.
#   seismic branch : rate at MMIN_HAZ from s03 (AB_ESTIMATOR), b from s03
#   geodetic branch: Mdot0 = chi * mu * A * v per segment and chi variant;
#                    rate at MMIN_HAZ solved so the MFD moment equals Mdot0
#                    (direct closure, option A), b borrowed from s03
# Both branches, both MFD forms (tgr / tapered with corner = MMAX), single
# Mmax = MMAX[seg]. Also the closure diagnostic: catalog-implied moment vs
# geodetic moment -> effective coupling per segment.
# Outputs: outputs/rates/branch_params.csv   consumed by s05
#          outputs/rates/moment_closure.csv  diagnostic
#          figures/s04_branch_mfds.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sub_config as C
from s03_ab import load_dc, complete_subset, obs_cum_rates

RT_DIR = C.OUT_DIR / "rates"
DM = 0.01


def m0(m):
    return 10 ** (1.5 * np.asarray(m, float) + 9.05)


def cum_shape(form, b, mmin, mmax, grid):
    """
    Cumulative N(>=m) for unit rate at mmin. Both forms are hard-truncated
    at mmax (no tapered tail beyond it — no admissible fault area there).

    tgr: doubly truncated GR. tapered: Kagan tapered Pareto with corner
    moment at mmax, truncated and renormalized at mmax (beta = 2b/3).
    """
    if form == "tgr":
        n = ((10 ** (-b * grid) - 10 ** (-b * mmax))
             / (10 ** (-b * mmin) - 10 ** (-b * mmax)))
        return np.clip(n, 0, None)
    beta = 2.0 * b / 3.0

    def tap(m):
        return ((m0(mmin) / m0(m)) ** beta
                * np.exp((m0(mmin) - m0(m)) / m0(mmax)))

    n = (tap(grid) - tap(mmax)) / (1.0 - tap(mmax))
    return np.where(grid > mmax, 0.0, np.clip(n, 0, None))


def moment_per_unit_rate(form, b, mmin, mmax):
    grid = np.arange(mmin, mmax + DM, DM)
    ncum = cum_shape(form, b, mmin, mmax, grid)
    ninc = np.maximum(ncum[:-1] - ncum[1:], 0)
    mc = grid[:-1] + DM / 2
    return (ninc * m0(mc)).sum()


def main():
    RT_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    ab = json.loads((C.OUT_DIR / "ab" / "ab_results.json").read_text())
    est = C.AB_ESTIMATOR
    areas = pd.read_csv(C.GEOM_DIR / "segment_areas.csv").set_index("seg_id")

    # config MMAX must not sit below the catalog: list top events per
    # segment and fail if any observed magnitude exceeds MMAX
    dfc = load_dc(C.DC_METHOD)
    bad = False
    for sid in C.SEG_IDS + [C.FULL_ID]:
        cat = dfc if sid == C.FULL_ID else dfc[dfc["seg"] == sid]
        top = cat.nlargest(3, "mag")
        mm = C.MMAX.get(sid, max(C.MMAX.values()))
        tops = ", ".join(f"M{r.mag:.1f}@{r.year:.0f}" for r in top.itertuples())
        mark = "  <-- exceeds MMAX" if top["mag"].max() > mm + 1e-9 else ""
        print(f"[mmax] {sid}: config {mm}, catalog top: {tops}{mark}")
        bad = bad or top["mag"].max() > mm + 1e-9
    if bad:
        raise SystemExit("config MMAX below observed catalog magnitude — "
                         "update sub_config.MMAX (Mmax = M_obs by decision)")

    # full-margin inputs: area from s00, v and chi area-weighted
    aw = np.array([areas.loc[s, "area_km2"] for s in C.SEG_IDS])
    v_full = float((aw * [C.V_CONV[s] for s in C.SEG_IDS]).sum() / aw.sum())
    chi_full = float((aw * [C.CHI[s] for s in C.SEG_IDS]).sum() / aw.sum())
    mmax_full = max(C.MMAX.values())

    rows, closure = [], []
    for geom, sids in (("segmented", C.SEG_IDS), ("non_segmented", [C.FULL_ID])):
        for sid in sids:
            seg = ab["segments"][sid]
            b = seg[est]["b"]
            lam_seis = seg[est]["rate_mmin"]
            A = areas.loc[sid, "area_km2"] * 1e6
            v = C.V_CONV[sid] if sid in C.V_CONV else v_full
            chi0 = C.CHI[sid] if sid in C.CHI else chi_full
            mmax = C.MMAX.get(sid, mmax_full)

            for form in ("tgr", "tapered"):
                mpr = moment_per_unit_rate(form, b, C.MMIN_HAZ, mmax)
                w0 = C.W_GEOM[geom] * C.W_MFD[form]

                rows.append({"geom": geom, "seg": sid, "rate_model": "seismic",
                             "chi_branch": "-", "form": form, "b": b,
                             "mmax": mmax, "lam_mmin": lam_seis,
                             "M0_rate": lam_seis * mpr,
                             "weight": w0 * C.W_RATE["seismic"]})

                for br, dchi in (("lo", -C.DCHI), ("mid", 0.0), ("hi", C.DCHI)):
                    chi = min(max(chi0 + dchi, 0.0), 1.0)
                    md0 = chi * C.MU * A * v
                    rows.append({"geom": geom, "seg": sid,
                                 "rate_model": "geodetic", "chi_branch": br,
                                 "form": form, "b": b, "mmax": mmax,
                                 "lam_mmin": md0 / mpr, "M0_rate": md0,
                                 "weight": w0 * C.W_RATE["geodetic"]
                                 * C.CHI_W[br]})

            # closure diagnostic on the tgr shape; mmax_adm is the
            # Thingbaijam et al. (2017) interface median from segment area
            # (validation only — Mmax stays M_obs by decision)
            mpr = moment_per_unit_rate("tgr", b, C.MMIN_HAZ, mmax)
            md_cat = lam_seis * mpr
            md_pot = C.MU * A * v
            m_adm = (np.log10(A / 1e6) + 3.292) / 0.949
            closure.append({"geom": geom, "seg": sid,
                            "M0_catalog": md_cat, "M0_full_coupling": md_pot,
                            "chi_effective": round(md_cat / md_pot, 3),
                            "chi_assumed": chi0,
                            "ratio_cat_geo": round(md_cat / (chi0 * md_pot), 3),
                            "mmax_obs": mmax, "mmax_adm": round(m_adm, 2)})

    bp = pd.DataFrame(rows)
    # weights must close per geometry family: each geom's branches sum to W_GEOM
    for geom in ("segmented", "non_segmented"):
        w = bp[(bp["geom"] == geom)
               & (bp["seg"] == (C.SEG_IDS[0] if geom == "segmented"
                                else C.FULL_ID))]["weight"].sum()
        if abs(w - C.W_GEOM[geom]) > 1e-9:
            raise RuntimeError(f"weights for {geom} sum to {w}")
    bp.to_csv(RT_DIR / "branch_params.csv", index=False)

    cl = pd.DataFrame(closure)
    cl.to_csv(RT_DIR / "moment_closure.csv", index=False)
    print(bp.round(4).to_string(index=False))
    print("\nmoment closure (chi_effective = catalog moment / full-coupling "
          "moment; ratio_cat_geo ~ 1 means branches agree):")
    print(cl.to_string(index=False))
    for _, r in cl.iterrows():
        if abs(r["mmax_obs"] - r["mmax_adm"]) > 0.3:
            print(f"[note] {r['seg']}: Mmax_obs={r['mmax_obs']} vs "
                  f"Thingbaijam admissible {r['mmax_adm']} from area — "
                  "expected for the Chilean giants; document, don't change")
        if not 0.3 < r["ratio_cat_geo"] < 3.0:
            print(f"[warn] {r['seg']}: catalog and geodetic moment differ "
                  f"by x{r['ratio_cat_geo']:.2f} — segmentation, chi, or "
                  "completeness deserve a second look")

    # all branch MFDs vs observed, per segment, with the weighted ensemble
    y_end = ab["meta"]["y_end"]
    styles = {("seismic", "-", "tgr"): ("C0", "-", 1.8, "seismic tgr"),
              ("seismic", "-", "tapered"): ("C0", "--", 1.8, "seismic tapered"),
              ("geodetic", "lo", "tgr"): ("gold", "-", 1.0, "geod tgr chi-lo"),
              ("geodetic", "mid", "tgr"): ("C1", "-", 1.8, "geod tgr chi-mid"),
              ("geodetic", "hi", "tgr"): ("C3", "-", 1.0, "geod tgr chi-hi"),
              ("geodetic", "lo", "tapered"): ("gold", "--", 1.0, "geod tap chi-lo"),
              ("geodetic", "mid", "tapered"): ("C1", "--", 1.8, "geod tap chi-mid"),
              ("geodetic", "hi", "tapered"): ("C3", "--", 1.0, "geod tap chi-hi")}
    ids = C.SEG_IDS + [C.FULL_ID]
    fig, axes = plt.subplots(1, len(ids), figsize=(3.4 * len(ids), 4.2),
                             sharey=True)
    for ax, sid in zip(np.atleast_1d(axes), ids):
        sub = bp[bp["seg"] == sid]
        mmax = sub["mmax"].iloc[0]
        grid = np.arange(C.MMIN_HAZ, mmax + 0.05, 0.05)

        cat = dfc if sid == C.FULL_ID else dfc[dfc["seg"] == sid]
        comp = complete_subset(cat, y_end)
        comp = comp[comp["mag"] >= C.MMIN_HAZ]
        if len(comp):
            og = np.arange(C.MMIN_HAZ, comp["mag"].max() + 0.05, 0.1)
            ax.semilogy(og, np.maximum(obs_cum_rates(comp, y_end, og), 1e-8),
                        "k.", ms=5, zorder=5, label="observed")

        wsum = sub["weight"].sum()
        ens = np.zeros_like(grid)
        for _, r in sub.iterrows():
            n = r["lam_mmin"] * cum_shape(r["form"], r["b"], C.MMIN_HAZ,
                                          r["mmax"], grid)
            ens += r["weight"] / wsum * n
            col, ls, lw, lab = styles[(r["rate_model"], r["chi_branch"]
                                       if r["rate_model"] == "geodetic"
                                       else "-", r["form"])]
            ax.semilogy(grid, np.maximum(n, 1e-8), color=col, ls=ls, lw=lw,
                        label=lab)
        ax.semilogy(grid, np.maximum(ens, 1e-8), "k", lw=2.4, alpha=0.75,
                    zorder=4, label="weighted ensemble")
        ax.axvline(mmax, color="gray", lw=0.5)
        ax.set_ylim(1e-6, 3)
        ax.set_title(sid, fontsize=9)
        ax.set_xlabel("M")
    np.atleast_1d(axes)[0].set_ylabel("N(>=M) /yr")
    h, l = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(C.FIG_DIR / "s04_branch_mfds.png", dpi=200)
    print(f"\nwrote {RT_DIR}")


if __name__ == "__main__":
    main()