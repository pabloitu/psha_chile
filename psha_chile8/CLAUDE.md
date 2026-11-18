# CLAUDE.md: working instructions for Claude Code in psha_chile8

## Before starting
1. Read `PLAN.md`, `DECISIONS.md`, `LEARNINGS.md` and `CURRENT.md`.
2. Read the task brief you were given in `tasks/`. Do that task, nothing else. If the brief conflicts with DECISIONS, stop and say so.

## Where things are
- Repo root: `/data/PyCharmProjects/psha_chile`. Work only inside `psha_chile8/`.
- psha_chile6, psha_chile7, cat_handler_2 and older folders are archive: read them, never write to them, never import from them. Copy what you need into psha_chile8.
- Inputs enter as dated files (`name_YYYY-MM-DD.ext`) and are not edited after freezing. Every catalog run gets a row in `DATA.md`.
- Do not list or open heavy or vendored paths: `.git/`, `oq-engine/`, `pycsep/`, `SeismoStats/`, `data/967_buildings.csv`, `data/global_vs30.grd`, `data/Exposure_Res_Chile.csv`, `v2016.0.0.zip`, `data/catalogs/export_*.csv`, `*.tar.gz`, `*.zip`.
- Environment: conda `psha_renta`, OpenQuake 3.26 built from source, numpy 2.2.6 (works with this build; keep it).

## Parallel sessions
Several Claude Code sessions may run at the same time in psha_chile8, each on its own brief.
- Read `DECISIONS.md` at the start. Read it again before any choice that touches another family's model (classes, completeness, fits, declustering, Mmax, depths, the logic tree), and again before you finish. If it changed while you worked, check that your choices still hold, and say so in the WORKLOG entry.
- Never change a rule that belongs to another task. If your work needs a change in DECISIONS or in a shared module (`fits/`, `catalog/`, `model/faults/`), stop that part, and propose the change in the WORKLOG entry for Pablo.
- Ownership of shared inputs (Pablo, 16 Nov): `catalog/` belongs to the catalogue sessions (A6, A7), `fits/` to the fits session (B11/B12). A change to either is decided in the main conversation, made by its owner, and published as a new dated file (`catalog/frozen/<date>/`, `fits/tables/fits_<date>.csv`). The model sessions (S1, S2, S3, C15, B14) and the hazard session (S5) read those inputs by their date only, and rebuild when Pablo names a new date. If a model session finds a problem in a shared input, it reports it in the WORKLOG and waits; it does not edit the input.
- Current inputs: `CURRENT.md` lists the current file or folder of every shared input (catalogue, fits, depth cells, nodal planes, each family's NRML folder). Read your inputs from it at the start and before a build; do not rely on a date in a script or in memory. When you publish a new dated output that others read, update your own line in `CURRENT.md` in the same step as the DATA row. A folder you are still writing goes under "in progress".
- Messages to another session go into `handoffs/` as a short note, `handoffs/<date>_<from>_to_<to>.md` (what changed, the file or folder to read, branch ids, checks to run). Pablo then only points the other session to the note.
- Sessions are named by the part they own: CAT (`catalog/`), FITS (`fits/`, `catalog/declustered/`, `model/mechanisms/`, and the in-slab depth model: `model/inslab/depth.py`, `run.py`, `options.py`, `bench.py`, their figures and tests, `REPORT_C14.md`, `REPORT_C15.md`, the tables `depth_cells_*` and `class_share_*`), IF (`model/interface/`), IS (the rest of `model/inslab/`: the in-slab sources, patterns and tornado rows), CR (`model/crustal/`, `model/faults/`), HAZ (`hazard/`), GMM (`gmm/`).
- Write only inside the folders your brief names. Shared files (`WORKLOG.md`, `PLAN.md`, `DATA.md`, `FIGURES.md`, `REFERENCES.md`): re-read each one just before editing it, append or change only your own lines, and never rewrite the file from an earlier read.

## Running things
- Claude Code writes the code and may run tests or a quick check on a small subset. Pablo makes the runs: OpenQuake jobs, full catalog builds and full fits are not run unless the brief asks for it. Write the commands to run into the WORKLOG entry.
- Entry scripts keep their settings at the top of the file (Pablo runs them from PyCharm), not as command-line arguments.
- Tests: `pytest` from `psha_chile8/`. New code that computes something gets a test.

## Git
- Git commands that change the repo are denied in this setup. Pablo commits.
- When a commit is due, write the suggested `git add` lines and commit message into the WORKLOG entry. Commit messages carry no Claude signature or co-author lines.

## At the end of every session
1. Append one entry to `WORKLOG.md`: date, what was done, decisions made, commands Pablo has to run, open questions.
2. Tick the boxes in `PLAN.md` that are done, and move the ← marker if the step changed.
3. A new catalog run or input version gets a row in `DATA.md`.
4. New figures that are paper candidates get a row in `FIGURES.md`.
5. DECISIONS.md: when Pablo decides something in your session, write the line yourself, in the section of your own part, ending with "(Pablo, <date>, <session>)"; add a Superseded line when it reverses an earlier one. Re-read the file just before editing and change only those lines. Anything Pablo has not confirmed, and anything that belongs to another part, stays a proposal in the WORKLOG entry. Decisions Pablo makes in the context conversation (chat) are written into DECISIONS and logged in the WORKLOG by that conversation directly, tagged "(Pablo, <date>, context)"; sessions read them there and do not wait for a prompt (Pablo, 17 Nov). LEARNINGS.md: propose lines in the WORKLOG entry.

## Code style
- Minimal inline comments. Section comments only as `# text`, no decorative separators.
- Short variable names, few private helper functions.
- NumPy-style docstrings for important functions only.
- Nothing that reads like AI-generated code.
- Settings per tectonic class, next to the class, not one large config file.

## Figure style
- The full figure rules are in `FIGURE_STYLE.md` (repo root); read it before making any figure. The lines below are the short version.
- Catalogue paper and supplement figures go straight into `catalog/FIGURES/<type>/` (`maps`, `magnitudes`, `rules`); checks stay in `catalog/figs/`. Every paper or supplement figure keeps its row in `FIGURES.md`.
- Ubuntu font; one shared palette and one set of display class names for catalog, fit and hazard figures (start from `cat_handler_2/palette.py`); no code names in legends.
- Large events drawn on top; in sections only M ≥ 7 labelled, landward extent capped at 400 km, near-proportional depth-to-distance axes.
- Few labels, concise titles, comfortable margins. Comparisons as hazard curves against a baseline rather than tables alone.
- Comprehensive static figures, not HTML viewers, unless the brief asks.
