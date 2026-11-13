# Rules for location, depth and magnitude, with their support

13 Nov 2026. One table per topic: the rule as the code applies it now (`locate.py`, `magnitude.py`, run `2026-11-13b`, after the simplification of section 4), what in our data supports it, what in the literature supports it, and how hard it will be to defend.

Support column:
- **A** standard practice, citable.
- **B** follows from the documentation of the source catalogue.
- **C** our own measurement, with literature for the principle but not for the number.
- **D** our own choice; no literature found for it.

References marked † were found by web search on 13 Nov and only their abstract or citing text was seen, not the paper. The others are in `REFERENCES.md` or `MAGNITUDES.md` and were read.

## 1. The rules in three sentences each

**Location and depth.**
1. The epicentre comes from the local catalogue (Potin et al. to July 2020, CSN after) where its network surrounds the event, and from the best teleseismic or calibrated catalogue elsewhere.
2. The depth is the first depth in the same order that was actually measured. A depth that the agency fixed, set to a default, or set to a nominal value is not a measurement, and an event with none left has an unknown depth.
3. Offshore, where the land network sees the event from one side, depths from depth phases or calibrated relocations go before the local depth.

**Magnitude.**
1. A measured moment magnitude is always preferred, with Global CMT as the scale above Mw 5.4 and the regional and W-phase Mw below.
2. Without one, a single native magnitude is converted with a relation fitted on Chilean pairs.
3. The surface-wave scale is used before ML and mb, and only for shallow events.

## 2. Location and depth

| # | rule | our evidence | literature | support |
|---|---|---|---|---|
| L1 | **Order by period.** Before 1904 the historical catalogue (Cabello et al. 2025). 1904–1963: Centennial where it was relocated (1918–1942, 1956 on), then ISC-GEM, then ISC. From 1964: L2 and L3. | – | Centennial epicentres are relocated only in those years (Engdahl and Villaseñor 2002). ISC-GEM relocates every event (Bondár et al. 2015). Ruiz and Madariaga (2018) recommend the Centennial for large Chilean events. | B |
| L2 | **Inside the local network, the local catalogue gives the epicentre.** Inside = from 1982, 18–46° S, not east of the volcanic arc. | Against 775 GCCEL events left out of the rule: 8.8 km epicentre error with this rule. | A local network is accurate to about 5 km only when its stations surround the event (Bondár et al. 2004 †). Potin et al. (2024) relocate in 3-D models and state that events east of the Andes are poorly located in depth; Riedel-Hornig et al. (2026) say the same for events outside the network. | A for the principle, C for the limits |
| L3 | **Outside the network: GCCEL, ISC-EHB L1, L2, ISC, ComCat.** | "Potin first everywhere" gives 9.5 km against 8.8 km, and 28 km against 15 km in depth in the backarc. | Hierarchies of this kind are the usual practice: ISC-GEM, then EHB, then ISC (Weatherill et al. 2016); ISC-EHB for South America after 1964 (GEM SARA project †). GCCEL locations are calibrated to 1–5 km (Bergman et al. 2023 †). | A |
| L4 | **A local record more than 50 km from every teleseismic record of the same event is not used.** 85 events at Mw ≥ 4.5. | The 50 km is a round value above the 99th percentile of the matched pairs. | None for the number. ISC-EHB mislocation against ground truth is 11 ± 5 km (Weston et al. 2018), so 50 km is far outside the teleseismic error. | D |
| D1 | **Depth = first measured depth in the order of L1–L3. No filling from the slab model. None left = unknown.** | 13 % of the events at Mw ≥ 4.5 end without a depth. | Cabello et al. (2025) fill from Slab2 and warn about it; a slab-filled depth decides the tectonic class by construction. | D (a choice of principle) |
| D2 | **Not measured: depths flagged fixed, ISC-EHB L3, depths on a default value of the agency.** Defaults are found as spikes in each agency's depth histogram, plus the documented 10, 33, 35 km. | ISC fixed depths sit on a regional grid: 181 km 908 times. | ISC fixes unconstrained depths at 10, 15, 33 km or a regional default (Engdahl et al. 1998; Storchak et al. 2017; Bondár and Storchak 2011 †). L3 = fixed from nearby seismicity (Weston et al. 2018). | B |
| D3 | **Fixed ISC-EHB L1 depth counts as measured.** A fixed L2 depth does not. | Arica 1987: 69.7 km (L1) against 19 km (ISC). | L1 fixed = constrained by depth phases or USGS broadband depth; L2 fixed = the GCMT depth (Weston et al. 2018, p. 4; Engdahl et al. 2020 †). | B |
| D4 | **Before 1964 a depth counts only where its catalogue marks it as constrained:** ISC-GEM depth quality A or B, or a free-depth Centennial solution. σ = 20 km. | 83 events before 1964 keep a depth; of the ISC-GEM depths, 273 are graded A and 467 C. | ISC-GEM depth quality: A = depth phases or a station within 10 km, B = more than two stations within 150 km, C = other (Di Giacomo et al. 2018, Table 1). About a third of ISC-GEM events get a nominal depth from neighbours (Bondár et al. 2015). Centennial depth codes: Engdahl and Villaseñor (2002). Atacama 1922 at 70 km is considered wrong (Ruiz and Madariaga 2018). | B |
| D5 | **Offshore (more than 20 km from the coast): GCCEL and ISC-EHB L1 / L2 before the local depth.** | Potin is a median 11 km shallower than GCCEL there; ISC-EHB L1 1 km. | Offshore events seen only from land have poorly resolved depth (Husen et al. 1999 †). Depth needs a station within about 1.4 focal depths (Gomberg et al. 1990 †). Offshore, the CSN catalogue is consistently shallower than a dense-network catalogue (Münchmeyer et al. 2025 †, arXiv:2501.14396); offshore depth errors are high (Riedel-Hornig et al. 2026). Depth phases do not depend on station geometry (Engdahl et al. 1998). | A for the principle, C for 20 km |
| D6 | **Dropped on 13 Nov, not in the code.** Near the coast, a Potin depth under 20 km or over 80 km gives way to GCCEL, ISC-EHB, ISC or ComCat. 702 events. | Potin 11–21 km shallower than GCCEL for those depths; but 634 of the replacements are plain ISC or ComCat depths, which could be tested only on large aftershocks. | Same as D5 for the principle. Nothing supports ISC over a local catalogue; Weston et al. (2018) say ISC depths are overestimated for shallow events. | D |
| D7 | **Depth σ:** from our comparisons between catalogues, with floors of 5 km, 10 km offshore, 20 km before 1964; 3 km for GCCEL. | The tabled values (1.6–3 km) are spreads between catalogues that share data. | EHB depth uncertainty ± 10–15 km (Engdahl et al. 1998); ISC-EHB L1 relative uncertainty ≤ 15 km at 2σ (Weston et al. 2018); automatic Chilean catalogue 6 km mean (Riedel-Hornig et al. 2026). | C; the floors are round values |

## 3. Magnitude

| # | rule | our evidence | literature | support |
|---|---|---|---|---|
| M1 | **One Mw per event, by kind:** Ruiz and Madariaga (2018) for the events they name; a measured Mw; before 1976 ISC-GEM, then Centennial; before 1904 the historical value; else one converted magnitude. | – | Measured before proxy is the order of ISC-GEM (Di Giacomo et al. 2015) and of Lolli et al. (2023). One proxy by a priority list: Weatherill et al. (2016); Allen et al. (2018); Christophersen et al. (2024). | A |
| M2 | **Reference Mw: Global CMT from 5.4. Below: USGS W-phase, CSN, USGS regional, GFZ, each shifted by a constant of at most 0.08.** | Offsets measured on shared events. | GCMT is discarded below 5.4 when another Mw exists, because it reads high (Lolli et al. 2023; Lolli et al. 2020 †; Gasperini et al. 2012). Constant offsets between moment-tensor catalogues: Gasperini et al. (2012). CSN W-phase within ± 0.2 of USGS and GCMT (Riquelme et al. 2018). | A |
| M3 | **A GCMT value below 5.4 with no other Mw is lowered by 0.162 × (5.4 − GCMT).** About 1 000 events. | Fitted on 812 pairs; off the bin means by up to 0.04. | Lolli et al. (2023) leave such a value unchanged. The bias itself is documented; correcting it with a line is ours. | D |
| M4 | **A CSN regional Mw more than 0.3 from the median of two or more other Mw of the event is left out.** 26 values. | 16 of 97 GUC Mwr differ by ≥ 0.3 from the event's tensor, against 7 of 1 879 GCMT. | None. Ordinary outlier screening. | D |
| M5 | **Converted scales: only mb and Ms of ISC and NEIC, ML of CSN, ML of INPRES.** | The other agencies have too few pairs with a measured Mw. | ISC mb and Ms from ≥ 3 stations are the homogeneous ones; contributed agency magnitudes are heterogeneous (Storchak et al. 2017; Lolli et al. 2014, 2023). | A |
| M6 | **Relation: native magnitude regressed on Mw and inverted, slope corrected for the reference error; straight or bent form chosen by cross-validation; split at 50 km depth where cross-validation prefers it.** | Synthetic test: unbiased where a forward fit is off by 0.1–0.5. | Ordinary regression is biased (Castellaro et al. 2006; Lolli and Gasperini 2012). Fits on GCMT overestimate Mw at low M because the reference thins out (Lolli et al. 2014, 2023). Regressing the other way under truncation: Hausman and Wise (1977). Curved forms: Lolli et al. (2014); Gasperini et al. (2013). No paper proposes the inverse fit for this purpose. | C (the argument is citable, the method is new) |
| M7 | **Order of converted scales: surface-wave (events not deeper than 60 km), CSN ML, ISC mb, NEIC mb, INPRES ML.** Ordered by the scatter of each relation. | Withheld-Mw check (run of 12 Nov). | Ms before mb, shallow events only: Di Giacomo et al. (2015); Engdahl and Villaseñor (2002; h ≤ 60 km); Scordilis (2006); Lolli et al. (2023; < 50 km). | A |
| M8 | **Acceptance tests:** b-value against the fit floor, rate per period, large events predicted from small ones, held-out regional Mw, histogram. | Passed except mb + 0.10–0.16 at 5.0–5.5. | Magnitude shifts seen as rate changes: Habermann (1991); Zúñiga and Wiemer (1999); Tormann et al. (2010). | C |

## 4. What was hard to defend, and what was done (13 Nov, agreed by Pablo)

The rules above are of two kinds. L1–L3, D1–D3, D5, M1, M2, M5, M7 are the method, and each has a citation. The rest are patches added when a check found a problem. Each patch touches few events and has no citation for its number.

| patch | events (Mw ≥ 4.5) | proposal and outcome |
|---|---|---|
| D6 coastal Potin depths → ISC | 702 | **Dropped.** Not supported, and against the judgement that the local study is better. D5 is unchanged (GCCEL and ISC-EHB before Potin more than 20 km offshore). |
| D3, fixed L2 depth as last resort | 3 | **Dropped.** Three events do not justify a rule; they are unknown. |
| L4, 50 km | 85 | **Keep, as a quality check**, described in one sentence ("local records inconsistent with all teleseismic records of the event were not used"), not as a rule of the method. |
| D4, "multiple of 5 km" | 134 | **Replaced** by the catalogues' own flags (D4 above). 83 events before 1964 keep a depth (78 with the old rule); 35 depths changed in all. |
| D7, four σ floors | all | **Simplify** to one sentence: σ is at least 5 km, 10 km offshore and 20 km before 1964, citing Engdahl et al. (1998) and Weston et al. (2018) for the size. |
| M3, GCMT line | about 1 000 | **Kept for now; open for Pablo.** Dropping it means following Lolli et al. (2023) exactly (citable), at the cost of a step of about 0.05 at 5.4, which the tests of 12 Nov disliked. |
| M4, CSN cross-check | 26 | **Keep as a quality check**, one sentence. |
| M6, depth split of NEIC mb | about 600 moved by ± 0.05 | **Kept.** The split is not a hand choice: every relation takes the simplest form within one standard error of the best in cross-validation, and that rule picks the split. Removing it would need an exception for one scale. |

With these, the method section reads (text of the σ floors and of the two quality checks still to be shortened in the paper draft): source order by period and by network coverage (L1–L3); measured depths only (D1, D2, D4); depth-phase and calibrated depths first offshore (D5); measured Mw first on one scale (M1, M2); one converted magnitude from Chilean relations (M5–M7); and one sentence of quality checks (L4, M4).

## 5. References to add to `REFERENCES.md`

Found by web search on 13 Nov; details from publisher or agency pages, papers not read.

| ref | for |
|---|---|
| Gomberg, J.S., Shedlock, K.M., Roecker, S.W. (1990). The effect of S-wave arrival times on the accuracy of hypocenter estimation. BSSA 80(6A), 1605–1628. doi:10.1785/BSSA08006A1605 | depth needs a station within about 1.4 focal depths (D5) |
| Bondár, I., Myers, S.C., Engdahl, E.R., Bergman, E.A. (2004). Epicentre accuracy based on seismic network criteria. GJI 156, 483–496 | when a local network location is accurate (L2). The exact criteria differ between the summaries seen; read the paper |
| Bondár, I., Storchak, D. (2011). Improved location procedures at the International Seismological Centre. GJI 186, 1220–1244. doi:10.1111/j.1365-246X.2011.05107.x | ISC locator, default depths (D2). The default depth grid was not confirmed in the text seen |
| Bergman, E.A., Benz, H.M., Yeck, W.L., Karasözen, E., Engdahl, E.R., Ghods, A., Hayes, G.P., Earle, P.S. (2023). A global catalog of calibrated earthquake locations. SRL 94(1), 485–495. doi:10.1785/0220220217 | GCCEL (L3, D5) |
| Engdahl, E.R., Di Giacomo, D., Sakarya, B., Gkarlaouni, C.G., Harris, J., Storchak, D.A. (2020). ISC-EHB 1964–2016, an improved data set for studies of Earth structure and global seismicity. Earth and Space Science 7, e2019EA000897. doi:10.1029/2019EA000897 | ISC-EHB for 1964–2016 (D3) |
| Husen, S., Kissling, E., Flueh, E., Asch, G. (1999). Accurate hypocentre determination in the seismogenic zone of the subducting Nazca Plate in northern Chile using a combined on-/offshore network. GJI 138, 687–701 *(volume and pages to check)* | offshore depth not resolved from land (D5) |
| Münchmeyer, J. et al. (2025). Characterising the Atacama segment of the Chile subduction margin (24–31° S) with > 165 000 earthquakes. arXiv:2501.14396 *(journal to check)* | CSN depths shallower offshore than a dense-network catalogue (D5) |
| Husen, S., Hardebeck, J.L. (2010). Earthquake location accuracy. CORSSA. doi:10.5078/corssa-55815573 *(DOI to check)* | general reference on network geometry and depth |
| Lolli, B., Randazzo, D., Vannucci, G., Gasperini, P. (2020). The Homogenized Instrumental Seismic Catalog (HORUS) of Italy from 1960 to present. SRL 91(6) *(pages to check)* | GCMT discarded below 5.4 (M2) |

Web pages used: usgs.gov/publications (Gomberg et al.; Bergman et al.), isc.ac.uk/isc-ehb, sara.openquake.org/hazard_rt4, academic.oup.com/gji/article/206/3/1652, arxiv.org/abs/2501.14396, essd.copernicus.org (Riedel-Hornig et al. preprint), earth-prints.org/handle/2122/8635.
