"""S4 step 6: the smallest OpenQuake jobs that read every crustal file. One site (Puerto Aysén), ASK14, PGA, 475 yr.
One job per fault database (sourceModel = its four background files, extendModel = its 36 fault files) and one for
the no-faults files. Compares the rates OpenQuake builds per source with tables/rates_<DATE>.csv. No hazard is
interpreted.

Run from this folder with PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine; set CALCS after the jobs ran.
"""
import json

import numpy as np
import pandas as pd

import build as B
import nrml as X

# settings
SITE = ("Puerto Aysén", -72.7020, -45.4028)
GSIM = "[AbrahamsonEtAl2014]"
MESH = 5.0
D = B.F.HERE / "oqcheck"
JOBS = ("A", "B", "Bmm", "none")

JOB = """[general]
description = S3/S4 crustal check, {db}
calculation_mode = classical
random_seed = 23

[geometry]
sites = {lon} {lat}

[logic_tree]
number_of_logic_tree_samples = 0

[erf]
rupture_mesh_spacing = {mesh}
width_of_mfd_bin = 0.1
area_source_discretization = 10.0

[site_params]
reference_vs30_type = inferred
reference_vs30_value = 800.0
reference_depth_to_1pt0km_per_sec = 40.0
reference_depth_to_2pt5km_per_sec = 0.6

[calculation]
source_model_logic_tree_file = source_lt_{db}.xml
gsim_logic_tree_file = gmm_lt.xml
investigation_time = 50.0
intensity_measure_types_and_levels = {{"PGA": logscale(0.005, 3.0, 30)}}
truncation_level = 3.0
maximum_distance = {{"Active Shallow Crust": 300.0}}
pointsource_distance = 100.0

[output]
individual_rlzs = false
mean = true
poes = 0.1
"""


def jobs():
    D.mkdir(exist_ok=True)
    f = pd.DataFrame(json.loads((B.NR / "branches.json").read_text())["files"])
    X.gmm_tree(D / "gmm_lt.xml", B.TRT, GSIM)
    for db in JOBS:
        bg = f[(f.kind == "background") & (f.db == db)].file.tolist()
        lv = [("sourceModel", [(f"bg{i}", [f"../nrml/{x}"], 1 / len(bg)) for i, x in enumerate(bg)])]
        if db != "none":
            fl = f[(f.kind == "faults") & (f.db == db)]
            lv.append(("extendModel", [(f"f{i:02d}", [f"../nrml/{x}"], w) for i, (x, w) in enumerate(zip(fl.file, fl.weight))]))
        X.logic_tree(D / f"source_lt_{db}.xml", lv)
        (D / f"job_{db}.ini").write_text(JOB.format(db=db, lon=SITE[1], lat=SITE[2], mesh=MESH))


def compare(fn):
    """Rates per source of one file as OpenQuake's NRML converter builds them, against tables/rates_<DATE>.csv."""
    from openquake.hazardlib import nrml, sourceconverter
    conv = sourceconverter.SourceConverter(investigation_time=50.0, rupture_mesh_spacing=MESH, width_of_mfd_bin=0.1)
    sm = nrml.to_python(str(B.NR / fn), conv)
    rt = RT[RT.file == fn].set_index("source")
    out = []
    for g in sm.src_groups:
        for s in g:
            m, r = np.array(s.get_annual_occurrence_rates()).T
            t = rt.loc[s.source_id]
            out.append(dict(file=fn, source=s.source_id, N=r.sum(), N_tab=t.N5, m_top=m.max(), m_top_tab=t.m_top,
                            m_min=m.min()))
    x = pd.DataFrame(out)
    x["dN"] = x.N / x.N_tab - 1
    return x


def pga(calc):
    from openquake.commonlib import datastore
    ds = datastore.read(calc)
    return float(ds["hmaps-stats"][0, 0, 0, 0]), len(ds["weights"][:])


if __name__ == "__main__":
    jobs()
    RT = pd.read_csv(B.TAB / f"rates_{B.DATE}.csv")
    files = json.loads((B.NR / "branches.json").read_text())["files"]
    x = pd.concat([compare(f["file"]) for f in files])
    x.to_csv(B.TAB / f"oqcheck_{B.DATE}.csv", index=False, float_format="%.6e")
    n = x.groupby("file").agg(sources=("source", "size"), N=("N", "sum"), N_tab=("N_tab", "sum"),
                              max_dN=("dN", lambda v: v.abs().max()), m_top_ok=("m_top", "size"))
    n["m_top_ok"] = x.assign(ok=(x.m_top.round(2) == x.m_top_tab.round(2))).groupby("file").ok.all()
    n["n_files_expected"] = [next(f["n_sources"] for f in files if f["file"] == k) for k in n.index]
    print(n.to_string())
    print("all files:", len(n), "of", len(files), "; max |dN|", x.dN.abs().max(), "; m_top equal", bool(n.m_top_ok.all()),
          "; source counts equal", bool((n.sources == n.n_files_expected).all()))
    # calculation ids of the jobs once they have run (oq engine --run job_<db>.ini from oqcheck/)
    CALCS = {"none": 501, "A": None, "B": None, "Bmm": None}
    for db, c in CALCS.items():
        if c is not None:
            print(db, "calc", c, "mean PGA 475 yr %.3f g, %d realizations" % pga(c))
