# Interface segmentation (proposed, CAT_03, 20 Nov 2026)

This is a proposal for the orchestrator, not yet a decision. It replaces the limits of D-IF-03 north of Los Vilos and extends the interface from 17.1° to 15.5° S. The frozen shapes are not changed until DATA draws the new footprints. Working notes and maps are in `orchestration/CAT.md` (CAT_03, Addenda 1–5) and `trials/segment_limits/`.

## Why two branches
- Geometry can inhibit multisegment ruptures, but it does not prohibit them:
  - Abrupt changes of dip or strike raise the chance that simulated Mw 8–9 ruptures stop (herrera_2024, abstract only).
  - Ruptures still cross barriers: 1730 crossed 29.9° and 32° S (ruiz_2018 Fig. 2; molina_2021 p. 20).
- Neither model captures this behaviour on its own:
  - The segmented model stops every rupture at a limit.
  - The full-margin model ignores the limits.
- So the two are kept as end-members, 0.5 / 0.5 (D-IF-03).
- PSHA could represent the behaviour with rates for each rupture extent, but those rates are hard to get without synthetic catalogues.

## Segments (° S)
15.5 | 19.1 | 23.3 | 26 | 29.9 | 32 | 37 | 45.55

| Segment | Limits | Ruptures inside | Basis |
|---|---|---|---|
| Southern Peru–Arica | 15.5–19.1 | 1604, 1784, 1868, 2001 | 15.5° S: box edge, Ilo (contreras-reyes_carrizo_2011 p. 52). 19.1° S: barrier of molina_2021 p. 18; the 1868 / 1877 limit (comte_1991 Fig. 1; ruiz_2018 Fig. 1); the Arica bend (bejarpizarro_2013 p. 465; vigny_2022 p. 12) |
| Northern Chile (1877) | 19.1–23.3 | 1877, 2014, 2007 | 23.3° S: Mejillones (metois_2013 p. 7; victor_2011 pp. 3, 17; molina_2021 p. 18); 1877 and 2007 end there and 1995 starts there |
| Antofagasta | 23.3–26 | 1995, 1987, 1966 | 26° S: north end of 1922 and 1819 (metois_2014 p. 2; klein_2018 Fig. 1b; bravo_2026 p. 44); nishenko_1985 p. 3606; ruiz_2018 p. 43 |
| Atacama | 26–29.9 | 1819, 1918, 1922, 1946, 1983 | 29.9° S: La Serena low-coupling zone (metois_2014 p. 9; molina_2021 p. 18); Challenger fracture zone (contreras-reyes_carrizo_2011 p. 55) |
| Illapel | 29.9–32 | 1880, 1943, 2015, 1971 | 32° S: Los Vilos; Juan Fernández Ridge (contreras-reyes_carrizo_2011 p. 53; metois_2016 p. 1439) |
| Central | 32–37 | 1822, 1906, 1985, 2010 (north part) | unchanged |
| Southern | 37–45.55 | 1960, 1837, 1575 | unchanged |

## Drawing
Each limit is a line through the limit latitude at the trench, running perpendicular to the trench, down the Slab2 dip direction to the bottom edge (Pablo, 20 Nov).
- At Arica (19.1° S) the trench strikes about N36°W, so a cut along the parallel would move the down-dip end by about 120 km. The same applies at 15.5° S.
- At the other limits the two ways differ by 9–28 km.

## Limitations
- 1730 (about 28.6–36.4° S) fits only in the full-margin branch.
- 19.1° S is the least certain limit. giovanni_2002 sees a gap at 18.1–19.9° S, and contreras-reyes_carrizo_2011 treat 15.5–23.5° S as one gap.
- 26° S lies about 70 km south of the Taltal coupling low (25.1–25.6° S; klein_2018; molina_2021). It was kept so that the Antofagasta segment is large enough to fit (Pablo).
- 1877 may be only about 20.5–22.5° S, Mw ~8.5 (vigny_2022; metois_2013) rather than about 19–23° S. That matters for Mmax, not for the limits.
