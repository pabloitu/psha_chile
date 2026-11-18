# Magnitudes: one Mw per earthquake (A5)

State of 14 Nov 2026, run `2026-11-14b`. Methods note for the paper. Code: `catalog/magnitude.py` (fits, assignment; settings at the top) and `catalog/magnitude_check.py` (tests, figures). The run uses the A3 events of 2026-11-11 (204 956 events), the final depths of the same run (`locations_2026-11-14b.csv`) and the corrections of the large-event review (`catalog/overrides_A6.csv`). Tables in `catalog/merged/` (`mw_`, `relations_`, `relations_floor_`, `mw_offsets_`, `mw_tests_`, `mw_sensitivity_`, `mw_synthetic_`, `mw_coverage_`, `mw_histogram_`, all `_2026-11-14b`), figures in `catalog/figs/magnitude/`. A frozen copy of the main tables is in `catalog/frozen/2026-11-14/`.

**Status: tests 1, 2 and 5 pass; test 3 passes in 30 of 32 cases (the misses: Mw 6.5–7 from floor 5.0, all events, 87.8 predicted against a band from 88.6; shallow crustal, declustered, M ≥ 7 from floor 5.3, 0.6 predicted against a band from 1.1); test 4 passes in 16 of 20 bins (mb reads 0.10–0.17 above the regional Mw at 5.0–5.5).**

## 1. Rules as applied

1. **Magnitudes per event.** Every row of the frozen magnitude tables of GCMT, the ISC Bulletin, CSN web, ComCat, ISC-GEM, the Centennial catalogue and Cabello is joined to its event through the A3 links; agency and type are kept as written (470 327 values, one per event and scale). Left out: Potin and GCCEL magnitudes, the ISC-EHB and CSN-in-ISC tables (the same rows as the ISC Bulletin), the PDE values inside the GCMT file, and CSN / GUC coda and duration magnitudes before 1990. ComCat's USGS and CSN values take the name of the same scale in the ISC Bulletin; where both give it, the ISC row is used. The ISC-GEM value comes from its own table, which says whether the Mw is direct or a proxy, not from its copy in ComCat.
2. **Reference Mw, one scale.** Members: GCMT; USGS W-phase Mw (NEIC Mww); CSN regional Mw (GUC Mwr) and the Mw of the CSN web catalogue; USGS regional Mw (NEIC Mwr); GFZ Mw; CSN W-phase Mw. Each member is shifted to NEIC Mww by a constant (section 2). GCMT ≥ 5.4: GCMT. Below 5.4: the W family in that order, then GCMT, with CSN Mww after GCMT below 5.0. The CSN moment magnitude of the ISC Bulletin (GUC MW) comes last: it is used only when the event has no other measured Mw, and it is not used to fit the relations or the offsets of the others. 6 334 events have a reference Mw in the frozen catalogue (GCMT 2 265, NEIC Mwr 1 459, GUC Mwr 1 197, NEIC Mww 709, CSN web Mw 555, GUC MW 106, GFZ 40, CSN Mww 3; the event of 2011-01-07 04:55 takes its Mw from the large-event review).
3. **Cross-check of the CSN regional Mw.** A CSN regional Mw (GUC Mwr, CSN web Mw, GUC MW) more than 0.3 from the median of the event's other moment magnitudes (GCMT, NEIC Mww / Mwr / Mwb, GFZ, CSN Mww) is left out when the event has two or more of them: 26 values of GUC Mwr and CSN web Mw, and 18 of GUC MW. With one other value nothing is dropped and the order decides (131 pairs for GUC Mwr and CSN web Mw). List: `merged/review/mw_reference_dropped_2026-11-14b.csv`.
4. **GCMT below 5.4 without another Mw.** Lolli et al. (2023, Table 1 and its notes) discard GCMT below 5.4 only when another source gives an Mw; a GCMT-only value stays unchanged. Here such a value is lowered by its measured offset to the W family: a line in the GCMT value that is zero at 5.4, fitted on 812 pairs: 0.162 × (5.4 − GCMT), that is 0.10 at 4.75, 0.06 at 5.0, 0.02 at 5.25 (`LOWER = "ramp0"`); 1 017 events, 865 of them in the domain, flag `gcmt_lowered`.
5. **Conversion relations.** Only the agencies that observe Chile directly or are the global references are converted (decision of 11 Nov, `PROXY` in `magnitude.py`): ISC and NEIC mb and surface-wave magnitudes (MS, MSZ, Ms_20), CSN / GUC ML with the web `Ml` and `Mlv`, INPRES / SJA ML. Every other contributing agency (MOS, BJI, VAO, IDC / EIDC, GFZ non-moment types, and the rest) and every other type of the kept agencies (coda and duration, untyped M, SJA MW, the NEIC moment types outside the reference) is left out. For each kept scale: the native magnitude is regressed on the reference Mw, the slopes are divided by λ = 1 − σ_ref² / var(Mw) (σ_ref the rms of 0.08 for GCMT and 0.10 for the W family over the pairs), and the relation is inverted. The pairs are the events with a reference Mw of 4.0 or more; an event whose reference is GUC MW is not a pair. Candidates with at least 100 pairs: straight line; line with a saturation bend (slope drops above a fitted Mw); each without split and split by depth at 50 km (final depth of this run where measured, else the reference depth of A3; unknown depths shallow). Chosen by cross-validation in five time blocks: the simplest candidate within one standard error of the best, on paired differences. Outside the 1st–99th percentile of the native values of the pairs the relation continues and σ grows by 0.1 per unit. σ of a relation is the residual scatter of the native value with the reference part removed, over the slope, and never below σ_ref. Bootstrap intervals (200 resamples) at native 4.5 / 5.0 / 5.5 / 6.0.
6. **Priority list.** The scales ordered once by σ (`PRIORITY` in `magnitude.py`): NEIC Ms_20, ISC MS, NEIC MS, NEIC MSZ, CSN ML (GUC ML, web Ml, Mlv), ISC mb, NEIC mb, INPRES ML. `Mlv` has 36 pairs only, so it takes the ML relation after subtracting the measured offset of 0.25, flagged. Surface-wave scales are used without a magnitude limit, only for events not deeper than 60 km (Di Giacomo et al. 2015, p. 3 and p. 10; `JUDGE = "depth"`).
7. **One Mw per event.** From 1976: the reference Mw; else Ruiz and Madariaga (2018) for the events it names (ranges by their middle, bounds and "~" by the value, flagged); else the first eligible scale of the list; else no Mw (kept, flagged, listed). Before 1976 a moment-based value goes before a converted one, and the Centennial catalogue before ISC-GEM only within the same level: Ruiz and Madariaga; the reference Mw; a Centennial Mw; an ISC-GEM direct Mw; the preferred Centennial magnitude converted; an ISC-GEM proxy Mw; Cabello's CERESIS value before 1904; else the first eligible scale of the list. Centennial values: Ms and untyped values (less 0.2) by the Di Giacomo et al. (2015) Ms relation; Abe mB by Abe (1982, eqs. 5 and 7), Mw = 1.6 mB − 4.07 for events deeper than 60 km and 1.6 mB − 4.33 otherwise; an entry whose preferred magnitude is mb leaves the event to the next source.
8. **Large-event review (A6).** The accepted Mw rows of `catalog/overrides_A6.csv` replace the value of the rule as the last step (7 events, kind `a6`): 1543 (7.7), 1949-04-20 (7.1), 1959-06-14 (7.2), 1960-06-06 Aysén (7.7), 1971-05-08 (7.2), 2010-02-27 08:25 (6.3), 2011-01-07 04:55 (5.7). The accepted depth of 1934-03-01 21:45 (120 km) enters through the final depths: its Abe mB 7.3 is converted as an intermediate-depth event, Mw 7.6.
9. **Dither.** Native values on the 0.1 grid are spread uniformly within their bin before conversion (fixed seed per scale); `mw` is rounded to 0.1, `mw_raw` is the undithered value.

Result: 116 780 events with an Mw; 15 687 with Mw ≥ 4.5 (10 018 converted, 4 728 measured, 600 ISC-GEM, 158 Cabello, 149 Centennial, 27 Ruiz and Madariaga, 7 corrected in the review); 14 279 of them in the model domain. 88 176 events without Mw, of them 69 746 Potin-only; 844 have a native M ≥ 4.5 (243 M ≥ 5): `review/no_mw`.

## 2. Offsets of the reference members (`mw_offsets`, `figs/magnitude/offsets.png`)

Mean of member − NEIC Mww on shared events, pair mean 4.5–6.5. Means are used because the values are rounded to 0.1 and medians jump.

| member | pairs | mean | sd | shift applied | X2 review |
|---|---|---|---|---|---|
| CSN regional Mw (GUC Mwr) | 350 | +0.01 | 0.14 | −0.01 | 0 |
| CSN web Mw | 257 | −0.01 | 0.12 | +0.01 | 0 |
| USGS regional Mw (NEIC Mwr) | 489 | −0.08 | 0.10 | +0.08 | +0.10 |
| GFZ Mw | 396 | −0.04 | 0.07 | +0.04 | +0.03 |
| CSN W-phase Mw | 171 | +0.03 | 0.10 | −0.03 | 0 |
| CSN Mw of the ISC Bulletin (GUC MW) | 125 | +0.06 | 0.20 | −0.06 | – |
| GCMT | 963 | +0.08 (4.75–5.0), +0.05 (5.0–5.25), +0.02 (5.25–5.75), 0.00 above | 0.08 | none; lowered below 5.4 when alone | +0.08 / +0.04 / 0 |

All W members are flat (no bin with 30 pairs departs from the mean by more than 0.05). Reference errors from GCMT, NEIC Mww and GUC Mwr on the 314 events that have all three (variances of the pairwise differences): GCMT 0.059, NEIC Mww 0.047, GUC Mwr 0.11. The settings stay at 0.08 and 0.10.

## 3. Relations of the main scales (`relations`, `FIGURES/magnitudes/relations.png`)

| scale | form, split | pairs | σ | Mw at native 4.5 (95 % interval) | 5.0 | 5.5 | 6.0 |
|---|---|---|---|---|---|---|---|
| ISC mb, ≤ 50 km | bend at Mw 6.2 | 3 033 | 0.27 | 4.40 (4.39–4.41) | 5.04 | 5.69 | 6.41 |
| ISC mb, > 50 km | bend at Mw 5.2 | 2 322 | 0.18 | 4.52 (4.51–4.53) | 5.02 | 5.64 | 6.34 |
| NEIC mb | bend at Mw 6.2, no split | 5 584 | 0.24 | 4.36 (4.35–4.37) | 5.00 | 5.63 | 6.30 |
| CSN ML, ≤ 50 km | line | 2 381 | 0.26 | 4.55 (4.54–4.56) | 5.07 | 5.60 | 6.13 |
| CSN ML, > 50 km | line | 1 852 | 0.19 | 4.43 (4.42–4.44) | 4.92 | 5.41 | 5.89 |
| INPRES ML, ≤ 50 / > 50 km | line | 1 455 / 1 435 | 0.27 / 0.27 | 4.49 / 4.64 | 5.04 / 5.13 | 5.59 / 5.62 | 6.14 / 6.11 |
| ISC MS, ≤ 50 km | bend at Mw 6.6 | 2 276 | 0.14 | 5.04 | 5.43 | 5.82 | 6.20 |
| ISC MS, > 50 km | bend at Mw 5.8 | 185 | 0.15 | 5.18 | 5.55 | 5.91 | 6.29 |
| NEIC MS | bend at Mw 6.6, no split | 402 | 0.16 | 4.97 | 5.39 | 5.80 | 6.21 |
| NEIC Ms_20 / MSZ | line | 219 / 163 | 0.12 / 0.21 | 4.93 / 5.02 | 5.37 / 5.48 | 5.81 / 5.93 | 6.24 / 6.38 |

16 relation rows for 8 fitted scales and the two that borrow the ML relation; coefficients, ranges, intervals and the cross-validation score of every candidate in `relations_2026-11-14b.csv`. A depth split is chosen for ISC mb, ISC MS, CSN ML and INPRES ML, and the bend for the mb and MS scales. NEIC mb is not split: the depth split scores 0.0412 against 0.0414 unsplit, inside one standard error. A split by period at 1990 is in the code for ISC mb and NEIC mb but gets no cross-validation score with time blocks, so it is never chosen. The floor of Mw 4.0 on the pairs changes the converted values by less than 0.01 at native 4.5–5.5, except for NEIC mb, which is split by depth without the floor (`relations_floor_2026-11-14b.csv`). mb ≈ Mw and CSN ML ≈ Mw at 4.5–5 stand.

**Forward and inverse fits on the same pairs** (`figs/magnitude/forward_inverse.png`). With the W family in the reference, the forward chi-square line and the chosen inverse relation differ by 0.00–0.04 at native 4.5 (run of 12 Nov; not rechecked for run `2026-11-14b`, the figure has the values of this run). The large bias of forward fits in X1 came from GCMT as the only reference. **Coverage** (`figs/magnitude/coverage.png`, `mw_coverage`): the share of events with a reference Mw rises from under 10 % at native 4.0 to 40–50 % at 5.0 and 75–90 % at 5.6 (ISC mb, NEIC mb, CSN ML; 1976 to today), and from 2011 it reaches 50 % at 4.6–4.7. ISC MS has a reference for 30–40 % of its events already at MS 3.5–4: it is measured mostly for events that are large for their MS, which is the violated condition of section 5.

## 4. Priority list

Given in rule 6. Converted events with Mw ≥ 4.5 come from ISC mb (4 772), CSN ML (2 788, with web Ml and Mlv), ISC MS (1 430), NEIC mb (862), NEIC surface-wave scales (124) and INPRES ML (42).

## 5. Stated assumptions

- Selection acts on the reference, not on the native scale. True for mb and ML; not for the surface-wave scales (coverage figure). They are used without a magnitude limit, and the withheld-value check of section 6a shows no bias.
- Reference σ 0.08 (GCMT) and 0.10 (W family). Measured: 0.05–0.06 for GCMT and NEIC Mww, 0.11 for the CSN regional Mw.
- The slope correction is exact when the reference selects on true size and over-corrects when it selects on the measured value (test 9: +0.05 at native 4.5 with a floor at 5.3). It is carried as a ± 0.05 systematic at native 4.5. In the catalogue: no correction raises the M ≥ 7 prediction by 6–7 %; σ 0.15 changes it less (sensitivity (e)).
- Depth is the final depth of this run where it is measured, else the reference depth of A3 (no default-depth screening); the families of the tests use it too.
- The tests use the events from 1976 on (test 6: 1964–1975) and the values of the rule, before the corrections of the large-event review.

## 6. Test results (`mw_tests`, `mw_sensitivity`; figures in `FIGURES/magnitudes/` (tests 1, 7, 9) and `figs/magnitude/` (the others))

| test | result | pass |
|---|---|---|
| 1 b range over floors 4.7–5.8 | 0.12 / 0.14 (2011 on, full / declustered), 0.08 / 0.08 (1976 on) | yes |
| 2 declustered rate M ≥ 5.5 per yr | 15.9 / 15.5 / 19.4 / 17.1, departure 14.1 % | yes (limit 15 %) |
| 2 rate M ≥ 5.0 (no criterion) | 52 / 44 / 57 / 52, 14 % | – |
| 3 M ≥ 7, predicted / observed | 36.9 / 43 (from 5.0), 39.1 / 43 (from 5.3) | yes |
| 3 Mw 6.5–7 | 87.8 / 108 (from 5.0), 90.5 / 108 (from 5.3); band from 88.6 | **no** from 5.0 |
| 3 all cases | 30 of 32 (the second miss: shallow crustal, declustered, M ≥ 7 from 5.3: 0.6 predicted, band 1.1–10.2) | 30 of 32 |
| 4 converted − regional Mw, held out | 16 of 20 bins within 0.1; ISC mb +0.10 / +0.13 and NEIC mb +0.17 / +0.14 at 5.0–5.25 / 5.25–5.5 | partly |
| 5 histogram, largest \|z\| by period | 2.2 / 1.1 / 1.3 / 1.9 | yes (limit 3.0) |
| 6 1964–1975 | M ≥ 5.5: 15.6 per yr; converted − ISC-GEM −0.21 / +0.05 / +0.13 | reported |
| 7 comparison | Cabello et al. (2025): b range 0.55, rate departure 34 %, M ≥ 7 26 / 35 and 15 / 35. Candia and Macedo (2026): 0.42, 17 %, 25 / 46 and 24 / 46 | – |

Measure of test 5: each 0.1 bin n against the geometric mean g of its two neighbours, z = (n − g) / sqrt(1.5 g); a comb or a heap gives |z| > 3.

**Sensitivity** (tests 1–3 and the histogram on this run; `mw_sensitivity`):

| variant | b range (four cases) | rate M ≥ 5.5 departure | M ≥ 7 pred / obs, from 5.0 and 5.3 | histogram \|z\| | fails (T1–T3 on all events, T5) |
|---|---|---|---|---|---|
| as run | 0.08–0.14 | 14.1 % | 36.9 / 43, 39.1 / 43 | 2.2 | T3 |
| (a) GCMT first at all magnitudes | 0.12–0.18 | 13.9 % | 35.1 / 43, 31.3 / 43 | 2.5 | T3 |
| (b) weighted mean of the converted scales, with their correlations | 0.06–0.15 | 10.9 % | 34.6 / 41, 41.3 / 41 | 1.6 | T3 |
| (b) inverse-variance mean of the converted scales | 0.05–0.12 | 10.7 % | 43.0 / 41, 42.9 / 41 | 3.5 | T5 |
| (c) straight lines only | 0.08–0.15 | 13.1 % | 39.1 / 43, 37.0 / 43 | 2.2 | none |
| (d) ISC-GEM before the Centennial inside each level | 0.08–0.14 | 14.0 % | 36.9 / 43, 39.1 / 43 | 2.2 | T3 |
| (e) no slope correction | 0.08–0.14 | 13.7 % | 39.2 / 43, 41.8 / 43 | 2.1 | none |
| (e) slope correction with σ 0.15 | 0.08–0.15 | 13.5 % | 35.0 / 41, 39.2 / 41 | 2.9 | T3 |
| (f) forward chi-square regression | 0.09–0.14 | 14.1 % | 39.1 / 42, 36.6 / 42 | 2.5 | none |
| (g) surface-wave scales only where their own value reaches Mw 5 | 0.11–0.15 | 14.6 % | 34.1 / 43, 35.7 / 43 | 2.1 | T3 |
| (g) surface-wave scales only where another scale reaches Mw 5 | 0.07–0.15 | 13.2 % | 36.7 / 43, 40.4 / 43 | 2.0 | T3 |
| (h) surface-wave scales after all others | 0.10–0.15 | 15.6 % | 33.2 / 42, 32.1 / 42 | 1.6 | T2, T3 |
| (i) GCMT below 5.4 lowered by one step per bin | 0.07–0.16 | 13.8 % | 34.5 / 43, 40.3 / 43 | 3.7 | T3, T5 |
| (i) GCMT below 5.4 not lowered | 0.09–0.15 | 13.5 % | 37.5 / 43, 35.2 / 43 | 2.5 | T3 |
| Cabello et al. (2025) | 0.24–0.55 | 33.9 % | 26.2 / 35, 15.1 / 35 | – | T1, T2, T3 |
| Candia and Macedo (2026) | 0.11–0.42 | 17.2 % | 25.4 / 46, 23.5 / 46 | – | T1, T2, T3 |

The T3 failures of our variants are all in the Mw 6.5–7 count (predicted below the band). The variants before 1976 (d) do not show in the tests, which use 1976 on.

## 6a. Why the surface-wave rule and the GCMT line (run of 12 Nov, `explore/X4`)

The numbers of this section are of the run of 12 Nov and were not recomputed for run `2026-11-14b`.

A limit at Mw 5 on a noisy converted value keeps the events that scatter up and replaces those that scatter down. Checked on the events that have a measured Mw, with that value withheld (`explore/X4/tables/x4_blind.csv`, `x4_combos.csv`): the number of events at Mw ≥ 5 is 4.7 % too high with the limit on the scale's own value and 6.9 % too low with the limit judged on another scale (six agencies converted; 9.7 % and 14.8 % with every agency of the ISC Bulletin, hence the +5 to +10 % and −7 to −15 % of DECISIONS). Without a limit and with the depth limit of the published catalogues it is 1.9 % low in both sets, and the mean difference is within 0.02 in every 0.25 bin from 4.5 to 5.5. One step per bin for GCMT left gaps between the bins and a comb in the histogram of 2000–2010.

Tested: four ways of lowering GCMT (step per bin, line that is zero at 5.4, free line, none) by four rules for the converted scales (own value reaches Mw 5; depth limit and first scale; depth limit and inverse-variance mean; depth limit and mean with the correlations between scales), 16 catalogues. Chosen: line that is zero at 5.4, depth limit, first scale of the list. The weighted mean (Lolli et al. 2014) has steadier rates but pulls the largest converted events down where mb saturates, so it is kept as sensitivity (b). The free line lowers GCMT up to 6.07 and failed test 3.

Still open: test 4 (mb against the regional Mw at 5.0–5.5); converted events at Mw ≥ 5.5 were 5–7 % too many against measured values under every rule tested; the withheld events are the fitting pairs and are not a random sample below Mw 5.

## 7. Synthetic comparison of the regression methods (test 9, `FIGURES/magnitudes/test9_synthetic.png`, `mw_synthetic`)

A Gutenberg–Richter population (b = 1, from M 3.5), native = 0.5 + 0.9 M with σ 0.20, reference with σ 0.08, 20 populations of 200 000 events. Bias of the converted Mw at native 4.5 (5.0):

| method | every event paired | reference above 5.3, cut on measured Mw | cut on true size |
|---|---|---|---|
| forward least squares | −0.11 (−0.22) | +0.26 (+0.14) | +0.22 (+0.12) |
| forward orthogonal (η = 1) | −0.05 (−0.10) | +0.14 (+0.08) | +0.10 (+0.05) |
| forward chi-square, correct η | 0.00 | +0.05 (+0.03) | 0.00 |
| forward chi-square, η × 2 / η ÷ 2 | −0.01 / +0.01 | +0.08 / +0.03 | +0.03 / −0.02 |
| inverse, plain | +0.02 (+0.04) | +0.02 (+0.01) | −0.03 (−0.02) |
| inverse, slope corrected | 0.00 | +0.05 (+0.03) | 0.00 |

Castellaro et al. (2006) discourage inverted regression, and for a complete sample they are right: the plain inverse line is off by +0.02 to +0.04 there, and chi-square with the correct error ratio is exact. Our samples are not complete: the reference exists for under half of the events below native 5 (coverage figure). With a floor on the reference, least squares and orthogonal regression are biased by 0.1–0.26 at native 4.5, while the inverse fits stay within 0.05. Chi-square regression with the correct η does as well as the slope-corrected inverse fit in every case; it depends on knowing η (a factor 2 costs up to 0.03 more), the plain inverse fit does not. So the inverse step protects against the forms that fail (least squares, orthogonal, and curved forward fits, X1); against chi-square with a well-measured η its advantage is small, and on our pairs the two agree within 0.04 (section 3).

## 8. Draft methods paragraph (from REVIEW §6, numbers of this run where they changed)

> Native magnitudes were converted to Mw with one relation per agency and scale, fitted on Chilean event pairs by regressing the native magnitude on the reference Mw and inverting, with the slope corrected for the reference error. Global moment-tensor catalogues are incomplete below Mw 5.2–5.6, so a regression of Mw on the native magnitude selects pairs on its dependent variable, a truncated regression that is biased at the low end (Hausman and Wise 1977; Lolli et al. 2014, 2023). Regressing on the truncated variable avoids this, provided the native scale is reported independently of size, which holds for mb and ML (Supplement). Inverted regression is discouraged for complete samples (Castellaro et al. 2006); ours are not complete, and a synthetic test shows the inverse fit within 0.05 of the true relation where least-squares and orthogonal fits are off by 0.1–0.26. Below Mw 5.4 the reference is the regional and W-phase moment-magnitude family, whose members agree within 0.03 after constant offsets of at most 0.08. Only ISC and NEIC teleseismic magnitudes and the local magnitudes of the Chilean and Argentine networks are converted. GCMT reads 0.05–0.08 higher there, as found by Gasperini et al. (2012), and agrees above 5.4 (Lolli et al. 2023). Measured Mw takes precedence over converted values; a converted event takes one scale from a fixed priority list. Before 1976 a moment-based value takes precedence over a converted one, and body-wave magnitudes of the Centennial catalogue are converted with Abe (1982). [Test numbers to be filled.]

The inverse step is the method's new element for this purpose: no paper was found that proposes it for the incompleteness of the reference (REVIEW §5).

## 9. References for each choice (REVIEW §5; marks kept)

| step | support |
|---|---|
| Inverse regression | Hausman and Wise (1977) 10.2307/1912682; Heckman (1979) 10.2307/1912352; Lolli et al. (2014) 10.1093/gji/ggu264; Lolli et al. (2023) 10.1093/gji/ggad164; Di Giacomo et al. (2015); Castellaro et al. (2006); Osborne (1991) 10.2307/1403690; Fuller (1987); Gasperini et al. (2025) 10.1785/0120250007. Counter-position: Christophersen et al. (2024) 10.1785/0120230169; Llenos et al. (2026) 10.1785/0220250231 |
| Form | Gasperini et al. (2013b) 10.1785/0220130105; Lolli et al. (2014); Poulos et al. (2019); Deichmann (2017) |
| Reference Mw and order | Lolli et al. (2023); Gasperini et al. (2012) GJI 190:1733 (as cited by Lolli et al.); Di Giacomo et al. (2021) 10.5194/essd-13-1957-2021; Rovida et al. (2020) 10.1007/s10518-020-00818-y; Riquelme et al. (2018) |
| One proxy by a priority list | Allen et al. (2018); Christophersen et al. (2024). Mean of proxies: CEUS-SSC Eqs. 3.3.1-9/10; Lolli et al. (2023) |
| Surface-wave scale before mb, shallow events only, no magnitude limit | Di Giacomo et al. (2015) p. 3, p. 10; Engdahl and Villaseñor (2002) p. 3; Weatherill et al. (2016) Table 1; Lolli et al. (2023) p. 3–4 (depth < 50 km) |
| Magnitudes before 1976 | Ruiz and Madariaga (2018); Engdahl and Villaseñor (2002); Di Giacomo et al. (2015); Abe (1982) 10.4294/jpe1952.30.321, eqs. 5 and 7 |
| Rate bias (step B) | Tinti and Mulargia (1985) 10.1785/BSSA0750061681; CEUS-SSC §3.3.1; Musson (2012) 10.1785/0120110224; Mueller (2019) 10.1785/0220170108 |
| Validation | Lolli et al. (2014); Habermann (1991) 10.1016/0040-1951(91)90337-R; Zúñiga and Wiemer (1999) 10.1007/s000240050285; Tormann et al. (2010) 10.1785/0120090124 |

Not yet verified, check before citing: Felzer (2008); Mueller (2019) and Riquelme et al. (2018) beyond the passages read; the ESHM20 and Canada conversion rules; items marked (mem) in REVIEW §5.

## 10. Depth groups and the comparison with Cabello and Candia–Macedo (17 Nov, A11)

**Change.** The converted scales may take three depth groups (down to 50 km, 50–150 km, below 150 km; 150 km is the top of the Jujuy nest in `classify.NEST`), chosen per scale by the same time-block cross-validation as the other forms (`magnitude.ZNEST`, split `depth3`). It is chosen for GUC ML (and CSN Ml / Mlv through it), SJA ML, ISC mb and NEIC mb. Asked by FITS (`handoffs/2026-11-17_FITS_to_CAT.md`): the Jujuy nest fit bends at about Mw 5.8.

**What the figures show** (`FIGURES/magnitudes/`: `relations`, `relations_others`, `residual_depth`, `residual_converted`, `compare_relations`, `test1_b_floor`, `test7_comparison`):
- As reported, the scales disagree with the measured Mw by depth: CSN ML +0.2 below 150 km, ISC mb sliding to −0.3 at 250 km, NEIC mb and INPRES ML −0.1 to −0.2 below 200 km. With two depth groups (17f) the deep ML relation, fitted mostly near 110 km, left nest events (about 205 km) 0.1 too high and deep mb 0.1–0.15 too low. With three groups every scale is within ±0.1 of the measured Mw at every depth.
- The nest b barely moves (1.45 → 1.46 from Mw 5.0 since 1976, events of most weight): the ML values go down and the mb values up by about 0.08. The bend of the nest is not a conversion artefact; the split of its fit into direct and converted Mw is the selection FITS described (direct Mw for most events above 5.5).
- A5 tests on the three groups: all pass that passed on 17f, plus Mw 6.5–7 predicted from 5.0 (88.8 / 107); b range 0.05–0.16, M ≥ 5.5 rate drift 13.6 %, M ≥ 7 37.9 / 43. Still failing: ISC and NEIC mb held out at 5.0–5.5 (+0.10 to +0.15 against the regional Mw) and shallow crustal declustered M ≥ 7 from 5.3.
- The magnitudes as reported (measured Mw where there is one, the native value otherwise) give the same b against the fit floor within 0.05. From 4.7 to 5.8 the conversions are close to 1:1; their value is the removal of the depth and period biases, not the b.

**Why the other two catalogues fail.**
- Candia and Macedo (2026) convert ComCat mb with one forward relation, Mw = 0.994 mb + 0.179, at every depth. Below about Mw 5 only the larger events have a measured Mw, so a regression of Mw on mb is pulled up; their converted Mw sits 0.15–0.25 above the measured Mw at mb 4.3–5.5 (0.6–0.8 below mb 4 for ISC mb, where the flat part of their values sits). Their CSN values are taken as Mw unchanged: 0.3–0.6 below the measured Mw above ML 5 at depth. One relation at every depth also keeps the mb drift with depth.
- Cabello et al. (2025) use forward relations as well and one per scale (CSN ML split at 50 km); their Mw on our events sits 0.3–0.5 above ours for NEIC mb at 4–5.5, and their ISC mb line stays below the saturation above mb 6.
- At catalogue level (test 7): b moves 0.24–0.55 (Cabello) and 0.11–0.42 (Candia–Macedo) with the fit floor against 0.05–0.16 here; the M ≥ 5.5 rate drifts 34 % and 17 %; a fit from Mw 5.0 predicts 0.4–0.75 and 0.5–0.66 of the observed M ≥ 7 against 0.9 here. Both do worse on b than the magnitudes as reported.

**How to compare a converted catalogue** (learned here): on events that have a measured Mw the other catalogues carry that same Mw (Candia–Macedo take ComCat, ISC-GEM and ISC Mw unchanged), so the comparison says nothing; compare on events without a measured Mw. A relation drawn through its own converted values is a straight line by construction. Below about magnitude 4.3 the paired medians rise for every scale (only the larger events are paired), so no relation can be judged there from pairs.
