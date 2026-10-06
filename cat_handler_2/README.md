# cat_handler_2: the earthquake catalog of psha_chile

Builds the classified earthquake catalog the source models read, from the
Cabello et al. (2025) integrated catalog of Chile. Two steps with one data
product between them:

```
frozen sources ──prepare.py──▶ catalog_base.csv ──classify.py──▶ catalog.csv
(Cabello, Potin, GCMT,          one row per earthquake,           + tectonic class
 ANSS, GEM; overrides.csv,      location, depth status,           and family
 additions.csv)                 magnitude, mechanism              (class_overrides.csv)
```

`catalog_base.csv` is frozen once the preparation is accepted; the
classification is the part that enters the reproducibility repository, with
`params.py` as its only numeric input. The preparation may stay private.

## Layout

| file | role |
|---|---|
| `params.py` | classification parameters, the choices that matter for the hazard |
| `config.py` | paths, and the windows and preferences of the preparation; re-exports params |
| `sources.py` | readers of the frozen sources; event matching (pairs, one-to-one) |
| `prepare.py` | overrides → dedup → locate → mech → magnitudes; writes `catalog_base.csv` |
| `classify.py` | rules → `class_overrides.csv`; writes `catalog.csv` and `crustal_exceptions.csv` |
| `check.py` | figures and review tables (sections, map, Ruiz and Madariaga 2018) |
| `compare.py` | old classified catalog against `catalog.csv` on common ground |
| `beachballs.py` | beachball images and a points table for the QGIS map |
| `slides.py` | presentation figures (`results/cat_handler_2/slides/`) and `CATALOG_final.md`, from the run outputs |
| `overrides.csv` | hand decisions of the preparation: row fixes (time, location) and magnitudes |
| `additions.csv` | events missing from Cabello |
| `class_overrides.csv` | hand decisions of the classification |
| `DECISIONS.md` | every decision, numbered, with its evidence |
| `CONTEXT.md` | state of the catalog and what the source models need to know |
| `tools/` | one-off checks, `qgis_project.py`, `reclass_report.py` (old vs new classification); not part of the build |

Every hand decision is one CSV row with a reason and a reference; nothing is
hard-coded per event.

## Run

```
python -m cat_handler_2.prepare      # results/cat_handler_2/prepare/, catalog_base.csv
python -m cat_handler_2.classify     # catalog.csv, classify.json
python -m cat_handler_2.check        # results/cat_handler_2/check/
python -m cat_handler_2.compare      # results/cat_handler_2/compare/
python -m cat_handler_2.beachballs   # results/cat_handler_2/beachballs/
python -m cat_handler_2.slides       # results/cat_handler_2/slides/, CATALOG_final.md (after check and compare)
```

`prepare` takes minutes and only needs rerunning when a source or
`overrides.csv` / `additions.csv` changes. `classify` takes seconds; rerun it
after any change to `params.py` or `class_overrides.csv`.

## Inputs (frozen, `data/`)

| file | role |
|---|---|
| catalogs/Integrated_Seismic_Catalog_complete.csv | Cabello et al. (2025), the base catalog; every event and magnitude comes from it |
| catalogs/CHILE_SEISMICITY_RELOCATED.csv | Potin et al. (2024) relocations |
| catalogs/gcmt_jan76_dec20.txt, gcmt_jan21_aug25.txt | GCMT ndk: PDE hypocentre, centroid, tensor |
| catalogs/anss_fm.csv | ComCat moment tensors queried per event, M >= 5 |
| catalogs/cat_gem_chile.csv | GEM mechanisms 1960-1975 |
| catalogs/ruiz_madariaga_2018.csv | the paper's events, parsed (review) |
| slab_2.0/sam_slab2_*.xyz | Slab2 depth, strike, dip, thickness |
| shapefiles/intra_arc.shp, sam_nazca_trench.shp | intra-arc polygon, Nazca trench |
| shapefiles/pb2002_antarctic_trench.geojson | Antarctic trench south of the triple junction (Bird 2003) |

## Outputs (`results/cat_handler_2/`)

- `catalog_base.csv`: one row per earthquake with Cabello magnitude above
  3.9 south of 17 S (config `LAT_MAX`). Columns: `id` (the Cabello id of the row kept), `time_iso`, `year`,
  `longitude`, `latitude`, `depth`, `depth_status` (relocated_cabello,
  relocated_potin, free, filled, fixed, missing, assigned), `depth_src`,
  `mag`, `mag_src`, `mag_cabello`, `Mw_native`, `agency`, `loc_src`,
  `relocated`, `n_rows`, `dup_ids` (the rows merged into the event),
  `general_remarks`, `reference`, `override`, `lon_orig`, `lat_orig`,
  `depth_orig` (before relocation), the ids of the matched sources
  (`gcmt_id`, `anss_id`, `anss_loc_id`, `gem_id`, `potin_id`,
  `cab_mech_id`), `mech_src`, `mech_type`, `strike1..rake2`, `Mrr..Mtp`.
- `catalog.csv`: the same plus `slab_top`, `slab_thk`, `slab_str`,
  `slab_dip`, `dz` (depth minus slab top), `dist_an` (km to the Antarctic
  trench), `class`, `cls_rule` (the rule that decided, `override` for a hand
  decision), `class_auto` (the rule's class), `family`.
- `prepare/`: the stage tables (`01_dedup.csv`, `01_dedup_groups.csv`,
  `02_locate.csv`, `03_mech.csv`) and `prepare.json`; `classify.json`.

## Classes and families

| family | classes |
|---|---|
| interface | slab_interface, patagonia_interface |
| in-slab | intra_slab (slab top above 50 km), slab_deep, deep_nest |
| crustal | forearc, intraarc, backarc, patagonia_crustal, unclassified (real depth <= 30 km) |
| excluded | outer_rise, deep_unknown, unresolved |

`family` is in `catalog.csv`; the source models read it and the classes of
`params.FAMILIES`.

## How to review a build

1. `check/map.png`: each family where it belongs; black rings are hand decisions.
2. `check/sections.pdf`, one transect per 2 deg of latitude with a locator map: the
   plate shadow, the interface band, hollow markers for unknown depths.
3. `check/review_m7.csv`: every M >= 7 event with its flags; `review_rm.csv`:
   the catalog against Ruiz and Madariaga (2018).
4. `compare/compare.txt`: family counts and moves against the old catalog.

To change one event: a row in `class_overrides.csv` (class) or
`overrides.csv` (time, location, magnitude), with a reason and a reference,
then rerun the step that reads it.
