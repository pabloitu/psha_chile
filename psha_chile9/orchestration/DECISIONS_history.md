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
