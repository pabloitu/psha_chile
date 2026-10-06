# cat_handler_2

Builds the earthquake catalog of the Chile PSHA from frozen inputs, with the
provenance of every field. Replaces cat_handler / cat_no_mech_handler
(merge_catalogs, get_moment_and_relocate, the formatted catalogs).
psha_chile6 classifies and declusters the output; this package does not.

Run from the repo root, with the inputs in data/catalogs:

    python -m cat_handler_2.build

Outputs go to results/cat_handler_2/: one table per stage (01_dedup.csv,
01_dedup_groups.csv, ...), build.json with the counts, and at the end catalog.csv.
Only events with Cabello magnitude above 3.9 are written (config MMIN).

To check the merge:

    python -m cat_handler_2.check

writes results/cat_handler_2/check/: pairs.png, summary.png, locate.png, mech.png, classify.png, sections.pdf, groups.pdf, mech_disagree.csv, class_changes.csv (one panel
per merged group with kept M >= 6 and per near miss with M >= 5.5) and
near_misses.csv.

## Inputs (data/catalogs, frozen)

| file | role |
|---|---|
| ../shapefiles/pb2002_antarctic_trench.geojson | Antarctic trench south of the Chile triple junction, from Bird (2003) PB2002 |
| Integrated_Seismic_Catalog_complete.csv | Cabello et al. (2025): base catalog; every event and every magnitude comes from it |
| CHILE_SEISMICITY_RELOCATED.csv | Potin et al. (2024): location and depth of CSN events Cabello left unrelocated, and of fixed-depth events |
| gcmt_*.txt (ndk) | centroid, centroid-depth flag, mechanism fallback; ties Cabello's GCMT rows (centroids) to their PDE hypocentre |
| anss_fm.csv | ComCat moment tensors queried event by event (old parsers/anss.py): first mechanism source |
| cat_gem_chile.csv | mechanisms of large pre-1976 events |
| overrides.csv (in this package) | event-level decisions with a reference |

## Files

| file | content |
|---|---|
| config.py | paths, windows and preference orders; every choice that changes the catalog |
| sources.py | one reader per input, and the matching (pairs within time / distance / magnitude windows, one-to-one) |
| build.py | the stages as functions in order, and main |
| classify.py | the classification stage (geometry and mechanism tests) |
| check.py | diagnostics of the merge: figures, a PDF of the large groups and near misses |
| overrides.csv, additions.csv | event-level decisions and missing events, each with a reason and reference |
| compare.py | old classified catalog against catalog.csv on common ground (python -m cat_handler_2.compare) |
| beachballs.py | beachball images and a points table for the QGIS map (python -m cat_handler_2.beachballs) |
| tools/ | one-off checks, not part of the build |

## Stages (build.py)

| stage | does | status |
|---|---|---|
| dedup | cross-agency duplicates in Cabello: GCMT rows tied to their ndk hypocentre, groups by time / distance / magnitude windows, one row per group; magnitude always a Cabello magnitude (GCMT row, ISC-GEM row, native Mw, location row) | done |
| locate | Potin one-to-one for CSN rows Cabello did not relocate; depth_status (relocated_cabello, relocated_potin, free, assigned, fixed, missing, filled); a fixed (USGS / ISC / ISC-GEM at 0, 10, 33 km) or missing depth is filled from another row of the same group, then Potin, then the GCMT centroid if FREE; loc_src, depth_src, potin_id, depth_orig | done |
| mech | nodal planes (and tensor when the source has one) from ANSS > GCMT > Cabello's own planes > GEM, one-to-one within MECH_WIN; mech_src, mech_type, the ids and match distances of every source found | done |
| classify | classify.py: class and deciding rule (cls_rule) from Slab2, the intra-arc polygon, the trench and the mechanism; unknown depths (fixed, missing, assigned) skip the depth test: mechanism, else interface where the slab top is shallower than 50 km, else unresolved | done |
| overrides | overrides.csv (id, field, value, reason, reference): row fixes (time, location, ...) applied to Cabello rows before the dedup, class decisions after the classification (class_auto keeps the rule's class); additions.csv: events missing from Cabello | done |
| review | data/catalogs/ruiz_madariaga_2018.csv matched to the catalog (05_review_rm.csv: our class next to the paper's, agree, weak and shared matches); every M >= 7 event with its flags (05_review_m7.csv); proposed overrides where we differ (05_overrides_draft.csv); writes catalog.csv | done |

## Output columns (catalog.csv)

id (Cabello id), time_iso, t, longitude, latitude, depth, mag (Cabello Mw),
depth_status, loc_src, depth_src, mag_src, mech_src, strike1..rake2,
Mrr..Mtp, gcmt_id, anss_id, potin_id, c_lon, c_lat, c_depth, c_dtype
(GCMT centroid), dup_ids, n_rows, override, flags; Cabello's own columns
(agency, relocated, obs_depth, general_remarks, reference, Mw_native, Mb, Ms,
Ml) are carried unchanged.

## Rules

All windows and preferences are in config.py. Current choices:
- output: Cabello magnitude above 3.9
- duplicates: different agencies, from 1900, inside any window of DUP_RULES
  (now 15 s, 50 km, 0.8 units); pairs beyond 10 s / 30 km flagged loose
- fixed depths: 0, 10, 33, 35 km, only for USGS, ISC, ISC-GEM rows; GCMT fills a
  depth only where Cabello's is missing or fixed
- magnitude of a group: Cabello magnitude of the GCMT row, else ISC-GEM, else a
  row with native Mw, else the location row; never a magnitude from outside Cabello
- location of a group: Potin-relocated CSN, ISC-GEM, ISC, USGS, CSN, GCMT, CERESIS-GEM

## tools/

Checks run before the build (check_raw.py, check_depth.py) and the
reproduction of the old chain (reproduce.py, audit.py).