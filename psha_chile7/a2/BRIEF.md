# A2 night run: completeness, b, a and floor methods, benchmarked and run on the frozen catalog

Written 3 Nov 2026 for an unattended Claude Code session on pansito. Read all of it before the
first command. Work from the repository root `/data/PyCharmProjects/psha_chile`.

## Purpose

Task A2 of the plan is to *decide* the fit method per tectonic class. This run does not decide.
It produces the evidence Pablo decides from in the morning:

1. the candidate methods, implemented and unit-tested;
2. a benchmark on synthetic catalogs with a known truth, built to have the problems of the real
   catalog; this is the objective ranking of the methods;
3. every method combination run on every class of the frozen catalog, reported next to the
   benchmark;
4. one report, `psha_chile7/a2/MORNING.md`.

Never write that a method "is chosen", "is best for the model" or similar. Write what the
benchmark shows and what the real-catalog numbers are.

## Hard rules

- **No git.** Pablo's settings deny git commands that change the repository (add, commit,
  switch, checkout, ...). Do not run them or work around them. The run happens on branch
  `a2-night`, which Pablo created; he commits in the morning. Read-only git (status, log, diff)
  is fine.
- **Write only** under `psha_chile7/a2/` (code, tests, report) and `psha_chile7/outputs/a2/`
  (tables, figures, logs). Every other file is read-only: `psha_chile7/lib/`, the class
  pipelines, `cat_handler_2/`, `data/`, `results/`.
- **Catalog.** Read only `results/cat_handler_2/frozen/2026-11-03/catalog.csv` (sha256 starts
  `36ae7ecc`). Check the hash once at the start and stop if it differs.
- **Python environment.** Run everything in Pablo's `psha_renta` environment: prefix commands
  with `conda run -n psha_renta` (e.g. `conda run -n psha_renta python -m pytest ...`), or use
  that environment's interpreter directly. Check in P0 that numpy, scipy, pandas and matplotlib
  import there; stop with a note in PROGRESS.md if they do not.
- **No new packages.** The environment has numpy, scipy, pandas, matplotlib and
  `SeismoStats/` (vendored). If something is missing, write it in numpy/scipy. No network.
- **Settings before results.** Every method parameter (periods, bands, test levels, STAI
  window, bootstrap sizes, seeds) goes into `psha_chile7/a2/settings.py` before phase 4 starts.
  From phase 4 on, change a method only to fix a bug, and log the fix and its reason in
  `PROGRESS.md`. Do not tune anything on the real-catalog results.
- **Checkpoint after each phase** instead of committing: all code, tables and figures of the
  phase written to disk, and one line appended to `psha_chile7/a2/PROGRESS.md`: time, phase,
  done / partial / skipped, the files written, one sentence. A later phase must not overwrite an
  earlier phase's outputs.
- **Time budget** (total about 7 h): P0 15 min, P1 1 h, P2 2.5 h, P3 1.25 h, P4 1.25 h, P5 45 min.
  When a phase runs over, write what exists, mark the rest "not done: reason", checkpoint, move on.
  The report at the end matters more than any single method.
- **Stuck rule.** A failing test or estimator you cannot fix in 20 minutes: mark that method
  "broken: reason" in the results, keep its code, continue with the others.
- **Tests.** `python -m pytest psha_chile7/a2/tests -q` must pass at every checkpoint (a test of a
  method marked broken may be marked xfail with the reason).

## Code style (Pablo's)

Few files, short names, few private helpers. Minimal inline comments; section comments only as
`# text`, no decorative lines. Numpy-style docstrings for the key functions only. Code that reads
like a person wrote it. Figures: `cat_handler_2/palette.py` (`palette.apply()`, `CLASS`,
`FAMILY`, `NAME`); import it the way `psha_chile7/paths.py` does. Reuse `psha_chile7/lib/gr.py`
(Weichert, `weichert_joint`, `kijko_smit`, `since`, `complete`) and `lib/cat.py` (`load`,
`decyear`) by import; do not copy them. `psha_chile7/tests/synth.py` shows the style of a
synthetic generator written without `lib.gr`.

## Context you need (from FITS_method.md and FITS_literature.md, condensed)

The catalog is a merge of agencies (Cabello et al. 2025). Before 2000 most small events come
from ISC / USGS, after 2000 from the Chilean network (CSN). Four problems:

1. **Thinning, not a cut.** Before 2000 many M4.0–4.6 events are present but a large share of
   M4.5–5.4 is missing. Shape-based Mc methods (max curvature, KS) return Mc 4.2–4.4 for
   1986–2000 and miss it; rates per band and period show it (forearc M5.0–5.4: 0.4–0.7/yr
   before 2000, 2.1 after).
2. **Agency magnitudes differ.** Against GCMT Mw: ISC about −0.3, CSN −0.1, USGS +0.1. ISC-only
   events (many 1964–1990s) sit about 0.3 low. Not corrected in the catalog (settled); its
   effect on Mc and b is to be measured.
3. **Sequences and unequal windows.** Rates come from the full catalog (settled for in-slab and
   crustal; recommended for interface). With a variable-Mc table the small bins are observed
   only in recent, sequence-rich years (Maule 2010, Iquique 2014, Illapel 2015), so Weichert
   raises b (forearc b 1.18–1.58 on all periods against 0.75–0.97 on single periods).
4. **The floor is chosen by eye** and moves the rate at the controlling magnitude by ×0.5–1.9.

Recommended path from the literature notes (topics 1–5), which this run implements and tests
against alternatives:

- **Completeness in time:** fixed periods from network history (before 1964, 1964–1979,
  1980–1999, 2000–2006, 2007–2013, 2014–). Inside each period a *detection fraction* per
  0.5-unit band against a reference band complete in all periods of the window (EPRI / CEUS-SSC
  2012 "probability of detection"); cap at 1, flag values > 1 (magnitude shift, not detection);
  effective observation time per band = Σ fraction × period length. Change-point check only.
- **Completeness without declustering:** judge it on the *split of counts between bands within
  a period* (binomial / multinomial against the GR shares), not on rates between periods. Mask
  short-term aftershock incompleteness (STAI) windows after large mainshocks.
- **Completeness in space:** at most two or three along-strike zones per family; optional
  tonight (see phase 4).
- **b:** from magnitudes only, pooled over sub-catalogs with different Mc (Kijko and Smit 2012;
  Taroni 2021: subtract each sub-catalog's Mc, the shifted values follow one exponential, use
  Aki–Utsu with the binning correction). Counts are not used, so sequences cannot tilt b.
  b-positive (van der Elst 2021) as a table-free check on the modern period.
- **a:** count above the floor divided by the effective time, b fixed; uncertainty from a
  negative binomial (NBD), dispersion from yearly counts of the modern complete period.
- **Floor:** lowest floor where the pooled shifted magnitudes pass a binned Lilliefors test
  (Herrmann and Marzocchi 2021; plain Lilliefors overestimates the cutoff for binned data, so
  build the null distribution by simulating binned exponentials) *and* b stays within 1 σ over
  the next 0.5 units (MBS). Record both.
- **Tests:** shape test per (period, zone) sub-catalog: band counts against the multinomial
  shares of the fitted b given the sub-catalog's count, MLL statistic summed, reference
  distribution by simulation. Number test: observed against expected counts, NBD, two-sided 95 %.
  Large events: N(M ≥ 7) over a documentary period (default since 1900) against expectation, NBD.

## Classes

Read the families with `lib.cat.family(path, fam)` (it checks the family column against
`params.FAMILIES`). Fit per class: interface `slab_interface` (whole margin; `patagonia_interface`
reported but too small to fit alone), in-slab `intra_slab`, `slab_deep`, `deep_nest`, crustal
`forearc`, `intraarc`, `backarc` (`patagonia_crustal`: report counts only). Catalog end: the
last event time (2022-12-31).

## Phases

**P0. Setup (15 min).** Check the catalog hash. Count events per class, per period and per
0.5 band (M ≥ 4.0) into `outputs/a2/real/counts.csv`. Write `a2/settings.py` with the periods,
bands and seeds. Locate the completeness tables the current models use (read-only: the class
configs under `interface/`, `intraslab/`, `crustal/`, `forecast/decisions.json`) and record them
as baseline C0 where found.

**P1. Synthetic generator (1 h).** `a2/synth.py`, independent of the methods under test. A
true doubly truncated GR (b, rate, Mmax) over 1900–2023, then the observation:
- S0: Poisson, hard completeness table, exact magnitudes;
- S1: S0 + thinning: detection probability per period a logistic in M (mc50 and width per
  period, wide before 2000), not a cut;
- S2: S1 + clustering: Poisson mainshocks plus aftershocks with Omori decay and productivity
  10^(α(M−Mc)), magnitudes from the same GR, Fano factor of yearly counts 5–15;
- S3: S2 + agency shift: before 2000, half of the events recorded 0.3 low;
- S4: S3 + STAI (detection lowered for days after M ≥ 7) + rounding to 0.1.
Two regimes: rich (interface-like, about 1 000 events M ≥ 5.5 in 120 yr) and poor
(backarc-like, about 50). b true 0.9 and 1.1. Fixed seeds. Tests: on S0 the generator's own
truth is recovered (counts within Poisson error, Aki b within 2 σ on complete data).

**P2. Methods (2.5 h).** One small module per step in `a2/`:
- completeness: C1 fixed periods with a hard Mc per period (max curvature + 0.2); C2 fixed
  periods with detection fractions and effective times (recommended); C3 Stepp-type start year
  per band (check); C0 the current tables where found (real catalog only);
- STAI mask: on / off (window after each M ≥ 7, e.g. masking events below
  M_main − 4.5 − 0.75 log10(t in days) for t ≤ 100 days; state the rule in settings.py);
- b: B1 Weichert with the table (`lib.gr.weichert` / effective times); B2 pooled shifted
  magnitudes (Kijko–Smit / Taroni, binning correction); B3 b-positive (check only);
- floor: F1 binned Lilliefors (simulated null); F2 MBS b-stability; F3 fixed floors
  4.5, 5.0, 5.5, 5.8 for comparison;
- a: count over effective time with b fixed, NBD interval;
- tests: shape (MLL), number (NBD), large events (NBD).
Unit tests for each on S0 / S1 with known answers.

**P3. Synthetic benchmark (1.25 h).** All combinations C1–C3 × B1–B2 × F1–F3 × STAI on/off on
S0–S4, both regimes, both b, 20 seeds. Score: bias and RMSE of b; of N(≥ floor), N(≥ 6),
N(≥ 7) per year; coverage of the 90 % intervals; failure rate. Table
`outputs/a2/synth/scores.csv` and one heat-map figure (method × scenario, bias of N(≥ 6)).

**P4. Real catalog (1.25 h).** Every combination on every class. Per class one row per
combination in `outputs/a2/real/fits.csv`: completeness (table or effective times), floor F1 and
F2, b ± σ (B1, B2), b-positive, rate N(≥ floor), N(≥ 6), N(≥ 7) with intervals, shape / number /
large-event p-values, flags (detection fraction > 1, test failure, method broken). Then, if time
allows, in this order:
1. **in-slab sensitivity** (open decision 3 of the catalog): the in-slab fits again with the
   unresolved events of rules `unk_deep` and `deep_mid` over a deep slab counted as in-slab
   (`cls_rule` column), recommended combination and C1/B1 only;
2. **agency check:** b per agency subset (CSN, ISC, USGS) at the same Mc, per family;
3. **interface full vs declustered b** (`lib/dc.py`, gk74), recommended b estimator.

**P5. Report (45 min).** `psha_chile7/a2/MORNING.md`, at most about three pages:
1. What ran, what did not, and why (from PROGRESS.md).
2. Synthetic benchmark: the ranking table (top combinations by bias and coverage of N(≥ 6),
   per scenario S4 and per regime), and where each method fails.
3. Per class: a compact table of the combinations that do well on S4, with their real-catalog
   b, floor, N(≥ 6), N(≥ 7) and test results; and the spread across *all* combinations
   (min–max of N(≥ 6)), which is the method uncertainty.
4. Where methods disagree on the real catalog by more than their intervals, per class.
5. The sensitivity and checks of P4, if done.
6. Figures: at most 12, each with one line on what it shows. Per class one 2×2 figure: time
   against M with the period limits; b against floor per estimator with bands; observed
   cumulative MFD (per period, effective-time weighted) with the fits; test results.
7. Open questions for Pablo, as questions.

Use plain language, numbers with units, no decision words.

## Done when

`psha_chile7/a2/MORNING.md` has every section of P5 filled or marked "not done: reason",
`conda run -n psha_renta python -m pytest psha_chile7/a2/tests -q` passes with its output shown,
and `PROGRESS.md` has a line for every phase.
