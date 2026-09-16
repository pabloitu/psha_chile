from os import makedirs
from os.path import join
import pickle
import h5py
from functools import partial
import fiona
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

from shapely.geometry import Polygon as shpPoly
from shapely.geometry import shape
from shapely.geometry import shape, mapping, Point

from openquake.hmtk.seismicity import selector
from openquake.hazardlib.geo.mesh import Mesh
from openquake.hazardlib.source.rupture import BaseRupture
from openquake.hazardlib.scalerel.point import PointMSR
from openquake.hazardlib.geo.geodetic import geodetic_distance
from openquake.hazardlib.source.non_parametric import NonParametricSeismicSource
from openquake.hazardlib.source.point import PointSource
from openquake.hazardlib.geo.utils import OrthographicProjection
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

from pyproj import Proj, transform, Transformer
import vtk
from vtk import vtkImageData
from vtkmodules.util.numpy_support import numpy_to_vtk
import rasterio
import rasterio.mask
import pandas
import geopandas

from osgeo import gdal
import pyvista

def get_oqcalc(num, folder=None):

    if folder:
        h5_path = join(folder, 'calc_%i.hdf5' % num)
    else:
        h5_path = join('/home/pciturri/oqdata/', 'calc_%i.hdf5' % num)
    return h5_path


def parse_raster(fname, offset=0):
    from osgeo import gdal
    raster = gdal.Open(fname)
    affine = raster.GetGeoTransform()
    dims = (raster.RasterXSize + 1 , raster.RasterYSize + 1, 1)
    spacing = (affine[1], -affine[5], 0)
    origin = (affine[0], affine[3] - spacing[1]*dims[1], offset)

    return raster, affine, dims, spacing, origin


def reproject_coordinates(array, crs_0, crs_f):

    transformer = Transformer.from_crs(crs_0, crs_f, always_xy=True)
    x, y = transformer.transform(array[:, 0], array[:, 1])
    reprojected = np.vstack((x, y)).T

    return reprojected


def mask_raster(shapefile, input_fn, output_fn, all_touched=False,
                crop=False):
    """
    Mask a raster (.tiff) using a Polygon shapefile. Both should be in the
    same CRS

    Input:  -shapefile(str):    Path of the shapefile
            -input_fn(str):     Path of the input raster to crop
            -output_fn(str):    Path of the results raster
            -all_touched(bool): Include (or not) pixels that falls within the
                                polygon's boundaries
            -crop(bool):        Crop the results raster bounds down to the
                                shapefile boundaries
    """

    with fiona.open(shapefile, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
    with rasterio.open(input_fn) as src:
        out_meta = src.meta
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=crop,
                                                      all_touched=all_touched)
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open(output_fn, "w", **out_meta) as dest:
        dest.write(out_image)


def write_vtk(fname, vti_data):

    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(fname)
    writer.SetCompressorTypeToZLib()
    writer.SetDataModeToAppended()
    writer.SetInputData(vti_data)
    writer.Write()


def rasters2vti(fname_vti, rasters, names,
               offset=0, nodata_val=-9999):
    """
    Creates 2D vtkImage. All rasters must be in the same
    projection, extent and dimension.

    Input:  fname_vti(str):  Filename of the results vti file
            rasters(list): list of string, pointing the rasters to be casted
                           onto the vtk
            arrays_names(list): List of lists of strings. Each sublists contains
                        the array names of each raster band.
                        e.g. [['PGA_a','SA(0.1)'_a], ['PGV_b','SA(0.4)'_b]]
            offset (int): Vertical elevation upon which to cast the vti.
            nodata_val(float): Nodata value of the raster
            mask_rgb(list of int): Color value to set transparency

    Last mod. 07/08/2020
    """


    _, affine, dims, spacing, origin = parse_raster(rasters[0], offset)
    image_data = vtkImageData()
    image_data.SetDimensions(*dims)
    image_data.SetOrigin(*origin)
    image_data.SetSpacing(*spacing)




    for raster_path, name in zip(rasters, names):
        raster, *_ = parse_raster(raster_path, offset)
        n_bands = raster.RasterCount
        mask = None
        Array = []
        for i in range(n_bands):
            array = np.flipud(raster.GetRasterBand(i + 1). \
                              ReadAsArray()).flatten(order='C')
            array[array == nodata_val] = np.nan
            Array.append(array)
            if i == 0:
                mask = np.isnan(array)

            else:
                mask += np.isnan(array)
        Array = np.ascontiguousarray(np.array(Array).T)
        vtk_array = numpy_to_vtk(Array, deep=True,
                                 array_type=vtk.VTK_FLOAT)
        vtk_array.SetName(name)
        image_data.GetCellData().AddArray(vtk_array)
    vtk_mask = numpy_to_vtk(1 - mask.ravel() * 1, deep=True,
                            array_type=vtk.VTK_INT)
    vtk_mask.SetName('mask')
    image_data.GetCellData().AddArray(vtk_mask)
    write_vtk(fname_vti, image_data)


def hazard_model2raster(array, storedir, filename, grid, res, srs='EPSG:4326'):
    """
    Rasterize point attributes into a multi-band GeoTIFF.
    Each band i burns array[:, i] at the pixel containing each (snapped) point.
    Pixels not hit by any point are set to -9999.
    """
    import math
    import numpy as np
    import pandas
    import geopandas
    from shapely.geometry import Point
    from os.path import join
    from osgeo import ogr, gdal, osr

    shp_fn = join(storedir, filename + '.GeoJSON')
    raster_fn = join(storedir, filename + '.tiff')

    # --- 0) Setup & snap coordinates to avoid float drift ---
    px, py = float(res[0]), float(res[1])

    # pick decimal rounding based on resolution (e.g., 0.01 -> 2 decimals)
    def decimals_for_step(step):
        # allow one extra decimal to be safe when step is like 0.1, 0.25, etc.
        if step == 0:
            return 8
        d = int(max(0, round(-math.log10(abs(step))) + 2))
        return min(12, d)

    dec_x = decimals_for_step(px)
    dec_y = decimals_for_step(py)

    # snap each input coordinate to the nearest px/py grid using rounding
    # (this makes centers *exactly* repeatable and aligned)
    snap_x = np.round(grid[:, 0], dec_x)
    snap_y = np.round(grid[:, 1], dec_y)

    # --- 1) Write points (GeoJSON) using snapped coordinates ---
    df = pandas.DataFrame(array, columns=[str(i) for i in range(array.shape[1])])
    gdf = geopandas.GeoDataFrame(
        df,
        crs=srs,
        geometry=[Point(xy) for xy in zip(snap_x, snap_y)]
    )
    gdf.to_file(shp_fn, driver='GeoJSON')

    # --- 2) Build raster geometry from unique snapped centers ---
    ux = np.unique(snap_x.astype(float))
    uy = np.unique(snap_y.astype(float))
    ux.sort()
    uy.sort()

    cols = int(len(ux))
    rows = int(len(uy))

    # geotransform: top-left *corner*; we want centers to be ux[j] / uy[i]
    # so origin must be half a pixel "outside" the first/last centers
    origin_x = ux[0] - px / 2.0     # left edge left of first center
    origin_y = uy[-1] + py / 2.0    # top edge above top center (max Y)

    # (Optional) sanity checks: ensure grid spacing matches res
    # If these asserts fail, your input isn't a rectilinear grid at the given res.
    print(np.diff(ux))
    print(px)
    # if cols > 1:
    #     if not np.allclose(np.diff(ux), px, rtol=0, atol=8**(-dec_x)):
    #         raise ValueError("X coordinates are not on uniform spacing equal to res[0].")
    # if rows > 1:
    #     if not np.allclose(np.diff(uy), py, rtol=0, atol=8**(-dec_y)):
    #         raise ValueError("Y coordinates are not on uniform spacing equal to res[1].")

    # --- 3) Create raster ---
    target_ds = gdal.GetDriverByName('GTiff').Create(
        raster_fn, cols, rows, array.shape[1], gdal.GDT_Float32
    )
    target_ds.SetGeoTransform((origin_x, px, 0.0, origin_y, 0.0, -py))

    srs_obj = osr.SpatialReference()
    srs_obj.ImportFromEPSG(int(str(srs).split(':')[-1]))
    target_ds.SetProjection(srs_obj.ExportToWkt())

    # init bands to NoData
    for i in range(array.shape[1]):
        band = target_ds.GetRasterBand(i + 1)
        band.SetNoDataValue(-9999)
        band.Fill(-9999)

    # --- 4) Rasterize attributes (one band per column) ---
    source_ds = ogr.Open(shp_fn)
    source_layer = source_ds.GetLayer()

    # schema (expects string field names "0","1",... from the DataFrame)
    schema = []
    ldefn = source_layer.GetLayerDefn()
    for n in range(ldefn.GetFieldCount()):
        schema.append(ldefn.GetFieldDefn(n).GetName())

    for i in range(array.shape[1]):
        gdal.RasterizeLayer(
            target_ds,
            [i + 1],
            source_layer,
            options=[f'ATTRIBUTE={schema[i]}']  # write field values into the pixel containing the (snapped) point
        )

    # cleanup
    target_ds = None
    source_ds = None
    return shp_fn, raster_fn


def basemap2vti(fname_vti, raster,
                offset=0, mask_rgb=[0, 0, 0]):
    """
    Creates 2D vtkImage. All rasters must be in the same
    projection, extent and dimension.

    Input:  fname_vti(str):  Filename of the results vti file
            rasters(list): list of string, pointing the rasters to be casted
                           onto the vtk
            arrays_names(list): List of lists of strings. Each sublists contains
                        the array names of each raster band.
                        e.g. [['PGA_a','SA(0.1)'_a], ['PGV_b','SA(0.4)'_b]]
            offset (int): Vertical elevation upon which to cast the vti.
            nodata_val(float): Nodata value of the raster
            mask_rgb(list of int): Color value to set transparency

    Last mod. 07/08/2020
    """

    raster = gdal.Open(raster)

    affine = raster.GetGeoTransform()
    dims = (raster.RasterXSize + 1, raster.RasterYSize + 1, 1)
    spacing = (affine[1], -affine[5], 0)
    origin = (affine[0], affine[3] - spacing[1] * dims[1], offset)

    image = pyvista.ImageData(dimensions=dims, spacing=spacing, origin=origin)

    r = np.flipud(np.abs(raster.GetRasterBand(1).ReadAsArray())).flatten(order='C')
    g = np.flipud(np.abs(raster.GetRasterBand(2).ReadAsArray())).flatten(order='C')
    b = np.flipud(np.abs(raster.GetRasterBand(3).ReadAsArray())).flatten(order='C')

    rgb = np.ascontiguousarray(np.vstack((r, g, b)).T)
    dim = rgb.astype('uint16').max(0) + 1
    mask = np.in1d(np.ravel_multi_index(rgb.T, dim),
                   np.ravel_multi_index(np.array(mask_rgb).T,
                                        dim)).astype('int')
    image.cell_data["basemap"] = rgb
    image.cell_data["mask"] = mask
    image.save(fname_vti)

    return image


class hazardResults(object):

    def __init__(self, name, path, calcpath=None):

        self.name = name
        self.path = path
        print(path)
        self.calcpath = calcpath
        if path:
            self.dirs = {'input': join(path, 'input'),
                         'output': join(path, 'output'),
                         'vti': join(path, 'vti'),
                         'figures': join(path, 'figures')}

        if isinstance(calcpath, int):
            self.calcpath = get_oqcalc(calcpath)
        elif calcpath is None:
            files = list(os.walk(self.dirs['output']))[0][2]
            calcs = [i for i in files if 'calc' in i]
            ids = [int(i.split('_')[1].split('.')[0]) for i in calcs]
            self.calcpath = join(self.dirs['output'], calcs[int(np.argmax(ids))])


        # Initialize class atritubtes
        self.ns = None  # Number of sites
        self.nb = None  # Number of branches
        self.ni = None  # Number of intensity measures
        self.nl = None  # Number of intensity measure levels
        self.nps = 0  # Number of intensity measure poes

        self.trt = []  # Tectonic region types
        self.gmpe_lt = {}  # Idem for the GMPE logic tree
        self.sm_lt = {}  # Creates a simplified structure for a source model logic tree
        self.branches = None  # Branch id, components and weight of each realization

        self.grid = None  # 2D np array
        self.hmaps = None  # 4D np array, containing geofft_hazard maps
        self.hcurves = None  # 4D h5py database , containing geofft_hazard curves
        self.immp = {}
        self.imtl = {}

        self.hmaps_stats = None  # Mean, 0.1q, 0.15q, 0.25q, 0.5q (median), 0.75q, 0.85q, 0.9q
        self.hcurves_stats = None

    def parse_db(self, imtl):
        db = h5py.File(self.calcpath, 'r')
        try:
            shape = db['hcurves-rlzs'].shape
        except:
            shape = db['hcurves-stats'].shape
        self.ns = shape[0]
        self.nb = shape[1]
        self.ni = shape[2]
        self.nl = shape[3]

        self.grid = np.stack((db['sitecol']['lon'], db['sitecol']['lat'])).T
        self.sm_lt = [(sm[1], sm[4]) for sm in db['full_lt']['source_model_lt']]
        self.trt = np.unique([tr[0] for tr in db['full_lt']['gsim_lt']])
        self.gsim_lt = {tr: [(br[2], br[3])
                             for br in db['full_lt']['gsim_lt']
                                   if (br[0] == tr)] for tr in self.trt}

        branch_components = itertools.product([sm[0] for sm in self.sm_lt], *[[i[0] for i in j]
                                                                  for j in self.gsim_lt.values()])
        branch_weights = db['weights'][:]
        self.branches = [(n, comp, w) for n, comp, w in zip(range(self.nb), branch_components, branch_weights)]
        try:
            self.hcurves = db['hcurves-rlzs']
        except:
            self.hcurves = db['hcurves-stats']
        self.hmaps = np.zeros((self.ns, self.nb, self.ni, 0))

        #todo automatize
        if imtl:
            self.imtl = imtl
        else:
            imtls = [i for i in db['oqparam'] if 'hazard_imtls' in i[0].decode('utf-8')]
            self.imtl = {i[0].decode('utf-8').split('.')[-1]: np.array(eval(i[1])) for i in imtls}

        # self.hmaps = db['hmaps-rlzs'][:]
        # self.immp = {i: np.array([0.002105]) for i in self.imtl.keys()}  #todo automatize
        # self.nps = 1


    @staticmethod
    def compute_hazard_maps(A):
        """
        Modification of openquake.commonlib.calc.compute_hazard_maps() for efficiency
        """
        EPSILON = 1E-30

        curves, log_imls, log_poes = A[0], A[1], A[2]
        P = len(log_poes)

        N, L = curves.shape  # number of levels

        if L != len(log_imls):
            raise ValueError('The curves have %d levels, %d were passed' %
                             (L, len(log_imls)))

        hmap = np.zeros((N, P))

        for n, curve in enumerate(curves):
            # the geofft_hazard curve, having replaced the too small poes with EPSILON
            log_curve = np.log([max(poe, EPSILON) for poe in curve[::-1]])
            for p, log_poe in enumerate(log_poes):
                hmap[n, p] = np.exp(np.interp(log_poe, log_curve, log_imls))
        return hmap

    def get_maps_from_curves(self, measures, poes, nproc=16):

        if isinstance(poes, (float, int, list)):
            poes = np.array([poes]).ravel()

        self.hmaps = np.zeros((self.ns, self.nb, self.ni, len(poes)))

        index_measure = list(range(self.ni))
        self.immp = {measure: np.zeros(0) for measure in measures}

        t0 = time.time()

        for ind, measure in zip(index_measure, measures):
            pool = Pool(nproc)
            log_poes = np.log(poes)
            log_levels = np.log(np.array(self.imtl[measure][::-1]))
            A = pool.map(self.compute_hazard_maps, [(i, log_levels, log_poes) for i in self.hcurves[:, :, ind, :]])
            pool.close()

            t1 = time.time()
            print(f'Processing {self.name} maps in: {t1-t0} seconds')
            self.immp[measure] = np.append(self.immp[measure], poes)
            map = np.array(A)
            self.hmaps[:,:,ind, :] = map.reshape(self.ns, self.nb, len(poes))
        self.nps = len(poes)
        #                        map.reshape(self.ns, self.nb, 1, len(poes)), axis=-1)
        # self.nps += len(poes)

        # measure_new_array = np.copy(self.hmaps)
        # map = np.array(A).reshape((self.ns, self.nb, len(poes)))
        # new_array = np.append(measure_new_array[:, :, index_measure, :], map, axis=-1)
        # measure_new_array[:, :, index_measure, :] = new_array.reshape((self.ns, self.nb, 1, len(poes)))
        # print(new_array.shape,
        #       'aaa')  # self.hmaps[:,:,index_measure,:]  # self.hmaps = np.append(self.hmaps[:, :, index_measure, :],  # map.reshape(self.ns, self.nb, 1, len(poes)), axis=-1)  # self.nps += len(poes)

    @staticmethod
    def log_interp1d(x, xx, yy, kind='linear', axis=-1):
        lin_interp = sp.interpolate.interp1d(np.log10(xx), np.log10(yy), axis=axis, kind=kind, fill_value='extrapolate')
        log_interp = lambda zz: np.power(10.0, lin_interp(np.log10(zz)))
        interp = log_interp(x)

        return interp

    @staticmethod
    def quantile_curve(quantile, curves, weights=None):
        """
        Modification of openquake.hazardlib.stats.quantile_curve() for efficiency
        """

        R = len(curves)
        if weights is None:
            weights = np.ones(R) / R
        else:
            weights = np.array(weights)
            assert len(weights) == R, (len(weights), R)
        result = np.zeros((len(quantile), *curves.shape[1:]))
        for idx, _ in np.ndenumerate(np.zeros(curves.shape[1:])):
            data = curves[:, idx[0], idx[1]]
            sorted_idxs = np.argsort(data)
            cum_weights = np.cumsum(weights[sorted_idxs])
            result[:, idx[0], idx[1]] = np.interp(quantile, cum_weights, data[sorted_idxs])
        return result

    @staticmethod
    def geometric_mean(a, axis=0, dtype=None, weights=None):

        if not isinstance(a, np.ndarray):
            log_a = np.log(np.array(a, dtype=dtype))
        elif dtype:
            # Must change the default dtype allowing array type
            if isinstance(a, np.ma.MaskedArray):
                log_a = np.log(np.ma.asarray(a, dtype=dtype))
            else:
                log_a = np.log(np.asarray(a, dtype=dtype))
        else:
            log_a = np.log(a)

        if weights is not None:
            weights = np.asanyarray(weights, dtype=dtype)
        return np.exp(np.average(log_a, axis=axis, weights=weights))

    def get_stats(self, attr, measure):

        # Stats >  hmaps_stats, hcurves_stats

        # 0 arithmetic mean
        # 1 geometric mean
        # 2 0.1 quantile
        # 3 0.25 quantile
        # 4 median
        # 5 0.75 quantile
        # 6 0.9 quantile

        if attr == 'hcurves':
            pointer = self.imtl
            if self.hcurves_stats is None:
                self.hcurves_stats = np.zeros((self.ns, 7, self.ni, self.nl))
            Stats = self.hcurves_stats

        elif attr == 'hmaps':
            pointer = self.immp
            if self.hmaps_stats is None:
                self.hmaps_stats = np.zeros((self.ns, 7, self.ni, self.nps))
            Stats = self.hmaps_stats

        t0 = time.time()
        print(pointer, measure)
        measure_ind = np.argwhere(np.in1d(sorted(list(pointer.keys())), measure)).ravel()[0]
        levels_ind = np.arange(0, len(pointer[measure]))

        # Arithmetic mean
        # print(len([i[2] for i in self.branches]), getattr(self, attr).shape)
        mean = np.average(getattr(self, attr)[:, :, measure_ind, levels_ind],
                          weights=[i[2] for i in self.branches], axis=1)
        Stats[:, 0, measure_ind, :] = mean

        # Geometric mean
        geom_mean = self.geometric_mean(getattr(self, attr)[:, :, measure_ind, levels_ind],
                                   weights=[i[2] for i in self.branches], axis=1)
        Stats[:, 1, measure_ind, :] = geom_mean

        qs = np.array([0.1, 0.25, 0.5, 0.75, 0.9])
        q = self.quantile_curve(qs, np.swapaxes(getattr(self, attr)[:, :, measure_ind, levels_ind], 0, 1),
                           weights=[i[2] for i in self.branches])
        Stats[:, 2:, measure_ind, :] = np.swapaxes(q, 0, 1)
        t1 = time.time()
        if attr == 'hcurves':
            self.hcurves_stats = Stats

        elif attr == 'hmaps':
            self.hmaps_stats = Stats
        print('Processing stats in: %.1f seconds' % (t1 - t0))

    def plot_pointcurves(self, measure, point, ax=None, title=None, plot_args={}, filename=None, yrs=None):
        xlims = plot_args.get('xlims', [1e-2, 1.5])
        ylims = plot_args.get('ylims', [1e-3, 1.2])
        poes_label = plot_args.get('poes', False)
        plot_branches = plot_args.get('plot_branches', False)
        plot_mean = plot_args.get('plot_mean', True)
        plot_geomean = plot_args.get('plot_geomean', False)
        plot_median = plot_args.get('plot_median', False)
        plot_quantile = plot_args.get('plot_quantile', False)
        plot_env = plot_args.get('plot_env', False)
        branches_lw = plot_args.get('branches_lw', 0.05)
        branches_c = plot_args.get('branches_c', 'steelblue')
        branches_alpha = plot_args.get('branches_alpha', 0.1)
        stats_lw = plot_args.get('stats_lw', 2)
        mean_c = plot_args.get('mean_c', 'steelblue')
        mean_s = plot_args.get('mean_s', '-')
        geomean_c = plot_args.get('geomean_c', 'green')
        geomean_s = plot_args.get('geomean_s', '-')
        median_c = plot_args.get('median_c', 'green')
        median_s = plot_args.get('median_s', '-')
        quantile_c = plot_args.get('quantile_c', 'gold')
        quantile_s = plot_args.get('quantile_s',  '--')
        env_c = plot_args.get('env_c', 'steelblue')
        env_alpha = plot_args.get('env_alpha', 0.3)
        labels = plot_args.get('labels', None)  # branch, am, gm, med, q, env:  Labels
        xlabel = plot_args.get('xlabel', None)
        ylabel = plot_args.get('ylabel', None)
        legend = plot_args.get('legend', None)
        if labels is None:
            labels = [self.name]
        else:
            if not isinstance(labels, list):
                labels = [self.name]
        print(labels)
        index_measure = np.argwhere(np.in1d(sorted(list(self.imtl.keys())), measure)).ravel()[0]
        if np.argwhere(np.all(np.isclose(self.grid, point), axis=1)).shape[0]:
            print(np.isclose(self.grid, point))
            point = np.argwhere(np.all(np.isclose(self.grid, point), axis=1))[0, 0]
        else:
            point = np.argmin(np.sum((self.grid - point) ** 2, axis=1))




        title = title if title else '%s - $x=(%.1f,%.1f)$' % (self.name, self.grid[point, 0], self.grid[point, 1])

        if ax is None:
            fig, ax = plt.subplots()

        ax.set_title(title, fontsize=16)

        if plot_branches:
            ax.loglog(self.imtl[measure], self.hcurves[point, :, index_measure, :].T,
                       linewidth=branches_lw, alpha=branches_alpha, color=branches_c, label=labels.pop(0))
        if plot_mean:
            ax.loglog(self.imtl[measure], self.hcurves_stats[point, 0, index_measure, :].T,
                       linewidth=stats_lw, color=mean_c, linestyle=mean_s, label=labels.pop(0))
        if plot_geomean:
            ax.loglog(self.imtl[measure], self.hcurves_stats[point, 1, index_measure, :].T,
                       linewidth=stats_lw, linestyle=geomean_s, color=geomean_c, label=labels.pop(0))
        if plot_median:
            ax.loglog(self.imtl[measure], self.hcurves_stats[point, 4, index_measure, :].T,
                       linewidth=stats_lw, linestyle=median_s, color=median_c, label=labels.pop(0))
        if plot_quantile:
            ax.loglog(self.imtl[measure], self.hcurves_stats[point, 2, index_measure, :].T,
                       linewidth=stats_lw, linestyle=quantile_s, color=quantile_c, label=labels.pop(0))
            ax.loglog(self.imtl[measure], self.hcurves_stats[point, -1, index_measure, :].T,
                       linewidth=stats_lw, linestyle=quantile_s, color=quantile_c)

        if plot_env:
            ax.fill_between(self.imtl[measure], self.hcurves_stats[point, 2, index_measure, :].T,
                             self.hcurves_stats[point, -1, index_measure, :].T,
                             color=env_c, alpha=env_alpha, label=labels[5])

        if not xlims:
            xlims = [min(self.imtl[measure]), max(self.imtl[measure])]

        ax.set_xlim(xlims)
        if ylims:
            ax.set_ylim(ylims)

        if poes_label == True:
            if yrs == 50:
                ax.axhline(0.1, linestyle='--', linewidth=0.8, color='black')
                ax.text(min(xlims)*1.1, 0.102, '10% in ' + '50 yr.', fontsize=12)
                ax.axhline(0.02, linestyle='--', linewidth=0.8, color='black')
                ax.text(min(xlims)*1.1, 0.0202, '2% in '+'50 yr.', fontsize=12)
            elif yrs == 1:
                ax.axhline(0.00205, linestyle='--', linewidth=0.8, color='black')
                ax.text(min(xlims)*1.1, 0.00215, '10% in ' + '50 yr.', fontsize=12)
                ax.axhline(0.000404, linestyle='--', linewidth=0.8, color='black')
                ax.text(min(xlims)*1.1, 0.000454, '2% in '+'50 yr.', fontsize=12)
        if xlabel is False:
            ax.set_xlabel(f'{measure} $[g]$', fontsize=14)

        if ylabel is False:
            if yrs:
                ylabel = 'Probability of exceedance - %i years' % yrs
            else:
                ylabel = 'Probability of exceedance'

            ax.set_ylabel(ylabel, fontsize=14)

        if legend:
            ax.legend(loc='upper right', fontsize=14)
        if filename:
            plt.savefig(join(self.dirs['figures'], filename), dpi=300)
        return ax


    def get_map_histogram(self, point, title=None, measure='PGA', poe=0.002105, weighted=False,
                          bins=50, plot=False, color='steelblue', lw=0.2, alpha=0.7, filename=False):

        if isinstance(point, int):
            point = point
        else:
            point = np.argwhere(np.all(np.isclose(self.grid, point), axis=1))[0, 0]
        index_measure = np.argwhere(np.in1d(sorted(list(self.immp.keys())), measure)).ravel()[0]
        index_poe = np.argwhere(self.immp[measure] == poe).ravel()[0]

        distribution = self.hmaps[point, :, index_measure, index_poe]

        if weighted:
            weights = np.array([i[2] for i in self.branches])
            med = self.hmaps_stats[point, 4, index_measure, index_poe]
            mean = self.hmaps_stats[point, 0, index_measure, index_poe]
            quart_1 = self.hmaps_stats[point, 3, index_measure, index_poe]
            quart_3 = self.hmaps_stats[point, 5, index_measure, index_poe]
        else:
            weights = None
            med = np.median(distribution)
            mean = np.mean(distribution)
            quart_1 = np.quantile(distribution, 0.25)
            quart_3 = np.quantile(distribution, 0.75)

        if plot:
            bin_cutoffs = np.linspace(0, 1.1 * np.percentile(distribution, 99), bins)
            plt.hist(distribution, density=True,
                     color=color, bins=bin_cutoffs, linewidth=lw, alpha=alpha, weights=weights)
            plt.axvline(med, linestyle='-', color='purple', label='Median')
            plt.axvline(mean, linestyle='-', color='green', label='Arithmetic mean')
            plt.axvline(quart_1, linestyle='--', color='orange', label='1st and 3rd Quartiles')
            plt.axvline(quart_3, linestyle='--', color='orange')

            plt.ylabel('Probability Density', fontsize=14)
            plt.xlabel('$\mathrm{%s}_{\mathrm{PoE}=%s}$' % (measure, str(poe)), fontsize=14)
            plt.legend()
            plt.xlim(0, np.percentile(distribution, 99))
            plt.title(title, fontsize=16)
            if filename:
                plt.savefig(join(self.dirs['figures'], filename), dpi=300)
            plt.show()
        histogram = np.histogram(distribution,
                                 range=(np.nanmin(distribution), np.nanmax(distribution)),
                                 bins=bins, density=True)

        bins = histogram[1]
        Hist = histogram[0]

        return Hist, bins, distribution

    def get_curve_histogram(self, point, title=None, measure='PGA', level=0.1, weighted=False,
                            bins=50, plot=False, color='steelblue', lw=0.2, alpha=0.7, filename=False):

        if isinstance(point, int):
            point = point
        else:
            point = np.argwhere(np.all(np.isclose(self.grid, point), axis=1))[0, 0]
        index_measure = np.argwhere(np.in1d(sorted(list(self.imtl.keys())), measure)).ravel()[0]
        index_level = np.argwhere(self.imtl[measure] == level).ravel()[0]

        distribution = self.hcurves[point, :, index_measure, index_level]

        if weighted:
            weights = np.array([i[2] for i in self.branches])
            med = self.hcurves_stats[point, 4, index_measure, index_level]
            mean = self.hcurves_stats[point, 0, index_measure, index_level]
            quart_1 = self.hcurves_stats[point, 3, index_measure, index_level]
            quart_3 = self.hcurves_stats[point, 5, index_measure, index_level]

        else:
            weights = None
            med = np.median(distribution)
            mean = np.mean(distribution)
            quart_1 = np.quantile(distribution, 0.25)
            quart_3 = np.quantile(distribution, 0.75)

        if plot:
            bin_cutoffs = np.linspace(0, 1.1 * np.percentile(distribution, 99), bins)
            plt.hist(distribution, density=True,
                     color=color, bins=bin_cutoffs, linewidth=lw, alpha=alpha, weights=weights)
            plt.axvline(med, linestyle='-', color='purple', label='Median')
            plt.axvline(mean, linestyle='-', color='green', label='Arithmetic mean')
            plt.axvline(quart_1, linestyle='--', color='orange', label='1st and 3rd Quartiles')
            plt.axvline(quart_3, linestyle='--', color='orange')

            plt.ylabel('Probability Density', fontsize=14)
            plt.xlabel('$\mathrm{PoE}_{\mathrm{%s}=%s}$' % (measure, str(level)), fontsize=14)
            plt.legend()
            plt.xlim(0, np.percentile(distribution, 99))
            plt.title(title, fontsize=16)
            if filename:
                plt.savefig(join(self.dirs['figures'], filename), dpi=300)
            plt.show()
        histogram = np.histogram(distribution,
                                 range=(np.nanmin(distribution), np.nanmax(distribution)),
                                 bins=bins, density=True)

        bins = histogram[1]
        Hist = histogram[0]

        return Hist, bins, distribution

    def model2vti(self, filename, attr, measures, levels=None,
                  branches=None, res=None, res_method='nearest', crs_f='EPSG:4326', crop=False):
        """
        Complete method to create a VTK 2D image to read in Paraview from class attributes.
        Calls a data_structure organizer to pre-arrange the data, in a readable format.
        Returns raster and shapefiles as intermediate step

        :param filename: (str) Name of the produced output files. No extension is needed
        :param attribute: (str)  Name of the class attribute (e.g. 'hazard_maps', 'hazard_curves', 'quantiles', 'mean'
        :param measure: (str) Intensity measure, e.g. 'PGA', 'SA0.1', 'SA1', etc.
        :param levels: (float/str/list) Levels (intensity levels, or poes, depending if maps/curves are flagged)
        :param structure_type (str): Organization of data
        :param id_elements (str/int/list): Elements to be plotted. In case of structure_type 'bylevel',
                        returns data structured by branch, etc. see e.g.: get_datastruct_bybranch()
        :param res_0 (tuple/list):  Resolution of the original crs_0, or input data. Default: min grid distance
        :param res_i: (tuple/list): Exporting resolution in crs_i. Default: res_0
        :param log:  (not implemented) log of variables
        :param bounds: Bounding box of the output raster/image
        :param resample: Method on which doing resample

        :param crs_0:  Coordinate reference system of the initial data. Usually same as OQ: epsg:4326
        :param crs_f:  Output of the raster and vti images

        :return:
        Creates as intermediate step, a GeoJSON file, a GeoTiff file with multi-band corresponding to all data arrays,
        and a .vti image, to be loaded in ParaView

        """

        from osgeo import gdal



        if isinstance(measures, str):
            measures = [measures]
        if isinstance(levels, float):  # Supports only same shape of levels for all measures
            levels = np.array([levels])
        else:
            levels = np.array(levels)

        if 'curve' in attr:
            pointer = self.imtl
        elif 'map' in attr:
            pointer = self.immp

        measure_ind = np.argwhere(np.in1d(sorted(list(pointer.keys())), measures)).ravel()
        levels_ind = np.argwhere(np.in1d(pointer[measures[0]], levels)).ravel()
        names = ['_'.join([str(j) for j in i]) for i in list(itertools.product(measures, levels))]
        indexes = list(itertools.product(measure_ind, levels_ind))

        if branches is None:
            data = [getattr(self, attr)[:, :, i, j] for i, j in indexes]

        elif isinstance(branches, (np.ndarray, list, range, int)):
            data = [getattr(self, attr)[:, np.array(branches), i, j] for i, j in indexes]


        # Reproject grid
        # if crs_f != 'EPSG:4326':
        #     grid = geo.reproject_coordinates(self.grid, 'EPSG:4326', crs_f)
        # else:
        #     grid = self.grid
        #
        # res_x = np.min(np.diff(np.unique(np.sort(grid[:, 0]))))
        # res_y = np.min(np.diff(np.unique(np.sort(grid[:, 1]))))
        # res0 = (res_x, res_y)

        if crs_f == 'EPSG:4326':
            grid = self.grid
            res_x = np.min(np.diff(np.unique(np.sort(self.grid[:, 0]))))
            res_y = np.min(np.diff(np.unique(np.sort(self.grid[:, 1]))))
            res0 = (res_x, res_y)

        else:
            grid = reproject_coordinates(self.grid, 'EPSG:4326', crs_f)
            res_x = np.min(np.diff(np.unique(np.sort(self.grid[:, 0]))))
            res_y = np.min(np.diff(np.unique(np.sort(self.grid[:, 1]))))
            res0 = (res_x * 111100,  res_y * 111100)   # approximate degrees to m



        raster2vti_names = []
        for array, raster_fn0 in zip(data, [filename + '_' + name for name in names]):
            _, raster_fn = hazard_model2raster(array, self.dirs['output'], raster_fn0, grid, res0, srs=crs_f)
            if res:
                raster_fn_f = raster_fn.replace('.tiff', '') + '_rs.tiff'
                ds = gdal.Translate(raster_fn_f, raster_fn, xRes=res[0], yRes=res[1], resampleAlg=res_method)
                ds = None
                if crop:
                    print('aa')
                    mask_raster(crop, raster_fn_f, raster_fn_f, all_touched=False, crop=False)
            else:
                raster_fn_f = raster_fn
                if crop:
                    mask_raster(crop, raster_fn_f, raster_fn_f, all_touched=False, crop=False)
            raster2vti_names.append(raster_fn_f)

        # Creates VTI Image from the raster file
        image_filename = join(self.dirs['vti'], filename + '.vti')
        _ = rasters2vti(image_filename, raster2vti_names, names, offset=10)

    def load_data(self, filename=None):
        """
        Loads a serialized Model_results object
        :param filename:
        :return:
        """
        if filename is None:
            filename = join(self.dirs['output'], 'data.obj')

        with open(filename, 'rb') as f:
            A = pickle.load(f)
            self.hmaps = A[0]
            self.immp = A[1]
            self.hcurves_stats = A[2]
            self.hmaps_stats = A[3]

            self.ks1_curve = A[4]
            self.ks1_map = A[5]
            self.chi_curve = A[6]
            self.chi_map = A[7]

    def save_data(self, filename=None):
        """
        Serializes Model_results object into a file
        :param filename: If None, save in results folder named with self.name
        """
        if filename is None:
            filename = join(self.dirs['output'], 'data.obj')

        with open(filename, 'wb') as hazardobj:
            Data = (self.hmaps, self.immp, self.hcurves_stats, self.hmaps_stats,
                    self.ks1_curve, self.ks1_map, self.chi_curve, self.chi_map)
            pickle.dump(Data, hazardobj)


# basemap2vti('basemap.vti', '../../../data/basemaps/basemap_chile/basemap.tiff')
#
# model = hazardResults(name='chile_with', path='./', calcpath='./results_all/calc_42.hdf5')
# model.parse_db({'PGA': np.logspace(np.log10(0.0005), np.log10(3.00), 25)})
# model.get_maps_from_curves(['PGA'], poes=[0.002105])
# model.get_stats('hmaps', 'PGA')
# model.model2vti('maps_faults_updated', 'hmaps_stats', 'PGA', [0.002105])