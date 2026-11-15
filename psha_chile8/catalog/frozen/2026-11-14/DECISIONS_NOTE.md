# Frozen catalogue of 14 Nov 2026: decisions note

Final chain run on one set of depths: locations and magnitudes `2026-11-14b`, classes `2026-11-14c`. The catalogue is `catalog_2026-11-14c.csv` (one row per earthquake, 204 956 events, 1513 to 2026). Checksums in `SHA256SUMS` (inputs of the matching step in `INPUTS_SHA256`); the code that made it is in `code/`. Method notes: `catalog/REPORT_A3-A5.md`, `MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md`, `CLASSIFICATION.md`; every decision with its date in `DECISIONS.md`.

## Rules

**Sources and matching.** Ruiz and Madariaga (2018) for the large events; Cabello et al. (2025) before 1904 only; Centennial, ISC-GEM, ISC, ISC-EHB, GCCEL, GCMT, USGS ComCat, Potin et al. (2024, to July 2020) and CSN. Events are matched across catalogues once and carry one identifier.

**Epicentre.** A local catalogue (Potin, CSN) comes first only inside its own network (18–46° S, west of the arc, from 1982); elsewhere and before 1982 the global catalogues come first (GCCEL, ISC-EHB, ISC, ComCat). A local record more than 50 km from every global record of the event is not used.

**Depth.** The first measured depth in the same order, with GCCEL and ISC-EHB before the local catalogue offshore. Fixed depths, agency defaults, ISC-EHB level 3 and the GCMT centroid are not measured depths. An event with none left has an unknown depth; it is not filled in. Where the literature states the class of such an event, a depth is assigned from the class and Slab2 and flagged (17 events).

**Magnitude.** One Mw per event. From 1976: GCMT from Mw 5.4; W-phase and regional moment magnitudes; GCMT below 5.4, lowered slightly; the CSN moment magnitude of the ISC Bulletin only if there is no other; Ruiz and Madariaga; else a magnitude converted with relations fitted on Chilean pairs (surface-wave scales for shallow events only). Before 1976: Ruiz and Madariaga, a Centennial Mw, an ISC-GEM direct Mw, a Centennial Ms or mB converted, an ISC-GEM proxy Mw, Cabello. Depth-dependent conversions use the final depths.

**Large events.** Reviewed one by one; a value is corrected only from a source that was read, in `overrides_A6.csv` (74 accepted rows: 65 class hints, 7 Mw, 1 longitude, 1 depth).

**Class.** Each event has weights for interface, in-slab, crustal and outer rise that add to 1. A class hint comes first. West of the trench is outer rise. Over the shallow slab (Slab2 top ≤ 50 km) the depth gives scores after Haynie et al. (2026), interface within ± 15 km of the slab surface, averaged over the depth error of the event. A mechanism is compared with the interface mechanism (the Slab2 plane slipping in the convergence direction) by one misfit, strict on the plane (20°) and loose on the slip direction (45°): inside, the interface odds are raised by 3.9; outside, no interface weight. A mechanism never decides alone. A weight of 0.8 or more becomes 1. An event without a measured depth takes the class shares of the classified events of its bin, unless its position decides. Sub-classes by position; the Jujuy nest (within 0.8° of 66.9° W, 24.0° S, 150–320 km) is a class of its own.

## Numbers (Mw ≥ 4.5 in the domain)

| | events or weight |
|---|---|
| events | 14 279 (1 943 of Mw ≥ 5.5, 163 of Mw ≥ 7) |
| depth measured / unknown / assigned | 12 391 / 1 871 / 17 |
| with a mechanism | 2 671 |
| Mw measured / converted / ISC-GEM / Centennial / Cabello / Ruiz and Madariaga / A6 | 4 296 / 9 177 / 542 / 126 / 104 / 27 / 7 |
| interface (of it Antarctic) | 4 497.7 (142) |
| in-slab: shallow / intermediate / Jujuy nest | 1 636.5 / 5 388.4 / 1 054 |
| crustal: forearc / arc / backarc / Patagonia | 581.1 / 221.6 / 309.6 / 77 |
| outer rise / unclassified | 509 / 4 |
| one class (weight 1) | 11 251 |
| split with a depth / split without a depth | 1 736 / 1 292 |

Against the catalogue of 13 Nov, this run changes one magnitude (1934-03-01, Mw 7.3 → 7.6, converted at its accepted depth of 120 km), no epicentre and no depth.

## Open points

- **Events without a measured depth (1 871):** 103 before 1900, 269 in 1900–1963, 548 in 1964–1981, 951 from 1982; 431 of Mw ≥ 5.5 and 74 of Mw ≥ 7. By position 579 have one class (outer rise 194, Antarctic interface 97, deep slab 225, no slab 58, class hint 5); 1 292 are shared by the bin shares (interface 645, in-slab 508, crustal 139). They count in the rates by their weights and cannot enter a depth model. The fits are to be run with and without them (DECISIONS).
- **Width of the interface zone:** the largest choice. ± 10 km gives 23 % less interface, ± 20 km 11 % more; the mechanism rule moves it by 4 %.
- **Mechanism tolerances** (20°, 45°) are chosen, not fitted; one convergence azimuth (257°) for the whole margin; the hard edge leaves 122 events just outside without interface weight.
- **With the catalogued depth errors** no rule classes more than about two thirds of the events over the shallow slab correctly (synthetic test, `explore/X5`).
- **Large events left as they are** (converted Centennial values above the ISC-GEM proxies): 1918-05-20, 1925-05-15, 1948-05-11, 1971-06-17; a sensitivity case for the in-slab Mmax.
- **Mw ≥ 7 still split with a depth:** eight events of 1940–1965, with depth errors of 20 km in seven of them.
- **Rules alone against the literature:** Copiapó 1918 (epicentre west of the trench) and La Ligua 1971 (slab top at 56 km) get another class from the rules; both carry the literature class.
- **Not re-read before citing:** Kanamori and Rivera (2017), Astiz (1987) and the web tables used for 1878 and 2025 were opened by a sub-agent only.
