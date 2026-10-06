# The catalog of psha_chile: hand-off

Status 2026-09-30. Code: `cat_handler_2` (README.md, DECISIONS.md, CONTEXT.md), commit `64c2617`; final `catalog.csv` written 2026-09-30 11:02. Figures for the presentation: `results/cat_handler_2/slides/`.

## Pipeline

| stage | count |
|---|---|
| Cabello rows south of 17 S with M > 3.9 | 64,439 |
| earthquakes after removing cross-agency copies | 50,218 (22% of rows were copies) |
| CSN rows relocated with Potin here (besides Cabello's own) | 5,456 |
| default or missing depths filled (group, Potin, GCMT) | 2,545 of 8,019 |
| events with a focal mechanism | 2,458 (35% of M >= 5.5) |
| magnitudes taken from Ruiz and Madariaga (2018) | 21 |
| `catalog_base.csv` | 50,218 events |
| `catalog.csv`: classified, 13 classes in 4 families | 50,218 events |

## Key numbers

**Duplicates.** Share of Cabello rows that were copies of another agency's row, by magnitude: 3.9-4.4: 21%, 4.4-4.9: 26%, 4.9-5.4: 25%, 5.4-5.9: 11%, 5.9-6.4: 16%, 6.4-6.9: 8%, 6.9-7.4: 9%, 7.4-7.9: 14%, 7.9-8.4: 0%.

**Depth status** (share of events): free 50.3%, relocated_cabello 22.4%, fixed 10.9%, relocated_potin 10.9%, filled 5.1%, assigned 0.6%. The classifier trusts relocated, free and filled depths only.

**Mechanisms.** anss 1,814, gcmt 475, cabello 121, gem 48.

**Magnitudes.** Cabello's Mw for the same earthquake, by agency, against the GCMT Mw (median): CSN -0.10, USGS +0.10, ISC -0.30. Events present only as ISC rows carry an Mw about 0.3 low (DECISIONS 32).

**Counts per family and magnitude bin** (campaign rows / campaign deduplicated / new, common ground: Cabello magnitude, years 1513-2022, lon -78.5 to -65.0, lat -57.6 to -16.0):

| M | interface | in-slab | crustal |
|---|---|---|---|
| 3.9-4.5 | 13334 / 11220 / 11644 | 18805 / 12616 / 13107 | 4881 / 4119 / 2972 |
| 4.5-5.0 | 4974 / 3854 / 3447 | 10626 / 7573 / 6055 | 1618 / 1170 / 625 |
| 5.0-5.5 | 1886 / 1537 / 1716 | 3530 / 2888 / 2820 | 759 / 628 / 282 |
| 5.5-6.0 | 486 / 421 / 459 | 744 / 658 / 538 | 179 / 159 / 60 |
| 6.0-6.5 | 171 / 127 / 174 | 257 / 166 / 149 | 103 / 89 / 21 |
| 6.5-7.0 | 83 / 70 / 103 | 105 / 96 / 63 | 40 / 36 / 9 |
| 7.0-10.0 | 71 / 65 / 85 | 36 / 31 / 23 | 20 / 11 / 4 |

**Family moves at M >= 5.5** (rows campaign, columns new):

| | interface | in-slab | crustal | excluded |
|---|---|---|---|---|
| interface | 834 | 22 | 6 | 2 |
| in-slab | 152 | 972 | 7 | 155 |
| crustal | 37 | 65 | 101 | 150 |
| excluded | 7 | 7 | 0 | 106 |

**M >= 7 events:** 154; against Ruiz and Madariaga (2018): 47 same class, 2 different (check/review_rm.csv).

## Hand decisions

| file | id | field | value | reason |
|---|---|---|---|---|
| overrides.csv | 83388 | time_iso | 2010-02-27T06:35:14 | Maule 2010: Cabello time is 3 h early (local time); GCMT centroid time 06:35:14 UTC for th |
| overrides.csv | 43 | mag | 9.0 | Concepcion 1751: Mw ~9 in the paper (Cabello 8.50) |
| overrides.csv | 160 | mag | 7.5 | Illapel 1880: Mw 7.5 in the paper (Cabello 8.10) |
| overrides.csv | 234 | mag | 7.8 | Copiapo 1918: Mw 7.8 in the paper (Cabello 8.00) |
| overrides.csv | 356 | mag | 7.7 | Talca 1928: Mw 7.7 in the paper (Cabello 8.10) |
| overrides.csv | 552 | mag | 7.8 | Chillan 1939: Mw 7.8 in the paper (Cabello 8.00) |
| overrides.csv | 608 | mag | 7.9 | Illapel 1943: Mw 7.9 in the paper (Cabello 8.20) |
| overrides.csv | 631 | mag | 7.1 | Santiago 1945: Mw 7.1 in the paper (Cabello 7.00) |
| overrides.csv | 835 | mag | 6.3 | Las Melosas 1958: Mw 6.3 in the paper (Cabello 6.80) |
| overrides.csv | 2370 | mag | 7.4 | Tocopilla 1967: Mw 7.4 in the paper (Cabello 7.50) |
| overrides.csv | 3289 | mag | 7.8 | La Ligua 1971: Mw 7.8 in the paper (Cabello 7.50) |
| overrides.csv | 4704 | mag | 7.7 | Arauco 1975: Mw 7.7 in the paper (Cabello 7.80) |
| overrides.csv | 6353 | mag | 7.2 | Papudo 1981: Mw 7.2 in the paper (Cabello 7.50) |
| overrides.csv | 6854 | mag | 7.7 | Copiapo 1983: Mw 7.7 in the paper (Cabello 7.20) |
| overrides.csv | 7282 | mag | 8.0 | Valparaiso 1985: Mw 8.0 in the paper (Cabello 7.90) |
| overrides.csv | 8464 | mag | 7.6 | Antofagasta 1987: Mw 7.6 in the paper (Cabello 7.20) |
| overrides.csv | 36911 | mag | 7.0 | Papudo 2001: Mw 7.0 in the paper (Cabello 6.70) |
| overrides.csv | 52159 | mag | 6.4 | Curico 2004: Mw 6.4 in the paper (Cabello 6.50) |
| overrides.csv | 69130 | mag | 7.8 | Tocopilla 2007: Mw 7.8 in the paper (Cabello 7.70) |
| overrides.csv | 110688 | mag | 7.2 | Constitucion 2012: Mw 7.2 in the paper (Cabello 7.10) |
| overrides.csv | 145193 | mag | 8.3 | Illapel 2015: Mw 8.3 in the paper (Cabello 8.40) |
| overrides.csv | add:pichilemu2010a | mag | 6.9 | Pichilemu 2010 first event: Mw 6.9 in the paper (GCMT 6.88) |
| class_overrides.csv | 157950 | class | slab_interface | Chiloe 2016: deep interface patch (domain C), not intraslab |
| class_overrides.csv | 24 | class | intra_slab | Santiago 1647: historical intraslab, most probable of its type (section 7.4) |
| class_overrides.csv | 160 | class | slab_interface | Illapel 1880: interplate; deep submarine cable break off Limari (section 5.4.1); Cabello e |
| class_overrides.csv | 1987 | class | slab_interface | Taltal 1966: thrust on the plate interface (Deschamps et al. 1980; Table 1 domain B) |
| class_overrides.csv | 3289 | class | slab_interface | La Ligua 1971: interplate near the bottom of the contact zone (Table 1 domain C) |
| class_overrides.csv | 4704 | class | slab_interface | Arauco 1975: interplate, domain C (Table 1; paper gives 14 Oct 1975, event is 10 May 1975) |
| class_overrides.csv | 8464 | class | slab_interface | Antofagasta 1987: interplate at the southern end of the 1995 rupture (section 4.2); GCMT t |
| class_overrides.csv | 9347 | class | slab_deep | Arica 1987: intraplate intermediate depth (Fig. 4); catalog depth 19 km is wrong |
| class_overrides.csv | 70065 | class | intra_slab | Michilla 2007: intraplate intermediate depth (Fig. 4; Ruiz and Madariaga 2011) |
| class_overrides.csv | 110688 | class | slab_interface | Constitucion 2012: interplate near the bottom of the seismogenic contact (Table 1 domain C |
| class_overrides.csv | 678 | class | patagonia_crustal | Tierra del Fuego 1949 M8.0: Magallanes-Fagnano transform, 240 km from the Antarctic trench |
| class_overrides.csv | 159 | class | patagonia_crustal | Magallanes 1879 M7.2: Magallanes-Fagnano fault system, 350 km from the trench; no depth |
| class_overrides.csv | 3030 | class | patagonia_crustal | Tierra del Fuego 1970-06-15 M6.8 (54.5 S 64.5 W): eastern Magallanes-Fagnano segment, 380  |
| class_overrides.csv | 196 | class | patagonia_crustal | Magallanes 1907 M5.5: same fault system as 1879, no depth |
| additions.csv | add:pichilemu2010a | event | 6.88 | Pichilemu doublet, first event (Mw 6.9, normal faulting in the upper plate); missing in Ca |

## Changes after 29 Sep 2026

- North limit: Cabello rows north of 17 S dropped before anything else (7,937 rows; DECISIONS 2).
- Crustal depth cap 30 km and unknown depths to the slab family; the neighbour vote removed (DECISIONS 18, 21, 22, 33, 34).
  Against the catalog of 29 Sep (`catalog_v1.csv`, 50195 events in both): 3499 events changed class (335 at M >= 5.5, 18 at M >= 7). By cause: unknown depth 2382; real depth > 30 km 1079; other 38.

| old class -> new class | all | M >= 5.5 | M >= 7 |
|---|---|---|---|
| slab_deep -> unresolved | 1198 | 83 | 4 |
| backarc -> unresolved | 756 | 108 | 3 |
| deep_nest -> unresolved | 359 | 6 | 0 |
| intraarc -> unresolved | 356 | 37 | 3 |
| forearc -> unresolved | 320 | 33 | 1 |
| intraarc -> slab_deep | 95 | 16 | 3 |
| patagonia_crustal -> unresolved | 58 | 7 | 1 |
| intra_slab -> slab_interface | 50 | 4 | 0 |
| deep_nest -> slab_deep | 45 | 1 | 0 |
| slab_deep -> deep_unknown | 43 | 0 | 0 |
| deep_unknown -> unresolved | 40 | 1 | 0 |
| slab_deep -> deep_nest | 39 | 0 | 0 |
| forearc -> slab_interface | 32 | 11 | 3 |
| forearc -> intra_slab | 29 | 15 | 0 |
| intra_slab -> unresolved | 8 | 1 | 0 |

## Open

- In-slab Mmax: Santiago 1647 M8.4 is now the largest in-slab event; whether historical events count for Mmax is a source-model decision (DECISIONS 31).
- Cabello magnitudes are agency-dependent; ISC-only events about 0.3 low (DECISIONS 32).
- Historical M >= 7 still unresolved: 1687, 1850, 1870 (DECISIONS 29); paper events absent from Cabello (DECISIONS 30).
- Crustal events deeper than 30 km kept by hand: 5 (`crustal_exceptions.csv`, DECISIONS 34); events above the deep slab between 30 and 70 km are unresolved (rule deep_mid, lever FOREARC_MAX_Z).

## Figures (results/cat_handler_2/slides/)

- `01_pipeline.png`: the two steps of the catalog build, sources to catalog_base to catalog, with the counts at each stage.
- `02_duplicates.png`: share of Cabello rows that duplicate another agency's row, by magnitude; what the merged groups are made of.
- `03_depth_status.png`: depth histogram as read (dotted: the agency default depths) and after relocation and filling, by depth status.
- `04_magnitudes.png`: Cabello's Mw of the CSN, USGS and ISC rows against the GCMT Mw of the same earthquake, with the median offsets.
- `05_mechanisms.png`: share of events with a focal mechanism by source and magnitude; beachballs of the M >= 6 events.
- `06_map_families.png`: the four source families in map view, M >= 5.5 enlarged, with the cities and both trenches.
- `07_map_decisions.png`: the hand decisions (class, magnitude, row fixes) and the unresolved events, which enter no family.
- `08_counts_old_new.png`: events per family and magnitude bin, campaign catalog (rows and deduplicated) against the new catalog.
- `09_moves.png`: family moves of the same events at M >= 5.5 between the campaign and the new classification, with the deciding rules.
- `10_mt_family.png`: magnitude against time per family since 1900, coloured by depth status.
- `11_large_events.png`: the M >= 7 events by class through time; rings mark agreement with Ruiz and Madariaga (2018).
- `12_patagonia.png`: south of the triple junction: Antarctic trench, the 150 km interface footprint and the Patagonian classes, in map and section.
- `sections/secNN_<lat>S.png`: the 23 transects of sections.pdf, one PNG each, with their locator map.
- `sections_slide/secNN_<lat>S.png`: slide version of every transect (23): M >= 5.5, the cities of the section at the surface, M >= 7 named; `_all` for backup.
