# Task B11: fitting code, GR fitting methods compared, final fits

Input: the frozen catalogue `catalog/frozen/2026-11-14/catalog_2026-11-14c.csv` (read only).

Read first: `CLAUDE.md`, `PLAN.md` (B), `DECISIONS.md` (Statistics (B9), Magnitudes, Interface, In-slab, Crustal and faults, Logic tree), `LEARNINGS.md` (Completeness; b-value and rates; Fits pitfalls; the B9 lines), `explore/B9/REPORT.md` (sections 6–8), `explore/B9/STEP0.md`, `explore/B9/MAG_ERROR_REFS.md`.

Pablo allows you to edit, for step 0 only: `DECISIONS.md` (the 85 → 94 count), `catalog/REPORT_A3-A5.md`, `catalog/MAGNITUDES.md`, `catalog/RULES_LOCATION_MAGNITUDE.md`, `paper/CATALOG_SECTION_draft.md`. Do not change the frozen catalogue.

## Step 0: the step-0 audit of B9

Apply the corrections listed in `explore/B9/STEP0.md` to the files above, one by one, each checked against the frozen run (the 50 km check drops 94 events of Mw ≥ 4.5 in the domain, not 85). List in the WORKLOG what you changed and what you left (with the reason). Do not rewrite the documents beyond the listed points.

## Step 1: the magnitude σ, now that it sets event counts

Under DECISIONS every event counts exp(−β²σ²/2). With β ≈ 2.2, an event with σ 0.5 counts about 0.55, and with σ 1.1 about 0.07. Before any fit:
- table of σ by Mw kind (`direct`, `proxy`, `iscgem`, `centennial`, `cabello`, `rm18`, `a6`) and period, with the resulting weight; where each σ comes from (the source column, or a default set in `magnitude.py`);
- the ISC-GEM values of 1964–1975 with σ near 1: what the ISC-GEM uncertainty column says for them (quality D? a proxy?), and whether σ is the right reading of that column;
- what the weight does to the large events: per class and interface segment, N(≥ 7) and N(≥ 8) observed by count and by weight, before 1904, 1904–1975, from 1976;
- report, do not change: if a σ looks wrong, propose the correction for Pablo.

## Step 2: the fitting code

Turn the B9 pieces into tested code in `fits/` (not `explore/`): `b9_lib.py` (Weichert, bootstrap), `b9_9_magerr.py` (weight), `b9_10_mc_all.py` and `b9_11_autotable.py` (automatic table). Do not import from `explore/`. Files: `fits/table.py` (completeness table), `fits/gr.py` (estimators), `fits/run.py` (settings at the top, per class and segment), `fits/tests/`.

Tests on synthetic catalogues built like ours (the table of DECISIONS, class weights, magnitude σ per kind and period, 0.1 bins): each estimator recovers known b, a and N(≥ 5, 7, 8); the automatic table recovers a known table; the bootstrap intervals cover the true values at their nominal rate (report the coverage).

## Step 3: GR fitting methods compared

Same completeness table, weights and magnitude-error weight for all; per class and per interface segment.

| method | what it adds | note |
|---|---|---|
| Weichert, unbounded GR | current choice (DECISIONS) | reference |
| Weichert, doubly truncated GR at the Mmax of the class | the MFD the crustal and in-slab sources use (Mmax = observed + 0.2) | |
| Tapered GR, maximum likelihood with the table (Kagan 2002; Bird and Kagan 2004) | the interface MFD of DECISIONS (corner 9.6 fixed); corner free as a check | interface; also in-slab as a test |
| Aki–Utsu (Aki 1965; Utsu 1965) on the instrumental part only (Mw ≥ 5.0 from 1976), binning correction | the simplest estimate, no table | reference for b |
| Joint Mc–b fit, EMR (Woessner and Wiemer 2005) or Ogata and Katsura (1993), from 1976 | uses the incomplete part below Mc instead of cutting it | not run in B9 |
| Pooled b with shrinkage (hierarchical, or a Bayesian prior centred on the family b) | stabilises the small classes (arc, backarc, Patagonia, Jujuy nest) and the interface segments | LEARNINGS: a random-effects pooling was dropped for crustal before; report, do not adopt |
| Least squares on the cumulative counts | contrast only (known biased) | one line in the table |

Compare by:
1. recovery on the synthetic catalogues of step 2 (bias and interval coverage of b and N(≥ 7));
2. the large-event check (fitted against observed N(≥ 7), N(≥ 8), Poisson band), per class and segment;
3. b against the fit floor (5.0 to 6.0);
4. for truncated and tapered forms against unbounded: the likelihood (AIC), and N(≥ 7), N(≥ 8) — the difference is what the source models will see;
5. sensitivity to the split events (weight-1 only against all).

## Step 4: final fits

With the methods of DECISIONS (Weichert, unbounded GR, the automatic table, weights, magnitude-error weight, event bootstrap): b, a, σ_b, the covariance of (a, b), N(≥ 5, 6, 7, 8) with 5–95 % intervals, per class and per interface segment; Patagonia with the forearc b; backarc and Jujuy nest at the table floor. For the interface (DECISIONS, Interface): the (a, b) pairs at the 5th, maximum-likelihood and 95th percentile of N(≥ controlling M), weights 0.185 / 0.63 / 0.185. The alternatives of step 3 as a sensitivity table. Fits with and without the split events.

Outputs: `fits/tables/fits_<date>.csv` (one row per class or segment, every number above), `fits/tables/fits_sensitivity_<date>.csv`, `fits/FITS.md` (method, table, numbers, checks, the two known failures named in DECISIONS: intermediate in-slab before 1976, interface segment 32–26° S), figures in `fits/figs/` (frequency–magnitude per class with the table and the fits, large-event check, b against floor, method comparison), FIGURES.md rows for paper candidates, DATA.md row.

## Running and end of session

Claude Code runs it in full. WORKLOG entry as CLAUDE.md: step 0 changes; step 1 table and any proposed σ corrections; the method comparison in one table with a recommendation (options, not decisions); the final fits; proposed DECISIONS / LEARNINGS lines; commands; suggested `git add` and commit message (no Claude signature). PLAN: tick B10 (DECISIONS, Statistics), leave B11 for Pablo, ← on B11.
