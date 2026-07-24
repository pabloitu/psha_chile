# make_curves_branches.py
# Hazard curves per source-model branch:
#   - fault branches (al1, al2, al3, yc, wc_scaling): min-max envelope across
#     them (shaded) + their weighted mean (solid)
#   - nofaults (subduction + UNCAPPED crustal ssm): single line
#   - subduction_only (no crustal seismicity): single line
# No global envelope: only the fault branches get one.
#
# Realizations are grouped by the source-model branch id, which is
# components[0] of hazardResults.branches; the GMPE branches within each group
# are collapsed by their weights.

import os

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import hazard

# model
MODEL_NAME = "AllBranches"
MODEL_PATH = "./model_branches"
CALC_ID = 1642            # None -> latest calculation in the output folder
IMT = "PGA"
IMTL = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
YRS = 1                   # investigation time of the curves

# branch grouping (source-model branch ids as written in the logic tree)
FAULT_BRANCHES = ["al1", "al2", "al3", "yc", "wc_scaling"]
LINE_BRANCHES = {
    "nofaults": dict(label="No faults (crustal ssm only)", color="steelblue"),
    "subduction_only": dict(label="Subduction only", color="0.35"),
}
FAULT_COLOR = "darkred"
PLOT_INDIVIDUAL_FAULT_BRANCHES = False   # thin lines per fault branch

XLIMS = (1e-2, 3)
YLIMS = (1e-5, 2)
OUTDIR = "figures_branches"

CITIES = {
    "Iquique": (-70.1357, -20.2133),
    "Antofagasta": (-70.4000, -23.6500),
    "Copiapo": (-70.3314, -27.3668),
    "Valparaíso": (-71.6127, -33.0472),
    "Santiago Centro": (-70.6693, -33.4489),
    "Santiago Peñalolén": (-70.52, -33.46),
    "Concepción": (-73.0503, -36.8269),
    "Pucón": (-71.9600, -39.2822),
    "Puerto Montt": (-72.9423, -41.4693),
    "Puerto Aysen": (-72.7020, -45.4028),
}


def site_index(model, point):
    """Nearest site of the hazard grid to (lon, lat)."""
    d = np.sum((model.grid - np.array(point)) ** 2, axis=1)
    i = int(np.argmin(d))
    print(f"[site_index] {point} -> site {i} at "
          f"({model.grid[i, 0]:.3f}, {model.grid[i, 1]:.3f})")
    return i


def branch_groups(model):
    """
    Map source-model branch id -> (rlz indices, weights).

    branches is [(rlz_index, components, weight)] with components[0] the
    source-model branch id; the remaining components are the GMPE branches.
    """
    groups = {}
    for n, comp, w in model.branches:
        sm_id = comp[0]
        sm_id = sm_id.decode() if isinstance(sm_id, bytes) else str(sm_id)
        groups.setdefault(sm_id, {"idx": [], "w": []})
        groups[sm_id]["idx"].append(n)
        groups[sm_id]["w"].append(float(w))
    for k, v in groups.items():
        v["idx"] = np.array(v["idx"])
        v["w"] = np.array(v["w"])
        print(f"[branch_groups] {k}: {len(v['idx'])} rlzs, "
              f"weight {v['w'].sum():.4f}")
    return groups


def group_curves(model, isite, imt_index, groups, name):
    """
    Curves of one source-model branch at one site: (n_rlzs, n_levels), plus
    the GMPE-weighted mean of the group (weights renormalized within it).
    """
    if name not in groups:
        raise KeyError(f"[group_curves] branch '{name}' not in the datastore; "
                       f"available: {sorted(groups)}")
    idx, w = groups[name]["idx"], groups[name]["w"]
    curves = model.hcurves[isite, idx, imt_index, :]
    mean = np.average(curves, axis=0, weights=w / w.sum())
    return np.asarray(curves), mean, w.sum()


def poes(curves, yrs):
    """Curves are annual PoE; rescale to the requested time window."""
    if yrs == 1:
        return curves
    return 1.0 - (1.0 - np.asarray(curves)) ** yrs


def plot_city(model, city, point, groups, imt_index, levels):
    isite = site_index(model, point)

    # fault branches: min-max envelope + weighted mean across the branches
    means, wsum = [], []
    per_branch = {}
    for b in FAULT_BRANCHES:
        c, m, w = group_curves(model, isite, imt_index, groups, b)
        per_branch[b] = m
        means.append(m)
        wsum.append(w)
    means = np.array(means)
    wsum = np.array(wsum)
    lo, hi = means.min(axis=0), means.max(axis=0)
    fault_mean = np.average(means, axis=0, weights=wsum / wsum.sum())

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.fill_between(levels, poes(lo, YRS), poes(hi, YRS), color=FAULT_COLOR,
                    alpha=0.25, lw=0,
                    label="Fault branches (min-max)")
    if PLOT_INDIVIDUAL_FAULT_BRANCHES:
        for b, m in per_branch.items():
            ax.plot(levels, poes(m, YRS), color=FAULT_COLOR, lw=0.8,
                    alpha=0.7, ls="--", label=f"_{b}")
    ax.plot(levels, poes(fault_mean, YRS), color=FAULT_COLOR, lw=2,
            label="Faults (mean)")

    # reference models: one line each, no envelope
    for b, style in LINE_BRANCHES.items():
        _, m, _ = group_curves(model, isite, imt_index, groups, b)
        ax.plot(levels, poes(m, YRS), color=style["color"], lw=2,
                label=style["label"])

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*XLIMS)
    ax.set_ylim(*YLIMS)
    ax.set_xlabel(f"{IMT} (g)")
    ax.set_ylabel(f"PoE in {YRS} yr" if YRS > 1 else "Annual PoE")
    ax.set_title(city)
    ax.tick_params(which="major", axis="y", length=8, color="gray", width=0.5)
    ax.tick_params(which="minor", axis="y", length=4, color="gray", width=0.5)
    ax.grid(axis="y", which="major", linewidth=1)
    ax.grid(axis="y", which="minor", linewidth=0.4)
    ax.grid(axis="x", which="major", linewidth=1)
    ax.grid(axis="x", which="minor", linewidth=0.4)

    handles, labels = ax.get_legend_handles_labels()
    keep = [(h, l) for h, l in zip(handles, labels) if not l.startswith("_")]
    if PLOT_INDIVIDUAL_FAULT_BRANCHES:
        keep.append((Line2D([0], [0], color=FAULT_COLOR, lw=0.8, ls="--"),
                     "individual fault branches"))
    ax.legend([h for h, _ in keep], [l for _, l in keep], loc="best",
              frameon=True, fontsize=8)

    os.makedirs(OUTDIR, exist_ok=True)
    png = os.path.join(OUTDIR, f"{city}_{IMT}_branches.png")
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.02,
                facecolor="white")
    plt.close(fig)
    print(f"[plot_city] wrote {png}")


def main():
    sns.set_style("darkgrid", {"ytick.left": True, "xtick.bottom": True,
                               "axes.facecolor": ".9",
                               "font.family": "Ubuntu"})
    model = hazard.hazardResults(MODEL_NAME, MODEL_PATH, CALC_ID)
    model.parse_db(IMTL)
    groups = branch_groups(model)

    missing = [b for b in FAULT_BRANCHES + list(LINE_BRANCHES)
               if b not in groups]
    if missing:
        raise KeyError(f"[main] branches not found in the datastore: {missing}; "
                       f"available: {sorted(groups)}")

    imt_index = list(model.imtl.keys()).index(IMT)
    levels = np.asarray(model.imtl[IMT])

    for city, point in CITIES.items():
        plot_city(model, city, point, groups, imt_index, levels)
    POES = [0.0021030, 0.000399999]

    model.model2vti("nmin_branches", "hmaps", ["PGA"], levels=POES,
                    res=(0.01, 0.01), res_method="nearest", crs_f="EPSG:4326")
if __name__ == "__main__":
    main()