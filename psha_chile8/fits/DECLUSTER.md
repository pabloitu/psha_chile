# Declustered catalogues and their fits (B12)

15 Nov 2026. Brief `tasks/B12_declustered.md`. Input: the frozen catalogue `catalog/frozen/2026-11-14/catalog_2026-11-14c.csv` (unchanged). Code: `decluster.py` (methods), `run_declustered.py` (completeness, fits, comparison), `figs_declustered.py`; tests `tests/test_decluster.py` (10 tests). The fits use `run.py` and `gr.py` unchanged, after step 0 (section 7 of `FITS.md`: Mmax = largest event + 0.2 everywhere, corner from Kagan 2002b).

Revised the same day after Pablo's reply: Gardner–Knopoff and nearest neighbour are two options of one factor, each run the same way in every family. Nearest neighbour per family, keeping the largest event of each cluster, was added for that (`nn_family`). The other variants stay in the files for comparison.

Outputs:
- catalogues `catalog/declustered/<method>_2026-11-15.csv`: event_id, mw, mainshock, cluster (event_id of the cluster's mainshock); the nearest-neighbour files also parent and log10 η. The same from Mw 3.5 as `<method>_m35_2026-11-15.csv`, used only for the completeness rule.
- `tables/fits_declustered_2026-11-15.csv`: the columns of `fits_2026-11-15b.csv` plus `method` (full, gk, gk_family, nn, nn_depth, nn_family), `table` (completeness table used: full or declustered), `b_option` (own, or shared by the four segments), `family_b`, `family_tau`. The full catalogue is in the file too (method "full"), with its shared-b segment fits.
- `tables/declustered_tables_`, `declustered_removed_`, `declustered_compare_` (b, N, checks, Fano factors), `declustered_floor_2026-11-15.csv`.
- `figs/declustered_fmd.png`, `declustered_b_floor.png`, `declustered_N7.png`.

## 1. The methods and what they remove

The two options of the factor:
- **gk_family, Gardner–Knopoff per family.** Gardner and Knopoff (1974) with the windows of van Stiphout et al. (2012), largest event first, foreshock window equal to the aftershock window, run separately inside each class family (interface, in-slab, crustal, other; each event in the family of its largest class weight). Keeps 42 % of the 14 279 events of Mw ≥ 4.5.
- **nn_family, nearest neighbour per family.** Zaliapin and Ben-Zion (2013), b 1, d_f 1.6, epicentral distance; proximities computed inside each family, one threshold fitted on all of them (two-Gaussian mixture of the events from 1964: log10 η −5.75). A cluster is a tree of links below the threshold, and its largest event stays. Keeps 77 %.

Both run from Mw 4.5 over the whole span. Per family, no event is removed because of an event of another family (DECISIONS, Crustal: no removal of crustal events after interface mainshocks).

Share of each class removed (class weights summed), gk_family / nn_family:

| class | Mw ≥ 4.5 | Mw ≥ 5.5 | Mw ≥ 7.0 |
|---|---|---|---|
| interface | 74 / 51 % | 60 / 49 % | 17 / 17 % |
| in-slab, shallow | 50 / 21 % | 28 / 19 % | 8 / 7 % |
| in-slab, intermediate | 47 / 4 % | 21 / 5 % | 2 / 2 % |
| Jujuy nest | 88 / 9 % | 59 / 7 % | 0 |
| crustal, forearc | 51 / 35 % | 27 / 28 % | 13 / 13 % |
| crustal, arc | 40 / 22 % | 35 / 19 % | 0 |
| crustal, backarc | 32 / 20 % | 44 / 39 % | 0 |
| crustal, Patagonia | 25 / 12 % | 26 / 13 % | 33 % (one event of three) |

On the interface the two methods remove a similar share of the large events and differ at the small ones. In the in-slab classes Gardner–Knopoff removes half of the intermediate events and almost all of the Jujuy nest; nearest neighbour removes 4–9 %. The Gardner–Knopoff windows at Mw 4.5 (about 35 km and 80 days) are wider than the spacing of events in these dense zones, so independent events go with the clusters.

**The large events.** Both options keep the largest event of a cluster.
- gk_family removes 4 of the 74 events of Mw ≥ 7.5: the 1960 foreshocks of Mw 8.1 and 7.8, 1878 Mw 7.9 after 1877, and the second 1949 Magallanes event.
- nn_family removes 7: the same four, Iquique 2014's Mw 7.7 aftershock, and two links across decades. 1657 Mw 8.0 is put in the cluster of 1751 Mw 9.0 (94 years apart), and 1975 Mw 7.7 in that of Valdivia 1960. The threshold is set on the dense record after 1964, and in the sparse old record a pair of great earthquakes can fall below it. Reported, not patched.

**The variants kept for comparison:**
- **gk (Gardner–Knopoff, all classes together):** keeps 36 %. It removes crustal and in-slab events after interface mainshocks: 57 % of its crustal removals have a mainshock of another family. On the interface it is within 0.03 in b and 5 % in N(≥ 7) of gk_family.
- **nn and nn_depth (nearest neighbour all together, the first event of a cluster kept; B9's setting):** keep 70 %. They drop great mainshocks in favour of foreshocks: Valdivia 1960 (its Mw 8.1 foreshock is kept), 1877 Mw 8.9, 1922 Mw 8.5, 1985 Mw 7.9 and Iquique 2014 Mw 8.1. N(≥ 8) of the interface then falls to half (0.017 against 0.032). This is why nn_family keeps the largest event. Depth changes nearly nothing (thresholds −5.52 and −5.32).

**Synthetic tests** (`tests/test_decluster.py`; mainshocks Poisson in space and time over the margin, aftershocks inside 0.15 of the window distance and 0.3 of the window time, smaller than their mainshock):
- Sparse catalogue (600 mainshocks in 60 years): Gardner–Knopoff, all together and per family, recovers the mainshock count within 5 %, every aftershock pointing to a true mainshock. Nearest neighbour does so with a threshold in the gap between the two modes (log10 η −4.0).
- With the mixture threshold, nearest neighbour takes 5–15 % of the mainshocks as clustered: the equal-posterior point lies in the lower tail of the background mode. The test records this; the setting was not changed. Per family, no link crosses a family and the largest event of a cluster is a true mainshock in more than 95 % of cases.
- At the density of the real catalogue (6 000 mainshocks in 60 years, one-off run): Gardner–Knopoff −10 % (per family −3.5 %, families drawn at random), nearest neighbour −10 to −11 %. For Gardner–Knopoff the loss is chance overlap of independent events inside the windows, a property of the method.

The flags from Mw 4.5 and from Mw 3.5 agree for 99.9 % (Gardner–Knopoff) and 98 % (nearest neighbour) of the events of Mw ≥ 4.5.

## 2. Completeness and fits

**Completeness** (`table.py` on the declustered events from Mw 3.5):

| catalogue | table |
|---|---|
| full | 5.0 from 1976, 5.2 from 1964, 7.0 from 1905, 7.5 from 1830, 8.0 from 1500 |
| Gardner–Knopoff (both) | 5.0 from 1976, 5.1 from 1964, 6.0 from 1950, 6.5 from 1890, 7.0 from 1825, 8.0 from 1500 |
| nearest neighbour (all three) | 5.0 from 1976, 5.1 from 1964, 6.0 from 1950, 6.5 from 1900, 7.0 from 1830, 8.0 from 1500 |

The instrumental steps hardly move. The historical steps move by up to 80 years and 1.0 unit, so both fits are in the table (column `table`). Declustering lowers the instrumental line, and the rate rule is one-sided (LEARNINGS): it accepts old counts that sit above a lower line, so bands 6.0 and 6.5 become complete before 1964 and 7.0 about 80 years earlier. On the declustered table the interface N(≥ 7) is 10–14 % lower and b 0.02 higher, in every method. Completeness is a property of the catalogue (DECISIONS), and these steps come from the one-sidedness of the rule, not from a better record. The full-catalogue table is used below; the declustered-table fits stay in the file.

**Fits** (tapered, own b, full-catalogue table, full / gk_family / nn_family; the cut line gives the same within a few per cent up to Mw 8; Mmax of every unit from the full catalogue, corner by Kagan on the unit's own declustered b):

| unit | b | N(≥ 5) | N(≥ 7) | N(≥ 8) |
|---|---|---|---|---|
| interface | 0.963 / 0.766 / 0.900 | 25.2 / 7.00 / 12.1 | 0.299 / 0.206 / 0.192 | 0.0324 / 0.0350 / 0.0241 |
| interface, 45.6–37° S | 0.915 / 0.836 / 0.888 | 2.94 / 1.13 / 1.38 | 0.0435 / 0.0241 / 0.0231 | 0.0053 / 0.0035 / 0.0030 |
| interface, 37–32° S | 0.997 / 0.660 / 0.895 | 8.48 / 1.41 / 3.28 | 0.0859 / 0.0674 / 0.0530 | 0.0085 / 0.0144 / 0.0066 |
| interface, 32–26° S | 0.941 / 0.762 / 0.887 | 7.40 / 2.32 / 4.21 | 0.0965 / 0.0690 / 0.0705 | 0.0094 / 0.0099 / 0.0078 |
| interface, 26–17.6° S | 0.965 / 0.845 / 0.941 | 5.71 / 1.90 / 2.92 | 0.0671 / 0.0387 / 0.0383 | 0.0069 / 0.0052 / 0.0042 |
| in-slab, shallow | 1.151 / 0.984 / 1.120 | 9.24 / 5.63 / 7.77 | 0.0451 / 0.0591 / 0.0436 | 0.0016 / 0.0026 / 0.0016 |
| in-slab, intermediate | 1.154 / 1.000 / 1.146 | 25.3 / 15.9 / 24.4 | 0.122 / 0.155 / 0.122 | 0.0042 / 0.0068 / 0.0042 |
| Jujuy nest | 1.229 / 0.767 / 1.223 | 3.74 / 0.96 / 3.42 | 0.0093 / 0.0163 / 0.0087 | |
| crustal, forearc | 0.982 / 0.853 / 0.958 | 3.54 / 2.11 / 2.44 | 0.0250 / 0.0253 / 0.0190 | |
| crustal, arc | 1.002 / 0.909 / 0.951 | 1.31 / 0.87 / 1.06 | 0.0120 / 0.0121 / 0.0122 | |
| crustal, backarc | 0.988 / 1.020 / 1.064 | 2.30 / 1.39 / 1.61 | 0.0208 / 0.0109 / 0.0104 | |
| crustal, Patagonia (forearc b) | 0.982 / 0.853 / 0.958 | 0.64 / 0.52 / 0.60 | 0.0066 / 0.0097 / 0.0068 | |

- **Gardner–Knopoff lowers b** by 0.1–0.34 on the interface, 0.15–0.17 in-slab and 0.46 in the nest. It removes many small independent events along with the aftershocks, so the rate falls far at Mw 5 (interface × 0.28), less at Mw 7 (× 0.69), and at Mw 8 it is above the full catalogue (× 1.08; segment 37–32° S × 1.7).
- **Nearest neighbour per family lowers b a little** (interface 0.90, segments 0.89–0.94; in-slab within 0.01) and the rate more evenly: interface × 0.48 at Mw 5, × 0.64 at Mw 7, × 0.74 at Mw 8.
- **b against the floor** (`figs/declustered_b_floor.png`): the Gardner–Knopoff interface b is flat, 0.72–0.76 from 5.0 to 6.0 (B9's "no plateau" was on the network table from Mw 4.5). The nearest-neighbour interface b falls from 0.90 to 0.80, in every segment: the method still keeps more small events per large one than a window method. In-slab, both follow the full catalogue's fall with the floor; the Gardner–Knopoff nest b is 0.4–0.8.
- **Large-event check** (fitted / observed inside the table, Mw ≥ 7): interface full 54.5 / 49.7, gk_family 43.0 / 43.7, nn_family 36.4 / 41.5. Gardner–Knopoff passes every unit, including the two failures of the full catalogue (segment 32–26° S 13.7 / 9.1; intermediate in-slab 24.0 / 31.1). nn_family passes segment 32–26° S (13.0 / 8.8) and keeps the intermediate in-slab failure (18.1 / 29.5). Mw ≥ 8 passes everywhere.
- **Fano factor** of the yearly counts, Mw ≥ 5.0 from 1976 (Mw ≥ 5.5 from 1964), full / gk_family / nn_family:
  - interface: 58 / 1.2 / 2.6 (17.6 / 1.0 / 1.2); segments 24–71 / 0.8–1.2 / 0.9–3.4;
  - in-slab shallow 7.5 / 1.3 / 2.3; intermediate 3.4 / 1.2 / 2.8; nest 3.5 / 0.7 / 3.1;
  - forearc 14.4 / 2.7 / 3.6; backarc 12.6 / 1.5 / 1.9.

  Gardner–Knopoff makes the counts nearly Poisson. Nearest neighbour leaves them overdispersed at Mw ≥ 5.0 from 1976 (about 2–3) and close to Poisson at Mw ≥ 5.5 from 1964 (1.1–1.4).
- **Interface (a, b) branches**, rate at the controlling magnitude (5th / ML / 95th), margin at Mw 8.8:
  - full 0.0040 / 0.0051 / 0.0066;
  - gk_family 0.0056 / 0.0078 / 0.0108;
  - nn_family 0.0030 / 0.0042 / 0.0060.

  The two options bracket the full catalogue: × 1.5 and × 0.8 at the maximum likelihood. Per segment, gk_family is × 0.8–2.8 the full rate and nn_family × 0.6–0.9.
- **Shared b of the four segments** (random-effects mean, cut line): full 0.959 (τ 0), gk_family 0.759 (τ 0.072), nn_family 0.898 (τ 0). Under Gardner–Knopoff the segments differ (τ > 0: central segments 0.66 and 0.76, outer ones 0.84–0.85); one shared b is then a choice, not what the data say.

## 3. The factor "declustering method" (report only; Pablo decides)

One factor with two options, each applied the same way to every place the model uses a declustered catalogue:

| | Gardner–Knopoff per family | nearest neighbour per family |
|---|---|---|
| interface, declustered rate branch | b 0.77, rate at Mw 8.8 × 1.5 the full one | b 0.90, rate at Mw 8.8 × 0.8 |
| in-slab pattern | from 53 % of the intermediate events and 12 % of the nest | from 96 % and 91 % |
| crustal pattern | from 49–75 % of the events per class | from 65–88 % |
| completeness table | full catalogue | full catalogue |

**What favours each:**
- Gardner–Knopoff: Poisson counts, a plateau of b, every large-event check passed. It is the standard method of the old tree and of psha_chile7. Its known flaw is the low b (Mizrahi et al. 2021), and its in-slab pattern loses most of the dense zones.
- Nearest neighbour: b near the full catalogue, in-slab pattern nearly the full catalogue's. Its counts stay overdispersed at Mw ≥ 5.0, its b falls with the floor, and the threshold links two pairs of great historical earthquakes decades apart.

**Proposal:** both into the tornado, 0.5 / 0.5, as one factor applied jointly to the interface rate branch and the in-slab and crustal patterns; it stays a branch only if it moves PGA 475 yr by 5 % or more at some city (DECISIONS, Logic tree). Inside the interface tree it sits under the full / declustered branch, so the declustered half of the interface rates has two sub-branches that bracket the full catalogue at Mw 8.8.

**psha_chile7 choices** (`psha_chile7/FORECAST_v2.md`, item 7):
- "Declustered b 0.73 against 0.92, inconsistent with Bird and Kagan 0.96; N(≥ 8.8) × 1.5 with declustering": reproduced for Gardner–Knopoff (0.77 against 0.96, × 1.5). The nearest-neighbour option does not show it (0.90, × 0.8): the low b and the high rate at Mw 8.8 are a property of window declustering, not of declustering as such.
- "Gardner–Knopoff for the crustal pattern": kept as one of the two options, run per family.
- "Uhrhammer suggested for crustal and in-slab": not tested (B9 did not build it). Its windows are smaller than Gardner–Knopoff's; it would sit between the two options.

## 4. Proposed DECISIONS lines

- Declustering method, a tornado factor with two options applied jointly to the declustered interface rate branch and to the in-slab and crustal patterns (Pablo, 15 Nov):
  - Gardner–Knopoff (van Stiphout et al. 2012 windows, foreshock window = aftershock window);
  - nearest neighbour (Zaliapin and Ben-Zion 2013; b 1, d_f 1.6, epicentral distance, one mixture threshold from 1964, the largest event of a cluster kept).
  - Both run per class family, Mw ≥ 4.5, the whole span: `catalog/declustered/gk_family_2026-11-15.csv`, `nn_family_2026-11-15.csv`. Weights 0.5 / 0.5 until the tornado (B12).
- Declustered fits use the B11 code, the completeness table and the Mmax of the full catalogue (`fits/tables/fits_declustered_2026-11-15.csv`, methods gk_family and nn_family, table full). The declustered tables move the historical steps up to 80 years earlier because the rate rule is one-sided (reported, not used) (B12).
- Superseded: "Uhrhammer for the crustal and in-slab pattern" (psha_chile7 suggestion) → the two-option factor.

Proposed LEARNINGS lines (Declustering):
- Nearest neighbour keeping the first event of a cluster (B9's setting) removes great mainshocks in favour of foreshocks (Valdivia 1960, 1877, 1922, Iquique 2014) and halves the interface N(≥ 8). Keep the largest event of each cluster if the catalogue is used for rates (B12).
- With the threshold set after 1964, nearest neighbour links great historical earthquakes decades apart (1657 to 1751, 1975 to 1960) (B12).
- On the full-catalogue table the Gardner–Knopoff interface b has a plateau (0.72–0.76, floors 5.0–6.0); B9's "no plateau" was on the network table from Mw 4.5 (B12).
- Run on all classes together, both methods remove crustal and in-slab events after interface mainshocks (57–68 % of their crustal removals); run them per family (B12).
- The two-Gaussian threshold of log10 η takes 5–15 % of the background events of synthetic catalogues as clustered (B12).

## 5. Not done, assumptions

- Uhrhammer windows not built.
- The family of an event is that of its largest class weight; outer-rise and unclassified events form their own groups.
- Mmax and corner rule as in step 0; Mmax from the full catalogue.
- The completeness rule reads the shape from Mw 3.5, so each method was run again from Mw 3.5 for that step only (`*_m35_*` files).
- No hazard computed. For S1 the declustered interface branch is the rows method gk_family or nn_family, table full, both shapes, b_option own (segments and margin) or shared.
- Run times (16 cores): `decluster.py` about 3 minutes for all methods (nn_family alone 70 s), `run_declustered.py` 2.5 minutes, tests about 20 s.

## 6. Rerun on the catalogue of 16 Nov (A9)

Input `catalog/frozen/2026-11-16/catalog_2026-11-16.csv`; `decluster.py` and `run_declustered.py` unchanged except `DATE = "2026-11-16"`. Sections 1 to 5 keep the numbers of the 2026-11-14c catalogue. The figures `figs/declustered_*.png` are of this run; those of 15 Nov are in `figs/2026-11-15/`.

- **Declustered catalogues** `catalog/declustered/{gk,gk_family,nn,nn_depth,nn_family}_2026-11-16.csv` and the `_m35_` files: same settings. Mainshocks kept at Mw ≥ 4.5 (of 14 279): Gardner–Knopoff 5 171 (unchanged), per family 6 006 (6 013 before), nearest neighbour 10 068 (unchanged), with depth 9 934 (9 939), per family 10 923 (10 926). Thresholds of log10 η: −5.52, −5.31, −5.75 (−5.52, −5.32, −5.75 before). Only the per-family methods and the depth variant can change: the revision moved classes and no location; the depth variant differs by 5 events through the threshold.
- **Completeness tables of the declustered catalogues:** unchanged for all five methods (Gardner–Knopoff: 5.0 from 1976, 5.1 from 1964, 6.0 from 1950, 6.5 from 1890, 7.0 from 1825, 8.0 from 1500; nearest neighbour: the same with 6.5 from 1900 and 7.0 from 1830).
- **Fits** `fits/tables/fits_declustered_2026-11-16.csv` (352 rows, same layout), with `declustered_tables_`, `declustered_removed_`, `declustered_compare_` and `declustered_floor_2026-11-16.csv`. Mmax of every unit unchanged; corners within 0.01.
- **What moved against `fits_declustered_2026-11-15.csv`** (tapered, the two options of the declustering factor, table of the full catalogue, own b):

| unit | Gardner–Knopoff per family: b | N(≥ 6) | N(≥ 7) | nearest neighbour per family: b | N(≥ 6) | N(≥ 7) |
|---|---|---|---|---|---|---|
| interface | 0.766 → 0.758 | +1.8 % | +3.6 % | 0.899 → 0.893 | +1.5 % | +3.0 % |
| interface, 45.6–37° S | 0.836 → 0.823 | +3.7 % | +6.9 % | 0.888 → 0.875 | +3.6 % | +6.8 % |
| interface, 37–32° S | 0.660 → 0.653 | +1.9 % | +3.5 % | 0.895 → 0.890 | +1.5 % | +2.9 % |
| interface, 32–26° S | 0.762 → 0.758 | +1.1 % | +2.0 % | 0.887 → 0.884 | +0.8 % | +1.5 % |
| interface, 26–17.6° S | 0.845 → 0.841 | +1.0 % | +1.8 % | 0.941 → 0.938 | +0.8 % | +1.5 % |
| in-slab, shallow | 0.984 → 0.975 | +1.4 % | +3.3 % | 1.120 → 1.111 | +1.8 % | +3.9 % |
| in-slab, intermediate depth | 1.000 → 1.004 | −1.0 % | −1.8 % | 1.146 → 1.149 | −0.8 % | −1.5 % |
| Jujuy nest | 0.767 → 0.767 | 0 | 0 | 1.223 → 1.223 | 0 | 0 |
| crustal, forearc | 0.853 → 0.856 | −1.3 % | −1.9 % | 0.958 → 0.962 | −1.4 % | −2.1 % |
| crustal, arc | 0.909 → 0.936 | −6.8 % | −12.1 % | 0.951 → 0.974 | −6.1 % | −10.9 % |
| crustal, backarc | 1.020 → 1.004 | +4.4 % | +8.1 % | 1.064 → 1.050 | +3.9 % | +7.2 % |
| crustal, Patagonia | forearc b | −37 % | −38 % | forearc b | −33 % | −34 % |

- The moves follow the full catalogue: Patagonia loses a third (the triple-junction events), the arc loses its three split events of Mw ≥ 7, the interface gains at the top. With the declustered tables the backarc is also over 5 % at N(≥ 6) (+5.4 to +5.8 %, b −0.02).
- **Large-event check:** no unit changes its result in any method, table or shape (intermediate in-slab still fails with the nearest-neighbour catalogues and passes with Gardner–Knopoff).
- **Over the thresholds of the A9 brief** (0.02 in b, 5 % in N(≥ 6), 0.1 in Mmax), for the two options: the arc and Patagonia in every case, the backarc on the declustered tables. No interface or in-slab unit, no Mmax.

## 7. Mmax from weight-1 events (16 Nov, run 2026-11-16b)

`fits/tables/fits_declustered_2026-11-16b.csv` and the four `declustered_*_2026-11-16b.csv` tables, on the declustered catalogues of 2026-11-16 (unchanged). Only the forearc changes (Mmax 7.4 → 7.2) and Patagonia through the forearc b; numbers in `fits/FITS.md` section 9. Figures `figs/declustered_*.png` are of this run; those of 2026-11-16 are in `figs/2026-11-16/`.

## 8. Crustal classes fitted from 1976 (16 Nov, run 2026-11-16c)

`fits/tables/fits_declustered_2026-11-16c.csv` and the four `declustered_*_2026-11-16c.csv` tables, on the declustered catalogues of 2026-11-16 (unchanged). Only the four crustal classes change; numbers in `fits/FITS.md` section 10. Figures `figs/declustered_*.png` are of this run; those of 16b are in `figs/2026-11-16b/`.

## 9. One b for the crustal family (16 Nov, run 2026-11-16d)

`fits/tables/fits_declustered_2026-11-16d.csv` and the four `declustered_*_2026-11-16d.csv` tables, on the declustered catalogues of 2026-11-16 (unchanged). The four crustal classes take the b of the crustal family of the same catalogue (new unit `crustal`); numbers in `fits/FITS.md` section 11. Figures `figs/declustered_*.png` are of this run; those of 16c are in `figs/2026-11-16c/`.

## 10. Catalogue 2026-11-16c (16 Nov, run 2026-11-16e)

- **Declustering.** `fits/decluster.py` reads the classes only for the per-family methods (the family of the largest of the five family weights) and never `sub_crustal`. All five methods were run again as `catalog/declustered/*_2026-11-16e.csv` (the script builds them together). Compared with the `_2026-11-16` files: `gk`, `nn`, `nn_depth` and their `_m35` files are identical; `gk_family` has the same mainshock flags (6 006) and differs only in cluster labels; `nn_family` differs in 2 flags (10 923 → 10 921; 4 flags from Mw 3.5), through the 13 Scotia events that changed family. Completeness tables of the declustered catalogues unchanged.
- **Declustered fits** (`fits_declustered_2026-11-16e.csv`; two options, table full, own family b): family b 0.923 → 0.922 (Gardner–Knopoff per family) and 0.999 → 1.001 (nearest neighbour per family), so the declustered b hardly moves, unlike the full one. N(≥ 6): forearc −8 % and −9 %, arc 0 % and −0.5 %, backarc −75 % and −78 %, Patagonia −45 % and −53 %. Interface, in-slab and nest rows identical. Checks as before.
- Numbers per unit in `fits/FITS.md` section 12. Figures `figs/declustered_*.png` are of this run; those of 16d are in `figs/2026-11-16d/`.

## 11. Interface Mmax from the catalogue (16 Nov, run 2026-11-16f)

`fits/tables/fits_declustered_2026-11-16f.csv` and the four `declustered_*_2026-11-16f.csv` tables, on the declustered catalogues of 2026-11-16e (unchanged). Only interface segment rows change (37–32° S Mmax 9.3 → 9.2, 26–17.6° S 9.0 → 9.1, and the shared-b rows of the other two segments in the fourth decimal); numbers in `fits/FITS.md` section 13. Figures `figs/declustered_*.png` are of this run; those of 16e are in `figs/2026-11-16e/`.

## 12. Check of `nn_family` against Zaliapin and Ben-Zion (2013) (17 Nov, B15)

Checked against the method of the paper (the PDF is not in `refs/`; checked from the method as published, no page numbers):
- Proximity η_ij = t_ij · r_ij^d_f · 10^(−b m_i) for a parent i earlier than j, with b 1 and d_f 1.6 on epicentral distance: as in the code (t in years, r in km, the product does not depend on q).
- Parent = the earlier event of smallest η; links with η below the threshold η0 are kept, the others cut; clusters are the trees that remain; the largest event of a cluster is its mainshock (`largest=True`, first on ties): as in the code.
- Threshold from a two-Gaussian mixture on log10 η (from 1964), at equal posterior: as in the code.
- Choices of ours, not of the paper (DECISIONS, Statistics, 15 Nov): proximities inside each class family, one threshold for all families; Mw ≥ 4.5 over the whole span, historical part included (the source of the 1657 → 1751 and 1975 → 1960 links); distance at least 1 km.

Two deviations found and fixed in `decluster.py`:
1. Event times dropped the seconds (`gr.load` reads to the minute), so 38 pairs of events in one family shared a time and 24 of them were in the wrong order. `decluster.one` now adds the seconds and sorts again; `gr.load` is not changed (it is shared with the fits, and the table test draws its pool in its order).
2. A zero time difference was floored at 1e-7 yr and linked; the paper sets η infinite for t_ij ≤ 0. Now an event at the same time is no parent (test `test_nearest_neighbour_no_parent_at_the_same_time`).

Effect on catalogue 16c (`nn_family`, Mw ≥ 4.5; against `catalog/declustered/nn_family_2026-11-16e.csv`): 7 flags change, mainshocks 10 921 → 10 922, threshold log10 η −5.74. Three pairs swap which copy is the mainshock (2026-09-25 15:29, 2024-03-13 22:10, 2025-09-01 / 2020-06-15 near 24.2° S); the 2025-09-04 04:10 pair (two ISC Mw 5.9 at the same time) is now kept twice, a duplicate that A11 removes from the catalogue.
