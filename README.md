# psha_chile


## install

```shell
mamba create -n psha_chile
mamba activate psha_chile
git clone https://github.com/gem/oq-engine --depth=1 --branch=master
cd oq-engine
pip install -r requirements-py311-linux64.txt 
pip install -e .
pip install geopandas vtk rasterio rioxarray
```




## make grid (QGIS)

* Import region shapefile
* Create cell grid: Vector / Research Tools / Create Grid
  * Extent from layer (region shapefile)
  * Grid type: Rectangle polygon > set vertical/horizontal dimensions
* Intersect to polygon
  * Processing Toolbox > Extract by location
  * extraction layer (Grid), type (intersection or touch) / auxiliary layer (region shapefile)
* Get cell centroids
  * Processing Toolbox >  Centroids
  * select Extracted (location) layer
* Export grid
  * Export > Geometry (AS_XY)