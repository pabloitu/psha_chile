# cat_no_mech_handler/plot_sections.py
# Trench-perpendicular cross-sections of the classified catalog, with the
# Slab2 top and the plate bottom (top + local thk) overlaid. The plate
# bottom IS the classification boundary: events below it are deep_unknown,
# events inside it are intra_slab or slab_deep depending on the slab-top
# depth at their position (SUBDUCTION_CLASSIFY_MAX_SLAB_DEPTH).
#
# Slab2 'dep' is the TOP surface (verified: shallowest nodes sit at 5-10 km
# at the trench = seafloor depth; a mid-slab surface would be at seafloor +
# thk/2 ~ 42 km). 'thk' is full lithospheric thickness, median 72 km,
# varying 86 km in the north to 61 km in the south with plate age.
#
# Distance is measured along the convergence azimuth (CONV_AZIMUTH_DEG),
# positive landward from an arbitrary offshore origin, so a "profile" is a
# latitude band collapsed onto one section. Slab dip varies with latitude,
# so bands are kept narrow and plotted separately.
#
# Outputs
#   figures/sections_by_lat.png           one panel per latitude band
#   figures/sections_deep_unknown.png     what the plate bound removed
#   figures/sections_depth_below_top.png  event depth minus slab-top depth
#   figures/sections_thickness_check.png  seismicity vs the plate bottom
#   figures/sections_deep_nest.png        the excluded nests

import numpy as np
import pandas as pd
import matplotlib
import paths
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import classify_events as CC

FIG_DIR = "figures"
# Slab2 thickness grid, same node layout as the depth grid. Set to None to
# skip the plate-bottom overlay.
SLAB_THK_XYZ = paths.slab_thk   # e.g. paths.slab_thk, set in main()
LAT_BANDS = [(-20, -18), (-24, -22), (-28, -26), (-32, -30),
             (-36, -34), (-40, -38), (-45, -42)]
# color, label, zorder. Drawing order matters: the slab classes overlap
# in section, so the sparse ones must sit on top of the dense ones or
# they vanish. intra_slab (hundreds) over interface (thousands) over
# deep_unknown (the population the plate bound removed).
CLASS_STYLE = {
    "deep_unknown": ("k", "deep_unknown", 2),
    "outer_rise": ("tab:purple", "outer_rise", 3),
    "intraarc": ("tab:brown", "intraarc", 3),
    "forearc": ("tab:orange", "forearc", 4),
    "slab_interface": ("tab:green", "interface", 5),
    "slab_deep": ("tab:red", "slab_deep", 6),
    "intra_slab": ("tab:blue", "intra_slab", 7),
    "deep_nest": ("magenta", "deep_nest", 8),
}
DEG_KM = 111.195
MAX_DEPTH = 300.0   # section y-limit, km


def trench_distance(lon, lat, lon0, lat0, az_deg=None):
    """Distance (km) along the convergence azimuth from a reference point.

    Parameters
    ----------
    lon, lat : array_like
        Event coordinates, degrees.
    lon0, lat0 : float
        Origin of the profile, typically offshore at the trench.
    az_deg : float or None
        Profile azimuth clockwise from North; defaults to the classifier's
        convergence azimuth so the section is trench-perpendicular.

    Returns
    -------
    numpy.ndarray
        Along-profile distance, km, positive in the azimuth direction.
    """
    az = np.radians(CC.CONV_AZIMUTH_DEG if az_deg is None else az_deg)
    dx = (np.asarray(lon, float) - lon0) * DEG_KM * np.cos(np.radians(lat))
    dy = (np.asarray(lat, float) - lat0) * DEG_KM
    return dx * np.sin(az) + dy * np.cos(az)


def slab_profile(slab, lat_lo, lat_hi, lon0, lat0, step=10.0, thk=None):
    """Slab-top and plate-bottom envelopes across the latitude band.

    A section collapses 2 degrees of latitude onto one plane, and the slab
    dips differently across that span, so each surface is a range rather
    than a curve. Returns per-distance-bin minimum and maximum for the top
    and, when thickness is supplied, for the plate bottom (top + thk) —
    the surface the classification actually cuts on.

    Parameters
    ----------
    slab : SlabGrid
        Slab2 nodes.
    lat_lo, lat_hi : float
        Latitude band limits.
    lon0, lat0 : float
        Profile origin passed to trench_distance.
    step : float
        Distance bin width, km.
    thk : numpy.ndarray or None
        Per-node thickness, aligned with slab.depth. Defaults to
        slab.thk when the grid carries it.

    Returns
    -------
    dict
        Keys d, top_lo, top_hi and, if thickness is available, bot_lo,
        bot_hi. Empty arrays if the band has no nodes.
    """
    if thk is None:
        thk = getattr(slab, "thk", None)
    m = (slab.lat >= lat_lo) & (slab.lat <= lat_hi)
    empty = {"d": np.array([]), "top_lo": np.array([]), "top_hi": np.array([])}
    if not m.any():
        return empty
    d = trench_distance(slab.lon[m], slab.lat[m], lon0, lat0)
    z = slab.depth[m]
    zb = z + thk[m] if thk is not None else None
    bins = np.arange(d.min(), d.max() + step, step)
    idx = np.digitize(d, bins)
    out = {k: [] for k in ("d", "top_lo", "top_hi", "bot_lo", "bot_hi")}
    for k in range(1, len(bins)):
        s = idx == k
        if not s.any():
            continue
        out["d"].append(0.5 * (bins[k - 1] + bins[k]))
        out["top_lo"].append(np.min(z[s]))
        out["top_hi"].append(np.max(z[s]))
        if zb is not None:
            v = zb[s]
            v = v[np.isfinite(v)]
            out["bot_lo"].append(np.min(v) if v.size else np.nan)
            out["bot_hi"].append(np.max(v) if v.size else np.nan)
    return {k: np.array(v) for k, v in out.items() if v}


def fig_sections(df, slab, thk=None):
    """One cross-section per latitude band, all classes, slab surfaces."""
    n = len(LAT_BANDS)
    ncol = 2
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(7 * ncol, 3.6 * nrow),
                             squeeze=False)
    for k, (lo, hi) in enumerate(LAT_BANDS):
        ax = axes[k // ncol][k % ncol]
        sub = df[(df["latitude"] >= lo) & (df["latitude"] <= hi)]
        lat0 = 0.5 * (lo + hi)
        lon0 = -74.0
        for cl, (c, lab, zo) in CLASS_STYLE.items():
            s = sub[sub["class"] == cl]
            if not len(s):
                continue
            # sparse classes lose to dense overlapping ones even when drawn
            # on top: at low alpha a few hundred points vanish under
            # thousands. Scale opacity and size by population.
            sparse = len(s) < 0.1 * len(sub)
            d = trench_distance(s["longitude"], s["latitude"], lon0, lat0)
            ax.plot(d, s["depth"], ".",
                    ms=3.5 if sparse else 2.5,
                    alpha=0.95 if sparse else 0.35,
                    color=c, zorder=zo, label=f"{lab} ({len(s)})")
        p = slab_profile(slab, lo, hi, lon0, lat0, thk=thk)
        if len(p.get("d", [])):
            sd, tlo, thi = p["d"], p["top_lo"], p["top_hi"]
            has_bot = "bot_lo" in p and np.isfinite(p["bot_lo"]).any()
            if has_bot:
                # the plate itself: everything between the top and the
                # bottom is in the slab, and that is exactly what the
                # classification keeps
                ax.fill_between(sd, tlo, p["bot_hi"], color="0.45",
                                alpha=0.18, lw=0, zorder=0,
                                label="plate (top to top+thk)")
                ax.plot(sd, p["bot_lo"], "-", color="tab:cyan", lw=1.2,
                        alpha=0.9, zorder=1, label="plate bottom")
                ax.plot(sd, p["bot_hi"], "-", color="tab:cyan", lw=0.8,
                        alpha=0.5, zorder=1)
            ax.fill_between(sd, tlo, thi, color="0.35", alpha=0.45,
                            lw=0, zorder=1, label="Slab2 top")
        ax.set_xlim(0, 700)
        ax.set_ylim(MAX_DEPTH, 0)
        ax.set_xlabel("distance along convergence azimuth (km)")
        ax.set_ylabel("depth (km)")
        ax.set_title(f"lat {lo} to {hi}", fontsize=9)
        if k == 0:
            h, l = ax.get_legend_handles_labels()
            order = sorted(range(len(l)), key=lambda i: l[i].startswith(
                ("deep_unknown", "Slab2", "+")))
            ax.legend([h[i] for i in order], [l[i] for i in order],
                      fontsize=6, markerscale=2.5, ncol=2, loc="lower right")
    for k in range(n, nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")
    fig.suptitle("Trench-perpendicular sections "
                 f"(azimuth {CC.CONV_AZIMUTH_DEG:.0f} deg)", fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/sections_by_lat.png", dpi=180)
    plt.close(fig)


def fig_deep_unknown(df, slab):
    """What the plate bound removed, and whether it is coherent.

    Two populations are expected and must be told apart: events below the
    Slab2 depth limit (real deep seismicity the geometry cannot reach,
    matched to a shallow node in map view) and scattered outliers. The
    former cluster along the downdip continuation of the slab; the latter
    do not.
    """
    du = df[df["class"] == "deep_unknown"]
    if not len(du):
        print("[sections] no deep_unknown events")
        return
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    (a1, a2), (a3, a4) = axes

    keep = df[df["class"].isin(["intra_slab", "slab_deep"])]
    a1.plot(keep["longitude"], keep["latitude"], ".", ms=1.5, alpha=0.15,
            color="0.75", label=f"kept slab classes ({len(keep)})")
    sc = a1.scatter(du["longitude"], du["latitude"], c=du["depth"], s=4,
                    cmap="magma_r", vmin=0, vmax=700)
    a1.set_xlabel("lon")
    a1.set_ylabel("lat")
    a1.legend(fontsize=7, markerscale=4)
    a1.set_title(f"deep_unknown map ({len(du)})")
    fig.colorbar(sc, ax=a1, label="depth (km)", shrink=0.7)

    a2.plot(keep["depth"], keep["latitude"], ".", ms=1.5, alpha=0.15,
            color="0.75")
    a2.plot(du["depth"], du["latitude"], ".", ms=2, alpha=0.5, color="k")
    a2.set_xlabel("depth (km)")
    a2.set_ylabel("lat")
    a2.invert_xaxis()
    a2.set_title("depth vs latitude (grey = kept)")

    bins = np.arange(0, 720, 20)
    a3.hist(keep["depth"], bins=bins, color="0.8", label="kept")
    a3.hist(du["depth"], bins=bins, color="k", alpha=0.75,
            label="deep_unknown")
    zmax = float(np.nanmax(slab.depth))
    a3.axvline(zmax, color="crimson", lw=1.2,
               label=f"Slab2 max depth ({zmax:.0f} km)")
    a3.set_xlabel("depth (km)")
    a3.set_ylabel("count")
    a3.set_yscale("log")
    a3.legend(fontsize=8)
    a3.set_title("depth distribution")

    a4.plot(du["mag"], du["depth"], ".", ms=3, alpha=0.5, color="k")
    a4.set_xlabel("M")
    a4.set_ylabel("depth (km)")
    a4.invert_yaxis()
    a4.set_title("deep_unknown: magnitude vs depth")

    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/sections_deep_unknown.png", dpi=180)
    plt.close(fig)

    below = int((du["depth"] > zmax).sum())
    print(f"[deep_unknown] {len(du)} total; {below} deeper than the Slab2 "
          f"limit ({zmax:.0f} km) = real deep seismicity with no geometry; "
          f"{len(du) - below} shallower = candidates for a wrong-node match")


def fig_depth_below_top(df, thk=None):
    """Event depth minus slab-top depth, per class.

    The classification works in this coordinate, so it shows directly:
    interface near zero, intra_slab and slab_deep spread through the
    plate, deep_unknown beyond it. The cut is per-event against the local
    thickness, so it appears as a band rather than a single line.
    """
    d = df.dropna(subset=["sub_depth"]).copy()
    d["dz"] = d["depth"] - d["sub_depth"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    bins = np.arange(-80, 200, 4)
    for cl, (c, lab, zo) in CLASS_STYLE.items():
        s = d[d["class"] == cl]
        if not len(s):
            continue
        a1.hist(s["dz"], bins=bins, histtype="step", lw=1.4, color=c,
                zorder=zo, label=f"{lab} ({len(s)})")
        a2.plot(s["dz"], s["latitude"], ".", ms=2, alpha=0.4, color=c,
                zorder=zo)
    lo = hi = None
    if thk is not None and np.isfinite(thk).any():
        lo, hi = np.nanpercentile(thk, 5), np.nanpercentile(thk, 95)
    for ax in (a1, a2):
        ax.axvline(0, color="k", lw=1)
        if lo is not None:
            ax.axvspan(lo, hi, color="tab:cyan", alpha=0.20, zorder=0)
    a1.set_xlabel("depth below slab top (km)")
    a1.set_ylabel("count")
    a1.set_yscale("log")
    a1.legend(fontsize=7)
    a1.set_title("depth relative to Slab2 top"
                 + (f" (cyan = plate bottom, {lo:.0f}-{hi:.0f} km)"
                    if lo is not None else ""))
    a2.set_xlabel("depth below slab top (km)")
    a2.set_ylabel("lat")
    a2.set_xlim(-80, 200)
    a2.set_title("same, vs latitude")
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/sections_depth_below_top.png", dpi=180)
    plt.close(fig)


def fig_plate_bound(df, slab, thk):
    """How the plate bottom cuts the catalog.

    The classification keeps everything between the Slab2 top and
    top + local thickness. This figure shows the thickness field that
    sets the limit, and where the events sit relative to it.
    """
    d = df.dropna(subset=["sub_depth"]).copy()
    d["dz"] = d["depth"] - d["sub_depth"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    (a1, a2), (a3, a4) = axes

    ok = np.isfinite(thk)
    sc = a1.scatter(slab.lon[ok], slab.lat[ok], c=thk[ok], s=1, cmap="viridis")
    a1.set_xlabel("lon")
    a1.set_ylabel("lat")
    a1.set_title("Slab2 thickness = plate bound (km)")
    fig.colorbar(sc, ax=a1, shrink=0.75)

    lat_bins = np.arange(-46, -16, 1.0)
    med = [np.nanmedian(thk[ok][(slab.lat[ok] >= b) & (slab.lat[ok] < b + 1)])
           for b in lat_bins]
    a2.plot(med, lat_bins + 0.5, "o-", color="tab:cyan", ms=3)
    a2.set_xlabel("thickness (km)")
    a2.set_ylabel("lat")
    a2.set_xlim(0, 100)
    a2.set_title("plate thickness vs latitude (tracks plate age)")

    # depth below the top, per class, with the thickness range marked:
    # the cut is per-event, so it appears as a band not a line
    bins = np.arange(-60, 200, 3)
    for cl, (c, lab, zo) in CLASS_STYLE.items():
        s = d[d["class"] == cl]
        if len(s) < 5:
            continue
        a3.hist(s["dz"], bins=bins, histtype="step", lw=1.4, color=c,
                zorder=zo, label=f"{lab} ({len(s)})")
    a3.axvline(0, color="k", lw=1)
    a3.axvspan(np.nanpercentile(thk, 5), np.nanpercentile(thk, 95),
               color="tab:cyan", alpha=0.20, label="plate bottom (p5-p95)")
    a3.set_xlabel("depth below slab top (km)")
    a3.set_ylabel("count")
    a3.set_yscale("log")
    a3.legend(fontsize=6, ncol=2)
    a3.set_title("events relative to the plate bottom")

    # the same, per event, against its own local plate bound
    sl = d[d["class"].isin(["intra_slab", "slab_deep", "deep_unknown",
                            "deep_nest"])]
    for cl in ["intra_slab", "slab_deep", "deep_nest", "deep_unknown"]:
        s = sl[sl["class"] == cl]
        if not len(s):
            continue
        c, lab, zo = CLASS_STYLE[cl]
        a4.plot(s["dz"], s["latitude"], ".", ms=1.5, alpha=0.35, color=c,
                zorder=zo, label=lab)
    a4.plot(med, lat_bins + 0.5, "-", color="tab:cyan", lw=1.8,
            label="plate bottom")
    a4.axvline(0, color="k", lw=1)
    a4.set_xlim(-60, 200)
    a4.set_xlabel("depth below slab top (km)")
    a4.set_ylabel("lat")
    a4.legend(fontsize=7, markerscale=4)
    a4.set_title("slab classes vs the local plate bound")

    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/sections_thickness_check.png", dpi=180)
    plt.close(fig)

    inside = int((d["dz"] <= np.nanmedian(thk)).sum())
    print(f"[plate] {inside}/{len(d)} events within the median plate "
          f"thickness ({np.nanmedian(thk):.0f} km) of the slab top")


def fig_deep_nest(df):
    """The excluded nests: map, section and MFD against the slab classes.

    The MFD panel is the argument for excluding them — a nest with its own
    Mmax and slope cannot share a truncated GR with the distributed slab
    population.
    """
    dn = df[df["class"] == "deep_nest"]
    if not len(dn):
        return
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    a1, a2, a3 = axes

    other = df[df["class"].isin(["intra_slab", "slab_deep"])]
    a1.plot(other["longitude"], other["latitude"], ".", ms=1.5, alpha=0.15,
            color="0.7", label="slab classes")
    a1.plot(dn["longitude"], dn["latitude"], ".", ms=3, alpha=0.7,
            color="magenta", label=f"deep_nest ({len(dn)})")
    for n in CC.DEEP_NEST_EXCLUSIONS:
        th = np.linspace(0, 2 * np.pi, 100)
        a1.plot(n["lon"] + n["radius_deg"] * np.cos(th) /
                np.cos(np.radians(n["lat"])),
                n["lat"] + n["radius_deg"] * np.sin(th), "-",
                color="crimson", lw=1.2)
        a1.annotate(n["name"], (n["lon"], n["lat"]), fontsize=8,
                    color="crimson")
    a1.set_xlabel("lon")
    a1.set_ylabel("lat")
    a1.legend(fontsize=7, markerscale=3)
    a1.set_title("excluded deep nests")

    a2.plot(other["depth"], other["latitude"], ".", ms=1.5, alpha=0.15,
            color="0.7")
    a2.plot(dn["depth"], dn["latitude"], ".", ms=3, alpha=0.7,
            color="magenta")
    a2.set_xlabel("depth (km)")
    a2.set_ylabel("lat")
    a2.invert_xaxis()
    a2.set_title("depth vs latitude")

    edges = np.arange(3.5, 8.5, 0.1)
    for lab, s, c in [("slab classes", other, "0.4"),
                      ("deep_nest", dn, "magenta")]:
        if not len(s):
            continue
        m = s["mag"].to_numpy()
        a3.semilogy(edges, [max((m >= e).sum(), 0.5) for e in edges], "-",
                    color=c, lw=1.5,
                    label=f"{lab} (n={len(s)}, Mmax {m.max():.1f})")
    a3.set_xlabel("M")
    a3.set_ylabel("N(>=M)")
    a3.legend(fontsize=8)
    a3.set_title("MFD: the nest has its own Mmax and slope")

    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/sections_deep_nest.png", dpi=180)
    plt.close(fig)
    print(f"[deep_nest] {len(dn)} events, Mmax {dn['mag'].max():.1f}, "
          f"depth {dn['depth'].min():.0f}-{dn['depth'].max():.0f} km")


def main():
    import os
    os.makedirs(FIG_DIR, exist_ok=True)
    from cat_no_mech_handler import paths

    df = pd.read_csv(str(paths.cat_classified))
    thk_path = SLAB_THK_XYZ or getattr(paths, "slab_thk", None)
    slab = CC.load_slab_xyz(str(paths.slab_depth), str(paths.slab_strike),
                            str(paths.slab_dip),
                            str(thk_path) if thk_path else None)
    print(f"[input] {len(df)} events, classes: "
          + ", ".join(f"{c}={n}" for c, n in df['class'].value_counts().items()))

    thk = getattr(slab, "thk", None)
    if thk is not None and np.isfinite(thk).any():
        print(f"[thk] {int(np.isfinite(thk).sum())}/{len(thk)} nodes, "
              f"median {np.nanmedian(thk):.1f} km, "
              f"range {np.nanmin(thk):.0f}-{np.nanmax(thk):.0f} km")
    else:
        thk = None
        print("[thk] no thickness grid — set paths.slab_thk")

    fig_sections(df, slab, thk)
    fig_deep_unknown(df, slab)
    fig_depth_below_top(df, thk)
    if thk is not None:
        fig_plate_bound(df, slab, thk)
    fig_deep_nest(df)
    print(f"wrote {FIG_DIR}/sections_*.png")


if __name__ == "__main__":
    main()