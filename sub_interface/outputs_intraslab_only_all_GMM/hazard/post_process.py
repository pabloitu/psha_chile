# process_sub_branches.py
# Hazard curves for the subduction interface tree at the city sites:
#   - realizations grouped by source-model branch (16), GMM branches
#     collapsed within each group by their renormalized weights
#   - branch lines colored by rate model (seismic/geodetic), dashed for the
#     non-segmented geometry; min-max envelope across the 16 collapsed
#     branches; weighted ensemble mean
#   - previous full-model calculation (PREV_CALC_ID) at the nearest grid
#     site, for order-of-magnitude comparison
# Realization -> branch mapping is RECONSTRUCTED (sm branches x interface
# GMM branches in logic-tree order) and VERIFIED against the datastore
# rlz weights; the script refuses to run if they do not match. Copy next
# to hazard.py in the model output hazard folder.

import os

import h5py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import hazard

# new calculation (interface tree, city sites)
NEW_CALC_ID = 1654          # None -> set it; int -> ~/oqdata/calc_<id>.hdf5
OQDATA = None               # None -> hazard.get_oqcalc default folder
NEW_IMTL = {"PGA": np.logspace(np.log10(0.005), np.log10(3.0), 30)}
TRT = "Subduction Interface"

# previous full model for comparison
PREV_CALC_ID = 1642
PREV_IMTL = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
PREV_LABEL = f"Previous full model (calc {PREV_CALC_ID})"

IMT = "PGA"
YRS = 1
RUN_LABEL = "intraslab only"   # plot title suffix for this run
XLIMS = (1e-2, 3)
YLIMS = (1e-5, 2)
OUTDIR = "figures_sub_branches"

CITIES = {
    "Iquique": (-70.14, -20.21),
    "Antofagasta": (-70.40, -23.65),
    "Copiapo": (-70.33, -27.37),
    "Valparaiso": (-71.62, -33.05),
    "Santiago": (-70.66, -33.45),
    "Concepcion": (-73.05, -36.83),
    "Valdivia": (-73.25, -39.81),
}

# branch styling from the tag structure {seg|full}__{rate}__{form};
# tags outside that pattern (e.g. a single intraslab model) get a
# generic style and their own legend entry
def branch_style(tag):
    parts = tag.split("__")
    if len(parts) != 3:
        return dict(color="seagreen", ls="-", lw=1.8, alpha=0.9)
    geom, rate, form = parts
    color = "steelblue" if rate == "seis" else "darkorange"
    ls = "-" if geom == "seg" else "--"
    faint = rate in ("geo_lo", "geo_hi")
    return dict(color=color, ls=ls, lw=0.7 if faint else 1.4,
                alpha=0.45 if faint else 0.9)


def standard_tags(tags):
    return all(len(t.split("__")) == 3 for t in tags)


def load_model(name, calc_id, imtl):
    path = hazard.get_oqcalc(calc_id, OQDATA) if OQDATA else calc_id
    m = hazard.hazardResults(name, None, path)
    m.parse_db(imtl)
    return m


def interface_groups(model):
    """
    Map source-model branch tag -> (rlz indices, gmm weights, branch weight).

    Realizations come in contiguous blocks per source model, ordered by
    full_lt/sm_data (source models sorted alphabetically by FILE NAME).
    Within each block the GMM branches of ALL active TRTs cycle; their
    collapse weights are taken directly from the stored rlz weights, so
    any number of GMM axes (e.g. interface x intraslab) is handled.
    Structural checks: block weight sums must reproduce the sm weights and
    the normalized within-block pattern must be identical across blocks.
    """
    def s(x):
        # sm_data names arrive as b"['src/x.xml']" — a bytes repr of a list
        x = x[0] if isinstance(x, (list, np.ndarray)) else x
        x = x.decode() if isinstance(x, bytes) else str(x)
        return x.strip("[]'\" ")

    with h5py.File(model.calcpath, "r") as db:
        sm = [(s(r["name"]), float(r["weight"]))
              for r in db["full_lt/sm_data"][:]]
        gs_info = [(s(r["trt"]), s(r["branch"]), float(r["weight"]))
                   for r in db["full_lt/gsim_lt"][:]]
        w_rlz = db["weights"][:].astype(float)

    n_sm = len(sm)
    if model.nb % n_sm:
        raise RuntimeError(f"{model.nb} rlzs not divisible by {n_sm} source "
                           "models — enumeration differs from block layout")
    gsz = model.nb // n_sm

    wb = w_rlz.reshape(n_sm, gsz)
    sums = wb.sum(axis=1)
    w_sm = np.array([w for _, w in sm])
    if not np.allclose(sums / sums.sum(), w_sm / w_sm.sum(),
                       rtol=1e-4, atol=1e-7):
        raise RuntimeError("block weight sums do not reproduce sm_data "
                           "weights — refusing to group")
    norm = wb / sums[:, None]
    if not np.allclose(norm, norm[0], rtol=1e-4, atol=1e-7):
        raise RuntimeError("within-block GMM weight pattern differs across "
                           "source models — refusing to group")

    groups = {}
    for i, (name, ws) in enumerate(sm):
        tag = name.split("/")[-1].replace("sub_int__", "").replace(".xml", "")
        groups[tag] = {"idx": np.arange(i * gsz, (i + 1) * gsz),
                       "w": norm[0], "w_branch": ws}
    trts = {}
    for trt, _, _ in gs_info:
        trts[trt] = trts.get(trt, 0) + 1
    print(f"[groups] {n_sm} source branches x {gsz} GMM combinations "
          f"({' x '.join(f'{n} {t}' for t, n in trts.items())}), "
          "weights verified (sm_data order)")
    return groups


def collapsed_curves(model, isite, imt_index, groups):
    """GMM-collapsed mean curve per source branch at one site."""
    out = {}
    for sid, g in groups.items():
        c = model.hcurves[isite, g["idx"], imt_index, :]
        out[sid] = np.average(c, axis=0, weights=g["w"])
    return out


def poes(c, yrs):
    return c if yrs == 1 else 1.0 - (1.0 - np.asarray(c)) ** yrs


def prev_mean_curve(model, isite, imt_index):
    with h5py.File(model.calcpath, "r") as db:
        if "hcurves-rlzs" in db:
            w = db["weights"][:]
            return np.average(model.hcurves[isite, :, imt_index, :],
                              axis=0, weights=w / w.sum())
    return model.hcurves[isite, 0, imt_index, :]  # stats: index 0 = mean


def plot_city(city, point, new, groups, prev):
    isite = hazard_site(new, point)
    imt_i = list(new.imtl.keys()).index(IMT)
    lv = np.asarray(new.imtl[IMT])

    curves = collapsed_curves(new, isite, imt_i, groups)
    tags = list(curves)
    arr = np.array([curves[t] for t in tags])
    wb = np.array([groups[t]["w_branch"] for t in tags])
    mean = np.average(arr, axis=0, weights=wb / wb.sum())
    lo, hi = arr.min(axis=0), arr.max(axis=0)

    std = standard_tags(tags)
    fig, ax = plt.subplots(figsize=(6, 5))
    if len(tags) > 1:
        ax.fill_between(lv, poes(lo, YRS), poes(hi, YRS), color="0.55",
                        alpha=0.25, lw=0, label="Source branches (min-max)")
    for t in tags:
        ax.plot(lv, poes(curves[t], YRS), **branch_style(t),
                label=(f"_{t}" if std else t))
    ax.plot(lv, poes(mean, YRS), "k", lw=2.2,
            label="GMM-collapsed mean" if len(tags) == 1
            else "Weighted mean (GMM+SSC)")

    ip = hazard_site(prev, point)
    imt_ip = list(prev.imtl.keys()).index(IMT)
    lvp = np.asarray(prev.imtl[IMT])
    ax.plot(lvp, poes(prev_mean_curve(prev, ip, imt_ip), YRS), color="0.2",
            lw=2, ls=":", label=PREV_LABEL)

    from matplotlib.lines import Line2D
    if not std:
        ax.legend(loc="best", frameon=True, fontsize=8)
    else:
        ax.legend(handles=[
        plt.Rectangle((0, 0), 1, 1, fc="0.55", alpha=0.25),
        Line2D([0], [0], color="steelblue", lw=1),
        Line2D([0], [0], color="darkorange", lw=1),
        Line2D([0], [0], color="k", lw=1, ls="--"),
        Line2D([0], [0], color="k", lw=2.2),
        Line2D([0], [0], color="0.2", lw=2, ls=":")],
        labels=["Source branches (min-max)", "Seismic branches",
                "Geodetic branches", "Non-segmented (dashed)",
                "Weighted mean", PREV_LABEL],
        loc="best", frameon=True, fontsize=8)

    # 10% / 2% in 50 yr as annual PoE
    for poe50, lab in ((0.10, "475 yr (10% in 50)"),
                       (0.02, "2475 yr (2% in 50)")):
        y = 1.0 - (1.0 - poe50) ** (1.0 / 50.0) if YRS == 1 else poe50
        ax.axhline(y, color="0.25", lw=0.8, ls="-.", alpha=0.8)
        ax.text(XLIMS[0] * 1.15, y * 1.15, lab, fontsize=7, color="0.25")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*XLIMS)
    ax.set_ylim(*YLIMS)
    ax.set_xlabel(f"{IMT} (g)")
    ax.set_ylabel("Annual PoE" if YRS == 1 else f"PoE in {YRS} yr")
    ax.set_title(f"{city} — {RUN_LABEL} vs previous full model")
    for wh, lwd in (("major", 1), ("minor", 0.4)):
        ax.grid(axis="both", which=wh, linewidth=lwd)

    os.makedirs(OUTDIR, exist_ok=True)
    png = os.path.join(OUTDIR, f"{city}_{IMT}_sub_branches.png")
    fig.savefig(png, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_city] {png}")


def hazard_site(model, point):
    d = np.sum((model.grid - np.array(point)) ** 2, axis=1)
    i = int(np.argmin(d))
    print(f"[site] {point} -> ({model.grid[i, 0]:.3f}, {model.grid[i, 1]:.3f})")
    return i


def main():
    sns.set_style("darkgrid", {"ytick.left": True, "xtick.bottom": True,
                               "axes.facecolor": ".9"})
    if NEW_CALC_ID is None:
        raise SystemExit("set NEW_CALC_ID to the oq calculation id of the "
                         "city run")
    new = load_model("sub_cities", NEW_CALC_ID, NEW_IMTL)
    groups = interface_groups(new)
    prev = load_model("previous", PREV_CALC_ID, PREV_IMTL)
    for city, point in CITIES.items():
        plot_city(city, point, new, groups, prev)


if __name__ == "__main__":
    main()