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

## 2026-11-11: A2b, GCCEL added as a source and benchmarked as the location reference (Claude Code)

- Done:
  - **Fetch and freeze.**
    - `fetch.py` has a `gccel` source. It downloads `Distribution_v20230722.zip` (455 MB, ISC dataset repository, doi 10.31905/MFDY4QHD) into `sources/raw/gccel/` and unzips it with the inner zips. Downloaded and unzipped once.
    - `read.py` has a `gccel` reader (MNF v1.4 E / H / M records of `all_gccel.dat`). It wrote `sources/gccel_2026-11-11_{events,mags}.csv`: 801 events and 1 375 magnitudes in the box; no mechanisms; no CHECK lines.
  - **Bookkeeping.** MANIFEST rows, DATA.md row, SOURCES.md card, `figs/profile/gccel.png`, a test sample of real lines in `tests/data/gccel/` and `test_gccel` (catalog tests: 29 pass).
  - **Benchmark.** `explore/X3/` (`x3_gccel.py`, `REPORT.md`, `figures_index.md`, 10 tables, 4 figures, 4 tests).
- **Version.** 20230722 is the only GCCEL in the ISC repository.
  - ScienceBase (USGS, doi 10.5066/P95R8K8G) is behind a bot check and could not be inspected. Its usgs.gov page still describes the 2021 release.
  - A web-search summary of an SSA 2025 abstract mentions ≈ 28 000 events in 366 clusters at the USGS, so a newer ScienceBase version may exist. **Pablo to check by hand**: https://www.sciencebase.gov/catalog/item/59fb91fde4b0531197b16ac7. If there is one, put the files in `sources/raw/gccel/`; the reader needs only `all_gccel.dat`.
- **ComCat** carries no GCCEL origins (no GCCEL catalogue or contributor; none on the Illapel 2015 event page).
- **Coverage.** 12 clusters (Iquique, Tocopilla, Vallenar, La Serena, Illapel, Valparaíso, San Pedro, Tabuco, Maule, Tomé, Tirúa, San Juan), 18.5–38.5° S, 1973–2021, 96 % from 2000. Depth 4–95 km; 14 events at 70–95 km, none deeper. GCCEL selects events shallower than about 50 km.
- **Main results** (`explore/X3/REPORT.md`):
  - 775 of 801 link to X1 baseline events. The 26 others have no origin in any source: M < 3.5 San Juan events, and 3 Tabuco events from March–April 2010.
  - DECISIONS order (GCCEL left out): mean epicentre distance 8.9 km and mean |Δz| 8.1 km. By depth: 10.7 km above 30 km, 6.4 km at 30–70 km, 3.7 km at 70–120 km.
  - Potin is the best epicentre in its network core: 18–36° S, 3–6 km, depth spread 2–4 km. It is poor south of 36° S and in the backarc.
  - Above 30 km, Potin depths are worse than EHB L1, ISC and ComCat on the same events (mean |Δz| 13.9 vs 4.9 km against EHB L1).
  - X1 finding 6 cannot be tested with GCCEL (no events below 95 km): the EHB-before-Potin-at-depth decision rests on X1. At 70–95 km, EHB is closer in 5 of 8 pairs, which is not significant.
  - Valparaíso: every source is 8–14 km shallower than GCCEL. Tirúa: the global catalogues are ≈ 20 km east of GCCEL.
- Decisions made: none.
- Commands (from `psha_chile8/catalog/` with the psha_renta python), only if a newer GCCEL is fetched:
  - `python -c "import fetch; fetch.gccel()"`, or set `RUN = ["gccel"]` in `fetch.py`. Note: `gccel` was added at the head of `fetch.RUN`; files on disk are skipped.
  - `python read.py` (RUN now includes `gccel`; it rewrites every source from raw, ≈ the A2 time), or only `read.gccel` and `read.write`.
  - `python profile.py`.
  - Benchmark: from `psha_chile8/explore/X3/`, `python x3_gccel.py` (≈ 10 s, needs the X1 cache; delete `cache/gccel_linked.csv` to relink).
  - Tests: `pytest catalog/tests explore/X3/tests` from `psha_chile8/` (33 pass).
- Proposed for DECISIONS (Catalog), if Pablo agrees:
  - "GCCEL version 20230722 (ISC dataset repository), frozen 2026-11-11; ComCat carries no GCCEL origins (A2b)."
  - Depth exception, one of these:
    - "Below 70 km EHB L1/L2 before Potin, on X1 evidence (GCCEL has no events below 95 km)", or
    - keep "no exceptions", with the Potin flat-slab cloud flagged in A7.
  - Possibly: "Depth above 30 km: EHB L1 before Potin (X3: Potin 13.9 vs EHB L1 4.9 km on shared events)". This conflicts with the 11 Nov "no regional or depth exceptions" line, so it is Pablo's call.
- Proposed for LEARNINGS (Pitfalls, Catalog):
  - "GCCEL selects events shallower than about 50 km (none below 95 km in Chile); it cannot test intermediate-depth locations (X3)."
  - "Potin et al. (2024) locations are excellent at 18–36° S (epicentre 3–6 km, depth σ 2–4 km against GCCEL) but poor south of 36° S, in the backarc (San Juan) and in depth above 30 km (X3)."
  - "Teleseismic catalogues (ISC, ComCat, EHB) are ≈ 20 km east of GCCEL at Tirúa, 38–39° S (X3)."
- Proposed for PREFERENCES (location line): note that the GCCEL step only matters where Potin and CSN are missing. In the GCCEL footprint that is San Juan, before 1982, and the southern clusters with no Potin event.
- Open questions for Pablo:
  - The Valparaíso depth offset (all sources 8–14 km shallower): ask E. Bergman, or treat the cluster's depths as uncertain?
  - Should Potin be first outside its network (south of 36–37° S, backarc)? See X3 option (c).
  - Newer GCCEL on ScienceBase (above).
- Suggested commit:
  `git add psha_chile8/catalog/fetch.py psha_chile8/catalog/read.py psha_chile8/catalog/profile.py psha_chile8/catalog/tests/test_read.py psha_chile8/catalog/tests/data/gccel psha_chile8/catalog/sources/gccel_2026-11-11_events.csv psha_chile8/catalog/sources/gccel_2026-11-11_mags.csv psha_chile8/catalog/sources/MANIFEST.csv psha_chile8/catalog/figs/profile/gccel.png psha_chile8/catalog/SOURCES.md psha_chile8/DATA.md psha_chile8/explore/.gitignore psha_chile8/explore/X3/x3_gccel.py psha_chile8/explore/X3/tests psha_chile8/explore/X3/REPORT.md psha_chile8/explore/X3/figures_index.md psha_chile8/explore/X3/tables psha_chile8/explore/X3/figs psha_chile8/WORKLOG.md`
  `git commit -m "A2b: GCCEL frozen as a source (v20230722) and benchmarked as the location reference (X3)"`

## 2026-11-11: A2b follow-up, crustal vs subduction split and draft A4 location rule (Claude Code)

- Asked by Pablo: whether the shallow (< 30 km) Potin result separates into crustal and subduction events, and whether GCCEL is a good reference for subduction events.
- Done:
  - `x3_gccel.py`: `classes()` (crustal onshore / crustal backarc / interface-slab onshore / offshore, from Slab2 and the X1 setting), `slab_check()`, L-g variants, and scores by group.
  - New tables `x3_slab_check.csv` and `x3_variant_scores_by_group.csv`; the summary and paired tables are split by group.
  - New section in `explore/X3/REPORT.md`.
  - Draft `catalog/PREFERENCES_draft_A4_location.md`. PREFERENCES and DECISIONS are not changed.
- Findings:
  - Crustal onshore: Potin is the best source (epicentre 3.3 km, depth −0.1 ± 4.9 km).
  - Interface / slab onshore: Potin is level with EHB L1 in depth (4.3 vs 4.2 km spread) and better in epicentre.
  - The shallow problem is the backarc (San Juan), the southern edge (Tirúa, Tabuco) and offshore events.
  - **Offshore, GCCEL is not a dependable depth reference** (stations on one side only). Every source is shallower than GCCEL there, and Slab2 sits between them.
  - Region rule L-g (Potin first only at 18–37° S and outside the backarc): mean |Δz| 8.12 → 6.85 km, epicentre 8.91 → 8.57 km.
- Decisions made: none.
- Commands: from `psha_chile8/explore/X3/`, `python x3_gccel.py` (≈ 15 s); `pytest explore/X3/tests` from `psha_chile8/` (4 pass).
- Proposed for DECISIONS (Catalog), replacing the 11 Nov location line if Pablo and S. Ruiz agree: the text in `catalog/PREFERENCES_draft_A4_location.md` (regional order, EHB first below 70 km in the flat slab, offshore depths uncertain).
- Proposed for LEARNINGS (Pitfalls, Catalog): "GCCEL offshore depths are one-sided (coastal stations only): all catalogues are 5–12 km shallower than GCCEL offshore, and Slab2 does not decide between them (X3)."
- Open questions: southern limit of the core (36 or 37° S); a note from E. Bergman on the depths of the offshore and Valparaíso clusters.
- Suggested commit (in addition to the A2b one above, or merged with it):
  `git add psha_chile8/explore/X3 psha_chile8/catalog/PREFERENCES_draft_A4_location.md psha_chile8/WORKLOG.md`
  `git commit -m "X3: crustal vs subduction split of the GCCEL benchmark; draft regional location rule for A4"`

## 2026-11-11: A3, events matched across the source catalogues (Claude Code)

- Done: `catalog/match.py`, `catalog/tests/test_match.py` (26 tests; catalog tests 55 pass), real samples in `catalog/tests/data/match/` (cut by `make_sample.py`), full run in `catalog/merged/` (log `run_2026-11-11.log`, sha256 in `merged/MANIFEST.csv`), `catalog/figs/match/summary.png`, method and references in `catalog/merged/METHOD.md`, DATA.md row. Run time 32 s.
- **Result.** 388 441 records of 11 sources → **205 001 events**; **22 477 with a native M ≥ 4.5** (target 22 300–23 200); 1 406 with M ≥ 6, 264 with M ≥ 7. 124 409 events have one source (69 781 Potin only, 41 141 CSN web only, 13 233 ISC only); at M ≥ 4.5 only 1 529 (1 334 ISC only, 167 Cabello before 1904).
- **Counts per source and rule** (rule = weakest link between the record and the reference member of its event; `ref` = it is the reference member):

  | source | records | alone | ref | id | foreign | window | second_pass | same_source |
  |---|---|---|---|---|---|---|---|---|
  | Potin | 117 998 | 69 781 | 117 974 | 0 | 0 | 0 | 0 | 24 |
  | GCCEL | 801 | 26 | 180 | 0 | 0 | 621 | 0 | 0 |
  | ISC-EHB | 10 220 | 0 | 6 153 | 0 | 0 | 4 064 | 0 | 3 |
  | ISC-GEM | 4 129 | 9 | 901 | 2 013 | 0 | 1 214 | 0 | 1 |
  | Centennial | 661 | 0 | 5 | 0 | 599 | 52 | 5 | 0 |
  | CSN web | 55 547 | 41 141 | 51 568 | 0 | 455 | 3 496 | 0 | 28 |
  | ISC | 91 171 | 13 233 | 28 023 | 7 020 | 9 220 | 46 860 | 7 | 41 |
  | ComCat | 43 982 | 30 | 30 | 551 | 20 615 | 22 768 | 0 | 18 |
  | CSN in ISC | 60 944 | 0 | 0 | 6 922 | 9 217 | 44 789 | 0 | 16 |
  | GCMT | 2 797 | 0 | 0 | 0 | 1 527 | 1 268 | 0 | 2 |
  | Cabello (< 1904) | 169 | 167 | 167 | 0 | 0 | 2 | 0 | 0 |

  Identity edges: 76 352 by ID, 57 033 by an agency's own solution. Links made by windows: Potin 45 586, CSN web 3 808, GCCEL 755, ComCat 339, ISC-GEM 10, Cabello 2, GCMT 1. Second-pass merges 7 (6 of them before 1964). Same-source merges 80. The "window" column is large for the other sources because their event's reference member is a Potin record tied by a window. The 26 GCCEL records left alone are the 26 that X3 found in no source. All 2 501 `comcat_mt` events have an event ID through ComCat.
- **Known cases.** Maule 2010, Illapel 2015 (7 sources each), Iquique 2014 (8 sources, 9 records) and Arauco 2011 (8 sources) are one event each; first-hour aftershocks stay separate (tests). RM18: 59 matched, 10 not (all year or month only); Mejillones on 1994-12-10; the Valdivia foreshock on the 18:56 event.
- **Checks** (`merged/check_blind`, `check_chance`, METHOD.md):
  - Blind recovery: identity links hidden and the records matched by time and distance alone. Of 122 308 records, 8 land in the wrong event (≤ 0.04 % per source) and 506 are missed (0.07–0.76 %). The misses are true pairs wider than the windows, mostly > 50 km at the same time. This is the rate to expect for Potin and CSN web.
  - Chance matches (source shifted ± 10, ± 20 min): Potin 160 per 118 003 records, 38 per 5 411 at M ≥ 4.5; CSN web 23 per 55 549.
  - X1 diagnostics: **splits 22** (X1 baseline 121), all between events that share a source. **False merges 536** (baseline 202): above the baseline, for reasons that are not errors. 134 are within 10 s / 50 km (the diagnostic uses 5 s / 25 km, the X1 baseline used 5 s; the brief set 10 s). 314 are CSN-in-ISC origins, tied to their ISC event by ID, in events whose reference is a Potin record more than 54 km away: the tail of the Potin–CSN distance, recovered through another member. 28 have |ΔM| > 1 (24 of them in 2025–2026, CSN web against the unreviewed ISC and ComCat). The rest are events where the CSN location is far off (next point).
- **Differences from the brief** (table with evidence in METHOD.md; each has a switch at the top of `match.py`):
  - A record is matched to the closest member of an event, not only to its best-located member (`LINK`).
  - Attach order: leftovers of the sources with identity links first, then GCCEL, Potin, CSN web (`STAGES`). With Potin first the Iquique 2014 mainshock split, because Potin lists it twice.
  - Second pass before 1964 uses 60 s / 300 km. Without it the M 7.1–7.5 events of 1909, 1910, 1911, 1912 and 1917 stay split in two.
  - New step: one source listing an earthquake twice (2 s, 50 km, scaled; `SAME_T`). 82 cases, of them 26 in the unreviewed ISC Bulletin of 2025–2026 (M up to 7.05).
  - ComCat identity links also through GUC, SJA and LIM origins; windows from pairs from 1964 on with at least 100 pairs.
  - Non-earthquakes are dropped after matching, with every record matched to them (`KEEP` to keep one).
- Decisions made: Pablo accepted the six differences from the brief (11 Nov, in the session). The DECISIONS lines below are still his to add.
- **Review lists** (`catalog/merged/review/`, sizes): `id_disagree` 693 (33 with M ≥ 7), `pre1964_window` 21, `ambiguous` 102, `merges_m6` 356, `second_pass_m5` 6, `rm18` 347 rows (59 events side by side), `rm18_matches` 59, `rm18_unmatched` 10, `dropped_types` 22, plus `same_source` 82, `id_refused` 3, `close_events_m45` 33, `possible_splits` 52, `x1_splits` 22, `x1_false_merges` 536, `blind_failures` 514.
- **What Pablo should look at first:**
  1. `dropped_types`: ISC flags 6 events as explosions. Two are M 5.0–5.1 with five sources: 2009-10-05 13:18 near Calama (plausible mine blast?) and **2010-07-30 12:10 at 37.4° S, 73.6° W**, on the coast of Arauco, which looks like a Maule aftershock. To keep one: `KEEP = [("isc", "17179356")]`.
  2. `close_events_m45` (33 pairs, 12 with M ≥ 5.5): two events within 10 s / 50 km that share a source, so nothing merged them. Real doublets (1993-05-24, 2014-04-01 23:57) and probable duplicates (ISC 2025–2026; Potin 2015-06-20; ComCat 2014-04-03 03:11) are mixed.
  3. `same_source` (82): the automatic duplicate merges; the top rows are Iquique 2014 (Potin twice, 5 s apart) and ISC 2025.
  4. `pre1964_window` (21) and `id_disagree` for M ≥ 7 (33).
  5. `possible_splits` (52; 7 with M ≥ 5.5): a Potin-only or CSN-only record 50–150 km from an ISC event at nearly the same time, with no other event around. Probably the same earthquakes. No duplicate reaches the final catalogue (these Potin records have no usable magnitude), but the event keeps the teleseismic location.
  6. `rm18_matches` where `n_candidates` > 1.
- **For A4** (not done here): 629 events have a member more than 30 s or 100 km from the reference; in 251 the reference is a Potin record. These are distant events that the CSN located badly (up to 100 s and 900 km off, e.g. 1994-09-08, 2003-08-23). "Potin first" must not apply to them. Events with `same_source` have two records of one source to choose from.
- Commands (from `psha_chile8/catalog/`, psha_renta python): `python match.py` (32 s; rewrites `merged/`); samples: `python tests/data/match/make_sample.py`; tests: `pytest catalog/tests` from `psha_chile8/`.
- Proposed for DECISIONS (Catalog), if Pablo agrees:
  - "A3 as run on 11 Nov: a record is matched to the closest member of an event; sources with identity links are completed before GCCEL, Potin and CSN web are attached; before 1964 the second pass uses 60 s / 300 km."
  - "One source listing an earthquake twice (records within 2 s and 50 km, widened for large events) is one event; listed in `review/same_source`."
  - "Non-earthquakes flagged by a source are dropped with all records matched to them."
- Proposed for LEARNINGS (Pitfalls, Catalog):
  - "The unreviewed ISC Bulletin (2025 on) lists some events twice, up to M 7; Potin lists the Iquique 2014 mainshock twice (5 s, 37 km apart); ComCat has pairs of records for one event (A3)."
  - "CSN locations of distant events can be off by 100 s and 900 km; Potin keeps them. A Potin record is not a location for events outside the network (A3)."
  - "Before 1964 ISC-GEM and Centennial / ISC origins of M 7 events differ by up to 13 s and 260 km (A3)."
- Open questions for Pablo: keep the 2010-07-30 event; merge the `possible_splits` with a wider window for isolated pairs (30 s / 150 km, both events without other neighbours); the new references in METHOD.md have unchecked DOIs.
- PLAN: A3 box and the ← marker left as they are until Pablo has gone through the review lists.
- Suggested commit (`links` is 41 MB and `events` 28 MB; leave them out if too heavy and regenerate with `python match.py`):
  `git add psha_chile8/catalog/match.py psha_chile8/catalog/tests/test_match.py psha_chile8/catalog/tests/data/match psha_chile8/catalog/merged psha_chile8/catalog/figs/match psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  `git commit -m "A3: events matched across the source catalogues, one ID per earthquake, with review lists and checks"`

## 2026-11-11: A3 rerun, single-source duplicates of ISC events removed (Claude Code)

- Asked by Pablo (11 Nov): non-earthquakes stay dropped (`KEEP = []`, so the 2010-07-30 12:10 Arauco event stays out), and the `possible_splits` records are removed.
- Done: new step `lone_dups` in `catalog/match.py`, called in `tables` after the non-earthquake step and before the event IDs. Rule (settings `LONE = ["potin", "csn"]`, `LONE_D = 50`, `LONE_M = 4.5`, with `WIDE_T = 30` s and `WIDE_D = 150` km): an event with records of Potin only or CSN web only is removed when an event with an ISC record lies within 30 s and 50–150 km, the two share no source, neither has another event within 30 s / 150 km, and the larger native magnitude is ≥ 4.5. The removed records go to the `dropped` table with `step = duplicate` and the ISC-side record they duplicate; new review list `review/dropped_duplicates`. `check` (partition) covers them. METHOD.md step 7, DATA.md row.
- Tests: 8 new in `catalog/tests/test_match.py` (removed for Potin and for CSN web; kept when closer than 50 km (merged by the window instead), beyond 150 km, another single source, no ISC record on the other side, M < 4.5, a third event within 30 s / 150 km; removed when the third event is far in time). Catalog tests: 63 pass.
- **Rerun** (`python match.py`, 34 s; `merged/` overwritten, log `run_2026-11-11.log`):

  | | before | after |
  |---|---|---|
  | events | 205 001 | **204 956** |
  | native M ≥ 4.5 | 22 477 | **22 471** |
  | M ≥ 6 / M ≥ 7 | 1 406 / 264 | 1 406 / 264 |
  | Potin records (alone) | 117 998 (69 781) | 117 960 (69 743) |
  | CSN web records (alone) | 55 547 (41 141) | 55 540 (41 134) |
  | dropped: non-earthquake / duplicate | 22 / – | 22 / 45 |

  45 records removed: 38 Potin, 7 CSN web (6 of the CSN records carried a native M ≥ 4.5; the Potin ones have no usable magnitude). All other counts, the blind and chance checks and the X1 diagnostics are unchanged.
- **Seven rows of the old list are not removed**, because they do not fit the rule as stated; they are what `review/possible_splits` now holds:
  - 3 pairs ISC against CSN web + ComCat (2026-01-02, 2026-01-23, 2026-04-15): the far event is not CSN-only;
  - ISC against ComCat alone (2026-09-05);
  - Potin 1987-04-24, 25 km and 21 s from the ISC event (closer than 50 km);
  - 2025-05-02 13:09 and 2014-04-03 03:11 (ComCat against ISC, other events nearby).
  Say if these should go too (the first four are 2026 events of the unreviewed bulletins).
- Commands: `cd psha_chile8/catalog && /data/miniforge3/envs/psha_renta/bin/python match.py`; `pytest catalog/tests` from `psha_chile8/`.
- Suggested commit:
  `git add psha_chile8/catalog/match.py psha_chile8/catalog/tests/test_match.py psha_chile8/catalog/merged psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  `git commit -m "A3 rerun: Potin-only and CSN-only duplicates of ISC events removed (45 records), 204 956 events"`

## 2026-11-11: A5, one Mw per earthquake (Claude Code)

- Done, on the rerun A3 outputs: `catalog/magnitude.py` (fits, assignment), `catalog/magnitude_check.py` (tests 1–9, figures), `catalog/tests/test_magnitude.py` (15 tests; catalog tests 78 pass), `catalog/MAGNITUDES.md`, outputs in `catalog/merged/` (DATA.md row, MANIFEST rows), 12 figures in `catalog/figs/magnitude/`. Run times: `magnitude.py` 20 s, `magnitude_check.py` 75 s. Nothing imported from `explore/`.
- **Result.** 131 347 of 204 956 events have an Mw; **16 293 with Mw ≥ 4.5** (10 672 converted, 4 654 measured, 701 ISC-GEM, 159 Cabello, 55 RM18, 52 Centennial). 73 609 without Mw (69 746 Potin-only; 362 with a native M ≥ 4.5, 181 M ≥ 5, mostly before 1964 with Pasadena MS or an untyped M): `review/no_mw`.
- **Tests, rules as briefed:**

  | test | result | pass |
  |---|---|---|
  | 1 b range 4.7–5.8 | 0.14 / 0.17 (2011 on, full / declustered), 0.20 / 0.16 (1976 on) | yes |
  | 2 rate M ≥ 5.5 | 15.8 / 16.7 / 20.9 / 19.2 per yr, departure 15.3 % | **no** |
  | 3 large events | M ≥ 7: 32.3 / 44 (from 5.0, inside the band), 31.9 / 44 (from 5.3, band starts at 32.0); Mw 6.5–7: 85.9 and 84.9 / 107 (band from 87.7). Declustered inside. Interface and in slab 16 of 16; crustal shallow 4 of 8 | **no** |
  | 4 held-out against regional Mw | 26 of 30 bins within 0.1; NEIC mb +0.16 / +0.13 at 5.0–5.5, ISC mb +0.11 at 5.25–5.5, Beijing mB +0.25 at 4.75–5.0 | partly |
  | 5 histogram | \|z\| 2.3 / 2.0 / **6.5** / 2.1: heap at 5.0–5.1 in 2000–2010 | **no** |
  | 6 1964–75 | M ≥ 5.5: 15.8 per yr, as later; converted − ISC-GEM −0.21 at 5.0–5.5, +0.05 at 5.5–6 | reported |
  | 7 Cabello / Candia–Macedo | b range 0.55 / 0.42; rate departure 34 % / 17 %; M ≥ 7 26 / 35 and 25 / 46 | – |
  | 8 sensitivity | table in MAGNITUDES.md §6 and `mw_sensitivity`; rows (a)–(f) change the M ≥ 7 prediction by ≤ 10 % and none removes the failures | – |
  | 9 synthetic | matches the quick check: floor on the reference, least squares +0.26, orthogonal +0.14, chi-square +0.05 / 0.00, inverse +0.02 / −0.03 (plain), +0.05 / 0.00 (corrected) | – |

- **What failed and why.** Tests 2, 3 and 5 fail for one reason. The surface-wave scales have the smallest σ, so they head the priority list, and the brief makes them eligible only when their own converted value is ≥ 5. That is a cut on the same noisy value: events whose MS scatters above 5.0 enter at 5.0–5.3, the rest fall back to mb or ML, which read lower. From 2000 on (IDC, Beijing, ISC MS) 100–200 events per 0.1 bin sit at 5.0–5.3 and none below. The M ≥ 5 rate of 2000–2010 is 70 per yr against 48–61, the fit on 5.0–6.5 is too steep, the large events are under-predicted. Nothing was tuned; the catalogue in `mw_2026-11-11.csv` is built as briefed.
- **Options (numbers in MAGNITUDES.md §6):**
  1. (g) judge the Mw 5 limit on the event's first other scale (mb, ML), on its own value only when there is no other. Passes tests 1–3 (b range 0.06–0.15, rate departure 12 %, M ≥ 7 41.8 / 44 and 50.1 / 44); histogram \|z\| 3.4 against the limit 3.0. One line: `JUDGE = "other"` in `magnitude.py`. My recommendation.
  2. (h) put those scales after all others: tests 1, 2, 5 pass, test 3 fails in one of eight cases (Mw 6.5–7 from 5.0).
  3. (b) the GLS mean: rate departure 9 %, histogram passes, M ≥ 7 27 / 43 from 5.0 but 40 / 43 from 5.3.
  IDC scales were left in, as the brief names no exclusion; X2 had left IDC out, which is why X2 did not show the heap this strongly.
- **Test 4, mb at 5.0–5.5:** NEIC mb and ISC mb convert 0.11–0.16 above the regional Mw there, on 160–250 held-out events. Likely the bend: the relations are tied to GCMT above 5.4 and the regional Mw sits below GCMT at 5.0–5.4. Not looked into further.
- **Other findings.**
  - Forward chi-square and inverse fits on the same pairs differ by only 0.00–0.04 at native 4.5 (`figs/magnitude/forward_inverse.png`), and sensitivity (f) scores like the main run. With the W family as reference the pairs reach low enough; the large forward bias of X1 came from GCMT alone. In test 9, chi-square with the correct η does as well as the corrected inverse fit; the inverse fit's advantage is over least squares, orthogonal fits and a wrong η. The paper's claim for the inverse step should be worded with this in mind (MAGNITUDES.md §7).
  - Offsets re-measured (means): NEIC Mwr +0.08, GFZ +0.04, GUC Mwr −0.01, CSN web Mw +0.01, CSN Mww −0.03; GCMT +0.08 / +0.05 / +0.02 above NEIC Mww at 4.75–5.0 / 5.0–5.25 / 5.25–5.75. Reference σ measured on 322 events with three Mw: GCMT 0.055, NEIC Mww 0.052, GUC Mwr 0.13.
  - Depth split chosen for ISC mb, CSN ML, VAO mb, INPRES ML; bend for the mb scales; the 1990 period split never.
  - `Mlv` has 42 pairs: ML relation with an offset of 0.24, flagged.
- **GCMT below 5.4.** Lolli et al. (2023, Table 1 notes) discard GCMT below 5.4 only when another source gives an Mw; alone it stays unchanged. So the brief's fallback applies: lowered by the measured offset per bin (0.05 / 0.07 / 0.04), 1 016 events flagged `gcmt_lowered`.
- **Priority list:** `PRIORITY` at the top of `magnitude.py` (87 scales). Head: NEIC Mwc, GS Mw, NEIC mw, USGS;NEIC Mw, IPGP Mw, NEIC MW, NEIC Mwb, AUST Mw, ComCat nc mw, GFZ MwMwp (moment types, few pairs); NEIC Ms_20, ISC MS, IDC ms1mx, GFZ MW, IDC Ms1, MOS MS, NEIC MS, NEIS MSZ, EIDC MS, …, BJI Ms7, …; VAO mb; GFZ mb, GFZ M; …; GUC ML, CSN Ml, CSN Mlv; ISC mb, NEIC mb; SJA MW; …; SJA ML; IDC mb variants; MOS mb; coda and duration scales; IDC ML and RSNC Mwp last. A pure σ order is unstable among scales within 0.01 and puts scales with 30–100 pairs ahead of ISC mb.
- **Choices I made where the brief was silent** (each a setting):
  - ISC-EHB and CSN-in-ISC magnitude tables skipped as copies of ISC rows; PDE values in the GCMT file skipped.
  - Offsets by means, not medians (values rounded to 0.1); flat = no bin with 30 pairs more than 0.05 from the mean.
  - Fitted native range = 1st to 99th percentile of the pairs; σ of a relation floored at the reference σ.
  - Cabello before 1904: its CERESIS-GEM Mw column, not Cabello's final value (they differ, e.g. 1543: 7.37 against 8.7).
  - RM18 notes: range → middle, bound and "~" → the value, "(Ms)" as Mw; flagged, σ 0.3 or half the range.
  - Test 3 band: 95 % interval of the Poisson mean given the observed count. Test 5 measure: bin against the geometric mean of its neighbours.
  - Families from the A3 reference depth without default-depth screening.
- **For A6 / A3:**
  - `review/mw_large_proxy` (17 converted Mw ≥ 6.5 since 1976), e.g. two ISC-only Maule first-hour events with IDC mb 5.6–5.7 → 6.6–6.8.
  - The 2025-05-02 Drake Passage M 7.4 is three events in the unreviewed ISC Bulletin (12:58, 13:07, 13:09); the magnitudes of the mainshock sit on the later two. Here they get 5.3 and 6.3 from mb; with a slightly different list order one of them got 8.3 from GFZ M.
  - `review/mw_iscgem_centennial`: 36 events before 1976 with ISC-GEM or Centennial ≥ 7 and a difference ≥ 0.3.
- Proposed for DECISIONS (Magnitudes), if Pablo agrees: "Surface-wave scales, MOS mb and BJI mB: the Mw 5 limit is judged on the event's first other converted scale, not on their own value (A5 heap at 5.0–5.1)." "W-family offsets as measured in A5: NEIC Mwr +0.08, GFZ +0.04, the others within 0.03."
- Proposed for LEARNINGS (Catalog pitfalls): "An eligibility limit applied to a scale's own converted value is a cut on a noisy value and heaps events just above the limit (A5)." "With the W family in the reference, forward chi-square and inverse fits agree within 0.04 at native 4.5; the forward bias is a GCMT-only effect (A5)." "The CSN regional Mw has σ ≈ 0.13, GCMT and NEIC Mww ≈ 0.05 (A5)."
- Commands (from `psha_chile8/catalog/`): `/data/miniforge3/envs/psha_renta/bin/python magnitude.py`, then `... magnitude_check.py`; tests `pytest catalog/tests` from `psha_chile8/`. The Candia and Macedo sheet is cached in `catalog/cache/candia_macedo.csv` (33 MB, read from `~/Downloads/srl-2025449_supplement.xlsx`; not for git). `match.py` rewrites `merged/MANIFEST.csv`; rerun `magnitude.py` and `magnitude_check.py` after it.
- Open questions: which option for the surface-wave rule; keep the IDC scales; a minimum number of pairs for a place in the priority list; Cabello column before 1904; the seven `possible_splits` left (entry above).
- PLAN: ← moved to A4; A3 and A5 boxes left for Pablo. FIGURES.md: the comparison figure and the synthetic figure added as drafts.
- Suggested commit:
  `git add psha_chile8/catalog/magnitude.py psha_chile8/catalog/magnitude_check.py psha_chile8/catalog/tests/test_magnitude.py psha_chile8/catalog/MAGNITUDES.md psha_chile8/catalog/figs/magnitude psha_chile8/catalog/merged psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`
  `git commit -m "A5: one Mw per earthquake, relations by inverse regression, acceptance tests (tests 2, 3, 5 fail on the surface-wave rule)"`

## 2026-11-11: A5 rerun, converted magnitudes restricted to six agencies (Claude Code)

- Asked by Pablo (11 Nov): converted (proxy) magnitudes only from the agencies that observe Chile directly or are the global references: ISC and NEIC (mb, MS), CSN / GUC ML, INPRES / SJA ML. Everything else dropped (MOS, BJI, VAO, IDC / EIDC and the rest). Measured Mw as in the brief.
- Done: setting `PROXY` at the top of `catalog/magnitude.py` (a pattern of scale names); `relations` fits only those. `PRIORITY` rewritten: NEIC Ms_20, ISC MS, NEIC MS, NEIC MSZ, GUC ML, CSN Ml, CSN Mlv, ISC mb, NEIC mb, SJA ML. `magnitude_check.py`: main scales now ISC mb, NEIC mb, CSN ML, INPRES ML, ISC MS, NEIC MS. Both scripts rerun (outputs of the first A5 run overwritten; the first-run numbers are in the entry above and in the "before" column of MAGNITUDES.md §6). Catalog tests: 78 pass. MAGNITUDES.md and DATA.md updated. `JUDGE` left at `"own"`.
- **How I read the rule** (say if any of these should be otherwise):
  - NEIC surface-wave types MS, MSZ and Ms_20 all count as NEIC MS.
  - NEIS and USCGS (the names of NEIC before 1984) are **not** kept: read strictly, they are other agency codes. 2 events with Mw ≥ 4.5 lost their Mw for this.
  - The web catalogue `Ml` and `Mlv` count as CSN ML.
  - CSN coda and duration magnitudes (GUC MD, md), the untyped GUC M and NEIC M, SJA MW and the NEIC moment types that are not reference members (Mwb, Mwc, MW) are not kept: the rule names mb, MS and ML only.
- **Events with a final Mw ≥ 4.5 in the first run (16 293):**

  | | events |
  |---|---|
  | same source and value | 13 618 |
  | changed source, still have an Mw | 2 222 |
  | … of these still Mw ≥ 4.5 | 1 229 |
  | … of these now below 4.5 | 993 |
  | lost their Mw | 453 |

  Events with Mw ≥ 4.5 now: **15 306** (459 came up from below 4.5). All events with an Mw: 116 760 (was 131 347).
  - Changed source: mostly from VAO mb (795), the Beijing, IDC and EIDC scales (1 013), GFZ mb (98), NEIC M (87), SJA MW (79), to CSN ML (1 340 with the web types), ISC mb (695), INPRES ML (88) and NEIC mb (93). Their Mw moved by −0.30 in the median (mean −0.45); 1 397 moved by 0.3 or more. The drop is the surface-wave events that sat at 5.0–5.3 and now take the mb or ML value.
  - Lost Mw (453): CSN coda and duration only (259, mostly 1990s), IDC / EIDC only (156), VAO mb only (15), others 23. By decade: 1990s 286, 2000s 75, 2010s 54, 2020s 36. 83 had Mw ≥ 5, 16 ≥ 5.5, 6 ≥ 6: 1995-07-30 05:26 (EIDC MS 6.9), 1996-03-11, 2006-04-29, two Maule first-hour events of 2010-02-27 (IDC mb only), 2018-06-21 (RSNC mb 6.0). They are in `review/no_mw` (88 196 events; 846 with a native M ≥ 4.5, 243 with M ≥ 5).
- **Acceptance table, before and after:**

  | test | before | after | pass after |
  |---|---|---|---|
  | 1 b range 4.7–5.8 | 0.14 / 0.17 / 0.20 / 0.16 | 0.14 / 0.17 / 0.11 / 0.09 | yes |
  | 2 rate M ≥ 5.5 per yr | 15.8 / 16.7 / 20.9 / 19.2, 15.3 % | 15.9 / 15.7 / 19.7 / 17.0, 15.4 % | **no** |
  | 3 M ≥ 7 pred / obs | 32.3 / 44, 31.9 / 44 | 32.9 / 44, 37.3 / 44 | yes |
  | 3 Mw 6.5–7 | 85.9, 84.9 / 107 | 82.4, 88.3 / 107 (band from 87.7) | **no** from 5.0 |
  | 3 cases passed | 25 of 32 | 30 of 32 (all events 7 of 8; crustal shallow 7 of 8) | – |
  | 4 held-out against regional Mw | 26 of 30 | 17 of 20 (same three mb bins fail: NEIC mb +0.16 / +0.13, ISC mb +0.11) | partly |
  | 5 histogram \|z\| | 2.3 / 2.0 / 6.5 / 2.1 | 2.3 / 1.3 / 3.5 / 2.2 | **no** (limit 3.0) |
  | 6 1964–75, M ≥ 5.5 | 15.8 per yr | 15.5 per yr | reported |

  The restriction removes most of the heap at 5.0–5.1 (it came from the IDC and Beijing surface-wave scales) and with it the large-event failures but one. Three narrow failures remain: the rate of M ≥ 5.5 by 0.4 % (2000–2010 at 19.7 per yr; hardly touched by converted scales), Mw 6.5–7 from floor 5.0, and the 2000–2010 histogram at 3.5. The rest of the heap is ISC MS and NEIC MS under the own-value limit; with `JUDGE = "other"` (sensitivity (g)) the histogram is at 2.2 and the rate at 12.7 %, and only the Mw 6.5–7 case from floor 5.0 stays out (84.9 / 107).
- Proposed for DECISIONS (Magnitudes (A5)), replacing "else one proxy by a fixed priority list of scales ordered by measured scatter … MS, MOS mb and BJI mB are not used below Mw 5":
  - "Converted magnitudes come only from the agencies that observe Chile directly or are the global references: ISC and NEIC mb and MS, CSN (GUC) ML, INPRES (SJA) ML. Every other agency in the ISC Bulletin (MOS, BJI, VAO, IDC / EIDC, GFZ non-moment types and the rest) and the coda, duration and untyped magnitudes are not converted; an event with nothing else has no Mw and is listed. Priority by measured scatter: NEIC and ISC MS (not below Mw 5), CSN ML, ISC mb, NEIC mb, INPRES ML (11 Nov)."
- Proposed for LEARNINGS (Catalog pitfalls): "Converting every agency of the ISC Bulletin adds little and costs homogeneity: the IDC and Beijing surface-wave scales heaped 2000–2010 at Mw 5.0–5.1; without them 453 of 16 293 events (M ≥ 4.5) lose their Mw, most of them 1990s events with a CSN coda magnitude only (A5)."
- Commands: as the entry above (`magnitude.py`, then `magnitude_check.py`).
- Open questions: the four readings above (NEIS / USCGS, coda, NEIC Mwb / Mwc); `JUDGE`; the 1990s coda-only events (213 with md, 46 with MD at Mw ≥ 4.5 in the first run) now have no Mw, which thins 1990–1999 (M ≥ 5.0 rate 48 → 44 per yr).
- Suggested commit: the `git add` lines of the entry above, with
  `git commit -m "A5: one Mw per earthquake; converted scales restricted to ISC, NEIC, CSN and INPRES; acceptance tests (2, 3, 5 fail narrowly)"`

## 2026-11-11: A4, one location, depth and mechanism per earthquake (Claude Code)

- Done: `catalog/locate.py` (rule, default-depth table, depth σ, mechanisms), `catalog/locate_check.py` (checks 1–5, figures), `catalog/tests/test_locate.py` (11 tests; catalog tests 89 pass), outputs in `catalog/merged/` (DATA.md row, MANIFEST rows), four figures in `catalog/figs/locate/`. Run times 14 s and 12 s. Nothing imported from `explore/`; the two σ tables are read from `explore/X3/tables/` and `explore/X1/tables/`, as the brief says. The location rule of the brief was followed, not the older DECISIONS line.
- **Result.** 204 956 events, each with an epicentre and origin time from one source record. 121 012 are inside the network (local catalogue first). Depth unknown for 12 070 (5.9 %). Mechanism for 3 016 events. With the Mw of the A5 second run: **15 306 events with final Mw ≥ 4.5, 13 961 of them in the domain**, 12 294 of those with a measured depth (`catalog_2026-11-11.csv`).
- **Checks:**

  | check | result |
  |---|---|
  | 1 unknown depth | all events 5.9 %; native M ≥ 4.5: 13.6 %; final Mw ≥ 4.5: 12.7 % (1 942 of 15 306). By period (final Mw ≥ 4.5): before 1964 57 %, 1964–81 23 %, 1982–99 14 %, 2000–10 8 %, 2011 on 5 %. Inside the network 0.3 %, outside 17 %. By band 6–9 % at 18–26° S, 14–15 % at 32–38° S, 27–75 % south of 38° S (`loc_checks`, `figs/locate/depth_unknown.png`) |
  | 1 saved from a fixed or default depth | the location source had no measured depth for 21 283 events; a later source gave one for 9 213 (final Mw ≥ 4.5: 2 583 of 4 525) |
  | 2 against GCCEL (775 events, GCCEL left out of both orders) | this rule: epicentre 9.35 km, \|Δz\| 7.49 km; Potin first everywhere: 9.52 and 8.40 km. Crustal backarc: 14.3 / 15.2 km against 16.7 / 28.1 km. Crustal onshore (5.2 / 6.7), interface and slab onshore (9.1 / 5.7) and offshore (10.3 / 12.7) are the same under both (`loc_gccel`, `figs/locate/gccel.png`) |
  | 3 who decides (final Mw ≥ 4.5) | epicentre: ISC 5 656, Potin 3 455, ISC-EHB L1 3 226, L2 1 517, CSN web 778, ISC-GEM 323, Cabello 169, GCCEL 93, Centennial (EHB) 81, ComCat 8. Depth: Potin 3 558, EHB L1 2 953, ISC 2 391, ComCat 1 892, EHB L2 1 331, CSN web 758, ISC-GEM 219, CSN in ISC 109, GCCEL 92, others 61, unknown 1 942 (`loc_sources`, `figs/locate/who_decides.png`) |
  | 4 sections | `figs/locate/sections.png`, six latitudes, coloured by depth source |
  | 5 A3 distant events (629) | 526 now take a global location, 103 keep the local one (at native M ≥ 4.5: 292 and 52). Of the 161 whose A3 reference was a Potin record, 65 moved to a global source and 96 stay with Potin: their teleseismic epicentre is also inside the network, so the test cannot tell which is wrong (`review/distant_events`) |

- **Potin cloud at 31° S.** Under this rule the flat-slab events east of the arc are outside the network, so most of the cloud is gone from the catalogue: at 30–32° S and 100–170 km only 13 events with Mw ≥ 4.5 keep a Potin depth, 12 of them more than 20 km below the Slab2 top. Flagged here, not corrected (A7: below the slab counts as in-slab).
- **Default depths** (`defaults_2026-11-11.csv`, 376 rows, 125 bins over the whole record): found again on the frozen data, per agency and per period. ComCat us 5 / 10 / 33 / 35, ISC 35 and the cell depths 150 / 181 / 200 / 250, NEIC 10 / 33, ISC-GEM 10 / 15 (35 added as documented), ISC-GEM supplement 15 / 25 / 35, EHB L3 steps, Centennial 35, CSN web 10, GCMT centroid 12; Potin none. 23 668 records sit on a default. A depth counts as default only if it equals the modal value of the bin (33.0, not 33.4).
- **Mechanisms:** GCMT 1 759, ComCat W-phase and other USGS tensors 1 257 (us 899, legacy US 304, Duputel 53, NEIC 1); 4 events have nodal planes only. Maule 2010 takes the Duputel W-phase product (M0 2.26e22, Mw 8.84). 19 products have a listed moment that differs from their tensor by more than 10 % (`review/mech_m0_mismatch`): 11 legacy USGS WCMT products (2010–2011), 6 GCMT and 2 recent USGS W-phase products. For those the tensor value is kept as briefed, but it is not always right either: 2010-02-28 11:25 gets Mw 4.9 from the tensor against a catalogue Mw of 6.2, and the Maule WCMT tensor itself gives 1.96e23. These need A6.
- **Choices where the brief was silent** (each a setting in `locate.py`):
  - Sources not named in the orders come last, as fallbacks: ISC-EHB L3 (epicentre only), ISC-GEM, Centennial, GCMT reference hypocentre, Cabello. In practice 1 event after 1964 is located by one.
  - Before 1964 the order continues Centennial (not EHB) → ComCat → ISC-EHB → GCMT after ISC.
  - A fixed or default depth of the location source is kept in `depth_of_loc_src` for information; `depth` is empty when unknown.
  - σ: the X3 value needs at least 20 events and σ > 0; otherwise the largest σ of the range, flagged (12 797 events, nearly all CSN web at 30–70 km, where X3 has 12 events). GCCEL depths get 3 km (its own bound). At ≥ 70 km the X1 whole-margin values (Potin 7.4, CSN web 7.6, EHB L1 1.65, L2 2.3, ISC 2.8, ISC-GEM 3.0, ComCat 5.2 km). Offshore floor of 10 km applied to 15 517 events.
  - Offshore = in the sea and more than 20 km from the coast (Natural Earth 10 m land), as X1.
  - Backarc = east of the eastern edge of the arc polygon at that latitude.
  - Domain: latitude −58 to −17 (the southern limit of the source box stands in for "the end of the Antarctic interface"), longitude −78.5 to −65.0. 200 427 events in the domain.
  - Mechanism order inside ComCat: W-phase (us Mww, Duputel, legacy WCMT), other USGS tensors, then our GCMT file, then GCMT copies in ComCat, then focal mechanisms; within a rank a product whose listed moment matches its tensor first.
- **Things to look at.**
  - Far-offshore CSN web events of 2024–2026 at 44–46° S, west of the trench, count as inside the network (the rule excludes only the backarc and the latitude limits) and have no teleseismic record yet. Visible in `who_decides.png`.
  - Of the events with Mw ≥ 4.5 in 1982–1999 only 350 of 3 106 have a Potin record, so that period is located mostly by ISC and ISC-EHB whatever the rule.
  - South of 38° S a quarter to three quarters of the M ≥ 4.5 depths are unknown.
- Proposed DECISIONS line (Catalog), replacing "Location and depth: the local relocated catalogue first … with no regional or depth exceptions":
  - "Location and depth (A4): a local catalogue comes first only inside its own network: Potin et al. (1982 to 2020-07-16) and CSN web (after) at 18–46° S and not east of the arc (`data/intraarc.shp`), tested on the epicentre of the event's teleseismic members (ISC-EHB, ISC, ComCat) where it has one. Inside: Potin / CSN web → GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → CSN in ISC. Outside, and in 1964–1981: GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → Potin / CSN web → CSN in ISC. Before 1964: Centennial where EHB-relocated (1918–1942, 1956 on), else ISC-GEM, then ISC; before 1904 Cabello's epicentre. Epicentre and origin time from the first source; depth from the first source with a measured depth (not fixed, not ISC-EHB L3, not GCCEL codes c / i / u, not on a default bin of its agency), else unknown; no filling from Slab2; GCMT centroid depths never used. Depth σ from X3 below 70 km and X1 from 70 km, at least 10 km offshore (11 Nov)."
- Proposed for LEARNINGS (Catalog pitfalls): "Legacy USGS WCMT products of 2010–2011 in ComCat carry wrong moments, in the listed scalar and sometimes in the tensor too (A4)." "Before 2000 only about one event in nine with Mw ≥ 4.5 has a Potin record (A4)."
- Commands (from `psha_chile8/catalog/`): `/data/miniforge3/envs/psha_renta/bin/python locate.py`, then `... locate_check.py`. `locate.py` joins `mw_2026-11-11.csv` if it is there; rerun it after any A5 rerun.
- PLAN: A4 box left for Pablo; ← stays on A4.
- Suggested commit:
  `git add psha_chile8/catalog/locate.py psha_chile8/catalog/locate_check.py psha_chile8/catalog/tests/test_locate.py psha_chile8/catalog/figs/locate psha_chile8/catalog/merged psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  `git commit -m "A4: one location, depth and mechanism per earthquake; local catalogue first only inside its network"`

## 2026-11-12: X4, the rule for the surface-wave magnitudes checked (Claude Code)
- Asked by Pablo: test the hypothesis that the surface-wave rule causes the failed A5 tests, also without the agency restriction, with referenced practice. No brief in `tasks/`. Nothing in `catalog/` was changed and no catalogue output was rewritten.
- Done: `explore/X4/x4_surface_wave.py` (reads `catalog/magnitude.py` and `magnitude_check.py`, writes only to `explore/X4/tables/`). The A5 fits are repeated for the six-agency set and for all agencies (87 scales, 21 of them surface-wave). Each set gets its Mw under seven rules for the surface-wave scales, scored with tests 1, 2, 3 and 5. A second score withholds the measured Mw of the events that have one and compares what the rule gives them with the measured value (`x4_blind.csv`).
- Result 1, the hypothesis holds but the effect is small with six agencies. "Own value reaches Mw 5" gives too many events at Mw ≥ 5 among the events with a measured Mw: +4.7 % (six agencies), +9.7 % (all agencies). With all agencies it is also the histogram failure (largest |z| 6.5, against 2.8–3.8 for the other single-scale rules).
- Result 2, `JUDGE = "other"` is not the fix. It errs the other way: −6.9 % (six agencies) and −14.8 % (all agencies) at Mw ≥ 5, and converted values 0.05–0.11 too low at measured Mw 4.75–5.25. It passed tests 2 and 5 only because those tests do not see a bias. Sensitivity variant (g) should not be adopted.
- Result 3, the rules of the literature have no magnitude limit, only a depth limit, and they are unbiased here. Rule 3 (surface-wave value first, no limit, events not deeper than 60 km) gives −1.9 % at Mw ≥ 5 and mean differences within 0.03 in every bin up to 5.5; rule 7 (inverse-variance mean of all converted scales, same depth limit) −2.2 % and within 0.02. Rule 3 is the order of ISC-GEM (Di Giacomo et al. 2015, p. 3 and p. 10: Ms proxy before mb proxy, Ms only for depth − error ≤ 60 km), the Centennial catalogue (Engdahl and Villaseñor 2002, p. 3) and Weatherill et al. (2016, Table 1). Rule 7 is Lolli et al. (2014, p. 13) and Gasperini et al. (2013, p. 10–11); Lolli et al. (2023, p. 3–4) use Ms only above 50 km depth. With all agencies 11 310 of 46 383 surface-wave values from 1976 belong to events deeper than 60 km (173 of 5 818 for ISC and NEIC).
- Result 4, our surface-wave relations agree with the published ones. ISC MS gives Mw 5.04, 5.43, 5.81, 6.20 at MS 4.5, 5.0, 5.5, 6.0; Scordilis (2006) 5.08, 5.42, 5.75, 6.09; Di Giacomo et al. (2015) 5.15, 5.43, 5.75, 6.10; Lolli et al. (2014) 5.00, 5.36, 5.73, 6.13 (`x4_published.csv`).
- Result 5, two A5 failures do not come from the surface-wave rule. (a) Test 3, N 6.5–7 predicted from 5.0 on the full catalogue, fails under all seven rules in both sets, also with no surface-wave magnitudes (80.1 / 101), and for Candia and Macedo (2026); the declustered version passes everywhere with the same ratio (about 0.86). (b) The histogram of 2000–2010 fails mainly because of the measured Mw: the events with a measured Mw alone count 105, 135, 73, 87, 41, 47 at Mw 5.0–5.5. These are GCMT values below 5.4 lowered by a step offset per bin after rounding to 0.1 (`reference` in `magnitude.py`), which maps two native bins into one. Not changed.
- Scores, six agencies (declustered b range 1976 on / rate M ≥ 5.5 departure / histogram |z| / events Mw ≥ 5 against measured): rule 1 0.094 / 0.154 / 3.5 / 1.047; rule 2 0.068 / 0.127 / 2.2 / 0.931; rule 3 0.075 / 0.142 / 3.3 / 0.981; rule 4 (not used) 0.098 / 0.153 / 2.8 / 0.987; rule 7 0.067 / 0.109 / 4.2 / 0.978. Full table in `x4_scores.csv`.
- Limits of the check: the withheld events are the pairs the relations were fitted on (2 to 4 parameters per relation), and they are the events that have a measured Mw, which are not a random sample below Mw 5.
- Proposed for DECISIONS (Magnitudes (A5)), replacing "MS … not used below Mw 5": "Surface-wave magnitudes are converted without a magnitude limit, only for events not deeper than 60 km (Di Giacomo et al. 2015; Engdahl and Villaseñor 2002). A limit on the converted value itself, or on another scale, biases the count at Mw ≥ 5 by +5 to +10 % or −7 to −15 % (X4)." Open between rule 3 (first scale of the list) and rule 7 (weighted mean); rule 7 has the steadier rates and b.
- Proposed for LEARNINGS: "A test that passes is not proof of no bias: judging the surface-wave limit on another scale passed the rate and histogram tests and was 7–15 % low against measured Mw." "Shifting a magnitude that is rounded to 0.1 by a step offset makes a comb in the histogram."
- Open questions: rule 3 or rule 7; whether to replace the step offset of GCMT below 5.4 by a smooth one (or dither before the shift); whether test 3 on the full catalogue is a fair test (aftershock sequences are not Poisson).
- Commands: `cd explore/X4 && python x4_surface_wave.py` (several minutes). Pablo to rerun `catalog/magnitude.py`, `magnitude_check.py` and `locate.py` only after the rule is decided and coded.
- Suggested commit:
  - `git add psha_chile8/explore/X4/x4_surface_wave.py psha_chile8/explore/X4/tables psha_chile8/WORKLOG.md`
  - message: `X4: surface-wave magnitude rule checked against measured Mw and published practice`

## 2026-11-12: A5 third run, the two published surface-wave rules and the GCMT correction tested and the best applied (Claude Code)
- Asked by Pablo after X4: test both rules and use the best. No brief in `tasks/`.
- Code: `catalog/magnitude.py` has three new settings. `JUDGE = "depth"` (surface-wave scales without a magnitude limit, only for events not deeper than `SW_Z` = 60 km; `"own"` and `"other"` kept), `COMBINE = "first"` or `"mean"` (new function `combine`, the weighted mean of the eligible scales, moved from `magnitude_check.py`; with or without the correlations between scales), `LOWER = "ramp0"` (GCMT below 5.4 lowered by a line in the GCMT value that is zero at 5.4; `"step"`, `"ramp"`, `"none"` kept). `magnitude_check.py`: sensitivity variants (b), (g), (i) follow the new settings. Three new tests in `catalog/tests/test_magnitude.py`; 108 tests pass (`pytest` from `psha_chile8/`).
- Tested (`explore/X4/x4_combos.py`, `tables/x4_combos.csv`): 4 ways of lowering GCMT × 4 rules for the converted scales, each with tests 1, 2, 3, 5 and the withheld-value check.
  - Passing everything: line zero at 5.4 with the depth limit and the first scale; the same with the mean with correlations; the step with the inverse-variance mean (but 10 % fewer events at Mw ≥ 5 than the others and correlated scales counted as independent).
  - The line zero at 5.4 removes the comb of the measured values (histogram |z| 3.3 → 2.0 for the same rule). The free line (zero at 6.07) fails test 3; no lowering fails test 3 from floor 5.3.
- Decision made, to be confirmed by Pablo: depth limit, first scale, line zero at 5.4. I first ran the weighted mean and withdrew it after looking at the largest events: with mb saturated it pulls converted large events down (2001-06-23 23:10, MS 6.97: Mw 7.0 → 6.5; 2010-03-11 15:06, MS 6.74: 6.8 → 6.4; 21 fewer events at Mw ≥ 6). The tests did not show this. The mean stays as sensitivity (b); its rates are steadier (11.3 % against 13.5 %).
- Result of the run: tests 1, 2 and 5 pass; test 3 31 of 32 (shallow crustal, declustered, M ≥ 7 from floor 5.3: 0.6 predicted, band 1.1–10.2); test 4 16 of 20 (ISC mb +0.10 / +0.12, NEIC mb +0.17 / +0.14 above the regional Mw at 5.0–5.25 / 5.25–5.5). Table before and after in `catalog/MAGNITUDES.md` §6a.
- Catalogue: Mw ≥ 4.5 15 306 → 15 549 (196 left, 439 entered); Mw ≥ 5.0 6 317 → 6 147; ≥ 5.5 2 267 → 2 259; ≥ 6.0 995 → 995. 230 measured values moved by 0.1. Converted Mw ≥ 6.5 from 1976 on: 16 events in `review/mw_large_proxy` (two from ML alone: 2010-02-27 08:25 ML 6.8 → 7.0 and 2011-01-07 04:55 at 337 km depth, ML 6.8 → 6.6 with mb 5.1; to review by hand).
- A4 rejoined with the new Mw (`locate.py`, `locate_check.py` rerun; locations unchanged): 14 157 events with Mw ≥ 4.5 in the domain, 12 413 of them with a measured depth.
- Not solved: test 4 (mb reads high against the regional Mw at 5.0–5.5); converted events at Mw ≥ 5.5 are 5–7 % too many against measured values under every rule; single ML outliers at large size.
- Proposed for DECISIONS (Magnitudes (A5)): "Surface-wave magnitudes head the list of converted scales, without a magnitude limit, only for events not deeper than 60 km (Di Giacomo et al. 2015; Engdahl and Villaseñor 2002; Weatherill et al. 2016). A GCMT value below 5.4 that stands alone is lowered by 0.159 × (5.4 − GCMT). One converted scale per event; the weighted mean is a sensitivity case because it lowers large events where mb saturates."
- Proposed for LEARNINGS: "Look at the largest events after any change of the magnitude rule; the rate, b and histogram tests do not see a few large events moving by 0.5."
- Commands (already run): `cd catalog && python magnitude.py && python magnitude_check.py && python locate.py && python locate_check.py`; `cd explore/X4 && python x4_combos.py`.
- Suggested commit:
  - `git add psha_chile8/catalog/magnitude.py psha_chile8/catalog/magnitude_check.py psha_chile8/catalog/tests/test_magnitude.py psha_chile8/catalog/MAGNITUDES.md psha_chile8/catalog/merged psha_chile8/catalog/figs psha_chile8/explore/X4 psha_chile8/WORKLOG.md psha_chile8/DATA.md`
  - message: `A5 third run: surface-wave scales by depth without a magnitude limit, smooth GCMT correction below 5.4 (X4)`
- 2026-11-12, later: Pablo confirmed the rule (surface-wave scales first, depth limit, no magnitude limit). All figures of `catalog/figs/magnitude/` and `catalog/figs/locate/` are from the third run. `offsets.png` now also shows the GCMT correction applied; it does not follow the three bin means (0.085 against 0.05 at GCMT 4.9, 0.004 against 0.04 at 5.4), the price of having no step at 5.4. New figure `explore/X4/figs/x4_rule_choice.png` (`x4_fig.py`). FIGURES.md row 3 updated. Share of measured Mw at Mw ≥ 5.0: 33 % (1976–1989), 52 %, 50 %, 82 % (2011 on); from mb: 60 %, 35 %, 12 %, 4 %.

## 2026-11-12: draft of the catalogue section of the paper (Claude Code)

- Asked by Pablo: how the catalogue-building section and its methods would read.
- Done: `paper/CATALOG_SECTION_draft.md` (new folder `paper/`). Part A method table (step, rule, references, check), part B draft text of sections 2.1–2.7 (sources, matching, location and depth, Mw, validation, catalogue, limitations), part C figures and tables with their files, part D the file behind each number, part E what is open. No code, no run.
- Numbers checked against `mw_tests_2026-11-11.csv`, `explore/X4/tables/x4_blind.csv` and `catalog_2026-11-11.csv`. In the domain at Mw ≥ 4.5: 14 157 events; 4 229 measured, 9 096 converted (mb 4 939, ML 2 822, surface-wave 1 335), 832 from ISC-GEM, Centennial, Cabello, Ruiz and Madariaga; 12 413 with a measured depth, 1 744 without (262 before 1964, 389 in 1964–1975, 1 093 from 1976); 2 671 with a mechanism.
- Also answered: unknown depths can be handled in A7 by mechanism (54 events have one), the depth set by the agency as weak information (207 of the 1 482 from 1964 set deeper than 60 km), Slab2 position, and split weights; the ISC depth-phase depths would need a new download (not done, needs approval).
- Decisions made: none. The text follows the runs as they are; classification and completeness are placeholders.
- Open: list in part E of the draft (mb sensitivity before 1990, the lower M ≥ 5 count against the published catalogues, two ML-only large events, references to add to REFERENCES.md).
- Suggested commit: `git add psha_chile8/paper psha_chile8/WORKLOG.md` with `git commit -m "Paper: outline and first draft of the catalogue section"`

## 2026-11-12: report of A3–A5 and commit lines (Claude Code)

- Asked by Pablo: commit the relevant changes, write a report for the overall conversation, say what is left here.
- Done: `catalog/REPORT_A3-A5.md` (state, numbers, method in short, tests, weak points, what Pablo decides, next steps, where the detail is). Catalog tests: 92 pass.
- Checked for the unknown depths: of the 1 482 events from 1964 on (Mw ≥ 4.5, in the domain), 1 097 have a depth from another agency in the frozen ISC download that is not flagged fixed; most sit on 33, 10 or 0 km; 258 have a USGS-family (NEIC, NEIS, USCGS) depth off the round values, 158 of them deeper than 60 km; none has a depth error. For A7 as weak information, not for the depth column.
- **Not committed:** the commit was denied by the permission setup, as CLAUDE.md says. Three commits for Pablo, from the repo root:
  1. `git add psha_chile8/catalog/match.py psha_chile8/catalog/tests/test_match.py psha_chile8/catalog/merged/METHOD.md psha_chile8/catalog/merged/counts_2026-11-11.csv psha_chile8/catalog/merged/events_2026-11-11.csv psha_chile8/catalog/merged/links_2026-11-11.csv psha_chile8/catalog/merged/review/id_disagree_2026-11-11.csv psha_chile8/catalog/merged/review/possible_splits_2026-11-11.csv psha_chile8/catalog/merged/review/dropped_duplicates_2026-11-11.csv psha_chile8/catalog/merged/run_2026-11-11.log psha_chile8/catalog/figs/match/summary.png`
     `git commit -m "A3 rerun: single-source duplicates of ISC events removed"`
  2. `git add psha_chile8/catalog/locate.py psha_chile8/catalog/locate_check.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/magnitude_check.py psha_chile8/catalog/tests psha_chile8/catalog/MAGNITUDES.md psha_chile8/catalog/merged psha_chile8/catalog/figs psha_chile8/explore/X4 psha_chile8/explore/X1/tables/t2_depth_sigma_used_for_L-d.csv psha_chile8/DATA.md psha_chile8/FIGURES.md`
     `git commit -m "A4 and A5: one location, depth, mechanism and Mw per earthquake; surface-wave scales by depth, smooth GCMT correction below 5.4 (X4)"`
  3. `git add psha_chile8/paper psha_chile8/catalog/REPORT_A3-A5.md psha_chile8/WORKLOG.md`
     `git commit -m "Catalogue report for A3-A5 and first draft of the catalogue section of the paper"`
- Left out of these lines on purpose: `PLAN.md` (Pablo's edit), `catalog/cache/` (32 MB, built from the Candia and Macedo supplement), the rest of `explore/X1/`, and the project files that were never tracked (`CLAUDE.md`, `DECISIONS.md`, `LEARNINGS.md`, `README.md`, `REFERENCES.md`, `PSHA6_NEEDED.md`, `tasks/`, `catalog/LITERATURE.md`, `MAGNITUDE_PRIMER.md`, `NOTE_SRuiz`, `PREFERENCES.md`, `RULES.md`, `WORKPLAN_A3-A5.md`). `locate.py` reads the one X1 table named in commit 2.
- Open for Pablo: list in section 6 of the report.

## 2026-11-12: DECISIONS, LEARNINGS and PLAN updated at Pablo's request (Claude Code)

- Pablo asked Claude to write the proposed lines itself and to tick the boxes (an exception to "Claude Code proposes, Pablo adds").
- `DECISIONS.md`: Catalog: the location line replaced by the A4 rule (local catalogue first only inside its network); new line on unknown depths (not filled in the catalogue, handled in A7). Magnitudes: GCMT below 5.4 lowered by the line 0.159 × (5.4 − GCMT); the proxy line now names the six agencies, the priority list and the surface-wave rule (depth limit 60 km, no magnitude limit, one scale per event). Superseded: two lines for the reversals. The offsets written in the reference line (NEIC Mwr + 0.10, GFZ + 0.03) were left as they are; the run applies + 0.08 and + 0.04 (`mw_offsets`), Pablo to say which the line should carry.
- `LEARNINGS.md` (Pitfalls, Catalog): 11 lines from the X3, A3, A4, A5 and X4 entries. The withdrawn proposal of the A5 first run (limit judged on another scale) was not added.
- `PLAN.md`: A3, A4, A5 ticked; marker on A6. `catalog/REPORT_A3-A5.md` section 6 updated.
- Commit: add `psha_chile8/PLAN.md` to the third commit of the entry above; `DECISIONS.md` and `LEARNINGS.md` are not tracked yet (`git add psha_chile8/DECISIONS.md psha_chile8/LEARNINGS.md` if they should be).

## 2026-11-12: X4 (classification), exploratory classes of the merged catalogue for A7 (Claude Code)

- Asked by Pablo in the session (no brief in `tasks/`): classify every event against Slab2, the trench and the arc polygon under several rule variants, repeat the two-plane test, compare with the old classes, Ruiz and Madariaga and Candia and Macedo. Nothing under `catalog/` changed; nothing decided; no DATA.md row (no catalogue run), no FIGURES.md row (diagnostics).
- Name clash: `explore/X4/` already held the surface-wave check of this morning. The files of this task carry the prefix `x4b_`; the earlier ones are untouched. Say if it should move to `explore/X5/`.
- Done: `explore/X4/x4b_classify.py`, `x4b_dsz.py`, `x4b_compare.py`, `x4b_figs.py`, `tests/test_x4b.py` (11 tests; 119 pass from `psha_chile8/`), `REPORT.md`, 28 tables `tables/x4b_*`, 6 figures `figs/x4b_*` (pituPLOTS b9be58a). `explore/.gitignore`: `X4/cache/` added.
- Results (Mw ≥ 4.5 in the domain, 14 157 events; baseline ± 15 km, no σ, with mechanisms, below the plate in-slab):
  - Classes: interface 3 877, in-slab 7 076, crustal forearc 466, arc 184, backarc 282, Patagonia 87, outer rise 512, unknown depth 1 567, unclassified 106.
  - 2 206 events (365 of Mw ≥ 5.5, 18 of Mw ≥ 7) change class over the 24 variants. Band ± 10 → ± 20 km: 1 226 / 129 / 10; with σ: 649 / 59 / 3; with mechanisms: 269 / 120 / 6; below the plate apart: 94 / 8 / 0.
  - 68 of the 153 events with Mw ≥ 7 have no depth (67 before 1964).
  - Atacama 1922, Concepción 1960-05-21, the Valdivia foreshock, La Ligua 1971 and Copiapó 1918 are not interface under the rule; Valdivia 1960 only at ± 15 km or wider; Valparaíso 1985 only through its mechanism.
  - Two-plane test: two modes in 7 bands below 80 km, but the sections show one thick cloud; 31–33° S is the too-deep cloud under the flat slab. Seen in every dataset: 24–25° S at 120–200 km only.
  - Same family as the old classifier for 91 % of the events both classify (88 % at Mw ≥ 5.5), as Candia and Macedo for 88 %; Ruiz and Madariaga: 33 agree, 8 disagree, 15 without depth.
- Found upstream (REPORT section 7), not corrected:
  - A4 treats every fixed depth as not measured, also the ISC and ISC-EHB depths held at a non-round value (probably depth-phase depths): 1 175 events replaced, 359 by more than 20 km (Arica 1987: 69.7 → 19 km), 285 on another side of the band.
  - 134 of the 211 "measured" depths before 1964 are round nominal values (ISC-GEM 20 / 25 km, ComCat copies at 15 / 35 / 70 km), with σ of 3–6 km.
  - The depth σ of ISC-EHB and ISC (1.6–2.8 km) is the spread between dependent catalogues.
  - Potin depths offshore: 203 events above 5 km over a deeper slab, 88 more than 40 km under a shallow slab top.
  - Two arc polygons (`data/intraarc.shp` in A4, `data/shapefiles/intra_arc.shp` in cat_handler_2), 15 square degrees apart.
  - Five mechanisms 0.5–0.6 below the catalogue Mw without a flag; 1878-01-23 at 77° W.
  - Bookkeeping: `DATA.md` "Other inputs" empty; the catalogue file is not sorted by time; the date in the merged file names no longer identifies the run; `cat_handler_2/` has uncommitted changes.
- Decisions made: none. Options for A7 in REPORT section 8. My assumptions in section 9.
- Proposed for LEARNINGS (Catalog pitfalls), if Pablo agrees:
  - "A fixed depth is not always a default: ISC and ISC-EHB hold depths at depth-phase values; discarding them replaced 359 depths by one more than 20 km off (X4 classification)."
  - "Before 1964 the ISC-GEM depths (and their ComCat copies) are nominal round values; treat them as unknown or give them a large σ."
  - "A rule on catalogue depth alone misclasses great interface events (1922, 1960 foreshocks, 1971); the events Ruiz and Madariaga name need their class from the paper."
  - "The two-plane mixture test finds two modes in a thick cloud; check the section before calling it a double zone."
- Commands (psha_renta python, from `psha_chile8/explore/X4/`, about one minute in all): `python x4b_classify.py`, `python x4b_dsz.py`, `python x4b_compare.py`, `python x4b_figs.py`; tests `pytest explore/X4/tests` from `psha_chile8/`.
- Open questions for Pablo: whether A4 is rerun for the fixed non-round depths and the pre-1964 depths before A7; which arc polygon; whether the Ruiz and Madariaga classes are set by hand in A6; whether the double zone stays in the model if the catalogue does not resolve it (ask S. Ruiz; Sippl et al. is not in refs).
- PLAN: unchanged (X4 is not a plan step; ← stays on A6).
- Suggested commit:
  `git add psha_chile8/explore/.gitignore psha_chile8/explore/X4/x4b_*.py psha_chile8/explore/X4/tests psha_chile8/explore/X4/REPORT.md psha_chile8/explore/X4/tables/x4b_* psha_chile8/explore/X4/figs/x4b_* psha_chile8/WORKLOG.md`
  `git commit -m "X4 classification: exploratory classes of the merged catalogue under 24 rule variants, two-plane test, comparison with earlier classifications"`

## 2026-11-13: X4 (classification) revised after Pablo's answers; findings for the A3–A5 conversations (Claude Code)

- Pablo's answers (12 Nov, evening):
  - A4 is rerun, in another conversation.
  - The arc polygon is the one modified last: `data/intraarc.shp` (25 Nov 2025), the one A4 and X4 already use.
  - Ruiz and Madariaga (2018) is authoritative for class.
  - The two-plane test of the first version is not valid (the Jujuy nest was not removed); the double zone is not treated in the classification, it goes into the in-slab source model.
  - In-slab classes: `intraslab_shallow`, `intraslab_intermediate`, `jujuy_nest`.
- Done:
  - `x4b_classify.py`: `sub()` (in-slab class: slab top above 50 km at the epicentre = shallow; nest within 0.8° of 66.9° W, 24.0° S at 170–320 km, measured depth, as cat_handler_2; else intermediate) and `rm18()` (the 56 events with a class in the paper take it after the rules, in every variant; `cls_auto` keeps the rule's class).
  - `x4b_dsz.py`, its tables and its three figures removed. `x4b_compare.py`, `x4b_figs.py`, tests (11) and `REPORT.md` updated (section 0 lists the changes). 119 tests pass.
  - `explore/X4/HANDOFF_A3-A5.md`: the findings for the A3, A4 and A5 conversations.
- Results (Mw ≥ 4.5 in the domain; baseline as before):
  - interface 3 893 (50 of Mw ≥ 7), intraslab_shallow 1 211 (6), intraslab_intermediate 4 963 (25), jujuy_nest 902 (3), crustal forearc 465, arc 185, backarc 282, Patagonia 87, outer rise 511 (7), unknown depth 1 552 (54), unclassified 106 (3).
  - 23 of the 56 Ruiz and Madariaga events change class through the paper (12 from unknown depth to interface).
  - Over the 24 variants 2 195 events change class (354 of Mw ≥ 5.5, 10 of Mw ≥ 7).
  - The three in-slab classes map almost one to one onto the old intra_slab, slab_deep and deep_nest.
- New upstream finding (for A5): the five events with a catalogue Mw 0.5–0.6 above their moment tensor take a CSN regional Mw; 16 of 97 GUC Mwr values differ from the event's tensor by 0.3 or more.
- Proposed for DECISIONS (Classification), Pablo to add:
  - "In-slab classes: intraslab_shallow (slab top above 50 km), intraslab_intermediate, jujuy_nest; the double seismic zone is not an event class, it is built in the in-slab source model (12 Nov)." This replaces "Jujuy nest no longer a class of its own (9 Nov)" and the double-zone line of 8–9 Nov.
  - "Arc polygon: `data/intraarc.shp` (12 Nov)."
  - "The events Ruiz and Madariaga (2018) name take the paper's class, set after the rules (12 Nov)."
- Commands: from `explore/X4/`, `python x4b_classify.py`, `python x4b_compare.py`, `python x4b_figs.py`. Rerun after the A4 rerun (change `RUN` at the top of `x4b_classify.py` if the files get a new date).
- Open: the shallow / intermediate limit acts on the slab top at the epicentre (La Ligua 1965 is shallow, Punitaqui 1997 intermediate); nest limits taken from cat_handler_2, not refitted.
- Suggested commit (replaces the one of the entry above):
  `git add psha_chile8/explore/.gitignore psha_chile8/explore/X4/x4b_*.py psha_chile8/explore/X4/tests psha_chile8/explore/X4/REPORT.md psha_chile8/explore/X4/HANDOFF_A3-A5.md psha_chile8/explore/X4/tables/x4b_* psha_chile8/explore/X4/figs/x4b_* psha_chile8/WORKLOG.md`
  `git commit -m "X4 classification: exploratory classes under 24 rule variants, in-slab classes, Ruiz and Madariaga classes, findings for A3-A5"`

## 2026-11-13: X4 handoff checked against the catalogue (Claude Code, A3–A5 conversation)

Checked `explore/X4/HANDOFF_A3-A5.md` on `catalog_2026-11-11.csv` and the frozen ISC and ISC-EHB files. No code or output changed.

- A4 point 1 (fixed depths): not right for ISC. Fixed ISC depths off a multiple of 5 km are whole numbers that repeat by region (181 km 908 times, 117 km 346 times, 99 % integers): the default depth grid of the ISC locator (Bondár and Storchak 2011), not depth-phase depths. They account for 1 061 of the 1 175 events and 338 of the 359 changes above 20 km. Discarding them is right. For ISC-EHB the point holds: 881 L1 / L2 records are flagged fixed; in the catalogue (Mw ≥ 4.5, domain) 398 events located by ISC-EHB L1 / L2 take their depth elsewhere, 66 by more than 20 km, 15 end unknown. Arica 1987 (69.7 → 19 km) confirmed. To confirm in Engdahl et al. (2020) what a fixed L1 / L2 depth is.
- A4 point 2 (before 1964): confirmed. 211 measured depths, 134 on a multiple of 5 km, σ 2.8–11 km. Atacama 1922 at 70 km comes from ComCat.
- A4 point 3 (Potin): the examples are confirmed (Tirúa 2011 at 2.8 km, 1995-11-01 at 88.5 km); counts not recomputed.
- A4 point 7: catalogue file not sorted by time, confirmed.
- A5 point 1: confirmed. 13 of 92 GUC Mwr values are 0.3 or more from the event's tensor (7 of 1 839 for GCMT). Also seen: six GCMT events of Feb–Jun 2010 whose ComCat tensor Mw is 0.5–1.3 away; the tensor probably belongs to another event (review list of moment mismatches).
- A3: nothing to change.

Proposed for a rerun of A4 (not started): fixed ISC-EHB L1 / L2 depths count as measured; before 1964 a depth on a round value is unknown and the rest get σ ≥ 20 km; offshore, ISC-EHB and GCCEL before Potin for depth, and a Potin record more than 50 km from the teleseismic members is not used; depth σ floor of 5 km. For A5: drop a reference value more than 0.3 from the event's other moment magnitudes; rerun after A4. Fixed ISC depths stay discarded.

## 2026-11-13: A4 rerun with four changes, A5 fourth run, classification rerun (Claude Code, A3–A5 conversation)

Asked by Pablo after the check of the X4 handoff (entry above). All 123 tests pass. New files carry the date 2026-11-13; the files of 11 Nov are kept.

- **A4, `catalog/locate.py`** (settings `FAR_KM`, `SEA`, `OLD_ROUND`, `LAST`, `SIG_MIN`, `SIG_LAST`, `SIG_OLD`, `MECH_DIFF`):
  - Fixed ISC-EHB depths. The ISC-EHB page defines L1 as a free depth with error below 5 km and three depth phases, or a fixed depth constrained by depth phases or USGS broadband depths; L2 as a free depth with error 5–15 km, or a fixed depth from the GCMT solution (isc.ac.uk/isc-ehb). So a fixed L1 depth counts as measured; a fixed L2 depth is used only when no other depth is measured (flag `depth_fixed_gcmt`, σ 15 km; 3 events at Mw ≥ 4.5). Fixed ISC depths stay out.
  - Before 1964 a depth on a multiple of 5 km is unknown (133 events at Mw ≥ 4.5 lose their depth, Valdivia 1960 and Atacama 1922 among them); the 78 that keep one get σ 20 km.
  - Offshore (more than 20 km from the coast) and inside the network, the depth order is GCCEL, ISC-EHB L1, L2, then the local catalogue. Measured on the catalogue first: offshore Potin is a median 11.1 km shallower than GCCEL (138 events), ISC-EHB L1 1.1 km (40), L2 4.2 km (24), ISC 5.2 km.
  - A local record more than 50 km from the closest teleseismic or GCCEL record of its event is not used (the event follows the order of events outside the network): 85 events at Mw ≥ 4.5, 13 of Mw ≥ 5.5.
  - Depth σ at least 5 km for every source but GCCEL.
  - Output sorted by time. New review list `review/mech_mw_differs_2026-11-13.csv` (mechanism Mw 0.4 or more from the catalogue Mw, 13 events).
  - Not changed: `backarc()` beyond the ends of the polygon (it acts only north of 17.6° S and south of 47.2° S, outside the network latitudes, so A4 is not affected); the far-offshore CSN web events at 44–46° S.
- **A4 result** (Mw ≥ 4.5 in the domain, against the run of 11 Nov on the same events): epicentre source changed for 91 events, depth for 860 (126 by more than 20 km; 133 to unknown, 9 from unknown). Arica 1987 is back at 69.7 km; 1995-11-01 Mw 6.6 goes from 88.5 to 20 km; Iquique 2014 from 21 to 30 km (GCCEL). GCCEL benchmark (775 events, GCCEL left out): epicentre 8.82 km (9.35), depth 6.96 km (7.49), offshore depth 10.99 km (12.65). The offshore order was chosen on the same GCCEL events, so this gain is not an independent check.
- **A5, `catalog/magnitude.py`** (settings `LOC`, `REG`, `REG_OTHER`, `REG_TOL`, `REG_N`):
  - Depth for the depth split and the surface-wave limit: the A4 depth where measured, else the A3 reference depth.
  - CSN regional Mw cross-check: first tried as proposed (any value more than 0.3 from the event's other moment magnitudes): 157 values dropped, 148 of them above the others. 131 of these have a single other value, almost always NEIC Mwr, which is 0.15 lower than GUC Mwr on average with a pair scatter of 0.16; a difference above 0.3 is then expected for about one pair in eight and does not show which value is wrong. Kept: dropped only against two or more other values (26); the 131 pairs are listed, not changed.
  - Result: 15 636 events with Mw ≥ 4.5, 14 234 in the domain (14 157). 613 values changed, 84 by 0.2 or more. NEIC mb now split by depth (cross-validation 0.0410 against 0.0412), about ± 0.05 at mb 4.5. Mw ≥ 5.0: 5 470 (5 463); Mw ≥ 5.5: 1 941 (1 949).
  - Tests (`magnitude_check.py`): 1 0.08 / 0.15 declustered; 2 13.8 %; 3 31 of 32, Mw ≥ 7 37.3 of 44; 4 16 of 20; 5 2.1 σ. Same passes and failures as on 12 Nov.
- **Classification (`explore/X4`, three scripts, `RUN` set to 2026-11-13, `A3` added for the Ruiz and Madariaga file)**, baseline, Mw ≥ 4.5 / ≥ 5.5 / ≥ 7: interface 3 896 / 636 / 46; in-slab 7 131 / 664 / 29 (shallow 1 211, intermediate 5 011, nest 909); crustal forearc 419, arc 179, backarc 283, Patagonia 86; outer rise 504 / 94 / 7; unknown depth 1 644 / 384 / 66 (1 552 / 282 / 54 before); unclassified 92. `REPORT.md` of X4 not rewritten: its numbers are those of 11 Nov.
- Run order used: `locate.py` (with `MW` on the old date), `locate_check.py`, `magnitude.py`, `locate.py` (with `MW = "2026-11-13"`, the state of the file now), `magnitude_check.py`; then from `explore/X4/`: `x4b_classify.py`, `x4b_compare.py`, `x4b_figs.py`.
- Updated: `DATA.md` (row), `catalog/REPORT_A3-A5.md` (numbers and points 3, 5), `catalog/MAGNITUDES.md` (section 10), `paper/CATALOG_SECTION_draft.md` (note at the top; text and numbers below it still of 12 Nov). The figures in `catalog/figs/locate/` and `magnitude/` are redrawn from the new run.
- Proposed for DECISIONS, Pablo to add:
  - Location: "A local record more than 50 km from the closest teleseismic or GCCEL record of its event is not used (13 Nov)."
  - Depth: "A fixed ISC-EHB L1 depth counts as measured (depth phases); a fixed L2 depth (GCMT) only when nothing else is measured. Before 1964 depths on a multiple of 5 km are unknown. Offshore, inside the network: GCCEL → ISC-EHB L1 / L2 → local catalogue. Depth σ at least 5 km, 20 km before 1964 (13 Nov)."
  - Magnitudes: "A CSN regional Mw more than 0.3 from the median of two or more other moment magnitudes of the event is left out. Depth split of the relations on the A4 depths (13 Nov)."
- Open:
  - The 131 CSN / NEIC regional pairs more than 0.3 apart: which agency to trust below Mw 5.2 where no third value exists.
  - The NEIC mb depth split is a marginal choice of the cross-validation.
  - 66 events of Mw ≥ 7 have an unknown depth after the classification (most before 1964): A6.
  - The paper draft text is to be brought to the numbers of 13 Nov.
- Suggested commit (after the three of 12 Nov):
  `git add psha_chile8/catalog/locate.py psha_chile8/catalog/locate_check.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/tests/test_locate.py psha_chile8/catalog/tests/test_magnitude.py psha_chile8/catalog/merged/*_2026-11-13.* psha_chile8/catalog/merged/review/*_2026-11-13.csv psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/catalog/figs psha_chile8/catalog/REPORT_A3-A5.md psha_chile8/catalog/MAGNITUDES.md psha_chile8/paper/CATALOG_SECTION_draft.md psha_chile8/explore/X4 psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  `git commit -m "A4 and A5 rerun: ISC-EHB fixed depths, depths before 1964, offshore depth order, distant local records, CSN regional Mw cross-check; classification rerun"`

## 2026-11-13: paper draft brought to the run of 13 Nov (Claude Code, A3–A5 conversation)

- `paper/CATALOG_SECTION_draft.md`: method table (steps 3–5), text 2.3 (50 km condition, offshore depth order, fixed and nominal depths, σ floors, benchmark 8.8 / 7.0 km), 2.4 (CSN cross-check), 2.5 (test values), 2.6 and 2.7 (counts; two new limitations), parts C to E (file dates, two new open items). The note of the morning is removed.
- The fit of the GCMT correction gives 0.162 × (5.4 − GCMT) on 812 pairs in the run of 13 Nov (0.159, 813 before); DECISIONS still carries 0.159.
- Not redone on the new run: the withheld-Mw check of the surface-wave rule (`explore/X4/tables/x4_blind.csv`); marked in the draft.
- Add `psha_chile8/paper/CATALOG_SECTION_draft.md` and `psha_chile8/catalog/REPORT_A3-A5.md` to the commit of the entry above (already in its list).

## 2026-11-13: X4 classification report brought to the catalogue of 13 Nov (Claude Code, A3–A5 conversation)

Asked by Pablo. Only `explore/X4/REPORT.md` changed; no code, table or figure (those are of the rerun of this morning).

- Every number of the report now comes from the tables of the 13 Nov run or from a recount on `tables/x4b_events_m45.csv` (soft membership, the two settings outside the grid, depth differences against the old classifier, Potin depths).
- Section 0 has a table of what moved against the first version; section 7 is now "what was found upstream and what was done with it", with what remains.
- Main changes: class depends on the variant for 2 173 events (2 195); unknown depth 1 644 (1 552), 66 of Mw ≥ 7 (54); against Ruiz and Madariaga the rule alone gives 31 right, 5 wrong, 20 without depth (33, 8, 15).
- Corrected against the first version: the far-offshore cluster at 44–46° S in the outer-rise class has only 10 events from 2024 on at Mw ≥ 4.5 (153 of all years); the dense cluster is in the map of all events.
- Still open, new in the report: 180 Potin depths above 5 km over a slab top deeper than 15 km and 56 more than 40 km under a shallow slab top (near the coast, so not reached by the offshore rule of A4); two of the five CSN regional Mw outliers unchanged (2015-09-05, 2016-02-05).
- `HANDOFF_A3-A5.md` is left as written (numbers of 11 Nov).
- Suggested commit:
  `git add psha_chile8/explore/X4/REPORT.md psha_chile8/WORKLOG.md`
  `git commit -m "X4 classification report brought to the catalogue of 13 Nov"`

## 2026-11-13: Potin depths near the coast, A4 third rule, A5 fifth run (Claude Code, A3–A5 conversation)

Asked by Pablo ("fix the Potin depths near the coast"). All 124 tests pass. New files carry the run name `2026-11-13b`; the files of `2026-11-13` are kept.

- **What was measured** (events inside the network, Potin depth against the GCCEL depth of the same event; ISC-EHB L1 gives the same picture):
  - by distance to the coast: Potin is a median 11.7 km shallower than GCCEL at 20–40 km offshore, 1.4 km at 10–20 km offshore, within 1.5 km from the coast inland;
  - by Potin depth, west of the line 20 km inland: −17 to −21 km for Potin depths under 10 km, −11 km at 10–20 km, −2 km at 20–30 km, +1 km at 30–80 km; +64 km above 80 km (3 events; 11 against ISC-EHB L1, +72 km);
  - of 92 such events with a Potin depth under 20 km, GCCEL is deeper by more than 10 km for 62 and never shallower by more than 5 km; 25 are also under 20 km in GCCEL;
  - of the 770 events of Mw ≥ 4.5 concerned, 189 have a mechanism and 161 are thrusts.
- **Rule (`locate.py`, `COAST_KM = 20`, `POTIN_Z = (20, 80)`, function `coastal`)**: west of the line 20 km inland of the coast, a Potin depth outside 20–80 km gives way to the first measured depth of GCCEL, ISC-EHB L1, L2, ISC, ComCat. Without one the Potin depth stays. The epicentre stays Potin's. Flag `potin_depth_not_used`. Not applied to CSN web depths (too few pairs with GCCEL to judge).
- **Tried and not taken**: ISC and ComCat before Potin for every offshore event. Against GCCEL it changes nothing (mean depth difference offshore 9.8 against 9.9 km); against ISC-EHB L1 it looks much better (5.1 against 14.0 km), but ISC and ISC-EHB share data.
- **Effect**: 702 events of Mw ≥ 4.5 in the domain take another depth (79 of Mw ≥ 5.5): ISC 539, ComCat 95, GCCEL 25, ISC-EHB 43. 236 become more than 10 km deeper; 251 become shallower (27 of them from the deep side). GCCEL benchmark, depth: 6.59 km (6.96); offshore group 10.58 (10.99). The rule was chosen on the same GCCEL events.
- **Limits**: for the events that are also shallow in GCCEL the replacement is no better than Potin (7.5 against 6.4 km); the replacement depths are poor offshore too (2015-11-11 01:54 Mw 6.8: Potin 12.2 km, now ISC 3.9 km). The Iquique foreshock of 2014-03-16 keeps a shallow depth (ISC 9.4 km).
- **A5 fifth run** (same rule, new depths): 14 243 events of Mw ≥ 4.5 in the domain (14 234); 5 467 of Mw ≥ 5.0, 1 943 of Mw ≥ 5.5; 44 magnitudes changed, 8 by 0.2 or more. Tests: T1 0.08 / 0.15 (declustered), T2 13.7 %, T3 32 of 32 (Mw ≥ 7: 37.5 of 44), T4 16 of 20, T5 2.1 σ.
- **Classification rerun** (baseline, Mw ≥ 4.5 / ≥ 5.5 / ≥ 7): interface 3 926 / 644 / 46; in-slab 7 177 / 669 / 29 (shallow 1 255, intermediate 5 012, nest 910); crustal forearc 352 / 47 / 2 (419 / 58 / 2 before); arc 179, backarc 283, Patagonia 86; outer rise 504; unknown depth 1 644; unclassified 92. Class depends on the variant for 2 168 events. Left: 52 Potin depths above 5 km over a slab top deeper than 15 km (180), 38 more than 40 km under a shallow slab top (56).
- **Not updated**: `catalog/REPORT_A3-A5.md`, `paper/CATALOG_SECTION_draft.md` and `explore/X4/REPORT.md` still carry the numbers of the run `2026-11-13`, while `explore/X4/tables` and `figs` and `catalog/figs` are now of `2026-11-13b`. To be brought up once Pablo keeps the rule.
- **Proposed line for DECISIONS**: "Near the coast (west of the line 20 km inland) a Potin depth shallower than 20 km or deeper than 80 km is replaced by the first measured depth of GCCEL, ISC-EHB, ISC, ComCat (13 Nov; Potin is a median 11–21 km shallower than GCCEL there for depths under 20 km)."
- Run order: `locate.py` (`MW` on 2026-11-13), `magnitude.py`, `locate.py` (`MW = "2026-11-13b"`, the state of the file now), `locate_check.py`, `magnitude_check.py`; from `explore/X4/`: `x4b_classify.py`, `x4b_compare.py`, `x4b_figs.py`.
- Suggested commit (with the report line of the entry above):
  `git add psha_chile8/catalog/locate.py psha_chile8/catalog/locate_check.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/tests/test_locate.py psha_chile8/catalog/merged psha_chile8/catalog/figs psha_chile8/explore/X4 psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  `git commit -m "A4: Potin depths outside 20-80 km near the coast replaced by a global depth; A5 and classification rerun (run 2026-11-13b)"`

## 2026-11-13: table of the location, depth and magnitude rules with their support (Claude Code, A3–A5 conversation)

Asked by Pablo: the rules had become confusing and need references. New file `catalog/RULES_LOCATION_MAGNITUDE.md`. No code or run changed.

- One table for location and depth (L1–L4, D1–D7) and one for magnitude (M1–M8): the rule as the code applies it, our evidence, the literature, and a support grade (standard practice / documentation of the source / own measurement / own choice).
- Literature searched on the web for the location and depth rules (the magnitude rules were already covered in `MAGNITUDES.md`). Nine references to add to `REFERENCES.md`, listed in section 5 of the file; only abstracts or citing text were seen, so each needs reading before it is cited.
- Section 4 separates the method (citable) from the patches (few events, no citation for the number) and proposes: drop the coastal Potin rule of this afternoon (D6) and the last-resort GCMT depth (3 events); describe the 50 km check and the CSN cross-check as quality checks; simplify the σ floors; drop the depth split of NEIC mb; decide on the GCMT line below 5.4.
- Pablo's objection to D6 recorded: the local study is expected to be better than global locations, and thrust mechanisms do not exclude upper-plate splay faults. The check of the afternoon: GCCEL depths for these events come from near-source and local stations (80 of 92) and agree with depth phases, but the rule replaces 634 of 702 depths with plain ISC or ComCat values, which is not supported.
- Open: Pablo to choose which patches stay; then one rerun of A4, A5 and the classification, and the three reports brought to it. The run `2026-11-13b` (with D6) is on disk; the run `2026-11-13` is the committed one.

## 2026-11-13: A4 simplified (run 2026-11-13b), report section on events without depth (Claude Code, A3–A5 conversation)

Agreed by Pablo after the rules table ("Yes, simplify"). All 123 tests pass. This entry replaces the entry "Potin depths near the coast, A4 third rule" above: that rule was discarded and the files of `2026-11-13b` were overwritten with this run.

- **Dropped from `locate.py`:** the coastal Potin depth rule (Pablo: a local study is expected to locate better than global catalogues, and thrust mechanisms do not exclude upper-plate splay faults; the rule replaced 634 of 702 depths with plain ISC or ComCat values, which nothing supports); the last-resort GCMT depth of ISC-EHB L2 (3 events).
- **Changed:** before 1964 a depth counts only where its catalogue marks it as constrained (`OLD_OK`): ISC-GEM depth quality A or B (Di Giacomo et al. 2018, Table 1) or a free-depth Centennial solution (DEQ). This replaces "not on a multiple of 5 km". 83 events before 1964 keep a depth (78 before).
- **Kept after looking:** the depth split of NEIC mb. It comes out of the general choice rule (simplest form within one standard error of the best in cross-validation); removing it would need an exception.
- **Kept, open for Pablo:** the GCMT line below 5.4 (own choice; Lolli et al. 2023 leave such values unchanged).
- **Result:** against the committed run `2026-11-13`, 35 depths differ (16 to unknown, 18 from unknown) and no magnitude. 14 234 events of Mw ≥ 4.5 in the domain, 12 376 with a measured depth, 1 858 without. GCCEL benchmark and the five magnitude tests unchanged (8.82 km, 6.96 km; T3 31 of 32).
- **Classification rerun** (baseline, Mw ≥ 4.5 / ≥ 5.5 / ≥ 7): interface 3 897 / 637 / 47; in-slab 7 133 / 666 / 31; crustal forearc 418, arc 178, backarc 282, Patagonia 85; outer rise 504; unknown depth 1 646 / 384 / 64; unclassified 91. `explore/X4/REPORT.md` has a note with these; its other numbers are of the run `2026-11-13` and differ by a few events.
- **`catalog/REPORT_A3-A5.md`, new section 6:** what the classification has to decide about events without depth (counts by period and size, why each depth was rejected, position against the slab, four options, what to check first). Large events are left to the hand review of A6. The paper draft and `RULES_LOCATION_MAGNITUDE.md` are on this run.
- **Proposed lines for DECISIONS** (replace the depth lines proposed in the entry "A4 rerun with four changes"):
  - "A local record more than 50 km from every teleseismic or GCCEL record of the event is not used (quality check, 85 events)."
  - "Depth: fixed depths, ISC-EHB L3 and agency default values are not measurements; a fixed ISC-EHB L1 depth is (held at its depth-phase value). Before 1964 only ISC-GEM depth quality A or B and free-depth Centennial solutions count. Offshore (more than 20 km from the coast) GCCEL and ISC-EHB L1 / L2 go before the local depth. σ at least 5 km, 10 km offshore, 20 km before 1964."
  - "Potin depths are not replaced by ISC or ComCat depths (13 Nov, tried and dropped)."
  - "A CSN regional Mw more than 0.3 from the median of two or more other moment magnitudes of the event is left out (quality check, 26 values)."
- **Proposed lines for LEARNINGS:**
  - "A check that finds a problem tends to produce a patch rule for a few events. Before adding one, ask whether it has a citation and whether a quality-check sentence would do. Table of rules by support: `catalog/RULES_LOCATION_MAGNITUDE.md`."
  - "ISC fixed depths at odd values (181, 117 km) are the regional default grid of its locator, not depth-phase depths; ISC-EHB L1 fixed depths are depth-phase depths."
  - "Potin depths under 20 km at and off the coast are a median 11–21 km shallower than GCCEL and ISC-EHB L1, but about a quarter are truly shallow; ISC depths are not a tested replacement for small events."
  - "The source catalogues carry their own depth quality flags (ISC-GEM A–C, Centennial DEQ / FEQ / LEQ, ISC-EHB L1–L3, GCCEL depth codes); use them before inventing a screen."
- Open: Pablo to choose the option of section 6; GCMT line; the nine references of `RULES_LOCATION_MAGNITUDE.md` section 5 to read and add to `REFERENCES.md`; withheld-Mw check of the surface-wave rule not repeated since 12 Nov.
- Suggested commit (from the repo root; it includes the report commit of the entry "X4 classification report brought to the catalogue of 13 Nov" if that was not run):
  `git add psha_chile8/catalog/locate.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/tests/test_locate.py psha_chile8/catalog/merged psha_chile8/catalog/figs psha_chile8/catalog/REPORT_A3-A5.md psha_chile8/catalog/RULES_LOCATION_MAGNITUDE.md psha_chile8/paper/CATALOG_SECTION_draft.md psha_chile8/explore/X4 psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  `git commit -m "A4 simplified: depths before 1964 by the catalogues' own flags, no last-resort GCMT depth (run 2026-11-13b); rules table with references; report section on events without depth"`
