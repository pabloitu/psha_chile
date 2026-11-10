# PLAN

Chile PSHA manuscript, round psha_chile8. Agreed 8 Nov 2026. Current step marked ←.
Tick a box when its "done when" holds. Detail of each step lives in its task brief (`tasks/`).

## 0. Clean working setup
- [ ] psha_chile8 with `catalog/`, `fits/`, `model/`, `runs/`, `figures/`, `tasks/`
- [ ] PLAN.md, DECISIONS.md, LEARNINGS.md, CLAUDE.md, WORKLOG.md, FIGURES.md, DATA.md in place
- [ ] note of the psha_chile6/7 results still needed (`PSHA6_NEEDED.md`)
- [ ] project memory reduced to a pointer to psha_chile8

## A. Rebuild the catalog from scratch
- [ ] A0 new catalog module inside `psha_chile8/catalog/`
- [ ] A1 Sergio's rules written down (no Cabello from 1900 on, his source order) → DECISIONS
- [x] A2 source catalogs collected, each frozen as a dated file
- [ ] A3 events matched across catalogs once (one ID per event) ←
- [ ] A4 magnitude, location and mechanism chosen per event, each by its own priority rule
- [ ] A5 Mw conversion redone, checked against events with known Mw
- [ ] A6 large events reviewed one by one against the literature
- [ ] A7 where the double seismic zone exists (literature, data); new class names for events and source models; classified, with upper and lower plane where the zone exists
- [ ] A8 final catalog frozen, dated, with a decisions note

## B. Earthquake statistics
- [ ] B9 method comparison: completeness (incl. spatial), b-value methods, with / without declustering
- [ ] B10 method per source type picked and documented
- [ ] B11 fitting code, tested on synthetic catalogs (known Mc, b, a recovered)
- [ ] B12 fits: crustal, interface, each in-slab plane
- [ ] B13 faults and background join cleanly at M6 (domain-wide)

## C. In-slab double-zone model
- [ ] C14 each plane its own source at small M, one merged source at large M
- [ ] C15 merge magnitude and geometry options to test decided

## D. Magallanes–Fagnano
- [ ] D16 segments (Chilean / Argentine overlap), geometry, slip rate, Mmax, single or joined source

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
