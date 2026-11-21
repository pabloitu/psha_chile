"""Headless QGIS export of the basemap (DATA_03, choice c): basemap_north.qgz plus the sea hillshade and the northern
borders, rendered in four versions on the grid of the old basemap_gray.tif (0.004°, 80-63.616° W, 62.056-14.5° S,
RGBA, transparent outside the data) into exports/. Trial, not used.
Run with the system Python (PyQGIS): QT_QPA_PLATFORM=offscreen /usr/bin/python3 export.py
"""
import subprocess
from pathlib import Path

from qgis.core import (QgsApplication, QgsColorRampShader, QgsMapRendererSequentialJob, QgsMapSettings, QgsProject,
                       QgsRasterLayer, QgsRasterShader, QgsRectangle, QgsVectorLayer, QgsCoordinateReferenceSystem)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor, QPainter

here = Path(__file__).parent
x0, x1, y0, y1, res, dpi = -80.0, -63.616, -62.056, -14.5, 0.004, 200
seas = {"color": (["#9fb9cc", "#b8cddc", "#cfdde8", "#e1eaf1", "#eef4f8"], 0.7),
        "gray": (["#9a9a9a", "#b4b4b4", "#cccccc", "#e0e0e0", "#f2f2f2"], 0.6)}
lines = ["sam_nazca_trench", "sam_antarctica_trench", "chile_rise"]

QgsApplication.setPrefixPath("/usr", True)
app = QgsApplication([], False)
app.initQgis()
p = QgsProject.instance()
p.read(str(here / "basemap_north.qgz"))
root = p.layerTreeRoot()
by = {l.name(): l for l in p.mapLayers().values()}
for n in ("merged", "topo_masked", "bathy_masked", "hillshade", "coastline"):
    assert n in by, n

# sea hillshade above the land one, same style, multiply
hl = by["hillshade"]
hs = QgsRasterLayer(str(here / "hillshade_sea.tif"), "hillshade_sea")
hs.setRenderer(hl.renderer().clone())
hs.setBlendMode(QPainter.CompositionMode_Multiply)
p.addMapLayer(hs, False)
node = root.findLayer(hl.id())
node.parent().insertLayer(node.parent().children().index(node), hs)

# northern borders, styled as the Chile-Argentina border
bd = QgsVectorLayer(str(here / "borders_ne10m.shp"), "borders_ne10m", "ogr")
bd.setRenderer(by["chile_argentina_border"].renderer().clone())
p.addMapLayer(bd, False)
node = root.findLayer(by["chile_argentina_border"].id())
node.parent().insertLayer(node.parent().children().index(node), bd)

# coastline: dark gray, 0.26 mm as in the project but fully opaque (the project symbol has opacity 0.31); drawn at
# `dpi` so 0.26 mm is about 2 px on this grid (at 96 dpi lines fall under one pixel)
sym = by["coastline"].renderer().symbol()
sym.setColor(QColor("#4d4d4d"))
sym.setWidth(0.26)
sym.setOpacity(1.0)


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
gdal = "/data/miniforge3/envs/psha9/bin/gdal_translate"
(here / "exports").mkdir(exist_ok=True)
for sea, (cols, op) in seas.items():
    ramp(by["bathy_masked"], cols)
    hs.renderer().setOpacity(op)
    for trench in (False, True):
        for n in lines:
            if n in by:
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
        png = here / "exports" / f"{name}.png"
        job.renderedImage().save(str(png))
        subprocess.run([gdal, "-q", "-of", "GTiff", "-a_srs", "EPSG:4326", "-a_ullr", str(x0), str(y1), str(x1), str(y0),
                        "-co", "COMPRESS=DEFLATE", "-co", "TFW=YES", str(png), str(here / "exports" / f"{name}.tif")],
                       check=True, env={"PROJ_DATA": "/data/miniforge3/envs/psha9/share/proj",
                                        "GDAL_DATA": "/data/miniforge3/envs/psha9/share/gdal"})
        png.unlink()
        print(name, w, h, [l.name() for l in ms.layers()])
app.exitQgis()
