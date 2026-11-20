# STATS session

Finished briefs and reports: `orchestration/archive/STATS_1.md` (STATS_01: `stats-01`, update `stats-02`).

Two briefs below run in parallel, in two fresh sessions: STATS_02 (fits) writes `stats-03`, STATS_03 (mechanisms and depths) writes `stats-04`. Each session does only its own brief. Both read `runs/stats/stats-02`, `runs/catalog/cat-07` and `runs/data/data-07`. Shared files: in `config/stats.yaml` each session edits only its own section, and re-reads the file just before writing; STATS_03 adds its own entry point and does not edit `run.py`. After the segment decision (Q-77) one update run brings everything together.

Format for every item decided with Pablo, one at a time: what is done now, in plain terms; a comparison figure; a small table; then the recommendation in two or three sentences. His answer goes under "Decisions with Pablo", in his words.

## Brief STATS_02 (20 Nov): declustered fits, pad tables, the crustal b

**Goal:** `runs/stats/stats-03`: `stats-02` plus the declustered fits of every unit with the four algorithms (T5), the Mmax pad tables (T6), and the crustal b settled by a small trial (D-STA-12, Q-51, Q-61).

**Read first:** `psha_chile9/CLAUDE.md`; this file's header; `docs/PORTING_MAP.md` section STATS, rows T5 and T6; in `orchestration/DECISIONS.md` the Statistics section, D-IF-08, D-IS-08, D-IS-09, D-CR-01, D-CR-02; `docs/LEARNINGS.md` sections Declustering and b-value and rates; the STATS_01 report (`orchestration/archive/STATS_1.md`); psha_chile8 `fits/DECLUSTER.md`, `fits/FITS.md` (declustered fits, pads, the crustal b), `docs/psha_chile8_reports/FITS_state_2026-11-18.md` ("Left" items 1–3); psha_chile8 code `fits/run_declustered.py`, `figs_declustered.py`, `run_pad.py`.

**What changed upstream:** `stats-02` is the base (catalogue `cat-07`; its fits identical to `stats-01`), and its declustered catalogues exist. The interface segment limits may change later (Q-77); then this brief's outputs get an update rerun, so nothing here depends on the present limits beyond running on them.

**Tasks:**
1. Port T5 into `src/psha9/stats/`: the declustered fits per unit and algorithm (Gardner–Knopoff, Grünthal, Uhrhammer, nearest neighbour) on the declustered catalogues of `stats-02`, with the full-catalogue table and Mmax (D-STA-13), both shapes; for each algorithm and unit the scoring psha_chile8 prepared for the co-authors: b against b-positive, the large-event check, the great mainshocks kept.
2. Port T6: the fits at Mmax pad 0.0 / 0.2 / 0.4 (D-STA-10).
3. The crustal b trial, in `trials/crustal_b/` (trial, not used until Pablo decides): for the four crustal classes, (i) the family b now, (ii) own b per class, (iii) penalised maximum likelihood with the crustal family b as prior (ESHM13 / ESHM20 practice, Woessner et al. 2015; check in the papers; prior width from the scatter of b within the family). Aysén 1960 (Mw 7.7) in the arc: the arc fit with a 7.5 step from 1905 or 1960 against the 1976 table, and whether it predicts the arc's large events (Q-51); then own b per class again (Q-61).
4. Run, write `stats-03` (everything of `stats-02` plus 1–2, and 3 only if Pablo adopts a change), with the declustered FMD panels of psha_chile8 and a table full against declustered per unit; compare with psha_chile8's declustered fits of 18 Nov where they exist.

**Decided with Pablo in the session:**
- a. Which algorithm is the reference of the declustered branch (D-IF-08, D-IS-09, D-CR-02; Q-14 itself stays with the co-authors): the four side by side per unit.
- b. Crustal b (D-STA-12): family, own, or penalised.
- c. Aysén 1960 in the arc (Q-51), and with it own b per class (Q-61).

**Out of scope:** the segment limits (Q-77); moment rates (Q-53, Q-56) and the geodetic construction (T7), which wait for the segments; nodal planes and the depth model (STATS_03); paper figures (FIG).

**Time:** `stats-01` took 16 minutes, mostly the Mc maps and the declustering, which this brief reuses. Estimate the four declustered fits with their bootstrap before running and tell Pablo; over ten minutes in the background with a log.

**Done when:** `stats-03` exists with the declustered fits, the pad tables and their check figures; the trial of task 3 shown; a–c answered or listed as left to do.

**Report:** below this brief, with the headings of CLAUDE.md.

## Report STATS_02 (20 Nov)

### Done
- **T5 and T6 ported:** `src/psha9/stats/extend.py` builds a new run from a finished one: the files of the base run, the fits of every unit on each declustered catalogue (both shapes, full-catalogue table and Mmax, cluster bootstrap, checks), the scoring for the co-authors (b against the full catalogue's b-positive, the large-event check, the events of Mw ≥ 7.5 each algorithm removes), the comparison with psha_chile8, and the fits at pads 0.0 / 0.2 / 0.4. `run.py`: two small changes (`top` takes the pad, `fit` takes Mmax from outside). Settings in `config/stats.yaml`, section `extend`. Test `tests/test_extend.py` (the declustered weights); stats tests pass (18).
- **Run:** `stats-03` from `stats-02` (`cat-07`, `data-07`) in 76 s (estimated 3 min). The full-catalogue fits equal `stats-02` (`full_equals_base: true` in `run.yaml`).
- **Declustered fits (tapered; b, and N(≥ 7) as a ratio to the full catalogue):**

| unit | full | Gardner–Knopoff | Grünthal | Uhrhammer | nearest neighbour | b-positive (full) |
|---|---|---|---|---|---|---|
| interface | 0.95 | 0.75, × 0.72 | 0.71, × 0.74 | 0.83, × 0.50 | 0.89, × 0.62 | 0.92 |
| 26–17.1° S | 0.90 | 0.76, × 0.71 | 0.73, × 0.71 | 0.86, × 0.46 | 0.88, × 0.59 | 0.82 |
| 32–26° S | 0.92 | 0.74, × 0.73 | 0.69, × 0.77 | 0.84, × 0.59 | 0.87, × 0.72 | 0.89 |
| 37–32° S | 0.97 | 0.67, × 0.74 | 0.63, × 0.76 | 0.71, × 0.48 | 0.88, × 0.59 | 1.03 |
| 45.55–37° S | 0.91 | 0.80, × 0.52 | 0.75, × 0.57 | 0.80, × 0.32 | 0.92, × 0.38 | 1.09 |
| in-slab, shallow | 1.12 | 0.94, × 1.43 | 0.85, × 1.78 | 1.04, × 1.13 | 1.08, × 1.02 | 1.19 |
| in-slab, intermediate | 1.19 | 1.02, × 1.36 | 0.94, × 1.63 | 1.15, × 1.00 | 1.19, × 0.98 | 1.20 |
| Jujuy nest | 1.21 | 0.81, × 1.48 | 0.64, × 1.88 | 1.05, × 1.39 | 1.21, × 0.93 | 1.11 |
| crustal family | 1.03 | 1.01, × 0.64 | 1.00, × 0.65 | 1.04, × 0.60 | 1.07, × 0.60 | 1.24 |

- Large-event check (Mw ≥ 7): the full catalogue fails 32–26° S; every declustered fit passes it; Uhrhammer and nearest neighbour fail 26–17.1° S. Mw ≥ 8 passes everywhere.
- Events of Mw ≥ 7.5 removed: all four remove the 1960 foreshocks (8.1, 7.8), 1878 (after 1877) and the second 1949 Magallanes event. Uhrhammer also removes Iquique 1877 (Mw 8.9) and 1869 as aftershocks of 1868, 1918 into 1922, 1971 and 1975 into 1960, and the 2001 and 2014 aftershocks; nearest neighbour also 1657 into 1751, 1975 into 1960, and the 2001 and 2014 aftershocks.
- Against psha_chile8's declustered fits of 18 Nov (`fits_declustered_2026-11-18.csv`, the `_family` methods): no b differs by more than 1.645 sd. N(≥ 7) differs where the units changed in STATS_01 (backarc × 2.4–3.2, the new polygon; 26–17.1° S × 1.3–1.5, the limit at 17.1° S; Patagonia × 0.4–0.6).
- **Pads (T6, maximum likelihood, full catalogue):** pad 0.0 / 0.4 against 0.2 moves b by ≤ 0.008 and N(≥ 6) by ≤ 1.4 %; N(≥ 7) forearc × 0.56 / × 1.33, Jujuy nest × 0.73 / × 1.16, backarc × 0.87 / × 1.07; in-slab N(≥ 8) × 0.47–0.49 / × 1.42–1.46; no check changes. As in psha_chile8.
- **Crustal b trial (task 3; trial, not used)** in `trials/crustal_b/`: family b, own b, penalised b (prior on the family b, width the scatter of the own b 0.16, and the EPRI widths 0.3 and 0.6), each checked against the old large events (Mw ≥ 7 in 1905–1975, Mw ≥ 7.5 in 1830–1975). Own b, from 1976: forearc 1.00 ± 0.09, arc 1.09 ± 0.13, backarc 0.96 ± 0.10, Patagonia 1.32 ± 0.46 (family 1.023 ± 0.080). Penalised b with the EPRI widths ≈ own b.
- **Papers read** (Pablo put them in `refs/`): ESHM13 used Bayesian penalised likelihood with the prior b from Weichert in b-value superzones, prior width not given (woessner_2015 p. 3565; file `woessner_etal_2013.pdf`); ESHM20 dropped it: own b with at least 30 complete events (b within 0.70–1.15), else the b of the tectonic super-zone with the source's own rate (danciu_2021 p. 46–47). danciu_2024 does not describe the b method. EPRI: prior on b, moderate sd 0.6, strong 0.3 (epri_2012_b p. 5-39).
- **Aysén 1960 and the step 7.5 from 1905, all crustal classes** (`all.py`, `arc.py`; trial, not used), ESHM20 rule:

| class | complete events | b now (family, from 1976) | b, ESHM20 + 7.5 from 1905 | N(≥ 7) now → new | Mw ≥ 7.5 in table, fitted / observed |
|---|---|---|---|---|---|
| forearc | 610 | 1.023 | 1.005 | 0.016 → 0.017 | 0 / 0 |
| arc | 83 | 1.023 | 1.033 | 0.012 → 0.012 | 0.30 / 0.89 |
| backarc | 138 | 1.023 | 0.971 | 0.016 → 0.020 | 0.34 / 0.98 |
| Patagonia | 9 | 1.023 | 1.001 (family) | 0.0012 → 0.0021 | 0.04 / 1.42, fails |

  The family b with the step is 1.001. Arc alone from 1976: own b 1.09, and it expects 0.6 old Mw ≥ 7 events against 1.8 observed; with Aysén inside (step from 1960 or 1905) its own b is 1.02–1.03.

### Outputs (run ids, paths)
- `runs/stats/stats-03/` (log `runs/stats/stats-03.log`): all files of `stats-02`, plus `fits_declustered.csv` (every unit, shape and method, the columns of `fits.csv` plus `method`), `declustered_compare.csv` (the scoring), `declustered_great.csv` (events of Mw ≥ 7.5, kept or the mainshock of their cluster, per algorithm), `declustered_compare_psha8.csv`, `fits_pad.csv`, `run.yaml`.
- `stats-03` does not carry the decisions of b and c: its reference fits are those of `stats-02` (see Left to do).
- Trials, not used: `trials/crustal_b/` (`crustal_b.py`, `crustal_b.csv`, `profiles.csv`, `crustal_b.png`; `arc.py`, `arc.png`; `all.py`, `all_classes.csv`).

### Figures to look at (paths, and what to compare with)
- `runs/stats/stats-03/figs/declustered_fmd.png`: every unit, full and four algorithms; compare with psha_chile8 `fits/figs/2026-11-18/declustered_fmd.png` and `fits/FIGURES/declustering/interface_segments_declustered.png`.
- `runs/stats/stats-03/figs/declustered_scores.png`: b against b-positive, N(≥ 5) and N(≥ 7) as ratios to the full catalogue (new).
- `runs/stats/stats-03/figs/pad.png`: N(≥ 6, 7, 8) per pad (new; psha_chile8 had tables only).
- `trials/crustal_b/crustal_b.png`, `arc.png` (trial).

### Decisions with Pablo (in his words)
- **a, reference algorithm of the declustered branch:** "Yes, nearest neighbour" (as the reference; the four stay side by side as tornado rows; Q-14 stays with the co-authors).
- **b, crustal b (D-STA-12):** first: "I always prefer having that they have their own b, because they are completely different tectonic regimes (ofc patagonia will have to borrow)"; he put Woessner et al. (2015) and Danciu et al. (2021, 2024) in `refs/` ("ok, I put them in refs, check them"); after the papers: "Yes, ESHM20 rule" (own b with at least 30 complete events, else the crustal family b; now forearc, arc, backarc own, Patagonia borrows).
- **c, Aysén 1960 in the arc (Q-51) and own b per class (Q-61):** "Ok, happy to try out for all classes"; after asking whether the step is justified by the data: "No, keep 7.5 under the justification of including such events -- they existed and got observed ---, acknoledgins that we prefer that number than the 7 for the complete table". So every crustal class takes the step 7.5 from 1905 on top of its 1976 table; the margin table would allow 7.0 from 1905, 7.5 is preferred.

### Questions for Pablo (numbered, each with a recommendation)
1. **Patagonia and the 1949 doublet.** With the step, the two Magallanes events (Mw 7.7, 7.6) enter Patagonia's table: N(≥ 5) +21 %, N(≥ 7) × 1.7, and the fit fails the Mw ≥ 7.5 check (0.04 / 1.42; it failed already as old events). They belong to the Magallanes–Fagnano fault source. Recommendation: CR decides whether they stay in the Patagonia background; if the fault source carries them, take them out of the background count (an override, with the source), and name the failure as a limitation.
2. **ESHM20's other conditions** (0.2 bins, at least three events in two consecutive bins, b within 0.70–1.15) were not applied; they do not change the outcome here. Recommendation: state the 30-event rule only, and that all own b are inside the range.
3. **Declustered branch with the 26–17.1° S failure** (Uhrhammer and nearest neighbour fail Mw ≥ 7 there, 0.46–0.59 of the full N(≥ 7)). Recommendation: revisit after Q-77; it may move with the segment limits as in STATS_01's trial.
4. **The (a, b) branches of the declustered fits** are in `fits_declustered.csv` for every algorithm (interface rows). Recommendation: IF reads the nearest-neighbour rows for the declustered half of D-IF-08.

### Requests for other sessions
- **Orchestrator:** add `woessner_2015` (file `refs/woessner_etal_2013.pdf`, BEE 13:3553–3596, 2015), `danciu_2021` (`refs/danciu_etal_2021.pdf`, ESHM20 model overview report) and `danciu_2024` (`refs/danciu_etal_2024.pdf`, NHESS 24, 3049–3073) to `docs/REFERENCES.md`. Lines for DECISIONS: D-STA-12 and D-CR-01 (ESHM20 rule), D-STA-05 (crustal: 1976 plus 7.5 from 1905), D-IF-08 / D-IS-09 / D-CR-02 (nearest neighbour as reference), Q-51 and Q-61 closed.
- **CR:** the 1949 doublet in the Patagonia background against the Magallanes–Fagnano source (question 1).
- **IF, IS, CR:** declustered parameters per unit and algorithm in `runs/stats/stats-03/fits_declustered.csv`; pads in `fits_pad.csv`.

### Learnings (proposed lines)
- Declustering: Uhrhammer's windows remove Iquique 1877 (Mw 8.9) and 1869 as aftershocks of 1868, and 1971 and 1975 into 1960: at Mw 9 its distance window covers half the margin.
- Declustering: the window methods raise in-slab N(≥ 7) by × 1.4–1.9 (b pivots down); nearest neighbour leaves it within 7 %.
- b-value: ESHM13 used penalised likelihood and replaced many results by expert judgement; ESHM20 uses own b with ≥ 30 complete events, else the super-zone b (danciu_2021 p. 46–47). The penalised b with the EPRI prior widths is practically the own b.
- b-value: the arc's own b from 1976 (1.09) rests on events below Mw 6.5; with Aysén 1960 inside the table it is 1.03.
- Completeness: a step is justified when the events it brings in were observed and the margin table supports the year; the crustal area alone cannot test it.

### Left to do
- **Implement b and c in the pipeline:** in `run.py` and `config/stats.yaml` (section `crustal`): b by the ESHM20 rule (own b with ≥ 30 complete events, else the family b) and the step 7.5 from 1905 for the crustal tables. Not done in `stats-03` (its reference fits are those of `stats-02`; a rerun of the full stage takes about 16 minutes, and the id `stats-04` belongs to STATS_03). Carry it in the update run after Q-77; check that `extend.py` then reads the crustal b of the new fits (it takes `b_from` from `run.units`).
- Patagonia's 1949 doublet (question 1), after CR.
- Figures, checked with Pablo one by one (pad, declustered FMD, scores, great events; no problem in the numbers). Fix in `extend.py` for the next run: draw the full catalogue last in `declustered_fmd.png` (its points at the great events are hidden under nearest neighbour); add a bootstrap interval and the number of pairs to b-positive in `declustered_scores.png` (crustal family 48 pairs, 45.55–37° S 38); widen the N(≥ 8) axis of `pad.png` (in-slab at 0.47 touches the edge).
- For the paper: nearest neighbour as reference with its two doubtful links named (Concepción 1657 into 1751, Arauco 1975 into 1960); Uhrhammer removes Iquique 1877 (Mw 8.9).

## Brief STATS_03 (20 Nov): nodal planes, class shares and the in-slab depth model

**Goal:** `runs/stats/stats-04`: the nodal-plane tables per class and the class shares per cell (T8), and the in-slab depth model (T9), from `cat-07` and `data-07`, ported from psha_chile8 and compared by eye with its `npd_2026-11-18` and depth cells of 18 Nov.

**Read first:** `psha_chile9/CLAUDE.md`; this file's header; `docs/PORTING_MAP.md` section STATS, rows T8 and T9; in `orchestration/DECISIONS.md` D-CR-04, D-CR-05, D-IS-04, D-IS-05, D-IS-07, D-IS-11, D-IS-12, D-CLS-03 (the depth model reads all events with their weights), D-CLS-07; `docs/LEARNINGS.md` sections In-slab and Spatial pattern; psha_chile8 `model/mechanisms/REPORT_B14.md` and `npd.py`; `model/inslab/REPORT_C14.md`, `REPORT_C15.md` and `depth.py`, `bench.py`, `run.py`, `options.py`; `docs/psha_chile8_reports/FITS_state_2026-11-18.md` ("Left" items 5–6).

**What changed upstream:** the classes (D-CLS-01 to 09: band to a slab top of 60 km, the new outer rise, no unclassified), the crustal class polygons and the in-slab area of `data-07` (the in-slab grid now covers the flat slab), the location and depth orders of D-CAT-12 and 14, the literature rows. The Riedel-Hornig catalogue is at `data/raw/faults/riedel_hornig_primary_2026-11-14.csv` (it moves to `data/raw/catalog/` later).

**Tasks:**
1. Port T8 into `src/psha9/stats/` (own entry point; settings in a section of `config/stats.yaml`): mechanism types by the P, T, B plunges (Frohlich 1992), the planes per class with the auxiliary at half weight, types below 10 % dropped, the fallback for classes with fewer than 15 weighted mechanisms (D-CR-05); the in-slab planes per sub-class (D-IS-07); the class shares per cell that the crustal sources need (D-CR-04).
2. Port T9: the in-slab depth zone and slices (D-IS-04), with the class weights (the C15 method), on the in-slab grid of `data-07`.
3. Run, write `stats-04`, with the psha_chile8 check figures of both (mechanism types per class, the depth slices); compare with `npd_2026-11-18` and the depth cells of 18 Nov.

**Decided with Pablo in the session:**
- a. Oblique as a type of its own in the crustal classes, instead of moving it to the type of the largest plunge (D-CR-05).
- b. Two planes where an in-slab class has two dominant types: the shallow class keeps reverse only now, and its normal type holds 43 % (D-IS-07, Q-29).
- c. Classes with few mechanisms (backarc, Patagonia): own mechanisms or the dominant fault system's (D-CR-05).
- d. Which depths for the depth model: the catalogue, Riedel-Hornig et al. (2026) inside Chile, or both (Q-59).

**Out of scope:** fits (STATS_02); the segment limits (Q-77); the in-slab and crustal patterns (IS, CR); paper figures (FIG).

**Time:** short in psha_chile8; estimate before the first run and tell Pablo.

**Done when:** `stats-04` exists with the nodal-plane tables, class shares, depth model and their check figures; a–d answered or listed as left to do.

**Report:** below this brief, with the headings of CLAUDE.md.

## Report STATS_03 (20 Nov)

### Done
- T8 ported into `src/psha9/stats/mech.py`, T9 into `src/psha9/stats/depth.py`; own entry point `python -m psha9.stats.planes` (figures `planes_figs.py`); settings in the `planes` and `depth` sections of `config/stats.yaml`; `run.py` not touched. Test `tests/test_planes.py` (types, auxiliary plane and Kagan angle, representative of one mechanism, slice weights; 4 pass).
- Nodal planes: Frohlich (1992) types from the P, T, B plunges, oblique to the type of its largest plunge; the two largest types per class, each at least 10 %; per type the representative mechanism is the best double couple of the summed moment tensor (Kostrov 1974, not read; each event at unit moment times its class weight). This replaces the psha_chile8 plane (separate medians of strike, dip and rake), which sat away from its cluster. Then one plane per type, chosen with Pablo class by class (table below); the run reports the Kagan angle of each chosen plane to the computed one. Classes below 15 weighted mechanisms take their fault system (Patagonia only; the extended backarc now has 44).
- Class of every crustal cell (D-CR-04): share of the 0.1° cell in each class polygon, and the class holding the centre.
- Depth model (D-IS-04, C15 method): zone to 0.439 of the Slab2 thickness (95 %), three slices, kernel weights, one layer at 0.222 of the thickness, from the catalogue only (item d). Riedel-Hornig written as a check file.
- Time: trial 7 min (three depth sets), final run 3.7 min.

| class | type | plane | weight | Kagan to computed |
|---|---|---|---|---|
| in-slab shallow | normal / reverse | 0/65/−100 / 355/35/80 | 0.44 / 0.56 | 4° / 0° |
| in-slab intermediate | normal / strike-slip | 350/65/−90 / 330/80/−130 | 0.84 / 0.16 | 0° / 2° |
| Jujuy nest | normal | 350/65/−100 | 1.00 | 3° |
| forearc | normal / reverse | 150/55/−90 / 350/35/85 | 0.38 / 0.62 | 42° / 0° |
| arc | strike-slip / reverse | 10/90/180 / 0/55/75 | 0.75 / 0.25 | 0° / 6° |
| backarc | reverse / strike-slip | 10/55/95 / 135/75/−10 | 0.74 / 0.26 | 3° / 0° |
| Patagonia | strike-slip (Magallanes–Fagnano) | 110/90/0 | 1.00 | – |

Against `npd_2026-11-18` (`npd_compare_psha8.csv`, computed pairs): in-slab planes within 0–8° (intermediate strike-slip 56°, few scattered events); the backarc changes from the Precordillera fault mechanism to its own types (44 weighted mechanisms against 8). Depth cells against 18 Nov (`depth_compare_psha8.csv`): zone bottom −3.4 km (median; the catalogue alone gives 0.439 against 0.4715), hypocentres 1.7–3.0 km shallower, slice weights within ± 0.07 (16–84 %); the top-slice weight falls by up to 0.3 along the line where the slab top is 50–60 km deep, from the interface band now ending sharply at 60 km (D-CLS-03).

### Outputs (run ids, paths)
- `runs/stats/stats-04` (reads `cat-07`, `data-07`, `stats-02`; log `runs/stats/stats-04.log`):
  - `npd.csv` (one plane per type, for IS and CR); `npd_representative.csv` (computed plane pairs); `npd_counts.csv`, `npd_shares.csv`, `mech_events.csv`, `npd_compare_psha8.csv`;
  - `crustal_cell_class.csv` (lon, lat, share per class, `cls`);
  - `depth_cells.csv` (catalogue; lon, lat, top, thk, usd, lsd, w1–w3, h1–h3, h_one, h_one_median, n_events), `depth_cells_rh.csv` (Riedel-Hornig, check only; 3 cells without events have no weights), `depth_fractions.csv`, `depth_events.csv`, `depth_events_log.csv`, `depth_compare_psha8.csv`.
- Trials, not used: `trials/stats03/` (`run-a` with all three depth sets, `items.py`, `rep.py`, `figs/`, `NOTES.md`).

### Figures to look at (paths, and what to compare with)
- `runs/stats/stats-04/figs/ternary.png`: types per class with the table planes; compare `psha_chile8/model/mechanisms/figs/ternary_2026-11-18.png`.
- `runs/stats/stats-04/figs/depth_slices.png` (zone, slice weights, one layer) and `depth_vs_psha8.png` (against the cells of 18 Nov); compare `psha_chile8/model/inslab/figs/2026-11-18/maps_weights.png`, `maps_zone.png`.
- `runs/stats/stats-04/figs/crustal_cells.png`: class of the crustal cells.
- Decision figures: `trials/stats03/figs/a_oblique.png`, `np_<class>.png` (one per class), `b_shallow.png`, `d_depthsets.png`.

### Decisions with Pablo (in his words)
- a. Oblique: "No, dont want an extra class/sm." Third types: "two representative forearcs are enough" (applied as the two largest types per class). Representative plane: "no ACE, just our current method (referenced)" (summed moment tensor).
- b. "yes, both planes for in-slab" (both types of each sub-class), then one plane per type: "Im trying to reduce the number of planes. E.g. One plane per FM. Let's go by class, so we dont come back to this."
  - In-slab shallow, intermediate, Jujuy nest: the east-dipping plane ("ok", "ok", "yes").
  - Forearc normal: "but faults are NW or WNW (e.g. Pichilemu)" → 150/55/−90; forearc reverse: "Also a NS as splay faults of the subduction? Maybe those are the reverse?" → 350/35/85, "Yes."
  - Arc 10/90/180 and 0/55/75, backarc 10/55/95 and 135/75/−10: "ok".
- c. Patagonia (5 weighted mechanisms: 3 reverse in the fold-and-thrust belt, 1 strike-slip, 1 normal): Magallanes–Fagnano 110/90/0, "ok". Backarc has its own types now.
- d. "no tornado row. Our catalog will be used for depths. Riedel Hornig is only for testing or calibrating models. The inslab depth and the interface buffer."
- Arc polygon: "The intraarc could be including backarc events, or northern events are not strike slip. Might solve later (I noticed that the intraarc polygon captured some backarc events, please annotate that issue)."

### Questions for Pablo
1. Arc polygon captures some backarc events (Pablo, above); the arc reverse type (9 events, 0.25) may come from them. Recommendation: DATA redraws the arc–backarc line where backarc events fall inside, then a STATS update; until then the arc reverse plane stands.
2. D-CR-05 and D-IS-07 change: one plane per type at the full type weight (not the plane and its auxiliary at half weight), the two largest types, the summed moment tensor as the representative, the planes chosen by class. Recommendation: the orchestrator replaces both lines with the table above.
3. Forearc normal at 150/55/−90 (Pichilemu) is 42° from the computed N–S plane: the northern N–S east-dipping Coastal Cordillera normal faults (556 km in the database) get a NW plane. Recommendation: accept for now (one plane per class); a north–south split only if the hazard shows it matters.

### Requests for other sessions
- IS: read `npd.csv` (in-slab rows, one plane per type, cell sub-class by D-IS-07) and `depth_cells.csv` of `stats-04`; the depth model is now the catalogue only (zone 0.439, one layer 0.222 of the thickness, zone bottom 3.4 km and one layer 2.5 km shallower than 18 Nov, medians).
- CR: read `npd.csv` (crustal rows) and `crustal_cell_class.csv`.
- CAT (with Q-68): about 20 of the 53.5 forearc reverse weight is interface events at or below the slab top (median 7 km below, crustal weight median 0.28); shallow in-slab reverse events crowd 0–10 km below the slab top. Both are the interface band at work; to look at in the calibration.
- DATA: the arc–backarc line (question 1).
- Riedel-Hornig for the calibration (Q-68) and depth-model checks: `depth_cells_rh.csv` and `depth_events.csv` (source `rh`).

### Learnings (proposed lines)
- Fits / source models: "A representative plane from separate medians of strike, dip and rake falls outside its cluster for scattered types; the summed moment tensor of the type sits in it. For small scattered groups its best double couple can be far from any event (in-slab shallow strike-slip 75° on average), so keep only the two largest types (STATS_03)."
- Source models: "For dip-slip mechanisms both nodal planes strike the same way; a 'trench-parallel' rule does not pick a plane, the dip direction does (STATS_03)."
- In-slab: "The catalogue alone puts the 95 % zone at 0.439 of the Slab2 thickness, Riedel-Hornig at 0.475; the catalogue shows the double zone as two peaks at 0.12 and 0.30 (STATS_03)."

### Left to do
- Nothing of the brief. Open: questions 1–3; the arc polygon (later, Pablo).
