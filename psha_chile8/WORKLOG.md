# WORKLOG

One entry per session: date, done, decisions, commands for Pablo, open questions.

## 2026-11-09
- Done: psha_chile8 set up as the working folder for the new round; PLAN, DECISIONS, LEARNINGS and CLAUDE.md written from the project notes of psha_chile4–7 and cat_handler_2.
- Decisions of 8 Nov (after the meeting with S. Ruiz):
  - The catalog is rebuilt from scratch. No Cabello et al. (2025) for events from 1900 on; Sergio's source order is used (to fill in). Cabello's Mw conversion was wrong and is redone. Events are matched across catalogs once; magnitude, location and mechanism are chosen per event by separate priority rules.
  - The in-slab model becomes a double seismic zone: upper and lower plane, each its own source at small M, merging into one source at large M; the construction is tested in a new tornado round.
  - All statistical fits are redone on the new catalog (Mc incl. spatial, b-value methods, with and without declustering).
  - The new tornado round decides the final logic tree; then the recipe (methods, rules, tree) is frozen.
  - Pseudo-prospective test: catalog cropped at the end of 2009, training models with the frozen recipe (faults and geodetic unchanged), branches converted with hazard2csep, tested on 2010–2022 per source family, plus a test of the spread between branches; reported, not fed back into the tree.
  - The Chile fault model is part of Chile PSHA, not a separate workstream.
  - The same model goes to Renta Nacional later (separate project).
- Next: A1, Sergio's rules into DECISIONS (source order to fill in).

## 2026-11-10 (A2, source catalogs)
- Done: `catalog/fetch.py`, `catalog/read.py`, `catalog/profile.py`, shared `palette.py` (style and magnitude-band colours, from cat_handler_2/palette.py), `catalog/tests/test_read.py` with real samples under `catalog/tests/data/` (ISC-GEM sample constructed, see below), `catalog/SOURCES.md` rewritten as one card per source. Tests: 24 passed (`pytest` from psha_chile8).
- Checked on a tiny run into the scratchpad (not in `sources/`): ComCat and ISC Mar 2010, ComCat moment tensors for 5 events, ISC-EHB 2010, GCMT monthly files, Centennial, local copies; read and profile on all of them. Nothing is in `catalog/sources/` yet: the frozen files come from Pablo's run.
- How each source is obtained, and where it departs from the brief:
  - comcat: USGS FDSN CSV through urllib (same service as obspy `Client("USGS")`; the CSV carries errors, magNst, location and magnitude source). ≈ 44 000 events ≥ 3.5; no year needs splitting.
  - comcat_mt: ComCat GeoJSON event pages (what libcomcat wraps; libcomcat is not in `psha_renta`). Every moment-tensor and focal-mechanism product kept, not only the preferred. 4 274 events M ≥ 5 from 1976.
  - isc: FDSN QuakeML, all origins and magnitudes, parsed with ElementTree. `minmagnitude=3.5` only from 1964; before 1964 no filter (most ISS events have no magnitude and would be lost).
  - iscehb: ISC-EHB catalogue search (CSV for DEPFIX and L1–L3, QuakeML for errors) instead of the per-year `.hdf` files, which have no L1–L3 class.
  - centennial: obtained from the Wayback snapshot of 2013-09-09 (`centennial_Y2K.CAT` + README). Not a substitute: the USGS file itself.
  - iscgem: no direct download (form with e-mail and CAPTCHA). Manual, see commands.
  - csn: only the GUC rows of the ISC download. sismologia.cl has per-event and daily HTML pages and no event service (FDSN path 403); evtdb.csn.uchile.cl has a POST filter form returning HTML and an RSS feed. No bulk file; nothing scraped.
  - gcmt: monthly ndk available to Jun 2026; Jul–Oct 2026 not yet published (listed as failed in `fetch.json`; a later rerun picks them up).
- Extra columns beyond the brief: events `origin_id, prime, etype` (one row per origin for ISC and GCMT), mags `note` (Centennial preferred flag, ISC-GEM Mw quality and source, Ruiz and Madariaga Mw text such as `>7.7`), mechs `code, mw_type`.
- Commands for Pablo (env `psha_renta`; settings at the top of each script). Expected time: fetch 4–5 h (ISC ≈ 750 requests, 1.5–2 h; comcat_mt ≈ 4 300 pages at ~1/s, ≈ 2 h; the rest < 15 min), safe to stop and rerun (resumes); read 15–30 min (ISC QuakeML); profile ≈ 5 min.
  1. ISC-GEM by hand: https://www.isc.ac.uk/iscgem/download.php → main and supplementary CSV into `psha_chile8/catalog/sources/raw/iscgem/` (names starting `isc-gem`).
  2. `cd /data/PyCharmProjects/psha_chile/psha_chile8/catalog && /data/miniforge3/envs/psha_renta/bin/python fetch.py`
  3. `cd /data/PyCharmProjects/psha_chile/psha_chile8/catalog && /data/miniforge3/envs/psha_renta/bin/python read.py`
  4. `cd /data/PyCharmProjects/psha_chile/psha_chile8/catalog && /data/miniforge3/envs/psha_renta/bin/python profile.py`
  5. `cd /data/PyCharmProjects/psha_chile/psha_chile8 && /data/miniforge3/envs/psha_renta/bin/python -m pytest -q`
  Then a Claude session: check `fetch.json` failures, ISC-GEM reader against the real header (replace the constructed sample with real rows), DATA.md rows, the *after the full fetch* lines in SOURCES.md, and the profile findings below.
- DATA.md rows to add after the run (Source catalogs table; one per source, date = `downloaded` in `fetch.json`): `comcat_<date>_*.csv | ComCat FDSN, box, M ≥ 3.5, 1500–<date>`; `comcat_mt_<date>_mechs.csv | ComCat GeoJSON, M ≥ 5 from 1976, all MT/FM products`; `isc_<date>_*.csv | ISC Bulletin FDSN, all origins and magnitudes, M ≥ 3.5 from 1964`; `csn_<date>_*.csv | GUC rows of isc_<date>`; `iscehb_<date>_*.csv | ISC-EHB 1964–2021, catalogue search`; `iscgem_<date>_*.csv | ISC-GEM v12 (to confirm), manual`; `gcmt_<date>_*.csv | GCMT ndk 1976–Aug 2025 local + monthly to Jun 2026`; `centennial_<date>_*.csv | Centennial, Wayback 2013-09-09`; `potin_`, `cabello_`, `rm2018_<date>_*.csv | copies of data/catalogs/…`.
- Found in the local files and the tiny run (more after the full profiles):
  - Potin magnitude types change through time: `c` (coda) 1982–2009, `l` from 2000, `W` 1995–2016, `ww` from 2014; 8 694 events without magnitude, mostly 1982–1985; 1 830 depths at or above sea level.
  - GCMT fixed depths at 15 and 12 km (and 33, 10, 25), BDY mostly 15 km.
  - Centennial: early events at depth 0.0 with no solution type (unknown, not 0 km); some EHB updates run past the stated 2002 end, to 2007.
  - Cabello: rows labelled GCMT before 1976 (1971).
  - ComCat WCMT product for Maule has a scalar moment that does not match its Mw.
- Proposed for DECISIONS (Catalog): "Centennial catalogue taken from the Wayback snapshot of 2013-09-09 of the USGS page (USGS no longer hosts it) (10 Nov)." "ISC-EHB depth quality L1–L3 from the ISC-EHB catalogue search (10 Nov)."
- Open questions:
  - CSN after 2020-07-16: ask S. Ruiz / CSN for a catalogue file, or approve querying evtdb.csn.uchile.cl or the sismologia.cl daily pages.
  - Potin `W` vs `ww`, `B`, `xx` codes (S. Ruiz or the paper).
  - Raw downloads (ISC ≈ a few hundred MB gzipped) and the frozen ISC tables (≈ 100 MB) in git or not; suggest ignoring `catalog/sources/raw/` and archiving it with the data DOI (K28).
- Suggested commit (after the run, or now for the code):
  `git add psha_chile8/palette.py psha_chile8/catalog/fetch.py psha_chile8/catalog/read.py psha_chile8/catalog/profile.py psha_chile8/catalog/SOURCES.md psha_chile8/catalog/tests psha_chile8/WORKLOG.md psha_chile8/PLAN.md`
  message: `psha_chile8 A2: fetch, read and profile scripts for the source catalogs; source cards; reader tests`

## 2026-11-10 (R1, literature review of the catalog references)
- Done:
  - `catalog/LITERATURE.md`: one card for each of the 44 papers in `refs/catalogs/`, then the six synthesis sections (source order per PREFERENCES period with evidence for Q1 and Q2; magnitude homogenization with a relation table per native scale and three candidate approaches for A5; depths per source; DSZ table and where along Chile it is documented; large-event disagreements; open points).
  - Engdahl and Villaseñor (2002) Table 1: all 106 Chilean rows (15–60°S, 64–82°W) checked field by field against the page images (250 dpi, rotated). All match the OCR and none is missing.
  - `REFERENCES.md`: file names as in `refs/catalogs/`, DOIs and details from page 1, pdf column ticked, Engdahl and Villaseñor 2002 and Giesecke 2004 added, corrections listed at the end.
  - No code, no tests.
- Hard to read:
  - dziewonski_etal_1981: garbled OCR; its two South American events (Table 4) are not identifiable. Marked "(check PDF)".
  - comte_etal_1999 and hanks_kanamori_1979: numbers checked on the page images.
  - Table 1 of engdahl_villasenor_2002: unreadable at the default rendering; readable after rotating at 250 dpi.
  - ekstrom_etal_2012 Table 1 lost its minus signs.
  - digiacomo_etal_2015 lost minus signs in its proxy equations; the equations were checked on the image.
  - The Slab2 thickness and uncertainty grids are only in the Slab2 supplement, which is not in refs.
- Surprising for our decisions (detail and pages in LITERATURE.md section 6):
  - The DSZ is not only intermediate depth. In 19–24°S the planes are separate above ~80–90 km, with the lower plane from ~45–50 km, then merge into one cluster at 80–120 km. In central Chile it runs from 50 km down to 100–120 km. Nothing documents it south of ~33–35°S, and the lower plane is patchy along strike. Rietbrock and Waldhauser (2004) give 9 km plane separation; everyone else gives 15–27 km.
  - Q1: Centennial magnitudes are not recomputed. Pre-1976 Chilean "Mw" are Pacheco and Sykes (1992) values, and intermediate-depth events carry Abe mB. The Centennial is not relocated for 1904–1917 and 1943–1955, while ISC-GEM relocated every event. ISC-GEM has no pre-1964 deep events without a literature Mw.
  - Cabello's paper prints 1.04·mb − 0.02 and 1.03·mb + 0, not 1.03·mb + 0.28. Every Mc, Md and m, and every value outside an equation's range, goes in as Mw.
  - ISC mb saturation from Lolli et al. (2023): about −0.19 at Mw 5.5 and −0.43 at Mw 6.5, not −0.4 throughout.
  - No paper calibrates CSN, GUC or SAN magnitudes except Poulos 2019 and Leyton 2009, and neither names the agency. Potin documents no magnitude homogenization (only ML ≈ Mc − 0.25).
  - GCMT Mw < 5.4 may be overestimated, and teleseismic proxies run high in subduction zones (Lolli 2014, 2023).
  - "ISC-GEM default depths 15–35 km" is not stated in any ISC-GEM paper. Additional defaults to flag: GCMT 10 km in 1981–1985 and its 12 km floor; ISC-EHB 10 / 15 km.
  - Ruiz and Madariaga (2018) Table 1 disagrees with its own text on 1918 (4 vs 18 Dec), 1983 (4 Nov, Mw 7.4 vs 4 Oct, Mw 7.7), 1995 (30 vs 31 Jul) and the 1966 domain. Arauco is dated 14 Oct 1975 against 10 May 1975 in the Centennial. "5 October 1959" Copiapó is probably 1859 (Lomnitz), and the Centennial has no Chilean M ≥ 7 in October 1959; this bears on cat_handler_2 DECISIONS 30.
  - 1960-06-06 Aysén is in Cabello (Mw 7.7, crustal) and in the Centennial (Mw 7.2 P&S). It is the candidate for the "Kanamori intra-arc > 7.5" open point.
  - 1647 Santiago: Lomnitz suggests a crustal source, while Ruiz and Madariaga call it intraslab citing Lomnitz. The Pica event is 1768 or 1786 within Ruiz and Madariaga; Lomnitz lists neither.
  - Riquelme 2018 Illapel: the printed M0 gives Mw 8.44, not the stated 8.36.
  - Storchak 2013 prints the completeness change reversed (5.6 before 1964, 6.4 after).
- Proposed for DECISIONS / LEARNINGS (Pablo decides):
  - LEARNINGS, Catalog pitfalls: "Cabello takes Mc, Md, m and every native magnitude outside its equation ranges as Mw (paper p. 3, p. 10); the paper's mb relations are 1.04·mb − 0.02 and 1.03·mb + 0."
  - LEARNINGS, Catalog pitfalls: "ISC mb saturation grows with size: ≈ −0.19 at Mw 5.5, −0.43 at Mw 6.5 (Lolli et al. 2023)."
  - LEARNINGS, Default depths: add "GCMT 10 km in 1981–1985 and a 12 km floor; ISC-EHB 10 km (ocean) / 15 km (trench, volcano); ISC 10 / 35 km and 1° cell depths after the rebuild."
  - DECISIONS, Classification (for discussion with S. Ruiz): the DSZ question is better posed as 45–120 km than as intermediate depth only.
- Commands for Pablo: none to run.
- Open questions:
  - Q1 and Q2 in PREFERENCES now have the evidence in LITERATURE.md section 1; still for S. Ruiz.
  - The RM18 Table 1 dates (1918, 1975, 1983, 1995) and the "1959" Copiapó: which reading does Sergio take?
  - The Slab2 supplement (thickness and uncertainty grids) and the Sippl et al. 2019 DSZ paper are not in refs; add them if A7 needs them.
- Suggested commit:
  `git add psha_chile8/catalog/LITERATURE.md psha_chile8/REFERENCES.md psha_chile8/WORKLOG.md`
  message: `psha_chile8 R1: literature cards and synthesis for the catalog references; REFERENCES updated from the PDFs`
- Later the same day:
  - ISC-GEM v13.0 (released 2026-10-21) downloaded by Pablo into `catalog/sources/raw/iscgem/`. Reader checked on the real header: 4 129 events in the box (3 695 main, 434 supplementary). Test sample replaced by three real rows. Rerun `fetch.py` once after the main download so it writes `iscgem/fetch.json`.
  - GCMT Jul–Oct 2026 return 404: not yet published (GCMT monthly lag). GCMT runs to Jun 2026; recent mechanisms come from comcat_mt.
  - pituPLOTS installed editable into `psha_renta` (`pip install -e /data/PyCharmProjects/pituPLOTS`, commit b9be58a; added pyyaml 6.0.3 only). Sections are drawn in A7 (not in the A2 profiles), perpendicular to `data/shapefiles/sam_nazca_trench.shp` with `profiles_from_line`, Slab2 via `add_slab`, map on `data/basemaps/basemap_chile_gray/basemap_gray.tif`. Record the pituPLOTS commit with every figure run.
  - Noted: pituPLOTS imports pyshp without declaring it in `pyproject.toml`; psha_renta has numpy 2.2.6, while CLAUDE.md says numpy < 2.
  - Proposed for DECISIONS (Figures): "Figures drawn with pituPLOTS (installed editable in psha_renta), sections perpendicular to the Nazca trench, gray basemap (10 Nov)."
  - fetch.py: pause per server (USGS 0.3 s, ISC 1.0 s) and per-process temp names (`*.part<pid>`), so the USGS and ISC parts can run in two terminals at once. Restarted run: terminal 1 `fetch.comcat(); fetch.comcat_mt()`, terminal 2 `fetch.iscehb(); fetch.isc()`, then one plain `fetch.py` to log ISC-GEM and retry failures.
  - CSN after Potin (approved by Pablo): new source `csn` from the sismologia.cl daily catalogue pages, 2020-01-01 to yesterday (overlap with Potin for A3 / A5), one request per day, ≈ 1 h. The day pages hold the full published catalogue (counts match Potin on test days); no magnitude floor, since the request count does not depend on it. Felt events are rows `<tr class="percibido">`; a first version of the reader missed them, caught by checking row counts per day. The GUC rows of ISC are now source `csn_isc`. Run in a third terminal: `/data/miniforge3/envs/psha_renta/bin/python -c "import fetch; fetch.csn()"` from `catalog/`.
  - read.py now runs check() on each source after writing it and prints `CHECK:` lines for problems: events without exactly one preferred origin, repeated origins, preferred origins outside the box or without coordinates, years outside 1500–today, depths outside −10–800 km, magnitudes or mechanisms without their event, magnitudes outside −2–10, mechanism Mw outside 3–10, non-positive moments. Only expected flag: rm2018 has no coordinates. It also prints events / with magnitude / with mechanism per source (ComCat should give 43 985 events). Test added (27 pass).
  - Full read, first try: stopped at ISC. Four ISC files (1997-02, 2008-11, 2020-06, 2024-01) end with a stray `?` line after `</q:quakeml>`; the documents are complete, so quakeml() now cuts after the closing tag. My earlier "all ISC files valid" was checked too loosely. ComCat read clean (43 985 events, no CHECK flags). comcat_mt: 2 501 of the 4 274 M ≥ 5 events have a moment-tensor or focal-mechanism product (5 288 products); the 1 773 without are mostly M 5 events before 2000 and Maule aftershocks in 2010.
  - Full read, second try (all sources written). CHECK flags looked into:
    - ISC: 8 events came back from the ISC box search with no origin in the box (Japan, Turkey, Finland, Fiji, …); 189 more have the ISC preferred origin just outside the box but another origin inside (kept, by design). The ISC, csn_isc, Potin and Cabello readers did not call inbox(); now they do. Drops ISC 8, csn_isc 6 (GUC epicentre outside), Cabello 2 374 (its area reaches 11.6° S and south of 58° S), Potin none.
    - GCMT 12: centroid outside, PDE hypocentre inside (kept).
    - The box check now flags events with no origin in the box, not preferred origins outside it.
    - rm2018: 27 of 69 events have no coordinates (historical, by design; kept, no box filter).
    - CSN: 56 051 events on the pages (2 header rows per page account for the rest of the 61 061 rows), 502 outside the box (mostly south of 58° S and Argentina east of 60° W), 55 549 kept.
  - Commands for Pablo: rerun `read.py` (rewrites the tables of the same date and their MANIFEST rows), then `profile.py`.
  - rm2018 without longitude (27 of 69; the paper gives latitudes or rupture bars only): checked against the frozen tables by date (±1 day for local vs UTC) and latitude (within 2°). 24 have a counterpart with a full location (Cabello for the historical ones, e.g. 1543, 1575, 1604, 1615, 1647, 1730, 1751, 1822, 1835, 1837, 1868, 1877, 1880; ISC-GEM / ComCat from 1909). The other 3 are the ones already settled in cat_handler_2 DECISIONS 30: Taltal 1887 (no magnitude), Copiapo 1959-10-05 (no single event in any catalog), Mejillones 1994-10-12 (probably 1994-12-10 Mw 6.0, day and month swapped). The A2 table stays as the paper gives it (no invented longitudes).
  - Proposed for DECISIONS (Catalog): "Ruiz and Madariaga (2018) is not an event source but an authority for the class and magnitude of the events it names: each of its events is matched to a located event (date ±1 day, latitude within 2°, name checked by hand) and lends it class and Mw; its own coordinates are not used. Taltal 1887, Copiapo 1959 and Mejillones 1994-10-12 are not added (as cat_handler_2 DECISIONS 30)."
  - Pablo approved the rm2018 line above (10 Nov): add it to DECISIONS (Catalog). For A3: rm2018 events are matched to located events (date ±1 day, latitude within 2°, name checked by hand; pick by time and magnitude where a day has many events, e.g. Valparaiso 2017), and lend class and Mw; Taltal 1887, Copiapo 1959-10-05 and Mejillones 1994-10-12 left out.
  - Full read and profiles done (third run): no CHECK flags except rm2018 (27 without coordinates, expected). Profiles reviewed; per-source findings now in the last line of each SOURCES.md card. profile.py: Mw from M0 for mechanism products without a derived Mw (figure only), no empty depth panel, cartopy warning removed.
  - Surprises for later steps:
    - CSN web: `Ml` replaced by `Mlv` in 2026 (9 163 of the 2026 magnitudes). A5 treats them as two types until shown equal.
    - Potin: gap February–August 2000 (one event in January). A3 / B: completeness and rates there come from csn_isc or ISC.
    - ISC-EHB has no Mw for 1985–1998 (GCMT MW in it stops in 1984, HRVD starts in 1999); take Mw from gcmt for those years.
    - ComCat preferred depths at 10 / 33 / 35 km are 17 % of events with no fixed flag: A4 has to treat them as fixed.
    - comcat_mt before 1996: focal mechanisms only, no moment.
  - DATA.md: 12 Source catalog rows added. PLAN: A2 ticked, ← on A3. FIGURES.md: no row (profiles are diagnostics, not paper candidates; a combined source-coverage figure could be one later).
  - `psha_chile8/.gitignore` added: `__pycache__/`, `catalog/sources/raw/` (155 MB; keep on disk and archive with the data DOI, K28).
  - psha_chile8 has never been committed (whole folder untracked). Frozen tables are 125 MB (largest `isc_..._events.csv` 32 MB); `MANIFEST.csv` holds their sha256.
  - Pablo: frozen tables go into git (125 MB for all 26 tables plus MANIFEST.csv together, largest 32 MB).
  - Suggested commit (A2 only; the R1 files and the rest of the scaffold are Pablo's call):
    `git add psha_chile8/.gitignore psha_chile8/palette.py psha_chile8/catalog/fetch.py psha_chile8/catalog/read.py psha_chile8/catalog/profile.py psha_chile8/catalog/SOURCES.md psha_chile8/catalog/tests psha_chile8/catalog/figs/profile psha_chile8/catalog/sources psha_chile8/DATA.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`
    `git commit -m "psha_chile8 A2: source catalogs fetched, read and frozen (2026-11-10), with profiles"`

## 2026-11-10 (X1, exploratory analysis of A3–A5, previews of B9 and A7)
- Task `tasks/X1_explore_catalog.md`, run unattended. Full runs over all sources and fits (allowed by the brief). Nothing under `catalog/` changed; DECISIONS, LEARNINGS, PLAN untouched (X1 is not a plan step); no DATA.md row (the X1 catalogs are exploration variants, not catalog runs).
- What ran:
  - Tier 1: origin table (387 471), ISC-ID and foreign-origin backbone, window calibration on 276 202 known pairs, 204 matching variants, hot spots, RM18.
  - Tier 2: default depths, location agreement, location variants L-a / L-b / L-c / L-d with a depth proxy class, sections.
  - Tier 3: inventory, pairs, triple collocation, 3 500 fits per matching, published relations, A2 checks, Mw variants M0–M8.
  - Tier 4: Mc / Weichert / b-positive / TM weights / GK on 50 combinations, tornado.
  - Tier 5: two-plane test by 1° band.
  - Deeper pass: censored GCMT pairs (M9), Potin flat-slab depths, two-plane test without the interface band, Valdivia foreshock.
- Outputs: `explore/X1/REPORT.md` (summary of 15 findings, per tier, assumptions, failures), `explore/X1/figures_index.md` (28 figures), `explore/X1/tables/` (73 tables), `explore/X1/figs/`, `explore/X1/cache/` (595 MB, git-ignored by `explore/.gitignore`).
- Main points for A3–A5 (detail and options in the report):
  - The ISC-ID / foreign-origin backbone links everything except Potin. The window choice moves M ≥ 4.5 counts by ±2 %; avoid 25 km.
  - X1 baseline: 5 s / 50 km, magnitude scaling, Hungarian, anchor-first.
  - Potin magnitudes are the CSN bulletin values (`l` = GUC ML, `c` = GUC MD / md, `W` = GUC MW, `ww` = CSN Mww). Coda values of the 1980s are unusable.
  - Potin intermediate depths at 29–34° S are 25–60 km too deep.
  - The low end of every conversion (native < ~5.5) is censored by GCMT completeness. It controls Mc, b at floors < 5.3 and N(≥ 4.5) (×0.5–1.45 across variants).
  - Weichert at floor 5.0 under-predicts M ≥ 7 about 2×.
  - Double-zone evidence only at 20–24° S, 80–120 km, ~10 km apart.
- Decisions made: none (exploration). Every choice made without asking is under "Assumptions" in the report.
- Settings: at Pablo's request, `.claude/settings.local.json` in the repo root and in `psha_chile8/` now allow `python`, `python3`, `pytest` and the psha_renta interpreter and pytest without a prompt.
- Environment issue: `geopandas.read_file` fails in psha_renta (pyogrio: incomplete GDAL data directory); X1 reads shapefiles with cartopy. No Slab2 uncertainty grid is on disk.
- Commands to rerun, from `psha_chile8/explore/X1/` with `/data/miniforge3/envs/psha_renta/bin/python` (each resumes from `cache/`; delete a cache file to recompute it):
  - `python x1_match.py` (tier 1; deletes nothing, reuses `cache/grid.jsonl`; remove it to rerun the grid)
  - `python x1_loc.py` (tier 2, needs tier 1)
  - `python x1_mag.py` (tier 3, needs tiers 1–2; remove `cache/fits.json` and `cache/fits_m6.json` to refit, ≈ 10 min on 14 processes)
  - `python x1_stats.py` (tier 4, needs tier 3)
  - `python x1_dsz.py` (tier 5, needs tier 2)
  - `python x1_deep.py` (deeper pass, needs tiers 2–3)
  - `python x1_report.py` (figure index)
  - tests: `pytest explore/X1/tests` from `psha_chile8/` (8 pass)
- Proposed for LEARNINGS (Pitfalls, Catalog), for Pablo to add if he agrees:
  - "Potin et al. (2024) magnitudes are the CSN bulletin values (l = GUC ML, c = GUC MD/md, W = GUC MW, ww = CSN Mww, 96–100 % identical); its 1982–1990 coda values are 0.2–1.0 for M 4 events (X1)."
  - "Potin intermediate-depth hypocentres under the flat slab (29–34° S, > 90 km) are 25–60 km deeper than ISC-EHB L1 and Slab2 (X1)."
  - "Conversion fits against GCMT are censored below native ~5.5 (GCMT has few Mw < 4.7). Exponential / quadratic forms then flatten, heap the converted catalog at Mw 4.7–4.9 and make maximum-curvature Mc and b(floor < 5.3) artefacts (X1)."
  - "ISC-GEM depths are ISC-EHB depths where both exist; depth triple collocation with EHB / ISC / ISC-GEM is invalid (X1)."
  - "ISC-GEM gives the 1960-05-22 18:56 Valdivia foreshock Mw 8.72 (P&S 7.9, RM18 Ms 7.8): check in A6 (X1)."
- Proposed for DECISIONS (Catalog), if Pablo agrees: "Mejillones 1994 is the event of 1994-12-10 (Mw 6.0): RM18's 12 Oct 1994 has day and month swapped (X1 confirms)."
- Open questions for Pablo:
  - The reference below Mw 5.4: GCMT only (censored), or USGS Mww shifted to GCMT (+0.04 to +0.10)?
  - Linear vs curvilinear forms at 4.5–5.
  - Potin depths at 29–34° S.
  - Whether to keep Potin magnitudes at all, given they duplicate the CSN bulletin.
- Suggested commit (scripts, report, index, small tables, figures; not the cache):
  `git add psha_chile8/explore/.gitignore psha_chile8/explore/X1/*.py psha_chile8/explore/X1/tests psha_chile8/explore/X1/REPORT.md psha_chile8/explore/X1/figures_index.md psha_chile8/explore/X1/tables psha_chile8/explore/X1/figs psha_chile8/WORKLOG.md`
  `git commit -m "X1: exploratory analysis of A3-A5 with B9 and A7 previews (report, tables, figures)"`

## 2026-11-11: X2, magnitude homogenization from Mw 4.5 to the large events (Claude Code)

- Asked by Pablo after X1: explore fits and assumptions until the homogenized Mw is consistent and uniform from 4.5 to M 7–8, without overfitting, and better than Cabello.
- Done: `explore/X2/` (`x2_prep.py`, `x2_fit.py`, `x2_eval.py`, `REPORT.md`, `figures_index.md`, 8 tables, 5 figures, 4 tests). Uses the X1 cache (baseline events); nothing under `catalog/` changed.
- Main result: the X1 under-prediction of M ≥ 7 came from forward conversion fits on pairs selected by the GCMT floor. That pushed small events up into Mw 4.7–5.5 and gave b ≈ 1.5 at floor 5.0.
- The fix: regress the native magnitude on Mw, then invert.
- Recommended variant, INV-W linear mean: one straight line per scale; reference GCMT plus the W-phase/regional Mw family (NEIC Mww, CSN Mww, GUC Mwr, CSN web Mw, NEIC Mwr + 0.10, GFZ Mw + 0.03); inverse-variance mean of proxies.
  - A GR fitted on Mw 5.0–6.5 predicts 40.5 of 41 observed M ≥ 7 since 1976 (interface 22 / 20, in slab 14 / 12).
  - b flat within 0.13 over floors 4.7–5.8.
  - M ≥ 5.5 rate stable within ±10 % across 1976–2026. Cabello's halves over the same span.
- Decisions made: none.
- Commands, from `psha_chile8/explore/X2/` with the psha_renta python (needs the X1 cache): `python x2_prep.py`, `python x2_fit.py` (delete `cache/fits_x2.json` to refit), `python x2_eval.py`; tests `pytest explore/X2/tests` from `psha_chile8/`.
- Proposed for DECISIONS (Catalog), if Pablo agrees: "Mw conversions by inverse regression (native on Mw, slope corrected for the Mw error, then inverted), one linear relation per scale, reference GCMT plus the W-phase/regional Mw family shifted to NEIC Mww; proxies combined by inverse-variance mean (X2). Replaces the chi-square forward fits of the 10 Nov line."
- Proposed for LEARNINGS (Pitfalls, Catalog): "Forward Mw-on-native fits (OLS or chi-square) against GCMT are biased high below native ~5.5 because GCMT is incomplete there (selection on the dependent variable); regress native on Mw instead. With it, ISC/NEIC mb ≈ Mw at 4.5–5 for Chile (X2)."
- Open questions for Pablo:
  - W family before GCMT below Mw 5.4, a change to the hierarchy?
  - Inverse-variance mean of proxies instead of the smallest σ?
  - Should pre-1976 (1964–1975, ISC/USCGS mb) be checked the same way before A5?
- Suggested commit:
  `git add psha_chile8/explore/.gitignore psha_chile8/explore/X2/*.py psha_chile8/explore/X2/tests psha_chile8/explore/X2/REPORT.md psha_chile8/explore/X2/figures_index.md psha_chile8/explore/X2/tables psha_chile8/explore/X2/figs psha_chile8/WORKLOG.md`
  `git commit -m "X2: inverse-regression Mw homogenization, checked against large events, rates and regional Mw"`

## 2026-11-11: review of X1/X2 magnitude homogenization (Claude Code)

- Asked by Pablo: check every step of CONTEXT_X1_X2.md for robustness, reproduce, and tie the key choices to the literature for the manuscript.
- Done: `explore/X2/review/` (`REVIEW.md`, `r_robust.py`, `r_robust2.py`, `r_pre76.py`, `tables/` A–H). X2 rerun from a clean copy: all six tables identical.
- Findings:
  - Inverse regression holds for mb and ML. For MS, MOS mb and BJI mB it is biased the other way below Mw ~4.8, because those scales are reported selectively; no effect on the catalogue.
  - Restricting to the jointly complete window is worse (N7 0.7–0.8).
  - The λ correction is model-dependent (±0.05 at native 4.5).
  - The period split was never tested; ISC/NEIC mb may be offset by ~0.15 before 1990 at Mw 5.0–5.4.
  - The W offsets are flat. GCMT is +0.08 at 4.5–5.0 (as Gasperini et al. 2012). CSN Mww is +0.10 below 5.0.
  - The inverse-variance mean under-states σ (0.14 vs 0.22): ISC mb and NEIC mb residuals correlate at 0.92.
  - The direct-Mw order changes N7 by ≤ 10 %. The 1964–75 rate at M ≥ 5.5 is consistent with later periods.
  - The Tinti–Mulargia correction must use the M̂ sign for inverse conversions, not the CEUS N* applied at E[M].
- Decisions made: none.
- Commands, from `psha_chile8/explore/X2/review/` with the psha_renta python (needs the X2 cache): `python r_robust.py`, `python r_robust2.py`, `python r_pre76.py`.
- Proposed for DECISIONS (Magnitudes), if Pablo agrees:
  - "Mw conversions by inverse regression (native on Mw, then inverted), one linear relation per scale; reference below Mw 5.4 the regional/W-phase family on the NEIC Mww scale, GCMT mapped onto it (Lolli et al. 2023); proxies combined by GLS mean with the inter-scale correlation."
  - "Magnitude-error rate correction uses the M̂ form, exp(−β²σ²/2), for direct and inverse-converted Mw (CEUS-SSC 2012, §3.3.1)."
- Open questions for Pablo: nominal reference scale (W family vs GCMT with a magnitude-dependent offset); period split for ISC/NEIC mb; delete CONTEXT_X1_X2.md now.
- Suggested commit:
  `git add psha_chile8/explore/X2/review psha_chile8/WORKLOG.md`
  `git commit -m "X2 review: robustness checks and literature support for the magnitude homogenization"`

## 2026-11-11: Candia and Macedo (2026) checked against X2 (Claude Code)

- Done: `explore/X2/review/CANDIA_MACEDO.md`, `r_candia_read.py` (reads the SRL supplement xlsx from Downloads into `X2/cache/`), `r_candia.py`.
- Findings:
  - Their catalogue fails the large-event test: GR on 5.0–6.5 predicts 0.29 × the observed M ≥ 7, with b 1.37.
  - Their declustered M ≥ 5 rate drifts −29 % between 1976–89 and 2011–26.
  - Their Mw is +0.21 above ours at 4.6–5.1 and +0.10 at 5.0–5.5; it agrees with ours above 5.5.
  - Causes: forward regressions, SARA/SISRA/CSN magnitudes passed through as Mw, no dithering, and 275 duplicates left in.
- Decisions made: none.
- Proposed: cite as related work and as an example of the forward-regression bias; use its Table S1 (tsunami evidence) and the declustering comparison; compare its classes with A7 later. Add to REFERENCES (D): Candia, G., Macedo, J. (2026), SRL, doi:10.1785/0220250449.
- Input to freeze if kept: the supplement xlsx as `catalog/sources/candia_macedo_2026-11-11.xlsx` (29 MB; or keep it raw and archive it with the data DOI).
- Suggested commit: `git add psha_chile8/explore/X2/review psha_chile8/WORKLOG.md` with `git commit -m "X2 review: Candia and Macedo (2026) checked with the X2 tests"`
