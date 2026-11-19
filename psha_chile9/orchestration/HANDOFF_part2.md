# Handoff to the new orchestrator conversation (psha_chile9, part 2), 19 Nov 2026

## Who does what
- **Pablo** decides, looks at figures, commits (git branch `psha9`, D-ORC-04).
- **You, the orchestrator,** write the briefs, DECISIONS, QUESTIONS, STATUS and PLAN; read session reports yourself; do not write model code. Read and write files on pansito through the device bridge, and after every write re-stage and compare (the bridge sometimes writes the old version).
- **Sessions** (Claude Code in `/data/PyCharmProjects/psha_chile`, one per stage: SETUP, DATA, CAT, STATS, IF, IS, CR, GMM, HAZ, FIG) do one brief each, from `psha_chile9/orchestration/<SESSION>.md`, and report below it.

## Read first (pansito: `/data/PyCharmProjects/psha_chile/psha_chile9/`; copies in the project)
1. `claude/DESIGN_psha_chile9_orchestration.md` (project doc): how the work is organised.
2. `orchestration/PLAN.md`, `STATUS.md`: where things stand; the open questions by session in working order.
3. `orchestration/DECISIONS.md`: the current rules (about 136, ids D-…); history apart.
4. `orchestration/QUESTIONS.md`: open questions Q-11 to Q-69.
5. `docs/PORTING_MAP.md`: per stage, the psha_chile8 steps, code, reports, the decisions and questions each step carries, and the order of work.
6. `docs/methods/CLASSIFICATION.md`: the one method note written so far, the model for the others.
7. `docs/LEARNINGS.md`, `docs/FIGURE_STYLE.md`, `CLAUDE.md`: when a brief needs them.
psha_chile8 method reports are in the project folder `psha_chile8_reports/` (and on pansito in psha_chile8, read-only).

## Where we are
- Part 1 done (18–19 Nov): design rev. 4, skeleton, DECISIONS consolidated with Pablo section by section, QUESTIONS, LEARNINGS cleaned, FIGURE_STYLE, the classification method note, the porting map. Pablo commits them on `psha9` before part 2 starts; if `git status` shows them uncommitted, ask him.
- SETUP_01 (references) is ready to run; SETUP_02 (environment `psha9`, OpenQuake 3.27 on pansito, rs1, rs28, rs37) is written.
- No runs yet in psha_chile9.

## How part 2 goes
- Method notes are written one stage at a time, just before the stage starts, with Pablo: `docs/methods/<STAGE>.md`, simple to explain but capturing the science, each with references for and against where the method is debated, a validation plan and the limits to state.
- Order: SETUP (runs alone) → **DATA note with Pablo** (collection and forecast areas, segment ends incl. Arica, grid spacing; Pablo draws the crustal polygons incl. the forearc) → CAT note (reading, matching, merge, locations and depths, magnitudes with the inverse-regression argument and its references, classification already written) → CAT steps 1–6 can start in parallel with DATA; step 7 waits for DATA → STATS → IF, IS, CR → GMM → HAZ → FIG.
- Briefs are short because the porting map carries the detail: "port steps C1–C4, apply D-…, answer Q-…, rerun, compare these figures with psha_chile8 17g".
- Spin-offs, not in the main build: the clustering model (negative binomial with α falling with magnitude, stochastic event sets), checked in STATS once the whole model stands (Q-13).

## Pablo's way of working (keep)
- Explain simply, few numbers at once; he is a seismologist, not a catalogue or GMM specialist. Speak and write slowly when he is on voice.
- Write decisions directly into the files; never ask him to relay prompts.
- No unnecessary bookkeeping; tests only for new routines; check figures by eye against psha_chile8, no reproduction tests.
- Argue against him when you think he is wrong; he wants sparring, especially on methods.
- He prefers equal weights, nearest-neighbour declustering, and not modifying data to fit a model.

## Opening message (paste into the new conversation)
> You are the orchestrator of psha_chile9 (Chile PSHA). Read the project doc `claude/HANDOFF_psha_chile9_part2.md` first and follow its "Read first" list, from the project copies or from pansito (`/data/PyCharmProjects/psha_chile/psha_chile9/`). Then tell me in a few lines where we stand and what you propose for today. I will start SETUP_01 and SETUP_02 in Claude Code; today we write the DATA method note together.
