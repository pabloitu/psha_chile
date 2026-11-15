# GM1: ground-motion residuals for the subduction GMMs

Brief written 15 Nov 2026 (Pablo, chat session). Self-contained; read it fully before starting.

## Why
The GMM choice is the largest epistemic term of the hazard (LEARNINGS, GMMs and sites). The tree has four subduction GMMs at equal weights and DECISIONS says "no residual analysis" (Oct). Pablo reopened that on 15 Nov: this task produces the evidence for a later decision on GMM selection and weights. It changes nothing in the tree.

Not a conflict with DECISIONS: the lines "Equal weights, no residual analysis" and "Idini et al. (2017) and BC Hydro out" stay as they are; this task tests GMMs (those two included) and proposes nothing into DECISIONS. Do not stop on them.

## Scope
- Interface and in-slab only. No crustal GMMs, no crustal or outer-rise records.
- Only GMMs that exist in the installed OpenQuake (conda `psha_renta`). Nothing new is implemented; Contreras & Boroschek (2015) is therefore out.
- Intensity measures: PGA, SA(0.2), SA(1.0). Code written so that a period is one entry in a list.
- Work in a new folder `psha_chile8/gmm/` (`gmm/NOTES_data.md` is already there: read it first, it has what was found in the data). Other sessions may be running in psha_chile8 (B12, D16b, S1): touch nothing outside `gmm/` except the appends listed under "At the end".
- This task is light (minutes). Run everything yourself, tables and figures included.

## Inputs
- Strong-motion flatfiles of Bastías et al. (2026), in `/data/PyCharmProjects/psha_chile/data/ground_motion/`: `Flatfile_chileanEvents_v11.csv`, `Flatfile_chileanSiteStation_v7(1).csv`, `Flatfile_chileanRecord_v10.csv` (181 MB), `README-1.pdf` (field list). Paper: `/data/PyCharmProjects/psha_chile/refs/gmm/`. Missing values are `-999`. Vector fields are strings like `['0.01'; '0.05'; ...]`.
  - Copy the three CSVs to `psha_chile8/data/ground_motion/` as dated files (`_2026-11-15`), add them to `.gitignore` and to `data/SHA256SUMS`, one row each in DATA.md (same way as the Riedel-Hornig file).
- Frozen catalogue: `catalog/frozen/2026-11-14/catalog_2026-11-14c.csv` (all magnitudes, 204 956 events). Columns used: `event_id, time, lon, lat, depth, depth_sigma, depth_kind, mw, mw_kind, w_interface, w_inslab, w_crustal, w_outer_rise, cls, sub_inslab, strike1, dip1, rake1, strike2, dip2, rake2`.
- OpenQuake from the environment (`import openquake`); write its version into the report. Do not list or open the `oq-engine/` folder; read GMM docstrings through Python (`inspect`, `get_available_gsims()`).

## Step 1: record table (`gmm/build.py` → `gmm/tables/records_2026-11-15.csv`)
One row per record, with everything a GMM needs. Rules:

1. Match flatfile events to catalogue events: nearest in time within ± 90 s and 150 km; second pass for the rest within ± 330 s, 50 km and |ΔMw| ≤ 0.3 (some flatfile origins are about 65 s or 300 s late). Report the unmatched events.
2. Two flatfile events on one catalogue event are one earthquake (12 pairs, listed in `NOTES_data.md`): merge them, one record per station, taken from the flatfile entry closest in time to the catalogue origin.
3. Mw, hypocentral depth and class come from the catalogue, not from the flatfile.
4. Drop events with |Mw flatfile − Mw catalogue| ≥ 0.5 and write them to `gmm/tables/review_mw.csv` (22 expected; four are aftershocks inside the coda of the 2014 and 2015 mainshocks).
5. Class:
   - `cls` interface or in-slab: used as is.
   - `cls` split (no weight ≥ 0.8): dropped, unless Mw ≥ `BIG` (setting, 6.5); then the class with the larger weight, if that is interface or in-slab.
   - crustal, outer rise, unclassified: dropped.
   - Keep `sub_inslab` (shallow, intermediate, Jujuy nest) as a column.
6. Base selection: Mw ≥ 5.0, Rrup ≤ 300 km, RotD50 present, period usable: T ≤ 1/(1.25 f_lc), f_lc the larger low-cut of the two horizontal components (PGA always usable).
7. Observed values: RotD50. PGA = `PSa_RotD50` at 0.01 s. No conversion between component definitions; state this in the report.
8. Distances `Rrup, Rjb, Rhyp, Repi` as given in the flatfile. Flag events whose flatfile and catalogue hypocentres differ by more than 30 km horizontally or 20 km in depth (`loc_flag`).
9. Site: `vs30` = `StationVs30_m_s`; `vs30measured` = (`Vs30Ind` == 1); station `f0_HVSR`, `A0_HVSR`, `TypeCurveHVSR` carried along.
10. Rupture parameters not in the flatfile:
    - `rake`, `dip`, `strike`: from the catalogue mechanism. Interface: the plane dipping shallower. In-slab: the steeper plane. No mechanism: interface dip 20°, rake 90°; in-slab dip 45°, rake −90°.
    - `width`: OpenQuake scaling relations (`ThingbaijamInterface` for interface, `StrasserIntraslab` for in-slab), aspect ratio left to the relation.
    - `ztor`: for the 14 events with stored rupture nodes (`Rupture_Lat_Lon_Dep_deg_deg_km`), the shallowest node. Otherwise hypocentre in the middle of the width: `ztor = max(depth − 0.5·width·sin(dip), 0)`.
    - `rx`, `ry0` are not needed for subduction GMMs; if a kept GMM asks for one, say so and leave that GMM out.
11. `backarc`: True for stations east of the volcanic front. Use the arc definition already in the project (the crustal sub-classes forearc / arc / backarc of `catalog/classify.py`; copy what you need). Report how many stations and records are flagged.
12. `rvolc` = 0 for every record (no volcanic-path model). `z1pt0`, `z2pt5`: the value that makes the basin term of that GMM zero (the model's own default from Vs30, or −999 where OpenQuake supports it). Write per GMM what was used.
13. Idini et al. (2017) `soiltype`: from f0 and the HVSR amplitude with the class definitions of that model (see its OpenQuake docstring). Stations without f0 get no soil type.

Print and save a count table: events and records per class at each step of the selection.

## Step 2: candidate list and screening (`gmm/screen.py` → `gmm/tables/screening.csv`)
- Start from every GSIM class of the installed OpenQuake defined for subduction interface or in-slab.
- Collapse variants to their base model: scaled, epistemic (High / Low / Upper / Lower), NSHMP, country- or region-adjusted copies for other regions (Cascadia, Japan, Swiss, …) are not separate candidates.
- Regional options: where a model has a South America option (Parker et al. 2020 `region="SA"` with `saturation_region="SA_S"`, as in our tree; Kuehn et al. 2020; Abrahamson & Gülerce 2020), test both the global and the South America version as two candidates. Read the constructor arguments; do not guess them.
- Arteta et al. (2021): the Vs30 variants.
- Apply the criteria of Cotton et al. (2006), as listed in the CSN report (MASCSN26, p. 88): (1) irrelevant tectonic regime, (2) not published in a peer-reviewed journal, (3) documentation or data insufficient, (4) superseded by a newer model of the same authors, (5) frequency range inadequate, (6) inadequate functional form, (7) regression or coefficients inappropriate. Add two practical ones: (8) lacks PGA, SA(0.2) or SA(1.0); (9) needs an input we cannot derive.
- Judge from the OpenQuake docstrings and what is firmly known about the model. Where unsure, keep the model and write "unsure".
- Always kept, whatever the screening says (flag them if a criterion fails): the current tree (AG20, Parker SA_S, Kuehn, Montalva 2017) and the CSN 2026 models available in OpenQuake (Idini 2017, Montalva 2017, Youngs 1997, Zhao 2016), and the BC Hydro model (Abrahamson et al. 2015, as in the GEM South America set).
- `screening.csv`: one row per OpenQuake class: class name, model, interface / in-slab, kept or dropped, criterion number, one-line reason, required site / rupture / distance parameters, component definition, has total σ only or τ and φ.

## Step 3: residuals (`gmm/residuals.py`, entry script `gmm/run.py`)
Evaluate each kept GMM with `openquake.hazardlib` contexts (one context per event is fine), ln units.

- Total residual r = ln(obs) − μ; normalised z = r / σ_total.
- Between- and within-event split with the GMM's own τ and φ (Abrahamson & Youngs 1992): for event e with n records, δB_e = τ² Σ r / (n τ² + φ²), δW = r − δB_e; normalised by τ and φ. GMMs with total σ only: total residuals only.
- Also estimate τ and φ from the data (random intercept per event on r, maximum likelihood; `statsmodels` if installed, otherwise a short own likelihood) and compare with the model's values.
- Per GMM, class and intensity measure: N records, N events, mean and standard deviation of z, mean bias in ln units, τ and φ (model, data).
- Trends: δW (or r) against Rrup and Vs30, δB_e (or event mean) against Mw and depth: binned means with standard errors, and the slope of a straight line with its standard error.

## Step 4: scores (`gmm/scores.py`)
- LLH (Scherbaum et al. 2009): LLH = −(1/N) Σ log₂ g(x_i), g the normal density of the GMM (μ, σ_total) at the observation. A standard normal sample scored by its own model gives 2.05.
- LLH weights: w_k = 2^(−LLH_k) / Σ 2^(−LLH_j), over the kept GMMs of a class. Reported as evidence only.
- EDR (Kale & Akkar 2013). For record i: D = obs − model is normal with mean μ_D = a_i − μ_i and σ_D = σ_i. |d|max = max |μ_D ± 3σ_D|; bins d_j of width dd = 0.01 from dd/2 to |d|max; MDE_i = Σ_j |d_j| · [P(|D| < |d_j| + dd/2) − P(|D| < |d_j| − dd/2)]. κ = DE_orig / DE_corr, with DE_orig² = Σ (a_i − μ_i)² and DE_corr² = Σ (a_i − μ_c,i)², μ_c the model medians corrected by the straight line fitted between observed and predicted values. EDR² = κ · (1/N) Σ MDE_i². Report MDE (√ of the mean square), κ and EDR.
- The LLH and EDR formulas above are written from memory. If `refs/gmm/` holds the papers, check the code against them and cite equation and page in the report; if not, say "not checked against the paper" in the report. If `openquake.smtk` imports in the environment, compare your LLH and EDR with it on one GMM and report the difference; do not depend on it.
- Uncertainty: bootstrap over events (200 resamples) for LLH and EDR; report the 16–84 % range and, per class and intensity measure, how often each GMM ranks first.
- Common data: the main ranking uses the records every kept GMM can be evaluated on. GMMs that lose records (Idini without soil type) are also scored on their own set, in a second table.
- Subsets, same scores: (a) base; (b) Mw ≥ 6.5; (c) events from 2017 on (not in the data of the Chilean and NGA-Sub models); (d) measured Vs30 only; (e) without `loc_flag` events; (f) in-slab shallow and intermediate separately; (g) `backarc` all False; (h) `ztor` = hypocentral depth.

## Outputs
- `gmm/tables/`: `records_`, `screening.csv`, `review_mw.csv`, `residuals_summary_`, `scores_`, `scores_subsets_`, `trends_` (dated `_2026-11-15`).
- `gmm/figures/` (house style: Ubuntu font, `palette.py`, pituPLOTS, display names of the models as "Montalva et al. (2017)", no class names from code):
  1. data: Mw against Rrup per class, measured and inferred Vs30 marked; histograms of depth and Vs30.
  2. per class and intensity measure: one panel per GMM with z histogram against the standard normal.
  3. per class and intensity measure: residual trends against Mw, Rrup, depth, Vs30, GMMs as small multiples, binned means on top.
  4. summary: LLH and EDR per GMM, class and intensity measure, with the bootstrap range; current tree marked.
  5. τ and φ: model against data.
- `gmm/REPORT_GM1.md`: data and selection counts, screening table with reasons, score tables, what the subsets change, what cannot be tested with these data (two in-slab events above Mw 7, no station east of 68° W, three south of 46° S, backarc terms, basin terms), every assumption of step 1 with its effect. Plain language. No proposal of weights: the numbers only.
- Tests (`gmm/tests/`, `pytest` from `psha_chile8/`): parsing of the vector fields; LLH of a standard normal sample ≈ 2.05; EDR of a perfect model below that of a biased one, κ = 1 without trend; the event split recovers known τ and φ on a synthetic set; one GMM evaluated on three hand-made records equals a direct `hazardlib` call; duplicate merge on the pair 20140403024315 / 20140403024815.

## Style and rules
- CLAUDE.md applies: settings at the top of the entry script, minimal inline comments, section comments as `# text`, short names, NumPy docstrings for important functions only.
- No git. Suggested `git add` lines and a commit message without Claude signature go into the WORKLOG entry.

## At the end
Re-read each file right before appending; other sessions write to them.
- WORKLOG.md: one appended entry (what was done, commands, open questions, proposed LEARNINGS lines).
- PLAN.md: append a section "GM. Ground-motion models" with "GM1 residuals of the subduction GMMs on the Bastías et al. (2026) database (`tasks/GM1_gmm_residuals.md`, `gmm/REPORT_GM1.md`)", ticked when the report exists, and an open box "GM2 GMM selection and weights (Pablo)".
- DATA.md: rows for the three flatfiles and for `records_2026-11-15.csv`.
- FIGURES.md: rows for figures 1 and 4.
- REFERENCES.md: rows for Bastías et al. (2026), Cotton et al. (2006), Scherbaum et al. (2009), Kale & Akkar (2013), Abrahamson & Youngs (1992) and each kept GMM (citation from the OpenQuake docstring), marked as not in `refs/` where the PDF is missing.
- Do not edit DECISIONS.md or LEARNINGS.md.

## Done when
`pytest` passes, the tables and figures exist, `REPORT_GM1.md` is written, and the appends above are in.
