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

**By thickness branch** (share of the weight that passes, 10 / 20 km): A 8 / 4 %, B 0 / 0 %, B-mm 0 / 13 %; class maximum: A 100 / 87 %, B 75 / 17 %, B-mm 96 / 96 %.
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

**Against the class maximum (Pablo):** it passes the test for the wrong reason. A Mw 7.9 on a 35 km × 20 km fault needs about 38 m of average slip; Leonard puts a Mw 7.9 strike-slip rupture at about 8 000 km² (400 km at 20 km thickness). The class maximum is Aysén 1960 + 0.2, an event already in the background fit, copied onto segments that cannot host it. It stays a sensitivity only. MASCSN does not join traces either: 130 independent simple-fault sources, Liquiñe–Ofqui Mmax 6.1–7.1.

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
  - ψ × thickness × shape files per fault branch
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
- **Faults, 216 files** `cr_flt_<A|B|Bmm|A_cm|B_cm|Bmm_cm>_psi<060|080|100>_z<10|20>_<al1|al2|al3|yc|tap|hyb>.xml`: 132 sources in A, 160 in B; 0 to the thickness of the branch. Rupture scaling Leonard (2014), aspect 2 (Pablo: Leonard for both Mmax and ruptures; psha_chile7 had WC1994). `_cm` is the class-maximum Mmax sensitivity, with its own background files (the join follows the faults): 28 background files in all.
- **Logic-tree fragments for S5:**
  - `lt_crustal_<db>_<shape>.xml`: sourceModel = the background of the two declustering options (0.5 / 0.5), extendModel = the 36 fault branches with ψ × thickness × shape weights
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
8. **B-mm and the thickness branch.** As in `compare.sources`, the MASCSN moment does not change with depth. The thickness branch still sets Mmax (Leonard on L × z / sin dip) and the rupture width of the MASCSN faults in that variant. "Keeps its own thickness" could instead mean Mmax and width from the FaultQuake T. Not done; the effect is on Mmax only.
9. **Nodal planes (B14, added to DECISIONS during this session):** the files use the two psha_chile7 planes; DECISIONS takes the class planes of `npd_2026-11-15.csv` from S5. With per-class planes the background must be one point source per class and cell (the files here sum the classes), about four times the size.
10. **Pattern events:** the complete events of the table (Mw ≥ 5.0 from 1976, …), as the calibration. DECISIONS (Magnitudes) still reads "catalog cut at Mw 4.5 for the spatial pattern". Mw 4.5–4.9 is complete nowhere (B9), so they are not used. Proposed: "The crustal (and in-slab) pattern uses the events complete in the table of DECISIONS."
11. **Proposed LEARNINGS lines:**
    - "A grid that ends before the events does not lose their rate: a kernel normalised over the grid piles it onto the edge (backarc S3: half the rate in the eastern 0.5°)."
    - "Fault N(≥ 6) depends more on the Mmax rule than on the slip: Leonard against the class maximum is a factor 3–4 at the same moment (S3)."

## 8. Rerun on the A9 catalogue (16 Nov)

Inputs: catalogue `2026-11-16`, `fits_2026-11-16.csv`, `gk_family` / `nn_family_2026-11-16.csv`. Fault databases and grid unchanged (2026-11-15). Outputs dated 2026-11-16; the 2026-11-15 tables stay. No NRML files (Pablo: fits checked first).

- **Arc–Patagonia boundary:** `compare.classes()` now uses `classify.arc_end()` (47.24° S), as for events. Moved to the arc: CL-006vv Teresa and CL-006yy San Rafael (A); MASCSN-146, 440, 498, 590, 731, 733, 734 (B and B-mm). CL-006aaa stays in Patagonia.
- **Kernel:** n = 5 is now fixed in the code (`N_FIX`, DECISIONS). On the new catalogue the crustal-family calibration under nearest neighbour prefers n = 50, which the arc and Patagonia would have borrowed. Kept in `kernel_n_2026-11-16.csv` as `n_cal`, not used.
- **Fits (taper):** forearc and backarc within 2 % in N(≥ 6); arc b 1.002 → 1.023, N(≥ 6) 0.130 → 0.123; Patagonia N(≥ 6) 0.067 → 0.045 (−33 %). Mmax unchanged (7.4 / 7.9 / 7.7 / 8.0).

Faults over the fit at Mw 6 (weighted-mean fault rate / fit; 15 Nov → 16 Nov):

| class | A | B | B-mm |
|---|---|---|---|
| forearc | 0.17 → 0.17 | 0.43 → 0.44 | 0.50 → 0.51 |
| arc | 3.3 → 3.7 | 8.8 → 10.1 | 4.6 → 5.2 |
| backarc | 0.21 → 0.20 | 0.21 → 0.20 | 0.21 → 0.20 |
| Patagonia | 1.3 → 1.65 | 3.6 → 3.5 | 1.4 → 1.3 |

- Arc faults N(≥ 6): A 0.431 → 0.450, B 1.149 → 1.244, B-mm 0.596 → 0.640 (the moved faults); Patagonia loses the same.
- **Arc count test** (observed 9.45 → 8.98 weighted Mw ≥ 6): A expected 27.6 → 28.8 (8 → 6 % of the tree passes), B 73.7 → 79.7 (0 %), B-mm 37.9 → 40.6 (6 %). Class maximum: A_cm 94 % (unchanged), B_cm 46 → 35 %, Bmm_cm 96 → 92 %. Mw ≥ 7 passes for A and B-mm, as before.
- **Puerto Aysén** (rate of Mw ≥ 6 within 50 km): A 0.049, B 0.123, B-mm 0.049, all +1 %; faults 99.9 %. No-faults background 0.0021 → 0.0019 (−7 %). Across the cities the totals move within ±3 % except Copiapó (−5 %); the no-faults background falls 9–18 % at Puerto Montt and Hornopirén.
- **Mmax rules** (`mmax_rules_2026-11-16.csv`): unchanged; Aysén 1960 still sets the arc at 7.9.

### 8b. Liquiñe–Ofqui multi-fault quick estimate (16 Nov)

`multifault.lofs()`:
- Database A. The 48 faults of system "Liquiñe–Ofqui" (34 main traces, slip rate ≥ 1 mm/yr) link by the UCERF3 filters and get the SHERIFS partition.
- The other arc faults keep their single-fault rates (six shapes, Leonard).
- Thickness 10 km. Chain Mmax is Leonard on the linked area, capped at the class Mmax (7.9). The cap does not bind.
- 10 seeds per case.
- Files: `tables/mf_A_lofs_2026-11-16.csv`, `figs/mf_A_lofs_2026-11-16.png`.

Observed arc events: Mw ≥ 6 8.98, Mw ≥ 7 1.74 (the fit gives 8.57). Expected inside the completeness table, mean of 10 seeds:

| jump | ψ | chains | expected Mw ≥ 6 | p | expected Mw ≥ 7 | p(≥ 2) | chain Mmax | longest | NMS |
|---|---|---|---|---|---|---|---|---|---|
| 5 km | 0.6 / 0.8 / 1.0 | 27 | 15.0 / 20.0 / 25.2 | 0.07 / 0.005 / 0.000 | 0.44 / 0.57 / 0.71 | 0.07 / 0.11 / 0.16 | 7.4 | 229 km | 5 % |
| 10 km | 0.6 / 0.8 / 1.0 | 94 | 12.6 / 16.8 / 21.0 | 0.20 / 0.03 / 0.003 | 0.61 / 0.81 / 1.02 | 0.13 / 0.20 / 0.27 | 7.4 | 229 km | 2–3 % |
| 15 km | 0.6 / 0.8 / 1.0 | 300 | 9.5 / 12.7 / 15.7 | 0.53 / 0.19 / 0.05 | 0.68 / 0.92 / 1.14 | 0.15 / 0.23 / 0.32 | 7.6 | 416 km | 3–5 % |

- **Segmented A at 10 km** (same ψ, mean of the shapes): 19.1 / 25.4 / 31.8. Linking LOFS removes 20–50 % of the Mw ≥ 6 excess. The SHERIFS GR target moves LOFS moment from Mw 6–7 into the chains.
- **Seed spread:** standard deviation 0.1–0.3 events.
- **Where the excess sits:** at Mw 6–6.5. Above 6.8 the faults run at or below the fit.
- **Count test:** passes (p ≥ 0.05) for 10 km with ψ 0.6, and for 15 km with ψ 0.6, 0.8 and 1.0. At 5 km it passes only for ψ 0.6, by a margin.
- **Aysén 1960 (7.7):** not reached at 10 km thickness. The longest chain, 416 km × 10 km, gives Leonard 7.6. The Mw ≥ 7 rate stays below the observed count (p 0.07–0.32), as you accepted for the tail.
- **NMS:** small on average (2–5 %). The worst single fault reaches 33–78 %, above the 30–40 % flag of Chartier et al. (2019): a short trace whose slip rate the GR target cannot use.
- **Not in this estimate:** B, B-mm, subsections, the Coulomb filter.

### 8c. Liquiñe–Ofqui multi-fault, databases B and B-mm, jump 15 km (16 Nov)

`multifault.lofs(db, (15.0,))`:
- The 65 faults of system "Liquiñe–Ofqui" in B. Main traces have a slip rate ≥ 3 mm/yr (34 of them; MASCSN rows start at 2 mm/yr).
- Thickness 10 km, 10 seeds.
- Files: `tables/mf_{B,Bmm}_lofs_2026-11-16.csv`, `figs/mf_{B,Bmm}_lofs_2026-11-16.png`.

Expected arc Mw ≥ 6 against 8.98 observed (ψ 0.6 / 0.8 / 1.0; single faults at 10 km in brackets):

| database | expected Mw ≥ 6 | p | expected Mw ≥ 7 | chains | longest | chain Mmax | NMS mean / max |
|---|---|---|---|---|---|---|---|
| A (8b) | 9.5 / 12.7 / 15.7 (19.1 / 25.4 / 31.8) | 0.53 / 0.19 / 0.05 | 0.7 / 0.9 / 1.1 | 300 | 416 km | 7.6 | 3–5 % / 44 % |
| B | 30.5 / 40.7 / 50.8 (52.6 / 70.1 / 87.7) | 0.000 | 1.6 / 2.2 / 2.7 | 687 | 983 km | 7.9 (cap) | 5–6 % / 35 % |
| B-mm | 22.0 / 29.5 / 36.9 (36.8 / 49.1 / 61.4) | ≤ 0.002 | 0.7 / 0.9 / 1.2 | 687 | 983 km | 7.9 (cap) | 17–18 % / 79 % |

- **Linking cuts the excess by 40 %** in both B variants, but both still fail. B's LOFS moment is about 3 times A's, from MASCSN slip rates of 2–10.6 mm/yr on more traces. The moment, not the segmentation, drives the excess.
- **Chain length:** the B traces chain along the whole system (983 km). The class cap of 7.9 binds there; Leonard alone would give more.
- **Linked share of Mw ≥ 6:** 3–4 %. The excess sits in the single-fault Mw 6–6.5 bins.
- **B-mm NMS:** the MASCSN budget leaves 17 % of the slip unused, against 5 % in B.

## 9. Rerun on fits 2026-11-16d and the S2 kernel rule (16 Nov)

Inputs: `fits_2026-11-16d.csv` (one family b 0.975; table 5.0 from 1976; forearc Mmax 7.2); declustered catalogues 2026-11-16. Outputs dated `2026-11-16d`. No NRML files.

**Code:**
- `background.TABLE` is now 5.0 from 1976, the fits' `steps`; the arc test counts on it too.
- Forearc Mmax is 7.2 in `background.CLASSES` and `faults.CLASS_MMAX`.
- Kernel: the S2 rule (n scored at 1–100, first local maximum from 5; pattern events weighted w / (t_end − T_c(m)), training events w / (2010 − T_c(m))). `smooth.first_max` is copied from `model/inslab/is_smooth.py`.
- Figure: `figs/kernel_loglik_2026-11-16d.png`.

**Kernel n per class, before (n = 5 fixed) → after:**

| | forearc | arc | backarc | Patagonia |
|---|---|---|---|---|
| Gardner–Knopoff | 5 → 5 | 5 → **50** (family) | 5 → 10 | 5 → **50** (family) |
| nearest neighbour | 5 → 5 | 5 → **50** (family) | 5 → 25 | 5 → **50** (family) |

- **The family rule breaks for the arc and Patagonia.** Their test sets are under 20 events, so they take the n of all crustal events together, whose curve rises to 50. That family curve mixes four separated classes and so prefers a broad kernel.
- The arc has 34 / 50 training events and Patagonia 9, so the 50th neighbour is the far end of the class. Median bandwidth: 2000 km (arc), 950 km (Patagonia), against 135 and 280 km with n = 5. Those patterns are close to uniform within the 500 km cut.
- Their own curves peak at n = 3 and give n = 5 from the floor: arc −3.1 at 5 against −4.2 at 50 (gk).
- **City backgrounds (no faults)** move by this: Puerto Aysén −82 %, Valparaíso +49 %, La Serena +39 %, Copiapó and Calama +32 %. **Not for use until Pablo decides on the family rule.**

**Rates per class (tapered, full catalogue), 16 → 16d:**

| class | fit N(≥ 6) | fit N(≥ 7) | background N(≥ 6), A | background N(≥ 7), A | fault share of N(≥ 6), A / B / B-mm | faults / fit at 6, A / B / B-mm |
|---|---|---|---|---|---|---|
| forearc | 0.361 → 0.393 | 0.0246 → 0.0179 | 0.301 → 0.333 | 0.0235 → 0.0169 | 0.17 → 0.15 / 0.44 → 0.40 / 0.51 → 0.46 | 0.15 / 0.40 / 0.46 |
| arc | 0.123 → 0.147 | 0.0108 → 0.0144 | 0 → 0 | 0 → 0 | 1 (bulge) | 3.7 → 3.0 / 10.1 → 8.3 / 5.2 → 4.3 |
| backarc | 0.241 → 0.249 | 0.0218 → 0.0227 | 0.192 → 0.200 | 0.0201 → 0.0209 | 0.20 → 0.20 (all) | 0.20 |
| Patagonia | 0.045 → 0.044 | 0.0044 → 0.0044 | 0 → 0 | 0 → 0 | 1 (bulge) | 1.65 / 3.5 / 1.3 (unchanged) |

- Fault rates change by less than 2 % (b 0.975 for every class, against 0.98–1.02).
- The arc bulge shrinks because the fit rose 20 %.
- Forearc and backarc have no bulge. Their background is the fit minus the faults; the forearc N(≥ 7) falls 28 % (Mmax 7.2).

**Arc count test (table from 1976 only):**
- Observed 6.5 of Mw ≥ 6 (was 9.0 with the historical steps); none of Mw ≥ 7 since 1976.
- Expected, single faults: A 22.4 (13 % of the tree passes), B 61.8 (0 %), B-mm 31.9 (6 %).
- Class maximum: A_cm 94 %, B_cm 52 %, Bmm_cm 96 %.
- Since 1976 the test no longer sees Aysén 1960 or 1927. The Mw ≥ 7 check needs the 1905–2026 window of the fits' large-event check.

**Liquiñe–Ofqui multi-fault, A, 15 km, 10 seeds:** expected arc Mw ≥ 6 of 7.1 / 9.5 / 11.8 against 6.5 observed (ψ 0.6 / 0.8 / 1.0); p 0.58 / 0.27 / 0.10, all pass. Chains up to 416 km, Mmax 7.6; NMS 4–6 % (worst fault 46 %).

**Tornado row: background from the declustered fits** (`lower.py`; `fits_declustered_2026-11-16d.csv`, gk_family / nn_family, table full, own b; `tables/join_decl_2026-11-16d.csv`, `background_mfd_decl_2026-11-16d.csv`). Faults / declustered fit at Mw 6 (gk; nn within 0.04):

| class | A | B | B-mm |
|---|---|---|---|
| forearc | 0.23 | 0.61 | 0.71 |
| arc | 4.2 | 11.4 | 5.9 |
| backarc | 0.31 | 0.31 | 0.31 |
| Patagonia | 1.8 | 3.8 | 1.4 |

**Other:** `model/faults/fagnano.py` reads `fits_2026-11-15.csv` only for Patagonia's cut-line b in its D16 rates table (one system against separate segments). Nothing in the crustal model imports it; following the new fits would change b 0.98 → 0.97 in that diagnostic only.

### 9b. Kernel n per class (Pablo, 16 Nov)

- **Rule:** each class takes its own n: the first local maximum from 5 of its own curve. Only b pools. Patagonia is fixed at n = 5 (9–12 test events). The crustal family is scored for reference only.
- **n:** forearc 5 / 5, arc 5 / 5, backarc 10 / 25, Patagonia 5 (fixed) (Gardner–Knopoff / nearest neighbour).
- **Median training bandwidths:** forearc 59 / 44 km, arc 239 / 114 km, backarc 175 / 150 km, Patagonia 700 / 330 km.
- **No-faults background N(≥ 6) within 50 km, 16 → 16d:**
  - northern and central cities +13 to +30 %: the forearc fit is +9 %, plus the 1976 table and the new weights
  - Concepción +16 %, Puerto Williams +14 %, Pucón +4 %
  - Puerto Montt −3 %, Hornopirén −12 %, Puerto Aysén −11 %
- **With faults:** the arc and Patagonia have no background above Mw 6. Their pattern does not change the city totals, which move by −2 % (south) to +30 % (Copiapó, forearc).

## 10. Rerun on fits 2026-11-16e, crustal domain = the grid (16 Nov)

Inputs:
- fits `fits_2026-11-16e.csv` and `fits_declustered_2026-11-16e.csv`;
- catalogue `2026-11-16c` (events outside the crustal grid in the sub-class `outside`; Scotia events to outer rise);
- declustered families `*_family_2026-11-16e.csv`.

The crustal code pins its catalogue (`background.CAT`). Outputs dated `2026-11-16e`; figures in `figs/2026-11-16e/`. The join figure is now drawn per 0.1 bin, with the arc twice (single faults, multi-fault).

**Kernel n:** 5 for every class and option. The backarc now has 7 test events, inside the grid: its curve no longer drifts to 10 / 25.

**Per class, tapered, database A (16d → 16e):**

| class | fit N(≥ 6) | background N(≥ 6) | background N(≥ 7) | faults / fit at 6, A / B / B-mm | fault share of N(≥ 6), A |
|---|---|---|---|---|---|
| forearc | 0.393 → 0.332 | 0.333 → 0.272 | 0.0169 → 0.0134 | 0.15 → 0.18 / 0.40 → 0.48 / 0.46 → 0.55 | 0.18 |
| arc | 0.147 → 0.135 | 0 → 0 | 0 → 0 | 3.0 → 3.3 / 8.3 → 9.1 / 4.3 → 4.7 | 1 |
| backarc | 0.249 → 0.039 | 0.200 → **0** | 0.0209 → **0** | 0.20 → **1.28** (all three) | 1 |
| Patagonia | 0.044 → 0.020 | 0 → 0 | 0 → 0 | 1.65 → 3.9 / 3.5 → 8.2 / 1.3 → 3.0 | 1 |

- **Backarc: a new bulge.** The class rate fell 84 %, but its faults did not change (0.050 at Mw 6), so the faults now fill the fit from Mw 6 and the backarc has no background above 6.
  - The three Argentine faults outside the grid (Niquizanga, Las Chacras a and b) carry 0.0095 of the 0.050. Their events are now `outside`, but the faults are still sources.
  - Without them the backarc faults are 0.041 against the fit's 0.039: a ratio of 1.03, still at the fit.
- **Patagonia:** the faults are 3–8 times the fit, now that the class rate is halved. Magallanes–Fagnano check since 1905 (A, tree mean; range in brackets):
  - Mw ≥ 7: 0.68 expected (0.35–1.33)
  - Mw ≥ 7.5: 0.16 expected (0.04–0.32)
  - The 1949 doublet (two Mw 7.8) is one sequence. P(≥ 1 of Mw ≥ 7.5) = 0.15 with the tree mean.
- **Arc count test** (6.48 observed, the fit 6.87): single faults fail (A 22.8, 4 % of the tree passes; B 62.8; B-mm 32.4). The Liquiñe–Ofqui multi-fault branch (A, 15 km) expects 7.3 / 9.8 / 12.2 for ψ 0.6 / 0.8 / 1.0, p 0.41 / 0.15 / 0.04: it passes at ψ 0.6 and 0.8.

**Tornado row, declustered background** (faults / declustered fit at Mw 6, gk; nn in brackets), 16d → 16e:

| class | A | B | B-mm |
|---|---|---|---|
| forearc | 0.23 → 0.26 (0.27) | 0.61 → 0.67 (0.69) | 0.71 → 0.78 (0.81) |
| arc | 4.2 → 4.2 (4.1) | 11.4 → 11.6 (11.4) | 5.9 → 6.0 (5.9) |
| backarc | 0.31 → 1.23 (1.43) | same | same |
| Patagonia | 1.8 → 3.5 (4.1) | 3.8 → 7.3 (8.7) | 1.4 → 2.7 (3.2) |

### 10b. Faults outside the grid dropped (Pablo, 16 Nov)

- `faults.load` drops a source whose trace lies wholly outside the crustal grid (`faults.GRID`). That is AR-0025a Niquizanga, AR-0027a and AR-0027b Las Chacras, in A, B and B-mm.
- Magallanes–Fagnano stays (60 % of its trace is inside). Test added.
- The 2026-11-16e fault, join, arc and tornado tables and the figures are rewritten with this rule.
- **Backarc at Mw 6:** faults 0.050 → 0.041 against the fit's 0.039 (ratio 1.28 → 1.03). The background is still 0 above Mw 6, because the faults reach the fit in the Mw 6 bin.
- **Backarc at Mw ≥ 7:** faults 0.0017, half the fit. The tail above 7 is under the fit (no background there).
- **Declustered row:** backarc faults / fit 1.00 (gk), 1.16 (nn).
- Other classes unchanged.

### 10c. Liquiñe–Ofqui multi-fault: jump distance × thickness (16 Nov)

Database A; jumps 5 / 10 / 15 / 20 km; thickness 10 and 20 km; ψ 0.6 / 0.8 / 1.0; 10 seeds (`multifault.lofs("A", JUMPS_STUDY, DEPTHS_LOFS)`).
- Files: `tables/mf_A_lofs_2026-11-16e.csv`, `figs/2026-11-16e/mf_lofs_study_A.png`.
- Observed arc events, by weight: Mw ≥ 6 since 1976, 6.48. Before 1976, out of the fit: Mw ≥ 7 since 1905, 1.74; Mw ≥ 7.5 since 1830, 0.90 (Aysén 1960).

Expected arc Mw ≥ 6 since 1976 (p), for ψ 0.6 / 0.8 / 1.0:

| jump | thickness 10 km | thickness 20 km |
|---|---|---|
| 5 km | 11.9 (0.05) / 15.9 / 20.0 | 15.4 (0.006) / 20.5 / 25.8 |
| 10 km | 9.9 (0.14) / 13.1 (0.02) / 16.5 | 12.4 (0.04) / 16.7 / 20.9 |
| 15 km | 7.3 (0.41) / 9.8 (0.15) / 12.2 (0.04) | 9.3 (0.18) / 12.3 (0.04) / 15.3 (0.006) |
| 20 km | 5.8 (0.64) / 7.7 (0.35) / 9.8 (0.15) | 7.9 (0.33) / 10.7 (0.10) / 13.1 (0.02) |

Expected Mw ≥ 7 since 1905, against 1.74 observed (ψ 0.6 / 0.8 / 1.0):

| jump | thickness 10 km | thickness 20 km | longest chain, chain Mmax (10 / 20 km) |
|---|---|---|---|
| 5 km | 0.4 / 0.6 / 0.7 | 1.3 / 1.7 / 2.2 | 229 km, 7.4 / 7.7 |
| 10 km | 0.6 / 0.8 / 1.0 | 1.3 / 1.7 / 2.2 | 229 km, 7.4 / 7.7 |
| 15 km | 0.7 / 0.9 / 1.1 | 1.2 / 1.6 / 2.0 | 416 km, 7.6 / 7.9 |
| 20 km | 0.5 / 0.6 / 0.8 | 1.0 / 1.4 / 1.7 | 860 km, 7.9 / 7.9 |

- **Reaching Aysén** (≥ 7.7) takes 20 km thickness or a 20 km jump; seeds do not change it. At 20 km thickness and a 15 km jump, Mw ≥ 7.5 since 1830 is 0.38 / 0.51 / 0.62 expected against 0.9 observed.
- **The trade-off:** thickness 20 km fits the large events, while thickness 10 km fits the Mw 6 count. No single case passes both at ψ 0.8.
  - Closest: jump 15 km, thickness 20 km, ψ 0.6 (Mw ≥ 6: 9.3, p 0.18; Mw ≥ 7: 1.2 against 1.7).
  - Also: jump 20 km, thickness 20 km, ψ 0.6–0.8 (7.9–10.7, p 0.33–0.10; Mw ≥ 7: 1.0–1.4).
- **A 20 km jump** links the whole system (842–860 km chains, the cap 7.9 binds). NMS rises to 10–13 % on average and up to 93 % on one fault, beyond the 30–40 % flag of Chartier et al. (2019) for that fault.
- **Seed spread:** 0.1–0.5 events. More seeds smooth the curves only.
- The join figures (`join_*.png`) now show the events of Mw ≥ 7 before 1976 as open diamonds (since 1905; Mw ≥ 7.5 since 1830), out of the fit.

### 10d. Jump × thickness study for B and B-mm (16 Nov)

Same setup as 10c (65 Liquiñe–Ofqui faults; main traces from 3 mm/yr). Figures: `figs/2026-11-16e/mf_lofs_study_{A,B,Bmm}.png`; tables `mf_{B,Bmm}_lofs_2026-11-16e.csv`.

Expected arc Mw ≥ 6 since 1976 (6.5 observed), at ψ 0.6 / 1.0:

| jump | B, 10 km depth | B, 20 km thickness | B-mm, 10 km thickness | B-mm, 20 km depth | longest chain |
|---|---|---|---|---|---|
| 5 km | 38.7 / 64.6 | 50.0 / 83.6 | 27.6 / 46.0 | 18.4 / 30.8 | 250 km |
| 10 km | 28.3 / 47.4 | 36.8 / 61.5 | 21.8 / 36.4 | 14.8 / 24.9 | 690–700 km |
| 15 km | 23.8 / 39.7 | 31.3 / 52.0 | 17.4 / 29.1 | 12.7 / 21.1 | 930–980 km |
| 20 km | 18.4 / 30.6 | 24.6 / 41.0 | 13.5 / 22.7 | 10.5 / 17.4 | 1 390–1 480 km |

- **B fails in every case** (p < 0.001).
- **B-mm passes only** at a 20 km jump, 20 km depth and ψ 0.6 (p 0.10), with chains of 1 400 km.
- **B's traces link along the whole system** from a 10 km jump (700 km). Its LOFS moment is 2–3 times A's.
- **B-mm is lower at 20 km thickness than at 10 km:** its moment is MASCSN's, so a wider fault gets less slip per unit area and a higher Mmax.
- **Code:** the partition is vectorised (same results to 1e-10 on A and B; B at a 20 km jump went from 22 s to 2 s per run). The full study took 18 min for B and B-mm.

### 10e. Checks of the 16e model (figures `figs/2026-11-16e/check_*.png`, `figs_checks.py`)

- **Trade-off** (`check_tradeoff`): only database A multi-fault cases fall inside both Poisson ranges (arc Mw ≥ 6 since 1976 and Mw ≥ 7 since 1905). B never does; B-mm only at chains over 900 km. Single faults are outside for every database.
- **Liquiñe–Ofqui map** (`check_lofs_map`; A, 15 km, ψ 0.8, one seed): 233–238 chains carry rate.
  - The main northern (39–41° S) and southern (46–48° S) traces release 60–100 % of their slip in linked ruptures.
  - The branch and secondary traces stay single.
- **Fault share of N(≥ 6)** (`check_fault_share_map`): nearly 1 south of 38° S in all databases; 0.2–0.8 in the northern forearc.
- **Counts by magnitude** (`check_counts`):
  - forearc: the model falls 2× under the observed count at Mw 6.5 and 7 (the family b 1.01 against its own 0.93)
  - arc: single faults over at Mw 5.5–6.5, the multi-fault branch close
  - backarc: within the ranges
  - Patagonia: faults over at Mw 5.5–6.5, and no source of the 1949 doublet's rate at Mw ≥ 7.5 since 1830
- **Moment rate** (`check_moments`): observed (Mw < 7 since 1976, 7–7.4 since 1905, ≥ 7.5 since 1830) against fit and faults (A):

| class | observed | fit | A faults |
|---|---|---|---|
| forearc | 4.5e18 | 2.7e18 | 0.29e18 |
| arc | 3.0e18 | 2.4e18 | 2.0e18 |
| backarc | 1.6e18 | 0.56e18 | 0.29e18 |
| Patagonia | 5.7e18 | 0.40e18 | 1.2e18 |

  - **Arc:** the faults release about the catalogue moment. The arc bulge is the MFD shape, not the moment, which supports the multi-fault branch over a lower ψ.
  - **Patagonia:** the faults release a fifth of the catalogue moment (the 1949 doublet) while over-predicting Mw 6.
  - **Backarc:** San Juan 1944 and 1894 put the observed moment 3× above the fit.
- **Near-fault share** (`check_near_share`, observed Mw ≥ 6 within 20 km of a trace):
  - forearc: 13–15 % observed (A) against a model fault share of 18 %, consistent
  - arc: 28–42 % (A), 50–57 % (B) against 100 %
  - Patagonia: 0–14 % (A), up to 29 % (B) against 100 % (the 1949 events are 16–27 km from the Fagnano trace)
  - So the join gives the arc and Patagonia all their Mw ≥ 6 rate on faults, where at most half the observed events are near one.

## 11. OpenQuake source model of the crustal family (S5b, 16 Nov)

Code: `build.py`, `mfsource.py`, `nrml.py`, `oqcheck.py`. Files: `nrml/2026-11-16e/` (59 files, 373 MB), `branches.json` (tree, tornado rows, every file with its factors), `lt_crustal_tree.xml`, `lt_crustal_reference.xml`. Hand-off note for S5: `S5_HANDOFF.md`.

**Modelling decisions** (Pablo's word where marked, the rest mine, written here):
1. **Fault systems** (Pablo):
   - Segmented: single-fault simple-fault sources, the six MFD shapes, Leonard Mmax; ψ × thickness × shape with the weights of DECISIONS.
   - Multi-fault: Liquiñe–Ofqui (system "Liquiñe–Ofqui" of A) by the SHERIFS partition, jump 15 km; ψ (0.6 / 0.8 / 1.0) × thickness (10 / 20 km), equal weights.
   - The class maximum is gone (its role is taken by the multi-fault ruptures).
   - Fault system weights 0.5 / 0.5 (Pablo, 16 Nov).
2. **Multi-fault branch, in OpenQuake** (mine):
   - Linked ruptures form one `multiFaultSource` per file, with Poisson occurrence probabilities for 1 yr. These files are NRML 0.5 with one source group and `investigation_time = 1`; jobs must use 1 yr.
   - Sections are one planar surface per trace segment, from the surface to the branch depth, dipping right of the trace (`cr_sections_<db>_z<depth>.xml`; OpenQuake builds a section from one surface only).
   - Single-fault Liquiñe–Ofqui ruptures are simple-fault sources with their SHERIFS MFD.
   - The other faults keep their single-fault rates as the mean of the six shapes at that ψ and depth.
   - Rupture rates are the mean of 10 SHERIFS seeds. 1 060–1 140 linked ruptures per tree file.
3. **Background**:
   - Joined (the S3 rule, kept by Pablo) with the branch-mean fault MFD of each fault system. The segmented and the multi-fault (A, 15 km) backgrounds come out equal at N(≥ 5.5) = 1.453 per year: forearc and backarc faults are the same in both, and the arc and Patagonia have no background above Mw 6 in either.
   - One point source per cell, the classes summed (mine).
   - Nodal planes: per cell the B14 class distributions mixed by the class rates there, probabilities in 1e-4 (mine). Exact where one class dominates; approximate where classes with different Mmax share a cell.
   - Depths 0–30 km, hypocentre 10 km (Pablo: keep 10 km); WC1994, aspect 1.
4. **Source Mmin 5.5** (first bin centre) for the background, as for interface and in-slab (DECISIONS, Hazard runs; Pablo); faults from 6.0. Families add in rate space; one Mmin keeps the tornado and the disaggregation like for like.
5. **Tree** (flattened, one sourceModel branch per combination; 84 branches; realizations = 84 × GMMs):
   - declustering gk / nn 0.5 / 0.5 × system 0.5 / 0.5
   - segmented: 36 branches (ψ 0.25 / 0.5 / 0.25 × depth 0.5 / 0.5 × shape 1/6)
   - multi-fault: 6 branches, 1/6 each
6. **Tornado reference** (mine): multi-fault A, jump 15 km, ψ 0.8, thickness 10 km, tapered fit, Gardner–Knopoff pattern. It is the case that passes both count tests best at ψ 0.8 (REPORT_S3 10c).
7. **Tornado rows** (14 with the reference):
   - pattern from nearest-neighbour declustering
   - background fit cut at Mmax
   - declustered background rates (lower bound; Pablo)
   - no faults, smoothed seismicity only (Pablo)
   - segmented system (six shapes 1/6, ψ 0.8, 10 km)
   - ψ 0.6, ψ 1.0
   - thickness 20 km
   - jumps 5, 10 and 20 km (Pablo: 20 km kept as a tornado row although not credible, chains to 860 km)
   - fault database B and B-mm (multi-fault 15 km; Pablo: tornado only)
   - Rows with another fault system use the background joined with that system.

**Check** (`tables/oqcheck_2026-11-16e.csv`):
- All 59 files read by OpenQuake's converter. The multi-fault sources were split against their sections as the engine does (`save_and_split`).
- 242 230 sources, none missing, rates within 4.2e-6 (5-digit rounding), top magnitudes equal.

**Wording (Pablo, 16 Nov):** the fault parameter formerly called "depth" (the 10 / 20 km branches) is the seismogenic thickness; "depth" is kept for events and the point-source hypocentre. Earlier sections use the old word.

## 12. Strict UCERF3 rupture set for Liquiñe–Ofqui (16 Nov, discussion; no rates)

Code `rupset.py` (UCERF3 path rules on 5 km subsections, strict rule, merge to whole-fault scenarios), `rupset_compare.py`, figure `figs/2026-11-16e/check_strict_scenarios.png`, table `tables/rupset_compare_2026-11-16e.csv`. Database A, 48 LOFS faults.

| depth | jump | traces | subsection ruptures | strict | scenarios | most faults | longest scenario | Mmax (Leonard) |
|---|---|---|---|---|---|---|---|---|
| 10 km | 5 | main | 2 249 | 24 | 12 | 3 | 229 km | 7.4 |
| 10 km | 5 | all | 9 034 | 42 | 22 | 4 | 246 km | 7.4 |
| 10 km | 10 | main | 4 139 | 50 | 25 | 3 | 229 km | 7.4 |
| 10 km | 10 | all | 67 783 | 101 | 52 | 5 | 339 km | 7.5 |
| 10 km | 15 | main | 13 328 | 150 | 75 | 7 | 359 km | 7.5 |
| 10 km | 15 | all | 182 261 | 239 | 121 | 7 | 359 km | 7.5 |
| 20 km | 15 | main | 13 328 | 150 | 75 | 7 | 359 km | 7.8 |
| 20 km | 15 | all | 182 261 | 239 | 121 | 7 | 359 km | 7.8 |

- **The strict scenarios are simple linear chains**, splays included (figure): no T-shapes, no side-by-side strands, no doubling back. The splays appear only as continuations off a fault tip (the Aysén splays onto the southern main trace).
- **Extents fall:** longest scenario 359 km at 15 km (416 km with the old whole-fault chains; 810 km with splays). Mmax 7.5 at 10 km thickness, 7.8 at 20 km. None reaches the arc cap of 7.9, so the drop-against-clip question does not arise in A.
- **Aysén (7.7):** reached only at 20 km thickness. At 10 km no scenario passes 7.5.
- **Subsections are 5 km at both depths** (Pablo, 16 Nov). With half-thickness pieces (10 km in the 20 km branch) nine faults of 10–14 km had one subsection and the two-subsection rule barred them from every linked rupture (22 scenarios instead of 75). The subsection is a resolution for the path rules only; now both thickness branches share the same scenarios and differ only in width and Mmax.
- **Coulomb proxy** (junction angle > 45° or a change of rake, 10 km depth): 3–7 junctions with main traces (jump 5 / 10 / 15), 9–22 with splays. The worst are a dextral main trace onto a dextral-normal splay at 48–53° (CL-006m with CL-007 and CL-012; CL-006tt with CL-006kkk). Every other junction is below 45°. The NS–NE junctions are Coulomb-compatible (Pablo).
- **Why strict loses most subsection ruptures:** partial members are nearly always the first or last fault of the path (the rupture ends mid-fault), 23 000 of 28 000 partial memberships at 15 km; mid-path partial members (a splay joining mid-trace) are 5 000. Those end-partial ruptures are what the floating single-fault ruptures and the whole-fault scenarios between them represent.

## 13. SHERIFS on the strict rupture set: one case (16 Nov)

Database A, Liquiñe–Ofqui only, 15 km jump, main traces, strict scenarios (section 12) merged to whole faults; ψ 0.6 / 0.8 / 1.0 × thickness 10 / 20 km; 10 seeds. `multifault.RUPSET = "strict"`; scenarios above the class Mmax are dropped (none in A). Table `tables/mf_A_lofs_2026-11-16e.csv` (overwritten; the chain run of 10c is in the WORKLOG), figure `figs/2026-11-16e/mf_lofs_study_A.png`.

| | chains (10c) | strict |
|---|---|---|
| scenarios | 300 | 75 |
| longest, Mmax (10 / 20 km) | 416 km, 7.6 / 7.9 | 359 km, 7.5 / 7.8 |
| arc Mw ≥ 6 since 1976 (obs. 6.5), ψ 0.6 / 0.8 / 1.0, 10 km | 7.3 / 9.8 / 12.2 | 9.2 / 12.2 / 15.3 |
| p, 10 km | 0.41 / 0.15 / 0.04 | 0.19 / 0.04 / 0.006 |
| arc Mw ≥ 6, 20 km | 9.3 / 12.3 / 15.3 | 11.7 / 15.7 / 19.6 |
| Mw ≥ 7 since 1905 (obs. 1.7), 10 / 20 km, ψ 0.8 | 0.9 / 1.6 | 0.7 / 1.7 |
| Mw ≥ 7.5 since 1830 (obs. 0.9), 10 / 20 km, ψ 0.8 | 0.08 / 0.51 | 0.05 / 0.29 |
| linked share of N(≥ 6) | 9.5 % / 5 % | 7.5 % / 4 % |
| NMS | 3–4 % / 2 % | 6–7 % / 3 % |

- **The strict set moves less moment into large ruptures:** 75 scenarios against 300, and the longest 359 instead of 416 km. More slip stays in the single faults at Mw 6–6.5, so the Mw ≥ 6 count rises by 25 % and the test passes only at ψ 0.6 and 10 km thickness (p 0.19).
- **The old chains were passing partly for a wrong reason:** the branching and overlapping chains gave many more long ruptures to spend slip on. The strict set removes them, and the arc bulge comes back in part.
- **Aysén:** 7.7 reached only at 20 km thickness (Mmax 7.8); Mw ≥ 7.5 since 1830 0.22–0.36 expected against 0.9 observed.
- Single faults of A, 10 km thickness, ψ 0.8: 25.4 expected. The strict multi-fault halves that; the chains cut it to 40 %.

## 14. Rows on the strict rupture set, and the Fagnano row (16 Nov)

**Liquiñe–Ofqui rows** (`multifault.py`, `tables/mf_A_lofs_2026-11-16e.csv`, `mf_A_lofs_splays_…`, `mf_B_…`, `mf_Bmm_…`; figures `figs/2026-11-16e/mf_lofs_study_*.png`). Arc Mw ≥ 6 since 1976 against 6.5 observed, ψ 0.6 / 0.8 / 1.0:

| row | 10 km thickness | 20 km | Mmax (10 / 20) | passes (p ≥ 0.05) |
|---|---|---|---|---|
| A main, 5 km | 12.4 / 16.5 / 20.7 | 16.4 / 21.9 / 27.6 | 7.4 / 7.7 | none |
| A main, 10 km | 11.1 / 15.0 / 18.7 | 14.3 / 19.0 / 23.9 | 7.4 / 7.7 | ψ 0.6, 10 km (0.07) |
| A main, 15 km | 9.2 / 12.2 / 15.3 | 11.7 / 15.7 / 19.6 | 7.5 / 7.8 | ψ 0.6, 10 km (0.19); ψ 0.6, 20 km (0.05) |
| A splays, 5 km | 10.7 / 14.4 / 18.0 | 13.7 / 18.4 / 23.0 | 7.4 / 7.7 | ψ 0.6, 10 km (0.09) |
| A splays, 10 km | 8.8 / 11.7 / 14.6 | 11.2 / 14.9 / 18.9 | 7.5 / 7.8 | ψ 0.6, 0.8 at 10 km; ψ 0.6 at 20 km |
| A splays, 15 km | 7.2 / 9.7 / 12.3 | 9.5 / 12.8 / 15.9 | 7.5 / 7.8 | ψ 0.6, 0.8 at 10 km (0.42, 0.15); ψ 0.6 at 20 km (0.17) |
| B, 15 km | 31 / 41 / 51 | 40 / 53 / 66 | 7.6 / 7.9 | none |
| B-mm, 15 km | 22 / 29 / 37 | 15 / 20 / 25 | 7.6 / 7.9 | none |

- Splays pass more because the Aysén splays give the single faults more linked partners; their unused slip is 30–35 % (worst fault 90 %), above the 30–40 % flag of Chartier et al. (2019): the 0.5 mm/yr splays are drained by the long ruptures.
- Best case by the count test and credibility: A, main + splays, 15 km, 10 km thickness (reference ψ 0.8, p 0.15); runner-up main traces only (ψ 0.6 only).
- Mw ≥ 7 since 1905 (1.7 observed): 0.5–0.9 at 10 km, 1.3–2.2 at 20 km. Aysén (7.7) only at 20 km.
- No scenario above the arc cap 7.9 in A; B and B-mm reach 7.9 at 20 km with scenarios of 366 km.

**Fagnano row** (`fagnano_row.py`; `tables/mf_fagnano_2026-11-16e.csv`, `figs/2026-11-16e/mf_fagnano.png`). The measured Magallanes–Fagnano traces as separate faults (`faults.load(split_system=True)`), the strict rupture set and SHERIFS with the Patagonia target, against the joined 490 km system source.
- Three of the seven traces (AR-0056b, d, g, east of 67.6° W, 82 km) lie outside the crustal grid and drop under the domain rule when split; the joined source keeps them because part of it is inside. The split model is therefore 408 km of Fagnano in four traces.
- **The traces do not chain.** CL-056b (224 km) ends 67 km from CL-056c; CL-056d overlaps CL-056c instead of continuing it, so every three-trace path uses CL-056d in part and fails the strict rule. Strict scenarios: CL-056d + AR-0056a (98 km) and, in the north, CL-006aaa + CL-006zz (130 km). Mmax of the SHERIFS model 7.3 (10 km) / 7.6 (20 km), against 7.7 / 8.0 for the joined source.
- Patagonia Mw ≥ 6 since 1976: none observed; the joined source expects 2.5–5.5 (ψ 0.6–1.0, 10–20 km), SHERIFS 3.9–8.7. Mw ≥ 7.5 since 1830 (1.7 observed, the 1949 doublet): joined 0.15–0.41, SHERIFS 0–0.16.
- **Conclusion:** with the measured traces of A, SHERIFS makes Patagonia worse on both counts: more Mw 6 (no long ruptures to spend slip on) and no source for the 1949 doublet. The joined system source is the better representation of Fagnano; the row is kept as a tornado row only. A chain across the 67 km gap between CL-056b and CL-056c would need a trace that is not in A.

## 15. Mmax pad rows (16 Nov; `pad.py`, `tables/pad_rows_2026-11-16e.csv`)

The reference branches (segmented and multi-fault A, 15 km, ψ 0.8, 10 km thickness) with the class Mmax pad 0.0 and 0.4 against 0.2 (fits tables `fits_2026-11-16f_pad00` / `_pad04`, through the background lists, the join and the multi-fault cap), and the single faults with Leonard + 0.2 / 0.4 (`faults.FAULT_PAD`). Rates per year; the large-event checks as section 10c.

**Background pad** (class Mmax 7.0 / 7.7 / 7.5 / 7.8 → 7.2 / 7.9 / 7.7 / 8.0 → 7.4 / 8.1 / 7.9 / 8.2):
- Moves only the background's tail. N(≥ 6) of the fit within 2 %; the forearc background N(≥ 7) 0.006 / 0.014 / 0.021 (pad 0 / 0.2 / 0.4), and its expected Mw ≥ 7 since 1905 0.8 / 1.8 / 2.7 against 3.5 observed (p 0.04 / 0.26 / 0.50). The backarc is similar in proportion.
- The arc and Patagonia are untouched: they have no background above Mw 6, and the multi-fault cap (7.7 / 7.9 / 8.1) is above every scenario's Mmax (7.5), so it never binds in A. The multi-fault rows are identical at the three pads.
- The segmented rows do not change either: the single faults do not read the class Mmax.

**Fault pad** (Leonard + 0 / 0.2 / 0.4 on the single faults, pad 0.2 background):
- Spreads each fault's moment over 2–4 more bins. Arc faults / fit at Mw 6: 2.97 → 2.13 → 1.58; expected arc Mw ≥ 6 since 1976: 20.4 → 14.7 → 10.8 (p 0.000 / 0.009 / 0.085). Patagonia: 3.3 → 2.5 → 1.9.
- Fault N(≥ 7) rises (arc 0.002 → 0.008); Mw ≥ 7 since 1905 0.28 → 0.71 → 1.00 against 1.7.
- The forearc and backarc faults fall below the fit at Mw 6 by more, and the backarc regains a background above 6 (0.013 / 0.020 at Mw ≥ 6).
- A fault pad of 0.4 gives the segmented reference about the same arc count as the multi-fault branch (10.8 against 12.2), by a different route: more magnitude per fault rather than linked ruptures.

**So:** the background pad is a tail-only factor (the forearc's Mw ≥ 7 check is where it shows); the fault pad is the one that moves the arc bulge. In OpenQuake terms, the rows are: background pad 0.0 and 0.4 (two background files each, segmented and multi-fault), fault pad 0.2 and 0.4 (two segmented fault files).
