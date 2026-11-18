# CAT to FITS, 17 Nov: final catalogue 2026-11-17f

## What changed
The final catalogue is frozen: `catalog/frozen/2026-11-17f/catalog_2026-11-17f.csv` (CURRENT.md, DATA.md row "2026-11-17f"). Against 16e (and 16c, which the fits read):
- Five override rows: 1953-05-06 Chillán in-slab (was split, interface 0.27 / in-slab 0.70); 1952-06-11 San Juan crustal (was in-slab 0.56 / crustal 0.44); 1958-09-04 Las Melosas Mw 6.3 → 6.8; 2010-03-11 15:06 Pichilemu Mw 6.8 → 6.2 and crustal (was interface).
- Mechanisms before 1976 from the literature listed by ISC-GEM: 14 events of Mw 5.7–7.1 in 1962–1970 change class.
- Valdivia 1960 mechanism 7/20/105 (Barrientos and Ward 1990); no weight changes from it.
- Three 1960 events are now interface with weight 1: 1960-12-02 Mw 7.2 off Taltal (was crustal 0.78; depth 35 km from ISC-GEM), 1960-06-20 02:01 Mw 7.0 and 12:59 Mw 7.1 (were split; Cifuentes 1989). The 1960-12-02 event was the forearc Mmax question of 16 Nov.
- Totals, Mw ≥ 4.5 in the domain: interface 4 502.8 → 4 497.4, in-slab 8 075.3 → 8 079.8 (shallow 1 631.7 → 1 636.8, intermediate 5 389.6 → 5 389.0), crustal 1 145.9 → 1 146.8 (forearc 541.9 → 542.3, backarc 87.1 → 87.7). Same 164 events of Mw ≥ 7.
- 16e itself differs from 16c only in two epicentres (Aysén 1960, 1927-11-21).

## To do
1. Refit on `2026-11-17f` (full and declustered) with the next free fits date; then the model sessions rebuild on it.
2. Crustal fit figure: draw 1907-01-19 Magallanes, M 5.5 (Cabello et al. 2025, CERESIS-GEM Mw 5.47 ± 0.6; Lomnitz 1970) as a reference event, Patagonia class, not part of the catalogue (Pablo, 17 Nov). It is in Cabello only, after 1904, so the merge leaves it out.
3. Columns are unchanged; `mech_src` has new values `ISC-GEM literature` and `a6`.

## Checks
- `sha256sum -c catalog/frozen/2026-11-17f/SHA256SUMS` from that folder.
- Count of events of Mw ≥ 4.5 in the domain: 14 279.
