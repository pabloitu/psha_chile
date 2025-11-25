import shapefile  # pip install pyshp

cities = {
    "Iquique":      (-70.1357, -20.2133),
    "Antofagasta":  (-70.4000, -23.6500),
    "Copiapo":      (-70.3314, -27.3668),
    "Valparaiso":   (-71.6127, -33.0472),
    "Santiago Centre":     (-70.6693, -33.4489),
    "Santiago Penalolen":  (-70.52,   -33.46),
    "Concepcion":   (-73.0503, -36.8269),
    "Pucon":        (-71.9600, -39.2822),
    "Puerto Montt": (-72.9423, -41.4693),
    "Puerto Aysen": (-72.7020, -45.4028),
}

# Create a POINT shapefile (one feature per city)
w = shapefile.Writer("cities", shapeType=shapefile.POINT)
w.autoBalance = 1  # keeps geometry/records in sync

# Add a text field for the city name
w.field("name", "C", size=50)

for name, (lon, lat) in cities.items():
    w.point(lon, lat)
    w.record(name)

w.close()

# Write WGS84 .prj file
prj_wkt = (
    'GEOGCS["WGS 84",'
    'DATUM["WGS_1984",'
    'SPHEROID["WGS 84",6378137,298.257223563]],'
    'PRIMEM["Greenwich",0],'
    'UNIT["degree",0.0174532925199433]]'
)

with open("cities.prj", "w") as f:
    f.write(prj_wkt)
