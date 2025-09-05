import numpy as np
from matplotlib import pyplot as plt
import hazard

imtl = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}
model = hazard.hazardResults('test', './', 26)
model.parse_db(imtl)
a = model.get_maps_from_curves(['PGA'], [0.0021030, 0.000399999])
model.get_stats('hcurves', 'PGA')
model.get_stats('hmaps', 'PGA')

poi = np.array([-71.537, -33.062])
fig, axes = plt.subplots(1, 1, figsize=(16, 10))
#
model.plot_pointcurves('PGA', poi, ax=axes,
                        plot_args={'mean_c': 'red', 'mean_s': '-', 'stats_lw': 2,
                                   'xlims': [1e-2, 3],
                                   'ylims': [1e-5, 2],
                                   'poes': False}, yrs=1)
# plt.show()
model.model2vti('test', 'hmaps_stats', ['PGA'], levels=[0.0021030],
                res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
                crop='../../shp/chile.shp')