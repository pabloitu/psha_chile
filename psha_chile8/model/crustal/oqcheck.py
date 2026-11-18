"""S5b check of the crustal OpenQuake files: every file of branches.json read by OpenQuake's converter (multi-fault
sources with their sections), the rates per source against tables/rates_<DATE>.csv, and one small job (the reference
branch, Puerto Aysén, ASK14, PGA, 1 yr) to show that the multi-fault source runs. No hazard is interpreted.

Run from this folder with PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine.
"""
import json
import os

os.environ.setdefault("OQ_DISTRIBUTE", "no")

import numpy as np
import pandas as pd

import build as B

# settings
SITE = ("Puerto Aysén", -72.7020, -45.4028)
GSIM = "[AbrahamsonEtAl2014]"
D = B.F.HERE / "oqcheck" / B.DATE

JOB = """[general]
description = S5b crustal reference, one site
calculation_mode = classical
random_seed = 23

[geometry]
sites = {lon} {lat}

[logic_tree]
number_of_logic_tree_samples = 0

[erf]
rupture_mesh_spacing = 5.0
width_of_mfd_bin = 0.1
area_source_discretization = 10.0

[site_params]
reference_vs30_type = inferred
reference_vs30_value = 800.0
reference_depth_to_1pt0km_per_sec = 40.0
reference_depth_to_2pt5km_per_sec = 0.6

[calculation]
source_model_logic_tree_file = {lt}
gsim_logic_tree_file = gmm_lt.xml
investigation_time = 1.0
intensity_measure_types_and_levels = {{"PGA": logscale(0.005, 3.0, 30)}}
truncation_level = 3.0
maximum_distance = {{"Active Shallow Crust": 300.0}}
pointsource_distance = 100.0

[output]
individual_rlzs = false
mean = true
poes = 0.002105
"""


def job():
    """Job folder with the reference logic tree, its files and a one-branch GMM tree."""
    import shutil
    D.mkdir(parents=True, exist_ok=True)
    for f in ["lt_crustal_reference.xml"] + next(r for r in json.loads((B.NR / "tornado.json").read_text())["rows"] if r["id"] == "reference")["branches"][0]["files"]:
        shutil.copy(B.NR / f, D / f)
    B.X.gmm_tree(D / "gmm_lt.xml", B.TRT, GSIM)
    (D / "job.ini").write_text(JOB.format(lon=SITE[1], lat=SITE[2], lt="lt_crustal_reference.xml"))
    print("job in", D)


def parse(fn, sections, conv):
    """Rates per source of one file as OpenQuake builds them: total rate, top magnitude, ruptures."""
    from openquake.hazardlib import nrml
    sm = nrml.to_python(str(B.NR / fn), conv)
    secs = None
    if sections:
        conv.fname = str(B.NR / sections)
        secs = conv.convert_geometryModel(nrml.read(str(B.NR / sections))[0])
    out = []
    for grp in sm.src_groups:
        for s in grp:
            if type(s).__name__ == "MultiFaultSource":
                import tempfile
                from openquake.hazardlib.source.multi_fault import save_and_split
                with tempfile.TemporaryDirectory() as tmp:
                    save_and_split([s], secs, f"{tmp}/mf.hdf5", split=False)
                    n = int(s.count_ruptures())
                r = -np.log(np.array([p[0] for p in s.probs_occur]))
                out.append(dict(source=s.source_id, N_oq=float(r.sum()), m_top_oq=float(np.max(s.mags)), ruptures=n))
            else:
                mags = [(m, r) for m, r in s.mfd.get_annual_occurrence_rates()]
                out.append(dict(source=s.source_id, N_oq=float(sum(r for _, r in mags)), m_top_oq=float(max(m for m, _ in mags)),
                                ruptures=int(s.count_ruptures())))
    return pd.DataFrame(out)


def main():
    from openquake.hazardlib.sourceconverter import SourceConverter
    conv = SourceConverter(investigation_time=1.0, rupture_mesh_spacing=5.0, width_of_mfd_bin=0.1,
                           area_source_discretization=10.0)
    br = json.loads((B.NR / "branches.json").read_text())
    rt = pd.read_csv(B.TAB / f"rates_{B.DATE}.csv")
    res = []
    for f in br["files"]:
        x = parse(f["file"], f.get("sections"), conv)
        y = rt[rt.file == f["file"]].merge(x, on="source", how="outer")
        res.append(y.assign(file=f["file"]))
        print(f["file"], len(x), "sources", "max |dN|", float(np.abs(y.N - y.N_oq).max()))
    t = pd.concat(res)
    t.to_csv(B.TAB / f"oqcheck_{B.DATE}.csv", index=False, float_format="%.6e")
    rel = np.abs(t.N - t.N_oq) / t.N
    print("files:", len(br["files"]), "; sources:", len(t), "; missing:", int(t.N.isna().sum() + t.N_oq.isna().sum()),
          "; max relative dN:", float(rel.max()), "; m_top equal:", bool(np.allclose(t.m_top, t.m_top_oq, atol=1e-6)))
    job()


if __name__ == "__main__":
    main()
