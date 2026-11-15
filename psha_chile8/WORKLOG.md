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

## 2026-11-13: two decisions of 13 Nov applied; A5 rerun with the Centennial first before 1976 (run 2026-11-13c) (Claude Code, A6 conversation)

Asked by Pablo, who allowed the edits of DECISIONS, PREFERENCES and RULES_LOCATION_MAGNITUDE for these two decisions and the full rebuild. All 123 tests pass.

- **Notes edited:** `DECISIONS.md` (Magnitudes (A5): the GCMT line below 5.4 is kept, with the agreed wording; the "One Mw per event" line carries the new order before 1976); `catalog/RULES_LOCATION_MAGNITUDE.md` (M3 is support C; M1 carries the order; section 4 row of M3); `catalog/PREFERENCES.md` (question 1 answered, the two Mw cells of 1904–1975, a row in the change table).
- **`magnitude.py`:** `OLD = ["Centennial", "ISC-GEM"]`. A Centennial entry gives: an Mw (Pacheco and Sykes, Okal) as given; else its preferred (first-listed) magnitude, Ms by the Di Giacomo et al. (2015) relation, an untyped value the same way after subtracting 0.2 (both as before), mB by Abe (1982). An entry whose preferred magnitude is mb leaves the event to ISC-GEM. Before, the type order Mw, mB, Ms, untyped was applied to all listed values, which would have taken a secondary mB before the preferred Ms of a shallow event.
- **Abe mB was going in as Mw unconverted** (22 events of the run `2026-11-13b`, the intermediate-depth events ISC-GEM lacks, e.g. 1929-10-19 mB 7.4 as Mw 7.4). Now converted with Abe (1982, J. Phys. Earth 30, 321–330; read, PDF from J-STAGE): log M0 = 2.4 mB + 10.0 for intermediate and deep events (eq. 5, p. 324) and 2.4 mB + 9.6 for shallow ones (eq. 7, p. 328), M0 in dyn cm, with the Hanks and Kanamori constant, so Mw = 1.6 mB − 4.07 deeper than 60 km and 1.6 mB − 4.33 otherwise (depth of the event, the provisional A3 depth where none was measured). σ 0.3 (`SIG_MB`, my choice: Abe shows a scatter of about a factor 3 in M0). Flag `converted_from_mb`. Check on the new catalogue: 42 events take an Abe mB (32 in the domain), none with Mw equal to the mB. Calama 1950 (mB 7.7) and La Ligua 1965 (mB 7.4) are named by Ruiz and Madariaga and keep Mw 8.0 and 7.4; by the relation they would be 8.25 and 7.77.
- **Rerun:** `magnitude.py`, `locate.py`, `magnitude_check.py` with `RUN = "2026-11-13c"` (depths of `locations_2026-11-13b`; locations, depths and mechanisms are identical to `2026-11-13b`). DATA.md has the row.
- **What changed** (against `2026-11-13b`): 138 events changed Mw, all of 1906–1975, 121 in the domain. Of the events with Mw ≥ 6 before or after, **113 changed: 70 up, 43 down, 43 by 0.3 or more**, mean +0.10. Events of Mw ≥ 7 in the domain: 165 (153); before 1976 129 (117); of Mw ≥ 7.5 before 1976 59 (47). Counts at Mw ≥ 4.5, 5.0, 5.5 unchanged (14 234, 5 470, 1 941). Kinds at Mw ≥ 4.5 in the domain: Centennial 157 (37), ISC-GEM 515 (635).
- **Largest changes** (Mw before → after, Centennial value):

| event | before (ISC-GEM) | after | Centennial | note |
|---|---|---|---|---|
| 1967-03-13 16:06, 40.2° S | 5.7 | 7.1 | BRK 7.3, untyped | suspect Centennial value; A6 |
| 1971-06-17 21:00, 25.4° S, 90 km | 6.3 | 7.5 | Abe mB 7.2 | A6 |
| 1948-05-11 08:55, 17.3° S | 6.5 | 7.5 | Abe mB 7.4 | A6 |
| 1918-05-20 17:55, 28.9° S | 6.9 | 7.8 | Abe mB 7.6 | A6 |
| 1925-05-15 11:57, 25.5° S | 6.3 | 7.1 | Abe Ms 7.1 | A6 |
| 1959-06-14 00:12, 20.3° S, 109 km | 7.1 | 7.9 | Abe mB 7.5 | Abe (1982, Table 1) lists M0 87 × 10²⁵ dyn cm for it: Mw 7.2 |
| 1962-07-17 05:32, 43.1° S | 5.8 | 6.6 | BRK 6.8, untyped | |
| 1969-07-19 04:54, 17.3° S | 6.5 | 5.7 | PAS 5.7, untyped | |
| 1934-03-01 21:45, 40.9° S | 6.6 | 7.3 | Abe mB 7.3 | |
| 1962-08-03 08:56, 23.3° S, 113 km | 6.8 | 7.5 | Abe mB 7.2 | |
| 1960-11-01 08:45, 38.4° S | 7.4 | 6.8 | Abe Ms 6.8 | |
| 1920-08-03 19:57, 27.3° S | 7.0 | 6.4 | G&R 6.6, untyped | |
| 1962-02-14 06:36, 38.1° S | 7.1 | 7.7 | Abe mB 7.5 | |
| 1960-06-06 05:55, Aysén | 7.7 | 7.2 | Pacheco and Sykes Mw 7.2 | A6 (named case) |

  By Centennial type, mean change at Mw ≥ 6: Abe mB +0.33 (30 events), Pacheco and Sykes Mw +0.01 (18), Abe Ms −0.04 (14), Pasadena untyped +0.08 (15), G&R untyped −0.16 (7), Berkeley untyped +0.87 (3), NEIS and USCGS Ms −0.1 (16). Full list: the events with `mw_kind` changed between `catalog_2026-11-13b.csv` and `catalog_2026-11-13c.csv`.
- **To look at (Pablo, S. Ruiz):** the converted Abe mB reads a mean 0.39 above ISC-GEM on the 16 events of the domain that have both (median 0.35), and ISC-GEM uses a literature M0 for some of them (1957-11-29: Abe's table M0 gives Mw 7.8, ISC-GEM 7.7, converted mB 7.8; 1959-06-14: 7.2, 7.1, 7.9). The slope 1.6 widens Abe's scatter. Options: keep; take ISC-GEM where it has a direct Mw; correct the single events in A6 from a cited M0. Not decided here. The "−0.2" of untyped values is Engdahl and Villaseñor's correction for catalogues before 1960 and is applied also to the Berkeley and Pasadena values of 1960–1975.
- **Test table, before and after** (this study; the tests use 1976 on, except test 6, so they do not see this change):

| test | 2026-11-13b | 2026-11-13c |
|---|---|---|
| 1 b range over floors 4.7–5.8 (2011 on full / declustered; 1976 on full / declustered) | 0.12 / 0.15; 0.08 / 0.08 | 0.12 / 0.14; 0.08 / 0.08 |
| 2 rate departure, M ≥ 5.5 / M ≥ 5.0 | 13.8 % / 14.2 % | 13.6 % / 14.4 % |
| 3 large events from small ones | 31 of 32; Mw ≥ 7 full 37.3 / 44, declustered 32.4 / 36 | 31 of 32; 37.3 / 44, 32.5 / 36 |
| 4 converted against held-out regional Mw | 16 of 20 | 16 of 20 (same four mb bins) |
| 5 histogram, largest z | 2.1 | 2.1 |
| sensitivity (d) | Centennial first: same passes | ISC-GEM first (the old order): same passes |

  The small differences in the declustered rows come from the declustering windows of the changed events before 1976.
- **Not updated:** `catalog/MAGNITUDES.md` rule 6, `catalog/REPORT_A3-A5.md`, `paper/CATALOG_SECTION_draft.md` and `explore/X4` still describe or use `2026-11-13b`; `locate_check.py` and the X4 classification were not rerun.
- **Proposed line for LEARNINGS:** "The Centennial lists Abe mB for intermediate-depth events and for shallow events without Ms; it is not Mw (Abe 1982: log M0 = 2.4 mB + 10.0). The acceptance tests of A5 use 1976 on and do not see any change before 1976."
- **Reference to add to `REFERENCES.md`:** Abe, K. (1982). Magnitude, seismic moment and apparent stress for major deep earthquakes. J. Phys. Earth 30(4), 321–330. doi:10.4294/jpe1952.30.321 (read).
- Commands (already run; to repeat, from `catalog/`): `python magnitude.py`, `python locate.py`, `python magnitude_check.py`.
- Suggested commit (from the repo root):
  `git add psha_chile8/DECISIONS.md psha_chile8/DATA.md psha_chile8/WORKLOG.md psha_chile8/catalog/PREFERENCES.md psha_chile8/catalog/RULES_LOCATION_MAGNITUDE.md psha_chile8/catalog/magnitude.py psha_chile8/catalog/magnitude_check.py psha_chile8/catalog/locate.py psha_chile8/catalog/tests/test_magnitude.py psha_chile8/catalog/merged psha_chile8/catalog/figs`
  `git commit -m "A5: GCMT line below 5.4 kept; Centennial before ISC-GEM for magnitude before 1976, Abe mB converted (run 2026-11-13c)"`

## 2026-11-13: A6 large events, first pass on the run 2026-11-13c (Claude Code, A6 conversation)

Task `tasks/A6_large_events.md`. 124 tests pass. **Not finished:** every period has its dossiers and source comparison, but literature was read for 103 of the 458 selected events only. PLAN boxes untouched.

- **Selection:** 458 events (111 before 1904, 239 in 1904–1963, 11 in 1964–1975, 97 from 1976): 165 of Mw ≥ 7, 223 of Mw 6–6.99 without depth, the named cases and the M ≥ 6 rows of the review lists.
- **Files:** `catalog/a6.py` (selection, dossiers, tables, figure); `catalog/A6/dossiers.csv` (11975 rows), `literature.csv` (225 literature values with reference and page), `selection.csv`, `counts.csv`, `changes_for_review.csv`, `no_depth.csv`, `REPORT.md`; `catalog/overrides_A6.csv` (71 rows, all `proposed`); `catalog/figs/A6/large_events.png`.
- **Code:** `overrides()` in `magnitude.py`, called as the last step of `magnitude.py` (Mw) and `locate.py` (time, epicentre, depth, nodal planes; existence and class hint as new columns). Only rows with status `accepted` are applied; flag `a6_<property>`. Test `test_a6_corrections_only_accepted_rows`. Rerun of both scripts with the table (no accepted row): `mw`, `locations` and `catalog` of `2026-11-13c` have the same sha256 as before.
- **Read:** Lomnitz (2004) Table 1 in full; Abe (1982) in full; Ruiz and Madariaga (2018) through the frozen table and the R1 notes; the ISC-GEM entries and their magnitude source; by a sub-agent on the web: Kanamori and Rivera (2017, full text), the USGS page of the Drake Passage event, the CSN and NOAA tables for 1878. Comte and Pardo (1991) could not be opened.
- **Not done:** rupture studies and finite-fault products for the events from 1976; Engdahl and Villaseñor's Table 1 row by row; any literature for 355 events, among them almost all of the 223 events of Mw 6–7 without depth. No depth could be proposed for any event.
- **Short table for Pablo** (accept or reject; full reasons in `A6/REPORT.md` section 2):

| event | property | old → new | source |
|---|---|---|---|
| 1543 Tarapacá | Mw | 7.4 → 7.7 | Ruiz and Madariaga (2018), "> 7.7" |
| 1878-01-23 | longitude | −77.0 → −70.3 | CSN table, NOAA database |
| 1916-06-21 (deep, outside the domain) | Mw | 7.8 → 7.1 | ISC-GEM direct |
| 1952-06-11 | Mw | 6.5 → 6.8 | ISC-GEM direct |
| 1959-06-14, 109 km | Mw | 7.9 → 7.2 | Abe (1982) Table 1, moment |
| 1960-06-06 Aysén | Mw | 7.2 → 7.7 | Kanamori and Rivera (2017); Ruiz and Madariaga |
| 1962-02-14 | Mw | 7.7 → 7.1 | ISC-GEM direct |
| 1962-08-03, 113 km | Mw | 7.5 → 6.8 | ISC-GEM direct |
| 1967-03-13 | Mw | 7.1 → 5.7 | ISC-GEM direct (Centennial Berkeley 7.3: one of the two is wrong) |
| 1970-06-15 | Mw | 7.0 → 6.8 | ISC-GEM direct |
| 1974-01-02, 122 km | Mw | 7.3 → 7.0 | ISC-GEM direct |
| 1974-08-18 | Mw | 7.1 → 6.9 | ISC-GEM direct |
| 2010-02-27 08:25 | Mw | 7.0 → 6.3 | ISC-GEM proxy; mb 6.1 (was CSN ML alone) |
| 2011-01-07 04:55, 307 km | Mw | 6.6 → 5.7 | CSN moment magnitude in the ISC Bulletin (was CSN ML) |

  Plus 57 class hints for A7 (55 from Ruiz and Madariaga, 2 from Lomnitz for Magallanes 1949).
- **Patterns, no rule changed** (REPORT section 4): ten of the Mw proposals come from converted Centennial values standing before an ISC-GEM direct Mw (38 such events in the catalogue); `GUC MW` of the ISC Bulletin is not in the reference family (343 converted events have one, 66 differ by 0.5 or more); CSN ML of deep and very large events; legacy WCMT tensors of 2010 before GCMT (4 events); poor Centennial solutions used as epicentres before 1964.
- **Open, large events without a decision:** 1971-06-17 (7.5 against 6.3), 1948-05-11, 1918-05-20, 1934-03-01, 1925-05-15; Papudo 2001 (7.0 against GCMT 6.65); Santiago 1647 class; the 1919-03-02 and 1918-12-04 epicentres; 1604 / 1639 La Serena.
- **Proposed line for DECISIONS:** "Large events: corrections only from cited sources, recorded in `catalog/overrides_A6.csv` and applied as the last step of `magnitude.py` and `locate.py` (rows with status `accepted`)."
- **Proposed line for LEARNINGS:** "A source order by catalogue hides the kind of value: before 1976 a converted Centennial mB or Ms can stand before a direct Mw of ISC-GEM. Order by kind of value first (direct before converted), then by catalogue."
- **References:** Abe (1982) to add; Kanamori and Rivera (2017) and the web pages read by a sub-agent, to be opened once more before citing; † Comte and Pardo (1991), Wyss (1970), Kausel and Campos (1992), Beck et al. (1998) not read.
- **Commands:** to accept a row, set its `status` to `accepted` in `catalog/overrides_A6.csv`, then from `catalog/`: `python magnitude.py`, `python locate.py`, `python a6.py`. To continue A6: add rows to `A6/literature.csv` and `overrides_A6.csv`, rerun `a6.py`.
- **Next for A6:** the five open large events above; Engdahl and Villaseñor Table 1 and Beck et al. (1998) for 1904–1975; rupture studies for the 36 events of Mw ≥ 7 from 1976 (depth and class); then the Mw 6–7 events without depth.
- Suggested commit (from the repo root):
  `git add psha_chile8/catalog/a6.py psha_chile8/catalog/A6 psha_chile8/catalog/overrides_A6.csv psha_chile8/catalog/figs/A6 psha_chile8/catalog/magnitude.py psha_chile8/catalog/locate.py psha_chile8/catalog/tests/test_magnitude.py psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/WORKLOG.md`
  `git commit -m "A6 first pass: dossiers of 458 large events, corrections table and its last-step application, 14 proposed changes and 57 class hints"`

## 2026-11-13: A6, the five open large events (Claude Code, A6 conversation)

Asked by Pablo. 124 tests pass; no code changed except one setting in `a6.py` (`EXTRA`, an event added to the selection). Detail in `catalog/A6/REPORT.md` section 7.

- **Read:** Abe and Kanamori (1979) Table 2 and Astiz and Kanamori (1986) pp. 1617–1620, both on the page images. By a sub-agent: Astiz (1987, thesis), the CaltechDATA transcription of Abe (1981), the CSN table. Not opened (no free copy): Astiz et al. (1988), Abe (1981), Pacheco and Sykes (1992).
- **Result: no seismic moment exists in what was read for any of the five (1971-06-17, 1948-05-11, 1918-05-20, 1934-03-01, 1925-05-15), so no Mw change is proposed for them.** They stay at the converted Centennial values (7.5, 7.5, 7.8, 7.3, 7.1), against ISC-GEM proxies of 6.3–6.9.
- **Proposed** (8 new rows in `overrides_A6.csv`, now 79, all `proposed`): 1934-03-01 depth 120 ± 20 km (depth phases, Astiz and Kanamori 1986) and class hint in-slab; class hint in-slab for 1918-05-20 and 1971-06-17; 1949-04-20 Mw 7.0 → 7.1 (moment 6.0 × 10^26 dyn cm) and in-slab; **1971-05-08 (42.3° S, 157 km) Mw 6.0 → 7.2** (moment 8.0 × 10^26 dyn cm, same paper) and in-slab.
- **To decide (Pablo, S. Ruiz):** depth feeds the mB conversion. Accepting 120 km for 1934 makes the next run convert its mB 7.3 as an intermediate-depth event: Mw 7.6 instead of 7.3. 1918-05-20 and 1939-04-18 are listed at 80 and 100 km by Abe and Kanamori (depths of Gutenberg and Richter) and are converted as shallow because the catalogue has no depth for them; as intermediate-depth events they would be 8.1 and 7.6.
- **Pattern to report:** an intermediate-depth event of 1964–1975 with an ISC-GEM proxy from mb can be far too low (1971-05-08: 6.0 against a measured 7.2). Not searched systematically.
- Counts now: 459 events selected, literature read for 112, 15 Mw proposals, 1 longitude, 1 depth, 62 class hints.
- References to add: Abe and Kanamori (1979), Astiz and Kanamori (1986) (read); † Astiz et al. (1988), Abe (1981), Pacheco and Sykes (1992).
- Commit: add `psha_chile8/catalog/A6 psha_chile8/catalog/overrides_A6.csv psha_chile8/catalog/a6.py psha_chile8/catalog/figs/A6 psha_chile8/WORKLOG.md` to the A6 commit of the entry above.

## 2026-11-13: decisions of 13 Nov applied, run 2026-11-13d (Claude Code)

Asked by Pablo (no brief in `tasks/`): apply the 13 Nov lines of DECISIONS (large events A6, mechanism order, magnitudes before 1976, GUC MW). 124 tests pass. `magnitude.py`, `locate.py`, `magnitude_check.py` and `locate_check.py` were run; `a6.py` was not (its tables and figure are still of `2026-11-13c`). PLAN boxes untouched (A6 literature is not finished).

- **`magnitude.py`:**
  - Before 1976: Ruiz and Madariaga > Centennial Mw > ISC-GEM direct (flag `d`) > Centennial Ms, mB, untyped converted > ISC-GEM proxy (flag `p`, new flag `iscgem_proxy`) > Cabello. Setting `OLD` now lists the four levels.
  - From 1976 a measured Mw goes before Ruiz and Madariaga (28 events; 27 events keep the paper's value, all 1730–1975).
  - `GUC MW` added to `WFAM` (after `CSN web Mw`) and to `REG` (0.3 cross-check). Measured offset to NEIC Mww +0.06 on 125 pairs (sd 0.20; GUC Mwr has 0.14), shift −0.06.
  - **Not asked, needed for rule 1:** the ISC-GEM value now comes from the frozen ISC-GEM v13 table, not from its copy in ComCat. 540 events before 1976 took the ComCat copy, which has no `d` / `p` flag and an older value for 37 of them (11 changes at Mw ≥ 6 in the table below, −0.1 to +0.3).
  - `LOC` left at `2026-11-13b`, so the accepted 1934 depth of 120 km does not enter the mB conversion and 1934-03-01 stays at 7.3, as DECISIONS says ("left as they are"). With `LOC = "2026-11-13d"` it would become 7.6.
- **`locate.py`:** mechanisms GCMT (our file, then its copies in ComCat), then ComCat W-phase, other tensors, nodal planes. 1049 events changed mechanism (619 with strike more than 20° apart); GCMT now gives 2797 of 3016, ComCat 219.
- **`overrides_A6.csv`:** 72 rows `accepted` (63 class hints and the nine listed in DECISIONS), 8 rows `superseded`. Applied: 7 Mw rows in `magnitude.py`, 65 rows in `locate.py` (63 hints, 1878 longitude, 1934 depth). The 63rd hint was added afterwards on Pablo's word: Santiago 1647 in-slab (Ruiz and Madariaga 2018, p. 16; page not re-read here), `locate.py` rerun, only that column changed. The rule gives exactly the proposed value for all eight superseded rows: 1916-06-21 7.1, 1952-06-11 6.8, 1962-02-14 7.1, 1962-08-03 6.8, 1967-03-13 5.7, 1970-06-15 6.8, 1974-01-02 7.0, 1974-08-18 6.9 (all ISC-GEM direct). `old_value` was not edited: for 1959-06-14 the rule alone now gives 7.1 (not 7.9), for 2011-01-07 about 5.6 (GUC MW 5.7 − 0.06).
- **`magnitude_check.py`:** variant (d) is now "ISC-GEM before the Centennial inside each level". **`tests`:** `test_one_mw_per_event` (levels before 1976, measured Mw before the paper from 1976), `test_maule_moment_check` (GCMT first).

### To decide (Pablo)

1. **1967-03-13 is now 5.7 by the rule** (ISC-GEM direct before the converted Centennial Berkeley 7.3). **Decided by Pablo the same day: 1967-03-13 and Papudo 2001 (6.7, GCMT) follow the general rule, no override.**
2. **GUC MW changes the conversion of small events.** 51 of its 352 values are below 4.5 (down to 2.1), so the reference now reaches Mw 2.7 instead of 3.8 and the CSN ML line moved: 42 400 ML events are 0.1 lower (0.02 at ML 4.5), almost all below Mw 4.5. Events of Mw ≥ 4.5: 15 636 → 15 448 (domain 14 234 → 14 054). The split of NEIC mb also changed (by depth → none), 2 472 values moved by 0.1. Option: use GUC MW in the reference only from Mw 4.0 or 4.5. Not changed.
3. **GUC MW against a single other moment magnitude.** The cross-check needs two others. 11 events take a GUC MW more than 0.3 from their only other moment magnitude, the largest 2010-05-05 15:24: GCMT 5.39 → GUC MW 6.0 (list: `review/mw_reference_dropped_2026-11-13d.csv`, rows `GUC MW`, `dropped` False). 18 values were dropped by the check. Option: for GUC MW drop on one other value, or put it last in the family.
4. The priority of the converted scales by σ of this fit puts ISC mb and NEIC mb before CSN ML (0.247, 0.245, 0.247); the `PRIORITY` setting was kept.
5. The acceptance tests run on the rule values before the A6 rows; with them the observed N ≥ 7 from 1976 would be one lower (2010-02-27 08:25).

### Events of Mw ≥ 6 that changed (60, 55 in the domain; `review/mw6_changed_2026-11-13d.csv`)

Before 1904: 1. 1904–1963: 23. 1964–1975: 18. From 1976: 18. Counts at Mw ≥ 6: 999 → 997 (domain 826 → 826); at Mw ≥ 7: 195 → 192 (domain 165 → 163).

| group | n | change |
|---|---|---|
| converted Centennial → ISC-GEM direct | 26 | mean −0.13, −1.4 to +0.6 |
| ISC-GEM, ComCat copy → v13 table | 11 | −0.1 to +0.3 |
| Ruiz and Madariaga → GCMT (from 1976) | 10 | −0.3 to +0.1 |
| A6 rows | 7 | see below |
| converted or GCMT → GUC MW | 3 | −0.5, +0.4, +0.6 |
| converted, relation refitted | 3 | −0.1 |

Those at Mw ≥ 7 before or after:

| date | depth | before | after |
|---|---|---|---|
| 1543 | | 7.4 Cabello | 7.7 A6 |
| 1916-06-21 (outside) | | 7.8 Abe mB | 7.1 ISC-GEM direct |
| 1949-04-20 | 58 | 7.0 Abe mB | 7.1 A6 |
| 1950-08-14 (outside) | 610 | 7.5 Abe mB | 7.1 ISC-GEM direct |
| 1957-11-29 | 159 | 7.8 Abe mB | 7.7 ISC-GEM direct |
| 1959-06-14 | 109 | 7.9 Abe mB | 7.2 A6 |
| 1960-06-06 Aysén | | 7.2 Pacheco and Sykes | 7.7 A6 |
| 1960-11-01 | 20 | 6.8 Abe Ms | 7.4 ISC-GEM direct |
| 1962-02-14 | 41 | 7.7 Abe mB | 7.1 ISC-GEM direct |
| 1962-08-03 | 113 | 7.5 Abe mB | 6.8 ISC-GEM direct |
| 1965-02-23 | 42 | 6.5 Abe Ms | 7.0 ISC-GEM direct |
| 1967-03-13 | 23 | 7.1 Berkeley | 5.7 ISC-GEM direct |
| 1970-06-15 (outside) | 15 | 7.0 USCGS Ms | 6.8 ISC-GEM direct |
| 1971-05-08 | 157 | 6.0 ISC-GEM proxy | 7.2 A6 |
| 1974-01-02 | 122 | 7.3 Abe mB | 7.0 ISC-GEM direct |
| 1974-08-18 | 25 | 7.1 NEIS Ms | 6.9 ISC-GEM direct |
| 1981-10-16 Papudo | 24 | 7.2 R&M | 7.1 GCMT |
| 1983-10-04 Copiapó | 29 | 7.7 R&M | 7.6 GCMT |
| 1985-03-03 Valparaíso | 50 | 8.0 R&M | 7.9 GCMT |
| 1987-03-05 Antofagasta | 40 | 7.6 R&M | 7.5 GCMT |
| 2001-04-09 Papudo | 11 | 7.0 R&M | 6.7 GCMT |
| 2007-11-14 Tocopilla | 42 | 7.8 R&M | 7.7 GCMT |
| 2010-02-27 08:25 | 47 | 7.0 CSN ML | 6.3 A6 |
| 2012-03-25 Constitución | 50 | 7.2 R&M | 7.1 GCMT |
| 2014-04-01 Iquique | 30 | 8.2 R&M | 8.1 GCMT |

Other A6 row: 2011-01-07 04:55 (307 km) 6.6 → 5.7. Location: 1878-01-23 longitude −77.0 → −70.3; 1934-03-01 depth unknown → 120 ± 20 km. No other epicentre or depth changed.

### Acceptance tests 1 to 5, before and after (`mw_tests`, `mw_sensitivity`)

| test | 2026-11-13c | 2026-11-13d |
|---|---|---|
| 1 b against the floor | 4 of 4 (b range 0.12 / 0.14 / 0.08 / 0.08) | 4 of 4 (0.11 / 0.14 / 0.08 / 0.08) |
| 2 rates in time | pass (departure 13.6 % at 5.5, 14.4 % at 5.0) | pass (13.3 %, 13.9 %) |
| 3 large events | 31 of 32; N ≥ 7 from 5.0: 37.3 / 44 | 31 of 32; 38.5 / 43 |
| 4 against the regional Mw | 16 of 20 | 15 of 20 |
| 5 histogram | 4 of 4 (largest \|z\| 2.1) | 4 of 4 (1.8) |

Test 3 misses the same case (shallow crustal, declustered, N ≥ 7 from 5.3: 0.6 predicted, band 1.1–10.2). Test 4: the four mb bins fail as before (ISC mb +0.11 / +0.13, NEIC mb +0.17 / +0.14); new miss SJA ML at 5.0–5.25, +0.101 against the limit 0.1. `locate_check.py`: tables and figures rewritten for `2026-11-13d`, not compared line by line with `2026-11-13b` (the last run it was made for).

### Events of Mw ≥ 7 (192, 163 in the domain; all in `review/mw7_2026-11-13d.csv`)

Before 1904 (61, 52 in the domain): 52 Cabello et al., 8 Ruiz and Madariaga (1730, 1751, 1819, 1837, 1859, 1868, 1877, 1880), 1 A6 (1543). From 1904 (131, 111 in the domain): GCMT 41, converted Centennial 38 (Abe mB 30, Ms 8), Centennial Mw of Pacheco and Sykes 19, Ruiz and Madariaga 18, ISC-GEM direct 8, A6 4, ISC-GEM proxy 2, converted ISC MS 1 (2001-06-23 23:10, aftershock of Arequipa, outside the domain).

| date | Mw | source | depth (km) | in the domain |
|---|---|---|---|---|
| 1904-03-19 06:27 | 7.0 | Centennial AN2 Ms 7, converted |  | yes |
| 1906-08-17 00:40 | 8.2 | Ruiz and Madariaga (2018) |  | yes |
| 1906-08-30 02:38 | 7.1 | Centennial P&S Mw |  | yes |
| 1906-12-26 05:53 | 7.0 | Centennial AN2 Ms 7, converted |  | yes |
| 1909-05-17 08:02 | 7.1 | Centennial ABE1 mB 7, converted |  | yes |
| 1909-06-08 05:46 | 7.0 | Ruiz and Madariaga (2018) |  | yes |
| 1910-09-06 20:03 | 7.1 | Centennial P&S Mw |  | yes |
| 1910-10-04 23:00 | 7.5 | Centennial ABE1 mB 7.2, converted |  | yes |
| 1911-09-15 13:09 | 7.1 | Centennial P&S Mw |  | yes |
| 1912-12-07 22:46 | 7.6 | Centennial ABE1 mB 7.3, converted |  | no |
| 1913-07-28 05:39 | 7.0 | Centennial AN1 Ms 7, converted |  | yes |
| 1913-08-06 22:14 | 7.8 | Centennial P&S Mw |  | no |
| 1914-01-30 03:36 | 7.5 | Centennial P&S Mw |  | yes |
| 1914-02-26 04:58 | 7.5 | Centennial ABE1 mB 7.2, converted |  | no |
| 1915-06-06 21:29 | 7.6 | Centennial ABE1 mB 7.3, converted | 160 | yes |
| 1916-06-21 21:32 | 7.1 | ISC-GEM direct |  | no |
| 1918-05-20 17:55 | 7.8 | Centennial ABE1 mB 7.6, converted |  | yes |
| 1918-12-04 11:47 | 7.8 | Ruiz and Madariaga (2018) |  | yes |
| 1919-03-02 03:26 | 7.2 | Centennial P&S Mw |  | yes |
| 1919-03-02 11:45 | 7.1 | Centennial P&S Mw |  | yes |
| 1920-08-20 16:15 | 7.0 | ISC-GEM proxy |  | yes |
| 1920-12-10 04:25 | 7.2 | Centennial P&S Mw |  | yes |
| 1921-10-20 06:03 | 7.5 | Centennial ABE1 mB 7.2, converted | 114 | yes |
| 1922-01-06 14:10 | 7.1 | Centennial P&S Mw |  | yes |
| 1922-03-28 03:58 | 7.3 | Centennial ABE1 mB 7.1, converted | 136 | yes |
| 1922-10-11 14:50 | 7.2 | Centennial P&S Mw |  | no |
| 1922-11-07 23:00 | 7.1 | Centennial ABE1 Ms 7.1, converted |  | yes |
| 1922-11-11 04:32 | 8.5 | Ruiz and Madariaga (2018) |  | yes |
| 1925-05-15 11:57 | 7.1 | Centennial ABE1 Ms 7.1, converted |  | yes |
| 1926-04-28 11:13 | 7.3 | Centennial ABE1 mB 7.1, converted |  | yes |
| 1927-04-14 06:23 | 7.2 | Ruiz and Madariaga (2018) |  | yes |
| 1927-11-21 23:12 | 7.1 | Centennial P&S Mw |  | yes |
| 1927-11-26 12:54 | 7.1 | Centennial ABE1 mB 7, converted | 179 | yes |
| 1928-12-01 04:06 | 7.7 | Ruiz and Madariaga (2018) |  | yes |
| 1928-12-02 04:20 | 7.2 | ISC-GEM proxy |  | yes |
| 1929-10-19 10:12 | 7.8 | Centennial ABE1 mB 7.4, converted |  | yes |
| 1931-03-18 08:02 | 7.1 | Centennial ABE1 Ms 7.1, converted |  | yes |
| 1933-02-23 08:09 | 7.2 | Centennial P&S Mw |  | yes |
| 1933-10-25 23:28 | 7.1 | Centennial ABE1 mB 7, converted | 206 | yes |
| 1934-03-01 21:45 | 7.3 | Centennial ABE1 mB 7.3, converted | 120 | yes |
| 1936-07-13 11:12 | 7.0 | Ruiz and Madariaga (2018) |  | yes |
| 1939-01-25 03:32 | 7.8 | Ruiz and Madariaga (2018) |  | yes |
| 1939-04-18 06:22 | 7.3 | Centennial ABE1 mB 7.3, converted |  | yes |
| 1940-10-04 07:54 | 7.0 | Centennial ABE1 mB 7.1, converted | 24 | yes |
| 1940-10-11 18:41 | 7.0 | Centennial ABE1 Ms 7, converted |  | yes |
| 1941-04-03 15:21 | 7.5 | Centennial ABE1 mB 7.2, converted | 150 | yes |
| 1943-03-14 18:38 | 7.3 | Centennial ABE1 mB 7.1, converted | 120 | yes |
| 1943-04-06 16:07 | 7.9 | Ruiz and Madariaga (2018) |  | yes |
| 1943-12-01 10:34 | 7.3 | Centennial ABE1 mB 7.1, converted | 114 | yes |
| 1944-01-15 23:49 | 7.1 | Centennial P&S Mw | 28 | yes |
| 1945-09-13 11:17 | 7.1 | Centennial ABE1 mB 7, converted | 92 | yes |
| 1946-08-02 19:18 | 7.1 | Centennial ABE1 Ms 7.1, converted | 39 | yes |
| 1946-08-28 22:28 | 7.3 | Centennial ABE1 mB 7.1, converted | 574 | no |
| 1947-01-29 08:17 | 7.1 | Centennial ABE1 mB 7, converted | 566 | no |
| 1948-05-11 08:55 | 7.5 | Centennial ABE1 mB 7.4, converted | 59 | yes |
| 1948-07-20 11:02 | 7.0 | Centennial ABE1 mB 7.1, converted | 30 | no |
| 1949-04-20 03:29 | 7.1 | A6: Astiz and Kanamori (1986) | 58 | yes |
| 1949-04-25 13:55 | 7.5 | Centennial ABE1 mB 7.2, converted | 101 | yes |
| 1949-12-17 06:53 | 7.8 | Centennial P&S Mw |  | yes |
| 1949-12-17 15:07 | 7.8 | Centennial P&S Mw |  | yes |
| 1950-08-14 22:51 | 7.1 | ISC-GEM direct | 610 | no |
| 1950-12-09 21:38 | 8.0 | Ruiz and Madariaga (2018) | 114 | yes |
| 1952-09-21 02:30 | 7.3 | Centennial ABE1 mB 7.1, converted | 268 | yes |
| 1953-05-06 17:16 | 7.5 | Centennial P&S Mw | 66 | yes |
| 1953-12-07 02:05 | 7.5 | Centennial ABE1 mB 7.2, converted | 106 | yes |
| 1957-11-29 22:19 | 7.7 | ISC-GEM direct | 159 | yes |
| 1958-01-15 19:14 | 7.1 | Centennial ABE1 mB 7, converted | 69 | no |
| 1959-06-14 00:11 | 7.2 | A6: Abe (1982) | 109 | yes |
| 1960-01-13 15:40 | 7.9 | Centennial ABE1 mB 7.5, converted | 130 | no |
| 1960-05-21 10:02 | 8.1 | Ruiz and Madariaga (2018) | 12 | yes |
| 1960-05-22 18:56 | 7.8 | Ruiz and Madariaga (2018) |  | yes |
| 1960-05-22 19:11 | 9.5 | Ruiz and Madariaga (2018) | 25 | yes |
| 1960-06-06 05:55 | 7.7 | A6: Kanamori and Rivera (2017) |  | yes |
| 1960-06-20 02:01 | 7.0 | Centennial P&S Mw | 25 | yes |
| 1960-06-20 12:59 | 7.1 | Centennial P&S Mw | 25 | yes |
| 1960-11-01 08:45 | 7.4 | ISC-GEM direct | 20 | yes |
| 1960-12-02 09:10 | 7.2 | Centennial P&S Mw | 14 | yes |
| 1962-02-14 06:36 | 7.1 | ISC-GEM direct | 41 | yes |
| 1962-12-08 21:27 | 7.2 | ISC-GEM direct | 589 | no |
| 1965-02-23 22:11 | 7.0 | ISC-GEM direct | 42 | yes |
| 1965-03-28 16:33 | 7.4 | Ruiz and Madariaga (2018) | 68 | yes |
| 1966-12-28 08:18 | 7.7 | Ruiz and Madariaga (2018) | 20 | yes |
| 1967-12-21 02:25 | 7.4 | Ruiz and Madariaga (2018) | 45 | yes |
| 1967-12-27 09:17 | 7.1 | Centennial ABE1 mB 7, converted | 116 | yes |
| 1971-05-08 00:49 | 7.2 | A6: Astiz and Kanamori (1986) | 157 | yes |
| 1971-06-17 21:00 | 7.5 | Centennial ABE1 mB 7.2, converted | 90 | yes |
| 1971-07-09 03:03 | 7.8 | Ruiz and Madariaga (2018) | 61 | yes |
| 1974-01-02 10:42 | 7.0 | ISC-GEM direct | 122 | yes |
| 1975-05-10 14:27 | 7.7 | Ruiz and Madariaga (2018) | 24 | yes |
| 1976-11-30 00:41 | 7.5 | GCMT | 104 | yes |
| 1977-11-23 09:26 | 7.5 | GCMT | 21 | yes |
| 1979-02-16 10:08 | 7.1 | GCMT | 54 | no |
| 1981-10-16 03:25 | 7.1 | GCMT | 24 | yes |
| 1983-10-04 18:52 | 7.6 | GCMT | 29 | yes |
| 1985-03-03 22:47 | 7.9 | GCMT | 50 | yes |
| 1985-03-04 00:32 | 7.4 | GCMT | 41 | yes |
| 1985-04-09 01:56 | 7.1 | GCMT | 38 | yes |
| 1987-03-05 09:17 | 7.5 | GCMT | 40 | yes |
| 1987-08-08 15:48 | 7.2 | GCMT | 70 | yes |
| 1988-01-19 07:30 | 7.0 | GCMT | 28 | yes |
| 1988-02-05 14:01 | 7.2 | GCMT | 35 | yes |
| 1988-04-12 23:19 | 7.1 | GCMT | 32 | yes |
| 1991-06-23 21:22 | 7.2 | GCMT | 564 | no |
| 1993-05-24 23:51 | 7.0 | GCMT | 220 | yes |
| 1995-07-30 05:11 | 8.0 | GCMT | 33 | yes |
| 1997-01-23 02:15 | 7.1 | GCMT | 271 | yes |
| 1997-10-15 01:03 | 7.1 | GCMT | 60 | yes |
| 1998-01-30 12:16 | 7.0 | GCMT | 42 | yes |
| 2000-05-12 18:43 | 7.2 | GCMT | 225 | yes |
| 2001-06-23 20:33 | 8.4 | GCMT | 32 | no |
| 2001-06-23 23:10 | 7.1 | ISC MS 6.97, converted | 25 | no |
| 2001-07-07 09:38 | 7.6 | GCMT | 25 | yes |
| 2005-06-13 22:44 | 7.8 | GCMT | 105 | yes |
| 2007-11-14 15:40 | 7.7 | GCMT | 42 | yes |
| 2010-02-27 06:34 | 8.8 | GCMT | 28 | yes |
| 2010-02-27 08:01 | 7.4 | GCMT | 42 | yes |
| 2010-03-11 14:55 | 7.0 | GCMT | 23 | yes |
| 2011-01-01 09:56 | 7.0 | GCMT | 583 | no |
| 2011-01-02 20:20 | 7.1 | GCMT | 3 | yes |
| 2012-03-25 22:37 | 7.1 | GCMT | 50 | yes |
| 2013-09-25 16:42 | 7.0 | GCMT | 63 | no |
| 2014-04-01 23:46 | 8.1 | GCMT | 30 | yes |
| 2014-04-01 23:58 | 7.0 | GCMT | 19 | yes |
| 2014-04-03 02:43 | 7.7 | GCMT | 30 | yes |
| 2015-09-16 22:54 | 8.3 | GCMT | 25 | yes |
| 2015-09-16 23:18 | 7.1 | GCMT | 5 | yes |
| 2016-12-25 14:22 | 7.6 | GCMT | 35 | yes |
| 2018-01-14 09:18 | 7.1 | GCMT | 40 | no |
| 2024-06-28 05:36 | 7.1 | GCMT | 20 | no |
| 2024-07-19 01:50 | 7.3 | GCMT | 124 | yes |
| 2025-05-02 12:58 | 7.5 | GCMT |  | yes |

- **Not updated:** `catalog/MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md`, `PREFERENCES.md`, `REPORT_A3-A5.md`, `A6/REPORT.md`, `paper/CATALOG_SECTION_draft.md` and `explore/X4` still describe earlier runs.
- **Proposed lines for DECISIONS:** "ISC-GEM magnitudes are read from the frozen ISC-GEM table, not from its copy in ComCat (13 Nov)." "1967-03-13 (5.7, ISC-GEM direct) and Papudo 2001 (6.7, GCMT) follow the general rule; Santiago 1647 is in-slab (Ruiz and Madariaga 2018, p. 16) (13 Nov)", replacing the two open items of the A6 line. Lines for points 2 and 3 above once decided.
- Commands (already run; to repeat, from `catalog/`): `python magnitude.py`, `python locate.py`, `python magnitude_check.py`, `python locate_check.py`; `pytest` from `psha_chile8/`. To refresh the A6 tables: set `RUN = "2026-11-13d"` in `a6.py` and run it.
- Suggested commit (from the repo root):
  `git add psha_chile8/DATA.md psha_chile8/WORKLOG.md psha_chile8/catalog/magnitude.py psha_chile8/catalog/magnitude_check.py psha_chile8/catalog/locate.py psha_chile8/catalog/overrides_A6.csv psha_chile8/catalog/tests psha_chile8/catalog/merged psha_chile8/catalog/figs`
  `git commit -m "Decisions of 13 Nov applied: moment-based magnitudes first before 1976, measured Mw before Ruiz and Madariaga from 1976, GUC MW in the reference, GCMT mechanisms first, A6 rows accepted (run 2026-11-13d)"`

## 2026-11-13: A7, tectonic classification with class weights; step 0 rerun (runs 2026-11-13e and 2026-11-13f) (Claude Code)

Brief `tasks/A7_classification.md`. Everything was run in full. 146 tests pass (`pytest` from `psha_chile8/`). Report: `catalog/CLASSIFICATION.md`. PLAN: A7 box left for Pablo.

### Step 0: GUC MW last, fitting floor (run `2026-11-13e`)

- **`magnitude.py`:** `GUC MW` is out of `WFAM` and is the new setting `LAST`: its own offset to NEIC Mww is still measured (+0.06, sd 0.20, 125 pairs), but it does not enter the GCMT line or the relations, and as an event Mw it is taken only where no other measured moment magnitude exists, GCMT included (107 events, 153 before). The 0.3 cross-check stays. New setting `FIT_MIN = 4.0`: relations are fitted on pairs with reference Mw ≥ 4.0. The offsets already used pairs from 4.5 on (`BINS`), so the floor changes nothing there. New table `relations_floor_2026-11-13e.csv`. `locate.py`: only `RUN` and `MW`.
- **Mw ≥ 4.5 in the domain:** 14 279 (`2026-11-13c` 14 234, `2026-11-13d` 14 054); all events 15 687 (15 636, 15 448). 47 681 events changed by 0.1 against `d`, 47 495 of them upward and nearly all below 4.5: the CSN ML line is back where it was before GUC MW entered the reference.
- **The floor itself does almost nothing** (converted Mw at native 4.5 / 5.0 / 5.5, with and without it): CSN ML shallow 4.546 / 5.073 / 5.600 against 4.542 / 5.072 / 5.602; ISC mb shallow 4.397 / 5.044 / 5.691 against 4.390 / 5.042 / 5.695; ISC mb deep, ISC MS, SJA ML within 0.006; the NEIC surface-wave scales have no pair below 4.0. One change of form: NEIC mb is a single hinge with the floor (4.363 / 4.997 / 5.632) and split by depth without it (deep 4.416 / 5.009 / 5.601, shallow 4.305 / 4.984 / 5.663). The effect of step 0 is the removal of GUC MW from the fit, not the floor.
- **Five tests** (`d` → `e`): 1: 4 of 4 → 4 of 4 (b range 0.12 / 0.14 / 0.08 / 0.08). 2: pass → pass (departure 14.1 % at 5.5 and 5.0). **3: 31 of 32 → 30 of 32**: new miss "all events, full, fit from 5.0, N 6.5–7": 87.8 predicted against the band 88.6–130.4 (observed 108); N ≥ 7 from 5.0 is 36.9 / 43. The old miss (shallow crustal, declustered) stays. 4: 15 of 20 → 16 of 20 (SJA ML back inside; the four mb bins fail as before). 5: 4 of 4 (largest |z| 2.2).
- **Events of Mw ≥ 6 that changed** (8, `review/mw6_changed_2026-11-13e.csv`): 2010-05-05 15:24 6.0 (GUC MW) → 5.4 (GCMT); seven converted values by ± 0.1 from the refitted relations (1977-11-23 6.5 → 6.6, 2010-02-27 07:37 6.4 → 6.5, 2010-02-27 10:30 6.2 → 6.1, 2010-02-27 17:24 6.3 → 6.2, 2025-05-02 13:09 6.0 → 5.9, and outside the domain 2001-06-23 23:10 7.1 → 7.0, 2025-07-04 6.3 → 6.2). Mw ≥ 7 in the domain: 163, unchanged.
- Not updated: `catalog/MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md`, the module text at the top of `magnitude.py`, `locate_check.py` tables (not rerun), `a6.py` tables.

### Classification (run `2026-11-13f`)

- **Code:** `catalog/classify.py` (geometry, weights, sub-classes, assigned depths; settings at the top), `catalog/classify_check.py` (the seven checks, five figures), `catalog/tests/test_classify.py` (20 tests: the eleven of the brief and nine more). `palette.py`: `CLASS` with one display name and colour per class. Nothing imported from `explore/`.
- **Counts (Mw ≥ 4.5 in the domain, summed weights):** interface 3 671.8 (142 of it Antarctic), in-slab 8 548.8 (shallow 2 106.4, intermediate 5 537.4, Jujuy nest 905), crustal 1 545.4 (forearc 937.2, arc 221.6, backarc 309.6, Patagonia 77), outer rise 509, unclassified 4. At Mw ≥ 7 (163): 62.7 / 71.6 / 20.7 / 8.
- **Split events: 4 445 of 14 279** (3 153 near the band, 1 292 without depth); 772 of 1 943 at Mw ≥ 5.5; 67 of 163 at Mw ≥ 7. This is not "most events at weight 1" for the shallow slab: 58 % of the events with a depth there are split.
- **Band measurement: `unc` holds as W.** Thrusts on the contact with calibrated or depth-phase depths (257): median 3.4 km below the surface, robust sd 6.6 km, 86 % within `unc` (median 12 km), 98 % within `unc` + σ. All depths (979): +2.1 km, sd 8.0 km, 78 % and 94 %. Other mechanisms: median 10 km below, 42 % inside the band.
- **Why so many are split.** An event on the surface has an interface weight of 2Φ(W/σ) − 1; with W ≈ 12 km and σ = 10 km this is 0.77, under the 0.8 line. 53 % of the events over the shallow slab have W < 1.28 σ. The σ of A4 (floors of 5 and 10 km) is larger than the scatter of the thrust events about the surface (6.6–8.0 km, Slab2's own error included). Maule 2010 is 1.4 km from the surface and gets 0.79. Not tuned; variants: hardening 0.7 → 3 111 split, W = 15 km → 3 117, W = 20 km → 2 460.
- **Sensitivity of the interface total:** W 10 / 15 / 20 km −12 / +23 / +41 %; hardening 0.7 / 0.9 / none +6.6 / −0.2 / −0.5 %; interface to 60 km +4.7 %; mechanisms not used +4.1 % (+11.5 % at Mw ≥ 5.5); events without depth left out −14 % (first written as −17 %, a number of the run before the depth error was cut at the ground; corrected the same day, as the row in CLASSIFICATION.md section 7).
- **Jujuy nest:** the circle encloses the cluster (95 % within 0.65°) and nothing is below 260 km, but the upper limit of 170 km cuts it: 149 events (3 of Mw ≥ 5.5) at 150–170 km inside the circle are intermediate in-slab. Limits not changed.
- **Slab2 check:** `dep` is the surface (9.4 km on the trench line, not about 5; deepens landward; thrusts sit on it), `thk` the thickness (median 79 km), `unc` 10 km above 20 km, 12.6 km at 20–50 km, 25–33 km deeper. The USGS data release text was not opened.

### Done differently from the brief, or decided without asking

1. **Depth error cut at the ground** (normal renormalised to depth ≥ 0). Without it shallow events over a shallow slab were half crustal from probability at negative depths (interface total 3 554 → 3 672).
2. **Mechanisms "both ways" and "only to exclude" are the same rule under R3 as written** (thrust and no mechanism allow the same classes). The baseline excludes only. I added a variant that is not in the brief: a thrust on the contact is interface with weight 1 (interface +10 %, +26 % at Mw ≥ 5.5).
3. **Antarctic interface takes every event that meets the position rule with weight 1** (142; 97 without depth), which would otherwise be crustal Patagonia (77 left). No slab model there to weigh them.
4. "Not deeper than 50 km" is read on the catalogue depth. Rejected depths are those of the source records of A4, one per source. Shares from events east of the trench with a slab, from 1976, Mw ≥ 4.5. In-slab assigned depth at 0.30 of the thickness below the top (psha_chile6–7).
5. The classified catalogue has its own date (`2026-11-13f`) so that the `2026-11-13e` files of `locate.py` are not overwritten.
6. Added, not asked: `review/class_thrust_not_interface_` (thrusts of Mw ≥ 6.5 with interface weight under 0.5).

### For Pablo

- **Wrong against the literature (rules alone):** Copiapó 1918 (outer rise: epicentre west of the trench), La Ligua 1971 (in-slab: slab top 55.6 km), Valparaíso 1985 (in-slab: 49.6 ± 5 km, 21 km below the surface). Split: Concepción 1960, Valdivia 1960, Taltal 1966, Copiapó 1983, Maule 2010, Pichilemu 2010 14:55, Arauco 2011, Iquique 2014 with its foreshock and aftershock, Chiloé 2016, Valparaíso 2017. Right 30, no depth 18. All carry the literature class.
- **Mw ≥ 7 not at weight 1 (67):** 54 without depth (36 before 1904, 18 of 1904–1940: 1904-03-19, 1906-08-30, 1906-12-26, 1909-06-08, 1910-09-06, 1914-01-30, 1919-03-02 03:26, 1920-08-20, 1920-12-10, 1925-05-15, 1926-04-28, 1928-12-02, 1929-10-19, 1931-03-18, 1933-02-23, 1936-07-13, 1939-04-18, 1940-10-11) and 13 near the band (1940-10-04, 1946-08-02, 1953-05-06, 1960-06-20 twice, 1960-12-02, 1962-02-14, 1965-02-23, 1988-01-19, 1988-04-12, 2001-07-07, 2014-04-01 23:58, 2015-09-16 23:18). Table with weights in CLASSIFICATION.md section 6.
- **Thrusts classified crustal with weight 1:** Illapel aftershocks of 2015-09-17 04:10 and 2015-09-21, and 2007-11-15, on Potin depths of 0–2.4 km (2015-09-16 23:18 Mw 7.1 and 2015-09-17 03:55 are 0.75–0.78 crustal). Fix, if any, is a cited class hint.
- **Six historical events (1687–1870, Mw 7.0–7.5) are in-slab with weight 1** because Cabello's depths for them are 70 km or more. A historical depth is hardly a "deep default of an agency"; say if Cabello's depths should not count for this rule.
- **Bins that borrowed:** slab top 50–100 km and > 100 km at 38–46° S, Mw ≥ 5.5 (0 and 7 events; both take the lower magnitude range).
- **To decide:** (a) accept a third of the catalogue split, or change one of hardening, W, or the depth σ of A4 (the measurement supports a σ below 10 km offshore); (b) the Antarctic interface rule against crustal Patagonia; (c) the nest's upper limit (170 or 150 km); (d) whether a thrust on the contact should add to the interface.

### Proposed lines for DECISIONS

- Classification: "Run 2026-11-13f. The Slab2 depth uncertainty is confirmed as the interface band: 86 % of thrust events with calibrated or depth-phase depths lie within it, 98 % within it plus their σ (13 Nov)."
- Classification: "The depth error is a normal distribution cut at the ground surface (13 Nov)."
- Classification: "Mechanisms only exclude: a mechanism that is not a thrust on the plate contact rules the interface out; a thrust adds nothing beyond what the depth gives (13 Nov)." (or the opposite, point (d)).
- Magnitudes: replace "Conversion relations are fitted only on pairs with a reference Mw ≥ 4.0" by the same sentence plus "(run 2026-11-13e; the floor moves no relation by more than 0.01 at 4.5–5.5)".
- LEARNINGS, Catalog: "A class weight from depth and σ cannot reach 0.8 for an event on the slab surface unless the band is at least 1.28 σ wide; with σ floors of 10 km and a band of 12 km a third of the catalogue is split (A7)."

### Commands (already run; to repeat, from `catalog/`)

`python magnitude.py`, `python locate.py`, `python magnitude_check.py` (step 0, minutes); `python classify.py` (15 s), `python classify_check.py` (a few minutes; not timed); `pytest` from `psha_chile8/`.

### Suggested commit (from the repo root)

`git add psha_chile8/WORKLOG.md psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/palette.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/locate.py psha_chile8/catalog/classify.py psha_chile8/catalog/classify_check.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/tests psha_chile8/catalog/merged psha_chile8/catalog/figs`
`git commit -m "A7: tectonic classes as weights (run 2026-11-13f); GUC MW last and fitting floor at Mw 4.0 (run 2026-11-13e)"`

## 2026-11-13: A7 follow-up, the depth σ against the scatter of the thrust events (Claude Code)

Asked by Pablo after the A7 report ("revisit depth σ"). Analysis only: `locate.py`, the catalogue and the classes of run `2026-11-13f` are unchanged. New in `classify_check.py`: `sigma_check()`, tables `merged/class_sigma_2026-11-13f.csv` and `class_sigma_variants_2026-11-13f.csv`; `classify_check.py` rerun, its other tables identical. Report: `catalog/CLASSIFICATION.md` section 11.

- **Measured** (scatter of the thrusts on the contact about the Slab2 surface, an upper bound of σ): offshore 8.9 km against the σ of 10 km; ISC-EHB L1 5.6 km offshore and onshore (σ 10 and 5); Potin offshore 7.1 km (σ 10.4, its own tabled value); GCCEL offshore 7.8 km; ISC-EHB L2 9.3 km; ISC 11.7 km offshore and 10.6 onshore (σ 10 and 6.8); onshore all sources 6.8 km (σ 5). CSN web depths are 7–11 km below the surface, GCCEL offshore 6 km below: a bias, not a σ.
- **Effect on the classes** (Mw ≥ 4.5 in the domain): no offshore floor → 3 695 split (4 445 now), interface 3 829 (3 672); offshore floor 7.5 km → 3 962; σ set to the measured scatter per source → 3 729. With hardening 0.7 as well: 2 722–2 860. Thrusts on the contact at interface weight 1: 249 now, 407 without the offshore floor, but those in another class with weight 1 rise from 65 to 83.
- **Reading:** σ explains about a sixth of the split events. The rest comes from band edges at ± 12 km lying inside the scatter of the interface events (7–9 km): an event within 0.84 σ of an edge is split whatever σ is.
- **Not changed, conflicts with DECISIONS** ("σ at least 5 km, 10 km offshore, 20 km before 1964", 13 Nov). Options in section 11; I would drop the offshore floor for ISC-EHB L1 and GCCEL depths only, and decide the hardening separately.
- **Proposed line for DECISIONS (if (b) is taken):** "Depth σ: the 10 km offshore floor does not apply to ISC-EHB L1 and GCCEL depths, whose thrust events scatter 5.6–7.8 km about the Slab2 surface offshore (A7, 13 Nov)."
- **Proposed line for LEARNINGS:** "Reducing the depth σ does not remove split classes: a hard band inside a continuous depth distribution splits every event within 0.84 σ of its edges (A7)."
- Commands (already run): `python classify_check.py` from `catalog/`. Commit: add `psha_chile8/catalog/classify_check.py`, `catalog/CLASSIFICATION.md`, `catalog/merged`, `WORKLOG.md` to the A7 commit above.

## 2026-11-13: depth σ over the shallow slab from the thrust scatter; reruns 2026-11-13g (locate) and 2026-11-13h (classes) (Claude Code)

Asked by Pablo. 146 tests pass. Report: `catalog/CLASSIFICATION.md` section 12 (sections 1–11 still describe run `f`; a note at the top says so).

- **`locate.py`:** `SIG_OFF` removed. New settings `SIG_TOP = 50`, `SIG_BEST = ["gccel", "ehb1"]`, `SIG_SLAB = (6.6, 8.5)`: where the Slab2 top at the epicentre is ≤ 50 km, σ = 6.6 km for GCCEL and ISC-EHB L1 depths and 8.5 km for the others, in place of the tabled value, onshore and offshore; elsewhere the tabled σ, at least 5 km; 20 km before 1964. The Slab2 top comes from `classify.slab_at` (imported inside the function). Flag `sigma_offshore_floor` → `sigma_slab_scatter`. The two values are settings, not recomputed in the run; `classify_check.py` prints the measured scatter every time (6.58 and 8.48 km before and after).
- **Read as asked, with one consequence to check:** "events over the shallow slab" includes onshore events, so 2 222 events (Mw ≥ 4.5) went from about 5 km to 8.5 or 6.6 km, while 3 518 offshore went down from 10 km.
- **`classify.py`:** only `RUN = "2026-11-13h"`, `CAT = "2026-11-13g"`. Band width and 0.8 untouched. `classify_check.py`: the σ variants renamed (tabled σ; tabled σ with the old 10 km floor; scatter per source and offshore flag).
- **Split events:** 4 445 → 3 955 (near the band 3 153 → 2 663; 772 → 710 at Mw ≥ 5.5; 67 → 66 at Mw ≥ 7).
- **Thrusts on the contact inside the band (762):** interface with weight 1 241 → 374; offshore 5 → 149, onshore 236 → 225; GCCEL and ISC-EHB L1 78 → 142 of 217. 388 are still split.
- **Rules alone:** Maule 2010 interface 1 (was 0.79); Iquique 2014 split 0.69 / 0.30 / 0.01 (was 0.58 / 0.36 / 0.05); Valparaíso 1985 in-slab 1, unchanged (21 km below the surface, W 12.4 km).
- **Class totals:** interface 3 671.8 → 3 843.5, in-slab 8 548.8 → 8 448.5, crustal 1 545.4 → 1 474.0, outer rise 509, unclassified 4.
- **Side effects:** Valparaíso 2017 is now in-slab with weight 1 by the rules (was split); La Ligua 1965, Arauco 1975 and Constitución 2012 are newly split (onshore σ up); 2015-09-16 23:18 Mw 7.1 is now crustal with weight 1 (Potin depth 5 km). Literature events: right 29, wrong 4, split 12, no depth 18.
- **Correction of the earlier A7 entry:** the sensitivity row "events without depth left out" carried numbers of an earlier pass (interface 3 057.3); the file says 3 157.7 / 7 964.3 / 1 352.0. Fixed in CLASSIFICATION.md section 7.
- **Not rerun:** `locate_check.py` (its σ-dependent tables are of `2026-11-13d`), `magnitude.py` (reads depths of `2026-11-13b`, unaffected). Not updated: `RULES_LOCATION_MAGNITUDE.md` row D7, `PREFERENCES.md`, `REPORT_A3-A5.md`.
- **Open for Pablo:** whether the measured σ should apply onshore too. Applied offshore only it would keep the onshore thrusts as they were (236 at weight 1) and give fewer split events; the variant "tabled σ, minimum 5 km" (3 695 split) is the lower bound of that.

### Proposed line for DECISIONS (Catalog, replacing the σ sentence of the depth line of 13 Nov)

"Depth σ: where the Slab2 top at the epicentre is ≤ 50 km, σ is the robust scatter of thrust events on the plate contact about the Slab2 surface, 6.6 km for GCCEL and ISC-EHB L1 depths and 8.5 km for the other sources (979 events, run 2026-11-13f); an upper bound, since it contains the error of Slab2. Elsewhere the σ of the comparisons between catalogues, at least 5 km; 20 km before 1964. The 10 km offshore floor is dropped (13 Nov, run 2026-11-13g)."
And in Superseded: "Depth σ floor of 10 km offshore (13 Nov) → measured scatter over the shallow slab (13 Nov, A7: the floor left a third of the catalogue split between classes)."

### Commands (already run; to repeat, from `catalog/`)

`python locate.py`, `python classify.py`, `python classify_check.py`; `pytest` from `psha_chile8/`.

### Suggested commit (from the repo root; replaces the A7 commit line above if that is not yet committed)

`git add psha_chile8/WORKLOG.md psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/palette.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/locate.py psha_chile8/catalog/classify.py psha_chile8/catalog/classify_check.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/tests psha_chile8/catalog/merged psha_chile8/catalog/figs`
`git commit -m "A7: tectonic classes as weights (run 2026-11-13h); depth σ over the shallow slab from the scatter of thrust events (run 2026-11-13g); GUC MW last and fitting floor at Mw 4.0 (run 2026-11-13e)"`

## 2026-11-13: σ change rolled back; blind test of the depth rule; mechanisms decide (run 2026-11-13i) (Claude Code)

Asked by Pablo: roll back, look for the simplest way to handle the split events, try alternatives. 146 tests pass. Report: `catalog/CLASSIFICATION.md` section 12.

- **Rolled back:** `locate.py` and `tests/test_locate.py` are as in run `2026-11-13e` (10 km offshore floor back; `git diff` shows only the earlier changes). The 20 files of runs `2026-11-13g` and `h` are deleted and their 15 MANIFEST rows removed; the DATA rows stay, marked withdrawn. The entry above is kept as the record; its DECISIONS line is void.
- **Alternatives tried** on the 1 270 events over the shallow slab with a depth and a mechanism (974 thrusts on the contact, 296 others), classified without the mechanism: three σ (catalogue, tabled, 6.6 / 8.5 km) × four bands (Slab2 uncertainty, 10, 15, 20 km) × hardening (0.8, none, largest class), and a model fitted on d. New table `class_blind_`, function `blind()` in `classify_check.py`.
- **Finding:** depth hardly separates the interface. Brier score 0.205 for the rule of run `f`, 0.179 for giving every event the same weight, 0.173 for a 15 km band, 0.152 for the fitted model; the three σ differ by 0.01. The rule gives thrusts an interface weight of 0.68 and other mechanisms 0.40, and under-counts the interface by 20 % (34 % offshore). The σ was never the lever, and the count of split events was the wrong thing to drive down.
- **Mechanisms against the literature:** 28 of 29 agree (exception: Iquique foreshock 2014-03-16). From 1976 they cover 74–87 % of the events over the shallow slab at Mw ≥ 5.5, 49 % at 5.0–5.5, 4 % below 5.
- **Decided and applied:** `MECH = "add"` in `classify.py`: a thrust on the plate contact over a slab top ≤ 50 km is interface with weight 1 (959 events); another mechanism rules the interface out; no mechanism: depth and its error as before. Band, σ and 0.8 untouched. This is the variant "not in the brief" of the first A7 entry, now the baseline. It conflicts with the DECISIONS line "thrust on the plate contact: all [classes possible]"; line proposed below.
- **Result (Mw ≥ 4.5 in the domain):** interface 4 056.0 (3 671.8), in-slab 8 293.4 (8 548.8), crustal 1 416.6 (1 545.4), outer rise 509, unclassified 4. Split 3 785 (4 445); at Mw ≥ 5.5 519 (772), of which 200 near the band (453) and 319 without depth. From 1976 the split share is 13 % at Mw ≥ 5.5 and nil at Mw ≥ 7. Literature events by the rules alone: right 38 (30), split 4, wrong 3, no depth 18; Maule 2010, Iquique 2014 and Valparaíso 1985 are interface with weight 1. Thrusts of Mw ≥ 6.5 not interface: 3 (12).
- **Not checked:** 58 of the 959 thrusts are more than 20 km from the Slab2 surface (33 Potin depths, 44 of them below it); some may be in-slab thrusts. No distance limit was added.
- **Open for Pablo:** the band for events without a mechanism. The blind test favours 15 km over the Slab2 uncertainty (summed weight over thrusts 1.00 against 0.80; same below and above Mw 5.5), which would give interface 4 702.9 and 2 817 split events. Caveat: the test events are larger than the events the band is used for. Not changed.
- Not updated: sections 1–11 of CLASSIFICATION.md (run `f`, said at its top); the figures in `figs/classify/` are redrawn for run `i`.

### Proposed lines for DECISIONS (Classification)

- Replace "The mechanism says which classes are possible (thrust on the plate contact: all; ...)" by: "A mechanism decides between interface and not interface where there is one: a thrust on the plate contact (one nodal plane within 35° of the Slab2 plane, rake 45–135°) over a slab top ≤ 50 km is interface; any other mechanism is not. Depth alone separates the interface poorly (blind test on 1 270 events, A7), and mechanisms agree with the literature class in 28 of 29 events. Events without a mechanism take weights from the depth and its error (13 Nov, run 2026-11-13i)."
- LEARNINGS, Catalog: "Depth against Slab2 hardly tells interface from non-interface events (Brier 0.20 against 0.18 for a constant weight; A7 blind test). Check a classification rule against mechanisms withheld before tuning its inputs."

### Commands (already run; from `catalog/`)

`python classify.py`, `python classify_check.py`; `pytest` from `psha_chile8/`.

### Suggested commit (from the repo root; replaces the two commit lines above)

`git add psha_chile8/WORKLOG.md psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/palette.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/locate.py psha_chile8/catalog/classify.py psha_chile8/catalog/classify_check.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/tests psha_chile8/catalog/merged psha_chile8/catalog/figs`
`git commit -m "A7: tectonic classes as weights, mechanisms decide where they exist (run 2026-11-13i); GUC MW last and fitting floor at Mw 4.0 (run 2026-11-13e)"`

## 2026-11-13: band of 15 km (run 2026-11-13j) (Claude Code)

Decided by Pablo after the blind test. 147 tests pass. Report: `catalog/CLASSIFICATION.md` section 13.

- **`classify.py`:** `W = 15.0` (was `"unc"`), `RUN = "2026-11-13j"`; nothing else. `classify_check.py`: the Slab2 uncertainty is now a sensitivity variant; sections and band figure draw the 15 km band. One test added (default band).
- **Mw ≥ 4.5 in the domain:** interface 4 702.9 (run `i` 4 056.0, run `f` 3 671.8), in-slab 7 913.3, crustal 1 149.8 (forearc 541.6), outer rise 509, unclassified 4. Split 2 817 (1 525 near the band, 1 292 without depth); at Mw ≥ 5.5 477 (158 and 319). From 1976 split share 17 % at Mw ≥ 4.5, 11 % at ≥ 5.5, none at ≥ 7.
- **Literature events and Mw ≥ 7:** as in run `i` (right 38, split 4, wrong 3, no depth 18; 62 events of Mw ≥ 7 not at weight 1, 54 without depth and 8 of 1940–1965).
- **Sensitivity:** band 10 / Slab2 uncertainty / 20 km moves the interface −21 / −14 / +12 % (−8 / −5 / +5 % at Mw ≥ 5.5). Hardening 0.8 against none is now +3.8 % on the interface: with the wider band more events are rounded up than down. Worth knowing for the fits "with and without split events".
- **Limit of the evidence:** the 15 km rests on events with mechanisms (mostly Mw ≥ 5); it is applied mainly to smaller events.
- Runs `f` and `i` stay on disk as the comparison. Sections 1–11 of CLASSIFICATION.md still describe run `f`; a clean rewrite for run `j` is due before A8.

### Proposed lines for DECISIONS (Classification), replacing the band line

- "Interface band around the Slab2 surface: ± 15 km. On the 1 270 events over the shallow slab with a depth and a mechanism, classified without the mechanism, 15 km gives the right interface total and the Slab2 depth uncertainty (median 12 km) 20 % too little (A7 blind test, run 2026-11-13j); 10 and 20 km and the Slab2 uncertainty as sensitivity (13 Nov)."
- The mechanism line of the entry above stands.

### Commands (already run; from `catalog/`)

`python classify.py`, `python classify_check.py`; `pytest` from `psha_chile8/`.

### Suggested commit (from the repo root; replaces the commit lines above)

`git add psha_chile8/WORKLOG.md psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/palette.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/locate.py psha_chile8/catalog/classify.py psha_chile8/catalog/classify_check.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/tests psha_chile8/catalog/merged psha_chile8/catalog/figs`
`git commit -m "A7: tectonic classes as weights, mechanisms decide where they exist, band 15 km (run 2026-11-13j); GUC MW last and fitting floor at Mw 4.0 (run 2026-11-13e)"`

## 2026-11-13: X5, USGS-style class scores with our depth errors, and what can be validated (Claude Code)

Asked by Pablo after reading Haynie et al. (2026, CatSep) and García et al. (2012). Exploration only: `explore/X5/` (`x5_lib.py`, `x5_models.py`, `x5_check.py`, `tables/`, `REPORT.md`). Nothing under `catalog/` changed except two cards added to `catalog/LITERATURE.md`; run `2026-11-13j` is still the current classification. No tests added (exploration).

- **Papers:** CatSep uses an interface zone of ± 15 km about Slab2 (set by minimising the Brier score on 107 labelled events), a Kagan-angle factor that only lowers the interface score (1 up to 30°, 0.25 from 53°), and does not use the event depth error. García et al. require a thrust-like mechanism and a depth within ± 20 km of the interface together. Neither lets a mechanism decide alone, as run `j` does.
- **Models compared** on the 5 438 events with a depth over the shallow slab: A run `j`; A2 run `j` with mechanisms only excluding; B CatSep re-implemented (Moho fixed at 40 km); C = B averaged over the event depth error; E = C with a thrust-like mechanism (Kagan ≤ 30°) multiplying the interface odds by 3.3 (measured on best-depth events); D a mixture fitted without labels.
- **Checks:** 24 literature events: A 22 right (Brier 0.151), E 21 (0.167), C 20 (0.228), B 18 (0.430). Mechanisms withheld: C and E Brier 0.183, summed score 0.98 of the thrust-like events; A 0.196 and 1.06. Thrust-like events more than 20 km from the slab (56): interface score 0.89 in A, 0.32 in E, 0.15 in C. In the literature events the Kagan angle separates interface (4–27°) from the others (31–96°).
- **Reading:** E is the best compromise and follows USGS practice plus the two steps its authors name as future work. D is not robust. The data on disk cannot validate the classes of small events without mechanism.
- **Not done:** E is not implemented in `catalog/classify.py`. If Pablo takes it: replace the rules R3–R5 by the E scores, keep R1, R2, R6–R8, new run.
- **Validation that needs downloads (ask Pablo):** Riedel-Hornig et al. 2017–2021 catalogue (Zenodo), CRUST1.0 Moho, the CatSep code; and a synthetic test that needs nothing.
- Commands: `python x5_check.py` from `explore/X5/` (2 min).
- Suggested commit: add `psha_chile8/explore/X5` and `psha_chile8/catalog/LITERATURE.md` to the A7 commit, or `git commit -m "X5: USGS-style class scores with depth errors, checks against literature and mechanisms"`.

## 2026-11-14: X5 rerun, every scoring method through six tests, with the Riedel-Hornig catalogue (Claude Code)

Asked by Pablo. Exploration only: `explore/X5/` (`x5_riedel.py`, `x5_synth.py` new; `x5_check.py` rewritten; `REPORT.md` rewritten; `tables/x5_diagnostics.csv` and five more). Nothing under `catalog/` changed; run `2026-11-13j` is still the current classification. 147 tests as before (none added for the exploration).

- **Download (approved by Pablo):** primary catalogue of Riedel-Hornig et al. (2026), Zenodo 10.5281/zenodo.15284376, 101 MB, md5 verified, in `explore/X5/data/riedel_hornig_2026-11-14/` (not for git). DATA.md row under "Other inputs".
- **Tests:** (1) 24 literature events; (2) mechanisms hidden, 1 270 events; (3) Riedel-Hornig class and, as a second reference, their depth within −5 to +15 km of Slab2, 306 events of which 210 without mechanism; (4) reliability by score bin; (5) synthetic catalogues with known classes, three scenarios; (6) thrusts far from the slab. Diagnostics: share right, Brier score, summed interface over the true count, AUC, calibration gap.
- **Ceiling:** on the synthetic catalogues no method classes more than 62–65 % of the events right with our catalogued errors (66–71 % with errors × 0.7).
- **Ranking:** C (USGS scores averaged over the depth error) and E (C with a thrust-like mechanism multiplying the interface odds by 3.3) are best or equal best on tests 2, 3, 3d and 5; A (current run) is best only on the 24 literature events and gives thrust-like non-interface events a score of 1. B (USGS as published, no depth error) is worst on Brier everywhere. D (fitted mixture) is unstable.
- **Riedel-Hornig, the new finding:** in their depths the thrust-like events form a layer 4 km wide centred 5 km below Slab2, and other mechanisms sit 17 km below: with good depths the classes separate. Their class takes about ± 5 km of Slab2 as interface and so calls 27 of 58 thrust-like events in-slab. By their class every method of ours gives twice their interface (1.8–2.0), also for the 210 small events without mechanism; by their depths with −5 to +15 km, C and E give 0.97 and 1.00. If their class is right our interface rates at Mw 4.5–5.5 are a factor of two high.
- **Depths:** over the shallow slab ours agree with theirs within our σ (74 %; Potin −2.0 km, scatter 3.5). Under a deeper slab ISC-EHB and ISC depths are 11–24 km shallower than theirs (Potin −4 km); LEARNINGS already notes their eastern depths run deep.
- **Open for Pablo:** (a) take E (or C) into `catalog/classify.py` in place of rules R3–R5; (b) where the interface is centred and how wide it is: Slab2 ± 15 km as now, or the thrust layer the local depths show (about 5 km below Slab2); (c) whether the offset of the thrust layer is a Slab2 error or thrusts in the top of the slab, which is a question for S. Ruiz or C. Sippl.
- **Proposed line for LEARNINGS (Catalog):** "With our depth errors no rule classes more than about two thirds of the events over the shallow slab correctly (synthetic test, X5). In the local depths of Riedel-Hornig et al. (2026) thrust events sit about 5 km below Slab2 in a layer 4 km wide; their own class (± 5 km of Slab2) calls half of them in-slab."
- Commands: `python x5_check.py` from `explore/X5/` (about 8 min).
- Suggested commit: add `psha_chile8/explore/X5/*.py`, `explore/X5/REPORT.md`, `explore/X5/tables`, `psha_chile8/DATA.md`, `psha_chile8/WORKLOG.md`, `psha_chile8/catalog/LITERATURE.md`; not `explore/X5/data`.

## 2026-11-14: X5, the interface mechanism as plane plus slip, a skewed Kagan angle (Claude Code)

Asked by Pablo in steps: explain E; no interface weight for another mechanism; plane strict and rake loose about the convergence direction; one measure that does both; compare and review the math. Exploration only: `explore/X5/` (`x5_scheme.py`, `x5_kagan_scheme.py`, `x5_plane_slip.py`, `x5_skew.py` new; `x5_lib.py`, `x5_models.py`, `x5_synth.py`, `x5_check.py` extended; `REPORT.md` section 7; `tables/x5_buffer_other.csv`; four figures in `figs/`). Nothing under `catalog/` changed; run `2026-11-13j` is still the current classification. No tests added (exploration; the checks of the math are listed in the report and become tests when the rule moves to `catalog/classify.py`).

- **Why:** the Kagan angle gives 30° both to a plane 30° off with rake 90° and to the exact plane with rake 120°, which is 6° from the convergence direction. The USGS factor 0.25 for other mechanisms has no support here: the 14 literature interface events with a mechanism are all within 27°.
- **Measure:** swing σ (tilt of the plane from Slab2) and twist τ (turn of the slip from the convergence direction, in the plane), m = min over the four descriptions of the double couple of √((σ/20°)² + (τ/45°)²); interface possible where m ≤ 1. cos(Φ/2) = cos(σ/2) cos(τ/2) links it to the Kagan angle Φ. Verified against an independent quaternion decomposition on 20 000 random pairs.
- **Methods added:** F0 (C, interface 0 outside the ellipse), F (F0, odds × 3.9 inside), F1 (F with the weight falling to 0 between m = 1 and 1.5). A to E give the same scores as before.
- **Results:** literature 22 of 24 right for F and F1 (Brier 0.120 and 0.130; E 0.167, A 0.151). Riedel-Hornig depths: Brier 0.098 for F1, the best of all; totals 0.96–0.97. Synthetic: F1 64.0 % right, E 64.1 %. The 243 events with a mechanism outside the ellipse within 15 km of the slab carry 141 interface in E, 110 in run `j`, 0 in F, 53 in F1; of the 19 with a Riedel-Hornig class 16 are in-slab. Summed interface over the shallow slab: E 3 629, F 3 493, F1 3 548.
- **Reading:** the measure is sound; the weak point is the edge. Events with m 1–1.5 lie on the slab almost as those inside (0.70 of best depths within 10 km against 0.74), those beyond 1.5 do not (0.52). The share inside grows with magnitude, so part of what falls outside is mechanism error. Hence F1.
- **For Pablo:** 1985-03-04 00:32 Mw 7.4 is outside the ellipse (m 3.0; strike 234, dip 32, rake 155; two hours after the mainshock); 2014-03-16 Mw 6.7 (crustal in the literature) has m 1.25; 2015-11-07 Mw 6.1 near the trench has m 1.06 with a thrust mechanism.
- **Open:** F or F1; the tolerances; the convergence azimuth from a plate model per epicentre (one value now); then the rule into `catalog/classify.py` in place of R3–R5, with tests, as a new run.
- **Proposed line for DECISIONS (Classification), if taken:** "Interface mechanism: the Slab2 plane slipping in the plate convergence direction. Misfit m = √((swing/20°)² + (twist/45°)²), smallest of the four descriptions of the double couple; interface is possible for m ≤ 1, excluded from m = 1.5, linear between. A mechanism never proves interface: depth gives the weights."
- Commands: from `explore/X5/`, `python x5_check.py` (about 9 min), `python x5_skew.py`, `python x5_plane_slip.py`.
- Suggested commit: add `psha_chile8/explore/X5/*.py`, `explore/X5/REPORT.md`, `explore/X5/tables`, `explore/X5/figs`, `psha_chile8/WORKLOG.md`; not `explore/X5/data`. Message: "X5: interface mechanism as plane and slip misfit (skewed Kagan angle), methods F, F0, F1 through the six tests".

## 2026-11-14: A7, the F1 rule in `catalog/classify.py` (Claude Code)

Pablo chose F1 (soft edge). `catalog/classify.py`: new default `MECH = "ellipse"`, functions `nu`, `skew`, `ramp`, `by_depth`, `lift`, settings `SZ, DIFF, MOHO, NQ, TOL, AZ, LR, EDGE`, column `em` in `geometry()` and `mech_m` in the classes table, `RUN = "2026-11-14a"`. The modes `"add"`, `"exclude"`, `"none"` are kept (X5 and `classify_check.py` call them). `catalog/tests/test_classify.py`: the old tests name `mech="add"`; four new tests (misfit measure, scores by depth, inside and outside the ellipse, no depth with a mechanism). 151 tests pass. `explore/X5/x5_models.py`: model G (F1 with the 0.8 rule); `x5_check.py` rerun; `REPORT.md` section 8.

- **Port checked:** with `hard=None` the weights of `classify.py` equal the F1 scores of X5 on the 5 438 events (difference 0); `em` equals the X5 measure.
- **Conflict with DECISIONS, for Pablo:** DECISIONS (Classification) says a thrust on the plate contact allows all classes and any other mechanism rules the interface out, with a depth band; F1 replaces that over the shallow slab. It also says a weight ≥ 0.8 becomes 1. F1 was tested without that rule; with it (model G) every per-event score except the 24 literature events is worse and the interface over the shallow slab is 6 % higher (REPORT section 8). `HARD = 0.8` is left in the file because the decision stands; `HARD = None` is the tested F1.
- **Not run:** no file of run `2026-11-14a` written. In memory, Mw ≥ 4.5 in the domain: interface 4 564.0, in-slab 8 038.6, crustal 1 163.3, 3 030 split with `HARD = 0.8` (run `j`: 4 702.9, 7 913.3, 1 149.8, 2 817); 4 329.2, 8 170.4, 1 266.5, 6 280 split with `HARD = None`.
- **Mw ≥ 7 now split:** 2001-07-07 Mw 7.6 (interface 0.77) and 2015-09-16 23:18 Mw 7.1 (interface 0.58), thrusts with depths 16 and 24 km above Slab2. Candidates for a class hint in A6 if the literature has them as interface.
- **Stale:** `catalog/CLASSIFICATION.md` and the texts of `classify_check.py` describe run `j`; `mech_kind` is still the cone of the old rule. The convergence azimuth is one value (257°); tolerances not fitted.
- **Commands for Pablo:** set `HARD`, then `python classify.py` and `python classify_check.py` from `catalog/`; add the DATA.md row for run `2026-11-14a` with the printed totals.
- **Proposed lines for DECISIONS (Classification), replacing the mechanism and band lines of 13 Nov:** "Over the shallow slab (top ≤ 50 km) the depth gives scores after Haynie et al. (2026): interface within ± 15 km of Slab2, fading between 50 and 65 km; averaged over the depth error of the event. Interface mechanism: the Slab2 plane slipping in the plate convergence direction; misfit m = √((swing/20°)² + (twist/45°)²), smallest of the four descriptions of the double couple. m ≤ 1: interface odds × 3.9; from m = 1 to 1.5 the interface weight falls to 0. A mechanism never decides alone (14 Nov, X5)." And, if taken: "Weights are kept as they are; no weight is rounded to 1."
- Suggested commit: add `psha_chile8/catalog/classify.py`, `psha_chile8/catalog/tests/test_classify.py`, `psha_chile8/explore/X5/x5_models.py`, `explore/X5/REPORT.md`, `explore/X5/tables`, `psha_chile8/WORKLOG.md`. Message: "A7: interface by depth scores and the plane and slip misfit of the mechanism (F1 of X5) in classify.py; tests".
- **Later the same day, Pablo: keep the weights.** `HARD = None` in `catalog/classify.py`; the default now equals F1 of X5 (difference below the rounding of the table). The old-rule tests and the X5 models A, A2, G name `hard=0.8`; in `classify_check.py` the two loops over hardening now compare kept weights with 0.8. 151 tests pass. Expected totals of run `2026-11-14a` (Mw ≥ 4.5 in the domain): interface 4 329.2, in-slab 8 170.4, crustal 1 266.5, outer rise 509, unclassified 4; 6 280 split. The line "Weights are kept as they are; no weight is rounded to 1" is to go into DECISIONS in place of the 0.8 rule. Commands for Pablo: `python classify.py`, then `python classify_check.py`, from `catalog/`; then the DATA.md row. Add `psha_chile8/catalog/classify_check.py` to the commit.
- **Final settings, Pablo, same day:** hard edge of the ellipse (`EDGE = 1.0`: interface 0 for m > 1, method F of X5) and the 0.8 rule kept (`HARD = 0.8`). This supersedes the two notes above on F1 and on kept weights. With `hard=None` the weights equal method F of X5. 151 tests pass. Expected totals of run `2026-11-14a` (Mw ≥ 4.5 in the domain): interface 4 496.9, in-slab 8 078.9, crustal 1 190.1, outer rise 509, unclassified 4; 3 030 split; interface Mw ≥ 5.5 763.1 (run `j` 809.0). New figures `explore/X5/figs/spread.png`, `footprint.png` (`x5_spread.py`, `x5_footprint.py`). DECISIONS line to use: "… m ≤ 1: interface odds × 3.9; m > 1: no interface. A weight ≥ 0.8 becomes 1 (kept)."
- **Run `2026-11-14a` made** (asked by Pablo): `classes_`, `catalog_` and `class_shares_2026-11-14a.csv` in `catalog/merged/`, MANIFEST and DATA.md row added; totals as expected above. `classify_check.py` not rerun. Add `psha_chile8/DATA.md` and `psha_chile8/catalog/merged/MANIFEST.csv` to the commit.

## 2026-11-14: X5, nodal-plane clusters after Specht et al. (2017) on our mechanisms (Claude Code)

Asked by Pablo after reading Specht et al. (2017, GFZ STR17/01) and von Specht and Cotton (2020); neither was in our notes before. Exploration only: `explore/X5/x5_planes.py`, `x5_ace.py`, `x5_ace_fig.py`, `x5_spread.py`, `x5_footprint.py`; tables `x5_ace_*.csv`; figures `planes.png`, `ace.png`, `spread.png`, `footprint.png`. `catalog/` and run `2026-11-14a` unchanged.

- **Method:** mixture of components (normal in strike and rake on the circle, beta in dip) plus a uniform noise component, by expectation–maximisation, on both nodal planes of the 1 270 events with a mechanism over the shallow slab. Not their code (github.com/AgentSmith660/ACE, not downloaded): no merging and removal of components, number of components by BIC (2 to 8; BIC still falls at 8), no truncation along the rake; strike taken against the Slab2 strike. Second fit with depth − slab top as a further dimension (not in ACE).
- **Result, mechanism only:** families tight thrust (rupture plane strike −3°, rake 96°, dip 24°; auxiliary 169°, 88°, 69°) 912 events, broad reverse 145, normal 121, noise 92. Median depth below Slab2: 1.9, 7.4, 16.8, 7.1 km. Of the 878 events inside the ellipse 833 are in the tight thrust family; mean probability of that family 0.89 inside the ellipse, 0.50 for m 1–1.5, 0.03 beyond 1.5.
- **With depth:** the same families (856, 227, 138, 49); depth moves 56 events from tight thrust to broad reverse.
- **Reading:** the clusters exist and the ellipse picks the same interface cluster the data give. The earlier plots of swing and twist could not show the other clusters because they measure distance from one mechanism.
- **Open for Pablo:** whether the class rule should use the cluster probabilities in place of the ellipse; cards for the two papers in `catalog/LITERATURE.md` not written.
- Commands: from `explore/X5/`, `python x5_ace.py` (2 min), `python x5_ace_fig.py`, `python x5_planes.py`.

## 2026-11-14: A7 closed on run `2026-11-14a` (Claude Code)

Pablo: go with the ellipse and the depth error; finish A7. `classify_check.py` run on `2026-11-14a` (its sensitivity variants now: mechanisms not used, rules of run `j`; `classify.py` has the mode `"scores"` for the first); tables `class_*_2026-11-14a.csv` and `figs/classify/*.png` rewritten. `catalog/CLASSIFICATION.md` rewritten for this run; the note of the 13 Nov runs kept as `CLASSIFICATION_2026-11-13.md`. 151 tests pass.

- **Counts (Mw ≥ 4.5 in the domain, 14 279):** interface 4 496.9, in-slab 8 078.9, crustal 1 190.1, outer rise 509, unclassified 4; 11 249 at weight 1, 3 030 split (1 738 with a depth, 1 292 without).
- **Literature events, rules alone:** 36 right, 18 without depth, 7 split, 2 wrong (Copiapó 1918 west of the trench; La Ligua 1971 over a slab top of 56 km).
- **For Pablo:** Mw ≥ 7 with a depth and split: 10 events (table in CLASSIFICATION.md section 4); 2001-07-07 Mw 7.6 and 2015-09-16 23:18 Mw 7.1 are candidates for a class hint. `mech_kind` and the band figure still use the thrust test of 13 Nov.
- **Proposed lines for DECISIONS (Classification), replacing the mechanism and band lines of 13 Nov:** "Over the shallow slab (top ≤ 50 km) the depth gives scores after Haynie et al. (2026): interface within ± 15 km of Slab2, fading between 50 and 65 km depth; averaged over the depth error of the event. Interface mechanism: the Slab2 plane slipping in the plate convergence direction; misfit m = √((swing/20°)² + (twist/45°)²), smallest of the four descriptions of the double couple. m ≤ 1: interface odds × 3.9; m > 1: no interface. A mechanism never decides alone. A weight ≥ 0.8 becomes 1 (14 Nov, run `2026-11-14a`, X5)."
- **Proposed line for LEARNINGS (Catalog):** "Plots of the misfit to one reference mechanism hide the other mechanism families; nodal planes in strike, rake and dip show them (Specht et al. 2017)."
- **Not done:** cards for Specht et al. (2017) and von Specht and Cotton (2020) in `catalog/LITERATURE.md`; convergence azimuth per epicentre; PLAN A7 box left for Pablo.
- Commands: from `catalog/`, `python classify.py`, `python classify_check.py` (about 5 min).
- Suggested commit: `git add psha_chile8/catalog/classify.py psha_chile8/catalog/classify_check.py psha_chile8/catalog/tests/test_classify.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/CLASSIFICATION_2026-11-13.md psha_chile8/catalog/figs/classify psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/explore/X5 psha_chile8/DATA.md psha_chile8/WORKLOG.md` (not `explore/X5/data`; the `merged/*_2026-11-14a.csv` files as the earlier runs were handled). Message: "A7: classification run 2026-11-14a, depth scores with the depth error and the plane and slip misfit of the mechanism; checks, method note; X5 comparison of rules and nodal-plane clusters".

## 2026-11-14: A8, final chain run and frozen catalogue (Claude Code)

Brief pasted by Pablo (no file in `tasks/`); he allowed edits to DECISIONS.md, PLAN.md and REFERENCES.md for this task.

- **Three decisions of Pablo (in DECISIONS):** (1) `magnitude.py` reads the depths of the same run of `locate.py` (`LOC` = the run), so 1934-03-01 is Mw 7.6; (2) Jujuy nest from 150 km (`NEST` in `classify.py`; was 170), 1 054 events of Mw ≥ 4.5 (905 before), histogram in `catalog/figs/classify/nest.png`; (3) two interface class hints in `overrides_A6.csv` (2001-07-07 Mw 7.6, 2015-09-16 23:18 Mw 7.1), accepted, no reference: 74 accepted rows now.
- **Chain run:** `locate.py` (locations), `magnitude.py`, `locate.py` again (it joins the Mw into the catalogue; the locations are the same), `classify.py`; then `locate_check.py`, `magnitude_check.py`, `classify_check.py`. Locations and magnitudes are run `2026-11-14b`, classes `2026-11-14c` (two names because `classify.py` writes `catalog_<run>.csv` too). Against `2026-11-13e`: one Mw changed (1934-03-01, 7.3 → 7.6), no epicentre, no depth; 14 279 events of Mw ≥ 4.5 in the domain, 12 391 with a measured depth.
- **Classes (Mw ≥ 4.5 in the domain):** interface 4 497.7, in-slab 8 078.9 (shallow 1 636.5, intermediate 5 388.4, Jujuy nest 1 054), crustal 1 189.3, outer rise 509, unclassified 4; 11 251 at weight 1, 3 028 split (1 736 with a depth, 1 292 without).
- **Tests:** 151 pass. One test changed: the event just above the nest in `test_subclasses_and_the_jujuy_nest` moved from 150 to 140 km.
- **Frozen:** `catalog/frozen/2026-11-14/`: the catalogue, classes, shares, locations, Mw, defaults, relations, offsets, `overrides_A6.csv`, the five scripts in `code/`, `SHA256SUMS` (verified), `INPUTS_SHA256` (A3 events and links), and the one-page `DECISIONS_NOTE.md`.
- **Documents brought to this run:** `catalog/CLASSIFICATION.md` (by me); `catalog/REPORT_A3-A5.md`, `MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md` and `paper/CATALOG_SECTION_draft.md` (by two sub-agents, numbers recomputed from the files of the run; the paper draft has a new section 2.6 on the tectonic class, which I read; the three notes I did not read line by line). Rules figure `catalog/figs/rules/catalog_rules.png`: the CSN Mw of the ISC Bulletin last among the measured magnitudes. REFERENCES.md: new section F with the papers of A6 and A7. FIGURES.md: rows for the nest and the rules figure. DATA.md: rows for `2026-11-14b` and `2026-11-14c`. PLAN: A7 and A8 ticked, marker on B9.
- **Found by the sub-agents, for Pablo:**
  - Test 3 of the magnitudes passes 30 of 32, not 31 (Mw 6.5–7 from floor 5.0: 87.8 predicted, band from 88.6, 108 observed; so since run `e`).
  - The count of local records left out by the 50 km check is 94 in a recount with the functions of `locate.py`, not the 85 written in DECISIONS and the paper draft (marked "[to check]" there). Not settled.
  - NEIC mb is no longer split by depth (ISC mb is); the 1990 period split is a candidate in the code that is never scored.
  - The acceptance tests of `magnitude_check.py` run on the rule values, before the A6 corrections.
  - Marked "[to check]" in the paper draft: 833 of 878 (cluster check, run `2026-11-14a`), the 151 and 53 events behind the factor 3.9, the A6 review coverage (112 of 459).
- **Open:** the points listed in `DECISIONS_NOTE.md`; cards for Specht et al. (2017) and von Specht and Cotton (2020) in `catalog/LITERATURE.md`; the rules figure is not in the Ubuntu font; `explore/X5` still reads the catalogue of `2026-11-13e`.
- **Commands (to repeat the run):** from `catalog/`, `python locate.py`, `python magnitude.py`, `python locate.py`, `python classify.py`, `python locate_check.py`, `python magnitude_check.py`, `python classify_check.py`; `pytest` from `psha_chile8/`.
- **Suggested commit** (from the repo root; about 180 MB of run files, the frozen copies are the same blobs):
  - `git add psha_chile8/catalog/*.py psha_chile8/catalog/tests psha_chile8/palette.py psha_chile8/catalog/overrides_A6.csv psha_chile8/catalog/figs` (this takes in the edits to `locate.py`, `magnitude.py`, `magnitude_check.py`, their tests, `a6.py` and `palette.py` left uncommitted since 13 Nov; the frozen run depends on them)
  - `git add psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/catalog/merged/*_2026-11-14b.* psha_chile8/catalog/merged/*_2026-11-14c.csv psha_chile8/catalog/merged/review/*_2026-11-14b.csv psha_chile8/catalog/merged/review/*_2026-11-14c.csv psha_chile8/catalog/frozen`
  - `git add psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/REPORT_A3-A5.md psha_chile8/catalog/MAGNITUDES.md psha_chile8/catalog/RULES_LOCATION_MAGNITUDE.md psha_chile8/paper/CATALOG_SECTION_draft.md`
  - `git add psha_chile8/DECISIONS.md psha_chile8/PLAN.md psha_chile8/REFERENCES.md psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`
  - `git commit -m "A8: final chain run 2026-11-14b/c on one set of depths, frozen catalogue with checksums and decisions note; Jujuy nest from 150 km, two interface hints, 1934-03-01 Mw 7.6; notes, paper draft and rules figure brought to the run"`
  - `overrides_A6.csv`, `a6.py`, `catalog/A6/` and the runs of 13 Nov were never committed; `overrides_A6.csv` is in the first line above, the rest is Pablo's call.

## 2026-11-14: B9, earthquake statistics per class, exploratory run (Claude Code)

Brief `tasks/B9_statistics_explore.md`. Everything is in `explore/B9/`; nothing under `catalog/` changed. Report `explore/B9/REPORT.md`, figures `explore/B9/figs/` (21, index in `figures_index.md`), tables `explore/B9/tables/`, intermediate results `explore/B9/cache/`. 15 tests of the estimators pass (`explore/B9/tests/`). No decisions taken; B9 stays open, no PLAN tick, no DATA.md row (no new run or input), no FIGURES.md row (no figure is proposed for the paper yet).

- **Step 0** (`explore/B9/STEP0.md`, done by a sub-agent, not re-run by me):
  - The 50 km check leaves out **94** events of Mw ≥ 4.5 in the domain (97 anywhere, 423 of any size, 13 of Mw ≥ 5.5 in the domain). 85 is not reproduced by any saved run. Proposed: DECISIONS:23 → "(quality check; 94 events of Mw ≥ 4.5 in the domain, 423 of any size, run 2026-11-14b)"; paper draft :49 and :143 → 94; REPORT_A3-A5:103 → "97 of Mw ≥ 4.5 anywhere; 13 of Mw ≥ 5.5 in the domain, 14 anywhere".
  - Disagreements with the frozen run or DECISIONS, and the open marks: listed file by line in `STEP0.md`. The ones in DECISIONS itself: :35 still lists 1934-03-01 among the events left as they are; :14–15 "Cabello not from 1900 on" against 1904 in :17 and the code; :15 Potin to 2022 against 2020-07-16; :26 unknown depths "classified by mechanism" against the frozen rule; :50 the order before 1976 omits the measured Mw that the code puts second.
- **What ran:** declustering (Gardner–Knopoff, nearest neighbour); completeness in time (Stepp, change points, Mc per window) on full and declustered counts; `classify.py` rerun with an interface band of ± 10 and ± 20 km (the ± 15 km rerun gives the frozen weights exactly); 7 386 Weichert fits (tables × weights × declustering × error correction, floors, periods, fits below Mw 7, sensitivity cases) and b-positive; Mc maps; the checks; a follow-up of the two surprises.
- **Main findings** (numbers and figures in the report):
  - A table that mixes a short window for the small events with long windows for the larger ones raises the interface b to 1.06 and under-predicts the large events (29 fitted, 44 observed at Mw ≥ 7 since 1900). One instrumental window plus the long record from Mw 7 (5.0 from 1964, 7.0 from 1900, 7.5 from 1820, 8.0 from 1730) gives b 0.93, N(≥ 7) 0.37 per year, and passes at Mw ≥ 7 (60 / 56) and Mw ≥ 8 (12.6 / 15.6), for the margin and the four segments.
  - Mw 4.5–4.9 is complete only from about 2000; Mw ≥ 5.0 and 5.5 from 1964 hold. Shape-based Mc does not see this.
  - Intermediate in-slab: Mw ≥ 7 is 2.8 times more frequent in 1900–1975 than since 1976 (p 0.01); every table reaching before 1964 fails the large-event check. b 1.12–1.16 whatever the table.
  - Gardner–Knopoff removes 79 % of the interface and 88 % of the Jujuy nest and gives an interface b of 0.6–0.77 without a plateau; the nearest-neighbour method leaves b unchanged.
  - The split events are a rate question (shallow in-slab × 0.51, forearc × 0.37, interface × 0.75), hardly a b question.
  - The CEUS-SSC procedure moves historical events by 0.2–0.9 magnitude units. **The report is not on disk; the equations were not checked against §3.3.1.**
- **Proposed lines for LEARNINGS** (proposals):
  - Completeness: "With the analysis set cut at Mw 4.5 (the frozen file holds smaller events, not used in B9), Mc per window (maximum curvature, b-stability, KS) reads 4.5–5.1 everywhere; the steps show in the count of Mw 4.5–4.9 over 5.0–5.4 per period (0.7–1.1 before 1990, about 3 from 2000) and in change points of declustered yearly counts (1964, 2001) (B9)."
  - Completeness: "An automated Stepp test on the full catalogue reads 'complete from 2000' at every magnitude, because the reference rate holds Maule, Iquique and Illapel; read completeness years on declustered counts (B9)."
  - Fits: "A table with Mw 4.5 from 2000 and Mw 5.5 from 1964 gives the interface b 1.04–1.06 where each window alone gives 0.92–0.96: the Mw ≥ 5.5 rate is 12.3 per year in 2000–2026 and 7.0 in 1964–1999. One window for the instrumental part, long windows only from Mw 7 (B9)."
  - Fits: "Gardner–Knopoff keeps the largest event of each window and lowers b by 0.15–0.4; at Mw 4.5 it removes 88 % of the Jujuy nest and half of the intermediate in-slab events. The nearest-neighbour method leaves b as it is (B9)."
  - Catalog: "Intermediate in-slab events of Mw ≥ 7: 29 in 1900–1975 (most converted from Centennial mB / Ms), 7 since 1976; at Mw ≥ 6.5 the two periods agree. Fits that use them fail the large-event check (B9)."
  - Fits: "The CEUS-SSC move to M − βσ² shifts events with σ 0.3–0.6 by 0.2–0.9 units; apply it to instrumental values or use the weight exp(−β²σ²/2) (B9)."
- **Proposed lines for DECISIONS** (for B10, options not decisions): the completeness table of the interface (one window from 1964 plus the historical steps; floor 5.0, 5.2 or 5.5); whether Mw ≥ 7 before 1964 counts in the in-slab rates; b of the Jujuy nest, backarc and Patagonia (no plateau: borrowed or fixed); which declustered catalogue feeds the spatial pattern; the form of the magnitude-error correction once the CEUS-SSC report has been read.
- **Open questions for Pablo:** (1) the old intermediate-depth events: lower them (the ISC-GEM proxies are 0.5–1.2 below), leave them out of the rate fits, or accept a quiet half century; (2) is the forearc of 1964–1975 incomplete at Mw ≥ 5.5 (0.2 per year against 1.1 later) or a class effect of the old depths; (3) the interface north of 21° S stays thin at Mw 4.5–4.9 after 2010; (4) a copy of CEUS-SSC (2012) chapter 3 for `refs/`.
- **Commands to rerun** (from `explore/B9/`, conda `psha_renta`, about 6 min in all; settings at the top of each script; `FORCE = True` in `b9_3_fits.py` to redo cached fits): `python b9_2_decluster.py`, `python b9_1_completeness.py`, `python b9_0_bands.py`, `python b9_3_fits.py`, `python b9_4_space.py`, `python b9_5_checks.py`, `python b9_6_deeper.py`, `python b9_7_figs.py`; `pytest explore/B9/tests` from `psha_chile8/`.
- **Suggested commit** (from the repo root; `cache/` holds 25 MB of pickles that the scripts rebuild, left out):
  - `git add psha_chile8/tasks/B9_statistics_explore.md psha_chile8/explore/B9/*.py psha_chile8/explore/B9/*.md psha_chile8/explore/B9/tests psha_chile8/explore/B9/tables psha_chile8/explore/B9/figs psha_chile8/explore/B9/cache/*.csv psha_chile8/WORKLOG.md`
  - `git commit -m "B9: exploratory statistics per class on the frozen catalogue: completeness in time and space, Weichert and b-positive fits with weights, declustering, large-event and stationarity checks, sensitivity cases; report, figures and step 0 audit"`

## 2026-11-15: B9 follow-up, magnitude-error references and Mc from Mw 4.0 (Claude Code)

- **Magnitude error and rates.** Read CEUS-SSC (2012) Volume 1 §3.3.1 and Volume 2 §5.3.2 (parts), Mueller (2019), Felzer (2008, 2013), Rollins et al. (2024), Michael and Llenos (2026), Llenos et al. (2026), Petersen et al. (2024), Musson (2012). Notes: `explore/B9/MAG_ERROR_REFS.md`. `ceus()` in `b9_lib.py` agrees with eq. 3.3.1-5 and 3.3.1-12 (mode `ceus`) and 3.3.1-1 (mode `plain`); the caveat of the 14 Nov entry ("equations not checked") is closed. Not read: Tinti and Mulargia (1985, BSSA); `refs/catalogs/tinti_mulargia_1985.pdf` is their completeness paper of the same year.
- **Recommendation given to Pablo, not decided:** weight exp(−β²σ²/2) per instrumental event, no magnitude shift (CEUS-SSC shows shifts are biased when completeness varies with magnitude), no correction for historical events (Mueller 2019 after Musson 2012). Pablo: no logic-tree branch for it. This would change the wording of DECISIONS (magnitude-uncertainty line of 11 Nov: "shift to E[M] = M − βσ², then N*"). The variant "weight on instrumental events only" has not been run.
- **Correction of the 14 Nov entry:** the frozen catalogue is not cut at Mw 4.5; it holds 18 002 events of Mw 4.0–4.4 in all. B9 loaded only Mw ≥ 4.5 (DECISIONS). Wording fixed in `REPORT.md` and in the proposed LEARNINGS line above.
- **Mc from Mw 4.0** (`explore/B9/b9_8_mc40.py`, `tables/mc_from_40.csv`, `figs/mc_from_40.png`; check only, no fit uses the events). b-stability and KS, interface: 5.1 / 5.0 in 1964–1975 / 1976–1989, 4.7 in the 1990s, 4.6 in 2000–2006, 4.5 in 2007–2011, 4.2–4.3 in 2012–2019. Mw 4.5 from 2000 and Mw 5.0 from 1964 hold, each 0.1 short in its first window. Mw 4.0–4.4 is not complete in any period, so there is no case for lowering the cut. Maximum curvature reads 4.2–4.4 everywhere and is not usable.
- **Proposed line for LEARNINGS:** Completeness: "Mc per window needs the events below the cut: read from Mw 4.0, b-stability and KS give the interface 5.0–5.1 before 1990, 4.7 in the 1990s, 4.5–4.6 in 2000–2011 and 4.2–4.3 from 2012; maximum curvature reads 4.2–4.4 in every window (B9, 15 Nov)."
- **Command:** from `explore/B9/`, `python b9_8_mc40.py` (about 1 min; writes `cache/m40.pkl`).
- **Suggested commit:** add to the B9 commit `psha_chile8/explore/B9/b9_8_mc40.py psha_chile8/explore/B9/MAG_ERROR_REFS.md psha_chile8/explore/B9/tables/mc_from_40.csv psha_chile8/explore/B9/figs/mc_from_40.png`.
- **Fit with the magnitude-error weight on instrumental events only** (asked by Pablo, 15 Nov; `explore/B9/b9_9_magerr.py`, report section 6, `tables/magerr_*.csv`, `figs/magerr_weight.png`, `tests/test_magerr.py`; 17 tests pass). Kinds `direct`, `proxy`, `iscgem`, `centennial` count exp(−β²σ²/2); `cabello`, `rm18`, `a6` count 1; no magnitude moved.
  - Change of the Gutenberg–Richter parameters: N(≥ 5) −8 to −10 % in every class (interface −7.6 %), b −0.01 (inside its bootstrap sd), interface N(≥ 7) −2.7 % and N(≥ 8) −0.2 %. Intermediate in-slab N(≥ 7) −13 %, from ISC-GEM values of 1964–1975 with σ up to 1.1.
  - Test on real data: 6 193 events with a measured and a converted Mw. Converted counts are 6–9 % higher at Mw ≥ 5.6–6.0 from 1976 (expected 8 %; 3–7 % from 2000), and equal within the bootstrap band with the weights. The direction is the one DECISIONS assumes for the inverse-fit conversions.
  - Test on synthetic interface catalogues: no weight leaves N(≥ 5) 10 % high; the instrumental weight removes it in all three cases for the historical magnitudes. N(≥ 7) then is +13 % if the historical magnitudes carry their listed error, +3 % if they are exact, −3 % if they are regression values; with the weight on all events +3 / −3 / −6 %. One catalogue scatters 4–6 % at N(≥ 7).
  - Open for Pablo: the historical events (weight or not), and whether ISC-GEM values with σ above about 0.5 should take the full weight (a count of 0.07 at σ 1.0).
  - Command: from `explore/B9/`, `python b9_9_magerr.py` (about 1 min). Add to the commit: `psha_chile8/explore/B9/b9_9_magerr.py psha_chile8/explore/B9/tests/test_magerr.py psha_chile8/explore/B9/tables/magerr_*.csv psha_chile8/explore/B9/figs/magerr_weight.png`.
- **Completeness of the whole catalogue, by region, depth and on a map** (asked by Pablo, 15 Nov; `explore/B9/b9_10_mc_all.py`, report part 2, `tables/mc_all_regions.csv`, `figs/mc_all_map_1deg.png`, `mc_all_map_05deg.png`). All events of Mw ≥ 3.5, no class weights; a check only.
  - Whole margin, KS / b-stability: 5.2 / 5.1 in 1964–1975, 5.1 / 5.0 in 1976–1989, 4.6 / 4.8 in 2000–2006, 4.9 / 4.8 in 2007–2011, 4.6 in 2012–2019. It reads 0.1–0.4 above the regional values from 2000 (a mixture of regions is curved), so the regional rows are the ones to use.
  - Map, cells of 1° with 250 km: Mc above 4.5 in 97 % of the cells in 1976–1999, 52 % in 2000–2011 (coast 30–41° S, east of the Andes 22–30° S, Peruvian border), 15 % in 2012–2026 (18–21° S and the far south). Above 5.0: 11 %, 1.5 %, none. No estimate south of 36° S before 2000 or south of 41° S before 2012.
  - Read: Mw 5.0 holds everywhere mapped from 2000 and in nine of ten cells from 1976; 1964–1975 reads 5.1–5.2. Mw 4.5 from 2000 does not hold for the whole catalogue.
  - Proposed line for LEARNINGS: Completeness: "Mc belongs to place, depth and period, not to the tectonic class; read it on all events from Mw 3.5 per region. A shape-based Mc of the whole margin reads 0.1–0.4 too high because regions with different b add to a curved distribution (B9, 15 Nov)."
  - Pablo on the magnitude-error weight: one rule for all events or none; to be settled after completeness.
  - Command: from `explore/B9/`, `python b9_10_mc_all.py` (about 2 min the first time; `FORCE = True` to redo). Add to the commit: `psha_chile8/explore/B9/b9_10_mc_all.py psha_chile8/explore/B9/tables/mc_all_regions.csv psha_chile8/explore/B9/figs/mc_all_map_*.png`.
- **Automatic completeness table** (asked by Pablo, 15 Nov; `explore/B9/b9_11_autotable.py`, report section 7, `tables/auto_*.csv`, `figs/auto_table.png`, `tests/test_autotable.py`; 20 tests pass).
  - Searched: the automated Stepp of the OpenQuake HMTK, the table search of oq-mbtk (generate candidate tables, keep the best; its criterion was not found in the documentation), Hakimhashemi and Grünthal (2012), Kijko and Smit (2012, 2017), Ogata and Katsura (1993). None was read in full.
  - Joint rule (rates of all bands and blocks against one Gutenberg–Richter line, BIC, larger magnitudes complete no later): recovers the table on stationary synthetic catalogues (b within 0.01, N(≥ 5) within 1 %), fails on the real one: the 2010–2015 sequences set the complete level and earlier periods read as incomplete (interface b 1.08, 9.6 events of Mw ≥ 8 expected against 19).
  - Hybrid rule: instrumental steps from Mc per window and region (4.5 from 2020, 4.7 from 2012, 5.0 from 1976, 5.2 from 1964, the same for every class), historical steps from the rate rule with the instrumental line held fixed. Interface: + 5.5 / 1960, 6.5 / 1955, 7.0 / 1900, 7.5 / 1830, 8.0 / 1500; b 0.950, N(≥ 5) 27.4, N(≥ 7) 0.345, large events 64 / 59 at Mw ≥ 7 and 20 / 19 at Mw ≥ 8. Close to the candidate read by hand (b 0.929, N(≥ 7) 0.368).
  - In-slab: the rule accepts the old large events because they are too many, not too few; no historical steps there. Crustal: b 0.93 or 1.02 depending on the floor.
  - Kijko–Smit implemented next to Weichert: same number on one period, within the bootstrap sd on a table that fits, 0.06–0.17 apart on a table that does not. Use as a check of the table.
  - Pablo, 15 Nov: completeness must fall monotonically in time (both rules do); Patagonia b fixed from the crustal classes, backarc and Jujuy nest one floor each, no pooling; no check of Maule at Mw 5.0; no comparison of the two hand-made windows.
  - Proposed line for LEARNINGS: Completeness: "A completeness rule that compares rates between periods takes the sequences of 2010–2015 for the complete level and reads earlier periods as incomplete (Stepp, change points and a joint likelihood all do). Take the instrumental steps from the shape of the magnitude distribution with events from Mw 3.5, and use rates only before 1964 with the instrumental line fixed (B9, 15 Nov)."
  - Command: from `explore/B9/`, `python b9_11_autotable.py` after `b9_10_mc_all.py` (about 1 min). Add to the commit: `psha_chile8/explore/B9/b9_11_autotable.py psha_chile8/explore/B9/tests/test_autotable.py psha_chile8/explore/B9/tables/auto_*.csv psha_chile8/explore/B9/figs/auto_table.png`.
- **Refit of every class on the single table, and DECISIONS written** (asked by Pablo, 15 Nov; `explore/B9/b9_12_refit.py`, report section 8, `tables/refit_single_table.csv`, `figs/refit_single_table.png`).
  - Table for every class: Mw 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500.
  - Interface b 0.958 (sd 0.017), N(≥ 5) 27.5, N(≥ 7) 0.333, large events 60.6 / 58.5 and 18.9 / 19.0. In-slab shallow b 1.147, intermediate 1.136, Jujuy nest 1.237; forearc 0.999, arc 1.003, backarc 0.988; Patagonia with the forearc b. Only intermediate in-slab fails the large-event check (22 fitted, 38 observed at Mw ≥ 7).
  - **DECISIONS.md edited by Claude Code at Pablo's word ("write the decisions")**, against the usual rule of proposing only: new section "Statistics (B9)" (completeness on the whole catalogue, automatic rule, the table, estimators, Patagonia / backarc / Jujuy nest, three open points); the lines on the Mw 4.5 cut and on the magnitude-error correction rewritten; two lines under Superseded. Only what Pablo said or approved on 15 Nov was written as decided. A copy of the file before the edit is in the session scratchpad, not in the repo; `git diff psha_chile8/DECISIONS.md` shows the change.
  - Still open: the magnitude-error weight on all events or none; the intermediate in-slab events of Mw ≥ 7 before 1976; Mw 8.0 from 1500 against 1730. Not ticked in PLAN (the brief says B9 stays open for B10).
  - Command: from `explore/B9/`, `python b9_12_refit.py` (10 s). Add to the commit: `psha_chile8/explore/B9/b9_12_refit.py psha_chile8/explore/B9/tables/refit_single_table.csv psha_chile8/explore/B9/figs/refit_single_table.png psha_chile8/DECISIONS.md`.
- **Weight on all events against none, on the single table** (asked by Pablo, 15 Nov; report section 8, `tables/refit_single_table.csv`). b moves by 0.02 at most; N(≥ 5) −8 to −11 % in every class; interface N(≥ 7) −10 %, N(≥ 8) −11 %. The weight is nearly one factor for the whole line (interface mean count 0.92 at Mw 5.0–5.4, 0.77 at Mw ≥ 8). Large-event checks pass or fail the same way in both. Still Pablo's choice.
- **Decided by Pablo, 15 Nov: the magnitude-error weight on all events.** DECISIONS.md updated (magnitude line under Magnitudes, the open line of Statistics, the Superseded line). `b9_12_refit.py` runs with `MAGERR = True`; `tables/refit_single_table.csv` and `figs/refit_single_table.png` are the weighted fits (columns `_none` without). Interface b 0.962 (sd 0.017), N(≥ 5) 25.2, N(≥ 7) 0.300, N(≥ 8) 0.033; large events 54.4 / 49.7 and 16.9 / 14.7. Fails of the large-event check: intermediate in-slab (18.3 / 29.4) and segment 32–26° S (17.0 / 9.6). Kijko–Smit for the interface 0.915, 2.8 sd below Weichert. Open: the intermediate in-slab events before 1976; Mw 8.0 from 1500 against 1730.
- **Pablo, 15 Nov: the two open points are left as they are and go into the discussion of the paper** (old intermediate in-slab events of Mw ≥ 7; Mw 8.0 from 1500). DECISIONS.md, Statistics: the "Open" line rewritten accordingly. With this the B9 statistics have no open decision; for the paper draft: one paragraph in the discussion on each point.
- **Project documents brought up to date (Pablo, 15 Nov: "make sure the learnings go into the project documents").** Written directly, not as proposals: `LEARNINGS.md` (Completeness, b-value and rates, Declustering, In-slab, Pitfalls / Fits; the "Open for B9" line replaced by the results); `PLAN.md` (B9 ticked, marker on B10); `FIGURES.md` (six rows from `explore/B9/figs/`); `REFERENCES.md` (section G, statistics: nine entries read, a list of methods used but not read). `explore/B9/REPORT.md` has a status block at the top. The LEARNINGS lines proposed in the entries of 14 and 15 Nov above are superseded by what is now in the file (the line on the CEUS-SSC move in particular).
  - Not touched: `DATA.md` (no new catalogue run), the paper draft, and the catalogue documents listed in `explore/B9/STEP0.md` (94 not 85 events in the 50 km check, and the other disagreements): still to be corrected by Pablo or in the catalogue conversation.
  - Add to the commit: `psha_chile8/LEARNINGS.md psha_chile8/PLAN.md psha_chile8/FIGURES.md psha_chile8/REFERENCES.md psha_chile8/WORKLOG.md psha_chile8/DECISIONS.md psha_chile8/explore/B9`.
  - Suggested message: `B9: statistics exploration closed: whole-catalogue completeness and automatic table, magnitude-error weight, refit of every class; decisions, learnings, figures and references updated`

## 2026-11-15: B11, fitting code, methods compared, final fits (Claude Code)

Brief `tasks/B11_fits.md`. Everything is in `fits/`; the report is `fits/FITS.md`. The frozen catalogue was not changed. 15 tests pass (`pytest fits/tests`).

- **Step 0 (audit of `explore/B9/STEP0.md`).** Every number was recomputed before editing: the 50 km check with `locate.py` and the frozen defaults (94 of Mw ≥ 4.5 in the domain, 97 anywhere, 13 / 14 of Mw ≥ 5.5, 423 of any size; `inside_network` reproduced for 204 956 of 204 956 events); 6 334 reference Mw and 106 GUC MW (42 at Mw ≥ 4.5 in the domain); 1 017 GCMT values lowered, 865 in the domain; the per-period differences to the published catalogues from `mw_tests_2026-11-14b.csv`; the X4 percentages from `x4_blind.csv`.
  - Changed: `DECISIONS.md:23` (85 → 94, 423 of any size). `catalog/REPORT_A3-A5.md`: 107 → 106; "35–40 % fewer" → per period (40 / 45 / 44 / 33 % against Cabello, 42 / 36 / 34 / 19 % against Candia and Macedo); 1 017 with 865 in the domain; the 2011-01-07 event (rule gives GUC MW 5.6, A6 5.7; only 2010-02-27 was from ML); the line on the 50 km check. `catalog/MAGNITUDES.md`: 6 334 and 106; 865 in the domain; §6a percentages given for both agency sets, which reconciles them with DECISIONS (+5 to +10 %, −7 to −15 %). `catalog/RULES_LOCATION_MAGNITUDE.md`: M3, M5 and the patch table (each count with its population). `paper/CATALOG_SECTION_draft.md`: 94 (two places), 106, 6 334 (two places), the measured Mw in the order before 1976 (nine GCMT events of 1964–1975), the crustal score fading from the Moho, 865, the stale notes on MAGNITUDES.md and CLASSIFICATION.md, "(limitation 2)", the 40 % of E.3, the 2011-01-07 wording of E.4, one clause in the header.
  - Left: the other DECISIONS lines of STEP0 (`:14-15`, `:26`, `:35`, `:50`; the brief allows only the count) — still for Pablo. `frozen/2026-11-14/DECISIONS_NOTE.md` and `frozen/overrides_A6.csv` (frozen). `MAGNITUDES.md:135` "[Test numbers to be filled.]" and every open mark of STEP0 part 3 (they need a choice of numbers or a rerun, not a correction). `MAGNITUDES.md` §6a is still the run of 12 Nov. RULES D4 "83 keep a depth" against the paper's 84: not in STEP0, not checked.
- **Step 1 (magnitude σ; FITS.md section 3, `fits/sigma.py`, `tables/sigma_*.csv`).** Table of σ and count per kind and period. Counts at β 2.2: direct 0.98, proxy 0.87–0.89, Centennial 0.85, ISC-GEM 0.77–0.79 on average, Cabello 0.55.
  - The ISC-GEM values with σ near 1 are all quality D, and all quality-D values come from the ISC-GEM Supplement (events ISC-GEM lists apart because epicentre or magnitude is unreliable). 23 events of Mw ≥ 5.0, the largest Mw 6.6; 11 inside the table, counted 2.9 together. No effect on the fits or on the large events.
  - **Proposed σ correction (not applied; a catalogue rule):** do not take an Mw of quality D from the ISC-GEM Supplement; the event goes to the next source.
  - The weight removes 20–30 % of the events of Mw ≥ 7 and ≥ 8, nearly all before 1904, where every Cabello value has the set σ 0.5 (interface Mw ≥ 8 before 1904: 11 events count 7.2). B9's remark that intermediate in-slab loses 13 % at N(≥ 7) through ISC-GEM values with σ 1.1 is wrong: those are of Mw ≤ 6.6; the loss is the Centennial and Cabello values.
- **Step 2 (code).** `fits/gr.py` (Weichert, truncated and tapered forms, Aki–Utsu, Ogata–Katsura, Kijko–Smit, b-positive, least squares, shrinkage, large-event check, bootstrap), `fits/table.py` (automatic table), `fits/synth.py` (synthetic catalogues built like ours), `fits/run.py` (settings and units at the top), `fits/compare.py`, `fits/sigma.py`, `fits/figs.py`, `fits/tests/`. Nothing imports from `explore/`.
  - `table.py` gives the table of DECISIONS on the frozen catalogue, and `run.py` stops if it does not. One new setting: a historical step less than 10 years before 1964 is dropped (`MIN_BACK`), instead of dropping "6.0 from 1960, 6.5 from 1955" by hand.
  - Synthetic tests: Weichert recovers b within 0.003 and N(≥ 5, 7, 8) within 2 %, 1 % and 1 % (large class); bootstrap intervals hold the truth in 87–89 % of 400 catalogues for b and N(≥ 7) (nominal 90 %), 81–87 % for N(≥ 5). Without the magnitude-error weight N(≥ 5) is 12 % and N(≥ 7) 26–29 % high.
  - **The automatic table does not recover a known table reliably** (40 synthetic margins per case). By the rule of DECISIONS "5.0 from 1976" is found in 0–5 % of the catalogues (median 2009–2020: one window that reads high by chance moves the step) and Mw 7.0 comes out 30–75 years early; the fit on the automatic table has b +0.015 to +0.033, N(≥ 7) 6–14 % low and N(≥ 8) 9–20 % low. With the smaller of the two Mc methods "5.2 from 1964" is found in 83–88 % instead of 23–30 %.
- **Step 3 (methods; FITS.md section 4, `tables/fits_sensitivity_2026-11-15.csv`, `synth_methods.csv`, `synth_pooled.csv`, `figs/methods.png`, `figs/synthetic_methods.png`).**

  | method | synthetic: bias of b / N(≥ 7), large class | real catalogue |
  |---|---|---|
  | Weichert, open line (reference) | +0.003 / +1 % | fails intermediate in-slab and segment 32–26° S at Mw ≥ 7 |
  | Weichert, line cut at Mmax | +0.002 / +1 % | same b; N(≥ 7) −24 % nest, −32 % forearc, −16 % backarc, ≤ 3 % interface and in-slab |
  | tapered, corner 9.6 | +0.003 / +1 % | same as the open line below Mw 8.5; free corner: interface 9.6 (lower bound only), in-slab 7.8 |
  | Aki–Utsu from 1976 | −0.001 / +5 % | interface b 0.914, N(≥ 7) +31 % |
  | Ogata–Katsura from 1976 | +0.001 / +4 % | fails (b 1.26–1.71; detection width 0.7–1.5) |
  | pooled b | error of b down by 20–65 % if the true b are equal, +15 % for the outer classes if not | between-unit variance zero in all families: segments 0.958, in-slab 1.159, crustal 0.980 |
  | least squares | +0.013 / −1 %, scatter × 2.4 | b 0.81–1.22 |

  Recommendation (options): keep Weichert on the table; give the source builders the truncated normalisation for the classes with Mmax = observed + 0.2; pooled b as an option for the interface segments only; table rule and its historical steps as a sensitivity case (FITS.md section 5).
- **Step 4 (final fits; `tables/fits_2026-11-15.csv`, FITS.md section 2).** b (sd), N(≥ 5), N(≥ 7): interface 0.962 (0.017), 25.2, 0.300; segments S to N 0.915, 0.996, 0.934, 0.973 with N(≥ 5) 2.94, 8.48, 7.41, 5.70; in-slab shallow 1.153 (0.037), 9.24, 0.046; intermediate 1.156 (0.027), 25.3, 0.123; Jujuy nest 1.236 (0.090), 3.74, 0.013; forearc 0.984 (0.059), 3.55, 0.038; arc 1.004 (0.099), 1.31, 0.013; backarc 0.987 (0.071), 2.30, 0.024; Patagonia with the forearc b, 0.640, 0.007. Same as B9 section 8. Covariance of (a, b), N(≥ 6) and N(≥ 8) with intervals, the interface (a, b) pairs at the 5th / ML / 95th percentile of the rate at Mw 8.8 (8.2 and 8.5 for the two northern segments), and the weight-1 fits are in the table.
- **Proposed lines for DECISIONS** (Pablo adds):
  - Statistics: "A historical step of the automatic table is kept only if it reaches at least 10 years before 1964 (15 Nov, B11)."
  - Statistics: "Final fits of 15 Nov: `fits/tables/fits_2026-11-15.csv`; the a and b are those of a likelihood cut at the Mmax of the class, so a truncated MFD is normalised to N(≥ 5), not cut from the open line."
  - Catalog (if accepted): "An Mw of quality D from the ISC-GEM Supplement is not used (23 events of Mw ≥ 5.0)."
- **Proposed lines for LEARNINGS:**
  - Completeness: "The automatic table was checked on synthetic margins (B11): the instrumental steps come out later than the truth in most catalogues (largest of two methods over regions and windows), the historical steps of Mw ≥ 7 30–75 years early; N(≥ 7) 6–14 % and N(≥ 8) 9–20 % low. Give a sensitivity fit with later historical steps."
  - b-value and rates: "Ogata–Katsura (joint Mc and b) fails on the catalogue from 1976 (b 1.3–1.7): below Mw 5 it is a mixture of regions and agencies, not one line times one detection curve."
  - b-value and rates: "The magnitude-error weight leaves N(≥ 5) about 2 % high (3–4 % on 1976–2026 alone) because small events have the larger σ; bootstrap intervals do not contain that bias."
  - b-value and rates: "A likelihood that keeps the empty bins above the largest event of a small class raises b by 0.03–0.06 (crustal classes, nest)."
  - Catalog pitfalls: "ISC-GEM quality D exists only in its Supplement (σ 0.7–2.3); check the file a value comes from."
  - Working: "Pool workers with numpy need `OMP_NUM_THREADS=1`; 14 workers without it took the machine to a load of 130."
- **Open questions for Pablo.**
  1. The brief calls the reference "unbounded GR" and DECISIONS puts the Mmax of the class in the likelihood. I took both: likelihood cut at Mmax, open line reported; the fit with no Mmax in the likelihood is a row of the sensitivity table. Is that the intended reading?
  2. Mmax of the in-slab classes uses the historical events (8.0 + 0.2); DECISIONS has this open.
  3. The interface branches are single bootstrap replicates (as psha_chile7); the 5th-percentile pair has the higher b. Keep, or take pairs along the (a, b) covariance?
  4. ISC-GEM Supplement quality D (above), and whether σ 0.5 for every Cabello value should stay a single default.
- **Commands** (from `psha_chile8/fits/`, conda `psha_renta`): `python run.py` (45 s; table, fits, sensitivity table, figures); `python sigma.py` (5 s); `OMP_NUM_THREADS=1 python compare.py` (about 10 min, 14 processes; synthetic tables; run before `run.py` if `figs/synthetic_methods.png` is to be redrawn); `pytest fits/tests` from `psha_chile8/` (15 s). All were run in full in this session.
- **PLAN:** B10 ticked, ← on B11 (not ticked: for Pablo). DATA.md: new section "Fit runs". FIGURES.md: six rows.
- **Suggested commit:**
  - `git add psha_chile8/fits psha_chile8/tasks/B11_fits.md psha_chile8/WORKLOG.md psha_chile8/PLAN.md psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/DECISIONS.md psha_chile8/catalog/REPORT_A3-A5.md psha_chile8/catalog/MAGNITUDES.md psha_chile8/catalog/RULES_LOCATION_MAGNITUDE.md psha_chile8/paper/CATALOG_SECTION_draft.md`
  - Message: `B11: fitting code with tests, GR fitting methods compared, final fits per class and interface segment; magnitude sigma report; B9 step-0 corrections applied to the catalogue documents`
  - `fits/tables/synth_methods_runs.csv` (0.5 MB) and `synth_table_runs.csv` are per-catalogue results; leave them out of the commit if only the summaries are wanted.

## 2026-11-15: B11 follow-up, tapered and truncated shapes, branches from the covariance (Claude Code)

After Pablo's reply to the four open questions of the B11 entry.

- **Pablo, 15 Nov:** the line is never open: tapered (preferred) or cut at Mmax, both kept until the tornado. Mmax probably observed + 0.2; a corner consistent with it wanted. Branches as correlated (a, b) pairs from the covariance; whether they stay is decided with the tornado. σ of the historical values: undecided, a referenced approach preferred.
- **Done.** `fits/run.py` fits every unit with both shapes (`SHAPES`), each by its own likelihood; `tables/fits_2026-11-15.csv` now has one row per unit and shape, with a in the convention of the shape (cut line: OpenQuake truncated Gutenberg–Richter; tapered: Kagan 2002), `rate_mlo`, and the branches. `fits/gr.py`: the tapered fit takes a fixed b (Patagonia); `a_value` per shape. `fits/compare.py` and `fits/figs.py` adapted (figures drawn on the tapered fit, the cut line dashed). `fits/FITS.md` sections 1 and 2 rewritten; sections 3–5 as before. 15 tests pass.
  - Corner: 9.6 for the interface; for the other classes the observed maximum, which has the moment rate of a line cut at observed + 0.2 (computed: 8.04 against 8.2 in-slab, 7.19 forearc, 7.26 nest, 7.70 arc, 7.49 backarc, 7.79 Patagonia). The whole interface margin now has Mmax 9.5 (it had none).
  - The two shapes give the same b (within 0.003; nest 0.010) and N(≥ 5); N(≥ 7) within 4 % (nest 9 %); N(≥ 8) tapered 2–15 % higher for the interface (37 % for segment 32–26° S) and 20 % lower for in-slab. Both fail the same two large-event checks.
  - Branches: the expected (a, b) at the 5th and 95th percentile of the rate at the controlling magnitude, from the bootstrap covariance (± 1.645 sd along it). Interface margin: (6.304, 0.991), (6.165, 0.962), (6.025, 0.934); rate at Mw 8.8 0.0041 / 0.0053 / 0.0068 per year.
- **σ of the historical values (not changed; needs a new catalogue version).** `magnitude.py` sets 0.5 for every Cabello value, but the source lists an uncertainty for all 104 values used before 1904 (CERESIS-GEM Mw): 0.2 for 27 of the 43 events of Mw ≥ 7, 0.6 for 15, 0.25 for one. Albini et al. (2014): historical magnitude uncertainty is inferred from the quality and number of sources or is the sd of the intensity regression. Which document sets the CERESIS-GEM values was not found. With the listed σ: interface N(≥ 7) +3 %, N(≥ 8) +4 %, b −0.005; shallow in-slab N(≥ 7) +6 %; the two check failures stay. Other models as in `explore/B9/MAG_ERROR_REFS.md` (not re-read).
- **Proposed lines for DECISIONS:**
  - Statistics: "The fitted line is never open: tapered (preferred) and cut at Mmax are both fitted and carried to the tornado (Pablo, 15 Nov)."
  - Statistics: "Corner of the tapered line: 9.6 for the interface; the observed maximum for the other classes, which has the moment rate of a line cut at observed + 0.2 (15 Nov, B11)."
  - Interface: "(a, b) branches are the expected pairs at the 5th and 95th percentile of the rate at the controlling magnitude, from the bootstrap covariance of (a, b) (15 Nov)."
  - Magnitudes (if accepted): "Historical values of Cabello et al. carry the uncertainty listed by their source (CERESIS-GEM), not a default of 0.5."
- **Open:** the σ of the historical values (above) and the ISC-GEM Supplement quality D; whether the tapered source MFD is also cut at Mmax; Kagan (2002) to add to `refs/` and check for the moment-equivalence of corner and cut.
- **Commands:** as the B11 entry (`python run.py` now 80 s). Same suggested commit; message `B11: fitting code with tests, GR methods compared, final fits per class and segment with tapered and truncated shapes; magnitude sigma report; B9 step-0 corrections`.

## 2026-11-15: B11 closed: decisions written, Kagan (2002) read, intermediate in-slab misfit located (Claude Code)

- **Pablo, 15 Nov:** σ of the Cabello values stays 0.5; the tapered line is not cut at Mmax; "update the documents with the decisions and learnings".
- **DECISIONS.md and LEARNINGS.md edited by Claude Code at Pablo's word**, against the usual rule of proposing only. DECISIONS: Magnitudes (σ 0.5 kept, ISC-GEM Supplement values kept); Statistics (estimator, the two shapes, corner rule, full catalogue, the 10-year rule of the table, where the fits are); Interface (tapered not cut, Mmax of the margin, branches from the covariance); In-slab and Crustal (Mmax values, corner); Superseded. LEARNINGS: Completeness (the table on synthetic margins); b-value and rates (methods compared, the two shapes, Ogata–Katsura, residual bias of the weight); In-slab (where the excess sits); Pitfalls (empty bins, open line above Mmax, cumulative plots, ISC-GEM quality D, Cabello's own uncertainty); Working (thread count).
- **Kagan (2002a, b)** read from `refs/catalogs/kagan_2002a.pdf`, `kagan_2002b.pdf`. 2002a section 2.2.4 is the tapered form of `fits/gr.py`. 2002b eq. 12 gives the maximum and corner moments of equal moment rate: corner = Mmax × (β / Γ(2 − β))^(1/(1 − β)) in moment; for b 1.15 that is 0.21 magnitude units below the cut, the same as our numerical 8.04 against 8.25 (upper edge of the 8.2 bin). His example: 8.35 against 8.10. Added to `REFERENCES.md` (section G), `fits/FITS.md` and DECISIONS. DOIs not on the pages, marked to check.
- **Declustering:** none anywhere in `fits/`. Table, fits, checks and bootstrap use all events; the synthetic catalogues are Poisson. Written into DECISIONS (Statistics) and FITS.md.
- **Intermediate in-slab misfit, per band and period inside the table** (weighted observed against fitted): Mw 7.0–7.4 in 1905–1963 10.3 / 5.5; Mw ≥ 7.5 8.8 / 1.7; Mw ≥ 7 from 1976 6.9 / 6.1; Mw 6.0–6.9 from 1976 85 / 84. The fit matches the modern record; the excess is all before 1964, and 19 of the 32 events of Mw ≥ 7 before 1976 are Abe mB values converted with Abe (1982). The points above the line at Mw 6.3–7.5 in the figure are the same excess seen through a cumulative plot. Also found: 1964–1975 is short at Mw 5.0–6.4 (110 / 173), not followed up.
- **PLAN:** B11 left unticked for Pablo. No new run: tables and figures are those of the follow-up entry above.
- **Suggested commit:** as the B11 entry, with `psha_chile8/LEARNINGS.md psha_chile8/REFERENCES.md` added.
- **Pablo, 15 Nov (later):** historical events count for the in-slab Mmax; the source MFDs will be evenly discretized in OpenQuake (bin rates from the fitted line, so the tapered line needs no upper magnitude from OpenQuake). DECISIONS (In-slab) and FITS.md updated. The observed maximum 8.0 comes from Santiago 1647 (shallow) and Calama 1950 (intermediate); Chillán 1939 is Mw 7.8 in the catalogue.


## 2026-11-15: C14, in-slab depth model (Claude Code)

- **Done.** `model/inslab/`: `depth.py` (inputs, Slab2 sampling, Riedel-Hornig reader, one-to-one matching, A7 depth rule for unclassed events, regions, bounds, bootstrap, cells, held-out check), `bench.py` (step 1), `run.py` (steps 2–4, settings at the top), `figs.py`; 8 tests in `model/inslab/tests/` pass (synthetic double zone recovered, weights sum to 1, hypocentres inside their layers, upper < hypocentres < lower on the cell table). Cell table `model/inslab/tables/depth_cells_2026-11-15.csv` (13 847 cells: lon, lat, top, thk, w1–w3, h1–h3, h_one, usd, lsd, layer bounds b1 b2, n_events, region, double-zone index, old psha_chile7 depths). Report `model/inslab/REPORT_C14.md`. Inputs copied to `data/` with `data/SHA256SUMS` (Riedel-Hornig, Slab2 dep / thk / unc, grid); `.gitignore` gains `data/riedel_hornig_*` and `data/*.xyz`.
- **Results.** Layers by slab-top region (≤ 50, 50–150, > 150 km), equal-count cut: 0–17.8–27.0–62.5, 0–13.2–25.1–42.0, 0–23.9–33.4–69.8 km below the top; inner bounds stable within 4 km under 2 000 resamples. 50 nearest events (held-out 2020–2021: −0.741 per event against −0.751 / −0.745 for 25 / 100, −0.844 for 50 km, −1.096 regional). Double zone: bottom-layer weight 0.34–0.36 at 20–24° S (index +0.10 to +0.16); one zone at 24–34° S; 34–40° S positive on few events. Mean hypocentre within −6 to +4 km of the old thickness-fraction depth in half the cells; lower depth median +7 km.
- **Benchmark.** Inside Chile Potin and ISC-EHB L1 agree with Riedel-Hornig within 2–4 km (spread 4–5); ISC is 12 km shallow at 0–70 km; CSN web spread 5–7. East of the Chile border every teleseismic depth is 10–50 km shallower than Riedel-Hornig, at all latitudes 22–34° S, growing eastward: their eastern events are too deep, as they say. Potin agrees with Riedel-Hornig there (−2 km), but both use Chilean stations only, so that is no test. Riedel-Hornig not recommended as a location source (report section 2).
- **Departures from the brief (for Pablo).** (1) Catalogue depths selected by source (Potin, ISC-EHB L1, GCCEL), not by listed σ ≤ 5 km: the listed σ is set per depth range, so the σ cut is a cut on depth (Potin then only at 30–70 km; median d 3.7 km against 22.6 for Riedel-Hornig over the same slab). `SELECT = "sigma"` gives the literal version. (2) Local-network depths left out east of the Chile border everywhere, not only under the flat slab (7 139 events, 5 662 of them in the flat slab); `POTIN_OUT = "flat"` gives the DECISIONS version. (3) Stability judged on the two inner bounds only: no scheme keeps the 97.5 % bound within 5 km in its small regions.
- **OpenQuake (3.26 installed source read):** ruptures centred on the hypocentre, width cut to the seismogenic range and length extended, then shifted vertically into [usd, lsd]; a large rupture fills the zone whatever layer its hypocentre is in. Collapsed point sources and the far-site approximation average the hypocentral depths (for C15).
- **Proposed lines for DECISIONS and LEARNINGS:** in `REPORT_C14.md` section 3 (four In-slab lines; two Pitfalls lines).
- **Open:** report section 4 (the two departures, central-Chile double zone not seen, jump of the lower depth at slab top 50 km, sparse south of 40° S, small events stand for large ones, Jujuy nest cells, low match rate at 26–28° S and south of 36° S).
- **Commands** (from `psha_chile8/model/inslab/`, conda `psha_renta`): `python bench.py` (25 s), `OMP_NUM_THREADS=4 python run.py` (about 6 min with the bootstrap; `REUSE_BOOT = True` reuses `tables/bounds_bootstrap.csv`, 2 min); `pytest model/inslab/tests` from `psha_chile8/`. All were run in this session (the final `run.py` with the bootstrap of the same event set reused).
- **PLAN:** C14 ticked (cell table exists, tests pass). DATA.md: three input rows and a new section "In-slab depth runs". FIGURES.md: four rows.
- **Suggested commit:**
  - `git add psha_chile8/model/inslab/*.py psha_chile8/model/inslab/tests psha_chile8/model/inslab/REPORT_C14.md psha_chile8/model/inslab/figs psha_chile8/model/inslab/tables/depth_cells_2026-11-15.csv psha_chile8/model/inslab/tables/rh_*.csv psha_chile8/model/inslab/tables/bounds_*.csv psha_chile8/model/inslab/tables/neighbours_heldout.csv psha_chile8/model/inslab/tables/choice.csv psha_chile8/model/inslab/tables/events_log.csv psha_chile8/model/inslab/tables/d_summary.csv psha_chile8/data/inslab_grid_01_2026-11-15.csv psha_chile8/data/SHA256SUMS psha_chile8/.gitignore psha_chile8/WORKLOG.md psha_chile8/PLAN.md psha_chile8/DATA.md psha_chile8/FIGURES.md`
  - Message: `C14: in-slab depth model, Riedel-Hornig benchmark, three layers below the slab top with weights and hypocentres per cell`
  - Leave out `tables/rh_matched.csv` (9 MB) and `tables/depth_events_2026-11-15.csv` (12 MB) if only summaries are wanted.

## 2026-11-15: D16 fault database, faults missing from GEM, Magallanes–Fagnano (Claude Code)

Brief `tasks/D16_fault_database.md`. Report `model/faults/REPORT_D16.md`, fields in `model/faults/FIELDS.md`.

- **Inputs frozen** in `data/` with sha256 in `data/SHA256SUMS`, rows in DATA.md (Other inputs): `crustal_faults_chile_updated_2026-11-15.*`, `crustal_faults_chile_2026-11-15.*`, `sara_active_faults_2026-11-15.*`, `chaf_pangea_v1_2026-11-15.*`.
- **Step 1, clean database** (`model/faults/db.py`): `data/faults/faults_2026-11-15.gpkg` (layer `faults`, EPSG:4326; the gpkg FID column is `gpkg_fid` so that our `fid` field is free) and `.csv`.
  - 160 rows, none removed.
  - The 156 GEM rows are identical to the SARA release, area-source fields and max_mag 0 of the Fagnano segments included. Only 4 rows were added by hand, and all four lie on CHAF strands (now `CHAF-100601`, `-300201`, `-300301`, `-300901`). Their old lengths were wrong (Bajo Molle 19 → 8.3 km).
  - Area-source fields removed. Dip from the source text: 124 rows change, 89 of them 87° → 90°.
  - Kinematics filled for 3 rows (AR-0005a assumed reverse).
  - sr_kind: class 140, range 15, measured 5.
  - 4 duplicate pairs flagged. Systems by rule for 113 rows.
- **Step 2** (`model/faults/chaf.py`):
  - At 2 km, 374 of 958 CHAF strands (40 % of the length) lie on GEM traces; 1 km 274, 5 km 535.
  - 10 of the 17 CHAF systems are absent from GEM.
  - San Ramón is not missing: CHAF's San Ramón strands lie on GEM's segment.
  - 146 missing faults, ranked by class and then by the median BSSA14 PGA at the most-affected city (`tables/missing_2026-11-15.csv`).
  - The top 20 add about 10 % to the moment rate of the GEM faults with the slip-rate rule "median GEM rate of the system". Several lie within 1–13 km of Iquique, Valparaíso, Pucón, Hornopirén and Puerto Aysén.
  - Literature for the top 20 in the report. Literature agents read the papers from the web; nothing was downloaded into the repo.
  - Map: `figs/gem_chaf_map.png`.
- **Step 3** (`model/faults/fagnano.py`):
  - AR-0056a overlaps CL-056c, d, e, i over 75–90 km, all in Chile. Proposed rule: each national database inside its own country (AR-0056a cut at the border, 174 → 55 km), 639 km of trace.
  - GPS slip rate 5.9 (4.4–6.8) mm/yr: Mendoza et al. 2015, Table 3; Mendoza et al. 2011. All GPS is east of 68.6° W.
  - Mmax: Leonard 2014 on the system area gives 8.10, WC94 8.17; observed 7.8 (1949, frozen catalogue).
  - One system source against 13 segments: N(≥ 6.5) 0.024 against 0.061 per yr; N(≥ 7) 0.0072 against 0.0059.
  - Puerto Williams: every SARA segment near the city is in the database. GEM's release lacks AR-0056c, e, f (ID gaps).
  - Figure: `figs/fagnano_segments.png`.
- **Tests:** `model/faults/tests/` (11), all pass.
- **Commands** (env `psha_renta`, from `psha_chile8/model/faults/`; all were run in this session):
  - `python db.py` (40 s)
  - `python chaf.py` (3 min)
  - `python fagnano.py` (10 s)
  - `pytest model/faults/tests` from `psha_chile8/`
  - Outside PyCharm, the shell needs `GDAL_DATA` and `PROJ_DATA` of the env (`conda activate psha_renta` sets them; calling the env's python directly does not).
- **Proposed DECISIONS lines:** see REPORT_D16.md section 4: fault database file, dip rule, no CHAF fault added this round, Fagnano territory rule, Fagnano slip rate 5.9 (4.4–6.8), one system source with Mmax 8.1.
- **Proposed LEARNINGS lines:**
  - Pitfalls / Source models: "The area-source fields and max_mag 0 of the old fault file come from GEM's SARA release itself; a fault file can carry values of another source type without a sign of it. Check every column of a database against what it describes (D16)."
  - Crustal and faults: "GEM traces are coarser than CHAF; the GEM–CHAF match depends on the distance (40 % of the CHAF length at 2 km, 56 % at 5 km) (D16)."
  - Crustal and faults: "140 of 160 GEM segments carry an activity-class slip rate (0.5 or 3.0 mm/yr), not a measured one; the Liquiñe–Ofqui master fault is measured at 14–19 mm/yr against 3.0 in the database (D16)."
- **Open questions:** REPORT_D16.md section 4, items 1–8. The main ones: the Liquiñe–Ofqui rates; the Fagnano rate in Chile (geology 8–16 mm/yr, no GPS); Fagnano dip and depth (GPS: 63–66° S, 11–15 km); keep 90° or GEM's 87°.
- **PLAN:** D16 ticked, ← on B13.
- **FIGURES.md:** two rows. **DATA.md:** four input rows and a "Fault database" section.
- **Suggested commit:**
  - `git add psha_chile8/model/faults psha_chile8/data/faults psha_chile8/data/crustal_faults_chile_updated_2026-11-15.* psha_chile8/data/crustal_faults_chile_2026-11-15.* psha_chile8/data/sara_active_faults_2026-11-15.* psha_chile8/data/chaf_pangea_v1_2026-11-15.* psha_chile8/data/SHA256SUMS psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`
  - Message: `D16: clean crustal fault database with sources per value, CHAF comparison and ranked missing faults, Magallanes-Fagnano overlap, GPS slip rate, Mmax and source options`
- **Pablo, 15 Nov (after D16):** keep 90° for vertical faults; adopt the territory rule for Magallanes–Fagnano; one Fagnano system source; Liquiñe–Ofqui keeps the GEM slip rates (CHAF gives a rate on 2 of its 379 LOFS strands: Liquiñe 20.4 ± 2.5 and 13.6 mm/yr, Escorial 23.8–28.6 mm/yr horizontal). Not yet in DECISIONS. Pending: the fault source may change to the "MASCSN" database inside Chile with GEM outside (to be clarified).
- **Pablo, 15 Nov (later): GEM base fixed in one go** (`db.py` rerun; 164 rows).
  - Magallanes–Fagnano territory cut applied in the database: AR-0056a 174 → 55 km; CL-056d 44.3 → 43.5 km.
  - Hand rows extended to all their CHAF strands: Marga Marga 8.3 → 34.6 km, Laguna Verde 6.7 → 23.4 km.
  - Added from CHAF as simplified traces (`geo.trace`), with dip 72 and 0.5 mm/yr (class 0.1–1) as the similar GEM forearc faults:
    - Mejillones, northern section (38.9 km; CL-049 already holds the southern 36 km of the Mejillones fault)
    - Valparaíso (52.0 km, dextral as in CHAF)
    - Quintay (47.9 km, normal and SW as its parallel neighbours)
    - Santa María (11.1 km, only the CHAF reverse strand "Santa Maria (SMFS)"; the other strands are short normal faults on the island)
  - Pichilemu (CL-003) and Zofri (CL-055) were already in GEM; the CHAF "missing" parts are a 15 km second Pichilemu strand and the separate Tarapacá fault.
  - Not added (Pablo): El Yolki, Lago Laja, Aroma, Pisagua, Paposo, Liquiñe–Ofqui branches.
  - Shapefiles for review: `data/faults/faults_gem_2026-11-15.shp` (156 GEM rows) and `data/faults/faults_gem_extra_2026-11-15.shp` (164 rows).
  - `chaf.py` and `fagnano.py` were not rerun; the missing-fault table predates the additions.

## 2026-11-15: C14 revised, kernel depth model (Claude Code)

Follows the C14 entry above; replaces its method and its departures list.

- **Pablo, 15 Nov:** zone per place from the slab top to the 95 % depth of the in-slab events (not the slab bottom); three layers inside it by a cheap smooth method; in-slab only; final catalogue depths, not per source; then: keep Riedel-Hornig inside Chile, for the depths only; instrumental period only; then, after the run with all final depths: drop ISC, CSN web and ComCat depths.
- **Done.** `depth.py`: kernel of the in-slab rate pattern (psha_chile7 settings: power 1.5, 25 neighbours, 5 km floor, 500 km) spreads every event's distance below the top onto the cells; `zone()` gives per cell the 95 % distance (lower depth), three equal layers, shares (+1 event per layer), medians, one-layer median. The region / bootstrap code of the first version is gone. `run.py` (`RUN = "2026-11-15c"`, `T_FROM = 1990`, `DROP`), `figs.py` (`maps_zone.png` replaces `maps_vs_old.png`, `hist_d_top.png` dropped), tests rewritten (8 pass). Frozen catalogue unchanged (checksums verified).
- **Results.** 30 150 catalogue events (Potin 28 097, ISC-EHB 2 046) and 40 654 Riedel-Hornig events. Zone 30–45 km below the top from 16 to 34° S; 60–90 km where events are few (south, shallow slab). Held-out 2020–2021: kernel −0.778 per event, 50 nearest −0.769, equal shares −1.099. Bottom layer heaviest at 20–22° S (lower plane of the northern double zone); one zone at 24–34° S; top layer heaviest south of 34° S. With ISC, CSN web and ComCat depths the lower depth is a median 6 km and in 5 % of cells 52 km deeper (sensitivity table). Report `model/inslab/REPORT_C14.md` rewritten (benchmark section unchanged).
- **Proposed DECISIONS and LEARNINGS lines:** `REPORT_C14.md` section 3 (they replace those of the entry above).
- **Open:** report section 4: sparse areas (thick zones and lower-depth spikes where few events; a floor on the effective number or a cap at the Slab2 bottom are the simple fixes), the northern upper plane falls in the middle third, central-Chile double zone not seen, small events stand for large ones, nest cells, Riedel-Hornig match rate in places.
- **Commands** (from `psha_chile8/model/inslab/`, conda `psha_renta`): `python bench.py` (25 s); `OMP_NUM_THREADS=8 python run.py` (about 8 min: model, held-out, all-depths sensitivity, figures); `pytest model/inslab/tests` from `psha_chile8/`. All run in this session.
- **Suggested commit** (replaces the one above):
  - `git add psha_chile8/model/inslab/*.py psha_chile8/model/inslab/tests psha_chile8/model/inslab/REPORT_C14.md psha_chile8/model/inslab/figs psha_chile8/model/inslab/tables/depth_cells_2026-11-15c.csv psha_chile8/model/inslab/tables/depth_cells_2026-11-15_v1.csv psha_chile8/model/inslab/tables/*_2026-11-15c.csv psha_chile8/model/inslab/tables/rh_*.csv psha_chile8/data/inslab_grid_01_2026-11-15.csv psha_chile8/data/SHA256SUMS psha_chile8/.gitignore psha_chile8/WORKLOG.md psha_chile8/PLAN.md psha_chile8/DATA.md psha_chile8/FIGURES.md`
  - Message: `C14: in-slab depth model (kernel, zone to the 95 % depth, three layers), Riedel-Hornig benchmark`
  - Leave out `tables/rh_matched.csv` (9 MB) and `tables/depth_events_2026-11-15c.csv` (8 MB) if only summaries are wanted.
- **Pablo, 15 Nov (later): GEM fault file final.**
  - Pablo edited `data/faults/faults_gem_extra_2026-11-15.shp` by hand. That edit is frozen untouched as `faults_gem_extra_pablo_2026-11-15.*` (sha256 in `data/SHA256SUMS`).
  - `model/faults/curate.py` rebuilds `faults_gem_extra_2026-11-15.shp` and `.csv` (152 faults) from it.
  - 12 removed (traces deleted): CL-044a, b, e, f (Chuculay), CL-051 Ordoñez, CL-050 Mititus, CL-040 Bolfín, CL-006mmm Los Palos, CL-006eee Punta Colas, PE-43a, PE-38, PE-47.
  - 4 traces edited, lengths recomputed: CL-006ddd 80.7 → 65.1 km, AR-0028a 36.4 → 6.4 km, Mejillones north 38.9 → 19.7 km, Valparaíso 52.0 → 33.2 km.
  - Magallanes–Fagnano slip rate set to 5.9 (4.4–6.8) mm/yr, from GPS (DECISIONS).
  - `db.py` no longer writes the extra shapefile, so a rerun cannot overwrite the edit.
  - Commands: `python db.py` (only if the inputs change) and then `python curate.py`.
  - This file is the fault input for B13.
- **Pablo, 15 Nov (later):** Las Peñas AR-0028a deleted (`REMOVE` in `curate.py`). **Final fault file: `data/faults/faults_gem_extra_2026-11-15.shp` / `.csv`, 151 faults** (143 GEM, 4 hand-added faults traced to CHAF, 4 added from CHAF). Written into REPORT_D16.md ("Final fault file"), FIELDS.md and DATA.md.
  - Proposed DECISIONS line (Crustal and faults): "Fault source: `data/faults/faults_gem_extra_2026-11-15.shp` (D16, 151 faults: GEM SARA cleaned and edited by Pablo, plus Bajo Molle, Marga Marga, Laguna Verde, Carranza, Mejillones north, Valparaíso, Quintay, Santa María); replaces the shapefile `crustal_faults_chile_updated` (15 Nov)."
  - Proposed DECISIONS lines (Magallanes–Fagnano): territory rule; slip rate 5.9 (4.4–6.8) mm/yr; one system source, Mmax 8.1.
  - Suggested commit: add `psha_chile8/model/faults/curate.py psha_chile8/data/faults/faults_gem_extra_2026-11-15.* psha_chile8/data/faults/faults_gem_extra_pablo_2026-11-15.* psha_chile8/data/faults/faults_gem_2026-11-15.*` to the D16 commit above.
- **Pablo, 15 Nov (later): second edit.**
  - 7 far Argentine faults removed: AR-0002a, AR-0050a, AR-0268a, AR-0005a, AR-0054a, AR-0350a, AR-0045b.
  - Frozen as `faults_gem_extra_pablo_2026-11-15b.*`; `curate.py` now reads it.
  - **Final file: 144 faults** (136 GEM, 4 hand-added faults traced to CHAF, 4 added from CHAF). REPORT_D16.md, FIELDS.md and DATA.md updated.
  - Edit `faults_gem_extra_pablo_2026-11-15b.shp` for further changes; `curate.py` overwrites `faults_gem_extra_2026-11-15.shp`.
- **Pablo, 15 Nov (later):** Magallanes–Fagnano strands beside the main trace deleted (CL-056e, f, g, h, i, j; `REMOVE` in `curate.py`).
  - **Final file: 138 faults.** Fagnano is 7 segments, 490 km.
  - Mmax of the system: Leonard 7.98 on the summed area, 8.00 on the end-to-end length 517 km. This replaces 8.1 in the proposed DECISIONS line.
  - Segments stay separate in the file; B13 joins them into one system source and bridges the 60 km gap between CL-056b and c.
- **DECISIONS.md edited by Claude Code at Pablo's word (15 Nov).**
  - Crustal and faults: fault source line replaced; three new lines (added faults, dip rule, Liquiñe–Ofqui rates).
  - Magallanes–Fagnano: the "to be checked" Mmax line replaced by trace, slip rate, one source and Mmax lines.
  - Superseded: fault source and Fagnano Mmax and slip rate.
  - LEARNINGS lines proposed above, not added.
  - Suggested commit for the whole D16 session:
    - `git add psha_chile8/model/faults psha_chile8/data/faults psha_chile8/data/*_2026-11-15.* psha_chile8/data/SHA256SUMS psha_chile8/DATA.md psha_chile8/DECISIONS.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`
    - `data/*_2026-11-15.*` also matches the C14 inputs of that date; check with `git status` first.
    - Message: `D16: clean crustal fault database, CHAF comparison, faults added and GEM file edited (138 faults), Magallanes-Fagnano trace, GPS slip rate, single source and Mmax`

## 2026-11-15: C14, lower depth capped at the Slab2 bottom (Claude Code)

- **Pablo, 15 Nov:** cap the lower depth at the Slab2 bottom, one clear rule; in-slab events thin out south of 36° S.
- **Done.** `depth.zone(..., cap=)`: lower depth = min(95 % distance below the top, Slab2 thickness); `run.py` passes the thickness (`RUN = "2026-11-15d"`); run `2026-11-15c` files deleted. 9 tests pass (new: cap respected on a synthetic slab and in the cell table).
- **Results.** 22 % of cells capped: none north of 22° S, 4–17 % at 22–34° S, 23–39 % at 34–42° S, 91 % south of 42° S; the isolated deep spikes are gone. Zone 30–45 km below the top at 16–34° S, 26–66 km farther south. Held-out unchanged (kernel −0.778, 50 nearest −0.770). With ISC, CSN web and ComCat back in, the lower depth is a median 5 km deeper (95 %: 40 km).
- **South of 36° S:** 1 054 events at 36–38° S, 445 at 38–42° S, 20 south of 42° S; the 500 km kernel lends the southern cells the depth shape of 33–36° S. Proposed for C15: one layer where the shape is borrowed, or accept it (report section 4.1).
- **Commands:** `OMP_NUM_THREADS=8 python run.py` from `model/inslab/` (about 8 min). Suggested commit as the entry above, with `*_2026-11-15d.csv` in place of `*_2026-11-15c.csv`.

## 2026-11-15: C14, zone as a fraction of the Slab2 thickness (Claude Code)

- **Pablo, 15 Nov:** the Slab2 bottom is too deep for the seismogenic depth; use the 95 % of all in-slab seismicity as a fraction of the slab thickness, then the three layers. Asked to check whether the fraction is representative and whether Chillán 1939 and Tarapacá 2005 fit.
- **Done.** `depth.fraction()` (weighted 95 % of d / thickness), `depth.zone(..., lsd=)` takes the lower depth per cell; `run.py` computes the fraction from the event set (`RUN = "2026-11-15e"`); cell table without `b1`, `b2` (the slices are thirds of the zone); run `2026-11-15d` files deleted; figure `maps_zone.png` redrawn (zone, mean and one-layer hypocentre against psha_chile7). 9 tests pass.
- **Results.** Fraction 0.4746 (catalogue 0.475, Riedel-Hornig 0.474; 0.46–0.50 in every 2° band 16–36° S; 0.49–0.55 across magnitudes up to Mw ≥ 6.5; 0.45–0.56 across periods; with ISC, CSN web and ComCat it would be 0.615). Zone 40 km below the top in the north, 30–35 km at 30–40° S, 19–28 km south of 40° S; 4–15 km shallower than the old 0.65 rule. Held-out: kernel −0.794, 50 nearest −0.784, equal −1.099. 16 of 17 in-slab events of Mw ≥ 6.9 since 1964 inside the zone; Tarapacá 2005 rupture (90–115 km) inside its zone (85–125 km); Chillán 1939 (80–100 km in Beck et al. 1998) up to 9 km below its zone (59–91 km). Rupture extents from search summaries only; papers not in `refs/`.
- **Report** `model/inslab/REPORT_C14.md` sections 1, 3 and 4 rewritten (benchmark unchanged); proposed DECISIONS and LEARNINGS lines in section 3 replace those of the earlier C14 entries.
- **Open:** report section 4 (south of 36° S borrows the depth shape; events below the zone at 22–26° S; Chillán to read; northern upper plane in the middle slice; central-Chile double zone; nest cells; Riedel-Hornig match rates). Add Beck et al. (1998), Peyrat et al. (2006), Delouis and Legrand (2007), Kuge et al. (2010) to `refs/`.
- **Commands:** `OMP_NUM_THREADS=8 python run.py` from `model/inslab/` (about 8 min); `pytest model/inslab/tests` from `psha_chile8/`. Suggested commit as the C14 entries above, with `*_2026-11-15e.csv` in place of the `c` / `d` tables.

## 2026-11-15: D16b fault database B (MASCSN26 + GEM outside Chile), A against B (Claude Code)
- **Done.** Brief `tasks/D16b_fault_options.md`; database A = `data/faults/faults_gem_extra_2026-11-15.shp` (138 faults; it already had its DATA.md row 2026-11-15e, its sha256 now added to `data/SHA256SUMS`). Code in `model/faults/`: `mascsn.py` (step 1), `dbB.py` (step 2), `rates.py` (fault MFDs with our rules, six shapes ported from psha_chile7), `compare.py` (step 3), `figs_b.py`; tests `tests/test_d16b.py` (45 pass in `model/faults/tests`). Report `model/faults/REPORT_D16b.md`; fields of B in `FIELDS.md`; inputs (MASCSN XMLs, report PDF, Chile outline copied as `data/chile_outline_2026-11-15.*`) and database B in DATA.md; two figures in FIGURES.md.
- **Step 1.** `minMag` is the first bin centre (OpenQuake `EvenlyDiscretizedMFD`); M0 constant 9.05. Mmax 6.1–7.6, b 0.88–1.36 (four of them MASCSN zone b of Table 35). Closure exact (5e-14); SCC 0.5 = 0.5 × SCC 1 exactly. Against Table 17: E–W 0.65 (1.62 ×), Atacama 8–12 × too high, Liquiñe–Ofqui 51 of 65 below 4 mm/yr, Magallanes all below 6. MASCSN's moment does not scale with trace length (four Magallanes traces 79–311 km carry the same moment; Liquiñe–Ofqui plateaus beyond ~28 km). Reported, not corrected.
- **Step 2.** `data/faults/faults_B_2026-11-15.gpkg` / `.csv`: 166 faults, 129 MASCSN (5 823 km) + 37 GEM AR/PE (1 205 km), none dropped by overlap. Knokeke dropped, Deseado and 722 cut at the border. Fagnano main trace in B = MASCSN 726, 721, 720 + AR-0056a, b, d, g (494 km), GPS 5.9 mm/yr; MASCSN side traces 722, Bahía Indio, Río San Juan keep MASCSN slip (open).
- **Step 3.** Fault N(≥ 6) / tapered fit: forearc A 0.17, B 0.52; arc A 3.3, B 4.7; backarc 0.21 both; Patagonia A 1.3, B 1.8; domain A 0.79, B 1.21 (B as published 1.10). Cities: Concepción × 54 in B (Santa María at 4 mm/yr), Valparaíso × 0.35, Puerto Montt × 3.7, Puerto Williams unchanged.
- **Decision taken here (Pablo to confirm):** fault depth weights 10 / 20 km 0.5 / 0.5 (not in DECISIONS); fault Mmax on the 0.1 grid = the bin holding the Leonard value, at least 6.0.
- **Proposed DECISIONS lines:** `REPORT_D16b.md` section 3 (database B; restored slip used as given; Fagnano main trace in B and the side traces; depth weights).
- **Proposed LEARNINGS line (Pitfalls, Source models):** "A slip rate restored from a published moment rate is only as good as the moment convention of that model: MASCSN26 closes exactly but does not balance moment on trace length × width (constant moment on long traces), so its restored slips are model values, not measurements (D16b)."
- **Open:** arc bulge (faults 3–5 × the arc fit) for B13; Magallanes side traces in B; Santa María 4 mm/yr and El Yolki 8.3 mm/yr in B; MASCSN zone b against our class b.
- **Commands** (from `psha_chile8/model/faults/`, conda `psha_renta`; all run in this session): `python mascsn.py` (30 s), `python dbB.py` (20 s), `python compare.py` (25 s); `pytest model/faults/tests` from `psha_chile8/`.
- **Suggested commit:**
  - `git add psha_chile8/model/faults/{mascsn,dbB,rates,compare,figs_b}.py psha_chile8/model/faults/tests/test_d16b.py psha_chile8/model/faults/REPORT_D16b.md psha_chile8/model/faults/FIELDS.md psha_chile8/model/faults/tables/{mascsn,d16b,dbB}_*2026-11-15.csv psha_chile8/model/faults/figs/{mascsn_slip_systems,faults_A_B_map}.png psha_chile8/data/faults/faults_B_2026-11-15.* psha_chile8/data/faults/mascsn26 psha_chile8/data/chile_outline_2026-11-15.* psha_chile8/data/SHA256SUMS psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`
  - Message: `D16b: MASCSN26 slip and Mmax restored from its NRML, fault database B, A against B per class and near the cities`

## 2026-11-15: C14 closed (Claude Code)

- PLAN: C14 ticked (cell table `model/inslab/tables/depth_cells_2026-11-15e.csv` exists, 9 tests pass), its ← removed.
- **Commit for C14** (replaces the suggestions of the C14 entries above; `DATA.md`, `FIGURES.md`, `PLAN.md`, `WORKLOG.md` also hold edits of the B13 / D16 sessions; `data/SHA256SUMS` already holds the C14 inputs since commit c0bf82a, its current diff is D16b's):
  - `git add psha_chile8/model/inslab/*.py psha_chile8/model/inslab/tests/test_depth.py psha_chile8/model/inslab/REPORT_C14.md psha_chile8/model/inslab/figs/*.png psha_chile8/model/inslab/tables/rh_*.csv psha_chile8/model/inslab/tables/*_2026-11-15e.csv psha_chile8/model/inslab/tables/depth_cells_2026-11-15_v1.csv psha_chile8/data/inslab_grid_01_2026-11-15.csv psha_chile8/.gitignore psha_chile8/PLAN.md psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`
  - Optional to leave out (large, rebuilt by the scripts): `tables/rh_matched.csv` (9 MB), `tables/depth_events_2026-11-15e.csv` (8 MB).
  - Message: `C14: in-slab depth model. Riedel-Hornig benchmark; zone from the Slab2 top to 0.475 of the slab thickness; three-slice hypocentre distribution from kernel-smoothed depths`

## 2026-11-15: B12 declustered catalogues and their fits; step 0 refit with one Mmax rule (Claude Code)
- **Step 0 (done first, for S1).** `gr.kagan_corner` (Kagan 2002b, eq. 12); `run.py`: interface Mmax 9.7 / 9.7 / 9.3 / 8.7 / 9.0, corner from Mmax and the unit's cut-line b everywhere, `DATE = "2026-11-15b"`. Test `fits/tests/test_corner.py` (tapered moment rate = cut-line moment rate within 1 %). New table `fits/tables/fits_2026-11-15b.csv` (old kept); `fits_sensitivity_2026-11-15b.csv` and the B11 figures in `fits/figs/` redrawn on it. `FITS.md` section 7: interface corners 9.10–9.48, b and N(≥ 7) within 0.01 and 5 %; N(≥ 8) of segment 32–26° S tapered −19 %; the two known failures stay.
- **For S1:** `gr.rates` stops at Mw 9.7; the tapered margin and the 45.6–37° S segment hold 6 % of their moment rate above Mw 9.75. Extend the grid when writing the lists, or raise `MTOP` (not done: it also changes the empty bins of the open-line sensitivity fits).
- **Step 1.** `fits/decluster.py` (B9 code in house style); tests `fits/tests/test_decluster.py` (8). Four catalogues in `catalog/declustered/` (gk, gk_family, nn, nn_depth; also from Mw 3.5 for the completeness rule), rows in DATA.md. B9 reproduced (kept 36 % / 71 %, threshold −5.52).
  - The brief's test "mainshock count within 5 %" passes for Gardner–Knopoff on sparse synthetic catalogues. Nearest neighbour passes it only with a threshold in the gap between the modes; with the B9 mixture threshold it takes 5–15 % of the mainshocks as clustered. The test records that bias; the setting was not changed. At real density every method loses 3–11 % of the mainshocks.
  - **Finding:** nearest neighbour (B9 settings) removes great mainshocks: Valdivia 1960, 1751, 1877, 1922, 1985, Iquique 2014 (it keeps foreshocks or events decades earlier).
- **Step 2.** Declustered completeness tables: instrumental steps unchanged (5.1 from 1964 instead of 5.2), historical steps up to 80 years earlier (6.0 from 1950, 6.5 from 1890–1900, 7.0 from 1825–1830), because the rate rule is one-sided. Both fits reported (column `table`); recommended: the full-catalogue table.
- **Steps 3–4.** `fits/run_declustered.py` (run.py and gr.py unchanged; Mmax from the full catalogue; interface shared b as the random-effects mean of the segment b, per bootstrap replicate) → `fits/tables/fits_declustered_2026-11-15.csv` and comparison tables; figures `fits/figs/declustered_{fmd,b_floor,N7}.png` (FIGURES.md). Interface b full 0.96, gk 0.74, gk_family 0.77, nn 0.93; rate at Mw 8.8 × 1.6 (gk) and × 0.57 (nn); Fano at Mw ≥ 5.0 from 1976: 58 full, 1.1–1.2 gk, 1.9–2.0 nn. Gardner–Knopoff passes the large-event check everywhere, including the two units that fail on the full catalogue.
- **Step 5, recommendation** (`fits/DECLUSTER.md` section 3): interface rate branch gk_family on the full table; in-slab pattern nn; crustal pattern gk_family (the only catalogue that respects "no removal of crustal events after interface mainshocks"; gk and nn take 57–68 % of their crustal removals from interface or in-slab parents).
- **Proposed DECISIONS lines:** `fits/DECLUSTER.md` section 4 (interface declustered branch; declustered fits on the full table; in-slab and crustal pattern catalogues; superseded Uhrhammer suggestion).
- **Proposed LEARNINGS lines (Declustering):** DECLUSTER.md section 4 (nearest neighbour removes great mainshocks; the Gardner–Knopoff interface b has a plateau on the full table; the mixture threshold takes 5–15 % of the background).
- **Open:** nearest neighbour per family, or keeping the largest event of each cluster, and Uhrhammer windows, if Pablo wants them before choosing. Does the DECISIONS line on crustal events after interface mainshocks apply to the pattern? I read it so.
- **Commands** (from `psha_chile8/fits/`, conda `psha_renta`; all run in this session): `python run.py` (95 s), `python decluster.py` (about 3 min), `OMP_NUM_THREADS=1 python run_declustered.py` (a few minutes), `python figs_declustered.py` (figures only); `pytest fits/tests` from `psha_chile8/` (29 pass).
- **Suggested commit:**
  - `git add psha_chile8/fits/{gr,run,figs,decluster,run_declustered,figs_declustered}.py psha_chile8/fits/tests/{test_corner,test_decluster}.py psha_chile8/fits/FITS.md psha_chile8/fits/DECLUSTER.md psha_chile8/fits/tables/{fits,fits_sensitivity}_2026-11-15b.csv psha_chile8/fits/tables/*declustered*_2026-11-15.csv psha_chile8/fits/figs psha_chile8/catalog/declustered psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`
  - Message: `B12: one Mmax rule and Kagan corner refit (fits_2026-11-15b), declustered catalogues (Gardner-Knopoff, nearest neighbour, two variants) and their fits with the B11 code`

## 2026-11-15: B12 revised, declustering as one factor with two options (Claude Code)
- **Pablo, 15 Nov:** Gardner–Knopoff and nearest neighbour as two branches, each consistent across families (not a different method per purpose, as the entry above recommended).
- **Done.** `decluster.py`: nearest neighbour per family (proximities inside each family, one mixture threshold on all of them, −5.75) and the largest event of each cluster kept (`nn_clusters(..., m)`), method `nn_family`; 2 new tests (10 in `test_decluster.py`, 31 in `fits/tests`). Catalogues `catalog/declustered/nn_family_2026-11-15.csv` and `_m35_` (DATA.md). `run_declustered.py` rerun with six methods; tables and figures overwritten. `fits/DECLUSTER.md` rewritten around the factor.
- **Results.** nn_family keeps 77 % of the events; it now keeps Valdivia 1960, 1877, 1922 and Iquique 2014. Two links across decades remain (1657 into 1751, 1975 into 1960), reported, not patched. Interface b: full 0.96, gk_family 0.77, nn_family 0.90. Rate at Mw 8.8: full 0.0051, gk_family 0.0078, nn_family 0.0042: the two options bracket the full catalogue. In-slab pattern from 53 % (GK) or 96 % (NN) of the intermediate events, 12 % or 91 % of the nest.
- **Proposed DECISIONS lines:** `fits/DECLUSTER.md` section 4 (the factor, both per family, 0.5 / 0.5 until the tornado; declustered fits on the full table and Mmax; Uhrhammer suggestion superseded). These replace the lines proposed in the entry above.
- **Commands:** `python decluster.py` (about 4 min, all methods), `OMP_NUM_THREADS=1 python run_declustered.py` (2.5 min) from `fits/`; `pytest fits/tests` from `psha_chile8/`.
- **Suggested commit:** as the entry above (the same paths cover the new files).
- **DECISIONS.md edited by Claude Code at Pablo's word (15 Nov):** Statistics, two lines (the declustering factor; declustered fits on the full table and Mmax); Superseded, one line (Uhrhammer suggestion); the line "Fits of 15 Nov" now names `fits_2026-11-15b.csv`. The LEARNINGS lines of `fits/DECLUSTER.md` section 4 are still only proposed.

## 2026-11-15: D16b revised, MASCSN26 method identified (FaultQuake) and fault model rebuilt (Claude Code)
- **Why.** Pablo: the aim was to rebuild MASCSN's fault model from its OpenQuake files, i.e. find how the bin rates were made from slip rates (Mmin, Mmax). The first version assumed moment = μ × trace length × 12 km × slip; it closed only by construction.
- **Found.** The report has no per-fault data (Appendix C lists field names, Appendix D repeats Table 17). The rates are FaultQuake output (Tavakolizadeh et al. 2024; code github.com/GeoSignalAnalysis/FaultQuake, main, read through a fetch agent): Tmean = M0(Mmax) / (μ V min(L, LAR) T / sin dip) rounded to whole years, M0 constant 9.1, truncated GR on the points 6.0..Mmax (bin lower edges) balanced to M0(Mmax) / Tmean; Mmax = mode of the conflated scaling-relation pdfs rounded to 0.1. Proof: M0(Mmax) / moment rate is a whole number for all 130 sources (1e-9), FaultQuake rebuilds every rate to 7e-14. SCC 0.5 file = SCC 1 halved. `minMag` 6.0 is FaultQuake's lower bin edge, read by OpenQuake as a centre: MASCSN runs 0.05 low.
- **Done.** `model/faults/faultquake.py` (port: `mmax`, `lar`, `tmean`, `rates`); `mascsn.py` rewritten (restore Tmean, invert per fault for WC94 kind, thickness T, slip V; forward FaultQuake check; rebuilt NRML for SCC 1 / 0.75 / 0.5 in `model/faults/nrml/`); `dbB.py` carries the FaultQuake slip and `t_fq`, `scr_fq`, `tmean_fq`, `fq_how`; tests rewritten (48 pass). Report `model/faults/REPORT_D16b.md` rewritten; FIELDS.md, DATA.md (row 2026-11-15b) updated.
- **Results.** Inputs: 82 sources exact and capped (slip and thickness fixed), 7 exact, 35 with the system thickness (slip × thickness fixed), 6 tolerant. Forward run: Mmax 130 / 130, Tmean exact 101, rates within 2 % all. Liquiñe–Ofqui 12 km, 7.0 mm/yr on the master faults, 2.0 on secondary; Magallanes 15 km, 6.5; Atacama 23 km, ~0.5; Transversales Noroeste 20 km, 0.4; San Ramón 15 km, 0.6; E–W only V × T ≈ 8.7 (0.29 at 30 km). With these slips, B with our rules has fault N(≥ 6) / fit: arc 8.8, Patagonia 3.6, domain 2.0 (B as published 4.2, 1.8, 1.1; A 3.3, 1.3, 0.79).
- **Proposed DECISIONS lines:** report section 3.
- **Proposed LEARNINGS line (Source models):** "A published fault model can hide its moment convention: MASCSN26 (FaultQuake) caps the length at the aspect-ratio length, uses a database thickness, M0 constant 9.1 and bin lower edges. Identify the generating code (integer Tmean was the fingerprint) before restoring slip rates (D16b)."
- **Open:** our rules on B spread MASCSN slips over the whole trace (2.4 × MASCSN's moment); Magallanes strand 722 at 6.5 mm/yr in B (double counts the GPS rate); arc bulge; slip of faults below the cap depends on T; half-bin shift of the published model. The comparison uses `fits/tables/fits_2026-11-15.csv` as the brief says; another session now names `fits_2026-11-15b.csv` as current, so rerun `compare.py` with `FITS` changed if that table is the one for B13.
- **Commands** (from `psha_chile8/model/faults/`): `python mascsn.py` (1 min), `python dbB.py`, `python compare.py`; `pytest model/faults/tests` from `psha_chile8/`. All run in this session.
- **Suggested commit** (with or after the D16b commit above): `git add psha_chile8/model/faults/{faultquake,mascsn,dbB,compare,figs_b}.py psha_chile8/model/faults/tests/test_d16b.py psha_chile8/model/faults/nrml psha_chile8/model/faults/REPORT_D16b.md psha_chile8/model/faults/FIELDS.md psha_chile8/model/faults/tables/{mascsn,d16b,dbB}_*2026-11-15.csv psha_chile8/model/faults/figs/{mascsn_slip_systems,faults_A_B_map}.png psha_chile8/data/faults/faults_B_2026-11-15.* psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `D16b: MASCSN26 fault sources identified as FaultQuake output, inputs restored per fault, model rebuilt (SCC 1/0.75/0.5), database B with FaultQuake slip rates`

## 2026-11-15: D16b, MASCSN-moment variant of database B (Claude Code)
- **Pablo:** add a variant of B with the MASCSN moment.
- **Done.** `compare.budget` (MASCSN FaultQuake budget per fault: μ slip min(L, LAR) T / sin dip, their T and scaling relation, trace as kept in B) and `rates.source(fixed=, Lsr=)` (a fixed moment in every depth branch, times ψ). Variant "B, MASCSN moment, our MFD rules": our Mmax, shapes, class b and ψ on that moment; GEM rows and the Argentine Fagnano traces with our rules; Magallanes main trace at the GPS rate. Columns in `tables/d16b_class_table_`, `d16b_sources_` (N6_mm), `d16b_cities_` (B_mm). Two new tests (50 pass).
- **Bug fixed:** `dbB.py` wrote `x.T` (pandas transpose) into `t_fq`; now `x["T"]`, with a test that `t_fq` is a thickness. `faults_B_2026-11-15.gpkg` / `.csv` rewritten.
- **Results** (fault N(≥ 6) / tapered fit): arc 4.6 (our rules 8.8, published 4.2, A 3.3); Patagonia 1.4; domain 1.16 (published 1.10, our rules 2.0, A 0.79). The doubling under plain our rules is the MASCSN length cap and thickness, not the MFD rules. Puerto Williams 0.027 with the MASCSN budget (each Magallanes trace capped at 37.6 km).
- **Proposed DECISIONS line:** "Database B is run in B13 in two variants: our rules, and our MFD rules on the MASCSN moment budget (Pablo, 15 Nov)." Report `REPORT_D16b.md` updated (section 2 table and cities, section 3).
- **For B13:** run B twice; the per-source rates of the variant come from `compare.sources(b, bb, mm=True)` (column `mm`).
- **Commands:** `python dbB.py`, `python compare.py` from `model/faults/`; `pytest model/faults/tests`. Run in this session.
- **Suggested commit:** add `psha_chile8/model/faults/{rates,compare,dbB}.py psha_chile8/model/faults/tests/test_d16b.py psha_chile8/model/faults/REPORT_D16b.md psha_chile8/model/faults/tables/d16b_*_2026-11-15.csv psha_chile8/data/faults/faults_B_2026-11-15.* psha_chile8/WORKLOG.md` to the D16b commit.

## 2026-11-15: D16b, Pablo's answers (Claude Code)
- **Decided (Pablo):** B13 runs database B in two variants (our rules; our MFD rules on the MASCSN moment budget). The MASCSN Magallanes parallel trace 722 and the splays Bahía Indio and Río San Juan stay in B as MASCSN has them (6.5 and 1.0 mm/yr). B13 is a separate task, not started.
- **MASCSN weights (for the MASCSN variant):** MASCSN's fault branch is SCC 1.0 / 0.75 / 0.5 with weights 0.25 / 0.5 / 0.25 (Figure 74, p. 129); nothing else is branched (0–12 km, one Mmax, one truncated GR, zone b). Our ψ 0.6 / 0.8 / 1.0 (0.25 / 0.5 / 0.25) takes the place of SCC in the variant. The 10 / 20 km depth weights 0.5 / 0.5 are ours (A and B with our rules), not MASCSN's; still to be written into DECISIONS.
- **Fits table:** `compare.py` now reads `fits/tables/fits_2026-11-15b.csv` (current); the brief named `fits_2026-11-15.csv`. Crustal rates and b differ by less than 0.2 %; every fault / fit ratio is unchanged to two decimals. Tables rerun.
- **Proposed DECISIONS lines:** `model/faults/REPORT_D16b.md` section 3 (updated with these answers).
- **DECISIONS.md edited by Claude Code at Pablo's word (15 Nov):** Crustal and faults, the fault depth line now reads "10 / 20 km, weights 0.5 / 0.5 (Pablo, 15 Nov) …; MASCSN26 has no depth branch". Add `psha_chile8/DECISIONS.md` to the D16b commit.
