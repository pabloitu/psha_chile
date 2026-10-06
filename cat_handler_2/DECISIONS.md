# cat_handler_2: decisions

Each decision with its evidence and the place in the code where it lives
(`prepare.py` and `config.py` for items 1-15, `classify.py` and `params.py`
for 16-25, the CSV files for 26-28). Numbers from the full runs of 29 Sep 2026
unless marked otherwise.

## Inputs and scope
1. Base catalog: Cabello et al. (2025) as distributed; every event and every magnitude comes from it (config CABELLO).
2. Only events with Cabello magnitude above 3.9 are written (MMIN); lower rows are read only so that a twin can merge. North limit (LAT_MAX = 17 S, 30 Sep 2026): Cabello rows north of it are dropped before anything else, so that Peruvian seismicity does not enter the source fits; no other bound (Cabello reaches 78.5 W, 65 W and 57.6 S).
3. Frozen inputs: Potin et al. (2024) relocations, GCMT ndk, the ANSS moment tensors queried per event (anss_fm.csv), GEM.

## Duplicates (dedup)
4. Cabello contains cross-agency duplicates (same earthquake from CSN, ISC, USGS, GCMT): 23-33 % of rows at M 4.5-5.5, 11 % at M 6-6.5, none left at M >= 7 (check/summary.png).
5. Cabello's GCMT rows carry the centroid; each is tied to its ndk entry and matched on the PDE hypocentre (GC_DT, GC_KM).
6. Merge windows (DUP_RULES): 15 s, 50 km, 0.8 units; plus 10 s, 30 km, 2.0 units when the larger magnitude of the pair is 5.5 or more (applied to all magnitudes it merged M 4 rows into M 2 rows and dropped ~2 000 events below the cut), for the large events whose Cabello magnitudes differ by more than 0.8 between agencies (e.g. 1975-05-10 ISC-GEM 7.8 vs ISC 6.3). Chance pairs expected inside the windows: ~30 of ~18 500 merges.
7. Magnitude: Ruiz and Madariaga (2018) where the paper gives a single Mw for a matched event (21 events, overrides.csv, field mag; mag_cabello keeps Cabello's value); ranges, bounds (>, <) and Ms values keep Cabello's. Otherwise always a Cabello magnitude; for a merged event the GCMT row, else ISC-GEM, else a row with native Mw, else CSN, USGS, ISC, CERESIS in that order (MAG_FALLBACK; local magnitudes are the best for small events). Formerly from the GCMT row, else ISC-GEM, else a row with native Mw, else the location row (MAG_PREF).
8. Location of a merged event: Potin-relocated CSN, ISC-GEM, ISC, USGS, CSN, GCMT, CERESIS (LOC_PREF). Events located by a Cabello GCMT row (its centroid) take the ComCat location of their ANSS match, as the old merge did (ANSS preferred): 10 s, 50 km, else 90 s, 100 km (ComCat times for large events are often W-phase centroid times); a default ComCat depth keeps the centroid depth (GCMT_TO_ANSS, ANSS_LOC_WIN). The centroid stays in lon_orig, lat_orig, depth_orig. Restores Maule 2010, Valparaiso 1985, Antofagasta 1995, Iquique 2014, Illapel 2015.

## Location and depth (locate)
9. Cabello already relocated 58 163 CSN rows with Potin (identical to Potin); the old pipeline's relocation step was lost in the code (it wrote the frame before relocation) but was mostly redundant.
10. CSN rows Cabello did not relocate take Potin's location and depth, one-to-one within 5 s, 30 km (POT_*): 5 461 events.
11. Default depths, per agency (FIXED_DEPTHS), detected as spikes of each agency's depth histogram (an integer depth with at least 30 rows and 5 times the median count of its neighbours within 3 km): ISC 0, 10, 33, 35 and the regional intermediate defaults 100, 150, 169, 181, 195, 200, 222, 250, 251, 262; USGS 0, 5, 10, 33, 35, 100, 150, 200; ISC-GEM 15, 20, 25, 30, 35 (15 km holds 14 % of its rows); GCMT 12 and 15 (fixed centroids); CSN 0, 10, 150, 200, 220, 230 and every row with depth_error = 0, which is how CSN flags a fixed depth (FIXED_ERROR_ZERO). Until 30 Sep only 0, 10, 33, 35 km of USGS, ISC and ISC-GEM were treated as defaults, which left rows of intermediate-depth events on default depths (150, 181, 200 km) inside the in-slab family with a trusted depth.
12. A default or missing depth is filled from another row of the same earthquake with a free depth, then Potin (10 s, 50 km), then the GCMT centroid depth when GCMT solved for it (FREE); GCMT never otherwise.
13. Cabello's assigned historical depths (obs_depth) are kept but marked assigned.

## Mechanisms (mech)
14. Order ANSS (ComCat moment tensors), GCMT, GEM, Cabello's own planes (MECH_ORDER); one-to-one matches (MECH_WIN). GEM before Cabello as in the old merge: Cabello's ISC-GEM planes for Valdivia 1960 (10/17/140 and 139/79/77) are not conjugate; GEM gives 10/17/90.
15. ANSS and GCMT agree within 60 deg (Kagan) for all but 6 of ~1 800 shared events; those 6 are left to review, no rule.

## Classification (classify.py)
16. Rules ported from the old classifier: deep nest, outer rise, intra-arc polygon, backarc, below the plate, deep slab, pre-1930 rule, Cabello's 'Crustal' remarks.
17. Outer rise: seaward side of the local trench segment, not 'west of the nearest trench point' (the old test put Peru events in the outer rise).
18. Backarc kept as its own class (as in the backarc variant of the old code), for events with a real depth of at most CRUSTAL_MAX_Z (item 34). Default-depth events east of the arc go to the slab (item 22): under the Argentine backarc the slab is at 100-200 km and many intermediate-depth events carry default depths.
19. South of the Chile triple junction (46.15 S, SOUTH_LAT) there is no Slab2. The Antarctic trench is taken from Bird (2003) PB2002 (segments AN\SA and SC/AN, data/shapefiles/pb2002_antarctic_trench.geojson). Seaward of it: outer_rise; within 150 km landward and not deeper than 60 km: patagonia_interface; the rest: patagonia_crustal (PAT_WIDTH_KM, PAT_MAX_Z). Magallanes-Fagnano events (1879, 1949 M8.0, 1950) fall 240-350 km from the trench: crustal (their assigned depths are shallow). Since 30 Sep 2026 patagonia_crustal, like every crustal class, needs a real depth of at most 30 km; unknown depths outside the footprint are unresolved, except the four Magallanes-Fagnano events kept by hand (class_overrides.csv: 1879 M7.2, 1907 M5.5, 1949 M8.0, 1970-06-15 M6.8), the only large events of that fault system. No dip is inferred: the footprint is a band in map view; the sections south of the junction show the Slab2 top of 44 S to 46.15 S against distance from the trench as a reference for a dip.
20. Interface band half-width by depth status: 11 km for Potin locations, 15 km otherwise (IF_TOL); the error-ellipse test is dropped (it read km as degrees).
21. Unknown depth (default, missing, assigned) skips every depth test: interface-like mechanism -> interface; other mechanism -> intra_slab; no mechanism -> interface, where the interface can exist (slab top < 50 km). Amended 30 Sep 2026 (item 34): a non-interface mechanism no longer goes to forearc.
22. Unknown depth over a deeper slab (slab top >= 50 km, inside the arc polygon or east of it) or without a slab: unresolved, in no family (rule unk_deep). Decided 30 Sep 2026 after the neighbour check (check/unknown_depth.csv): of 1 469 such events the located neighbours were in-slab for 697, crustal for 395, mixed for 253; 332 lay over a slab top deeper than 250 km, mostly CERESIS historical events in NW Argentina whose assigned depth is the Slab2 top itself (96 % of CERESIS assigned depths equal it). Poorly constrained data; 171 events of M >= 5.5 leave the in-slab family, almost all east of the arc. Unknown depths never go to a crustal class where a slab exists (item 34); the neighbour vote of 29 Sep (rule unk_vote) is withdrawn.
23. Above a deep slab and deeper than 70 km: slab_deep, not forearc (FOREARC_MAX_Z).
24. An interface-like mechanism makes the event interface up to a 65 km slab top and up to 10 km beyond the band (IF_MECH_MAX_TOP, MECH_EXTRA): Arauco 1975, Antofagasta 1987, La Ligua 1971 in Ruiz and Madariaga (2018).
25. Assigned historical depths: the unknown-depth rule reaches a 65 km slab top (IF_MAX_TOP_HIST), because damage-based epicentres sit landward of the rupture (Illapel 1880).

## Event-level decisions (overrides.csv, additions.csv, class_overrides.csv)
26. Maule 2010: Cabello time 3 h early, set to the GCMT centroid time.
27. Pichilemu 2010 first event (Mw 6.9, 14:39) added; missing in Cabello.
28. Class decisions (class_overrides.csv) and magnitude decisions (overrides.csv) from Ruiz and Madariaga (2018) where the rules disagree: Chiloe 2016, Illapel 1880, Taltal 1966, La Ligua 1971, Arauco 1975, Antofagasta 1987, Constitucion 2012 -> interface; Santiago 1647, Michilla 2007 -> intra_slab; Arica 1987 -> slab_deep.

## Left open
29. Historical M >= 7 still unresolved after rule 25: 1687 (Santiago area), 1850 (arc), 1870 (Calama).
30. Events of the paper not in Cabello: Pica 1768, Taltal 1887, Copiapo 1959, Mejillones 1994, the Valdivia Ms 7.8 foreshock, the Maule outer-rise Mw 7.4.
31. In-slab Mmax: Santiago 1647 (M8.4, intraslab by the paper) is now the largest in-slab event; with the catalog Mmax + 0.2 rule it raises the in-slab Mmax from 8.3 to 8.6. Whether historical events count for Mmax is a source-model decision.
32. Cabello's Mw differs by agency for the same earthquake: against GCMT Mw, ISC rows are 0.33 low, CSN 0.14 low, USGS 0.06 high (medians, M >= 5). Events present only as ISC rows (many in 1964-1990s) carry an Mw about 0.3 low. Not corrected (the Cabello rule); to be stated as a limitation or corrected in the source-model step.
33. The neighbour vote (item 22, 29 Sep) sent 37 default-depth events of M >= 5.5 from slab_deep to backarc, several in the Pampean flat-slab region (28-33 S). Reversed by item 34: they are slab_deep again.
34. Crustal depth cap (30 Sep 2026, CRUSTAL_MAX_Z = 30 km in params.py): forearc, intraarc, backarc, patagonia_crustal and unclassified hold only events with a real depth (relocated_*, free, filled) of at most 30 km. Deeper events go through the slab tests: at or below the slab top slab_deep, in the interface band by the band rules, above a deep slab and deeper than FOREARC_MAX_Z slab_deep (deep_above), between 30 km and FOREARC_MAX_Z above a deep slab unresolved (rule deep_mid, the lever is FOREARC_MAX_Z), no slab unresolved. Unknown depths go to the slab family (item 22). Evidence: four intraarc events of M >= 7 at 70-90 km in northern Chile (1782, 1922, 1949, 1976) taken by the old arc-polygon rule, which tested depth only against 90 km; they distorted the intraarc MFD and set its Mmax. Exceptions, kept crustal regardless of depth and listed in results/cat_handler_2/crustal_exceptions.csv: Cabello's 'Crustal' remarks (rule remark) and class_overrides.csv.