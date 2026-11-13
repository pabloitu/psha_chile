# Task A5: one Mw per earthquake

Needs: the A3 outputs (`catalog/merged/events_<date>.csv`, `links_<date>.csv`), reviewed by Pablo.

Read first: `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (Magnitudes (A5), Catalog), `LEARNINGS.md` (Catalog pitfalls), `catalog/WORKPLAN_A3-A5.md` (sections 3.3, 4 step A5, 6), `catalog/MAGNITUDE_PRIMER.md`, `explore/X2/REPORT.md`, `explore/X2/review/REVIEW.md` and `explore/X2/review/CANDIA_MACEDO.md`.

## Goal

Every event of the A3 catalogue gets one Mw with its error σ and the record it came from, on one Mw scale, by the rules in DECISIONS "Magnitudes (A5)". The result passes the acceptance tests below.

X2 (`explore/X2/x2_fit.py`, `x2_eval.py`) and its review (`r_robust*.py`) hold working code for most of this. Turn it into clean, tested code in `catalog/magnitude.py` (fits and assignment) and `catalog/magnitude_check.py` (tests and figures). Do not import from `explore/`. One method; the alternatives appear only in the sensitivity table.

## Method

1. **Magnitudes per event.** Join every row of the frozen `*_mags.csv` tables to its event through `links`. Keep agency and type as written. Leave out Potin magnitudes, GCCEL magnitudes (copies of the input bulletins, already present through ISC), and CSN / GUC coda and duration magnitudes before 1990.
2. **Reference Mw on one scale.**
   - Members: GCMT; NEIC Mww (ISC and ComCat); GUC Mwr and CSN web Mw; NEIC Mwr; GFZ Mw; CSN Mww.
   - Measure each member's offset to NEIC Mww on shared events, per 0.25 bin of Mw from 4.5 to 6.5. Members with a flat offset get a constant (X2 review: NEIC Mwr +0.10, GFZ +0.03, the others 0; re-measure, don't copy). Write the table and a figure.
   - GCMT below 5.4: read what Lolli et al. (2023) do with a GCMT value that has no other Mw (PDF in `refs/catalogs/`, or LITERATURE.md). Follow it. If they leave it unchanged or the paper is not clear, lower it by the measured offset per bin, and say which was done in the WORKLOG.
   - Reference value of an event: above 5.4 GCMT, then the W family in the order NEIC Mww, GUC Mwr / CSN web Mw, NEIC Mwr, GFZ, CSN Mww. Below 5.4 the W family in that order, then GCMT, with CSN Mww last below 5.0. ("Above / below 5.4" is judged on the GCMT value if there is one, else on the W value.)
3. **Conversion relations,** for each agency and scale with ≥ 100 pairs against the reference (scales with 30–100 pairs: straight line only; below 30: no relation).
   - Regress the native magnitude on the reference Mw; correct the slope for the reference error (σ 0.08 GCMT, 0.10 W family; from the data where possible); invert.
   - Candidates: straight line; line with a saturation hinge (slope drops above a fitted Mw); each without split, with a depth split at 50 km (provisional A3 depth; unknown depths in the shallow group), and, for ISC mb and NEIC mb, with a period split at 1990.
   - Choice by cross-validation in time blocks with the one-standard-error rule.
   - Outside the fitted range: continue the straight part; σ grows by 0.1 per magnitude unit beyond the range.
   - σ of a relation: the residual scatter after inversion, without the reference error counted twice (the review notes `conv_inv` overstates it by 0.01–0.02).
   - CSN web `Ml` uses the GUC ML relation (identical values in X1); `Mlv` gets its own relation if it has enough pairs, else the ML relation with the measured offset and a flag.
   - Bootstrap CIs of Mw at native 4.5 / 5.0 / 5.5 / 6.0 per relation.
4. **Proxy priority list.** Order the scales once by their σ; ISC mb and NEIC mb count as one measurement family (ISC first). MS, MOS mb and BJI mB are not eligible when their converted value is below Mw 5. Write the list into the settings at the top of the file and into the WORKLOG.
5. **One Mw per event.**
   - Ruiz and Madariaga Mw for the events it names (from the A3 `rm18` links; ranges and "~" values as in the frozen table's `note`, flagged).
   - else the reference Mw (step 2);
   - else, before 1976: ISC-GEM Mw, then the Centennial (Mw types as given, the others converted by their type as in X1), then Cabello for events before 1904. Keep the ISC-GEM vs Centennial order as one setting at the top (pending S. Ruiz). List every event of M ≥ 7 where ISC-GEM and the Centennial differ by ≥ 0.3;
   - else the first eligible scale of the priority list, converted;
   - else no Mw: the event is kept and flagged, and listed.
6. **Dither** converted values within the native 0.1 bin (uniform, fixed seed) before rounding Mw to 0.1. Keep the undithered value in its own column.
7. **Columns of the result** (`catalog/merged/mw_<date>.csv`): `event_id, mw, mw_sigma, mw_kind` (rm18 / direct / iscgem / centennial / cabello / proxy / none), `mw_src, mw_src_id, mw_agency, mw_type, native_value, relation_id, mw_raw` (before dither), `flags`.

## Acceptance tests (`magnitude_check.py`, table `mw_tests_<date>.csv`, one figure each)

Families for the per-family tests: the X1 depth proxy classes on the provisional A3 depth (crustal shallow, interface band, in slab). Declustering: Gardner–Knopoff, as X2.

1. **b against floor:** Aki b for floors 4.7–5.8, 2011 to today and 1976 to today, full and declustered. Pass: range ≤ 0.2.
2. **Rate steadiness:** declustered rate of M ≥ 5.0 and M ≥ 5.5 in 1976–89, 1990–99, 2000–10, 2011 to today. Pass: M ≥ 5.5 within ± 15 % of its mean.
3. **Large events:** doubly truncated GR fitted on Mw 5.0–6.5 (1976 to today); predicted against observed N in 6.5–7.0 and ≥ 7, overall and per family, floors 5.0 and 5.3. Pass: within the Poisson band of the observed count.
4. **Independent Mw:** for each main scale, converted value minus a regional Mw on events held out of that scale's fit (time blocks), by 0.25 bin from 4.0 to 5.5. Pass: |median| ≤ 0.1 from 4.5 up.
5. **Histogram:** events per 0.1 bin, 4.3–5.6, per period. Pass: no comb and no heap (neighbouring bins within the expected GR ratio; state the measure).
6. **1964–1975:** rate of M ≥ 5.5 against the later periods; ISC-GEM against our proxies on the same events.
7. **Comparison:** tests 1–3 for Cabello's own catalogue and for Candia and Macedo (2026) (their supplement read as in `explore/X2/review/r_candia_read.py`; if the xlsx is not on disk, skip and say so). One summary figure: b against floor, rates in time, and the M ≥ 7 ratio for the three catalogues. Add it to `FIGURES.md` as a paper candidate.
8. **Sensitivity table:** tests 1–3 for (a) GCMT first at all magnitudes, (b) the error-weighted mean of proxies in place of the list (generalized least squares with the measured correlation between scales), (c) straight lines only, (d) Centennial before ISC-GEM, (e) no slope correction and slope correction with σ 0.15, (f) forward chi-square regression (Mw on native, straight line, error ratio η from the measured σ of each scale and of the reference), the strongest conventional alternative (Castellaro et al. 2006; Lolli et al. 2014).
9. **Synthetic comparison of the regression methods** (supplement figure, and the answer to the Castellaro et al. 2006 objection to inverted regression). A Gutenberg–Richter population (b = 1), a native scale with a known linear relation and σ 0.20, a reference Mw with σ 0.08. Methods: forward OLS, forward orthogonal (η = 1), forward chi-square with the correct η, inverse plain, inverse slope-corrected. Cases: (i) every event paired; (ii) pairs only above a GCMT-like floor (Mw 5.3), with the floor applied to the measured Mw; (iii) the same with the floor applied to the true size. Show the bias of the converted Mw against native magnitude 3.5–6.5 for each method and case, and repeat with η wrong by a factor 2 for the chi-square fit. Expected (quick check in the project conversation, 11 Nov): with every event paired chi-square is exact and plain inverse is +0.02 at native 4.5; with the floor, forward OLS is +0.24, orthogonal +0.09 to +0.14, chi-square +0.05 to −0.01, inverse within ± 0.05. Put the figure and a short paragraph in `MAGNITUDES.md`.

If a test fails, do not tune until it passes. Report the failure, the likely cause and the options in the WORKLOG; Pablo decides.

## Other deliverables

- `catalog/merged/relations_<date>.csv`: per relation: agency, type, split, form, coefficients, range, n, σ, CIs, CV score, and the scores of the rejected candidates.
- `catalog/MAGNITUDES.md`: a short methods note for the paper: the rules as applied, the table of relations, the offsets, the priority list, the test results, and the stated assumptions (selection acts on the reference, not on the native scale; reference σ; the slope correction as a ± 0.05 systematic at native 4.5). Take the draft paragraph and the reference table of `REVIEW.md` §5–6 as the starting point; keep its "not yet verified" marks. State plainly that the inverse step is the method's new element, that Castellaro et al. (2006) discourage inverted regression for complete samples, and why our samples are not complete (test 9).
- Figures in `figs/magnitude/`: reference offsets; one panel per main scale with pairs, the chosen relation, the rejected forms and the 1:1 line; the test figures. Figure style as CLAUDE.md.
- Tests in `catalog/tests/test_magnitude.py`: inverse regression recovers a known relation on synthetic GR data with a reference cut-off, where the forward fit fails; the hinge reduces to the line on linear data; dithering keeps the mean and removes the comb; the hierarchy picks the right record on hand-made events (GCMT 5.2 + Mww 5.1 → Mww; GCMT 6.0 + Mww 6.0 → GCMT; MS-only at converted 4.7 → not eligible).
- `DATA.md` row for the run; MANIFEST rows.

## Running

Fits and checks take minutes (X2: about 2 min). Claude Code runs them in full.

## Done when

- Tests pass; the acceptance table is complete, including the sensitivity row (f) and the synthetic comparison (9); every event has an Mw or is in the no-Mw list.
- WORKLOG entry: results of tests 1–8 in one small table, what failed if anything, the priority list, how GCMT below 5.4 was treated, proposed DECISIONS / LEARNINGS lines, commands, suggested `git add` and commit message.
- PLAN: leave the A5 box for Pablo; move ← to A4.

## Not in this task

The rate correction for magnitude error (step B; the CEUS-SSC equations are re-checked there). Location, depth, classification. Completeness and b-value methods beyond the tests above.
