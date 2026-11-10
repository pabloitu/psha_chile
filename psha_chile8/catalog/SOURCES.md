# Source catalogs (plan A2)

Each source is fetched by `fetch.py` into `sources/raw/<name>/` (with `fetch.json`: query, period, download date) and read by `read.py` into `sources/<name>_<YYYY-MM-DD>_{events,mags,mechs}.csv`, listed in `sources/MANIFEST.csv`. Profiles in `figs/profile/<name>.png` (`profile.py`).

Download box for all sources: lat −58.0 to −15.5, lon −80.0 to −60.0. Native magnitude ≥ 3.5 where the service filters (ComCat; ISC from 1964). Global files are cut to the box in `read.py` (an event is kept if any of its origins is inside).

Common tables:
- **events**: `src, src_id, origin_id, prime, time, lon, lat, depth, depth_fixed, lon_err, lat_err, depth_err, depth_quality, agency, etype`. One row per origin; `prime` marks the source's preferred origin. Time is the source's UTC string (partial dates kept as given). Depth and errors in km; `lon_err = lat_err` is the horizontal error (semi-major axis) where the source gives one number.
- **mags**: `src, src_id, agency, mag_type, mag, mag_err, n_sta, note`, every magnitude with the agency and the type string as the source writes it.
- **mechs**: `src, src_id, agency, code, m0, mw, mw_type, strike1 … rake2, mrr … mtp`; M0 and tensor in N m.
- A few sources carry extra columns after these (Potin `rms`; Cabello `relocated, reference`; Ruiz and Madariaga `lat_n, lat_s, rm_class, domain, basis, note`).

Cards below: what was known from the test run and the local files, and a last line per card from the full download of 2026-11-10 and its profile. Depth percentages are of the preferred origins.

## comcat: USGS ComCat
- **How:** USGS FDSN event service, CSV, yearly requests (split to months or days if a year exceeds 19 000; the largest year in the box, 2010, has 2 318 events ≥ 3.5); events before 1900 in one request.
- **Coverage:** 1500 – download date; ≈ 44 000 events ≥ 3.5 in the box (count on 2026-11-10).
- **Magnitudes:** the preferred magnitude only (`magType`, `magSource`, `magError`, `magNst`); native magnitudes per agency come from `isc`.
- **Depth:** no fixed-depth flag in the CSV (`depth_fixed` empty); default depths (10, 33, 35 km) to be read from the profile.
- **Issues:** `etype` keeps non-earthquakes (quarry blast, explosion) for A3 to drop. Event IDs can change between downloads (network that authors the preferred origin); the frozen file is the reference.
- **After the full fetch (2026-11-10):** 43 985 events, 1904–2026 (`comcat_2026-11-10`). Before 1973 mostly M ≥ 5.5 events with ISC-GEM Mw; M < 4 common only from the 1990s. Preferred magnitudes: us mb from 1973 (25 343), guc md 1997–2010, san md 1990–1997, us mwr / mww from 2011, iscgem mw before 1973, hrv / gcmt mwc. Default depths: 10 km 7.1 %, 33 km 6.6 %, 35 km 3.5 %, 100 km 1.1 % of preferred origins (no flag, so A4 has to treat these values as fixed).

## comcat_mt: ComCat moment tensors and focal mechanisms
- **How:** one GeoJSON event page per ComCat event with M ≥ 5.0 from 1976 (4 274 events), throttled to about one request per second, resumes by skipping events already on disk. Uses the GeoJSON detail that `libcomcat` wraps (libcomcat is not installed in `psha_renta`); same products as `cat_no_mech_handler/parsers/anss.py`.
- **Content:** every `moment-tensor` and `focal-mechanism` product, not only the preferred one: `agency` is the `beachball-source` (us, LD = GCMT via PDE, duputel, …), `code` the product kind and code, `mw` / `mw_type` the product's derived magnitude where it has one.
- **Issues:** old PDE products have no derived magnitude; the `scalar-moment` of the Maule WCMT product (2.78e23) does not match its Mw 8.8 (W-phase moment 2.26e22), so moments are checked against the tensor in A4. GCMT solutions appear twice (moment-tensor and focal-mechanism products).
- **After the full fetch (2026-11-10):** 2 501 of the 4 274 events have a product (5 288 products). Before 1996 the products are focal mechanisms without moment or Mw (566 events with no magnitude in the profile). 1 773 events have no product: mostly M 5 before 2000 and Maule aftershocks in 2010. Products without a derived Mw but with M0 are drawn with Mw from M0 in the profile (figure only, not in the table). Agencies: us 3 494, US 594, LD 547 (2006–2013), HRV 479 (1996–2006), gcmt 103, duputel 53.

## isc: ISC Bulletin
- **How:** ISC FDSN event service, QuakeML, `includeallorigins`, `includeallmagnitudes`; yearly requests 1904–1963 (no magnitude filter, most events have none), monthly from 1964 with `minmagnitude=3.5`; a request that fails is halved down to one day. Parsed with ElementTree (all origins, all magnitudes).
- **Coverage:** 1904 – download date (ISC review lags by about two years; recent months are unreviewed).
- **Magnitudes:** per agency and type, e.g. ISC mb / MS, NEIC mb, IDC mb / mb1 / mb1mx / mbtmp / ML / MS / Ms1 / ms1mx, GUC (CSN) ML / MD, GCMT MW, BJI, MOS. Type strings are kept as written (MS vs Ms differ by agency).
- **Depth:** `depth_fixed` from QuakeML `depthType = operator assigned`; in Mar 2010 most ISC, NEIC and IDC origins are flagged so (IDC 0 km, NEIC 35 km, ISC 25 km). Origin errors from the uncertainty ellipse (semi-major axis); depth error often missing.
- **Issues:** includes ISC-EHB origins (agency ISC-EHB) inside the Bulletin; ISC prime is not always the best origin.
- **After the full fetch (2026-11-10):** 91 177 events, 1904–2026; 1 162 without any magnitude (ISS years before 1964); 670 preferred origins without depth. 255 agency-type pairs; the large ones: GUC ML from 2000 (49 633), IDC mb / mbtmp / mb1 / mb1mx / ML / MS from about 2000, ISC mb from 1964 (32 207), NEIC mb from 1985, SJA (Argentina) ML and MW from 2010. M < 4 events rare before 1987. 25.7 % of preferred depths flagged fixed; spikes 35 km 3.6 %, 10 km 2.6 %, 0 km 2.3 %. Four monthly files end with a stray `?` after the closing tag (reader cuts it). 8 events returned by the box search had no origin in the box (dropped).

## csn: CSN catalogue (sismologia.cl daily pages)
- **How:** one page per UTC day, `https://www.sismologia.cl/sismicidad/catalogo/<yyyy>/<mm>/<yyyymmdd>.html`, from 2020-01-01 (6.5 months of overlap with Potin, for A3 and A5) to the day before the download; 1 s between requests, ≈ 1 h. Data use: academic use allowed with citation of the Centro Sismológico Nacional, Universidad de Chile (sismologia.cl, "Uso de datos"). Approved by Pablo on 2026-11-10.
- **Completeness:** the day pages list the whole published catalogue, not only felt events: 13 / 28 / 34 events on 2019-06-01, 2015-03-01 and 2020-07-15 against 13 / 26 / 29 in Potin. The per-event report pages carry nothing more (fewer decimals), so they are not fetched.
- **Content:** UTC time to the second, lat / lon to 0.001°, depth in whole km, one magnitude with its type (`Ml`; `Mw` from a Brune model for mid-size events; `Mww` W-phase for large ones), `felt` (rows marked `percibido`). `src_id` = year / month / report number of the event page (e.g. `2024/01/221233`).
- **No magnitude floor:** a day page costs the same whatever it lists, so everything is kept; the floor for the conversion fits is set in A5.
- **Issues:** no errors, no fixed-depth flag, integer depths (1 km heaping in the profile is expected, not a default); one magnitude per event, so Ml and Mw are not both available for an event (pairs with GCMT and ComCat instead); the catalogue is not relocated (DECISIONS).
- **After the full fetch (2026-11-10):** 55 549 events, 2020-01-01 to 2026-11-09 (≈ 7 000–7 800 a year; 2026 to early November already 10 300), 92 % M < 4; 2 026 felt. 502 events on the pages fall outside the box. **Magnitude type change in 2026:** `Ml` (44 616, all years) is replaced by `Mlv` (9 175, almost all in 2026); also `Mw` 1 536 (3.6–6.3), `Mww` 148 (4.8–7.5), `M` 58, `Mb` 9, `Mlh` 5, `Ms` 2. Ml vs Mlv to be treated as two types in A5 until shown equal. Depth spikes small (10 km 1.4 %; integer depths).

## csn_isc: CSN solutions inside the ISC Bulletin
- **How:** the GUC (CSN) origins and magnitudes of the `isc` download. Same frozen date as `isc`.
- **Magnitudes:** GUC ML (most), MD, a few MS, MG.
- **Use:** cross-check of `csn` and of Potin (ISC keeps several GUC magnitudes per event where the web page shows one); two years behind for reviewed months.
- **After the full fetch (2026-11-10):** 60 949 events, 1988–2025, 324 without magnitude. Type sequence: GUC M 1988–1992, md 1989–1998, MD 1999–2010, ML from 2001, MG 2005–2011, MW 2001–2023, Mwr from 2013, Mww from 2017. 4.1 % fixed depths, spike at 15 km (1.4 %). 6 events with the GUC epicentre outside the box dropped.

## iscehb: ISC-EHB
- **How:** ISC-EHB catalogue search, yearly 1964–2021, twice: CSV (gives `DEPFIX` and the depth quality class `DEPQUAL` L1–L3) and QuakeML (origin errors, magnitude errors and station counts), joined by event ID. The per-year `.hdf` files on download.isc.ac.uk carry no L1–L3 class, so the catalogue search is used instead.
- **Coverage:** 1964–2021; 908 events in the box in 2010.
- **Depth:** quality 2010: L1 240, L2 141, L3 527; L3 events mostly have fixed depths.
- **Magnitudes:** ISC mb, ISC MS, GCMT MW (with errors and station counts).
- **After the full fetch (2026-11-10):** 10 221 events, 1964–2021, almost all M ≥ 4 (65 below). Counts roughly double from 1995. 30.9 % of depths fixed (L3), spikes 15 km 7.2 %, 20, 10, 25 km. Magnitudes: ISC mb (all years), ISC MS; Mw only from GCMT 1976–1984 and from 2006, HRVD 1999–2006: none in 1985–1998.

## iscgem: ISC-GEM
- **How:** manual. The download page (https://www.isc.ac.uk/iscgem/download.php) is a form with name, e-mail and a CAPTCHA; no direct link (tried the archived file names too). Pablo downloads the main and supplementary CSV into `sources/raw/iscgem/` (file names starting `isc-gem`); `fetch.py` then only writes `fetch.json`.
- **Version:** 13.0, released 2026-10-21 (main `isc-gem-cat.csv` and `isc-gem-suppl.csv`, from the header of both files).
- **Coverage:** 4 129 events in the box (3 695 main, 434 supplementary), from 1904; 2 602 with a mechanism or moment.
- **Reader:** header from the last `#` comment line; the repeated `q` / `unc` columns become `q, q.1, q.2` / `unc, unc.1` (location, depth, Mw quality). `depth_quality` = depth quality (A 2 443, B 387, C 1 299), `note` = Mw quality and `s`, the Mw source (`d` direct 2 602, `p` proxy 1 142, empty 385 with quality D). Checked on the real v13 header; the test sample is three real rows.
- **To do:** compare with `data/isc_gem.csv` (2 105 rows, from 1976, M ≥ 5 cut) in A4.
- **After the full fetch (2026-11-10):** 4 129 events, 1904–2022 (v13 stops at 2022). 385 without Mw (quality D), mostly 1940–1965. Depth spikes 15 km 10 %, 35 km 4.7 %, 25 and 20 km.

## gcmt: Global CMT
- **How:** the two local ndk files (`gcmt_jan76_dec20.txt`, `gcmt_jan21_aug25.txt`) plus the monthly ndk files from Sep 2025 (available up to Jun 2026 on 2026-11-10; later months not yet published and listed as failed in `fetch.json`).
- **Coverage:** 1976 – Jun 2026; 2 797 events in the box (1976 – Jun 2026), Mw 4.1–8.8.
- **Events:** two origins per event: the reference hypocentre (`agency` = PDE, PDEW, PDEQ, MLI, …; `prime` false) and the centroid (`agency` GCMT, `prime` true; centroid time = reference time + shift). `depth_quality` = FREE / FIX / BDY, `depth_fixed` true for FIX and BDY.
- **Magnitudes:** GCMT Mw from M0 (Mw = 2/3 (log10 M0 − 9.1)), and the mb / Ms of the reference catalogue (PDE / PDEW, MLI before 1983).
- **Depth:** fixed depths 15 km (134) and 12 km (99), then 33, 10, 25 km; BDY mostly 15 km. Free depths 2 405, FIX 301, BDY 91.
- **Issues:** ndk centroid line read by fixed columns (two blocks have the time shift and its error run together).
- **After the full fetch (2026-11-10):** 2 797 events; 14 % of centroid depths fixed (15 km 6.1 %, 12 km 3.6 %). Reference magnitudes: MLI mb / Ms 1976–1983, PDE mb / Ms 1981–2005, PDEW mb 2006–2013, PDEW Ms from 2006. Jul–Oct 2026 not yet published (failed in `fetch.json`). 12 centroids outside the box with the reference hypocentre inside (kept).

## centennial: Centennial catalogue (Engdahl and Villaseñor 2002)
- **How:** `centennial_Y2K.CAT` and `centennial_README.rtf` from the Wayback Machine snapshot of 2013-09-09 of `earthquake.usgs.gov/research/data/centennial.php` (raw files, `id_` URL). Fixed-width format from the README.
- **Coverage:** 661 events in the box, 1902–2007 (the README says extended to 2002-04-01; a few EHB updates run to 2007). Preferred magnitude ≥ 6.8 before 1930, ≥ 6.6 in 1930–1963, ≥ 5.5 from 1964 in the box.
- **Magnitudes:** up to 8 per event, the first is the preferred (`note = preferred`): ISC mb / Ms, HRV Ms, NEIC / NEIS mb / Ms, ABE1 mB, PAS / B&D / G&R `UK` (unknown scale), GSX M / Ms / ML.
- **Depth:** `depth_quality` = solution type (DEQ depth free, FEQ / LEQ / BEQ / HEQ / CEQ fixed, XEQ poor, with suffixes M = mechanism, d, r, x); early events have depth 0.0 and no type (49): unknown, not 0 km. Agency of the hypocentre: EHB 608, G&R 24, ISS 14, ABE 8.
- **Issues:** no event ID (`src_id` is the line number in the frozen file). Not on USGS servers any more; the snapshot is the version.
- **After the full fetch (2026-11-10):** 661 events, 1902–2007; 37 agency-type pairs (PAS / B&D / G&R `UK` and ABE1 mB before 1960; ISC mb, HRV Ms, NEIC mb afterwards). Depth spikes 35 km 6.1 % and 0 km 3.6 % (the unknown depths).

## potin: Potin et al. (2024) relocated CSN catalogue
- **How:** copy of `data/catalogs/CHILE_SEISMICITY_RELOCATED.csv`.
- **Coverage:** 118 003 events, 1982-01-08 – 2020-07-16; 8 694 without magnitude (mostly 1982–1985, and 2000).
- **Magnitudes (`agency` CSN, `mag_type` = the file's code, trailing spaces stripped):** `l` 89 168 (0.6–6.8, from 2000), `c` 18 629 (0.2–6.4, 1982–2009, coda), `ww` 1 238 (3.1–7.6, from 2014, W-phase), `W` 264 (2.1–8.2, 1995–2016), `B` 9 (4.4–5.3), `xx` no magnitude. Meaning of `W` vs `ww` and `B` to confirm with S. Ruiz / the paper.
- **Depth:** relocated, no flags or errors (only `rms`); 1 830 events at or above 0 km (down to −4.95 km).
- **After the full fetch (2026-11-10):** 118 003 events, none cut by the box. **Gap February–August 2000** (one event in January, monthly counts ≈ 200 before and ≈ 100 after). No default-depth spikes (relocated). Type sequence: `c` 1982–2009, `W` 1995–2016, `l` from 2000, `ww` from 2014.

## cabello: Cabello et al. (2025) integrated catalogue
- **How:** copy of `data/catalogs/Integrated_Seismic_Catalog_complete.csv`. Used before 1904 and as a reference only (DECISIONS).
- **Coverage:** 229 865 rows, 1513–2022: CERESIS-GEM 710 (1513–1963), ISC 69 099, USGS 28 669, CSN-improved 127 858, GCMT 2 564, ISC-GEM 965.
- **Magnitudes:** native columns `Mw, Ms, Mb, Ml, Md, Mc, M` kept with the row's catalogue as agency; Cabello's final converted value as `agency = cabello, mag_type = magnitude` (the conversion found wrong in DECISIONS). `mag_unc` attached to the Mw row only.
- **Depth:** `obs_depth` remarks in `depth_quality` (336 "original depth: -"); depth spikes 10, 33, 35, 100, 0, 15 km.
- **Issues:** rows labelled GCMT before 1976 (e.g. 1971-02-21); pre-1904 dates often 1 January 00:00 (date unknown). One blank-padded magnitude cell (read as missing).
- **After the full fetch (2026-11-10):** 227 491 events after the box cut (2 374 dropped, mostly 15.5–11.6° S). Final magnitude for every row; native columns: CSN-improved Ml 111 583 (from 2000), ISC Ml, ISC Mb, USGS Mb, CSN-improved Mc 2000–2010, GCMT Mw / Ms / Mb, ISC-GEM Mw. Depth spikes 10 km 2.1 %, 33 km 1.4 %, 35 km 1.2 %, 100 km (inherited from the source agencies).

## rm2018: Ruiz and Madariaga (2018)
- **How:** copy of `data/catalogs/ruiz_madariaga_2018.csv` (hand table from the paper).
- **Coverage:** 69 events, 1543–2017, 62 with an Mw entry.
- **Magnitudes:** `mag` numeric where the paper gives a number, otherwise empty with the text in `note` (`>7.7`, `7.5-7.9`, `~9`, `<8.5`).
- **Depth:** none. Dates partly year only; longitudes often missing (latitude or rupture extent only).
- **Issues:** to check against the paper in A6 (e.g. Pica 1768 vs 1786 typo noted in the table).
- **After the full fetch (2026-11-10):** 69 events; 27 without longitude (24 matched to located events, see DECISIONS / A3), 24 without a numeric Mw (7 empty, 17 qualified text). No depth panel in the profile.
