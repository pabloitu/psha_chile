# X2: magnitude homogenization that holds from Mw 4.5 to the large events

Follow-up to X1, finding 13 (fits at floor 5.0 under-predict M ≥ 7). Same frozen tables and X1 baseline events, nothing under `catalog/` changed. Scripts: `x2_prep.py` (inputs from the X1 cache), `x2_fit.py` (fits, Mw variants), `x2_eval.py` (checks, figures). Tables in `tables/`, figures in `figs/` (`figures_index.md`), tests `pytest explore/X2/tests` (4 pass, together with the 8 of X1).

## Summary

1. **The M ≥ 7 deficit was a magnitude artifact, not a property of the data.** In 1976–1999, 1 754 proxy-converted events sat in Mw 5.0–5.5 against 363 with direct Mw. The step N(≥ 5.0)/N(≥ 5.5) implied b ≈ 1.5, while above 5.5, where direct Mw dominates, b ≈ 1. A GR fitted on 5.0–6.5 then predicted 0.12× the observed M ≥ 7 (X1 M0). `figs/x2_fmd.png`
2. **Cause:** every forward fit (Mw on native, by OLS or chi-square) uses pairs selected on Mw, because GCMT reports few events below Mw 5.2–5.6 (depending on period). At a low native value, only the events with a high Mw have a pair, so the fit over-predicts Mw there. Black ▼ against red ▶ in `figs/x2_relations.png`.
3. **Fix: regress native on Mw, then invert.** Selection on the regressor doesn't bias a regression. The error of Mw (0.08–0.10) is corrected for in the slope. A test on synthetic GR data with a GCMT-like floor recovers the slope within 0.04, while the forward fit is off by more than 0.2 at native 4.0 (`tests/test_x2.py`).
4. **Second reference below the GCMT floor:** USGS Mww, CSN Mww, GUC Mwr, CSN web Mw, NEIC Mwr (+0.10) and GFZ Mw (+0.03) agree with each other within 0.0–0.03 from Mw 4.5 to 7, measured on pairs whose mean is at least 5. Together they reach Mw 3.8 from 2011 on (the "W" composite).
5. **Recommended: INV-W linear mean.** One straight line per native scale (native on the W composite, GCMT where no member exists), no depth or period splits, and the inverse-variance mean of all proxies per event.
   - Out-of-sample large events: a GR fitted on Mw 5.0–6.5 (1976–2026) predicts 40.5 M ≥ 7 against 41 observed; declustered, 36.6 against 36.
   - The same per family: interface 22.4 / 20, in slab 13.8 / 12, crustal 4.6 / 5.
   - Mw 6.5–7: 91.5 against 97 observed.
   - b moves by only 0.13 across floors 4.7–5.8 (X1 M0: 1.1–1.5; Cabello: 0.47–0.55).
6. **Cabello's catalogue is inhomogeneous in time.** Its declustered rate of M ≥ 5.5 falls from 29.9/yr (1976–1989) to 14.4/yr (2011–2026), and of M ≥ 5.0 from 88 to 77/yr. INV-W linear mean holds 14.6–17.5/yr at M ≥ 5.5 and 43–51/yr at M ≥ 5.0. The direct-Mw-dominated rate at M ≥ 5.5 is the same in X1 M0 and here (14–17.5/yr), so it is Cabello that drifts. `tables/x2_rates.csv`
7. **For small events, mb ≈ Mw.** With either reference, ISC mb 4.5 → Mw 4.44–4.51 and 5.0 → 5.06; NEIC mb 4.5 → 4.35–4.43. GUC ML ≈ Mw (slope 0.99). By period (1976–89, 1990–99, 2000–10, 2011–26), Mw at ISC mb 5.0 stays within 4.95–5.18. The published GCMT-based relations (and X1) give 4.8–5.0 at mb 4.5. That is the same selection bias. `tables/x2_stability.csv`
8. **The simple model is the better one.** Hinged and depth-split fits, chosen by time-block cross-validation with a one-standard-error rule, score no better than the straight lines. Below Mw 4.3 they are worse: their extrapolations differ more from the regional Mw. Saturation of mb above Mw ~6 is real, but events above 5.5 since 1976 have direct Mw, so it barely matters for the catalogue.
9. **What failed:** truncated forward regression (TRUNC-G). Above the GCMT completeness only the saturated range remains, so the relations are too steep (Mw 0.3–0.9 too low at mb 4–5) and the FMD breaks. Dropped.
10. **M ≥ 8 is not predicted**, as expected: 4–5 observed since 1976 against about 2.3 from the GR. That is a question for the source model, not for the homogenization.

## Variants (all on the X1 baseline events; direct Mw and pre-1976 handling as in X1 unless stated)

| name | reference for the fits | form | proxies per event | direct Mw first |
|---|---|---|---|---|
| X1 M0 | GCMT, forward chi-square | linear / quadratic / exponential by BIC, splits | smallest σ | RM18 > GCMT > CSN Mww > USGS Mww |
| X1 M2 linear | same, linear only | linear | smallest σ | same |
| Cabello | Cabello et al. (2025), its own events and values | | | |
| INV-G | GCMT, inverse | CV choice (linear / hinge, depth split) | smallest σ | as X1 |
| INV-G mean | same | same | inverse-variance mean | as X1 |
| INV-G linear | GCMT, inverse | linear, no split | smallest σ | as X1 |
| INV-W, INV-W mean | W composite, inverse | CV choice | smallest σ / mean | RM18 > W family > GCMT |
| INV-W linear | W composite, inverse | linear, no split | smallest σ | RM18 > W family > GCMT |
| **INV-W linear mean** | W composite, inverse | linear, no split | inverse-variance mean | RM18 > W family > GCMT |
| TRUNC-G | GCMT, truncated forward ML | CV choice | smallest σ | as X1 |

## Scores (`tables/x2_scores.csv`)

All region; "decl" = Gardner–Knopoff declustered; b range = max − min of Aki b over floors 4.7–5.8, 2011–2026; N7 = predicted / observed M ≥ 7, 1976–2026, from a doubly truncated GR fitted on 5.0–6.5; the last two columns are median differences (Mw), averaged over scales and bins 3.5–5.5.

| variant | b range decl | N7 full | N7 decl | rate M ≥ 5 decl, cv | between converted scales | against regional Mw (events with no direct Mw) |
|---|---|---|---|---|---|---|
| X1 M0 | 1.09 | 0.12 | 0.17 | 0.07 | 0.13 | 0.21 |
| X1 M2 linear | 0.25 | 0.58 | 0.63 | 0.07 | | |
| Cabello | 0.47 | 0.75 | 0.88 | 0.13 | | |
| INV-G | 0.20 | 0.85 | 0.87 | 0.13 | 0.13 | 0.10 |
| INV-G linear | 0.21 | 0.92 | 0.93 | 0.16 | 0.11 | 0.07 |
| INV-W | 0.13 | 1.12 | 1.01 | 0.13 | 0.13 | 0.06 |
| INV-W linear | 0.15 | 1.02 | 1.05 | 0.17 | 0.10 | 0.06 |
| **INV-W linear mean** | 0.13 | 0.99 | 1.02 | 0.08 | | |

Poisson scatter on 36–45 observed events is ±15–17 %, so every INV variant passes the large-event test, and X1 M0, X1 M2 and Cabello (full) do not. X1 M0 has the lowest rate cv at M ≥ 5 only because its heap at 4.7–4.9 fills 5.0 evenly in every period.

## Relations (INV-W linear, `tables/x2_fits.csv`, fit `inv-lin W`)

Mw at native 4.0 / 4.5 / 5.0 / 5.5 / 6.0, and residual sd of the native value:

| scale | pairs | Mw | sd |
|---|---|---|---|
| NEIC mb | 5 711 | 3.70 / 4.35 / 5.01 / 5.67 / 6.32 | 0.20 |
| ISC mb | 5 467 | 3.81 / 4.44 / 5.07 / 5.70 / 6.33 | 0.22 |
| GUC ML | 4 416 | 4.00 / 4.51 / 5.01 / 5.51 / 6.02 | 0.25 |
| VAO mb | 3 282 | 3.87 / 4.45 / 5.03 / 5.62 / 6.20 | 0.23 |
| SJA ML | 2 993 | 4.04 / 4.57 / 5.09 / 5.62 / 6.15 | 0.28 |
| ISC MS | 2 451 | 4.68 / 5.07 / 5.46 / 5.84 / 6.23 | 0.23 |
| MOS mb | 1 906 | 3.24 / 3.98 / 4.72 / 5.46 / 6.20 | 0.24 |
| BJI mB | 1 363 | 3.55 / 4.21 / 4.86 / 5.51 / 6.17 | 0.21 |

Above the fitted data range a straight line overshoots for saturating scales (mb above ~6.2). Those events have direct Mw since 1976; before 1976 ISC-GEM comes first.

## Why this justifies our own conversion over Cabello's

- **Cabello** has a time-dependent scale: the M ≥ 5.5 rate halves over 1976–2026. Its b moves by about 0.5 with the floor. Its file mb relation is 0.3–0.4 too high (X1), and it passes Mc, Md and m through as Mw.
- **INV-W linear mean** holds the M ≥ 5.5 rate within ±10 % across four periods and keeps b flat from 4.7 to 5.8. A GR fitted on 5.0–6.5 reproduces the observed Mw 6.5–7.0 and M ≥ 7 counts, overall and per family. Converted values agree with an independent Mw to 0.06 down to Mw 3.8. It uses one straight line per scale, with no form or split chosen per scale.

## Assumptions

- Mw errors of the references: 0.08 (GCMT), 0.10 (W composite). With GCMT alone the result depends on this choice: at σ = 0.15, ISC mb 4.5 → 4.69 instead of 4.51, because the narrow, censored GCMT range amplifies the correction. With the W composite it hardly matters (4.46–4.48). That is one more reason for W.
- GCMT completeness used for TRUNC-G: 5.6 (to 1989), 5.4 (1990–2003), 5.3 (2004–2014), 5.2 (2015 on), read from the GCMT magnitude histograms.
- The W composite takes NEIC Mww, CSN Mww, GUC Mwr, CSN web Mw, NEIC Mwr and GFZ Mw in that order, each shifted to NEIC Mww. GCMT is used where none exists.
- Families as in X1 (L-a proxy classes). GK declustering from M 3.5. Large-event test 1976–2026 only, since pre-1976 events depend on ISC-GEM and Centennial and were not changed here.

## Limits and open points

- The regional Mw used in the W fits may be computed only for events whose CSN ML passed a threshold, which is selection on a native scale and would bias the inverse fit the other way. INV-G uses GCMT only, so it can't be biased this way, and it gives the same answer within 0.07 at mb 4.5, so the effect looks small.
- The "against regional Mw" check is not independent for the W variants; INV-G passes it at 0.07–0.10.
- GCMT sits 0.04–0.10 above the W family below Mw 5.4. INV-W puts the catalogue on the W scale there; above 5.4 the two agree. This changes the DECISIONS hierarchy (GCMT first). Pablo decides.
- The proxy mean is a change from DECISIONS (smallest σ). INV-W linear (smallest σ) scores almost as well.
- Below about Mw 4.3 the conversions are extrapolations for most scales before 2011.
- b in 2011–2026 drifts from 0.95 to 0.80 between floors 5.2 and 5.8 in every variant, including the direct-Mw part. That is the data (large sequences), not the conversion.
- 1964–1975 is not tested.

## Run times

`x2_prep.py` 25 s, `x2_fit.py` about 1 min, `x2_eval.py` 15 s.
