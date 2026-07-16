# check_domain_mfd.py
# Domain-level sanity check (e.g. intraarc): compare the catalog-derived
# b-value inside a tectonic-domain polygon with the b assigned to the faults
# there, and plot the combined MFD (capped background + faults) against the
# observed catalog rates. Works for any domain polygon (intraarc, forearc).
#
# Catalog rates honor time-varying completeness via the per-event
# (mc_window, tc_years) columns produced by the catalog pipeline; b is
# estimated with Weichert (1980) on those unequal observation periods.

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely
from shapely.ops import unary_union

from fault_buffers import load_union, cell_mask
from cap_ssm_mmax import bin_cols
from check_fault_ssm_merger import (read_fault_mfds, fault_bin_edges,
                                    add_fault_rates, load_crustal_catalog,
                                    CheckConfig)


@dataclass
class DomainConfig:
    domain_shp: Path = Path("../data/shapefiles/intraarc.shp")
    domain_name: str = "intraarc"
    ssm_pre_csv: Path = Path("ssm_crustal_outputs/ssm_mfd_grid.csv")
    ssm_post_csv: Path = Path("ssm_crustal_outputs/ssm_mfd_grid_capped.csv")
    fault_xml: Path = Path("../fault_model/crustal_faults_phi100_mgeo_tgr.xml")
    faults_shp: Path = Path("../data/active_faults/crustal_faults_chile_updated.shp")
    # catalogs for the OBSERVED MFD; default: the domain's own class catalog
    catalog_csvs: tuple = ()
    mc_min: float = 4.5
    dm: float = 0.1
    cap_mag: float = 6.0
    out_dir: Path = Path("merger_checks")

    def __post_init__(self):
        for f in ("domain_shp", "ssm_pre_csv", "ssm_post_csv",
                  "fault_xml", "faults_shp", "out_dir"):
            setattr(self, f, Path(getattr(self, f)))


def load_domain(shp: Path):
    g = gpd.read_file(shp)
    if g.crs is not None:
        g = g.to_crs("EPSG:4326")
    dom = unary_union(g.geometry)
    shapely.prepare(dom)
    return dom


def completeness_steps(cat: pd.DataFrame) -> pd.DataFrame:
    """
    Completeness step function reconstructed from the per-event
    (mc_window, tc_years) pairs: for magnitude M, the observation period is
    the tc_years of the largest mc_window <= M.
    """
    steps = (cat[["mc_window", "tc_years"]].dropna()
             .drop_duplicates().sort_values("mc_window").reset_index(drop=True))
    print(f"[completeness_steps] {len(steps)} windows:")
    print(steps.to_string(index=False))
    return steps


def obs_periods(mags: np.ndarray, steps: pd.DataFrame) -> np.ndarray:
    mc = steps["mc_window"].to_numpy()
    tc = steps["tc_years"].to_numpy()
    idx = np.searchsorted(mc, mags + 1e-9) - 1
    out = np.where(idx >= 0, tc[np.clip(idx, 0, len(tc) - 1)], np.nan)
    return out


def weichert(mags: np.ndarray, periods: np.ndarray, mmin: float,
             dm: float) -> dict:
    """
    Weichert (1980) ML estimate of (a, b) for unequal observation periods.

    Parameters
    ----------
    mags : array
        Event magnitudes (>= mmin, each within its completeness window).
    periods : array
        Observation period (yr) applicable to each event's magnitude.
    mmin, dm : float
        First bin lower edge and bin width.

    Returns
    -------
    dict with b, b_err, a (log10 N(>=0)/yr), rate_mmin (N(>=mmin)/yr), bins.
    """
    edges = np.arange(mmin, mags.max() + dm + 1e-9, dm)
    ctr = edges[:-1] + dm / 2.0
    n = np.histogram(mags, bins=edges)[0].astype(float)
    t = np.array([np.median(periods[(mags >= lo) & (mags < hi)])
                  if ((mags >= lo) & (mags < hi)).any() else np.nan
                  for lo, hi in zip(edges[:-1], edges[1:])])
    # fill empty bins from neighbours (completeness is monotone in M)
    for i in range(len(t)):
        if np.isnan(t[i]):
            prev = t[:i][~np.isnan(t[:i])]
            t[i] = prev[-1] if len(prev) else np.nan
    ok = ~np.isnan(t)
    ctr, n, t = ctr[ok], n[ok], t[ok]
    N = n.sum()

    beta = 1.5
    for _ in range(100):
        w = t * np.exp(-beta * ctr)
        f = (w * ctr).sum() / w.sum() - (n * ctr).sum() / N
        d = -((w * ctr**2).sum() / w.sum() - ((w * ctr).sum() / w.sum())**2)
        step = f / d
        beta -= step
        if abs(step) < 1e-10:
            break
    b = beta / math.log(10.0)

    w = np.exp(-beta * ctr)
    # annual rate for M >= mmin (Weichert ML activity estimate)
    rate_mmin = N * w.sum() / (t * w).sum()
    a = math.log10(rate_mmin) + b * mmin
    b_err = b / math.sqrt(N)

    print(f"[weichert] N={int(N)} events, b={b:.3f} +/- {b_err:.3f}, "
          f"rate(M>={mmin})={rate_mmin:.4f} /yr, a={a:.3f}")
    return {"b": b, "b_err": b_err, "a": a, "rate_mmin": rate_mmin,
            "edges": edges[np.concatenate([ok, [True]])], "n": n, "t": t,
            "ctr": ctr}


def fault_b_summary(cfg: DomainConfig, dom) -> pd.Series:
    g = gpd.read_file(cfg.faults_shp)
    if g.crs is not None:
        g = g.to_crs("EPSG:4326")
    inside = np.array([dom.contains(geom.centroid) for geom in g.geometry])
    bv = pd.to_numeric(g.loc[inside, "b_val"], errors="coerce")
    bv = bv.where(bv > 0, 1.0)  # model fallback rule
    print(f"[fault_b_summary] {inside.sum()} shapefile faults in "
          f"{cfg.domain_name}: applied b min={bv.min():.2f} "
          f"median={bv.median():.2f} mean={bv.mean():.2f} max={bv.max():.2f}")
    return bv


def check_domain(cfg: DomainConfig | None = None):
    cfg = cfg or DomainConfig()
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    dom = load_domain(cfg.domain_shp)

    # catalog inside domain
    base = CheckConfig(catalog_csvs=cfg.catalog_csvs) if cfg.catalog_csvs \
        else CheckConfig(catalog_csvs=(_default_domain_catalog(cfg),))
    cat = load_crustal_catalog(base)
    inside = cell_mask(cat["longitude"].to_numpy(),
                       cat["latitude"].to_numpy(), dom)
    cat = cat[inside].reset_index(drop=True)
    print(f"[check_domain] {len(cat)} {cfg.domain_name} events inside polygon")

    # 1) catalog b (Weichert on completeness windows) vs fault b
    steps = completeness_steps(cat)
    sel = cat[cat["mag"] >= cfg.mc_min].copy()
    per = obs_periods(sel["mag"].to_numpy(), steps)
    good = np.isfinite(per)
    wch = weichert(sel.loc[good, "mag"].to_numpy(), per[good],
                   mmin=cfg.mc_min, dm=cfg.dm)
    fb = fault_b_summary(cfg, dom)
    print(f"[check_domain] catalog b = {wch['b']:.3f} +/- {wch['b_err']:.3f}; "
          f"fault b (median applied) = {fb.median():.3f} -> "
          f"difference {wch['b'] - fb.median():+.3f}")

    # 2) combined MFD in the domain
    pre = pd.read_csv(cfg.ssm_pre_csv)
    post = pd.read_csv(cfg.ssm_post_csv)
    cmask = cell_mask(pre["lon"].to_numpy(), pre["lat"].to_numpy(), dom)
    cols = bin_cols(pre)
    names = [c for c, _, _ in cols]
    edges = np.array([lo for _, lo, _ in cols] + [cols[-1][2]])
    r_pre = pre.loc[cmask, names].to_numpy().sum(axis=0)
    r_post = post.loc[cmask, names].to_numpy().sum(axis=0)

    faults = read_fault_mfds(cfg.fault_xml)
    fdom = [f for f in faults if dom.contains(shapely.Point(f["lon"], f["lat"]))]
    print(f"[check_domain] {len(fdom)} / {len(faults)} fault sources in "
          f"{cfg.domain_name}")
    e_tot, r_tot = add_fault_rates(edges.copy(), r_post, fdom)

    # observed incremental rates n_i / t_i on the same bins
    oe = np.arange(cfg.mc_min, sel["mag"].max() + cfg.dm + 1e-9, cfg.dm)
    on = np.histogram(sel.loc[good, "mag"], bins=oe)[0].astype(float)
    ot = np.array([np.median(per[good][(sel.loc[good, "mag"] >= lo)
                                       & (sel.loc[good, "mag"] < hi)])
                   if ((sel.loc[good, "mag"] >= lo)
                       & (sel.loc[good, "mag"] < hi)).any() else np.nan
                   for lo, hi in zip(oe[:-1], oe[1:])])
    for i in range(len(ot)):
        if np.isnan(ot[i]):
            prev = ot[:i][~np.isnan(ot[:i])]
            ot[i] = prev[-1] if len(prev) else np.nan
    orate = np.where(np.isfinite(ot) & (ot > 0), on / ot, np.nan)

    def cum(edges, rates):
        return edges[:-1], np.cumsum(rates[::-1])[::-1]

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for A, (conv, ylab) in zip(ax, [(lambda e, r: (e[:-1], r),
                                     "incremental rate (/yr)"),
                                    (cum, "cumulative rate N(>=M) (/yr)")]):
        for e, r, lab, st in [
                (edges, r_pre, "background pre-cap", dict(color=".55", ls="--")),
                (edges, r_post, "background capped", dict(color="steelblue")),
                (e_tot, r_tot, "capped + faults", dict(color="darkorange", lw=2))]:
            x, y = conv(np.asarray(e), np.asarray(r))
            m = y > 0
            if m.any():
                A.step(x[m], y[m], where="post", label=lab, **st)
        # observed: incremental as points; cumulative from completeness rates
        if conv is cum:
            oc = np.nancumsum(orate[::-1])[::-1]
            m = np.isfinite(oc) & (oc > 0)
            A.plot(oe[:-1][m], oc[m], "k.", ms=6, label="catalog (Weichert periods)")
            gr = wch["rate_mmin"] * 10 ** (-wch["b"] * (oe[:-1] - cfg.mc_min))
            A.plot(oe[:-1], gr, color="seagreen", lw=1,
                   label=f"GR fit b={wch['b']:.2f}")
        else:
            m = np.isfinite(orate) & (orate > 0)
            A.plot(oe[:-1][m] + cfg.dm / 2, orate[m], "k.", ms=6,
                   label="catalog (Weichert periods)")
        A.axvline(cfg.cap_mag, color="k", lw=0.8, ls=":")
        A.set_yscale("log")
        A.set_xlabel("M")
        A.set_ylabel(ylab)
        A.grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    fig.suptitle(f"{cfg.domain_name}: {int(cmask.sum())} cells, "
                 f"{len(fdom)} fault sources, {len(sel)} events M>={cfg.mc_min}")
    fig.tight_layout()
    png = cfg.out_dir / f"domain_mfd_{cfg.domain_name}.png"
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[check_domain] wrote {png}")

    # 3) domain count consistency at M >= cap_mag
    n_fault = sum(float(f["rates"].sum()) for f in fdom)
    obs6 = float(np.nansum(np.where(oe[:-1] >= cfg.cap_mag - 1e-9,
                                    orate, 0.0)))
    print(f"[check_domain] N(M>={cfg.cap_mag}): faults {n_fault:.4f} /yr, "
          f"catalog {obs6:.4f} /yr (completeness-corrected), "
          f"background pre-cap {r_pre[edges[:-1] >= cfg.cap_mag - 1e-9].sum():.4f} /yr")
    if obs6 > 0:
        print(f"[check_domain] fault/catalog = {n_fault / obs6:.2f}")
    return wch, fb


def _default_domain_catalog(cfg: DomainConfig) -> Path:
    from cat_no_mech_handler import paths as cat_paths
    return {"intraarc": cat_paths.cat_intraarc_dc,
            "forearc": cat_paths.cat_forearc_dc}[cfg.domain_name]


if __name__ == "__main__":
    check_domain(DomainConfig(domain_name="intraarc",
                              domain_shp=Path("../data/shapefiles/intra_arc.shp")))