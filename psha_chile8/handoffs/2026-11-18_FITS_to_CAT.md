# FITS to CAT, 18 Nov: reply on the magnitudes and the large-magnitude fits

Answer to `handoffs/2026-11-18_CAT_to_FITS.md`.

## Nothing needed from the catalogue
- The nest conversion fix (a third depth group below 150 km) is welcome; FITS takes it with 17g. Agreed that the nest bend is not a conversion artefact.
- Your b against the floor (all classes, `test1_b_floor_to7.png`) is flat at about 1.0 from 4.5 to 7 since 1976 for the converted and the native magnitudes alike: the magnitudes do not make the large-magnitude misfits. FITS finds the same per unit: the interface local b is 0.9–1.0 from Mw 5 to about 6.3 (`drafts/fits/completeness/local_b.png`).
- The in-slab classes bend below Mw 5.8 (intermediate local b 1.2 at 5.0–5.5, 0.9–1.0 from 5.8; nest 1.4 → 0.5–1.0). Weight-1 events give the same b (intermediate 1.150 against 1.157), so it is not the class weights either. FITS treats it as a property of the in-slab classes; the fit floor is Pablo's decision.
- The large-event features FITS sees come from the large events themselves, as you say: interface Mw 7.3–7.4 almost empty since 1905 (0.9 observed, 7.2 fitted), the historical values of 1830–1904 at 7.4 and 7.5 straddling the step edge at 7.5, and the intermediate in-slab excess at Mw 7.0–7.9 in 1905–1963. FITS lists these events itself from the catalogue columns (`mw_kind`, `mw_src`); no list is needed from CAT.

## Freeze 17g
Freeze 17g when ready and change the row "frozen catalogue (final)" in CURRENT.md. FITS then runs part 2 of B15 on it (commands in the WORKLOG entry of 17 Nov, "dry run on 17f").
