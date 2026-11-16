Note for S5 (hazard jobs), from S3 (crustal), Pablo 16 Nov. Re-read CLAUDE.md and DECISIONS (Crustal and faults, Hazard runs, Logic tree) when you pick this up.

The crustal family (S5b) is being built now. Do not start crustal jobs until all of the following are true:
- WORKLOG has an entry "S3: crustal OpenQuake files ready (2026-11-16g)" (the 16e folder is superseded: old rupture set, old section ids).
- `model/crustal/nrml/2026-11-16g/branches.json` exists and has `"ready": true`.
- The S3 parse check passed: `model/crustal/tables/oqcheck_2026-11-16g.csv`, every file read by OpenQuake's converter, rates equal to the tables.
Check those three every time you finish a job; until then keep running interface and in-slab.

What you will find in `model/crustal/nrml/2026-11-16g/`:
- `branches.json`:
  - `files`: every source file with its factors (declustering, fault system, database, psi, depth, MFD shape, jump);
  - `tree`: the crustal family tree, files and weights per level;
  - `tornado`: the crustal rows, each a list of (file, weight) sets;
  - `reference`: the reference branch;
  - `settings`: maximum distance, Mmin, tectonic region type.
- Logic-tree fragments: `lt_crustal_tree.xml` (84 sourceModel branches, each listing all its files) and `lt_crustal_reference.xml`. `branches.json` is the source of truth.
- Thickness tags are `t10` / `t20` (the seismogenic thickness; the 16e files said `z10` / `z20`). Branch ids changed accordingly.
- New tornado rows against 16e: `splays`, `mmax_pad00_mf`, `mmax_pad04_mf`, `mmax_pad00_seg`, `mmax_pad04_seg`, `fault_pad02_seg`, `fault_pad04_seg`; `depth20` is now `thickness20`; `jump20` is gone (not credible, 860 km chains).
- Source types:
  - background: point sources, nodal planes per class;
  - faults: simple-fault sources (single-fault ruptures, Leonard Mmax);
  - Liquiñe–Ofqui multi-fault ruptures: multiFaultSource, with a sections file `cr_sections_<db>_z<depth>.xml` that must sit next to the source file in the job's src folder.
- Source Mmin 5.5 (first bin centre), as interface and in-slab.

Crustal job settings (DECISIONS, Hazard runs): maximum distance 300 km, point-source distance 100 km, the 14 cities, PGA, 475 yr, the crustal GMM tree of DECISIONS; everything else as your interface and in-slab jobs.
- `investigation_time = 1.0` is required: the multi-fault files (NRML 0.5, one source group) carry occurrence probabilities for 1 yr, and OpenQuake refuses a job with another investigation time.
- A multi-fault branch lists three files (background, faults, sections); copy all three into the job's src folder and put them in the same `uncertaintyModel`, space-separated.
- A working single-site example: `model/crustal/oqcheck/2026-11-16g/` (job.ini, lt_crustal_reference.xml).

Queue order once ready:
1. the crustal reference (`t_cr_ref`); time it first and give the expected total;
2. the crustal tornado rows;
3. the crustal family tree; check its realizations, and split by the fault-system level if it is above about 2 000;
4. the GMM rows for the crustal family.

One OpenQuake job at a time in the running queue, as for your other families. Then add the crustal family to the combined results, and drop the "without the crustal family" marks where the crustal family is now in.
