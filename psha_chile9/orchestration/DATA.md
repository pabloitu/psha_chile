# DATA session

Finished briefs and reports: `orchestration/archive/DATA_1.md` (DATA_01, 19 Nov).

## Brief DATA_02 (20 Nov): publishable input data

**Goal:** `data/raw/` ready to publish as is (Zenodo, D-DAT-04): every external input as obtained and described, every change that made our own data recorded in words, the known defects fixed, and the scripts that changed data set aside outside the final repository. No geometry or model choice changes.

**Read first:** `psha_chile9/CLAUDE.md`; in `orchestration/DECISIONS.md` the Data section (D-DAT-01 to 04), D-CLS-07, D-HAZ-01, D-HAZ-05; the DATA_01 report (`orchestration/archive/DATA_1.md`); for the faults `psha_chile8/model/faults/FAULTS.md` section 1, `FIELDS.md`, `REPORT_D16.md` ("Final fault file", hand rows), `REPORT_D16b.md` section 1, and the code `db.py`, `curate.py`, `dbB.py`, `mascsn.py`.

**Found in the orchestrator's review (20 Nov):**
- Database A (`faults/faults_gem_extra_2026-11-15.shp`): 91 text cells with broken accents ("ValparaÃ­so", "San RamÃ³n"); the `.csv` is correct. The previous-work file `crustal_faults_chile_updated` has the same defect (27 cells); the GEM release (`sara_active_faults`) does not.
- The four hand rows of the previous-work file (Bajo Molle, Marga Marga, Laguna Verde, Carranza) have no recorded origin; Marga Marga's 0.4–0.6 mm/yr is in no source found (REPORT_D16). The rule that chose 156 of the 437 GEM SARA rows for that file is not recorded either.
- Eight fault files in `faults/`, of which several are intermediate steps (`faults_2026-11-15`, `faults_gem_*`, `faults_gem_extra_pablo_*` and `*_b`, `crustal_faults_chile_*` without "updated").
- `grids/chile_005.csv` carries `vs30` = 380 for every site, against D-HAZ-01 (rock, Vs30 800); its origin is not recorded.
- No source recorded for `outlines/intraarc.shp` (empty metadata), `trenches/sam_nazca_trench_*`, the basemap; `outlines/chile_outline` is from simplemaps.com (licence not recorded).
- `trenches/pb2002_antarctic_trench_2026-11-15.geojson` (used for the western edge and the Antarctic plane) is an extract made in psha_chile8; the full PB2002 files are now in `trenches/`.
- `faults/riedel_hornig_primary_2026-11-14.csv` is a catalogue, not a fault file.
- File names carry the copy date (`_2026-11-15`), not the source version; the CHAF files carry impossible modification times (years 2073 and 2099).
- Checked and fine: every shape valid, WGS84; the crustal classes tile the crustal area exactly; margin footprints are the union of the segments; western sides on the edge except the Chile Rise inset; the interface lies inside the in-slab area; grids 0.1°, no duplicates (47 crustal and 34 in-slab cell centres lie on an area boundary, 2 more within 1e-6°, harmless); city coordinates plausible.

**Added after CAT_01 and CAT_02 (20 Nov):** CAT copied into `data/raw/` the source catalogues (`catalog/`, 28 tables and `MANIFEST.csv`), the hand-made files (`catalog/manual/`: `overrides_A6.csv` with 30 rows added on 20 Nov from the literature, D-CAT-23; `named_events.csv`, `duplicates.csv`), the depth-σ tables (`catalog/depth_sigma/`), the Natural Earth 10 m land outline (`catalog/land/`), and the Slab2 dip and strike grids (`slab2/sam_slab2_dip_…`, `sam_slab2_str_…`). They get README rows too (read only: do not edit anything in `data/raw/catalog/`); the overrides file is its own record of changes (reference, page, reason), and CHANGES.md points to it.

**Tasks:**
1. `data/raw/README.md`: one row per input (file or folder): what it is, external or ours, source and citation key (`docs/REFERENCES.md`), version, URL or DOI, licence, when and how obtained, the original file name if renamed, which stage reads it. Unknowns stay as "unknown (asked Pablo)".
2. `data/raw/CHANGES.md`: every change from an external input to our data, in words, with counts, IDs, sources and dates, so a reader can follow it without code:
   - faults: GEM SARA (437 rows) → previous-work selection (156) and the four hand rows → database A (cleaning rules of `FIELDS.md`, Pablo's two edits, the removals with reasons, the CHAF additions, the San Ramón trace, the Magallanes–Fagnano GPS rate) → 138 faults; database B from MASCSN26 (restored inputs) and the GEM rows of A. Also `faults/CHANGES_faults.csv`, one row per fault and change (fid, name, change, reason, source, date), made by comparing the files;
   - every shape in `shapes/` (what it was made from, Pablo's choices with dates), the PB2002 extract, the site grid.
3. Fixes, each recorded in CHANGES.md:
   - a. write database A's shapefile again with correct UTF-8 text (values from the `.csv`), and check every field against the `.csv`;
   - b. the intermediate fault files and other superseded files move out of `data/raw/` into the archive of task 4, after Pablo agrees to the list;
   - c. the site grid `vs30` column as Pablo decides (choice B).
4. Archive, not published: `psha_chile9/archive/data_provenance/` with copies of the scripts that made or changed data (`trials/data_shapes/*.py`, psha_chile8 `model/faults/{db,curate,dbB,mascsn,chaf,fagnano,geo}.py`, `trials/data_qgis/make_layers.py`) and a short README; add `archive/` to `.gitignore`. psha_chile8 stays unchanged.

**Decided with Pablo in the session** (one at a time, with a recommendation):
- A. Origin of the four hand rows, of Marga Marga's slip rate, and the rule that chose the 156 GEM rows (his previous work). Recommended: write what he remembers; where nothing is known, CHANGES.md says so.
- B. The site grid: origin, and the `vs30` column. Recommended: drop the column (the job sets Vs30, D-HAZ-01).
- C. `intraarc.shp`, `sam_nazca_trench`, the basemap: origin, and whether each is published. Recommended: publish only what a stage reads; the basemap is a figure input and is cited, not published.
- D. The country outline: keep simplemaps if its licence allows publishing, otherwise use Natural Earth (public domain; the 10 m land outline is already in `data/raw/catalog/land/`). Recommended: check the licence first.
- E. Licences of the derived fault databases: GEM's active-fault data carry a share-alike licence (to check), which would bind A and B. Recommended: check, and state it in the README.
- F. The list of files to move out (3b).

**Out of scope:** no geometry or model changes; nothing in `data/raw/catalog/` (CAT_01 writes there; Riedel-Hornig moves with CAT later); no renaming of files other sessions read (the README records original names instead); no downloads.

**Time:** short; no step runs longer than a minute.

**Done when:** README.md, CHANGES.md and CHANGES_faults.csv exist; 3a done; 3b and 3c done or waiting for Pablo; the archive exists; A–F answered or listed.

**Report:** below this brief, with the headings of CLAUDE.md.

## Brief DATA_03 (20 Nov): the new interface segments and the northern end

(DATA_02 above is still to do, later, before CR; it will record these changes too. This brief comes first.)

**Goal:** `runs/data/data-08`: the interface segments chosen in CAT_03 (D-IF-03), the interface run north to 15.5° S, the northern end of the in-slab and crustal areas, and the arc–backarc line, all as frozen shapes in `data/raw/shapes/` (D-DAT-03).

**Read first:** `psha_chile9/CLAUDE.md`; the DATA_01 report (`orchestration/archive/DATA_1.md`); in `orchestration/DECISIONS.md` the Data section, D-IF-03, D-IF-10, D-CLS-07, D-CLS-08; `orchestration/CAT.md`, CAT_03 Addendum 5 (the segments, the drawing rule) and `docs/methods/SEGMENTATION.md`; QUESTIONS Q-72, Q-75, Q-79; the one-off scripts in `trials/data_shapes/` (how the frozen shapes were made).

**Tasks:**
1. Segment limits, ° S: 15.5 | 19.1 | 23.3 | 26 | 29.9 | 32 | 37 | 45.55. Each limit starts on the western edge at its latitude and runs perpendicular to the trench (the edge's strike there), down the Slab2 dip, past the 60 km contour. Replace `interface_segment_limits.geojson`.
2. Interface footprints: margin and the seven segments, from the edge to 50 and to 60 km, 15.5–45.55° S, cut by the new limits; the Chile Rise inset kept. Made once by a one-off script in `trials/data_shapes/`, written to `interface_footprints.geojson`.
3. Northern end of the in-slab and crustal areas (choice a): if they follow to 15.5° S, draw a rough first version of the extra part (in-slab on Slab2 as before; crustal with the forearc to the edge, the arc continued with its width, the backarc to the eastern side) for Pablo to redraw in QGIS.
4. Arc–backarc line (choice b, Q-79): a map of the backarc-type events (reverse, east of the arc) that fall inside the arc polygon; Pablo redraws the line; the other classes rebuilt around his arc (`tidy_classes.py`).
5. Basemap north of 17° S (choice c): find how `basemap_gray.tif` was made (source, resolution) and propose how to extend it; nothing downloaded without Pablo.
6. Run, write `data-08`, with the check figures of `data-07` plus the crustal-classes map (Q-75), and a comparison with `data-07` (areas, footprints per segment in km², grid cells).

**Decided with Pablo in the session** (one at a time: what is done now, a map, a small table, the recommendation in two or three sentences; his answer under "Decisions with Pablo", in his words):
- a. Q-72: do the in-slab and crustal areas follow the interface to 15.5° S? Recommended: yes, one northern limit for every family, as at 17.1° S before; Arica then gets its in-slab hazard from the north.
- b. The arc–backarc line (Q-79).
- c. The basemap north of 17° S.
- d. If a is yes: the crustal classes north of 17.1° S.

**Out of scope:** DATA_02 (provenance, later); the catalogue and the classification (CAT_04 classifies on `data-08`); fits.

**Time:** short; the drawing is Pablo's.

**Done when:** `data-08` exists with the new limits, footprints, areas and classes and the check figures; a–d answered or listed as left to do.

**Report:** below this brief, with the headings of CLAUDE.md.

## Report DATA_03 (20–21 Nov)

### Done
- Task 1: eight segment limits (D-IF-03), each from the western edge at its latitude along the edge's strike + 90° (strike over ± 0.5° of latitude), from 30 km west of the edge to 30 km past the Slab2 60 km contour (`trials/data_shapes/make_segments.py`). The northern limit is the 15.5° S parallel (choice a). Edge strikes: 45.55° S 6°, 37° S 10°, 32° S 7°, 29.9° S 5°, 26° S 8°, 23.3° S 4°, 19.1° S 323° (N37°W), 15.5° S 317°. The 45.55° S line runs at azimuth 96° and cuts nothing north of Slab2's last row.
- Task 2: interface footprints, margin and seg1–seg7 (south to north), edge to 50 and to 60 km, 15.5–45.55° S, Chile Rise inset kept. South of 17.2° S the new margin matches data-07 to 0.0007 deg² (about 8 km²).
- Task 3: rough northern extension of the in-slab and crustal areas to 15.5° S (`extend_north.py`): eastern sides continued along their trend over the last 2°, the arc with its width. Pablo then redrew the arc and the backarc's eastern edge (choices b, d); the in-slab extension stays as drafted.
- Task 4 (choice b): map of the reverse events inside the arc (`trials/data_choices/b03_arc_backarc.png`): only 3 of the 9 lie on the eastern edge. Arc drafts tried and set aside: 20 km at 30–35° S (`arc_east_30_35.py`), a volcanic-front band (`arc_north.py`, GVP volcanoes downloaded with Pablo's yes, trial only), a half-height rule from topography (`arc_fwhm.py`; Pablo: "Doesn't look well"). Pablo redrew the arc by hand; I simplified it (1,212 → 87 nodes, at most 1.0 km moved, `simplify_arc.py`) and rebuilt the other classes (`tidy_classes.py`). Pablo redrew the backarc's eastern edge; the crustal area follows it (`area_from_classes.py`). The edge had come loose from Patagonia's north-east corner; joined again by a straight line from 71.90° W 46.17° S to the corner (71.65° W 47.28° S; `join_backarc.py`, `trials/data_choices/backarc_join.png`).
- Trial classifications (CAT code unchanged, cat-06 on a trial DATA build, 12 s; `trials/data_classify/run_trial.py`) and E–W sections in the X4 style of psha_chile8 (`sections.py`): t1 volcanic-front draft, t2 Pablo's arc, t3 Pablo's arc and backarc edge. QGIS layers of each in `t*/qgis/` (`trials/data_qgis/make_cat07.py`).
- Task 5 (choice c): `basemap_gray.tif` was made in QGIS (`data/basemaps/basemap_chile_gray/basemap_gen.qgz`) from GEBCO_2025 (15″, 80–65° W, 58–17° S): land gray ramp, sea Blues ramp, hillshade (azimuth 315°, altitude 45°, multiply), coastline, border, trenches. Downloaded, with Pablo's yes, GEBCO_2025 80–63.5° W, 17.5–14.5° S (download.gebco.net, 21 Nov; identical to the old grid over 17–17.5° S). New layers to 14.5° S, sea restyled (choice of nine variants), trench continued north, the four basemaps rendered headless with PyQGIS (`trials/basemap/export.py`, 200 dpi on the old 0.004° grid so lines are 2–4 px).
- Task 6: `runs/data/data-08` with the check figures of data-07 plus the crustal-classes map (Q-75, new `classes()` in `figs.py`); comparison with data-07 below.
- Edits in `data/raw/shapes/` (all 20–21 Nov): `interface_segment_limits.geojson` and `interface_footprints.geojson` replaced (7 segments, 15.5° S); `inslab_area.geojson` extended to 15.5° S; `crustal_area.geojson` extended to 15.5° S and its eastern side moved to Pablo's backarc edge; `crustal_classes.geojson` Pablo's arc and backarc, the forearc, Patagonia and backarc rebuilt. Shapes before DATA_03 in `trials/data_shapes/before_data03/`; Pablo's QGIS files in `pablo_arc_d03/`, `pablo_backarc_d03/`.
- New raw inputs (21 Nov): `data/raw/basemaps/basemap_chile_2026-11-21/` (four basemaps + `project/` with `basemap.qgz` and its rasters, relative paths, styles saved, no code); `data/raw/basemaps/gebco_2025_north/` (the tile as downloaded, GEBCO documentation and terms of use); `data/raw/outlines/coastline_2026-11-21` (0 m contour of GEBCO_2025), `chile_borders_2026-11-21` (was `chile_argentina_border`, which holds all Chilean borders), `borders_ne10m_2026-11-21` (Natural Earth 10 m land boundaries north of Chile); `data/raw/trenches/nazca_trench_2026-11-21` (the old trench to 17.0° S, then PB2002 NZ\AP–NZ\SA, the 53 km E–W offset faded over 2°, edited by Pablo), `antarctic_trench_2026-11-21`, `chile_rise_2026-11-21` (copies of the repo shapefiles).
- Shapes and new lines in `data/raw` left as plain files (`clean_shapes.py`): attributes reduced to a name (classes `cls`, footprints `segment`, `top`, `bottom`, limits `name`, `lat`), coordinates on a 1e-6° grid except the crustal classes and area (rounding there reopens hairline slivers at the arc's tip); files before in `trials/data_shapes/before_clean_d03/`. data-08 was built before the backarc join and the clean-up, deleted (Pablo: "Delete and rebuild08") and rebuilt.
- Final check of the shapes and the run (Pablo: "I don't want to come back modifying the data no more"): 106 checks in `trials/data_checks/check_data.py` (validity, one part, no repeated nodes; areas east of the edge, northern sides at 15.5° S, inside the box; classes fill the area without gaps, holes or overlaps, the arc separates forearc and backarc; limits through the edge at their latitudes, not crossing; footprints add up to the margin, do not overlap, lie between their limits, eastern sides on the 50 / 60 km Slab2 contour within 0.1 km, western sides on the edge, edge-50 inside edge-60; in-slab south of 44.3° S equal to the edge-60 margin; run copies equal the shapes; grids on 0.1° multiples, no duplicates, every centre inside, cell areas within 0.6 % of the area; cities inside; Antarctic plane 5–50 km). Result `trials/data_checks/check_data-08.txt`: 0 FAIL. Fixed on the way (`fix_checks.py`): nodes at 15.5° S set exactly (they were 8e-12° south, so the northern grid row fell out of the crustal grid); edge-50 segments cut by the edge-60 segments (slivers of up to 340 m² outside); the in-slab area south of 44.275° S set to the new edge-60 margin (8.6 km² off near the Chile Rise inset, left from data-07); a self-touching ring at the forearc's northern tip. `build.grid` now counts a centre on the boundary within 1e-7° (1 cm), so float noise from the cut at the edge cannot drop a boundary row; test added (`tests/test_data_grid.py`, 3 passed). data-08 rebuilt again.
- `config/data.yaml`: run data-08, seven segment names. `figs.py`: basemap `basemap_color_trench.tif`, new crustal-classes figure. `build.grid` changed (above) with its test.

### Outputs
- `runs/data/data-08`. Against data-07 (`trials/data_compare/data-07_vs_data-08.csv`):

| Item | data-07 | data-08 |
|---|---|---|
| crustal area, km² | 2,227,148 | 2,011,083 (+139,800 north, −364,300 east, +1,800 at 42–44° S, +6,600 at 46.2–47.3° S) |
| crustal grid cells | 22,907 | 20,725 |
| in-slab area, km² | 1,752,376 | 1,899,282 |
| in-slab grid cells | 16,552 | 17,898 |
| forearc / arc / backarc / Patagonia, km² | 718,164 / 435,512 / 668,532 / 404,915 | 894,053 / 326,899 / 385,191 / 404,915 |
| margin edge–50 / edge–60, km² | 478,910 / 548,010 | 515,567 / 590,873 |

| Segment (data-08) | Limits ° S | edge–50 km² | edge–60 km² |
|---|---|---|---|
| seg1 | 37–45.55 | 141,460 | 157,187 |
| seg2 | 32–37 | 88,531 | 101,051 |
| seg3 | 29.9–32 | 31,958 | 36,663 |
| seg4 | 26–29.9 | 60,825 | 69,901 |
| seg5 | 23.3–26 | 43,520 | 52,158 |
| seg6 | 19.1–23.3 | 76,099 | 90,696 |
| seg7 | 15.5–19.1 | 73,173 | 83,217 |

  The edge–50 and edge–60 footprints are one file (`interface_footprints.geojson`, 16 features: margin and seg1–seg7 for `bottom` 50 and 60, `top` 0 = the edge), on the same limits; each edge–50 polygon lies exactly inside its edge–60 one.
  seg1 loses 2,100 km² against data-07 (the 37° S limit now slants south down-dip). The names seg3 and seg4 mean other segments than in data-07.
- Trials (trial, not used): `trials/data_compare/` (the comparison), `trials/data_classify/t1–t3/`, `trials/data_shapes/` (scripts, backups), `trials/data_choices/` (choice figures), `trials/data_qgis/cat07/` and `volcanoes/` (GVP Holocene list, downloaded 20 Nov), `trials/basemap/` and `trials/data_basemap/` (scripts and decision figures only; the 420 MB of copies deleted with Pablo's yes).

### Figures to look at
- `runs/data/data-08/figs/overview.png`, `zoom_45_47S.png`, `areas_vs_psha8.png`: compare with the same figures of data-07 (interface and both areas now reach 15.5° S; seven segments; the crustal area narrower in the east; new basemap).
- `runs/data/data-08/figs/crustal_classes.png` (new, Q-75): the four classes with the crustal events coloured by the polygon they fall in.
- `trials/data_classify/t3/sections/` (14 E–W sections, 16.3–38° S): Pablo's arc and backarc (before the 46–47° S join, which lies south of every section); compare with `t1/sections/` (volcanic-front draft).
- Choices: `trials/data_choices/a03_northern_end.png` (a), `b03_arc_backarc.png`, `arc_north.png`, `arc_fwhm.png` (b), `trials/data_basemap/sea_variants.png`, `sea_compare.png`, `trench_lines.png` (c).

### Decisions with Pablo
- a. Northern end (Q-72): the source catalogues were downloaded with the box (15.5° S) as the query, and Cabello ends there too. "Yes, 15.5 parallel for all three, cut seg7 there. Shame, but ok." The northern limit of seg7 is the parallel, not perpendicular (7,500 km² of seg7 edge–50 would lie outside the box). North of 17.1° S cat-07 has 435 in-slab intermediate events of Mw ≥ 4.5 (9 of Mw ≥ 7), 133 shallow (3), 306 interface (5), 67 crustal.
- b. Arc–backarc (Q-79): "The arc, more than the 'volcanic arc' it represents the main cordillera, to classify the events there." On the half-height rule: "nono, not half height. Doesn't look well. The FM prior is nice, to delimitate arc and back arc I'd rather redraw it." Pablo redrew the arc ("it is beautiful"). Over the flat slab: "we keep the arc name and explain it" (methods: the main cordillera, which holds the magmatic arc where there is one; over the Pampean flat slab, 27.5–33° S, the main cordillera without an active arc). In t2 the arc's mechanisms by position are strike-slip 17.0, oblique 12.6, reverse 2.0, normal 1.0 (weights; 9.0 reverse before); Las Flores (30.3° S) now lies wholly in the backarc.
- d. Crustal classes north of 17.1° S and the backarc: "I've redrawn the backarc eastern edge, in the spirit only chilean relevant earthquakes, and to save grid cells." Where it came loose from Patagonia: "Straighten from 46° S". The crustal backarc weight of Mw ≥ 4.5 falls from 309.8 to 258.4; the largest that leave are the two 1929-05-30 events in southern Mendoza (Mw 6.4, 6.0, crustal weight 0.45 each), 1936 Mw 6.2, 2004 Mw 6.1, 2002 Mw 6.0; 1861 Mendoza, 1944 San Juan and 1977 Caucete stay inside. "ok leave them outside and inslab as it is" (in-slab eastern side unchanged, about 65° W).
- c. Basemap: GEBCO downloaded by me ("You try it"). Sea: "i is super, but a little bit more hillshade for the trench"; "Yes, i at 70 %" (sea ramp #9fb9cc–#eef4f8, sea hillshade 70 %, coastline #4d4d4d 0.26 mm). Land stays gray ("lets keep it like this"). Trench: "merge it and I adapt it manually". "The four maps go, to have backup and not return to trials. The basemap project also goes to data, without the codes"; "the chile_argentina_border should be actually chile_borders".
- Sections: "I like the section figures style, we should save that for the classification session to make those figures as well."

### Questions for Pablo
1. The in-slab area north of 17.1° S is my rough draft (eastern side continued to 67.9° W at 15.5° S). Recommended: keep it; the Arequipa intermediate events lie well inside.
2. The basemap has no elevation east of 65° W and south of 58° S (transparent, as before): the old GEBCO grid ends there. Recommended: leave it; the figures end at about 63.6° W.
3. The GVP volcano list (trial only) could become a raw input if the arc is ever redrawn from volcanoes. Recommended: no; the arc is Pablo's drawing.

### Requests for other sessions
- CAT (CAT_04): classify on `runs/data/data-08`. Use the section figures of `trials/data_classify/sections.py` (X4 style: class palette, Slab2, topography ×3, crustal-class bar, location map) for the classification figures (Pablo). Basemap in `config/catalog.yaml` → `data/raw/basemaps/basemap_chile_2026-11-21/basemap_color_trench.tif`.
- STATS: segments seg1–seg7 south to north (limits above; seg3/seg4 renamed); a planes update for the arc (Q-79): by position the arc is now strike-slip, reverse 2 of 32.6 weighted mechanisms. Basemap in `config/stats.yaml`.
- IF: seven footprints from data-08; the northern limit is the 15.5° S parallel; seg1 is 2,100 km² smaller.
- IS: in-slab area and grid from data-08 (to 15.5° S, 17,898 cells).
- CR: crustal area and classes from data-08 (backarc 385,191 km², area to 15.5° S, east side Pablo's).
- FIG: `docs/FIGURE_STYLE.md` basemap path; the sections' X4 colours (forearc #ffb000, arc #2e8b57, backarc #8c6d1f, Patagonia #c2a5cf) differ from the house class palette.
- DATA_02: README and CHANGES rows for the new raw inputs and the shape edits listed under Done.
- Orchestrator: D-DAT-01 (northern side 15.5° S for every family; crustal east side Pablo's backarc edge), D-DAT-03 (data-08; limits drawn perpendicular, the northern one the parallel), D-IF-03 (same), D-CLS-07 (arc = main cordillera, redrawn by Pablo; the wording above), D-CLS-10 (the 1929 southern Mendoza pair outside), Q-72, Q-75 and Q-79 (DATA part) closed.

### Learnings
- Shapes rebuilt by scripts pick up float noise (8e-12°) on straight sides; a grid rule "inside or on the boundary" then depends on it. Count boundary centres within a tolerance, and check boundary rows after every rebuild.
- A rebuild script that writes `data/raw/shapes/` overwrites an unsaved QGIS edit; copy Pablo's saved file aside first, then rebuild.
- `tidy_classes.py` needs the arc to reach past the area's sides (e.g. 0.1° beyond the northern limit), or forearc and backarc join through a hairline.
- Trial classifications on a trial DATA build take 12 s and their sections show at once which side a sequence falls; check class lines this way, not on maps.
- PyQGIS renders a QGIS project headless; on a 0.004° grid at 96 dpi a 0.26 mm line falls under a pixel, so render at about 200 dpi on the same grid. Check symbol opacity too (the project coastline was at 31 %).
- download.gebco.net has a JSON queue API (`/api/queue`, no email needed) for small GEBCO tiles.

### Left to do
- DATA_02 (provenance, README, CHANGES), later.
- Line widths for the classified-events map (CAT_04 / FIG): coastline, trench and borders may need to be wider once that figure exists (Pablo: "we can then replace the existing in data/raw, as long as the code is still saved"). Re-export with `trials/basemap/export.py` (`lw` at the top scales every line, `dpi` the pixel size of a mm), replace the four basemaps in `data/raw/basemaps/basemap_chile_2026-11-21/`, commit script and basemaps together.
- Zoomed basemaps (e.g. the LOFS), when needed: `trials/basemap/export.py` renders `basemap.qgz` at any extent, pixel size and line width; GEBCO (15″, about 460 m) limits the resolution, a finer inset needs a finer elevation model (a new download).
- Questions 1–3.
