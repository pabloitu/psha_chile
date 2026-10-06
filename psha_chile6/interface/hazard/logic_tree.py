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
#   crustal:   {phi050|phi075|phi100}__{mobs|mgeo}__{tgr|tap|al1|al2|al3|yc}, reference, nofaults
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
        "mmax_m02": ("c_mmax_m02", 1.0, ["seg__seis__tapered"]), "mmax_p02": ("c_mmax_p02", 1.0, ["seg__seis__tapered"]),
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
    ("interface", "segment Mmax -0.2 / +0.2", ["mmax_m02", "mmax_p02"]),
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
STAGES = [f"c_{s}_{r}" for r in ("stage_camp", "stage_conv") for s in ("if", "is", "cr")]
TIER1 = ["c_if_rate_gk74", "c_is_rate_gk74", "c_if_ab_p16", "c_if_ab_p84", "c_if_geo", "c_if_seg",
         "c_is_smooth_window_T", "c_is_smooth_complete", "c_is_pattern_none", "c_if_ztop5"]
TIER2 = ["c_is_classmask", "c_if_mmax_m02", "c_if_mmax_p02", "c_is_b_separate", "c_cr_rate_gk74"]
GMM_SINGLE = [f"c_{s}_gmm_{k}" for s, ks in (("if", ("ag", "pk", "ku")), ("is", ("ag", "pk", "mv")),
                                              ("cr", ("ask", "bssa", "cb", "cy"))) for k in ks]
# run order: references, the tornado (tier 1, then 2), single GMMs, the stage curves;
# the disaggregation job ("disagg") is slow and is added only when needed
BUILD = REFS + TIER1 + TIER2 + GMM_SINGLE + STAGES
