# DATA session

Finished briefs and reports: `orchestration/archive/DATA_1.md` (DATA_01, 19 Nov).

## Brief DATA_02 (20 Nov): publishable input data

**Goal:** `data/raw/` ready to publish as is (Zenodo, D-DAT-04): every external input as obtained and described, every change that made our own data recorded in words, the known defects fixed, and the scripts that changed data set aside outside the final repository. No geometry or model choice changes.

**Read first:** `psha_chile9/CLAUDE.md`; in `orchestration/DECISIONS.md` the Data section (D-DAT-01 to 04), D-CLS-07, D-HAZ-01, D-HAZ-05; the DATA_01 report (`orchestration/archive/DATA_1.md`); for the faults `psha_chile8/model/faults/FAULTS.md` section 1, `FIELDS.md`, `REPORT_D16.md` ("Final fault file", hand rows), `REPORT_D16b.md` section 1, and the code `db.py`, `curate.py`, `dbB.py`, `mascsn.py`.

**Found in the orchestrator's review (20 Nov):**
- Database A (`faults/faults_gem_extra_2026-11-15.shp`): 91 text cells with broken accents ("ValparaÃ­so", "San RamÃ³n"); the `.csv` is correct. The previous-work file `crustal_faults_chile_updated` has the same defect (27 cells); the GEM release (`sara_active_faults`) does not.
- The four hand rows of the previous-work file (Bajo Molle, Marga Marga, Laguna Verde, Carranza) have no recorded origin; Marga Marga's 0.4–0.6 mm/yr is in no source found (REPORT_D16). The rule that chose 156 of the 437 GEM SARA rows for that file is not recorded either.
- Eight fault files in `faults/`, of which several are intermediate steps (`faults_2026-11-15`, `faults_gem_*`, `faults_gem_extra_pablo_*` and `*_b`, `crustal_faults_chile_*` without "updated").
- `grids/chile_005.csv` carries `vs30` = 380 for every site, against D-HAZ-01 (rock, Vs30 800); its origin is not recorded.
- No source recorded for `outlines/intraarc.shp` (empty metadata), `trenches/sam_nazca_trench_*`, the basemap; `outlines/chile_outline` is from simplemaps.com (licence not recorded).
- `trenches/pb2002_antarctic_trench_2026-11-15.geojson` (used for the western edge and the Antarctic plane) is an extract made in psha_chile8; the full PB2002 files are now in `trenches/`.
- `faults/riedel_hornig_primary_2026-11-14.csv` is a catalogue, not a fault file.
- File names carry the copy date (`_2026-11-15`), not the source version; the CHAF files carry impossible modification times (years 2073 and 2099).
- Checked and fine: every shape valid, WGS84; the crustal classes tile the crustal area exactly; margin footprints are the union of the segments; western sides on the edge except the Chile Rise inset; the interface lies inside the in-slab area; grids 0.1°, no duplicates (47 crustal and 34 in-slab cell centres lie on an area boundary, 2 more within 1e-6°, harmless); city coordinates plausible.

**Tasks:**
1. `data/raw/README.md`: one row per input (file or folder): what it is, external or ours, source and citation key (`docs/REFERENCES.md`), version, URL or DOI, licence, when and how obtained, the original file name if renamed, which stage reads it. Unknowns stay as "unknown (asked Pablo)".
2. `data/raw/CHANGES.md`: every change from an external input to our data, in words, with counts, IDs, sources and dates, so a reader can follow it without code:
   - faults: GEM SARA (437 rows) → previous-work selection (156) and the four hand rows → database A (cleaning rules of `FIELDS.md`, Pablo's two edits, the removals with reasons, the CHAF additions, the San Ramón trace, the Magallanes–Fagnano GPS rate) → 138 faults; database B from MASCSN26 (restored inputs) and the GEM rows of A. Also `faults/CHANGES_faults.csv`, one row per fault and change (fid, name, change, reason, source, date), made by comparing the files;
   - every shape in `shapes/` (what it was made from, Pablo's choices with dates), the PB2002 extract, the site grid.
3. Fixes, each recorded in CHANGES.md:
   - a. write database A's shapefile again with correct UTF-8 text (values from the `.csv`), and check every field against the `.csv`;
   - b. the intermediate fault files and other superseded files move out of `data/raw/` into the archive of task 4, after Pablo agrees to the list;
   - c. the site grid `vs30` column as Pablo decides (choice B).
4. Archive, not published: `psha_chile9/archive/data_provenance/` with copies of the scripts that made or changed data (`trials/data_shapes/*.py`, psha_chile8 `model/faults/{db,curate,dbB,mascsn,chaf,fagnano,geo}.py`, `trials/data_qgis/make_layers.py`) and a short README; add `archive/` to `.gitignore`. psha_chile8 stays unchanged.

**Decided with Pablo in the session** (one at a time, with a recommendation):
- A. Origin of the four hand rows, of Marga Marga's slip rate, and the rule that chose the 156 GEM rows (his previous work). Recommended: write what he remembers; where nothing is known, CHANGES.md says so.
- B. The site grid: origin, and the `vs30` column. Recommended: drop the column (the job sets Vs30, D-HAZ-01).
- C. `intraarc.shp`, `sam_nazca_trench`, the basemap: origin, and whether each is published. Recommended: publish only what a stage reads; the basemap is a figure input and is cited, not published.
- D. The country outline: keep simplemaps if its licence allows publishing, otherwise replace it with Natural Earth (public domain). Recommended: check the licence first.
- E. Licences of the derived fault databases: GEM's active-fault data carry a share-alike licence (to check), which would bind A and B. Recommended: check, and state it in the README.
- F. The list of files to move out (3b).

**Out of scope:** no geometry or model changes; nothing in `data/raw/catalog/` (CAT_01 writes there; Riedel-Hornig moves with CAT later); no renaming of files other sessions read (the README records original names instead); no downloads.

**Time:** short; no step runs longer than a minute.

**Done when:** README.md, CHANGES.md and CHANGES_faults.csv exist; 3a done; 3b and 3c done or waiting for Pablo; the archive exists; A–F answered or listed.

**Report:** below this brief, with the headings of CLAUDE.md.
