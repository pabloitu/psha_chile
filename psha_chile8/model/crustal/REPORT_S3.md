# S3 and S4: the crustal source model (background and faults)

15 Nov 2026. Brief `tasks/S3_crustal.md` (replaces B13). Code in `model/crustal/`:
- `smooth.py`: kernel and calibration score
- `background.py`: step 2
- `faults.py`: step 1
- `join.py`: step 3
- `large.py`: step 4
- `build.py` and `nrml.py`: step 5
- `oqcheck.py`: step 6

Tables are in `tables/`, figures in `figs/`, OpenQuake files in `nrml/`. Tests: `tests/test_crustal.py`, 11 pass.

Inputs:
- frozen catalogue `2026-11-14c`
- declustered flags `gk_family` and `nn_family` (2026-11-15)
- fits `fits_2026-11-15b.csv`
- fault databases A (`faults_gem_extra_2026-11-15.shp`) and B (`faults_B_2026-11-15.gpkg`)
- the psha_chile7 crustal grid, copied as `data/crustal_grid_01_2026-11-15.csv` (19 686 cells of 0.1°)

How the model is built, in short:
- **Background.** Each crustal class (forearc, arc, backarc, Patagonia) has its catalogue fit (rate and b, from the full catalogue) and a map. The map is a smoothed density of the declustered events of that class. Every grid cell gets the class rate times its share of the map.
- **Faults.** Each fault gets a moment rate from its slip rate, ψ μ L W slip. That moment is spread over magnitudes 6.0 to Mmax by one of six MFD shapes.
- **The join.** Per class and per 0.1 magnitude bin from 6.0 up, the background is the fit minus the faults of the class, never below zero. Below 6.0 the background is the fit.

## 1. The join and the bulge

Rates are events per year at and above the magnitude. These columns are for the tapered fit; the cut fit gives the same to 2 % at Mw 6 (`tables/join_2026-11-15.csv`, both shapes):
- **fit**: the catalogue fit
- **observed**: the weighted count inside the completeness table, per year (class weight times the magnitude-error count, as the fit)
- **faults**: the weighted mean over the 36 branches of the fault tree; lo and hi are the lowest and highest branch
- **background**: after the join. Rule (Pablo, 15 Nov): below 6.0 the fit; from 6.0 the fit minus the faults, and zero from the first bin where the faults reach the fit (the background does not come back above the faults)
- **total / fit**: faults plus background, over the fit
- **bulge**: the bins where the faults alone exceed the fit, and the excess N(≥ 6)

Model names: **A**, GEM (D16); **B**, MASCSN26 with our rules; **B-mm**, B on the MASCSN moment with our MFD rules.

**Mw ≥ 6.0**

| class | model | fit | observed | faults (lo–hi) | background | total / fit | bulge: bins, excess |
|---|---|---|---|---|---|---|---|
| forearc | A | 0.365 | 0.391 | 0.060 (0.024–0.126) | 0.304 | 1.00 | 7.9–8.2, < 10⁻⁴ |
| | B | | | 0.157 (0.082–0.312) | 0.207 | 1.00 | 8.0, < 10⁻⁴ |
| | B-mm | | | 0.183 (0.075–0.350) | 0.182 | 1.00 | 8.0, < 10⁻⁴ |
| arc | A | 0.130 | 0.131 | 0.431 (0.181–0.896) | 0 | **3.32** | 6.0–7.1, 0.307 |
| | B | | | 1.149 (0.368–2.476) | 0 | **8.84** | 6.0–7.2, 1.023 |
| | B-mm | | | 0.596 (0.151–1.238) | 0 | **4.59** | 6.0–7.0, 0.473 |
| backarc | A = B = B-mm | 0.235 | 0.270 | 0.049 (0.014–0.111) | 0.186 | 1.00 | none |
| Patagonia | A | 0.067 | 0.067 | 0.087 (0.017–0.214) | 0 | **1.31** | 6.0–8.5, 0.022 |
| | B | | | 0.238 (0.062–0.550) | 0 | **3.57** | 6.0–8.5, 0.172 |
| | B-mm | | | 0.096 (0.019–0.212) | 0 | **1.44** | 6.0–8.5, 0.032 |
| all crustal | A | 0.797 | 0.859 | 0.628 (0.235–1.347) | 0.490 | **1.40** | 0.328 |
| | B | | | 1.594 (0.529–3.448) | 0.393 | **2.49** | 1.194 |
| | B-mm | | | 0.924 (0.258–1.875) | 0.368 | **1.62** | 0.505 |

**Mw ≥ 6.5 and 7.0**, total / fit:

| class | A, Mw ≥ 6.5 | B, Mw ≥ 6.5 | B-mm, Mw ≥ 6.5 | A, Mw ≥ 7 | B, Mw ≥ 7 | B-mm, Mw ≥ 7 |
|---|---|---|---|---|---|---|
| arc | 1.90 | 6.11 | 2.60 | **0.66** | 1.99 | **0.51** |
| Patagonia | 1.19 | 2.81 | 1.03 | 0.93 | 1.70 | **0.59** |
| all crustal | 1.16 | 2.00 | 1.27 | 0.93 | 1.26 | 0.87 |

Forearc and backarc stay at 1.00 at every magnitude (the forearc background stops at 7.9, where faults with Mmax 7.5–7.7 reach the far tail of the fit; the loss is below 10⁻⁴ per year). The fit and observed rates at Mw ≥ 6.5 and 7 are in the table file.

What it says:
- **Forearc and backarc.** The faults stay below the fit. The background takes the rest, and the total is the fit by construction. The faults carry 17 % (A) to 50 % (B-mm) of the forearc N(≥ 6), and 21 % of the backarc.
- **Arc: the bulge.** The arc faults (Liquiñe–Ofqui) alone give 3.4 (A), 8.9 (B) or 4.6 (B-mm) times the arc fit at Mw ≥ 6. The background above 6.0 is zero from 6.0 to about 7.1, and the faults alone set the rate there. The arc fit agrees with the observed count (0.130 against 0.131 per year), so the excess is not a weak fit. It is the slip rates: A carries GEM's 3.0 mm/yr on the master faults, B MASCSN's 7.0 mm/yr. This is D16b's result, now inside the model.
- **Above the arc faults nothing is left.** The arc faults are short, with Leonard Mmax 6.0–7.4 (6.3–7.4 at 20 km). The background stops at 6.0 and does not come back, so the arc has no source above about 7.4. At Mw ≥ 7 the model is 0.66 (A) and 0.51 (B-mm) of the fit: Aysén 1960 (7.7), 1927 (7.1) and the other old arc events of Mw ≥ 7 have no source of their size. Before the rule change (15 Nov) the fit's tail above 7.1 stayed in the background and carried them.
- **Patagonia.** The Magallanes–Fagnano system alone reaches the fit (Mmax 8.0). With B's parallel strand 722 at 6.5 mm/yr it is 3.6 times the fit. The background above 6.0 is zero; at Mw ≥ 7 the model is 0.93 (A) and 0.59 (B-mm) of the fit.
- **The forearc bins 7.9–8.2** are a formal bulge of less than 10⁻⁴ per year. Faults with Leonard Mmax 7.5–7.7 (Atacama, Paposo) and the tapered shape's 0.5 tail pass the tapered fit's tail, which ends near 8.2. With the rule the forearc background stops there; nothing to act on.
- **Domain-wide** the model has 1.40 (A), 2.49 (B) and 1.62 (B-mm) times the catalogue rate of Mw ≥ 6, and 0.93, 1.26 and 0.87 times at Mw ≥ 7. All of the excess comes from the arc and Patagonia.
- **The spread of the fault tree is large:** a factor of 5–7 between the lowest and highest branch at Mw ≥ 6. The lowest branch (ψ 0.6, 10 km, AL-I) leaves the arc bulge in place in A (0.18 against 0.13).

**The jump at Mw 6.0** (`tables/jump_2026-11-15.csv`): background in bin 5.9 against background plus faults in bin 6.0. The fit itself steps by 0.80 from bin to bin.

| class | A | B | B-mm |
|---|---|---|---|
| forearc, backarc | 0.80 (continuous) | 0.80 | 0.80 |
| arc | **3.8** | **8.6** | **4.9** |
| Patagonia | 1.11 | **3.2** | 1.35 |
| all crustal | 1.32 | 2.29 | 1.52 |

Where there is a bulge the incremental MFD jumps up at 6.0. This is the bulge seen bin by bin: the faults put more events in the bin 6.0 than the background has in 5.9.

**The fault-tree class-maximum sensitivity** (`tables/fault_classes_2026-11-15.csv`): Mmax = the background Mmax of the class instead of Leonard. It lowers fault N(≥ 6) by a factor of 3–4: domain-wide from 0.63 to 0.19 (A), 1.59 to 0.45 (B) and 0.92 to 0.23 (B-mm). In the arc it goes from 0.43 to 0.094 (A), below the fit. The moment is the same, but a larger Mmax puts it into fewer, larger events. With the class maximum the arc bulge would disappear in A and B-mm, and fall to 2.2 times the fit in B. This is the single largest lever on the bulge. It is a sensitivity only (DECISIONS); its files are written (`_cm`, section 6).

Figures:
- `figs/mfd_A_2026-11-15.png`, `mfd_B_…`, `mfd_Bmm_…`: per class, cumulative. The fit band is the bootstrap 5–95 % of N(≥ 5, 6, 7), interpolated. Observed points per completeness period; the faults as mean and range of the tree; the background; the total.
- `figs/fault_share_2026-11-15.png`: the fault share of N(≥ 6) in 0.5° cells, the three databases.
- `figs/arc_join_leonard_2026-11-15.png` and `arc_join_classmax_2026-11-15.png`: the arc, rates per bin of the fit, faults, background and total, with the observed rates; Leonard Mmax and class maximum.

## 1b. The arc bulge: fault count test (after Pablo's questions)

`arc.py`, `tables/arc_test_2026-11-15.csv`, `tables/arc_branches_2026-11-15.csv`, `figs/arc_test_2026-11-15.png`.

**The test.** For each branch of the fault tree:
- **expected:** the number of arc events of Mw ≥ 6 the model expects inside the completeness table, i.e. (faults + background after the join) × the observation time of each bin. Mw 6.0–6.9 is complete from 1964, Mw ≥ 7 from 1905.
- **observed:** 9.5 events, by weight. The arc fit expects 9.1, so the fit itself agrees with the record.
- **pass:** a branch passes if observing as few as 9.5 events has Poisson probability ≥ 0.05.
- **ψ needed:** the mean ψ that would make the faults plus background match the observed count.

| fault model | expected, Mw ≥ 6 (lowest–highest branch) | of which faults | tree weight that passes | ψ needed | Mw ≥ 7: expected / observed |
|---|---|---|---|---|---|
| A, Leonard Mmax | 27.6 (12–57) | 27.6 | 8 % | 0.27 | 1.0 / 2.2 |
| B, our rules | 73.7 (26–157) | 73.7 | 0 % | 0.10 | 2.9 / 2.2 |
| B-mm | 37.9 (10–78) | 37.9 | 6 % | 0.20 | 0.8 / 2.2 |
| A, class-maximum Mmax | 9.1 (3–21) | 6.6 | **94 %** | 0.84 | 1.7 / 2.2 |
| B, class-maximum Mmax | 19.7 (2–56) | 19.7 | 46 % | 0.38 | 3.8 / 2.2 |
| B-mm, class-maximum Mmax | 9.2 (2–19) | 8.3 | **96 %** | 0.82 | 1.8 / 2.2 |

What it says:
- **With the Leonard Mmax the arc fault model fails the catalogue at Mw 6–7.** The tree expects 3 (A), 8 (B) or 4 (B-mm) times the observed count (numbers after the join-rule change of 15 Nov), and almost no branch passes. The only passing branches in A are ψ 0.6 with AL-I or Youngs–Coppersmith, the shapes that put the moment into the largest events.
- **At Mw ≥ 7** the class-maximum variants agree with the record (1.7–3.8 expected against 2.2 observed). With the Leonard Mmax A and B-mm now expect only 0.8–1.0: the background stops at 6.0, so the arc events above the faults' Mmax have no source. The test checks too many events, so they still pass. The excess is at Mw 6–7, i.e. how each fault's moment is shared among magnitudes.
- **The cause is the Leonard Mmax of short faults.** The arc faults are 10–120 km long (median 32–37 km), so Leonard gives them Mmax 6.0–7.4, and their whole slip-rate moment has to come out as Mw 6–7 events. With the class maximum (7.9) the same moment goes into fewer, larger events. A and B-mm then match the record (94–96 % of the tree passes, ψ needed about 0.8, the middle of the tree). B with our rules still expects twice the record: MASCSN's 7 mm/yr on whole traces is too much moment for the arc.
- **Lowering ψ alone would need ψ 0.10–0.25,** far below the range of DECISIONS (0.6–1.0). It is not a credible fix.
- psha_chile7 saw the same thing: "φ = 1 over-predicts observed M ≥ 6 in the buffers (LOFZ region dominant)" (LEARNINGS).

**By depth branch** (share of the weight that passes, 10 / 20 km): A 8 / 4 %, B 0 / 0 %, B-mm 0 / 13 %; class maximum: A 100 / 87 %, B 75 / 17 %, B-mm 96 / 96 %.
- With our rules a deeper fault has more moment (wider), so 20 km expects more events: A 31.6 against 25.4.
- In B-mm the MASCSN moment is fixed and the depth only sets Mmax, so 20 km expects fewer (30.8 against 46.9).

**Forearc.** The forearc faults stay under the fit with either Mmax, so the join makes the total equal to the fit: 24.5 expected against 26.9 observed, and every variant passes.
- Leonard Mmax of the forearc faults is 6.3–7.7 (median 6.8–6.9). One fault per database is above the class maximum 7.4: the Atacama segment Salar del Carmen in A (7.7), Paposo in B (7.5), at 20 km.
- With the class maximum (7.4) the forearc fault rate of Mw ≥ 6 halves (A 0.060 → 0.027, B 0.157 → 0.059), and the background takes the difference.
- The sensitivity sets every fault to the class maximum, so for those two faults it lowers Mmax rather than raising it.

**With the class maximum the join changes** (Mw ≥ 6, tapered fit; `join` rows `<db>_cm`):
- **Arc bulge:** gone in A (faults 0.094, 72 % of the fit; background 0.036) and B-mm (0.118, 91 %). B keeps 2.2 times the fit.
- **Patagonia bulge:** gone in A and B-mm, 1.4 times in B.
- **Whole crust:** total / fit 1.00 (A, B-mm) and 1.22 (B).
- **Near the cities:** the fault rate within 50 km falls 4–7 times at Pucón, Hornopirén and Puerto Aysén (A: 0.050 → 0.008, 0.029 → 0.008, 0.049 → 0.012). The faults still hold 85–89 % of N(≥ 6) there, and the total stays 2–7 times the no-faults background.
- **The catch:** a short fault now carries events up to Mw 7.9 that its own area cannot hold. These are in effect multi-fault ruptures of the Liquiñe–Ofqui system, which the model does not have explicitly (DECISIONS: no multi-fault ruptures).

**Against the class maximum (Pablo):** it passes the test for the wrong reason. A Mw 7.9 on a 35 km × 20 km fault needs about 38 m of average slip; Leonard puts a Mw 7.9 strike-slip rupture at about 8 000 km² (400 km at 20 km depth). The class maximum is Aysén 1960 + 0.2, an event already in the background fit, copied onto segments that cannot host it. It stays a sensitivity only. MASCSN does not join traces either: 130 independent simple-fault sources, Liquiñe–Ofqui Mmax 6.1–7.1.

**Options for the arc (Pablo decides):**
1. **Keep the Leonard Mmax and accept the bulge.** The arc then has 3–8 times more Mw 6–7 crustal events than observed since 1964. It is the most conservative choice and is rejected by this test.
2. **Class maximum for the arc faults.** It passes the test for A and B-mm, and keeps the moment and slip rates. It stands in for Liquiñe–Ofqui rupturing as a system, with Aysén 1960 (Mw 7.7) as the example.
3. **Leonard on the system area** (all master Liquiñe–Ofqui segments joined, as done for Magallanes–Fagnano). It is the same idea as option 2, but with a geometric Mmax: 8.0–8.3 for a 1 000 km system at 10–20 km depth. It needs a decision on which segments form the system.

The sensitivity files with the class maximum for every class are written (section 6), so the tornado can measure option 2 directly.

## 2. What A and B change, by class and near the cities

**By class** (table above):
- B raises the forearc faults from 0.06 to 0.16–0.18 per year. The cause is the faults only in B: Santa María, El Yolki, Morguilla, Cachet, Pelluhue and the E–W faults of the north (D16b).
- B raises the arc from 0.43 to 1.15 (our rules) or 0.60 (B-mm), and Patagonia from 0.09 to 0.24 or 0.10.
- The backarc is the same in all three: GEM rows in Argentina.

**Near the cities.** These are N(≥ 6) per year within 50 km (`tables/cities_2026-11-15.csv`):
- **Faults:** each fault source counts with the share of its trace that lies within 50 km. This is not the whole source as in D16b, so a long system counts only for its nearby part.
- **Background:** the cells within 50 km, tapered fit, the mean of the two declustering options.
- **No faults:** the background with the full fit.

| city | A: faults / background (share) | B: faults / background (share) | B-mm: faults / background (share) | no faults |
|---|---|---|---|---|
| Iquique | 0.0025 / 0.0059 (30 %) | 0.0027 / 0.0040 (40 %) | 0.0059 / 0.0036 (62 %) | 0.0074 |
| Antofagasta | 0.0053 / 0.0069 (44 %) | 0.0049 / 0.0047 (51 %) | 0.0046 / 0.0041 (53 %) | 0.0084 |
| Calama, Copiapó, La Serena | 0 / 0.001–0.004 | 0 | 0 | 0.001–0.005 |
| Valparaíso | 0.0075 / 0.0025 (75 %) | 0.0019 / 0.0018 (51 %) | 0.0026 / 0.0017 (61 %) | 0.0035 |
| Santiago (both points) | 0.0013 / 0.0021 (39 %) | 0.0022 / 0.0018 (55 %) | 0.0021 / 0.0017 (54 %) | 0.0050–0.0057 |
| Concepción | 0.0012 / 0.0040 (22 %) | 0.050 / 0.0027 (95 %) | 0.052 / 0.0024 (96 %) | 0.0051 |
| Pucón | 0.050 / 0.0010 (98 %) | 0.116 / 0.0007 (99 %) | 0.075 / 0.0006 (99 %) | 0.0020 |
| Puerto Montt | 0.0037 / 0.0007 (83 %) | 0.025 / 0.0005 (98 %) | 0.015 / 0.0005 (97 %) | 0.0019 |
| Hornopirén | 0.029 / 0.0005 (98 %) | 0.098 / 0.0004 (100 %) | 0.047 / 0.0004 (99 %) | 0.0022 |
| Puerto Aysén | 0.049 / 0.0003 (99 %) | 0.122 / 0.0002 (100 %) | 0.048 / 0.0003 (99 %) | 0.0054 |
| Puerto Williams | 0.0043 / 0.0000 (100 %) | 0.0047 / 0.0000 (100 %) | 0.0024 / 0.0000 (99 %) | 0.0007 |

What it says:
- **North and centre (Iquique to Santiago):** the faults hold 30–75 % of N(≥ 6) within 50 km. The total stays close to the no-faults background (within a factor of 0.7–2.9).
- **Concepción:** B adds the Santa María faults, and N(≥ 6) within 50 km goes up ten times (0.005 → 0.053).
- **The southern cities (Pucón to Puerto Aysén):** nearly everything is fault, and the total is 2–60 times the no-faults background. The no-faults branch is not a small change there; it is a different model.
- **Puerto Williams:** with the system's 490 km counted only where it is within 50 km, the city sees 0.004–0.005 per year (A, B), 0.002 (B-mm). That is 6–7 times the no-faults background. The background at Mw ≥ 6 is zero there (Patagonia bulge).

## 3. The checks

**The kernel.** The two codes give the same field. Both use K = 1 / (r² + d²)^1.5, with d the distance to the n-th neighbour, at least 5 km, cut at 500 km, and each event normalised over the cells it reaches.
- `psha_chile7/lib/smooth.py` (`kernel`, `field`) and `smoothed_seismicity/ssm/smoothing.py` (`adaptive_radii`, `compute_ssm`) agree to 10⁻¹⁰. Test `test_field_equals_compute_ssm_of_smoothed_seismicity`, n = 1, 5, 25.
- Both follow the adaptive kernel of Helmstetter et al. (2007), except that the normalisation is over the grid cells inside 500 km rather than over the plane, so all of an event's weight stays in the model.
- **The difference is in `optimize_kernel`** (smoothed_seismicity):
  - It puts every test event in the nearest grid node, even an event hundreds of kilometres outside the grid. Here a test event counts only inside a cell.
  - It counts events, not weights; here a test event counts with its class weight.
  - Its default event weights are 1/T, or completeness weights when the catalogue carries them; here they are equal.
- Ported: the psha_chile7 kernel (`smooth.py`), with the S-test score of `optimize_kernel` rewritten with these three changes.

**Calibration of n** (`tables/calibration_2026-11-15.csv`):
- Split: train before 2010-01-01, test from 2010-01-01 to the end of the catalogue (2026-11).
- Events: declustered, complete in the table of DECISIONS (Mw 5.0 from 1976, 5.2 from 1964, …), class weights.
- Score: log-likelihood of the test events, the forecast scaled to the observed test count. Δ is the difference to the best candidate; n = 1–3 are a diagnostic, not candidates.

| unit | option | train / test (weighted) | n = 1 | 2 | 3 | **5** | 10 | 15 | 25 | 50 | 100 | gain over uniform at n = 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| forearc | GK | 87.8 / 46.1 | +0.7 | +2.0 | +1.1 | **0** | −4.2 | −8.2 | −13.1 | −18.9 | −22.7 | 38.6 |
| | NN | 100.0 / 54.7 | +0.5 | +2.6 | +2.4 | **0** | −3.4 | −7.1 | −11.3 | −17.7 | −22.0 | 40.6 |
| arc | GK | 37.9 / 18.4 | −1.9 | +2.7 | +2.5 | **0** | −3.4 | −3.8 | −4.0 | −4.3 | −4.3 | 8.5 |
| | NN | 50.4 / 18.0 | −4.0 | +1.1 | +1.1 | **0** | −3.2 | −4.6 | −4.3 | −4.9 | −5.0 | 7.7 |
| backarc | GK | 66.0 / 25.2 | +0.7 | +0.4 | +0.3 | **0** | −0.7 | −1.4 | −2.0 | −4.4 | −6.7 | 16.0 |
| | NN | 81.9 / 25.3 | +0.5 | +0.3 | +0.1 | **0** | −0.7 | −1.2 | −1.3 | −2.7 | −6.8 | 16.2 |
| Patagonia | GK | 19.0 / 14.0 | +5.7 | +5.2 | +4.0 | **0** | −13.9 | −14.9 | −15.4 | −15.4 | −15.4 | 22.7 |
| | NN | 21.0 / 17.0 | +4.6 | +4.3 | +3.4 | **0** | −14.1 | −14.5 | −15.7 | −15.7 | −15.7 | 22.0 |
| crustal family | GK | 210.7 / 103.7 | −6.3 | −1.9 | −0.7 | **0** | −9.1 | −10.7 | −13.5 | −15.3 | −17.0 | 30.3 |
| | NN | 253.3 / 114.9 | −8.4 | −2.2 | −0.7 | **0** | −7.8 | −8.6 | −8.7 | −9.5 | −10.6 | 23.7 |

- **n = 5 everywhere**, for both declustering options, so one n per class; the two options do not differ.
- Arc (18 test events) and Patagonia (14–17) have fewer than 20 and take the family n, which is also 5.
- **n = 5 is the smallest candidate, so the optimum lies at the edge of the range.** Below it the score keeps rising for the forearc, backarc and Patagonia, by 0.3–5.7, and falls for the family, by 0.7–8.4. The family optimum is n = 5. The forearc's is n = 2, but n = 2 to 5 lie within 2.6 log units.
- The gain over a uniform map is 8–41 log units. In the arc it is small (8 for 18 events), as expected for a class whose recent events (2007 Aysén fjord, 2004 Teno) differ from its old ones.
- With n = 5 the median bandwidth of the training events is 40–55 km (forearc), 70–90 km (backarc), about 100–125 km (arc) and 145–215 km (Patagonia).
- psha_chile7 used n = 15 for crustal. Here n = 15 scores 4–15 log units worse in every class.

**Kernel diagnostic** (after Pablo's question; `kernels.py`, `tables/calibration_kernels_2026-11-15.csv`, `figs/kernel_calibration_2026-11-15.png`). The same split, repeated with a Gaussian kernel (exp(−r²/2d²), same adaptive d) and on the full catalogue (complete events, not declustered). The chosen n is unchanged. Differences to the power law at n = 5, in log units:
- **Power law, n = 5, is best or within 3 log units in every class and catalogue.** Smaller n (2–3) gains at most 2.7, except in Patagonia (up to 5.7 at n = 1, on 14–17 test events).
- **The Gaussian is never clearly better.** In single classes it is within ±3, at best +3.4 (forearc, Gardner–Knopoff, n = 3). On the crustal family it is 6–10 worse at its best n, and it collapses at n = 1 (−30 to −57). Its thin tail gives almost no rate to test events away from the training events.
- **Full catalogue:** the power law picks n = 3 (forearc), 2 (arc), 1 (backarc, flat to within 0.8 over n = 1–100), 1 (Patagonia), and 5 for the family. The test set then includes the 2010 Pichilemu sequence, so its scores are not comparable with the declustered ones.
- Differences of 2–3 log units on 14–55 test events are not a meaningful preference. Helmstetter's power law with n = 5 stays.

**Joint search of n and the exponent** (Pablo, 15 Nov; exponents 0.75–4.0, n 1–100, both declustering options). No interior optimum:
- forearc: still rising at exponent 4 (best n 10, +5.7 / +4.7 over n 5, exponent 1.5)
- backarc: flat within about 1 log unit
- crustal family (taken by arc and Patagonia): n 1 with exponent 1.0
- n and the exponent trade off and cannot be separated on one split with 14–55 test events per class

**Decided (Pablo):** exponent 1.5 (Helmstetter et al. 2007), n from the candidates 5–100: n = 5 in every class. With n 1–3 allowed, the per-class picks move (forearc 2, backarc 1) for gains of 0.7–2.0, while the merged crustal family stays at 5.

**Test events outside the grid.** 18.2 of the 25.2 backarc test events (weighted) and 5–8 of 14–17 in Patagonia lie outside the crustal grid.

**The grid of psha_chile7 pulls rate into its eastern edge** (`tables/grid_outside_2026-11-15.csv`; the field also computed on the same grid extended to 80–60° W):

| class | events outside the grid | kernel mass outside the grid | share in the grid's eastern 0.5°, as built | same, on the extended grid |
|---|---|---|---|---|
| forearc | 8–9 % | 14–15 % | 1 % | 1 % |
| arc | 0 | 15–19 % | 11 % | 9 % |
| backarc | **69–71 %** | 65–67 % | **47–49 %** | 15–16 % |
| Patagonia | 24–29 % | 42–44 % | 12–13 % | 4 % |

- The grid ends about 1° east of the border. The backarc events of San Juan and the Sierras Pampeanas lie outside it.
- The field is normalised over the cells inside the grid, as in psha_chile7, so their weight is piled onto the eastern edge. Half the backarc rate ends up within 0.5° of that edge, against 15 % if the grid reached 60° W.
- It shows as the dark rim at 31–34° S in `figs/background_N5_2026-11-15.png`. It moves backarc rate about 100 km closer to Santiago and the Andean towns than the events are.
- The brief fixes the grid, so it is kept. Proposed in the open points.

**Rates, shapes and the moment convention:**
- The background lists (`background.mfd`) give the N(≥ 5, 6, 7) of the fit table within 0.2 %. Test, both shapes.
  - The cut list ends at the class Mmax (7.4, 7.9, 7.7, 8.0).
  - The tapered list ends at Mmax + 0.2, its last bin carrying the rate of the line above (DECISIONS, Statistics, changed 15 Nov from "about one unit above the corner"; files rebuilt).
  - `min_mag` is the first bin centre, 5.0.
- Fault MFDs come from `model/faults/rates.py`, unchanged: moments at the bin centres, `min_mag` 6.0 at the first bin centre.
  - Test: every shape of every branch returns its target moment to 10⁻⁹.
  - Test: Mmax lands on the 0.1 grid.
  - Test: the weighted mean of the 36 branches equals `rates.source`.
- The class sums reproduce the D16b table exactly (arc A 0.431, B 1.149, B-mm 0.597). The MFDs here are those of D16b; only the per-branch values are new.
- **Shapefile fields** (LEARNINGS): no zero or missing slip rate, dip, length or MASCSN thickness in A or B. Zero rakes are the sinistral faults (5 in A, 7 in B).
- **Magallanes–Fagnano** is one system source in every fault file (`f_MF_system`; no CL-056 / AR-0056 / MASCSN-720, 721, 726 sources; test).
  - Length 490 km (A) or 494 km (B) summed over the traces.
  - Mmax 7.7 / 8.0 at 10 / 20 km.
  - N(≥ 6) 0.050 (A, B) and 0.027 (B-mm).
- **Trimmed lists:** a background cell list ends at its last non-zero bin (in the arc of A, at 5.9 up to 7.1, then the bins above). The rate check compares sums per source, not lengths.

**Events of Mw ≥ 6 within 10 km of a fault trace** (A or B; `tables/events_near_faults_2026-11-15.csv`, 57 events, most of them historical with small crustal weights). Those with crustal weight ≥ 0.3:

| date | Mw | class (crustal weight) | fault, km |
|---|---|---|---|
| 1960-06-06 | 7.7 | arc (1.0) | Canal Costa, 3 |
| 1919-03-02 | 7.2 | arc (0.38) | Peulla–Cochamó, 2 (B: unnamed, 0.1) |
| 1960-06-20 | 7.0 | forearc (0.31) | Morguilla (B), 0.6 |
| 1861-03-20 | 7.0 | backarc (0.45) | Cerro La Cal, 5 |
| 1950-01-30 | 6.9 | Patagonia (1.0) | Río San Juan (B), 6 |
| 2010-03-11 | 6.9 | forearc (1.0) | Pichilemu, 5 |
| 1907-06-13 | 6.8 | arc (0.38) | Neltume, 6 |
| 2007-11-15 | 6.8 | forearc (0.39) | Mejillones, 0.2 |
| 1977-11-23 | 6.6 | backarc (0.44) | Las Chacras, 0.5 |
| 2021-01-19 | 6.5 | backarc (1.0) | Maradona–Acequión, 5 |
| 1941-07-03 | 6.5 | backarc (0.44) | Niquizanga, 8 |
| 1962-02-14 | 7.1 | forearc (0.24) | Lanalhue, 4–9 |
| 2001-07-24, 2007-04-21, 2007-04-02, 1965-11-28 | 6.1–6.3 | arc (1.0) | Aroma (B), Los Palos, Quitralco, Riesco–Mañihuales, 4–6 |
| 2007-11-14 | 6.2 | forearc (0.79) | Mejillones, 0.2 |
| 1977-11-28, 1979-11-27 | 6.0–6.1 | backarc (1.0) | Las Chacras, Niquizanga, 1–4 |

The 1949 Magallanes doublet (Mw 7.8, 7.8) is not on the list. Its catalogue epicentres lie 16–27 km from the traces, which is within the location error of 1949 (A6).

## 4. Large events and the background Mmax (report only)

psha_chile7 removed Aysén 1960 from the arc and the Magallanes–Fagnano events of Mw ≥ 7 from Patagonia by hand. DECISIONS no longer allows that.

Crustal events of Mw ≥ 6.5 within 10 km of a trace of A or B (`tables/large_events_2026-11-15.csv`; all events of Mw ≥ 6.5 of the four classes are there with their distance):
- arc: Aysén 1960 (7.7, 3 km), 1919 (7.2, w 0.38), 1907 (6.8, w 0.38)
- backarc: 1861 (7.0, w 0.45), 1977-11-23 09:34 (6.6), 1941 (6.5), 2021 (6.5)
- forearc: 1960-06-20 (7.0, w 0.31), 2010 Pichilemu (6.9), 2007 Tocopilla aftershock (6.8, w 0.39)
- Patagonia: 1950-01-30 (6.9, 6 km from Río San Juan, B only)

Background Mmax (largest event with class weight ≥ 0.5, + 0.2; `tables/mmax_rules_2026-11-15.csv`):

| class | Mmax now, set by | without the events near faults |
|---|---|---|
| forearc | 7.4, 1960-12-02 (7.2) | 7.4 (same) |
| arc | **7.9, Aysén 1960 (7.7)** | **7.3**, 1927-11-21 (7.1) |
| backarc | 7.7, 1977-11-23 (7.5) | 7.7 (same; the 1977 epicentre is 25 km from Las Chacras) |
| Patagonia | 8.0, 1949-12-17 (7.8) | 8.0 (same; the doublet is 16–27 km from the traces) |

**The Kanamori intra-arc event is Aysén 1960.**
- 1960-06-06 05:55, 45.70° S, 73.50° W, Mw 7.7 from Kanamori and Rivera (2017), accepted in A6 (DECISIONS).
- It is a slow event, probably a multiple rupture. It lies 3 km from the Canal Costa trace (Liquiñe–Ofqui) in both databases.
- Its class is arc, weight 1, and it is the largest arc event. It sets the arc Mmax at 7.9, and through the Kagan corner the tapered tail of the arc fit.
- Without it the arc Mmax is 7.3. That changes the arc fit at Mw ≥ 7 only (N(≥ 7) 0.012). It does not touch the faults, whose Mmax is Leonard's.
- For the class-maximum sensitivity of the faults it matters: the arc class maximum 7.9 against 7.3.

Two general rules for Pablo (no event is removed in the files):
1. **All events count** (the current rule). Aysén 1960 sets the arc Mmax at 7.9 and the arc background tail. The Magallanes doublet sets Patagonia at 8.0, in line with the Fagnano system Mmax by Leonard (8.0).
2. **An event within the location error of a modelled fault, larger than the Leonard Mmax of that fault plus its uncertainty, belongs to the fault system, not to the background Mmax.** Only Aysén would move: 7.7 against Canal Costa's Leonard Mmax of 6.9–7.2 (A) or 6.6–6.9 (B). The arc Mmax becomes 7.3, and the Aysén event has no source of its size in the model unless the arc faults are joined (multi-fault ruptures, not in the model). This rule removes Mmax without adding a source for the event, so I would keep rule 1.

## 5. Lessons from psha_chile6 and 7

Used:
- **One moment convention:** moments at bin centres, `min_mag` the first bin centre, everywhere. Moment balance tested per fault and branch.
- **Fields from shapefiles** checked for zero or missing values (section 3). Fagnano's Mmax comes from Leonard on the system area, not from a field (the max_mag-0 bug of psha_chile7).
- **The no-faults baseline is the full fit,** not fit minus faults (`cr_bg_nofaults_*`).
- **Equal event weights** times the class weight; no zonation, no coast mask. Each class is smoothed over the whole grid.
- **The kernel n is calibrated,** not 15. It is 5 for all classes.
- **Rate checks with ≤ on trimmed lists:** the OpenQuake check compares sums per source.
- **Fagnano overlap:** one trace per country (D16) and one joined source; no double trace in A. B keeps strand 722 and the splays as MASCSN has them (DECISIONS).
- **Old structure kept:**
  - point sources 0–30 km, hypocentre 10 km
  - two nodal planes (strike 0 and 180, dip 60, reverse)
  - WC1994, aspect 1 for points
  - simple faults WC1994, aspect 2
  - ψ × depth × shape files per fault branch
  - a no-faults branch
- **Branch IDs are sortable** (`psi080_z20_al2`), and `branches.json` lists every file with its factors (the realization-ordering pitfall).
- **The two numbers of the brief:**
  - The faults carried 21 % of crustal N(≥ 6) in psha_chile7. Here they carry 79 % of the fit in A (0.63 / 0.80), 200 % in B and 116 % in B-mm. Most of the rise is the Mmax rule: Leonard alone gives the short faults small Mmax, so their moment goes into Mw 6–7 events. With the class maximum, A's faults carry 24 % of the fit, close to the old 21 %. The old tree also had an "observed + 0.2" branch that read the GEM area-zone max_mag (DECISIONS).
  - Puerto Williams changed from 0.10 to 0.02 g between runs. The Fagnano Mmax here is 7.7–8.0 on the system (not the segment) area. The system N(≥ 6) is 0.050 per year (A, B), as D16 found.

Old branches still missing:
- the fault Mmax branches "observed + 0.2" and Wells and Coppersmith (dropped by DECISIONS)
- fault depth 30 km (psha_chile6 tornado; DECISIONS has 10 / 20)
- fault and cap Mmin 6.5 (psha_chile6 tornado row, 15 % at Aysén; DECISIONS fixes 6.0)
- the buffer and cap rows (replaced by the join)
- the background Mmax 7.5 row
- the pattern from the full catalogue (psha_chile7 tornado row)
- multi-fault ruptures (out)
- the class-maximum fault Mmax sensitivity: computed in the tables only, no NRML files written

## 6. OpenQuake files and check

Files (`nrml/`, `branches.json`):
- **Background, 28 files** `cr_bg_<A|B|Bmm|A_cm|B_cm|Bmm_cm|nofaults>_<taper|trunc>_<gk|nn>.xml`, each 19 686 point sources. In each cell the four classes are summed: they share depths, nodal planes and scaling, so one source per cell gives the same hazard as one per class. The per-class rates are `pattern_<option>` × `background_mfd`.
- **Faults, 216 files** `cr_flt_<A|B|Bmm|A_cm|B_cm|Bmm_cm>_psi<060|080|100>_z<10|20>_<al1|al2|al3|yc|tap|hyb>.xml`: 132 sources in A, 160 in B; 0 to the depth of the branch. Rupture scaling Leonard (2014), aspect 2 (Pablo: Leonard for both Mmax and ruptures; psha_chile7 had WC1994). `_cm` is the class-maximum Mmax sensitivity, with its own background files (the join follows the faults): 28 background files in all.
- **Logic-tree fragments for S5:**
  - `lt_crustal_<db>_<shape>.xml`: sourceModel = the background of the two declustering options (0.5 / 0.5), extendModel = the 36 fault branches with ψ × depth × shape weights
  - `lt_crustal_nofaults_<shape>.xml`
  - `branches.json`: every file with its factors and weights. The tree uses the tapered fit, as S1; the database weights are left to the tornado.
- `tables/rates_2026-11-15.csv` gives N per source of every file.

**OpenQuake check** (`oqcheck.py`, `oqcheck/`; one site, Puerto Aysén, ASK14, PGA, 475 yr; no hazard interpreted):
- **Every file read by OpenQuake.** OpenQuake's own NRML converter read all 244 source files (after the class-maximum variants and Leonard scaling; 124 before) (`tables/oqcheck_2026-11-15.csv`). Per source:
  - the rate is that of `tables/rates_2026-11-15.csv` within 5 × 10⁻⁶ (the 5-digit rounding of the files)
  - the top magnitude is equal in every source
  - the source counts are equal (19 686 per background file; 132 or 160 per fault file)
- **No-faults job:** calc 501 (four background files, 4 realizations) ran in 6 min. Mean PGA 0.228 g, reported only as proof that the job runs.
- **The three fault-database jobs** (`job_A.ini`, `job_B.ini`, `job_Bmm.ini`; sourceModel 4 background files, extendModel 36 fault files, 144 realizations each) had not run when this report was written. The engine runs one job at a time, and a dead S2 job (calc 503, status "submitted", no process) blocks the queue. Skipped (Pablo): S4 ticked on the parse check; the tree structure is tested in the first city run.

## 7. Open points and proposed DECISIONS lines

Decided by Pablo during the session (for DECISIONS when he says so):
- the psha_chile7 grid stays (a grid to 60° W was built and rejected)
- kernel exponent 1.5, n = 5 (written in DECISIONS)
- fault Mmax with the class maximum is computed and written as sensitivity files
- Magallanes–Fagnano stays one joined system, with no separate-segment files (my choice, as asked)
- no MASCSN length cap in our rules; B-mm stays as MASCSN built it
- Leonard (2014) for the fault rupture scaling
- nodal planes per class only in the final model, not in the tornado
- the join: above 6.0 the background is the fit minus the faults and stops for good at the first bin where the faults reach the fit (the arc and Patagonia have no background above 6.0)


1. **The grid.** Decided (Pablo): the psha_chile7 grid stays; a grid extended east to 60° W was built and rejected (too wide). The psha_chile7 grid ends 1° east of the border. It piles 47–49 % of the backarc rate into its eastern 0.5°, against 15 % on a grid to 60° W (section 3). Proposed: "The crustal background grid covers the domain box east to 60° W (or the 300 km integration distance around the cities); the field is normalised over the whole grid." This needs a new dated grid and a rerun of `background.py`, `join.py` and `build.py` (minutes).
2. **The kernel.** Decided (Pablo), written in DECISIONS (Crustal and faults): exponent 1.5, n = 5 for every class. The merged crustal catalogue also gives n = 5 (checked only, not a rule).
3. **The arc bulge** (3.4 / 8.9 / 4.6 times the fit at Mw ≥ 6). The fault count test (section 1b) rejects the Leonard Mmax for the arc faults; the class maximum passes for A and B-mm. Options 1–3 of section 1b, Pablo decides.
4. **Patagonia bulge** (1.3 / 3.6 / 1.5). In B it comes from strand 722 at 6.5 mm/yr next to the main trace at 5.9 (D16b open point 2).
5. **The Kanamori event** = Aysén 1960. Proposed: "The intra-arc event of Kanamori is Aysén 1960 (Mw 7.7, arc); all events count, so it sets the arc Mmax 7.9 (rule 1, section 4)." This closes the open item of DECISIONS.
6. **Fault-database weights** in the tree: not decided (tornado). The fragments are per database.
7. **min_mag:** background 5.0, faults 6.0. S1 writes the interface from 5.5. MMIN_HAZ must match across families (LEARNINGS); S5 decides.
8. **B-mm and the depth branch.** As in `compare.sources`, the MASCSN moment does not change with depth. The depth branch still sets Mmax (Leonard on L × z / sin dip) and the rupture width of the MASCSN faults in that variant. "Keeps its own thickness" could instead mean Mmax and width from the FaultQuake T. Not done; the effect is on Mmax only.
9. **Nodal planes (B14, added to DECISIONS during this session):** the files use the two psha_chile7 planes; DECISIONS takes the class planes of `npd_2026-11-15.csv` from S5. With per-class planes the background must be one point source per class and cell (the files here sum the classes), about four times the size.
10. **Pattern events:** the complete events of the table (Mw ≥ 5.0 from 1976, …), as the calibration. DECISIONS (Magnitudes) still reads "catalog cut at Mw 4.5 for the spatial pattern". Mw 4.5–4.9 is complete nowhere (B9), so they are not used. Proposed: "The crustal (and in-slab) pattern uses the events complete in the table of DECISIONS."
11. **Proposed LEARNINGS lines:**
    - "A grid that ends before the events does not lose their rate: a kernel normalised over the grid piles it onto the edge (backarc S3: half the rate in the eastern 0.5°)."
    - "Fault N(≥ 6) depends more on the Mmax rule than on the slip: Leonard against the class maximum is a factor 3–4 at the same moment (S3)."
