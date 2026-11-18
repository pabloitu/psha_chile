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
- **DECISIONS.md edited by Claude Code at Pablo's word (15 Nov):** Crustal and faults, join line: "the smoothed background (SSM) GR line and the fault traces are mixed, with no 3-D volume around the faults (no taper by 3-D distance from the fault surface)"; replaces the 12 km 3-D taper. The B13 brief (`tasks/B13_faults_background.md`, step 4 and the zone in step 1) still describes the 3-D taper and needs updating before B13 starts.

## 2026-11-15: S1 interface source model (Claude Code)
- **Done.** `model/interface/`: `geom.py`, `mfd.py`, `nrml.py`, `build.py` (entry, settings at the top), `figs.py`, `oqcheck.py`, `tests/test_interface.py` (10 pass). Report `model/interface/REPORT_S1.md`. Geometry on the Slab2 top 10–50 km (edges follow the depth contours; psha_chile7 used straight lines), margin 45.1–17.6° S 438 325 km², segments tile it to 2e-8; Antarctic plane 58 203 km². 240 NRML files (geometry × convention full / gk_family / nn_family × b option × shape × (a, b) × seismic / geodetic χ), `nrml/branches.json`, `nrml/source_lt_interface.xml` (72 files × Strasser / Thingbaijam by `setMSRAbsolute` = 144 paths). Inputs copied dated: `data/sam_nazca_trench_2026-11-15.*`, `data/pb2002_antarctic_trench_2026-11-15.geojson` (DATA.md, SHA256SUMS).
- **Fits.** `fits_2026-11-15b.csv` (own b); `fits_declustered_2026-11-15.csv` table full (shared b of the full catalogue was there as method `full`; gk_family and nn_family own / shared). The segment fits with the margin b were not in any table: computed with `fits/run.py` as B12's shared b, `model/interface/tables/fits_marginb_2026-11-15.csv`. `fits/` unchanged.
- **Choices made (for Pablo to confirm):** reference tree = tapered shape and own b (DECISIONS gives no weights to these tornado factors; the other 168 files have weight 0); "b of the margin fit" = segment rates refitted with b fixed at the margin b; Antarctic b = 45.6–37° S b of the same branch, and the scaling branch applies to it too; μ 30 GPa (psha_chile7); sources from Mw 5.5 (psha_chile7 `mmin55`), interface distance 600 km.
- **Conflict found (brief against DECISIONS):** the brief ends the tapered list where the rupture area reaches the source area; DECISIONS says about one unit above the corner. The area point lies at or below Mmax in every Nazca source (margin 9.41–9.58, 45.6–37° S 8.83–9.00), and 2–70 % of the moment lies above it, not under 1 %. OpenQuake (installed hazardlib, `complex_fault._float_ruptures`) turns such a rupture into one rupture over the whole surface with its magnitude and rate. Lists built with the DECISIONS end; proposed rule in the report, section 4.
- **Results.** Seismic closure (seismic moment / μ A v): margin 0.59, segments 0.36 / 0.50 / 0.28 / 0.17 (full catalogue). Tree mean N(≥ 8): margin 0.036, segments 0.058 per year. Both OpenQuake check jobs (one site, AG20, PGA 475 yr; calc 496 margin 4 min 46 s, calc 497 segments 9 min 44 s) read all 240 files; OpenQuake rates per source equal the tables (≤ 2.4e-6).
- **Environment:** the engine is 3.27.0-git c9cefc797f, not 3.26; `oq` needs `PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine` (stale editable install, `openquake.pfd` missing); fix with `pip install -e /data/PyCharmProjects/psha_renta/oq-engine` in psha_renta. GDAL data of psha_renta broken: `model/faults/tests` give 1 failure and 8 errors (not S1).
- **Proposed DECISIONS lines (Interface):** "Interface sources: one NRML file per branch, reference tree tapered with own b; cut line and shared / margin b options written for the tornado (S1, 15 Nov)." "Scaling relation as a setMSRAbsolute level, applied to every interface source, the Antarctic one included." "List end: the tapered list runs one unit above the corner; above the magnitude whose median area fills the source, OpenQuake uses one whole-surface rupture with the full magnitude and rate (stated, not cut)" (if Pablo accepts the proposal).
- **Proposed LEARNINGS line (Source models):** "Interface segment areas are filled by ruptures 0.2–0.9 units below Mmax (Strasser / Thingbaijam); an end of the MFD at the area would remove most of the moment of the southern segments. OpenQuake keeps magnitude and rate on a whole-surface rupture (S1)."
- **Commands** (from `psha_chile8/model/interface/`, PYTHONPATH as above): `python build.py` (10 s), `python oqcheck.py` (writes the jobs, compares; set `CALCS`), the jobs: `cd oqcheck && oq engine --run job_margin.ini` and `job_seg.ini`; `pytest model/interface/tests` from `psha_chile8/`. All run in this session.
- **Full city run for Pablo** (14 cities, S5 will merge): copy `nrml/source_lt_interface.xml` into the job folder next to the 72 tree files (paths are bare file names relative to `nrml/`), GMM tree of DECISIONS (AG20, Parker SA_S, Kuehn, Montalva, 0.25 each), Vs30 800 inferred, Z1.0 40 m, Z2.5 0.6 km, truncation 3, `maximum_distance = {"Subduction Interface": 600.0}`, `complex_fault_mesh_spacing = 10`, PGA and the SA set, poes 0.1 (and 0.02 in the final run): `oq engine --run job.ini` from `nrml/` (576 realizations).
- **Open:** list end rule; weights of shape and b option if they stay branches; southern gap 45.6–45.1° S (Slab2 too shallow); geodetic segment branches 3–5× the seismic rates at 32–17.6° S; declustered segments against the declustered margin not tested. DECISIONS re-read before finishing: the Interface and Statistics lines used here did not change during the session.
- **Suggested commit:** `git add psha_chile8/model/interface/{geom,mfd,nrml,build,figs,oqcheck}.py psha_chile8/model/interface/tests psha_chile8/model/interface/REPORT_S1.md psha_chile8/model/interface/{geometry,tables,figs,nrml} psha_chile8/model/interface/oqcheck/*.{ini,xml} psha_chile8/data/sam_nazca_trench_2026-11-15.* psha_chile8/data/pb2002_antarctic_trench_2026-11-15.geojson psha_chile8/data/SHA256SUMS psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `S1: interface source model, 240 NRML branch files (margin and segments, full and declustered, three b options, two shapes, (a, b), seismic and geodetic), Antarctic interface, logic-tree fragment, OpenQuake check`

## 2026-11-15: S1, end of the tapered list (Claude Code)
- **Pablo:** "one unit above the corner" (10.5 for the margin) is too far; choose a reasonable end.
- **Chosen:** the tapered list ends at Mmax + 0.2 and its last bin carries the rate of the line above it. Because the Kagan corner sits a fixed distance below Mmax, the share of moment above Mmax + 0.2 is the same in every unit, 0.56–0.65 % (Mmax + 0.1: 2.3–2.5 %; Mmax: 6.3 %). With the tail in the last bin, N(≥ M) of the list equals the fitted line at every edge, and the list keeps 99.8 % of the tapered moment. The geodetic branches are scaled on the written list, so they stay exact. Interface rates changed by under 0.2 % in moment and not at all in N(≥ 7, 8, 8.5); N(≥ 9) is now 0 where Mmax + 0.2 < 9 (32–26° S, Antarctic).
- **Done.** `mfd.top` (pad 0.2 above Mmax) and `mfd.bins(tail=True)`; `build.py` rerun, 240 files rewritten; tests 10 pass; REPORT_S1.md sections 1, 2, 4, 5 updated. Both OpenQuake check jobs rerun on the new files (result below when they finish).
- **Proposed DECISIONS line (Statistics, replaces "the tapered list running about one unit above the corner" in the line on source MFDs and "goes on past Mmax with the small tapered rates" in the Mmax-corner line):** "The evenly discretised tapered list ends at Mmax + 0.2 and its last bin carries the rate of the tapered line above it, so N(≥ M) equals the fitted line at every edge; with the Kagan corner 0.6 % of the moment lies above Mmax + 0.2 in every unit (Pablo, 15 Nov, S1)." It applies to every unit, so S2 and S3 should build their lists the same way.


## 2026-11-15: B14 nodal planes per class (Claude Code)
- **Done.** `model/mechanisms/npd.py` (settings at the top), `tests/test_npd.py` (2 pass), table `npd_2026-11-15.csv` (7 classes, 2–6 planes each, weights sum to 1), `tables/counts_2026-11-15.csv`, `tables/shares_2026-11-15.csv`, `figs/ternary.png`, `REPORT_B14.md`. Run in this session (a few seconds).
- **Numbers.** 1 461 mechanisms inside completeness (all from 1976, Mw ≥ 5.0); 636 oblique (44 %). Shares N / R / SS: in-slab shallow 0.38 / 0.51 / 0.11, intermediate 0.75 / 0.10 / 0.15, Jujuy nest 0.96 normal; forearc 0.29 / 0.63 / 0.09, arc 0.10 / 0.23 / 0.67, backarc reverse 0.66 / SS 0.30, Patagonia SS 0.81. No class took the family distribution (smallest Patagonia, 26 weighted). North–south of 30° S: same leading type on both sides in every class; arc and backarc shares differ by 0.2–0.3 on 10–29 events per side. No split made.
- **Choice made (for Pablo to confirm):** the listed nodal planes are unordered, so before the circular mean / medians one plane per event is picked: the one whose normal is closer to the first plane of the mean double couple of the type (principal axes of the weighted P and T orientation tensors). Pooling both planes would average orthogonal strikes for strike-slip and mix 20° and 70° dips. The second plane of each type is the exact auxiliary of the representative one. Type weights rounded to 0.01 so the plane weights sum to exactly 1.
- **DECISIONS.md edited at the brief's word:** the line "Nodal planes per class from the catalogue mechanisms (B14, `npd_2026-11-15.csv`); used from S5; not a tornado factor." added under In-slab and under Crustal and faults. The old in-slab line "Two nodal planes … (30 Sep)" was left as it is (S2 still uses it); Pablo may want to mark it as used until S5. DECISIONS re-read before finishing: no line used here (Catalog, Classification, Statistics table) changed during the session.
- **Open:** whether to split any class north / south (report, shares table); whether the 44 % oblique share needs a word in the paper (Frohlich limits as published).
- **Suggested commit:** `git add psha_chile8/model/mechanisms psha_chile8/DATA.md psha_chile8/DECISIONS.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `B14: nodal-plane distributions per in-slab and crustal class from the catalogue mechanisms (Frohlich types, representative plane and auxiliary per type), report and ternary figure`

## 2026-11-15: S3 and S4, crustal source model (Claude Code)
- **Done.** `model/crustal/`: `smooth.py` (kernel and S-test score), `background.py` (step 2), `faults.py` (step 1), `join.py` (step 3), `large.py` (step 4), `nrml.py` and `build.py` (step 5), `oqcheck.py` (step 6); tests `model/crustal/tests/test_crustal.py` (11 pass). Report `model/crustal/REPORT_S3.md`. Input copied: `data/crustal_grid_01_2026-11-15.csv` (psha_chile7 crustal grid, DATA.md row, sha256 in `data/SHA256SUMS`). `smoothed_seismicity` repository read (not changed).
- **Kernel.** psha_chile7 `lib/smooth.py` and `smoothed_seismicity/ssm/smoothing.py` give the same field (test, 10⁻¹⁰); ported the psha_chile7 kernel; the S-test score of `optimize_kernel` rewritten: test events count only inside a grid cell, with their class weight. Calibration (train < 2010, test 2010–2026, complete declustered events): **n = 5 in every class and both declustering options** (arc and Patagonia have < 20 test events and take the crustal-family n, also 5). n = 5 is the lowest candidate; n = 2–3 score up to 2.6 (forearc) and 5.7 (Patagonia) better, the family is best at 5.
- **Kernel diagnostic** (Pablo's question; `model/crustal/kernels.py`): Gaussian kernel and full catalogue next to the power law and the two declustering options. Power law n = 5 is best or within 3 log units everywhere; the Gaussian is 6–10 worse on the crustal family and never clearly better in a class; on the full catalogue the power law picks n = 1–5. No change to the model. Report section 3.
- **Joint search of n and exponent** (Pablo's request): no interior optimum (forearc rising to exponent 4, family at n 1 / exponent 1.0, backarc flat; gains 1–6 log units). **Decided (Pablo): exponent 1.5.** Candidates back to 5–100: n = 5 in every class, patterns rebuilt and equal to the NRML files (5 × 10⁻⁷). Merged crustal catalogue checked: n = 5 for both options (Pablo: a check only, no DECISIONS or logic-tree line). **DECISIONS.md edited by Claude Code at Pablo's word (15 Nov):** Crustal and faults, new line "Crustal background kernel: Helmstetter et al. (2007), exponent 1.5, n = 5 for every class and both declustering options …" (after the multi-fault line; the in-slab kernel line of S2 untouched). Add `psha_chile8/DECISIONS.md` to the S3 commit. `tables/calibration_2026-11-15.csv` now holds n 5–100 at exponent 1.5 only; the n 1–3 values in the report come from the earlier run.
- **Join** (tapered fit, Mw ≥ 6): total / fit forearc and backarc 1.00; arc 3.36 (A), 8.87 (B), 4.64 (B-MASCSN moment), background zero at 6.0–7.1 and back above 7.1; Patagonia 1.32 / 3.57 / 1.48; all crustal 1.41 / 2.50 / 1.63. Fault class sums reproduce D16b. Class-maximum sensitivity lowers fault N(≥ 6) 3–4 times (A 0.63 → 0.19).
- **Found:** the psha_chile7 crustal grid ends about 1° east of the border; 69–71 % of the backarc pattern events lie outside it, and the kernel normalised over the grid piles 47–49 % of the backarc rate into the eastern 0.5° (15–16 % on a grid to 60° W). Kept as the brief says; proposed below.
- **Kanamori event:** Aysén 1960-06-06 (Mw 7.7, arc, weight 1), 3 km from the Canal Costa trace; sets the arc Mmax 7.9 (7.3 without it). The 1949 Magallanes doublet is 16–27 km from the traces.
- **Choices made (for Pablo to confirm):** pattern events = complete in the table of DECISIONS (Mw 4.5–4.9 not used); join on the weighted-mean fault MFD of the tree; background files sum the four classes per cell; tree fragments per database and shape with the tapered fit as reference (as S1), database weights left to the tornado; B-MASCSN moment as `compare.sources` (depth branch sets Mmax and width); city fault rates count the share of each trace within 50 km (D16b counted whole sources); tapered background list ends at corner + 1 (current DECISIONS). If S1's proposed rule (Mmax + 0.2, last bin carries the tail) is adopted, change `TAPER_RUN` in `background.py` and rerun `background.py`, `join.py`, `build.py`.
- **DECISIONS re-read before finishing** (changed 20:00): new line under Crustal and faults, "Nodal planes per class from the catalogue mechanisms (B14, `npd_2026-11-15.csv`); used from S5". The S4 files keep the psha_chile7 planes (as the brief and "used from S5"). For S5: the background files sum the four classes per cell, so class planes need one point source per class and cell (a `build.py` change, about 1.3 GB of files instead of 0.3 GB). Nothing else of S3 changed.
- **Proposed DECISIONS lines:** in `REPORT_S3.md` section 7 (grid to 60° W; kernel n = 5; arc bulge accepted or class-maximum Mmax for the arc; Kanamori event = Aysén 1960, all events count; pattern from the complete events).
- **Proposed LEARNINGS lines:** a grid that ends before the events piles their rate onto its edge; fault N(≥ 6) depends more on the Mmax rule than on the slip (factor 3–4).
- **OpenQuake check:** every source file read by OpenQuake's converter, rates within 5 × 10⁻⁶, top magnitudes and counts equal (`tables/oqcheck_2026-11-15.csv`); no-faults job calc 501 ran. The fault-database jobs (calc 504 queued) wait behind S2's dead calc 503 ("submitted", no process; `serialize_jobs = 1`). Pablo: tick S4 on the parse check, skip the jobs; the tree structure (extendModel) is tested in the first city run. Calc 504 left queued (not aborted).
- **Commands** (from `psha_chile8/model/crustal/`, `PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine`): `python background.py` (1 min), `python faults.py` (20 s), `python join.py` (1 min), `python large.py`, `python build.py` (3 min, 335 MB), `python oqcheck.py` (writes jobs and compares files, 6 min); jobs `cd oqcheck && oq engine --run job_A.ini` (and `job_B`, `job_Bmm`, `job_none`); `pytest model/crustal/tests` from `psha_chile8/`.
- **Full city run for Pablo:** in `model/crustal/nrml/`, a job per tree fragment `lt_crustal_<A|B|Bmm>_taper.xml` (and `_trunc`, `lt_crustal_nofaults_<shape>.xml` for the tornado), GMM tree ASK14, BSSA14, CB14, CY14 (0.25 each), Vs30 800 inferred, Z1.0 40 m, Z2.5 0.6 km, truncation 3, `maximum_distance = {"Active Shallow Crust": 300.0}`, `pointsource_distance = 100`, `rupture_mesh_spacing = 5`, PGA and the SA set, poes 0.1, the 14 cities.
- **Suggested commit:** `git add psha_chile8/model/crustal/{smooth,background,faults,join,large,nrml,build,oqcheck}.py psha_chile8/model/crustal/tests psha_chile8/model/crustal/REPORT_S3.md psha_chile8/model/crustal/{tables,figs} psha_chile8/model/crustal/oqcheck/*.{ini,xml} psha_chile8/data/crustal_grid_01_2026-11-15.csv psha_chile8/data/SHA256SUMS psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md` (the 335 MB of `model/crustal/nrml/` are rebuilt by `build.py`; commit only `nrml/branches.json` and `nrml/lt_*.xml` unless the NRML is wanted in git). Message: "S3/S4: crustal model. Kernel calibrated (n = 5), fault MFDs A, B, B-MASCSN moment per branch, join (arc and Patagonia bulge), large-event report, NRML for every branch and tree fragments".

## 2026-11-15: GM1 residuals of the subduction GMMs (Claude Code)
- **Done.** `gmm/`:
  - code: `records.py` (record table; named so to avoid the `build.py` of `model/interface` and `model/inslab`), `screen.py`, `residuals.py`, `scores.py`, `run.py` (entry, settings at the top), `figs.py`, tests `gmm/tests/test_gmm_residuals.py` (6 pass);
  - report: `gmm/REPORT_GM1.md`; tables and figures in `gmm/tables/` and `gmm/figures/`.
  - Everything was run in this session (about 6 minutes). OpenQuake 3.27.0.
- **Data.** 813 events and 9 421 records (interface 431 / 4 326, in-slab 382 / 5 095), Mw ≥ 5, Rrup ≤ 300 km, RotD50.
  - 7 flatfile events are unmatched; 11 of the 12 listed duplicate pairs are merged (the twelfth is not in the selection).
  - 22 events go to `review_mw.csv` (|ΔMw| ≥ 0.5, one side ≥ 5.5; with 5.0 it would be 79).
  - No station is east of the arc polygon, so backarc is False everywhere; none south of 46° S.
- **Screening.** 158 OpenQuake classes; 14 candidates per class:
  - the tree (AG20 SAM, Parker SA/SA_S, Kuehn SAM, Montalva 2017);
  - the global versions of AG20, Parker and Kuehn;
  - Idini 2017, Youngs 1997, Zhao 2016, BC Hydro 2015, Si 2020, Arteta 2021 (Vs30), Atkinson & Boore 2003.
  - Criterion 1 is read as "built for one other region only" (my reading), which drops the Japan / Taiwan / Mexico / NZ models.
- **Results** (evidence, no weights proposed):
  - The South America versions of the NGA-Sub models beat the global ones everywhere at PGA and SA(0.2), by 0.4–1.6 bit of LLH.
  - Montalva et al. (2017) has the smallest interface bias (≤ 0.13 ln) and ranks first in-slab at PGA and SA(0.2) (100 % / 93 % of resamples).
  - On the interface, Zhao 2016 (PGA), Youngs 1997 (SA(0.2)) and Montalva (SA(1.0)) are first by LLH; in-slab SA(1.0), AG20 global.
  - From Mw 6.5 (36 interface, 10 in-slab events) the NGA-Sub South America versions move to the top.
  - τ from the data is larger than the models' τ almost everywhere (0.50–0.80 against 0.35–0.60); φ agrees.
  - The interface event terms rise by about 2 ln units per 100 km of depth for the tree models.
- **Not done as the brief says:**
  - Copying the flatfiles into `psha_chile8/data/ground_motion/` and writing DATA.md, FIGURES.md, REFERENCES.md, `.gitignore` and `SHA256SUMS` were blocked in this session (work only in `gmm/`). The rows and commands are in `gmm/APPENDS_GM1.md`; the code reads the flatfiles in place from `data/ground_motion/` at the repo root.
  - The Idini soil classes are from memory (not in the OpenQuake docstring; paper not in `refs/`): check against Idini et al. (2017) before using Idini's numbers (report, assumption 14).
  - LLH and EDR are not checked against the papers (not in `refs/`); `openquake.smtk` does not import.
  - My τ/φ maximum likelihood equals statsmodels MixedLM to 6 decimals.
- **Commands** (from `psha_chile8/gmm/`): `python run.py` (6 min; `REBUILD = True` rebuilds the record table, 40 s). Tests: `pytest gmm/tests` from `psha_chile8/`.
- **Full pytest** from `psha_chile8/`:
  - `model/interface` and `model/inslab` both have a `build.py`, so the full run stops at collection; that clash is between S1 and S2, not GM1.
  - With `--ignore=model/interface`: 287 pass, 3 fail in `model/inslab/tests/test_s2.py` (S2 in progress).
- **DECISIONS** re-read at the end: the GMM lines did not change; nothing in GM1 changes them.
- **Proposed LEARNINGS lines (GMMs and sites):**
  - "On the Bastías et al. (2026) records the global NGA-Sub models predict 0.6–1.3 ln too low at PGA and SA(0.2); their South America versions halve that. Use the regional versions (GM1)."
  - "Interface event terms of every tree GMM rise with hypocentral depth (about 2 ln per 100 km at PGA); events at 40–60 km are underpredicted, which may be partly the interface / in-slab boundary of the classification (GM1)."
  - "LLH weights over many GMMs come out nearly flat (0.08–0.11 for the reasonable models); the bootstrap rank shares separate the models more clearly (GM1)."
- **Open for Pablo (GM2):**
  - Idini soil classes;
  - whether the large-magnitude subset should steer the choice;
  - the depth trend of the interface event terms;
  - the PGA component (RotD50 at 0.01 s against the geometric mean).
- **Suggested commit:**
  - `git add psha_chile8/gmm/{records,screen,residuals,scores,run,figs}.py psha_chile8/gmm/tests psha_chile8/gmm/REPORT_GM1.md psha_chile8/gmm/APPENDS_GM1.md psha_chile8/gmm/NOTES_data.md psha_chile8/gmm/tables/*.csv psha_chile8/gmm/figures psha_chile8/PLAN.md psha_chile8/WORKLOG.md`
  - The `residuals_*.csv.gz` files are 13 MB each; leave them out (rebuilt by `run.py`).
  - Message: `GM1: residuals and scores (LLH, EDR, event bootstrap, subsets) of 14 subduction GMMs on the Bastías et al. (2026) records, screening of the OpenQuake subduction GMMs, report`

## 2026-11-15: S1, Allen and Hayes as a third scaling branch; check jobs rerun (Claude Code)
- **Pablo:** add Allen and Hayes as a third scaling branch.
- **Done.** `build.MSR`: Strasser, Thingbaijam, Allen and Hayes 2017 (`AllenHayesInterfaceBilinear`, as the psha_chile7 variant `msr_ah`), 1/3 each. `nrml/source_lt_interface.xml` now has 72 × 3 = 216 paths. OpenQuake parses it (weights sum to 1) and applies each branch: the margin reference source has 28 103 / 26 840 / 25 103 ruptures (Allen–Hayes / Strasser / Thingbaijam). `mfd.mag_area` returns nan when no magnitude fills the source: with the bilinear Allen and Hayes area no rupture fills the full margin. Area check, report and tests (10 pass) updated.
- **Check jobs rerun on the lists ending at Mmax + 0.2:** calc 499 (margin) and 502 (segments) read all 240 files; OpenQuake rates equal the tables (≤ 2.4e-6). These jobs had two scaling branches; the third was checked by parsing the tree, not by a job.
- **Integration distance (Pablo's question):** OpenQuake applies `maximum_distance` 600 km to the rupture distance Rrup of each rupture (`hazardlib/contexts.py`), so ruptures on the neighbouring segment are kept for a site near a segment end. Segmentation lowers the hazard there only because no rupture crosses the boundary.
- **Proposed DECISIONS line (Interface, replaces "Rupture scaling: Strasser 2010 / Thingbaijam 2017, 0.5 / 0.5; Allen and Hayes stated"):** "Rupture scaling: Strasser 2010, Thingbaijam 2017 and Allen and Hayes 2017 (bilinear), 1/3 each, as a setMSRAbsolute level applied to every interface source; aspect ratio 1, rake 90° (Pablo, 15 Nov, S1)."
- **Full city run:** as in the S1 entry above, now 72 × 3 × 4 GMMs = 864 realizations.

## 2026-11-15: S1, DECISIONS lines written (Claude Code)
- **DECISIONS.md edited by Claude Code at Pablo's word (15 Nov):**
  - Statistics, the Mmax-corner line: the tapered list ends at Mmax + 0.2, with the rate of the line above in its last bin.
  - Statistics, the source-MFD line: the same list end, replacing "about one unit above the corner".
  - Interface: the rupture scaling line (Strasser, Thingbaijam, Allen and Hayes bilinear, 1/3 each, setMSRAbsolute on every source; aspect ratio 1, rake 90°), and a new line on the interface sources (files per branch, reference tree tapered with own b, tornado-only files, Mw 5.5, distance on Rrup, Antarctic b).
  - Superseded: one line for both changes.
- **Checked before writing:** DECISIONS had been edited by another session at 20:00 (in-slab kernel and nodal planes, fault databases). None of the lines S1 uses had changed, and nothing of it was touched here.
- **For S2 / S3:** the list-end rule is in Statistics and applies to every unit.
- **Suggested commit:** add `psha_chile8/DECISIONS.md` to the S1 commit of the entry above. The new file `data/crustal_grid_01_2026-11-15.csv` belongs to another task.


## 2026-11-15: S2 in-slab source model (Claude Code)
- **Done.** `model/inslab/`: `smooth.py` (Helmstetter kernel ported from psha_chile7; equal to the ssm code, tested), `build.py` (patterns, calibration, MFDs, NRML, tables; settings at the top), `figs_s2.py`, `oqcheck.py`, `tests/test_s2.py` and `tests/ref_kernels.py` (copies of the two kernel codes for the port test). 19 tests pass. Report `model/inslab/REPORT_S2.md`. C14 files unchanged.
- **Built.** 24 branches (declustering gk / nn × tapered / cut × (a, b) p05 / ML / p95 × three / one hypocentre), 72 files `model/inslab/nrml/is_<class>_<branch>.xml` (381 MB), `branches.json`, fragment `source_lt_inslab.xml` (reference tree: tapered, ML, three layers; gk / nn 0.5 / 0.5; the other branches weight 0 for the tornado). Classes on their own domains: shallow (slab top ≤ 50 km, 4 901 cells), intermediate (> 50 km, 8 946), nest (190 cells, also intermediate cells). No tornado and no hazard run (Pablo).
- **Calibrated n** (split at 2010, complete declustered events): n = 5 for every class and option except shallow / nn (10). n = 5 is the smallest candidate (open point).
- **Checks:** patterns sum to 1 on each domain; summed lists equal the fits at every edge (1e-14); depth weights sum to 1; hypocentres inside the zone; branch weights; nest sources only in the nest region. The tapered list ends at Mmax + 0.2 with the tail in the last bin (DECISIONS, Statistics, S1 rule), rebuilt once after that rule arrived.
- **OpenQuake:** the reference branch ran at Calama (calcs 498 three hypocentres at pointsource_distance 100 km, 118 s; 500 at 500 km, 94 s; PGA differs 1.4 %, a numerical check only). These ran on the files before the list-end change. The 24-branch load job was not run: the engine queue was held by another session's `job_A.ini`; my queued jobs were stopped at Pablo's word.
- **DECISIONS re-read at the end:** two changes while I worked. (1) The tapered list end (Mmax + 0.2), now followed. (2) Nodal planes per class from B14, used from S5: the files carry the two fixed planes (`NPD` in `build.py`).
- **Proposed DECISIONS lines:** `REPORT_S2.md` section 6 (kernel n per class; the pattern uses the complete declustered events, not all from Mw 4.5; in-slab source Mmin 5.0 against interface 5.5, to be made one in S5; in-slab reference tree).
- **Open:** n at the lower edge of the candidates; Jujuy nest events half below the C14 zone of the nest cells (median depth 189 km, lower depth 188 km); corner of the (a, b) variants kept at the ML value (Kagan on the variant b differs by 0.01–0.04); source Mmin across families; file size.
- **Commands for Pablo** (from `psha_chile8/model/inslab/`, conda `psha_renta`): `python build.py` (3 min), `python figs_s2.py`, `pytest model/inslab/tests` from `psha_chile8/`. OpenQuake load check of all 24 branches: `cd oqcheck; PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine oq engine --run job_all.ini`, then put its calc id in `CALCS["all"]` of `oqcheck.py` and run `python oqcheck.py` (writes `tables/oqcheck_2026-11-15.csv`). Tick S2 in PLAN when it passes.
- **Suggested commit:** `git add psha_chile8/model/inslab/{smooth,build,figs_s2,oqcheck}.py psha_chile8/model/inslab/tests/{test_s2,ref_kernels}.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/figs/{pattern_gk,pattern_nn,sections_sources,mfd_sources}.png psha_chile8/model/inslab/tables/*_2026-11-15.csv psha_chile8/model/inslab/oqcheck/*.{ini,xml} psha_chile8/model/inslab/nrml/branches.json psha_chile8/model/inslab/nrml/source_lt_inslab.xml psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`. The 72 NRML files (381 MB) and `tables/bins/` (26 MB) are rebuilt by `build.py`; commit them only if wanted. Message: `S2: in-slab source model, calibrated Helmstetter patterns per class and declustering option, B11 MFDs with (a, b) variants, C14 depths (three or one hypocentre), 24 branches as NRML, logic-tree fragment`

## 2026-11-15: GM1, GMM sets for the tornado (Claude Code)
- **Pablo:**
  - four GMM sets for the E17 tornado, each run as a whole: A the GM1 top four, B the current tree, C MASCSN26, D GEM South America v2016;
  - equal weights inside each class (the spread of each tree is looked at first);
  - Contreras & Boroschek (2015) not implemented, left out of C;
  - Montalva 2016 kept in D;
  - crustal: our old models for A and B, against MASCSN26 (Arteta 2023, Vs30 form) and GEM (Akkar, Bindi, Boore);
  - no stable crust; constant Vs30 800.
  - The tornado files are not written here; they will be made in a separate conversation.
- **Done.**
  - REPORT_GM1.md section 8: top four against MASCSN26.
  - Section 9: the four sets, where each comes from, notes for the job files.
  - Set A in-slab: Youngs 1997 and Zhao 2016 tie for 4th; Youngs is listed, by its better mean LLH rank.
  - Logic-tree XMLs were written and checked in OpenQuake 3.27 (all load), then removed at Pablo's word.
- **Found:**
  - no MASCSN26 GMM file exists, neither in the repo nor in github.com/frabravo/MASCSN26 (commit 73b5a8d), so set C comes from report Table 27;
  - GEM: `psha_gem/gmmLT.xml`; old tree: `psha_chile6/outputs/hazard/rock800_final/c_{if,is,cr}_final/gmm_lt.xml`.
- **For the tornado task:**
  - Idini (set C) needs a `soiltype` site parameter (1 = sI for Vs30 800 rock, no site term);
  - `backarc` False;
  - no set uses Z1.0 or Z2.5.
- **Proposed DECISIONS line (GMMs):** "The GMM tornado (E17) runs four sets as wholes, equal weights inside each class: GM1 top four, current tree, MASCSN26 without Contreras & Boroschek (2015), GEM South America v2016 without stable crust (Pablo, 15 Nov; REPORT_GM1 section 9)."
- **Suggested commit:** `psha_chile8/gmm/REPORT_GM1.md` and `psha_chile8/WORKLOG.md` go into the GM1 commit (the GM1 entry above lists the rest).
- **Shared files, at Pablo's word (15 Nov):**
  - rows of `gmm/APPENDS_GM1.md` appended to DATA.md ("Ground-motion data (GM1)"), FIGURES.md (two rows) and REFERENCES.md (section H);
  - DECISIONS.md, GMMs: three lines (GM1 as evidence for GM2; the four tornado sets; caution on Idini's soil classes);
  - LEARNINGS.md, GMMs and sites: the three GM1 lines.
  - The dated flatfile copies, `.gitignore` and `SHA256SUMS` are still not done (commands in `gmm/APPENDS_GM1.md`).

## 2026-11-15: S2, Pablo's answers (Claude Code)
- **Pablo:** the OpenQuake 24-branch job is not run now; in-slab sources start at Mw 5.5 like the interface; the (a, b) variants keep the ML corner (no Kagan recomputation); the tornado keeps the two fixed nodal planes and the final run uses the B14 nodal-plane model; the Jujuy nest stays as built (completeness only); total rates and b from the fits; the pattern from the declustered catalogues only (as built: no full-catalogue pattern exists).
- **Done.** `build.py`: `M_MIN = 5.5`; rebuilt (72 files, 350 MB, `minMag="5.50"`); the edge check holds to 1e-14; 19 tests pass; `figs/mfd_sources.png` redrawn; REPORT_S2.md sections 1, 2 and 6 updated.
- **Proposed DECISIONS line (Hazard runs):** "Source Mmin 5.5 (first bin centre) for the interface and the in-slab sources (Pablo, 15 Nov)."
- **Still open:** the kernel n at the lower edge of the candidates (n = 5 in five of six class × declustering cases).
- **Pablo (kernel):** keep the candidates n = 5–100; n = 5 (10 for shallow, nearest neighbour) stands. Nothing rebuilt. Proposed DECISIONS line as in REPORT_S2.md section 6, item 1.

## 2026-11-15: S2 closed (Claude Code)
- **DECISIONS.md edited by Claude Code at Pablo's word (15 Nov)**, two inserted lines, nothing else touched: In-slab, "In-slab kernel n, calibrated (S2): 5 …, 10 for the shallow class under nearest neighbour; candidates 5–100 kept"; Hazard runs, "Source Mmin 5.5 (first bin centre) for the interface and the in-slab sources (S1, S2)".
- **OpenQuake check:** `oqcheck.read_all` reads all 72 files with the OpenQuake 3.26 parser (16 processes, 35 s): 336 888 sources as built, every list from Mw 5.5, hypocentre weights sum to 1, no hypocentre outside its zone, N(≥ 5.5) and N(≥ 7) within 2e-7 of the tables (`model/inslab/tables/oqread_2026-11-15.csv`). No hazard run (Pablo).
- **PLAN:** S2 ticked; ← moved to S5.
- **Commit (S2, all entries of today):**
  - `git add psha_chile8/model/inslab/{smooth,build,figs_s2,oqcheck}.py psha_chile8/model/inslab/tests/{test_s2,ref_kernels}.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/figs/{pattern_gk,pattern_nn,sections_sources,mfd_sources}.png psha_chile8/model/inslab/tables/{calibration,edge_check,kernel_n,nest_depths,oqread,pattern,pattern_sums,rates,south36_layers}_2026-11-15.csv psha_chile8/model/inslab/oqcheck/*.ini psha_chile8/model/inslab/oqcheck/*.xml psha_chile8/model/inslab/nrml/branches.json psha_chile8/model/inslab/nrml/source_lt_inslab.xml psha_chile8/DECISIONS.md psha_chile8/PLAN.md psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`
  - Optional (rebuilt by `build.py` in 3 min): `psha_chile8/model/inslab/nrml/is_*.xml` (72 files, 350 MB) and `psha_chile8/model/inslab/tables/bins/` (gzip, about 20 MB). Not the `oqcheck/log_*.txt` files.
  - Message: `S2: in-slab source model. Calibrated Helmstetter patterns per class and declustering option (n 5, shallow NN 10), B11 MFDs from Mw 5.5 with (a, b) variants, C14 depths (three or one hypocentre), 24 branches as NRML, logic-tree fragment; all files read by the OpenQuake parser`
  - `DECISIONS.md` and `PLAN.md` also carry other sessions' edits of today; check the diff before committing them with S2.

## 2026-11-15: S3 follow-up, Pablo's answers and the arc bulge (Claude Code)
- **Decided (Pablo):** psha_chile7 crustal grid stays (a grid to 60° W was built, judged too wide, deleted); kernel exponent 1.5 and n = 5 (DECISIONS line written, earlier entry); fault Mmax with the class maximum computed and written as sensitivity files; Magallanes–Fagnano stays one joined system (no segment files); no MASCSN length cap in our rules, B-MASCSN-moment stays as MASCSN built it; Leonard (2014) for the fault rupture scaling (was WC1994); nodal planes per class only in the final model, not the tornado. Not written in DECISIONS (Pablo's word needed): proposed lines "Fault rupture scaling Leonard (2014), aspect 2 (S3)", "No FaultQuake length cap in our rules (S3)", "Crustal background on the psha_chile7 grid (S3; the eastern-edge effect on the backarc stated)".
- **Done.** `faults.py`: variants `<db>_cm` (class-maximum Mmax, per branch); `join.py` and `build.py` run over six fault variants; `build.py` fault files with `Leonard2014_Interplate`. Rebuilt: 28 background and 216 fault files (588 MB), `branches.json`, tree fragments `lt_crustal_<variant>_<shape>.xml`. New `arc.py` (fault count test). Tests 13 pass (class-maximum keeps the moment; fault files carry Leonard).
- **Arc bulge, fault count test** (`model/crustal/REPORT_S3.md` section 1b): arc events of Mw ≥ 6 inside the completeness table, 9.5 observed (fit 9.1). Leonard Mmax: expected 28.5 (A), 74.3 (B), 38.9 (B-mm); 6 %, 0 %, 6 % of the tree passes (p ≥ 0.05); ψ needed 0.10–0.25. Class maximum: 9.2 / 19.8 / 9.3, 94 % / 46 % / 96 % pass. Mw ≥ 7 agrees in every variant. The excess is the Leonard Mmax of short arc faults (10–120 km, Mmax 6.0–7.4). With the class maximum the arc and Patagonia bulges vanish in A and B-mm (total / fit 1.00), B keeps 2.2 (arc).
- **Open for Pablo:** arc option (accept the bulge; class maximum for the arc faults; or Leonard on a joined Liquiñe–Ofqui system, Mmax 8.0–8.3 for 1 000 km).
- **Commands** (from `psha_chile8/model/crustal/`): `python faults.py && python join.py && python build.py` (8 min), `python arc.py` (1 min), `python oqcheck.py` (parse check of all files, about 15 min). Run: all 244 files read by the OpenQuake converter, rates within 5 × 10⁻⁶, top magnitudes and source counts equal.
- **Suggested commit:** add `psha_chile8/model/crustal/arc.py` and `figs/arc_test_2026-11-15.png`, `tables/arc_*_2026-11-15.csv` to the S3 commit of the earlier entry.
- **Join rule changed (Pablo, 15 Nov):** above 6.0 the background is the fit minus the faults, and zero from the first bin where the faults reach the fit; it does not come back above the faults' Mmax. `join.background` changed, test added; join, 28 background files and arc test rerun. Arc and Patagonia: no background above 6.0; at Mw ≥ 7 the arc model is 0.66 (A) and 0.51 (B-mm) of the fit (Aysén 1960 has no source). Proposed DECISIONS line (replaces the join sentence of "Fault Mmin 6.0 …"): "per crustal class the background above Mw 6.0 is the catalogue fit minus the summed fault MFD and stops at the first bin where the faults reach the fit; it does not return above the faults (Pablo, 15 Nov)".
- **Class maximum judged unphysical by Pablo** (a Mw 7.9 on a 35 km segment needs about 38 m of slip; the class maximum is Aysén 1960 copied onto every segment): sensitivity only. MASCSN does not join traces (130 independent simple faults). Open: Pablo is against joining the Liquiñe–Ofqui traces; options left for the arc are accepting the bulge or a quick multi-segment model for Aysén-size ruptures.
- **Figures:** `model/crustal/figs/arc_join_leonard_2026-11-15.png`, `arc_join_classmax_2026-11-15.png` (rates per bin, one panel per database); the confusing `arc_bulge` figure removed. Tests 14 pass.
- **Proposed for Pablo (A7 / B11, not S3):** the Patagonia cut of `catalog/classify.py` (`SOUTH_LAT = -46.15`) classes the Liquiñe–Ofqui faults and events south of 46.15° S as Patagonia (faults CL-006vv, yy, aaa; midpoints 46.5–47.8° S), although they lie along the arc. Proposal: end the arc class where the arc polygon (`data/intraarc.shp`) ends instead of at a fixed latitude, reclassify the catalogue (A7) and refit arc and Patagonia (B11); faults and events must share the boundary, so the faults are not reclassed alone. Expected effect small (a few events and three faults move from Patagonia to arc). The multi-fault rupture set already links across classes, so it does not wait for this.
- **Multi-fault quick estimate (in progress):** `model/crustal/multifault.py`, plan `model/crustal/WORKPLAN_multifault.md`. Main traces only link (slip rate ≥ 1 mm/yr; in A the GEM class 1–5 mm/yr). Exact trace distances (UTM 19S). QGIS layers `model/crustal/qgis/mf_A_{faults,jumps,chains}_2026-11-15.shp`.
- **Quick estimate, result** (A; arc and Patagonia faults; main traces link; ψ 0.8; `model/crustal/tables/mf_A_arc_quick_2026-11-15.csv`, `figs/mf_A_arc_quick_2026-11-15.png`): 38 main faults, 18 links, 27 chains, longest 229 km, chain Mmax 7.4 (10 km) / 7.7 (20 km). Arc N(≥ 6) 0.30 / 0.40 per year (Leonard alone 0.43); expected 18.8 / 25.9 against 9.5 observed, p 0.01 / 0.00: fails. Linked ruptures carry 1.6–3 % of the arc Mw ≥ 6; the main faults rupturing alone carry 0.22–0.29 per year. Non-main-shock slip only 2–6 % (the first run, with secondary traces allowed to link, had 43 % and passed: the slow secondary members held the chain rates down and SHERIFS anchored the target low).
- **Jump sensitivity** (quick estimate, A, main traces; `model/crustal/tables/mf_A_arc_jumps_2026-11-15.csv`, figures `figs/mf_A_arc_jump{5,10,15,20}_2026-11-15.png`; not referenced: Milner et al. 2013 test up to 5 km): longest chain 229 / 229 / 416 / 860 km at 5 / 10 / 15 / 20 km jumps; arc expected Mw ≥ 6 in the table (10 km / 20 km depth) 18.8 / 25.9, 16.3 / 21.2, 12.0 / 16.0, 9.3 / 13.3 against 9.5 observed; passes (p ≥ 0.05) from 15 km (10 km depth) and 20 km (both). Non-main-shock slip 2–12 %. Linked ruptures are 3–6.5 % of the Mw ≥ 6 count but take the moment into Mw 7.5–8.2.
- **Quick estimate, B** (our rules; main traces = slip ≥ 3.0 mm/yr, the MASCSN masters at 4.0–10.6 against secondary 2.0–2.9; `model/crustal/tables/mf_B_arc_jumps_2026-11-15.csv`, QGIS `model/crustal/qgis/mf_B_*`): 5 km jump: 14 links, 9 arc chains, longest 250 km, arc N(≥ 6) 0.96 / 1.24 per year (10 / 20 km), expected 61 / 80 against 9.5; 10 km jump: chains to 699 km (Mmax 7.8 / 8.1), N(≥ 6) 0.70 / 0.89, expected 45 / 59. Fails at both: the MASCSN slip rates on whole traces (7 mm/yr) carry 2–3 times A's moment; non-main-shock slip about 0–1.5 %.
- **Tapered background lists follow the new DECISIONS rule** (Statistics, changed during the session): end at Mmax + 0.2, last bin carries the rate of the line above (was: corner + 1). `background.mfd` changed (`TAPER_END = 0.2`), test updated (14 pass); `background.py`, `join.py`, `arc.py` rerun; arc test unchanged at Mw ≥ 6. **NRML not rebuilt and not parse-checked (Pablo: fits first):** the 28 background files in `model/crustal/nrml/` still carry the old corner + 1 tails; run `python build.py` before using them.
- **Quick estimate, B-MASCSN moment** (main ≥ 3 mm/yr by the database slip; budget = MASCSN moment as slip over our area; `model/crustal/tables/mf_Bmm_arc_jumps_2026-11-15.csv`): arc expected Mw ≥ 6 (10 / 20 km depth) 43 / 30 at a 5 km jump, 35 / 23 at 10 km, 27 / 18 at 15 km (chains to 983 km, Mmax 8.0 / 8.3), against 9.5: fails at every jump. Pablo (15 Nov): 5–13 km gaps between mapped traces are reasonable (poor mapping), 20 km too much; the tail above Mw 7.3 may fall short; multi-fault ruptures likely only for Liquiñe–Ofqui; more seeds later for resolution; DM stays 0.1.
- **Decided (Pablo, 15 Nov): Liquiñe–Ofqui seismogenic depth 10 km** (Sielfeld et al. 2019), no 10 / 20 km branch for these faults. Pablo: Sielfeld et al. (2019) show 10 km in the north of the system; south of it the depth may differ, but 10 km is also likely along the volcanic arc. **Reminder for Pablo:** put it in the fault databases (A and B: `z_bot` 10 km with source "Sielfeld et al. 2019" for the Liquiñe–Ofqui rows; the D16 / D16b files belong to model/faults, not changed here) and add Sielfeld et al. (2019) to REFERENCES.md. Proposed DECISIONS line (Crustal and faults, after the depth line): "Liquiñe–Ofqui faults: seismogenic depth 10 km (Sielfeld et al. 2019), no depth branch (Pablo, 15 Nov)."
- **Aysén 1960-06-06, all reported values** (Kanamori and Rivera 2017 and Pacheco and Sykes 1992 read in `refs/catalogs/`; the rest from `catalog/sources/` records linked to `cl19600606055549`):
  - moment magnitudes: Mw 7.7 ± 0.2, M0 4.5 × 10²⁰ N m from long-period records, slow event with at least 190 s duration (Kanamori and Rivera 2017; ISC-GEM direct Mw 7.7, q B); Mw 7.8 (Kanamori and Stewart 1979, as cited there); Mw 7.2 (Pacheco and Sykes 1992, Table 4: type "u", M0 0.62 × 10²⁰ N m with no reference, i.e. converted from their Ms 7.1)
  - surface-wave and body-wave: Ms 6.9 (Rothé 1969), Ms 7.1 (Abe; Pacheco and Sykes), ISC MS 7.5 ± 0.13 (8 stations), MOS M 7.5, PAS M 6.75 and 6.88, mB 7.1 (Abe)
  - locations: Centennial / EHB 45.70° S 73.50° W (used in the catalogue), ISC-GEM 45.75° S 72.92° W (± 9 km), ISC 45.79° S 72.89° W, ISS 45.71° S 73.08° W, BCIS and CGS 45.5° S 73.5° W, MOS 47.0° S 74.0° W; Pacheco and Sykes 45.71° S 73.00° W. All but MOS within about 50 km of each other, 35–60 km south of Puerto Aysén.
  - Kanamori and Rivera: depth not constrained, possibly deeper than the 2007 swarm in a ductile environment; "relatively minor shallow macroseismic effects", no reports of swarms or landslides; NS right-lateral preferred (proximity to Liquiñe–Ofqui) but not unique.

## 2026-11-15: A9 point 1, phase 1, Aysén 1960-06-06 (Claude Code, A6)
- **Read myself:** Ruiz and Madariaga (2018), `refs/catalogs/ruiz_madariaga_2018.pdf`, whole text, Tables 1–2. DECISIONS re-read at start and end, unchanged during the session.
- **What they give:** one sentence, section 6, Tectonophysics 733, p. 50 (PDF p. 14): "Kanamori and Rivera (2017) suggested that a slow Valdivia's aftershock of magnitude Mw 7.7 probably took place in this fault" (the Liquiñe–Ofqui shallow fault, same paragraph). No date, no location, no own magnitude; not in Table 1 (events of Mw ~8 since 1900) or Table 2. Their only magnitude is Kanamori and Rivera's 7.7, cited.
- **Citation fixes:** "p. 14" is the PDF page; the journal page is p. 50. The 7.2 in the A6 class-hint table (`A6/no_depth.csv`) is the catalogue Mw (Centennial), not a Ruiz and Madariaga value. Ruiz and Madariaga say "probably in this fault", not "crustal"; the crustal hint rests on that sentence and on Cabello et al. (2025) Table 7, p. 10.
- **Override row as the brief asks** (σ 0.2 = `SIG_RM` in `magnitude.py`, the σ for a plain Ruiz and Madariaga number):
  `cl19600606055549,mw,7.2,7.7,0.2,Ruiz and Madariaga (2018),"section 6, p. 50","Aysén slow event, the paper quotes Kanamori and Rivera; long-period moment Mw 7.7 of a slow event (Kanamori and Rivera 2017; M0 4.5e20 N m, source ≥ 190 s); not used. Reported: Mw 7.7 ISC-GEM direct (q B), Mw 7.8 Kanamori and Stewart 1979 (cited by K&R), Mw 7.2 Pacheco and Sykes 1992 (type u, M0 0.62e20 N m, from Ms 7.1); Ms 6.9 Rothé 1969, Ms 7.1 Abe and P&S, ISC MS 7.5 ± 0.13 (8 st.), MOS M 7.5, PAS M 6.75 and 6.88, mB 7.1 Abe",proposed`
  Class hint row kept: `cl19600606055549,class_hint,,crustal,,Ruiz and Madariaga (2018),"section 6, p. 50","probably on the Liquiñe–Ofqui fault (the paper, after Kanamori and Rivera 2017); crustal in Cabello et al. (2025) Table 7, p. 10",accepted`
- **The conflict for Pablo:** the row reproduces 7.7, i.e. Kanamori and Rivera under another name, so it does not meet the aim of a seismic-slip magnitude. Read strictly, Ruiz and Madariaga give no magnitude of their own; then the mw override is removed and the A5 rule gives Centennial Mw 7.2 (σ 0.25). Note: the A5 rule puts Ruiz and Madariaga first before 1976; 7.2 holds only because A3 does not match this event (the paper gives no date). If it were matched, the rule would return 7.7.
- **Effect on the arc** (`fits_2026-11-15b.csv`, b 1.00; corner by `gr.kagan_corner` on Mmax + DM/2, as `run.py`): with 7.7, Mmax 7.9, corner 7.70. Without it, the largest arc event with weight ≥ 0.5 is Aysén at 7.2 (1927-11-21 is 7.1; 1929-10-19 Mw 7.8 and 1926-04-28 Mw 7.3 have arc weight 0.07, 1919-03-02 Mw 7.2 has 0.38): Mmax 7.4, corner 7.20 at the same b, a drop of 0.5 in both. Observed arc events of Mw ≥ 7 do not change (Aysén stays at 7.2). The tail above Mw 7.4 goes from the tapered line to nothing in the cut shape and to a fast taper in the tapered shape; the refit (b, N(≥ 7)) is for the B11/B12 phase-1 test table. Also downstream: the arc class maximum (fault sensitivity, S3) and the arc background Mmax 7.9 in DECISIONS (Crustal) become 7.4.
- **Not changed:** `overrides_A6.csv`, every catalogue file.
- **Open for Pablo:** keep 7.7 under Ruiz and Madariaga, or remove the override (7.2).
- **Proposed DECISIONS line (after Pablo decides):** replace "Aysén 1960-06-06 Mw 7.7 (Kanamori and Rivera 2017)" in the A6 line with the chosen value and source.
- **Aysén, magnitudes in every catalogue** (searched by time, 05:40–06:10 on 1960-06-06, in all `catalog/sources/` files; also `data/catalogs/` ANSS, GEM, additions, relocated; and Table 1 of Engdahl and Villaseñor 2002, checked on the scanned page):
  - Centennial (src 2248): P&S Mw 7.2 (preferred), P&S Ms 7.1, ABE1 Ms 7.1, ABE1 mB 7.1, ROTHE Ms 6.9; EHB 45.70° S 73.50° W, 15 km fixed.
  - Engdahl and Villaseñor (2002), Table 1, p. 680: 1960 6 6 05:55 49.1, 45.70° S 73.50° W, 15 km, 7.2 Mw, EHB, P&S (same as Centennial).
  - ISC Bulletin (event 879416): ISC MS 7.50 ± 0.13 (8 stations), MOS M 7.50, PAS M 6.75 and 6.88, plus the Centennial values (P&S Mw 7.2, P&S / ABE1 Ms 7.1, ABE1 mB 7.1, ROTHE Ms 6.9). Origins ISC, BCIS, ISS, MOS, CENT, CGS.
  - ISC-GEM (879416): Mw 7.7 ± 0.2, q B, s d (direct, from a published moment: Kanamori and Rivera).
  - ComCat (iscgem879416): Mw 7.7 ± 0.2 (the ISC-GEM value).
  - Cabello et al. (2025) (src 922): Mw 7.7 (ISC-GEM, copied).
  - Ruiz and Madariaga (2018) table entry: Mw 7.7, month only (Kanamori and Rivera, cited).
  - Not listed: GCCEL, ISC-EHB, GCMT, Potin, CSN, ANSS file, GEM file, Lomnitz (2004) (its list has no Aysén event).
- **Reading:** every 7.7 traces back to Kanamori and Rivera. The only other moment magnitude is P&S Mw 7.2, converted from Ms 7.1. Measured magnitudes from seismic waves: Ms 6.9 (Rothé), 7.1 (Abe, P&S), 7.5 (ISC, 8 stations; MOS); mB 7.1; PAS 6.75 / 6.88.
- **Decided (Pablo, 15 Nov): Aysén keeps Mw 7.7 ± 0.2; no hand pick.** In the order before 1976 the ISC-GEM direct Mw (from a measured long-period moment) goes before the Centennial 7.2, which is Pacheco and Sykes' Ms 7.1 converted (type u). A long-period moment is the standard basis of Mw, like the other 89 ISC-GEM direct values before 1976; the σ 0.2 is ISC-GEM's own. Arc Mmax stays 7.9, corner 7.70: no change for A7 or B11/B12 from point 1.
- **Citation fixed in `catalog/overrides_A6.csv`** (values and status unchanged; the frozen copy in `catalog/frozen/2026-11-14/` not touched):
  - mw row: reference "ISC-GEM v13.0 (Di Giacomo et al. 2015); Kanamori and Rivera (2017)", page "catalogue entry 879416; Summary, p. 93" (K&R, GJI 211, 93–106), reason states the direct Mw and why it ranks above the converted Centennial value.
  - class_hint row: "Ruiz and Madariaga (2018); Cabello et al. (2025)", "section 6, p. 50; p. 10, Table 7" (was "p. 14", the PDF page).
  - Still open (not changed): `catalog/A6/literature.csv`, `changes_for_review.csv` and `REPORT.md` carry the old "p. 14" / mixed citation.
- **No rerun needed:** the reference and page fields are not read by `magnitude.py`; the catalogue is unchanged.
- **Proposed DECISIONS edit:** in the A6 line, "Aysén 1960-06-06 Mw 7.7 (Kanamori and Rivera 2017)" → "Aysén 1960-06-06 Mw 7.7 (ISC-GEM direct Mw, the moment of Kanamori and Rivera 2017; the Centennial 7.2 is a converted Ms)".
- **Commit:** `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`; message: `A9 point 1: Aysén 1960 keeps Mw 7.7 (ISC-GEM direct); override citation fixed`
- **Citation also fixed in the A6 files** (Pablo, 15 Nov): `catalog/A6/changes_for_review.csv` and `REPORT.md` (table row) get the same reference, page and reason as the override; `literature.csv` Ruiz and Madariaga rows p. 14 → "section 6, p. 50", the Mw row noted as a quote of Kanamori and Rivera; the REPORT no-depth table cites Ruiz and Madariaga p. 50 and Cabello et al. Table 7. Mw column of that table left at 7.2 (catalogue value of 13 Nov). Add `psha_chile8/catalog/A6/{changes_for_review.csv,literature.csv,REPORT.md}` to the commit above.
- **Interface hints for historical events (A9 point 2, A6 part; Pablo, 15 Nov).** The A7 session found 41 no-depth events of Mw ≥ 7 split forearc / interface (28 before 1904), none with a hint. A Ruiz and Madariaga class reaches `classify.py` only through a hint row of `overrides_A6.csv`; the A3 match alone does not set it. Read in the paper (journal page = PDF page + 36), rows added to `catalog/overrides_A6.csv`:
  - 1575-12-16 (`cl15751216183000`), section 6, p. 48: "could be a giant event similar to 1960"; accepted.
  - 1737-12-24 (`cl17371224000000`), section 6.1, p. 50: deeper zone of the plate interface, domain C; accepted.
  - 1822-11-20 (`cl18221120023000`), section 2.2, p. 41: interplate event deep on the plate interface; accepted.
  - 1835-02-20 (`cl18350220153000`), section 5.2, p. 47; p. 48; section 7, p. 52: uplift and tsunami, the 2010 interface rupture overlaps 1835; accepted.
  - 1604-11-24 (`cl16041124183000`), section 3.1.2, p. 42: destroyed and flooded Arica; the paper names no class, interface inferred from the tsunami; **proposed**, for Pablo.
  - Cabello et al. (2025) state no interface or in-slab class (only 13 crustal events, Table 7). Ruiz and Madariaga give no class for 1543 and 1859. The other 21 historical events (1513, 1520, 1562, 1570, 1590, 1604-12-01, 1639, 1657, 1822-11-25, 1829, 1831, 1833 ×2, 1843, 1847, 1849, 1851, 1869, 1871, 1878) need another source (Lomnitz 2004 and others): open A6 reading.
  - Effect on the frozen weights: forearc crustal weight at Mw ≥ 7 down 0.30 (four accepted rows; 0.43 with 1604), out of 3.2 from no-depth forearc / interface events.
  - Not in effect until the rerun of the A8 order (locate, magnitude, classify), phase 2. `catalog/A6/literature.csv` not updated with these rows.
- **Commit:** `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`; message: `A6: Ruiz and Madariaga interface hints for 1575, 1737, 1822, 1835 (1604 proposed)`
- **1604-11-24 interface hint accepted** (Pablo, 15 Nov; inferred from the tsunami at Arica, Ruiz and Madariaga p. 42). Forearc crustal weight at Mw ≥ 7 down 0.43 with the five rows.
- **Historical no-depth events without a class (23 left after the five hints): Lomnitz (2004) and Candia and Macedo (2026), both read in `refs/catalogs/`.** Lomnitz Table 1, pp. 370–374, gives no class, only tsunami, uplift and damage accounts. Candia and Macedo move events to interface when NOAA (2025) rates the tsunami 3 or 4 (p. 5). Their Figure 3 (p. 6) shows these megathrust tsunami events labelled by year only. The full list of 65 is their supplement Table S1, not in `refs/`, so absence from Figure 3 is not conclusive.
  - Tsunami in Lomnitz and in Candia Fig. 3: 1570-02-08 (p. 370, probable offshore epicentre, major tsunami); 1657-03-15 (p. 371, tsunami flooded the main square, offshore epicentre); 1849-12-17 (p. 372, tsunami 16 ft in Coquimbo Bay; **Lomnitz date 17 November**, check); 1859-10-05 (p. 373, severe tsunami damage at Caldera).
  - Candia Fig. 3 only: 1869-08-24 (label near 19° S; Lomnitz p. 373: possibly a large aftershock of 1868, "the sea seemed to boil" off Pisagua, no tsunami stated).
  - In Lomnitz, no tsunami, not in Candia Fig. 3: 1562-10-28 (p. 370, "great earthquake", possibly a storm); 1829-09-26 (p. 372, possibly a late aftershock of 1822); 1847-03-08 (p. 372, Lomnitz 8 October, La Ligua, felt; date differs); 1871-10-05 (p. 373, heavy damage in Iquique); 1878-01-23 (p. 373, named only as a large aftershock of 1877).
  - 1851-04-02 (33.2° S): Lomnitz's 1851 is 26 May, Huasco (28.5° S, tsunami), a different event. Our event matches Lomnitz 1850-04-02, Casablanca, Mw 7.5, no tsunami (p. 373): probably a year error in the catalogue; check.
  - In neither source: 1513, 1520, 1543, 1590, 1604-12-01, 1639, 1822-11-25, 1831, 1833-04-25, 1833-09-18, 1843.
  - Candidate interface hints (Lomnitz tsunami and Candia Fig. 3 IF): 1570, 1657, 1849, 1859, and 1869 (Candia only). Forearc crustal weight at Mw ≥ 7: −0.36 (0.06 + 0.06 + 0.05 + 0.05 + 0.13). Not added; Pablo decides. Getting Candia's Table S1 would confirm the dates and could add more events.
  - After 1904, Candia Fig. 3 labels 1918, 1920, 1922, 1928, 1936, 1943 among others. Of our 13 split events, 1920 (1920-08-20 at 37.9° S or 1920-12-10 at 39.5° S) and 1928 (12-01, hinted already, or 12-02) are ambiguous by year only; Table S1 needed.
- **Five more interface hints added, accepted** (Pablo, 15 Nov): 1570-02-08, 1657-03-15, 1849-12-17, 1859-10-05 (Lomnitz 2004 tsunami, pp. 370–373, and Candia and Macedo 2026 Fig. 3, p. 6), 1869-08-24 (Candia and Macedo only). Ten historical hints in all today; forearc crustal weight at Mw ≥ 7 down 0.79 in total after the rerun. Open: the 1849 date (Lomnitz 17 November), 1847 and 1851 (probably 1850-04-02) dates; Candia Table S1. Commit: `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`, message `A6: interface hints for 1570, 1657, 1849, 1859, 1869 (Lomnitz 2004; Candia and Macedo 2026)`.
- **Candia and Macedo checked in their own catalogue** (SRL supplement xlsx, sheet Catalog, cached as `catalog/cache/candia_macedo.csv`; it has no Table S1). The class is in `mech`. The tsunami reclassification shows in the EP score (Table 3, p. 8): EP = 0.2k + 1.5 (no tensor) + 0.4 (placeholder depth) + 3.0 (HM, tsunami evidence against the geometry). A NOAA record with EP 6.5 or a GHE record with 5.9 was moved to IF by tsunami evidence; EP 300 marks a rejected record (crustal, Mw > 7, depth 0). Matched to our 41 split events (same day ±1, or same year for 1 January dates; latitude ±2°):
  - IF by tsunami evidence (HM applied): 1570, 1575-12-16, 1604-11-24, 1657, 1822-11-20, 1835, 1859, and **1849, but as NOAA 1849-11-17**. Candia keeps SISRA 1849-12-17 as a separate, rejected SC record. Lomnitz and NOAA both give 17 November, so our 1849-12-17 (Cabello) is probably a month off. All of these already carry our hints.
  - IF by geometry only (no HM): 1513 and 1590 (GHE, 17.2° S), 1869 (NOAA, EP 3.5; in their Fig. 3 tsunami list, so the geometry already gave IF), and every split event after 1904 (ComCat locations, same Slab2 rule as ours, not a literature class). Not used as hints.
  - Not IF: 1562, 1575-03-17, 1737, 1871 (SC, rejected); 1829 and 1851-04-02 (SC); 1831 and 1833-09-18 (SL); 1878-01-23 (OR, GHE). 1737 stays interface, from Ruiz and Madariaga.
  - Not in their catalogue on that day: 1520, 1543, 1604-12-01, 1639, 1822-11-25, 1833-04-25, 1843, 1847-03-08. NOAA and SISRA have 1847 on **10-08** (31.6° S), as Lomnitz does, so our 1847-03-08 is probably a date error.
  - Correction to the entry above: NOAA and SISRA both date the event 1851-04-02 (33.3° S), so Lomnitz's 1850-04-02 may be his error. Our 1851-04-02 is probably right.
  - No new hints from Candia. Open for the catalogue (A6 date corrections, need a source read): 1849-12-17 → 11-17, 1847-03-08 → 10-08.
- **Dates not overridden** (Pablo, 15 Nov): 1849-12-17 and 1847-03-08 are the dates of our source (Cabello et al. 2025, from SISRA), so they stay. The NOAA and Lomnitz dates (1849-11-17, 1847-10-08) are noted here only. The 1849 interface hint stays on `cl18491217100000`.

## 2026-11-16: A9 point 2c, in-slab hints for no-depth events (Claude Code, A6)
- **Brief from the A7 session:** proposed rows for 1929-10-19 and 1926-04-28. Abe and Kanamori (1979) was read by A7. I read Astiz, Lay and Kanamori (1988), `refs/catalogs/astiz_etal_1988.pdf` (scan; Table A checked on the page images).
- **Astiz et al. (1988), Table A, "Large intermediate and deep focus events", pp. 130–131.** By region; nearly complete for mB ≥ 7 below 70 km from 1904 (p. 88). Our no-depth split events in it:
  - 1929-10-19 10:12:52, 23° S 69° W, 100 km, mB 7.10 (Altiplano, p. 130; again under North Chile, p. 131). Abe and Kanamori give mB 7.4, the value our catalogue converts.
  - 1936-07-13, 24.5° S 70° W, 80 km, mB 7.2 (p. 131); split forearc / in-slab, crustal 0.14.
  - 1939-04-18, 27° S 70.5° W, 100 km, mB 7.3 (p. 131); split forearc / interface (0.60 / 0.34 / crustal 0.05).
  - 1942-07-08, 24° S 70° W, 140 km, mB 7.0 (p. 131); split forearc / interface, Mw 6.9.
  - 1926-04-28 is not in Table A (not under Altiplano or North Chile).
- **Rows added to `catalog/overrides_A6.csv`, all `proposed`:** 1929 class hint in-slab and depth 100 ± 20 (Abe and Kanamori 1979, Table 2, p. 3591; Astiz et al. 1988, Table A, pp. 130–131). 1926 class hint in-slab with no reference ("agency depths of 90 to 180 km, slab top at 99 km (Pablo)"); the reason notes its absence from Astiz Table A, a point against. 1936, 1939, 1942: class hint in-slab and the table depth (80, 100, 140 km), σ 20, Astiz et al. (1988) p. 131. The table depths are compilations of the old determinations, not new ones.
- **Mw at the new depths** (Abe 1982 relation in `magnitude.py`; deep when z > 60 km). For an event with no location depth, the conversion already uses the depth of the A3 event file:
  - 1929: no change, Mw 7.8 (7.773 already from the intermediate relation; mB 7.4).
  - 1926: no change, Mw 7.3 (already intermediate).
  - 1939: 7.3 → **7.6** (mB 7.3, shallow 7.35 → intermediate 7.61).
  - 1942: 6.9 → **7.1** (mB 7.0, 6.87 → 7.13).
  - 1936: no change, Mw 7.0 (Ruiz and Madariaga value, not converted).
  - The new Mw of 1939 (7.6) is close to the in-slab maximum region of North Chile but below 1918 (7.8) and Calama 1950 (8.0); no Mmax change.
- **Weight moved if accepted:** arc crustal −0.15 (1929, 1926), forearc crustal −0.25 (1936 0.14, 1939 0.05, 1942 0.05), forearc interface −1.21 (1939, 1942) to in-slab.
- **Noted, not changed:**
  - 1916-08-25 (Mw 6.9) is classed outer rise in our catalogue; Astiz gives 21° S 68° W, 180 km (p. 130). Our location is probably wrong (A7).
  - Measured-depth events where Astiz differs: 1940-10-04 (24 vs 75 km), 1946-08-02 (39 vs 50), 1965-02-23 (42 vs 80), 1953-05-06 (66 vs 60). The A6 rule keeps measured depths.
  - 1925-05-15 is in Table A at 50 km; not an in-slab hint (interface depths).
- **Commit:** `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`; message: `A6 (A9 2c): proposed in-slab hints for 1929, 1926, 1936, 1939, 1942 (Abe and Kanamori 1979; Astiz et al. 1988)`. Add Astiz, Lay and Kanamori (1988) to REFERENCES.md if Pablo has not.
- **Accepted (Pablo, 16 Nov):** the in-slab hints and table depths of 1929, 1936, 1939 and 1942. 1926-04-28 stays `proposed` (no source with a page; absent from Astiz et al. 1988 Table A). Effect after the rerun: 1939 Mw 7.6, 1942 Mw 7.1; weight to in-slab 0.07 arc crustal, 0.25 forearc crustal, 1.21 interface.
- **Split no-depth events of Mw ≥ 7 after the hints** (frozen run, accepted hints of `overrides_A6.csv`): 61 events, 13 hinted, 48 not. The hints act only after the rerun (`locate.py` writes `a6_class_hint`), so a classification on the frozen locations still shows all 61. The events A7 named (1513, 1543, 1562, 1590, 1878, 1919, 1861, 1894, most of the 1800s) were never hinted: no source states their class.
- **NOAA NCEI tsunami database, checked directly** (Candia and Macedo's source and rule: validity 3 or 4 → interface; API `ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events`, Chile and Peru, 1400–1950, read 16 Nov). Candia's Table S1 is therefore not needed.
  - The hinted events agree: 1570, 1575-12, 1657 and 1869 have validity 3; 1604-11, 1822, 1835, 1849-11-17 and 1859 have 4. 1737 has 1 (its hint is from Ruiz and Madariaga).
  - Of the 48 unhinted, only **1920-08-20** (NOAA 1485, validity 3, M 7.0, central Chile) qualifies. 1928-12-02 matches NOAA 1609 of 1928-12-01, which is Talca, already hinted.
  - Validity 2 (questionable): 1513, 1562 (cause 2, questionable earthquake), 1590, 1784, 1851-05-26, 1906-12-26, 1913, 1925, 1931. Validity 1: 1582, 1681, 1833-09-18, 1878, 1933, 1940-10-11. Validity −1 (erroneous entry): 1829, 1851-04-02, 1861, 1871, 1909.
  - No NOAA tsunami: the other 25, including 1520, 1543, 1604-12-01, 1639, 1796, 1822-11-25, 1831, 1833-04-25, 1843, 1847, 1894, 1919.
- **Left without a literature class:** about 47 events, among them the backarc 1861 (Mendoza) and 1894 (San Juan) and the arc 1919 (41.4° S). Those three cannot be settled by a tsunami. They need Argentine and Chilean macroseismic studies, which are not in `refs/`. The rest is for A7's rule.
- **NOAA low-validity matches, what was reported** (runup records, API `tsunamis/runups`): the same-day entries exist, but validity grades whether a tsunami happened, not the earthquake. 7 of the 15 with validity 1–2 have no runup record at all (1513, 1681, 1906-12, 1913, 1925, 1931, 1940-10). The others have 1–2 reports, mostly without heights: 1562 Old Concepción (intensity 3.5; Lomnitz: possibly a storm), 1582 and 1590 Camaná (Peru), 1784 Camaná and Moquegua, 1878 Arica and Pisagua, 1933 Iquique. Two with heights: 1833-09-18 Arica 9 m (validity 1), and 1851-05-26 Caldera and Huasco 3 m (validity 2; Lomnitz 2004, p. 373, also reports a tsunami 10 ft at Huasco). 1851-05-26 has no interface weight today (in-slab 0.86, crustal 0.14).
- **Interface hints added, accepted (Pablo, 16 Nov):** 1920-08-20 (NOAA tsunami 1485, validity 3; Candia and Macedo rule) and 1851-05-26 (Lomnitz 2004 p. 373 and NOAA tsunami 783, validity 2; two reports). Weight after the rerun: 1920 forearc crustal −0.06; 1851-05-26 in-slab −0.86 and forearc crustal −0.14 to interface. Commit: `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`, message `A6 (A9): interface hints for 1920-08-20 and 1851-05-26 (NOAA tsunami database; Lomnitz 2004)`.
- **1513 (`cl15130101000000`, Mw 8.7, 17.21° S 72.30° W), from the A7 session.**
  - Sources: Cabello et al. (2025) take it from CERESIS-GEM (year only, Mw 8.69 ± 0.2, depth 30 km default, no remarks; CERESIS covers 1513–1963, Cabello Table 1). Not named in Ruiz and Madariaga (2018), Lomnitz (2004) or the Candia and Macedo text; in Candia's catalogue as GHE1513, IF by geometry only. NOAA: earthquake 680 (Peru, year only, M 8.7, intensity 8, depth 30) and tsunami 5488, validity 2, no runup records, labelled "Callao" (12° S) at 17.2° S. Its original source is probably Silgado (1978), not in `refs/`.
  - No source states a class: row added as the brief says, `class_hint interface`, no reference, reason "Mw 8.7: no in-slab or crustal source reaches this size (Pablo)", **proposed**.
  - Whether it belongs: it is inside the domain (cut at 15.5° S) and north of the seg4 band (17.6° S), so it counts only in the whole-margin interface unit, not in a segment. The A6 rule removes an event only when a source shows it is not real. Here the evidence is weak (year only, one compilation, a questionable tsunami at a mismatched place) but no source rejects it, so I recommend keeping it, with this note. If Pablo wants it out, it needs an `exists` row with his reason.
- **Noted for A7:** the brief's rule for pre-1900 events without a hint (no crustal share over the shallow slab) is A7's (phase 2). No further hints added here.
- **Commit:** `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`; message: `A6 (A9): proposed interface hint for 1513 (no source; Pablo)`
- **1513 interface hint accepted** (Pablo, 16 Nov); the event stays in the catalogue. 82 accepted class hints.

## 2026-11-16: A9 points 2 and 3, phase 1 (Claude Code, A7)

Read again: CLAUDE.md, DECISIONS, `tasks/A9_catalog_revision.md`. Nothing changed in `classify.py`, the frozen folder or the catalogue. Scripts in `explore/A9/` (run from `catalog/` with `PYTHONPATH=.`).

- **Point 2c, literature.** 1929-10-19: Abe and Kanamori (1979), Table 2, p. 3591, read on the page image: 10:12, 100 km, 23° S 69° W, M 7.5, mB 7.4. 1926-04-28: not in that table (mB 7.1, below its limit of 7.3); only agency depths in the ISC Bulletin (Gutenberg 180, ISC 90, ISC-GEM 130 ± 23 km). Both passed to A6, which added the hints (its entries above). Astiz et al. (1988) not opened by me.
- **Where the crustal weight of split events sits** (frozen run, Mw ≥ 4.5): forearc with interface, 1 121 events with a depth error (crustal weight 195.9; only 9.2 of it in events below the slab top) and 965 without a depth (69.0; 40 of Mw ≥ 7, 28 of them before 1900); forearc with in-slab only, 201 and 109 events; arc and backarc with in-slab, only events without a depth (74 and 144). The problem is the events without a depth, not the depth errors.
- **Tried and dropped:** leaving default depths out of the "every rejected depth ≥ 70 km" rule changes 3 events.
- **Rule chosen by Pablo (16 Nov), for phase 2:** an event before 1900 over the shallow slab, without a depth and without a hint, gets no crustal share; the share goes to interface and in-slab in proportion. Reason: a forearc crustal event large enough for the historical record is rare and its damage local; in-slab events are widely damaging (Chillán 1939, Calama 1950, Punitaqui 1997, Tarapacá 2005) and stay possible. Option (b) for every split event was not taken: it moves 137.5 of crustal weight at Mw ≥ 4.5 (forearc 90.4, arc 20.6, backarc 26.6), 28.8 at Mw ≥ 6, 4.5 at Mw ≥ 7.
- **Test file** `catalog/merged/classes_2026-11-16_test.csv`: frozen catalogue, the 82 accepted class hints, and the rule above (`rule = nodepth_share_pre1900`, 35 events). Not in it: the new magnitudes and the 1929 depth (they need the magnitude step). Weight moved, Mw ≥ 4.5 and Mw ≥ 6 are the same events:

| step | events | interface | in-slab | crustal | at Mw ≥ 7: events, interface, in-slab, crustal |
|---|---|---|---|---|---|
| new hints | 17 | +3.61 | −2.17 | −1.44 | 16, +4.21, −2.83, −1.39 |
| pre-1900 rule | 35 | +2.08 | +0.65 | −2.73 | 17, +1.12, +0.36, −1.48 |
| both | 52 | +5.69 | −1.52 | −4.17 | 33, +5.33, −2.46, −2.87 |

  All of the crustal weight comes from the forearc (4.10) but 0.07 from the arc. Still split without a depth at Mw ≥ 7 with a crustal share: forearc 17 events (1.66; 1904–1940 and pre-1900 over the deeper slab), arc 2 (0.46, mostly 1919-03-02), backarc 2 (0.89; 1861 Mendoza and 1894, which are probably crustal).
- **Point 3, arc boundary.** The arc polygon ends at 47.24° S; `SOUTH_LAT` is 46.15° S. Ending the arc at the polygon changes **no event** with crustal weight (any Mw ≥ 4.5). Faults that go from Patagonia to arc: database A, CL-006vv Teresa (46.51° S, 92 km) and CL-006yy San Rafael (46.68° S, 64 km); CL-006aaa Wager (47.84° S) stays Patagonia. Database B: MASCSN-146, 440 (Cachet), 498 (Teresa), 590 (Golfo de Penas), 731, 733, 734 (Exploradores). The fault class is set in `model/faults/compare.py`, `classes()`, from the fault midpoint with `classify.SOUTH_LAT`.
- **Seen on the way:** three events inside the arc polygon at 46.3–47.0° S are Antarctic interface with weight 1 by position: 1960-06-02 Mw 6.6 (18 km), 1977-05-12 Mw 5.4, 1999-05-01 Mw 5.0. They may be Liquiñe–Ofqui events. Not changed; for Pablo.
- **Proposed DECISIONS line:** "No depth, before 1900, over the shallow slab, no hint: the crustal share of the bin goes to interface and in-slab in proportion (Pablo, 16 Nov)." And, if point 3 is taken: "The arc class ends where the arc polygon ends (47.24° S), for events and faults; `SOUTH_LAT` stays for the trench side only."
- **Phase 2, after Pablo decides points 1 and 3:** I change `classify.py` (rule and boundary) with tests; then, with `RUN` set to `2026-11-16`: `locate.py`, `magnitude.py`, `locate.py`, `classify.py`, `locate_check.py`, `magnitude_check.py`, `classify_check.py`, `pytest`; freeze in `catalog/frozen/2026-11-16/`.
- **Commit:** `git add psha_chile8/explore/A9 psha_chile8/catalog/merged/classes_2026-11-16_test.csv psha_chile8/WORKLOG.md`; message: `A9 points 2 and 3, phase 1: test classes with the new hints and the pre-1900 rule; arc boundary list`

## 2026-11-16: A9 points 2 and 3, the two rules in `classify.py` (Claude Code, A7)

Pablo decided (16 Nov): the pre-1900 rule, and the arc class ends at the polygon. Both are in `catalog/classify.py`; no run made, the frozen folder untouched.

- **Pre-1900 rule:** `OLD = 1900`. In the shares step an event before 1900 over the shallow slab takes no crustal share (the column is set to 0 before the shares are normalised, the same as moving it in proportion). The rule name stays `nodepth_share`.
- **Arc end:** new `arc_end()`, the southern latitude of the arc polygon (47.24° S). `geometry()` sets Patagonia south of it. `SOUTH_LAT` stays for the trench side and the Antarctic interface only.
- **Check:** with the frozen catalogue and the 82 hints, the new code gives the weights of `classes_2026-11-16_test.csv` exactly. The sub-class differs in 8 events, all below Mw 4.5 or without Mw, now arc.
- **Tests:** two new (`test_no_depth_before_1900_takes_no_crustal_share`, `test_arc_class_ends_with_the_polygon`); `pytest catalog`: 126 pass. From `psha_chile8/`, `model/interface/tests/test_interface.py` fails at collection (`module 'build' has no attribute 'SEGS'`, a name clash between two `build.py`); alone it passes. Not mine, for S1.
- **For S3 (not changed by me):** `model/faults/compare.py`, `classes()`, uses `K.SOUTH_LAT` for Patagonia. To follow the events it should use `K.arc_end()` there. That moves CL-006vv and CL-006yy (database A) and seven sources of database B to the arc.
- **Script renamed:** `explore/A9/a9_test.py` is now `a9_classes.py` (pytest collected the old name).
- **Proposed DECISIONS lines:** as in the entry above (pre-1900 rule; arc class ends at the polygon, 47.24° S).
- **Still to do, phase 2:** after the A6 magnitude step, set `RUN` and run `locate.py`, `magnitude.py`, `locate.py`, `classify.py`, the three checks, `pytest`; freeze in `catalog/frozen/2026-11-16/`; `CLASSIFICATION.md` and the DATA row with that run.
- **Commit:** `git add psha_chile8/catalog/classify.py psha_chile8/catalog/tests/test_classify.py psha_chile8/explore/A9 psha_chile8/catalog/merged/classes_2026-11-16_test.csv psha_chile8/WORKLOG.md`; message: `A9: no crustal share for no-depth events before 1900 over the shallow slab; arc class ends at the arc polygon`

## 2026-11-16: A9, triple-junction events to outer rise (Claude Code, A7)

Pablo asked to see the classes around the Chile triple junction and decided (16 Nov) to class the cluster at the ridge–trench meeting point as outer rise.

- **Seen:** map `catalog/figs/classify/triple_junction.png` (script `explore/A9/a9_tj.py`, list `explore/A9/tj_events.csv`). About 20 events within 30 km east of the trench at 45.6–46.2° S were crustal, Patagonia (east of the trench line, no slab in Slab2). Of 13 mechanisms there, 10 are strike-slip with a plane near N 78° E, 2 normal, 1 oblique, no thrust; west of the trench at the same latitudes 26 strike-slip and 19 normal. One cluster of Chile Ridge fracture-zone events, cut by the trench line.
- **Rule, in `classify.py`:** `RIDGE = (-45.5, 75.0)`. Between 45.5° S and `SOUTH_LAT`, an event within 75 km east of the trench is outer rise. The 75 km come from the gap in the cluster (events to 73 km, the next at 119 km). Test `test_ridge_events_east_of_the_trench_are_outer_rise`; `pytest catalog`: 127 pass.
- **Effect** (frozen catalogue, 82 hints, Mw ≥ 4.5): 29 events to outer rise, the largest Mw 5.9; crustal Patagonia 77 → 54; in-slab −3.9, interface −0.6, unclassified −1. The shares of the 38–46° S bins move in the third decimal, so 84 no-depth forearc events change by that much.
- **Test file rewritten** with this rule: `catalog/merged/classes_2026-11-16_test.csv` (hints, pre-1900 rule, arc end, ridge rule). The fits session should use this version.
- **Not changed:** the events along the coast south of 46.15° S stay Antarctic interface (1960-06-02 Mw 6.6, 1963-05-19 Mw 6.4, 2024-11-08 Mw 6.3); their mechanisms were not checked.
- **Proposed DECISIONS line:** "Events within 75 km east of the trench between 45.5° S and 46.15° S are outer rise: Chile Ridge fracture-zone events (strike-slip and normal mechanisms), left out of the source model (Pablo, 16 Nov)."
- **Commit:** add `psha_chile8/catalog/figs/classify/triple_junction.png` to the lines of the entry above; message: `A9: pre-1900 rule, arc class to the end of the polygon, ridge events at the triple junction to outer rise`
- **Backarc 1861 and 1894, arc 1919: literature check** (A7 point: real large crustal events exist there, so they need hints, not a rule).
  - **1894-10-27 San Juan** (`cl18941027193000`, Mw 7.5, crustal 0.44 / in-slab 0.56). The MASCSN26 report (Bravo Sagua et al. 2026, `refs/hazard_chile/Mapa_Amenaza_CSN2026.pdf`), section 7.1.5, p. 117, names "M 7.5 en 1894" among the largest earthquakes of its crustal backarc zone Centro Este, "where the hypocentres of the most destructive earthquakes of Argentina lie". Giesecki et al. (2004), Table V, p. 431: a macroseismic source 54 km long, Mw 7.1, CERESIS depth 30 km. Crustal hint added, **proposed**.
  - **1861-03-20 Mendoza** (`cl18610320230000`, Mw 7.0, crustal 0.45 / in-slab 0.55). Salomon et al. (2013, BSSA 103, 936–949) attribute it to the 31 km La Cal thrust, with ~2 m of folding in a trench. I could read only their EGU 2013 abstract (EGU2013-1386, open); the BSSA paper is not open, so the source is †. MASCSN26 (p. 117) puts the Cerro La Cal fault in its crustal backarc zone but does not name 1861. Crustal hint added, **proposed**, with the † noted. To use it, the BSSA paper should be opened (Pablo's access).
  - **1919-03-02 03:26** (`cl19190302032635`, Mw 7.2, arc, crustal 0.38 / in-slab 0.62). No class in any source. Every depth is fixed at 15 km (Centennial, ISC-GEM, ISC). The epicentres are 500 km apart: Centennial 41.4° S 72.2° W (flagged poor) against ISC-GEM 43.8° S 78.3° W, west of the trench. A web search found no study. The arc class depends on the poor Centennial location; no hint, left to A7's rule.
  - Effect if both are accepted: backarc crustal +1.11 (0.55 + 0.56) from in-slab. The backarc crustal Mmax stays 7.7: 1977-11-23 Caucete (Mw 7.5) sets it, and 1894 at 7.5 equals it.
  - Sources: [Salomon et al. EGU 2013 abstract](https://meetingorganizer.copernicus.org/EGU2013/EGU2013-1386.pdf); BSSA doi 10.1785/0120110335 (not opened).
- **1919-03-02 03:26 epicentre moved to ISC-GEM** (Pablo, 16 Nov, simplest fix): `lon` and `lat` rows accepted, 43.814° S 78.294° W (ISC-GEM 912734, ± 31 km), ~250 km west of the trench. Reason: the Centennial epicentre (41.4° S 72.2° W) is flagged poor, and a Mw 7.2 there is absent from Lomnitz (2004) and NOAA. No class hint; A7's position rule classes it (expected outer rise / oceanic). The frozen run still has it as arc (in-slab 0.62, crustal 0.38). The 11:45 event of the same day is left as it is. Commit: `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`, message `A6 (A9): crustal hints 1894, 1861 proposed; 1919-03-02 03:26 epicentre to ISC-GEM`.
- **Crustal hints for 1894-10-27 and 1861-03-20 accepted** (Pablo, 16 Nov; 1861 rests on the Salomon et al. 2013 abstract †, accepted by Pablo). Backarc crustal +1.11 from in-slab after the rerun.

## 2026-11-16: A9 phase 2, chain run `2026-11-16` and frozen catalogue (Claude Code, A7)

Read again before the run: DECISIONS (no change that touches the classes). Pablo: Aysén stays Mw 7.7; run it.

- **Last rule changes (Pablo, 16 Nov):** the pre-1900 rule covers the whole forearc, whatever the slab depth (also where a bin has no shares); under the arc and backarc the shares stay and the large events got A6 hints. The 1926-04-28 in-slab hint set to `accepted` in `overrides_A6.csv` on Pablo's word ("accepted on the agency depths alone"): 100 accepted rows, none proposed.
- **Chain:** `locate.py`, `magnitude.py`, `locate.py`, `classify.py` (locations and magnitudes `2026-11-16a`, classes and catalogue `2026-11-16`), then `locate_check.py`, `magnitude_check.py`, `classify_check.py`; `pytest catalog`: 127 pass. A first run was stopped and restarted after the 1926 row changed.
- **Against `2026-11-14c`** (Mw ≥ 4.5 in the domain, 14 279 events in both):
  - Mw: 1939-04-18 7.3 → 7.6 and 1942-07-08 6.9 → 7.1, converted as intermediate-depth events at their new A6 depths (100 and 140 km). Aysén 7.7.
  - Position: 1919-03-02 Mw 7.2 moved by A6 to the ISC-GEM epicentre (43.8° S 78.3° W), now outer rise.
  - Depths: 4 from A6, 14 more assigned to hinted events (31 assigned in all); 12 395 measured, 1 853 unknown.
  - Classes: interface 4 502.8 (+5.1), in-slab 8 075.3 (−3.6), crustal 1 158.9 (−30.4: forearc 573.1, arc 221.1, backarc 310.7, Patagonia 54), outer rise 539 (+30), unclassified 3. 11 299 at weight 1; split 1 733 with a depth, 1 247 without.
  - Mw ≥ 7: 164 events, 37 split (62 before). Crustal weight in split no-depth events at Mw ≥ 7: forearc 0.9 (12 events of 1904–1940), arc and backarc none.
  - Checks: literature events by the rules alone 40 right, 34 no depth, 9 split, 2 wrong (as before); magnitude tests as before (test 3: 30 of 32).
- **Frozen:** `catalog/frozen/2026-11-16/` (catalogue, classes, shares, locations, Mw, defaults, relations, offsets, `overrides_A6.csv`, five scripts in `code/`, `SHA256SUMS` verified, `INPUTS_SHA256` the same as on 14 Nov, `DECISIONS_NOTE.md`). `catalog/frozen/2026-11-14/` untouched.
- **Documents:** DATA row; `catalog/CLASSIFICATION.md` new section 8 (sections 2–5 still give the numbers of `2026-11-14c`). Not brought to this run: `REPORT_A3-A5.md`, `MAGNITUDES.md`, `RULES_LOCATION_MAGNITUDE.md`, the paper draft.
- **Removed:** `catalog/merged/classes_2026-11-16_test.csv` (it lacked the forearc rule, the 1926 hint and the new magnitudes). The fits read `catalog/frozen/2026-11-16/catalog_2026-11-16.csv`.
- **For the other sessions:** B11/B12, refit on the new frozen catalogue (phase 2 step 3; Patagonia lost 23 of 77, the arc lost 1919 as a candidate, in-slab has 1939 at 7.6). S3: `model/faults/compare.py` `classes()` should use `K.arc_end()` instead of `K.SOUTH_LAT`. C14, B14, GM1 and the declustered catalogue were built on `2026-11-14c`.
- **Proposed DECISIONS lines (Pablo writes them):**
  - "No depth, before 1900, over the shallow slab or in the forearc: no crustal share; it goes to interface and in-slab in proportion. Under the arc and backarc the shares stay (16 Nov)."
  - "The arc class ends where the arc polygon ends (47.24° S), for events and faults; 46.15° S only chooses the trench (16 Nov)."
  - "Events within 75 km east of the trench between 45.5° S and 46.15° S are outer rise: Chile Ridge fracture-zone events, left out of the source model (16 Nov)."
  - "Frozen catalogue `2026-11-16` replaces `2026-11-14c`."
- **PLAN:** A9 not ticked; it closes with the refits.
- **Commit** (from the repo root):
  - `git add psha_chile8/catalog/classify.py psha_chile8/catalog/locate.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/tests/test_classify.py psha_chile8/catalog/overrides_A6.csv psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/figs/classify/triple_junction.png psha_chile8/explore/A9`
  - `git add psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/catalog/merged/*_2026-11-16a.* psha_chile8/catalog/merged/*_2026-11-16.csv psha_chile8/catalog/merged/review/*_2026-11-16a.csv psha_chile8/catalog/merged/review/*_2026-11-16.csv psha_chile8/catalog/frozen/2026-11-16`
  - `git add psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  - `git commit -m "A9: catalogue run 2026-11-16, frozen. No crustal share for no-depth events before 1900 in the forearc, arc class to the end of the polygon, Chile Ridge events at the triple junction to outer rise; A6 hints and depths applied"`

## 2026-11-16: A9 phase 2, fits rerun on the catalogue of 16 Nov (Claude Code, B11/B12)

Read again before starting and before finishing: `CLAUDE.md`, DECISIONS (A9 lines in Catalog, Classification, Superseded; unchanged while this ran), `tasks/A9_catalog_revision.md`. Asked by Pablo: the completeness table and the fits of `fits/run.py` only.

- **Run.** `fits/gr.py`: `CAT` → `catalog/frozen/2026-11-16/catalog_2026-11-16.csv` (checksum of the frozen file verified). `fits/run.py`: `DATE = "2026-11-16"`, nothing else. New files `fits/tables/table_2026-11-16.csv`, `mc_windows_2026-11-16.csv`, `fits_2026-11-16.csv`, `fits_sensitivity_2026-11-16.csv`; no older table touched. The figures have fixed names, so the 15b ones were first copied to `fits/figs/2026-11-15b/` and `fits/figs/*.png` (classes, interface segments, large-event check, b against floor, methods) are now of this run. 31 tests pass on the new catalogue. `fits/FITS.md` section 8.

Tapered fits (the cut-line fits move by the same amounts; both in the table). Mmax and corner are the same in both runs except where an arrow is given. Bold: outside the Poisson band in both runs.

| unit | Mmax | corner | b, 15b → 16 (sd) | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 fitted / observed, 15b → 16 |
|---|---|---|---|---|---|---|---|
| interface | 9.7 | 9.48 | 0.963 → 0.959 (0.018) | 25.20 → 25.22 | 2.745 → 2.772 (+1.0 %) | 0.299 → 0.305 (+1.9 %) | 54.5 / 49.7 → 55.7 / 51.6 |
| interface, 45.6–37° S | 9.7 | 9.47 | 0.915 → 0.909 (0.049) | 2.94 → 2.95 | 0.358 → 0.364 (+1.8 %) | 0.0435 → 0.0449 (+3.4 %) | 8.2 / 9.4 → 8.5 / 9.9 |
| interface, 37–32° S | 9.3 | 9.10 → 9.09 | 0.997 → 0.993 (0.033) | 8.48 → 8.49 | 0.854 → 0.862 (+1.0 %) | 0.0859 → 0.0875 (+1.8 %) | 15.3 / 12.1 → 15.6 / 12.6 |
| interface, 32–26° S | 8.7 | 8.48 | 0.941 → 0.939 (0.030) | 7.40 → 7.40 | 0.847 → 0.851 (+0.5 %) | 0.0965 → 0.0974 (+0.9 %) | **17.2 / 9.6 → 17.4 / 9.9** |
| interface, 26–17.6° S | 9.0 | 8.79 → 8.78 | 0.965 → 0.962 (0.039) | 5.71 → 5.72 | 0.620 → 0.623 (+0.6 %) | 0.0671 → 0.0679 (+1.1 %) | 12.1 / 15.1 → 12.2 / 15.3 |
| in-slab, shallow | 8.2 | 8.04 | 1.151 → 1.144 (0.039) | 9.24 → 9.22 | 0.652 → 0.662 (+1.4 %) | 0.0451 → 0.0465 (+3.1 %) | 6.7 / 7.5 → 6.9 / 8.3 |
| in-slab, intermediate depth | 8.2 | 8.04 | 1.154 → 1.157 (0.026) | 25.31 → 25.28 | 1.776 → 1.762 (−0.8 %) | 0.1219 → 0.1201 (−1.5 %) | **18.2 / 29.4 → 17.9 / 28.5** |
| Jujuy nest | 7.4 | 7.26 | 1.229 → 1.229 (0.090) | 3.74 → 3.74 | 0.219 → 0.219 | 0.0093 → 0.0093 | 1.1 / 2.4 → 1.1 / 2.4 |
| crustal, forearc | 7.4 | 7.19 | 0.982 → 0.984 (0.055) | 3.54 → 3.53 | 0.365 → 0.361 (−1.0 %) | 0.0250 → 0.0246 (−1.6 %) | 2.9 / 3.6 → 2.9 / 3.4 |
| crustal, arc | 7.9 | 7.70 | 1.002 → 1.023 (0.103) | 1.308 → 1.299 | 0.130 → 0.123 (−5.5 %) | 0.0120 → 0.0108 (−9.9 %) | 1.6 / 2.2 → 1.5 / 1.7 |
| crustal, backarc | 7.7 | 7.49 | 0.988 → 0.979 (0.069) | 2.30 → 2.31 | 0.235 → 0.241 (+2.5 %) | 0.0209 → 0.0218 (+4.6 %) | 2.7 / 2.1 → 2.8 / 2.4 |
| crustal, Patagonia | 8.0 | 7.79 | 0.982 → 0.984, forearc | 0.640 → 0.430 (−33 %) | 0.0667 → 0.0445 (−33 %) | 0.0066 → 0.0044 (−33 %) | 0.9 / 1.7 → 0.6 / 1.7 |

- **Completeness table:** unchanged (5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500). The Mc of every window and region is identical to the 15b run: completeness is read on all events, and the revision changed two magnitudes and no location.
- **What changed in the catalogue, as the fits see it:** 57 853 events of Mw ≥ 3.5 in the domain in both; two magnitudes (1939-04-18 7.3 → 7.6, 1942-07-08 6.9 → 7.1); class weights of 38–40 events each in the interface, shallow in-slab and forearc, 6 in intermediate in-slab, 3 in the arc, 1 in the backarc, 13 in Patagonia.
- **Patagonia:** 13 events (weight 13.0, all below Mw 6) became outer rise (Chile Ridge events at the triple junction): 41 → 28 events, rates −33 %. Mmax and corner unchanged (1949).
- **Arc:** three split no-depth events left (1919-03-02 Mw 7.2 to outer rise; 1926-04-28 Mw 7.3 and 1929-10-19 Mw 7.8 to in-slab; 0.53 of weight, all at Mw ≥ 7): b +0.021 (a fifth of its sd), N(≥ 6) −5.5 %, N(≥ 7) −10 %, observed Mw ≥ 7 2.2 → 1.7. Mmax still 7.9 (Aysén 1960 at 7.7). Moving the arc boundary to 47.24° S brought no event of Mw ≥ 5 into the table.
- **Forearc:** −1.5 of weight at Mw ≥ 7 (no crustal share before 1900): rates −1 to −2 %, observed Mw ≥ 7 3.6 → 3.4.
- **Interface:** +3.0 of weight at Mw ≥ 7: b −0.004, N(≥ 7) +1.9 %, branches a −0.02 and b −0.004 to −0.005.
- **In-slab:** shallow b −0.007, N(≥ 7) +3 %; intermediate N(≥ 7) −1.5 %, observed Mw ≥ 7 29.4 → 28.5.
- **Large-event check:** the same two failures (intermediate in-slab, segment 32–26° S), nothing new.
- **Over the thresholds of the A9 brief** (0.02 in b, 5 % in N(≥ 6), 0.1 in Mmax): the arc (b by 0.021, N(≥ 6) by 5.5 %) and Patagonia (33 %). Nothing in the interface or in-slab units, and no Mmax or corner moved.
- **Not done here:** `fits/run_declustered.py` and the declustered catalogues (`fits_declustered_2026-11-16.csv`, step 3 of the brief) were not asked for in this request and are still of 15 Nov on the old catalogue. `gr.CAT` now points at the new catalogue, so anything in `fits/` run from now on reads it; `sigma.py` and `compare.py` (synthetic part) were not rerun. A9 is not ticked in PLAN for that reason.
- **Downstream:** S3 (arc and Patagonia background) is over the thresholds and needs the new rates. S1 and S2 are under them (largest: segment 45.6–37° S N(≥ 6) +1.8 %, b −0.006; shallow in-slab b −0.007); they read `fits_2026-11-15b.csv` and change only if rebuilt for consistency. B14: only through the arc and Patagonia rates.
- **Proposed lines for DECISIONS** (Pablo adds):
  - Statistics: "Fits on the catalogue of 16 Nov: `fits/tables/fits_2026-11-16.csv` replaces `fits_2026-11-15b.csv` (kept); same table, methods, Mmax and corner. The completeness table did not change (A9, 16 Nov)."
  - Superseded: "Fits `fits_2026-11-15b.csv` on catalogue 2026-11-14c → `fits_2026-11-16.csv` on catalogue 2026-11-16 (arc b 1.00 → 1.02, Patagonia N(≥ 5) 0.64 → 0.43; other units within 2 % at N(≥ 6))."
- **Proposed line for LEARNINGS** (Completeness): "The completeness table read on all events did not move when classes and two magnitudes were revised (A9): reclassification cannot change it."
- **Commands** (from `psha_chile8/fits/`): `python run.py` (95 s). Still to run for A9 step 3: `python run_declustered.py` with a new date, after the declustered catalogues are rebuilt on the new catalogue.
- **Suggested commit:** `git add psha_chile8/fits/gr.py psha_chile8/fits/run.py psha_chile8/fits/FITS.md psha_chile8/fits/figs psha_chile8/fits/tables/table_2026-11-16.csv psha_chile8/fits/tables/mc_windows_2026-11-16.csv psha_chile8/fits/tables/fits_2026-11-16.csv psha_chile8/fits/tables/fits_sensitivity_2026-11-16.csv psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `A9: fits rerun on the catalogue of 2026-11-16 (completeness table unchanged; arc and Patagonia rates move)`.


## 2026-11-16 — C14 rerun on the A9 catalogue (run 2026-11-16)

- **Done:** in-slab depth model rerun with the settings of `2026-11-15e` (zone to 0.475 of the Slab2 thickness, three slices, kernel weights, Jujuy nest removed first) on `catalog/frozen/2026-11-16/catalog_2026-11-16.csv`. `depth.CAT` now points at it; `run.py`: `RUN = "2026-11-16"`, a per-cell comparison against `PREV` (`depth_cells_2026-11-15e.csv`), figures written to `figs/2026-11-16/` so the 2026-11-15e figures stay. Old tables untouched. Tests: 19 passed (cell-table test now reads the newest table).
- **What moved against 2026-11-15e:** nothing. `depth_events_` and `depth_cells_2026-11-16.csv` are byte-identical to `_2026-11-15e`: in 13 847 cells weights, hypocentres (h1–h3, one layer), lower depth and double-zone index change by 0.000 (`compare_2026-11-15e_2026-11-16.csv`). Fraction 0.4746 in both; held-out log-likelihoods identical (kernel −0.794, 50 nearest −0.784, equal −1.099); figures identical.
- **Why:** the A9 changes touch no-depth events, pre-1990 events and the triple junction. Two in-slab events with measured depths after 1990 left the class (cl20030620042327 Mw 5.3 and cl20141113163527 Mw 4.1, 45.6–45.7° S, 76.0° W, now outer rise under the Chile Ridge rule); their depths came from CSN-ISC and ComCat, which the model already drops. Only the all-depths sensitivity case sees them: 107 480 → 107 478 events, fraction 0.6152 → 0.6151. Riedel-Hornig selection unchanged (40 654 events; the A7 depth rule did not change).
- **DECISIONS.md** re-read at the start and end: the A9 lines (Catalog, Classification, Superseded) do not touch the depth rules; choices of C14 hold.
- **Proposed lines** (Pablo adds):
  - Depths: "In-slab depth model run `2026-11-16` on the catalogue of 16 Nov replaces `2026-11-15e` (kept); identical cells (C14, 16 Nov)."
  - Superseded: "In-slab depth cells `2026-11-15e` on catalogue 2026-11-14c → `2026-11-16` on catalogue 2026-11-16 (no change)."
- **Commands:** from `psha_chile8/model/inslab/`: `python run.py` (9 min).
- **Suggested commit:** `git add psha_chile8/model/inslab/depth.py psha_chile8/model/inslab/run.py psha_chile8/model/inslab/tests/test_depth.py psha_chile8/model/inslab/figs/2026-11-16 psha_chile8/model/inslab/tables/*_2026-11-16.csv psha_chile8/DATA.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `C14: in-slab depth model rerun on the catalogue of 2026-11-16 (run 2026-11-16, cells unchanged)`.

## 2026-11-16: A9 phase 2, declustered catalogues and fits rerun on the catalogue of 16 Nov (Claude Code, B11/B12)

Asked by Pablo after the full-catalogue rerun (entry above). DECISIONS read again before and after: no change that touches this.

- **Run.** `fits/decluster.py` and `fits/run_declustered.py`: `DATE = "2026-11-16"`, nothing else (`gr.CAT` already on the new catalogue). No file of 15 Nov touched; the three `figs/declustered_*.png` of 15 Nov copied to `fits/figs/2026-11-15/` before regenerating. 31 tests pass. `fits/DECLUSTER.md` section 6.
- **Declustered catalogues** `catalog/declustered/{gk,gk_family,nn,nn_depth,nn_family}_2026-11-16.csv` and the `_m35_` files: same settings. Mainshocks kept at Mw ≥ 4.5 (of 14 279): Gardner–Knopoff 5 171 (unchanged), per family 6 006 (6 013 before), nearest neighbour 10 068 (unchanged), with depth 9 934 (9 939), per family 10 923 (10 926). Thresholds of log10 η: −5.52, −5.31, −5.75 (−5.52, −5.32, −5.75 before). Only the per-family methods and the depth variant can change: the revision moved classes and no location; the depth variant differs by 5 events through the threshold.
- **Completeness tables of the declustered catalogues:** unchanged for all five methods (Gardner–Knopoff: 5.0 from 1976, 5.1 from 1964, 6.0 from 1950, 6.5 from 1890, 7.0 from 1825, 8.0 from 1500; nearest neighbour: the same with 6.5 from 1900 and 7.0 from 1830).
- **Fits** `fits/tables/fits_declustered_2026-11-16.csv` (352 rows, same layout), with `declustered_tables_`, `declustered_removed_`, `declustered_compare_` and `declustered_floor_2026-11-16.csv`. Mmax of every unit unchanged; corners within 0.01.
- **What moved against `fits_declustered_2026-11-15.csv`** (tapered, the two options of the declustering factor, table of the full catalogue, own b):

| unit | Gardner–Knopoff per family: b | N(≥ 6) | N(≥ 7) | nearest neighbour per family: b | N(≥ 6) | N(≥ 7) |
|---|---|---|---|---|---|---|
| interface | 0.766 → 0.758 | +1.8 % | +3.6 % | 0.899 → 0.893 | +1.5 % | +3.0 % |
| interface, 45.6–37° S | 0.836 → 0.823 | +3.7 % | +6.9 % | 0.888 → 0.875 | +3.6 % | +6.8 % |
| interface, 37–32° S | 0.660 → 0.653 | +1.9 % | +3.5 % | 0.895 → 0.890 | +1.5 % | +2.9 % |
| interface, 32–26° S | 0.762 → 0.758 | +1.1 % | +2.0 % | 0.887 → 0.884 | +0.8 % | +1.5 % |
| interface, 26–17.6° S | 0.845 → 0.841 | +1.0 % | +1.8 % | 0.941 → 0.938 | +0.8 % | +1.5 % |
| in-slab, shallow | 0.984 → 0.975 | +1.4 % | +3.3 % | 1.120 → 1.111 | +1.8 % | +3.9 % |
| in-slab, intermediate depth | 1.000 → 1.004 | −1.0 % | −1.8 % | 1.146 → 1.149 | −0.8 % | −1.5 % |
| Jujuy nest | 0.767 → 0.767 | 0 | 0 | 1.223 → 1.223 | 0 | 0 |
| crustal, forearc | 0.853 → 0.856 | −1.3 % | −1.9 % | 0.958 → 0.962 | −1.4 % | −2.1 % |
| crustal, arc | 0.909 → 0.936 | −6.8 % | −12.1 % | 0.951 → 0.974 | −6.1 % | −10.9 % |
| crustal, backarc | 1.020 → 1.004 | +4.4 % | +8.1 % | 1.064 → 1.050 | +3.9 % | +7.2 % |
| crustal, Patagonia | forearc b | −37 % | −38 % | forearc b | −33 % | −34 % |

- The moves follow the full catalogue: Patagonia loses a third (the triple-junction events), the arc loses its three split events of Mw ≥ 7, the interface gains at the top. With the declustered tables the backarc is also over 5 % at N(≥ 6) (+5.4 to +5.8 %, b −0.02).
- **Large-event check:** no unit changes its result in any method, table or shape (intermediate in-slab still fails with the nearest-neighbour catalogues and passes with Gardner–Knopoff).
- **Over the thresholds of the A9 brief** (0.02 in b, 5 % in N(≥ 6), 0.1 in Mmax), for the two options: the arc and Patagonia in every case, the backarc on the declustered tables. No interface or in-slab unit, no Mmax.
- **Downstream:** S3 (arc, Patagonia; backarc if it uses the declustered table) needs the new rates and the new mainshock flags for its pattern. S1 (declustered interface branch) and S2 are under the thresholds; their patterns change only through 7 (Gardner–Knopoff per family) or 3 (nearest neighbour per family) events of 14 279. Anything that reads `catalog/declustered/*_2026-11-15.csv` or `fits_declustered_2026-11-15.csv` by name still gets the old catalogue.
- **PLAN:** the A9 line now says the B11 and B12 reruns are done; A9 itself is not ticked (C14, B14, S1–S3 belong to other sessions).
- **Proposed lines for DECISIONS** (Pablo adds):
  - Statistics: "Declustered catalogues and fits on the catalogue of 16 Nov: `catalog/declustered/*_2026-11-16.csv`, `fits/tables/fits_declustered_2026-11-16.csv` replace those of 2026-11-15 (kept); settings and completeness tables unchanged (A9, 16 Nov)."
  - Superseded: "Declustered fits `fits_declustered_2026-11-15.csv` on catalogue 2026-11-14c → `fits_declustered_2026-11-16.csv` (arc N(≥ 6) −6 to −7 %, Patagonia −33 to −37 %, others within 5 % for the two options)."
- **Commands** (from `psha_chile8/fits/`): `OMP_NUM_THREADS=1 python decluster.py` (3 min), then `OMP_NUM_THREADS=1 python run_declustered.py` (3 min).
- **Suggested commit:** add to the commit of the entry above `psha_chile8/fits/decluster.py psha_chile8/fits/run_declustered.py psha_chile8/fits/DECLUSTER.md psha_chile8/fits/tables/*declustered*_2026-11-16.csv psha_chile8/catalog/declustered/*_2026-11-16.csv psha_chile8/PLAN.md`; message `A9: fits and declustered catalogues rerun on the catalogue of 2026-11-16`.


## 2026-11-16 — C15 brief written

- `tasks/C15_inslab_depth_options.md`: one-layer hypocentre, w1 check, lower-depth options (0.475 reference; 0.65, 0.615), rupture geometry options, job files for the tornado, south of 36° S.
- **Found:** the one-layer hypocentre of C14 (`h_one`, the median of the zone per cell, used by S2) jumps by about 10 km at the 50 km contour of the slab top: 20–23 km below the top over the shallow slab, 11 km at 50–70 km. Cause: the ± 15 km interface band of A7 removes the shallow in-slab events near the top. The median of d / thickness over all the events is 0.248 (0.252 with the events outside the zone), close to the zone middle (0.2375). Proposed in the brief: h_one = top + 0.25 × thickness, one rule. The top-slice weight w1 shows the same cut (0.2–0.3 against 0.5).
- Suggested commit: `git add psha_chile8/tasks/C15_inslab_depth_options.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `C15 brief: in-slab depth options (one-layer rule, lower depth, rupture geometry)`.

## 2026-11-16: B14 rerun on the A9 catalogue (Claude Code)
- **Done.** `model/mechanisms/npd.py` reads `catalog/frozen/2026-11-16/catalog_2026-11-16.csv` and `fits/tables/table_2026-11-16.csv` (settings `DATE`, `CAT`, `TABLE`, `PREV` at the top; `CAT` is now explicit instead of the default of `fits/gr.py`). New: `npd_2026-11-16.csv`, `tables/{counts,shares,moved}_2026-11-16.csv`, `figs/ternary.png` (copies `ternary_2026-11-16.png`, and `ternary_2026-11-15.png` for the earlier run). `REPORT_B14.md` rewritten for 2026-11-16 with a section "What moved against 2026-11-15" (type weights and Kagan angle per class and type; `kagan()` added, with a test). Tests: 3 pass. The 2026-11-15 files are kept.
- **What moved.** Only the A9 change of the Chile Ridge events to outer rise acts: 10 mechanisms inside completeness left (8 Patagonia strike-slip, 1 shallow in-slab normal, 1 forearc / shallow split strike-slip). Patagonia 26 → 18 weighted: N / R / SS 0 / 0.16 / 0.84 → 0.06 / 0.22 / 0.72; strike-slip mechanism 55/75/−175 → 115/75/0 (37°, now the Magallanes–Fagnano strike); the normal type is one event (2003-09-12, Mw 5.5, 1 of 18 = 5.6 %, a vertical plane with rake −90). Forearc strike-slip (weight 0.08, 71 % oblique) moved 72° on the loss of one split event: unstable, small weight. Shallow in-slab: two planes cross a 5° rounding step. Intermediate in-slab, Jujuy nest, arc, backarc: identical.
- **Open for Pablo:** whether a type resting on one event (Patagonia normal) should pass; a minimum count per type (e.g. at least a few weighted events, besides 5 %) would drop it, but that is a new rule, not made here.
- **Proposed DECISIONS lines (not edited):** In-slab and Crustal and faults, the B14 line to read `npd_2026-11-16.csv` instead of `npd_2026-11-15.csv`; Superseded: "Nodal planes `npd_2026-11-15.csv` (catalogue 2026-11-14c) → `npd_2026-11-16.csv` (A9, 16 Nov); moved: Patagonia (Chile Ridge events out), forearc strike-slip plane; other classes identical." DECISIONS re-read: the A9 lines (Classification, Superseded) are what this run follows; nothing else changed that touches B14.
- **Suggested commit:** `git add psha_chile8/model/mechanisms psha_chile8/DATA.md psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `B14 rerun on the A9 catalogue: npd_2026-11-16.csv, moves against 2026-11-15 (Patagonia without the Chile Ridge events, forearc strike-slip plane), Kagan angle table`

## 2026-11-16: B14, Patagonia from the forearc (Claude Code)
- **Decided (Pablo):** Patagonia takes the nodal-plane distribution of the forearc, as it takes the forearc b. `npd.py`: `BORROW = {"patagonia": "forearc"}` next to the class settings. `npd_2026-11-16.csv` and `tables/moved_2026-11-16.csv` rewritten (Patagonia rows = the six forearc rows; every other class unchanged); counts and shares unchanged (Patagonia's own shares still reported). `REPORT_B14.md` updated. Tests: 3 pass.
- **Effect:** Patagonia N / R / SS 0.29 / 0.63 / 0.08 (forearc) instead of its own 0.06 / 0.22 / 0.72; against 15 Nov (0 / 0.16 / 0.84) strike-slip falls from 0.84 to 0.08, so the GMM style-of-faulting term of Patagonia moves from strike-slip to mainly reverse. The one-event normal type of Patagonia is gone with it.
- **Proposed DECISIONS line (Crustal and faults, replaces the B14 line):** "Nodal planes per class from the catalogue mechanisms (B14, `npd_2026-11-16.csv`); Patagonia takes the forearc distribution (Pablo, 16 Nov); used from S5; not a tornado factor." In-slab line as proposed in the previous entry.
- **Suggested commit:** as the previous entry; message `B14 rerun on the A9 catalogue: npd_2026-11-16.csv, Patagonia takes the forearc distribution, moves against 2026-11-15`

## 2026-11-16: S1 rerun on the A9 fits (Claude Code)
- **Read again:** CLAUDE.md, DECISIONS (A9 lines in Catalog, Classification, Superseded), `tasks/A9_catalog_revision.md`. No S1 choice changes: Mmax rule, list end, weights and scaling as on 15 Nov.
- **Done.** `model/interface/if_build.py` reads `fits/tables/fits_2026-11-16.csv` and `fits_declustered_2026-11-16.csv`; margin-b refit (`fits/run.py`, catalogue 2026-11-16). New, dated 2026-11-16, nothing of 15 Nov overwritten: `tables/{rates,closure,area_check,fits_marginb,moved}_2026-11-16.csv`, `geometry/*_2026-11-16.*` (identical), `nrml_2026-11-16/` (240 files, `branches.json`, `source_lt_interface.xml`, 216 paths), `oqcheck_2026-11-16/` (jobs written, not run: left for the end at Pablo's word). `figs/` redrawn. REPORT_S1 section 6.
- **pytest clash fixed:** the interface modules are renamed `if_build.py`, `if_geom.py`, `if_mfd.py`, `if_nrml.py`, `if_figs.py`, `if_oqcheck.py` (they clashed with `build`, `nrml`, `figs`, `oqcheck` of inslab and crustal). `pytest` from `psha_chile8/`: interface collects and passes (10); 299 pass, 3 fail in `model/inslab/tests/test_s2.py`, a separate clash between `model/crustal/smooth.py` and `model/inslab/smooth.py` (inslab alone: 14 pass; interface + inslab: 29 pass). Not mine, for S2/S3. FIGURES rows 43–45 point to `if_build.py`.
- **What moved** (reference tree, weight-averaged; `tables/moved_2026-11-16.csv`): b −0.003 to −0.010; N(≥ 5.5) margin −1.7 %, segments −4.5 / −1.4 / −0.8 / −1.2 %, Antarctic −4.2 %; N(≥ 8) +0.3 to +1.6 %. Seismic full, own b, tapered, central: N(≥ 8) +1.4 to +4.9 % (45.6–37° S largest). Per branch N(≥ 8) −2 to +12 % (declustered own b, 45.6–37° S). Mmax, corners and list ends unchanged; closure margin 0.59 → 0.61. All under the A9 thresholds.
- **Proposed DECISIONS lines** (Pablo adds):
  - Interface, sources line: "... one NRML file per branch (`model/interface/nrml_2026-11-16/branches.json`, on the A9 fits 2026-11-16) ..." instead of `nrml/branches.json`.
  - Superseded: "Interface sources `model/interface/nrml/` on fits 2026-11-15b → `nrml_2026-11-16/` on the A9 fits (16 Nov): b −0.003 to −0.010, N(≥ 8) +0.3 to +1.6 % in the tree; Mmax unchanged."
- **Commands** (from `psha_chile8/model/interface/`, `PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine`): `python if_build.py` (50 s); at the end `cd oqcheck_2026-11-16 && oq engine --run job_margin.ini` and `job_seg.ini`, then set `CALCS` in `if_oqcheck.py` and run it.
- **Suggested commit:** `git add -A psha_chile8/model/interface psha_chile8/FIGURES.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `S1 rerun on the A9 fits (2026-11-16); interface modules renamed if_* for pytest`.

## 2026-11-16, S2 rerun on the A9 catalogue (in-slab sources)
- **Done:** `model/inslab/build.py` on catalogue `2026-11-16`, `fits_2026-11-16.csv`, declustered `gk_family_2026-11-16.csv` / `nn_family_2026-11-16.csv` (pattern and kernel calibration) and `depth_cells_2026-11-16.csv` (identical to 2026-11-15e). New dated outputs: `model/inslab/tables/*_2026-11-16.csv`, `tables/bins/rates_*_2026-11-16.csv.gz`, `nrml/2026-11-16/` (72 files, `branches.json`, `source_lt_inslab.xml`), `figs/2026-11-16/`, `oqcheck/2026-11-16/` (job files only). The 15 Nov files stay in `nrml/`, `figs/`, `oqcheck/`. Nodal planes unchanged (B14 at S5). Report: `model/inslab/REPORT_S2.md` section 7.
- **What moved per class** (ML (a, b)):
  - shallow: b 1.151 → 1.144; N(≥ 6) +1.4 %, N(≥ 7) +3.1 %; Mmax 8.2 and corner 8.04 unchanged; the in-slab shares of the great historical interface events go to 0 (A9 hints);
  - intermediate: b 1.154 → 1.157; N(≥ 6) −0.8 %, N(≥ 7) −1.5 %; Mmax 8.2 unchanged;
  - Jujuy nest: unchanged.
  - None passes 0.02 in b, 5 % in N(≥ 6) or 0.1 in Mmax.
- **Kernel n** (Pablo, 16 Nov): the curve is scored at n 1, 3, 5, 10, 15, 25, 50, 100 (kept for analysis); n is the first local maximum from n = 5 up (`smooth.first_max`, `N_MIN = 5`; n = 1 for the intermediate class is unreasonable). Chosen: shallow 5 (gk) / 10 (nn), intermediate 5 / 5, Jujuy nest 5 / 5 (without the floor: intermediate 1 / 1, nest 3 / 1). Pattern shift against 15 Nov: 1.1–2.0 % in every class. The intermediate test events repeat the training locations (median 12 km to the nearest training event, as between training events); a smooth n = 10 pattern would make n = 1 lose by 46, it wins by 28 (REPORT_S2 section 7). Figure `figs/2026-11-16/kernel_loglik.png`.
- **Completeness weights** (Pablo, 16 Nov): pattern events weighted w / (t_end − T_c(m)), training events of the calibration w / (2010 − T_c(m)); test events unweighted (one period). n picks unchanged; 1.2–2.3 % of the rate moves. No magnitude scaling, no lower-year cut.
- **Checks:** 20 tests pass; edge check 1.5e-14; all 72 files read by the OpenQuake parser (`tables/oqread_2026-11-16.csv`). Calama engine run stopped before the end (Pablo: fits and SSM parameters first).
- **Code:** `build.py` settings to the 16 Nov inputs (`CAT` explicit, NRML in `nrml/<DATE>/`); `oqcheck.py` job folder `oqcheck/<DATE>/`; `figs_s2.py` figures in `figs/<DATE>/`, pattern maps as a cell mesh (pituplots `Grid.from_points` + `plot_grid`) instead of square markers; a stale `N5` column name in the build print fixed.
- **DECISIONS re-read** (A9 lines, In-slab): choices hold.
- **Proposed DECISIONS lines** (Pablo adds):
  - In-slab, replace the kernel n line: "In-slab kernel n, calibrated (S2, 16 Nov, A9 catalogue): scored at n 1, 3, 5, 10, 15, 25, 50, 100; n is the first local maximum of the test log-likelihood from n = 5 up, a second maximum at large n is ignored (Pablo, 16 Nov). Shallow 5 (Gardner–Knopoff) / 10 (nearest neighbour), intermediate 5, Jujuy nest 5; without the floor the intermediate class would take 1 (`model/inslab/tables/calibration_2026-11-16.csv`)." In Statistics / kernel line: "candidates 5–100" → "scored at 1–100, n the first local maximum from 5".
  - In-slab, after the kernel line: "Pattern events enter as rates: class weight over the completeness period of their magnitude, w / (t_end − T_c(m)); in the calibration the training events over T_c(m) to 2010. No magnitude weighting and no fixed start year (Pablo, 16 Nov, S2)."
  - Superseded: "In-slab sources `model/inslab/nrml/` on catalogue 2026-11-14c and fits 2026-11-15b → `nrml/2026-11-16/` on the A9 catalogue and fits (16 Nov): shallow b −0.007, N(≥ 7) +3 %; intermediate b +0.003, N(≥ 7) −1.5 %; Mmax and corners unchanged; n chosen as the first local maximum from 5 (curve scored 1–100), completeness weights on the pattern events; n unchanged except shallow nn 10 (as 15 Nov)."
- **Commands** (from `psha_chile8/model/inslab/`): `python build.py` (2.5 min), `python figs_s2.py`; later the Calama check: `cd oqcheck/2026-11-16 && oq engine --run job_ps100.ini`, calc id into `CALCS` of `oqcheck.py`, then `python oqcheck.py`.
- **Suggested commit:** `git add psha_chile8/model/inslab/{build,oqcheck,figs_s2,smooth}.py psha_chile8/model/inslab/tests/test_s2.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/{calibration,edge_check,kernel_n,nest_depths,oqread,pattern,pattern_sums,rates,south36_layers}_2026-11-16.csv psha_chile8/model/inslab/figs/2026-11-16/{pattern_gk,pattern_nn,sections_sources,mfd_sources,kernel_loglik}.png psha_chile8/model/inslab/nrml/2026-11-16/{branches.json,source_lt_inslab.xml} psha_chile8/model/inslab/oqcheck/2026-11-16/*.{ini,xml} psha_chile8/PLAN.md psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`; message `S2 rerun on the A9 catalogue (2026-11-16): in-slab sources on fits 2026-11-16, declustered 2026-11-16 and depth cells 2026-11-16; kernel n first local maximum from 5 (curve scored 1-100), completeness weights on pattern events; pattern maps as cell mesh; log-likelihood figure`.
- **S1 addendum (16 Nov):** `figs/mfds.png` redrawn in three rows (`if_figs.mfds`): seismic fit of the full catalogue (own b, tapered, (a, b) 5–95 % band, cut line, completeness steps from `fits/tables/table_2026-11-16.csv`, as `fits/figs/fmd_interface_segments.png`); rate branch sets of the tree as weighted means (seismic full / Gardner–Knopoff / nearest neighbour, geodetic χ 0.7–0.9, tree mean); tornado options (cut shape, shared b, margin b) as ratios to the reference. Then, at Pablo's word: tornado row and Antarctic panel removed, pituPLOTS style (`darkgrid`, fmd colours and markers), shorter legend labels; 2 rows × 5 panels. FIGURES row updated.

## 2026-11-16 — S3 rerun on the A9 catalogue (crustal)
- **Done:**
  - Crustal code on catalogue 2026-11-16, `fits_2026-11-16.csv` and the 2026-11-16 declustered families. Fault databases and grid stay 2026-11-15.
  - Reran `background.py`, `faults.py`, `join.py`, `large.py` and `arc.py`. New tables and figures are dated 2026-11-16; the 2026-11-15 ones are kept.
  - No NRML files (Pablo: fits checked first). `build.py` now writes to `nrml/2026-11-16/` when it is run.
  - Report: `model/crustal/REPORT_S3.md` section 8. Tests: 12 passed, 2 skipped (the NRML files are not built).
- **Shared module changed at Pablo's request (A7 message):** in `model/faults/compare.py`, `classes()` now uses `classify.arc_end()` (47.24° S) instead of `SOUTH_LAT`.
  - Moved to the arc: CL-006vv and CL-006yy (A); MASCSN-146, 440, 498, 590, 731, 733 and 734 (B and B-mm), as A7 listed.
  - `d16b_*` tables of compare.py were not rerun.
- **Kernel:** on the new catalogue, the nearest-neighbour calibration of the crustal family prefers n = 50. The arc and Patagonia would have borrowed it.
  - DECISIONS fixes n = 5, so `background.py` now uses `N_FIX = 5`. The calibrated value stays in `kernel_n_2026-11-16.csv` (`n_cal`) as a diagnostic.
- **What moved:**
  - Faults / fit at Mw 6, arc: A 3.3 → 3.7, B 8.8 → 10.1, B-mm 4.6 → 5.2. Arc fit N6 is −5.5 % and the faults gained the moved traces.
  - Patagonia: A 1.3 → 1.65, B 3.6 → 3.5, B-mm 1.4 → 1.3 (fit −33 %, faults moved out).
  - Forearc and backarc: within 0.01.
  - Arc count test, share of the tree that passes: A 8 → 6 %, B 0 %, B-mm 6 %. Class maximum: A_cm 94 %, B_cm 46 → 35 %, Bmm_cm 96 → 92 %.
  - Puerto Aysén Mw ≥ 6 within 50 km: +1 % for every database. The no-faults background is −7 %.
  - Mmax unchanged.
- **DECISIONS was re-read** (A9 lines in Catalog, Classification and Superseded). My choices still hold.
- **Proposed DECISIONS lines:**
  - Classification: "Crustal faults take the arc class to `classify.arc_end()` (47.24° S), the boundary of the events (`model/faults/compare.py`, A9, 16 Nov)."
  - Superseded: "Crustal tables on fits 2026-11-15b → 2026-11-16 (S3, 16 Nov). Arc faults / fit at Mw 6: A 3.3 → 3.7, B 8.8 → 10.1, B-mm 4.6 → 5.2. Patagonia fit −33 %."
- **Open: branch structure (for Pablo).** Proposed:
  - One fault-system level with two branches:
    - (1) Segmented: single faults, the six MFD shapes, Leonard Mmax.
    - (2) Multi-fault: Liquiñe–Ofqui linked by the UCERF3 filters, SHERIFS partition, Leonard on the linked area, capped at the class Mmax.
  - No separate Mmax level. The class maximum on single faults stays a sensitivity, because it needs about 38 m of slip.
  - Tornado: A, B and B-mm.
  - Before the full set: the LOFS quick estimate on the new fits (main traces, 10 km depth, ψ 0.6 / 0.8 / 1.0, jumps 5 / 10 / 15 km, 10 seeds).
- **Commands (Pablo, when the fits are settled):** from `psha_chile8/model/crustal/`: `python build.py`, then `python oqcheck.py` (parse check).
- **Note:** the old OpenQuake jobs for A, B and B-mm (15 Nov) ended with exit code 144 and no result.
- **Suggested commit:** `git add psha_chile8/model/crustal/{background,faults,join,large,arc,kernels,multifault,build}.py psha_chile8/model/crustal/tests/test_crustal.py psha_chile8/model/crustal/REPORT_S3.md psha_chile8/model/crustal/tables/*2026-11-16* psha_chile8/model/crustal/figs/*2026-11-16* psha_chile8/model/faults/compare.py psha_chile8/WORKLOG.md` — message: "S3: crustal rerun on the A9 catalogue and fits 2026-11-16; faults use the arc_end boundary; kernel n fixed at 5"
- **Decided by Pablo (16 Nov): crustal fault-system level with two branches.** Proposed DECISIONS lines:
  - Crustal and faults: "Crustal fault system, two branches (Pablo, 16 Nov): (1) segmented: single-fault simple-fault sources, the six MFD shapes, Leonard (2014) Mmax; (2) multi-fault: Liquiñe–Ofqui faults linked by the UCERF3 plausibility filters (Milner et al. 2013), rates by the SHERIFS moment partition (Chartier et al. 2017, 2019), Leonard Mmax on the linked area, capped at the class Mmax. Other faults are the same in both branches. No separate Mmax level; the class maximum on single faults stays a sensitivity. Weights open."
  - Superseded: "Multi-fault ruptures: not in the model (Oct) → the multi-fault branch of the crustal fault system (16 Nov)."
  - Open before the full set: jump distance, ψ and depth of the multi-fault branch from the Liquiñe–Ofqui quick estimate on the 2026-11-16 fits; branch weights.
- **S3 addendum (16 Nov): Liquiñe–Ofqui multi-fault quick estimate** (`multifault.lofs()`, REPORT_S3 section 8b; `tables/mf_A_lofs_2026-11-16.csv`, `figs/mf_A_lofs_2026-11-16.png`).
  - Setup: database A, the 48 faults of system Liquiñe–Ofqui (34 main traces link), depth 10 km, ψ 0.6 / 0.8 / 1.0, jumps 5 / 10 / 15 km, 10 seeds. The other arc faults keep their single-fault rates.
  - Chain Mmax: Leonard, capped at the class Mmax (the cap does not bind).
  - Arc Mw ≥ 6, expected against 8.98 observed (segmented A at 10 km: 19.1 / 25.4 / 31.8):
    - 5 km: 15.0 / 20.0 / 25.2
    - 10 km: 12.6 / 16.8 / 21.0
    - 15 km: 9.5 / 12.7 / 15.7
  - Passes (p ≥ 0.05): 10 km with ψ 0.6, and 15 km with every ψ.
  - Chain Mmax is 7.4, and 7.6 at 15 km. Aysén 7.7 is not reached at 10 km depth.
  - NMS: 2–5 % on average; one fault reaches 33–78 %.
  - Tests: +2, moment balance of the partition and the chain Mmax cap.
  - Open for Pablo: the jump distance of the multi-fault branch (10 or 15 km); whether ψ is a branch inside it; B and B-mm runs before the full set.
- **Decided by Pablo (16 Nov): jump distance 15 km for the multi-fault branch.** Proposed DECISIONS line (Crustal and faults): "Multi-fault branch: Liquiñe–Ofqui main traces (slip rate ≥ 1 mm/yr) link when their traces come within 15 km. The other UCERF3 filters are kept: junction and total azimuth ≤ 60°, cumulative azimuth ≤ 560°, cumulative rake ≤ 180°. UCERF3 uses 5 km; 15 km is taken because the LOFS traces are poorly mapped, with gaps of 5–13 km (Pablo, 16 Nov; quick estimate REPORT_S3 8b: arc count test passes for ψ 0.6–1.0)."
- **S3 addendum (16 Nov): LOFS multi-fault on B and B-mm, jump 15 km** (REPORT_S3 8c).
  - Arc Mw ≥ 6, expected against 8.98 observed, for ψ 0.6 / 0.8 / 1.0:
    - B: 30.5 / 40.7 / 50.8 (single faults 52.6 / 70.1 / 87.7)
    - B-mm: 22.0 / 29.5 / 36.9 (single faults 36.8 / 49.1 / 61.4)
  - Both fail (p ≤ 0.002), even after linking cuts the excess by 40 %.
  - Chains span 983 km, and the class cap 7.9 binds. NMS: B 5 %, B-mm 17 %.
  - `multifault.lofs(db, jumps)` now takes the database; main-trace slip rate per database: `MAIN_SR` (A 1, B 3 mm/yr).
  - Open for Pablo: B fails in both fault-system branches. Keep it as a tornado row only, or with a low weight?
- **Decided by Pablo (16 Nov): B and B-mm only in the tornado.** Proposed DECISIONS line (Crustal and faults): "Crustal fault databases: A (GEM, D16) is the fault model of the logic tree. B and B-mm enter the tornado only, as sensitivity rows. They fail the arc count test in both fault-system branches: B 30–51 and B-mm 22–37 expected arc Mw ≥ 6 against 9 observed, with multi-fault ruptures at 15 km (Pablo, 16 Nov; REPORT_S3 8c)."

## 2026-11-16: Mmax from weight-1 events, forearc refit, run 2026-11-16b (Claude Code, B11/B12)

Asked by Pablo after looking at the forearc fit. DECISIONS read again before and after (Statistics line "One rule for Mmax and corner" unchanged meanwhile).

- **Rule** (Pablo, 16 Nov): the largest observed event of a unit, for Mmax and the corner, is taken among the events with class weight 1, not weight ≥ 0.5. `fits/run.py`: setting `MMAX_W = 1.0`, used in `observed()`; `run_declustered.py` takes its Mmax from the same function. Nothing else changed.
- **Why:** the forearc Mmax was set by 1960-12-02 09:10 Mw 7.2 (24.67° S, 70.08° W, near Paposo; forearc weight 0.78). Its class rests on the Centennial depth of 14 km alone (σ 20 km); ISC-GEM gives 35 ± 6 km (quality A), which is inside the interface band over a slab top at 49 km. No mechanism: Pacheco and Sykes (1992, Table 4) list type "u", no depth, Ms 7.1. Not named in Ruiz and Madariaga (2018), Comte et al. (1999) or Lomnitz (2004); no A6 hint. The 1987-03-05 Antofagasta thrust event (42 km) is 30 km away.
- **Only the forearc changes its largest event:** 7.2 → 7.0, 2010-03-11 14:55 Pichilemu (GCMT mechanism, crustal hint, weight 1). Every other unit already had a weight-1 event at its maximum (arc Aysén 1960 7.7; backarc 1894 and Caucete 1977 7.5; Patagonia 1949 7.8; interface, in-slab, nest unchanged).

| forearc | Mmax | corner | b (sd) | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 fitted / observed |
|---|---|---|---|---|---|---|---|
| tapered, 16 → 16b | 7.4 → 7.2 | 7.19 → 6.99 | 0.984 (0.055) → 0.961 (0.057) | 3.53 → 3.55 | 0.361 → 0.378 (+4.6 %) | 0.0246 → 0.0176 (−28 %) | 2.9 / 3.4 → 1.9 / 3.4 |
| cut at Mmax | 7.4 → 7.2 | – | 0.986 (0.057) → 0.968 (0.060) | 3.53 → 3.54 | 0.353 → 0.362 (+2.5 %) | 0.0256 → 0.0201 (−21 %) | 3.1 / 3.4 → 2.4 / 3.4 |

- The large-event check still passes for both shapes (3.4 observed is inside the Poisson band of 1.9 and of 2.4). The 3.4 are fractions of 17 events of Mw 7.0–7.2, one of them with weight 1; they stay in the fit, all at or below the new Mmax.
- **Patagonia** takes the forearc b, so it moves too: b 0.984 → 0.961, N(≥ 5) unchanged (0.430), N(≥ 6) +5.6 %, N(≥ 7) +11 %; Mmax 8.0 and corner 7.79 → 7.78.
- **All other units:** identical to the 2026-11-16 tables in every column (same seed). Completeness table unchanged.
- **Declustered fits** (`fits_declustered_2026-11-16b.csv`; the declustered catalogues of 2026-11-16 are used as they are): forearc Mmax 7.4 → 7.2, corner 7.15–7.19 → 6.94–6.98; b 0.856 → 0.825 (Gardner–Knopoff per family) and 0.962 → 0.937 (nearest neighbour per family); N(≥ 6) +6.3 % and +4.7 %; N(≥ 7) −31 % and −29 %; checks pass. Patagonia through the forearc b; other units identical.
- **Forearc b against the floor** falls more steeply with Mmax 7.2: 0.94 at 5.2, 0.87 at 5.4, 0.78–0.80 at 5.6–5.8, 0.73 at 6.0.
- **Files.** New: the nine `*_2026-11-16b.csv` tables in `fits/tables/`. Nothing of 2026-11-16 overwritten; its figures copied to `fits/figs/2026-11-16/` first. 31 tests pass. `fits/FITS.md` section 9, `fits/DECLUSTER.md` section 7, DATA row.
- **Downstream.** For the interface, in-slab, arc and backarc units `fits_2026-11-16.csv` and `fits_2026-11-16b.csv` are identical, so S1 (`model/interface/if_build.py`) and S2 (`model/inslab/build.py`), which read the 2026-11-16 files, need no rerun. S3 (`model/crustal/background.py` and `faults.py`, `DATE = "2026-11-16"`) needs `fits_2026-11-16b.csv`: forearc Mmax 7.2 and corner 6.99, and the Patagonia b. `model/faults/fagnano.py` names `fits_2026-11-15.csv`, the first B11 table: to check in its own session what it reads from it.
- **Proposed lines for DECISIONS** (Pablo adds):
  - Statistics, in the Mmax line: "The largest observed event of a unit is taken among the events with class weight 1 (Pablo, 16 Nov); it changes only the forearc: 7.0 (Pichilemu 2010-03-11) instead of 7.2 (1960-12-02, weight 0.78, class from one depth), Mmax 7.2, corner 6.99."
  - Statistics: "Fits: `fits/tables/fits_2026-11-16b.csv` and `fits_declustered_2026-11-16b.csv` replace the 2026-11-16 files for the forearc and Patagonia; the other units are identical in both."
  - Crustal: "Background Mmax: forearc 7.2, arc 7.9, backarc 7.7, Patagonia 8.0."
  - Superseded: "Largest observed event among events of weight ≥ 0.5 (B11) → among weight-1 events (16 Nov)."
- **Proposed line for LEARNINGS** (Pitfalls, Fits): "An Mmax set by a split event is set by its weakest property: the forearc 7.4 came from one event whose class rested on a single depth with σ 20 km, against another catalogue's depth on the interface. Take Mmax from events of certain class."
- **Open:** a class hint for 1960-12-02 (A6) would need a reference; none found. The two Valdivia aftershocks of 1960-06-20 (Mw 7.0 and 7.1, 25 km ± 20, split 0.31 and 0.50 crustal) are in the same position.
- **Commands** (from `psha_chile8/fits/`): `python run.py` (95 s), `OMP_NUM_THREADS=1 python run_declustered.py` (3 min).
- **Suggested commit:** add `psha_chile8/fits/run.py psha_chile8/fits/run_declustered.py psha_chile8/fits/FITS.md psha_chile8/fits/DECLUSTER.md psha_chile8/fits/figs psha_chile8/fits/tables/*_2026-11-16b.csv psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `Fits 2026-11-16b: Mmax from weight-1 events (forearc 7.4 to 7.2)`.

## 2026-11-16: results deck part 1 and P1, Cabello and Candia through our steps (Claude, chat session)

Asked by Pablo in the project chat (outline agreed 15 Nov, then "go ahead creating the presentation"); built in the chat session through the file bridge, not by a Claude Code brief. DECISIONS read at the start; re-read after the fits of 2026-11-16b appeared (Mmax from weight-1 events): the figures were redrawn on them; P1 follows the same rule and did not change.

- **P1** (`explore/P1/`, new folder; `p1.py`, `REPORT.md`, `tests/test_p1.py` (3 pass), `tables/`). Cabello et al. (2025) and Candia and Macedo (2026) as given (Candia: all records that are not their own duplicates) matched to the frozen catalogue of 16 Nov (30 s / 100 km from 1964, 60 s / 300 km 1900–1963, 1.5 d / 300 km before), our class weights for matched events and second listings, `classify.py` on their hypocentres for the rest; fits with `run.fit`, tapered, our completeness table, our Mmax and the Kagan corner; magnitude-error weight on ours only. Nothing in `catalog/` or `fits/` written.
  - Cabello lists 2 568 of its 10 553 events of Mw ≥ 5.0 twice (the same earthquake from two agencies, median 2 s apart); Candia 357 of 8 839.
  - Same events: their Mw 0.1–0.3 above ours below 5.5, the same above.
  - Families, ours / Cabello / Candia: b 0.96 / 1.10 / 1.13 (interface), 1.16 / 1.40 / 1.38 (in-slab), 1.00 / 1.22 / 1.23 (crustal); N(≥ 5) 1.7–2.6 times ours. Large events: Candia fails the interface (39.7 / 60.5); intermediate in-slab fails in all three; 32–26° S fails only for us.
- **Deck** `presentations/261116_psha8_results/`: `pres.tex` and `pres.pdf` (title, 10 slides, 3 backup; style of the 4 Nov deck), `OUTLINE.md`, `NOTES.md` (choices made), `figs/figs.py` (pituPLOTS slides theme and `palette.py`, writes `figures/`). Figures new or redrawn from the frozen catalogue of 16 Nov, `fits_2026-11-16b.csv`, `fits_declustered_2026-11-16b.csv` and the P1 tables. Three rows added to FIGURES.md; PLAN I25 added.
- **Decisions made:** none in DECISIONS. Choices in `presentations/261116_psha8_results/NOTES.md`.
- **Open questions** (on the slides): keep the shared no-depth events in the rates or give the weight-1 rates a branch (slide 8).
- **Commands:** from `psha_chile8/explore/P1/`: `python p1.py` (20 s); from `presentations/261116_psha8_results/figs/`: `python figs.py` (1 min); `latexmk -pdf pres.tex`.
- **Suggested commit:** `git add psha_chile8/explore/P1 presentations/261116_psha8_results psha_chile8/PLAN.md psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`; message `Results deck part 1 and P1: Cabello and Candia through our classes, table and fits`.

## 2026-11-16, S2 lines in DECISIONS
- Written with Pablo's go-ahead (16 Nov). In-slab: the 15 Nov kernel-n line is replaced by the 16 Nov rule (log-likelihood scored at n 1–100, n the first local maximum from 5; result 5, shallow nearest neighbour 10), plus one new line on the completeness weights of the pattern events. Superseded: the in-slab sources line for the A9 rerun (with the kernel and weight changes).
- The shared kernel line (In-slab, "No zonation …", in-slab and crustal alike, candidates 5–100) is left as it is: the crustal rule belongs to S3. If S3 should follow the in-slab rule (score 1–100, first maximum from 5, completeness weights), that line needs changing for both.
- Calama engine check dropped for now (Pablo, 16 Nov).
- **Suggested commit:** `git add psha_chile8/DECISIONS.md psha_chile8/WORKLOG.md`; message `S2: in-slab kernel rule (first local maximum from n 5, scored 1-100), completeness weights of the pattern events, superseded line for the A9 rerun`.

## 2026-11-16: crustal classes fitted from 1976, run 2026-11-16c (Claude Code, B11/B12)

Asked by Pablo after the diagnostic of the forearc and arc fits ("From 1976. But keep the Mmax for crustal classes"). DECISIONS read again before and after: the table line of Statistics still says one table for every class, so this needs a new line (proposed below, not written).

- **Rule** (Pablo, 16 Nov): the crustal classes (forearc, arc, backarc, Patagonia) are fitted on the completeness table from 1976 on only, that is "Mw 5.0 from 1976"; the step "5.2 from 1964" and the historical steps (7.0 from 1905, 7.5 from 1830, 8.0 from 1500) are not used for them. Mmax is kept: the largest weight-1 event of any year + 0.2 (forearc 7.2, arc 7.9, backarc 7.7, Patagonia 8.0), and the corner from it. Interface and in-slab units keep the full table. `fits/run.py`: `since=1976` in the crustal units and `table_of()`, used by the fits, the comparison, the declustered fits and the figures; the fits table has a new column `steps`.
- **Why** (diagnostic of 16 Nov): in 1964–1975 both classes are short at Mw 5.5–5.9 (forearc 0.12 per year against 0.64–0.78 afterwards; arc 0.04 against 0.16–0.67); the class Mc cannot be measured before 2000 (under 100 events per window; 4.6–4.8 pooled over 1976–2026, below the floor). The historical steps counted the arc's Mw 7.5–7.9 bins over 197 years on one event (Aysén 1960) in a region with no early record, and the forearc's Mw 7.0–7.2 bins on 16 fractions of events without depth (2.5 in all).

| unit (tapered) | Mmax | corner | events (counted) | b (sd), 16b → 16c | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 fitted / observed from 1976 |
|---|---|---|---|---|---|---|---|---|
| forearc | 7.2 | 6.99 → 6.98 | 782 → 710 (195) | 0.961 → 0.929 (0.061) | 3.55 → 3.84 (3.49–4.21) | +16 % | 0.0176 → 0.0213 (+21 %) | 1.0 / 1.0 |
| arc | 7.9 | 7.70 → 7.71 | 100 → 85 (70) | 1.023 → 1.047 (0.104) | 1.30 → 1.38 (1.12–1.63) | 0 % | 0.0108 → 0.0103 (−5 %) | 0.5 / 0 |
| backarc | 7.7 | 7.49 → 7.48 | 195 → 171 (121) | 0.979 → 0.934 (0.082) | 2.31 → 2.38 (2.06–2.71) | +14 % | 0.0218 → 0.0274 (+26 %) | 1.4 / 1.0 |
| Patagonia | 8.0 | 7.78 | 28 → 22 (21) | forearc b | 0.430 → 0.417 (0.28–0.57) | +4 % | 0.0049 → 0.0054 (+12 %) | 0.3 / 0 |

- The cut-line fits move the same way (forearc b 0.968 → 0.926, N(≥ 7) +28 %). Interface, in-slab and nest rows are identical to 16b.
- **Cross-check against the events left out.** The large events before 1976 no longer enter the fit, so they test it: over 1905–2026 the arc line expects 1.25 events of Mw ≥ 7 and the catalogue has 2 (1927, Aysén 1960; 1.7 by weight); the forearc line expects 2.6 and the catalogue has 3.4 by weight. Both inside the Poisson band.
- **Still weak, and visible in the table:**
  - forearc: weight-1 events alone give b 0.846 and N(≥ 5) 1.53 (40 % of the fit); b against the floor 0.92 (5.2), 0.88 (5.4), 0.81 (5.6), 0.82 (6.0);
  - arc: nothing above Mw 6.5 since 1976, so the line is extrapolated from 6.5 to its Mmax of 7.9; b against the floor rises (1.20 at 5.2, 1.15 at 5.4, 1.12 at 5.6, 1.83 at 6.0 on a handful of events); a pooled crustal b is 0.954;
  - the sequences of 2000–2010 are a quarter of the window and set the rate (Mw 5.0–5.4: forearc 5.4 per year then against 1.1–2.4, arc 1.8 against 0.7–0.8).
- **Declustered fits** (`fits_declustered_2026-11-16c.csv`; the crustal classes take the steps from 1976 of whichever table is used, so their "full" and "declustered" table rows now differ only through the declustered Mc): forearc b 0.825 → 0.795 (Gardner–Knopoff per family) and 0.937 → 0.912 (nearest neighbour per family), N(≥ 6) +13 %; arc b 0.936 → 1.000 and 0.974 → 1.014, N(≥ 7) −23 % and −13 %; backarc b 1.004 → 1.020 and 1.050 → 1.060, N(≥ 7) −12 % and −8 %. Checks pass.
- **Files.** New: the nine `*_2026-11-16c.csv` tables in `fits/tables/`. Nothing of 16 or 16b overwritten; the 16b figures copied to `fits/figs/2026-11-16b/` first. 31 tests pass. `fits/FITS.md` section 10, `fits/DECLUSTER.md` section 8, DATA row.
- **Downstream.** S3 needs `fits_2026-11-16c.csv` for all four crustal classes (it reads `DATE = "2026-11-16"` in `model/crustal/background.py` and `faults.py`); B13 (faults and background at M6) moves with the forearc and backarc N(≥ 6) (+16 %, +14 %). S1 and S2 unchanged (their units are identical in 16, 16b and 16c).
- **Proposed lines for DECISIONS** (Pablo adds):
  - Statistics, after the table line: "Crustal classes (forearc, arc, backarc, Patagonia) use the table from 1976 on only, Mw 5.0 from 1976: 1964–1975 is short of crustal events at Mw 5.5–5.9 and the historical steps rest on one or two events in regions with no early record. Their Mmax still comes from the largest weight-1 event of any year (Pablo, 16 Nov)."
  - Statistics, Mmax line: "The largest observed event of a unit is taken among the events with class weight 1 (Pablo, 16 Nov)."
  - Statistics: "Fits: `fits/tables/fits_2026-11-16c.csv` and `fits_declustered_2026-11-16c.csv` (crustal classes from 1976, forearc Mmax 7.2); interface and in-slab rows are those of 2026-11-16."
  - Superseded: "One completeness table for every class (15 Nov) → the crustal classes from 1976 only (16 Nov)."
- **Proposed line for LEARNINGS** (Fits pitfalls): "For a small class the completeness table moves the result more than the estimator: forearc N(≥ 5) 3.5–5.0 and arc N(≥ 7) × 2 over five reasonable tables, against a bootstrap interval of ± 9 %. Show the table spread next to the bootstrap."
- **Open:** the 2000–2010 sequences set the crustal rates (full catalogue by decision); the arc tail from Mw 6.5 to 7.9 is extrapolated.
- **Commands** (from `psha_chile8/fits/`): `python run.py`, `OMP_NUM_THREADS=1 python run_declustered.py`.
- **Suggested commit:** add `psha_chile8/fits/run.py psha_chile8/fits/compare.py psha_chile8/fits/run_declustered.py psha_chile8/fits/figs.py psha_chile8/fits/FITS.md psha_chile8/fits/DECLUSTER.md psha_chile8/fits/figs psha_chile8/fits/tables/*_2026-11-16[bc].csv psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `Fits 2026-11-16c: crustal classes from 1976, Mmax from weight-1 events`.
- **S1 OpenQuake check (16 Nov):** `if_oqcheck.py` writes the jobs as `preclassical` (`MODE` at the top): every file and the tree are read and checked, no hazard. Margin calc 514 (216 realizations, 55 s), segments calc 515 (504, 103 s); all 240 files load, rates equal the tables (≤ 1.8e-8 in N(≥ 5.5), ≤ 2.1e-6 in N(≥ 8)), last magnitudes equal (`tables/oqcheck_2026-11-16.csv`). `oq engine --run` and `oq run` both wait forever in `poll_queue` behind stale jobs 504–509 (status submitted, no process; 504, 505, 507 are S2/S3, 506, 508, 509 my killed runs): ran with `OQ_CONFIG_FILE` pointing to a private cfg with `[distribution] serialize_jobs = 0`. Pablo: clear the stale rows (`oq abort <id>` or set them failed) before the next `oq engine` run.

- **OpenQuake queue cleared (16 Nov, at Pablo's word):** the 12 stale rows of `~/oqdata/db.sqlite3` (jobs 1, 503–513: submitted or created, is_running 1, no process alive) set to status failed, is_running 0, directly in the database (not `oq abort`, which would signal the stored pids). Backup of the database before the change in the session scratchpad. `oq engine --run` no longer waits.

## 2026-11-16: results deck part 1, additions after Pablo's review (Claude, chat session)

Pablo: the deck did not show the b stability against Cabello and Candia, the conversions, or the large-event check at several magnitudes; is the 32–26° S segment really failing?
- **Large events, answer:** of 41 counts (12 units at Mw ≥ 6.5, 7, 7.5, 8, fits 2026-11-16b) 37 are inside the Poisson 5–95 % band, about what chance gives. 32–26° S misses only at Mw ≥ 7 (9.9 observed against 17.4 fitted: a deficit of Mw 7.0–7.4) and is inside at 6.5 (29.0 / 29.4), 7.5 (7.4 / 9.4) and 8 (2.6 / 5.0). Intermediate in-slab misses at 7.0 and 7.5: 21.6 events of 1905–1975 against 8.5 fitted; 1976–2026 6.8 against 6.1. Patagonia at 7.5 (1.7 against 0.3). The earlier figures that passed everywhere are test 3 (since 1976, line on 5.0–6.5): per unit on P1, ours 10 of 10, Cabello 10 of 10, Candia 5 of 10.
- **P1 additions:** `test3()`, `conversions()`, `pairs()` in `p1.py`; tables `test3_`, `pairs_`, `*_conversions_2026-11-16.csv`; REPORT sections. The fits and counts did not change.
- **Deck:** new slides for the conversion (our relations against Cabello Table 3 and Candia Table 6, pairs with Mw ≥ 6 darker), the b stability (tests 1 and 2), our fits at Mw 6.5–8, and test 3 on three catalogues; their Mw minus ours to the backup. 13 slides plus title, 4 backup. `figures/fig_large.png` is obsolete (delete it). FIGURES rows updated.
- **Suggested commit:** as in the entry above; message `Results deck part 1: conversions, b stability, large-event checks at several magnitudes`.

## 2026-11-16: B14, 10 % rule and Patagonia on its own (Claude Code)
- **Done (Pablo's decisions, already in DECISIONS):** `npd.py`: `MIN_SHARE = 0.10` (was 0.05; `PREV_MIN_SHARE = 0.05` kept to pair the 15 Nov rows), `BORROW` removed, so Patagonia is built from its own mechanisms. Plane choice unchanged (the plane closer to the type's mean double couple). Rewritten: `npd_2026-11-16.csv`, `tables/moved_2026-11-16.csv`, `figs/ternary.png` (unchanged in content), `REPORT_B14.md`; new `tables/dropped_2026-11-16.csv` (unrounded shares of the dropped types). Counts and shares unchanged. Tests: 3 pass. DATA row 2026-11-16c.
- **Dropped types (share before renormalising):** in-slab intermediate reverse 0.0994; Jujuy nest reverse 0.0283 and strike-slip 0.0094; forearc strike-slip 0.0829; backarc normal 0.0407; Patagonia normal 0.0556. New against 5 %: intermediate reverse, forearc strike-slip, Patagonia normal.
- **Table type weights (N / R / SS):** in-slab shallow 0.38 / 0.51 / 0.11; intermediate 0.84 / 0 / 0.16; Jujuy nest normal only; forearc 0.32 / 0.68 / 0; arc 0.10 / 0.23 / 0.67; backarc 0 / 0.68 / 0.32; Patagonia 0 / 0.24 / 0.76 (strike-slip 115/75/0).
- **Open:** three types sit near the line: intermediate reverse 0.0994 (dropped by half a weighted event of 803), shallow strike-slip 0.107 and arc normal 0.101 (kept). DECISIONS re-read at the end: lines 125 and 152 match this run.
- **Suggested commit:** `git add psha_chile8/model/mechanisms psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `B14: types below 10 % dropped, Patagonia on its own distribution (npd_2026-11-16.csv)`

## 2026-11-16: results deck part 1, motivation slide (Claude, chat session)

- Motivation slide 2 added with the October fits on Cabello et al. (2025) (`if_fmd`, `is_fmd` of the 4 Nov deck, copied unchanged as `figures/old_*.png`).

## 2026-11-16: one b for the crustal family, run 2026-11-16d (Claude Code, B11/B12)

Asked by Pablo after the 16c run left the arc with b 1.05 ± 0.10 ("Yes, shared b"). DECISIONS read again before and after: Statistics still says "Patagonia crustal: b of the forearc ... Backarc ... own fit ... no pooling" and Crustal "Backarc own b; Patagonia borrows the forearc b"; both are replaced by this (proposed below, not written).

- **Rule** (Pablo, 16 Nov): the four crustal classes share one b, that of the crustal family fitted as one unit (all crustal weight together, table from 1976, Mmax 8.0 from its largest weight-1 event); each class keeps its own rate, Mmax and corner. In the bootstrap each class takes the family b of the same replicate. `fits/run.py`: new unit `crustal` (also a row of the tables, "crustal, all classes"), and `b_from="crustal"` for forearc, arc, backarc and Patagonia.
- **Family:** b 0.975 (sd 0.042) tapered, 0.972 (0.043) cut; 988 events, 406 counted; N(≥ 5) 7.98 per year. Kijko–Smit 0.978, Aki–Utsu 0.974, b-positive 1.10; b against the floor 1.00 (5.2), 1.01 (5.4), 0.97 (5.6), 1.06 (5.8), 1.22 (6.0). Mw ≥ 7 since 1976: 4.3 fitted, 2.0 observed (inside the band).

| unit (tapered) | Mmax | corner | b, 16c → 16d | N(≥ 5) (5–95 %) | N(≥ 6), 16c → 16d | N(≥ 7) (5–95 %), against 16c | Mw ≥ 7 expected over 1905–2026 / observed by weight |
|---|---|---|---|---|---|---|---|
| forearc | 7.2 | 6.99 | 0.929 → 0.975 | 3.82 (3.47–4.19) | 0.440 → 0.393 (−10 %) | 0.0179 (0.0127–0.0241), −16 % | 2.6 / 3.5 |
| arc | 7.9 | 7.69 | 1.047 → 0.975 | 1.39 (1.13–1.64) | 0.123 → 0.147 (+19 %) | 0.0144 (0.0096–0.0201), +40 % | 1.7 / 1.7 |
| backarc | 7.7 | 7.49 | 0.934 → 0.975 | 2.36 (2.04–2.69) | 0.276 → 0.249 (−10 %) | 0.0227 (0.0158–0.0310), −17 % | 2.7 / 1.9 |
| Patagonia | 8.0 | 7.79 | 0.929 → 0.975 | 0.416 (0.28–0.57) | 0.049 → 0.044 (−10 %) | 0.0044 (0.0026–0.0067), −19 % | 0.5 / 1.6 |

- N(≥ 5) of every class within 1 % of 16c. The sd of b falls from 0.06–0.10 (own b) to 0.042 for all four. The last column is the cross-check on the large events left out of the fit (cut-line values); all four inside the Poisson band. With its own b Patagonia failed it (0.2 expected).
- Own b for reference (rows "line cut at Mmax, own b" of the sensitivity table): forearc 0.926, arc 1.043, backarc 0.930, Patagonia 1.166 (22 events).
- **Arc:** the observed points of 1976–2026 lie under the shared-b line at Mw 6.0–6.5 (about 6.4 events of Mw ≥ 6 observed, 7.5 fitted); nothing above 6.5 since 1976, so the tail to Mmax 7.9 is still extrapolated, now with the family slope.
- Interface, in-slab and nest rows are identical to 16, 16b and 16c.
- **Declustered fits** (`fits_declustered_2026-11-16d.csv`): family b 0.923 (0.054) with Gardner–Knopoff per family and 0.999 (0.051) with nearest neighbour per family, taken by the four classes; arc N(≥ 6) 0.106 and 0.109, forearc 0.257 and 0.252. Checks pass.
- **Tested and not adopted:** a completeness table read on crustal events only (Mc 5.3 in 1976–1989; table "5.0 from 1990, 5.3 from 1964" plus early historical steps; family b 1.06, arc 1.11). Rolling back to 16b was the other option on the table.
- **Files.** New: the nine `*_2026-11-16d.csv` tables. Nothing of 16, 16b or 16c overwritten; the 16c figures copied to `fits/figs/2026-11-16c/`. 31 tests pass. `fits/FITS.md` section 11, `fits/DECLUSTER.md` section 9, DATA row.
- **Downstream.** S3 and B13 need `fits_2026-11-16d.csv` for the four crustal classes (b 0.975, forearc Mmax 7.2, rates from 1976). The table has a new row `crustal`: a reader that loops over every unit will meet it. S1 and S2 unchanged.
- **Proposed lines for DECISIONS** (Pablo adds; they replace lines 92 and 131 for the crustal classes):
  - Statistics: "The four crustal classes share one b, fitted on the crustal family as one unit (0.975 ± 0.042 on the catalogue of 16 Nov); each class its own rate, Mmax and corner. Jujuy nest: own fit, as before (Pablo, 16 Nov)."
  - Statistics: "Crustal classes use the table from 1976 on only (Mw 5.0 from 1976); their Mmax comes from the largest weight-1 event of any year (Pablo, 16 Nov)."
  - Statistics: "The largest observed event of a unit is taken among the events with class weight 1 (Pablo, 16 Nov)."
  - Statistics: "Fits: `fits/tables/fits_2026-11-16d.csv` and `fits_declustered_2026-11-16d.csv`; interface and in-slab rows are those of 2026-11-16."
  - Crustal: "Background Mmax: forearc 7.2, arc 7.9, backarc 7.7, Patagonia 8.0; one b for the four classes (Statistics)."
  - Superseded: "Backarc own b, Patagonia with the forearc b (Oct, 15 Nov) → one b for the crustal family (16 Nov). One completeness table for every class (15 Nov) → crustal classes from 1976 (16 Nov). Largest event among weight ≥ 0.5 (B11) → among weight-1 events (16 Nov)."
- **Proposed lines for LEARNINGS:**
  - b-value and rates: "A crustal class of 70–200 counted events cannot hold its own b: arc 1.04 ± 0.10, backarc 0.93 ± 0.09, forearc 0.93 ± 0.06 against a family b of 0.97 ± 0.04 that hardly moves with the table (0.97–1.01). With the family b every class reproduces its events of Mw ≥ 7 since 1905, which are not in the fit."
  - Completeness: "A completeness table read on crustal events alone gives Mc 5.3 for 1976–1989 and raises b (arc 1.11); not adopted."
- **Open:** the arc tail from Mw 6.5 to 7.9 is extrapolated; the 2000–2010 sequences set the crustal rates.
- **Commands** (from `psha_chile8/fits/`): `python run.py`, `OMP_NUM_THREADS=1 python run_declustered.py`.
- **Suggested commit:** add `psha_chile8/fits/run.py psha_chile8/fits/compare.py psha_chile8/fits/run_declustered.py psha_chile8/fits/figs.py psha_chile8/fits/FITS.md psha_chile8/fits/DECLUSTER.md psha_chile8/fits/figs psha_chile8/fits/tables/*_2026-11-16[bcd].csv psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `Fits 2026-11-16d: crustal classes from 1976 with one family b, Mmax from weight-1 events`.


## 2026-11-16, S2: pytest clash fixed
- `model/inslab/smooth.py` → `model/inslab/is_smooth.py` (imports in `build.py` and `tests/test_s2.py`, REPORT_S2 line 4). From `psha_chile8/` pytest collected `model/crustal/smooth.py` first under the same module name, and 3 in-slab tests failed. Now `pytest` from `psha_chile8/` gives 311 passed, 2 skipped. `model/crustal` untouched. Not renamed: `build.py` and `oqcheck.py`, which share names with crustal modules but are imported by no other test.
- **Suggested commit:** `git add -A psha_chile8/model/inslab/smooth.py psha_chile8/model/inslab/is_smooth.py psha_chile8/model/inslab/build.py psha_chile8/model/inslab/tests/test_s2.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/WORKLOG.md`; message `S2: in-slab kernel module renamed is_smooth.py (pytest clash with model/crustal/smooth.py)`.


## 2026-11-16, deck 261116 (part 1): depth slide and text after review
- Depth slide: the period bars and the weight-1 ratios are gone. New `fig_depth`: share of the events of Mw ≥ 4.5 per period whose depth comes from the catalogue that locates the event, from another catalogue (2 611), from the literature class (31), or none (1 853); next to it, a schematic of how a depth with its error is split between classes. Counts in `presentations/261116_psha8_results/figs/depth_sources.csv`.
- Slide titles and bullets rewritten in plain language; the summary slide is now "Main findings" (problems and open points).
- The deck still uses `fits_2026-11-16b`; the later 16d fits (crustal classes) are not in it yet.
- **Suggested commit:** `git add presentations/261116_psha8_results psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`; message `Deck 261116: depth sources and class-split schematic, plain slide text`.

## 2026-11-16: DECISIONS written for the crustal fits of 16 Nov (Claude Code, B11/B12)

- **DECISIONS.md edited by Claude Code at Pablo's word ("include decisions")**, against the usual rule of proposing only; re-read just before, only the lines of the fits touched. Statistics: new line for the crustal table from 1976; the Mmax rule now says weight-1 events; the fits line points to `fits_2026-11-16d.csv` (the first A9 table kept as its own line); the declustered line names `fits_declustered_2026-11-16d.csv`; "Patagonia with the forearc b, backarc own fit" replaced by the shared crustal b (Jujuy nest unchanged). Crustal and faults: the b line and the background Mmax (forearc 7.2). Superseded: one line. These are the lines proposed in the three entries above.
- LEARNINGS.md not edited; the proposed lines stay in the entries above.
- For S3: read `fits_2026-11-16d.csv`; the message for that session is in the conversation with Pablo.
- Add to the commit: `psha_chile8/DECISIONS.md`.
- **LEARNINGS.md edited at Pablo's word ("update in learning", 16 Nov):** the lines proposed in today's fit entries, re-read just before and only added to. Completeness: the table unchanged by the A9 revision; the crustal classes against the catalogue-wide table; the crustal-only table tested and not adopted. b-value and rates: the crustal family b; what still sets the crustal rates. Pitfalls, Fits: Mmax from a split event; the table against the bootstrap for small classes; old large events as an independent check. Add `psha_chile8/LEARNINGS.md` to the commit.
- **Pablo, 16 Nov: crustal declustered rates as a tornado row.** DECISIONS (Crustal and faults) line written at his word. The numbers already exist in `fits_declustered_2026-11-16d.csv`; S3 builds a second background from the rows method gk_family and nn_family, table full, b_option own.

## 2026-11-16 — S3 rerun on fits 2026-11-16d, S2 kernel rule, declustered tornado row (crustal)
- **Done:**
  - Crustal code on `fits_2026-11-16d.csv`, `DATE = "2026-11-16d"`.
  - Completeness table 5.0 from 1976 (`background.TABLE`). Forearc Mmax 7.2 (`background.CLASSES`, `faults.CLASS_MMAX`).
  - Reran background, faults, join, large, arc, and the LOFS multi-fault (A, 15 km).
  - New dated outputs; nothing overwritten; no NRML. Report: `REPORT_S3.md` section 9.
- **S2 kernel rule applied** (copied, not imported):
  - n scored at 1, 3, 5, 10, 15, 25, 50, 100; n is the first local maximum from 5 (`smooth.first_max`).
  - Pattern events are weighted w / (t_end − T_c(m)); training events w / (2010 − T_c(m)).
  - Family rule kept. Figure `figs/kernel_loglik_2026-11-16d.png`.
  - n before → after: forearc 5 → 5 / 5; backarc 5 → 10 (gk) / 25 (nn); arc and Patagonia 5 → 50 (family) in both options.
- **Problem with the family rule, for Pablo:**
  - The arc and Patagonia have fewer than 20 test events, so they take the crustal family n. The family curve mixes four separated classes and rises to n = 50.
  - The arc has 34 / 50 training events and Patagonia 9, so n = 50 means bandwidths of about 2000 and 950 km. Those patterns are near uniform.
  - Their own curves give n = 5 from the floor.
  - Effect on the no-faults background at the cities: Puerto Aysén −82 %, Valparaíso +49 %, La Serena +39 %.
  - Options:
    - (a) keep the rule as it is
    - (b) a class under 20 test events takes its own first maximum from 5
    - (c) it takes the family's bandwidth in km, not its n
  - The in-slab classes don't hit this (they all have 20+ test events or n = 5 in the family). The patterns of 16d are not for use until this is decided.
- **What moved (16 → 16d, tapered):**
  - Faults / fit at Mw 6, arc: A 3.7 → 3.0, B 10.1 → 8.3, B-mm 5.2 → 4.3 (fit +20 %; fault rates within 2 %).
  - Patagonia: unchanged (1.65 / 3.5 / 1.3).
  - Forearc background N(≥ 6): 0.301 → 0.333 (A); N(≥ 7): 0.0235 → 0.0169 (Mmax 7.2).
  - Backarc: +4 %.
  - Fault share of N(≥ 6), A: forearc 0.15, backarc 0.20, arc and Patagonia 1 (no background above 6).
- **Arc count test** (now on 1976–2026 only):
  - Observed 6.5 (was 9.0). Single faults: A 22.4 (13 % passes), B 61.8 (0 %), B-mm 31.9 (6 %).
  - LOFS multi-fault, A, 15 km: 7.1 / 9.5 / 11.8 for ψ 0.6 / 0.8 / 1.0, all pass (p 0.58 / 0.27 / 0.10).
  - Since 1976 no arc event of Mw ≥ 7, so the test no longer sees Aysén or 1927.
  - Proposed: run the Mw ≥ 7 count on the 1905–2026 window, as the fits' large-event check does.
- **Tornado row, declustered background** (`lower.py`, `tables/join_decl_2026-11-16d.csv`):
  - Faults / declustered fit at Mw 6 (gk; nn within 0.04): forearc 0.23 / 0.61 / 0.71, arc 4.2 / 11.4 / 5.9, backarc 0.31, Patagonia 1.8 / 3.8 / 1.4 (A / B / B-mm).
- **fagnano.py** (`model/faults/`) reads `fits_2026-11-15.csv` only for the Patagonia b of its D16 diagnostic rates table. Nothing in the crustal model uses it. Proposed for its owner: point it to `fits_2026-11-16d.csv` (b 0.972 cut).
- **PGA at the cities:** not run (no OpenQuake until the fits are settled).
- **DECISIONS re-read** (Statistics, Crustal, In-slab, Superseded of 16 Nov). The choices hold, except the open family-rule point above.
- **Proposed DECISIONS lines:**
  - In-slab, the shared kernel line "No zonation …" (in-slab and crustal): replace "candidates 5–100" by "scored at n 1–100, n the first local maximum from 5; pattern events weighted by their completeness period".
  - Crustal: "Crustal kernel n (S3, 16 Nov, fits 16d): forearc 5, backarc 10 (gk) / 25 (nn), arc and Patagonia [after Pablo's choice on the family rule]."
  - Tornado: "Crustal background from the declustered fits (gk_family / nn_family, table full, own b) is a tornado row, a lower bound on the rates (Pablo, 16 Nov)."
  - Superseded: "Crustal tables on fits 2026-11-16 → 2026-11-16d (S3, 16 Nov). Arc faults / fit at Mw 6: A 3.7 → 3.0; forearc Mmax 7.4 → 7.2; kernel n fixed at 5 → the S2 rule."
- **Tests:** crustal 14 passed, 2 skipped. Full suite 311 passed, 2 skipped.
- **Suggested commit:** `git add psha_chile8/model/crustal/{background,smooth,faults,join,large,arc,kernels,multifault,build,lower}.py psha_chile8/model/crustal/REPORT_S3.md psha_chile8/model/crustal/tables/*2026-11-16d* psha_chile8/model/crustal/figs/*2026-11-16d* psha_chile8/WORKLOG.md` — message: "S3: crustal rerun on fits 2026-11-16d with the S2 kernel rule; declustered background tornado row"


## 2026-11-16, deck 261116 (part 1): text pass and completeness map
- Short titles and plain bullets on every slide. New slide "Completeness in space": the Mc map of B9 (`b9_10_mc_all.py`) rerun on the frozen 2026-11-16 catalogue, same shares as B9 (above 5.0: 11 %, 1.5 %, 0 of the cells). The completeness slide now says why one table: mixed windows give interface b 1.06 and miss the Mw ≥ 7 events (B9, 14 Nov catalogue).
- **Suggested commit:** `git add presentations/261116_psha8_results psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`; message `Deck 261116: short titles, plain text, completeness map`.
- **S3, kernel n per class (Pablo, 16 Nov):** each class its own first maximum from 5, no family borrowing (only b pools); Patagonia fixed at 5. n: forearc 5 / 5, arc 5 / 5, backarc 10 / 25, Patagonia 5 (gk / nn). Patterns `pattern_{gk,nn}_2026-11-16d.csv` rebuilt; cities rerun (REPORT_S3 9b). This replaces the family-rule open point above. Proposed DECISIONS line (Crustal): "Crustal kernel n per class (S3, Pablo, 16 Nov): each class its own n, the first local maximum from 5 of its own S-test curve; no family n (the crustal family mixes separate classes and prefers broad kernels); Patagonia fixed at n = 5 (9–12 test events). Result on fits 16d: forearc 5, arc 5, backarc 10 (gk) / 25 (nn), Patagonia 5."
- **S3 figures in the pituplots style (Pablo, 16 Nov):** `model/crustal/figs_s3.py` writes `figs/2026-11-16d/`.
  - `pattern_{gk,nn}.png`: mesh cells (plot_grid, magma alpha ramp), relief basemap, one colour scale (log₁₀ N(≥ 5) −6 to −2) for every class and the sum.
  - `mfd_classes.png`: catalogue steps and the 1976–2026 dots, tapered and cut, (a, b) 5–95 % from the fit covariance.
  - `kernel_loglik.png`.
  - The old maps and kernel figure were removed from `background.py`. FIGURES.md rows added.
  - Patagonia under nearest neighbour scores −∞ at every n: one test event lies more than 500 km from all 9 training events. Patagonia's n is fixed at 5.
  - **Seen on the maps, for Pablo:** each class pattern is normalised over the whole crustal grid, not over its own area. So the arc rate runs into the forearc and backarc, Patagonia reaches 41° S, and the backarc 43° S, at low rates. The in-slab model restricts each class to its domain (`dom_*`); the crustal model does not. Option: a domain per class, from the class polygons (proposal, not done).
  - Commands: `python figs_s3.py` (30 s) from `model/crustal/`.


## 2026-11-16, deck 261116 (part 1): completeness map dropped
- The map slide is gone. The Mc rule of B9 (b-stability, KS) reads too low in cells with few events: subsamples of the central cell (5 059 events, Mc 4.3) give 3.5 at 150, 3.7 at 300, 4.0 at 500; of the north cell (5 937, Mc 4.8) 3.5 up to 500 and 3.9 at 1 000. The B9 maps share the fault. A b-positive rule has no size bias but scatters ±0.3 in small cells and reads 3.9 in the north. Added to LEARNINGS (Pitfalls); FIGURES row marked dropped. The completeness table is not affected (read from rates and the large-event checks).
- **Suggested commit:** `git add presentations/261116_psha8_results psha_chile8/FIGURES.md psha_chile8/WORKLOG.md psha_chile8/LEARNINGS.md`; message `Deck 261116: completeness map dropped (Mc biased low in small samples), LEARNINGS note`.
- **S3 grid check (16 Nov):** `figs_s3.grid_events()` → `model/crustal/figs/2026-11-16d/grid_events.png`, the crustal grid against the complete events (Mw ≥ 5 since 1976) per class.
  - Weight outside the grid: forearc 9 % (north of 17.5° S), arc 0 %, backarc 84 %, Patagonia 50 %.
  - Backarc: events east of the grid edge, 65–69° W, 17–38.6° S (Sierras Pampeanas, Cuyo).
  - Patagonia: all 11 off-grid events at 57–58° S, 65–67° W (Scotia plate boundary, south of Tierra del Fuego).
  - For Pablo, before a new dated grid.

## 2026-11-16: Scotia events in crustal Patagonia, phase 1 (Claude Code, A7; task from S3)

Read again: CLAUDE.md, DECISIONS (Catalog, Classification, Superseded), `tasks/A9_catalog_revision.md`. Nothing changed in `classify.py` or the frozen folders. Script `explore/A9/a9_scotia.py`, list `explore/A9/scotia_events.csv`.

- **What the events are.** The cluster at 56.6–57.9° S, 65.3–69.4° W lies on the Scotia–Antarctic boundary of PB2002 (SC/AN, Bird 2003; the trace is on disk in `data/pb2002_antarctic_trench_2026-11-15.geojson`), not on the South America–Scotia boundary: 3 to 47 km from SC/AN, 240 to 380 km from the Magallanes–Fagnano system.
- **Why they are crustal.** 101 events of Mw ≥ 4.5 of the same cluster are already Antarctic interface by position (within 150 km east of the trench), the Mw 7.5 of 2025-05-02 among them. The position rule leaves out an event with a mechanism that is not a thrust; those 13 then find no slab and fall to crustal Patagonia. All 13 are strike-slip. It is a gap in the Antarctic rule, not a missing class.
- **Rule proposed** (candidate 1 of the brief, with the boundary that fits): an event without a slab whose nearest boundary is SC/AN of PB2002, nearer than the AN\SA trench and nearer than the Magallanes–Fagnano system (the seven traces of the fault source), is a Scotia–Antarctic boundary event and is not crustal; class outer rise, left out of the source model, as the Chile Ridge events. No distance or box is set. Source: Bird (2003) for the boundary; DECISIONS already leaves the Scotia–Antarctic trench out of the interface model (Oct). The plate polygon (candidate 2) was not taken: the Magallanes–Fagnano fault is the plate boundary itself, so events just south of it (2006-01-09 at 54.26° S, 3 km from the trace) would leave Patagonia.
- **Events that change** (Mw ≥ 4.5, all years): 13, all crustal Patagonia with weight 1: 1984-05-04 Mw 5.4, 1987-06-21 5.4, 1991-03-06 5.1, 2010-01-17 6.2, 2012-04-14 6.2, 2015-03-14 5.0, 2015-10-20 5.5, 2016-07-11 (two, 4.8 and 4.9, at 69.3° W), 2019-09-05 5.1, 2025-05-21 5.1, 2025-07-04 5.6, 2025-08-19 5.2. Positions, depths and distances in the list.
- **Stay in Patagonia:** the 1949 doublet (21 and 27 km from the Magallanes–Fagnano traces, 261 and 281 km from SC/AN), 1879 (115 against 317 km), 1950-01-30 (56 against 260 km), and every event near the system. The nearest case to the limit is 2003-09-12 Mw 5.5 at 51.6° S 75.6° W: AN\SA at 64 km, SC/AN at 78 km; it stays.
- **Patagonia weight:** crustal table (Mw 5.0 from 1976): Mw ≥ 5, 22 → 11; Mw ≥ 6, 2 → 0; Mw ≥ 7, 0. All years: Mw ≥ 5, 33 → 22; Mw ≥ 6, 10 → 8; Mw ≥ 7, 3 → 3. Mmax unchanged: the largest event stays 7.8 (1949), Mmax 8.0.
- **For Pablo:** the 101 Antarctic-interface events south of 52.07° S are all on SC/AN, the boundary the interface model leaves out. They feed no rate (the Antarctic interface is geodetic only), so nothing is proposed for them.
- **Stopped for Pablo's decision.** Phase 2 as in the brief.

## 2026-11-16, S2: shallow and intermediate on one grid
- Pablo (16 Nov): the two in-slab classes are smoothed over one grid and added. `build.py` CLASSES: shallow and intermediate domains are all 13 847 in-slab cells (were slab top ≤ 50 / > 50 km); the nest keeps its region. Rebuilt the 2026-11-16 outputs in place (the two-domain version is in commit eb4f784).
- Why: the two domains left a trough along the 50 km slab-top line, 19–20 % low at slab top 40–60 km.
- Effect: summed shallow + intermediate rate moves 2.7 % (gk) / 3.0 % (nn); 15–18 % of the shallow rate now lies in cells with slab top > 50 km. Kernel n is 5 everywhere; shallow nn 10 → 5 (on one grid the shallow curve has a clear peak). NRML 669 216 sources, 694 MB (was 350 MB).
- Checks: 20 tests pass, edge check 1.5e-14, all 72 files read by the OpenQuake parser.
- **DECISIONS to change** (Pablo): In-slab kernel line of 16 Nov, "Result: 5 for every class and both declustering options, except 10 for the shallow class under nearest neighbour" → "Result: 5 for every class and both declustering options"; new In-slab line: "Shallow and intermediate in-slab patterns are smoothed over all in-slab cells and added; the 50 km slab-top line splits the events for the fits only (two domains left a 20 % trough along it). The Jujuy nest keeps its region (Pablo, 16 Nov, S2)."
- **Suggested commit:** `git add psha_chile8/model/inslab/build.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/{calibration,edge_check,kernel_n,nest_depths,oqread,pattern,pattern_sums,rates,south36_layers}_2026-11-16.csv psha_chile8/model/inslab/figs/2026-11-16/{pattern_gk,pattern_nn,sections_sources,mfd_sources,kernel_loglik}.png psha_chile8/model/inslab/nrml/2026-11-16/branches.json psha_chile8/WORKLOG.md`; message `S2: shallow and intermediate in-slab patterns on one grid (no trough at the 50 km slab-top line); kernel n 5 everywhere`.

## 2026-11-16 — S3: crustal domain (crustal)
- **S3 proposal (16 Nov), crustal domain = the crustal grid:** "Crustal events outside the crustal grid (`data/crustal_grid_01_2026-11-15.csv`, 0.1° cells) are left out of the crustal classes and the crustal fits, so that the rate, the pattern and the sources cover the same region."
  - This replaces the Scotia-specific prompt: the Scotia events at 57–58° S are outside the grid.
  - Effect, complete events since 1976 by weight: backarc 133 → 22, Patagonia 22 → 11, forearc 209 → 191, arc unchanged.
  - Mmax unchanged: backarc 1894, 1944 and 1861 are inside the grid; Caucete 1977 is out.
  - Truncation accepted: sources 130–300 km east of the border are not in the model.
  - Kept: the three Argentine backarc faults (Niquizanga, Las Chacras) as sources.
  - Prompt for A7 given to Pablo.

## 2026-11-16: Scotia–Antarctic boundary rule, run `2026-11-16b`, frozen (Claude Code, A7; task from S3)

Pablo: apply it. DECISIONS read again before the run; no change that touches the classes.

- **Rule in `catalog/classify.py`:** `on_scotia()`; `PB`, `FAULTS`, `MF` at the top. An event without a slab, not Antarctic interface and not west of the trench, whose nearest line is SC/AN of PB2002 (nearer than AN\SA and the seven Magallanes–Fagnano traces of `faults_gem_extra_2026-11-15.shp`) is outer rise. Test `test_scotia_antarctic_boundary_events_are_outer_rise`; `pytest catalog`: 128 pass.
- **Run:** only `classify.py` and `classify_check.py` (`RUN, CAT = "2026-11-16b", "2026-11-16a"`); locations and magnitudes are those of run `2026-11-16`. No epicentre, depth or Mw changes.
- **Result:** the 13 events of the phase 1 list change (crustal Patagonia → outer rise), and 7 more below Mw 4.5 or outside the domain at 56.1–58.1° S; no other event. Mw ≥ 4.5 in the domain: crustal 1 158.9 → 1 145.9 (Patagonia 54 → 41), outer rise 539 → 552; interface 4 502.8, in-slab 8 075.3, unclassified 3, weight-1 and split counts unchanged. Patagonia in the crustal table (Mw 5.0 from 1976): 22 → 11 at Mw ≥ 5, 2 → 0 at Mw ≥ 6. Largest Patagonia event 7.8 (1949), Mmax 8.0 unchanged. Literature events: 40 right, 34 no depth, 9 split, 2 wrong, as before.
- **Frozen:** `catalog/frozen/2026-11-16b/` (same contents as `2026-11-16`, `SHA256SUMS` verified, `DECISIONS_NOTE.md`). `catalog/frozen/2026-11-16/` checked against its sums after the run: unchanged.
- **Documents:** DATA row; `catalog/CLASSIFICATION.md` section 8, one more rule.
- **Proposed DECISIONS line (Classification):** "An event without a slab whose nearest plate boundary is the Scotia–Antarctic one (SC/AN of PB2002, Bird 2003), nearer than the AN\SA trench and the Magallanes–Fagnano traces, is outer rise and left out of the source model: 13 strike-slip events of Mw 4.8–6.2 south of Cape Horn (S3, A7; Pablo, 16 Nov). Frozen catalogue `2026-11-16b`."
- **Proposed Superseded line:** "Frozen catalogue `2026-11-16` (A9) → `2026-11-16b` (16 Nov): Scotia–Antarctic boundary events crustal Patagonia → outer rise; Patagonia N(≥ 5) about halved in the crustal table."
- **For the other sessions:** `fits/gr.py` reads `catalog/frozen/2026-11-16/catalog_2026-11-16.csv` (`CAT`); the refit needs the new path. The declustered catalogues (`fits/decluster.py`, `DATE = "2026-11-16"`) take all classes together, so the clusters do not depend on the classes, but the per-family files do. B14 (`npd_2026-11-16.csv`): the Patagonia planes lose 13 strike-slip mechanisms.
- **Commit** (from the repo root):
  - `git add psha_chile8/catalog/classify.py psha_chile8/catalog/tests/test_classify.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/catalog/frozen/2026-11-16b psha_chile8/explore/A9 psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  - `git commit -m "A7: Scotia–Antarctic boundary events out of crustal Patagonia (nearest boundary, PB2002); catalogue run 2026-11-16b frozen"`

## 2026-11-16, S2: one-grid lines in DECISIONS
- Written with Pablo's go-ahead: the In-slab kernel line now gives 5 for every class and option (scored on one grid); new In-slab line on smoothing shallow and intermediate over all in-slab cells; the Superseded in-slab sources line adds the two-domain → one-grid change.
- **Suggested commit** (replaces the one of the previous S2 entry): `git add psha_chile8/DECISIONS.md psha_chile8/model/inslab/build.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/{calibration,edge_check,kernel_n,nest_depths,oqread,pattern,pattern_sums,rates,south36_layers}_2026-11-16.csv psha_chile8/model/inslab/figs/2026-11-16/{pattern_gk,pattern_nn,sections_sources,mfd_sources,kernel_loglik}.png psha_chile8/model/inslab/nrml/2026-11-16/branches.json psha_chile8/WORKLOG.md`; message `S2: shallow and intermediate in-slab patterns on one grid (no trough at the 50 km slab-top line); kernel n 5 everywhere; DECISIONS lines`.

## 2026-11-16: crustal events outside the crustal grid, phase 1 (Claude Code, A7; task from S3)

Read again: CLAUDE.md, DECISIONS (Catalog, Classification, Superseded), my Scotia entry. Nothing changed in `classify.py` or the frozen folders. Script `explore/A9/a9_grid.py`, list `explore/A9/grid_events.csv`; on the frozen catalogue `2026-11-16b`.

- **Grid:** `data/crustal_grid_01_2026-11-15.csv`, 19 686 cells, 17.2–56.3° S, 76.3–65.3° W.
- **Crustal weight per class, now → inside the grid:**

| class | Mw ≥ 5 from 1976 | Mw ≥ 6, all years | Mw ≥ 7, all years | Mw ≥ 4.5, all years |
|---|---|---|---|---|
| forearc | 209.0 → 191.7 | 46.4 → 44.9 | 4.0 → 4.0 | 573.1 → 541.9 |
| arc | 76.1 → 76.1 | 13.7 → 13.7 | 2.0 → 2.0 | 221.1 → 221.1 |
| backarc | 133.5 → 22.8 | 25.6 → 8.5 | 4.0 → 3.0 | 310.7 → 87.1 |
| Patagonia | 11.0 → 11.0 | 8.0 → 8.0 | 3.0 → 3.0 | 41.0 → 40.0 |

  S3's numbers are confirmed. 429 events leave (crustal weight 255.7; 216 at weight 1, 213 split): 311 backarc (17.0–38.6° S, 68.9–65.0° W), 117 forearc, 1 Patagonia (2019-10-17 Mw 4.9 at 46.4° S 69.0° W). No Scotia event is left to catch. Of the 117 forearc events 116 are north of the grid's northern edge (17.0–17.7° S, southern Peru, weight 31.2; the 2001 Arequipa aftershocks and 1988-04-13 Mw 6.2 among them); the other is 1961-12-09 Mw 6.6 offshore at 43.7° S with a crustal weight of 0.007.
- **Mw ≥ 6.5 that leave:** Caucete 1977-11-23 Mw 7.5 (weight 1), 1977-11-24 Mw 6.5 (1), 1977-11-23 09:35 Mw 6.6 (crustal 0.44, in-slab 0.56), 1941-07-03 Mw 6.5 (0.44 / 0.56), 1998-05-22 Mw 6.6 at 17.8° S 65.4° W (Aiquile, Bolivia; 1), 2001-06-23 Mw 6.6 (forearc 0.27, interface 0.72), 1961-12-09 Mw 6.6 (0.007).
- **Mmax unchanged:** largest weight-1 event inside the grid: forearc 7.0, arc 7.7, backarc 7.5 (1894-10-27, hint; 1944 San Juan 7.1 and 1861 Mendoza 7.0 also inside), Patagonia 7.8.
- **Where and how (proposed):** in `subs()` of `catalog/classify.py`, where the crustal sub-class is set by position: `sub_crustal = "outside"` for an event not in a cell; one setting `GRID` at the top; helper `in_grid(lon, lat)`. The crustal **weight** is not moved: the event stays crustal (Caucete is a crustal event), only its sub-class is one that no fit unit, pattern or source reads. This differs from the brief, which moves the share to a class like outer rise: that would label Caucete outer rise, change the sums of the family weights, and touch the bin shares of the no-depth rule. With the sub-class the interface and in-slab shares stay as they are, as the brief asks, and nothing else in the catalogue moves.
- **To weigh:** the catalogue classes then depend on a file of the source model (the S3 grid); if the grid changes, the classes must be rerun. The bin shares of the no-depth rule still use the Argentine backarc events (Mw ≥ 4.5 from 1976), which is right: they tell the class of an event, not its rate.
- **Stopped for Pablo's word.**

## 2026-11-16: crustal events outside the crustal grid, run `2026-11-16c`, frozen (Claude Code, A7; task from S3)

Pablo: sub-class only. DECISIONS read again before the run; no change that touches the classes.

- **Rule in `catalog/classify.py`:** `GRID` at the top, `in_grid()`, applied in `subs()`: a crustal event that is not in a cell of `data/crustal_grid_01_2026-11-15.csv` keeps its weight and takes `sub_crustal = "outside"`. Test `test_crustal_event_outside_the_grid_keeps_its_weight`; `pytest catalog`: 129 pass.
- **Run:** `classify.py` and `classify_check.py` only (`RUN, CAT = "2026-11-16c", "2026-11-16a"`).
- **Result against `2026-11-16b`:** no weight, class, rule, position, depth or Mw changes; only `sub_crustal`, for the 429 events of the phase 1 list (311 backarc, 117 forearc, 1 Patagonia) and 3 116 below Mw 4.5 or outside the domain. Crustal weight at Mw ≥ 4.5: forearc 541.9, arc 221.1, backarc 87.1, Patagonia 40, outside 255.7. Crustal table (Mw 5.0 from 1976): forearc 191.7, arc 76.1, backarc 22.8, Patagonia 11.0, outside 127.9. Class maxima unchanged.
- **Frozen:** `catalog/frozen/2026-11-16c/` (`SHA256SUMS` verified; `INPUTS_SHA256` now also has the grid file; `DECISIONS_NOTE.md`). The folders `2026-11-16` and `2026-11-16b` checked against their sums: unchanged.
- **Documents:** DATA row; `catalog/CLASSIFICATION.md` section 8, one more rule.
- **Who reads the sub-class:** `fits/gr.py` selects the four crustal names, so `outside` drops out by itself once `CAT` points to the new file. Any script that lists the values of `sub_crustal` (B14 planes, S3 pattern, GM1) should be checked for the new value.
- **Proposed DECISIONS line (Classification):** "A crustal event outside the crustal grid (`data/crustal_grid_01_2026-11-15.csv`) keeps its crustal weight and takes the sub-class `outside`, read by no fit, pattern or source, so that rate, pattern and sources cover the same region (S3, A7; Pablo, 16 Nov). The classes are rerun if the grid changes. Frozen catalogue `2026-11-16c`."
- **Proposed Superseded line:** "Crustal classes by position alone, whatever the distance to Chile (A7) → events outside the crustal grid in the sub-class `outside` (16 Nov): backarc 133.5 → 22.8 and forearc 209.0 → 191.7 by weight at Mw ≥ 5 since 1976. Frozen catalogue `2026-11-16b` → `2026-11-16c`."
- **Commit** (from the repo root; it also takes the uncommitted Scotia work of run b):
  - `git add psha_chile8/catalog/classify.py psha_chile8/catalog/tests/test_classify.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/catalog/frozen/2026-11-16b psha_chile8/catalog/frozen/2026-11-16c psha_chile8/catalog/figs psha_chile8/explore/A9 psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  - `git commit -m "A7: Scotia–Antarctic boundary events to outer rise (run 2026-11-16b); crustal events outside the crustal grid in the sub-class outside (run 2026-11-16c); both frozen"`
- **S3 (16 Nov):**
  - `fits/gr.py` now reads catalogue `2026-11-16c` (A7), while the crustal fits are still `16d` (catalogue 2026-11-16). The crustal code now pins its catalogue: `background.CAT`, passed to every `gr.load` call in model/crustal.
  - Reran the chain: the 16d tables are identical, so only one figure had read the new catalogue.
  - On the next fits, set `CAT` with the fits date.
  - New figure `figs_s3.joins()` → `figs/2026-11-16d/join_{A,B,Bmm}.png`.
  - `multifault.lofs` saves its MFDs (`tables/mf_A_lofs_mfd_2026-11-16d.npz`).

## 2026-11-16: fits on the catalogue 2026-11-16c, run 2026-11-16e (Claude Code, B11/B12; task from A7)

Read again before and after: CLAUDE.md, DECISIONS (Statistics, Crustal and faults, Superseded; the lines for the Scotia rule and the crustal grid are not in DECISIONS yet, only proposed by A7), the A7 entries for runs `2026-11-16b` and `2026-11-16c`. Run name `2026-11-16e` was free.

- **Catalogue.** `fits/gr.py`: `CAT` → `catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv` (checksum verified). Against `2026-11-16`: 57 853 events of Mw ≥ 3.5 in the domain in both; no Mw, σ, position or depth changed; 13 events moved their weight from crustal to outer rise; `sub_crustal` is `outside` for 1 150 events of Mw ≥ 3.5 (786 backarc, 360 forearc, 4 Patagonia).
- **The new sub-class.** Nothing in `fits/` reads `sub_crustal` by listing its values: `gr.load()` builds one weight column per class by name (`CLASSES`), so the `outside` events get no weight in any unit; `decluster.py` reads only the family weights (`w_interface`, `w_inslab`, `w_crustal`, `w_outer_rise`, `w_unclassified`). The run, the comparison, the declustered fits and the figures went through unchanged; 31 tests pass. Counted weight in the crustal table as A7 gave it: forearc 191.7, arc 76.1, backarc 22.8, Patagonia 11.0. Largest weight-1 events unchanged (7.0, 7.7, 7.5, 7.8).
- **Rules:** those of `fits_2026-11-16d.csv`, no code change: crustal table 5.0 from 1976, one b for the crustal family, Mmax from weight-1 events. Completeness table and Mc of every window identical.
- **The family b is fitted without the `outside` events:** 1.009 ± 0.053 tapered (1.006 ± 0.054 cut; 782 events, 278 counted), against 0.975 ± 0.042 in 16d. Reason: the family unit is the sum of the four classes, and the rule of A7 is that no fit reads `outside`, so that b, rates, pattern and sources describe one region. For comparison: with the outside events the family b is 0.974 ± 0.042 (395 counted), and the outside events alone give 0.896 ± 0.078 (117 counted; a third of them the Caucete sequence of 1977, the rest the Argentine backarc and southern Peru). The two differ by 0.03, inside the standard deviation; **this is a choice for Pablo** (b from the wider region with rates from the grid would give back 0.974).

| unit (tapered) | Mmax | corner, 16d → 16e | b | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 since 1976, fitted / observed |
|---|---|---|---|---|---|---|---|
| interface and the four segments | 9.7 / 9.7 / 9.3 / 8.7 / 9.0 | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |
| in-slab shallow, intermediate, Jujuy nest | 8.2 / 8.2 / 7.4 | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |
| crustal family | 8.0 | 7.79 → 7.80 | 0.975 → 1.009 (0.053) | 7.98 → 5.47 (−31 %) | 0.844 → 0.535 (−37 %) | 0.0847 → 0.0497 (−41 %) | 2.5 / 1.0 |
| forearc | 7.2 | 6.99 → 7.00 | 0.975 → 1.009 | 3.82 → 3.48 (−9 %) | 0.393 → 0.332 (−15 %) | 0.0179 → 0.0144 (−20 %) | 0.7 / 1.0 |
| arc | 7.9 | 7.69 → 7.70 | 0.975 → 1.009 | 1.390 → 1.383 (−0.5 %) | 0.147 → 0.135 (−8 %) | 0.0144 → 0.0123 (−15 %) | 0.6 / 0 |
| backarc | 7.7 | 7.49 → 7.50 | 0.975 → 1.009 | 2.36 → 0.403 (−83 %) | 0.249 → 0.039 (−84 %) | 0.0227 → 0.0033 (−85 %) | 0.2 / 0 |
| Patagonia | 8.0 | 7.79 → 7.80 | 0.975 → 1.009 | 0.416 → 0.202 (−51 %) | 0.044 → 0.020 (−55 %) | 0.0044 → 0.0018 (−58 %) | 0.1 / 0 |

- The cut-line fits move the same way (b 0.972 → 1.006). The interface, in-slab and nest rows are identical to 16d in every column.
- The arc lost no event; it moves only through the family b. The backarc keeps 27 events (20 counted) and Patagonia 11 (10 counted): their own b would be 1.26 and 1.66, so they depend entirely on the family b.
- **Cross-check against the events of Mw ≥ 7 since 1905** (not in the fit; expected by the line / observed by weight): forearc 1.8 / 3.5, arc 1.5 / 1.7, backarc 0.4 / 0.9 (San Juan 1944; Caucete 1977 is now outside), all inside the Poisson band. Patagonia 0.2 / 1.7 fails: the two events are the Magallanes doublet of 1949-12-17 (Mw 7.8), which belong to the Magallanes–Fagnano fault source, not to the background.
- **Declustering.** `fits/decluster.py` reads the classes only for the per-family methods (the family of the largest of the five family weights) and never `sub_crustal`. All five methods were run again as `catalog/declustered/*_2026-11-16e.csv` (the script builds them together). Compared with the `_2026-11-16` files: `gk`, `nn`, `nn_depth` and their `_m35` files are identical; `gk_family` has the same mainshock flags (6 006) and differs only in cluster labels; `nn_family` differs in 2 flags (10 923 → 10 921; 4 flags from Mw 3.5), through the 13 Scotia events that changed family. Completeness tables of the declustered catalogues unchanged.
- **Declustered fits** (`fits_declustered_2026-11-16e.csv`; two options, table full, own family b): family b 0.923 → 0.922 (Gardner–Knopoff per family) and 0.999 → 1.001 (nearest neighbour per family), so the declustered b hardly moves, unlike the full one. N(≥ 6): forearc −8 % and −9 %, arc 0 % and −0.5 %, backarc −75 % and −78 %, Patagonia −45 % and −53 %. Interface, in-slab and nest rows identical. Checks as before.
- **Rows over the thresholds** (0.02 in b, 5 % in N(≥ 6), 0.1 in Mmax; no Mmax moved):
  - S1 (interface, segments; full and declustered): none.
  - S2 (in-slab shallow, intermediate, Jujuy nest): none.
  - S3, `fits_2026-11-16e.csv`, both shapes: `crustal`, `forearc`, `arc`, `backarc`, `patagonia`, all by b (+0.034) and by N(≥ 6) (−37, −15, −8, −84, −55 %).
  - S3, `fits_declustered_2026-11-16e.csv` (gk_family and nn_family, table full, own b): `forearc`, `backarc`, `patagonia` and `crustal` by N(≥ 6); the `arc` rows are under the thresholds.
- **Files.** New: the nine `*_2026-11-16e.csv` tables in `fits/tables/` and the ten `catalog/declustered/*_2026-11-16e.csv`. Nothing older overwritten; the 16d figures copied to `fits/figs/2026-11-16d/`, then `fits/figs/*.png` regenerated (classes, interface segments, large-event check, b against floor, methods, three declustered figures). `fits/FITS.md` section 12, `fits/DECLUSTER.md` section 10, two DATA rows.
- **For S3:** `model/crustal/*.py` read `DATE = "2026-11-16d"`; they need `2026-11-16e` (fits and declustered fits). The background now covers the grid only: backarc N(≥ 6) 0.039 per year, Patagonia 0.020.
- **Open for Pablo:** the family b with or without the outside events (1.009 against 0.974); it moves the arc N(≥ 6) by 8 % and N(≥ 7) by 15 %.
- **Proposed lines for DECISIONS** (Pablo adds; not written):
  - Statistics, in the line of the shared crustal b: "The family is the four classes inside the crustal grid, without the `outside` events: b 1.009 ± 0.053 on the catalogue `2026-11-16c` (0.974 with them)."
  - Statistics: "Fits, current: `fits/tables/fits_2026-11-16e.csv` and `fits_declustered_2026-11-16e.csv` on the catalogue `2026-11-16c` and the declustered catalogues `catalog/declustered/*_2026-11-16e.csv`; interface, in-slab and nest rows identical to `fits_2026-11-16.csv`."
  - Crustal and faults: "Background rates cover the crustal grid only: N(≥ 5) per year forearc 3.48, arc 1.38, backarc 0.40, Patagonia 0.20. The Magallanes doublet of 1949 is not reproduced by the Patagonia background (0.2 events of Mw ≥ 7 expected since 1905); it belongs to the Magallanes–Fagnano fault."
  - Superseded: "Fits `fits_2026-11-16d.csv` on catalogue 2026-11-16 → `fits_2026-11-16e.csv` on catalogue 2026-11-16c (16 Nov): crustal family b 0.975 → 1.009, backarc N(≥ 5) 2.36 → 0.40, Patagonia 0.42 → 0.20."
- **Commands** (from `psha_chile8/fits/`): `OMP_NUM_THREADS=1 python decluster.py` (3 min), `python run.py` (95 s), `OMP_NUM_THREADS=1 python run_declustered.py` (3 min); `pytest fits/tests` from `psha_chile8/`.
- **Commit** (from the repo root):
  - `git add psha_chile8/fits/gr.py psha_chile8/fits/run.py psha_chile8/fits/run_declustered.py psha_chile8/fits/decluster.py psha_chile8/fits/FITS.md psha_chile8/fits/DECLUSTER.md psha_chile8/fits/figs psha_chile8/fits/tables/*_2026-11-16e.csv psha_chile8/catalog/declustered/*_2026-11-16e.csv psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  - `git commit -m "Fits 2026-11-16e on catalogue 2026-11-16c: crustal events outside the grid and Scotia events out of the units; declustered catalogues rebuilt"`
- **Decided by Pablo (16 Nov): the crustal family b stays without the `outside` events (1.009 ± 0.053).** The "Open for Pablo" line above is closed; `fits_2026-11-16e.csv` stands as written, and the proposed DECISIONS line for the family b can go in as it is. `fits/FITS.md` section 12 updated.

## 2026-11-16, GM1 summary figures and GMM set tables

- **What:**
  - `gmm/summary.py` writes four summary figures in the pituplots style (report theme, darkgrid): `summary_ranking`, `summary_bias`, `summary_large`, `summary_sets`.
  - The four GMM sets as one table, `gmm/tables/gmm_sets_2026-11-15.csv`.
  - Handoff note for GM2 and the tornado: `gmm/SUMMARY_GM1.md`.
  - REPORT_GM1 section 10; one new test (7 gmm tests pass).
- **New:** GEM's Zhao et al. (2006), Abrahamson et al. (2015) high and Montalva et al. (2016) were scored on the same GM1 records. Zhao 2006 (interface) and Montalva 2016 (both classes) would rank at the top of the 14 candidates.
- **No decisions taken.** For GM2 (Pablo):
  - Montalva 2016 or 2017;
  - whether Zhao 2006 joins the candidates;
  - whether the weights follow all events or the Mw ≥ 6.5 events.
- **Commands** (from `psha_chile8/gmm/`): `python summary.py` (25 s).
- **Commit** (from the repo root):
  - `git add psha_chile8/gmm/summary.py psha_chile8/gmm/SUMMARY_GM1.md psha_chile8/gmm/REPORT_GM1.md psha_chile8/gmm/tests/test_gmm_residuals.py psha_chile8/gmm/figures/summary_*.png psha_chile8/gmm/tables/gmm_sets_2026-11-15.csv psha_chile8/gmm/tables/scores_with_gem_2026-11-15.csv psha_chile8/gmm/tables/mean_rank_2026-11-15.csv`
  - `git add -p psha_chile8/WORKLOG.md psha_chile8/FIGURES.md` (GM1 lines only)
  - `git commit -m "GM1: summary figures (ranking, bias, large events, the four GMM sets on scenarios), table of the tornado GMM sets, GEM models scored on the records, handoff note"`
- **DECISIONS.md edited by Claude Code at Pablo's word ("write into decisions", 16 Nov):** only the lines of the fits. Statistics: the current fits line (`fits_2026-11-16e.csv`, catalogue `2026-11-16c`; the 16d line kept below it), the declustered fits line, the family b (without the `outside` events, 1.009). Crustal and faults: background rates on the grid and the note on the 1949 doublet. Superseded: one line. **Not written, because they belong to A7:** the Scotia–Antarctic rule, the crustal-grid sub-class `outside` and the frozen catalogue `2026-11-16c` (Catalog still names `2026-11-16`); their proposed lines are in the A7 entries above. Git: `git add` was denied to Claude Code in this setup; Pablo commits with the lines above plus `psha_chile8/DECISIONS.md psha_chile8/LEARNINGS.md`.
- **A7's lines written into DECISIONS.md by the B11/B12 session at Pablo's word ("add them please", 16 Nov),** taken from the two A7 entries above without changing their content: Catalog (frozen catalogue `2026-11-16c` replaces `2026-11-16`), Classification (the Scotia–Antarctic rule; the sub-class `outside` for crustal events outside the crustal grid), Superseded (one line). DECISIONS now agrees with the fits lines that name the catalogue `2026-11-16c`.

## 2026-11-16, GM1 figures redone in the pituplots style; report updated

- **Figures:** `gmm/figs.py` was rewritten in the pituplots report theme with darkgrid panels, and runs alone on the tables (`python figs.py`, 25 s).
  - New: `resid_example.png`, an introduction that shows one model's residuals.
  - `z_<class>.png` and `trends_<class>.png` replace the twelve per-period figures. They now show only the eight models of the tornado sets, with the three periods together.
  - `scores.png` is ordered by mean rank; `tau_phi.png` is relabelled.
- **REPORT_GM1:**
  - a short summary at the top;
  - plain-words guides for residuals, δB, δW, τ, φ, LLH and EDR;
  - all figures embedded;
  - `records.py` named correctly.
- **Commit:**
  - `git add psha_chile8/gmm/figs.py psha_chile8/gmm/REPORT_GM1.md psha_chile8/gmm/figures`
  - `git add -u psha_chile8/gmm/figures` (stages the removed old figures)
  - `git commit -m "GM1: figures in the pituplots style, residual introduction figure, report reading guide"`

## 2026-11-16 — S3 rerun on fits 2026-11-16e (crustal)
- **Done:**
  - Crustal code on `fits_2026-11-16e.csv` and `fits_declustered_2026-11-16e.csv`, catalogue `2026-11-16c` (pinned in `background.CAT`), declustered families `_2026-11-16e`; `DATE = "2026-11-16e"`.
  - Reran background, faults, join, large, arc, lower (tornado row), LOFS multi-fault (A, 15 km), and the figures in `figs/2026-11-16e/`.
  - Join figure redrawn per 0.1 bin (Pablo: the cumulative one was unreadable); the arc drawn twice (single faults, multi-fault).
  - Report: `REPORT_S3.md` section 10. Tests: 14 passed, 2 skipped (the fit-list test now allows the 5-decimal rounding of the table, atol 6e-6).
- **Kernel n:** 5 for every class and option (the backarc's 7 in-grid test events).
- **What moved (A, tapered, Mw 6):**
  - Faults / fit: forearc 0.15 → 0.18, arc 3.0 → 3.3, backarc 0.20 → 1.28, Patagonia 1.65 → 3.9.
  - Background N(≥ 6): forearc 0.333 → 0.272; backarc 0.200 → 0 (the faults now fill the fit from Mw 6); arc and Patagonia 0.
  - Background N(≥ 7): forearc 0.0169 → 0.0134; backarc 0.0209 → 0.
  - Same ratios for B and B-mm in REPORT_S3 section 10. The tornado row is there too: backarc 1.23–1.43, Patagonia 2.7–8.7.
- **For Pablo:**
  - **(1) Backarc faults outside the grid.** The three Argentine faults (Niquizanga, Las Chacras a and b) are outside the grid, their events are `outside`, but they are still sources: 0.0095 of the backarc's 0.050 at Mw 6.
    - Proposed: by the same domain rule, faults whose trace lies wholly outside the grid leave the model.
    - Magallanes–Fagnano stays: its events are inside the grid, and 60 % of its trace is.
    - Even without the three, the backarc faults are at the fit (1.03), so the backarc has no background above Mw 6.
  - **(2) Patagonia:** the Magallanes–Fagnano fault expects 0.16 events of Mw ≥ 7.5 since 1905 (0.04–0.32), against the 1949 doublet: P(≥ 1) = 0.15. It does carry the doublet, at the low end.
  - **(3) Arc:** the multi-fault branch passes at ψ 0.6 and 0.8; single faults fail, as before.
- **Proposed DECISIONS line (Crustal and faults):** "A crustal fault whose trace lies wholly outside the crustal grid is not a source, by the rule of the crustal domain: AR-0025a Niquizanga, AR-0027a and b Las Chacras (S3, 16 Nov)." This is for Pablo's word.
- **Follow-up, same day:**
  - The figure titles are plain now; the reading notes moved out of the figures into `gmm/FIGURES_GUIDE.md`, a study guide that also lists every figure for slides.
  - Commit: add `psha_chile8/gmm/FIGURES_GUIDE.md psha_chile8/gmm/summary.py` to the lines above.

## 2026-11-16: B14 on catalogue 2026-11-16c (Claude Code)
- **Done:** `npd.py` on `catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv` and `fits/tables/table_2026-11-16e.csv` (`DATE = "2026-11-16c"`, `PREV = "2026-11-16"`), 10 % rule, no borrow, plane choice unchanged. New `npd_2026-11-16c.csv`, `tables/{counts,shares,dropped,moved}_2026-11-16c.csv`, `figs/ternary_2026-11-16c.png` (and `ternary.png`); `REPORT_B14.md` rewritten. `npd_2026-11-16.csv` kept. Tests: 3 pass. DATA row 2026-11-16c (B14).
- **Moved:** in-slab classes and the arc unchanged. Forearc 113.4 → 104.3 weighted (17 events `outside`), planes by one 5° step, strike-slip still dropped (0.074). Backarc 50.2 → 8.0 (45 `outside`: 28 reverse, 15 strike-slip, 2 normal). Patagonia 18 → 7: all 11 that left went with the Scotia rule (10 strike-slip, 1 reverse; 56.9–57.9° S, Mw 5.0–6.2), none with `outside`.
- **Conflict, for Pablo:** backarc (8) and Patagonia (7) are below the B14 family minimum of 15, so the table gives both the pooled crustal distribution (N / R / SS 0.23 / 0.52 / 0.25). DECISIONS says Patagonia keeps its own. Own Patagonia: 0.14 / 0.43 / 0.43 on 7 events (normal = one event), planes not robust. Options: keep the count rule (as written), or Patagonia own regardless; the backarc pooled either way unless the minimum changes.
- **Proposed DECISIONS line (In-slab and Crustal, replaces the B14 line once chosen):** "Nodal planes per class from the catalogue mechanisms (B14, `npd_2026-11-16c.csv`, on the catalogue 2026-11-16c; Frohlich types, one plane per type and its auxiliary at half weight, types below 10 % dropped and the rest renormalised); backarc and Patagonia below 15 weighted mechanisms take the pooled crustal distribution (16 Nov); used from S5; not a tornado factor." Superseded line: `npd_2026-11-16.csv` → `npd_2026-11-16c.csv` (catalogue 2026-11-16c).
- **Suggested commit:** `git add psha_chile8/model/mechanisms psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `B14 on catalogue 2026-11-16c: npd_2026-11-16c.csv, backarc and Patagonia pooled below 15 mechanisms`
- **Decided by Pablo (16 Nov): crustal faults wholly outside the grid are not sources.** `faults.load` drops them (`faults.GRID`); that is AR-0025a, AR-0027a and AR-0027b in A, B and B-mm. Magallanes–Fagnano stays. Test added (15 passed, 2 skipped).
  - The 2026-11-16e fault, join, arc and tornado tables and the figures were rewritten in place with the rule. They are this session's own outputs of today.
  - Backarc faults / fit at Mw 6: 1.28 → 1.03 (A, B, B-mm). The background is still 0 above Mw 6, and the faults at Mw ≥ 7 are half the fit.
  - The proposed DECISIONS line above stands, now decided.


## 2026-11-16, deck 261116: ground-motion part
- Seven slides after "Summary: catalogue": hazard ours against MASCSN26 and GEM (MASCSN26 report Figure 78, two panels; our psha_chile6 city PGA), records, residuals, bias, LLH on all and on Mw ≥ 6.5 events, the four tornado sets (crop of `gmm/figures/summary_sets.png`), summary. New figures from `presentations/261116_psha8_results/figs/gm.py` on the GM1 tables of 15 Nov; nothing in `gmm/` changed.
- The MASCSN26 and GEM map values are read from the report's colour scale (Vs30 900 and 760 against our 800): a rough comparison, flagged in the slide notes.
- **Suggested commit:** `git add presentations/261116_psha8_results psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`; message `Deck 261116: ground-motion part (GM1 residuals, sets, hazard comparison)`.

## 2026-11-16, S2: one source per cell (run 2026-11-16b)
- **Done** (main conversation, Pablo 16 Nov): shallow and intermediate written as one point source per cell with the summed MFD (EvenlyDiscretized from Mw 5.5), the C14 depths and the two nodal planes; the nest a separate source, unchanged. `build.py`: `RUN = "2026-11-16b"`, `GROUPS`, `guard()`, `write()` returns the drop table and the class shares. Files in `model/inslab/nrml/2026-11-16b/` (48 files, 2 per branch, 336 888 sources, 350 MB); `nrml/2026-11-16/` unchanged. REPORT_S2 section 8.
- **Near-empty cells:** cut at 1e-8 of the branch total with the 50 km guard around in-slab events of Mw ≥ 7 (in-slab weight ≥ 0.5; 2 700 cells). Nothing is dropped in any branch: the weakest cell holds 1.3e-6 of the total.
- **Class shares** for S5: `tables/class_share_2026-11-16.csv` (per cell and rate branch, shallow and intermediate shares above Mw 5.5 and in the Mw 7.0 bin).
- **Checks:** per class, the sum over cells equals the rate table within 4e-15 in every branch; 22 tests pass; all 48 files read by the OpenQuake parser (rates within 2e-7).
- **Timing** at the 14 cities, reference branch, four in-slab GMMs, `individual_rlzs = true` (queue empty, one job at a time): one file per class (calc 516) 4 min 03 s (preclassical 139 s, classical 234 s), 27 884 sources, 5.0 M ruptures, peak 796 MB; one source per cell (calc 517) 2 min 21 s (80 s, 132 s), 14 037 sources, 2.5 M ruptures, peak 669 MB. PGA 475 yr the same within 0.0006 % at every city (La Serena 0.96 g, Iquique 0.73 g, Calama 0.63 g, Santiago centro 0.59 g).
- **Code:** `oqcheck.py` writes the timing jobs (`timing_jobs()`, 14 cities, `gmm_lt_4.xml`) into `oqcheck/2026-11-16b/` and reads them (`timing_report()`, cities matched by coordinates since OpenQuake sorts the sites); the parser check reads the group files against `tables/drop_<RUN>.csv`.
- **Proposed DECISIONS lines** (Pablo adds):
  - In-slab: "Shallow and intermediate in-slab are written as one point source per cell, the MFD the sum of the two class MFDs (EvenlyDiscretized from Mw 5.5), with the C14 depths of the cell; the Jujuy nest is a separate source (Pablo, 16 Nov, S2; `model/inslab/nrml/2026-11-16b/`). Same hazard as one file per class within 0.001 % at the 14 cities, 58 % of the run time."
  - In-slab: "A cell is left out when its rate above Mw 5.5 is below 1e-8 of the branch total, unless it lies within 50 km of an in-slab event of Mw ≥ 7 (in-slab weight ≥ 0.5). On the 16 Nov patterns no cell falls below the cut (Pablo, 16 Nov, S2)."
  - In-slab / Logic tree: "Nodal planes of the in-slab sources from S5: the B14 distributions of shallow and intermediate mixed per cell by the class share of the cell rate (`model/inslab/tables/class_share_2026-11-16.csv`); until then the two fixed planes (Pablo, 16 Nov)."
- **Suggested commit:** `git add psha_chile8/model/inslab/{build,oqcheck}.py psha_chile8/model/inslab/tests/test_s2.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/{drop_2026-11-16b,oqread_2026-11-16b,timing_2026-11-16b,timing_pga_2026-11-16b,class_share_2026-11-16}.csv psha_chile8/model/inslab/nrml/2026-11-16b/{branches.json,source_lt_inslab.xml} psha_chile8/model/inslab/oqcheck/2026-11-16b/*.{ini,xml,csv} psha_chile8/WORKLOG.md`; message `S2: in-slab shallow and intermediate as one point source per cell with the summed MFD (nrml/2026-11-16b); class shares for S5; 1e-8 cut with 50 km guard (nothing dropped); timing at the 14 cities, same hazard in 58 % of the time`.

## 2026-11-16, S2: in-slab rates against MASCSN26
- From the MASCSN26 report (Table 16 and Figure 33, Weichert a, b of zones 4–7; Mmax Tables 12–15; §3.3, §8.2), not from its repository. Ours summed over the same zones (latitude band, slab top 50–160 km). REPORT_S2 section 9, `model/inslab/tables/mascsn_compare_2026-11-16.csv`.
- Zones 5–7 (18–38° S, where both cover the slab): ours −11 % at N(≥ 5.5), −37 % at N(≥ 7). Ratio falls with magnitude (0.9 at 5.5 to 0.4 at 8 in zones 5 and 7) because our b is 1.14–1.16 (full catalogue) against their 0.97–1.07 (Knopoff windows); our own GK-declustered b is 0.93–1.03, close to theirs. Zone 4 (15–18° S) is mostly Peru, outside our grid.
- Whole model: ours has 25 % of its N(≥ 5.5) under the shallow slab (top < 50 km), which MASCSN does not model as in-slab; total N(≥ 5.5) 10.1 against 8.0 (+26 %), N(≥ 7) 0.176 against 0.218 (−19 %).
- Nothing changed in the model. Commit: `git add psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/mascsn_compare_2026-11-16.csv psha_chile8/WORKLOG.md` (with the 2026-11-16b commit of the previous entry, or after it).
- **S3 (16 Nov): LOFS jump × depth study** (A; jumps 5 / 10 / 15 / 20 km; depths 10 / 20 km; ψ 0.6–1.0; 10 seeds; REPORT_S3 10c; `figs/2026-11-16e/mf_lofs_study_A.png`).
  - New in `multifault.lofs`: a depth loop, and the large-event check before 1976 (`HIST`: Mw ≥ 7 since 1905, ≥ 7.5 since 1830, the historical steps of the B11 table, out of the fit).
  - Depth 20 km reaches Mmax 7.7–7.9 and the Mw ≥ 7 record (1.6 against 1.7 at 15 km, ψ 0.8), but overshoots the Mw ≥ 6 count since 1976 (12.3 against 6.5, p 0.04).
  - Depth 10 km fits Mw ≥ 6 at 15–20 km jumps but stays at 0.6–1.1 of Mw ≥ 7 (against 1.7).
  - More seeds only smooth the curves.
  - Join figures now show the pre-1976 large events (open diamonds).
  - Open for Pablo: the depth of the multi-fault branch (10, 20 or both as the depth branch), and whether the 20 km jump is acceptable (whole-system chains, NMS up to 93 % on one fault).
- **S3 queue (Pablo, 16 Nov; not started):**
  - (1) Fault Mmin raised or fitted, so the arc bulge goes and more moment is left for large ruptures. Discussion only for now.
  - (2) The LOFS jump × depth study for B and B-MASCSN, as for A (REPORT_S3 10c).
- **S3 (16 Nov): LOFS jump × depth study for B and B-mm** (REPORT_S3 10d; `figs/2026-11-16e/mf_lofs_study_{A,B,Bmm}.png`).
  - B fails everywhere: 18–84 expected arc Mw ≥ 6 against 6.5.
  - B-mm passes only at a 20 km jump, 20 km depth and ψ 0.6 (10.5, p 0.10), with 1 400 km chains.
  - B's chains reach 700 km at a 10 km jump and 1 460 km at 20 km.
  - `multifault.partition` vectorised: identical rates; B at a 20 km jump 22 s → 2 s per run.
  - Memory note kept: rupture extents per jump (Pablo: an 800 km crustal rupture is not credible); fault Mmin stays 6.0 (the Aysén fjord sequence is on a fault).
- **S3 (16 Nov): six check figures** (`model/crustal/figs_checks.py`, `figs/2026-11-16e/check_*.png`; REPORT_S3 10e; FIGURES rows).
  - Trade-off: only A multi-fault cases pass both counts.
  - Moment: the arc faults release about the catalogue moment, so the bulge is the shape. Patagonia faults release 1/5 of the catalogue moment, yet are over at Mw 6.
  - Near-fault share: arc 30–57 % and Patagonia 0–29 % of the observed Mw ≥ 6 near a trace, against 100 % in the model.
  - Forearc under by 2× at Mw 6.5–7 with the family b.
  - Open for Pablo: the join rule (background zero from the first filled bin) gives the arc and Patagonia no off-fault Mw ≥ 6, while half or more of the observed ones are off-fault.

## 2026-11-16 — S3: crustal OpenQuake files ready (2026-11-16e)
- **Ready for S5:** `model/crustal/nrml/2026-11-16e/branches.json` (`"ready": true`), 59 files, 373 MB.
  - Tree: 84 branches, flattened: declustering 0.5 / 0.5 × fault system 0.5 / 0.5; segmented 36 branches with the DECISIONS weights; multi-fault 6 branches equal.
  - Tornado: reference plus 13 rows.
  - Hand-off note: `model/crustal/S5_HANDOFF.md`.
  - Jobs need `investigation_time = 1.0` and maximum distance 300 km.
- **Check:**
  - `tables/oqcheck_2026-11-16e.csv`: every file read by OpenQuake's converter; multi-fault sources split against their sections as the engine does; rates within 4.2e-6.
  - Calc 532 (`oqcheck/2026-11-16e/`): the reference branch at Puerto Aysén runs (PGA 475 mean 0.46 g with ASK14 alone; not interpreted). It ran single-process and waited for S5's calc 531.
- **Code:** `build.py` (rewritten), `mfsource.py` (new), `nrml.py`, `oqcheck.py` (rewritten), `background.py` (`NPD`, `npds`, `mix`). Tests: crustal 20 passed.
  - Full suite: 328 passed, 1 failed, outside S3: `gmm/tests/test_gmm_residuals.py` imports `run` and gets `fits/run.py`, a module-name clash.
- **Format notes** (OpenQuake 3.27, found while building):
  - multi-fault rupture section ids are comma-separated;
  - a section must be one surface (so one planar surface per trace segment);
  - multi-fault and geometry files must be NRML 0.5, with the investigation time on the sourceModel and a sourceGroup.
- **Decisions taken (REPORT_S3 section 11), proposed DECISIONS lines (Crustal and faults):**
  - "Crustal fault system, two branches 0.5 / 0.5 (Pablo, 16 Nov):
    - segmented: single-fault simple-fault sources, six MFD shapes, Leonard Mmax, ψ × depth × shape as in DECISIONS;
    - multi-fault: the Liquiñe–Ofqui faults of database A by the SHERIFS partition (Chartier et al. 2017, 2019), UCERF3 filters with a 15 km jump, Leonard Mmax on the linked area capped at the class Mmax, ψ 0.6 / 0.8 / 1.0 × depth 10 / 20 km, equal weights. Linked ruptures in one multi-fault source per branch (rates the mean of 10 seeds); single-fault LOFS ruptures as simple-fault sources with their SHERIFS MFD; the other faults with the mean of the six shapes.
    - The class maximum is no longer a variant."
  - "Crustal background point sources: the four classes summed per cell; nodal planes per cell mixed from the B14 class distributions by the class rates there; 0–30 km, hypocentre 10 km; source Mmin 5.5 as interface and in-slab (16 Nov)."
  - "Crustal tornado reference: multi-fault A, 15 km jump, ψ 0.8, depth 10 km, tapered fit, Gardner–Knopoff pattern. Rows:
    - nearest-neighbour pattern; fit cut at Mmax; declustered background rates (lower bound); no faults;
    - segmented system; ψ 0.6 and 1.0; depth 20 km;
    - jumps 5 / 10 / 20 km (20 km not credible, chains to 860 km);
    - databases B and B-mm (16 Nov)."
  - Superseded: "Crustal fault variants with the class-maximum Mmax (sensitivity, 15 Nov) → the multi-fault branch (16 Nov). Crustal source Mmin 5.0 → 5.5 (16 Nov)."
- **Open:** fault-system weights 0.5 / 0.5 are mine (Pablo: equal weights); confirm.
- **Suggested commit** (the NRML files stay untracked, as before):
  - `git add psha_chile8/model/crustal/{background,smooth,faults,join,large,arc,kernels,multifault,mfsource,build,nrml,oqcheck,lower,figs_s3,figs_checks}.py psha_chile8/model/crustal/tests/test_crustal.py psha_chile8/model/crustal/{REPORT_S3,S5_HANDOFF}.md psha_chile8/model/crustal/tables/*2026-11-16e* psha_chile8/model/crustal/figs/2026-11-16e psha_chile8/model/crustal/nrml/2026-11-16e/branches.json psha_chile8/model/crustal/nrml/2026-11-16e/lt_crustal_*.xml psha_chile8/model/crustal/oqcheck/2026-11-16e/job.ini psha_chile8/model/faults/compare.py psha_chile8/WORKLOG.md psha_chile8/FIGURES.md`
  - leave out the large tables and caches (`tables/rates_2026-11-16e.csv`, `tables/oqcheck_2026-11-16e.csv`, `tables/mfsrc_*.pkl`): `git reset psha_chile8/model/crustal/tables/rates_2026-11-16e.csv psha_chile8/model/crustal/tables/oqcheck_2026-11-16e.csv psha_chile8/model/crustal/tables/mfsrc_*`
  - message: "S3/S5b: crustal model on fits 2026-11-16e: kernel n per class, faults outside the grid dropped, Liquiñe–Ofqui multi-fault branch (SHERIFS, 15 km), OpenQuake files, tree and tornado rows"

## 2026-11-16 — S5a: interface and in-slab hazard jobs (and the crustal family, S5b, after the S3 note)
- **Read:** CLAUDE.md, PLAN, DECISIONS (Interface, In-slab, Crustal and faults, GMMs, Logic tree, Hazard runs), LEARNINGS, the brief, and the S3 hand-off note (`model/crustal/S5_HANDOFF.md`, passed on by Pablo). DECISIONS read again before finishing: unchanged since 04:27, so the choices below still hold.
- **Done:**
  - psha_chile7 hazard code ported into `hazard/`: `config.py`, `jobs.py` (instead of `logic_tree.py`), `build.py`, `nrml.py`, `run_all.sh`, `combine.py` (unchanged), `post.py` (load, wquant, iml), `check_tree.py` (level 1, two families), `tornado_final.py`, plus `trees.py`, `branches.py`, `tables.py`, `crustal_ready.py`; tests `hazard/tests/test_hazard.py` (8 pass).
  - The families are read from their `branches.json`: interface `nrml_2026-11-16`; in-slab `nrml/2026-11-16b` (the S2 timing check passed); crustal `nrml/2026-11-16e`.
  - Branch tables: `hazard/branches_interface.csv`, `hazard/branches_inslab.csv`.
  - 66 OpenQuake jobs ran one at a time, calcs 522–591, 4.4 h in all. Interface reference 291 s, in-slab 133 s, interface tree (864 rlz) 57 min, crustal reference 147 s, crustal tree 585 + 236 s.
  - check_tree level 1 passes (mean 3.9e-6, every paired curve within 1.6e-5, quantiles 2.8e-6).
  - Tornado (interface + in-slab, and all three families), family-tree curves and PGA 475 tables. Report: `hazard/REPORT_S5a.md`.
- **Choices made here:**
  - The interface reference keeps the scaling level at 1/3 each (DECISIONS applies it to every interface source); b option own.
  - `strict = false` in every job: OpenQuake refuses fault sources above 52 000 ruptures, and the margin source has 101 864 at the 10 km mesh of the brief.
  - Every job reads a site model with soiltype 1 (Idini sI, rock) for the MASCSN26 interface set.
  - The coupling bar is measured against geodetic χ 0.8. The pooled and margin b rows are measured against the segmented row, the only geometry that has them.
  - The crustal tree runs in two parts (see open questions), mixed exactly.
  - The GM1 "top four" crustal set equals the current tree, so it has no job of its own.
- **Environment:** `oq` fails in `psha_renta` with `ModuleNotFoundError: openquake.calculators...`: the editable install does not map the new `openquake.pfd` subpackage. `run_all.sh` sets `PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine`; the entry scripts need the same to read datastores. Reinstalling the engine (`pip install -e`) would fix it for good.
- **Commands for Pablo** (all have run; to rerun):
  - `bash psha_chile8/hazard/run_all.sh`
  - then, with `PYTHONPATH` as above, from `psha_chile8/`: `python hazard/check_tree.py`, `python hazard/trees.py`, `python hazard/tornado_final.py`, `python hazard/tables.py`
- **Results** (PGA 475 yr; reference branches combined):
  - Interface + in-slab: 1.29 g La Serena, 1.27 Valparaíso, 1.24 Antofagasta, 0.73 Santiago centro, 0.13 Puerto Aysén.
  - The crustal family doubles the south: Hornopirén 0.33 → 0.60 g, Puerto Aysén 0.13 → 0.50 g.
  - Tornado on the interface + in-slab number, ≥ 5 %: the GMM sets and single GMMs (20–27 %), interface segmentation 20 %, geodetic rate 14 %, b option 13 %, in-slab nearest-neighbour pattern 12 %, declustered interface rate 12 %, interface (a, b) 10 %, scaling 10 %, in-slab (a, b) 8 %, coupling 6 %.
  - Below 5 %: truncation 2.5 / 4.0 (≤ 4.5 %) and the interface MFD shape (cut against tapered, 0.6 %).
  - Crustal, on the total: MASCSN26 GMM set 91 % (Pucón), no faults −71 % and database B +64 % (Puerto Aysén), jump 5 km 25 %, depth 20 km 24 %, segmented system 23 %, ψ 17 %. Below 5 %: background declustered rates, pattern declustering, cut MFD, truncation.
- **Open questions:**
  - **Crustal section ids (for S3):** the crustal tree failed as one job, because OpenQuake needs section ids unique across the sections files of a job, and `cr_sections_A_z10.xml` and `cr_sections_A_z20.xml` share them (`s_CL-006a_0` …). The tree ran as `f_cr_tree_a` (78 branches, weight 0.75) and `f_cr_tree_b` (6 multi-fault depth-20 branches, 0.25), mixed exactly in `trees.load`. Proposal for S3: depth in the section ids, so that the tree runs as one job.
  - **MASCSN26 crustal set** (Arteta et al. 2023 alone): crustal PGA 475 × 5–6 at Concepción (0.14 → 0.72 g) and Puerto Montt (0.11 → 0.70 g). Worth a check of the model's applicability and distance metric before it is shown.
  - C15 rows (in-slab one layer, lower depth) defined and skipped.
- **Proposed DECISIONS lines (Hazard runs):**
  - "Hazard jobs in `hazard/` (S5a, 16 Nov): one OpenQuake job per family, combined exactly in rate space (check_tree level 1 passes); the interface scaling level as setMSRAbsolute applied to Subduction Interface only; in-slab from `model/inslab/nrml/2026-11-16b/`."
  - "`strict = false` in the hazard jobs: the margin complex fault has 101 864 ruptures at the 10 km mesh, above OpenQuake's 52 000 guard (S5a, 16 Nov)."
  - "Site model with soiltype 1 (Idini et al. 2017 class sI, rock) at every site, for the MASCSN26 GMM set (S5a, 16 Nov)."
- **Proposed DECISIONS lines (Logic tree, for Pablo to judge by the 5 % rule):**
  - "Tornado of 16 Nov (S5a / S5b, PGA 475 yr, 14 cities): below 5 % everywhere: truncation 2.5 / 4.0, interface MFD shape cut against tapered (0.6 %), crustal background from declustered fits, crustal pattern declustering, crustal cut MFD."
- **Suggested commit:**
  - `git add psha_chile8/hazard/*.py psha_chile8/hazard/run_all.sh psha_chile8/hazard/tests psha_chile8/hazard/REPORT_S5a.md psha_chile8/hazard/branches_*.csv psha_chile8/hazard/out psha_chile8/hazard/jobs/*/build.json psha_chile8/hazard/jobs/*/job.ini psha_chile8/hazard/jobs/*/*_lt.xml psha_chile8/PLAN.md psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`
  - The job folders' `src/` hold hard links to the model NRML files (442 MB): leave them untracked.
  - Message: "S5a/S5b: hazard jobs ported from psha_chile7; interface, in-slab and crustal references, family trees, tornado rows; check_tree level 1 passes; tornado and tree post-processing"
- **Decided by Pablo (16 Nov): crustal fault-system weights 0.5 / 0.5** (segmented / multi-fault). The open point above is closed. Proposed DECISIONS line: "Crustal fault-system branches segmented 0.5, multi-fault 0.5 (Pablo, 16 Nov)."

## 2026-11-16 — S5a: tornado figures for the 17 Nov slides (Claude Code, same session)
- **Asked by Pablo:**
  - one tornado figure per city for the collaborator slides: vertical bars ordered by the change of the total, small axes left out, single results labelled;
  - GMM rows regrouped as one axis per set;
  - stored as preliminary, since more branch levels will be added.
- **Code:** `hazard/tornado_prelim.py` writes `hazard/out/tornado_prelim/<city>.png` and `.csv`, 14 cities.
  - **Axes:** those that move the total PGA 475 yr by ≥ 1 %, up to 18, ordered by the change. Thick bar = change of the total, pale bar = family alone, dots = rows, labels with leader lines on the 10 largest.
  - **GMM axes:** one per set and family (GMM-1R, GMM-FIT, GMM-MASCSN, GMM-GEM; crustal GMM-FIT = GMM-1R, no axis). Each single model's curve comes from the realizations of the set job, no new OpenQuake runs; checked against the single-GMM jobs of GMM-1R, identical. The set as a whole is drawn as a diamond.
  - **Below the lowest level:** a row whose total falls below 0.005 g is drawn at that bound and labelled (Puerto Williams without faults).
- **Names** (`hazard/jobs.py`; labels only, jobs unchanged):
  - GMM sets: GMM-1R (the current tree, NGA-Sub + Montalva, round 1), GMM-FIT (GM1 top four), GMM-MASCSN, GMM-GEM.
  - Axis "GMM-1R models": the four GMMs of GMM-1R, each alone.
- **Other figures from the session:**
  - `hazard/gmm_sets.py` (PGA 475 per set and family, six cities);
  - `hazard/shares.py` (family shares of the hazard at the total PGA 475, and the family-alone against total scatter);
  - `hazard/tornado_alt.py` and `hazard/tornado_trial.py` (layout trials).
- **Suggested commit:** add `psha_chile8/hazard/{tornado_prelim,tornado_trial,tornado_alt,gmm_sets,shares}.py psha_chile8/hazard/jobs.py psha_chile8/hazard/out psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`; message "S5: preliminary tornado figures per city with GMM sets as axes; GMM set names GMM-1R / FIT / MASCSN / GEM"

## 2026-11-16 — S5: tornado figure style frozen; review against the psha_chile6 tornado (Claude Code, same session)
- **Style:** written down in `hazard/FIGURE_STYLE_tornado.md`: layout, labels, fonts, and the trials that failed. `hazard/tornado_prelim.py` is the template.
  - Legend: "all tectonic settings" / "within tectonic setting".
  - The reference branch is drawn and labelled at 0; a hollow diamond marks the equal-weight average of each axis.
  - GMM axes: one per set (GMM-1R / FIT / CSN / GEM).
- **Compared with the psha_chile6 tornado** (`psha_chile6/outputs/hazard/rock800_tornado/_tornado/summary.txt`; 14 cities, PGA 475):
  - **Reference PGA:** lower now in the north and centre (Iquique 1.11 → 1.03 g, Calama 0.82 → 0.68, Copiapó 1.03 → 0.88, Concepción 1.24 → 1.12); the same in the south (Pucón 0.51 / 0.48, Puerto Aysén 0.50 / 0.50).
  - **Geodetic rate:** 1.2 % then, 13 % now (geodetic against seismic). The new seismic fits put the seismic branch further from the moment balance.
  - **Truncation 2.5 / 4.0:** 8.7 % then, ≤ 4.5 % now.
- **psha_chile6 rows ≥ 5 % that are not in the new tornado:**
  - fit floors ±0.2: interface 11 %, in-slab 14 %. DECISIONS fixes them by criteria, but the branch rule asks for the range to be stated, so they should be run once and reported.
  - crustal fault Mmax (single vs tree, 35 %) and "fault and cap Mmin 6.5" (15 %). Leonard alone now; the class-maximum variant was dropped with the multi-fault branch.
  - crustal fault MFD shape (18 %).
  - in-slab Mmax pad 0 / 0.4 (7.7 %) and interface segment Mmax +0.2 (5.2 %): fixed by the + 0.2 rule; range to be stated.
  - interface corner 9.1 / 10.1 (6.4 %): replaced by the Kagan rule.
- **psha_chile6 rows below 5 %, fixed and stated** (not needed again unless the geometry changes): Z_TOP 5 (4.5 %), Z_BOTTOM 60 (4.8 %), aspect ratio 2 (3.7 %), completeness ±0.1 (≤ 3.6 %), kernel neighbours, class domain cut, the crustal background details (≤ 0.6 %).
- **Can be read or run now with no model change:**
  - crustal fault MFD shape, each of the six alone: in the realizations of `t_cr_segmented` (6 branches), no new job;
  - in-slab MFD shape (tapered against truncated): S2 files exist (`gk_trunc_ml_l3`), one job of about 2 min.
- **Needs new files from other sessions:**
  - S2: in-slab declustered rates (DECISIONS: rates from the full catalogue, so only if Pablo wants it tested); C15 one layer and lower depth.
  - S3: section ids per depth (the crustal tree as one job); fault Mmax alternatives; fault Mmin 6.5.
  - S1: Antarctic source on / off (matters for Puerto Aysén and Williams); fit floor ±0.2 fits (B11).
- **Open from this session:**
  - GMM-CSN crustal (Arteta 2023 alone) raises crustal PGA 5 × at Concepción and Puerto Montt: check its applicability before showing it as a set.
  - Logic-tree weights instead of equal weights for the averages.
  - Interface jobs are serial-bound (about 5 min each). If many more interface rows are added, a hazard Mmin of 6.0 or a 15 km mesh would cut that; both need a DECISIONS change.
  - Reinstall the oq-engine checkout editable (`openquake.pfd` is missing from the editable map).
- **Proposed LEARNINGS lines (Sensitivity and tornado):**
  - "A tornado figure reads best as vertical bars with the change of the total, the family-alone range pale behind it, every branch labelled and the reference drawn at 0; brackets read as error bars (`hazard/FIGURE_STYLE_tornado.md`, 16 Nov)."
  - "Single-GMM results need no jobs of their own: each model's curve is in the realizations of the set job (identical to the single-GMM jobs, S5a)."

## 2026-11-16 — S5: Pablo's decisions on the review, and the reference PGA compared (Claude Code, same session)
- **Reference PGA 475 yr, total of the three families, per city** (`hazard/out/ref_compare.csv`):

  | | Iquique | Calama | Antofagasta | Copiapó | La Serena | Valparaíso | Santiago c. | Concepción | Puerto Montt | Hornopirén | Puerto Aysén |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | psha_chile6 (GMM-1R) | 1.11 | 0.82 | 1.33 | 1.02 | 1.34 | 1.37 | 0.80 | 1.24 | 0.63 | 0.64 | 0.50 |
  | now, GMM-1R | 1.03 | 0.68 | 1.24 | 0.88 | 1.29 | 1.28 | 0.74 | 1.12 | 0.53 | 0.60 | 0.50 |
  | now, GMM-FIT | 0.85 | 0.52 | 1.02 | 0.67 | 0.99 | 1.06 | 0.55 | 0.93 | 0.44 | 0.56 | 0.49 |

  - **Source model** (now against psha_chile6, both on GMM-1R): −4 to −17 %.
  - **GMMs** (GMM-FIT against GMM-1R): a further −16 to −25 % from Iquique to Concepción, −2 to −9 % in the far south.
  - **Together:** −23 to −37 % in the north and centre, −1 to −16 % in the south.
- **Geodetic branch:** the moment balance is unchanged (χ, 6.6 cm/yr, areas), so its moment rate is the same as before. The shape of its MFD changed with b and with the Mmax and corner rules of 15 Nov (Mmax = segment maximum + 0.2, corner from Kagan; before, no pad and corner 9.6). The jump of the geodetic axis, 1.2 % then and 13 % now, therefore comes mainly from the seismic branch and the MFD shape, not from the geodetic moment. To confirm with the S1 tables (N(≥ 8) seismic against geodetic, psha_chile6 against now).
- **Decided by Pablo (16 Nov):**
  - **Fit floors:** not tested; the fits are built to be stable against the floor (B9, B11).
  - **Fault Mmax:** not tested separately; it follows from the Mmax fit.
  - **Crustal fault MFD shapes:** already in the runs (the single-fault row mixes the six shapes); most will be dropped, since they barely move the hazard.
  - **Antarctic interface source:** always on, not a tornado factor.
  - **Averages in the tornado figures:** equal weights for now; logic-tree weights much later.
  - **To be tested, for completeness:** C15 one layer and lower depth; in-slab declustered rates (S2 has to build the files).
  - **GMM-CSN crustal (Arteta et al. 2023 alone):** needs a check; it gives a lot of PGA on its own.
- **Open:** Mmax pad (in-slab 0 / 0.4, interface segment + 0.2). psha_chile6 gave 5–8 %. The + 0.2 is fixed by a rule, but the branch rule asks for its range to be stated: one row per family would give that range. Pablo to decide.
- **Crustal questions for S3** (Pablo, 16 Nov; message passed on):
  - multi-fault ruptures for Magallanes–Fagnano and for arc segments;
  - whether the Liquiñe–Ofqui multi-fault branch touches only the intra-arc faults, or also intra-arc faults in the north;
  - whether background and fault seismicity are compared correctly, and what the joint background + fault MFD is;
  - possible jumps in databases A (GEM) and B (MASCSN), including jumps from main traces to favourably oriented secondary traces;
  - fault depths: most source values are not reliable; check CSN / CHAF for a depth source; section ids should carry the depth;
  - Mmax alternatives (none chosen yet).
- **Proposed DECISIONS lines:**
  - Interface: "The Antarctic interface source is always on; not a tornado factor (Pablo, 16 Nov)."
  - Logic tree: "Fit floors are not a tornado factor: the fits are built stable against the floor (B9, B11; Pablo, 16 Nov)."
  - Logic tree: "Tornado figures show the equal-weight average of each axis; logic-tree weights come later (Pablo, 16 Nov)."

## 2026-11-16 — S5: decisions confirmed by Pablo; REPORT_S5a section 9 (Claude Code, same session)
- **Confirmed by Pablo (to be written into DECISIONS by him):**
  - Hazard runs: "`strict = false` in the hazard jobs (the margin complex fault has 101 864 ruptures at the 10 km mesh)."
  - Interface: "The Antarctic interface source is always on; not a tornado factor."
  - Logic tree: "Fit floors are not a tornado factor: the fits are built stable against the floor (B9, B11)."
  - Figures: "Tornado figures show the equal-weight average of each level; logic-tree weights come later."
  - GMMs: "GMM sets named GMM-1R (current tree, round 1), GMM-FIT (GM1 top four), GMM-CSN (MASCSN26), GMM-GEM (GEM South America)."
- **New level:** Mmax pad 0 / 0.2 / 0.4 for interface (segments and margin) and in-slab. Pablo sends the rows to S1 and S2; the S1 prompt's point 2 is no longer conditional, and the S2 prompt gets the same line.
- **Every branch keeps source Mmin 5.5**, so the levels stay comparable (Pablo).
- **Left for the full model:** the ≥ 5 % verdicts, logic-tree weights, faster interface jobs.
- **Report:** `hazard/REPORT_S5a.md`.
  - Section 5: tables regenerated with the new names.
  - Section 9: the preliminary figures, the PGA comparison per city (psha_chile6 / GMM-1R / GMM-FIT), the decisions, how to add a level.

## 2026-11-16 — C15: in-slab depth tables ready (run 2026-11-16b)

- **Scope** (Pablo, 16 Nov): this session builds the depth cell tables only; S2 builds the source files and the rupture-geometry options; S5 runs the hazard. The S5 addendum about `nrml/<date>/` therefore goes to S2. The brief has a scope note.
- **Done:** `model/inslab/options.py`, `REPORT_C15.md`, 4 new tests (23 pass). DECISIONS re-read at the start and end; the In-slab line on the one layer is what changes (proposal below).
- **One layer:** h_one = top + 0.252 × Slab2 thickness. 0.252 is the fraction that holds half of the 70 804 depth-model events. It replaces the per-cell median of C14, which jumped about 10 km along the 50 km slab-top line (the ± 15 km interface band of A7). New − C14: median +0.7 km, 5–95 % −7.7 to +14 km. The fraction varies with latitude (0.15–0.17 at 32–36° S, 0.29–0.31 at 20–22 and 26–32° S, 0.04–0.11 south of 38° S): one value is a smoothing choice. Table `depth_cells_2026-11-16b.csv`; the three slices and the lower depth are unchanged from `2026-11-16`.
- **Lower-depth options**, reference hypocentres kept: 0.65 (psha_chile7; lsd +13.0 km median) and 0.615 (95 % with all depth sources; +10.4 km), in `depth_cells_lsd065_` and `depth_cells_lsd0615_2026-11-16b.csv`.
- **w1 over the shallow slab** (top ≤ 50 km, 4 901 cells): the top slice (11.4 km) lies inside the ± 15 km interface band in every cell. From the shallow-slab events alone w1 = 0.02. The 0.39 in the table comes from the kernel carrying the events under the deeper slab updip. No change proposed.
- **For S2** (new session or the S2 conversation): build `l1` from `depth_cells_2026-11-16b.csv`, and the lower-depth branches from the two `lsd` tables, as weight-0 branches in a new `nrml/<date>/` per the S5 addendum (reference `gk_taper_ml_l3` byte-identical to `2026-11-16b`). Also the rupture-geometry options (S2 already uses StrasserIntraslab; the OpenQuake alternative is AllenHayesIntraslab), the one-city check and the "negligible" threshold.
- **Proposed lines** (Pablo adds): see `REPORT_C15.md` section 5. DECISIONS In-slab, one layer → "top + 0.252 × the Slab2 thickness, the fraction holding half of the events of the depth model (C15, 16 Nov)". Lower-depth options 0.65 and 0.615 with the reference hypocentres. Superseded: per-cell median → 0.252 rule. LEARNINGS: per-cell in-slab depth statistics jump at the 50 km slab-top line because of the interface band.
- **Commands:** from `psha_chile8/model/inslab/`: `python options.py` (2 min).
- **Suggested commit:** `git add psha_chile8/model/inslab/options.py psha_chile8/model/inslab/REPORT_C15.md psha_chile8/model/inslab/tests/test_depth.py psha_chile8/model/inslab/tables/{depth_cells,depth_cells_lsd065,depth_cells_lsd0615,onelayer,options,w1_check}_2026-11-16b.csv psha_chile8/model/inslab/figs/2026-11-16b/{maps_onelayer,sections_layers}.png psha_chile8/model/inslab/figs.py psha_chile8/tasks/C15_inslab_depth_options.md psha_chile8/DATA.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `C15: in-slab depth options (one layer at top + 0.252 x thickness, lower depth 0.65 and 0.615)`.
- **Added:** `figs/2026-11-16b/sections_layers.png` (REPORT_C15 section 6). At 33° and 38° S the three-layer weights also switch at the 50 km slab-top line (bottom slice heavier updip, top slice downdip): the interface-band effect shows in the three layers too, not only in the one layer. Open for Pablo.

## 2026-11-16: S1: interface Mmax pad files ready (2026-11-16b) (Claude Code)
For S5 (note of 16 Nov). Details in `model/interface/REPORT_S1.md` section 7. DECISIONS re-read (Interface, Statistics, Logic tree): unchanged since the A9 rerun; the choices hold.
- **Files:** `model/interface/nrml_2026-11-16b/`. It holds every file of `nrml_2026-11-16` with the same sha256, `source_lt_interface.xml` copied unchanged, and four new files `if_{margin,seg}_full_own_taper_ml_seis_pad{00,04}.xml`.
- **branches.json:** factor `mmax_pad` on every branch (0.2 for the old ones, weight 0 for the new ones), and a `tornado` block with rows `mmax_pad00` / `mmax_pad02` (reference) / `mmax_pad04`. Each row holds margin and segmented at 0.5 / 0.5.
- **Code:** `if_pad.py`; `if_oqcheck.compare` takes a rates table; test `test_mmax_pad_files`. Interface tests: 11 pass.
- **Mmax and fits:** Mmax = largest historical event + 0 / 0.2 / 0.4 (9.5 / 9.7 / 9.9 on the margin). Each unit is refitted with that Mmax (no bootstrap, ML pair), and the corner comes from Kagan on it. The pad-0.2 refit rebuilds the reference files byte for byte.
- **Antarctic source:** its 8.5 comes from the area, not from an event; it is shifted by the same steps (8.3 / 8.5 / 8.7).
- **What the pad moves:** N(≥ 8.5) at 32–26° S by −58 / +53 %, N(≥ 8) by ≤ 12 %, b by ≤ 0.011.
- **OpenQuake check:** calc 592, preclassical. The four new files load, rates equal the table (|dN8| ≤ 1.1e-6), last magnitudes equal.
- **Geodetic lever (check, no files):**
  - At χ 0.8, geodetic / seismic N(≥ 8) went from 0.97 to 1.32 on the margin, and from 1.0–2.5 to 1.6–4.8 on the segments (table in REPORT section 7).
  - The geodetic moment is the same. The seismic moment of the margin fell from 7.1e20 to 5.3e20.
  - Margin, step by step: b 0.917 → 0.959 gives −25 %; N(≥ 5.5) 10.4 → 8.4 gives −20 %; the Kagan corner with the list to Mmax + 0.2 gives +23 %.
  - So the change comes from the seismic fits (b and rates). The Mmax / corner rules of 15 Nov reduce the lever, they don't raise it.
  - The psha_chile6 tornado also varied the geodetic level on the full margin only.
- **Note for Pablo:** in `fits/run.py`, the weight-1 observed maximum is 9.0 at 37–32° S and 8.9 at 26–17.6° S. The interface Mmax there are fixed at 9.3 and 9.0, i.e. 9.1 and 8.8 + 0.2, from the historical list. So the pads here are on the historical maxima, not on `observed()`. Not changed.
- **Proposed DECISIONS lines:**
  - Interface: "Mmax pad level for the tornado: + 0 / + 0.2 / + 0.4 on the largest historical event of each unit (Antarctic 8.5 shifted alike), units refitted, Kagan corner on each Mmax; files `model/interface/nrml_2026-11-16b/` (S1, 16 Nov). The reference stays + 0.2 until the tornado."
  - Logic tree: "The geodetic-rate lever grew from psha_chile6 (geodetic / seismic N(≥ 8) 0.97 → 1.32 on the margin) because the seismic fits give less moment (higher b, lower rates), not because of the Mmax / corner rules (S1, 16 Nov)."
- **Suggested commit:** `git add psha_chile8/model/interface/if_pad.py psha_chile8/model/interface/if_oqcheck.py psha_chile8/model/interface/tests/test_interface.py psha_chile8/model/interface/REPORT_S1.md psha_chile8/model/interface/nrml_2026-11-16b psha_chile8/model/interface/oqcheck_2026-11-16b psha_chile8/model/interface/tables/rates_2026-11-16b_pad.csv psha_chile8/model/interface/tables/oqcheck_2026-11-16b_pad.csv psha_chile8/WORKLOG.md`; message "S1: interface Mmax pad files for the tornado (nrml_2026-11-16b); geodetic lever check against psha_chile6".

## 2026-11-16: interface Mmax by the one rule, run 2026-11-16f (Claude Code, B11/B12)

Asked by Pablo. DECISIONS read again before and after: Statistics already says one rule for every unit, interface included; Interface still lists 9.7 / 9.3 / 8.7 / 9.0 (line to replace, proposed below, not written).

- **Rule** (Pablo, 16 Nov): the interface units take their Mmax like every other unit, the largest weight-1 event of the unit in the catalogue + 0.2. `fits/run.py`: the fixed list (9.7 / 9.7 / 9.3 / 8.7 / 9.0) is gone, the five interface units have `pad=0.2`; the controlling magnitude of the (a, b) branches now reads the Mmax of the fit (8.8, at most Mmax − 0.3). Nothing else changed; catalogue `2026-11-16c`, declustered catalogues `2026-11-16e`, completeness table and every Mc window identical.
- **Largest events** (all with class weight 1, from Ruiz and Madariaga 2018): margin and 45.6–37° S 1960-05-22 Mw 9.5; 37–32° S 1730-07-08 Mw 9.0 (1751-05-25 also 9.0); 32–26° S 1819-04-11 and 1922-11-11 Mw 8.5; 26–17.6° S 1877-05-10 Mw 8.9. The fixed list had 9.1 for 37–32° S and 8.8 for 26–17.6° S. Arica 1868-08-13 Mw 9.0 has its epicentre at 17.15° S, north of the last segment: it counts in the margin unit and in no segment.

| unit | Mmax, 16e → 16f | corner | b (sd) | N(≥ 7) | N(≥ 8) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|
| interface, tapered | 9.7 | 9.48 | 0.959 (0.018) | 0.3046 | 0.0333 | 55.7 / 51.6 | 17.5 / 15.8 |
| interface, cut | 9.7 | – | 0.959 (0.018) | 0.3046 | 0.0330 | 55.5 / 51.6 | 17.4 / 15.8 |
| 45.6–37° S, tapered | 9.7 | 9.47 | 0.909 (0.049) | 0.0449 | 0.0055 | 8.5 / 9.9 | 2.9 / 2.8 |
| 45.6–37° S, cut | 9.7 | – | 0.909 (0.049) | 0.0448 | 0.0054 | 8.4 / 9.9 | 2.8 / 2.8 |
| 37–32° S, tapered | 9.3 → 9.2 | 9.09 → 8.99 | 0.9932 → 0.9926 (0.033) | 0.0875 → 0.0878 (+0.3 %) | 0.00873 → 0.00870 (−0.3 %) | 15.6 / 12.6 | 4.6 / 5.5 |
| 37–32° S, cut | 9.3 → 9.2 | – | 0.9934 → 0.9928 (0.033) | 0.0872 → 0.0873 (+0.2 %) | 0.00852 → 0.00846 (−0.7 %) | 15.5 / 12.6 | 4.5 / 5.5 |
| 32–26° S, tapered | 8.7 | 8.48 | 0.939 (0.030) | 0.0974 | 0.0096 | **17.4 / 9.9** | 5.0 / 2.6 |
| 32–26° S, cut | 8.7 | – | 0.937 (0.031) | 0.0970 | 0.0094 | **17.3 / 9.9** | 5.0 / 2.6 |
| 26–17.6° S, tapered | 9.0 → 9.1 | 8.79 → 8.89 | 0.9624 → 0.9633 (0.039) | 0.0679 → 0.0676 (−0.4 %) | 0.00701 → 0.00708 (+1.0 %) | 12.2 / 15.3 | 3.7 / 2.9 |
| 26–17.6° S, cut | 9.0 → 9.1 | – | 0.9611 → 0.9621 (0.039) | 0.0678 → 0.0676 (−0.3 %) | 0.00683 → 0.00691 (+1.2 %) | 12.2 / 15.3 | 3.6 / 2.9 |

- Rows without an arrow are identical to 16e in every column. N(≥ 5) and N(≥ 6) of the two changed segments within 0.2 %. Large-event checks unchanged (32–26° S still outside the band at Mw ≥ 7).
- **Branches:** the controlling magnitude of 26–17.6° S goes from 8.7 to 8.8 (Mmax − 0.3 no longer below 8.8); its pairs (a, b) 5.836, 1.026 / 5.525, 0.963 / 5.215, 0.900 (5th / ML / 95th). 37–32° S: 6.105, 1.046 / 5.842, 0.993 / 5.578, 0.939. The other units unchanged.
- **Check that nothing else moved.** `fits_2026-11-16f.csv` against `fits_2026-11-16e.csv`, column by column: only the four rows of `seg2` and `seg4` differ; `interface`, `seg1`, `seg3`, the three in-slab units, the four crustal classes and `crustal` are identical. `fits_declustered_2026-11-16f.csv` (374 rows): 132 rows differ, all interface segments: the 88 rows of `seg2` and `seg4`, and the 44 rows of `seg1` and `seg3` with the shared segment b (`b_option` shared), whose family b moves in the fourth decimal (Gardner–Knopoff per family 0.7527 → 0.7530) because it pools the four segments. No row of another unit differs. In the sensitivity table the rows of `seg2` and `seg4` differ, and the pooled-b rows of `seg1` and `seg3`.
- **Declustered, the two options** (tapered, table full, own b): 37–32° S corner 8.98 → 8.88 (Gardner–Knopoff per family) and 9.06 → 8.96 (nearest neighbour per family), N(≥ 7) +0.8 % and +0.5 %, N(≥ 8) unchanged; 26–17.6° S corner 8.75 → 8.85 and 8.78 → 8.88, N(≥ 7) −0.7 % and −0.5 %, N(≥ 8) +0.8 % and +0.9 %.
- **Downstream (S1):** `seg2` and `seg4` meet the threshold of 0.1 in Mmax, in the full and the declustered table; b and N(≥ 6) are far under the others. `model/interface/if_build.py` reads `fits_2026-11-16.csv` and `fits_declustered_2026-11-16.csv`; its other interface rows are the same in 16f. S2 and S3: no row moves (S3 can read 16e or 16f).
- **Files.** New: the nine `*_2026-11-16f.csv` tables in `fits/tables/`. Nothing older overwritten; the 16e figures copied to `fits/figs/2026-11-16e/`, then `fits/figs/*.png` regenerated. 31 tests pass. `fits/FITS.md` section 13, `fits/DECLUSTER.md` section 11, DATA row.
- **Proposed lines for DECISIONS** (Pablo adds; not written):
  - Interface, replacing the Mmax line: "Mmax: largest weight-1 event of each unit in the catalogue + 0.2, by `observed()` of `fits/run.py` like every other unit, no fixed list: 9.7 for the whole margin and 45.6–37° S (1960, Mw 9.5), 9.2 for 37–32° S (1730 and 1751, Mw 9.0), 8.7 for 32–26° S (1819 and 1922, Mw 8.5), 9.1 for 26–17.6° S (1877, Mw 8.9) on the catalogue `2026-11-16c` (Pablo, 16 Nov). Arica 1868 Mw 9.0 (17.15° S) is north of the last segment and counts in the margin only. Moment closure only as a diagnostic."
  - Statistics: "Fits, current: `fits/tables/fits_2026-11-16f.csv` and `fits_declustered_2026-11-16f.csv`; they differ from 16e only in the interface segments 37–32° S and 26–17.6° S."
  - Superseded: "Interface Mmax from a fixed list, 9.7 / 9.3 / 8.7 / 9.0 (15 Nov; the Ruiz and Madariaga values 9.1 and 8.8 + 0.2) → from the catalogue like every unit, 9.7 / 9.2 / 8.7 / 9.1 (16 Nov). Fits `fits_2026-11-16e.csv` → `fits_2026-11-16f.csv`."
- **Open:** Arica 1868 belongs to no segment by its epicentre; if the segmented branch should carry it, the northern limit of the last segment (17.6° S) is the thing to look at, in S1.
- **Commands** (from `psha_chile8/fits/`): `python run.py` (95 s), `OMP_NUM_THREADS=1 python run_declustered.py` (3 min); `pytest fits/tests` from `psha_chile8/`.
- **Commit** (from the repo root):
  - `git add psha_chile8/fits/run.py psha_chile8/fits/run_declustered.py psha_chile8/fits/FITS.md psha_chile8/fits/DECLUSTER.md psha_chile8/fits/figs psha_chile8/fits/tables/*_2026-11-16f.csv psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  - `git commit -m "Fits 2026-11-16f: interface Mmax from the catalogue like every unit (37-32 S 9.2, 26-17.6 S 9.1)"`

## 2026-11-16: Mmax pad 0.0 and 0.4, tornado sensitivity on run 2026-11-16f (Claude Code, B11/B12)

Asked by Pablo. DECISIONS read again before and after (Statistics: pad 0.2, one rule for every unit; In-slab: "Mmax pad 0 / 0.2 / 0.4: 5–7 %; fixed at 0.2" in LEARNINGS); nothing here changes a rule.

- **What.** `fits/run_pad.py` (new; settings at the top): the fits of `run.py` with another pad on the largest weight-1 event for every unit, the corner of the tapered line following from Mmax by the Kagan rule; same catalogue (`2026-11-16c`), tables and rules as `fits_2026-11-16f.csv`. Maximum-likelihood rows only: no bootstrap, no (a, b) percentiles, no declustered tables. With pad 0.2 the script reproduces `fits_2026-11-16f.csv` to the rounding of that file (same Mmax; b within 0.00001; N(≥ 7) within 0.2 %, the five decimals of the CSV on the smallest rates), so the differences below are the pad alone.
- **Files:** `fits/tables/fits_2026-11-16f_pad00.csv`, `fits_2026-11-16f_pad04.csv` (26 rows each: 13 units, two shapes; columns unit, name, shape, pad, events, counted, mmax, corner, b, b_from, a, rate_mlo, m_lo, steps, N5–N8, the large-event check) and `fits_2026-11-16f_pad_compare.csv` (differences against 16f).
- **Tapered fits against 16f** (pad 0.2); Δb, and N as a ratio to 16f:

| unit | Mmax 0.0 / 0.2 / 0.4 | Δb, pad 0.0 | N(≥ 6) | N(≥ 7) | Δb, pad 0.4 | N(≥ 6) | N(≥ 7) |
|---|---|---|---|---|---|---|---|
| interface | 9.5 / 9.7 / 9.9 | −0.001 | × 1.001 | × 1.003 | 0.000 | × 1.000 | × 1.000 |
| interface, 45.6–37° S | 9.5 / 9.7 / 9.9 | −0.001 | × 1.002 | × 1.004 | 0.000 | × 0.999 | × 0.999 |
| interface, 37–32° S | 9.0 / 9.2 / 9.4 | −0.002 | × 1.004 | × 1.007 | +0.001 | × 0.997 | × 0.995 |
| interface, 32–26° S | 8.5 / 8.7 / 8.9 | −0.006 | × 1.015 | × 1.024 | +0.004 | × 0.991 | × 0.986 |
| interface, 26–17.6° S | 8.9 / 9.1 / 9.3 | −0.002 | × 1.005 | × 1.008 | +0.001 | × 0.997 | × 0.995 |
| in-slab, shallow | 8.0 / 8.2 / 8.4 | −0.008 | × 1.020 | × 1.016 | +0.006 | × 0.987 | × 0.985 |
| in-slab, intermediate depth | 8.0 / 8.2 / 8.4 | −0.008 | × 1.020 | × 1.016 | +0.006 | × 0.987 | × 0.985 |
| Jujuy nest | 7.2 / 7.4 / 7.6 | −0.014 | × 1.025 | × 0.76 | +0.011 | × 0.977 | × 1.12 |
| crustal family | 7.8 / 8.0 / 8.2 | −0.002 | × 1.003 | × 0.96 | +0.001 | × 0.998 | × 1.02 |
| forearc | 7.0 / 7.2 / 7.4 | −0.002 | × 0.980 | × 0.43 | +0.001 | × 1.010 | × 1.52 |
| arc | 7.7 / 7.9 / 8.1 | −0.002 | × 1.003 | × 0.94 | +0.001 | × 0.998 | × 1.03 |
| backarc | 7.5 / 7.7 / 7.9 | −0.002 | × 1.001 | × 0.87 | +0.001 | × 0.999 | × 1.07 |
| Patagonia | 7.8 / 8.0 / 8.2 | −0.002 | × 1.003 | × 0.96 | +0.001 | × 0.998 | × 1.02 |

- **Read:** b moves by 0.014 at most (Jujuy nest) and under 0.01 everywhere else, well inside every bootstrap sd; N(≥ 5) within 0.2 % and N(≥ 6) within 2.5 % in every unit. The pad matters only where N(≥ 7) sits next to Mmax: the forearc (Mmax 7.0 to 7.4: N(≥ 7) × 0.43 to × 1.52), the Jujuy nest (× 0.76 to × 1.12) and the backarc (× 0.87 to × 1.07). For the interface and the in-slab classes N(≥ 7) moves by under 2.5 %.
- **Above Mw 7:** N(≥ 8) of the in-slab classes × 0.50 with pad 0.0 and × 1.39 with pad 0.4 (tapered; × 0.44 and × 1.30 cut), since their Mmax is 8.0 to 8.4; interface 32–26° S × 0.89 and × 1.06; the other interface units within 2.5 %.
- **Cut-line fits** move the same way and a little less at N(≥ 7) (forearc × 0.42 and × 1.36; nest × 0.79 and × 1.09).
- **Large-event check:** the same result in all three pads for every unit (interface 32–26° S and intermediate in-slab outside the band at Mw ≥ 7, everything else inside).
- **Not done, as asked:** no declustered tables, no bootstrap, no (a, b) percentiles. `run.py`, the 16f tables and the figures are untouched; 31 tests pass.
- **For the tornado:** the source builders can read the two pad tables like `fits_2026-11-16f.csv` (same unit and shape keys; a in the convention of the shape; the row `crustal` is the family). They have no `b_sd`, covariance or branch columns.
- **Proposed line for DECISIONS** (Pablo adds; not written): Statistics or Logic tree: "Mmax pad is a tornado factor: 0.0 and 0.4 against 0.2 for every unit, corner by the Kagan rule (`fits/tables/fits_2026-11-16f_pad00.csv`, `_pad04.csv`; maximum-likelihood rows). It moves b by under 0.015 and N(≥ 6) by under 2.5 %; N(≥ 7) of the forearc by × 0.43 and × 1.52."
- **Commands** (from `psha_chile8/fits/`): `python run_pad.py` (about 15 s).
- **Commit** (from the repo root):
  - `git add psha_chile8/fits/run_pad.py psha_chile8/fits/FITS.md psha_chile8/fits/tables/fits_2026-11-16f_pad00.csv psha_chile8/fits/tables/fits_2026-11-16f_pad04.csv psha_chile8/fits/tables/fits_2026-11-16f_pad_compare.csv psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  - `git commit -m "Fits: Mmax pad 0.0 and 0.4 on run 2026-11-16f, tornado sensitivity (ML rows)"`

- **S3 queue (16 Nov, from the orchestrator via Pablo):** a crustal Mmax-pad tornado row, the reference branch rebuilt on `fits_2026-11-16f_pad00.csv` and `_pad04.csv` (segmented and multi-fault references), weight 0. Pablo: worth a tornado level. To be done after the S5-note items.

## 2026-11-16, S2: in-slab Mmax pad branches
- **Done:** pad 0.0 and 0.4 rows for the reference branch (tapered, ML (a, b), three hypocentres; Gardner–Knopoff and nearest neighbour), from `fits/tables/fits_2026-11-16f_pad00.csv` and `_pad04.csv` (corner as in those tables), one source per cell, weight 0 (tornado only). `build.py`: `PADS`, `PAD_BRANCH`, `fits(path)`; `branches()` adds the four rows with column `pad`. Files in `model/inslab/nrml/2026-11-16b/` (now 56 files, 28 branches). REPORT_S2 section 10.
- **For S5, branch ids** (in `nrml/2026-11-16b/branches.json`, column `pad`; files `is_slab_<id>.xml` and `is_nest_<id>.xml`): `gk_taper_ml_l3_pad00`, `nn_taper_ml_l3_pad00`, `gk_taper_ml_l3_pad04`, `nn_taper_ml_l3_pad04`. Their pad 0.2 counterparts are the reference branches `gk_taper_ml_l3` and `nn_taper_ml_l3`.
- **Effect:** in-slab N(≥ 8) × 0.50 / × 1.39, nest N(≥ 7) × 0.76 / × 1.12, N(≥ 7) of shallow and intermediate within 2 %.
- **Checks:** 25 tests pass; all 56 files read by the OpenQuake parser (393 036 sources; rates within 2e-7). `fits_2026-11-16f.csv` in-slab rows equal `fits_2026-11-16.csv`, so the other branches are unchanged.
- **Suggested commit** (with or after the 2026-11-16b commit): `git add psha_chile8/model/inslab/{build,oqcheck}.py psha_chile8/model/inslab/tests/test_s2.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/{drop_2026-11-16b,oqread_2026-11-16b}.csv psha_chile8/model/inslab/nrml/2026-11-16b/branches.json psha_chile8/WORKLOG.md`; message `S2: in-slab Mmax pad 0.0 and 0.4 branches for the reference branch (weight 0, tornado), read by OpenQuake`.

## 2026-11-16: S1: interface rebuilt on fits 2026-11-16f with the Mmax pad rows (nrml_2026-11-16c) (Claude Code)
Details in `model/interface/REPORT_S1.md` section 8. DECISIONS re-read: Statistics (16f, pad factor) and Interface (Mmax by `observed()`); the choices hold.
- **Folder for S5:** `model/interface/nrml_2026-11-16c/`. It holds 240 branch files, `source_lt_interface.xml`, the four pad files, and `branches.json` with factor `mmax_pad` on every branch and the `tornado` block. `nrml_2026-11-16` and `nrml_2026-11-16b` are kept. `nrml_2026-11-16b` is superseded: it was built on the old Mmax list.
- **Pad-row branch ids (weight 0):**
  - `margin_full_own_taper_ml_seis_pad00` and `_pad04`;
  - `seg_full_own_taper_ml_seis_pad00` and `_pad04`;
  - the reference ids, unchanged: `margin_full_own_taper_ml_seis` and `seg_full_own_taper_ml_seis`.
  - The tornado rows are `mmax_pad00`, `mmax_pad02` and `mmax_pad04`, each margin 0.5 / segmented 0.5. The scaling level of `source_lt_interface.xml` applies to all of them.
- **Pad rows:** taken from `fits/tables/fits_2026-11-16f_pad00.csv` and `_pad04.csv`. They match my own refit (`if_pad.check`) in all 15 rows: Mmax, b, rate and corner to the table rounding (`tables/pad_check_2026-11-16c.csv`). The Antarctic source uses 8.3 / 8.5 / 8.7.
- **What moved against nrml_2026-11-16:**
  - Only 37–32° S (Mmax 9.3 → 9.2) and 26–17.6° S (9.0 → 9.1) change, plus the Antarctic source in the shared-b branches in the fourth decimal.
  - Reference tree: N(≥ 8) +7.8 % and −9.1 %. The moves are in the geodetic branches; the seismic ML branch moves by ≤ 1 %.
  - The margin, 45.6–37° S and 32–26° S are identical.
- **OpenQuake check (preclassical):** calcs 594 (margin), 595 (segments) and 593 (pad files). All 244 files load; |dN8| ≤ 2.1e-6; last magnitudes equal.
- **Code:** `if_build.py` (DATE 2026-11-16c, fits 16f); `if_pad.py` reads the pad rows of the fits session and checks them; `if_oqcheck.py` leaves the pad branches to the pad job; `if_figs.py` table 16f. Interface tests: 11 pass. `figs/` redrawn.
- **Open:** Arica 1868 (Mw 9.0, 17.15° S) lies north of the margin source, which ends at 17.6° S. It counts only in the margin fit. Left as it is.
- **Proposed DECISIONS lines:**
  - Interface sources: "`model/interface/nrml_2026-11-16c/branches.json` on fits 2026-11-16f, with the Mmax pad branches (weight 0) and the tornado block."
  - Superseded: "Interface sources `nrml_2026-11-16/` (A9 fits, fixed Mmax list) and the pad files `nrml_2026-11-16b/` → `nrml_2026-11-16c/` on fits 16f (16 Nov): only 37–32° S and 26–17.6° S move, N(≥ 8) of the tree +7.8 / −9.1 %."
- **Suggested commit:** `git add -A psha_chile8/model/interface psha_chile8/WORKLOG.md`; message "S1: interface rebuilt on fits 2026-11-16f with the Mmax pad branches (nrml_2026-11-16c)".

## 2026-11-16 — C14/C15 depth run 2026-11-16c

- **Catalogue:** `depth.CAT` → `catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv` (DECISIONS: everything reads 16c). The 16b run had still read 2026-11-16.
- **Fixes:**
  - `depth.nest` now scales the longitude by cos(lat) like `classify.py`: 15 Riedel-Hornig Jujuy-nest events had stayed in the depth set.
  - `depth.zone` splits the 1 km bins at the slice limits (cumulative histogram, interpolated): weights no longer jump when the lower depth moves slightly.
- **Effect against 2026-11-16:** fraction 0.4746 → 0.4744; weights 16–84 % ± 0.02, max 0.08; hypocentres ± 0.2 km, max 4.7; held-out −0.794 → −0.791. One-layer fraction 0.252.
- **Tables:** `depth_cells_2026-11-16c.csv` is now the file for S2: three layers, plus the C15 one layer in `h_one`. Also `depth_cells_lsd065_` and `depth_cells_lsd0615_2026-11-16c.csv`. Runs 2026-11-16 and 16b are kept.
- **Tests:** 25 pass.
- **95 % or 99 % (Pablo's question):**
  - 99 % gives 0.713, driven by the catalogue tails (0.883 against 0.553 in Riedel-Hornig).
  - 0.475 contains 17 of the 18 in-slab events of Mw ≥ 6.9 since 1964 shallower than 300 km; the one outside is 1971-05-08 at 42.3° S, 157 km. 0.65 contains all 18.
  - Chillán 1939 needs 0.62.
  - Proposed: 95 % stays the reference, and 0.65 is the tornado option.
- **Sections:** `figs/2026-11-16c/sections_layers_south.png` (31–40° S): the three-layer weights switch at the 50 km slab-top line. Open for Pablo.
- **Commands:** from `psha_chile8/model/inslab/`: `python run.py` (12 min), then `python options.py` (2 min).
- **Suggested commit** (replaces the C15 one above): `git add psha_chile8/model/inslab/{depth,run,options,figs}.py psha_chile8/model/inslab/REPORT_C15.md psha_chile8/model/inslab/tests/test_depth.py psha_chile8/model/inslab/tables/*_2026-11-16b.csv psha_chile8/model/inslab/tables/*_2026-11-16c.csv psha_chile8/model/inslab/figs/2026-11-16b psha_chile8/model/inslab/figs/2026-11-16c psha_chile8/tasks/C15_inslab_depth_options.md psha_chile8/DATA.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `C14/C15: depth run 2026-11-16c on catalogue 16c (nest test as classify.py, slices split inside bins); one layer at top + 0.252 x thickness; lower-depth options 0.65 and 0.615`.
- **S3 → S5 (16 Nov): section ids fixed.**
  - The ids now carry database and depth (`s_<db>_z<depth>_<fid>_<segment>`). They are unique across the four sections files (550 ids).
  - The 11 multi-fault files and their sections were rewritten in place under the same names. Rates unchanged (within 3.3e-6).
  - Calc 596 ran the two depth branches (A, ψ 0.8, 10 and 20 km) in one job.
  - S5 can run the crustal tree as one job again. Recopy the multi-fault and sections files into the job folders: the old copies still hold the clashing ids.
  - Test added (21 passed).

## 2026-11-16 — C14/C15 depth run 2026-11-16d (class weights)

- **Done** (Pablo, 16 Nov): `run.CLASS_W = True`. Depth events now carry their in-slab class weight, as in the rates: catalogue `w_inslab`, Riedel-Hornig by the A7 depth rule. 87 955 events, weight 74 432. `options.py` per-group medians and the w1-check share are weighted too. `figs.CELL_STRIP = 7` km; events in the sections are shaded by weight. 25 tests pass.
- **Results** (REPORT_C15 section 8):
  - 95 % fraction 0.4715 (0.4744); one layer 0.243 (0.252).
  - The jump of the per-cell median at the 50 km slab-top line is gone: 17–20 km below the top everywhere, before 11–23 km.
  - What remains is a heavy top slice (w1 0.50) where the slab top is 50–70 km deep, where the interface band fades. Open for Pablo.
- **Tornado** (Pablo): only three layers against one layer. The S2 three-layer reference stays on `depth_cells_2026-11-16.csv`; S2 builds one new one-layer branch from `h_one` of `depth_cells_2026-11-16d.csv`.
- **Proposed DECISIONS lines:** REPORT_C15 section 8. They replace the C15 proposals of section 5, which assumed weight-1 events and the 0.252 fraction.
- **Commands:** from `psha_chile8/model/inslab/`: `python run.py` (15 min), then `python options.py` (2 min).
- **Suggested commit** (replaces the earlier C15 ones): `git add psha_chile8/model/inslab/{depth,run,options,figs}.py psha_chile8/model/inslab/REPORT_C15.md psha_chile8/model/inslab/tests/test_depth.py psha_chile8/model/inslab/tables/*_2026-11-16b.csv psha_chile8/model/inslab/tables/*_2026-11-16c.csv psha_chile8/model/inslab/tables/*_2026-11-16d.csv psha_chile8/model/inslab/figs/2026-11-16 psha_chile8/model/inslab/figs/2026-11-16b psha_chile8/model/inslab/figs/2026-11-16c psha_chile8/model/inslab/figs/2026-11-16d psha_chile8/tasks/C15_inslab_depth_options.md psha_chile8/DATA.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `C14/C15: in-slab depth runs 2026-11-16c and 16d (nest test as classify.py, slices split inside bins, events with their class weights); one layer at top + 0.243 x thickness`.
- **S3 (16 Nov, discussion): LOFS secondary traces as links** (`figs_checks.splay_map`, `model/crustal/figs/2026-11-16e/check_splays_j15.png`; A, 15 km jump, UCERF3 filters; no SHERIFS run).
  - Links: 45 with main traces only, 99 with all traces. Chains: 300 against 2 767.
  - Longest chain 416 km → 810 km; Leonard Mmax 7.6 → 7.9 at 10 km depth, 7.9 → 8.2 at 20 km (above the arc cap 7.9).
  - The length comes from two NE secondary traces near Aysén that bridge separate groups of main traces:
    - CL-006qq Fiordo Aysén–Puerto Cisnes (strike 41°, 24–42° to the main traces, the fault of the 2007 Aysén sequence)
    - CL-006rr Quitralco (strike 37°)
  - The transverse faults (9 in A, strikes 112–148°, sinistral-reverse) are NW, 90–120° to the main traces; not linked (Pablo).
  - Fagnano SHERIFS: a tornado row (Pablo). Atacama and the other systems: not linked.
- **Sections redrawn** (Pablo, 16 Nov), on run 2026-11-16d unchanged. The class weights stay in the model; only the plot changed.
  - Layout: pituPLOTS theme `report`, a map of the trench-normal profiles (`profiles_from_line`) with the trench and the Slab2 50, 100 and 200 km contours, and 8 sections in a 4 × 2 grid.
  - Events: shaded by their in-slab weight (alpha 0.6 × weight), events under 0.05 not drawn.
  - Files: `figs/2026-11-16d/sections_layers.png` (19–32.5° S) and `sections_layers_south.png` (33.5–42° S). `options.SECTIONS` and `SOUTH` give the latitudes.
- **Final commit for the C14/C15 depth work** (replaces the earlier C15 suggestions; S2's own changes in `build.py`, `oqcheck.py`, `REPORT_S2.md`, `test_s2.py` and `nrml/` are left out): `git add psha_chile8/model/inslab/{depth,run,options,figs}.py psha_chile8/model/inslab/REPORT_C15.md psha_chile8/model/inslab/tests/test_depth.py psha_chile8/model/inslab/tables/{depth_cells,depth_events,events_log,depth_summary,compare_v1,compare_2026-11-15e,heldout,sensitivity_all_depths,depth_cells_all_depths,fraction}_2026-11-16.csv psha_chile8/model/inslab/tables/{depth_cells,depth_cells_lsd065,depth_cells_lsd0615,onelayer,options,w1_check}_2026-11-16b.csv psha_chile8/model/inslab/tables/*_2026-11-16c.csv psha_chile8/model/inslab/tables/*_2026-11-16d.csv psha_chile8/model/inslab/figs/2026-11-16 psha_chile8/model/inslab/figs/2026-11-16b psha_chile8/model/inslab/figs/2026-11-16c psha_chile8/model/inslab/figs/2026-11-16d psha_chile8/tasks/C15_inslab_depth_options.md psha_chile8/DATA.md psha_chile8/PLAN.md psha_chile8/WORKLOG.md`; message `C14/C15: in-slab depth run 2026-11-16d (events with class weights, nest test as classify.py, slices split inside bins); one layer at top + 0.243 x thickness; lower-depth options 0.65 and 0.615; section figures`.

## 2026-11-16 — S3: multi-fault rupture sets, discussion (crustal)
- **S3 (16 Nov, discussion): largest potential multi-fault ruptures, A, 15 km** (`figs_checks.rupture_maps`, `model/crustal/figs/2026-11-16e/check_ruptures_j15.png`; maximal chains, no rates).
  - LOFS main traces: 416 km at 39–42.5° S (Mw 7.6 / 7.9), 316 km at 45–48° S, the Aysén segment (7.5 / 7.8), 229 km at 42.7–44.7° S.
  - LOFS with secondary traces: 810 km at 42.5–47.8° S (7.9 / 8.2), zig-zagging through the NE splays near Aysén and the eastern N–S traces; 535 km at 45–48° S (7.7 / 8.0); 454 km in the north (one splay).
  - North of LOFS: only Antiñir–Copahue chains (about 37° S, 133–148 km, Mw 7.2 / 7.5), almost all secondary traces at 0.3 mm/yr. None with main traces only. No multi-fault ruptures there in the model (linking is restricted to the LOFS system).
  - Correction: the 416 km chain of the main-trace rule is the northern LOFS, not Aysén. The longest main-trace chain at Aysén is 316 km.

## 2026-11-16, C15: in-slab depth files ready (2026-11-16c) (built by S2)
For S5. Details in `model/inslab/REPORT_S2.md` section 11.
- **Files:** `model/inslab/nrml/2026-11-16c/`. It holds every file of `nrml/2026-11-16b/` byte for byte (sha256 checked), with `branches.json` extended, plus three weight-0 branches made from the reference `gk_taper_ml_l3`. Each has `is_slab_<id>.xml` and `is_nest_<id>.xml`.
  - `gk_taper_ml_l3_l1c15`: one layer at top + 0.243 × thickness (`h_one` of `depth_cells_2026-11-16d.csv`).
  - `gk_taper_ml_l3_lsd065`: lower depth 0.65 (`depth_cells_lsd065_2026-11-16d.csv`), reference hypocentres.
  - `gk_taper_ml_l3_ah`: AllenHayesIntraslab (Pablo: worth trying; median area × 0.62–0.79 of Strasser).
  - Rates, source ids, upper depths and nodal planes are the reference's; lsd0615 not built (Pablo: lsd065 only).
- **Tornado block** in `branches.json` (S1 format, one branch at weight 1 per row):
  - `is_ref`: `gk_taper_ml_l3`;
  - `is_ab_p05` / `is_ab_p95`;
  - `is_decl_nn`: `nn_taper_ml_l3`;
  - `is_shape_cut`: `gk_trunc_ml_l3`;
  - `is_mmax_pad00` / `is_mmax_pad04`;
  - `is_l1c15`, `is_lsd065`, `is_ah`.
  - The old C14 one-layer branches `*_l1` stay in the files and are not rows.
- **Checks:** each variant differs from the reference in its one field only (ids, rates, depths and hypocentres compared as text). The OpenQuake parser reads all eight files, with rates equal to the tables (within 5e-8) and the scaling relation read as named. 26 tests pass.
- **For C15 / Pablo:** the 16d three-slice hypocentres differ from the reference cells (up to 7.7 km). The reference stays on `depth_cells_2026-11-16.csv` as C15 asked, so the tornado rows compare against it. If the 16d slices are to become the reference, that is a rebuild of the whole in-slab set.
- **Code:** `model/inslab/is_tornado.py` (entry script, settings at the top); test in `tests/test_s2.py`.
- **Commands** (from `psha_chile8/model/inslab/`, `PYTHONPATH` to the oq-engine checkout): `python is_tornado.py` (40 s).
- **Proposed DECISIONS lines** (Pablo adds):
  - In-slab tornado rows: "one layer at top + 0.243 × thickness, lower depth 0.65 and AllenHayesIntraslab scaling, each against the three-layer Strasser reference, weight 0 (`model/inslab/nrml/2026-11-16c/`, Pablo 16 Nov)".
- **Suggested commit:** `git add psha_chile8/model/inslab/is_tornado.py psha_chile8/model/inslab/tests/test_s2.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/oqread_2026-11-16c.csv psha_chile8/model/inslab/nrml/2026-11-16c/{branches.json,source_lt_inslab.xml} psha_chile8/WORKLOG.md`; message `S2: in-slab tornado files (one layer C15, lower depth 0.65, AllenHayesIntraslab) in nrml/2026-11-16c with the tornado block`.

## 2026-11-16 — S3: multi-fault rebuild, agreed design (crustal; not started)
- **Agreed with Pablo (16 Nov):** a new LOFS rupture set by the UCERF3 path rules, in a generalised builder, waiting until the open S5-note points are consolidated.
  - Units are subsections; a rupture is one path, each fault one contiguous run of subsections, jumps only between the closest subsection pair.
  - Azimuth is measured along the path; at least 2 subsections per fault in a linked rupture.
  - Every rupture gets one magnitude from its area; all LOFS ruptures come from the rupture set (no floating simple-fault sources for LOFS in the multi-fault branch); each subsection is one planar section in OpenQuake.
- **Settings, each a possible tornado row:**
  - systems to link (LOFS; Fagnano row) and to exclude (LOFS Transverse)
  - main traces only, or main plus NE splays
  - database (A; B later, for testing only)
  - subsection length (10 km proposed by Pablo, see the open point below)
  - jump 5 / 10 / 15 / 20 km
  - the UCERF3 filters as published (junction and total azimuth 60°, cumulative azimuth 560°, cumulative rake 180°, sinistral / dextral reversal, 2 subsections per fault)
  - rupture-length cap (none by default; the maximum rupture length of each choice reported)
  - scaling Leonard 2014 / Hanks and Bakun 2008 / Thingbaijam et al. 2017
  - class Mmax handling
  - SHERIFS increment, anchor bins, seeds, target b
  - coarse resolution for trials
- **Checks before rates:**
  - rupture counts and maps
  - the geometries by eye
  - junctions onto ENE-oblique faults or with a change of slip sense, listed as the Coulomb proxy (Pablo: NS–NE faults are Coulomb-compatible)
- **Note for later (Pablo asked to keep it):** the tornado shows one choice changed at a time from one reference, not every combination (jump × splays × depth × ψ would multiply the rows).
- **S3, multi-fault design, agreed with Pablo (16 Nov, supersedes the "one magnitude per rupture" line above):**
  - The rupture set comes from the UCERF3 path rules on subsections of half the depth (5 km in the comparison).
  - Strict rule: a rupture is kept only if it uses every member fault entirely, i.e. faults link tip to tip, including a main trace that ends and continues onto a splay.
  - The kept ruptures are merged to whole-fault scenarios for SHERIFS. Single faults keep their floating ruptures from Mw 6.0 to the Leonard Mmax, so the subsection size does not set Mmin. Linked scenarios host the bins above their members' Mmax.
  - Ruptures above the class Mmax are dropped, after a comparison with clipping.
  - Reason for the strict rule: the area that sets a linked rupture's magnitude and spends its members' slip must be the area that ruptured. Merging a partly used fault would overstate both.
  - First step, rupture sets only (no rates): per jump (5 / 10 / 15 km) and main only / main + splays, the count of UCERF3 ruptures that pass the strict rule and what is lost; maps of the largest ruptures; drop against clip (counts, moment). Starts after the open S5-note points are consolidated.
- **S3, decided with Pablo (16 Nov):**
  - Mmax tornado rows: background class Mmax pad 0 / 0.2 / 0.4 (0.2 the reference; the orchestrator's `fits_2026-11-16f_pad00` and `_pad04` tables); single faults Leonard + 0 / 0.2 / 0.4; multi-fault linked ruptures with the Leonard Mmax against the class-Mmax drop. EPRI (Johnston et al. 1994) is for stable continents, not a candidate here.
  - Crustal source Mmin 5.5 for the tornado (comparable rows across families); for the final model it may go to 5.0.
  - Full subsections into SHERIFS: a later test against the strict rule (both the linked rates and the single-fault MFDs).
- **Open:** whether S5 runs the crustal family tree now or only the tornado rows.
- **Pablo (16 Nov): all branch weights equal across the whole model.** The crustal tree keeps declustering 0.5 / 0.5, fault system 0.5 / 0.5, and equal weights inside each system (segmented: the DECISIONS ψ 0.25 / 0.5 / 0.25 and depth 0.5 / 0.5 are the current files; to be made equal when the tree is rebuilt). S5 runs the tornado rows now; the tree after the multi-fault rebuild.
- **S3 (16 Nov): strict UCERF3 rupture set built and compared** (`model/crustal/rupset.py`, `rupset_compare.py`; REPORT_S3 section 12; `figs/2026-11-16e/check_strict_scenarios.png`; `tables/rupset_compare_2026-11-16e.csv`, `rupsets_A_2026-11-16e.pkl`). No rates, no files.
  - Scenarios are linear chains; longest 359 km at a 15 km jump (Mw 7.5 at 10 km depth, 7.8 at 20 km); 75 scenarios with main traces, 121 with splays.
  - Aysén 7.7 reached only at 20 km depth. No scenario above the arc cap 7.9 in A.
  - Open for Pablo: the subsection size at 20 km depth (half-depth 10 km pieces bar nine short faults by the two-subsection rule; fixed 5 km pieces or MIN_SUBS 1 for short faults); and the three junctions at 48–53° onto dextral-normal splays (CL-007, CL-012, CL-006kkk) as the Coulomb proxy.
  - Test added (22 passed).

## 2026-11-16, S2: in-slab declustered-rate tornado rows ready (2026-11-16d)
For S5. Details in `model/inslab/REPORT_S2.md` section 12.
- **Files:** `model/inslab/nrml/2026-11-16d/`, its own folder: `branches.json` with a tornado block, plus `is_slab_<id>.xml` and `is_nest_<id>.xml` for two weight-0 branches. Each is the reference branch (tapered, ML (a, b), three layers, StrasserIntraslab, lower depth 0.475) with the rates and b of `fits_declustered_2026-11-16f.csv` (gk_family / nn_family, table full, b own, as the interface rows of S1) and the pattern of the same method.
- **Tornado rows:** `is_rate_gk` = `gk_taper_ml_l3_rategk`, `is_rate_nn` = `nn_taper_ml_l3_ratenn`, each one branch at weight 1. The reference row is `is_ref` of `nrml/2026-11-16c/`.
- **Effect** (slab = shallow + intermediate):
  - Gardner–Knopoff: b about 1.0, N(≥ 5.5) −25 %, N(≥ 7) +28 %;
  - nearest neighbour: within 5 %;
  - nest under Gardner–Knopoff: b 0.77, N(≥ 7) +76 %.
- **Checks:** rates equal the fits; the OpenQuake parser reads the four files; 27 tests pass.
- **Code:** `model/inslab/is_decl_rates.py` (entry script, settings at the top), test in `tests/test_s2.py`. Command, from `psha_chile8/model/inslab/` with `PYTHONPATH` to oq-engine: `python is_decl_rates.py` (1 min).
- **Proposed DECISIONS line** (Pablo adds), In-slab: "Rate convention as a tornado row: the reference branch with the rates and b of the declustered fits (gk_family / nn_family, table full, b own) and the matching pattern, weight 0 (`model/inslab/nrml/2026-11-16d/`, Pablo 16 Nov)."
- **Suggested commit:** `git add psha_chile8/model/inslab/is_decl_rates.py psha_chile8/model/inslab/tests/test_s2.py psha_chile8/model/inslab/REPORT_S2.md psha_chile8/model/inslab/tables/{decl_rates,oqread}_2026-11-16d.csv psha_chile8/model/inslab/nrml/2026-11-16d/branches.json psha_chile8/WORKLOG.md`; message `S2: in-slab declustered-rate tornado rows (gk_family, nn_family) in nrml/2026-11-16d`.
- **Decided by Pablo (16 Nov): subsections fixed at 5 km for every depth branch** (`rupset.SUB_KM`). The 20 km branch now has the same 75 / 121 scenarios as the 10 km branch (Mmax 7.8 at 20 km). Comparison table and REPORT_S3 section 12 updated. Open: the three junctions at 48–53° onto dextral-normal splays.

## 2026-11-16 — S5: interface 2026-11-16c and in-slab 2026-11-16c/d in the tornado (Claude Code)
- **Done:** hazard/config.py points to `model/interface/nrml_2026-11-16c` and `model/inslab/nrml/2026-11-16c` (+ extra folder `2026-11-16d` for the declustered-rate rows); build.py reads the tornado blocks of every family. New rows: IF · Mmax pad (+0 / +0.4 against t_if_pad02, margin + segments 0.5 / 0.5); IS · MFD shape, Mmax pad, layers (C15 one layer), lower depth 0.65, rupture scaling Allen–Hayes, declustering GK74 / NN. 17 jobs run (calcs 597–613), check_tree PASS, tornado_final, trees and tornado_prelim regenerated. REPORT_S5a section 10.
- **Crustal on hold:** S3 rewrote the multi-fault and sections files of `model/crustal/nrml/2026-11-16e` at 15:44 (rebuild in progress, Pablo). Crustal results stay on calcs 538–591 (earlier files); rerun when S3 publishes the new folder.
- **Suggested commit:** `git add psha_chile8/hazard/{config,build,jobs,tornado_prelim}.py psha_chile8/hazard/REPORT_S5a.md psha_chile8/hazard/out psha_chile8/WORKLOG.md`; message `S5: interface nrml_2026-11-16c (Mmax pad level, new segments) and in-slab 2026-11-16c/d rows in the tornado`.
- **S5 (16 Nov, later):** in-slab declustering split into IS · spatial pattern and IS · declustering (rates alone; the NN-rates job measured against the NN-pattern job). Branch labels on every axis of the slide figure. New review figures: `hazard/tornado_full.py` (full tornado, trial cities Iquique, Calama, Pucón) and `hazard/tornado_matrix.py` (cities × levels grouped by tectonic setting); style in FIGURE_STYLE_tornado.md. Final versions after the crustal rebuild. Add to the commit: `psha_chile8/hazard/{tornado_full,tornado_matrix}.py psha_chile8/hazard/FIGURE_STYLE_tornado.md`.
- **S3 (16 Nov): scenario pages** (`figs_checks.scenario_pages`): `model/crustal/figs/2026-11-16e/scenarios_j15_main/001–075.png` and `scenarios_j15_all/001–121.png`, largest first, with Pablo's layout (new `basemap_gray.tif`, no coastline, fault ids, Mw and length box, legend). The basemap of these pages is the setting `SCEN_BASEMAP` in `figs_checks.py`.
- **Wording (Pablo, 16 Nov): the fault 10 / 20 km branches are the seismogenic thickness**, not depth; depth stays for events and the point-source hypocentre. Figure labels, REPORT_S3 (section 12 on) and the memory note use "thickness" from here on; the file tags `z10` / `z20` and the branch ids become `t10` / `t20` at the next rebuild, since S5 reads the current ones.

## 2026-11-16: LOFS event maps and the Aysén 1960 location (Claude Code, A7)

Pablo asked for maps of the events along the Liquiñe–Ofqui fault system, to check which agency located them. Nothing changed in the catalogue.

- **Maps:** `catalog/figs/classify/lofs_south.png` (43.6–48.2° S, Mw ≥ 3) and `lofs_full.png` (37.8–48.2° S, Mw ≥ 4); script `explore/A9/a9_lofs.py` (from `catalog/`, `PYTHONPATH=.:..`), on the frozen catalogue `2026-11-16c`. Basemap `data/basemaps/basemap_chile_gray/basemap_gray.tif`, faults `data/faults/faults_gem_extra_2026-11-15.shp` (LOFS in red). Circle size by Mw, colour by reported depth (grey: none), white edge for split class weights. Callouts for events with crustal weight within 50 km of a LOFS trace (Mw ≥ 5.5, or 5.0 with a mechanism; full map 5.7 / 5.2): date, Mw, locating agency, depth and its source, class, GCMT mechanism. Every epicentre the ISC Bulletin lists is drawn for those of Mw ≥ 6.8 before 1964. Tables `explore/A9/lofs_*_events.csv`, `lofs_*_origins.csv`.
- **Aysén 1960-06-06 05:55 (Mw 7.7):** the catalogue uses the Centennial epicentre (EHB, 45.70° S 73.50° W, depth fixed at 15 km), which falls on the western LOFS trace. Other epicentres: ISC-GEM 45.75° S 72.92° W, ISC 45.79° S 72.89° W (both about 45 km east, among the 1965 and 1991 events), ISS 45.71° S 73.08° W, BCIS and CGS 45.5° S 73.5° W, MOS 47.0° S 74.0° W. Kanamori and Rivera (2017, p. 93) take the Centennial epicentre as given and do not relocate; their mechanism is a choice (NS right-lateral) on limited first motions. The A5 rule puts the Centennial first before 1964.
- **1927-11-21 (Mw 7.1):** also a Centennial epicentre (45.11° S 73.62° W); ISC-GEM, ISC, ISS and Gutenberg put it 40–90 km north-east, near the 2007 Aysén swarm.
- **1991-08 events (Mw 5.5–6.0, 45.8–45.9° S, 72.6–73.2° W):** a cluster near Hudson volcano, in August 1991; probably related to its eruption of that month (not checked in a source).
- **For Pablo:** whether the Centennial epicentre should stay first for these two events is an A6 question (a location override with a source).

## 2026-11-16, GM1: module-name clash fixed

- **Renames:**
  - `gmm/run.py` → `gmm/gm1_run.py` and `gmm/figs.py` → `gmm/gm1_figs.py`. The old names clashed with `fits/run.py`, `model/inslab/run.py` and three `figs.py` when pytest ran from `psha_chile8/`.
  - Imports in `gm1_run.py`, `gm1_figs.py` and `summary.py` follow the new names.
  - Mentions updated in REPORT_GM1, FIGURES_GUIDE, APPENDS_GM1 and the two GM1 rows of FIGURES.md.
- **Tests:** `pytest` from `psha_chile8/` gives 338 passed.
- **Commands:** from `psha_chile8/gmm/`, `python gm1_run.py` (full run) and `python gm1_figs.py` (figures only).
- **Commit:**
  - `git add -A psha_chile8/gmm`
  - `git add -p psha_chile8/FIGURES.md psha_chile8/WORKLOG.md`
  - `git commit -m "GM1: entry and figure modules renamed gm1_run.py and gm1_figs.py (pytest name clash with fits/ and model/)"`

## 2026-11-16: B14, backarc and Patagonia not pooled, options (Claude Code)
- **Asked (Pablo):** classes below 15 weighted mechanisms are not pooled; for the backarc (8) and Patagonia (7), choose between their own mechanisms and one fixed mechanism from the dominant faulting of the class. `REPORT_B14.md`, last section, gives both options per class with the planes, every event, and the Kagan angle of each event to the fixed mechanism. No code or table changed yet; `npd_2026-11-16d.csv` is written once Pablo picks.
- **Fixed mechanisms** (from the traces in `data/faults/faults_2026-11-15.gpkg`):
  - Backarc: the 8 Precordillera thrusts inside the crustal grid, 312 km, length-weighted axial strike 9°, median dip 37.5°, six of eight dipping east → 10/40/90 and 190/50/90. No Sierras Pampeanas fault lies inside the grid.
  - Patagonia: the Magallanes–Fagnano main trace, 490 km, axial strike 111°, vertical, left-lateral → 110/90/0 and 20/90/180.
- **Check:**
  - Backarc: the five Precordillera reverse events are 20–40° from the fixed thrust. San Juan 2021 (Mw 6.5, oblique strike-slip) is 62° away. The two Altiplano/Puna events (19° and 22° S) are 89–107° away.
  - Patagonia: none of its 7 mechanisms is on the Magallanes–Fagnano system; all are 53–95° from its mechanism. The own planes rest on 1–3 events per type.
- **Open (Pablo):** pick own or fixed for each class. Then `npd.py` drops the pooling (`min_n`) and takes the picked rows, writes `npd_2026-11-16d.csv`, and S3 and S5 read only that file.

## 2026-11-16: A9, LOFS epicentres of Aysén 1960 and 1927-11-21, phase 1 (Claude Code, A6)
Report only; nothing changed. Brief from A7 (Pablo, 16 Nov); the A7 entry "LOFS event maps and the Aysén 1960 location" and the DECISIONS Catalog lines were read.

- **Read myself:**
  - Centennial raw record and README (`catalog/sources/raw/centennial/`)
  - ISC-GEM v13.0 raw rows (`raw/iscgem/isc-gem-cat.csv`)
  - Engdahl and Villaseñor (2002), Table 1 and pp. 666–667
  - Bondár et al. (2015, PEPI 239), pp. 2 and 11
  - Kanamori and Rivera (2017), pp. 93, 100, 103
- **Not available** (not in `refs/`):
  - Kanamori and Stewart (1979), Cifuentes (1989), Naranjo et al. (2009), Agurto et al. (2012)
  - Gutenberg and Richter (1954), cited only through Kanamori and Rivera
- **How the epicentres were made:**
  - Centennial / EHB: relocated by the EHB method from ISS-era arrival times (Engdahl and Villaseñor 2002, pp. 666–667, who note that many pre-1964 locations are poorly constrained).
  - ISC-GEM: relocated in two steps (EHB, then the ISC locator, which accounts for correlated travel-time errors), with about one million P and S arrival times added for 1904–1970 from station bulletins and digitised ISS pages (Bondár et al. 2015, p. 2). Quality flags A–D; epicentres from a poor network geometry are never given the best flag (p. 11).
- **Aysén 1960-06-06 (`cl19600606055549`):**
  - Centennial 45.700° S 73.502° W: EHB, open azimuth < 180° (A), 137 teleseismic observations, depth fixed (FEQ).
  - ISC-GEM 45.748° S 72.919° W: epicentre quality A, error ellipse 9.3 × 6.7 km.
  - The others: ISC 45.785° S 72.889° W (5 km from ISC-GEM); Pacheco and Sykes 45.71° S 73.00° W; ISS 45.71° S 73.08° W; BCIS and CGS 45.5° S 73.5° W (coarse); MOS 47.0° S 74.0° W (outlier). Centennial and ISC-GEM are about 41 km apart.
  - Kanamori and Rivera (2017, p. 93) use the Centennial epicentre and depth as given, without relocating. On p. 103 they say no reports of macroseismic effects are available to them, so no damage, landslide or fjord tsunami places the source. Chinn and Isacks put the 1965-11-28 Ms 6.1 strike-slip event at 45.77° S 72.90° W (cited there, p. 93), 2 km from the ISC-GEM 1960 epicentre.
  - **Best supported:** not decided by the evidence, but it leans to ISC-GEM. Both solutions are top quality, and their 41 km difference is larger than either stated error. ISC-GEM uses more arrival times and the newer locator; ISC agrees with it, and P&S and ISS also lie east of Centennial.
- **1927-11-21 23:12 (`cl19271121231233`):**
  - Centennial 45.112° S 73.622° W: EHB, flagged XEQ ("poor solution"), only 17 teleseismic observations.
  - ISC-GEM 44.861° S 72.686° W: quality B, ellipse 12.1 × 8.6 km.
  - The others: ISC 44.816° S 72.926° W, ISS 44.7° S 73.0° W, Gutenberg and Richter 44.5° S 73.0° W (also cited by Kanamori and Rivera, p. 93, as M 7.1, "very little is known about this earthquake").
  - **Best supported: ISC-GEM.** The Centennial solution is flagged poor and rests on 17 readings. Every other agency is 20–30 km from ISC-GEM, and Centennial is about 79 km away.
- **Effect of a change** (traces `data/faults/faults_gem_extra_2026-11-15.shp`, LOFS by `system`; arc polygon `../data/intraarc.shp`):

  | Event | Candidate | Nearest LOFS trace | Distance |
  |---|---|---|---|
  | 1960 | Centennial | Canal Costa (006ww, western) | 3 km |
  | 1960 | ISC-GEM | Riesco–Mañihuales (006tt) | 5 km |
  | 1960 | ISC | Riesco–Mañihuales (006tt) | 10 km |
  | 1927 | Centennial | Canal Costa (006ww) | 15 km |
  | 1927 | ISC-GEM | Fiordo Aysén–Puerto Cisnes (006qq) | 6 km |
  | 1927 | ISC | Fiordo Puyuhuapi (006pp) | 3 km |

  - Every candidate is inside the arc polygon, so the class stays crustal arc (by hint for 1960, by position for 1927).
  - The arc Mmax stays 7.9: Aysén keeps Mw 7.7 wherever it sits, and 1927 stays Mw 7.1.
  - Only the epicentres move, 41 km and 79 km east and north-east. That affects the spatial pattern of the smoothed crustal background and any event-to-fault association; the arc rates do not change.
- **For Pablo (phase 2, if decided):**
  - 1927 location rows to ISC-GEM 44.861° S 72.686° W (ISC-GEM v13.0, entry 909648; Centennial flagged XEQ).
  - 1960: keep Centennial, or move to ISC-GEM 45.748° S 72.919° W (entry 879416), a judgement on two A-quality solutions.
  - No DECISIONS change needed: an A6 override with source.
- **S3 (16 Nov): SHERIFS on the strict rupture set, one case** (A, LOFS, 15 km, main traces; REPORT_S3 section 13). `multifault.RUPSET = "strict"` feeds the `rupset` scenarios; class Mmax now drops scenarios instead of clipping (test updated, 22 passed).
  - 75 scenarios (300 with the old chains); arc Mw ≥ 6 since 1976 at ψ 0.6 / 0.8 / 1.0: 9.2 / 12.2 / 15.3 at 10 km thickness (chains: 7.3 / 9.8 / 12.2), 11.7 / 15.7 / 19.6 at 20 km. Passes only at ψ 0.6, 10 km (p 0.19).
  - The old chains passed partly on branching and overlapping ruptures that spent extra slip; the strict set gives the bulge back in part.
  - Chain-run numbers of 10c kept here: 10 km 7.3 / 9.8 / 12.2 (p 0.41 / 0.15 / 0.04); 20 km 9.3 / 12.3 / 15.3.

## 2026-11-16: B14, npd_2026-11-16d.csv (Claude Code)
- **Decided (Pablo):** below 15 weighted mechanisms a class is not pooled; it takes the fixed mechanism of its dominant fault system. Backarc: Precordillera thrust 10/40/90. Patagonia: Magallanes–Fagnano 110/90/0. Each with its auxiliary plane, 0.5 per plane.
- **Done:**
  - `npd.py`: `MIN_N = 15` and `FAULT` replace the family pooling; `DATE = "2026-11-16d"`, `PREV = "2026-11-16c"`; moves typed from the counts table source.
  - Written `npd_2026-11-16d.csv`, `tables/*_2026-11-16d.csv` and `figs/ternary_2026-11-16d.png` (stars for the fault mechanisms); `REPORT_B14.md` updated.
  - Every other class is identical to `npd_2026-11-16c.csv`.
  - New test `test_fault_classes`; 4 tests pass. DATA row 2026-11-16d (B14).
- **Note:** none of Patagonia's 7 mechanisms (44.9–51.6° S) lies on the Magallanes–Fagnano system; they are 53–95° (Kagan) from its mechanism. Written in the report.
- **Proposed DECISIONS line (In-slab and Crustal, replaces the B14 line):** "Nodal planes per class from the catalogue mechanisms (B14, `npd_2026-11-16d.csv`, on the catalogue 2026-11-16c; Frohlich types, one plane per type and its auxiliary at half weight, types below 10 % dropped and the rest renormalised). A class below 15 weighted mechanisms takes the mechanism of its dominant fault system from the fault traces: backarc Precordillera thrust 10/40/90, Patagonia Magallanes–Fagnano 110/90/0 (Pablo, 16 Nov). S3 and S5 read only this file; not a tornado factor." Superseded line: "`npd_2026-11-16.csv` → `npd_2026-11-16d.csv` (catalogue 2026-11-16c; backarc and Patagonia from their faults, 16 Nov)."
- **For S3 and S5:** read `model/mechanisms/npd_2026-11-16d.csv` (columns class, strike, dip, rake, weight).
- **Suggested commit:** `git add psha_chile8/model/mechanisms psha_chile8/DATA.md psha_chile8/WORKLOG.md`; message `B14: npd_2026-11-16d.csv, backarc and Patagonia take the mechanism of their dominant fault system`
- **Phase 2 (Pablo, 16 Nov): both epicentres to ISC-GEM.** Accepted `lon` and `lat` rows in `catalog/overrides_A6.csv`:
  - 1927-11-21: 44.861° S 72.686° W (entry 909648)
  - Aysén 1960-06-06: 45.748° S 72.919° W (entry 879416)
  - Reference ISC-GEM v13.0 (Bondár et al. 2015, p. 2); the reasons as in the phase 1 entry.
  - The class (crustal arc), Mw and arc Mmax (7.9) do not change. They act at the next run of the chain (A7 reruns and freezes).
- **Proposed DECISIONS line** (A6 line, after the 1919 epicentre): "1927-11-21 and Aysén 1960-06-06 epicentres to ISC-GEM (1927: Centennial flagged poor; 1960: two A-quality solutions 41 km apart, ISC-GEM with more arrival times and ISC agreeing) (Pablo, 16 Nov, A9)."
- **Commit:** `git add psha_chile8/catalog/overrides_A6.csv psha_chile8/WORKLOG.md`; message: `A6 (A9): 1927-11-21 and Aysén 1960 epicentres to ISC-GEM`

## 2026-11-16: LOFS epicentres applied, run `2026-11-16e`, frozen (Claude Code, A7)

A6 moved Aysén 1960-06-06 and 1927-11-21 to the ISC-GEM epicentre (accepted lon/lat rows, commit 316c500; Pablo, 16 Nov). DECISIONS read again before the run; no change that touches the classes.

- **Chain:** `locate.py`, `magnitude.py`, `locate.py`, `classify.py` (locations and magnitudes `2026-11-16d`, classes and catalogue `2026-11-16e`), the three checks; `pytest catalog`: 129 pass.
- **Against `2026-11-16c`:** only the two epicentres changed (1960: 45.748 S 72.919 W; 1927: 44.861 S 72.686 W). No other position, no depth, Mw, weight, class, rule or sub-class. Both stay crustal arc. Literature events and magnitude tests as before.
- **Frozen:** `catalog/frozen/2026-11-16e/` (`SHA256SUMS` verified, `DECISIONS_NOTE.md` with the change). Folders `2026-11-16`, `16b`, `16c` checked against their sums: unchanged.
- **Maps** `catalog/figs/classify/lofs_south.png` and `lofs_full.png` redrawn on the new catalogue.
- **Note:** the fits table `fits_2026-11-16e` (B11/B12) is on catalogue `2026-11-16c`; the catalogue name `2026-11-16e` is a different file. The refit takes the next free fits name.
- **Not committed yet:** the Scotia and grid rules in `classify.py` and its tests, and the frozen folders `2026-11-16b` and `2026-11-16c`, although the fits `2026-11-16e` are built on run c.
- **Commit** (from the repo root; it covers runs b, c and e):
  - `git add psha_chile8/catalog/classify.py psha_chile8/catalog/locate.py psha_chile8/catalog/magnitude.py psha_chile8/catalog/tests/test_classify.py psha_chile8/catalog/CLASSIFICATION.md psha_chile8/catalog/merged/MANIFEST.csv psha_chile8/catalog/figs psha_chile8/catalog/frozen/2026-11-16b psha_chile8/catalog/frozen/2026-11-16c psha_chile8/catalog/frozen/2026-11-16e psha_chile8/explore/A9 psha_chile8/DATA.md psha_chile8/WORKLOG.md`
  - `git commit -m "A7: Scotia–Antarctic boundary events to outer rise (run 2026-11-16b), crustal events outside the grid in the sub-class outside (2026-11-16c), Aysén 1960 and 1927 at the ISC-GEM epicentre (2026-11-16e); all frozen; LOFS maps"`
- **Proposed DECISIONS line:** none of mine beyond those of runs b and c; A6 proposed the line for the epicentres.

## 2026-11-16: arc class by latitude, diagnostic for the fault / background mismatch (Claude Code, B11/B12)

Asked by Pablo (the arc b and the Liquiñe–Ofqui faults). Exploration only: no rule, table or script changed; numbers computed inline on `fits/gr.py` (catalogue `2026-11-16c`; the newer frozen catalogue `2026-11-16e` moves two Liquiñe–Ofqui epicentres and is not yet read by the fits). Figure `fits/figs/arc_regions_2026-11-16f.png`. DECISIONS read before and after; unchanged for the fits.

- **The arc class is three regions.** Counted events of Mw ≥ 5 since 1976 (70 in all): north of 32° S 22, 32–38° S 18, Liquiñe–Ofqui (38–47.2° S) 31. Mw ≥ 6: 2, 2 and 3. So 56 % of the arc rate that S3 compares with the Liquiñe–Ofqui faults lies north of 38° S.
- **Liquiñe–Ofqui is two swarms.** 18 of its 31 events of Mw ≥ 5, and all 3 of Mw ≥ 6, belong to Hudson 1991 (Aug 1991 to early 1992) and the Aysén fjord swarm of 2007–2008. Mw ≥ 5 per period: 2.2 (1976–1989), 12 (1990s), 1 (2000–2006), 17 (2007–2011), 1 (2012–2019), 0 since. Without the swarms 12 events remain and b cannot be fitted (2.0 ± 0.5).
- **Own b per region** (cut line, 5.0 from 1976): north 1.07 ± 0.29, 32–38° S 0.77 ± 0.27, Liquiñe–Ofqui 1.09 ± 0.18; with "4.5 from 2000" added 1.01 ± 0.16, 1.08 ± 0.18, 1.01 ± 0.10. None differs from the family b (1.006) within its error; the instrumental record gives no lower b for Liquiñe–Ofqui.
- **Rates, Liquiñe–Ofqui alone:** N(≥ 5) 0.61 per year and N(≥ 6) 0.050–0.060 with the swarms; 0.25–0.28 and 0.025–0.038 without them or declustered. The S3 fault rate at Mw ≥ 6 is 0.447 (database A, `model/crustal/tables/join_2026-11-16e.csv`): 3.3 times the whole-arc fit (0.135), but 7–9 times the Liquiñe–Ofqui seismicity and 12–18 times without the swarms.
- **The long record points the other way.** Two events of Mw ≥ 7 since 1905, both on Liquiñe–Ofqui (1927 Mw 7.1, Aysén 1960 Mw 7.7): 0.016 per year. The Liquiñe–Ofqui line with the family b expects 0.66 in that time (P of two or more 0.14; 0.30 and P 0.04 without the swarms). With "7.0 from 1905" in the table the Liquiñe–Ofqui b is 0.91 ± 0.18 (0.94 ± 0.11 with 4.5 from 2000; 0.72 ± 0.30 declustered) and N(≥ 7) 0.008–0.009.
- **Completeness in the Liquiñe–Ofqui box** (all classes, 38–47.3° S, 74.5–70.5° W): 63–85 events of Mw ≥ 3.5 per window before 2007, too few for an Mc; in 1976–1989 the bands hold 4 (3.5–3.9), 15 (4.0–4.4), 25 (4.5–4.9) and 19 (≥ 5.0) events, an inverted distribution. Mc 4.6 in 2007–2011 (the swarm), about 4.0 from 2012. "Mw 5.0 from 1976" cannot be checked there.
- **Options for Pablo** (nothing applied): (1) split the arc unit at 38° S, with the family b for both parts and their own rates; (2) for Liquiñe–Ofqui, keep the events of Mw ≥ 7 since 1905 in the table (b about 0.9); (3) compare the faults with the Liquiñe–Ofqui rate only, in S3; (4) treat the two swarms as volcanic and leave them out of the Liquiñe–Ofqui rate, as a tornado row.
- **Commit:** add `psha_chile8/fits/figs/arc_regions_2026-11-16f.png psha_chile8/WORKLOG.md` to the next fits commit.


## 2026-11-16: LOFS maps redrawn; refit on `2026-11-16e` on hold (Claude Code, A7)

- **Maps** `catalog/figs/classify/lofs_south.png`, `lofs_full.png` (Pablo): only intra-arc events (crustal weight > 0, sub-class arc) are coloured by reported depth; every other class is grey. Edges: thick black, no measured depth (white fill); orange, weight shared with another class; thin black, one class with a depth. Callouts for intra-arc events only. An A6 epicentre shows as "ISC-GEM (A6; was Centennial)".
- **Found:** with an A6 lon/lat override, `loc_src` stays `cent_ehb` in the catalogue; only `loc_flags` (`a6_lon;a6_lat`) tells the position came from A6. For `locate.py` (A7) to set `loc_src = a6`, as `depth_src` already does; not changed here.
- **On hold (Pablo, 16 Nov):** the refit of B11/B12 on catalogue `2026-11-16e` (only two arc epicentres moved against `2026-11-16c`). The prompt is in this conversation; ask for it again when it is due.
- **S3 (16 Nov): rows on the strict rupture set and the Fagnano row** (REPORT_S3 section 14).
  - LOFS rows (A main / splays at 5 / 10 / 15 km; B, B-mm at 15 km): best case A with splays, 15 km, 10 km thickness (p 0.42 / 0.15 / 0.04 at ψ 0.6 / 0.8 / 1.0); main only passes at ψ 0.6 (0.19). B and B-mm fail everywhere.
  - Fagnano row (`fagnano_row.py`, `faults.load(split_system=True)`, `arc.observed(cls)`): the measured traces do not chain (a 67 km gap, an overlap), so SHERIFS gives more Mw 6 and no source for 1949; the joined 490 km source stays the model, the row is a tornado row.
  - Three Argentine Fagnano traces (82 km) fall outside the grid when split; they stay in the joined source. For Pablo: fine as is, or extend the grid 1° east at Tierra del Fuego?
  - `background.NPD` → `npd_2026-11-16d.csv` (B14 final, Pablo); takes effect at the rebuild.
- **Decided by Pablo (16 Nov):** the three Argentine Fagnano traces outside the grid stay dropped when the system is split (the row); the joined source keeps them.
- **S3 (16 Nov): Mmax pad rows** (`pad.py`, `tables/pad_rows_2026-11-16e.csv`; REPORT_S3 section 15). `background.set_pad()` switches the fits table (16f pad00 / pad04) and the class Mmax; `faults.FAULT_PAD` adds to the Leonard Mmax; the multi-fault cap reads `faults.class_mmax()`. The crustal code now reads `fits_2026-11-16f.csv` (identical to 16e for the crustal classes).
  - Background pad: tail only; forearc Mw ≥ 7 since 1905 0.8 / 1.8 / 2.7 against 3.5. Arc and Patagonia unchanged (no background above 6; the cap never binds in A).
  - Fault pad 0.2 / 0.4: arc faults / fit at Mw 6 2.97 → 2.13 → 1.58, expected arc Mw ≥ 6 20.4 → 14.7 → 10.8.
  - Rows for the files: background pad 0.0 / 0.4 for both systems; fault pad 0.2 / 0.4 for the segmented reference.

## 2026-11-16: Arc Mmax, two Aysén cases for the multi-fault comparison (Claude Code, A6)
- **Decided (Pablo, 16 Nov):** the arc crustal Mmax is carried in two cases, both compared with the LOFS multi-fault rupture model (S3b):
  - Aysén 1960 at Mw 7.7 (catalogue, ISC-GEM direct Mw, Kanamori and Rivera's long-period moment): arc Mmax 7.9, the model value.
  - Aysén at Mw 7.2 (its seismic-wave size, Ms 6.9–7.1; Pacheco and Sykes' converted value): arc Mmax 7.4, a comparison only. 1927-11-21 (Mw 7.1) sets nothing; 7.2 + 0.2 = 7.4.
- **Why:** the 7.7 is a reliable moment, but the event was slow (source ≥ 190 s, Mw–Ms 0.8), had no reported macroseismic effects, and its LOFS attribution rests on proximity and one non-unique mechanism (Kanamori and Rivera 2017, pp. 93, 100, 103). The arc Mmax rests on that single crustal hint.
- **For S3b and B11:**
  - Fit the arc with both Mmax values (corner from Kagan on each).
  - Show the multi-fault rupture set's largest LOFS ruptures (chain Mmax 7.4–8.3 by jump and depth, S3) against both lines.
  - Carry the difference into the tornado as a comparison case, not a logic-tree branch.
  - No catalogue change.
- **Proposed DECISIONS line** (Crustal, after "Background Mmax"): "Arc Mmax: 7.9 from Aysén 1960 at Mw 7.7; a comparison case with Aysén at its seismic-wave size, Mw 7.2 (Mmax 7.4), shown with the LOFS multi-fault model; not a branch (Pablo, 16 Nov)."
- **Aysén 1960 epicentre, the ambiguity that remains** (addendum to the A9 LOFS entry; the override to ISC-GEM stands, Pablo 16 Nov):
  - Only one solution puts the event on the western LOFS branch: Centennial / EHB (45.700° S 73.502° W). Kanamori and Rivera (2017, p. 93) copied it without relocating, so they are not a second source. BCIS and CGS (45.5° S 73.5° W) are also west, but rounded to half a degree.
  - ISC-GEM (45.748° S 72.919° W) is a relocation with more data and a newer locator (Bondár et al. 2015, p. 2). No source explains why it lands 41 km east for this event.
  - The ISC solution (5 km from ISC-GEM) comes from the same rebuild of old data, so it is not independent. The independent positions lie between the two: ISS 73.08° W (contemporary) and Pacheco and Sykes 73.00° W.
  - Both main solutions are top quality and claim errors near 10 km, yet they are 41 km apart, so at least one error is understated. The choice of ISC-GEM is a judgement (more data, partial support from ISS and P&S), not a demonstrated correction. Which LOFS branch slipped in 1960 remains unknown, and it should be stated that way where the event is tied to a fault (S3b, paper).

## 2026-11-16 — S3: crustal OpenQuake files ready (2026-11-16g)
- **Published:** `model/crustal/nrml/2026-11-16g/` (`branches.json` `"ready": true`), 77 files; CURRENT.md updated; hand-off note `handoffs/2026-11-16_CR_to_HAZ.md`. The 16e folder is superseded.
  - Multi-fault branch on the strict UCERF3 rupture set (`rupset.py`), Liquiñe–Ofqui, 15 km, main traces: 75 scenarios, 225 ruptures per file.
  - Thickness tags `t10` / `t20`; equal weights (segmented 1/36, multi-fault 1/6, systems and declustering 0.5 / 0.5); nodal planes `npd_2026-11-16d.csv`; fits `fits_2026-11-16f.csv`; source Mmin 5.5; `investigation_time = 1.0`.
  - Tree: 84 branches. Tornado: reference + 19 rows (new: `splays`, `mmax_pad00/04_mf`, `mmax_pad00/04_seg`, `fault_pad02/04_seg`; `jump20` dropped; `depth20` → `thickness20`).
  - Check: `tables/oqcheck_2026-11-16g.csv`, every file read by OpenQuake, 322 738 sources, none missing, rates within 4.3e-6. No engine job run (Pablo).
- **DECISIONS (Crustal and faults, Superseded):** the lines decided today are written in (fault-system branches, the rupture set and strict rule, equal weights, databases, faults outside the grid, fault Mmin, thickness wording, background point sources and Mmin 5.5, kernel n per class, Mmax pad rows, Fagnano row), each ending "(Pablo, 16 Nov, S3)".
- **Figures redrawn** with the corrected historical diamonds (`figs_s3.old_events`: each bin over the window of the largest completeness step at or below it; Aysén 7.7 now over 1830–2026, 0.0046 per year; 1927 7.1 over 1905–2026, 0.0069) and added to the Fagnano figure: `mf_lofs_study_*`, `join_*`, `check_counts`, `mf_fagnano`.
- **Code:** `rupset.py`, `rupset_compare.py`, `fagnano_row.py`, `pad.py` (new); `multifault.py` (`RUPSET`, `strict`, class-Mmax drop, splays), `mfsource.py` (strict set, splays, pads, `t` tags), `build.py` (rewritten), `background.py` (`set_pad`, `FITS_DATE`, `NPD` 16d), `faults.py` (`FAULT_PAD`, `class_mmax`, `split_system`), `arc.py` (`observed(cls)`), `figs_s3.py`, `figs_checks.py` (`strict_maps`, `scenario_pages`, `splay_map`, `rupture_maps`). Tests: 22 passed.
- **Open for Pablo:** Fagnano as a file row (the split traces would be the row; not built); Mmin 5.0 for the final model; the three junctions at 48–53° onto dextral-normal splays (kept).
- **Proposed LEARNINGS lines:**
  - Whole-fault chains by the UCERF3 thresholds alone make branching and overlapping ruptures that drain slip and pass the count test for the wrong reason; the path rules on subsections, with the strict rule, give linear chains and give part of the arc bulge back (16 Nov).
  - SHERIFS keeps one slip budget per fault, so a partially ruptured fault cannot be represented: either merge to whole faults (strict rule) or give it subsections as faults (16 Nov).
  - OpenQuake 3.27 multi-fault files: comma-separated section ids, one planar surface per section, NRML 0.5 with the investigation time on the source model, section ids unique across every sections file of a job (16 Nov).
- **Suggested commit:** `git add psha_chile8/model/crustal/{rupset,rupset_compare,fagnano_row,pad,multifault,mfsource,build,background,faults,arc,join,nrml,oqcheck,figs_s3,figs_checks}.py psha_chile8/model/crustal/tests/test_crustal.py psha_chile8/model/crustal/{REPORT_S3,S5_HANDOFF}.md psha_chile8/model/crustal/tables/{rupset_compare,mf_A_lofs,mf_A_lofs_splays,mf_B_lofs,mf_Bmm_lofs,mf_fagnano,pad_rows}_2026-11-16e.csv psha_chile8/model/crustal/figs/2026-11-16e psha_chile8/model/crustal/nrml/2026-11-16g/{branches.json,lt_crustal_tree.xml,lt_crustal_reference.xml} psha_chile8/model/crustal/oqcheck/2026-11-16g/job.ini psha_chile8/handoffs/2026-11-16_CR_to_HAZ.md psha_chile8/{CURRENT,DECISIONS,WORKLOG,FIGURES,PLAN}.md` — message: "S3: strict UCERF3 rupture set and SHERIFS for Liquiñe–Ofqui, Fagnano and Mmax-pad rows, crustal OpenQuake files 2026-11-16g (t10/t20, equal weights, 20 tornado rows)". The NRML source files, the `.pkl` caches and the two large tables stay untracked.
- **Decided by Pablo (16 Nov): the Fagnano split-trace row stays report-only** (REPORT_S3 section 14, `mf_fagnano.png`); no OpenQuake files for it. The open point above is closed.
- **S3 (16 Nov): summary figure set** `model/crustal/figs/summary/` (14 files, README), copies of the 16e figures in reading order; new `figs_checks.pad_figure` (`check_mmax_pads.png`).

## 2026-11-16 (night) — HAZ: crustal 2026-11-16g in the tornado; final-format figures
- **Done:** hazard/config.py reads the three family folders from CURRENT.md. Crustal on `model/crustal/nrml/2026-11-16g/` (handoff `handoffs/2026-11-16_CR_to_HAZ.md`): t_cr_ref (calc 614, 71 s), 19 rows, the tree as one job (f_cr_tree, 84 branches, calc 634, 344 s), GMM rows and truncation; calcs 614–642, none failed. Single-fault rows (class Mmax pad single-fault, fault Mmax pad) measured against t_cr_segmented. Reduced tornado, full tornado (all 14 cities, PNG + PDF) and matrix redrawn; trees with the crustal tree. REPORT_S5a section 11; CURRENT.md HAZ line updated.
- **Decision written to DECISIONS (Hazard runs):** the three tornado figures (reduced, full, matrix total only) (Pablo, 16 Nov, HAZ).
- **For CR (to read, not a request):** linking the LOFS secondary traces lowers PGA 475 at Puerto Aysén by 48 %; the single-fault fault Mmax pad +0.4 lowers it by 16–22 % in the south (moment balance moves rate to larger events). Background rows move crustal hazard up to 15 % within the family but the total ≤ 1 %.
- **Open:** in-slab nodal planes from B14 per cell (S2 step) before the final run.
- **Suggested commit:** `git add psha_chile8/hazard psha_chile8/CURRENT.md psha_chile8/DECISIONS.md psha_chile8/WORKLOG.md` (without `hazard/jobs/*/src`); message `HAZ: crustal 2026-11-16g in the tornado (calcs 614-642); inputs from CURRENT.md; reduced, full and matrix tornado figures`.
- **HAZ (16 Nov, night, later):** new figures `hazard/curves_city.py` (hazard curves per city and tectonic setting with the tornado envelope; `out/curves/<city>.png`, `all.png`) and `hazard/shares_bar.py` (share of each tectonic setting at the total PGA 475 yr; `out/shares/contribution.png/.pdf/.csv`); styles in `hazard/FIGURE_STYLE_tornado.md`. Add both scripts to the commit.

## 2026-11-16: A3 closed (Claude Code, A3)
- Handoff `handoffs/2026-11-16_A3_close.md`. CURRENT.md: new Catalogue line for the A3 events and links (`merged/events_` / `links_2026-11-11`). DECISIONS (Catalog): one line, ComCat links through GUC / SJA / LIM and windows from ≥ 100 pairs from 1964 on (Pablo, 16 Nov, A3). No code or output changed; `pytest catalog/tests/test_match.py` 34 pass.
- Suggested commit: `git add psha_chile8/handoffs/2026-11-16_A3_close.md psha_chile8/CURRENT.md psha_chile8/DECISIONS.md psha_chile8/WORKLOG.md` — message "A3 close: handoff note, CURRENT line for the matched events, A3 link and window decision". (The HAZ lines above in WORKLOG are uncommitted too; they belong to the HAZ commit.)

## 2026-11-16: FITS session closed (Claude Code, B11/B12)
- Handoff `handoffs/2026-11-16_FITS_close.md` (owned scripts and commands, current outputs, open points, traps, suggested commit).
- CURRENT.md FITS lines checked: correct, unchanged.
- DECISIONS.md, Statistics: stale pointers corrected, no rule changed. The 16e fits line now reads "kept (before 16f)"; the declustering factor names the current catalogues `*_2026-11-16e.csv`; declustered fits current = `fits_declustered_2026-11-16f.csv`. All of Pablo's FITS decisions were already in DECISIONS.
- Commit: see the handoff.

## 2026-11-16: A2b close (Claude Code)
- Done: handoff note `handoffs/2026-11-16_A2b_close.md`. No new work; everything of A2b is in commit 3bb70b3.
- Decisions made: none. DECISIONS (A4 location rule, 11 / 13 Nov) supersedes the A2b draft `catalog/PREFERENCES_draft_A4_location.md`; proposed to CAT: delete the draft and update PREFERENCES.md line 24.
- Open: a newer GCCEL on ScienceBase (check by hand); questions to E. Bergman on the offshore and Valparaíso depths.
- Suggested commit: `git add psha_chile8/handoffs/2026-11-16_A2b_close.md psha_chile8/WORKLOG.md` with `git commit -m "A2b close: handoff note"`

## 2026-11-16: FITS close, arc decision (Claude Code, B11/B12)
- Pablo: the arc stays one unit, no split by latitude; written into DECISIONS, Statistics. Check for him, no file changed: the arc uses Mw 5.0 from 1976 only since run 16c (full table until 16b: own b 1.00–1.02, N(≥ 6) 0.123–0.130); whole arc with the 1905 step b 0.98 ± 0.10; N(≥ 6) at fixed N(≥ 5): b 0.8 → 0.22, 0.5 → 0.43 (faults 0.447).
- `handoffs/2026-11-16_FITS_close.md` updated (arc point closed, FITS.md has 14 sections). Commit as in the handoff.

## 2026-11-16: A2 close (Claude Code, A2 conversation)
- Handoff note `handoffs/2026-11-16_A2_close.md` (scripts, outputs, traps). CURRENT.md: line added for the frozen source catalogs (`catalog/sources/*_2026-11-10_*`, GCCEL `2026-11-11`). DECISIONS: all A2 decisions already present, nothing added. No new work.
- Suggested commit: `git add psha_chile8/handoffs/2026-11-16_A2_close.md psha_chile8/CURRENT.md psha_chile8/WORKLOG.md`; `git commit -m "A2 close: handoff note, CURRENT line for the frozen source catalogs"`

## 2026-11-16: DECK1104 close (Claude Code, catalog-review deck session of 4 Nov)
- Handoff note `handoffs/2026-11-16_DECK1104_close.md`: the deck `presentations/261104_catalog_review/` (v2, psha_chile6 model and the 2026-11-04 catalog freeze), its figure scripts, the catalog checks `psha_chile7/outputs/a2/checks_1104/`, open points, traps. No CURRENT.md line (nothing published for other sessions); no DECISIONS lines (deck choices only, in `NOTES_v2.md`).
- Suggested commit: as in the handoff (deck without `pres_v1.pdf` and `check/`, `checks_1104/`, the handoff, this entry); message `Catalog-review deck of 4 Nov (v2) with its figure scripts; catalog checks of 4 Nov; handoff`.

## 2026-11-17 — C14/C15 session closed

- Handoff: `handoffs/2026-11-16_C15_close.md`.
- DECISIONS (Pablo, 16 Nov, C15):
  - depth events with their in-slab class weight (In-slab, depth sources line);
  - one layer at top + 0.243 × thickness (pointer in the C14 line, two Superseded lines);
  - tornado one layer against three, the three-layer reference not rebuilt.
- CURRENT: depth line lists `depth_cells_lsd0615_2026-11-16d.csv` and the run.
- No new work. Suggested commit in the handoff.

## 2026-11-17 — HAZ: verdict table of the 16 Nov tornado (Claude Code)
- **Read:** CLAUDE.md, CURRENT, PLAN, DECISIONS (Logic tree, Hazard runs, GMMs, family sections, Statistics), REPORT_S5a sections 9–11, FIGURE_STYLE_tornado, the CR → HAZ handoff and the S5 / HAZ entries of 16 Nov. DECISIONS re-read before finishing: unchanged.
- **Done:** `hazard/verdicts.py` → `hazard/out/verdicts_2026-11-17.csv` (44 levels: 10 interface, 9 in-slab, 14 crustal, 11 GMM sets; largest change of the total PGA 475 yr with city and branch, family-alone change, range, cities ≥ 5 %, set average, rule, ⚠ within 1 % of the line, proposed verdict, criterion) and `hazard/out/verdicts_2026-11-17.md`. Test `hazard/tests/test_verdicts.py` (10 hazard tests pass). No OpenQuake runs.
- **Proposed branches:** IF segmentation, rate model, b per segment, (a, b), rupture scaling, χ (5.9 %, ⚠); IS (a, b); declustering method GK74 / NN on the patterns (IS 12 %); CR LOFS secondary traces (−48 % Puerto Aysén), thickness, ψ; the models of the chosen GMM set.
- **Proposed fixed by a DECISIONS criterion, with range:** declustered rates IF (−11 / +10 %) and IS (+10 %) (full catalogue); fault database A (+44 %, arc count test); with faults (−75 %); fault Mmax Leonard (−22 %); jump 15 km (5.2 %, ⚠, UCERF3). Below 5 %, fixed: Mmax pads, MFD shapes, truncation 3σ (IS 4.5 % ⚠), IS layers / depth / scaling, CR background rows.
- **Open for Pablo (context conversation):** (1) interface rate convention: Statistics fixes full-catalogue rates, the Interface line still says open; (2) fault linkage is 3.7 %, but jump and secondary-trace levels exist only in multi-fault: single or multi-fault?; (3) shared interface b as criterion (fit failure 32–26° S) or three branches; (4) GMM sets to GM2, crustal GMM-CSN (+107 %, Arteta23) still unchecked.
- **Commands:** from `psha_chile8/`, `PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine python hazard/verdicts.py` (seconds; rerun after `tornado_prelim.py`).
- **Suggested commit:** `git add psha_chile8/hazard/verdicts.py psha_chile8/hazard/tests/test_verdicts.py psha_chile8/hazard/out/verdicts_2026-11-17.csv psha_chile8/hazard/out/verdicts_2026-11-17.md psha_chile8/WORKLOG.md`; message `HAZ: verdict table of the 16 Nov tornado (proposal by the 5 % rule)`.
- **HAZ (17 Nov, later), Pablo's reading of the table:**
  - Rule: a level goes in when the spread of its branches, the reference included, is ≥ 10 % at one city. Written to DECISIONS (Logic tree) with the verdicts below (Pablo, 17 Nov, HAZ).
  - Changes: no faults becomes a comparison (the model has faults); GMM sets other than the fitted one are comparisons; truncation is a modelling decision (probably high); LOFS secondary traces probably go into multi-fault.
  - Team topics: rate declustering (interface spread 21 %, in-slab 10 %), fault database, fault Mmax scaling relations, GMM calibration (all magnitudes or large ones), fault linkage, shared interface b, truncation level, Arteta et al. (2023). The Arteta note is pinned in the md.
  - `hazard/verdicts.py` now has spread columns (`spread_pct`, `spread_city`, `cities_ge10`) and the verdicts branch / fixed / comparison / team; csv and md rewritten; 11 hazard tests pass.
  - Layers (three against one): the effect follows the top-slice weight under each city (Pucón 0.68, family −5.5 %; Santiago 0.47, −6.5 %; Iquique 0.42, −3.8 %; Calama 0.22, −1.5 %; La Serena 0.11, +1.4 %). Calama is among the weakest, and Iquique, with both planes, is already a city. No extra run is needed; for the paper, a catalogue with better depth resolution could separate the two planes.
  - Add `psha_chile8/DECISIONS.md` to the suggested commit.
- **HAZ (17 Nov, later still):**
  - Three in-slab layers stay the model: physically more accurate, though small (DECISIONS, Logic tree, Pablo, 17 Nov).
  - Crustal pattern GK74 or NN: a suggestion to choose on the maps (`model/crustal/figs/2026-11-16e/pattern_{gk,nn}.png`). NN shows the Aysén hotspot (2007 fjord sequence) and a small one at about 40.7° S; south of 47° S the two are identical. Suggested: NN. Fixing it alone splits the joint declustering factor.
  - Cities (probably, not yet in DECISIONS): Puerto Williams replaced by a site near the Magallanes–Fagnano fault around Lago Fagnano (to be chosen), and Punta Arenas added, to show near-zero hazard. `hazard/config.py` is unchanged until the sites are fixed; both need new jobs and lower intensity levels.
  - Verdict csv and md updated.
- **HAZ (17 Nov):** one declustering algorithm for every family, with no GK74 / NN branch; which one is still to choose (DECISIONS, Logic tree, Pablo, 17 Nov). Verdicts updated. The NN in `fits/decluster.py` is Zaliapin and Ben-Zion (2013): mixture threshold on η, cluster trees, the largest event kept. It is not the 2020 thinning version. A change of algorithm belongs to FITS (B12 line in Statistics).
- **HAZ (17 Nov):** the 10 % spread rule is now written in full in DECISIONS (Logic tree): the 6 Oct line points to it, and there is a Superseded line; the 16 Nov verdict line says "branch rule".
- **HAZ (17 Nov):** the verdicts are written into DECISIONS (Logic tree) as branches, fixed, comparisons and open (team) levels, replacing the summary line; the rule, its Superseded line and the three-layer line were already in (Pablo, 17 Nov, HAZ).

## 2026-11-17 — context conversation: decisions after the verdicts (Claude, chat)
- **Written into DECISIONS** (Pablo, 17 Nov, context), each in its own section:
  - (a, b) weights 0.185 / 0.63 / 0.185 for 5th / ML / 95th, interface and in-slab: the exception to equal weights (Interface, In-slab, Logic tree).
  - Geodetic χ 0.7 / 0.8 / 0.9 at equal weights (Interface; Superseded line).
  - No Scotia–Antarctic source: its events stay outer rise, in no unit or fit. The Antarctic interface (geodetic) is the far-south source for completeness, as long as its convergence rate has a source. This replaces the morning line "source added" (Interface, Crustal; Superseded line).
  - Declustering: the 17 Nov Statistics line read NN as chosen. Corrected: the algorithm is chosen with the co-authors, most likely `nn_family`; the 15 Nov two-option line and the 0.5 / 0.5 declustered-rate rows stand until then.
  - With the co-authors: rate convention and b per segment (their branches stay in the tree), GMM truncation level (3σ until then, answer needed before the final run), the models and weights of the fitted GMM set.
  - Crustal source Mmin for the final model 4.9 or 5.0, to settle (5.5 was for the tornado). Arc bulge: no change, for the discussion.
  - Seismic / geodetic 0.5 / 0.5 to confirm after IF's explanation (below).
- **For the sessions** (read this entry; no separate prompt):
  - IF: explain, without a rebuild, why the geodetic branch moves PGA 475 by 13 % (1.2 % in psha_chile6) and the geodetic / seismic N(≥ 8) of 1.3 (margin) and 1.6–4.8 (segments) at χ 0.8. Write it in the WORKLOG.
  - FITS: check the `nn_family` implementation before the refit. No outer-rise or Scotia unit.
  - HAZ: `hazard/out/verdicts_2026-11-17.md` still names a Lago Fagnano site; DECISIONS has Ushuaia (−54.80, −68.30) and Punta Arenas. Fix it at the next rewrite, and set both cities in `config.py` for the final run.
  - CAT: no Scotia label is needed in the catalogue batch.
- **Rule change** (Pablo, 17 Nov): the context conversation writes Pablo's decisions into DECISIONS and logs them here itself (CLAUDE.md, end-of-session item 5).


## 2026-11-17: San Ramón trace in database A (Claude Code, D16 session)

- **Pablo, 17 Nov:** San Ramón CL-001a takes the trace of MASCSN26 fault 687; A's attributes are kept (dip 47.5° E, 0.4 mm/yr, our 10 / 20 km depth rule).
  - New trace 44.4 km (was 28.2), on all proved CHAF San Ramón strands. Leonard Mmax rises from about 6.9 to about 7.1.
  - Implemented as `SWAP` in `model/faults/curate.py`. `data/faults/faults_gem_extra_2026-11-15.shp` / `.csv` rewritten (138 faults). Tests pass.
- **Multi-fault branch:** unchanged, still Liquiñe–Ofqui only. In A, San Ramón has no neighbour within the 15 km jump.
- **South of San Ramón and Las Melosas:**
  - MASCSN26 has no other fault at 33.4–35.5° S in the Andes.
  - CHAF has the following, none added:
    - Las Melosas: 3.2 km, probable, tied to the 1958 event.
    - Río Colorado: 23 km, possible, about 20 km east of Peñalolén.
    - Machalí: 26 km, possible.
    - El Fierro / Garcés / Tinguiririca / Guanaco: 63 km, proved only through 6.6 km of El Fierro, tied to the 2004 Mw 6.5.
- **Proposed DECISIONS line** (Crustal and faults): "Database A: San Ramón (CL-001a) on the MASCSN26 trace (fault 687, 44 km), attributes of A (Pablo, 17 Nov)."
- **Commit:**
  - `git add model/faults/curate.py model/faults/REPORT_D16.md data/faults/faults_gem_extra_2026-11-15.* DATA.md WORKLOG.md` (from `psha_chile8/`)
  - Message: `D16: San Ramon trace from MASCSN26 (44 km) in database A, attributes kept`
- DECISIONS line written (Crustal and faults, after "Fault databases into the tornado"): San Ramón on the MASCSN26 trace in A (Pablo, 17 Nov, D16).
- Map `drafts/san_ramon/san_ramon.png` (script `san_ramon.py`): old and new San Ramón traces, CHAF strands by class, crustal events of Mw ≥ 5.5 (catalogue 16e).
  - The first version, `model/faults/figs_sr.py` and `model/faults/figs/san_ramon.png`, is superseded and can be deleted; the session could not delete it.
- **A against B rerun with the new San Ramón:** `model/faults/compare.py`, 9 s.
  - Rewritten: `tables/d16b_*_2026-11-15.csv` and `figs/faults_A_B_map.png`. The previous versions are kept in `figs/` and `tables/2026-11-15_before_san_ramon/`.
  - Only Santiago changes: N(≥ 6) of A 0.0014 → 0.0015 per yr; B / A 1.65 → 1.44.
- **Database A is final for this round (Pablo, 17 Nov).**
  - Suggested commit, from `psha_chile8/`: `git add model/faults/curate.py model/faults/REPORT_D16.md model/faults/tables/d16b_*_2026-11-15.csv model/faults/tables/2026-11-15_before_san_ramon model/faults/figs/2026-11-15_before_san_ramon data/faults/faults_gem_extra_2026-11-15.* DECISIONS.md DATA.md WORKLOG.md`
  - Message: `D16: San Ramon on the MASCSN26 trace (44 km) in database A, attributes kept; A against B rerun`

## 2026-11-17 — CAT: final catalogue 2026-11-17c, catalogue figures (Claude Code, CAT)
- **Done, step by step with Pablo:**
  - Source figures: `catalog/sources_figs.py` → `catalog/figs/sources/2026-11-17/` (maps per source on the domain, time lanes).
  - Overrides (`overrides_A6.csv`, now 115 accepted rows, the file for every per-event correction): 1953 Chillán in-slab, 1952 San Juan crustal, Las Melosas Mw 6.8, Pichilemu 15:06 Mw 6.2 and crustal, Valdivia 1960 mechanism 7/20/105 (Barrientos and Ward 1990, p. 592; replaces the oblique ISC-GEM/Kanamori et al. 2019 one, Savage 2022 p. 1171). Table by event: `catalog/A6/overrides_by_event_2026-11-17.md`.
  - Code: `locate.mechanisms()` takes the ISC-GEM literature mechanisms (agency bibliog) last; `magnitude.A6_ALSO` sets `loc_src = a6` for A6 epicentres and `mech_src = a6` for A6 mechanisms; tests added (137 pass in `catalog` and `plots`).
  - Runs `2026-11-17` (overrides), `2026-11-17b` (ISC-GEM literature mechanisms: 62 events, 14 of 1962–1970 change class), `2026-11-17c` (Valdivia mechanism); checks run each time. Frozen `catalog/frozen/2026-11-17c/` with SHA256SUMS, INPUTS_SHA256, code, DECISIONS_NOTE.
  - Class totals (Mw ≥ 4.5, domain), 16e → 17c: interface 4 502.8 → 4 495.6, in-slab 8 075.3 → 8 080.0, crustal 1 145.9 → 1 148.4; the 164 events of Mw ≥ 7 are the same.
  - `catalog/named_events.csv` (88 events named in the literature, label flag, label positions); `catalog/A6/mechanisms_named_2026-11-17.csv` (all 186 source mechanisms of the named events).
  - `plots/` (new): all pituPLOTS palettes copied (`palettes.json`, registered as `pp.<name>`; pituPLOTS not a dependency), depth colours, map helpers (Mercator domain, bands, projected boxes, inside coordinate labels), tests.
  - `palette.py`: M ≥ 7 band red; class colours by family; `FAMILY_COLOR`.
  - Catalogue figures: `catalog/fig_positions.py`, `fig_classes.py`, `fig_mechanisms.py` (UTM 19 S, three equal panels, labels from `named_events.csv`, `EDIT = True` to drag labels, saved on release) → `catalog/figs/catalogue/2026-11-17c/`. Drafts in `drafts/catalog_figs/` (not committed).
- **Decisions (Pablo, 17 Nov, CAT), in DECISIONS:** Catalog (batch of overrides, ISC-GEM literature mechanisms, overrides file holds mechanisms, named events list, final catalogue 17c, Superseded line); Figures (M ≥ 7 red, map rules, class colours by family).
- **Not changed (Pablo):** GCMT ahead of Ruiz and Madariaga after 1976; 1918-05-20 keeps the slab-convention depth; Pica 1768 dropped; 1907 Magallanes not added (reference event in the crustal fit figure, handoff to FITS).
- **Handoffs:** `handoffs/2026-11-17_CAT_to_FITS.md` (refit on 17c, 1907 reference event), `handoffs/2026-11-17_CAT_to_CR_HAZ.md` (Magallanes 1879 in the crustal model, faults on the mechanism map, hazard scripts to `FAMILY_COLOR`).
- **Open:** the 16–17 Nov batch list of the context conversation never reached this session; the overrides above were decided here from the notes. Faults to add to the mechanism map. pituPLOTS installed in psha_renta is an old non-editable copy (the checkout is c71a937).
- **LEARNINGS proposals:** (1) A heredoc that writes Markdown must be quoted (`<<'EOF'`), else the shell runs the backticked names. (2) Matplotlib `Text` is not draggable; `annotate` is, and the leader line follows. (3) Cartopy's `epsg(32719)` clips to the zone (72–66° W); write UTM 19 S as a TransverseMercator for wider maps.
- **Commit (from `psha_chile8/`):**
  - `git add palette.py plots/ catalog/locate.py catalog/magnitude.py catalog/classify.py catalog/tests/ catalog/overrides_A6.csv catalog/named_events.csv catalog/A6/overrides_by_event_2026-11-17.md catalog/A6/mechanisms_named_2026-11-17.csv catalog/sources_figs.py catalog/fig_*.py catalog/figs/sources/ catalog/figs/catalogue/ catalog/frozen/2026-11-17c/ catalog/merged/MANIFEST.csv DECISIONS.md DATA.md CURRENT.md FIGURES.md WORKLOG.md handoffs/2026-11-17_CAT_to_FITS.md handoffs/2026-11-17_CAT_to_CR_HAZ.md`
  - Message: `CAT: final catalogue 2026-11-17c (overrides of 17 Nov, ISC-GEM literature mechanisms, Valdivia 1960 mechanism), catalogue figures, plots module, family class colours`

## 2026-11-17 — CAT addendum: final catalogue 2026-11-17e (Claude Code, CAT)
- **Replaces 17c as the final catalogue** (`catalog/frozen/2026-11-17e/`; 17c kept as a step). Three 1960 events set to interface with weight 1, the only weight changes against 17c:
  - 1960-12-02 Mw 7.2 off Taltal: depth row 35 ± 6.3 km (ISC-GEM entry 880905, quality A; Centennial EHB had 14.1 km → crustal 0.78); at 35 km it was still split 0.54 / 0.44, so an interface hint by Pablo (no paper).
  - 1960-06-20 02:01 Mw 7.0 and 12:59 Mw 7.1 (were split): Cifuentes (1989, p. 670, Figs. 8–9) gives underthrusting of the Nazca plate, depths 20 and 24 km.
  - Totals (Mw ≥ 4.5, domain): interface 4 497.4, in-slab 8 079.8, crustal 1 146.8; 164 events of Mw ≥ 7. Runs: 2026-11-17d (depth only), 2026-11-17e (hints); 137 tests pass, checks run.
- In-slab colours now oranges to brown (ColorBrewer YlOrBr) in `palette.CLASS` and `FAMILY_COLOR` (Pablo); DECISIONS › Figures updated. Catalogue figures redrawn into `catalog/figs/catalogue/2026-11-17e/` (scripts read `RUN = "2026-11-17e"`).
- REFERENCES: Cifuentes 1989, Barrientos and Ward 1990, Kanamori and Cipar 1974, Kanamori et al. 2019, Savage 2022 (PDFs in `refs/catalogs/`).
- DECISIONS line on ISC-GEM literature mechanisms: 61 events keep them (Valdivia's replaced). CURRENT, DATA, FIGURES and both handoffs point to 17e.
- **Remove from the open points above:** the 16–17 Nov batch list (checked against all transcripts by Pablo's searches: nothing decided is missing); faults on the mechanism map (for the paper, later); `paper/CATALOG_SECTION_draft.md` (later).
- **Still open:** `mw_src` shows the rule's source where an A6 row set Mw (Las Melosas rm2018, Pichilemu isc); one line in `magnitude.A6_ALSO` (`"mw": {"mw_kind": "a6", "mw_src": "a6"}`) fixes it at the next run.
- **Commit:** as the entry above, plus `catalog/frozen/2026-11-17e/ REFERENCES.md` and `catalog/figs/catalogue/2026-11-17e/`; message: `CAT: final catalogue 2026-11-17e (overrides, ISC-GEM literature mechanisms, Valdivia mechanism, three 1960 interface events), catalogue figures, plots module, family class colours`
- **Final freeze 2026-11-17f (17 Nov):** `magnitude.A6_ALSO` also sets `mw_src = a6` (test extended); run 2026-11-17f is identical to 17e except `mw_src` on the 9 events with an A6 Mw (Las Melosas, Pichilemu 15:06, 1543, 1949-04-20, 1959-06-14, Aysén 1960, 1971-05-08, 2010-02-27 08:25, 2011-01-07). Frozen in `catalog/frozen/2026-11-17f/`; figures in `catalog/figs/catalogue/2026-11-17f/`; CURRENT, DATA, DECISIONS, FIGURES and handoffs point to 17f. 137 tests pass. Commit: add `catalog/frozen/2026-11-17f/` and `catalog/figs/catalogue/2026-11-17f/` to the lines above; message ends "… final catalogue 2026-11-17f".

## 2026-11-17 — context conversation: CAT result read, next FITS (Claude, chat)
- Read CAT's entries, `handoffs/2026-11-17_CAT_to_FITS.md`, `_CAT_to_CR_HAZ.md`, DECISIONS (Catalog, Figures) and CURRENT: final catalogue `2026-11-17f` is in CURRENT, fits and models still on 16c until FITS refits.
- Possible duplicates in 17f (same earthquake under two ids, A3 matching): 30 pairs within 5 s and 0.5°. In 18 of them one copy has no Mw, so it counts in no fit. In 9 both copies have a Mw and at least one is ≥ 4.5: 2010-03-10 09:04 (ISC 5.1 / Potin 5.5), 2014-04-03 03:11 (ComCat 5.6 / Potin 5.1), 2017-04-24 21:38 (EHB 5.2, 3.6 s before the Potin Mw 6.9), 2020-06-29 05:06, 2025-05-02 13:09 (Drake Passage), 2025-09-04 04:10 (two ISC 5.9), 2025-11-13 09:04, 2026-09-09 10:06, 2026-09-25 15:29. Most are 2025–26, from the not yet reviewed ISC bulletin. Some may be real doublets in aftershock sequences; each needs a check of the source ids. Effect on the fits about 0.1 % of the events of Mw ≥ 4.5. (Replaces a first count of two pairs, made with 2 s and 0.1°.)
- PLAN: A10 (final catalogue) and E17 (verdicts) ticked; B15 refit on 17f is the current step (←).
- For FITS (runbook step 3): refit on `2026-11-17f` (full, declustered with both `gk_family` and `nn_family` while the team decides, pad tables); check the `nn_family` implementation before the refit (DECISIONS, Statistics, 17 Nov); no outer-rise or Scotia unit; the 1907-01-19 Magallanes reference event in the crustal fit figure (CAT handoff). Per unit against 16f in the WORKLOG: b, N(≥ 6), N(≥ 7), Mmax, corner; expect small moves in forearc (Pichilemu 2010 Mw 6.2), the units of the 14 events of 1962–1970 that changed class, shallow in-slab (Chillán 1953) and the interface units of the three 1960 events.

## 2026-11-17 — context conversation: CAT task A11, duplicates before the refit (Claude, chat)
- **Why:** 17f still holds earthquakes listed twice under two ids. A3 flagged every one of them on 11 Nov in its review lists, which went to A6 and were never decided (A3 close: review lists handed on; `possible_splits` question unanswered). Pablo, 17 Nov: fix before FITS.
- **Task for CAT (A11):**
  1. Work through `catalog/merged/review/close_events_m45_2026-11-11.csv` (33 pairs) and `possible_splits_2026-11-11.csv` (7 pairs), against the events of `catalog/frozen/2026-11-17f/`.
  2. Per pair, decide from the source records whether it is one earthquake or two: shared ISC event id or the same agency origin, ComCat / CSN listing them as one, magnitudes and phases. Within an aftershock sequence two events seconds apart can be real (e.g. 2014-04-01 23:57:58 / 23:58:04 have their own EHB origins); keep them.
  3. A duplicate gets an existence row in `overrides_A6.csv` (the copy with fewer sources or no Mw goes; keep the better-located record's event), source and reason in the row. Write the decisions per pair in `catalog/A6/duplicates_2026-11-17.md`.
  4. Pairs found by the context check that the lists must cover (all within 5 s and 0.5°, both with a Mw, one ≥ 4.5): 2010-03-10 09:04, 2014-04-03 03:11, 2017-04-24 21:38 (EHB 5.2 3.6 s before the Potin Mw 6.9), 2020-06-29 05:06, 2025-05-02 13:09, 2025-09-04 04:10 (two ISC 5.9), 2025-11-13 09:04, 2026-09-09 10:06, 2026-09-25 15:29; also 2026-07-06 16:15. If one of them is in neither list, decide it too.
  5. Run the chain (locate, magnitude, locate, classify, checks, pytest), freeze the next free date as the final catalogue with SHA256SUMS and DECISIONS_NOTE; CURRENT, DATA, DECISIONS (Catalog: how many removed, Pablo, 17 Nov, CAT); update `handoffs/2026-11-17_CAT_to_FITS.md` to the new date; WORKLOG with removed events per class and Mw ≥ 4.5 totals against 17f.
- `ambiguous` (102) and `same_source` (82) are matches A3 made; not part of this task.
- PLAN: A11 is the current step; B15 refits on the catalogue CURRENT.md names after A11.


## 2026-11-17 — FITS: B15 part 1, `nn_family` check and scripts ready for the refit (Claude Code, FITS)
- **`nn_family` against Zaliapin and Ben-Zion (2013):** proximity, parent, threshold and largest-event mainshock as in the paper; per family and the historical span are our choices (DECISIONS). Two deviations fixed in `fits/decluster.py`: times now carry the seconds (38 same-minute pairs, 24 in the wrong order), and an event at the same time is no parent (η infinite for t_ij ≤ 0; was floored at 1e-7 yr). On catalogue 16c: 7 flags change, mainshocks 10 921 → 10 922. `fits/DECLUSTER.md` section 12. New test; `pytest fits/tests` 32 pass.
- **Catalogue from CURRENT.md:** `gr.CAT = gr.current()` reads the row "frozen catalogue (final)"; every script reads it through `gr.load`. It now points to 17f. Do not run before A11 has frozen its catalogue and changed that row.
- **Dates:** `run.py` and `run_declustered.py` `DATE = "2026-11-17"` (fits tables), `decluster.py` `DATE = "2026-11-17"` (declustered catalogues; `run_declustered.DC_DATE` follows it), `run_pad.py` takes `run.DATE`. No 2026-11-17 file exists in `fits/tables/` or `catalog/declustered/`.
- **Figures 16f** copied to `fits/figs/2026-11-16f/` (the nine run figures and `arc_regions_2026-11-16f.png`).
- **1907 Magallanes** (CAT handoff): `figs.REF_EVENTS` draws M 5.5 as an open triangle with a label in the Patagonia panel of `fmd_classes.png`, not in the fit. Not yet seen on a figure; drawn at the refit.
- **Part 2 waits** for A11 (not on 17f): `OMP_NUM_THREADS=1 python decluster.py`, `python run.py`, `OMP_NUM_THREADS=1 python run_declustered.py`, `python run_pad.py`, from `psha_chile8/fits/`.
- **Commit (from `psha_chile8/`):** `git add fits/gr.py fits/decluster.py fits/run.py fits/run_declustered.py fits/figs.py fits/tests/test_decluster.py fits/DECLUSTER.md fits/figs/2026-11-16f WORKLOG.md`; message: `B15 part 1: nn_family checked against Zaliapin and Ben-Zion 2013 (seconds, no parent at t_ij <= 0); fits read the catalogue from CURRENT.md; dates 2026-11-17; 16f figures kept`

## 2026-11-17 — FITS: B15 dry run on 17f (trial, not used), figures, team evidence, FITS.md final form (Claude Code, FITS)
- **Trial, not used.** All four scripts ran end to end on 17f through `drafts/fits/trial.py` (date "trial", every output in `drafts/fits/trial/`: `declustered/`, `tables/`, `figs/`, logs). No CURRENT or DATA line. Nothing broke; the scripts needed no fix to run on a new catalogue. Changes made for the final run: `run.py` and `run_declustered.py` write figures to `fits/figs/<DATE>/` (FIG = `figs/DATE`, the save functions create it); the trap "figures overwrite the last run" is gone.
- **17f against 16f** (`drafts/fits/compare_16f.py`, tables `drafts/fits/trial/tables/compare_*16f_trial.csv`): no unit moves more than one sd in b or 10 % in N(≥ 6), full or declustered (gk_family, nn_family, own and shared b). Largest moves, tapered:
  - in-slab shallow b 1.144 → 1.131, N(≥ 6) +3.9 %, N(≥ 7) +7 %, observed Mw ≥ 7 8.3 → 8.7 (Chillán 1953 to in-slab);
  - interface 45.6–37° S observed Mw ≥ 7 9.9 → 11.0 (three 1960 events to interface), b −0.003;
  - interface and the other segments N(≥ 6) −0.6 to −1.2 %; crustal family b 1.009 → 1.005, every crustal class N(≥ 6) +1.0 to +1.4 %; intermediate in-slab and Jujuy nest identical;
  - declustered: interface 45.6–37° S b +0.023 (gk_family) and +0.025 (nn_family), N(≥ 6) −8.5 %; shallow in-slab N(≥ 6) +4.6 % and +5.0 %. Mmax and corners unchanged everywhere (forearc stays 7.2: Pichilemu 14:55 Mw 7.0 is its largest weight-1 event).
  - The same two failures (interface 32–26° S 17.2 / 9.9; intermediate in-slab 17.9 / 28.5); nn_family also fails intermediate in-slab, as before.
- **Both declusterings** stay in every output (decluster, declustered fits, figures, FITS.md, team figures). nn_family mainshocks on 17f: 10 922 of 14 279 (threshold log10 η −5.74); gk_family 6 010.
- **Figures in the shared style** (`fits/figs.py`, `figs_declustered.py`): no titles (unit tag in a corner), pituPLOTS `darkgrid` (commit c71a937), `palette.CLASS_COLOR` per unit and `FAMILY_COLOR` for the crustal family, the M ≥ 7 band in `BAND["M ≥ 7"]` red, one legend row below the axes, no code names. 1907-01-19 Magallanes M 5.5 drawn as a reference event in the Patagonia panel of `fmd_classes.png`. Trials in `drafts/fits/trial/figs/`.
- **Team evidence** (`drafts/fits/team/`, script `team_figs.py`, on the trial outputs):
  - `interface_32_26_b.png`: observed N(≥ M) against own b 0.94 and shared b 0.958; Mw ≥ 7 observed 9.9, own b 17.2, shared b 15.8 (passes); Mw ≥ 8 2.6 / 4.9 / 4.4.
  - `declustered_rates.png`: N(≥ 5, 6, 7) declustered over full per interface unit and in-slab class. Gardner–Knopoff keeps 17–37 % of the interface N(≥ 5) and lowers b by 0.13–0.34; nearest neighbour keeps 39–57 % and lowers b by 0.01–0.11; in-slab, GK raises N(≥ 7) (× 1.27–1.76) through its lower b, NN keeps it (× 0.98–1.00).
  - `gk_nn_sequences.png`: Valdivia 1960, Maule 2010, Iquique 2014, Illapel 2015. Removed by both 31 / 870 / 245 / 351; by GK only 4 / 210 / 37 / 56; by NN only 9 / 33 / 1 / 5.
- **FITS.md** rewritten to its final form (method as the final run does it, for the paper's statistics section; trial numbers marked to be replaced; the two failures with numbers; declustered and pad summaries; σ, methods and synthetic recovery condensed). The run history 15–16 Nov is kept as `fits/FITS_history.md`.
- Tests: `pytest fits/tests` 32 pass. DECISIONS changed during the session (Catalog and Figures lines of CAT); nothing in Statistics or Interface, so the fits rules hold.
- **Part 2 commands** (after A11 has changed the row "frozen catalogue (final)" in CURRENT.md). From `psha_chile8/fits/`, conda `psha_renta`; dates already `2026-11-17` in `decluster.py`, `run.py`, `run_declustered.py` (`run_pad.py` follows `run.DATE`); if the run happens on another day, set the next free date in those three first:
  1. `python -c "import gr; print(gr.CAT)"` (must print the A11 catalogue, not 17f)
  2. `OMP_NUM_THREADS=1 python decluster.py` (4 min; `catalog/declustered/*_2026-11-17.csv`)
  3. `python run.py` (2 min; stops if the automatic table differs from DECISIONS)
  4. `OMP_NUM_THREADS=1 python run_declustered.py` (3 min)
  5. `python run_pad.py` (15 s)
  6. `cd .. && python drafts/fits/compare_16f.py fits/tables 2026-11-17` (per unit against 16f)
  7. `cd fits && python ../drafts/fits/team/team_figs.py` with `FINAL = True` at its top (team figures on the final run)
  8. `cd .. && pytest fits/tests`
  Then: numbers into FITS.md, CURRENT.md (fits, declustered, table, pad, "catalogue the fits and models are built on"), DATA.md rows, WORKLOG with b, N(≥ 6), N(≥ 7), Mmax, corner per unit against 16f, `handoffs/2026-11-17_FITS_to_IF_IS_CR.md`.
- **LEARNINGS proposals:** (1) Nearest-neighbour declustering needs times to the second; to the minute, events in one minute come out of order and link at a floored time. (2) A test that draws its synthetic pool from the real catalogue in load order breaks when the load order changes; keep such changes out of `gr.load`.
- **Commit (from `psha_chile8/`):** `git add fits/gr.py fits/decluster.py fits/run.py fits/run_declustered.py fits/figs.py fits/figs_declustered.py fits/tests/test_decluster.py fits/FITS.md fits/FITS_history.md fits/DECLUSTER.md fits/figs/2026-11-16f WORKLOG.md`; message: `B15 before the refit: nn_family checked against Zaliapin and Ben-Zion 2013; fits read the catalogue from CURRENT.md, figures to figs/<date>/, shared figure style, 1907 Magallanes reference; FITS.md in final form (history in FITS_history.md); dry run on 17f in drafts/fits (not committed)`

## 2026-11-17 — FITS: crustal own b and Jujuy nest, exploration (Claude Code, FITS)
- Drafts only, `drafts/fits/crustal_nest/` (`explore.py`, `crustal_own_b.png`, `nest.png`; catalogue 17f). Nothing in `fits/` changed.
- **Crustal classes with their own b:** forearc 0.92 ± 0.06 (b-positive 0.94; N(≥ 6) × 1.24 against the family b 1.00), arc 1.05 ± 0.10, backarc 1.26 ± 0.38, Patagonia 1.66 ± 0.47. Forearc and arc could hold their own b; backarc and Patagonia cannot. The family b stays (DECISIONS, 16 Nov) unless Pablo reopens it.
- **Jujuy nest:** b 1.23 / 0.92 / 0.74 from Mw 5.0 / 5.5 / 6.0. Since 1976 the converted magnitudes (87 ISC ML, 28 mb) give b 1.96 and the direct Mw 0.89; the in-slab classes show the same split by selection, so a paired check is needed. Pablo: ask CAT → `handoffs/2026-11-17_FITS_to_CAT.md`. The nest refit waits for CAT; a floor of 5.5 for the nest is not taken.
- **Completeness** stays where it is (`fits/table.py`, one table for every class).

## 2026-11-17 — FITS: completeness table checked before the fits (Claude Code, FITS)
- Drafts only, `drafts/fits/completeness/` (`completeness.py`: `table.png`, `periods.png`, `segments_large_in_time.png`; `tables_test.py`: `tables_test.csv`; catalogue 17f). Nothing in `fits/` changed.
- **Observed against fitted per period and band:** interface 32–26° S lacks Mw 7.0–7.4 in every period, 1976–2026 included (1.0 / 3.3), so that part of its failure is not completeness; Mw ≥ 8 before 1830 is short in the margin (5.7 / 10.8), 32–26° S (0.8 / 3.1) and 26–17.6° S. 1964–1975 is short at Mw 5–6.9 in the interface (× 0.76, × 0.56), 37–32° S (× 0.40, × 0.28), intermediate in-slab (× 0.67, × 0.29) and the nest (× 0.36); short at 6–6.9 too, so not detection alone (magnitudes of that period, or the 1976–2026 sequences setting the rate). Mc windows agree with the instrumental steps.
- **Refit with one table for every class, two steps changed** (tapered; ratio to the current fit; Mw ≥ 7 fitted / observed):
  - "8.0 from 1830" (step 8.0 from 1500 dropped): 32–26° S passes (15.6 / 9.2); interface b 0.961 → 0.947, N(≥ 7) × 1.07, N(≥ 8) × 1.10; segments N(≥ 8) × 0.95–1.23.
  - no "5.2 from 1964" step: intermediate in-slab passes (22.0 / 28.8); N(≥ 6) × 1.13 intermediate, × 1.13 37–32° S, × 1.10 shallow, × 1.18 nest, × 1.06 interface; b −0.01 to −0.04.
  - both: intermediate passes, 32–26° S fails again (15.9 / 9.2); interface N(≥ 7) × 1.18, N(≥ 8) × 1.25.
- Both changes are against the automatic table of DECISIONS (Statistics); a change would be a change of the rule, for Pablo. Nothing proposed as a decision yet.
- **The 1964 step, explained (same day):** yearly rates of all events in the domain, Mw 5.2–5.9 / 6.0–6.9: 1964–1975 33.8 / 4.2, 1976–1989 42.9 / 6.2, 1990–1999 31.8 / 4.2, 2000–2009 42.1 / 5.5, 2010–2026 54.2 / 9.7. Declustered (gk_family) Mw 5.2–5.9: 20.2, 22.4, 20.0, 20.8, 19.8 (nn_family 27.5–34.7). 1964–1975 is as complete as the 1990s; its "shortfall" is against a rate raised by the sequences (1985, 2010–2015). The step stays; dropping it only lets the sequence years set more of the rate.
- **Proposal for Pablo (not decided):** keep full-catalogue rates and the table, and bootstrap clusters instead of events (resample whole `nn_family` clusters, mainshock with its aftershocks), so the intervals and the large-event band carry the clustering (Fano factors in `declustered_compare_*`). Change in `gr.fit` / `gr.boot`; one rule for every unit, no setting.

## 2026-11-17 — FITS: cluster bootstrap, and the completeness table on declustered catalogues (Claude Code, FITS)
- **Implemented (Pablo: "implement it"):** `gr.fit(..., cl=)` draws whole clusters in the bootstrap; `gr.dispersion` and `gr.band` give the large-event band (negative binomial with the cluster dispersion; Poisson without clusters); `run.CLUSTER = "nn_family"` and `run.clusters()` read the clusters from the declustered file of `decluster.DATE`, used by `run.py`, `run_declustered.py`, `run_pad.py`; `fits_*.csv` has new columns `phi7`, `phi8`; `figs.fig_check` draws the new band. Tests `fits/tests/test_cluster.py` (3); 35 pass. `compare.py` sensitivity rows keep the Poisson band (no clusters passed).
- **Trial on 17f** (event-bootstrap tables kept in `drafts/fits/trial/event_bootstrap/`): b unchanged. Bootstrap sd of b and the N intervals widen in the interface units (N(≥ 7) 95/5 ratio: margin 1.32 → 1.71, 45.6–37° S 2.15 → 6.30, 37–32° S 1.69 → 2.84, 26–17.6° S 1.80 → 3.01; dispersion at Mw ≥ 7: 1.68, 3.87, 1.00, 1.01, 1.42). In-slab and crustal under 15 %. The two failures stay: 32–26° S (dispersion 1.01) and intermediate in-slab (1.00) have no clustering among their large events, so they are real.
- **Is it common?** The pieces are (cluster bootstrap for dependent data; compound-Poisson counts); applying them to a full-catalogue Weichert fit is our proposal. Literature on full against declustered rates: Marzocchi and Taroni (2014, BSSA 104, doi 10.1785/0120130300), Taroni and Akinci (2021, GJI 224, 1174–1187, doi 10.1093/gji/ggaa462). DECISIONS line to write only when Pablo confirms.
- **Completeness table read on the declustered catalogues, fits on the full catalogue** (`drafts/fits/completeness/declustered_table_test.py`, `.csv`; gk_family table 5.0 / 1976, 5.1 / 1964, 6.5 / 1890, 7.0 / 1825, 8.0 / 1500; nn_family the same with 1900 and 1830): **both failures pass** (32–26° S 18.3 / 11.8 and 18.5 / 11.8; intermediate in-slab 22.0 / 30.2 and 22.0 / 30.2), all other units pass. b +0.02 to +0.04; N(≥ 6) × 0.87–0.95, N(≥ 7) × 0.79–0.92, N(≥ 8) × 0.72–0.87. Caution: the rate rule already puts historical steps early on synthetic catalogues (FITS.md section 9); the declustered tables are earlier still, and a passing check does not validate a table. Rule change for Pablo; nothing in DECISIONS.
- **Decided (Pablo, 17 Nov, FITS), written into DECISIONS (Statistics, Superseded):** keep the completeness table of the full catalogue; the cluster bootstrap and its band.
- Commit addition (from `psha_chile8/`): `fits/gr.py fits/run.py fits/run_declustered.py fits/run_pad.py fits/figs.py fits/tests/test_cluster.py fits/FITS.md DECISIONS.md WORKLOG.md`; message: `FITS: bootstrap of whole nn_family clusters, negative binomial band for the large-event check; completeness table kept`

## 2026-11-17 — FITS: historical completeness rule against the literature (Claude Code, FITS)
- Read `refs/catalogs/hakimhashemi_gruntal_2012.pdf` and `albarello_2001.pdf` (rows added to REFERENCES, section D).
- **Hakimhashemi and Grünthal (2012):** per magnitude class, the sample variance of interevent times as events are added back in time; the completeness time is where consecutive variances stop differing (F-test p > 0.75, or Siegel–Tukey p > 0.9). No rate model, works for non-stationary rates; the confidence level is a free choice; on synthetic catalogues it fails when only 25 % of the early events are missing (p. 2533).
- **Albarello et al. (2001):** per class, the span back from the present is cut into 2N equal subintervals and the rates of the early half are compared with the late half by a sign test (binomial, p = 0.5; eq. 2); P(C) is weighted by the span (eq. 5, insensitive to k) and the completeness time is where it peaks. Distribution-free, no aftershock removal, no Gutenberg–Richter line.
- **Our rule (`table.historical`)** is neither: a Poisson change point in the 5-year-block counts of each 0.5 band, against the rate the instrumental Gutenberg–Richter line predicts for that band, with a BIC penalty. Closest published relative: the change-point method of Rotondi and Garavaglia (2002), as summarised by Hakimhashemi and Grünthal (p. 2531; not read). Its two assumptions, that the instrumental line holds up to Mw 8 and that rates are stationary Poisson, are those both papers avoid; the second is the one the sequences break.
- **Proposal (not done):** run the Albarello test per band as an independent check of the historical steps (no free setting that matters; same data). If it agrees, the paper cites it as the check; if not, the steps need another look.
- **Hakimhashemi and Grünthal (2012) implemented and tested** (`drafts/fits/completeness/hg2012.py`, `hg2012.png`, `hg2012_synthetic.csv`, `hg2012_real.csv`). Their rule as written (variance of interevent times back from the present, F-test of consecutive variances at 0.8; Siegel–Tukey at 0.9; first 10 intervals not tested; monotone across bands); bands [mf, mf + 0.5) to match our steps.
  - Synthetic catalogues (100 per detection model, known table): F-test median error +20 / 0 / −3 to −21 / −20 to −59 / +7 years for bands 6.0, 6.5, 7.0, 7.5, ≥ 8; 10–90 % within about ± 60 years up to 7.0, wider at 7.5 (−180 to −325 in the tail). Less biased than our rule at 7.0 (ours 30–75 years early). Siegel–Tukey between the nested sets, as we read the paper, has no power (100–370 years early); not usable in this reading.
  - Real catalogue, whole margin, F-test 0.8: 7.0 from 1904 and 7.5 from 1834 (our table 1905, 1830), stable over levels 0.7–0.9, full or declustered (gk_family, nn_family); 8.0 from 1819 (ours 1500), unstable (1513–1823 over level and band edges); 6.0 and 6.5 from 1919 but 2000–2006 with band edges moved by 0.1 (sequences), unstable. Per region the times scatter widely (too few events).
  - Read: H&G confirms our 7.0 and 7.5 steps; it does not support "8.0 from 1500" (the same finding as the period diagnostic). Their paper advises historical methods for the sparsest classes (Stucchi et al. 2004), which fits the 8.0 step.
- **Albarello et al. (2001) implemented and tested** (`drafts/fits/completeness/albarello2001.py`, `albarello2001.png`, `albarello_synthetic.csv`, `albarello_real.csv`): sign test of early against late subinterval counts, P_i ∝ span × P(C|R), completeness time = median of P*, interquartile range as uncertainty; cumulative classes Mw ≥ mf; subinterval DT not stated in the text, tested 5 / 10 / 20 years.
  - Synthetic (100 per detection model): ≥ 6.0 within 3–17 years; ≥ 6.5 and ≥ 7.0 7–38 years early (median); ≥ 7.5 53–123 years early; ≥ 8 127–157 years late. For a class this sparse P(C|R) is near 1 at every start, the span weight then puts the median about 1/√2 of the span back (≈ 1650–1700) whatever the data: uninformative for Mw ≥ 8.
  - Real, whole margin, stable over DT and declustering: ≥ 7.0 from 1907 (IQR about 1870–1947; ours 1905, H&G 1904); ≥ 7.5 from 1907–1917 (ours 1830, H&G 1834); ≥ 8 from 1707–1787 (IQR 1587–1847), at the level the method gives for any sparse class; ≥ 6.0 and 6.5 1907–1957 (the instrumental steps decide there).
  - Read: both referenced methods confirm "7.0 from 1905". Neither supports "8.0 from 1500" (H&G 1819, unstable; Albarello cannot resolve the class). On 7.5 they part: H&G 1834, Albarello about 1907.
- Table not changed yet (Pablo: "wait").
- **Table written (Pablo, 17 Nov, FITS):** Mw 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830 (Mw ≥ 8 included); "8.0 from 1500" dropped. `run.TABLE` changed; `run.py` now asserts only the instrumental steps against the automatic table, runs `table.checks` (new `table.hg2012`, `table.albarello2001`) and writes `tables/table_checks_<date>.csv` (both methods, the automatic rule, the table). On 17f: H&G 1919 / 1919 / 1904 / 1834 / 1819 and Albarello 1947 / 1947 / 1907 / 1907 / 1767 for Mw 6.0 / 6.5 / 7.0 / 7.5 / 8.0. New test `test_published_checks_find_a_known_start`; 36 pass. Justification in `fits/FITS.md` section 2 (table, synthetic behaviour, each step, the discussion paragraph for the paper); DECISIONS Statistics and Superseded lines written.
- The trial numbers in FITS.md sections 4–5 are still of the old table; part 2 replaces them. `synth.TABLE` (the true table of the synthetic catalogues) is left as it was.
- Commit addition: `fits/table.py fits/run.py fits/tests/test_table.py fits/FITS.md REFERENCES.md DECISIONS.md WORKLOG.md`; message: `FITS: completeness table without the step 8.0 from 1500; published checks of the historical steps (Hakimhashemi and Grünthal 2012, Albarello et al. 2001) written by every run`
- **Mc measured, not set (Pablo: "measured, not argumentative"):** `drafts/fits/completeness/mc_maps.py` (Mc on 1° nodes per window, same estimators; `mc_maps.png`, `mc_nodes.csv`, `mc_regions.csv`) and `floor_test.py` (`floor_test.csv`). Median node Mc 4.2 since 2012; with no floor the rule gives 4.4 from 2020 and 4.7 from 2012 for the whole margin. Fitting on that table moves b by more than 2 sd in six units and N(≥ 7) by × 0.30–2.46 (new check failures at 37–32° S and the nest). FITS.md section 2 now states the measured Mc and why the fit floor is 5.0 (b-stability of the fits), replacing "Mw 4.5–4.9 complete in no period".
- **Proposed DECISIONS correction (Statistics, line of 15 Nov "Mw 4.5–4.9 is complete over the whole margin in no period"):** "Mc measured per window and node (median 4.2 since 2012; whole margin 4.4 from 2020, 4.7 from 2012); the fits start at Mw 5.0, the lowest floor at which b is stable (fits on the measured table move b by more than 2 sd in six units)." Waiting for Pablo.
- **Mc in time** (`drafts/fits/completeness/mc_time.py`, `mc_time.png`, `mc_time.csv`; moving windows of 500 events for the margin and 250 per region, step 100 / 50, bootstrap 30, same estimators): whole margin Mc 5.0–5.2 in 1970–1992, 4.8 around 1990, 4.2–4.5 from about 1995–1997, about 4.0 from 2010, with spikes after the 1985, 2010, 2014 and 2015 mainshocks (5.4 right after Maule). The same drop around 1995 in north, central-north and central; the south about 0.3 higher until 2010; the far south has enough events only from 2015 (4.4–4.7). The windows of 1964–1969 read 4.0–4.3, below 1970–1990: suspect (few events below Mw 5 in that period and a different magnitude mix), not read as completeness. The fixed network windows of `table.py` (1990–2000 etc.) smear the 1995 drop; a window by number of events does not.
- **Fit floor by b-stability of the fits** (`fit_floor.py`, `fit_floor.png`, `fit_floor.csv`; measured table 4.4 / 2020, 4.7 / 2012, 5.0 / 1976, 5.2 / 1964 and the historical steps; Cao and Gao rule on the Weichert fits): interface 4.5, 45.6–37° S 4.4, 37–32° S 4.7, 32–26° S 4.4, 26–17.6° S 4.5, shallow in-slab 4.8, intermediate 4.4, Jujuy nest 5.1 (b falls all the way from 1.53 at 4.4 to 0.76 at 6.0: no plateau), crustal family 4.6.
- **Proposed next step (not done):** instrumental steps from Mc(t) instead of fixed windows, with the incompleteness right after large mainshocks handled by a published model rather than by the window rule; fit floor per unit by the b-stability of its own fits. Waiting for Pablo.
- **Mc(t) per segment, envelope, in the code (Pablo: "analysis per latitude segment, a table that envelopes all segments"):** `table.py` now measures Mc(t) per interface segment (`SEG`, windows of 250 events, step 50, bootstrap 30, Pool of 16; 91 s), steps per segment from the last window above a magnitude beyond one bootstrap sd, envelope over the four (`mc_series`, `steps_series`, `envelope`, `cut`); `run.py` writes `mc_series_<date>.csv`, `mc_table_<date>.csv`, `table_checks_<date>.csv` and `figs/<date>/mc_time.png` (`figs.fig_mc`). `run.table_of` now moves steps before a unit's `since` to that year instead of dropping them (no change to the crustal tables: still 5.0 from 1976). `mc_windows_` and the fixed network windows are no longer written. Tests: `test_mc_series_on_a_known_table` replaces the old automatic-table test; 36 pass.
- **Result on 17f:** envelope 5.2 from 1964, 4.7 from 1999, 4.4 from 2011, 4.2 from 2017, 4.1 from 2019 (per segment in FITS.md section 2). For the fits from Mw 5.0 it means 5.0 from 1999; the south sets it.
- **Synthetic check of the rule:** where Mc sits near 5.0 the last-window rule puts the 5.0 step late in two of four catalogues (1977, 1999 for a true 1976). Because of that `run.TABLE` keeps 5.0 from 1976 for now and `run.py` no longer stops when the measured steps differ; both are written. Decision for Pablo: 5.0 from 1976 or 1999 (effect: interface b +0.03 to +0.06, N(≥ 7) × 0.83–0.93).
- **Trial rerun on 17f with the table 5.0 / 1976, 5.2 / 1964, 7.0 / 1905, 7.5 / 1830 and the cluster bootstrap** (`drafts/fits/trial/`, log_5): against 16f no unit beyond 1 sd in b or 10 % in N(≥ 6); interface b 0.959 → 0.947, N(≥ 7) × 1.06; segments N(≥ 7) × 0.95–1.15; 32–26° S now passes (15.6 / 9.2); intermediate in-slab still fails (17.2 / 28.5).
- **Fit floor 5.8 against 5.0, and local b** (`drafts/fits/completeness/floor58.py`, `floor58.png`, `floor58.csv`, `local_b.png`, `local_b.csv`; trial 17f, table 5.0 / 1976, cluster bootstrap): interface margin b 0.95 → 0.91 (sd 0.03 → 0.06), N(≥ 7) × 1.09, N(≥ 8) × 1.18; segments b −0.09 to +0.02, N(≥ 8) × 0.91–1.50 (26–17.6° S); every interface check passes either way. Intermediate in-slab b 1.15 → 0.95, N(≥ 7) × 1.53, N(≥ 8) × 2.14, and its large-event check passes (27.7 / 30.6); Jujuy nest b 1.23 → 0.73, N(≥ 7) × 2.9; shallow in-slab 1.13 → 1.06; crustal family 1.00 → 1.07 (sd 0.13). Local b (Weichert on [M, M + 1), cluster bootstrap): interface 0.9–1.0 from 5.0 to about 6.3, then noise; intermediate in-slab 1.2 at 5.0–5.5 falling to 0.9–1.0 by 5.8–6.0; nest 1.4 → 0.5–1.0; crustal 1.05 → about 0.85 by 5.6. The bend below 5.8 is in the in-slab classes and the crustal family, not the interface; it coincides with the converted magnitudes (handoff to CAT). No decision.

## 2026-11-18 — FITS: reply to CAT on the magnitudes (Claude Code, FITS)
- Read `handoffs/2026-11-18_CAT_to_FITS.md`: nest conversions fixed (third depth group below 150 km, every scale within ± 0.1 of measured Mw at every depth), nest b unchanged (1.45 → 1.46); b against the floor flat at about 1.0 from 4.5 to 7 since 1976 for converted and native magnitudes. Pablo: "the Mw transformation work looks good".
- Reply `handoffs/2026-11-18_FITS_to_CAT.md`: nothing needed from the catalogue; freeze 17g. The in-slab bend below Mw 5.8 is not magnitudes and not class weights (weight-1 b the same); the fit floor is open for Pablo.
- **Great interface events by segment** (Pablo: Valdivia and Concepción founded about 1550, an Mw ~8 should be recorded since): Mw ≥ 8 per century, 1550–1829 against 1830–2026: 37–32° S 1.79 against 1.52 (1570, 1657, 1730, 1751, 1822; then 1835, 1906, 2010); 45.6–37° S 0.36 against 1.52 (1575 only; Valdivia was abandoned 1599–1645); 32–26° S 0.36 against 1.02 (1819 only); 26–17.6° S none against 1.52. Arica 1513, 1604, 1868 are north of 17.6° S (margin unit only). So the central segment is complete for Mw ≥ 8 since about 1550, the other segments only from about 1830: completeness of great events varies along strike, and one margin-wide table must take the latest. Fitted recurrence (tapered): margin Mw ≥ 9 249 years, ≥ 9.5 about 1 400 years; 45.6–37° S Mw ≥ 9 about 1 150 years, ≥ 9.5 about 6 200 years, far longer than the paleoseismic interval of 1960-type events (about 300 years, Cisternas et al. 2005, to check). Proposal for Pablo: a historical step per segment for the four segments (37–32° S Mw ≥ 8 from 1550, the others from 1830), the margin unit on the envelope (1830).
- **Settlement along the margin (web, 18 Nov; sources in the chat answer):** Arica 1541 (Villa San Marcos de Arica), Santiago 1541, La Serena 1544, Valparaíso port 1544 (bay 1536), Concepción 1550, Valdivia 1552, destroyed 1599, repopulated 1645; Copiapó 8 Dec 1744 (Memoria Chilena); Antofagasta 1868 and Iquique as a town in the 19th century (from memory, not confirmed in the search). Proposed Mw ≥ 8 completeness per interface segment from the settlement record: 37–32° S from 1550; 45.6–37° S from 1645; 32–26° S from 1744; 26–17.6° S from about 1868 (or 1830 if the tsunami record of Arica and Cobija is taken as enough); margin unit on the envelope. The two published checks were run on the whole margin, which mixes these histories; per segment there are 1–5 events before 1830, too few for either method. Waiting for Pablo.
- Pablo adds Castro (Chiloé, about 1550; founded 1567 as I remember, to confirm). With Castro and Concepción continuously settled, 45.6–37° S is covered through Valdivia's gap of 1599–1645: its Mw ≥ 8 step moves from 1645 to about 1567.
- **Mw ≥ 8.5 complete from 1604, margin-wide** (Pablo: Peru records from 1604; the only coastal gap is Arica to Valparaíso; `drafts/fits/completeness/table_85_1604.py`, `.png`): table 5.0 / 1976, 5.2 / 1964, 7.0 / 1905, 7.5 / 1830, 8.5 / 1604. Mw ≥ 8.5 interface events: 1604, 1730, 1751, 1819 before 1830 (1.8 per century), 1837, 1868, 1877, 1922, 1960, 2010 after (3.0), consistent within Poisson. Effect: margin b 0.947 → 0.946, N(≥ 8) × 1.01; segments b −0.01 to +0.01, N(≥ 7) × 0.95–1.07; every check passes (margin Mw ≥ 8.5 5.1 fitted / 7.8 observed); the Valdivia point at 9.5 halves (counted over 423 years). Waiting for Pablo.
- **Decided (Pablo, 18 Nov, FITS): completeness step Mw 8.5 from 1550.** `run.TABLE` = 5.0 / 1976, 5.2 / 1964, 7.0 / 1905, 7.5 / 1830, 8.5 / 1550; DECISIONS (Statistics) and FITS.md section 2 written with the justification (start from the record, not from an event; variants 8.3 / 1575, 8.5 / 1604, 8.3 / 1550 and 8.0 / 1500 compared). Figure `drafts/fits/completeness/interface_85_1550.png`. Tests 36 pass. The trial on 17f is not rerun with it (part 2 runs on 17g).
- Commit addition: `fits/run.py fits/FITS.md DECISIONS.md WORKLOG.md handoffs/2026-11-18_FITS_to_CAT.md`; message: `FITS: completeness step Mw 8.5 from 1550 (historical record of the margin); reply to CAT`
- **Predictive band in the fit figures (Pablo, 18 Nov):** `gr.predictive` (bootstrap replicates × counts drawn per bin over its own time, Poisson or negative binomial with the per-bin cluster dispersion, cumulated from the top; 5–95 %); `figs.fmd` draws it instead of the parameter envelope, cumulative points only, no per-bin points (also in `figs_declustered`). Test `test_predictive_band_holds_the_observed_points`; 37 pass. Trial redrawn on the table with 8.5 / 1550 (`drafts/fits/trial/figs/`, log_7): every interface unit inside its band; intermediate in-slab above the band at Mw 6.5–7.5 (the old magnitudes), the nest above at 6–7, the forearc at the upper edge at 6–6.8. FITS.md section 4 notes the figures.

## 2026-11-18 — CAT: A11 duplicates, depth groups of the conversions, final catalogue 2026-11-17g (Claude Code, CAT)
- **Duplicates (A11, Pablo, 17 Nov):** merged, not removed (the records of a copy join the kept event, one per source). 22 pairs reviewed with Pablo on cards (largest first, then sweeps from Mw 4 and of Mw ≥ 6) in the new `catalog/duplicates.csv` (event, kept event, reference, reason); `overrides_A6.csv` keeps property corrections only. Rule for single-agency ISC copies (`magnitude.LONE_S` 10 s, `LONE_KM` 100 km): 22 events. Historical double entries of Cabello et al. merged: 1833, 1847, 1868-08-13 22:15, 1877-05-10 01:28; 1831-10-08 Arica kept as two. Instrumental Mw ≥ 6 pairs all listed apart by ISC-GEM. Notes: `catalog/A6/duplicates_2026-11-17.md`.
- **Conversions (FITS note on the Jujuy nest):** a third depth group below 150 km (`magnitude.ZNEST`, top of `classify.NEST`), candidate in the cross-validation; taken by GUC ML, SJA ML, ISC mb, NEIC mb. As reported, CSN ML is 0.2 high below 150 km and ISC mb drifts to −0.3 at 250 km; converted, every scale is within ± 0.1 at every depth. The nest b does not move (1.45 → 1.46): its bend is not the conversion. Reply `handoffs/2026-11-18_CAT_to_FITS.md`; FITS answered (`2026-11-18_FITS_to_CAT.md`): nothing more needed, freeze.
- **Magnitude figures (`magnitude_check.py`):** pituPLOTS slides theme, gray background, tol_muted palette (converted Mw indigo, Cabello olive, Candia–Macedo orange, measured Mw black), $M_w$ in labels, no titles. New: `relations_others` (co-authors), `residual_depth`, `residual_converted`, `compare_relations`, `compare_residual_depth`, `compare_residual_converted`; `test1_b_floor` with all four catalogues to floor 6.5 and 95 % bands; rates with 95 % Poisson bars, Mw ≥ 5.0 and 5.5 in one panel; native magnitudes as a reference series. Old set in `catalog/figs/magnitude/before_2026-11-17g/`. Explanations and why the published catalogues fail: `MAGNITUDES.md` section 10. Test figure to floor 7 and the FITS copies in `drafts/cat/mw_check/` (not committed).
- **Run 2026-11-17g (18 Nov, asked by Pablo):** locate, magnitude, locate, classify, the three checks; 140 tests pass. Frozen `catalog/frozen/2026-11-17g/` (SHA256SUMS, INPUTS_SHA256 identical to 17f, DECISIONS_NOTE, code, overrides, duplicates, merged list). Against 17f: 44 events merged (10 of Mw ≥ 4.5 in the domain; two of Mw ≥ 7: 1833 13:00, 1847-10-08), 162 events of Mw ≥ 7; 4 027 events of Mw ≥ 4.5 change by 0.1–0.3, none of Mw ≥ 7. Mw ≥ 4.5 in the domain 14 279 → 14 416; interface 4 497.4 → 4 482.7, in-slab 8 079.8 → 8 231.3 (intermediate 5 389.0 → 5 533.7, events near the 4.5 cut), crustal 1 146.8 → 1 146.0. Since 1976 at Mw ≥ 5.0 intermediate in-slab −2 %, interface −1 %. A5 tests: all pass for this run. Maps redrawn into `catalog/figs/catalogue/2026-11-17g/` (`RUN = "2026-11-17g"` in the three `fig_*.py`).
- DECISIONS (Catalog, Magnitudes, Superseded), CURRENT (final catalogue, overrides, new duplicates row), DATA (row 2026-11-17g), FIGURES, PLAN (A11 ticked, ← on B15), handoff `handoffs/2026-11-18_CAT_to_FITS_17g.md`. DECISIONS changed during the session (FITS: completeness step 8.5 from 1550; Statistics lines): nothing in them touches the catalogue.
- **LEARNINGS proposals:** (1) A converted catalogue compared on events with a measured Mw says nothing: the other catalogue carries that same Mw; compare on events without one, or apply its relation to the same pairs. (2) Native ML and mb drift with depth (CSN ML +0.2 below 150 km, ISC mb −0.3 at 250 km); one relation for all intermediate depths leaves the deepest events biased. (3) A hump of b against the fit floor at 4.5–5.5 is the signature of medium events inflated by a conversion (Cabello, Candia–Macedo); native magnitudes do better than both. (4) Merge duplicates rather than delete them, and keep the reviewed list apart from the property overrides.
- **Commit (from `psha_chile8/`):** `git add catalog/magnitude.py catalog/locate.py catalog/classify.py catalog/magnitude_check.py catalog/duplicates.csv catalog/overrides_A6.csv catalog/tests/test_magnitude.py catalog/tests/test_locate.py catalog/MAGNITUDES.md catalog/A6/duplicates_2026-11-17.md catalog/fig_mechanisms.py catalog/fig_positions.py catalog/fig_classes.py catalog/merged/MANIFEST.csv catalog/figs/magnitude catalog/figs/locate catalog/figs/classify catalog/figs/catalogue/2026-11-17g catalog/frozen/2026-11-17g DECISIONS.md CURRENT.md DATA.md FIGURES.md PLAN.md WORKLOG.md handoffs/2026-11-18_CAT_to_FITS.md handoffs/2026-11-18_CAT_to_FITS_17g.md handoffs/2026-11-18_FITS_to_CAT.md`; message: `CAT A11: duplicates merged (catalog/duplicates.csv, single-agency ISC copies), conversions with a depth group below 150 km, magnitude figures restyled and compared with Cabello and Candia-Macedo; final catalogue 2026-11-17g`. The 17c/17e/17f freezes and the earlier CAT files of 17 Nov (`fig_*.py`, `named_events.csv`, `sources_figs.py`, `figs/catalogue/`, `figs/sources/`, `A6/*_2026-11-17.*`) are still untracked; add them with the 17f commit lines of the entries above if not yet committed.
- **Addendum, figures (Pablo, 18 Nov):** the catalogue figures of the paper and supplement now go straight into `catalog/FIGURES/<type>/`: `maps` (`mechanisms_utm`, `classes_m45/m65`, `positions_m45/m65`; `fig_*.py` write there, no run subfolder), `magnitudes` (the ten FIGURES.md magnitude figures; `magnitude_check.OFFICIAL`, the other test figures stay in `catalog/figs/magnitude/`), `rules` (`catalog_rules.png` from `catalog/figs/rules/rules_fig.py`, shared font and palette, depth groups and duplicate merging added). A collector script for all parts was tried and dropped (an extra step). The 17g figures were moved, not redrawn; `figs/catalogue/2026-11-17g/` removed (older run folders kept). Paths updated in FIGURES.md, DATA, MAGNITUDES.md, the 17g decisions note (not under SHA256SUMS) and the handoff; rule in CLAUDE.md, FIGURE_STYLE.md, DECISIONS (Figures). FIGURES.md: figure 1 "catalog map by family" closed, figure 2 completeness through time to FITS, source-catalogue figures backup only. `classify_check` and `locate_check` figures left in `catalog/figs/` for now (Pablo). Commit addition: `catalog/FIGURES catalog/figs/rules catalog/figs/magnitude CLAUDE.md FIGURE_STYLE.md FIGURES.md`; message addition: `; catalogue paper figures in catalog/FIGURES/`.

## 2026-11-18 — context conversation: state saved (Claude, chat)
- What the context conversation of 17 Nov discussed and did not yet write elsewhere is in `handoffs/2026-11-18_context_state.md`. Open for Pablo: figures (pituPLOTS or `plots/`, then sync FIGURE_STYLE.md and CLAUDE.md), compaction aids (`/reread`, the "save state" line), AI disclosure for the paper and the port, four A11 points to confirm with CAT, the FITS work given in the chat, IF's geodetic explanation before step 4. Proposed LEARNINGS lines are in the same note.

- **Fit figure style in `fits/figs.py` (Pablo, 18 Nov):** `fmd` draws cumulative (filled points, solid) and incremental (open points, dashed) in two tones of the class colour (`tones`), each fit with its 95 % confidence band from the bootstrap of b, rate and corner (`band`, smooth per-bin band via `inc`), observed incremental rates with a Poisson 1σ interval, completeness steps with their year; no Mw ≥ 7 band; tags in mathtext with Ubuntu (`rcpaper`). `fig_fmd`: `fmd_classes.png` (2 × 4, page width) and `fmd_interface_segments.png/.pdf` (margin, then segments north to south, shared y 8e-5–300, map of the segment source outlines from `model/interface/geometry/edges_2026-11-16c.json`, legend). The predictive band (`gr.predictive`) stays in the library, not drawn. Drafts in `drafts/fits/interface_figs/`. Jujuy nest b on 17g 1.16 (17f 1.23): the nest conversion fix of CAT moves it.

## 2026-11-18 — context conversation: FITS takes the catalogue statistics (Claude, chat)
- Pablo, 18 Nov: FITS makes every table computed from the catalogue (declustering, GR fits, B14 nodal planes and class shares, C14 / C15 depth cells); IS builds the in-slab sources from them. Written into CLAUDE.md (sessions line), CURRENT.md (in-slab owner) and DECISIONS (In-slab: ownership, depth cells with the C15 class-weight method for the final model, B14 rebuilt). PLAN: B16 (mechanisms), C16 (depth cells).
- For the next FITS session: read `handoffs/2026-11-16_B14_close.md` and `2026-11-16_C15_close.md` for their traps (`RUN` and `CAT` hard-coded, `options.BASE` = `run.RUN`, `test_cell_table` picks the newest file by sort order, `b.pad` on a pandas row is a method, plain `python` not on the PATH).
- Order after FITS: IS builds the sources (and the pattern with its kernel n) from the new tables; CR reads the new nodal-plane file.
- Optional for FITS, open for Pablo: the in-slab Mmax comparison case named in DECISIONS (1918, 1925, 1934, 1948, 1971 at their ISC-GEM proxies), never built.

- **Completeness re-measured on 17g (Pablo, 18 Nov, FITS):** `table.auto` measures Mc(t) on the whole margin and on each segment, `steps_series` counts a window only if its point Mc and its 16th percentile exceed the magnitude (fix 1; a failed estimator no longer counts). `run.TABLE` = 5.0 / 1981, 5.1 / 1964, 7.0 / 1905, 7.5 / 1830, 8.5 / 1550 (margin and every class); `run.SEG_INST` per segment (seg4 5.0 / 1964; seg3 5.0 / 1976, 5.2 / 1964; seg2 5.0 / 1964; seg1 5.0 / 1999, 5.2 / 1964); `run.table_of` picks them; `run.py` asserts the measurement against both and writes `mc_table_<date>.csv` (every series) and `mc_series_<date>.csv`; `figs.fig_mc` restyled (five series). `table.CHECK_BANDS` adds 8.5. Trial on 17g (log_9): margin b 0.94 ± 0.02; 26–17.6° S 0.92; 32–26° S 0.92; 37–32° S 0.96; 45.6–37° S 0.95 ± 0.12. Historical figure `drafts/fits/completeness/historical_17g.png` (slope method with both checks). Open for later (memory): short Mc episodes moving a step by years (persistence rule or accept). Tests 37 pass.
- Questions answered: the Mc estimators fit an open exponential (Tinti for b-stability, binned exponential for KS), right for Mc where only small magnitudes matter; the fit floor stays 5.0 (b-stability floors 4.4–4.8 measured; Pablo, 17 Nov).

## 2026-11-18 — context conversation: geodetic question moved after the refit (Claude, chat)
- Pablo, 18 Nov: IF does not look into the geodetic branch now. The geodetic / seismic ratio depends on the seismic fits, which FITS is redoing. IF explains the 13 % effect and the N(≥ 8) ratio after its build on the new fits, with the new numbers. This replaces "IF: explain, without a rebuild" in the entry of 17 Nov above. DECISIONS, Interface, line on the 0.5 / 0.5 updated.


## 2026-11-18 — FITS: declustering algorithms consolidated (Claude Code, FITS)
- **Pablo:** consolidate the algorithms first (NN, GK with the Gruenthal and Uhrhammer windows, Reasenberg), calibrated to the catalogue where the method says so, nothing made up.
- `fits/decluster.py`: `gk_window(m, window)` with eqs. 1–3 of van Stiphout et al. (2012) (`refs/catalogs/vanstiphout_2012_corssa.pdf`, p. 10; identical to `openquake.hmtk` `GardnerKnopoffWindow`, `GruenthalWindow`, `UhrhammerWindow`); foreshock window = aftershock window for all (B12). `reasenberg()` from van Stiphout et al. section 5.2 (eq. 4, Table 3 standard parameters tau_min 1 d, tau_max 10 d, p1 0.95, xk 0.5, rfact 10) and the interaction distance of Molchan and Dmitrieva (1992) as quoted there (log10 d = 0.4 M − 1.943 + k); x_meff = the cut-off of the input (Mw 4.5). Not verified against Reasenberg (1985) itself: how x_k raises x_meff (Table 3 caption reads x_meff + x_k M; I used x_meff + x_k (M − x_meff), as I recall CLUSTER2000) and the pairing of two unclustered events; needs the paper or the CLUSTER2000 code. NN: b from the catalogue (Weichert on the margin table, all events: 1.037), d_f 1.6 of Zaliapin and Ben-Zion kept (no Chile estimate). Methods: `gk_family`, `gk_gruenthal_family`, `gk_uhrhammer_family`, `rb_family`, `nn_family` (+ comparison `gk`, `nn`, `nn_depth`). Tests 39 pass.
- Trial on 17g (`drafts/fits/trial/declustered/`), Mw ≥ 4.5 kept: GK 42 %, Gruenthal 32 %, Uhrhammer 61 %, Reasenberg 81 %, NN 77 %; Mw ≥ 7 kept of 162: 146, 146, 134, 153, 145. Every method keeps 1906, 1922, 1950, 1960 (9.5), 1995, 2010, 2014, 2015 and removes the 1960-05-21 Mw 8.1 foreshock.
- **Reasenberg dropped (Pablo, 18 Nov):** removed from `decluster.py` and its test (not checkable against the original paper); methods for the factor stay `gk_family` and `nn_family`, with `gk_gruenthal_family` and `gk_uhrhammer_family` added as published windows. Tests 38 pass.
- **Interface fits crystallized on the final rules** (FITS.md section 4, table "Interface, final rules on catalogue 17g"; trial numbers until the final run): margin b 0.942 ± 0.024, N(≥ 8) 0.0369; 26–17.6° S 0.916; 32–26° S 0.920; 37–32° S 0.958; 45.6–37° S 0.947 ± 0.116; every check passes. 8.5 / 1550 justification extended with Villarrica (1552), Angol (1553 or 1558) and Osorno (1558), and the destruction of the southern towns in 1598–1602 (FITS.md section 2, DECISIONS line).
- **Declustered interface fits, one figure** (`drafts/fits/completeness/interface_declustered.png`; cumulative, tapered, tables of the fits, Mmax of the full catalogue): b full / GK / Grünthal / Uhrhammer / NN = margin 0.94 / 0.74 / 0.70 / 0.81 / 0.88; 26–17.6° S 0.92 / 0.78 / 0.75 / 0.88 / 0.89; 32–26° S 0.92 / 0.73 / 0.68 / 0.82 / 0.86; 37–32° S 0.96 / 0.64 / 0.61 / 0.71 / 0.86; 45.6–37° S 0.95 / 0.85 / 0.78 / 0.82 / 0.94. b-positive of the margin about 0.88.

## 2026-11-18 — FITS: close of the conversation (Claude Code, FITS)
- **Code crystallized:** `fits/figs.py` (`fmd`, `fig_fmd`, `fig_mc`, `fig_historical`, `save(fig, name, kind)` → also `fits/FIGURES/<kind>/` PNG and PDF), `fits/figs_declustered.py` (`fig_margin`, `fig_segments`, all methods in `COL`, `MK`, `ALG`), `fits/run_declustered.py` (`METHODS` with the Gruenthal and Uhrhammer windows), `fits/mc_maps.py` (supplement map of Mc per node, moved from drafts), `run.PAPER`. `drafts/fits/trial.py` routes `PAPER` to `drafts/fits/trial/FIGURES`. Tests 38 pass.
- **Decisions written into DECISIONS** (Statistics, Figures; Pablo, 18 Nov, FITS): measured instrumental steps (margin and per segment); 8.5 from 1550 with the southern towns; fit floor 5.0; table kept against Albarello; the declustering algorithms (Reasenberg not used); the fit-figure style and `fits/FIGURES/`. Two earlier lines corrected so they no longer state the superseded instrumental steps.
- **Open, for Pablo:**
  - short Mc(t) episodes moving a step by years (two 1977.9–1980.3 windows set the margin 5.0 to 1981): a persistence rule or accept (memory note).
  - Choice of the declustering algorithm with the co-authors; scoring them on b against b-positive, a Poisson test and the great mainshocks kept is not done.
  - The non-interface classes on the new tables (in-slab, crustal): `fits/FIGURES/fits/fmd_classes.png` was drawn by the trial but not reviewed; the next session starts there.
  - d_f of nearest neighbour for Chile (kept at 1.6).
  - Paleoseismic interval of 1960-type events (about 300 years, Cisternas et al. 2005, to check) against the fitted recurrence of Mw ≥ 9 on 45.6–37° S (about 1 150 years): for IF and the geodetic branch.
  - Founding dates of Angol (1553 or 1558) and Castro (1567) to confirm before the paper.
- **Proposed LEARNINGS lines:**
  1. A completeness envelope over regions gives each region one vote: a quiet region with 5 % of the events set the table of the whole margin. Measure Mc(t) on the events that are fitted.
  2. In a last-window completeness rule a window whose Mc estimator fails must not count through its bootstrap alone.
  3. Declustering by windows flattens b on a subduction margin (to 0.6–0.75); the fit then passes through the great events because it pivots, not because the catalogue is better. Check b against b-positive.
  4. Cumulative points hide where a fit disagrees: one excess at large magnitude lifts every point to its left. Show the incremental rates with Poisson intervals.
  5. A default argument bound at definition (`table=TABLE`) keeps the old table when the module value is changed later; pass `None` and resolve inside.
  6. The fits of a catalogue that keeps its aftershocks depend on which years enter the lowest bin (Mw 5.0 from 1976 or 1999 moved b by 0.05); on the declustered catalogues the same choice moved b by 0.01.
- **Commit (from `psha_chile8/`):** `git add fits/ DECISIONS.md FIGURES.md REFERENCES.md WORKLOG.md handoffs/2026-11-18_FITS_to_CAT.md handoffs/2026-11-18_FITS_state.md` and `refs/catalogs/vanstiphout_2012_corssa.pdf albarello_2001.pdf hakimhashemi_gruntal_2012.pdf` from the repo root; message: `FITS: measured completeness (Mc(t) per margin and segment, 8.5 from 1550), cluster bootstrap, declustering algorithms (Gruenthal, Uhrhammer windows, NN b from the catalogue), fit-figure style and fits/FIGURES; interface fits on 17g`

## 2026-11-18 — IF: final interface build prepared, dry run on fits 16f (Claude Code, IF)
- **Inputs from CURRENT.md** (`gr.current`, the row names of the FITS block): `if_build.FITS`, `FITS_DC`, `CAT` ("catalogue the fits and models are built on"); `if_pad.PAD_FITS` from the row "Mmax pad 0.0 / 0.4"; `if_figs` takes the catalogue from CURRENT and each unit's table from the `steps` column of its fits row (the old `table_2026-11-16f.csv` path is gone; the segments now have their own steps). `DATE` is only the tag of the output folder; `write` stops if `nrml_<DATE>/` is named in CURRENT.md.
- **Margin-b cache:** `tables/fits_marginb_<fits date>.csv`, keyed by the fits file, not by `DATE`. Before using it, `margin_b` checks that `fits/run.py` reproduces the fits file (margin and segments refitted without bootstrap on `CAT` with the row's table, b and rate within 1e-5), then that the cached point fits equal a refit; otherwise it refits. A fresh refit is rounded like the cache, so a first build and a rebuild are byte-identical (16c was built from the unrounded refit: its margin-b files differ by about 1e-6 relative). `CLUSTER_BOOT = True`: the margin-b bootstrap draws `nn_family` clusters, as the fits from 17 Nov; False only for the 16f trial. `if_pad.check` refits on `CAT` with the row's table too.
- **Final-tree choices of DECISIONS (17 Nov):** tapered shape only (cut files at weight 0, for the tornado); geometry 0.5 / 0.5; seismic 0.5 / geodetic 0.5, χ 0.7 / 0.8 / 0.9 at 1/6 each; geodetic only under the full catalogue (no declustered geodetic files any more); seismic rate convention full 0.5 / declustered 0.5 (team level; one algorithm, line below); b per segment own / shared / whole-margin at 1/3 (declustered: own / shared at 1/2) (team level); (a, b) 0.185 / 0.63 / 0.185; scaling 1/3 each. 132 branch files (57 in the tree) + 4 pad files; `w_factor` holds every factor, its product is the weight; branches.json written at full precision. Every tornado row id of `hazard/jobs.py` still exists, and the `tornado` block is unchanged.
- `if_oqcheck.CALCS` and `if_pad.CALC` are settings at the top, None until the jobs have run.
- **Dry run (trial, not used):** fits 16f on catalogue 16c, into `/tmp/claude-1000/-home-pciturri--claude-spares-spare-sMSDXO/af0967fe-861a-4b47-8901-035b49df7e53/scratchpad/if_trial/` (`TRIAL.md`, driver `if_trial_run.py` beside it). No CURRENT line, no engine job. The run took 45 s with the cache. Pad check: all 15 rows ok. 108 of the 132 files are byte-identical to `nrml_2026-11-16c`; the other 24 are the margin-b files (the rounding above). A second trial without the cache (`if_trial_nocache/`) refits the same margin-b rows and gives the same 132 files. `pytest model/interface/tests`: 11 pass (tree checks rewritten for the final weights).
- **Not done (brief):** the geodetic explanation; it comes after the build on the new fits.
- **Commands for the real build**, after FITS has published its note in `handoffs/` and the CURRENT rows "fits, full catalogue", "fits, declustered", "Mmax pad 0.0 / 0.4" and "catalogue the fits and models are built on" name the new fits and 17g (if FITS renames a row, `gr.current` stops with a KeyError):
  1. In `model/interface/if_build.py` set `DATE` to the next free tag (e.g. `"2026-11-18"`) and `DC` to the team's algorithm; keep `CLUSTER_BOOT = True`.
  2. From `psha_chile8/model/interface/`: `python if_build.py` (about 5 min: margin-b refit with 2 000 cluster resamples; it stops if `fits/run.py` does not reproduce the new fits).
  3. `python if_pad.py` (pad check must print ok for all rows).
  4. From `psha_chile8/`: `pytest model/interface/tests`.
  5. `python if_oqcheck.py` writes `oqcheck_<DATE>/job_margin.ini`, `job_seg.ini` (and `if_pad.py` wrote `job_pad.ini`). Run them from `oqcheck_<DATE>/` with `OQ_CONFIG_FILE=<cfg with serialize_jobs = 0> PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine oq engine --run job_<x>.ini`, set `CALCS` / `CALC`, and run both scripts again (`OQ_DISTRIBUTE=no`).
  6. IF then updates the Interface line in CURRENT.md and DATA.md, writes a note to HAZ, and explains the geodetic branch with the new numbers. Also tell FITS that `fits/figs.EDGES` can point to `geometry/edges_<DATE>.json` (same geometry).
- **One declustering algorithm (Pablo, 18 Nov, IF; DECISIONS, Interface):** seismic rate convention full 0.5 / declustered 0.5, the declustered branch with one algorithm, `if_build.DC` (placeholder `nn_family` until the team chooses; set it before the real build). The other algorithm (`DC_METHODS`) is written at weight 0 for the tornado rows `decl_gk` / `decl_nn`. Tree: 57 branches (seismic full 0.25, declustered 0.25; geodetic 1/6 per χ); trial rerun and tests pass. FITS's `gk_gruenthal_family` / `gk_uhrhammer_family` are not read; if the team picks one of them, add it to `DC_METHODS`.
- **Commit (from `psha_chile8/`):** `git add model/interface/if_build.py model/interface/if_pad.py model/interface/if_figs.py model/interface/if_oqcheck.py model/interface/tests/test_interface.py model/interface/tables/fits_marginb_2026-11-16f.csv WORKLOG.md`. Message: "IF: final interface build prepared (inputs from CURRENT.md, checked margin-b cache, final-tree weights, geodetic under full only); dry run on 16f"

- **Addendum 2, figures (Pablo, 18 Nov):** `catalog/FIGURES/classes/` (maps, sections, band, nest, sensitivity from `classify_check.OFFICIAL`; `lofs_south`, `lofs_full` from `explore/A9/a9_lofs.py`; moved, not redrawn), `catalog/FIGURES/sources/` (`sources_figs.py` writes there; the 17 Nov files copied), rules figure back to the compact one-row layout of the 16 Nov deck (`presentations/261116_psha8_results/figs/figs.py`) in `catalog/figs/rules/rules_fig.py`. Check figures stay in `catalog/figs/`. Commit: `git add catalog/FIGURES catalog/figs/classify catalog/figs/rules catalog/classify_check.py catalog/sources_figs.py explore/A9/a9_lofs.py CLAUDE.md FIGURE_STYLE.md DECISIONS.md FIGURES.md WORKLOG.md`; message: `CAT: classification, source and rules figures in catalog/FIGURES/; compact rules figure`.

## 2026-11-18 — IS: final in-slab build prepared, dry run on the 16 Nov tables (Claude Code, IS)
- **Nodal planes mixed per cell** (`build.planes`, `npd_cells`; DECISIONS In-slab, B14): the slab source of each cell takes the shallow and intermediate planes of the B14 table, weighted by the cell's class share of the rate above Mw 5.5 (`shallow_m5.5` of the class-share table, the row of the branch's decl / shape / (a, b) when the table has those columns; pad rows take the ML row). Equal planes merged, probabilities rounded to 0.001, remainder on the largest. The nest takes its own planes. A cell with rate and no share stops the build. Two tests (`test_planes_mix_the_two_classes_by_share`, `test_planes_of_the_current_tables_sum_to_one_in_every_cell`). On npd 16d most cells carry 10 planes (12 884 of 13 847), against 2 before: about 5× the ruptures per cell, so expect longer in-slab jobs.
- **Inputs from CURRENT.md** (`build.current(row)`): catalogue ("catalogue the fits and models are built on"), fits, declustered fits, pad tables, completeness table (also the pattern table, no longer hard-coded), declustered catalogues, depth cells (three layers; one layer and lower depth), class shares, nodal planes. `is_tornado.py` and `is_decl_rates.py` take theirs from `build`. The build's own class shares go to `tables/class_share_check_<RUN>.csv` (not `class_share_<date>`, which is FITS's name now) and are compared with the CURRENT table (16 Nov: max difference 5e-6, no cell missing).
- **Final tree** (DECISIONS, Logic tree; In-slab line of 18 Nov): three layers, tapered, pad 0.2; (a, b) 0.185 / 0.63 / 0.185; rate convention full 0.5 / declustered 0.5 (`build.RATE_W`; Pablo, 18 Nov, IS, as IF); one declustering algorithm for pattern and declustered rates, `build.DC` (placeholder `nn`, as IF; the other algorithm at weight 0). Six tree branches: `nn_taper_{p05,ml,p95}_l3` (0.0925 / 0.315 / 0.0925) and the same with `_ratenn`. Tornado rows: one layer (C15), lower depth 0.65, Allen–Hayes, cut shape, pad 0.0 / 0.4, (a, b) rows, `is_decl_gk` (other pattern), `is_rate_gk`, `is_rate_nn`. The declustered-rate branches are now written by `build.py` in the same folder; `is_decl_rates.py` is no longer run (remove it in the commit). The tornado reference follows `DC`.
- **Decided (Pablo, 18 Nov, IS):** the brief had the declustered rates as tornado rows only, against DECISIONS (team levels stay in the tree) and IF's tree; Pablo: in the tree at 0.5, as IF. Written into DECISIONS (In-slab, Superseded).
- **Dry run** (trial, not used, no CURRENT line): `drafts/inslab/trial/` (`README.md`, `log.txt`, `nrml/`, `tables/`), on fits 16f, depth cells 16 / 16d, npd 16d, class shares 16; build and tornado 2 min. Parser read of the reference and every variant passes (rates within 1e-7 of the tables), so the mixed planes are valid NRML. Tests: `pytest model/inslab/tests` 29 pass on the trial outputs (with `TRIAL = True`); on `model/inslab/` 19 pass and the 10 checks of the built model skip until the real build.
- **Commands for the real build**, once FITS's note is in `handoffs/` and CURRENT.md names the new tables:
  1. Check that the CURRENT rows read by `build.current` still exist under these names (FITS may rename the depth-cell rows for the C15 cells): `/data/miniforge3/envs/psha_renta/bin/python -c "import build as B; print(B.CAT, B.FITS, B.DEPTH, B.ONE, B.LSD, B.SHARE, B.NPD_TAB, B.DECL, B.PADS, B.TABLE)"` from `model/inslab/`. The new class-share table must keep `lon, lat, shallow_m5.5` (decl / shape / ab columns optional).
  2. Settings: `build.py` `DATE` = the fits date, `RUN` = a new free run (e.g. `<date>b`), `TRIAL = False`, `DC` as the team chooses; `is_tornado.py` `RUN` (e.g. `<date>c`); no `is_decl_rates.py` step.
  3. From `psha_chile8/model/inslab/`: `python build.py` → `python is_tornado.py` → `python figs_s2.py` (full interpreter path as above).
  4. From `psha_chile8/`: `pytest model/inslab/tests`.
  5. IS then updates CURRENT.md In-slab ("sources and tornado rows"; the "declustered-rate rows" line goes, its rows are in the sources folder), DATA.md, and writes `handoffs/<date>_IS_to_HAZ.md`: six tree branches (full / declustered × (a, b)); tornado rows `is_decl_gk` (replaces `is_decl_nn` while `DC` = nn), `is_rate_gk`, `is_rate_nn` now in `branches.json` of the sources folder; `hazard/config.py` reads `extra` from the "declustered-rate rows" line, which HAZ removes. Hazard jobs: about 5× the in-slab ruptures per cell (10 nodal planes).
- **Commit (from `psha_chile8/`):** `git rm model/inslab/is_decl_rates.py`; `git add model/inslab/build.py model/inslab/is_tornado.py model/inslab/figs_s2.py model/inslab/tests/test_s2.py DECISIONS.md WORKLOG.md`. Message: "IS: final in-slab build prepared (inputs from CURRENT.md, nodal planes mixed per cell by class share, (a, b) and full / declustered rates in the tree, one declustering algorithm); dry run on the 16 Nov tables"
- `run_declustered.py` no longer reads a completeness table on each declustered catalogue (unused since 17 Nov; it now cost five Mc(t) series per catalogue): every catalogue is fitted on the tables of the full catalogue; `declustered_tables_<date>.csv` is not written any more; helpers `years`, `differ` and `DMAG`, `DYEAR` removed.
- **Figures in `fits/FIGURES/`** (copied from the trial on 17g, 18 Nov 03:22; the final run rewrites them): `completeness/mc_time`, `historical`, `mc_maps`; `fits/fmd_interface_segments`, `fmd_classes`; `declustering/interface_margin_declustered`, `interface_segments_declustered` (PNG and PDF; rows in FIGURES.md). `mc_maps` still in the old map layout (longitude labels crowd, the domain reaches 56° S where no node is measured): to tidy before the supplement.
