# Workplan: catalogue merge and magnitude homogenization (A3 – A5)

Written 11 Nov 2026 from the exploration runs X1 and X2, the X2 review, the Candia and Macedo check, and the discussions with S. Ruiz and a second seismologist. Status: **decided on 11 Nov 2026** (section 6); the rules are in `DECISIONS.md`. Briefs: `tasks/A3_matching.md`, `tasks/A5_magnitudes.md`, `tasks/A2b_gccel.md`; the A4 brief follows after A2b.

Where the evidence is:
- `explore/X1/REPORT.md`: matching, location, first magnitude attempt, previews of statistics and of the double seismic zone
- `explore/X2/REPORT.md`: the magnitude method that works
- `explore/X2/review/REVIEW.md`: robustness checks and literature support
- `explore/X2/review/CANDIA_MACEDO.md`: comparison with the latest published Chilean catalogue
- `catalog/SOURCES.md`, `catalog/LITERATURE.md`, `catalog/MAGNITUDE_PRIMER.md`: background

---

## 1. What we are building, in plain words

No single catalogue covers Chile from 1900 to today with good locations and one magnitude scale. Each agency records the same earthquake in its own way: a slightly different time and place, a different depth, and a magnitude of a different type. A merged catalogue has to answer three questions for every earthquake, and each is a separate step:

| question | step | why it is hard |
|---|---|---|
| **Which records are the same earthquake?** | A3, matching | Two agencies may place one event 50 km and several seconds apart. In an aftershock sequence, two different events can be closer than that. |
| **Where was it?** | A4, location and depth | Depth is the weakest number in most catalogues. Many depths are not measured but set to a default (10, 33, 35 km). Depth decides whether an event is crustal, interface or in-slab. |
| **How big was it?** | A5, magnitude | The hazard model needs moment magnitude Mw. Only the larger events have a measured Mw. All others have mb, ML, MS or coda magnitudes that must be converted. |

The order of the steps follows from what each needs:

```
A2  sources frozen (done)
 ├─ A2b  add GCCEL (calibrated locations)  ──┐
 └─ A3   matching: one ID per earthquake     │
      ├─ A5  one Mw per earthquake           │
      └─ A4  one location, depth, mechanism ◄┘
           └─ A6  large events checked by hand → A7 classification → A8 freeze
```

A5 needs only A3 (it uses pairs of magnitudes of the same event). A4 needs A3 and A2b. So A5 and A4 can be done in either order after A3.

## 2. The sources and what each is good for

Frozen on 2026-11-10 (`catalog/sources/`, `MANIFEST.csv`). Box: 15.5–58°S, 60–80°W.

| source | what it is | events in the box | good for | weak at |
|---|---|---|---|---|
| **ISC Bulletin** | The global collection of what every agency reported, re-located by the ISC. Lags two years. | 91 177 (401 452 magnitudes) | The backbone: it holds each agency's own magnitudes (ISC mb, NEIC mb, CSN ML…) for the same event. | ISC's own depths often fixed. |
| **ISC-EHB** | A subset of ISC, re-located with a careful method (Engdahl, van der Hilst, Buland). Depth quality classes L1 (best) to L3 (fixed). | 10 221 (1964–2021) | Teleseismic locations and depths, especially at intermediate depth. | Only M ≳ 5; L3 depths are defaults. |
| **ISC-GEM** | Global instrumental catalogue 1904 on, large events only. Relocated; one Mw per event (measured, or recomputed MS / mb converted). | 4 129 (v13.0) | Location and Mw before 1976. | Its converted Mw near 5.0–5.5 run ~0.25 high (review, row 9). Depths are EHB copies. |
| **Centennial** (Engdahl and Villaseñor 2002) | Global catalogue of large events of the 20th century. Magnitudes compiled from older catalogues, not recomputed. | 661 | S. Ruiz's first choice for large events. Carries intermediate-depth events before 1964 that ISC-GEM lacks. | Not relocated in 1904–1917 and 1943–1955; magnitude types mixed (Pacheco–Sykes Mw, Abe mB). |
| **GCMT** | Moment tensors from long-period waves, 1976 on. | 2 797 | Measured Mw and mechanism. The standard reference. | Few events below Mw 5.2–5.6; reads 0.04–0.10 high below 5.4; centroid depth ~12 km deeper than hypocentres. |
| **ComCat** (USGS) | The USGS catalogue with its preferred solution, plus moment tensors (W-phase Mww, regional Mwr). | 43 985; mechanisms for 2 501 | W-phase Mw down to ~4.5; mechanisms. | 17 % of depths are defaults without a flag. |
| **Potin et al. (2024)** | The CSN catalogue 1982 – 2020-07-16, re-located in 3-D velocity models. | 118 003 | Best location and depth for most of Chile. | Under the flat slab (29–34°S, below ~90 km) it is 25–60 km too deep. Its magnitudes are just the CSN bulletin values. |
| **CSN** (web) and **CSN inside ISC** | The national network's own catalogue, 2020 on (web) and 1988–2025 (inside ISC). | 55 549 and 60 949 | Recent events; CSN ML and Mw. | Not relocated. |
| **GCCEL** (to add, A2b) | "Calibrated" locations of earthquake clusters, with honest errors (1–5 km epicentre, ≤ 5 km depth). | to see | The yardstick to measure every other source's location error. | Covers sequences only, not the whole catalogue. |
| **Cabello et al. (2025)** | Merged Chilean catalogue from 1513. | 227 491 | Events before 1904 only. | Magnitude conversion wrong; rate drifts in time. |
| **Ruiz and Madariaga (2018)** | Review paper of the large Chilean earthquakes. | 69 | Authority for Mw and class of the events it names. | Not a catalogue: no coordinates used; a few dates wrong in its Table 1. |

Not a source, cited only: **Candia and Macedo (2026)**, the most recent published Chilean catalogue. It fails the same tests as Cabello (section 3.3).

## 3. What the exploration taught us

### 3.1 Matching (X1, tier 1)

- **Most records can be linked exactly, without guessing.** The ISC Bulletin stores the other agencies' solutions inside each of its events. So ISC-EHB, ISC-GEM, GCMT, the Centennial, ComCat (97 %) and CSN-inside-ISC link to an ISC event by ID, or by finding their own solution inside it (within 1.5 s and 10 km). Only Potin (no link at all) and the recent CSN web events (ISC lags two years) need matching by time and distance.
- **How far apart can two records of one earthquake be?** Measured on 276 202 known pairs: from 1964 on, 99 % are within 4–8 s and 25–80 km, for every pair of sources. Before 1964 it is 30–150 s and 450–550 km. The spread grows with the age of the event, not with its size.
- **The exact windows matter little.** Over 204 variants the number of M ≥ 4.5 events changes by ±2 %. The one bad choice is a 25 km window (it splits events and misses the known Arauco 2011 duplicate). 5 s is too tight for Potin against ISC-EHB.
- **Later effect:** the matching variant changes the b-value by less than 0.02.

### 3.2 Location and depth (X1, tier 2)

- **Default depths are everywhere.** 20 703 origins sit at their agency's default depth (ISC 35 km; NEIC 10 and 33; ComCat 10 / 33 / 35; ISC-EHB L3 15 km; GCMT 12 km floor; table `explore/X1/tables/t2_default_depths.csv`). They must count as "depth unknown".
- **Potin agrees with ISC-EHB L1 within 2 km down to 150 km**, with one exception: under the Pampean flat slab (29–34°S, below ~90 km) Potin is 25–60 km deeper than ISC-EHB, ComCat and the Slab2 surface. This supports the advice to trust EHB at depth.
- **GCMT centroid depths are ~12 km deeper** than hypocentres. They are not a depth source.
- **ISC-GEM depths are copies of ISC-EHB.** They add nothing independent.
- After all choices, about 12 % of M ≥ 4.5 events have no usable depth (mostly before 1976).
- **Later effect:** the location rule moves 1–3 % of events between depth classes, and b by ≤ 0.01. The exception is the flat-slab cloud.

### 3.3 Magnitudes (X1 tier 3, X2, review)

This is where the catalogue is won or lost. The conversion method changes the number of M ≥ 4.5 events by a factor 0.5 to 1.45, and b by up to 0.4.

**The trap (X1).** The usual way to convert, say, mb to Mw is to take events that have both and fit Mw as a function of mb. But GCMT only measures Mw for larger events (roughly Mw ≥ 5.2–5.6, depending on the year). So at mb 4.5, the only events with a GCMT Mw are the ones that happened to be big for their mb. The fit learns from those and pushes every small event up. Result in X1: a pile of converted events at Mw 4.7–5.0, a b-value of 1.5 at a floor of 5.0, and a Gutenberg–Richter fit that predicted only **12 %** of the observed M ≥ 7 events. Curved forms (exponential, quadratic) made it worse, because they bend to follow the biased low end. Statisticians call this a *truncated regression* (Hausman and Wise 1977); for magnitudes it is described by Lolli et al. (2014, 2023).

**The fix (X2).** Turn the regression round: fit mb as a function of Mw, then invert the line. The selection is on Mw, and a regression is not biased by selection on its input variable. On synthetic data with a GCMT-like cut-off this recovers the true relation; the forward fit is off by more than 0.2 at mb 4.0.

**A second reference for small events.** W-phase and regional moment magnitudes (USGS Mww and Mwr, CSN Mww, CSN regional Mwr, GFZ Mw) are measured Mw too, and reach down to Mw ~4 from 2011 on. After constant offsets they agree with each other within 0.03 (the "W family"). GCMT agrees with them above 5.4 and reads 0.04–0.10 higher below, a known effect (Gasperini et al. 2012; Lolli et al. 2023 discard GCMT below 5.4 when another Mw exists).

**What the new conversion gives (X2 "INV-W", and the review):**

| test | X1 forward fits | Cabello | Candia–Macedo | X2 inverse |
|---|---|---|---|---|
| GR fitted on Mw 5.0–6.5 predicts the observed number of M ≥ 7 (1976–2026); 1.0 is perfect | 0.12 | 0.75 | 0.29 | 0.99–1.12 |
| b changes by this much when the fit floor moves from 4.7 to 5.8 (small is good) | 1.09 | 0.47 | comb | 0.13–0.15 |
| rate of M ≥ 5.5 over 1976–2026 | flat | halves | −20 % | flat (±10 %) |

Other results worth knowing:
- **For small Chilean events, mb ≈ Mw and CSN ML ≈ Mw** (ISC mb 4.5 → Mw 4.44–4.51; ML slope 0.99). Published relations give Mw 4.8–5.0 at mb 4.5; that is the same trap.
- **Straight lines are enough at small M.** A bend is real only where mb saturates (above Mw ~6), and events that large have a measured Mw since 1976.
- **The inverse fit has one condition:** the native magnitude must be reported whatever the size. That holds for ISC mb, NEIC mb and CSN ML. It fails for MS, Moscow mb and Beijing mB (reported mostly for larger events), so their converted values below Mw ~4.8 run 0.2–0.5 high.
- **ISC mb and NEIC mb are nearly the same measurement** (their errors correlate at 0.92). Averaging them does not halve the error.
- **Potin's magnitudes are the CSN bulletin values** (96–100 % identical: `l` = CSN ML, `c` = coda, `W` and `ww` = CSN Mw). They are already in the ISC Bulletin, so Potin adds no magnitude information. Its 1980s coda values are unusable (0.2–1.0 for M 4 events).
- **Possible shift of ISC / NEIC mb before 1990** of about 0.15 at Mw 5.0–5.4. Not yet tested as a split.
- **1964–1975:** rates at M ≥ 5.5 are consistent with later periods; below 5.5 the period is incomplete.
- **CSN web `Ml` equals CSN ML in ISC.** The new `Mlv` (2026) looks ~0.1 higher; keep it a separate type.

---

## 4. The plan, step by step

### Step A2b: add GCCEL (already briefed, `tasks/A2b_gccel.md`)

- **What:** fetch and freeze GCCEL; measure every source's epicentre and depth error against it, by depth range and region.
- **Why:** it is the only source with trustworthy error bars, so it tells us how good Potin, ISC-EHB and the rest really are, and settles the flat-slab question if it has events there.
- **Can run any time before A4.**

### Step A3: matching, one ID per earthquake

**Method.**
1. **Drop non-earthquakes** (quarry blasts, explosions) flagged by the sources.
2. **Backbone by identity.** Link ISC, ISC-EHB, ISC-GEM by ISC event ID. Link GCMT, the Centennial, ComCat and CSN-inside-ISC by finding their own solution inside the ISC event (≤ 1.5 s, ≤ 10 km). GCMT is matched by its reference hypocentre, never by its centroid.
3. **Windows for the rest** (Potin, recent CSN web, the few unlinked records): the measured 99th percentile for that pair of sources, never below 10 s and 50 km. Windows widen for large events (× 1.5 at M 6, × 2 at M 7, × 3 at M 8), using the largest magnitude among the candidates. Magnitude never decides a match.
4. **Before 1964:** identity links first; then 60 s and 300 km, and every such match goes into a list to check by eye (there are few events).
5. **One-to-one assignment** within each pair of sources (each record matched at most once, closest in time and distance overall), built outward from the best-located source.
6. **Second pass for leftovers:** two final events within 10 s and 50 km are merged if they come from different sources; all such cases with M ≥ 5 are listed.
7. **Ruiz and Madariaga events:** dates corrected first (`NOTE_SRuiz`), then matched to a located event (± 1 day, latitude within 2°), one event each; Mejillones 1994 is the event of 1994-12-10.

**Outputs.** `events` (one row per earthquake, with its ID), `links` (every source record with its event ID, time and distance offset, and the rule that linked it), and review lists (ambiguous matches, every merge with M ≥ 6, pre-1964 window matches, unmatched Ruiz–Madariaga events).

**Done when.**
- The four test cases come out right: Maule 2010, Illapel 2015 and Iquique 2014 mainshocks are one event each with their aftershocks kept apart; the Arauco 2011 duplicate is merged.
- Split and false-merge counts are at or below the X1 baseline (121 and 202).
- The number of M ≥ 4.5 events is inside the X1 range (22 300–23 200 by any native magnitude).
- Pablo has gone through the review lists.

### Step A5: one Mw per earthquake

**Method.**

1. **One Mw scale.** Above Mw 5.4, GCMT. Below 5.4, the W family comes before GCMT, as in Lolli et al. (2023), who discard GCMT there when another Mw exists. Offsets of the W-family members are constants measured on our pairs (USGS Mwr +0.10, GFZ +0.03, the others 0). A GCMT value below 5.4 with no W-family partner is treated as Lolli et al. do; if they leave it, it is lowered by its measured offset (0.04–0.10).
2. **Measured Mw wins.** If an event has a measured Mw, that is its magnitude. Order: Ruiz and Madariaga (the events it names); then above 5.4 GCMT → W family, and below 5.4 USGS Mww → CSN regional Mwr / CSN web Mw → USGS Mwr → GFZ → GCMT → CSN Mww. (CSN Mww last because below 5.0 it is only computed for selected events and reads 0.10 high.) Before 1976: Ruiz and Madariaga → ISC-GEM → Centennial → Cabello (before 1904). See decision D7.
3. **Conversion relations for everything else.** For each agency and scale with enough pairs:
   - regress the **native magnitude on Mw**, correct the slope for the error of Mw, then invert;
   - candidates: a straight line; a line with a saturation bend (slope drops above a fitted Mw); each with or without a split by depth (50 km) or period (1990, for ISC and NEIC mb);
   - choose by cross-validation in time blocks with the one-standard-error rule: the simplest form wins unless a more complex one is clearly better. Every candidate contains the straight line as a special case, so the fit "falls back" to it by itself;
   - outside the range of the data: continue along the straight part, and enlarge the error.
4. **One proxy per event.** Without a measured Mw, the event takes the converted value of the first scale it has in a fixed priority list (ISC mb, NEIC mb, CSN ML, …, ordered once by measured scatter; the practice of Allen et al. 2018 and Christophersen et al. 2024). Not eligible below Mw 5: MS, Moscow mb, Beijing mB (they break the condition of the inverse fit). Not eligible at all: Potin's magnitudes (duplicates), coda and duration magnitudes of the 1980s. The error of each scale is the measured scatter of its relation, not an assumed number.
5. **Error per event (σ).** Stored with every Mw: ~0.1 for measured values, ~0.2–0.25 for converted ones. This is what the later rate correction needs (see the note under "For step B").
6. **Dithering.** Native magnitudes are rounded to 0.1. A converted value therefore lands on a comb of values. A small random spread within the native 0.1 bin, with a fixed seed, removes the comb before the final rounding.
7. **Events left without Mw** (X1: 809, Potin-only or old ISC-only events with an unfitted scale): listed; kept in the catalogue flagged "no Mw", not guessed.

**Checks the result must pass ("done when").**
- **b against the fit floor** is flat from 4.7 to 5.8 (range ≤ 0.2).
- **Rates are steady in time:** M ≥ 5.5 within ± 10–15 % across 1976–89, 1990–99, 2000–10, 2011–26.
- **Large-event test:** a Gutenberg–Richter fit on Mw 5.0–6.5 predicts the observed number of M ≥ 7 within the Poisson band (± 16 %), overall and per family (interface, in-slab, crustal).
- **Independent check:** converted values against measured regional Mw on events not used in that fit: within 0.1.
- **No comb, no pile** in the 0.1-bin histogram at 4.5–5.5.
- **Comparison table** against Cabello and Candia–Macedo with the same tests (a paper figure candidate).
- **Sensitivity table:** the same tests for the alternatives not chosen (W family first; weighted mean of proxies; straight lines only), so the paper can state that the choices do not matter much.

**For step B (not part of A5, but decided by it).** Magnitude errors inflate rates, because there are more small events to be scattered upward than large ones to be scattered downward (Tinti and Mulargia 1985). The direction of the correction depends on how the magnitude was obtained. Our values (measured, or from an inverted relation) are of the "measured with error" type. For those, CEUS-SSC (2012, §3.3.1) first shifts each magnitude to its expected value, M − βσ², and then applies its count factor N*; the net effect lowers the rate by exp(−β²σ²/2). Applying N* alone, which is meant for forward-regression values, would raise it instead (Musson 2012 warns about this). With σ = 0.22 the two differ by about ± 13 % in rate. The equations are re-checked against the report when step B is briefed.

### Step A4: one location, depth and mechanism per earthquake

**Method.**
1. **Epicentre and origin time,** first source that has the event:
   Potin (1982 – 2020-07, 18–46°S) → GCCEL → ISC-EHB L1 / L2 → ISC → ComCat → CSN.
   Before 1964: ISC-GEM, with the Centennial where it is EHB-relocated (decision D7).
2. **Depth,** first source in the same order with a *measured* depth. The aim is to keep fixed depths out wherever possible: a depth flagged fixed, or equal to its agency's default (table from X1, refreshed on the final data), is skipped as long as any other source has a measured depth, and counts as unknown only when none has. GCMT centroid depth is never used.
3. **No regional exceptions.** Potin keeps priority under the flat slab too. Its too-deep events there are handled by one general rule in A7: an event located below the slab is in-slab. The bias is measured against GCCEL (A2b) and stated in the paper.
4. **Depth error per event:** from the source's measured spread against GCCEL / ISC-EHB L1, by depth range and region. Needed by the classification (A7).
5. **Unknown depth** is kept as unknown, with a flag. No filling from Slab2 at this step.
6. **Mechanism:** ComCat moment tensor, then GCMT (as decided). Scalar moments are checked against the tensor (the Maule W-phase product has a wrong one). ComCat products before 1996 are focal mechanisms without moment.
7. **Domain cut** (south of 17°S, etc.) on the final location only.

**Done when.**
- Every event has a source named for each property.
- Share of unknown depths reported by period and region (X1: 12 % of M ≥ 4.5).
- Share of events whose final depth is fixed or default: reported per source and period, and as low as the sources allow.
- Sections at six latitudes drawn; the Potin cloud at 31°S is flagged, not corrected.
- The location rule scores at least as well against GCCEL as the alternatives.

### After that

- **A6, large events by hand:** every M ≥ 7 where sources differ by ≥ 0.3 in Mw or ≥ 30 km in depth; the Ruiz–Madariaga review list; known oddities (ISC-GEM gives the 1960-05-22 Valdivia foreshock Mw 8.72 against 7.9 elsewhere; Aysén 1960 Mw 7.2 or 7.7).
- **A7, classification,** and **A8, freeze.** Not part of this workplan.

---

## 5. How to run it in Claude Code

**Recommendation: one session per step, not one long session.** Each step ends with something Pablo must look at (review lists, test tables) before the next one builds on it, and a fresh session reads the files cleanly instead of carrying a long history.

| order | session | brief | Pablo checks before the next |
|---|---|---|---|
| 1 | A3 matching | `tasks/A3_matching.md` (ready) | the review lists, the four test cases |
| 2 | A5 magnitudes | `tasks/A5_magnitudes.md` (ready) | the test table and the sensitivity table |
| any time before 4 | A2b GCCEL | `tasks/A2b_gccel.md` (ready) | the benchmark report |
| 4 | A4 location | `tasks/A4_location.md` (to write, after A2b) | the sections, unknown-depth shares |

Each brief tells Claude Code to turn the exploration code (`explore/X1`, `explore/X2`) into clean, tested modules under `catalog/` (`match.py`, `magnitude.py`, `locate.py`), not to import from `explore/`. Every run is recorded in `DATA.md`.

Start a session with: *"Read `CLAUDE.md`, then do the task in `tasks/<brief>.md`."*

## 6. Choices (decided 11 Nov 2026)

| # | choice | decision | note |
|---|---|---|---|
| D1 / D2 | Mw scale and order of measured Mw | Above 5.4 GCMT first. Below 5.4 the W-phase and regional Mw before GCMT. | Follows Lolli et al. (2023); GCMT too high below 5.0–5.5 (Gasperini et al. 2012). |
| D3 | Several proxies for one event | Fixed priority list of scales, ordered by measured scatter; MS, Moscow mb, Beijing mB not below Mw 5. | As Allen et al. (2018), Christophersen et al. (2024). A5 reports the weighted mean as a comparison. |
| D4 | Form of the relations | Inverse regression; straight line or line with saturation bend, by cross-validation; period split at 1990 tested for mb. | The inverse step is new and must be argued in the paper. |
| D5 | Rate correction for magnitude error | CEUS-SSC (2012, §3.3.1) two steps for observed magnitudes. | Applied in step B; equations re-checked there. |
| D6 | Matching | Identity links, then measured windows (floor 10 s / 50 km), one-to-one, second pass. | – |
| D7 | Before 1976, magnitude | ISC-GEM first, Centennial fills; M ≥ 7 differences ≥ 0.3 to A6. | Centennial first if S. Ruiz says so (question 1 of the note). |
| D8 | Location and depth | Local catalogue first everywhere; no exceptions; nothing removed. Events below the slab are in-slab (A7). | Potin's flat-slab bias stated as a limitation. |
| D9 | Fixed and default depths | Avoided wherever any source has a measured depth; unknown otherwise. | The main aim of A4. |
| D10 | Potin magnitudes | Not used. | They are the CSN bulletin values. |
| D11 | Candia and Macedo (2026) | Cited and compared; not a source. | – |

## 7. Glossary

- **Origin:** one agency's solution for an earthquake (time, place, depth). One earthquake has several origins.
- **Hypocentre / centroid:** where the rupture starts / the centre of the moment release. GCMT gives centroids, which are later and, in Chile, deeper.
- **Fixed or default depth:** a depth the agency set by rule because the data could not resolve it.
- **Native magnitude:** the magnitude as the agency measured it (mb, ML, MS, coda…), before any conversion.
- **Measured (direct) Mw:** from a moment tensor (GCMT, W-phase Mww, regional Mwr). **Proxy Mw:** converted from a native magnitude.
- **mb / MS / ML / Mc, Md:** body-wave / surface-wave / local / coda-duration magnitudes. mb saturates above ~6, MS above ~8.
- **Forward / inverse regression:** fitting Mw from the native value / fitting the native value from Mw and inverting.
- **Censoring, truncation:** when one of the two magnitudes exists only above some size, so the pairs are a biased sample.
- **Errors-in-variables (chi-square, orthogonal) regression:** a fit that allows for error in both magnitudes.
- **Cross-validation, one-standard-error rule:** fit on some years, test on others; prefer the simplest form whose test score is within the noise of the best.
- **Triple collocation:** estimating each scale's error from events measured by three scales.
- **Heaping, dithering:** piles of events at certain 0.1 values after conversion; a small random spread that removes them.
- **b-value against floor:** b fitted above different minimum magnitudes. In a homogeneous, complete catalogue it does not change.
- **Declustering:** removing aftershocks and foreshocks (here Gardner–Knopoff) to test rates of independent events.
- **Tinti–Mulargia correction:** correction of rates for the upward scatter caused by magnitude errors.

## 8. References

DOIs as checked in `explore/X2/review/REVIEW.md`; entries without a DOI are in `REFERENCES.md` / `LITERATURE.md` or still need checking there.

Catalogues
- Bergman, E. A., et al. (2023). A global catalog of calibrated earthquake locations. SRL 94(1), 485–495. doi:10.1785/0220220217. Data: doi:10.31905/MFDY4QHD.
- Cabello et al. (2025). Integrated seismic catalogue for Chile. (See REFERENCES.md.)
- Candia, G., Macedo, J. (2026). A homogenized and declustered earthquake catalog for continental Chile. SRL. doi:10.1785/0220250449.
- Di Giacomo, D., et al. (2015, 2018). ISC-GEM: magnitudes; extension. (See REFERENCES.md.)
- Ekström, G., et al. (2012). The global CMT project 2004–2010.
- Engdahl, E. R., Villaseñor, A. (2002). Global seismicity: 1900–1999 (Centennial catalogue).
- Potin, B., et al. (2024). A revised Chilean seismic catalog from 1982 to mid-2020. SRL 96(1), 484–498. doi:10.1785/0220240047.
- Riquelme, S., et al. (2018). W-phase real-time implementation and network expansion in Chile.
- Ruiz, S., Madariaga, R. (2018). Historical and recent large megathrust earthquakes in Chile.
- Weston, J., et al. (2018). ISC-EHB.

Magnitude conversion
- Castellaro, S., et al. (2006). Regression problems for magnitudes.
- Christophersen, A., et al. (2024). NZ NSHM 2022 catalogue magnitudes. doi:10.1785/0120230169. (The counter-position: forward OLS, valid with a complete reference.)
- Gasperini, P., et al. (2012). GJI 190, 1733. (GCMT too high below Mw 5.0–5.5; as cited by Lolli et al.)
- Gasperini, P., et al. (2013). SRL 84, 932. doi:10.1785/0220130105. (mb ≈ Mw for small events.)
- Gasperini, P., et al. (2025). Equation error. doi:10.1785/0120250007.
- Hausman, J., Wise, D. (1977). doi:10.2307/1912682; Heckman, J. (1979). doi:10.2307/1912352. (Truncated regression.)
- Llenos, A., et al. (2026). doi:10.1785/0220250231. (Conversion choice moves hazard-model rates.)
- Lolli, B., et al. (2014). doi:10.1093/gji/ggu264; Lolli, B., et al. (2023). doi:10.1093/gji/ggad164.
- Osborne, C. (1991). Statistical calibration. doi:10.2307/1403690.
- Rovida, A., et al. (2020). CPTI15. doi:10.1007/s10518-020-00818-y. (Measured Mw always preferred over proxies.)
- Scordilis, E. (2006); Weatherill, G., et al. (2016). (Published relations, used as checks only.)

Magnitude error and rates
- CEUS-SSC (EPRI / DOE / NRC 2012), NUREG-2115, §3.3.1.
- Mueller, C. (2019). doi:10.1785/0220170108.
- Musson, R. (2012). doi:10.1785/0120110224.
- Tinti, S., Mulargia, F. (1985). doi:10.1785/BSSA0750061681.

Homogeneity tests
- Habermann, R. (1991). doi:10.1016/0040-1951(91)90337-R.
- Tormann, T., et al. (2010). doi:10.1785/0120090124.
- Zúñiga, F., Wiemer, S. (1999). doi:10.1007/s000240050285.

Not yet verified, check before citing: Felzer (2008); the ESHM20 and Canada conversion rules.
