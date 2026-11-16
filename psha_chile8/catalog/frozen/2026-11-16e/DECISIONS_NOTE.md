# Frozen catalogue of 16 Nov 2026, run e: decisions note

Chain run after the revision A9, on one set of depths: locations and magnitudes `2026-11-16d`, classes `2026-11-16e`. It replaces the frozen catalogues of 14 Nov and of 16 Nov (`catalog/frozen/2026-11-14/`, `2026-11-16/`, `2026-11-16b/` and `2026-11-16c/`, kept as they were). Against `2026-11-16`: the Scotia–Antarctic boundary events are outer rise (run b), and the crustal events outside the crustal grid have the sub-class `outside` (run c); no weight, position, depth or magnitude differs between b and c; run e moves two epicentres to ISC-GEM (A6) and changes nothing else. The catalogue is `catalog_2026-11-16e.csv` (one row per earthquake, 204 956 events, 1513 to 2026). Checksums in `SHA256SUMS` (inputs of the matching step in `INPUTS_SHA256`); the code that made it is in `code/`. Method notes: `catalog/REPORT_A3-A5.md`, `MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md`, `CLASSIFICATION.md`; every decision with its date in `DECISIONS.md`.

## Rules

**Sources and matching.** Ruiz and Madariaga (2018) for the large events; Cabello et al. (2025) before 1904 only; Centennial, ISC-GEM, ISC, ISC-EHB, GCCEL, GCMT, USGS ComCat, Potin et al. (2024, to July 2020) and CSN. Events are matched across catalogues once and carry one identifier.

**Epicentre.** A local catalogue (Potin, CSN) comes first only inside its own network (18–46° S, west of the arc, from 1982); elsewhere and before 1982 the global catalogues come first (GCCEL, ISC-EHB, ISC, ComCat). A local record more than 50 km from every global record of the event is not used.

**Depth.** The first measured depth in the same order, with GCCEL and ISC-EHB before the local catalogue offshore. Fixed depths, agency defaults, ISC-EHB level 3 and the GCMT centroid are not measured depths. An event with none left has an unknown depth; it is not filled in. Where the literature states the class of such an event, a depth is assigned from the class and Slab2 and flagged (31 events).

**Magnitude.** One Mw per event. From 1976: GCMT from Mw 5.4; W-phase and regional moment magnitudes; GCMT below 5.4, lowered slightly; the CSN moment magnitude of the ISC Bulletin only if there is no other; Ruiz and Madariaga; else a magnitude converted with relations fitted on Chilean pairs (surface-wave scales for shallow events only). Before 1976: Ruiz and Madariaga, a Centennial Mw, an ISC-GEM direct Mw, a Centennial Ms or mB converted, an ISC-GEM proxy Mw, Cabello. Depth-dependent conversions use the final depths.

**Large events.** Reviewed one by one; a value is corrected only from a source that was read, in `overrides_A6.csv` (104 accepted rows: 85 class hints, 7 Mw, 5 depths, 4 longitudes, 3 latitudes).

**Class.** Each event has weights for interface, in-slab, crustal and outer rise that add to 1. A class hint comes first. West of the trench is outer rise, and so are the Chile Ridge fracture-zone events within 75 km east of the trench between 45.5° S and 46.15° S (strike-slip and normal mechanisms; left out of the source model). An event without a slab whose nearest boundary is the Scotia–Antarctic one of PB2002 (Bird 2003), nearer than the Antarctic–South America trench and the Magallanes–Fagnano traces, is outer rise too: that boundary has no source in the model. Over the shallow slab (Slab2 top ≤ 50 km) the depth gives scores after Haynie et al. (2026), interface within ± 15 km of the slab surface, averaged over the depth error of the event. A mechanism is compared with the interface mechanism (the Slab2 plane slipping in the convergence direction) by one misfit, strict on the plane (20°) and loose on the slip direction (45°): inside, the interface odds are raised by 3.9; outside, no interface weight. A mechanism never decides alone. A weight of 0.8 or more becomes 1. An event without a measured depth takes the class shares of the classified events since 1976 of its bin, unless its position decides; before 1900, over the shallow slab or in the forearc, it takes no crustal share. The arc class ends where the arc polygon ends (47.24° S). Sub-classes by position; a crustal event outside the crustal grid of the source model (`data/crustal_grid_01_2026-11-15.csv`, 0.1° cells) keeps its crustal weight and takes the sub-class `outside`, which no fit, pattern or source reads, so that rate, pattern and sources cover the same region; the Jujuy nest (within 0.8° of 66.9° W, 24.0° S, 150–320 km) is a class of its own.

## Numbers (Mw ≥ 4.5 in the domain)

| | events or weight |
|---|---|
| events | 14 279 (1 943 of Mw ≥ 5.5, 164 of Mw ≥ 7) |
| depth measured / unknown / assigned | 12 395 / 1 853 / 31 |
| with a mechanism | 2 671 |
| Mw measured / converted / ISC-GEM / Centennial / Cabello / Ruiz and Madariaga / A6 | 4 296 / 9 177 / 542 / 126 / 104 / 27 / 7 |
| interface (of it Antarctic) | 4 502.8 (142) |
| in-slab: shallow / intermediate / Jujuy nest | 1 631.7 / 5 389.6 / 1 054 |
| crustal: forearc / arc / backarc / Patagonia / outside the grid | 541.9 / 221.1 / 87.1 / 40 / 255.7 |
| outer rise / unclassified | 552 / 3 |
| one class (weight 1) | 11 299 |
| split with a depth / split without a depth | 1 733 / 1 247 |

Against the frozen catalogue of 14 Nov: the same events; two magnitudes (1939-04-18, Mw 7.3 → 7.6, and 1942-07-08, 6.9 → 7.1, converted at their A6 depths of 100 and 140 km); one epicentre (1919-03-02 Mw 7.2, to the ISC-GEM position at 43.8° S 78.3° W, now outer rise); four A6 depths (1929, 1936, 1939, 1942) and 14 more assigned depths; 20 more class hints. Classes: interface +5.1, in-slab −3.6, crustal −43.4 (Patagonia −36, forearc −8), outer rise +43. Aysén 1960-06-06 stays at Mw 7.7 (Pablo, 16 Nov).

## Open points

- **Events without a measured depth (1 853):** 91 before 1900, 263 in 1900–1963, 548 in 1964–1981, 951 from 1982; 413 of Mw ≥ 5.5 and 57 of Mw ≥ 7. By position or hint 583 have one class (outer rise 205, deep slab 225, Antarctic interface 97, no slab 49, class hint 7); 1 270 take the bin shares (interface 638, in-slab 502, crustal 130), 23 of them with one class by the pre-1900 rule. Crustal weight left in them at Mw ≥ 7: forearc 0.9 (12 events of 1904–1940), arc and backarc none; at Mw ≥ 6: forearc 14.0, arc 2.7, backarc 4.6. They count in the rates by their weights and cannot enter a depth model. The fits are to be run with and without them (DECISIONS).
- **Width of the interface zone:** the largest choice. ± 10 km gives 23 % less interface, ± 20 km 11 % more; the mechanism rule moves it by 4 %.
- **Mechanism tolerances** (20°, 45°) are chosen, not fitted; one convergence azimuth (257°) for the whole margin; the hard edge leaves 122 events just outside without interface weight.
- **With the catalogued depth errors** no rule classes more than about two thirds of the events over the shallow slab correctly (synthetic test, `explore/X5`).
- **Large events left as they are** (converted Centennial values above the ISC-GEM proxies): 1918-05-20, 1925-05-15, 1948-05-11, 1971-06-17; a sensitivity case for the in-slab Mmax.
- **Mw ≥ 7 still split:** 37 of 164 (62 before), 8 with a depth (1940–1965, depth errors of 20 km in seven) and 29 without.
- **LOFS epicentres (A6, 16 Nov):** Aysén 1960-06-06 Mw 7.7 and 1927-11-21 Mw 7.1 take the ISC-GEM epicentre (45.748 S 72.919 W, quality A; 44.861 S 72.686 W, quality B) instead of the Centennial one, 41 km and about 90 km west of it. Both stay crustal arc; Mw and the arc Mmax (7.9) are unchanged. Nearest LOFS traces: Riesco–Mañihuales (006tt) 5 km and Fiordo Aysén–Puerto Cisnes (006qq) 6 km. Their depth stays unknown.
- **Outside the crustal grid:** 429 events (311 backarc in Argentina and Bolivia, 117 forearc of which 116 north of 17.2° S in southern Peru, 1 Patagonia). In the crustal table (Mw 5.0 from 1976): backarc 133.5 → 22.8, forearc 209.0 → 191.7, arc and Patagonia unchanged. Caucete 1977 (Mw 7.5) is among them; the class maxima are unchanged (forearc 7.0, arc 7.7, backarc 7.5 from 1894, Patagonia 7.8). The classes now depend on the grid file: if the grid changes, they are rerun. The bin shares of the no-depth rule still use these events.
- **Scotia–Antarctic boundary:** 13 strike-slip events of Mw 4.8–6.2 at 56.6–57.9° S left crustal Patagonia (22 → 11 events of Mw ≥ 5 since 1976); the Patagonia Mmax is unchanged (1949, Mw 7.8). The 101 Antarctic-interface events south of 52.07° S lie on the same boundary; they feed no rate (the Antarctic interface is geodetic only).
- **South of 46.15° S** the events along the coast are Antarctic interface by position (1960-06-02 Mw 6.6, 1963-05-19 Mw 6.4, 2024-11-08 Mw 6.3); their mechanisms were not checked.
- **1926-04-28 Mw 7.3** is in-slab on agency depths alone (no paper; Pablo, 16 Nov).
- **Rules alone against the literature:** Copiapó 1918 (epicentre west of the trench) and La Ligua 1971 (slab top at 56 km) get another class from the rules; both carry the literature class.
- **Not re-read before citing:** Kanamori and Rivera (2017), Astiz (1987) and the web tables used for 1878 and 2025 were opened by a sub-agent only.
