import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin

# 1) Load CSV
df = pd.read_csv("gear_chile.csv")  # columns: longitude, latitude, rate

# 2) Compute log10(rate)
df["log10rate"] = np.log10(df["rate"].astype(float))

# 3) Build regular grid (assumes square lon/lat grid)
xs = np.sort(df["longitude"].unique())
ys = np.sort(df["latitude"].unique())
xres = np.abs(np.diff(xs)).min()
yres = np.abs(np.diff(ys)).min()
# (optional) assert square cells
assert np.isclose(xres, yres), f"Non-square grid: dx={xres}, dy={yres}"

# 4) Create array (rows: north→south, cols: west→east)
arr = np.full((len(ys), len(xs)), np.nan, dtype="float32")
x_index = {x: i for i, x in enumerate(xs)}
y_index = {y: i for i, y in enumerate(ys[::-1])}  # top row = max lat

for lon, lat, v in df[["longitude", "latitude", "log10rate"]].itertuples(index=False):
    arr[y_index[lat], x_index[lon]] = v

# 5) Geo-transform (top-left origin) and write GeoTIFF
transform = from_origin(xs.min(), ys.max(), xres, yres)
nodata = -9999.0
arr_out = np.where(np.isnan(arr), nodata, arr).astype("float32")

with rasterio.open(
    "gear_log10.tif",
    "w",
    driver="GTiff",
    height=arr_out.shape[0],
    width=arr_out.shape[1],
    count=1,
    dtype="float32",
    crs="EPSG:4326",         # WGS84 lon/lat
    transform=transform,
    nodata=nodata,
    compress="deflate"
) as dst:
    dst.write(arr_out, 1)
