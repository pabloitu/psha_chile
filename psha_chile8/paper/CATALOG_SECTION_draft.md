# Catalogue section of the paper: outline and first draft

Draft of 12 Nov 2026, brought on 14 Nov to the final catalogue: locations and magnitudes of the run `2026-11-14b`, classes of the run `2026-11-14c` (frozen copy in `catalog/frozen/2026-11-14/`); counts rechecked against the frozen run on 15 Nov (B9 step 0). It covers A2 (sources), A3 (matching), A4 (locations), A5 (magnitudes), A6 (review of large events) and A7 (tectonic classes). Rules as applied: the settings and module notes of `catalog/locate.py`, `catalog/magnitude.py` and `catalog/classify.py`, and `catalog/CLASSIFICATION.md`.
Every number is taken from the files named in part D. Nothing here is decided for the paper; it shows how the section would read.

How to use this file in a Claude conversation: give it this file and, for detail, `catalog/merged/METHOD.md`, `catalog/MAGNITUDES.md`, `catalog/CLASSIFICATION.md`, `catalog/SOURCES.md` and `REFERENCES.md` (`MAGNITUDES.md` and `CLASSIFICATION.md` state the final runs `2026-11-14b` and `2026-11-14c`). Part A is the outline, part B the text, part C the figures and tables, part D where each number comes from, part E what is still open.

Not yet done and therefore only placeholders in the text: completeness and declustering for the model. The 2.7 and 2.8 texts will change when those exist. Section 2.6 (tectonic class) is new in this version; the former 2.6 and 2.7 are now 2.7 and 2.8.

---

## A. Method at a glance

| step | what it does | rule in one line | main references | how it was checked |
|---|---|---|---|---|
| 1 Sources | 13 catalogues downloaded and frozen | every origin and every magnitude kept as the source writes it; one download date | Table 1 | profile of each source |
| 2 Matching | one identifier per earthquake | identity links first; then time and distance windows measured per pair of sources; one-to-one assignment | Bondár and Storchak (2011); Kuhn (1955); Weatherill et al. (2016) | identity links withheld and recovered; time-shifted catalogues |
| 3 Location | one epicentre and origin time per event | local relocated catalogue inside its network and within 50 km of the teleseismic records, calibrated and teleseismic relocations elsewhere | Potin et al. (2024); Bergman et al. (2023); Weston et al. (2018) | 775 calibrated locations left out and compared |
| 4 Depth | one depth per event, or none | first measured depth in the same order (offshore: calibrated and ISC-EHB first); default depths, fixed depths not held at a depth-phase value and unconstrained depths before 1964 not used | Weston et al. (2018); Engdahl et al. (2020); Bondár and Storchak (2011); Di Giacomo et al. (2018) | share of unknown depths by period and latitude |
| 5 Reference Mw | one moment-magnitude scale | GCMT from 5.4; regional and W-phase Mw below, after constant offsets; outlying CSN values left out; the CSN moment magnitude of the ISC Bulletin last | Lolli et al. (2023); Gasperini et al. (2012) | offsets between members on shared events |
| 6 Conversion | native magnitudes to Mw | native magnitude regressed on Mw and inverted, slope corrected for the reference error | Lolli et al. (2014, 2023); Hausman and Wise (1977) | synthetic test; forward against inverse fits |
| 7 One Mw per event | measured before converted | from 1976: surface-wave scales first for shallow events, then ML, then mb; one scale per event. Before 1976: a moment-based value before a converted one, the Centennial catalogue before ISC-GEM within each level | Di Giacomo et al. (2015); Abe (1982); Weatherill et al. (2016) | measured Mw withheld and predicted |
| 8 Validation | is the scale steady in size and time | b against the fit floor, rates per period, large events predicted from small ones, held-out regional Mw, histogram | Habermann (1991); Lolli et al. (2014) | the same tests on the two published Chilean catalogues |
| 9 Large events | corrections of single events | only from sources that were read; applied as the last step | Ruiz and Madariaga (2018) and the sources of the review table | list of the corrections (74) |
| 10 Tectonic class | weights for interface, in-slab, crustal and outer rise | literature class first; depth scores about the Slab2 surface averaged over the depth error; mechanism compared with the interface mechanism; events without depth take the class shares of their bin | Haynie et al. (2026); Hayes et al. (2018); Kagan (1991); Specht et al. (2017) | events with a literature class; sensitivity to each setting |

---

## B. Draft text

### 2. Earthquake catalogue

We built the catalogue from the original global and Chilean catalogues, without using a previous compilation as a starting point. Each earthquake receives one identifier, one location, one depth where a measured depth exists, one moment magnitude, and a weight for each tectonic class. Every choice is a rule applied to all events, and each rule is tested on events for which the answer is known.

#### 2.1 Sources

Thirteen sources were downloaded for latitudes 58.0° S to 15.5° S and longitudes 80.0° W to 60.0° W and frozen on 10 November 2026 (Table 1). All origins and all magnitudes of each source were kept with the agency and magnitude type as written. The relocated catalogue of Potin et al. (2024) covers the Chilean network from 1982 to July 2020; the catalogue of the Centro Sismológico Nacional (CSN) continues it to the download date. The Bulletin of the International Seismological Centre (ISC) provides the hypocentres and magnitudes of all contributing agencies from 1904. ISC-EHB, ISC-GEM, the Centennial catalogue and the calibrated locations of Bergman et al. (2023) provide relocated hypocentres. Moment magnitudes come from the Global CMT catalogue, the U.S. Geological Survey (USGS), the CSN and GFZ. Before 1904 we use the historical rows of Cabello et al. (2025), and for the large historical and recent earthquakes the magnitudes of Ruiz and Madariaga (2018).

#### 2.2 One identifier per earthquake

Records of different sources were first linked by the identifiers the sources share: the ISC event and origin identifiers carried by ISC-EHB and ISC-GEM, and the solution of each agency found inside an ISC event within 1.5 s and 10 km. The grouping of reported hypocentres into events inside the ISC Bulletin is the reviewed association of the ISC (Bondár and Storchak 2011).

The remaining records were matched by origin time and epicentral distance. Instead of one fixed window (for example 60 s and 100 km in Weatherill et al. 2016), we measured the window for each pair of sources as the 99th percentile of the offsets of pairs already known to be the same event, with a floor of 10 s and 50 km and a cap of 120 s and 450 km. Windows are widened by 1.5, 2 and 3 at magnitudes 6, 7 and 8. Where several candidates compete, the assignment that minimizes the total normalized offset is taken (Kuhn 1955). Magnitude is never a matching criterion. Events flagged as non-earthquakes by any source were removed. Uncertain links were written to review lists and not decided automatically.

Two checks bound the errors. When the identity links of a source are withheld and its records matched again by time and distance only, at most 0.04 % are attached to the wrong event and 0.07–0.76 % are missed. When a source is shifted by 10 or 20 minutes, so that no match can be real, 0.14 % of the records of the largest catalogue still find a partner. The matched set has 204 956 events of any size.

#### 2.3 Location and depth

The best location source differs between regions. Against the 775 calibrated locations of Bergman et al. (2023), the relocated local catalogue has epicentres within 3–6 km inside the network between 18° S and 36° S, but it is poorer than the teleseismic relocations south of the network and east of the volcanic arc (Supplement). We therefore use the local catalogue first only inside its own network (18–46° S, not east of the arc, from 1982), and only where its record lies within 50 km of the closest teleseismic or calibrated record of the same event; 94 events of Mw ≥ 4.5 fail this condition. There the order is Potin et al. or CSN, calibrated locations, ISC-EHB, ISC, USGS. Outside the network and in 1964–1981 the calibrated and teleseismic sources come first. Before 1964 we use the Centennial catalogue where it is EHB-relocated, then ISC-GEM, then the ISC; before 1904 the epicentres of Cabello et al. (2025). Epicentre and origin time always come from the same record.

Depth is taken from the first source in the same order that has a measured depth. Offshore, more than 20 km from the coast, the calibrated locations and ISC-EHB come before the local catalogue: there the local depths are a median 11 km shallower than the calibrated ones, against 1 km for the best ISC-EHB class. A depth is not measured when the source flags it as fixed, when it is an ISC-EHB solution of the lowest depth class, or when it sits on a default value of its agency (for example 10, 33 or 35 km). Default values were identified from the data, per agency and period, as depths that hold an anomalous share of the events. Fixed depths of the ISC are regional default values of its locator (Bondár and Storchak 2011) and are not used. One kind of fixed depth is kept, following the ISC-EHB definitions (Weston et al. 2018; Engdahl et al. 2020 [to check]): a fixed depth of the best class is held at a value constrained by depth phases and counts as measured. Before 1964 a depth is used only where its catalogue marks it as constrained: depth quality A or B in ISC-GEM (depth phases or nearby stations; Di Giacomo et al. 2018) or a free-depth solution in the Centennial catalogue (Engdahl and Villaseñor 2002). Events with no measured depth in any source keep an unknown depth; we do not fill them from the slab geometry at this stage. The depth uncertainty is at least 5 km, 10 km offshore and 20 km before 1964. With the calibrated locations left out of the rule, the catalogue differs from them by 8.8 km in epicentre and 7.0 km in depth on average.

Focal mechanisms are taken from the Global CMT catalogue and, where it has none, from the USGS solutions, W-phase solutions first.

#### 2.4 Moment magnitude

**Reference scale.** Global moment-tensor catalogues are incomplete below about Mw 5.5 and the Global CMT catalogue reads higher than regional moment magnitudes below 5.4 (Gasperini et al. 2012; Lolli et al. 2023). Our reference is the Global CMT value from 5.4 and, below, the family of regional and W-phase moment magnitudes: USGS W-phase and regional Mw, CSN regional and W-phase Mw, and GFZ Mw. Each member was shifted to the USGS W-phase scale by its mean difference on shared events; the shifts are at most 0.08 and do not vary with magnitude (Table 2). The moment magnitude of the CSN that is reported in the ISC Bulletin scatters more against the USGS W-phase values than the other members (standard deviation 0.20, against 0.07–0.14). It is not used to fit the offsets or the conversion relations, and an event takes it, after its own shift of −0.06, only when it has no other measured moment magnitude (106 events). A Global CMT value below 5.4 that is the only moment magnitude of its event is lowered by 0.162 × (5.4 − Mw), fitted on 812 events that also have a regional or W-phase value. A CSN value that differs by more than 0.3 from the median of two or more other moment magnitudes of its event is left out (26 regional values and 18 values of the ISC Bulletin). In total 6 334 events have a reference Mw.

**Conversion relations.** Only the magnitudes of the agencies that observe Chile directly or serve as global references are converted: mb and Ms of the ISC and the USGS National Earthquake Information Center (NEIC), ML of the CSN, and ML of the Argentine network INPRES. Because the reference exists for fewer than half of the events below magnitude 5, regressing Mw on the native magnitude selects the pairs on the dependent variable and is biased at the low end (Hausman and Wise 1977; Lolli et al. 2014). We regress the native magnitude on the reference Mw and invert the relation, with the slope corrected for the error of the reference (0.08 for Global CMT, 0.10 for the other members). For each scale, a straight line and a line with a saturation bend were fitted, with and without a split at 50 km depth (the depth of section 2.3), and the form was chosen by cross-validation in time blocks. Table 3 gives the relations. A synthetic test with a known relation shows that this fit stays within 0.05 of the truth where least-squares and orthogonal fits are off by 0.10–0.26 at native magnitude 4.5 (Supplement).

**One Mw per event.** From 1976 an event takes its reference Mw, then the value of Ruiz and Madariaga (2018) if they list it, otherwise one converted magnitude. Before 1976 a moment-based value goes before a converted one, and within each level the Centennial catalogue (Engdahl and Villaseñor 2002) goes before ISC-GEM. The order is: the value of Ruiz and Madariaga (2018); a measured reference Mw (nine events of 1964–1975 with a Global CMT value); a moment magnitude listed in the Centennial catalogue; a direct ISC-GEM Mw; the preferred Centennial magnitude converted, Ms with the relation of Di Giacomo et al. (2015) and the mB of Abe with the moment relation of Abe (1982) for shallow or for intermediate and deep events; an ISC-GEM proxy Mw; and the historical value of Cabello et al. (2025). Magnitudes are computed on the final depths of section 2.3, because the depth enters the mB relation, the surface-wave rule and the relations split by depth. The converted scale is the first available of: surface-wave magnitudes (NEIC, ISC), CSN ML, ISC mb, NEIC mb, INPRES ML, ordered by the scatter of their relations. Following the ISC-GEM practice (Di Giacomo et al. 2015), surface-wave magnitudes are used only for events not deeper than 60 km and without any magnitude limit. We tested a magnitude limit and rejected it: on events with a measured Mw that was withheld, a limit at Mw 5 changes the number of events at Mw ≥ 5 by +5 to +10 % or by −7 to −15 %, depending on how it is applied, against −2 % without a limit (Figure S-x; computed on the run of 12 Nov). Events with no usable magnitude are kept without Mw and listed.

**Large events.** The earthquakes of Mw ≥ 7, those of Mw 6–7 without depth and the named historical earthquakes were compared one by one with the literature. A correction is accepted only from a source that we read, and it is applied as the last step, after all rules, so that the rules themselves stay general. There are 74 corrections: seven magnitudes, one epicentre (1878), one depth and 65 tectonic classes (section 2.6; Table S-x) [references of the review table to add: see part E]. The depth is that of the earthquake of 1 March 1934, 120 km from depth phases; with it the mB relation for intermediate depth gives Mw 7.6. The literature was read for about a quarter of the selected events [to check: 112 of 459 on 13 Nov], so the review is not complete.

#### 2.5 Validation of the magnitude scale

A magnitude scale that is consistent in size and time should give the same b-value whatever the lowest magnitude of the fit, the same rate in every period, and should predict the number of large earthquakes from the small ones. We applied five tests to the declustered catalogue (Gardner and Knopoff 1974) and to the full one:

1. The b-value changes by 0.08 between fit floors of 4.7 and 5.8 for 1976 to today, and by 0.14 for 2011 to today.
2. The rate of Mw ≥ 5.5 is 15.9, 15.5, 19.4 and 17.1 events per year in 1976–1989, 1990–1999, 2000–2010 and 2011 to today; the largest departure from the mean is 14.1 %.
3. The Gutenberg–Richter relation fitted from Mw 5.0 predicts 36.9 earthquakes of Mw ≥ 7 against 43 observed, and 87.8 of Mw 6.5–7 against 108. Of 32 combinations of source type, declustering, fit floor and magnitude range, 30 are inside the 95 % band; one of the two outside is the Mw 6.5–7 count just given (band 88.6–130.4).
4. Converted magnitudes were compared with regional Mw values held out of the fits. Sixteen of 20 bins agree within 0.1. The exceptions are ISC mb and NEIC mb at 5.0–5.5, which read 0.10–0.17 above the regional Mw.
5. The magnitude histogram of each period has no bin that departs from its neighbours by more than 2.2 standard deviations.

The same tests on the two published Chilean catalogues (Figure 3) give a b-value change of 0.26 and 0.47 for Cabello et al. (2025) and 0.11 and 0.36 for Candia and Macedo (2026), a rate departure of 34 % and 17 %, and 26 of 35 and 25 of 46 earthquakes of Mw ≥ 7 predicted. Both list 64–102 events per year at M ≥ 5.0, against 44–57 here; from 2011, when 82 % of our values at Mw ≥ 5.0 are measured moment magnitudes, the difference remains.

#### 2.6 Tectonic class

Each event has a weight for interface, in-slab, crustal and outer-rise that add to 1. An event that the rules cannot place keeps its weight as unclassified (four events). The slab geometry is Slab2 (Hayes et al. 2018).

A class from the literature comes first (65 events, 56 of them from Ruiz and Madariaga 2018). Events west of the trench are outer rise. South of the Chile triple junction, shallow events within 150 km landward of the trench are interface of the Antarctic plate.

Over the shallow slab, where the Slab2 surface is not deeper than 50 km, the depth gives a score to each class after Haynie et al. (2026). The interface score is 1 within ± 15 km of the Slab2 surface and fades to 0 between 50 and 65 km depth. What is left goes to crustal above the slab and to in-slab below it, with a transition of 20 km on each side of the slab surface; the crustal score also fades from the Moho (fixed at 40 km) down to the slab surface. Haynie et al. use the catalogue depth as exact. We average the scores over the depth error of each event, a normal distribution about the catalogue depth with the uncertainty of section 2.3; this step is ours.

A focal mechanism is compared with the interface mechanism at the epicentre: the Slab2 plane slipping in the direction of plate convergence (azimuth 257°). The misfit has two parts. The swing σ is the tilt of the fault plane from the slab plane, and the twist τ is the turn of the slip direction within the plane. We combine them as m = [(σ / 20°)² + (τ / 45°)²]^½ and take the smallest value over the four equivalent descriptions of the double couple. The two angles are the two parts of the rotation angle Φ between double couples (Kagan 1991), cos(Φ/2) = cos(σ/2) cos(τ/2); m scales them apart, strict on the plane and loose on the slip direction. This measure is ours. Where m ≤ 1 the interface odds given by the depth are multiplied by 3.9, the ratio of the share of such mechanisms within 5 km of the slab surface to their share beyond 15 km, among events with calibrated or depth-phase depths. Where m > 1 the event has no interface weight. A mechanism never decides alone. A cluster analysis of the nodal planes after Specht et al. (2017), used as a check only, finds the same group of interface mechanisms [to check on the final run: 833 of 878 events on 14 Nov].

Where the slab is deeper, the depth with its error places the event above or below the slab surface: crustal down to 50 km depth, in-slab below. A weight of 0.8 or more becomes 1. An event without a measured depth is in-slab where the slab is deeper than 50 km and every rejected depth is 70 km or more, and crustal where there is no slab; otherwise it takes the class shares of the classified events of its bin of slab depth, latitude and magnitude, and stays split. Sub-classes follow the position: the Jujuy nest (within 0.8° of 66.9° W, 24.0° S, 150–320 km depth) is kept apart from the other in-slab events, and crustal events are divided into forearc, arc, backarc and Patagonia.

For the 65 events with a literature class, the rules alone give the same class for 36, split 9, have no depth for 18 and give another class for 2 (Copiapó 1918, epicentre west of the trench; La Ligua 1971, slab surface at 56 km). The interface total at Mw ≥ 4.5 falls by 23 % with a zone of ± 10 km and rises by 11 % with ± 20 km; without mechanisms it rises by 4 % (Figure S-x).

The rule has limits. The tolerances of 20° and 45° are chosen, not fitted. One convergence azimuth is used for the whole margin. Only about a quarter of the events with a depth over the shallow slab have a mechanism (1 250 of 5 412); for the others the depth decides alone. The factor 3.9 rests on about 200 events and uses the distance to the slab as a stand-in for the class [to check on the final run: 151 and 53 events on 14 Nov].

#### 2.7 The catalogue

In the model domain (17–58° S, 65–78.5° W) the catalogue has 14 279 earthquakes of Mw ≥ 4.5 from 1513 to November 2026 (Figures 1 and 2). Of these, 4 296 have a measured moment magnitude, 9 177 a converted one (5 042 from mb, 2 782 from ML, 1 353 from surface-wave magnitudes), and 806 a value from ISC-GEM (542), the Centennial catalogue (126), Cabello et al. (2025) (104), Ruiz and Madariaga (2018) (27) or the review of large events (7). Epicentres come from the ISC (5 339), Potin et al. (3 412), ISC-EHB (4 183), the CSN (774) and other sources (571). A measured depth exists for 12 391 events and a focal mechanism for 2 671.

The summed class weights are 4 497.7 for interface (31 %), 8 078.9 for in-slab (57 %; 1 054 of them in the Jujuy nest), 1 189.3 for crustal (8 %) and 509 for outer rise (4 %); 4 events are unclassified. A single class holds the full weight for 11 251 events. The other 3 028 are split: 1 736 have a depth and lie near a class boundary, and 1 292 have no measured depth. At Mw ≥ 7 (163 events) the sums are 71.5, 67.4, 16.0 and 8; 62 of these events are split, 54 of them without depth.

[Completeness periods and declustering: to be written after the completeness step.]

#### 2.8 Limitations

- No measured depth exists for 1 888 events (13 %), almost all outside the Chilean network: 389 before 1964, where only 84 events keep a depth, and 1 099 from 1976, of which two thirds are below Mw 5. Their class comes from the literature, from the position or from the class shares of their bin (section 2.6); 54 of the 163 events of Mw ≥ 7 are split for this reason.
- The classification depends most on the width of the interface zone (± 15 km): ± 10 and ± 20 km move the interface total by −23 % and +11 %. The tolerances of the mechanism misfit are chosen, not fitted, and the convergence azimuth is one value for the margin (section 2.6).
- Between 1976 and 1989, 61 % of the magnitudes at Mw ≥ 5.0 are converted from mb, and mb conversions read about 0.1 above the regional Mw at 5.0–5.5 (test 4). We carry this as a sensitivity case in the recurrence fits [to be done].
- The correction of Global CMT below 5.4 is a smooth line chosen to avoid a step at 5.4; it departs from the measured bin means by up to 0.04 on the 1 017 values lowered (865 in the domain).
- The rules for the surface-wave scales and for the Global CMT correction were chosen among 16 combinations with the help of tests 1, 2, 3 and 5. These tests are therefore a description of the final catalogue and not an independent validation of it. The withheld-Mw check and test 4 were not used for the choice.
- For 131 events the CSN regional Mw and the USGS regional Mw are the only moment magnitudes and differ by more than 0.3. The two have a similar error (about 0.11) and the USGS value is 0.15 lower on average, so the data do not say which is right; the CSN value is used.
- Before 1976 the converted mB of Abe reads above the ISC-GEM proxy values for the same events [to check on the final run: mean 0.39 on 16 events on 13 Nov]; the order of section 2.4 takes the Centennial value.
- The rate of Mw ≥ 5.5 in 2000–2010 is higher than in the other periods (19.4 against 15.5–17.1 per year, declustered). The period contains the 2010 Maule sequence [check with the model declustering].

---

## C. Figures and tables

| item | content | status | file |
|---|---|---|---|
| Figure 1 | map of the catalogue (Mw ≥ 4.5) | planned | – |
| Figure 2 | source of Mw and of the location through time | parts exist | `catalog/figs/locate/who_decides.png`, `catalog/figs/magnitude/coverage.png` |
| Figure 3 | tests against Cabello et al. (2025) and Candia and Macedo (2026) | draft | `catalog/figs/magnitude/test7_comparison.png` |
| Table 1 | sources: period, number of events, what is used from each | to build from `catalog/SOURCES.md` | – |
| Table 2 | offsets of the reference Mw members | data ready | `catalog/merged/mw_offsets_2026-11-14b.csv` |
| Table 3 | conversion relations: form, pairs, σ, Mw at native 4.5–6.0 | data ready | `catalog/merged/relations_2026-11-14b.csv` |
| Supplement | matching windows and checks | data ready | `catalog/merged/windows_`, `check_blind_`, `check_chance_`, `catalog/figs/match/summary.png` |
| Supplement | location benchmark against calibrated events; cross-sections; unknown depths | draft | `catalog/figs/locate/gccel.png`, `sections.png`, `depth_unknown.png` |
| Supplement | relations with data; forward against inverse; offsets | draft | `catalog/figs/magnitude/relations.png`, `forward_inverse.png`, `offsets.png` |
| Supplement | tests 1–6 one figure each; synthetic test | draft | `catalog/figs/magnitude/test1_` … `test6_`, `test9_synthetic.png` |
| Supplement | rule for the surface-wave scales (withheld Mw) | draft | `explore/X4/figs/x4_rule_choice.png` |
| Supplement | sensitivity of the tests to each choice | data ready | `catalog/merged/mw_sensitivity_2026-11-14b.csv` |
| Supplement | corrections of large events (74 rows) | data ready | `catalog/overrides_A6.csv` |
| Figure (new) | classes on the map and in sections with the Slab2 surface and the ± 15 km zone | draft | `catalog/figs/classify/maps.png`, `sections.png` |
| Table (new) | class weights at Mw ≥ 4.5, 5.5 and 7 | data ready | `catalog/merged/class_counts_2026-11-14c.csv` |
| Supplement | classification: sensitivity, events with a literature class, events of Mw ≥ 7, Jujuy nest | draft | `catalog/merged/class_sensitivity_`, `class_named_`, `class_m7_2026-11-14c.csv`, `catalog/figs/classify/sensitivity.png`, `nest.png` |

---

## D. Where each number comes from

| numbers | file |
|---|---|
| sources, download box, counts per source | `catalog/SOURCES.md`, `catalog/sources/MANIFEST.csv` |
| matching rules, windows, check rates, 204 956 events | `catalog/merged/METHOD.md`, `counts_`, `check_blind_`, `check_chance_2026-11-11.csv` |
| location order, default depths, benchmark 8.8 / 7.0 km, offshore depth differences | `catalog/locate.py` (settings), `catalog/merged/loc_gccel_`, `defaults_2026-11-14b.csv`; WORKLOG entries A4 and 13 Nov. The 94 events of the 50 km condition were recounted on the final run (`explore/B9/STEP0.md`); the offshore depth differences (11 km, 1 km) were not |
| Potin 3–6 km inside the network | `explore/X3/REPORT.md` |
| reference members, offsets, 812 pairs, 6 334 events, 26 + 18 and 131 CSN values | printed output of `magnitude.py`, `catalog/merged/review/mw_reference_dropped_2026-11-14b.csv`, `mw_offsets_2026-11-14b.csv` |
| relations | `relations_2026-11-14b.csv` (same table in `catalog/MAGNITUDES.md` §3) |
| withheld-Mw percentages | `explore/X4/tables/x4_blind.csv` (run of 12 Nov, not redone) |
| tests 1–5 and the comparison | `mw_tests_`, `mw_sensitivity_2026-11-14b.csv` (declustered values for tests 1 and 2, full catalogue fitted from 5.0 for test 3; `MAGNITUDES.md` holds the values of run `2026-11-14b`, except its §6a, of 12 Nov) |
| synthetic test | `catalog/MAGNITUDES.md` §7, `mw_synthetic_2026-11-14b.csv` |
| order of the magnitudes before 1976, Abe mB, CSN moment magnitude of the ISC Bulletin | `catalog/magnitude.py` (module note, settings `OLD`, `LAST`, `MB_A82`) |
| corrections of large events (74: 7 Mw, 1 longitude, 1 depth, 65 classes) | `catalog/overrides_A6.csv`, rows with status `accepted`; selection and literature counts in the WORKLOG entries A6 of 13 Nov |
| classification rule and settings | `catalog/classify.py` (module note and settings), `catalog/CLASSIFICATION.md` (run `2026-11-14c`) |
| class weights, split events, literature events, Mw ≥ 7, sensitivity | `catalog/merged/class_counts_`, `class_named_`, `class_m7_`, `class_sensitivity_2026-11-14c.csv` |
| mechanisms over the shallow slab (1 250 of 5 412; 864 with m ≤ 1) | `catalog/merged/catalog_2026-11-14c.csv`: `in_domain`, `mw` ≥ 4.45, `top` ≤ 50, rule `depth` or `depth_split`, `mech_m` |
| counts of section 2.7 and 2.8 | `catalog/merged/catalog_2026-11-14c.csv`, rows with `in_domain` and `mw` ≥ 4.45 |

---

## E. Open before this text can be final

1. Completeness and the declustering for the model are not done; 2.7 is incomplete without them.
2. Sensitivity of the recurrence fits to the mb conversions before 1990 (third limitation of 2.8).
3. The explanation of why we have fewer events at M ≥ 5 than the two published catalogues (33–45 % fewer than Cabello et al. 2025 and 19–42 % fewer than Candia and Macedo 2026, by period) is stated in 2.5 in one sentence; it needs its own check per period and probably a supplement figure.
4. The review of large events is not complete: literature was read for about a quarter of the selected events (WORKLOG, 13 Nov). Two events are corrected in the review table: 2010-02-27 08:25, converted from ML alone (6.97 → 6.3), and 2011-01-07 04:55, where the rule gives the CSN moment magnitude of the ISC Bulletin (5.6 → 5.7).
5. Answered on 13 Nov (S. Ruiz): the Centennial catalogue before ISC-GEM within each level before 1976. Open: the converted Abe mB against the ISC-GEM proxy values (limitation in 2.8).
6. References not yet in `REFERENCES.md` or with details unchecked: Bergman et al. (2023), Candia and Macedo (2026, doi:10.1785/0220250449), Gasperini et al. (2012), Hausman and Wise (1977), Kuhn (1955), Bondár and Storchak (2011), Gardner and Knopoff (1974), Habermann (1991), Engdahl et al. (2020; the definition of the fixed depths was read on the ISC-EHB web page, not in the paper). New in this version: Abe (1982), Hayes et al. (2018; not re-read), Haynie et al. (2026), Kagan (1991; not re-read), Specht et al. (2017) (entries in `REFERENCES.md` section F and `catalog/CLASSIFICATION.md`). Sources of the review table that the text does not yet cite: Astiz and Kanamori (1986), Abe and Kanamori (1979), Astiz (1987), Lomnitz (2004), Kanamori and Rivera (2017).
9. The withheld-Mw check of the surface-wave rule (2.4) was computed on the run of 12 Nov and not repeated on the final run.
7. The test periods and the declustering in 2.5 are those of `catalog/magnitude_check.py`; check the wording against its settings before submission.
10. Classification numbers marked [to check] in 2.6 (cluster check 833 of 878, the 151 and 53 events behind the factor 3.9) are of the run `2026-11-14a` and were not recomputed on `2026-11-14c`.
8. Journal length: parts 2.2 to 2.5 are about 900 words; 2.6 adds about 550. For a hazard paper, 2.2 and 2.3 can shrink to one paragraph each with the detail in the supplement.
