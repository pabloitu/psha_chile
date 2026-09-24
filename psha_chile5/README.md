# psha_chile5

Chile PSHA: source models, the hazard sensitivity campaign and its report.
Sits in the repository root next to `psha_chile4/` (the Vs30 380 series, kept
as an archive) and reads the same inputs.

## Layout

```
psha_chile5/
  paths.py              inputs (catalogs, Slab2 grids, faults) and the output root
  run.py                builds a source model; steps are cached and reused across variants
  variants.py           named parameter variants per model
  run_report.sh         the whole campaign in one go (see below)
  lib/                  shared: config, catalog io, declustering, completeness, GR, NRML, smoothing
  interface/  s00-s05   subduction interface model
  intraslab/  s00-s03   in-slab model; check_rates, sections, depth_profile: model vs catalog
  crustal/    s00-s04   crustal background and faults
  hazard/
    config.py           site profile (SITE), cities, IMT, return periods, truncation
    logic_tree.py       the reference model, the campaign rows (CAMP, AXES), all jobs (JOBS)
    build.py            writes one OpenQuake job per entry of logic_tree.BUILD
    run_all.sh          builds and runs the jobs, records the calc ids
    post.py             contributions per split, curves of the full model
    tornado.py          one-at-a-time sensitivity from the family-only jobs
    disagg.py           disaggregation figures and tables
    figures.py          curves, contributions, source maps, sections, truncation
    fig_gmm.py, fig_intraslab.py, gmm_check.py
    report.py           collects everything into outputs/report/<site>/ with report.md
  check_completeness.py completeness ensemble: perturbed tables, refit, picks for the mc_lo / mc_hi rows
  interface/check_convention.py  fitted vs observed rates, declustered and full catalog
```

## Outputs

```
outputs/<model>/<tag>/       source models, one folder per variant (tag from the overrides)
outputs/hazard/<site>/       one folder per job, plus _contrib, _tornado, _disagg, _gmm, _pres
outputs/report/<site>/       01_inputs ... 08_checks, report.md, manifest.csv
```

## Run

```
conda activate psha_renta
cd psha_chile5
SMOKE=1 bash run_report.sh     two cities, a few jobs, ~15 min: checks the chain end to end
bash run_report.sh             the campaign, ~2.5 h; rerunning skips everything already done
```

`run_report.sh` builds the source models, runs every job of `logic_tree.BUILD`
that has no calc id yet, then the tables and figures, then the report tree.
`FORCE=1` reruns finished jobs. The site condition is `SITE` in
`hazard/config.py`; each profile has its own output trees.

Source-model steps are cached per step: a step reruns only if a config key it
reads (or an earlier step reads) changed, and a step already built with the
same settings in another variant folder is copied instead of rerun. `run.py`
can also build one model or variant by hand (settings at the top of the file).

Classification rows (cls_m5 / cls_p5) read alternative catalogs from
results/catalogs/integrated/tol_m5 and tol_p5, written by
cat_no_mech_handler/classify_tolerance.py (run it once before the campaign).

Requires numpy, pandas, matplotlib and OpenQuake 3.26 (`oq engine`);
`seismostats` for the optional completeness steps.
