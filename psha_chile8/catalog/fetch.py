"""Download and copy the source catalogs of plan A2 into sources/raw/<name>/.

Settings at the top. Each request is one file; files already on disk are skipped,
so a stopped run resumes where it stopped. A run writes raw/<name>/fetch.json with
the query, the period and the download date (read.py dates the frozen tables by it).
"""
import datetime as dt
import gzip
import json
import os
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

# settings
BOX = dict(lat0=-58.0, lat1=-15.5, lon0=-80.0, lon1=-60.0)
END = dt.date.today().isoformat()
MAG_MIN = 3.5
MT_MAG_MIN, MT_START = 5.0, "1976-01-01"
RUN = ["potin", "cabello", "rm2018", "gcmt", "centennial", "iscgem", "csn", "comcat", "comcat_mt", "iscehb", "isc"]

HERE = Path(__file__).resolve().parent
RAW = HERE / "sources" / "raw"
DATA = HERE.parents[1] / "data"
LOCAL = {"potin": DATA / "catalogs/CHILE_SEISMICITY_RELOCATED.csv",
         "cabello": DATA / "catalogs/Integrated_Seismic_Catalog_complete.csv",
         "rm2018": DATA / "catalogs/ruiz_madariaga_2018.csv",
         "gcmt": [DATA / "catalogs/gcmt_jan76_dec20.txt", DATA / "catalogs/gcmt_jan21_aug25.txt"]}

USGS = "https://earthquake.usgs.gov/fdsnws/event/1/"
ISC = "http://www.isc.ac.uk/fdsnws/event/1/query"
EHB = "http://www.isc.ac.uk/cgi-bin/web-db-run"
GCMT = "https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/NEW_MONTHLY/"
CENT = "http://web.archive.org/web/20130909170341id_/http://earthquake.usgs.gov/research/data/"
GCMT_LAST = "2025-08"
CSN = "https://www.sismologia.cl/sismicidad/catalogo/"
CSN_START = "2020-01-01"
WAIT = {"usgs.gov": 0.3, "isc.ac.uk": 1.0, "sismologia.cl": 1.0}


def get(url, out, tries=4, timeout=900):
    """Download url to out (gzipped if out ends in .gz). True if out exists afterwards."""
    if out.exists():
        return True
    out.parent.mkdir(parents=True, exist_ok=True)
    w = next((v for k, v in WAIT.items() if k in url), 1.0)
    req = urllib.request.Request(url, headers={"User-Agent": "psha_chile8 catalog fetch"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code in (204, 404) and "fdsnws" in url:
                b = b""
                break
            print(f"  HTTP {e.code} {url}")
            if e.code in (400, 404, 413):
                return False
        except Exception as e:
            print(f"  {type(e).__name__} {e} ({k + 1}/{tries})")
        time.sleep(w * 4 ** k)
    else:
        return False
    tmp = out.with_name(f"{out.name}.part{os.getpid()}")
    with (gzip.open(tmp, "wb") if out.suffix == ".gz" else open(tmp, "wb")) as f:
        f.write(b)
    tmp.rename(out)
    time.sleep(w)
    return True


def log(name, query, t0, t1, n, failed):
    d = RAW / name
    d.mkdir(parents=True, exist_ok=True)
    rec = dict(source=name, query=query, start=t0, end=t1, files=n, failed=failed,
               downloaded=dt.date.today().isoformat())
    (d / "fetch.json").write_text(json.dumps(rec, indent=1))
    print(f"{name}: {n} files, {len(failed)} failed")


def periods(t0, t1, freq):
    e = pd.date_range(t0, t1, freq=freq).union([pd.Timestamp(t0), pd.Timestamp(t1)])
    return list(zip(e[:-1], e[1:]))


def box_q(lat="latitude", lon="longitude"):
    return {f"min{lat}": BOX["lat0"], f"max{lat}": BOX["lat1"], f"min{lon}": BOX["lon0"], f"max{lon}": BOX["lon1"]}


def tag(a, b):
    return f"{a:%Y%m%dT%H}_{b:%Y%m%dT%H}"


# local copies
def copy(name):
    src = LOCAL[name] if isinstance(LOCAL[name], list) else [LOCAL[name]]
    for f in src:
        out = RAW / name / f.name
        if not out.exists():
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)
    return [str(f.relative_to(DATA.parent)) for f in src]


# comcat: yearly requests, split to months and days below the 20 000 limit
def comcat(t0="1500-01-01", t1=END):
    q = dict(box_q(), minmagnitude=MAG_MIN, orderby="time-asc")
    spans = [(pd.Timestamp(t0), pd.Timestamp("1900-01-01"))] if t0 < "1900-01-01" else []
    spans += periods(max(t0, "1900-01-01"), t1, "YS")
    n, failed = 0, []
    while spans:
        a, b = spans.pop(0)
        out = RAW / "comcat" / f"{tag(a, b)}.csv.gz"
        p = dict(q, starttime=a.isoformat(), endtime=b.isoformat())
        if not out.exists():
            c = int(urllib.request.urlopen(USGS + "count?" + urllib.parse.urlencode(p), timeout=300).read())
            if c > 19000:
                spans = periods(a, b, "MS" if (b - a).days > 40 else "D") + spans
                continue
        ok = get(USGS + "query?" + urllib.parse.urlencode(dict(p, format="csv")), out)
        n += ok
        if not ok:
            failed.append(out.name)
    log("comcat", USGS + "query?" + urllib.parse.urlencode(q), t0, t1, n, failed)


# comcat_mt: one GeoJSON detail per event (all moment-tensor and focal-mechanism products)
def comcat_mt(limit=None):
    fs = sorted((RAW / "comcat").glob("*.csv.gz"))
    ev = pd.concat([pd.read_csv(f) for f in fs if f.stat().st_size > 30])
    ev = ev[(ev.mag >= MT_MAG_MIN) & (ev.time >= MT_START)]
    ids = list(ev.id)[:limit]
    n, failed = 0, []
    for i, e in enumerate(ids):
        ok = get(USGS + "query?" + urllib.parse.urlencode(dict(eventid=e, format="geojson")),
                 RAW / "comcat_mt" / f"{e}.json.gz", tries=3)
        n += ok
        if not ok:
            failed.append(e)
        if i % 100 == 0:
            print(f"  comcat_mt {i}/{len(ids)}")
    log("comcat_mt", USGS + f"query?eventid=<id>&format=geojson for comcat M>={MT_MAG_MIN} from {MT_START}",
        MT_START, END, n, failed)


# isc: ISC Bulletin, all origins and magnitudes; yearly before 1964, monthly after, halved on failure
def isc(t0="1904-01-01", t1=END):
    spans = periods(t0, min(t1, "1964-01-01"), "YS") if t0 < "1964-01-01" else []
    spans += periods(max(t0, "1964-01-01"), t1, "MS") if t1 > "1964-01-01" else []
    n, failed = 0, []
    while spans:
        a, b = spans.pop(0)
        p = dict(box_q(), starttime=a.isoformat(), endtime=b.isoformat(), includeallorigins="true",
                 includeallmagnitudes="true", orderby="time-asc")
        if a.year >= 1964:
            p["minmagnitude"] = MAG_MIN
        out = RAW / "isc" / f"{tag(a, b)}.xml.gz"
        if get(ISC + "?" + urllib.parse.urlencode(p), out, tries=3):
            n += 1
        elif (b - a).days > 1:
            spans = [(a, a + (b - a) / 2), (a + (b - a) / 2, b)] + spans
        else:
            failed.append(out.name)
    q = dict(box_q(), includeallorigins="true", includeallmagnitudes="true", minmagnitude=f"{MAG_MIN} from 1964")
    log("isc", ISC + "?" + urllib.parse.urlencode(q), t0, t1, n, failed)


# iscehb: catalogue search, yearly, CSV (depth fix and quality L1-L3) and QuakeML (errors)
def iscehb(y0=1964, y1=2021):
    n, failed = 0, []
    for y in range(y0, y1 + 1):
        for fmt, ext in (("CATCSV", "csv"), ("CATQuakeML", "xml")):
            p = dict(request="COLLECTED", req_agcy="ISC-EHB", table_owner="iscehb", out_format=fmt,
                     searchshape="RECT", bot_lat=BOX["lat0"], top_lat=BOX["lat1"], left_lon=BOX["lon0"],
                     right_lon=BOX["lon1"], start_year=y, start_month=1, start_day=1, start_time="00:00:00",
                     end_year=y, end_month=12, end_day=31, end_time="23:59:59")
            out = RAW / "iscehb" / f"{y}.{ext}.gz"
            ok = get(EHB + "?" + urllib.parse.urlencode(p), out)
            n += ok
            if not ok:
                failed.append(out.name)
    log("iscehb", EHB + "?request=COLLECTED&req_agcy=ISC-EHB&table_owner=iscehb&out_format=CATCSV|CATQuakeML"
        f"&searchshape=RECT&box={BOX}", str(y0), str(y1), n, failed)


# gcmt: the two local ndk files plus the monthly files after them
def gcmt(t1=END):
    loc = copy("gcmt")
    n, failed = len(loc), []
    for m in pd.period_range(pd.Period(GCMT_LAST, "M") + 1, pd.Period(t1[:7], "M") - 1, freq="M"):
        f = f"{m.strftime('%b').lower()}{m.strftime('%y')}.ndk"
        ok = get(f"{GCMT}{m.year}/{f}", RAW / "gcmt" / f)
        n += ok
        if not ok:
            failed.append(f)
    log("gcmt", f"{loc} + {GCMT}<yyyy>/<mmmyy>.ndk", "1976-01-01", t1, n, failed)


# csn: daily catalogue pages of sismologia.cl, from before the end of Potin (overlap for A3 / A5)
def csn(t0=CSN_START, t1=END):
    n, failed = 0, []
    for d in pd.date_range(t0, pd.Timestamp(t1) - pd.Timedelta(days=1), freq="D"):
        ok = get(f"{CSN}{d:%Y/%m/%Y%m%d}.html", RAW / "csn" / f"{d:%Y%m%d}.html.gz")
        n += ok
        if not ok:
            failed.append(f"{d:%Y%m%d}")
    log("csn", CSN + "<yyyy>/<mm>/<yyyymmdd>.html (all events listed per UTC day)", t0, t1, n, failed)


def centennial():
    fs = ["centennial_Y2K.CAT", "centennial_README.rtf"]
    ok = [get(CENT + f, RAW / "centennial" / f) for f in fs]
    log("centennial", CENT + "{" + ",".join(fs) + "} (Wayback snapshot 2013-09-09)", "1900-01-01", "2002-04-01",
        sum(ok), [f for f, o in zip(fs, ok) if not o])


def iscgem():
    d = RAW / "iscgem"
    fs = sorted(d.glob("isc-gem*.csv"))
    if not fs:
        print("iscgem: no direct download (form with CAPTCHA). Download the main and supplementary CSV from\n"
              "  https://www.isc.ac.uk/iscgem/download.php into", d, "and run again.")
        d.mkdir(parents=True, exist_ok=True)
        return
    log("iscgem", "manual download, https://www.isc.ac.uk/iscgem/download.php", "1904-01-01", "", len(fs), [])


if __name__ == "__main__":
    for s in RUN:
        print(f"== {s}")
        if s in ("potin", "cabello", "rm2018"):
            log(s, f"copy of {copy(s)[0]}", "", "", 1, [])
        else:
            globals()[s]()
