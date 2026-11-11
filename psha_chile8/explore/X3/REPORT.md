# X3: GCCEL as the location benchmark

Task A2b, part 2. GCCEL (Bergman et al. 2023, version 20230722) is frozen as `catalog/sources/gccel_2026-11-11_*.csv` (801 events in the box, 12 clusters). This report compares every other source against it on shared events. Script: `x3_gccel.py` (reads the frozen GCCEL tables and the X1 cache, baseline variant). Tables are in `tables/`, figures in `figs/` (`figures_index.md`). Tests: `pytest explore/X3/tests` (4 pass).

GCCEL's own precision in the box: the median 90 % epicentral semi-major axis is about 2 km (σ ≈ 0.9 km), and the median depth bound is ±3 km. Against that, every catalogue's difference is mostly its own error.

## Summary

1. **775 of the 801 GCCEL events link to an X1 baseline event (97 %).** The X1 baseline windows were used (5 s / 50 km, ×1.5 at M 6, ×2 at M 7, ×3 at M 8, one-to-one).
   - None of the 26 unlinked events has any origin within 120 s and 450 km.
   - 22 are San Juan (Argentina) events: M 2.2–3.3, or no magnitude.
   - 3 are Tabuco events in March–April 2010 (M 3.7–4.1). No source in the box has an origin within 10 min of them; they are early Maule aftershocks that no catalogue kept.
   - 1 is a Valparaíso event of M 3.3.
   - All are below the 3.5 floor of the downloads or missed by every network. `tables/x3_link_counts.csv`, `tables/x3_unlinked.csv`
2. **How far the DECISIONS order (Potin → EHB L1/L2 → ISC → ComCat, GCCEL left out) puts us from GCCEL.** The epicentre is off by a mean of 8.9 km (median 6.3 km). The depth is off by a mean of 8.1 km (median 4.6 km). The error depends mostly on depth range and region. `tables/x3_variant_scores.csv`, `figs/x3_variant_scores.png`

   | GCCEL depth | events | mean epicentre distance | mean \|Δz\| (median) |
   |---|---|---|---|
   | < 30 km | 326 | 11.8 km | 10.7 km (6.5) |
   | 30–70 km | 435 | 6.8 km | 6.4 km (3.4) |
   | 70–120 km | 14 | 8.3 km | 3.7 km (2.7) |
   | > 120 km | 0 | — | — |

3. **Potin has the best epicentres in its network core and degrades at the edges.**
   - At 18–36° S (Iquique, Tocopilla, Illapel, La Serena, Maule, Tabuco, Valparaíso), Potin's median epicentre distance is 3–6 km and its depth spread is 2–4 km (1.4826 × MAD). Every other source is worse there (ISC prime, ComCat and EHB L1 at 4–12 km).
   - South of 36° S it degrades: Tomé 13 km and Tirúa 27 km epicentre, depth spread 9–18 km.
   - In the backarc it degrades too: San Juan 16 km epicentre, depth −8 ± 15 km.
   - On the same events, Potin is closer to GCCEL in epicentre than ISC prime (59 % of 540) and ComCat (61 % of 472). Against EHB L1 it is a draw (53 % of 111). `tables/x3_diff_summary.csv`, `tables/x3_paired.csv`
4. **Above 30 km, Potin depths are worse than ISC-EHB L1 and ISC on the same events.**
   - Mean |Δz| on shared events: Potin 13.9 vs EHB L1 4.9 km (26 events); Potin 11.6 vs ISC prime 7.4 km (173); Potin 9.2 vs ComCat 6.4 km (138).
   - At 30–70 km Potin is level with them (4.9 vs EHB L1 4.4; 6.2 vs ISC 6.2) and closer in 53–58 % of pairs.
   - The shallow problem comes from the edge clusters (Tirúa, Tabuco, San Juan, Tomé, Vallenar) and from Valparaíso (item 7). `figs/x3_diff_by_depth.png`
5. **X1 finding 6 (Potin too deep under the flat slab) cannot be tested with GCCEL.**
   - GCCEL selects events shallower than about 50 km. In the box it has 14 events at 70–95 km and none deeper than 95 km. The Potin artefact sits at 100–170 km.
   - At 70–95 km there are 8 pairs with both Potin and EHB L1/L2 depths. ISC-EHB is closer in 5 of them (3 of 5 in the flat slab).
   - On the 7 L1 events, mean |Δz| is EHB L1 2.8 km and Potin 4.7 km. That difference of 2 km on 7 events is not evidence either way.
   - Between 40 and 70 km in the flat slab, Potin and EHB L1 scatter alike (`figs/x3_potin_ehb_depth.png`).
   - **The decision on EHB before Potin below ~70 km rests on X1 alone.** `tables/x3_potin_vs_ehb_deep.csv`
6. **Changing the order of the location variants changes little.**
   - L-e (EHB L1/L2 before Potin when the chosen depth is ≥ 70 km) changes 22 events. Against L-e0 its mean |Δz| drops from 3.7 to 2.9 km at 70–120 km and from 8.12 to 7.99 km overall.
   - L-f (DECISIONS epicentre, depth from EHB L1 first) gives 7.73 km overall and 10.0 km above 30 km.
   - L-b (Potin only at 18–44° S and outside the backarc) gives 7.10 km for depth, by dropping Potin in San Juan. That is almost L-d's 7.07 km, without L-d's epicentre cost.
   - L-d (smallest σ) gives 7.07 km for depth but a worse epicentre (9.9 km).
   - Between all the variants, the epicentre spread is < 1 km and the depth spread is ≤ 1 km.
7. **Systematic offsets by cluster.**
   - **Tirúa (38–39° S):** ISC, ComCat and EHB L1 are 19–23 km east of GCCEL, a teleseismic bias. Potin is not shifted but scatters (median 27 km).
   - **Valparaíso (22–42 km):** every source is 8–14 km shallower than GCCEL, tightly (Potin −14.3 ± 3.4 km, ISC −14.4, ComCat −13.5, EHB L1 −7.8). Either the GCCEL depths there are deep or all catalogues are shallow. Worth checking the cluster's depth codes before using it as a depth reference.
   - **Vallenar:** ISC and ComCat are 10–13 km west. `tables/x3_cluster_shifts.csv`
8. **Other sources.**
   - GCMT centroids are 27 km from GCCEL (median), with depth +1.6 km. GCMT hypocentres (PDE) are 12 km off, with depth −1.2 km.
   - Centennial is 19 km off on 19 events.
   - ISC-GEM depth spread is 6.2 km, against EHB L1's 4.6 km. The two are on different event sets (196 and 170); X1 found ISC-GEM depths to be EHB copies where both exist.
   - CSN web, from 2020, is 8.5 km off with depth +4.5 km (33 events). CSN in ISC is 6.5 km off with depth spread 7.9 km.
   - EHB L3 depths are all fixed and were not scored.

## Linking

- **Method.** Every X1 origin within the scaled window counts. The window is scaled by the larger magnitude of the two origins. Cost = hypot(Δt / T, Δd / D), taken as the minimum over the event's origins. The Hungarian assignment gives one GCCEL event per baseline event.
- **Per cluster.** All events link in 10 clusters. San Juan links 57 of 79, Tabuco 38 of 41 and Valparaíso 66 of 67. `tables/x3_link_by_cluster.csv`
- **Why the 26 fail.** Small magnitude (below the ISC and ComCat download floor of 3.5; Potin and CSN web do not reach San Juan), and the Maule aftershock gap.

## Differences against GCCEL

`tables/x3_diff_summary.csv` has every source split by depth range (`zr`), cluster, 2° latitude band, flat slab (30–34° S) and period. Each row gives n, the median, the robust spread (1.4826 × MAD) and the 90th percentile of |Δ| for the epicentre distance (`dh_*`) and the depth difference, source − GCCEL (`dz_*`, measured depths only). `share_unmeasured` is the share of the source's depths that are fixed or on a default (X1 default table). `dz_all_*` includes those depths.

Overall (all depths):

| source | events | epicentre median / p90 (km) | Δz median ± spread (km) | measured share |
|---|---|---|---|---|
| Potin et al. | 606 | 5.5 / 17.9 | +0.1 ± 6.4 | 100 % |
| CSN in ISC | 693 | 6.5 / 20.8 | 0.0 ± 7.9 | 100 % |
| ISC prime | 746 | 7.9 / 19.7 | −1.4 ± 6.2 | 90 % |
| ISC-EHB L1 | 170 | 8.3 / 20.6 | −0.1 ± 4.6 | 90 % |
| ISC-EHB L2 | 135 | 8.5 / 19.1 | +1.8 ± 5.5 | 63 % |
| ISC-EHB L3 | 86 | 8.8 / 20.3 | all fixed | 0 % |
| ISC-GEM | 196 | 8.2 / 20.9 | 0.0 ± 6.2 | 98 % |
| ComCat | 688 | 8.8 / 25.0 | −1.3 ± 6.6 | 86 % |
| CSN web | 33 | 8.5 / 13.8 | +4.5 ± 5.2 | 97 % |
| GCMT hypocentre | 157 | 11.8 / 31.0 | −1.2 ± 7.1 | 92 % |
| GCMT centroid | 157 | 27.7 / 48.7 | +1.6 ± 9.5 | 91 % |
| Centennial | 19 | 19.0 / 29.4 | +0.8 ± 7.1 | 63 % |

Flat slab (30–34° S) against outside:
- Potin depth is −2.5 ± 9.5 km inside and +1.3 ± 5.3 km outside.
- EHB L1 is −0.1 ± 4.7 inside and −0.1 ± 4.4 outside.
- The wider Potin spread inside comes from Valparaíso (item 7), not from depth: these events are 22–42 km deep.

By period:
- Before 2000 every source is worse. ISC prime is 13 km off in 1976–1999 and 34 km in 1964–1975; Potin is 22 km off on 18 events in 1982–1999.
- From 2015, Potin is 4.9 km off with depth spread 3.7 km, ISC prime 7.2 km, ComCat 7.6 km.

## Depth-error model per source (input for A4)

`tables/x3_depth_error_model.csv`: per source and GCCEL depth range (< 30, 30–70, ≥ 70 km), the bias (median Δz), the spread (1.4826 × MAD) and the net σ. The net σ is the spread with GCCEL's ±3 km removed in quadrature, treating the bound as 1σ, which is conservative. The table also gives the horizontal σ (median Δh / 1.1774, Rayleigh) and the share unmeasured.

| source | < 30 km bias / σ_net | 30–70 km bias / σ_net | ≥ 70 km bias / σ_net (n) | σ_h 30–70 km |
|---|---|---|---|---|
| Potin et al. | −1.2 / 10.4 | +0.4 / 3.7 | −0.9 / ≈ 0 (14) | 4.0 |
| ISC-EHB L1 | −0.1 / 3.7 | −0.1 / 3.3 | −0.7 / ≈ 0 (7) | 6.3 |
| ISC-EHB L2 | +1.8 / 3.7 | +1.6 / 5.6 | (1) | 5.9 |
| ISC prime | −2.2 / 6.8 | −1.0 / 4.6 | −2.0 / ≈ 0 (14) | 5.7 |
| ComCat | −0.5 / 7.2 | −1.8 / 5.1 | −1.1 / 2.0 (14) | 5.5 |
| CSN in ISC | +0.4 / 11.0 | −0.1 / 6.0 | −0.5 / ≈ 0 (13) | 4.4 |
| ISC-GEM | +2.2 / 3.7 | −1.5 / 6.1 | −2.9 / ≈ 0 (4) | 5.0 |
| GCMT hypocentre | +0.6 / 5.0 | −3.0 / 6.0 | −2.9 / 1.6 (4) | 7.3 |
| GCMT centroid | +0.9 / 8.5 | +1.2 / 9.7 | +17.5 (3) | 24.6 |

- At ≥ 70 km the spreads are ≤ 3.6 km on ≤ 14 events, inside GCCEL's own ±3 km. GCCEL cannot resolve source errors there.
- The model holds for the GCCEL footprint only: 18.5–38.5° S, mostly coastal, 1990–2021. It says nothing below 95 km or south of 39° S.

## Potin and ISC-EHB at depth

`tables/x3_potin_vs_ehb_deep.csv` lists every event with both depths measured, for GCCEL depth ≥ 50 km and ≥ 70 km.

| GCCEL depth | region | pairs | EHB closer | Potin closer |
|---|---|---|---|---|
| ≥ 70 km | in flat slab | 5 (4 L1, 1 L2) | 3 | 2 |
| ≥ 70 km | outside | 3 (L1) | 2 | 1 |
| ≥ 50 km | in flat slab | 13 | 6 | 7 |
| ≥ 50 km | outside | 27 | 10 | 17 |

GCCEL has no cluster with events below 95 km, in or out of the flat slab. The test of X1 finding 6 (Potin 25–60 km too deep at 100–170 km, 29–34° S) is not possible with GCCEL; the decision rests on X1.

## Location variants

L-a to L-d are from X1 (baseline matching). New:
- **L-e0:** the DECISIONS order without GCCEL: Potin, CSN web, EHB L1, EHB L2, ISC, ComCat, then the X1 fallbacks.
- **L-e:** L-e0 with EHB L1/L2 before Potin where L-e0's depth is ≥ 70 km.
- **L-f:** L-e0 epicentre with the depth from EHB L1 first.

GCCEL is the reference, so it is left out of every order. Means over the 775 linked events (depth over 767 with a measured chosen depth and a constrained GCCEL depth):

| variant | mean epicentre distance | mean \|Δz\| all | < 30 km | 30–70 km | 70–120 km |
|---|---|---|---|---|---|
| L-a | 8.91 | 8.13 | 10.77 | 6.33 | 3.71 |
| L-b 44° S | 8.76 | 7.10 | 9.04 | 5.80 | 3.71 |
| L-c | 8.87 | 7.74 | 10.02 | 6.23 | 2.72 |
| L-d | 9.85 | 7.07 | 8.27 | 6.32 | 2.90 |
| L-e0 (DECISIONS order) | 8.91 | 8.12 | 10.73 | 6.35 | 3.71 |
| L-e (EHB below 70 km) | 8.87 | 7.99 | 10.44 | 6.35 | 2.94 |
| L-f (depth EHB L1 first) | 8.91 | 7.73 | 9.98 | 6.25 | 2.72 |

## Crustal and subduction events apart (added after Pablo's question)

The < 30 km result (summary item 4) mixes three kinds of event. `classes()` sorts each GCCEL event by its own hypocentre:
- crustal: more than 15 km above the Slab2 top, split into backarc and the rest;
- interface / slab: everything else, split by an offshore epicentre (depth not used for that split).

Tables `x3_diff_summary.csv` (`by = grp`), `x3_paired.csv` (`by = grp, depth`), `x3_variant_scores_by_group.csv` and `x3_slab_check.csv`.

| group | events | Potin epicentre median | Potin Δz median ± spread | ISC-EHB L1 Δz | ISC prime Δz |
|---|---|---|---|---|---|
| crustal onshore (forearc, arc, coast) | 57 | 3.3 km | −0.1 ± 4.9 | (2 events) | −1.6 ± 6.4 |
| crustal backarc (San Juan) | 29 | 15.5 km | −7.3 ± 18.8 | +0.6 ± 4.8 (4) | −7.0 ± 5.9 |
| interface / slab onshore or coast | 430 | 5.4 km | +1.0 ± 4.3 | −0.1 ± 4.2 | −0.6 ± 5.2 |
| offshore (interface / slab) | 90 | 7.0 km | −12.2 ± 7.8 | −1.4 ± 6.4 (26) | −5.1 ± 11.9 |

- **Crustal onshore:** Potin is the best source; its depth is not the problem. This is the setting GCCEL is designed for (near-source stations, depth codes n / l), so the benchmark is sound here.
- **Crustal backarc:** Potin is outside its network and poor (one event 141 km too deep); the global sources are better.
- **Interface and in-slab under the coast and inland:** Potin is level with ISC-EHB L1 in depth and better in epicentre. The remaining shallow onshore cases where EHB L1 beats Potin (13 events, 11.3 vs 4.3 km) are at Tirúa and Tabuco, the southern edge of the network.
- **Offshore:** every catalogue is shallower than GCCEL (Potin −12, ISC −5, ComCat −6 km), but GCCEL is not a dependable depth reference there. Its offshore depths are constrained by stations on one side only.
  - Against the Slab2 top, on 82 offshore events selected by epicentre alone, GCCEL is +5.5 ± 9.6 km, Potin −2.3 ± 7.7 and ISC −1.3 ± 11.0. On the 18 events that every source has, GCCEL is +0.3 ± 4.2 and Potin −7.7 ± 17.8.
  - Slab2 is built partly from the same global catalogues, so it does not arbitrate. Offshore depths are uncertain by ≈ 10 km in every source, and no order fixes that (mean |Δz| 10.7–12.3 km over all variants).
- **Region rule L-g** (Potin first only at 18–36° S or 18–37° S and outside the backarc, else the global sources first) gives mean |Δz| 6.85–6.89 km against 8.12 for the DECISIONS order. Epicentre: 8.40–8.57 against 8.91 km. The gain is almost all in the backarc (28.1 → 13.5 km); the onshore interface and crustal groups gain 0.1–0.3 km.

## What this suggests for the A4 location rule (options, not decisions)

- **(a) Keep the DECISIONS order (L-e0) for the epicentre.** Potin first is the best choice in its network core, and nothing else is better on average.
- **(b) Depth above 30 km:** EHB L1, then ISC, ahead of Potin. *Superseded by the split above:* the shallow problem is the backarc, the southern edge and offshore events, not crustal or interface events inside the network. Option (c) covers it better.
  - This is the largest gain available (mean |Δz| 10.7 → 10.0 km with EHB L1 first, L-f), but L1 is sparse.
  - Alternative: use the error model (σ by source and depth range) to pick the depth per event, a narrower L-d with σ from GCCEL rather than triple collocation.
- **(c, preferred after the split) Potin outside its network** (south of 36–37° S, and the backarc such as San Juan): treat its locations as a fallback, not first. This is close to X1's L-b; here it is among the best depth variants (7.10 km against L-d's 7.07 km).
- **(d) Below 70 km:** EHB before Potin (L-e) costs nothing and gains ≈ 0.8 km on 14 events. The case for it still rests on X1 finding 6, not on GCCEL.
- **(e) Cluster offsets** (Tirúa east shift of the global catalogues, Valparaíso depths): check them before quoting GCCEL as ground truth for depth there.
- **(f) For A4's σ per source,** use `tables/x3_depth_error_model.csv` at < 30 and 30–70 km. At ≥ 70 km keep the X1 values, since GCCEL is too sparse and too shallow there.

## Assumptions and limits

- GCCEL is a selection, not a catalogue: clusters around well-recorded sequences, mainly coastal, 18.5–38.5° S plus San Juan, 96 % from 2000. The scores describe that footprint only.
- "Measured" depth means not fixed and not on an X1 default bin (X1 `t2_default_depths.csv`, k = 5). EHB L3 depths are all fixed.
- The GCCEL depth bound (±3 km) is treated as 1σ for the net σ. If it is a 90 % bound, the net σ rises by ≤ 1 km.
- One GCCEL event (San Juan 2021-01-19, CT02, depth code i) has an uncalibrated depth; it is excluded from all depth statistics.
- ComCat does not carry GCCEL origins (no GCCEL catalogue or contributor, checked on the Illapel 2015 event page).
- **Version:** newer ScienceBase releases may exist but could not be checked (see `catalog/SOURCES.md`). A newer release with more clusters would mainly add events; it would not change the conclusion at depth, because GCCEL selects shallow events.
