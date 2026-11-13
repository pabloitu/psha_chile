# X4: exploratory classification of the merged catalogue

First written 12 Nov 2026; numbers brought to the catalogue of 13 Nov on 13 Nov (section 0). Exploration for A7: nothing under `catalog/` was changed by this task.
Input: `catalog/merged/catalog_2026-11-13.csv` (A4 second rule, A5 fourth run): 204 956 events, 200 427 in the domain, **14 234 with Mw ≥ 4.5 in the domain** (12 374 with a measured depth, 2 670 with a mechanism). Geometry: Slab2 (`data/slab_2.0`, top, thickness, dip, strike), `sam_nazca_trench.shp`, `sam_antarctica_trench.shp`, arc polygon `data/intraarc.shp`.

Name clash: `explore/X4/` already held the surface-wave check (`x4_*.py`, `tables/x4_*`). Everything of this task carries the prefix `x4b_`.

## 0. Revisions

**After Pablo's answers (12 Nov, evening).**
- **Arc polygon:** the one modified last, `data/intraarc.shp` (25 Nov 2025; `data/shapefiles/intra_arc.shp` is of 15 Oct 2025). It is the one A4 and this task use.
- **Ruiz and Madariaga (2018) is authoritative for class:** the 56 events with a class in the paper take it after the rules, in every variant (`rule = rm18`; `cls_auto` keeps the rule's class). All numbers below include this.
- **Double seismic zone: withdrawn from this task.** The two-plane test was run without removing the Jujuy nest, so its detections at 22–25° S are not valid; the test, its tables and figures are removed. The planes are handled in the in-slab source model.
- **In-slab classes:** `intraslab_shallow` (slab top above 50 km at the epicentre), `intraslab_intermediate`, `jujuy_nest` (within 0.8° of 66.9° W, 24.0° S, depth 170–320 km, measured depth; the cat_handler_2 definition).

**After the A4 and A5 rerun (13 Nov).** The findings of the first version (`HANDOFF_A3-A5.md`) were checked in the A3–A5 conversation and A4 and A5 were rerun; section 7 says what was done with each. The three scripts were rerun on the new catalogue without any change of rule (only `RUN` and the date of the Ruiz and Madariaga file). What moved against the first version:

| Mw ≥ 4.5 in the domain | 11 Nov | 13 Nov |
|---|---|---|
| events | 14 157 | 14 234 |
| measured depth | 12 413 | 12 374 |
| interface | 3 893 | 3 896 |
| in-slab | 7 076 | 7 131 |
| crustal (four classes) | 1 019 | 967 |
| outer rise | 511 | 504 |
| unknown depth | 1 552 | 1 644 |
| unknown depth, Mw ≥ 7 | 54 | 66 |
| class depends on the variant | 2 195 | 2 173 |

- Unknown depth grew because depths before 1964 on a multiple of 5 km are no longer called measured. Twelve more events of Mw ≥ 7 have no class.
- The depth σ now has a floor of 5 km (10 km offshore), so the "with σ" variants widen the band for every source and not mainly for Potin.
- Arica 1987 is back at 69.7 km and in-slab; Atacama 1922 and the Valdivia foreshock have no depth any more instead of a wrong one.

## 1. Summary

1. **The class of 2 173 of the 14 234 events (15 %) depends on the rule variant**; 337 of 1 941 at Mw ≥ 5.5 and 11 of 153 at Mw ≥ 7. Nearly all of it is the interface against in-slab and against forearc crust.
2. **The band width matters most** (± 10 → ± 20 km: 1 178 events, 100 of Mw ≥ 5.5, 4 of Mw ≥ 7). Adding the depth σ moves 669, mechanisms 265 (but 119 of Mw ≥ 5.5, where most mechanisms are), "below the plate" only 80 and none above Mw 5.9.
3. **Unknown depth is the largest problem for the large events: 66 of the 153 events with Mw ≥ 7 (65 of them before 1964) and 384 of 1 941 with Mw ≥ 5.5 have no class**, after the 20 that Ruiz and Madariaga settle (19 of Mw ≥ 7).
4. **Great interface earthquakes that are not interface under a rule on catalogue depth alone:** Concepción 1960-05-21 (forearc crust), La Ligua 1971 (in-slab), Copiapó 1918 (outer rise); Valparaíso 1985 is interface only through its mechanism. Atacama 1922, the Valdivia foreshock and Valdivia 1960 now have no depth. All are set from the paper; the same errors remain for large events the paper does not name. Section 6.
5. **In-slab classes (Mw ≥ 4.5):** 1 211 shallow, 5 011 intermediate, 909 Jujuy nest; at Mw ≥ 7: 5, 21 and 3.
6. **Against the old classifier the family agrees for 91 % of the events both classify (90 % at Mw ≥ 5.5)**, against Candia and Macedo for 88 %. Against Ruiz and Madariaga the rule alone gives 31 right, 5 wrong, 20 without depth; 3 have no class in the paper.
7. **The upstream errors of the first version are mostly corrected** (section 7). What remains: Potin depths near the coast that are close to 0 km or far below the slab (180 and 56 events), the CSN regional Mw where only one other value exists, and the historical epicentres.

Figures: `figs/x4b_maps.png`, `x4b_sections.png`, `x4b_variants.png`.

## 2. Rules

Code `x4b_classify.py`, settings at the top. Rules in order (`rule` column):

| rule | condition | class |
|---|---|---|
| outer_rise | west of the Nazca trench (Antarctic trench south of 46.15° S), any depth, also unknown | outer rise |
| unk_mech | depth unknown, thrust on the interface plane, slab top ≤ 65 km (mechanism variants only) | interface |
| unk | depth unknown | unknown depth |
| pat | south of 46.15° S, or no Slab2 south of 44° S outside the arc; depth ≤ 50 km | crustal Patagonia |
| noslab | no Slab2 node within 15 km; depth ≤ 50 km | crustal forearc / arc / backarc by the arc polygon |
| below | deeper than top + Slab2 thickness (+ σ) | in-slab, or "below slab" |
| mech_if | thrust on the interface plane, slab top ≤ 65 km, within the band + 10 km | interface |
| band_other_mech | in the band, slab top ≤ 50 km, another mechanism | in-slab below the top, crustal above |
| band | within ± W of the slab top, slab top ≤ 50 km | interface |
| above | above the band, depth ≤ 50 km | crustal forearc / arc / backarc |
| above_deep | above the band, deeper than 50 km | unclassified |
| slab | the rest (below the band; within the band where the slab top is deeper than 50 km) | in-slab |
| rm18 | named by Ruiz and Madariaga (2018) with a class; applied last | the paper's class (crustal: sub-class by position) |

- "With σ": the band half-width and the plate bottom are widened by the event's own depth σ (W + σ).
- "Thrust on the interface plane": one nodal plane within 35° of the Slab2 plane at the epicentre, rake 45–135°. 1 011 of the 2 670 mechanisms qualify.
- In-slab classes (section 4): by the slab top at the epicentre and the Jujuy nest; they depend on position only, so they do not change between variants.
- Baseline for the comparisons: ± 15 km, no σ, with mechanisms, below the plate = in-slab (the DECISIONS line of 11 Nov).

**Baseline counts** (`tables/x4b_counts_baseline.csv`, `x4b_counts_inslab.csv`, `x4b_rules_baseline.csv`):

| class | all events in the domain | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 7 |
|---|---|---|---|---|
| interface | 55 341 | 3 896 | 636 | 46 |
| in-slab, shallow (`intraslab_shallow`) | 11 948 | 1 211 | 148 | 5 |
| in-slab, intermediate (`intraslab_intermediate`) | 87 605 | 5 011 | 461 | 21 |
| Jujuy nest (`jujuy_nest`) | 10 612 | 909 | 55 | 3 |
| crustal forearc | 8 532 | 419 | 58 | 2 |
| crustal arc | 8 966 | 179 | 23 | 0 |
| crustal backarc | 2 277 | 283 | 54 | 1 |
| crustal Patagonia | 312 | 86 | 24 | 0 |
| outer rise | 4 425 | 504 | 94 | 7 |
| unknown depth | 9 653 | 1 644 | 384 | 66 |
| unclassified | 756 | 92 | 4 | 2 |

Of the in-slab events 80 (Mw ≥ 4.5; 3 of Mw ≥ 5.5, largest 5.9) are deeper than top + thickness; the maps show them apart.

## 3. Rule variants

24 variants (3 widths × σ × mechanisms × below the plate). `tables/x4b_counts.csv`, `x4b_changes.csv`, `x4b_transition_*.csv`, `figs/x4b_variants.png`. The crustal sub-class never changes (it depends on position only), so class changes and family changes are the same numbers.

**One factor at a time, the others as in the baseline** (events in a different class; in brackets the range over all settings of the other factors):

| change | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 7 |
|---|---|---|---|
| band ± 10 → ± 15 km | 699 | 63 | 3 |
| band ± 15 → ± 20 km | 479 | 37 | 1 |
| band ± 10 → ± 20 km | 1 178 (254–1 424 for any pair of widths) | 100 (9–218) | 4 (1–6) |
| without → with σ | 669 (444–1 231) | 56 (28–190) | 4 (4–7) |
| without → with mechanisms | 265 (265–332) | 119 (115–151) | 3 (1–3) |
| below the plate: in-slab → apart | 80 (54–80) | 3 (3) | 0 |
| more than one class over the 24 variants | 2 173 | 337 | 11 |

**Where the events go.**
- Band ± 10 → ± 15 km: 424 in-slab and 235 forearc events become interface; 30 unclassified and 10 forearc become in-slab.
- With σ (at ± 15 km): 451 in-slab and 183 forearc become interface. With the floors of 13 Nov, σ is 5 km for ISC-EHB and ISC and about 10 km for Potin, CSN and offshore depths, so it widens the band for every source: of the 669 events 236 have a Potin depth, 97 ISC, 92 ComCat, 75 CSN, 133 ISC-EHB.
- With mechanisms: 167 events leave the interface (116 to in-slab, 51 to forearc) and 98 enter it (69 from in-slab, 29 from forearc).
- Interface count over the variants: 3 151 to 4 990 (Mw ≥ 4.5), 42 to 50 (Mw ≥ 7). Forearc crust: 96 to 699.

**Soft membership.** With the event's σ as a normal error, 2 084 of the events with a known depth over the shallow slab have a probability of 0.2–0.8 of lying inside the ± 15 km band (337 of Mw ≥ 5.5, 14 of Mw ≥ 7). Column `p_if`.

**Two settings outside the grid**, for scale.
- Interface down to a slab top of 60 km instead of 50: 147 events change, 143 from in-slab to interface (10 of Mw ≥ 5.5, 1 of Mw ≥ 7). With 40 km: 384 change, 375 from interface to in-slab (36 of Mw ≥ 5.5, 1 of Mw ≥ 7).
- Crustal cap 30 km instead of 50: 170 events change class (20 of Mw ≥ 5.5), 159 of them from crustal to unclassified.

## 4. In-slab classes

`sub()` in `x4b_classify.py`; column `sub`. Table against the old classes: `tables/x4b_old_inslab_m*.csv`.

| new class (Mw ≥ 4.5) | events | old intra_slab | old slab_deep | old deep_nest | old interface | old sub_slab | old unresolved | other old class | not in the old catalogue |
|---|---|---|---|---|---|---|---|---|---|
| intraslab_shallow | 1 211 | 740 | 23 | 0 | 243 | 11 | 2 | 34 | 158 |
| intraslab_intermediate | 5 011 | 22 | 4 207 | 61 | 21 | 63 | 87 | 10 | 540 |
| jujuy_nest | 909 | 0 | 41 | 727 | 0 | 3 | 34 | 2 | 102 |

- The three classes map onto the old three (intra_slab, slab_deep, deep_nest) almost one to one; the 243 old interface events in the shallow class are the deeper depths of the new catalogue.
- Jujuy nest at Mw ≥ 6.5: nine events (1927, 1933, 1951, 1971, 1993, 2000 Mw 7.2, 2006, 2022, 2023). The Jujuy 2015 event of Ruiz and Madariaga (199.8 km) lies outside the 0.8° circle and is intermediate.
- The shallow limit acts on the slab top at the epicentre, not on the event depth: La Ligua 1965 (68.3 km deep, slab top 49.1 km) is shallow, Punitaqui 1997 (59.5 km, slab top 50.7 km) is intermediate. A limit on event depth, or a transition band, are the alternatives.
- The double seismic zone is not treated here (section 0).
- DECISIONS (9 Nov) says the Jujuy nest is no longer a class of its own; this follows Pablo's instruction of 12 Nov and the line needs updating.

## 5. Comparison with earlier classifications

`x4b_compare.py`. Events matched by time and distance (15 s / 100 km; 90 s / 300 km before 1964; for Mw ≥ 6 two wider passes, because the old catalogue carries centroid times up to 51 s late and dates one day off for 1922 and 1939). Tables `x4b_old_m*.csv`, `x4b_candia_macedo_m*.csv`, `x4b_agreement.csv`, `x4b_old_family_changes.csv`, `x4b_rm18.csv`, `x4b_m7_compare.csv`.

**Old classifier (cat_handler_2, frozen 2026-11-04).** 21 703 old events with M ≥ 4.5 against 14 234 new; 12 242 are in both. 9 461 old events have no new counterpart at Mw ≥ 4.5 (the old Mw was higher), 1 992 new ones have no old counterpart (921 after 2022).

| | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 6.5 | Mw ≥ 7 |
|---|---|---|---|---|
| both in a family (interface, in-slab, crustal) | 10 186 | 1 296 | 187 | 75 |
| same family | 9 281 (91 %) | 1 172 (90 %) | 166 | 72 |
| old interface → in-slab | 264 | 34 | 7 | 1 |
| old in-slab → interface | 287 | 31 | 3 | 1 |
| old interface → crustal | 109 | 26 | 7 | 1 |
| old in a family, now unknown depth | 1 019 | 259 | 117 | 57 |
| old unresolved, now in a family | 296 | 33 | 4 | 1 |

- The 751 old interface events that now have an unknown depth (45 of the 94 old interface events of M ≥ 7) are the old rule "unknown depth over a shallow slab = interface".
- The old interface events that are now in-slab are a median 12.5 km deeper in the new catalogue; old in-slab (shallow) now interface are 9 km shallower; old interface now forearc 12 km shallower. The class changes follow the new depths, not the rule.
- Old sub-slab is in-slab (77 of 84), old Antarctic interface is crustal Patagonia or unknown depth.

**Ruiz and Madariaga (2018)**, 59 events matched in A3 (`x4b_rm18.csv`, columns `cls_auto` and `cls`). The rule alone (`cls_auto`): 31 agree, 20 have no depth, 3 have no class in the paper (and no depth), 5 disagree. All 56 with a class carry the paper's class.

| event | paper | rule alone | why |
|---|---|---|---|
| Copiapó 1918, Mw 7.8 | interface | outer rise | ISC-GEM epicentre 163 km west of the trench |
| Concepción 1960-05-21, Mw 8.1 | interface | crustal forearc | Centennial depth 11.5 km (σ now 20 km), slab top 30 km |
| La Ligua 1971, Mw 7.8 | interface | in-slab | slab top 55.6 km at the epicentre, over the 50 km limit |
| Pichilemu 2010 14:55, Mw 7.0 | crustal | in-slab | Potin depth 22.7 km, 2 km under the slab top, normal mechanism |
| Iquique foreshock 2014-03-16, Mw 6.7 | crustal | interface | mechanism passes the interface test, depth 8.6 km |

- Out of this table since the rerun: Arica 1987 (ISC-EHB depth 69.7 km restored, in-slab, agrees); Atacama 1922 and the Valdivia foreshock (their nominal depths are now unknown).
- Without a depth, among others: Santiago 1647, the historical megathrust events, Valparaíso 1906, Atacama 1922, Talca 1928, Chillán 1939, Illapel 1943, Las Melosas 1958, Valdivia 1960 and its foreshock.
- Under the rule alone La Ligua 1965, Valparaíso 1985 and Michilla 2007 agree with the paper in 12 of the 24 variants, Concepción 1960 in 16.

**Candia and Macedo (2026)** (their classes interface, slab, shallow crustal, outer rise, unknown; 13 769 of our events matched). Same family for 9 857 of 11 202 (88 %; 1 178 of 1 324 at Mw ≥ 5.5; 60 of 68 at Mw ≥ 7). The disagreement is one-sided: 831 of their interface events are in-slab here (89 of Mw ≥ 5.5, 4 of Mw ≥ 7, Punitaqui 1997 among them) against 49 the other way; 238 of their interface events are crustal here. 6 467 of their 61 027 groups with M ≥ 4.0 carry more than one class among their own rows.

## 6. Surprises

1. **Large events, class by class** (`tables/x4b_m7.csv`, `x4b_m7_compare.csv`). Of the 153 events with Mw ≥ 7: 66 unknown depth, 46 interface, 29 in-slab, 7 outer rise, 3 crustal, 2 unclassified. Not named by the paper, so still on the rule:
   - Outer rise: Papudo 1981 and 2001 and the Maule aftershock of 08:01 are right. The others are doubtful: 1878-01-23 Mw 7.9 (Cabello epicentre at 77.0° W, 458 km west of the trench), 1919-03-02 11:45 (81 km west), 1922-11-07 and 1960-11-01 (7–9 km from the trench).
   - Unclassified: 1941-04-03 Mw 7.2 (150 km deep, 34 km above the Slab2 top) and 1943-03-14 Mw 7.1 (77 km, 19 km above), Centennial depths; they are slab events.
   - 2010-02-27 08:25 Mw 7.0 (in-slab) is the ML-only event already flagged in A5.
   - 1928-12-02 04:20 Mw 7.2 (now without depth) follows Talca 1928-12-01 04:06 by 24 h 14 min and is about 120 km away; worth a look in A6.
   - Eleven events of Mw ≥ 7 change class between variants: 1941, 1943, 1953-05-06, 1957-11-29, 1960-12-02, 1965-02-23, 1985-03-04, 1988-04-12, 2001-07-07, 2010-02-27 08:25, 2015-09-16 23:18.
2. **Pichilemu and the forearc.** Under the rule the 14:55 event falls on the in-slab side because the slab top is at 20.7 km under a Potin depth of 22.7 km. A crustal normal-fault event near the coast cannot be told from a slab event by depth; the old catalogue used Cabello's "crustal" remarks for these.
3. **88 events above the band and deeper than 50 km** (Mw ≥ 4.5; 48 of them less than 30 km above the top, 44 at 17–24° S). Mislocated slab events, most with ComCat or ISC depths (39 and 26).
4. **Outer rise holds 504 events**, 195 of them without a depth and 153 at 44–46° S west of the trench. Only 10 of those 153 are from 2024 on, so at Mw ≥ 4.5 the far-offshore CSN web events that the A4 entry noted are few; the dense cluster in the map of all events is mostly smaller ones.
5. **Mechanisms take more events out of the interface than they add** (167 out, 98 in), and decide for 119 events of Mw ≥ 5.5, more than σ (56) and more than a 5 km change of the band (37–63).
6. **With σ the class still depends on the depth source**, less than before: an ISC-EHB depth is in the band up to 20 km from the top, a Potin or offshore depth up to 25 km.

## 7. Errors found upstream and what was done with them

The first version listed these on the catalogue of 11 Nov. They were checked in the A3–A5 conversation (WORKLOG, 13 Nov) and A4 and A5 were rerun.

| finding of the first version | verdict | state on 13 Nov |
|---|---|---|
| Fixed depths at a non-round value are discarded | Wrong for ISC: those values are the regional default depths of the ISC locator (181 km 908 times). Right for ISC-EHB. | A fixed ISC-EHB L1 depth counts as measured; a fixed L2 depth (the GCMT depth) is a last resort. Arica 1987 at 69.7 km. ISC fixed depths stay out. |
| Depths before 1964 called measured | Confirmed | Depths on a multiple of 5 km before 1964 are unknown; 78 events keep a depth (ISC-GEM 46, Centennial 31, ISC 1), most with σ 20 km. |
| Depth σ of 1.6–3 km is a spread between catalogues | Confirmed | Floor of 5 km, 10 km offshore. |
| Potin first where it disagrees with the teleseismic records | Confirmed | A local record more than 50 km from the closest teleseismic or GCCEL record is not used (85 events). |
| Potin depths offshore | Confirmed (median 11 km shallower than GCCEL offshore) | More than 20 km from the coast, depth from GCCEL and ISC-EHB before the local catalogue. See below for what remains. |
| `backarc()` continues the end edges of the arc polygon | No effect in A4: it acts only outside the network latitudes | Unchanged. |
| CSN regional Mw 0.5–0.6 above the tensor | Confirmed | Left out where it is more than 0.3 from the median of two or more other moment magnitudes (26 values). 131 pairs with one other value are listed, not changed. |
| File not sorted; reruns overwrote files | Confirmed | Sorted by time; the rerun has its own date. |

**What remains.**
1. **Potin depths near the coast.** 180 events (Mw ≥ 4.5; 20 of Mw ≥ 5.5) still have a Potin depth above 5 km over a slab top deeper than 15 km: Illapel aftershocks of 2015-09-17 04:10 (Mw 6.8, 1.8 km) and 2015-09-21 (Mw 6.6, 0.0 km), 2007-11-15 (Mw 6.8, 2.4 km), Tirúa 2011 (Mw 7.1, 2.8 km). 56 lie more than 40 km under a slab top shallower than 50 km (2015-06-20 Mw 6.4 at 72 km over a slab top of 13 km). 25 depths are negative. 203, 88 and 28 before the rerun. These events are within 20 km of the coast or have no other measured depth.
2. **CSN regional Mw.** Of the five events named in the first version, 2015-09-27 and 2025-05-21 are corrected (now Mw 5.0 and 5.1). 2015-09-05 (5.1) and 2016-02-05 (5.0) have a single other value and are unchanged.
3. **Concepción 1960-05-21** keeps its Centennial depth of 11.5 km (not a round value); its class comes from the paper.
4. **Historical epicentres.** 1878-01-23 Mw 7.9 at 77.0° W (Cabello) is 458 km seaward of the trench; Copiapó 1918 163 km seaward (ISC-GEM). For A6.
5. **Bookkeeping.**
   - `DATA.md` "Other inputs": Slab2 (02.23.18), the trench and arc shapefiles have no version row.
   - DECISIONS still writes NEIC Mwr + 0.10 and GFZ + 0.03; the run applies + 0.08 and + 0.04. The lines for the rules of 13 Nov are proposed in the WORKLOG.
   - `cat_handler_2/` has uncommitted changes in ten files although it is archive; the comparison here uses the frozen catalogue of 2026-11-04, not the code.
   - The X4 label is used twice.

## 8. Options for the A7 rules

Not decisions. Numbers are events of Mw ≥ 4.5 in the domain unless said otherwise.

1. **Band width.** (a) ± 15 km fixed: 3 896 interface events. (b) ± 10 km: 3 237. (c) ± 20 km: 4 220. (d) Width by depth source instead of by event σ (for example ± 10 km for ISC-EHB L1 and GCCEL, ± 20 km offshore and for Potin above 30 km). With the σ floors of 13 Nov the "with σ" variants are now close to this, but the floors are round values, not measured errors.
2. **Soft classes.** Carry `p_if` (or a three-way probability) for the 2 084 events with 0.2–0.8 and run the fits with split weights, as DECISIONS already foresees for unknown depths. It replaces the choice of a width by a statement of the error.
3. **Mechanisms.** (a) Both ways as here. (b) Only to add interface events, never to remove (the 167 removals rest on a 35° cone and on Slab2 dip). (c) Not at all, and use them as a check. At Mw ≥ 5.5 this is the largest single choice.
4. **Large events.** Decided: the events Ruiz and Madariaga name take the paper's class. Open: the large events it does not name (the doubtful outer-rise and unclassified events of section 6, 1928-12-02, 2010-02-27 08:25) go to A6 one by one.
5. **Unknown depth (1 644; 384 of Mw ≥ 5.5; 66 of Mw ≥ 7).** By slab top at the epicentre: 951 over a top < 50 km (interface, shallow slab or forearc), 315 at 50–100 km, 222 deeper than 100 km (in-slab unless crustal), 156 without a slab. Options as DECISIONS of 12 Nov (mechanism: 25 events; depth of another agency; split weights). Before 1964 (331 events, 65 of Mw ≥ 7) nothing but the literature helps.
6. **Interface limit.** Slab top 50 km (the Z_BOTTOM of the interface source) or 60 km: 147 events. Or the limit applied to the event depth instead of the slab top at the epicentre.
7. **Events above a deep slab and deeper than the crust (88).** In-slab when deeper than 50–70 km (the old rule), or left out. In-slab is the reading the sections support.
8. **Below the plate.** 80 events, none above Mw 5.9: the choice does not matter for the fits. "In-slab" stands.
9. **In-slab classes.** Shallow against intermediate by the slab top at the epicentre (as here), by event depth, or with a transition band (section 4); the nest circle and depth range as in cat_handler_2 or refitted on the new catalogue.
10. **Crustal.** Cap 50 km as here or 30 km (159 events); whether forearc events inside the band with a non-thrust mechanism are crustal when above the top only (as here) or by a hand list.
11. **Upstream.** The A4 and A5 rerun is done and this exploration is on its output. Before A7 is written: the Potin depths near the coast (section 7, point 1) and the large events for A6.

## 9. Assumptions made without asking

- The baseline (± 15 km, no σ, with mechanisms) and every threshold of section 2: interface down to a slab top of 50 km, mechanism reach 65 km and + 10 km, cone 35°, rake 45–135°, crustal cap 50 km, Patagonia south of 46.15° S (44° S where Slab2 is missing).
- Outer rise is decided by position alone, so it includes 195 events of unknown depth.
- The band is measured vertically.
- "With σ" = band and plate bottom widened by one σ.
- Slab2 values are bilinear, with the nearest node within 15 km at the edge of the model; 636 events of Mw ≥ 4.5 have no slab.
- An Antarctic interface class was not made; 181 events are flagged `an_if` (within 150 km of the Antarctic trench, not deeper than 60 km).
- Ruiz and Madariaga events without a depth and with the class intraslab take the in-slab class by the slab top (Santiago 1647 shallow, Chillán 1939 intermediate).
- Class colours and display names in the figures are drafts kept in `x4b_figs.py`; `palette.py` has none yet.
- Candia and Macedo: one class per group (the most frequent of its rows), groups with M ≥ 4.0.

## 10. Files and run

- Code: `x4b_classify.py` (10 s), `x4b_compare.py` (10 s), `x4b_figs.py` (10 s), in this order; `tests/test_x4b.py` (11 tests). `RUN` at the top of `x4b_classify.py` is the catalogue date (2026-11-13), `A3` the date of the Ruiz and Madariaga matches (2026-11-11).
- Tables: `tables/x4b_*.csv` (28 files, all of the 13 Nov run; `x4b_events_m45.csv` has every event of Mw ≥ 4.5 with its geometry, `cls_auto`, `cls`, `sub`, `rule` and its class under each of the 24 variants). All events: `cache/x4b_events.csv.gz` (not for git).
- Figures: `figs/x4b_*.png` (3), drawn with pituPLOTS b9be58a.
- Findings of the first version for the other conversations: `HANDOFF_A3-A5.md` (numbers of 11 Nov, kept as written).
