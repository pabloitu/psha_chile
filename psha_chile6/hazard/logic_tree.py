import os
# Hazard jobs of the sensitivity campaign. Each entry of JOBS is one OpenQuake
# job (folder <hazard config OUT_ROOT>/<job>/); BUILD lists the jobs
# hazard/build.py writes and hazard/run_all.sh runs.
#
# Source models: family -> list of (variant, weight) or (variant, weight, branches).
# Variant names come from variants.py. Families combine as a product.
#   no branches          all branches with non-zero weight in the model
#   ["a", "b"]           only those, model weights renormalized to 1
#   {"a": 0.6, "b": 0.4} only those, with these weights
# Branch ids
#   interface: {seg|full}__{seis|geo_lo|geo_mid|geo_hi}__{tgr|tapered}
#   intraslab: is, is_intra_slab, is_slab_deep, is_deep_nest
#   crustal:   {phi060|phi080|phi100}__{mobs|mwc|mleo}__{al1|al2|al3|yc|tap}, reference, nofaults
#
# Reference: interface from M5.5, single full-margin seismic TGR branch;
# in-slab summed classes; crustal fault branches; the GMM tree of each region.
# Every campaign row is one family-only job with the full GMM tree of its
# region, named c_<if|is|cr>_<row>; the other families stay at their
# reference. Families combine exactly afterwards (hazard/tornado.py): the tree
# is a product, so 1 - P_total = prod over families of (1 - P_family) for the
# mean curves. AXES groups rows into one tornado bar each.

IF_B = ["full__seis__tapered"]
IF_TGR = ["full__seis__tgr"]
IF1 = [("mmin55", 1.0, IF_B)]
IS1 = [("ref", 1.0)]
CR1 = [("ref", 1.0)]

GMM_FULL = {
    "Subduction Interface": [
        ("AbrahamsonGulerce2020SInter", 0.34, {"region": "SAM"}),
        ("ParkerEtAl2020SInter", 0.33, {"region": "SA", "saturation_region": "SA_S"}),
        ("KuehnEtAl2020SInter", 0.33, {"region": "SAM"}),
    ],
    "Subduction IntraSlab": [
        ("AbrahamsonGulerce2020SSlab", 0.34, {"region": "SAM"}),
        ("ParkerEtAl2020SSlab", 0.33, {"region": "SA", "saturation_region": "SA_S"}),
        ("MontalvaEtAl2017SSlab", 0.33, {}),
    ],
    "Active Shallow Crust": [
        ("AbrahamsonEtAl2014", 0.25, {}),
        ("BooreEtAl2014", 0.25, {}),
        ("CampbellBozorgnia2014", 0.25, {}),
        ("ChiouYoungs2014", 0.25, {}),
    ],
}
CAMP = {
    "interface": {
        "ref": ("mmin55", 1.0, IF_B),
        "zbot40": ("c_zbot40", 1.0, IF_B), "zbot60": ("c_zbot60", 1.0, IF_B),
        "ztop5": ("c_ztop5", 1.0, IF_B),
        "ab_p16": ("c_ab_p16", 1.0, IF_B), "ab_p84": ("c_ab_p84", 1.0, IF_B),
        "mmax_p02": ("c_mmax_p02", 1.0, ["seg__seis__tapered"]),
        "stage_camp": ("c_stage_camp", 1.0, IF_TGR), "stage_conv": ("c_stage_conv", 1.0, IF_TGR),
        "dc_gk74sym": ("c_dc_gk74sym", 1.0, IF_B), "dc_gruenthal": ("c_dc_gruenthal", 1.0, IF_B),
        "keep6298": ("c_keep_1962_1998", 1.0, IF_B),
        "fit54": ("c_fit54", 1.0, IF_B), "fit60": ("c_fit60", 1.0, IF_B),
        "mmin65": ("ref", 1.0, IF_B),
        "seg": ("mmin55", 1.0, ["seg__seis__tapered"]),
        "geo": ("mmin55", 1.0, ["full__geo_mid__tapered"]),
        "geo_lo": ("mmin55", 1.0, ["full__geo_lo__tapered"]), "geo_hi": ("mmin55", 1.0, ["full__geo_hi__tapered"]),
        "tree": ("mmin55", 1.0),
        "msr_ah": ("c_msr_ah", 1.0, IF_B),
        "rate_gk74": ("c_rate_gk74", 1.0, IF_B),
        "asp15": ("c_asp15", 1.0, IF_B), "asp20": ("c_asp20", 1.0, IF_B), "asp30": ("c_asp30", 1.0, IF_B),
        "cls_m5": ("c_cls_m5", 1.0, IF_B), "cls_p5": ("c_cls_p5", 1.0, IF_B), "cls_fix": ("c_cls_fix", 1.0, IF_B),
        "mc_lo": ("c_mc_lo", 1.0, IF_B), "mc_hi": ("c_mc_hi", 1.0, IF_B),
    },
    "intraslab": {
        "ref": ("ref", 1.0),
        "stage_camp": ("stage_camp", 1.0), "stage_conv": ("stage_conv", 1.0),
        "pattern_none": ("pattern_none", 1.0), "b_separate": ("b_separate", 1.0),
        "classmask": ("classmask", 1.0),
        "dc_gk74sym": ("dc_gk74sym", 1.0), "dc_gruenthal": ("dc_gruenthal", 1.0),
        "sd_fit57": ("sd_fit57", 1.0), "sd_fit60": ("sd_fit60", 1.0),
        "is_fit55": ("is_fit55", 1.0), "is_fit58": ("is_fit58", 1.0),
        "pad0": ("pad0", 1.0), "pad04": ("pad04", 1.0),
        "regime": ("regime", 1.0),
        "band_rule": ("band_rule", 1.0),
        "nn10": ("nn10", 1.0), "nn50": ("nn50", 1.0),
        "smooth_complete": ("smooth_complete", 1.0), "smooth_floor": ("smooth_floor", 1.0),
        "smooth_1970": ("smooth_1970", 1.0), "smooth_cv": ("smooth_cv", 1.0), "smooth_period": ("smooth_period", 1.0),
        "smooth_window_T": ("smooth_window_T", 1.0),
        "gauss": ("gauss", 1.0), "dmax200": ("dmax200", 1.0),
        "msr_ah": ("msr_ah", 1.0),
        "dip45": ("dip45", 1.0), "dip90": ("dip90", 1.0),
        "mmin55": ("mmin55", 1.0),
        "rate_gk74": ("rate_gk74", 1.0),
        "asp20": ("asp20", 1.0),
        "cls_m5": ("cls_m5", 1.0), "cls_p5": ("cls_p5", 1.0), "cls_fix": ("cls_fix", 1.0),
        "mc_lo": ("mc_lo", 1.0), "mc_hi": ("mc_hi", 1.0),
    },
    "crustal": {
        "ref": ("ref", 1.0),
        "stage_camp": ("stage_camp", 1.0), "stage_conv": ("stage_conv", 1.0),
        "nofaults": ("ref", 1.0, {"nofaults": 1.0}),
        "margin0": ("margin0", 1.0), "margin20": ("margin20", 1.0),
        "cap65": ("cap65", 1.0),
        "dc_gruenthal": ("dc_gruenthal", 1.0),
        "rate_gk74": ("rate_gk74", 1.0),
        "cls_m5": ("cls_m5", 1.0), "cls_p5": ("cls_p5", 1.0), "cls_fix": ("cls_fix", 1.0),
        "mmax75": ("mmax75", 1.0),
        "smooth_complete": ("smooth_complete", 1.0), "smooth_window_T": ("smooth_window_T", 1.0),
    },
}
# single GMM of one region, source model at "ref": rows gmm_<k>
CAMP_GMM = {
    "interface": {"ag": GMM_FULL["Subduction Interface"][0], "pk": GMM_FULL["Subduction Interface"][1],
                  "ku": GMM_FULL["Subduction Interface"][2]},
    "intraslab": {"ag": GMM_FULL["Subduction IntraSlab"][0], "pk": GMM_FULL["Subduction IntraSlab"][1],
                  "mv": GMM_FULL["Subduction IntraSlab"][2]},
    "crustal": {"ask": GMM_FULL["Active Shallow Crust"][0], "bssa": GMM_FULL["Active Shallow Crust"][1],
                "cb": GMM_FULL["Active Shallow Crust"][2], "cy": GMM_FULL["Active Shallow Crust"][3]},
}
# final tornado (hazard/tornado.py): forecast and source decisions on the final reference
AXES = [
    ("interface", "rates from the declustered catalog", ["rate_gk74"]),
    ("interface", "(a, b) 16th / 84th percentile", ["ab_p16", "ab_p84"]),
    ("interface", "rate: geodetic (mid coupling)", ["geo"]),
    ("interface", "geometry: segmented", ["seg"]),
    ("interface", "segment Mmax +0.2 (segmented geometry)", ["mmax_p02"]),
    ("interface", "Z_TOP 5 km", ["ztop5"]),
    ("interface", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_ku"]),
    ("intraslab", "rates from the declustered catalog", ["rate_gk74"]),
    ("intraslab", "pattern weights: completeness window / magnitude step", ["smooth_window_T", "smooth_complete"]),
    ("intraslab", "pattern from the full catalog", ["pattern_none"]),
    ("intraslab", "class domain cut at 50 km", ["classmask"]),
    ("intraslab", "separate b per class", ["b_separate"]),
    ("intraslab", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_mv"]),
    ("crustal", "rates from the declustered catalog", ["rate_gk74"]),
    ("crustal", "GMM (single vs tree)", ["gmm_ask", "gmm_bssa", "gmm_cb", "gmm_cy"]),
]
AXES_CAMP = [
    ("interface", "Z_BOTTOM 40 / 60 km", ["zbot40", "zbot60"]),
    ("interface", "Z_TOP 10 km", ["ztop10"]),
    ("interface", "declustering", ["dc_gk74sym", "dc_gruenthal"]),
    ("interface", "rates from the declustered catalog (gk74)", ["rate_gk74"]),
    ("interface", "classification tolerance -5 / +5 km", ["cls_m5", "cls_p5"]),
    ("interface", "default-depth events to interface", ["cls_fix"]),
    ("interface", "completeness table, ends of the ensemble", ["mc_lo", "mc_hi"]),
    ("interface", "keep 1962 / 1998 events", ["keep6298"]),
    ("interface", "b: fit floor 5.4 / 6.0", ["fit54", "fit60"]),
    ("interface", "MMIN_HAZ 6.5", ["mmin65"]),
    ("interface", "geometry: segmented", ["seg"]),
    ("interface", "rate: geodetic (mid)", ["geo"]),
    ("interface", "MFD: tapered", ["tapered"]),
    ("interface", "full 16-branch tree", ["tree"]),
    ("interface", "rupture scaling: Allen & Hayes", ["msr_ah"]),
    ("interface", "rupture aspect ratio 1.5 / 2 / 3", ["asp15", "asp20", "asp30"]),
    ("interface", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_ku"]),
    ("intraslab", "class domain cut at 50 km", ["classmask"]),
    ("intraslab", "declustering", ["dc_gk74sym", "dc_gruenthal"]),
    ("intraslab", "rates from the declustered catalog (gk74)", ["rate_gk74"]),
    ("intraslab", "classification tolerance -5 / +5 km", ["cls_m5", "cls_p5"]),
    ("intraslab", "default-depth events to interface", ["cls_fix"]),
    ("intraslab", "completeness table, ends of the ensemble", ["mc_lo", "mc_hi"]),
    ("intraslab", "slab_deep b: floor 5.7 / 6.0", ["sd_fit57", "sd_fit60"]),
    ("intraslab", "intra_slab b: floor 5.5 / 5.8", ["is_fit55", "is_fit58"]),
    ("intraslab", "Mmax pad 0 / 0.4", ["pad0", "pad04"]),
    ("intraslab", "depths by slab-top regime, not thickness fraction", ["regime"]),
    ("intraslab", "previous geometry: top + 7.5 km, depth-rule band", ["band_rule"]),
    ("intraslab", "smoothing neighbours 10 / 50", ["nn10", "nn50"]),
    ("intraslab", "pattern: weighted by step / equal weights since 1970 / since 1990",
     ["smooth_complete", "smooth_1970", "smooth_period", "smooth_window_T"]),
    ("intraslab", "calibrated kernel", ["smooth_cv"]),
    ("intraslab", "kernel gaussian / cut-off 200 km", ["gauss", "dmax200"]),
    ("intraslab", "rupture scaling: Allen & Hayes", ["msr_ah"]),
    ("intraslab", "rupture aspect ratio 2", ["asp20"]),
    ("intraslab", "rupture dip 45 / 90", ["dip45", "dip90"]),
    ("intraslab", "sources from M5.5", ["mmin55"]),
    ("intraslab", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_mv"]),
    ("crustal", "faults vs no faults", ["nofaults"]),
    ("crustal", "buffer margin 0 / 20 km", ["margin0", "margin20"]),
    ("crustal", "cap and fault Mmin 6.5", ["cap65"]),
    ("crustal", "declustering", ["dc_gruenthal"]),
    ("crustal", "rates from the declustered catalog (gk74)", ["rate_gk74"]),
    ("crustal", "classification tolerance -5 / +5 km", ["cls_m5", "cls_p5"]),
    ("crustal", "default-depth events to interface", ["cls_fix"]),
    ("crustal", "background Mmax 7.5", ["mmax75"]),
    ("crustal", "GMM (single vs tree)", ["gmm_ask", "gmm_bssa", "gmm_cb", "gmm_cy"]),
    ("all", "truncation 2.5 / 4.0", ["tr25", "tr40"]),
    ("all", "truncation 2.0", ["tr20"]),
    ("all", "numerics: mesh 5 km, point-source distance 100 km", ["num"]),
    ("all", "rates from the declustered catalog, all families", ["rate_gk74"]),
    ("all", "classification tolerance -5 / +5 km, all families", ["cls_m5", "cls_p5"]),
    ("all", "default-depth events to interface, all families", ["cls_fix"]),
]
CALC_ROWS = {"num": {"MESH": 5.0, "PS_DIST": 100.0}}
TRUNC_ROWS = {"tr20": 2.0, "tr25": 2.5, "tr40": 4.0}
SHORT = {"interface": "if", "intraslab": "is", "crustal": "cr"}
TRT = {"interface": "Subduction Interface", "intraslab": "Subduction IntraSlab", "crustal": "Active Shallow Crust"}
FAMS = ["intraslab", "interface", "crustal"]

JOBS = {}
for fam, rows in CAMP.items():
    for r, e in rows.items():
        JOBS[f"c_{SHORT[fam]}_{r}"] = {fam: [e], "gmm": GMM_FULL}
    for k, g in CAMP_GMM[fam].items():
        JOBS[f"c_{SHORT[fam]}_gmm_{k}"] = {fam: [rows["ref"]], "gmm": {TRT[fam]: [(g[0], 1.0, g[2])]}}
    for k, tr in TRUNC_ROWS.items():
        JOBS[f"c_{SHORT[fam]}_{k}"] = {fam: [rows["ref"]], "gmm": GMM_FULL, "trunc": tr}
    for k, calc in CALC_ROWS.items():
        JOBS[f"c_{SHORT[fam]}_{k}"] = {fam: [rows["ref"]], "gmm": GMM_FULL, "calc": calc}
# in-slab classes alone (reference and class-cut smoothing): per-domain curves and shares
for _k in ("intra_slab", "slab_deep", "deep_nest"):
    JOBS[f"c_is_{_k}"] = {"intraslab": [("ref", 1.0, {f"is_{_k}": 1.0})], "gmm": GMM_FULL}
    JOBS[f"c_is_cm_{_k}"] = {"intraslab": [("classmask", 1.0, {f"is_{_k}": 1.0})], "gmm": GMM_FULL}
# the full model, run as a disaggregation at every city (its curves are the
# reference hazard; hazard/disagg.py reads the exports)
JOBS["disagg"] = {"interface": IF1, "intraslab": IS1, "crustal": CR1, "gmm": GMM_FULL,
                  "disagg": {"max_sites": 10, "mag_bin": 0.25, "dist_bin": 20.0, "n_eps": 8,
                             "outputs": ["Mag_Dist_Eps", "TRT_Mag_Dist", "TRT_Mag_Dist_Eps"]}}

REFS = [f"c_{SHORT[f]}_ref" for f in FAMS]
ALL = REFS + [j for j in JOBS if j not in REFS and j != "disagg"] + ["disagg"]
SMOKE = REFS + ["c_is_band_rule", "c_if_seg", "c_cr_nofaults", "c_is_slab_deep", "disagg"]
SMOOTHING = ["c_is_smooth_complete", "c_is_smooth_floor", "c_is_smooth_1970", "c_is_smooth_cv", "c_is_gauss", "c_is_dmax200"]
RAW = ["c_if_rate_gk74", "c_is_rate_gk74", "c_cr_rate_gk74"]
ASPECT = ["c_if_asp15", "c_if_asp20", "c_if_asp30", "c_is_asp20"]
INPUTS = [f"c_{f}_{r}" for f in ("if", "is", "cr") for r in ("cls_m5", "cls_p5")] + \
    [f"c_{f}_{r}" for f in ("if", "is") for r in ("mc_lo", "mc_hi")]
FIXDEP = ["c_if_cls_fix", "c_is_cls_fix", "c_cr_cls_fix"]
S1_JOBS = ([f"c_is_{k}" for k in ("intra_slab", "slab_deep", "deep_nest")]
           + ["c_is_smooth_window_T", "c_is_smooth_complete"]
           + ["c_if_gmm_ag", "c_if_gmm_pk", "c_if_gmm_ku", "c_cr_smooth_window_T"] + RAW)
# final logic tree (30 Sep 2026 decisions, HANDOFF_logic_tree / TORNADO_final):
#   interface  geometry (full, seg) x rate (seismic; geodetic at coupling lo / mid / hi)
#              x rate convention (full catalog, gk74-declustered; 0.5 / 0.5)
#              x (a, b) at 5 / ML / 95 (Keefer and Bodily 0.185 / 0.63 / 0.185); tapered MFD,
#              historical segment Mmax, Z_TOP 10, Z_BOTTOM 50 fixed
#   in-slab    one source model (pooled b, Mmax observed + 0.2, declustered pattern)
#   crustal    fault branches of crustal/config.py (phi 0.6/0.8/1.0 x Mmax observed/WC94/Leonard x MFD AL-I/II/III, YC,
#              tapered: 45) with the capped background
#   GMM        GMM_FINAL: the NGA-Sub trio (South American terms, Parker SA_S) plus Montalva et al.
#              (2017) for both subduction regions, NGA-West2 for the crust; equal weights (0.25)
# Run with FINAL=1 (hazard/config.py); PRELIM=1 runs the same tree at PGA, 475 yr, all cities
GMM_FINAL = {
    "Subduction Interface": [
        ("AbrahamsonGulerce2020SInter", 0.25, {"region": "SAM"}),
        ("ParkerEtAl2020SInter", 0.25, {"region": "SA", "saturation_region": "SA_S"}),
        ("KuehnEtAl2020SInter", 0.25, {"region": "SAM"}),
        ("MontalvaEtAl2017SInter", 0.25, {}),
    ],
    "Subduction IntraSlab": [
        ("AbrahamsonGulerce2020SSlab", 0.25, {"region": "SAM"}),
        ("ParkerEtAl2020SSlab", 0.25, {"region": "SA", "saturation_region": "SA_S"}),
        ("KuehnEtAl2020SSlab", 0.25, {"region": "SAM"}),
        ("MontalvaEtAl2017SSlab", 0.25, {}),
    ],
    "Active Shallow Crust": GMM_FULL["Active Shallow Crust"],
}
# candidates checked and left out (hazard/gmm_final.py draws them dashed)
GMM_EXTRA = {
    "Subduction Interface": [("AbrahamsonEtAl2015SInter", {})],
    "Subduction IntraSlab": [("AbrahamsonEtAl2015SSlab", {})],
}
# interface source branches: geometry x rate; the (a, b) percentile is the variant
IF_TREE = {f"{g}__{r}__tapered": 0.5 * w for g in ("full", "seg")
           for r, w in (("seis", 0.5), ("geo_lo", 0.125), ("geo_mid", 0.25), ("geo_hi", 0.125))}
# rate convention: full catalog (Marzocchi and Taroni 2014) or gk74-declustered, equal weights;
# each with (a, b) at 5 / ML / 95 (Keefer and Bodily 0.185 / 0.63 / 0.185)
AB_W = (0.185, 0.63, 0.185)
IF_AB = ([(v, 0.5 * w, IF_TREE) for v, w in zip(("c_ab_p05", "mmin55", "c_ab_p95"), AB_W)]
         + [(v, 0.5 * w, IF_TREE) for v, w in zip(("c_ab_p05_gk74", "c_rate_gk74", "c_ab_p95_gk74"), AB_W)])
JOBS["c_if_final"] = {"interface": IF_AB, "gmm": GMM_FINAL}
JOBS["c_is_final"] = {"intraslab": [CAMP["intraslab"]["ref"]], "gmm": GMM_FINAL}
JOBS["c_cr_final"] = {"crustal": [CAMP["crustal"]["ref"]], "gmm": GMM_FINAL}
# the same crustal model without faults (background only, uncapped): the question of the paper
JOBS["c_cr_final_nofaults"] = {"crustal": [("ref", 1.0, {"nofaults": 1.0})], "gmm": GMM_FINAL}
# in-slab classes alone on the final GMM tree, for the per-class curves
for _k in ("intra_slab", "slab_deep", "deep_nest"):
    JOBS[f"c_is_final_{_k}"] = {"intraslab": [("ref", 1.0, {f"is_{_k}": 1.0})], "gmm": GMM_FINAL}
FINAL_JOBS = ["c_if_final", "c_is_final", "c_cr_final", "c_cr_final_nofaults"]
# every family in one sampled job: OpenQuake's own fractiles against hazard/combine.py
JOBS["c_all_final_sample"] = {"interface": IF_AB, "intraslab": [CAMP["intraslab"]["ref"]],
                              "crustal": [CAMP["crustal"]["ref"]], "gmm": GMM_FINAL, "samples": 2000}
# small trees, fully enumerated, to check that the family jobs recombine into the joint tree
# (hazard/check_tree.py): 2 interface x 1 in-slab x 2 crustal source paths x 4 x 4 x 4 GMM paths
IF_S = [("mmin55", 1.0, {"full__seis__tapered": 0.5, "seg__geo_mid__tapered": 0.5})]
CR_S = [("ref", 1.0, {"phi060__mobs__al2": 0.5, "phi100__mleo__tap": 0.5})]
JOBS["c_all_small"] = {"interface": IF_S, "intraslab": IS1, "crustal": CR_S, "gmm": GMM_FINAL}
JOBS["c_if_small"] = {"interface": IF_S, "gmm": GMM_FINAL}
JOBS["c_cr_small"] = {"crustal": CR_S, "gmm": GMM_FINAL}
SMALL_JOBS = ["c_all_small", "c_if_small", "c_cr_small"]
# level 2 of hazard/check_tree.py: the small trees, then the full-size family jobs and the sampled joint job
LEVEL2_JOBS = SMALL_JOBS + ["c_is_final", "c_if_final", "c_cr_final", "c_all_final_sample"]
PRELIM_JOBS = FINAL_JOBS + ["c_all_final_sample"] + SMALL_JOBS + [f"c_is_final_{k}" for k in ("intra_slab", "slab_deep", "deep_nest")]

STAGES = [f"c_{s}_{r}" for r in ("stage_camp", "stage_conv") for s in ("if", "is", "cr")]
TIER1 = ["c_if_rate_gk74", "c_is_rate_gk74", "c_if_ab_p16", "c_if_ab_p84", "c_if_geo", "c_if_seg",
         "c_is_smooth_window_T", "c_is_smooth_complete", "c_is_pattern_none", "c_if_ztop5"]
TIER2 = ["c_is_classmask", "c_if_mmax_p02", "c_is_b_separate", "c_cr_rate_gk74"]
GMM_SINGLE = [f"c_{s}_gmm_{k}" for s, ks in (("if", ("ag", "pk", "ku")), ("is", ("ag", "pk", "mv")),
                                              ("cr", ("ask", "bssa", "cb", "cy"))) for k in ks]
# run order: references, the tornado (tier 1, then 2), single GMMs, the stage curves;
# the disaggregation job ("disagg") is slow and is added only when needed
BUILD = REFS + TIER1 + TIER2 + GMM_SINGLE + STAGES

if os.environ.get("FINAL"):
    BUILD = FINAL_JOBS
# Final one-at-a-time sensitivity (TORNADO=1): one family job per row on the reference, the other
# families at their reference; combination in rate space (hazard/tornado_final.py). Reference:
# interface single branch (full margin, seismic rate, tapered, M L (a, b),
# full-catalog rates, Antarctic
# source on), in-slab reference, crustal fault tree (45 branches) with the capped background; GMM_FINAL.
# TORN[family][row] = (variant, weight, branches) as in CAMP; GMM rows below. AXES_T groups rows:
# (family, label, rows, set, paper label, base row). set A: fixed by a criterion (stated); B: collaborator
# figure only; C: paper figure. base: the row the effect is measured against (None = the reference).
IF_T = ["full__seis__tapered"]
TORN = {
    "interface": {
        "ref": ("mmin55", 1.0, IF_T),
        "seg": ("mmin55", 1.0, ["seg__seis__tapered"]),
        "geo": ("mmin55", 1.0, ["full__geo_mid__tapered"]),
        "geo_lo": ("mmin55", 1.0, ["full__geo_lo__tapered"]),
        "geo_hi": ("mmin55", 1.0, ["full__geo_hi__tapered"]),
        "ab_p05": ("c_ab_p05", 1.0, IF_T), "ab_p95": ("c_ab_p95", 1.0, IF_T),
        "tgr": ("mmin55", 1.0, ["full__seis__tgr"]),
        "corner_lo": ("c_corner_lo", 1.0, IF_T), "corner_hi": ("c_corner_hi", 1.0, IF_T),
        "mmax_p02": ("c_mmax_p02", 1.0, ["seg__seis__tapered"]),
        "mmax_area": ("c_mmax_area", 1.0, ["seg__seis__tapered"]),
        "ztop5": ("c_ztop5", 1.0, IF_T), "zbot60": ("c_zbot60", 1.0, IF_T),
        "msr_tmg": ("c_msr_tmg", 1.0, IF_T), "msr_ah": ("c_msr_ah", 1.0, IF_T),
        "asp20": ("c_asp20", 1.0, IF_T),
        "floor_m02": ("c_floor_m02", 1.0, IF_T), "floor_p02": ("c_floor_p02", 1.0, IF_T),
        "mc_m01": ("c_mc_m01", 1.0, IF_T), "mc_p01": ("c_mc_p01", 1.0, IF_T),
    },
    "intraslab": {
        "ref": ("ref", 1.0),
        "pad0": ("pad0", 1.0), "pad04": ("pad04", 1.0),
        "b_separate": ("b_separate", 1.0),
        "floor_m02": ("floor_m02", 1.0), "floor_p02": ("floor_p02", 1.0),
        "mc_m01": ("mc_m01", 1.0), "mc_p01": ("mc_p01", 1.0),
        "nn10": ("nn10", 1.0), "nn50": ("nn50", 1.0),
        "classmask": ("classmask", 1.0),
        "msr_ah": ("msr_ah", 1.0),
    },
    "crustal": {
        "ref": ("ref", 1.0),
        "nofaults": ("ref", 1.0, {"nofaults": 1.0}),
        "only_al1": ("only_al1", 1.0), "only_al2": ("only_al2", 1.0), "only_al3": ("only_al3", 1.0),
        "only_yc": ("only_yc", 1.0), "only_tap": ("only_tap", 1.0), "only_hyb": ("only_hyb", 1.0),
        "multi05": ("multi05", 1.0),
        "only_mobs": ("only_mobs", 1.0), "only_mwc": ("only_mwc", 1.0), "only_mleo": ("only_mleo", 1.0),
        "only_phi060": ("only_phi060", 1.0), "only_phi100": ("only_phi100", 1.0),
        "depth10": ("depth10", 1.0), "depth30": ("depth30", 1.0),
        "msr_leonard": ("msr_leonard", 1.0),
        "cap65": ("cap65", 1.0),
        "margin0": ("margin0", 1.0), "margin10": ("margin10", 1.0),
        "mmax75": ("mmax75", 1.0),
        "backarc_borrow": ("backarc_borrow", 1.0), "patagonia_own": ("patagonia_own", 1.0),
        "intraarc_floor50": ("intraarc_floor50", 1.0),
        "no_exclude": ("no_exclude", 1.0),
        "floor_m02": ("floor_m02", 1.0), "floor_p02": ("floor_p02", 1.0),
        "mc_m01": ("mc_m01", 1.0), "mc_p01": ("mc_p01", 1.0),
    },
}
AXES_T = [
    ("interface", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_ku", "gmm_mv"], "C", "GMM, interface", None),
    ("interface", "geometry: segmented", ["seg"], "C", "Interface segmentation", None),
    ("interface", "rate: geodetic (mid coupling)", ["geo"], "C", "Geodetic rate", None),
    ("interface", "coupling 0.7 / 0.9 (geodetic)", ["geo_lo", "geo_hi"], "C", "Coupling coefficient", "geo"),
    ("interface", "(a, b): 5th / 95th percentile", ["ab_p05", "ab_p95"], "C", "Recurrence parameters (a, b)", None),
    ("interface", "MFD: truncated", ["tgr"], "B", None, None),
    ("interface", "corner 9.1 / 10.1 (Bird & Kagan interval)", ["corner_lo", "corner_hi"], "A", None, None),
    ("interface", "segment Mmax +0.2 (segmented)", ["mmax_p02"], "C", "Interface Mmax", "seg"),
    ("interface", "segment Mmax from the area (segmented)", ["mmax_area"], "A", None, "seg"),
    ("interface", "Z_TOP 5 km", ["ztop5"], "A", None, None),
    ("interface", "Z_BOTTOM 60 km", ["zbot60"], "A", None, None),
    ("interface", "scaling: Thingbaijam / Allen & Hayes", ["msr_tmg", "msr_ah"], "B", None, None),
    ("interface", "aspect ratio 2", ["asp20"], "B", None, None),
    ("interface", "fit floor -0.2 / +0.2", ["floor_m02", "floor_p02"], "A", None, None),
    ("interface", "completeness -0.1 / +0.1", ["mc_m01", "mc_p01"], "A", None, None),
    ("intraslab", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_ku", "gmm_mv"], "C", "GMM, in-slab", None),
    ("intraslab", "Mmax pad 0 / 0.4", ["pad0", "pad04"], "C", "In-slab Mmax", None),
    ("intraslab", "separate b per class", ["b_separate"], "A", None, None),
    ("intraslab", "fit floors -0.2 / +0.2", ["floor_m02", "floor_p02"], "A", None, None),
    ("intraslab", "completeness -0.1 / +0.1", ["mc_m01", "mc_p01"], "A", None, None),
    ("intraslab", "kernel neighbours 10 / 50", ["nn10", "nn50"], "B", None, None),
    ("intraslab", "class domain cut at 50 km", ["classmask"], "B", None, None),
    ("intraslab", "scaling: Allen & Hayes", ["msr_ah"], "B", None, None),
    ("crustal", "GMM (single vs tree)", ["gmm_ask", "gmm_bssa", "gmm_cb", "gmm_cy"], "C", "GMM, crust", None),
    ("crustal", "faults vs no faults", ["nofaults"], "C", "Crustal faults removed", None),
    ("crustal", "fault MFD (single vs tree)", ["only_al1", "only_al2", "only_al3", "only_yc", "only_tap", "only_hyb"], "C", "Fault MFD shape", None),
    ("crustal", "multi-fault ruptures, f = 0.5", ["multi05"], "C", "Multi-fault ruptures", None),
    ("crustal", "fault Mmax (single vs tree)", ["only_mobs", "only_mwc", "only_mleo"], "C", "Fault Mmax", None),
    ("crustal", "aseismic coefficient 0.6 / 1.0 (single vs tree)", ["only_phi060", "only_phi100"], "C", "Fault aseismic coefficient", None),
    ("crustal", "fault seismogenic depth 10 / 30 km", ["depth10", "depth30"], "C", "Fault seismogenic depth", None),
    ("crustal", "fault scaling: Leonard 2014", ["msr_leonard"], "B", None, None),
    ("crustal", "fault and cap Mmin 6.5", ["cap65"], "B", None, None),
    ("crustal", "buffer margin 0 / 10 km", ["margin0", "margin10"], "B", None, None),
    ("crustal", "background Mmax 7.5", ["mmax75"], "B", None, None),
    ("crustal", "backarc b borrowed", ["backarc_borrow"], "A", None, None),
    ("crustal", "Patagonia b own", ["patagonia_own"], "A", None, None),
    ("crustal", "intra-arc fit floor 5.0", ["intraarc_floor50"], "A", None, None),
    ("crustal", "exclusions off", ["no_exclude"], "A", None, None),
    ("crustal", "fit floors -0.2 / +0.2", ["floor_m02", "floor_p02"], "A", None, None),
    ("crustal", "completeness -0.1 / +0.1", ["mc_m01", "mc_p01"], "A", None, None),
    ("all", "truncation 2.5 / 4.0", ["trunc25", "trunc40"], "A", None, None),
]
GMM_T = {"interface": {"ag": 0, "pk": 1, "ku": 2, "mv": 3}, "intraslab": {"ag": 0, "pk": 1, "ku": 2, "mv": 3},
         "crustal": {"ask": 0, "bssa": 1, "cb": 2, "cy": 3}}
TORNADO_JOBS = []
for fam, rows in TORN.items():
    for r, e in rows.items():
        JOBS[f"t_{SHORT[fam]}_{r}"] = {fam: [e], "gmm": GMM_FINAL}
        TORNADO_JOBS.append(f"t_{SHORT[fam]}_{r}")
    for k, i in GMM_T[fam].items():
        g = GMM_FINAL[TRT[fam]][i]
        JOBS[f"t_{SHORT[fam]}_gmm_{k}"] = {fam: [rows["ref"]], "gmm": {TRT[fam]: [(g[0], 1.0, g[2])]}}
        TORNADO_JOBS.append(f"t_{SHORT[fam]}_gmm_{k}")
    for r, tr in (("trunc25", 2.5), ("trunc40", 4.0)):
        JOBS[f"t_{SHORT[fam]}_{r}"] = {fam: [rows["ref"]], "gmm": GMM_FINAL, "trunc": tr}
        TORNADO_JOBS.append(f"t_{SHORT[fam]}_{r}")
# the references first, so the combination can start while the rows run
TORNADO_JOBS = [j for j in TORNADO_JOBS if j.endswith("_ref")] + [j for j in TORNADO_JOBS if not j.endswith("_ref")]

if os.environ.get("PRELIM"):
    BUILD = PRELIM_JOBS
    SMOKE = SMALL_JOBS + ["c_is_final"]
if os.environ.get("LEVEL2"):
    BUILD = LEVEL2_JOBS
if os.environ.get("TORNADO"):
    BUILD = TORNADO_JOBS
