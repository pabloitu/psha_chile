# Magnitude error and rates: what other hazard models do

Notes of 15 Nov 2026 from seven PDFs in `refs/catalogs/`, read for the question behind `DECISIONS.md:52` and
`ceus()` in `b9_lib.py`. β = b ln 10, σ = standard error of the magnitude.

## The equations (CEUS-SSC 2012, Volume 1, section 3.3.1; read 15 Nov from `ceus_vol_I.pdf`)

With γ² = β² σ² / 2 and M̂ an observed magnitude with error σ:

- 3.3.1-1, 3.3.1-2 (Tinti and Mulargia 1985): counts of M̂ are too high by exp(γ²); `N(true) = N(M̂) exp(−γ²)`.
  b is not affected when σ is the same for all events.
- 3.3.1-3 (EPRI 1988): the same result by moving magnitudes, `M* = M̂ − β σ² / 2`.
- 3.3.1-5: `E[M] = M̂ − β σ²`. Counts of E[M] are too low by exp(γ²) (3.3.1-11).
- 3.3.1-4, 3.3.1-6: from another size measure X by regression, `E[M] = E[M|X]` with no shift, and
  `M* = E[M|X] + β σ²[M|X] / 2`: the sign changes.
- 3.3.1-8: for a converted value `σ²[M|X] = σ²[M̂|X] − σ²[M|M̂]`, the regression scatter less the error of the
  reference Mw. Our relations do the same (`MAGNITUDES.md`, point 5).
- 3.3.1-9, 3.3.1-10: several measures X_i are combined by inverse-variance weights, plus `(R − 1) β σ²` for R
  measures.
- 3.3.1-12: `N* = exp(β² σ² / 2)`, one per event, summed in the bin of E[M] and divided by the completeness period.
  N* in the catalogue is computed once with b = 0.95 from a first analysis.

Why N* and not M*: with full completeness both work. When smaller magnitudes have shorter completeness periods, moving
magnitudes brings too few events in from the bin below. In their simulations M* gives N(≥4) low by 25 % (two-thirds
case) and 48 % (half case) and b low by 2–12 %; N* stays within 2 %. Volume 2 (section 5.3.2.5) says the same in
one line: event factors avoid "edge effects at the lower magnitudes". The simulations only cover E[M] from a
regression; the observed kind with the downward shift and a stepped completeness table was not tested there.

Observed Mw (272 events) are moved with 3.3.1-5; nominal σ 0.30 for 1920–1959, 0.15 for 1960–1975, 0.125 for
1975–1984, 0.10 from 1985. Old events with a magnitude from a special study (isoseismal areas, intensity fall-off)
take that value in preference to the project's own regressions. Rounding to 0.1 was only tested for its effect on
t-tests between agencies and ignored.

In the recurrence fit (Volume 2, 5.3.2) the N* are the counts of a binned Poisson likelihood. The fit also has weights
per magnitude bin, because conversions, completeness and the exponential shape are less reliable at low magnitude:
case A all bins 1 (weight 0.3), case B the lowest bin 0.1 (0.3), case E the lowest bin 0 and the second 0.3 (0.4).

`ceus()` in `b9_lib.py`: mode `ceus` is 3.3.1-5 with 3.3.1-12, mode `plain` is 3.3.1-1. Both agree with the report.
Mueller (2019) quotes the same two equations by number; his examples: 1871, felt area, σ 0.333, Mw = E[M] = 4.63,
N* 1.342; 2011 Mineral, observed Mw 5.65, σ 0.10, E[M] 5.63, N* 1.027. For b = 1, N* is 1.03 at σ 0.1, 1.27 at
σ 0.3, 1.94 at σ 0.5.

## Per model

| Model | What is done | Source |
|---|---|---|
| USGS NSHM, central and eastern US (2014, 2018, 2023) | CEUS-SSC method: conversions by least squares give M_e, counted by N* (rates go up); observed Mw shifted, then N* | Mueller 2019; Petersen et al. 2024 ("catalog … using the methodology of Mueller (2019)") |
| USGS NSHM, western US | The same procedure. mb, ML etc. are set equal to Mw and treated like observed magnitudes: shift, then N* (net rate down) | Mueller 2019 |
| USGS, unclear magnitude history | No correction: M_e = M, N* = 1, after Musson's (2012) caution. Rounding is not corrected | Mueller 2019 |
| Size of the effect, USGS | "overall rate adjustments are typically smaller than about 15–20 %", because the modern part with small σ dominates | Mueller 2019 |
| UCERF3 California | Mean rate of M ≥ 5 corrected for rounding and magnitude error with Felzer (2008); needs an assumed b and Mmax. The direct counts per magnitude bin are left uncorrected | Felzer 2013, Appendix L |
| UCERF2 California, the method | Error: each magnitude lowered by ΔM from Tinti and Mulargia's factor (the M* form, βσ²/2; eq. 4 as extracted has b², which is the same only for b = 1). σ 0.09 for GCMT, 0.111 after 1972, 0.222 for 1932–1972, 0.333 before 1932 unless published; σ 0.7 for some historical events would triple the rate. Rounding: each rounded magnitude replaced by a draw from the Gutenberg–Richter shape inside its rounding interval, 500 times; uniform rounding to 0.5 with b = 1 inflates rates 1.8 times | Felzer 2008, Appendix I |
| New Zealand NSHM 2022 | Monte Carlo: magnitudes de-rounded (Felzer 2008), then perturbed by their σ with the mean shifted down (Rhoades 1996). σ about 0.1–0.2 recent, 0.2–0.5 old. Used for N, with three N branches per b | Rollins et al. 2024 |
| New Zealand, the doubt | Many magnitudes are converted; in McGuire's (2004) framework the correction would then go up, not down (Musson 2012). With σ set to zero N(≥5) rises 16 % (4.83 → 5.60 per yr) and 14 % for the upper plate. They suggest branches without or with a different correction | Rollins et al. 2024, discussion |
| USGS, next model | Monte Carlo over b, Mc and each magnitude. True magnitude ~ Normal(M − βσ², σ) (Rhoades 1996); counting at that mean overcorrects; the unbiased shift is βσ²/2 (Tinti and Mulargia 1985; Rhoades and Dowrick 2000). N* still summed for converted events; default σ 0.2. I did not trace how the two are combined | Michael and Llenos 2026 |
| USGS, conversions | Orthogonal regression preferred to least squares for new CEUS conversions; the choice of conversion changes rates more than this correction. σ 0.1 for events left unconverted | Llenos et al. 2026 |
| Italy MPS19, Europe ESHM20 | No correction mentioned (texts read on the web, 15 Nov) | Meletti et al. 2021; Visini et al. 2022; Danciu et al. 2024 |

Musson (2012), read on the web: values from an ordinary regression of Mw on the native scale undercount (36 % in his
simulation), values from an orthogonal fit overcount (32 %) and need the reduction, like observed magnitudes. One
catalogue can fall anywhere in a wide spread, so the correction can also make it worse.

## What this means for B10 (options, not decisions)

- Our conversions are inverse fits, so they belong with the observed and "set equal" kinds: shift, then N*. This is
  what DECISIONS:52 says and what `ceus()` does. Mueller treats western US mb and ML the same way.
- Historical events with a magnitude from intensities or a complex history: Mueller applies no correction. In B9 the
  shift moved them by 0.2–0.9 units. An option is to leave these events uncorrected.
- The net effect of shift and N* on a rate equals one shift by βσ²/2 (Tinti and Mulargia; Rhoades and Dowrick; Musson;
  Michael and Llenos). The `plain` mode of `ceus()` gives the same rate without moving events between bins.
- Rollins et al. and Mueller both give the size as 15–20 % on rates at most; Rollins et al. propose a branch without
  the correction. B9 already has fits with and without.
- Rounding: corrected in California and New Zealand, not by the USGS. Not looked at in B9.
- Stepped completeness: the report's case against moving magnitudes applies to our tables. The shift of 3.3.1-5 can
  carry an old event below the magnitude from which its period counts (for example Mw 8.0 of 1750 moved to 7.5, where
  the table starts in 1820), and the event is lost. The `plain` mode keeps events in place. To check in B10 for the
  historical part of the interface table.
- Weights per magnitude bin as in CEUS-SSC are another way to stop the Mw 4.5–4.9 bins from steering the fit.

## Not read

Tinti and Mulargia (1985, BSSA 75, 1681–1697): `tinti_mulargia_1985.pdf` is their other paper of that year, on
catalogue completeness (Nuovo Cimento 42); the result is quoted in CEUS-SSC and Felzer. Rhoades (1996); Rhoades and
Dowrick (2000); Arabasz et al. (2016). Of CEUS-SSC Volume 2 only the passages on N* and the bin weights.
