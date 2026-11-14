# X5: six ways to score the classes, each put through six tests

14 Nov 2026 (first version 13 Nov). Exploration for A7: nothing under `catalog/` was changed; run `2026-11-13j` stays the current classification.

Input: `catalog/merged/catalog_2026-11-13e.csv`. Events tested: the 5 438 of Mw ≥ 4.5 in the domain with a measured depth over a slab top ≤ 50 km (1 270 with a mechanism).
New data: catalogue of Riedel-Hornig et al. (2026), Zenodo 10.5281/zenodo.15284376, primary catalogue only (101 MB, md5 33645115…, downloaded 14 Nov into `data/riedel_hornig_2026-11-14/`; not for git).
Code: `x5_lib.py` (Kagan angle), `x5_models.py` (models), `x5_riedel.py` (matching), `x5_synth.py` (synthetic catalogues), `x5_check.py` (all tests, about 8 min). Tables in `tables/`; the full table of diagnostics is `tables/x5_diagnostics.csv`.

## 1. What comes out

1. **No method can class more than about two thirds of these events correctly.** On synthetic catalogues with known classes and our catalogued errors, every method gets 62–65 % right; with errors 0.7 times as large, 66–71 %. The limit is the depth error against the distances between the classes, not the rule.
2. **The methods that carry the depth error (C and E) are the best or equal best on every test except the 24 literature events,** where the current run (A) is slightly ahead because it lets a thrust mechanism override the depth.
3. **The current run (A) fails the test you raised:** it gives a thrust-like event that is not interface a score of 1 by construction (0.89 for the 56 real ones far from the slab). E gives 0.62 on the synthetic ones and 0.32 on the real ones; C 0.49 and 0.15.
4. **Against the Riedel-Hornig catalogue the verdict depends on what counts as interface.** By their class (within about 5 km of Slab2 in their depths) every method gives twice their interface. By their depths with the range the thrust events actually occupy (−5 to +15 km), C and E are within 3 % and well calibrated. The two readings bracket the truth; section 4 says why I trust the second more.
5. **Proposal: E.** If you prefer the method with no number of our own in it, C.

## 2. The methods

| | method | mechanism | depth error |
|---|---|---|---|
| A | current run `j` (band ± 15 km) | a thrust on the contact is interface whatever the depth; another mechanism excludes | yes |
| A2 | run `j` rules | only excludes | yes |
| B | USGS scores as published (Haynie et al. 2026), re-implemented | lowers the interface score beyond a Kagan angle of 30° | no |
| C | B averaged over the event's depth error | as B | yes |
| E | C, and a thrust-like mechanism multiplies the interface odds by 3.3 | both ways, as evidence | yes |
| D | three normal distributions fitted without labels | bins of the Kagan angle | through the fitted widths |

B departs from the paper in two points: the Moho is fixed at 40 km (their CRUST1.0 grid is not on disk) and their ramp between the Moho and the interface zone is left out. The 3.3 in E is measured on our events with calibrated or depth-phase depths (thrust-like: 75 % within 5 km of the slab surface, 23 % beyond 15 km).

## 3. The tests and the diagnostics

**The diagnostics.** *Right*: share of events whose largest score is the true class. *Brier*: mean squared distance between the scores and the truth (0 perfect; over three classes a blind guess gives about 0.67, over interface alone 0.25). *Total*: summed interface score over the number of interface events (1 = unbiased rates). *AUC*: how well the score ranks interface above the rest (0.5 none, 1 perfect). *Gap*: mean distance between a score and the share of events that turn out interface at that score (0 = a score of 0.7 means 70 %).

| test | diagnostic | A | A2 | B | C | **E** | D |
|---|---|---|---|---|---|---|---|
| **1 Literature** (24 events, all large) | right | 22 | 20 | 18 | 20 | **21** | 21 |
| | Brier | 0.151 | 0.234 | 0.430 | 0.228 | **0.167** | 0.224 |
| **2 Mechanisms hidden** (1 270): score by depth, compare with thrust-like or not | Brier | 0.196 | 0.196 | 0.237 | 0.183 | **0.183** | 0.179 |
| | total | 1.06 | 1.06 | 1.09 | 0.98 | **0.98** | 1.08 |
| | AUC | 0.70 | 0.70 | 0.66 | 0.70 | **0.70** | 0.69 |
| | gap | 0.15 | 0.15 | 0.24 | 0.08 | **0.08** | 0.08 |
| **3 Riedel-Hornig class** (306; their interface 116) | right | 168 | 170 | 173 | 178 | **176** | 162 |
| | Brier | 0.825 | 0.775 | 0.812 | 0.626 | **0.656** | 0.665 |
| | total | 2.04 | 1.97 | 1.99 | 1.79 | **1.85** | 1.84 |
| | AUC | 0.66 | 0.68 | 0.67 | 0.72 | **0.73** | 0.73 |
| – of them without mechanism (210, nearly all Mw < 5.5) | Brier | 0.805 | 0.805 | 0.862 | 0.660 | **0.660** | 0.645 |
| | total | 1.99 | 1.99 | 1.96 | 1.79 | **1.79** | 1.73 |
| **3d Riedel-Hornig depth, −5 to +15 km** (306; interface 214) | Brier | 0.142 | 0.128 | 0.129 | 0.105 | **0.104** | 0.118 |
| | total | 1.10 | 1.07 | 1.08 | 0.97 | **1.00** | 1.00 |
| | AUC | 0.79 | 0.83 | 0.85 | 0.89 | **0.89** | 0.87 |
| | gap | 0.14 | 0.11 | 0.12 | 0.04 | **0.02** | 0.11 |
| – of them without mechanism (210; interface 163) | Brier | 0.102 | 0.102 | 0.127 | 0.100 | **0.100** | 0.114 |
| | total | 1.03 | 1.03 | 1.01 | 0.92 | **0.92** | 0.89 |
| **5 Synthetic, errors as catalogued** | right | 65 % | 63 % | 62 % | 63 % | **64 %** | 64 % |
| | Brier | 0.568 | 0.600 | 0.722 | 0.545 | **0.527** | 0.540 |
| | total interface / in-slab / crustal | 1.02 / 0.88 / 1.22 | 0.95 / 0.98 / 1.38 | 1.00 / 0.89 / 1.32 | 0.95 / 0.98 / 1.37 | **0.98 / 0.95 / 1.29** | 1.16 / 0.56 / 1.35 |
| | score of thrust-like events that are not interface | 1.00 | 0.51 | 0.50 | 0.49 | **0.62** | 0.70 |
| **5 Synthetic, errors × 0.7** | right | 71 % | 70 % | 70 % | 70 % | **71 %** | 66 % |
| | Brier | 0.475 | 0.483 | 0.572 | 0.442 | **0.431** | 0.483 |
| **5 Synthetic, 30 % thrusts off the interface** | Brier | 0.590 | 0.607 | 0.730 | 0.550 | **0.535** | 0.551 |
| **6 Real thrust-like events > 20 km from the slab** (56) | interface score | 0.89 | 0.10 | 0.00 | 0.15 | **0.32** | 0.59 |
| **6 Other mechanisms within 5 km of the slab** | interface score | 0.40 | 0.40 | 0.62 | 0.57 | 0.57 | 0.60 |
| Totals over the 5 438 events | interface / in-slab / crustal | 3 869 / 1 242 / 327 | 3 716 / 1 358 / 364 | 3 842 / 1 251 / 344 | 3 524 / 1 484 / 430 | **3 629 / 1 410 / 399** | 3 628 / 1 552 / 258 |
| | interface, Mw ≥ 5.5 | 610.6 | 543.9 | 611.8 | 546.6 | **591.0** | 608.8 |

Test 4 (reliability by score bin) is `tables/x5_reliability.csv`; the "gap" rows above summarise it.

**What each test can and cannot show.**
1. *Literature:* independent of everything we do, but 24 events, all large, most of them thrusts.
2. *Mechanisms hidden:* many events; tests only the depth half of a method.
3. *Riedel-Hornig:* the only test of small events without a mechanism (210). Their depths are good (median error 2.7 km); their class is a narrow band on Slab2.
5. *Synthetic:* the truth is known and the errors can be turned up and down; it is only as good as its assumptions (interface 60 %, in-slab 30 %, crustal 10 %; in-slab events 2 km and more below the surface; 15 or 30 % of non-interface events thrust-like).
6. *Thrusts off the slab:* shows the behaviour you worried about; the truth for the 56 real ones is unknown.

## 4. The Riedel-Hornig comparison in detail

853 of our 1 274 events of 2017–2021 match (15 s, 100 km; none south of 43° S in their primary catalogue); 306 are over the shallow slab with one of the three classes, 278 of them below Mw 5.5.

**Where the events sit in their depths** (`tables/x5_riedel_position.csv`):

| | events | their depth − Slab2: median, scatter | our depth − Slab2: median, scatter |
|---|---|---|---|
| thrust-like | 58 | +4.7 km, 4.2 km | +3.2 km, 6.8 km |
| other mechanisms | 38 | +17.1 km, 16.6 km | +12.7 km, 8.7 km |
| no mechanism | 210 | +5.7 km, 7.1 km | +3.4 km, 7.8 km |

- **With good depths the classes do separate:** thrusts sit in a 4 km wide layer, other mechanisms 17 km below the surface. Only 4 of 38 other mechanisms are within 5 km.
- **The thrust layer is centred 5 km below Slab2, not on it.** Their class takes roughly −5 to +5 km as interface, so 27 of the 58 thrust-like events are "in-slab" for them, 22 of those at 5–15 km below. Either Slab2 is about 5 km shallow there or these are thrusts in the top of the slab; their catalogue cannot tell and neither can ours. This is why I read their class as a lower bound on the interface, and the −5 to +15 km range as the fairer reference.
- **By their class our interface is twice theirs** for every method (1.8 to 2.0), also for the small events without a mechanism. Of the 176 events they call in-slab, our methods put 100 to 116 in the interface. If their class is right, our interface rates at Mw 4.5–5.5 are a factor of two high at 18–43° S in 2017–2021. This is the largest open point of the classification.

**Depths** (`tables/x5_riedel_depths.csv`). Over the shallow slab our depths agree with theirs: Potin −2.0 km (scatter 3.5), CSN −0.8 (6.3), ISC-EHB L1 −4.5 (4.1), L2 −6.8 (7.5); 74 % within our σ. Where the slab is deeper the teleseismic depths are far shallower than theirs: ISC-EHB L1 −10.7 km (scatter 11.9), L2 −24.1 (17.9), ISC −19.0 (16.9), against Potin −4.1 (3.7). The project notes already say their depths east of central Chile run deep without Argentine stations, so this is not a verdict on ISC-EHB, but it is worth a look before the in-slab depths are used.

## 5. Why E, and what it costs

- E follows the USGS method and adds the two steps its authors name as future work (the event depth error; a reward for thrust mechanisms).
- It has one number of our own, the 3.3, measured on the catalogue it is applied to. Dropping it gives C, which loses on the literature events (Brier 0.228 against 0.167) and on nothing else.
- Under E, Valparaíso 1985 scores 0.26 interface (hypocentre 21 km below the surface) and keeps its class from the literature; Maule 2010 0.96, Iquique 2014 0.92, Valparaíso 2017 0.70.
- All methods overstate the crustal total on the synthetic catalogues by 22–38 %: shallow interface events scattered upward are read as forearc crust. This applies to the current run too.

## 6. Limits

- B is my re-implementation; the USGS code was not run.
- One synthetic design, three scenarios, three draws each.
- The Riedel-Hornig comparison covers five years and 18–43° S.
- E is not in `catalog/classify.py`.

## 7. The mechanism test as a skewed Kagan angle (methods F0, F, F1; 14 Nov, second part)

Pablo's rule: the interface has one mechanism, the subduction plane slipping in the convergence direction; another plane, sense or rake is in-slab or crustal. The Kagan angle cannot apply it, because it weighs a tilted plane and a turned rake the same (plane 30° off with rake 90°, and exact plane with rake 120°, both give 30°).

**Equation.** At the epicentre, n₀ is the unit normal of the Slab2 plane and s₀ the motion of the upper plate (azimuth 257°, fixed) projected on that plane. A double couple with normal n and slip s has four equivalent descriptions (a, b): (n, s), (−n, −s), (s, n), (−s, −n). For each:

- swing σ = arccos(a · n₀): the tilt of the plane;
- twist τ = arccos(b′ · s₀), where b′ is b after the smallest rotation that takes a onto n₀: the turn of the slip in the plane;
- m = min over the four of √((σ / σ₀)² + (τ / τ₀)²), with σ₀ = 20°, τ₀ = 45°.

Interface is possible where m ≤ 1. The Kagan angle Φ to the same reference obeys cos(Φ/2) = max over the four of cos(σ/2) cos(τ/2), so Φ² ≈ σ² + τ² for small angles: m is the Kagan angle with its two axes scaled apart. Code: `x5_skew.py`.

**Checks of the math** (20 000 random mechanism and slab pairs): swing and twist equal an independent quaternion decomposition (scipy) to 10⁻¹¹ degrees; the identity with the Kagan angle holds to 10⁻⁹ and `x5_lib.kagan` equals the smallest total rotation to 10⁻¹³; m is the same from either nodal plane; m = 0 for the reference and its conjugate plane, 4 for the reversed slip; a change of dip alone gives swing = the change and twist 0, of rake alone the reverse.

**Methods.** F0: C with interface 0 outside the ellipse. F: F0 with the interface odds × 3.9 inside (share inside the ellipse 0.74 within 5 km of the slab against 0.19 beyond 15 km, best depths). F1: as F, with the weight falling from 1 at m = 1 to 0 at m = 1.5.

| test | measure | A | C | E | F0 | F | F1 |
|---|---|---|---|---|---|---|---|
| 1 literature, 24 | right | 22 | 20 | 21 | 21 | 22 | 22 |
| | Brier | 0.151 | 0.228 | 0.167 | 0.187 | 0.120 | 0.130 |
| 2 mechanisms hidden | Brier | 0.196 | 0.183 | 0.183 | 0.183 | 0.183 | 0.183 |
| 3 Riedel-Hornig class | Brier | 0.825 | 0.626 | 0.656 | 0.603 | 0.635 | 0.637 |
| | total | 2.04 | 1.79 | 1.85 | 1.70 | 1.77 | 1.79 |
| 3d Riedel-Hornig depth −5 to +15 km | Brier | 0.142 | 0.105 | 0.104 | 0.106 | 0.107 | 0.098 |
| | total | 1.10 | 0.97 | 1.00 | 0.92 | 0.96 | 0.97 |
| 5 synthetic | right | 65.2 % | 62.7 % | 64.1 % | 62.1 % | 63.4 % | 64.0 % |
| | Brier | 0.568 | 0.545 | 0.527 | 0.562 | 0.547 | 0.536 |
| | interface total / true | 1.02 | 0.95 | 0.98 | 0.90 | 0.94 | 0.95 |
| 6 mechanism outside the ellipse, within 15 km of the slab (243) | summed interface | 110.0 | 132.4 | 140.7 | 0 | 0 | 52.8 |
| 6 inside the ellipse, > 20 km from the slab | mean interface | 0.94 | 0.14 | 0.30 | 0.15 | 0.34 | 0.34 |
| all 5 438 events | summed interface | 3 869 | 3 524 | 3 629 | 3 384 | 3 493 | 3 548 |
| | of it Mw ≥ 5.5 | 611 | 547 | 591 | 499 | 546 | 562 |

The scores of A to E are unchanged from section 3. Tests 2 and 3d define "thrust-like" by the Kagan angle (≤ 30°), which leans towards E. In the synthetic catalogues interface events carry real mechanisms of the thrust-like kind, some of them outside the ellipse, so the F methods lose interface there by construction.

**Events outside the ellipse inside the buffer** (`tables/x5_buffer_other.csv`, 243): 19 have a Riedel-Hornig class: 16 in-slab, 1 crustal, 2 interface. Of events of Mw ≥ 7 with a mechanism all pass (m ≤ 0.9) except Pichilemu 2010-03-11 (m 3.9, crustal in the literature) and 1985-03-04 00:32 Mw 7.4 (m 3.0), two hours after the Valparaíso mainshock.

**Where the edge is.** By depth, events just outside behave like those inside:

| m | events | best depths | of them within 10 km of the slab | beyond 15 km | Riedel-Hornig class |
|---|---|---|---|---|---|
| 0–0.5 | 390 | 128 | 0.82 | 0.02 | 9 interface, 8 in-slab, 2 crustal |
| 0.5–1 | 488 | 108 | 0.74 | 0.07 | 21 interface, 18 in-slab, 1 crustal |
| 1–1.5 | 122 | 46 | 0.70 | 0.20 | 1 interface, 3 in-slab |
| 1.5–2.5 | 141 | 58 | 0.52 | 0.36 | 1 interface, 21 in-slab |
| > 2.5 | 129 | 42 | 0.50 | 0.31 | 10 in-slab, 1 crustal |

**Limits found.**
- The tolerances 20° and 45° come from the 14 literature interface events (swing up to 12°, twist up to 15°) and the old rule; they are not fitted. Events inside: 763 at 15°/45°, 878 at 20°/45°, 938 at 25°/45°, 978 at 30°/45°. The 14 literature interface events pass every setting.
- The share inside the ellipse grows with magnitude (within 10 km of the slab: 0.61 at Mw < 5, 0.78–0.80 at 5–6.5, 0.91 above) and is low where the slab top is above 15 km (0.55; Slab2 dip 10°). Part of what falls outside is mechanism error, not another fault.
- The convergence azimuth is one value: ± 5° moves 17–21 of the 1 270 events across the edge, ± 10° 29–54.
- The odds factor rests on 151 and 53 events and on depth as a stand-in for the class.
- In the depth step only the event depth error is a distribution; the Slab2 error is inside the fixed ± 15 km.

## 8. F1 in `catalog/classify.py` (14 Nov)

Pablo chose F1. It is now the default of `catalog/classify.py` (`MECH = "ellipse"`): `skew()` gives the measure m, `by_depth()` the scores averaged over the depth error, `lift()` the odds factor. It replaces the depth band and the thrust rule for events with a measured depth over the shallow slab (slab top ≤ 50 km); events without depth take the shares of their bin, with the same factor from the mechanism. Everything else is as in run `j`. With `hard=None` the weights equal the F1 scores of section 7 on all 5 438 events (largest difference 0).

`classify.py` also turns a weight of 0.8 or more into 1 (`HARD`, in DECISIONS). F1 was tested without it. Model G is F1 with it:

| test | measure | A run j | F1 | G (F1, 0.8 becomes 1) |
|---|---|---|---|---|
| 1 literature | right of 24 | 22 | 22 | 22 |
| | Brier | 0.151 | 0.130 | 0.127 |
| 2 mechanisms hidden | Brier | 0.196 | 0.183 | 0.194 |
| | calibration gap | 0.148 | 0.082 | 0.145 |
| 3 Riedel-Hornig class | Brier | 0.825 | 0.637 | 0.726 |
| | total | 2.04 | 1.79 | 1.93 |
| 3d Riedel-Hornig depth | Brier | 0.142 | 0.098 | 0.105 |
| | total | 1.10 | 0.97 | 1.05 |
| | calibration gap | 0.139 | 0.037 | 0.098 |
| 5 synthetic | right | 65.2 % | 64.0 % | 64.0 % |
| | Brier | 0.568 | 0.536 | 0.575 |
| | interface total / true | 1.02 | 0.95 | 0.99 |
| shallow slab, 5 438 events | summed interface | 3 869 | 3 548 | 3 749 |

Making 0.8 into 1 costs on every per-event score except the 24 literature events, and adds 6 % interface. It keeps the number of split events low. On the whole catalogue (Mw ≥ 4.5 in the domain, 14 279 events):

| | interface | in-slab | crustal | split events | interface, Mw ≥ 5.5 |
|---|---|---|---|---|---|
| run `j` | 4 702.9 | 7 913.3 | 1 149.8 | 2 817 | 809.0 |
| F1 with 0.8 becomes 1 | 4 564.0 | 8 038.6 | 1 163.3 | 3 030 | 783.7 |
| F1, weights kept | 4 329.2 | 8 170.4 | 1 266.5 | 6 280 | 751.3 |

Two events of Mw ≥ 7 that run `j` made interface by the thrust alone are now split, with or without the 0.8 rule, because their depths are far above the slab: 2001-07-07 Mw 7.6 (depth 25 ± 10 km, slab at 40 km; interface 0.77, crustal 0.23) and 2015-09-16 23:18 Mw 7.1 (depth 5 ± 10 km, slab at 29 km; interface 0.58, crustal 0.41). Both have m near 0.5.
