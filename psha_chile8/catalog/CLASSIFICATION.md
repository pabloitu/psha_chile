# Tectonic classification with class weights (A7)

**Current run: `2026-11-14c`.** Code `classify.py` (rules), `classify_check.py` (checks, figures), `tests/test_classify.py` (25 tests). Input `merged/catalog_2026-11-14b.csv` (the final run of locations and magnitudes; 204 956 events; 14 279 of Mw ≥ 4.5 in the domain, 12 391 of them with a measured depth, 2 671 with a mechanism). Output `merged/classes_2026-11-14c.csv`, `merged/catalog_2026-11-14c.csv`, `merged/class_shares_2026-11-14c.csv` and the `class_*_2026-11-14c.csv` tables.

Run `2026-11-14a` had the same rules on the catalogue of 13 Nov; this run adds two class hints, the Jujuy nest from 150 km and the final magnitudes (1934-03-01 Mw 7.6). A frozen copy is in `frozen/2026-11-14/`. The runs of 13 Nov (`f`, `i`, `j`: depth band about Slab2, a thrust on the contact deciding alone in `i` and `j`) are described in `CLASSIFICATION_2026-11-13.md`; their files are kept. How the rule of this run was chosen is in `explore/X5/REPORT.md`.

Numbers below are events of Mw ≥ 4.5 in the domain unless said otherwise.

## 1. Rules

Each event has five weights (`w_interface`, `w_inslab`, `w_crustal`, `w_outer_rise`, `w_unclassified`) that add to 1, `cls` (the class with weight 1, else `split`), `cls_auto` (the same from the rules alone) and `rule`.

**R1, literature (`hint`, 65 events).** An accepted class hint of `overrides_A6.csv` gives weight 1 (63 from the literature, 2 stated by Pablo on 14 Nov). `cls_auto` and the columns `a_*` keep what the rules give.

**R2, outer rise (`outer_rise`, 506).** West of the Nazca trench (the Antarctic trench south of 46.15° S), with or without depth.

**R3, depth scores over the shallow slab** (slab top ≤ 50 km, measured depth). Scores after Haynie et al. (2026), for a depth z and d = z − slab top:
- interface: 1 where |d| ≤ 15 km, fading linearly to 0 between z = 50 and 65 km;
- crustal: of what is left, 1 at 20 km above the slab top falling to 0 at 20 km below, times 1 down to 40 km depth falling to 0 at the slab top (their Moho grid is replaced by 40 km);
- in-slab: the rest.

The scores are averaged over the depth error of the event: a normal distribution about the catalogue depth with the catalogue σ (at least 5 km), cut at the ground, in 61 quantiles. Haynie et al. use the depth as exact; the averaging is ours.

**R4, mechanism.** The interface mechanism at an epicentre has the Slab2 plane and slips along the plate convergence (upper plate towards 257°) laid on that plane. A double couple with plane normal n and slip s has four equivalent descriptions (a, b): (n, s), (−n, −s), (s, n), (−s, −n). For each, the swing σ is the angle between a and the slab normal, and the twist τ the angle between b and the interface slip after the smallest rotation that takes a onto the slab normal.

    m = min over the four of sqrt((σ / 20°)² + (τ / 45°)²)

With the Kagan angle Φ of the same pair, cos(Φ/2) = cos(σ/2) cos(τ/2): m is the Kagan angle with its two parts scaled apart, strict on the plane and loose on the slip direction.
- m ≤ 1: the interface odds of R3 are multiplied by 3.9 (the share of such mechanisms within 5 km of the slab over their share beyond 15 km, calibrated and depth-phase depths);
- m > 1: interface weight 0; in-slab and crustal share the event as R3 gives them;
- no mechanism: R3 as it is.

A mechanism never gives interface alone. Of 1 270 mechanisms over the shallow slab with a depth, 878 have m ≤ 1.

**R5, deeper slab and no slab (measured depth).** Slab top > 50 km: the depth with its error against the slab surface, above → crustal if the event is not deeper than 50 km, below → in-slab. No slab: crustal to 50 km (`no_slab`, 63), deeper unclassified (`no_slab_deep`, 4).

A weight of 0.8 or more becomes 1 (`depth`, 10 188 events); otherwise the event is split (`depth_split`, 1 736).

**R6, no measured depth.** No slab: crustal (`nodepth_no_slab`, 58). Slab top deeper than 50 km and every rejected depth ≥ 70 km: in-slab (`nodepth_deep`, 225). Otherwise the shares of the classified events of the same bin (slab-top range, latitude band, magnitude range), with R4 applied where there is a mechanism (`nodepth_share`, 1 292), no rounding to 1. Two bins borrowed the other magnitude range (slab top 50–100 km and > 100 km, 38–46° S, Mw ≥ 5.5).

**R7, sub-classes** by position: `sub_interface` (interface, antarctic_interface), `sub_inslab` (intraslab_shallow where the slab top is ≤ 50 km, intraslab_intermediate, jujuy_nest: within 0.8° of 66.9° W, 24.0° S, depth 150–320 km), `sub_crustal` (forearc, arc, backarc, patagonia). A split event carries the sub-class of each family it has weight in.

**R8, assigned depth (17 events).** Literature class, no measured depth, slab at the epicentre: interface on the slab top kept within 10–50 km; in-slab at 0.30 of the Slab2 thickness below the top; σ 20 km. `depth_kind = assigned`; the rules read only `measured`.

**Antarctic interface (`antarctic`, 142).** South of 46.15° S, within 150 km landward of the Antarctic trench, not deeper than 60 km or no depth, no non-thrust mechanism: interface with weight 1.

Settings are at the top of `classify.py`: `SZ, DIFF, MOHO, NQ` (R3), `TOL, AZ, LR, EDGE` (R4), `W`, `IF_TOP`, `HARD`.

## 2. Counts

`merged/class_counts_2026-11-14c.csv`.

| | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 7 |
|---|---|---|---|
| events | 14 279 | 1 943 | 163 |
| interface | 4 497.7 | 763.9 | 71.5 |
| of it Antarctic | 142 | 26 | 1 |
| in-slab | 8 078.9 | 865.3 | 67.4 |
| of it shallow / intermediate / Jujuy nest | 1 636.5 / 5 388.4 / 1 054 | 233.5 / 573.7 / 58 | 16.1 / 48.3 / 3 |
| crustal | 1 189.3 | 220.8 | 16.0 |
| of it forearc / arc / backarc / Patagonia | 581.1 / 221.6 / 309.6 / 77 | 105.0 / 31.8 / 61 / 23 | 7.6 / 2.5 / 2.9 / 3 |
| outer rise | 509 | 93 | 8 |
| unclassified | 4 | 0 | 0 |
| weight 1 | 11 251 | 1 410 | 101 |
| split, with a depth | 1 736 | 214 | 8 |
| split, no depth | 1 292 | 319 | 54 |

Against run `j`: interface 4 702.9 → 4 497.7 (−4 %), in-slab 7 913.3 → 8 078.9, crustal 1 149.8 → 1 189.3; interface at Mw ≥ 5.5 809.0 → 763.9; split events 2 817 → 3 028.

## 3. Events with a literature class

What the rules alone give for the 65 events (`merged/class_named_2026-11-14c.csv`): 36 right, 18 without depth, 9 split, 2 wrong (run `j`, 63 events: 38, 18, 4, 3). Their class in the catalogue is the literature class in every case.

| event | Mw | depth ± σ | slab top | literature | rules alone |
|---|---|---|---|---|---|
| Copiapó 1918 | 7.8 | none | none | interface | outer rise (epicentre west of the trench): wrong |
| La Ligua 1971 | 7.8 | 60.6 ± 5 | 55.6 | interface | in-slab (slab top below 50 km): wrong |
| Concepción 1960 | 8.1 | 11.5 ± 20 | 30.5 | interface | split, interface 0.52 |
| Valdivia 1960 | 9.5 | 25 ± 20 | 39.1 | interface | split, interface 0.49 |
| Taltal 1966 | 7.7 | 20 ± 5 | 31.1 | interface | split, interface 0.79 |
| Valparaíso 1985 | 7.9 | 49.6 ± 5 | 28.4 | interface | split, interface 0.30 (depth 21 km below the slab) |
| Valparaíso 2017 | 6.9 | 37 ± 10 | 19.9 | interface | split, interface 0.73 |
| Pichilemu 2010 (11 Mar) | 7.0 | 22.7 ± 10.4 | 20.7 | crustal | split, in-slab 0.56, crustal 0.44 (m > 1, no interface) |
| Iquique foreshock 2014 | 6.7 | 8.6 ± 10.4 | 22.2 | crustal | split, crustal 0.75 (m 1.25, no interface) |
| 2001-07-07 (hint of 14 Nov) | 7.6 | 24.5 ± 10 | 40.4 | interface | split, interface 0.77 |
| 2015-09-16 23:18 (hint of 14 Nov) | 7.1 | 5.2 ± 10.4 | 29.4 | interface | split, interface 0.58 |

## 4. Events of Mw ≥ 7

`merged/class_m7_2026-11-14c.csv`: 163 events; 101 at weight 1 (41 interface, 44 in-slab, 8 crustal, 8 outer rise), 62 split, of which 54 have no depth (before 1940 nearly all) and 8 have one:

| time | Mw | depth ± σ | slab top | interface | in-slab | crustal |
|---|---|---|---|---|---|---|
| 1940-10-04 | 7.0 | 23.5 ± 20 | 22.0 | 0.62 | 0.28 | 0.10 |
| 1946-08-02 | 7.1 | 39.2 ± 20 | 38.3 | 0.55 | 0.26 | 0.19 |
| 1953-05-06 | 7.5 | 66.0 ± 20 | 41.9 | 0.27 | 0.70 | 0.03 |
| 1960-06-20 02:01 | 7.0 | 25.0 ± 20 | 34.5 | 0.56 | 0.14 | 0.31 |
| 1960-06-20 12:59 | 7.1 | 24.6 ± 20 | 42.6 | 0.43 | 0.07 | 0.50 |
| 1960-12-02 | 7.2 | 14.1 ± 20 | 49.2 | 0.19 | 0.03 | 0.78 |
| 1962-02-14 | 7.1 | 40.6 ± 20 | 43.2 | 0.52 | 0.23 | 0.24 |
| 1965-02-23 | 7.0 | 41.8 ± 5.6 | 29.4 | 0.69 | 0.31 | 0.00 |

2001-07-07 Mw 7.6 and 2015-09-16 23:18 Mw 7.1, thrusts inside the ellipse with depths 16 and 24 km above the slab, were split by the rules (interface 0.77 and 0.58) and are interface by a class hint since 14 Nov. 1985-03-04 00:32 Mw 7.4 has a mechanism outside the ellipse (m 3.0; strike 234, dip 32, rake 155; two hours after the Valparaíso mainshock).

## 5. Sensitivity

`merged/class_sensitivity_2026-11-14c.csv`, `figs/classify/sensitivity.png`.

| variant | interface | in-slab | crustal | interface, Mw ≥ 5.5 | split events |
|---|---|---|---|---|---|
| baseline | 4 497.7 | 8 078.9 | 1 189.3 | 763.9 | 3 028 |
| interface zone ± 10 km | 3 472.7 | 8 698.5 | 1 594.8 | 662.6 | 4 309 |
| interface zone ± 20 km | 5 006.4 | 7 737.4 | 1 022.2 | 813.7 | 2 509 |
| interface zone ± Slab2 uncertainty | 3 809.8 | 8 487.6 | 1 468.6 | 704.4 | 4 124 |
| 0.7 becomes 1 | 4 588.2 | 8 038.3 | 1 139.5 | 769.2 | 2 341 |
| 0.9 becomes 1 | 4 324.7 | 8 172.8 | 1 268.5 | 747.6 | 4 442 |
| weights kept as they are | 4 264.2 | 8 208.2 | 1 293.6 | 731.7 | 6 275 |
| interface down to a slab top of 60 km | 4 586.5 | 8 030.5 | 1 148.9 | 779.4 | 3 110 |
| mechanisms not used | 4 679.8 | 7 970.0 | 1 116.1 | 822.2 | 3 195 |
| rules of run `j` | 4 702.9 | 7 913.3 | 1 149.8 | 809.0 | 2 817 |
| events without depth that take the shares left out | 3 852.9 | 7 570.7 | 1 050.4 | 616.5 | 1 736 |

The width of the interface zone moves the interface total most (−23 % at 10 km, +11 % at 20 km). The mechanism rule moves it by 4 %, the rounding at 0.8 by 5 %.

## 6. Limits

- With the catalogued depth errors no rule classes more than about two thirds of the events over the shallow slab right (synthetic test, `explore/X5`).
- Only 1 270 of the 5 438 events with a depth over the shallow slab have a mechanism; for the rest R3 decides alone.
- The tolerances 20° and 45° are not fitted; they come from the 14 literature interface events with a mechanism (swing up to 12°, twist up to 15°) and the rule of the old classifier. A cluster analysis of the nodal planes after Specht et al. (2017) finds the same interface cluster: 833 of the 878 events with m ≤ 1 are in it (`explore/X5/x5_ace.py`).
- Events with m between 1 and 1.5 (122) lie on the slab nearly as often as those inside; the hard edge at 1 gives them no interface weight (Pablo, 14 Nov).
- The convergence azimuth is one value for the whole margin; ± 5° moves 17–21 events across the edge.
- The Slab2 depth error is not a distribution of its own; it is inside the fixed ± 15 km.
- The odds factor 3.9 rests on 151 and 53 events and on depth as a stand-in for the class.
- `mech_kind` in the tables is still the thrust-on-the-contact test of the runs of 13 Nov (one nodal plane within 35° of the Slab2 plane, rake 45–135°); `mech_m` is m. The band measurement of `classify_check.py` (`class_band_`, `figs/classify/band.png`) uses `mech_kind`.

## 7. Figures and checks

`figs/classify/`: `maps.png` (classes on the map), `sections.png` (six sections with the Slab2 top and the ± 15 km zone), `band.png`, `sensitivity.png`, `nest.png`. Weights add to 1 for every event and every event has a row (asserted in `classify_check.py`). The Jujuy nest has 1 054 events; its upper depth limit was moved from 170 to 150 km on the depth histogram of the cluster (`figs/classify/nest.png`, Pablo, 14 Nov).

## 8. Revision of 16 Nov (A9, run `2026-11-16`)

Sections 2 to 5 give the numbers of run `2026-11-14c`. The run `2026-11-16` (frozen in `catalog/frozen/2026-11-16/`, numbers in its `DECISIONS_NOTE.md`) has three more rules (Pablo, 16 Nov):

- **No depth, before 1900** (`OLD`): over the shallow slab or in the forearc the event takes no crustal share; the share goes to interface and in-slab in proportion. A forearc crustal event large enough for the historical record is rare and its damage local; in-slab events are widely damaging (Chillán 1939, Calama 1950, Punitaqui 1997, Tarapacá 2005) and stay possible. Under the arc and backarc the shares are kept, since large crustal events are real there; the known ones carry hints.
- **Arc class** ends where the arc polygon ends (`arc_end()`, 47.24° S), for events and faults. `SOUTH_LAT` (46.15° S) only chooses the trench.
- **Chile Ridge at the triple junction** (`RIDGE`): between 45.5° S and 46.15° S an event within 75 km east of the trench is outer rise. Of 13 mechanisms there 10 are strike-slip with a plane near N 78° E, 2 normal and 1 oblique; the events west of the trench at the same latitudes have the same mix. 29 events of Mw ≥ 4.5, the largest Mw 5.9; map in `figs/classify/triple_junction.png`.

Effect against `2026-11-14c`, with the 20 new class hints of A6 (Mw ≥ 4.5): interface +5.1, in-slab −3.6, crustal −30.4 (Patagonia 77 → 54, forearc −8), outer rise +30. Events of Mw ≥ 7 still split: 37 of 164 (62 of 163 before). Literature events by the rules alone: 40 right, 34 without a depth, 9 split, 2 wrong (Copiapó 1918, La Ligua 1971, as before).

## References

- Hayes, G.P., Moore, G.L., Portner, D.E., Hearne, M., Flamme, H., Furtney, M., Smoczyk, G.M. (2018). Slab2, a comprehensive subduction zone geometry model. Science 362, 58–61. The paper and the data release were not re-read.
- Haynie, K.L., Thompson, E.M., Hearne, M., Hayes, G.P., Shelly, D.R., Shumway, A.M., Llenos, A.L., Michael, A.J., Powers, P.M. (2026). Subduction zone earthquake catalog separation tool: implementation in the USGS 2025 Puerto Rico and U.S. Virgin Islands National Seismic Hazard Model. Seismological Research Letters 97(2A). doi:10.1785/0220250078. The depth scores of R3.
- Kagan, Y.Y. (1991). 3-D rotation of double-couple earthquake sources. Geophysical Journal International 106, 709–716. The rotation angle between double couples. Not re-read; cited as in `explore/X5`.
- Ruiz, S., Madariaga, R. (2018). Historical and recent large megathrust earthquakes in Chile. Tectonophysics 733, 37–56. Class of the named events, through `overrides_A6.csv`.
- Specht, S., Heidbach, O., Cotton, F., Zang, A. (2017). Data-driven earthquake focal mechanism cluster analysis. GFZ Scientific Technical Report STR17/01. doi:10.2312/GFZ.b103-17012. Clusters of nodal planes; used as a check only.
