# C14: in-slab depth model, three layers below the slab top

Run `2026-11-15e` (15 Nov 2026), after Pablo's revisions of the method the same day. Code `model/inslab/`: `depth.py` (library), `bench.py` (step 1), `run.py` (steps 2–4, settings at the top), `figs.py`. Tests in `model/inslab/tests/` (9 pass). Cell table `tables/depth_cells_2026-11-15e.csv` (13 847 cells). Figures in `figs/` (pituPLOTS b9be58a). The frozen catalogue is read, never changed (its 15 checksums still hold); only the choice of events and depths for the depth model is made here.

## 1. What the model is and what it shows

**What a source gets.** Every in-slab point source has one seismogenic zone (upper depth = Slab2 top, lower depth = top + 0.475 × Slab2 thickness) and one hypocentre distribution: three depths with three weights (OpenQuake `hypoDepthDist`). Ruptures are not confined to a layer: OpenQuake centres each rupture on its hypocentre and keeps it inside the zone, so large ruptures cross the layers and fill the zone (section 3). The one-layer alternative has the same zone and a single hypocentre.

**How it is built** (Pablo, 15 Nov):
1. Each in-slab event gives its distance below the Slab2 top, d = depth − top.
2. **Lower depth:** the fraction of the Slab2 thickness below the top that holds 95 % of all events, one number for the margin: **0.475** (`tables/fraction_2026-11-15e.csv`). Zone = top to top + 0.475 × thickness.
3. **Layers:** the zone cut into three slices of equal thickness (for a thickness of 85 km: 0–13.5, 13.5–27, 27–40 km below the top). They only serve to build the hypocentre distribution.
4. **Weights:** the distances are spread onto the grid with the kernel of the in-slab rate pattern (psha_chile7 and DECISIONS: 1 / (r² + h²)^1.5, h the distance to the 25th neighbour, at least 5 km, out to 500 km). Each cell's weight per slice is the share of that smoothed distribution in the slice; events above the top count in the top slice, events below the zone are not counted; one event is added to each slice (Laplace's rule) so no weight is 0.
5. **Hypocentres:** the median d in each slice, the slice middle where fewer than 5 events fall in it. One layer: the median of the zone.

**Events** (`tables/events_log_2026-11-15e.csv`; each event once, at its depth):
- Final catalogue, in-slab with class weight 1, measured depth, from 1990 (start of the old in-slab rate pattern), Jujuy nest out, Potin / CSN web depths east of the Chile border out, events also in Riedel-Hornig counted there, depths from ISC, CSN web (and its ISC copy) and ComCat out: 30 150 events (Potin 28 097, ISC-EHB L1 1 313, L2 733, GCCEL 6, ISC-GEM 1).
- Riedel-Hornig, for the depths only, inside Chile: Ml ≥ 2.5, depth error ≤ 5 km, slab at the epicentre, east of the trench, not in the nest, in-slab by the A7 depth rule with weight 1: 40 654 events.
- ISC, CSN web and ComCat are out because their distances below the top have long tails: 95 % within 91, 56 and 66 km, against 35–40 km for Potin, ISC-EHB and Riedel-Hornig (Pablo, 15 Nov). With them in, the fraction would be 0.615 and the lower depth 10 km deeper (`tables/sensitivity_all_depths_2026-11-15e.csv`).

**Is 0.475 representative?** The same fraction comes out of the catalogue (0.475) and Riedel-Hornig (0.474) separately; in every 2° band from 16 to 36° S (0.46–0.50); for every magnitude (catalogue Mw < 3.5 to ≥ 6.5: 0.49–0.55; Riedel-Hornig Ml 2.5 to ≥ 4: 0.474–0.480); and for every period (0.45–0.56). The 5 % below the zone (3 514 events) lie a median 4 km below it, three quarters within 13 km. They cluster over the shallow slab south of 34° S (44–60 % of the events there; mostly Potin depths, poor south of 36° S and offshore) and at 22–26° S under a slab top of 100–150 km (60 % of 372 events; not resolved).

**Large in-slab events as a reference.** 16 of the 17 events of Mw ≥ 6.9 since 1964 with an ISC-EHB depth (Jujuy nest aside) have their hypocentre inside the zone, at a median 0.20 of the thickness below the top; 1971-05-08 at 42° S is 5 km below it. Tarapacá 2005 (Mw 7.8; hypocentre 105 km, zone 85–125 km): the published rupture lies at 90–115 km (a low-angle plane about 50–70 km long, or a sub-horizontal plane of about 60 × 30 km): inside. Calama 1950 (Mw 8.0; 114 km, zone 101–140 km): inside. Chillán 1939 (Mw 7.8; zone 59–91 km at the catalogue epicentre): Beck et al. (1998) model a normal fault at 80–100 km, up to about 9 km below the zone, within the uncertainty of its epicentre and depth. The rupture extents come from search summaries of the papers, which are not in `refs/`; to be read before citing.

**The zone** (`figs/maps_zone.png`, `tables/depth_summary_2026-11-15e.csv`): 40 km below the top at 16–22° S, 37–40 km at 22–30° S, 34–35 km at 30–34° S, 30–34 km at 34–40° S, 19–28 km south of 40° S and 12 km offshore over the thin slab at 44–46° S. It is 4–15 km shallower than the old 0.65 of the thickness everywhere (same rule, smaller fraction). The mean hypocentre is within −7 to +2 km of the old one (0.30 of the thickness) from 20 to 34° S and mostly 4–14 km shallower at 16–20° S and 34–42° S.

**Held-out check** (`tables/heldout_2026-11-15e.csv`; built from the events before 2020, scored on the 14 861 events of 2020–2021 inside their cell's zone): kernel −0.794 per event, 50 nearest events −0.784, equal shares −1.099.

**Where the double zone shows** (`figs/maps_weights.png`, `figs/sections_cells.png`, `figs/hist_d_lat.png`):
- **20–24° S:** the bottom slice is heavier than the top (0.28–0.46 against 0.17–0.24): the lower plane of the northern double zone. Its upper plane falls in the middle slice at these depths, so the double-zone index (mean of top and bottom minus middle, −0.12 to +0.04) understates it; the weights carry it.
- **24–34° S under a slab top of 50–150 km:** middle slice heaviest (0.41–0.52): one zone, including the flat slab.
- **Shallow slab (top ≤ 50 km) at 26–36° S:** bottom slice heaviest (0.50–0.64): the seismicity sits in the lowest third of the zone, about 22–38 km below the top.
- **34–42° S under a slab top deeper than 50 km:** top slice heaviest (0.45–0.73): seismicity close to the slab top.
- **16–20° S under a slab top shallower than 150 km:** top slice heaviest (0.49–0.62).
- The central-Chile double zone is not seen; east of the border only ISC-EHB depths remain.

**Against the first version** (`tables/compare_v1_2026-11-15e.csv`): lower depth a median 22 km shallower, hypocentres 1–7 km shallower in the median, weights within 0.07.

## 2. The benchmark (step 1)

**The catalogue of Riedel-Hornig et al. (2026)** (Zenodo 10.5281/zenodo.15284376; `tables/rh_summary.csv`): 621 917 automatic, relocated events, 2017–2021, 18.1–41.9° S, depth 0–331 km, local magnitude Ml 0.3–7.0 (Ml ≥ 2.5, their completeness: 131 200; Ml ≥ 4: 5 507). Depth error: median 4.7 km (5–95 %: 2.2–14.5); 4.5 km inside Chile, 8.4 km east of the border; 9.4 km at 150–300 km depth. Their classes: in-slab 459 739, crustal 75 534, interface 59 061, unclassified 20 208, outer rise 7 375.

**Matching** to the frozen catalogue (origin time within 10 s, epicentre within 50 km, one to one, closest first; `tables/rh_match_rates.csv`): 19 042 of 22 668 catalogue events of 2017–2021 at 18–43° S with an Mw. By depth: 95 % at 70–150 km, 87 % at 150–300 km, 75 % at 0–70 km. By latitude: 85–96 % from 18 to 36° S except 26–28° S (49 %); 21–45 % south of 36° S, where the Riedel-Hornig primary catalogue thins out. Mw ≥ 4.5: 74 %.

**Depth differences, source minus Riedel-Hornig** (median and robust spread 1.48 × MAD, km; `tables/rh_benchmark.csv`, `tables/rh_benchmark_lat.csv`, `figs/bench_depths.png`):

| source | 0–70 km | 70–150 km | 150–300 km | ≥ 70 km in Chile | ≥ 70 km east of the border |
|---|---|---|---|---|---|
| Potin / CSN web | −1.8 (4.8) | −2.8 (4.3) | −8.6 (16.2) | −3.0 (4.5) | −5.1 (13.5) |
| Potin alone | −2.2 (3.9) | −3.6 (3.6) | | | |
| CSN web alone | +1.1 (7.3) | +0.1 (5.3) | | | |
| ISC-EHB L1 | −1.0 (5.3) | −3.8 (5.6) | −28.9 (21.9) | −3.3 (5.1) | −22.2 (17.5) |
| ISC-EHB L2 | −3.2 (6.6) | −5.8 (9.4) | −23.5 (16.1) | −5.8 (10.1) | −22.8 (16.1) |
| ISC | −11.7 (11.5) | +1.5 (7.5) | −13.7 (16.0) | +1.4 (7.5) | −12.3 (16.1) |
| GCCEL (99 events, nearly all < 70 km) | −3.6 (5.2) | | | | |

By distance from the trench: Potin and ISC-EHB L1 agree within 1–4 km out to 300 km, ISC is 14 km shallower within 100 km of the trench (offshore); beyond 300 km ISC-EHB L1 is 20–37 km and ISC 12–14 km shallower than Riedel-Hornig. In the flat slab (27–33° S) inside Chile, ISC-EHB L1 is −2.6 km at ≥ 70 km; east of the border −32 km.

**The eastern hypocentres are too deep** (their p. 12–13). Shown: east of the Chile–Argentina border every teleseismic depth is shallower than Riedel-Hornig, and the gap grows with distance east (`figs/bench_depths.png`, lower right, median of ISC-EHB L1 and ISC at 27–33° S: about 0 at the border, −25 km 75 km east, −45 to −50 km 120–160 km east). It is not limited to the flat slab: at ≥ 70 km depth east of the border ISC-EHB L1 is −14 to −40 km in every 2° band with data from 22 to 34° S, and −20 km north of 27° S. Inside Chile the same sources agree within 3–4 km. Their own test with INPRES picks (their Fig. 10) moves these events up in the same direction.

**Potin under the flat slab agrees with Riedel-Hornig, but that does not test it.** Potin / CSN web minus Riedel-Hornig at ≥ 70 km in the flat slab is −2.3 km (spread 7) east of the border and −2.0 km inside Chile. Both are located with Chilean stations only, and both are 20–30 km deeper than ISC-EHB L1 there: they share the same network geometry and the same bias. The earlier finding that Potin is 25–60 km too deep under the flat slab (LEARNINGS, X1) stands; Riedel-Hornig cannot confirm or clear it.

**Should Riedel-Hornig become a location source of the catalogue for 2017–2021?** Not on this evidence. Against GCCEL (99 shallow events) the catalogue is closer than Riedel-Hornig in epicentre (median 3.6 against 4.4 km) and in depth (+0.6 against +3.6 km; spread 1.9 against 5.4 km) (`tables/rh_locations_gccel.csv`). Inside Chile its depths agree with Potin within 2–4 km, so replacing Potin there would change little; east of the border it is too deep, like Potin. Its value is the number of small, consistently located events and the uniform coverage of 2017–2021 after Potin ends (July 2020), where the catalogue falls back on CSN web depths (spread 5–7 km against Riedel-Hornig, twice Potin's). If anything, Riedel-Hornig could replace CSN web for July 2020 – December 2021 inside Chile; that is a small gain and a new source rule, so I leave it open.

## 3. Choices made, with proposed DECISIONS lines

- **Lower depth:** one fraction of the Slab2 thickness for the margin (0.475, the 95 % of all events), the rule of psha_chile7 with the fraction measured on the new depths (Pablo, 15 Nov). Two earlier versions of the same day were dropped: the 95 % per cell (followed sparse and noisy tails, 30–124 km) and the same capped at the Slab2 bottom (too deep to stand for the seismogenic depth).
- **Layers and weights:** equal thirds of the zone; weights from the kernel of the rate pattern (no new parameter).
- **Period:** depths from 1990 on.
- **Depth sources:** final catalogue depths without ISC, CSN web and ComCat (Pablo, 15 Nov), plus Riedel-Hornig inside Chile for the depths only. Local-network depths east of the Chile border are out (benchmark, section 2). The listed σ is not used to select: it is set per source and depth range in `catalog/locate.py`, so a cut on σ is a cut on depth (Potin would enter only at 30–70 km).
- **Interface events kept out:** catalogue by class weight 1 (split events not used); Riedel-Hornig by the A7 depth rule (Haynie et al. scores, ± 15 km band over a slab top ≤ 50 km), weight 1 only: 40 654 of 58 526 events kept. In the first version's tally of the same rule, 14 403 of the Riedel-Hornig weight went to interface (8 645 from their own "Interplate" class, 3 576 from their "Intraslab" class: the thrusts 5 km below Slab2, LEARNINGS X5) and 2 280 to crustal (`tables/rh_interface_removed.csv`).

**How OpenQuake places the ruptures** (read in the installed 3.26: `openquake.hazardlib.geo.surface.planar.get_rupdims` and `_build_corners`). The rupture is centred on the hypocentre (down-dip fraction 0.5). If its width times sin(dip) is more than the zone, the width is cut to the zone and the length grows to keep the area; if the rupture then crosses the upper or lower depth it is shifted vertically to lie inside. So a large rupture fills the zone from the slab top to the lower depth whatever slice its hypocentre is in; a small rupture stays centred on its hypocentre. With a zone of 30–40 km, ruptures of about Mw 7.3–7.5 and larger fill it (Strasser et al. 2010 in-slab area, aspect ratio 1, the 60° plane; Mw 7: height about 27 km). The DECISIONS line of 13 Nov holds. Caution for C15: a collapsed point source (`ps_grid_spacing`) and the far-site approximation (`iruptures`, for sources with more than one nodal plane or hypocentre) average the hypocentral depths into one, so the three hypocentres act only at sites within the point-source distance.

**Proposed DECISIONS lines (In-slab):**
- "In-slab depth model (C14, 15 Nov): seismogenic zone from the Slab2 top to 0.475 of the Slab2 thickness below it (the fraction that holds 95 % of the in-slab events; the same in the catalogue and in Riedel-Hornig, at every latitude 16–36° S and every magnitude). Inside it three equal slices give the hypocentre distribution: weights the share of the events in each slice, smoothed with the kernel of the rate pattern (plus one event per slice), hypocentres the median in each slice. One layer: the median of the zone. Ruptures are not bound to a slice."
- "Depths of the in-slab depth model: the final catalogue from 1990, class weight 1, without ISC, CSN web and ComCat depths (long tails below the slab), and Riedel-Hornig et al. (2026) inside Chile (Ml ≥ 2.5, depth error ≤ 5 km), for depths only. Local-network depths east of the Chile border are left out: they are 10–50 km deeper than ISC-EHB L1 there at every latitude from 22 to 34° S (Pablo, 15 Nov)."
- "Riedel-Hornig et al. (2026) is not a location source of the catalogue (C14 benchmark)."

**Proposed LEARNINGS lines:**
- Pitfalls, catalogue: "The listed depth σ of the frozen catalogue depends on source and depth range; a cut on σ is a cut on depth. Select depth sources, not σ values, when the depth is the quantity (C14)."
- Pitfalls, catalogue: "Riedel-Hornig and Potin agree under the flat slab because both use Chilean stations only; both are 20–30 km deeper than ISC-EHB L1 east of the border. Agreement of two local catalogues is no test there (C14)."
- In-slab: "A 95 % depth per place follows the worst depths and the sparse areas (30–124 km below the top); one fraction of the Slab2 thickness (0.475) holds along the margin, across magnitudes and in both depth sets (C14). Old fraction 0.65 → 0.475; old hypocentre fraction 0.30 ≈ the new mean hypocentre."

## 4. Open points

1. **South of 36° S the in-slab events thin out** (Pablo): 5 874 events at 34–36° S, 1 054 at 36–38° S, 445 at 38–42° S, 20 south of 42° S. The zone there follows Slab2 thickness, but the weights come largely from the events at 33–36° S (the kernel reaches 500 km). One layer may be the honest choice there; for C15.
2. **Events below the zone:** concentrated over the shallow slab south of 34° S (Potin depths) and at 22–26° S under a slab top of 100–150 km; the latter not resolved.
3. **Chillán 1939** reaches about 9 km below the zone in Beck et al. (1998); to read the paper and recheck its epicentre against Slab2.
4. **Northern double zone in the index:** the upper plane falls in the middle slice; the index shows the lower plane only. The weights carry both.
5. **Central Chile double zone** not seen; east of the border only ISC-EHB depths remain.
6. **Small events stand for large ones:** the fraction holds across magnitudes, but the weights come mostly from Ml 2.5–4.5.
7. **Jujuy nest cells** take weights from the surrounding non-nest events; the nest source may need its own depths.
8. **Riedel-Hornig matching** finds only 49 % of the catalogue events at 26–28° S and 21–45 % south of 36° S; not looked into.
