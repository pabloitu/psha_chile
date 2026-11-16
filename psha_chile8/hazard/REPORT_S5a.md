# S5a hazard jobs: interface and in-slab (plus the crustal family, S5b)

16 Nov 2026. Brief `tasks/S5a_assembly_if_is.md`; crustal part from the S3 hand-off note (`model/crustal/S5_HANDOFF.md`). Code in `hazard/`, ported from `psha_chile7/hazard/` (build, run_all, combine, post, check_tree, tornado_final, tests). PGA 475 yr at the 14 cities, rock (Vs30 800 inferred, Z1.0 40 m, Z2.5 0.6 km), truncation 3.

## 1. What runs

| family | files read | reference | tree |
|---|---|---|---|
| interface | `model/interface/nrml_2026-11-16/` (240 files) and its scaling level | `margin_full_own_taper_ml_seis` × Strasser / Thingbaijam / Allen and Hayes at 1/3 | 72 files × 3 scaling = 216 paths, 864 rlz |
| in-slab | `model/inslab/nrml/2026-11-16b/` (one source per cell; S2 timing check passed: same PGA within 0.0006 %, 58 % of the run time) | `gk_taper_ml_l3` | 2 branches (gk / nn 0.5), 8 rlz |
| crustal | `model/crustal/nrml/2026-11-16e/` (S3 ready flag, parse check verified: 59 files, rates within 4.2e-6) | `reference` (multi-fault A, jump 15 km, ψ 0.8, depth 10 km, tapered, GK pattern) | 84 branches, 336 rlz, run in two parts (section 6) |

- **Interface reference:** the scaling level stays in the reference at 1/3 each, because DECISIONS applies it to every interface source. The b option is the own b of each unit (REPORT_S1, tree). The "scaling alone" rows are measured against that.
- **GMMs:** the current tree of DECISIONS. Interface and in-slab: AG20 (SAM), Parker (SA, SA_S), Kuehn (SAM), Montalva 2017, 0.25 each. Crustal: ASK14, BSSA14, CB14, CY14.
- **Settings:** maximum distance 600 / 500 / 300 km; `pointsource_distance` 100 km; mesh 10 km; MFD bin 0.1; 30 log levels 0.005–3 g; investigation time 1 yr; `individual_rlzs = true`.
- **Site model:** every job reads `site_model.csv` with soiltype 1 (Idini class sI, rock), needed only by the MASCSN26 interface set. OpenQuake refuses `sites_csv` together with a site model.
- **`strict = false`:** OpenQuake refuses fault sources above 52 000 ruptures in strict mode. The margin source has 101 864 ruptures at the 10 km mesh. The flag removes only that guard; the S1 check jobs had avoided it with a 20 km mesh.
- **Branch tables:** `hazard/branches_interface.csv` (240 files plus the 3 scaling branches) and `hazard/branches_inslab.csv` (24). The id in the job source trees is `if_<id>` / `is_<id>` / `cr_<id>`.
- **Run order:** one job at a time (`run_all.sh` waits while any other OpenQuake job is executing). References first, then the family trees, the rows and the check jobs; the crustal jobs once S3 was ready, its reference first.

## 2. Jobs, calc ids, run times

66 jobs ran, 4.4 h of OpenQuake time in all (05:33–10:20). Every job has its `build.json` with calc id and wall time; `hazard/out/jobs.csv` lists them.

| job | calc | s | rlz |
|---|---|---|---|
| t_if_ref | 522 | 291 | 12 |
| t_is_ref | 523 | 133 | 4 |
| f_if_tree | 524 | 3 432 | 864 |
| f_is_tree | 525 | 224 | 8 |
| t_cr_ref | 538 | 147 | 4 |
| f_cr_tree_a + f_cr_tree_b | 590 + 591 | 585 + 236 | 312 + 24 |
| c_if_small / c_is_small / c_all_small | 565 / 566 / 567 | 290 / 203 / 403 | 24 / 8 / 192 |
| interface rows | 526–555 | 120–315 | |
| in-slab rows | 544–564 | 111–122 | |
| crustal rows | 568–589 | 124–152 | |

- **Why the interface is slow:** an interface job is serial-bound. The margin complex fault cannot be split, so a single-branch job uses 2 of 16 workers. The rows took 275 s with three scaling relations and 125 s with one. The interface tree spreads over all workers: 7.9 M ruptures in 57 min.
- **Why the in-slab and crustal jobs are fast:** they parallelize over point sources. The crustal tree costs about 4 backgrounds, because OpenQuake computes identical sources once across branches.

## 3. Reference PGA 475 yr (g)

Single reference branch per family, mean over its scaling and GMM realizations; combinations in rate space.

| site | interface | in-slab | crustal | interface + in-slab | all three |
|---|---|---|---|---|---|
| Iquique | 0.726 | 0.727 | 0.301 | 0.999 | 1.030 |
| Calama | 0.278 | 0.635 | 0.058 | 0.680 | 0.681 |
| Antofagasta | 1.078 | 0.660 | 0.239 | 1.237 | 1.242 |
| Copiapó | 0.689 | 0.560 | 0.106 | 0.879 | 0.882 |
| La Serena | 0.900 | 0.964 | 0.149 | 1.289 | 1.290 |
| Valparaíso | 1.054 | 0.756 | 0.280 | 1.268 | 1.281 |
| Santiago centro | 0.440 | 0.591 | 0.133 | 0.731 | 0.735 |
| Santiago Peñalolén | 0.377 | 0.564 | 0.167 | 0.673 | 0.708 |
| Concepción | 1.037 | 0.433 | 0.138 | 1.115 | 1.117 |
| Pucón | 0.266 | 0.180 | 0.380 | 0.325 | 0.479 |
| Puerto Montt | 0.484 | 0.192 | 0.105 | 0.529 | 0.533 |
| Hornopirén | 0.286 | 0.145 | 0.508 | 0.328 | 0.601 |
| Puerto Aysén | 0.123 | 0.024 | 0.486 | 0.126 | 0.502 |
| Puerto Williams | – | – | 0.074 | – | 0.074 |

Puerto Williams: interface and in-slab PGA below 0.005 g (the lowest level); it enters only through the crustal family.

## 4. Family trees: mean (16–84 %), PGA 475 yr (g)

Fractiles of the combinations by exact enumeration (`combine.exact`: 864 × 8 × 336 = 2.3 M joint realizations).

| site | interface | in-slab | crustal | interface + in-slab | interface + in-slab + crustal |
|---|---|---|---|---|---|
| Iquique | 0.881 (0.52–1.10) | 0.723 (0.56–0.89) | 0.314 (0.27–0.35) | 1.093 (0.85–1.28) | 1.119 (0.90–1.30) |
| Calama | 0.323 (0.19–0.42) | 0.683 (0.52–0.84) | 0.057 (0.05–0.06) | 0.730 (0.57–0.87) | 0.731 (0.57–0.87) |
| Antofagasta | 1.212 (0.72–1.52) | 0.640 (0.49–0.79) | 0.239 (0.21–0.25) | 1.330 (0.96–1.62) | 1.334 (0.97–1.62) |
| Copiapó | 0.799 (0.57–0.99) | 0.538 (0.44–0.70) | 0.105 (0.09–0.11) | 0.934 (0.74–1.10) | 0.936 (0.75–1.10) |
| La Serena | 1.084 (0.76–1.33) | 1.007 (0.73–1.35) | 0.149 (0.13–0.16) | 1.409 (1.13–1.66) | 1.410 (1.13–1.66) |
| Valparaíso | 1.138 (0.88–1.39) | 0.787 (0.57–0.95) | 0.296 (0.24–0.35) | 1.341 (1.11–1.55) | 1.352 (1.13–1.56) |
| Santiago centro | 0.476 (0.38–0.56) | 0.562 (0.46–0.70) | 0.128 (0.11–0.14) | 0.721 (0.61–0.84) | 0.725 (0.62–0.84) |
| Santiago Peñalolén | 0.407 (0.33–0.48) | 0.535 (0.44–0.66) | 0.160 (0.13–0.19) | 0.659 (0.56–0.77) | 0.690 (0.59–0.80) |
| Concepción | 1.049 (0.83–1.28) | 0.419 (0.30–0.52) | 0.153 (0.14–0.17) | 1.121 (0.91–1.34) | 1.124 (0.92–1.34) |
| Pucón | 0.256 (0.18–0.31) | 0.165 (0.14–0.19) | 0.427 (0.35–0.47) | 0.309 (0.25–0.36) | 0.504 (0.44–0.55) |
| Puerto Montt | 0.487 (0.34–0.60) | 0.174 (0.14–0.22) | 0.116 (0.10–0.13) | 0.526 (0.40–0.63) | 0.530 (0.40–0.63) |
| Hornopirén | 0.289 (0.20–0.35) | 0.132 (0.11–0.15) | 0.624 (0.48–0.72) | 0.326 (0.26–0.38) | 0.686 (0.57–0.78) |
| Puerto Aysén | 0.128 (0.09–0.16) | 0.021 (0.02–0.03) | 0.540 (0.44–0.61) | 0.131 (0.10–0.16) | 0.553 (0.46–0.62) |
| Puerto Williams | – | – | 0.084 (0.07–0.10) | – | 0.084 (0.07–0.10) |

- **Effect of the crustal family on the totals:** it changes the combined numbers little in the north and centre (+0 to +5 %). It doubles them in the south: Pucón 0.31 → 0.50 g, Hornopirén 0.33 → 0.69 g, Puerto Aysén 0.13 → 0.55 g.
- **Interface tree against the single reference branch:** 0–21 % higher, highest at Iquique, La Serena and Antofagasta, through the geodetic and segmented branches.
- Figure `hazard/out/trees/curves.png`: mean and 16–84 % per family and combined, with the interface + in-slab mean dashed.

## 5. Tornado

`hazard/tornado_final.py` writes two sets:
- **`hazard/out/tornado_if_is/`:** interface + in-slab, without the crustal family, the numbers of the brief.
- **`hazard/out/tornado/`:** all three families.

Each set has `tornado.csv` (both numbers per row and city: family alone and combined), `bars.csv`, `summary.txt` (ranked, ≥ 5 % verdict), `heatmap.png` (largest |change| per axis and city, family alone and combined) and `bars_<city>.png`. There are no figure titles. The heat-map scale is capped at 50 % and the bar axes at ±100 %; larger values are printed.

Each row changes one choice of its family's reference. The base is the family reference, except: χ 0.7 / 0.9 against geodetic χ 0.8; the pooled and margin b options against the segmented row (they exist only for segments).

### Interface + in-slab (without the crustal family), change of the combined PGA 475 yr (%)

| family | axis | row | Iqu | Cal | Ant | Cop | LSe | Val | SCe | SPe | Con | Puc | PMo | Hor | Ays |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IF | segmentation | four segments | -8 | -4 | -19 | -7 | -3 | -2 | -5 | -4 | -13 | -20 | -19 | -17 | -13 |
| IF | rate model | geodetic χ 0.8 | +7 | +2 | +10 | +9 | +6 | +10 | +5 | +4 | +13 | +10 | +13 | +12 | +13 |
| IF | geodetic coupling χ | 0.7 | -3 | -1 | -5 | -4 | -3 | -4 | -3 | -2 | -6 | -5 | -6 | -5 | -6 |
| IF | geodetic coupling χ | 0.9 | +3 | +1 | +4 | +4 | +3 | +4 | +3 | +2 | +5 | +4 | +6 | +5 | +5 |
| IF | (a, b) uncertainty | 5th | -4 | -1 | -7 | -6 | -4 | -6 | -4 | -3 | -8 | -7 | -9 | -8 | -8 |
| IF | (a, b) uncertainty | 95th | +5 | +2 | +7 | +7 | +5 | +7 | +5 | +4 | +9 | +8 | +10 | +9 | +10 |
| IF | b per segment | shared b | +1 | +0 | +1 | -2 | -2 | +7 | +4 | +3 | +6 | -7 | -12 | -11 | -11 |
| IF | b per segment | whole-margin b | +0 | +0 | +1 | -3 | -2 | +6 | +4 | +3 | +6 | -7 | -13 | -12 | -12 |
| IF | MFD shape | truncated | +0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | +1 |
| IF | declustering | GK74 | +3 | +3 | +6 | +10 | +7 | +7 | +7 | +6 | +8 | +11 | +10 | +10 | +7 |
| IF | declustering | NN | -6 | -1 | -9 | -6 | -5 | -8 | -3 | -3 | -11 | -8 | -12 | -10 | -11 |
| IF | rupture scaling | Strasser | -1 | -0 | -2 | -2 | -1 | -1 | -1 | -0 | -2 | -2 | -2 | -1 | -1 |
| IF | rupture scaling | Thingbaijam | +4 | +1 | +6 | +6 | +4 | +7 | +4 | +3 | +8 | +6 | +9 | +8 | +10 |
| IF | rupture scaling | Allen–Hayes | -4 | -1 | -5 | -5 | -4 | -6 | -4 | -3 | -6 | -5 | -7 | -7 | -8 |
| IF | GMM-1R models | AG20 | -6 | -2 | -10 | -7 | -6 | -9 | -4 | -4 | -11 | -8 | -9 | -8 | -15 |
| IF | GMM-1R models | Parker | -7 | +2 | -12 | -3 | -4 | -9 | +2 | +3 | -13 | +5 | -5 | +2 | +3 |
| IF | GMM-1R models | Kuehn | +9 | +3 | +17 | +15 | +12 | +17 | +9 | +7 | +20 | +9 | +13 | +7 | -11 |
| IF | GMM-1R models | Montalva | +3 | -3 | +3 | -4 | -2 | +1 | -6 | -6 | +3 | -5 | +1 | -0 | +15 |
| IF | GMM set | GMM-FIT | -8 | -4 | -11 | -13 | -9 | -11 | -10 | -9 | -14 | -16 | -16 | -16 | -12 |
| IF | GMM set | GMM-CSN | -12 | -4 | -17 | -17 | -13 | -16 | -11 | -9 | -20 | -14 | -18 | -14 | -3 |
| IF | GMM set | GMM-GEM | -13 | -2 | -21 | -13 | -12 | -18 | -6 | -4 | -24 | -7 | -17 | -11 | -11 |
| IF | GMM truncation | 2.5σ | -2 | -1 | -3 | -2 | -2 | -2 | -1 | -1 | -3 | -2 | -3 | -3 | -4 |
| IF | GMM truncation | 4σ | +1 | +0 | +1 | +1 | +1 | +1 | +1 | +1 | +2 | +1 | +2 | +2 | +3 |
| IS | (a, b) uncertainty | 5th | -4 | -7 | -2 | -4 | -5 | -3 | -5 | -6 | -1 | -3 | -1 | -2 | -1 |
| IS | (a, b) uncertainty | 95th | +5 | +8 | +3 | +5 | +7 | +4 | +6 | +7 | +2 | +3 | +2 | +3 | +1 |
| IS | spatial pattern | NN | -1 | +12 | -2 | -3 | +5 | +3 | -6 | -7 | -1 | -5 | -3 | -4 | -1 |
| IS | GMM-1R models | AG20 | -2 | +6 | -2 | -1 | -5 | -4 | +1 | +1 | -2 | +1 | -0 | +0 | -0 |
| IS | GMM-1R models | Parker | +13 | +24 | +9 | +16 | +23 | +9 | +19 | +20 | +3 | +7 | +4 | +5 | +1 |
| IS | GMM-1R models | Kuehn | -11 | -13 | -7 | -8 | -15 | -9 | -12 | -12 | -4 | -5 | -3 | -4 | -0 |
| IS | GMM-1R models | Montalva | -1 | -21 | -1 | -8 | -5 | +2 | -10 | -12 | +3 | -3 | -0 | -2 | -1 |
| IS | GMM set | GMM-FIT | -11 | -19 | -6 | -11 | -14 | -7 | -15 | -16 | -3 | -5 | -3 | -4 | -0 |
| IS | GMM set | GMM-CSN | -11 | -27 | -6 | -13 | -14 | -6 | -19 | -20 | -2 | -6 | -3 | -4 | -0 |
| IS | GMM set | GMM-GEM | -11 | -23 | -6 | -12 | -14 | -6 | -16 | -17 | -2 | -5 | -3 | -4 | -0 |
| IS | GMM truncation | 2.5σ | -3 | -5 | -2 | -2 | -3 | -2 | -4 | -4 | -1 | -2 | -1 | -1 | -0 |
| IS | GMM truncation | 4σ | +2 | +3 | +1 | +2 | +2 | +1 | +2 | +2 | +1 | +1 | +0 | +1 | +0 |

Ranked by the largest |change| over the cities (`tornado_if_is/summary.txt`):
- **≥ 5 %:**
  - GMM sets: in-slab 27 % (Calama), interface 24 % (Concepción).
  - GMM-1R models, each alone: 24 % and 20 %.
  - Interface source choices: segmentation 20 % (Pucón), geodetic rate 14 %, b option 13 %, declustered rate 12 %, (a, b) 10 %, scaling 10 %, coupling 6 %.
  - In-slab: nearest-neighbour pattern 12 % (Calama), (a, b) 8 %.
- **< 5 %:** truncation 2.5 / 4.0 (in-slab 4.5 %, interface 4.2 %) and the interface MFD shape (cut against tapered, 0.6 %).

### All three families, change of the total PGA 475 yr (%)

| family | axis | row | Iqu | Cal | Ant | Cop | LSe | Val | SCe | SPe | Con | Puc | PMo | Hor | Ays | PWi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IF | segmentation | four segments | -7 | -4 | -18 | -7 | -3 | -2 | -5 | -4 | -13 | -7 | -19 | -4 | -0 | +0 |
| IF | rate model | geodetic χ 0.8 | +6 | +2 | +10 | +9 | +6 | +9 | +5 | +4 | +13 | +4 | +13 | +3 | +1 | +0 |
| IF | geodetic coupling χ | 0.7 | -3 | -1 | -5 | -4 | -3 | -4 | -3 | -2 | -6 | -2 | -6 | -2 | -0 | +0 |
| IF | geodetic coupling χ | 0.9 | +3 | +1 | +4 | +4 | +3 | +4 | +2 | +2 | +5 | +2 | +6 | +2 | +0 | +0 |
| IF | (a, b) uncertainty | 5th | -4 | -1 | -7 | -6 | -4 | -6 | -4 | -3 | -8 | -3 | -9 | -2 | -1 | +0 |
| IF | (a, b) uncertainty | 95th | +4 | +2 | +7 | +7 | +5 | +7 | +4 | +3 | +9 | +3 | +10 | +3 | +1 | +0 |
| IF | b per segment | shared b | +1 | +0 | +1 | -2 | -2 | +7 | +4 | +3 | +6 | -2 | -12 | -2 | -1 | +0 |
| IF | b per segment | whole-margin b | +0 | +0 | +1 | -3 | -2 | +6 | +3 | +2 | +6 | -2 | -12 | -2 | -1 | +0 |
| IF | MFD shape | truncated | +0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | +0 | +0 | +0 |
| IF | declustering | GK74 | +3 | +3 | +6 | +10 | +7 | +7 | +7 | +6 | +8 | +5 | +9 | +4 | +2 | +0 |
| IF | declustering | NN | -5 | -1 | -9 | -6 | -5 | -7 | -3 | -2 | -11 | -2 | -11 | -2 | -0 | +0 |
| IF | rupture scaling | Strasser | -1 | -0 | -2 | -2 | -1 | -1 | -1 | -0 | -2 | -1 | -2 | -0 | -0 | +0 |
| IF | rupture scaling | Thingbaijam | +4 | +1 | +6 | +6 | +4 | +6 | +4 | +3 | +8 | +3 | +8 | +3 | +1 | +0 |
| IF | rupture scaling | Allen–Hayes | -3 | -1 | -5 | -4 | -4 | -5 | -3 | -3 | -6 | -2 | -7 | -2 | -1 | +0 |
| IF | GMM-1R models | AG20 | -5 | -2 | -10 | -6 | -6 | -8 | -4 | -3 | -11 | -3 | -8 | -3 | -1 | +0 |
| IF | GMM-1R models | Parker | -6 | +2 | -12 | -3 | -4 | -9 | +2 | +2 | -13 | +3 | -5 | +2 | +2 | +0 |
| IF | GMM-1R models | Kuehn | +8 | +3 | +17 | +15 | +12 | +16 | +9 | +6 | +20 | +5 | +13 | +4 | +1 | +0 |
| IF | GMM-1R models | Montalva | +2 | -3 | +3 | -4 | -2 | +1 | -6 | -5 | +3 | -4 | +0 | -3 | -1 | +0 |
| IF | GMM set | GMM-FIT | -8 | -4 | -11 | -13 | -9 | -10 | -9 | -8 | -13 | -7 | -15 | -6 | -2 | +0 |
| IF | GMM set | GMM-CSN | -11 | -4 | -17 | -16 | -12 | -15 | -11 | -8 | -20 | -7 | -18 | -6 | -2 | +0 |
| IF | GMM set | GMM-GEM | -12 | -2 | -21 | -13 | -12 | -18 | -6 | -4 | -24 | -3 | -17 | -3 | -0 | +0 |
| IF | GMM truncation | 2.5σ | -2 | -1 | -3 | -2 | -2 | -2 | -1 | -1 | -3 | -1 | -3 | -1 | -0 | +0 |
| IF | GMM truncation | 4σ | +1 | +0 | +1 | +1 | +1 | +1 | +1 | +1 | +2 | +1 | +2 | +1 | +0 | +0 |
| IS | (a, b) uncertainty | 5th | -4 | -7 | -2 | -4 | -5 | -3 | -5 | -5 | -1 | -1 | -1 | -1 | -0 | +0 |
| IS | (a, b) uncertainty | 95th | +5 | +8 | +3 | +5 | +7 | +4 | +6 | +6 | +2 | +1 | +2 | +1 | +0 | +0 |
| IS | spatial pattern | NN | -1 | +12 | -1 | -3 | +5 | +2 | -6 | -6 | -1 | -2 | -2 | -1 | -0 | +0 |
| IS | GMM-1R models | AG20 | -2 | +6 | -2 | -1 | -5 | -4 | +1 | +1 | -2 | +1 | -0 | +0 | +0 | +0 |
| IS | GMM-1R models | Parker | +12 | +24 | +8 | +16 | +22 | +9 | +19 | +18 | +3 | +3 | +3 | +2 | +0 | +0 |
| IS | GMM-1R models | Kuehn | -10 | -13 | -7 | -8 | -15 | -8 | -11 | -10 | -4 | -2 | -3 | -1 | -0 | +0 |
| IS | GMM-1R models | Montalva | -1 | -20 | -1 | -7 | -5 | +2 | -10 | -11 | +3 | -2 | -0 | -1 | -0 | +0 |
| IS | GMM set | GMM-FIT | -10 | -19 | -6 | -10 | -14 | -7 | -15 | -14 | -3 | -2 | -3 | -1 | -0 | +0 |
| IS | GMM set | GMM-CSN | -10 | -27 | -6 | -12 | -14 | -6 | -18 | -18 | -2 | -3 | -3 | -2 | -0 | +0 |
| IS | GMM set | GMM-GEM | -10 | -22 | -6 | -11 | -14 | -6 | -16 | -15 | -2 | -2 | -3 | -2 | -0 | +0 |
| IS | GMM truncation | 2.5σ | -3 | -5 | -2 | -2 | -3 | -2 | -3 | -3 | -1 | -1 | -1 | -0 | -0 | +0 |
| IS | GMM truncation | 4σ | +2 | +3 | +1 | +2 | +2 | +1 | +2 | +2 | +1 | +0 | +0 | +0 | +0 | +0 |
| CR | spatial pattern | NN | +0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | +0 | -0 | -0 | -0 | +3 | -0 |
| CR | GMM-1R models | ASK14 | +0 | +0 | +0 | +0 | +0 | +0 | -0 | -0 | +0 | -4 | +0 | -3 | -5 | -1 |
| CR | GMM-1R models | BSSA14 | -1 | +0 | -0 | +0 | -0 | -0 | +0 | -0 | -0 | -0 | +0 | -3 | -4 | -1 |
| CR | GMM-1R models | CB14 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +1 | +0 | +8 | +0 | +7 | +7 | +0 |
| CR | GMM-1R models | CY14 | -0 | -0 | -0 | -0 | -0 | +0 | -0 | -1 | -0 | -5 | -0 | -1 | +2 | +2 |
| CR | GMM set | GMM-CSN | -2 | -0 | -0 | -0 | -0 | -1 | -0 | -3 | +22 | +91 | +74 | +23 | +32 | +19 |
| CR | GMM set | GMM-GEM | +1 | +0 | +0 | +0 | +0 | +0 | +0 | +1 | +0 | +2 | +0 | -3 | -6 | +0 |
| CR | GMM truncation | 2.5σ | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -1 | -0 | -0 | -1 | -1 |
| CR | GMM truncation | 4σ | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| CR | background MFD | truncated | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| CR | background rates | declustered | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| CR | with faults | no | -2 | +0 | +0 | +0 | +0 | -1 | +1 | -3 | +0 | -29 | +1 | -43 | -71 | – |
| CR | fault linkage | single-fault | +0 | +0 | +0 | -0 | +0 | -0 | -0 | -0 | -0 | +3 | -0 | +23 | +12 | -0 |
| CR | aseismic coefficient ψ | 0.6 | -1 | +0 | -0 | +0 | +0 | -0 | -0 | -1 | -0 | -6 | -0 | -9 | -17 | -14 |
| CR | aseismic coefficient ψ | 1.0 | +1 | +0 | +0 | +0 | +0 | +0 | +0 | +1 | +0 | +5 | +0 | +7 | +11 | +11 |
| CR | fault depth | 20 km | +0 | -0 | +0 | -0 | +0 | +0 | +0 | -1 | +0 | +8 | +0 | +0 | +1 | +24 |
| CR | max. jump distance | 20 km | +0 | +0 | +0 | -0 | -0 | -0 | -0 | +0 | +0 | -3 | +0 | -4 | -2 | -0 |
| CR | max. jump distance | 5 km | +0 | -0 | +0 | -0 | +0 | +0 | -0 | +0 | -0 | +3 | -0 | +25 | +14 | -0 |
| CR | max. jump distance | 10 km | -0 | -0 | +0 | -0 | +0 | -0 | -0 | +0 | -0 | +3 | -0 | +7 | +14 | -0 |
| CR | fault database | CSN | -1 | -0 | -0 | -0 | -0 | -1 | +0 | -1 | -0 | +5 | -0 | +23 | +64 | +22 |
| CR | fault database | CSN-$\dot{M}_0$ | +1 | -0 | -0 | -0 | -0 | -0 | +0 | +1 | -0 | -9 | -0 | +1 | +25 | -5 |

Crustal axes on the total (`tornado/summary.txt`):
- **≥ 5 %:**
  - GMM set 91 % (Pucón; MASCSN26, see below); no faults −71 % (Puerto Aysén); fault database 64 % (B, Puerto Aysén).
  - Multi-fault jump 25 % (5 km, Hornopirén); fault depth 24 % (Puerto Williams); fault system 23 % (segmented, Hornopirén); ψ 17 %; GMM alone 8 %.
- **< 5 %:** nearest-neighbour pattern 2.7 %, truncation 1.2 %, declustered background rates 0.3 %, cut MFD 0.0 %.
- **Faults dominate the south:** where the crustal family matters (Pucón to Puerto Aysén), its hazard comes from the Liquiñe–Ofqui faults. The background choices move the crustal PGA by about 20 % only further north, where the crustal share of the total is small.

**MASCSN26 crustal set.** The set is Arteta et al. (2023) alone, a model built in Colombia. It raises the crustal PGA 475 by 5–6 times at Concepción (0.14 → 0.72 g) and Puerto Montt (0.11 → 0.70 g), and the total by 91 % at Pucón and 74 % at Puerto Montt. The four NGA-West2 models alone stay within ±15 % of the tree. This needs a look before it is shown.

## 6. Checks

- **check_tree level 1** (`hazard/out/check_tree.txt`): **PASS**. The small joint job (2 interface branches × 3 scaling × 2 in-slab × 4 × 4 GMMs, 192 rlz) against its two family jobs (24 and 8 rlz):
  - mean within 3.9e-6;
  - weights equal to the products of the family weights;
  - every joint curve within 1.6e-5 of the product with the same branches, and its best partner in 192 of 192;
  - 5 / 50 / 95 % PGA within 2.8e-6 of `combine.exact`.
- **Realization mean** against OpenQuake's mean in every job read: below 1e-7.
- **Tests** (`hazard/tests/test_hazard.py`, 8): combination (mean, exact quantiles, Monte Carlo), check_tree on true and broken synthetic trees, logic-tree writer (levels, scaling level restricted to the interface, weights), job list, mixture of tree parts.
- **Crustal tree in two parts.** The single tree job failed: OpenQuake requires section ids to be unique across all sections files of a job, and `cr_sections_A_z10.xml` and `cr_sections_A_z20.xml` share them (e.g. `s_CL-006a_0`). The tree runs as `f_cr_tree_a` (78 branches, weight 0.75) and `f_cr_tree_b` (the 6 multi-fault depth-20 branches, 0.25). Branches are alternatives, so the parts mix exactly: realizations pooled with weight part × weight inside the part (`trees.load`, tested). Renaming the section ids per depth in S3 would let the tree run as one job.

## 7. What is missing

- **In-slab one layer and lower depth:** defined and skipped (`t_is_one_layer`, `t_is_lower_depth`), C15 open. The one-layer files exist but the one-layer hypocentre is to be fixed first.
- **GM1 "top four" crustal set:** not a separate job; it is the current crustal tree.
- **check_tree level 2:** not run; level 1 was the brief.
- **Spectral periods and 2475 yr:** not run (DECISIONS: final run only).

## 8. Rerun

```bash
conda activate psha_renta
cd /data/PyCharmProjects/psha_chile/psha_chile8
bash hazard/run_all.sh                 # builds every job; unchanged ones keep their calc id (FORCE=1 reruns)
python hazard/branches.py              # branch tables
python hazard/check_tree.py            # level 1
python hazard/trees.py                 # family trees and combinations
python hazard/tornado_final.py         # both tornado sets
python hazard/tables.py                # jobs.csv, ref_pga475.csv
```

`run_all.sh` sets `PYTHONPATH` to the oq-engine checkout: the editable install does not map the new `openquake.pfd` subpackage, and `oq` fails without it. The entry scripts need the same `PYTHONPATH` to read the datastores.

## 9. Preliminary tornado figures, comparison with psha_chile6, decisions (16 Nov, afternoon)

**Figures** (`hazard/tornado_prelim.py` → `hazard/out/tornado_prelim/<city>.png` and `.csv`; style in `hazard/FIGURE_STYLE_tornado.md`). Preliminary, for the 17 Nov slides; more levels will follow.
- **Bars:**
  - vertical bars, one per level, ordered by the change of the total PGA 475 yr;
  - levels below 1 % left out, at most 18;
  - thick bar = all tectonic settings, pale bar = within tectonic setting.
- **Markers:**
  - dots = branches, the reference drawn and labelled at 0;
  - hollow diamond = the average of the level, with the curves of its branches averaged at equal weights.
- **GMMs:**
  - one level per set and setting: GMM-1R (the current tree, NGA-Sub + Montalva, round 1), GMM-FIT (GM1 top four), GMM-CSN (MASCSN26), GMM-GEM (GEM South America);
  - the branches are the single models, read from the realizations of each set job (identical to the single-GMM jobs of GMM-1R).
- **Level and branch names:**
  - IF / IS / CR prefixes;
  - segmentation, rate model, geodetic coupling χ, (a, b) uncertainty, b per segment, MFD shape, declustering (full / GK74 / NN), rupture scaling, GMM truncation, spatial pattern;
  - with faults, fault database (GEM / CSN / CSN-Ṁ₀), fault linkage (multi-fault / single-fault), max. jump distance, aseismic coefficient ψ, fault depth, background rates, background MFD.

**Reference PGA 475 yr, all three families** (`hazard/out/ref_compare.csv`, g):

| | Iqu | Cal | Ant | Cop | LSe | Val | SCe | SPe | Con | Puc | PMo | Hor | Ays | PWi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| psha_chile6 (GMM-1R) | 1.11 | 0.82 | 1.33 | 1.02 | 1.34 | 1.37 | 0.80 | 0.74 | 1.24 | 0.51 | 0.63 | 0.64 | 0.50 | 0.10 |
| now, GMM-1R | 1.03 | 0.68 | 1.24 | 0.88 | 1.29 | 1.28 | 0.74 | 0.71 | 1.12 | 0.48 | 0.53 | 0.60 | 0.50 | 0.07 |
| now, GMM-FIT | 0.85 | 0.52 | 1.02 | 0.67 | 0.99 | 1.06 | 0.55 | 0.55 | 0.93 | 0.43 | 0.44 | 0.56 | 0.49 | 0.07 |

- **New source model** (both on GMM-1R): −4 to −17 %; −29 % at Puerto Williams, where the hazard is small.
- **New GMMs** (GMM-FIT against GMM-1R): a further −16 to −25 % from Iquique to Concepción, −2 to −9 % in the far south.
- **Geodetic branch:** the moment rate is unchanged (χ, plate rate, areas); its MFD shape moved with b and the Mmax / corner rules of 15 Nov. The geodetic level rose from 1.2 % (psha_chile6) to 13 % mainly through the seismic branch; S1 is asked to confirm.

**Decided by Pablo (16 Nov):**
- **No tornado level:**
  - fit floors: the fits are built stable against the floor;
  - fault Mmax: follows from the Mmax fit;
  - the Antarctic interface source: always on.
- **Crustal fault MFD shapes:** already in the runs (the single-fault level); most will be dropped.
- **Figure conventions:**
  - averages at equal weights; logic-tree weights later;
  - GMM set names GMM-1R / FIT / CSN / GEM;
  - `strict = false` in the hazard jobs.
- **To be added as levels:**
  - Mmax pad 0 / 0.2 / 0.4 for interface (segments and margin) and in-slab (S1, S2);
  - in-slab declustered rates (S2);
  - in-slab one layer, lower depth and rupture geometry (C15, through C14);
  - the crustal items sent to S3 (section ids with depth, depth sources, multi-fault for Magallanes–Fagnano and arc segments, jumps incl. secondary traces, background–fault comparison, Mmax alternatives).
- **Every branch keeps source Mmin 5.5** (first bin centre), so the levels stay comparable.
- **To check:** GMM-CSN crustal (Arteta et al. 2023 alone) multiplies the crustal PGA by about 5 at Concepción and Puerto Montt.
- **Left for the full model:** the ≥ 5 % verdicts, logic-tree weights, faster interface jobs.

**Adding a level:**
1. The family session writes its new branches into a new dated NRML folder, with the reference files identical and a `tornado` block in `branches.json`.
2. S5 points `hazard/config.py` at the folder and adds the rows to `hazard/jobs.py`.
3. Run `bash hazard/run_all.sh` (unchanged jobs keep their calc ids), then `python hazard/tornado_final.py` and `python hazard/tornado_prelim.py`.

## 10. Interface 2026-11-16c and in-slab 2026-11-16c/d (16 Nov, evening)

- **Inputs:** interface `model/interface/nrml_2026-11-16c` (S1, fits 2026-11-16f; margin files byte-identical, the 168 segment files changed); in-slab `model/inslab/nrml/2026-11-16c` (S2 and C15; every file of 2026-11-16b unchanged) and the tornado rows of `nrml/2026-11-16d` (declustered rates).
- **Jobs run (calcs 597–613):** t_if_pad02 (base of the pad level: margin + segments 0.5 / 0.5), t_if_pad00, t_if_pad04, t_if_seg, t_if_b_shared, t_if_b_margin, t_is_cut, t_is_pad00, t_is_pad04, t_is_one_layer (C15), t_is_lower_depth (0.65), t_is_msr_ah, c_if_small, c_all_small, f_if_tree (35 min), t_is_decl_gk, t_is_decl_nn. Margin-only and in-slab reference jobs kept their calc ids. check_tree level 1: PASS.
- **Crustal:** not rerun. S3 rewrote the multi-fault and sections files of `2026-11-16e` at 15:44 (rebuild in progress); the crustal jobs keep calcs 538–591 on the earlier files (note in each build.json).
- **New levels, change of the total PGA 475 yr (%):**

| row | Iquique | Antofagasta | Copiapó | La Serena | Valparaíso | Santiago | Concepción | Puerto Montt |
|---|---|---|---|---|---|---|---|---|
| IF · Mmax pad +0 | −1.5 | −1.7 | −2.6 | −1.9 | −1.5 | −1.3 | −2.2 | −1.8 |
| IF · Mmax pad +0.4 | 1.2 | 1.3 | 2.2 | 1.5 | 1.0 | 1.0 | 1.5 | 1.5 |
| IF · segmentation (new segments) | −7.6 | −18.2 | −7.0 | −2.8 | −2.2 | −5.0 | −13.4 | −19.4 |
| IS · declustering GK74 | 4.5 | 2.6 | 4.7 | 5.6 | 3.1 | 6.6 | 1.3 | 1.2 |
| IS · declustering NN (rates alone, against the NN pattern) | −0.4 | −0.3 | −0.3 | −0.8 | −0.5 | −0.3 | −0.2 | −0.1 |
| IS · layers (one, C15) | −1.7 | 0.0 | −0.6 | 0.0 | −0.6 | −3.8 | −0.5 | −0.4 |
| IS · rupture scaling Allen–Hayes | −1.4 | −1.0 | −1.6 | −1.9 | −1.1 | −1.7 | −0.5 | −0.4 |
| IS · lower depth 0.65 | −0.6 | −0.4 | −0.8 | −1.3 | −0.6 | −0.6 | −0.3 | −0.2 |
| IS · Mmax pad +0 / +0.4 | −0.4 / 0.3 | −0.3 / 0.3 | −0.5 / 0.5 | −0.3 / 0.2 | −0.3 / 0.3 | −0.5 / 0.4 | −0.1 / 0.1 | 0 / 0 |
| IS · MFD shape truncated | −0.2 | −0.1 | −0.2 | −0.3 | −0.1 | −0.3 | −0.1 | −0.1 |

- **Reading:** the Mmax pad is small for both families (≤ 2.6 % interface, ≤ 0.5 % in-slab). In-slab declustering is shown in two levels: IS · spatial pattern (NN pattern, full rates, against the reference) and IS · declustering (rates alone): GK74 against the reference (same GK pattern), NN against the NN-pattern job, since S2's NN-rates file also carries the NN pattern. The rates alone: GK74 +1 to +7 %, NN below 1 %; the NN pattern −6 to +5 %. The average of IS · declustering is the mean of its changes and 0 (two bases). Figures: `out/tornado_prelim/<city>.png` (redrawn), tables `out/tornado/`, trees `out/trees/`.

## 11. Crustal 2026-11-16g (16 Nov, night)

- **Input:** `model/crustal/nrml/2026-11-16g/` from CURRENT.md (CR handoff `handoffs/2026-11-16_CR_to_HAZ.md`): strict UCERF3 rupture set, thickness tags t10 / t20, equal weights, B14 nodal planes. The 16e results (calcs 538–591) are superseded.
- **Jobs (calcs 614–642):** t_cr_ref (71 s), 19 rows, f_cr_tree as one job (84 branches, 344 s), GMM rows and truncation. Rows on the single-fault system (class Mmax pad single-fault, fault Mmax pad) are measured against t_cr_segmented. jump20 is gone; depth20 is now seismogenic thickness 20 km.
- **Crustal reference PGA 475 yr (g):** Iquique 0.301, Santiago centro 0.133, Concepción 0.138, Pucón 0.396, Puerto Montt 0.106, Hornopirén 0.658, Puerto Aysén 0.564, Puerto Williams 0.074.
- **Change of the total PGA 475 yr (%), crustal source rows:**

| row | Iquique | Santiago centro | Concepción | Pucón | Puerto Montt | Hornopirén | Puerto Aysén | Puerto Williams |
|---|---|---|---|---|---|---|---|---|
| with faults: no | -2.4 | 0.7 | 0.1 | -30.2 | 0.7 | -52 | -74.6 | nan |
| fault linkage: single-fault | 0 | -0 | -0 | 0.4 | -0 | 3.7 | -1.8 | -0 |
| fault database: CSN | -1.3 | 0 | -0 | 6.7 | -0.1 | 7.2 | 43.6 | 22 |
| fault database: CSN-Ṁ₀ | 1.2 | 0 | -0 | 5 | -0.1 | -14.1 | 8.9 | -5.4 |
| ψ 0.6 | -0.6 | -0 | 0 | -6 | -0 | -8.6 | -11.8 | -13.9 |
| ψ 1.0 | 0.6 | 0 | 0 | 5.3 | 0 | 7.5 | 11.2 | 11.2 |
| thickness 20 km | 0.1 | 0 | 0 | 6.1 | 0 | 2 | 7.8 | 23.8 |
| jump 5 km | 0 | -0 | -0 | 0.7 | -0 | 5.2 | 0.3 | -0 |
| jump 10 km | 0 | -0 | -0 | 0.7 | -0 | 3.1 | 0.4 | -0 |
| secondary traces linked | 0 | 0 | 0 | -0 | 0 | -0.7 | -48.2 | -0 |
| fault Mmax +0.2 (single-fault) | -0.4 | -0 | -0 | -4.1 | 0 | -8.2 | -10.8 | -9.5 |
| fault Mmax +0.4 (single-fault) | -0.8 | -0 | -0 | -8.5 | 0 | -15.8 | -22.4 | -20.7 |
| background rates declustered | -0.1 | -0.1 | -0.1 | -0.3 | -0.3 | -0.1 | -0.1 | -0 |
| spatial pattern NN | 0.1 | -0.1 | 0.1 | -0.1 | -0.2 | -0 | 1.4 | 0 |

- **Reading:** the background rows (rates, pattern, MFD, class Mmax pad) move the crustal hazard by up to 15 % within the family (Santiago, Iquique) but the total by ≤ 1 %: where the background matters the crustal share is small, and where the crustal hazard dominates (Pucón to Puerto Williams) the faults carry it.
- **Figures:** reduced tornado `out/tornado_prelim/`, full tornado for every city `out/tornado_full/` (PNG and PDF), matrix `out/tornado_matrix/matrix.png`; trees `out/trees/` now with the crustal tree.

## Full job list

| job | calc_id | run_time_s | n_realizations | skip |
|---|---|---|---|---|
| t_if_ref | 522 | 291 | 12 |  |
| t_is_ref | 523 | 133 | 4 |  |
| f_if_tree | 524 | 3432 | 864 |  |
| f_is_tree | 525 | 224 | 8 |  |
| t_if_seg | 526 | 177 | 12 |  |
| t_if_geo08 | 527 | 278 | 12 |  |
| t_if_geo07 | 529 | 303 | 12 |  |
| t_if_geo09 | 531 | 276 | 12 |  |
| t_if_ab_p05 | 533 | 280 | 12 |  |
| t_if_ab_p95 | 534 | 277 | 12 |  |
| t_if_b_shared | 535 | 182 | 12 |  |
| t_if_b_margin | 536 | 185 | 12 |  |
| t_if_cut | 537 | 281 | 12 |  |
| t_if_decl_gk | 539 | 276 | 12 |  |
| t_if_decl_nn | 540 | 275 | 12 |  |
| t_if_msr_strasser | 541 | 129 | 4 |  |
| t_if_msr_thingbaijam | 542 | 122 | 4 |  |
| t_if_msr_allenhayes | 543 | 135 | 4 |  |
| t_is_ab_p05 | 544 | 122 | 4 |  |
| t_is_ab_p95 | 545 | 121 | 4 |  |
| t_is_pattern_nn | 546 | 121 | 4 |  |
| t_is_one_layer |  |  |  | C15 open: one-layer hypocentre to be fixed first |
| t_is_lower_depth |  |  |  | C15 open: no lower-depth files yet |
| t_if_gmm_ag20 | 547 | 248 | 3 |  |
| t_if_gmm_parker | 548 | 246 | 3 |  |
| t_if_gmm_kuehn | 549 | 261 | 3 |  |
| t_if_gmm_montalva | 550 | 259 | 3 |  |
| t_if_set_gm1top4 | 551 | 288 | 12 |  |
| t_if_set_mascsn26 | 552 | 315 | 12 |  |
| t_if_set_gem_sam | 553 | 269 | 9 |  |
| t_if_trunc25 | 554 | 275 | 12 |  |
| t_if_trunc40 | 555 | 276 | 12 |  |
| t_is_gmm_ag20 | 556 | 112 | 1 |  |
| t_is_gmm_parker | 557 | 112 | 1 |  |
| t_is_gmm_kuehn | 558 | 111 | 1 |  |
| t_is_gmm_montalva | 559 | 116 | 1 |  |
| t_is_set_gm1top4 | 560 | 121 | 4 |  |
| t_is_set_mascsn26 | 561 | 118 | 2 |  |
| t_is_set_gem_sam | 562 | 117 | 2 |  |
| t_is_trunc25 | 563 | 122 | 4 |  |
| t_is_trunc40 | 564 | 120 | 4 |  |
| t_cr_ref | 538 | 147 | 4 |  |
| t_cr_decl_nn | 568 | 142 | 4 |  |
| t_cr_fit_cut | 569 | 135 | 4 |  |
| t_cr_rates_declustered | 570 | 143 | 4 |  |
| t_cr_no_faults | 571 | 174 | 4 |  |
| t_cr_segmented | 572 | 152 | 24 |  |
| t_cr_psi060 | 573 | 143 | 4 |  |
| t_cr_psi100 | 574 | 144 | 4 |  |
| t_cr_depth20 | 575 | 145 | 4 |  |
| t_cr_jump5 | 576 | 143 | 4 |  |
| t_cr_jump10 | 577 | 143 | 4 |  |
| t_cr_jump20 | 578 | 144 | 4 |  |
| t_cr_db_B | 579 | 148 | 4 |  |
| t_cr_db_Bmm | 580 | 145 | 4 |  |
| f_cr_tree_a | 590 | 585 | 312 |  |
| f_cr_tree_b | 591 | 236 | 24 |  |
| t_cr_gmm_ask14 | 582 | 140 | 1 |  |
| t_cr_gmm_bssa14 | 583 | 124 | 1 |  |
| t_cr_gmm_cb14 | 584 | 134 | 1 |  |
| t_cr_gmm_cy14 | 585 | 132 | 1 |  |
| t_cr_set_mascsn26 | 586 | 126 | 1 |  |
| t_cr_set_gem_sam | 587 | 126 | 3 |  |
| t_cr_trunc25 | 588 | 144 | 4 |  |
| t_cr_trunc40 | 589 | 144 | 4 |  |
| c_all_small | 567 | 403 | 192 |  |
| c_if_small | 565 | 290 | 24 |  |
| c_is_small | 566 | 203 | 8 |  |
