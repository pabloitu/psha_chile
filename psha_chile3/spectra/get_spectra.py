import numpy as np
from matplotlib import pyplot as plt
import hazard
import seaborn as sns
sns.set_style(
    "darkgrid",
    {
        "ytick.left": True,
        "xtick.bottom": True,
        "axes.facecolor": ".9",
        "font.family": "Ubuntu",
    },
)
disc = np.logspace(np.log10(0.0005), np.log10(3.00), 25)
im = ["PGA", "SA(0.1)","SA(0.2)","SA(0.3)","SA(0.5)","SA(0.75)","SA(1)","SA(2)","SA(3)","SA(5)"]
imtl = {"PGA":disc,
         "SA(0.1)": disc,
         "SA(0.2)": disc,
         "SA(0.3)": disc,
         "SA(0.5)": disc,
         "SA(0.75)":disc,
         "SA(1)": disc,
         "SA(2)": disc,
         "SA(3)": disc,
         "SA(5)": disc,
        }
model = hazard.hazardResults('test', './', 66)
model.parse_db(imtl)
a = model.get_maps_from_curves(im, [0.0021030])

for i in im:
    model.get_stats('hcurves', i)
    model.get_stats('hmaps', i)

poi = np.array([[-70.1, -20.3],
                [-70.7, -33.4]])
poi = ['Iquique', 'Santiago']

for npoint, p in enumerate(poi):
    uhs = []

    fig, ax = plt.subplots(figsize=(6, 4))

    for n, i in enumerate(im):
        # value shape is something like (n_stats,); we keep only the FIRST stat (e.g. mean)
        value_vec = model.hmaps_stats[npoint, 0, n, :]
        value = value_vec[0]  # first statistic only
        uhs.append(value)

    uhs = np.array(uhs)

    # ---- SAVE UHS TO FILE (IM label + value) ----
    outname = f"{p}_uhs_values.txt"
    with open(outname, "w") as f:
        f.write("# Uniform Hazard Spectrum (10% in 50 yr) for {}\n".format(p))
        f.write("# IM_label    value\n")
        for label, val in zip(im, uhs):
            f.write(f"{label:8s}  {val:.6e}\n")
    # --------------------------------------------

    # Plot: x is implicitly 0..len(im)-1
    ax.plot(uhs, color="red", marker="o", label="Uniform Hazard Spectra (10% in 50yr.)")

    # --- set IM labels on x-axis ---
    x_positions = np.arange(len(im))
    im_labels = [
        r"$\mathrm{PGA}$",
        r"$SA(0.1\,\mathrm{s})$",
        r"$SA(0.2\,\mathrm{s})$",
        r"$SA(0.3\,\mathrm{s})$",
        r"$SA(0.5\,\mathrm{s})$",
        r"$SA(0.75\,\mathrm{s})$",
        r"$SA(1.0\,\mathrm{s})$",
        r"$SA(2.0\,\mathrm{s})$",
        r"$SA(3.0\,\mathrm{s})$",
        r"$SA(5.0\,\mathrm{s})$",
    ]

    ax.set_xticks(x_positions)
    ax.set_xticklabels(im_labels, rotation=45, ha="right", fontsize=8)

    ax.tick_params(which="major", axis="y", length=8, color="gray", width=0.5, labelsize=8)
    ax.tick_params(which="minor", axis="y", length=4, color="gray", width=0.5)
    ax.tick_params(which="major", axis="x", length=5, color="gray", width=0.5)

    ax.grid(axis="y", which="major", linewidth=1)
    ax.grid(axis="y", which="minor", linewidth=0.4)
    ax.grid(axis="x", which="major", linewidth=1)
    ax.grid(axis="x", which="minor", linewidth=0.4)
    ax.set_ylim([-0.02, 2.6])
    ax.set_title(f"{p}")
    ax.legend(loc="best")

    fig.tight_layout()
    fig.savefig(fname=f"{p}_uhs.png", dpi=200, bbox_inches="tight")
    plt.close(fig)




    # model.plot_pointcurves('SA(0.2)', poi, ax=axes,
    #                         plot_args={'mean_c': 'red', 'mean_s': '-', 'stats_lw': 2,
    #                                    'xlims': [1e-2, 3],
    #                                    'ylims': [1e-5, 2],
    #                                    'poes': False}, yrs=1)
    # # plt.show()
