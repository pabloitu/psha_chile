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
- Maximum curvature (+0.2), goodness of fit, b-stability per window (mc_crustal.py). Shape-based estimators cannot see the pre-2000 thinning of a merged catalog when the set is cut near the fit floor; rates per band and period show it, and so do the same estimators once the smaller events are included (B9, below).
- Lilliefors: not used.
- Stationarity audit of the tables (f1, Laplace / KS on declustered rates): dropped, it moved tables late and the method was not justifiable.
- Perturbed-table ensemble (15 tables, Mc ± 0.1 / 0.2, start ± 5 yr): hazard −7 to +3 % interface, ± 4 % in-slab; dropped for crustal.
- B9 (14–15 Nov, `explore/B9/REPORT.md`): completeness belongs to place, depth and period, not to the tectonic class. Read it on all events with the small ones included (from Mw 3.5), per region; one table for every class. A shape-based Mc of the whole margin reads 0.1–0.4 above the regional values, because regions with different b add to a curved distribution.
- Shape-based Mc needs the events below the cut: on a set cut at Mw 4.5 every method reads 4.5–5.1 in every window. Read from Mw 3.5, b-stability and KS give the regions 5.0–5.2 in 1964–1975, 4.8–5.0 in 1976–1989, 4.6–4.8 in the 1990s, 4.5–5.0 in 2000–2011 (Tocopilla and Maule inside) and 4.2–4.7 in 2012–2019. Maximum curvature reads 4.2–4.4 in every window, 1964–1975 included: not usable.
- Mw 4.5–4.9 is complete over the whole margin in no period. Map (cells of 1°, 250 km): Mc above 4.5 in 97 % of the cells in 1976–1999, 52 % in 2000–2011, 15 % in 2012–2026 (18–21° S and the far south); above 5.0 in 11 %, 1.5 %, none. No estimate south of 36° S before 2000 or south of 41° S before 2012.
- Rules that compare rates between periods fail from 1964 on: the automated Stepp test, change points of yearly counts and a joint likelihood of all bands and periods with BIC all take the sequences of 2010–2015 for the complete level and read earlier periods as incomplete (interface b 1.04–1.08, 9.6 events of Mw ≥ 8 expected against 19). The joint rule recovers the table on stationary synthetic catalogues (b within 0.01), so the failure is the rate change, not the code.
- Automatic table that works (hybrid): instrumental steps from the regional Mc per window (a magnitude is complete from the window after the last one whose Mc is above it); before 1964 the earliest year from which the counts of a 0.5 band stay consistent with the instrumental line held fixed. Result on all events: 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500. It lands next to the table read by hand (interface b 0.95 against 0.93).
- The rate rule is one-sided: it objects to too few events, never to too many. It accepts the in-slab record of Mw ≥ 7 back to 1830 because that record has an excess. With few events it cannot see mild incompleteness: steps of Mw ≥ 7 come out up to 40 years early on synthetic catalogues (N(≥ 7) 2–3 % low).
- The automatic table checked on synthetic margins with a known table (B11, 40 catalogues per case): the instrumental steps come out later than the truth in most catalogues ("5.0 from 1976" found in 0–5 %; one window that reads high by chance moves the step, because the rule takes the largest of two methods over regions and windows), and the historical steps of Mw ≥ 7 30–75 years early (a band of few events that is 40–60 % complete is accepted). The fit on that table has N(≥ 5) within 1 %, b +0.015 to +0.033, N(≥ 7) 6–14 % and N(≥ 8) 9–20 % low. The smaller of the two Mc methods finds "5.2 from 1964" in 83–88 % instead of 23–30 %. On the real catalogue the rule gives the table the regional rows show by eye. Give a sensitivity fit with later historical steps; do not call the rule validated.
- The completeness table read on all events did not move when the catalogue was revised (A9, 16 Nov: classes of about 100 events and two magnitudes changed, no location): every Mc per window and region identical, also for the five declustered catalogues. Reclassification cannot change a table that is read on all events.
- Crustal classes against the catalogue-wide table (B11, 16 Nov): the class Mc cannot be measured before 2000 (under 100 events per window; 4.6–4.8 pooled over 1976–2026). In 1964–1975 the forearc and the arc are short at Mw 5.5–5.9 (0.12 and 0.04 per year against 0.64–0.78 and 0.16–0.67 afterwards), so "5.2 from 1964" does not hold for them. The historical steps counted the arc's Mw 7.5–7.9 bins over 197 years on one event (Aysén 1960), and the forearc's Mw 7.0–7.2 bins on 16 fractions of events without depth. The crustal classes are fitted from 1976 only.
- A completeness table read on crustal events alone gives Mc 5.3 for 1976–1989 (above the catalogue-wide 5.0) and early historical steps (6.5 from 1950, 7.0 from 1860, 7.5 from 1500); b rises (family 1.06, arc 1.11). From a floor of 4.5 the family b is steady (0.97 ± 0.02 on 600 events) but through the small events of the sequence years. Not adopted (16 Nov).
- Network-history table (4.5 from 2000, 5.0 from 1976, 5.5 from 1964, …) and the change-point table: both raise the interface b to 1.04–1.06 and fail the large-event check (29 fitted against 44 observed at Mw ≥ 7). Not used.

### b-value and rates
- Weichert (1980) with the completeness table: the standard and the reference.
- Kijko–Smit (2012): erratic at high floors (starved periods). It takes b from the magnitudes inside each period; Weichert also uses the counts per period against their length. Same number on a one-period table, within the bootstrap error on a table that fits, 0.06–0.17 apart on a table that does not (B9): a check of the table, not a second estimate of b.
- Magnitude error (B9, 15 Nov): converted magnitudes overcount. On 6 193 events with a measured and a converted Mw the converted values give 6–9 % more events at Mw ≥ 5.6–6.0 from 1976 (8 % expected from the listed σ); the weight exp(−β²σ²/2) per event brings the two counts together. On synthetic catalogues the uncorrected N(≥ 5) is 10 % high. The weight on all events is nearly one factor for the whole line: rates −8 to −11 %, b within 0.02.
- CEUS-SSC (2012, §3.3.1) read in full: observed-type magnitudes are moved to M − βσ² and counted N* = exp(β²σ²/2); regression values get N* only; the net effect on a rate equals the plain weight exp(−β²σ²/2). Musson (2012): values from an orthogonal or inverse fit behave like observed ones (overcount), values from least squares undercount. Who corrects: USGS (Mueller 2019), UCERF3 (Felzer), New Zealand 2022 (Monte Carlo, Rollins et al. 2024); MPS19 and ESHM20 do not mention it. Notes in `explore/B9/MAG_ERROR_REFS.md`.
- Methods compared on the frozen catalogue and on 400 synthetic catalogues per case built like it (B11, `fits/FITS.md`). Maximum likelihood on the table recovers b within 0.003 and rates within 3 %, and its bootstrap intervals hold the truth in 87–89 % of the catalogues for b and N(≥ 7) (nominal 90 %). Without the magnitude-error weight N(≥ 5) is 12 % and N(≥ 7) 26–29 % high. Aki–Utsu on 1976–2026 scatters 1.3 times more and reads the interface b at 0.914 (rate of the sequence years); least squares scatters 2.4 times more. Pooled b (random effects): the between-unit variance is zero in every family (segments 0.958, in-slab 1.159, crustal 0.980); it helps when the true b are equal and pulls the outer classes when they are not.
- Tapered and cut at Mmax give the same b (within 0.003; nest 0.010) and N(≥ 5); N(≥ 7) within 4 % (nest 9 %); they part above (N(≥ 8): tapered 2–15 % higher on the interface, 37 % for segment 32–26° S, 20 % lower in-slab). A tapered line with its corner at the observed maximum has the moment rate of a line cut at observed + 0.2 (Kagan 2002b, eq. 12). Corner 9.6 changes nothing below Mw 8.5; a free corner gives 9.6 for the interface (lower bound only) and 7.8 for in-slab.
- Joint fit of b and detection (Ogata and Katsura 1993, one detection curve per network window) fails on the catalogue from 1976: b 1.26–1.71 from Mw 3.5, 0.93–1.62 from Mw 4.5, detection widths of 0.7–1.5 units. Below Mw 5 the catalogue is a mixture of regions and agencies, not one line times one detection curve. It works on synthetic catalogues.
- The magnitude-error weight leaves N(≥ 5) about 2 % high (3–4 % on 1976–2026 alone), because small events carry the larger σ and the weight is exact only when σ does not depend on size; the bootstrap intervals do not contain that bias (N(≥ 5) interval holds the truth in 81–87 %). It removes 20–30 % of the events of Mw ≥ 7 and 8, nearly all before 1904 (σ 0.5, count 0.55).
- A crustal class of 70–200 counted events cannot hold its own b: arc 1.04 ± 0.10, backarc 0.93 ± 0.09, forearc 0.93 ± 0.06, Patagonia 1.17 ± 0.32, against a family b of 0.975 ± 0.042 that hardly moves with the table (0.97–1.01). With the family b every class reproduces its events of Mw ≥ 7 since 1905, which are not in the fit (arc 1.7 expected, 1.7 observed); with its own b Patagonia fails. One b for the family, own rates (16 Nov, `fits/FITS.md` section 11).
- What still sets the crustal rates (16 Nov): the sequences of 2000–2010 are a quarter of the 1976–2026 window with 2–5 times the rate of Mw 5.0–5.4 of the other periods; the forearc is mostly fractions (weight-1 events alone give 40 % of its rate); the arc has no event above Mw 6.5 since 1976, so its tail to Mmax 7.9 is extrapolated.
- Split events (class weight between 0 and 1) change rates, hardly b: weight-1 events only against all, N(≥ 5) × 0.51 shallow in-slab, × 0.37 forearc, × 0.75 interface (B9).
- b-positive reads about 0.04 low on a synthetic catalogue thinned by a completeness table, and scatters by 0.1–0.2 on classes with fewer than 100 pairs. Cross-check only.
- Jujuy nest, backarc and Patagonia show no plateau of b against the floor: one floor, no pooling, rough numbers (Patagonia with the forearc b).
- b-positive / a-positive (van der Elst 2021; van der Elst and Page 2023): table-free check, kept as a cross-check.
- Random-effects pooling with shrinkage (f10) and floor-averaged b: dropped for crustal.
- Per-epoch fits: localize a bad table; keep as a diagnostic.
- Large-event consistency (fitted vs observed N at M ≥ 7, 8): the most convincing check against a wrong b; keep.
- Fit floor at the start of the b plateau per class: still chosen partly by eye; ± 0.2 moves the controlling-M rate × 0.5–1.9.

### Declustering
- Gardner–Knopoff (gk74), symmetric GK, Grünthal, Uhrhammer compared: method changes hazard 2–3 %.
- Declustered interface b 0.68–0.73 against 0.89–0.92 full; Bird and Kagan 0.96 ± 0.06 fits the full one. Full catalog overdispersed (Fano 7–17).
- Declustered fit reproduced the observed M ≥ 8 rate better in the campaign; the full catalog gives lower N(≥ 8.8). Both kept as a 0.5 / 0.5 branch.
- B9 on the frozen catalogue: Gardner–Knopoff (van Stiphout windows) removes 79 % of the interface and 88 % of the Jujuy nest at Mw ≥ 4.5 and gives an interface b of 0.6–0.77 with no plateau; the nearest-neighbour method (Zaliapin and Ben-Zion) leaves b unchanged. The two give very different catalogues for the in-slab pattern (50 % against 7 % removed).

- Nearest neighbour keeping the first event of a cluster (B9's setting) removes great mainshocks in favour of foreshocks (Valdivia 1960, 1877, 1922, Iquique 2014) and halves the interface N(≥ 8). Keep the largest event of each cluster if the catalogue is used for rates (B12).
- With the threshold set after 1964, nearest neighbour links great historical earthquakes decades apart (1657 to 1751, 1975 to 1960) (B12).
- On the full-catalogue table the Gardner–Knopoff interface b has a plateau (0.72–0.76, floors 5.0–6.0); B9's "no plateau" was on the network table from Mw 4.5 (B12).
- Run on all classes together, both methods remove crustal and in-slab events after interface mainshocks (57–68 % of their crustal removals); run them per family (B12).
- The two-Gaussian threshold of log10 η takes 5–15 % of the background events of synthetic catalogues as clustered (B12).

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
- Intermediate in-slab events of Mw ≥ 7 are 2.8 times more frequent in 1900–1975 than since 1976 (29 against 7 events; at Mw ≥ 6.5 the two periods agree). Completeness cannot make an excess; most are converted from Centennial mB / Ms. Any table that reaches before 1964 at Mw ≥ 7 fails the large-event check for this class (B9). Left as it is, named in the paper (15 Nov). B11, per band and period inside the table: Mw ≥ 7 in 1905–1963 19.1 observed (by weight) against 7.2 fitted, of them 8.8 against 1.7 at Mw ≥ 7.5; from 1976 6.9 against 6.1. 19 of the 32 old events are Abe mB values of the Centennial catalogue converted with Abe (1982). In 1964–1975 the class is short at Mw 5.0–6.4 (110 against 173 fitted; ISC-GEM proxy values), the opposite sign: the two old magnitude sources do not agree with each other or with the modern record.

- Intermediate in-slab from 1905 against 1964, reviewed on catalogue 17g (18 Nov, FITS; scripts `drafts/fits/inslab/`). From 1905 the Mw ≥ 7 check fails (16.2 fitted, 28.8 observed); from 1964 it passes on every floor (5.0, 5.8, 6.0) and with every estimator tried (magnitude errors inside the likelihood, b-positive, b-more-positive, penalized ML with a prior b 1.0 ± 0.1: b within 0.03 of the fit). Measured causes: (1) the Abe (1982) Mw of deep events (> 60 km) runs 0.36 high against a measured Mw of the same event (14 pairs, 1909–1980, 13 positive; shallow −0.06 on 21 pairs), and 70 % of the intermediate Mw ≥ 7 of 1905–1963 are Abe mB, while the interface events of those years are mostly moment Mw and Ms; (2) with the deep Abe values 0.36 lower the Mw ≥ 7 rates of 1905–1963 and 1964–2026 agree (ratio 1.6, p 0.32), and since 1964 no rate change at Mw 5.5–6.5; (3) what still fails is the bend: the b of Mw 5–6 (1.15–1.18) predicts too few Mw ≥ 7 in both periods, the long 1905 span makes the gap significant, 1964 keeps it inside the band. Not causes: deep-focus events, class weights, merging shallow and intermediate, an in-slab table of its own (same instrumental steps). The early values not from Abe (1939, 1950, 1957) agree with ISC-GEM and Pasadena within 0.2.
- A 95 % depth per place follows the worst depths and the sparse areas (30–124 km below the top); one fraction of the Slab2 thickness (0.475) holds along the margin, across magnitudes and in both depth sets (C14). Old fraction 0.65 → 0.475; old hypocentre fraction 0.30 ≈ the new mean hypocentre.

### Crustal and faults
- Fault MFD shapes AL-I/II/III, YC, tapered, hybrid (Gaussian characteristic plus GR tail, r = 0.5): all kept as branches.
- Multi-fault ruptures (moment-partition cascade, pairs at fault ends within 5 km, f = 0.5): implementation aborted.
- Fault depth from D90 of crustal seismicity: unusable, depths pile at the 30 km cap.
- Fault count test: φ = 1 over-predicts observed M ≥ 6 in the buffers (LOFZ region dominant); data pull toward lower φ.
- Faults carry about 21 % of crustal N(≥ 6).
- FaultQuake (Tavakolizadeh et al. 2024; used by MASCSN26) on single faults: Mmax conflated from strain-drop, aspect-ratio, length and area estimates; moment rate μ · slip · min(L, LAR) · W, with LAR the aspect-ratio length of Pace and Peruzza (2002); one truncated GR. The conflated Mmax is the same as Leonard or 0.1–0.3 lower; on A it raises the arc bulge from 3.3 to 3.5 times the fit (more Mw 6 for the same moment), so it is no lever on the bulge. The length cap is: it keeps 0.47 of the arc fault moment at 10 km thickness (0.80 at 20 km), 0.08 in Patagonia, but by fault length (long Liquiñe–Ofqui traces 0.19, Fagnano 0.05, short faults 1.0), so it cuts the large events selectively, and it counts the moment of one rupture-length patch for a whole long fault. Not a coupling; a lower ψ does a uniform cut (S3, 16 Nov).

### GMMs and sites
- Idini et al. (2017) on the interface: removed (needs a soil class).
- Vs30 380 soil series: the nonlinear site term compressed the in-slab GMM axis three-fold; analysis moved to rock (Vs30 800).
- GMM choice is the largest epistemic term everywhere (in-slab 27–42 %, interface 18–23 %).
- On the Bastías et al. (2026) records the global NGA-Sub models predict 0.6–1.3 ln too low at PGA and SA(0.2); their South America versions halve that. Use the regional versions (GM1).
- Interface event terms of every tree GMM rise with hypocentral depth (about 2 ln per 100 km at PGA); events at 40–60 km are underpredicted, which may be partly the interface / in-slab boundary of the classification (GM1).
- LLH weights over many GMMs come out nearly flat (0.08–0.11 for the reasonable models); the bootstrap rank shares separate the models more clearly (GM1).

### Sensitivity and tornado
- One-at-a-time tornado at PGA 475 yr over 10, then 14 cities; ≥ 5 % rule for branches.
- Integration distance 400 vs 500 km: small; final 600 / 500 / 300 per family.
- Family-split equivalence proven exactly (level 1) and by sampling (level 2, ~1 %).
- A tornado figure reads best as vertical bars with the change of the total, the family-alone range pale behind it, every branch labelled and the reference at 0 (`hazard/FIGURE_STYLE_tornado.md`, 16 Nov).
- Single-GMM results need no jobs of their own: each model's curve is in the realizations of the set job (S5a).
- A geodetic branch copies the b of the seismic fit beside it. Under a declustered b the same moment moves into large events; build geodetic branches on the full-catalogue fit only (16 Nov).
- Mc(t) on interface events only (17g, 18 Nov) gives the same whole-margin table within a few years (5.0 from 1975 against 1981) and the same margin fit (b 0.942, N(≥ 7) within 0.3 %). In a quiet segment a class-only series cannot resolve its history: in the south (37–46° S) it reads 5.0 from 1964, while all events show the real shortfall before 1999 (half the Mw 5.0–5.1, all smaller events converted). Read Mc on all events of a region; completeness belongs to the network, not to the class.

## Pitfalls

### Catalog
- Mc by b-stability or KS reads too low in small samples: subsamples of dense cells give 3.5 at 150–500 events where the full cell gives 4.3–4.8; about 2 000 events are needed. The B9 Mc maps (`mc_all_map_*`, at least 150 events per cell) are biased low in sparse cells. A b-positive rule has no size bias but scatters ±0.3 at 150–300 events and reads low where b rises with the cut (deck 261116, 16 Nov).
- **Cabello's Mw conversion.** The file holds about 1.03·mb + 0.28 for NEIC mb; the paper prints 1.04·mb − 0.02 (pooled) and 1.03·mb + 0 (GCMT) (C25 p. 8). Mc, Md and m at any size, and every native magnitude outside an equation's range, go in as Mw unchanged (C25 p. 3, p. 10). Avoid: convert from native magnitude and scale only; validate every relation against GCMT on pairs matched by time and distance alone.
- **ISC mb saturation grows with size:** mb − Mw ≈ −0.19 at Mw 5.5, −0.43 at Mw 6.5 (Lolli et al. 2023). Literature value; recheck on our pairs in A5.
- **Forward conversion fits against GCMT are biased.** GCMT has few events below Mw 5.2–5.6, so at low native values only the events with a high Mw have pairs; Mw-on-native fits (OLS or chi-square, worst with exponential or quadratic forms) push small events up, heap the catalogue at Mw 4.7–5.0, give b ≈ 1.5 at floor 5.0 and predict 12 % of the observed M ≥ 7 (X1). Regress native on Mw and invert (X2). For Chile mb ≈ Mw and CSN ML ≈ Mw at 4.5–5. Cabello and Candia–Macedo (2026) show the same bias.
- **Inverse fits need the native scale reported at every size.** True for ISC mb, NEIC mb, CSN ML; not for MS, MOS mb, BJI mB (X2 review).
- **ISC mb and NEIC mb errors correlate at 0.92:** averaging them does not halve σ (X2 review).
- **Potin et al. (2024) magnitudes are the CSN bulletin values** (l = GUC ML, c = GUC MD/md, W = GUC MW, ww = CSN Mww; 96–100 % identical); its 1982–1990 coda values are 0.2–1.0 for M 4 events (X1).
- **Potin depths under the flat slab** (29–34°S, below ~90 km) are 25–60 km deeper than ISC-EHB L1 and Slab2; elsewhere they agree within 2 km (X1).
- **ISC-GEM quality D exists only in its Supplement** (events ISC-GEM lists apart as unreliable; Mw uncertainty 0.7–2.3). Check which file a value comes from before reading its uncertainty as a standard error (B11).
- **Cabello's historical magnitudes carry an uncertainty of their own** (CERESIS-GEM: 0.2 or 0.6); the catalogue uses a default of 0.5 (kept, 15 Nov).
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
- **ISC fixed depths at odd values** (181, 117 km) are the regional default grid of its locator, not depth-phase depths; ISC-EHB L1 fixed depths are depth-phase depths (A4).
- **Potin depths under 20 km at and off the coast** are a median 11–21 km shallower than GCCEL and ISC-EHB L1, but about a quarter are truly shallow; ISC depths are not a tested replacement for small events (A4).
- **The source catalogues carry their own depth quality flags** (ISC-GEM A–C, Centennial DEQ / FEQ / LEQ, ISC-EHB L1–L3, GCCEL depth codes); use them before inventing a screen (A4).
- **Depth against Slab2 hardly separates interface from other events.** On 1 270 events with a mechanism, classified without it, the depth rule scored a Brier of 0.20 against 0.18 for one constant weight; changing the depth σ moved it by 0.01. Test a classification rule against withheld mechanisms before tuning its inputs (A7).
- **The count of split events is not a quality measure.** A band with a sharp edge inside a continuous depth error splits every event near the edge; lowering σ moves the edge cases, it does not remove them (A7).
- **With our depth errors no rule classes more than about two thirds of the events over the shallow slab correctly** (synthetic catalogues, X5).
- **In the local depths of Riedel-Hornig et al. (2026) thrust events form a layer 4 km wide about 5 km below Slab2**, and other mechanisms sit 17 km below; their own class (± 5 km of Slab2) calls half the thrusts in-slab. Whether the offset is a Slab2 error or thrusts in the top of the slab is a question for S. Ruiz or C. Sippl (X5).
- **Misfit plots against one reference mechanism hide the other mechanism families**; nodal planes in strike, rake and dip show them (Specht et al. 2017; X5).
- **The Kagan angle mixes plane and slip:** 30° can be a plane 30° off or the right plane with the slip 30° off; for the interface the plane must be strict and the slip direction can be loose (X5).
- **Claims withdrawn** (so they don't come back): "Cabello Mw 0.4 too high at M4–4.5" was a binning artifact.

- The listed depth σ of the frozen catalogue depends on source and depth range; a cut on σ is a cut on depth. Select depth sources, not σ values, when the depth is the quantity (C14).
- Riedel-Hornig and Potin agree under the flat slab because both use Chilean stations only; both are 20–30 km deeper than ISC-EHB L1 east of the border. Agreement of two local catalogues is no test there (C14).

- Split no-depth events leak great historical events into small classes: shares of 0.06–0.13 of Mw 8+ interface events made most of the forearc's observed crustal Mw ≥ 7 (A9). Before trusting a crustal Mmax or N(≥ 7), list the split events behind it.
- A literature class reaches `classify.py` only through a hint row in `overrides_A6.csv`; an A3 match to Ruiz and Madariaga alone does not set it (A9).
- Every reported Mw 7.7 of Aysén 1960 (ISC-GEM, ComCat, Cabello, Ruiz and Madariaga) traces back to one paper, Kanamori and Rivera (2017). Count independent determinations, not catalogues (A9).
- NOAA NCEI tsunami validity grades whether a tsunami happened, not the earthquake. Validity 3–4 is the usable interface signal for historical events (Candia and Macedo's rule); validity 1–2 entries mostly have no runup record (A9).
- A converted magnitude depends on the depth: an accepted in-slab depth moved 1939-04-18 from Mw 7.3 to 7.6 (A9). Rerun the magnitude step after depth hints.
- **Large historical events just outside the domain carry unchecked classes.** North of 17° S (`DOMAIN` in `catalog/locate.py`, `in_domain` False) the position rule classes southern-Peru giants without depth as in-slab with weight 1: 1784 Mw 8.4, 1821 Mw 8.2, 1600-02-19 Mw 7.9 and 1600-02-28 Mw 8.1, 1552, 1582, 1715; 1913 Mw 7.8 is split. No fit uses them today. Avoid: if the domain is moved north, or these events feed a spatial model or a hazard check near Arica, each needs an A6 row first, either a class hint with a source or removal. The two 1600 events fall in the days of the Huaynaputina eruption (19 Feb 1600) and may be volcanic (A6, 16 Nov; not checked in a source).

### Fits
- **One correction, two questions.** "Does the corrected catalogue make the fit pass?" and "is the rate constant?" can answer differently on the same correction (intermediate in-slab, deep Abe values 0.36 lower: the fit still fails, the rates agree). Say which question a test answers before reading it as settling a cause (18 Nov, FITS).
- **A count ratio without the magnitude-error weight overstates a rate change.** Intermediate Mw ≥ 7, 1905–1963 against 1964–2026: 2.4 on raw weights, 2.06 with exp(−β²σ²/2) and the cluster dispersion, p 0.10, not significant (18 Nov, FITS).
- **Completeness methods cannot see an excess.** Rate-based rules (ours, Hakimhashemi–Grünthal, Albarello) read early magnitudes that are too high as early completeness: on intermediate in-slab alone our rule gave Mw 6.5 complete from 1820 (18 Nov, FITS).
- **Empty bins above the largest event.** A likelihood that keeps them raises the b of a small class by 0.03–0.06 (forearc, arc, backarc, nest) and lowers N(≥ 7) by up to 23 %. Leave the bins above Mmax out (B11).
- **An open line above Mmax.** Against a tapered or cut line it gives 24–34 % more events at Mw ≥ 7 for the nest and the forearc. Fit and report the shape the source uses (B11).
- **A cumulative plot carries an excess downward.** The intermediate in-slab points sit above the line from Mw 6.3 to 7.5, but the bins 6.0–6.9 fit (since 1976: 85 observed, 84 fitted); the lift is the excess of Mw ≥ 7 of 1905–1963 added into every point below it. Compare per bin and period before reading a bump (B11).
- **An Mmax set by a split event** is set by its weakest property. The forearc 7.4 came from 1960-12-02 Mw 7.2 (24.7° S), crustal by one Centennial depth of 14 km with σ 20 km, while ISC-GEM puts it at 35 km on the interface and no source gives a mechanism. Take the largest event among those of certain class (weight 1): forearc 7.0, Pichilemu 2010 (16 Nov).
- **For a small class the table moves the result more than the estimator.** Over five reasonable tables the forearc N(≥ 5) runs from 3.5 to 5.0 and the arc N(≥ 7) by a factor of two, against a bootstrap interval of about ± 9 % at N(≥ 5). The bootstrap does not contain the table; show its spread next to it (16 Nov).
- **A fit that keeps the old large events cannot be checked against them.** With the crustal classes fitted from 1976, the events of Mw ≥ 7 of 1905–1975 became an independent test of the line (16 Nov).
- **Crowded completeness table.** Narrow steps make Weichert swing; slab_deep b 1.72 from such a table. Avoid: space steps by ≥ 0.3–0.5; check against the large events.
- **Per-epoch stamps read as a lookup** (`completeness_steps` with `drop_duplicates` + `searchsorted`): nonsensical b (forearc 0.86, unclassified 0.40).
- **Rate anchoring.** a anchored at MC_MIN_FIT when the first complete magnitude is higher inflates the rate. Anchor at the first complete magnitude.
- **Overriding b at fixed a.** Changing b without refitting a inflated N(≥ 4.9) 20×. Always refit a with b fixed; the total rate above Mc must not move.
- **Optimistic b error.** b/√N is too small; use a bootstrap.
- **Unequal windows with sequences.** Small bins observed only in sequence-rich recent years raise b (forearc 1.18–1.58 vs 0.75–0.97 on single periods).
- **Mc on the full catalog, rates on the declustered one** (or the reverse): Mc differs by > 1 unit in the 1960 and 2010 windows. Use one basis.
- **seismostats binning.** Off-grid magnitudes raise "Magnitudes are not binned correctly"; snap to the 0.1 grid first.
- **Thin classes** (deep_nest b 0.53 on 36 events, Patagonia 14 events): borrow b, keep the local rate.
- **Short window for the small events, long windows for the larger ones.** If the short window is the sequence-rich recent one, b rises and the large events are under-predicted (interface 1.06, 29 against 44 at Mw ≥ 7). One instrumental window from 1964–1976 for everything below Mw 7 does not (B9).
- **Moving magnitudes for the error correction.** The shift M − βσ² moved historical events by 0.2–0.9 units and can carry an event below the magnitude from which its period counts; CEUS-SSC itself finds shifts biased (rate −25 to −48 %) when completeness varies with magnitude. Weight the counts instead.
- **A weight on part of the events.** With the magnitude-error weight on instrumental events only, N(≥ 7) depends on what the historical magnitudes are (+13 to −3 % on synthetic catalogues); ISC-GEM values with σ near 1 count 0.07. One rule for all events (15 Nov).
- **"The catalogue is cut at 4.5."** The frozen file holds every size (18 002 events of Mw 4.0–4.4 in the domain); only the working set of the B9 scripts was cut. Check what a loader keeps before calling a method blind.

### Source models
- **min_mag bin-centre convention.** Catalog magnitudes are 0.1 bin centres; `EvenlyDiscretizedMFD.min_mag` is the first bin centre. Using the edge shifted every source 0.05 low. Avoid: `HALF = 0.05` in one place; MFDs, NRML bins and moment balances all at bin centres; unit test.
- **The 0.53× fault-rate mismatch.** Two conventions together: +0.2 on the geometric Mmax branch (× 0.68) and M0 at bin lower edges vs centres (× 0.84). Avoid: one moment convention (bin centres, `M0_AT_EDGE = False`) and Mmax rules exactly as in the logic-tree figure; test the moment balance per fault.
- **Faults without max_mag.** 13 Fagnano segments carry max_mag 0 in the shapefile; read as NaN they fell back to each short segment's own area. The fix raised Puerto Williams from 0.02 to 0.10 g. Avoid: check for zero / missing fields when reading the shapefile.
- **Fagnano overlap.** CL-056c/d/e/i and AR-0056a are probably the same trace in two databases (~90 km within 5 km): up to 12–13 % extra moment if both kept.
- **nofaults branch on the capped background** leaves a hole at M ≥ 6 near faults. The no-fault baseline uses the uncapped grid.
- **Trimmed point-source MFDs.** Capped cells drop trailing zero bins; consistency checks must compare with ≤, not ==.
- **Concepción in-slab excess** (2–3×) was a pattern-weight artifact, not a catalog issue.
- Whole-fault chains by the UCERF3 thresholds alone make branching, overlapping ruptures that drain slip; path rules on subsections with the strict whole-fault rule give linear chains (S3, 16 Nov).
- SHERIFS keeps one slip budget per fault, so a partly ruptured fault cannot be represented: merge to whole faults or make the subsections faults (S3, 16 Nov).
- OpenQuake 3.27 multi-fault files: comma-separated section ids, one planar surface per section, NRML 0.5 with the investigation time on the source model, section ids unique across every sections file of a job (S3, 16 Nov).
- Per-cell in-slab depth statistics jump at the 50 km slab-top line because of the ± 15 km interface band; use one rule for every cell and class-weighted events (C15, 16 Nov).
- Two classes on the same cells double the point sources; write one source per cell with the summed MFD (same hazard, 58 % of the time) (S2, 16 Nov).
- Module caches keyed by a date in another module (`mfsrc_*.pkl` on `faults.DATE`) silently reuse old sources; bump the date or delete the cache when a rule changes (S3).

### Hazard
- **OpenQuake realization ordering.** `full_lt/source_model_lt` is in logic-tree file order, realizations are enumerated sorted by branch ID, so reconstructed labels were swapped (yc ↔ nofaults). Reconstructing with a Cartesian product also fails when branches have different source sets. Avoid: read labels from the datastore realization objects; sortable branch IDs (`b01_…`); a check that the weighted mean of the realizations equals the stored mean; a physical guard (no-fault branch is the minimum).
- **Mixed result files.** Puerto Williams 0.105 g in `summary.txt` vs 0.020 g in `fr_summary.csv`: one run probably lacked the Fagnano faults. Record the calc ID and build.json with every result table.
- **MMIN_HAZ across families** must match, or the M5–6.5 range is double counted or missing.
- **hazard2csep**: complex-fault mesh spacing, coarse simple-fault mesh, CSV precision, inverted point-source depth factor; check projected rates against the NRML totals.
- OpenQuake refuses fault sources above 52 000 ruptures unless `strict = false`; the full-margin interface has 101 864 at a 10 km mesh (S5a).
- Job rows left as executing with no live process block `oq engine`; check `oq engine --lj` before a batch and abort them (S1, 16 Nov).
- OpenQuake sorts sites by longitude: match results to cities by coordinates, never by order (S2).

### Working
- A check that finds a problem tends to produce a patch rule for a few events. Before adding one, ask whether it has a citation and whether a quality-check sentence would do. Table of rules by support: `catalog/RULES_LOCATION_MAGNITUDE.md` (13 Nov).
- An automated git commit script (rebase) removed working-directory files in psha_chile5. Pablo does git by hand.
- A file revert in a session did not write to disk. Verify writes (size, hash) after changing frozen inputs.
- psha_chile7/interface holds stray copies of top-level files; check which copy is imported before editing.
- Code tested in a sandbox without OpenQuake or Slab2 is untested for those parts; say so.
- A process pool with numpy needs `OMP_NUM_THREADS=1`: 14 workers without it took the machine to a load of 130 and a 45 s job to 10 minutes (B11).
- Four generations of fit code plus hand edits left no single reproducible path. One script per family from a dated catalog.
- Hard-coded dates go stale (the crustal background read an old nodal-plane table for a day). Inputs are read from `CURRENT.md`; the owner updates its line on publishing (16 Nov).
- Publishing a shared input five times in a day meant five rebuild rounds. Batch catalogue and fits changes and publish once (16 Nov).
- Decisions made inside a session and only proposed in the WORKLOG lagged DECISIONS by half a day; the session writes Pablo's confirmed decisions itself (16 Nov).
- The chat-to-device file bridge sometimes writes the previous version silently: after every write, re-read the file and compare, and write again until it matches (15–16 Nov).
