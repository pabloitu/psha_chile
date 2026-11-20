# STATUS (19 Nov, evening)

## psha_chile9
- Design: `claude/DESIGN_psha_chile9_orchestration.md` rev. 4 (project doc). Work on git branch `psha9`.
- SETUP done (references, environment). DATA done: geometry frozen in `data/raw/shapes/`, latest run `runs/data/data-07` (data-01 to 06 deleted).
- CAT_01 written in `orchestration/CAT.md`, not started (Pablo starts it).

## Latest runs
- data: `data-07`. catalog, stats, interface, inslab, crustal, gmm, hazard: none yet.

## Waiting for later briefs (from the DATA_01 report)
- CAT_02 (classification, C7): read data-07; Antarctic interface class from 45.55° S; outer rise = shallow, no slab under it, outside the crustal area (the Chile Rise inset replaces the 75 km rule); Scotia–Antarctic events to outer rise (17g put them in the Antarctic interface class); crustal sub-classes from `crustal_classes.geojson`, Patagonia south of the arc (48.5° S); events north of 17.1° S keep their class but are outside every source (Q-72); Q-74.
- IF: footprints from `data/raw/shapes/interface_footprints.geojson`; top at the edge only, bottom 50 / 60 km; geodetic moment about +10 % against 10–50 km; seg1's western side at 45.05–45.56° S is the inset line; Antarctic plane 5–50 km from 45.55° S, about 57,800 km² (Q-73).
- IS: area and grid from data-07; south of 44.27° S the area is the edge–60 km band; Q-71.
- CR: crustal area, grid and class polygons from data-07 (planes by class, D-CR-04).
- HAZ: `sites_cities.csv` (16, Puerto Williams for Ushuaia), `sites_grid.csv` (0.05°); coarse grids 0.1° and 0.2° in `data/raw/grids/`.
- DATA, next run: crustal-classes map in the check figures (Q-75).

## Where psha_chile8 stopped (inputs for the port)
- Catalogue `catalog/frozen/2026-11-17g/`.
- Fits, declustered catalogues, pad tables `2026-11-18`; nodal planes `npd_2026-11-18`; depth cells `2026-11-18`.
- Interface `model/interface/nrml_2026-11-18/`; in-slab `model/inslab/nrml/2026-11-18i/`; crustal `model/crustal/nrml/2026-11-18b/`.
- Hazard: cities calcs 646–648 (final trees), interface grid calc 698.
