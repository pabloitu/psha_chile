# A3 matching: method, references and checks

Code: `catalog/match.py` (settings at the top). Run of 2026-11-11 on the tables frozen 2026-11-10 (GCCEL 2026-11-11).
One record = one event of one source, placed by its preferred origin (GCMT: the reference hypocentre, never the centroid). Magnitude is never a matching criterion; it only widens windows and sorts review lists.

## Steps

1. **Identity links.** ISC-EHB by ISC origin ID, ISC-GEM and CSN-in-ISC by ISC event ID, ComCat by its `iscgem` IDs. Then each agency's own solution found inside an ISC event within 1.5 s and 10 km: NEIC / USCGS / NEIS and GUC / SJA / LIM for ComCat (ComCat lists Chilean and Argentine solutions as its own preferred origin for 10 800 events), GCMT, CENT, GUC for CSN web. The ISC grouping of reported hypocentres into events is the reviewed association of the ISC Bulletin (Bondár and Storchak 2011; Storchak et al. 2017, 2020).
2. **Windows per pair of sources.** 99th percentile of the offsets of known same-event pairs from 1964 on (identity groups, plus one-to-one nearest pairs for the sources without IDs), floor 10 s / 50 km, cap 120 s / 450 km; at least 100 pairs, else combined through the best shared source. × 1.5 / 2 / 3 at M 6 / 7 / 8 (largest native magnitude). Before 1964: 60 s / 300 km, all reviewed. Published fixed windows for comparison: 10 s / 20 km for regression pairs (Lolli et al. 2014), 60 s / 100–110 km for merging (Gasperini et al. 2013; Weatherill et al. 2016), 10 min / 50 km (Cabello et al. 2025). Ours are measured per pair instead of assumed.
3. **One-to-one assignment.** Single records are attached source by source to the existing events that lack that source. Cost = hypot(Δt / T, Δd / D); the assignment that minimizes the total cost in each connected block of candidates is found with the Hungarian method (Kuhn 1955; implementation of Crouse 2016 in SciPy). Blocks are the connected components of the candidate graph, so the result does not depend on how time is cut.
4. **Second pass.** Events that share no source and have members within 10 s / 50 km (scaled; 60 s / 300 km before 1964) are merged, closest first.
5. **Same source twice.** Two events that share sources are merged only if, for every shared source, the two records lie within 2 s (scaled) and 50 km: one earthquake listed twice by a source. 2 s is the 99th percentile of the origin-time difference between two solutions of the same network (CSN web vs CSN in ISC 1.0 s; Potin vs CSN 1.9 s).
6. **Non-earthquakes** flagged by a source are dropped with every record matched to them, without exceptions.
7. **Single-source duplicates.** An event with records of Potin only or of CSN web only is removed when an event with an ISC record lies within 30 s and 50–150 km of it, the two share no source, neither has another event within 30 s / 150 km, and the larger native magnitude is at least 4.5 (`LONE`, `LONE_D`, `LONE_M`; `lone_dups`). These are the true pairs wider than the windows that the blind check predicts; the ISC event stays, with its teleseismic location. Listed in `review/dropped_duplicates` (45 in the run of 11 Nov: 38 Potin, 7 CSN web).
8. **Ruiz and Madariaga (2018)** is attached last (dates corrected, ± 1 day, 2° latitude, M ≥ 5.5, closest Mw).

Review lists follow the record-linkage practice of sending uncertain links to clerical review instead of deciding them (Fellegi and Sunter 1969).

## Where this differs from the brief, and why

Accepted by Pablo on 11 Nov 2026.

| point | brief | done | evidence |
|---|---|---|---|
| distance of a record to an event | to its best-located member | to its closest member, each with the window of its pair of sources | blind check over six sources (122 308 records): 8 wrong and 506 missed, against about 210 and 990 with the reference-only rule (measured before the last fixes); Potin records of badly located CSN events (251 events, up to 900 km) would otherwise become events of their own |
| attach order | best-located source first | leftovers of the sources with identity links first, then GCCEL, Potin, CSN web; single records of later sources are not targets | Potin lists the Iquique 2014 mainshock twice; attached first, the second copy took the GCCEL record and split the mainshock. The reference member is still the best-located source |
| second pass before 1964 | 10 s / 50 km | 60 s / 300 km | M 7.1–7.5 events of 1909, 1910, 1911, 1912 and 1917 were split between ISC-GEM / ComCat and Centennial / ISC (up to 13 s, 259 km) |
| one source twice in an event | not covered | step 5, and identity links inside one ISC event | unreviewed ISC Bulletin 2025–2026 lists M 5–7 events twice (26 cases), Potin 24, CSN web 28, ComCat 4; all in `review/same_source` |
| ComCat identity agencies | NEIC, USCGS, NEIS | plus GUC, SJA, LIM | ComCat's own preferred origin is the GUC solution for 10 548 events |
| windows from | all known pairs | pairs from 1964 on, ≥ 100 pairs | pairs before 1964 have their own rule; a 99th percentile of 84 pairs gave 31 s / 450 km for Centennial vs CSN-in-ISC |

Switches: `LINK = "ref"` gives the brief's distance rule; `SAME_T = 0` switches step 5 off; `STAGES` sets the order; `KEEP` keeps a flagged non-earthquake.

## Checks (every run writes them)

- **Partition** (`check`): every origin of the inputs is in exactly one event or in `dropped_types` / `dropped_duplicates`; a source event is never in two events.
- **Blind recovery** (`check_blind`): the records of a source with identity links are taken out of the final events and matched again by time and distance only. The identity link is the truth. Wrong ≤ 0.04 %, missed 0.07–0.76 % per source. The misses are true pairs further apart than the windows (mostly > 50 km at the same time); this is the expected miss rate for Potin and CSN web, which have no IDs.
- **Chance matches** (`check_chance`): a source is shifted by ± 10 and ± 20 min and matched to the final events; none of those matches can be real. Potin 160 per 118 003 records (0.14 %; 38 per 5 411 at M ≥ 4.5), CSN web 23 per 55 549. This bounds the false-merge rate of records that have no true partner. The same idea is used to rate accidental associations in catalogue cross-identification (Sutherland and Saunders 1992; Budavári and Szalay 2008).
- **X1 diagnostics** (`review/x1_splits`, `x1_false_merges`), same definitions as X1.
- **Possible splits** (`review/possible_splits`): events with no common source within 30 s / 150 km that step 7 did not remove (7: ISC against CSN web + ComCat or ComCat alone, a Potin record 25 km away, and two pairs with other events nearby); **close events** (`review/close_events_m45`): events within 10 s / 50 km that share a source.
- Unit tests: `catalog/tests/test_match.py` (34).

## References

In `REFERENCES.md` / `LITERATURE.md` already: Cabello et al. (2025); Gasperini et al. (2013); Lolli et al. (2014); Weatherill et al. (2016), doi:10.1093/gji/ggw232; Ruiz and Madariaga (2018).

New, to add to `REFERENCES.md`; bibliographic data from memory, DOIs not checked:
- Bondár, I., Storchak, D. (2011). Improved location procedures at the International Seismological Centre. Geophys. J. Int. 186, 1220–1244.
- Budavári, T., Szalay, A. S. (2008). Probabilistic cross-identification of astronomical sources. Astrophys. J. 679, 301–309.
- Crouse, D. F. (2016). On implementing 2D rectangular assignment algorithms. IEEE Trans. Aerosp. Electron. Syst. 52(4), 1679–1696.
- Fellegi, I. P., Sunter, A. B. (1969). A theory for record linkage. J. Am. Stat. Assoc. 64, 1183–1210.
- Kuhn, H. W. (1955). The Hungarian method for the assignment problem. Nav. Res. Logist. Q. 2, 83–97.
- Storchak, D. A., et al. (2017, 2020). Rebuild of the Bulletin of the International Seismological Centre (ISC), parts 1 and 2. Geosci. Lett. 4:32; 7:18.
- Sutherland, W., Saunders, W. (1992). On the likelihood ratio for source identification. Mon. Not. R. Astron. Soc. 259, 413–420.
