# DECISIONS

Still-valid scientific decisions, latest version only, one line each, date where known.
New lines are added from the project conversations ("write the brief"); Claude Code proposes, Pablo adds.

## Scope
- Chile PSHA manuscript: hazard model, sensitivity, logic tree, pseudo-prospective testing in the same paper (24 Oct).
- The Chile fault model is part of Chile PSHA; the paper's question includes the hazard increase from faults, so faults are always in and fault terms are developed, never collapsed (30 Sep, 8 Nov).
- The same model goes to Renta Nacional later, as a separate project (8 Nov).
- Settings per tectonic class, next to the class, no single large config (24 Oct).

## Catalog
- Compiled and harmonized from scratch in `psha_chile8/catalog/`, with S. Ruiz's source ordering; nothing from cat_handler_2 carries over as a rule (8–9 Nov). Old rules are reference only (LEARNINGS).
- Cabello et al. (2025) not used for events from 1900 on (8 Nov).
- Source order (S. Ruiz, 10 Nov): Ruiz and Madariaga (2018) for large events; Centennial catalogue (1900 on); ISC-GEM (1900–1999); Potin et al. (1982–2022); CSN (2022 to today); Cabello et al. (2025) before 1900. Starting order only: quality of location, depth, magnitude and mechanism is checked per source, and the order may differ by property. Per-period, per-property record in `catalog/PREFERENCES.md` (10 Nov).
- Catalog runs to today (10 Nov).
- Before 1904 Cabello only; Potin ends 2020-07-16, CSN after; mechanisms GCMT first, then ComCat (13 Nov; the legacy USGS WCMT tensors of 2010 carry wrong moments, A6).
- Centennial catalogue taken from the Wayback snapshot of 2013-09-09 of the USGS page (USGS no longer hosts it); the snapshot is the version (10 Nov).
- CSN after Potin: the sismologia.cl daily catalogue pages, 2020-01-01 to the download date, all magnitudes (source csn); not relocated. The GUC origins of the ISC Bulletin kept as a separate source (csn_isc) (10 Nov).
- ISC-EHB depth quality L1–L3 from the ISC-EHB catalogue search (10 Nov).
- GCCEL (Bergman et al. 2023, calibrated locations, ISC dataset repository) added as a source and as the location and depth benchmark (task A2b) (11 Nov).
- Location and depth (A4): a local catalogue comes first only inside its own network: Potin et al. (1982 to 2020-07-16) and CSN web (after) at 18–46° S and not east of the arc (`data/intraarc.shp`), tested on the epicentre of the event's teleseismic members (ISC-EHB, ISC, ComCat) where it has one. Inside: Potin / CSN web → GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → CSN in ISC. Outside, and in 1964–1981: GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → Potin / CSN web → CSN in ISC. Before 1964: Centennial where EHB-relocated (1918–1942, 1956 on), else ISC-GEM, then ISC; before 1904 Cabello's epicentre. Epicentre and origin time from the first source; depth from the first source with a *measured* depth (not fixed, not ISC-EHB L3, not GCCEL codes c / i / u, not on a default bin of its agency), else unknown; no filling from Slab2; GCMT centroid depths never used (11 Nov).
- A local record more than 50 km from every teleseismic or GCCEL record of the event is not used (quality check; 94 events of Mw ≥ 4.5 in the domain, 423 of any size, run 2026-11-14b) (13 Nov).
- Depth: fixed depths, ISC-EHB L3 and agency default values are not measurements; a fixed ISC-EHB L1 depth is (held at its depth-phase value). Before 1964 only ISC-GEM depth quality A or B and free-depth Centennial solutions count. Offshore (more than 20 km from the coast) GCCEL and ISC-EHB L1 / L2 go before the local depth. σ at least 5 km, 10 km offshore, 20 km before 1964 (13 Nov; rules and support in `catalog/RULES_LOCATION_MAGNITUDE.md`).
- Potin depths are not replaced by ISC or ComCat depths (13 Nov, tried and dropped).
- Unknown depths are not filled in the catalogue. In A7 they are classified by mechanism, by the depth another agency gives in the ISC Bulletin (weak information), by position against Slab2, and with split weights where still ambiguous; fits are run with and without the split events (12 Nov).
- Every source catalog is cut to the box lat −58 to −15.5, lon −80 to −60, keeping an event if any of its origins is inside; Ruiz and Madariaga (2018) is not cut (27 of its events have no longitude). The final domain cut is applied on the chosen location (10 Nov).
- Ruiz and Madariaga (2018): where Table 1, its text and other sources disagree (date, Mw), the reading corroborated by an independent source (Centennial, Lomnitz 2004, GCMT) is used; readings listed in `catalog/NOTE_SRuiz_2026-11-10.md` (10 Nov).
- Ruiz and Madariaga (2018) is not an event source but an authority for the class and Mw of the events it names. In A3 its dates are first replaced by the corrected readings (NOTE_SRuiz), then each event is matched to a located event (date ±1 day, latitude within 2°, name checked by hand; by time and magnitude where a day has many events, logged for review) and lends it class and Mw; its own coordinates are not used. Mejillones 1994 is the event of 1994-12-10, Mw 6.0 (day and month swapped in the paper; X1); Taltal 1887 and Copiapó "1959-10-05" (= 1859) are not added (as cat_handler_2 DECISIONS 30) (10 Nov).
- Potin et al. (2024) magnitudes not used: they are the CSN bulletin values already in the ISC Bulletin (X1) (11 Nov).
- GCMT and USGS ComCat kept: mechanisms, and moment magnitudes as the reference for the homogenization (GCMT from Mw 5.4, the W-phase and regional Mw below; see Magnitudes (A5)) (13 Nov).
- Mw reconverted from native magnitude and scale; Cabello's conversion is wrong (8 Nov).
- Matching (A3): identity links first (ISC event IDs, and each agency's own solution found inside the ISC event within 1.5 s and 10 km); then time-and-distance windows from the measured same-event offsets per pair of sources, never below 10 s / 50 km, widened for large events; before 1964, 60 s / 300 km with every match reviewed; one-to-one assignment; magnitude never decides a match (11 Nov).
- Candia and Macedo (2026) is cited and compared, not used as a source (11 Nov).
- Large events (A6): a value is corrected only from a source that was read, recorded in `catalog/overrides_A6.csv` and applied as the last step of the run. Accepted on 13 Nov: 1543 Mw 7.7 (lower bound, Ruiz and Madariaga); 1878-01-23 longitude 70.3° W (CSN and NOAA web tables); 1934-03-01 depth 120 ± 20 km (Astiz and Kanamori 1986); 1949-04-20 Mw 7.1 and 1971-05-08 Mw 7.2 (same paper); 1959-06-14 Mw 7.2 (Abe 1982); Aysén 1960-06-06 Mw 7.7 (Kanamori and Rivera 2017); 2010-02-27 08:25 Mw 6.3; 2011-01-07 04:55 Mw 5.7. Left as they are, as a sensitivity case for the in-slab Mmax: 1918-05-20, 1925-05-15, 1934-03-01, 1948-05-11, 1971-06-17 (converted Centennial values 0.5–1.2 above the ISC-GEM proxies, no moment found). Settled by Pablo (13 Nov): Papudo 2001 and 1967-03-13 follow the general rule (GCMT 6.65; ISC-GEM direct 5.7), no exception; Santiago 1647 is in-slab, as in Ruiz and Madariaga (2018) (13 Nov).
- Magnitudes are computed on the final depths of `locate.py`, the A6 depth corrections included: 1934-03-01 (120 km) is converted as an intermediate-depth event, Mw 7.6 instead of 7.3, and leaves the list of events left as they are (Pablo, 14 Nov).
- Class hints without a literature reference are allowed where Pablo states the class: 2001-07-07 Mw 7.6 and 2015-09-16 23:18 Mw 7.1 are interface (thrust on the plate contact, consistent with the interface), `overrides_A6.csv`, accepted (14 Nov).
- A3 as run on 11 Nov (`catalog/match.py`, `merged/METHOD.md`): a record is matched to the closest member of an event; sources with identity links are completed first, then GCCEL, Potin and CSN web are attached; before 1964 the second pass uses 60 s / 300 km; one source listing an earthquake twice (2 s, 50 km, widened for large events) is one event (11 Nov).
- Events a source flags as non-earthquakes (explosion, quarry blast) are removed with every record matched to them, without exceptions. A Potin-only or CSN-only record 50–150 km from an ISC event at nearly the same time, with no other event nearby (`review/possible_splits`), is removed as a duplicate (11 Nov).
- Events matched across catalogs once, one ID per event; magnitude, location and mechanism each chosen by its own priority rule (8 Nov).
- Every catalog run is recorded in `DATA.md` until the final one (9 Nov).
- Frozen source tables are committed to git; raw downloads are not (kept on disk, archived with the data DOI) (10 Nov).

## Magnitudes (A5)
- Catalog cut at Mw 4.5 for the spatial pattern; conversions must be accurate at 4.5–6 (10 Nov). Fits start at Mw 5.0 and completeness is read with the events from Mw 3.5 (15 Nov, see Statistics).
- Conversions fitted on Chilean pairs only (matched by time and distance, no magnitude criterion) by inverse regression: the native magnitude is regressed on Mw, the slope corrected for the Mw error, and the relation inverted. Forward fits (Mw on native) are biased high below native ~5.5 because GCMT is incomplete there (X1, X2). The inverse step is new for this purpose; it is argued in the paper from truncated regression (Hausman and Wise 1977; Lolli et al. 2014, 2023). Published relations are a check only (11 Nov).
- Forms per scale: a straight line, or a line with a saturation hinge; split by depth (50 km) or period (1990, ISC and NEIC mb) as candidates; chosen by time-block cross-validation with the one-standard-error rule (the simplest form wins unless another is clearly better). Outside the data range the straight part continues and σ grows (11 Nov).
- One Mw scale (Hanks and Kanamori 1979 constant). Above Mw 5.4 GCMT first. Below 5.4 the W-phase and regional Mw (NEIC Mww, GUC Mwr and CSN web Mw, NEIC Mwr + 0.08, GFZ Mw + 0.04, CSN Mww last below 5.0; offsets measured on shared events) come before GCMT, following Lolli et al. (2023); a GCMT value below 5.4 that stands alone is lowered by 0.162 × (5.4 − GCMT), a line fitted on 812 pairs that is zero at 5.4, so there is no step (0.10 at 4.75, 0.06 at 5.0). Lolli et al. (2023) leave such values unchanged; we keep the line, as the magnitude-dependent offset of GCMT to the W-phase family, the same principle as the constant offsets of the other members (13 Nov).
- A CSN regional Mw more than 0.3 from the median of two or more other moment magnitudes of the event is left out (quality check, 26 values) (13 Nov).
- One Mw per event: Ruiz and Madariaga (the events it names), then a direct Mw in the order above, else one proxy by a fixed priority list of scales ordered by measured scatter (as Allen et al. 2018; Christophersen et al. 2024): NEIC and ISC surface-wave magnitudes, CSN ML, ISC mb, NEIC mb, INPRES ML. Converted magnitudes come only from the agencies that observe Chile directly or are the global references (ISC, NEIC, CSN / GUC, INPRES / SJA); every other agency of the ISC Bulletin and the coda, duration and untyped magnitudes are not converted, and an event with nothing else has no Mw and is listed. Surface-wave magnitudes are used without a magnitude limit, only for events not deeper than 60 km (Di Giacomo et al. 2015; Engdahl and Villaseñor 2002; Weatherill et al. 2016); a limit at Mw 5 biases the count at Mw ≥ 5 by +5 to +10 % or −7 to −15 % (X4). One converted scale per event; the weighted mean of the scales is a sensitivity case because it lowers large events where mb saturates. Potin magnitudes are not used (11–12 Nov). Before 1976 (13 Nov, after A6): a moment-based magnitude goes before a converted one, and inside each level the Centennial goes before ISC-GEM (S. Ruiz): Ruiz and Madariaga > Centennial Mw (Pacheco and Sykes, Harvard) > ISC-GEM direct Mw (flag d) > Centennial Ms, mB and untyped values converted by their type > ISC-GEM proxy Mw (flag p) > Cabello (before 1904). From 1976 a measured Mw (GCMT, W-phase and regional family) goes before Ruiz and Madariaga, whose value is used where no measured Mw exists and whose class is always used. The CSN moment magnitude listed as GUC MW in the ISC Bulletin (noisier than the others, sd 0.20, and reaching Mw 2) is not used to fit the relations or offsets; as an event Mw it comes last among the measured moment magnitudes, with the 0.3 cross-check (13 Nov, after run 2026-11-13d). Conversion relations are fitted only on pairs with a reference Mw ≥ 4.0 (Pablo, 13 Nov): the catalogue starts at 4.5 and smaller events must not steer the fit; a floor on the reference does not bias a native-on-Mw regression. Run 2026-11-13e: the floor moves no relation by more than 0.01 at 4.5–5.5. Each event keeps its σ; values dithered within the native 0.1 bin (11 Nov).
- Acceptance tests of the homogenized catalogue: b range ≤ 0.2 over fit floors 4.7–5.8; M ≥ 5.5 rate steady across 1976–89 / 1990–99 / 2000–10 / 2011–26; a GR fitted on Mw 5.0–6.5 predicts the observed M ≥ 7 count within the Poisson band, overall and per family; converted values within 0.1 of independent regional Mw; no comb or heap at 4.5–5.5 (11 Nov).
- Rate bias from magnitude uncertainty: every event counts exp(−β²σ²/2) with its own σ and the β of the fit (CEUS-SSC 2012, eq. 3.3.1-1 applied per event); no magnitude is moved; the same rule for all events, no logic-tree branch, no cap on σ (Pablo, 15 Nov). It lowers the rates by 8–11 % and leaves b as it is. Support: on the same events the converted magnitudes give about 8 % more events at Mw ≥ 5.6–6.0 than the measured ones, as expected from their errors; on synthetic catalogues the uncorrected N(≥ 5) is 10 % high (B9).

## Classification
- Depth kinds: measured, assigned, unknown. Where an event has no measured depth but the literature states its class (Ruiz and Madariaga 2018, or a source accepted in A6), the depth is assigned from that class and Slab2 at the epicentre: interface = the slab top, kept within the 10–50 km of the interface model; in-slab = inside the slab, by the convention of the in-slab sources; crustal = none, unless the literature gives one. Assigned depths are flagged, carry a large σ, and are never used to classify or to test a rule. The class comes first and the depth follows; no other depth is filled from the slab model (13 Nov).
- An event located below the slab counts as in-slab (general rule, covers Potin's too-deep depths under the flat slab; in-slab source depths come from Slab2 anyway) (11 Nov).
- Rules rebuilt in A7 (`tasks/A7_classification.md`, 13 Nov), few and general, no patch rules for single events:
  - Each event carries a weight per class (interface, in-slab, crustal, outer rise) adding up to 1; the rates sum the weights. A class from the literature (Ruiz and Madariaga 2018, A6 hints) has weight 1 and goes first.
  - Over the shallow slab (top ≤ 50 km) the depth gives class scores after Haynie et al. (2026): interface within ± 15 km of Slab2, fading between 50 and 65 km depth; crustal and in-slab share the rest (Moho fixed at 40 km). The scores are averaged over the depth error of the event (a normal distribution cut at the ground; ours, not in Haynie et al.) (14 Nov, run 2026-11-14a, X5).
  - Interface mechanism: the Slab2 plane slipping in the plate convergence direction (one azimuth, 257°). Misfit m = √((swing/20°)² + (twist/45°)²), smallest of the four descriptions of the double couple. m ≤ 1: interface odds × 3.9; m > 1: no interface. A mechanism never decides alone. Chosen over the Kagan angle and over "a thrust on the contact is interface" by six tests (literature events, mechanisms withheld, Riedel-Hornig et al. 2026 classes and depths, synthetic catalogues) (14 Nov, X5).
  - A weight ≥ 0.8 becomes 1, otherwise the event is split (kept 14 Nov). Deeper slab: depth with its error above or below the slab surface. With our depth errors no rule classes more than about two thirds of the events over the shallow slab correctly (synthetic test, X5); the split weights carry that uncertainty.
  - No depth: outer rise west of the trench; crustal where there is no slab; in-slab where the slab is deeper than 50 km and all rejected depths are ≥ 70 km; otherwise split by the shares of the classified events in the same position and magnitude bin. Fits run with and without the split events.
  - Sub-classes by position only. Class names: interface, antarctic_interface, intraslab_shallow, intraslab_intermediate, jujuy_nest, crustal forearc / arc / backarc / Patagonia, outer rise.
- Double seismic zone: not a catalogue class; the two planes are handled in the in-slab source model (plan C) (13 Nov).
- In-slab classes: shallow (slab top above 50 km at the epicentre), intermediate, and the Jujuy nest as a class of its own, so that it does not contaminate the in-slab model: within 0.8° of 66.9° W, 24.0° S, 150–320 km, measured depth. The upper limit was moved from 170 to 150 km on the depth histogram of the cluster (Pablo, 14 Nov; 1 054 events of Mw ≥ 4.5).
- Antarctic interface kept as a class for completeness; its source uses the geodetic model only, not the catalogue rates (13 Nov).

## Statistics (B9)
- Completeness is a property of the catalogue, not of the tectonic class: it is read on all events, by region and period, and one table is used for every class. A larger magnitude is never complete later than a smaller one (Pablo, 15 Nov).
- The table is automatic. From 1964 the steps come from the shape of the magnitude distribution with the events from Mw 3.5: Mc by b-stability and a Kolmogorov–Smirnov test per network window and region, the largest value, and a magnitude is complete from the window after the last one whose Mc is above it. Before 1964 a step is the earliest year from which the counts of a 0.5 band stay consistent with the instrumental Gutenberg–Richter line (5-year blocks, BIC), on all events (15 Nov).
- Completeness table, every class: Mw 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500 (15 Nov). Mw 4.5–4.9 is complete over the whole margin in no period and is not used in the fits.
- Rules that compare rates between periods (Stepp, change points, a joint likelihood) are not used from 1964 on: the sequences of 2010–2015 set the level and earlier periods read as incomplete (B9).
- Estimator: Weichert (1980) on the table with the class weights, event bootstrap; the largest magnitude in the likelihood is the Mmax of the class. Kijko and Smit (2012) is a check of the table (same b within the bootstrap error on a table that fits) and b-positive a check of b (15 Nov).
- Patagonia crustal: b of the forearc, own rate. Backarc and Jujuy nest: own fit at the floor of the table, no pooling; rough estimates (Pablo, 15 Nov).
- Left as they are and named in the discussion of the paper (Pablo, 15 Nov): the intermediate in-slab events of Mw ≥ 7 before 1976, which are more than the fit expects (29 against 18 on this table, by weight; old magnitudes probably too high), and the step Mw 8.0 from 1500, where the magnitudes before about 1730 are the least certain (the rule accepts it on 15 observed against 17 fitted).

## Interface
- Rates: seismic branch and geodetic branch (moment balance), weights 0.5 / 0.5; no moment-deficit approach (Sep–6 Oct).
- Geodetic: convergence 6.6 cm/yr fixed, coupling χ 0.7 / 0.8 / 0.9 (0.125 / 0.25 / 0.125 of the total weight) (6 Oct).
- Geometry: full margin and four segments, 0.5 / 0.5 (Sep).
- MFD tapered GR in both branches, corner Mw 9.6 fixed (Bird and Kagan 2004), stated (6 Oct).
- Mmax: largest historical event per segment, no pad (9.5 / 9.1 / 8.5 / 8.8); moment closure only as a diagnostic (6 Oct).
- Z_TOP 10 km, Z_BOTTOM 50 km fixed, stated (6 Oct).
- Rupture scaling: Strasser 2010 / Thingbaijam 2017, 0.5 / 0.5; Allen and Hayes stated (6 Oct).
- (a, b) branches at 5th / ML / 95th of N(≥ controlling M), weights 0.185 / 0.63 / 0.185 (6 Oct).
- Rate convention full vs declustered: open, decided with the new tornado at hand (9 Nov). Old tree had 0.5 / 0.5.
- Antarctic interface: PB2002 trench, dip 30°, 10–50 km, geodetic only, χ 0.5, 1.8 cm/yr, b of the southern segment, Mmax 8.5 from the area; inside every interface branch; Scotia–Antarctic trench left out (Oct).

## In-slab
- Depth of the in-slab sources (13 Nov; replaces "each plane its own source" of 8 Nov and the thickness-fraction rule of Sep): one point source per cell with three hypocentral depths and three weights (OpenQuake hypocentral depth distribution), all measured vertically below the Slab2 top. Layer boundaries per region, from the central 95 % of the distance of the events below the top, cut in three. Weights per cell from the share of the nearest well-located events in each layer; hypocentre per cell and layer from their median distance below the top (layer middle where too few). A double zone then shows as weight in the top and bottom layers, wherever it exists, without a yes / no decision.
- The map pattern stays 2-D and uses all in-slab events (split weights and unknown depths included); only the depth weights use depths. Depth information comes from precise depths only (σ about 5 km or better), weighted by precision; an event is not spread over the layers by its error (the observed distribution already contains the error, spreading would blur it twice). Jujuy nest and Potin's depths under the flat slab left out. One layer against three is a tornado factor (13 Nov).
- Upper and lower seismogenic depth of each in-slab point source: the top and bottom of the three layers under that cell (slab top to the bottom of the 95 % range). Large ruptures then fill that zone whatever layer their hypocentre is in, so no separate rule for the depth of large events is needed; to confirm in the OpenQuake documentation when the sources are built (13 Nov).
- Riedel-Hornig et al. (2026) (automatic, relocated, 2017–2021, 18–43° S, 620 000 events, depth error about 6 km; Zenodo 10.5281/zenodo.15284376): the data for the in-slab depth weights, and a depth benchmark at intermediate depth (test of Potin under the flat slab, which GCCEL cannot do). Its eastern hypocentres are too deep without Argentine stations (their p. 12–13). Whether it also becomes a location source of the catalogue for 2017–2021 is decided after that benchmark (13 Nov).
- Rates and b from the full catalog; declustered catalog only for the spatial pattern (Marzocchi and Taroni 2014) (Sep–24 Oct).
- No zonation; equal pattern weights; power-law kernel, 25 neighbours (30 Sep).
- Two nodal planes: N–S strike, 60° dipping west normal and 30° dipping east reverse (30 Sep).
- Mmax: observed maximum + 0.2 per class (Sep); whether historical events (Santiago 1647 M8.4, Pica 1768) count is open (Nov).
- b per class or pooled: decided after the new classes exist (B10).
- (a, b) variability: tried in the tornado once catalog and Mc are reasonable (9 Nov).

## Crustal and faults
- Background classes forearc, intraarc, backarc, patagonia_crustal; unclassified gets no forecast (Oct).
- One point fit per class, no (a, b) branches, no perturbed tables; rates from the full catalog, no declustering for rates, pattern declustered (7 Oct).
- No removal of crustal events after interface mainshocks, even if correlated (24 Oct).
- Backarc own b; Patagonia crustal borrows the forearc b with its own rate (Oct).
- Background Mmax: observed maximum + 0.2 per class (Sep).
- Large intra-arc event reported by Kanamori (> 7.5, probably multi-rupture): open. Its Mmax may change the fault hazard significantly; check whether it is Aysén 1960 (9 Nov).
- Fault source: shapefile `crustal_faults_chile_updated` is authoritative, read in code (6 Oct).
- Slip rate: reported average, one value (30 Sep).
- Aseismic coefficient ψ 0.6 / 0.8 / 1.0, weights 0.25 / 0.5 / 0.25 (6 Oct).
- Mmax: observed + 0.2 / Wells and Coppersmith 1994 area / Leonard 2014 area, 1/3 each; Leonard where no observed maximum (6 Oct).
- MFD shapes: AL-I, AL-II, AL-III, Youngs–Coppersmith, tapered, hybrid, 1/6 each (6 Oct).
- Fault seismogenic depth 10 / 20 km, checked in the new tornado (9 Nov).
- Fault Mmin and background cap 6.0 inside down-dip-aware fault buffers (5 km margin), background hypocentre 10 km (6 Oct).
- Multi-fault ruptures: not in the model (aborted, future work) (Oct).

## Magallanes–Fagnano
- Own analysis (plan D): segments, Chilean / Argentine overlap, slip rate (3 mm/yr database vs 4–7 GPS), Mmax, single or joined source (24 Oct).
- Mmax: to be checked thoroughly in D. Old model used a system value 8.0 + 0.2 from the 1949 event (6 Oct).

## GMMs
- Interface and in-slab: AG20, Parker (SA_S), Kuehn, Montalva, 0.25 each; Montalva must be in for both subduction types (6 Oct).
- Crustal: ASK14, BSSA14, CB14, CY14, 0.25 each; Patagonia treated as active crust, stable-crust GMM dropped (Oct).
- Equal weights, no residual analysis (Oct).
- New tornado (E17) also runs the GMM sets of the GEM South America model and of the official Chilean hazard map, to separate the GMM effect from the source-model effect in the hazard difference to those models; a test, not a branch unless it passes the ≥ 5 % rule (10 Nov).
- Idini et al. (2017) and BC Hydro out; sigma_mu_epsilon not tested, left as a question for collaborators (Oct).

## Logic tree
- Branch rule: an axis that moves PGA 475 yr by ≥ 5 % at some city becomes a branch, unless a statistical or physical criterion fixes the value (then fixed and stated with its range) (6 Oct).
- Fit parameters (floor, Mc, Mmax) are set by statistical or physical criteria, not by the tornado (30 Sep).
- Family split: one OpenQuake job per family, combined exactly (LOGIC_TREE_equivalence.md) (1 Oct).
- psha_chile6 final tree is the starting tree; the new tornado decides the final one (8 Nov).

## Hazard runs
- Rock: Vs30 800 inferred, Z1.0 40 m, Z2.5 0.6 km; truncation 3 (Sep–6 Oct).
- Maximum distance: interface 600, in-slab 500, crust 300 km; point-source distance 100 km (6 Oct).
- Working runs and tornado at 475 yr only; 2475 yr only in the final run (Sep).
- 14 cities: Iquique, Antofagasta, Calama, Copiapó, La Serena, Valparaíso, Santiago centro, Santiago Peñalolén, Concepción, Pucón, Puerto Montt, Hornopirén, Puerto Aysén, Puerto Williams (30 Sep).
- Tornado output: one collaborator figure with every factor, one paper figure with the non-trivial factors (30 Sep).

## Testing
- Pseudo-prospective: catalog cropped at 2009-12-31, training models with the frozen recipe (faults and geodetic unchanged), yearly rates, branches converted with hazard2csep to pyCSEP / floatCSEP, tested on 2010–2022 per family on its own domain (8 Nov).
- Test of the spread between branches (own method); results reported, not fed back into the tree (8 Nov).

## Figures
- One palette and one set of display names for all figures; Ubuntu font (2 Nov).
- Figures drawn with pituPLOTS (installed editable in psha_renta, commit recorded per run); sections perpendicular to the Nazca trench (`data/shapefiles/sam_nazca_trench.shp`), gray basemap; sections in A7 (10 Nov).
- FIGURES.md is the figure manifest: every paper figure, status, producing script.

## Superseded (only where the reversal matters)
- Cabello et al. (2025) as the trusted base catalog and its Mw as authoritative (24 Oct) → corrected per agency (A2, 4 Nov) → dropped from 1900 on, catalog rebuilt (8 Nov).
- Declustered catalog for rates (campaign, Sep) → full catalog for rates, declustered only for the pattern (30 Sep).
- Completeness-window event weights for the pattern (Hiemer style) → equal weights (30 Sep).
- Interface Mmax by moment closure → historical per segment, closure a diagnostic (6 Oct).
- Hand classes for unknown-depth events near cities → withdrawn, sensitivity instead (3 Nov).
- Local catalogue first for location and depth everywhere, no exceptions (11 Nov) → first only inside its own network (A4, 11 Nov).
- Centennial before ISC-GEM for every magnitude before 1976 (13 Nov) → only within the same level, moment-based before converted (13 Nov, after A6: 38 converted Centennial values had replaced ISC-GEM direct Mw, 0.4 high on average). Mechanisms ComCat first (10 Nov) → GCMT first (13 Nov).
- Jujuy nest no longer a class of its own (9 Nov) → a class of its own again (13 Nov). Upper depth limit 170 → 150 km (14 Nov).
- 1934-03-01 left at Mw 7.3 (13 Nov) → Mw 7.6 on its accepted depth (14 Nov).
- Interface band = the Slab2 depth uncertainty (13 Nov, run f) → ± 15 km (run j: on 1 270 events with a mechanism, classified without it, the Slab2 uncertainty gave 20 % too little interface). A thrust on the contact allows all classes (13 Nov, f) → is interface alone (i, j) → raises the interface odds, plane and slip misfit (14 Nov, run 2026-11-14a). Depth σ over the shallow slab from the thrust scatter (run g) → rolled back the same day: depth hardly separates the interface whatever σ (blind test), so the split count was the wrong target.
- Surface-wave magnitudes not used below Mw 5 (11 Nov) → no magnitude limit, shallow events only (X4, 12 Nov). GCMT below 5.4 lowered by a step per 0.25 bin → by a line that is zero at 5.4 (12 Nov).
- Potin depths under 20 km or over 80 km near the coast replaced by GCCEL / ISC-EHB / ISC / ComCat (13 Nov) → dropped the same day: not supported; the local study is expected to locate better. A fixed ISC-EHB L2 depth as a last resort (3 events) → dropped. Pre-1964 depths judged by "not on a multiple of 5 km" → by the catalogues' own depth flags (13 Nov).
- All statistical work at Mw ≥ 4.5 (10 Nov) → fits from Mw 5.0, completeness read from Mw 3.5 (15 Nov, B9: Mw 4.5–4.9 complete margin-wide in no period).
- Magnitude-error correction by the CEUS-SSC shift to M − βσ² and N* (11 Nov) → no shift; the count weight exp(−β²σ²/2) on every event (15 Nov; a shift is biased when completeness varies with magnitude, CEUS-SSC §3.3.1, and moved historical events by 0.2–0.9 units).
