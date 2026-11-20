# PLAN

## Part 1: how we work
- [x] Design, rev. 4 (18 Nov)
- [x] Skeleton of psha_chile9 (18 Nov)
- [x] DECISIONS consolidated with Pablo, every section (18 Nov): 135 rules, history apart
- [x] LEARNINGS cleaned with Pablo (18–19 Nov)
- [x] FIGURE_STYLE merged (18 Nov)
- [x] References merged into `refs/` and `docs/REFERENCES.md` (SETUP_01, 19 Nov; 87 PDFs, 117 keys; missing citations open)
- [x] Environment `psha9` and `config/hosts.yaml` set up by Pablo (19 Nov; D-ENV-01, D-HAZ-09)
- [x] Porting map `docs/PORTING_MAP.md` (19 Nov)
- [x] Handoff to the new orchestrator conversation: `orchestration/HANDOFF_part2.md`, project doc `claude/HANDOFF_psha_chile9_part2.md` (19 Nov)

## Part 2: methods and the step-by-step plan
- [x] Classification method note `docs/methods/CLASSIFICATION.md` (18 Nov)
- [x] DATA_01 (19 Nov): geometry frozen in `data/raw/shapes/`, run `runs/data/data-07`
- [ ] DATA method note `docs/methods/DATA.md`, written by the orchestrator from DECISIONS (Data, D-CLS-07–10, D-IF-03, D-IF-10) and the DATA_01 report
- [ ] CAT method note, drafted by the orchestrator from the decisions for Pablo to read before CAT_01
- [ ] CAT_01 (written, not started): steps C1–C6, run `cat-01`
- [ ] CAT_02 (after CAT_01): review of the Mw ≥ 7 events classed by rule or with poor depths (D-CAT-23), literature, overrides
- [ ] CAT_03: classification C7 on data-07, check figures C8
- [x] Review of the input data by the orchestrator (20 Nov): findings in brief DATA_02
- [ ] DATA_02 (written, not started): README and CHANGES for `data/raw/`, fault encoding fix, intermediates out, scripts archived (D-DAT-04)
- [ ] Magnitudes as a section of the CAT method note: inverse regression with references for and against, dithering (Stallone and Spassiani 2026)
- [ ] Method notes for the other stages, then the step-by-step plan (pipeline order, one note just before each stage: DATA, CAT, STATS, IF / IS / CR, GMM, HAZ, FIG)
- HAZ to port: a status command (job running or stale, phase preclassical / classical, progress or waiting), nothing written

## Open questions by session (QUESTIONS.md), in working order
- CAT first, everything reads the catalogue: Q-36, Q-38, Q-39, Q-41, Q-42, Q-43, Q-44, Q-45, Q-60, Q-67, Q-68, Q-69; review lines D-CAT-03, 10, 12, 14, 15, 18, 19, 20, D-MAG-06.
- DATA: done (19 Nov); open: Q-71 (with CAT), Q-72, Q-73 (with IF), Q-74 (with CAT_02), Q-75.
- STATS (trials, then fits): Q-46, Q-47, Q-48 (inconsistency first), Q-49, Q-50, Q-51, Q-52, Q-53, Q-56, Q-57, Q-58, Q-59, Q-61, Q-62; review lines D-STA-12, D-CR-05, D-IS-07.
- IF: Q-11, Q-12, Q-16, Q-56 (geodetic part, with Pablo's moment-deficit idea), Q-55.
- IS: Q-29, Q-59, D-IS-06 (cells dropped, southern extent).
- CR: Q-19, Q-20, Q-21, Q-22, Q-23, Q-24, Q-28, Q-34, Q-35, Q-63, Q-64, Q-65.
- HAZ: Q-33, Q-66.
- Co-authors, send early (they block the final tree, not the work): Q-13, Q-14, Q-15, Q-17, Q-18, Q-30, Q-31, Q-32.
