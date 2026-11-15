# C14: in-slab depth model (three layers below the slab top)

Read `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (sections In-slab, Classification, Statistics) and `LEARNINGS.md` first. Work in `model/inslab/`. Tests in `model/inslab/tests/`. You may run everything in this task yourself (no OpenQuake jobs).

## Why

The in-slab source is one point source per grid cell. Each cell has three hypocentral depths and three weights, measured vertically below the Slab2 top (DECISIONS, In-slab, 13 Nov).

- **Double zone:** where one exists, it shows as weight in the top and bottom layers, without a yes / no decision.
- **Map pattern and rates:** stay 2-D (B11 fits). This task only builds the depth part.
- **Tornado:** one layer against three is a factor. If the change in hazard is negligible, the three layers are dropped (Pablo, 15 Nov).

## Inputs

Copy each into `psha_chile8/data/` as a dated file with its sha256, and give it a row in `DATA.md`:

- **Riedel-Hornig catalogue:** `explore/X5/data/riedel_hornig_2026-11-14/Riedel-Hornig_et_al_Primary_Catalogue.csv`. Riedel-Hornig et al. 2026, Zenodo 10.5281/zenodo.15284376, 2017–2021, 18–43° S, depth error about 6 km.
  - Do not commit it. `explore/*/data/` and the dated copy go in `.gitignore`. Record the source, the sha256 and the size in `DATA.md` instead.
- **Frozen catalogue:** `catalog/frozen/2026-11-14/`, with class weights, depth kind and depth σ.
- **Slab2:** `../data/slab_2.0/sam_slab2_dep_02.23.18.xyz` (top), `_thk_` (thickness) and `_unc_` (uncertainty of the top).
- **Grid:** the in-slab grid of psha_chile7, `../ssm/data/grid_01.csv`. Restrict it to cells where the slab exists.
- **Old code (read only):** `psha_chile7/intraslab/`. It has the old thickness-fraction depths (0.30 and 0.65 of the Slab2 thickness) and the class-domain logic. Port what you need.

## Step 1: freeze and benchmark Riedel-Hornig

- **Read and summarize:** columns, number of events, magnitude type and range, depth error distribution.
- **Match to the frozen catalogue for 2017–2021.** Use the A3 rules in simple form: origin time within 10 s, epicentre within 50 km, one to one. Report the match rate by depth and latitude.
- **Depth differences on the matched events,** median and spread, against:
  - Potin / CSN web
  - GCCEL
  - ISC-EHB L1 / L2
  - ISC

  Split them:
  - by depth (0–70, 70–150, 150–300 km)
  - by distance from the trench
  - for the flat slab (about 27–33° S) on its own

  Two points need care:
  - The authors say the eastern hypocentres are too deep without Argentine stations (their p. 12–13). Show it.
  - Show whether Potin under the flat slab agrees with Riedel-Hornig. GCCEL cannot test that.
- **Location source:** say in one paragraph whether Riedel-Hornig should become a location source of the catalogue for 2017–2021 (DECISIONS leaves this open). Report only.

## Step 2: depth below the slab top

- **Distance below the top:** for every depth event, the vertical distance from the Slab2 top at its epicentre, d = depth − top.
- **Events used:**
  - Riedel-Hornig events.
  - Catalogue in-slab events with measured depth and σ ≤ 5 km, weighted by precision and by class weight.

  Left out:
  - the Jujuy nest (DECISIONS)
  - Potin depths under the flat slab
  - Riedel-Hornig events in the eastern part the authors flag
  - assigned and unknown depths

  Each event counts once, at its depth. It is not spread over layers by its error (DECISIONS).
- **Interface events:** state how they are kept out of the in-slab set:
  - catalogue: by the A7 class weights
  - Riedel-Hornig, which has no class: by the same ± 15 km band and the Haynie et al. scores used in A7, applied to its depths

  Report how many events each rule removes.
- **Figures:**
  - histograms of d per latitude band
  - trench-normal sections showing d, with the Slab2 top and the slab bottom (top + thickness)

  The double zone should be visible where it is known: northern Chile about 18–24° S, and central Chile. Say where it is and where it is not.

## Step 3: layers

- **Layer bounds per region:** from the central 95 % of d, cut in three (DECISIONS).
  - Compare two cuts: equal thirds of the 95 % range, and equal numbers of events.
  - Compare at least three ways to define the regions:
    - 2° latitude bands
    - slab-top depth bins (shallow ≤ 50 km, 50–150 km, 150–300 km)
    - the two combined

    Pick the simplest one whose bounds are stable under an event bootstrap (2 000 resamples). Report the bounds with their bootstrap spread.
- **Weights per cell:** the share of the nearest well-located events in each layer.
  - Test 25, 50 and 100 neighbours, and a fixed radius of 50 km.
  - Pick by a held-out check: keep out 2020–2021, and compare the predicted layer shares with the observed shares of those events (log-likelihood per event).
- **Hypocentre per cell and layer:** the median d of those neighbours in that layer. Use the layer middle where fewer than 5 events fall in the layer.
- **Upper and lower seismogenic depth per cell:** the top and bottom of the three layers (slab top to the bottom of the 95 % range).
  - Confirm in the installed OpenQuake code how a point source places ruptures relative to the hypocentre and these two depths. Do this with `python -c "import inspect, openquake.hazardlib.source.point as p; print(inspect.getsource(p))"` or similar; do not list the `oq-engine/` folder.
  - Say in one paragraph whether a large rupture with its hypocentre in the top layer still fills the zone down to the lower depth.
- **One layer (for the tornado):** the same cells, one hypocentre at the median d of all neighbours, the same upper and lower depths.

## Step 4: checks

- **Weight maps:** one map per layer, plus a map of the "double-zone index": the top and bottom weight against the middle weight.
- **Sections:** at 20°, 23°, 30°, 33° and 38° S, the cell hypocentres and weights drawn over the events.
- **Hypocentre depths:** compare the new depths with the old thickness-fraction depths of psha_chile7, cell by cell. Map the differences.
- **Tests:**
  - weights sum to 1 in every cell
  - hypocentres lie within their layer
  - upper depth < every hypocentre < lower depth
  - on a synthetic slab with a known double zone, the method recovers its layer shares

## Outputs

- **Code:** in `model/inslab/`, with tests (pytest passes).
- **Cell table:** `model/inslab/tables/depth_cells_<date>.csv`, one row per cell, with:
  - lon, lat, slab top
  - three hypocentres and three weights
  - upper and lower depth
  - the one-layer hypocentre
  - the number of events used
- **`model/inslab/REPORT_C14.md`:** simple and explanatory, written for a seismologist who is not a catalogue specialist. Order:
  1. what the layers look like and where the double zone shows
  2. the benchmark
  3. the choices made, with proposed DECISIONS lines
  4. open points
- **Figures:** in `model/inslab/figs/`, with rows in `FIGURES.md` for paper candidates. Use the house figure style: sections perpendicular to the Nazca trench, gray basemap, pituPLOTS.
- **Not here:** no NRML files, no OpenQuake runs.

## At the end

Follow `CLAUDE.md`. Another Claude Code session runs B13 at the same time and also appends to `WORKLOG.md`: re-read the file just before appending. Tick C14 in `PLAN.md` when the cell table exists and the tests pass.
