# Parameter variants per model: name -> config overrides.
# Dict parameters are merged into the config value, so only the changed
# keys are listed (e.g. one segment of MMAX).

import json

import paths


def _mc(model, end):
    """Completeness table picked by check_completeness.py (reference table if not run yet)."""
    p = paths.OUT / "completeness" / f"{model}.json"
    return json.loads(p.read_text())[end] if p.exists() else None


def _shift(table, dm):
    """Completeness table with every step moved by dm (the years kept)."""
    return [(round(m + dm, 2), y) for m, y in table]


def _shift_all(tables, dm):
    return {k: _shift(v, dm) for k, v in tables.items()}


from interface import config as _ifc
from intraslab import config as _isc
from crustal import config as _crc

# stage curves (hazard/stages.py): the campaign's settings on the new catalog, and the
# rate convention with equal pattern weights on top of them; the reference is the rest
IF_CAMP = {"DC_METHOD": "gk74", "MMIN_FIT": 5.6, "MMIN_FIT_BY_SEG": {}, "Z_TOP": 5.0,
           "W_MFD": {"tgr": 1.0, "tapered": 0.0},
           "COMPLETENESS": [(8.3, 1513), (6.8, 1900), (6.0, 1950), (5.3, 1976), (5.2, 1986), (5.0, 1997),
                            (4.8, 2002), (4.4, 2013)]}
IS_CAMP = {"DC_METHOD": "gk74", "SMOOTH_EVENTS": "complete", "B_POOL": [], "B_SOURCE": {"deep_nest": "slab_deep"},
           "MMIN_FIT_BY_CLASS": {"slab_deep": 5.8, "intra_slab": 5.6},
           "COMPLETENESS": {"intra_slab": [(7.5, 1900), (5.1, 1970), (4.8, 1990), (4.7, 2010)],
                            "slab_deep": [(7.5, 1900), (6.5, 1950), (5.1, 1960), (4.7, 1990), (4.5, 2010)],
                            "deep_nest": [(7.5, 1900), (4.8, 1970), (4.7, 1990), (4.6, 2000)]}}
CR_OLD_MC = [(4.4, 2015), (4.7, 1990), (4.8, 1985), (5.0, 1980), (5.1, 1965)]
CR_CAMP = {"DC_METHOD": "gk74", "SMOOTH_EVENTS": "complete", "EXCLUDE": {},
           "CLASS_MAP": {"backarc": "unclassified", "patagonia_crustal": "unclassified"},
           "CLASSES": {"forearc": None, "intraarc": None, "unclassified": None},
           "MMIN_FIT_BY_CLASS": {}, "MMAX_OVERRIDE": {"forearc": 7.2, "intraarc": 7.2, "unclassified": 7.2},
           "COMPLETENESS": {"forearc": CR_OLD_MC, "intraarc": CR_OLD_MC, "unclassified": [(4.5, 1995)]}}

INTERFACE = {
    "ref": {},
    "stage_camp": IF_CAMP,
    "stage_conv": {**IF_CAMP, "DC_METHOD": "none"},
    "zbot40": {"Z_BOTTOM": 40.0},
    "zbot60": {"Z_BOTTOM": 60.0},
    "ztop5": {"Z_TOP": 5.0},
    "ab_p05": {"AB_PCT": 5},
    "ab_p95": {"AB_PCT": 95},
    "ab_p05_gk74": {"AB_PCT": 5, "DC_METHOD": "gk74"},
    "ab_p95_gk74": {"AB_PCT": 95, "DC_METHOD": "gk74"},
    "ab_p16": {"AB_PCT": 16},
    "ab_p84": {"AB_PCT": 84},
    "mmax_p02": {"MMAX": {"seg1_south": 9.7, "seg2": 9.3, "seg3": 8.7, "seg4_north": 9.0}},
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
    "rate_gk74": {"DC_METHOD": "gk74"},
    "asp15": {"ASPECT": 1.5},
    "asp20": {"ASPECT": 2.0},
    "asp30": {"ASPECT": 3.0},
    "cls_m5": {"CAT_VARIANT": "tol_m5"},
    "cls_p5": {"CAT_VARIANT": "tol_p5"},
    "cls_fix": {"CAT_VARIANT": "fixdep_if"},
    "mc_lo": {"COMPLETENESS": _mc("interface", "lo")},
    "mc_hi": {"COMPLETENESS": _mc("interface", "hi")},
    # final tornado (hazard/logic_tree.py TORN)
    "floor_m02": {"MMIN_FIT": 5.6, "MMIN_FIT_BY_SEG": {"seg2": 5.8}},
    "floor_p02": {"MMIN_FIT": 6.0, "MMIN_FIT_BY_SEG": {"seg2": 6.2}},
    "mc_m01": {"COMPLETENESS": _shift(_ifc.COMPLETENESS, -0.1)},
    "mc_p01": {"COMPLETENESS": _shift(_ifc.COMPLETENESS, 0.1)},
    # Mmax = larger of the historical value and the area-based one (Thingbaijam et al. 2017, s04
    # closure.csv: 8.8 / 8.6 / 8.7 / 8.9, full margin 9.4): raises seg3 and seg4_north
    "mmax_area": {"MMAX": {"seg3": 8.7, "seg4_north": 8.9}},
    "corner_lo": {"CORNER": 9.1},
    "corner_hi": {"CORNER": 10.1},
    "msr_tmg": {"MSR": "ThingbaijamInterface"},
}

INTRASLAB = {
    "ref": {},
    "stage_camp": IS_CAMP,
    "stage_conv": {**IS_CAMP, "DC_METHOD": "none", "SMOOTH_EVENTS": "all"},
    "dc_gk74sym": {"DC_METHOD": "gk74_sym"},
    "dc_gruenthal": {"DC_METHOD": "gruenthal"},
    "dc_uhrhammer": {"DC_METHOD": "uhrhammer"},
    "mask50": {"MASK_ZTOP": 50.0},
    "mask60": {"MASK_ZTOP": 60.0},
    # classes smoothed only where the classifier can put them: Slab2 top < 50 km
    # -> intra_slab, >= 50 km -> slab_deep (SUBDUCTION_CLASSIFY_MAX_SLAB_DEPTH)
    "classmask": {"MASK_BY_CLASS": {"intra_slab": (None, 50.0), "slab_deep": (50.0, None)}},
    "pattern_none": {"PATTERN_DC": "none"},
    "b_separate": {"B_POOL": []},
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
    "smooth_complete": {"SMOOTH_EVENTS": "complete"},
    "smooth_floor": {"SMOOTH_EVENTS": "floor"},
    "smooth_period": {"SMOOTH_EVENTS": "period"},
    "smooth_window": {"SMOOTH_EVENTS": "window"},
    "smooth_window_T": {"SMOOTH_EVENTS": "window_T"},
    "smooth_1970": {"SMOOTH_EVENTS": "period", "SMOOTH_FROM": 1970, "SMOOTH_MC": 5.1},
    "smooth_cv": {"KERNEL_CV": True},
    "gauss": {"KERNEL": "gauss"},
    "dmax200": {"MAX_DIST_KM": 200.0},
    "msr_ah": {"MSR": "AllenHayesIntraslab"},
    "dip45": {"NPD": [(0.5, 0.0, 45.0, 90.0), (0.5, 180.0, 45.0, 90.0)]},
    "dip90": {"NPD": [(0.5, 0.0, 90.0, 90.0), (0.5, 180.0, 90.0, 90.0)]},
    "mmin55": {"MMIN": 5.5},
    "rate_gk74": {"DC_METHOD": "gk74"},
    "asp20": {"ASPECT": 2.0},
    "cls_m5": {"CAT_VARIANT": "tol_m5"},
    "cls_p5": {"CAT_VARIANT": "tol_p5"},
    "cls_fix": {"CAT_VARIANT": "fixdep_if"},
    "mc_lo": {"COMPLETENESS": _mc("intraslab", "lo")},
    "mc_hi": {"COMPLETENESS": _mc("intraslab", "hi")},
    # final tornado
    "floor_m02": {"MMIN_FIT_BY_CLASS": {"intra_slab": 5.5, "slab_deep": 5.8, "deep_nest": 5.4}},
    "floor_p02": {"MMIN_FIT_BY_CLASS": {"intra_slab": 5.9, "slab_deep": 6.2, "deep_nest": 5.8}},
    "mc_m01": {"COMPLETENESS": _shift_all(_isc.COMPLETENESS, -0.1)},
    "mc_p01": {"COMPLETENESS": _shift_all(_isc.COMPLETENESS, 0.1)},
}

CRUSTAL = {
    "ref": {},
    "stage_camp": CR_CAMP,
    "stage_conv": {**CR_CAMP, "DC_METHOD": "none", "SMOOTH_EVENTS": "all"},
    "smooth_complete": {"SMOOTH_EVENTS": "complete"},
    "smooth_window_T": {"SMOOTH_EVENTS": "window_T"},
    "dc_gk74sym": {"DC_METHOD": "gk74_sym"},
    "dc_gruenthal": {"DC_METHOD": "gruenthal"},
    "margin0": {"BUFFER_MARGIN_KM": 0.0},
    "margin20": {"BUFFER_MARGIN_KM": 20.0},
    "cap65": {"CAP_MAG": 6.5, "FAULT_MMIN": 6.5},
    "m0_center": {"M0_AT_EDGE": False},
    "no_orient": {"ORIENT_BY_DIP_DIR": False},
    "mmax75": {"MMAX_OVERRIDE": {"forearc": 7.5, "intraarc": 7.5, "unclassified": 7.5}},
    "patagonia_box": {"CLASSES": {"forearc": None, "intraarc": None, "unclassified": (-76.0, -64.0, -56.0, -47.0)}},
    "rate_gk74": {"DC_METHOD": "gk74"},
    "cls_m5": {"CAT_VARIANT": "tol_m5"},
    "cls_p5": {"CAT_VARIANT": "tol_p5"},
    "cls_fix": {"CAT_VARIANT": "fixdep_if"},
    # final tornado: the fault tree reduced to one value of one factor (the others keep their weights)
    "depth10": {"FAULT_DEPTH": (0.0, 10.0)},
    "depth30": {"FAULT_DEPTH": (0.0, 30.0)},
    "msr_leonard": {"FAULT_MSR": "Leonard2014_Interplate"},
    "margin0": {"BUFFER_MARGIN_KM": 0.0},
    "margin10": {"BUFFER_MARGIN_KM": 10.0},
    "backarc_borrow": {"B_SOURCE": {"patagonia_crustal": "forearc", "backarc": "forearc"}},
    "patagonia_own": {"B_SOURCE": {}},
    "intraarc_floor50": {"MMIN_FIT_BY_CLASS": {"intraarc": 5.0}},
    "no_exclude": {"EXCLUDE": {}},
    "floor_m02": {"MMIN_FIT_BY_CLASS": {"forearc": 5.3, "intraarc": 4.4, "backarc": 5.3, "patagonia_crustal": 4.3}},
    "floor_p02": {"MMIN_FIT_BY_CLASS": {"forearc": 5.7, "intraarc": 4.8, "backarc": 5.7, "patagonia_crustal": 4.7}},
    "mc_m01": {"COMPLETENESS": _shift_all(_crc.COMPLETENESS, -0.1)},
    "mc_p01": {"COMPLETENESS": _shift_all(_crc.COMPLETENESS, 0.1)},
}
# run.config merges dicts, so a single-factor branch lists every key with the others at weight 0
for _p in _crc.PHI:
    CRUSTAL[f"only_{_p}"] = {"PHI": {k: (v[0], 1.0 if k == _p else 0.0) for k, v in _crc.PHI.items()}}
for _m in _crc.MMAX:
    CRUSTAL[f"only_{_m}"] = {"MMAX": {k: (1.0 if k == _m else 0.0) for k in _crc.MMAX}}
_MFD5 = ("al1", "al2", "al3", "yc", "tap")
for _k in _MFD5:
    CRUSTAL[f"only_{_k}"] = {"MFD": {k: (1.0 if k == _k else 0.0) for k in _MFD5}}
CRUSTAL["only_hyb"] = {"MFD": {k: (1.0 if k == "hyb" else 0.0) for k in _crc.MFD}}
CRUSTAL["multi05"] = {"FAULT_F": 0.5}

# interface campaign variants on top of the hazard base (MMIN_HAZ 5.5): c_<variant>
for k in ("stage_camp", "stage_conv", "zbot40", "zbot60", "ztop5", "ab_p05", "ab_p95", "ab_p05_gk74", "ab_p95_gk74", "ab_p16", "ab_p84", "mmax_p02", "dc_gk74sym", "dc_gruenthal", "fit54", "fit60", "keep_1962_1998", "msr_ah", "rate_gk74", "asp15", "asp20", "asp30", "cls_m5", "cls_p5", "cls_fix", "mc_lo", "mc_hi",
          "floor_m02", "floor_p02", "mc_m01", "mc_p01", "mmax_area", "corner_lo", "corner_hi", "msr_tmg"):
    INTERFACE[f"c_{k}"] = {**INTERFACE["mmin55"], **INTERFACE[k]}

for _v in (INTERFACE, INTRASLAB):
    for _k in ("mc_lo", "mc_hi", "c_mc_lo", "c_mc_hi"):
        if _k in _v and "COMPLETENESS" in _v[_k] and _v[_k]["COMPLETENESS"] is None:
            del _v[_k]["COMPLETENESS"]
VARIANTS = {"interface": INTERFACE, "intraslab": INTRASLAB, "crustal": CRUSTAL}