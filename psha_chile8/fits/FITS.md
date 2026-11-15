# Fits: Gutenberg–Richter parameters per class and interface segment (B11)

15 Nov 2026. Input: `catalog/frozen/2026-11-14/catalog_2026-11-14c.csv` (read only; 57 853 events of Mw ≥ 3.5 in the domain, 5 463 of Mw ≥ 5.0). Code in `fits/`: `gr.py` (estimators), `table.py` (completeness table), `synth.py` (synthetic catalogues), `run.py` (final fits; settings and units at the top), `compare.py` (methods compared), `sigma.py` (magnitude σ report), `figs.py`, `tests/` (15 tests). Tables in `tables/`, figures in `figs/`.

Revised 15 Nov after Pablo's reply: the line is never open. Every unit is fitted with two shapes, tapered (preferred) and cut at Mmax; both stay in until the tornado. The interface branches come from the covariance of (a, b). Sections 3 to 5 are as first written; where section 4 says "reference" it is the open line with the b of the cut-line fit, which now is only a row of the sensitivity table.

Conventions. Magnitudes are 0.1 bin centres; N(≥ 7) is the yearly number in the bin 7.0 and above (Mw ≥ 6.95). An event counts in a class by its class weight times exp(−β²σ²/2). Intervals are 5–95 % of an event bootstrap (2 000 resamples). "Fitted / observed" compares the number the fit expects inside the completeness table with the weighted count there; bold = outside the Poisson 5–95 % band.

The a of each shape, with M a magnitude edge (N(≥ 7) uses M = 6.95) and Mmax the upper edge of the last bin (Mmax of the table + 0.05):
- cut at Mmax: N(≥ M) = 10^(a − b M) − 10^(a − b Mmax), the OpenQuake truncated Gutenberg–Richter convention;
- tapered: N(≥ M) = 10^(a − b M) × exp((M0(4.95) − M0(M)) / M0(corner)), with M0 the moment (Kagan 2002a, section 2.2.4). The line does not end at Mmax (Pablo, 15 Nov).

## 1. Method (DECISIONS, Statistics)

- **Completeness table, one for every class:** Mw 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500. `table.py` recomputes it from the catalogue and `run.py` stops if it differs. Instrumental steps: Mc per network window and region from Mw 3.5 (larger of b-stability and KS, largest region; `tables/mc_windows_2026-11-15.csv`). Historical steps: the rate rule on 0.5 bands and 5-year blocks against the instrumental line.
  - One setting is new: a historical step that reaches less than 10 years (two blocks) before 1964 is not kept (`MIN_BACK`). It replaces the dropping by hand of the steps "6.0 from 1960" and "6.5 from 1955" in B9.
- **Shapes.** Cut at Mmax: Weichert (1980) with the bins above Mmax left out. Tapered: maximum likelihood on the same bins with the corner fixed. Both with class weights, the magnitude-error weight on every event with the β of the fit (iterated) and a Poisson bootstrap of the events.
- **Mmax:** the segment values of DECISIONS for the interface (9.5 / 9.1 / 8.5 / 8.8; 9.5 for the whole margin), observed maximum + 0.2 for the other classes (events with class weight ≥ 0.5, historical ones included).
- **Corner:** 9.6 for the interface (DECISIONS). For the other classes the observed maximum: a tapered line with that corner has the moment rate of a line cut at observed + 0.2 (Kagan 2002b, eq. 12: corner moment = maximum moment × (β / Γ(2 − β))^(1/(1 − β)), β = 2b/3; for b 1.15 the corner is 0.21 below the cut, and our numerical value agrees: corner 8.04 for a cut at 8.2 in-slab; 7.19 forearc, 7.26 nest, 7.70 arc, 7.49 backarc, 7.79 Patagonia). The free-corner fits give 7.8–7.85 for in-slab and 7.5 for the nest.
- **Patagonia:** b of the forearc (each bootstrap replicate takes the forearc b of the same replicate), own rate. **Backarc, Jujuy nest:** own fit at the floor 5.0.
- **Full catalogue.** Nothing is declustered: the completeness table, the fits, the checks and the bootstrap use all events.
- **Checks:** Kijko and Smit (2012), b-positive (from 1976, Mw ≥ 5.0, differences ≥ 0.2), large events at Mw ≥ 7 and 8.

## 2. Final fits

`tables/fits_2026-11-15.csv` (one row per unit and shape; also var(a), var(b), cov(a, b), the rate at Mw 4.95, the checks, the weight-1 fit and the interface branches). `figs/fmd_classes.png`, `figs/fmd_interface_segments.png`, `figs/large_event_check.png`.

| unit | shape | Mmax | corner | b (sd) | a (sd) | corr(a, b) | N(≥ 5) | N(≥ 6) | N(≥ 7) | N(≥ 8) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| interface | tapered | 9.5 | 9.6 | 0.962 (0.017) | 6.16 (0.09) | 0.993 | 25.2 (24.2–26.2) | 2.75 (2.54–2.94) | 0.3 (0.261–0.339) | 0.0326 (0.0265–0.0391) | 54.5 / 49.7 | 17.0 / 14.7 |
|  | cut at Mmax | 9.5 | – | 0.962 (0.017) | 6.16 (0.09) | 0.993 | 25.2 (24.2–26.2) | 2.75 (2.55–2.95) | 0.3 (0.26–0.339) | 0.0319 (0.026–0.0381) | 54.4 / 49.7 | 16.8 / 14.7 |
| interface, 45.6–37° S | tapered | 9.5 | 9.6 | 0.915 (0.050) | 5.00 (0.25) | 0.993 | 2.94 (2.61–3.28) | 0.358 (0.284–0.43) | 0.0436 (0.0286–0.0604) | 0.00529 (0.0028–0.00865) | 8.2 / 9.4 | 2.7 / 2.5 |
|  | cut at Mmax | 9.5 | – | 0.915 (0.050) | 5.00 (0.25) | 0.993 | 2.94 (2.61–3.28) | 0.358 (0.284–0.43) | 0.0434 (0.0286–0.0601) | 0.00512 (0.00274–0.00826) | 8.1 / 9.4 | 2.7 / 2.5 |
| interface, 37–32° S | tapered | 9.1 | 9.6 | 0.996 (0.033) | 5.86 (0.17) | 0.994 | 8.48 (7.92–9.04) | 0.856 (0.74–0.97) | 0.0864 (0.0656–0.109) | 0.00869 (0.00578–0.0122) | 15.2 / 12.1 | 4.3 / 5.1 |
|  | cut at Mmax | 9.1 | – | 0.996 (0.033) | 5.86 (0.17) | 0.994 | 8.48 (7.92–9.04) | 0.856 (0.74–0.969) | 0.0859 (0.0654–0.108) | 0.00817 (0.00549–0.0114) | 15.2 / 12.1 | 4.3 / 5.1 |
| interface, 32–26° S | tapered | 8.5 | 9.6 | 0.934 (0.031) | 5.49 (0.16) | 0.993 | 7.41 (6.89–7.94) | 0.863 (0.749–0.974) | 0.1 (0.0773–0.125) | 0.0117 (0.00792–0.0163) | **17.0 / 9.6** | 4.5 / 2.6 |
|  | cut at Mmax | 8.5 | – | 0.934 (0.032) | 5.49 (0.16) | 0.993 | 7.41 (6.88–7.94) | 0.86 (0.747–0.97) | 0.0974 (0.0753–0.121) | 0.00849 (0.00592–0.0115) | **17.0 / 9.6** | 4.5 / 2.6 |
| interface, 26–17.6° S | tapered | 8.8 | 9.6 | 0.974 (0.041) | 5.58 (0.21) | 0.994 | 5.7 (5.23–6.16) | 0.606 (0.505–0.707) | 0.0644 (0.0458–0.0857) | 0.00682 (0.00411–0.0104) | 11.2 / 14.1 | 3.1 / 2.0 |
|  | cut at Mmax | 8.8 | – | 0.973 (0.041) | 5.57 (0.21) | 0.994 | 5.7 (5.23–6.16) | 0.606 (0.505–0.707) | 0.0636 (0.0454–0.0843) | 0.00595 (0.00365–0.00893) | 11.2 / 14.1 | 3.1 / 2.0 |
| in-slab, shallow | tapered | 8.2 | 8 | 1.150 (0.037) | 6.66 (0.18) | 0.996 | 9.24 (8.7–9.82) | 0.654 (0.555–0.755) | 0.0451 (0.0332–0.0586) | 0.00141 (0.0009–0.00208) | 6.7 / 7.5 | 0.7 / 0.6 |
|  | cut at Mmax | 8.2 | – | 1.153 (0.037) | 6.67 (0.18) | 0.996 | 9.24 (8.7–9.81) | 0.649 (0.551–0.749) | 0.0443 (0.0328–0.0573) | 0.00177 (0.00117–0.00252) | 6.8 / 7.5 | 0.9 / 0.6 |
| in-slab, intermediate depth | tapered | 8.2 | 8 | 1.153 (0.027) | 7.11 (0.13) | 0.997 | 25.3 (24.3–26.4) | 1.78 (1.6–1.97) | 0.122 (0.0992–0.148) | 0.0038 (0.00279–0.00508) | **18.1 / 29.4** | 1.8 / 0.9 |
|  | cut at Mmax | 8.2 | – | 1.156 (0.027) | 7.12 (0.13) | 0.997 | 25.3 (24.3–26.3) | 1.76 (1.58–1.95) | 0.12 (0.0976–0.145) | 0.00474 (0.00356–0.00619) | **18.3 / 29.4** | 2.5 / 0.9 |
| Jujuy nest | tapered | 7.4 | 7.2 | 1.226 (0.090) | 6.64 (0.45) | 0.998 | 3.74 (3.34–4.14) | 0.219 (0.148–0.3) | 0.00867 (0.00403–0.016) | 0 | 1.0 / 2.4 | – |
|  | cut at Mmax | 7.4 | – | 1.236 (0.090) | 6.69 (0.45) | 0.998 | 3.73 (3.34–4.13) | 0.214 (0.146–0.291) | 0.00957 (0.00475–0.0168) | 0 | 1.2 / 2.4 | – |
| crustal, forearc | tapered | 7.4 | 7.2 | 0.982 (0.056) | 5.41 (0.28) | 0.997 | 3.54 (3.24–3.85) | 0.364 (0.287–0.448) | 0.0252 (0.0159–0.0371) | 0 | 2.9 / 3.6 | – |
|  | cut at Mmax | 7.4 | – | 0.984 (0.059) | 5.42 (0.29) | 0.997 | 3.54 (3.24–3.85) | 0.356 (0.281–0.439) | 0.0259 (0.0169–0.0372) | 0 | 3.2 / 3.6 | – |
| crustal, arc | tapered | 7.9 | 7.7 | 1.002 (0.098) | 5.08 (0.49) | 0.995 | 1.31 (1.08–1.55) | 0.13 (0.0817–0.18) | 0.012 (0.00497–0.0217) | 0.00012 (3e-05–0.00029) | 1.6 / 2.2 | – |
|  | cut at Mmax | 7.9 | – | 1.004 (0.099) | 5.09 (0.50) | 0.995 | 1.31 (1.08–1.55) | 0.128 (0.0809–0.178) | 0.0116 (0.00497–0.0203) | 0 | 1.6 / 2.2 | – |
| crustal, backarc | tapered | 7.7 | 7.5 | 0.988 (0.068) | 5.25 (0.34) | 0.995 | 2.3 (2.01–2.61) | 0.235 (0.173–0.302) | 0.0209 (0.0118–0.0335) | 2e-05 (1e-05–4e-05) | 2.7 / 2.1 | – |
|  | cut at Mmax | 7.7 | – | 0.987 (0.071) | 5.25 (0.35) | 0.995 | 2.3 (2.01–2.61) | 0.234 (0.172–0.3) | 0.0205 (0.0118–0.0321) | 0 | 2.8 / 2.1 | – |
| crustal, Patagonia | tapered | 8.0 | 7.8 | 0.982 (0.056), forearc | 4.67 (0.29) | 0.970 | 0.64 (0.471–0.812) | 0.0666 (0.0457–0.0897) | 0.00659 (0.00391–0.0102) | 0.00014 (7e-05–0.00025) | 0.9 / 1.7 | 0.0 / 0.0 |
|  | cut at Mmax | 8.0 | – | 0.984 (0.059), forearc | 4.68 (0.30) | 0.972 | 0.64 (0.471–0.812) | 0.0659 (0.0451–0.089) | 0.00633 (0.00378–0.00978) | 0.00015 (7e-05–0.00025) | 0.9 / 1.7 | 0.1 / 0.0 |

- The two shapes give the same b (within 0.003; nest 0.010) and the same N(≥ 5) and N(≥ 6). At N(≥ 7) they differ by 0–4 % (nest: tapered 9 % lower). They part above: at N(≥ 8) the tapered interface lines are 2–15 % higher (segment 32–26° S 37 %, where the cut is at 8.5), the tapered in-slab lines 20 % lower.
- b and N(≥ 5) equal those of B9 section 8 to the third digit.
- N(≥ 7) and N(≥ 8) of a class whose Mmax is below that magnitude are 0 for the cut line and a remnant for the tapered one.

Tapered fits, all events and weight-1 events only (the cut-line values are the same within 1 %):

| unit | events (counted) | b Kijko–Smit | b-positive (pairs) | weight-1 events only: events | b | N(≥ 5) | N(≥ 7) |
|---|---|---|---|---|---|---|---|
| interface | 1 921 (1 511) | 0.915 | 0.879 (372) | 1 242 | 0.925 | 19.3 (× 0.76) | 0.272 (× 0.91) |
| interface, 45.6–37° S | 233 (178) | 0.935 | 1.032 (39) | 134 | 0.870 | 2.06 (× 0.70) | 0.0374 (× 0.86) |
| interface, 37–32° S | 644 (505) | 0.941 | 0.995 (132) | 408 | 0.956 | 6.36 (× 0.75) | 0.0779 (× 0.90) |
| interface, 32–26° S | 566 (445) | 0.896 | 0.882 (107) | 372 | 0.887 | 5.77 (× 0.78) | 0.0972 (× 0.97) |
| interface, 26–17.6° S | 421 (341) | 0.900 | 0.835 (92) | 300 | 0.947 | 4.68 (× 0.82) | 0.0596 (× 0.93) |
| in-slab, shallow | 1 133 (539) | 1.131 | 1.162 (96) | 314 | 1.153 | 4.96 (× 0.54) | 0.0239 (× 0.53) |
| in-slab, intermediate depth | 1 676 (1 476) | 1.165 | 1.167 (394) | 1 574 | 1.157 | 24.3 (× 0.96) | 0.115 (× 0.94) |
| Jujuy nest | 241 (216) | 1.220 | 1.138 (63) | 241 | 1.226 | 3.74 (× 1.00) | 0.00867 (× 1.00) |
| crustal, forearc | 788 (209) | 1.000 | 0.918 (22) | 91 | 0.969 | 1.43 (× 0.40) | 0.0108 (× 0.43) |
| crustal, arc | 103 (77) | 1.062 | 1.166 (21) | 78 | 0.994 | 1.21 (× 0.92) | 0.0115 (× 0.96) |
| crustal, backarc | 195 (136) | 0.974 | 1.133 (35) | 141 | 0.983 | 2.14 (× 0.93) | 0.0199 (× 0.95) |
| crustal, Patagonia | 41 (38) | – | – | 41 | 0.969 | 0.64 (× 1.00) | 0.007 (× 1.06) |

"Events" are the events with a weight above 0 inside the table; "counted" is their weighted sum.

**The two known failures** (DECISIONS, left as they are, for the discussion of the paper), with either shape:
- Intermediate in-slab at Mw ≥ 7: 18 fitted, 29.4 observed (by weight). 29.2 of the events are of 1904–1975 (21.9 after the magnitude-error weight), 20 of them converted Centennial values (σ 0.25–0.30); 7 since 1976. No fitting method removes it (section 4).
  - Where it sits, fitted against observed inside the table: Mw 7.0–7.4 in 1905–1963 5.5 / 10.3 and Mw ≥ 7.5 1.7 / 8.8; from 1976 Mw ≥ 7 6.1 / 6.9. The fit describes the modern record and the excess is all before 1964. 19 of the 32 old events are Abe mB values of the Centennial catalogue converted with Abe (1982).
  - The points above the line from Mw 6.3 to 7.5 in `figs/fmd_classes.png` are that same excess: the plot is cumulative, so every point below Mw 7 carries it. Per bin, Mw 6.0–6.9 fits (from 1976: 85 observed, 84 fitted).
  - In 1964–1975 the class has too few events at Mw 5.0–6.4 (110 against 173 fitted; mostly ISC-GEM proxy values). Not looked into further.
- Interface segment 32–26° S at Mw ≥ 7: 17.0 fitted, 9.6 observed. Here the fit expects more than observed. It passes from a floor of 5.4 up (b 0.97–1.01, 15 fitted) and with a pooled b (0.958, 15.0 fitted).

**Interface (a, b) branches** (DECISIONS, Interface): 5th percentile, maximum likelihood and 95th percentile of the rate at the controlling magnitude (8.8, at most Mmax − 0.3), weights 0.185 / 0.63 / 0.185. log10 of that rate is a − b (M − 0.05) plus a constant of the shape, so its standard deviation follows from the bootstrap covariance of (a, b), and the pair of a branch is the expected (a, b) given the rate at that percentile (± 1.645 sd along the covariance). a and b are correlated at 0.99, so the pairs lie on one line: the low branch has the higher a and b. Tapered fits; the cut-line pairs differ in the third decimal and are in the table.

| unit | controlling Mw | sd of log10 rate there | a, b: 5th percentile | maximum likelihood | 95th percentile | rate at the controlling Mw: 5th / ML / 95th |
|---|---|---|---|---|---|---|
| interface | 8.8 | 0.066 | 6.304, 0.991 | 6.165, 0.962 | 6.025, 0.934 | 0.0041 / 0.0053 / 0.0068 |
| interface, 45.6–37° S | 8.8 | 0.188 | 5.393, 0.995 | 4.996, 0.915 | 4.599, 0.834 | 0.00046 / 0.00093 / 0.0019 |
| interface, 37–32° S | 8.8 | 0.126 | 6.124, 1.050 | 5.859, 0.996 | 5.594, 0.942 | 0.00082 / 0.0013 / 0.0021 |
| interface, 32–26° S | 8.2 | 0.101 | 5.741, 0.985 | 5.493, 0.934 | 5.244, 0.883 | 0.0052 / 0.0076 / 0.011 |
| interface, 26–17.6° S | 8.5 | 0.143 | 5.905, 1.040 | 5.575, 0.974 | 5.246, 0.907 | 0.0013 / 0.0022 / 0.0038 |

Whether the branches stay is decided with the tornado.

## 3. The magnitude σ (step 1; a report, nothing changed)

`sigma.py`, `tables/sigma_kinds.csv`, `sigma_proxy.csv`, `sigma_iscgem.csv`, `sigma_iscgem_events.csv`, `sigma_large.csv`. Events of Mw ≥ 5.0 in the domain; counts with β = 2.2.

| kind | period | events | σ median (range) | count, mean (lowest) | where σ comes from |
|---|---|---|---|---|---|
| direct | 1964–2026 | 2 396 | 0.08–0.10 | 0.98 | set in `magnitude.py`: 0.08 GCMT, 0.10 W-phase and regional Mw |
| proxy | 1964–1975 | 328 | 0.27 (0.16–0.28) | 0.87 (0.83) | scatter of the conversion relation less the reference error, larger outside the fitted range |
| proxy | 1976–1989 | 754 | 0.24 (0.14–0.43) | 0.87 (0.65) | |
| proxy | 1990–2010 | 935 | 0.18–0.19 (0.14–0.43) | 0.89 (0.65) | |
| proxy | from 2011 | 244 | 0.21 (0.13–0.27) | 0.88 (0.83) | |
| iscgem | 1904–1963 | 240 | 0.23 (0.20–1.02) | 0.79 (0.08) | the Mw uncertainty column of ISC-GEM; 0.2 where empty |
| iscgem | 1964–1975 | 302 | 0.29 (0.20–1.12) | 0.77 (0.05) | |
| centennial | to 1975 | 126 | 0.25 (0.25–0.30) | 0.85 (0.80) | set: 0.25, 0.30 for a converted mB |
| cabello | before 1904 | 104 | 0.50 | 0.55 | set: 0.5 |
| rm18 | to 1975 | 27 | 0.20–0.30 (0.20–0.63) | 0.78–0.91 (0.39) | set: 0.2, + 0.1 for bounds and "~", half the range for a range |
| a6 | all | 7 | 0.10–0.52 | 0.52–0.98 | the σ column of `overrides_A6.csv`, else that of the value replaced |

Per converted scale: ISC mb shallow 0.27 (683 events, count 0.83), CSN ML shallow 0.26, NEIC mb 0.24, ISC mb deep 0.18, CSN ML deep 0.19, ISC MS 0.14.

**The ISC-GEM values with σ near 1.** All of them are quality D, and every quality-D value comes from the *Supplement* of ISC-GEM, not from the main catalogue. The header of the catalogue file defines the Mw quality as A to C and describes the Supplement as the earthquakes for which "poor data availability" prevented a reliable epicentre or magnitude.

| ISC-GEM file, quality, source | 1904–1963: events, σ median (max), mean count | 1964–1975 |
|---|---|---|
| main, B, direct / proxy | 7, 0.30, 0.85 / 85, 0.20 (0.29), 0.90 | 34, 0.30, 0.83 / 9, 0.20 (0.30), 0.89 |
| main, C, direct / proxy | 5, 0.40, 0.68 / 118, 0.32 (0.70), 0.75 | 5, 0.40, 0.70 / 243, 0.27 (0.68), 0.78 |
| Supplement, B and C, proxy | 13, 0.23 (0.51), 0.82 | – |
| Supplement, D, proxy | 12, 0.75 (1.02), 0.35 | 11, 0.75 (1.12), 0.29 |

- 27 values have σ ≥ 0.6: 19 Supplement D and 8 main-catalogue C proxies. The largest is Mw 6.6 (1922-03-12, σ 1.02; 1970-06-11, 112 km, σ 1.12, count 0.05). None is of Mw ≥ 7, so they do not touch the large-event counts.
- Is σ the right reading of the column? Formally yes: the column is the uncertainty of Mw, and for the main catalogue (0.1 for GCMT, 0.2–0.4 for B and C) it behaves like a standard error. For the Supplement D values it marks a magnitude ISC-GEM does not stand behind. The weight then keeps a twentieth to a third of an event at a magnitude nobody trusts, and exp(−β²σ²/2) assumes a normal error and a Gutenberg–Richter line far below the value, which does not hold at σ 1.
- Size of the effect: 23 quality-D events of Mw ≥ 5.0, 11 of them inside the table (Mw ≥ 5.2 from 1964), counted 2.9 together. Negligible for the fits.
- **Proposed correction for Pablo (catalogue rule, not applied):** do not take an Mw from the ISC-GEM Supplement with quality D; the event falls to the next source of the order (converted Centennial or ISC / NEIC magnitude). 23 events at Mw ≥ 5.0. The same question for the 8 main-catalogue C proxies with σ 0.6–0.7 is weaker; I would leave them.
- B9 attributed the 13 % loss of intermediate in-slab N(≥ 7) to "ISC-GEM values of 1964–1975 with σ up to 1.1". That is not the cause: the loss comes from the Centennial (σ 0.25–0.30) and Cabello (0.5) values of the large old events.

**Large events by count and by weight** (class weight summed; "weighted" also with the magnitude-error weight; all events in the domain, in or out of the table):

| unit | Mw ≥ | before 1904: count / weighted | 1904–1975 | from 1976 | all: weighted over count |
|---|---|---|---|---|---|
| interface | 7 | 26.9 / 16.5 | 23.6 / 20.5 | 20.0 / 19.7 | 0.80 |
| interface | 8 | 11.0 / 7.2 | 4.0 / 3.5 | 4.0 / 3.9 | 0.77 |
| interface, 45.6–37° S | 7 / 8 | 3.0 / 1.5, 1.5 / 0.7 | 7.5 / 6.7, 2.0 / 1.8 | 2.0 / 2.0, 0 | 0.82, 0.73 |
| interface, 37–32° S | 7 / 8 | 9.0 / 5.2, 5.1 / 3.2 | 5.3 / 4.6, 1.0 / 0.9 | 4.0 / 3.9, 1.0 / 1.0 | 0.75, 0.71 |
| interface, 32–26° S | 7 / 8 | 5.6 / 3.9, 1.0 / 0.8 | 6.0 / 5.1, 1.0 / 0.8 | 3.0 / 3.0, 1.0 / 1.0 | 0.82, 0.87 |
| interface, 26–17.6° S | 7 / 8 | 6.2 / 3.9, 1.0 / 0.9 | 4.8 / 4.1, 0 | 9.0 / 8.9, 2.0 / 2.0 | 0.84, 0.96 |
| in-slab, shallow | 7 | 7.7 / 3.4 | 7.4 / 5.8 | 1.0 / 1.0 | 0.63 |
| in-slab, shallow | 8 | 2.4 / 1.0 | 0 | 0 | 0.41 |
| in-slab, intermediate depth | 7 | 12.2 / 5.0 | 29.2 / 21.9 | 7.0 / 6.8 | 0.70 |
| in-slab, intermediate depth | 8 | 0 | 1.0 / 0.9 | 0 | 0.87 |
| Jujuy nest | 7 | 0 | 2.0 / 1.4 | 1.0 / 1.0 | 0.79 |
| crustal, forearc | 7 | 3.3 / 1.8 | 3.3 / 2.8 | 1.0 / 1.0 | 0.73 |
| crustal, arc | 7 | 0 | 2.5 / 2.2 | 0 | 0.86 |
| crustal, backarc | 7 | 0.9 / 0.5 | 1.0 / 0.9 | 1.0 / 1.0 | 0.80 |
| crustal, Patagonia | 7 | 1.0 / 0.5 | 2.0 / 1.7 | 0 | 0.74 |

The weight removes 20–30 % of the large events, almost all of it before 1904 (σ 0.5, count 0.55 at b 0.96 and 0.42 at b 1.16). The set σ of 0.5 for every Cabello value is the single number that matters most here; it is a default, not a measurement. Not proposed for change, but it is what makes the step "Mw 8.0 from 1500" count 7.2 interface events instead of 11.

## 4. Methods compared (step 3)

`compare.py`; real catalogue in `tables/fits_sensitivity_2026-11-15.csv` (every method, unit, with all events and with weight-1 events), synthetic catalogues in `tables/synth_methods.csv`, `synth_pooled.csv`, `synth_table.csv`. `figs/methods.png`, `figs/synthetic_methods.png`, `figs/b_floor.png`.

**Recovery on synthetic catalogues** (400 per case; true Gutenberg–Richter line, the table of DECISIONS, class weights of the real class, each event with the kind and σ of a real event of its period and size, 0.1 bins). Bias of b / N(≥ 5) / N(≥ 7), and in brackets the share of catalogues whose 5–95 % interval holds the truth (nominal 90 %) for b / N(≥ 7):

| method | large class (b 0.96, 25 per year) | small class (b 1.0, 3.5 per year) |
|---|---|---|
| Weichert, open line (reference) | +0.003 / +1.7 % / +0.8 % (88 / 87 %) | +0.002 / +1.8 % / +2.9 % (89 / 87 %) |
| the same without the magnitude-error weight | −0.026 / +12 % / +26 % | −0.026 / +13 % / +29 % |
| Weichert, line cut at Mmax | +0.002 / +1.7 % / +0.6 % (88 / 87 %) | +0.002 / +1.7 % / +0.4 % (89 / 87 %); N(≥ 8) −20 % |
| tapered, corner 9.6 | +0.003 / +1.7 % / +0.5 % (84 / 85 %) | +0.002 / +1.8 % / +2.8 % (88 / 86 %) |
| Aki–Utsu, Mw ≥ 5.0 from 1976 | −0.001 / +3.4 % / +4.6 % (92 / 89 %) | 0.000 / +3.6 % / +7.5 % (88 / 85 %) |
| joint Mc–b (Ogata–Katsura), from 1976 | +0.001 / +3.8 % / +4.2 % (90 / 87 %) | −0.001 / +4.4 % / +8.9 % (88 / 86 %) |
| least squares, cumulative | +0.013 / +5.0 % / −0.9 % (88 / 85 %) | +0.038 / +10 % / −6 % (77 / 75 %) |

- Scatter of one catalogue (reference): b 0.017 and N(≥ 7) 8 % for the large class, 0.044 and 22 % for the small one. Aki–Utsu and the joint fit scatter 1.3–1.4 times more (they use 51 years), least squares 2.3–2.5 times more.
- The bootstrap sd equals the scatter between catalogues. The intervals hold the truth in 87–89 % of the catalogues for b and N(≥ 7), close to nominal. For N(≥ 5) they hold it in 81 % (large class) and 87 % (small): the rate keeps a bias of +1.7 % that the bootstrap does not know about (the magnitude-error weight is exact only when σ does not depend on magnitude; in the catalogue small events have the larger σ). For the methods on 1976–2026 only, the bias is +3.5 to +4.4 % and the N(≥ 5) interval holds the truth in 51–81 %.
- On these catalogues detection below the table is a cumulative normal, the form the joint fit assumes: its best case.

**Real catalogue** (all events; reference = the open line with the b of the cut-line fit; in the sensitivity file the rows are named "line cut at Mmax (reference)", "tapered, corner of run.py", "open line", "open line, no largest magnitude in the likelihood" and so on):

| method | what it changes |
|---|---|
| Weichert, no largest magnitude in the likelihood | b −0.01 to +0.06 (forearc 1.04, arc 1.04, backarc 1.04, nest 1.27); N(≥ 7) −23 to +3 %. The bins above the largest event are empty and pull b up; the reference leaves them out. |
| Weichert, line cut at Mmax | same b. N(≥ 7): interface and segments 0 to −3 %; in-slab −3 %; nest −24 %; forearc −32 %; arc −10 %; backarc −16 %; Patagonia −8 %. N(≥ 8): interface −2.5 %, segment 32–26° S −28 %, 26–17.6° S −13 %, in-slab −45 %. AIC better than the open line by 3–7 for intermediate in-slab, forearc, backarc and segment 32–26° S, within 2 elsewhere. |
| tapered, corner 9.6 | same b (within 0.001); N(≥ 7) and N(≥ 8) within 1 % of the open line for the interface, the segments and the in-slab classes. AIC equal within 0.2. The corner at 9.6 changes nothing below Mw 8.5. |
| tapered, corner free | interface 9.6 (the likelihood is flat from 9.3 up: lower bound only, as LEARNINGS); segments 9.8, 9.3, 9.25, 7.95 (26–17.6° S, AIC better by 2); in-slab shallow 7.85, intermediate 7.8 (AIC better by 4.5; N(≥ 8) × 0.24), nest 7.5. The in-slab classes prefer an MFD that ends near Mw 8. |
| Aki–Utsu, Mw ≥ 5.0 from 1976 | b lower for the interface (0.914; segments 0.875–0.965, −0.07 to +0.05) and −0.05 to +0.04 elsewhere; N(≥ 5) −4 to +11 % (the rate of 1976–2026 with its sequences); interface N(≥ 7) +31 %, N(≥ 8) +47 %. |
| joint Mc–b (Ogata–Katsura), one detection curve per network window | fails: b 1.26–1.71 from Mw 3.5 and 0.93–1.62 from Mw 4.5, with detection widths of 0.7–1.5 magnitude units. Below Mw 5 the catalogue is a mixture of regions and agencies with different completeness, not one line times one detection curve. Works on the synthetic catalogues. Not usable here. |
| pooled b (shrinkage) | the between-unit variance comes out zero in all three families, so every unit takes the family b: segments 0.958, in-slab 1.159 (nest from 1.236), crustal 0.980. N(≥ 7): segments × 0.82 (45.6–37° S), × 1.19 (37–32° S), × 0.89 (32–26° S, which then passes the check), × 1.07; nest × 1.44; arc × 1.12; others within 3 %. |
| least squares on cumulative rates | b 0.81–1.22, scattered (forearc 1.22, segment 45.6–37° S 0.81). Contrast only. |

- **Large-event check:** the reference, the cut line and the tapered line fail the same two units (section 2). Pooled b fails intermediate in-slab only. A floor of 5.6 passes all (intermediate in-slab b 1.07), but the b of that class and of the Jujuy nest falls steadily with the floor (1.16 → 0.96; 1.24 → 0.75), the old large events pulling.
- **b against the floor** (`figs/b_floor.png`): interface 0.95–0.97 from 5.0 to 6.0, segments within ± 0.05; in-slab shallow 1.09–1.15; forearc 0.98 → 0.84–0.90; backarc rises (0.99 → 1.39 at 6.0); intermediate in-slab and nest fall.
- **Pooled b on synthetic families** (four classes with the crustal rates, 200 families): with equal true b the error of b falls from 0.044–0.128 to 0.035–0.043 and that of log N(≥ 7) by 20–60 %, most for the smallest class. With true b 0.9 / 1.0 / 1.1 / 1.0 it pulls the outer classes toward the middle (b +0.014 and −0.033) and their errors grow by 10–15 %, while the two classes at the mean still gain. Intervals hold the truth in 81–92 % either way.
- **Split events:** weight-1 events only give N(≥ 5) × 0.40 (forearc), × 0.54 (shallow in-slab), × 0.70–0.82 (interface), × 0.92–0.96 (arc, backarc, intermediate in-slab) and b −0.04 for the interface (0.925), within 0.02 elsewhere. The same factors with Aki–Utsu and the tapered form: it is a property of the catalogue, not of the method.

**The automatic table on synthetic margins** (40 catalogues per case with the table of DECISIONS, four regions, all events; `tables/synth_table.csv`). This is the test of the brief "the automatic table recovers a known table", and it does not pass cleanly:

| detection below the table | rule for Mc | "5.2 from 1964" found | "5.0 from 1976" found | Mw 7.0 from (true 1905) | b, fit on the automatic table against the true table | N(≥ 7) | N(≥ 8) |
|---|---|---|---|---|---|---|---|
| cumulative normal | larger of KS and b-stability (DECISIONS) | 30 % | 5 % (median 2009) | 1830 | +0.033 | × 0.86 | × 0.80 |
| | smaller of the two | 88 % | 18 % | 1830 | +0.022 | × 0.89 | × 0.85 |
| one in ten per 0.5 magnitude | larger (DECISIONS) | 23 % | 0 % (median 2020) | 1875 (1830–1910) | +0.015 | × 0.94 | × 0.91 |
| | smaller of the two | 83 % | 23 % | 1875 | +0.009 | × 0.96 | × 0.94 |

- Instrumental steps: with 4 regions × 7 windows × 2 methods and "the largest", one window that reads high by chance moves a step later. The result is cautious (N(≥ 5) within 1 %), it only throws data away. On the real catalogue the rule gave exactly the table that the regional rows show by eye, but that is one draw.
- Historical steps: the rate rule accepts a band that is 40–60 % complete when it holds few events (B9 said "up to 40 years early"; here Mw 7.0 comes out 30–75 years early, and Mw 7.5 from 1500 in the first case). The fit then counts incomplete periods as complete: N(≥ 7) 6–14 % low and N(≥ 8) 9–20 % low on these catalogues. How incomplete the real record is just above each step is not known; the synthetic catalogues make it mildly incomplete by construction.
- With the instrumental steps given, the historical steps come out at or before the true year and never more than a block late (`tests/test_table.py`).

## 5. Recommendation (options, not decisions)

1. **Keep Weichert on the table as the estimator.** It has the smallest bias and scatter, its bootstrap intervals are close to nominal, and no alternative passes a check that it fails except by changing the question (floor 5.6, pooled b).
2. **MFD shape** (settled by Pablo, 15 Nov: tapered preferred, cut at Mmax kept, both into the tornado). Section 2 gives a and b for each shape in its own convention. Against an open line the two shapes lower N(≥ 7) by 24–34 % for the nest and the forearc and by 16 % for the backarc; between themselves they differ by a few per cent up to Mw 7.
3. **Pooled b:** option for the four interface segments (family b 0.958; the data do not show the segments to differ; it removes the failure at 32–26° S and moves N(≥ 7) by −18 to +19 %). Not for the Jujuy nest (b falls with the floor; pooling hides that). The crustal classes are already within 0.02 of each other.
4. **Aki–Utsu and the joint fit** stay out: the first is a check of b on 1976–2026 (interface 0.914 against 0.962, the Kijko–Smit value is 0.915), the second does not work on this catalogue.
5. **Completeness table:** keep the table of DECISIONS for B12, but do not describe the rule in the paper as validated on synthetic catalogues. Two things to consider: "the smaller of KS and b-stability" (or both must agree) for the instrumental Mc, and a sensitivity fit with the historical steps moved later (for example 7.0 from 1930, 7.5 from 1880, 8.0 from 1730) to bound the 6–20 % effect on the large-event rates.
6. **σ:** the ISC-GEM Supplement quality-D magnitudes (section 3).

## 6. Not done, assumptions

- Mmax "observed + 0.2" and the corner at the observed maximum use every event with class weight ≥ 0.5, historical ones included (Pablo, 15 Nov). In-slab 8.0 in both classes: Santiago 1647 for the shallow class (7.8 without it), Calama 1950 for the intermediate one (Chillán 1939 is 7.8).
- The tapered line is fitted with the bins above Mmax left out and does not end there (Pablo, 15 Nov). OpenQuake's tapered MFD asks for an upper magnitude; it has to be set well above the corner so that it cuts nothing.
- σ: the historical values keep 0.5 and the ISC-GEM Supplement values stay (Pablo, 15 Nov); the proposal of section 3 is closed.
- The magnitude-error weight in the bootstrap uses the β of the maximum-likelihood fit; it is not iterated per replicate.
- AIC values use weighted (non-integer) counts, so they are a pseudo-likelihood; differences below about 2 mean nothing. The cut line has Mmax taken from the data, which the AIC does not charge for.
- Synthetic catalogues: one b for all sizes, Poisson in time (no sequences), normal magnitude errors with the listed σ. The real rate changes of 2010–2015 are not in them.
- No EMR fit (Woessner and Wiemer 2005); Ogata–Katsura was run instead. No hierarchical Bayesian pooling; the random-effects estimate (DerSimonian and Laird 1986) was used.
- The frozen catalogue was not changed. No hazard effect of any of this was computed.
- Run times (16 cores): `run.py` 80 s, `sigma.py` 5 s, `compare.py` about 10 min with one thread per worker (set `OMP_NUM_THREADS=1`; without it the 14 workers oversubscribe the cores), tests 15 s.
