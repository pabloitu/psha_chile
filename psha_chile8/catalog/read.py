"""Read each raw source catalog into three common tables (plan A2).

sources/<name>_<YYYY-MM-DD>_{events,mags,mechs}.csv, dated by the download in
raw/<name>/fetch.json, and a row per table in sources/MANIFEST.csv. Nothing is
matched, chosen or converted: every origin and every magnitude a source reports is
kept with its agency and native type. Errors and depths in km, moments in N m.
"""
import datetime as dt
import gzip
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

from fetch import BOX, RAW

# settings
RUN = ["comcat", "comcat_mt", "isc", "csn_isc", "csn", "iscehb", "iscgem", "gcmt", "centennial", "potin", "cabello",
       "rm2018"]
OUT = RAW.parent

EV = ["src", "src_id", "origin_id", "prime", "time", "lon", "lat", "depth", "depth_fixed", "lon_err", "lat_err",
      "depth_err", "depth_quality", "agency", "etype"]
MG = ["src", "src_id", "agency", "mag_type", "mag", "mag_err", "n_sta", "note"]
MC = ["src", "src_id", "agency", "code", "m0", "mw", "mw_type", "strike1", "dip1", "rake1", "strike2", "dip2",
      "rake2", "mrr", "mtt", "mpp", "mrt", "mrp", "mtp"]
NS = {"q": "http://quakeml.org/xmlns/bed/1.2"}
KM = 111.195


def num(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


def frame(rows, cols, src):
    df = pd.DataFrame(rows)
    df["src"] = src
    extra = [c for c in df.columns if c not in cols]
    return df.reindex(columns=cols + extra).drop_duplicates(ignore_index=True)


def inbox(ev, *tabs):
    """Keep the events with any origin in BOX, and the rows of the other tables that belong to them."""
    ok = ev.lat.between(BOX["lat0"], BOX["lat1"]) & ev.lon.between(BOX["lon0"], BOX["lon1"])
    ids = set(ev.src_id[ok])
    return [t[t.src_id.isin(ids)].reset_index(drop=True) for t in (ev,) + tabs]


def opener(f):
    return gzip.open(f, "rb") if str(f).endswith(".gz") else open(f, "rb")


def iso(y, mo, d, h=0, mi=0, s=0.0):
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}T{int(h):02d}:{int(mi):02d}:{float(s):05.2f}"


# QuakeML of the ISC services (ISC Bulletin, ISC-EHB)
def quakeml(f, src):
    """All origins and magnitudes of a QuakeML file, ISC flavour (agency = creationInfo/author)."""
    with opener(f) as h:
        b = h.read()
    ev, mg = [], []
    if not b.strip():
        return ev, mg
    k = b.rfind(b"</q:quakeml>")
    b = b[:k + 12] if k > 0 else b
    t = lambda e, p: (e.findtext(p, namespaces=NS) or "").strip() or None
    for e in ET.fromstring(b).iter(f"{{{NS['q']}}}event"):
        eid = e.get("publicID").split("=")[-1]
        pref = (t(e, "q:preferredOriginID") or "").split("=")[-1]
        for o in e.findall("q:origin", NS):
            oid = o.get("publicID").split("=")[-1]
            h = num(t(o, "q:originUncertainty/q:maxHorizontalUncertainty")) / 1000
            ev.append(dict(src_id=eid, origin_id=oid, prime=oid == pref, time=(t(o, "q:time/q:value") or "").rstrip("Z"),
                           lon=num(t(o, "q:longitude/q:value")), lat=num(t(o, "q:latitude/q:value")),
                           depth=num(t(o, "q:depth/q:value")) / 1000,
                           depth_fixed=t(o, "q:depthType") == "operator assigned", lon_err=h, lat_err=h,
                           depth_err=num(t(o, "q:depth/q:uncertainty")) / 1000,
                           agency=t(o, "q:creationInfo/q:author") or t(o, "q:creationInfo/q:agencyID"),
                           etype=t(e, "q:type")))
        for m in e.findall("q:magnitude", NS):
            mg.append(dict(src_id=eid, agency=t(m, "q:creationInfo/q:author") or t(m, "q:creationInfo/q:agencyID"),
                           mag_type=t(m, "q:type"), mag=num(t(m, "q:mag/q:value")),
                           mag_err=num(t(m, "q:mag/q:uncertainty")), n_sta=num(t(m, "q:stationCount"))))
    return ev, mg


def isc(d):
    ev, mg = [], []
    for f in sorted(d.glob("*.xml.gz")):
        a, b = quakeml(f, "isc")
        ev += a
        mg += b
    return inbox(frame(ev, EV, "isc"), frame(mg, MG, "isc"), frame([], MC, "isc"))


def csn_isc(d):
    """CSN (agency GUC) origins and magnitudes inside the ISC Bulletin download."""
    ev, mg, mc = isc(d)
    ev, mg = ev[ev.agency == "GUC"], mg[mg.agency == "GUC"]
    for t in (ev, mg, mc):
        t["src"] = "csn_isc"
    ev = ev.assign(prime=True)
    return inbox(ev, mg, mc)


def csn(d):
    """CSN daily catalogue pages: UTC time, epicentre, depth (km, integer), one magnitude and its type."""
    ev, mg = [], []
    for f in sorted(d.glob("*.html.gz")):
        with opener(f) as h:
            txt = h.read().decode("utf-8", "replace")
        for att, row in re.findall(r"<tr([^>]*)>(.*?)</tr>", txt, re.S):
            c = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
            if len(c) != 5:
                continue
            link = re.search(r'href="[^"]*/(\d{4}/\d{2}/\d+)\.html"', c[0])
            t = re.sub(r"<[^>]+>", " ", c[1]).strip()
            ll = re.sub(r"<[^>]+>", " ", c[2]).split()
            m = re.sub(r"<[^>]+>", " ", c[4]).split()
            i = link.group(1) if link else t
            ev.append(dict(src_id=i, origin_id=i, prime=True, time=t.replace(" ", "T"), lat=num(ll[0]),
                           lon=num(ll[1]), depth=num(re.sub(r"[^0-9.\-]", "", re.sub(r"<[^>]+>", "", c[3]))),
                           agency="CSN", etype="earthquake", felt="percibido" in att))
            if m:
                mg.append(dict(src_id=i, agency="CSN", mag_type=m[1] if len(m) > 1 else None, mag=num(m[0])))
    return inbox(frame(ev, EV, "csn"), frame(mg, MG, "csn"), frame([], MC, "csn"))


def iscehb(d):
    """ISC-EHB: origins and magnitudes from QuakeML, depth fix and quality class (L1-L3) from the CSV."""
    ev, mg, q = [], [], {}
    for f in sorted(d.glob("*.xml.gz")):
        a, b = quakeml(f, "iscehb")
        ev += a
        mg += b
    for f in sorted(d.glob("*.csv.gz")):
        with opener(f) as h:
            txt = h.read().decode("utf-8", "replace")
        rows = [r.split(",") for r in txt.splitlines() if r[:1].isdigit() and r.count(",") >= 9]
        q.update({r[0].strip(): (r[8].strip() == "TRUE", r[9].strip()) for r in rows})
    ev = frame(ev, EV, "iscehb")
    ev["depth_fixed"] = [q.get(i, (np.nan,))[0] for i in ev.src_id]
    ev["depth_quality"] = [q.get(i, (None, None))[1] for i in ev.src_id]
    return ev, frame(mg, MG, "iscehb"), frame([], MC, "iscehb")


def comcat(d):
    fs = [f for f in sorted(d.glob("*.csv.gz")) if f.stat().st_size > 30]
    c = pd.concat([pd.read_csv(f, dtype={"id": str}) for f in fs], ignore_index=True).drop_duplicates("id")
    ev = pd.DataFrame(dict(src_id=c.id, origin_id=c.id, prime=True, time=c.time.str.rstrip("Z"), lon=c.longitude,
                           lat=c.latitude, depth=c.depth, lon_err=c.horizontalError, lat_err=c.horizontalError,
                           depth_err=c.depthError, agency=c.locationSource, etype=c.type))
    mg = pd.DataFrame(dict(src_id=c.id, agency=c.magSource, mag_type=c.magType, mag=c.mag, mag_err=c.magError,
                           n_sta=c.magNst))
    return frame(ev, EV, "comcat"), frame(mg, MG, "comcat"), frame([], MC, "comcat")


def comcat_mt(d):
    """Every moment-tensor and focal-mechanism product of the ComCat event pages."""
    mc = []
    for f in sorted(d.glob("*.json.gz")):
        with opener(f) as h:
            b = h.read()
        if not b.strip():
            continue
        e = json.loads(b)
        for kind in ("moment-tensor", "focal-mechanism"):
            for p in e["properties"]["products"].get(kind, []):
                g = p["properties"].get
                mc.append(dict(src_id=e["id"], agency=g("beachball-source") or p["source"], code=f"{kind}:{p['code']}",
                               m0=num(g("scalar-moment")), mw=num(g("derived-magnitude")),
                               mw_type=g("derived-magnitude-type"),
                               **{f"{k}{i}": num(g(f"nodal-plane-{i}-{k}")) for i in (1, 2)
                                  for k in ("strike", "dip", "rake")},
                               **{k: num(g(f"tensor-{k}")) for k in ("mrr", "mtt", "mpp", "mrt", "mrp", "mtp")}))
    return frame([], EV, "comcat_mt"), frame([], MG, "comcat_mt"), frame(mc, MC, "comcat_mt")


def ndk(lines):
    """Parse GCMT ndk 5-line blocks: reference hypocentre and centroid origins, mb / Ms / Mw, tensor."""
    ev, mg, mc = [], [], []
    lines = [l.rstrip("\n").ljust(80) for l in lines if l.strip()]
    for i in range(0, len(lines) - 4, 5):
        l1, l2, l3, l4, l5 = lines[i:i + 5]
        cid = l2[:16].strip()
        y, mo, dd = l1[5:15].split("/")
        hh, mi, ss = l1[16:26].split(":")
        t0 = dt.datetime(int(y), int(mo), int(dd), int(hh), int(mi)) + dt.timedelta(seconds=float(ss))
        ref = l1[:4].strip()
        ev.append(dict(src_id=cid, origin_id=f"{cid}_hyp", prime=False, time=t0.isoformat(timespec="milliseconds"),
                       lat=num(l1[27:33]), lon=num(l1[34:41]), depth=num(l1[42:47]), agency=ref, etype="earthquake"))
        for k, mt in zip(l1[48:55].split(), ("mb", "Ms")):
            if num(k) > 0:
                mg.append(dict(src_id=cid, agency=ref, mag_type=mt, mag=num(k)))
        c = [num(l3[a:b]) for a, b in ((9, 18), (22, 29), (29, 34), (34, 42), (42, 47), (47, 53), (53, 58))]
        tc = t0 + dt.timedelta(seconds=c[0])
        kind = l3[58:63].strip()
        ev.append(dict(src_id=cid, origin_id=f"{cid}_cen", prime=True, time=tc.isoformat(timespec="milliseconds"),
                       lat=c[1], lon=c[3], depth=c[5], depth_fixed=kind != "FREE", depth_quality=kind,
                       lat_err=c[2] * KM, lon_err=c[4] * KM * np.cos(np.radians(c[1])), depth_err=c[6],
                       agency="GCMT", etype="earthquake"))
        x = int(l4[:2])
        f = 10.0 ** (x - 7)
        ten = {k: num(l4[2 + 13 * j:9 + 13 * j]) * f for j, k in enumerate(("mrr", "mtt", "mpp", "mrt", "mrp", "mtp"))}
        m0 = num(l5[49:56]) * f
        mw = 2 / 3 * (np.log10(m0) - 9.1)
        mg.append(dict(src_id=cid, agency="GCMT", mag_type="Mw", mag=round(mw, 2)))
        mc.append(dict(src_id=cid, agency="GCMT", code=cid, m0=m0, mw=round(mw, 2), mw_type="Mw",
                       **{k: num(l5[a:b]) for k, a, b in (("strike1", 56, 60), ("dip1", 60, 63), ("rake1", 63, 68),
                                                       ("strike2", 68, 72), ("dip2", 72, 75), ("rake2", 75, 80))},
                       **ten))
    return ev, mg, mc


def gcmt(d):
    ev, mg, mc = [], [], []
    for f in sorted(d.glob("*.txt")) + sorted(d.glob("*.ndk")):
        a, b, c = ndk(open(f, encoding="utf-8", errors="replace").readlines())
        ev, mg, mc = ev + a, mg + b, mc + c
    return inbox(frame(ev, EV, "gcmt"), frame(mg, MG, "gcmt"), frame(mc, MC, "gcmt"))


def centennial(d):
    """Centennial catalogue, fixed-width format of its README; up to 8 magnitudes, first is the preferred."""
    ev, mg = [], []
    fixed = {"HEQ", "BEQ", "CEQ", "FEQ", "LEQ"}
    for n, l in enumerate(open(d / "centennial_Y2K.CAT", encoding="latin-1"), 1):
        isol = l[7:12].strip()
        ev.append(dict(src_id=str(n), origin_id=str(n), prime=True,
                       time=iso(l[12:16], l[16:19], l[19:22], l[23:26], l[26:29], l[29:35]),
                       lat=num(l[36:44]), lon=num(l[44:52]), depth=num(l[52:58]),
                       depth_fixed=(isol[:3] in fixed) if isol[:3] in fixed | {"DEQ"} else np.nan,
                       depth_quality=isol or None, agency=l[:6].strip(), etype="earthquake"))
        for k in range(66, len(l.rstrip("\n")) - 3, 13):
            if num(l[k:k + 4]) > 0:
                mg.append(dict(src_id=str(n), agency=l[k + 8:k + 13].strip(), mag_type=l[k + 5:k + 7].strip(),
                               mag=num(l[k:k + 4]), note="preferred" if k == 66 else None))
    return inbox(frame(ev, EV, "centennial"), frame(mg, MG, "centennial"), frame([], MC, "centennial"))


def iscgem(d):
    """ISC-GEM csv (main and supplementary): header is the last comment line naming the columns."""
    ev, mg, mc = [], [], []
    for f in sorted(d.glob("isc-gem*.csv")):
        lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        head = [l for l in lines if l.startswith("#") and "date" in l and "lat" in l][-1].lstrip("#")
        ren = {"str1": "strike1", "str2": "strike2", "mpr": "mrp"}
        cs = [ren.get(c.strip(), c.strip()) for c in head.split(",")]
        cs = [c + (f".{cs[:i].count(c)}" if cs[:i].count(c) else "") for i, c in enumerate(cs)]
        g = pd.read_csv(io.StringIO("\n".join(l for l in lines if l.strip() and not l.startswith("#"))),
                        names=cs, header=None, dtype=str)
        g = g.apply(lambda s: s.str.strip())
        ag = "ISC-GEM-suppl" if "suppl" in f.name else "ISC-GEM"
        for _, r in g.iterrows():
            v = lambda k: num(r.get(k))
            e, k = r.eventid, 10.0 ** v("fac")
            ev.append(dict(src_id=e, origin_id=e, prime=True, time=r.date.replace(" ", "T"), lat=v("lat"),
                           lon=v("lon"), depth=v("depth"), lat_err=v("smajax"), lon_err=v("smajax"),
                           depth_err=v("unc"), depth_quality=r.get("q.1"), agency=ag, etype="earthquake"))
            mg.append(dict(src_id=e, agency=ag, mag_type="Mw", mag=v("mw"), mag_err=v("unc.1"),
                           note=f"q={r.get('q.2')} s={r.get('s')}"))
            if v("mo") > 0 or v("strike1") >= 0:
                mc.append(dict(src_id=e, agency=r.get("mo_auth"), code=ag, m0=v("mo") * k, mw=v("mw"), mw_type="Mw",
                               **{c: v(c) for c in ("strike1", "dip1", "rake1", "strike2", "dip2", "rake2")},
                               **{c: v(c) * k for c in ("mrr", "mtt", "mpp", "mrt", "mrp", "mtp")}))
    return inbox(frame(ev, EV, "iscgem"), frame(mg, MG, "iscgem"), frame(mc, MC, "iscgem"))


def potin(d):
    p = pd.read_csv(next(d.glob("*.csv")))
    i = p["#"].astype(str)
    t = [iso(*r) for r in p[["year", "month", "day", "hour", "minute", "seconds"]].itertuples(index=False)]
    ev = pd.DataFrame(dict(src_id=i, origin_id=i, prime=True, time=t, lon=p.longitude, lat=p.latitude,
                           depth=p.depth, agency="potin", etype="earthquake", rms=p.rms))
    mg = pd.DataFrame(dict(src_id=i, agency="CSN", mag_type=p.magnitude_type.str.strip(), mag=p.magnitude))
    return inbox(frame(ev, EV, "potin"), frame(mg[mg.mag.notna()], MG, "potin"), frame([], MC, "potin"))


def cabello(d):
    """Cabello et al. (2025): all rows; native magnitude columns and the final 'magnitude' kept apart."""
    c = pd.read_csv(next(d.glob("*.csv")), sep=";", low_memory=False)
    i = c.id.astype(str)
    s = c.second.fillna(0)
    t = [iso(*r) for r in zip(c.year, c.month.fillna(1), c.day.fillna(1), c.hour.fillna(0), c.minute.fillna(0), s)]
    ev = pd.DataFrame(dict(src_id=i, origin_id=i, prime=True, time=t, lon=c.longitude, lat=c.latitude,
                           depth=c.depth, lon_err=c.longitudeError, lat_err=c.latitudeError, depth_err=c.depthError,
                           depth_quality=c.obs_depth, agency=c.catalog, etype="earthquake",
                           relocated=c.relocated, reference=c.reference))
    mg = []
    for k in ("Mw", "Ms", "Mb", "Ml", "Md", "Mc", "M", "magnitude"):
        m = pd.DataFrame(dict(src_id=i, agency=c.catalog if k != "magnitude" else "cabello", mag_type=k, mag=c[k].map(num),
                              mag_err=c.mag_unc if k == "Mw" else np.nan))
        mg.append(m[m.mag.notna()])
    mc = pd.DataFrame(dict(src_id=i, agency=c.catalog, m0=c.Mo_escalar, strike1=c.strike1, dip1=c.dip1,
                           rake1=c.rake1, strike2=c.strike2, dip2=c.dip2, rake2=c.rake2))
    mc = mc[mc.strike1.notna() | mc.m0.notna()]
    return inbox(frame(ev, EV, "cabello"), frame(pd.concat(mg), MG, "cabello"), frame(mc, MC, "cabello"))


def rm2018(d):
    """Ruiz and Madariaga (2018) table: dates as given (year only for some), Mw as text where qualified."""
    r = pd.read_csv(next(d.glob("*.csv")), dtype=str)
    i = r.name
    ev = pd.DataFrame(dict(src_id=i, origin_id=i, prime=True, time=r.date, lon=r.lon.map(num), lat=r.lat.map(num),
                           agency="rm2018", etype="earthquake", lat_n=r.lat_n, lat_s=r.lat_s, rm_class=r.rm_class,
                           domain=r.domain, basis=r.basis, note=r.note))
    mg = pd.DataFrame(dict(src_id=i, agency="rm2018", mag_type="Mw", mag=r.mw.map(num), note=r.mw))
    return frame(ev, EV, "rm2018"), frame(mg[r.mw.notna()], MG, "rm2018"), frame([], MC, "rm2018")


def sha(f):
    h = hashlib.sha256()
    with open(f, "rb") as x:
        for b in iter(lambda: x.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write(name, tabs, out=OUT):
    """Write the three tables dated by the download and update MANIFEST.csv."""
    raw = RAW / ("isc" if name == "csn_isc" else name)
    log = json.loads((raw / "fetch.json").read_text())
    day = log["downloaded"]
    q = log["query"] + (" (GUC origins and magnitudes)" if name == "csn_isc" else "")
    man = out / "MANIFEST.csv"
    m = pd.read_csv(man) if man.exists() else pd.DataFrame(
        columns=["file", "source", "version_or_query", "downloaded", "rows", "sha256"])
    for k, t in zip(("events", "mags", "mechs"), tabs):
        if t.empty:
            continue
        f = out / f"{name}_{day}_{k}.csv"
        t.to_csv(f, index=False)
        m = pd.concat([m[m.file != f.name], pd.DataFrame([dict(file=f.name, source=name, version_or_query=q,
                                                               downloaded=day, rows=len(t), sha256=sha(f))])])
        print(f"  {f.name}: {len(t)} rows")
    m.sort_values("file").to_csv(man, index=False)


def check(ev, mg, mc):
    """Sanity checks on the full tables of one source; returns the list of problems found (empty if none)."""
    bad = []
    say = lambda n, what: bad.append(f"{n:,} {what}") if n else None
    if len(ev):
        p = ev[ev.prime.astype(bool)]
        say((ev.groupby("src_id").prime.sum() != 1).sum(), "events without exactly one preferred origin")
        say(ev.duplicated(["src_id", "origin_id"]).sum(), "repeated origins")
        q = ev.dropna(subset=["lat", "lon"])
        q = q.lat.between(BOX["lat0"], BOX["lat1"]) & q.lon.between(BOX["lon0"], BOX["lon1"])
        say((~q.groupby(ev.src_id).any()).sum(), "events with no origin in the box")
        say(p.lat.isna().sum() + p.lon.isna().sum(), "preferred origins without lat or lon")
        y = pd.to_numeric(ev.time.astype(str).str[:4], errors="coerce")
        say((~y.between(1500, dt.date.today().year)).sum(), "origin times without a year in 1500–today")
        say((~ev.depth.dropna().between(-10, 800)).sum(), "depths outside −10–800 km")
        ids = set(ev.src_id)
        say((~mg.src_id.isin(ids)).sum(), "magnitudes without their event")
        say((~mc.src_id.isin(ids)).sum(), "mechanisms without their event")
    say((~mg.mag.dropna().between(-2, 10)).sum(), "magnitudes outside −2–10")
    say((~mc.mw.dropna().between(3, 10)).sum(), "mechanism Mw outside 3–10")
    say((mc.m0.dropna() <= 0).sum(), "non-positive moments")
    return bad


if __name__ == "__main__":
    for s in RUN:
        d = RAW / ("isc" if s == "csn_isc" else s)
        if not (d / "fetch.json").exists():
            print(f"{s}: not fetched, skipped")
            continue
        print(f"== {s}")
        tabs = globals()[s](d)
        write(s, tabs)
        ev, mg, mc = tabs
        print(f"  {ev.src_id.nunique():,} events, {mg.src_id.nunique():,} with a magnitude, "
              f"{mc.src_id.nunique():,} with a mechanism")
        for b in check(*tabs):
            print(f"  CHECK: {b}")
