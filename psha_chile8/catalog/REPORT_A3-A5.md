# Catalogue report: matching, locations and magnitudes (A3, A4, A5)

State of 13 Nov 2026 (A4 and A5 rerun after the findings of the classification, `explore/X4/HANDOFF_A3-A5.md`). Written to be read in the overall project conversation: what exists, how good it is, what Pablo has to decide, what comes next. Detail is in the files named at the end.

## 1. Where we are

| step | state | output |
|---|---|---|
| A2 sources | done, frozen 10 Nov (GCCEL 11 Nov) | `catalog/sources/` |
| A3 one ID per earthquake | done, rerun 11 Nov with the single-source duplicate step | `merged/events_`, `links_2026-11-11.csv` |
| A4 location, depth, mechanism | rerun 13 Nov with four changes (point 3 below) | `merged/locations_`, `catalog_2026-11-13.csv` |
| A5 one Mw per earthquake | fourth run, 13 Nov: same rule, depths of A4, CSN cross-check | `merged/mw_`, `relations_2026-11-13.csv` |
| A6 large events by hand | not started | – |
| A7 tectonic classification | not started | – |
| completeness, fits | not started | – |

The working catalogue is `catalog/merged/catalog_2026-11-13.csv`, sorted by time. The files of 11 Nov are kept for comparison.

## 2. The catalogue in numbers

- 204 956 events of any size; 200 427 in the model domain (17–58° S, 65–78.5° W).
- 116 773 with an Mw. **14 234 with Mw ≥ 4.5 in the domain**, 1513 to Nov 2026 (14 157 in the run of 12 Nov; 5 470 with Mw ≥ 5.0 against 5 463, 1 941 with Mw ≥ 5.5 against 1 949).
- Mw of those: 4 226 measured, 9 176 converted (mb 5 030, ML 2 805, surface-wave 1 341), 832 from ISC-GEM, Centennial, Cabello (before 1904) and Ruiz and Madariaga (2018).
- Epicentre: ISC 5 326, Potin 3 388, ISC-EHB 4 176, CSN 772, others 572.
- Depth: measured for 12 374, unknown for 1 860 (13 %). Mechanism for 2 671.

## 3. Method in short

1. **Matching (A3).** Identity links first; then time and distance windows measured per pair of sources (99th percentile of known pairs); one-to-one assignment; non-earthquakes dropped; single-source duplicates of ISC events removed. Withheld identity links are recovered with ≤ 0.04 % wrong and 0.07–0.76 % missed.
2. **Location (A4).** Local catalogue (Potin to July 2020, CSN after) first only inside its network (18–46° S, not east of the arc, from 1982); elsewhere GCCEL, ISC-EHB L1 / L2, ISC, ComCat. Before 1964 Centennial (EHB part), ISC-GEM, ISC; before 1904 Cabello. A local record more than 50 km from every teleseismic record of the event is not used (85 events at Mw ≥ 4.5). Against 775 GCCEL events left out of the rule: 8.8 km in epicentre, 7.0 km in depth (9.4 and 7.5 km before the rerun).
3. **Depth (A4).** First measured depth in the same order; offshore, GCCEL and ISC-EHB L1 / L2 before the local catalogue (Potin is a median 11 km shallower than GCCEL there, ISC-EHB L1 1 km). Not used: fixed depths, ISC-EHB L3, depths on a default value of the agency, and before 1964 depths on a multiple of 5 km (nominal values). Exceptions: a fixed ISC-EHB L1 depth is held at its depth-phase value and counts as measured; a fixed L2 depth is the GCMT depth and is used only when nothing else is measured (3 events). Fixed ISC depths stay out: they are the regional default of the ISC locator (181 km 908 times). No filling from Slab2. Depth σ at least 5 km (10 km offshore, 15 km for the GCMT depth, 20 km before 1964).
4. **Reference Mw (A5).** GCMT from 5.4; below, the regional and W-phase family (NEIC Mww, CSN, NEIC Mwr, GFZ) after constant offsets ≤ 0.08. A GCMT value below 5.4 that stands alone is lowered by 0.162 × (5.4 − GCMT) (0.159 in the run of 12 Nov). A CSN regional Mw more than 0.3 from the median of two or more other moment magnitudes of the event is left out (26 values).
5. **Conversion (A5).** Only ISC and NEIC mb and surface-wave magnitudes, CSN ML and INPRES ML. Native magnitude regressed on Mw and inverted, slope corrected for the reference error; form chosen by cross-validation.
6. **One Mw per event (A5).** Ruiz and Madariaga; reference Mw; before 1976 ISC-GEM then Centennial; then one converted scale: surface-wave (events not deeper than 60 km, no magnitude limit; Di Giacomo et al. 2015), CSN ML, ISC mb, NEIC mb, INPRES ML.

## 4. How good it is

| test | result | pass |
|---|---|---|
| 1 b-value change over fit floors 4.7–5.8 | 0.08 (1976 on), 0.15 (2011 on), declustered | yes |
| 2 rate of Mw ≥ 5.5 per period | 15.9 / 15.5 / 19.3 / 17.0 per yr, departure 13.8 % | yes |
| 3 large events predicted from Mw 5.0–6.5 | Mw ≥ 7: 37.3 of 44; 31 of 32 cases in the band | 31 of 32 |
| 4 converted against held-out regional Mw | 16 of 20 bins within 0.1; mb +0.10 to +0.16 at 5.0–5.5 | partly |
| 5 histogram smoothness | largest departure 2.1 σ | yes |

Against the two published catalogues (same tests): b change 0.26 / 0.47 for Cabello et al. (2025) and 0.11 / 0.36 for Candia and Macedo (2026); rate departure 34 % and 17 %; Mw ≥ 7 predicted 26 of 35 and 25 of 46.

## 5. Weak points

1. **mb before 1990.** In 1976–1989, 60 % of the values at Mw ≥ 5.0 come from mb, and mb reads about 0.1 high at 5.0–5.5. Cause not found. To be carried as a sensitivity case in the fits (floor 5.5 before 1990, or those values lowered by 0.1).
2. **About 40 % fewer events at M ≥ 5 than both published catalogues** (44–57 against 65–100 per year). It holds from 2011, when 82 % of our values are measured, so we think ours is right; the paper needs the argument made per period.
3. **Unknown depths.** 1 860 events: 395 before 1964 (316 at Mw ≥ 6; only 78 events before 1964 keep a depth), 386 in 1964–1975, 1 079 from 1976 (721 below Mw 5). Nearly all outside the network. To be handled in A7: the class of Ruiz and Madariaga for the events they name, mechanism (52 events), the depth another agency gives in the ISC Bulletin (about 250 with a USGS-family depth off the default values, 158 of them deeper than 60 km), Slab2 position, split weights for what stays ambiguous. The ISC depth-phase depths would need a new download and are expected to add little.
4. **The tests chose the rule.** Sixteen combinations were tried and tests 1, 2, 3 and 5 helped to choose, so they describe the catalogue and do not validate it independently. The withheld-Mw check and test 4 were not used for the choice.
5. **GCMT correction.** A smooth line, chosen to avoid a step at 5.4; off from the measured bin means by up to 0.04 on about 1 000 events.
6. **The rerun of 13 Nov moved 613 magnitudes** at Mw ≥ 4.5 in the domain (84 by 0.2 or more). Most come from NEIC mb: with the A4 depths the cross-validation now splits its relation by depth (score 0.0410 against 0.0412 unsplit), which moves it by about ± 0.05 at 4.5. The choice is marginal; the tests do not change.
7. **CSN regional Mw against NEIC regional Mw.** 131 pairs differ by more than 0.3 with only these two values. Both have an error near 0.11, and NEIC Mwr is 0.15 lower on average, so the data do not say which is wrong; the order decides (CSN first) and the pairs are listed in `merged/review/mw_reference_dropped_2026-11-13.csv` (`dropped` false).

## 6. For Pablo to decide or do

- Done on 12 Nov by Claude at Pablo's request: the lines for A4, A5 and X4 are in `DECISIONS.md` and `LEARNINGS.md`; A3, A4, A5 ticked in `PLAN.md`, marker on A6. To check: the reference line of DECISIONS still says NEIC Mwr + 0.10 and GFZ + 0.03, the run applies + 0.08 and + 0.04.
- Run the three commits (lines in the WORKLOG; git is blocked for Claude Code).
- Hand review of two large events converted from ML alone: 2010-02-27 08:25 (→ 7.0) and 2011-01-07 04:55 (337 km deep, ML 6.8 → 6.6 with mb 5.1); list in `merged/review/mw_large_proxy_2026-11-13.csv`. Part of A6.
- S. Ruiz: Centennial or ISC-GEM first for magnitude before 1964 (`catalog/PREFERENCES.md`, question 1).
- Review lists not yet looked at: `merged/review/` (possible splits 7, distant events, moment mismatches 19, events without Mw but native M ≥ 4.5: 846, and new: `mech_mw_differs_2026-11-13.csv`, 13 events whose mechanism Mw is 0.4 or more from the catalogue Mw; six of 2010 probably carry the tensor of another event).
- To propose for DECISIONS: the four A4 changes and the CSN cross-check (lines in the WORKLOG entry of 13 Nov).
- References to add to `REFERENCES.md`: list in `paper/CATALOG_SECTION_draft.md`, part E.

## 7. Next steps, in order

1. A6: the large events one by one (includes the two ML-only events and the moment mismatches).
2. A7: classification, with the rule for unknown depths of point 5.3.
3. Completeness per class, then fits, with the mb sensitivity case of point 5.1 and the rate comparison of point 5.2.
4. A8: freeze the catalogue with its decisions note.

## 8. Where the detail is

| topic | file |
|---|---|
| matching method and checks | `catalog/merged/METHOD.md` |
| magnitude method, relations, tests, the three runs | `catalog/MAGNITUDES.md` |
| surface-wave rule and GCMT correction tests | `explore/X4/` (tables, `figs/x4_rule_choice.png`) |
| location rule and settings | `catalog/locate.py` (top of file), WORKLOG entry "A4" |
| location benchmark | `explore/X3/REPORT.md` |
| sources | `catalog/SOURCES.md` |
| paper text and figure list | `paper/CATALOG_SECTION_draft.md` |
| figures | `catalog/figs/match/`, `locate/`, `magnitude/` |
| every run | `DATA.md`; session notes in `WORKLOG.md` |

Code to rerun everything (from `catalog/`, psha_renta python): `match.py`, `magnitude.py`, `magnitude_check.py`, `locate.py`, `locate_check.py`. Tests: `pytest` from `psha_chile8/`.
