# Frozen catalogue of 17 Nov 2026, run g: decisions note

Final catalogue of psha_chile8. Chain run on the matched events of 11 Nov (`merged/events_2026-11-11.csv`, `links_2026-11-11.csv`, unchanged): `locate.py` → `magnitude.py` → `locate.py` → `classify.py`, run `2026-11-17g` (run on 18 Nov). It replaces `catalog/frozen/2026-11-17f/`, kept unchanged. The catalogue is `catalog_2026-11-17g.csv` (one row per earthquake, 204 912 events, 1513 to 2026). Checksums in `SHA256SUMS`, inputs in `INPUTS_SHA256` (identical to 17f), code in `code/`; `overrides_A6.csv`, `duplicates.csv` and `named_events.csv` are copied as used. Method notes: `catalog/REPORT_A3-A5.md`, `MAGNITUDES.md` (section 10 for this run), `RULES_LOCATION_MAGNITUDE.md`, `CLASSIFICATION.md`, `A6/duplicates_2026-11-17.md`; every decision with its date in `DECISIONS.md`.

## Changes against 2026-11-17f

- Duplicates (A11, Pablo, 17 Nov): 44 events merged into the event of the same earthquake. 22 reviewed pairs in `duplicates.csv` (among them the historical double entries of Cabello et al. 2025: 1833-09-18 Arica, 1847 La Ligua, 1868-08-13 Arica, 1877-05-10 Iquique); 22 single-agency ISC copies by the rule. List with the kept event, time and distance: `duplicates_merged_2026-11-17g.csv`. 10 of the merged events had Mw ≥ 4.5 in the domain; two of Mw ≥ 7 (1833 13:00 Mw 7.4, 1847-10-08 Mw 7.0), so 162 events of Mw ≥ 7 against 164. 1831-10-08 Arica stays two earthquakes.
- Magnitude conversions: a third depth group below 150 km (top of the Jujuy nest), taken by GUC ML (and CSN Ml / Mlv), SJA ML, ISC mb and NEIC mb (FITS to CAT, 17 Nov). With two groups the deep ML relation left nest events 0.1 too high and deep mb 0.1–0.15 too low; now every scale is within ± 0.1 of the measured Mw at every depth. 4 027 events of Mw ≥ 4.5 change by 0.1–0.3 (median −0.1 or +0.1); no event of Mw ≥ 7 changes. Near the Mw 4.5 cut 579 events enter and 432 leave, mostly converted values at about 110–120 km: in-slab intermediate weight 5 389.0 → 5 533.7.
- Totals (Mw ≥ 4.5, domain): 14 279 → 14 416 events; interface 4 497.4 → 4 482.7, in-slab 8 079.8 → 8 231.3, crustal 1 146.8 → 1 146.0, outer rise 552 → 553.
- A5 tests on this run: all pass that passed on 17f, plus Mw 6.5–7 predicted from Mw 5.0; figures in `catalog/figs/magnitude/` (new: `relations_others`, `residual_depth`, `residual_converted`, `compare_relations`, `compare_residual_depth`, `compare_residual_converted`).

## Rules

**Sources and matching.** Ruiz and Madariaga (2018) for the large events; Cabello et al. (2025) before 1904 only; Centennial, ISC-GEM, ISC, ISC-EHB, GCCEL, GCMT, USGS ComCat, Potin et al. (2024, to July 2020) and CSN. Events are matched across catalogues once and carry one identifier. An event that is a copy of another is merged into it (its records join the kept event, one record per source): the pairs reviewed by hand in `duplicates.csv` (22, with reference and reason), and an event made of one ISC record whose prime origin is not ISC's own, within 10 s and 100 km of an event with records from two or more sources (22 in this run; listed in `duplicates_merged_2026-11-17g.csv`).

**Epicentre.** A local catalogue (Potin, CSN) comes first only inside its own network (18–46° S, west of the arc, from 1982); elsewhere and before 1982 the global catalogues come first (GCCEL, ISC-EHB, ISC, ComCat). A local record more than 50 km from every global record of the event is not used.

**Depth.** The first measured depth in the same order, with GCCEL and ISC-EHB before the local catalogue offshore. Fixed depths, agency defaults, ISC-EHB level 3 and the GCMT centroid are not measured depths. An event with none left has an unknown depth; it is not filled in. Where the literature states the class of such an event, a depth is assigned from the class and Slab2 and flagged (31 events).

**Magnitude.** One Mw per event. From 1976: GCMT from Mw 5.4; W-phase and regional moment magnitudes; GCMT below 5.4, lowered slightly; the CSN moment magnitude of the ISC Bulletin only if there is no other; Ruiz and Madariaga; else a magnitude converted with relations fitted on Chilean pairs (surface-wave scales for shallow events only); a relation may have up to three depth groups (down to 50 km, 50–150 km, below 150 km), chosen per scale by cross-validation. Before 1976: Ruiz and Madariaga, a Centennial Mw, an ISC-GEM direct Mw, a Centennial Ms or mB converted, an ISC-GEM proxy Mw, Cabello. Depth-dependent conversions use the final depths.

**Mechanism.** One per event: GCMT, then the ComCat products (GCMT copies, W-phase, other tensors, nodal planes), then for events before 1976 without one the literature mechanism listed by ISC-GEM (agency bibliog).

**Large events.** Reviewed one by one; a value is corrected only from a source that was read, in `overrides_A6.csv` (119 accepted rows: 91 class hints, 9 Mw, 6 depths, 4 longitudes, 3 latitudes, one mechanism of six values). Applied as the last step of `locate.py` and `magnitude.py`; the source (`loc_src`, `depth_src`, `mw_src`, `mech_src`) of an overridden epicentre, depth, Mw or mechanism is `a6`.

**Class.** Each event has weights for interface, in-slab, crustal and outer rise that add to 1. A class hint comes first. West of the trench is outer rise, and so are the Chile Ridge fracture-zone events within 75 km east of the trench between 45.5° S and 46.15° S (strike-slip and normal mechanisms; left out of the source model). An event without a slab whose nearest boundary is the Scotia–Antarctic one of PB2002 (Bird 2003), nearer than the Antarctic–South America trench and the Magallanes–Fagnano traces, is outer rise too: that boundary has no source in the model. Over the shallow slab (Slab2 top ≤ 50 km) the depth gives scores after Haynie et al. (2026), interface within ± 15 km of the slab surface, averaged over the depth error of the event. A mechanism is compared with the interface mechanism (the Slab2 plane slipping in the convergence direction) by one misfit, strict on the plane (20°) and loose on the slip direction (45°): inside, the interface odds are raised by 3.9; outside, no interface weight. A mechanism never decides alone. A weight of 0.8 or more becomes 1. An event without a measured depth takes the class shares of the classified events since 1976 of its bin, unless its position decides; before 1900, over the shallow slab or in the forearc, it takes no crustal share. The arc class ends where the arc polygon ends (47.24° S). Sub-classes by position; a crustal event outside the crustal grid of the source model (`data/crustal_grid_01_2026-11-15.csv`, 0.1° cells) keeps its crustal weight and takes the sub-class `outside`, which no fit, pattern or source reads, so that rate, pattern and sources cover the same region; the Jujuy nest (within 0.8° of 66.9° W, 24.0° S, 150–320 km) is a class of its own.

## Numbers (Mw ≥ 4.5 in the domain)

| | events or weight |
|---|---|
| events | 14 416 (1 931 of Mw ≥ 5.5, 162 of Mw ≥ 7) |
| depth measured / unknown / assigned | 12 565 / 1 820 / 31 |
| with a mechanism | 2 724 (GCMT 2 487, ComCat 184, ISC-GEM literature 52, A6 1) |
| Mw converted / measured / ISC-GEM / Centennial / Cabello / Ruiz and Madariaga / A6 | 9 322 / 4 291 / 542 / 126 / 100 / 26 / 9 |
| interface (of it Antarctic) | 4 482.7 (140) |
| in-slab: shallow / intermediate / Jujuy nest | 1 640.6 / 5 533.7 / 1 057 |
| crustal: forearc / arc / backarc / Patagonia / outside the grid | 547.5 / 218.0 / 89.5 / 40 / 251.0 |
| outer rise / unclassified | 553 / 3 |

## Figures

Drawn from this catalogue into `catalog/FIGURES/maps/`: `catalog/fig_positions.py` (`positions_m45`, `positions_m65`), `catalog/fig_classes.py` (`classes_m45`, `classes_m65`) and `catalog/fig_mechanisms.py` (`mechanisms_utm`, paper candidate). Magnitude figures: `catalog/magnitude_check.py`, the paper and supplement ones into `catalog/FIGURES/magnitudes/`, the other test figures into `catalog/figs/magnitude/` (the 17f set kept in `catalog/figs/magnitude/before_2026-11-17g/`).
