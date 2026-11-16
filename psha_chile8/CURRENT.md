# CURRENT: the inputs everything reads

One line per published input. The owner session updates its line when it publishes a new dated file or folder, in the same step as the DATA.md row. Everyone else reads inputs from here, not from dates remembered or hard-coded. A folder still being written is listed under "in progress" and is not read by others.

Last full check: 16 Nov 2026, 21:30 (main conversation).

## Catalogue (owner: CAT, sessions A6 / A7)

| input | current | note |
|---|---|---|
| frozen catalogue | `catalog/frozen/2026-11-16e/catalog_2026-11-16e.csv` | as 16c, with Aysén 1960 and 1927-11-21 at the ISC-GEM epicentre |
| catalogue the fits and models are built on | `catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv` | refit on 16e on hold (Pablo, 16 Nov) |
| overrides | `catalog/overrides_A6.csv` | |
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
| sources and tree | `model/interface/nrml_2026-11-16c/` (`branches.json`) | on fits 16f; pad rows inside |

## In-slab (owner: IS, sessions S2, C14/C15, B14)

| input | current | note |
|---|---|---|
| depth cells, three layers (reference) | `model/inslab/tables/depth_cells_2026-11-16.csv` | |
| depth cells, one layer and lower depth | `model/inslab/tables/depth_cells_2026-11-16d.csv`, `depth_cells_lsd065_2026-11-16d.csv` | C15 |
| sources and tornado rows | `model/inslab/nrml/2026-11-16c/` (`branches.json`) | one source per cell; pad, one layer, lower depth, Allen–Hayes |
| declustered-rate rows | `model/inslab/nrml/2026-11-16d/` | tornado only |
| class shares per cell | `model/inslab/tables/class_share_2026-11-16.csv` | for the nodal planes at S5 |
| nodal planes, all classes | `model/mechanisms/npd_2026-11-16d.csv` | B14 final |

## Crustal (owner: CR, sessions S3, D16)

| input | current | note |
|---|---|---|
| fault database A | `data/faults/faults_gem_extra_2026-11-15.shp` | |
| fault database B | `data/faults/faults_B_2026-11-15.gpkg` | |
| crustal grid | `data/crustal_grid_01_2026-11-15.csv` | |
| sources and tree | `model/crustal/nrml/2026-11-16g/` (`branches.json`) | strict UCERF3 rupture set, thickness tags t10 / t20, 20 tornado rows, equal weights; on fits 16f, catalogue 16c, npd 16d; parse check passed |
| superseded | `model/crustal/nrml/2026-11-16e/` | old rupture set; hazard results on it are from before |

## Ground motion (owner: GMM, session GM1)

| input | current | note |
|---|---|---|
| GMM sets | `gmm/tables/gmm_sets_2026-11-15.csv` | GMM-1R, GMM-FIT, GMM-CSN, GMM-GEM |

## Hazard (owner: HAZ, session S5)

| input | current | note |
|---|---|---|
| jobs and code | `hazard/` (`jobs.py`, `config.py`) | reads the three `branches.json` above |
| tornado results | `hazard/out/` | interface and in-slab on the folders above; crustal on the earlier 16e files |
