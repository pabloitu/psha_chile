# Task A7: tectonic classification with class weights

Needs: the working catalogue `catalog/merged/catalog_2026-11-13d.csv` (or the rerun of step 0), `catalog/overrides_A6.csv` (accepted class hints), Slab2 in `data/slab_2.0/` (`dep`, `thk`, `dip`, `str`, and the depth uncertainty grid `unc`, on disk since 13 Nov), `sam_nazca_trench.shp`, `sam_antarctica_trench.shp`, the arc polygon `data/intraarc.shp`.

Read first: `CLAUDE.md`, `DECISIONS.md` (Classification; Catalog; Magnitudes), `LEARNINGS.md` (Old classifier; Working: the line on patch rules), `catalog/REPORT_A3-A5.md` section 6, `explore/X4/REPORT.md` (the exploratory classification: rules, variants, surprises), the project doc on the old classifier if on disk (`cat_handler_2/` is archive: read, never import).

## Goal

Every event gets a weight for each class (interface, in-slab, crustal, outer rise), adding up to 1, a sub-class, and the rule that decided it. Most events have one weight of 1. An event is split only where the data cannot decide: its depth is within its error of a class boundary, or it has no depth and position does not settle it.

Keep it to the few rules below. **No patch rules for single events:** if a check finds a wrong class for a named event, report it; the fix is a cited class hint in `overrides_A6.csv`, not code (LEARNINGS).

Write `catalog/classify.py` (rules) and `catalog/classify_check.py` (checks, figures), tested; start from `explore/X4/x4b_classify.py` but do not import from `explore/`. Settings at the top.

## Step 0: the CSN moment magnitude (GUC MW), before classifying

The rerun of 13 Nov showed that GUC MW is noisier than the other members (sd 0.20 against 0.14), reaches down to Mw 2.1 and moved the CSN ML relation; one event went from GCMT 5.39 to GUC MW 6.0. Change (Pablo, 13 Nov):
- **Fitting floor for every scale:** the conversion relations and the offsets are fitted only on pairs whose reference Mw is ≥ 4.0 (setting at the top; the catalogue starts at 4.5, and smaller events must not steer the fit). The floor is on the reference, which does not bias a native-on-Mw regression. Report each relation at native 4.5 / 5.0 / 5.5 with and without the floor.
- GUC MW is **not used to fit** the conversion relations or the offsets of the others.
- As the Mw of an event it comes **last among the measured moment magnitudes**: used only when the event has no other member of the family and no GCMT. The 0.3 cross-check stays.

Rerun `magnitude.py`, `magnitude_check.py`, `locate.py`. Log the count of Mw ≥ 4.5 in the domain against `2026-11-13c` and `2026-11-13d`, the five tests, and the events of Mw ≥ 6 that changed. Classify the rerun catalogue.

## Geometry per event

- Slab2 values at the epicentre: `top` (depth of the slab surface, positive down, from `dep`), `thk`, `dip`, `str`, `unc` (depth uncertainty of the surface). Bilinear; nearest node within 15 km at the edge of the model; else "no slab".
- `d = depth − top` (positive = below the surface), measured vertically.
- Position: west or east of the Nazca trench (Antarctic trench south of 46.15° S); inside the arc polygon, west of it, east of it; offshore flag from A4.
- First check, in the report: `dep` is the slab surface (it is about −5 km at the trench and deepens landward; well-located thrust events sit on it, step "Band" below), `thk` the plate thickness, `unc` the uncertainty of `dep` (USGS data release: "slab depth uncertainty grid").

## Rules

**R1. Literature first.** An event with an accepted class hint (`overrides_A6.csv`: Ruiz and Madariaga 2018 and the A6 sources) takes that class with weight 1. Its sub-class comes from position (R7). `cls_auto` keeps what the rules below would have given.

**R2. Outer rise.** West of the trench: outer rise, weight 1, with or without depth.

**R3. The mechanism says which classes are possible.**
- Thrust on the plate contact (one nodal plane within 35° of the Slab2 plane at the epicentre, rake 45–135°): interface, in-slab and crustal are possible.
- Any other mechanism: interface is not possible; crustal or in-slab.
- No mechanism: all three.
- Interface is possible only where the slab top at the epicentre is ≤ 50 km (the bottom of the interface source), and for the Antarctic interface (R7).

**R4. The band around the slab surface.** The interface zone is `|d| ≤ W`.
- First, measure it (figure and table): for events that are interface without using depth (thrust on the plate contact, and the Ruiz and Madariaga interface events with a measured depth), the distribution of `d`, for all sources and for the best depths alone (GCCEL depth codes n / l / d, ISC-EHB L1). Report the median (a bias of Slab2 or of the catalogue), the spread, the spread after removing the depth σ of the best sources, by latitude band and by slab-top range. Compare with the Slab2 `unc` at those events, and with the `d` of non-thrust events near the coast (they should lie mostly outside).
- Baseline: **W = the Slab2 depth uncertainty at the epicentre** (`unc`; median about 8 km where the top is above 20 km, 12 km at 20–50 km), a published, location-dependent value (Hayes et al. 2018). Variants for the sensitivity table: fixed 10, 15 and 20 km, and the width the measurement above suggests if it differs.
- If the measurement shows `unc` is clearly too narrow or too wide (for example fewer than about two thirds of the well-located thrust events within `W` plus their σ), say so and show the alternative; do not tune.

**R5. Depth and its error give the weights.** For an event with a measured (or A6) depth and σ:
- Zones along depth: above the band; the band; below the band down to `top + thk`; below the plate.
- Probability of each zone from a normal error on the depth (σ from the catalogue), then mapped to the classes that R3 allows:
  - above the band → crustal if not deeper than 50 km, else in-slab (a mislocated slab event);
  - the band → interface if allowed; otherwise crustal above the surface, in-slab below it;
  - below the band, and below the plate → in-slab (DECISIONS: below the slab counts as in-slab).
- **Hardening:** if one class has weight ≥ 0.8 it becomes 1 and the others 0. Otherwise the weights are kept (a split event). Report the count of split events with 0.8 and, as variants, 0.7, 0.9 and no hardening.
- No slab at the epicentre: crustal if not deeper than 50 km, else unclassified (weight 1 in `unclassified`, reported).

**R6. No measured depth.**
- West of the trench: R2. No slab: crustal, weight 1.
- Slab top deeper than 50 km and every rejected depth of the event ≥ 70 km (the agencies' deep defaults): in-slab, weight 1.
- Otherwise split weights among the classes R3 allows (slab top ≤ 50 km: interface, in-slab, crustal; deeper: in-slab, crustal), with the shares of the classified events (summed weights from R1–R5) in the same bin: slab-top range (≤ 50, 50–100, > 100 km), latitude band (17–24, 24–30, 30–38, 38–46° S), magnitude range (4.5–5.5, ≥ 5.5), events from 1976 on. A bin with fewer than 30 classified events borrows from the neighbouring magnitude range, then the neighbouring latitude band; say which did.
- No hardening for these.

**R7. Sub-classes (position only, no weights).**
- In-slab: `intraslab_shallow` (slab top ≤ 50 km at the epicentre), `intraslab_intermediate`, `jujuy_nest` (a class of its own: within 0.8° of 66.9° W, 24.0° S, depth 170–320 km, measured depth). Check the nest limits on this catalogue (map and depth histogram of the cluster) and report whether they still enclose it; do not change them without saying.
- Crustal: forearc (west of the arc polygon), arc, backarc (east), Patagonia (south of 46.15° S, or no Slab2 south of 44° S outside the arc).
- Interface: `interface` (Nazca), and `antarctic_interface` for completeness: south of 46.15° S, within 150 km landward of the Antarctic trench, not deeper than 60 km or no depth, no non-thrust mechanism. Its source uses the geodetic model only.
- An event split between families carries the sub-class it would have in each (`sub_interface`, `sub_inslab`, `sub_crustal`).

**R8. Assigned depth.** An event with a literature class and no measured depth gets `depth_kind = assigned`: interface → the slab top at the epicentre, kept within 10–50 km; in-slab → inside the slab by the convention of the in-slab sources (DECISIONS, In-slab); crustal → none unless the source gives one. σ 20 km. Assigned depths are never used by R4–R6 or by any check.

**Not in A7:** the double seismic zone (the planes are handled in the in-slab source model, plan C).

## Outputs

- `catalog/merged/classes_<date>.csv`: `event_id, w_interface, w_inslab, w_crustal, w_outer_rise, w_unclassified, cls` (the class with weight 1, else `split`), `cls_auto, rule, sub_interface, sub_inslab, sub_crustal, top, thk, unc, d, W, mech_kind, n_candidates`, and the assigned depth columns.
- `catalog/merged/catalog_<date>.csv` with these joined.
- `catalog/CLASSIFICATION.md`: the rules as applied (one short paragraph each), the band measurement, the counts, the sensitivity table, the references (Hayes et al. 2018 for Slab2 and its uncertainty; others only if read).
- DATA.md row (catalogue run, and "Other inputs": Slab2 version 02.23.18 with the five grids, the trench and arc shapefiles); MANIFEST rows; FIGURES.md rows for the paper candidates.

## Checks and figures (`figs/classify/`)

1. **Band measurement** (R4): histogram of `d` for thrust-on-contact events against the others, best depths marked; table by latitude and slab-top range.
2. **Counts:** summed weights per class and sub-class at Mw ≥ 4.5, ≥ 5.5, ≥ 7; number of split events by reason (near the band, no depth); the same against the X4 baseline and the old classifier (frozen catalogue of 2026-11-04, matched as in `x4b_compare.py`).
3. **Named events:** for the events with a literature class, what the rules alone give (`cls_auto`): right, wrong, split, no depth. List the wrong ones with the reason.
4. **Events of Mw ≥ 7:** table with weights, rule, depth kind; every one not at weight 1 listed for Pablo.
5. **Sensitivity** (summed interface, in-slab and crustal weights at Mw ≥ 4.5 and ≥ 5.5, and the events that change): W variants; hardening variants; interface limit 50 against 60 km; mechanisms used both ways (baseline), only to exclude, not at all; unknown-depth events split (baseline) against left out.
6. **Maps** per class (Mw ≥ 4.5, split events in their own colour) and **sections** at 20°, 23°, 27°, 31°, 33.5° and 37° S with pituPLOTS: Slab2 top with ± W and the plate bottom, events coloured by class, Mw ≥ 7 labelled. One palette entry and display name per class in `palette.py`.
7. **Weights add to 1** for every event; no event without a row.

## Tests (`catalog/tests/test_classify.py`)

Hand-made events: on the surface with a thrust mechanism (interface 1); on the surface with a normal mechanism (split crustal / in-slab, interface 0); far below (in-slab 1); 2 km below with σ 10 km and no mechanism (split); west of the trench without depth (outer rise 1); no depth over a shallow slab (weights equal to the bin shares); deep defaults over a deep slab (in-slab 1); a literature class overrides and keeps `cls_auto`; hardening at 0.8; the Jujuy nest; assigned depth not used by the rules.

## Running and end of session

Runs in full (expected minutes). WORKLOG entry as CLAUDE.md: step 0 results; the band measurement and whether `unc` holds as W; the counts; the list for Pablo (wrong named events, Mw ≥ 7 not at weight 1, bins that borrowed); proposed DECISIONS lines; commands; suggested `git add` and commit message. PLAN: leave the A7 box for Pablo.
