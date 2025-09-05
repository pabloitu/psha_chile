import rioxarray

data = rioxarray.open_rasterio("./data/global_vs30.grd")
print(data.rio.crs)       # CRS
print(data.shape)         # Dimensions

chile_extent = [-76, -56, -66, -17]
subset = data.sel(
    x=slice(chile_extent[0], chile_extent[2]),
    y=slice(chile_extent[3], chile_extent[1])  # careful: many rasters have y descending
)