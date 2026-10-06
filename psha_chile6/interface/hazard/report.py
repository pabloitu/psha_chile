# Collect the figures and tables of the campaign into outputs/report/<site>/,
# one numbered folder per report section, each figure next to its data, and
# write report.md (figures in order with captions, the key tables inline) and
# manifest.csv (every hazard job: config hash and calc id). The text of the
# report is written by hand around this skeleton.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import shutil

import pandas as pd

import paths
import run
from variants import VARIANTS
from hazard import config as hc
from hazard import logic_tree as lt

# settings
OUT = hc.REPORT
H = hc.OUT_ROOT
MOD = {f: run.config(f, VARIANTS[f][v]).OUT for f, v in (("interface", "mmin55"), ("intraslab", "ref"), ("crustal", "ref"))}
# section -> [(glob relative to a root, caption)]; a .png is copied with its .csv when one exists
SECTIONS = [
    ("01_inputs", "Inputs: catalog, classification, completeness, declustering", [
        (MOD["intraslab"] / "check" / "sections" / "sections_map.png", "sections through the classified catalog"),
        (MOD["intraslab"] / "check" / "sections" / "section_*.png",
         "trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth"),
        (MOD["intraslab"] / "figures" / "s00_classes.png", "in-slab classes: catalog and declustering"),
        (MOD["crustal"] / "figures" / "s00_classes.png", "crustal classes: catalog and declustering"),
        (MOD["interface"] / "figures" / "s01_decluster.png", "interface: declustering"),
        (MOD["interface"] / "figures" / "s02_mc.png", "interface: completeness"),
        (MOD["intraslab"] / "decluster" / "summary.csv", "in-slab declustering per class and method"),
        (MOD["crustal"] / "decluster" / "summary.csv", "crustal declustering per class and method"),
    ]),
    ("02_interface", "Interface source model", [
        (MOD["interface"] / "figures" / "s00_geometry.png", "interface geometry: segments and areas from Slab2"),
        (MOD["interface"] / "figures" / "s03_b_stability.png", "b-value against the fit floor"),
        (MOD["interface"] / "figures" / "s03_mfd.png", "observed and fitted MFD per segment"),
        (MOD["interface"] / "figures" / "s04_mfd.png", "branch MFDs and moment closure"),
        (MOD["interface"] / "ab" / "compare.csv", "a, b and rates per segment and estimator"),
        (MOD["interface"] / "rates" / "closure.csv", "seismic vs geodetic moment per segment"),
        (MOD["interface"] / "rates" / "branches.csv", "rate branches"),
    ]),
    ("03_inslab", "In-slab source model", [
        (MOD["intraslab"] / "figures" / "s02_fit_*.png", "b-value fit per class against the fit floor"),
        (MOD["intraslab"] / "figures" / "s02_maps.png", "smoothed rate per class"),
        (MOD["intraslab"] / "figures" / "s03_depths.png", "source depths"),
        (MOD["intraslab"] / "figures" / "depth_profile.png", "depth of the in-slab events below the Slab2 top"),
        (MOD["intraslab"] / "check" / "depth_profile.csv", "quantiles of depth below the top, per class and region"),
        (MOD["intraslab"] / "ssm" / "classes.csv", "class parameters: b, rates, Mmax, kernel"),
    ]),
    ("04_crustal", "Crustal source model", [
        (MOD["crustal"] / "figures" / "s02_fit_*.png", "b-value fit per class"),
        (MOD["crustal"] / "figures" / "s02_maps.png", "smoothed background rate"),
        (MOD["crustal"] / "figures" / "s04_cap.png", "background cap and faults"),
        (MOD["crustal"] / "ssm" / "classes.csv", "class parameters"),
        (MOD["crustal"] / "faults" / "branches.csv", "fault branches"),
    ]),
    ("05_gmm", "Ground-motion models", [
        (H / "_gmm" / "g1_depth_mag.png", "in-slab GMMs: depth and magnitude scaling of the median"),
        (H / "_gmm" / "g4_depth.png", "in-slab GMMs: median against hypocentre depth"),
        (H / "_gmm" / "g2_scenarios.png",
         "controlling scenarios from the disaggregation: median, +/-1 sigma, epsilon to the city PGA"),
        (H / "_gmm" / "g3_attenuation.png", "attenuation of the controlling scenarios"),
        (H / "_gmm" / "gmm_scenarios.csv", "median, sigma and epsilon per GMM and scenario"),
    ]),
    ("06_reference", "Reference hazard", [
        (H / "_pres" / "f03_sources.png", "source model"),
        (H / "_pres" / "f04_sections.png", "sources below the cities"),
        (H / "_pres" / "f01_curves.png", "mean hazard curves per city, families and 16-84 % band"),
        (H / "_pres" / "f01b_curves_domains.png", "hazard curves per domain, in-slab classes separated"),
        (H / "_pres" / "f02_contrib.png", "share of the exceedance rate per source"),
        (H / "_contrib" / "full_ref" / "contributions.csv", "PGA and shares per city"),
        (H / "_contrib" / "full_classes" / "contributions.csv", "shares with the in-slab classes"),
        (H / "disagg" / "post" / "figures" / "*_PGA.png", "full-model curve per city with source branches"),
        (H / "disagg" / "post" / "imls.csv", "PGA per city at the target PoEs, mean and quantiles"),
        (H / "_disagg" / "disagg_trt_*.png", "contribution by tectonic region, mean M and R"),
        (H / "_disagg" / "disagg_[!t]*_475.png", "disaggregation M-R-epsilon, 475 yr"),
        (H / "_disagg" / "disagg_[!t]*_2475.png", "disaggregation M-R-epsilon, 2475 yr"),
        (H / "_disagg" / "disagg_summary.csv", "mean M, R, epsilon and shares per city"),
        (H / "_disagg" / "disagg_trt_summary.csv", "mean M, R, epsilon per source type"),
    ]),
    ("07_sensitivity", "Sensitivity", [
        (H / "_tornado" / "overview_PGA.png", "largest change per axis and city"),
        (H / "_tornado" / "tornado_*_PGA.png", "tornado per city"),
        (H / "_contrib" / "figures" / "fig_gmm_pga.png", "single GMM against the tree: PGA"),
        (H / "_contrib" / "figures" / "fig_gmm_share.png", "single GMM against the tree: in-slab share"),
        (H / "_contrib" / "figures" / "fig_intraslab_split.png", "in-slab classes: summed vs class-cut smoothing"),
        (H / "_pres" / "f05_truncation.png", "PGA against truncation level"),
        (H / "_pres" / "f06_declustering.png", "hazard curves per city, declustered vs full catalog"),
        (H / "_disagg" / "disagg_eps.png", "epsilon distribution by source type"),
        (H / "_tornado" / "bars.csv", "range per axis, city and return period"),
        (H / "_tornado" / "tornado.csv", "every row"),
        (H / "_contrib" / "summary.csv", "PGA and shares per split"),
    ]),
    ("08_checks", "Model against the catalog", [
        (MOD["intraslab"] / "figures" / "check_rates.png", "in-slab rate near each city, model vs catalog"),
        (H / "_contrib" / "figures" / "fig_intraslab_rates.png", "in-slab rate by depth and magnitude"),
        (MOD["intraslab"] / "check" / "rates.csv", "model / catalog N(>=M) within 150 km"),
        (MOD["intraslab"] / "check" / "depth.csv", "model and catalog shares per depth band"),
        (MOD["intraslab"] / "check" / "rates_compare.csv",
         "model / catalog per city for the classification, completeness, catalog and smoothing variants"),
        (paths.OUT / "completeness" / "ensemble.png",
         "completeness ensemble: b and N(>=M_ref) for perturbed tables, reference +/- sigma_b"),
        (paths.OUT / "completeness" / "ensemble.csv", "completeness ensemble, every table and fit"),
        (paths.OUT / "completeness" / "convention.png",
         "interface fitted vs observed rates, declustered and full catalog"),
        (paths.OUT / "completeness" / "convention.csv", "fitted / observed N(>=M), declustered and full catalog"),
        (run.config("intraslab", VARIANTS["intraslab"]["smooth_cv"]).OUT / "ssm" / "kernel_cv.csv",
         "kernel cross-validation scores per class and setting"),
    ]),
]
TABLES = [  # (section, csv name in that section, index, columns, values) pivot tables written into report.md
    ("06_reference", "contributions.csv", ["site"], "return_period", "iml_total"),
    ("07_sensitivity", "bars.csv", ["family", "axis"], "site", "range"),
]


COUNT = {}


def md_table(t):
    """Markdown table of a DataFrame (index included)."""
    t = t.reset_index()
    cols = [str(c) for c in t.columns]
    rows = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in t.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |")
    return "\n".join(rows)


def copy(src, sec):
    d = OUT / sec
    d.mkdir(parents=True, exist_ok=True)
    fs = sorted(src.parent.glob(src.name))
    out = []
    for f in fs:
        n = COUNT[sec] = COUNT.get(sec, 0) + 1
        dst = d / f"{n:02d}_{f.name}"
        shutil.copy(f, dst)
        out.append(dst)
        csv = f.with_suffix(".csv")
        if f.suffix == ".png" and csv.exists():
            shutil.copy(csv, dst.with_suffix(".csv"))
    return out


def manifest():
    rows = []
    for p in sorted(H.glob("*/build.json")):
        b = json.loads(p.read_text())
        rows.append({"job": b["name"], "key": b["description"].split()[-1], "calc_id": b.get("calc_id"),
                     "sources": json.dumps(b.get("builds")), "gmm": json.dumps({k: [g[0] for g in v] for k, v in b["gmm"].items()}),
                     "trunc": b.get("trunc"), "site_params": json.dumps(b.get("site_params")),
                     "n_realizations": b.get("n_realizations")})
    return pd.DataFrame(rows)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    md = [f"# psha_chile5 sensitivity campaign, site {hc.SITE} (Vs30 {hc.VS30:g}, Z1.0 {hc.Z1PT0:g} m, "
          f"Z2.5 {hc.Z2PT5:g} km)\n",
          f"Cities: {', '.join(hc.CITIES)}. Return periods: "
          f"{', '.join(str(round(-hc.INV_TIME / __import__('math').log(1 - p))) for p in hc.POES)} yr. "
          f"Truncation {hc.TRUNC}.\n"]
    missing = []
    for sec, title, items in SECTIONS:
        md.append(f"\n## {int(sec[:2])}. {title}\n")
        for src, cap in items:
            fs = copy(src, sec)
            if not fs:
                missing.append(str(src))
                continue
            for f in fs:
                rel = f"{sec}/{f.name}"
                if f.suffix == ".png":
                    md.append(f"![{cap}]({rel})\n\n*{cap}* ({rel}"
                              + (f", data {rel[:-4]}.csv" if f.with_suffix(".csv").exists() else "") + ")\n")
                else:
                    md.append(f"- table: {cap} ({rel})\n")
        for tsec, name, idx, cols, vals in TABLES:
            if tsec != sec:
                continue
            fs = sorted((OUT / sec).glob(f"*_{name}"))
            if fs:
                t = pd.read_csv(fs[0])
                if all(k in t for k in idx + [cols, vals]):
                    piv = t.pivot_table(index=idx, columns=cols, values=vals, aggfunc="max").round(2)
                    md.append(f"\n{vals} by {cols} ({fs[0].name})\n\n" + md_table(piv) + "\n")
    m = manifest()
    m.to_csv(OUT / "manifest.csv", index=False)
    n_ok = int(m["calc_id"].notna().sum()) if len(m) else 0
    md.append(f"\n## 9. Manifest\n\n{len(m)} hazard jobs, {n_ok} with a calc id (manifest.csv).\n")
    if missing:
        md.append("\n## Missing inputs\n\n" + "\n".join(f"- {x}" for x in missing) + "\n")
    (OUT / "report.md").write_text("\n".join(md))
    print(f"wrote {OUT / 'report.md'}" + (f", {len(missing)} inputs missing" if missing else ""))


if __name__ == "__main__":
    main()
