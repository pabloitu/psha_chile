# Parameter variants per model: name -> config overrides.
# Dict parameters are merged into the config value, so only the changed
# keys are listed (e.g. one segment of MMAX).

import json

import paths


def _mc(model, end):
    """Completeness table picked by check_completeness.py (reference table if not run yet)."""
    p = paths.OUT / "completeness" / f"{model}.json"
    return json.loads(p.read_text())[end] if p.exists() else None


INTERFACE = {
    "ref": {},
    "zbot40": {"Z_BOTTOM": 40.0},
    "zbot60": {"Z_BOTTOM": 60.0},
    "ztop10": {"Z_TOP": 10.0},
    "dc_gk74sym": {"DC_METHOD": "gk74_sym"},
    "dc_gruenthal": {"DC_METHOD": "gruenthal"},
    "dc_uhrhammer": {"DC_METHOD": "uhrhammer"},
    "fit54": {"MMIN_FIT": 5.4},
    "fit60": {"MMIN_FIT": 6.0},
    "seg2_90": {"MMAX": {"seg2": 9.0}},
    "seg2_93": {"MMAX": {"seg2": 9.3}},
    "mmin55": {"MMIN_HAZ": 5.5},
    "mmin60": {"MMIN_HAZ": 6.0},
    "mu33": {"MU": 33.0e9},
    "m0c91": {"M0_C": 9.1},
    "keep_1962_1998": {"DC_KEEP_IDS": [1009, 28776]},
    "msr_ah": {"MSR": "AllenHayesInterfaceBilinear"},
    "raw": {"DC_METHOD": "none", "DC_METHODS": ["gk74", "none"]},
    "asp15": {"ASPECT": 1.5},
    "asp20": {"ASPECT": 2.0},
    "asp30": {"ASPECT": 3.0},
    "cls_m5": {"CAT_VARIANT": "tol_m5"},
    "cls_p5": {"CAT_VARIANT": "tol_p5"},
    "cls_fix": {"CAT_VARIANT": "fixdep_if"},
    "mc_lo": {"COMPLETENESS": _mc("interface", "lo")},
    "mc_hi": {"COMPLETENESS": _mc("interface", "hi")},
}

INTRASLAB = {
    "ref": {},
    "dc_gk74sym": {"DC_METHOD": "gk74_sym"},
    "dc_gruenthal": {"DC_METHOD": "gruenthal"},
    "dc_uhrhammer": {"DC_METHOD": "uhrhammer"},
    "mask50": {"MASK_ZTOP": 50.0},
    "mask60": {"MASK_ZTOP": 60.0},
    # classes smoothed only where the classifier can put them: Slab2 top < 50 km
    # -> intra_slab, >= 50 km -> slab_deep (SUBDUCTION_CLASSIFY_MAX_SLAB_DEPTH)
    "classmask": {"MASK_BY_CLASS": {"intra_slab": (None, 50.0), "slab_deep": (50.0, None)}},
    # previous reference geometry: band by depth rule, hypocentre top + 7.5
    "band_rule": {"BAND": "rule", "HYPO": "offset"},
    # catalog depths in km by slab-top regime instead of thickness fractions
    "regime": {"CATALOG_DEPTH": "regime"},
    "pad0": {"MMAX_PAD": 0.0},
    # slab_deep and intra_slab b through their own fit floors (ref 5.8 / 5.6)
    "sd_fit57": {"MMIN_FIT_BY_CLASS": {"slab_deep": 5.7}},
    "sd_fit60": {"MMIN_FIT_BY_CLASS": {"slab_deep": 6.0}},
    "is_fit55": {"MMIN_FIT_BY_CLASS": {"intra_slab": 5.5}},
    "is_fit58": {"MMIN_FIT_BY_CLASS": {"intra_slab": 5.8}},
    "pad04": {"MMAX_PAD": 0.4, "MMAX_SANITY": 8.5},
    "nn10": {"N_NEIGHBORS": 10},
    "nn50": {"N_NEIGHBORS": 50},
    "no_deep_nest": {"CLASSES": ["intra_slab", "slab_deep"]},
    # spatial pattern of the smoothing
    "smooth_all": {"SMOOTH_EVENTS": "complete"},
    "smooth_cv": {"SMOOTH_EVENTS": "complete", "KERNEL_CV": True},
    "gauss": {"KERNEL": "gauss"},
    "dmax200": {"MAX_DIST_KM": 200.0},
    "msr_ah": {"MSR": "AllenHayesIntraslab"},
    "dip45": {"NPD": [(0.5, 0.0, 45.0, 90.0), (0.5, 180.0, 45.0, 90.0)]},
    "dip90": {"NPD": [(0.5, 0.0, 90.0, 90.0), (0.5, 180.0, 90.0, 90.0)]},
    "mmin55": {"MMIN": 5.5},
    "raw": {"DC_METHOD": "none", "DC_METHODS": ["gk74", "none"]},
    "asp20": {"ASPECT": 2.0},
    "cls_m5": {"CAT_VARIANT": "tol_m5"},
    "cls_p5": {"CAT_VARIANT": "tol_p5"},
    "cls_fix": {"CAT_VARIANT": "fixdep_if"},
    "mc_lo": {"COMPLETENESS": _mc("intraslab", "lo")},
    "mc_hi": {"COMPLETENESS": _mc("intraslab", "hi")},
}

CRUSTAL = {
    "ref": {},
    "dc_gk74sym": {"DC_METHOD": "gk74_sym"},
    "dc_gruenthal": {"DC_METHOD": "gruenthal"},
    "margin0": {"BUFFER_MARGIN_KM": 0.0},
    "margin20": {"BUFFER_MARGIN_KM": 20.0},
    "cap65": {"CAP_MAG": 6.5, "FAULT_MMIN": 6.5},
    "m0_center": {"M0_AT_EDGE": False},
    "no_orient": {"ORIENT_BY_DIP_DIR": False},
    "mmax75": {"MMAX_OVERRIDE": {"forearc": 7.5, "intraarc": 7.5, "unclassified": 7.5}},
    "patagonia_box": {"CLASSES": {"forearc": None, "intraarc": None, "unclassified": (-76.0, -64.0, -56.0, -47.0)}},
    "raw": {"DC_METHOD": "none", "DC_METHODS": ["gk74", "none"]},
    "cls_m5": {"CAT_VARIANT": "tol_m5"},
    "cls_p5": {"CAT_VARIANT": "tol_p5"},
    "cls_fix": {"CAT_VARIANT": "fixdep_if"},
}

# interface campaign variants on top of the hazard base (MMIN_HAZ 5.5): c_<variant>
for k in ("zbot40", "zbot60", "ztop10", "dc_gk74sym", "dc_gruenthal", "fit54", "fit60", "keep_1962_1998", "msr_ah", "raw", "asp15", "asp20", "asp30", "cls_m5", "cls_p5", "cls_fix", "mc_lo", "mc_hi"):
    INTERFACE[f"c_{k}"] = {**INTERFACE["mmin55"], **INTERFACE[k]}

for _v in (INTERFACE, INTRASLAB):
    for _k in ("mc_lo", "mc_hi", "c_mc_lo", "c_mc_hi"):
        if _k in _v and "COMPLETENESS" in _v[_k] and _v[_k]["COMPLETENESS"] is None:
            del _v[_k]["COMPLETENESS"]
VARIANTS = {"interface": INTERFACE, "intraslab": INTRASLAB, "crustal": CRUSTAL}