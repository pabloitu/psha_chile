# CONTEXT HANDOFF — ssm_intraslab (in-slab smoothed-seismicity model)

Chile PSHA, intraslab pipeline. This file records the architecture, the
forensic history of why the intraslab model appeared to govern hazard,
what each experiment established, and the closeout items. Companion:
sub_interface/CONTEXT_handoff_interface.md.

## Architecture (post-isolation)

Pipeline: s00_decluster -> s01_mc -> s02_build_ssm -> s03_build_sm.
Single upstream input: cat_classified.csv (the classified catalog).
The catalog handler's mc.py / decluster.py and *_mc / *_dc files are DEAD
CODE for this module — isolated after the stamp/classification confusion.
Two classes, intra_slab and slab_deep, declustered and fit SEPARATELY
(different b, different Mmax; GK epicentral windows must not link 600-km
deep events to shallow ones; the OLD model pooled them under one national
(a,b) — a primary defect). CLASSES dict in ssm_config points at the
internal dc outputs; flipping DC_METHOD re-routes the whole build.
Config: ssm_config.py, run order in header. Aliases keep old names
(OUT/FIG, DM) working alongside the new (OUT_DIR/FIG_DIR, DELTA_M).

## Decisions register

- Regular Mc windows: historical block 1513->1900, then WINDOW_YEARS=10
  steps (user decision: uniform windows "more sound" than hand-drawn
  network epochs; kills the hand-list's 2001-overlap and 2013-gap by
  construction). Starved windows fall to MC_HIST_FLOOR, honest; for
  slab_deep most windows may floor — hand judgment when pasting the table.
- Mc on UNdeclustered catalog; rates on internally declustered (gk74
  fs=0.1 default; gk74_sym = upstream-compatible).
- Fast KS everywhere: n=2500 sims, subsample cap 3000 (seeded), modal-
  start candidate grid, parallel windows. Verified identical results to
  the slow settings on all tested windows; the subsample cap also tempers
  KS over-rejection at large n (conservative-Mc inflation) — a feature.
- Superposition: per-class TGR fields (shape from adaptive-kernel
  smoothing, total pinned to the class Weichert rate), summed. tgr_bins
  truncation convention verified consistent with the build assert.
- Mmax = M_obs + 0.2 per class, MMAX_OVERRIDE escape hatch, MMAX_SANITY
  = 8.4 (Chiapas 2017 M8.2 = global in-slab record + pad). GUARD STILL TO
  WIRE into build_class (top-5 print + hard stop) — s01_mc's [top events]
  print is the early warning only.
- Depths (s03): hypo = nearest slab-top + 7.5 km; usd/lsd = hypo +/-
  depth-stepped half-thickness. LSD later widened +25 km (~40 km band) —
  BOTH a ribbon mitigation and the physically more defensible slab
  thickness; keep.
- min_mag = first bin CENTER (half-bin fix present in the new builder;
  the OLD builder had min_mag = edge — small, direction down).

## Forensic history — why "intraslab governs" (keep; reviewers will ask)

Symptoms: intraslab-only hazard ~ previous FULL model at Iquique; new grid
initially lambda(M>=4.9)=250/yr with effective slope 1.83 and Mmax 9.3.

Root causes found, in order of discovery:
1. 1575 M9.1 (+ 1575 M7.8, 1615 M7.9) classified intra_slab: BAD DATA +
   the pre-1930 override silently skipped pre-1677 events (pandas
   Timestamp bug). Fixed upstream (string-slice years + regression print).
   The pre-1930 rule still exempts slab_deep — OPEN policy question.
2. Completeness table with NO long window (intra_slab topped at 5.1/1960):
   1939 Chillan and 1950 Antofagasta excluded from the fit; b set by M5-6
   alone; model lambda(M>=7)=0.47/yr vs OBSERVED ~0.06-0.09/yr (x5 tail).
   Fix: re-derive COMPLETENESS from s01_mc with long large-M windows.
   Calibration anchors: intra_slab b ~0.9-1.2, lambda(M>=5.0) ~5-15/yr;
   slab_deep b ~1.0-1.3, lambda(M>=5.2) ~1-5/yr; lambda(M>=7) ~0.06-0.09.
3. ~24-28% of rate (and of M>=7 rate) in up-dip cells with slab-top inside
   the interface locked window (smoothing re-injects rate the classifier
   sends to the interface; nearest-neighbor depth assignment has NO
   distance cutoff — dist_deg computed, never used — so off-slab cells get
   edge depths; degree-space KDTree anisotropy minor). PROPER FIX: mask
   the grid in s02 BEFORE normalization (renormalizes onto the deep
   domain; a post-hoc clip DELETES the rate). Crude clip verified as
   diagnostic only.
4. CSV<->XML chain verified faithful (totals, per-bin, minMag, depths).

## Hazard attribution experiments (all at Iquique, intraslab-only)

- pointsource_distance=40: NO change -> hazard from sources within ~40 km.
- LSD +25 km (band ~15->40 km): moderate low-PoE drop -> ribbons real but
  secondary. (Rule of thumb: L = A/W; M7.7 A~4200 km2; 15-km band @45deg
  -> ~200 km ribbon; OQ clips inside usd-lsd and stretches along strike —
  ruptures NEVER breach the surface. AG2020 SSlab REQUIRES rrup, so
  ribbons do shrink distances.)
- clip50/60 (shallow cells removed): ~no further change after widening.
- GMM swap SSlab->SInter: LARGE drop. Parker SSlab: HIGHER than AG2020.
=> VERDICT: the driver is the legitimate deep model (M6-7.5 at 60-110 km)
under slab-GMM scaling and sigma (2-3 eps at 2475 yr), NOT a source bug.
Partially real physics: Tarapaca 2005 ~0.7 g from ~100 km; CRSHM-family
models show in-slab domains in the north. The success criterion is
defensible rates + correct domain + regional GMM ensemble — wherever
hazard then lands is a FINDING.

## GMM state

3-slab-GMM comparison tree built (gmm_logictree_3slab.xml): AG2020 SSlab
region='SAM' 0.34, ParkerEtAl2020SSlab (GLOBAL spec — SA regionalization
optional next) 0.33, MontalvaEtAl2017SSlab (Chilean data — the epistemic
floor candidate) 0.33. FOOTGUN fixed: the interface TRT branchset briefly
carried Montalva-SSlab from swap experiments; restored to AG2020-SInter
SAM. post_process PLOT_GMMS mode shows per-GMM curves + weighted mean.

## Closeout checklist (ordered)

1. Re-derive COMPLETENESS from real s01_mc; paste; verify [fit_class] b
   and rates land in the calibration anchors above.
2. Wire the Mmax guard into build_class (MMAX_SANITY).
3. s02 domain mask (slab-top >= interface z_bottom) with renormalization;
   retire the crude clip. Add the dist_km cutoff in s03 depth assignment.
4. Add the observed-vs-model MFD overlay to the build (the missing
   validation that would have caught the 1.83 slope at build time).
5. One clean intraslab-only run: 3-GMM tree + Iquique disaggregation at
   475/2475 (M-R-eps) — the forensic exhibit.
6. slab_deep pre-1930 override policy decision (upstream).
7. Then re-judge intraslab vs interface with the comparison script
   (compare_interface_intraslab_mfd.py) and the city curves.