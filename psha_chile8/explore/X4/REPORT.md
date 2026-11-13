# X4: exploratory classification of the merged catalogue

12 Nov 2026, revised the same evening after Pablo's answers (section 0). Exploration for A7: nothing under `catalog/` was changed.
Input: `catalog/merged/catalog_2026-11-11.csv` (third A5 run joined with the A4 locations): 204 956 events, 200 427 in the domain, **14 157 with Mw ≥ 4.5 in the domain** (12 413 with a measured depth, 2 670 with a mechanism). Geometry: Slab2 (`data/slab_2.0`, top, thickness, dip, strike), `sam_nazca_trench.shp`, `sam_antarctica_trench.shp`, arc polygon `data/intraarc.shp`.

Name clash: `explore/X4/` already held the surface-wave check of this morning (`x4_*.py`, `tables/x4_*`). Everything of this task carries the prefix `x4b_`; nothing of the earlier work was touched.

## 0. Revision after Pablo's answers (12 Nov, evening)

- **Arc polygon:** the one modified last, `data/intraarc.shp` (25 Nov 2025; `data/shapefiles/intra_arc.shp` is of 15 Oct 2025). It is the one A4 and this task already use; nothing changes.
- **Ruiz and Madariaga (2018) is authoritative for class:** the 56 events with a class in the paper take it after the rules, in every variant (`rule = rm18`; `cls_auto` keeps the rule's class). 23 of them change class. All numbers below include this.
- **Double seismic zone: withdrawn from this task.** The two-plane test was run without removing the Jujuy nest, so its detections at 22–25° S are not valid; the test, its tables and figures are removed. The planes are handled in the in-slab source model.
- **In-slab classes:** `intraslab_shallow` (slab top above 50 km at the epicentre), `intraslab_intermediate`, `jujuy_nest` (within 0.8° of 66.9° W, 24.0° S, depth 170–320 km, measured depth; the cat_handler_2 definition).
- **A4 is rerun in another conversation.** The findings for the A3, A4 and A5 conversations are in `HANDOFF_A3-A5.md`. Rerun this task after it (about 30 s).

## 1. Summary

1. **The class of 2 195 of the 14 157 events (16 %) depends on the rule variant**; 354 of 1 949 at Mw ≥ 5.5 and 10 of 153 at Mw ≥ 7. Nearly all of it is the interface against in-slab and against forearc crust.
2. **The band width matters most** (± 10 → ± 20 km: 1 221 events, 124 of Mw ≥ 5.5, 5 of Mw ≥ 7). Adding the depth σ moves 648, mechanisms 265 (but 116 of Mw ≥ 5.5, where most mechanisms are), "below the plate" only 94 and none above Mw 6.6.
3. **Unknown depth is the largest problem for the large events: 54 of the 153 events with Mw ≥ 7 (53 of them before 1964) and 282 of 1 949 with Mw ≥ 5.5 have no class**, after the 15 that Ruiz and Madariaga settle.
4. **Several great interface earthquakes are not interface under a rule on catalogue depth alone:** Atacama 1922 (in-slab), Concepción 1960-05-21 and the Valdivia foreshock (forearc crust), La Ligua 1971 (in-slab), Copiapó 1918 (outer rise); Valdivia 1960 is interface at ± 15 km and forearc crust at ± 10 km; Valparaíso 1985 is interface only through its mechanism. They are now set from the paper; the same errors remain for large events the paper does not name. Section 6.
5. **In-slab classes (Mw ≥ 4.5):** 1 211 shallow, 4 963 intermediate, 902 Jujuy nest; at Mw ≥ 7: 6, 25 and 3.
6. **Against the old classifier the family agrees for 91 % of the events both classify (89 % at Mw ≥ 5.5)**, against Candia and Macedo for 88 %. Against Ruiz and Madariaga the rule alone gives 33 right, 8 wrong, 15 without depth; 3 have no class in the paper.
7. **Errors and weak points found upstream** (section 7): depths held by ISC and ISC-EHB at a non-round value are discarded as "fixed" and replaced by a worse depth (Arica 1987: 69.7 → 19 km); two thirds of the "measured" depths before 1964 are round nominal values with σ of 3–6 km; Potin depths of offshore events are near 0 km or tens of km below the slab.

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
- "Thrust on the interface plane": one nodal plane within 35° of the Slab2 plane at the epicentre, rake 45–135°. 1 010 of the 2 670 mechanisms qualify.
- In-slab classes (section 4): by the slab top at the epicentre and the Jujuy nest; they depend on position only, so they do not change between variants.
- Baseline for the comparisons: ± 15 km, no σ, with mechanisms, below the plate = in-slab (the DECISIONS line of 11 Nov).

**Baseline counts** (`tables/x4b_counts_baseline.csv`, `x4b_counts_inslab.csv`, `x4b_rules_baseline.csv`):

| class | all events in the domain | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 7 |
|---|---|---|---|---|
| interface | 55 344 | 3 893 | 669 | 50 |
| in-slab, shallow (`intraslab_shallow`) | 11 963 | 1 211 | 168 | 6 |
| in-slab, intermediate (`intraslab_intermediate`) | 87 774 | 4 963 | 480 | 25 |
| Jujuy nest (`jujuy_nest`) | 10 623 | 902 | 54 | 3 |
| crustal forearc | 8 605 | 465 | 77 | 2 |
| crustal arc | 8 985 | 185 | 27 | 2 |
| crustal backarc | 2 280 | 282 | 57 | 1 |
| crustal Patagonia | 313 | 87 | 26 | 0 |
| outer rise | 4 414 | 511 | 99 | 7 |
| unknown depth | 9 328 | 1 552 | 282 | 54 |
| unclassified | 798 | 106 | 10 | 3 |

Of the in-slab events 94 (Mw ≥ 4.5; 8 of Mw ≥ 5.5, largest 6.6) are deeper than top + thickness; the maps show them apart.

## 3. Rule variants

24 variants (3 widths × σ × mechanisms × below the plate). `tables/x4b_counts.csv`, `x4b_changes.csv`, `x4b_transition_*.csv`, `figs/x4b_variants.png`. The crustal sub-class never changes (it depends on position only), so class changes and family changes are the same numbers.

**One factor at a time, the others as in the baseline** (events in a different class; in brackets the range over all settings of the other factors):

| change | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 7 |
|---|---|---|---|
| band ± 10 → ± 15 km | 727 | 77 | 3 |
| band ± 15 → ± 20 km | 494 | 47 | 2 |
| band ± 10 → ± 20 km | 1 221 (272–1 454 for any pair of widths) | 124 (21–234) | 5 (1–7) |
| without → with σ | 648 (426–1 188) | 58 (32–181) | 2 (2–6) |
| without → with mechanisms | 265 (256–317) | 116 (105–138) | 3 (1–3) |
| below the plate: in-slab → apart | 94 (66–94) | 8 (6–8) | 0 |
| more than one class over the 24 variants | 2 195 | 354 | 10 |

The Mw ≥ 7 numbers are lower than in the first version because the events Ruiz and Madariaga name no longer move.

**Where the events go.**
- Band ± 10 → ± 15 km: 412 in-slab and 265 forearc events become interface; 38 unclassified become in-slab.
- With σ (at ± 15 km): 416 in-slab and 197 forearc become interface. σ acts like a wider band for the sources with a large σ (Potin offshore 10 km, CSN) and not at all for ISC-EHB (1.6–2.3 km).
- With mechanisms: 162 events leave the interface (105 to in-slab, 57 to forearc) and 103 enter it (68 from in-slab, 35 from forearc).
- Interface count over the variants: 3 135 to 4 959 (Mw ≥ 4.5), 46 to 54 (Mw ≥ 7). Forearc crust: 115 to 779.

**Soft membership.** With the event's σ as a normal error, 1 981 of the events with a known depth over the shallow slab have a probability of 0.2–0.8 of lying inside the ± 15 km band (310 of Mw ≥ 5.5, 11 of Mw ≥ 7). Column `p_if`.

**Two settings outside the grid**, for scale: interface down to a slab top of 60 km instead of 50: 147 in-slab events become interface (14 of Mw ≥ 5.5, 3 of Mw ≥ 7, La Ligua 1971 among them); 40 km: 377 the other way. Crustal cap 30 km instead of 50: 179 events change class (24 of Mw ≥ 5.5), 168 of them from crustal to unclassified.

## 4. In-slab classes

`sub()` in `x4b_classify.py`; column `sub`. Table against the old classes: `tables/x4b_old_inslab_m*.csv`.

| new class (Mw ≥ 4.5) | events | old intra_slab | old slab_deep | old deep_nest | old interface | old sub_slab | old unresolved | not in the old catalogue |
|---|---|---|---|---|---|---|---|---|
| intraslab_shallow | 1 211 | 746 | 21 | 0 | 246 | 14 | 1 | 156 |
| intraslab_intermediate | 4 963 | 21 | 4 155 | 63 | 22 | 64 | 87 | 538 |
| jujuy_nest | 902 | 0 | 41 | 721 | 0 | 3 | 34 | 100 |

- The three classes map onto the old three (intra_slab, slab_deep, deep_nest) almost one to one; the 246 old interface events in the shallow class are the deeper depths of the new catalogue.
- Jujuy nest at Mw ≥ 6.5: nine events (1927, 1933, 1951, 1971, 1993, 2000 Mw 7.2, 2006, 2022, 2023). The Jujuy 2015 event of Ruiz and Madariaga (199.8 km) lies outside the 0.8° circle and is intermediate.
- The shallow limit acts on the slab top at the epicentre, not on the event depth: La Ligua 1965 (68 km deep, slab top 49.1 km) is shallow, Punitaqui 1997 (59.5 km, slab top 50.7 km) is intermediate. A limit on event depth, or a transition band, are the alternatives.
- The double seismic zone is not treated here (section 0).
- DECISIONS (9 Nov) says the Jujuy nest is no longer a class of its own; this follows Pablo's instruction of 12 Nov and the line needs updating.

## 5. Comparison with earlier classifications

`x4b_compare.py`. Events matched by time and distance (15 s / 100 km; 90 s / 300 km before 1964; for Mw ≥ 6 two wider passes, because the old catalogue carries centroid times up to 51 s late and dates one day off for 1922 and 1939). Tables `x4b_old_m*.csv`, `x4b_candia_macedo_m*.csv`, `x4b_agreement.csv`, `x4b_old_family_changes.csv`, `x4b_rm18.csv`, `x4b_m7_compare.csv`.

**Old classifier (cat_handler_2, frozen 2026-11-04).** 21 703 old events with M ≥ 4.5 against 14 157 new; 12 171 are in both. 9 532 old events have no new counterpart at Mw ≥ 4.5 (the old Mw was higher), 1 986 new ones have no old counterpart (913 after 2022).

| | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 6.5 | Mw ≥ 7 |
|---|---|---|---|---|
| both in a family (interface, in-slab, crustal) | 10 183 | 1 376 | 207 | 85 |
| same family | 9 276 (91 %) | 1 222 (89 %) | 184 | 81 |
| old interface → in-slab | 268 | 52 | 9 | 2 |
| old in-slab → interface | 277 | 27 | 2 | 1 |
| old interface → crustal | 127 | 40 | 7 | 1 |
| old in a family, now unknown depth | 942 | 177 | 97 | 48 |
| old unresolved, now in a family | 295 | 38 | 6 | 1 |

- The 693 old interface events that now have an unknown depth (40 of the 94 old interface events of M ≥ 7) are the old rule "unknown depth over a shallow slab = interface".
- The old interface events that are now in-slab are a median 13.7 km deeper in the new catalogue; old in-slab (shallow) now interface are 9 km shallower; old interface now forearc 10 km shallower. The class changes follow the new depths, not the rule.
- Old sub-slab is in-slab (81 of 85), old Antarctic interface is crustal Patagonia or unknown depth.

**Ruiz and Madariaga (2018)**, 59 events matched in A3 (`x4b_rm18.csv`, columns `cls_auto` and `cls`). The rule alone (`cls_auto`): 33 agree, 15 have no depth, 3 have no class in the paper, 8 disagree. All 56 with a class now carry the paper's class.

| event | paper | rule alone | why |
|---|---|---|---|
| Copiapó 1918, Mw 7.8 | interface | outer rise | ISC-GEM epicentre 163 km west of the trench |
| Atacama 1922, Mw 8.5 | interface | in-slab | ComCat depth 70 km (nominal), slab top 59 km |
| Concepción 1960-05-21, Mw 8.1 | interface | crustal forearc | Centennial depth 11.5 km, slab top 30 km |
| Valdivia foreshock 1960-05-22 18:56, Mw 7.8 | interface | crustal forearc | ISC-GEM depth 25 km, slab top 44 km |
| La Ligua 1971, Mw 7.8 | interface | in-slab | slab top 55.6 km at the epicentre, over the 50 km limit |
| Arica 1987, Mw 7.2 | intraslab | crustal forearc | depth 19 km taken from ISC; ISC-EHB has 69.7 km (section 7) |
| Pichilemu 2010 14:55, Mw 7.0 | crustal | in-slab | Potin depth 22.7 km, 2 km under the slab top, normal mechanism |
| Iquique foreshock 2014-03-16, Mw 6.7 | crustal | interface | mechanism passes the interface test, depth 8.6 km |

Without a depth, among others: Santiago 1647, the historical megathrust events, Talca 1928, Chillán 1939, Illapel 1943, Las Melosas 1958. Under the rule alone Valdivia 1960, La Ligua 1965, Valparaíso 1985 and Michilla 2007 agree in only 12–16 of the 24 variants.

**Candia and Macedo (2026)** (their classes interface, slab, shallow crustal, outer rise, unknown; 13 686 of our events matched). Same family for 9 798 of 11 177 (88 %; 1 220 of 1 401 at Mw ≥ 5.5; 67 of 76 at Mw ≥ 7). The disagreement is one-sided: 836 of their interface events are in-slab here (107 of Mw ≥ 5.5, 5 of Mw ≥ 7, Punitaqui 1997 and Michilla 2007 among them) against 50 the other way; 268 of their interface events are crustal here. 6 467 of their 61 027 groups with M ≥ 4.0 carry more than one class among their own rows.

## 6. Surprises

1. **Large events, class by class** (`tables/x4b_m7.csv`, `x4b_m7_compare.csv`). Of the 153 events with Mw ≥ 7: 54 unknown depth, 50 interface, 34 in-slab, 7 outer rise, 5 crustal, 3 unclassified. Not named by the paper, so still on the rule:
   - Outer rise: Papudo 1981 and 2001 and the Maule aftershock of 08:01 are right. The others are doubtful: 1878-01-23 Mw 7.9 (Cabello epicentre at 77.0° W, 458 km west of the trench), 1919-03-02 11:45, 1922-11-07 and 1960-11-01 (7–9 km from the trench).
   - Unclassified: 1909, 1910 and 1941, intermediate-depth events 19–34 km above the Slab2 top with round ISC-GEM or Centennial depths; they are slab events.
   - 2010-02-27 08:25 Mw 7.0 (in-slab) is the ML-only event already flagged in A5.
   - 1928-12-02 04:20 Mw 7.2 (interface) follows Talca 1928-12-01 04:06 by 24 h 14 min and is about 120 km away; worth a look in A6.
2. **Pichilemu and the forearc.** Under the rule the 14:55 event falls on the in-slab side because the slab top is at 20.7 km under a Potin depth of 22.7 km. A crustal normal-fault event near the coast cannot be told from a slab event by depth; the old catalogue used Cabello's "crustal" remarks for these.
3. **106 events above the band and deeper than 50 km** (Mw ≥ 4.5; 62 of them less than 30 km above the top, 56 at 17–24° S). Mislocated slab events, most with ISC or ComCat depths.
4. **Outer rise holds 512 events**, with a dense cluster at 44–46° S west of the trench: the CSN web events of 2024–2026 that the A4 entry already noted.
5. **Mechanisms take more events out of the interface than they add** (162 out, 103 in), and decide for 116 events of Mw ≥ 5.5, more than σ (58) and more than a 5 km change of the band (47–77).
6. **With σ the class depends on the depth source.** An ISC-EHB depth 17 km under the top is in-slab, a Potin offshore depth 24 km under it is interface.

## 7. Errors and inconsistencies found upstream

Ordered by what they do to the classes. None was corrected here.

1. **A4 discards depths held at a non-round value.** The ISC-EHB table has 372 L1 and 509 L2 depths flagged `depth_fixed`; 20 % of all fixed ISC-EHB depths are not on a multiple of 5 km, and the ISC prime depths show the same (fixed at 112, 136, 219 km). Those look like depths held at a depth-phase value, not defaults. A4 treats every fixed depth as not measured and takes the next source: 1 175 events (Mw ≥ 4.5, in the domain) have a non-round depth of their location source replaced, 359 by more than 20 km (329 of them ISC → ComCat), and 285 would lie on another side of the ± 15 km band (18 of Mw ≥ 5.5). Example: Arica 1987-08-08 Mw 7.2, ISC-EHB L1 69.7 km replaced by ISC 19.05 km. To check in the ISC and EHB documentation what the flag means for non-round values.
2. **Depths before 1964 are called measured.** 211 events before 1964 have a measured depth; 134 sit on a multiple of 5 km (ISC-GEM 25 km 35 times, 20 km 20 times; ComCat 15 and 35 km). The default table was built per agency and period from 1964, and ComCat's copies of ISC-GEM do not carry the agency `us`. They get σ of 3.0–6.1 km from the modern tables (ISC-GEM 3.0 km at 255 km depth for 1909). Atacama 1922 at 70 km and Valparaíso 1906 at 35 km come from here.
3. **Depth σ is a spread between catalogues, not an error.** ISC-EHB L1 1.65 km, L2 2.3, ISC 2.8 at ≥ 70 km come from 7–14 pairs (X3 table) or from X1 against EHB itself; LEARNINGS says the EHB / ISC / ISC-GEM depths are not independent. With these values the σ variants reward the sources that agree with each other.
4. **Potin depths offshore.** 203 events (Mw ≥ 4.5) have a Potin depth above 5 km over a slab top deeper than 15 km (23 of Mw ≥ 5.5: aftershocks of Illapel 2015 at 0.0–5 km, Tirúa 2011 at 2.8 km); 88 lie more than 40 km under a slab top shallower than 50 km (1995-11-01 Mw 6.6 at 88.5 km where the slab top is 9.5 km; 2015-06-20 Mw 6.4 at 72 km, one of the Potin doubles of A3). 28 measured depths are negative. X3 said that Potin depths above 30 km are poor; the A4 rule still puts them first.
5. **Arc polygon.** Settled: `data/intraarc.shp` (section 0); the older `data/shapefiles/intra_arc.shp` of cat_handler_2 differs by 15 square degrees and should not be used again. `backarc()` of `locate.py` continues the polygon's end edges north of 17.6° S and south of 47.2° S (359 and 185 events of Mw ≥ 4.5).
6. **Catalogue Mw 0.5–0.6 above the moment tensor of the same event:** five events (2015-09-05, -18, -27, 2016-02-05, 2025-05-21). The catalogue takes the CSN regional Mw (GUC Mwr 5.0–5.4; CSN web Mw 5.7) where the USGS tensor gives 4.4–5.2; 16 of 97 GUC Mwr values differ from the event's tensor by 0.3 or more (GCMT 7 of 1 879, NEIC Mww 3 of 499). An A5 matter, not a mechanism error.
7. **Historical epicentres.** 1878-01-23 Mw 7.9 at 77.0° W (Cabello) is 458 km seaward of the trench; Copiapó 1918 163 km seaward (ISC-GEM).
8. **Bookkeeping.**
   - `DATA.md` "Other inputs" is empty: Slab2 (02.23.18), the trench and arc shapefiles have no version row.
   - `catalog_2026-11-11.csv` is not sorted by time.
   - Three A5 runs and two A4 runs overwrote files of the same name and date, so the date in the name no longer identifies the run.
   - DECISIONS still writes NEIC Mwr + 0.10 and GFZ + 0.03; the run applies + 0.08 and + 0.04 (already noted on 12 Nov).
   - `cat_handler_2/` has uncommitted changes in ten files (`classify.py`, `params.py`, …) although it is archive; the comparison here uses the frozen catalogue of 2026-11-04, not the code.
   - The paper-draft entry of 12 Nov gives 54 unknown-depth events with a mechanism; in the domain at Mw ≥ 4.5 there are 27.
   - The X4 label is used twice.

## 8. Options for the A7 rules

Not decisions. Numbers are events of Mw ≥ 4.5 in the domain unless said otherwise.

1. **Band width.** (a) ± 15 km fixed: 3 893 interface events. (b) ± 10 km: 3 216. (c) ± 20 km: 4 348. (d) Width by depth source instead of by event σ (for example ± 10 km for ISC-EHB L1 and GCCEL, ± 20 km offshore and for Potin above 30 km), which is what "with σ" does in effect but stated openly. I would not use the present σ column for this before point 3 of section 7 is settled.
2. **Soft classes.** Carry `p_if` (or a three-way probability) for the 1 981 events with 0.2–0.8 and run the fits with split weights, as DECISIONS already foresees for unknown depths. It replaces the choice of a width by a statement of the error.
3. **Mechanisms.** (a) Both ways as here. (b) Only to add interface events, never to remove (the 162 removals rest on a 35° cone and on Slab2 dip). (c) Not at all, and use them as a check. At Mw ≥ 5.5 this is the largest single choice.
4. **Large events.** Decided: the events Ruiz and Madariaga name take the paper's class. Open: the large events it does not name (the doubtful outer-rise and unclassified events of section 6, 1928-12-02, 2010-02-27 08:25) go to A6 one by one.
5. **Unknown depth (1 552; 282 of Mw ≥ 5.5).** By slab top at the epicentre: 895 over a top < 50 km (interface, shallow slab or forearc), 294 at 50–100 km, 209 deeper than 100 km (in-slab unless crustal), 154 without a slab. Options as DECISIONS of 12 Nov (mechanism: 27 events; depth of another agency; split weights). Before 1964 (222 events, 53 of Mw ≥ 7) nothing but the literature helps.
6. **Interface limit.** Slab top 50 km (the Z_BOTTOM of the interface source) or 60 km: 147 events, La Ligua 1971 among them. Or the limit applied to the event depth instead of the slab top at the epicentre.
7. **Events above a deep slab and deeper than the crust (106).** In-slab when deeper than 50–70 km (the old rule), or left out. In-slab is the reading the sections support.
8. **Below the plate.** 94 events, none above Mw 6.6: the choice does not matter for the fits. "In-slab" stands.
9. **In-slab classes.** Shallow against intermediate by the slab top at the epicentre (as here), by event depth, or with a transition band (section 4); the nest circle and depth range as in cat_handler_2 or refitted on the new catalogue.
10. **Crustal.** Cap 50 km as here or 30 km (168 events); whether forearc events inside the band with a non-thrust mechanism are crustal when above the top only (as here) or by a hand list.
11. **Upstream first.** Points 1, 2 and 4 of section 7 move more large events than any rule choice. A4 is being rerun; rerun this exploration on its output before A7 is written.

## 9. Assumptions made without asking

- The baseline (± 15 km, no σ, with mechanisms) and every threshold of section 2: interface down to a slab top of 50 km, mechanism reach 65 km and + 10 km, cone 35°, rake 45–135°, crustal cap 50 km, Patagonia south of 46.15° S (44° S where Slab2 is missing).
- Outer rise is decided by position alone, so it includes 177 events of unknown depth.
- The band is measured vertically.
- "With σ" = band and plate bottom widened by one σ.
- Slab2 values are bilinear, with the nearest node within 15 km at the edge of the model; 638 events of Mw ≥ 4.5 have no slab.
- An Antarctic interface class was not made; 181 events are flagged `an_if` (within 150 km of the Antarctic trench, not deeper than 60 km).
- Ruiz and Madariaga events without a depth and with the class intraslab take the in-slab class by the slab top (Santiago 1647 shallow, Chillán 1939 intermediate).
- Class colours and display names in the figures are drafts kept in `x4b_figs.py`; `palette.py` has none yet.
- Candia and Macedo: one class per group (the most frequent of its rows), groups with M ≥ 4.0.

## 10. Files and run

- Code: `x4b_classify.py` (10 s), `x4b_compare.py` (10 s), `x4b_figs.py` (10 s), in this order; `tests/test_x4b.py` (11 tests).
- Tables: `tables/x4b_*.csv` (28 files; `x4b_events_m45.csv` has every event of Mw ≥ 4.5 with its geometry, `cls_auto`, `cls`, `sub`, `rule` and its class under each of the 24 variants). All events: `cache/x4b_events.csv.gz` (not for git).
- Figures: `figs/x4b_*.png` (3), drawn with pituPLOTS b9be58a.
- For the other conversations: `HANDOFF_A3-A5.md`.
