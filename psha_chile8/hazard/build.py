# Write one self-contained OpenQuake job per entry of BUILD (hazard/jobs.py) into hazard/jobs/<name>/:
# job.ini, source_lt.xml, gmm_lt.xml, sites.csv, site_model.csv, src/ (NRML files hard-linked from the family
# folders), build.json with a hash of every file OpenQuake reads (an unchanged job keeps its calc id).
# Ported from psha_chile7 hazard/build.py; the families are already built, so the files come from their tree.json
# and tornado.json. A job may carry "sites": "grid" (hc.GRID instead of the cities) or a file of hazard/sites/, "poes", "ini" (job.ini keys) and "rebin" ({family: k}, MFD bins merged k at a time in the job's
# copies of the files).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hashlib
import json
import os
import re
import shutil

import numpy as np

from hazard import config as hc
from hazard import jobs as J
from hazard import nrml

# settings
BUILD = None            # None: every job in jobs.RUN; else a list of names


def branches(fam):
    """{branch id: [file paths]}: the tree branches (crustal: paths) and the tornado rows of the family folder. A
    crustal row with one branch is <row>, with several <row>_<id>; interface and in-slab rows use their branch ids."""
    d = hc.FAMILIES[fam]["dir"]
    t, r = J.manifests(fam)
    out = {}
    for x in t.get("branches") or t["paths"]:
        fs = x.get("files", x.get("file"))
        out[x["id"]] = [d / f for f in ([fs] if isinstance(fs, str) else fs)]
    for row in r["rows"]:
        if fam == "crustal":
            b = row["branches"]
            new = {row["id"] if len(b) == 1 else f"{row['id']}_{x['id']}": x["files"] for x in b}
        else:
            new = row["files"]
        for k, fs in new.items():
            fs = [d / f for f in ([fs] if isinstance(fs, str) else fs)]
            if k in out and out[k] != fs:
                raise ValueError(f"{fam}: branch {k} has two file lists")
            out[k] = fs
    return out


def rebin(text, k):
    """Incremental MFDs of the text with k bins merged: rates summed, first bin centre the mean of the first k."""
    def one(m):
        m0, dm, r = float(m.group(1)), float(m.group(2)), np.array(m.group(3).split(), float)
        r = np.pad(r, (0, -len(r) % k)).reshape(-1, k).sum(1)
        return (f'<incrementalMFD minMag="{m0 + dm * (k - 1) / 2:.3f}" binWidth="{dm * k:.2f}">\n'
                f'                <occurRates>{" ".join(f"{x:.8e}" for x in r)}</occurRates>')
    return re.sub(r'<incrementalMFD minMag="([\d.]+)" binWidth="([\d.]+)">\s*<occurRates>([^<]+)</occurRates>', one, text)


def link(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy(src, dst)


def ini(desc, trts, trunc, poes, extra=None):
    """job.ini text; extra {key: value} replaces a key of the text or is added to [calculation]."""
    s = base(desc, trts, trunc, poes)
    for k, v in (extra or {}).items():
        line = next((x for x in s.splitlines() if x.startswith(f"{k} =")), None)
        s = s.replace(line, f"{k} = {v}") if line else s.replace("[output]", f"{k} = {v}\n\n[output]")
    return s


def base(desc, trts, trunc, poes):
    imtl = ", ".join(f'"{k}": logscale({a}, {b}, {hc.N_LEVELS})' for k, (a, b) in hc.IMTL.items())
    md = json.dumps({t: hc.MAX_DIST[t] for t in trts})
    return f"""[general]
description = {desc}
calculation_mode = classical
random_seed = 23
strict = false

[geometry]
site_model_file = site_model.csv

[logic_tree]
number_of_logic_tree_samples = 0

[erf]
rupture_mesh_spacing = {hc.MESH}
complex_fault_mesh_spacing = {hc.MESH}
width_of_mfd_bin = {hc.MFD_BIN}
pointsource_distance = {hc.PS_DIST}

[calculation]
source_model_logic_tree_file = source_lt.xml
gsim_logic_tree_file = gmm_lt.xml
investigation_time = {hc.INV_TIME}
intensity_measure_types_and_levels = {{{imtl}}}
truncation_level = {trunc}
maximum_distance = {md}

[output]
individual_rlzs = {str(hc.INDIVIDUAL_RLZS).lower()}
mean = true
poes = {" ".join(str(p) for p in poes)}
"""


def one(name, job):
    """Write the job folder of one job; returns build.json as a dict."""
    hd = hc.JOBS_DIR / name
    shutil.rmtree(hd / "src", ignore_errors=True)
    hd.mkdir(parents=True, exist_ok=True)
    if job.get("sites"):
        f = hc.GRID if job["sites"] == "grid" else hc.HERE / "sites" / job["sites"]
        names, xy = None, np.loadtxt(f, delimiter=",", skiprows=1)
    else:
        names, xy = list(hc.CITIES), np.array(list(hc.CITIES.values()))
    (hd / "sites.csv").write_text("lon,lat\n" + "".join(f"{x},{y}\n" for x, y in xy))
    # soiltype 1 (Idini et al. 2017 class sI, rock) for the MASCSN26 set; read by no other GMM
    (hd / "site_model.csv").write_text("lon,lat,vs30,vs30measured,z1pt0,z2pt5,soiltype\n" + "".join(
        f"{x},{y},{hc.VS30},0,{hc.Z1PT0},{hc.Z2PT5},1\n" for x, y in xy))

    levels, trts, fams = [], [], [f for f in hc.FAMILIES if f in job]
    for fam in fams:
        fa = hc.FAMILIES[fam]
        bs = branches(fam)
        bad = [b for b in job[fam] if b not in bs]
        if bad:
            raise KeyError(f"{name}: {fam} has no branches {bad}")
        if abs(sum(job[fam].values()) - 1) > 1e-6:
            raise ValueError(f"{name}: {fam} weights sum to {sum(job[fam].values())}")
        rows = []
        for b, w in job[fam].items():
            for f in bs[b]:
                link(f, hd / "src" / fam / f.name)
                if fam in job.get("rebin", {}):
                    s = rebin(f.read_text(), job["rebin"][fam])
                    (hd / "src" / fam / f.name).unlink()
                    (hd / "src" / fam / f.name).write_text(s)
            rows.append((f"{fa['short']}_{b}", [f"src/{fam}/{f.name}" for f in bs[b]], w))
        levels.append(rows)
        trts.append(fa["trt"])
    msr = None
    if "interface" in fams:
        msr = {k: (hc.MSR[k][0], w) for k, w in (job.get("msr") or {k: v[1] for k, v in hc.MSR.items()}).items()}
    nrml.source_tree(hd / "source_lt.xml", levels, msr)
    gmm = {t: (job.get("gmm") or {}).get(t, J.GMM[t]) for t in trts}
    nrml.gmm_tree(hd / "gmm_lt.xml", gmm)

    trunc, poes = job.get("trunc", hc.TRUNC), job.get("poes", hc.POES)
    h = hashlib.sha1(ini("", trts, trunc, poes, job.get("ini")).encode())
    for f in [hd / "source_lt.xml", hd / "gmm_lt.xml", hd / "sites.csv", hd / "site_model.csv"] + sorted(
            (hd / "src").rglob("*.xml")):
        h.update(f.read_bytes())
    key = h.hexdigest()[:8]
    desc = f"psha_chile8 HAZ {name} {key}"
    (hd / "job.ini").write_text(ini(desc, trts, trunc, poes, job.get("ini")))
    old = json.loads((hd / "build.json").read_text()) if (hd / "build.json").exists() else {}
    cid = old.get("calc_id") if old.get("description") == desc else None
    nsrc = int(np.prod([len(x) for x in levels])) * (len(msr) if msr else 1)
    nr = nsrc * int(np.prod([len(v) for v in gmm.values()]))
    info = {"name": name, "description": desc, "calc_id": cid, "run_time_s": old.get("run_time_s") if cid else None,
            "families": fams, "trts": trts, "sources": {f: job[f] for f in fams}, "msr": msr, "gmm": gmm,
            "trunc": trunc, "site_names": names, "n_sites": len(xy), "poes": poes, "n_source_paths": nsrc, "n_realizations": nr}
    (hd / "build.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"{name}: {nsrc} source paths, {nr} realizations" + (f", unchanged (calc {cid})" if cid else ""))
    return info


def main(names=None):
    names = names or BUILD or J.RUN
    return {n: one(n, J.JOBS[n]) for n in names}


if __name__ == "__main__":
    main()
