# FITS state, 18 Nov: for the next FITS session

B15 part 2 (the final run on 17g) is not run. Everything below was checked on catalogue 2026-11-17g through `drafts/fits/trial.py` (date "trial", outputs in `drafts/fits/trial/`, marked "trial, not used"). Decisions: DECISIONS, Statistics and Figures, lines tagged "(Pablo, 17 Nov, FITS)" and "(Pablo, 18 Nov, FITS)". Method and reasons: `fits/FITS.md` (sections 2, 4, 6, 10). Log: WORKLOG entries of 17–18 Nov "FITS".

## Done
- **Catalogue:** `gr.CAT = gr.current()` reads the row "frozen catalogue (final)" of `CURRENT.md`: `catalog/frozen/2026-11-17g/catalog_2026-11-17g.csv`.
- **`nn_family` check** against Zaliapin and Ben-Zion (2013): two fixes (seconds in the event times; no parent at t_ij ≤ 0). `fits/DECLUSTER.md` section 12.
- **Bootstrap:** whole `nn_family` clusters (`gr.fit(cl=)`, `run.clusters()`); large-event check with a negative binomial band (`gr.dispersion`, `gr.band`). Intervals of the interface units 1.3–2.9 times wider than with the event bootstrap; the (a, b) branches of IF will widen with them.
- **Completeness (instrumental), measured:** `table.auto` gives Mc(t) of the margin and of each segment (`table.SEG`: north 15–26° S, central-north 26–32° S, central 32–37° S, south 37–46° S; windows of 250 events, step 50, bootstrap 30), steps by the last-window rule with fix 1. On 17g, from Mw 5.0: margin and every class 5.0 from 1981, 5.1 from 1964; 26–17.6° S 5.0 from 1964; 32–26° S 5.0 from 1976, 5.2 from 1964; 37–32° S 5.0 from 1964; 45.6–37° S 5.0 from 1999, 5.2 from 1964. Written in `run.TABLE` and `run.SEG_INST` (`run.SEG_MC` maps units to series); `run.py` stops if the measurement differs.
- **Completeness (historical):** 7.0 from 1905, 7.5 from 1830, 8.5 from 1550, margin-wide. Checks by Hakimhashemi and Grünthal (2012) and Albarello et al. (2001) in `table.checks`, written by every run. Refs in `refs/catalogs/` (`albarello_2001.pdf`, `hakimhashemi_gruntal_2012.pdf`).
- **Fit floor:** Mw 5.0 for every unit; the crustal classes keep only the steps from 1976 on (`since=1976`; their table becomes 5.0 from 1981, 5.1 from 1976).
- **Declustering algorithms** (`fits/decluster.py`, ref `refs/catalogs/vanstiphout_2012_corssa.pdf`): `gk_family`, `gk_gruenthal_family`, `gk_uhrhammer_family`, `nn_family` (b of the catalogue 1.037, d_f 1.6); comparison only `gk`, `nn`, `nn_depth`. Reasenberg removed.
- **Interface fits on 17g (trial):** margin b 0.942 ± 0.024, N(≥ 8) 0.0369; 26–17.6° S 0.916, 32–26° S 0.920, 37–32° S 0.958, 45.6–37° S 0.947 ± 0.116; every check passes (`fits/FITS.md` section 4).
- **Figures** (style in DECISIONS, Figures; paper and support figures in `fits/FIGURES/<kind>/`, rows in FIGURES.md): `completeness/mc_time`, `historical`, `mc_maps`; `fits/fmd_interface_segments`, `fmd_classes`; `declustering/interface_margin_declustered`, `interface_segments_declustered`. Copied from the trial of 18 Nov (03:22); the final run rewrites them. `mc_maps` still needs a tidy layout (crowded longitude labels; the domain reaches 56° S where no node is measured). `run_declustered.py` no longer reads completeness tables on the declustered catalogues (fits them on the tables of the full catalogue). Test and exploration figures stay in `drafts/fits/` (not committed).

## Left, in order
1. **In-slab and crustal fits** on the new tables and the new style. Start from `fits/FIGURES/fits/fmd_classes.png` (drawn by the trial, not reviewed with Pablo). Open there: intermediate in-slab fails the large-event check (old magnitudes before 1964); the in-slab b bends below Mw 5.8 (CAT, 18 Nov: not magnitudes; FITS: not weights); Jujuy nest b 1.16 on 17g (1.23 on 17f); crustal own b against family b (forearc 0.92 and arc 1.05 could hold their own; backarc, Patagonia cannot); the crustal table now starts at 1981 for Mw 5.0.
2. **Declustered fits** of all units with the four algorithms (`run_declustered.py`), and the scoring for the co-authors (b against b-positive, Poisson test, great mainshocks kept).
3. **Pad tables** (`run_pad.py`).
4. **The final run (B15 part 2) and the CURRENT and DATA lines:** fits, declustered fits, table, pad, declustered catalogues, "catalogue the fits and models are built on" → 17g; DATA rows; WORKLOG with b, N(≥ 6), N(≥ 7), Mmax, corner per unit against 16f; note for IF, IS and CR.
5. **B16** focal mechanisms and class shares per cell on the final catalogue (`model/mechanisms/npd.py`).
6. **C16** in-slab depth cells on the final catalogue with the C15 class-weight method (`model/inslab/depth.py`, `run.py`, `options.py`).

## Commands (from `psha_chile8/fits/`, conda `psha_renta`)
```
python -c "import gr; print(gr.CAT)"
OMP_NUM_THREADS=1 python decluster.py
OMP_NUM_THREADS=1 python run.py
OMP_NUM_THREADS=1 python run_declustered.py
python run_pad.py
OMP_NUM_THREADS=1 python mc_maps.py
cd .. && python drafts/fits/compare_16f.py fits/tables 2026-11-17 && pytest fits/tests
```
Order matters: `run.py` reads the `nn_family` clusters of `decluster.py` (`run.CLUSTER`, file `catalog/declustered/nn_family_<decluster.DATE>.csv`). Trial of any step: `OMP_NUM_THREADS=1 python ../drafts/fits/trial.py decluster|run|declustered|pad`.

## Dates and paths the scripts read
- `CURRENT.md`, row "frozen catalogue (final)" (`gr.current`).
- `decluster.DATE = "2026-11-17"` → `catalog/declustered/<method>_2026-11-17.csv`; `run_declustered.DC_DATE = decluster.DATE`.
- `run.DATE = "2026-11-17"`, `run_declustered.DATE = "2026-11-17"`, `run_pad.DATE = run.DATE` → `fits/tables/*_2026-11-17*.csv`, `fits/figs/2026-11-17/`. No 2026-11-17 file exists yet in `fits/tables/` or `catalog/declustered/`; set the next free date if the run is on another day.
- `run.PAPER = fits/FIGURES/`; `figs.EDGES = model/interface/geometry/edges_2026-11-16c.json` (IF's segment outlines, for the map).
- `run.TABLE`, `run.SEG_INST` (the measured tables above); `run.CLUSTER = "nn_family"`.
- `sigma.py` reads `catalog/sources/iscgem_2026-11-10_mags.csv`.

## For IF, IS and CR (after the final run)
- **IF:** interface fits change through the measured tables and the cluster bootstrap: (a, b) branches wider; segment b 0.916–0.958; the south segment's Mw 5.0 from 1999. The fitted recurrence of Mw ≥ 9 on 45.6–37° S (about 1 150 years) is far longer than the paleoseismic interval of 1960-type events (about 300 years, Cisternas et al. 2005, to check): a case for the geodetic branch. Arica 1868 stays outside every segment.
- **IS:** in-slab refit pending (item 1); the nest b moved with CAT's deep-event conversion.
- **CR:** crustal refit pending (item 1); the crustal table now 5.0 from 1981; family b about 1.00 on 17g.

## Not placed
- Nothing else.
