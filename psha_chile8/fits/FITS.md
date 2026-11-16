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

## 7. Refit with one Mmax rule for every unit (B12 step 0, 15 Nov)

DECISIONS (Statistics, 15 Nov): Mmax = largest observed event + 0.2 in every unit, the interface included (segments 9.7 / 9.3 / 8.7 / 9.0, margin 9.7); the corner of the tapered line comes from that Mmax and the b of the unit by Kagan (2002b, eq. 12), corner moment = M0(Mx) (β / Γ(2 − β))^(1/(1 − β)), β = 2b/3, with Mx the upper edge of the last bin (Mmax + 0.05) and b of the cut-line fit of the unit. It replaces the fixed corner 9.6 of the interface and "corner = observed maximum" of the other classes.

Changed: `gr.kagan_corner`, and in `run.py` the interface Mmax, the corner rule (`corner(d, u, b)`) and `DATE`. Test `tests/test_corner.py`: the tapered line with that corner has the moment rate of the cut line within 1 % (b 0.92–1.23, Mx 7.45–9.75). Table `tables/fits_2026-11-15b.csv` (same columns); `fits_2026-11-15.csv` kept. `fits_sensitivity_2026-11-15b.csv` and the figures of `figs/` were redrawn on the new fits. The completeness table is unchanged.

Old (`fits_2026-11-15.csv`) → new (`fits_2026-11-15b.csv`); fitted / observed at Mw ≥ 7 and ≥ 8 of the new fit:

| unit | shape | Mmax | corner | b | N(≥ 7) | N(≥ 8) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|---|
| interface | tapered | 9.5 → 9.7 | 9.6 → 9.48 | 0.962 → 0.963 | 0.300 → 0.299 | 0.0326 → 0.0324 | 54.5 / 49.7 | 17.1 / 14.7 |
| interface, 45.6–37° S | tapered | 9.5 → 9.7 | 9.6 → 9.47 | 0.915 → 0.915 | 0.0436 → 0.0435 | 0.00529 → 0.00526 | 8.2 / 9.4 | 2.8 / 2.5 |
| interface, 37–32° S | tapered | 9.1 → 9.3 | 9.6 → 9.10 | 0.996 → 0.997 | 0.0864 → 0.0859 | 0.00869 → 0.00849 | 15.3 / 12.1 | 4.5 / 5.1 |
| interface, 32–26° S | tapered | 8.5 → 8.7 | 9.6 → 8.48 | 0.934 → 0.941 | 0.100 → 0.0965 | 0.0117 → 0.00945 | **17.2 / 9.6** | 4.9 / 2.6 |
| interface, 26–17.6° S | tapered | 8.8 → 9.0 | 9.6 → 8.79 | 0.974 → 0.965 | 0.0644 → 0.0671 | 0.00682 → 0.00690 | 12.1 / 15.1 | 3.6 / 2.9 |
| in-slab, shallow | tapered | 8.2 | 8.0 → 8.04 | 1.150 → 1.151 | 0.0451 → 0.0451 | 0.00141 → 0.00156 | 6.7 / 7.5 | 0.7 / 0.6 |
| in-slab, intermediate depth | tapered | 8.2 | 8.0 → 8.04 | 1.153 → 1.154 | 0.122 → 0.122 | 0.0038 → 0.0042 | **18.2 / 29.4** | 2.0 / 0.9 |
| Jujuy nest | tapered | 7.4 | 7.2 → 7.26 | 1.226 → 1.229 | 0.00867 → 0.00927 | 0 | 1.1 / 2.4 | – |
| crustal, forearc | tapered | 7.4 | 7.2 → 7.19 | 0.982 → 0.982 | 0.0252 → 0.0250 | 0 | 2.9 / 3.6 | – |
| crustal, arc | tapered | 7.9 | 7.7 → 7.70 | 1.002 → 1.002 | 0.0120 → 0.0120 | 0.00012 | 1.6 / 2.2 | – |
| crustal, backarc | tapered | 7.7 | 7.5 → 7.49 | 0.988 → 0.988 | 0.0209 → 0.0209 | 2e-05 | 2.7 / 2.1 | – |
| crustal, Patagonia | tapered | 8.0 | 7.8 → 7.79 | 0.982 → 0.982 | 0.00659 → 0.00659 | 0.00014 → 0.00013 | 0.9 / 1.7 | 0.0 / 0.0 |
| interface | cut at Mmax | 9.5 → 9.7 | – | 0.962 → 0.962 | 0.300 → 0.299 | 0.0319 → 0.0321 | 54.4 / 49.7 | 16.9 / 14.7 |
| interface, 45.6–37° S | cut at Mmax | 9.5 → 9.7 | – | 0.915 → 0.916 | 0.0434 → 0.0433 | 0.00512 → 0.00515 | 8.1 / 9.4 | 2.7 / 2.5 |
| interface, 37–32° S | cut at Mmax | 9.1 → 9.3 | – | 0.996 → 0.997 | 0.0859 → 0.0856 | 0.00817 → 0.00830 | 15.2 / 12.1 | 4.4 / 5.1 |
| interface, 32–26° S | cut at Mmax | 8.5 → 8.7 | – | 0.934 → 0.939 | 0.0974 → 0.0961 | 0.00849 → 0.00928 | **17.1 / 9.6** | 4.9 / 2.6 |
| interface, 26–17.6° S | cut at Mmax | 8.8 → 9.0 | – | 0.973 → 0.963 | 0.0636 → 0.0670 | 0.00595 → 0.00672 | 12.0 / 15.1 | 3.5 / 2.9 |

The other classes keep their Mmax, so their cut-line fits are identical to the old table.

- The interface b and N(≥ 7) move by less than 0.01 and 5 %. N(≥ 8) of the segments: within 3 % except 32–26° S (tapered −19 %, its corner falls from 9.6 to 8.48; cut +9 %) and 26–17.6° S (cut +13 %; one event of Mw 8.9 now lies below the top bin and enters the likelihood: 422 events against 421).
- The interface corners now sit 0.21–0.27 below Mmax, so the two shapes of a segment now agree at N(≥ 8) within 2 % (before up to 37 %).
- The other classes: the corner moves by 0.01–0.06, N(≥ 7) by up to 7 % (nest), N(≥ 8) of the in-slab classes by +10 %.
- The two failures stay (32–26° S and intermediate in-slab at Mw ≥ 7).
- **For S1:** `gr.rates` returns bins up to Mw 9.7 only (`MTOP`). With the margin corner at 9.48, the tapered line holds 6 % of its moment rate above Mw 9.75 (segment 45.6–37° S the same; 37–32° S none). DECISIONS asks for the tapered list to run about one unit above the corner. Either extend the grid in S1 when the lists are written, or raise `MTOP` in `gr.py` (not done here: it also changes the empty bins of the open-line sensitivity fits).

## 8. Rerun on the catalogue of 16 Nov (A9)

Input `catalog/frozen/2026-11-16/catalog_2026-11-16.csv`; `fits/run.py` unchanged except `DATE` (and `CAT` in `gr.py`); same Mmax and corner rule as section 7. Tables `fits_2026-11-16.csv`, `fits_sensitivity_2026-11-16.csv`, `table_2026-11-16.csv`, `mc_windows_2026-11-16.csv`. The figures in `figs/` are of this run; those of the 15b run are in `figs/2026-11-15b/`. Sections 2 to 7 keep the numbers of the 2026-11-14c catalogue.

Tapered fits (the cut-line fits move by the same amounts; both in the table). Mmax and corner are the same in both runs except where an arrow is given. Bold: outside the Poisson band in both runs.

| unit | Mmax | corner | b, 15b → 16 (sd) | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 fitted / observed, 15b → 16 |
|---|---|---|---|---|---|---|---|
| interface | 9.7 | 9.48 | 0.963 → 0.959 (0.018) | 25.20 → 25.22 | 2.745 → 2.772 (+1.0 %) | 0.299 → 0.305 (+1.9 %) | 54.5 / 49.7 → 55.7 / 51.6 |
| interface, 45.6–37° S | 9.7 | 9.47 | 0.915 → 0.909 (0.049) | 2.94 → 2.95 | 0.358 → 0.364 (+1.8 %) | 0.0435 → 0.0449 (+3.4 %) | 8.2 / 9.4 → 8.5 / 9.9 |
| interface, 37–32° S | 9.3 | 9.10 → 9.09 | 0.997 → 0.993 (0.033) | 8.48 → 8.49 | 0.854 → 0.862 (+1.0 %) | 0.0859 → 0.0875 (+1.8 %) | 15.3 / 12.1 → 15.6 / 12.6 |
| interface, 32–26° S | 8.7 | 8.48 | 0.941 → 0.939 (0.030) | 7.40 → 7.40 | 0.847 → 0.851 (+0.5 %) | 0.0965 → 0.0974 (+0.9 %) | **17.2 / 9.6 → 17.4 / 9.9** |
| interface, 26–17.6° S | 9.0 | 8.79 → 8.78 | 0.965 → 0.962 (0.039) | 5.71 → 5.72 | 0.620 → 0.623 (+0.6 %) | 0.0671 → 0.0679 (+1.1 %) | 12.1 / 15.1 → 12.2 / 15.3 |
| in-slab, shallow | 8.2 | 8.04 | 1.151 → 1.144 (0.039) | 9.24 → 9.22 | 0.652 → 0.662 (+1.4 %) | 0.0451 → 0.0465 (+3.1 %) | 6.7 / 7.5 → 6.9 / 8.3 |
| in-slab, intermediate depth | 8.2 | 8.04 | 1.154 → 1.157 (0.026) | 25.31 → 25.28 | 1.776 → 1.762 (−0.8 %) | 0.1219 → 0.1201 (−1.5 %) | **18.2 / 29.4 → 17.9 / 28.5** |
| Jujuy nest | 7.4 | 7.26 | 1.229 → 1.229 (0.090) | 3.74 → 3.74 | 0.219 → 0.219 | 0.0093 → 0.0093 | 1.1 / 2.4 → 1.1 / 2.4 |
| crustal, forearc | 7.4 | 7.19 | 0.982 → 0.984 (0.055) | 3.54 → 3.53 | 0.365 → 0.361 (−1.0 %) | 0.0250 → 0.0246 (−1.6 %) | 2.9 / 3.6 → 2.9 / 3.4 |
| crustal, arc | 7.9 | 7.70 | 1.002 → 1.023 (0.103) | 1.308 → 1.299 | 0.130 → 0.123 (−5.5 %) | 0.0120 → 0.0108 (−9.9 %) | 1.6 / 2.2 → 1.5 / 1.7 |
| crustal, backarc | 7.7 | 7.49 | 0.988 → 0.979 (0.069) | 2.30 → 2.31 | 0.235 → 0.241 (+2.5 %) | 0.0209 → 0.0218 (+4.6 %) | 2.7 / 2.1 → 2.8 / 2.4 |
| crustal, Patagonia | 8.0 | 7.79 | 0.982 → 0.984, forearc | 0.640 → 0.430 (−33 %) | 0.0667 → 0.0445 (−33 %) | 0.0066 → 0.0044 (−33 %) | 0.9 / 1.7 → 0.6 / 1.7 |

- **Completeness table:** unchanged (5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500). The Mc of every window and region is identical to the 15b run: completeness is read on all events, and the revision changed two magnitudes and no location.
- **What changed in the catalogue, as the fits see it:** 57 853 events of Mw ≥ 3.5 in the domain in both; two magnitudes (1939-04-18 7.3 → 7.6, 1942-07-08 6.9 → 7.1); class weights of 38–40 events each in the interface, shallow in-slab and forearc, 6 in intermediate in-slab, 3 in the arc, 1 in the backarc, 13 in Patagonia.
- **Patagonia:** 13 events (weight 13.0, all below Mw 6) became outer rise (Chile Ridge events at the triple junction): 41 → 28 events, rates −33 %. Mmax and corner unchanged (1949).
- **Arc:** three split no-depth events left (1919-03-02 Mw 7.2 to outer rise; 1926-04-28 Mw 7.3 and 1929-10-19 Mw 7.8 to in-slab; 0.53 of weight, all at Mw ≥ 7): b +0.021 (a fifth of its sd), N(≥ 6) −5.5 %, N(≥ 7) −10 %, observed Mw ≥ 7 2.2 → 1.7. Mmax still 7.9 (Aysén 1960 at 7.7). Moving the arc boundary to 47.24° S brought no event of Mw ≥ 5 into the table.
- **Forearc:** −1.5 of weight at Mw ≥ 7 (no crustal share before 1900): rates −1 to −2 %, observed Mw ≥ 7 3.6 → 3.4.
- **Interface:** +3.0 of weight at Mw ≥ 7: b −0.004, N(≥ 7) +1.9 %, branches a −0.02 and b −0.004 to −0.005.
- **In-slab:** shallow b −0.007, N(≥ 7) +3 %; intermediate N(≥ 7) −1.5 %, observed Mw ≥ 7 29.4 → 28.5.
- **Large-event check:** the same two failures (intermediate in-slab, segment 32–26° S), nothing new.
- **Over the thresholds of the A9 brief** (0.02 in b, 5 % in N(≥ 6), 0.1 in Mmax): the arc (b by 0.021, N(≥ 6) by 5.5 %) and Patagonia (33 %). Nothing in the interface or in-slab units, and no Mmax or corner moved.

## 9. Mmax from the events that belong to the unit for certain (16 Nov, run 2026-11-16b)

Tables `fits_2026-11-16b.csv`, `fits_sensitivity_2026-11-16b.csv`, `table_2026-11-16b.csv`, `mc_windows_2026-11-16b.csv`; the figures in `figs/` are of this run, those of the 2026-11-16 run are in `figs/2026-11-16/`. Single-unit figures of the 2026-11-16 run: `figs/forearc_2026-11-16.png`, `figs/arc_2026-11-16.png`.

- **Rule** (Pablo, 16 Nov): the largest observed event of a unit, for Mmax and the corner, is taken among the events with class weight 1, not weight ≥ 0.5. `fits/run.py`: setting `MMAX_W = 1.0`, used in `observed()`; `run_declustered.py` takes its Mmax from the same function. Nothing else changed.
- **Why:** the forearc Mmax was set by 1960-12-02 09:10 Mw 7.2 (24.67° S, 70.08° W, near Paposo; forearc weight 0.78). Its class rests on the Centennial depth of 14 km alone (σ 20 km); ISC-GEM gives 35 ± 6 km (quality A), which is inside the interface band over a slab top at 49 km. No mechanism: Pacheco and Sykes (1992, Table 4) list type "u", no depth, Ms 7.1. Not named in Ruiz and Madariaga (2018), Comte et al. (1999) or Lomnitz (2004); no A6 hint. The 1987-03-05 Antofagasta thrust event (42 km) is 30 km away.
- **Only the forearc changes its largest event:** 7.2 → 7.0, 2010-03-11 14:55 Pichilemu (GCMT mechanism, crustal hint, weight 1). Every other unit already had a weight-1 event at its maximum (arc Aysén 1960 7.7; backarc 1894 and Caucete 1977 7.5; Patagonia 1949 7.8; interface, in-slab, nest unchanged).

| forearc | Mmax | corner | b (sd) | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 fitted / observed |
|---|---|---|---|---|---|---|---|
| tapered, 16 → 16b | 7.4 → 7.2 | 7.19 → 6.99 | 0.984 (0.055) → 0.961 (0.057) | 3.53 → 3.55 | 0.361 → 0.378 (+4.6 %) | 0.0246 → 0.0176 (−28 %) | 2.9 / 3.4 → 1.9 / 3.4 |
| cut at Mmax | 7.4 → 7.2 | – | 0.986 (0.057) → 0.968 (0.060) | 3.53 → 3.54 | 0.353 → 0.362 (+2.5 %) | 0.0256 → 0.0201 (−21 %) | 3.1 / 3.4 → 2.4 / 3.4 |

- The large-event check still passes for both shapes (3.4 observed is inside the Poisson band of 1.9 and of 2.4). The 3.4 are fractions of 17 events of Mw 7.0–7.2, one of them with weight 1; they stay in the fit, all at or below the new Mmax.
- **Patagonia** takes the forearc b, so it moves too: b 0.984 → 0.961, N(≥ 5) unchanged (0.430), N(≥ 6) +5.6 %, N(≥ 7) +11 %; Mmax 8.0 and corner 7.79 → 7.78.
- **All other units:** identical to the 2026-11-16 tables in every column (same seed). Completeness table unchanged.
- **Declustered fits** (`fits_declustered_2026-11-16b.csv`; the declustered catalogues of 2026-11-16 are used as they are): forearc Mmax 7.4 → 7.2, corner 7.15–7.19 → 6.94–6.98; b 0.856 → 0.825 (Gardner–Knopoff per family) and 0.962 → 0.937 (nearest neighbour per family); N(≥ 6) +6.3 % and +4.7 %; N(≥ 7) −31 % and −29 %; checks pass. Patagonia through the forearc b; other units identical.
- **Forearc b against the floor** falls more steeply with Mmax 7.2: 0.94 at 5.2, 0.87 at 5.4, 0.78–0.80 at 5.6–5.8, 0.73 at 6.0.

## 10. Crustal classes fitted from 1976 (16 Nov, run 2026-11-16c)

Tables `fits_2026-11-16c.csv`, `fits_sensitivity_2026-11-16c.csv`, `table_2026-11-16c.csv`, `mc_windows_2026-11-16c.csv`; the figures in `figs/` are of this run, those of 16b are in `figs/2026-11-16b/`.

- **Rule** (Pablo, 16 Nov): the crustal classes (forearc, arc, backarc, Patagonia) are fitted on the completeness table from 1976 on only, that is "Mw 5.0 from 1976"; the step "5.2 from 1964" and the historical steps (7.0 from 1905, 7.5 from 1830, 8.0 from 1500) are not used for them. Mmax is kept: the largest weight-1 event of any year + 0.2 (forearc 7.2, arc 7.9, backarc 7.7, Patagonia 8.0), and the corner from it. Interface and in-slab units keep the full table. `fits/run.py`: `since=1976` in the crustal units and `table_of()`, used by the fits, the comparison, the declustered fits and the figures; the fits table has a new column `steps`.
- **Why** (diagnostic of 16 Nov): in 1964–1975 both classes are short at Mw 5.5–5.9 (forearc 0.12 per year against 0.64–0.78 afterwards; arc 0.04 against 0.16–0.67); the class Mc cannot be measured before 2000 (under 100 events per window; 4.6–4.8 pooled over 1976–2026, below the floor). The historical steps counted the arc's Mw 7.5–7.9 bins over 197 years on one event (Aysén 1960) in a region with no early record, and the forearc's Mw 7.0–7.2 bins on 16 fractions of events without depth (2.5 in all).

| unit (tapered) | Mmax | corner | events (counted) | b (sd), 16b → 16c | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 fitted / observed from 1976 |
|---|---|---|---|---|---|---|---|---|
| forearc | 7.2 | 6.99 → 6.98 | 782 → 710 (195) | 0.961 → 0.929 (0.061) | 3.55 → 3.84 (3.49–4.21) | +16 % | 0.0176 → 0.0213 (+21 %) | 1.0 / 1.0 |
| arc | 7.9 | 7.70 → 7.71 | 100 → 85 (70) | 1.023 → 1.047 (0.104) | 1.30 → 1.38 (1.12–1.63) | 0 % | 0.0108 → 0.0103 (−5 %) | 0.5 / 0 |
| backarc | 7.7 | 7.49 → 7.48 | 195 → 171 (121) | 0.979 → 0.934 (0.082) | 2.31 → 2.38 (2.06–2.71) | +14 % | 0.0218 → 0.0274 (+26 %) | 1.4 / 1.0 |
| Patagonia | 8.0 | 7.78 | 28 → 22 (21) | forearc b | 0.430 → 0.417 (0.28–0.57) | +4 % | 0.0049 → 0.0054 (+12 %) | 0.3 / 0 |

- The cut-line fits move the same way (forearc b 0.968 → 0.926, N(≥ 7) +28 %). Interface, in-slab and nest rows are identical to 16b.
- **Cross-check against the events left out.** The large events before 1976 no longer enter the fit, so they test it: over 1905–2026 the arc line expects 1.25 events of Mw ≥ 7 and the catalogue has 2 (1927, Aysén 1960; 1.7 by weight); the forearc line expects 2.6 and the catalogue has 3.4 by weight. Both inside the Poisson band.
- **Still weak, and visible in the table:**
  - forearc: weight-1 events alone give b 0.846 and N(≥ 5) 1.53 (40 % of the fit); b against the floor 0.92 (5.2), 0.88 (5.4), 0.81 (5.6), 0.82 (6.0);
  - arc: nothing above Mw 6.5 since 1976, so the line is extrapolated from 6.5 to its Mmax of 7.9; b against the floor rises (1.20 at 5.2, 1.15 at 5.4, 1.12 at 5.6, 1.83 at 6.0 on a handful of events); a pooled crustal b is 0.954;
  - the sequences of 2000–2010 are a quarter of the window and set the rate (Mw 5.0–5.4: forearc 5.4 per year then against 1.1–2.4, arc 1.8 against 0.7–0.8).
- **Declustered fits** (`fits_declustered_2026-11-16c.csv`; the crustal classes take the steps from 1976 of whichever table is used, so their "full" and "declustered" table rows now differ only through the declustered Mc): forearc b 0.825 → 0.795 (Gardner–Knopoff per family) and 0.937 → 0.912 (nearest neighbour per family), N(≥ 6) +13 %; arc b 0.936 → 1.000 and 0.974 → 1.014, N(≥ 7) −23 % and −13 %; backarc b 1.004 → 1.020 and 1.050 → 1.060, N(≥ 7) −12 % and −8 %. Checks pass.

## 11. One b for the crustal family (16 Nov, run 2026-11-16d)

Tables `fits_2026-11-16d.csv`, `fits_sensitivity_2026-11-16d.csv`, `table_2026-11-16d.csv`, `mc_windows_2026-11-16d.csv`; the figures in `figs/` are of this run, those of 16c are in `figs/2026-11-16c/`. This is the current state of the crustal fits: table from 1976 (section 10), Mmax from weight-1 events (section 9), shared b.

- **Rule** (Pablo, 16 Nov): the four crustal classes share one b, that of the crustal family fitted as one unit (all crustal weight together, table from 1976, Mmax 8.0 from its largest weight-1 event); each class keeps its own rate, Mmax and corner. In the bootstrap each class takes the family b of the same replicate. `fits/run.py`: new unit `crustal` (also a row of the tables, "crustal, all classes"), and `b_from="crustal"` for forearc, arc, backarc and Patagonia.
- **Family:** b 0.975 (sd 0.042) tapered, 0.972 (0.043) cut; 988 events, 406 counted; N(≥ 5) 7.98 per year. Kijko–Smit 0.978, Aki–Utsu 0.974, b-positive 1.10; b against the floor 1.00 (5.2), 1.01 (5.4), 0.97 (5.6), 1.06 (5.8), 1.22 (6.0). Mw ≥ 7 since 1976: 4.3 fitted, 2.0 observed (inside the band).

| unit (tapered) | Mmax | corner | b, 16c → 16d | N(≥ 5) (5–95 %) | N(≥ 6), 16c → 16d | N(≥ 7) (5–95 %), against 16c | Mw ≥ 7 expected over 1905–2026 / observed by weight |
|---|---|---|---|---|---|---|---|
| forearc | 7.2 | 6.99 | 0.929 → 0.975 | 3.82 (3.47–4.19) | 0.440 → 0.393 (−10 %) | 0.0179 (0.0127–0.0241), −16 % | 2.6 / 3.5 |
| arc | 7.9 | 7.69 | 1.047 → 0.975 | 1.39 (1.13–1.64) | 0.123 → 0.147 (+19 %) | 0.0144 (0.0096–0.0201), +40 % | 1.7 / 1.7 |
| backarc | 7.7 | 7.49 | 0.934 → 0.975 | 2.36 (2.04–2.69) | 0.276 → 0.249 (−10 %) | 0.0227 (0.0158–0.0310), −17 % | 2.7 / 1.9 |
| Patagonia | 8.0 | 7.79 | 0.929 → 0.975 | 0.416 (0.28–0.57) | 0.049 → 0.044 (−10 %) | 0.0044 (0.0026–0.0067), −19 % | 0.5 / 1.6 |

- N(≥ 5) of every class within 1 % of 16c. The sd of b falls from 0.06–0.10 (own b) to 0.042 for all four. The last column is the cross-check on the large events left out of the fit (cut-line values); all four inside the Poisson band. With its own b Patagonia failed it (0.2 expected).
- Own b for reference (rows "line cut at Mmax, own b" of the sensitivity table): forearc 0.926, arc 1.043, backarc 0.930, Patagonia 1.166 (22 events).
- **Arc:** the observed points of 1976–2026 lie under the shared-b line at Mw 6.0–6.5 (about 6.4 events of Mw ≥ 6 observed, 7.5 fitted); nothing above 6.5 since 1976, so the tail to Mmax 7.9 is still extrapolated, now with the family slope.
- Interface, in-slab and nest rows are identical to 16, 16b and 16c.
- **Declustered fits** (`fits_declustered_2026-11-16d.csv`): family b 0.923 (0.054) with Gardner–Knopoff per family and 0.999 (0.051) with nearest neighbour per family, taken by the four classes; arc N(≥ 6) 0.106 and 0.109, forearc 0.257 and 0.252. Checks pass.
- **Why not a crustal-only completeness table** (tested, not adopted): read on crustal events alone, Mc is 5.3 in 1976–1989 and the automatic table becomes "5.0 from 1990, 5.3 from 1964" with historical steps 6.5 from 1950, 7.0 from 1860, 7.5 from 1500; b rises (family 1.06, arc 1.11). From a floor of 4.5 the family b is 0.972 (0.021) on 600 events, but through the small events of the sequence years.

## 12. Catalogue 2026-11-16c: crustal events outside the crustal grid, Scotia events (16 Nov, run 2026-11-16e)

Tables `fits_2026-11-16e.csv`, `fits_sensitivity_2026-11-16e.csv`, `table_2026-11-16e.csv`, `mc_windows_2026-11-16e.csv`, `fits_declustered_2026-11-16e.csv`; the figures in `figs/` are of this run, those of 16d are in `figs/2026-11-16d/`. Current state of the fits.

- **Catalogue.** `fits/gr.py`: `CAT` → `catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv` (checksum verified). Against `2026-11-16`: 57 853 events of Mw ≥ 3.5 in the domain in both; no Mw, σ, position or depth changed; 13 events moved their weight from crustal to outer rise; `sub_crustal` is `outside` for 1 150 events of Mw ≥ 3.5 (786 backarc, 360 forearc, 4 Patagonia).
- **The new sub-class.** Nothing in `fits/` reads `sub_crustal` by listing its values: `gr.load()` builds one weight column per class by name (`CLASSES`), so the `outside` events get no weight in any unit; `decluster.py` reads only the family weights (`w_interface`, `w_inslab`, `w_crustal`, `w_outer_rise`, `w_unclassified`). The run, the comparison, the declustered fits and the figures went through unchanged; 31 tests pass. Counted weight in the crustal table as A7 gave it: forearc 191.7, arc 76.1, backarc 22.8, Patagonia 11.0. Largest weight-1 events unchanged (7.0, 7.7, 7.5, 7.8).
- **Rules:** those of `fits_2026-11-16d.csv`, no code change: crustal table 5.0 from 1976, one b for the crustal family, Mmax from weight-1 events. Completeness table and Mc of every window identical.
- **The family b is fitted without the `outside` events:** 1.009 ± 0.053 tapered (1.006 ± 0.054 cut; 782 events, 278 counted), against 0.975 ± 0.042 in 16d. Reason: the family unit is the sum of the four classes, and the rule of A7 is that no fit reads `outside`, so that b, rates, pattern and sources describe one region. For comparison: with the outside events the family b is 0.974 ± 0.042 (395 counted), and the outside events alone give 0.896 ± 0.078 (117 counted; a third of them the Caucete sequence of 1977, the rest the Argentine backarc and southern Peru). The two differ by 0.03, inside the standard deviation; **Pablo, 16 Nov: keep it without them** (b from the wider region with rates from the grid would give back 0.974; not taken).

| unit (tapered) | Mmax | corner, 16d → 16e | b | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 since 1976, fitted / observed |
|---|---|---|---|---|---|---|---|
| interface and the four segments | 9.7 / 9.7 / 9.3 / 8.7 / 9.0 | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |
| in-slab shallow, intermediate, Jujuy nest | 8.2 / 8.2 / 7.4 | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |
| crustal family | 8.0 | 7.79 → 7.80 | 0.975 → 1.009 (0.053) | 7.98 → 5.47 (−31 %) | 0.844 → 0.535 (−37 %) | 0.0847 → 0.0497 (−41 %) | 2.5 / 1.0 |
| forearc | 7.2 | 6.99 → 7.00 | 0.975 → 1.009 | 3.82 → 3.48 (−9 %) | 0.393 → 0.332 (−15 %) | 0.0179 → 0.0144 (−20 %) | 0.7 / 1.0 |
| arc | 7.9 | 7.69 → 7.70 | 0.975 → 1.009 | 1.390 → 1.383 (−0.5 %) | 0.147 → 0.135 (−8 %) | 0.0144 → 0.0123 (−15 %) | 0.6 / 0 |
| backarc | 7.7 | 7.49 → 7.50 | 0.975 → 1.009 | 2.36 → 0.403 (−83 %) | 0.249 → 0.039 (−84 %) | 0.0227 → 0.0033 (−85 %) | 0.2 / 0 |
| Patagonia | 8.0 | 7.79 → 7.80 | 0.975 → 1.009 | 0.416 → 0.202 (−51 %) | 0.044 → 0.020 (−55 %) | 0.0044 → 0.0018 (−58 %) | 0.1 / 0 |

- The cut-line fits move the same way (b 0.972 → 1.006). The interface, in-slab and nest rows are identical to 16d in every column.
- The arc lost no event; it moves only through the family b. The backarc keeps 27 events (20 counted) and Patagonia 11 (10 counted): their own b would be 1.26 and 1.66, so they depend entirely on the family b.
- **Cross-check against the events of Mw ≥ 7 since 1905** (not in the fit; expected by the line / observed by weight): forearc 1.8 / 3.5, arc 1.5 / 1.7, backarc 0.4 / 0.9 (San Juan 1944; Caucete 1977 is now outside), all inside the Poisson band. Patagonia 0.2 / 1.7 fails: the two events are the Magallanes doublet of 1949-12-17 (Mw 7.8), which belong to the Magallanes–Fagnano fault source, not to the background.
- **Declustering.** `fits/decluster.py` reads the classes only for the per-family methods (the family of the largest of the five family weights) and never `sub_crustal`. All five methods were run again as `catalog/declustered/*_2026-11-16e.csv` (the script builds them together). Compared with the `_2026-11-16` files: `gk`, `nn`, `nn_depth` and their `_m35` files are identical; `gk_family` has the same mainshock flags (6 006) and differs only in cluster labels; `nn_family` differs in 2 flags (10 923 → 10 921; 4 flags from Mw 3.5), through the 13 Scotia events that changed family. Completeness tables of the declustered catalogues unchanged.
- **Declustered fits** (`fits_declustered_2026-11-16e.csv`; two options, table full, own family b): family b 0.923 → 0.922 (Gardner–Knopoff per family) and 0.999 → 1.001 (nearest neighbour per family), so the declustered b hardly moves, unlike the full one. N(≥ 6): forearc −8 % and −9 %, arc 0 % and −0.5 %, backarc −75 % and −78 %, Patagonia −45 % and −53 %. Interface, in-slab and nest rows identical. Checks as before.
- **Rows over the thresholds** (0.02 in b, 5 % in N(≥ 6), 0.1 in Mmax; no Mmax moved):
  - S1 (interface, segments; full and declustered): none.
  - S2 (in-slab shallow, intermediate, Jujuy nest): none.
  - S3, `fits_2026-11-16e.csv`, both shapes: `crustal`, `forearc`, `arc`, `backarc`, `patagonia`, all by b (+0.034) and by N(≥ 6) (−37, −15, −8, −84, −55 %).
  - S3, `fits_declustered_2026-11-16e.csv` (gk_family and nn_family, table full, own b): `forearc`, `backarc`, `patagonia` and `crustal` by N(≥ 6); the `arc` rows are under the thresholds.

