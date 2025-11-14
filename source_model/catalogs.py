
import datetime
from datetime import datetime as dt

import fiona
import pandas
import numpy as np
from shapely.geometry import Polygon as Polygon_Shapely
import csep
from csep.core import regions
from csep.utils import time_utils

from openquake.hazardlib.geo import Polygon as Polygon_OQ
from openquake.hazardlib.geo import Point
from openquake.hmtk.seismicity import catalogue, selector
from openquake.hazardlib.geo.utils import OrthographicProjection

from source_model import paths


def cat_oq2csep(cat_oq, region=None):
    """
    Converts Openquake catalogs into pyCSEP format
    """
    times = cat_oq.get_decimal_time()
    year = times.astype(int)
    rem = times - year
    base = [dt(y, 1, 1) for y in year]
    datetimes = [b + datetime.timedelta(seconds=(b.replace(year=b.year + 1) - b).total_seconds() * r) for b, r in
              zip(base, rem)]

    out = []
    for n, time_i in enumerate(datetimes):
        event_tuple = (n,
                       csep.utils.time_utils.datetime_to_utc_epoch(time_i),
                       cat_oq['latitude'][n],
                       cat_oq['longitude'][n],
                       cat_oq['depth'][n],
                       np.round(cat_oq['magnitude'][n], 1)
                       )
        out.append(event_tuple)

    cat = csep.catalogs.CSEPCatalog(data=out, region=region, name=cat_oq.name)

    return cat


def get_cat_relocated(name='relocated', event_class=None):


    raw = pandas.read_csv(paths.relocated_classified)
    lon = raw['longitude'].to_numpy()
    lat = raw['latitude'].to_numpy()
    depth = raw['depth'].to_numpy()
    mag = raw['mag'].to_numpy().astype(float)

    id = raw['id']
    datetimes = [datetime.datetime.fromisoformat(i) for i in raw['time_iso']]

    year = np.array([i.year for i in datetimes])
    month = np.array([i.month for i in datetimes])
    day = np.array([i.day for i in datetimes])
    hour = np.array([i.hour for i in datetimes])
    min = np.array([i.minute for i in datetimes])
    sec = np.array([i.second for i in datetimes])
    cat = catalogue.Catalogue()
    cat.load_from_array(['eventID', 'year', 'month', 'day', 'hour', 'minute',
                         'second', 'longitude', 'latitude', 'depth', 'magnitude'],
                        np.vstack((id, year, month, day, hour, min, sec, lon, lat, depth, mag)).T)
    cat.update_end_year()
    cat.update_start_year()
    cat.sort_catalogue_chronologically()
    cat.name = name
    return cat


def get_cat_nz_dc(name=None):

    raw = np.genfromtxt(paths.cat_nz_dc, skip_header=1, delimiter=',')
    lon = raw[:, 6]
    lat = raw[:, 7]
    depth = raw[:, 8]
    mag = raw[:, 9]

    id = np.zeros(len(mag))
    year = raw[:, 0]
    month = raw[:, 1]
    day = raw[:, 2]
    hour = raw[:, 3]
    min = raw[:, 4]
    sec = raw[:, 5]
    cat = catalogue.Catalogue()
    cat.load_from_array(['eventID', 'year', 'month', 'day', 'hour', 'minute',
                         'second', 'longitude', 'latitude', 'depth', 'magnitude'],
                        np.vstack((id, year, month, day, hour, min, sec, lon, lat, depth, mag)).T)
    cat.update_end_year()
    cat.update_start_year()
    cat.sort_catalogue_chronologically()
    if name is None:
        cat.name = 'nz_dc'
    else:
        cat.name = name
    return cat


def filter_cat(cat, mws=(3.99, 10.0), depth=(40, -2),
               start_time=dt(1964, 1, 1),
               end_time=None, shapefile=None, circle=False):

    filter = selector.CatalogueSelector(cat)
    new_cat = filter.within_depth_range(*depth)
    filter = selector.CatalogueSelector(new_cat)
    new_cat = filter.within_magnitude_range(*mws)
    filter = selector.CatalogueSelector(new_cat)
    new_cat = filter.within_time_period(start_time=start_time, end_time=end_time)
    if shapefile:
        polygon = fiona.open(shapefile)
        shell_sphe = polygon[0]['geometry']['coordinates'][0]
        holes_sphe = polygon[0]['geometry']['coordinates'][1:]
        proj = OrthographicProjection.from_lons_lats(np.array([i[0] for i in shell_sphe]),
                                                     np.array([i[1] for i in shell_sphe]))
        shapely_poly = Polygon_Shapely(shell=np.array(proj(*np.array(shell_sphe).T)).T,
                       holes=[np.array(proj(*np.array(i).T)).T for i in holes_sphe])
        oq_poly = Polygon_OQ._from_2d(shapely_poly, proj)
        filter = selector.CatalogueSelector(new_cat)
        new_cat = filter.within_polygon(oq_poly)
    if circle:

        filter = selector.CatalogueSelector(new_cat)
        point = Point(circle[0][0], circle[0][1], 0)
        new_cat = filter.circular_distance_from_point(point, circle[1], distance_type='epicentral')

    new_cat.update_end_year()
    new_cat.update_start_year()
    new_cat.sort_catalogue_chronologically()

    return new_cat


if __name__ == "__main__":

    a = get_cat_relocated()