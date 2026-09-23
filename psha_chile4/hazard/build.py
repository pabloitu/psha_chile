# Build the source models of the jobs listed in logic_tree.BUILD and write one
# self-contained OpenQuake job per entry: outputs/hazard/<NAME>/{job.ini, source_lt.xml, gmm_lt.xml,
# sites.csv, src/, build.json}. A job may carry "gmm": {trt: [...]}, which
# replaces logic_tree.GMM for those regions, and "site": {"VS30": ...}, which
# replaces the site parameters of hazard/config.py. Run this file in PyCharm, then
#   cd outputs/hazard/<NAME> && oq engine --run job.ini
# and put the calc id in post.py (or in build.json as "calc_id").

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hashlib
import importlib
import itertools
import json
import shutil

import numpy as np
import pandas as pd

import run
from lib import nrml
from variants import VARIANTS
from hazard import config as hc
from hazard import logic_tree as lt

SHORT = {"interface": "if", "intraslab": "is", "crustal": "cr"}


def sites(hd):
    if hc.SITES == "cities":
        df = pd.DataFrame([{"name": k, "lon": x, "lat": y} for k, (x, y) in hc.CITIES.items()])
    elif hc.GRID_CSV:
        df = pd.read_csv(hc.GRID_CSV)[["lon", "lat"]]
    else:
        lo, hi, la, ha = hc.GRID_BBOX
        x, y = np.meshgrid(np.arange(lo, hi + 1e-9, hc.GRID_STEP), np.arange(la, ha + 1e-9, hc.GRID_STEP))
        df = pd.DataFrame({"lon": x.ravel().round(4), "lat": y.ravel().round(4)})
    df[["lon", "lat"]].to_csv(hd / "sites.csv", index=False)
    return df


def source_branches(hd):
    """
    One branch set per family (variant weight x internal weight), NRMLs copied
    into src/, then the product across families.

    Returns
    -------
    list of (branch_id, [files], weight), and the TRT of each family.
    """
    sets, trts = [], {}
    for fam, vs in lt.SOURCES.items():
        vs = [(e[0], e[1], e[2] if len(e) > 2 else None) for e in vs]
        if abs(sum(e[1] for e in vs) - 1.0) > 1e-6:
            raise ValueError(f"variant weights for {fam} do not sum to 1")
        trts[fam] = importlib.import_module(f"{fam}.config").TRT
        rows = []
        for v, wv, pick in vs:
            if "-" in v:
                raise ValueError(f"variant name {v} must not contain '-'")
            if v not in VARIANTS[fam]:
                raise KeyError(f"{fam}: unknown variant {v}; available {list(VARIANTS[fam])}")
            c = run.build(fam, VARIANTS[fam][v])
            sd = hd / "src" / fam / v
            sd.mkdir(parents=True, exist_ok=True)
            bs = json.loads((c.OUT / "nrml" / "branches.json").read_text())
            if pick is not None:
                bad = [x for x in pick if x not in {b["id"] for b in bs}]
                if bad:
                    raise KeyError(f"{fam}/{v}: unknown branches {bad}; available {[b['id'] for b in bs]}")
                bs = [b for b in bs if b["id"] in pick]
                if isinstance(pick, dict):
                    if abs(sum(pick.values()) - 1.0) > 1e-6:
                        raise ValueError(f"{fam}/{v}: branch weights {pick} do not sum to 1")
                    bs = [{**b, "weight": pick[b["id"]]} for b in bs]
                else:
                    tot = sum(b["weight"] for b in bs)
                    zero = [b["id"] for b in bs if b["weight"] == 0]
                    if zero and len(bs) > 1:
                        raise ValueError(f"{fam}/{v}: {zero} have weight 0 in the model; "
                                         "give weights explicitly as a dict, e.g. {id: 0.5, ...}")
                    bs = [{**b, "weight": b["weight"] / tot if tot else 1.0} for b in bs]
                bs = [b for b in bs if b["weight"] > 0]
            else:
                bs = [b for b in bs if b["weight"] > 0]
            for b in bs:
                fs = b.get("files", [b.get("file")])
                for fn in fs:
                    shutil.copy(c.OUT / "nrml" / fn, sd / fn)
                rows.append((f"{SHORT.get(fam, fam[:2])}-{v}-{b['id']}", [f"src/{fam}/{v}/{fn}" for fn in fs],
                             wv * b["weight"], c.TAG))
        sets.append(rows)
    br = [("_x_".join(r[0] for r in combo), [f for r in combo for f in r[1]], float(np.prod([r[2] for r in combo])))
          for combo in itertools.product(*sets)]
    ids = {f"b{i:05d}" if len(b[0]) > 75 else b[0]: b[0] for i, b in enumerate(br)}
    br = [(k, b[1], b[2]) for k, b in zip(ids, br)]
    tags = {r[0]: r[3] for s in sets for r in s}
    return br, trts, tags, ids


def job(hd, desc, site=None):
    st = site or {}
    imtl = ", ".join(f'"{k}": logscale({a}, {b}, {hc.N_LEVELS})' for k, (a, b) in hc.IMTL.items())
    return f"""[general]
description = {desc}
calculation_mode = classical

[geometry]
sites_csv = sites.csv

[logic_tree]
number_of_logic_tree_samples = 0

[erf]
rupture_mesh_spacing = {hc.MESH}
complex_fault_mesh_spacing = {hc.MESH}
width_of_mfd_bin = 0.1
pointsource_distance = {hc.PS_DIST}

[site_params]
reference_vs30_type = measured
reference_vs30_value = {st.get("VS30", hc.VS30)}
reference_depth_to_1pt0km_per_sec = {st.get("Z1PT0", hc.Z1PT0)}
reference_depth_to_2pt5km_per_sec = {st.get("Z2PT5", hc.Z2PT5)}

[calculation]
source_model_logic_tree_file = source_lt.xml
gsim_logic_tree_file = gmm_lt.xml
investigation_time = {hc.INV_TIME}
intensity_measure_types_and_levels = {{{imtl}}}
truncation_level = {hc.TRUNC}
maximum_distance = {hc.MAX_DIST}
max_sites_disagg = {10 if getattr(hc, "STORE_RUPTURES", False) else 1}

[output]
individual_rlzs = {str(hc.INDIVIDUAL_RLZS).lower()}
mean = true
quantiles = 0.16 0.5 0.84
poes = {" ".join(str(p) for p in hc.POES)}
"""


def main():
    names = getattr(lt, "BUILD", None) or [lt.NAME]
    for n in names:
        lt.NAME = n
        job = dict(lt.JOBS[n]) if hasattr(lt, "JOBS") else dict(lt.SOURCES)
        lt.GMM_JOB = {**lt.GMM, **job.pop("gmm", {})}
        lt.SITE_JOB = job.pop("site", {})
        lt.SOURCES = job
        one()


def one():
    hd = hc.OUT_ROOT / lt.NAME
    if hd.exists():
        shutil.rmtree(hd / "src", ignore_errors=True)
    hd.mkdir(parents=True, exist_ok=True)

    st = sites(hd)
    br, trts, tags, ids = source_branches(hd)
    nrml.logic_tree(hd / "source_lt.xml", br)
    g = getattr(lt, "GMM_JOB", lt.GMM)
    gmm = {t: g[t] for t in dict.fromkeys(trts.values())}
    nrml.gmm_tree(hd / "gmm_lt.xml", gmm)

    # key from everything OpenQuake reads, so an unchanged job keeps its calc id
    site = getattr(lt, "SITE_JOB", {})
    h = hashlib.sha1(job(hd, "", site).encode())
    for f in [hd / "source_lt.xml", hd / "gmm_lt.xml", hd / "sites.csv"] + sorted((hd / "src").rglob("*.xml")):
        h.update(f.read_bytes())
    key = h.hexdigest()[:8]
    desc = f"psha_chile4 {lt.NAME} {key}"
    (hd / "job.ini").write_text(job(hd, desc, site))
    old = json.loads((hd / "build.json").read_text()) if (hd / "build.json").exists() else {}
    cid = old.get("calc_id") if old.get("description") == desc else None

    n_rlz = len(br) * int(np.prod([len(v) for v in gmm.values()]))
    info = {"name": lt.NAME, "description": desc, "calc_id": cid, "sites": hc.SITES, "site_params": site,
            "site_names": st["name"].tolist() if "name" in st else None,
            "sources": lt.SOURCES, "gmm": gmm, "trts": trts, "builds": tags,
            "poes": hc.POES, "n_source_branches": len(br), "n_realizations": n_rlz,
            "branch_map": ids}
    (hd / "build.json").write_text(json.dumps(info, indent=1))
    print(f"{hd}\n  {len(st)} sites ({hc.SITES}), {len(br)} source branches, "
          f"{n_rlz} realizations\n  description: {desc}"
          + (f"\n  unchanged, keeps calc {cid}" if cid else f"\n  run: cd {hd} && oq engine --run job.ini"))


if __name__ == "__main__":
    main()