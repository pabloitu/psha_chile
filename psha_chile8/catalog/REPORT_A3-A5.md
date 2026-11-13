# Catalogue report: matching, locations and magnitudes (A3, A4, A5)

State of 13 Nov 2026, run `2026-11-13b` (A4 and A5 rerun after the findings of the classification, `explore/X4/HANDOFF_A3-A5.md`, then simplified; rules and their support in `catalog/RULES_LOCATION_MAGNITUDE.md`). Written to be read in the overall project conversation: what exists, how good it is, what Pablo has to decide, what comes next. Detail is in the files named at the end.

## 1. Where we are

| step | state | output |
|---|---|---|
| A2 sources | done, frozen 10 Nov (GCCEL 11 Nov) | `catalog/sources/` |
| A3 one ID per earthquake | done, rerun 11 Nov with the single-source duplicate step | `merged/events_`, `links_2026-11-11.csv` |
| A4 location, depth, mechanism | rerun 13 Nov, simplified the same day (point 3 below) | `merged/locations_`, `catalog_2026-11-13b.csv` |
| A5 one Mw per earthquake | fourth run, 13 Nov: same rule, depths of A4, CSN cross-check (`2026-11-13b` gives the same magnitudes) | `merged/mw_`, `relations_2026-11-13b.csv` |
| A6 large events by hand | not started | – |
| A7 tectonic classification | not started | – |
| completeness, fits | not started | – |

The working catalogue is `catalog/merged/catalog_2026-11-13b.csv`, sorted by time. The files of 11 Nov and of the first run of 13 Nov are kept for comparison; the two runs of 13 Nov differ in 35 depths and in no magnitude.

## 2. The catalogue in numbers

- 204 956 events of any size; 200 427 in the model domain (17–58° S, 65–78.5° W).
- 116 773 with an Mw. **14 234 with Mw ≥ 4.5 in the domain**, 1513 to Nov 2026 (14 157 in the run of 12 Nov; 5 470 with Mw ≥ 5.0 against 5 463, 1 941 with Mw ≥ 5.5 against 1 949).
- Mw of those: 4 226 measured, 9 176 converted (mb 5 030, ML 2 805, surface-wave 1 341), 832 from ISC-GEM, Centennial, Cabello (before 1904) and Ruiz and Madariaga (2018).
- Epicentre: ISC 5 326, Potin 3 388, ISC-EHB 4 176, CSN 772, others 572.
- Depth: measured for 12 376, unknown for 1 858 (13 %). Mechanism for 2 671.

## 3. Method in short

1. **Matching (A3).** Identity links first; then time and distance windows measured per pair of sources (99th percentile of known pairs); one-to-one assignment; non-earthquakes dropped; single-source duplicates of ISC events removed. Withheld identity links are recovered with ≤ 0.04 % wrong and 0.07–0.76 % missed.
2. **Location (A4).** Local catalogue (Potin to July 2020, CSN after) first only inside its network (18–46° S, not east of the arc, from 1982); elsewhere GCCEL, ISC-EHB L1 / L2, ISC, ComCat. Before 1964 Centennial (EHB part), ISC-GEM, ISC; before 1904 Cabello. A local record more than 50 km from every teleseismic record of the event is not used (85 events at Mw ≥ 4.5). Against 775 GCCEL events left out of the rule: 8.8 km in epicentre, 7.0 km in depth (9.4 and 7.5 km before the rerun).
3. **Depth (A4).** First measured depth in the same order; offshore, GCCEL and ISC-EHB L1 / L2 before the local catalogue (Potin is a median 11 km shallower than GCCEL there, ISC-EHB L1 1 km). Not used: fixed depths, ISC-EHB L3 and depths on a default value of the agency. One exception: a fixed ISC-EHB L1 depth is held at its depth-phase value and counts as measured. Fixed ISC depths stay out: they are the regional default of the ISC locator (181 km 908 times). Before 1964 a depth counts only where its catalogue marks it as constrained: ISC-GEM depth quality A or B (Di Giacomo et al. 2018) or a free-depth solution of the Centennial catalogue; 83 events keep one. No filling from Slab2. Depth σ at least 5 km (10 km offshore, 20 km before 1964).
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
3. **Unknown depths.** 1 858 events: 390 before 1964 (304 at Mw ≥ 6; 83 events before 1964 keep a depth), 386 in 1964–1975, 1 082 from 1976 (723 below Mw 5). Nearly all outside the network. What the classification needs to decide about them is in section 6.
4. **The tests chose the rule.** Sixteen combinations were tried and tests 1, 2, 3 and 5 helped to choose, so they describe the catalogue and do not validate it independently. The withheld-Mw check and test 4 were not used for the choice.
5. **GCMT correction.** A smooth line, chosen to avoid a step at 5.4; off from the measured bin means by up to 0.04 on about 1 000 events.
6. **The rerun of 13 Nov moved 613 magnitudes** at Mw ≥ 4.5 in the domain (84 by 0.2 or more). Most come from NEIC mb: with the A4 depths the cross-validation now splits its relation by depth (score 0.0410 against 0.0412 unsplit), which moves it by about ± 0.05 at 4.5. The choice is marginal; the tests do not change.
7. **CSN regional Mw against NEIC regional Mw.** 131 pairs differ by more than 0.3 with only these two values. Both have an error near 0.11, and NEIC Mwr is 0.15 lower on average, so the data do not say which is wrong; the order decides (CSN first) and the pairs are listed in `merged/review/mw_reference_dropped_2026-11-13.csv` (`dropped` false).

## 6. Events without depth: what the classification has to decide

Numbers are events of Mw ≥ 4.5 in the domain, run `2026-11-13b`; slab top from Slab2 at the epicentre (`explore/X4/tables/x4b_events_m45.csv`).

**How many, and which matter.** 1 858 events have no measured depth.

| | Mw 4.5–5 | 5–5.5 | 5.5–6 | 6–7 | ≥ 7 | all |
|---|---|---|---|---|---|---|
| before 1904 | 0 | 0 | 4 | 59 | 52 | 115 |
| 1904–1963 | 0 | 5 | 77 | 160 | 33 | 275 |
| 1964–1975 | 312 | 69 | 5 | 0 | 0 | 386 |
| from 1976 | 723 | 300 | 48 | 10 | 1 | 1 082 |

- **The large events are a hand job (A6), not a rule.** 315 events of Mw ≥ 6 have no depth, 304 of them before 1964. Ruiz and Madariaga (2018) already give the class of 20. These are corrected one by one from the literature in A6, so the classification rule does not have to solve them.
- **The rule is needed for the small modern events:** 1 457 events from 1964 on below Mw 6, of which 1 035 are below Mw 5. With a fit floor of Mw 5.0 only 422 remain.

**Why they have no depth.** Every one of them has at least one depth value in some source, and each was rejected as not measured. From 1964 the rejected values are ComCat 33 km (501 records), 10 km (232), 35 km (231); ISC 35 km (353), 10 km (219) and its regional grid values; ISC-EHB L3 (370 records, mostly 10–35 km); GCMT 10 km (37). The epicentre comes from the ISC for 1 434 of the 1 457; only 10 are inside the Chilean network; 699 are offshore.

**What a default depth does and does not say.** It is the agency's prior for the region, not a measurement. A shallow default (10, 33, 35 km) says only "not obviously deep". A deep default (70 km or more) is assigned where the regional seismicity is deep, so it is weak evidence for an in-slab event.

**The 1 457 small modern events, by position and by their rejected depths:**

| slab top at the epicentre | all rejected depths ≤ 40 km | all ≥ 70 km | mixed | all |
|---|---|---|---|---|
| shallower than 50 km | 702 | 8 | 48 | 758 |
| 50–100 km | 108 | 87 | 28 | 223 |
| deeper than 100 km | 88 | 95 | 5 | 188 |
| no slab (Patagonia, far backarc) | 136 | 0 | 0 | 136 |
| west of the trench | 152 | 0 | 0 | 152 |

- **West of the trench (152):** outer rise by position; nothing to decide.
- **No slab (136):** crustal by position.
- **Slab top deeper than 50 km and deep defaults (182):** in-slab with little doubt.
- **Slab top deeper than 50 km and shallow defaults (196):** crust of the arc or backarc, or in-slab. The default does not separate them.
- **Slab top shallower than 50 km (758):** interface, shallow in-slab or forearc crust. This is the real ambiguity, and it is the group that matters for the interface rate.

**Other information per event.** A mechanism exists for 54 of the 1 858; the 16 that are thrusts on the interface plane are already classified as interface. By latitude the small modern events lie at 30–38° S (543), 16–24° S (320), 24–30° S (246), 38–46° S (236) and south of 46° S (112).

**Options.**
1. Leave them out of the class fits and keep them in the total rate. Simple, but it lowers every class rate by the same unknown share.
2. Split weights: each event without depth counts partly in each possible class, with the shares of the classified events in the same position bin (slab-top range, latitude band) and magnitude range. This is what DECISIONS of 12 Nov foresees. It keeps the total rate and does not pretend to know the class.
3. Class by position alone (slab top shallower than 50 km = interface). This is the old rule of cat_handler_2; it put 751 such events in the interface class.
4. Option 2, with the deep defaults used as evidence for in-slab (the 182 events above).

I would take option 4: positions decide where they can (outer rise, no slab, deep slab with deep defaults), and split weights for the rest.

**To check before deciding.**
- The share of unknown depths by period: 386 events in 1964–1975 against 1 082 in the fifty years since. If the class fits start in 1976 or later the problem halves.
- Whether the split shares should come from the same period, since the classified events of 1964–1975 are the well-recorded ones.

**Measured depths that could still be defaults.** After the screening, the measured depths show no spike: of 12 376, 7 sit on exactly 10 km, 24 on 33 km and 35 on 35 km, spread over several sources. The share on a multiple of 5 km is high only where the catalogue itself rounds (GCCEL 48 of 190, CSN web 161 of 732, ISC-GEM 44 of 94).

**Depths that are measured but doubtful.** 180 Potin depths lie above 5 km where the slab top is deeper than 15 km, and 56 lie more than 40 km under a shallow slab top (all near the coast). Comparison with calibrated locations shows Potin 11–21 km too shallow for such depths, but about a quarter are truly shallow, so the catalogue keeps them. The classification can treat them as uncertain through the depth σ (10 km near and off the coast) and the soft interface probability (`p_if`), without changing the depth.

## 7. For Pablo to decide or do

- Done on 12 Nov by Claude at Pablo's request: the lines for A4, A5 and X4 are in `DECISIONS.md` and `LEARNINGS.md`; A3, A4, A5 ticked in `PLAN.md`, marker on A6. To check: the reference line of DECISIONS still says NEIC Mwr + 0.10 and GFZ + 0.03, the run applies + 0.08 and + 0.04.
- Run the three commits (lines in the WORKLOG; git is blocked for Claude Code).
- Hand review of two large events converted from ML alone: 2010-02-27 08:25 (→ 7.0) and 2011-01-07 04:55 (337 km deep, ML 6.8 → 6.6 with mb 5.1); list in `merged/review/mw_large_proxy_2026-11-13.csv`. Part of A6.
- S. Ruiz: Centennial or ISC-GEM first for magnitude before 1964 (`catalog/PREFERENCES.md`, question 1).
- Review lists not yet looked at: `merged/review/` (possible splits 7, distant events, moment mismatches 19, events without Mw but native M ≥ 4.5: 846, and new: `mech_mw_differs_2026-11-13.csv`, 13 events whose mechanism Mw is 0.4 or more from the catalogue Mw; six of 2010 probably carry the tensor of another event).
- To propose for DECISIONS: the A4 changes and the CSN cross-check (lines in the WORKLOG entries of 13 Nov; the last entry replaces the depth lines).
- Choose in section 6 how events without depth enter the classification.
- The GCMT correction below 5.4 is our own choice (Lolli et al. 2023 leave such values unchanged); keep or drop (`RULES_LOCATION_MAGNITUDE.md`, M3).
- References to add to `REFERENCES.md`: list in `paper/CATALOG_SECTION_draft.md`, part E.

## 8. Next steps, in order

1. A6: the large events one by one (includes the two ML-only events and the moment mismatches).
2. A7: classification, with the rule for unknown depths of section 6.
3. Completeness per class, then fits, with the mb sensitivity case of point 5.1 and the rate comparison of point 5.2.
4. A8: freeze the catalogue with its decisions note.

## 9. Where the detail is

| topic | file |
|---|---|
| matching method and checks | `catalog/merged/METHOD.md` |
| magnitude method, relations, tests, the three runs | `catalog/MAGNITUDES.md` |
| surface-wave rule and GCMT correction tests | `explore/X4/` (tables, `figs/x4_rule_choice.png`) |
| location rule and settings | `catalog/locate.py` (top of file), WORKLOG entry "A4" |
| every rule with its evidence, literature and support | `catalog/RULES_LOCATION_MAGNITUDE.md` |
| location benchmark | `explore/X3/REPORT.md` |
| sources | `catalog/SOURCES.md` |
| paper text and figure list | `paper/CATALOG_SECTION_draft.md` |
| figures | `catalog/figs/match/`, `locate/`, `magnitude/` |
| every run | `DATA.md`; session notes in `WORKLOG.md` |

Code to rerun everything (from `catalog/`, psha_renta python): `match.py`, `magnitude.py`, `magnitude_check.py`, `locate.py`, `locate_check.py`. Tests: `pytest` from `psha_chile8/`.
