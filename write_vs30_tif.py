import rioxarray as rxr

da = rxr.open_rasterio("./data/global_vs30.grd").squeeze(drop=True)
# ensure CRS (if missing)
if not da.rio.crs:
    da = da.rio.write_crs("EPSG:4326")

# bbox (lon_min, lon_max, lat_min, lat_max)
lon_min, lon_max, lat_min, lat_max = -76, -56, -66, -17

# subset by bbox (note: clip_box uses minx,miny,maxx,maxy)
da_sub = da.rio.clip_box(minx=lon_min, miny=lat_min, maxx=lon_max, maxy=lat_max)

# write GeoTIFF
da_sub = da_sub.rio.write_nodata(-9999)
da_sub.rio.to_raster("vs30_santiago_native.tif", compress="deflate")