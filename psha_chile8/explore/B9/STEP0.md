# B9 step 0: two loose ends from A8

Read-only audit by a sub-agent on 14 Nov 2026; counts recomputed from `catalog/frozen/2026-11-14/*.csv` and
`catalog/merged/*_2026-11-14b/c.csv`. I did not re-run the recount myself; the per-event table of the 50 km check was
left in the session scratchpad (not in the repo). Nothing was edited.

## 1. The 50 km check: 94, not 85

No flag marks the check in the frozen files: in `locate.py:210-222` (`inside_network`, `FAR_KM = 50`) a far local
record only makes `inside_network` False. Recount by calling `records()` and `wide()` of `catalog/locate.py` with the
frozen defaults and repeating the distance test (reproduces `inside_network` for 204 956 of 204 956 events).
Counted: the event has a local record, more than 50 km from every teleseismic or GCCEL record, and would otherwise be
inside the network.

| population | count |
|---|---|
| all events, any size | 423 |
| in the domain, any size | 420 |
| Mw ≥ 4.5, anywhere | 97 |
| **Mw ≥ 4.5 in the domain** | **94** (89 Potin era, 5 CSN era) |
| Mw ≥ 5.5 in the domain / anywhere | 13 / 14 |

94 is right. 85 is not reproduced by any saved run (the Mw files of 13 Nov, 13e and 14b all give 94; the file of
11 Nov gives 91). 85 with "13 of Mw ≥ 5.5" first appears in WORKLOG:675 and was copied to DECISIONS:23 and the paper
draft; what it counted was not found.

Proposed corrections:
- `DECISIONS.md:23` → "… is not used (quality check; 94 events of Mw ≥ 4.5 in the domain, 423 of any size, run 2026-11-14b) (13 Nov)."
- `paper/CATALOG_SECTION_draft.md:49` → "94 events of Mw ≥ 4.5 fail this condition" (drop the "[to check on the final run]"); `:143` → the 94 were recounted on the final run, the offshore depth differences were not.
- `catalog/REPORT_A3-A5.md:103` → "(97 of Mw ≥ 4.5 anywhere; 13 of Mw ≥ 5.5 in the domain, 14 anywhere; 423 of any size)"; the present "97 in all, 14 of Mw ≥ 5.5" mixes populations.

## 2. Numbers and statements that disagree with the frozen run or DECISIONS

**DECISIONS.md** (for Pablo; not edited)
- `:23` 85 events → 94.
- `:35` the list "left as they are" still names 1934-03-01; `:36`, `:150` and the DECISIONS_NOTE give four events (frozen Mw 7.6).
- `:14-15` Cabello "not used from 1900 on" / "before 1900" against `:17` and the code: 1904. Three events of 1902–1903 have a Cabello epicentre, one (1903-08-12, Mw 6.1) a Cabello Mw.
- `:15` "Potin (1982–2022); CSN (2022 to today)" against `:17` and the run: Potin to 2020-07-16, CSN after.
- `:26` unknown depths "classified by mechanism, by the depth another agency gives …" against the frozen rule (`:62`, `classify.py`): position, in-slab if every rejected depth is ≥ 70 km, else bin shares; a mechanism does not classify an event without depth.
- `:50` order before 1976 omits the measured reference Mw, which the code puts second (`magnitude.py:552-553`; 9 events before 1976 are `direct`). Same omission in DECISIONS_NOTE:13 and paper:61; REPORT:36, RULES M1 and MAGNITUDES:15 have it.

**frozen/2026-11-14/DECISIONS_NOTE.md**: every recomputed number agrees. `:13` as above. `:45` "web tables used for 1878 and 2025" against REPORT:106 "for 1878".

**catalog/REPORT_A3-A5.md**
- `:103` "97 in all, 14 of Mw ≥ 5.5" → see part 1.
- `:34` GUC MW "107 events" → 106 in the frozen catalogue (any size; 42 at Mw ≥ 4.5 in the domain); the 107th is 2011-01-07, now kind `a6`.
- `:56` "about 35–40 % fewer events at M ≥ 5 than both published catalogues … holds from 2011" → per period −40 / −45 / −44 / −33 % against Cabello, −42 / −36 / −34 / −19 % against Candia and Macedo (19 % for 2011 on).
- `:59` "about 1 000 events (1 017)" → 1 017 anywhere, 865 in the domain.
- `:102` 2011-01-07 "converted from ML alone … corrected in A6" → the frozen rule already gives GUC MW 5.6; A6 moves it to 5.7. 2010-02-27 is still from ML (6.97 → 6.3).

**catalog/MAGNITUDES.md**
- `:10` "6 335 events have a reference Mw (GUC MW 107)" → 6 334 and 106 (2011-01-07 is `a6`).
- `:12` 1 017 → 865 in the domain.
- `:112` (§6a) limit at Mw 5 "4.7 % too high … 6.9 % too low", no limit "1.9 % low" against DECISIONS:50 and paper:61 "+5 to +10 % or −7 to −15 %" and "−2 %"; both labelled 12 Nov.
- `:135` "[Test numbers to be filled.]".

**catalog/RULES_LOCATION_MAGNITUDE.md**
- `:61-68` the column "events (Mw ≥ 4.5)" mixes populations: L4 94 (Mw ≥ 4.5 in the domain), M3 1 017 (anywhere; 865 in the domain), M5 107 (any size, before A6; 106 frozen, 42 at Mw ≥ 4.5 in the domain).
- `:50` (M5) 107 → 106. `:48` (M3) 1 017 → 865 in the domain.

**paper/CATALOG_SECTION_draft.md**
- `:49`, `:143` 85 → 94.
- `:6`, `:146`, `:148`, `:152` say MAGNITUDES.md and CLASSIFICATION.md describe earlier runs; both now state runs `2026-11-14b` / `2026-11-14c` and their tables match the frozen files.
- `:57` 107 and 6 335 → 106 and 6 334.
- `:61` order before 1976 omits the measured Mw.
- `:83` the crustal score also fades from the Moho (40 km) to the slab top; the text does not say it.
- `:106` 1 017 → 865 in the domain.
- `:163` (E.3) "about 40 % fewer" → 33–45 % against Cabello, 19–42 % against Candia and Macedo.
- `:164` (E.4) 2011-01-07 "converted from ML alone" → GUC MW 5.6, A6 5.7.
- `:162` (E.2) "(limitation 2)": the mb point is the third bullet of 2.8.
- `:3`, `:8` stale header ("Draft of 12 Nov").

**frozen/overrides_A6.csv** (found on the way): two accepted Mw rows carry an `old_value` from before the order changes of 13 Nov: 1959-06-14 (old 7.9; the rule now gives 7.1, A6 7.2) and 2011-01-07 (old 6.6; the rule now gives 5.6, A6 5.7).

## 3. Open marks

- paper:49 "85 [to check on the final run]"; :51 "Engdahl et al. 2020 [to check]"; :63 "[references of the review table to add]", "[to check: 112 of 459 on 13 Nov]"; :85 "[to check on the final run: 833 of 878 events on 14 Nov]"; :91 "[… 151 and 53 events on 14 Nov]"; :99 "[Completeness periods and declustering: to be written …]"; :105 "[to be done]" (mb sensitivity case); :109 "[… mean 0.39 on 16 events on 13 Nov]"; :110 "[check with the model declustering]"; :143, :147, :167, :169 "not recomputed" / "not redone".
- MAGNITUDES:54 forward against inverse "not rechecked for run 2026-11-14b"; :110 §6a numbers of 12 Nov; :135 "[Test numbers to be filled.]"; :152 references "not yet verified".
- REPORT:98 Potin 11–21 km too shallow, "not rechecked"; :106 Kanamori and Rivera (2017), Astiz (1987), web tables not re-read.
- RULES:49 "16 of 97 GUC Mwr … (count of 13 Nov, not rechecked)"; :86-89 "(volume and pages to check)", "(journal to check)", "(DOI to check)", "(pages to check)"; :11 references marked † seen by abstract only.

## 4. Not verified (not flagged as wrong)

Why 85. Anything needing the source tables: "181 km 908 times" (REPORT:32), rejected default-depth counts (REPORT:79), ISC-GEM "273 A and 467 C" (RULES D4), 470 327 magnitude values, the Potin-only counts, "ISC Bulletin from 1904" (paper:37) against DATA.md "from 1964". Offshore medians 11 km / 1 km; MAGNITUDES §2 reference errors; paper:108; MAGNITUDES §3 coverage percentages and §7; REPORT:58-59; DECISIONS_NOTE:40-41 (122 events, two thirds); the 32 cases of test 3.
