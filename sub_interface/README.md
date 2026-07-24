# sub_interface runbook

## Full chain (in order)

```
s00_geometry.py     Slab2 -> locked interface, exact-cut segments, areas, shp
s01_decluster.py    GK variants on cat_slab_interface.csv
                    -> review outputs/decluster/removed_large.csv
                    -> fill DC_KEEP_IDS, rerun s01
s02_mc.py           KS Mc on the UNdeclustered catalog
                    -> read figures/s02_magtime.png + completeness_proposal.txt
                    -> paste approved steps into COMPLETENESS
s03_ab.py           Weichert vs Kijko-Smit
                    -> read s03_b_stability.png, ab_compare.csv
                    -> set MMIN_FIT, AB_ESTIMATOR
s04_rates.py        moment budget, branch params, closure diagnostic
                    -> fix MMAX if the [mmax] guard fires, rerun
s05_sources.py      16 NRMLs + source_logictree_sub.xml + sites + job.ini
```

## Rerun rules (what changed -> what to rerun, always ending at s05)

| config change                         | rerun            |
|---------------------------------------|------------------|
| SEG_BOUNDS / SEG_IDS                  | s00 s03 s04 s05  |
| Z_TOP / Z_BOTTOM / LAT_STEP / N_EDGES | s00 s04 s05      |
| DC_METHOD / DC_FS / DC_KEEP_IDS       | s01 s03 s04 s05  |
| MC_WINDOWS / MC_* / floor             | s02, hand-update COMPLETENESS, then s03 s04 s05 |
| COMPLETENESS / MMIN_FIT / AB_ESTIMATOR| s03 s04 s05      |
| V_CONV / CHI / DCHI / MU / MMAX / W_* | s04 s05          |
| TRT / RUPT_MESH / ASPECT / RAKE       | s05              |

## Sensitivity variants (OAT, outside the tree)

1. Set `RUN_TAG` in sub_config (e.g. "_z60", "_b077", "_mc_alt"), make the
   one config change, rerun from the earliest affected step per the table.
   Outputs land in `outputs<RUN_TAG>/` — the reference stays untouched.
2. Planned variants: z_bottom 50->60; b at the stability-plot extremes
   (via MMIN_FIT floor/plateau); completeness historical steps variant;
   MMAX seg2 alternatives; MU 30->33.
3. Hazard per variant: `oq engine --run outputs<RUN_TAG>/hazard/job_cities.ini`
   (gmm_logictree.xml must sit next to the job file — collapsed, one GMM
   per TRT, so SSC axes are isolated).
4. Compare per city at 475/2475 yr: tree axes via individual_rlzs of the
   reference run (group rlzs by branchID fields gtag/rtag/form); variants
   via their mean curves vs reference mean.
5. Collapse rule (stated before running): tree axis < ~5% range at all
   sites and both return periods -> collapse; non-tree variant exceeding
   the smallest surviving axis -> promote into the tree or document.

## Notes

- poes in job_cities.ini assume investigation_time = 1 yr
  (0.002105 / 0.000404 ~ 475 / 2475 yr). If switching to 50 yr, change
  both together (0.1 / 0.02).
- sub_interface consumes exactly one upstream file:
  results/catalogs/integrated/cat_slab_interface.csv (classified,
  UNfiltered, UNdeclustered). The upstream *_mc.csv / *_dc.csv are never
  used. s01/s02 print the input fingerprint — compare after any upstream
  re-run.
- s05 write time is dominated by OQ's per-source geometry validation
  (~15-20 s/source at 5 km mesh); the full build is minutes, run it once
  per variant.