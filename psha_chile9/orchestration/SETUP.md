# SETUP session

## Brief SETUP_01 (18 Nov): merge the references

**Goal:** one reference library for psha_chile9, without moving anything out of psha_chile8.

**Read first:** `psha_chile9/CLAUDE.md`; `claude/DESIGN_psha_chile9_orchestration.md` section 4.3 is summarised here, no need to read it.

**Tasks:**
1. Copy, do not move, every PDF from the psha_chile8 places into `psha_chile9/refs/`, named `<firstauthor>_<year>.pdf` (lower case, `_b` for a second paper of the same author and year):
   - `/data/PyCharmProjects/psha_chile/refs/` and its subfolders;
   - `psha_chile8/refs` if present;
   - any PDF named in `psha_chile8/REFERENCES.md`.
2. Write `psha_chile9/docs/REFERENCES.md`, one row per key: key, full citation, DOI (if known), file (or "no PDF"), and "supports": the psha_chile8 DECISIONS sections and reports that cite it.
   - Sources: psha_chile8 `REFERENCES.md`, `catalog/LITERATURE.md` and the PDFs themselves.
   - Group by topic: catalogue, statistics, interface, in-slab, crustal and faults, GMM, hazard.
3. List what does not match: citations without a PDF, PDFs cited nowhere, two files for one paper.

**Out of scope:** no reading of the papers beyond their first page; no changes in psha_chile8.

**Done when:** `refs/` and `docs/REFERENCES.md` exist; the report lists the mismatches.

**Report:** below this brief, with the headings of CLAUDE.md.

## Brief SETUP_02 (19 Nov): the `psha9` environment on every machine

**Goal:** one conda environment `psha9` with OpenQuake 3.27 on pansito, rs1, rs28 and rs37 (D-ENV-01).

**Read first:** `psha_chile9/CLAUDE.md`; `psha_chile9/environment.yml` (draft); psha_chile8 `hazard/remote.sh` (how the machines are reached).

**Tasks:**
1. On pansito: create `psha9` from `environment.yml`, `pip install -e .` in `psha_chile9/`; check `oq --version` is 3.27 and that `import openquake.hazardlib, geopandas, cartopy` work (the old `psha_renta` had broken GDAL data: check that geopandas reads a shapefile).
2. Pin the versions that were installed in `environment.yml` (exact versions, not ranges).
3. Write `config/hosts.yaml` (ssh name, working folder, how to activate `psha9`, cores) for pansito, rs1, rs28, rs37, from what `remote.sh` already uses.
4. On rs1, rs28 and rs37: the same environment from the pinned file, if Pablo's ssh access allows it; report each machine's OpenQuake version, cores, memory and free disk. If a machine needs Pablo (password, module system), stop there and say what is needed.
5. Run one tiny OpenQuake job (one site, one source, PGA) on each machine and compare the result across machines.

**Out of scope:** no model code; no changes to psha_chile8 or to `psha_renta`.

**Done when:** `psha9` works on pansito; pinned `environment.yml`; `config/hosts.yaml`; the report lists each remote machine as ready or what it needs.

**Report:** below this brief, with the headings of CLAUDE.md.

## Report SETUP_01 (19 Nov)

### Done
- Copied all 87 distinct PDFs from `psha_chile/refs/` (catalogs, faults, gmm, hazard_chile, root) into `psha_chile9/refs/<key>.pdf`. `psha_chile8/refs` does not exist; every PDF named in psha_chile8 `REFERENCES.md` lies in `psha_chile/refs/`. Nothing moved or changed in psha_chile8 or `psha_chile/refs/`.
- Wrote `docs/REFERENCES.md`: 117 keys in seven topic groups (catalogue, statistics, interface, in-slab, crustal and faults, GMM, hazard), with citation, DOI, file and "supports". Citations come from psha_chile8 `REFERENCES.md`; the 14 PDFs not listed there (rong, cisternas, pacheco, metois, youngs_coppersmith, costa, bird_kagan, chartier ×2, anderson_luco, wesnousky, field ×2, milner) from their page 1 only.
- "Supports" is found by author and year in the psha_chile8 DECISIONS sections, all `REPORT*.md`, LEARNINGS and the catalogue method notes. It is a text search, so it may miss a citation written in an odd form.
- Mismatches are listed at the end of `docs/REFERENCES.md`.

### Outputs (run ids, paths)
- `refs/` (87 PDFs), `docs/REFERENCES.md`.
- `trials/refs/merge_refs.py` makes both again (trial, not used by the pipeline).

### Figures to look at (paths, and what to compare with)
- None.

### Decisions with Pablo (in his words)
- None.

### Questions for Pablo (numbered, each with a recommendation)
1. Keys follow the brief (`<firstauthor>_<year>`, `_b`), so some files were renamed where the old name had the wrong year or spelling (digiacomo_2014 → digiacomo_2015, savage_2021 → savage_2022, rollins_2022 → rollins_2024, felzer_ucerf_2011 → felzer_2013, muller → mueller, giesecki → giesecke). Recommendation: keep these keys.
2. In some groups the second key goes to a later paper rather than the first (digiacomo_2015 = ISC-GEM part I, digiacomo_2015_b = part III; kagan_2002 = part I, kagan_2002_b = part II; leyton_2009 = Adv. Geosci., leyton_2009_b = PEPI). The three CEUS volumes are epri_2012, _b, _c. Recommendation: keep.
3. 123 author–year citations in psha_chile8 DECISIONS and reports have neither a full citation nor a PDF (Leonard 2014, Strasser 2010, Thingbaijam 2017, Allen and Hayes 2017, Wells and Coppersmith 1994, Gardner and Knopoff 1974, Weichert 1980, most of the GMMs and the D16 fault papers). Full citations for some of them are in psha_chile8 `catalog/A6/REPORT.md` §6, `catalog/MAGNITUDES.md` §9 and `catalog/RULES_LOCATION_MAGNITUDE.md` §5. Recommendation: one short follow-up brief to add those citations and get the PDFs, starting with the ones that support a DECISIONS line (Leonard, Strasser, Thingbaijam, Allen and Hayes, Wells and Coppersmith, Gardner and Knopoff, Weichert, Woessner and Wiemer, Helmstetter, Marzocchi and Taroni, Keefer and Bodily, Arteta 2023).

### Requests for other sessions
- None.

### Learnings (proposed lines)
- In psha_chile8, a PDF's file name did not always match the paper inside it (`tinti_mulargia_1985.pdf` is their 1985 completeness paper, not the BSSA 75 paper cited in B9). Check page 1 before citing a file by its name.

### Left to do
- 30 cited works have no PDF; the list is in `docs/REFERENCES.md` → Mismatches. Abe 1982, Abe and Kanamori 1979, Astiz and Kanamori 1986, Haynie 2026, García 2012 were read in psha_chile8 from copies that are not in `refs/` ("copy supplied by Pablo" / page images).
- DOIs still to check: kagan_2002, kagan_2002_b, musson_2012, llenos_2026; the authors of petersen_2024 and field_2013 are abbreviated with "et al."; the pages of wesnousky_2006 could not be read on page 1.
- 31 PDFs are cited only in the WORKLOG, handoffs or briefs and not in any decision or report (mainly the ISC-GEM series and the DSZ papers). Three are cited nowhere: epri_2012_c (CEUS Vol. 3), costa_2020, anderson_1983.
