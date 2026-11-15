# A6: the large events, one by one. Report

13 Nov 2026, on the catalogue `merged/catalog_2026-11-13c.csv` (Centennial first before 1976). Files: `A6/dossiers.csv` (one row per event, property and source), `A6/literature.csv` (the literature values typed in, with reference and page), `overrides_A6.csv` (the proposals, all `proposed`), `A6/selection.csv`, `A6/changes_for_review.csv`, `A6/no_depth.csv`, `A6/counts.csv`, `figs/A6/large_events.png`. Script: `a6.py`.

**The review is not complete.** All 459 selected events have a dossier with every source value and were compared across their source catalogues. Literature was read for 112 of them; for 347 no paper was opened. What was read: Ruiz and Madariaga (2018, the frozen table and the notes of R1), Lomnitz (2004, Table 1, all of it), Abe (1982, all of it), the ISC-GEM entries with their magnitude source, the R1 notes of section 5 of `LITERATURE.md`, and three sources on the web for the named cases. Not read: rupture studies and finite-fault products for the events from 1976, Engdahl and Villaseñor's Table 1 beyond the notes of R1, and anything on the 223 events of Mw 6–7 without depth beyond the two historical papers.

## 1. Counts

Selected: 458 events (165 of Mw ≥ 7; 223 of Mw 6–6.99 without depth; the rest from the named cases and the review lists).

| period | selected | literature read, change proposed | literature read, no change | source values compared only | proposed Mw | proposed epicentre | proposed class hints |
|---|---|---|---|---|---|---|---|
| before 1904 | 111 | 10 | 24 | 77 | 1 | 1 | 8 |
| 1904–1963 | 239 | 24 | 15 | 200 | 7 | 0 | 19 |
| 1964–1975 | 12 | 11 | 0 | 1 | 5 | 0 | 7 |
| from 1976 | 97 | 26 | 2 | 69 | 2 | 0 | 28 |
| all | 459 | 71 | 41 | 347 | 15 | 1 | 62 |

Counts after the second pass (section 7), which added one event (1971-05-08) and one depth proposal (1934-03-01). No change of date, mechanism or existence is proposed. 79 rows in `overrides_A6.csv`: 15 Mw, 1 longitude, 1 depth, 62 class hints.

## 2. Proposed changes for Pablo to accept or reject

Every proposed change of Mw or location (all have Mw ≥ 7 before or after, or change Mw by 0.3 or more, except two of 0.2).

| event (UTC) | property | old | new | σ | source | reason |
|---|---|---|---|---|---|---|
| 1543-01-01 00:00 | mw | 7.4 | 7.7 | 0.3 | Ruiz and Madariaga (2018), section 3.1.1, p. 6–7 | named by the paper as larger than 7.7 (Comte and Pardo 1991, cited there); not matched in A3 because the paper gives the year only |
| 1878-01-23 00:00 | lon | -77.0 | -70.3 |  | CSN, Grandes terremotos en Chile (web table); NOAA NCEI significant earthquake database, event 2253, web table; event 2253 | the catalogue (CERESIS row of Cabello et al.) has 77.0° W, 700 km offshore; both sources give 70.3° W for the same latitude, magnitude and depth |
| 1916-06-21 21:32 | mw | 7.8 | 7.1 | 0.3 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 913818 | the catalogue value is the Centennial ABE1 mB 7.4 converted; ISC-GEM lists a direct Mw from a published moment |
| 1952-06-11 00:31 | mw | 6.5 | 6.8 | 0.3 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 893012 | the catalogue value is the Centennial ABE1 Ms 6.5 converted; ISC-GEM lists a direct Mw from a published moment |
| 1959-06-14 00:11 | mw | 7.9 | 7.2 | 0.2 | Abe (1982), p. 323, Table 1 | seismic moment 87 × 10^25 dyn cm (Wyss 1970) against the converted Abe mB 7.5; ISC-GEM direct Mw 7.10 |
| 1960-06-06 05:55 | mw | 7.2 | 7.7 | 0.2 | ISC-GEM v13.0 (Di Giacomo et al. 2015); Kanamori and Rivera (2017), catalogue entry 879416; Summary, p. 93 | ISC-GEM direct Mw 7.7 ± 0.2 (q B, s d) from the long-period moment of Kanamori and Rivera (M0 4.5e20 N m, slow event, source ≥ 190 s); the Centennial Mw 7.2 is Pacheco and Sykes' Ms 7.1 converted (1992, Table 4, p. 1339, type u), so the direct Mw goes first |
| 1962-02-14 06:36 | mw | 7.7 | 7.1 | 0.2 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 17291428 | the catalogue value is the Centennial ABE1 mB 7.5 converted; ISC-GEM lists a direct Mw from a published moment |
| 1962-08-03 08:56 | mw | 7.5 | 6.8 | 0.4 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 875121 | the catalogue value is the Centennial ABE1 mB 7.2 converted; ISC-GEM lists a direct Mw from a published moment |
| 1967-03-13 16:06 | mw | 7.1 | 5.7 | 0.3 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 837800 | the catalogue value is the Centennial BRK UK 7.3 converted; ISC-GEM lists a direct Mw from a published moment |
| 1970-06-15 11:14 | mw | 7.0 | 6.8 | 0.3 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 794605 | the catalogue value is the Centennial USCGS Ms 7.0 converted; ISC-GEM lists a direct Mw from a published moment |
| 1974-01-02 10:42 | mw | 7.3 | 7.0 | 0.4 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 752200 | the catalogue value is the Centennial ABE1 mB 7.1 converted; ISC-GEM lists a direct Mw from a published moment |
| 1974-08-18 10:44 | mw | 7.1 | 6.9 | 0.2 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 738898 | the catalogue value is the Centennial NEIS Ms 7.1 converted; ISC-GEM lists a direct Mw from a published moment |
| 2010-02-27 08:25 | mw | 7.0 | 6.3 | 0.52 | ISC-GEM v13.0 (Di Giacomo et al. 2015), catalogue entry 14869030 | the catalogue value comes from CSN ML 6.8 alone, outside the fitted range; ISC-GEM proxy Mw 6.32, ISC and NEIC mb 6.1 |
| 2011-01-07 04:55 | mw | 6.6 | 5.7 | 0.1 | ISC Bulletin, GUC MW, event 15908420 | the catalogue value comes from CSN ML 6.8 of an event 307 km deep; CSN moment magnitude 5.7 (also in Potin et al. 2024), ISC and NEIC mb 5.1 |

Notes on these:
- **Ten of the thirteen Mw proposals undo an effect of the rerun of today.** With the Centennial first, a converted Abe mB, Ms or untyped value now stands where ISC-GEM lists a direct Mw (from a published seismic moment). I read the ISC-GEM entries, not the papers behind their moments (the ISC-GEM bibliography is not on disk). For 1959-06-14 the moment is in Abe (1982, Table 1), which I read.
- **1967-03-13** (Centennial Berkeley 7.3, ISC-GEM direct 5.7) differs by 1.6; one of the two is wrong and I could not tell which from a third source. The ISC Bulletin values of the event are in the dossier.
- **Aysén 1960** and **Drake Passage 2025** and **1878** rest on sources opened by a sub-agent on the web, not by me: Kanamori and Rivera (2017, full text), the USGS event page us7000pwkn, the CSN table of large earthquakes and the NOAA database. Comte and Pardo (1991) could not be opened, so the Mw 7.9 of 1878 is unchecked.
- **Tarapacá 1543**: the paper says "larger than 7.7"; 7.7 is a lower bound, as for its other bounds in A5.

## 3. Disagreements recorded, no change proposed

- **Converted Centennial values far above the ISC-GEM proxy, no measured value to decide:** 1971-06-17 (25.4° S, 90 km; Abe mB 7.2 → 7.5, ISC-GEM 6.3), 1948-05-11 (7.5, 6.5), 1918-05-20 (7.8, 6.9), 1934-03-01 (7.3, 6.6), 1925-05-15 (7.1, 6.3), 1946-08-02 (7.1, 6.9 against Pasadena 7.9), 1906-12-26 (7.0, 6.9 against 7.9). These set the largest in-slab and northern events before 1976 and need a paper each.
- **Ruiz and Madariaga against a measured Mw:** Papudo 2001-04-09, 7.0 in the paper, 6.65 GCMT and ISC-GEM. Arauco 1975, 7.7 against ISC-GEM direct 7.3. Kept by the decision that the paper is the authority.
- **Valdivia foreshock 1960-05-22 18:56:** catalogue 7.8 (Ruiz and Madariaga, Ms), Lomnitz 7.9, Centennial Mw 7.9; the ISC-GEM 8.72 is a proxy. No change.
- **Santiago 1647:** in-slab for Ruiz and Madariaga (p. 16), crustal source suggested by Lomnitz (p. 370), who calls it unresolved. No hint proposed.
- **Pica 1768 / 1786:** no event of that year in the catalogue at Mw ≥ 6.
- **1562-10-28** (Mw 7.7 in the catalogue): Lomnitz gives no magnitude and says it might have been a storm.
- **Dates:** Lomnitz has Coquimbo on 17 November 1849 (catalogue 17 December) and Casablanca on 2 April 1850 (catalogue 1851). No second source read.
- **Lomnitz magnitudes** differ from the catalogue by 0.5 or more for 1715 (8 against 7.5), 1751, 1868 (8.5 against 9.0) and 1877 (8 against 8.9); the last three follow Ruiz and Madariaga.
- **Chillán 1939 depth:** 60 km (Lomnitz), 80 km (Leyton et al. 2009b), 80–100 km (Barrientos 2018). The catalogue has none; the hint is in-slab.
- **1919-03-02 03:26:** the Centennial epicentre used (41.4° S, 72.2° W, flagged as a poor solution) is 500 km from the ISC-GEM one (43.8° S, 78.3° W). **1918-12-04:** the Centennial epicentre used is at 73.5° W, west of the trench, against 70.65° W in Ruiz and Madariaga's figure.
- **1604-12-01 and 1639-12-01** (La Serena, both Mw 7.4, nearly the same epicentre) are not in Lomnitz; possibly one event entered twice.
- **Drake Passage 2025-05-02:** depth fixed at 10 km by the USGS; reverse mechanism. The 13:09 event exists (two aftershocks 28 s apart in ComCat).
- **1993-05-24 23:51:** two events 5.5 s and 24 km apart at 220 km depth, both in ISC, ISC-EHB, ISC-GEM and the Centennial; kept as two.

## 4. Patterns across many events (reported, no rule changed)

1. **Converted Centennial magnitude against ISC-GEM direct Mw.** In the whole catalogue 38 events take a converted Centennial value where ISC-GEM has a direct Mw; 21 differ by 0.2 or more. A rule "before 1976 a direct Mw of ISC-GEM goes before a converted Centennial value" would replace ten of the proposals above.
2. **Converted Abe mB reads high:** a mean 0.39 above ISC-GEM on the 16 events of the domain with both.
3. **CSN moment magnitude listed as `GUC MW` in the ISC Bulletin is not in the reference family** (only `GUC Mwr` is). 343 converted events of Mw ≥ 4.5 have one; 66 differ from it by 0.5 or more (the 2011-01-07 case is one).
4. **CSN ML of deep or very large events** is far above mb (2011-01-07: ML 6.8, mb 5.1, 307 km; 2010-02-27 08:25: ML 6.8, mb 6.1).
5. **Legacy USGS WCMT tensors of 2010** are chosen before the GCMT tensor of the same event for four events and carry wrong moments (`review/mech_mw_differs`); the GCMT tensor exists for each.
6. **Before 1964 the Centennial epicentre is used even where its solution is flagged poor** (XEQ).

## 5. Events still without depth after A6

324 selected events of Mw ≥ 6 have no measured depth (111 before 1904, 202 in 1904–1963, 11 from 1976; 96 of Mw ≥ 7). No depth is proposed for any. 20 have a class hint from the literature:

| date | lat | Mw | hint | source |
|---|---|---|---|---|
| 1615-09-17 | -19.1 | 7.5 | interface | Ruiz and Madariaga (2018) |
| 1730-07-08 | -33.0 | 9.0 | interface | Ruiz and Madariaga (2018) |
| 1751-05-25 | -36.8 | 9.0 | interface | Ruiz and Madariaga (2018) |
| 1819-04-11 | -27.9 | 8.5 | interface | Ruiz and Madariaga (2018) |
| 1837-11-07 | -43.1 | 8.6 | interface | Ruiz and Madariaga (2018) |
| 1868-08-13 | -17.1 | 9.0 | interface | Ruiz and Madariaga (2018) |
| 1877-05-10 | -20.6 | 8.9 | interface | Ruiz and Madariaga (2018) |
| 1880-08-15 | -31.1 | 7.5 | interface | Ruiz and Madariaga (2018) |
| 1906-08-17 | -32.4 | 8.2 | interface | Ruiz and Madariaga (2018) |
| 1918-12-04 | -27.3 | 7.8 | interface | Ruiz and Madariaga (2018) |
| 1922-11-11 | -29.0 | 8.5 | interface | Ruiz and Madariaga (2018) |
| 1927-04-14 | -32.5 | 7.2 | in-slab | Ruiz and Madariaga (2018) |
| 1928-12-01 | -35.1 | 7.7 | interface | Ruiz and Madariaga (2018) |
| 1939-01-25 | -36.3 | 7.8 | in-slab | Ruiz and Madariaga (2018) |
| 1943-04-06 | -31.3 | 7.9 | interface | Ruiz and Madariaga (2018) |
| 1949-12-17 | -54.0 | 7.8 | crustal | Lomnitz (2004) |
| 1949-12-17 | -54.0 | 7.8 | crustal | Lomnitz (2004) |
| 1958-09-04 | -33.8 | 6.3 | crustal | Ruiz and Madariaga (2018) |
| 1960-05-22 | -38.1 | 7.8 | interface | Ruiz and Madariaga (2018) |
| 1960-06-06 | -45.7 | 7.2 | crustal | Ruiz and Madariaga (2018), p. 50; Cabello et al. (2025), Table 7 |

For the other 304 nothing was found in the papers read. Full list: `A6/no_depth.csv`.

## 6. References

Read (to add to `REFERENCES.md` where missing):
- Abe, K. (1982). Magnitude, seismic moment and apparent stress for major deep earthquakes. J. Phys. Earth 30(4), 321–330. doi:10.4294/jpe1952.30.321. New.
- Lomnitz (2004), Ruiz and Madariaga (2018), Di Giacomo et al. (2015), Engdahl and Villaseñor (2002): already listed.

Read by a sub-agent on the web, to be opened once by Pablo or in a later session before citing:
- Kanamori, H., Rivera, L. (2017). An Mw = 7.7 slow earthquake in 1960 near the Aysén Fjord region, Chile. Geophys. J. Int. 211(1), 93–106. doi:10.1093/gji/ggx292.
- USGS ComCat event us7000pwkn (Drake Passage, 2025-05-02).
- CSN, "Grandes terremotos en Chile", csn.uchile.cl/sismologia/grandes-terremotos-en-chile; NOAA NCEI significant earthquake database, event 2253.

† Not read:
- Comte, D., Pardo, M. (1991). Reappraisal of great historical earthquakes in the northern Chile and southern Peru seismic gaps. Nat. Hazards 4, 23–44. doi:10.1007/BF00126557.
- Soloviev and Go (1975), quoted in the NOAA tsunami event 1090.
- The papers behind the ISC-GEM direct moments; Wyss (1970), the source of Abe's moments for 1957 and 1959; Kausel and Campos (1992); Beck et al. (1998).

## 7. Second pass: the five open large events (13 Nov, later)

Read by me on the page images: Abe and Kanamori (1979, Table 2) and Astiz and Kanamori (1986, pp. 1617–1620). Read by a sub-agent: Astiz (1987, PhD thesis; the paper Astiz et al. 1988 could not be opened), the CaltechDATA transcription of Abe (1981, Table A-II), the CSN table. Not opened: Abe (1981) itself, Pacheco and Sykes (1992), Kelleher (1972), Malgrange and Madariaga (1983).

**No seismic moment was found for any of the five, so none of their magnitudes can be settled by the rule of A6.** What the papers give is depth and setting:

| event | catalogue Mw | what was found | proposed |
|---|---|---|---|
| 1971-06-17, 25.4° S, 90 km | 7.5 (Abe mB 7.2) | normal fault 2/70/−104 at 93 km, down-dip tension (Astiz 1987, sub-agent); CSN Ms 7.0; no moment | class hint in-slab |
| 1948-05-11, 17.4° S | 7.5 (Abe mB 7.4) | 70 km, M 7.3, mB 7.4 (Abe and Kanamori 1979, Table 2); no moment, no mechanism | nothing |
| 1918-05-20, 28.9° S | 7.8 (Abe mB 7.6) | 80 km (depth of Gutenberg and Richter), M 7.5, mB 7.6, listed as intermediate depth (same table); not in Abe's shallow list; CSN Ms 7.9 | class hint in-slab |
| 1934-03-01, 40.9° S | 7.3 (Abe mB 7.3) | 120 km from pP−P at nine stations and sS−S; steep normal fault 12/80/−60 preferred; Ms 7.1; no moment (Astiz and Kanamori 1986) | depth 120 ± 20 km, class hint in-slab |
| 1925-05-15, 25.5° S | 7.1 (Abe Ms 7.1) | Ms 7.1, mB 7.1, 50 km (Abe 1981 transcription, CSN table); no moment | nothing |

Consequences to weigh before accepting:
- **The magnitudes stay as the rerun of today left them**, 0.5–1.2 above the ISC-GEM proxies. For each event two families disagree: Abe's and Gutenberg and Richter's values (7.1–7.6), and the Ms that ISC recomputed from station amplitudes (6.3–6.8, from 3 to 9 stations). Nothing read decides between them.
- **Depth feeds the mB conversion.** 1918-05-20 and 1934-03-01 are converted with the shallow equation because the catalogue has no depth for them. If the 120 km of 1934 is accepted, the next run of `magnitude.py` converts its mB 7.3 with the intermediate-depth equation: Mw 7.6 instead of 7.3. As an intermediate-depth event 1918-05-20 would be 8.1 instead of 7.8, and 1939-04-18 (100 km in Abe and Kanamori's table, no depth in the catalogue) 7.6 instead of 7.3; no depth is proposed for these two, because the depths are Gutenberg and Richter's.
- These events are intermediate-depth, and normal-faulting where a mechanism exists, so they set the largest in-slab magnitudes before 1976: 7.8 (1918, 1929), 7.5 (1971, 1948).

**Found on the way, in Astiz and Kanamori (1986):**
- **1971-05-08, 42.3° S, 157 km:** seismic moment 8.0 × 10^26 dyn cm, "Mw = 7.2" (p. 1618). The catalogue has 6.0, the ISC-GEM proxy from mb 5.85. Proposed: Mw 7.2. The event was below the A6 selection and was added.
- **1949-04-20, 37.6° S:** moment 6.0 × 10^26 dyn cm (Mw 7.1), depth 63 km from waveforms, normal fault 350/70/−130 (p. 1619). Proposed: Mw 7.0 → 7.1, class hint in-slab. The catalogue depth is 57.7 km (ISC-GEM), kept.

The 1971-05-08 case is a seventh pattern for section 4: **an intermediate-depth event of 1964–1975 with an ISC-GEM proxy from mb can be more than one unit low.** Not searched systematically.

References added by this pass. Read: Abe, K., Kanamori, H. (1979). Temporal variation of the activity of intermediate and deep focus earthquakes. J. Geophys. Res. 84(B7), 3589–3595. Astiz, L., Kanamori, H. (1986). Interplate coupling and temporal variation of mechanisms of intermediate-depth earthquakes in Chile. Bull. Seismol. Soc. Am. 76(6), 1614–1622. Read by a sub-agent: Astiz Delgado, L. (1987). PhD thesis, Caltech, doi:10.7907/278K-HZ75; CaltechDATA doi:10.22002/D1.1170 (Abe 1981, Table A-II). † Not read: Astiz, Lay and Kanamori (1988, PEPI 53, 80–166); Abe (1981, PEPI 27, 72–92); Pacheco and Sykes (1992).
