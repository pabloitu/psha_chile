# synthetic end-to-end test
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import LineString

from fault_buffers import BufferConfig, build_buffers, write_buffers, margin_sensitivity
from cap_ssm_mmax import cap_grid
from check_fault_ssm_merger import CheckConfig, run_all

out = Path("synth")
out.mkdir(exist_ok=True)

# faults: two overlapping near Pichilemu (~-34.4, -72), one at Aysen (~-45.4, -73)
faults = gpd.GeoDataFrame({
    "id_seg": [1, 2, 3],
    "name": ["PichilemuF", "TopocalmaF", "LOFZ_seg"],
    "rup_type": ["reverse", "reverse", "sinistral"],
    "dip": [30.0, 55.0, 90.0],
    "upp_sd": [0.0, 0.0, 0.0],
    "low_sd": [20.0, 20.0, 15.0],
    "min_mag": [6.05] * 3, "max_mag": [7.2, 7.0, 6.8],
    "b_val": [1.0] * 3, "slip_rate": [1.0, 0.5, 4.0],
    "geometry": [
        LineString([(-72.1, -34.6), (-71.9, -34.2)]),
        LineString([(-72.0, -34.35), (-71.8, -34.0)]),
        LineString([(-73.0, -45.7), (-72.9, -45.1)]),
    ]}, crs="EPSG:4326")
shp = out / "faults.shp"
faults.to_file(shp)

# ssm grid, GR bins 4.9-7.4
lon = np.arange(-73.5, -71.0, 0.1)
lat = np.arange(-46.0, -33.5, 0.1)
LON, LAT = np.meshgrid(lon, lat)
grid = pd.DataFrame({"lon": LON.ravel(), "lat": LAT.ravel(), "depth": 0.0})
edges = np.round(np.arange(4.9, 7.4001, 0.1), 1)
b = 1.0
shape = np.exp(-(((grid.lon + 72.0) / 0.8) ** 2 + ((grid.lat + 34.3) / 1.5) ** 2)) \
      + 0.3 * np.exp(-(((grid.lon + 72.95) / 0.5) ** 2 + ((grid.lat + 45.4) / 0.8) ** 2)) + 1e-4
shape /= shape.sum()
lam = shape.to_numpy() * 10 ** (4.0 - b * 4.9)
for lo, hi in zip(edges[:-1], edges[1:]):
    r = lam * (10 ** (b * (4.9 - lo)) - (10 ** (b * (4.9 - hi)) if hi < 7.4 else 0))
    grid[f"rate_M{lo:.1f}_{hi:.1f}"] = r
ssm_csv = out / "ssm_mfd_grid.csv"
grid.to_csv(ssm_csv, index=False)

# fault nrml (minimal, one simpleFaultSource per fault)
def src_xml(i, name, trace, rates, minmag=6.05, dm=0.1):
    pos = " ".join(f"{x} {y}" for x, y in trace.coords)
    rr = " ".join(f"{r:.6e}" for r in rates)
    return f'''<simpleFaultSource id="f{i}" name="{name}" tectonicRegion="Active Shallow Crust">
<simpleFaultGeometry><gml:LineString><gml:posList>{pos}</gml:posList></gml:LineString>
<dip>60</dip><upperSeismoDepth>0</upperSeismoDepth><lowerSeismoDepth>20</lowerSeismoDepth></simpleFaultGeometry>
<magScaleRel>WC1994</magScaleRel><ruptAspectRatio>1</ruptAspectRatio>
<incrementalMFD minMag="{minmag}" binWidth="{dm}"><occurRates>{rr}</occurRates></incrementalMFD>
<rake>90</rake></simpleFaultSource>'''

rates = [2e-3 * 10 ** (-1.0 * k * 0.1) for k in range(12)]
xml = ('<?xml version="1.0"?>\n<nrml xmlns="http://openquake.org/xmlns/nrml/0.4" '
       'xmlns:gml="http://www.opengis.net/gml"><sourceModel name="t">'
       + "".join(src_xml(i, r["name"], r.geometry, rates) for i, r in faults.iterrows())
       + "</sourceModel></nrml>")
fault_xml = out / "faults.xml"
fault_xml.write_text(xml)

# catalog with Pichilemu + Aysen + background
cat = pd.DataFrame({
    "time_iso": ["2010-03-11T14:39:00", "2007-04-21T17:53:00",
                 "1998-07-01T00:00:00", "2001-05-05T00:00:00"],
    "mag": [6.9, 6.2, 6.1, 5.6],
    "longitude": [-72.0, -72.95, -70.5, -71.95],
    "latitude": [-34.3, -45.4, -40.0, -34.25],
    "depth": [11, 6, 10, 12]})
cat_csv = out / "cat_crustal_dc.csv"
cat.to_csv(cat_csv, index=False)

# run pipeline
bcfg = BufferConfig(faults_shp=shp, out_dir=out, margin_km=10.0)
gdf = build_buffers(bcfg)
pf, pu = write_buffers(gdf, bcfg)

capped = cap_grid(ssm_csv, pu, out / "ssm_mfd_grid_capped.csv", cap_mag=6.0)

margin_sensitivity(ssm_csv, bcfg, margins=(0, 5, 10, 20))

ccfg = CheckConfig(ssm_pre_csv=ssm_csv, ssm_post_csv=out / "ssm_mfd_grid_capped.csv",
                   union_geojson=pu, fault_xml=fault_xml, catalog_csvs=(cat_csv,),
                   out_dir=out / "checks")
run_all(ccfg)

# builder on capped grid
from create_crustal_point_source_model import (
    load_ssm_mfd_grid, assign_constant_depths, build_point_sources_from_ssm,
    check_mfd_consistency, PointSourceModelConfig)
df, rm, me, dM = load_ssm_mfd_grid(out / "ssm_mfd_grid_capped.csv")
dfd = assign_constant_depths(df, PointSourceModelConfig())
srcs = build_point_sources_from_ssm(dfd, rm, me, dM, PointSourceModelConfig())
check_mfd_consistency(rates_matrix=rm, mag_edges=me, sources=srcs)
capped_src = [s for s in srcs if len(s.mfd.occurrence_rates) < len(me) - 1]
print(f"trimmed (capped) sources: {len(capped_src)} / {len(srcs)}")
print("OK")