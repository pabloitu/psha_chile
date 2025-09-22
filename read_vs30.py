import numpy as np
import xarray as xr
import rioxarray

# 1) Open and squeeze to (y, x) if single-band
da = rioxarray.open_rasterio("./data/global_vs30.grd").squeeze(drop=True)
grid = './shp/analysis_regions/santiago_grid_008.csv'
# (optional) set nodata to NaN
if da.rio.nodata is not None:
    da = da.where(da != da.rio.nodata)

# 2) (optional) subset to a bbox to speed things up
lon_min, lon_max, lat_min, lat_max = -76, -56, -66, -17
da_sub = da.sel(x=slice(lon_min, lon_max),
                y=slice(lat_max, lat_min))  # note y from max->min if descending


lons, lats = np.loadtxt(grid, delimiter=",", usecols=(0, 1), skiprows=1, unpack=True)

# 4) Interpolate (bilinear). This returns one value per point.
xi = xr.DataArray(lons, dims="points")
yi = xr.DataArray(lats, dims="points")

vals_linear = da_sub.interp(x=xi, y=yi, method="linear")  # bilinear in 2D
# If you prefer nearest-cell values instead:
# vals_nearest = da_sub.interp(x=xi, y=yi, method="nearest")

# 5) Pack into a table / save CSV
import pandas as pd
out_df = pd.DataFrame({"lon": lons, "lat": lats,
                       "vs30": vals_linear.values})
out_df.to_csv("santiago_008_vs30.csv", index=False)
print(out_df.head())
