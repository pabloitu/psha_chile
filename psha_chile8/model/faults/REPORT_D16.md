# D16: crustal fault database, faults missing from GEM, Magallanes–Fagnano

15 Nov 2026. Code in `model/faults/` (`db.py`, `chaf.py`, `fagnano.py`, `figs.py`, `geo.py`), tests in `model/faults/tests/` (11 pass). The database is `data/faults/faults_2026-11-15.gpkg` and `.csv`, with its fields in `FIELDS.md`. Tables are in `tables/` and figures in `figs/`. The inputs are frozen in `data/` with dated names and sha256 sums (rows in `DATA.md`).

A short guide for readers who are not fault-database specialists:
- A *segment* is one mapped line (trace) with its attributes.
- A *strand* in CHAF is the same thing, at a finer scale (often 1–10 km).
- A *slip rate* is how fast the two sides of a fault move past each other, averaged over many earthquakes. With the fault area it sets the moment rate, and so the earthquake rate the model gives the fault.

## Final fault file (GEM, for B13 and the model)

**`data/faults/faults_gem_extra_2026-11-15.shp`** (and `.csv`, same rows without geometry), EPSG:4326, **138 faults**, fields as in `model/faults/FIELDS.md`. Built by `model/faults/curate.py` from Pablo's second hand edit, frozen untouched as `data/faults/faults_gem_extra_pablo_2026-11-15b.*`. The first edit, `…_pablo_2026-11-15.*`, is kept for the record.

Contents:
- **130 GEM SARA segments** (93 Chilean, 27 Argentine, 10 Peruvian), cleaned as in section 1.
  - 13 GEM segments removed by Pablo in the first edit: Chuculay CL-044a, b, e, f; Ordoñez CL-051; Mititus CL-050; Bolfín CL-040; Los Palos CL-006mmm; Punta Colas CL-006eee; Las Peñas AR-0028a; PE-43a; PE-38; PE-47.
  - 6 Magallanes–Fagnano strands beside the main trace removed (Pablo): CL-056e, f, g, h, i, j (`REMOVE` in `curate.py`).
  - 7 far Argentine faults removed in the second edit: Aconquija AR-0002a, El Molino AR-0050a, El Duraznillo AR-0268a, Chumbicha AR-0005a, Las Lagunas AR-0054a, Medeiros AR-0350a, Las Malvinas AR-0045b.
  - Río Cuervo CL-006ddd: trace edited (80.7 → 65.1 km).
  - San Ramón CL-001a: trace swapped to MASCSN26 fault 687 (28.2 → 44.4 km, all proved CHAF strands); A's attributes kept (47.5° E, 0.4 mm/yr, our depth rule) (Pablo, 17 Nov; `SWAP` in `curate.py`).
- **4 faults added by hand earlier**, traced to CHAF: Bajo Molle; Marga Marga and Laguna Verde, both extended to all their CHAF strands (34.6 and 23.4 km); Carranza.
- **4 faults added from CHAF in D16**:
  - Mejillones, northern section (19.7 km after Pablo's edit; the southern Mejillones fault is GEM CL-049)
  - Valparaíso (33.2 km after Pablo's edit)
  - Quintay (47.9 km)
  - Santa María (11.1 km, the CHAF reverse strand)
  - All four with dip 72°, 0–20 km and 0.5 mm/yr, as the similar GEM forearc faults.
- **Magallanes–Fagnano:** one main trace, 7 segments, 490 km.
  - The segments are CL-056b, c, d and AR-0056a, b, d, g. AR-0056a is cut at the border (territory rule, 174 → 55 km).
  - The parallel strands were removed, because the GPS rate is the motion of the whole zone and each extra strand would count it again.
  - Slip rate 5.9 (4.4–6.8) mm/yr from GPS.
  - The segments stay separate, as mapped. The model (B13) joins them end to end into one system source, bridging the gap of about 60 km between CL-056b and CL-056c (Almirantazgo Sound, 70.96–69.93° W).
  - Mmax of the system source: Leonard 2014 gives 7.98 on the sum of the traces (9 792 km²) and 8.00 on the end-to-end length (517 km); WC94 gives 8.05–8.07.
  - These replace the 8.1 and the rates of section 3, which used all 13 traces (639 km). With the main trace, the one-source rates are N(≥ 6.5) 0.019–0.021 and N(≥ 7) 0.006 per year.
- Total trace length 5 854 km. Slip rates: 114 class, 12 range, 12 measured (including the 7 Fagnano segments).

Rebuild: `python db.py` (only if an input changes), then `python curate.py`, from `model/faults/`. `db.py` does not write this file, so a rerun cannot overwrite the edit. The other outputs are intermediate: `faults_2026-11-15.gpkg` / `.csv` (the full clean database before Pablo's edit, 164 rows) and `faults_gem_2026-11-15.shp` (GEM rows only, before the edit).

## 1. What changed in the database

**Where the old file came from.** `crustal_faults_chile_updated` has 160 rows:
- 156 are segments of the GEM SARA release (CL-, AR- and PE- IDs; 108 Chilean, 35 Argentine, 13 Peruvian). They are identical to the release, attribute by attribute and vertex by vertex.
- 4 were added by hand: Bajo Molle, Marga Marga, Laguna Verde, Carranza.

So the seven area-source columns (`id_area`, `min_mag`, `max_mag`, `a_val`, `b_val`, `usd`, `lsd`) were not added in Chile. They come with GEM's own release: 407 of its 437 rows carry them.

The 13 rows with `max_mag` 0 are also in the release. They are the nine CL-056 and the four AR-0056 Magallanes–Fagnano segments, which lie in no GEM area source. They are not hand rows.

**Columns.** The new file keeps only properties of the faults. Every value has a source column (`kin_src`, `dip_src`, `sr_src`, `z_src`, `sys_src`, `src`, `src_ref`).

Removed:
- the seven area-source fields
- `ogc_fid` and `id_sys`, which is empty
- `downt_side`, which is empty in every row
- `len_st` and `length_km`
- `az_tr`

Changes from the proposed schema:
- `gem_flt` added (the GEM fault ID, which groups segments).
- `vertical` added.
- `dip_txt` and `sr_txt` added: the text as given by the source.
- `dup_of` added: the duplicate flag.
- One source column per field, filled for every row.
- `sr_kind` has a third value, `range`. This is a range given by the source that is not one of GEM's activity classes, such as "0.02–0.5" in the Argentine rows. It is neither a measurement nor a class.

**Rows: 160, none removed.** There are no exact duplicates.

| change | rows | rule |
|---|---|---|
| area-source fields removed | 160 | — |
| IDs | 4 | Each hand row gets `CHAF-<F_id>` of the CHAF strand that covers most of its trace. All four lie on CHAF strands over their whole length (`tables/d16_hand_rows_2026-11-15.csv`). So all four are traced: Bajo Molle → CHAF 100601 "Bajo Molle / Los Pacos", Marga Marga → 300201, Laguna Verde → 300301, Carranza → 300901. No row is left untraced. |
| dip | 124 | The number in the SARA dip text, or the midpoint of a range given there. For open classes (">60", "<45"), the value GEM gives them (72, 37). <br>89 segments: "90" / "90." becomes 90° (GEM had 87°). <br>35 segments: GEM's class value becomes the stated number or midpoint (for example "80" 72 → 80; "45" 52 → 45; "30-45" 37 → 37.5). <br>San Ramón: "40-55" was 37°, outside its own range; now 47.5°. |
| kinematics | 3 | AR-0236l: reverse, from the segments of the same GEM fault with the same dip class. <br>AR-0005a: no source, set to reverse (assumed; the old default rake). <br>Carranza: normal, from CHAF. |
| length | 0 | Recomputed on WGS84. All 156 GEM rows agree with GEM's `len_st` within 1 %. <br>The hand rows had wrong lengths: Bajo Molle 19 → 8.3 km, Marga Marga 10 → 8.3, Laguna Verde 8 → 6.7, Carranza 39 → 36.5. |
| system | 113 of 160 | Rules in order: <br>1. the GEM fault ID: CL-006 = Liquiñe–Ofqui, CL-056 / AR-0056 = Magallanes–Fagnano (63 rows) <br>2. the GEM name "Sistema / Zona / Grupo de fallas X" (7 rows) <br>3. the CHAF system of the matched strands (43 rows) <br>47 stay empty: Peruvian and Argentine segments, and 17 Chilean segments with no CHAF strand on them (below). |
| sr_kind | 160 | class 140, range 15, measured 5 |
| duplicates flagged | 4 | Within 2 km over more than half of the shorter trace: CL-044a / CL-044b (50 %), CL-006bbb / CL-006ddd (50 %), PE-42b / PE-42c2 (51 %), PE-51b / PE-51a (100 %). <br>The first three are adjacent or branching segments just over the limit. PE-51b lies entirely on PE-51a and is a true duplicate. <br>Nothing is deleted. |
| note | 1 | CL-027: the dip direction S lies within 28° of the trace azimuth. |

**Slip rates.** Almost the whole database carries a class value, not a measured rate.

| sr_kind | segments | km of trace | values |
|---|---|---|---|
| class (GEM activity class; `sr` its representative value) | 140 | 5 905 | "0.1–1" → 0.5 mm/yr (86); "1–5" → 3.0 (53); "0.01–0.1" → 0.055 (1) |
| range (source range, `sr` its midpoint) | 15 | 423 | Argentine segments: 0.02–0.5 (6), 0.1–2 (2), 0.2–1, 0.5–1, 0.5–2, 1–2, 0.1–0.5, 0.01–0.5; Marga Marga 0.4–0.6 (hand row, value not in CHAF, origin unknown) |
| measured | 5 | 130 | San Ramón 0.4 (SARA); Las Tapias–Villicum 0.8 (SARA); Bajo Molle 0.4 (0.3–0.5; CHAF 0.4 ± 0.1, Allmendinger et al. 2009, González et al. 2015); Laguna Verde 0.7 (CHAF, Valdivia et al. 2017); Carranza 0.4 (a CHAF *throw* rate, Jara-Muñoz et al. 2015; as slip on a 60° normal fault, 0.46) |

All 50 Liquiñe–Ofqui segments carry 3.0 (class "1–5") or 0.5. The literature gives much more for the master fault:
- 18.8 ± 2.0 mm/yr Holocene at Liquiñe (Astudillo-Sotomayor et al. 2021, p. 1, p. 7)
- 11.6–24.6 mm/yr south of 45° S (De Pascale et al. 2021, Table 1)
- 6.5 mm/yr forearc-sliver GPS rate (Wang et al. 2007)

That is outside D16, but it is the largest open question about the slip rates.

**Depths.** SARA gives 0–20 km for all 156 rows, a uniform default; the hand rows give 15 or 18 km. They are kept as given. The model uses its own 10 / 20 km (DECISIONS).

## 2. The important faults missing from GEM

**Matching.** A CHAF strand matches a GEM segment if more than half of its length lies within the distance of the GEM trace (`tables/match_2026-11-15.csv`):

| distance | strands matched (of 958) | km matched (of 9 014) | proved | probable | possible | GEM segments hit |
|---|---|---|---|---|---|---|
| 1 km | 274 | 2 762 | 27 of 78 | 232 of 592 | 15 of 288 | 75 |
| **2 km (rule)** | **374** | **3 575 (40 %)** | 28 | 318 | 28 | 82 |
| 5 km | 535 | 5 085 (56 %) | 32 | 425 | 78 | 84 |

The result moves with the distance because GEM traces are drawn at a coarser scale than CHAF (1:25 000 to 1:500 000). Going from 2 to 5 km adds mostly probable and possible strands next to the Liquiñe–Ofqui and Atacama traces.

**System against system (2 km; `tables/systems_2026-11-15.csv`).**
- **Partly in GEM:** Atacama (68 % of the CHAF length), Liquiñe–Ofqui (58 %), Liquiñe–Ofqui Transverse (37 %), Central Coastal Forearc (34 %), East–West (30 %), Western Andean Thrust Front (13 %), Lanalhue (12 %).
- **Absent from GEM:** Lago Laja, Santa María, Los Vilos–Puerto Aldea, South-Central Coastal Forearc, Cordillera de la Sal, Salar de Atacama, Caldera, Cachet, Central Andean and Exploradores. That is 10 of the 17 systems and about 1 900 km of CHAF trace.

The reverse also holds: GEM has faults that CHAF lacks. Inside the CHAF latitudes, 27 GEM segments (1 007 km) have no system and only 78 km of them lie on a CHAF strand. Most are the NW-striking faults of the arc between 39° and 43° S: Huequi, Chacao, Fiordo Reñihue, Chaitén, Lago Yelcho, Calbuco–Reloncaví, Riñihue–Choshuenco, Villarrica–Quetrupillán–Lanín, Sollipulli–Icalma, Callaqui, Futrono and others. All are class 0.5 mm/yr. CHAF does not map them as active.

**San Ramón is not missing.** All proved and probable CHAF strands of the Western Andean Thrust Front near Santiago (25 strands, 39 km) lie within 2 km of GEM's single segment "San Ramon 01a" (28 km). The CHAF WATF strands left unmatched are possible-class faults south of Santiago: Cachapoal, Machalí, Cariño Botado and others.

**Missing faults.** The 584 unmatched strands join into 146 faults: strands of one system less than 5 km apart. Of these, 7 contain proved strands, 68 probable and 71 possible (`tables/missing_2026-11-15.csv`). For each fault the table gives:
- length (end-to-end span of its strands)
- Mw of a full rupture of that length and 20 km width, from Wells and Coppersmith (1994) and Leonard (2014), as implemented in OpenQuake, with the rake of the main CHAF sense
- distance to every city, and to Santiago, Valparaíso and Concepción
- crustal events of the frozen catalogue nearby (crustal weight ≥ 0.5, Mw ≥ 5.5, within 10 km)
- CHAF slip or throw rates and references

**Ranking.** First by activity class (proved, probable, possible). Within a class, by one number: the median PGA at the most-affected of the 14 cities from a full rupture. This uses BSSA14 (one of the four crustal GMMs of DECISIONS), Vs30 800 m/s, the Leonard Mw, and the Joyner–Boore distance taken as the distance to the trace. It combines magnitude and distance without a free weight. It is a ranking device only; slip rate, and so frequency, is not in it.

| rank | fault (CHAF names) | system | class | length km | Mw WC94 / Leonard | nearest city | PGA g | crustal events within 10 km |
|---|---|---|---|---|---|---|---|---|
| 1 | Mejillones | Atacama | proved | 45 | 6.9 / 7.0 | Antofagasta 62 km | 0.04 | – |
| 2 | Pisagua | East–West | proved | 13 | 6.5 / 6.4 | Iquique 75 km | 0.03 | – |
| 3 | Aroma | not assigned | proved | 17 | 6.6 / 6.5 | Iquique 106 km | 0.02 | 2001-07-24 Mw 6.3; 2002-01-14 Mw 5.6 |
| 4 | Garcés / Tinguiririca / Guanaco | Central Andean | proved | 34 | 6.9 / 6.8 | Santiago 148 km | 0.01 | – |
| 5 | Lago Laja | Lago Laja | proved | 48 | 7.0 / 7.0 | Concepción 156 km | 0.01 | – |
| 6 | Pichilemu | Central Coastal Forearc | proved | 15 | 6.5 / 6.5 | Valparaíso 152 km | 0.01 | 2010-03-11 Mw 6.9; two Mw 5.6–5.7 |
| 7 | El Yolki | Central Coastal Forearc | proved | 14 | 6.4 / 6.4 | Concepción 162 km | 0.01 | – |
| 8 | Tarapacá / Zofri | East–West | probable | 42 | 7.0 / 6.9 | Iquique 2 km | 0.39 | – |
| 9 | Valparaíso / Quintay / Laguna Verde | Central Coastal Forearc | probable | 52 | 7.0 / 7.0 | Valparaíso 1 km | 0.35 | – |
| 10 | Caburgua | Liquiñe–Ofqui | probable | 23 | 6.7 / 6.7 | Pucón 8 km | 0.24 | – |
| 11 | unnamed, 42.4° S 72.5° W | Liquiñe–Ofqui | probable | 69 | 7.1 / 7.1 | Hornopirén 13 km | 0.21 | – |
| 12 | Río Blanco / Los Palos | Liquiñe–Ofqui | probable | 37 | 6.9 / 6.9 | Puerto Aysén 11 km | 0.20 | 1991-08-15 Mw 5.9 |
| 13 | Marga-Marga | Central Coastal Forearc | probable | 26 | 6.7 / 6.7 | Valparaíso 12 km | 0.15 | – |
| 14 | Lago Cabrera | Liquiñe–Ofqui | probable | 10 | 6.3 / 6.3 | Hornopirén 11 km | 0.14 | – |
| 15 | Salar del Carmen (side strand) | Atacama | probable | 6 | 6.0 / 6.0 | Antofagasta 10 km | 0.14 | – |
| 16 | Cerro Mollecillo | Atacama | probable | 3 | 6.0 / 5.8 | Iquique 12 km | 0.14 | – |
| 17 | Maihue / Los Guindos | Liquiñe–Ofqui | probable | 98 | 7.3 / 7.3 | Pucón 25 km | 0.11 | – |
| 18 | unnamed, 41.4° S 72.3° W | Liquiñe–Ofqui | probable | 58 | 7.1 / 7.1 | Hornopirén 30 km | 0.11 | – |
| 19 | unnamed, 39.1° S 71.7° W | Liquiñe–Ofqui Transverse | probable | 22 | 6.7 / 6.6 | Pucón 26 km | 0.10 | – |
| 20 | Paposo | Atacama | probable | 32 | 6.8 / 6.8 | Antofagasta 21 km | 0.10 | 1977-06-05 Mw 5.9; 1989-05-29 Mw 5.5 |

Notes on the list:
- **A fault takes the highest class of its strands.** Rank 4 is proved only through one 6.6 km El Fierro strand; the other 55 km of the group are possible.
- **Proved first.** Because the class comes first, seven proved faults of 13–48 km rank above probable faults beside Iquique and Valparaíso, although the proved ones are 60–160 km from any city. Ranked by PGA alone, the top five would be: Tarapacá / Zofri, Valparaíso / Quintay / Laguna Verde, two possible-class strands near Puerto Aysén, and Caburgua.
- **Salar del Carmen** is in GEM as CL-046 (256 km, the Atacama "segmento Salar del Carmen"). Only a 6 km side strand is unmatched.
- **Mejillones.** GEM has a 36 km "Mejillones" segment (CL-049) on the western side of the peninsula. The proved CHAF Mejillones system (28 strands, 45 km) lies more than 2 km from it.

The checked candidates by name:
- In GEM: San Ramón, Salar del Carmen, most of the Atacama system, and the Liquiñe–Ofqui master fault.
- Missing: Pichilemu (rank 6), El Yolki (7), the Mejillones system (1), Marga-Marga (13; the GEM file has an 8 km hand row on part of it), the Liquiñe branches (ranks 10–12, 14, 17–19), Lanalhue (CHAF 369 km, 12 % on GEM's Lanalhue 004b; ranks 37–38) and Santa María (ranks 24, 26; a blind splay fault offshore Arauco).
- West Andean Thrust: only its San Ramón segment is mapped as active in either database.

**Literature for the top 20.** Read in full unless marked. Sources were read by literature agents of this session from the publisher or open-access PDFs; page, paragraph or table given.

| rank | fault | slip rate | palaeoseismic or event evidence | source (read in full unless marked) |
|---|---|---|---|---|
| 1 | Mejillones | 0.61 ± 0.26 m/ka over 35–3.3 ka; 0.22 ± 0.06 m/ka since 3.3 ka | first upper-plate palaeoseismic study in Chile: two Mw ~7 events, recurrence 5.0 ± 3.5 ka, last Mw ~6.6 at ca. 3.5 ka; fault 36–40 km | Cortés A. et al. 2012, Tectonics 31, TC2017, doi 10.1029/2011TC002877, abstract [1], [9], §9.4 [49]–[52] |
| 2 | Pisagua | none found | CHAF says "OSL ages suggest an earthquake in the past 10 ka", but the source (Santibáñez et al. 2019) gives that result for Bajo Molle; probably a CHAF copy error | González et al. 2015, Geology, doi 10.1130/G36703.1 (not read, paywalled) |
| 3 | Aroma | none for the fault; 0.02 mm/yr uplift across three flexures since 8 Ma (Farías et al. 2005, abstract only) | 2001 Mw 6.3 at 5 km depth, no surface rupture (Legrand et al. 2007, via Santibáñez et al. 2019 §4.1; CHAF writes 2011) | Santibáñez et al. 2019, Andean Geol. 46:32–65 |
| 4 | Garcés / Tinguiririca / Guanaco (with El Fierro) | none found | proved only through a 6.6 km El Fierro strand that CHAF ties to the 2004 Mw 6.4 earthquake; the other 55 km are possible; the 1958 Las Melosas events lie near 33.8° S, not here | Giambiagi et al. 2019 (only CHAF reference; not read) |
| 5 | Lago Laja | Holocene minimum vertical rates: 0.68 ± 0.37 mm/yr averaged over the fault groups, 0.50 ± 0.02 on the northern main fault, > 0.77 lake-floor scarps; E–W extension 1.2 ± 0.6 mm/yr | Holocene surface ruptures; seismites > 2 m in late-Pleistocene lake beds; "M > 6" qualitative | Melnick et al. 2006, Tectonics 25, TC5004, doi 10.1029/2005TC001918, Table 2 p. 16, [20], [25], [42], [45] |
| 6 | Pichilemu | 0.52 ± 0.04 mm/yr over about 500 ka (terrace model) | blind fault; 2010 Mw 6.9 and 7.0 events, 1.1 m slip; recurrence 2.12 ka (1.85–2.28) for Mw 6.7–7.0 | Jara-Muñoz et al. 2022, Nat. Commun. 13:3371, doi 10.1038/s41467-022-30754-1, p. 1, 5–8 |
| 7 | El Yolki | Holocene throw about 2 mm/yr; slip 5–6 mm/yr from dislocation models (5.6 and 5.9) | 10 m vertical offset of 4.3–4.0 ka sediments; a cluster of slip events at 4.3–4.0 ka; no Mw | Melnick et al. 2019, JGR 124:7280–7302, doi 10.1029/2018JB017188, §2.2, §4.3, §6 |
| 8 | Tarapacá / Zofri | none found | none found | García-Pérez et al. 2018 (abstract only); Sepúlveda and Quezada 2015 (congress abstract, not found) |
| 9 | Valparaíso / Quintay / Laguna Verde | Laguna Verde 0.7 mm/yr (terrace heights; no uncertainty); Quintay, Valparaíso none | none | Valdivia et al. 2017, AGU Fall Meeting abstract (an abstract only) |
| 10 | Caburgua | none from geology; models give up to 1.4 mm/yr on NW-striking transverse faults (Stanton-Yonge et al. 2016) | 2014 swarm defines a 20 km left-lateral transpressional fault at 1–10 km depth | Sielfeld et al. 2019, Tectonics 38:552–578, doi 10.1029/2018TC004985, manuscript p. 16, 25 |
| 11 | unnamed, 42.4° S | none found | none | — |
| 12 | Río Blanco / Los Palos | none for these faults | Los Palos dextral, recent activity in sub-bottom profiles; Mw 6.2–6.5 for most Aysén strands by scaling, 7.1 for the master faults; 2007 Aysén Mw 6.2 on the nearby Punta Cola fault | Vargas et al. 2013, Andean Geol. 40:141–171, doi 10.5027/andgeoV40n1-a07, p. 152, 154, 166–167 |
| 13 | Marga-Marga | none found | none | Muñoz et al. 2012, congress abstract (not found) |
| 14 | Lago Cabrera | none for the fault; Liquiñe–Ofqui 32 ± 6 mm/yr at 40–42° S over 4 Ma (Rosenau et al. 2006) | none | Rosenau et al. 2006, Tectonics 25, TC4013, abstract [1], [28] |
| 15 | Salar del Carmen (side strand) | main fault 0.06 ± 0.02 m/kyr | three events at 100, 78 and 59 ka, Mw 6.9–7.0, recurrence 35 ± 12 kyr; rupture about 42 km | González et al. 2025, Sci. Rep. 15:2914, doi 10.1038/s41598-025-86877-0, p. 1, 6, 11 |
| 16 | Cerro Mollecillo | none found | none | — |
| 17 | Maihue / Los Guindos | none for these strands; Liquiñe 18.8 ± 2.0 mm/yr Holocene | scenario only: Liquiñe + Los Guindos about 100 km, Mw ~7.0 every ~150 yr, not supported by the record (the authors) | Astudillo-Sotomayor et al. 2021, Sci. Rep. 11:5970, doi 10.1038/s41598-021-85036-5, p. 1, 7 |
| 18 | unnamed, 41.4° S | none found | none | — |
| 19 | unnamed, 39.1° S (Liquiñe–Ofqui Transverse) | none; models ≤ 1.4 mm/yr on transverse faults | none | Stanton-Yonge et al. 2016, Tectonics 35, doi 10.1002/2016TC004226 (abstract) |
| 20 | Paposo | none Quaternary (Miocene normal motion only) | none | Allmendinger and González 2010 (not read) |

Seven of the twenty have a fault-specific rate or palaeoseismic record: Mejillones, Lago Laja, Pichilemu, El Yolki, Laguna Verde, Caburgua (a swarm only) and Salar del Carmen. The other thirteen have none that we could find. Also checked by name: San Ramón (in GEM) has one trench with two events in 17–19 ka, the last about 8 ka, Mw 7.2–7.5 (Vargas et al. 2014, Geology 42:1083–1086, doi 10.1130/G35741.1, p. 1085–1086) and 0.1–0.5 mm/yr (Armijo et al. 2010, p. 17–18; Estay et al. 2016). Santa María: a blind reverse splay, 3.0–3.7 m/ka, reactivated in 2010 (Jara-Muñoz et al. 2017, JGR 122:4529–4558, doi 10.1002/2016JB013339). Lanalhue: no Quaternary rate in any source read (Melnick et al. 2009; Glodny et al. 2008 and Haberland et al. 2006 not read).

**What adding the top faults could change (estimate only, nothing added).** A missing fault would need a slip-rate rule. The obvious one is the median slip rate of the GEM segments of the same system: 3.0 mm/yr for Liquiñe–Ofqui, 0.5 for the others; the class value 0.5 where the system has no GEM segment.

With that rule and a 20 km width, the top 20 add about 10 % to the moment rate of all GEM faults (`tables/added_moment_2026-11-15.csv`):

| region | added moment rate |
|---|---|
| north of 27° S | +13 % |
| 27–38° S | +5 % |
| south of 38° S | +11 % (nearly all from the five Liquiñe–Ofqui faults) |

The hazard effect is more local than these totals:
- Tarapacá / Zofri runs under Iquique, the Valparaíso / Laguna Verde system under Valparaíso, Caburgua 8 km from Pucón, and two Liquiñe–Ofqui branches 11–13 km from Hornopirén and Puerto Aysén.
- At these cities a fault of Mw 6.7–7.0 a few km away gives a median PGA of 0.2–0.4 g by itself. So the PGA 475 yr could change by more than the 5 % branch rule even at 0.5 mm/yr.
- The faults are not in the buffers where the background is capped at Mw 6, so adding them would also move the background cap.

The slip rates of the rule are the weak point:
- At Liquiñe the measured 18.8 mm/yr is six times the 3.0 of the rule.
- Mejillones has 0.6 mm/yr measured, against 0.5 in the rule.
- Pichilemu has 0.52 mm/yr, against 0.5.

## 3. Magallanes–Fagnano

**Segments.** The clean database has 13 segments: CL-056b–j (Chilean database, "Falla Lago Fagnano, sección occidental", sinistral-normal, 503 km) and AR-0056a, b, d, g ("Sistema de fallas Fagnano", sinistral, 256 km). All have the class value 3.0 mm/yr, dip 90° and 0–20 km depth (`tables/fagnano_segments_2026-11-15.csv`, `figs/fagnano_segments.png`).

The SARA release has no other segment of the system. The gaps in its IDs (AR-0056c, e and f; `ogc_fid` 165, 168, 169) show that GEM dropped three Argentine segments before release; their traces cannot be recovered from these files. CHAF ends at 47.8° S.

**Overlap.** AR-0056a (174 km) starts at 70.25° W, well inside Chile, and runs through Lago Fagnano beside four Chilean segments. Within 5 km (`tables/fagnano_overlap_2026-11-15.csv`):

| pair | km of the Chilean segment on the Argentine trace | share | median gap |
|---|---|---|---|
| CL-056c / AR-0056a | 44 of 85 | 51 % | 1.5 km |
| CL-056i / AR-0056a | 25 of 25 | 100 % | 3.4 km |
| CL-056e / AR-0056a | 11 of 39 | 27 % | 4.5 km |
| CL-056d / AR-0056a | 10 of 44 | 22 % | 2.5 km |

In all, 75–90 km of the system is mapped twice, all west of the border (69.0–70.0° W).

**One trace per section, proposed rule.** Each national database is kept inside its own country: Chilean segments west of the border (68° 36′ 38″ W in Tierra del Fuego), Argentine segments east of it. Each country maps its own territory in more detail and from field work there. The rule cuts AR-0056a at the border (174 → 55 km) and leaves every other segment whole. The system then has 639 km of trace and no section twice.

The alternative, "keep the more detailed trace" (vertices per km), fails here:
- AR-0056a (0.7 vertices per 10 km) is more detailed than CL-056c (0.5) but less than CL-056i (1.6).
- So the rule drops CL-056c and still keeps the 25 km of CL-056i twice (673 km).

The Chilean traces themselves are coarse. CL-056b, 224 km along the Magellan Strait and Almirantazgo Sound, has a vertex every 25 km.

**Slip rate from GPS.** All geodetic networks lie east of about 68.6° W, in Argentina; no GPS rate exists for the Chilean part (Vassallo et al. 2024, p. 333).

| study | what | rate (mm/yr) | where | read |
|---|---|---|---|---|
| Mendoza et al. 2015, Tectonophysics 651–652:58–65, doi 10.1016/j.tecto.2015.03.013 | block model, 48 sites, rate on the fault, preferred model 2c (dip 66° S, locking depth 11 ± 5 km) | 6.0 / 5.9 / 5.8 ± 0.2 on three segments, Irigoyen to western Lago Fagnano; vertical-fault models 6.5–6.8 (Model 1) and 5.4–5.6 (Model 1c) | Table 3, p. 64; abstract p. 58 | in full |
| Mendoza et al. 2011, GJI 184:1009–1022, doi 10.1111/j.1365-246X.2010.04912.x | difference between two rigid zones, the full relative motion across a 30 km belt | 4.4 ± 1.1 E (2σ), −0.3 ± 0.8 N | p. 1018, Table 6 p. 1019 | in full |
| Smalley et al. 2003, G-cubed 4:1070, doi 10.1029/2002GC000446 | elastic model, vertical fault, assumed 15 km locking depth | 6.6 ± 1.3 | abstract | abstract only |
| Mendoza et al. 2022, Tectonics 41, doi 10.1029/2021TC006801 | 24 yr GNSS with post-seismic relaxation after 1949 | no rate in the abstract; seismogenic layer 15 ± 3 km, dip 63 ± 4° S | abstract | abstract only (PDF too large to fetch) |

Rule:
- `sr` = the rate on the fault of the preferred model of the latest GPS study read in full: **5.9 mm/yr** (Mendoza et al. 2015, segments 5.8–6.0).
- `sr_lo` / `sr_hi` = the lowest and highest central values of the GPS studies: **4.4** (Mendoza et al. 2011) and **6.8** (Mendoza et al. 2015, Model 1). Smalley et al. (2003), 6.6, lies inside.

This matches Pablo's 4–7 mm/yr.

Geological rates, for context:
- 6.4 ± 0.9 since 18 ka (Roy et al. 2020, Argentina)
- 7.8 ± 1.3 (Sandoval and De Pascale 2020, Argentina)
- in Chile, 7.8 ± 1.1 on the main fault and 10.5 ± 1.5 summed over strands (Sandoval and De Pascale 2020, disputed by Vassallo et al. 2024, Sci. Rep.), and 15.7 ± 2.4 on Almirantazgo Sound (Vassallo et al. 2024, Terra Nova, p. 327)

So the western, Chilean part may slip faster than any GPS rate.

**Mmax** (`tables/fagnano_mmax_2026-11-15.csv`). With the territory rule:

| quantity | value |
|---|---|
| system length, sum of the kept traces | 639 km |
| system length, end to end | 517 km |
| area at 20 km width | 12 775 km² |
| Mmax, Wells and Coppersmith 1994 (strike-slip, area) | 8.17 |
| **Mmax, Leonard 2014 (rule of DECISIONS)** | **8.10** |
| Mmax, Leonard 2014, end to end | 8.00 |
| observed maximum, frozen catalogue | Mw 7.8 (17 Dec 1949, both shocks, Centennial Mw) |

Other events in the box (crustal weight ≥ 0.5): 1879-02-02 Mw 7.0, 1950-01-30 Mw 6.9, 1970-06-15 Mw 6.8.

The current ISC-GEM gives the doublet Mw 7.69 ± 0.25 and 7.58 ± 0.46 (ComCat). The literature says 7.5–7.8 (Roy et al. 2020, p. 1; Vassallo et al. 2024, p. 328).

The old model's 8.0 + 0.2 came from the old catalogue value 8.0. With the rule of DECISIONS (Leonard, from the system area) the system Mmax is 8.1. The observed maximum + 0.2 gives 8.0, the same as the Patagonia background Mmax.

The 1949 surface rupture is at least 50 km long east of Lago Fagnano, with up to 6.5 m of slip (Roy et al. 2020, p. 5, p. 8). Roy et al. (2023, p. 2) give more than 150 km including Chilean ruptures, from a source not read. Which shock ruptured which section is unknown (Vassallo et al. 2024, p. 328).

**One source or separate segments** (`tables/fagnano_rates_2026-11-15.csv`). Assumptions:
- truncated Gutenberg–Richter from Mw 6.0, b 0.984 (the Patagonia b of B11, which is the forearc b)
- balanced to ψ μ L W s, with ψ 0.8, μ 30 GPa, W 20 km
- s = 5.9 mm/yr (4.4–6.8)

| model | Mmax | N(≥ 6.5) per yr | return period, Mw ≥ 6.5 | N(≥ 7) per yr | return period, Mw ≥ 7 |
|---|---|---|---|---|---|
| one system source, 639 km | 8.10 | 0.024 (0.018–0.027) | 42 yr (36–56) | 0.0072 (0.0054–0.0083) | 138 yr (120–186) |
| 13 separate segments | 6.45–7.64 | 0.061 (0.046–0.070) | 16 yr (14–22) | 0.0059 (0.0044–0.0068) | 171 yr (148–229) |

The moment is the same in both. Separate segments cannot produce an event above Mw 7.64 (the longest segment, CL-056b), so they put the moment into smaller events: 2.6 times more events of Mw ≥ 6.5 and 20 % fewer of Mw ≥ 7.

Against the record:
- One system source agrees with the Mw 7.5–7.8 doublet of 1949, which separate segments of 6.45–7.64 cannot produce.
- One system source also agrees with the four events of Mw ≥ 6.8 in about 145 years (1879–2026). For comparison, one source expects about 1.0 event of Mw ≥ 7 in 145 years, and segments 0.85.
- Separate segments predict an Mw ≥ 6.5 event every 16 years. Only five are known since 1879.

**Puerto Williams.** The clean database contains every segment of the SARA release near the city:

| segment | distance |
|---|---|
| AR-0056b | 43 km |
| AR-0056a | 45 km |
| AR-0056d | 50 km |
| AR-0056g | 70 km |
| CL-056d | 84 km |
| CL-056i | 90 km |
| CL-056c | 93 km |

Nothing near the city is missing apart from what GEM itself dropped (AR-0056c, e, f), and those cannot be recovered here.

The fall from 0.10 to 0.02 g in psha_chile7 is the max_mag-0 problem of LEARNINGS:
- With max_mag 0 read as missing, each short segment took its own small area Mmax.
- In the clean database there is no Mmax field, so the system Mmax must be set in the model. The test of B13 should check that every Magallanes–Fagnano segment gets the system Mmax.

## 4. Proposed DECISIONS lines and open questions

Proposed lines (Pablo decides):
- *Crustal and faults:* "Fault database: `data/faults/faults_2026-11-15.gpkg` (D16), 160 segments, fault properties only with a source per value (`model/faults/FIELDS.md`); replaces the shapefile `crustal_faults_chile_updated` as the fault input (15 Nov)."
- *Crustal and faults:* "Dip from the source text: the given number, the midpoint of a given range, GEM's class value for an open class; '90' is vertical (90°, not 87°) (D16)."
- *Crustal and faults:* "No fault from CHAF is added in this round; the GEM faults stay as they are. Faults missing from GEM, ranked, in `model/faults/tables/missing_2026-11-15.csv`; adding them would need a slip-rate rule and is future work, named in the paper (D16)." Or, if Pablo wants some added, which ones and with what rate.
- *Magallanes–Fagnano:* "One trace per section: each national database inside its own country, cut at the border (68° 36′ 38″ W); AR-0056a cut from 174 to 55 km; 639 km of trace (D16)."
- *Magallanes–Fagnano:* "Slip rate 5.9 mm/yr (4.4–6.8) for every segment: rate on the fault of Mendoza et al. (2015, Table 3); bounds the lowest and highest GPS values (Mendoza et al. 2011, 4.4; Mendoza et al. 2015, Model 1, 6.8) (D16)."
- *Magallanes–Fagnano:* "One system source, Mmax 8.1 (Leonard 2014 on the system area, 12 775 km²); separate segments only as a sensitivity. The observed maximum is Mw 7.8 (1949) in the frozen catalogue (D16)."
- *Magallanes–Fagnano:* replace "Mmax: to be checked thoroughly in D. Old model used a system value 8.0 + 0.2 from the 1949 event (6 Oct)" with the line above.

Open questions:
1. **Liquiñe–Ofqui slip rates.** The GEM class value of 3.0 mm/yr against 14–19 mm/yr measured on the master fault. This is not a D16 change, but it matters more for the southern cities than any missing fault.
2. **Fagnano west of the border.** GPS covers only Argentina. The Chilean geological rates are 7.8–15.7 mm/yr. Keep the GPS rate everywhere (as decided), or take the geological rate as a sensitivity in Chile?
3. **Fagnano geometry.** Mendoza et al. (2015) and (2022) find a dip of 63–66° S and a seismogenic layer of 11 ± 5 or 15 ± 3 km. The database has 90° and 0–20 km. Does B13 / the tornado use these?
4. **The 87° → 90° change** for 89 segments. OpenQuake accepts 90°. If Pablo prefers to keep GEM's 87°, it is one line in `db.py` (`OPEN_DIP` and the dip rule).
5. **AR-0005a (Chumbicha)**: no kinematics in any source; set to reverse.
6. **The 17 Chilean GEM segments that CHAF does not map**, NW-striking faults of the arc (class 0.5 mm/yr). Keep them as GEM has them?
7. **CHAF values to check.** El Yolki throw is "~0.2 mm/yr" in the CHAF file, but Melnick et al. (2019) give about 2 mm/yr throw and 5–6 mm/yr slip. The CHAF counts differ slightly between the file (78 / 592 / 288, 958 strands) and the paper (81 / 589 / 288; Table 1 sums to 959).
8. **The frozen catalogue gives the 1949 doublet Mw 7.8 / 7.8 (Centennial).** ISC-GEM now gives 7.69 / 7.58. This does not change the Mmax rule (Leonard on the area), but it changes the observed maximum + 0.2 of the Patagonia background (8.0 against 7.9).
