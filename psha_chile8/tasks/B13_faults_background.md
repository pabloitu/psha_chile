# B13: crustal faults and background join cleanly at Mw 6

Read `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (sections Statistics, Crustal and faults, Magallanes–Fagnano) and `LEARNINGS.md` first. Work in `model/crustal/`. Tests in `model/crustal/tests/`. You may run everything in this task yourself (no OpenQuake jobs).

## Why

The crustal hazard is carried by two sources:

1. A smoothed background per crustal class: forearc, arc, backarc, Patagonia.
2. Active faults whose rates come from slip rates.

Near each fault the background above Mw 6.0 is reduced and the fault takes over from 6.0. The join is the linear taper of the US NSHM 2023 over 12 km (DECISIONS, 15 Nov; step 4); psha_chile7 cut the background at 6.0 inside 5 km buffers. The result was never checked on the whole domain. The check asks two things:

- Do the background left in place plus the faults give the rate the catalogue fit gives, at Mw ≥ 6, 6.5 and 7?
- Is there a jump at Mw 6.0 inside the buffers?

In psha_chile7 the faults carried about 21 % of crustal N(≥ 6): 0.13 against 0.62 per year (`claude/FORECAST_v2.md`, item 5). The paper's question includes the hazard increase from faults, so faults are always in (DECISIONS). This task measures the join; it does not remove the faults.

## Inputs

Copy each into `psha_chile8/data/` as a dated file with its sha256, and give it a row in `DATA.md`:

- **Fits:** `fits/tables/fits_2026-11-15.csv`, both shapes, with `fits/gr.py` for the bin rates.
- **Catalogue:** the frozen catalogue `catalog/frozen/2026-11-14/` (class weights, completeness table of DECISIONS).
- **Faults, two databases (Pablo, 15 Nov):** A, the clean GEM database of D16 (`data/faults/faults_<date>.gpkg`), and B, MASCSN26 for Chile plus GEM outside Chile (`data/faults/faults_B_<date>.gpkg`, D16b, with our rules). Run steps 1–4 for both and give every table and figure for A and B side by side; stop if D16b is not done. For A: with its field description `model/faults/FIELDS.md` and the D16 proposals for Magallanes–Fagnano. Stop if D16 is not done. Do not read the area-source fields of the old shapefile: they are removed in D16.
- **Grid and arc:** the crustal grid `../ssm/data/grid_01_crustal.csv`; the arc polygon `data/intraarc.shp`.
- **Old code (read only):**
  - `psha_chile7/crustal/s03_faults.py` (moment balance, the six MFD shapes, the Mmax branches, the Fagnano system, down-dip-aware buffers)
  - `s02_ssm.py` and `lib/smooth` (kernel)
  - `s04_sources.py` (the cap)
  - `config.py` (settings)

  Port what you need into `model/crustal/` in the house style. Do not import from psha_chile7.

## Step 1: fault sources

- **Port the fault code.** The settings are those of DECISIONS (Crustal and faults):
  - moment rate ψ μ L W slip, with μ 30 GPa
  - ψ 0.6 / 0.8 / 1.0
  - Mmax: Leonard 2014 from the fault area (system area where segments are joined), one value. Sensitivity (report only, not a branch): every fault takes the background Mmax of its crustal class (observed maximum + 0.2); give the fault rates at Mw ≥ 6, 6.5, 7 under both and say how much moment moves to large magnitudes. It would become a branch only with multi-fault ruptures (DECISIONS)
  - MFD shapes AL-I, AL-II, AL-III, Youngs–Coppersmith, tapered, hybrid, 1/6 each
  - seismogenic depth 10 / 20 km
  - fault Mmin 6.0
  - the zone around each fault: cells within 12 km (3-D) of the fault surface for the taper, and the old 5 km down-dip-aware buffer for the comparison
- **Bin grid:** the same 0.1 bin edges as `gr.rates`, so fault and background bins line up.
- **Magallanes–Fagnano:** use the D16 proposal Pablo accepted in DECISIONS; if none is accepted yet, the psha_chile7 system rule, stated as provisional.
  - List which segments are read. The Puerto Williams result changed from 0.10 g to 0.02 g between runs, probably because the Fagnano segments were missing. Make sure they are present, and say how many are read and how many are skipped, with the reason.
- **Tests:**
  - every shape returns the target moment rate
  - Mmax lands on the bin grid
  - buffers contain their trace
- **Fault b:** the old code took an area-zone b from the database. Compare the b of the crustal class the fault lies in (B11) with 0.8 and report the effect on fault N(≥ 6); use the class b in the reference unless the report shows a reason.

## Step 2: background

- **Rates:** per class, from the fits of B11, both shapes. The bin rates come from `gr.rates`; a and b are never re-entered (DECISIONS).
- **Spatial pattern:**
  - Port the psha_chile7 crustal kernel: power law, power 1.5, 15 neighbours, cut at 500 km, minimum 5 km.
  - Use the declustered events for the pattern only (DECISIONS: rates from the full catalogue, pattern declustered). Gardner–Knopoff as in psha_chile7.
  - Weight the events by their class weight.
  - Normalize the pattern and scale it to the class rate.
- **Total grid:** the per-bin sum over the classes, before the cap.
- **Figures:** a map of N(≥ 5) per class.

## Step 3: the check (main result)

**Table.** One table per class and for the whole crustal domain, at Mw ≥ 6.0, 6.5 and 7.0, with these columns:

| column | what |
|---|---|
| fit | catalogue fit of the class, each shape |
| observed | weighted count inside the completeness table, per year |
| bg outside | background outside the buffers |
| bg removed | background removed near the faults by the join (taper; cap as the comparison) |
| faults | summed fault rate: weighted mean over the fault tree, plus the lowest and highest branch |
| total | bg outside + bg inside below 6.0 + faults |
| total / fit | the ratio |

Also give the observed events of Mw ≥ 6 inside and outside the buffers, with their class, year and Mw.

**Join at Mw 6.0.** Summed over the buffers, give the incremental rate of the background bin 5.9 against the fault bin 6.0:
- per class and domain-wide
- for the weighted fault tree and its extreme branches

Flag a jump larger than ×2 in either direction.

**Figures:**
- per class, the incremental and cumulative MFD with:
  - the fit band (5–95 % of the bootstrap)
  - the observed series per completeness period
  - the background outside the buffers
  - the background inside the buffers
  - the faults (weighted mean and range)
  - the total
- a map of the fault share of N(≥ 6) per cell
- a map of the buffers on the background N(≥ 6)

## Step 4: the join

Four joins, the last one the reference:

- **Rate balance:** the background inside each buffer is reduced, not removed, so that background plus faults inside the buffer match the catalogue fit above 6.0, never below zero.
- **No cap:** faults added on top of the full background. This is the upper bound of double counting.
- **Cap at 6.0 in 5 km buffers:** the psha_chile7 join, kept only as the comparison.
- **Reference join, the US NSHM 2023 linear taper (DECISIONS, 15 Nov).** Field et al. 2024 (BSSA 114, 523–571, doi 10.1785/0120230120, section "Merging with other source models"; free manuscript at https://par.nsf.gov/servlets/purl/10503871), read by Pablo on 15 Nov. What it says, and how we apply it:
  1. *Totals:* the gridded MFD is the regional target minus the summed fault MFD, with negative values set to zero (above the gridded Mmax, or where the faults exceed the target, the "bulge"). Ours: per crustal class, background above 6.0 = catalogue fit of the class minus the summed fault MFD of the faults in that class, bin by bin, never below zero. Below 6.0 the background is the fit. Report every bin and class with a bulge (faults above the fit) and its size.
  2. *Magnitudes:* the taper applies to the magnitudes the faults carry (their supraseismogenic range). Ours: background bins from 6.0, the fault Mmin.
  3. *Distance (simple version, Pablo 15 Nov):* weight w = min(d / 12 km, 1), with d the 3-D distance from the cell's background hypocentre (10 km depth) to the fault surface. Several faults: the smallest w. No depth cubes, no nucleation-depth profile, no further literature for this.
  4. *Spatial share:* the background above 6.0 of each class is spread by its smoothed pattern times w and renormalized, so its class total stays as in point 1.
  5. *Faults:* their ruptures stay on the fault surfaces as they are.

  Show maps of N(≥ 6) and N(≥ 6.5) across three typical faults (strike-slip Liquiñe–Ofqui, reverse San Ramón, normal Atacama): there should be no hole near the fault. In the step-3 table this join matches the fit by construction except in bulge bins, so the bulge is the check.

For the paper, also say in a few lines how ESHM20 (Danciu et al. 2021) and the New Zealand NSHM 2022 join faults and background, and how UCERF3 did it (Field et al. 2014: fault-zone polygons, 12 km on each side of vertical faults, scaling with dip; gridded events inside the polygons assigned to the fault). Give the reference with the page.

Read the source before citing it. Mark what you could not read. For each alternative give the same table as step 3 at Mw ≥ 6 and 6.5. Build the reference join; the others are columns of the table only. The hazard effect of cap against taper is checked later in the tornado (E17).

## Step 5: large events and the background Mmax (report only)

In psha_chile7 two kinds of event were removed by hand:
- Aysén 1960-06-06 from the arc
- the Magallanes–Fagnano events from the Patagonian background

Those are single-event rules, and DECISIONS no longer allows them. Report:
- the crustal events of Mw ≥ 6.5 inside the buffers, with the fault each one lies on
- the background Mmax (observed + 0.2) of each class with and without the events inside buffers

Then propose at most two general rules, one sentence each, with their effect on the background Mmax and N(≥ 7). One of them must be "no rule, all events count". Pablo decides.

The DECISIONS open item on the Kanamori intra-arc event (> 7.5): say whether it is Aysén 1960 (Mw 7.7 in the frozen catalogue, Kanamori and Rivera 2017), which class it has, and what it sets.

## Outputs

- `model/crustal/` code with tests (pytest passes)
- `model/crustal/REPORT_B13.md`: simple and explanatory, written for a seismologist who is not a catalogue specialist. Main numbers first, then method, then open points with proposed DECISIONS lines.
- tables in `model/crustal/tables/`, dated
- figures in `model/crustal/figs/`, with rows in `FIGURES.md` for paper candidates
- no NRML files and no OpenQuake runs; those are plan F

## At the end

Follow `CLAUDE.md`. Another Claude Code session runs C14 at the same time and also appends to `WORKLOG.md`: re-read the file just before appending. Tick B11 and B12 in `PLAN.md` (Pablo reviewed them on 15 Nov). In this task "buffer" means the 12 km zone of the taper unless the old cap is named. Tick B13 only if the join is within ×2 and the domain total is within the 5–95 % band of the fit; otherwise leave it open and say why. Move the ← marker.
