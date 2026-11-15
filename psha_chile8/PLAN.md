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

## B. Earthquake statistics
- [x] B9 method comparison: completeness (incl. spatial), b-value methods, with / without declustering (`explore/B9/REPORT.md`, 14–15 Nov)
- [x] B10 method per source type picked and documented (DECISIONS, Statistics, 15 Nov)
- [ ] B11 fitting code, tested on synthetic catalogs (known Mc, b, a recovered) ← (code, tests, method comparison and fits in `fits/`, 15 Nov; for Pablo to review: `fits/FITS.md`)
- [ ] B12 fits: crustal, interface, in-slab classes (shallow, intermediate, Jujuy nest)
- [ ] B13 faults and background join cleanly at M6 (domain-wide), for fault databases A and B (after D16 and D16b)

## C. In-slab double-zone model
- [ ] C14 in-slab depth model: Riedel-Hornig et al. (2026) frozen and benchmarked; three layers below the slab top, weights and hypocentres per cell from well-located events (Jujuy nest removed first); the double zone shows through the weights
- [ ] C15 one layer against three tested in the tornado; lower seismogenic depth and rupture geometry options decided

## D. Magallanes–Fagnano
- [ ] D16 fault database: GEM/SARA faults cleaned (fault properties only, area-source fields removed, plain field names, source per value), compared with CHAF (Maldonado et al. 2021) for important missing faults (exploration, nothing added), Magallanes–Fagnano segments, overlap, slip rate, Mmax, single or joined source (`tasks/D16_fault_database.md`; runs before B13)
- [ ] D16b fault database B: MASCSN26 faults for Chile (slip rate and Mmax restored from its OpenQuake files and checked against its report) plus GEM outside Chile; A against B per class and near the cities (`tasks/D16b_fault_options.md`)

## E. New tornado round
- [ ] E17 double-zone construction plus the choices reopened by the new catalog → final logic tree
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

## J. Paper
- [ ] J25 outline and key messages → methods → results → discussion → intro, conclusions, abstract
- [ ] J26 every number checked against the tables; co-author round

## K. Clean public repo, release, submit
- [ ] K27 clean public repo from the finished work; pinned environment; regression test against the paper numbers
- [ ] K28 data and code archive with DOI; WORKLOG becomes the decisions register, FIGURES.md the figure manifest
- [ ] K29 submitted
