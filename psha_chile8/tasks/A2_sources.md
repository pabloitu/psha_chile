# Task A2: collect and freeze the source catalogs

Read first: `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (Catalog), `catalog/PREFERENCES.md`, `catalog/SOURCES.md`, `REFERENCES.md`.

## Goal

Every source catalog of the new catalog is on disk as a frozen, dated file, read into one common format, and described by a profile figure. Nothing is matched, chosen or converted yet (that is A3–A5).

## Domain for all downloads

- Box: latitude −15.5 to −58.0, longitude −80.0 to −60.0 (margin around the final domain south of 17°S; the backarc and the Jujuy area must be inside).
- Time: from the start of each source to today.
- Magnitude: native magnitude ≥ 3.5 where the service allows a filter, so the later Mw conversion is not truncated at the bottom.

## Sources

| name | what to get | how | notes |
|---|---|---|---|
| `comcat` | all events in the box | FDSN event service (`obspy` `Client("USGS")`), split into yearly (or shorter) requests below the 20 000-event limit | preferred magnitude only; native magnitudes per agency come from `isc` |
| `comcat_mt` | moment tensors and nodal planes, events M ≥ 5 from 1976 | per-event query with `libcomcat`, as in `cat_no_mech_handler/parsers/anss.py` | throttle requests; resume where it stopped |
| `isc` | ISC Bulletin, all origins and **all magnitudes with their agency** | FDSN (`Client("ISC")`, `includeallorigins`, `includeallmagnitudes`), monthly requests, QuakeML | the main source of native magnitudes (ISC mb, NEIC mb, CSN ML, Ms, Md); also carries CSN (agency GUC) solutions |
| `iscgem` | ISC-GEM v12 | CSV from the ISC-GEM page (manual download if no direct link works) | record the version; compare with `data/isc_gem.csv` |
| `iscehb` | ISC-EHB 1964–2021 | per-year files from the ISC-EHB site | depths with quality class L1–L3 |
| `gcmt` | GCMT ndk | existing `data/catalogs/gcmt_jan76_dec20.txt`, `gcmt_jan21_aug25.txt`, plus the monthly ndk files after Aug 2025 from globalcmt.org | parser logic in `cat_no_mech_handler/parsers/gcmt.py` |
| `centennial` | Centennial catalogue (Engdahl and Villaseñor) | USGS no longer hosts it. Try the archived USGS page (`earthquake.usgs.gov/research/data/centennial.php` in web archives) for `centennial.cat` and its README | if not retrievable, stop and report; do not substitute another catalogue |
| `potin` | relocated CSN catalogue 1982 – 2020-07-16 | copy `data/catalogs/CHILE_SEISMICITY_RELOCATED.csv` | `magnitude_type` codes (e.g. `l`, `xx`) to be documented |
| `csn` | CSN catalogue after 2020-07-16 | **no known bulk download.** (1) take the GUC solutions from the `isc` download; (2) check whether sismologia.cl / csn.uchile.cl offer a catalogue file or service; report what exists | do not scrape web pages without Pablo's approval |
| `cabello` | Cabello et al. (2025) integrated catalogue | copy `data/catalogs/Integrated_Seismic_Catalog_complete.csv` | used before 1904 only, and as a reference |
| `rm2018` | Ruiz and Madariaga (2018) events | copy `data/catalogs/ruiz_madariaga_2018.csv` | check against the paper later (A6) |

## Deliverables

All under `psha_chile8/catalog/`. Keep it lean: three scripts, no package of small modules.

1. `fetch.py`: downloads `comcat`, `comcat_mt`, `isc`, `iscehb`, new `gcmt` months; copies the local files. Settings (box, dates, floor, which sources) at the top. Each run writes raw files to `sources/raw/<name>/` and can resume.
2. `read.py`: one reader per source into three tables, written as `sources/<name>_<YYYY-MM-DD>_{events,mags,mechs}.csv`:
   - **events**: `src, src_id, time` (UTC ISO), `lon, lat, depth, depth_fixed` (flag from the source if it says so, else empty), `lon_err, lat_err, depth_err, depth_quality` (e.g. EHB class), `agency`
   - **mags** (long format, one row per magnitude): `src, src_id, agency, mag_type, mag, mag_err, n_sta`
   - **mechs**: `src, src_id, agency, m0, mw, strike1, dip1, rake1, strike2, dip2, rake2, mrr, mtt, mpp, mrt, mrp, mtp`
   Keep every magnitude a source reports, with its agency and native type. Do not convert or pick.
3. `profile.py`: one figure per source in `figs/profile/<name>.png`: events per year by magnitude band; magnitude types through time; depth histogram (log counts, 1 km bins, so default depths show as spikes); map of the box. Shared palette and Ubuntu font.
4. `sources/MANIFEST.csv`: `file, source, version_or_query, downloaded, rows, sha256`.
5. A row per frozen source in `DATA.md` (Source catalogs table).
6. `SOURCES.md`: one card per source: coverage (time, magnitude, area), magnitude types present, depth handling, known issues found while reading.
7. Tests in `tests/test_read.py`: each reader on a small sample file (a few rows per source, committed under `tests/data/`).

## How to run

- Claude Code writes the scripts and runs them only on a tiny request (one month of `comcat` and `isc`, a handful of `comcat_mt` events) and on the test samples.
- Pablo runs the full `fetch.py`, then `read.py` and `profile.py`. Put the exact commands, with a time estimate, in the WORKLOG entry.

## Done when

- Tests pass; Pablo has run the full fetch and read; every source has frozen files, a MANIFEST row, a DATA.md row, a SOURCES.md card and a profile figure.
- WORKLOG lists what could not be obtained (expected: `centennial` and `csn` may need Pablo or S. Ruiz) and anything surprising in the profiles (default-depth spikes, magnitude-type changes, gaps in time).

## Not in this task

Matching events across sources (A3), choosing properties (A4), magnitude conversion (A5), classification (A7). No edits outside `psha_chile8/` except reading `data/catalogs/` and the old parsers.
