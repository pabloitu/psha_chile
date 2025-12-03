import os
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import numpy as np
from matplotlib import pyplot as plt
from sklearn.conftest import pyplot

import hazard

imtl = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
cities = {
    "Iquique":      (-70.1357, -20.2133),
    "Antofagasta":  (-70.4000, -23.6500),
    "Copiapo":      (-70.3314, -27.3668),
    "Valparaiso":   (-71.6127, -33.0472),
    "Santiago Centre":     (-70.6693, -33.4489),
    "Santiago Penalolen": (-70.52, -33.46),
    "Concepcion":   (-73.0503, -36.8269),
    "Pucon":        (-71.9600, -39.2822),
    "Puerto Montt": (-72.9423, -41.4693),
    "Puerto Aysen": (-72.7020, -45.4028),
}


model_with = hazard.hazardResults('Faults', './with', './with/results_all/calc_50.hdf5')
model_with.parse_db(imtl)
model_with.get_stats('hcurves', 'PGA')

# model_without = hazard.hazardResults('No_Faults', './without', './without/results_all/calc_1632.hdf5')
# model_without.parse_db(imtl)
# model_without.get_stats('hcurves', 'PGA')

import seaborn as sns
sns.set_style("darkgrid", {"ytick.left": True, 'xtick.bottom': True,"axes.facecolor": ".9", 'font.family': 'Ubuntu'})
os.makedirs('figures', exist_ok=True)
for city, coords in cities.items():
    if city != "Concepcion":
        continue
    ax = model_with.plot_pointcurves('PGA', point=coords, title=" ",
                                     plot_args={'mean_c': 'darkred', 'mean_s': '-', 'stats_lw': 2, 'env_c': 'darkred',
                                       'xlims': [1e-2, 3],
                                        'xlabel': "PGA (%g)$",
                                        'ylabel': "Probabilidad de excedencia",
                                       'ylims': [2e-4, 1.5],
                                       'plot_env': True,
                                       'labels': {'mean': None,
                                                  },
                                       'poes': True
                                                },
                                     yrs=50)
    ax.tick_params(which='major', axis='y', length=8, color='gray', width=0.5)
    ax.tick_params(which='minor', axis='y', length=4, color='gray', width=0.5)
    ax.grid(axis='y', which='major', linewidth=1)
    ax.grid(axis='y', which='minor', linewidth=0.4)

    ax.grid(axis='x', which='major', linewidth=1)
    ax.grid(axis='x', which='minor', linewidth=0.4)
    handles, labels = ax.get_legend_handles_labels()
    ax.set_xlabel("PGA [%g]")
    ax.set_ylabel("Probabilidad de excedencia")
    extra_handles = [Patch(facecolor="0.8", edgecolor="none", alpha=0.5, label="95% confianza"),
                    Line2D([0], [0],color="black", lw=0.5,label="Promedio"),]
    extra_labels = [h.get_label() for h in extra_handles]
    handles += extra_handles
    labels += extra_labels
    unique = dict(zip(labels, handles))
    ax.legend(list(unique.values()), list(unique.keys()),loc="best", frameon=True)
    fig = ax.get_figure()
    fig.savefig(f"figures/example2.png",dpi=300,bbox_inches="tight", pad_inches=0.02, facecolor="white",)
    plt.show()
    plt.close(fig)

# model.model2vti('test', 'hmaps_stats', ['PGA'], levels=[0.0021030],
#                 res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
#                 crop='../../shp/chile.shp')