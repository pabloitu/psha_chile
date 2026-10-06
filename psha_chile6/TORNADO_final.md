# psha_chile6: stage curves, final tornado and the final logic tree, 30 Sep 2026

Sections 2b-2c of FINAL_PLAN. PGA 475 yr, rock800, family jobs combined in rate
space. Sources: outputs/stages/stages.csv, outputs/tornado_final/{tornado,bars}.csv.

## 1. Stages: from the campaign to the final forecast (PGA 475, g)

| city | campaign | new catalog, campaign settings | + full-catalog rates, equal weights | final forecast | final vs campaign |
|---|---|---|---|---|---|
| Iquique | 1.201 | 1.097 (-8.7 %) | 1.013 (-7.6 %) | 1.163 (+14.8 %) | -3.2 % |
| Antofagasta | 1.390 | 1.298 (-6.6 %) | 1.153 (-11.2 %) | 1.380 (+19.7 %) | -0.7 % |
| Copiapo | 1.068 | 0.999 (-6.5 %) | 0.900 (-9.9 %) | 1.104 (+22.7 %) | +3.3 % |
| Valparaiso | 1.510 | 1.311 (-13.1 %) | 1.182 (-9.9 %) | 1.438 (+21.7 %) | -4.7 % |
| Santiago centro | 0.879 | 0.772 (-12.1 %) | 0.735 (-4.9 %) | 0.860 (+17.0 %) | -2.2 % |
| Santiago Penalolen | 0.810 | 0.706 (-12.8 %) | 0.688 (-2.5 %) | 0.796 (+15.7 %) | -1.7 % |
| Concepcion | 1.418 | 1.430 (+0.8 %) | 1.069 (-25.2 %) | 1.296 (+21.2 %) | -8.6 % |
| Pucon | 0.541 | 0.519 (-4.1 %) | 0.474 (-8.7 %) | 0.526 (+10.9 %) | -2.9 % |
| Puerto Montt | 0.627 | 0.627 (0.0 %) | 0.536 (-14.5 %) | 0.655 (+22.3 %) | +4.5 % |
| Puerto Aysen | 0.480 | 0.474 (-1.3 %) | 0.471 (-0.8 %) | 0.477 (+1.4 %) | -0.7 % |

Reading:
- Catalog: -7 to -13 % at the northern and central cities (in-slab events moved to the interface, deduplication), Concepcion and Puerto Montt unchanged.
- Full-catalog rates at the campaign's 5.6 floor and equal pattern weights: a further -3 to -15 %, and -25 % at Concepcion (the weights). At that floor the full-catalog b (about 1.0) under-predicts M >= 7.5.
- The fitting decisions (floors at the b plateau, recomputed tables, pooled in-slab b, tapered MFD, Z_TOP 10, crustal classes) raise it again by 11-23 %: b at the interface floors is 0.92 instead of 1.0, which restores the observed M7.5-8 rates.
- Net: the final forecast is within -9 to +5 % of the campaign at every city, with a different composition (interface-dominated, Concepcion down 9 %).

## 2. Tornado (range, % of the final reference, largest city)

| axis | range, where | signed effect | verdict |
|---|---|---|---|
| In-slab GMM | 32 % Iquique, Santiago | Montalva -15 to -18 %, Parker +10 to +17 % | branch (3, equal) |
| Interface GMM | 30 % Concepcion, Antofagasta | Kuehn +15 to +19 %, AG20 -10 % | branch (3, equal) |
| Crustal GMM | 23 % Aysen, 11 % Pucon | CB +12 %, CY -11 % at Aysen | branch (4, equal) |
| Interface geometry: segmented | 19 % Copiapo, 14 % Antofagasta | -3 to -19 % | branch (2, equal) |
| Interface (a, b) 16 / 84 | 18 % Puerto Montt, 13-15 % coast | -4 to -9 / +4 to +9 % | branch: 5 / ML / 95 with 0.185 / 0.63 / 0.185 |
| Interface rates from the declustered catalog | 18 % Puerto Montt, 11-16 % coast | +7 to +18 % | fixed (full catalog, Marzocchi and Taroni 2014); stated with this range |
| Interface segment Mmax +0.2 | 2-7 % on the segmented branch (the bar in bars.csv includes the segmentation effect; corrected against the segmented row: Iquique +5.5, Antofagasta +6.6, Copiapo +5.2, Concepcion +4.8, others <= 3 %) | +2 to +7 % on half the tree, <= 3.5 % on the mean | fixed, stated |
| In-slab pattern weights (window_T / magnitude step) | 7 % Concepcion, 6 % Puerto Montt | +7 % Concepcion, -1 to -4 % elsewhere | fixed (equal weights; retrospective test), stated |
| In-slab pattern from the full catalog | 5.5 % Penalolen | -2 to -5.5 % | fixed (declustered map), stated |
| Interface Z_TOP 5 km | 4.6 % Valparaiso | -2 to -5 % (so Z_TOP 10 raises PGA) | fixed at 10 km, stated |
| In-slab class domain cut | 2.7 % Iquique | -1 to -3 % | fixed (whole slab); closes D9 |
| Interface rate: geodetic (mid coupling) | 1.6 % | -1 to -2 % (full margin; catalog moment 98 % of geodetic) | branch as decided (it matters under segmentation, where geodetic doubles seg3 and seg4 rates; seg x geo not in the tornado) |
| In-slab separate b | 0.9 % | +-1 % | fixed (pooled b) |
| In-slab, crustal rates from the declustered catalog | <= 0.4 % | ~0 | fixed |

Not run: in-slab (a, b) and Mmax pad (dropped), fit floors, coupling lo / hi, crustal exclusions.

## 3. Final logic tree

| family | branch set | n | weights |
|---|---|---|---|
| interface | geometry: full margin, segmented | 2 | 0.5 / 0.5 |
| interface | rate: seismic, geodetic (coupling mid) | 2 | 0.5 / 0.5 |
| interface | (a, b): 5th percentile, maximum likelihood, 95th percentile of N(>=M8.8), same percentile in every segment; the geodetic branch keeps b and rescales the rate | 3 | 0.185 / 0.63 / 0.185 |
| interface | GMM: AG20, Parker, Kuehn | 3 | equal |
| in-slab | GMM: AG20, Parker SA_S, Montalva | 3 | equal |
| crustal | fault model (12 branches, from the fault conversation) x GMM: ASK14, BSSA14, CB14, CY14 | 12 x 4 | as defined / equal |

Realizations: interface 36, in-slab 3, crustal 48. Combination: exact mean in rate space; fractiles by Monte Carlo over family realizations.

Fixed and stated (with the ranges above): full-catalog rates; floors and tables; tapered MFD, corner 9.6; segment Mmax; Z_BOTTOM 50, Z_TOP 10; pooled in-slab b; in-slab Mmax observed + 0.2; equal pattern weights, declustered map, whole-slab domain; crustal classes, own b, exclusions; truncation 3.

## 4. Running the final model

```
FINAL=1 bash hazard/run_all.sh        # c_if_final, c_is_final, c_cr_final -> outputs/hazard/rock800_final/
python hazard/stages.py               # adds stage 5, the full-tree mean (PGA)
```

FINAL=1 switches hazard/config.py to PGA and SA(0.1, 0.2, 0.5, 1.0, 2.0), 475 and 2475 yr,
integration distance 500 km, point-source distance 100 km, and a separate output tree; the
building runs are untouched. The (a, b) 5 / 95 variants (c_ab_p05, c_ab_p95) are built on the fly.

## 5. Still open before the final run

- Patagonia interface source (geodetic, coupling 0.5, 50 km): not implemented; affects Puerto Aysen only (campaign interface share there 5 %).
- Segmented x geodetic interaction untested; the final tree carries it.
- GMM selection pending (equal weights).
- Fractile combination (Monte Carlo) and disaggregation at both return periods: code for the final-model step.
- Corner 9.6: confirm in Bird and Kagan (2004).
