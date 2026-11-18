# PLAN

Chile PSHA manuscript, round psha_chile8. Agreed 8 Nov 2026. Current step marked ←.
Tick a box when its "done when" holds. Detail of each step lives in its task brief (`tasks/`).

## 0. Clean working setup
- [x] psha_chile8 with `catalog/`, `fits/`, `model/`, `runs/`, `figures/`, `tasks/`
- [x] PLAN.md, DECISIONS.md, LEARNINGS.md, CLAUDE.md, WORKLOG.md, FIGURES.md, DATA.md in place
- [x] note of the psha_chile6/7 results still needed (`PSHA6_NEEDED.md`)
- [x] project memory reduced to a pointer to psha_chile8

## A. Rebuild the catalog from scratch
- [x] A0 new catalog module inside `psha_chile8/catalog/`
- [x] A1 Sergio's rules written down (no Cabello from 1900 on, his source order) → DECISIONS
- [x] A2 source catalogs collected, each frozen as a dated file
- [x] A3 events matched across catalogs once (one ID per event)
- [x] A4 magnitude, location and mechanism chosen per event, each by its own priority rule
- [x] A5 Mw conversion redone, checked against events with known Mw
- [x] A6 large events reviewed one by one against the literature
- [x] A7 events classified with class weights (interface, in-slab, crustal, outer rise) and sub-classes; new class names for events and source models
- [x] A8 final catalog frozen, dated, with a decisions note (`catalog/frozen/2026-11-14/`)
- [x] A9 catalogue revision after S3: Aysén 1960 Mw, split no-depth events in the crustal classes, arc–Patagonia boundary; new frozen run `2026-11-16` and refits (`tasks/A9_catalog_revision.md`; sessions A6, A7, B11/B12) (catalogue frozen `catalog/frozen/2026-11-16/`, 16 Nov; phase-1 test fits skipped; reruns on it, Pablo 16 Nov: B11 fits (done 16 Nov, `fits_2026-11-16.csv`), B12 declustered catalogues and fits (done 16 Nov, `fits_declustered_2026-11-16.csv`), C14 depth model, B14 nodal planes, then S1 (done 16 Nov, `model/interface/nrml_2026-11-16/`), S2 (done 16 Nov, `model/inslab/nrml/2026-11-16/`; Calama engine run not yet), S3; GM1 stays) (closed 16 Nov: final catalogue `catalog/frozen/2026-11-16c/` (Scotia rule, crustal events outside the grid); fits `fits_2026-11-16f.csv` with the interface Mmax by the one rule, pad tables `_pad00`, `_pad04`)
- [x] A10 final catalogue: the batch of 17 Nov (overrides, ISC-GEM literature mechanisms before 1976, Valdivia 1960 mechanism, three 1960 events to interface), frozen `catalog/frozen/2026-11-17f/` (CAT, 17 Nov; handoffs `2026-11-17_CAT_to_FITS.md`, `_CAT_to_CR_HAZ.md`)
- [x] A11 duplicates: the A3 review lists and sweeps of Mw ≥ 4 and Mw ≥ 6 decided pair by pair; 44 events merged (22 reviewed in `catalog/duplicates.csv`, 22 single-agency ISC copies by rule); conversions with a third depth group below 150 km (FITS note); frozen `catalog/frozen/2026-11-17g/` as the final catalogue (CAT, 18 Nov; handoff `2026-11-18_CAT_to_FITS_17g.md`)

## B. Earthquake statistics
- [x] B9 method comparison: completeness (incl. spatial), b-value methods, with / without declustering (`explore/B9/REPORT.md`, 14–15 Nov)
- [x] B10 method per source type picked and documented (DECISIONS, Statistics, 15 Nov)
- [ ] B11 fitting code, tested on synthetic catalogs (known Mc, b, a recovered) (code, tests, method comparison and fits in `fits/`, 15 Nov; for Pablo to review: `fits/FITS.md`)
- [x] B12a fits on the full catalogue: crustal, interface, in-slab classes (shallow, intermediate, Jujuy nest) (B11, `fits/tables/fits_2026-11-15.csv`)
- [x] B12 declustered catalogues (Gardner–Knopoff, nearest neighbour) and their fits with the B11 methods, for the declustered interface branch and the smoothed patterns (`tasks/B12_declustered.md`; before S2 and S3) (`catalog/declustered/`, `fits/tables/fits_declustered_2026-11-15.csv`, `fits/DECLUSTER.md`, 15 Nov; method to be picked by Pablo; step 0 refit `fits_2026-11-15b.csv`)
- [x] B14 focal mechanisms per class: nodal-plane distribution (normal / reverse / strike-slip shares, one plane per type, both nodal planes) from the catalogue mechanisms, for the OpenQuake point sources; not a tornado factor; used from S5 (`tasks/B14_mechanisms.md`) (`model/mechanisms/npd_2026-11-15.csv`, report `model/mechanisms/REPORT_B14.md`, 15 Nov; rerun on the A9 catalogue `npd_2026-11-16.csv`, 16 Nov); on catalogue 2026-11-16c `npd_2026-11-16c.csv`, backarc and Patagonia below 15 mechanisms (pooled or own: Pablo)
- [ ] B15 refit on the final catalogue named in CURRENT.md after A11: full, declustered (`gk_family` and `nn_family` until the team picks one; check the `nn_family` implementation first), pad tables; new fits date in CURRENT.md (runbook step 3) ←
- [ ] B16 focal mechanisms and class shares per cell on the final catalogue (FITS; `model/mechanisms/npd.py`, B14 close-out traps)
- [ ] C16 in-slab depth cells on the final catalogue with the C15 class-weight method, compared by eye against `depth_cells_2026-11-16.csv` (FITS; `model/inslab/depth.py`, `run.py`, `options.py`; C15 close-out traps)

## C. In-slab double-zone model
- [x] C14 in-slab depth model: Riedel-Hornig et al. (2026) frozen and benchmarked; three layers below the slab top, weights and hypocentres per cell from well-located events (Jujuy nest removed first); the double zone shows through the weights (`model/inslab/REPORT_C14.md`, run 2026-11-15e: zone to 0.475 of the Slab2 thickness, three slices for the hypocentre distribution, kernel weights; 15 Nov) (final run 2026-11-15e; rerun 2026-11-16 on the A9 catalogue, identical)
- [x] C15 one layer against three tested in the tornado; lower seismogenic depth and rupture geometry options decided (`tasks/C15_inslab_depth_options.md`; depth part done 16 Nov, `model/inslab/REPORT_C15.md`, run 2026-11-16d: events with their class weights, one layer at top + 0.243 × thickness, lower-depth options 0.65 and 0.615; source files and geometry options in S2, hazard rows in S5); tornado files built by S2 in `model/inslab/nrml/2026-11-16c/` (one layer 0.243, lower depth 0.65, AllenHayesIntraslab), rows running in S5 (16 Nov). Open: three-layer weights switch at the 50 km slab-top line; heavy top slice where the top is 50–70 km

## D. Magallanes–Fagnano
- [x] D16 fault database: GEM/SARA faults cleaned (fault properties only, area-source fields removed, plain field names, source per value), compared with CHAF (Maldonado et al. 2021) for important missing faults (exploration, nothing added), Magallanes–Fagnano segments, overlap, slip rate, Mmax, single or joined source (`tasks/D16_fault_database.md`; runs before B13; database `data/faults/faults_2026-11-15.gpkg`, report `model/faults/REPORT_D16.md`, 15 Nov) (final: `data/faults/faults_gem_extra_2026-11-15.shp`, 138 faults)
- [x] D16b fault database B: MASCSN26 faults for Chile (slip rate and Mmax restored from its OpenQuake files and checked against its report) plus GEM outside Chile; A against B per class and near the cities (`tasks/D16b_fault_options.md`; database `data/faults/faults_B_2026-11-15.gpkg`, report `model/faults/REPORT_D16b.md`, 15 Nov)

## S. Source models (OpenQuake), after C14 and the fault database (no outer-rise source)
- [x] S1 interface: complex-fault sources for the full margin and the four segments; seismic branch from the B11 fits (tapered and cut shapes, (a, b) branches, the three b options) and geodetic branch (coupling χ); rupture scaling, 10–50 km; Antarctic interface (geodetic only) (`tasks/S1_interface.md`; declustered branch from B12) (`model/interface/REPORT_S1.md`, 240 NRML files and `branches.json`, reference tree 72 files × 2 scaling relations, tests pass, both OpenQuake check jobs read every file; 15 Nov; rerun on the A9 fits 2026-11-16 into `nrml_2026-11-16/`, 216 paths, 16 Nov)
- [x] S2 in-slab: point sources on the in-slab grid for shallow, intermediate and Jujuy nest; 2-D smoothed pattern scaled to the B11 rates; three-layer depths and seismogenic depths from C14 (and the one-layer version); nodal planes (`tasks/S2_inslab.md`) (NRML 72 files and tests in `model/inslab/`, report `REPORT_S2.md`, 15 Nov; all 72 files read by the OpenQuake parser, rates as built)
- [x] S3 crustal model: fault MFDs for databases A and B (two variants), smoothed background per class, the join of DECISIONS (background above 6.0 = fit minus faults, bulge reported), checked against the catalogue fits (`tasks/S3_crustal.md`; replaces the B13 brief) (`model/crustal/REPORT_S3.md`, 15 Nov; kernel n = 5 every class; arc and Patagonia bulge)
- [x] S4 crustal OpenQuake sources: background point sources and simple-fault sources for every branch, fault logic tree (in `tasks/S3_crustal.md`, same session) (`model/crustal/nrml/`, 124 files and `branches.json`, all read by OpenQuake's converter with the rates of the tables; no-faults job calc 501 ran; ticked on the parse check, the fault-database jobs skipped (Pablo))
- [x] S5a interface and in-slab hazard jobs: psha_chile7 hazard code ported, references, family trees, tornado rows, two-family post-processing (`tasks/S5a_assembly_if_is.md`; crustal in S5b) (`hazard/REPORT_S5a.md`, 16 Nov; 66 jobs, calcs 522–591; check_tree level 1 passes; the crustal reference, rows, tree (in two parts) and GMM rows also ran, S3 note; C15 rows skipped)
- [x] S5b crustal hazard jobs on `model/crustal/nrml/2026-11-16e/` (reference, 13 rows, tree in two parts, GMM rows; 16 Nov, `hazard/REPORT_S5a.md`). Section ids now carry database and depth (calc 596), so the tree runs as one job
- [x] S3b crustal rebuild on the strict UCERF3 rupture set: Liquiñe–Ofqui multi-fault by SHERIFS, Fagnano and Mmax-pad rows, `model/crustal/nrml/2026-11-16g/` (84 tree branches, 20 tornado rows, equal weights, t10 / t20; parse check passed; `handoffs/2026-11-16_CR_to_HAZ.md`, 16 Nov) ← S5 runs the crustal rows and tree on 16g
- [x] S5c all three families in the tornado on the current folders (interface `nrml_2026-11-16c`, in-slab `2026-11-16c` + `16d`, crustal `2026-11-16g`; calcs 597–642; reduced, full and matrix tornado, curves and shares per city; `hazard/REPORT_S5a.md` section 11, 16 Nov)
- [ ] S5 final source logic tree: decide whether to refit on catalogue `2026-11-16e` first; equal weights; B14 nodal planes into the in-slab sources (mixed per cell by class share); geodetic branches on the full catalogue only; crustal source Mmin 5.0 or 5.5; checks: rates per class against the fits, moment rates, the 14 cities against psha_chile6

## E. New tornado round
- [x] E17 tornado verdicts → final logic tree (verdicts by the 10 % spread rule in DECISIONS, Logic tree, 17 Nov; `hazard/out/verdicts_2026-11-17.md`; team items open: declustering algorithm and declustered rates, fault database, fault Mmax, fault linkage, interface b per segment, GMM set and truncation; geodetic 0.5 / 0.5 after IF's explanation)
  - to settle with the verdicts: rate convention (full catalogue intended), geodetic weight where it is far above the seismic branch (N(≥ 8) × 1.3 margin, × 1.6–4.8 segments), the arc bulge (faults 3.3 × the arc fit), Aysén Mmax comparison case, Arica 1868 outside every segment, GMM-CSN crustal (Arteta 2023) check, GMM selection (GM2)
  - include the old GMM sets (GEM South America model, official Chilean hazard map) as a tornado factor, to tell whether the hazard difference to those models comes from the GMMs or from the source model

## F. Freeze the model
- [ ] F18 recipe frozen (methods, rules, logic tree); rebuild from configs gives the same sources; tests pass; logic-tree figure

## G. Hazard runs
- [ ] G19 cities: curves, regime shares, uncertainty, disaggregation
- [ ] G20 full grid: mean and fractile maps, PGA, SA(0.2), SA(1.0), 475 and 2475 yr

## H. Pseudo-prospective testing
- [ ] H21 catalog cropped at 2009-12-31, training models built with the frozen recipe (faults, geodetic unchanged)
- [ ] H22 branches converted with hazard2csep, tested on 2010–2022 per source family
- [ ] H23 test of the spread between branches; results reported, not fed back into the tree

## I. Figures
- [ ] I24 figure list (one message each) in FIGURES.md; main and discussion figures final
- [ ] I25 results deck for the co-authors, in parts (beamer, `presentations/261116_psha8_results/`): part 1 catalogue, statistics and the Cabello / Candia comparison [x] (16 Nov; comparison in `explore/P1/`); ground-motion part [x] (16 Nov); part 2 source models (S1–S5, C14); part 3 tornado (E17); part 4 hazard results

## J. Paper
- [ ] J25 outline and key messages → methods → results → discussion → intro, conclusions, abstract
- [ ] J26 every number checked against the tables; co-author round

## K. Clean public repo, release, submit
- [ ] K27 clean public repo from the finished work; pinned environment; regression test against the paper numbers
- [ ] K28 data and code archive with DOI; WORKLOG becomes the decisions register, FIGURES.md the figure manifest
- [ ] K29 submitted

## GM. Ground-motion models
- [x] GM1 residuals of the subduction GMMs on the Bastías et al. (2026) database (`tasks/GM1_gmm_residuals.md`, `gmm/REPORT_GM1.md`, 15 Nov)
- [ ] GM2 GMM selection and weights (Pablo)
