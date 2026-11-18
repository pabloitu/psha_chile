# HAZ jobs on the family manifests (DECISIONS, Logic tree, 18 Nov): final trees from tree.json, tornado rows from
# tornado.json, GMM rows and truncation, check_tree jobs.
# JOBS[name] = {family: {branch id: weight}, "msr": {id: weight} (interface scaling, default the tree's), "gmm":
# {trt: [(gsim, weight)]} (default GMM-FIT), "trunc": level, "sites": "grid", "poes": [...], "part": weight}.
# ROWS[name] = (family, axis, row label, base job): base None is the family reference.

import json

import pandas as pd

from hazard import config as hc

IF, IS, CR = "Subduction Interface", "Subduction IntraSlab", "Active Shallow Crust"
FAM = {"interface": ("if", IF), "inslab": ("is", IS), "crustal": ("cr", CR)}

# GMM sets (DECISIONS, GMMs): the fitted set A is the model and the tornado reference; B, C, D are comparisons
SET_NAME = {"A": "GMM-FIT", "B": "GMM-1R", "C": "GMM-CSN", "D": "GMM-GEM"}
SET_KEY = {"A": "gm1top4", "B": "current", "C": "mascsn26", "D": "gem_sam"}
SETS_CSV = hc.ROOT / "gmm" / "tables" / "gmm_sets_2026-11-15.csv"


def gmm_sets():
    d = pd.read_csv(SETS_CSV)
    trt = {f: t for f, (_, t) in FAM.items()}
    return {s: {trt[c]: [(x.gsim.replace("; ", "\n"), float(x.weight)) for x in h.itertuples()]
                for c, h in g.groupby("cls")} for s, g in d.groupby("set")}


def manifests(fam):
    """tree.json and tornado.json of the family folder (CURRENT.md)."""
    d = hc.FAMILIES[fam]["dir"]
    return json.loads((d / "tree.json").read_text()), json.loads((d / "tornado.json").read_text())


def tree(fam):
    t = manifests(fam)[0]
    return {x["id"]: x["weight"] for x in t.get("branches") or t["paths"]}


SETS = gmm_sets()
GMM = SETS["A"]
TREE_MSR = {m["id"]: m["weight"] for m in manifests("interface")[0]["msr"]}
assert set(TREE_MSR) == set(hc.MSR)

# final trees: cities (475 and 2475 yr) and the 0.05° grid
JOBS = {}
for f, (s, _) in FAM.items():
    j = {f: tree(f), "poes": hc.POES_FINAL}
    if f == "interface":
        j["msr"] = TREE_MSR
    JOBS[f"f_{s}_tree"] = j
    JOBS[f"g_{s}_tree"] = {**j, "sites": "grid"}
# grid interface: Mmin 6.0 and MFD bins of 0.2 (speed test on 200 grid sites: within 1.4 % at 95 % of the sites at
# 475 yr, 0.8 % at 2475 yr; up to 5 % lower in Patagonia; hazard/speed.py, Pablo, 18 Nov)
JOBS["g_if_tree"] |= {"ini": {"minimum_magnitude": f'{{"{IF}": 6.0}}'}, "rebin": {"interface": 2}}
TREE_PARTS = {}

# tornado rows: axis and label per family level (labels of the 16 Nov tornado and verdicts)
AXIS = {
    "inslab": {"ab": "(a, b) uncertainty", "pattern": "spatial pattern", "shape": "MFD shape", "mmax_pad": "Mmax pad",
               "rate": "declustering", "layers": "layers", "lower_depth": "lower depth", "msr": "rupture scaling"},
    "crustal": {"aseismic coefficient psi": "aseismic coefficient ψ", "fault database, single-fault": "fault database",
                "class Mmax pad, segmented": "class Mmax pad, single-fault",
                "single-fault Mmax pad": "fault Mmax pad, single-fault"},
}
LABEL = {"cut at Mmax": "truncated", "trunc": "truncated", "p05": "5th", "p95": "95th", "gk_family": "GK74",
         "nn_family": "NN", "Gardner–Knopoff": "GK74", "nearest neighbour": "NN", "Grünthal windows": "Grünthal",
         "Uhrhammer windows": "Uhrhammer", "AllenHayesIntraslab": "Allen–Hayes", "GK": "GK74", "B": "CSN",
         "B-mm": "CSN-Ṁ₀", "segmented": "single-fault", "main + NE secondary": "linked", "no faults": "no"}
ROWS = {}
REF = {}
for f, (s, _) in FAM.items():
    rows = manifests(f)[1]["rows"]
    name = {x["id"]: f"t_{s}_{x['id'].removeprefix(s + '_')}" for x in rows}
    for x in rows:
        if x["id"] in ("ref", "is_ref"):
            name[x["id"]] = f"t_{s}_ref"
        if x["id"] == "reference":
            name[x["id"]] = "t_cr_ref"
    for x in rows:
        n = name[x["id"]]
        if f == "crustal":
            b = x["branches"]
            j = {f: {x["id"]: 1.0} if len(b) == 1 else {f"{x['id']}_{y['id']}": y["weight"] for y in b}}
        else:
            j = {f: x["branches"]}
        if "msr" in x:
            j["msr"] = x["msr"]
        JOBS[n] = j
        if x["against"] is None:
            continue
        v = x["value"]
        lab = LABEL.get(v, f"+{v:g}" if "pad" in x["level"] and isinstance(v, float) else
                    f"{v:g} km" if "jump" in x["level"] else str(v))
        base = None if name[x["against"]] == f"t_{s}_ref" else name[x["against"]]
        ROWS[n] = (f, AXIS.get(f, {}).get(x["level"], x["level"]), lab, base)
    REF[f] = f"t_{s}_ref"
# in-slab declustered rates on GK74 sit on the GK74 pattern: measured against it (16 Nov rule, Hazard runs)
ROWS["t_is_rate_gk"] = (*ROWS["t_is_rate_gk"][:3], "t_is_decl_gk")

# GMM rows per family on the source reference: the other sets and truncation. The single models of GMM-FIT need no
# jobs: each model's curve is in the realizations of the reference job (LEARNINGS, S5a)
GMM_ROWS = []
for f, (s, trt) in FAM.items():
    ref = JOBS[REF[f]]
    for st, kk in SET_KEY.items():
        if st == "A" or SETS[st][trt] == GMM[trt]:
            continue
        n = f"t_{s}_set_{kk}"
        JOBS[n] = {**ref, "gmm": {trt: SETS[st][trt]}}
        ROWS[n] = (f, "GMM set", SET_NAME[st], None)
        GMM_ROWS.append(n)
    for k, tr in (("trunc25", 2.5), ("trunc40", 4.0)):
        n = f"t_{s}_{k}"
        JOBS[n] = {**ref, "trunc": tr}
        ROWS[n] = (f, "GMM truncation", f"{tr:g}σ", None)
        GMM_ROWS.append(n)

# check_tree level 1: a small joint job and its two family jobs (two branches each)
IF_S = {"margin_full_own_taper_ml_seis": 0.5, "seg_full_own_taper_ml_geo08": 0.5}
IS_S = {"nn_taper_ml_l3": 0.5, "nn_taper_ml_l3_ratenn": 0.5}
JOBS["c_all_small"] = {"interface": IF_S, "inslab": IS_S}
JOBS["c_if_small"] = {"interface": IF_S}
JOBS["c_is_small"] = {"inslab": IS_S}

# remote check (hazard/remote.sh): the in-slab reference under its own name, compared with t_is_ref
JOBS["r_is_ref"] = dict(JOBS["t_is_ref"])

# run order: references, base rows, rows, GMM rows, check jobs, city trees; the grid trees apart (GRID_RUN)
REFS = list(REF.values())
BASES = sorted({b for *_, b in ROWS.values() if b} - set(REFS) - set(ROWS))
TORNADO = REFS + BASES + [n for n in ROWS if n not in GMM_ROWS] + GMM_ROWS
CHECK = ["c_if_small", "c_is_small", "c_all_small"]
TREES = ["f_if_tree", "f_is_tree", "f_cr_tree"]
RUN = TORNADO + CHECK + TREES
GRID_RUN = ["g_if_tree", "g_is_tree", "g_cr_tree"]
