# CURRENT: the inputs everything reads

One line per published input. The owner session updates its line when it publishes a new dated file or folder, in the same step as the DATA.md row. Everyone else reads inputs from here, not from dates remembered or hard-coded. A folder still being written is listed under "in progress" and is not read by others.

Last full check: 16 Nov 2026, 21:30 (main conversation).

## Catalogue (owner: CAT, sessions A6 / A7)

| input | current | note |
|---|---|---|
| source catalogs (A2, A2b) | `catalog/sources/<name>_2026-11-10_{events,mags,mechs}.csv` (11 sources), `gccel_2026-11-11_*`; `sources/MANIFEST.csv` (sha256) | read by `match.py`; downloaded 10 Nov, unchanged since (commits c3ecf3b, 3bb70b3); raw in `sources/raw/` (not in git) |
| frozen catalogue | `catalog/frozen/2026-11-16e/catalog_2026-11-16e.csv` | as 16c, with Aysén 1960 and 1927-11-21 at the ISC-GEM epicentre |
| catalogue the fits and models are built on | `catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv` | refit on 16e on hold (Pablo, 16 Nov) |
| overrides | `catalog/overrides_A6.csv` | A6: 104 accepted, 8 superseded, none proposed; identical to the copy in `frozen/2026-11-16e/` (all applied); applied by `locate.py` (location, depth, class hint) and `magnitude.py` (Mw) as their last step |
| matched events and links (A3) | `catalog/merged/events_2026-11-11.csv`, `links_2026-11-11.csv` (`windows_`, `review/`) | 204 956 events; read by `locate.py` and `magnitude.py`; unchanged since the rerun of 11 Nov (commit 2267cc9) |
| declustered catalogues | `catalog/declustered/*_2026-11-16e.csv` | built on catalogue 16c (owner: FITS) |

## Fits (owner: FITS, session B11/B12)

| input | current | note |
|---|---|---|
| fits, full catalogue | `fits/tables/fits_2026-11-16f.csv` | on catalogue 16c |
| fits, declustered | `fits/tables/fits_declustered_2026-11-16f.csv` | |
| completeness table | `fits/tables/table_2026-11-16f.csv` | same steps since 15 Nov |
| Mmax pad 0.0 / 0.4 | `fits/tables/fits_2026-11-16f_pad00.csv`, `_pad04.csv` | ML rows, tornado only |

## Interface (owner: IF, session S1)

| input | current | note |
|---|---|---|
| sources and tree | `model/interface/nrml_2026-11-16c/` (`branches.json`) | on fits 16f; pad rows inside (`*_pad00`, `*_pad04`, tornado block); `nrml_2026-11-16/` and `nrml_2026-11-16b/` superseded |

## In-slab (owner: IS, sessions S2, C14/C15, B14)

| input | current | note |
|---|---|---|
| depth cells, three layers (reference) | `model/inslab/tables/depth_cells_2026-11-16.csv` | |
| depth cells, one layer and lower depth | `model/inslab/tables/depth_cells_2026-11-16d.csv` (`h_one`), `depth_cells_lsd065_2026-11-16d.csv`, `depth_cells_lsd0615_2026-11-16d.csv` | C15 run 2026-11-16d (class weights), catalogue 16c; three-layer columns of 16d not used by the sources |
| sources and tornado rows | `model/inslab/nrml/2026-11-16c/` (`branches.json`) | one source per cell; pad, one layer, lower depth, Allen–Hayes |
| declustered-rate rows | `model/inslab/nrml/2026-11-16d/` | tornado only |
| class shares per cell | `model/inslab/tables/class_share_2026-11-16.csv` | for the nodal planes at S5 |
| nodal planes, all classes | `model/mechanisms/npd_2026-11-16d.csv` | B14 final |

## Crustal (owner: CR, sessions S3, D16)

| input | current | note |
|---|---|---|
| fault database A | `data/faults/faults_gem_extra_2026-11-15.shp` | |
| fault database B | `data/faults/faults_B_2026-11-15.gpkg` | D16b: 166 faults, MASCSN slips as restored FaultQuake inputs (`t_fq`, `scr_fq`, `tmean_fq`); B-mm moment from `model/faults/compare.py` `budget`; rebuilt MASCSN model `model/faults/nrml/mascsn26_rebuilt_scc{10,075,05}_2026-11-15.xml` (reference only) |
| crustal grid | `data/crustal_grid_01_2026-11-15.csv` | |
| sources and tree | `model/crustal/nrml/2026-11-16g/` (`branches.json`) | strict UCERF3 rupture set, thickness tags t10 / t20, 20 tornado rows, equal weights; on fits 16f, catalogue 16c, npd 16d; parse check passed |
| superseded | `model/crustal/nrml/2026-11-16e/` | old rupture set; hazard results on it are from before |

## Ground motion (owner: GMM, session GM1)

| input | current | note |
|---|---|---|
| GMM sets | `gmm/tables/gmm_sets_2026-11-15.csv` (made by `gmm/summary.py`) | column `set`: A = GMM-FIT, B = GMM-1R, C = GMM-CSN, D = GMM-GEM; equal weights; Vs30 800; Idini 2017 needs soiltype 1 |

## Hazard (owner: HAZ, session S5)

| input | current | note |
|---|---|---|
| jobs and code | `hazard/` (`jobs.py`, `config.py`) | reads the three `branches.json` above |
| tornado results | `hazard/out/` (`tornado/`, `tornado_prelim/`, `tornado_full/`, `tornado_matrix/`, `trees/`) | all three families on the folders above: interface 16c, in-slab 16c + 16d, crustal 16g (calcs 597–642); family folders read from this file by `hazard/config.py` |
