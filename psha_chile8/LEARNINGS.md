# LEARNINGS

What earlier rounds (psha_chile4–7, cat_handler_2, the A2 night run) taught us, so we don't repeat it.

## Methods tried

### Catalog and magnitudes
- Cabello integrated catalog as base, dedup by time, distance and |dM| ≤ 0.8 (cat_handler_2). Dropped: the magnitude criterion biased later calibration pairs, and fixed windows missed large-M duplicates (Arauco 2011 twice, CSN vs GCMT 6 s, 59 km).
- Constant agency offsets (ISC +0.3, CSN +0.1, USGS −0.1) and a full reverse-regression re-homogenization. Dropped: the second over-corrected ML.
- A2 correction (4 Nov): published NEIC mb relation restored, ISC mb hinge above 5.2, Md / Mc / m converted by offsets, dithering. Kept as the method template for A5; made b stop depending on the floor and Mc estimators agree. Superseded as data by the rebuild.
- Hand classes for unknown-depth events (by city, period, neighbours). Withdrawn: selection by hazard relevance without event evidence.
- Neighbour vote for unknown-depth events. Removed in favour of excluding them over the deep slab.

### Old classifier (cat_handler_2), reference for A7
- First-match rules by position against Slab2, arc polygon, trench and mechanism; 18 hand overrides after the rules. Detail: `claude/CATALOG_explainer_2_depths_classification.md`.
- Interface band ±11 km (relocated) / ±15 km (free, filled) around the slab top where the top is < 50 km, 65 km with an interface-like mechanism; crustal cap 30 km (50 km over the Pampean flat slab); unknown depths over a deep slab unresolved; Antarctic rules south of 46.15°S and in the Slab2 gap.
- Weak spots: 2 434 interface events (367 of M ≥ 5.5) are interface only because the depth is unknown and the slab is shallow; 2 602 unresolved for unknown depth over the deep slab; triple-junction gap; sub-slab events clustering under the flat slab and next to Jujuy (location error or Slab2 thickness).
- Names grew piecemeal: code names (slab_interface, intra_slab, slab_deep) differ from display names (interface, intraslab, intermediate-depth); "intraslab" meant both the family and one class; renames on 4 Nov (deep_unknown → sub_slab, patagonia_interface → antarctic_interface).

### Completeness
- KS (Clauset 2009) in 10-yr windows, b = 1, reverse running maximum, hand edits: the psha_chile5–6 tables. Justifiable but only partly reproducible.
- Maximum curvature (+0.2), goodness of fit, b-stability per window (mc_crustal.py). Shape-based estimators cannot see the pre-2000 thinning of a merged catalog; only rates per band and period show it.
- Lilliefors: not used.
- Stationarity audit of the tables (f1, Laplace / KS on declustered rates): dropped, it moved tables late and the method was not justifiable.
- Perturbed-table ensemble (15 tables, Mc ± 0.1 / 0.2, start ± 5 yr): hazard −7 to +3 % interface, ± 4 % in-slab; dropped for crustal.
- Open for B9: Stepp, Kijko–Smit sub-catalogs, joint Mc–b–a (Ogata–Katsura, EMR), spatial Mc (Wiemer–Wyss, Mignan), periods from network history vs change points.

### b-value and rates
- Weichert (1980) with the completeness table: the standard and the reference.
- Kijko–Smit (2012): erratic at high floors (starved periods); comparison only.
- b-positive / a-positive (van der Elst 2021; van der Elst and Page 2023): table-free check, kept as a cross-check.
- Random-effects pooling with shrinkage (f10) and floor-averaged b: dropped for crustal.
- Per-epoch fits: localize a bad table; keep as a diagnostic.
- Large-event consistency (fitted vs observed N at M ≥ 7, 8): the most convincing check against a wrong b; keep.
- Fit floor at the start of the b plateau per class: still chosen partly by eye; ± 0.2 moves the controlling-M rate × 0.5–1.9.

### Declustering
- Gardner–Knopoff (gk74), symmetric GK, Grünthal, Uhrhammer compared: method changes hazard 2–3 %.
- Declustered interface b 0.68–0.73 against 0.89–0.92 full; Bird and Kagan 0.96 ± 0.06 fits the full one. Full catalog overdispersed (Fano 7–17).
- Declustered fit reproduced the observed M ≥ 8 rate better in the campaign; the full catalog gives lower N(≥ 8.8). Both kept as a 0.5 / 0.5 branch.

### Spatial pattern (in-slab, crustal)
- Hiemer-style completeness weighting (window_T): single early events dominated (79 % of Concepción's intra_slab rate from one event) → equal weights.
- Calibrated Gaussian kernel by time-block CV (10 neighbours): within 4 % of the power-law 25-neighbour kernel; power-law kept.
- Zonation by latitude: rejected.
- mask50 / clip60 under the coast: mask renormalizes the rate to deeper cells, clip deletes it; neither adopted.

### Interface
- Moment-deficit (time-dependent) branch: rejected; geodetic branch is a moment balance.
- Truncated vs tapered GR (3 %): tapered kept; corner 9.6 is bounded from below only by the data.
- Mmax by moment closure: seg3 and seg4 need 9.2–9.4 to close; kept as a diagnostic.
- Aspect ratio 1–3 (≤ 6 %), Allen and Hayes (4.5 %), Z_TOP 5 / 10, Z_BOTTOM 40–60 (≤ 10 %, now fixed 50).
- Classification tolerance ± 5 km and default-depth events to the interface: ≤ 5 % (9 % Puerto Montt).

### In-slab
- Old depth rule (top + 7.5 km) vs thickness-fraction depths: 5 %; thickness fractions kept.
- Mmax pad 0 / 0.2 / 0.4: 5–7 %; fixed at 0.2.
- Separate vs pooled b, class domain cut: ≤ 4 %.

### Crustal and faults
- Fault MFD shapes AL-I/II/III, YC, tapered, hybrid (Gaussian characteristic plus GR tail, r = 0.5): all kept as branches.
- Multi-fault ruptures (moment-partition cascade, pairs at fault ends within 5 km, f = 0.5): implementation aborted.
- Fault depth from D90 of crustal seismicity: unusable, depths pile at the 30 km cap.
- Fault count test: φ = 1 over-predicts observed M ≥ 6 in the buffers (LOFZ region dominant); data pull toward lower φ.
- Faults carry about 21 % of crustal N(≥ 6).

### GMMs and sites
- Idini et al. (2017) on the interface: removed (needs a soil class).
- Vs30 380 soil series: the nonlinear site term compressed the in-slab GMM axis three-fold; analysis moved to rock (Vs30 800).
- GMM choice is the largest epistemic term everywhere (in-slab 27–42 %, interface 18–23 %).

### Sensitivity and tornado
- One-at-a-time tornado at PGA 475 yr over 10, then 14 cities; ≥ 5 % rule for branches.
- Integration distance 400 vs 500 km: small; final 600 / 500 / 300 per family.
- Family-split equivalence proven exactly (level 1) and by sampling (level 2, ~1 %).

## Pitfalls

### Catalog
- **Cabello's Mw conversion.** The file holds about 1.03·mb + 0.28 for NEIC mb; the paper prints 1.04·mb − 0.02 (pooled) and 1.03·mb + 0 (GCMT) (C25 p. 8). Mc, Md and m at any size, and every native magnitude outside an equation's range, go in as Mw unchanged (C25 p. 3, p. 10). Avoid: convert from native magnitude and scale only; validate every relation against GCMT on pairs matched by time and distance alone.
- **ISC mb saturation grows with size:** mb − Mw ≈ −0.19 at Mw 5.5, −0.43 at Mw 6.5 (Lolli et al. 2023). Literature value; recheck on our pairs in A5.
- **Forward conversion fits against GCMT are biased.** GCMT has few events below Mw 5.2–5.6, so at low native values only the events with a high Mw have pairs; Mw-on-native fits (OLS or chi-square, worst with exponential or quadratic forms) push small events up, heap the catalogue at Mw 4.7–5.0, give b ≈ 1.5 at floor 5.0 and predict 12 % of the observed M ≥ 7 (X1). Regress native on Mw and invert (X2). For Chile mb ≈ Mw and CSN ML ≈ Mw at 4.5–5. Cabello and Candia–Macedo (2026) show the same bias.
- **Inverse fits need the native scale reported at every size.** True for ISC mb, NEIC mb, CSN ML; not for MS, MOS mb, BJI mB (X2 review).
- **ISC mb and NEIC mb errors correlate at 0.92:** averaging them does not halve σ (X2 review).
- **Potin et al. (2024) magnitudes are the CSN bulletin values** (l = GUC ML, c = GUC MD/md, W = GUC MW, ww = CSN Mww; 96–100 % identical); its 1982–1990 coda values are 0.2–1.0 for M 4 events (X1).
- **Potin depths under the flat slab** (29–34°S, below ~90 km) are 25–60 km deeper than ISC-EHB L1 and Slab2; elsewhere they agree within 2 km (X1).
- **ISC-GEM depths are ISC-EHB copies;** GCMT centroid depths are ~12 km deeper than hypocentres (X1).
- **ISC-GEM gives the 1960-05-22 18:56 Valdivia foreshock Mw 8.72** (P&S 7.9, RM18 Ms 7.8): check in A6 (X1).
- **Heaping.** Relations with slope < 1 plus rounding put two native values into one bin (CSN ML: 4.0, 4.4, 4.8, 5.2). Avoid: dither within the native bin before rounding.
- **Default catalog depths.** Not only 0 / 10 / 33 / 35 km: each agency has its own spikes (ISC up to 262, USGS 5–200, GCMT 12 / 15, CSN zero-error depths; ISC-GEM 15–35 seen in the old data but not documented by ISC-GEM). Documented defaults: GCMT 10 km in 1981–1985 and a 12 km floor; ISC-EHB 10 km (ocean) / 15 km (trench, volcano) and fixes in 10 km steps; ISC 10 / 35 km and cell depths after the rebuild, 10 / 15 / 33 km before. Recheck all against the A2 profiles. CERESIS depths flagged "free" are round estimates. Avoid: find defaults per agency as histogram spikes; treat historical CERESIS depths as unknown.
- **Magnitude criterion in matching.** |dM| ≤ 0.8 makes calibration pairs circular. Avoid: match by time and distance only, wider windows at large M, check newly merged M ≥ 6 pairs by eye.
- **Domain cut before relocation.** GCMT-located events moved north of 17°S after relocation (Arequipa 2001). Avoid: apply the domain cut on the final location.
- **Local time and wrong dates.** Maule 2010 time 3 h off in Cabello; Arauco 1975 date in the paper; Mejillones 1994 day and month swapped. Avoid: check large events against two sources.
- **Agency-dependent magnitudes inside one catalog** show up as completeness steps and floor-dependent b, not as an error. Check b per agency at equal Mc.
- **GCCEL is a shallow benchmark.** It selects events shallower than about 50 km (none below 95 km in Chile) and cannot test intermediate-depth locations. Offshore its depths are one-sided (coastal stations only): all catalogues are 5–12 km shallower there, and Slab2 does not decide between them (X3).
- **Potin et al. (2024) locations** are excellent at 18–36° S (epicentre 3–6 km, depth σ 2–4 km against GCCEL) but poor south of 36° S, in the backarc (San Juan) and in depth above 30 km (X3). A Potin record is not a location for events outside the network: CSN locations of distant events can be off by 100 s and 900 km, and Potin keeps them (A3). Before 2000 only about one event in nine with Mw ≥ 4.5 has a Potin record (A4).
- **Teleseismic catalogues** (ISC, ComCat, EHB) are about 20 km east of GCCEL at Tirúa, 38–39° S (X3).
- **Sources list events twice.** The unreviewed ISC Bulletin (2025 on) up to M 7; Potin the Iquique 2014 mainshock (5 s, 37 km apart); ComCat has pairs of records for one event (A3).
- **Before 1964** ISC-GEM and Centennial / ISC origins of M 7 events differ by up to 13 s and 260 km (A3).
- **Legacy USGS WCMT products of 2010–2011 in ComCat carry wrong moments,** in the listed scalar and sometimes in the tensor too (A4).
- **Converting every agency of the ISC Bulletin** adds little and costs homogeneity: the IDC and Beijing surface-wave scales heaped 2000–2010 at Mw 5.0–5.1; without them 453 of 16 293 events (M ≥ 4.5) lose their Mw, most of them 1990s events with a CSN coda magnitude only (A5).
- **A magnitude limit on a converted value is a cut on a noisy value.** On the scale's own value it keeps the events that scatter up (count at Mw ≥ 5 +5 to +10 %); judged on another scale it is 7–15 % low, and that version passed the rate and histogram tests. A test that passes is not proof of no bias: check against measured Mw withheld (X4).
- **Step offsets on values rounded to 0.1 make a comb in the histogram** (GCMT lowered per 0.25 bin; X4). Use a continuous correction.
- **Look at the largest events after any change of the magnitude rule.** The rate, b and histogram tests do not see a few large events moving by 0.5 (the weighted mean of scales took an MS 6.97 event from Mw 7.0 to 6.5; A5).
- **mb conversions read 0.10–0.17 above the regional Mw at 5.0–5.5** and carry 60 % of the values at Mw ≥ 5.0 in 1976–1989; cause not found (A5, test 4). Run the fits with and without a correction.
- **Claims withdrawn** (so they don't come back): "Cabello Mw 0.4 too high at M4–4.5" was a binning artifact.

### Fits
- **Crowded completeness table.** Narrow steps make Weichert swing; slab_deep b 1.72 from such a table. Avoid: space steps by ≥ 0.3–0.5; check against the large events.
- **Per-epoch stamps read as a lookup** (`completeness_steps` with `drop_duplicates` + `searchsorted`): nonsensical b (forearc 0.86, unclassified 0.40).
- **Rate anchoring.** a anchored at MC_MIN_FIT when the first complete magnitude is higher inflates the rate. Anchor at the first complete magnitude.
- **Overriding b at fixed a.** Changing b without refitting a inflated N(≥ 4.9) 20×. Always refit a with b fixed; the total rate above Mc must not move.
- **Optimistic b error.** b/√N is too small; use a bootstrap.
- **Unequal windows with sequences.** Small bins observed only in sequence-rich recent years raise b (forearc 1.18–1.58 vs 0.75–0.97 on single periods).
- **Mc on the full catalog, rates on the declustered one** (or the reverse): Mc differs by > 1 unit in the 1960 and 2010 windows. Use one basis.
- **seismostats binning.** Off-grid magnitudes raise "Magnitudes are not binned correctly"; snap to the 0.1 grid first.
- **Thin classes** (deep_nest b 0.53 on 36 events, Patagonia 14 events): borrow b, keep the local rate.

### Source models
- **min_mag bin-centre convention.** Catalog magnitudes are 0.1 bin centres; `EvenlyDiscretizedMFD.min_mag` is the first bin centre. Using the edge shifted every source 0.05 low. Avoid: `HALF = 0.05` in one place; MFDs, NRML bins and moment balances all at bin centres; unit test.
- **The 0.53× fault-rate mismatch.** Two conventions together: +0.2 on the geometric Mmax branch (× 0.68) and M0 at bin lower edges vs centres (× 0.84). Avoid: one moment convention (bin centres, `M0_AT_EDGE = False`) and Mmax rules exactly as in the logic-tree figure; test the moment balance per fault.
- **Faults without max_mag.** 13 Fagnano segments carry max_mag 0 in the shapefile; read as NaN they fell back to each short segment's own area. The fix raised Puerto Williams from 0.02 to 0.10 g. Avoid: check for zero / missing fields when reading the shapefile.
- **Fagnano overlap.** CL-056c/d/e/i and AR-0056a are probably the same trace in two databases (~90 km within 5 km): up to 12–13 % extra moment if both kept.
- **nofaults branch on the capped background** leaves a hole at M ≥ 6 near faults. The no-fault baseline uses the uncapped grid.
- **Trimmed point-source MFDs.** Capped cells drop trailing zero bins; consistency checks must compare with ≤, not ==.
- **Concepción in-slab excess** (2–3×) was a pattern-weight artifact, not a catalog issue.

### Hazard
- **OpenQuake realization ordering.** `full_lt/source_model_lt` is in logic-tree file order, realizations are enumerated sorted by branch ID, so reconstructed labels were swapped (yc ↔ nofaults). Reconstructing with a Cartesian product also fails when branches have different source sets. Avoid: read labels from the datastore realization objects; sortable branch IDs (`b01_…`); a check that the weighted mean of the realizations equals the stored mean; a physical guard (no-fault branch is the minimum).
- **Mixed result files.** Puerto Williams 0.105 g in `summary.txt` vs 0.020 g in `fr_summary.csv`: one run probably lacked the Fagnano faults. Record the calc ID and build.json with every result table.
- **MMIN_HAZ across families** must match, or the M5–6.5 range is double counted or missing.
- **hazard2csep**: complex-fault mesh spacing, coarse simple-fault mesh, CSV precision, inverted point-source depth factor; check projected rates against the NRML totals.

### Working
- An automated git commit script (rebase) removed working-directory files in psha_chile5. Pablo does git by hand.
- A file revert in a session did not write to disk. Verify writes (size, hash) after changing frozen inputs.
- psha_chile7/interface holds stray copies of top-level files; check which copy is imported before editing.
- Code tested in a sandbox without OpenQuake or Slab2 is untested for those parts; say so.
- Four generations of fit code plus hand edits left no single reproducible path. One script per family from a dated catalog.
