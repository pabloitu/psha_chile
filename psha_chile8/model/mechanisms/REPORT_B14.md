# B14: nodal planes per class from the catalogue mechanisms

Current table `npd_2026-11-16d.csv` (16 Nov): catalogue `catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv` (Scotia rule and crustal sub-class `outside`), completeness table `fits/tables/table_2026-11-16e.csv`. Code `npd.py` (settings at the top), tests `tests/test_npd.py`. Tables `tables/counts_`, `shares_`, `dropped_`, `moved_2026-11-16d.csv` (moves against `npd_2026-11-16c.csv`); figure `figs/ternary.png` (copy `figs/ternary_2026-11-16d.png`; stars mark the fault mechanisms). S3 and S5 read only `npd_2026-11-16d.csv`.

`npd_2026-11-16d.csv` equals `npd_2026-11-16c.csv` except for the backarc and Patagonia. Pablo, 16 Nov: a class below 15 weighted mechanisms is not pooled. It takes the mechanism of its dominant fault system, from the fault traces. Backarc: Precordillera thrust 10/40/90 and 190/50/90. Patagonia: Magallanes–Fagnano 110/90/0 and 20/90/180. Weight 0.5 per plane in both. The comparison with the classes' own mechanisms is in the last section. The run `2026-11-16c` (backarc and Patagonia pooled) is kept with its tables.

## Method

- The catalogue's chosen mechanism (GCMT, then ComCat), Mw ≥ 4.5 in the domain; nodal planes as listed (`strike1..rake2`).
- Events inside the completeness table (5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500), counted with their class weight. Every mechanism inside is from 1976 on, so the crustal "1976 on" rule changes nothing here. Crustal events of sub-class `outside` and Scotia–Antarctic events (outer rise) are in no class, as in the fits `2026-11-16e`.
- Types from the plunges of P, T and B (Frohlich 1992): reverse if T > 50°, strike-slip if B > 60°, normal if P > 60°; otherwise oblique, typed by the largest plunge.
- Representative plane per class and type: each event keeps the nodal plane closer to the type's mean double couple (from the mean P and T axes). On those planes: axial circular mean strike on the side dipping in the mean dip direction, weighted median dip, weighted median rake. The second row is the auxiliary plane; each plane has half the type's weight.
- Types below 10 % dropped and the rest renormalised; type weights to 0.01; angles to 5°.
- Below 15 weighted mechanisms a class is not pooled: it takes the mechanism of its dominant fault system (`FAULT` in `npd.py`; last section).

## Counts

| class | with a mechanism | inside completeness | weighted (inside) | of it oblique (weight) | source of the table rows |
|---|---|---|---|---|---|
| in-slab, shallow | 452 | 387 | 283.1 | 93.0 | own |
| in-slab, intermediate | 931 | 809 | 803.4 | 430.8 | own |
| Jujuy nest | 130 | 106 | 106.0 | 50.0 | own |
| crustal, forearc | 279 | 224 | 104.3 | 27.0 | own |
| crustal, arc | 47 | 41 | 39.5 | 11.5 | own |
| crustal, backarc | 11 | 8 | 8.0 | 1.0 | fault (Precordillera) |
| crustal, Patagonia | 11 | 7 | 7.0 | 4.0 | fault (Magallanes–Fagnano) |

Oblique: 621 of the 1 395 distinct events inside completeness (45 %).

## Type shares (weighted, inside completeness)

| class | normal | reverse | strike-slip | north of 30° S (weight; N / R / SS) | south of 30° S (weight; N / R / SS) |
|---|---|---|---|---|---|
| in-slab, shallow | 0.38 | 0.52 | 0.11 | 156.9; 0.41 / 0.46 / 0.13 | 126.2; 0.33 / 0.59 / 0.08 |
| in-slab, intermediate | 0.75 | 0.10 | 0.15 | 656.3; 0.78 / 0.09 / 0.13 | 147.1; 0.64 / 0.15 / 0.21 |
| Jujuy nest | 0.96 | 0.03 | 0.01 | 106.0; 0.96 / 0.03 / 0.01 | none |
| crustal, forearc | 0.30 | 0.63 | 0.07 | 52.0; 0.23 / 0.69 / 0.09 | 52.3; 0.36 / 0.58 / 0.06 |
| crustal, arc | 0.10 | 0.23 | 0.67 | 10.0; 0.10 / 0.40 / 0.50 | 29.4; 0.10 / 0.17 / 0.73 |
| crustal, backarc (own) | 0.13 | 0.63 | 0.25 | 2.0; 0.50 / 0 / 0.50 | 6.0; 0 / 0.83 / 0.17 |
| crustal, Patagonia (own) | 0.14 | 0.43 | 0.43 | none | 7.0; 0.14 / 0.43 / 0.43 |
| in-slab, all pooled | 0.68 | 0.19 | 0.12 | | |
| crustal, all pooled | 0.23 | 0.52 | 0.25 | | |

North–south: no class split (as on 16 Nov); the backarc halves now hold 2 and 6 events.

## Table (`npd_2026-11-16d.csv`)

| class | type | strike | dip | rake | weight |
|---|---|---|---|---|---|
| in-slab, shallow | normal | 200 | 25 | −80 | 0.190 |
| | | 10 | 65 | −95 | 0.190 |
| | reverse | 0 | 35 | 80 | 0.255 |
| | | 190 | 55 | 95 | 0.255 |
| | strike-slip | 345 | 80 | −30 | 0.055 |
| | | 85 | 60 | −165 | 0.055 |
| in-slab, intermediate | normal | 345 | 70 | −95 | 0.420 |
| | | 180 | 20 | −80 | 0.420 |
| | strike-slip | 230 | 70 | −20 | 0.080 |
| | | 325 | 75 | −160 | 0.080 |
| Jujuy nest | normal | 350 | 70 | −100 | 0.500 |
| | | 200 | 25 | −60 | 0.500 |
| crustal, forearc | normal | 190 | 45 | −85 | 0.160 |
| | | 5 | 45 | −95 | 0.160 |
| | reverse | 0 | 30 | 90 | 0.340 |
| | | 180 | 60 | 90 | 0.340 |
| crustal, arc | normal | 275 | 30 | −35 | 0.050 |
| | | 35 | 70 | −115 | 0.050 |
| | reverse | 185 | 45 | 115 | 0.115 |
| | | 330 | 50 | 65 | 0.115 |
| | strike-slip | 95 | 80 | −5 | 0.335 |
| | | 185 | 85 | −170 | 0.335 |
| crustal, backarc (Precordillera thrust) | reverse | 10 | 40 | 90 | 0.500 |
| | | 190 | 50 | 90 | 0.500 |
| crustal, Patagonia (Magallanes–Fagnano) | strike-slip | 110 | 90 | 0 | 0.500 |
| | | 20 | 90 | 180 | 0.500 |

## Types dropped below 10 % (unrounded share before renormalising)

| class | type | share | weighted events |
|---|---|---|---|
| in-slab, intermediate | reverse | 0.0994 | 79.8 |
| Jujuy nest | reverse | 0.0283 | 3.0 |
| Jujuy nest | strike-slip | 0.0094 | 1.0 |
| crustal, forearc | strike-slip | 0.0741 | 7.7 |

The backarc and Patagonia take a fault mechanism, so no type is dropped there.

## What moved against 2026-11-16 (catalogue 2026-11-16c, before the fault mechanisms)

| class | weighted inside, 16 Nov → 16c | type weights in the table (N / R / SS) | representative planes | Kagan angle |
|---|---|---|---|---|
| in-slab, shallow, intermediate, Jujuy nest | unchanged | unchanged | unchanged | 0° |
| crustal, forearc | 113.4 → 104.3 | 0.32 / 0.68 / 0, unchanged | normal 190/40/−85 → 190/45/−85, reverse 355/30/90 → 0/30/90 (5° steps) | 5° |
| crustal, arc | unchanged | unchanged | unchanged | 0° |
| crustal, backarc | 50.2 → 8.0 | 0 / 0.68 / 0.32 → 0.23 / 0.52 / 0.25 (pooled) | reverse 0/55/90 → 0/35/90; strike-slip 120/75/10 → 100/80/−5; normal enters | 20° (R), 23° (SS) |
| crustal, Patagonia | 18.0 → 7.0 | 0 / 0.24 / 0.76 → 0.23 / 0.52 / 0.25 (pooled) | reverse 15/35/115 → 0/35/90; strike-slip 115/75/0 → 100/80/−5; normal enters | 15° (R), 16° (SS) |

Why the mechanisms left (inside completeness, against the catalogue 2026-11-16):

| class | left | Scotia rule (outer rise) | sub-class `outside` |
|---|---|---|---|
| crustal, Patagonia | 11 events, 11.0 by weight | 11 (10 strike-slip, 1 reverse) | 0 |
| crustal, backarc | 45 events, 42.2 | 0 | 45 (28 reverse, 15 strike-slip, 2 normal) |
| crustal, forearc | 17 events, 9.1 | 0 | 17 (5.4 reverse, 1.7 strike-slip, 2.1 normal by weight) |

- **Patagonia:** all 11 that left went with the Scotia rule: south of Cape Horn at 56.9–57.9° S, 65.4–67.4° W, Mw 5.0–6.2, 1984–2025 (10 strike-slip; the reverse one is 2019-09-05). None left for `outside`; the one Patagonia `outside` event of the catalogue has no mechanism inside completeness. The seven left are at 44.9–51.6° S: three reverse (1992, 2004, 2021, at 50.3–50.6° S, 72° W), three strike-slip (2003, 2016, 2024) and the normal event of 2003-09-12. The class was mainly strike-slip (0.76) because of the Scotia events.
- **Backarc:** 45 of its 53 mechanisms are outside the crustal grid; 8 remain.
- **Forearc:** 17 events, mostly split, are outside the grid; its kept planes move by one 5° step and the strike-slip share falls further, to 0.074.
- Everything else is identical to the table of 16 Nov.

## Against the old fixed planes

| family | old (psha_chile7) | new (2026-11-16c) |
|---|---|---|
| in-slab | 0.5 normal (180/60/−90), 0.5 reverse (0/30/90), every class | shallow N 0.38 / R 0.51 / SS 0.11; intermediate N 0.84 / SS 0.16; Jujuy nest normal only |
| crustal | reverse only, 0/60/90 and 180/60/90, every class | forearc R 0.68 / N 0.32; arc SS 0.67; backarc Precordillera thrust 10/40/90; Patagonia Magallanes–Fagnano 110/90/0 |

## Classes below 15 weighted mechanisms

Backarc (8.0) and Patagonia (7.0): fault mechanisms (last section). Against `npd_2026-11-16c.csv` (pooled), the Kagan angle is 11° for the backarc reverse plane and 15° for the Patagonia strike-slip plane. The pooled normal and second type are gone.

## Backarc and Patagonia: fault mechanism or own mechanisms (16 Nov; Pablo picked the fault mechanism for both)

Pablo, 16 Nov: classes below 15 weighted mechanisms are not pooled. The two options were their own mechanisms as they are (B14 rules, 10 % rule), or one fixed mechanism from the dominant faulting. The fixed one is taken for both, because the own planes rest on one to three events per type. The Patagonia background thus has the Magallanes–Fagnano mechanism, which none of its seven events has (see below). The check is the Kagan angle between each event and the fixed mechanism.

**Fixed mechanisms, from the traces of the fault database (`data/faults/faults_2026-11-15.gpkg`, the crustal-grid fault sources of `model/crustal/tables/fault_sources_2026-11-16e.csv`):**
- Backarc: the 8 Precordillera thrusts inside the grid (La Cantera, Maradona–Acequión, Las Tapias–Villicum, Rinconada, Los Berros, Cerro Salinas, Cerro La Cal, Zonda; 312 km, all reverse). Strike: length-weighted axial mean of the trace segments, 9° (resultant 0.81). Dip: length-weighted median, 37.5° (20–80°). Six faults dip east (193 km) and two dip west (119 km), so the plane is taken east-dipping. Rounded to 5°: **10/40/90**, auxiliary **190/50/90**, weight 0.5 each. No Sierras Pampeanas fault lies inside the grid; those are `outside`.
- Patagonia: the Magallanes–Fagnano main trace (7 segments, 490 km). Strike: length-weighted axial mean, 111° (resultant 0.83; Chilean segments 104–125°, Argentine 80–100°). Vertical and left-lateral (rake 0; the database has −45 on the Chilean segments from GEM "sinistral-normal", MASCSN −5). Rounded: **110/90/0**, auxiliary **20/90/180**, weight 0.5 each.

**Backarc (8 events, 8.0 by weight)**

| option | type | strike | dip | rake | weight |
|---|---|---|---|---|---|
| own | normal | 130 | 50 | −115 | 0.060 |
| | | 345 | 50 | −60 | 0.060 |
| | reverse | 350 | 60 | 85 | 0.315 |
| | | 185 | 30 | 100 | 0.315 |
| | strike-slip | 185 | 60 | 165 | 0.125 |
| | | 280 | 75 | 30 | 0.125 |
| fixed (Precordillera thrust) | reverse | 10 | 40 | 90 | 0.500 |
| | | 190 | 50 | 90 | 0.500 |

Own shares N / R / SS 0.13 / 0.63 / 0.25, nothing dropped. The events:

| date | Mw | lat, lon | type | nodal plane | Kagan to 10/40/90 |
|---|---|---|---|---|---|
| 1985-01-26 | 5.9 | −33.11, −68.61 | reverse | 158/38/65 | 25° |
| 2006-08-05 | 5.6 | −33.12, −68.76 | reverse | 137/39/44 | 38° |
| 2012-01-18 | 5.0 | −31.78, −68.43 | reverse | 215/42/130 | 30° |
| 2015-08-01 | 5.2 | −30.06, −68.36 | reverse | 166/29/102 | 40° |
| 2022-11-05 | 5.1 | −33.42, −68.65 | reverse | 200/47/115 | 20° |
| 2021-01-19 | 6.5 | −31.87, −68.90 | strike-slip (oblique) | 223/61/164 | 62° |
| 1995-11-06 | 5.3 | −19.11, −68.32 | strike-slip | 237/78/8 | 107° |
| 2016-07-23 | 5.0 | −22.38, −67.22 | normal | 346/48/−62 | 89° |

- The five reverse events, all in the Precordillera at 30–33.4° S, are within 20–40° of the fixed thrust. The 2021 San Juan event (Mw 6.5) is typed strike-slip by its plunges, but it is oblique and lies in the same belt.
- The other two are in the Altiplano and Puna backarc (19° and 22° S), far from the Precordillera faults: one strike-slip, one normal. They supply the normal type and half the strike-slip type of the own option.
- Weighted mean Kagan angle to the fixed mechanism: 51°.

**Patagonia (7 events, 7.0 by weight)**

| option | type | strike | dip | rake | weight |
|---|---|---|---|---|---|
| own | normal | 35 | 90 | −90 | 0.070 |
| | | 260 | 5 | −45 | 0.070 |
| | reverse | 25 | 35 | 115 | 0.215 |
| | | 175 | 60 | 75 | 0.215 |
| | strike-slip | 270 | 45 | 10 | 0.215 |
| | | 170 | 85 | 135 | 0.215 |
| fixed (Magallanes–Fagnano) | strike-slip | 110 | 90 | 0 | 0.500 |
| | | 20 | 90 | 180 | 0.500 |

Own shares N / R / SS 0.14 / 0.43 / 0.43, nothing dropped. The events:

| date | Mw | lat, lon | type | nodal plane | Kagan to 110/90/0 |
|---|---|---|---|---|---|
| 1992-07-30 | 5.5 | −50.38, −72.38 | reverse | 31/25/114 | 95° |
| 2004-08-30 | 5.0 | −50.64, −71.93 | reverse | 355/35/73 | 83° |
| 2021-10-13 | 5.5 | −50.28, −72.26 | reverse | 48/53/140 | 66° |
| 2003-10-28 | 5.2 | −51.61, −75.44 | strike-slip (oblique) | 87/56/−180 | 74° |
| 2016-12-05 | 5.2 | −47.18, −75.34 | strike-slip (oblique) | 307/41/−4 | 53° |
| 2024-08-26 | 5.0 | −44.87, −73.92 | strike-slip (oblique) | 235/46/10 | 73° |
| 2003-09-12 | 5.5 | −51.60, −75.65 | normal (oblique) | 253/2/−54 | 90° |

- None of the seven lies on the Magallanes–Fagnano system (52–55° S). The reverse events are in the Patagonian fold-and-thrust belt near 50.3–50.6° S, 72° W; the rest are on the coast at 44.9–51.6° S. Every event is 53–95° from the fault mechanism (weighted mean 76°).
- The own planes rest on 1–3 events per type and are not robust: the normal pair is one event (a 2° dipping plane), the strike-slip pair has a 45° dip, and 4 of the 7 are oblique.
- The Magallanes–Fagnano fault is a fault source of its own (S3), with its own trace and mechanism. The fixed option gives the Patagonia background the same mechanism; the own option describes the background events the catalogue has.
