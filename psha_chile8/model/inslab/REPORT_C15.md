# C15: in-slab depth options (depth part)

Scope (Pablo, 16 Nov): this task builds the depth cell tables only. The source files, the rupture-geometry options and the tornado branches are made in S2 and run by S5. Script `options.py`, on the cells and events of C14. Current run `2026-11-16d` (class weights, section 8; catalogue 2026-11-16c, nest test and slicing fixed, section 7); the numbers of sections 1–6 are of run `2026-11-16b` and moved by less than 0.01 in the fractions.

## 1. One-layer hypocentre

**Before.** In C14 the one-layer hypocentre `h_one` was the kernel-weighted median of the zone, per cell, and S2 used it. It jumps by about 10 km along the 50 km contour of the slab top:

| slab top (km) | 0–30 | 30–40 | 40–50 | 50–60 | 60–70 | 70–90 | 90–120 | 120–200 | > 200 |
|---|---|---|---|---|---|---|---|---|---|
| C14 median, km below the top | 23.3 | 19.9 | 12.8 | 10.7 | 11.2 | 17.5 | 16.2 | 13.8 | 18.0 |
| new rule, km below the top | 18.0 | 18.4 | 18.6 | 18.8 | 19.5 | 19.9 | 19.0 | 18.0 | 20.8 |

The cause is the class rule. Over the shallow slab (top ≤ 50 km), A7 counts any event within ± 15 km of the top as interface. So only 0.9 % of the in-slab events there lie within 15 km of the top.

**Rule.** h_one = top + 0.252 × Slab2 thickness. 0.252 is the fraction of the thickness that holds half of the 70 804 events of the depth model, measured the same way as the 0.475 of the lower depth (`onelayer_2026-11-16b.csv`).

| group | median d / thickness | events |
|---|---|---|
| all | 0.252 | 70 804 |
| Riedel-Hornig / catalogue | 0.279 / 0.214 | 40 654 / 30 150 |
| slab top ≤ 50 km / > 50 km | 0.363 / 0.234 | 6 105 / 64 699 |
| 2° bands, 16–36° S | 0.14–0.31 | |
| 36–38° S / 38–42° S | 0.26 / 0.04–0.11 | 1 054 / 445 |

The fraction is much less stable than the 0.475:
- 0.29–0.31 at 20–22° S and 26–32° S;
- 0.15–0.17 at 32–36° S;
- 0.14 at 18–20° S.

So one fraction is a smoothing choice, not a constant of the data. It removes the jump along the coast. In exchange, it puts the one layer up to 14 km deeper than the C14 median at 32–40° S, and 5–8 km shallower along the coast at 18–30° S. Per cell, new − C14: median +0.7 km, 5–95 % −7.7 to +14.0 km. Figure: `figs/2026-11-16b/maps_onelayer.png`.

Only the one layer changes. The three slices (weights and hypocentres) and the lower depth are those of run 2026-11-16.

## 2. Lower-depth options

Same hypocentres and weights as the reference; only `lsd` moves. So a tornado row shows only the effect of how deep a rupture can reach.

| option | fraction of the thickness | lsd − reference (median, range) | source |
|---|---|---|---|
| reference | 0.475 | | C14: 95 % of the events |
| `lsd065` | 0.65 | +13.0 km (2.6–15.0) | psha_chile7 rule |
| `lsd0615` | 0.615 | +10.4 km (2.1–12.0) | 95 % with ISC, CSN web and ComCat depths kept (C14 sensitivity) |

Both options are deeper than the reference, and both have a source. A shallower option has no source, so I propose none.

## 3. Top-slice weight over the shallow slab

`w1_check_2026-11-16b.csv` covers the 4 901 cells with the slab top at 50 km or less:
- **Width:** the top slice is 11.4 km wide (median) and lies inside the ± 15 km interface band in every cell. The class rule leaves it nearly empty of in-slab events there.
- **Weights:** from the shallow-slab events alone, w1 = 0.02 and w3 = 0.69. With all events, the kernel brings in the events under the deeper slab and gives w1 = 0.39, w2 = 0.37, w3 = 0.27. From the deeper-slab events alone, w1 = 0.41.
- **Meaning:** over the shallow slab the top-slice weight is not measured; it comes from the cells downdip. That is what a fix would have done by hand, so no change is proposed. The top slice there sits where interface events are, and that point belongs to the discussion of the double zone and the interface width, not to this table.

## 4. For S2

- **Reference tables:**
  - three layers: `tables/depth_cells_2026-11-16d.csv`;
  - one layer: the same file, which has the same columns plus `h_one_median` (the old C14 value, for comparison); `h_one` is the new rule.
- **Lower-depth options:** `tables/depth_cells_lsd065_2026-11-16d.csv` and `depth_cells_lsd0615_2026-11-16d.csv`. Their `h_one` is the new rule.
- **Not in this task:**
  - rupture-geometry options: S2. Note that S2 already uses StrasserIntraslab; the alternative in OpenQuake 3.26 is AllenHayesIntraslab;
  - the "negligible" threshold and the one-city check: they need source files, so S2 or S5;
  - the 500 km `pointsource_distance` run: S5.
- **South of 36° S:** few events (1 499 south of 36° S), and the median fraction drops to 0.04–0.11 south of 38° S. That is a reason to test one layer there. The decision waits for the hazard rows.

## 5. Proposed lines

- DECISIONS, In-slab, replace "One layer: the median of the zone" with: "One layer: top + 0.252 × the Slab2 thickness, the fraction that holds half of the events of the depth model; the per-cell median jumped about 10 km at the 50 km slab-top line, from the ± 15 km interface band (C15, 16 Nov; `depth_cells_2026-11-16b.csv`)."
- DECISIONS, In-slab: "Lower-depth options for the tornado: 0.65 (psha_chile7) and 0.615 (95 % with all depth sources), with the reference hypocentres (C15, 16 Nov)."
- Superseded: "One-layer hypocentre: per-cell median of the zone (C14) → top + 0.252 × thickness (C15, 16 Nov)."
- LEARNINGS: "Over the shallow slab the in-slab depth distribution near the top is set by the interface band of the classification, not by the data: per-cell statistics of in-slab depths jump at the 50 km slab-top line."

## 6. Sections

`figs/2026-11-16b/sections_layers.png` (21°, 30°, 33° and 38° S) shows the events, the zone, the slice limits, the three hypocentres sized by weight, and both one-layer versions. At 33° and 38° S the three-layer weights also switch at the 50 km slab-top line: the bottom slice is heavier updip of it and the top slice is heavier downdip. This is the same interface-band effect as in section 3, visible per cell even though the median over all shallow-slab cells (w1 0.39) does not show it.

## 7. Run 2026-11-16c: fixes, the 99 % question and more sections

- **Catalogue 2026-11-16c** (13 Scotia events to outer rise): no in-slab depth event changes.
- **Jujuy nest:** `depth.nest` tested the 0.8° radius without scaling the longitude by cos(lat), unlike `classify.py`. 15 Riedel-Hornig nest events (Ml 2.5–3.4, 190–260 km) had stayed in the depth set; now out. The catalogue nest events were already out (by `sub_inslab`).
- **Slices:** the slice masses and medians now come from the cumulative histogram, interpolated inside each 1 km bin. Before, a bin went whole into one slice, so a 0.0002 change of the fraction (0.014 km of lower depth) moved weights by up to 0.10 in cells far from the change. Against run 2026-11-16, per cell: weights 16–84 % within ± 0.02 (max 0.08), hypocentres ± 0.2 km (max 4.7). Held-out log-likelihood −0.794 → −0.791. New test: weights continuous in the lower depth.
- **95 % or 99 %:** the fraction of the thickness is 0.431 (90 %), 0.474 (95 %), 0.524 (97.5 %), 0.713 (99 %). The 99 % comes from the tails: 0.553 in Riedel-Hornig against 0.883 in the catalogue. It measures location error more than the seismogenic zone.
  - In-slab events of Mw ≥ 6.9 since 1964, shallower than 300 km: 17 of 18 lie inside 0.475. The one outside is 1971-05-08 Mw 7.2 at 42.3° S, 157 km (0.56 of the thickness). All 18 lie inside 0.65.
  - Chillán 1939: Slab2 top 58 km, thickness 68 km, so the zone bottom is at 90 km with 0.475 and at 106 km with 0.99 % fraction. The rupture (80–100 km, Beck et al. 1998) needs 0.62.
  - Proposal: keep 95 % as the reference, and let the 0.65 option, which contains Chillán and 1971, carry it in the tornado.
- **Sections 31–40° S** (`figs/2026-11-16c/sections_layers_south.png`, dash-dot line: slab top at 50 km): at 31–38° S the bottom slice is heavier updip of the line and the top slice downdip of it. Updip, the in-slab events start below the interface band; downdip, many events lie just under the slab top. South of 37° S there are few events and the weights come mostly from the kernel.

## 8. Run 2026-11-16d: events with their class weights

**Why.** Until 2026-11-16c the depth model kept only events of in-slab weight 1. Over the shallow slab (top ≤ 50 km), most events within the ± 15 km interface band carry mixed weights, so the in-slab events there were almost all deeper than 15 km below the top: 1 % of them lay within 15 km, against 26 % of the in-slab weight. The rates (fits, S2 pattern) sum the class weights, so the depth model now does the same (Pablo, 16 Nov).
- Catalogue: `w_inslab`.
- Riedel-Hornig: the in-slab weight of the A7 depth rule.

**Events.** 87 955 events with a total weight of 74 432, against 70 789 events of weight 1 in 16c. Events above the slab top by more than 15 km: 3 956 events, weight 309 (mostly crustal events with a small in-slab share).

**Fractions.**
- The 95 % fraction is 0.4715 (0.4744 in 16c), so the zone keeps its rule.
- The one-layer fraction is 0.243 (0.252 in 16c).
- Median d / thickness: 0.285 over the shallow slab against 0.234 over the deeper slab. Before the weights it was 0.363 against 0.234.

**The 50 km line, by slab-top depth band:**

| slab top (km) | 0–30 | 30–40 | 40–50 | 50–60 | 60–70 | 70–90 | 90–120 | 120–200 | > 200 |
|---|---|---|---|---|---|---|---|---|---|
| per-cell median below the top, 16c | 23.3 | 19.9 | 12.8 | 11.1 | 11.3 | 17.5 | 16.2 | 13.7 | 17.9 |
| per-cell median below the top, 16d | 17.3 | 17.7 | 18.0 | 18.1 | 18.8 | 19.2 | 18.3 | 17.4 | 20.1 |
| w1, 16c / 16d | 0.21 / 0.25 | 0.32 / 0.27 | 0.40 / 0.39 | 0.49 / 0.50 | 0.51 / 0.50 | 0.26 / 0.26 | 0.29 / 0.28 | 0.38 / 0.38 | 0.37 / 0.38 |
| w3, 16c / 16d | 0.46 / 0.31 | 0.36 / 0.28 | 0.26 / 0.20 | 0.15 / 0.13 | 0.14 / 0.14 | 0.24 / 0.24 | 0.27 / 0.27 | 0.26 / 0.25 | 0.27 / 0.27 |

- **The jump of the per-cell median is gone.** It was mostly the weight-1 cut.
- **What remains:** a heavy top slice (w1 0.50) in the strip where the slab top is 50–70 km deep. This is where the interface band fades (50–65 km), so events just under the top become in-slab. It may be the down-dip end of the interface seen as in-slab, and it is open for Pablo.
- **Shallow-slab events alone** now give w1 = 0.18 (0.02 before).

**Per cell against 16c:** lower depth −0.2 km. Weights 16–84 %: w1 −0.01 to +0.04 and w2 0.00 to +0.13. The largest changes, up to 0.6, are in the cells over the shallow slab.

**Held-out:** kernel −0.799, 50 nearest −0.818, equal shares −1.099, on 16 271 weighted test events. This is not comparable with 16c, because the test set changed.

**Figures** (`figs/2026-11-16d/`): `sections_layers.png` and `sections_layers_south.png`. Events are shaded by their in-slab weight, and cells are drawn within 7 km of a section; at 5 km, the 0.1° grid left empty columns along oblique sections, for example at 35° S near 160 km.

**For S2 and the tornado** (Pablo, 16 Nov): only "three layers against one layer" is needed. The three-layer reference stays as in the S2 files (`depth_cells_2026-11-16.csv`). The one-layer branch reads `h_one` of `depth_cells_2026-11-16d.csv`: top + 0.243 × thickness.

**Proposed DECISIONS lines (replace those of section 5):**
- In-slab, depth events: "class weight 1" → "each event with its in-slab class weight, as in the rates (catalogue `w_inslab`, Riedel-Hornig by the A7 depth rule) (C15, 16 Nov, run 2026-11-16d)".
- One layer: "top + 0.243 × the Slab2 thickness, the fraction that holds half of the in-slab weight of the depth model (C15, 16 Nov)".
