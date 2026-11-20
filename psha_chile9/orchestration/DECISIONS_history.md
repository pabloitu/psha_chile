# DECISIONS history

Superseded rules, each with the id of the rule that replaced it and the date.

## From psha_chile8, Scope and Catalog (moved 18 Nov)
- Pseudo-prospective testing in the same paper (24 Oct) → out of the paper (D-SCO-01).
- The model goes to Renta Nacional later as a separate project (8 Nov) → not a rule of this project.
- Nothing from cat_handler_2 carries over as a rule (8–9 Nov) → cat_handler_2 no longer used at all (D-CAT-01).
- Cabello not used for events from 1900 on; before 1904 Cabello only (8 and 13 Nov) → one split at 1904 (D-CAT-02).
- Potin et al. (2024) magnitudes not used: the CSN values already in ISC (11 Nov) → which copy of the CSN magnitudes to use is Q-36 (D-CAT-03).
- Large events left as they are, as an in-slab Mmax sensitivity case (1918-05-20, 1925-05-15, 1934-03-01, 1948-05-11, 1971-06-17; 13 Nov); dropped on 18 Nov → reinstated through D-CAT-15.
- Deep Abe-converted magnitudes stay as converted (18 Nov, CAT) → native magnitudes only (D-CAT-15, under review).
- Non-earthquakes removed with every record matched to them (11 Nov) → kept as class `non-earthquake` (D-CAT-10).
- Duplicate rules: same source twice within 2 s / 50 km; Potin-only or CSN-only records 50–150 km from an ISC event; lone single-agency ISC copies within 10 s / 100 km (11 and 17 Nov) → one rule (D-CAT-09).
- Depth: ISC-EHB L3 not a measurement; before 1964 only ISC-GEM quality A / B and free-depth Centennial (13 Nov) → under review (D-CAT-14, Q-42).
- Per-event batches of 13–17 Nov (A6, A9, final batch): values and references in `overrides_A6.csv`; Pablo's calls in D-CAT-19.
- Frozen catalogues 2026-11-14, 16, 16b, 16c, 16e, 17c, 17e, 17f, 17g, with their "everything reads …" lines; every catalogue run recorded in `DATA.md`; frozen source tables committed to git (9–18 Nov) → runs in `runs/catalog/`, git rule D-ORC-02.


## From psha_chile8, Magnitudes and Classification (moved 18 Nov)
- The weighted mean of the converted scales as a sensitivity case (11–12 Nov; never built) → scrapped (Pablo, 18 Nov); one converted scale per event (D-MAG-02).
- Fits run with and without the split events (12 Nov; not done since 15 Nov) → a check figure (D-STA-15).
- No-depth forearc rule "before 1900" (16 Nov) → before 1904 (D-CLS-06).
- Crustal assigned depth "none, unless the literature gives one" (13 Nov) → 10 km (D-CLS-02).
- Outer rise only for no-depth events west of the trench (13 Nov) → every event west of the trench, weight 1 (D-CLS-01).
- Chile Ridge outer-rise box, 75 km east of the trench at 45.5–46.15° S (16 Nov) → the forearc polygon starts east of them (D-CLS-09).

## From psha_chile8, Statistics (moved 18 Nov)
- Completeness tables of 15 and 17 Nov, with the step 8.0 from 1500 (dropped 17 Nov: two methods do not support it) → measured instrumental steps and 7.0 / 7.5 / 8.5 historical steps (D-STA-02, 03).
- Measured steps on 17g: margin 5.0 from 1981, 5.1 from 1964; 26–17.6° S 5.0 from 1964; 32–26° S 5.0 from 1976, 5.2 from 1964; 37–32° S 5.0 from 1964; 45.6–37° S 5.0 from 1999, 5.2 from 1964 → a property of each run, in `runs/fits/`.
- Fit files `fits_2026-11-15*`, `16`, `16d`, `16e`, `16f`, their declustered and pad tables, and declustered catalogues `gk_family_*`, `nn_family_*` (15–16 Nov) → runs in `runs/fits/`.
- Bins above Mmax left out of the likelihood (15 Nov) → under review (Q-52).
- Tapered list ending at Mmax + 0.2 as part of the fits (15 Nov) → discretisation in the source stage (D-STA-11).
- Large-event check with a negative binomial band (17 Nov) → under review (Q-52).
- Declustering as one tornado factor with two options, GK and NN, at 0.5 / 0.5 (15 Nov); NN most likely for every use (17 Nov) → Q-13, Q-14.
- Rules not used: Stepp, change points, joint likelihood, Ogata–Katsura, declustered tables, crustal-only table, arc by latitude, later historical steps (15–18 Nov) → tried in trials (D-STA-14).

## From psha_chile8, Interface (moved 18 Nov)
- Fixed corner 9.6 (Bird and Kagan 2004) → the Mmax rule and Kagan corner (D-STA-10).
- χ weights 0.125 / 0.25 / 0.125 of the total (6 Oct) → equal weights (D-IF-02).
- Mmax values per segment on catalogue 16c (9.7, 9.2, 8.7, 9.1) → a property of each fits run.
- Source folders `nrml_2026-11-16c`, `nrml_2026-11-18` and the 57 × 3 branch count → runs in `runs/interface/`.
- Intention of 16 Nov: declustered fits only as tornado rows → full / declustered 0.5 / 0.5 in the tree (D-IF-08).
- Z_TOP 10 / Z_BOTTOM 50 fixed (6 Oct) → tornado rows (D-CLS-08).
- Aspect ratio 1 fixed (15 Nov) → 2 as a tornado row (D-IF-06).

## From psha_chile8, In-slab (moved 18 Nov)
- Two fixed N–S nodal planes, 60° W normal and 30° E reverse (30 Sep); planes mixed per cell by class share; two planes per class (HAZ handoff, 18 Nov) → one plane per sub-class (D-IS-07).
- Fixed 25 neighbours for the in-slab kernel (Sep) → calibrated n (D-IS-01).
- Depth cells of weight-1 events (`depth_cells_2026-11-16.csv`) and the C14 one-layer files → class-weighted depth model (D-IS-04), one layer a tornado row.
- Declustered catalogue only for the pattern (Marzocchi and Taroni 2014; Sep–24 Oct) → also a declustered rate branch (D-IS-09).
- File and folder names (`depth_cells_*`, `npd_*`, `class_share_*`, `model/inslab/nrml/*`) → runs.
- "The in-slab Mmax comparison case is not built" (18 Nov) → D-IS-13.

## From psha_chile8, Crustal, faults and Magallanes–Fagnano (moved 18 Nov)
- Declustered crustal rates a tornado row only (7 Oct, 16 Nov) → full / declustered 0.5 / 0.5 (D-CR-02).
- Nodal planes mixed per cell by class rates (16 Nov) → the plane of the cell's class (D-CR-04).
- In-slab pattern T_c from the fit steps (18 Nov) → full table with historical steps (D-IS-03).
- Multi-fault ruptures not in the model (Oct) → a fault system branch (D-CR-11).
- Wells and Coppersmith 1994; the class maximum as a fault variant; the old "observed + 0.2" fault Mmax branch (Oct–16 Nov) → Leonard (D-CR-10).
- 12 km 3-D taper around faults (15 Nov) → no taper (D-CR-13), under review (Q-64).
- Seismogenic thickness 10 / 20 km at 0.5 / 0.5 (15 Nov) → 20 km (D-CR-12), under review.
- Source Mmin 5.5 for the tornado; Mmin 4.9 or 5.0 open (16–17 Nov) → 5.0 (D-CR-04).
- Rates of fits 16e per class (N(≥ 5) forearc 3.48, arc 1.38, backarc 0.40, Patagonia 0.20) and the 1949 doublet check → run properties.
- 120-path and 60-path crustal trees, `model/crustal/nrml/2026-11-18*`, database file names → runs.
- Liquiñe–Ofqui Holocene rates not used (15 Nov) → under review (D-CR-08, Q-23).
- MASCSN26 restoration details (FaultQuake inputs, M0 constant 9.1, 0.05 low bins; SCC tree 1.0 / 0.75 / 0.5) → method notes for CR (`docs/methods/`).

## From psha_chile8, GMMs, Logic tree, Hazard runs, Testing, Figures (moved 18 Nov)
- GMM tree AG20, Parker, Kuehn, Montalva 0.25 each, equal weights without residuals (6 Oct) → GMM-FIT (D-GMM-01); GMM-1R a comparison.
- Branch rule ≥ 5 % change at some city (6 Oct) → 10 % spread (D-LT-01).
- psha_chile6 final tree as the starting tree (8 Nov) → 17 Nov verdicts (D-LT-08).
- Verdict table process of 16–17 Nov (HAZ writes verdicts, context decides) → the tornado stage reports, the orchestrator writes the decisions.
- Mmax pad and source Mmin 5.5 in every branch (16 Nov) → tornado only (D-HAZ-03).
- 14 cities with Puerto Williams (30 Sep) → 16 cities (D-HAZ-05).
- Testing: pseudo-prospective test and the branch-spread test (8 Nov) → out of the paper (D-SCO-01).
- Figures: pituPLOTS figures, FIGURES.md manifest, palettes, catalogue and fit figure rules (2–18 Nov) → ported code and `docs/FIGURE_STYLE.md` (D-FIG-01).

## From the LEARNINGS review (18–19 Nov)
- Single-fault MFD shapes as a tree branch, 1/6 each (6 Oct) → one reference shape in the tree, the six shapes as a tornado row (D-CR-11, D-CR-14).
- D-ENV-01 "OpenQuake 3.27 on every machine (pansito, rs1, rs28, rs37), in `psha9`" (18 Nov) → 3.26.2, the latest release; 3.27 was a development commit (Pablo, 19 Nov).
- D-ENV-01 "OpenQuake 3.26.2 installed with --no-deps into a conda environment" (19 Nov) → pip with OpenQuake's pinned file, Python 3.12, lock file and wheelhouse (Pablo, 19 Nov).
- D-ENV-01 "pip with OpenQuake's pinned file, requirements.lock and wheelhouse" (19 Nov) → conda-forge only with an explicit lock: GEM's wheel server was down and its GDAL wheel exists nowhere else (Pablo, 19 Nov).

## Moved 19 Nov
- D-CLS-08 The interface depth range (top 10 km, bottom 50 km now) and the shallow / intermediate boundary are classification settings, so a sensitivity case can change them; the classification and the assigned depths follow. Tornado rows: top 0 / 10 km, bottom 50 / 60 km (Q-47) (18 Nov). → the interface band is fixed (edge to 60 km); top and bottom only move the ruptures (D-CLS-08, Pablo, 19 Nov).
- D-CAT-06 "Review in DATA, Q-40: a collection area for the fits and a forecast area for the sources" → one collection area; each area is its own fit and forecast area (D-DAT-01, Pablo, 19 Nov).
- From DATA_01 (Pablo, 19 Nov):
  - D-DAT-01 One collection area, the catalogue box (D-CAT-06). Each family's area (crustal, in-slab) and each interface segment polygon is both its fit area and its forecast area: the sources cover exactly what was fitted, with no separate source crop. Crustal and in-slab areas differ: in-slab follows Slab2, crustal the upper plate; Pablo draws both in `data/raw/shapes/` (`crustal_area`, `inslab_area … → D-DAT-01 of 19 Nov.
  - D-DAT-02 One western edge for every area and source: the western edge of the slab model, Slab2 north of the triple junction and the D-IF-10 plane (PB2002 Antarctic trench) south of it. The crustal area (so the forearc), the in-slab area and the interface segments are cut to it in DATA; Pablo draws only north, south and east sides. Outer rise is an event with no slab under it. Slab2's edge lies wit … → D-DAT-02 of 19 Nov.
  - D-DAT-03 Interface footprints are not drawn: each is derived in DATA from Slab2 between the depth contours of the setting (D-CLS-08) and cut along strike by the segment limits, the only interface shapes Pablo draws (Pablo, 19 Nov). → D-DAT-03 of 19 Nov.
  - D-CLS-08 The interface class is one fixed band: on the slab top, from the slab model's western edge (D-DAT-02) down to 60 km, the unequivocal definition of the slab interface. The interface top (0 / 10 km) and bottom (50 / 60 km) are source-geometry settings only: they move where interface ruptures sit, never the classes or the fits, so no rate moves into crustal or in-slab sources. The shallow /  … → D-CLS-08 of 19 Nov.
  - D-CLS-10 Crustal events outside the crustal source area take the sub-class `outside`, which nothing reads, so rate, pattern and sources cover one region (review in DATA, Q-25 / Q-40) (16 Nov). → D-CLS-10 of 19 Nov.
  - D-IF-03 Geometry: full margin or four segments, 0.5 / 0.5; complex faults on the Slab2 top, 10–50 km (tornado rows D-CLS-08). The sources end at 17.6° S; Arica 1868 (17.15° S) counts only in the margin fit. Review in DATA, Q-55: extend the northern end to cover Arica 1868 (Sep, 18 Nov). → D-IF-03 of 19 Nov.
  - D-IF-10 Antarctic interface: PB2002 trench, dip 30°, 10–50 km; geodetic only (it matters in the south): χ 0.5, 1.8 cm/yr (IF cites the source of the rate), b of the southern segment of the same branch, Mmax 8.5 from the area; always on, not a tornado factor. No outer-rise source; no Scotia–Antarctic source (Oct–18 Nov). → D-IF-10 of 19 Nov.
  - D-HAZ-05 16 cities: Arica, Iquique, Antofagasta, Calama, Copiapó, La Serena, Valparaíso, Santiago centro, Santiago Peñalolén, Concepción, Pucón, Puerto Montt, Hornopirén, Puerto Aysén, Punta Arenas (−53.16, −70.91), Ushuaia (−54.80, −68.30). The lowest intensity level is extended for the far south (30 Sep, 17 Nov; Arica Pablo 18 Nov). → D-HAZ-05 of 19 Nov.
  - D-IS-11 Grid: the cells cover the slab; 13 % of the intermediate weight lies outside, under the Pampean flat slab. DATA extends the grid over Slab2 (Q-26) and sets how far the collection area reaches (Q-40) (18 Nov). → D-IS-11 of 19 Nov.
  - D-CLS-07 "Antarctic south of 46.15° S" and "crustal polygons, review in DATA" → 45.55° S and the drawn crustal classes (D-CLS-07, 19 Nov).
  - D-CLS-09 "the forearc polygon starts east of the Chile Ridge events"; "whether SC/AN needs a source is Q-54" → the crustal area's inset; no SC/AN source (D-CLS-09, 19 Nov).
  - D-CR-15 "reported at Ushuaia only (Puerto Williams out of the city set)" → reported at Puerto Williams (D-HAZ-05, 19 Nov).
