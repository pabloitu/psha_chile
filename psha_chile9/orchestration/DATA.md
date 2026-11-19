# DATA session

## Brief DATA_01 (19 Nov): the first data run

**Goal:** `runs/data/data-01`, the geometry every later stage reads (design 4.2), from `data/raw/` and Pablo's shapes.

**Read first:** `psha_chile9/CLAUDE.md`; `docs/PORTING_MAP.md` section DATA (D1–D3); in `orchestration/DECISIONS.md` the Data section (D-DAT-01 to 03), D-CLS-07 to 10, D-IF-03, D-IF-10, D-IS-11, D-HAZ-05, D-HAZ-07.

**Already there:** Pablo's `data/raw/shapes/crustal_area.geojson` and `inslab_area.geojson` (19 Nov; north, south and east sides count, the western side is replaced by the edge of task 2). QGIS layers of the psha_chile8 17g catalogue and context in `trials/data_qgis/` (made by `make_layers.py` there); reuse them for the figures.

**Tasks:**
1. Copy, do not move, the D1 raw inputs from `psha_chile8/data/` into `data/raw/` (Slab2 top, thickness, uncertainty; Nazca trench; PB2002 Antarctic trench and the SC/AN boundary, locate the full PB2002 file; Chile outline; arc polygon (locate); fault databases; CHAF; Riedel-Hornig; the gray basemap).
2. `src/psha9/data_processing/` with `config/data.yaml`, writing `runs/data/data-01/`:
   - the western edge (D-DAT-02): the Slab2 western edge, then the Antarctic trench south of the triple junction;
   - the crustal and in-slab areas, cut to that edge;
   - interface segment limits: port the psha_chile8 limits from `model/interface/if_geom.py` into `data/raw/shapes/interface_segment_limits.geojson` (lines across strike, northern end 17.6° S for now); footprints derived from Slab2 between the depth contours of the setting (D-DAT-03; contours 0, 10, 50, 60 km), cut at the edge and the limits; the Antarctic plane of D-IF-10;
   - in-slab and crustal grids inside their areas, 0.1° as in psha_chile8; site files: the 16 cities of D-HAZ-05 into `data/raw/shapes/cities.geojson`, and the 0.05° grid (D-HAZ-07).
3. Check figures in `runs/data/data-01/figs/`: one map with every area, the edge and the segments over the 17g catalogue (size by Mw, big events on top, FIGURE_STYLE); a zoom on 45–47° S with the 17g classes of the events there; the new areas against the psha_chile8 domains.

**Decided with Pablo in the session** (show the figure, give a recommendation, write his answer under "Decisions with Pablo"):
- a. Northern end of the interface (Q-55): show the large events north of 17° S (1552, 1582, 1600-02-19 and 28, 1604, 1715, 1784, 1821, 1913) with their 17g classes, and the segment limits with the northern end at 17.6° and at 15.5° S. Recommended: extend; those events then need a checked class in CAT.
- b. The strip 45.6–46.15° S (D-DAT-02): how psha_chile8 classified the events there, and a rule.
- c. Crustal sub-class polygons (D-CLS-07, 09): export the psha_chile8 forearc, arc, backarc and Patagonia cut to the new crustal area into `data/raw/shapes/crustal_classes.geojson`; Pablo redraws them in QGIS (the western side comes from the edge); rerun.
- d. Scotia–Antarctic boundary (Q-54): one map of SC/AN and its PB2002 rates against the area and Ushuaia.

**Out of scope:** no catalogue changes and no classification run (CAT step 7 reads data-01 later); no changes in psha_chile8.

**Time:** nothing long; every step runs in seconds to a minute.

**Done when:** data-01 holds the edge, the two areas, the interface footprints, the grids and the sites; the check figures exist; a–d are answered or listed as left to do.

**Report:** below this brief, with the headings of CLAUDE.md.

## Report DATA_01 (19 Nov)

### Done
- Task 1: D1 inputs copied (not moved) into `data/raw/`: `slab2/` (top, thickness, uncertainty), `trenches/` (Nazca trench, PB2002 AN\SA and SC/AN extract; Pablo added the full PB2002 set: `pb2002_boundaries.dig`, `pb2002_plates.dig`, `pb2002_orogens.dig`, `pb2002_steps.dat`, readme and tables, bird 2003 "not read" beyond the readme), `outlines/` (Chile outline; arc polygon `intraarc.shp`, found in the repo `data/`), `faults/` (psha_chile8 `faults/` with mascsn26, CHAF, SARA, crustal_faults_chile, Riedel-Hornig), `basemaps/basemap_chile_gray/basemap_gray.tif` (+ tfw, aux; the 1 GB of other rasters left out), `grids/chile_005.csv` (the 0.05° site grid, repo `data/grids/`). psha_chile8 unchanged.
- Task 2: `src/psha9/data_processing/build.py` with `config/data.yaml` writes the run; `figs.py` draws the check figures. During the session the geometry moved from code into data (Pablo): the western edge, the interface footprints and both areas are now frozen shapes in `data/raw/shapes/`, made once by one-off scripts in `trials/data_shapes/`; the build copies them, cuts the areas to the edge, builds the Antarctic plane, the 0.1° grids and the site files.
- Task 3: three check figures (below), plus the figures for choices a, b, d.
- Choices a, b, d answered; c (crustal sub-class polygons) postponed by Pablo.
- Edits in `data/raw/shapes/` (all 19 Nov): new `western_edge.geojson`, `interface_footprints.geojson`, `interface_segment_limits.geojson` (psha_chile8 SEGS, now 45.55 to 17.1° S), `cities.geojson` (16 cities of D-HAZ-05, Arica −70.3126 −18.4783 added); `crustal_area.geojson` and `inslab_area.geojson`: Pablo's drawings, cut to the edge, northern sides at 17.1° S, in-slab southern side on the interface, Pablo's outer-rise inset in the crustal area, repeated nodes removed.

### Outputs
- `runs/data/data-01/`: `edge.geojson`/`.csv`; `crustal_area.geojson` (2.21 M km²), `inslab_area.geojson` (1.75 M km²); `interface_footprints.geojson` (margin and seg1–4, top at the edge, bottom 50 or 60 km; edge–50: margin 479,700 km², seg1 144,400, seg2 87,500, seg3 92,900, seg4 154,900); `interface_segment_limits.geojson`; `antarctic_plane.geojson` and `antarctic_plane_edges.csv` (5–50 km, 57,800 km²); `crustal_grid.csv` (22,768 cells), `inslab_grid.csv` (16,532 cells), centres on multiples of 0.1°; `sites_cities.csv` (16), `sites_grid.csv` (34,841, 17.5–55.9° S); `run.yaml`.
- One-off scripts (trial, not used by the pipeline, kept as the record of how the frozen shapes were made): `trials/data_shapes/make_shapes.py` (limits, cities), `freeze_geometry.py` (edge, footprints), `cut_areas.py` (areas to the edge, in-slab south; run once only), `tidy_shapes.py` (northern sides, nodes). Choice figures: `trials/data_choices/a_northern_end.png`, `d_scotia_antarctic.png` (`fig_d.py`). `trials/data_build/draft/` is a scratch build (trial, not used; can be deleted).

### Figures to look at
- `runs/data/data-01/figs/overview.png`: every area, the edge, segments (edge–50 km) and the Antarctic plane over the 17g catalogue (Mw ≥ 4.5). Compare with `trials/data_qgis/` layers.
- `runs/data/data-01/figs/zoom_45_47S.png`: 45–47° S with the 17g classes; the in-slab southern side lies under the seg1 line; the crustal inset leaves the Chile Ridge cluster outside.
- `runs/data/data-01/figs/areas_vs_psha8.png`: new areas against the psha_chile8 domains (`class_domains_2026-11-18`).

### Decisions with Pablo
- Western edge and interface delimitation first, then the areas; geometry frozen as data in `data/raw/shapes/`, "will be frozen as data, not got in code" (replaces deriving the footprints in each run, D-DAT-03). The edge is the Slab2 western edge smoothed over 5 rows (≤ 4.8 km shift), then the PB2002 AN\SA trench.
- a. Northern end: "End at 17.1° S" (not extended to 15.5° S). Interface, in-slab and crustal end at "the exact same latitude (17.1)". Arica 1868 (17.15° S) and 1604 are inside.
- b. Strip 45.6–46.15° S: "Yes, at 45.6° S": the Antarctic class starts where Slab2 and the Nazca interface end. Pablo then moved the interface and in-slab southern edge "a little bit north", to 45.55° S (the last Slab2 row dropped); the segment limits and the Antarctic plane follow. The Chile Ridge cluster is left out by an inset Pablo cut in the crustal area ("extract a small inset to avoid the outer rise").
- Areas: "I want them maximum until the basemap extent" (north and east sides redrawn by Pablo, east about 65° W); the in-slab southern side matches the interface; the crustal northern side snapped to 17.1° S ("snap it").
- Interface top: "scrap the 0/10 z0 branch, and just use the full interface now drawn for 0/60 and 0/50": the slab top at the edge is 6.5–10.8 km deep (median 8.6), so a 10 km top differs by 1–4 km. One top (the edge), bottoms 50 and 60 km (changes D-CLS-08 and D-IF-03; the top tornado row goes).
- Antarctic plane: "should stop at the trench, but yes at the depth of the trench (approximate, maybe 5km is okay ... this zone is really poorly constrained)": top on the trench at 5 km (Slab2 top at its southern end 6.4–10.5 km), bottom 50 km.
- c. Crustal sub-class polygons: "dont do crustal classes yet"; sub-crustal domains after the areas.
- d. Scotia–Antarctic boundary (Q-54): "No source for now". PB2002 gives SC/AN 12–15 mm/yr, convergence 15 mm/yr in the west to 4 mm/yr in the east; nearest point 236 km from Ushuaia.

### Questions for Pablo
1. Deep in-slab events east of the new in-slab area (about 65° W): 317 events of Mw ≥ 4.5 fall outside, among them the Santiago del Estero deep events of Mw 7.0–7.6 (1912, 1916, 1946, 1947, 1950, 1962, 1991, 2011). Recommended: keep them out if they are deep-focus (> 300 km, D-CLS-07), which matter little for hazard; otherwise move the eastern side to about 62.5° W.
2. Events north of 17.1° S now lie outside every source (550 in-slab of Mw ≥ 4.5, including 1552, 1582, 1600 ×3, 1784, 1821, 1914, 1922, 1958, 1960, 1979 of Mw ≥ 7; 70 crustal). Recommended: accept for now (D-CLS-10 `outside` for crustal; same for the others) and note it as a limitation for Arica.
3. Antarctic plane bottom: only 50 km (D-IF-10), while the Nazca interface has 50 and 60. Recommended: keep 50 only (poorly constrained, no tornado row).
4. The 25 Mw ≥ 4.5 outer-rise events of 17g at 45.3–46.3° S that are still inside the crustal area are near the trench east of the inset. Recommended: leave to CAT's classification (the in-slab/interface tests come first).

### Requests for other sessions
- CAT (step 7, reads data-01): Antarctic interface class from 45.55° S (not 46.15°); the 75 km ridge rule is replaced by the crustal area (shallow events west of it, no slab: outer rise, D-CLS-09); 17g puts most SC/AN events (e.g. 2025-05-02 Mw 7.5 Drake Passage) in the Antarctic interface class, D-CLS-09 says outer rise; crustal sub-classes not yet in data-01 (no `crustal_classes`); large events north of 17° S keep their class but are outside the source areas.
- IF: footprints from `runs/data/data-01/interface_footprints.geojson`, top at the edge only, bottom 50 / 60 km; segment limits 45.55, 37, 32, 26, 17.1° S; with the top at the edge the geodetic moment is about 10 % above a 10–50 km band (margin 479,700 vs 434,700 km²); Antarctic plane 5–50 km from 45.55° S, about 57,800 km², larger than the psha_chile8 10–50 km plane.
- IS: area and grid from data-01; the area's southern side is Slab2's end (in-slab south of 44.27° S is the edge–60 km band).
- HAZ: `sites_cities.csv` (16), `sites_grid.csv` (0.05°, copied from `data/grids/chile_005.csv`).
- Orchestrator: D-DAT-03, D-CLS-07 (46.15 → 45.55° S), D-CLS-08 and D-IF-03 (top at the edge, no top branch), D-IF-03 / Q-55 (northern end 17.1° S), D-IF-10 (plane 5–50 km, from 45.55° S), Q-54 closed (no source).

### Learnings
- psha_chile8 `data/SHA256SUMS` does not match its own `faults/faults_gem_extra_2026-11-15.{shp,shx,dbf,csv}` (the files changed after the sums); the copies in data/raw equal the current psha_chile8 files.
- Shapes made by sweeping (union of shifted copies) leave repeated nodes and a sawtooth on slanted sides and are not idempotent; build caps and cuts as single polygons instead.
- `conda run` does not pass a heredoc on stdin: write scripts to files.
- `run.yaml` lists `slab_top` under `reads` although the build no longer reads Slab2 (it is read by the freeze script); fix the reads list in the next run.

### Left to do
- c. Crustal sub-class polygons (forearc, arc, backarc, Patagonia) inside the new crustal area, drawn by Pablo; then a new run (data-02).
- Questions 1–4 above.

## Report DATA_01, second run (19 Nov): data-02 with the crustal sub-classes

### Done
- c. Crustal sub-class polygons in `data/raw/shapes/crustal_classes.geojson` (+ `.qml`): a rough first version from the arc of `data/raw/outlines/intraarc.shp` (continued north of 18.3° S with its width to 17.1° S), the forearc to the edge, the backarc to the eastern side, Patagonia south of 47.28° S (`trials/data_shapes/draw_classes.py`); Pablo redrew the arc (reaching 48.5° S into Patagonia, the south-eastern edges moved so the backarc is one polygon); the other three rebuilt around his arc so the four fill the crustal area exactly, with no gaps, overlaps or slivers (`trials/data_shapes/tidy_classes.py`).
- `runs/data/data-02`: data-01 plus `crustal_classes.geojson`; everything else identical to data-01 (checked file by file). `run.yaml` no longer lists Slab2 under `reads` (the build does not read it; the freeze scripts, CAT, IF and IS do; it stays in `data/raw/slab2/`).

### Outputs
- `runs/data/data-02/crustal_classes.geojson`: forearc 719,000 km², arc 434,000, backarc 657,000, Patagonia 405,000; one valid polygon each.

### Figures to look at
- `trials/data_choices/c_crustal_classes.png` (`fig_classes.py`): the four classes over the 17g crustal events (old 17g colours). The check figures of data-02 are the same three as data-01.

### Decisions with Pablo
- "Please draw me roughly the forearc, intraarc and backarc. Naturally the forearc fit to the western edge, and backarc to the eastern edge"; the arc is Pablo's ("I will make it reach further closer to the LOFS end"); "the top edge should continue its width approx at also end at 17.1".
- Slab2 depth, thickness and uncertainty stay in `data/raw/slab2/` for the classification.

### Questions for Pablo
1. Add the crustal classes map to the DATA check figures (a change of the figure set)? Recommended: yes, from the next run.

### Requests for other sessions
- CAT (step 7): read `runs/data/data-02` (sub-classes from `crustal_classes.geojson`, D-CLS-07); Patagonia now starts where the arc ends (the arc reaches 48.5° S).
- CR: class polygons from data-02 for the planes by class (D-CR-04).

### Learnings
- QGIS edits of adjacent polygons leave invalid or sliver geometry; rebuild the neighbours from the edited one (one drawn polygon, the rest derived) rather than drawing shared borders twice.

### Left to do
- Questions 1–4 of the first report and question 1 above.

## Report DATA_01, third run (19 Nov): data-05, Chile Rise inset

### Done
- Pablo moved one node of the crustal inset near the Chile Rise (edited in `runs/data/data-02/crustal_area.geojson`; runs are not edited, so the edit was carried into `data/raw/shapes/crustal_area.geojson`, cleaned of 75 repeated nodes; data-02's `crustal_area.geojson` now holds Pablo's edit, not the build output). The new inset also removes a wedge of 0.10 deg² (about 1,100 km²) at 45.05–45.56° S, 75.95–75.56° W next to the trench; the same wedge was cut from every interface footprint (margin and segments alike, they still match) and from the in-slab area (`trials/data_shapes/apply_inset.py`); the crustal classes rebuilt around Pablo's arc (`tidy_classes.py`).
- Build: outputs cleaned of repeated nodes (cutting at the edge repeated the shared nodes); grid cells now count when the centre is inside or on the boundary (`covered_by`; before, centres exactly on the edge flipped with node clean-up); test `tests/test_data_grid.py` (2 passed).
- data-03 and data-04 were superseded within the session (repeated nodes; boundary cells), never read, and deleted (Pablo).

### Outputs
- `runs/data/data-05`: seg1 edge–50 km 143,600 km² (margin 478,900); edge–60 km seg1 159,900 (margin 548,000); crustal grid 22,787 cells, in-slab 16,552; classes forearc 718,200, arc 433,600, backarc 657,300, Patagonia 404,900 km². No repeated nodes in any shape.

### Figures to look at
- `runs/data/data-05/figs/zoom_45_47S.png` (the wedge near 45.3° S); `trials/data_choices/c_crustal_classes.png`.

### Decisions with Pablo
- "I moved one node close to the chile rise, so the removed piece didnt look so rectangular"; IF, IS and the crustal classes adapted to it.

### Questions for Pablo
1. (answered) `runs/data/data-03` and `data-04` deleted (Pablo: "Yes, delete them").
2. The Antarctic plane is built from the trench and is not cut by the inset (it starts at 45.55° S, on the trench). Recommended: leave it as a plane.

### Requests for other sessions
- IF: seg1's western side at 45.05–45.56° S is now the inset line, not the trench; the top edge of the seg1 and margin sources follows the footprint there.
- CAT, CR, IS, IF, HAZ: read data-05.

### Left to do
- As before: questions of the first two reports.

## Report DATA_01, fourth run (19 Nov): data-06, northern end of the arc and backarc

### Done
- Pablo redrew the northern end of the arc and backarc (in `runs/data/data-05/crustal_classes.geojson`, which now holds his edit) and drew them past the crustal area's north-eastern side; the crustal area takes them in up to the northern limit, 17.1° S (+1.12 deg², about 13,000 km², at 17.1–18.7° S, 69.1–67.7° W; `trials/data_shapes/extend_area_ne.py`), so the northern side is straight at 17.1° S from the edge to 67.8° W; the classes rebuilt around his arc (`tidy_classes.py`).
- `runs/data/data-06`: only the crustal area, its grid and the classes change against data-05; in-slab, interface, edge and plane identical.

### Outputs
- `runs/data/data-06`: crustal grid 22,907 cells (+120); classes forearc 718,200, arc 435,500, backarc 668,500, Patagonia 404,900 km²; one valid polygon each, no repeated nodes, no gaps or overlaps.

### Figures to look at
- `trials/data_choices/c_crustal_classes.png`; `runs/data/data-06/figs/areas_vs_psha8.png`.

### Decisions with Pablo
- "I moved the northern most edge of the intraarc/backarc, so it looks more harmonious ... you can just simply bring them back to the latitude limit": classes cut only at 17.1° S, the crustal area enlarged to hold them.

### Requests for other sessions
- CAT, CR, IS, IF, HAZ: read data-06.

## Note (19 Nov)
- Pablo: "Let's stick with this. Delete the others". `runs/data/data-01`, `data-02` and `data-05` deleted, and the scratch `trials/data_build/`; `runs/data/data-06` was the DATA run (now data-07, below). Later fixes start from `data/raw/shapes/`.
- The 0.1° and 0.2° Chile site grids copied (not moved) from the repo `data/grids/` into `data/raw/grids/` (`chile_01.csv`, 9,361 sites; `chile_02.csv`, 2,590), next to `chile_005.csv`; available for coarse HAZ runs, not written into the DATA run (D-HAZ-07 names the 0.05° grid).
- Cities: Ushuaia replaced by Puerto Williams (−67.6167, −54.9333) in `data/raw/shapes/cities.geojson` (Pablo: "2. All chilean"; the site grid stays Chile-only). `runs/data/data-07` differs from data-06 only in `sites_cities.csv`; data-06 deleted. Orchestrator: D-HAZ-05 changes (16 cities, all Chilean; Ushuaia out, Puerto Williams in). Puerto Williams coordinates from memory, to check.
