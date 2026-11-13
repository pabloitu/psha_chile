# Task A4: one location, depth and mechanism per earthquake

Needs: the A3 outputs (`catalog/merged/events_<date>.csv`, `links_<date>.csv`, latest run). A5 is not needed; if `catalog/merged/mw_<date>.csv` exists, join it at the end.

Read first: `CLAUDE.md`, `DECISIONS.md` (Catalog), `LEARNINGS.md` (Catalog pitfalls), `catalog/WORKPLAN_A3-A5.md` (sections 3.2 and 4, step A4), `catalog/PREFERENCES.md`, `catalog/SOURCES.md`, `explore/X1/REPORT.md` tier 2, `explore/X3/REPORT.md`, the "For A4" point of the A3 WORKLOG entry.

**Location rule decided by Pablo on 11 Nov 2026, after X3 and A3.** It replaces the DECISIONS line "Location and depth: the local relocated catalogue first … with no regional or depth exceptions". The new DECISIONS line is pending (Pablo adds it); follow this brief, and do not stop over the old line.

## Goal

Every event gets one epicentre, origin time, depth (or "unknown"), a depth error, and a mechanism where one exists, each traceable to one source record. **The main aim is to avoid fixed and default depths wherever any source has a measured depth.**

X1 (`explore/X1/x1_loc.py`) and X3 (`explore/X3/x3_gccel.py`) hold working code for most of this. Write `catalog/locate.py`, tested; do not import from `explore/`.

## Rule

One principle for every local catalogue: **a local catalogue comes first only inside its own network**, the area its authors say is well resolved. Elsewhere the global sources come first and the local catalogue is the last fallback.

1. **Inside the network** (Potin from 1982 to 2020-07-16, CSN web after): epicentre at 18–46° S (Potin et al. 2024, relocation domain) and not in the backarc (east of the arc polygon `data/intraarc.shp`; events east of the Andes are poorly located, Potin et al. 2024 p. 5). The test is made on the epicentre of the event's teleseismic members (ISC-EHB, then ISC, then ComCat) where it has one, otherwise on the local record itself. This also catches distant events that the CSN mislocated into the network (A3: 629 events with a member > 30 s or 100 km off).
2. **Order inside the network:** Potin / CSN web → GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → CSN in ISC.
3. **Order outside the network, and 1964–1981:** GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → Potin / CSN web → CSN in ISC.
4. **Before 1964:** the Centennial where it is EHB-relocated (1918–1942, 1956 on), ISC-GEM otherwise; then ISC. Before 1904: Cabello's epicentre, depth unknown.
5. **Epicentre and origin time** from the first source in the order.
6. **Depth** from the first source in the same order with a **measured** depth. Not measured: flagged fixed in the source (`depth_fixed`), ISC-EHB L3, GCCEL depth codes c / i / u, and any depth on a default bin of its agency. Refresh the default table on the frozen data with the X1 method (1 km bins, spike > 5 × the median of the ± 5 km neighbours, per agency and period; also ComCat 10 / 33 / 35, ISC 35 and its cell depths, GCMT 12, EHB 10 / 15 steps, ISC-GEM 15 / 35). GCMT centroid depths are never used. No source with a measured depth: depth unknown, flagged. No filling from Slab2.
7. **Depth error σ per event:** from `explore/X3/tables/x3_depth_error_model.csv` by source and depth range (< 30, 30–70 km); at ≥ 70 km the X1 values; for sources or ranges not covered, the largest σ of that range, flagged. Offshore events (epicentre offshore): σ at least 10 km (X3).
8. **Mechanism:** ComCat moment tensor (W-phase first), then GCMT. Check the scalar moment against the tensor (the Maule WCMT product is wrong) and keep the tensor value. ComCat products before 1996 are focal mechanisms without moment: keep nodal planes, no moment.
9. **Domain flag:** `in_domain` on the final location: south of 17° S, longitude −78.5 to −65.0 (RULES.md), to the end of the Antarctic interface. Do not delete events outside; flag them.

## Outputs (`catalog/merged/`, dated)

- `locations_<date>.csv`: `event_id, time, lon, lat, loc_src, loc_src_id, depth, depth_sigma, depth_src, depth_kind` (measured / unknown), `inside_network, offshore, in_domain`, mechanism columns (`mech_src`, nodal planes, tensor, M0), flags.
- `defaults_<date>.csv`: the default-depth table used.
- If `mw_<date>.csv` exists: `catalog_<date>.csv` = locations joined with Mw (one row per event), and the count of events with final Mw ≥ 4.5 in the domain.
- DATA.md row; MANIFEST rows.

## Checks and figures (`figs/locate/`)

1. **Fixed and default depths:** share of events whose final depth is unknown, and how many were saved from a default by a later source, by period, region (2° bands; inside / outside the network) and magnitude (all, M ≥ 4.5 by any native or final Mw).
2. **Against GCCEL:** mean epicentre distance and |Δz| of this rule against "Potin first everywhere" (the X3 L-e0 order) on the GCCEL events, by group (crustal onshore, crustal backarc, interface / slab onshore, offshore), as in X3.
3. **Who decides:** map of the first source per event (M ≥ 4.5), and counts per source and period.
4. **Sections** with pituPLOTS at 20°, 23°, 27°, 31°, 33.5° and 37° S, perpendicular to the trench, 50 km strip, Slab2 top and bottom, M ≥ 4.5, coloured by depth source. The Potin cloud at 31° S, 100–170 km, is flagged in the WORKLOG, not corrected (DECISIONS: events below the slab count as in-slab, A7).
5. **The A3 distant-event list** (629 events): how many now take a teleseismic location.

## Tests (`catalog/tests/test_locate.py`)

Hand-made events: inside / outside the network (including a mislocated distant Potin record); a fixed depth skipped for a later measured one; all depths fixed → unknown; a default-bin depth recognised; GCMT centroid never chosen; the Maule moment check.

## Running and end of session

Claude Code runs it in full (expected minutes). WORKLOG entry as CLAUDE.md: the check results in one small table, the proposed DECISIONS line for the location rule (wording of the rule above), commands, suggested `git add` and commit message. PLAN: leave the A4 box for Pablo.

## Not in this task

Classification (A7), large-event review (A6), magnitudes (A5).
