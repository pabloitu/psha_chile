# CAT to FITS, 18 Nov: magnitudes of the Jujuy nest, and the large-magnitude fits

Answer to `handoffs/2026-11-17_FITS_to_CAT.md`. Figures (drafts, catalogue 17f with the A11 merges, not committed): `drafts/cat/mw_check/`. Nothing frozen yet; the next catalogue (17g) waits for your reply.

## 1. Jujuy nest conversions
- The nest ML values are converted by "GUC ML | deep" (> 50 km), fitted mostly on in-slab pairs near 110 km. Against the measured Mw at nest depth (about 205 km) it was 0.1 too high; ISC and NEIC mb were 0.1–0.15 too low there (`residual_depth.png`, left panel: as reported).
- Fix in `catalog/magnitude.py`: a third depth group below 150 km (top of `classify.NEST`), chosen by the same cross-validation as the other forms; taken for GUC ML, SJA ML, ISC mb and NEIC mb. Every scale is now within ±0.1 of the measured Mw at every depth (`residual_depth.png`, right panel).
- Effect on the nest b: none (1.45 → 1.46 from Mw 5.0 since 1976, events of most weight): ML values go down and mb values up by about 0.08. The nest bend is not a conversion artefact; the split direct / converted is the selection you described.

## 2. b above the fit floor up to 7 (`test1_b_floor_to7.png`)
- b against the floor for four catalogues: converted Mw, the native magnitudes (measured Mw where there is one, the native value otherwise), Cabello et al. (2025) and Candia and Macedo (2026), with 95 % bands (b/√n).
- From floor 5.8 up, all four agree within their bands (since 1976: b 0.85–1.1, no trend). Since 2011 the curves wobble 0.8–1.3 at 6.5–7, from few events.
- Reason: the larger the event, the more often its Mw is measured, so the conversion matters less. Since 1976 in the domain: Mw 4.5–5.0 24 % measured, 5.0–5.5 47 %, 5.5–6.0 72 %, 6.0–6.5 82 %, 6.5–7.0 85 %, ≥ 7 100 %.
- So a poor Gutenberg–Richter fit at large magnitudes does not come from the magnitude conversion; it is in the large events themselves (counts, periods, completeness) or in the fit.

## 3. Catalogue tests on the new conversions (A5)
All tests that passed on 17f pass, plus Mw 6.5–7 predicted from 5.0 (88.8 / 107). b range over floors 4.7–5.8: 0.05–0.16. Declustered M ≥ 5.5 rate drift: 13.6 %. M ≥ 7 predicted / observed: 37.9 / 43. Cabello and Candia–Macedo fail b range, rate and large-event tests (`test7_comparison.png`).

## Asked of FITS
Your view on the large-magnitude fits before CAT freezes 17g: is anything needed from the catalogue (magnitudes, completeness inputs, a list of the large events by class and period)?
