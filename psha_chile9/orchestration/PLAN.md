# PLAN

## Part 1: how we work
- [x] Design, rev. 4 (18 Nov)
- [x] Skeleton of psha_chile9 (18 Nov)
- [x] DECISIONS consolidated with Pablo, every section (18 Nov): 135 rules, history apart
- [x] LEARNINGS cleaned with Pablo (18–19 Nov)
- [x] FIGURE_STYLE merged (18 Nov)
- [ ] References merged into `refs/` and `docs/REFERENCES.md` (SETUP_01)
- [ ] Environment `psha9` created and tested on every machine (SETUP, OpenQuake 3.27, D-ENV-01)
- [x] Porting map `docs/PORTING_MAP.md` (19 Nov)
- [x] Handoff to the new orchestrator conversation: `orchestration/HANDOFF_part2.md`, project doc `claude/HANDOFF_psha_chile9_part2.md` (19 Nov)
- [ ] SETUP_02 environment (brief written, 19 Nov)

## Part 2: methods and the step-by-step plan
- [x] Classification method note `docs/methods/CLASSIFICATION.md` (18 Nov)
- [ ] Magnitude method note `docs/methods/MAGNITUDES.md`: inverse regression with references for and against, dithering (Stallone and Spassiani 2026)
- [ ] Method notes for the other stages, then the step-by-step plan (after Pablo commits the skeleton)
- HAZ to port: a status command (job running or stale, phase preclassical / classical, progress or waiting), nothing written

## Open questions by session (QUESTIONS.md), in working order
- CAT first, everything reads the catalogue: Q-36, Q-38, Q-39, Q-41, Q-42, Q-43, Q-44, Q-45, Q-60, Q-67, Q-68, Q-69; review lines D-CAT-03, 10, 12, 14, 15, 18, 19, 20, D-MAG-06.
- DATA (polygons, grids, collection area, segment limits): Q-25, Q-26, Q-40, Q-54, Q-55; crustal polygons redrawn by Pablo over the psha_chile8 seismicity (D-CLS-07, 09, 10).
- STATS (trials, then fits): Q-46, Q-47, Q-48 (inconsistency first), Q-49, Q-50, Q-51, Q-52, Q-53, Q-56, Q-57, Q-58, Q-59, Q-61, Q-62; review lines D-STA-12, D-CR-05, D-IS-07.
- IF: Q-11, Q-12, Q-16, Q-56 (geodetic part, with Pablo's moment-deficit idea), Q-55.
- IS: Q-29, Q-59, D-IS-06 (cells dropped, southern extent).
- CR: Q-19, Q-20, Q-21, Q-22, Q-23, Q-24, Q-28, Q-34, Q-35, Q-63, Q-64, Q-65.
- HAZ: Q-33, Q-66.
- Co-authors, send early (they block the final tree, not the work): Q-13, Q-14, Q-15, Q-17, Q-18, Q-30, Q-31, Q-32.
