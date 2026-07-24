# s05_sources.py
# Build the OpenQuake inputs for the subduction interface tree. Pure
# read-input/write-output: NRML 0.4 written directly (no openquake import;
# the engine validates sources when the job runs).
#   hazard/src/sub_int__{geom}__{rate}__{form}.xml   16 end-branch models
#   hazard/source_logictree_sub.xml                  weights from s04
#   hazard/sites_cities.csv, hazard/job_cities.ini
# MFDs: EvenlyDiscretized from the s04 branch shape, min_mag = first bin
# CENTER (MMIN_HAZ + BIN_W/2) — the half-bin fix. Every source's rate sum
# is checked against branch_params.

import json

import numpy as np
import pandas as pd

import sub_config as C
from s04_rates import cum_shape

HZ_DIR = C.OUT_DIR / "hazard"
SRC_DIR = HZ_DIR / "src"

RATES = [("seismic", "-", "seis"), ("geodetic", "lo", "geo_lo"),
         ("geodetic", "mid", "geo_mid"), ("geodetic", "hi", "geo_hi")]

CITIES = [("iquique", -70.14, -20.21), ("antofagasta", -70.40, -23.65),
          ("copiapo", -70.33, -27.37), ("valparaiso", -71.62, -33.05),
          ("santiago", -70.66, -33.45), ("concepcion", -73.05, -36.83),
          ("valdivia", -73.25, -39.81)]


def branch_rates(lam, b, form, mmax):
    nb = int(round((mmax - C.MMIN_HAZ) / C.BIN_W))
    edges = C.MMIN_HAZ + C.BIN_W * np.arange(nb + 1)
    ncum = lam * cum_shape(form, b, C.MMIN_HAZ, mmax, edges)
    inc = np.maximum(ncum[:-1] - ncum[1:], 0.0)
    if inc.sum() <= 0:
        raise RuntimeError("empty MFD")
    if abs(inc.sum() - lam) > 0.02 * lam:
        raise RuntimeError(f"MFD sum {inc.sum():.4g} != lam {lam:.4g}")
    return inc


def edge_xml(edge, kind, ind):
    pos = " ".join(f"{n['lon']:.5f} {n['lat']:.5f} {n['depth_km']:.3f}"
                   for n in edge["nodes"])
    return (f"{ind}<{kind}>\n{ind}    <gml:LineString>\n"
            f"{ind}        <gml:posList>\n{ind}            {pos}\n"
            f"{ind}        </gml:posList>\n{ind}    </gml:LineString>\n"
            f"{ind}</{kind}>")


def source_xml(sid, edges, row):
    inc = branch_rates(row["lam_mmin"], row["b"], row["form"], row["mmax"])
    ind = "        "
    kinds = (["faultTopEdge"] + ["intermediateEdge"] * (len(edges) - 2)
             + ["faultBottomEdge"])
    geo = "\n".join(edge_xml(e, k, ind + "        ")
                    for e, k in zip(edges, kinds))
    rates = " ".join(f"{r:.8e}" for r in inc)
    return f"""{ind}<complexFaultSource id="{sid}" name="{sid}"
{ind}                    tectonicRegion="{C.TRT}">
{ind}    <complexFaultGeometry>
{geo}
{ind}    </complexFaultGeometry>
{ind}    <magScaleRel>StrasserInterface</magScaleRel>
{ind}    <ruptAspectRatio>{C.ASPECT}</ruptAspectRatio>
{ind}    <incrementalMFD minMag="{C.MMIN_HAZ + C.BIN_W / 2}" binWidth="{C.BIN_W}">
{ind}        <occurRates>{rates}</occurRates>
{ind}    </incrementalMFD>
{ind}    <rake>{C.RAKE}</rake>
{ind}</complexFaultSource>"""


def model_xml(name, sources):
    body = "\n".join(sources)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<nrml xmlns:gml="http://www.opengis.net/gml"
      xmlns="http://openquake.org/xmlns/nrml/0.4">
    <sourceModel name="{name}">
{body}
    </sourceModel>
</nrml>
"""


def main():
    SRC_DIR.mkdir(parents=True, exist_ok=True)

    bp = pd.read_csv(C.OUT_DIR / "rates" / "branch_params.csv")
    segs = json.loads((C.GEOM_DIR / "segments.json").read_text())
    glob = json.loads((C.GEOM_DIR / "global_geometry.json").read_text())

    branches = []
    for geom, gtag in (("segmented", "seg"), ("non_segmented", "full")):
        for rate, chi, rtag in RATES:
            for form in ("tgr", "tapered"):
                sub = bp[(bp["geom"] == geom) & (bp["rate_model"] == rate)
                         & (bp["chi_branch"] == chi) & (bp["form"] == form)]
                if not len(sub):
                    raise RuntimeError(f"no rows for {geom}/{rate}/{chi}/{form}")
                tag = f"{gtag}__{rtag}__{form}"
                srcs = []
                for _, r in sub.iterrows():
                    ed = (glob["edges"] if r["seg"] == C.FULL_ID
                          else segs[r["seg"]]["edges"])
                    srcs.append(source_xml(f"{r['seg']}_{tag}", ed, r))
                fname = f"sub_int__{tag}.xml"
                (SRC_DIR / fname).write_text(
                    model_xml(f"subduction interface {tag}", srcs))
                branches.append((tag, fname, float(sub["weight"].iloc[0])))
                print(f"{fname}: {len(srcs)} sources, "
                      f"w={sub['weight'].iloc[0]:.5f}")

    # source logic tree, last branch absorbs rounding
    ws = [w for _, _, w in branches]
    if abs(sum(ws) - 1.0) > 1e-6:
        raise RuntimeError(f"branch weights sum to {sum(ws)}")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<nrml xmlns:gml="http://www.opengis.net/gml"',
             '      xmlns="http://openquake.org/xmlns/nrml/0.4">',
             '    <logicTree logicTreeID="lt_sub_interface">',
             '        <logicTreeBranchingLevel branchingLevelID="bl1">',
             '            <logicTreeBranchSet uncertaintyType="sourceModel"',
             '                                branchSetID="bs_sub">']
    acc = 0.0
    for i, (tag, fname, w) in enumerate(branches):
        wstr = (f"{1.0 - acc:.12f}" if i == len(branches) - 1
                else f"{round(w, 12):.12f}")
        acc += float(wstr)
        lines += [f'                <logicTreeBranch branchID="{tag}">',
                  '                    <uncertaintyModel>',
                  f'                        src/{fname}',
                  '                    </uncertaintyModel>',
                  f'                    <uncertaintyWeight>{wstr}</uncertaintyWeight>',
                  '                </logicTreeBranch>']
    lines += ['            </logicTreeBranchSet>',
              '        </logicTreeBranchingLevel>',
              '    </logicTree>', '</nrml>']
    (HZ_DIR / "source_logictree_sub.xml").write_text("\n".join(lines) + "\n")

    rows = "\n".join(f"{lon},{lat},380" for _, lon, lat in CITIES)
    (HZ_DIR / "sites_cities.csv").write_text("lon,lat,vs30\n" + rows + "\n")

    (HZ_DIR / "job_cities.ini").write_text(f"""[general]
description = sub interface branch sensitivity, cities{C.RUN_TAG}
calculation_mode = classical

[geometry]
sites_csv = sites_cities.csv

[logic_tree]
number_of_logic_tree_samples = 0

[erf]
rupture_mesh_spacing = {C.RUPT_MESH}
width_of_mfd_bin = {C.BIN_W}
complex_fault_mesh_spacing = {C.RUPT_MESH}

[site_params]
reference_vs30_type = measured
reference_vs30_value = 380
reference_depth_to_2pt5km_per_sec = 5.0
reference_depth_to_1pt0km_per_sec = 100.0

[calculation]
source_model_logic_tree_file = source_logictree_sub.xml
gsim_logic_tree_file = gmm_logictree.xml
investigation_time = 1.0
intensity_measure_types_and_levels = {{"PGA": logscale(0.005, 3.0, 30)}}
truncation_level = 3
maximum_distance = 400.0

[output]
export_dir = ./out{C.RUN_TAG}
individual_rlzs = true
mean = true
quantiles = 0.16 0.84
poes = 0.002105 0.000404
""")
    print(f"\nwrote {len(branches)} models, logic tree, sites, job to {HZ_DIR}")


if __name__ == "__main__":
    main()