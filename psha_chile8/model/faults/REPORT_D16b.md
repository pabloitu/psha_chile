# D16b: two fault databases, A (GEM) and B (MASCSN26 + GEM outside Chile)

15 Nov 2026 (second version, after the MASCSN method was identified).

**Where things are.** Code in `model/faults/`:
- `faultquake.py`: FaultQuake, ported
- `mascsn.py`: step 1
- `dbB.py`: step 2
- `rates.py` and `compare.py`: step 3
- `figs_b.py`: figures

Tests are in `tests/test_d16b.py`; all 50 tests of `model/faults/tests` pass.

The two databases:
- **A** is the final GEM file of D16, `data/faults/faults_gem_extra_2026-11-15.shp` (138 faults).
- **B** is `data/faults/faults_B_2026-11-15.gpkg` and `.csv` (166 faults).

**The rebuilt MASCSN fault model** is in `model/faults/nrml/mascsn26_rebuilt_scc{10,075,05}_2026-11-15.xml`.

Pages are the numbers printed in the MASCSN report.

## 1. How MASCSN built its fault sources, and the inputs restored

**The method is FaultQuake.** The report (§8.3, p. 127) cites FaultQuake (Tavakolizadeh et al. 2024) for Mmax only. Its source code (github.com/GeoSignalAnalysis/FaultQuake, `momentbudget` and `TruncatedGR`) also builds the rates, and the published files carry its fingerprints exactly:

- **Mmax** is the mode of the product of normal pdfs, rounded to 0.1. There are four pdfs:
  - MMO, from the strain drop
  - MAR, from the aspect-ratio length; used only when the fault is longer than that length
  - the WC94 length relation of the chosen kind
  - the WC94 area relation of the same kind
- **Moment rate:** M0(Mmax) / Tmean.
  - Tmean = M0(Mmax) / (μ V L_eff W), **rounded to whole years**
  - M0 = 10^(1.5 M + **9.1**), μ = 30 GPa
  - V = the mean of the minimum and maximum slip rate
  - W = T / sin(dip), with T the seismogenic thickness of their database
  - **L_eff = min(L, LAR)**, where LAR is the aspect-ratio length of Pace and Peruzza (2002), linear in W. For strike-slip WC94 it is −7.096 + 2.9807 W, which is 28.7 km at W = 12.
- **Rates:** a truncated GR on the points 6.0, 6.1, …, Mmax. In FaultQuake these are the **lower edges** of the bins, and the moment is balanced at those points. MASCSN wrote the first point as `minMag` 6.0, so OpenQuake reads every bin 0.05 lower than FaultQuake meant: Mmin is 6.0 and Mmax is the last point, but both as bin edges.

**Proof.** Two checks make this the method beyond doubt:
- For every one of the 130 sources, M0(Mmax) / moment rate is a whole number of years, to within 10⁻⁹ years.
- FaultQuake's `TruncatedGR`, given Mmax, b and that whole-number Tmean, rebuilds every published rate to 7 × 10⁻¹⁴.

The SCC 0.5 file is exactly the SCC 1 file halved. It is not a new FaultQuake run, which would have rounded Tmean / 0.5 again.

**Why my first version was wrong.** It assumed moment = μ × trace length × 12 km × slip. FaultQuake caps the length at LAR, and its thickness T is not the 12 km written in the NRML. This is why the moment of the long Liquiñe–Ofqui and Magallanes traces did not grow with length.

**Inputs restored** (`mascsn.invert`, `tables/mascsn_restored_2026-11-15.csv`). For each source we searched:
- the WC94 kind (that of the rake first, then strike-slip, all, reverse, normal)
- thickness T from 5 to 40 km in steps of 0.5
- slip V with one or two decimals

The search kept the inputs that give the published Mmax and Tmean. Faults longer than LAR ("capped", 88 of 130) fix V and T together, because their moment does not depend on length. Below the cap only V × T is fixed, and our trace length differs a little from their database length. There T is the most common T of the capped faults of the same system, and Tmean is matched within 2 %.

| result | sources |
|---|---|
| exact, capped (V and T fixed, Tmean exact) | 82 |
| exact, below the cap (Tmean exact) | 7 |
| system T (V × T fixed; T of the system; Tmean within 2 %) | 35 |
| tolerant (no exact solution; Salar de Atacama 0.01 mm/yr, Aroma, Caleta Herradura) | 6 |

**Forward check.** FaultQuake run on the restored inputs gives:
- the published Mmax for **130 of 130** sources
- the published Tmean exactly for 101
- every published rate within 2 %

This is the rebuilt model in `nrml/`. Tmean and Mmax come from the forward run, the geometry and rake from the published file, and `minMag` is 6.0 as MASCSN wrote it. It is written for SCC 1, 0.75 and 0.5. The MASCSN repository has no SCC 0.75 file, although that branch has weight 0.5 (Figure 74).

**FaultQuake inputs per system**, against Table 17 (p. 77; `tables/mascsn_systems_2026-11-15.csv`, `figs/mascsn_slip_systems.png`):

| system | sources | T (km) | V (mm/yr), number of sources | Table 17 | inside / below / above |
|---|---|---|---|---|---|
| Liquiñe-Ofqui | 65 | 12 (58 sources), 9.5–13 | 7.0 (29), 2.0 (26), 4.0, 5.5, 8.3, 10.6 (2), 2.3–2.9 (5) | 4–12 | 34 / 31 / 0 |
| Magallanes | 7 | 15 | 6.5 (5 main traces), 1.0 (Bahía Indio, Río San Juan) | 6–7 | 5 / 2 / 0 |
| Atacama | 11 | 23 (one 19) | 0.4–0.6 (9), 0.07 (Mititus), 0.03 (Caleta Herradura) | 0.06–0.07 | 1 / 1 / 9 |
| Transversales Este-Oeste | 12 | 30 (from the one capped fault) | 0.29 (10), 0.33, 0.4 | 0.4 | 1 / 11 / 0 |
| Transversales Noroeste | 7 | 20 | 0.4 (4; Carranza, Topocalma, Marga-Marga, Pelluhue), Pichilemu 0.52, Laguna Verde 0.16, El Yolki 5.6 | 0.5 | 0 / 5 / 2 |
| San Ramón | 2 | 15 | 0.6 (San Ramón, Cariño Botado) | 0.5 | 0 / 0 / 2 |
| no Table 17 system | 26 | 6.5–27 | Santa María 2.8–4.3 (T 12.5–19), Lanalhue 3.0 and Morguilla 1.2 (T 27), Cachet 2.0 (T 10), Exploradores 1.2 (T 8), Puerto Aldea 0.3, Salar de Atacama 0.01 | — | — |

What it says:
- **Liquiñe–Ofqui and Magallanes follow Table 17.**
  - The master Liquiñe–Ofqui faults (Río Cuervo, Los Palos, Maqueo, Maihue, Caburgua, Neltume, Puyuhuapi and others) take 7.0 mm/yr. The secondary and transverse faults take 2.0.
  - Every Magallanes main trace takes 6.5, the midpoint of 6–7. Magallanes T is 15 km.
- **Atacama:** the values are about 0.5 mm/yr, not Table 17's 0.06–0.07. MASCSN gave these faults their own values.
- **E–W faults:** only V × T ≈ 8.7 km·mm/yr is fixed. Table 17's 0.4 would need T = 22 km; the one capped E–W fault gives 30 km and 0.29 (T 25 would give 0.35).
- **Kinematics:** the WC94 kind is mostly that of the rake, but the 45° and −135° GEM "Falla …" faults take the strike-slip or reverse kind.

**What is left over.** Only V × T is fixed for the 35 "system T" faults below the cap, and 6 faults have no exact solution. The method, Mmax and the moment rate of every source are exact. The slip of a fault below the cap is as good as the choice of T.

## 2. Database B and how A and B differ

**Database B** (`dbB.py`; fields as in `FIELDS.md`): 166 faults.
- **129 MASCSN26 faults (5 823 km):**
  - slip = the restored FaultQuake V, with its T, scaling relation, Tmean and how it was found (`t_fq`, `scr_fq`, `tmean_fq`, `fq_how`)
  - Mmax, b and moment rate as `mmax_mascsn`, `b_mascsn`, `mo_mascsn` (FaultQuake M0 at its points)
  - geometry and depths 0–12 km from the NRML
- **37 GEM faults of A in Argentina and Peru (1 205 km):** none dropped by the 5 km overlap rule.
- **Magallanes–Fagnano:**
  - MASCSN west of the border, AR-0056 east of it. Knokeke dropped; Deseado and 722 cut.
  - The main trace (MASCSN 726, 721 and 720 + AR-0056a, b, d and g; 494 km) takes the GPS rate of DECISIONS, 5.9 mm/yr. MASCSN gives 6.5 there, close to the GPS rate, as it should be.
  - **To decide:** MASCSN gives the parallel trace 722 (162 km in Chile) 6.5 mm/yr as well, and Bahía Indio and Río San Juan 1.0. Kept as MASCSN has them, they count the zone's GPS motion again: 722 alone adds 0.036 events of M ≥ 6 per year. DECISIONS removed such strands in A.

**Per crustal class** (`tables/d16b_class_table_2026-11-15.csv`; catalogue fits from `fits/tables/fits_2026-11-15b.csv`, the current table; with `fits_2026-11-15.csv` of the brief every ratio is the same to two decimals, since only the tapered corners moved, by less than 0.01):
- "Our rules" are as in DECISIONS: ψ 0.6 / 0.8 / 1.0, depth 10 / 20 km (0.5 / 0.5), Leonard Mmax, six shapes, class b, Mmin 6.0 (`rates.py`). They apply the slip of each database to the **whole trace length**.
- "MASCSN moment, our MFD rules" (added at Pablo's request) uses our Mmax, shapes, b and ψ, but the moment of each MASCSN fault is MASCSN's own FaultQuake budget: μ × slip × min(L, LAR) × T / sin dip, with their T and length cap, on the trace as kept in B, times ψ (ψ takes the place of their SCC). For the Magallanes main trace the slip is the GPS 5.9 mm/yr. GEM rows use our rules (`compare.budget`, `rates.source(fixed=...)`).
- "As published" are MASCSN's own rates × the mean SCC 0.75.
- N per year; moment in 10¹⁷ N m/yr for M ≥ 6; "/ fit" is fault N(≥ 6) over the tapered catalogue fit.

| class | model | N(≥ 6) | N(≥ 6.5) | N(≥ 7) | moment | / fit |
|---|---|---|---|---|---|---|
| forearc | A | 0.060 | 0.011 | 0.0011 | 2.9 | 0.17 |
| | B, our rules | 0.157 | 0.022 | 0.0027 | 6.3 | 0.43 |
| | B, MASCSN moment, our MFD rules | 0.183 | 0.022 | 0.0024 | 6.4 | 0.50 |
| | B, as published | 0.163 | 0.015 | 0.0018 | 5.4 | 0.45 |
| | fit, tapered / cut | 0.364 / 0.355 | 0.111 / 0.105 | 0.025 / 0.025 | 33.5 / 30.8 | |
| arc | A | 0.431 | 0.077 | 0.0080 | 19.1 | **3.3** |
| | B, our rules | 1.149 | 0.248 | 0.024 | 56.6 | **8.8** |
| | B, MASCSN moment, our MFD rules | 0.597 | 0.106 | 0.0062 | 23.8 | **4.6** |
| | B, as published | 0.543 | 0.097 | 0.0028 | 20.2 | **4.2** |
| | fit, tapered / cut | 0.130 / 0.128 | 0.041 / 0.039 | 0.012 / 0.011 | 22.3 / 20.7 | |
| backarc | A = B (GEM Argentine rows only) | 0.049 | 0.012 | 0.0017 | 3.2 | 0.21 |
| | fit, tapered / cut | 0.235 / 0.233 | 0.074 / 0.072 | 0.021 / 0.020 | 32.1 / 30.0 | |
| Patagonia | A | 0.088 | 0.025 | 0.0061 | 12.7 | **1.3** |
| | B, our rules | 0.238 | 0.060 | 0.011 | 22.1 | **3.6** |
| | B, MASCSN moment, our MFD rules | 0.096 | 0.022 | 0.0039 | 8.7 | 1.4 |
| | B, as published | 0.122 | 0.028 | 0.0043 | 7.4 | **1.8** |
| | fit, tapered / cut | 0.067 / 0.066 | 0.021 / 0.021 | 0.0066 / 0.0063 | 13.6 / 12.6 | |
| all crustal | A | 0.628 | 0.125 | 0.017 | 37.8 | 0.79 |
| | B, our rules | 1.594 | 0.342 | 0.040 | 88.1 | **2.0** |
| | B, MASCSN moment, our MFD rules | 0.924 | 0.161 | 0.014 | 42.1 | 1.16 |
| | B, as published | 0.877 | 0.152 | 0.011 | 36.2 | 1.10 |
| | MASCSN file, all 130 sources, as published | 0.761 | 0.127 | 0.0068 | 29.3 | 0.96 |
| | fit, tapered / cut | 0.796 / 0.782 | 0.246 / 0.237 | 0.065 / 0.062 | 101.5 / 94.0 | |

What this means:
- **B with our rules has 2.4 times the moment of B as published** (88 against 36). The difference is mostly the MASCSN length cap.
  - MASCSN puts the moment of a 28.7 km piece on a Liquiñe–Ofqui fault of 85 km. Our rules put 7 mm/yr on the whole 85 km.
  - The depths add to it: our 10–20 km against their T of 12 km on Liquiñe–Ofqui.
  - So B with our rules is not "MASCSN with our rules" in moment. It is MASCSN's slip rates on MASCSN's traces with our rules.
- **The MASCSN-moment variant is close to MASCSN as published:**
  - domain-wide 1.16 against 1.10 times the fit, and moment 42 against 36
  - The rest is ψ̄ 0.8 against SCC 0.75, and our Mmax and shapes.
  - So the doubling under plain our rules comes from the moment budget (the length cap and the thickness), not from the MFD rules.
  - With MASCSN's moment, B is 1.5 times A in N(≥ 6) domain-wide. The arc is 4.6 times its fit (A 3.3).
- **The arc bulge grows from 3.3 (A) to 8.8 (B with our rules).** It comes from the Liquiñe–Ofqui master faults at 7 mm/yr, against GEM's 3.0 or 0.5. As published, MASCSN gives 4.2 times the arc fit.
- **Patagonia:** 3.6 times the fit in B, from the 722 strand at 6.5 mm/yr and the side traces.

**Faults in one database and not the other** (less than half of the trace within 5 km of the other database; `tables/d16b_only_2026-11-15.csv`, `figs/faults_A_B_map.png`):
- **Only in A:** 10 faults, 398 km, N(≥ 6) 0.029. These are Wager, Quintay and Valparaíso, the arc transverse faults, and the side traces of Quitralco and Puyuhuapi.
- **Only in B:** 37 faults, 1 278 km, N(≥ 6) 0.256:
  - Magallanes strand 722 (6.5 mm/yr, 0.036)
  - three unnamed Liquiñe–Ofqui branches at 42.8–43.8° S (7.0 mm/yr, 0.020–0.027 each)
  - El Yolki (5.6 mm/yr, 0.015) and El Saltón (4.6)
  - the five Santa María faults (2.8–4.3 mm/yr)
  - Morguilla, Cachet, Pelluhue, Cariño Botado, and E–W faults in the north
- By class, B adds 0.066 in the forearc, 0.104 in the arc and 0.086 in Patagonia.

**Near the cities** (summed fault N(≥ 6) of the sources within 50 km; our rules unless named; `tables/d16b_cities_2026-11-15.csv`):

| city | A | B, our rules | B, MASCSN moment | B as published | largest in B (our rules) |
|---|---|---|---|---|---|
| Iquique | 0.0026 | 0.0027 | 0.0059 | 0.0039 | Tarapacá, 14 km |
| Antofagasta | 0.0104 | 0.0094 | 0.0089 | 0.0060 | Paposo, 10 km |
| La Serena | 0 | 0.0012 | 0.0008 | 0.0007 | Puerto Aldea, 50 km |
| Valparaíso | 0.0076 | 0.0019 | 0.0026 | 0.0025 | Marga-Marga, 7 km |
| Santiago (both points) | 0.0014 | 0.0022 | 0.0021 | 0.0022 | San Ramón |
| Concepción | 0.0012 | 0.0569 | 0.0609 | 0.0557 | Santa María, 38 km |
| Pucón | 0.090 | 0.202 | 0.110 | 0.099 | Reigolil–Pirehueico, 38 km |
| Puerto Montt | 0.0049 | 0.031 | 0.018 | 0.017 | unnamed Liquiñe–Ofqui, 38 km |
| Hornopirén | 0.034 | 0.152 | 0.066 | 0.062 | unnamed Liquiñe–Ofqui, 4 km |
| Puerto Aysén | 0.052 | 0.132 | 0.052 | 0.048 | Los Palos, 0 km |
| Puerto Williams | 0.0505 | 0.0510 | 0.0266 | 0.059 | Magallanes–Fagnano system |
| Calama, Copiapó | 0 | 0 | 0 | 0 | — |

Puerto Williams falls to 0.027 with the MASCSN moment. The budget caps each Magallanes trace at its aspect-ratio length (37.6 km at T 15 km), so the 494 km system carries the moment of about 4 × 38 km of trace at the GPS rate. As published it is 0.059, because there MASCSN's 6.5 mm/yr also sits on 722 and the Argentine traces.

## 3. Proposed DECISIONS lines (Pablo decides)

- *Crustal and faults:* "MASCSN26 fault sources were built with FaultQuake (Tavakolizadeh et al. 2024). Tmean = M0(Mmax) / (μ V min(L, LAR) T / sin dip), rounded to whole years, with M0 constant 9.1, and a truncated GR on 6.0..Mmax balanced at the bin lower edges, written as `minMag` 6.0, so OpenQuake reads them 0.05 low. Inputs restored per fault (`model/faults/tables/mascsn_restored_2026-11-15.csv`). The rebuild reproduces all Mmax and every rate within 2 % (D16b)."
- *Crustal and faults:* "Fault database B (D16b): `data/faults/faults_B_2026-11-15.gpkg`, 166 faults. 129 MASCSN26 faults in Chile with their restored FaultQuake slip rates, plus the 37 GEM faults of A in Argentina and Peru. B13 runs A and B with our rules."
- *Magallanes–Fagnano:* "In B the main trace is MASCSN 726, 721 and 720 plus AR-0056a, b, d, g (494 km), at the GPS rate 5.9 mm/yr (MASCSN 6.5). The MASCSN parallel trace 722 and the splays Bahía Indio and Río San Juan stay as MASCSN has them (6.5 and 1.0 mm/yr) (Pablo, 15 Nov)."
- *Crustal and faults:* "MASCSN's own fault logic tree has one branch level only: SCC 1.0 / 0.75 / 0.5 with weights 0.25 / 0.5 / 0.25 (Figure 74, p. 129); fixed 0–12 km geometry, one Mmax (FaultQuake), one truncated GR, b of the MASCSN crustal zone. In the B variant on the MASCSN moment, our ψ 0.6 / 0.8 / 1.0 (0.25 / 0.5 / 0.25) takes the place of SCC (same weights, mean 0.8 against 0.75)."
- *Crustal and faults:* "Fault depth weights 10 / 20 km: 0.5 / 0.5" (used here).
- *Crustal and faults:* "Database B is run in B13 in two variants: our rules (MASCSN slip rates on the whole trace) and our MFD rules on the MASCSN moment budget (their thickness and aspect-ratio length cap, times ψ) (Pablo, 15 Nov)."

Open questions:
1. **Which B goes to B13** (Pablo chose to add the MASCSN-moment variant, 15 Nov):
   - B13 runs A, B with our rules, and B with the MASCSN moment and our MFD rules (`compare.sources(..., mm=True)`).
   - Open: whether the length cap of FaultQuake is a rule we want to adopt or only MASCSN's choice. It also halves Puerto Williams.
2. **Magallanes strand 722 and the splays in B:** kept as in MASCSN (Pablo, 15 Nov).
3. **The arc bulge:** 3.3 (A), 8.8 (B, our rules), 4.2 (B as published). The Liquiñe–Ofqui master faults at 7 mm/yr, against GEM's 3.0 or 0.5, are the cause in B.
4. **Faults below the cap in B** carry a slip that depends on the chosen T. The E–W faults are 0.29 mm/yr at T 30 km, or 0.4 at 22 km (Table 17).
5. **Half-bin shift in the published model.** FaultQuake's points are bin lower edges, and MASCSN wrote them as `minMag` 6.0, so OpenQuake runs every MASCSN fault 0.05 low in magnitude (the same pitfall as in LEARNINGS). The rebuilt files keep it, to reproduce MASCSN. A corrected version would use `minMag` 6.05.
