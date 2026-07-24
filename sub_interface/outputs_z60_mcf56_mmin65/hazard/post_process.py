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
NEW_CALC_ID = 1644          # None -> set it; int -> ~/oqdata/calc_<id>.hdf5
OQDATA = None               # None -> hazard.get_oqcalc default folder
NEW_IMTL = {"PGA": np.logspace(np.log10(0.005), np.log10(3.0), 30)}
TRT = "Subduction Interface"

# previous full model for comparison
PREV_CALC_ID = 1642
PREV_IMTL = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
PREV_LABEL = f"Previous full model (calc {PREV_CALC_ID})"

IMT = "PGA"
YRS = 1
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

# branch styling from the tag structure {seg|full}__{rate}__{form}
def branch_style(tag):
    geom, rate, form = tag.split("__")
    color = "steelblue" if rate == "seis" else "darkorange"
    ls = "-" if geom == "seg" else "--"
    faint = rate in ("geo_lo", "geo_hi")
    return dict(color=color, ls=ls, lw=0.7 if faint else 1.4,
                alpha=0.45 if faint else 0.9)


def load_model(name, calc_id, imtl):
    path = hazard.get_oqcalc(calc_id, OQDATA) if OQDATA else calc_id
    m = hazard.hazardResults(name, None, path)
    m.parse_db(imtl)
    return m


def interface_groups(model):
    """
    Map source-model branch tag -> (rlz indices, gmm weights, branch weight).

    OQ orders realizations by full_lt/sm_data — the source models sorted
    ALPHABETICALLY BY FILE NAME, not by logic-tree order — with the TRT's
    gsim branches cycling within each block. Groups are built from sm_data
    directly and accepted only if the product weights reproduce the stored
    per-rlz weights.
    """
    def s(x):
        # sm_data names arrive as b"['src/x.xml']" — a bytes repr of a list
        x = x[0] if isinstance(x, (list, np.ndarray)) else x
        x = x.decode() if isinstance(x, bytes) else str(x)
        return x.strip("[]'\" ")

    with h5py.File(model.calcpath, "r") as db:
        sm = [(s(r["name"]), float(r["weight"]))
              for r in db["full_lt/sm_data"][:]]
        gs = [(s(r["branch"]), float(r["weight"]))
              for r in db["full_lt/gsim_lt"][:] if s(r["trt"]) == TRT]
        w_rlz = db["weights"][:]

    if not gs:
        raise KeyError(f"TRT '{TRT}' not in full_lt/gsim_lt")
    n_exp = len(sm) * len(gs)
    if n_exp != model.nb:
        raise RuntimeError(
            f"rlz count mismatch: {len(sm)} sm x {len(gs)} gmm = {n_exp}, "
            f"datastore has {model.nb}")
    w_rec = np.array([ws * wg for _, ws in sm for _, wg in gs])
    w_rec = w_rec / w_rec.sum() * w_rlz.sum()
    if not np.allclose(w_rec, w_rlz, rtol=1e-4, atol=1e-7):
        raise RuntimeError(
            "sm_data x gsim product weights do not match datastore rlz "
            "weights — refusing to group")

    groups, n = {}, 0
    gw = np.array([wg for _, wg in gs])
    for name, ws in sm:
        tag = name.split("/")[-1].replace("sub_int__", "").replace(".xml", "")
        groups[tag] = {"idx": np.arange(n, n + len(gs)),
                       "w": gw / gw.sum(), "w_branch": ws}
        n += len(gs)
    print(f"[groups] {len(sm)} source branches x {len(gs)} GMMs = "
          f"{n_exp} rlzs, weights verified (sm_data order)")
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

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.fill_between(lv, poes(lo, YRS), poes(hi, YRS), color="0.55",
                    alpha=0.25, lw=0, label="Source branches (min-max)")
    for t in tags:
        ax.plot(lv, poes(curves[t], YRS), **branch_style(t), label=f"_{t}")
    ax.plot(lv, poes(mean, YRS), "k", lw=2.2, label="Weighted mean (GMM+SSC)")

    ip = hazard_site(prev, point)
    imt_ip = list(prev.imtl.keys()).index(IMT)
    lvp = np.asarray(prev.imtl[IMT])
    ax.plot(lvp, poes(prev_mean_curve(prev, ip, imt_ip), YRS), color="0.2",
            lw=2, ls=":", label=PREV_LABEL)

    from matplotlib.lines import Line2D
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
    ax.set_title(f"{city} — interface sources only vs previous full model")
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