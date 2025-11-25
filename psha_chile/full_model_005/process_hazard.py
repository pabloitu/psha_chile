import numpy as np
from matplotlib.ticker import LogLocator

from matplotlib import pyplot as plt
import hazard
import seaborn as sns
import matplotlib as mpl

sns.set_style(
    "darkgrid",
    {
        "axes.facecolor": ".9",
        "font.family": "DejaVu Sans"   # or "Liberation Sans"
    }
)

mpl.rcParams["axes.grid.which"] = "both"   # grid on both major and minor ticks
imtl = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
model = hazard.hazardResults('test', './', 348)
model.parse_db(imtl)
a = model.get_maps_from_curves(['PGA'], [0.0021030, 0.000399999])
model.get_stats('hcurves', 'PGA')
model.get_stats('hmaps', 'PGA')

fig, axes = plt.subplots(1, 1, figsize=(16, 10))

iquique = np.array([-70.13, -20.24])
antofagasta =  np.array([-70.39, -23.65])
coquimbo =  np.array([-71.34, -29.95])
santiago = np.array([-70.6693, -33.4489])

concepcion = np.array([-73.8201, -36.82])
puertomontt = np.array([-72.94, -41.64])
puertoaysen = np.array([-72.68, -45.4])
puntaarenas = np.array([-70.9, -53.16])

fig, axes = plt.subplots(1, 1, figsize=(12, 8))


model.plot_pointcurves('PGA', iquique, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'green', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'labels': ['Iquique'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': False}, yrs=1)
model.plot_pointcurves('PGA', antofagasta, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'purple', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'legend': True,
                                   'labels':[ 'Antofagasta'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': False}, yrs=1)
model.plot_pointcurves('PGA', coquimbo, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'steelblue', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'legend': True,
                                   'labels': ['Coquimbo'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': False}, yrs=1)
model.plot_pointcurves('PGA', santiago, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'red', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'legend': True,
                                   'labels': ['Santiago'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': True}, yrs=1)
axes.xaxis.set_minor_locator(LogLocator(base=10, subs=range(1, 10)))
axes.yaxis.set_minor_locator(LogLocator(base=10, subs=range(1, 10)))
plt.savefig('psha_north.png', dpi=200)
# plt.show()

fig, axes = plt.subplots(1, 1, figsize=(12, 8))


model.plot_pointcurves('PGA', concepcion, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'green', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'labels': ['Concepcion'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': False}, yrs=1)
model.plot_pointcurves('PGA', puertomontt, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'purple', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'legend': True,
                                   'labels':[ 'Puerto Montt'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': False}, yrs=1)
model.plot_pointcurves('PGA', puertoaysen, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'steelblue', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'legend': True,
                                   'labels': ['Puerto Aysen'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': False}, yrs=1)
model.plot_pointcurves('PGA', puntaarenas, ax=axes,
                       title='Hazard Chile main cities',
                        plot_args={'mean_c': 'red', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [5e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'legend': True,
                                   'labels': ['Punta Arenas'],
                                   'xlabel': False,
                                   'ylabel': False,
                                   'poes': True}, yrs=1)

axes.xaxis.set_minor_locator(LogLocator(base=10, subs=range(1, 10)))
axes.yaxis.set_minor_locator(LogLocator(base=10, subs=range(1, 10)))

plt.savefig('psha_south.png', dpi=200)
# plt.show()
# model.model2vti('test', 'hmaps_stats', ['PGA'], levels=[0.0021030],
#                 res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
#                 crop='../../shp/chile.shp')