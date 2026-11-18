# Frozen catalogue of 17 Nov 2026, run f: decisions note

Final catalogue of psha_chile8. Chain run on the matched events of 11 Nov (`merged/events_2026-11-11.csv`, `links_2026-11-11.csv`, unchanged): `locate.py` → `magnitude.py` → `locate.py` → `classify.py`, run `2026-11-17f`. It replaces `catalog/frozen/2026-11-16e/` and the intermediate `2026-11-17c/` and `2026-11-17e/`, all kept unchanged; against 17c it adds three interface events (below), and against 17e only `mw_src` reads `a6` where an A6 row sets the Mw (9 events). The catalogue is `catalog_2026-11-17f.csv` (one row per earthquake, 204 956 events, 1513 to 2026). Checksums in `SHA256SUMS`, inputs in `INPUTS_SHA256`, code in `code/`; `overrides_A6.csv` and `named_events.csv` (events named in the literature, with the label positions of the mechanism map) are copied as used. Method notes: `catalog/REPORT_A3-A5.md`, `MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md`, `CLASSIFICATION.md`; every decision with its date in `DECISIONS.md`.

## Changes against 2026-11-16e

- Overrides (Pablo, 17 Nov): 1953-05-06 Chillán in-slab (Astiz et al. 1988, Table A, p. 131; Lomnitz 2004, p. 374); 1952-06-11 San Juan crustal (MASCSN26, p. 117); 1958-09-04 Las Melosas Mw 6.3 → 6.8 (Cabello et al. 2025, Table 7; MASCSN26, p. 116; ISC-GEM 6.81); 2010-03-11 15:06 Pichilemu Mw 6.8 → 6.2 (ISC-GEM) and crustal as its sequence; 1960-05-22 Valdivia mechanism 7/20/105 (Barrientos and Ward 1990, p. 592) instead of the oblique 10/17/140 (Kanamori et al. 2019; disputed by Savage 2022, p. 1171); 1960-12-02 Mw 7.2 off Taltal at the ISC-GEM depth of 35 km (quality A) and interface (Pablo's call); the Valdivia aftershocks of 1960-06-20 02:01 and 12:59 interface (Cifuentes 1989, p. 670, Figs. 8–9).
- Mechanisms from the literature listed by ISC-GEM for events before 1976 without another: 62 events (53 in the domain; 61 keep it, Valdivia's is replaced by the override); 14 events of Mw 5.7–7.1 between 1962 and 1970 change class with them.
- `loc_src = a6` where A6 moves the epicentre (Aysén 1960, 1927-11-21, 1919-03-02, 1878-01-23); `mech_src = a6` for an A6 mechanism.
- Class totals (Mw ≥ 4.5 in the domain): interface 4 502.8 → 4 497.4, in-slab 8 075.3 → 8 079.8, crustal 1 145.9 → 1 146.8. The 164 events of Mw ≥ 7 are the same events.
- Not changed: after 1976 the measured GCMT Mw stays ahead of Ruiz and Madariaga (10 events differ by 0.1–0.3); 1918-05-20 keeps the depth of the slab convention; Pica 1768 (in no catalogue) and 1907-01-19 Magallanes (Cabello only, after 1904) are not added.

## Rules

**Sources and matching.** Ruiz and Madariaga (2018) for the large events; Cabello et al. (2025) before 1904 only; Centennial, ISC-GEM, ISC, ISC-EHB, GCCEL, GCMT, USGS ComCat, Potin et al. (2024, to July 2020) and CSN. Events are matched across catalogues once and carry one identifier.

**Epicentre.** A local catalogue (Potin, CSN) comes first only inside its own network (18–46° S, west of the arc, from 1982); elsewhere and before 1982 the global catalogues come first (GCCEL, ISC-EHB, ISC, ComCat). A local record more than 50 km from every global record of the event is not used.

**Depth.** The first measured depth in the same order, with GCCEL and ISC-EHB before the local catalogue offshore. Fixed depths, agency defaults, ISC-EHB level 3 and the GCMT centroid are not measured depths. An event with none left has an unknown depth; it is not filled in. Where the literature states the class of such an event, a depth is assigned from the class and Slab2 and flagged (31 events).

**Magnitude.** One Mw per event. From 1976: GCMT from Mw 5.4; W-phase and regional moment magnitudes; GCMT below 5.4, lowered slightly; the CSN moment magnitude of the ISC Bulletin only if there is no other; Ruiz and Madariaga; else a magnitude converted with relations fitted on Chilean pairs (surface-wave scales for shallow events only). Before 1976: Ruiz and Madariaga, a Centennial Mw, an ISC-GEM direct Mw, a Centennial Ms or mB converted, an ISC-GEM proxy Mw, Cabello. Depth-dependent conversions use the final depths.

**Mechanism.** One per event: GCMT, then the ComCat products (GCMT copies, W-phase, other tensors, nodal planes), then for events before 1976 without one the literature mechanism listed by ISC-GEM (agency bibliog).

**Large events.** Reviewed one by one; a value is corrected only from a source that was read, in `overrides_A6.csv` (119 accepted rows: 91 class hints, 9 Mw, 6 depths, 4 longitudes, 3 latitudes, one mechanism of six values). Applied as the last step of `locate.py` and `magnitude.py`; the source (`loc_src`, `depth_src`, `mw_src`, `mech_src`) of an overridden epicentre, depth, Mw or mechanism is `a6`.

**Class.** Each event has weights for interface, in-slab, crustal and outer rise that add to 1. A class hint comes first. West of the trench is outer rise, and so are the Chile Ridge fracture-zone events within 75 km east of the trench between 45.5° S and 46.15° S (strike-slip and normal mechanisms; left out of the source model). An event without a slab whose nearest boundary is the Scotia–Antarctic one of PB2002 (Bird 2003), nearer than the Antarctic–South America trench and the Magallanes–Fagnano traces, is outer rise too: that boundary has no source in the model. Over the shallow slab (Slab2 top ≤ 50 km) the depth gives scores after Haynie et al. (2026), interface within ± 15 km of the slab surface, averaged over the depth error of the event. A mechanism is compared with the interface mechanism (the Slab2 plane slipping in the convergence direction) by one misfit, strict on the plane (20°) and loose on the slip direction (45°): inside, the interface odds are raised by 3.9; outside, no interface weight. A mechanism never decides alone. A weight of 0.8 or more becomes 1. An event without a measured depth takes the class shares of the classified events since 1976 of its bin, unless its position decides; before 1900, over the shallow slab or in the forearc, it takes no crustal share. The arc class ends where the arc polygon ends (47.24° S). Sub-classes by position; a crustal event outside the crustal grid of the source model (`data/crustal_grid_01_2026-11-15.csv`, 0.1° cells) keeps its crustal weight and takes the sub-class `outside`, which no fit, pattern or source reads, so that rate, pattern and sources cover the same region; the Jujuy nest (within 0.8° of 66.9° W, 24.0° S, 150–320 km) is a class of its own.

## Numbers (Mw ≥ 4.5 in the domain)

| | events or weight |
|---|---|
| events | 14 279 (1 943 of Mw ≥ 5.5, 164 of Mw ≥ 7) |
| depth measured / unknown / assigned | 12 395 / 1 853 / 31 |
| with a mechanism | 2 724 (GCMT 2 487, ComCat 184, ISC-GEM literature 52, A6 1) |
| Mw converted / measured / ISC-GEM / Centennial / Cabello / Ruiz and Madariaga / A6 | 9 176 / 4 296 / 542 / 126 / 104 / 26 / 9 |
| interface (of it Antarctic) | 4 497.4 (142) |
| in-slab: shallow / intermediate / Jujuy nest | 1 636.8 / 5 389.0 / 1 054 |
| crustal: forearc / arc / backarc / Patagonia / outside the grid | 542.3 / 221.1 / 87.7 / 40 / 255.7 |
| outer rise / unclassified | 552 / 3 |

## Figures

Drawn from this catalogue into `catalog/figs/catalogue/2026-11-17f/`: `catalog/fig_positions.py` (epicentres by depth, `positions_m45`, `positions_m65`), `catalog/fig_classes.py` (classes, `classes_m45`, `classes_m65`) and `catalog/fig_mechanisms.py` (focal-mechanism map in UTM 19 S, `mechanisms_utm`, paper candidate; labels from `catalog/named_events.csv`). `catalog/sources_figs.py` draws the source catalogues.
