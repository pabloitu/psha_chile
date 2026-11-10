# DATA

Every catalog run and every input version, newest first, until the final catalog. One row per run; never edit an old row, add a new one.
Status: `test` (not used further), `used` (something was built on it), `final`.

## Catalog runs

| date | folder | built from | what changed | events (M > 3.9) | status |
|---|---|---|---|---|---|

## Source catalogs (frozen inputs)

| file | source, version or query | downloaded | notes |
|---|---|---|---|
| `catalog/sources/comcat_2026-11-10_*.csv` | USGS ComCat FDSN, CSV, box, M ≥ 3.5, yearly requests | 2026-11-10 | 43 985 events (preferred origin and magnitude only); sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/comcat_mt_2026-11-10_*.csv` | ComCat GeoJSON event pages, every moment-tensor and focal-mechanism product, ComCat M ≥ 5.0 from 1976 | 2026-11-10 | 5 288 products for 2 501 events (mechs only); sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/isc_2026-11-10_*.csv` | ISC Bulletin FDSN, QuakeML, all origins and magnitudes, box, M ≥ 3.5 from 1964 | 2026-11-10 | 91 177 events, 275 287 origins, 401 452 magnitudes; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/csn_isc_2026-11-10_*.csv` | GUC (CSN) origins and magnitudes of the isc download | 2026-11-10 | 60 949 events, 1988–2025; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/csn_2026-11-10_*.csv` | sismologia.cl daily catalogue pages 2020-01-01 – 2026-11-09 (approved 10 Nov) | 2026-11-10 | 55 549 events; Ml → Mlv in 2026; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/iscehb_2026-11-10_*.csv` | ISC-EHB catalogue search, CATCSV + CATQuakeML, 1964–2021 | 2026-11-10 | 10 221 events, depth class L1–L3; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/iscgem_2026-11-10_*.csv` | ISC-GEM v13.0 (2026-10-21), main + supplementary, manual download | 2026-11-10 | 4 129 events, 2 602 mechanisms; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/gcmt_2026-11-10_*.csv` | local ndk 1976 – Aug 2025 + NEW_MONTHLY to Jun 2026 (Jul–Oct 2026 not published) | 2026-11-10 | 2 797 events; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/centennial_2026-11-10_*.csv` | Centennial catalogue, Wayback snapshot 2013-09-09 of the USGS page | 2026-11-10 | 661 events, 1902–2007; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/potin_2026-11-10_*.csv` | copy of data/catalogs/CHILE_SEISMICITY_RELOCATED.csv (Potin et al. 2024) | 2026-11-10 | 118 003 events, 1982 – 2020-07-16; gap Feb–Aug 2000; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/cabello_2026-11-10_*.csv` | copy of data/catalogs/Integrated_Seismic_Catalog_complete.csv (Cabello et al. 2025) | 2026-11-10 | 227 491 events after the box cut; sha256 in `catalog/sources/MANIFEST.csv` |
| `catalog/sources/rm2018_2026-11-10_*.csv` | copy of data/catalogs/ruiz_madariaga_2018.csv (Ruiz and Madariaga 2018) | 2026-11-10 | 69 events, 27 without longitude; sha256 in `catalog/sources/MANIFEST.csv` |

## Other inputs

| file | what | version | notes |
|---|---|---|---|
