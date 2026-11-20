# CAT session

Finished briefs and reports: `orchestration/archive/CAT_1.md` (CAT_01: `cat-02`), `orchestration/archive/CAT_2.md` (CAT_02: classification, `cat-04` / `cat-05`).

## Brief CAT_03 (20 Nov): literature for the catalogue

**Goal:** the open literature points of the catalogue settled from papers that were read, through the overrides file (D-CAT-17), and the references in order; then the catalogue built and classified again (an update, D-CAT-01: a build run and a classified run).

**Read first:** `psha_chile9/CLAUDE.md`; in `orchestration/DECISIONS.md` D-CAT-17, 19, 20, 23 and D-CLS-01, 02; the CAT_02 report, "Requests for other sessions" (literature) and "Questions" 4 (`orchestration/archive/CAT_2.md`); `runs/catalog/cat-05/m7_by_rule.csv`; `docs/REFERENCES.md`.

**Tasks:**
1. First, one list for Pablo of every paper this brief needs that is not in `refs/` (from the CAT_02 report: Giovanni et al. 2002, Vigny and Klein 2022, Martinic 1988, Ammirati et al. 2020, Comte et al. 1986, Beck et al. 1998, Christensen and Ruff 1987, Thouret et al. 2002, Greve 1964, Montessus de Ballore 1911–1916, Abe 1981, Gutenberg and Richter 1954, Duda 1963, the supplement table S1 of candia_2026; for the points below: Pica 1768, Taltal 1887, Magallanes 1907, the 1861 Mendoza BSSA paper, Salomon et al. 2013; Stallone and Spassiani 2026, Gardner and Knopoff 1974), each with the reason. Wait for Pablo to place what he can.
2. With what is in `refs/`:
   - a. Pica 1768, Taltal 1887, Magallanes 1907 (D-CAT-20): did they happen, date, place, Mw with σ, class;
   - b. 1861 Mendoza (D-CAT-19): the BSSA paper;
   - c. the Mw of 1821 and 1600-02-28 (both interface by the Mw ≥ 8 rule; 1821 is Ms 7.0 in comte_1991 p. 34; 1600-02-28 is in the days of the Huaynaputina eruption);
   - d. the 49 events of Mw ≥ 7 still classed by rule (`m7_by_rule.csv`), the 32 with nothing in the papers first.
   Each finding a proposed overrides row (property, value, reference, page, reason) or "not settled".
3. References: rows in `docs/REFERENCES.md` for every paper read or placed; the three PDFs of CAT_02 renamed to the key style (`comte_1991`, `dorbath_1990`, `benavente_2022`) and every citation of the old names in the overrides file and the docs changed with them (CAT_02 question 4).
4. After Pablo accepts rows: append them to `data/raw/catalog/manual/overrides_A6.csv`, build and classify again (`cat-06`, `cat-07`), and list what changed against `cat-05`.

**Decided with Pablo in the session:** the rows, one event or group at a time, with a recommendation; an event the papers do not settle stays by rule.

**Out of scope:** no change to the rules; the calibration (CAT_04, after the STATS fits); figures.

**Time:** reading; the rebuild about one minute.

**Done when:** the list of task 1 given; a–d settled or listed as not settled; REFERENCES rows and renames done; `cat-07` if rows were accepted.

**Report:** below this brief, with the headings of CLAUDE.md.

## Report CAT_03 (20 Nov)

### Done
- Task 1: the list of 20 missing papers was given to Pablo. Of these, ammirati_2020 and the candia_2026 supplement were placed. All the others are still missing.
- Task 2, from the papers in `refs/`:
  - a. Pica 1768 settled and added (rows below). Taltal 1887 not settled: ruiz_2018 p. 45 only names it, from Montessus (not read). Magallanes 1907 not settled: no paper in `refs/` mentions it (lomnitz_2004 and ammirati_2020 p. 1 cover only 1879 and 1949).
  - b. 1861 Mendoza not settled: salomon_2013 not placed; it stays as it is.
  - c. 1821: Mw 7.0 ± 0.3 from comte_1991 p. 34 (Ms 7.0, 38 km rupture); the 8.2 is SARA from CERESIS with no basis (bravo_2026 p. 50), and the event is not among the great events of dorbath_1990. Now classed by the share rule: split, 96 % in-slab. 1600-02-28 not settled (thouret_2002 not placed).
  - d. No new rows. None of the 49 events is in table S1 of the candia supplement (tsunami events). Candia's own classes come from a depth rule, not from a paper, so they do not settle a class. The 49 stay by rule.
- Task 3:
  - Renamed in `refs/`: `comte_pardo_1991` → `comte_1991`, `dorbath_etal_1990` → `dorbath_1990`, `benavente_etal_2022` → `benavente_2022`, `ammirati_etal_2020` → `ammirati_2020`, and the supplement files to `candia_2026_supp_a.docx` / `candia_2026_supp_b.xlsx`.
  - REFERENCES: the comte_1991 row updated (it was "no PDF"), rows added for dorbath_1990, benavente_2022 and ammirati_2020, and the supplement added to the candia_2026 row.
  - The overrides file cites authors and years, not file names, so no citation needed changing. The old names remain only in `orchestration/archive/CAT_2.md`, which was not edited.
- Task 4: 7 rows appended to `overrides_A6.csv` (6 for Pica, 1 for 1821).
  - New property use: `exists = true` on an id that no source has now adds the event, built from its time, lat, lon, mw and class_hint rows (`build.added`, test `test_added_event_from_overrides`; 4 tests pass).
  - Built and classified again.
- Changes against `cat-05`:
  - One new event, cl17680101000000 Pica: Mw 7.7 ± 0.5, in-slab by the literature, assigned depth 101 km (D-CLS-02).
  - One change, cl18210710130000: Mw 8.2 → 7.0, interface (great_no_depth) → split by nodepth_share (w_inslab 0.96, w_crustal 0.04).
  - Nothing else changed. Mw ≥ 7 by rule: still 49 (1821 stays in the list, Pica is not in it).

### Outputs (run ids, paths)
- `runs/catalog/cat-06` (build), `runs/catalog/cat-07` (classified; reads `cat-06`); `added_events.csv` in `cat-06`.
- `config/catalog.yaml`: run ids cat-06 / cat-07.
- `data/raw/catalog/manual/overrides_A6.csv`: 7 rows; `src/psha9/catalog/build.py` (`added`); `tests/test_catalog.py`.
- `docs/REFERENCES.md`; the renamed files in `refs/`.

### Figures to look at (paths, and what to compare with)
- None (out of scope).

### Decisions with Pablo (in his words)
- Pica 1768, as in-slab, Mw 7.7 ± 0.5, at Pica: "Yes, add it".
- 1821: "yes, Mw 7.0 for 1821".
- Interface segments north of Los Vilos (Addenda 1–4): "PB is most likely wrong, also we wont get statistics"; "I'm in favor of all 19-23, since they match with RM"; south of Los Vilos unchanged ("happy ... from los vilos to Arauco and Arauco southward"); "keep 26 and write it in the report". Result (Addendum 5): 15.5 | 19.1 | 23.3 | 26 | 29.9 | 32 | 37 | 45.55° S.
- Drawing: "ok, perpendicular to the trench".
- Why two branches (Pablo, 20 Nov): geometry can inhibit, albeit not prohibit, multisegment ruptures (Herrera, Crempien, Cembrano and Moreno 2024); neither the segmented nor the non-segmented model captures that behaviour, so the two branches are end-members. PSHA could capture it with rates for the different rupture extents, but those are hard to get without synthetic catalogues. 1730 is the argument.

### Questions for Pablo
1. Taltal 1887, Magallanes 1907, 1861 Mendoza, 1600-02-28 and the 49 events still need Montessus, Greve, Martinic, Thouret, salomon_2013, Abe 1981, Gutenberg and Richter 1954, Beck 1998 and Comte 1986. Recommend: a short literature brief once some of them are placed; until then all stay by rule.
2. The 1821 σ of 0.3 is my own choice (comte_1991 gives none). Recommend: keep.
4. (Answered: perpendicular.) Segment limits along parallels or perpendicular to the trench. Recommend: perpendicular to the trench, through the limit at the trench, down the Slab2 dip direction to the bottom edge. It matters only at Arica: the edge strikes about N36°W at 19.1° S, so a cut along the parallel puts the down-dip end of the limit about 120 km off; elsewhere the trench strikes 3–10° from N and the two differ by 9–28 km (Addendum 5).
3. cat-05 has three entries for 1600-02-19 (02:00, 10:00 and 16:00, Mw 7.9 and 7.1, at nearly the same place). They may be duplicates. Recommend: check them in the next literature brief, with thouret_2002.

### Requests for other sessions
- Orchestrator: D-CAT-01 current run `cat-07`. D-CAT-20: Pica added; Taltal 1887 and Magallanes 1907 not settled. D-CAT-19: 1861 Mendoza still waits for its paper. D-CAT-23: the Mw of 1821 is settled (7.0) and 1600-02-28 is not. Overrides may add an event (`exists = true`). `data/raw/README.md`: 7 rows.
- STATS (Pablo, 20 Nov): a trial, not used, in `trials/segments_23/`: the interface segment limit moved from 26 to 23° S (Mejillones LCZ, metois_2016 p. 1438–1439; 26° S is no LCZ there), on a copy of the footprints (the frozen shapes untouched). For the two changed segments, against the 26° S fits: events, Mc(t), b, rate, Mmax, share of the interface moment, and whether b differs between them.
- DATA (for the orchestrator to brief; Pablo, 20 Nov): new interface footprints for the segments of Addendum 5, 15.5 | 19.1 | 23.3 | 26 | 29.9 | 32 | 37 | 45.55° S, with the interface extended north from 17.1 to 15.5° S (changes D-DAT-01 / D-IF-03; whether in-slab and crustal follow is open), and a basemap north of 17° S. Limits drawn perpendicular to the trench, not along parallels (Addendum 5, question 4).
- STATS: read `cat-07`. 1821 is no longer a Mw 8 interface event. The Pica event (Mw 7.7, in-slab, 1768) sits before any completeness period that would include it.

### Learnings (proposed lines)
- Candia's catalogue classes come from a depth rule, and only its table S1 (tsunamis) is a literature basis: it settles no event that our rules have not already set.
- The Mw 8.2 of 1821 goes back to CERESIS without a basis; the one reasoned estimate (comte_1991) is Ms 7.0.

### Left to do
- The events listed in Question 1, when their papers are placed.
- `docs/methods/CLASSIFICATION.md` and `data/raw/README.md` do not yet mention the `exists = true` row type.

### Addendum: interface segment limits, the literature (20 Nov; trial, not used)
Answer to the STATS addendum (`orchestration/STATS.md`, Addendum 1–2). A proposal for the orchestrator; no shape or run changed. Map: `trials/segment_limits/seg_limits_map.png` (script and the GEM interface edges in the same folder). The basemap ends at 17° S.

1. **Published basis of each limit.** These are the low-coupling zones (LCZs) of metois_2016, read from Fig. 3 p. 1437:
   - Strong LCZs: Iquique 20.3–20.7, Mejillones 22.8–23.3, Baranquilla 27.5–28.3, La Serena 29.3–30.6, San Antonio 33.1–33.9, Arauco 37.2–38.0° S.
   - Weak ones (p. 1438–1439, "model-dependent"): Arica ~19.0, Los Vilos ~31.9, Constitución ~35.2° S.
   - Taltal 24.5–25.9° S is a gap in their data, not an LCZ (p. 1436).

   The other two zonations:
   - GEM SAM 2016 (`psha_gem/ssm.xml`, i03–i07, at the trench): 16.5, 21.1, 27.0, 33.3, 45.4° S. GEM's reasons for them are not read.
   - Martin (1990), as drawn in poulos_2019 Fig. 1 p. 68 and used by leyton_2009 and bravo_2026 p. 37: about 25 and 35° S. Martin itself is not read.

   Our limits:
   - 37° S: Arauco LCZ.
   - 32° S: Los Vilos (weak LCZ), plus the change in slab geometry and seismicity rate at the same place (metois_2016 p. 1439).
   - 23° S: Mejillones LCZ. Kausel (1986), via ruiz_2018 p. 45: the 1877 rupture did not break south of Mejillones. bravo_2026 p. 39 splits its northern zone into the 1868, 1877 and 1995 segments.
   - 26° S: no published basis found. It lies between Martin's 25° and GEM's 27°, inside the Taltal data gap.
   - 17.1° S and 45.55° S: model-domain limits (D-IF-03), not segment boundaries.
2. **Rupture extents in the north:**
   - 1868: 15.5–19° S (dorbath_1990 p. 576); intensity VIII zone about 16–19° S (comte_1991 p. 28, Fig. 1d); "the rupture seems to have overpassed the Arica bend in 1868" (dorbath_1990 p. 563).
   - 1604: intensity VIII zone about 16.3–18.7° S (comte_1991 p. 25, Fig. 1a), 415–450 km (comte_1991 p. 32; dorbath_1990 p. 560).
   - 1877: intensity VIII zone about 18.8–22.6° S (comte_1991 p. 29, Fig. 1e), L = 420 km (p. 38). Vigny and Klein (2022) give ≤ 250 km (via bravo_2026 p. 41; not read).
   - 1513: only a SISRA epicentre, 17.21° S 72.3° W, and L > 100 km (comte_1991 p. 30–31); its extent is unknown.

   So the boundary the papers use is the coast's "Arica bend", and the 1868 and 1877 ruptures meet at about 18.5–19° S, by the weak Arica LCZ. No paper read uses the trench bend at 19.6° S.
3. **Arica (18.5–17.1° S).** By the literature this stretch is the southern end of the 1868 / 1604 segment, which lies mostly in Peru. Three ways to keep a source there:
   - a. Keep it in the northern Chilean segment, with a limitation. This is the simplest and fits D-DAT-01. The cost: three Mw ≥ 8.7 epicentres of the Peruvian segment fall just south of 17.1° S and are counted in full, which is a large part of why the northern segment has more large events than its fit (STATS: 13.4 observed against 8.0 fitted at Mw ≥ 7, and 3.2 against 1.6 at Mw ≥ 8).
   - b. A southern Peru segment fitted over 15.5–19° S (the box reaches 15.5° S) and applied only south of 17.1° S, with the rate scaled by area and Mmax from 1868 (Mw 8.8, dorbath_1990 p. 576). Needs an exception to D-DAT-01.
   - c. Extend the interface to about 15.5° S. Breaks D-IF-03 ("the exact same latitude, 17.1").
4. **Recommendation:** 23° S with 17.1° S, and Arica handled by (a), with the limitation stated. Option (b) can be tested later as a tornado row.
   - 23° S is the one limit in the north with a published basis.
   - On the fits it is a draw (STATS).
   - The elbow is where the papers put the 1868 / 1877 boundary, but ending the model there removes the source for Arica.
   - 26° S with the elbow is the weakest option: an unsupported limit plus a lost source.


### Addendum 2: candidate segmentations (20 Nov; trial, not used)
Pablo: the 17.1° S end may be overruled if the science supports it; he wants segmentations with a published basis, each on its own map. Map: `trials/segment_limits/seg_proposals_map.png` (script `seg_proposals_map.py`). Counts come from `cat-07`: interface weights summed, no completeness.

**Which segment is "the northern Chile gap".**
- comte_1991 p. 23 (abstract): both the 1868 region (southern Peru to Arica) and the 1877 region (northern Chile) are seismic gaps "in the maturity state". The 1868 region shows notable quiescence.
- ruiz_2018 p. 43: the 2014 Iquique Mw 8.2 occurred "in the middle of Northern Chile seismic gap", the 1877 zone; "Why did the entire seismic gap not fail?" Its slip lies at about 19.5–20.7° S (metois_2016 Fig. 3, p. 1437).
- bravo_2026 p. 41: the slip deficit of the 1877 zone takes 153–219 years to build a Mw 8.8 (Chlieh et al. 2011 and Michel et al. 2023, cited there; not read).
- In short, "the" northern Chile gap is the 1877 segment, about 19–23° S (Arica bend to Mejillones), with 2014 in its middle; its northern and southern ends have not broken.
- The 1868 segment (15.5–19° S) is the other mature gap. 2001 broke its northern part (Giovanni et al. 2002 via bravo_2026 p. 40; extent not read).
- Arica sits where the two meet.

**Candidates** (limits in ° S; the basis of each limit in the addendum above):
- A (ours): 17.1 | 26 | 32 | 37 | 45.55. 26° S has a basis after all: ruiz_2018 p. 43 splits north-central Chile (23–30° S) "for practical purposes", for lack of historical data, into an Antofagasta segment (23–26° S, named after the city at its northern end) and an Atacama segment (26–30° S).
- P1 "two northern gaps": 15.5 | 19 | 23 | 32 | 37.5 | 45.55. The 1868 and 1877 gaps are separate segments, with the limit at their meeting point (comte_1991 Fig. 1, pp. 28–29; dorbath_1990 p. 576; weak Arica LCZ). The middle is as in A but starts at Mejillones. 37.5° S is the centre of the Arauco LCZ.
- P2 "coupling and ruptures": 15.5 | 19 | 23 | 30 | 33.5 | 37.5 | 45.55. P1 plus the La Serena LCZ (30° S; ruiz_2018 p. 43, the north-central region 23–30° S) and the San Antonio LCZ (33.5° S, the northern end of 2010).
- GEM SAM 2016 is shown for comparison: 16.5 | 21.1 | 27.0 | 33.3 | 45.4.

**Data** (Mw ≥ 5 since 1964 / Mw ≥ 7, interface weights): P1 15.5–19: 177 / 13; 19–23: 207 / 13; 23–32: 681 / 24; 32–37.5: 631 / 20; 37.5–45.55: 148 / 16. The two northern segments hold about as many events as the southern one, which is already fitted alone. In P2 the smallest segment is 33.5–37.5, with 422 events and 10 of Mw ≥ 7.

**Recommendation:** P1, with the interface extended to 15.5° S (the box edge) and P2 as the tornado row.
- Reasons:
  - It separates the two gaps the literature names, so each gets its own rate and Mmax: 1868 (Mw 9.0) and 1877 (Mw 8.9, or about 8.5 by Vigny and Klein, not read).
  - Arica keeps a source, and the three Mw ≥ 8.7 events south of 17.1° S stop inflating a Chilean segment.
  - Every limit except the domain ends has a published basis.
- What stays a limitation in every scheme: 1730 (about 30–35° S) crosses 32 and 33.5° S, so long ruptures across limits are left to the full-margin branch.
- Needs:
  - D-DAT-01 and D-IF-03 changed (interface to 15.5° S; whether in-slab and crustal follow is open).
  - New footprints (DATA).
  - A basemap north of 17° S: every raster we have ends at 17° S.
  - The fits again (STATS).

### Addendum 3: northern segmentation, published schemes and ruptures (20 Nov; trial, not used)
Pablo keeps 32° S (Los Vilos) and Arauco southward; only the north is open. Map: `trials/segment_limits/seg_north_maps.png`, script `seg_north_maps.py`. It has nine panels: ours, four published schemes, two hazard models and three proposals. Each panel has the rupture extents beside it on the same latitude scale.

**Rupture extents** (read from ruiz_2018 Fig. 1–2, pp. 38–39, unless stated otherwise), ° S:
- 1868: 15.5–19.2 (dorbath_1990 p. 576 and ruiz_2018).
- 1604: 16.3–18.7 (comte_1991 p. 25).
- 1877: 19.0–22.9.
- 2014: 19.5–20.8, and its aftershock 20.3–21.0.
- 1967: 21.4–22.0. 2007: 21.6–23.1.
- 1995: 23.3–24.6.
- 1966: 24.8–26.2.
- 1922: 26.0–29.9 (bravo_2026 p. 44; the ruiz_2018 figure starts at 28° S).
- 1880 / 1943 / 2015: 29.9–31.6.
- 1971: 31.1–32.2.
- 1822 / 1906 / 1985: 32.5–34.2.
- 1730: 28.6–36.4.

**Published schemes, read:**
- comte_1991 (p. 23, Fig. 1 pp. 25–29) and dorbath_1990 (pp. 563, 576): two regions, 1868 (southern Peru to Arica, about 19° S) and 1877 (about 19–23° S).
- ruiz_2018:
  - Northern Chile, the 1877 zone, ends at 23° S.
  - North-central, 23–30° S (p. 43), is split into Antofagasta 23–26° S and Atacama 26–30° S.
  - Central Chile, 30–35° S (p. 47).
- metois_2016 (Fig. 3, p. 1437): coupled segments between the low-coupling zones (LCZs):
  - Camarones, 19–20.5° S.
  - Loa, 20.5–23° S.
  - Paranal and Chañaral, 23–27.9° S, with the Taltal data gap at 24.5–25.9° S (p. 1436).
  - Atacama, 27.9–30° S.
  - Metropolitan, 30–33.5° S.
- shrivastava_2019 (Sci. Rep. 9:4403, read online, partly): the most curved part of the margin, near Arica–Pisagua, acted as a barrier for both 1868 and 1877. No latitudes are stated in the text.

**Published, abstract only (not read; PDFs needed):**
- Métois et al. 2013 (GJI 194, 1283–1294, doi 10.1093/gji/ggt183): the 1877 gap has at least two locked segments, bounded by the Iquique and Mejillones LCZs.
- Métois et al. (GJI): the Atacama coupling paper.
- Klein et al. 2018 (GJI 213, 1924–1933, doi 10.1093/gji/ggy094): a relative coupling low at Taltal splits the Paranal segment (north) from the Atacama segment (south).
- Béjar-Pizarro et al. 2013 (Nat. Geosci. 6): segments controlled by upper-plate coastal structures.
- Victor et al. 2011 (JGR 116, doi 10.1029/2010JB007771): Mejillones is a long-lived segment boundary.
- Molina et al. 2021 (JGR 126, doi 10.1029/2020JB020647): 17 frictional segments for the whole margin.
- Contreras-Reyes and Carrizo 2011 (PEPI 186, 49–58): subducting oceanic features (Iquique Ridge and others) bound ruptures.
- Nishenko 1985 (JGR 90, doi 10.1029/JB090iB05p03589): the classic segments, Mollendo–Arica, Arica–Antofagasta, Coquimbo–Illapel, Valparaíso 32–35° S, and so on.

The open copies were blocked by bot checks or returned 403, and I did not work around them.

**Each northern limit against the ruptures:**
- 19° S: 1868 ends at 19.2° S and 1877 starts at 19.0° S. Comte and Pardo, Ruiz and Madariaga, and Shrivastava agree; weak Arica LCZ.
- 23° S: 1877 and 2007 end at 22.9–23.1° S, and 1995 starts at 23.3° S. Mejillones LCZ; Victor et al. 2011 (not read).
- 26° S: 1966 ends at 26.2° S and 1922 starts at 26.0° S. Ruiz and Madariaga's limit; Klein et al. 2018's Taltal low is nearby (not read).
- 30° S: 1922 ends at 29.9° S and the Illapel events start at 29.9° S. La Serena LCZ.
- 32° S: kept.
- 1730 crosses 30° and 32° S, as before.

**Proposals north of 32° S** (interface Mw ≥ 5 since 1964 / Mw ≥ 7 in `cat-07`):
- P1: 15.5 | 19 | 23 | 32. Segments: 177/13, 207/13, 681/24.
- P2: 15.5 | 19 | 23 | 30 | 32. Segments: 177/13, 207/13, 402/20, 279/4.
- P3: 15.5 | 19 | 23 | 26 | 30 | 32. Segments: 177/13, 207/13, 161/8, 241/13, 279/4. Every limit falls where one rupture ends and the next begins; it is the scheme of ruiz_2018 with the 1868 segment added.

**Recommendation:** P3 for the segmented branch, with b shared among the northern segments and a rate for each. P2 is the alternative if STATS finds 23–26° S or 30–32° S too small to fit.
- P3 gives Antofagasta, the one segment with no known giant earthquake (ruiz_2018 pp. 43–45), its own rate and Mmax, separate from 1922-type Atacama.
- The full-margin branch keeps ruptures like 1730.
- To decide: the orchestrator, after the PDFs above are read.

### Addendum 4: northern segmentation from the papers read (20 Nov; trial, not used)
Pablo placed the papers; 26 were copied from his Downloads into `refs/` under key names, with REFERENCES rows. The segmentation papers below were read in full by three reading agents; the figure values are good to about ±0.1–0.3°. Contreras-Reyes and Carrizo 2011 and Nishenko 1985 are still missing.

Map: `trials/segment_limits/seg_north_maps2.png` (script `seg_north_maps2.py`). It has 13 panels: ours, eight published schemes, two hazard models and three proposals, each beside the same rupture bars.

**Published limits north of 32° S** (° S; LCZ = low-coupling zone):

| Source | Limits or bands | Kind |
|---|---|---|
| comte_1991, dorbath_1990 | 19 (1868 / 1877), 23 | historical ruptures |
| ruiz_2018 pp. 43, 47 | 19, 23, 26 ("for practical purposes"), 30 | historical ruptures |
| metois_2013 pp. 7–8 | Camarones 18.3–20.2; Iquique LCZ 20.2–20.8; Loa 20.8–22.5; Mejillones LCZ 22.5–23.3; Paranal 23.3– | GPS coupling |
| metois_2014 pp. 8–9 | Chañaral 25.5–27.2; Baranquilla LCZ 27.2–28.2; Atacama 28.2–29; La Serena LCZ 29–30.8 | GPS coupling |
| klein_2018 pp. 1925–1931 | Paranal 23–25; Taltal LCZ 25.1–25.6 (bay at 25.5); Chañaral 25.6–27.2 | GPS coupling |
| molina_2021 p. 18, Fig. 8 | 19.1, 20.35, 21.6, 23.6, 25.2, 27.5, 29.8, 31.4; master barriers 19.1, 23.6, 25.2, 29.8 | gravity, friction, locking |
| victor_2011 p. 3 | Iquique segment ~18–23.2; Mejillones boundary 23.2; Antofagasta 23.2–25 | structure, terraces |
| bejarpizarro_2013 pp. 463–465 | Mejillones 23.1–23.5; Arica bend (~18.5) "possibly" a barrier | InSAR, GPS, structure |
| vigny_2022 pp. 11–14 | Arica bend 18–19, poorly coupled; Camarones 18–20; Iquique LCZ ~20.5; 1877 = Loa only | historical sources |
| giovanni_2002 p. 14-4 | south-central Peru segment 12–19 (2001 and 1784); "gap?" 18.1–19.9 | intensities, aftershocks |

From molina_2021 p. 19: all 13 ends of the 7 instrumental ruptures lie within 25 km of one of its boundaries.

**Which gap is "the northern Chile gap".**
- In the older literature it is the 1877 zone, about 19–23° S (comte_1991; ruiz_2018 p. 43).
- vigny_2022 (pp. 1, 11–14) and metois_2013 (p. 8) put 1877 at only 20.5–22.5° S, the Loa segment, about Mw 8.5. They call the idea that 1868 and 1877 were contiguous a misconception.
- So the unbroken pieces are:
  - Loa: the shallow part above 2007.
  - The Arica bend and Camarones, 18–19.5° S: between 2001 and 2014, and unbroken since 1868 (giovanni_2002 "gap?" 18.1–19.9).
  - The shallow Paranal segment: 1995 did not reach the trench (metois_2013 p. 8).
  - The 1922 zone: klein_2018 p. 1925 calls the Atacama region (25–30° S) a gap.
- A joint Camarones + Loa rupture "cannot be ruled out" and would approach Mw 9 (metois_2013).
- bejarpizarro_2013 (pp. 465–466) gives the deficit since 1877 as about Mw 8.6.

**The northern limits, checked:**
- **Mejillones, 23.3° S:** the strongest limit. Every source has it; it has persisted for more than 400 kyr (victor_2011); 1877, 2007 and 1995 all end or start there.
- **La Serena, 29.9° S:** coupling (Métois, Klein), Molina's master barrier, and the ends of 1922, 1943, 1880 and 2015.
- **Taltal, 25.4° S rather than 26° S:**
  - Molina's master barrier is at 25.2° S and the Klein / Métois 2014 LCZ at 25.1–25.6° S.
  - 1995 ends at about 25.0° S and 1966 at 25.75° S.
  - 1922 starts at about 26.1° S (klein_2018 Fig. 1b; the text, p. 1931, says it stopped at Taltal).
  - The 26° S of ruiz_2018 is a practical split.
- **Arica, 19.1° S:**
  - For: Molina's master barrier, the 1868 / 1877 limit (comte_1991), and the Arica bend in Béjar-Pizarro and in Vigny & Klein.
  - Against: giovanni_2002 sees a gap at 18.1–19.9° S that the limit splits, and the 1604 and 1868 intensity zones run past it.
- **Iquique, 20.5° S, and Baranquilla, 27.7° S:** coupling lows in Métois, Klein and Molina. 1922 and 1819 cross Baranquilla (the super-cycle of metois_2014 p. 9), and the old 1877 extent crosses Iquique.

**Proposals** (interface Mw ≥ 5 since 1964 / Mw ≥ 7 in `cat-07`, from north to south):
- **PA, master barriers:** 15.5 | 19.1 | 23.3 | 25.4 | 29.9 | 32. Segments: 177/14, 241/12, 101/6, 260/13, 285/6.
- **PB, coupling segments:** PA plus 20.5 and 27.7. Segments: 177/14, 133/7, 109/5, 101/6, 139/8, 121/5, 285/6.
- **PC, two northern gaps:** 15.5 | 19.1 | 23.3 | 32. Segments: 177/14, 241/12, 646/24.

**Recommendation:** PA for the segmented branch, PB as a tornado row; the full-margin branch stays at 0.5 and carries ruptures like 1730, 1819 and 1922 across the coupling lows.
- Every PA limit has at least three independent kinds of support: coupling, structure or friction, and rupture ends.
- PA replaces 26° S with 25.4° S and splits 1868 from 1877.
- PB's segments hold 100–140 events each, too few for their own b. PB fits only with b shared across the north and a rate per segment.

**Needs:**
- D-DAT-01 / D-IF-03 changed (interface to 15.5° S).
- New footprints from DATA, and a basemap north of 17° S.
- The STATS fits redone.
- The two missing papers and Molina's Table S1.

**Addendum 4, the last two papers** (read 20 Nov; panels added to `seg_north_maps2.png`):
- **nishenko_1985:**
  - Segments: Mollendo–Arica 17–18° S and Arica–Antofagasta 18–24° S (p. 3589); Copiapó–Coquimbo 26–30° S, the 1796 and 1922 great events (p. 3606); Coquimbo–Illapel 30–32° S (p. 3589).
  - Also a large-event zone, Taltal–Copiapó 25–27° S (p. 3607).
  - The stretch from Antofagasta to Caldera (about 24–27° S) has no known great event; 1877 "may have" ruptured into it, for 650 km (p. 3607). vigny_2022 and metois_2013 later reject that extent.
- **contreras-reyes_carrizo_2011:**
  - The 1868–1877 gap runs from Ilo to Mejillones, 15.5–23.5° S (p. 52). The northern Chile gap, 18.5–23° S, coincides with the subducting Iquique Ridge (p. 51).
  - 1995 is bounded by the south end of the Iquique Ridge to the north and by the Tal-Tal Ridge to the south (p. 52).
  - The Juan Fernández Ridge (~32.5° S) is the northern barrier of 1906 and 1985 and the southern barrier of 1943 (p. 53).
  - Fracture zones (Challenger, Iquique and others) coincide with rupture limits (p. 55).
- **Effect on PA:** none.
  - Both papers support 30° S and 32° S.
  - The Tal-Tal Ridge supports the Taltal limit (PA 25.4° S).
  - Nishenko's 18° S and 24° S are the older, coarser version of the Arica and Mejillones limits.
  - Contreras-Reyes and Carrizo treat 15.5–23.5° S as one gap and give no feature at Arica. That is one more reason the 19.1° S limit is the least certain one in PA.
- **REFERENCES rows:**
  - nishenko_1985: Nishenko, S.P. (1985). Seismic potential for large and great interplate earthquakes along the Chilean and southern Peruvian margins of South America: a quantitative reappraisal. JGR 90(B5), 3589–3615.
  - contreras-reyes_carrizo_2011: Contreras-Reyes, E., Carrizo, D. (2011). Control of high oceanic features and subduction channel on earthquake ruptures along the Chile–Peru subduction zone. PEPI 186, 49–58.

### Addendum 5: segments chosen (20 Nov; for the orchestrator)
Interface segments, in ° S: 15.5 | 19.1 | 23.3 | 26 | 29.9 | 32 | 37 | 45.55. This is PA with Taltal at 26° S, as Pablo decided. The bases of the limits are in Addenda 1–4. The north is compared with Ruiz and Madariaga in `trials/segment_limits/seg_pa_rm.png`.

| Segment | Limits (° S) | Ruptures inside | Basis of the limits |
|---|---|---|---|
| Southern Peru–Arica | 15.5–19.1 | 1604, 1868, 1784, 2001 | 15.5° S: box edge (Ilo, contreras-reyes_carrizo_2011 p. 52). 19.1° S: master barrier of molina_2021 p. 18; the 1868 / 1877 limit (comte_1991 Fig. 1; ruiz_2018 Fig. 1); the Arica bend (bejarpizarro_2013 p. 465; vigny_2022 p. 12) |
| Northern Chile (1877) | 19.1–23.3 | 1877, 2014, 2007 | 23.3° S: Mejillones (metois_2013 p. 7; victor_2011 pp. 3, 17; molina_2021 23.6° S); 1877 and 2007 end there and 1995 starts there |
| Antofagasta / Paranal | 23.3–26 | 1995, 1987, 1966 | 26° S: north end of 1922 and 1819 (metois_2014 p. 2; klein_2018 Fig. 1b; bravo_2026 p. 44); nishenko_1985 p. 3606 (Copiapó–Coquimbo 26–30° S); ruiz_2018 p. 43. The Taltal coupling low (25.1–25.6° S, klein_2018; molina_2021 25.2° S) falls inside the segment |
| Atacama | 26–29.9 | 1922, 1819, 1918, 1946, 1983 | 29.9° S: La Serena LCZ (metois_2014 p. 9; molina_2021 29.8° S); Challenger fracture zone (contreras-reyes_carrizo_2011 p. 55); 1922 ends and 2015 starts there |
| Illapel | 29.9–32 | 1880, 1943, 2015, 1971 | 32° S: kept (Los Vilos; Juan Fernández Ridge, contreras-reyes_carrizo_2011 p. 53) |
| South of 32° S | 32–37, 37–45.55 | unchanged | unchanged (Pablo) |

**Counts** (cat-07; interface events of Mw ≥ 5 since 1964 / Mw ≥ 7): 15.5–19.1: 177 / 14; 19.1–23.3: 241 / 12; 23.3–26: 127 / 8; 26–29.9: 234 / 11; 29.9–32: 285 / 6 (no completeness; STATS recounts).

**Limitations:**
- 1730 (about 28.6–36.4° S, ruiz_2018 Fig. 2) crosses 29.9° and 32° S, so only the full-margin branch can hold it.
- The 19.1° S limit is the least certain: giovanni_2002 sees a gap at 18.1–19.9° S, and contreras-reyes_carrizo_2011 treat 15.5–23.5° S as one gap.
- The 26° S limit and the Taltal low are 70 km apart. 26° S was kept so that the segment is large enough to fit (Pablo).

**Drawing** (question 4): the limits should run perpendicular to the trench, not along parallels.
- It matters at Arica: the edge strikes about N36°W at 19.1° S, so a cut along the parallel moves the down-dip end of the limit by about 120 km.
- Elsewhere the trench strikes 3–10° from N, and the two ways differ by 9–28 km at the bottom edge.
- At 15.5° S the trench strikes about N50°W, so the same applies there.

### Feedback for the orchestrator (CAT_03, 20 Nov; Pablo reviews before the orchestrator)
1. **Catalogue:** the current run is `cat-07`.
   - Pica 1768 was added through a new overrides row type (`exists = true`), and 1821 now has Mw 7.0.
   - Not settled: Taltal 1887, Magallanes 1907, 1861 Mendoza (salomon_2013 not placed), 1600-02-28, and the 49 events classed by rule.
   - For DECISIONS: D-CAT-01 (current run `cat-07`), D-CAT-19, D-CAT-20, D-CAT-23. For `data/raw/README.md`: 7 new override rows.
2. **New literature row, to decide:** 1946-08-02 as interface (metois_2014 pp. 2, 9). It is one of the 49 events still classed by rule.
3. **Interface segments** (`docs/methods/SEGMENTATION.md`): 15.5 | 19.1 | 23.3 | 26 | 29.9 | 32 | 37 | 45.55° S, drawn perpendicular to the trench (Pablo).
   - For DECISIONS: change D-IF-03 (limits) and D-DAT-01 / D-DAT-03 (interface to 15.5° S; whether in-slab and crustal follow is open).
   - Keep segmented and full-margin at 0.5 / 0.5 as end-members (Pablo's argument above; 1730).
4. **DATA brief:** new interface footprints, the segment-limits shape, and a basemap north of 17° S.
5. **STATS brief, after Pablo commits STATS:** fits on the new segments, with b shared where a segment is small; 23.3–26° S is the smallest (127 events of Mw ≥ 5 since 1964).
   - The STATS trials in `trials/segments_23/` are superseded by this proposal.
6. **References:**
   - 28 PDFs placed in `refs/` with REFERENCES rows: 10 with full citations, 18 still "not read".
   - Still to place: herrera_2024; molina_2021 Table S1; Carvajal et al. 2017 (1730); Beck et al. 1998; Thouret et al. 2002; Abe 1981; Gutenberg and Richter 1954; Gardner and Knopoff 1974; Greve 1964; salomon_2013.
7. **LEARNINGS (proposed):**
   - The northern Chile gap is two or three pieces, not one: 1877 was probably only 20.5–22.5° S (vigny_2022, metois_2013), and the Arica bend has not broken since 1868 (giovanni_2002).
   - Segment limits from coupling, structure and rupture ends agree within about 0.5° at Mejillones, Taltal and La Serena. Arica is the least certain.

**Left to do:** wait for Pablo to commit STATS, then return to this session.
