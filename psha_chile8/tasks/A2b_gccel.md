# Task A2b: add GCCEL as a source and use it as the location benchmark

Read first: `CLAUDE.md`, `DECISIONS.md` (Catalog: the GCCEL line), `catalog/PREFERENCES.md` (location after the local catalogue), `catalog/SOURCES.md`, `tasks/A2_sources.md` (format of the frozen tables), `explore/X1/REPORT.md` tier 2 (finding 6: Potin under the flat slab).

## Goal

GCCEL (Global Catalog of Calibrated Earthquake Locations; Bergman et al. 2023, SRL 94(1) 485–495, doi 10.1785/0220220217) is frozen like the other sources. Its calibrated hypocentres (epicentre about 1–5 km, depth usually ≤ 5 km) are used to measure how well each other source locates the same events, by depth range and region. The measurements answer two questions:
1. How far behind GCCEL does the local-first order put us in each depth range and region?
2. Should ISC-EHB L1/L2 come before Potin below about 70 km?

## 1. Fetch and read

- **Source.** ISC Seismological Dataset Repository, doi 10.31905/MFDY4QHD, `Distribution_v20230722.zip` (436 MB): `all_gccel.dat.zip`, `byCountry.zip`, and the format PDFs (`GCCEL data format.pdf`, `Summary file format.pdf`). The USGS data release (doi 10.5066/P95R8K8G, ScienceBase) is the second option.
  - Check whether a newer version exists on either site and take the newest. Record the version.
  - Also check whether ComCat carries GCCEL origins (as a contributing catalogue in the event products). If it does, note it, but freeze the repository file.
- **fetch.py:** add `gccel`: download into `sources/raw/gccel/`, unzip, write `fetch.json`. If the download needs a form or fails, stop and tell Pablo the file names to fetch by hand, as for ISC-GEM.
- **read.py:** add a reader into the three common tables, `sources/gccel_<date>_{events,mags,mechs}.csv`, cut to the A2 box (lat −58 to −15.5, lon −80 to −60, any origin inside).
  - **events:** keep the calibrated hypocentre, its uncertainties (epicentral ellipse or 90 % semi-axes, depth uncertainty), the depth constraint code (how the depth was set: local distance, depth phases, waveform, fixed), the cluster name and the calibration level (the GT / CE class, if the file gives one) in `depth_quality` and `note`. Map the depth constraint code to `depth_fixed`.
  - **mags:** whatever magnitudes the file carries, with their source.
  - **mechs:** none, unless the file carries them.
  - The CHECK lines as for the other sources.
- **Bookkeeping:** MANIFEST row, DATA.md row, SOURCES.md card (coverage in the box: clusters, events, years, depth range; format notes; issues), profile figure with `profile.py`, and a reader test on a small real sample in `tests/data/`.

## 2. Benchmark (exploration, in `explore/X3/`)

Use the X1 matching (`explore/X1`, baseline variant) to link GCCEL events to the other sources. GCCEL is not in the X1 cache, so match it to the X1 baseline events with the baseline windows. Report how many link, how many don't, and why.

For every source that shares events with GCCEL (Potin, csn, csn_isc, ISC prime, ISC-EHB by L1 / L2 / L3, ComCat, ISC-GEM, GCMT hypocentre and centroid, Centennial):
- **Differences against GCCEL:** horizontal distance and depth difference (source − GCCEL). Give median, robust spread (1.4826 × MAD) and the 90th percentile of |Δ|. Split by:
  - depth range: < 30, 30–70, 70–120, > 120 km
  - region: GCCEL cluster, latitude band, and in or out of the flat slab (30–34°S)
  - period
- **Depth-error model per source,** from the GCCEL differences, as the input for the location-priority rule in A4.
- **Potin and ISC-EHB at depth:** at 70–120 and > 120 km, in and out of the flat slab, check which of the two is closer to GCCEL where both exist. This is the test of X1 finding 6. If GCCEL has no clusters at those depths in the flat slab, say so plainly; the decision then rests on X1 alone.
- **The X1 location variants** (L-a to L-d), plus a new L-e: local first, then GCCEL, then EHB L1/L2, then ISC, then ComCat, and below 70 km EHB L1/L2 before Potin. Score each by its mean |Δ| against GCCEL on the shared events.

Figures:
- map of GCCEL clusters in the box, coloured by depth
- Δ horizontal and Δ depth against GCCEL per source, by depth range (box or violin plots)
- Potin vs ISC-EHB depth against GCCEL, at depth, in and out of the flat slab
- scores of the location variants

Report: `explore/X3/REPORT.md`, with a summary, the tables and figures, and a "what this suggests" block (options, not decisions) for the A4 location rule.

## Running

Claude Code may run the fetch (one download), the reader and the benchmark in full. All of it is small.

## End of the session

As CLAUDE.md:
- WORKLOG entry, with the commands and the suggested `git add` lines
- DATA.md and SOURCES.md rows for gccel
- proposed DECISIONS / PREFERENCES lines in the WORKLOG only
- no PLAN ticks (A2 stays ticked; A2b is an addition)
