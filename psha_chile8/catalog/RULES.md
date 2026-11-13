# Catalog rules (plan A1)

Draft 2026-11-09. Items marked TODO need Pablo's input (from the meeting with S. Ruiz).

## From S. Ruiz
1. Cabello et al. (2025) is not used for events from 1900 on. TODO: also not as a source of agency rows (e.g. CSN)? Before 1900: Cabello / CERESIS-GEM, or the original historical catalogue?
2. Source order. TODO, separately for:
   - magnitude:
   - location (epicentre, depth):
   - mechanism:
3. Mw conversion redone (plan A5).
4. In-slab split into upper and lower plane of the double seismic zone (plan A7).
5. Ruiz and Madariaga (2018) authoritative for class and Mw of its events (kept from cat_handler_2 unless he said otherwise).

## Domain (TODO confirm)
- south of 17°S, to the end of the Antarctic interface; lon box as before (−78.5 to −65.0)
- 1513–2022 (training cut for the pseudo-prospective test at 2009-12-31)
- keep events with final Mw ≥ 4.5; download native magnitudes from 3.5 so the conversion is not truncated

## Carried over from cat_handler_2 / A2 (lessons, not rules from Ruiz)
- Match across catalogs by time and distance only; never with a magnitude criterion (it biased the calibration pairs). Wider windows for large events (Arauco 2011 duplicate: CSN vs GCMT 6 s, 59 km).
- Agency default depths found as histogram spikes, per agency; defaults treated as unknown. CERESIS depths before 1964 at round values treated as unknown, not free.
- Each converted Mw from the native value and scale, never from a precomputed Mw column. Relations fitted with errors in variables against GCMT, split by depth where needed; ISC mb saturation above about 5.3; Md, Mc and unspecified m converted, not taken as Mw.
- Dithering within the native 0.1 bin before rounding (heaping from slope < 1 relations).
- One ID per event, all choices traceable to a source row.
