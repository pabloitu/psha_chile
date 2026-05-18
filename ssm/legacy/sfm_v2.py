#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:07:58 2020

@author: pciturri
"""

import datetime, time
import numpy as np
import fiona
import matplotlib.pyplot as plt
import psutil
import gc
import h5py
import scipy.special as scp
from shapely.geometry import Point, shape
from multiprocessing import Pool
from functools import partial




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
    precision=12
    dtheta = (np.sin(geom[0][1]) * geom[1][:,2] +
              np.cos(geom[0][1]) * geom[1][:,1] *
              np.cos(geom[1][:,0] - geom[0][0]))

    row =  6371. * np.arccos(np.round(dtheta, precision))
    return row

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
    
    
    def __init__(self, name):
        
        self.name = name
        self.toc = datetime.datetime.now()
        self.catalog = []
        self.faults = []
        self.dists = {}
        self.subcatalog = {}    
        self.subfaults = {}
        self.pdfx_faults = {}
        self.pdfx_catalog_vk = {}
        self.pdfx_catalog_fk = {}
        self.testgrid = {}
        self.L_r = {}
        self.G_r = {}
        self.L_n = {}
        self.G_n = {}
    
  
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
            
    def set_grid(self, filename):
        
        """
        Load the model's grid.
        """
        
        ### Input columns: [left-bot-corner lon, left-bot-corner lat,
        ###                 center lon, center lat, cell area]
        
        self.grid = np.genfromtxt(filename)[:,3:]
        
        
    # ============================= #
    #     Data handling methods     #
    # ============================= #
    
    
    def set_subcatalog(self, name, specific=None, minmag=None, depth=None,
                       nan_inc=False, bbox=None, polygon=None, time=None):
        
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
            subfaults = np.array(self.faults)[specific]
        else:
            subfaults = np.array(self.faults[:])
            
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

        indexes = [self.faults.index(i) for i in subfaults.tolist()
                                           if i in self.faults[:]]
        self.subfaults[name] = {'faults': subfaults, 'ind': indexes}    


    def set_testgrid(self, res):
        
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

        x = np.arange(sf.grid[:,0].min()-res[0]/2.,
                      sf.grid[:,0].max()+3./2.*res[0], res[0])
        y = np.arange(sf.grid[:,1].min()-res[1]/2.,
                      sf.grid[:,1].max()+3./2.*res[1], res[1])   
        testgrid = []
        for i in self.grid:
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
            
            
            filename = 'd_' + att1 + '_' +att2
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




    # ============================== #
    #   Model construction methods   #
    # ============================== #            
            
            
    def get_catalogSSM_varKernel(self, subcat ='full', N=2, power=1.5,
                                 mc_min=4.5, area_norm=True,
                                 sum_norm=True, nproc=16, 
                                 memclean=False):
        
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

        grid = self.grid

        print ("Starting catalog variable-size kernel smoothing\n" +
               "\tsub-catalog used: " + subcat + "\n" +
               "\tnumber of events: %i\n" % catalog.shape[0] +
               "\tnumber of cells: %i\n" % grid.shape[0] +
               "\tnumber of processes: %i\n" % nproc)       

        
        # Calculate distances between all events
        d_cat2cat = self.dists[('catalog','catalog')][cat_ind,:][:,cat_ind]
        kernel_size = np.sort(d_cat2cat).T[N,:]    
        catalog[np.where(catalog[:,6] >= mc_min), 6] = mc_min
        
        pdfX = np.zeros(grid.shape[0])


        for i, j, k in zip(self.dists[('catalog','grid')][cat_ind,:],
                                      kernel_size, catalog[:, 5:]):
            kernel_i = 1./((i**2 + j**2)**power)  
            kernel_i /= np.sum(kernel_i)/(10**(k[1] - mc_min)/k[0])
            pdfX += kernel_i 

        if area_norm:
            pdfX /= grid[:,2]

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
                                 nproc=16, mag_scaling=False, mc_min=False):
        
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
        grid = self.grid

        print ("Starting catalog fixed-size kernel smoothing\n" +
               "\tnumber of events: %i\n" % catalog.shape[0] +
               "\tnumber of cells: %i\n" % grid.shape[0] +
               "\tnumber of processes: %i\n" % nproc +
               "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])       

        
        # Calculate distances between all events

        pdfX = np.zeros(grid.shape[0])
        for i,j in zip(self.dists[('catalog','grid')][cat_ind,:], catalog):
            
            kernel_i = 1./((i**2 + KernelSize**2)**power)
            kernel_i /= (np.sum(kernel_i))
            
            if mag_scaling:
                kernel_i *= j[3]
            if mc_min:
                kernel_i*=(10**(j[6] - mc_min)/j[5])
            pdfX += kernel_i

        if area_norm:
            pdfX /= grid[:,2]

        if sum_norm:
            pdfX /= np.sum(pdfX)
            
        self.pdfx_catalog_fk[subcat] = pdfX[:]

        print("Catalog fixed-size kernel smoothing complete.\n\
              \ttime taken: %i seconds \n" % (time.process_time() - start) +
              "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])
        
    
        
        
    def get_faultSSM_fixKernel(self, subfault='full', KernelSize=10.,
                               power=1.5, pond=1, area_norm=True, 
                               sum_norm=True, nproc=16, dist_memclean=False):
        
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
        grid = self.grid          

        print ("Starting faults fixed-size kernel smoothing\n" +
               "\tnumber of events: %i\n" % len(faults) +
               "\tnumber of cells: %i\n" % len(grid) +
               "\tnumber of processes: %i\n" % nproc)    
         

        pdfX = np.zeros(grid.shape[0])
        for i,j in zip(self.dists[('faults','grid')][faults_ind,:], faults):
            kernel_i = 1./((i**2 + KernelSize**2)**power)
            kernel_i /= (np.sum(kernel_i)*j[-1]/j[-2])
            pdfX += kernel_i


        if area_norm:
            pdfX /= grid[:,2]
        
        if sum_norm:
            pdfX /= np.sum(pdfX)
        
        if dist_memclean:
            self.dists.pop(('faults', 'grid'))
        
        print("Faults fixed-size kernel smoothing complete.\n\
              \ttime taken: %i seconds \n" % (time.process_time() - start) +
              "\tmemory use: %.1f\n\n" % psutil.virtual_memory()[2])
        
        self.pdfx_faults[subfault] = pdfX[:]



    # ====================================== #
    #   Model spatial calibration methods    #
    # ====================================== #
        

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
        r = findCellsParallel(catalog[:,:2],testgrid)
        results = np.unique(r, return_counts=True)
        inside = False==np.isnan(results[0])
        omega[results[0][inside].astype('int')] = results[1][inside]
        
        return omega     
    
    


    
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

    

    
    def calibrate_fixKernel(self, training_cat, target_cat, r_disc,
                            model_area_norm=True, ref_area_norm=False,
                            mag_scaling=False, Mc_min=False):
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
    
        n_cells = self.grid.shape[0]
        pdfx_uniform = 1./n_cells*np.ones(n_cells)
        if ref_area_norm:
            pdfx_uniform /= self.grid[:,2]
            pdfx_uniform /= np.sum(pdfx_uniform)
        pdfx_uniform *= Nt
        
        logL_uni = 0
        for i in range(omega.shape[0]):
            logL_uni += -pdfx_uniform[i] + \
                             omega[i]*np.log10(pdfx_uniform[i]) -\
                             np.log10(scp.factorial(omega[i]))

        for r in r_disc:
            logL[r] = 0
            
            self.get_catalogSSM_fixKernel(subcat=training_cat, KernelSize=r,
                                      area_norm=model_area_norm,
                                      mag_scaling=mag_scaling,
                                      target_mw=Mc_min)
            
            mu = Nt*self.pdfx_catalog_fk[training_cat][:] 
                
            for i in range(omega.shape[0]):
                logL[r] += -mu[i] + omega[i]*np.log10(mu[i]) -\
                            np.log10(scp.factorial(omega[i]))
            
            G[r] = 10**((logL[r]-logL_uni)/Nt)
            
        self.G_r[(training_cat,target_cat)] = {'r': r_disc,
                                               'L_ref': logL_uni,
                                               'L': logL,
                                               'G': G}

        
    def calibrate_varKernel(self, training_cat, target_cat, n_disc,
                            model_area_norm=True, ref_area_norm=False,
                            Mc_min=4.5): 
        
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
    
        n_cells = self.grid.shape[0]
        pdfx_uniform = 1./n_cells*np.ones(n_cells)
        if ref_area_norm:
            pdfx_uniform /= self.grid[:,2]
            pdfx_uniform /= np.sum(pdfx_uniform)
        pdfx_uniform *= Nt
        
        logL_uni = 0
        for i in range(omega.shape[0]):
            logL_uni += -pdfx_uniform[i] + \
                             omega[i]*np.log10(pdfx_uniform[i]) -\
                             np.log10(scp.factorial(omega[i]))
        self.logL_uni = logL_uni
        
        for n in n_disc:
            logL[n] = 0
            self.get_catalogSSM_varKernel(subcat=training_cat, N=n,
                                          target_mw=Mc_min,
                                          area_norm=model_area_norm)   
            
            mu = Nt*self.pdfx_catalog_vk[training_cat][:] 
                
            for i in range(omega.shape[0]):
                logL[n] += -mu[i] + omega[i]*np.log10(mu[i]) -\
                            np.log10(scp.factorial(omega[i]))
            
            G[n] = 10**((logL[n]-self.logL_uni)/Nt)
            
        self.G_n[(training_cat,target_cat)] = {'N': n_disc,
                                               'L_ref': logL_uni,
                                               'L': logL,
                                               'G': G}


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
        filename = 'd_' + att1 + '_' +att2
        f = h5py.File(filename, 'r')
        self.dists[(att1, att2)] = f['dist'][:]
        f.close()
        gc.collect()
        
        
    def load_pdf(self, pdf_type, subcat, filename):
        
        
        data = np.genfromtxt(filename)
        if pdf_type == 'catalog_fix':
            self.pdfx_catalog_fk[subcat] = data
        elif pdf_type == 'catalog_var':
            self.pdfx_catalog_vk[subcat] = data
        elif pdf_type == 'fault_fix':
            self.pdfx_faults[subcat] = data
            
            
    def save_pdf(self, pdf_type, subcat, filename,
                 fmt='%.12f', header='',delimiter=' '):
        
        if pdf_type == 'catalog_fix':
            data = self.pdfx_catalog_fk[subcat]
        elif pdf_type == 'catalog_var':
            data = self.pdfx_catalog_vk[subcat]
        elif pdf_type == 'fault_fix':
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
        
        np.savetxt(filename, data, fmt=fmt, header=header,
                   delimiter=delimiter)
        
        
   
if __name__ == '__main__':
    
    print("Executing from module")
    
    catalog_fn = '../matlab/Input/Data_Catalog_complete.txt'
    fault_fn = '../matlab/Input/Data_Faults.txt'
    grid_fn = '../matlab/Input/Cells_Model.txt'

    sf = ssm_model('test')

    sf.set_grid(grid_fn)  
    sf.set_catalog(catalog_fn, 'sheec')
    sf.set_faults(fault_fn, 'edsf')  
    
#    sf.set_subcatalog(name='asd',specific=[-4,-3,-2,-1])

#    sf.set_distances('catalog', 'grid', drop=True, dtype='d')
#    sf.set_distances('catalog','catalog',drop=True, dtype='d')
#    sf.set_distances('faults','grid',drop=True, dtype='f')    

    
#    sf.load_distances('catalog','grid')
#    sf.load_distances('catalog','catalog')
    sf.load_distances('faults','grid')   
    sf.get_faultSSM_fixKernel()    
#    sf.save_txt('python_fault_pdfx.txt', 'pdfx_faults',
#                 subcat='full', log10=True, asgrid=True)
#    sf.get_catalogSSM_varKernel(area_norm=True, sum_norm=True, 
#                                dist_memclean=True)
    

    
#    sf.set_subcatalog('2004-', time=(datetime.datetime(2004,1,1),
#                                     datetime.datetime.now()))
#    sf.set_subcatalog('-2004', time=(datetime.datetime(800,1,1),
#                                     datetime.datetime(2004,1,1)))
#    sf.set_subfaults('asd', specific=np.arange(9999,10999).tolist())

#    sf.get_faultSSM_fixKernel(area_norm=True, sum_norm=True)
#    sf.get_catalogSSM_varKernel(area_norm=True, sum_norm=True)
    
    
#    sf.save_txt('python_pdfx_faults.txt', 'pdfx_faults', subcat='full', 
#              log10=True, asgrid=True)    
#    sf.save_txt('python_pdfx.txt', 'pdfx_catalog_vk', subcat='2004-',
#             log10=True, asgrid=True)




#    sf.create_testgrid((0.1,0.1))    
#    sf.set_subcatalog('2002-', time=(datetime.datetime(2002,1,1),
#                                     datetime.datetime.now()), minmag=5.0)
#    sf.set_subcatalog('-2002', time=(datetime.datetime(800,1,1),
#                                     datetime.datetime(2002,1,1)))    
#
#    sf.calibrate_fixKernel('-2002','2002-',[5.,10.,15.,20.,25.,30.,50.])
    
    
#    sf.set_subcatalog('2002-', time=(datetime.datetime(2002,1,1),
#                                     datetime.datetime.now()), minmag=5.0)    
#    sf.set_subcatalog('-2002', time=(datetime.datetime(800,1,1),
#                                     datetime.datetime(2002,1,1)))  
#    sf.calibrate_varKernel('-2002','2002-',[1,2,3,4,5,6,7,8,9,10])    


#    sf.set_subcatalog('-1997', time=(datetime.datetime(800,1,1),
#                                     datetime.datetime(1997,1,1)))    
#    sf.set_subcatalog('1997-2002', time=(datetime.datetime(1997,1,1),
#                                     datetime.datetime(2002,1,1)),
#                                                         minmag=5.0)
#    inds = sf.subcatalog['-1997']['ind']
#    inds.extend(sf.subcatalog['2002-']['ind'])
#    sf.set_subcatalog('-1997,2002-', specific=inds)
    
    
    
    
#    sf.get_magPDF(8.5, 5.8672, 0.9, 4.5)