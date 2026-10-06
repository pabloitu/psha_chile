# Step 0 tests: numerical, input, output

Run from psha_chile6: `pytest -q` (all), `pytest -m "not built"` (before anything is built),
`pytest -m built` (after run.py and fit_check.py).

| file | what it checks |
|---|---|
| test_gr.py | completeness lookups, Weichert b and rate (unbiased, bootstrap b_err calibrated, any floor), observed rates, tapered and truncated MFD, moment of binned MFDs |
| test_convention.py | bin precision: catalog magnitudes are the nearest 0.1, a recorded value is a bin centre; fit -> MFD -> NRML -> read back equals the true GR; the edge convention (`gr.HALF = 0`) must fail |
| test_dc.py | declustering windows against the published formulas, the window algorithm on a known cluster, the great-event limit |
| test_smooth.py | kernel, mass conservation of the smoothed field, per-cell magnitude bins |
| test_nrml.py | valid XML, rates read back, branch weights, chained logic tree (one branch set per family) in OpenQuake's parser |
| test_combine.py | mean and exact quantiles of the family combination against full enumeration |
| test_check_tree.py | hazard/check_tree.py passes a correct joint tree, flags a mislabelled one as pairing only, fails a wrong one; level 2 |
| test_run_cache.py | step hashes follow config, code and input files |
| test_catalog.py | format and conventions of catalog.csv, the rounding rule, Mmax coverage, family limits, Slab2 and trench inputs |
| test_patagonia.py | Antarctic interface: trench line, plane, area, moment of the written source, s05 integration |
| test_faults.py | fault MFD shapes (AL-I, AL-II, AL-III, YC, tapered) release the slip-rate moment at the bin centres; Mmax modes (observed, WC1994, Leonard 2014); the 45-branch tree; tornado variants and axes are consistent |
| test_hazard_config.py | city sets, output trees, per-region distances, the tornado job list |
| test_built.py | built NRML against the branch table, point sources against the grid, class rates, pooled b, built models against fit_check, config tables against fit_check tables, stale folders |
| test_fits_current.py | outputs/fits against a refit of the current catalog |

synth.py builds synthetic catalogs with a known truth without using lib.gr; builtchecks.py holds the
check functions of test_built.py.
