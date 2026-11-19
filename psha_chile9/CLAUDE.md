# CLAUDE.md: working rules for sessions in psha_chile9

## Start and end
- Your task is the last brief in `orchestration/<SESSION>.md` (the last `## Brief` heading). Read from that heading down, not the whole file. Read what the brief lists, nothing more unless you need it.
- Do the brief, nothing else. If it conflicts with `orchestration/DECISIONS.md`, stop and say so.
- End by writing your report below the brief in the same file, with these headings:
  - Done
  - Outputs (run ids, paths)
  - Figures to look at (paths, and what to compare with)
  - Decisions with Pablo (in his words)
  - Questions for Pablo (numbered, each with a recommendation)
  - Requests for other sessions
  - Learnings (proposed lines)
  - Left to do
- If Pablo says "save state", write the report now, with "Left to do" filled in.
- Do not write DECISIONS, PLAN, STATUS, QUESTIONS or another session's file: the orchestrator does that from your report.

## Where things go
- Code: `src/psha9/<your stage>/`, shared helpers in `src/psha9/common/` (change them only if the brief says so).
- Settings: `config/<stage>.yaml`; the model options and weights: `config/model.yaml`. No dates or settings hard-coded in code.
- Inputs: `data/raw/` is never edited; `data/raw/shapes/` only when the brief says so, and the report names the edit.
- Outputs of the pipeline: `runs/<stage>/<id>/`, ids by sequence (`cat-01`, `stats-02`). Write `run.yaml` there: date, the run ids read, a copy of the settings. A run is never edited after it is written; a change is a new run.
- A stage reads the newest run of the stage before it, unless its settings name another.
- Trials, comparisons, one-off scripts: `trials/<topic>/`. Never read by the pipeline. Say "trial, not used" in the report for anything left there.
- Figures: check figures in `runs/<stage>/<id>/figs/` (the same set every run); paper, supplement and presentation figures only by the FIG session in `figures/`; style in `docs/FIGURE_STYLE.md`.

## Reruns
- **Update:** an upstream run changed a little. Rerun, compare your check figures with the previous run, and write one line in the report. No tests, no long report.
- **Change:** your method changes. Full report.
- Do not redo work that is done (matching, overrides, fault curation); correct single entries.
- No patch rules for a few events: a rule needs a citation, or the problem is stated as a limitation; single events with a source go through the overrides file.

## Running
- You run the code yourself. Runs longer than about ten minutes: start them in the background with a log file, tell Pablo where the log is, and stop.
- One OpenQuake job at a time; check for stale jobs first (`oq engine --lhc`).
- Environment: conda `psha9`.
- Use `OMP_NUM_THREADS=1` with process pools.

## Tests
- Write a test when you create or rewrite a routine whose error would be silent (bin centres, moment balance, tree sums, reading results by label).
- Run tests only when you change code, never on an update.

## Code style
- Minimal inline comments; section comments only as `# text`, no decorative separators.
- Short variable names, few private helper functions.
- NumPy-style docstrings for important functions only.
- Nothing that reads like AI-generated code.
- Settings per tectonic class next to the class, not one large config.

## Writing
- Explain simply; Pablo is a seismologist, not a catalogue or ground-motion specialist.
- Cite by key and page from `docs/REFERENCES.md` (`rong_2014 p. 2312`). A claim from a paper nobody read is marked "not read". Missing papers go in the report.

## Other
- psha_chile8 and older folders: read them, copy from them, never change them.
- Git: work is on the branch `psha9`. Pablo commits. Do not run git commands that change the repository.
