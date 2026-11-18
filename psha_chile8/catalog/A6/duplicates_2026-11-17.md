# Duplicates (A11), 17 Nov 2026

The 40 pairs of the A3 review lists of 11 Nov (`merged/review/close_events_m45_2026-11-11.csv`, 33 pairs;
`possible_splits_2026-11-11.csv`, 7 pairs), decided from the source records of each event. One earthquake is two
events when a source lists it under two ids that the merge kept apart; it is two earthquakes when a reviewed
catalogue (ISC-EHB, reviewed ISC) or the local network lists both.

## Rule (Pablo, 17 Nov)

An event made of one ISC record whose prime origin is not ISC's own (an ISC copy of one agency's solution, mostly in
the unreviewed months) joins the nearest event with records from two or more sources within 10 s and 100 km
(`LONE_S`, `LONE_KM`; `magnitude.merges`, read by `locate.py` and `magnitude.py` before they choose location and Mw). It merges 22 events on catalogue 17f: 10 pairs of the close-events list, 2 of the splits (2026-01-02 00:28, 2026-04-15 08:46), 3 pairs found by the scan of 17 Nov (2026-03-30 08:25 Mw 4.2, 2026-05-11 17:14 Mw 4.8, 2026-05-27 04:17 Mw 4.9) and 7 events without Mw outside the lists. 50 km was tried first (14 events); 20 s and more starts to catch events of the 2010 and 2014 aftershock sequences. The merged events are
listed with the event they join in `merged/review/duplicates_merged_<run>.csv` (copied into each freeze; 22 in run 2026-11-17g). Merging keeps every source record of the earthquake in one event; an A6 row `exists = False` would drop an event with its records.

| pair | merged | into |
|---|---|---|
| 2010-03-01 23:27 | cl20100301232705 (IDC) | cl20100301232700 |
| 2025-03-25 22:55 | cl20250325225549 (AUST) | cl20250325225553 |
| 2025-04-08 22:30 | cl20250408223041 (AUST) | cl20250408223045 |
| 2025-04-24 03:20 | cl20250424032004 (IDC) | cl20250424032008 |
| 2025-07-02 01:39 | cl20250702013944 (IDC) | cl20250702013940 |
| 2025-11-13 04:59 | cl20251113045938 (GFZ) | cl20251113045936 |
| 2025-11-13 09:04 | cl20251113090444 (VAO) | cl20251113090441 |
| 2026-04-24 13:49 | cl20260424134944 (VAO) | cl20260424134941 |
| 2026-07-06 16:15 | cl20260706161551 (GFZ) | cl20260706161552 |
| 2026-09-09 10:06 | cl20260909100700 (GFZ) | cl20260909100658 |

## Reviewed merges in `catalog/duplicates.csv` (event, kept event, reference, reason), decided one by one with Pablo

These rows were first written as `merge_into` rows of `overrides_A6.csv` and moved to their own file on 17 Nov (Pablo): the override file keeps corrections of event properties only. The review went pair by pair from the largest magnitude down (cards with one map and the source records grouped per earthquake and agency), then a sweep from Mw 4 and one of Mw ≥ 6 (`WE CANT REPEAT ANY LARGE EVENT`, Pablo). Instrumental Mw ≥ 6 pairs are all listed apart by ISC-GEM and kept. Historical double entries of Cabello et al. (2025): 1833, 1847, 1868 and 1877 merged; 1831-10-08 Arica kept as two earthquakes (main shock and a 02:15 event 62 km away, both unrevised in CERESIS-GEM except the first). The 1784 'Aftershocks?' entries (17 rows, all Mw 6.23 at one point), 1600 (Huaynaputina) and 1822 are not copies and lie outside the domain or before the completeness periods; left as the source gives them. Remaining close pairs after the sweep: 27 Potin records without magnitude and 9 ISC copies without Mw (no effect on any count).

| merged | into | reason |
|---|---|---|
| cl20250904041018 | cl20250904041009 | the Mw 5.9 counted twice: the kept event cl20250904041009 holds the same quake (NEIC ISC 643990120, ComCat us7000qtpj Mww 5.9, GCMT C202509040410A); CSN and ComCat also list a Mw 4.7–5.0 foreshock at 04:10:09, whose records stay in the kept event |
| cl20260925152910 | cl20260925152906 | unreviewed ISC lists the same quake twice (IDC 646459988 and NEIC 646462088, 4 s and 14 km apart); kept event cl20260925152906 has the CSN solution (Mw 5.2), located inside the network |
| cl20140403031114 | cl20140403031118 | ComCat 03:11:14 is the ISC 604399523 event (03:11:16) of the kept event cl20140403031118; A3 paired that event with ComCat usb000pnzl (03:11:31), which belongs to the ISC 03:11:34 event |
| cl20200629050633 | cl20200629050630 | second ComCat id of the quake of the kept event cl20200629050630 (ComCat us7000ae33, ISC 618639527, ISC-EHB, ISC-GEM), 3 s and 16 km apart |
| cl19970112083016 | cl19970112083019 | same quake as ISC 1006026 (08:30:19, 1.5 km) of the kept event cl19970112083019; A3 attached there ComCat usp0007vsj, a separate M 4.4 at 32.7° S |
| cl20150620052214 | cl20150620052219 | Potin lists the same Mw 5.5 twice, 4 s and 44 km apart; ISC, ISC-EHB, ISC-GEM, ComCat and GCMT list one event, the kept cl20150620052219 |
| cl20260123102640 | cl20260123102641 | IDC copy 121 km from the CSN / ComCat event cl20260123102641, 0.7 s earlier |
| cl20260905065459a | cl20260905065459b | IDC copy 78 km from the ComCat event cl20260905065459b, 0.7 s earlier |
| cl20250502131005 | cl20250502130940 | IDC copy 25 s after ComCat us7000pwkz (mb 5.7, 10 km away), event cl20250502130940 |
| cl19870424084605 | cl19870424084627 | Potin copy 21 s and 25 km from NEIC 469875 / ComCat usp00034e8 (mb 4.6), event cl19870424084627; Potin has no other record within 5 min |
| cl20250502160644 | cl20250502160641 | Drake Passage aftershock: CSN located the NEIC / ComCat mb 4.1 event (16:06:41.9) 70 km away, outside its network (Pablo, 17 Nov) |
| cl20250502162532 | cl20250502162525 | Drake Passage aftershock: CSN located the NEIC / ComCat event (16:25:25) 7 s later and 70 km away, outside its network (Pablo, 17 Nov) |
| cl20250502170832 | cl20250502170839 | Drake Passage aftershock: CSN located the NEIC / ComCat mb 4.0 event (17:08:39) 7 s earlier and 75 km away, outside its network (Pablo, 17 Nov) |
| cl20251008172251 | cl20251008172248 | deep in-slab event under the Puna: CSN located the NEIC / ComCat mb 4.2 event (17:22:48) 3 s later and 67 km away (Pablo, 17 Nov) |
| cl20250502152948 | cl20250502152942 | Drake Passage aftershock: CSN located the NEIC / ComCat mb 4.4 event (15:29:43) 5 s later and 75 km away, outside its network (Pablo, 17 Nov) |
| cl20220810214701 | cl20220810214659 | two CSN versions of one Ml 4.0 quake off Patagonia (48.3° S): the solution sent to ISC (GUC, 227 km) and the web catalogue (16 km), 60 km apart (Pablo, 17 Nov) |
| cl20251129175907 | cl20251129175905 | deep in-slab event under the Puna: CSN located the NEIC / ComCat mb 4.1 event (17:59:05) 2 s later and 60 km away (Pablo, 17 Nov) |
| cl20230724161428 | cl20230724161431 | CSN lists the ML 4.4 quake off Patagonia (49° S) twice: its web solution and its solution in ISC (GUC), with ComCat and ISC in the kept event (Pablo, 17 Nov) |
| cl18471008153000 | cl18470308150000 | 1847 La Ligua entered twice by Cabello: the CERESIS entry 1847-03-08 15:00 (Mw 7.4) and the 'This work' entry 1847-10-08 15:30 (Mw 7.0), same day of the month and hour, 94 km apart; Lomnitz lists one quake, 8 October; the date of 16 Nov (8 March, our source) is kept (Pablo, 17 Nov) |
| cl18330918130000 | cl18330918104500 | 1833-09-18 Arica entered twice by Cabello: the 'This work' entry 10:45 (Mw 7.45) and the CERESIS entry 13:00 (Mw 7.37), 2 h 15 min and 75 km apart (Pablo, 17 Nov) |
| cl18680813221500 | cl18680813164500 | 1868 Arica entered twice by Cabello: the unrevised CERESIS entry 22:15 Mw 6.2 sits at Arica, 251 km from the great earthquake, 5.5 h later; read as the same quake reported from Arica under another clock (Pablo, 17 Nov) |
| cl18770510012800 | cl18770510021600 | 1877 Iquique entered twice by Cabello: the unrevised CERESIS entry 01:28 Mw 6.5 sits off Arica, 269 km from the great earthquake, 48 min before it; read as the same quake reported from Arica under another clock (Pablo, 17 Nov) |

## Kept as two earthquakes

ISC-EHB or the reviewed ISC lists both, with their own phases, or the local network (Potin, CSN) lists both:
1993-05-24 23:51 (deep, Jujuy region); 2001-06-24 03:04, 05:05:09, 05:05:18 and 2001-07-07 10:12 (southern Peru
aftershocks); 2010-02-27 10:05 and 13:52 (Maule aftershocks); 2010-03-10 09:04; 2010-09-26 06:20; 2014-03-22 13:20;
2014-04-01 23:57/23:58 (Iquique foreshock and main shock); 2015-10-02 16:22; 2016-06-22 03:54; 2017-04-24 21:38
(Valparaíso foreshock and main shock); 2017-04-28 15:33; 2019-02-06 18:50; 2020-09-06 03:24.

Card 18 of the review (two events seconds apart in a sequence, separate ISC-EHB origins) kept as two earthquakes.

Run 2026-11-17g (frozen 18 Nov): 44 events merged, 22 reviewed and 22 by the rule; 10 had Mw ≥ 4.5 in the domain, two Mw ≥ 7 (1833 13:00, 1847-10-08).
