# s01_build_ssm.py
# Crustal smoothed-seismicity model (SSM) by per-class superposition.
#
# Each tectonic class is smoothed from its OWN declustered catalog and scaled
# by its OWN Weichert (a, b) and Mmax; the total SSM is the per-bin sum of the
# class fields. Domain membership is a property of the events, not of the
# cells, so the total field is continuous across class boundaries (no seams).
#
# Completeness: rates and b come from the per-event (mc_window, tc_years)
# stamps produced by the catalog pipeline; Weichert (1980) handles the
# unequal observation periods, so the incomplete early decades do not bias
# the fit as long as the stamped windows are right for the class. The
# completeness audit printed per class is there to check that assumption.

from __future__ import annotations

import numpy as np
import pandas as pd

import ssm_config as C
from ssm_lib import (load_catalog, completeness_steps, obs_periods, weichert,
                     completeness_audit, usable_windows, event_weights,
                     adaptive_kernel, smooth_field, mag_edges, tgr_bins,
                     write_mfd_grid, write_raster, safe_log10, plot_class_fit,
                     plot_total_mfd, plot_rate_map)


def fit_class(name: str, cat: pd.DataFrame) -> dict:
    """
    Weichert (a, b) for one class catalog.

    Prints the completeness audit, then keeps only the windows the class can
    support (C.MIN_EVENTS_PER_WINDOW). b_err is bootstrapped, so a class that
    leans on sparse historical windows shows a large error here rather than an
    optimistic b/sqrt(N).
    """
    steps = completeness_steps(C.COMPLETENESS[name], C.PRESENT_YEAR)
    completeness_audit(cat, steps, name)
    use = usable_windows(cat, steps, C.MC_MIN_FIT, C.MIN_EVENTS_PER_WINDOW, name)
    if len(use) == 0:
        raise ValueError(f"[fit_class] {name}: no usable completeness window; "
                         "pool it with another class via B_SOURCE and set "
                         "its rate from a coarser window")
    sel = cat[cat["mag"] >= C.MC_MIN_FIT]
    per = obs_periods(sel["mag"].to_numpy(), use)
    good = np.isfinite(per)
    wch = weichert(sel.loc[good, "mag"].to_numpy(), per[good],
                   mmin=C.MC_MIN_FIT, dm=C.DM)
    wch["mags_fit"] = sel.loc[good, "mag"].to_numpy()
    wch["per_fit"] = per[good]
    wch["n_win_used"] = len(use)
    print(f"[fit_class] {name}: N={wch['N']} in {len(use)} window(s), "
          f"b={wch['b']:.3f}+/-{wch['b_err']:.3f} (bootstrap), "
          f"rate(M>={wch['mmin']:.2f})={wch['rate_mmin']:.4f}/yr")
    if wch["b_err"] > C.B_ERR_WARN:
        print(f"[fit_class] WARNING: {name} b_err={wch['b_err']:.3f} > "
              f"{C.B_ERR_WARN}; consider borrowing/pooling b via B_SOURCE")
    return wch


def build_class(name: str, cat: pd.DataFrame, wch: dict, b_use: float,
                grid: pd.DataFrame, edges: np.ndarray,
                b_from_name: str = "") -> tuple[np.ndarray, dict]:
    """
    Smoothed field for one class, scaled to its truncated-GR rates.

    b_use may differ from wch['b'] when the class borrows a b (C.B_SOURCE);
    the activity rate is always re-anchored with b_use so that the observed
    N(M >= MC_MIN_FIT) is preserved.
    """
    # anchor at the fit's effective mmin (first complete magnitude), which for
    # some classes sits above MC_MIN_FIT
    rate_fc = wch["rate_mmin"] * 10.0 ** (b_use * (wch["mmin"] - C.MMIN_FORECAST))
    mmax = C.MMAX_OVERRIDE.get(name, float(cat["mag"].max()) + C.MMAX_PAD)

    steps = completeness_steps(C.COMPLETENESS[name], C.PRESENT_YEAR)
    w = event_weights(cat, steps, b=(C.B_COMPLETENESS or b_use),
                      mc_min=C.MC_MIN_FIT)
    kern = adaptive_kernel(cat, C.N_NEIGHBORS, C.MIN_KERNEL_KM)
    shape = smooth_field(cat, grid, w, kern, C.KERNEL_POWER,
                         C.MAX_EVENT_GRID_DIST_KM)
    if shape.sum() <= 0:
        raise ValueError(f"[build_class] empty field for class {name}")

    rb = tgr_bins(shape, rate_fc, b_use, edges, mmax)

    # rate check: the binned field must total the truncated-GR expectation
    exp = rate_fc * (1 - 10.0 ** (-b_use * (mmax - C.MMIN_FORECAST)))
    assert abs(rb.sum() - exp) / exp < 1e-9, (rb.sum(), exp)
    print(f"[build_class] {name}: b_used={b_use:.3f} "
          f"N(M>={C.MMIN_FORECAST})={rate_fc:.4f}/yr Mmax={mmax:.2f} "
          f"kernel_med={np.median(kern):.0f} km  rate check OK")

    info = {"class": name, "n_events": len(cat), "n_fit": wch["N"],
            "n_windows_used": wch.get("n_win_used", np.nan),
            "b_fit": wch["b"], "b_err": wch["b_err"], "b_used": b_use,
            "b_borrowed_from": b_from_name,
            "rate_mcfit": wch["rate_mmin"], "rate_forecast": rate_fc,
            "mmax": mmax, "kernel_med_km": float(np.median(kern))}
    return rb, info


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)

    # 1) grid, restricted to the model bbox
    grid = pd.read_csv(C.GRID_CSV)
    lo, hi, la, ha = C.BBOX
    grid = grid[(grid["lon"] >= lo) & (grid["lon"] <= hi)
                & (grid["lat"] >= la) & (grid["lat"] <= ha)].reset_index(drop=True)
    print(f"[main] grid: {len(grid)} cells inside bbox")

    # 2) load every class catalog once (declustered mainshocks, bbox, region)
    cats = {n: load_catalog(s["catalog"], bbox=C.BBOX, region=s.get("region"))
            for n, s in C.CLASSES.items()}

    # 3) fit (a, b) per class BEFORE building fields, so that a class can
    #    borrow another class's b (C.B_SOURCE) for its MFD shape
    fits = {n: fit_class(n, c) for n, c in cats.items()}
    b_used, b_from = {}, {}
    for n in cats:
        src = C.B_SOURCE.get(n)
        if src is None:
            b_used[n], b_from[n] = fits[n]["b"], ""
            continue
        donors = [src] if isinstance(src, str) else list(src)
        if len(donors) == 1:
            b_used[n] = fits[donors[0]]["b"]
        else:
            # pooled fit: b from the donors' catalogs together (rate stays local)
            pooled = pd.concat([cats[d] for d in donors], ignore_index=True)
            b_used[n] = fit_class("+".join(donors), pooled)["b"]
        b_from[n] = "+".join(donors)
        print(f"[main] {n}: using b={b_used[n]:.3f} from {b_from[n]} "
              f"(own fit {fits[n]['b']:.3f}+/-{fits[n]['b_err']:.3f}); "
              "rate stays local")

    # 4) shared magnitude bins from MMIN_FORECAST to the largest class Mmax,
    #    so all class fields can be summed bin by bin
    mmax_all = [C.MMAX_OVERRIDE.get(n, float(c["mag"].max()) + C.MMAX_PAD)
                for n, c in cats.items()]
    edges = mag_edges(C.MMIN_FORECAST, max(mmax_all), C.DM)
    print(f"[main] shared bins {edges[0]:.2f}-{edges[-1]:.2f} "
          f"({len(edges) - 1} bins of {C.DM})")

    # 5) per-class smoothing + truncated GR; write grid, map, raster each
    per_class, infos, total = {}, [], None
    for n, cat in cats.items():
        print(f"\n===== class: {n} =====")
        rb, info = build_class(n, cat, fits[n], b_used[n], grid, edges,
                               b_from[n])
        per_class[n], total = rb, (rb.copy() if total is None else total + rb)
        infos.append(info)
        plot_class_fit(fits[n], fits[n]["mags_fit"], fits[n]["per_fit"], C.DM,
                       f"{n}: Weichert fit", C.FIG / f"fit_{n}.png")
        write_mfd_grid(grid, rb, edges, C.OUT / f"ssm_mfd_grid_{n}.csv")
        plot_rate_map(grid, rb.sum(axis=1), f"{n}: N(M>={C.MMIN_FORECAST}) /yr",
                      C.FIG / f"map_{n}.png")
        write_raster(grid, safe_log10(rb.sum(axis=1)),
                     C.OUT / f"ssm_log10_rate_{n}.tif")

    # 6) superposition -> total SSM (this file feeds s03/s04)
    assert np.allclose(total, sum(per_class.values())), "superposition mismatch"
    write_mfd_grid(grid, total, edges, C.SSM_GRID)
    plot_rate_map(grid, total.sum(axis=1),
                  f"total: N(M>={C.MMIN_FORECAST}) /yr", C.FIG / "map_total.png")
    write_raster(grid, safe_log10(total.sum(axis=1)),
                 C.OUT / "ssm_log10_rate_total.tif")
    plot_total_mfd(per_class, edges, C.FIG / "mfd_superposition.png")

    # 7) summary table: what every class contributed
    summ = pd.DataFrame(infos)
    summ["frac_of_total"] = summ["rate_forecast"] / summ["rate_forecast"].sum()
    summ.to_csv(C.OUT / "ssm_class_summary.csv", index=False)
    print("\n[main] class summary:")
    print(summ.to_string(index=False))
    print(f"[main] total N(M>={C.MMIN_FORECAST}) = "
          f"{summ['rate_forecast'].sum():.4f} /yr; grid total (to Mmax) = "
          f"{total.sum():.4f} /yr")
    print(f"[main] SSM grid -> {C.SSM_GRID.resolve()}")


if __name__ == "__main__":
    main()
