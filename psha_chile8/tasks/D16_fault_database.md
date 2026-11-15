# D16: crustal fault database (clean, compared with CHAF, Magallanes–Fagnano)

Read `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (sections Crustal and faults, Magallanes–Fagnano) and `LEARNINGS.md` first. Work in `model/faults/`, with tests in `model/faults/tests/`. You may run everything in this task yourself. This task comes before B13: B13 reads the database made here.

## Why

The fault model reads `../data/active_faults/crustal_faults_chile_updated.shp`. It has 160 segments taken from the GEM South America (SARA) fault database, with IDs CL-… and AR-…, plus rows added by hand. A first look (15 Nov) found four problems.

**1. Seven columns are not fault properties.** `id_area`, `min_mag`, `max_mag`, `a_val`, `b_val`, `usd` and `lsd` were copied from the GEM area source each fault sits in. For example, 75 faults share `max_mag` 7.75 and one a and b, all from area zone 566. The old code read them in two places:
- the "observed + 0.2" Mmax branch took `max_mag` + 0.2, so that branch was an area-zone Mmax
- the fault b came from `b_val`

**2. Slip rates are mostly the midpoints of classes.** 87 faults have 0.5 mm/yr (the "0.1–1" class) and 53 have 3.0 mm/yr (the "1–5" class). The class text is kept in `slip_rates`.

**3. Depths are almost all the same.** The upper depth is 0 everywhere, and the lower depth is 20 km for all but four segments.

**4. Some rows were added by hand:**
- 13 rows with `max_mag` 0
- 4 without `id_seg`
- 3 without a length
- the Magallanes–Fagnano segments, where the Chilean (CL-056) and Argentine (AR-0056) lines overlap near Lago Fagnano

Pablo wants a clean database. Then a comparison with the Chilean Database of Active Faults (CHAF; Maldonado, Contreras and Melnick 2021, Scientific Data 8:20, doi 10.1038/s41597-021-00802-4) to see which important faults the GEM database lacks. **The comparison is exploration only. No fault is added in this task.**

## Inputs

- **Current database:** `../data/active_faults/crustal_faults_chile_updated.shp`, and the older `crustal_faults_chile.shp` for the history.
- **The full SARA release:** `../data/active_faults/shapefile/sara-active-faults.shp`, also geojson and kml. Use it to recover GEM's own fields and IDs for the rows that lost them.
- **CHAF:** `../data/active_faults/CHAF_Pangaea_v1/CHAF_Pangea_v1.shp` (note the spelling "Pangea" in the file names), downloaded by Pablo on 15 Nov. Data: Melnick, Maldonado and Contreras 2020, PANGAEA, doi 10.1594/PANGAEA.922241, CC-BY-4.0. It has 959 strands in 17 systems (78 proved, 592 probable, 288 possible) and covers 19.3–47.8° S only, so it says nothing about Magallanes–Fagnano. Read its field descriptions from the paper and the files.
- **Fault code (read only):** `psha_chile7/crustal/s03_faults.py` and `config.py` (`FIELDS`, `FAULT_SYSTEMS`, the Fagnano rule) show how the old fields were used.

Copy every input into `psha_chile8/data/` as a dated file with its sha256, and give it a row in `DATA.md`.

## Step 1: clean database

**Columns.** Keep only properties of the fault itself: geometry and the attributes below. Every value says where it came from. Delete the area-source columns (`id_area`, `min_mag`, `max_mag`, `a_val`, `b_val`, `usd`, `lsd`). Rename the fields to plain names; `length` can stay. Proposed schema (adjust if needed, and explain any change in the report):

| field | content |
|---|---|
| `fid` | our segment ID (keep the GEM ID where there is one) |
| `gem_id` | GEM / SARA segment ID, empty if none |
| `system` | fault system name (e.g. Liquiñe–Ofqui, Atacama, Magallanes–Fagnano) |
| `name` | fault or segment name |
| `kin` | kinematics as given (reverse, normal, dextral, …) |
| `rake` | rake in degrees, from `kin` by a stated table |
| `dip`, `dip_dir` | dip in degrees, dip direction as azimuth (vertical → none) |
| `sr`, `sr_lo`, `sr_hi` | slip rate (mm/yr): preferred value and the class or range bounds |
| `sr_kind` | `measured` (a study gives a value) or `class` (only an activity class: midpoint) |
| `z_top`, `z_bot` | seismogenic depths as given by the source, empty if the source has none |
| `length` | km, recomputed from the trace |
| `src`, `src_ref` | source database and reference for the row; a column per field if the sources differ |
| `chaf_ids`, `chaf_act` | matched CHAF strands and their activity class (filled in step 2) |
| `note` | free text, only where needed |

**Rows:**
- **IDs:** each row gets an ID. Rows added by hand are traced to their origin where possible; say which ones cannot be traced.
- **Duplicates:** flag overlaps and duplicates (traces within 2 km over more than 50 % of the shorter one) and list them. Do not delete them, apart from exact duplicates.
- **Fagnano:** leave its overlap for step 3.
- **Mmax, a, b:** not in the database. They are computed in the model, so no Mmax field.

**Files:**
- Write `data/faults/faults_<date>.gpkg` (one layer, EPSG:4326) and a CSV without geometry. Write a field description, `model/faults/FIELDS.md`.
- **Tests:**
  - every row has geometry, dip, dip direction (or vertical), kinematics, slip rate and length
  - no area-source field is left
  - lengths match the traces within 1 %

**Report:**
- the slip-rate table, from `sr_kind` and the classes
- how many rows changed and how

## Step 2: what GEM is missing (exploration)

**Matching.** Match the clean database to CHAF strand by strand:
- **Rule:** a CHAF strand matches a GEM segment if it lies within 2 km of the GEM trace over most of its length.
- **Checks:** report the result for 1, 2 and 5 km. Also report system against system: CHAF's 17 systems against the GEM `system` field.

**Important missing faults.** For the CHAF strands with no GEM match, group them into faults (joined strands of one system with a gap under 5 km). Rank them by these criteria:
- activity class: proved, then probable, then possible
- length, and the magnitude a full rupture could give (Wells and Coppersmith 1994 and Leonard 2014, from the length and a 20 km width)
- distance to the 14 cities of DECISIONS and to Santiago, Valparaíso and Concepción in particular
- known historical or instrumental crustal earthquakes nearby (frozen catalogue, crustal class weight ≥ 0.5, Mw ≥ 5.5, within 10 km)

**Literature.** For the top 20, say whether a slip rate or palaeoseismic study exists, with the reference. Read the source before citing it; mark what you could not read. Known candidates to check by name (they may or may not be missing):
- San Ramón (only one segment, "San Ramon 01a", is in GEM)
- Pichilemu
- El Yolki
- Mejillones
- the Atacama system segments
- the Liquiñe–Ofqui branches
- Lanalhue
- Santa María / Marga Marga
- the West Andean Thrust

**Outputs:**
- a ranked table `model/faults/tables/missing_<date>.csv`
- a map of the GEM faults against the CHAF faults: matched, unmatched by activity class, and the cities; with insets for northern Chile, central Chile around Santiago, and the Liquiñe–Ofqui zone
- a short paragraph on what adding the top faults could change. Measure that change with the slip-rate rule the model would need (e.g. the class midpoint of the system), as an estimate only, not added to the database.

## Step 3: Magallanes–Fagnano

1. **Map** every segment of the system in the GEM/SARA database (CL-056b to j, AR-0056a, b, d, g, and any other).
2. **Overlap:** show where the Chilean and Argentine traces run parallel (within 5 km). Propose one trace per section, by a stated general rule (for example, the more detailed mapping).
3. **Slip rate:** the database gives 3 mm/yr; GPS studies give 4–7 mm/yr. Find and read the GPS and geological studies, giving the reference and page for each value used.
4. **Mmax:** the old model took one value for the whole system, 8.0 + 0.2 (the 17 Dec 1949 doublet, Mw 7.5–7.8, which is 8.0 in the old catalogue). Give the system length and area, the Mmax from Wells and Coppersmith 1994 and from Leonard 2014, and the observed maximum in the frozen catalogue.
5. **One source or several:** one system source against separate segments. Give what each implies for the rates at Mw ≥ 6.5 and 7.
6. **Proposal:** propose DECISIONS lines. Pablo decides.
7. **Puerto Williams:** that result went from 0.10 to 0.02 g between psha_chile7 runs. Say whether the clean database contains every segment near Puerto Williams.

## Outputs

- `data/faults/faults_<date>.gpkg` and `.csv`, `model/faults/FIELDS.md`
- `model/faults/` code with tests (pytest passes)
- `model/faults/REPORT_D16.md`: simple and explanatory, written for a seismologist who is not a fault-database specialist. In this order:
  1. what changed in the database
  2. the missing important faults
  3. Magallanes–Fagnano
  4. proposed DECISIONS lines and open questions
- tables in `model/faults/tables/` and figures in `model/faults/figs/`, with rows in `FIGURES.md` for paper candidates

## At the end

Follow `CLAUDE.md`. A C14 session may be appending to `WORKLOG.md` at the same time: re-read the file just before appending. Tick D16 in `PLAN.md` when the clean database exists and the tests pass, and move the ← marker to B13.
