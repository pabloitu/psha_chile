# checks/check_domain_mfd.py
# Zone MFD check. For each zone polygon in DOMAIN_SHPS, everything is
# restricted to the polygon:
#   - observed catalog rates: all class catalogs clipped to the zone, each
#     event weighted 1/T(M) from ITS OWN class completeness table
#   - background uncapped:   total SSM grid (s01), cells inside the zone
#   - background capped:     s03 grid, cells inside the zone
#   - faults:                fault sources with trace midpoint inside the zone
#   - merged model:          capped background + faults
# One figure per zone: merger_checks/zone_mfd_<zone>.png
#
# Run from ssm_3/ after s01 (+ s02/s03 and the fault XML for the full set):
#   python -m checks.check_domain_mfd

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shapely

import ssm_config as C
from ssm_lib import load_catalog, completeness_steps, obs_periods
from s02_fault_buffers import cell_mask
from check_fault_ssm_merger import read_fault_mfds, fault_bin_edges

# zone polygons; a zone may span several classes (the curves are zone sums)
DOMAIN_SHPS = {
    "intraarc": Path("../data/shapefiles/intra_arc.shp"),
    # "forearc": Path("../data/shapefiles/forearc.shp"),
    # "backarc": Path("../data/shapefiles/backarc.shp"),
}
FAULT_XML = Path("../fault_model/crustal_faults_phi100_mgeo_tgr.xml")


def load_zone(shp: Path):
    import geopandas as gpd
    from shapely.ops import unary_union
    g = gpd.read_file(shp)
    if g.crs is not None:
        g = g.to_crs("EPSG:4326")
    z = unary_union(g.geometry)
    shapely.prepare(z)
    return z


def zone_catalog_rates(zone, dm: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Observed incremental rates in the zone: every class catalog is clipped to
    the polygon and each event contributes 1/T(M) from its own class's
    completeness steps (classes are complete over different periods, so a
    single zone-wide T would be wrong).
    """
    pairs = []
    for name, spec in C.CLASSES.items():
        cat = load_catalog(spec["catalog"], bbox=C.BBOX,
                           region=spec.get("region"))
        inside = cell_mask(cat["longitude"].to_numpy(),
                           cat["latitude"].to_numpy(), zone)
        cat = cat[inside]
        if len(cat) == 0:
            continue
        steps = completeness_steps(C.COMPLETENESS[name], C.PRESENT_YEAR)
        mags = cat["mag"].to_numpy(float)
        per = obs_periods(mags, steps)
        good = np.isfinite(per) & (per > 0)
        pairs.append((mags[good], per[good]))
        print(f"[zone_catalog_rates] {name}: {int(inside.sum())} events in "
              f"zone, {int(good.sum())} within completeness")
    if not pairs:
        return np.array([]), np.array([])
    mags = np.concatenate([p[0] for p in pairs])
    per = np.concatenate([p[1] for p in pairs])
    lo = np.floor(mags.min() / dm) * dm
    edges = np.round(np.arange(lo, mags.max() + dm, dm), 6)
    rate = np.zeros(len(edges) - 1)
    for i, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
        m = (mags >= a) & (mags < b)
        if m.any():
            rate[i] = (1.0 / per[m]).sum()
    return edges, rate


def grid_in_zone(csv: Path, zone) -> tuple[np.ndarray, np.ndarray]:
    """Total grid rates summed over the cells inside the zone."""
    df = pd.read_csv(csv)
    inside = cell_mask(df["lon"].to_numpy(), df["lat"].to_numpy(), zone)
    cols = [c for c in df.columns if c.startswith("rate_M")]
    los = [float(c[6:].split("_")[0]) for c in cols]
    his = [float(c[6:].split("_")[1]) for c in cols]
    order = np.argsort(los)
    edges = np.array([los[i] for i in order] + [max(his)])
    rates = df.loc[inside, cols].to_numpy().sum(axis=0)[order]
    return edges, rates


def zone_fault_rates(zone, edges: np.ndarray) -> np.ndarray:
    out = np.zeros(len(edges) - 1)
    if not FAULT_XML.exists():
        print(f"[zone_fault_rates] {FAULT_XML.resolve()} not found; "
              "skipping faults")
        return out
    faults = [f for f in read_fault_mfds(FAULT_XML)
              if zone.contains(shapely.Point(f["lon"], f["lat"]))]
    print(f"[zone_fault_rates] {len(faults)} fault sources inside zone")
    dm = edges[1] - edges[0]
    for f in faults:
        fe = fault_bin_edges(f)
        for k, r in enumerate(f["rates"]):
            i = int(round((fe[k] - edges[0]) / dm))
            if 0 <= i < len(out):
                out[i] += r
    return out


def cum(edges, rates):
    return edges[:-1], np.cumsum(rates[::-1])[::-1]


def plot_zone(zname: str, shp: Path):
    print(f"\n===== zone: {zname} =====")
    if not shp.exists():
        print(f"[plot_zone] shapefile not found: {shp.resolve()} -> skipped")
        return
    zone = load_zone(shp)

    oe, orate = zone_catalog_rates(zone, C.DM)
    e_bg, r_bg = grid_in_zone(C.SSM_GRID, zone)
    if C.SSM_GRID_CAPPED.exists():
        _, r_cap = grid_in_zone(C.SSM_GRID_CAPPED, zone)
    else:
        print(f"[plot_zone] {C.SSM_GRID_CAPPED} not found (run s03); "
              "capped/merged curves unavailable")
        r_cap = np.zeros_like(r_bg)
    r_f = zone_fault_rates(zone, e_bg)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for A, mode in zip(ax, ("inc", "cum")):
        conv = (lambda e, r: (e[:-1], r)) if mode == "inc" else cum
        series = [(r_bg, "background uncapped", dict(color="steelblue", lw=1.5)),
                  (r_cap, "background capped", dict(color=".55", ls="--", lw=1.2)),
                  (r_f, "faults in zone", dict(color="firebrick", lw=1.2)),
                  (r_cap + r_f, "merged: capped bg + faults",
                   dict(color="darkorange", lw=2))]
        for r, lab, st in series:
            if not np.any(r > 0):
                continue
            x, y = conv(e_bg, np.asarray(r))
            m = y > 0
            A.step(x[m], y[m], where="post", label=lab, **st)
        if len(oe):
            x, y = conv(oe, orate)
            m = y > 0
            A.plot(x[m] + (C.DM / 2 if mode == "inc" else 0), y[m], "k.",
                   ms=6, label="catalog in zone (completeness periods)")
        A.axvline(C.CAP_MAG, color="k", lw=0.8, ls=":")
        A.set_yscale("log")
        A.set_xlabel("M")
        A.set_ylabel("incremental rate (/yr)" if mode == "inc"
                     else "cumulative N(>=M) (/yr)")
        A.grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    fig.suptitle(f"zone {zname}: catalog vs background vs faults vs merged")
    fig.tight_layout()
    png = C.OUT / "merger_checks" / f"zone_mfd_{zname}.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[plot_zone] wrote {png}")

    i6 = e_bg[:-1] >= C.CAP_MAG - 1e-9
    o6 = float(np.nansum(np.where(oe[:-1] >= C.CAP_MAG - 1e-9, orate, 0.0))) \
        if len(oe) else np.nan
    print(f"[{zname}] N(M>={C.CAP_MAG}) /yr: bg={r_bg[i6].sum():.4f}, "
          f"capped={r_cap[i6].sum():.4f}, faults={r_f[i6].sum():.4f}, "
          f"merged={(r_cap + r_f)[i6].sum():.4f}, catalog={o6:.4f}")


def main():
    for zname, shp in DOMAIN_SHPS.items():
        plot_zone(zname, shp)


if __name__ == "__main__":
    main()