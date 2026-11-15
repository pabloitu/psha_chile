# X1: exploratory analysis of A3–A5, with previews of B9 and A7

Run 2026-11-10 on the frozen tables `catalog/sources/*_2026-11-10_*` (nothing under `catalog/` changed). Scripts: `x1_io.py` (shared inputs), `x1_match.py`, `x1_loc.py`, `x1_mag.py`, `x1_stats.py`, `x1_dsz.py`, `x1_deep.py` (deeper pass), `x1_report.py` (figure index). Tables in `tables/` (`t1_…` to `t6_…`), figures in `figs/` (list in `figures_index.md`), resumable intermediates in `cache/` (git-ignored). Tests: `pytest explore/X1/tests` (8 pass).

Everything here is exploration. "X1 baseline" is a working reference, not a decision; the last block of each tier lists options for Pablo.

## Summary: the most important findings

1. **The ISC event ID links almost everything (tier 1).** ISC-EHB links to ISC by origin ID (100 %), ISC-GEM by event ID (99 %), CSN-in-ISC by construction. ComCat (97 %), GCMT (100 %), Centennial (99 %) and CSN web (19 %, ISC lags 2 years) link by an exact foreign origin inside the ISC Bulletin (NEIC, GCMT, CENT, GUC; |Δt| ≤ 1.5 s, ≤ 10 km). Only Potin has no link and must be matched by windows. `figs/t1_window_calibration.png`
2. **Same-event distances are period-dependent, not source-dependent (tier 1).** From 1964 the 99th percentiles of known pairs are 4–8 s and 25–80 km for every pair; before 1964 they are 30–150 s and 450–550 km (ISC vs ISC-GEM, Centennial vs ISC-GEM). Potin vs CSN-in-ISC: 2 s, 54 km. GCMT centroid vs its hypocentre: 14 s, 100 km. `figs/t1_window_p99_period_mag.png`
3. **Matching choices matter little once the backbone is in (tier 1).** Over 204 variants, M ≥ 4.5 events range 22 300–23 200 (±2 %); greedy and Hungarian assignment differ in 13 of 102 otherwise identical variants, by at most one event; the 25 km distance window is the one bad choice (5× more splits, Arauco 2011 missed). Anchor-first vs all-pairs clustering: 375 events (1.7 %). `figs/t1_grid_heatmap.png`, `figs/t1_events_per_year.png`
4. **Potin coda magnitudes before ~1990 are unusable (tier 1, tier 3).** Many 1982–1990 Potin `c` values are 0.2–1.0 for events ISC rates M 4 (Δt < 1 s): 3 300 of the 3 400 "magnitude disagreements" of the first diagnostic run. `tables/t3_check_potin_by_year.csv`
5. **Potin magnitudes are the CSN bulletin values, not a homogenized set (tier 3).** `l` = GUC ML (97 % identical), `c` = GUC MD / md (96–97 %), `W` = GUC MW (100 %) and GUC Mwr (97 %), `ww` = CSN Mww (98 %) / GUC Mwr (91 %), `B` ≈ mb (7 events). This settles question 5 of the note to S. Ruiz in practice. `tables/t3_check_potin_codes.csv`
6. **Potin puts intermediate-depth events under the Pampean flat slab 25–60 km too deep (tier 2).** At 30–34° S, Potin − ISC-EHB L1 is −3 to 0 km down to 90 km, then +27 km (119 events) at 100–120 km; the 31° S section shows a Potin cloud at 150–170 km below EHB and ComCat (~110 km, on the Slab2 top). Elsewhere Potin and EHB agree within 2 km down to 150 km; at 20–24° S below 190 km Potin is +17 km. Potin's paper flags raw-CSN artefacts at 150 km at 31.5° S; they survive the relocation. `figs/t2_sections.png`, `figs/t6_potin_flat_slab.png`
7. **Location priority moves few events between depth classes, except Potin's flat-slab cloud (tier 2).** L-b (Potin only inside 18–44° S and west of the backarc) moves 646 M ≥ 4.5 events (3 %), mostly "below slab" → "in slab" (707 → 268); L-c (EHB L1 first) 201; L-d (smallest σ) 1 817 (9 %). 12 % of M ≥ 4.5 events have no usable depth. `figs/t2_class_changes.png`
8. **The low end of every conversion is bent by censored GCMT pairs (tier 3, deeper pass).** GCMT has few events below Mw 4.7, so at native mb 4–4.5 only the events with high Mw have pairs. Exponential and quadratic fits then flatten (ISC mb exponential: slope 0.2–0.4 below mb 4.5, mb 4.0–4.5 all → Mw 4.74–4.88). The converted catalog heaps at Mw 4.7–4.9, maximum-curvature Mc is pinned at ~5.0 in every window and b(floor) spikes to 1.6–2.1 at floor 4.8. Linear forms (M2) give a flat b(floor) ≈ 1.05–1.2. Fitting only above the native value where GCMT is ≥ 80 % complete (M9) needs cuts at 5.4–6.2 (saturated range) and gives slopes 1.4–3.6 that are unusable when extended down. There is no uncensored GCMT reference below native ~5.5. `figs/t6_censoring_m9.png`, `figs/t4_b_vs_floor.png`
9. **W-phase Mw can extend the reference to ~4.8, with an offset (tier 3).** GCMT − USGS Mww: +0.10 (Mww < 5.0, n 119), +0.04 (5.0–5.4), 0.00 above, σ 0.06–0.08. GCMT runs high at small size, as Lolli et al. say. CSN Mww agrees with GCMT within 0.01–0.03 (σ 0.09) but has no pairs below 5.0; CSN Mwr and USGS Mwr scatter more (σ 0.11–0.14) and USGS Mwr runs 0.15–0.20 low below 5.4. `figs/t3_mww_vs_gcmt.png`
10. **ISC mb saturation on our pairs matches Lolli 2023 (tier 3).** mb − Mw: −0.11 at 5.5, −0.30 at 6.0, −0.50 at 6.5, −0.59 at 7.0, against −0.19 / −0.29 / −0.43 / −0.60 from L23. `figs/t3_checks.png`
11. **The conversion choice is the largest upstream factor for counts at 4.5 (tier 3).** M ≥ 4.5 events in 2010–2019: M0 13 460; OLS (M1) 19 481 (+45 %); linear only (M2) 6 198 (−54 %); published relations (M4) 9 360 (−30 %); weighted mean (M5) 12 132; Mww below 5.4 as reference (M6) 13 891; Cabello's own values (M7) 8 010. N(≥ 6) per decade moves by ≤ 10 % except M7. `figs/t3_fmd_variants.png`, `tables/t3_variant_counts_decade.csv`
12. **b depends on the fit floor far more than on matching, location or weights (tier 4).** One-at-a-time from the reference (floor 5.0): fit floor ±0.3 moves b by −0.40 to +0.30; the magnitude variant by −0.37 to +0.21; declustering by −0.09 (crustal) to −0.28 (interface); Tinti–Mulargia weights +0.01 to +0.02 (N(≥ 6) × 0.84–0.90); location ≤ 0.01; matching ≤ 0.02. Above floor 5.3 all variants converge to b ≈ 0.95–1.05 (full catalog). `figs/t4_tornado.png`
13. **At floor 5.0 the fits under-predict the large events by about 2× (tier 4).** Interface band, M0, full catalog: 21 fitted against 48 observed M ≥ 7 since 1904, and 1.3 against 8 M ≥ 8. Declustered: 26 and 3.1. This is the b inflated by finding 8, plus completeness tables pinned at Mc ≈ 5. b-positive gives 0.91 (interface) and 1.13 (in-slab) at 5.0. `figs/t4_large_events.png`
14. **Two-plane detections exist in Potin at 20–23.5° S and 80–120 km, separation 8–13 km (tier 5).** There are more at 40–80 km (separation 15–24 km) all along 20–37° S, but most disappear once cells with a slab top < 50 km are excluded. They are interface vs in-slab, not a double seismic zone. ISC-EHB is too sparse to test (≤ 1 band). The 120–200 km "planes" at 31–32.5° S are the Potin depth artefact of finding 6. `figs/t5_two_plane_strip.png`, `figs/t6_two_plane_exclusions.png`
15. **Data surprises for A6.** ISC-GEM gives the 1960-05-22 18:56 Valdivia foreshock Mw 8.72 (ISC MS 8.56) against P&S Mw 7.9 and RM18 Ms 7.8, and lists a separate event 36 s before the mainshock without Mw. ISC MS drifts against GCMT: Mw − MS is 0.34 (1976–1999), 0.45 (2000–2013), 0.57 (2014 on). `tables/t3_check_neic_ms.csv`

## Tier 1: A3 matching

**Tried.**
- One origin table of all nine sources: 387 471 preferred origins (GCMT by its reference hypocentre).
- ID backbone and exact foreign-origin links.
- Windows calibrated on 276 202 known same-event pairs.
- A grid of 4 time × 4 distance windows × 3 scalings × 2 assignments × 2 orders (192), plus 12 calibrated-window variants.
- Hot spots: Maule, Illapel, Iquique, Arauco 2011.
- RM18 matching and the baseline choice.
- Candidate pairs were built once at the widest window (120 s, 450 km; 346 702 pairs), so each variant takes ~0.5 s.

**Backbone** (`tables/t1_backbone_*.csv`).
- Linked shares: ISC-EHB, ISC-GEM, CSN-in-ISC, GCMT, Centennial ≥ 98 %; ComCat 96–100 %; ISC prime 41–44 % before 1976 and 85–90 % after; Potin 0 %; CSN web 19 %.
- ComCat carries ISC-GEM IDs for 551 events (`iscgem…`, `iscgemsup…`); no other foreign IDs.
- Foreign origins inside the ISC Bulletin are the more useful link: NEIC / USCGS / NEIS for ComCat (42 552), GCMT for GCMT (2 796), CENT for Centennial (659), GUC for CSN web (10 553).
- 693 links disagree by > 30 s or > 100 km, mostly CSN-in-ISC vs ISC prime (350), ISC-GEM vs ISC (128, almost all before 1964), ComCat vs ISC (185).
- The largest disagreements are old great events: 1914 M8.2 at 232 km, 1906 at 255 km, 1922 Atacama at 114 km.

**Windows** (`tables/t1_window_percentiles.csv`, `tables/t1_calibrated_windows.csv`).
- Medians are 0.2–1 s and 3–10 km for almost all pairs.
- 99th percentiles from 1964: 4–8 s, 25–80 km (Potin–CSN-in-ISC 1.9 s / 54 km; CSN web–Potin 1.9 s / 27 km; ComCat–GCMT 4.1 s / 35 km).
- Before 1964: 30–150 s and 450–550 km.
- The p99 distance does not grow with magnitude band in a consistent way; it grows with age.
- Calibrated windows per pair: p99, floors 5 s / 25 km. Pairs without data get a quadrature sum through the best shared hub (Potin–ISC through CSN-in-ISC).

**Grid** (`tables/t1_grid.csv`, `tables/t1_links_per_pair.csv`).
- Final events 204 667–207 650; M ≥ 4.5 (any native M) 22 329–23 194.
- Split diagnostics (different events within 10 s / 50 km, one M ≥ 5): 43–171, but 395 on average with the 25 km window.
- False-merge diagnostics (linked across ID groups with Δt or Δd above the pair p99, or |ΔM| > 1 without Potin): 155–750. They rise with the windows.
- Ambiguous origins (≥ 2 candidates): 146 at 5 s / 25 km, 2 651 at 40 s / 150 km with scaling.
- Scaling changes ≤ 10 splits.
- Hungarian and greedy differ in 13 of 102 otherwise identical variants, by at most one event.
- Anchor-first gives 3× more splits than clustering (226 vs 73 on average) but fewer merges (382 vs 460).

**Hot spots** (`figs/t1_hotspot_maps.png`, hot columns in `t1_grid.csv`).
- Every variant with ≥ 50 km keeps Maule, Illapel and Iquique mainshocks as one event (6–7 sources).
- Arauco 2011 (CSN–GCMT 6 s, 59 km) is merged by 92 % of the anchor variants and all clustering variants with ≥ 100 km, by 67 % at 50 km, never at 25 km.
- 134 of 204 variants get all four right.

**RM18** (`tables/t1_rm18_matches.csv`, `tables/t1_rm18_side_by_side.csv`, `figs/t1_rm18_table.png`).
- 47 events matched to a catalog event; 12 more (pre-1904, plus Copiapó 1859) only to Cabello rows; 10 unmatched. The rule: one-to-one, ±1 day, latitude within 2°, magnitude closest to the RM18 Mw, ≥ 5.5.
- Concepción 1960, the Valdivia foreshock, Maule outer rise and Pichilemu b each get their own event (a "largest in the window" rule put them on the mainshock).
- Mejillones 1994: the table date gives an M 4.7 event; the swapped date 1994-12-10 gives Mw 6.0. Use the swapped date.
- Review list (year or month only): Tarapacá 1543, Valdivia 1575, Arica 1604, Arica 1615, Pica 1768, Taltal 1887, Santiago 1945, Aysén 1960 slow event, Copiapó swarms 1973 and 2006.

**Baseline.**
- X1 baseline: **5 s / 50 km, ×1.5 at M 6, ×2 at M 7, ×3 at M 8, Hungarian, anchor-first**: 206 633 events, 121 splits, 202 false merges, all four hot spots right. It has the lowest diagnostic sum among the 134 variants that get the hot spots right.
- Neighbours: the same windows with all-pairs clustering (`nb_order`: 205 308 events, 50 splits, 285 merges) and the best calibrated-window variant (`nb_calibrated`, anchor-first: 205 897).
- In the baseline, 88 of the 121 splits are Potin vs ISC-EHB (52) and CSN web vs ISC (36), all after 2000 (`tables/t1_baseline_splits.csv`). 5 s is too tight for those pairs, not too loose.
- 194 M ≥ 6 window merges, almost all of them the normal 6–8-source events (`tables/t1_baseline_m6_window_merges.csv`).

**Surprises.**
- Potin's 1980s coda magnitudes (finding 4).
- The backbone does most of the work, so the window grid is a second-order choice.
- The magnitude criterion of the false-merge diagnostic only works without Potin.

**What this suggests for A3 (options).**
- (a) Keep the ID + foreign-origin backbone as step one: it is exact, and it removes the window question for ~85 % of origins.
- (b) Windows: 5–10 s and 50 km, or the calibrated per-pair windows. The difference is ±0.5 % of M ≥ 4.5 events. Avoid 25 km.
- (c) Before 1964, rely on IDs only, or use windows of ≥ 60 s / 300 km: the p99s are an order of magnitude larger.
- (d) Order: anchor-first (fewer merges, more Potin–EHB splits) or clustering (fewer splits). A combination is anchor-first, then a final clustering pass on the residual splits.
- (e) Assignment: either; Hungarian costs nothing extra.
- (f) RM18: as done, with Mejillones on 1994-12-10.

## Tier 2: A4 location and depth

**Tried.**
- Automatic default-depth detection for every source / agency with ≥ 300 origins, for k = 3 / 5 / 10, over the whole record and per period.
- Pairwise epicentre and depth differences on baseline events, by 2° band, setting, period and magnitude band, with ISC-EHB L1 as reference.
- Triple collocation of free depths.
- Location variants L-a, L-b (44° S and 46° S; west of the backarc, or west of 68° W), L-c and L-d, each turned into a depth proxy class against Slab2.

**Default depths** (`tables/t2_default_depths.csv`, k = 5, share of the agency's origins).
- ISC 35 km (6 %), plus cell depths 181 / 200 / 150 / 250 km. NEIC 10 (8 %) and 33 (7 %). USCGS 33 (13 %). NEIS 33 (16 %). IDC 0 (38 %). EIDC 0 (26 %). GFZ 10 (16 %). VAO 10 (22 %). MOS 33 (41 %). LDG 10 (42 %). CGS 100 / 60 / 150 / 200. ISS 0 / 96 / 128 / 160. SJA 10 / 40. BJI 33 / 35 / 10.
- ComCat us 10 (10 %), 33 (9 %), 35 (5 %), 5 (1 %). ComCat iscgem 15 / 35 / 25 / 20 / 10. GUC (via ComCat) 150 km (1.1 %), the alignment Potin et al. describe.
- ISC-EHB L3 15 (29 %), 20, 10, 25, 35 (the 10 km fix steps). ISC-EHB as an ISC agency 15 (7.5 %) and 10.
- ISC-GEM 15 (10 %) and 10; ISC-GEM supplement 15 / 35 / 25.
- GCMT centroid 12 (4.8 %, the floor) and 10; PDE hypocentres 33 (21 %).
- Centennial (EHB) 35 (6.9 %). CSN web 10 (1.4 %). Potin none.
- All LEARNINGS defaults are confirmed, plus new ones: ISC cell depths, ISS, CGS, MOS, IDC 0 km.
- 20 703 origins sit on a default bin of their agency and are treated as unknown depth.

**Agreement** (`tables/t2_location_agreement.csv`, `figs/t2_dz_vs_lat.png`, `figs/t2_potin_vs_ehb_maps.png`).

| pair | events | median epicentre Δ | depth Δ (median) | depth MAD |
|---|---|---|---|---|
| Potin vs EHB L1 | 1 530 | 13 km | 0.1 km | 7.4 km |
| Potin vs ISC | 44 060 | 7 km | — | 9.8 km |
| EHB L1 vs ISC | — | 8 km | −0.6 km | 3.2 km |
| EHB L1 vs ComCat | — | 10 km | −1.4 km | 5.2 km |
| EHB L1 vs GCMT centroid | — | 29 km | −12 km (centroid deeper) | 12 km |
| ISC-GEM vs EHB L1 | 1 759 | — | 0.0 km | 0.0 km |
| CSN web vs Potin | 3 464 | 3.7 km | +4.9 km | — |

- ISC-GEM depths are EHB copies.
- The GCMT centroid depth offset is +10 to +20 km north of 25° S.

**Depth σ.** Triple collocation (`tables/t2_depth_triple_collocation.csv`) gives Potin 7.5–8.7 km, ComCat 3–7 km, GCMT centroid 10.5–13 km and CSN web 6–11 km. EHB L1 and ISC collapse to the 0.5 km floor because their errors are correlated (ISC prime often is the EHB solution), so those σ are not usable.

**Variants** (`tables/t2_proxy_class_counts.csv`, `tables/t2_proxy_class_changes.csv`, `tables/t2_transition_*.csv`).
- M ≥ 4.5 under L-a: 9 287 in slab, 5 557 interface band, 1 161 above-slab shallow, 707 below slab, 437 above slab deep, 655 outside Slab2, 2 413 unknown depth (12 %).
- Changes against L-a: L-b 565–646 (54 at M ≥ 5.5), L-c 201 (46), L-d 1 817 (184).
- The 44° S / 46° S and arc / 68° W versions of L-b differ by < 80 events.
- Changes are concentrated at 30–34° S (Potin's flat-slab cloud) and in the north below 190 km.

**Unknown depths** (`tables/t2_unknown_depths.csv`): mostly before 1976 and in the ISC-only small events. L-b raises the unknown share slightly (11.9 → 12.7 %), since ISC fallbacks carry more defaults.

**Sections** (`figs/t2_sections.png`):
- At 20°, 23° and 33.5° S, Potin, EHB and ComCat sit on the same slab.
- At 31° S, Potin is 40–60 km below the others at 250–400 km from the trench.
- At 27° S and 37° S, everything is sparse below 100 km.
- Crustal seismicity at 33.5° S 250 km from the trench (Andes) is shallow in all catalogs.

**Surprises.**
- The Potin flat-slab artefact (finding 6).
- The GCMT centroid depth is systematically deeper.
- ISC-GEM depths are not independent of EHB.

**What this suggests for A4 (options).**
- (a) Potin first, except at 29–34° S below ~90 km, where EHB L1/L2 or ISC is preferable. This is a narrower L-b.
- (b) Plain L-a (Potin everywhere), with the flat-slab cloud flagged in A7.
- (c) L-c (EHB L1 first). It changes little because L1 is sparse (1 530 events shared with Potin).
- (d) Treat the detected defaults (k = 5, full table) as unknown depth for every source, including ComCat 10 / 33 / 35 and EHB L3.
- L-d is not recommended: its σ come from too few independent triples.

## Tier 3: A5 magnitudes

**Tried.**
- Inventory of 292 scale names (`tables/t3_inventory.csv`, `figs/t3_type_year_raster.png`).
- Pairs against GCMT, CSN Mww and USGS Mww, raw and offset-corrected (offsets 0.01 / 0.03; `tables/t3_pairs.csv`).
- Triple collocation on all 531 triples among the 24 most-used scales.
- For every scale with ≥ 30 pairs, 4 methods × 3 forms × 4 splits, with bootstrap CIs on the baseline (`tables/t3_fits.csv`, best per method in `tables/t3_best_form_split.csv`). The same fits were repeated on the two neighbour matchings (`tables/t3_fits_by_matching.csv`).
- Published relations evaluated on our pairs (`tables/t3_published_bias.csv`).
- Specific checks (`tables/t3_check_*.csv`, `figs/t3_checks.png`).
- Variants M0–M8 for all three matchings (M6 baseline only), plus M9 in the deeper pass.

**Pairs.**
- Against GCMT: ISC mb 2 711, NEIC mb 2 646, MOS mb 1 729, ISC MS 1 522, GUC ML 1 469, BJI mB 1 248, SJA ML 844, SJA MW 812, NEIC Mww 809, GUC Mwr 351, CSN Mww 134, GUC MD 67.
- About 45 % of the pairs are deeper than 50 km.
- The neighbour matchings change pair counts by < 1 % and Mw(4.5 / 5 / 6) of the preferred fits by ≤ 0.02.

**Reference below 5.4** (`tables/t3_mww_vs_gcmt_bands.csv`). Finding 9.
- USGS Mww can extend the reference down to ~4.8 with σ ≈ 0.08, but it sits 0.04–0.10 below GCMT there.
- CSN Mww has only 33 pairs below 5.4, so it cannot.
- GCMT Mw < 5.4 does look high against W-phase, by 0.04–0.10.

**Errors.**
- Triple-collocation σ (`tables/t3_sigma_per_scale.csv`, `figs/t3_tc_sigma.png`): GCMT 0.12, ISC-GEM 0.13, NEIC mb 0.14, ISC mb 0.16, GUC MD 0.16, MOS mb 0.16, BJI mB 0.20, SJA MW 0.22, GUC ML 0.22, SJA ML 0.23, ISC MS 0.24.
- Four scales hit the 0.05 floor because their triples are few and correlated (CSN web Ml, GUC md, Potin c, SAN md); treat those as unknown (0.25 used where missing).
- The GCMT value is inflated by the non-linearity between scales; a priori GCMT σ is ~0.07.
- η = σ²(GCMT) / σ²(native) is therefore 0.25–0.6 for mb and 0.3 for ML.
- Equation errors from the Gasperini correction: ISC mb 0.11–0.16, NEIC mb 0.13–0.17, GUC ML 0.06–0.15, GUC MD 0.22, ISC MS 0.

**Fits.**
- BIC prefers curvilinear forms where there are many pairs: ISC mb exponential (ΔBIC −708 against linear), NEIC mb exponential (−609), ISC MS quadratic (−383), NEIC MS quadratic (−64), NEIC Ms_20 exponential.
- GUC ML: linear with a depth split. GUC MD / md: linear.
- Period splits are preferred for SJA and, under some methods, for ISC / NEIC mb.
- OLS slopes are 0.15–0.3 lower than chi-square slopes (ISC mb linear: 0.97 vs 1.14–1.25), as expected.
- Bootstrap CIs at native 4.5 are ±0.03–0.07 for the large scales.
- Exponential fits failed to converge for GUC ML and GUC MD (infinite σ). They are now rejected by a validity check: σ finite and the slope positive over the data range.
- Residuals in time (`figs/t3_residuals_time.png`) are flat except for ISC MS (drift, finding 15) and SJA (step around 2015).

**Published relations** (bias = GCMT − relation on our pairs at native 4.5 / 5 / 5.5 / 6).
- ISC mb: L23 exp +0.25 / −0.02 / −0.18 / −0.18; DG15 exp −0.03 / −0.11 / −0.09 / +0.02 (best).
- NEIC mb: L23 exp +0.32 / +0.03 / −0.14 / −0.13; S06 +0.04 / −0.16 / −0.20 / +0.04. Cabello's file relation (1.03 mb + 0.28) is −0.05 / −0.32 / −0.43 / −0.29: too high by 0.3–0.4, as LEARNINGS says.
- ISC MS: L23 and DG15 within 0.05 everywhere.
- GUC ML: P19 +0.21 / −0.11 / −0.24 / −0.18; C25 (≤ 50 km) +0.19 / −0.08 / −0.18 / −0.06.
- The positive bias at 4.5 for every relation is partly the censoring of finding 8.

**Specific checks.**
- Potin codes: finding 5. ML ≈ Mc − 0.25: GUC ML − GUC MD has median −0.30 (2000–2002) and −0.40 (2003–2010), but the relation is not an offset: a chi-square slope of 2.5–3.5 is driven by MD heaping (`t3_check_coda_ml.csv`).
- CSN web Ml is identical to GUC ML (median 0.00, sd 0.04).
- **Mlv vs Ml:** against NEIC mb, Ml is −0.30 (2020–2024), −0.20 (2025), −0.30 (2026, n 55); Mlv is −0.20 (2026, n 234). Against GFZ, Mlv is ~0.1–0.15 higher than Ml. Tentatively Mlv ≈ Ml + 0.1; keep them as two types.
- ISC mb saturation: finding 10.
- NEIC Ms: Mw − Ms is 0.31 (1976–1999), 0.34 (2000–2013), 0.30 for Ms_20 from 2014. There is no detectable change in 2013 on these pairs (n 107–262, shallow only).
- Heaping (`t3_check_heaping_decimals.csv`): GUC MD and Potin c heap on even decimals. Dithering removes the converted-value heaping of GUC ML (slope 0.86).
- ISC-EHB carries no Mw in 1985–1998 (0 of 69–255 events a year). GCMT covers 21–56 events a year there and is matched on all of them.

**Variants** (`tables/t3_variant_delta.csv`, `tables/t3_variant_counts_decade.csv`, `tables/t3_variant_sources.csv`, `figs/t3_dmw_variants.png`, `figs/t3_fmd_variants.png`).
- M0 takes ISC mb for 22 832 events, GUC ML 19 642, GUC MD 7 085, SJA MW 6 825, NEIC mb 6 728, GUC md 6 421, GCMT 2 770, ISC-GEM 714 (before 1976) and RM18 for 48.
- Median Δ against M0 (2000–2014): M1 +0.09, M2 0 (mean −0.14), M4 0 (sd 0.37), M5 0, M6 −0.03, M7 −0.17.
- Events crossing 4.5 against M0 (2000–2014): M1 7 603, M2 7 291, M4 5 123, M5 1 823, M3 1 168.
- M8 changes 0 events after 1976 and few before.
- Count changes: finding 11.
- **First build failed and was fixed.**
  - Quadratic fits extrapolated outside the data range (GUC ML quadratic: ML 2 → Mw 8), and Potin magnitudes had been used as proxies, giving 61 000 "M ≥ 4.5" events in the 2010s.
  - Conversions now continue linearly outside the fitted range: slope 1 below, the end slope (1–2) above. σ grows by 0.1 per unit beyond the range.
  - Potin is excluded as a proxy (DECISIONS).
  - 809 events with a native M ≥ 4.5 have no Mw: Potin-only (277), and ISC-only events whose scale has no fit (mostly before 1964).

**Surprises.**
- Censoring at the low end (finding 8).
- Potin = CSN bulletin.
- ISC MS drifts against GCMT.
- The equation error of ISC MS is 0 (TC σ 0.24 already explains the scatter).

**What this suggests for A5 (options).**
- (a) The chi-square method with η from triple collocation is fine, but the exponential / quadratic preference by BIC is a high-M effect. At 4.5–5 these forms are censored extrapolations. Options:
  - linear forms (M2, flat b(floor));
  - exponential only above native ~5;
  - a joint fit with USGS Mww as the reference below 5.4 (M6), shifted by +0.04 to +0.10 to the GCMT scale or not (the scale choice is open: W-phase or GCMT).
- (b) Depth splits are preferred for GUC ML only; period splits for SJA. DECISIONS' "only where the data show a difference" leaves few splits.
- (c) Hierarchy (M0) vs weighted mean (M5): ≤ 0.05 median difference, 1 800 crossings at 4.5. Either works.
- (d) Potin magnitudes add nothing: they are the CSN values already in the ISC Bulletin.
- (e) Before 1976, M8 vs M0 matters for ≤ 3 M ≥ 6 events per decade.
- (f) Check every converted Mw against the censoring diagnostic (share of events with a GCMT pair per native bin, `figs/t6_censoring_m9.png`).

## Tier 4: preview of B9

**Tried.**
- Families from the tier-2 proxy classes, L-a and L-b 44° S: crustal shallow, interface band, in slab, in slab < 70 / ≥ 70 km.
- 3 matchings × M0–M8 (M6 baseline only) × 2 locations = 50 combinations, full and Gardner–Knopoff declustered.
- Mc by maximum curvature + 0.2, b-stability and Clauset KS in five windows; completeness tables with steps ≥ 0.3.
- Weichert b and rate with and without Tinti–Mulargia weights (w = exp(−(β σ)² / 2), two iterations), floors 4.5–6.0; b-positive (δ 0.2).
- 104 000 fits in 100 s (`cache/stats_fits.csv.gz`; tables `t4_*`).

**Results.**
- Mc (`tables/t4_mc_windows.csv`): maximum curvature gives 5.0 in every window from 1976. That is the heaping of finding 8, not network completeness. b-stability and KS give 4.6–5.6.
- b(floor) (`figs/t4_b_vs_floor.png`): spikes at 4.7–5.0 for M0 / M1, flat for M2 / M4. All variants converge to 0.95–1.05 above 5.3 (full catalog); declustered interface 0.75–0.85.
- Tornado: finding 12 (`tables/t4_tornado.csv`).
- Large events: finding 13 (`tables/t4_large_fit_vs_obs.csv`).
- b-positive: 0.91 (interface) / 1.13 (in slab) / 0.97 (crustal) at 5.0, and 0.82 / 0.95 / 0.89 at 5.5. It is less sensitive to the conversion at 5.0–5.5 but swings below 5 (`tables/t4_bpositive.csv`).

**Surprises.** The completeness tables are set by conversion artefacts rather than by the network. Matching and location barely move b (< 0.02).

**What this suggests (options for A5 and B9).**
- (a) Settle the low-end conversion before B9. It controls Mc, b at floors < 5.3 and N(≥ 4.5).
- (b) Use b-stability or KS rather than maximum curvature on a converted catalog.
- (c) Fit floors ≥ 5.3 are robust to every upstream choice tested; floors below need (a).
- (d) TM weights lower N(≥ 6) by 10–16 % and b by < 0.02.

## Tier 5: preview of A7

**Tried.**
- Datasets: Potin (all events, and M ≥ 3), ISC-EHB L1 and L1+L2, and the full baseline catalog under L-a and L-b.
- 1° bands at 18–40° S in three depth ranges, using the slab-normal (and vertical) distance below the Slab2 top within −15 to 60 km.
- A one- against two-component Gaussian mixture. "Two planes" needs ΔBIC > 10, both weights ≥ 0.15, a separation ≥ 8 km and larger than either σ.
- The Slab2 top shifted ±5 km, because no uncertainty grid is on disk.
- Deeper pass: exclude cells with a slab top < 50 km, or events within 10 km of the top.

**Results** (`tables/t5_two_plane_tests.csv`, `tables/t6_two_plane_exclusions.csv`).
- 80–120 km: two planes at 20.5–23.5° S in Potin (separation 8–13 km) and at 18.5° S (12 km).
- 40–80 km: two planes at 20–23° S (20–22 km, as Sippl et al.) and at 29–37° S (12–24 km). Excluding cells with a slab top < 50 km removes all of them south of 29° S except 28.5° S and 25.5° S. Excluding events within 10 km of the top keeps most, so there is a second population ~20 km below the top. It is not separable from interface-depth events with catalogue depths.
- 120–200 km: "two planes" at 22.5–24.5° S (16–25 km) and 31–32.5° S (15–16 km, the Potin artefact).
- L-a and L-b give the same pattern except 30.5° S 80–120 km (L-b only).
- Vertical and normal distance agree; the ±5 km shift changes nothing (a constant shift cannot change bimodality).
- `figs/t5_dslab_histograms.png`, `figs/t5_sections_dslab.png`

**What this suggests for A7 (options).**
- (a) A lower plane at 80–120 km is supported at 20–24° S only, with ~10 km separation. That is less than the 20 km in the literature, and at the limit of Potin's depth σ (~8 km).
- (b) At 40–80 km the test cannot separate a double zone from interface events. A7 needs mechanisms or a local catalogue there.
- (c) Do not use Potin depths at 29–34° S below 90 km for plane detection.
- (d) South of 33° S no evidence beyond the interface / slab split.

## Assumptions

- **Origins and links.** GCMT is matched by its reference hypocentre; the centroid is a location source only. Exact foreign-origin links (≤ 1.5 s, ≤ 10 km to an ISC-Bulletin origin of the corresponding agency) count as part of the backbone. IDC / EIDC mb are left out of the magnitude proxies used for matching diagnostics (they run high). Non-earthquake event types are kept in matching (filter in A3).
- **Matching rules.** The event representative for anchor-first matching is the member with the best location priority (Potin, EHB, ISC-GEM, Centennial, CSN, ISC, ComCat, CSN-in-ISC, GCMT). Window scaling uses the larger native maximum of the two origins. Calibrated windows are p99 with floors 5 s / 25 km and caps 120 s / 450 km; uncalibrated pairs use a quadrature sum through a hub.
- **Diagnostics.** The false-merge diagnostic compares member and representative only, and only across ID groups. Its |ΔM| > 1 test uses the median native magnitude and excludes Potin.
- **Baseline choice.** The baseline rule adds a hot-spot requirement to "fewest diagnostics", because the plain rule picks 5 s / 25 km, which misses Arauco 2011.
- **RM18.** One-to-one, magnitude ≥ 5.5, closest Mw; Copiapó 1959 read as 1859.
- **Settings.** Offshore / coast / forearc / arc / backarc come from the Natural Earth 10 m coastline (coast = within 20 km), `data/intraarc.shp` and the Nazca trench. Santiago-area events fall in "arc".
- **Depth choice.** Within a location variant the epicentre comes from the first source in the order, and the depth from the first source with a free depth.
- **Proxy classes.** Slab thickness defaults to 40 km where missing.
- **Fallback order.** EHB L1, L2, ISC-GEM, Centennial, ISC, ComCat, CSN-in-ISC, EHB L3, GCMT.
- **Reference Mw.** CSN Mww = GUC Mww in ISC ∪ CSN web Mww; USGS Mww = NEIC Mww (ISC) ∪ ComCat us mww; both shifted by their median offset to GCMT.
- **Magnitude errors.** Scales without a triple-collocation σ use 0.25; GCMT σ comes from triple collocation (0.12).
- **Splits and hierarchy.** Unknown depths go to the ≤ 50 km group in depth splits. RM18 Mw is taken first in all periods (PREFERENCES "large events"), not only before 1976.
- **Old magnitudes.** Centennial conversion: Mw types direct, Ms with DG15, UK as Ms − 0.2, mB as Mw.
- **M7.** Cabello's value is the nearest Cabello row within 10 s / 50 km of any member origin.
- **Tier 4.** Families exclude unknown depths. The declustering catalog is Mw ≥ 3.5, Gardner–Knopoff aftershock windows only. Weichert runs to 2026.86. The large-event check counts from 1904.
- **Tier 5.** The thresholds of the two-plane rule are my choice (listed in tier 5).

## Failures and skips

- `geopandas.read_file` fails in psha_renta: pyogrio finds an incomplete GDAL data directory. Shapefiles are read with cartopy's reader instead. Worth fixing in the environment.
- No Slab2 uncertainty grid in `data/slab_2.0/` (depth, dip, strike, thickness only). The tier-5 sensitivity used ±5 km shifts instead; this is uninformative for bimodality.
- The first M0–M8 build was invalid (extrapolated quadratics, Potin proxies); it was fixed and rerun (tier 3).
- Exponential fits of GUC ML and GUC MD did not converge (infinite σ); they are rejected by the validity check.
- M9 (fits above the GCMT censoring cut) ran but is not usable (finding 8). It is kept in `mw_variants.csv.gz` as a diagnostic only.
- Triple-collocation σ for CSN web Ml, GUC md, Potin c and SAN md are at the 0.05 clip (unreliable). Depth triple collocation is unusable for correlated EHB / ISC / ISC-GEM depths.
- CSN web Ml has only 9 GCMT pairs (it starts in 2020), so it gets no own fit. Events after 2020 with only a CSN web Ml and no GUC ML in ISC (ISC lags ~2 years) get no Mw (about 20 of them M ≥ 4.5).
- Tier 4 ran every listed combination; nothing was dropped for time. Only M6 is missing for the two neighbour matchings.
- Not done: the per-region σ for L-d from triple collocation (too few independent triples; L-d used the spread against EHB L1 per band); equation-error variants with σ > 0.1 assumed; bootstrap CIs for the neighbour matchings (point fits only).

## Run times and output sizes

| step | run time |
|---|---|
| Tier 1 (origins, backbone, candidates, 204-variant grid on 14 processes, figures) | ≈ 1 min after caching |
| Tier 2 | 3.3 min |
| Tier 3 (fits with bootstrap, first run) | 11 min |
| Tier 3 (rerun on cached fits) | 1.6 min |
| Tier 4 | 1.7 min |
| Tier 5 | 1.1 min |
| Deeper pass | < 1 min |

Outputs: `cache/` 595 MB (git-ignored; holds the origin table, candidates, labels, the 204 variant label arrays, wide location table, Mw variants, fits), `tables/` 7.4 MB (73 files), `figs/` 15 MB (28 PNG).
