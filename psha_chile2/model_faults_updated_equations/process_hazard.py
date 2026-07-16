# postprocess_nmin.py
"""
Post-process the 5-branch SSM comparison run (al1/al2/al3/yc vs
phi100_mgeo_tgr, single GMM per TRT).

Plots the hazard curve of every SSM branch (plus the weighted mean) at
selected cities, labeled with the source-model branch id taken from the
calculation's logic tree, and exports the per-branch and stats hazard
maps as vti. Run as:

    python postprocess_nmin.py <calc_id>
"""

import sys
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

import hazard

sns.set_style("darkgrid", {"ytick.left": True, "xtick.bottom": True,
                           "axes.facecolor": ".9"})

CITIES = {
    "Iquique":      (-70.1357, -20.2133),
    "Antofagasta":  (-70.4000, -23.6500),
    "Copiapo":      (-70.3314, -27.3668),
    "Valparaíso":   (-71.6127, -33.0472),
    "Santiago Centro":     (-70.6693, -33.4489),
    "Santiago Peñalolén": (-70.52, -33.46),
    "Concepción":   (-73.0503, -36.8269),
    "Pucón":        (-71.9600, -39.2822),
    "Puerto Montt": (-72.9423, -41.4693),
    "Puerto Aysen": (-72.7020, -45.4028),
}
POES = [0.0021030, 0.000399999]
TR_LABELS = ["$T_r = 475\\,\\mathrm{years}$", "$T_r = 2475\\,\\mathrm{years}$"]
IMTL = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
BRANCH_COLORS = ["steelblue", "seagreen", "darkorange", "purple",
                 "teal", "sienna"]


def branch_labels(model):
    """SSM branch id of each realization, in realization order.

    The full_lt/source_model_lt table is stored in logic-tree FILE order,
    but OpenQuake enumerates realizations sorted by branch id. Sorting the
    ids restores the realization order (verified against an engine run).
    """
    out = []
    for _, comp, _ in model.branches:
        sm = comp[0]
        out.append(sm.decode() if isinstance(sm, bytes) else str(sm))
    return sorted(out)


def check_labels(model, labels, measure_ind):
    """The nofaults branch must be the pointwise minimum everywhere."""
    if "nofaults" not in labels:
        return
    i0 = labels.index("nofaults")
    hc = model.hcurves[:, :, measure_ind, :]
    base = hc[:, i0, :]
    bad = [lab for ib, lab in enumerate(labels)
           if not (hc[:, ib, :] >= base - 1e-12).all()]
    if bad:
        raise RuntimeError(f"branch labeling inconsistent: {bad} plot below "
                           "nofaults somewhere; realization order mismatch")


def site_index(model, lonlat):
    return int(np.argmin(np.sum((model.grid - np.asarray(lonlat)) ** 2, axis=1)))


def plot_city_curves(model, measure="PGA", fname="hazard_curves_cities.png"):
    labels = branch_labels(model)
    im = np.argwhere(np.isin(sorted(model.imtl), measure)).ravel()[0]
    check_labels(model, labels, im)
    x = model.imtl[measure]

    fig, axes = plt.subplots(5, 2, figsize=(11, 20), sharex=True, sharey=True)
    for ax, (city, lonlat) in zip(axes.ravel(), CITIES.items()):
        p = site_index(model, lonlat)
        curves = model.hcurves[p, :, im, :]
        for ib, lab in enumerate(labels):
            ax.loglog(x, curves[ib], linewidth=1.2, linestyle="--",
                      color=BRANCH_COLORS[ib % len(BRANCH_COLORS)], label=lab)
        ax.fill_between(x, curves.min(axis=0), curves.max(axis=0),
                        color="red", alpha=0.15, label="Envelope")

        ax.set_xlim(1e-2, 3)
        ax.set_ylim(1e-5, 2)
        xlims = ax.get_xlim()
        for poe, lab in zip(POES, TR_LABELS):
            ax.axhline(poe, linestyle="--", linewidth=0.8, color="black")
            ax.text(min(xlims) * 1.1, poe * 1.08, lab, fontsize=12)

        ax.tick_params(which="major", axis="y", length=8, color="gray", width=0.5)
        ax.tick_params(which="minor", axis="y", length=4, color="gray", width=0.5)
        ax.grid(axis="y", which="major", linewidth=1)
        ax.grid(axis="y", which="minor", linewidth=0.4)
        ax.grid(axis="x", which="major", linewidth=1)
        ax.grid(axis="x", which="minor", linewidth=0.4)
        ax.set_title(f"{city} - PoE in 1 year", fontsize=16)

    for ax in axes[-1]:
        ax.set_xlabel(f"{measure} $[g]$", fontsize=14)
    for ax in axes[:, 0]:
        ax.set_ylabel("Probability of exceedance - 1 year", fontsize=14)
    axes[0, 0].legend(loc=3, fontsize=11)
    fig.tight_layout()
    fig.savefig(fname, dpi=300)
    print(f"wrote {fname}")
    return fig


def export_city_csv(model, measure="PGA", prefix="hcurves"):
    labels = branch_labels(model)
    im = np.argwhere(np.isin(sorted(model.imtl), measure)).ravel()[0]
    x = model.imtl[measure]
    for city, lonlat in CITIES.items():
        p = site_index(model, lonlat)
        cols = [x] + [model.hcurves[p, ib, im, :] for ib in range(len(labels))]
        cols.append(model.hcurves_stats[p, 0, im, :])
        fname = f"{prefix}_{city.lower()}.csv"
        np.savetxt(fname, np.column_stack(cols), delimiter=",",
                   header=",".join([measure] + labels + ["mean"]), comments="")
        print(f"wrote {fname}")


def main(calc):
    model = hazard.hazardResults("nmin_test", "./", calc)
    model.parse_db(IMTL)
    model.get_maps_from_curves(["PGA"], POES)
    model.get_stats("hcurves", "PGA")
    model.get_stats("hmaps", "PGA")

    print("realizations (vti band order):")
    for n, comp, w in model.branches:
        print(f"  band {n}: {branch_labels(model)[n]}  w={w:.3f}")

    plot_city_curves(model)
    export_city_csv(model)

    # per-branch maps: one band per realization, order as printed above
    model.model2vti("nmin_branches", "hmaps", ["PGA"], levels=POES,
                    res=(0.01, 0.01), res_method="nearest", crs_f="EPSG:4326")
    # stats maps: bands = mean, geom. mean, q10, q25, median, q75, q90
    model.model2vti("nmin_stats", "hmaps_stats", ["PGA"], levels=POES,
                    res=(0.01, 0.01), res_method="nearest", crs_f="EPSG:4326")


if __name__ == "__main__":
    main(1639)