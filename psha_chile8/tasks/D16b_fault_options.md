# D16b: two fault databases, A (GEM) and B (MASCSN26 + GEM outside Chile)

Read `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` (Crustal and faults) and `LEARNINGS.md` first, then `model/faults/REPORT_D16.md` and `model/faults/FIELDS.md`. This task runs after D16 and before B13. Work in `model/faults/`, with tests in `model/faults/tests/`. You may run everything yourself.

## Why

Pablo wants to see what changes between two fault databases (15 Nov):

- **A.** The cleaned GEM/SARA database of D16 (`data/faults/faults_<date>.gpkg`).
- **B.** The crustal faults of the new official CSN hazard model (MASCSN26) for Chile, plus the cleaned GEM faults outside Chile (Argentina, southern Peru).

### What MASCSN26 is

Bravo Sagua, Koch, Urrutia, Cembrano, Rauld, Leyton and Barrientos (2026), *Modelo Probabilístico de Amenaza Sísmica para Chile Continental*, v1.1, CSN, Universidad de Chile, April 2026. The PDF is at `../refs/faults/Mapa_Amenaza_CSN2026.pdf`. Page numbers below are those printed in the report; check them.

**Database (ch. 5, from p. 63; §5.3, p. 74–76):**
- It starts from CHAF (Maldonado et al. 2021) and keeps the "proved" and "probable" faults only.
- It is checked against GEM, SARA, the Atacama database (Mittelstädt and Victor 2020) and the forearc database (Vega-Ruiz et al. 2025), with updates: Cerro Aguirre, San Ramón extended to Pirque, Cariño Botado.
- It adds the Magallanes–Fagnano system.
- Slip rate, dip, rake and depths come from the literature, or from the fault's system where there is no study. The system values are in Table 17 (p. 77); for example Liquiñe–Ofqui 4–12 mm/yr and Magallanes 6–7 mm/yr.

**Hazard version (§5.4, p. 80–81):**
- segments of one system with the same kinematics and less than 5 km apart are joined
- subsidiary faults within 3 km of a main one are dropped
- traces are simplified, and faults shorter than 5 km are dropped

**Source model (§8.3–8.4, p. 127–128):**
- Mmax per fault from FaultQuake (Tavakolizadeh et al. 2024); faults with Mmax below 6 are dropped.
- Truncated GR from Mw 6 to Mmax, with b from the crustal zone of the fault and a from the moment balance with the slip rate.
- Seismic coupling coefficient SCC 1 / 0.75 / 0.5, weights 0.25 / 0.5 / 0.25.
- Background with a 50 km Gaussian kernel, Mmax 7, cut at Mw 6 inside 5 km buffers.

**Gap:** the per-fault database (fields `BDslipr`, `BDdip`, `BDzmin`, `BDzmax` and refs) is described but not published. The repository (github.com/frabravo/MASCSN26, commit 73b5a8d) has only the OpenQuake files. Two of them are copied for you:
- `data/faults/mascsn26/mascsn26_faults_scc1_2026-11-15.xml` (sha256 5c264860…a09cc)
- `data/faults/mascsn26/mascsn26_faults_scc05_2026-11-15.xml` (sha256 adc99902…53c0)

Each holds 130 simple-fault sources: depth 0–12 km, Leonard2014_SCR scaling, incremental MFD from 6.0 in 0.1 bins.

**So slip rate and Mmax must be restored from those files (step 1).** Give these files and the report a row in `DATA.md`.

## Step 1: restore slip rate and Mmax per MASCSN fault

**From the SCC 1 file, for each source:**
- Read trace, dip, rake, upper and lower depth, the bins and their rates.
- Mmax is the last bin. Say whether `minMag` 6.0 is the first bin centre or edge, by checking the OpenQuake documentation or code (installed `openquake.hazardlib.mfd`, not the `oq-engine/` folder).
- b is the slope of log10 rate against magnitude.
- The moment rate is Σ rate × M0(bin), with the M0 convention of the installed OpenQuake (`openquake.hazardlib.scalerel` / `mfd`; probably 10^(1.5 M + 9.05)).

**Restored slip rate:**
- slip = moment rate / (μ L W), with μ = 30 GPa, L the geodesic trace length and W = (lower − upper depth) / sin(dip), the MASCSN geometry.
- **Closure test:** rebuild the MASCSN MFD from the restored slip, b, Mmax and the geometry, and recover the published rates within 1 %.
- The SCC 0.5 file must give rates × 0.5; check it.
- **Sensitivity:** state the effect of μ 30 against 32 GPa and of the M0 constant 9.05 against 9.1 (about 12 %). It does not change the moment rate, only the slip value.

**Check against the report:**
- Assign each fault to its system: by name, by the system of the matched CHAF strands, or by location against Figure 35, p. 76.
- Compare the restored slip with the Table 17 range of its system.
- List the faults outside the range. A factor that is the same for a whole system points to a convention we have wrong, for example a different width used for the moment balance. Report it rather than correcting it.

**Output:**
- `model/faults/tables/mascsn_restored_<date>.csv`, one row per source, with id, name, system, L, dip, rake, depths, Mmax, b, moment rate, restored slip and its Table 17 range
- a figure of restored slip by system against Table 17

## Step 2: database B

**Contents:**
- the MASCSN faults (restored slip, their Mmax kept as `mmax_mascsn`)
- the cleaned GEM faults of D16 that lie outside Chile: Argentina and Peru. Use the national border, or `AR-` / non-Chilean IDs where the border is not at hand.

**Fields:** the D16 schema (`FIELDS.md`), with every value's source given, and `chaf_ids` and `chaf_act` from CHAF where matched.

**Overlap:**
- Where a GEM segment lies within 5 km of a MASCSN trace over more than half its length, keep the MASCSN trace.
- For Magallanes–Fagnano: MASCSN traces in Chile, GEM AR-0056 traces in Argentina, joined at the border without overlap.
- The Fagnano slip rate follows DECISIONS (GPS, about 4–7 mm/yr) in both A and B. Report what MASCSN gives there.

**Output:** `data/faults/faults_B_<date>.gpkg` and `.csv`. Tests:
- every fault appears once
- no two traces overlap
- the fields are complete

## Step 3: A against B

**Two parametrisations of B:**
- *Our rules:* the same as A, for a fair comparison. That is the DECISIONS rules:
  - Leonard Mmax
  - ψ 0.6 / 0.8 / 1.0
  - depth 10 / 20 km
  - the six MFD shapes
  - b of the crustal class
  - Mmin 6.0
- *As published:* MASCSN depth 0–12 km, their Mmax and b, SCC 1 / 0.75 / 0.5, truncated GR. A check that we reproduce their fault model.

**Assigning faults to classes:** each fault goes to a crustal class (forearc, arc, backarc, Patagonia) by its midpoint and the class polygons of A7 (`data/intraarc.shp` and the Patagonia rule in `catalog/CLASSIFICATION.md`).

**Table.** Per class and domain-wide, N(≥ 6), N(≥ 6.5), N(≥ 7) and the moment rate for:
- A
- B with our rules
- B as published
- the catalogue fit of the class (`fits/tables/fits_2026-11-15.csv`, both shapes)

The ratio faults / fit at Mw ≥ 6 shows where a bulge will appear in B13.

**Faults in one and not the other:** a list with length, Mmax, slip and N(≥ 6), and a map of A against B, with insets for the north, Santiago–Valparaíso, Concepción–Arauco (Santa María, Morguilla) and Liquiñe–Ofqui.

**Near the cities:** for each of the 14 cities of DECISIONS, the summed fault N(≥ 6) within 50 km in A and in B, and the largest contributor.

## Outputs

- `model/faults/REPORT_D16b.md`: simple and explanatory. In this order:
  1. what was restored and how well (the closure test and Table 17)
  2. how A and B differ, and where
  3. proposed DECISIONS lines
- tables and figures in `model/faults/`, with rows in `FIGURES.md` for paper candidates

## At the end

Follow `CLAUDE.md`. Re-read `WORKLOG.md` just before appending, because other sessions may be writing. Tick D16b in `PLAN.md` when database B exists and the tests pass. B13 runs on both databases.
