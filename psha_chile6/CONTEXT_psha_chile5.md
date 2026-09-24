# psha_chile5: state of the analysis, 2026-09-23

## Reference model

- interface: full-margin, seismic rate, truncated GR, from M5.5 (`mmin55`, branch `full__seis__tgr`)
- in-slab: three classes fitted separately (fit floors slab_deep 5.8, intra_slab 5.6), smoothed
  over the whole slab and summed; source depths from the in-slab catalog: hypocentre at
  0.30 and lower seismogenic depth at 0.65 of the Slab2 thickness below the Slab2 top
- crustal: capped background plus the 12 fault branches
- GMMs: AG20 / Parker / Montalva (in-slab), AG20 / Parker / Kuehn (interface),
  ASK14 / BSSA14 / CB14 / CY14 (crustal), equal weights
- site: Vs30 800, Z1.0 40 m, Z2.5 0.6 km; truncation 3.0; PGA at 475 and 2475 yr, 10 cities

## Campaign

Family-only jobs with the full GMM tree of their region; families combine exactly in rate
space (hazard/tornado.py). Axes in hazard/logic_tree.py AXES: interface geometry, rate, MFD,
declustering, b floor, MMIN_HAZ, segmentation, full tree, GMM; in-slab class cut,
declustering, b floors, Mmax pad, depth rule, previous geometry, smoothing, GMM; crustal
faults, margin, cap, declustering, Mmax, GMM; truncation 2.0 / 2.5 / 4.0.

## Findings of the Vs30 380 series (psha_chile4), to be re-read at Vs30 800

- in-slab rates match the catalog within Poisson error at M >= 6 near the cities; the
  depth change (top + 7.5 km -> catalog depths) lowered PGA 4-6 % at 475 yr
- slab_deep dominance at Santiago and Iquique holds under every source parameter, class
  labelling and GMM; the in-slab source wins by rate, not by proximity to the median
  (mean epsilon 1.8-1.9 for both source types at 475 yr)
- GMM axes are the largest (slab GMM up to +/-12 %, interface GMM up to +/-11 %), then
  interface segmentation (-3 to -12 %), interface b (up to 12 %); all in-slab source
  parameters under 5 %; crustal faults 51 % at Puerto Aysen
- truncation: 2.5 lowers PGA 5-9 %, 4.0 raises it 3-6 %, 2.0 lowers 14-22 %
- Vs30 760 raised PGA 6-19 % at the subduction cities (nonlinear soil term at ~1 g)

## Open, deferred to the final-model phase

interface rate check against the catalog near the cities; Concepcion in-slab rate
(2-3 x catalog within 150 km); sigma and the Montalva weight (Chilean records);
Aysen / Pucon fault slip rates and Mmin; in-slab rupture scaling (Allen & Hayes);
comparison with published models on the same basis.
