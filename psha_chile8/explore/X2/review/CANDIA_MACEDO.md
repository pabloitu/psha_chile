# Candia and Macedo (2026): check against our homogenization (2026-11-11)

Candia, G., Macedo, J. (2026). A homogenized and declustered earthquake catalog for continental Chile. SRL, doi:10.1785/0220250449. PDF in `refs/catalogs/candia_macedo_2026.pdf`; supplement xlsx (253 609 records with group, priority, Mw, mechanism class and four declustering flags) read by `r_candia_read.py`, checked by `r_candia.py` with the X2 checks. Box 15–60° S, 60–80° W for both catalogues; their retained records (GK flag ≠ 1); ours INV-W linear mean.

## What they do

- 12 sources (ComCat, GCMT, ISC-GEM, ISC Bulletin, CSN Zenodo, IGP, ANSS, GHE, NOAA, Centennial, SISRA, SARA), 1471–2025, 15–60° S.
- Duplicates: time-sorted single pass, each record compared only with its predecessor, windows by era (after 1990: 30 s, 100 km, ΔM 0.75). The record with the lowest priority score is kept. Source rank: ComCat > GCMT > ISC-GEM > ISC Bulletin > CSN > …
- Magnitudes: any value typed Mw in ComCat, ISC-GEM or the ISC Bulletin is kept unchanged. Otherwise a depth-dependent hierarchy (Mw > Ms > mb > ML > Mc shallow; mb before Ms deeper) and Mw-on-native regressions "following Weatherill et al. (2016)", from about 4 000 pairs (Table 6; e.g. ComCat mb: Mw = 0.994 mb + 0.179, 469 pairs). About 16 000 Md and 7 300 coda-magnitude records are dropped rather than converted.
- Classification: Slab2 geometry, then focal-mechanism consistency (1 843 changed), then tsunami evidence (65 historical events to interface; Table S1).
- Declustering: Gardner–Knopoff, Reasenberg (6 parameter sets), Poulos et al. (2019), Zaliapin–Ben-Zion, compared; flags for all four in the file.

## Results of our checks on their catalogue

| check | Candia–Macedo | ours (INV-W linear mean, same box) |
|---|---|---|
| GR on Mw 5.0–6.5, 1976–2026: predicted / observed N(≥ 7) | 14.5 / 50 = **0.29** (declustered 0.39) | 40.3 / 41 = 0.98 (declustered 1.01) |
| same, Mw 6.5–7.0 | 55.6 / 101 | 91.2 / 97 |
| b on 5.0–6.5 | 1.37 | 1.03 |
| per family N(≥ 7), pred / obs | interface 7.8 / 30, in slab 3.3 / 9 | 22.4 / 20, 13.8 / 12 |
| declustered M ≥ 5 rate, 1976–89 → 2011–26 | 94 → 67 /yr (−29 %) | 47 → 50 /yr |
| declustered M ≥ 5.5 rate | 22.4 → 17.9 /yr | 16.2 → 16.6 /yr |
| events per 0.1 bin, 1976–99, Mw 4.7 / 4.8 / 4.9 / 5.0 / 5.1 | 251 / 1 321 / 220 / 1 167 / 142 | 488 / 454 / 316 / 298 / 273 |
| Aki b against floor, 2011–26, 4.8 → 5.2 | 1.21, 0.94, 1.06, 0.94, 1.00 (comb) | 0.92, 0.93, 0.92, 0.89, 0.88 |

Event by event (their M ≥ 4.6 since 1976, matched to ours within 30 s / 100 km; 71 % matched):

| their Mw | median theirs − ours |
|---|---|
| 4.6–5.1 | +0.21 (13 187) |
| 5.0–5.5 | +0.10 (4 897) |
| ≥ 5.5 | 0.00–0.01 |

By source at Mw 4.6–5.5: ComCat mb +0.22 (8 045 events, the forward-fit bias); CSN "mw" +0.27; SARA "mw" +0.42 and SISRA "mw" +0.36 (non-moment magnitudes passed through as Mw); GCMT Ms +0.27. ComCat, ISC-GEM and ISC-Bulletin Mw agree with ours to 0.00.

Duplicates left in: 275 of our events match two or more of their retained records. Clear cases, same event a few seconds apart and both kept:
- 1985-03-04 00:32 M 7.4 (ComCat and ISC-GEM, both classed crustal; this record also appears twice in their Table S4).
- 1987-03-05 09:17 M 7.4/7.5 (GCMT Ms and ISC Bulletin).
- 1988-07-28, 2003-07-27, 2007-04-02, 2009-04-17.
- Several Maule aftershocks.

Comparing only with the predecessor misses a duplicate as soon as another record falls between the two copies, which is common in sequences. That also inflates their observed M ≥ 7 count (50 against our 41 in the same box).

## Verdict

**Don't use it as the catalogue.** At Mw ≥ 5.5 the two agree event by event, so the large events are not the problem. Below 5.5 their Mw is 0.1–0.2 too high, and that is the range that sets a and b at a 4.5–5.0 floor. The causes:
- the forward regression on an incomplete Mw reference (the same failure as X1 M0 and Cabello);
- non-moment magnitudes from SARA, SISRA and CSN passed through as Mw;
- no dithering, so the conversions comb the 0.1 bins;
- Md and coda events deleted instead of converted;
- duplicates left in sequences.

The result fails the large-event test at 0.29 and drifts 29 % in rate. Ours passes both.

**What it gives us:**
1. **A strong argument for the paper.** The most recent published Chilean catalogue still shows the forward-regression bias. A one-paragraph comparison (the table above) shows why the inverse step is needed, without criticising anything but the method.
2. **An independent check for A7.** Their classification (geometry + mechanism + tsunami) can be compared event by event once our A7 classes exist. Their Table S1, tsunamigenic events 1570–2025 with probable/definite occurrence, is worth adopting for historical interface classification (cite it).
3. **Declustering sensitivity.** They compare GK, Reasenberg, Poulos and Zaliapin–Ben-Zion on Chilean data. Useful for the open DECISIONS item on rate convention and for the tornado; their flags could be reused only after their magnitudes and duplicates are replaced, so cite the comparison rather than the flags.
4. **Coverage north of Arica.** Their box reaches 15° S (IGP for southern Peru). Check that our catalogue region covers what the Arica and Iquique hazard needs.

**What not to take:** the source rank (ComCat first takes its preferred magnitude, often mb), the predecessor-only duplicate search, the Table 6 relations.
