# CLAUDE.md: working instructions for Claude Code in psha_chile8

## Before starting
1. Read `PLAN.md`, `DECISIONS.md` and `LEARNINGS.md`.
2. Read the task brief you were given in `tasks/`. Do that task, nothing else. If the brief conflicts with DECISIONS, stop and say so.

## Where things are
- Repo root: `/data/PyCharmProjects/psha_chile`. Work only inside `psha_chile8/`.
- psha_chile6, psha_chile7, cat_handler_2 and older folders are archive: read them, never write to them, never import from them. Copy what you need into psha_chile8.
- Inputs enter as dated files (`name_YYYY-MM-DD.ext`) and are not edited after freezing. Every catalog run gets a row in `DATA.md`.
- Do not list or open heavy or vendored paths: `.git/`, `oq-engine/`, `pycsep/`, `SeismoStats/`, `data/967_buildings.csv`, `data/global_vs30.grd`, `data/Exposure_Res_Chile.csv`, `v2016.0.0.zip`, `data/catalogs/export_*.csv`, `*.tar.gz`, `*.zip`.
- Environment: conda `psha_renta`, OpenQuake 3.26 built from source, numpy 2.2.6 (works with this build; keep it).

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
5. Do not edit DECISIONS.md or LEARNINGS.md yourself; propose lines in the WORKLOG entry.

## Code style
- Minimal inline comments. Section comments only as `# text`, no decorative separators.
- Short variable names, few private helper functions.
- NumPy-style docstrings for important functions only.
- Nothing that reads like AI-generated code.
- Settings per tectonic class, next to the class, not one large config file.

## Figure style
- Ubuntu font; one shared palette and one set of display class names for catalog, fit and hazard figures (start from `cat_handler_2/palette.py`); no code names in legends.
- Large events drawn on top; in sections only M ≥ 7 labelled, landward extent capped at 400 km, near-proportional depth-to-distance axes.
- Few labels, concise titles, comfortable margins. Comparisons as hazard curves against a baseline rather than tables alone.
- Comprehensive static figures, not HTML viewers, unless the brief asks.
