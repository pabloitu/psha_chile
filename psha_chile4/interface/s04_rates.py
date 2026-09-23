# Rate parameters for every interface end branch.
#   seismic : b and rate at MMIN_HAZ from s03
#   geodetic: moment rate chi * mu * A * v, rate at MMIN_HAZ solved so the
#             MFD releases it; b from s03
# Both MFD forms, single Mmax per segment. Plus the catalog-vs-geodetic
# moment closure.
# Outputs: rates/branches.csv, rates/closure.csv, figures/s04_mfd.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cfg, gr
from interface import config
from interface.s03_ab import load_dc, t_end


def check_mmax(df, c):
    """Mmax = M_obs: stop if the catalog exceeds MMAX, warn if MMAX sits above it."""
    bad = []
    for sid in c.SEG_IDS + [c.FULL_ID]:
        sub = df if sid == c.FULL_ID else df[df["seg"] == sid]
        mm = c.MMAX.get(sid, max(c.MMAX.values()))
        top = sub.nlargest(3, "mag")
        print(f"[mmax] {sid}: config {mm}, catalog "
              + ", ".join(f"M{r.mag:.1f}@{int(r.year)}" for r in top.itertuples()))
        if top["mag"].max() > mm + 1e-9:
            bad.append(sid)
        elif mm > top["mag"].max() + c.MMAX_TOL:
            print(f"[mmax] WARNING {sid}: MMAX {mm} above M_obs {top['mag'].max():.1f}")
    if bad:
        raise SystemExit(f"catalog exceeds MMAX in {bad}; update config.MMAX")


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "rates"
    od.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)
    ab = json.loads((c.OUT / "ab" / "ab.json").read_text())["segments"]
    area = pd.read_csv(c.OUT / "geometry" / "areas.csv").set_index("seg")["area_km2"] * 1e6
    df = load_dc(c)
    check_mmax(df, c)

    # full margin: moment summed over segments, so both geometries carry the same budget
    md = lambda sids, d: sum(min(max(c.CHI[s] + d, 0), 1) * c.MU * area[s] * c.V_CONV[s] for s in sids)
    rows, clo = [], []
    for geom, sids in (("segmented", c.SEG_IDS), ("non_segmented", [c.FULL_ID])):
        for sid in sids:
            parts = c.SEG_IDS if sid == c.FULL_ID else [sid]
            b = ab[sid][c.AB_ESTIMATOR]["b"]
            lam = ab[sid][c.AB_ESTIMATOR]["rate_mmin"]
            mmax = c.MMAX.get(sid, max(c.MMAX.values()))
            for form in ("tgr", "tapered"):
                u = gr.mpr(form, b, c.MMIN_HAZ, mmax, c.M0_C)
                w0 = c.W_GEOM[geom] * c.W_MFD[form]
                base = {"geom": geom, "seg": sid, "form": form, "b": b, "mmax": mmax}
                rows.append({**base, "rate": "seismic", "chi": "-", "lam": lam,
                             "m0_rate": lam * u, "weight": w0 * c.W_RATE["seismic"]})
                for br, d in (("lo", -c.DCHI), ("mid", 0.0), ("hi", c.DCHI)):
                    rows.append({**base, "rate": "geodetic", "chi": br, "lam": md(parts, d) / u,
                                 "m0_rate": md(parts, d),
                                 "weight": w0 * c.W_RATE["geodetic"] * c.CHI_W[br]})
            u = gr.mpr("tgr", b, c.MMIN_HAZ, mmax, c.M0_C)
            full = sum(c.MU * area[s] * c.V_CONV[s] for s in parts)
            clo.append({"geom": geom, "seg": sid, "m0_catalog": lam * u, "m0_full_coupling": full,
                        "chi_effective": lam * u / full, "chi_assumed": md(parts, 0) / full,
                        "ratio_cat_geo": lam * u / md(parts, 0), "mmax": mmax,
                        "mmax_thingbaijam": (np.log10(area[sid] / 1e6) + 3.292) / 0.949})

    bp = pd.DataFrame(rows)
    for geom in c.W_GEOM:
        g = bp[bp["geom"] == geom]
        w = g[g["seg"] == g["seg"].iloc[0]]["weight"].sum()
        if abs(w - c.W_GEOM[geom]) > 1e-9:
            raise RuntimeError(f"{geom} weights sum to {w}")
    for m in (7.0, 8.0):
        bp[f"N{m}"] = [r.lam * gr.cum(r.form, r.b, c.MMIN_HAZ, r.mmax, m, c.M0_C) for r in bp.itertuples()]
    bp.to_csv(od / "branches.csv", index=False)
    cl = pd.DataFrame(clo)
    cl.to_csv(od / "closure.csv", index=False)
    print(bp.round(4).to_string(index=False))
    print(cl.round(3).to_string(index=False))
    for r in cl.itertuples():
        if not 0.3 < r.ratio_cat_geo < 3:
            print(f"[warn] {r.seg}: catalog/geodetic moment x{r.ratio_cat_geo:.2f}")

    tot = bp.groupby(["geom", "rate", "chi", "form"])[["N7.0", "N8.0"]].sum()
    print("\nannual rates summed per branch:\n" + tot.round(4).to_string())

    te = t_end(c)
    ids = c.SEG_IDS + [c.FULL_ID]
    f, axs = plt.subplots(1, len(ids), figsize=(3.4 * len(ids), 4.2), sharey=True)
    for ax, sid in zip(axs, ids):
        sub = bp[bp["seg"] == sid]
        g = np.arange(c.MMIN_HAZ, sub["mmax"].iloc[0] + 0.05, 0.05)
        d = df if sid == c.FULL_ID else df[df["seg"] == sid]
        comp = d[gr.complete(d, c.COMPLETENESS) & (d["mag"] >= c.MMIN_HAZ)]
        if len(comp):
            og = np.arange(c.MMIN_HAZ, comp["mag"].max() + 0.05, 0.1)
            ax.semilogy(og, gr.obs_cum(comp, c.COMPLETENESS, te, og), "k.", ms=5, zorder=5)
        ens = np.zeros_like(g)
        for r in sub.itertuples():
            n = r.lam * gr.cum(r.form, r.b, c.MMIN_HAZ, r.mmax, g, c.M0_C)
            ens += r.weight / sub["weight"].sum() * n
            ax.semilogy(g, np.maximum(n, 1e-8), color="C0" if r.rate == "seismic" else "C1",
                        ls="-" if r.form == "tgr" else "--", lw=1.6 if r.chi in ("-", "mid") else 0.6)
        ax.semilogy(g, np.maximum(ens, 1e-8), "k", lw=2.2, alpha=0.7)
        ax.set_ylim(1e-6, 3)
        ax.set_title(sid, fontsize=9)
        ax.set_xlabel("M")
    axs[0].set_ylabel("N(>=M)/yr  (blue seismic, orange geodetic, black weighted)")
    f.tight_layout()
    f.savefig(c.FIG / "s04_mfd.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s04")


if __name__ == "__main__":
    main()
