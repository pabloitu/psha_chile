# FIGURES

Paper figures. Status: planned / draft / final.

| # | figure | message | status | script | file |
|---|---|---|---|---|---|
| 1 | catalog map by family | | planned | | |
| 2 | magnitude source and completeness through time | | planned | | |
| 3 | magnitude homogenization against Cabello et al. (2025) and Candia and Macedo (2026): b against the fit floor, declustered rates per period, predicted over observed M ≥ 7 | our Mw scale is steadier in time and size than the two published catalogues | draft (paper candidate; redrawn 2026-11-12 with the third A5 run) | `catalog/magnitude_check.py` | `catalog/figs/magnitude/test7_comparison.png` |
| S | synthetic comparison of the regression methods (supplement) | with an incomplete reference the inverse fit stays within 0.05, least squares and orthogonal do not | draft | `catalog/magnitude_check.py` | `catalog/figs/magnitude/test9_synthetic.png` |
| | interface band: thrust events against the Slab2 surface | thrust events sit on the Slab2 surface within its published depth uncertainty | draft (paper or supplement candidate) | `catalog/classify_check.py` | `catalog/figs/classify/band.png` |
| 1 | tectonic classes, maps per family | where each class is, and how many events are shared between classes | draft (candidate for figure 1) | `catalog/classify_check.py` | `catalog/figs/classify/maps.png` |
| | sections at six latitudes coloured by class | classes against the slab geometry | draft (paper candidate, one or two sections) | `catalog/classify_check.py` | `catalog/figs/classify/sections.png` |
| S | class totals under other rule settings | the band width is the largest choice of the classification | draft (supplement) | `catalog/classify_check.py` | `catalog/figs/classify/sensitivity.png` |
| S | Jujuy nest: map, depth histogram, density against distance | the nest is one cluster within 0.8° and 150–320 km depth | draft (supplement) | `catalog/classify_check.py` | `catalog/figs/classify/nest.png` |
| | catalogue rules: which source gives Mw, epicentre and depth, by period | the order of sources per property | draft (paper or supplement candidate; font to bring to Ubuntu) | `catalog/figs/rules/rules_fig.py` | `catalog/figs/rules/catalog_rules.png` |
| | fits per class on the single completeness table | one table and one rule give every class a Gutenberg–Richter line that agrees with its large events, except intermediate in-slab | draft (paper candidate) | `explore/B9/b9_12_refit.py` | `explore/B9/figs/refit_single_table.png` |
| 2 | completeness table on the magnitude–time plot | the automatic table against the events; a rate-only rule fails | draft (candidate for figure 2; one panel for all events would do) | `explore/B9/b9_11_autotable.py` | `explore/B9/figs/auto_table.png` |
| S | Mc of the whole catalogue on a 1° map, three periods | Mw 5.0 is complete everywhere mapped from 2000; Mw 4.5 is not, in any period | draft (supplement or paper) | `explore/B9/b9_10_mc_all.py` | `explore/B9/figs/mc_all_map_1deg.png` |
| S | magnitude-error weight: change per class, synthetic test, measured against converted Mw on the same events | converted magnitudes overcount by about 8 %; the weight removes it | draft (supplement) | `explore/B9/b9_9_magerr.py` | `explore/B9/figs/magerr_weight.png` |
| S | mixed-window tables against one window: fitted and observed large events | the network-history table under-predicts the interface events of Mw ≥ 7 | draft (supplement) | `explore/B9/b9_7_figs.py` | `explore/B9/figs/tables_one_window_or_mixed.png` |
| S | large events per era, intermediate in-slab | more events of Mw ≥ 7 before 1976 than since; for the discussion | draft (supplement) | `explore/B9/b9_7_figs.py` | `explore/B9/figs/large_events_per_era.png` |
| | frequency–magnitude distribution and fit per class, with the completeness table | every class follows one tapered Gutenberg–Richter line on one table; the line cut at Mmax next to it | draft (paper candidate; replaces the B9 refit figure) | `fits/run.py` (`figs.py`) | `fits/figs/fmd_classes.png` |
| | interface margin and four segments with the (a, b) branches | the segments share one slope within their errors; spread of the branches at the controlling magnitude | draft (paper or supplement candidate) | `fits/run.py` (`figs.py`) | `fits/figs/fmd_interface_segments.png` |
| | large-event check, Mw ≥ 7 and Mw ≥ 8, all units | the fits agree with the observed large events except intermediate in-slab (too many observed) and segment 32–26° S (too few) | draft (paper candidate) | `fits/run.py` (`figs.py`) | `fits/figs/large_event_check.png` |
| S | fitting methods compared: b, N(≥ 5), N(≥ 7) per unit | truncated and tapered forms change nothing below the top; the instrumental-only and least-squares estimates scatter around the reference | draft (supplement) | `fits/run.py` (`figs.py`) | `fits/figs/methods.png` |
| S | recovery of the methods on synthetic catalogues | Weichert with the magnitude-error weight is unbiased within 2 %; without the weight rates are 12–29 % high | draft (supplement) | `fits/compare.py`, `fits/run.py` (`figs.py`) | `fits/figs/synthetic_methods.png` |
| S | b against the fit floor, all units | b is stable from 5.0 to 6.0 for the interface; it falls with the floor for intermediate in-slab and the Jujuy nest | draft (supplement) | `fits/run.py` (`figs.py`) | `fits/figs/b_floor.png` |
