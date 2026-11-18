# GM1: rows for the shared files (to paste)

Pasted into DATA.md, FIGURES.md and REFERENCES.md on 15 Nov (GM1 session). The dated flatfile copies below are still to be made.

Writing outside `gmm/` other than WORKLOG and PLAN was not allowed in the GM1 session; these are the rows the brief asks for.

## DATA.md (new section at the end)

```
## Ground-motion data (GM1)

| date | file | what | version | notes |
|---|---|---|---|---|
| 2026-11-15 (GM1) | `data/ground_motion/Flatfile_chileanEvents_v11.csv` (repo root; dated copy `psha_chile8/data/ground_motion/Flatfile_chileanEvents_v11_2026-11-15.csv`) | Bastías et al. (2026) event flatfile, 6 679 events, 28 columns | DesignSafe doi:10.17603/ds2-6gyp-t353, v11; sha256 d1201b33180d24dc725001581a2b161351542654030479ff27d9cd42db6105db, 1 411 274 bytes | read by `gmm/records.py` |
| 2026-11-15 (GM1) | `data/ground_motion/Flatfile_chileanSiteStation_v7(1).csv` (dated copy `…/Flatfile_chileanSiteStation_v7_2026-11-15.csv`) | Bastías et al. (2026) station flatfile, 524 stations, 27 columns | v7; sha256 cbbb15b2345978299618a48e8c1555ffb3fe67a16610e6ce3be9a1909e3dbcee, 119 877 bytes | as above |
| 2026-11-15 (GM1) | `data/ground_motion/Flatfile_chileanRecord_v10.csv` (dated copy `…/Flatfile_chileanRecord_v10_2026-11-15.csv`) | Bastías et al. (2026) record flatfile, 43 050 records, 50 columns | v10; sha256 07ee77232f148f85b4a2c9e736477eb65d4b59dc6710c903627f6fa8ffff90a7, 181 182 474 bytes | as above; not for git (181 MB) |
| 2026-11-15 (GM1) | `gmm/tables/records_2026-11-15.csv` | record table for the subduction GMM residuals: one row per record, catalogue Mw, depth and class, flatfile distances, RotD50 PGA, SA(0.2), SA(1.0) (g), site and rupture parameters | `gmm/records.py` on the three flatfiles and the frozen catalogue `2026-11-14c` | 813 events, 9 421 records (interface 431 / 4 326, in-slab 382 / 5 095); counts per step in `gmm/tables/selection_counts_2026-11-15.csv`; used (GM1) |
```

## FIGURES.md (two rows at the end of the table)

```
| S | strong-motion data for the GMM test: Mw against Rrup per class (measured and inferred Vs30), depths, station Vs30 | the Bastías et al. (2026) records cover Mw 5–8.8 on the interface but only two in-slab events above Mw 7, and no backarc station | draft (supplement candidate) | `gmm/gm1_run.py` (`gm1_figs.py`) | `gmm/figures/data.png` |
| | LLH and EDR of 14 subduction GMMs per class and period, event bootstrap, current tree marked | the South America versions of the NGA-Sub models score better than the global ones; Montalva et al. (2017) scores best in-slab at short periods; no model is best everywhere | draft (paper or supplement candidate) | `gmm/gm1_run.py` (`gm1_figs.py`) | `gmm/figures/scores.png` |
```

## REFERENCES.md (new section H)

```
## H. Ground-motion models (GM1, added 15 Nov 2026)

GMM citations from the OpenQuake 3.27 docstrings (completed from memory where the docstring is short, marked). Only Bastías et al. (2026) is in `psha_chile/refs/gmm/`.

| ref | for | file | pdf |
|---|---|---|---|
| Bastías, N., Montalva, G.A., Leyton, F., Heresi, P., Domínguez, F. (2026). An extended and updated strong ground-motion database for the Chilean subduction earthquakes. Earthquake Spectra 42, e70032. doi:10.1002/esp4.70032. Data doi:10.17603/ds2-6gyp-t353 | strong-motion flatfiles of GM1 | Earthquake Spectra - 2026 - Bastías - ….pdf | [x] |
| Cotton, F., Scherbaum, F., Bommer, J.J., Bungum, H. (2006). Criteria for selecting and adjusting ground-motion models for specific target regions: application to Central Europe and rock sites. J. Seismol. 10, 137–156 | GMM screening criteria (as listed in MASCSN26 p. 88) | – | not in refs |
| Scherbaum, F., Delavaud, E., Riggelsen, C. (2009). Model selection in seismic hazard analysis: an information-theoretic perspective. BSSA 99(6), 3234–3247 | LLH score and weights | – | not in refs |
| Kale, Ö., Akkar, S. (2013). A new procedure for selecting and ranking ground-motion prediction equations (GMPEs): the Euclidean distance-based ranking (EDR) method. BSSA 103(2A), 1069–1084 | EDR score | – | not in refs |
| Abrahamson, N.A., Youngs, R.R. (1992). A stable algorithm for regression analyses using the random effects model. BSSA 82(1), 505–510 | between- and within-event split | – | not in refs |
| Abrahamson, N., Gulerce, Z. (2020). Regionalized ground-motion models for subduction earthquakes based on the NGA-SUB database. PEER Report 2020/25 | GMM, tree (SAM) | – | not in refs |
| Parker, G.A., Stewart, J.P., Boore, D.M., Atkinson, G.M., Hassani, B. (2020). NGA-Subduction global ground-motion models with regional adjustment factors. PEER Report 2020/03 (docstring gives only "Parker et al. (2020)"; report number from memory) | GMM, tree (SA, SA_S) | – | not in refs |
| Kuehn, N., Bozorgnia, Y., Campbell, K.W., Gregor, N. (2020). Partially non-ergodic ground-motion model for subduction regions using the NGA-Subduction database. PEER Report 2020/04 | GMM, tree (SAM) | – | not in refs |
| Montalva, G.A., Bastías, N., Rodriguez-Marek, A. (2017). Ground-motion prediction equation for the Chilean subduction zone. BSSA 107(2), 901–911 | GMM, tree; CSN 2026 | – | not in refs |
| Idini, B., Rojas, F., Ruiz, S., Pastén, C. (2017). Ground motion prediction equations for the Chilean subduction zone. Bull. Earthq. Eng. 15(5), 1853–1880 | GMM; CSN 2026; soil classes to check (REPORT_GM1, assumption 14) | – | not in refs |
| Youngs, R.R., Chiou, S.-J., Silva, W.J., Humphrey, J.R. (1997). Strong ground motion attenuation relationships for subduction zone earthquakes. SRL 68(1), 58–73 | GMM; CSN 2026 | – | not in refs |
| Zhao, J.X. et al. (2016). Ground-motion prediction equations for subduction interface earthquakes in Japan using site class and simple geometric attenuation functions. BSSA 106(4), 1518–1534 (and the companion in-slab paper of 2016) | GMM; CSN 2026 | – | not in refs |
| Abrahamson, N., Gregor, N., Addo, K. (2016). BC Hydro ground motion prediction equations for subduction earthquakes. Earthquake Spectra 32(1), 23–44 (docstring: 2015, in press) | GMM; GEM South America set | – | not in refs |
| Si, H., Midorikawa, S., Kishida, T. (2020). Development of NGA-Sub ground-motion model of 5%-damped pseudo-spectral acceleration based on database for subduction earthquakes in Japan. PEER Report 2020/06 | GMM | – | not in refs |
| Arteta, C.A. et al. (2021). Ground-motion model for subduction earthquakes in northern South America. Earthquake Spectra. doi:10.1177/87552930211027585 | GMM (Vs30 variants) | – | not in refs |
| Atkinson, G.M., Boore, D.M. (2003). Empirical ground-motion relations for subduction-zone earthquakes and their application to Cascadia and other regions. BSSA 93(4), 1703–1729; erratum BSSA 98(5), 2567–2569 (2008) | GMM | – | not in refs |
```

## Dated copies of the flatfiles (commands, from `psha_chile8/`)

```bash
mkdir -p data/ground_motion
cp ../data/ground_motion/Flatfile_chileanEvents_v11.csv data/ground_motion/Flatfile_chileanEvents_v11_2026-11-15.csv
cp "../data/ground_motion/Flatfile_chileanSiteStation_v7(1).csv" data/ground_motion/Flatfile_chileanSiteStation_v7_2026-11-15.csv
cp ../data/ground_motion/Flatfile_chileanRecord_v10.csv data/ground_motion/Flatfile_chileanRecord_v10_2026-11-15.csv
(cd data && sha256sum ground_motion/*_2026-11-15.csv >> SHA256SUMS)
echo 'data/ground_motion/' >> .gitignore
```

Then set `FF`, `F_EV`, `F_ST`, `F_REC` at the top of `gmm/records.py` to the dated copies.
