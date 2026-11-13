# Magnitudes: one Mw per earthquake (A5)

Methods note for the paper. Code: `catalog/magnitude.py` (fits, assignment; settings at the top) and `catalog/magnitude_check.py` (tests, figures). Run of 2026-11-12 (third A5 run: surface-wave scales by depth, smooth GCMT correction; section 6a compares it with the second run, section 6 the second with the first; files keep the date 2026-11-11 of the inputs) on the A3 events of the same date (204 956 events). Tables in `catalog/merged/` (`mw_`, `relations_`, `mw_offsets_`, `mw_tests_`, `mw_sensitivity_`, `mw_synthetic_`, `mw_coverage_`, `mw_histogram_`, all `_2026-11-11`), figures in `catalog/figs/magnitude/`.

**Status (third run): tests 1, 2 and 5 pass; test 3 passes in 31 of 32 cases (the miss is shallow crustal, declustered, M ≥ 7 from floor 5.3: 0.6 predicted, 3 observed); test 4 passes in 16 of 20 bins (mb reads 0.10–0.17 above the regional Mw at 5.0–5.5). Sections 1 to 5 describe the second run except where marked.**

## 1. Rules as applied

1. **Magnitudes per event.** Every row of the frozen magnitude tables of GCMT, the ISC Bulletin, CSN web, ComCat, ISC-GEM, the Centennial catalogue and Cabello is joined to its event through the A3 links; agency and type are kept as written (470 327 values, one per event and scale). Left out: Potin and GCCEL magnitudes, the ISC-EHB and CSN-in-ISC tables (the same rows as the ISC Bulletin), the PDE values inside the GCMT file, and CSN / GUC coda and duration magnitudes before 1990. ComCat's USGS and CSN values take the name of the same scale in the ISC Bulletin; where both give it, the ISC row is used.
2. **Reference Mw, one scale.** Members: GCMT; USGS W-phase Mw (NEIC Mww); CSN regional Mw (GUC Mwr) and the Mw of the CSN web catalogue; USGS regional Mw (NEIC Mwr); GFZ Mw; CSN W-phase Mw. Each member is shifted to NEIC Mww by a constant (section 2). GCMT ≥ 5.4: GCMT. Below 5.4: the W family in that order, then GCMT, with CSN Mww after GCMT below 5.0. 6 228 events have a reference Mw.
3. **GCMT below 5.4 without another Mw.** Lolli et al. (2023, Table 1 and its notes) discard GCMT below 5.4 only when another source gives an Mw; a GCMT-only value stays unchanged. Following the brief, such a value is lowered by its measured offset to the W family. Third run: the offset is a line in the GCMT value that is zero at 5.4, fitted on 813 pairs: 0.159 × (5.4 − GCMT), that is 0.10 at 4.75, 0.06 at 5.0, 0.02 at 5.25 (`LOWER = "ramp0"`); 1 016 events, flag `gcmt_lowered`. The second run used one step per 0.25 bin (0.05 / 0.07 / 0.04), which left gaps between the bins and a comb in the histogram (section 6a).
4. **Conversion relations.** Only the agencies that observe Chile directly or are the global references are converted (decision of 11 Nov, `PROXY` in `magnitude.py`): ISC and NEIC mb and surface-wave magnitudes (MS, MSZ, Ms_20), CSN / GUC ML with the web `Ml` and `Mlv`, INPRES / SJA ML. Every other contributing agency (MOS, BJI, VAO, IDC / EIDC, GFZ non-moment types, and the rest) and every other type of the kept agencies (coda and duration, untyped M, SJA MW, the NEIC moment types outside the reference) is left out. For each kept scale: the native magnitude is regressed on the reference Mw, the slopes are divided by λ = 1 − σ_ref² / var(Mw) (σ_ref the rms of 0.08 for GCMT and 0.10 for the W family over the pairs), and the relation is inverted. Candidates with at least 100 pairs: straight line; line with a saturation bend (slope drops above a fitted Mw); each without split, split by depth at 50 km (provisional A3 depth; unknown depths shallow) and, for ISC mb and NEIC mb, by period at 1990. Chosen by cross-validation in five time blocks with the one-standard-error rule on paired differences. Outside the 1st–99th percentile of the native values of the pairs the relation continues and σ grows by 0.1 per unit. σ of a relation is the residual scatter of the native value with the reference part removed, over the slope, and never below σ_ref. Bootstrap intervals (200 resamples) at native 4.5 / 5.0 / 5.5 / 6.0.
5. **Priority list.** The scales ordered once by σ (`PRIORITY` in `magnitude.py`): NEIC Ms_20, ISC MS, NEIC MS, NEIC MSZ, CSN ML (GUC ML, web Ml, Mlv), ISC mb, NEIC mb, INPRES ML. `Mlv` has 42 pairs only, so it takes the ML relation after subtracting the measured offset of 0.24, flagged. Third run: surface-wave scales are used without a magnitude limit, only for events not deeper than 60 km (Di Giacomo et al. 2015, p. 3 and p. 10; `JUDGE = "depth"`). In the second run they were not eligible when their own converted value was below Mw 5.
6. **One Mw per event:** Ruiz and Madariaga (2018) for the events it names (ranges by their middle, bounds and "~" by the value, flagged); else the reference Mw; else before 1976 ISC-GEM, then the Centennial catalogue (Mw and mB as given, Ms and unknown types by the Di Giacomo et al. 2015 Ms relation, as X1), then Cabello's CERESIS value before 1904; else the first eligible scale of the list; else no Mw (kept, flagged, listed).
7. **Dither.** Native values on the 0.1 grid are spread uniformly within their bin before conversion (fixed seed per scale); `mw` is rounded to 0.1, `mw_raw` is the undithered value.

Result (third run): 116 773 events with an Mw; 15 549 with Mw ≥ 4.5 (9 928 converted, 4 654 measured, 701 ISC-GEM, 159 Cabello, 55 Ruiz and Madariaga, 52 Centennial). 88 183 events without Mw, of them 69 746 Potin-only; 846 have a native M ≥ 4.5 (243 M ≥ 5): `review/no_mw`.

## 2. Offsets of the reference members (`mw_offsets`, `figs/magnitude/offsets.png`)

Mean of member − NEIC Mww on shared events, pair mean 4.5–6.5. Means are used because the values are rounded to 0.1 and medians jump.

| member | pairs | mean | sd | shift applied | X2 review |
|---|---|---|---|---|---|
| CSN regional Mw (GUC Mwr) | 350 | +0.01 | 0.14 | −0.01 | 0 |
| CSN web Mw | 257 | −0.01 | 0.12 | +0.01 | 0 |
| USGS regional Mw (NEIC Mwr) | 489 | −0.08 | 0.10 | +0.08 | +0.10 |
| GFZ Mw | 396 | −0.04 | 0.07 | +0.04 | +0.03 |
| CSN W-phase Mw | 171 | +0.03 | 0.10 | −0.03 | 0 |
| GCMT | 963 | +0.08 (4.75–5.0), +0.05 (5.0–5.25), +0.02 (5.25–5.75), 0.00 above | 0.08 | none; lowered below 5.4 when alone | +0.08 / +0.04 / 0 |

All W members are flat (no bin with 30 pairs departs from the mean by more than 0.05). Reference errors from GCMT, NEIC Mww and GUC Mwr on the 322 events that have all three (variances of the pairwise differences): GCMT 0.055, NEIC Mww 0.052, GUC Mwr 0.13. The settings stay at 0.08 and 0.10; the CSN regional Mw is noisier than assumed.

## 3. Relations of the main scales (`relations`, `figs/magnitude/relations.png`)

| scale | form, split | pairs | σ | Mw at native 4.5 (95 % interval) | 5.0 | 5.5 | 6.0 |
|---|---|---|---|---|---|---|---|
| ISC mb, ≤ 50 km | bend at Mw 6.2 | 3 159 | 0.27 | 4.39 (4.38–4.40) | 5.04 | 5.69 | 6.42 |
| ISC mb, > 50 km | bend at Mw 5.2 | 2 351 | 0.18 | 4.52 (4.50–4.53) | 5.01 | 5.63 | 6.34 |
| NEIC mb | bend at Mw 6.3, no split | 5 762 | 0.24 | 4.35 (4.34–4.36) | 4.99 | 5.63 | 6.28 |
| CSN ML, ≤ 50 km | line | 2 543 | 0.26 | 4.54 (4.53–4.55) | 5.07 | 5.60 | 6.13 |
| CSN ML, > 50 km | line | 1 881 | 0.19 | 4.43 (4.42–4.44) | 4.92 | 5.40 | 5.89 |
| INPRES ML, ≤ 50 / > 50 km | line | 1 543 / 1 452 | 0.27 / 0.27 | 4.48 / 4.63 | 5.04 / 5.12 | 5.60 / 5.62 | 6.15 / 6.11 |
| ISC MS, ≤ 50 km | bend at Mw 6.6 | 2 266 | 0.14 | 5.04 | 5.43 | 5.81 | 6.20 |
| NEIC MS | bend, no split | 402 | 0.16 | 4.95 | 5.38 | 5.80 | 6.22 |
| NEIC Ms_20 / MSZ | line | 219 / 163 | 0.12 / 0.21 | 4.93 / 5.00 | 5.37 / 5.46 | 5.81 / 5.92 | 6.24 / 6.38 |

16 relation rows for 8 fitted scales and the two that borrow the ML relation; coefficients, ranges, intervals and the cross-validation score of every candidate in `relations_2026-11-11.csv`. A depth split is chosen for ISC mb, ISC MS, CSN ML and INPRES ML, and the bend for the mb and MS scales; the period split at 1990 is never chosen. mb ≈ Mw and CSN ML ≈ Mw at 4.5–5 stand.

**Forward and inverse fits on the same pairs** (`figs/magnitude/forward_inverse.png`). With the W family in the reference, the forward chi-square line and the chosen inverse relation differ by 0.00–0.04 at native 4.5 (ISC mb 4.38 / 4.39 shallow and 4.48 / 4.52 deep; NEIC mb 4.34 / 4.35; CSN ML equal). The large bias of forward fits in X1 came from GCMT as the only reference. **Coverage** (`figs/magnitude/coverage.png`, `mw_coverage`): the share of events with a reference Mw rises from under 10 % at native 4.0 to about 50 % at 5.0 and over 90 % from 5.6 (mb, ML; 1976 to today), and from 2011 it reaches 50 % at 4.5–4.7. ISC MS has a reference for 30–40 % of its events already at MS 3.5–4: it is measured mostly for events that are large for their MS, which is the violated condition of section 5.

## 4. Priority list

Given in rule 5. Converted events with Mw ≥ 4.5 (third run) come from ISC mb (4 673), CSN ML (2 830, with web Ml and Mlv), ISC MS (1 421), NEIC mb (837), NEIC surface-wave scales (125) and INPRES ML (42).

## 5. Stated assumptions

- Selection acts on the reference, not on the native scale. True for mb and ML; not for the surface-wave scales (coverage figure). The second run answered this with a limit at Mw 5, which biased the counts (section 6a); the third run uses them without a limit and the withheld-value check shows no bias.
- Reference σ 0.08 (GCMT) and 0.10 (W family). Measured: 0.05–0.06 for GCMT and NEIC Mww, 0.13 for the CSN regional Mw.
- The slope correction is exact when the reference selects on true size and over-corrects when it selects on the measured value (test 9: +0.05 at native 4.5 with a floor at 5.3). It is carried as a ± 0.05 systematic at native 4.5. In the catalogue: no correction or σ 0.15 move the M ≥ 7 prediction by ± 5 % (sensitivity (e)).
- Depth is the provisional A3 depth (reference member, no default-depth screening); the families of the tests use it too.

## 6. Test results (`mw_tests`, `mw_sensitivity`; one figure each in `figs/magnitude/`)

"Before" is the first A5 run (every agency with 30 pairs converted, 87 scales); "after" is this run.

| test | before | after | pass after |
|---|---|---|---|
| 1 b range over floors 4.7–5.8 | 0.14 / 0.17 (2011 on, full / declustered), 0.20 / 0.16 (1976 on) | 0.14 / 0.17, 0.11 / 0.09 | yes |
| 2 declustered rate M ≥ 5.5 per yr | 15.8 / 16.7 / 20.9 / 19.2, departure 15.3 % | 15.9 / 15.7 / 19.7 / 17.0, departure 15.4 % | **no** (limit 15 %) |
| 2 rate M ≥ 5.0 (no criterion) | 51 / 48 / 70 / 61, 22 % | 52 / 44 / 59 / 53, 16 % | – |
| 3 M ≥ 7, predicted / observed | 32.3 / 44 (from 5.0), 31.9 / 44 (from 5.3) | 32.9 / 44, 37.3 / 44 | yes |
| 3 Mw 6.5–7 | 85.9 and 84.9 / 107 (band from 87.7) | 82.4 / 107 (from 5.0), 88.3 / 107 (from 5.3) | **no** from 5.0 |
| 3 all cases | 25 of 32; all events 5 of 8, crustal shallow 4 of 8 | 30 of 32; all events 7 of 8, crustal shallow 7 of 8, interface and in slab 16 of 16 | 30 of 32 |
| 4 converted − regional Mw, held out | 26 of 30 bins within 0.1 | 17 of 20 (Beijing mB, Moscow mb and VAO mb no longer tested); NEIC mb +0.16 / +0.13 at 5.0–5.5, ISC mb +0.11 at 5.25–5.5 | partly |
| 5 histogram, largest \|z\| by period | 2.3 / 2.0 / 6.5 / 2.1 | 2.3 / 1.3 / 3.5 / 2.2 | **no** (2000–2010, limit 3.0) |
| 6 1964–1975 | M ≥ 5.5: 15.8 per yr; converted − ISC-GEM −0.21 / +0.05 / +0.12 | 15.5 per yr; −0.21 / +0.05 / +0.13 | reported |
| 7 comparison | Cabello: b range 0.55, rate departure 34 %, M ≥ 7 26 / 35 and 15 / 35. Candia and Macedo: 0.42, 17 %, 25 / 46 and 24 / 46 | unchanged | – |

Measure of test 5: each 0.1 bin n against the geometric mean g of its two neighbours, z = (n − g) / sqrt(1.5 g); a comb or a heap gives |z| > 3.

**What the restriction changed.** The heap at Mw 5.0–5.1 came mostly from the IDC and Beijing surface-wave scales, which are gone; it shrank from |z| 6.5 to 3.5 and the rate of M ≥ 5.0 in 2000–2010 from 70 to 59 per yr. What is left comes from ISC MS and NEIC MS through the same mechanism: they head the list and are eligible only when their own converted value reaches Mw 5, which is a cut on a noisy value. The rate test fails as before, by 0.4 %: the M ≥ 5.5 rate of 2000–2010 (19.7 per yr against a mean of 17.1) is hardly touched by the converted scales.

**Sensitivity** (tests 1–3 and the histogram on this run; `mw_sensitivity`):

| variant | b range (four cases) | rate M ≥ 5.5 departure | M ≥ 7 pred / obs, from 5.0 and 5.3 | histogram \|z\| | fails (T1–T3 on all events, T5) |
|---|---|---|---|---|---|
| as run (agencies restricted) | 0.09–0.17 | 15.4 % | 32.9 / 44, 37.3 / 44 | 3.5 | T2, T3, T5 |
| (a) GCMT first at all magnitudes | 0.15–0.20 | 14.5 % | 33.7 / 44, 30.0 / 44 | 2.7 | T3 |
| (b) generalized least-squares mean of the converted scales | 0.07–0.16 | 10.7 % | 31.7 / 42, 40.5 / 42 | 4.1 | T3, T5 |
| (c) straight lines only | 0.11–0.17 | 14.1 % | 33.8 / 44, 35.0 / 44 | 2.8 | T3 |
| (d) Centennial before ISC-GEM | 0.09–0.16 | 15.1 % | 32.9 / 44, 37.3 / 44 | 3.5 | T2, T3, T5 |
| (e) no slope correction | 0.10–0.16 | 15.6 % | 34.6 / 44, 38.9 / 44 | 4.1 | T2, T3, T5 |
| (e) slope correction with σ 0.15 | 0.09–0.17 | 13.9 % | 31.7 / 42, 36.5 / 42 | 2.7 | T3 |
| (f) forward chi-square regression | 0.12–0.17 | 14.5 % | 33.1 / 43, 34.6 / 43 | 2.2 | T3 |
| (g) surface-wave scales: Mw 5 judged on the first other scale | 0.07–0.16 | 12.7 % | 35.7 / 44, 42.1 / 44 | 2.2 | T3 |
| (h) those scales after all others | 0.10–0.17 | 15.3 % | 31.9 / 43, 33.9 / 43 | 2.8 | T2, T3 |
| Cabello et al. (2025) | 0.24–0.55 | 33.9 % | 26.2 / 35, 15.1 / 35 | – | T1, T2, T3 |
| Candia and Macedo (2026) | 0.11–0.42 | 17.2 % | 25.4 / 46, 23.5 / 46 | – | T1, T2, T3 |

Variant (g) applies the Mw 5 limit of the surface-wave scales to an independent value, the converted value of the event's first other scale (mb, ML), and to their own value only when it is the event's only scale. It is `JUDGE = "other"` at the top of `magnitude.py`; it removes the rest of the heap (|z| 2.2) and the rate failure (12.7 %), and leaves the Mw 6.5–7 case from floor 5.0 (84.9 / 107, band from 87.7). The catalogue of this run keeps `JUDGE = "own"`.

## 6a. Third run: surface-wave rule and GCMT correction (12 Nov, `explore/X4`)

Why. A limit at Mw 5 on a noisy converted value keeps the events that scatter up and replaces those that scatter down. Checked on the events that have a measured Mw, with that value withheld (`explore/X4/tables/x4_blind.csv`, `x4_combos.csv`): the number of events at Mw ≥ 5 is 4.7 % too high with the limit on the scale's own value (9.7 % with all agencies) and 6.9 % too low with the limit judged on another scale (14.8 %). Without a limit and with the depth limit of the published catalogues it is 1.9 % low, and the mean difference is within 0.02 in every 0.25 bin from 4.5 to 5.5. The comb of the 2000–2010 histogram came from the measured values: the step offsets of GCMT left gaps between bins (105, 135, 73, 87, 41, 47 measured events at Mw 5.0–5.5).

Tested: four ways of lowering GCMT (step per bin, line that is zero at 5.4, free line, none) by four rules for the converted scales (own value reaches Mw 5; depth limit and first scale; depth limit and inverse-variance mean; depth limit and mean with the correlations between scales), 16 catalogues. Chosen: line that is zero at 5.4, depth limit, first scale of the list. It passes tests 1, 2, 3 (all events) and 5. The weighted mean (Lolli et al. 2014) has steadier rates (11.3 % against 13.5 %) but pulls the largest converted events down where mb saturates (a 2001 aftershock with MS 6.97 from Mw 7.0 to 6.5; 21 fewer events at Mw ≥ 6), so it is kept as sensitivity (b). The free line lowers GCMT up to 6.07 and fails test 3.

| test | second run | third run | pass |
|---|---|---|---|
| 1 b range over floors 4.7–5.8 | 0.14 / 0.17 (2011 on, full / declustered), 0.11 / 0.09 (1976 on) | 0.12 / 0.15, 0.08 / 0.08 | yes |
| 2 declustered rate M ≥ 5.5 per yr | 15.9 / 15.7 / 19.7 / 17.0, departure 15.4 % | 16.0 / 15.8 / 19.4 / 17.1, departure 13.5 % | yes |
| 2 rate M ≥ 5.0 (no criterion) | 52 / 44 / 59 / 53, 16 % | 52 / 44 / 57 / 52, 14 % | – |
| 3 M ≥ 7, predicted / observed | 32.9 / 44 (from 5.0), 37.3 / 44 (from 5.3) | 38.3 / 44, 40.5 / 44 | yes |
| 3 Mw 6.5–7 | 82.4 / 107, 88.3 / 107 | 90.0 / 106, 92.5 / 106 (band from 86.8) | yes |
| 3 all cases | 30 of 32 | 31 of 32 (shallow crustal, declustered, M ≥ 7 from 5.3: 0.6 predicted, band 1.1–10.2) | 31 of 32 |
| 4 converted − regional Mw, held out | 17 of 20 | 16 of 20: ISC mb +0.10 / +0.12 and NEIC mb +0.17 / +0.14 at 5.0–5.25 / 5.25–5.5 | partly |
| 5 histogram, largest \|z\| by period | 2.3 / 1.3 / 3.5 / 2.2 | 1.5 / 1.5 / 1.3 / 2.0 | yes |
| 6 1964–1975 | 15.5 per yr; −0.21 / +0.05 / +0.13 | 15.5 per yr; −0.21 / +0.06 / +0.13 | reported |

Changes in the catalogue: 15 306 → 15 549 events at Mw ≥ 4.5 (196 left, 439 entered); 6 317 → 6 147 at Mw ≥ 5.0; 2 267 → 2 259 at 5.5; 995 at 6.0 both. 230 measured values moved by 0.1 (GCMT line). Sensitivity of the third run in `mw_sensitivity`: every variant passes tests 1–3 on all events except GCMT first, the step or no lowering of GCMT, and the surface-wave scales after all others.

Still open: test 4 (mb against the regional Mw at 5.0–5.5); converted events at Mw ≥ 5.5 are 5–7 % too many against measured values under every rule tested; the withheld events are the fitting pairs and are not a random sample below Mw 5.

## 7. Synthetic comparison of the regression methods (test 9, `figs/magnitude/test9_synthetic.png`, `mw_synthetic`)

A Gutenberg–Richter population (b = 1, from M 3.5), native = 0.5 + 0.9 M with σ 0.20, reference with σ 0.08, 20 populations of 200 000 events. Bias of the converted Mw at native 4.5 (5.0):

| method | every event paired | reference above 5.3, cut on measured Mw | cut on true size |
|---|---|---|---|
| forward least squares | −0.11 (−0.22) | +0.26 (+0.14) | +0.22 (+0.12) |
| forward orthogonal (η = 1) | −0.05 (−0.10) | +0.14 (+0.08) | +0.10 (+0.05) |
| forward chi-square, correct η | 0.00 | +0.05 (+0.03) | 0.00 |
| forward chi-square, η × 2 / η ÷ 2 | −0.01 / +0.01 | +0.08 / +0.03 | +0.03 / −0.02 |
| inverse, plain | +0.02 (+0.04) | +0.02 (+0.01) | −0.03 (−0.02) |
| inverse, slope corrected | 0.00 | +0.05 (+0.03) | 0.00 |

These match the quick check of 11 Nov (forward least squares +0.24, orthogonal +0.09 to +0.14, chi-square +0.05 to −0.01, inverse within ± 0.05). Castellaro et al. (2006) discourage inverted regression, and for a complete sample they are right: the plain inverse line is off by +0.02 to +0.04 there, and chi-square with the correct error ratio is exact. Our samples are not complete: the reference exists for under half of the events below native 5 (coverage figure). With a floor on the reference, least squares and orthogonal regression are biased by 0.1–0.26 at native 4.5, while the inverse fits stay within 0.05. Chi-square regression with the correct η does as well as the slope-corrected inverse fit in every case; it depends on knowing η (a factor 2 costs up to 0.03 more), the plain inverse fit does not. So the inverse step protects against the forms that fail (least squares, orthogonal, and curved forward fits, X1); against chi-square with a well-measured η its advantage is small, and on our pairs the two agree within 0.04 (section 3).

## 8. Draft methods paragraph (from REVIEW §6, numbers of this run where they changed)

> Native magnitudes were converted to Mw with one relation per agency and scale, fitted on Chilean event pairs by regressing the native magnitude on the reference Mw and inverting, with the slope corrected for the reference error. Global moment-tensor catalogues are incomplete below Mw 5.2–5.6, so a regression of Mw on the native magnitude selects pairs on its dependent variable, a truncated regression that is biased at the low end (Hausman and Wise 1977; Lolli et al. 2014, 2023). Regressing on the truncated variable avoids this, provided the native scale is reported independently of size, which holds for mb and ML (Supplement). Inverted regression is discouraged for complete samples (Castellaro et al. 2006); ours are not complete, and a synthetic test shows the inverse fit within 0.05 of the true relation where least-squares and orthogonal fits are off by 0.1–0.26. Below Mw 5.4 the reference is the regional and W-phase moment-magnitude family, whose members agree within 0.03 after constant offsets of at most 0.08. Only ISC and NEIC teleseismic magnitudes and the local magnitudes of the Chilean and Argentine networks are converted. GCMT reads 0.05–0.08 higher there, as found by Gasperini et al. (2012), and agrees above 5.4 (Lolli et al. 2023). Measured Mw takes precedence over converted values; a converted event takes one scale from a fixed priority list. [Test numbers to be filled after the decision of section 6.]

The inverse step is the method's new element for this purpose: no paper was found that proposes it for the incompleteness of the reference (REVIEW §5).

## 9. References for each choice (REVIEW §5; marks kept)

| step | support |
|---|---|
| Inverse regression | Hausman and Wise (1977) 10.2307/1912682; Heckman (1979) 10.2307/1912352; Lolli et al. (2014) 10.1093/gji/ggu264; Lolli et al. (2023) 10.1093/gji/ggad164; Di Giacomo et al. (2015); Castellaro et al. (2006); Osborne (1991) 10.2307/1403690; Fuller (1987); Gasperini et al. (2025) 10.1785/0120250007. Counter-position: Christophersen et al. (2024) 10.1785/0120230169; Llenos et al. (2026) 10.1785/0220250231 |
| Form | Gasperini et al. (2013b) 10.1785/0220130105; Lolli et al. (2014); Poulos et al. (2019); Deichmann (2017) |
| Reference Mw and order | Lolli et al. (2023); Gasperini et al. (2012) GJI 190:1733 (as cited by Lolli et al.); Di Giacomo et al. (2021) 10.5194/essd-13-1957-2021; Rovida et al. (2020) 10.1007/s10518-020-00818-y; Riquelme et al. (2018) |
| One proxy by a priority list | Allen et al. (2018); Christophersen et al. (2024). Mean of proxies: CEUS-SSC Eqs. 3.3.1-9/10; Lolli et al. (2023) |
| Surface-wave scale before mb, shallow events only, no magnitude limit | Di Giacomo et al. (2015) p. 3, p. 10; Engdahl and Villaseñor (2002) p. 3; Weatherill et al. (2016) Table 1; Lolli et al. (2023) p. 3–4 (depth < 50 km) |
| Rate bias (step B) | Tinti and Mulargia (1985) 10.1785/BSSA0750061681; CEUS-SSC §3.3.1; Musson (2012) 10.1785/0120110224; Mueller (2019) 10.1785/0220170108 |
| Validation | Lolli et al. (2014); Habermann (1991) 10.1016/0040-1951(91)90337-R; Zúñiga and Wiemer (1999) 10.1007/s000240050285; Tormann et al. (2010) 10.1785/0120090124 |

Not yet verified, check before citing: Felzer (2008); Mueller (2019) and Riquelme et al. (2018) beyond the passages read; the ESHM20 and Canada conversion rules; items marked (mem) in REVIEW §5.

## 10. Fourth run (13 Nov 2026)

Same rule as the third run, two changes (`magnitude.py`, `LOC` and `REG_TOL`):
- The depth for the depth split of the relations (50 km) and for the 60 km limit of the surface-wave scales is the A4 depth of `locations_2026-11-13.csv` where it is measured, else the A3 reference depth as before.
- A CSN regional Mw (GUC Mwr, CSN web Mw) more than 0.3 from the median of the event's other moment magnitudes (GCMT, NEIC Mww / Mwr / Mwb, GFZ, CSN Mww) is left out of the reference when the event has two or more of them: 26 values. With one other value (131 pairs, almost all against NEIC Mwr) nothing is dropped: the two have a similar error (about 0.11, from the pair differences) and NEIC Mwr is 0.15 lower on average. List: `merged/review/mw_reference_dropped_2026-11-13.csv`.

Effect at Mw ≥ 4.5 in the domain: 14 234 events (14 157), 613 values changed, 84 by 0.2 or more. NEIC mb is now split by depth (cross-validation 0.0410 against 0.0412 unsplit): 4.42 deep and 4.31 shallow at mb 4.5, against 4.35. Tests: 1 0.08 / 0.15; 2 13.8 %; 3 31 of 32 (Mw ≥ 7: 37.3 of 44); 4 16 of 20; 5 2.1 σ. The priority list is unchanged.

