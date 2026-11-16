"""S2 step 5: the smallest OpenQuake jobs that read every in-slab file. One site (Calama), AG20, PGA, 475 yr.

job_all.ini reads all 24 branches (72 files); the rates per class and branch that OpenQuake holds are compared with
tables/rates_<DATE>.csv. job_ps100 / job_ps500 / job_one run the reference branch (gk, tapered, ML, three hypocentres)
with pointsource_distance 100 and 500 km and its one-layer twin, for the run time of the depth settings.

Run the jobs from oqcheck/ (`oq engine --run job_<name>.ini`, PYTHONPATH set to the oq-engine checkout), put their
calculation ids into CALCS and run this file again.
"""
import json
import re

import numpy as np
import pandas as pd

import build as B

# settings; CALCS holds calculation ids, or a job file to read the sources without running (OQ_DISTRIBUTE=no)
SITE = ("Calama", -68.9333, -22.4667)
GSIM = '[AbrahamsonGulerce2020SSlab]\nregion = "SAM"'
D = B.HERE / "oqcheck" / B.DATE
REF = "gk_taper_ml"
JOBS = {"all": dict(files=None, psdist=100), "ps100": dict(files=f"{REF}_l3", psdist=100),
        "ps500": dict(files=f"{REF}_l3", psdist=500), "one": dict(files=f"{REF}_l1", psdist=100)}
CALCS = {"all": D / "job_all.ini", "ps100": None, "ps500": None, "one": None}

JOB = """[general]
description = S2 in-slab check, {name}
calculation_mode = classical
random_seed = 23

[geometry]
sites = {lon} {lat}

[logic_tree]
number_of_logic_tree_samples = 0

[erf]
rupture_mesh_spacing = 5.0
width_of_mfd_bin = 0.1
pointsource_distance = {{"default": {psdist}}}

[site_params]
reference_vs30_type = inferred
reference_vs30_value = 800.0
reference_depth_to_1pt0km_per_sec = 40.0
reference_depth_to_2pt5km_per_sec = 0.6

[calculation]
source_model_logic_tree_file = source_lt_{name}.xml
gsim_logic_tree_file = gmm_lt.xml
investigation_time = 1.0
intensity_measure_types_and_levels = {{"PGA": logscale(0.005, 3.0, 30)}}
truncation_level = 3.0
maximum_distance = {{"Subduction IntraSlab": 500.0}}

[output]
individual_rlzs = false
mean = true
poes = 0.002105
"""


def jobs():
    D.mkdir(parents=True, exist_ok=True)
    br = pd.DataFrame(json.loads((B.NR / "branches.json").read_text())["branches"])
    (D / "gmm_lt.xml").write_text(
        B.HEAD + '<logicTree logicTreeID="lt_gmm">\n<logicTreeBranchingLevel branchingLevelID="gl1">\n'
        f'<logicTreeBranchSet uncertaintyType="gmpeModel" branchSetID="gs1" applyToTectonicRegionType="{B.TRT}">\n'
        f'<logicTreeBranch branchID="g1"><uncertaintyModel>{GSIM}</uncertaintyModel><uncertaintyWeight>1.0</uncertaintyWeight>'
        "</logicTreeBranch>\n</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n</logicTree>\n</nrml>\n")
    for name, j in JOBS.items():
        b = br if j["files"] is None else br[br.id == j["files"]]
        b = b.assign(files=b.files.apply(lambda f: [f"../../nrml/{B.DATE}/{x}" for x in f]), weight=1 / len(b))
        B.logic_tree(D / f"source_lt_{name}.xml", b)
        (D / f"job_{name}.ini").write_text(JOB.format(name=name, lon=SITE[1], lat=SITE[2], psdist=j["psdist"]))


def compare(calc):
    """Rates per class and branch as OpenQuake reads them (the composite source model of a calculation, or of a job
    file read without running it) against the build table, and the mean PGA of a calculation."""
    from openquake.commonlib import datastore, readinput
    ds = datastore.read(calc) if isinstance(calc, int) else None
    csm = readinput.get_composite_source_model(ds["oqparam"] if ds else readinput.get_oqparam(str(calc)))
    path = {i: re.search(r"path=is_(\w+?)_(taper|trunc)_(\w+?)_(l\d)", str(r)).groups() for i, r in enumerate(csm.full_lt.sm_rlzs)}
    out = {}
    for g in csm.src_groups:
        for s in g:
            m, r = np.array(s.get_annual_occurrence_rates()).T
            for t in s.trt_smrs:
                o = out.setdefault((s.source_id[:4],) + path[int(t) % 2 ** 24], np.zeros(5))
                h = np.array(s.hypocenter_distribution.data)
                ok = (h[:, 1] >= s.upper_seismogenic_depth) & (h[:, 1] <= s.lower_seismogenic_depth)
                o += [r.sum(), r[m > 6.95].sum(), 1, abs(h[:, 0].sum() - 1) > 1e-9, (~ok).sum()]
    rt = pd.read_csv(B.TAB / f"rates_{B.DATE}.csv")
    rt["key"] = rt.cls.map({c: "is" + s["short"][:2] for c, s in B.CLASSES.items()})
    rows = []
    for (sid, k, sh, ab, ly), (n5, n7, ns, bad_w, bad_h) in out.items():
        t = rt[(rt.key == sid) & (rt.decl == k) & (rt["shape"] == sh) & (rt.ab == ab)].iloc[0]
        rows.append(dict(cls=t.cls, decl=k, shape=sh, ab=ab, layers=ly, sources=int(ns), sources_built=t.sources, N5_oq=n5,
                         N5=t.N5, N7_oq=n7, N7=t.N7, weights_not_1=int(bad_w), hypo_outside=int(bad_h)))
    x = pd.DataFrame(rows)
    x["dN5"], x["dN7"] = x.N5_oq / x.N5 - 1, x.N7_oq / x.N7 - 1
    return x, float(ds["hmaps-stats"][0, 0, 0, 0]) if ds else float("nan")


def read_one(f):
    """One file read by the OpenQuake parser: sources, N(>= 5.5), N(>= 7), first magnitude, hypocentre weights
    not summing to 1, hypocentres outside the zone."""
    from openquake.hazardlib import nrml, sourceconverter
    conv = sourceconverter.SourceConverter(investigation_time=1.0, rupture_mesh_spacing=5.0, width_of_mfd_bin=0.1)
    n, n55, n7, m0, bad_w, bad_h = 0, 0.0, 0.0, 99.0, 0, 0
    for grp in nrml.to_python(str(f), conv):
        for s in grp:
            m, r = np.array(s.get_annual_occurrence_rates()).T
            h = np.array(s.hypocenter_distribution.data)
            n, n55, n7, m0 = n + 1, n55 + r.sum(), n7 + r[m > 6.95].sum(), min(m0, m.min())
            bad_w += abs(h[:, 0].sum() - 1) > 1e-9
            bad_h += int(((h[:, 1] < s.upper_seismogenic_depth) | (h[:, 1] > s.lower_seismogenic_depth)).sum())
    return f.name, n, n55, n7, m0, bad_w, bad_h


def read_all():
    """Every NRML file read by the OpenQuake parser (in parallel), against tables/rates_<DATE>.csv."""
    from multiprocessing import Pool
    with Pool(16) as pool:
        q = pool.map(read_one, sorted(B.NR.glob("is_*.xml")))
    x = pd.DataFrame(q, columns=["file", "sources", "N55_oq", "N7_oq", "m_first", "weights_not_1", "hypo_outside"])
    k = x.file.str.extract(r"is_(\w+?)_(gk|nn)_(taper|trunc)_(p05|ml|p95)_(l\d)\.xml")
    x[["short", "decl", "shape", "ab", "layers"]] = k
    rt = pd.read_csv(B.TAB / f"rates_{B.DATE}.csv")
    rt["short"] = rt.cls.map({c: s["short"] for c, s in B.CLASSES.items()})
    x = x.merge(rt[["short", "decl", "shape", "ab", "sources", "N5.5", "N7"]].rename(columns={"sources": "sources_built"}),
                on=["short", "decl", "shape", "ab"])
    x["dN55"], x["dN7"] = x.N55_oq / x["N5.5"] - 1, x.N7_oq / x.N7 - 1
    return x


if __name__ == "__main__":
    jobs()
    rows = []
    for name, c in CALCS.items():
        if c is None:
            continue
        x, pga = compare(c)
        print(f"{name}: calc {c}, mean PGA 475 yr {pga:.3f} g")
        if name == "all":
            print(f"{len(x)} class-branch sets, max |dN5| {x.dN5.abs().max():.2e}, max |dN7| {x.dN7.abs().max():.2e}")
            x.insert(0, "calc", c)
            x.to_csv(B.TAB / f"oqcheck_{B.DATE}.csv", index=False)
