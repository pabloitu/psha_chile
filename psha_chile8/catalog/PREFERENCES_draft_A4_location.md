# Draft for PREFERENCES.md: location and depth rule for A4 (from X1 and X3)

Status: **draft by Claude Code, 2026-11-11, for Pablo to review.** Nothing in `PREFERENCES.md` or `DECISIONS.md` is changed. If you accept it, the text under "Proposed text" replaces the "Location and depth order" bullet in PREFERENCES section 2, and the DECISIONS line of 11 Nov ("no regional or depth exceptions") changes with it.

## Why change the 11 Nov rule

The 11 Nov rule is Potin → GCCEL → ISC-EHB L1/L2 → ISC → ComCat → CSN, everywhere. Against GCCEL (X3, 775 shared events, GCCEL left out of the order), it is 8.9 km off in epicentre and 8.1 km in depth on average. Splitting the events by tectonic group shows where that error comes from:

| group (by the GCCEL hypocentre) | events | Potin epicentre median | Potin depth − GCCEL (median ± spread) | best other source |
|---|---|---|---|---|
| crustal, onshore forearc / arc / coast | 57 | 3.3 km | −0.1 ± 4.9 km | ISC prime −1.6 ± 6.4 |
| crustal, backarc (San Juan) | 29 | 15.5 km | −7.3 ± 18.8 km | ComCat +0.1 ± 7.4 |
| interface / slab, onshore or coast | 430 | 5.4 km | +1.0 ± 4.3 km | EHB L1 −0.1 ± 4.2 |
| offshore (interface / slab) | 90 | 7.0 km | −12.2 ± 7.8 km | EHB L1 −1.4 ± 6.4 (26) |

(`explore/X3/tables/x3_diff_summary.csv`, `by = grp`. Crustal: more than 15 km above the Slab2 top. Offshore: epicentre offshore, whatever the depth.)

What the table says:

1. **Crustal events inside the network:** Potin is the best source in both epicentre and depth. Keep it first.
2. **Crustal events in the backarc:** Potin is poor, because it is outside its network (it has one event 141 km too deep). The global sources are better.
3. **Interface and in-slab events under the coast and inland:** Potin is the best epicentre, and its depth is as good as ISC-EHB L1 (spread 4.3 vs 4.2 km). Keep it first.
4. **Offshore events:** Potin is 12 km shallower than GCCEL, and ISC and ComCat are 5–6 km shallower. But GCCEL is not a reliable judge here. Its depths for offshore events are constrained by stations on one side only (the coast). Against the Slab2 top on the same 82 events, GCCEL is 5.5 ± 9.6 km below it, Potin −2.3 ± 7.7 and ISC −1.3 ± 11.0 (`x3_slab_check.csv`). Slab2 sits between them, so neither is shown to be wrong. No location order brings the offshore depths below about 10.7 km (mean |Δz| 10.7–12.3 km over the variants, against GCCEL).
5. **South of about 36–37° S** (Tomé, Tirúa), Potin's epicentres scatter (13–27 km) and its depths spread 9–18 km.
6. **Below 70 km,** GCCEL has 14 events and none below 95 km, so it cannot test X1 finding 6 (Potin 25–60 km too deep under the flat slab at 100–170 km). That exception rests on X1.

Scored against GCCEL (`x3_variant_scores_by_group.csv`), with mean |Δz| in km:

| variant | all | crustal onshore | crustal backarc | interface / slab onshore | offshore |
|---|---|---|---|---|---|
| 11 Nov rule (L-e0) | 8.12 | 6.71 | 28.11 | 5.47 | 12.18 |
| Potin only at 18–37° S and not in the backarc (L-g) | 6.85 | 6.62 | 13.49 | 5.17 | 12.07 |

The epicentre also improves, from 8.91 to 8.57 km. L-g changes the first source of 63 of the 775 events.

## Proposed text (replaces the "Location and depth order" bullet)

- **Location and depth order:**
  - **Inside the local network** (Potin's or CSN's epicentre at 18–37° S and not in the backarc): Potin (CSN after 2020-07-16) → GCCEL → ISC-EHB L1/L2 → ISC → ComCat.
  - **Elsewhere** (south of 37° S, north of 18° S, the backarc): GCCEL → ISC-EHB L1/L2 → ISC → ComCat → Potin / CSN.
  - **Depth** is the first *measured* depth in that order. A fixed depth or an agency default is never taken while any source has a measured one.
  - **Below 70 km in the flat slab (29–34° S):** ISC-EHB L1/L2 before Potin, on the X1 evidence (GCCEL cannot test it). (**P**, Pablo / S. Ruiz)
  - **Offshore events:** the same order, with depth σ of about 10 km for every source. The depth is used only to separate interface from outer-rise and in-slab events in A7, against the Slab2 geometry. (**P**)

Changes table row:

| date | change | by |
|---|---|---|
| 2026-11-?? | location order by region (local network inside 18–37° S, west of the backarc; global sources first elsewhere); EHB first below 70 km in the flat slab; offshore depths treated as uncertain (X1, X3) | Pablo |

## Open points for Pablo / S. Ruiz

- **Southern limit of the network core:** 36° S or 37° S. The scores barely differ (6.89 vs 6.85 km depth, 8.40 vs 8.57 km epicentre). X1's L-b used 44° S, and X3 has no events between 39° S and 44° S to test that.
- **The backarc limit:** the X1 setting polygon or a fixed longitude. X1 found < 80 events of difference between the two.
- **Offshore depths:** whether to ask E. Bergman how the depths of the offshore Chilean clusters are constrained. 51 offshore events carry depth code `n` (near-source stations), 33 `l` and 10 `d`. A short note from him would settle whether GCCEL can be a depth reference offshore.
- **Valparaíso cluster:** every source is 8–14 km shallower than GCCEL there (6 of the shallow offshore events). Same question to E. Bergman.
- Whether S. Ruiz agrees to drop "Potin first everywhere" for the backarc and the far south. His 10 Nov order put Potin first for 1982–2020, without a regional limit.
