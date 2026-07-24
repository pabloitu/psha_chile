# CONTEXT HANDOFF — sub_interface (subduction interface source model)

Chile PSHA, subduction interface pipeline. Standalone: consumes exactly one
upstream file, produces the OQ inputs for the interface logic tree. This
file records every decision, the reasons, the guards, and the open items.
Companion: ssm_intraslab/CONTEXT_handoff_intraslab.md, crustal handoff.

## Architecture

Pipeline: s00_geometry -> s01_decluster -> s02_mc -> s03_ab -> s04_rates
-> s05_sources (-> s06_check_oq optional). One config (sub_config.py,
plain module constants). Outputs under outputs<RUN_TAG>/ — RUN_TAG isolates
sensitivity variants ("" = reference). RUNBOOK.md has the change->rerun
table. Single upstream input: cat_slab_interface.csv (classified,
UNfiltered, UNdeclustered). The catalog handler's *_mc.csv / *_dc.csv are
never used: _mc files are Mc-FILTERED with national per-epoch stamps
(decided unreliable) and upstream dc inherits them. s01/s02 print an input
fingerprint (sha256, spans, counts) — compare after any upstream re-run.

## Logic tree (as built, 16 end branches)

geometry {segmented, non_segmented} 0.5/0.5
x rate model {seismic, geodetic} 0.5/0.5
x [geodetic only] chi {lo, mid, hi} 0.25/0.5/0.25  (chi +/- 0.1)
x MFD form {tgr, tapered} 0.5/0.5
Mmax: SINGLE value per segment = M_obs (no +0.2 branch, no
geometry-admissible branch — decided against Mmax uncertainty; southern
segment fixed 9.5 = Valdivia). GMMs: separate collapsed tree for the
SSC sensitivity runs.

## Decisions register (decision — reason)

- Segment boundaries [-45.6, -37, -32, -26, -17.6]: TEAM INPUT, config
  list; "somewhat arbitrary, team decides"; shapefile exported for review.
  Boundary and MMAX inputs move together (Maule at ~-36 sits just inside
  seg2's southern edge).
- Exact-cut slicing: boundary nodes interpolated so adjacent segments share
  nodes; area closure asserted (sum(segments) == global). Areas are true 3D
  mesh areas (ECEF triangulation) — feed the geodetic moment.
- z_top 5 km, z_bottom 50 km, constant, parametrized. (z60 exists as a
  RUN_TAG variant for sensitivity.)
- Declustering INSIDE the pipeline (GEM practice: the window is an analysis
  choice). Per-class, not grouped (deviation from Pagani's grouped
  declustering; consistency with the crustal SSM). Default gk74 fs=0.1;
  gk74_sym reproduces the upstream symmetric choice; uhrhammer DISQUALIFIED
  for this catalog (M9.5 windows ~19 yr/740 km delete independent large
  events: 1967, 1974, 2011 Araucania). Removed-M>=7 review table +
  DC_KEEP_IDS override. Decisions on specific events:
  * 1960 M8.1 Arauco (id 887): STAYS REMOVED (dependent foreshock of
    Valdivia; keeping it violates the Poisson framework). Flip via
    DC_KEEP_IDS if the team disagrees; sensitivity via the s03 table.
  * 1962 M7.2 (632 d post-Valdivia) and 1998 M7.0 (915 d post-Antofagasta):
    flagged to the team, removal is a window artifact as much as physics.
  * 2012 M7.1 Constitucion: stays removed (consensus Maule aftershock).
- Mc on the UNDECLUSTERED catalog (detection is a network property;
  estimating on a declustered catalog manufactures artifacts — the
  Mc=6.1@2010 episode was GK deletions masquerading as incompleteness).
  Full-catalog windows only; segments enter at the rate step.
- COMPLETENESS (hand-approved, load-bearing): [(8.3,1513), (6.8,1900),
  (6.0,1950), (5.3,1976), (5.2,1986), (5.0,1997), (4.8,2002), (4.4,2013)].
  The 8.3 historical step is the KS estimate on 1513-1900 ACCEPTED AS IS
  (conservative; excludes pre-1900 M7.5-8.2; comparable in spirit to GEM's
  interface thresholds). With MMIN_FIT=5.6 this table carries much of the
  fit — it is the single most decision-laden input.
- a-b: Weichert (AB_ESTIMATOR), MMIN_FIT = 5.6 — chosen from the
  b-stability plot: pooled b slides 1.0 -> plateau 0.75-0.78 over floors
  5.6-6.2, all segments converge there; Kijko-Smit erratic at high floors
  (starved per-period Aki estimates) -> rejected as branch and as
  estimator-axis (method uncertainty, not nature's). The low-M drift is
  magnitude-scale heterogeneity + real curvature; the M7-8 observed bulge
  is the Pagani bulge, carried by the geodetic branch, not refit away.
- Rate branches: seismic = Weichert (a,b) per segment; geodetic = direct
  moment closure (OPTION A): Mdot0 = chi*mu*A*v; b borrowed from seismic;
  a solved per MFD form so total MFD moment = Mdot0. A&L/YC85 machinery
  REJECTED (crustal-lineage constants); Pagani hybrid (max of catalog GR +
  characteristic) kept as OPTION B for the discussion section only.
  Consequence: geodetic a differs per Mmax -> computed at build time, never
  stored per-segment.
- Tapered form: Kagan tapered Pareto, corner = Mmax, HARD-TRUNCATED AND
  RENORMALIZED at Mmax (standard conditioning on M<=Mmax; our construction,
  not Kagan's — OQ's TaperedGRMFD cuts without renormalizing, difference
  ~0.4% in lambda; needs its one methods sentence). Both forms end at Mmax;
  no tail (no admissible fault area beyond).
- mu = 30 GPa (consistency with crustal SSM). v_conv per segment, TEAM
  INPUT (Angermann defaults). chi Scholz & Campos +/- 0.1.
- MMIN_HAZ = 6.5 (user decision; no distributed interface component below).
- Mmax = M_obs enforced by the s04 [mmax] guard (top-3 catalog events per
  segment printed; hard stop if catalog exceeds config). seg2 must carry
  ~9.0-9.1 (1730 Valparaiso per catalog). Thingbaijam-2017 admissible Mmax
  kept as a VALIDATION column only (mmax_adm in moment_closure.csv);
  expected to flag seg1 (scaling under-predicts the Chilean giants — a
  documented finding, not a change).
- Weights 0.5/0.5 everywhere binary; chi 0.25/0.5/0.25.
- s05 writes NRML 0.4 DIRECTLY (no openquake import): OQ's sourcewriter
  spends minutes/source in check_complex_fault, which ENUMERATES EVERY
  RUPTURE (profiled: 44k ruptures for a small source) — redundant with the
  engine's own validation at job time. s06_check_oq (optional, OQ-dep)
  does surface-level validation only (~seconds).
- Rupture mesh: 10 km recommended (OQ "suspiciously large" at 5 km for the
  full-margin source; Mmin 6.5 rupture ~16x16 km so 10 km floats fine;
  spacing lives in job.ini only — no source rebuild to change it).
- Half-bin rule: EvenlyDiscretized min_mag = first bin CENTER
  (MMIN_HAZ + BIN_W/2 = 6.55). Verified in round-trip.

## Guards (all hard or printed; keep them)

- s00 area closure assertion; segments shapefile for team review.
- s01/s02 input fingerprint (sha256 + spans + counts).
- s01 removed_large.csv (M>=7 with parent attribution) + DC_KEEP_IDS.
- s02 band-rate audit on the proposed steps; COMPLETENESS empty -> s03
  refuses to run.
- s03 b_err > 0.15 warning; observed-MFD overlay + implied-rate table
  (the estimator decision evidence).
- s04 [mmax] guard (hard stop); moment closure ratio warning outside
  [0.3, 3] (the Costa-Rica Central-Pacific failure mode); weight closure
  assertion (sums to W_GEOM per family, 1.0 total).
- s05 per-source MFD-sum-vs-lambda check (2%); LT weight sum assertion,
  last branch absorbs rounding.

## Critical bug fixed here (relevant everywhere)

pandas Timestamp bottoms out at 1677-09-21: pd.to_datetime(...,
errors="coerce") silently NaT's 1513-1677 events. Bit three times: (a)
sub_interface s01 would have dropped historical events (fixed: string-
slice decimal years); (b) upstream classify_events pre-1930 rule silently
exempted the 1575/1615 events -> the 1575 M9.1 leaked into intra_slab
(fixed upstream, regression print added); (c) merge_catalogs duplicate
detection cannot match pre-1677 events (OPEN — historical duplicates
possible, check merged catalog; also NaT sorts last).

## Hazard / postprocessing

- job_cities.ini: 7 cities (Iquique..Valdivia), vs30 380, comma-sep sites,
  investigation_time=1 with poes 0.002105/0.000404 (475/2475 yr) — change
  BOTH if switching to 50-yr convention.
- OQ realization ordering: by full_lt/sm_data = source models sorted
  ALPHABETICALLY BY FILE NAME (not LT order); gsim branches cycle within
  each block; sm_data names are a bytes repr of a list. post_process
  groups by contiguous blocks and takes within-block GMM weights FROM the
  stored rlz weights (verified structurally: block sums == sm weights,
  identical normalized pattern across blocks) -> handles any number of
  GMM axes (interface x intraslab). Guard refuses on mismatch — trust it.
- process_sub_branches.py (= post_process.py): GMM-collapsed per-source-
  branch curves + envelope + weighted mean + previous-model reference
  (calc 1642) + 475/2475 lines. PLOT_GMMS mode: per-GMM curves for
  single-source-model runs. RUN_LABEL sets titles.
- First real 16-branch result (Iquique): spread dominated by the
  GEOMETRY x RATE interaction — segmented-geodetic >> all non-segmented
  (both rate models coincide margin-wide) >> segmented-seismic. The
  northern slip deficit expresses only when segmentation confines the
  budget. chi and MFD form = fine structure only (collapse candidates).

## Sensitivity campaign (designed, pending)

Tree axes carry: rate model (x2-5 at M7.5+), geometry (redistributes),
MFD form (small), chi (+/-13% — smallest). NOT carried, measured larger:
b via MMIN_FIT x decluster x estimator (b 0.75-1.05 => x2-3 at M8, shared
by BOTH branches), locked depth (area + distance-to-site), historical
completeness, Mmax(seg2), mu. Plan: 16-branch reference + OAT variants via
RUN_TAG at 7 cities, PGA 475/2475, tornado per city. Pre-stated rules:
collapse tree axes with <~5% range everywhere; promote non-tree parameters
exceeding the smallest surviving axis (b is the promotion candidate) or
document exclusion. This study IS the epistemic justification.

## Open items

- Run the campaign; collapse/promote per the rules.
- seg2 MMAX update from the real catalog (guard will force it).
- 1962/1998 decluster review; team sign-off on boundaries, v_conv, chi.
- merge_catalogs pre-1677 duplicate check (upstream).
- GMM tree for the final model (interface: AG2020/Parker/Kuehn per
  original tree; watch the swap-experiment footgun: the interface TRT
  branchset briefly carried Montalva-SSlab).
- Deferred: shared ssm_lib consolidation (three copies); documented debt.