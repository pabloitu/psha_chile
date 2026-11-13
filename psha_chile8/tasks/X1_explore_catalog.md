# Task X1: exploratory analysis of A3–A5 (and a preview of A7 and B9)

Read first: `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (Catalog, Magnitudes (A5)), `LEARNINGS.md`, `catalog/PREFERENCES.md`, `catalog/SOURCES.md` (including the findings from the full download), `catalog/NOTE_SRuiz_2026-11-10.md`, `catalog/MAGNITUDE_PRIMER.md`, and `catalog/LITERATURE.md` sections 1–6.

## Purpose

This is an **exploration, not a step of the plan**. Pablo is away for a long time and will decide A3–A5 from what you find. Try many combinations of choices and assumptions, measure what each one changes, and summarize it in figures and one report. **Breadth and evidence matter more than polish.** Use the time: when a tier is done, go to the next one; when all are done, go deeper where the results were surprising.

Rules for this task:
- **Exploration code.** The frozen inputs are `catalog/sources/*_2026-11-10_*.csv` and `data/` (read only). All output goes to `psha_chile8/explore/X1/`. Do not change `catalog/` code, frozen files, DECISIONS, LEARNINGS or PLAN boxes.
- **Full runs are allowed and expected** in this task, including runs over all sources and all fits. CLAUDE.md's "Pablo makes the runs" is lifted for X1.
- **No questions.** Pablo can't answer. When a choice is needed, try the alternatives as variants. If that is impossible, pick one, write it under "Assumptions" in the report, and carry on.
- **Checkpoints.** Write intermediate tables to `explore/X1/cache/` (parquet or csv) so later tiers can resume without recomputing. If something fails, log it in the report and move on to the next item; don't stop the run.
- **Code style.** As CLAUDE.md: a few scripts by tier (`x1_match.py`, `x1_loc.py`, `x1_mag.py`, `x1_stats.py`, `x1_dsz.py`, `x1_report.py`), settings at the top, short names, minimal comments. Add tests in `explore/X1/tests/` only for the core functions: matching assignment, chi-square/orthogonal regression on synthetic data with known coefficients, triple collocation on synthetic data, and the Weichert and b-positive estimators on synthetic GR catalogs with known b.
- **Figure style.** As CLAUDE.md: Ubuntu font, shared palette (`palette.py`), pituPLOTS for maps and sections, comfortable margins, no code names in legends. Each figure answers one question, written in its title or caption in the report. PNG at 200 dpi.
- **Slab2:** `data/slab_2.0/` (South America depth, thickness and uncertainty grids if present). Trench: `data/shapefiles/sam_nazca_trench.shp`.

## Tier 1: A3 matching (events across catalogs, one ID per event)

1. **ID backbone.** Link ISC, ISC-GEM and ISC-EHB by their ISC event ID. Report the linked fraction per source and period, and how many links disagree badly in time or location (> 30 s or > 100 km). Check whether ComCat carries ISC-GEM or other foreign IDs that can be used as links too.
2. **Calibrate the windows from data.** Get the dt and dd distributions (and depth difference dz) for pairs that are known to be the same event:
   - ID-linked ISC / ISC-GEM / ISC-EHB origins
   - Potin against `csn_isc` (same agency's events, original against relocated location)
   - `csn` against Potin in the 2020-01-01 – 2020-07-16 overlap
   - GCMT reference hypocentre against ComCat, and GCMT centroid against the hypocentre

   Give the 95th and 99th percentiles per source pair, per period (before 1964, 1964–1975, 1976–1999, 2000–2014, 2015 on) and per magnitude band (< 5, 5–6, 6–7, ≥ 7).
3. **Variant grid.** Run the full matching for every combination of:
   - time window 5 / 10 / 20 / 40 s
   - distance window 25 / 50 / 100 / 150 km
   - scaling: fixed, or both windows widened for large events using the largest magnitude among the candidates (e.g. ×2 at M ≥ 7, ×3 at M ≥ 8; try two scalings)
   - assignment: greedy nearest, or one-to-one by cost (Hungarian per source pair and time block)
   - source order for building the event list: anchor-first (ID backbone, then Potin, then the rest), or all-pairs clustering (connected components with a one-per-source constraint)
   - windows per source pair taken from step 2 (data-calibrated), as an extra variant

   For each variant, report:
   - number of final events, in total and per year with M ≥ 4.5 (any native magnitude ≥ 4.5 as a proxy)
   - links per source pair
   - ambiguous cases (≥ 2 candidates in the window)
   - **probable split events:** final events of different IDs within 10 s and 50 km, with at least one M ≥ 5
   - **probable false merges:** linked origins with dt or dd above the 99th percentile of step 2, or magnitudes differing by > 1 (diagnostic only; magnitude is never used to match)
   - every M ≥ 6 merge, listed
4. **Hot spots.** Rerun the variants on the first month after Maule 2010, Illapel 2015 and Iquique 2014 (foreshocks and aftershocks), and on Arauco 2011 (the known CSN–GCMT duplicate, 6 s, 59 km). Show which variants get these right.
5. **RM18 matching** as in DECISIONS: dates corrected first (table in `NOTE_SRuiz`), Mejillones 1994 searched with day and month swapped, ±1 day and latitude within 2°. List each RM18 event with its matched event and the values of each source side by side. Unmatched events go in a review list.
6. **Baseline for the later tiers.** Pick the variant with the fewest split and false-merge diagnostics and call it the *X1 baseline* (not a decision). Also keep the two variants nearest to it, so tiers 2–4 can show how much the matching choice matters.

Figures:
- dt / dd / dz distributions per source pair, with percentiles
- events per year by variant
- split and merge counts across the variant grid (heatmap)
- maps of the hot-spot sequences coloured by event ID for 2–3 variants
- the RM18 side-by-side table rendered as a figure

## Tier 2: A4 location and depth

1. **Default depths per agency.** Find the spikes in the depth histograms automatically: 1 km bins, a bin counts as a spike if it exceeds k× the median of its ±5 km neighbours; try k = 3 / 5 / 10. Do this per source and agency, and per period where the agency changed procedure. Compare with the defaults listed in LEARNINGS and SOURCES. Output a table of defaults per agency, with the share of events at each.
2. **Location agreement on matched events (X1 baseline).** For Potin, ISC-EHB (by L1 / L2 / L3), ISC prime, ComCat, ISC-GEM, Centennial and GCMT centroid, compute the horizontal and depth differences against each other. Split by:
   - region: latitude bands of 2°; offshore / coast / forearc / arc / backarc (by distance from the trench, or by longitude against the arc polygon `data/intraarc.shp`); south of 44°S and south of 46°S
   - period and magnitude band

   Use ISC-EHB L1 as the depth reference where it exists. Estimate a per-source depth σ by region: the spread against L1, and three-way estimates (triple collocation) where three sources share events.
3. **Location priority variants.**
   - L-a: Potin first everywhere in its period.
   - L-b: Potin first only inside its well-resolved region (try 18–44°S and 18–46°S, west of the arc or of a longitude cut chosen from step 2), else ISC-EHB L1/L2, then ISC, then ComCat.
   - L-c: ISC-EHB L1 first wherever it exists, then Potin.
   - L-d: smallest estimated σ wins per event.

   For each variant: the depth relative to the Slab2 top for every event, in classes **above slab and shallow (< 30 km below the surface), interface band (±15 km of the top where the top is < 60 km), in slab, below slab, unknown depth** (a simple proxy, not the A7 classification). Report how many events, and how many M ≥ 5.5, change proxy class between variants, by region.
4. **Unknown and fixed depths.** Count events whose chosen depth is a default or fixed, by period and region and by variant, with the defaults from step 1 treated as unknown.

Figures:
- depth histograms with detected spikes per agency
- maps of median horizontal offset and depth offset per 1° cell, Potin against ISC-EHB L1
- depth difference against latitude
- proxy-class change between variants (bars by region)
- 4–6 trench-perpendicular sections, at about 20°S, 23°S, 27°S, 31°S, 33.5°S and 37°S: Potin, ISC-EHB and ComCat depths against the Slab2 top and bottom, 50 km strip either side

## Tier 3: A5 magnitudes

Follow the "Magnitudes (A5)" decisions as the main line and explore the alternatives around them.

1. **Inventory.** Every native magnitude type per agency in the frozen tables (ISC Bulletin all agencies, `csn`, `csn_isc`, Potin codes, ComCat, ISC-GEM, Centennial, GCMT, Cabello natives). Give counts per year and per magnitude band, and the period each type is used. This is a figure (type × year raster) plus a table.
2. **Pairs.** Build the pairs for each native type against GCMT Mw, and against CSN Mww and USGS Mww (raw, and after removing their median offset to GCMT), on X1-baseline matched events. Report n per type, split by depth (≤ / > 50 km) and by period. Compare with the two neighbouring matching variants, to see whether the pairs, and so the relations, change with the matching.
3. **Reference below Mw 5.4.**
   - CSN Mww and USGS Mww against GCMT, by magnitude band: offset, scatter, slope.
   - Can they extend the reference to Mw 4.5–5.4? With what σ?
   - Does GCMT Mw < 5.4 look biased high against the W-phase values (Lolli 2014, 2023)?
4. **Measurement errors per scale.** Triple collocation, for example on CSN ML, ISC mb and NEIC mb with GCMT or Mww, or any triple with ≥ 100 shared events; also the station spread where `mag_err` or `n_sta` exist. The cat_handler_2 night run did triple collocation on 893 events (read it in the archive, copy the method, don't import it). Output σ per scale and the error ratio η for each pair.
5. **Fits per scale.** For every scale with ≥ 30 pairs:
   - methods: OLS (as a contrast), chi-square / general orthogonal regression with η from step 4, and with η = 1
   - forms: linear, quadratic, exponential Mw = exp(a + b·x) + c
   - splits: none, by depth, by period, by both
   - equation-error correction (Gasperini et al. 2025) where an assumed error is ≤ 0.1

   Report for each fit: coefficients with bootstrap CIs, residual σ, AIC/BIC, and residuals against magnitude and against time.
6. **Published relations as a check.** Overlay the relations from LITERATURE section 2 (Lolli et al. 2014, 2023; Di Giacomo et al. 2015; Scordilis 2006; Cabello's printed and found-in-file relations; Weatherill 2016 where it applies) on each scale's pairs. Give their bias against our pairs at 4.5 / 5 / 5.5 / 6.
7. **Specific checks from A2:**
   - Potin codes `l`, `c`, `W`, `ww`, `B` against GCMT, CSN Mww and csn_isc: infer what `W` and `B` are; check ML ≈ Mc − 0.25 in the overlap; check whether Potin magnitudes differ from csn_isc GUC ML on the same events (was something homogenized?).
   - CSN web `Ml` vs `Mlv` in 2026: are they the same?
   - CSN coda Mc to ML across the 2000–2002 change.
   - ISC mb saturation curve from our pairs, against Lolli 2023 (−0.19 at 5.5, −0.43 at 6.5).
   - NEIC Ms change in 2013.
   - Heaping: native-value histograms and the effect of dithering on converted values.
   - ISC-EHB has no Mw in 1985–1998: confirm GCMT covers it.
8. **Mw catalog variants.** Build one Mw per event on the X1 baseline for each variant:
   - M0: the DECISIONS line (chi-square, exponential form where AIC/BIC prefer it, hierarchy direct Mw > smallest-σ proxy; before 1976 RM18 > ISC-GEM > Centennial converted > Cabello; dithering; σ per event)
   - M1: as M0 with OLS
   - M2: as M0 with linear forms only
   - M3: as M0 without depth or period splits
   - M4: published relations instead of our fits (best-matching one per scale)
   - M5: as M0 but a σ-weighted mean of all available proxies in place of the hierarchy
   - M6: as M0 with Mww below 5.4 used as reference (if step 3 supports it)
   - M7: Cabello's own Mw on the same events (reference only)
   - M8: as M0 with Centennial before ISC-GEM before 1976

   Compare the variants:
   - Δ Mw per event against M0, as distributions by period and source
   - frequency–magnitude distributions by period
   - N(≥ 4.5, ≥ 5, ≥ 6, ≥ 7) per decade
   - events crossing the 4.5 cut

Figures:
- type × year raster
- pair scatter plots per main scale, with all fitted forms, the published relations and the 1:1 line (one panel per scale; split panels where a depth or period split is preferred)
- residuals against time per scale
- Mww against GCMT by band
- triple collocation σ bars
- Δ Mw distributions across variants
- FMDs per period for M0–M8

## Tier 4: preview of B9 (only to see whether the A3–A5 choices matter)

Not the B-step analysis: quick, standard estimators, so Pablo sees which upstream choices move b and the rates.

1. **Proxy families** from the tier-2 proxy classes (L-a and L-b): crustal-shallow, interface band, in-slab (all depths), and in-slab split at 70 km.
2. **For each Mw variant (M0–M8) and each of the 3 matching variants × 2 location variants** (keep the product manageable; drop combinations that are too slow and say so):
   - Mc by maximum curvature + 0.2, by b-stability, and by Clauset KS, in time windows (≤ 1964, 1964–1975, 1976–1999, 2000–2009, 2010 on)
   - b and a by Weichert with a completeness table built from those Mc (steps spaced ≥ 0.3), and by b-positive
   - both with and without Tinti–Mulargia weights (σ per event)
   - both full catalog and Gardner–Knopoff declustered
3. **Report:**
   - b against fit floor (4.5–6.0) curves
   - N(≥ 7), N(≥ 8) fitted against observed per family
   - a tornado-style figure: which upstream choice (matching, location, magnitude variant, weights, declustering) moves b and N(≥ 6) the most, per family

## Tier 5: preview of A7 (double seismic zone)

1. **Data.** Potin events, and ISC-EHB L1 events in the slab, at 18–40°S in 1° bands.
2. **Distance below the slab top.** For each band, the histogram of the distance below the Slab2 top, as depth and as distance normal to the slab, in depth ranges 40–80, 80–120 and 120–200 km.
3. **Two-plane test.** Bimodality by a two-component Gaussian mixture, with BIC against one component, and the plane separation where two win. Map the bands where a lower plane is detected, with its depth range.
4. **Sensitivity** to the location variant (L-a vs L-b) and to Slab2 uncertainty (± the uncertainty grid, if present).

Figures:
- Sections at the six latitudes of tier 2, 50 km strip, Potin only, coloured by distance to the slab top.
- A summary strip plot: latitude against depth range, showing where one or two planes are found.

## Report

`explore/X1/REPORT.md`, written for Pablo to read on return:
1. A one-page summary: the 10–15 most important findings, each with its figure.
2. Per tier:
   - what was tried
   - what changed and by how much
   - surprises
   - **what this suggests for the decision**, with the evidence and the alternatives. Pablo decides; phrase these as options, not as decisions.
3. **Assumptions:** every choice you had to make without asking.
4. **Failures and skips:** what didn't run and why.
5. Run times and output sizes.

Also produce `explore/X1/figures_index.md`: one line per figure (file, question it answers).

## End of the session

- WORKLOG entry as CLAUDE.md:
  - what ran
  - where the outputs are
  - commands to rerun each tier
  - proposed DECISIONS / LEARNINGS lines, if any (as proposals)
  - suggested `git add` (scripts, REPORT, figures index, small tables; not the cache)
- `explore/` gets a `.gitignore` for `cache/`.
- No PLAN ticks; X1 is not a plan step.
