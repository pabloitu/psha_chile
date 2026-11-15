# B9: earthquake statistics per class, exploratory run

14 Nov 2026. Input: `catalog/frozen/2026-11-14/catalog_2026-11-14c.csv`, the 14 279 events of Mw ≥ 4.5 in the domain. An exploration: nothing here is a decision; the options for B10 are at the end of each part. Scripts `b9_*.py`, results in `cache/` and `tables/`, figures in `figs/` (`figures_index.md`). Step 0 is in `STEP0.md`.

**Status, 15 Nov 2026.** Parts 1–5 and the summary are the exploration of 14 Nov and are left as written; their "options for B10" are superseded where sections 6–8 and the additions of 15 Nov in parts 1 and 2 say otherwise. Decided by Pablo on 15 Nov (DECISIONS, Statistics):
- one completeness table for every class, read on the whole catalogue: Mw 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500 (section 7);
- Weichert on that table, with every event counted exp(−β²σ²/2) (sections 6 and 8); Kijko–Smit and b-positive as checks;
- Patagonia with the forearc b, backarc and Jujuy nest with their own fit at the floor, no pooling;
- not acted on, for the discussion of the paper: the intermediate in-slab events of Mw ≥ 7 before 1976, and Mw 8.0 from 1500.
The fits to use are the last table of section 8 (`tables/refit_single_table.csv`). Two statements of 14 Nov no longer hold: the catalogue is not cut at Mw 4.5, only the working set of the scripts was (corrected in part 1); and the CEUS-SSC equations, said below to be unchecked (summary point 10, part 5, Failures and skips), were checked against the report on 15 Nov (`MAG_ERROR_REFS.md`).

Conventions. An event counts in a class by its weight; "weight-1" fits use only the events with weight 1 in that class. Magnitudes are 0.1 bin centres, so N(≥ 7) means the bin 7.0 and above (Mw ≥ 6.95). A completeness table is a list "magnitude from, complete since". Fits are Weichert (1980), an open Gutenberg–Richter line (no taper), bootstrap of the events (300 resamples), ranges are 5–95 %. "Fitted against observed" compares the count the fit gives inside the table with the count the catalogue has there, with a Poisson 5–95 % band.

## Summary

1. **Mixing a short window for the small events with a long window for the larger ones raises b and fails the large-event check on the interface.** The network table (4.5 from 2000, 5.0 from 1976, 5.5 from 1964, …) gives b 1.06 and 29 fitted against 44 observed events of Mw ≥ 7 since 1900; each window alone gives b 0.92–0.96 and passes. The Mw ≥ 5.5 rate of the interface is 12.3 per year in 2000–2026 against 7.0 in 1964–1999 (Maule, Iquique, Illapel), so the bins seen only after 2000 sit too high against the others. This is the pitfall of LEARNINGS ("unequal windows with sequences") on the new catalogue. `figs/tables_one_window_or_mixed.png`, `figs/large_event_check_M7.png`.
2. **One instrumental window plus the long record for the large events only works for the interface:** 5.0 from 1964, 7.0 from 1900, 7.5 from 1820, 8.0 from 1730 gives b 0.93 (0.90–0.96), N(≥ 7) 0.37 per year, 60 fitted against 56 observed at Mw ≥ 7 and 12.6 against 15.6 at Mw ≥ 8. A floor of 5.2 or 5.5 gives the same (b 0.93). `figs/frequency_magnitude_classes.png`.
3. **b against the floor (interface):** falls from 1.06 at 4.5 to a plateau of 0.91–0.97 from 5.0–5.2 up (network table); b-positive gives 0.94–0.99. `figs/b_against_floor_classes.png`.
4. **Mw 4.5–4.9 is complete only from about 2000.** Before 1990 the interface has as many events at 4.5–4.9 as at 5.0–5.4 (ratio 0.7–1.1 in every region; about 3 expected); b at floor 4.5 is 0.6 in 1964–1989. The change points of the yearly counts fall at 1964 and 2001–2002. Shape-based Mc (maximum curvature, b-stability, KS) sees none of it: 4.5–5.1 in every window, because the catalogue is cut at 4.5. `figs/cumulative_counts_gk.png`, `figs/regions_band_ratio.png`.
5. **Mw ≥ 5.0 from 1964 and Mw ≥ 5.5 from 1964 hold** for the large classes (declustered rates steady per period, p 0.2–0.98); the full-catalogue rates are not Poisson (interface Fano factor 18 at Mw ≥ 5.5). `figs/stationarity.png`.
6. **In-slab, intermediate depth: the large events before 1976 do not fit the modern record.** Mw ≥ 7: 0.31–0.46 per year in 1900–1963 against 0.07 in 2000–2026 (ratio before / after 1976 2.8, p 0.01; 4.3 at Mw ≥ 7.5). Every table that reaches before 1964 fails the Mw ≥ 7 check (21–25 fitted, 36–38 observed); the tables from 1964 pass (8 against 11). 14 of the 29 events of 1900–1975 are converted Centennial values with a measured depth. The four events of the DECISIONS_NOTE move the rate by 1–2 %: the question is the whole group, not those four. `figs/large_events_per_era.png`.
7. **Historical tables (interface):** with the instrumental part fixed, the choice of the historical steps moves N(≥ 7.5) and N(≥ 8) by 10 % or less; the instrumental table moves them by a factor 2 (finding 1). Counts per half century say Mw ≥ 8 is steady from about 1730–1800 and Mw ≥ 7.5 from about 1820; "7.5 from 1535" (Lomnitz 2004) holds for the margin as a whole only because it is filled by the centre. `figs/cumulative_large_events.png`, `figs/historical_tables_rates.png`.
8. **Gardner–Knopoff removes 79 % of the interface events and 88 % of the Jujuy nest;** the declustered interface b is 0.6–0.77 and keeps falling with the floor (no plateau). The nearest-neighbour method removes 57 % (interface) and 7 % (intermediate in-slab) and leaves b unchanged (0.93 against 0.92, 5.0 from 1964). `figs/declustering.png`.
9. **Weights:** weight-1 events only lower the rates of the classes that hold the split events, at nearly the same b: shallow in-slab × 0.51 (N ≥ 5), forearc × 0.37, interface × 0.75 (b 1.01 against 1.06; 0.88 against 0.93 on the one-window table), intermediate in-slab × 0.96. `figs/weights_and_error_correction.png`.
10. **Magnitude-error correction** (CEUS-SSC procedure as written in DECISIONS, not checked against the report, which is not on disk): N(≥ 5) −6 to −15 %, N(≥ 7) −3 to −27 %; the plain weight −3 to −14 % at both. On the historical events (σ 0.3–0.6) the procedure moves an Mw 8.0 with σ 0.5 to 7.4 and counts it 1.9 times: the count of Mw ≥ 8 inside a historical table stays about the same for the interface (14.9 against 15.6) but is made of other events, and for the shallow in-slab class it falls from 2.2 to 0.3. `tables/deeper_ceus_large_interface.csv`, `deeper_error_correction.csv`.
11. **Jujuy nest:** b 1.44 at floor 4.5, 1.2 at 5.0–5.4, about 1.0 from 5.5; b-positive 1.3. No floor gives a plateau; Gardner–Knopoff is unusable there.
12. **Crustal classes:** forearc b 0.98–1.03 and steady; arc 1.0–1.1 (thin); backarc b rises with the floor (0.90 → 1.5), carried by 1976–1989 (San Juan 1977): rate of Mw ≥ 5.5 2.5 per year then, 0.2–0.6 since; Patagonia 62 events, b 0.75–0.85.
13. **Space:** the Mc maps are flat (4.5–4.7 from 1990 and from 2010). The count ratio 4.5–4.9 over 5.0–5.4 shows one region that stays thin after 2010: the interface north of 21° S (ratio about 2). No other need for a regional table at Mw ≥ 4.5 from 2000. `figs/mc_maps.png`.
14. **What moves N(≥ 7) most** (`figs/tornado_N7.png`): interface: the table and the floor (× 1.3–1.9), nearest-neighbour declustering (× 0.46); shallow in-slab and forearc: the split events (× 0.54, × 0.37); intermediate in-slab: the floor (× 1.5 at 6.0) and the error correction (× 0.8); the catalogue cases (mb −0.1, floor 5.5 before 1990, the four old events, interface band ± 10 / 20 km) stay within ± 10 %, except the band on the forearc (× 0.86 / 1.10).
15. **Step 0:** the 50 km check drops 94 events of Mw ≥ 4.5 in the domain (423 of any size); 85 is not reproduced by any saved run. List of disagreements in `STEP0.md`.

## 1. Completeness in time

**Tried** (`b9_1_completeness.py`, `cache/comp_years.csv`, `comp_mc_windows.csv`): for every class, all events and weight-1 events: yearly counts per threshold (4.5 to 8.0); Stepp (1972), automated as the longest span back from 2026 whose mean rate stays within 2 standard errors of the rate of the last 20 years (60 for Mw ≥ 6.5); change points of the yearly counts (binary segmentation of a Poisson likelihood, BIC penalty scaled by the dispersion), read as "complete since the last jump up"; Mc per network period and per decade by maximum curvature (+0.2), b-stability and Kolmogorov–Smirnov. Stepp and the change points were run on the full counts and on both declustered sets, because Stepp assumes a Poisson process.

**What came out.**
- The automated Stepp on the full catalogue is not usable: the last 20 years hold three great sequences, the reference rate is high, and it reads "complete from 2000–2005" at every magnitude up to 6.0 (interface). On declustered counts it is erratic (interface Mw ≥ 5.0: 1956; Mw ≥ 6.0: 1992).
- Change points are steadier. On the Gardner–Knopoff counts: interface Mw ≥ 4.5 breaks at 1964 and 2001 (1.1 → 9.7 → 17.0 per year), Mw ≥ 5.0 at 1964, Mw ≥ 5.5 at 1960, Mw ≥ 6.0 and 6.5 none from 1900, Mw ≥ 7 at 1819. Intermediate in-slab: 1964 and 2002 at Mw ≥ 4.5, 1964 at Mw ≥ 5.0, 1965 at Mw ≥ 5.5, 1906 at Mw ≥ 7.
- "No break from 1900" at Mw ≥ 6.0 is too kind: the interface rate of Mw 6.0–6.4 is 0.33 per year in 1900–1929, 0.77 in 1930–1949 and 1.3–2.1 in 1950–1999; Mw 6.5–6.9 is 0.15–0.21 before 1950 and 0.4–0.5 from 1950. The test needs a jump inside a noisy series of small counts and misses a slow rise. Mw ≥ 6.5 from about 1950 reads better than the 1930 of Engdahl and Villaseñor (2002).
- Window Mc: 4.5–5.1 for all classes and periods with enough events; maximum curvature 4.7–5.3. Not informative here, because B9 loaded only Mw ≥ 4.5 (the statistical cut of DECISIONS); the frozen file also holds 18 002 events of Mw 4.0–4.4, which were not used and could show the roll-off (LEARNINGS confirmed for the cut set).
- Window Mc from Mw 4.0 (added 15 Nov, `b9_8_mc40.py`, `tables/mc_from_40.csv`, `figs/mc_from_40.png`; a check only, no fit uses these events). With the roll-off in view, b-stability and KS agree with the steps read from the count ratios. Interface: 5.1 / 5.0 in 1964–1975 and 1976–1989, 4.7 in the 1990s, 4.6 in 2000–2006, 4.5 in 2007–2011, 4.2–4.3 in 2012–2019. All events: 5.0–5.2 to 1989, 4.6–4.8 in 2000–2011, 4.3–4.6 in 2012–2019. So Mw 4.5 from 2000 holds, by 0.1 short in 2000–2006, and Mw 5.0 from 1964 is 0.1 short in the first window. Before 1990 the distribution is flat or falling below 5.0 (in 1976–1989 there are fewer events at 4.0–4.4 than at 4.5–4.9, ratio 0.5–0.7). Mw 4.0–4.4 is not complete in any period: its count over that of 4.5–4.9 is 2.4–2.5 from 2012 (interface) where the ratio one band higher is 3.0. Maximum curvature reads 4.2–4.4 in every window, 1964–1975 included, and is not usable. Interface north of 26° S: 4.5–4.6 in 2000–2011 and still 4.5 by b-stability in 2012–2019 (KS 4.2), with a 4.5–4.9 to 5.0–5.4 ratio of 2.0–2.6. Intermediate in-slab reads 5.0–5.1 in 2007–2011 because b rises with the floor there (1.02 at 4.5, 1.31 at 5.0), not because events are missing. 2020–2026 is short and the readings scatter (4.2–4.6). Magnitudes below 4.5 are at the edge of the conversion fits.
- Rates per band and period (declustered) show the steps directly: interface Mw 4.5–4.9 3.1–4.2 per year before 2000 and 9.6–13.0 after; Mw 5.0–5.4 2.6–4.0 throughout from 1964.

**Network-history table**, the same for every class: 4.5 from 2000, 5.0 from 1976, 5.5 from 1964, 6.5 from 1930, 7.0 from 1900.

**Historical steps** (`b9_tables.py`, `HIST`): Lomnitz (7.5 from 1535; Lomnitz 2004 gives Ms 7.5 for 1535–1960); counts (7.5 from 1820, 8.0 from 1730, read off the half-century counts by segment); long (7.0 from 1819, the change point, and 8.0 from 1570); old (8.3 from 1513, psha_chile6). Interface, fitted rates per year on the network table:

| historical steps | b | N(≥ 7.5) | N(≥ 8) | Mw ≥ 8 fitted / observed (years) |
|---|---|---|---|---|
| none (7.0 from 1900) | 1.06 | 0.067 | 0.020 | 2.5 / 8 (127) |
| Lomnitz | 1.06 | 0.065 | 0.019 | 9.3 / 18.3 (492) |
| counts | 1.05 | 0.071 | 0.021 | 6.2 / 15.6 (297) |
| long | 1.06 | 0.067 | 0.020 | 9.0 / 18.3 (457) |
| old | 1.05 | 0.072 | 0.021 | 6.6 / 17.5 (514) |
| 5.0 from 1964, 7.0 from 1900 | 0.93 | 0.128 | 0.044 | 5.5 / 8 (127) |
| 5.0 from 1964, 7.0 from 1900, counts | 0.93 | 0.126 | 0.043 | 12.6 / 15.6 (297) |

The historical steps hardly move the fit (the few hundred large events weigh little against 3 600 small ones); they decide whether the fit can be *checked* against the great earthquakes. The observed rate of Mw ≥ 8 is 0.063 per year since 1900 and 0.052 since 1730; of the 15.6 events since 1730, 5.6 are in segment 2 (37–32° S). Before 1700 most large events are Cabello values with σ 0.5 and split weights (interface 0.49–0.78).

**Surprises.** Finding 1 (mixed windows). The in-slab large events (part 5). 1950–1963 has more Mw 6.0–6.4 events than any later period outside the great sequences, in three classes (interface 2.1 per year, shallow in-slab 1.1, forearc 0.57): the Valdivia sequence with ISC-GEM proxy magnitudes; not followed further.

**Options for B10.**
- (a) One instrumental window per class (5.0 from 1964, or 5.2–5.5), plus the long record only from Mw 7: passes the checks on the interface, uses a third of the events, floor independent.
- (b) The network table with a fit floor of 5.2 or more: the same result by another road (the 4.5–5.1 bins are dropped).
- (c) Keep Mw 4.5–4.9 from 2000 for the spatial pattern only.
- (d) Mw ≥ 6.5 from 1950 instead of 1930; Mw ≥ 6.0 not before 1950–1964.
- (e) Historical steps: "counts" (7.5 from 1820, 8.0 from 1730) or "Lomnitz"; the difference is below 10 % in the rates.

## 2. Completeness in space

**Tried** (`b9_4_space.py`): 0.5° cells, events within 150 km (at least 60 by weight), interface and in-slab families, from 1990 and from 2010: Mc by maximum curvature and b-stability, b, and the count of Mw 4.5–4.9 over 5.0–5.4. The same ratio and Mc per region (the four segment bands and the far south) and network period.

**What came out.** Mc 4.5–4.7 nearly everywhere (median 4.5–4.6); patches of 4.8–5.0 at 19–21° S and near 28° S. The count ratio is the better tool. Interface, by region and period: 0.7–1.1 before 1990 everywhere; about 2 in 1990–1999; mostly 2.7–3.7 from 2000 outside the north (north 2.0–2.6). In-slab: 2.2–2.8 from 1964 to 2011 in the north (b 1.15 would give 3.8), 4.2 from 2012. On the map the interface north of 21° S stays near 2 after 2010 (b about 0.6 there, or events missing towards Peru); the south (38–46° S) has too few events for any estimate before 2007.

**Whole catalogue, not per class (added 15 Nov).** `b9_10_mc_all.py`, `tables/mc_all_regions.csv`, `figs/mc_all_map_1deg.png` and `mc_all_map_05deg.png`. All events of Mw ≥ 3.5 in the domain, no class weights; Mc by b-stability and KS. A check only: no fit uses the small events.

Mc per period (KS / b-stability):

| | 1964–75 | 1976–89 | 1990–99 | 2000–06 | 2007–11 | 2012–19 | 2020–26 |
|---|---|---|---|---|---|---|---|
| whole margin | 5.2 / 5.1 | 5.1 / 5.0 | 4.7 / 5.4 | 4.6 / 4.8 | 4.9 / 4.8 | 4.6 / 4.6 | 4.4 / 4.4 |
| north (15–26° S) | 5.1 / 5.1 | 4.8 / 4.9 | 4.7 / 4.7 | 4.3 / 4.7 | 4.8 / 4.8 | 4.7 / 4.7 | 4.4 / 4.3 |
| central-north (26–32° S) | 5.2 / 5.1 | 5.0 / 5.0 | 4.6 / 4.6 | 4.5 / 4.5 | 4.6 / 5.0 | 4.2 / 4.2 | 4.4 / 4.3 |
| central (32–37° S) | 4.9 / 5.1 | 5.0 / 5.0 | 4.8 / – | 4.0 / 4.6 | 4.5 / 4.8 | 4.3 / 4.3 | 4.3 / 4.3 |
| south (37–46° S) | 4.6 / 4.6 | – | – | 4.4 / 4.4 | 4.6 / 4.6 | 4.5 / 4.7 | 3.5 / 3.5 |
| far south | – | – | – | – | – | – | 4.0 / 3.6 |

- The whole-margin reading is 0.1–0.4 above most regional ones from 2000 (2012–2019: 4.6 against 4.2–4.3 in the centre). A sum of regions with different b is curved, and a shape-based Mc reads that as incompleteness. The regional rows are the ones to use.
- Mw 5.0 from 1964: 5.1–5.2 in 1964–1975 in every region with an estimate, 5.0–5.1 in 1976–1989. The first window supports a floor of 5.2 for 1964, or 5.0 from 1976.
- Mw 4.5 from 2000 does not hold for the whole catalogue: 4.6–4.8 in 2000–2006 and 4.8–4.9 in 2007–2011 (Tocopilla 2007 and Maule 2010 with their sequences are inside). From 2012 it holds in the centre (4.2–4.3) and not in the north (4.7).
- By depth: events at 70 km and deeper read like the shallow ones in the north (4.6–4.9 from 2007) and lower in the centre (3.5–4.0 from 2000).
- South of 37° S there is no estimate before 2000 and none south of 46° S before 2020: fewer than 100 events of Mw ≥ 3.5 per window.

On the map (cells of 1°, events within 250 km, at least 150):

| period | cells with an estimate | latitudes covered | median Mc | cells above 4.5 | above 5.0 |
|---|---|---|---|---|---|
| 1976–1999 | 143 | 17–36° S | 4.9 | 97 % | 11 % |
| 2000–2011 | 198 | 17–41° S | 4.6 | 52 % | 1.5 % |
| 2012–2026 | 234 | 17–56° S | 4.3 | 15 % | 0 |

- 1976–1999: Mc 4.8–5.1 everywhere mapped; above 5.0 only east of the Andes at 31–33° S, 67–69° W (5.3) and a few coastal cells at 34–36° S (5.1).
- 2000–2011: above 4.5 along the coast from 30 to 41° S (4.6–4.9, the Maule region), east of the Andes at 22–30° S (up to 5.3 in one cell) and at the Peruvian border.
- 2012–2026: above 4.5 only at 18–21° S (4.7–4.9, the Iquique 2014 region, the same place where B9 found the 4.5–4.9 band thin) and in the far south (4.6–4.7).
- With cells of 0.5° and 150 km the picture is the same with smaller shares (94 %, 31 %, 7 % above 4.5).

**Read for B10 (options).** A floor of Mw 5.0 is complete in every mapped cell from 2000 and in nine of ten from 1976. Mw 4.5–4.9 is complete over the whole margin in no period: from 2012 everywhere except 18–21° S and the far south. South of 41° S nothing can be read before 2012; the table there has to be taken from the rest of the margin or from the large events alone.

**Options for B10.** One table for the margin at Mw ≥ 5.0. If Mw 4.5–4.9 is used (pattern), a later start in the north (2007) is supported; with a floor of 5.0 or more a regional table changes nothing that was measured here.

## 3. b-values and rates

**Tried** (`b9_3_fits.py`, 7 386 fits): Weichert on every table × all / weight-1 × full / Gardner–Knopoff / nearest neighbour × no correction / CEUS-SSC / plain weight (`cache/fits_main.csv`); the same against the fit floor 4.5–6.0 (`fits_floors.csv`); per period at floors 4.5, 5.0, 5.5 with b-positive (`fits_periods.csv`); b-positive from 1964, 1990, 2000, 2012 with difference thresholds 0.1–0.5 (`fits_bpos.csv`); fits that see only Mw < 7 or < 6.5 (`fits_below.csv`).

**Per class** (all events, full catalogue, no correction; rates per year):

| class | network table: b, N(≥ 5), N(≥ 7) | 5.0 from 1964, 7.0 from 1900 (+ counts for interface and in-slab): b, N(≥ 5), N(≥ 7) | b-positive, 1964 on | b plateau against the floor |
|---|---|---|---|---|
| interface | 1.06, 30.0, 0.23 | 0.93 (0.90–0.96), 26.5, 0.37 | 0.94 | 0.91–0.97 from 5.0–5.2 |
| in-slab, shallow | 1.03, 9.8, 0.085 | 1.13 (1.07–1.18), 9.9, 0.055 | 1.21 | 1.05–1.16 from 4.8; no clear plateau |
| in-slab, intermediate | 1.12, 28.5, 0.16 | 1.12 (1.09–1.16), 27.4, 0.16 | 1.13 | 1.12–1.15 at 4.5–5.3, then falls to 0.88 at 6.0 |
| Jujuy nest | 1.44, 4.9, 0.006 | 1.21 (1.08–1.35), 4.0, 0.015 | 1.32 | none (1.45 → 1.0) |
| crustal, forearc | 1.03, 4.1, 0.036 | 0.98 (0.93–1.08), 3.6, 0.039 | 1.07 | 0.93–1.08 throughout |
| crustal, arc | 1.07, 1.5, 0.011 | 0.96, 1.3, 0.016 | 1.00 | 0.9–1.1, noisy |
| crustal, backarc | 0.90, 2.3, 0.037 | 0.97 (0.89–1.07), 2.4, 0.028 | 1.14 | none (0.90 → 1.5) |
| crustal, Patagonia | 0.76, 0.64, 0.020 | 0.82, 0.64, 0.015 | 0.79 | 0.75–0.9, 62 events |
| in-slab, shallow + intermediate | 1.10, 38.4, 0.25 | 1.12, 37.3, 0.21 | 1.14 | as intermediate |
| crustal, all | 0.98, 8.7, 0.097 | 0.96, 8.0, 0.096 | 1.10 | 0.96–1.03 to 5.7 |

**Interface segments** (5.0 from 1964, 7.0 from 1900, 7.5 from 1820, 8.0 from 1730; all pass the Mw ≥ 7 and Mw ≥ 8 checks):

| segment | b | N(≥ 5) | N(≥ 7) | N(≥ 8) | Mw ≥ 7 fitted / observed |
|---|---|---|---|---|---|
| 1, 45.6–37° S | 0.88 (0.80–0.97) | 3.1 | 0.055 | 0.0073 | 9.2 / 10.5 |
| 2, 37–32° S | 0.96 (0.92–1.03) | 8.9 | 0.106 | 0.0115 | 17.2 / 13.7 |
| 3, 32–26° S | 0.92 (0.87–0.97) | 7.8 | 0.114 | 0.0138 | 18.8 / 11.6 |
| 4, 26–17.6° S | 0.93 (0.87–1.00) | 5.9 | 0.084 | 0.0099 | 13.7 / 16.9 |
| margin | 0.93 (0.90–0.96) | 26.5 | 0.37 | 0.043 | 60.5 / 55.7 |

The four segments add to 25.8 at N(≥ 5) and 0.36 at N(≥ 7): the margin fit is reproduced by the sum. On the network table the segment b are 0.99–1.11 and segment 1 fails the Mw ≥ 7 check (4.3 fitted, 9.5 observed).

**Per period** (`figs/b_per_period.png`): at floor 5.5 the interface b is 0.88–0.96 in four of the five periods (1.07 in 1990–1999, 47 events); at floor 5.0 it is 0.84–0.88 before 2000 and 0.93–1.01 after, a sign that 5.0–5.2 is slightly thin before 2000 (or of the mb reading, part 6); at floor 4.5 it is 0.6–0.7 before 2000.

**b-positive.** Agrees with the Weichert plateau within 0.05 for interface, intermediate in-slab and forearc, and is 0.05–0.1 higher for shallow in-slab, backarc and the nest. On the synthetic test it reads 0.04 low under a static incompleteness: it is exact for short-term loss after large events, not a full replacement of the table. Pairs of consecutive events are weighted by the product of the class weights.

**Magnitude-error correction.** Implemented as DECISIONS writes it: the event moves to M − βσ² and counts N* = exp(β²σ²/2), the moved magnitude shared linearly between the two neighbouring bins; β from the uncorrected fit of the same case. The net effect on a rate is the factor exp(−β²σ²/2), which is the "plain weight" variant (no move). **The CEUS-SSC report is not on disk; the equations are from the DECISIONS wording and memory and were not checked against §3.3.1.** On a synthetic catalogue with σ 0.25 both bring an inflated rate (+ 15 %) back within 4 % of the truth. On the catalogue, network table: b +0.00 to +0.03; N(≥ 5) × 0.85–0.94 (CEUS) and × 0.87–0.96 (plain); N(≥ 7) × 0.73–0.97 (CEUS) and × 0.87–0.97 (plain). The two differ at Mw ≥ 7 because the move by βσ² takes the old, large-σ events across the completeness steps. For the historical events the shift is 0.2 (σ 0.3) to 0.9 (σ 0.625, 1837) magnitude units at β of b = 1; capping σ at 0.25 or correcting only the events from 1964 changes N(≥ 7) by 1–9 % against the full correction (interface 3 %, intermediate in-slab 9 %) (`tables/deeper_error_correction.csv`).

**Options for B10.** b per class from a one-window table or from a floor on the plateau; b-positive as the cross-check that is already within 0.05. In-slab: one b for shallow and intermediate (1.12) or two (1.13, 1.12: the same). Jujuy nest, backarc, Patagonia: no stable b; borrow (LEARNINGS: thin classes) or fix by a rule. Error correction: the plain weight, or the CEUS move restricted to instrumental events; the move as written is not safe for σ ≥ 0.3.

## 4. Declustering

**Tried** (`b9_2_decluster.py`): Gardner and Knopoff (1974) windows (the fit of van Stiphout et al. 2012), largest event first, foreshock window equal to the aftershock window (a variant without foreshock window is cached); Zaliapin and Ben-Zion (2013) nearest neighbour with b = 1, d_f = 1.6, threshold log10 η = −5.52 from a two-Gaussian mixture of the distances from 1964 on. Both on all classes together.

| class | removed, Mw ≥ 4.5: GK / NN | removed, Mw ≥ 5.5: GK / NN | b full / GK / NN (5.0 from 1964) |
|---|---|---|---|
| interface | 79 % / 57 % | 64 % / 57 % | 0.92 / 0.70 / 0.93 |
| in-slab, shallow | 67 % / 33 % | 45 % / 33 % | 1.15 / 0.92 / 1.12 |
| in-slab, intermediate | 50 % / 7 % | 23 % / 11 % | 1.16 / 0.99 / 1.17 |
| Jujuy nest | 88 % / 13 % | 59 % / 17 % | 1.24 / 0.86 / 1.28 |
| crustal, forearc | 71 % / 55 % | 52 % / 49 % | 0.99 / 0.86 / 1.00 |
| crustal, arc | 47 % / 33 % | 43 % / 47 % | 1.04 / 0.98 / 1.05 |
| crustal, backarc | 40 % / 26 % | 45 % / 45 % | 0.94 / 0.92 / 1.09 |
| crustal, Patagonia | 34 % / 21 % | 35 % / 30 % | 0.95 / 0.89 / 0.94 |

Gardner–Knopoff keeps 36 % of the catalogue, the nearest-neighbour method 71 %. Gardner–Knopoff lowers b by 0.15–0.4 because it keeps the largest event of each window; the nearest-neighbour method keeps the first event of a cluster and leaves b as it is, while it lowers the interface rate by more than half at every magnitude. The declustered interface b on Gardner–Knopoff has no plateau (0.77 at 4.5, 0.59 at 6.0). Gardner–Knopoff treats the Jujuy nest and half of the intermediate in-slab events as aftershocks: the windows at Mw 4.5 (about 35 km, 80 days) are wide for a dense deep zone. On declustered counts the rates per period are Poisson (part 5).

**Options for B10.** As DECISIONS: rates and b from the full catalogue. For the spatial pattern the two methods give very different catalogues in the in-slab classes (50 % against 7 % removed); the nearest-neighbour set is the candidate there. The completeness years are best read on declustered counts, the fits on the full catalogue with the same table.

## 5. The checks that decide

**Large events** (`tables/large_events.csv`, `figs/large_event_check_M7.png`, `_M8.png`). Fitted / observed inside the table, all events:

| class | network | network + counts | 5.0 from 1964 only | 5.0 from 1964, 7.0 from 1900 (+ counts) |
|---|---|---|---|---|
| interface, Mw ≥ 7 | 29 / 44 fails | 38 / 56 fails | 24 / 25 | 60 / 56 |
| interface, Mw ≥ 8 | 2.5 / 8 fails | 6.2 / 15.6 fails | 2.9 / 4 | 12.6 / 15.6 |
| in-slab shallow, Mw ≥ 7 | 10.7 / 8.4 | 13.1 / 9.7 | 3.2 / 2.3 | 8.5 / 9.7 |
| in-slab intermediate, Mw ≥ 7 | 21 / 36 fails | 25 / 38 fails | 8.3 / 11 | 25 / 38 fails |
| forearc, Mw ≥ 7 | 4.6 / 4.3 | | 2.3 / 1 | 4.9 / 4.3 |
| backarc, Mw ≥ 7 | 4.7 / 2 | | 2.0 / 1 | 3.5 / 2 |
| crustal all, Mw ≥ 7 | 12.3 / 10.8 | | 5.5 / 2 | 12.2 / 10.8 |

A fit that sees only Mw < 7 gives the same picture (interface, network table: 25 fitted against 44). With weight-1 events only, the one-window interface fit has b 0.88 and over-predicts Mw ≥ 7 on the margin (56 fitted, 39 observed) and on segments 2 and 3: the split events, most of the old Mw 7–7.5 ones, are not in the observed count. Mw ≥ 8 still passes (12.8 against 14).

**Large events per era** (`tables/deeper_large_by_era.csv`, `deeper_large_by_source.csv`). Rate of Mw ≥ 7 per year:

| class | 1900–29 | 1930–63 | 1964–75 | 1976–99 | 2000–26 | before / after 1976 |
|---|---|---|---|---|---|---|
| interface | 0.33 | 0.26 | 0.39 | 0.38 | 0.41 | 0.8 (p 0.54) |
| in-slab, shallow | 0.11 | 0.08 | 0.11 | 0.04 | 0 | 4.9 (p 0.16) |
| in-slab, intermediate | 0.31 | 0.46 | 0.33 | 0.21 | 0.07 | 2.8 (p 0.011) |
| crustal, all | 0.07 | 0.19 | 0 | 0.04 | 0.04 | 2.9 (p 0.22) |

The interface is steady over 127 years. The intermediate in-slab class has 29 events of Mw ≥ 7 in 1900–1975 (14 Centennial conversions with a measured depth, 6.3 Centennial without depth, 3 A6 values, 3.9 Ruiz and Madariaga, 2 ISC-GEM) and 7 measured ones since 1976. At Mw ≥ 6.5 the ratio is 1.3 (p 0.41): the excess is in the size of the old events, not in their number. Either the mB and Ms conversions of the old intermediate-depth events are 0.3–0.5 high (the direction of the four events of the DECISIONS_NOTE and of the ISC-GEM proxies), or the last 50 years are quiet. Shallow in-slab has one Mw ≥ 7 since 1976 against 7.4 before by weight, most of them split events without depth.

**Stationarity** (`tables/stationarity.csv`, `figs/stationarity.png`). Rate of Mw ≥ 5.5 per period 1964–75, 1976–89, 1990–99, 2000–10, 2011 on, chi-square against a constant rate:

| class | full: rates per year, p | Gardner–Knopoff: p | Fano factor, full |
|---|---|---|---|
| interface | 7.0, 7.2, 6.7, 13.0, 11.8; p < 0.001 | 0.34 | 17.5 |
| in-slab, shallow | 1.5, 3.0, 3.0, 3.3, 2.6; p 0.06 | 0.18 | 2.8 |
| in-slab, intermediate | 6.8, 7.8, 5.6, 8.0, 6.6; p 0.20 | 0.98 | 1.6 |
| Jujuy nest | 0.5, 0.6, 0.6, 1.4, 1.1; p 0.09 | 0.78 | 1.2 |
| crustal, forearc | 0.2, 1.1, 1.1, 2.5, 0.8; p < 0.001 | 0.05 | 4.2 |
| crustal, backarc | 0.7, 2.5, 0.2, 0.6, 0.3; p < 0.001 | 0.14 | 9.8 |

Mw ≥ 5.0 from 1976 and Mw ≥ 4.5 from 2000 behave the same way: not Poisson on the full catalogue for interface, shallow in-slab and the crustal classes; on the declustered counts interface and in-slab are steady (p 0.16–0.95), forearc and arc are not at Mw ≥ 4.5 from 2000 (p 0.02, 0.003). The intermediate in-slab class is close to Poisson as it is. The forearc of 1964–1975 is low (0.2 against 1.1 per year) on both bases: either Mw ≥ 5.5 is not complete there before 1976 or the split weights change with the depth quality of the period.

**Weights** (`tables/weights_effect.csv`). Share of the fitted weight that is weight-1, N(≥ 5) ratio, b all / weight-1 (network table): interface 72 %, 0.75, 1.06 / 1.01; shallow in-slab 50 %, 0.51, 1.03 / 1.01; intermediate in-slab 97 %, 0.96, 1.12 / 1.13; forearc 38 %, 0.37, 1.03 / 1.03; arc 96 %, 0.96; backarc 95 %, 0.94. The split events are a rate question, not a b question, except on the interface (b −0.05), where they are a larger share of the small events than of the large ones.

**Sensitivity cases** (`cache/fits_sens.csv`; ratio of N(≥ 7) to the baseline: network table, + counts for interface and in-slab, all events):

| case | interface | in-slab shallow | in-slab intermediate | forearc | backarc |
|---|---|---|---|---|---|
| mb values before 1990 lowered by 0.1 | 0.96 | 0.93 | 0.91 | 0.97 | 0.89 |
| floor 5.5 before 1990 | 1.07 | 0.95 | 0.95 | 1.04 | 0.88 |
| four old in-slab events at the ISC-GEM value | 1.00 | 0.98 | 0.99 | 1.00 | 1.00 |
| four old in-slab events left out | 1.00 | 0.98 | 0.99 | 1.00 | 1.00 |
| no Mw ≥ 7 before 1976 | 0.90 | 1.02 | 0.90 | 0.99 | 1.15 |
| interface band ± 10 km | 1.05 | 1.03 | 1.00 | 0.86 | 1.00 |
| interface band ± 20 km | 1.01 | 0.98 | 1.00 | 1.10 | 1.00 |

The band cases are full reruns of `classify.py` (`b9_0_bands.py`; the ± 15 km rerun reproduces the frozen weights exactly). The band moves N(≥ 5) much more than N(≥ 7): interface 24.3 / 30.2 / 33.0 per year at ± 10 / 15 / 20 km, with b 0.99 / 1.05 / 1.07; shallow in-slab 13.3 / 9.8 / 7.9; forearc 6.3 / 4.1 / 3.1. The events that change class are small.

## 6. Magnitude-error weight on instrumental events (added 15 Nov)

`b9_9_magerr.py`, `tables/magerr_fits.csv`, `magerr_synthetic.csv`, `magerr_paired.csv`, `figs/magerr_weight.png`; notes on the method in `MAG_ERROR_REFS.md`. Each instrumental event (kinds `direct`, `proxy`, `iscgem`, `centennial`) counts exp(−β²σ²/2) with its own σ (CEUS-SSC 2012, eq. 3.3.1-1 per event); no magnitude is moved; the other kinds (`cabello`, `rm18`, `a6`) count 1. β from the fit itself, iterated. Tables: the "one window + long record" column of the candidate tables. Full catalogue, all weights.

| class | b without | b with | Δb | a without | a with | N(≥ 5) | N(≥ 7) | N(≥ 8) | sd of b / of N(≥ 5), bootstrap |
|---|---|---|---|---|---|---|---|---|---|
| interface | 0.929 | 0.917 | −0.011 | 6.02 | 5.93 | −7.6 % | −2.7 % | −0.2 % | 0.017 / 2.4 % |
| in-slab, shallow | 1.124 | 1.113 | −0.012 | 6.56 | 6.46 | −9.8 % | −4.8 % | −2.2 % | 0.038 / 3.5 % |
| in-slab, intermediate | 1.158 | 1.164 | +0.006 | 7.17 | 7.15 | −10.4 % | −12.9 % | −14.1 % | 0.027 / 2.4 % |
| Jujuy nest | 1.235 | 1.222 | −0.013 | 6.71 | 6.60 | −10.1 % | −4.5 % | −1.5 % | 0.086 / 6.0 % |
| crustal, forearc | 0.984 | 0.972 | −0.013 | 5.43 | 5.33 | −7.8 % | −2.3 % | +0.6 % | 0.046 / 5.4 % |
| crustal, arc | 0.959 | 0.956 | −0.004 | 4.88 | 4.82 | −8.2 % | −6.7 % | −5.9 % | 0.092 / 11 % |
| crustal, backarc | 0.969 | 0.964 | −0.005 | 5.18 | 5.11 | −10.4 % | −8.2 % | −7.1 % | 0.060 / 7.6 % |
| crustal, Patagonia | 0.819 | 0.836 | +0.017 | 3.86 | 3.92 | −5.6 % | −12.7 % | −16.1 % | 0.124 / 16 % |

a is log10 of the yearly number at Mw ≥ 0, so it carries the change of b; the rates are the cleaner reading. Interface segments: N(≥ 5) −7.1 to −8.3 %, b −0.009 to −0.013.

- The weight lowers N(≥ 5) by 8–10 % in every class, three to four times the bootstrap sd for the interface and the in-slab classes, inside it for the arc and Patagonia.
- b moves by −0.01 where the small events are converted (σ 0.19) and the large ones measured (σ 0.08): inside the bootstrap sd everywhere.
- Intermediate in-slab loses 13 % at N(≥ 7): its events of 1964–1975 are ISC-GEM values with σ up to 1.1. With the weight on `direct` and `proxy` only, N(≥ 7) is +3 % and b −0.023.
- Interface, weight on every event instead: N(≥ 5) −8.0 %, N(≥ 7) −7.9 %, N(≥ 8) −7.8 %, b unchanged. The choice for the historical events moves N(≥ 7) by 5 % and N(≥ 8) by 8 %.

**Test 1, same events, two magnitudes** (real data). 6 193 events have a measured Mw and a converted value of their own (rebuilt with `catalog/magnitude.py`; the rebuilt values equal the frozen Mw for all 9 177 converted events of the set). Above a threshold where the measured Mw is complete, the converted values should give more events by exp(β²(σ_c² − σ_m²)/2), and the weighted counts should agree.

| from | Mw ≥ | measured | converted | ratio (5–95 %) | expected | with weights (5–95 %) |
|---|---|---|---|---|---|---|
| 1976 | 5.6 | 765 | 812 | 1.06 (1.03–1.10) | 1.08 | 0.98 (0.95–1.02) |
| 1976 | 5.8 | 495 | 531 | 1.07 (1.03–1.12) | 1.08 | 0.99 (0.96–1.03) |
| 1976 | 6.0 | 316 | 346 | 1.09 (1.04–1.15) | 1.08 | 1.01 (0.96–1.07) |
| 2000 | 5.6 | 478 | 493 | 1.03 (0.99–1.08) | 1.07 | 0.97 (0.93–1.01) |
| 2000 | 5.8 | 309 | 318 | 1.03 (0.98–1.09) | 1.07 | 0.97 (0.92–1.02) |
| 2000 | 6.0 | 202 | 216 | 1.07 (1.01–1.14) | 1.07 | 1.00 (0.95–1.07) |

The converted magnitudes do overcount, by about the expected amount, and the weights bring the two counts together. This is the direction DECISIONS assumes for our inverse-fit conversions. Limits: the thresholds are cumulative, so the rows are not independent; from 2000 alone the excess is 3–7 % and one in three thresholds excludes 1; above Mw 6.2 the converted counts fall below the measured ones (0.92–1.00 from 1976, few events, saturation of mb); the relations were fitted on these pairs; b = 1 in the weights.

**Test 2, synthetic catalogues.** 200 per case with the b and rate of the interface fit, the interface table, and each event dressed with the kind and σ of a real event of its period and size. Fitted over true:

| magnitudes of the historical events | variant | b − true | N(≥ 5) | N(≥ 7) | N(≥ 8) |
|---|---|---|---|---|---|
| carry their listed error | none | −0.024 | +10 % | +23 % | +30 % |
| | instrumental | −0.024 | +1 % | +13 % | +20 % |
| | all events | −0.006 | 0 % | +3 % | +5 % |
| | move and N*, all events | −0.002 | 0 % | +1 % | +1 % |
| are exact | none | −0.006 | +10 % | +13 % | +15 % |
| | instrumental | −0.005 | 0 % | +3 % | +4 % |
| | all events | +0.006 | 0 % | −3 % | −4 % |
| | move and N*, all events | +0.010 | 0 % | −5 % | −6 % |
| are expected values from a regression | none | +0.005 | +10 % | +7 % | +6 % |
| | instrumental | +0.006 | 0 % | −3 % | −4 % |
| | all events | +0.014 | 0 % | −6 % | −9 % |
| | move and N*, all events | +0.017 | −1 % | −8 % | −12 % |

One catalogue scatters by 1.2–1.5 % at N(≥ 5), 4–6 % at N(≥ 7) and 6–10 % at N(≥ 8).

- Without any weight N(≥ 5) is 10 % high in every case. The weight on instrumental events removes that whatever the historical magnitudes are.
- What to do with the historical events decides N(≥ 7) within about ± 10 %, and the right answer depends on what their magnitudes are, which the simulation cannot tell. Weight on instrumental events only: +13 / +3 / −3 % over the three cases. Weight on all events: +3 / −3 / −6 %.
- "Modern only" (no weight on ISC-GEM and Centennial values) leaves N(≥ 7) as biased as no weight at all.
- Moving the magnitudes did not fail here as in the CEUS-SSC simulations: the interface table has one step below Mw 7.

`tests/test_magerr.py`: on a synthetic catalogue with σ 0.25 the unweighted rate is exp(β²σ²/2) too high and the weighted rate and b come back within 2 % and 0.01; kinds not listed keep a count of 1.

## 7. An automatic completeness table (added 15 Nov)

`b9_11_autotable.py`, `tables/auto_tables.csv`, `auto_runs.csv`, `auto_synthetic.csv`, `figs/auto_table.png`, `tests/test_autotable.py`. Two rules were built; in both a larger magnitude is complete no later than a smaller one.

**Joint rule (rates only).** Magnitude bands of 0.5 and blocks of 5 years from 1500. With a Gutenberg–Richter line, a band is complete from one year on: after it the counts follow the line, before it a step function of lower rates, each step paid with a BIC penalty. The years of all bands are chosen together, the line is refitted with Weichert on the chosen table until nothing moves, and five starting tables are tried.
- On synthetic catalogues (30 per case, stationary) it finds the table: steps below Mw 6.5 within one block, b +0.003 to +0.008, N(≥ 5) −0.4 to −0.9 %, N(≥ 7) −2 to −4 %. Steps of Mw ≥ 7 come out up to 40 years too early where the catalogue is only mildly incomplete: too few events to see it.
- On the real catalogue it fails. With all counts it reads everything before 2010 as incomplete below Mw 6.0 (all events: "6.0 from 2010", 377 events used). With declustered counts it gives the interface "4.5 from 2000, 5.5 from 1965" and b 1.08, and expects 9.6 events of Mw ≥ 8 where 19 are observed. The starting tables do not all end at the same table. The rule takes the higher rates of 2010–2015 for the complete level, as the automated Stepp test did. A rate rule cannot tell a real rate change from incompleteness.

**Hybrid rule.** From 1964 the steps come from the shape of the magnitude distribution, which does not need stationary rates: Mc per window and region of part 2 (largest region, larger of KS and b-stability), and a magnitude is complete from the window after the last one whose Mc is above it. Before 1964 the rate rule is used for the 0.5 bands above the top instrumental step, with the line of the instrumental fit held fixed, so nothing is iterated. A band with no event gets no step.
- Mc per window: 5.2, 5.0, 4.8, 4.7, 5.0, 4.7, 4.4 → instrumental steps for every class: **4.5 from 2020, 4.7 from 2012, 5.0 from 1976, 5.2 from 1964**.
- Synthetic, instrumental steps given: historical steps of Mw 5.5–6.5 exact, Mw 7.0 and 7.5 up to 40 years early in the mildly incomplete case, b +0.003 to +0.007, N(≥ 5) −0.3 %, N(≥ 7) −1.5 to −3 %.

| unit | table | b Weichert (sd) | b Kijko–Smit | N(≥ 5) | N(≥ 7) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|
| interface, hybrid | steps above, 5.5 / 1960, 6.5 / 1955, 7.0 / 1900, 7.5 / 1830, 8.0 / 1500 | 0.950 (0.015) | 0.942 | 27.4 | 0.345 | 64.2 / 59.1 | 20.0 / 19.0 |
| interface, hybrid from 5.0 | | 0.954 (0.020) | 0.918 | 27.4 | 0.338 | 62.8 / 59.1 | 19.4 / 19.0 |
| interface, 5.0 from 1964 only | | 0.919 (0.021) | 0.920 | 26.6 | 0.386 | 24.2 / 24.7 | 2.9 / 4.0 |
| interface, B9 candidate | 5.0 / 1964, 7.0 / 1900, 7.5 / 1820, 8.0 / 1730 | 0.929 (0.017) | 0.913 | 26.5 | 0.368 | 60.5 / 55.7 | 12.6 / 15.6 |
| in-slab family, hybrid | steps above, 6.0 / 1960, 6.5 / 1950, 7.0 / 1830, 7.5 / 1500 | 1.179 (0.014) | 1.200 | 42.9 | 0.188 | 52.9 / 61.9 | 6.5 / 3.4 |
| in-slab, 5.0 from 1964 only | | 1.162 (0.026) | 1.162 | 41.0 | 0.194 | 12.2 / 14.3 | 0.8 / 0 |
| crustal family, hybrid | steps above, 5.5 / 1960, 6.0 / 1925, 6.5 / 1905, 7.0 / 1845 | 0.932 (0.020) | 0.959 | 7.7 | 0.105 | 19.1 / 14.0 | 2.2 / 0 |
| crustal, hybrid from 5.0 | | 1.022 (0.026) | 0.972 | 8.4 | 0.076 | 13.8 / 14.0 | 1.3 / 0 |
| crustal, 5.0 from 1964 only | | 0.980 (0.038) | 0.980 | 8.0 | 0.087 | 5.5 / 2.0 | 0.6 / 0 |

- Interface: the automatic table lands next to the candidate read by hand (b 0.95 against 0.93, N(≥ 7) −6 %) and passes both large-event checks. It reads Mw ≥ 8 as complete from 1500 (20 expected, 19 observed), Mw ≥ 7.5 from 1830, Mw ≥ 7 from 1900.
- In-slab: the rule accepts Mw ≥ 7 from 1830 and Mw ≥ 7.5 from 1500, because it only objects to too few events and the old in-slab record has too many (62 against 53 at Mw ≥ 7). The literature says that record is incomplete. Here the historical steps should not be used; "5.0 from 1964 only" or the instrumental steps alone are the automatic answer.
- Crustal: with the floor at 4.5 the fit gives b 0.93, with 5.0 it gives 1.02: the first three steps hold 120 of 660 events and move b by 0.09. Few events; rough numbers either way.
- The steps at 1950–1960 for Mw 5.5–6.5 are the rule saying those bands reach one or two blocks before 1964. They add 30–40 events and could be dropped.

**Weichert and Kijko–Smit.** Kijko and Smit (2012) take b from the magnitudes inside each period of the table and weight the periods by their events; Weichert also uses how many events each period holds against its length. With one period they are the same number. On a table that fits the catalogue they agree within the bootstrap sd (hybrid interface 0.950 / 0.942; candidate 0.929 / 0.913). On the tables of the joint rule they differ by 0.06–0.17. So the difference between the two is a check of the table, and Kijko–Smit is not a second opinion on b once the table is right.

**What is still chosen by hand in the hybrid rule:** the seven windows and five regions of the Mc table, at least 100 events per window, "larger of two Mc methods, largest region" (cautious, reads high), bands of 0.5 and blocks of 5 years, the BIC penalty, and 1964 as the year where the rule changes.

## 8. Every class on the single table (added 15 Nov)

`b9_12_refit.py`, `tables/refit_single_table.csv`, `figs/refit_single_table.png`. Table for every class: **Mw 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500** (instrumental steps from the whole-catalogue Mc, historical steps from the rate rule on all events, floor 5.0, the steps at 1955–1960 dropped). Full catalogue, class weights, no magnitude-error correction. Largest magnitude in the likelihood: none for the interface margin, the segment Mmax of DECISIONS, observed maximum + 0.2 for the other classes.

| class | events | b (sd) | b Kijko–Smit | b-positive | a | N(≥ 5) (5–95 %) | N(≥ 7) (5–95 %) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|---|---|
| interface | 1 649 | 0.958 (0.017) | 0.931 | 0.893 | 6.18 | 27.5 (26.5–28.5) | 0.333 (0.286–0.375) | 60.6 / 58.5 | 18.9 / 19.0 |
| in-slab, shallow | 602 | 1.147 (0.038) | 1.156 | 1.185 | 6.69 | 10.3 (9.7–11.0) | 0.052 (0.038–0.068) | 7.8 / 10.4 | 1.1 / 1.3 |
| in-slab, intermediate | 1 649 | 1.136 (0.026) | 1.172 | 1.195 | 7.07 | 28.2 (27.0–29.3) | 0.151 (0.124–0.183) | **22.4 / 37.6** | 3.2 / 1.0 |
| Jujuy nest | 241 | 1.237 (0.090) | 1.245 | 1.159 | 6.75 | 4.17 (3.75–4.58) | 0.014 (0.006–0.023) | 1.3 / 3.0 | – |
| crustal, forearc | 226 | 0.999 (0.058) | 1.023 | 0.924 | 5.53 | 3.86 (3.56–4.18) | 0.039 (0.024–0.061) | 3.2 / 4.1 | – |
| crustal, arc | 85 | 1.003 (0.101) | 1.075 | 1.156 | 5.12 | 1.44 (1.18–1.71) | 0.014 (0.006–0.029) | 1.8 / 2.5 | – |
| crustal, backarc | 153 | 0.988 (0.068) | 0.985 | 1.160 | 5.30 | 2.59 (2.26–2.91) | 0.027 (0.016–0.044) | 3.1 / 2.4 | – |
| crustal, Patagonia | 41 | 0.999 (forearc) | | | 4.79 | 0.69 (0.51–0.88) | 0.007 | 1.0 / 2.0 | 0.1 / 0 |

Interface segments (S to N): b 0.903, 0.989, 0.938, 0.973 (sd 0.03–0.05); N(≥ 5) 3.19, 9.32, 8.04, 6.20; all pass the check at Mw ≥ 7 and 8 (32–26° S at the edge: 18.0 fitted, 11.0 observed).

- Every class passes the large-event check except intermediate in-slab at Mw ≥ 7 (22 fitted, 38 observed): the old events again, now inside the table from 1905.
- Weichert and Kijko–Smit agree within two bootstrap sd everywhere. b-positive is 0.07 lower for the interface and 0.04–0.17 away for the small classes (24–74 pairs there).
- Patagonia alone gives b 0.86 on 41 events; with the forearc b its rate is 0.69 per year at Mw ≥ 5.
- Against the table read by hand (section 3): interface b 0.958 against 0.929, N(≥ 5) 27.5 against 26.5, N(≥ 7) 0.333 against 0.368.

**Weight on all events against none** (same table; `tables/refit_single_table.csv`, columns `_w`).

| class | b none | b all | N(≥ 5) none | all | change | N(≥ 7) change | N(≥ 8) change | Mw ≥ 7 fitted / observed, none | all |
|---|---|---|---|---|---|---|---|---|---|
| interface | 0.958 | 0.962 | 27.5 | 25.2 | −8 % | −10 % | −11 % | 60.6 / 58.5 | 54.4 / 49.7 |
| in-slab, shallow | 1.147 | 1.153 | 10.3 | 9.2 | −10 % | −13 % | −14 % | 7.8 / 10.4 | 6.8 / 7.5 |
| in-slab, intermediate | 1.136 | 1.156 | 28.2 | 25.3 | −10 % | −18 % | −22 % | 22.4 / 37.6 | 18.3 / 29.4 |
| Jujuy nest | 1.237 | 1.236 | 4.17 | 3.74 | −10 % | −10 % | | 1.3 / 3.0 | 1.2 / 2.4 |
| crustal, forearc | 0.999 | 0.984 | 3.86 | 3.55 | −8 % | −1 % | | 3.2 / 4.1 | 3.2 / 3.6 |
| crustal, arc | 1.003 | 1.004 | 1.44 | 1.31 | −9 % | −10 % | | 1.8 / 2.5 | 1.6 / 2.2 |
| crustal, backarc | 0.988 | 0.987 | 2.59 | 2.30 | −11 % | −10 % | | 3.1 / 2.4 | 2.8 / 2.1 |
| crustal, Patagonia | 0.999 | 0.999 | 0.69 | 0.64 | −8 % | −8 % | | 1.0 / 2.0 | 0.9 / 1.7 |

- The weight is close to one factor for the whole line: b moves by 0.02 at most (inside its bootstrap sd in every class), and the rates fall by 8–11 % at Mw ≥ 5 and about the same above. Interface, mean count per event in the table: 0.92 at Mw 5.0–5.4, 0.93 at 5.5–6.9, 0.91 at 7.0–7.4, 0.86 at 7.5–7.9, 0.77 at Mw ≥ 8 (σ 0.14, 0.08, 0.25, 0.20, 0.30).
- The large-event check comes out the same way with and without (the observed counts carry the weights too). Only intermediate in-slab fails in both; segment 32–26° S fails with the weight (17.0 fitted, 9.6 observed) and is at the edge without.
- So the choice is a rate level of about 9 %, not a shape. From section 6: without the weight N(≥ 5) was 10 % high in every synthetic case; with it on all events N(≥ 7) was +3, −3 and −6 % over the three kinds of historical magnitudes, against +23, +13 and +7 % with none.

**Decided 15 Nov (Pablo): the weight on all events.** `b9_12_refit.py` now runs with it (`MAGERR = True`); the table and the figure are the weighted fits, and the columns `_none` keep the fits without it.

| class | events (counted) | b (sd) | b Kijko–Smit | b-positive | a | N(≥ 5) (5–95 %) | N(≥ 7) (5–95 %) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|---|---|
| interface | 1 649 (1 511) | 0.962 (0.017) | 0.915 | 0.881 | 6.17 | 25.2 (24.3–26.2) | 0.300 (0.260–0.335) | 54.4 / 49.7 | 16.9 / 14.7 |
| in-slab, shallow | 602 (539) | 1.153 (0.037) | 1.131 | 1.163 | 6.67 | 9.24 (8.71–9.83) | 0.046 (0.034–0.060) | 6.8 / 7.5 | 0.9 / 0.6 |
| in-slab, intermediate | 1 649 (1 475) | 1.156 (0.027) | 1.165 | 1.168 | 7.13 | 25.3 (24.2–26.3) | 0.123 (0.101–0.151) | **18.3 / 29.4** | 2.5 / 0.9 |
| Jujuy nest | 241 (216) | 1.236 (0.090) | 1.219 | 1.138 | 6.69 | 3.74 (3.35–4.11) | 0.013 (0.006–0.022) | 1.2 / 2.4 | – |
| crustal, forearc | 226 (208) | 0.984 (0.058) | 1.000 | 0.916 | 5.42 | 3.55 (3.28–3.85) | 0.038 (0.024–0.060) | 3.2 / 3.6 | – |
| crustal, arc | 85 (77) | 1.004 (0.100) | 1.061 | 1.166 | 5.09 | 1.31 (1.07–1.55) | 0.013 (0.005–0.025) | 1.6 / 2.2 | – |
| crustal, backarc | 153 (136) | 0.987 (0.070) | 0.975 | 1.133 | 5.25 | 2.30 (2.01–2.59) | 0.024 (0.014–0.040) | 2.8 / 2.1 | – |
| crustal, Patagonia | 41 (38) | 0.984 (forearc) | | | 4.68 | 0.64 (0.47–0.81) | 0.007 | 0.9 / 1.7 | 0.1 / 0 |

Interface segments (S to N): b 0.915, 0.996, 0.934, 0.973; N(≥ 5) 2.94, 8.48, 7.41, 5.70. Segment 32–26° S fails the check at Mw ≥ 7 (17.0 fitted, 9.6 observed); the others pass. For the interface Kijko–Smit is now 0.047 below Weichert, 2.8 bootstrap sd (0.027 without the weight): the weight lowers the old large events more than the small ones, and Weichert reads that through the counts per period.

**Not acted on, to be named in the discussion of the paper (Pablo, 15 Nov):** the intermediate in-slab events of Mw ≥ 7 before 1976 (29 observed against 18 fitted, by weight), and the step Mw 8.0 from 1500 with its uncertain magnitudes before about 1730.

## Candidate completeness tables

| class | network history | change points (latest of full, GK, NN) | one window + long record | read of the evidence |
|---|---|---|---|---|
| interface | 4.5 / 2000, 5.0 / 1976, 5.5 / 1964, 6.5 / 1930, 7.0 / 1900 | 4.5 / 2006, 5.0 / 1964, 6.0 / 1960, 7.0 / 1900 | 5.0 (or 5.2) / 1964, 7.0 / 1900, 7.5 / 1820, 8.0 / 1730 | third column passes all checks; first two fail Mw ≥ 7 and 8 |
| in-slab, shallow | same | 4.5 / 1973, 5.5 / 1959, 6.0 / 1900 | 5.0 / 1964, 7.0 / 1900 | all pass; b 0.96–1.15 depending on the table; half the weight is split events |
| in-slab, intermediate | same | 4.5 / 2002, 5.0 / 1971, 5.5 / 1965, 6.0 / 1929, 7.0 / 1906 | 5.0 / 1964 only | anything before 1964 at Mw ≥ 7 fails; b 1.12–1.16 whatever the table |
| Jujuy nest | same | 4.5 / 2005, 5.5 / 1968, 6.0 / 1900 | 5.0 / 1964 | b depends on the floor, not on the table |
| crustal, forearc | same | 4.5 / 2001, 5.0 / 1972, 5.5 / 1900 | 5.0 / 1964 (5.5 / 1976?), 7.0 / 1900 | "5.5 from 1900" is not credible (Mw 5.5–5.9: 0.06 per year before 1950, 0.2–1.2 after) |
| crustal, arc | same | 4.5 / 1999, 5.0 / 1975, 5.5 / 1900 | 5.0 / 1964, 7.0 / 1900 | thin |
| crustal, backarc | same | 4.5 / 1973, 5.0 / 1964, 6.0 / 1900 | 5.0 / 1964, 7.0 / 1900 | 1976–1989 dominates |
| crustal, Patagonia | same | 4.5 / 2003, 5.0 / 1970, 5.5 / 1949 | 5.0 / 1964, 7.0 / 1900 | 62 events |
| outer rise (reported) | same | 4.5 / 2009, 5.0 / 1961, 5.5 / 1900 | | b 1.04–1.12; 8 events of Mw ≥ 7, 5 before 1930 |
| Antarctic interface (reported) | same | 4.5 / 2016, 5.0 / 1954, 5.5 / 1900 | | 142 events, b 0.9–1.1 |

Historical steps for the interface and the large in-slab events: Lomnitz (7.5 / 1535), counts (7.5 / 1820, 8.0 / 1730), long (7.0 / 1819, 8.0 / 1570), old (8.3 / 1513). For the in-slab classes the literature says the historical record is incomplete for deep and intermediate events throughout (Albini et al. 2013), and the counts agree: no historical step is supported there.

## Assumptions

- End of the catalogue 2026.87 (last event); years as decimal years.
- Gutenberg–Richter without taper or Mmax up to Mw 9.7 in the likelihood; the tapered form of DECISIONS (corner 9.6) changes N(≥ 8) by a few per cent, not tested.
- Interface segments by the epicentre latitude, bounds of `psha_chile7/interface/config.py` (−45.6, −37, −32, −26, −17.6), copied, not imported. Regions of the spatial part are the same bands plus the far south.
- Events with weight between 0 and 1 enter every estimator by their weight, pairs in b-positive by the product. The bootstrap resamples events (Poisson multiplicities), with the weights carried; the two halves of a moved event are resampled together.
- Change points: at least 5 years per segment (15 at Mw ≥ 7), penalty 1.5 ln(n) times the dispersion; "complete since" = the last break where the rate before is below 0.6 of the rate after. Stepp: 2 standard errors, reference 20 years.
- KS Mc: p 0.1, 200 simulations, sample size capped at 3 000 (as psha_chile6).
- Declustering on all classes together, Mw ≥ 4.5, the whole time span. GK foreshock window = aftershock window. Nearest neighbour: b 1, d_f 1.6, depth not used, one threshold.
- σ of the magnitude as in the catalogue; β of the correction from the uncorrected fit.
- mb case: events before 1990 whose relation is ISC mb or NEIC mb. Old in-slab events at the ISC-GEM values of the A6 report (6.9, 6.3, 6.5, 6.3).
- Baseline of the tornado: network table (+ counts for interface and in-slab), all events, full catalogue, no correction. It is the reference, not a recommendation: on the interface it is the table that fails.
- Poisson bands 5–95 %; an observed weighted count is compared as it is.

## Failures and skips

- CEUS-SSC (2012) report not on disk: equations not checked (brief, fallback used and both variants run).
- `classify.py` could not be imported from the frozen `code/` copy (its relative data paths do not resolve there); the identical `catalog/classify.py` was used.
- geopandas cannot read shapefiles in `psha_renta` (GDAL data directory broken); the coast in the maps is read with pyshp.
- Not run: Kijko–Smit, Ogata–Katsura / EMR joint fits, Reasenberg (one alternative was asked for); the tapered MFD; the classes with the mechanism rule switched off; hazard effect of any of this.
- Stepp is automated crudely and should not be read alone.
- Step 0 was done by a sub-agent; I did not repeat its recount.

## Run times (16 cores, single process)

`b9_2_decluster.py` 11 s; `b9_1_completeness.py` 15 s; `b9_0_bands.py` 50 s; `b9_3_fits.py` 150 s; `b9_4_space.py` 3 s; `b9_5_checks.py` and `b9_6_deeper.py` under 30 s each; `b9_7_figs.py` 40 s; tests 3 s (15 pass).
