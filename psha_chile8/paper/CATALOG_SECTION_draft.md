# Catalogue section of the paper: outline and first draft

Draft of 12 Nov 2026, brought to the runs of 13 Nov: A2 (sources), A3 (matching), the second A4 rule (locations) and the fourth A5 run (magnitudes).
Every number is taken from the files named in part D. Nothing here is decided for the paper; it shows how the section would read.

How to use this file in a Claude conversation: give it this file and, for detail, `catalog/merged/METHOD.md`, `catalog/MAGNITUDES.md`, `catalog/SOURCES.md` and `REFERENCES.md`. Part A is the outline, part B the text, part C the figures and tables, part D where each number comes from, part E what is still open.

Not yet done and therefore only placeholders in the text: tectonic classification (A7), completeness, declustering for the model. The 2.6 and 2.7 texts will change when those exist.

---

## A. Method at a glance

| step | what it does | rule in one line | main references | how it was checked |
|---|---|---|---|---|
| 1 Sources | 13 catalogues downloaded and frozen | every origin and every magnitude kept as the source writes it; one download date | Table 1 | profile of each source |
| 2 Matching | one identifier per earthquake | identity links first; then time and distance windows measured per pair of sources; one-to-one assignment | Bondár and Storchak (2011); Kuhn (1955); Weatherill et al. (2016) | identity links withheld and recovered; time-shifted catalogues |
| 3 Location | one epicentre and origin time per event | local relocated catalogue inside its network and within 50 km of the teleseismic records, calibrated and teleseismic relocations elsewhere | Potin et al. (2024); Bergman et al. (2023); Weston et al. (2018) | 775 calibrated locations left out and compared |
| 4 Depth | one depth per event, or none | first measured depth in the same order (offshore: calibrated and ISC-EHB first); default depths, fixed depths not held at a depth-phase value and nominal depths before 1964 not used | Weston et al. (2018); Engdahl et al. (2020); Bondár and Storchak (2011) | share of unknown depths by period and latitude |
| 5 Reference Mw | one moment-magnitude scale | GCMT from 5.4; regional and W-phase Mw below, after constant offsets; outlying CSN regional values left out | Lolli et al. (2023); Gasperini et al. (2012) | offsets between members on shared events |
| 6 Conversion | native magnitudes to Mw | native magnitude regressed on Mw and inverted, slope corrected for the reference error | Lolli et al. (2014, 2023); Hausman and Wise (1977) | synthetic test; forward against inverse fits |
| 7 One Mw per event | measured before converted | surface-wave scales first for shallow events, then ML, then mb; one scale per event | Di Giacomo et al. (2015); Weatherill et al. (2016) | measured Mw withheld and predicted |
| 8 Validation | is the scale steady in size and time | b against the fit floor, rates per period, large events predicted from small ones, held-out regional Mw, histogram | Habermann (1991); Lolli et al. (2014) | the same tests on the two published Chilean catalogues |

---

## B. Draft text

### 2. Earthquake catalogue

We built the catalogue from the original global and Chilean catalogues, without using a previous compilation as a starting point. Each earthquake receives one identifier, one location, one depth where a measured depth exists, and one moment magnitude. Every choice is a rule applied to all events, and each rule is tested on events for which the answer is known.

#### 2.1 Sources

Thirteen sources were downloaded for latitudes 58.0° S to 15.5° S and longitudes 80.0° W to 60.0° W and frozen on 10 November 2026 (Table 1). All origins and all magnitudes of each source were kept with the agency and magnitude type as written. The relocated catalogue of Potin et al. (2024) covers the Chilean network from 1982 to July 2020; the catalogue of the Centro Sismológico Nacional (CSN) continues it to the download date. The Bulletin of the International Seismological Centre (ISC) provides the hypocentres and magnitudes of all contributing agencies from 1904. ISC-EHB, ISC-GEM, the Centennial catalogue and the calibrated locations of Bergman et al. (2023) provide relocated hypocentres. Moment magnitudes come from the Global CMT catalogue, the U.S. Geological Survey (USGS), the CSN and GFZ. Before 1904 we use the historical rows of Cabello et al. (2025), and for the large historical and recent earthquakes the magnitudes of Ruiz and Madariaga (2018).

#### 2.2 One identifier per earthquake

Records of different sources were first linked by the identifiers the sources share: the ISC event and origin identifiers carried by ISC-EHB and ISC-GEM, and the solution of each agency found inside an ISC event within 1.5 s and 10 km. The grouping of reported hypocentres into events inside the ISC Bulletin is the reviewed association of the ISC (Bondár and Storchak 2011).

The remaining records were matched by origin time and epicentral distance. Instead of one fixed window (for example 60 s and 100 km in Weatherill et al. 2016), we measured the window for each pair of sources as the 99th percentile of the offsets of pairs already known to be the same event, with a floor of 10 s and 50 km and a cap of 120 s and 450 km. Windows are widened by 1.5, 2 and 3 at magnitudes 6, 7 and 8. Where several candidates compete, the assignment that minimizes the total normalized offset is taken (Kuhn 1955). Magnitude is never a matching criterion. Events flagged as non-earthquakes by any source were removed. Uncertain links were written to review lists and not decided automatically.

Two checks bound the errors. When the identity links of a source are withheld and its records matched again by time and distance only, at most 0.04 % are attached to the wrong event and 0.07–0.76 % are missed. When a source is shifted by 10 or 20 minutes, so that no match can be real, 0.14 % of the records of the largest catalogue still find a partner. The matched set has 204 956 events of any size.

#### 2.3 Location and depth

The best location source differs between regions. Against the 775 calibrated locations of Bergman et al. (2023), the relocated local catalogue has epicentres within 3–6 km inside the network between 18° S and 36° S, but it is poorer than the teleseismic relocations south of the network and east of the volcanic arc (Supplement). We therefore use the local catalogue first only inside its own network (18–46° S, not east of the arc, from 1982), and only where its record lies within 50 km of the closest teleseismic or calibrated record of the same event; 85 events of Mw ≥ 4.5 fail this condition. There the order is Potin et al. or CSN, calibrated locations, ISC-EHB, ISC, USGS. Outside the network and in 1964–1981 the calibrated and teleseismic sources come first. Before 1964 we use the Centennial catalogue where it is EHB-relocated, then ISC-GEM, then the ISC; before 1904 the epicentres of Cabello et al. (2025). Epicentre and origin time always come from the same record.

Depth is taken from the first source in the same order that has a measured depth. Offshore, more than 20 km from the coast, the calibrated locations and ISC-EHB come before the local catalogue: there the local depths are a median 11 km shallower than the calibrated ones, against 1 km for the best ISC-EHB class. A depth is not measured when the source flags it as fixed, when it is an ISC-EHB solution of the lowest depth class, or when it sits on a default value of its agency (for example 10, 33 or 35 km). Default values were identified from the data, per agency and period, as depths that hold an anomalous share of the events. Fixed depths of the ISC are regional default values of its locator (Bondár and Storchak 2011) and are not used. Two kinds of fixed depth are kept, following the ISC-EHB definitions (Engdahl et al. 2020 [to check]): a fixed depth of the best class is held at a value constrained by depth phases and counts as measured; a fixed depth of the second class is the Global CMT depth and is used only when no other depth is measured (3 events). Before 1964, depths on a multiple of 5 km are nominal values and are treated as unknown. Events with no measured depth in any source keep an unknown depth; we do not fill them from the slab geometry at this stage. The depth uncertainty is at least 5 km, 10 km offshore and 20 km before 1964. With the calibrated locations left out of the rule, the catalogue differs from them by 8.8 km in epicentre and 7.0 km in depth on average.

Focal mechanisms are taken from USGS W-phase solutions and the Global CMT catalogue.

#### 2.4 Moment magnitude

**Reference scale.** Global moment-tensor catalogues are incomplete below about Mw 5.5 and the Global CMT catalogue reads higher than regional moment magnitudes below 5.4 (Gasperini et al. 2012; Lolli et al. 2023). Our reference is the Global CMT value from 5.4 and, below, the family of regional and W-phase moment magnitudes: USGS W-phase and regional Mw, CSN regional and W-phase Mw, and GFZ Mw. Each member was shifted to the USGS W-phase scale by its mean difference on shared events; the shifts are at most 0.08 and do not vary with magnitude (Table 2). A Global CMT value below 5.4 that is the only moment magnitude of its event is lowered by 0.162 × (5.4 − Mw), fitted on 812 events that also have a regional or W-phase value. A regional Mw of the CSN that differs by more than 0.3 from the median of two or more other moment magnitudes of its event is left out (26 values). In total 6 228 events have a reference Mw.

**Conversion relations.** Only the magnitudes of the agencies that observe Chile directly or serve as global references are converted: mb and Ms of the ISC and the USGS National Earthquake Information Center (NEIC), ML of the CSN, and ML of the Argentine network INPRES. Because the reference exists for fewer than half of the events below magnitude 5, regressing Mw on the native magnitude selects the pairs on the dependent variable and is biased at the low end (Hausman and Wise 1977; Lolli et al. 2014). We regress the native magnitude on the reference Mw and invert the relation, with the slope corrected for the error of the reference (0.08 for Global CMT, 0.10 for the other members). For each scale, a straight line and a line with a saturation bend were fitted, with and without a split at 50 km depth (the depth of section 2.3), and the form was chosen by cross-validation in time blocks. Table 3 gives the relations. A synthetic test with a known relation shows that this fit stays within 0.05 of the truth where least-squares and orthogonal fits are off by 0.10–0.26 at native magnitude 4.5 (Supplement).

**One Mw per event.** An event takes, in this order: the value of Ruiz and Madariaga (2018) if they list it; the reference Mw; before 1976 the ISC-GEM Mw, then the Centennial magnitude; before 1904 the historical value of Cabello et al. (2025); otherwise one converted magnitude. The converted scale is the first available of: surface-wave magnitudes (NEIC, ISC), CSN ML, ISC mb, NEIC mb, INPRES ML, ordered by the scatter of their relations. Following the ISC-GEM practice (Di Giacomo et al. 2015), surface-wave magnitudes are used only for events not deeper than 60 km and without any magnitude limit. We tested a magnitude limit and rejected it: on events with a measured Mw that was withheld, a limit at Mw 5 changes the number of events at Mw ≥ 5 by +5 to +10 % or by −7 to −15 %, depending on how it is applied, against −2 % without a limit (Figure S-x; computed on the run of 12 Nov). Events with no usable magnitude are kept without Mw and listed.

#### 2.5 Validation of the magnitude scale

A magnitude scale that is consistent in size and time should give the same b-value whatever the lowest magnitude of the fit, the same rate in every period, and should predict the number of large earthquakes from the small ones. We applied five tests to the declustered catalogue (Gardner and Knopoff 1974) and to the full one:

1. The b-value changes by 0.08 between fit floors of 4.7 and 5.8 for 1976 to today, and by 0.15 for 2011 to today.
2. The rate of Mw ≥ 5.5 is 15.9, 15.5, 19.3 and 17.0 events per year in 1976–1989, 1990–1999, 2000–2010 and 2011 to today; the largest departure from the mean is 13.8 %.
3. The Gutenberg–Richter relation fitted from Mw 5.0 predicts 37.3 earthquakes of Mw ≥ 7 against 44 observed, and 88.4 of Mw 6.5–7 against 107. Of 32 combinations of source type, declustering, fit floor and magnitude range, 31 are inside the 95 % band.
4. Converted magnitudes were compared with regional Mw values held out of the fits. Sixteen of 20 bins agree within 0.1. The exceptions are ISC mb and NEIC mb at 5.0–5.5, which read 0.10–0.16 above the regional Mw.
5. The magnitude histogram of each period has no bin that departs from its neighbours by more than 2.1 standard deviations.

The same tests on the two published Chilean catalogues (Figure 3) give a b-value change of 0.26 and 0.47 for Cabello et al. (2025) and 0.11 and 0.36 for Candia and Macedo (2026), a rate departure of 34 % and 17 %, and 26 of 35 and 25 of 46 earthquakes of Mw ≥ 7 predicted. Both list 65–100 events per year at M ≥ 5.0, against 44–57 here; from 2011, when 81 % of our values at Mw ≥ 5.0 are measured moment magnitudes, the difference remains.

#### 2.6 The catalogue

In the model domain (17–58° S, 65–78.5° W) the catalogue has 14 234 earthquakes of Mw ≥ 4.5 from 1513 to November 2026 (Figures 1 and 2). Of these, 4 226 have a measured moment magnitude, 9 176 a converted one (5 030 from mb, 2 805 from ML, 1 341 from surface-wave magnitudes), and 832 a value from ISC-GEM, the Centennial catalogue, Cabello et al. (2025) or Ruiz and Madariaga (2018). Epicentres come from the ISC (5 326), Potin et al. (3 388), ISC-EHB (4 176), the CSN (772) and other sources (572). A measured depth exists for 12 374 events and a focal mechanism for 2 671.

[Tectonic classification, completeness periods and declustering: to be written after A7 and the completeness step.]

#### 2.7 Limitations

- Depth is unknown for 1 860 events (13 %), almost all outside the Chilean network: 395 before 1964, where only 78 events keep a depth, and 1 079 from 1976, of which two thirds are below Mw 5. Their tectonic class has to come from the mechanism, the slab geometry or the literature [A7].
- Before 1990, 61 % of the magnitudes at Mw ≥ 5.0 are converted from mb, and mb conversions read about 0.1 above the regional Mw at 5.0–5.5 (test 4). We carry this as a sensitivity case in the recurrence fits [to be done].
- The correction of Global CMT below 5.4 is a smooth line chosen to avoid a step at 5.4; it departs from the measured bin means by up to 0.04 on about 1 000 events.
- The rules for the surface-wave scales and for the Global CMT correction were chosen among 16 combinations with the help of tests 1, 2, 3 and 5. These tests are therefore a description of the final catalogue and not an independent validation of it. The withheld-Mw check and test 4 were not used for the choice.
- For 131 events the CSN regional Mw and the USGS regional Mw are the only moment magnitudes and differ by more than 0.3. The two have a similar error (about 0.11) and the USGS value is 0.15 lower on average, so the data do not say which is right; the CSN value is used.
- The split of the NEIC mb relation by depth is a marginal choice of the cross-validation; it moves the converted value by about 0.05 at mb 4.5.
- The rate of Mw ≥ 5.5 in 2000–2010 is higher than in the other periods (19.3 against 15.5–17.0 per year, declustered). The period contains the 2010 Maule sequence [check with the model declustering].

---

## C. Figures and tables

| item | content | status | file |
|---|---|---|---|
| Figure 1 | map of the catalogue (Mw ≥ 4.5) | planned | – |
| Figure 2 | source of Mw and of the location through time | parts exist | `catalog/figs/locate/who_decides.png`, `catalog/figs/magnitude/coverage.png` |
| Figure 3 | tests against Cabello et al. (2025) and Candia and Macedo (2026) | draft | `catalog/figs/magnitude/test7_comparison.png` |
| Table 1 | sources: period, number of events, what is used from each | to build from `catalog/SOURCES.md` | – |
| Table 2 | offsets of the reference Mw members | data ready | `catalog/merged/mw_offsets_2026-11-13.csv` |
| Table 3 | conversion relations: form, pairs, σ, Mw at native 4.5–6.0 | data ready | `catalog/merged/relations_2026-11-13.csv` |
| Supplement | matching windows and checks | data ready | `catalog/merged/windows_`, `check_blind_`, `check_chance_`, `catalog/figs/match/summary.png` |
| Supplement | location benchmark against calibrated events; cross-sections; unknown depths | draft | `catalog/figs/locate/gccel.png`, `sections.png`, `depth_unknown.png` |
| Supplement | relations with data; forward against inverse; offsets | draft | `catalog/figs/magnitude/relations.png`, `forward_inverse.png`, `offsets.png` |
| Supplement | tests 1–6 one figure each; synthetic test | draft | `catalog/figs/magnitude/test1_` … `test6_`, `test9_synthetic.png` |
| Supplement | rule for the surface-wave scales (withheld Mw) | draft | `explore/X4/figs/x4_rule_choice.png` |
| Supplement | sensitivity of the tests to each choice | data ready | `catalog/merged/mw_sensitivity_2026-11-13.csv` |

---

## D. Where each number comes from

| numbers | file |
|---|---|
| sources, download box, counts per source | `catalog/SOURCES.md`, `catalog/sources/MANIFEST.csv` |
| matching rules, windows, check rates, 204 956 events | `catalog/merged/METHOD.md`, `counts_`, `check_blind_`, `check_chance_2026-11-11.csv` |
| location order, default depths, benchmark 8.8 / 7.0 km, offshore depth differences | `catalog/locate.py` (settings), `catalog/merged/loc_gccel_`, `defaults_2026-11-13.csv`; WORKLOG entries A4 and 13 Nov |
| Potin 3–6 km inside the network | `explore/X3/REPORT.md` |
| reference members, offsets, 812 pairs, 6 228 events, 26 and 131 CSN values | `catalog/MAGNITUDES.md` §1–2 and §10, `review/mw_reference_dropped_2026-11-13.csv`, `mw_offsets_2026-11-13.csv` |
| relations | `catalog/MAGNITUDES.md` §3, `relations_2026-11-13.csv` |
| withheld-Mw percentages | `explore/X4/tables/x4_blind.csv` (run of 12 Nov, not redone) |
| tests 1–5 and the comparison | `catalog/MAGNITUDES.md` §6a, `mw_tests_`, `mw_sensitivity_2026-11-13.csv` (`MAGNITUDES.md` §6a holds the values of 12 Nov, §10 those of 13 Nov) |
| synthetic test | `catalog/MAGNITUDES.md` §7, `mw_synthetic_2026-11-13.csv` |
| counts of section 2.6 and 2.7 | `catalog/merged/catalog_2026-11-13.csv`, rows with `in_domain` and `mw` ≥ 4.45 |

---

## E. Open before this text can be final

1. Tectonic classification and completeness are not done; 2.6 is incomplete without them.
2. Sensitivity of the recurrence fits to the mb conversions before 1990 (limitation 2).
3. The explanation of why we have about 40 % fewer events at M ≥ 5 than the two published catalogues is stated in 2.5 in one sentence; it needs its own check per period and probably a supplement figure.
4. Two large events converted from ML alone (2010-02-27 08:25 and 2011-01-07 04:55) need a hand review.
5. S. Ruiz: order of the Centennial catalogue and ISC-GEM for magnitude before 1964 (`catalog/PREFERENCES.md`, question 1).
6. References not yet in `REFERENCES.md` or with details unchecked: Bergman et al. (2023), Candia and Macedo (2026, doi:10.1785/0220250449), Gasperini et al. (2012), Hausman and Wise (1977), Kuhn (1955), Bondár and Storchak (2011), Gardner and Knopoff (1974), Habermann (1991), Engdahl et al. (2020; the definition of the fixed depths was read on the ISC-EHB web page, not in the paper).
9. The withheld-Mw check of the surface-wave rule (2.4) was computed on the run of 12 Nov and not repeated on the run of 13 Nov.
7. The test periods and the declustering in 2.5 are those of `catalog/magnitude_check.py`; check the wording against its settings before submission.
8. Journal length: parts 2.2 to 2.5 are about 900 words. For a hazard paper, 2.2 and 2.3 can shrink to one paragraph each with the detail in the supplement.
