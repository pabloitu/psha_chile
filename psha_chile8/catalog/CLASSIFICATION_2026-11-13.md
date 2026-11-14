# Tectonic classification with class weights (A7)

**Current run: `2026-11-13j` (sections 12 and 13): a mechanism decides between interface and not interface where there is one, and the band is 15 km.** Sections 1–11 describe run `2026-11-13f` (mechanisms only exclude, band = Slab2 uncertainty); section 12 run `i`. Every table exists as `_2026-11-13f`, `_i` and `_j`. The depth σ is as in A4 (the change of runs `g` and `h` was withdrawn).

Run `2026-11-13f`, 13 Nov 2026. Code `classify.py` (rules), `classify_check.py` (checks, figures), `tests/test_classify.py` (20 tests).
Input: `merged/catalog_2026-11-13e.csv` (the rerun of step 0: 204 956 events, 14 279 of Mw ≥ 4.5 in the domain, 12 391 of them with a measured depth, 2 671 with a mechanism). Output: `merged/classes_2026-11-13f.csv`, `merged/catalog_2026-11-13f.csv`.
Numbers below are events of Mw ≥ 4.5 in the domain unless said otherwise.

## 1. What to read first

1. **Nearly a third of the events is split: 4 445 of 14 279** (3 153 near the band, 1 292 without depth); 772 of 1 943 at Mw ≥ 5.5 and 67 of 163 at Mw ≥ 7. The brief expected most events at weight 1. Over the shallow slab 58 % of the events with a depth are split.
2. **The cause is the ratio of the band to the depth error, not the band.** The Slab2 uncertainty holds as a band (section 4): 86 % of the well-located thrust events lie within it and 98 % within it plus their σ. But an event exactly on the surface gets an interface weight of 2Φ(W/σ) − 1, which reaches 0.8 only if W ≥ 1.28 σ. With W about 12 km and a σ of 10 km (the offshore floor of A4, and Potin's σ) this is 0.77. 53 % of the events over the shallow slab have W < 1.28 σ and cannot be hardened to interface at any depth.
3. **The depth σ of the catalogue is larger than the scatter it is meant to describe.** The thrust events scatter about the Slab2 surface with a robust sd of 6.6 km (calibrated and depth-phase depths) and 8.0 km (all), which includes the error of Slab2; their catalogue σ has a median of 10 km. Of 959 thrust events on the contact with a depth, 235 are interface with weight 1, 660 are split, 64 are in-slab or crustal; their summed interface weight is 644.
4. **Not tuned.** What would change it is in the sensitivity table (section 7): hardening at 0.7 gives 3 111 split events, W = 15 km 3 117, W = 20 km 2 460. **The depth σ was looked at afterwards (section 11): it is only part of it.** Without the offshore floor 3 695 events stay split; the floor is too large for ISC-EHB L1 and Potin and about right for ISC and ISC-EHB L2.
5. **The totals move less than the split count.** Interface 3 672, in-slab 8 549, crustal 1 545, outer rise 509, unclassified 4. Hardening (0.7, 0.9, none) moves the interface total by −0.5 to +6.6 %; the band width moves it by −12 % (10 km) to +41 % (20 km).

## 2. The Slab2 grids (first check of the brief)

Slab2 South America, version 02.23.18 (Hayes et al. 2018), grids `dep`, `thk`, `dip`, `str`, `unc` (`merged/class_grids_2026-11-13f.csv`).

- `dep` is the slab surface: on the Nazca trench line (18–45° S) it is at 9.4 km (6.7–11.5; the brief expected about 5 km, the value is the depth of the trench floor below sea level), it deepens landward (correlation with distance from the trench 0.94), and thrust events sit on it (median 2.1 km below).
- `thk` is the plate thickness: median 79 km (68–86).
- `unc` is the depth uncertainty of the surface. The USGS data release was not opened in this session; the reading rests on the file name and on the values: median 10.2 km where the top is above 20 km, 12.6 km at 20–50 km, 25 km at 50–100 km, 33 km below 100 km.

## 3. Rules as applied

Each event has five weights (`w_interface`, `w_inslab`, `w_crustal`, `w_outer_rise`, `w_unclassified`) that add to 1, `cls` (the class with weight 1, else `split`), `cls_auto` (the same from the rules alone) and `rule`.

**R1, literature (`hint`, 63 events).** An accepted class hint of `overrides_A6.csv` gives weight 1. `cls_auto` and the columns `a_*` keep what the rules give.

**R2, outer rise (`outer_rise`, 506).** West of the Nazca trench (the Antarctic trench south of 46.15° S), with or without depth.

**R3, mechanism.** Thrust on the plate contact (one nodal plane within 35° of the Slab2 plane, rake 45–135°): 1 021 of the 2 671 mechanisms, 974 of them over a slab top ≤ 50 km. Any other mechanism rules the interface out. Interface is possible only where the slab top is ≤ 50 km. As written, a thrust mechanism and no mechanism allow the same classes, so the mechanism only excludes; see section 7.

**R4, band.** Half-width W = the Slab2 depth uncertainty at the epicentre (15 km where the grid has none; no event needed it).

**R5, depth and its error (`depth` 8 773, `depth_split` 3 153).** The true depth is normal about the catalogue depth with the catalogue σ (at least 5 km). Probability above the band → crustal if the event is not deeper than 50 km, else in-slab; in the band → interface if allowed, otherwise crustal above the surface and in-slab below; below the band or the plate → in-slab. A weight of 0.8 or more becomes 1. No slab: crustal to 50 km (`no_slab`, 63), deeper unclassified (`no_slab_deep`, 4).

**R6, no measured depth.** No slab: crustal (`nodepth_no_slab`, 58). Slab top deeper than 50 km and every rejected depth ≥ 70 km: in-slab (`nodepth_deep`, 225). Otherwise the shares of the classified events of the same bin among the classes R3 allows (`nodepth_share`, 1 292), no hardening. Shares in `merged/class_shares_2026-11-13f.csv`.

**R7, sub-classes** by position: `sub_interface` (interface, antarctic_interface), `sub_inslab` (intraslab_shallow where the slab top is ≤ 50 km, intraslab_intermediate, jujuy_nest), `sub_crustal` (forearc, arc, backarc, patagonia). A split event carries the sub-class of each family it has weight in.

**R8, assigned depth (17 events).** Literature class, no measured depth, slab at the epicentre: interface on the slab top kept within 10–50 km; in-slab at 0.30 of the Slab2 thickness below the top (the hypocentre of the in-slab sources of psha_chile6–7); σ 20 km. In `catalog_2026-11-13f.csv` these have `depth_kind = assigned`; the rules read only `measured`.

**Choices made where the brief was open** (each is one setting at the top of `classify.py`):
- The depth error is cut at the ground: the normal distribution is renormalised to depths ≥ 0. Without it an event at 4 km over a slab top of 12 km was 46 % crustal from probability at negative depths; interface total 3 554 without, 3 672 with.
- "Not deeper than 50 km" (above the band → crustal) is read on the catalogue depth, not integrated over the error.
- **Antarctic interface (`antarctic`, 142 events, 26 of Mw ≥ 5.5, 1 of Mw ≥ 7):** every event that meets the position rule (south of 46.15° S, within 150 km landward of the Antarctic trench, not deeper than 60 km or no depth, no non-thrust mechanism) is interface with weight 1. 97 of them have no depth. They would otherwise be crustal Patagonia, which keeps 77. There is no slab model there to weigh them.
- Rejected depths are the depths of the source records A4 looked at (one per source), not every agency of the ISC Bulletin.
- Shares are counted on events with a slab at the epicentre, east of the trench, from 1976, Mw ≥ 4.5, with a measured depth or a literature class. Events outside the latitude bands take the nearest band; events below Mw 4.5 take the lower range.
- `n_candidates` is the number of classes the position and the mechanism allow (1 to 3).
- All 204 956 events get a row; the bin shares and every count here are of Mw ≥ 4.5.

**Bins that borrowed:** slab top 50–100 km, 38–46° S, Mw ≥ 5.5 (0 events, takes the 46 of the lower range) and slab top > 100 km, 38–46° S, Mw ≥ 5.5 (7, takes 55). None needed the neighbouring latitude band.

## 4. Band measurement

Events that are interface without their depth: thrust on the plate contact, plus the interface events of the literature with a measured depth; slab top ≤ 50 km; d = depth − Slab2 surface. `merged/class_band_2026-11-13f.csv`, `figs/classify/band.png`.

| | n | median d | robust sd | 68 % / 90 % half-width | median unc | within unc | within unc + σ | within 10 / 15 / 20 km |
|---|---|---|---|---|---|---|---|---|
| all depths | 979 | +2.1 | 8.0 | 8.8 / 16.2 | 11.8 | 78 % | 94 % | 74 / 88 / 94 % |
| GCCEL and ISC-EHB L1 | 257 | +3.4 | 6.6 | 7.7 / 12.8 | 12.0 | 86 % | 98 % | 79 / 96 / 98 % |
| other depths | 722 | +1.8 | 8.5 | 9.2 / 18.1 | 11.6 | 76 % | 93 % | 72 / 86 / 93 % |
| other mechanisms, all | 296 | +10.3 | 15.2 | 19.1 / 30.4 | 12.5 | 42 % | 68 % | 39 / 54 / 69 % |
| other mechanisms, best | 128 | +8.2 | 10.7 | 15.1 / 23.9 | 12.1 | 52 % | 79 % | 52 / 67 / 82 % |

- **`unc` holds as W.** Far more than two thirds of the well-located thrust events are within W plus their σ. No other width is suggested; the 90 % half-width of the best depths (12.8 km) is the median `unc`.
- **Bias:** thrust events are 2–3 km below the surface (best depths: +7.0 km where the top is above 20 km, +2.3 at 20–35, −0.8 at 35–50; by latitude +0.5 at 17–24° S, +3.4 at 24–30, +5.0 at 30–38, −3.3 at 38–46 on 10 events). CSN web depths are 8.7 km below (96 events).
- **Spread after removing σ:** zero. The catalogue σ (median 10 km) is larger than the observed scatter, so nothing is left for Slab2. The σ of the best sources is a floor, not a measured error.
- **Other mechanisms** lie mostly below (median +10 km) but 42 % are inside the band (52 % of the best depths): "mostly outside" holds only weakly. Inside the band they are split between crustal and in-slab by side.
- By slab-top range the share within `unc` rises with depth (68 % above 20 km, 80 % at 20–35, 91 % at 35–50), because `unc` grows and the scatter does not.

## 5. Counts

`merged/class_counts_2026-11-13f.csv` (summed weights).

| | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 7 |
|---|---|---|---|
| events | 14 279 | 1 943 | 163 |
| interface | 3 671.8 | 608.8 | 62.7 |
| – interface (Nazca) | 3 529.8 | 582.8 | 61.7 |
| – antarctic_interface | 142.0 | 26.0 | 1.0 |
| in-slab | 8 548.8 | 961.9 | 71.6 |
| – intraslab_shallow | 2 106.4 | 330.1 | 20.2 |
| – intraslab_intermediate | 5 537.4 | 576.7 | 48.3 |
| – jujuy_nest | 905.0 | 55.0 | 3.0 |
| crustal | 1 545.4 | 279.4 | 20.7 |
| – forearc | 937.2 | 163.5 | 12.3 |
| – arc | 221.6 | 31.8 | 2.5 |
| – backarc | 309.6 | 61.0 | 2.9 |
| – patagonia | 77.0 | 23.0 | 3.0 |
| outer rise | 509.0 | 93.0 | 8.0 |
| unclassified | 4.0 | 0 | 0 |
| events at weight 1 | 9 834 | 1 171 | 96 |
| split, near the band | 3 153 | 453 | 13 |
| split, no depth | 1 292 | 319 | 54 |
| no depth, decided by position | 283 | 49 | 10 |
| literature class | 63 | 63 | 52 |
| in-slab events below the plate | 84 | 3 | 0 |

**Against earlier classifications** (`merged/class_compare_2026-11-13f.csv`; where the weight of the earlier class went).

| earlier class | events | interface | in-slab | crustal | outer rise | split events |
|---|---|---|---|---|---|---|
| X4 interface | 3 892 | 2 848.9 | 652.2 | 391.0 | 0 | 2 643 |
| X4 in-slab | 7 068 | 77.9 | 6 943.9 | 46.3 | 0 | 292 |
| X4 crustal | 961 | 106.4 | 10.7 | 843.9 | 0 | 196 |
| X4 unknown depth | 1 643 | 602.0 | 790.1 | 250.8 | 0 | 1 268 |
| X4 unclassified | 91 | 0 | 87.0 | 0 | 0 | 0 |
| old interface | 4 173 | 2 700.7 | 977.0 | 474.4 | 21 | 2 879 |
| old in-slab | 6 395 | 249.4 | 6 027.6 | 106.0 | 12 | 458 |
| old crustal | 738 | 126.4 | 80.9 | 527.7 | 1 | 285 |
| old, no family | 716 | 19.5 | 464.4 | 231.1 | 0 | 202 |
| not in the old catalogue | 1 997 | 566.0 | 984.2 | 203.8 | 242 | 604 |

- X4 is the baseline of `explore/X4` (± 15 km, run `2026-11-13b`), joined by event ID; 120 events of this run were not in it. The old classifier is the frozen catalogue of 2026-11-04, matched by time and distance as in `x4b_compare.py`.
- The interface loses a quarter of its X4 weight to in-slab and crustal (narrower band, and the error spreads the weight); 2 643 of the 3 892 X4 interface events are split. In-slab and crustal are close to X4.
- The X4 "unclassified" events (above a deep slab and deeper than 50 km) are in-slab.

## 6. Named events and large events

**Literature class against the rules alone** (`merged/class_named_2026-11-13f.csv`): 63 events; right 30, no depth 18, split 12, wrong 3.

| event | literature | rules alone | reason |
|---|---|---|---|
| Copiapó 1918, Mw 7.8 | interface | outer rise | ISC-GEM epicentre west of the trench, no depth |
| La Ligua 1971, Mw 7.8 | interface | in-slab | slab top 55.6 km at the epicentre, over the 50 km limit |
| Valparaíso 1985, Mw 7.9 | interface | in-slab | depth 49.6 ± 5 km, 21 km below the surface, thrust mechanism |
| Concepción 1960, Mw 8.1 | interface | split (0.41 / 0.09 / 0.50) | depth 11.5 ± 20 km, 19 km above |
| Valdivia 1960, Mw 9.5 | interface | split (0.42 / 0.10 / 0.48) | depth 25 ± 20 km, 14 km above |
| Taltal 1966, Mw 7.7 | interface | split (0.53 / 0 / 0.47) | 11 km above, σ 5 km |
| Copiapó 1983, Mw 7.6 | interface | split (0.67 / 0 / 0.33) | 11 km above |
| Maule 2010, Mw 8.8 | interface | split (0.79 / 0.08 / 0.13) | 1.4 km above, σ 10 km: on the surface and still under 0.8 |
| Pichilemu 2010 14:55, Mw 7.0 | crustal | split (0 / 0.58 / 0.42) | 2 km below, normal mechanism |
| Arauco 2011, Mw 7.1 | interface | split (0.42 / 0.01 / 0.57) | Potin depth 2.8 km, 16 km above |
| Iquique foreshock 2014, Mw 6.7 | crustal | split (0.42 / 0.02 / 0.56) | 14 km above, thrust mechanism |
| Iquique 2014, Mw 8.1 | interface | split (0.58 / 0.36 / 0.05) | 6 km below, σ 10 km |
| Iquique aftershock 2014, Mw 7.7 | interface | split (0.75 / 0.10 / 0.15) | 1.2 km above, σ 10 km |
| Chiloé 2016, Mw 7.6 | interface | split (0.52 / 0.48 / 0) | 6.6 km below, W 6.9 km |
| Valparaíso 2017, Mw 6.9 | interface | split (0.28 / 0.71 / 0) | 17 km below |

Weights in brackets: interface / in-slab / crustal. All carry the literature class in `cls`. No rule was added for any of them.

**Events of Mw ≥ 7** (`merged/class_m7_2026-11-13f.csv`, 163): 52 by the literature; 44 with weight 1 from the rules (27 by depth, 8 in-slab by deep defaults, 6 outer rise, 2 crustal without slab, 1 Antarctic interface); **67 not at weight 1**: 54 without depth (36 before 1904, 18 in 1904–1940, none later) and 13 near the band:

| date | Mw | depth ± σ | d | mechanism | interface / in-slab / crustal |
|---|---|---|---|---|---|
| 1940-10-04 | 7.0 | 23.5 ± 20 | +1.5 | | 0.42 / 0.39 / 0.19 |
| 1946-08-02 | 7.1 | 39.2 ± 20 | +0.9 | | 0.52 / 0.27 / 0.21 |
| 1953-05-06 | 7.5 | 66.0 ± 20 | +24.1 | | 0.29 / 0.71 / 0 |
| 1960-06-20 02:01 | 7.0 | 25.0 ± 20 | −9.5 | | 0.44 / 0.16 / 0.39 |
| 1960-06-20 12:59 | 7.1 | 24.6 ± 20 | −18.0 | | 0.34 / 0.08 / 0.58 |
| 1960-12-02 | 7.2 | 14.1 ± 20 | −35.1 | | 0.20 / 0.01 / 0.80 |
| 1962-02-14 | 7.1 | 40.6 ± 20 | −2.6 | | 0.51 / 0.21 / 0.27 |
| 1965-02-23 | 7.0 | 41.8 ± 5.6 | +12.4 | | 0.43 / 0.57 / 0 |
| 1988-01-19 | 7.0 | 27.9 ± 6.8 | −5.6 | thrust | 0.80 / 0.01 / 0.20 |
| 1988-04-12 | 7.1 | 31.5 ± 10 | −10.2 | thrust | 0.68 / 0.01 / 0.31 |
| 2001-07-07 | 7.6 | 24.5 ± 10 | −15.9 | thrust | 0.43 / 0 / 0.57 |
| 2014-04-01 23:58 | 7.0 | 19.0 ± 10.4 | −1.7 | thrust | 0.64 / 0.15 / 0.21 |
| 2015-09-16 23:18 | 7.1 | 5.2 ± 10.4 | −24.3 | thrust | 0.22 / 0 / 0.78 |

The 54 without depth carry the shares of their bin (for example 0.60 / 0.28 / 0.12 at 30–38° S over the shallow slab). They are the events A6 has not settled; the list is the column `rule = nodepth_share` of the table.

Weight 1 by the rules, worth a look: 1944-01-15 Mw 7.1 crustal (27.7 km, slab top 95 km: San Juan, as expected); 1960-11-01 Mw 7.4 and 1922-11-07 Mw 7.1 outer rise at 9 km from the trench; 1911, 1913, 1919-03-02 11:45 and 1922-01-06 outer rise from epicentres before 1964; six events of 1687–1870 in-slab because Cabello's depths for them are 70 km or more (deep defaults of a historical catalogue: weak).

**Thrusts on the contact of Mw ≥ 6.5 with an interface weight under 0.5** (`merged/review/class_thrust_not_interface_2026-11-13f.csv`, 12): four Illapel 2015 aftershocks and 2007-11-15 with Potin depths of 0–5 km over a slab top of 28–36 km (crustal with weight 1 or 0.75–0.78; the Potin coastal depths of the A3–A5 report), Arequipa aftershocks of 2001, 1987-08-13 and 1993-07-11 (slab top over 50 km), 1997-07-06 and 2004-05-03 (12 km below). Candidates for class hints if a source states their class.

## 7. Sensitivity

`merged/class_sensitivity_2026-11-13f.csv`, `figs/classify/sensitivity.png`.

| setting | interface | in-slab | crustal | interface, Mw ≥ 5.5 | split events | largest class changes (Mw ≥ 4.5 / 5.5 / 7) |
|---|---|---|---|---|---|---|
| baseline | 3 671.8 | 8 548.8 | 1 545.4 | 608.8 | 4 445 | |
| W = 10 km | 3 249.3 | 8 817.2 | 1 699.6 | 545.3 | 4 627 | 417 / 61 / 2 |
| W = 15 km | 4 518.8 | 8 053.1 | 1 194.1 | 726.3 | 3 117 | 614 / 61 / 1 |
| W = 20 km | 5 160.7 | 7 602.8 | 1 002.5 | 809.9 | 2 460 | 1 113 / 163 / 9 |
| hardening 0.7 | 3 913.4 | 8 447.4 | 1 405.2 | 642.7 | 3 111 | 154 / 0 / 0 |
| hardening 0.9 | 3 662.7 | 8 544.7 | 1 558.6 | 605.6 | 5 058 | 0 |
| no hardening | 3 652.2 | 8 547.2 | 1 566.5 | 600.7 | 6 688 | 0 |
| interface to a slab top of 60 km | 3 843.2 | 8 416.9 | 1 505.9 | 629.0 | 4 495 | 196 / 24 / 0 |
| mechanisms not used | 3 822.6 | 8 452.9 | 1 490.4 | 678.9 | 4 517 | 322 / 93 / 7 |
| a thrust on the contact is interface (not in the brief) | 4 056.0 | 8 293.4 | 1 416.6 | 768.3 | 3 785 | 337 / 78 / 2 |
| events without depth that take shares left out | 3 157.7 | 7 964.3 | 1 352.0 | 494.0 | 3 153 | 1 292 / 319 / 54 |

- **The band width is the largest choice** (interface −12 % to +41 %), as in X4. W = 15 km is close to `unc` in value (median 12 km) but adds 23 % to the interface, because it lifts many events over the 0.8 line.
- **Mechanisms.** Under R3 as written a mechanism can only exclude, so "both ways" and "only to exclude" are the same rule and the baseline is that rule. Two variants around it: mechanisms not used (interface +4 % at Mw ≥ 4.5, +12 % at Mw ≥ 5.5, where the mechanisms are), and a thrust on the contact made interface with weight 1 wherever the slab top is ≤ 50 km (not in the brief: interface +10 % at Mw ≥ 4.5 and +26 % at Mw ≥ 5.5).
- **Hardening** moves few totals but decides how many events are split (3 111 to 6 688).
- Events of Mw ≥ 7 whose weights move by 0.2 or more under a variant: `merged/review/class_m7_sensitive_2026-11-13f.csv` (35; 26 of them only under W = 20 km or the thrust variant).

## 8. Jujuy nest

`merged/class_nest_2026-11-13f.csv`, `figs/classify/nest.png`. Limits unchanged (within 0.8° of 66.9° W, 24.0° S, 170–320 km, measured depth): 905 events, 55 of Mw ≥ 5.5, 3 of Mw ≥ 7.

- **The circle encloses the cluster:** median epicentre 66.89° W, 24.05° S; 95 % of the events within 0.65°; the density falls from 300 events per 1 000 km² at the centre to 4 at the edge, the level of the surrounding slab.
- **The lower limit is generous:** nothing below 260 km (98 % above 234 km).
- **The upper limit cuts the cluster:** 149 events (3 of Mw ≥ 5.5) lie inside the circle at 150–170 km and are intermediate in-slab; the depth histogram is continuous through 170 km. A limit at 150 km would take them in. Not changed.
- A second, looser band of events at the same depths runs north-east of the circle (22–23.5° S); it is intermediate in-slab.

## 9. Figures

`figs/classify/`: `band.png` (check 1), `maps.png` (one panel per family, split events in their own panel), `sections.png` (20°, 23°, 27°, 31°, 33.5°, 37° S; Slab2 top with ± `unc` and the plate bottom; drawn with pituPLOTS 0.1.0.dev0), `sensitivity.png`, `nest.png`. Class colours and display names: `palette.CLASS`.

## 10. Checks

Weights add to 1 for every event and every event has a row (asserted in `classify_check.py` and tested on random input). `pytest` from `psha_chile8/`: 146 tests pass, 20 of them in `tests/test_classify.py`.

## 11. The depth σ, revisited (asked by Pablo after the first report)

`merged/class_sigma_2026-11-13f.csv`, `class_sigma_variants_2026-11-13f.csv`; `sigma_check()` in `classify_check.py`. Nothing in `locate.py` or in the catalogue was changed.

**Where the σ comes from (A4).** Per depth source and depth range, the spread against GCCEL (X3) or between catalogues (X1); then at least 5 km; then at least 10 km for events more than 20 km offshore; 20 km before 1964. Of the 5 438 events with a depth over the shallow slab, 2 719 are offshore and 1 820 of those sit exactly on the 10 km floor; Potin's 10.4 km offshore is its own tabled value for depths above 30 km, not the floor.

**Measured.** Scatter (robust sd) of the thrusts on the contact about the Slab2 surface. It holds the depth error, the error of Slab2 and thrusts that are not on the contact, so it is an upper bound of σ.

| | depth source | thrust events | median d | scatter | σ in the catalogue | σ without the offshore floor | within ± σ |
|---|---|---|---|---|---|---|---|
| offshore | all | 577 | +2.1 | 8.9 | 10.0 | 6.1 | 71 % |
| | ISC-EHB L1 | 95 | +5.4 | 5.6 | 10.0 | 5.0 | 87 % |
| | Potin | 243 | −0.2 | 7.1 | 10.4 | 10.4 | 77 % |
| | GCCEL | 62 | +6.4 | 7.8 | 10.0 | 5.0 | 90 % |
| | CSN web | 48 | +10.9 | 7.8 | 10.0 | 6.1 | 77 % |
| | ISC-EHB L2 | 63 | +1.2 | 9.3 | 10.0 | 5.0 | 71 % |
| | ISC | 43 | −1.2 | 11.7 | 10.0 | 6.8 | 63 % |
| onshore | all | 397 | +2.2 | 6.8 | 5.0 | 5.0 | 61 % |
| | ISC-EHB L1 | 83 | +0.2 | 5.6 | 5.0 | 5.0 | 59 % |
| | Potin | 196 | +2.0 | 6.4 | 5.0 | 5.0 | 67 % |
| | CSN web | 48 | +7.4 | 5.3 | 6.1 | 6.1 | 77 % |
| | ISC | 23 | −4.8 | 10.6 | 6.8 | 6.8 | 43 % |
| | ISC-EHB L2 | 16 | +8.3 | 12.0 | 5.6 | 5.6 | 31 % |

- **Offshore the 10 km floor is too large for the good depths:** ISC-EHB L1 scatters 5.6 km, the same as onshore, and 87 % of its events are within ± σ (68 % expected). Potin's 10.4 km is also too large (7.1 km measured).
- **It is about right for ISC-EHB L2 and too small for ISC** (9.3 and 11.7 km), offshore and onshore. ComCat (26 events, both sides) scatters 14.5 km.
- **Onshore the σ of 5 km is slightly small** (scatter 6.8 km), or it is right and the rest is Slab2.
- **Bias, not scatter, for two sources:** CSN web depths are 7–11 km below the surface and GCCEL offshore 6 km below. A σ does not describe that.
- GCCEL's σ without the floor is 5 km here because `classify.py` applies its own minimum of 5 km (A4 gives 3 km).

**The classification under other σ.**

| depth σ | hardening | interface | in-slab | crustal | split events | thrusts: interface 1 / split / other |
|---|---|---|---|---|---|---|
| catalogue (baseline) | 0.8 | 3 671.8 | 8 548.8 | 1 545.4 | 4 445 | 249 / 660 / 65 |
| | 0.7 | 3 913.4 | 8 447.4 | 1 405.2 | 3 111 | 492 / 389 / 93 |
| no offshore floor | 0.8 | 3 829.4 | 8 474.5 | 1 462.1 | 3 695 | 407 / 484 / 83 |
| | 0.7 | 3 991.5 | 8 400.9 | 1 373.7 | 2 722 | 568 / 288 / 118 |
| offshore floor 7.5 km | 0.8 | 3 794.2 | 8 488.2 | 1 483.5 | 3 962 | 348 / 552 / 74 |
| | 0.7 | 3 978.8 | 8 407.0 | 1 380.2 | 2 860 | 547 / 325 / 102 |
| σ = scatter of the group | 0.8 | 3 864.0 | 8 425.6 | 1 476.4 | 3 729 | 449 / 447 / 78 |
| | 0.7 | 4 006.8 | 8 360.2 | 1 399.0 | 2 812 | 598 / 276 / 100 |

The thrust counts here include the events with a literature class (974 thrusts over the shallow slab with a depth). "σ = scatter of the group" sets σ to the measured value of the event's depth source and offshore flag; it is not independent, because the same events are then classified, and it is shown for scale only.

**What it says.**
1. **σ is a partial lever.** The best-supported change (no offshore floor, or σ from the scatter) takes the split events from 4 445 to about 3 700 and the interface total up by 4–5 %. A quarter of the catalogue stays split.
2. **The rest is the design, not an input error.** The band edges at ± 12 km lie inside the distribution of the interface events themselves (scatter 7–9 km) and next to the shallow in-slab and forearc events. Any event within about 0.84 σ of an edge is split at hardening 0.8, whatever σ is. With σ smaller, more thrust events also become wrong with weight 1 (65 → 83) instead of split.
3. **Hardening at 0.7 does as much as any σ** (3 111 split), and the two together reach about 2 700–2 800.
4. **A σ per source cannot be read off this table for A4**, because the scatter includes Slab2. What it supports: the offshore floor should not apply to ISC-EHB L1 (and probably GCCEL) depths, which is what "depth-phase and calibrated depths first offshore" in A4 already assumes; and ISC and ComCat depths deserve more than 5–7 km.

**Conflict with DECISIONS, so not changed here:** "σ at least 5 km, 10 km offshore, 20 km before 1964 (13 Nov)". Options for Pablo: (a) keep σ and accept the split share; (b) drop the offshore floor for ISC-EHB L1 and GCCEL only (one line in `locate.py`, a rerun of `locate.py` and `classify.py`); (c) drop it for all sources; (d) keep σ and harden at 0.7. I would take (b) and decide on the hardening separately: (b) is the part the data support source by source, and it does not pretend to fix what is a property of a hard band in a continuous distribution.

## 12. Run `2026-11-13i`: the mechanism decides where there is one (13 Nov)

**Withdrawn.** The replacement of the depth σ by the scatter of the thrust events (runs `2026-11-13g`, `h`) is rolled back: `locate.py` is as in run `e`, the files of `g` and `h` are deleted. It cut the split events by a ninth, raised σ onshore and made new errors.

**What the data can check** (`merged/class_blind_2026-11-13i.csv`, `blind()` in `classify_check.py`). 1 270 events over the shallow slab have a measured depth and a mechanism: 974 thrusts on the plate contact, 296 others. Classified by depth alone, without their mechanism:

| band, hardening | interface weight of the thrusts | of the others | summed weight / thrusts | Brier score |
|---|---|---|---|---|
| Slab2 uncertainty, 0.8 (the rule) | 0.68 | 0.40 | 0.80 | 0.205 |
| Slab2 uncertainty, none | 0.67 | 0.41 | 0.79 | 0.196 |
| 10 km, 0.8 | 0.61 | 0.35 | 0.72 | 0.228 |
| 15 km, 0.8 | 0.84 | 0.53 | 1.00 | 0.173 |
| 20 km, 0.8 | 0.93 | 0.68 | 1.14 | 0.177 |
| every event given the share of thrusts (0.77) | | | 1.00 | 0.179 |

- **Depth separates the interface poorly.** No band and no σ does clearly better than giving every event the same weight (Brier 0.179); the rule of run `f` does worse (0.205). The area under the ROC curve of |d| is 0.73. A model fitted on d itself (cross-validated) reaches 0.152. The tabled σ and the 6.6 / 8.5 km σ give 0.20–0.21: σ was never the lever.
- **The rule of run `f` under-counts the interface by 20 %** among these events, by 34 % offshore and 37 % where the slab top is above 20 km; onshore it is unbiased (0.99).
- **Mechanisms agree with the literature in 28 of 29 events** that have both (14 of 14 interface events are thrusts on the contact; 13 of 13 in-slab, crustal and outer-rise events with another mechanism). The exception is the Iquique foreshock of 2014-03-16 (crustal in the paper, thrust on the contact).
- **Mechanisms cover the events that matter:** from 1976, 49 % of the events over the shallow slab at Mw 5.0–5.5, 74 % at 5.5–6.0, 79 % at 6.0–6.5, 87 % above; 4 % below Mw 5.

**Rule now (`MECH = "add"`, rule name `thrust`).** A thrust on the plate contact over a slab top ≤ 50 km is interface with weight 1, with or without depth; any other mechanism rules the interface out (as before); no mechanism: depth and its error, as before. Band, σ and the 0.8 are unchanged. 959 events take the new rule; 58 of them are more than 20 km from the surface (33 with Potin depths).

**Counts** (Mw ≥ 4.5 in the domain; before = run `f`).

| | before | now | Mw ≥ 5.5 before | now | Mw ≥ 7 before | now |
|---|---|---|---|---|---|---|
| interface | 3 671.8 | 4 056.0 | 608.8 | 768.3 | 62.7 | 71.6 |
| in-slab | 8 548.8 | 8 293.4 | 961.9 | 860.8 | 71.6 | 67.3 |
| crustal | 1 545.4 | 1 416.6 | 279.4 | 220.9 | 20.7 | 16.1 |
| outer rise | 509 | 509 | 93 | 93 | 8 | 8 |
| unclassified | 4 | 4 | 0 | 0 | 0 | 0 |
| split events | 4 445 | 3 785 | 772 | 519 | 67 | 62 |
| – near the band | 3 153 | 2 493 | 453 | 200 | 13 | 8 |
| – no depth | 1 292 | 1 292 | 319 | 319 | 54 | 54 |

Sub-classes now: interface 3 914.0 Nazca and 142 Antarctic; in-slab 1 850.9 shallow, 5 537.4 intermediate, 905 Jujuy nest; crustal 808.4 forearc, 221.6 arc, 309.6 backarc, 77 Patagonia.

**Where the split events are.** From 1976 the share of split events is 25 % at Mw ≥ 4.5, 18 % at ≥ 5.0, 13 % at ≥ 5.5, 12 % at ≥ 6.0 and none at ≥ 7. The split events are the small ones without a mechanism and the old ones without a depth, which is where the information is missing.

**Literature events, rules alone:** right 38 (30 before), no depth 18, split 4 (Concepción 1960, Valdivia 1960, Taltal 1966, Pichilemu 2010 14:55), wrong 3 (Copiapó 1918: epicentre west of the trench; La Ligua 1971: slab top 55.6 km; Iquique foreshock 2014: thrust on the contact, crustal in the paper). Maule 2010, Iquique 2014 and Valparaíso 1985 are interface with weight 1.

**Mw ≥ 7:** 62 not at weight 1: 54 without depth (all before 1941) and 8 near the band, all of 1940–1965 and without a mechanism (1940-10-04, 1946-08-02, 1953-05-06, 1960-06-20 twice, 1960-12-02, 1962-02-14, 1965-02-23).

**Thrusts of Mw ≥ 6.5 not interface:** 3, down from 12: 1987-08-13 and 1993-07-11 (slab top over 50 km) and the Iquique foreshock (literature). The Illapel 2015 aftershocks with Potin depths of 0–5 km are interface.

**Sensitivity now** (`merged/class_sensitivity_2026-11-13i.csv`).

| setting | interface | in-slab | crustal | interface, Mw ≥ 5.5 | split events |
|---|---|---|---|---|---|
| baseline | 4 056.0 | 8 293.4 | 1 416.6 | 768.3 | 3 785 |
| W = 10 km | 3 706.8 | 8 514.0 | 1 545.2 | 740.5 | 3 919 |
| W = 15 km | 4 702.9 | 7 913.3 | 1 149.8 | 809.0 | 2 817 |
| W = 20 km | 5 244.2 | 7 535.8 | 986.0 | 847.6 | 2 331 |
| hardening 0.7 | 4 233.7 | 8 221.9 | 1 310.5 | 778.8 | 2 722 |
| no hardening | 4 047.6 | 8 284.7 | 1 433.8 | 766.0 | 5 732 |
| interface to a slab top of 60 km | 4 230.0 | 8 161.7 | 1 374.3 | 790.1 | 3 831 |
| mechanisms only exclude (run `f`) | 3 671.8 | 8 548.8 | 1 545.4 | 608.8 | 4 445 |
| mechanisms not used | 3 822.6 | 8 452.9 | 1 490.4 | 678.9 | 4 517 |

At Mw ≥ 5.5 the band width now moves the interface total by −4 to +10 % (it was −10 to +33 %), because most of those events are decided by their mechanism.

**Open: the band for events without a mechanism.** The blind test says the Slab2 uncertainty as band gives the interface 20 % too little weight in total and 15 km gives it right (0.95 offshore, 1.09 onshore), with the same result below and above Mw 5.5. The test events are the ones with mechanisms, which are larger than the events the band is then used for. Not changed.

## 13. Run `2026-11-13j`: band of 15 km (Pablo, 13 Nov)

**Change.** `W = 15.0` in `classify.py` in place of the Slab2 depth uncertainty. Reason: on the 1 270 events whose mechanism tells the class, the depth rule with a 15 km band gives the right interface total (summed weight over thrusts 1.00; 0.95 offshore, 1.09 onshore; 1.00 below and above Mw 5.5) and the Slab2 uncertainty 20 % too little (section 12). The band acts on the events without a mechanism; the test events are larger than those, which is the limit of the evidence. Mechanism rule, σ and 0.8 unchanged.

**Counts** (Mw ≥ 4.5 in the domain; `merged/class_counts_2026-11-13j.csv`).

| | run `f` | run `i` | now | now, Mw ≥ 5.5 | now, Mw ≥ 7 |
|---|---|---|---|---|---|
| interface | 3 671.8 | 4 056.0 | 4 702.9 | 809.0 | 73.3 |
| – Nazca / Antarctic | | | 4 560.9 / 142 | 783.0 / 26 | 72.3 / 1 |
| in-slab | 8 548.8 | 8 293.4 | 7 913.3 | 831.9 | 66.2 |
| – shallow / intermediate / Jujuy nest | | | 1 470.8 / 5 537.4 / 905 | 200.2 / 576.7 / 55 | 14.9 / 48.3 / 3 |
| crustal | 1 545.4 | 1 416.6 | 1 149.8 | 209.1 | 15.5 |
| – forearc / arc / backarc / Patagonia | | | 541.6 / 221.6 / 309.6 / 77 | 93.2 / 31.8 / 61 / 23 | 7.1 / 2.5 / 2.9 / 3 |
| outer rise | 509 | 509 | 509 | 93 | 8 |
| unclassified | 4 | 4 | 4 | 0 | 0 |
| split events | 4 445 | 3 785 | 2 817 | 477 | 62 |
| – near the band | 3 153 | 2 493 | 1 525 | 158 | 8 |
| – no depth | 1 292 | 1 292 | 1 292 | 319 | 54 |

- The forearc crust loses the most (937 → 808 → 542): events a few km above the surface are now inside the band.
- From 1976 the share of split events is 17 % at Mw ≥ 4.5, 15 % at ≥ 5.0, 11 % at ≥ 5.5, 10 % at ≥ 6.0, none at ≥ 7.
- The shares for events without depth moved with it: over the shallow slab the interface share is now 0.50–0.84 by bin (about 0.4–0.6 in run `f`). Bins that borrowed: the same two.

**Literature events, rules alone:** unchanged from run `i`: right 38, no depth 18, split 4 (Concepción 1960 0.52 / 0.06 / 0.41, Valdivia 1960 0.50 / 0.08 / 0.42, Taltal 1966 0.78 / 0 / 0.22, Pichilemu 2010 14:55 0 / 0.58 / 0.42), wrong 3 (Copiapó 1918, La Ligua 1971, Iquique foreshock 2014).

**Mw ≥ 7:** 62 not at weight 1: 54 without depth and the same 8 of 1940–1965 near the band. 1985-03-04 00:32 Mw 7.4 (11 km below the surface, another mechanism) is in-slab.

**Sensitivity now** (`merged/class_sensitivity_2026-11-13j.csv`).

| setting | interface | in-slab | crustal | interface, Mw ≥ 5.5 | split events |
|---|---|---|---|---|---|
| baseline (15 km) | 4 702.9 | 7 913.3 | 1 149.8 | 809.0 | 2 817 |
| W = Slab2 depth uncertainty | 4 056.0 | 8 293.4 | 1 416.6 | 768.3 | 3 785 |
| W = 10 km | 3 706.8 | 8 514.0 | 1 545.2 | 740.5 | 3 919 |
| W = 20 km | 5 244.2 | 7 535.8 | 986.0 | 847.6 | 2 331 |
| hardening 0.7 | 4 780.1 | 7 876.8 | 1 109.1 | 810.9 | 2 188 |
| hardening 0.9 | 4 557.1 | 7 987.2 | 1 221.7 | 800.7 | 4 098 |
| no hardening | 4 530.1 | 8 001.6 | 1 234.3 | 797.9 | 5 734 |
| interface to a slab top of 60 km | 4 867.5 | 7 788.8 | 1 109.7 | 829.8 | 2 863 |
| mechanisms only exclude | 4 518.8 | 8 053.1 | 1 194.1 | 726.3 | 3 117 |
| mechanisms not used | 4 723.9 | 7 917.9 | 1 124.3 | 825.1 | 3 161 |

- **The band is still the largest choice at Mw ≥ 4.5** (−21 % to +12 % on the interface) and a small one at Mw ≥ 5.5 (−8 % to +5 %).
- **Hardening now matters more than before:** 0.8 against none is +3.8 % on the interface (it was −0.5 % with the narrow band), because with 15 km more events sit just above the line and are rounded up.
- With the band at 15 km the mechanism adds little to the totals at Mw ≥ 4.5 (4 702.9 against 4 723.9 without mechanisms): the depth rule and the mechanisms now agree in total, which is what the band was set for.

**Figures** in `figs/classify/` are of this run; the sections and the band figure draw the 15 km band.

## References

- Hayes, G.P., Moore, G.L., Portner, D.E., Hearne, M., Flamme, H., Furtney, M., Smoczyk, G.M. (2018). Slab2, a comprehensive subduction zone geometry model. Science 362, 58–61. Slab2 and its depth uncertainty grid. The paper and the data release were not re-read in this session.
- Ruiz, S., Madariaga, R. (2018). Historical and recent large megathrust earthquakes in Chile. Tectonophysics 733, 37–56. Class of the named events, through `overrides_A6.csv`.
