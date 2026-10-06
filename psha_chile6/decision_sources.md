# psha_chile6: decisions on the catalog-based source models

Status 2026-09-30. Scope: interface, in-slab and crustal background models built
from the catalog. The crustal fault model uses the empirical models defined
separately and is not covered here. Each decision: what, why, and how it is
settled (fixed, derived from a fit, from hazard sensitivity, or a logic-tree
branch). Read with CONTEXT_sources.md, findings_rock800.md, DECISIONS_catalog.md.

## Inputs
1. Catalog: results/cat_handler_2/catalog.csv as given; families from
   cat_handler_2/params.py FAMILIES. Classification questions go back to
   cat_handler_2, not to the source models.
2. Magnitudes (D1): Cabello et al. (2025) homogenized Mw as given. Limitation:
   their conversions hold within about Mw 4.5-6.5; outside that range, and for
   Md, Mc and m, original values are taken as Mw.

## Rates and spatial pattern
3. Rates, b and Mmax from the full catalog, no declustering, for all families
   (Marzocchi and Taroni 2014; config DC_METHOD "none"). Variant rate_gk74
   keeps the campaign's declustered rates for comparison.
4. Spatial pattern (in-slab, crustal) from the gk74-declustered catalog
   (PATTERN_DC), scaled to the full-catalog rate.
5. Pattern weights: completeness window of each event, 10^(b (Mc - floor)) / T
   of the window (Hiemer et al. 2014, eq. 4; SMOOTH_EVENTS "window_T").
   Evidence: the retrospective spatial test (pattern_test.py) scored equal
   weights ("all") 3-10 % (intra_slab) and 10-20 % (slab_deep) higher on
   independent targets; "window_T" kept as the published, completeness-based
   choice; "all" and the old magnitude-step weights kept as variants. The old
   weights let single events draw up to 70 % of a city's rate (Concepcion).
6. Kernel: power law, 25 neighbours, cut-off 500 km (calibrated kernel moved
   PGA by 4 % at most).
7. Pattern declustering: gk74, fixed. Known limit: aftershocks of great
   earthquakes (Maule, Illapel, Iquique) outlast its point-source windows; they
   now affect the map only.

## Completeness and fits
8. Completeness Mc(t) (D3): derived. Lilliefors test with b free, windows cut at
   network changes (1964, 1976, 1982, ~2007, 2012), masking of short-term
   aftershock incompleteness after M >= 7.5, regional historical steps for the
   interface.
9. a and b: Weichert, no magnitude-uncertainty correction, fixed.
10. Correlated (a, b) branches: only where the rate spread at the controlling
    magnitude matters (derived per family from the bootstrap fits).

## Interface
11. Rate: seismic (catalog) and geodetic (moment rate) are logic-tree branches;
    the seismic branch uses no geodetic information.
12. MFD: tapered Gutenberg-Richter in both branches, corner Mw ~9.6 from global
    subduction seismicity (Bird and Kagan 2004; exact value to confirm), segment
    Mmax as a hard upper cut. The geodetic branch keeps b and corner and scales
    the rate to the moment rate.
13. Geometry: full margin and segmented as logic-tree branches, equal weights.
14. Z_BOTTOM 50 km, fixed. Z_TOP 5 or 10 km: derived from the trench depth and
    the shallowest interface events with real depths.
15. Patagonia interface (south of 46.15 S): same construction as the Nazca
    interface, 50 km locked depth, rate from the geodetic moment rate only,
    coupling 0.5; the catalog events in its footprint are not used for rates;
    the rest are patagonia_crustal. It keeps its geodetic rate in both Nazca
    rate branches.

## In-slab
16. intra_slab vs slab_deep b: derived from a b-equality test (Weichert
    likelihood ratio, b-positive as check) after the new completeness tables.
17. Smoothing domain (whole slab summed vs each class on its own slab-top
    domain): from the pattern test and the hazard.
18. Mmax: instrumental maximum per class + 0.2 (currently 7.9 intra_slab,
    8.2 slab_deep, 7.4 deep_nest); if intra_slab and slab_deep are merged, the
    merged instrumental maximum + 0.2. deep_nest (Jujuy) always its own class.
19. Depths: one hypocentre and one lower seismogenic depth per cell, as
    fractions of the Slab2 thickness below the top (0.30, 0.65); the method is
    fixed, the fractions are recomputed from real depths only (relocated_*,
    free, filled).

## Crustal background
20. forearc, intraarc, backarc and Patagonia are separate sources, each with its
    own b; a class with sigma_b > 0.2 borrows b (Patagonia from intraarc,
    unclassified from forearc).

## Ground motion and hazard settings
21. GMMs: equal weights for now; the choice of GMMs for Chile is pending.
22. Vs30 800 m/s, Z1.0 40 m, Z2.5 0.6 km, truncation 3, mesh 10 km. While
    building: 475 yr, point-source distance 40 km. Final run: 475 and 2475 yr,
    point-source distance 100 km, integration distance 500 km.

## Checks without a decision
23. Concepcion in-slab rate against the catalog under decisions 3-5.
24. Interface model against the catalog within 150 km of each city (D5).