# C15: in-slab depth options (one layer against three, lower depth, rupture geometry)

**Scope changed (Pablo, 16 Nov):** C15 builds the depth cell tables only (steps 1 and 2 and the w1 check; done, `model/inslab/REPORT_C15.md`). Step 3 (rupture geometry), the source files, the one-city check and the "negligible" threshold go to S2; the hazard runs to S5.

Read `CLAUDE.md` first, including the section on parallel sessions. Then read `PLAN.md`, `DECISIONS.md` (In-slab, Classification, run settings) and `LEARNINGS.md`, and then `model/inslab/REPORT_C14.md` and `REPORT_S2.md`.

Work in `model/inslab/` and keep the C14 and S2 files as they are; new outputs get new dated names. Tests go in `model/inslab/tests/`. You may run everything here yourself, including small OpenQuake checks at one or a few sites. Pablo makes the hazard runs: write the job files and the commands into the WORKLOG.

## Why

C14 built the depth model and S2 wrote it into the in-slab sources with two layer options: three hypocentres (`l3`) and one (`l1`). Four points are still open:
- **One-layer hypocentre:** it is not right yet (step 1).
- **One layer or three:** not tested in hazard. If the difference is negligible, the three layers are dropped (Pablo, 15 Nov).
- **Lower seismogenic depth:** only one option exists, 0.475 of the Slab2 thickness.
- **Rupture geometry:** not set as options.

## Step 1: one-layer hypocentre

**Now.** `h_one` is the kernel-weighted median of the events inside the zone, per cell (C14; S2 uses it). It jumps by about 10 km at the 50 km contour of the slab top:
- 20–23 km below the top where the top is shallower than 40 km
- 11 km below the top where the top is 50–70 km deep

That is a line running along the margin, and the depth shifts across it in longitude. It comes from the classification, not from the slab. Over the shallow slab (top ≤ 50 km), an event within ± 15 km of the top counts as interface (A7, Haynie et al. 2026). So the in-slab events there start about 15–20 km below the top (5 % quantile 17–21 km).

**Proposal: one rule, no per-cell median.** Put `h_one` at the slab top + 0.25 × the Slab2 thickness. 0.25 is the median of d / thickness over all the events of the depth model:
- 0.248 inside the zone, 0.252 over all events
- close to the zone middle (0.2375)

It is measured the same way as the 0.475 of the lower depth. Report it for latitude bands, for top ≤ 50 and > 50 km, for the catalogue and Riedel-Hornig separately, and against the zone middle. Pablo picks between 0.25 and the zone middle.

**The same cut in the three slices.** The top-slice weight w1 is 0.2–0.3 where the top is shallower than 40 km and 0.5 where it is 50–70 km deep. Show how much of that is the class band. One check: recompute the weights over the shallow slab with the top 15 km of the zone left out. Propose a fix only if the artefact is clear, for example:
- the shallow-slab cells take the weights of the cells just downdip
- or the top slice starts at the edge of the interface band

Report it; Pablo decides.

## Step 2: lower seismogenic depth options

- **Reference:** 0.475 of the thickness (C14, DECISIONS).
- **Options with a source:**
  - 0.65, the old psha_chile7 rule
  - 0.615, the same 95 % fraction with all depth sources kept (C14 sensitivity, `fraction_2026-11-16.csv`)
- Propose which of them become tornado options. For each one, write the cell table with the same slice rule and the same hypocentre rule as the reference (step 1).
- Report how often a rupture reaches the lower depth, by magnitude, under the OpenQuake 3.26 placement checked in C14.

## Step 3: rupture geometry options

- **Now.** Point sources with the magnitude-scaling relation, aspect ratio and nodal planes of S2 (B14 from S5). Ruptures are centred on the hypocentre and kept inside the zone.
- **Options.**
  - The scaling relation for in-slab events: Strasser et al. (2010) intraslab against the S2 relation.
  - The aspect ratio.
  - How a rupture taller than the zone is handled: width capped and length extended, the OpenQuake rule.

  Use only relations that are in `refs/` or in REFERENCES.md; add any missing paper first.
- Show the rupture dimensions at Mw 6, 7 and 8 for each option, against a few well-studied in-slab events: Tarapacá 2005, Chillán 1939, Punitaqui 1997, Calama 1950 (only if its source has dimensions). Read Beck et al. (1998) and the Tarapacá papers yourself and add them to `refs/` (open in C14).
- Propose which options enter the tornado.

## Step 4: hazard comparison set-up

- **Layers.** Rebuild the S2 files only for the changed depths, on `depth_cells_2026-11-16.csv` (identical to 2026-11-15e). The `l1` branch gets the step 1 rule, and the `l3` branch too if step 1 changes the weights. New file names; the S2 files stay.
- **Jobs.** Write the job files for Pablo, at the tornado cities of psha_chile7:
  - one layer against three, reference tree, PGA and SA(1.0), 475 and 2475 years
  - one run at `pointsource_distance` 500 km at two or three cities, so that the collapse to one depth beyond 100 km does not hide the depth effect (REPORT_S2, section 4)
  - the step 2 and 3 options chosen for the tornado
- **"Negligible".** Propose a threshold for dropping the three layers, as a change in ground motion at both return periods, with a source if one exists. Pablo decides.
- **Quick check.** Run one small OpenQuake check yourself: one city, a reduced source set. It shows that the jobs run and that the depth options change the ground motion in the expected direction.

## South of 36° S

The events thin out, and the slice weights there come partly from 33–36° S. Say whether one layer should be the rule south of 36° S, independent of the tornado result, with the numbers of `south36_layers_2026-11-15.csv`.

## Not in this task

- The rates, the map pattern, Mmax, the classes, and the 0.475 rule itself (only alternatives are added).
- Hazard runs beyond the small check.
- Changes in `catalog/` or `fits/`. If one is needed, propose it in the WORKLOG.

## Done when

- The cell tables of the options exist with DATA rows: one-layer rule, w1 check, lower-depth options.
- The rebuilt `l1` (and `l3`) source files and the job files exist.
- `model/inslab/REPORT_C15.md` gives:
  - the step 1 numbers and the w1 check
  - the lower-depth and geometry options with their rupture dimensions
  - the proposed tornado rows and the "negligible" threshold
  - the south of 36° S recommendation
  - the proposed DECISIONS and LEARNINGS lines
- WORKLOG entry with the commands for Pablo; C15 ticked in PLAN when Pablo has the jobs.
