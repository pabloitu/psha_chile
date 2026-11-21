"""Choice c (DATA_03): the gray basemap's layers extended north to 14.5° S, for Pablo to re-export in QGIS.

The basemap (data/basemaps/basemap_chile_gray/basemap_gen.qgz) is drawn from merged.tif, GEBCO_2025 at 15",
80-65° W, 58-17° S (repo data/basemaps, outside psha_chile9). The new GEBCO_2025 tile
(data/raw/basemaps/gebco_2025_north, 80-63.5° W, 17.5-14.5° S, 21 Nov) equals merged.tif where they overlap. The
rasters of data/raw/basemaps/basemap_chile_2026-11-21/project were made this way (the project there holds the styles). Here: merged.tif extended north, topo_masked (>= 0 m) and bathy_masked (< 0 m, nodata -9999),
hillshade (gdaldem, scale 111120, azimuth 315, altitude 45: matches the old one, mean difference 1.8 of 255),
the coastline as the 0 m contour, the northern borders from Natural Earth 10 m, and a copy of basemap_gen.qgz
pointing to them. The originals are not changed. Trial, not used.
"""
import shutil
import subprocess
import zipfile
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

here = Path(__file__).parent
old = Path("/data/PyCharmProjects/psha_chile/data/basemaps/basemap_chile_gray")
tile = here.parents[1] / "data/raw/basemaps/gebco_2025_north/gebco_2025_n-14.5_s-17.5_w-80.0_e-63.5_geotiff.tif"
out = here / "layers"
out.mkdir(exist_ok=True)
g = "/data/miniforge3/envs/psha9/bin/"
run = lambda *a: subprocess.run([g + a[0], *a[1:]], check=True)

# elevation
run("gdal_translate", "-q", "-ot", "Float32", "-projwin", "-80", "-14.5", "-65", "-17.5", str(tile), str(out / "north.tif"))
run("gdalbuildvrt", "-q", str(out / "m.vrt"), str(out / "north.tif"), str(old / "merged.tif"))
run("gdal_translate", "-q", "-co", "COMPRESS=DEFLATE", "-co", "TILED=YES", str(out / "m.vrt"), str(out / "merged.tif"))
for f in ("north.tif", "m.vrt"):
    (out / f).unlink()
for name, expr in (("topo_masked", "where(A>=0,A,-9999)"), ("bathy_masked", "where(A<0,A,-9999)")):
    run("gdal_calc", "--quiet", "-A", str(out / "merged.tif"), "--outfile", str(out / f"{name}.tif"), "--calc", expr,
        "--NoDataValue=-9999", "--type=Float64", "--co=COMPRESS=DEFLATE", "--co=TILED=YES", "--overwrite")
run("gdaldem", "hillshade", "-q", "-s", "111120", "-az", "315", "-alt", "45", "-co", "COMPRESS=DEFLATE",
    str(out / "merged.tif"), str(out / "hillshade.tif"))

# lines
run("gdal_contour", "-q", "-fl", "0", "-a", "elev", str(out / "merged.tif"), str(out / "coastline.shp"))
ne = Path.home() / ".local/share/cartopy/shapefiles/natural_earth/cultural/ne_10m_admin_0_boundary_lines_land.shp"
b = gpd.read_file(ne).clip(box(-80, -58, -60, -14.5))
b[["geometry"]].to_file(out / "borders_ne10m.shp")

# QGIS project: the local layers, the others by absolute path
with zipfile.ZipFile(old / "basemap_gen.qgz") as z:
    z.extractall(out / "qgz")
q = out / "qgz/basemap_gen.qgs"
s = q.read_text().replace("../../shapefiles/", "/data/PyCharmProjects/psha_chile/data/shapefiles/")
s = s.replace("./chile_argentina_border.shp", str(old / "chile_argentina_border.shp"))
q.write_text(s)
with zipfile.ZipFile(out / "basemap_gen_north.qgz", "w", zipfile.ZIP_DEFLATED) as z:
    for f in (out / "qgz").iterdir():
        z.write(f, f.name)
shutil.rmtree(out / "qgz")
print(sorted(p.name for p in out.iterdir()))

# sea variant i (Pablo, 21 Nov): hillshade split into land (full) and sea (70 % in QGIS)
for name, expr in (("hillshade_sea", "where(B<0,A,0)"), ("hillshade_land", "where(B>=0,A,0)")):
    run("gdal_calc", "--quiet", "-A", str(out / "hillshade.tif"), "-B", str(out / "merged.tif"), "--outfile",
        str(out / f"{name}.tif"), "--calc", expr, "--NoDataValue=0", "--type=Byte", "--co=COMPRESS=DEFLATE", "--overwrite")
