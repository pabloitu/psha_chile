# CURRENT: the inputs everything reads

One line per published input. The owner session updates its line when it publishes a new dated file or folder, in the same step as the DATA.md row. Everyone else reads inputs from here, not from dates remembered or hard-coded. A folder still being written is listed under "in progress" and is not read by others.

Last full check: 17 Nov 2026, 14:10 (main conversation, wrap-up; every owner checked its lines in the close-out notes).

## Catalogue (owner: CAT, sessions A6 / A7)

| input | current | note |
|---|---|---|
| source catalogs (A2, A2b) | `catalog/sources/<name>_2026-11-10_{events,mags,mechs}.csv` (11 sources), `gccel_2026-11-11_*`; `sources/MANIFEST.csv` (sha256) | read by `match.py`; downloaded 10 Nov, unchanged since (commits c3ecf3b, 3bb70b3); raw in `sources/raw/` (not in git) |
| frozen catalogue (final) | `catalog/frozen/2026-11-17g/catalog_2026-11-17g.csv` | final catalogue (Pablo, 18 Nov, CAT); 17f with the A11 merges (44 events, `duplicates.csv` and the ISC-copy rule) and the conversions with three depth groups (below 150 km); 14 416 events of Mw ≥ 4.5 in the domain; handoff `handoffs/2026-11-18_CAT_to_FITS_17g.md` |
| catalogue the fits and models are built on | `catalog/frozen/2026-11-17g/catalog_2026-11-17g.csv` | fits 2026-11-18 (FITS, 18 Nov); the models rebuild on it (`handoffs/2026-11-18_FITS_to_IF_IS_CR.md`) |
| overrides | `catalog/overrides_A6.csv` | per-event corrections of event properties: 119 accepted, 8 superseded, none proposed; identical to the copy in `frozen/2026-11-17g/` (all applied); applied by `locate.py` (location, depth, mechanism, class hint) and `magnitude.py` (Mw) as their last step |
| duplicates | `catalog/duplicates.csv` | reviewed merges (22 accepted: event, kept event, reference, reason); with the ISC-copy rule read by `locate.py` and `magnitude.py` before they choose location and Mw; merged events of a run in `merged/review/duplicates_merged_<run>.csv` and in the freeze |
| named events | `catalog/named_events.csv` | events named in the literature (88), label flag and label positions of the mechanism map; add a row for every event cited in the paper |
| matched events and links (A3) | `catalog/merged/events_2026-11-11.csv`, `links_2026-11-11.csv` (`windows_`, `review/`) | 204 956 events; read by `locate.py` and `magnitude.py`; unchanged since the rerun of 11 Nov (commit 2267cc9) |
| declustered catalogues | `catalog/declustered/*_2026-11-18.csv` | built on catalogue 17g (owner: FITS) |

## Fits (owner: FITS, session B11/B12)

| input | current | note |
|---|---|---|
| fits, full catalogue | `fits/tables/fits_2026-11-18.csv` | on catalogue 17g; in-slab from 1964 |
| fits, declustered | `fits/tables/fits_declustered_2026-11-18.csv` | |
| completeness table | `fits/tables/table_2026-11-18.csv` | measured on 17g (segments: `mc_table_2026-11-18.csv`) |
| Mmax pad 0.0 / 0.4 | `fits/tables/fits_2026-11-18_pad00.csv`, `_pad04.csv` | ML rows, tornado only |

## Interface (owner: IF, session S1)

| input | current | note |
|---|---|---|
| sources and tree | `model/interface/nrml_2026-11-18/` (`tree.json`, `tornado.json`; `branches.json` lists the variants) | on fits 2026-11-18, catalogue 17g; final tree confirmed (Pablo, 18 Nov); declustered branch `nn_family` as the placeholder; OpenQuake parse check calcs 643–645; `nrml_2026-11-16c/` and older superseded |

## In-slab (owner: IS for the sources; FITS for depth cells, class shares and nodal planes, from 18 Nov)

| input | current | note |
|---|---|---|
| depth cells, three layers (reference) | `model/inslab/tables/depth_cells_2026-11-18.csv` | C16 on catalogue 17g, events with their class weights (C15 rules); replaces `depth_cells_2026-11-16.csv` (weight-1 events) as the reference (DECISIONS, In-slab) |
| depth cells, one layer and lower depth | `model/inslab/tables/depth_cells_2026-11-18.csv` (`h_one`), `depth_cells_lsd065_2026-11-18.csv`, `depth_cells_lsd0615_2026-11-18.csv` | C16 run 2026-11-18 (class weights), catalogue 17g; the same file as the reference holds `h_one` |
| sources and tornado rows | `model/inslab/nrml/2026-11-18i/` (`tree.json`, `tornado.json`, `branches.json`) | IS build `2026-11-18h` on catalogue 17g, fits 2026-11-18, depth cells 2026-11-18, `npd_2026-11-18.csv`: one nodal plane per cell (representative plane of the dominant type of the sub-class of its domain), pattern completeness from 1964; 6 tree branches (full / declustered `nn_family` × (a, b)), 12 tornado rows (declustered rates inside); rates as `2026-11-18e` / `18g` (superseded; 18e kept for the city jobs that hard-link it); `handoffs/2026-11-18_IS_to_HAZ.md` |
| class shares per cell | `model/inslab/tables/class_share_2026-11-16.csv` | for the nodal planes at S5; to be replaced by the `class_share_check_<RUN>.csv` of IS's build on fits 2026-11-18 (FITS publishes it) |
| nodal planes, all classes | `model/mechanisms/npd_2026-11-18.csv` | B16 on catalogue 17g, per-class tables of the fits 2026-11-18; crustal rows identical to 16d; intermediate in-slab reverse now kept (0.10) |

## Crustal (owner: CR, sessions S3, D16)

| input | current | note |
|---|---|---|
| fault database A | `data/faults/faults_gem_extra_2026-11-15.shp` | |
| fault database B | `data/faults/faults_B_2026-11-15.gpkg` | D16b: 166 faults, MASCSN slips as restored FaultQuake inputs (`t_fq`, `scr_fq`, `tmean_fq`); B-mm moment from `model/faults/compare.py` `budget`; rebuilt MASCSN model `model/faults/nrml/mascsn26_rebuilt_scc{10,075,05}_2026-11-15.xml` (reference only) |
| crustal grid | `data/crustal_grid_01_2026-11-15.csv` | |
| sources and tree | `model/crustal/nrml/2026-11-18b/` (`tree.json`, `tornado.json`, `branches.json`) | final build (CR, 18 Nov): thickness 20 km fixed, 60 paths, 19 tornado rows (no thickness row); parse check 117 files, 348 393 sources, none missing, rates within 3.8e-6; otherwise as the first build of the day on catalogue 17g, fits 2026-11-18, declustered 2026-11-18, npd 2026-11-18; database A in the tree (single / multi-fault 0.5 / 0.5, single-fault pad, ψ, thickness, shape, LOFS secondary traces; 120 paths), B and B-mm single-fault tornado rows; source Mmin 5.0 (Pablo, 18 Nov), pattern `nn` (placeholder); San Ramón 44 km; 20 tornado rows; manifest check and parse check passed; tree confirmed by Pablo (18 Nov), `"ready": true`; note `handoffs/2026-11-18_CR_to_HAZ.md` |
| superseded | `model/crustal/nrml/2026-11-18/` (both thicknesses, 120 paths), `2026-11-16g/`, `2026-11-16e/` | 16g: fits 16f, old San Ramón trace, ψ means 0.25 / 0.5 / 0.25 in the join, tree and tornado mixed in `branches.json`; hazard results on it are from before |

## Ground motion (owner: GMM, session GM1)

| input | current | note |
|---|---|---|
| GMM sets | `gmm/tables/gmm_sets_2026-11-15.csv` (made by `gmm/summary.py`) | column `set`: A = GMM-FIT, B = GMM-1R, C = GMM-CSN, D = GMM-GEM; equal weights; Vs30 800; Idini 2017 needs soiltype 1 |

## Hazard (owner: HAZ, session S5)

| input | current | note |
|---|---|---|
| jobs and code | `hazard/` (`jobs.py`, `config.py`, `build.py`) | reads `tree.json` (final trees) and `tornado.json` (rows) of the three folders above (HAZ, 18 Nov); jobs built in `hazard/jobs/`, not yet run; grid `hazard/sites/grid_005_2026-11-18.csv` |
| tornado results | `hazard/out/` (`tornado/`, `tornado_prelim/`, `tornado_full/`, `tornado_matrix/`, `trees/`, `curves/`, `shares/`) | all three families on the folders above: interface 16c, in-slab 16c + 16d, crustal 16g (calcs 522–642; crustal 614–642); family folders read from this file by `hazard/config.py`; job calc ids in `hazard/jobs/<job>/build.json` |
