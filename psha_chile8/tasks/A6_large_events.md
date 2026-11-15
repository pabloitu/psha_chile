# Task A6: the large events, one by one

Needs: the working catalogue `catalog/merged/catalog_2026-11-13b.csv` and the review lists in `catalog/merged/review/`.

Read first: `CLAUDE.md`, `DECISIONS.md` (Catalog, Magnitudes (A5)), `LEARNINGS.md` (Catalog pitfalls, Working: the line on patch rules), `catalog/REPORT_A3-A5.md` (sections 5–7), `catalog/RULES_LOCATION_MAGNITUDE.md`, `catalog/NOTE_SRuiz_2026-11-10.md`, `catalog/LITERATURE.md` section 5 (large events, with the RM18 / Lomnitz / Centennial / Cabello table) and section 6, `catalog/PREFERENCES.md`.

## Why

The rules of A3–A5 are built for many events. The largest events are few, they control Mmax, the large-event rates and the hazard, and for them the literature often knows more than any catalogue: rupture studies give Mw, depth and mechanism; historical studies give the date and the setting. A6 checks each of them against the literature and records every correction with its source.

## Principle (the same for every event)

- **A value is changed only when a source that was read says so,** with author, year and page or table. No change without a citation; if the sources disagree and none is clearly better, keep the catalogue value and write the disagreement in the dossier.
- **Corrections are data, not code:** they go into one table, `catalog/overrides_A6.csv`, which `locate.py` / `magnitude.py` apply at the end of their run (a final step reading the table; flag `a6` on every changed field). No hand edits of merged files, no event-specific code.
- **Properties are corrected separately:** date / time, epicentre, depth (with σ), Mw (with σ), mechanism, existence (duplicate, not an earthquake, two events), and a **class hint** for A7 (interface, in-slab, crustal, outer rise) where a source states it. A7 decides the class; A6 only records what the literature says.
- **Ruiz and Madariaga (2018)** stays the authority for Mw and class of the events it names (DECISIONS), with the readings of `NOTE_SRuiz`.

## Which events

All in the model domain.

1. **Every event with catalogue Mw ≥ 7.0** (153: 53 before 1904, 57 in 1904–1963, 8 in 1964–1975, 35 from 1976).
2. **Every event with Mw 6.0–6.99 and no measured depth** (229, almost all before 1964). Depth and class hint are the main point here.
3. **Named cases from the A3–A5 report:**
   - 2010-02-27 08:25 (ML only → Mw 7.0) and 2011-01-07 04:55 (337 km, ML 6.8 → 6.6 with mb 5.1): `review/mw_large_proxy_2026-11-13b.csv`.
   - 1878-01-23, 1928-12-02, the 1919-03-02 pair, the Drake Passage events of 2025-05-02.
   - The 13 events of `review/mech_mw_differs_2026-11-13b.csv` (mechanism Mw ≥ 0.4 from the catalogue Mw; six of 2010 probably carry another event's tensor) and the 19 of `review/mech_m0_mismatch_2026-11-13b.csv`.
   - From LITERATURE.md and LEARNINGS: the 1960-05-22 18:56 Valdivia foreshock (ISC-GEM Mw 8.72 against 7.9), Aysén 1960-06-06 (Mw 7.2 or 7.7), Atacama 1922 depth, Chillán 1939, Calama 1950, the 1918 Copiapó dates, 1647 Santiago and Pica 1768 / 1786 (class hints only).
4. **Review lists, only their M ≥ 6 rows:** `mw_iscgem_centennial` (ISC-GEM vs Centennial ≥ 0.3), `id_disagree`, `pre1964_window`, `rm18_matches` with more than one candidate, `rm18_unmatched`, `close_events_m45`, `possible_splits`, `distant_events_2026-11-13b`.

Expected 400–450 events. Work in this order: from 1976 (best data, fastest), 1964–1975, 1904–1963, before 1904.

## For each event

1. **Dossier row** (`catalog/A6/dossiers.csv`, one row per event and property): every source value of that property from the links (source, value, flags), the catalogue's choice and its rule, and every literature value found, with reference and page.
2. **Literature, in this order:** `refs/catalogs/` PDFs and `LITERATURE.md` (already read); Ruiz and Madariaga (2018); Lomnitz (2004); Engdahl and Villaseñor (2002) Table 1; ISC-GEM and its literature Mw (Di Giacomo et al. 2015); for events from 1976, the finite-fault and W-phase products in ComCat and published rupture studies. **Web search is allowed to find papers, but a value is cited only from a paper or agency page that was opened and read**; anything seen only in an abstract or a search summary is marked † and not used for a change.
3. **Proposal** in `overrides_A6.csv`: `event_id, property, old_value, new_value, sigma, reference, page, reason, status` with status `proposed`. One sentence of reason.
4. **Events with nothing to change** get one line in the dossier saying "checked, no change", with the sources looked at.

Do not change: events below the selection; magnitudes of events with a measured Mw unless the measurement itself is shown wrong (wrong tensor, wrong event); anything by a rule of thumb.

## Outputs

- `catalog/A6/dossiers.csv`, `catalog/overrides_A6.csv` (all `proposed`), `catalog/A6/REPORT.md`:
  - counts: events checked, changes proposed by property and period;
  - a table of every proposed change with Mw ≥ 7 or a depth change ≥ 30 km or a Mw change ≥ 0.3, for Pablo to accept or reject one by one;
  - events still without depth after A6, with what the literature says about their setting (class hints);
  - references used, to add to `REFERENCES.md` (read ones only; † ones listed apart).
- Code: the final step in `locate.py` / `magnitude.py` that applies `overrides_A6.csv` rows with status `accepted` (none yet), a test for it, and a rerun showing that with no accepted rows the catalogue is unchanged.
- One figure, `figs/A6/large_events.png`: Mw against time for Mw ≥ 6, coloured by Mw kind, with proposed changes as arrows.

## Running

This is reading-heavy. Work period by period and write the dossier and the WORKLOG entry after each period, so the work survives a stop. If time runs out, stop at the end of a period and say where. Do not change PLAN boxes.

## End of session

WORKLOG entry as CLAUDE.md: periods done, counts, the short table for Pablo, references read and †, proposed DECISIONS line ("Large events: corrections only from cited sources, recorded in `catalog/overrides_A6.csv` and applied as the last step"), commands, suggested `git add` and commit message.

## Not in this task

Classification rules (A7), completeness and fits. Changes to the general rules of A3–A5: if a pattern shows up across many events, report it; do not change a rule.
