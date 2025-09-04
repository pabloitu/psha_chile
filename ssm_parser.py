from os import makedirs
import geopandas as gpd
from os.path import join
import pickle
from functools import partial
import scipy.special as scp
import logging
import subprocess
import shutil
import shapely

import itertools
import scipy as sp
import time
import numpy as np
import random
import psutil
import scipy.stats as st
import os
import datetime
import matplotlib.pyplot as plt
from shutil import copyfile
import openquake
from PIL.JpegImagePlugin import get_sampling

from shapely.geometry import Polygon as shpPoly
from shapely.geometry import shape
from shapely.geometry import Point as shp_point
from openquake.hmtk.seismicity import selector
from openquake.hazardlib.geo.mesh import Mesh
from openquake.hazardlib.source.rupture import BaseRupture
from openquake.hazardlib.scalerel.point import PointMSR
from openquake.hazardlib.geo.geodetic import geodetic_distance
from openquake.hazardlib.source.non_parametric import NonParametricSeismicSource
from openquake.hazardlib.source.point import PointSource
from openquake.hazardlib.geo.utils import OrthographicProjection
from openquake.hazardlib.geo.point import Point as oq_point
from openquake.hazardlib.geo.surface import PlanarSurface
from openquake.hazardlib.geo.nodalplane import NodalPlane
from openquake.hazardlib.geo import Polygon as oqpoly
from openquake.hazardlib.pmf import PMF
from openquake.hazardlib.scalerel.point import PointMSR
from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
from openquake.hazardlib.mfd.evenly_discretized import EvenlyDiscretizedMFD
from openquake.hazardlib import sourcewriter, sourceconverter
from datetime import datetime as dt
from openquake.hazardlib.tom import PoissonTOM, NegativeBinomialTOM
import gc
from multiprocessing import Pool
import copy

chile_bbox = []


def unique_nodal_plane_dist(nodal_plane_distribution):

    new_npd = copy.deepcopy(nodal_plane_distribution)
    sdr = []  # [strike/dip/rake]
    weights = []

    for i in new_npd:
        sdr.append( (i['strike'], i['dip'], i['rake']))
        weights.append(i['probability'])


    unique, ind, inv, counts = np.unique(sdr, return_index=True, return_inverse=True, return_counts=True, axis=0)

    remove = np.setdiff1d(np.arange(len(new_npd)), ind)
    remove = np.sort(remove)

    count = 0
    for r in remove:
        new_npd.__delitem__(r - count)
        count += 1

    for i in range(len(new_npd)):
        new_npd[i]['probability'] *= counts[inv[i]]

    return new_npd

def simplify_point_source(node):

    new_node = copy.deepcopy(node)

    npd = new_node[4]

    weights = []
    for nodal_plane in npd:

        weights.append(nodal_plane['probability'])

    unique_index = np.argmax(weights)

    npd[0] = npd[unique_index]

    for i in range(len(npd) - 1):
        npd.__delitem__(1)

    npd[0]['probability'] = 1.0

    hpd = new_node[5]
    depths = [i['depth'] for i in hpd]
    probability = [i['probability'] for i in hpd]

    avg_depth = np.average(depths, weights=probability)

    hpd[0]['depth'] = avg_depth
    hpd[0]['probability'] = 1.0

    for i in range(len(hpd) - 1):
        hpd.__delitem__(1)


    return new_node

def get_sam_basemodel(simplify=True):

    path = 'psha_gem/ssm.xml'
    chile_shp = gpd.read_file('./shp/chile_buffer.shp')

    Model_original = openquake.hazardlib.nrml.read(path)
    ns = '{' + Model_original.attrib['xmlns'] + '}'
    sm = Model_original[0]
    ind = []

    ## Filter by Source Type (ignore fault sources)
    ps_xml = []
    sf_xml = []
    cf_xml = []
    for i, source in enumerate(sm):
        if source.tag.split(ns)[1] == 'pointSource':
            ps_xml.append(source)
        elif source.tag.split(ns)[1] == 'simpleFaultSource':
            sf_xml.append(source)
        elif source.tag.split(ns)[1] == 'complexFaultSource':
            cf_xml.append(source)


    conv = sourceconverter.SourceConverter()

    nodes_sf = [conv.convert_node(node) for node in sf_xml if node]
    nodes_cf = [conv.convert_node(node) for node in cf_xml if node]

    nodes_ps = []
    for node in ps_xml:
        node[4] = unique_nodal_plane_dist(node[4])

        if simplify:
            node = simplify_point_source(node)

        nodes_ps.append(conv.convert_node(node))


    nodes_sf_chile = []
    nodes_cf_chile = []
    nodes_ps_chile = []

    for source in nodes_sf:
        fault_trace_gdp = gpd.GeoDataFrame(
            geometry=[shp_point(i.longitude, i.latitude) for i in source.fault_trace.points], crs='4326')
        if len(chile_shp.sjoin(fault_trace_gdp, predicate='intersects').index) > 0:
            nodes_sf_chile.append(source)
    sourcewriter.write_source_model('./psha_chile/crustalfaults.xml', nodes_sf_chile, name=None, investigation_time=None)

    for source in nodes_cf:
        subduction_polygon = gpd.GeoDataFrame(
            geometry=[shp_point(i[0], i[1]) for i in source.polygon.coords], crs='4326')
        if len(chile_shp.sjoin(subduction_polygon, predicate='intersects').index) > 0:
            nodes_cf_chile.append(source)
    sourcewriter.write_source_model('./psha_chile/subduction.xml', nodes_cf_chile, name=None, investigation_time=None)

    point_coords =  gpd.GeoDataFrame(geometry=[shp_point(i.location.longitude, i.location.latitude) for i in nodes_ps], crs='4326')
    valid_idx = chile_shp.sjoin(point_coords, predicate='intersects').index_right
    for idx in valid_idx:
        nodes_ps_chile.append(nodes_ps[idx])
    sourcewriter.write_source_model('./psha_chile/pointsources.xml', nodes_ps_chile, name=None, investigation_time=None)
    return nodes_ps, nodes_ps_chile, nodes_sf, nodes_sf_chile, nodes_cf, nodes_cf_chile


output = get_sam_basemodel()

# chile_shp = gpd.read_file('./shp/chile_buffer.shp')
