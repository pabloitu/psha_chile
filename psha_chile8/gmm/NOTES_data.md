# GMM residuals: data notes (step 1)

15 Nov 2026. Written from the chat session, before any brief. Nothing here is a decision.
Numbers come from a first pass over the flatfiles and the frozen catalogue; the matching is a quick one (time and distance windows), to be redone properly in the task.

## Files read
- `refs/gmm/Earthquake Spectra - 2026 - Bastías - ...pdf`: Bastías, Montalva, Leyton, Heresi, Domínguez (2026), An extended and updated strong ground-motion database for the Chilean subduction earthquakes, Earthquake Spectra 42:e70032, doi:10.1002/esp4.70032. Data: doi:10.17603/ds2-6gyp-t353.
- `data/ground_motion/`: `Flatfile_chileanEvents_v11.csv` (6 679 events, 28 columns), `Flatfile_chileanSiteStation_v7(1).csv` (524 stations, 27 columns), `Flatfile_chileanRecord_v10.csv` (43 050 records, 50 columns), `README-1.pdf` (field descriptions), `example_read_h5_files_chSGMdb.ipynb`.
- `refs/hazard_chile/Mapa_Amenaza_CSN2026.pdf`, chapter 6 (report pp. 84–105, PDF pp. 102–123) and logic tree (report p. 129).
- `catalog/frozen/2026-11-14/catalog_2026-11-14c.csv`.
- GMM list of the `oq-engine` checkout in the repo root (file names and required parameters only).

## What the paper says (page of the article)
- 43 050 records, 6 679 events, Mw 4.0–8.8, 530 stations, 1985–2024 (p. 1).
- Mw: CSN magnitudes converted with Cabello et al. (2025); duplicates removed with 60 s and 110 km windows (p. 3).
- Mechanisms: GCMT first, then USGS, then CSN (p. 3).
- Class: trench, 60 km slab contour, mechanism and depth; no mechanism: interface within 10 km above / 20 km below the slab (p. 3). Slab2 used (p. 4).
- Rupture: 14 published finite faults (SRCMOD); the rest simulated from centroid or hypocentre, strike and dip, Thingbaijam et al. (2017) dimensions, 5 000 hypocentre positions; Slab2 strike and dip when there is no mechanism (pp. 3–5). Distances: Repi, Rhyp, Rjb, Rrup with a standard deviation (p. 13).
- Vs30: measured profile at 223 stations; otherwise a weighted mean of three proxies (HVSR f0, slope, P-wave seismogram); residual σ about 0.43 ln units (pp. 7–8, Table 2 p. 9). Kappa at 148 stations (p. 9).
- Processing: 4th-order acausal Butterworth; low cut where SNR first exceeds 3, never below 0.02 Hz; high cut 80 % of Nyquist; usable period 1/(1.25 f_lc) (pp. 12–13).
- Intensity measures: PGA, PGV, CAV, Ia, Tm, durations per component; PSa for N, E, Z and RotD00, RotD50, RotD100 (p. 13). The paper says 27 periods; the file has 22 (0.01 to 10 s).

## What the files hold
- Records file: 6 505 events and 480 stations with records. 174 events of the events file have none (its NoRecords column sums to 43 565).
- Periods: 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10 s. RotD50 present and positive for every record at 0.01, 0.2 and 1.0 s. No RotD50 PGA column; PSa(0.01 s) RotD50 stands in (mean ln ratio to the geometric-mean PGA +0.05).
- Usable period ≥ 1 s for 94 % of all records, 98–99 % at Mw ≥ 5; ≥ 3 s for 62 %.
- Vs30 flag (`Vs30Ind` = station `IDPreferedVs30`): 1 measured (223 stations, 13 991 records, 32 %); 2, 3, 5 inferred (25 156, 3 829, 74 records). The README does not explain codes 2, 3, 5, 8.
- Mw source: BM16 4 112, CSN 1 161, CMT 837, USGS 561, ISC 8. Mechanism known for 1 471 events.
- Rupture geometry stored for 14 events only. The simulated planes of the other events are not in the files; only the distances are.
- Station f0 and HVSR amplitude for 478 stations.
- No Ztor, rupture width, Rx, Ry0, Z1.0, Z2.5, forearc/backarc flag, volcanic-path distance, Idini soil type.
- Stations: 17.6–51.7° S, none east of 68.0° W; 3 south of 46° S.

## Match to the frozen catalogue
- 6 675 of 6 679 events matched (4 left, Mw ≤ 5.5, 6 records).
- 12 pairs of flatfile events point to the same catalogue event: the second entry is about 300 s later with the same coordinates. One pair shares 20 stations (Mw 7.7, 3 Apr 2014: 20140403024315 and 20140403024815). Pairs: 20100923163617/164116, 20101125032730/033229, 20101219204805/205303, 20120827003955/004455, 20130907191331/191831, 20140223234002/234502, 20140322125954/130454, 20140403015831/020331, 20140403024315/024815, 20140411085556/090056, 20140424045650/050150, 20140619195942/200442.
- Maule 2010 and Peru 2001 carry an origin time about 65 s late in the flatfile.
- Mw: flatfile minus catalogue, mean +0.08, σ 0.23. 22 events differ by ≥ 0.5 with one side ≥ 5.5. Four flatfile "Mw 7.0–7.1" entries are minutes after the Iquique 2014 and Illapel 2015 mainshocks (20140401235758, 20140402000258, 20150916225915, 20150916231608); the catalogue gives 4.6, 6.0, 6.5, 6.4.
- Class, flatfile against catalogue (events): Inslab 3 128 of 3 225 the same; Interface 1 611 of 2 610 (711 split, 240 in-slab); ShallowCrust 185 of 720 (264 interface, 241 split, 30 in-slab).

## Records per class (catalogue class and Mw; Mw ≥ 5, Rrup ≤ 300 km)
| class | events | records | events with ≥ 3 records | measured Vs30 | events Mw ≥ 6 | events Mw ≥ 7 (records) | records < 50 km |
|---|---|---|---|---|---|---|---|
| interface | 442 | 4 365 | 348 | 57 % | 77 | 16 (291) | 209 |
| in-slab | 388 | 5 126 | 326 | 43 % | 39 | 2 (16) | 23 |
| crustal | 44 | 286 | 27 | 46 % | 10 | 1 (3) | 21 |
| outer rise | 7 | 60 | 5 | 55 % | 1 | 0 | 0 |
| split (no class ≥ 0.8) | 114 | 1 057 | 86 | 57 % | 13 | 0 | 30 |

- In-slab Mw ≥ 7: 1997 Punitaqui (3 records) and 2005 Tarapacá (14).
- Mw ≥ 5 records by year: 186 to 2009, 1 611 in 2010–13, 4 327 in 2014–16, 3 547 in 2017–19, 2 465 in 2020–22, 476 in 2023–24.

## MASCSN26 (CSN 2026) on GMMs
- Data: CSN EVTDB, 1 816 events Mw ≥ 4.5, 13 854 records; own processing (report pp. 84–87).
- Tested: subduction CB15, Idini 2017, Montalva 2017, Youngs 1997, Zhao 2016, Kuehn 2020, Parker 2020, Si 2020, AG20, Arteta 2021; crustal CB08, CB14, Idriss 2008/2014, ASK14, BSSA14, CY14, Arteta 2023, Cauzzi 2014, Bindi 2014, Akkar 2014 (pp. 88–89).
- Scores: LH (Scherbaum et al. 2004), LLH (Scherbaum et al. 2009), multivariate LLH (Mak et al. 2017), area metric (Sunny et al. 2022); PGA, SA(0.3), SA(1), SA(3) (pp. 89–90; Tables 18–26, pp. 93–104).
- Chosen (Table 27, p. 105): interface CB15, Idini, Montalva, Youngs, Zhao 2016 at 0.2; in-slab CB15 0.34, Montalva 0.34, Youngs 0.32; crustal Arteta et al. 2023 at 1.0. Figure 74 (p. 129) labels the crustal model "Arteta et al. 2021"; the text and tables say 2023.
- The report does not say which regional version of AG20, Kuehn and Parker was evaluated.

## GMMs in the repo's oq-engine checkout, by regime (file names)
- Interface and in-slab: AG20, Kuehn 2020, Parker 2020, Si 2020, Montalva 2016/2017, Idini 2017, Abrahamson 2015 and 2018 (BC Hydro), Youngs 1997, Zhao 2006, Zhao 2016, Atkinson & Boore 2003, Arteta 2021, Lin & Lee 2008, Kanno 2006, McVerry 2006, Bahrampouri 2021, Chao 2020, Phung 2020, Hassani & Atkinson 2020, Morikawa & Fujiwara 2013. Interface only: Ghofrani & Atkinson 2014, Atkinson & Macias 2009, Arroyo 2010, Megawati & Pan 2010. In-slab only: García 2005, Jaimes 2020, Manea 2021.
- Crustal: ASK14, BSSA14, CB14, CY14, Idriss 2014, Arteta 2023, Akkar 2014, Bindi 2014, Cauzzi 2014, Kotha 2020, Lanzano 2019, Boore 2020, CB08, Zhao 2006/2016, and others.
- Contreras & Boroschek (2015) has no file there.

## Open
- Papers not in `refs/gmm/`: every GMM paper and the method papers (Scherbaum et al. 2009, Kale & Akkar 2013, Abrahamson & Youngs 1992, Mak et al. 2017, Bastías & Montalva 2016, Contreras & Boroschek 2015).
- Vs30 codes 2, 3, 5, 8: ask the authors or read Supplement S1 of the DesignSafe deposit.
