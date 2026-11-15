# Fields of the clean fault database

**Final file for the model: `data/faults/faults_gem_extra_2026-11-15.shp` (and `.csv`), 138 faults**, built by `curate.py` from Pablo's two edits of the database below (`REPORT_D16.md`, section "Final fault file"). It has the same fields; `vertical` is 0 / 1 in the shapefile.

`data/faults/faults_<date>.gpkg` (layer `faults`, EPSG:4326, one row per segment) and `faults_<date>.csv` (the same without geometry). Built by `model/faults/db.py` from the frozen copy of `crustal_faults_chile_updated` (`data/crustal_faults_chile_updated_2026-11-15.*`). Shapefiles of the same rows: `faults_gem_<date>.shp` (the 156 GEM rows) and `faults_gem_extra_<date>.shp` (all rows). Source codes: **SARA** = the GEM SARA release (`data/sara_active_faults_2026-11-15.*`; the 156 GEM rows of the model file are identical to it), **CHAF** = Maldonado et al. (2021), Pangaea v1 (`data/chaf_pangea_v1_2026-11-15.*`), **hand row** = a row added to the model file by hand, origin not recorded.

The database holds only properties of the faults. No Mmax, a or b: those are computed in the model.

| field | content |
|---|---|
| `fid` | our segment ID: the GEM segment ID (`id_seg`) where there is one; `CHAF-<F_id>` for a hand row traced to a CHAF strand (the strand that covers most of the trace); `HAND-<n>` for a row that could not be traced (none at present) |
| `gem_id` | GEM / SARA segment ID (`id_seg`), empty if none |
| `gem_flt` | GEM / SARA fault ID (`id_flt`), which groups the segments of one GEM fault; empty if none |
| `system` | fault system. Rule, first that applies: (1) the GEM fault ID names it (CL-006 = Liquiñe–Ofqui, CL-056 and AR-0056 = Magallanes–Fagnano); (2) the GEM name is "Sistema de fallas X", "Zona de falla X" or "Grupo de fallas X" → X; (3) the CHAF system with the largest length of strands matched to the segment (`chaf_ids`), by the names of Maldonado et al. (2021), Table 1; otherwise empty |
| `sys_src` | which of the three rules gave `system`, or `none` |
| `name` | fault or segment name as in the source |
| `kin` | kinematics as given (SARA `rup_type`, lower case). Two SARA segments have none: AR-0236l takes the kinematics of the segments of the same GEM fault with the same dip class; AR-0005a has no such segment and is set to reverse (assumed, the old model's default rake). Carranza (hand row) takes the CHAF sense |
| `rake` | degrees, Aki and Richards convention, from `kin`: reverse 90, normal −90, sinistral 0, dextral 180; an oblique kind ("dextral-reverse", …) halfway between its two terms (135, 45, −135, −45) |
| `kin_src` | source of `kin` |
| `dip` | degrees. The number given in the SARA dip text (`dips`); the midpoint of a range given there ("30-45" → 37.5, "40-55" → 47.5); for the open classes the value GEM gives them (">60" → 72, "<45" → 37); "90" and "90." → 90. Hand rows: as in the row |
| `dip_dir` | dip direction, azimuth in degrees from the cardinal direction given (N 0, NE 45, …); empty where the source says VERTICAL |
| `vertical` | true where the source says VERTICAL or the dip is 90 |
| `dip_txt` | the SARA dip text as given |
| `dip_src` | source of `dip` |
| `sr` | slip rate, mm/yr, preferred value as given by the source (SARA `slip_rate`) |
| `sr_lo`, `sr_hi` | bounds of the class or range given by the source (`sr_txt`); empty for a single value |
| `sr_kind` | `class`: only an activity class of the GEM release (0.01–0.1, 0.1–1, 1–5 mm/yr), `sr` its representative value (0.055, 0.5, 3.0); `range`: a range given by the source that is not one of the classes, `sr` its midpoint as given; `measured`: a study gives the value (a single value, or a hand row whose CHAF strand carries a slip or throw rate) |
| `sr_txt` | the slip-rate text as given |
| `sr_src` | source of `sr`, with the CHAF value and reference for hand rows |
| `z_top`, `z_bot` | upper and lower seismogenic depth, km, as given. SARA gives 0 and 20 km for every segment of this file (a uniform default, not a fault property); the hand rows give 15 or 18 km |
| `z_src` | source of the depths |
| `length` | km, geodesic length of the trace on WGS84 (`geo.length`). Magallanes–Fagnano traces are cut at the border (68° 36′ 38″ W), each national database inside its own country (AR-0056a 174 → 55 km) |
| `src` | source of the geometry and name of the row: `SARA`; `hand row on CHAF strands` (Marga Marga and Laguna Verde extended to all strands of their CHAF name); `CHAF strands, simplified trace (added D16)` for the four faults added at Pablo's request (Mejillones northern section, Valparaíso, Quintay, Santa María): one trace through the strands (`geo.trace`), dip 72, 0–20 km and 0.5 mm/yr (class 0.1–1) as the similar GEM forearc faults (`ADD` in `db.py`) |
| `src_ref` | reference of the row. SARA rows: the GEM SARA release (South America Risk Assessment active faults, GEM Foundation; part of the GEM Global Active Faults database, Styron and Pagani 2020); hand rows: the CHAF strand name and its references |
| `chaf_ids` | CHAF strands (`F_id`) matched to the segment: more than half of the strand within 2 km of the trace; a strand matching several segments goes to the one it follows over the largest share |
| `chaf_act` | highest CHAF activity class among the matched strands (Proved > Probable > Possible); empty if none |
| `dup_of` | longer segments that lie within 2 km of this one over more than half of its length (flag only, nothing removed; exact duplicates would be removed and there are none) |
| `note` | free text where needed |

Removed from the model file: `id_area`, `min_mag`, `max_mag`, `a_val`, `b_val`, `usd`, `lsd` (values of the GEM area source each fault lies in), `ogc_fid`, `id_sys` (empty), `downt_side` (empty in every row), `len_st` and `length_km` (replaced by `length`), `az_tr` (computable from the trace). Renamed: `id_seg` → `gem_id`, `id_flt` → `gem_flt`, `rup_type` → `kin`, `dips` → `dip_txt`, `slip_rates` → `sr_txt`, `slip_rate` → `sr`, `upp_sd` → `z_top`, `low_sd` → `z_bot`.

CHAF activity classes (Maldonado et al. 2021, p. 3–4): **Proved**, a historical earthquake or robust published evidence of Holocene slip; **Probable**, geological or geomorphic evidence of rupture or deformation in the last 125 ka (MIS 5e); **Possible**, evidence of Quaternary activity.
