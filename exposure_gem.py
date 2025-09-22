# requirements: pandas, numpy, rasterio
# pip install pandas numpy rasterio

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import box
import rasterio
from rasterio.transform import from_origin
from math import floor, ceil

# ==== USER INPUTS ====
csv_path = "./data/Exposure_Res_Chile.csv"  # your CSV
lon_col, lat_col = "lon", "lat"
value_col = "structural"

# bounding box (min_lon, min_lat, max_lon, max_lat)
bbox = (-71.7, -33.1, -71.4, -32.9)

# optional bounding box (min_lon, min_lat, max_lon, max_lat); set to None to auto-fit data
# bbox = None  # e.g., (-147.0, -78.0, -146.0, -77.0)
#
# quadtree controls
max_points = 10          # split if a node has more than this many points
max_depth  = 10           # safety cap on depth
min_size   = 1e-6         # minimum cell size in degrees to avoid infinite splitting
clip_to_bbox = True       # clip output cells to the bbox if provided

# Output
out_geojson = "quadtree_logsum1.geojson"

# ====== LOAD & PREP ======
df = pd.read_csv(csv_path)
df = df.dropna(subset=[lon_col, lat_col, value_col])
df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
df = df.dropna(subset=[value_col])

if bbox is not None:
    minx, miny, maxx, maxy = bbox
    df = df[(df[lon_col] >= minx) & (df[lon_col] <= maxx) &
            (df[lat_col] >= miny) & (df[lat_col] <= maxy)]

if df.empty and bbox is None:
    raise SystemExit("No points. Provide a bbox to build a quadtree over an empty area.")

xs = df[lon_col].to_numpy()
ys = df[lat_col].to_numpy()
vals = df[value_col].to_numpy()

# Determine root bbox
if bbox is None:
    pad = 1e-9
    minx, maxx = (np.min(xs) - pad, np.max(xs) + pad) if xs.size else (0, 1)
    miny, maxy = (np.min(ys) - pad, np.max(ys) + pad) if ys.size else (0, 1)
    # Make square-ish to avoid skinny cells (optional)
    dx, dy = maxx - minx, maxy - miny
    if dx == 0: dx = 1e-6
    if dy == 0: dy = 1e-6
    s = max(dx, dy)
    cx, cy = 0.5 * (minx + maxx), 0.5 * (miny + maxy)
    minx, maxx = cx - 0.5 * s, cx + 0.5 * s
    miny, maxy = cy - 0.5 * s, cy + 0.5 * s
else:
    minx, miny, maxx, maxy = bbox

root_bbox = (minx, miny, maxx, maxy)

# ====== QUADTREE ======
class QuadNode:
    __slots__ = ("xmin","ymin","xmax","ymax","idx","children","depth")
    def __init__(self, bbox, idx, depth):
        self.xmin, self.ymin, self.xmax, self.ymax = bbox
        self.idx = idx          # numpy array of point indices in this node
        self.children = None
        self.depth = depth
    def is_leaf(self):
        return self.children is None

def split_indices(xmin, ymin, xmax, ymax, idx):
    xm = 0.5 * (xmin + xmax)
    ym = 0.5 * (ymin + ymax)
    # Child order: NW, NE, SW, SE
    iNW = idx[(xs[idx] <= xm) & (ys[idx] >  ym)]
    iNE = idx[(xs[idx] >  xm) & (ys[idx] >  ym)]
    iSW = idx[(xs[idx] <= xm) & (ys[idx] <= ym)]
    iSE = idx[(xs[idx] >  xm) & (ys[idx] <= ym)]
    return [
        (iNW, (xmin, ym,  xm,  ymax)),
        (iNE, (xm,  ym,  xmax, ymax)),
        (iSW, (xmin, ymin, xm,  ym)),
        (iSE, (xm,  ymin, xmax, ym)),
    ]

def build_quadtree(bbox, max_points, max_depth, depth=0, idx_all=None):
    if idx_all is None:
        idx_all = np.arange(xs.size, dtype=int)
    xmin, ymin, xmax, ymax = bbox
    node = QuadNode(bbox, idx_all, depth)

    # stop conditions
    if (depth >= max_depth) or ((xmax - xmin) < min_size) or ((ymax - ymin) < min_size) \
       or (idx_all.size <= max_points):
        return node

    # split ALWAYS into 4 children to ensure coverage (even if some are empty)
    children = []
    for idx_child, bb in split_indices(xmin, ymin, xmax, ymax, idx_all):
        # Recurse further only if there are points OR we still need to subdivide to maintain structure
        # We still create child nodes with possibly empty idx to cover 'no-data' areas
        child = build_quadtree(bb, max_points, max_depth, depth+1, idx_child)
        children.append(child)
    node.children = children
    return node

# Build tree
root = build_quadtree(root_bbox, max_points=max_points, max_depth=max_depth)

# ====== COLLECT LEAVES & AGGREGATE ======
records = []
def visit(node):
    if node.is_leaf():
        i = node.idx
        sum_raw = float(np.sum(vals[i])) if i.size else 0.0
        count = int(i.size)
        # Requested metric: log10(sum(structural) + 1)
        value_logsum1 = float(np.log10(sum_raw + 1.0))
        rec = {
            "xmin": node.xmin, "ymin": node.ymin,
            "xmax": node.xmax, "ymax": node.ymax,
            "count": count,
            "sum_raw": sum_raw,
            "value_log10_sum1": value_logsum1,
            # optional extras:
            "depth": node.depth,
        }
        records.append(rec)
    else:
        for ch in node.children:
            visit(ch)

visit(root)

gdf = gpd.GeoDataFrame(
    records,
    geometry=[box(r["xmin"], r["ymin"], r["xmax"], r["ymax"]) for r in records],
    crs="EPSG:4326"
)

# If you passed a bbox and want exact clipping (optional)
if bbox is not None:
    gdf = gdf.clip(gpd.GeoSeries([box(*bbox)], crs="EPSG:4326").iloc[0])

gdf.to_file(out_geojson, driver="GeoJSON")
print(f"Wrote {len(gdf)} quadtree cells to {out_geojson}")
print("Attributes per cell: count, sum_raw, value_log10_sum1, depth")