"""Headless QGIS export of the basemap (DATA_03, choice c): data/raw/basemaps/basemap_chile_2026-11-21/project/
basemap.qgz (styles saved there) rendered in four versions, colour or gray sea, with or without the trench lines, on
the grid of the old basemap_gray.tif (0.004°, 80-63.616° W, 62.056-14.5° S, RGBA, transparent outside the data).
Lines are drawn at `dpi` so that a 0.26 mm line is about 2 px on this grid.
Run with the system Python (PyQGIS): QT_QPA_PLATFORM=offscreen /usr/bin/python3 export.py [out folder]
"""
import subprocess
import sys
from pathlib import Path

from qgis.core import (QgsApplication, QgsColorRampShader, QgsCoordinateReferenceSystem, QgsMapRendererSequentialJob,
                       QgsMapSettings, QgsProject, QgsRasterShader, QgsRectangle)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

d = Path(__file__).resolve().parents[2] / "data/raw/basemaps/basemap_chile_2026-11-21"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else d
x0, x1, y0, y1, res, dpi = -80.0, -63.616, -62.056, -14.5, 0.004, 200
seas = {"color": (["#9fb9cc", "#b8cddc", "#cfdde8", "#e1eaf1", "#eef4f8"], 0.7),
        "gray": (["#9a9a9a", "#b4b4b4", "#cccccc", "#e0e0e0", "#f2f2f2"], 0.6)}
lines = ["nazca_trench", "antarctic_trench", "chile_rise"]
gdal = "/data/miniforge3/envs/psha9/bin/gdal_translate"
env = {"PROJ_DATA": "/data/miniforge3/envs/psha9/share/proj", "GDAL_DATA": "/data/miniforge3/envs/psha9/share/gdal"}

QgsApplication.setPrefixPath("/usr", True)
app = QgsApplication([], False)
app.initQgis()
p = QgsProject.instance()
p.read(str(d / "project/basemap.qgz"))
root = p.layerTreeRoot()
by = {l.name(): l for l in p.mapLayers().values()}
for n in ["bathy_masked", "hillshade_sea", "coastline"] + lines:
    assert n in by and by[n].isValid(), n


def ramp(layer, cols, lo=-10000.0, hi=-1000.0):
    f = QgsColorRampShader(lo, hi)
    f.setColorRampType(QgsColorRampShader.Interpolated)
    f.setColorRampItemList([QgsColorRampShader.ColorRampItem(lo + k * (hi - lo) / (len(cols) - 1), QColor(c))
                            for k, c in enumerate(cols)])
    f.setClip(False)
    s = QgsRasterShader()
    s.setRasterShaderFunction(f)
    layer.renderer().setShader(s)


w, h = round((x1 - x0) / res), round((y1 - y0) / res)
out.mkdir(parents=True, exist_ok=True)
for sea, (cols, op) in seas.items():
    ramp(by["bathy_masked"], cols)
    by["hillshade_sea"].renderer().setOpacity(op)
    for trench in (False, True):
        for n in lines:
            root.findLayer(by[n].id()).setItemVisibilityChecked(trench)
        ms = QgsMapSettings()
        ms.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        ms.setLayers(root.checkedLayers())
        ms.setExtent(QgsRectangle(x0, y0, x1, y1))
        ms.setOutputSize(QSize(w, h))
        ms.setBackgroundColor(QColor(255, 255, 255, 0))
        ms.setOutputDpi(dpi)
        job = QgsMapRendererSequentialJob(ms)
        job.start()
        job.waitForFinished()
        name = f"basemap_{sea}{'_trench' if trench else ''}"
        png = out / f"{name}.png"
        job.renderedImage().save(str(png))
        subprocess.run([gdal, "-q", "-of", "GTiff", "-a_srs", "EPSG:4326", "-a_ullr", str(x0), str(y1), str(x1), str(y0),
                        "-co", "COMPRESS=DEFLATE", "-co", "TFW=YES", str(png), str(out / f"{name}.tif")], check=True, env=env)
        png.unlink()
        print(name, w, h)
app.exitQgis()
