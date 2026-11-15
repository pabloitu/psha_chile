# Task B9: earthquake statistics per class, a broad exploratory run

Input: the frozen catalogue `catalog/frozen/2026-11-14/catalog_2026-11-14c.csv` (one row per event, Mw with σ, class weights, sub-classes). Read it, never change it.

Read first: `CLAUDE.md`, `PLAN.md` (B), `DECISIONS.md` (Magnitudes, Classification, Interface, In-slab, Crustal and faults, Logic tree), `LEARNINGS.md` (Completeness, b-value and rates, Declustering, Fits pitfalls), `catalog/frozen/2026-11-14/DECISIONS_NOTE.md`, `catalog/CLASSIFICATION.md`, `catalog/MAGNITUDES.md`.

## Purpose

An **exploration, not a decision**: for each class, find from which magnitude and which year the catalogue is complete, and what rates and b-values the main methods give. Try many variants, measure what each changes, summarize in figures and one report. Pablo picks the methods afterwards (B10). Work in `explore/B9/`; nothing under `catalog/` changes. Full runs are allowed in this task. No questions: where a choice is needed, try the alternatives as variants, or pick one and write it under "Assumptions". Checkpoint intermediate results in `explore/B9/cache/` so a stop can resume; log failures and move on.

Code style as CLAUDE.md: a few scripts by part, settings at the top, short names. Tests in `explore/B9/tests/` only for the estimators: Weichert, b-positive and the completeness methods recover known Mc, b and a on synthetic Gutenberg–Richter catalogues with time-varying completeness and with weighted events.

## Step 0: two loose ends from A8 (small, first)

1. The count of local records dropped by the 50 km check: 94 in the rewritten notes, 85 in DECISIONS and the paper draft. Find the right number on the frozen run and propose the correction (WORKLOG; do not edit DECISIONS).
2. Read `catalog/REPORT_A3-A5.md`, `MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md` and `paper/CATALOG_SECTION_draft.md` against the frozen run and `DECISIONS.md`; list every number or statement that disagrees, and the "[to check]" marks, in the WORKLOG. Do not rewrite them.

## Classes and data

- Families and sub-classes from the weights: interface (Nazca; the Antarctic interface only reported, it has no catalogue source), in-slab shallow, in-slab intermediate, Jujuy nest, crustal forearc, arc, backarc, Patagonia, outer rise (reported only).
- **An event counts in a class by its weight.** Every method must accept weighted events. Each result is computed twice: all events (split weights included) and only events with weight 1 in that class (DECISIONS: fits with and without the split events).
- Magnitudes on the 0.1 grid as in the catalogue; keep σ per event for the error correction.
- Domain as in the catalogue (`in_domain`).

## Completeness in time: the historical record is needed for the interface

The interface rates at large magnitude rest on the historical earthquakes (Ruiz and Madariaga 2018; Cabello before 1904; Centennial and ISC-GEM from 1904). So completeness is **a table of steps reaching back in time for the larger magnitudes**, not one Mc:

| magnitude from | complete since (to be tested) |
|---|---|
| ~4.5–5.0 | 1964–1990 (network history) |
| ~5.5–6.0 | 1930–1964 |
| ~7.0 | 1900–1930 |
| ~7.5–8.0 | 1700s–1850s (historical; literature) |

Explore, for each class:
1. **Data-driven steps** from 1964 on: Stepp (1972), cumulative rate by magnitude band against time (breaks found by eye and by a change-point test), Kolmogorov–Smirnov / b-stability Mc per window. Maximum curvature reported but not trusted (LEARNINGS: it was pinned by conversion artefacts).
2. **Network history steps** (CSN changes 2000, 2007, 2012; GCMT 1976; ISC rebuild 1964) as the alternative set of periods.
3. **Historical steps for the interface (and the large in-slab events):** completeness years for M ≥ 7, 7.5, 8 from the literature (Lomnitz 2004 and Ruiz and Madariaga 2018 in `LITERATURE.md`; Cabello et al. 2025 bands) and from the data (cumulative count of the large events against time, by segment). Report two or three candidate historical tables and how much each moves the rates at M ≥ 7.5 and 8.
4. Rules from LEARNINGS: steps at least 0.3–0.5 apart; anchor the rate at the first complete magnitude; one basis (full catalogue) for both Mc and rates.

## Completeness methods compared

Run every method below on each class (and on the interface segments), and compare the tables they give, not only the Mc values. Where a method gives one Mc per window, turn it into a step table with the same rules (steps ≥ 0.3 apart, monotone back in time).

| method | what it gives | note |
|---|---|---|
| Stepp (1972) | year from which each magnitude band's rate is stable | the classic for historical catalogues |
| Cumulative count per band against time, change-point test | break years per band | visual and objective version of the same idea |
| Maximum curvature (+0.2) | Mc per window | report only (LEARNINGS) |
| Goodness of fit (Wiemer and Wyss 2000) | Mc per window at 90 / 95 % fit | |
| b-stability (Cao and Gao 2002; Woessner and Wiemer 2005) | Mc per window | |
| Kolmogorov–Smirnov (Clauset et al. 2009) | Mc per window | the psha_chile5–6 basis |
| Entire-magnitude-range, EMR (Woessner and Wiemer 2005) | Mc, b, a jointly, with the detection curve below Mc | uses the incomplete part instead of cutting it |
| Ogata and Katsura (1993) | joint b and detection function | as EMR, parametric |
| Kijko and Smit (2012) / Kijko–Sellevoll (1989) | b and rate from sub-catalogues with their own Mc, historical part included | LEARNINGS: erratic at high floors; check |
| Albarello et al. (2001) or Stucchi et al. (2004) style historical completeness | completeness years of the historical part from the stability of the large-event rate | for the interface before 1904 |
| b-positive / a-positive (van der Elst 2021; van der Elst and Page 2023) | b and rate without a completeness table | the table-free reference |
| Network history | steps at known network changes | the alternative to data-driven steps |

Compare them by:
1. the step tables they give per class, drawn on the magnitude–time plot;
2. Weichert b, a and N(≥ 6, 7, 8) with each table;
3. the large-event check and the stationarity check (below);
4. how stable each is to the fit floor and to the split events;
5. recovery of known tables on synthetic catalogues that copy our periods and our magnitude errors (the tests of this task).

Use existing implementations where they are trustworthy (SeismoStats is in the repo as vendored code: read it, copy what is needed into `explore/B9/`, do not import from the vendored folder unless it imports cleanly; snap magnitudes to the 0.1 grid first, LEARNINGS). Say which method came from where.

## Completeness in space

Mc on a map for the interface and the in-slab families (from 1990 and from 2010), and whether a regional table (north, central, south, far south) is needed.

## b-value and rates

For each class and each completeness table:
- **Weichert (1980)** with the time-varying table, weighted events: b, a, N(≥ 5, 6, 7, 8) with bootstrap errors (not b/√N).
- **b-positive** (van der Elst 2021) as a table-free check.
- **b against fit floor** (4.5 to 6.0), per period.
- **With and without the magnitude-error correction:** the CEUS-SSC (2012, §3.3.1) procedure for observed magnitudes (shift to M − βσ², then N*). Check the equations against the report first and write them in the report; if the report is not on disk, implement the plain weight exp(−β²σ²/2) and say so.
- **Interface only:** the fits are needed down to the segment level later; report the margin total and the four segments of DECISIONS (Interface, geometry).

## Declustering

Gardner–Knopoff (1974) and one alternative (Reasenberg 1985 or Zaliapin–Ben-Zion). Rates and b from the full catalogue (DECISIONS); the declustered catalogue is reported for comparison and for the spatial pattern only. Show the declustered b and the share removed per class.

## The checks that decide

1. **Large events:** fitted against observed N(≥ 7) and N(≥ 8) per class and per completeness table, with the Poisson band. The interface must reproduce the historical great earthquakes.
2. **Stationarity:** the rate above the first complete magnitude per period (1964–75, 1976–89, 1990–99, 2000–10, 2011 on), against Poisson.
3. **Weights:** how much the split events move rates and b (all against weight-1 only).
4. **Sensitivity:** the known catalogue cases: mb read 0.1 high before 1990 (floor 5.5 before 1990, or those values lowered by 0.1); the four old large in-slab events (DECISIONS_NOTE, open points); the interface band ± 10 / 20 km (the classes of `classify.py` run with those settings, if quick; otherwise say so).

## Report

`explore/B9/REPORT.md`:
- one-page summary: the 10–15 main findings with their figures;
- per part: what was tried, what changed and by how much, surprises, and **options for B10** (not decisions);
- the candidate completeness tables per class in one table;
- assumptions; failures and skips; run times.

Figures (`explore/B9/figs/`, shared palette, Ubuntu font, comfortable margins): cumulative counts against time per magnitude band and class; the completeness tables drawn over the magnitude–time plot of each class (historical events included); frequency–magnitude per class with the fits; b against floor; large-event check; Mc maps; one tornado per class of what moves N(≥ 7) most. `figures_index.md` with one line per figure.

## End of session

WORKLOG entry as CLAUDE.md: what ran, where the outputs are, step 0 findings, commands to rerun, proposed DECISIONS / LEARNINGS lines (as proposals), suggested `git add` and commit message (no Claude signature). No PLAN ticks: B9 stays open until Pablo has chosen in B10.
