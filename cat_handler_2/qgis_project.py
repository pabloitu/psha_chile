# Point the QGIS map project (project.qgz, kept in results/<dir>/<dir>/) at the
# cat_handler_2 outputs, keeping every style, layout and filter:
#   cat_classified        -> results/cat_handler_2/catalog.csv (same filter)
#   relocated_classified  -> results/cat_handler_2/beachballs/beachballs.csv,
#                            image path from its png column
#   class colours         -> the new classes added (same colours as beachballs.py)
# usage: python -m cat_handler_2.tools.qgis_project old.qgz new.qgz

import re
import sys
import zipfile

from cat_handler_2 import palette as PAL

hexrgb = lambda h: ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
CASE = "CASE\n" + "\n".join(f"    WHEN \"class\" = '{c}' THEN color_rgb({hexrgb(v)})   -- {PAL.NAME[c]}" for c, v in PAL.CLASS.items()) \
    + "\n    ELSE color_rgb(150,150,150)\nEND"
OPTS = "type=csv&maxFields=10000&detectTypes=yes&xField=longitude&yField=latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no"


def esc(s, attr):
    s = s.replace("&", "&amp;").replace('"', "&quot;")
    return s.replace("\n", "&#xa;") if attr else s


def main(src, dst):
    with zipfile.ZipFile(src) as z:
        files = {n: z.read(n) for n in z.namelist()}
    name = next(n for n in files if n.endswith(".qgs"))
    q = files[name].decode("utf-8")

    old = re.search(r"file:\.\./\.\./catalogs/integrated/cat_classified_NOMEC\.csv\?[^<\"]*?(&(?:amp;)?subset=[^<\"]*)", q)
    sub = old.group(1).replace("&amp;", "&") if old else ""
    new_cat = "file:../../cat_handler_2/catalog.csv?" + OPTS + sub
    new_bb = "file:../../cat_handler_2/beachballs/beachballs.csv?" + OPTS
    for pat, new in ((r"file:\.\./\.\./catalogs/integrated/cat_classified_NOMEC\.csv\?[^<\"]*", new_cat),
                     (r"file:\.\./\.\./catalogs/classified/relocated_classified\.csv\?[^<\"]*", new_bb)):
        q = re.sub(pat + r"(?=<)", lambda m: esc(new, False), q)
        q = re.sub(pat + r"(?=\")", lambda m: esc(new, True), q)

    q = re.sub(r'value="replace\(@project_path[^"]*beachballs/relocated/[^"]*"', 'value="&quot;png&quot;"', q)
    q, nc = re.subn(r'value="CASE&#xa;.*?END"', lambda m: 'value="' + esc(CASE, True) + '"', q, count=1, flags=re.S)
    files[name] = q.encode("utf-8")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for f, b in files.items():
            z.writestr(f, b)
    print(f"{dst}: catalog -> {new_cat.split('?')[0]}, beachballs -> {new_bb.split('?')[0]}, colour expression replaced: {nc}")


if __name__ == "__main__":
    main(*sys.argv[1:3])