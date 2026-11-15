# B13: crustal faults and background join cleanly at Mw 6

Read `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (sections Statistics, Crustal and faults, Magallanes–Fagnano) and `LEARNINGS.md` first. Work in `model/crustal/`. Tests in `model/crustal/tests/`. You may run everything in this task yourself (no OpenQuake jobs).

## Why

The crustal hazard is carried by two sources:

1. A smoothed background per crustal class: forearc, arc, backarc, Patagonia.
2. Active faults whose rates come from slip rates.

Inside a buffer around each fault the background is cut at Mw 6.0 and the fault takes over from 6.0 (DECISIONS). This was never checked on the whole domain. The check asks two things:

- Do the background left in place plus the faults give the rate the catalogue fit gives, at Mw ≥ 6, 6.5 and 7?
- Is there a jump at Mw 6.0 inside the buffers?

In psha_chile7 the faults carried about 21 % of crustal N(≥ 6): 0.13 against 0.62 per year (`claude/FORECAST_v2.md`, item 5). The paper's question includes the hazard increase from faults, so faults are always in (DECISIONS). This task measures the join; it does not remove the faults.

## Inputs

Copy each into `psha_chile8/data/` as a dated file with its sha256, and give it a row in `DATA.md`:

- **Fits:** `fits/tables/fits_2026-11-15.csv`, both shapes, with `fits/gr.py` for the bin rates.
- **Catalogue:** the frozen catalogue `catalog/frozen/2026-11-14/` (class weights, completeness table of DECISIONS).
- **Faults:** the clean database of D16, `data/faults/faults_<date>.gpkg`, with its field description `model/faults/FIELDS.md` and the D16 proposals for Magallanes–Fagnano. Stop if D16 is not done. Do not read the area-source fields of the old shapefile: they are removed in D16. The "observed + 0.2" Mmax branch needs an observed fault maximum; where the database has none, use the Leonard rule as psha_chile7 did for missing values, and report how many faults that affects.
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
  - Mmax: observed + 0.2 / Wells and Coppersmith 1994 / Leonard 2014, 1/3 each
  - MFD shapes AL-I, AL-II, AL-III, Youngs–Coppersmith, tapered, hybrid, 1/6 each
  - seismogenic depth 10 / 20 km
  - fault Mmin 6.0
  - buffers with a 5 km margin on the down-dip side
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
| bg removed | background removed inside the buffers by the cap |
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

## Step 4: alternatives for the join (report only)

Compare the cap of DECISIONS with at least these two:

- **Rate balance:** the background inside each buffer is reduced, not removed, so that background plus faults inside the buffer match the catalogue fit above 6.0, never below zero.
- **No cap:** faults added on top of the full background. This is the upper bound of double counting.

Check how three recent national or regional models join faults and background, and give the reference with the page:
- ESHM20 (Danciu et al. 2021)
- the New Zealand NSHM 2022
- the US NSHM 2023 or the Italian MPS19

Read the source before citing it. Mark what you could not read. For each alternative give the same table as step 3 at Mw ≥ 6 and 6.5. Say in one paragraph which you would keep and why. Do not change the model.

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

Follow `CLAUDE.md`. Another Claude Code session runs C14 at the same time and also appends to `WORKLOG.md`: re-read the file just before appending. Tick B11 and B12 in `PLAN.md` (Pablo reviewed them on 15 Nov). Tick B13 only if the join is within ×2 and the domain total is within the 5–95 % band of the fit; otherwise leave it open and say why. Move the ← marker.
