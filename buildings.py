# requirements: pandas, geopandas, shapely
# pip install pandas geopandas shapely

import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import box

# ==== USER INPUTS ====
csv_path = "./data/967_buildings.csv"          # your CSV file
geom_col = "geometry"               # WKT column name in your CSV
crs = "EPSG:4326"                   # WGS84 lon/lat (your data appears to be this)

# Bounding box in lon/lat: (min_lon, min_lat, max_lon, max_lat)
# Example near your coords ~(-73.05, -36.81, -73.02, -36.78)

bbox_tuple = (-70.67,-33.47,-70.61,-33.42 )
# -70.664217889,-70.631492483,-33.455900861,-33.427695163
out_geojson = "buildings_bbox.geojson"
# Optional alternative:
out_gpkg = "buildings_bbox.gpkg"    # layer name "buildings" will be used

# ==== READ CSV & BUILD GEODATAFRAME ====
df = pd.read_csv(csv_path)
df[geom_col] = df[geom_col].apply(wkt.loads)  # convert WKT -> shapely geometry
gdf = gpd.GeoDataFrame(df, geometry=geom_col, crs=crs)
print(min(gdf.latitude), max(gdf.latitude), min(gdf.longitude), max(gdf.longitude))
# # ==== FILTER BY BBOX ====
minx, miny, maxx, maxy = bbox_tuple
bbox_poly = box(minx, miny, maxx, maxy)

# keep features that intersect the bbox (use .within(bbox_poly) if you want strictly inside)
gdf_bbox = gdf[gdf.intersects(bbox_poly)].copy()

# ==== WRITE OUTPUT ====
# GeoJSON
gdf_bbox.to_file(out_geojson, driver="GeoJSON")

# Optional: also write a GeoPackage
# gdf_bbox.to_file(out_gpkg, driver="GPKG", layer="buildings")

print(f"Wrote {len(gdf_bbox)} features to {out_geojson}")
# print(f"Wrote {len(gdf_bbox)} features to {out_gpkg} (layer 'buildings')")
