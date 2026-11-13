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
- Before 1904 Cabello only; Potin ends 2020-07-16, CSN after; mechanisms ComCat first, then GCMT (10 Nov).
- Centennial catalogue taken from the Wayback snapshot of 2013-09-09 of the USGS page (USGS no longer hosts it); the snapshot is the version (10 Nov).
- CSN after Potin: the sismologia.cl daily catalogue pages, 2020-01-01 to the download date, all magnitudes (source csn); not relocated. The GUC origins of the ISC Bulletin kept as a separate source (csn_isc) (10 Nov).
- ISC-EHB depth quality L1–L3 from the ISC-EHB catalogue search (10 Nov).
- GCCEL (Bergman et al. 2023, calibrated locations, ISC dataset repository) added as a source and as the location and depth benchmark (task A2b) (11 Nov).
- Location and depth (A4): a local catalogue comes first only inside its own network: Potin et al. (1982 to 2020-07-16) and CSN web (after) at 18–46° S and not east of the arc (`data/intraarc.shp`), tested on the epicentre of the event's teleseismic members (ISC-EHB, ISC, ComCat) where it has one. Inside: Potin / CSN web → GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → CSN in ISC. Outside, and in 1964–1981: GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → Potin / CSN web → CSN in ISC. Before 1964: Centennial where EHB-relocated (1918–1942, 1956 on), else ISC-GEM, then ISC; before 1904 Cabello's epicentre. Epicentre and origin time from the first source; depth from the first source with a *measured* depth (not fixed, not ISC-EHB L3, not GCCEL codes c / i / u, not on a default bin of its agency), else unknown; no filling from Slab2; GCMT centroid depths never used. Depth σ from X3 below 70 km and X1 from 70 km, at least 10 km offshore (11 Nov).
- Unknown depths are not filled in the catalogue. In A7 they are classified by mechanism, by the depth another agency gives in the ISC Bulletin (weak information), by position against Slab2, and with split weights where still ambiguous; fits are run with and without the split events (12 Nov).
- Every source catalog is cut to the box lat −58 to −15.5, lon −80 to −60, keeping an event if any of its origins is inside; Ruiz and Madariaga (2018) is not cut (27 of its events have no longitude). The final domain cut is applied on the chosen location (10 Nov).
- Ruiz and Madariaga (2018): where Table 1, its text and other sources disagree (date, Mw), the reading corroborated by an independent source (Centennial, Lomnitz 2004, GCMT) is used; readings listed in `catalog/NOTE_SRuiz_2026-11-10.md` (10 Nov).
- Ruiz and Madariaga (2018) is not an event source but an authority for the class and Mw of the events it names. In A3 its dates are first replaced by the corrected readings (NOTE_SRuiz), then each event is matched to a located event (date ±1 day, latitude within 2°, name checked by hand; by time and magnitude where a day has many events, logged for review) and lends it class and Mw; its own coordinates are not used. Mejillones 1994 is the event of 1994-12-10, Mw 6.0 (day and month swapped in the paper; X1); Taltal 1887 and Copiapó "1959-10-05" (= 1859) are not added (as cat_handler_2 DECISIONS 30) (10 Nov).
- Potin et al. (2024) magnitudes not used: they are the CSN bulletin values already in the ISC Bulletin (X1) (11 Nov).
- GCMT and USGS ComCat kept: mechanisms, and GCMT Mw as the reference for magnitude homogenization (10 Nov).
- Mw reconverted from native magnitude and scale; Cabello's conversion is wrong (8 Nov).
- Matching (A3): identity links first (ISC event IDs, and each agency's own solution found inside the ISC event within 1.5 s and 10 km); then time-and-distance windows from the measured same-event offsets per pair of sources, never below 10 s / 50 km, widened for large events; before 1964, 60 s / 300 km with every match reviewed; one-to-one assignment; magnitude never decides a match (11 Nov).
- Candia and Macedo (2026) is cited and compared, not used as a source (11 Nov).
- Events matched across catalogs once, one ID per event; magnitude, location and mechanism each chosen by its own priority rule (8 Nov).
- Every catalog run is recorded in `DATA.md` until the final one (9 Nov).
- Frozen source tables are committed to git; raw downloads are not (kept on disk, archived with the data DOI) (10 Nov).

## Magnitudes (A5)
- Catalog cut at Mw 4.5; all statistical work (completeness included) and the spatial pattern use M ≥ 4.5. Conversions must be accurate at 4.5–6 (10 Nov).
- Conversions fitted on Chilean pairs only (matched by time and distance, no magnitude criterion) by inverse regression: the native magnitude is regressed on Mw, the slope corrected for the Mw error, and the relation inverted. Forward fits (Mw on native) are biased high below native ~5.5 because GCMT is incomplete there (X1, X2). The inverse step is new for this purpose; it is argued in the paper from truncated regression (Hausman and Wise 1977; Lolli et al. 2014, 2023). Published relations are a check only (11 Nov).
- Forms per scale: a straight line, or a line with a saturation hinge; split by depth (50 km) or period (1990, ISC and NEIC mb) as candidates; chosen by time-block cross-validation with the one-standard-error rule (the simplest form wins unless another is clearly better). Outside the data range the straight part continues and σ grows (11 Nov).
- One Mw scale (Hanks and Kanamori 1979 constant). Above Mw 5.4 GCMT first. Below 5.4 the W-phase and regional Mw (NEIC Mww, GUC Mwr and CSN web Mw, NEIC Mwr + 0.10, GFZ Mw + 0.03, CSN Mww last below 5.0) come before GCMT, following Lolli et al. (2023); a GCMT value below 5.4 that stands alone is lowered by 0.159 × (5.4 − GCMT), a line fitted on 813 pairs that is zero at 5.4, so there is no step (0.10 at 4.75, 0.06 at 5.0) (12 Nov).
- One Mw per event: Ruiz and Madariaga (the events it names), then a direct Mw in the order above, else one proxy by a fixed priority list of scales ordered by measured scatter (as Allen et al. 2018; Christophersen et al. 2024): NEIC and ISC surface-wave magnitudes, CSN ML, ISC mb, NEIC mb, INPRES ML. Converted magnitudes come only from the agencies that observe Chile directly or are the global references (ISC, NEIC, CSN / GUC, INPRES / SJA); every other agency of the ISC Bulletin and the coda, duration and untyped magnitudes are not converted, and an event with nothing else has no Mw and is listed. Surface-wave magnitudes are used without a magnitude limit, only for events not deeper than 60 km (Di Giacomo et al. 2015; Engdahl and Villaseñor 2002; Weatherill et al. 2016); a limit at Mw 5 biases the count at Mw ≥ 5 by +5 to +10 % or −7 to −15 % (X4). One converted scale per event; the weighted mean of the scales is a sensitivity case because it lowers large events where mb saturates. Potin magnitudes are not used (11–12 Nov). Before 1976: Ruiz and Madariaga > ISC-GEM > Centennial (converted by its type) > Cabello (before 1904); Centennial before ISC-GEM is pending S. Ruiz's answer, and every M ≥ 7 where the two differ by ≥ 0.3 goes to A6. Each event keeps its σ; values dithered within the native 0.1 bin (11 Nov).
- Acceptance tests of the homogenized catalogue: b range ≤ 0.2 over fit floors 4.7–5.8; M ≥ 5.5 rate steady across 1976–89 / 1990–99 / 2000–10 / 2011–26; a GR fitted on Mw 5.0–6.5 predicts the observed M ≥ 7 count within the Poisson band, overall and per family; converted values within 0.1 of independent regional Mw; no comb or heap at 4.5–5.5 (11 Nov).
- Rate bias from magnitude uncertainty: the CEUS-SSC (2012, §3.3.1) procedure for directly observed magnitudes (shift to E[M] = M − βσ², then N*), which lowers rates; not the N* alone, which is for forward-regression values. Equations re-checked in step B; fits also run without it (11 Nov).

## Classification
- An event located below the slab counts as in-slab (general rule, covers Potin's too-deep depths under the flat slab; in-slab source depths come from Slab2 anyway) (11 Nov).
- Rules rebuilt in A7; classes and source models renamed consistently at the same time (9 Nov). Naming scheme: open.
- Double seismic zone: where it exists is to be found first (possibly only in the intermediate-depth slab); upper and lower plane become in-slab classes there (8–9 Nov).
- Jujuy nest no longer a class of its own (9 Nov).
- How to handle shallow in-slab (slab top < 50 km) vs intermediate-depth in-slab, together with the double seismic zone: open (9 Nov).

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
- Double seismic zone: each plane its own source at small M, one source at large M; construction and merge magnitude tested in the new tornado (8 Nov).
- Rates and b from the full catalog; declustered catalog only for the spatial pattern (Marzocchi and Taroni 2014) (Sep–24 Oct).
- No zonation; equal pattern weights; power-law kernel, 25 neighbours (30 Sep).
- Depths from Slab2 top and thickness: one hypocentre and one lower seismogenic depth per cell, by thickness fraction (Sep).
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
- Surface-wave magnitudes not used below Mw 5 (11 Nov) → no magnitude limit, shallow events only (X4, 12 Nov). GCMT below 5.4 lowered by a step per 0.25 bin → by a line that is zero at 5.4 (12 Nov).


- A3 as run on 11 Nov (`catalog/match.py`, `merged/METHOD.md`): a record is matched to the closest member of an event; sources with identity links are completed first, then GCCEL, Potin and CSN web are attached; before 1964 the second pass uses 60 s / 300 km; one source listing an earthquake twice (2 s, 50 km, widened for large events) is one event (11 Nov).
- Events a source flags as non-earthquakes (explosion, quarry blast) are removed with every record matched to them, without exceptions. A Potin-only or CSN-only record 50–150 km from an ISC event at nearly the same time, with no other event nearby (`review/possible_splits`), is removed as a duplicate (11 Nov).