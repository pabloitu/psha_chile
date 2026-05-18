import numpy as np
import hazard

imtl = {"SA(0.2)": np.logspace(np.log10(0.0005), np.log10(3.00), 25)}

model = hazard.hazardResults('Faults_sa', './model_faults_sa', 1635)
model.parse_db(imtl)
model.get_maps_from_curves(['SA(0.2)'], [0.0021030, 0.0004])
model.get_stats('hmaps', 'SA(0.2)')
model.model2vti('Faults', 'hmaps_stats', ['SA(0.2)'], levels=[0.0021030, 0.0004],
                res=(0.01, 0.01), res_method='nearest', crs_f='EPSG:4326',
                crop='../data/shapefiles/chile.shp')
