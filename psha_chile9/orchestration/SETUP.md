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
