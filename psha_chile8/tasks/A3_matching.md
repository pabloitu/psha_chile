# Task A3: match events across the source catalogues, one ID per earthquake

Read first: `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (Catalog), `LEARNINGS.md` (Catalog pitfalls), `catalog/WORKPLAN_A3-A5.md` (sections 3.1 and 4, step A3), `catalog/SOURCES.md`, `catalog/NOTE_SRuiz_2026-11-10.md` (the corrected Ruiz and Madariaga dates), and `explore/X1/REPORT.md` tier 1 with its assumptions.

## Goal

Every record of the frozen source tables (`catalog/sources/*_2026-11-10_*`, plus `gccel_2026-11-11_*` from A2b) belongs to exactly one earthquake with one ID. Nothing is chosen yet: no location, depth or magnitude is picked (A4, A5).

X1 explored this (`explore/X1/x1_match.py`, `x1_io.py`). Turn what worked there into clean, tested code in `catalog/match.py`. Do not import from `explore/`; copy and simplify. The variant grid is not needed any more: one method, settings at the top.

## Method

1. **Inputs.** All origins of: `isc`, `iscehb`, `iscgem`, `gcmt`, `centennial`, `comcat`, `csn`, `csn_isc`, `potin`, `cabello` (rows before 1904 only), and `gccel` (frozen 2026-11-11 in A2b, 801 events). GCCEL has no ISC IDs, so it is matched by windows only; X3 linked 775 of 801 to the X1 baseline (`explore/X3/tables/x3_link_counts.csv`), and the 26 left are below the download floor or missed by every network (`x3_unlinked.csv`): they stay as GCCEL-only events. `comcat_mt` follows `comcat` by ID. GCMT is matched by its reference hypocentre, never by the centroid.
2. **Drop non-earthquakes** by the sources' event type (quarry blast, explosion, …). List what was dropped per source and type.
3. **Identity links (the backbone).**
   - ISC, ISC-EHB, ISC-GEM by ISC event / origin ID.
   - ComCat events that carry ISC-GEM IDs.
   - An agency's own solution found inside an ISC event: NEIC / USCGS / NEIS for ComCat, GCMT for GCMT, CENT for the Centennial, GUC for `csn` and `csn_isc`; accepted within 1.5 s and 10 km.
   - Identity links that disagree by > 30 s or > 100 km go to a review list, and stay linked.
4. **Window matching for what is left** (Potin, recent `csn`, unlinked records of any source, GCCEL).
   - Windows per pair of sources: the 99th percentile of the same-event offsets measured on known pairs (recompute them as X1 did; write the table), never below **10 s and 50 km**, capped at 120 s and 450 km. Pairs without known pairs: combine through the best shared source, as in X1.
   - Widened for large events: × 1.5 at M 6, × 2 at M 7, × 3 at M 8, using the largest native magnitude among the candidates. **Magnitude is never a matching criterion.**
   - Events before 1964: 60 s and 300 km; every such match goes to a review list.
   - One-to-one assignment per pair of sources and time block (Hungarian, cost from normalized dt and dd), built outward from the best-located source (Potin, GCCEL, ISC-EHB, ISC-GEM, Centennial, CSN, ISC, ComCat).
5. **Second pass.** Final events from different sources that lie within 10 s and 50 km of each other and share no source are merged. List every such merge with M ≥ 5.
6. **Ruiz and Madariaga (2018).** Not an event source. Replace its dates by the corrected readings first (table in `NOTE_SRuiz`; Mejillones 1994 is 1994-12-10). Match each of its events to one located event: ± 1 day, latitude within 2°, magnitude ≥ 5.5, closest in Mw where a day has several (logged). Events with year or month only, and unmatched ones, go to a review list. Taltal 1887 and Copiapó "1959" (= 1859) are not added as new events.
7. **IDs.** Stable and readable: `cl` + origin time of the best-located member to the second (e.g. `cl20100227063411`), with a letter suffix on collisions.

## Outputs (under `catalog/merged/`, dated)

- `events_<date>.csv`: `event_id`, time / lon / lat / depth of the best-located member (provisional, for A5 splits and for reading; A4 replaces it), list of member sources, n members, largest native magnitude with its type and agency, flags (`pre1964_window`, `second_pass`, `ambiguous`).
- `links_<date>.csv`: one row per source origin: `event_id, src, src_id, origin_id, rule` (id, foreign, window, second_pass, rm18), `dt, dd, dz` to the event's reference member.
- `windows_<date>.csv`: the measured windows per pair.
- Review lists in `catalog/merged/review/`: `id_disagree`, `pre1964_window`, `ambiguous` (≥ 2 candidates), `merges_m6` (every window or second-pass merge with M ≥ 6), `second_pass_m5`, `rm18` (side by side: RM18 values and each source's values for the matched event), `rm18_unmatched`, `dropped_types`.
- One figure, `figs/match/summary.png`: events per year with M ≥ 4.5 (any native), by number of member sources; and the dt / dd distributions of window matches against the windows.
- `DATA.md` row; `MANIFEST.csv` rows with sha256.

## Tests (`catalog/tests/test_match.py`)

- Assignment on a small synthetic set (two sources, a pair of close events, one-to-one holds).
- Window scaling by magnitude.
- The four known cases on small real samples cut from the frozen tables (commit them under `tests/data/`): Maule 2010-02-27, Illapel 2015-09-16 and Iquique 2014-04-01 mainshocks each end as one event with all their sources, and their first-hour aftershocks stay separate events; the Arauco 2011 duplicate (CSN vs GCMT, 6 s, 59 km) is merged.
- No source origin appears in two events; every origin of the inputs is in `links` or in `dropped_types`.

## Running

The full match takes minutes (X1: about 1 min after caching). Claude Code runs it in full and reports.

## Done when

- Tests pass.
- Splits and false merges, by the X1 diagnostics, are at or below the X1 baseline (121 and 202); if not, say why.
- At least 775 of the 801 GCCEL events are linked, and the unlinked ones are those listed in `x3_unlinked.csv` (or the difference is explained).
- M ≥ 4.5 events (any native magnitude) are within 22 300–23 200, or the difference is explained (GCCEL added, non-earthquakes dropped).
- The WORKLOG entry gives the counts per rule and per source, the size of each review list, and what Pablo should look at first.
- PLAN: move ← to A5 and tick A3 only after Pablo has gone through the review lists (leave the box for him; say so in the WORKLOG).

## Not in this task

Choosing location, depth, mechanism (A4) or magnitude (A5); the domain cut; classification. No edits to the frozen source tables.
