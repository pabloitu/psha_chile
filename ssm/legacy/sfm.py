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
from shapely.geometry import Point, shape
from functools import reduce
from multiprocessing import Pool



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
    precision=14
    
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
    for parallelization efficiency
    Input:
        - geom[0] (dtype=list/array, shape=(2,)):
                    Single point to evaluate distances (in radians)
        - geom[1] (dtype=list of 3 array), shape=(3, (n,3)):
                    List of 3 arrays of the grid geom:
                        geom[1][0] (dtype=array, shape(n,): lon      (in rads.)
                        geom[1][1] (dtype=array, shape(n,): cos(lat) (in rads.)
                        geom[1][2] (dtype=array, shape(n,): sin(lat) (in rads.)
    """
    precision=14
    dtheta = (np.sin(geom[0][1]) * geom[1][2] +
              np.cos(geom[0][1]) * geom[1][1] *
              np.cos(geom[1][0] - geom[0][0]))

    row =  6371. * np.arccos(np.round(dtheta, precision))

    return row

def fixKernel_eqkSpatialContribution(Input):
    """
    Calculathes an individual event's spatial contribution to the entire grid.
    Input:
    - Input[0] (dtype=list): event data:
                                [0]: longitude
                                [1]: latitude
                                [2]: magnitude
                                [3]: time of completeness
                                [4]: magnitude of completeness
    - Input[1] (dtype=float): Initial Kernel Size (N-th closest event distance)
    - Input[2] (dtype=array, shape=(m,2)): Complete grid
    - Input[3] (dtype=float): Power of the Kernel method
    - Input[4] (dtype=float): Target forecasting magnitude
    
    """
    eqk_lon = Input[0][0]
    eqk_lat = Input[0][1]
    eqk_mw = Input[0][2]
    eqk_num = Input[0][3]

    KernelSize = Input[1]
    grid_x = Input[2][:,0]
    grid_cosy = Input[2][:,1]
    grid_siny = Input[2][:,2]
    Power = Input[3]
    
    r_dist = dist_p2grid([[np.deg2rad(eqk_lon), np.deg2rad(eqk_lat)],
                           [grid_x, grid_cosy, grid_siny]])
    
    kernel_values = 1./((r_dist**2 + KernelSize**2)**Power)  
    total_kernelarea = np.sum(kernel_values)   
    
    spatial_contribution = kernel_values / total_kernelarea / eqk_num
                           
    return eqk_mw * spatial_contribution



def varKernel_eqkSpatialContribution(Input):
    """
    Calculathes an individual event's spatial contribution to the entire grid.
    Input:
    - Input[0] (dtype=list): event data:
                                [0]: longitude
                                [1]: latitude
                                [2]: magnitude
                                [3]: time of completeness
                                [4]: magnitude of completeness
    - Input[1] (dtype=float): Initial Kernel Size (N-th closest event distance)
    - Input[2] (dtype=array, shape=(m,2)): Complete grid
    - Input[3] (dtype=float): Power of the Kernel method
    - Input[4] (dtype=float): Target forecasting magnitude
    
    """
    eqk_lon = Input[0][0]
    eqk_lat = Input[0][1]
    eqk_t = Input[0][5]
    eqk_mc = Input[0][6]
    
    KernelSize = Input[1]
    grid_x = Input[2][:,0]
    grid_cosy = Input[2][:,1]
    grid_siny = Input[2][:,2]
    Power = Input[3]
    target_mw = Input[4]
    

    r_dist = dist_p2grid([[np.deg2rad(eqk_lon), np.deg2rad(eqk_lat)],
                           [grid_x, grid_cosy, grid_siny]])

    kernel_values = 1./((r_dist**2 + KernelSize**2)**Power)  
   
    total_kernelarea = np.sum(kernel_values)   
        
    spatial_contribution = kernel_values / total_kernelarea *\
                           10**(eqk_mc - target_mw) / eqk_t
                           
    return spatial_contribution


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
        self.subcatalog = {}    
        self.subfaults = {}
        self.pdfx_faults = {}
        self.pdfx_catalog = {}
        
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
                            i[10], i[11]]   
                            for i in raw]       # Event corrected completeness
            self.subcatalog['full'] = self.catalog[:]


            
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
            self.faults = np.array([raw[:,x] if x!=5 
                                        else 10**(1.5*raw[:,x] + 9.0) 
                                    for x in [0,1,5]]).T
            self.subfaults['full'] = self.faults[:]
    def set_grid(self, filename):
        
        """
        Load the model's grid.
        """
        
        ### Input columns: [left-bot-corner lon, left-bot-corner lat,
        ###                 center lon, center lat, cell area]
        
        self.grid = np.genfromtxt(filename)[:,3:]
        

    def set_subcatalog(self, name, specific=None, depth=None, nan_inc=False,
                             bbox=None, polygon=None, time=None):
        
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
        
        """
        if specific:
            self.subcatalog[name] = self.catalog[specific]
        else:
            self.subcatalog[name] = self.catalog[:]
            
        if depth:
            if nan_inc:
                self.subcatalog[name] = [i for i in self.subcatalog[name]
                                           if depth[0] < i[4] < depth[1]
                                               or np.isnan(i[4])]
            else:
                self.subcatalog[name] = [i for i in self.subcatalog[name]
                                           if depth[0] < i[4] < depth[1]]
        
        if bbox:
            self.subcatalog[name] = [i for i in self.subcatalog[name]
                                     if bbox[0][0] < i[0] < bbox[0][1]
                                         and bbox[1][0] < i[1] < bbox[1][1]]           
        
        if polygon:
            shpfile = fiona.open(polygon)
            poly = next(iter(shpfile))
            self.subcatalog[name] = [i for i in self.subcatalog[name]
                                        if Point(i[0], i[1]).within(
                                                shape(poly['geometry']))]

        if time:
            self.subcatalog[name] = [i for i in self.subcatalog[name]
                                        if time[0] <= i[2] < time[1]]
            

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
        
        """
        
        if specific:
            self.subfaults[name] = self.faults[specific]
        else:
            self.subfaults[name] = self.faults[:]
            
        if bbox:
            self.subfaults[name] = [i for i in self.subfaults[name]
                                     if bbox[0][0] < i[0] < bbox[0][1]
                                         and bbox[1][0] < i[1] < bbox[1][1]]           
        
        if polygon:
            shpfile = fiona.open(polygon)
            poly = next(iter(shpfile))
            self.subfaults[name] = [i for i in self.subfaults[name]
                                        if Point(i[0], i[1]).within(
                                                shape(poly['geometry']))]


            
            
            
    def get_catalogSSM(self, subcat ='full', N=2, power=1.5, target_mw=5.0,
                       area_norm=False, sum_norm=False, nproc=16):
        
        """
        Variable-sized Kernel smoothing from Helmstetter et al, 2007
        Modified from func_kernelvariable.m developed by Hiemer, S. in matlab
        
        Input
        - subcat (string): Name of the sub-catalog to calculate
        - N (int): Sorting position of the closest event for each
                         earthquake, which controlls initial Kernel Size
        - power (float): 1.0: Wang-Kernel, 1.5: Helmstetter-Kernel
        - target_mw (float): Target forecasting magnitude
        - area_norm (boolean): Flag to normalize each cell with its area
        - sum_norm (boolean): Flag to normalize every cell by the total sum of
                                of all cells
        - nproc (int): Number of processes for parallelization. If 0, no
                             parallelization scheme is used.
        
        Output
        - catalog_pdfx[subcat] (dtype=array, shape=(m,)): probability density
                               for each grid cell, as the sum of every catalog
                               event contribution
        
        """
        
        # Initialize        
        start = time.process_time()
        catalog = np.array(self.subcatalog[subcat][:])
        grid_geom = np.vstack((np.deg2rad(self.grid[:,0]),
                               np.cos(np.deg2rad(self.grid[:,1])),
                               np.sin(np.deg2rad(self.grid[:,1])))).T
        area = self.grid[:,2][:]

                                                              
        print ("Starting catalog variable-size kernel smoothing\n" +
               "\tnumber of events: %i\n" % catalog.shape[0] +
               "\tnumber of cells: %i\n" % grid_geom.shape[0] +
               "\tnumber of processes: %i\n" % nproc)       

        
        # Calculate distances between all events
        dist_matrix = np.array([deg_dist( [x, [catalog[:,0], catalog[:,1]]] )
                                for x in catalog[:,:2]])
        dist_n = np.sort(dist_matrix).T[N,:]    
        self.DIST = dist_n[:]
        catalog[np.where(catalog[:,6] >= target_mw), 6] = target_mw    
        
        ## Create input for parallelization
        Input_list = [[i, j, grid_geom, power, target_mw]
                        for i,j in zip(catalog, dist_n)]

        if nproc != 0:
            pool = Pool(nproc)
            A = pool.map(varKernel_eqkSpatialContribution, Input_list)

            ProbDens = reduce(lambda x,y: x+y, A)
            pool.terminate()
            pool.close()
            
        else:
            ProbDens = np.zeros(self.grid.shape[0])
            for i in Input_list:
                ProbDens += self.varKernel_eqkSpatialContribution(i)
        
        print("Catalog variable-size kernel smoothing complete.\
              Time taken: %i seconds \n\n" % 
              (time.process_time() - start))
        
        if area_norm:
            ProbDens /= area
        
        if sum_norm:
            ProbDens /= np.sum(ProbDens)
            
        self.pdfx_catalog[subcat] = ProbDens[:]

    def get_faultSSM(self, subfault='full', KernelSize=10., N=2, power=1.5, pond=1,
                     area_norm=False, sum_norm=False, nproc=16):
        
        """
        Fixed-sized Kernel smoothing from Helmstetter et al, 2007
        Modified from func_kernelfix.m developed by Hiemer, S. in matlab
        
        Input
        - fault_eqk (dtype=array, shape=(n,5)): Must contain lon, lat, Magnitude,
            time_of_completeness, magnitud_of_completeness
        - grid (dtype=array, shape=(m,2)): The grid's lon/lat values
        - N (dtype=int): Position of the closest event for each earthquake, 
                         controlling initial Kernel Size
        - power (dtype=float): 1.0: Wang-Kernel, 1.5: Helmstetter-Kernel
        - area_norm (boolean): Flag to normalize each cell with its area
        - sum_norm (boolean): Flag to normalize every cell by the total sum of
                                of all cells
        - nproc (dtype=int): Number of processes for parallelization. If 0, no
                             parallelization scheme is used.
        
        Output
        - fault_pdfx (dtype=array, shape=(m,)): accummulated probability density
            for each grid cell, as the sum of every catalog event contribution
        
        
        """
        
        
        start = time.process_time()
        
        faults = self.subfaults[subfault][:]
        
        if pond == 1:
            faults = np.array([np.hstack((i, 1)) for i in faults])
        else:
            faults = np.array([np.hstack((i, 1)) 
                     for i,j in zip(faults,pond)])
       
        grid_geom = np.vstack((np.deg2rad(self.grid[:,0]),
                               np.cos(np.deg2rad(self.grid[:,1])),
                               np.sin(np.deg2rad(self.grid[:,1])))).T
                               
        area = self.grid[:,2][:]
        
        print ("Starting faults fixed-size kernel smoothing\n" +
               "\tnumber of events: %i\n" % len(self.faults) +
               "\tnumber of cells: %i\n" % self.grid.shape[0] +
               "\tnumber of processes: %i\n" % nproc)    
         
         
        ## Create input for parallelization
        Input_list = [[i, KernelSize, grid_geom, power]
                        for i in faults]

        if nproc != 0:
            pool = Pool(nproc)
    
            A = pool.map(fixKernel_eqkSpatialContribution, Input_list)
            ProbDens = reduce(lambda x,y: x+y, A)
            pool.terminate()
            pool.close()
            
        else:
            ProbDens = np.zeros(self.grid.shape[0])
            for i in Input_list:
                ProbDens += self.eqkSpatialContribution(i)
                
        if area_norm:
            ProbDens /= area
        
        if sum_norm:
            ProbDens /= np.sum(ProbDens)
        
        print("Faults fixed-size kernel smoothing complete.\
              Time taken: %i seconds" % 
              (time.process_time() - start))
        
        self.pdfx_faults[subfault] = ProbDens[:]
    
    
    def get_discrete_eqk_field(self, subcat, res):
        
        grid = self.grid[:]
        catalog = self.subcatalog[subcat]
        omega = np.zeros(grid.shape[0])
        for n, i in enumerate(grid):
            for j in catalog:
                if ((i[0] - res[0] < j[0] < i[0] + res[0]) and 
                   (i[1] - res[1] < j[1] < i[1] + res[1])):
                   omega[n] += 1
       
        self.omega = omega
                    
                   
            
    
    
#    def calibrate_varKernel(self, learn_cat, train_cat, grid_res, n_disc):
        
        
        
        
        
    
    
    def get_magPDF(self, Mw_max, a, b, Mw_target, bin_size=0.1):
        
        magnitudes = np.arange(Mw_target, Mw_max + 2*bin_size, bin_size)
        
        cdf_trunc = ( (np.exp(-b*np.log(10.) *
                                       (magnitudes - Mw_target)) -
                            np.exp(-b*np.log(10.) * (Mw_max - Mw_target))) /
                         (1 - np.exp(-b*np.log(10.) * (Mw_max - Mw_target))) ) 
        self.cdf_trunc = cdf_trunc[:-1]
        self.pdf_trunc = -np.diff(cdf_trunc)/np.sum(-np.diff(cdf_trunc))
        self.scale_factor= 10**(a-b*Mw_target)

    
    
    def save_txt(self, filename, att, subcat=None, log10=False, 
                 asgrid=False, fmt='%.18e', header='',delimiter=' '):
        
        if not subcat:
            data = getattr(self, att)[:]
        else:
            data = getattr(self, att)[subcat][:]
        if log10:
            data = np.log10(data)
        if asgrid:
            data = np.hstack((self.grid[:,:2], data.reshape(-1,1)))           
        
        np.savetxt(filename, data, fmt=fmt, header=header,
                   delimiter=delimiter)
    

if __name__ == '__main__':
    
    print("Executing from module")
    
    catalog_fn = '../Input/Data_Catalog_complete.txt'
    fault_fn = '../Input/Data_Faults.txt'
    grid_fn = '../Input/Cells_Collect.txt'

    sf = ssm_model('test')
#    
    sf.set_grid(grid_fn)  
    sf.set_catalog(catalog_fn, 'sheec')
    sf.set_subcatalog('2004-', time=(datetime.datetime(2004,1,1),
                                     datetime.datetime.now()))
#    sf.get_discrete_eqk_field('2004-',(0.1,0.1))
    
    
#    sf.set_faults(fault_fn, 'edsf')   
#
    sf.get_catalogSSM(subcat='2004-',area_norm=False, sum_norm=False)
#    sf.get_faultSSM(area_norm=True, sum_norm=True)
#
#
#    sf.save_txt('Faults_PD_py.txt', 'pdfx_faults', subcat='full', log10=True,
#                asgrid=True)
#                  
    
#    sf.get_magPDF(8.5, 5.8672, 0.9, 4.5)