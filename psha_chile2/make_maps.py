import numpy as np
import hazard

imtl = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}

model = hazard.hazardResults('Faults', './model_faults', 64)
model.parse_db(imtl)
model.get_maps_from_curves(['PGA'], [0.0021030, 0.0004])
model.get_stats('hmaps', 'PGA')
# model.model2vti('Faults', 'hmaps_stats', ['PGA'], levels=[0.0021030, 0.0004],
#                 res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
#                 crop='../../data/shapefiles/chile.shp')

#
imtl = {"PGA": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}

model2 = hazard.hazardResults('No_Faults', './model_nofaults', 1633)
model2.parse_db(imtl)
model2.get_maps_from_curves(['PGA'], [0.0021030, 0.0004])
model2.get_stats('hmaps', 'PGA')
# model2.model2vti('No_Faults', 'hmaps_stats', ['PGA'], levels=[0.0021030,  0.0004],
#                 res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
#                 crop='../../data/shapefiles/chile.shp')

abs_diff = model.hmaps_stats[:, :, :, :] - model2.hmaps_stats[:, :, :, :]
rel_diff = (model.hmaps_stats[:, :, :, :] - model2.hmaps_stats[:, :, :, :])/ model2.hmaps_stats[:, :, :, :]

model2.abs_diff_map = abs_diff
model2.rel_diff_map = rel_diff

model2.model2vti('abs_diff', 'abs_diff_map', ['PGA'], levels=[0.0021030, 0.0004],
                res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
                crop='../data/shapefiles/chile.shp')
model2.model2vti('rel_diff', 'rel_diff_map', ['PGA'], levels=[0.0021030, 0.0004],
                res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
                crop='../data/shapefiles/chile.shp')