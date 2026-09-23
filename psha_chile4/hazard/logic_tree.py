# Logic trees of the hazard jobs, edited here.
# Each entry of JOBS is one job (folder outputs/hazard/<job>/); BUILD lists the
# jobs hazard/build.py writes. GMM is shared by all jobs.

# Source models: family -> list of (variant, weight) or (variant, weight, branches).
# Variant names come from variants.py. Families combine as a product.
#   no branches          all branches with non-zero weight in the model
#   ["a", "b"]           only those, model weights renormalized to 1
#   {"a": 0.6, "b": 0.4} only those, with these weights
#
# Branch ids
#   interface: {seg|full}__{seis|geo_lo|geo_mid|geo_hi}__{tgr|tapered}
#   intraslab: is
#   crustal:   {phi050|phi075|phi100}__{mobs|mgeo}__{tgr|tap|al1|al2|al3|yc},
#              reference, nofaults
#              (fault branches = capped points + faults; nofaults = uncapped points)

# one branch per family, reused by the jobs below
IF1 = [("mmin55", 1.0, ["full__seis__tgr"])]      # interface from M5.5; "ref" = M6.5
IS1 = [("ref", 1.0)]
CR_FAULTS = [("ref", 1.0)]                          # 12 fault branches + capped background
CR_NOFAULTS = [("ref", 1.0, {"nofaults": 1.0})]     # uncapped background only

JOBS = {
    "interface": {"interface": IF1},
    "intraslab": {"intraslab": IS1},
    "crustal": {"crustal": CR_FAULTS},
    "crustal_nofaults": {"crustal": CR_NOFAULTS},
    "subduction": {"interface": IF1, "intraslab": IS1},
    "all": {"interface": IF1, "intraslab": IS1, "crustal": CR_FAULTS},
    "all_nofaults": {"interface": IF1, "intraslab": IS1, "crustal": CR_NOFAULTS},
    # intraslab split by class (weight-0 branches of the same model)
    "is_intra_slab": {"intraslab": [("ref", 1.0, {"is_intra_slab": 1.0})]},
    "is_slab_deep": {"intraslab": [("ref", 1.0, {"is_slab_deep": 1.0})]},
    "is_deep_nest": {"intraslab": [("ref", 1.0, {"is_deep_nest": 1.0})]},
    # classes smoothed only on their own Slab2 domain (variants.py classmask)
    "all_cm": {"interface": IF1, "intraslab": [("classmask", 1.0)], "crustal": CR_FAULTS},
    "cm_intra_slab": {"intraslab": [("classmask", 1.0, {"is_intra_slab": 1.0})]},
    "cm_slab_deep": {"intraslab": [("classmask", 1.0, {"is_slab_deep": 1.0})]},
    "cm_deep_nest": {"intraslab": [("classmask", 1.0, {"is_deep_nest": 1.0})]},
    # full tree
    "full": {"interface": [("ref", 1.0)], "intraslab": [("ref", 1.0)], "crustal": [("ref", 1.0)]},
}

# single GMMs of the final tree, by short name; one family-only job per GMM.
# AG20 is the default GMM below, so its jobs are "interface" and "intraslab".
G_SINTER = {"pk": ("ParkerEtAl2020SInter", 1.0, {"region": "SA", "saturation_region": "SA_S"}),
            "ku": ("KuehnEtAl2020SInter", 1.0, {"region": "SAM"})}
G_SSLAB = {"pk": ("ParkerEtAl2020SSlab", 1.0, {"region": "SA", "saturation_region": "SA_S"}),
           "mv": ("MontalvaEtAl2017SSlab", 1.0, {})}
for k, g in G_SINTER.items():
    JOBS[f"interface_{k}"] = {"interface": IF1, "gmm": {"Subduction Interface": [g]}}
for k, g in G_SSLAB.items():
    JOBS[f"intraslab_{k}"] = {"intraslab": IS1, "gmm": {"Subduction IntraSlab": [g]}}

# One-at-a-time campaign. Every row is one family-only job with the full GMM tree
# of its region, named c_<if|is|cr>_<row>; the other two families stay at "ref".
# Families combine exactly afterwards (hazard/tornado.py): the tree is a product,
# so 1 - P_total = prod over families of (1 - P_family) for the mean curves.
# AXES groups rows into one tornado bar each (range over its rows, reference = 0).
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
IF_B = ["full__seis__tgr"]
CAMP = {
    "interface": {
        "ref": ("mmin55", 1.0, IF_B),
        "zbot40": ("c_zbot40", 1.0, IF_B), "zbot60": ("c_zbot60", 1.0, IF_B),
        "ztop10": ("c_ztop10", 1.0, IF_B),
        "dc_gk74sym": ("c_dc_gk74sym", 1.0, IF_B), "dc_gruenthal": ("c_dc_gruenthal", 1.0, IF_B),
        "keep6298": ("c_keep_1962_1998", 1.0, IF_B),
        "fit54": ("c_fit54", 1.0, IF_B), "fit60": ("c_fit60", 1.0, IF_B),
        "mmin65": ("ref", 1.0, IF_B),
        "seg": ("mmin55", 1.0, ["seg__seis__tgr"]),
        "geo": ("mmin55", 1.0, ["full__geo_mid__tgr"]),
        "tapered": ("mmin55", 1.0, ["full__seis__tapered"]),
        "tree": ("mmin55", 1.0),
    },
    "intraslab": {
        "ref": ("ref", 1.0),
        "classmask": ("classmask", 1.0),
        "dc_gk74sym": ("dc_gk74sym", 1.0), "dc_gruenthal": ("dc_gruenthal", 1.0),
        "sd_fit57": ("sd_fit57", 1.0), "sd_fit60": ("sd_fit60", 1.0),
        "is_fit55": ("is_fit55", 1.0), "is_fit58": ("is_fit58", 1.0),
        "pad0": ("pad0", 1.0), "pad04": ("pad04", 1.0),
        "dz0": ("dz0", 1.0), "dz15": ("dz15", 1.0),
        "lsd0": ("lsd0", 1.0), "lsd40": ("lsd40", 1.0),
        "usd_free": ("usd_free", 1.0),
        "nn10": ("nn10", 1.0), "nn50": ("nn50", 1.0),
    },
    "crustal": {
        "ref": ("ref", 1.0),
        "nofaults": ("ref", 1.0, {"nofaults": 1.0}),
        "margin0": ("margin0", 1.0), "margin20": ("margin20", 1.0),
        "cap65": ("cap65", 1.0),
        "dc_gruenthal": ("dc_gruenthal", 1.0),
        "mmax75": ("mmax75", 1.0),
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
AXES = [
    ("interface", "Z_BOTTOM 40 / 60 km", ["zbot40", "zbot60"]),
    ("interface", "Z_TOP 10 km", ["ztop10"]),
    ("interface", "declustering", ["dc_gk74sym", "dc_gruenthal"]),
    ("interface", "keep 1962 / 1998 events", ["keep6298"]),
    ("interface", "b: fit floor 5.4 / 6.0", ["fit54", "fit60"]),
    ("interface", "MMIN_HAZ 6.5", ["mmin65"]),
    ("interface", "geometry: segmented", ["seg"]),
    ("interface", "rate: geodetic (mid)", ["geo"]),
    ("interface", "MFD: tapered", ["tapered"]),
    ("interface", "full 16-branch tree", ["tree"]),
    ("interface", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_ku"]),
    ("intraslab", "class domain cut at 50 km", ["classmask"]),
    ("intraslab", "declustering", ["dc_gk74sym", "dc_gruenthal"]),
    ("intraslab", "slab_deep b: floor 5.7 / 6.0", ["sd_fit57", "sd_fit60"]),
    ("intraslab", "intra_slab b: floor 5.5 / 5.8", ["is_fit55", "is_fit58"]),
    ("intraslab", "Mmax pad 0 / 0.4", ["pad0", "pad04"]),
    ("intraslab", "hypocentre below slab top 0 / 15 km", ["dz0", "dz15"]),
    ("intraslab", "rupture band bottom +0 / +40 km", ["lsd0", "lsd40"]),
    ("intraslab", "rupture top free above slab top", ["usd_free"]),
    ("intraslab", "smoothing neighbours 10 / 50", ["nn10", "nn50"]),
    ("intraslab", "GMM (single vs tree)", ["gmm_ag", "gmm_pk", "gmm_mv"]),
    ("crustal", "faults vs no faults", ["nofaults"]),
    ("crustal", "buffer margin 0 / 20 km", ["margin0", "margin20"]),
    ("crustal", "cap and fault Mmin 6.5", ["cap65"]),
    ("crustal", "declustering", ["dc_gruenthal"]),
    ("crustal", "background Mmax 7.5", ["mmax75"]),
    ("crustal", "GMM (single vs tree)", ["gmm_ask", "gmm_bssa", "gmm_cb", "gmm_cy"]),
    # family "all": every family rerun with the row's setting (site parameters)
    ("all", "Vs30 760 (rock)", ["vs760"]),
]
SITE_ROWS = {"vs760": {"VS30": 760.0, "Z1PT0": 48.0, "Z2PT5": 0.61}}
SHORT = {"interface": "if", "intraslab": "is", "crustal": "cr"}
TRT = {"interface": "Subduction Interface", "intraslab": "Subduction IntraSlab", "crustal": "Active Shallow Crust"}
for fam, rows in CAMP.items():
    for r, e in rows.items():
        JOBS[f"c_{SHORT[fam]}_{r}"] = {fam: [e], "gmm": GMM_FULL}
    for k, g in CAMP_GMM[fam].items():
        JOBS[f"c_{SHORT[fam]}_gmm_{k}"] = {fam: [rows["ref"]], "gmm": {TRT[fam]: [(g[0], 1.0, g[2])]}}
    for k, site in SITE_ROWS.items():
        JOBS[f"c_{SHORT[fam]}_{k}"] = {fam: [rows["ref"]], "gmm": GMM_FULL, "site": site}

# jobs written by hazard/build.py, one folder each: outputs/hazard/<job>/
# campaign: the three references first, then the rows of CAMP_FAMS
CAMP_FAMS = ["intraslab", "interface", "crustal"]
BUILD = ([f"c_{SHORT[f]}_ref" for f in CAMP_FAMS]
         + [j for f in CAMP_FAMS for j in JOBS if j.startswith(f"c_{SHORT[f]}_") and not j.endswith("_ref")])

# Ground motion: tectonic region -> list of (gsim, weight, arguments).
# Only regions present in SOURCES are written.

# one GMM per region
GMM = {
    "Subduction Interface": [
        ("AbrahamsonGulerce2020SInter", 1.0, {"region": "SAM"}),
    ],
    "Subduction IntraSlab": [
        ("AbrahamsonGulerce2020SSlab", 1.0, {"region": "SAM"}),
    ],
    "Active Shallow Crust": [
        ("AbrahamsonEtAl2014", 1.0, {}),
    ],
}

# full tree
# GMM = {
#     "Subduction Interface": [
#         ("AbrahamsonGulerce2020SInter", 0.34, {"region": "SAM"}),
#         ("ParkerEtAl2020SInter", 0.33, {"region": "SA", "saturation_region": "SA_S"}),
#         ("KuehnEtAl2020SInter", 0.33, {"region": "SAM"}),
#     ],
#     "Subduction IntraSlab": [
#         ("AbrahamsonGulerce2020SSlab", 0.34, {"region": "SAM"}),
#         ("ParkerEtAl2020SSlab", 0.33, {"region": "SA", "saturation_region": "SA_S"}),
#         ("MontalvaEtAl2017SSlab", 0.33, {}),
#     ],
#     "Active Shallow Crust": [
#         ("AbrahamsonEtAl2014", 0.25, {}),
#         ("BooreEtAl2014", 0.25, {}),
#         ("CampbellBozorgnia2014", 0.25, {}),
#         ("ChiouYoungs2014", 0.25, {}),
#     ],
# }