# S5a jobs (tasks/S5a_assembly_if_is.md): references, family trees, tornado rows, check_tree jobs.
# JOBS[name] = {family: {branch id of branches.json: weight}, "msr": {id: weight} (interface scaling, default the
# three at 1/3), "gmm": {trt: [(gsim, weight)]} (default GMM), "trunc": level, "skip": reason}.
# ROWS[name] = (family, axis, row label, base job): base None is the family reference.

import json

import pandas as pd

from hazard import config as hc

IF, IS, CR = "Subduction Interface", "Subduction IntraSlab", "Active Shallow Crust"

# current GMM tree (DECISIONS, GMMs): AG20, Parker SA_S, Kuehn, Montalva, 0.25 each
GMM = {
    IF: [('[AbrahamsonGulerce2020SInter]\nregion = "SAM"', 0.25),
         ('[ParkerEtAl2020SInter]\nregion = "SA"\nsaturation_region = "SA_S"', 0.25),
         ('[KuehnEtAl2020SInter]\nregion = "SAM"', 0.25), ("[MontalvaEtAl2017SInter]", 0.25)],
    IS: [('[AbrahamsonGulerce2020SSlab]\nregion = "SAM"', 0.25),
         ('[ParkerEtAl2020SSlab]\nregion = "SA"\nsaturation_region = "SA_S"', 0.25),
         ('[KuehnEtAl2020SSlab]\nregion = "SAM"', 0.25), ("[MontalvaEtAl2017SSlab]", 0.25)],
    CR: [("[AbrahamsonEtAl2014]", 0.25), ("[BooreEtAl2014]", 0.25), ("[CampbellBozorgnia2014]", 0.25),
         ("[ChiouYoungs2014]", 0.25)],
}
GMM_KEY = ["ag20", "parker", "kuehn", "montalva"]
GMM_NAME = {"ag20": "AG20", "parker": "Parker", "kuehn": "Kuehn", "montalva": "Montalva", "ask14": "ASK14", "bssa14": "BSSA14", "cb14": "CB14", "cy14": "CY14"}

# the four GMM sets of DECISIONS (E17) as wholes; B is the current tree (GMM-1R, the reference: no row)
SET_NAME = {"A": "GMM-FIT", "B": "GMM-1R", "C": "GMM-CSN", "D": "GMM-GEM"}
SETS_CSV = hc.ROOT / "gmm" / "tables" / "gmm_sets_2026-11-15.csv"
SET_KEY = {"A": "gm1top4", "B": "current", "C": "mascsn26", "D": "gem_sam"}


def gmm_sets():
    d = pd.read_csv(SETS_CSV)
    trt = {"interface": IF, "inslab": IS, "crustal": CR}
    out = {}
    for s, g in d.groupby("set"):
        out[s] = {trt[c]: [(x.gsim.replace("; ", "\n"), float(x.weight)) for x in h.itertuples()]
                  for c, h in g.groupby("cls")}
    return out


def tree(fam):
    """Every branch of the family tree with its weight in branches.json (weight > 0)."""
    d = json.loads((hc.FAMILIES[fam]["dir"] / "branches.json").read_text())
    return {x["id"]: x["weight"] for x in d["tree" if fam == "crustal" else "branches"] if x["weight"] > 0}


# references
IF_REF = "margin_full_own_taper_ml_seis"
IS_REF = "gk_taper_ml_l3"
JOBS = {"t_if_ref": {"interface": {IF_REF: 1.0}}, "t_is_ref": {"inslab": {IS_REF: 1.0}}}

# family trees
JOBS["f_if_tree"] = {"interface": tree("interface")}
JOBS["f_is_tree"] = {"inslab": tree("inslab")}

# tornado rows: interface
ROWS = {}
IF_ROWS = {
    "seg": ("segmentation", "four segments", "seg_full_own_taper_ml_seis", None),
    "geo08": ("rate model", "geodetic χ 0.8", "margin_full_own_taper_ml_geo08", None),
    "geo07": ("geodetic coupling χ", "0.7", "margin_full_own_taper_ml_geo07", "t_if_geo08"),
    "geo09": ("geodetic coupling χ", "0.9", "margin_full_own_taper_ml_geo09", "t_if_geo08"),
    "ab_p05": ("(a, b) uncertainty", "5th", "margin_full_own_taper_p05_seis", None),
    "ab_p95": ("(a, b) uncertainty", "95th", "margin_full_own_taper_p95_seis", None),
    "b_shared": ("b per segment", "shared b", "seg_full_shared_taper_ml_seis", "t_if_seg"),
    "b_margin": ("b per segment", "whole-margin b", "seg_full_margin_taper_ml_seis", "t_if_seg"),
    "cut": ("MFD shape", "truncated", "margin_full_own_trunc_ml_seis", None),
    "decl_gk": ("declustering", "GK74", "margin_gk_family_own_taper_ml_seis", None),
    "decl_nn": ("declustering", "NN", "margin_nn_family_own_taper_ml_seis", None),
}
for k, (ax, lab, b, base) in IF_ROWS.items():
    JOBS[f"t_if_{k}"] = {"interface": {b: 1.0}}
    ROWS[f"t_if_{k}"] = ("interface", ax, lab, base)
# Mmax pad (S1, nrml_2026-11-16c): margin and segments at 0.5 each, against that mixture at pad 0.2
IF_PAD = {"pad00": "mmax_pad00", "pad04": "mmax_pad04"}
JOBS["t_if_pad02"] = {"interface": {"mmax_pad02_margin": 0.5, "mmax_pad02_seg": 0.5}}
for k, row in IF_PAD.items():
    JOBS[f"t_if_{k}"] = {"interface": {f"{row}_margin": 0.5, f"{row}_seg": 0.5}}
    ROWS[f"t_if_{k}"] = ("interface", "Mmax pad", f"+{int(k[3:]) / 10:g}", "t_if_pad02")
for k, (m, _) in hc.MSR.items():
    n = f"t_if_{k}"
    JOBS[n] = {"interface": {IF_REF: 1.0}, "msr": {k: 1.0}}
    ROWS[n] = ("interface", "rupture scaling", {"msr_strasser": "Strasser", "msr_thingbaijam": "Thingbaijam",
                                                "msr_allenhayes": "Allen–Hayes"}[k], None)

# tornado rows: in-slab (S2, nrml/2026-11-16c; one layer and lower depth from C15)
IS_ROWS = {
    "ab_p05": ("(a, b) uncertainty", "5th", "gk_taper_p05_l3"),
    "ab_p95": ("(a, b) uncertainty", "95th", "gk_taper_p95_l3"),
    "pattern_nn": ("spatial pattern", "NN", "nn_taper_ml_l3"),
    "cut": ("MFD shape", "truncated", "gk_trunc_ml_l3"),
    "pad00": ("Mmax pad", "+0", "is_mmax_pad00"),
    "pad04": ("Mmax pad", "+0.4", "is_mmax_pad04"),
    "one_layer": ("layers", "one", "is_l1c15"),
    "lower_depth": ("lower depth", "0.65", "is_lsd065"),
    "msr_ah": ("rupture scaling", "Allen–Hayes", "is_ah"),
    "decl_gk": ("declustering", "GK74", "is_rate_gk"),
    "decl_nn": ("declustering", "NN", "is_rate_nn"),
}
for k, (ax, lab, b) in IS_ROWS.items():
    JOBS[f"t_is_{k}"] = {"inslab": {b: 1.0}}
    ROWS[f"t_is_{k}"] = ("inslab", ax, lab, None)
# declustering of the rates alone: the NN-rates job also has the NN pattern, so it is measured against the NN pattern
ROWS["t_is_decl_nn"] = ("inslab", "declustering", "NN", "t_is_pattern_nn")

# GMM rows and truncation, per family
SETS = gmm_sets()
for fam, s, trt, ref in (("interface", "if", IF, IF_REF), ("inslab", "is", IS, IS_REF)):
    for k, g in zip(GMM_KEY, GMM[trt]):
        JOBS[f"t_{s}_gmm_{k}"] = {fam: {ref: 1.0}, "gmm": {trt: [(g[0], 1.0)]}}
        ROWS[f"t_{s}_gmm_{k}"] = (fam, "GMM-1R models", GMM_NAME[k], None)
    for st, kk in SET_KEY.items():
        if st == "B":
            continue
        JOBS[f"t_{s}_set_{kk}"] = {fam: {ref: 1.0}, "gmm": {trt: SETS[st][trt]}}
        ROWS[f"t_{s}_set_{kk}"] = (fam, "GMM set", SET_NAME[st], None)
    for k, tr in (("trunc25", 2.5), ("trunc40", 4.0)):
        JOBS[f"t_{s}_{k}"] = {fam: {ref: 1.0}, "trunc": tr}
        ROWS[f"t_{s}_{k}"] = (fam, "GMM truncation", f"{tr:g}σ", None)

# crustal family (S5b; S3 hand-off model/crustal/S5_HANDOFF.md): reference, the S3 rows, tree, GMM rows, truncation
CR_D = json.loads((hc.FAMILIES["crustal"]["dir"] / "branches.json").read_text())
JOBS["t_cr_ref"] = {"crustal": {"reference": 1.0}}
CR_AXIS = {"decl_nn": ("spatial pattern", "NN"), "fit_cut": ("background MFD", "truncated"),
           "rates_declustered": ("background rates", "declustered"), "no_faults": ("with faults", "no"),
           "segmented": ("fault linkage", "single-fault"), "psi060": ("aseismic coefficient ψ", "0.6"),
           "psi100": ("aseismic coefficient ψ", "1.0"), "thickness20": ("seismogenic thickness", "20 km"),
           "jump5": ("max. jump distance", "5 km"), "jump10": ("max. jump distance", "10 km"),
           "splays": ("LOFS secondary traces", "linked"), "db_B": ("fault database", "CSN"),
           "db_Bmm": ("fault database", r"CSN-$\dot{M}_0$"),
           "mmax_pad00_mf": ("class Mmax pad, multi-fault", "+0"), "mmax_pad04_mf": ("class Mmax pad, multi-fault", "+0.4"),
           "mmax_pad00_seg": ("class Mmax pad, single-fault", "+0"),
           "mmax_pad04_seg": ("class Mmax pad, single-fault", "+0.4"),
           "fault_pad02_seg": ("fault Mmax pad, single-fault", "+0.2"),
           "fault_pad04_seg": ("fault Mmax pad, single-fault", "+0.4")}
CR_ROWS = []
for row, r in CR_D["tornado"].items():
    if row == "reference":
        continue
    n = f"t_cr_{row}"
    br = r["branches"]
    JOBS[n] = {"crustal": {row: 1.0} if len(br) == 1 else {f"{row}_{x['id']}": x["weight"] for x in br}}
    # rows on the single-fault system are measured against the single-fault row
    ROWS[n] = ("crustal", *CR_AXIS.get(row, (row.replace("_", " "), r["label"])),
               "t_cr_segmented" if row.endswith("_seg") else None)
    CR_ROWS.append(n)
# the tree as one job (16g: section ids unique across databases and thicknesses)
JOBS["f_cr_tree"] = {"crustal": tree("crustal")}
TREE_PARTS = {}
CR_GMM = []
for k, g in zip(["ask14", "bssa14", "cb14", "cy14"], GMM[CR]):
    JOBS[f"t_cr_gmm_{k}"] = {"crustal": {"reference": 1.0}, "gmm": {CR: [(g[0], 1.0)]}}
    ROWS[f"t_cr_gmm_{k}"] = ("crustal", "GMM-1R models", GMM_NAME[k], None)
    CR_GMM.append(f"t_cr_gmm_{k}")
for st, kk in (("C", "mascsn26"), ("D", "gem_sam")):
    JOBS[f"t_cr_set_{kk}"] = {"crustal": {"reference": 1.0}, "gmm": {CR: SETS[st][CR]}}
    ROWS[f"t_cr_set_{kk}"] = ("crustal", "GMM set", SET_NAME[st], None)
    CR_GMM.append(f"t_cr_set_{kk}")
for k, tr in (("trunc25", 2.5), ("trunc40", 4.0)):
    JOBS[f"t_cr_{k}"] = {"crustal": {"reference": 1.0}, "trunc": tr}
    ROWS[f"t_cr_{k}"] = ("crustal", "GMM truncation", f"{tr:g}σ", None)
    CR_GMM.append(f"t_cr_{k}")

# check_tree level 1: a small joint job and its two family jobs (two branches each)
IF_S = {"margin_full_own_taper_ml_seis": 0.5, "seg_full_own_taper_ml_geo08": 0.5}
IS_S = {"gk_taper_ml_l3": 0.5, "nn_taper_ml_l3": 0.5}
JOBS["c_all_small"] = {"interface": IF_S, "inslab": IS_S}
JOBS["c_if_small"] = {"interface": IF_S}
JOBS["c_is_small"] = {"inslab": IS_S}

# run order: references, family trees, rows, check jobs
REFS = ["t_if_ref", "t_is_ref"]
TREES = ["f_if_tree", "f_is_tree"]
S5A = REFS + ["t_if_pad02"] + TREES + [n for n in ROWS if "skip" not in JOBS[n] and not n.startswith("t_cr_")] + [
    "c_if_small", "c_is_small", "c_all_small"]
# crustal (S3 note): reference, rows, tree, GMM rows and truncation
S5B = ["t_cr_ref"] + CR_ROWS + ["f_cr_tree"] + CR_GMM
RUN = S5A + S5B
