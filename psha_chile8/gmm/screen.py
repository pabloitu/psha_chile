"""Screening of the subduction GMMs of the installed OpenQuake (task GM1, step 2).

Every GSIM class defined for subduction interface or in-slab gets one row. Variants (scaled, epistemic, NSHMP,
basin, site-sigma and region-adjusted copies) are collapsed to their base model. Base models are judged by the
criteria of Cotton et al. (2006) as listed in MASCSN26 (p. 88), plus (8) lacks PGA, SA(0.2) or SA(1.0) and (9)
needs an input we cannot derive. Criterion 1 is read as "built for one other region from that region's data only"
as well as for an irrelevant regime.
"""
import inspect
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TAB = HERE / "tables"

# base model per OpenQuake module: display name, kept, criterion, reason
BASE = {
    "abrahamson_2015": ("Abrahamson et al. (2015)", True, "4", "BC Hydro; superseded by its 2018 update and AG20, kept as required (GEM South America set)"),
    "abrahamson_2018": ("Abrahamson et al. (2018)", False, "2, 4", "BC Hydro update in a PEER report; superseded by Abrahamson & Gülerce (2020)"),
    "abrahamson_gulerce_2020": ("Abrahamson & Gülerce (2020)", True, "", "NGA-Sub, global and South America versions; current tree"),
    "allen_2022": ("Allen (2022)", False, "1", "far-field model for the North Australian Craton"),
    "arroyo_2010": ("Arroyo et al. (2010)", False, "1", "Mexican interface data only"),
    "arteta_2021": ("Arteta et al. (2021)", True, "", "northern South America; Vs30 variants tested"),
    "atkinson_2022": ("Atkinson (2022)", False, "1", "New Zealand backbone model"),
    "atkinson_boore_2003": ("Atkinson & Boore (2003)", True, "", "global subduction data; unsure on 4 (no newer global model of the same authors); random horizontal component"),
    "atkinson_macias_2009": ("Atkinson & Macias (2009)", False, "1, 3", "stochastic simulations for large Cascadia interface events"),
    "bahrampouri_2021": ("Bahrampouri et al. (2021)", False, "8", "Arias intensity, not spectral acceleration"),
    "bahrampouri_2021_duration": ("Bahrampouri et al. (2021), duration", False, "8", "significant duration, not spectral acceleration"),
    "can_shm6_inslab": ("Canada SHM6 in-slab models", False, "", "variant: Canadian adjustments of other base models"),
    "can_shm6_interface": ("Canada SHM6 interface models", False, "", "variant: Canadian adjustments of other base models"),
    "chao_2020": ("Chao et al. (2020)", False, "1", "Taiwan data"),
    "dowrickrhoades_2005": ("Dowrick & Rhoades (2005)", False, "8", "intensity prediction equation (MMI)"),
    "eshm20_bchydro": ("BC Hydro, ESHM20 adjustment", False, "", "variant of Abrahamson et al. (2015), Mediterranean adjustment"),
    "garcia_2005": ("García et al. (2005)", False, "1", "Central Mexico in-slab data only"),
    "geomatrix_1993": ("Geomatrix (1993)", False, "2", "unpublished consultant report"),
    "ghofrani_atkinson_2014": ("Ghofrani & Atkinson (2014)", False, "1, 3", "records of the Tohoku 2011 earthquake only"),
    "gupta_2010": ("Gupta (2010)", False, "1", "Indo-Burmese in-slab events"),
    "hassani_atkinson_2020": ("Hassani & Atkinson (2020)", False, "1", "equivalent point-source model for Japan"),
    "idini_2017": ("Idini et al. (2017)", True, "", "Chilean data; CSN 2026 model; needs the soil type"),
    "jaimes_2020": ("Jaimes & García-Soto (2020)", False, "1", "Mexican intermediate-depth in-slab data only"),
    "kanno_2006": ("Kanno et al. (2006)", False, "1, 7", "Japanese data; peak square-root-sum-of-squares component"),
    "kuehn_2020": ("Kuehn et al. (2020)", True, "", "NGA-Sub, global and South America versions; current tree"),
    "lin_lee_2008": ("Lin & Lee (2008)", False, "1", "northeastern Taiwan data"),
    "macedo_2019": ("Macedo et al. (2019)", False, "8", "Arias intensity, conditional on PGA and SA(1.0)"),
    "manea_2021": ("Manea et al. (2021)", False, "1", "Vrancea intermediate-depth events"),
    "mcverry_2006": ("McVerry et al. (2006)", False, "1, 7", "New Zealand data; larger of the two horizontal components"),
    "megawati_pan_2010": ("Megawati & Pan (2010)", False, "1, 3", "simulations for Sumatran megathrust events"),
    "montalva_2016": ("Montalva et al. (2016)", False, "4", "superseded by Montalva et al. (2017) (OpenQuake docstring)"),
    "montalva_2017": ("Montalva et al. (2017)", True, "", "Chilean data; current tree and CSN 2026"),
    "morikawa_fujiwara_2013": ("Morikawa & Fujiwara (2013)", False, "1, 9", "Japanese data; needs Z1.4"),
    "nath_2012": ("Nath et al. (2012)", False, "1, 8", "Shillong Plateau simulations, vertical component"),
    "nz_nshm2022_abrahamson_gulerce_2020": ("AG20, NZ NSHM 2022", False, "", "variant of Abrahamson & Gülerce (2020)"),
    "nz_nshm2022_kuehn_2020": ("Kuehn et al. (2020), NZ NSHM 2022", False, "", "variant of Kuehn et al. (2020)"),
    "nz_nshm2022_parker": ("Parker et al. (2020), NZ NSHM 2022", False, "", "variant of Parker et al. (2020)"),
    "parker_2020": ("Parker et al. (2020)", True, "", "NGA-Sub, global and South America (SA_S) versions; current tree"),
    "phung_2020": ("Phung et al. (2020)", False, "1", "Taiwan and Japan data"),
    "si_2020": ("Si et al. (2020)", True, "", "NGA-Sub, Japanese data in a PEER report: unsure on 1 and 2; tested by CSN 2026"),
    "si_midorikawa_1999": ("Si & Midorikawa (1999)", False, "1, 4", "Japanese data; superseded by Si et al. (2020)"),
    "sinter": ("Canada 2015 interface backbone", False, "", "variant: backbone of other models"),
    "sslab": ("Canada 2015 in-slab backbone", False, "", "variant: backbone of other models"),
    "skarlatoudis_2013": ("Skarlatoudis et al. (2013)", False, "1", "Hellenic arc in-slab data"),
    "youngs_1997": ("Youngs et al. (1997)", True, "", "global subduction data incl. Chile; CSN 2026 model; total σ only"),
    "zhang_zhao_2005": ("Zhang & Zhao (2005)", False, "8", "lateral spread displacement"),
    "zhao_2006": ("Zhao et al. (2006)", False, "4", "superseded by Zhao et al. (2016)"),
    "zhao_2016": ("Zhao et al. (2016)", True, "", "CSN 2026 model; rvolc set to 0"),
}

# kept classes and their candidates: key, display name, OpenQuake string; the other classes of a kept module are
# variants
REGIME = {"interface": "SInter", "inslab": "SSlab"}
CAND = {
    "interface": [
        ("AG20_GLO", "Abrahamson & Gülerce (2020), global", '[AbrahamsonGulerce2020SInter]\nregion = "GLO"'),
        ("AG20_SAM", "Abrahamson & Gülerce (2020), South America", '[AbrahamsonGulerce2020SInter]\nregion = "SAM"'),
        ("P20_GLO", "Parker et al. (2020), global", "[ParkerEtAl2020SInter]"),
        ("P20_SA", "Parker et al. (2020), South America", '[ParkerEtAl2020SInter]\nregion = "SA"\nsaturation_region = "SA_S"'),
        ("K20_GLO", "Kuehn et al. (2020), global", '[KuehnEtAl2020SInter]\nregion = "GLO"'),
        ("K20_SAM", "Kuehn et al. (2020), South America", '[KuehnEtAl2020SInter]\nregion = "SAM"'),
        ("M17", "Montalva et al. (2017)", "[MontalvaEtAl2017SInter]"),
        ("I17", "Idini et al. (2017)", "[IdiniEtAl2017SInter]"),
        ("Y97", "Youngs et al. (1997)", "[YoungsEtAl1997SInter]"),
        ("Z16", "Zhao et al. (2016)", "[ZhaoEtAl2016SInter]"),
        ("A15", "Abrahamson et al. (2015)", "[AbrahamsonEtAl2015SInter]"),
        ("S20", "Si et al. (2020)", "[SiEtAl2020SInter]"),
        ("A21", "Arteta et al. (2021)", "[ArtetaEtAl2021InterVs30]"),
        ("AB03", "Atkinson & Boore (2003)", "[AtkinsonBoore2003SInter]"),
    ],
    "inslab": [
        ("AG20_GLO", "Abrahamson & Gülerce (2020), global", '[AbrahamsonGulerce2020SSlab]\nregion = "GLO"'),
        ("AG20_SAM", "Abrahamson & Gülerce (2020), South America", '[AbrahamsonGulerce2020SSlab]\nregion = "SAM"'),
        ("P20_GLO", "Parker et al. (2020), global", "[ParkerEtAl2020SSlab]"),
        ("P20_SA", "Parker et al. (2020), South America", '[ParkerEtAl2020SSlab]\nregion = "SA"\nsaturation_region = "SA_S"'),
        ("K20_GLO", "Kuehn et al. (2020), global", '[KuehnEtAl2020SSlab]\nregion = "GLO"'),
        ("K20_SAM", "Kuehn et al. (2020), South America", '[KuehnEtAl2020SSlab]\nregion = "SAM"'),
        ("M17", "Montalva et al. (2017)", "[MontalvaEtAl2017SSlab]"),
        ("I17", "Idini et al. (2017)", "[IdiniEtAl2017SSlab]"),
        ("Y97", "Youngs et al. (1997)", "[YoungsEtAl1997SSlab]"),
        ("Z16", "Zhao et al. (2016)", "[ZhaoEtAl2016SSlab]"),
        ("A15", "Abrahamson et al. (2015)", "[AbrahamsonEtAl2015SSlab]"),
        ("S20", "Si et al. (2020)", "[SiEtAl2020SSlab]"),
        ("A21", "Arteta et al. (2021)", "[ArtetaEtAl2021SlabVs30]"),
        ("AB03", "Atkinson & Boore (2003)", "[AtkinsonBoore2003SSlab]"),
    ],
}
TREE = {"AG20_SAM", "P20_SA", "K20_SAM", "M17"}
ALWAYS = TREE | {"I17", "Y97", "Z16", "A15"}
NAME = {k: n for v in CAND.values() for k, n, _ in v}
# z1pt0 / z2pt5 per GMM: -999 lets OpenQuake take the model's own default from Vs30
BASIN = {"S20": "z2pt5 = -999 (OpenQuake: Campbell & Bozorgnia 2014 Japan relation from Vs30)"}


def gsims():
    from openquake.hazardlib.const import TRT
    from openquake.hazardlib.gsim import get_available_gsims
    out = {}
    for k, c in get_available_gsims().items():
        if inspect.isclass(c) and getattr(c, "DEFINED_FOR_TECTONIC_REGION_TYPE", None) in (
                TRT.SUBDUCTION_INTERFACE, TRT.SUBDUCTION_INTRASLAB):
            out[k] = c
    return out


def screen():
    from openquake.hazardlib.const import TRT, StdDev
    from openquake.hazardlib.imt import PGA, SA
    kept = {s.split("]")[0][1:] for v in CAND.values() for _, _, s in v}
    rows = []
    for k, c in sorted(gsims().items()):
        mod = c.__module__.split(".")[-1]
        name, ok, crit, why = BASE[mod]
        lack = not ({PGA, SA} <= set(c.DEFINED_FOR_INTENSITY_MEASURE_TYPES))
        if k in kept:
            status = "kept"
        elif ok:
            status, crit, why = "variant", "", "variant of the base model (collapsed)" + (
                "; Arteta PHV/THV form: Vs30 variants tested instead" if mod == "arteta_2021" else "")
        else:
            status = "dropped" if crit else "variant"
        if lack and status == "kept":
            crit = (crit + ", 8").strip(", ")
        sd = c.DEFINED_FOR_STANDARD_DEVIATION_TYPES
        rows.append(dict(oq_class=k, model=name, regime="interface" if c.DEFINED_FOR_TECTONIC_REGION_TYPE ==
                         TRT.SUBDUCTION_INTERFACE else "in-slab", status=status, criterion=crit, reason=why,
                         sites=" ".join(sorted(c.REQUIRES_SITES_PARAMETERS)),
                         rupture=" ".join(sorted(c.REQUIRES_RUPTURE_PARAMETERS)),
                         distances=" ".join(sorted(c.REQUIRES_DISTANCES)),
                         component=str(c.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT).split(".")[-1],
                         sigma="tau and phi" if StdDev.INTER_EVENT in sd else "total only"))
    t = pd.DataFrame(rows)
    t.to_csv(TAB / "screening.csv", index=False)
    return t


if __name__ == "__main__":
    t = screen()
    print(t.status.value_counts())
    print(t[t.status != "variant"].groupby(["model", "status", "criterion"]).size().to_string())
