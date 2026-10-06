# cat_handler_2: state of the catalog, 2026-09-30

For the next conversation (source-model rebuild in psha_chile6). Read with
README.md (what the code does) and DECISIONS.md (why).

## What exists

- `results/cat_handler_2/catalog_base.csv`: 53 418 earthquakes with Cabello
  magnitude above 3.9, 1513-2022, one row each, deduplicated (about 20 % of
  Cabello's rows were cross-agency copies), Potin-relocated where Cabello
  had not, depth status per event, focal mechanisms for about 2 700 events,
  magnitudes from Cabello except 21 from Ruiz and Madariaga (2018).
- `results/cat_handler_2/catalog.csv`: the same with class, family and the
  slab geometry at the event. This replaces
  `results/catalogs/integrated/cat_classified.csv` of the sensitivity
  campaign (psha_chile5).
- The code: `prepare.py` (sources -> catalog_base), `classify.py`
  (catalog_base -> catalog), `params.py` (the classification parameters),
  the three hand-decision CSVs, `check.py`, `compare.py`, `beachballs.py`.
- Review material: `check/sections.pdf` (transects every 2 deg),
  `check/map.png`, `check/review_m7.csv`, `check/review_rm.csv`,
  `compare/compare.txt`, the QGIS project `project_cat2.qgz`.

## What changed against the campaign catalog (M >= 5.5, common ground)

| family | old, after removing duplicates | new |
|---|---|---|
| interface | 704 | 826 |
| in-slab | 1 016 | 910 |
| crustal | 315 | 259 |

Sources of the change: thrust mechanisms on the interface plane now go to
the interface (rule `cone`, about 100 events); default-depth and historical
events over a slab top of up to 65 km go to the interface when they have no
mechanism; events over the deep slab at 100-200 km that were forearc are
slab_deep; crustal classes hold only real depths of at most 30 km, and
default-depth events go to the slab family wherever a slab exists
(DECISIONS 34, 30 Sep 2026). Details in `compare/compare.txt` and
`compare/changes.csv`.

## What the source models must do differently

1. Read `family` (or `params.FAMILIES`) instead of hard-coded class lists:
   the crustal family now has `backarc` and `patagonia_crustal`, the
   interface family has `patagonia_interface`. `unresolved`, `outer_rise`
   and `deep_unknown` stay out.
2. The Antarctic interface south of 46.15 S is a new source: trench from
   Bird (2003) PB2002 (`data/shapefiles/pb2002_antarctic_trench.geojson`, or
   the user's `sam_antarctica_trench.shp`), footprint 150 km landward and
   60 km deep, convergence about 16 mm/yr towards N100E (Breitsprecher and
   Thorkelson 2009); no slab model exists, the Slab2 dip at 44-46 S is the
   reference (sections A16-A23).
3. In-slab Mmax: the largest in-slab event is now Santiago 1647 M8.4
   (intraslab by Ruiz and Madariaga); decide whether historical events
   count for Mmax (DECISIONS 31).
4. Magnitudes: Cabello's Mw is agency-dependent; ISC-only events are about
   0.3 low against GCMT (DECISIONS 32). Either state it or correct it before
   the completeness and b-value fits.
5. `depth_status` tells which depths are real; the in-slab depth model
   should use `relocated_*`, `free` and `filled` only.
6. Duplicate removal lowers the small-magnitude rates (interface and
   in-slab at M 4-5.5) relative to the campaign; fit floors of 5.5-5.8
   are above the affected range.

## Open

- Historical M >= 7 events still `unresolved`: 1687 (Santiago area), 1850
  (arc), 1870 (Calama).
- Events of Ruiz and Madariaga (2018) absent from Cabello: Pica 1768, Taltal
  1887, Copiapo 1959, Mejillones 1994, the Valdivia Ms 7.8 foreshock, the
  Maule outer-rise Mw 7.4.
- Crustal events deeper than 30 km kept by hand (results/cat_handler_2/crustal_exceptions.csv): literature class or the 30 km cap, one by one (DECISIONS 34).
- Above a deep slab between 30 km and FOREARC_MAX_Z (70 km): now unresolved (rule deep_mid); FOREARC_MAX_Z is the lever.
- Concepcion in-slab rate excess (findings_rock800 section 4, item 7): to be
  rechecked against the new catalog in the source-model step.

## Next

psha_chile6: point the classifier input at `results/cat_handler_2/catalog.csv`,
add the new classes to the families, refit interface and in-slab sources,
check the Concepcion in-slab rate and the in-slab Mmax, then continue with
workplan step 3 (source calibration).
