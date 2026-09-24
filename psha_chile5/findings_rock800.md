# Sensitivity campaign, site rock800: findings and interpretation

Interpretation of outputs/report/rock800 (psha_chile5, final run 2026-09-24).
PGA at 475 and 2475 yr, Vs30 800 (Z1.0 40 m, Z2.5 0.6 km), truncation 3.0,
integration distance 400 km, ten cities. Ranges are the largest change of PGA
(high minus low, in % of the reference) over the eight subduction cities
(Iquique to Puerto Montt) unless a southern city is named. The Vs30 380 series
(psha_chile4) is quoted where it differs. The catalog is the integrated,
relocated catalog as classified on 2026-09-24; a revised catalog will change
the numbers slightly but not the ranking.

## 1. Reference hazard

| city | PGA 475 yr | PGA 2475 yr | interface / in-slab / crustal at 475 yr (%) |
|---|---|---|---|
| Iquique | 1.20 g | 2.27 g | 36 / 62 / 2 |
| Antofagasta | 1.39 | 2.66 | 61 / 39 / 0 |
| Copiapo | 1.07 | 2.07 | 58 / 41 / 1 |
| Valparaiso | 1.51 | 2.82 | 51 / 49 / 0 |
| Santiago centro | 0.88 | 1.66 | 41 / 57 / 2 |
| Santiago Penalolen | 0.81 | 1.51 | 35 / 60 / 5 |
| Concepcion | 1.42 | 2.67 | 54 / 46 / 0 |
| Pucon | 0.54 | 0.97 | 34 / 32 / 34 |
| Puerto Montt | 0.63 | 1.31 | 80 / 17 / 3 |
| Puerto Aysen | 0.48 | 0.87 | 5 / 0 / 95 |

Rock is 7-12 % above soil at the coastal cities (the nonlinear site term
de-amplifies at ~1 g), equal at Santiago, lower at the crustal sites.

Within the in-slab family, slab_deep (slab top below 50 km) carries 32 % of
the total at Iquique and 38 % at Santiago; intra_slab (slab top above 50 km)
30 % at Iquique and 20-33 % at the other coastal cities.

The disaggregation gives the same two controlling earthquakes at every
subduction city: in-slab M7.2-7.3 at 55-90 km and interface M8.6-9.0 at 30-70
km. Mean epsilon is 1.6-1.7 at 475 yr and 2.0-2.1 at 2475 yr and equal for the
two source types: the in-slab family dominates by rate, not by proximity to the
median. Under every in-slab GMM the city PGA sits 0.8-1.5 sigma above the median
of the controlling scenario.

## 2. What each axis means

Each axis changes one choice of the reference and recomputes the family it
belongs to with the full GMM tree of that family; the other families stay at
their reference. Families combine exactly in rate space.

Ground motion
- GMM, single vs tree: each GMM of a family alone instead of the equally
  weighted tree. In-slab AG20 (Abrahamson & Gulerce 2020), Parker (Parker et al.
  2022, SA_S region) and Montalva (Montalva et al. 2017); interface AG20, Parker,
  Kuehn (Kuehn et al. 2020); crustal ASK14, BSSA14, CB14, CY14. Measures the
  spread between the models, i.e. the epistemic uncertainty the tree carries.
- truncation 2.0 / 2.5 / 4.0: the ground-motion distribution cut at that many
  sigma instead of 3.0. 2.0 is a bound, not an option.

Interface source
- geometry, segmented: four segments with their own Mmax and rates instead of
  one full-margin source; tests whether ruptures can span the margin.
- b: fit floor 5.4 / 6.0: the Gutenberg-Richter b and rate refitted above M5.4
  or M6.0 instead of M5.6; a proxy for the b-value uncertainty.
- Z_BOTTOM 40 / 60 km: down-dip limit of the seismogenic interface instead of
  50 km; changes the rupture area, the moment balance and the distance to
  the cities.
- Z_TOP 10 km: up-dip limit instead of 5 km.
- completeness table, ends of the ensemble: the rate and b refitted with the
  two completeness tables that give the lowest and highest N(>=M8) among 15
  perturbed tables (Mc of every step +/-0.1 and +/-0.2, start years +/-5).
- no declustering (full catalog): rates and b fitted on the full catalog, with
  aftershocks, instead of the declustered one.
- declustering: Gardner-Knopoff symmetric windows or Gruenthal instead of the
  reference Gardner-Knopoff (foreshock window 0.1 of the aftershock window).
- keep 1962 / 1998 events: two M7 events that declustering removes as
  aftershocks of 1960 and 1995 kept as mainshocks.
- classification tolerance -5 / +5 km: the catalog reclassified with the
  interface depth band around the Slab2 top 5 km narrower or wider (6 / 16 km
  instead of 11); moves events between interface, intra_slab and forearc.
- default-depth events to interface: events at an agency default depth (0, 10,
  33, 35 km), not relocated and without a mechanism, that were classified
  intra_slab or forearc above a slab top shallower than 50 km, moved to the
  interface (1305 events, 29 of M >= 5.5).
- rate: geodetic (mid): rates scaled to the geodetic moment rate instead of
  the catalog.
- MFD: tapered: tapered Gutenberg-Richter instead of truncated.
- full 16-branch tree: all combinations of geometry, rate and MFD with their
  weights, against the single reference branch.
- rupture scaling: Allen & Hayes: Allen & Hayes (2017) magnitude-area relation
  instead of Strasser et al. (2010).
- rupture aspect ratio 1.5 / 2 / 3: length / width of the ruptures instead of
  1 (limited by the down-dip width).
- MMIN_HAZ 6.5: sources from M6.5 instead of M5.5.

In-slab source
- completeness table, ends of the ensemble: as for the interface, per class
  (intra_slab, slab_deep), picking the tables with the lowest and highest
  N(>=M7).
- classification tolerance, default-depth events: as above, seen from the
  in-slab side (the same reclassified catalogs).
- Mmax pad 0 / 0.4: maximum magnitude = largest observed event per class plus
  0 or 0.4 instead of 0.2 (7.9 intra_slab, 8.2 slab_deep in the reference).
- smoothing neighbours 10 / 50: adaptive kernel bandwidth set by the 10th or
  50th nearest event instead of the 25th.
- pattern from all complete events / + calibrated kernel: spatial pattern from
  every complete event, and the kernel form, bandwidth and cut-off chosen by
  time-block cross-validation (Gaussian, 10 neighbours for every class).
- kernel gaussian / cut-off 200 km: Gaussian instead of power-law kernel; kernel
  truncated at 200 instead of 500 km.
- intra_slab b / slab_deep b floor: b and rate of each class refitted from
  M5.5 / 5.8 (intra_slab) and M5.7 / 6.0 (slab_deep).
- previous geometry: hypocentres at slab top + 7.5 km with the old depth-rule
  rupture band, instead of the catalog-based depths (hypocentre and lower
  seismogenic depth at 0.30 and 0.65 of the Slab2 thickness below the top).
- depths by slab-top regime: catalog-based depths in km per regime instead of
  thickness fractions.
- class domain cut at 50 km: each class smoothed only where its slab-top depth
  applies, instead of over the whole slab and summed.
- no declustering, declustering: as for the interface.
- rupture scaling, dip 45 / 90, aspect ratio 2: rupture geometry of the point
  sources (Allen & Hayes 2017 instead of Strasser et al. 2010; nodal-plane dip
  instead of 60; aspect ratio instead of 1).
- sources from M5.5: point sources from M5.5 instead of M4.9.

Crustal source (south only)
- faults vs no faults: the fault model removed, background only.
- cap and fault Mmin 6.5: background capped and faults starting at M6.5
  instead of 6.0.
- buffer margin 0 / 20 km, background Mmax 7.5, declustering, no declustering,
  classification: as named.

All families
- numerics: rupture mesh 5 km and point-source distance 100 km instead of 10
  and 40; a convergence check.

## 3. Ranked results

Largest range at any subduction city, 475 / 2475 yr, and where it occurs.

| axis | range % | where |
|---|---|---|
| in-slab GMM | 38 / 42 | Iquique, Santiago (Montalva -18, Parker +20) |
| interface GMM | 23 / 21 | Antofagasta (Kuehn +15, AG20 -8) |
| no declustering, all families | 20 / 21 | Puerto Montt; -6 to -17 at every interface city |
| interface geometry, segmented | 18 / 21 | Copiapo, Antofagasta (-16 to -18); -5 to -8 elsewhere |
| interface no declustering | 17 / 17 | Puerto Montt |
| interface b, fit floor | 15 / 13 | Puerto Montt |
| truncation 2.0 | 13 / 19 | bound |
| in-slab completeness | 12 / 4 | Valparaiso +12 at 475 yr only; +/-4 elsewhere |
| in-slab classification tolerance | 10 / 7 | Puerto Montt +9; -5 to +4 elsewhere |
| interface Z_BOTTOM | 10 / 10 | sign changes along the margin |
| interface completeness | 10 / 7 | Puerto Montt -7; -2 to -4 elsewhere |
| truncation 2.5 / 4.0 | 8 / 12 | -4.5 / +3 |
| interface aspect ratio 1.5 / 2 / 3 | 6 / 5 | +2 to +6 at 3, ~0 at Santiago |
| in-slab Mmax pad | 5 / 7 | |
| in-slab smoothing neighbours | 5 / 4 | Concepcion |
| in-slab b floors | 5 / 5 | |
| in-slab previous geometry | 5 / 3 | the depth correction |
| in-slab no declustering | 4.5 / 5 | |
| interface Allen & Hayes | 4.5 / 5 | central cities |
| interface Z_TOP, 16-branch tree | 4 / 5-6 | |
| in-slab calibrated kernel, gaussian, cut-off, class cut, dip | 4 / 3-5 | |
| in-slab and interface declustering methods, geodetic rate, tapered MFD, in-slab Allen & Hayes, interface classification tolerance | 2-3 | |
| numerics | 2 / 2 | 4 at Puerto Aysen |
| in-slab depth rule, in-slab aspect ratio, default-depth events, keep 1962/1998, MMIN_HAZ, in-slab Mmin 5.5 | <= 1.5 | |

Southern cities: crustal faults vs no faults 54 % at Puerto Aysen, 12 % at
Pucon; crustal GMM 23 and 11 %; cap and fault Mmin 14 % at Aysen; crustal full
catalog 9 % at Aysen; in-slab GMM 16 % at Pucon.

## 4. Highlights

1. Ground motion dominates. The in-slab GMM axis (38-42 %) is the largest
   epistemic term on the margin and larger than all in-slab source terms
   together; the interface GMM axis (21-23 %) is second. On soil the in-slab
   GMM axis was only 12-15 %: the nonlinear site term compressed it. The rock
   reference is what exposes it.
2. The interface source choices matter; the in-slab ones do not. Interface
   geometry, b, the catalog convention and Z_BOTTOM each move PGA 10-20 % at
   some city, because the M8.5-9 rates are weakly constrained. Every in-slab
   source choice is at or below 5 % except two single-city effects (completeness
   at Valparaiso, tolerance at Puerto Montt), because the catalog fixes the
   in-slab rates at the magnitudes that make the hazard.
3. The catalog convention is settled by evidence, not by outcome. The full
   catalog lowers the interface hazard 6-17 % because its aftershock-rich b,
   extrapolated to M8-9, undercuts the observed rates: fitted / observed N(>=M)
   is 0.84 at M7.5 and 0.62 at M8 for the declustered fit, 0.65 and 0.36 for the
   full catalog. The declustered fit reproduces the large events; that it is
   also the conservative choice is secondary.
4. Classification choices are small. The interface tolerance +/-5 km moves 5 000
   events between classes and PGA by 1-5 % (9 % at Puerto Montt); moving the
   1305 default-depth events to the interface changes PGA by <= 0.8 %.
5. Completeness uncertainty is comparable to the statistical one. The interface
   b stays at 0.77-0.80 across the 15 tables (sigma_b is larger); in-slab b varies
   0.87-0.96 (intra_slab) and 1.00-1.09 (slab_deep). Hazard effects are -7 to +3 %
   (interface) and +/-4 % (in-slab), except Valparaiso +12 % under one in-slab
   table.
6. Rupture geometry and numerics are converged: scaling, aspect ratio, dip,
   mesh and point-source distance are all within 6 %.
7. The in-slab model reproduces the catalog near the northern and central
   cities (model / catalog 0.7-1.0 at M5.5 and 0.9-1.2 at M6 within 150 km)
   under every variant. Concepcion is the exception: 2.0-2.9 at M5.5 (12
   observed events) under every smoothing, classification, completeness and
   catalog variant, including the default-depth fix (2.44). The excess is not a
   modelling choice; it goes to the catalog review.
8. The in-slab dominance at Santiago and Iquique holds under every source
   parameter, class labelling, depth rule, classification and GMM: 33-76 % of
   the hazard across the in-slab GMMs, 57-62 % in the tree.

## 5. Interpretation by family

In-slab. Rates are fixed by the catalog at the magnitudes that matter, depths
now follow the observed depth of the events in the plate, the kernel is
calibrated by cross-validation, and every labelling, fitting, geometry and
catalog choice moves the hazard by 5 % or less at nearly every city. The only
term that matters is the GMM. Two single-city effects deserve a look before the
final model: the Valparaiso sensitivity to one completeness step of intra_slab,
and the Puerto Montt sensitivity to the interface tolerance (few in-slab events,
so a reclassification moves a large share). Concepcion's rate excess survives
every variant and is a catalog question.

Interface. The M8.5-9 rates are weakly constrained, so fit and geometry propagate:
segmentation, b, Z_BOTTOM and the catalog convention. The convention is decided
by the fit to the observed large-event rates (declustered). Completeness is a
minor contributor at 2-7 %. Rate branches, MFD shape, declustering method,
Z_TOP, scaling, aspect ratio, classification and the rest of the 16-branch tree
are within 2-6 %.

Crustal. Irrelevant at the subduction cities. At Puerto Aysen the fault model
is the hazard (54 %), with the crustal GMM (23 %), fault Mmin and cap (14 %) and
the full catalog (9 %); at Pucon faults and GMM are 11-12 %. These terms are the
subject of the study and are developed in the final model, not collapsed.

GMM and truncation. The in-slab GMM axis is the largest term anywhere; the
interface GMM second. Truncation is fixed at 3.0; 2.5-4.0 is a +/-5 % band.

Site. The soil run compressed the slab GMM axis threefold and hid the rock
levels; every other ranking was the same. The campaign is stated on rock.

## 6. Classification for the final model

### 6a. Logic-tree branches (epistemic, carried)

| term | range | branches |
|---|---|---|
| in-slab GMM | 38-42 % | AG20, Parker (SA_S), Montalva; weights from residuals against Chilean records |
| interface GMM | 21-23 % | AG20, Parker, Kuehn; weights from residuals |
| interface geometry | 18-21 % | full margin, segmented; weights from historical rupture extents |
| interface b | 13-15 % | data-based, from the fit uncertainty (6c-a), not fit floors |
| interface Z_BOTTOM | 10 % | from the interface event depths (6c-b); two values if it stays open |
| crustal GMM | 23 % Aysen, 11 % Pucon | ASK14, BSSA14, CB14, CY14 |
| crustal fault model | 54 % Aysen, 12 % Pucon | slip-rate, Mmax method, MFD shape and phi branches, never on / off |
| in-slab Mmax | 5-7 % | catalog Mmax plus 0 / 0.2 / 0.4, or fixed at 0.2 with one sentence |

Fixed and stated, not branches: declustered catalog (gk74); truncation 3.0;
Vs30 800 with Z1.0 40 m and Z2.5 0.6 km; mesh 10 km and point-source distance
40 km; integration distance (400 km in this campaign, 500 km in the final model).

### 6b. Collapsed to the reference value

Interface: seismic rate (geodetic 3 %), truncated GR (tapered 3 %), gk74
declustering (methods 3 %), 1962 / 1998 as aftershocks (1 %), MMIN_HAZ 5.5
(0.1 %), Z_TOP 5 km (4-5 %), Strasser scaling (4.5 %), aspect ratio 1 (3 would
add up to 6 % at the coast), classification tolerance 11 km (2 %), default-depth
rule (0.3 %), completeness table (-7 to +3 %, stated), the rate and MFD branches
of the 16-branch tree given the geometry (4-6 %).

In-slab: summed classes (4 %), gk74 declustering (methods 3 %, full catalog
4.5 %), fit floors 5.6 / 5.8 (5 %), catalog depths by thickness fraction (regime
1.5 %, previous geometry 5 %), calibrated Gaussian kernel with 10 neighbours
(other settings 4-5 %), Strasser scaling (3 %), dip 60 (4 %), aspect ratio 1
(1.4 %), Mmin 4.9 (0 %), classification tolerance 11 km (5 %, 9 % at Puerto
Montt, stated), default-depth events to the interface (0.8 %), completeness
(+/-4 %, Valparaiso +12 %, stated).

Crustal at the subduction cities: everything (<= 1.5 %). At the southern
cities nothing crustal is collapsed.

About thirty collapsed axes of <= 5 % each are "none carried", not "no effect".

### 6c. Dedicated analysis before fixing a value

a. Interface b and rate: b per geometry with its statistical uncertainty
   (bootstrap or likelihood), carried as data-based branches if sigma_b is
   large, one value otherwise; the interface rate check against the catalog
   within 150 km of each city.
b. Interface Z_BOTTOM: from the depth distribution of the classified interface
   events (the profile made for the in-slab class), with thermal and locking
   constraints.
c. GMM weights: residuals of the in-slab and interface models against Chilean
   records.
d. Crustal fault model at Puerto Aysen and Pucon: each fault term isolated
   (phi, Mmax method, MFD shape, slip rates), then weighted from the data.
e. Concepcion in-slab rate: the catalog review (next section).
f. Valparaiso in-slab completeness: which step of the intra_slab table drives the
   +12 %, and whether the reference table is right there.

## 7. Carried over to the catalog review

The campaign varied the models' parameters; the catalog they are fitted to is
the next piece of work (cat_handler_2):
- source preference rules per field (location, depth, Mw, mechanism) as a
  table, with provenance per event;
- one overrides file for event-level decisions from publications (the
  Pichilemu 2010 doublet, the Chiloe 2016 earthquake as interface, others);
- review of every large event (Mw, depth, mechanism, class) with automatic
  flags: mechanism inconsistent with class, default depth, source
  disagreement, duplicates, great sequences;
- the default-depth rule (to interface) moved from a sensitivity variant into
  the classification;
- Concepcion's in-slab rate as a specific target of the review;
- the reference classified catalog regenerated by code (today's file differs
  from the code's output by a few events).

## 8. Kept out of the analysis by choice

Soil profiles and site terms, the sigma model, regional vs global GMM
coefficients, magnitude homogenization (Mw from Cabello et al.), a second slab
model, segment boundary positions, non-stationarity after 2010 and 2014,
spatially variable b, spectral periods (with the final model), comparison with
published models (a later, separate exercise).
