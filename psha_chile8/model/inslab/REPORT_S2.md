# S2: in-slab source model for OpenQuake

15 Nov 2026. Brief `tasks/S2_inslab.md`. Code in `model/inslab/`:
- `is_smooth.py`: the kernel (renamed from `smooth.py`, 16 Nov, so that pytest from `psha_chile8/` does not take the crustal module).
- `build.py`: patterns, calibration, MFDs, NRML and tables. Settings are at the top.
- `figs_s2.py`: figures.
- `oqcheck.py`: the OpenQuake check.

Tests are in `tests/test_s2.py` (10) and the C14 tests (9); all 19 pass. Build time is 2.5 minutes. C14's files are unchanged.

This task builds the source files only. No hazard is computed or read here, and the tornado is a later task.

## 1. What was built

**One point source per cell.** The cells are the 13 847 cells of `data/inslab_grid_01_2026-11-15.csv` that have a Slab2 top (the C14 cells). Each class has its own source set:

| class | domain on the grid | cells |
|---|---|---|
| in-slab, shallow | slab top at the cell ≤ 50 km | 4 901 |
| in-slab, intermediate depth | slab top > 50 km | 8 946 |
| Jujuy nest | within 0.8° of 66.9° W, 24.0° S (longitude scaled by cos lat, as `catalog/classify.py`) | 190 |

- The shallow and intermediate domains split the cells at the same 50 km slab-top line as the catalogue sub-classes. Together they tile all cells.
- The nest cells are also intermediate cells. The intermediate class keeps them because it has 792 events (by weight) inside the nest circle, above or below the nest depths. So the two classes overlap there as separate sources.
- Each class is smoothed only over its own domain. An event spreads its weight over the domain cells within 500 km, normalised to its weight. Every domain cell is reached, so every cell carries a source.

**Spatial pattern** (`tables/pattern_2026-11-15.csv`, `pattern_sums_2026-11-15.csv`):
- Events: every in-slab event, split weights and unknown depths included, with its class weight as its weight (equal event weights, no completeness weighting).
- Only the mainshocks of the declustered catalogue count. Each declustering option is used separately: Gardner–Knopoff (`gk_family`) and nearest neighbour (`nn_family`), 0.5 / 0.5.
- Only events complete in their period count (completeness table of DECISIONS: Mw 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500). The same selection is used in the calibration and in the final pattern. This is psha_chile7's "all" option.
- The pattern sums to 1 over each class domain, and to 0 outside it, for all six class × declustering patterns.

**Kernel.** Helmstetter et al. (2007): K = 1 / (r² + d²)^1.5, with d the distance to the n-th nearest event, at least 5 km, and a cut at 500 km.
- I ported `psha_chile7/lib/smooth.py`. Its kernel and the `adaptive_radii` + `compute_ssm` pair of `smoothed_seismicity/ssm/smoothing.py` compute the same field: the same n-th neighbour (self excluded), the same per-event normalisation over the cells within 500 km, and the same great-circle distance.
- `tests/test_s2.py` shows that the port and both codes agree to 1e-9 on random input. Copies of the two codes are in `tests/ref_kernels.py`, for the test only.
- Differences between the two codes, none of which matters here:
  - ssm raises an error with fewer than 2 events; psha_chile7 falls back to the 5 km floor.
  - ssm clamps the denominator at 1e-12.
  - ssm's `weights()` switches to Hiemer-style completeness weights when the catalogue has `mc_window` / `tc_years` columns. This is the known pitfall (LEARNINGS), and `optimize_kernel` calls it.
  - Neither code is the kernel of Helmstetter et al. exactly: they normalise each event over the cells it reaches, instead of over the infinite plane. Within a domain this keeps the rate of events near its edge inside it. That is what we want here.

**Calibration of n** (`tables/calibration_2026-11-15.csv`): one split per class. Train on events before 2010-01-01, test on 2010-01-01 to today. The score is the S-test log-likelihood with the forecast scaled to the observed test count.

| decl. | unit | train / test events | logL at n = 5 | 10 | 15 | 25 | 50 | 100 | n |
|---|---|---|---|---|---|---|---|---|---|
| GK | shallow | 249 / 112 | **−516.6** | −517.4 | −518.5 | −519.2 | −519.6 | −518.2 | 5 |
| GK | intermediate | 737 / 294 | **−1125.2** | −1141.7 | −1153.1 | −1171.7 | −1197.4 | −1211.2 | 5 |
| GK | Jujuy nest | 41 / 20 | **−51.7** | −53.2 | −54.8 | −59.1 | −62.3 | −62.3 | 5 |
| GK | in-slab family | 1 028 / 426 | **−1686.9** | −1704.7 | −1717.7 | −1740.7 | −1773.3 | −1792.4 | (5) |
| NN | shallow | 346 / 155 | −668.6 | **−667.9** | −670.0 | −671.1 | −671.0 | −669.1 | 10 |
| NN | intermediate | 1 110 / 475 | **−1412.1** | −1439.0 | −1456.3 | −1482.4 | −1536.8 | −1604.8 | 5 |
| NN | Jujuy nest | 131 / 90 | **−59.5** | −65.7 | −71.0 | −79.6 | −95.1 | −118.7 | 5 |
| NN | in-slab family | 1 587 / 720 | **−2133.2** | −2164.0 | −2186.1 | −2219.6 | −2292.1 | −2392.8 | (5) |

- Every class has at least 20 test events (the Gardner–Knopoff nest has exactly 20.0 by weight), so no class borrows its family's n.
- The two options differ only for the shallow class: n = 5 under Gardner–Knopoff, 10 under nearest neighbour. Each option uses its own n with its own catalogue.
- **n = 5 is the smallest candidate** and wins clearly for the intermediate class and the nest. Their optimum may be below 5. Shallow is flat: 3 log-units across all candidates.
- The kernel is much narrower than psha_chile7's 25 neighbours. The top 1 % of intermediate cells now hold 6–12 % of the class rate.

**MFDs** (`fits/tables/fits_2026-11-15b.csv`):
- Bin rates are differences of the fitted cumulative line at the bin edges (`gr.surv`). The lists start at Mw 5.5 (`min_mag` = 5.5, the first bin centre; the fits start at the edge 4.95).
- The cut line ends at Mmax: 8.2 for shallow and intermediate, 7.4 for the nest.
- The tapered list ends at Mmax + 0.2 (8.4 / 8.4 / 7.6; corners 8.04 / 8.04 / 7.26), and its last bin carries the rate of the line above it. This is the rule of DECISIONS (Statistics, from S1, 15 Nov). The list then equals the fitted line at every edge, and 0.9 % of the tapered moment sits in the last bin.
- (a, b) variants: the 5th and 95th percentiles of the rate at the controlling magnitude, min(8.8, Mmax − 0.3) = 7.9 (7.1 for the nest). This is the interface rule, from the bootstrap covariance of (a, b) in the fits table. The corner is kept. On the cut line the open-line pair narrows the spread at 7.9 by 7–9 %, because 7.9 is close to the cut. This is the convention of `fits/run.py`, kept as is.
- Rates are from the full catalogue, so they do not depend on the declustering option. Only the pattern does.

**Depth** (C14, `tables/depth_cells_2026-11-15e.csv`):
- Upper depth = Slab2 top. Lower depth = top + 0.475 × thickness.
- Three hypocentres: `hypoDepthDist` with the C14 weights, renormalised and rounded to 0.001 so that they sum to exactly 1.
- One layer: the C14 median of the zone's events (`h_one`), not the middle of the zone.

**Ruptures** (as psha_chile7): `StrasserIntraslab`, aspect ratio 1. Two nodal planes, 0.5 each: strike 180°, dip 60°, rake −90° (dipping west, normal) and strike 0°, dip 30°, rake 90° (dipping east, reverse).

**Branches** (`nrml/branches.json`): declustering (gk, nn) × shape (tapered, cut) × (a, b) (p05, ml, p95) × layers (l3, l1) = 24 branches.
- Each branch has three files, one per class: 72 files, `nrml/is_<class>_<decl>_<shape>_<ab>_<layers>.xml`, 381 MB.
- Rates per cell for every declustering × shape × (a, b) are in `tables/bins/rates_*.csv.gz`. The layer options only change depths.
- The reference tree has two branches, tapered / ML / three layers, gk and nn at 0.5 / 0.5. The other 22 branches carry weight 0 and exist only for the later tornado.
- Fragment for S5: `nrml/source_lt_inslab.xml` (one sourceModel branch set; each branch lists its three files).

**Hazard settings stated:**
- Sources from Mw 5.5 (first bin centre), the same as the interface (Pablo, 15 Nov).
- Maximum distance 500 km and point-source distance 100 km (DECISIONS, Hazard runs).
- `ps_grid_spacing` is not set (section 4).

## 2. Rate table

N(≥ M) per year of the summed sources, per class. The table shows the gk files; the nn files carry the same totals, because the pattern only moves rate between cells. All 24 branches are in `tables/rates_2026-11-15.csv`, and the fit's own value is beside each number there.

| class | shape | (a, b) | b | N(≥ 5.5) | N(≥ 6) | N(≥ 7) | N(≥ 7.5) | N(≥ 8) |
|---|---|---|---|---|---|---|---|---|
| shallow | tapered | p05 | 1.211 | 2.270 | 0.563 | 0.0339 | 0.0075 | 0.0010 |
| shallow | tapered | ML | 1.151 | 2.456 | 0.652 | 0.0451 | 0.0108 | 0.0016 |
| shallow | tapered | p95 | 1.091 | 2.658 | 0.756 | 0.0599 | 0.0153 | 0.0024 |
| shallow | cut | ML | 1.153 | 2.450 | 0.649 | 0.0443 | 0.0107 | 0.0018 |
| intermediate | tapered | p05 | 1.197 | 6.404 | 1.613 | 0.1001 | 0.0227 | 0.0031 |
| intermediate | tapered | ML | 1.154 | 6.705 | 1.775 | 0.1219 | 0.0290 | 0.0042 |
| intermediate | tapered | p95 | 1.110 | 7.019 | 1.954 | 0.1484 | 0.0371 | 0.0057 |
| intermediate | cut | ML | 1.156 | 6.682 | 1.763 | 0.1195 | 0.0287 | 0.0047 |
| Jujuy nest | tapered | p05 | 1.375 | 0.761 | 0.155 | 0.0047 | 0.0002 | 0 |
| Jujuy nest | tapered | ML | 1.229 | 0.907 | 0.219 | 0.0093 | 0.0005 | 0 |
| Jujuy nest | tapered | p95 | 1.082 | 1.081 | 0.308 | 0.0183 | 0.0011 | 0 |
| Jujuy nest | cut | ML | 1.236 | 0.898 | 0.214 | 0.0096 | 0 | 0 |

The variants pivot at the controlling magnitude, so N(≥ 5.5) moves by 5–8 % (nest 16–19 %), while N(≥ 7) moves by −25 / +33 % (shallow), −18 / +22 % (intermediate) and −50 / +98 % (nest).

Maps of N(≥ 5) per cell: `figs/pattern_gk.png`, `figs/pattern_nn.png`. MFDs against the observed series per completeness period: `figs/mfd_sources.png`. Depth sections at 20°, 23°, 30°, 33° and 38° S: `figs/sections_sources.png`.

## 3. Checks

| check | result | where |
|---|---|---|
| pattern sums to 1 over each class domain, 0 outside | 1.000000 for all six | `tables/pattern_sums_2026-11-15.csv`, test |
| summed rate of each class reproduces its fit at every bin edge within 0.1 % | largest difference 1e-14 (72 class × branch sets); within 1e-3 from the rates as written in a nest file | `tables/edge_check_2026-11-15.csv`, test |
| `min_mag` is the first bin centre; moments at bin centres | yes | test |
| (a, b) variants at the 5th / 95th percentile of the controlling rate | tapered exact; cut line 7–9 % narrower (see above) | test |
| depth weights sum to 1 in every cell | yes (also checked in the written file of the nest) | test |
| hypocentres between the upper and lower depth | yes, every cell, both layer options | test |
| weights of each branch set sum to 1 | declustering 0.5 / 0.5, (a, b) 0.185 / 0.63 / 0.185, reference tree 1 | test |
| Jujuy nest sources only inside its region | yes, all 8 nest files read | test |
| kernel port = psha_chile7 = ssm | to 1e-9 | test |
| OpenQuake reads every file, rates per source as in the tables | yes: the OpenQuake 3.26 parser (`oqcheck.read_all`) read all 72 files (336 888 sources, as built); every list starts at Mw 5.5; hypocentre weights sum to 1; no hypocentre outside its zone; N(≥ 5.5) and N(≥ 7) per class and branch within 2e-7 of the tables. The reference branch also ran a full job at Calama (calcs 498, 500) on an earlier build | `tables/oqread_2026-11-15.csv` |

## 4. Job settings for the depths

OpenQuake 3.26 reduces the three hypocentres (and the two nodal planes) of a point source to a single averaged rupture per magnitude in two places (`hazardlib/contexts.py`, `source/point.py`):
- **`pointsource_distance`.** A site farther than this distance plus the rupture radius from a source sees one rupture per magnitude, with the averaged plane and hypocentre (`iruptures`). With a single site, if any site is close, all ruptures are kept.
- **`ps_grid_spacing`.** It merges point sources onto a coarser grid and averages them; it also adds 0.7 × the spacing to the distance above.

**Settings chosen:**
- `ps_grid_spacing` not set (0).
- `pointsource_distance = 100` km for the in-slab sources, as in DECISIONS.

The three hypocentres then act for every source within about 100 km plus the rupture radius of a site: up to roughly 150 km epicentral distance for Mw 8. That covers the in-slab sources that control the hazard at a city: in psha_chile7 these were Mw 7.2–7.3 at 55–90 km. Beyond that distance the depth spread matters little next to the distance itself.

**Run time at Calama**, one branch (14 037 sources, 3.4 million point-source ruptures, 1 site, PGA, AG20, 16 cores; the calculation's own time, measured on a machine shared with two other sessions):

| setting | time |
|---|---|
| three hypocentres, `pointsource_distance` 100 km | 118 s |
| three hypocentres, `pointsource_distance` 500 km (no collapse within the maximum distance) | 94 s |
| one hypocentre, 100 km | not measured (queued behind another session's job, then stopped) |

- At one site the cost of the full depth distribution cannot be told apart from the load of the machine. A one-site job keeps every rupture of a source once the site is within the distance, so the setting changes little here.
- On a grid of sites it is the main lever on run time: beyond 100 km, OpenQuake computes 1 rupture per magnitude instead of 6 (2 planes × 3 depths).
- As a numerical check, not a hazard result: PGA 475 yr at Calama moves by 1.4 % between 100 and 500 km.
- Proposed for the city runs: keep 100 km (DECISIONS). For the tornado row "one against three layers", also run 500 km at two or three cities, to show that the collapse does not hide the depth effect.

**South of 36° S** (`tables/south36_layers_2026-11-15.csv`; N(≥ 5) per 5 km of hypocentre depth, tapered ML, both declustering options at 0.5): the rule is unchanged. The one layer puts the rate of the shallow slab at 15–20 km (0.275 per year in that bin). The three layers spread it from 5 to 20 km (0.109 / 0.111 / 0.094 per year at 5–10, 10–15 and 15–20 km). They also put 0.10–0.14 per year more at 25–40 km and 0.11 less at 40–55 km. Below 60 km the two differ by less than 0.015 per bin. The top-slice weights there come partly from the events at 33–36° S (C14).

## 5. Lessons from psha_chile6 and psha_chile7

**Used:**
- **Equal event weights**, no Hiemer-style completeness weights (Concepción's old excess). The class weight is the only weight.
- **No zonation, no coast mask or clip.** The only cut is the class domain at the 50 km slab top. psha_chile7 smoothed every class over the whole slab and found the domain cut changed hazard by ≤ 2.7 %; the brief now asks for the cut.
- **The kernel** of psha_chile7 (power law, 1.5, 5 km floor, 500 km), now with n calibrated per class.
- **`min_mag` at the first bin centre** (`HALF` pitfall). Moments at bin centres. Both tested.
- **Rate checks with a tolerance**, not equality. Every source carries the full list, so no list is trimmed.
- **Rates from the full catalogue; declustered catalogue only for the pattern** (Marzocchi and Taroni 2014), scaled to the class rate.
- **Ruptures and settings as in the last tornado:** nodal planes, Strasser in-slab scaling, aspect ratio 1, 500 km, point-source distance 100 km.
- **Logic-tree labels.** Branch IDs are sortable (`is_<decl>_<shape>_<ab>_<layers>`), and the check reads branch paths from the composite source model, never reconstructs them.
- **Thickness-fraction depths** (C14 replaces 0.30 / 0.65 with the 0.475 zone and three slices).

**Old in-slab tornado rows not built** (psha_chile7 `findings_rock800.md`, `TORNADO_final.md`):
- Settled by DECISIONS, not needed: completeness-table ensemble, Mmax pad 0 / 0.4, pattern weights `window_T`, pooled b.
- Possible inputs for the later tornado, not built here:
  - smoothing neighbours 10 / 50: the calibration table above replaces this row; n = 25 could be a sensitivity case;
  - Gaussian kernel and 200 km cut-off;
  - pattern from the full (not declustered) catalogue;
  - classification tolerance and default-depth events (catalogue variants);
  - b floors;
  - previous geometry (0.30 / 0.65 of the thickness): the C14 table still holds `old_hypo` and `old_lsd`;
  - depths by slab-top regime;
  - rupture scaling Allen and Hayes, dip 45 / 90, aspect ratio 2;
  - sources from Mw 5.5.

## 6. Open points, with proposed DECISIONS lines

1. **Calibrated n at the lower edge of the candidates.** n = 5 wins for the intermediate class and the nest in both options. Pablo (15 Nov): keep the candidates 5–100; n = 5 stands.
   - Proposed: "In-slab kernel n (S2, 15 Nov): shallow 5 (Gardner–Knopoff) / 10 (nearest neighbour), intermediate 5, Jujuy nest 5, from one split at 2010 on complete declustered events (`model/inslab/tables/calibration_2026-11-15.csv`)."
2. **Events of the pattern:** complete events only (the completeness table), the same in the calibration and in the final pattern. This is not the 4.5 cut of "Catalog cut at Mw 4.5 for the spatial pattern" (Magnitudes, 10 Nov). Mw 4.5–4.9 is complete in no period, so using it would map the network instead of the seismicity.
   - Proposed: "In-slab and crustal patterns use the declustered events complete in their period (completeness table of Statistics), not all events from Mw 4.5 (S2, 15 Nov)."
3. **Source Mmin:** settled. In-slab sources start at Mw 5.5, as the interface (Pablo, 15 Nov).
   - Proposed: "Source Mmin 5.5 (first bin centre) for the interface and the in-slab sources (Pablo, 15 Nov)."
4. **Jujuy nest depths.** The nest events (median depth 189 km, 5–95 %: 163–220 km) lie half below the zone of the nest cells (median top 149 km, lower depth 188 km). C14 left the nest out of the depth model. The nest may need its own depth range (open point 7 of C14). Not changed here. Pablo (15 Nov): the nest is there for completeness and hardly matters far from it; kept as built, narrow kernel included.
5. **Shape and layer weights in the reference tree.** I used tapered and three layers as the reference, with the cut line and the one layer at weight 0 until the tornado (as S1 does for the shape). The (a, b) variants are also at weight 0 in the tree (DECISIONS: tried in the tornado).
   - Proposed: "In-slab reference tree (S2): tapered, ML (a, b), three hypocentres; declustering 0.5 / 0.5; cut line, (a, b) 5 / 95 and one layer only in the tornado."
6. **Overlap of the nest and intermediate sources.** The 190 nest cells hold both. This is correct as a superposition of two classes, but the nest's lower depth (open point 4) and the intermediate class share the same zone there.
7. **Tapered list end:** settled. DECISIONS (Statistics, lines on Mmax and corner and on source MFDs) now says what the files do: end at Mmax + 0.2, tail in the last bin.
8. **Corner of the (a, b) variants:** settled. They keep the ML corner, with no Kagan recomputation (Pablo, 15 Nov). The Kagan corner on each variant's b would differ by 0.01–0.04.
9. **Nodal planes:** settled. The tornado keeps the two fixed planes of these files; the final run uses the B14 nodal-plane model (DECISIONS, from S5) (Pablo, 15 Nov).
10. **File size.** 72 files, 381 MB. Each branch repeats the same 14 037 sources with scaled rates. A `multiPointSource` cannot hold per-cell depths. If size matters for S5, write only the reference tree and generate the tornado files on demand.

## 7. Rerun on the A9 catalogue (16 Nov)

Inputs: catalogue `catalog/frozen/2026-11-16/catalog_2026-11-16.csv`, fits `fits/tables/fits_2026-11-16.csv`, declustered catalogues `gk_family_2026-11-16.csv` and `nn_family_2026-11-16.csv`, depth cells `depth_cells_2026-11-16.csv` (identical to 2026-11-15e). Outputs dated 2026-11-16: tables, `nrml/2026-11-16/`, `figs/2026-11-16/`, `oqcheck/2026-11-16/`. The 15 Nov files are kept.

What moved in the catalogue for the in-slab classes (complete events from Mw 4.95):
- shallow: the in-slab shares (0.16–0.42) of the great historical interface events 1513, 1575, 1604, 1570, 1657, 1822, 1835 go to 0 (A9 hints); 76 events change, summed weight 685.4 → 681.6;
- intermediate: 1929-10-19, 1926-04-28, 1796, 1845, 1833 and 1681 to weight 1; 1851 and 1894 to 0; 30 events change, 1844.9 → 1846.1;
- Jujuy nest: no change.

Per class, ML (a, b), Gardner–Knopoff pattern (rates do not depend on the pattern):

| class | shape | b 15 → 16 | Mmax | corner | N(≥ 5.5) | N(≥ 6) | N(≥ 7) | N(≥ 8) |
|---|---|---|---|---|---|---|---|---|
| shallow | tapered | 1.151 → 1.144 | 8.2 | 8.038 → 8.036 | +0.6 % | +1.4 % | +3.1 % | +4.3 % |
| shallow | cut | 1.153 → 1.145 | 8.2 | | +0.6 % | +1.4 % | +3.0 % | +4.4 % |
| intermediate | tapered | 1.154 → 1.157 | 8.2 | 8.039 → 8.040 | −0.4 % | −0.8 % | −1.5 % | −1.9 % |
| intermediate | cut | 1.156 → 1.159 | 8.2 | | −0.4 % | −0.8 % | −1.4 % | −2.0 % |
| Jujuy nest | both | unchanged | 7.4 | 7.260 | 0 | 0 | 0 | |

None passes the A9 thresholds (0.02 in b, 5 % in N(≥ 6), 0.1 in Mmax).

Kernel n (`calibration_2026-11-16.csv`, figure `figs/2026-11-16/kernel_loglik.png`). The curve is scored at n 1, 3, 5, 10, 15, 25, 50, 100 (kept for analysis); n is the first local maximum of the test log-likelihood from n = 5 up (`N_MIN`), a second maximum at large n ignored (Pablo, 16 Nov: n = 1 for the intermediate class is unreasonable). Chosen: shallow 5 (gk) / 10 (nn; the global maximum is 100, 0.3 higher, on a flat curve), intermediate 5 / 5, Jujuy nest 5 / 5. Without the floor (column `best_all`): intermediate 1 / 1, nest 3 / 1, in-slab family 3 / 3. The shallow curve is flat over 3–100 (within 3); the intermediate curve falls steeply: against n = 1, −2.1 / −3.2 at n = 3, −12 / −8 at 5, −28 / −35 at 10.

Why the intermediate class wants n = 1 (Gardner–Knopoff numbers; nearest neighbour the same):
- the test events repeat the training locations: median distance from a test event to the nearest training event 12 km, the same as between training events (11.5 km); for the shallow class 14 against 12 km;
- if the test events were drawn from the n = 10 pattern, n = 1 would lose by 46 ± 9; it wins by 28. The intermediate seismicity is stationary and clustered on a 10 km scale (persistent nests along the 90–130 km slab contour, e.g. 67.5° W 27.6° S with 22 training and 10 test events);
- the gain comes from 30–27° S (+18) and 24–21° S (+16), the flat slab and the Calama–Antofagasta belt; elsewhere n = 1 loses slightly;
- the isotropic kernel at n = 10 (bandwidth about 50 km) also spreads rate down dip: cells with the slab top at 130–300 km are 29 % of the domain and hold 14 % of the events.
- with n = 1 the bandwidth is the distance to the nearest neighbour (median 11.5 km, 17 % at the 5 km floor), so the pattern is close to a map of the training events at the 0.1° cell size.

Completeness weights (Pablo, 16 Nov): each event of the pattern carries its class weight over its completeness period, w / (t_end − T_c(m)) with T_c from the completeness table, so that every magnitude enters as a rate (an Mw 5.0–5.1 event counts over 50 years, Mw 5.2–6.9 over 62, Mw ≥ 7 over 121, Mw ≥ 8 over 527). In the calibration the training events take w / (2010 − T_c(m)); the test events share one period (2010 to today) and keep w. No magnitude scaling, no lower-year cut. The picks of n did not change with the weights. The weights move 1.2–2.3 % of the rate (at the n of `best_all`) (cells 0.75–1.12, 1st–99th percentile; the intermediate class most, where events of 1964–1976 sit).

Pattern, share of the rate that moves against 15 Nov (half the summed absolute difference; same n, catalogue and completeness weights): shallow 2.0 % (gk) / 1.5 % (nn), intermediate 1.5 % / 1.3 %, nest 1.6 % / 1.1 %.

One grid for shallow and intermediate (Pablo, 16 Nov). Each class was smoothed over its own domain (slab top ≤ 50 km / > 50 km), so an event near the line kept its kernel on its side and the sum of the two had a trough along the 50 km slab-top line: 19–20 % low at slab top 40–60 km against the same patterns on one grid. Now both classes are smoothed over all 13 847 in-slab cells, each scaled to its own fit, and the files add them; the 50 km line only splits the events for the fits. The Jujuy nest keeps its region. Effect (Gardner–Knopoff / nearest neighbour):
- the summed shallow + intermediate rate moves 2.7 % / 3.0 %; at slab top 40–50 km ×1.19 / ×1.11, 50–60 km ×1.20 / ×1.28, elsewhere within 3 %;
- 17.6 % / 15.1 % of the shallow rate lies in cells with slab top > 50 km, 7.3 % / 5.4 % of the intermediate rate in cells with slab top ≤ 50 km;
- kernel n on the same grid: 5 for every class and option. Shallow under nearest neighbour goes 10 → 5: on one grid a wide shallow kernel puts rate into deep cells where no shallow test event lies, and the shallow curve gets a clear peak (n 3; −4.4 at 5, −15 at 10) instead of the flat curve of its own domain;
- sources: the shallow and intermediate files hold every cell, 669 216 sources in the 72 files, 694 MB (was 336 888, 350 MB). One source per cell with the two MFDs summed would halve this.

Checks: 20 tests pass; edge check 1.5e-14; all 72 files read by the OpenQuake parser (336 888 sources, all from Mw 5.5, weights 1, no hypocentre outside the zone, rates within 2e-7 of the build, `oqread_2026-11-16.csv`). The Calama engine run was not done (Pablo, 16 Nov: fits and SSM parameters first).

Maps: the pattern maps are drawn as a cell mesh (pituplots `Grid.from_points` and `plot_grid`, 0.1° cells) instead of square markers, which left gaps between cells.

## 8. One source per cell (16 Nov, run 2026-11-16b)

Pablo (16 Nov): shallow and intermediate are written as one point source per cell. The MFD of a cell is the sum of the two class lists (EvenlyDiscretizedMFD from Mw 5.5, bin centre). The cell keeps its C14 hypocentres, its seismogenic depths, the TRT and the two nodal planes. The Jujuy nest stays a separate source, unchanged. Files: `nrml/2026-11-16b/`, two per branch (`is_slab_*`, `is_nest_*`), 48 files, with `branches.json` and `source_lt_inslab.xml`. `nrml/2026-11-16/` (one file per class) is kept.

- **Near-empty cells:** a cell is dropped when its rate above Mw 5.5 is below 1e-8 of the branch total, unless it lies within 50 km of an in-slab event of Mw ≥ 7 with in-slab weight ≥ 0.5 (2 700 cells are guarded). No cell is dropped in any branch: the weakest cell holds 1.3e-6 (nn) to 2.0e-6 (gk) of the total, because the kernel tail (500 km) reaches every cell. Removed rate 0 (`tables/drop_2026-11-16b.csv`).
- **Sources:** 14 037 per branch (13 847 slab + 190 nest), 336 888 in the 48 files, 350 MB (one file per class: 669 216 sources, 694 MB).
- **Rates:** per class, the sum over the kept cells equals the rate table within 4e-15, at N(≥ 5.5) and N(≥ 7), in every branch. All 48 files read by the OpenQuake parser: first magnitude 5.5, hypocentre weights 1, none outside the zone, rates within 2e-7 of the build (`tables/oqread_2026-11-16b.csv`).
- **Class shares for S5:** `tables/class_share_2026-11-16.csv` gives, per cell and rate branch (declustering, shape, (a, b); the hypocentre option does not change them), the share of the cell rate from shallow and from intermediate, above Mw 5.5 and in the Mw 7.0 bin. S5 mixes the B14 nodal-plane distributions with these shares.

Timing, reference branch (Gardner–Knopoff, tapered, ML (a, b), three hypocentres) at the 14 cities: four in-slab GMMs at 0.25 (AG20 SAM, Parker SA / SA_S, Kuehn SAM, Montalva), PGA 30 levels 0.005–3 g, PoE 0.002105, truncation 3, Vs30 800 inferred, Z1.0 40 m, Z2.5 0.6 km, 500 km, `pointsource_distance` 100 km, `individual_rlzs = true`. The queue was empty; one job at a time (`oqcheck/2026-11-16b/`, `tables/timing_2026-11-16b.csv`, `timing_pga_2026-11-16b.csv`).

| run | calc | sources | ruptures | preclassical | classical | total wall | peak memory |
|---|---|---|---|---|---|---|---|
| one file per class (`nrml/2026-11-16/`) | 516 | 27 884 | 5 010 000 | 139 s | 234 s | 4 min 03 s | 333 MB master, 796 MB largest process |
| one source per cell (`nrml/2026-11-16b/`) | 517 | 14 037 | 2 517 540 | 80 s | 132 s | 2 min 21 s | 210 MB master, 669 MB largest process |

PGA 475 yr (mean, g), the same in both runs within 0.0006 %: Iquique 0.727, Antofagasta 0.660, Calama 0.635, Copiapó 0.560, La Serena 0.964, Valparaíso 0.756, Santiago centro 0.592, Santiago Peñalolén 0.565, Concepción 0.433, Pucón 0.180, Puerto Montt 0.193, Hornopirén 0.145, Puerto Aysén 0.024, Puerto Williams 0 (no in-slab source within 500 km). OpenQuake sorts the sites by longitude; the cities are matched by coordinates.

## 9. Against MASCSN26 (in-slab)

Source: the MASCSN26 report (Bravo Sagua et al. 2026, v1.1, `../refs/faults/Mapa_Amenaza_CSN2026.pdf`): §3.3.3–3.3.4 (classes, declustering), §4 (zones 4–7, Mmax Tables 12–15), Table 16 and Figure 33 (Weichert a, b; p. 56–57), §8.2 (source model). The repository file was not read; Figure 33 confirms that a is log10 N(≥ 0) (zone 5: 6.50 − 1.07 × 5.1 = 1.04, as plotted).

MASCSN26 in-slab: intermediate depth only, events within 40 km below the Slab2 top where the top is at 50–160 km and more than 10 km below the Moho; four zones from Martin (1990), 15–18, 18–25, 25–31, 31–38° S; catalogue declustered with Knopoff (1982) windows (C_dist 100 km, C_time 130 d); truncated GR from Mw 5 with Mmax 8.3 / 8.3 / 7.4 / 8.3 and b 0.88 / 1.07 / 0.97 / 1.02; point sources spread uniformly or by the hypocentre density over a 40 km slab; dips 45° and 135° to the slab top.

Ours, reference rates (tapered, ML (a, b)), summed over the same zones (cells with latitude in the band and slab top 50–160 km; shallow, intermediate and nest added; Gardner–Knopoff pattern, nearest neighbour within 2–15 % per zone), N(≥ M) per year (`tables/mascsn_compare_2026-11-16.csv`):

| zone | N(≥ 5.5) ours / MASCSN | N(≥ 7) ours / MASCSN | ratio at 5.5 / 6 / 7 / 7.5 / 8 |
|---|---|---|---|
| 4, 15–18° S | 0.37 / 1.20 | 0.007 / 0.053 | 0.31 / 0.22 / 0.12 / 0.09 / 0.07 |
| 5, 18–25° S | 3.38 / 4.12 | 0.056 / 0.098 | 0.82 / 0.73 / 0.58 / 0.48 / 0.38 |
| 6, 25–31° S | 1.45 / 1.31 | 0.026 / 0.028 | 1.10 / 0.92 / 0.95 / – / – (MASCSN Mmax 7.4) |
| 7, 31–38° S | 1.23 / 1.38 | 0.022 / 0.039 | 0.89 / 0.76 / 0.57 / 0.49 / 0.39 |
| zones 4–7 | 6.43 / 8.01 | 0.112 / 0.218 | 0.80 / 0.68 / 0.51 / 0.48 / 0.36 |
| zones 5–7 | 6.06 / 6.81 | 0.104 / 0.165 | 0.89 / – / 0.63 / – / – |

- **Zone 4 is mostly Peru.** Our cells start at 17.2° S, so the 0.31 there is a domain difference, not a rate difference. Over zones 5–7, where both models cover the slab, ours is 11 % lower at Mw 5.5 and 37 % lower at Mw 7.
- **The shape is the main difference.** Our b is 1.14–1.16 (full catalogue); MASCSN's is 0.97–1.07 on a declustered catalogue. The ratio falls from about 0.9 at Mw 5.5 to about 0.4 at Mw 8 in zones 5 and 7. Our own Gardner–Knopoff-declustered fits give b 0.99–1.03 for intermediate and 0.93–1.00 for shallow (`fits_declustered_2026-11-16.csv`), close to MASCSN. Window declustering removes small aftershocks and lowers b; DECISIONS takes rates and b from the full catalogue.
- **Mmax:** 8.2 with a taper ending at 8.4 (ours) against a truncated 8.3 (MASCSN). This matters little next to b.
- **Our model has in-slab rate where MASCSN has none:** of our total N(≥ 5.5) of 10.05 per year, 2.5 (25 %) lies under the shallow slab (top < 50 km; MASCSN puts these events in the interface or crust), 1.0 below a slab top of 160 km and 0.1 south of 38° S. Over the whole model, ours is above MASCSN at Mw 5.5 (10.1 against 8.0, +26 %) and below at Mw 7 (0.176 against 0.218, −19 %).
- **Zone 6 (25–31° S):** MASCSN caps it at Mmax 7.4; ours runs to 8.2, with N(≥ 7.5) about 0.003 per year there.

## 10. Mmax pad branches (16 Nov)

DECISIONS (Statistics): the Mmax pad is a tornado factor, 0.0 and 0.4 against 0.2, refitted with the Kagan corner (`fits/tables/fits_2026-11-16f_pad00.csv`, `_pad04.csv`, maximum-likelihood rows). The in-slab rows of `fits_2026-11-16f.csv` equal those of `fits_2026-11-16.csv`, so the pad 0.2 files stand. Built for the reference branch only (tapered, ML (a, b), three hypocentres), both declustering options, one source per cell as in section 8, weight 0. The nest takes the pad of its own fit. Files in `nrml/2026-11-16b/`, listed in `branches.json` with `pad` = pad00 / pad04 (pad02 for all other branches):

| branch id | files | Mmax / corner, shallow and intermediate | Mmax / corner, nest |
|---|---|---|---|
| `gk_taper_ml_l3_pad00`, `nn_taper_ml_l3_pad00` | `is_slab_<id>.xml`, `is_nest_<id>.xml` | 8.0 / 7.83–7.84, list to 8.2 | 7.2 / 7.06, list to 7.4 |
| `gk_taper_ml_l3_pad04`, `nn_taper_ml_l3_pad04` | same | 8.4 / 8.24, list to 8.6 | 7.6 / 7.46, list to 7.8 |

Rates (Gardner–Knopoff pattern; the rates do not depend on it), N per year:

| pad | shallow N(≥ 5.5) / N(≥ 7) / N(≥ 8) | intermediate | nest N(≥ 5.5) / N(≥ 7) |
|---|---|---|---|
| 0.0 | 2.497 / 0.0472 / 0.00081 | 6.749 / 0.1221 / 0.00208 | 0.923 / 0.0070 |
| 0.2 (reference) | 2.470 / 0.0465 / 0.00163 | 6.676 / 0.1201 / 0.00412 | 0.907 / 0.0093 |
| 0.4 | 2.452 / 0.0458 / 0.00227 | 6.626 / 0.1183 / 0.00571 | 0.894 / 0.0104 |

N(≥ 8) × 0.50 / × 1.39 and nest N(≥ 7) × 0.76 / × 1.12, as in DECISIONS. N(≥ 7) moves by under 2 %, in the opposite direction from N(≥ 8): the smaller pad lowers b slightly (1.136 against 1.144 for shallow). Checks: 25 tests pass, including one that reads the pad files against their fits tables; all 56 files read by the OpenQuake parser (393 036 sources, rates within 2e-7 of the build).

## 11. Tornado files for the depth and rupture options (16 Nov, run 2026-11-16c)

C15 feedback and Pablo (16 Nov): the in-slab tornado rows compare one choice against the three-layer reference; the lower depth 0.65 and the AllenHayesIntraslab scaling are tried as well. `is_tornado.py` writes `nrml/2026-11-16c/`: every file of `nrml/2026-11-16b/` copied byte for byte (sha256 checked; `branches.json` extended), plus three weight-0 branches made from the reference `gk_taper_ml_l3` (slab and nest files). Each changes one thing in every point source; rates, source ids, upper depths and nodal planes are those of the reference:

| branch id | change | input |
|---|---|---|
| `gk_taper_ml_l3_l1c15` | one hypocentre per cell at top + 0.243 × Slab2 thickness (C15); lower depth as the reference | `h_one` of `tables/depth_cells_2026-11-16d.csv` |
| `gk_taper_ml_l3_lsd065` | lower depth at top + 0.65 × thickness (13 km below the reference 0.475 in the median); the three reference hypocentres kept | `lsd` of `tables/depth_cells_lsd065_2026-11-16d.csv` |
| `gk_taper_ml_l3_ah` | rupture scaling AllenHayesIntraslab instead of StrasserIntraslab (aspect ratio 1 kept); median area × 0.62 / 0.67 / 0.72 / 0.79 at Mw 6.5 / 7 / 7.5 / 8 | OpenQuake 3.26 |

Only `h_one` and `lsd` are taken from the C15 tables of 16d. Their three slices differ from the reference cells (`depth_cells_2026-11-16.csv`: hypocentres by up to 7.7 km, weights by up to 0.64, lower depth by up to 0.26 km), and the reference stays as it is (C15). Every new value lies inside the zone of its cell. The C14 one-layer branches (`*_l1`, per-cell median) stay in the files but are not tornado rows.

`branches.json` has a `tornado` block, one row per choice, each a single branch at weight 1 (the format of the interface files):
- `is_ref`: `gk_taper_ml_l3`;
- `is_ab_p05` / `is_ab_p95`: `gk_taper_p05_l3` / `gk_taper_p95_l3`;
- `is_decl_nn`: `nn_taper_ml_l3`;
- `is_shape_cut`: `gk_trunc_ml_l3`;
- `is_mmax_pad00` / `is_mmax_pad04`: `gk_taper_ml_l3_pad00` / `_pad04`;
- `is_l1c15`, `is_lsd065`, `is_ah`.

Checks (`tables/oqread_2026-11-16c.csv`, test `test_tornado_variants_change_one_thing_only`):
- each variant file has the source ids, rate lists, upper and lower depths and hypocentres of the reference as text, except the one field it changes;
- the OpenQuake parser reads all eight files: 13 847 + 190 sources, N(≥ 5.5) 9.146 + 0.907 per year as the rate table (within 5e-8), hypocentre weights 1, none outside the zone, and the scaling relation read as named;
- 26 tests pass.
