# Catalogue report: matching, locations and magnitudes (A3, A4, A5)

State of 14 Nov 2026, run `2026-11-14b` (final run of locations and magnitudes; the classified catalogue is run `2026-11-14c`, described in `catalog/CLASSIFICATION.md`). Rules and their support are in `catalog/RULES_LOCATION_MAGNITUDE.md`. Written to be read in the overall project conversation: what exists, how good it is, what is still open. Detail is in the files named at the end.

## 1. Where we are

| step | state | output |
|---|---|---|
| A2 sources | done, frozen 10 Nov (GCCEL 11 Nov) | `catalog/sources/` |
| A3 one ID per earthquake | done, run of 11 Nov | `merged/events_`, `links_2026-11-11.csv` |
| A4 location, depth, mechanism | final run, 14 Nov | `merged/locations_`, `catalog_2026-11-14b.csv` |
| A5 one Mw per earthquake | final run, 14 Nov, on the depths of the same run | `merged/mw_`, `relations_2026-11-14b.csv` |
| A6 large events by hand | done; 74 accepted corrections, applied as the last step of the run | `catalog/overrides_A6.csv`, `catalog/A6/REPORT.md` |
| A7 tectonic classification | done, run `2026-11-14c` | `merged/classes_`, `catalog_2026-11-14c.csv`, `catalog/CLASSIFICATION.md` |
| A8 frozen catalogue | done, 14 Nov | `catalog/frozen/2026-11-14/` with `SHA256SUMS` |
| completeness, fits | not started | – |

The catalogue of locations and magnitudes is `catalog/merged/catalog_2026-11-14b.csv`, sorted by time; `catalog_2026-11-14c.csv` is the same with the classes joined. The files of the earlier runs are kept for comparison. Against run `2026-11-13e` this run changes one magnitude (1934-03-01 21:45, Mw 7.3 → 7.6) and no epicentre or depth.

## 2. The catalogue in numbers

- 204 956 events of any size; 200 427 in the model domain (17–58° S, 65–78.5° W).
- 116 780 with an Mw. **14 279 with Mw ≥ 4.5 in the domain**, 1513 to Nov 2026; 5 463 with Mw ≥ 5.0, 1 943 with Mw ≥ 5.5, 163 with Mw ≥ 7.
- Mw of those: 4 296 measured, 9 177 converted (mb 5 042, ML 2 782, surface-wave 1 353), 542 from ISC-GEM, 126 from the Centennial catalogue, 104 from Cabello (before 1904), 27 from Ruiz and Madariaga (2018), 7 corrected in the large-event review.
- Epicentre: ISC 5 339, Potin 3 412, ISC-EHB 4 183, CSN 774, others 571.
- Depth: measured for 12 391, not measured for 1 888 (13 %). Mechanism for 2 671 (GCMT 2 487, ComCat 184).

## 3. Method in short

1. **Matching (A3).** Identity links first; then time and distance windows measured per pair of sources (99th percentile of known pairs); one-to-one assignment; non-earthquakes dropped; single-source duplicates of ISC events removed. Withheld identity links are recovered with ≤ 0.04 % wrong and 0.07–0.76 % missed.
2. **Location (A4).** Local catalogue (Potin to July 2020, CSN after) first only inside its network (18–46° S, not east of the arc, from 1982); elsewhere GCCEL, ISC-EHB L1 / L2, ISC, ComCat. Before 1964 Centennial (EHB part), ISC-GEM, ISC; before 1904 Cabello. A local record more than 50 km from every teleseismic or GCCEL record of the event is not used (94 events at Mw ≥ 4.5 in the domain). Against 775 GCCEL events left out of the rule: 8.8 km in epicentre, 7.0 km in depth.
3. **Depth (A4).** First measured depth in the same order; offshore, GCCEL and ISC-EHB L1 / L2 before the local catalogue (Potin is a median 11 km shallower than GCCEL there, ISC-EHB L1 1 km). Not used: fixed depths, ISC-EHB L3 and depths on a default value of the agency. One exception: a fixed ISC-EHB L1 depth is held at its depth-phase value and counts as measured. Fixed ISC depths stay out: they are the regional default of the ISC locator (181 km 908 times). Before 1964 a depth counts only where its catalogue marks it as constrained: ISC-GEM depth quality A or B (Di Giacomo et al. 2018) or a free-depth solution of the Centennial catalogue; 83 events keep one. No filling from Slab2. Depth σ at least 5 km (10 km offshore, 20 km before 1964).
4. **Mechanism (A4).** GCMT first, then its copies in ComCat, a ComCat W-phase tensor, another ComCat tensor, nodal planes.
5. **Reference Mw (A5).** GCMT from 5.4; below, the regional and W-phase family (NEIC Mww, CSN, NEIC Mwr, GFZ) after constant offsets ≤ 0.08. A GCMT value below 5.4 that stands alone is lowered by 0.162 × (5.4 − GCMT). The CSN moment magnitude of the ISC Bulletin comes last: it is used only when the event has no other measured Mw (106 events), and it is not used to fit the relations or the offsets. A CSN regional Mw more than 0.3 from the median of two or more other moment magnitudes of the event is left out (26 values).
6. **Conversion (A5).** Only ISC and NEIC mb and surface-wave magnitudes, CSN ML and INPRES ML. Native magnitude regressed on Mw and inverted, slope corrected for the reference error; form chosen by cross-validation. Depth splits use the final depths of this run.
7. **One Mw per event (A5).** From 1976: measured Mw; Ruiz and Madariaga; then one converted scale: surface-wave (events not deeper than 60 km, no magnitude limit; Di Giacomo et al. 2015), CSN ML, ISC mb, NEIC mb, INPRES ML. Before 1976: Ruiz and Madariaga; measured Mw; a Centennial Mw; an ISC-GEM direct Mw; a Centennial Ms or mB converted (mB by Abe 1982); an ISC-GEM proxy Mw; Cabello before 1904. A moment-based value goes before a converted one, and the Centennial before ISC-GEM only within the same level.
8. **Large events (A6).** A value is corrected only from a source that was read. The 74 accepted rows of `overrides_A6.csv` are applied as the last step: 7 Mw, 1 longitude (1878-01-23), 1 depth (1934-03-01, 120 km) and 65 class hints (63 from the literature, 2 stated by Pablo on 14 Nov: 2001-07-07 and 2015-09-16 23:18, interface). The class hints are used by the classification.

## 4. How good it is

| test | result | pass |
|---|---|---|
| 1 b-value change over fit floors 4.7–5.8 | 0.08 (1976 on), 0.14 (2011 on), declustered | yes |
| 2 rate of Mw ≥ 5.5 per period | 15.9 / 15.5 / 19.4 / 17.1 per yr, departure 14.1 % | yes |
| 3 large events predicted from Mw 5.0–6.5 | Mw ≥ 7: 36.9 of 43; 30 of 32 cases in the band | 30 of 32 |
| 4 converted against held-out regional Mw | 16 of 20 bins within 0.1; mb +0.10 to +0.17 at 5.0–5.5 | partly |
| 5 histogram smoothness | largest departure 2.2 σ | yes |

The two misses of test 3: Mw 6.5–7 predicted from floor 5.0, all events (87.8 against a band from 88.6; 108 observed), and Mw ≥ 7 for shallow crustal events, declustered, from floor 5.3 (0.6 against a band from 1.1). The tests use the events from 1976 and the values of the rule, before the corrections of the large-event review.

Against the two published catalogues (same tests): b change 0.26 / 0.47 for Cabello et al. (2025) and 0.11 / 0.36 for Candia and Macedo (2026); rate departure 34 % and 17 %; Mw ≥ 7 predicted 26 of 35 and 25 of 46.

## 5. Weak points

1. **mb before 1990.** In 1976–1989, 61 % of the values at Mw ≥ 5.0 come from mb, and mb reads 0.10–0.17 high at 5.0–5.5. Cause not found. To be carried as a sensitivity case in the fits (floor 5.5 before 1990, or those values lowered by 0.1).
2. **Fewer events at M ≥ 5 than both published catalogues** (44–57 against 64–102 per year, declustered): 40, 45, 44 and 33 % fewer than Cabello et al. (2025) in 1976–1989, 1990–1999, 2000–2010 and from 2011, and 42, 36, 34 and 19 % fewer than Candia and Macedo (2026). The difference is smallest from 2011 (33 and 19 %), when 82 % of our values are measured, so we think ours is right; the paper needs the argument made per period.
3. **Depths not measured.** 1 888 events: 389 before 1964 (305 at Mw ≥ 6; 84 events before 1964 have a depth, one of them from the large-event review), 400 in 1964–1975, 1 099 from 1976 (741 below Mw 5). Nearly all outside the network. How they enter the classification is in section 6.
4. **The tests chose the rule.** Sixteen combinations were tried on the run of 12 Nov and tests 1, 2, 3 and 5 helped to choose, so they describe the catalogue and do not validate it independently. The withheld-Mw check and test 4 were not used for the choice.
5. **GCMT correction.** A smooth line, chosen to avoid a step at 5.4; off from the measured bin means by up to 0.04 on 1 017 events (865 in the domain).
6. **CSN regional Mw against a single other moment magnitude.** 131 CSN regional values differ by more than 0.3 from the only other moment magnitude of their event (mostly a NEIC Mwr, as found on 13 Nov). The data do not say which is wrong; the order decides (CSN first) and the pairs are listed in `merged/review/mw_reference_dropped_2026-11-14b.csv` (`dropped` false).
7. **Large events left on converted Centennial values** above the ISC-GEM proxies, no seismic moment found: 1918-05-20, 1925-05-15, 1948-05-11, 1971-06-17. A sensitivity case for the in-slab Mmax.

## 6. Events without a measured depth

Numbers are events of Mw ≥ 4.5 in the domain, run `2026-11-14b`.

**How many.** 1 888 events have no measured depth.

| | Mw 4.5–5 | 5–5.5 | 5.5–6 | 6–7 | ≥ 7 | all |
|---|---|---|---|---|---|---|
| before 1904 | 0 | 0 | 4 | 59 | 52 | 115 |
| 1904–1963 | 0 | 5 | 75 | 156 | 38 | 274 |
| 1964–1975 | 326 | 69 | 5 | 0 | 0 | 400 |
| from 1976 | 741 | 299 | 49 | 9 | 1 | 1 099 |

- **The large events were a hand job (A6), not a rule.** 315 events of Mw ≥ 6 have no measured depth, 305 of them before 1964. 22 events without a measured depth carry a class from the literature; 17 of them get a depth assigned from that class and Slab2, flagged (`CLASSIFICATION.md`, rule R8).
- **A rule is needed for the small modern events:** 1 489 events from 1964 on below Mw 6, of which 1 067 are below Mw 5. With a fit floor of Mw 5.0 only 422 remain.

**Why they have no depth.** Every event from 1964 on has at least one depth value in some source, and each was rejected as not measured. The rejected values are ComCat 33 km (516 records), 10 km (238), 35 km (231); ISC 35 km (358), 10 km (222) and its regional grid values; ISC-EHB L3 (371 records, mostly 10–35 km); GCMT 10 km (37). The epicentre comes from the ISC for 1 466 of the 1 489 small modern events; only 10 are inside the Chilean network; 713 are offshore. By latitude they lie at 30–38° S (557), 16–24° S (325), 24–30° S (254), 38–46° S (239) and south of 46° S (114).

**What a default depth does and does not say.** It is the agency's prior for the region, not a measurement. A shallow default (10, 33, 35 km) says only "not obviously deep". A deep default (70 km or more) is assigned where the regional seismicity is deep, so it is weak evidence for an in-slab event.

**How they are classified** (run `2026-11-14c`, `CLASSIFICATION.md`, rule R6; 1 871 events after the 17 assigned depths). Positions decide where they can, and split weights carry the rest:

| group | events | class |
|---|---|---|
| west of the trench | 194 | outer rise |
| Antarctic interface, by position | 97 | interface |
| no slab at the epicentre | 58 | crustal |
| slab top deeper than 50 km and every rejected depth ≥ 70 km | 225 | in-slab |
| class from the literature, no depth assigned | 5 | as stated |
| the rest | 1 292 | shared by the weights of the classified events of the same position and magnitude bin |

A mechanism exists for 54 of the events without a measured depth.

**Measured depths that could still be defaults.** After the screening, the measured depths show no spike: of 12 391, 7 sit on exactly 10 km, 25 on 33 km and 36 on 35 km, spread over several sources. The share on a multiple of 5 km is high only where the catalogue itself rounds (GCCEL 48 of 191, CSN web 161 of 734, ISC-GEM 44 of 94).

**Depths that are measured but doubtful.** 184 Potin depths lie above 5 km where the slab top is deeper than 15 km, and 57 lie more than 40 km under a slab top not deeper than 50 km. Comparison with calibrated locations shows Potin 11–21 km too shallow for such depths, but about a quarter are truly shallow (comparison of 13 Nov, not rechecked for run `2026-11-14b`), so the catalogue keeps them. The classification treats them as uncertain through the depth σ (10 km offshore) and the split weights, without changing the depth.

## 7. Open points

- Settled since the report of 13 Nov: the order of Centennial and ISC-GEM before 1976 (S. Ruiz, 13 Nov); the GCMT line below 5.4 is kept (Pablo, 13 Nov); two large events were corrected in A6: 2010-02-27 08:25, converted from ML alone (6.97 → 6.3), and 2011-01-07 04:55, for which the rule gives the CSN moment magnitude of the ISC Bulletin (5.6 → 5.7); events without depth enter the classification as in section 6.
- The 50 km check of local records drops 94 events of Mw ≥ 4.5 in the domain (97 of Mw ≥ 4.5 anywhere; 13 of Mw ≥ 5.5 in the domain, 14 anywhere; 423 of any size). Recounted on 15 Nov with `locate.py` and the frozen defaults; the 85 of earlier notes is not reproduced by any saved run.
- Review lists of this run in `merged/review/`: events without Mw but native M ≥ 4.5 (844, 243 of M ≥ 5), moment mismatches (9), mechanism Mw 0.4 or more from the catalogue Mw (3), Mw ≥ 7 with ISC-GEM and Centennial apart (36), converted Mw ≥ 6.5 from 1976 on (15).
- The fits are to be run with and without the events without a measured depth, and with the mb sensitivity case of point 5.1.
- Not re-read before citing: Kanamori and Rivera (2017), Astiz (1987) and the web tables used for 1878 were opened by a sub-agent only.
- References to add to `REFERENCES.md`: list in `paper/CATALOG_SECTION_draft.md`, part E, and section 5 of `RULES_LOCATION_MAGNITUDE.md`.

## 8. Next steps, in order

1. Completeness per class.
2. Fits, with the mb sensitivity case of point 5.1 and the rate comparison of point 5.2.

## 9. Where the detail is

| topic | file |
|---|---|
| matching method and checks | `catalog/merged/METHOD.md` |
| magnitude method, relations, tests | `catalog/MAGNITUDES.md` |
| surface-wave rule and GCMT correction tests | `explore/X4/` (tables, `figs/x4_rule_choice.png`) |
| location rule and settings | `catalog/locate.py` (top of file) |
| every rule with its evidence, literature and support | `catalog/RULES_LOCATION_MAGNITUDE.md` |
| large-event review | `catalog/A6/REPORT.md`, `catalog/overrides_A6.csv` |
| classification | `catalog/CLASSIFICATION.md` |
| frozen catalogue and decisions note | `catalog/frozen/2026-11-14/` |
| location benchmark | `explore/X3/REPORT.md` |
| sources | `catalog/SOURCES.md` |
| paper text and figure list | `paper/CATALOG_SECTION_draft.md` |
| figures | `catalog/figs/match/`, `locate/`, `magnitude/` |
| every run | `DATA.md`; session notes in `WORKLOG.md` |

Code to rerun everything (from `catalog/`, psha_renta python): `match.py`, `locate.py`, `magnitude.py`, `locate.py` again (the magnitudes need the depths, the catalogue file needs the magnitudes), `magnitude_check.py`, `locate_check.py`, `classify.py`. Tests: `pytest` from `psha_chile8/`.
