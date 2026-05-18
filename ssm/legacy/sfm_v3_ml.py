#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:07:58 2020

@author: pciturri
"""

import datetime, time
import numpy as np
import fiona
import os
import matplotlib.pyplot as plt
import psutil
import gc
import h5py
import scipy.special as scp
import pickle
from functools import partial
from scipy import optimize
from shapely.geometry import Point, shape
from multiprocessing import Pool
import postprocessing_lib_v2 as pl



def deg_dist(geom):
    """
    Calculate geodesic distance, using small_angle hyphotesis, between a point
    and an array of points. 
    Input:
        - geom[0] (dtype=list/array, shape=(2,)):
                    Single point to evaluate distances (in deg)
        - geom[1] (dtype=list/array, shape=(2,n)):
                    Single point or list of points to evaluate distances
                    (in deg)
    """
    precision= 12
    
    x1 = [np.deg2rad(geom[0][0]), np.deg2rad(geom[0][1])]
    x2 = [[np.deg2rad(i) for i in geom[1][0]],
          [np.deg2rad(i) for i in geom[1][1]]]
    dtheta = np.sin(x1[1]) * np.sin(x2[1]) +\
             np.cos(x1[1]) * np.cos(x2[1])*np.cos(x2[0] - x1[0])
    distances =  6371. * np.arccos(np.round(dtheta, precision))
    
    return distances


def dist_p2grid(geom):
    """
    Calculate geodesic distance, using small_angle hyphotesis, between a point
    and an array of points. Uses precalculated deg2rad(x) and cos(x), sin(x)
    for parallelization efficiency.
    
    **** I suggest that this formula should be changed, as it gives prec error!
    Input:
        - geom[0] (dtype=list/array, shape=(2,)):
                    Single point to evaluate distances (in radians)
        - geom[1] (dtype=list of 3 array), shape=(3, (n,3)):
                    List of 3 arrays of the grid geom:
                        geom[1][0] (dtype=array, shape(n,): lon      (in rads.)
                        geom[1][1] (dtype=array, shape(n,): cos(lat) (in rads.)
                        geom[1][2] (dtype=array, shape(n,): sin(lat) (in rads.)
    """
    global dtype
    precision=12
    dtheta = (np.sin(geom[0][1]) * geom[1][:,2] +
              np.cos(geom[0][1]) * geom[1][:,1] *
              np.cos(geom[1][:,0] - geom[0][0]))
    
    row =  6371. * np.arccos(np.round(dtheta, precision))

#    return row
    return row.astype(dtype)


def piecewise_linear(x, y0, y1):
    """
    Creates a piecewise linear function for an optimization scheme.
    Careful, that it uses global variables mw_lowcutoff, mw_highcutoff & w_min.
    """
    global mw_lowcutoff, mw_highcutoff, w_min
    return np.piecewise(x, [x < mw_lowcutoff,
                            (x >= mw_lowcutoff) & (x <= mw_highcutoff),
                            x > mw_highcutoff],
                    [lambda x:y0,
                     lambda x: (y1-y0)/(mw_highcutoff-mw_lowcutoff)*
                                     (x - mw_highcutoff) + y1 
                                     if y1 > w_min else 
                             (w_min-y0)/(mw_highcutoff-mw_lowcutoff)*
                             (x - mw_highcutoff) + w_min ,
                     lambda x: y1 if y1 > w_min else w_min])
    

def bounding_box(iterable):
    min_x, min_y = np.min(iterable[0], axis=0)
    max_x, max_y = np.max(iterable[0], axis=0)
    return np.array([(min_x, max_y), (min_y, max_y)])


def findCells(points, bounds):
    
    points = points.reshape((-1,2))

    allInBounds = (points[:,0] >= bounds[:,None,0])
    allInBounds &= (points[:,1] >= bounds[:,None,1])
    allInBounds &= (points[:,0] < bounds[:,None,2])
    allInBounds &= (points[:,1] < bounds[:,None,3])
    
    nz = np.nonzero(allInBounds)
    r = np.full(points.shape[0], np.nan)
    r[nz[1]] = nz[0]
    
    return r


def findCellsParallel(points, bounds, chunksize=100):
    
    func = partial(findCells, bounds=bounds) 
    p = Pool()
    try:
        return np.hstack(p.map(func, points, chunksize))
    finally:
        p.close()
        
        
class ssm_model(object):
    
    """
    Class used to represent a seismicity & faults Smoothed Seismicity Model.
        ...
    
    
    Attributes
    - - - - - - - - 
    name :  str
        the name of the model
    toc : datetime.datetime()
        the time of creation of the model
    catalog : list
        the complete seismicity catalog
    subcatalog : list
        subset of the complete catalog, filtered by depth, shapefile, time or
        specificied events
    grid : array
        grid of observation to produce the forecast
    s_probdens : array
        probability density field of the class's grid and subcatalog
    f_probdens : array
        probability density field of the class's grid and discretized faults
    
    
    Methods
    - - - - - - - -
    set_catalog(filename, db_format)
        Loads the complete catalog in specific format
    set_faults(filename, db_format)
        Loads the fault-base equivalent catalog
    set_grid(filename)
        Loads the observation grid to calculate the smoothed-seismicity model
    set_subcatalog(name, specific=None, depth=None, nan_inc=False, 
                   polygon=None, time=None)
        Filters the complete catalog
    get_catalogSSM(self, cat_name='full', N=2, power=1.5, target_mw=5.0,
                   nproc=16)
        Calculates the SSM spatial smoothing based only in seismicity catalog
        Creates a normalized probability density field 
    get_faultSSM(KernelSize=10., N=2, power=1.5, pond=1, nproc=16)  
        Calculates the SSM spatial smoothing based only in faults
        Creates a normalized probability density field
    get_magPDF(Mw_max, a, b, Mw_target, bin_size=0.1) 
        Calculates the SSM magnitude smoothing based only in seismicity
        statistics. Construct a tapered-GR curve
    save_txt(filename, att, fmt='%.18e', header='',delimiter=' ')
        Save into a txtfile a model result
        
        
    """
    
    
    def __init__(self, name, model_dir):
        
        self.name = name
        self.dir = {'model': model_dir,
                    'store': model_dir + 'store/',
                    'vtk': model_dir + 'vtk/',
                    'basemap': model_dir + 'basemap/'}
        for subdir in self.dir.values():
            if not os.path.exists(subdir):
                os.makedirs(subdir)
        self.toc = datetime.datetime.now()
        self.catalog = []
        self.faults = []
        self.dists = {}
        self.subcatalog = {}    
        self.subfaults = {}
        self.pdfx_faults = {}
        self.pdfx_catalog_vk = {}
        self.pdfx_catalog_fk = {}
        self.pdfx_weighted = {}
        self.testgrid = {}
        self.omega = {}
        self.G_r = {}               # Calibration of fixed kernel
        self.G_n = {}               # Calibration of variable kernel
        self.mask_faults = {}       # Mask of fault pdf cutoff contribution
        self.seismic_weight = {}    # Weighing calibration
        
        
    # ============================= #
    #     Input loading methods     #
    # ============================= #
    
    def set_catalog(self, filename, db_format):
        
        """
        Load complete seismic catalog for the model
        """
        
        if db_format == 'sheec':
            ### Columns: [lon, lat, year, month, day, magnitude, depth,
            ###           hour, minute, second,
            ###           time_of_completeness, mag_of_completeness]
            
            raw = np.genfromtxt(filename)
            self.catalog = [[i[0], i[1],                # Epicenter position
                             datetime.datetime(int(i[2]),    # Date of event
                                               int(i[3]),    
                                               int(i[4])),
                            10**(1.5 * i[5] + 9.0),         # Magnitude (N · m)  
                            -i[6],                           # depth (km)
                            i[10], i[11]]     # Event corrected completeness
                                            for i in raw]       
            self.subcatalog['full'] = {'cat':self.catalog[:],
                                       'ind':[i for i 
                                              in range(len(self.catalog))]}


            
    def set_faults(self, filename, db_format):
        
        """
        Load complete fault-based synthetic catalog for the model.
        It consist of a 2-D line discretization of the fault traces, where each
        point is equivalent to an earthquake of Mw equivalent to the avg. fault
        slip rate
        """       

        if db_format == 'edsf':
            ### Input columns: [lon, lat, year, -, multiplicity, Mw rate,
            ### - - - -]
            raw = np.genfromtxt(filename)
            self.faults = [[i[0], i[1], 10**(1.5*i[5] + 9.0) ] for i in raw]
            self.subfaults['full'] = {'faults':self.faults[:],
                                       'ind':[i for i 
                                              in range(len(self.faults))]}
            
    def set_grid(self, filename, mask=False):
        
        """
        Load the model's grid.
        """
        ### Pending: Provide flexibility for the mesh area and mask setting
        
        ### Input columns: [left-bot-corner lon, left-bot-corner lat,
        ###                 center lon, center lat, cell area]
        self.maskflag = mask
        self.grid = np.genfromtxt(filename)[:,3:]
        if mask:
            self.gridmask = self.grid[:,-1]
            self.grid_int = self.grid[self.gridmask==1]
        else:
            self.gridmask = np.ones(self.grid.shape[0])
            self.grid_int = self.grid
#        self.grid = self.grid[self.grid[:,-1]==1]
        ### Input columns: [center lon, center lat, cell area]
#        
#        self.grid = np.genfromtxt(filename)     
        
    # ============================= #
    #     Data handling methods     #
    # ============================= #
    
    
    def set_subcatalog(self, name, specific=None, minmag=None, maxmag=None,
                       depth=None, nan_inc=False, bbox=None, polygon=None,
                       time=None):
        
        """
        Filters the model catalog and creates a subcatalog. It filters by
        a specific index list, a depth range, a polygon shapefile a bound-box
        and a time window.
        
        Input
        -----
        specific : array/list
            Simply filters the catalog by an array of index
        depth : tuple/list
            Minimum and maximum depth windows (in negative values)
        nan_inc : boolean
            Flag to include nan values of depth
        bbox : list of two tuples/lists
            x and y ranges of the bounding box [(x_min,x_max),(y_min,y_max)]
        polygon : string
            Filepath of the shapefile to crop the catalog
        time : tuple/list of datetime.datetime() objects
            Time range to crop the catalog. Provide datetime.datetime.now() to
            unbound by above and datetime.datetime(0,0,0) by below
            
        Output
        -----
        self.subcatalog[name] : dict of two lists
            Creates two lists with the cropped catalog, and the corresponding
            indexes to the full catalog        
        """
        if specific:
            subcatalog = [self.catalog[i] for i in specific]
        else:
            subcatalog = self.catalog[:]
        
        if minmag:
            subcatalog = [i for i in subcatalog if (np.log10(i[3])-9.)/1.5 
                                                                  >= minmag]
        if maxmag:
            subcatalog = [i for i in subcatalog if (np.log10(i[3])-9.)/1.5 
                                                                  <= maxmag]

        if depth:
            if nan_inc:
                subcatalog = [i for i in subcatalog
                                           if depth[0] <= i[4] < depth[1]
                                               or np.isnan(i[4])]
            else:
                subcatalog = [i for i in subcatalog
                                           if depth[0] <= i[4] < depth[1]]
        
        if bbox:
            subcatalog = [i for i in subcatalog
                                     if bbox[0][0] <= i[0] <= bbox[0][1]
                                         and bbox[1][0] <= i[1] <= bbox[1][1]]           
        
        if polygon:
            shpfile = fiona.open(polygon)
            poly = next(iter(shpfile))
            subcatalog = [i for i in subcatalog
                                        if Point(i[0], i[1]).within(
                                                shape(poly['geometry']))]

        if time:
            subcatalog = [i for i in subcatalog
                                        if time[0] <= i[2] < time[1]]
        
        indexes = [self.catalog.index(i) for i in subcatalog 
                                           if i in self.catalog[:]]

        self.subcatalog[name] = {'cat': subcatalog, 'ind': indexes}        

        
        
    def set_subfaults(self, name, specific=None, bbox=None,
                            polygon=None, time=None):
        
        """
        Filters the model catalog and creates a subcatalog. It filters by
        a specific index list, a depth range, a polygon shapefile a bound-box
        and a time window.
        
        Input
        -----
        specific : array/list
            Simply filters the catalog by an array of index
        bbox : list of two tuples/lists
            x and y ranges of the bounding box [(x_min,x_max),(y_min,y_max)]
        polygon : string
            Filepath of the shapefile to crop the catalog
        
        Output
        -----
        self.subfaults[name] : dict of two lists
            Creates two lists with the cropped fault database, and the corresp-
            onding indexes to the full database
        """
        
        if specific:
            subfaults = self.faults[specific]
        else:
            subfaults = self.faults[:]
            
        if bbox:
            subfaults = [i for i in subfaults
                                     if bbox[0][0] < i[0] < bbox[0][1]
                                         and bbox[1][0] < i[1] < bbox[1][1]]           
        
        if polygon:
            shpfile = fiona.open(polygon)
            poly = next(iter(shpfile))
            subfaults = [i for i in subfaults
                                        if Point(i[0], i[1]).within(
                                                shape(poly['geometry']))]

        indexes = [self.faults.index(i) for i in subfaults
                                           if i in self.faults[:]]
        self.subfaults[name] = {'faults': subfaults, 'ind': indexes}    


    def set_testgrid(self, res, mask=False):
        
        """
        Redefines grid in terms of each cell boundaries, so testing can be
        performed,
        Input:
            res (tuple): x and y resolution
            
        Output:
            self.testgrid['bounds']: redefined grid
            self.testgrid['res']: resolution
            self.testgrid['n']: number of cells in x and y directions
            self.testgrid['bbox']: expanded grid onto a rectangle.

        """
        
        if isinstance(mask, (list, np.ndarray)):    
            grid = self.grid_int[mask==1]         
        elif mask == False:
            grid = self.grid_int
        else:
            raise Exception('Mask object type not understood')
        testgrid = []
   
        x = np.arange(grid[:,0].min()-res[0]/2.,
                      grid[:,0].max()+3./2.*res[0], res[0])
        y = np.arange(grid[:,1].min()-res[1]/2.,
                      grid[:,1].max()+3./2.*res[1], res[1])   
        
        for i in grid:
            testgrid.append([i[0]-res[0]/2., i[1]-res[1]/2.,
                             i[0]+res[0]/2., i[1]+res[1]/2.])   

        self.testgrid['bounds'] = np.array(testgrid[:])
        self.testgrid['res']= res
        self.testgrid['n'] =(x.shape[0]-1,y.shape[0]-1)
        self.testgrid['bbox'] = np.meshgrid(x,y)
        
        
    # ============================= #
    #   Basic calculation methods   #
    # ============================= #
    
    
    def set_distances(self, att1, att2, drop=False, dtype='f',nproc=8):
        
        """
        Fast paralellized function that calculates the distances between two
        set of points.
        
        Input
        -------
        att1 :  str
            Name of the first class attribute, which must contain its position
            (i.e. 'catalog', 'grid', 'faults'). The referenced array must be
            of shape (n, >=2)
        att1 :  str
            Name of the second class attribute (i.e. 'catalog', etc.). The
            referenced array must be of shape (m, >=2)
        drop : bool
            Flag to drop the distance results into a hdf5 database, which could
            be loaded later for better performance
        nproc : int
            Number of processes for multiprocessing.Pool.map()
            
        Output
        --------
        self.dists[(attr, att2)] : array
            Distance matrix of shape n × m. 
            
        """
     
        start = time.process_time()
        pointarray1 = np.deg2rad(np.array([[i[0], i[1]] 
                                 for i in getattr(self, att1)]))
        pointarray2 = np.deg2rad(np.array([[i[0], i[1]] 
                                 for i in getattr(self, att2)]))

        print ("Calculate distances between " + att1 + ' and ' +
               att2 +"\n\t number of points: %i × %i" % (pointarray1.shape[0],
                                                         pointarray2.shape[0]))
               
        geom2 = np.vstack((pointarray2[:,0],
                               np.cos(pointarray2[:,1]),
                               np.sin(pointarray2[:,1]))).T
                           
        Input_list = [[i, geom2] for i in pointarray1]
        
        
        if nproc != 0:
            pool = Pool(nproc)
            A = np.array(pool.map(dist_p2grid, Input_list))
            pool.close()
            pool.join()
       
        
        if drop:
            
            
            filename = self.dir['store'] + 'd_' + att1 + '_' +att2
            with h5py.File(filename, 'w') as f:             
                dset = f.create_dataset('dist', A.shape, dtype=dtype,
                                        chunks=True)
                dset[:A.shape[0],:A.shape[1]] = A
            f.close()
            del A
            gc.collect()
        else:
            self.dists[(att1, att2)] = A[:]
            del A
            gc.collect()

        print("Processing time: %.1f seconds" % (time.process_time() - start))    


    def get_discrete_eqk_field(self, subcat):
        
        """
        Counts the number of earthquakes that occurs within each cell of the
        test grid.
        Input:
            subcat (string): name of the subcatalog
        Output:
            omega (array): 1-array of ints containing the cell earthquake count
        
        """
        
        testgrid = self.testgrid['bounds'][:]
        catalog = np.array(self.subcatalog[subcat]['cat'][:])
        
        omega = np.zeros(testgrid.shape[0])
        
        if catalog.shape[0] != 0:
            r = findCellsParallel(catalog[:,:2],testgrid)
        else:
            r = np.full(testgrid.shape, np.nan)
        results = np.unique(r, return_counts=True)
        inside = False==np.isnan(results[0])
        omega[results[0][inside].astype('int')] = results[1][inside]
        
        self.omega[subcat] = omega
        return omega   
    

    # ============================== #
    #   Model construction methods   #
    # ============================== #            
            
            
    def get_catalogSSM_varKernel(self, subcat ='full',
                                 N=2, power=1.5,
                                 mc_min=4.5, dist_cutoff=0.,
                                 area_norm=True, sum_norm=True,
                                 nproc=16, memclean=False):
        
        """
        Variable-sized Kernel smoothing from Helmstetter et al, 2007
        Modified from func_kernelvariable.m developed by Hiemer, S. in matlab
        
        Input
        - subcat (string): Name of the sub-catalog to calculate
        - N (int): Sorting position of the closest event for each
                         earthquake, which controlls initial Kernel Size
        - power (float): 1.0: Wang-Kernel, 1.5: Helmstetter-Kernel
        - mc_min (float): min magnitude used for completeness correction
        - area_norm (boolean): Flag to normalize each cell by its area
        - sum_norm (boolean): Flag to normalize every cell by the total sum of
                                of all cells
        - nproc (int): Number of processes for parallelization. If 0, no
                             parallelization scheme is used.
        - memclean (bool): Removes the cat2grid distance matrix
        
        Output
        - pdfx_catalog_vk[subcat] (dtype=array, shape=(m,)):
            Probability density for each grid cell, as the sum of every catalog
            event contribution.
        
        """
        
        # Initialize        
        start = time.process_time()
        catalog = np.array(self.subcatalog[subcat]['cat'][:])
        cat_ind= np.array(self.subcatalog[subcat]['ind'][:])

        print ("Starting catalog variable-size kernel smoothing\n" +
               "\tsub-catalog used: " + subcat + "\n" +
               "\tnumber of events: %i\n" % catalog.shape[0] +
               "\tnumber of cells: %i\n" % self.grid.shape[0] +
               "\tnumber of masked cells: %i\n" % len(self.grid_int) +
               "\tnumber of processes: %i\n" % nproc)       


        
        # Calculate distances between all events
        d_cat2cat = self.dists[('catalog','catalog')][cat_ind,:][:,cat_ind]
        kernel_size = np.sort(d_cat2cat).T[N,:]
        if dist_cutoff:
            kernel_size[kernel_size < dist_cutoff] = dist_cutoff
        catalog[np.where(catalog[:,6] >= mc_min), 6] = mc_min
        
        pdfX = np.zeros(self.grid.shape[0])

        for i, j, k in zip(self.dists[('catalog','grid')][cat_ind,:],
                                      kernel_size, catalog[:, 5:]):
            kernel_i = 1./((i.astype('f8')**2 + j.astype('f8')**2)**power)  
            kernel_i /= np.sum(kernel_i)/(10**(k[1] - mc_min)/k[0])
            pdfX += kernel_i 
   
        
        pdfX = pdfX[self.gridmask==1]
            
        if area_norm:
            pdfX /= self.grid_int[:,2]

        if sum_norm:
            pdfX /= np.sum(pdfX)
    
        if memclean:
            self.dists.pop(('catalog', 'grid'))
            
        self.pdfx_catalog_vk[subcat] = pdfX[:]

        print("Catalog variable-size kernel smoothing complete.\n\
              \ttime taken: %i seconds \n" % (time.process_time() - start) +
              "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])


    def get_catalogSSM_fixKernel(self, subcat ='full', KernelSize=10.,
                                 power=1.5, area_norm=True, sum_norm=True, 
                                 nproc=16, mag_scaling=False, mc_min=False,
                                 memclean=False):
        
        """
        Fixed-sized Kernel smoothing from Helmstetter et al, 2007
        Modified from func_kernelfix.m developed by Hiemer, S. in matlab
        
        Input
        
        - subcat (string): Name of the sub-catalog to calculate
        - KernelSize (float): Fix distance of the smoothing kernel       
        - power (float): 1.0: Wang-Kernel, 1.5: Helmstetter-Kernel
        - mc_min (float): min magnitude used for completeness correction
        - mag_scaling (bool): Ponderates kernel by moment of event
        - area_norm (boolean): Flag to normalize each cell by its area
        - sum_norm (boolean): Flag to normalize every cell by the total sum of
                                of all cells
        - nproc (int): Number of processes for parallelization. If 0, no
                             parallelization scheme is used.
        - memclean (bool): Removes the cat2grid distance matrix
        
        Output
        - pdfx_catalog_fk[subcat] (dtype=array, shape=(m,)):
            Probability density for each grid cell, as the sum of every catalog
            event contribution.
            
        """
        
        # Initialize        
        start = time.process_time()
        catalog = np.array(self.subcatalog[subcat]['cat'][:])
        cat_ind= np.array(self.subcatalog[subcat]['ind'][:])
        if mc_min:
            catalog[np.where(catalog[:,6] >= mc_min), 6] = mc_min        

        print ("Starting catalog fixed-size kernel smoothing\n" +
               "\tnumber of events: %i\n" % catalog.shape[0] +
               "\tnumber of cells: %i\n" % self.grid.shape[0] +
               "\tnumber of masked cells: %i\n" % len(self.grid_int) +
               "\tnumber of processes: %i\n" % nproc +
               "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])       

        
        # Calculate distances between all events

        pdfX = np.zeros(self.grid.shape[0])
        for i,j in zip(self.dists[('catalog','grid')][cat_ind,:],
                                  catalog[:,[3,5,6]]):
            
            kernel_i = 1./((i.astype('f8')**2 + KernelSize**2)**power)
            kernel_i /= (np.sum(kernel_i))
            
            if mag_scaling:
                kernel_i *= j[0]
            if mc_min:
                kernel_i*=(10**(j[2] - mc_min)/j[1])
            pdfX += kernel_i


        pdfX = pdfX[self.gridmask==1]
        if area_norm:
            pdfX /= self.grid_int[:,2]

        if sum_norm:
            pdfX /= np.sum(pdfX)
            
        if memclean:
            self.dists.pop(('catalog', 'grid'))
        self.pdfx_catalog_fk[subcat] = pdfX[:]

        print("Catalog fixed-size kernel smoothing complete.\n" +
              "\t time taken: %i seconds \n" % (time.process_time() - start) +
              "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])
        
    
        
        
    def get_faultSSM_fixKernel(self, subfault='full', KernelSize=10.,
                               power=1.5, pond=1, area_norm=True, 
                               sum_norm=True, nproc=16, memclean=False):
        
        """
        Fixed-sized Kernel smoothing from Helmstetter et al, 2007
        Modified from func_kernelfix.m developed by Hiemer, S. in matlab
        
        Input
        
        - subfault (string): Name of the sub-catalog to calculate
        - KernelSize (float): Fix distance of the smoothing kernel
        - power (float): 1.0: Wang-Kernel, 1.5: Helmstetter-Kernel
        - pond (int, array_{nfaults}): Ponderation for each fault event
        - area_norm (boolean): Flag to normalize each cell with its area
        - sum_norm (boolean): Flag to normalize every cell by the total sum of
                                of all cells
        - nproc (int): Number of processes for parallelization. If 0, no
                             parallelization scheme is used.
        - memclean (bool): Removes the fault2grid distance matrix                            
        
        Output
        - fault_pdfx (dtype=array, shape=(m,)): accummulated probability 
            density for each grid cell, as the sum of every fault event
            contribution
        
        
        """
        

     
        start = time.process_time()
        faults = np.array(self.subfaults[subfault]['faults'][:])
        faults_ind = np.array(self.subfaults[subfault]['ind'][:])
        if pond == 1:
            faults = np.array([np.hstack((i, 1)) for i in faults])
        else:
            faults = np.array([np.hstack((i, 1)) 
                     for i,j in zip(faults,pond)])

        print ("Starting faults fixed-size kernel smoothing\n" +
               "\tnumber of events: %i\n" % len(faults) +
               "\tnumber of cells: %i\n" % len(self.grid) +
               "\tnumber of masked cells: %i\n" % len(self.grid_int) +
               "\tnumber of processes: %i\n" % nproc)    
         

        pdfX = np.zeros(self.grid.shape[0])
        
        for i,j in zip(self.dists[('faults','grid')][faults_ind,:], faults):
            kernel_i = 1./((i.astype('f8')**2 + KernelSize**2)**power)
            kernel_i /= (np.sum(kernel_i)*j[-1]/j[-2])
            pdfX += kernel_i
            
        pdfX = pdfX[self.gridmask==1]
            
        if area_norm:
            pdfX /= self.grid_int[:,2]
        
        if sum_norm:
            pdfX /= np.sum(pdfX)
        
        if memclean:
            self.dists.pop(('faults', 'grid'))
        
        print("Faults fixed-size kernel smoothing complete.\n" +
              "\t time taken: %i seconds \n" % (time.process_time() - start) +
              "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])
   
        self.pdfx_faults[subfault] = pdfX[:]



    # ====================================== #
    #   Model spatial calibration methods    #
    # ====================================== #
        

    
    def calibrate_fixKernel(self, training_cat, target_cat, r_disc,
                            model_area_norm=True, ref_area_norm=False,
                            mag_scaling=False, Mc_min=False,
                            plot=False, save=False):
        """
        Calibrates the fixed kernel method in terms of the smoothing distance
        using the Log-likelihood method.
        Input:
            training_cat (str): name of the catalog used to create the models
            target_cat (str): name of the catalog used to perform the retro-
                spective testing
            r_disc (list): values of r (smoothing distance) to create the models
            model_area_norm (bool): Normalize the cells spatial pdf by its area
            ref_area_norm (bool): normalize the reference model by cell area
            mag_scaling (bool): Ponderates the kernel by the event magnitude
            Mc_min (bool): Corrects the kernel by the catalog completeness
        Output:
            self.G_r[(training_cat,target_cat)] (dict):
                Dictionary containg the results of the calibration for the sub-
                catalogs pair. Contains the r_discretization, the joint log 
                likelihod of the ref model (L_uni) and the fix kernel model (L)
                along with the Probability gain of the model (G)
        """
        logL = {}
        G = {}
        omega = self.get_discrete_eqk_field(target_cat)
        
        Nt = np.sum(omega)
    
        n_cells = self.grid_int.shape[0]
        pdfx_uniform = 1./n_cells*np.ones(n_cells)
        if ref_area_norm:
            pdfx_uniform /= self.grid_int[:,2]
            pdfx_uniform /= np.sum(pdfx_uniform)
        pdfx_uniform *= Nt
        
        logL_uni = 0
        for i in range(omega.shape[0]):
            logL_uni += -pdfx_uniform[i] + \
                             omega[i]*np.log10(pdfx_uniform[i]) -\
                             np.log10(scp.factorial(omega[i]))

        for r in r_disc:
            logL[r] = 0
            
            self.get_catalogSSM_fixKernel(subcat=training_cat,
                                          KernelSize=r,
                                          area_norm=model_area_norm,
                                          mag_scaling=mag_scaling,
                                          mc_min=Mc_min)
            
            mu = Nt*self.pdfx_catalog_fk[training_cat][:] 
                
            for i in range(omega.shape[0]):
                logL[r] += -mu[i] + omega[i]*np.log10(mu[i]) -\
                            np.log10(scp.factorial(omega[i]))
            
            G[r] = 10**((logL[r]-logL_uni)/Nt)

        y = np.array([G[i] for i in r_disc])            
        self.G_r[(training_cat,target_cat)] = {'r': r_disc,
                                               'r_opt': r_disc[y.argmax()],
                                               'L_ref': logL_uni,
                                               'L': logL,
                                               'G': G}

        
        if plot:       
            plt.figure(figsize=(8,6))

            plt.plot(r_disc, y,'o-')
            plt.plot(r_disc[y.argmax()], y.max(), "^", markersize=13)
            plt.axvline(r_disc[y.argmax()])
            plt.title('Fixed-Kernel calibration\n' +
                      'Training cat:  ' + training_cat +
                      r'   $N_0=%i$' %
                      len(self.subcatalog[training_cat]['cat']) + 
                      '\nTarget cat:  ' + target_cat + 
                      r'   $N_t=%i$' % Nt)
            if len(r_disc) > 1:
                plt.xticks(r_disc)
                plt.grid()
            plt.xlabel('Smoothing distance \n' + 
                       r'$r \,[\mathrm{km}]$', fontsize=16)
            plt.ylabel(' Probability gain per earthquake \n' +
                       r'$G = \frac{L - L_0}{N_t}$', fontsize=16)
            plt.tight_layout()
            
            
        if save:
            with open(self.dir['store'] + 'Gr_' + 
                      training_cat + '_' + target_cat, 'wb') as file_:
              pickle.dump(self.G_r, file_)             
            
        return G, r_disc[y.argmax()]
            
            
    def calibrate_varKernel(self, training_cat, target_cat, n_disc,
                            model_area_norm=True, ref_area_norm=False,
                            Mc_min=4.5, plot=False, save=False): 
        
        """
        Calibrates the variable kernel method in terms of the smoothing 
        distance using the Log-likelihood method.
        Input:
            training_cat (str): name of the catalog used to create the models
            target_cat (str): name of the catalog used to perform the retro-
                spective testing
            n_disc (list): values of N (nearest neighbors) to create the models
            model_area_norm (bool): Normalize the cells spatial pdf by its area
            ref_area_norm (bool): normalize the reference model by cell area
            Mc_min (bool): Corrects the kernel by the catalog completeness
        Output:
            self.G_n[(training_cat,target_cat)] (dict):
                Dictionary containg the results of the calibration for the sub-
                catalogs pair. Contains the n discretization, the joint log 
                likelihod of the ref model (L_uni) and the fix kernel model (L)
                along with the Probability gain of the model (G)
        """

        logL = {}
        G = {}
        omega = self.get_discrete_eqk_field(target_cat)
        Nt = np.sum(omega)
    
        n_cells = self.grid_int.shape[0]
        pdfx_uniform = 1./n_cells*np.ones(n_cells)
        if ref_area_norm:
            pdfx_uniform /= self.grid_int[:,2]
            pdfx_uniform /= np.sum(pdfx_uniform)
        pdfx_uniform *= Nt
        
        logL_uni = 0
        for i in range(omega.shape[0]):
            logL_uni += -pdfx_uniform[i] + \
                             omega[i]*np.log10(pdfx_uniform[i]) -\
                             np.log10(scp.factorial(omega[i]))

        for n in n_disc:
            logL[n] = 0
            self.get_catalogSSM_varKernel(subcat=training_cat,
                                          N=n,
                                          mc_min=Mc_min,
                                          area_norm=model_area_norm)   
            
            mu = Nt*self.pdfx_catalog_vk[training_cat][:] 
                
            for i in range(omega.shape[0]):
                logL[n] += -mu[i] + omega[i]*np.log10(mu[i]) -\
                            np.log10(scp.factorial(omega[i]))
            
            G[n] = 10**((logL[n]-logL_uni)/Nt)
            
        y = np.array([G[i] for i in n_disc])
        self.G_n[(training_cat,target_cat)] = {'N': n_disc,
                                               'N_opt': n_disc[y.argmax()],
                                               'L_ref': logL_uni,
                                               'L': logL,
                                               'G': G}
        if plot:       
            plt.figure(figsize=(8,6))

            plt.plot(n_disc, y,'o-')
            plt.plot(n_disc[y.argmax()], y.max(), "^", markersize=13)
            plt.axvline(n_disc[y.argmax()])
            plt.title('Fixed-Kernel calibration\n' +
                      'Training cat:  ' + training_cat +
                      r'   $N_0=%i$' %
                      len(self.subcatalog[training_cat]['cat']) + 
                      '\nTarget cat:  ' + target_cat + 
                      r'   $N_t=%i$' % Nt)
            if len(n_disc) > 1:
                plt.xticks(n_disc)
                plt.grid()
            plt.xlabel('Nearest Neighbor \n' + 
                       r'$N $', fontsize=16)
            plt.ylabel(' Probability gain per earthquake \n' +
                       r'$G = \frac{L - L_0}{N_t}$', fontsize=16)
            plt.tight_layout()
            
        if save:
            with open(self.dir['store'] + 'Gn_' + 
                      training_cat + '_' + target_cat, 'wb') as file_:
              pickle.dump(self.G_n, file_) 
              
              
        return G, n_disc[y.argmax()]            
            
    # ============================================= #
    #           Calibrate weighting function        #
    # ============================================= #
            
    def get_cdf_mask(self, field, subcat, clvl):
        
        attr = getattr(self, field)[subcat]

        pdf = np.flip(np.sort(attr))
        cdf = np.cumsum(pdf)
        val = pdf[np.where(cdf >= clvl)[0][0]]
        print(val)
        ind = np.where(attr >= val)
        mask = np.zeros(attr.shape[0]).astype('int')
        mask[ind] = 1
        self.mask_faults[subcat] = mask
        

    def calibrate_weight(self, training_cat, target_cat, target_cat_time, 
                         mask, 
                         fault_subcat='full',
                         weight_disc=np.arange(0, 1.1, 0.1),
                         mw_disc=np.arange(4.5, 7.6, 0.1), dmw=0.1,
                         mw_lowcutoff=5.5, mw_highcutoff=7.0,
                         w_min=0., 
                         plot=False,
                         save=False):
  
        """
        Calibrates the Seismic-Weighting of both Seismic- and Fault-based
        smoothed spatial pdf, by using a Log-Likelihood approach. 
        Input:
            training_cat (str): name of the catalog used to create the models
            target_cat (str): name of the catalog used to perform the retro-
                spective calibration
            mask (array): mask that points the cells with a considerable con-
                tribution of the fault pdf (1: the cells is used, 0: not)
            fault_subcat (str): fault subcatalog
            weight_disc (array): Discretization of the weighting functions
            mw_disc (array): Discretization of Mw for the calibration
            mw_lowcutoff, mw_highcutoff (float): Below and above which, the 
                seismic and fault catalog respectively dominates the final pdf
        Output:
            self.seismic_weight[(training_cat,target_cat)] (dict):
                Dictionary containg the results of the calibration for the sub-
                catalogs pair. Contains the the joint log likelihod of each
                w, mw pair, the optimal weights  opt_w for each mw bin and the
                polynom 
                model (L_uni) and the fix kernel model (L)
                along with the Probability gain of the model (G)
        """

        start = time.process_time()     
        print ("Starting Seismic-Weight calibration\n" +
               "\tnumber of target events: %i\n" %\
                           len(self.subcatalog[training_cat]['cat']) +
               "\tnumber of masked cells: %i\n" %\
                           len(np.where(mask==1)[0]))            

        mw_disc_range = np.array([[i - dmw/2., i + dmw/2.] for i in mw_disc])

    
#        seism = self.pdfx_catalog_vk[training_cat][mask==1]
#        seism = seism/np.sum(seism)
#        faults = self.pdfx_faults[fault_subcat][mask==1]
#        faults = faults/np.sum(faults)
#        
        seism = 1.*self.pdfx_catalog_vk[training_cat][mask==1]
#        seism = seism/np.sum(seism)
        faults = 1.*self.pdfx_faults[fault_subcat][mask==1]
        faults /= np.sum(faults)
        faults *= np.sum(seism)
        
        logL = np.zeros((len(mw_disc_range), len(weight_disc)))

        Ntotal = 0
        for i, mw in enumerate(mw_disc_range):
            subcat_t = (target_cat, np.round((mw[0] + mw[1])/2.0,1))
            
            self.set_subcatalog(name=subcat_t,
                                time=target_cat_time,
                                minmag=mw[0], maxmag=mw[1])
            
            omega = self.get_discrete_eqk_field(subcat_t)
            Nt = np.sum(omega)        
            Ntotal += Nt
        
            for j, w in enumerate(weight_disc):
                mu = (w * seism + (1. - w) * faults)
                mu = Nt * mu/np.sum(mu)
                logL[i, j] = np.sum(-mu + omega*np.log10(mu) -
                                np.log10(scp.factorial(omega)))

            logL[i,:] /= np.max(logL[i,:])
            
            
        valid_logL = np.where(~np.isnan(np.sum(logL, axis=1)))
        ind_opt = logL.argmin(axis=1)
        opt_w = weight_disc[ind_opt]        
            
        p , e = optimize.curve_fit(piecewise_linear,
                                   mw_disc[valid_logL],
                                    opt_w[valid_logL])

        if plot:
            plt.figure(figsize=(10,8))
            plt.imshow(np.flipud(logL.T), cmap='magma_r', aspect='auto',
                       extent=[min(mw_disc_range[:,0]),
                               max(mw_disc_range[:,1]),
                               min(weight_disc), max(weight_disc)])
            plt.title('Seismic weight calibration\n' +
                      'Training cat:  ' + training_cat +
                      r'   $N_0=%i$' %
                      len(self.subcatalog[training_cat]['cat']) + 
                      '\nTarget cat:  ' + target_cat + 
                      r'   $N_t=%i$' % Ntotal)
            plt.ylabel('Seismic weight')
            plt.xlabel('Magnitude target')
            cbar = plt.colorbar()
            cbar.set_label(r'$\frac{L}{L_{max}}$', fontsize=20)
            for i,j in enumerate(mw_disc):
                plt.plot(mw_disc[valid_logL], opt_w[valid_logL],'k+')                    

            
            plt.plot(mw_disc, piecewise_linear(mw_disc, *p))            
            plt.tight_layout()
        self.seismic_weight[(training_cat, target_cat)] = {
                                                    'logL' : logL,
                                                    'opt_w' : opt_w,
                                                    'func': piecewise_linear,
                                                    'params': p,
                                                    } 
        if save:
            with open(self.dir['store'] + 'w_' + 
                      training_cat + '_' + target_cat, 'wb') as file_:
              pickle.dump(self.seismic_weight, file_)            
        print("Calibration Finished.\n" +
              '\t params: w_1=%.3f, w_2=%.3f ' % (p[0], p[1]) + '\n' +
              "\t time taken: %i seconds \n" % (time.process_time() - start) +
              "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])        


    # ============================================= #
    #            Construct final forecast           #        
    # ============================================= #


    def get_magPDF(self, Mw_max, a, b, Mw_target, bin_size=0.1):
        
        """
        yet to define
        """
        magnitudes = np.arange(Mw_target, Mw_max + 2*bin_size, bin_size)
        
        cdf_trunc = ( (np.exp(-b*np.log(10.) *
                                       (magnitudes - Mw_target)) -
                            np.exp(-b*np.log(10.) * (Mw_max - Mw_target))) /
                         (1 - np.exp(-b*np.log(10.) * (Mw_max - Mw_target))) ) 
        self.cdf_trunc = cdf_trunc[:-1]
        self.pdf_trunc = -np.diff(cdf_trunc)/np.sum(-np.diff(cdf_trunc))
        self.scale_factor= 10**(a-b*Mw_target)


    def get_weighted_pdfx(self, s_subcat, f_subset, mask, m_disc,
                          f=None, params=None):
        
        mu_s = 1.0*self.pdfx_catalog_vk[s_subcat][:]
        mu_f = 1.0*self.pdfx_faults[f_subset][:]
        
        if f is None:
            f = self.seismic_weight[s_subcat]['func']
            print('[ASD')
        if params is None:
            params = self.seismic_weight[s_subcat]['params']
        
        scale_s = np.sum(mu_s[mask==1])
        mu_f_crop = (mu_f[mask==1][:]/np.sum(mu_f[mask==1][:]))*scale_s
        mu_s_crop = 1.*mu_s[mask==1][:]
        
        self.pdfx_mw = {}
        self.cdfx_mw = {}
        for m_i in m_disc:
            
            w = f(m_i, params[0], params[1])

            PDF = 1.0*mu_s[:]
            PDF[mask==1] = w * mu_s_crop + (1.-w) * mu_f_crop
            self.pdfx_mw[m_i] = PDF[:]
        
        for mw in m_disc:
            
            self.cdfx_mw[mw] = np.sum(np.array([self.pdfx_mw[i]
                            for i in mw_disc if i >= mw]), axis=0)
        
        
        return self.pdfx_mw, self.cdfx_mw
    
    
    
    # ============================================= #
    #     Load&save pre-calculated data methods     #
    # ============================================= #
           
            
    def load_distances(self, att1, att2):
        
        """
        Load dropped distance matrix, in format hdf5. 
        
        Input
        -------
        att1 :  str
            Name of the first class attribute.
        att1 :  str
            Name of the second class attribute.
        Output
        --------
        self.dists[(attr, att2)] : array
            Distance matrix of shape n × m. 
            
        """        
        filename = self.dir['store'] + 'd_' + att1 + '_' +att2
        f = h5py.File(filename, 'r')
        self.dists[(att1, att2)] = f['dist'][:]
        f.close()
        gc.collect()
        
        
    def load_pdf(self, pdf_type, subcat, filename=None):
        
        if not filename:
            filename = self.dir['store'] + subcat + '_' + pdf_type
        data = np.genfromtxt(filename)
        if pdf_type == 'catalog_fix':
            self.pdfx_catalog_fk[subcat] = data
        elif pdf_type == 'catalog_var':
            self.pdfx_catalog_vk[subcat] = data
        elif pdf_type == 'faults':
            self.pdfx_faults[subcat] = data
            
            
    def load_seismic_calibration(self, training_cat, target_cat):
        
        with open(self.dir['store'] + 'w_' + 
                  training_cat + '_' + target_cat, 'rb') as file_:
            self.seismic_weight = pickle.load(file_)  
         
            
    def load_fix_calibration(self, training_cat, target_cat):
        
        with open(self.dir['store'] + 'Gr_' + 
                  training_cat + '_' + target_cat, 'rb') as file_:
            self.G_r = pickle.load(file_)  


    def load_var_calibration(self, training_cat, target_cat):
        
        with open(self.dir['store'] + 'Gn_' + 
                  training_cat + '_' + target_cat, 'rb') as file_:
            self.G_n = pickle.load(file_)   
            
            
    def save_pdf(self, pdf_type, subcat, filename=None,
                 fmt='%.16e', header='',delimiter=' '):
        
        if not filename:
            filename = self.dir['store'] + subcat + '_' + pdf_type
        if pdf_type == 'catalog_fix':
            data = self.pdfx_catalog_fk[subcat]
        elif pdf_type == 'catalog_var':
            data = self.pdfx_catalog_vk[subcat]
        elif pdf_type == 'faults':
            data = self.pdfx_faults[subcat]
        np.savetxt(filename, data, fmt=fmt, header=header, delimiter=delimiter)


    def save_results(self, filename, att, subcat=None, log10=False, 
                 asgrid=False, fmt='%.8e', header='',delimiter=' '):
        
        if not subcat:
            data = getattr(self, att)[:]
        else:
            data = getattr(self, att)[subcat][:]
        if log10:
            data = np.log10([i for i in data])
        if asgrid:
            data = np.hstack((self.grid[:,:2], data.reshape(-1,1)))           
        
        np.savetxt(self.dir['store']+filename, data, fmt=fmt, header=header,
                   delimiter=delimiter)
        
        
    def model2vti(self, filename, fields, subcats, res_0, res_i,
                  log10_cols=[], bounds=None, new_names=None,
                  resample='nearest',  crs_0='EPSG:4326', crs_f='EPSG:4326'):
        
        data = []
        array_names = []
        for attr in fields:
            fx = getattr(self, attr)

            if isinstance(fx, dict):  #Check that field is dict
                for subcat in subcats:
                    array_names.append(attr + '_' + str(subcat))
                    data.append(fx[subcat])
            elif isinstance(fx,(list, np.ndarray)):
                array_names.append(attr)
                data.append(fx)
        if new_names:
            array_names = new_names
        data = np.array(data).T
        
#        print(data.shape)
        assert data.shape[0]==self.grid_int.shape[0],\
                            'Dimension not matching'
        
        for i in log10_cols:
            data[:,i] = np.log10(data[:,i])
            array_names[i] += '_log'
            
            
        _,raster_fn = pl.rasterize_results(self.dir['store'],
                                           filename,
                                           data,
                                           array_names,
                                           self.grid_int,
                                           res_0)        
        
        raster_rpj = raster_fn.split('.tiff')[0] + crs_f + '.tiff'
        
        if bounds:

            pl.reproject_rio(raster_fn,
                             raster_rpj,
                             dst_CRS=crs_0,
                             res=res_0,
                             bounds=bounds,
                             resample='nearest')      
            
            pl.reproject_rio(raster_rpj,
                             raster_rpj,
                             dst_CRS=crs_f,
                             res=res_i,
                             resample=resample)      
        else:
            pl.reproject_rio(raster_fn,
                             raster_rpj,
                             dst_CRS=crs_f,
                             res=res_i,
                             resample=resample)               
            
        im = pl.raster2vti(self.dir['vtk'] + filename + '.vti',
                       [raster_rpj], 
                       [array_names], offset=10)
        return im
    

    def model2nDvtk(self, filename, fields, res_0, res_i, subsets={},
                  log_var=[], bounds=None, names={}, group_arrays=[],
                  resample='nearest',  crs_0='EPSG:4326', crs_f='EPSG:4326'):
        
        data = []
        array_names = []
        index = 0
        data_struct = {i:[] for i in group_arrays}
        for i in group_arrays:
            if i in names:
                data_struct.pop(i)
                new_name = names[i]
                if i in log_var:
                    new_name += '_log'
                data_struct[new_name] = []
            else:
                if i in log_var:
                    new_name = i + '_log'
                    data_struct.pop(i)
                    data_struct[new_name] = []
                
        for attr in fields:
            fx = getattr(self, attr)
            print('Retrieving attribute ' + attr)
            
            
            ## Class attribute is multivariable array
            if isinstance(fx, dict):  #Check that field is dict
                print('  Attribute field is a dict')
                if attr in subsets:     
                # The attr is flagged, only a subset(s) to be saved
                    if not isinstance(subsets[attr], list):   ##Only a string
                        catalogs = [subsets[attr]]
                    else:   ## An iterable
                        catalogs = subsets[attr]
                    print('    Only subsets ' + ",".join(
                            [str(k) for k in catalogs]) + ' will be saved')
                    
                    for cat in catalogs:                        
                        array = fx[cat]                        
                        if isinstance(data, (list, np.ndarray)):
                            sufix = ''
                            
                            #Check Log flag
                            if attr in log_var:
                                data.append(np.log10(array))
                                sufix += '_log'
                            else:
                                data.append(array)    
                                
                            # Check rename flag
                            if attr in names:
                                array_names.append(names[attr] + '_' +
                                                   str(cat) + sufix)
                            else:
                                array_names.append(attr + '_' + str(cat) 
                                                    + sufix)
                            
                            # Check group flag
                            if attr in group_arrays:
                                if attr in names:
                                    data_struct[names[attr] + sufix].\
                                                        append(index)
                                else:
                                    data_struct[attr + sufix].append(index)
                            else:
                                data_struct[array_names[-1]] = [index]
                            index += 1   
                            
                            
                        else:
                            raise Exception('Pointed attribute is not at the\
                                            end of the data tree')
                else:
                    # All subsets are saved
                     print('    All catalogs (' + ",".join([str(k)
                                 for k in fx.keys()]) + ') will be saved')
               
                     for key, array in fx.items():                                      
                        if isinstance(data, (list, np.ndarray)):
                            sufix = ''
                            
                            if attr in log_var: # Log Flag
                                data.append(np.log10(array))
                                sufix += '_log'
                            else:
                                data.append(array)   
                                
                            if attr in names:   # Rename flag
                                array_names.append(names[attr] + '_' +
                                                   str(key) + sufix)
                            else:
                                array_names.append(attr + '_' + str(key)
                                                        + sufix)
                                
                            if attr in group_arrays:
                                if attr in names:
                                    data_struct[names[attr] + sufix].\
                                                        append(index)
                                else:
                                    data_struct[attr + sufix].append(index)
                            else:
                                data_struct[array_names[-1]] = [index]
                            index += 1                            
                        else:
                            raise Exception('Pointed attribute is not at the\
                                            end of the data tree')                    


                    ### Build exceptions
                    
                    
            ## Class attribute is single array     
            elif isinstance(fx,(list, np.ndarray)):
                print('  Attribute is a scalar')
                sufix = ''
                if attr in log_var:
                    data.append(np.log10(fx))
                    sufix += '_log'
                else:
                    data.append(fx)
                    
                if attr in names:
                    array_names.append(names[attr] + sufix)
                else:
                    array_names.append(attr + sufix)
                
                data_struct[array_names[-1]] = [index]
                index += 1       

        log = 'VTK Data Structure\n'
        for i,j in data_struct.items():
            log += '  Array name - ' + i + '\n'
            for n, k in enumerate(j):
                log += '    %i - ' % n + array_names[k] +'\n'
        print(log)
        with open(self.dir['vtk'] + filename + '.log', 'w') as f:
            print(log, file=f)
            

        data = np.array(data).T
        assert data.shape[0]==self.grid_int.shape[0],\
                            'Dimension not matching'
        
            
        _,raster_fn = pl.rasterize_results(self.dir['store'],
                                           filename,
                                           data,
                                           array_names,
                                           self.grid_int,
                                           res_0)        
        
        raster_rpj = raster_fn.split('.tiff')[0] + crs_f + '.tiff'
        
        if bounds:

            pl.reproject_rio(raster_fn,
                             raster_rpj,
                             dst_CRS=crs_0,
                             res=res_0,
                             bounds=bounds,
                             resample='nearest')      
            
            pl.reproject_rio(raster_rpj,
                             raster_rpj,
                             dst_CRS=crs_f,
                             res=res_i,
                             resample=resample)      
        else:
            pl.reproject_rio(raster_fn,
                             raster_rpj,
                             dst_CRS=crs_f,
                             res=res_i,
                             resample=resample)               
#        
#        im = pl.raster2vti(self.dir['vtk'] + filename + '.vti',
#                       [raster_rpj], 
#                       [grouping], offset=10)
#            
        im = pl.raster2vti2(self.dir['vtk'] + filename + '.vti',
                       raster_rpj, 
                       data_struct, offset=10)
        return im

    
    

if __name__ == '__main__':
    
# =============================================================================
# Building SSM from scratch    
# =============================================================================

    print("Executing from module")
    
    model_dir = '../full_model/'
    
    
    catalog_fn = model_dir + 'input/Data_Catalog_complete.txt'
    fault_fn = model_dir + 'input/Data_Faults.txt'
    grid_fn = model_dir + 'input/Cells_Collect.txt'
    basemap_fn = model_dir + 'basemap/blue_basemap.tiff'      


# =============================================================================
# Load input
# =============================================================================
    sf = ssm_model('full', model_dir)

    sf.set_grid(grid_fn, mask=True)  
    sf.set_catalog(catalog_fn, 'sheec')
    sf.set_faults(fault_fn, 'edsf')  

# =============================================================================
# Calculating distances (for memory issues, results 
# can be dropped into a file, and then reloaded)
# =============================================================================
  
#    dtype = 'f2'
#    sf.set_distances('catalog', 'grid', drop=True, dtype=dtype)
#    sf.set_distances('catalog','catalog', drop=True, dtype=dtype)
#    sf.set_distances('faults','grid', drop=True, dtype=dtype)    



# =============================================================================
# Calibrating model parameters
# =============================================================================
    
#    plt.close('all')
    
    # Set test grid (the model grid, redefined in term of cell boundaries)
#    sf.set_testgrid((0.1,0.1))

    ### Fix Kernel
#    r_disc = [2., 5., 8., 10., 12., 15., 20., 30., 50. ]   
#    # Load distances        
#    sf.load_distances('catalog','grid')
#    sf.load_distances('catalog','catalog')
#    # Select target catalog 
#    sf.set_subcatalog('2002-', time=(datetime.datetime(2002,1,1),
#                                     datetime.datetime.now()), minmag=5.0)
#    # Select training catalog
#    sf.set_subcatalog('-2002', time=(datetime.datetime(800,1,1),   
#                                     datetime.datetime(2002,1,1)))    
#    _, r = sf.calibrate_fixKernel('-2002','2002-', r_disc,
#                                   plot=True, save=True)
#    
#    
#    ### Variable Kernel
#    n_disc = [1, 2, 3, 4, 5, 10, 15]
#    sf.set_subcatalog('2002-', time=(datetime.datetime(2002,1,1),
#                                     datetime.datetime.now()), minmag=5.0)    
#    sf.set_subcatalog('-2002', time=(datetime.datetime(1980,1,1),
#                                     datetime.datetime(2002,1,1)))  
#    _, n = sf.calibrate_varKernel('-2002','2002-',n_disc, 
#                                   plot=True, save=True)   
#
#    # Load saved results, if desired.
#    sf.load_fix_calibration('-2002','2002-')
#    sf.load_var_calibration('-2002','2002-')
    
    
# =============================================================================
# Calculating and saving ssm    
# =============================================================================
    
    # Regular ssm calculation. 
#    sf.load_distances('catalog','grid')
#    sf.load_distances('catalog','catalog')

#    sf.get_catalogSSM_varKernel(N=2, dist_cutoff=0., mc_min=5.0)
#    sf.save_pdf('catalog_var', 'full')
#    sf.get_catalogSSM_varKernel(N=2, mc_min=5.0,dmin=0., memclean=True)
#    sf.save_pdf('catalog_var', 'full')
#    sf.get_catalogSSM_fixKernel(KernelSize=10., memclean=True)    
#    sf.save_pdf('catalog_fix', 'full')
#
#    sf.set_subfaults(name='na',polygon=sf.dir['model'] +
#                     './input/europe_NA_shp/Europe_noAfrica_crop.shp')
#    sf.load_distances('faults','grid')      
#    sf.get_faultSSM_fixKernel(subfault = 'na', KernelSize=10., memclean=True)    
#    sf.save_pdf('faults', 'na')



# =============================================================================
#    Calibration of weight function
# =============================================================================
#    
#    
#    # Mask Fault SSM by its total contribution up to a cutoff limit
#    sf.load_pdf('faults', 'na')
#    a = sf.get_cdf_mask('pdfx_faults', 'na', 0.975)
#    
#     # Create test grid using the mask
#    sf.set_testgrid((0.1,0.1), mask=sf.mask_faults['na']) 
#    
#    # Set training subcatalog
#    sf.set_subcatalog('-1987', time=(datetime.datetime(800,1,1),   
#                                     datetime.datetime(1987,1,1)))  
#    sf.load_distances('catalog','grid')
#    sf.load_distances('catalog','catalog')
#    sf.get_catalogSSM_varKernel(subcat='-1987',N=2, dist_cutoff=0.)
#    sf.save_pdf('catalog_var', '-1987')  
#    
#    # Calibration parameters
#    sf.load_pdf('catalog_var', '-1987')
#    mw_lowcutoff = 5.5
#    mw_highcutoff = 7.5
#    w_min = 0.
#    dmw = 0.1
#    mw_disc = np.round(np.arange(4.5, 7.6, dmw),1)
#    weight_disc = np.arange(0.0, 1.05, 0.05)  
#    sf.calibrate_weight(training_cat='-1987',
#                            target_cat='1987-',
#                            target_cat_time=(datetime.datetime(1987,1,1),
#                                             datetime.datetime.now()),
#                            fault_subcat='na',
#                            mask=sf.mask_faults['na'],
#                            mw_disc=mw_disc,
#                            mw_lowcutoff=mw_lowcutoff,
#                            mw_highcutoff=mw_highcutoff,
#                            w_min=w_min,
#                            dmw=dmw,
#                            weight_disc=weight_disc,
#                            plot=True, save=True)
#    
#    # Load previously saved results
#    sf.load_seismic_calibration(training_cat='-1987',
#                            target_cat='1987-')
#    
    
# =============================================================================
#   Get final forecast
# =============================================================================
    mw_lowcutoff = 4.8795
    mw_highcutoff = 7.0
    w_min=0.
    Mw_min = 4.5
    Mw_max = 8.5
    dmw = 0.1
    mw_precision = 1   # for floating point arithmetics
    mw_disc = np.round(np.arange(Mw_min, Mw_max + dmw, dmw), mw_precision)
    
    training_cat = '-1987'
    target_cat = '1987-'
    sf.load_seismic_calibration(training_cat=training_cat,
                            target_cat=target_cat)
    sf.seismic_weight['full'] = sf.seismic_weight[(training_cat, target_cat)]
    
    sf.load_pdf('catalog_var', 'full')
    sf.load_pdf('faults', 'na')    
    sf.get_cdf_mask('pdfx_faults', 'na', 0.975)
   
    a,b = sf.get_weighted_pdfx('full','na',
                             sf.mask_faults['na'],
                             mw_disc,
                             f=piecewise_linear,
                             params=[0.7725, 0.1364])
    
#    sf.get_magPDF(Mw_max, a, b, Mw_target, bin_size=0.1)               

# =============================================================================
#  Matlab
# =============================================================================
#    sf.mask = np.genfromtxt(sf.dir['model'] + '/input/Cells_Collect.txt')[:,-1]
#    sf.grid = sf.grid[sf.mask==1]
# 
#    sf.pdfx_seismic_m = np.genfromtxt(
#            '../matlab/model_b/Store/Spatial_PDF_Seismicity.txt')[:,-2]
#    sf.pdfx_mask_m = np.genfromtxt(
#            '../matlab/model_b/Store/mask.txt')
    sf.pdfx_faults_m = np.genfromtxt(
            '../matlab/model_b/Store/Spatial_PDF_Faults.txt')[:,-2]
#    sf.pdfx_weigh_ml = np.genfromtxt(
#            '../matlab/model_b/Store/forecast_mw5.9.txt', delimiter=',')[:,-2]
#    
#    print(max(np.abs((np.log10(sf.pdfx_weigh_ml)-
#                      np.log10(sf.pdfx_weighted['full']))/
#                                        np.log10(sf.pdfx_weigh_ml))))
## =============================================================================
##    Saving raster
## =============================================================================
#   
    # CRS of exported vtk
    crs_f = 'EPSG:102014'
   #  Resolution of the original grid
    res_0 = (0.1000001, 0.1000001)
    # Export resolution in the output CRS
    res_f = (5000,5000)
    # Subcatalogs
    subcats = mw_disc
    
    sf.load_pdf('faults', 'na')
    sf.load_pdf('faults', 'full')
    sf.load_pdf('catalog_var', 'full')
    sf.load_pdf('catalog_var', '-1987')
#    sf.load_pdf('catalog_fix', 'full')
    
#    sf.load_pdf('catalog_var', 'full')
    
#    sf.model2vti('Full_model',
#                 ['pdfx_catalog_vk',
#                  'pdfx_catalog_fk',
#                  'pdfx_faults'],
#                 subcats, res_0, res_f,
#                 new_names=['VarKernel',
#                            'FixKernel',
#                            'Faults'],
#                 resample='nearest',
#                 log10_cols=[0,1,2],
#                 crs_f=crs_f)
#
#    sf.model2vti('Full_model',
#                 ['pdfx_faults',
#                  'pdfx_faults_m'],
#                 subcats, res_0, res_f,
#                 new_names=['faults_py',
#                            'faults_ml'],
#                 resample='nearest',
#                 log10_cols=[0,1],
#                 crs_f=crs_f)
    
    im = sf.model2nDvti('Full_model',
                     ['pdfx_faults', 'pdfx_catalog_vk', 'pdfx_mw', 'cdfx_mw'],
                     res_0, res_f,
                     subsets={'pdfx_faults' : 'full',
                              'pdfx_catalog_vk' : 'full',
                              'pdfx_mw' : [4.5, 5.5, 6.5, 7.5, 8.5],
                              'cdfx_mw' : [4.5, 5.5, 6.5, 7.5, 8.5]},
                     names={},
                     log_var=['pdfx_faults', 'pdfx_mw', 'cdfx_mw'],
                     group_arrays=['pdfx_mw', 'cdfx_mw'],
                     resample='nearest',
                     crs_f=crs_f)
    

# =============================================================================
#   Create Basemap
# =============================================================================


#    rgb_input = './store/blue_basemap.tiff'      
#    rgb_crp = './store/blue_basemap_crp.tiff'
#    rgb_rpj = './store/blue_basemap_rpj.tiff'  
#    rgb_input_crs = rasterio.open(rgb_input).crs.to_string()
#    rgb_input_res = rasterio.open(rgb_input).res
#    rgb_output_res = 2000
#    
#    ### Match basemap extent to results extent
#    Map_bounds = rasterio.open(sf.dir['store'] + 'Full_model.tiff').bounds
#    pl.reproject_rio(rgb_input, rgb_crp, dst_CRS=rgb_input_crs,
#                     bounds=Map_bounds,res=rgb_input_res[0])
#    
#    ### Reproject to final crs resolution
#    pl.reproject_rio(rgb_crp, rgb_rpj, dst_CRS='EPSG:102014', 
#                     res=rgb_output_res)   
#
#
#
#    bm_img = pl.raster2vti( model_dir + '/vtk/blue_basemap.vti',
#                           [rgb_rpj], 
#                           [['basemap']], mask_rgb = [0,0,0])
   
    
    
# =============================================================================
# example Disjoint subcatalog    
# =============================================================================


#    sf.set_subcatalog('-1997', time=(datetime.datetime(800,1,1),
#                                     datetime.datetime(1997,1,1)))    
#    sf.set_subcatalog('1997-2002', time=(datetime.datetime(1997,1,1),
#                                     datetime.datetime(2002,1,1)),
#                                                         minmag=5.0)
#    inds = sf.subcatalog['-1997']['ind']
#    inds.extend(sf.subcatalog['2002-']['ind'])
#    sf.set_subcatalog('-1997,2002-', specific=inds)
    