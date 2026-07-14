import numpy as np
from matplotlib import pyplot as plt
import hazard
import seaborn as sns

sns.set_style("darkgrid", {"ytick.left": True, 'xtick.bottom': True,"axes.facecolor": ".9", 'font.family': 'Ubuntu'})
imtl = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
model = hazard.hazardResults('test', './', 83)
model.parse_db(imtl)
a = model.get_maps_from_curves(['PGA'], [0.0021030, 0.000399999])
model.get_stats('hcurves', 'PGA')
model.get_stats('hmaps', 'PGA')
poi = np.array([-72.991, -45.357])

grid = model.grid
point = poi


point = np.argmin(np.sum((grid - point) ** 2, axis=1))

index_measure = np.argwhere(np.in1d(sorted(list(model.imtl.keys())), 'PGA')).ravel()[0]

print(point, index_measure)
# fig, axes = plt.subplots(1, 1, figsize=(12, 8))
# #
# ax = model.plot_pointcurves('PGA', poi, ax=axes,
#                        title='Hazard Puerto Aysén - PoE in 1 year',
#                         plot_args={'mean_c': 'red', 'mean_s': '-', 'stats_lw': 2,
#                                    'xlims': [1e-2, 3],
#                                    'ylims': [1e-5, 2],
#                                    'labels': ['Mean Hazard'],
#                                    'poes': False}, yrs=1)
# measure = 'PGA'
# q05 = model.hcurves_stats[point, 2, index_measure, :].T
# q95 = model.hcurves_stats[point, -1, index_measure, :].T
# ax.fill_between(model.imtl[measure], q05, q95,
#                              color='red', alpha=0.3, label='Epistemic Uncertainty ('
#                                                            '$95\%$)')
# ax.legend(loc='upper right', fontsize=14)
#
# ax.tick_params(which='major', axis='y', length=8, color='gray', width=0.5)
# ax.tick_params(which='minor', axis='y', length=4, color='gray', width=0.5)
# ax.grid(axis='y', which='major', linewidth=1)
# ax.grid(axis='y', which='minor', linewidth=0.4)
#
# ax.grid(axis='x', which='major', linewidth=1)
# ax.grid(axis='x', which='minor', linewidth=0.4)
# xlims = ax.get_xlim()
# ax.axhline(0.00205, linestyle='--', linewidth=0.8, color='black')
# ax.text(min(xlims) * 1.1, 0.00215, '$T_r = 475\,\mathrm{years}$', fontsize=12)
# ax.axhline(0.000404, linestyle='--', linewidth=0.8, color='black')
# ax.text(min(xlims) * 1.1, 0.000454, '$T_r = 2475\,\mathrm{years}$', fontsize=12)
#
# plt.savefig('aysen_envelope.png', dpi=300)
# plt.show()

#
# grid = model.grid
# point = poi
# if np.argwhere(np.all(np.isclose(grid, point), axis=1)).shape[0]:
#     print(np.isclose(grid, point))
#     point = np.argwhere(np.all(np.isclose(grid, point), axis=1))[0, 0]
# else:
#     point = np.argmin(np.sum((grid - point) ** 2, axis=1))
#
# index_measure = np.argwhere(np.in1d(sorted(list(model.imtl.keys())), 'PGA')).ravel()[0]
#
# imtl = model.imtl['PGA']
# mean = model.hcurves_stats[point, 0, index_measure, :].T
#
# fig  = plt.figure(figsize=(12, 8))
# plt.loglog(imtl, mean)
# plt.show()
#
# plt.xlim([1e-2, 3])
# plt.ylim([1e-5, 2])
#
# np.savetxt(
#     "aysen_hazard_unc.csv",
#     np.column_stack((imtl.ravel(),  mean.ravel(), q05.ravel(), q95.ravel())),
#     delimiter=",",
#     header="PGA, Mean - Yearly probability of exceedance, '0.05 quantile', "
#            "'0.95 quantile'",
#     comments="",
#     fmt="%.18e",
# )
model.model2vti('faults_new', 'hmaps_stats', ['PGA'], levels=[0.0021030, 0.000399999],
                res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
                crop='../../data/shapefiles/chile.shp')