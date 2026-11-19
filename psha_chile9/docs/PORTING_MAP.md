# Porting map: psha_chile8 → psha_chile9

For each stage: the steps psha_chile8 ran, in order; the psha_chile8 code and report behind each; where it goes; what changes on the way (decision ids); the open questions the step answers; what it hands on. Sessions port, clean, apply the decisions, answer the questions, rerun, and compare their check figures with psha_chile8 by eye (design section 9). Paths are relative to `/data/PyCharmProjects/psha_chile/`. A path marked "(locate)" was referenced in psha_chile8 but not found in its folder; find it before porting.

Order of work: SETUP → DATA and CAT steps 1–6 in parallel → CAT step 7 (needs DATA) → STATS → IF, IS, CR in parallel → GMM (any time) → HAZ → FIG. Method notes are written just before each stage starts (`docs/methods/<STAGE>.md`); classification is done.

## SETUP
| step | what | from | to |
|---|---|---|---|
| S1 | references into `refs/`, index `docs/REFERENCES.md` | `refs/`, `psha_chile8/REFERENCES.md`, `psha_chile8/catalog/LITERATURE.md` | brief SETUP_01 |
| S2 | conda env `psha9`, OpenQuake 3.27 on pansito, rs1, rs28, rs37; pinned `environment.yml` | psha_chile8 `hazard/remote.sh` (machine access) | brief SETUP_02; D-ENV-01 |
| S3 | raw inputs copied (not moved) into `psha_chile9/data/raw/` | the files listed under DATA and CAT | with DATA and CAT |

## DATA (`src/psha9/data_processing/`; no psha_chile8 equivalent, geometry was made inside model code)
| step | what | psha_chile8 inputs and code | changes | questions |
|---|---|---|---|---|
| D1 | raw inputs: Slab2 top, thickness, uncertainty; Nazca and Antarctic trenches; PB2002 (SC/AN); Chile outline; arc polygon; fault databases; CHAF; Riedel-Hornig; basemap | `psha_chile8/data/sam_slab2_{dep,thk,unc}_*.xyz`, `sam_nazca_trench_*.shp`, `pb2002_antarctic_trench_*.geojson`, `chile_outline_*.shp`, `intraarc.shp` (locate), `faults/`, `chaf_pangea_*`, `sara_active_faults_*`, `riedel_hornig_primary_*.csv`; `data/basemaps/basemap_chile_gray/` | copy into `data/raw/`; shapes as GeoJSON (Q-8) | – |
| D2 | shapes Pablo draws (`data/raw/shapes/`): crustal polygons forearc, arc, backarc, Patagonia (over the psha_chile8 seismicity); collection and forecast areas; interface segment limits incl. the northern end; in-slab and crustal grid outlines; cities | start from `psha_chile8/data/class_domains_2026-11-18.geojson`, `crustal_grid_01_*.csv`, `inslab_grid_01_*.csv`, `hazard/config.py` (cities) | forearc polygon starts east of the Chile Ridge events (D-CLS-09); grids extended over Slab2 / east of the arc | Q-25, Q-26, Q-40, Q-54, Q-55 |
| D3 | build: class domains, interface segment edges and areas, grids (outline + spacing), site files (16 cities, 0.05° grid) | geometry parts of `model/interface/if_geom.py`; grids of `model/inslab`, `model/crustal`; `hazard/grid.py`, `hazard/sites/` | one run `runs/data/data-01` read by every later stage (design 4.2) | – |
Hands on: polygons and grids to CAT (step 7), STATS, IF, IS, CR, HAZ.

## CAT (`src/psha9/catalog/`; method note to write: sources, matching, merge, locations and depths, magnitudes; classification in `docs/methods/CLASSIFICATION.md`)
| step | what | psha_chile8 code, files, reports | changes | questions |
|---|---|---|---|---|
| C1 | read sources (frozen tables of 10–11 Nov) | `catalog/read.py`, `fetch.py` (not rerun), `profile.py`; `catalog/sources/*.csv`, `MANIFEST.csv`; `SOURCES.md` | sources and split year 1904 (D-CAT-02, 03, 07); CSN in ISC only if needed | Q-36, Q-41 |
| C2 | match: one id per earthquake | `catalog/match.py`; `merged/links_*`, `windows_*`; `REPORT_A3-A5.md`, `merged/METHOD.md` | identity links, windows, no magnitude (D-CAT-08); duplicates merged (D-CAT-09, `duplicates.csv`) | Q-38 |
| C3 | locations and depths | `catalog/locate.py`, `locate_check.py`; `PREFERENCES.md`; `RULES_LOCATION_MAGNITUDE.md` | orders per property in config (D-CAT-05, 12–14); defaults as no depth | Q-42 |
| C4 | magnitudes: offsets, conversions, one Mw per event, σ, dither | `catalog/magnitude.py`, `magnitude_check.py`; `MAGNITUDES.md` (project copy) | native only (D-CAT-15); D-MAG-01–12; dither test (D-MAG-08) | Q-43, Q-44, Q-67 |
| C5 | large events and overrides | `catalog/a6.py`; `overrides_A6.csv`, `named_events.csv`, `A6/REPORT.md`, `NOTE_SRuiz_2026-11-10.md` | overrides applied last (D-CAT-17); Pablo's calls rechecked (D-CAT-19); Pica, Taltal, 1907 (D-CAT-20) | Q-38, Q-45 |
| C6 | non-earthquakes | flags in the sources | own class (D-CAT-10) | Q-39 |
| C7 | classification (needs DATA) | `catalog/classify.py`, `classify_check.py`; `CLASSIFICATION.md` (project copy) | D-CLS-01–13; band from data and calibration (method note) | Q-46, Q-60, Q-68, Q-69 |
| C8 | check figures | `catalog/fig_classes.py`, `fig_mechanisms.py`, `fig_positions.py`, `sources_figs.py`, `plots/maps.py` | ported as code (D-FIG-01); acceptance tests (D-MAG-12) | – |
Compare with: `catalog/frozen/2026-11-17g/` (D-CAT-01). Hands on: `runs/catalog/cat-NN/` (events, weights, σ, mechanisms) to STATS.

## STATS (`src/psha9/stats/`; reports `FITS.md`, `FITS_state_2026-11-18.md`, `fits/DECLUSTER.md`, `model/mechanisms/REPORT_B14.md`, `REPORT_C14`, `REPORT_C15`)
| step | what | psha_chile8 code | changes | questions |
|---|---|---|---|---|
| T1 | declustering (four algorithms per family) | `fits/decluster.py` | D-STA-13; NN parameters from the catalogue | Q-14 |
| T2 | completeness: Mc(t) per region, historical steps, checks | `fits/table.py`, `mc_maps.py` | D-STA-01–03 | Q-48, Q-49 |
| T3 | magnitude σ and the error weight | `fits/sigma.py` | D-MAG-09 | – |
| T4 | GR fits, both shapes, Mmax, corner, cluster bootstrap, checks | `fits/gr.py`, `run.py`, `compare.py`, `synth.py`, `domains.py` | output parameters, not bin lists (D-STA-11); periods per family (D-STA-05); weight-1 check (D-STA-15) | Q-50, Q-51, Q-52, Q-53, Q-61, Q-62 |
| T5 | declustered fits | `fits/run_declustered.py`, `figs_declustered.py` | full-catalogue table and Mmax | Q-13 |
| T6 | Mmax pad tables | `fits/run_pad.py` | – | – |
| T7 | geodetic construction for IF | `model/interface/geo_alt_*.py`, `geo_b_*.py`, `geo_cml_*.py`, `drafts/geodetic/` | IF_to_FITS note (project copy) | Q-11, Q-16, Q-56 |
| T8 | nodal planes per class, class shares per cell | `model/mechanisms/npd.py` | oblique as own type, two planes where two dominate (D-CR-05, D-IS-07) | Q-29 |
| T9 | in-slab depth model | `model/inslab/depth.py`, `bench.py`, `run.py`, `options.py` | class weights (D-IS-04) | Q-46, Q-59 |
| T10 | fit figures | `fits/figs.py` (FMD panels) | ported as code | – |
Hands on: `runs/stats/stats-NN/` (parameters per unit and branch, declustered catalogues, tables) to IF, IS, CR.

## IF (`src/psha9/interface/`; report `REPORT_S1_interface.md`)
| step | what | psha_chile8 code | changes | questions |
|---|---|---|---|---|
| I1 | geometry from DATA | `model/interface/if_geom.py` | segments from DATA; northern end | Q-55 |
| I2 | MFD lists from STATS parameters | `if_mfd.py`, `if_pad.py` | discretisation here, one last-bin rule (D-STA-11) | – |
| I3 | branches and NRML | `if_build.py`, `if_nrml.py` | builder per choice from `model.yaml` (design 7.1); depth rows, aspect ratio 2 (D-CLS-08, D-IF-06) | Q-12, Q-15, Q-47 |
| I4 | OpenQuake check, figures | `if_oqcheck.py`, `if_figs.py` | – | – |

## IS (`src/psha9/inslab/`; reports `REPORT_C14`, `REPORT_C15`, `model/inslab/REPORT_S2.md`)
| step | what | psha_chile8 code | changes | questions |
|---|---|---|---|---|
| N1 | patterns (kernel, calibration) | `model/inslab/is_smooth.py` | historical events in the map (D-IS-03) | Q-57, Q-58 |
| N2 | sources per cell, nest, depth distribution | `model/inslab/build.py`, `is_decl_rates.py` | one plane per sub-class (D-IS-07); dropped cells (D-IS-06) | Q-26 |
| N3 | tornado variants, check, figures | `is_tornado.py`, `oqcheck.py`, `figs_s2.py`, `figs.py` | variants from `model.yaml` | – |

## CR (`src/psha9/crustal/`; reports `CR_state_2026-11-18.md`, `model/crustal/REPORT_S3.md`, `model/faults/FAULTS.md`, `REPORT_D16.md`, `REPORT_D16b.md`)
| step | what | psha_chile8 code | changes | questions |
|---|---|---|---|---|
| R1 | fault databases A and B | `model/faults/curate.py`, `db.py`, `dbB.py`, `chaf.py`, `mascsn.py`, `faultquake.py`, `fagnano.py`, `geo.py`, `rates.py` | slip-rate review (D-CR-08) | Q-17, Q-23, Q-65 |
| R2 | background patterns and MFDs | `model/crustal/background.py`, `smooth.py`, `kernels.py` | planes by class polygon (D-CR-04); full / declustered (D-CR-02) | Q-57 |
| R3 | single-fault sources | `model/crustal/faults.py`, `pad.py` | one reference MFD shape in the tree (D-CR-11) | Q-19 |
| R4 | multi-fault rupture set and SHERIFS | `model/crustal/rupset.py`, `rupset_compare.py`, `multifault.py`, `mfsource.py` | rupture-set trials | Q-20, Q-22, Q-63 |
| R5 | join, arc and large-event checks | `model/crustal/join.py`, `arc.py`, `large.py`, `lower.py`, `fagnano_row.py` | the join meets in one bin (D-CR-13) | Q-21, Q-24, Q-28, Q-34, Q-35, Q-64 |
| R6 | build, NRML, OpenQuake check, figures | `model/crustal/build.py`, `nrml.py`, `oqcheck.py`, `figs_paper.py` (`figs_s3.py`, `figs_checks.py` retired) | builder per choice | Q-62 |

## GMM (`src/psha9/gmm/`; reports `SUMMARY_GM1_gmm.md`, `gmm/REPORT_GM1.md`)
| step | what | psha_chile8 code | changes | questions |
|---|---|---|---|---|
| G1 | residuals on the records (done; port only if rerun) | `gmm/records.py`, `screen.py`, `residuals.py`, `scores.py`, `summary.py`, `gm1_run.py`, `gm1_figs.py` | – | Q-30, Q-31, Q-32 |
| G2 | GMM sets for the jobs | `hazard/gmm_sets.py` | D-GMM-01–05 | – |

## HAZ (`src/psha9/hazard/`; report `hazard/REPORT_S5a.md`, verdicts `verdicts_2026-11-17_tornado.md`)
| step | what | psha_chile8 code | changes | questions |
|---|---|---|---|---|
| H1 | job settings and sites | `hazard/config.py`, `grid.py`, `hazard/sites/` | 16 cities (D-HAZ-05); sites from DATA | Q-33, Q-66 |
| H2 | trees and jobs from `tree.json` / `tornado.json` | `hazard/trees.py`, `branches.py`, `jobs.py`, `build.py`, `nrml.py`, `check_tree.py` | labels from the datastore (LEARNINGS) | Q-47 |
| H3 | runs on several machines | `hazard/remote.sh`, `run_all.sh`, `speed.py` | `psha9.hazard.remote` with check / push / run / status / pull / stop (design 6.1) | – |
| H4 | combine families, tables, shares | `hazard/combine.py`, `tables.py`, `post.py`, `shares.py` | exact rate-space combination (D-LT-03) | – |
| H5 | tornado, verdicts, figures | `hazard/tornado_final.py`, `tornado_full.py`, `tornado_matrix.py`, `verdicts.py`, `curves_city.py`, `shares_bar.py` (`tornado_prelim`, `_trial`, `_alt` not ported) | 10 % spread rule (D-LT-01) | – |

## FIG (`figures/`)
| step | what | psha_chile8 code | changes |
|---|---|---|---|
| F1 | plotting module | `plots/colors.py`, `plots/maps.py`, `plots/palettes.json`, `palette.py` | into `src/psha9/common/plots` (D-FIG-01, FIGURE_STYLE) |
| F2 | paper, supplement, presentation figures | the check-figure code of each stage; `FIGURES.md` (manifest) | one script per figure, reading runs |
