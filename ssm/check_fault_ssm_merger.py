# check_fault_ssm_merger.py
# Diagnostics for the fault-model / smoothed-seismicity merger (Mmax cap
# inside fault buffers). Checks, in order:
#   1. rate conservation outside buffers (regression test)
#   2. MFD handoff continuity at the cap magnitude, per region and national
#   3. moment closure per buffer region (removed background vs fault budget)
#   4. event attribution audit (which component claims each M>=5.5 event)
#   5. map of background rate removed by the cap
#   6. count consistency: expected fault N(M>=6) vs observed catalog counts
# Moment convention: log10 M0 = 1.5 M + 9.1, evaluated at bin LOWER EDGES
# (matches bin_moment() in create_model.py).

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely
from shapely.geometry import Point
from shapely.ops import unary_union

from fault_buffers import load_union, cell_mask
from cap_ssm_mmax import bin_cols


@dataclass
class CheckConfig:
    ssm_pre_csv: Path = Path("ssm_crustal_outputs/ssm_mfd_grid.csv")
    ssm_post_csv: Path = Path("ssm_crustal_outputs/ssm_mfd_grid_capped.csv")
    union_geojson: Path = Path("fault_buffers_union.geojson")
    fault_xml: Path = Path("../fault_model/crustal_faults_phi100_mgeo_tgr.xml")
    # catalogs feeding the crustal SSM (ssm_crustal.py: forearc + intraarc,
    # mainshocks only, bbox-filtered); if empty, resolved from
    # cat_no_mech_handler.paths at run time
    catalog_csvs: tuple = ()
    bbox: tuple = (-80.0, -60.0, -60.0, -17.0)  # lon_min, lon_max, lat_min, lat_max
    cap_mag: float = 6.0
    completeness_year: int = 1950
    audit_min_mag: float = 5.5
    out_dir: Path = Path("merger_checks")


def load_crustal_catalog(cfg: CheckConfig) -> pd.DataFrame:
    """
    Same catalog combination that feeds the crustal SSM (ssm_crustal.py):
    forearc + intraarc declustered classes, mainshocks only, bbox-filtered.
    """
    paths = list(cfg.catalog_csvs)
    if not paths:
        from cat_no_mech_handler import paths as cat_paths
        paths = [cat_paths.cat_forearc_dc, cat_paths.cat_intraarc_dc]

    dfs = []
    for p in paths:
        df = pd.read_csv(p)
        if "is_mainshock" in df.columns:
            df = df[df["is_mainshock"] == True]
        dfs.append(df)
        print(f"[load_crustal_catalog] {p}: {len(df)} mainshocks")
    cat = pd.concat(dfs, ignore_index=True)

    lon_min, lon_max, lat_min, lat_max = cfg.bbox
    cat = cat[(cat["longitude"] >= lon_min) & (cat["longitude"] <= lon_max)
              & (cat["latitude"] >= lat_min) & (cat["latitude"] <= lat_max)]
    print(f"[load_crustal_catalog] combined: {len(cat)} events after bbox")
    return cat.reset_index(drop=True)


def m0(mag) -> np.ndarray:
    return 10.0 ** (1.5 * np.asarray(mag, float) + 9.1)


# fault NRML parsing

def strip(tag: str) -> str:
    return tag.split("}")[-1]


def read_fault_mfds(xml_path: Path) -> list[dict]:
    """
    Parse simple-fault sources with incremental MFDs from an NRML file.

    Returns
    -------
    list of dict
        Per source: id, name, min_mag (bin center), dm, rates, and the trace
        midpoint (lon, lat) used to assign the fault to a buffer region.
    """
    root = ET.parse(xml_path).getroot()
    out = []
    for src in root.iter():
        if strip(src.tag) != "simpleFaultSource":
            continue
        mfd = trace = None
        for el in src.iter():
            t = strip(el.tag)
            if t == "incrementalMFD":
                rates = [float(x) for x in
                         el.find("./{*}occurRates").text.split()]
                mfd = (float(el.get("minMag")), float(el.get("binWidth")), rates)
            elif t == "posList":
                v = [float(x) for x in el.text.split()]
                trace = np.array(v).reshape(-1, 2)
        if mfd is None or trace is None:
            continue
        mid = trace[len(trace) // 2]
        out.append({"id": src.get("id"), "name": src.get("name"),
                    "min_mag": mfd[0], "dm": mfd[1],
                    "rates": np.array(mfd[2]), "lon": mid[0], "lat": mid[1]})
    print(f"[read_fault_mfds] {len(out)} fault sources from {xml_path}")
    return out


def fault_bin_edges(f: dict) -> np.ndarray:
    lo = f["min_mag"] - f["dm"] / 2.0
    return lo + f["dm"] * np.arange(len(f["rates"]) + 1)


# regions = connected components of the buffer union

def union_regions(union) -> list:
    geoms = list(union.geoms) if hasattr(union, "geoms") else [union]
    return sorted(geoms, key=lambda g: -g.area)


def assign_faults_to_regions(faults: list[dict], regions: list) -> np.ndarray:
    idx = np.full(len(faults), -1, dtype=int)
    for i, f in enumerate(faults):
        p = Point(f["lon"], f["lat"])
        for j, r in enumerate(regions):
            if r.contains(p):
                idx[i] = j
                break
        if idx[i] < 0:
            idx[i] = int(np.argmin([r.distance(p) for r in regions]))
    return idx


# checks

def check_outside_unchanged(pre: pd.DataFrame, post: pd.DataFrame) -> bool:
    """Rates outside the buffers must be bit-identical pre/post cap."""
    cols = [c for c, _, _ in bin_cols(pre)]
    outside = ~post["in_fault_buffer"].to_numpy()
    a = pre.loc[outside, cols].to_numpy()
    b = post.loc[outside, cols].to_numpy()
    d = np.abs(a - b).max() if outside.any() else 0.0
    scale = max(np.abs(a).max(), 1e-300)
    ok = d / scale < 1e-12
    print(f"[check_outside] max |diff| outside buffers = {d:.3e} "
          f"(rel {d / scale:.1e}) -> {'PASS' if ok else 'FAIL'}")
    return ok


def total_mfd(df: pd.DataFrame, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cols = bin_cols(df)
    edges = np.array([lo for _, lo, _ in cols] + [cols[-1][2]])
    rates = df.loc[mask, [c for c, _, _ in cols]].to_numpy().sum(axis=0)
    return edges, rates


def add_fault_rates(edges: np.ndarray, base: np.ndarray,
                    faults: list[dict]) -> np.ndarray:
    """Accumulate fault incremental rates onto the background bin edges."""
    lo_all, hi_all = edges[0], edges[-1]
    dm = edges[1] - edges[0]
    n = len(base)
    out = base.copy()
    extra_lo, extra_rates = [], []
    for f in faults:
        fe = fault_bin_edges(f)
        for k, r in enumerate(f["rates"]):
            b_lo = fe[k]
            if b_lo >= hi_all - 1e-9:
                extra_lo.append(b_lo)
                extra_rates.append(r)
                continue
            i = int(round((b_lo - lo_all) / dm))
            if 0 <= i < n:
                out[i] += r
    if extra_lo:
        order = np.argsort(extra_lo)
        n_extra = int(round((max(extra_lo) + dm - hi_all) / dm))
        ext = np.zeros(n_extra)
        for b_lo, r in zip(np.array(extra_lo)[order], np.array(extra_rates)[order]):
            ext[int(round((b_lo - hi_all) / dm))] += r
        out = np.concatenate([out, ext])
        edges = np.concatenate([edges, hi_all + dm * (1 + np.arange(n_extra))])
    return edges, out


def plot_handoff(pre: pd.DataFrame, post: pd.DataFrame, faults: list[dict],
                 mask: np.ndarray, cap_mag: float, title: str, png: Path):
    e_pre, r_pre = total_mfd(pre, mask)
    e_post, r_post = total_mfd(post, mask)
    e_tot, r_tot = add_fault_rates(e_post.copy(), r_post, faults)

    if r_pre.sum() <= 0 and r_tot.sum() <= 0:
        print(f"[plot_handoff] SKIP '{title}': {int(mask.sum())} cells, "
              f"{len(faults)} faults, no positive rates "
              "(buffer outside SSM grid coverage?)")
        return

    def cum(edges, rates):
        return edges[:-1], np.cumsum(rates[::-1])[::-1]

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for a, (conv, ylab) in zip(ax, [(lambda e, r: (e[:-1], r), "incremental rate (/yr)"),
                                    (cum, "cumulative rate N(>=M) (/yr)")]):
        for edges, rates, lab, st in [
                (e_pre, r_pre, "background pre-cap", dict(color=".55", ls="--")),
                (e_post, r_post, "background capped", dict(color="steelblue")),
                (e_tot[:len(r_tot) + 1] if len(e_tot) > len(r_tot) else e_tot,
                 r_tot, "capped + faults", dict(color="darkorange", lw=2))]:
            x, y = conv(np.asarray(edges), np.asarray(rates))
            m = y > 0
            if m.any():
                a.step(x[m], y[m], where="post", label=lab, **st)
        a.axvline(cap_mag, color="k", lw=0.8, ls=":")
        a.set_yscale("log")
        a.set_xlabel("M")
        a.set_ylabel(ylab)
        a.grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[plot_handoff] wrote {png}")


def moment_closure(pre: pd.DataFrame, post: pd.DataFrame, faults: list[dict],
                   regions: list, f_region: np.ndarray,
                   out_csv: Path) -> pd.DataFrame:
    """
    Per buffer region: background moment rate removed by the cap vs the moment
    rate carried by the fault MFDs assigned to that region (M0 at bin lower
    edges, project convention).
    """
    cols = bin_cols(pre)
    names = [c for c, _, _ in cols]
    lo_edges = np.array([lo for _, lo, _ in cols])
    lons, lats = pre["lon"].to_numpy(), pre["lat"].to_numpy()

    rows = []
    for j, reg in enumerate(regions):
        shapely.prepare(reg)
        inreg = shapely.contains_xy(reg, lons, lats)
        dr = (pre.loc[inreg, names].to_numpy()
              - post.loc[inreg, names].to_numpy()).sum(axis=0)
        mo_removed = float((dr * m0(lo_edges)).sum())
        n_removed = float(dr.sum())

        fj = [f for f, r in zip(faults, f_region) if r == j]
        mo_fault = sum(float((f["rates"] * m0(fault_bin_edges(f)[:-1])).sum())
                       for f in fj)
        n_fault = sum(float(f["rates"].sum()) for f in fj)

        rows.append({
            "region": j, "n_faults": len(fj),
            "names": "; ".join(str(f["name"]) for f in fj)[:80],
            "N_removed_bg": n_removed, "N_fault": n_fault,
            "Mo_removed_bg": mo_removed, "Mo_fault": mo_fault,
            "Mo_fault/Mo_removed": mo_fault / mo_removed if mo_removed > 0 else np.inf,
            "N_fault/N_removed": n_fault / n_removed if n_removed > 0 else np.inf,
        })
    df = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"[moment_closure] wrote {out_csv}")
    low = df[(df["Mo_fault/Mo_removed"] < 1.0) & (df["Mo_removed_bg"] > 0)]
    if len(low):
        print(f"[moment_closure] WARNING: {len(low)} regions where the fault "
              "budget does not cover the removed background moment:")
        print(low[["region", "names", "Mo_fault/Mo_removed"]].to_string(index=False))
    return df


def audit_events(cat: pd.DataFrame, union, cap_mag: float, min_mag: float,
                 out_csv: Path) -> pd.DataFrame:
    """
    For each declustered crustal event with mag >= min_mag: is it inside a
    buffer, and which component of the merged model now claims its magnitude?
    """
    cat = cat[cat["mag"] >= min_mag].copy()
    inside = cell_mask(cat["longitude"].to_numpy(), cat["latitude"].to_numpy(), union)
    cat["in_fault_buffer"] = inside
    cat["claimed_by"] = np.where(
        cat["mag"] >= cap_mag,
        np.where(inside, "faults", "background"),
        "background")
    flags = []
    for _, r in cat.iterrows():
        t = str(r.get("time_iso", ""))
        f = ""
        if t.startswith("2010-03-11"):
            f = "PICHILEMU?"
        elif t.startswith("2007-04-21"):
            f = "AYSEN?"
        flags.append(f)
    cat["flag"] = flags

    keep = [c for c in ["time_iso", "mag", "longitude", "latitude", "depth",
                        "in_fault_buffer", "claimed_by", "flag"] if c in cat.columns]
    out = cat[keep].sort_values("mag", ascending=False)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)
    n_in = int(inside.sum())
    print(f"[audit_events] {len(out)} events M>={min_mag}; {n_in} inside buffers")
    named = out[out["flag"] != ""]
    if len(named):
        print(named.to_string(index=False))
    return out


def removed_rate_map(pre: pd.DataFrame, post: pd.DataFrame, union,
                     cap_mag: float, png: Path):
    cols = [c for c, lo, _ in bin_cols(pre) if lo >= cap_mag - 1e-6]
    removed = (pre[cols].to_numpy() - post[cols].to_numpy()).sum(axis=1)
    fig, ax = plt.subplots(figsize=(6, 10))
    m = removed > 0
    ax.scatter(pre.loc[~m, "lon"], pre.loc[~m, "lat"], s=2, c=".85")
    sc = ax.scatter(pre.loc[m, "lon"], pre.loc[m, "lat"], s=6,
                    c=np.log10(removed[m]), cmap="magma_r")
    plt.colorbar(sc, ax=ax, label=f"log10 N(M>={cap_mag}) removed (/yr/cell)")
    gpd.GeoSeries([union], crs="EPSG:4326").boundary.plot(
        ax=ax, color="steelblue", lw=0.5)
    ax.set_aspect("equal")
    ax.set_title(f"Background rate removed by Mmax cap "
                 f"(total {removed.sum():.4f} /yr)")
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[removed_rate_map] wrote {png}")


def count_consistency(faults: list[dict], regions: list, f_region: np.ndarray,
                      cat: pd.DataFrame, union, cap_mag: float,
                      completeness_year: int) -> pd.DataFrame:
    """
    N-test-like check: expected annual fault-model count of M>=cap_mag inside
    the buffers vs observed catalog count over the completeness window.
    """
    cat = cat.copy()
    cat["year"] = pd.to_datetime(cat["time_iso"], utc=True,
                                 errors="coerce").dt.year
    cat = cat[(cat["mag"] >= cap_mag) & (cat["year"] >= completeness_year)]
    inside = cell_mask(cat["longitude"].to_numpy(), cat["latitude"].to_numpy(), union)
    n_obs = int(inside.sum())
    years = pd.Timestamp.now().year - completeness_year

    n_exp_yr = sum(float(f["rates"].sum()) for f in faults)
    n_exp = n_exp_yr * years
    p_ge = 1.0 - sum(np.exp(-n_exp) * n_exp ** k / math.factorial(k)
                     for k in range(n_obs)) if n_exp < 500 else np.nan

    print(f"[count_consistency] fault model: {n_exp_yr:.4f} /yr M>={cap_mag} "
          f"-> {n_exp:.2f} expected in {years} yr; observed inside buffers: {n_obs}")
    if not np.isnan(p_ge):
        print(f"[count_consistency] Poisson P(N >= {n_obs}) = {p_ge:.3f}")
    return pd.DataFrame([{"expected_per_yr": n_exp_yr, "years": years,
                          "expected": n_exp, "observed": n_obs,
                          "p_ge_obs": p_ge}])


def run_all(cfg: CheckConfig | None = None):
    cfg = cfg or CheckConfig()
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    pre = pd.read_csv(cfg.ssm_pre_csv)
    post = pd.read_csv(cfg.ssm_post_csv)
    union = load_union(cfg.union_geojson)
    faults = read_fault_mfds(cfg.fault_xml)
    regions = union_regions(union)
    f_region = assign_faults_to_regions(faults, regions)

    check_outside_unchanged(pre, post)

    inside = post["in_fault_buffer"].to_numpy(bool)
    plot_handoff(pre, post, faults, inside, cfg.cap_mag,
                 "All buffer regions", cfg.out_dir / "handoff_national.png")

    # region summary; plot the strongest regions by removed rate
    cols = bin_cols(pre)
    names = [c for c, _, _ in cols]
    cap_cols = [c for c, lo, _ in cols if lo >= cfg.cap_mag - 1e-6]
    lons, lats = pre["lon"].to_numpy(), pre["lat"].to_numpy()
    summary, masks = [], []
    for j, reg in enumerate(regions):
        shapely.prepare(reg)
        mask = shapely.contains_xy(reg, lons, lats)
        masks.append(mask)
        n_f = int((f_region == j).sum())
        removed = float((pre.loc[mask, cap_cols].to_numpy()
                         - post.loc[mask, cap_cols].to_numpy()).sum())
        summary.append({"region": j, "n_cells": int(mask.sum()),
                        "n_faults": n_f, "removed_N": removed})
    summ = pd.DataFrame(summary)
    summ.to_csv(cfg.out_dir / "region_summary.csv", index=False)
    empty = summ[(summ["n_cells"] == 0)]
    if len(empty):
        print(f"[run_all] NOTE: {len(empty)} buffer regions contain no SSM "
              "cells (fault buffers without background coverage): regions "
              f"{empty['region'].tolist()}")

    for j in summ.sort_values("removed_N", ascending=False)["region"][:8]:
        fj = [f for f, r in zip(faults, f_region) if r == j]
        plot_handoff(pre, post, fj, masks[j], cfg.cap_mag,
                     f"Region {j} ({summ.at[j, 'n_cells']} cells, {len(fj)} faults)",
                     cfg.out_dir / f"handoff_region{j:02d}.png")

    moment_closure(pre, post, faults, regions, f_region,
                   cfg.out_dir / "moment_closure.csv")
    cat = load_crustal_catalog(cfg)
    audit_events(cat, union, cfg.cap_mag, cfg.audit_min_mag,
                 cfg.out_dir / "event_audit.csv")
    removed_rate_map(pre, post, union, cfg.cap_mag,
                     cfg.out_dir / "removed_rate_map.png")
    count_consistency(faults, regions, f_region, cat, union,
                      cfg.cap_mag, cfg.completeness_year)
    print(f"[run_all] outputs in {cfg.out_dir.resolve()}")


if __name__ == "__main__":
    run_all()