# Crustal model, summary figures (S3, 16 Nov 2026)

Copies of the figures of `figs/2026-11-16e/` that tell the story, in reading order. Built on fits 2026-11-16f (identical to 16e for the crustal classes), catalogue 2026-11-16c, fault database A (B and B-MASCSN as rows). Sources: `figs_s3.py`, `figs_checks.py`, `fagnano_row.py`.

| file | what it shows |
|---|---|
| 01 / 01b `background_pattern_*` | smoothed rate per class and all classes, N(≥ 5) per cell, Gardner–Knopoff / nearest neighbour (own kernel n per class) |
| 02 `class_fits_vs_catalogue` | the four class fits (one family b) against the catalogue since 1976, tapered and cut, 5–95 % band |
| 03 `join_faults_background_A` | per class: fit, faults (tree range), background after the join, sum, observed; the arc twice (single faults, multi-fault) |
| 04 `multifault_rupture_set` | the strict UCERF3 scenarios of Liquiñe–Ofqui per jump and trace rule (largest four each) |
| 05 `largest_ruptures` | the largest potential ruptures, main traces, with splays, and north of Liquiñe–Ofqui |
| 06 `multifault_mfd_jump_thickness_A` | faults + background per 0.1 bin for jump 5 / 10 / 15 km × thickness 10 / 20 km × ψ, with the count tests and the historical events |
| 07 `count_tests_all_cases` | expected arc Mw ≥ 6 (1976–) against Mw ≥ 7 (1905–) for every fault model; the Poisson box of the observed counts |
| 08 `counts_by_magnitude` | per class, counts above Mw 5–7.5 in their windows: fit, single faults (A, B, B-MASCSN), multi-fault |
| 09 `moment_rates` | catalogue moment rate against fit, faults and faults + background per class |
| 10 `near_fault_share` | share of observed Mw ≥ 6 within 20 km of a trace against the model's fault share |
| 11 `mmax_pad_rows` | the Mmax pad rows: background pad through the join and the multi-fault cap, and the single-fault Leonard pad |
| 12 `fagnano_row` | Magallanes–Fagnano as separate traces with SHERIFS against the joined system source |
| 13 `fault_share_map` | fault share of N(≥ 6) per 0.5° cell, three databases |

The 196 scenario pages (one per Liquiñe–Ofqui scenario, largest first) stay in `figs/2026-11-16e/scenarios_j15_main/` and `scenarios_j15_all/`.
