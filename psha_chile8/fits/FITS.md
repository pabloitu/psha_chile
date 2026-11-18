# Fits: Gutenberg–Richter parameters per class and interface segment

Final form (B15, 17 Nov 2026). The method below is what `run.py`, `run_declustered.py` and `run_pad.py` do; it is written to become the statistics section of the paper. **Numbers are those of the trial on catalogue 2026-11-17f (`drafts/fits/trial/`, not used); the final run on the catalogue of A11 replaces them.** Earlier runs (15–16 Nov, catalogues 2026-11-14c to 2026-11-16c) and how each rule came about: `FITS_history.md`. Declustering: `DECLUSTER.md`. Rules: DECISIONS, Statistics and Interface.

## 1. Data and units

- **Catalogue.** The frozen catalogue named in `CURRENT.md` ("frozen catalogue (final)"), read by `gr.load()`: events in the domain with Mw ≥ 3.5, decimal year, and one weight per class (the class weight of the event). An event counts in a unit by its class weight; events split between classes count in each by their share.
- **Units.** Interface: the whole margin and four segments by epicentral latitude (45.6–37° S, 37–32° S, 32–26° S, 26–17.6° S). In-slab: shallow, intermediate depth, Jujuy nest. Crustal: forearc, arc, backarc, Patagonia, and the crustal family (the four together) for the shared b. Crustal events outside the crustal grid (`outside`), outer-rise and Scotia–Antarctic events are in no unit. Arica 1868 (17.15° S) counts in the margin unit only.
- **Magnitudes** are 0.1 bins (centres); N(≥ 7) is the yearly rate in the bin 7.0 and above (Mw ≥ 6.95).
- **Magnitude error.** Every event counts exp(−β²σ²/2) times its class weight, β = b ln 10 of its own fit (iterated), σ the Mw uncertainty of the catalogue (CEUS-SSC 2012, eq. 3.3.1-1). Section 8 gives the σ by source.

## 2. Completeness

One table for every class, read on all events, because completeness is a property of the catalogue and its networks, not of the tectonic class (DECISIONS, Statistics):

| Mw from | complete since | from |
|---|---|---|
| 5.0 | 1976 | automatic, instrumental |
| 5.2 | 1964 | automatic, instrumental |
| 7.0 | 1905 | automatic, historical; both published checks agree |
| 7.5 | 1830 | automatic, historical; Mw 8.0–8.4 included (17 Nov) |
| 8.5 | 1550 | historical record of the margin (18 Nov) |

- **Instrumental steps (from 1964).** For each network window and region, Mc from the events of Mw ≥ 3.5 by b-stability (Cao and Gao 2002; Woessner and Wiemer 2005) and by a Kolmogorov–Smirnov test (Clauset et al. 2009); the larger of the two and the largest region; a magnitude is complete from the window after the last one whose Mc is above it (`table.py`; windows in `tables/mc_windows_<date>.csv`). `run.py` recomputes them and stops if they differ from the table. They agree with the Mc of every region (Mc ≤ 5.0 after 1976, 5.1–5.2 in 1964–1976).
- **Mc in time, measured** (`table.auto`, written by every run as `tables/mc_series_<date>.csv`, `mc_table_<date>.csv`, figure `figs/<date>/mc_time.png`): Mc(t) per latitude segment (the four interface segments) by moving windows of 250 events, step 50 (Woessner and Wiemer 2005), each with b-stability and the KS test (the larger) and a bootstrap of 30; in a segment a magnitude is complete from the end of the last window whose Mc is above it beyond one bootstrap sd; the table of the catalogue is the envelope of the four (the latest year). On 17f:

| segment | steps |
|---|---|
| north, 15–26° S | 5.0 from 1964, 4.8 from 1984, 4.5 from 1995, 4.4 from 1996, 4.1 from 2009 |
| central-north, 26–32° S | 5.1 from 1964, 5.0 from 1978, 4.8 from 1987, 4.6 from 1996, 4.3 from 2003, 4.1 from 2016 |
| central, 32–37° S | 5.1 from 1964, 5.0 from 1990, 4.7 from 1998, 4.3 from 2011, 3.8 from 2019 |
| south, 37–46° S | 5.2 from 1964, 4.7 from 1999, 4.4 from 2011, 4.0 from 2017 |
| envelope (catalogue) | 5.2 from 1964, 4.7 from 1999, 4.4 from 2011, 4.2 from 2017, 4.1 from 2019 |

  Mc falls from 5.0–5.2 before 1990 to 4.4–4.7 around 2000 and 3.8–4.3 in the last decade; short rises follow the 1985, 2010, 2014 and 2015 mainshocks. The south sets the envelope until 1999: its windows of 1984–1991 read 5.4 with a narrow bootstrap band. The far south (46–60° S) has enough events only from 2015 (Mc 4.4–4.7) and is not in the envelope. Spatial Mc maps per window (supplement): `drafts/fits/completeness/mc_maps.png`.
- **Caution, from synthetic catalogues** (true steps 5.2 from 1964, 5.0 from 1976): Mc(t) reads 5.0–5.2 before 1976 and ≤ 5.0 after, but where Mc sits at about 5.0 the last-window rule can put the 5.0 step years late (1977 and 1999 in two of four catalogues). So the step of a magnitude near the plateau of Mc(t) is the weak point of the rule; steps well above or below it are robust.
- **Fit floor:** the fits start at Mw 5.0 (Pablo, 17 Nov). The b-stability of the fits themselves (`drafts/fits/completeness/fit_floor.png`) gives floors of 4.4–4.8 in every unit but the Jujuy nest (b falls with the floor; section 5), so 5.0 is above the floor the data need.
- **Open (Pablo):** the measured envelope gives Mw 5.0 complete from 1999 (the south), the fits use 5.0 from 1976. With 5.0 from 1999 (trial of 17 Nov): interface b +0.03 to +0.06, N(≥ 7) × 0.83–0.93; crustal and in-slab within 1.1 sd; the large-event checks unchanged.
- **Historical steps (before 1964).** The automatic rule: for 0.5 bands, the earliest year from which the counts in 5-year blocks stay consistent with the instrumental Gutenberg–Richter line (Poisson change point, BIC); a step is kept only if it reaches at least 10 years before 1964. It is our construction, so every run also applies two published methods to the same events (`table.checks`, `tables/table_checks_<date>.csv`): Hakimhashemi and Grünthal (2012), the variance of interevent times per band with an F-test at 0.8, and Albarello et al. (2001), a distribution-free sign test of early against late counts per class. The table keeps the steps they support.
- **Crustal classes** use the steps from 1976 only (Mw 5.0 from 1976). In 1964–1975 they are short of events at Mw 5.5–5.9, and their historical steps would rest on one or two events in regions with no early record. Interface and in-slab units keep the whole table.

**Justification of the historical steps** (catalogue 17f, whole margin; `drafts/fits/completeness/` for the stability runs):

| Mw | automatic rule | Hakimhashemi–Grünthal | Albarello | table |
|---|---|---|---|---|
| 7.0 | 1905 | 1904 (stable over level 0.7–0.9, full or declustered) | 1907 (stable over 5–20-year subintervals; interquartile about 1870–1947) | 1905 |
| 7.5 | 1830 | 1834 (1904 at level 0.7) | 1907 (1887–1947) | 1830 |
| ≥ 8 | 1500 | 1819 (1513–1823 over level and band edges) | 1767 (uninformative, see below) | 8.0–8.4 in 7.5 from 1830; ≥ 8.5 from 1550 |

- **On synthetic catalogues with a known table** (100 per detection model): the automatic rule puts the 7.0 step 30–75 years early (section 9). Hakimhashemi–Grünthal: median error −21 to +20 years up to Mw 7.0, −20 to −59 at 7.5; in a dense band it triggers by chance near the present (one test per event), so it says nothing below Mw 7. Albarello: 7–38 years early up to 7.0, 53–123 early at 7.5; for Mw ≥ 8 it returns about 1650–1700 whatever the data (with so few events every start is equally likely and the span weight sets the median), so it cannot resolve that class.
- **7.0 from 1905:** all three agree within 3 years.
- **8.0 from 1500 dropped (Pablo, 17 Nov):** neither published method supports it; Mw ≥ 8 on the margin is short of the fit before 1830 (observed / fitted 3 / 3.7 in the 1500s, 2 / 3.7 in the 1600s, 4 / 4.8 in 1700–1829, against 4 / 2.8 and 8 / 4.5 after 1830); and the colonial record covers central Chile, not the far south or the Atacama, while the table holds for the whole margin. The events before 1830 (1513, 1570, 1575, 1604, 1647, 1657, 1730, 1751, 1819, 1822) stay in the catalogue and in Mmax (largest event of any year; 1730 sets the Mmax of 37–32° S). Effect: interface b 0.961 → 0.947, N(≥ 7) × 1.07, N(≥ 8) × 1.10; segments N(≥ 8) × 0.95–1.23; in-slab under 4 %; all inside the bootstrap intervals (margin N(≥ 7) about −25 / +30 %). Interface 32–26° S then passes its large-event check. A start at 1600 or 1700 was tested (N(≥ 8) × 1.03, × 1.08) and not taken: no method selects it.
- **8.5 from 1550 (Pablo, 18 Nov):** the start is set by the record, not by an event: Santiago (1541), La Serena (1544), Valparaíso (1544), Concepción (1550), Valdivia (1552), Villarrica (1552), Angol (1553 or 1558, sources differ), Osorno (1558) and Castro (1567) in Chile, and the Peruvian record (Lima 1535, Arica 1541) for the north. The southern towns between Concepción and Chiloé were destroyed in 1598–1602 (the destruction of the seven cities); Concepción and Castro stayed, and Valdivia was resettled in 1645, so the south keeps a record at both ends of the segment through the gap. Sources: Memoria Chilena (Osorno 1558–1950; Valdivia colonial), Wikipedia (Villarrica; timeline of Chilean history), not checked against a historiographic study; an Mw ≥ 8.5 floods and damages a long stretch of coast, so the one unsettled stretch, the Atacama (Copiapó 1744), does not hide one (1819 and 1922 are recorded). Mw ≥ 8.5 interface events: 1604, 1730, 1751, 1819 before 1830 (1.4 per century from 1550) and 1837, 1868, 1877, 1922, 1960, 2010 after (3.0), consistent with one rate for six and four events. The great earthquakes below 8.5 before 1830 (1570, 1575, 1657, 1822) stay in the catalogue and in Mmax but not in the rate. A threshold and start read off one event (8.3 from 1575, 8.5 from 1604) were tried and not taken: they bias the rate up; all variants give the same fits within 0.004 in b and 3 % in N(≥ 8). Effect against the table without the step: margin b 0.947 → 0.948, N(≥ 8) × 0.99; every large-event check passes, interface 32–26° S included (16.4 / 10.0). A step 8.0 from 1500 fits the points best but assumes every Mw 8 since 1500 was recorded along the whole margin, which the counts per segment do not support (1550–1829 against 1830–2026 per century: 37–32° S 1.8 / 1.5, 45.6–37° S 0.4 / 1.5, 32–26° S 0.4 / 1.0, 26–17.6° S 0 / 1.5).
- **7.5 from 1830 kept:** Hakimhashemi–Grünthal (per band 7.5–7.9) supports it; Albarello (class ≥ 7.5) gives about 1907 but is the less precise method and runs early on synthetic catalogues, so its late answer is a hint that the 19th-century record above 7.5 is short. Named for the discussion.
- **Declustering:** completeness stays read on the full catalogue (Pablo, 17 Nov). Both published methods give the same steps on the declustered catalogues (Albarello et al. 2001 need no aftershock removal; Hakimhashemi and Grünthal 2012 used declustered data).
- **The step 5.2 from 1964** is not short: the yearly rate of 1964–1975 equals that of the 1990s (Mw 5.2–5.9: 33.8 against 31.8; declustered 20.2 against 20.0). It looks short only against a rate raised by the sequences of 1985 and 2010–2015.

**For the discussion of the paper:** the large-magnitude rates rest on the historical steps, and there the record is spatially uneven (central Chile documented since the 16th century, the south and north much later). Two published statistical methods agree on Mw 7.0 from about 1905; for Mw ≥ 7.5 they part (1834 against 1907), and for Mw ≥ 8 neither can resolve completeness before 1830. The choice moves interface N(≥ 8) by about 10 %, inside the uncertainty of the fit. Rules that compare rates between periods are sensitive to the sequences of 2010–2015.

## 3. Estimator, shapes, Mmax

- **Maximum likelihood on the table** with the class weights and the magnitude-error weight (Weichert 1980 for unequal observation times); bins above the Mmax of the unit are left out of the likelihood. Uncertainty: bootstrap of whole clusters (each mainshock with its fore- and aftershocks, from the `nn_family` declustering; 2 000 resamples), so that the intervals carry the clustering of a full catalogue; intervals are 5–95 %. The large-event check takes a negative binomial band whose variance is the expected number times the dispersion of the observed clusters at that magnitude (Poisson where every cluster holds one event). Our construction from standard parts (cluster bootstrap, compound Poisson counts), not a published PSHA recipe; rates stay those of the full catalogue (Marzocchi and Taroni 2014 argue that declustered rates underestimate the hazard). DECISIONS, Statistics (Pablo, 17 Nov). The completeness table read on the declustered catalogues was tested and not taken (same section).
- **Two shapes, both into the logic tree.** Tapered (Kagan 2002a), preferred; and cut at Mmax (OpenQuake truncated Gutenberg–Richter). Each has its own likelihood and its own a:
  - cut: N(≥ M) = 10^(a − bM) − 10^(a − b Mx), Mx = Mmax + 0.05;
  - tapered: N(≥ M) = 10^(a − bM) × exp((M0(4.95) − M0(M)) / M0(corner)); the line does not end at Mmax.
- **Mmax** = the largest observed event of the unit + 0.2, among events with class weight 1, of any year. The same rule in every unit, interface included.
- **Corner** of the tapered line from Mmax and the b of the unit (Kagan 2002b, eq. 12): M0(corner) = M0(Mx) (β/Γ(2 − β))^(1/(1 − β)), β = 2b/3, so that the tapered line releases the moment rate of the cut line. The corner is 0.20–0.23 below Mmax for these b values.
- **Crustal b.** The four crustal classes share the b of the crustal family fitted as one unit (inside the crustal grid); each class keeps its own rate, Mmax and corner. In the bootstrap each class takes the family b of the same replicate. A class of 10–180 counted events cannot hold its own b (own b: forearc 0.91, arc 1.04, backarc 1.26, Patagonia 1.66).
- **Jujuy nest:** own fit at the floor of the table, no pooling.
- **Interface b** is a tornado factor with three options: b per segment (the fits below), one b shared by the four segments (random-effects mean, from `run_declustered.py`, rows `b_option` shared) and the b of the whole margin.
- **Interface (a, b) branches.** 5th percentile, maximum likelihood and 95th percentile of the rate at the controlling magnitude (8.8, at most Mmax − 0.3), weights 0.185 / 0.63 / 0.185. The pair of a branch is the expected (a, b) given that rate, from the bootstrap covariance of (a, b) (correlation 0.99).
- **Source MFDs** go to OpenQuake as evenly discretised lists: bin rates are differences of the fitted cumulative line at the bin edges (`gr.rates`), the tapered list ends at Mmax + 0.2 with the rate of the line above in its last bin. `gr.rates` stops at Mw 9.7 (`MTOP`): a caller with a corner near 9.5 extends the grid itself (S1 does).
- **Rates from the full catalogue** in every class. The declustered fits (section 6) are an alternative rate branch and give the pattern of the smoothed sources.

## 4. Fits

Tapered line; the cut line gives the same b within 0.003 (nest 0.007) and N(≥ 6) within 1 %; both are in `tables/fits_<date>.csv`. Intervals 5–95 %. Fitted / observed: events of Mw ≥ 7 (≥ 8) the line expects inside the completeness table against the weighted count there; bold outside the 5–95 % band. Intervals in this table are still those of the event bootstrap (trial before the cluster bootstrap); with clusters the N(≥ 7) interval of the interface units widens 1.3–2.9 times, the in-slab and crustal ones by under 15 %; the two failures stay (no clustering among their large events).

| unit | events (counted) | Mmax | corner | b (sd) | N(≥ 5) | N(≥ 6) | N(≥ 7) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|---|---|
| interface | 1 908 (1 509) | 9.7 | 9.49 | 0.961 (0.018) | 25.1 | 2.75 (2.54–2.96) | 0.301 (0.261–0.345) | 55.0 / 52.8 | 17.3 / 15.8 |
| interface, 45.6–37° S | 228 (178) | 9.7 | 9.47 | 0.906 (0.051) | 2.94 | 0.365 (0.286–0.433) | 0.0453 (0.0288–0.0620) | 8.6 / 11.0 | 2.9 / 2.8 |
| interface, 37–32° S | 643 (505) | 9.2 | 9.00 | 0.996 (0.034) | 8.47 | 0.855 (0.736–0.974) | 0.0863 (0.0646–0.109) | 15.3 / 12.6 | 4.4 / 5.5 |
| interface, 32–26° S | 565 (444) | 8.7 | 8.48 | 0.941 (0.031) | 7.39 | 0.846 (0.736–0.954) | 0.0964 (0.0746–0.120) | **17.2 / 9.9** | 4.9 / 2.6 |
| interface, 26–17.6° S | 418 (341) | 9.1 | 8.89 | 0.966 (0.039) | 5.69 | 0.615 (0.517–0.715) | 0.0664 (0.0481–0.0864) | 12.0 / 15.5 | 3.6 / 2.9 |
| in-slab, shallow | 1 124 (543) | 8.2 | 8.03 | 1.131 (0.039) | 9.29 | 0.688 (0.585–0.793) | 0.0498 (0.0364–0.0655) | 7.5 / 8.7 | 0.8 / 0.4 |
| in-slab, intermediate depth | 1 673 (1 474) | 8.2 | 8.04 | 1.157 (0.026) | 25.3 | 1.76 (1.58–1.95) | 0.120 (0.098–0.146) | **17.9 / 28.5** | 1.9 / 0.9 |
| Jujuy nest | 241 (216) | 7.4 | 7.26 | 1.229 (0.090) | 3.74 | 0.219 (0.148–0.298) | 0.0093 (0.0043–0.0171) | 1.1 / 2.4 | – |
| crustal, all classes | 783 (279) | 8.0 | 7.80 | 1.005 (0.051) | 5.49 | 0.542 (0.433–0.656) | 0.0508 (0.0333–0.0728) | 2.6 / 1.0 | – |
| crustal, forearc | 660 (178) | 7.2 | 7.00 | family | 3.50 | 0.337 (0.267–0.416) | 0.0147 (0.0095–0.0213) | 0.7 / 1.0 | – |
| crustal, arc | 85 (70) | 7.9 | 7.70 | family | 1.38 | 0.137 (0.101–0.175) | 0.0125 (0.0078–0.0187) | 0.6 / 0 | – |
| crustal, backarc | 27 (21) | 7.7 | 7.50 | family | 0.403 | 0.040 (0.025–0.056) | 0.0034 (0.0019–0.0054) | 0.2 / 0 | – |
| crustal, Patagonia | 11 (10) | 8.0 | 7.80 | family | 0.202 | 0.020 (0.010–0.031) | 0.0019 (0.0009–0.0033) | 0.1 / 0 | – |

"Events" have a weight above 0 inside the table; "counted" is their weighted sum. For the crustal classes the check is on 1976–2026 only (their table).

**Interface (a, b) branches** (tapered; a, b at the 5th percentile / maximum likelihood / 95th percentile of the rate at the controlling Mw):

| unit | controlling Mw | sd of log10 rate | 5th | ML | 95th |
|---|---|---|---|---|---|
| interface | 8.8 | 0.069 | 6.300, 0.990 | 6.156, 0.961 | 6.012, 0.931 |
| interface, 45.6–37° S | 8.8 | 0.193 | 5.360, 0.989 | 4.951, 0.906 | 4.543, 0.823 |
| interface, 37–32° S | 8.8 | 0.128 | 6.129, 1.051 | 5.858, 0.996 | 5.587, 0.941 |
| interface, 32–26° S | 8.4 | 0.106 | 5.774, 0.992 | 5.527, 0.941 | 5.279, 0.891 |
| interface, 26–17.6° S | 8.8 | 0.147 | 5.845, 1.029 | 5.538, 0.966 | 5.230, 0.903 |

**Checks of b** (tapered fits): Kijko and Smit (2012) on the same table and b-positive (van der Elst 2021; from 1976, Mw ≥ 5.0, differences ≥ 0.2) agree within the bootstrap error except for the interface segments 26–17.6° S (b-positive 0.84 against 0.97) and 45.6–37° S (1.03 against 0.91), each on under 100 pairs. Weight-1 events alone give the same b within 0.04 except 45.6–37° S (0.83), and N(≥ 5) × 0.77 (interface) to × 0.39 (forearc), the share of split events.

**Figures.** The fit figures (`figs/<date>/fmd_classes.png`, `fmd_interface_segments.png`) show the observed cumulative rates (each bin over its own observation time) against the fitted line and a predictive band (`gr.predictive`): for each bootstrap replicate of the fit, counts per bin are drawn over the bin's own observation time and summed from the top as the observed points are; the band is their 5–95 %. Counts are Poisson, or negative binomial with the dispersion of the observed clusters in the bin, so that a clustered full catalogue is not judged against a Poisson spread. A point outside the band disagrees with the fit; a point inside does not (Pablo, 18 Nov). The earlier figures with bars on the points mixed the sampling spread of the observations with the uncertainty of the fit.

**Interface, final rules on catalogue 17g** (trial of 18 Nov, `drafts/fits/trial/`, tapered line, cluster bootstrap; the final run on 17g replaces it; figure `figs/<date>/fmd_interface_segments.png`):

| unit | completeness | events (counted) | Mmax | corner | b (sd) | N(≥ 5) | N(≥ 6) (5–95 %) | N(≥ 7) (5–95 %) | N(≥ 8) (5–95 %) | Mw ≥ 7 fitted / observed | Mw ≥ 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| whole margin | 5.0 from 1981, 5.1 from 1964, 7.0 from 1905, 7.5 from 1830, 8.5 from 1550 | 1 902 (1 513) | 9.7 | 9.48 | 0.942 (0.024) | 24.9 | 2.84 (2.14–3.74) | 0.325 (0.242–0.427) | 0.0369 (0.0265–0.0497) | 51.2 / 50.3 | 10.7 / 13.1 |
| 26–17.6° S | 5.0 from 1964; historical as above | 423 (347) | 9.1 | 8.87 | 0.916 (0.047) | 5.41 | 0.656 (0.387–0.985) | 0.0794 (0.0408–0.123) | 0.00925 (0.00401–0.0156) | 12.5 / 15.6 | 2.5 / 2.9 |
| 32–26° S | 5.0 from 1976, 5.2 from 1964 | 565 (447) | 8.7 | 8.47 | 0.920 (0.033) | 7.45 | 0.896 (0.632–1.20) | 0.107 (0.0698–0.146) | 0.0110 (0.00655–0.0158) | 16.2 / 10.0 | 2.6 / 2.6 |
| 37–32° S | 5.0 from 1964 | 655 (517) | 9.2 | 8.98 | 0.958 (0.040) | 8.07 | 0.890 (0.490–1.41) | 0.0981 (0.0508–0.155) | 0.0105 (0.00487–0.0175) | 15.2 / 11.2 | 2.9 / 4.0 |
| 45.6–37° S | 5.0 from 1999, 5.2 from 1964 | 213 (167) | 9.7 | 9.48 | 0.947 (0.116) | 3.23 | 0.365 (0.139–0.625) | 0.0413 (0.0113–0.0882) | 0.00465 (0.0009–0.0135) | 6.5 / 10.3 | 1.3 / 2.2 |

Every interface unit passes the large-event check (negative binomial band of the clusters), 32–26° S included. Intervals are wider than in the table of section 4 (event bootstrap): the bootstrap draws whole clusters (DECISIONS, Statistics, 17 Nov).

## 5. The two known fit failures

Left as they are and named in the discussion (DECISIONS, Statistics). Both failed the large-event check with either shape, on every catalogue since 14 Nov and with every pad; the numbers in this section and section 4 are of the trial with the table of 15 Nov:

1. **Interface 32–26° S at Mw ≥ 7: 17.2 fitted, 9.9 observed** with the table of 15 Nov; with the table of 17 Nov (no step 8.0 from 1500) 15.6 / 9.2, inside the band. Even so the segment lacks Mw 7.0–7.4 events in every period, 1976–2026 included (1.0 observed, 3.3 fitted), which is not completeness (Mw ≥ 8: 4.9 / 2.6, inside the band). The fit expects more large events than the segment has. With the b shared by the four segments (0.958) the expected number falls to 15.8 and the check passes; from a floor of 5.4 up the own b is 0.97–1.01 and it also passes (`drafts/fits/team/interface_32_26_b.png`).
2. **Intermediate in-slab at Mw ≥ 7: 17.9 fitted, 28.5 observed** (by weight). The excess is all before 1964: from 1976 the line fits (Mw ≥ 7 6.1 fitted, 6.9 observed), while in 1905–1963 it expects 5.5 of Mw 7.0–7.4 and 1.7 of Mw ≥ 7.5 against 10.3 and 8.8 (numbers of the 15 Nov catalogue, `FITS_history.md` section 2; the total has moved by 1 event since). Most of those old events are converted Centennial magnitudes (19 of 32 Abe mB values, σ 0.25–0.30), probably too high. No fitting method removes it; the floor at 5.6 passes the check only by letting b fall to 1.07 (and the nest to 0.88). Also left open: the shortfall at Mw 5.0–6.4 in 1964–1975 (about 110 against 173 fitted).

## 6. Declustered fits

`run_declustered.py`: the fits of section 4 on each declustered catalogue of `decluster.py`, with the completeness table and the Mmax of the full catalogue, and the interface segments also with the shared b. Two algorithms are kept in every output until the team chooses one (DECISIONS, Statistics, 17 Nov): Gardner–Knopoff with the windows of van Stiphout et al. (2012), and nearest neighbour (Zaliapin and Ben-Zion 2013; b 1, d_f 1.6, epicentral distance, threshold from a two-Gaussian mixture of log10 η from 1964, the largest event of a cluster kept), both run inside each class family (`gk_family`, `nn_family`). `gk`, `nn` and `nn_depth` (all classes together) are comparison only; `nn` and `nn_depth` keep the first event of a cluster and drop great mainshocks. Rows for the logic tree: `method` gk_family / nn_family, `table` full. The tables read on the declustered catalogues moved the historical steps up to 80 years earlier (the rate rule is one-sided); not taken (17 Nov), and no longer computed by `run_declustered.py` (18 Nov). Figures: `figs/<date>/declustered_*.png`; numbers and the algorithm check in `DECLUSTER.md`.

Declustered against full (tapered, own b, table full; N as a ratio to the full-catalogue fit):

| unit | b full | b gk_family | b nn_family | N(≥ 5) gk / nn | N(≥ 6) gk / nn | N(≥ 7) gk / nn |
|---|---|---|---|---|---|---|
| interface | 0.961 | 0.762 | 0.897 | × 0.28 / × 0.48 | × 0.44 / × 0.55 | × 0.69 / × 0.64 |
| interface, 45.6–37° S | 0.906 | 0.846 | 0.900 | × 0.37 / × 0.46 | × 0.43 / × 0.47 | × 0.49 / × 0.47 |
| interface, 37–32° S | 0.996 | 0.658 | 0.888 | × 0.17 / × 0.39 | × 0.37 / × 0.50 | × 0.80 / × 0.64 |
| interface, 32–26° S | 0.941 | 0.763 | 0.886 | × 0.32 / × 0.57 | × 0.48 / × 0.65 | × 0.72 / × 0.73 |
| interface, 26–17.6° S | 0.966 | 0.834 | 0.941 | × 0.33 / × 0.51 | × 0.45 / × 0.54 | × 0.61 / × 0.57 |
| in-slab, shallow | 1.130 | 0.961 | 1.095 | × 0.61 / × 0.84 | × 0.90 / × 0.92 | × 1.33 / × 0.99 |
| in-slab, intermediate depth | 1.157 | 1.004 | 1.149 | × 0.63 / × 0.96 | × 0.89 / × 0.98 | × 1.27 / × 1.00 |
| Jujuy nest | 1.229 | 0.767 | 1.214 | × 0.26 / × 0.92 | × 0.74 / × 0.95 | × 1.76 / × 0.98 |
| crustal family | 1.005 | 0.922 | 1.001 | × 0.63 / × 0.73 | × 0.76 / × 0.73 | × 0.92 / × 0.74 |

- Gardner–Knopoff removes far more of the interface (72 % of N(≥ 5), and 83 % at 37–32° S, the Maule and Illapel sequences) and lowers b by 0.13–0.34, so its N(≥ 7) falls less than its N(≥ 5); in the in-slab classes it lowers b by 0.15–0.46 and raises N(≥ 7). Nearest neighbour lowers b by 0.01–0.11 and moves the rates of a unit nearly in parallel. Figure for the team: `drafts/fits/team/declustered_rates.png`; the events each algorithm removes in 1960, 2010, 2014 and 2015: `drafts/fits/team/gk_nn_sequences.png`.
- Shared interface b: 0.958 (full), 0.757 (gk_family), 0.898 (nn_family). With it, 32–26° S passes the large-event check in all three (full: 15.8 fitted, 9.8 observed).
- Large-event check: every declustered unit passes except intermediate in-slab with nearest neighbour (as the full catalogue).

**Algorithms consolidated (18 Nov, catalogue 17g, trial).** Four algorithms per class family, from published sources only (DECISIONS, Statistics): Gardner–Knopoff with three window sets of van Stiphout et al. (2012, eqs. 1–3; the same forms as `openquake.hmtk`): Gardner and Knopoff (1974) as fitted there (`gk_family`), Gruenthal (`gk_gruenthal_family`) and Uhrhammer (1986; shorter in time, wider in distance at large magnitude: 100 km and 322 days at Mw 7 against 70 km and 918 days) (`gk_uhrhammer_family`); and nearest neighbour (`nn_family`) with the b of the catalogue (1.037), as Zaliapin and Ben-Zion (2013) prescribe, and their d_f 1.6 (no estimate for Chile; measuring it would need a scale range of our own). Reasenberg (1985) was implemented from the summary of van Stiphout et al. (2012, section 5.2, Table 3) and dropped: two steps (how x_k raises the cut-off during a cluster, how two single events start one) could not be checked against the original paper. Kept at Mw ≥ 4.5: GK 42 %, Gruenthal 32 %, Uhrhammer 61 %, NN 77 %; Mw ≥ 7 kept of 162: 146, 146, 134, 145. All keep the great mainshocks (1906, 1922, 1950, 1960, 1995, 2010, 2014, 2015).

| interface b (tapered, tables of the fits) | full | Gardner–Knopoff | Gruenthal | Uhrhammer | nearest neighbour |
|---|---|---|---|---|---|
| whole margin | 0.94 | 0.74 | 0.70 | 0.81 | 0.88 |
| 26–17.6° S | 0.92 | 0.78 | 0.75 | 0.88 | 0.89 |
| 32–26° S | 0.92 | 0.73 | 0.68 | 0.82 | 0.86 |
| 37–32° S | 0.96 | 0.64 | 0.61 | 0.71 | 0.86 |
| 45.6–37° S | 0.95 | 0.85 | 0.78 | 0.82 | 0.94 |

- b-positive (van der Elst 2021), insensitive to clustering, gives about 0.88 for the margin: nearest neighbour agrees with it, the window methods lower b by up to 0.35, most where the great sequences are (37–32° S). The window fits pass through the great earthquakes only because b pivots down; that is not evidence for them. Figures `FIGURES/declustering/interface_margin_declustered.png`, `interface_segments_declustered.png`.
- On the declustered catalogues the step of Mw 5.0 (1976 or 1999) moves b by 0.01, against 0.05 on the full catalogue: the full-catalogue sensitivity comes from the aftershocks of 1976–1998.
- Still to do for the co-authors' choice: score the algorithms on b against b-positive, a Poisson test of the declustered catalogue, and the great mainshocks kept.

## 7. Mmax pad

`run_pad.py`: the fits with Mmax = largest observed + 0.0 and + 0.4 instead of + 0.2, the corner following by the Kagan rule; maximum-likelihood rows only, full catalogue (`tables/fits_<date>_pad00.csv`, `_pad04.csv`, `_pad_compare.csv`). A tornado factor. On 16f: b moves under 0.015 and N(≥ 6) under 2.5 % in every unit; N(≥ 7) moves only where Mmax is near 7 (forearc × 0.43 / × 1.52, Jujuy nest × 0.76 / × 1.12, backarc × 0.87 / × 1.07); in-slab N(≥ 8) × 0.50 / × 1.39. On 17f (trial) the same within 0.001 in b and 1 % in N: pad 0.0 / 0.4 give forearc N(≥ 7) × 0.43 / × 1.52, nest × 0.76 / × 1.12, in-slab N(≥ 8) × 0.50 / × 1.39; the large-event check gives the same result in all three pads.

## 8. Magnitude σ

`sigma.py` (a report; 16 Nov, still valid for 17f). Direct Mw from 1964: σ 0.08 (GCMT) to 0.10 (W-phase, regional Mw), count 0.98. Converted (proxy) magnitudes: σ 0.18–0.27, count 0.87–0.89. ISC-GEM 1904–1975: σ 0.23–0.29 (its own Mw uncertainty; 0.2 where empty), count 0.77–0.79; the 23 Supplement quality-D values reach σ 1.0–1.1 and count 2.9 together inside the table, negligible. Centennial: 0.25, 0.30 for a converted mB. Before 1904 (Cabello et al. 2025): 0.5, count 0.55 at b 0.96. The weight removes 20–30 % of the large events, nearly all before 1904; the default σ 0.5 of the historical values is the single number that matters most there (it makes the step "Mw 8.0 from 1500" count about 7 interface events instead of 11).

## 9. Methods compared, and recovery on synthetic catalogues

`compare.py`; `tables/fits_sensitivity_<date>.csv`, `figs/<date>/methods.png`, `synthetic_methods.png`, `b_floor.png`.

- **On synthetic catalogues** built like this one (400 per case; the table, class weights, the kind and σ of a real event of each period and size): Weichert on the table has bias +0.003 in b and +1.7 % in N(≥ 5), and its 5–95 % intervals hold the truth in 87–89 % of catalogues for b and N(≥ 7). Without the magnitude-error weight b is 0.026 low and N(≥ 7) 26–29 % high. Aki–Utsu and a joint Mc–b fit on 1976–2026 scatter 1.3–1.4 times more; least squares on cumulative rates 2.3–2.5 times more, and biased for small classes.
- **On the catalogue:** the open line and the tapered line with a corner at 9.6 give the same b; the open line raises N(≥ 7) where Mmax is near 7 (forearc × 2.4, nest × 1.4). Aki–Utsu from 1976 gives the interface b 0.92 and N(≥ 7) × 1.3 (the rate of 1976–2026 with its sequences). The joint Ogata–Katsura fit fails (b 1.3–1.7 from Mw 3.5): below Mw 5 the catalogue is a mixture of regions and agencies, not one line times one detection curve. Pooled b (random effects, DerSimonian and Laird 1986): the between-unit variance is zero in each family, so every unit takes the family b; for the segments it moves N(≥ 7) by × 0.79 to × 1.19.
- **b against the floor:** interface and segments within ± 0.05 from 5.0 to 6.0; intermediate in-slab and the Jujuy nest fall steadily (1.16 → 0.97, 1.24 → 0.75), pulled by the old large events.
- **The automatic table on synthetic margins** (40 per case): the historical steps come out 30–75 years early and the fit on them gives N(≥ 7) 6–14 % and N(≥ 8) 9–20 % low; the instrumental "5.0 from 1976" is found in 0–18 % of catalogues (later in the rest). The rule is cautious, not validated: the paper states that it does not recover a known table. With the instrumental steps given, the historical ones come out at or before the true year (`tests/test_table.py`).
- A completeness table read on crustal events alone was tested and not taken (Mc 5.3 in 1976–1989; crustal family b 1.06).

## 10. Assumptions and limits

- AIC values use weighted counts (a pseudo-likelihood); differences below about 2 mean nothing. Mmax is taken from the data and not charged.
- The magnitude-error weight in the bootstrap uses the β of the maximum-likelihood fit, not iterated per replicate.
- Synthetic catalogues have one b, Poisson times and normal magnitude errors; no sequences.
- The arc stays one unit; nothing above Mw 6.5 since 1976, so its line to Mmax 7.9 is extrapolated with the family slope. Its Liquiñe–Ofqui fault rate at Mw ≥ 6 (0.45 per year) is far above the background fit; that mismatch is in the fault moment (CR), not in b.
- Patagonia: the 1949 Magallanes doublet (Mw 7.8) belongs to the Magallanes–Fagnano fault source; 1907-01-19 Magallanes (M 5.5; Cabello et al. 2025, CERESIS-GEM Mw 5.47 ± 0.6; Lomnitz 1970) is drawn in the class figure as a reference event, not in the catalogue.

**Tried and not taken (17–18 Nov), with the reason:**
- Completeness table read on the declustered catalogues: both large-event failures pass, N(≥ 7) × 0.79–0.92, but its historical steps are earlier still than the rule's, which is already early on synthetic catalogues.
- Instrumental steps as the envelope of the four segments: Mw 5.0 from 1999, set by the south (Mc 5.2–5.4 until 1998, 5 % of the events); it threw away about 550 complete events of the other segments and moved the margin b by +0.044. Replaced by the margin series plus per-segment steps. The margin series first gave 1991, from two windows of 1988–1990 whose point estimate failed (counted by the bootstrap alone); fix 1 counts a window only if its point Mc exceeds the magnitude too.
- A step Mw 8.0 from 1500: fits the great events best, but Mw ≥ 8 before 1830 is short of the fit in every segment but 37–32° S, and no published method supports it. Steps read off one event (8.3 from 1575, 8.5 from 1604) bias the rate up. 8.5 from 1600 and 1745 change the fit by under 3 %.
- Dropping the step 5.2 from 1964: passes the intermediate in-slab check, but 1964–1975 is not incomplete (its rate equals the 1990s; flat after declustering), the sequence years set the fitted level.
- A fit floor of 5.8: the interface b barely moves (0.95 → 0.91, sd doubles); the in-slab classes bend (intermediate b 1.15 → 0.95, N(≥ 8) × 2.1). Floor stays 5.0.
- A predictive band in the fit figures (fit and counting, cluster dispersion): standard statistics, but not PSHA practice; the figures show the fit's 95 % confidence and Poisson 1σ on the incremental points.
- Reasenberg declustering (above).

## 11. Files and how to run

From `psha_chile8/fits/` in conda `psha_renta`; settings at the top of each script (`DATE`, the next free date; the catalogue comes from `CURRENT.md`).

| script | writes | time |
|---|---|---|
| `OMP_NUM_THREADS=1 python decluster.py` | `catalog/declustered/<method>_<DATE>.csv`, `<method>_m35_<DATE>.csv` | 4 min |
| `python run.py` | `tables/fits_<DATE>.csv`, `fits_sensitivity_`, `table_`, `table_checks_`, `mc_table_`, `mc_series_`; `FIGURES/completeness/mc_time`, `historical`, `FIGURES/fits/fmd_classes`, `fmd_interface_segments`; `figs/<DATE>/fmd_classes.png`, `fmd_interface_segments.png`, `large_event_check.png`, `b_floor.png`, `methods.png`, `synthetic_methods.png` | 2 min |
| `OMP_NUM_THREADS=1 python run_declustered.py` | `tables/fits_declustered_<DATE>.csv`, `declustered_removed_`, `_compare_`, `_floor_`; `figs/<DATE>/declustered_*.png`, `FIGURES/declustering/interface_*_declustered` | 10 min |
| `OMP_NUM_THREADS=1 python mc_maps.py` | `tables/mc_nodes_<DATE>.csv`, `mc_regions_<DATE>.csv`; `FIGURES/completeness/mc_maps` | 8 min |
| `python run_pad.py` | `tables/fits_<DATE>_pad00.csv`, `_pad04.csv`, `_pad_compare.csv` | 15 s |

Library: `gr.py` (loading, estimators, `kagan_corner`, `rates`), `table.py`, `compare.py`, `synth.py`, `sigma.py`, `figs.py`, `figs_declustered.py`. Tests: `pytest fits/tests` from `psha_chile8/`.
