# Findings from X4 (classification) for the A3, A4 and A5 conversations

13 Nov 2026. From `explore/X4/REPORT.md` (section 7) and the checks behind it. Counts are events with Mw ≥ 4.5 in the domain (14 157) of `catalog/merged/catalog_2026-11-11.csv` unless said otherwise. Nothing was corrected in X4.

## For A4 (location, depth, mechanism): rerun

1. **Fixed depths that are not defaults are thrown away.** A4 treats every `depth_fixed` depth as not measured and takes the next source.
   - ISC-EHB: 372 L1 and 509 L2 depths are flagged fixed; 20 % of all fixed ISC-EHB depths are not on a multiple of 5 km. ISC prime depths show the same (fixed at 112, 136, 219 km). These look like depths held at a depth-phase value. To confirm in the ISC and ISC-EHB documentation.
   - Effect: 1 175 events have a non-round depth of their location source replaced by another source's depth; 359 by more than 20 km (329 of them ISC → ComCat); 285 would fall on another side of a ± 15 km interface band (18 of Mw ≥ 5.5).
   - Example: Arica 1987-08-08 Mw 7.2, ISC-EHB L1 69.7 km replaced by ISC 19.05 km (an intraslab event that then looks crustal). Also 1979-02-11 (ISC 112 → ComCat 77 km), 1976-09-06 (219 → 188), 1988-02-20 (136 → 169).
   - Suggested rule to test: a fixed depth counts as measured when it is not on a default bin of its agency and not a round value; or, for ISC-EHB, by its depth-phase information if the search output carries it.
2. **Depths before 1964 are called measured.** 211 events before 1964 have a measured depth; 134 sit on a multiple of 5 km (ISC-GEM 25 km 35 times, 20 km 20 times; ComCat 15 km 11 times, 35 km 7 times).
   - The default table is built per agency and period from 1964; ComCat's copies of ISC-GEM do not carry the agency `us`, so the forced bins (`us` 10 / 33 / 35) miss them.
   - They get σ from the modern tables: 3.0 km for an ISC-GEM depth of 255 km in 1909.
   - Consequences: Atacama 1922 (Mw 8.5) at 70 km, Valparaíso 1906 at 35 km, Concepción 1960-05-21 at 11.5 km.
   - Suggested: before 1964 a depth on a round value is unknown, and any kept depth gets a large σ (20–25 km).
3. **Potin first also where the Potin record disagrees with every teleseismic member.**
   - 120 Potin-located events have their closest ISC-EHB or ComCat member more than 50 km away (18 of Mw ≥ 5.5): Tirúa 2011-01-02 Mw 7.1 (61 km), 2011-02-11 Mw 6.8 (55 km), 1995-11-01 Mw 6.6 (81 km and 69 km deeper than the others), Maule aftershocks of 2010 at 37–38° S (55–74 km).
   - Depth: 203 events have a Potin depth above 5 km over a slab top deeper than 15 km (23 of Mw ≥ 5.5; Illapel aftershocks of 2015-09-17 and -21, Mw 6.6–6.8, at 0.0–1.8 km; 2007-11-15 Mw 6.8 at 2.4 km; Tirúa 2011 at 2.8 km). 88 lie more than 40 km under a slab top shallower than 50 km, 77 % of them offshore (1995-11-01 at 88.5 km over a slab top of 9.5 km; 2015-06-20 Mw 6.4 at 72 km). 28 depths are negative.
   - X3 already found Potin depths above 30 km and offshore poor. Suggested to test: offshore (or west of the coast by more than 20 km), ISC-EHB L1 / L2 and GCCEL before Potin for depth; a Potin record more than 50 km from the event's teleseismic members is not used.
4. **Depth σ.** ISC-EHB L1 1.65 km, L2 2.3, ISC 2.8, ISC-GEM 3.0 km at ≥ 70 km are spreads between catalogues that share data (X1 against EHB; X3 with 7–14 pairs), not errors. Any rule that uses σ (band width, split weights) then favours those sources. Suggested: a floor (5 km?) or σ by depth-phase quality.
5. **`backarc()`** continues the end edges of the arc polygon north of 17.6° S and south of 47.2° S (359 and 185 events). The polygon itself is right: `data/intraarc.shp` (Pablo, 12 Nov).
6. **Far-offshore CSN web events** of 2024–2026 at 44–46° S, west of the trench, count as inside the network (already in the A4 entry); they form a dense cluster in the outer-rise class.
7. **Output.** `catalog_2026-11-11.csv` is not sorted by time. Three A5 runs and two A4 runs overwrote files with the same name and date; give the rerun its own date.

## For A5 (Mw)

1. **CSN regional Mw (GUC Mwr) outliers taken before other moment magnitudes.** Five events have a catalogue Mw 0.5–0.6 above the moment tensor of the same event: 2015-09-05 10:17 (GUC Mwr 5.1, USGS Mwr 4.56), 2015-09-18 13:51 (5.2 against 4.61; a GCMT solution exists), 2015-09-27 21:04 (5.4 against 4.89), 2016-02-05 05:24 (5.0 against 4.42), 2025-05-21 00:38 (CSN web Mw 5.7 against USGS Mwb 5.18).
   - Over all direct values with a tensor: 16 of 97 GUC Mwr differ by 0.3 or more from the tensor Mw, against 7 of 1 879 GCMT, 3 of 499 NEIC Mww, 1 of 86 NEIC Mwr.
   - A5 measured σ 0.13 for GUC Mwr against 0.05 for GCMT and NEIC Mww, and still ranks it second below 5.4. Suggested to test: NEIC Mww, then NEIC Mwr and GCMT before GUC Mwr; or a cross-check that drops a reference value more than 0.3 from the event's other moment magnitudes.
2. **2010-02-27 08:25 Mw 7.0** (ML 6.8 alone, already in `review/mw_large_proxy`) enters the Mw ≥ 7 statistics as an in-slab event. It needs a decision before any M ≥ 7 count.
3. **1878-01-23 Mw 7.9** (Cabello, CERESIS value) sits at 77.0° W, 458 km west of the trench; magnitude and epicentre both need A6.
4. **The provisional depth used for the depth split of the relations (50 km) and for the 60 km limit of the surface-wave scales** is the A3 reference depth without default screening. After the A4 rerun (points 1–3 above change depths by more than 20 km for several hundred events), rerun A5 on the new depths and check how many events change relation.

## For A3 (matching)

1. **No matching error was found in X4.** The Potin records far from their teleseismic members (A4 point 3) are matched correctly; the problem is which member locates the event.
2. **To look at once:** 1928-12-02 04:20 Mw 7.2 (ISC-GEM 908989, 24 h 14 min after Talca 1928-12-01 04:06, about 120 km away) and the pair 1919-03-02 03:26 Mw 7.3 / 11:45 Mw 7.2 (the second 80 km west of the trench): real separate events in ISC-GEM, or one earthquake listed with two dates?
3. **Still open from A3:** the three Drake Passage events of 2025-05-02 (12:58, 13:07, 13:09); the first has Mw 7.5 and no depth.
4. **Ruiz and Madariaga matches** were used as they are (59 events); Pablo confirmed the paper as the authority for class (12 Nov). X4 found no wrong match; Talca 1928 is on the 12-01 event.
