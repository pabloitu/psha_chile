# FITS session closed (16 Nov): handoff to the next fits session

## What FITS owns
`fits/` (B11/B12) and the declustered catalogues `catalog/declustered/`. Reports: `fits/FITS.md` (fits, sections 1–14), `fits/DECLUSTER.md` (declustering, sections 1–11). Entry scripts, run from `psha_chile8/fits/` in conda `psha_renta`, settings at the top of each:

| script | what | command | time |
|---|---|---|---|
| `decluster.py` | five declustered catalogues (gk, gk_family, nn, nn_depth, nn_family), from Mw 4.5 and from 3.5 (`_m35_`) | `OMP_NUM_THREADS=1 python decluster.py` | 3–4 min |
| `run.py` | full-catalogue fits, both shapes, bootstrap, (a, b) branches, sensitivity table, B11 figures | `python run.py` | 95 s |
| `run_declustered.py` | declustered completeness tables, fits (incl. shared interface b), comparison, figures | `OMP_NUM_THREADS=1 python run_declustered.py` | 3 min |
| `run_pad.py` | Mmax pad 0.0 / 0.4, maximum-likelihood rows only | `python run_pad.py` | 15 s |
| `figs_declustered.py` | the three declustered figures from the saved tables | `python figs_declustered.py` | 1 min |

Library: `gr.py` (estimators, `kagan_corner`, `rates`), `table.py` (automatic completeness), `compare.py`, `synth.py`, `sigma.py`, `figs.py`. Tests: `pytest fits/tests` from `psha_chile8/` (31 pass).

## Current outputs (CURRENT.md lines checked, correct)
- Fits, full catalogue: `fits/tables/fits_2026-11-16f.csv`, on catalogue `2026-11-16c`.
- Fits, declustered: `fits/tables/fits_declustered_2026-11-16f.csv`. Rows for the factor are `method` gk_family / nn_family with `table` full.
- Completeness table: `fits/tables/table_2026-11-16f.csv` (same steps since 15 Nov).
- Mmax pad: `fits_2026-11-16f_pad00.csv`, `_pad04.csv` (ML rows, tornado only).
- Declustered catalogues: `catalog/declustered/*_2026-11-16e.csv`, built on catalogue 16c.

## Decisions
All of Pablo's decisions for FITS are in DECISIONS.md (Statistics, Interface Mmax, Superseded): the Mmax rule and Kagan corner, the declustering factor (two options, per family), the crustal family b without `outside` events, interface Mmax from the catalogue, the Mmax pad as a tornado factor. Added on closing: the arc stays one unit. On closing I only corrected stale pointers in Statistics: the 16e fits line now reads "kept", and the declustering lines name the current 16e catalogues and 16f declustered fits.

## Open
- **Refit on catalogue `2026-11-16e`** (Aysén 1960 and 1927 at the ISC-GEM epicentre): on hold (Pablo). It needs `CAT` in `gr.py`, `DATE` in `run.py`, `run_declustered.py` and `decluster.py`, then all three scripts and a CURRENT.md / DATA.md update.
- **Arc class:** decided (Pablo, 16 Nov, in DECISIONS, Statistics): one unit, no split by latitude, table from 1976 only; fit 16f stands (family b 1.009, N(≥ 6) 0.135). The options in WORKLOG "arc class by latitude" are closed. The fault / background mismatch on Liquiñe–Ofqui (fault rate 0.447 at Mw ≥ 6; would need b about 0.5) is for CR, in the fault moment.
- **Arica 1868** (Mw 9.0, 17.15° S) is north of the last interface segment and counts in the margin unit only (S1 question).
- **Two known fit failures**, left for the paper: interface 32–26° S and intermediate in-slab at Mw ≥ 7.
- **Not built:** Uhrhammer windows. LEARNINGS lines proposed in `DECLUSTER.md` section 4 and in the WORKLOG entries are not added.

## Traps
- `decluster.py` has its own `DATE` (`2026-11-16e`), and `run_declustered.py` reads the catalogues by that date (`DC_DATE = D.DATE`). On a new catalogue, change it, or the 16e files are overwritten.
- `fits/figs/*.png` always show the last run. Earlier runs were copied by hand to `fits/figs/<date>/`; copy before rerunning.
- `gr.py` reads one catalogue (`CAT`); CURRENT.md lists a newer frozen one (16e) that the fits do not use yet, on purpose.
- Nearest neighbour as B9 set it (`nn`, `nn_depth`: first event of a cluster kept) drops great mainshocks (Valdivia 1960, 1877, 1922, Iquique 2014). Only `nn_family` (largest kept) is a factor option; `nn` and `nn_depth` are comparison only.
- Even `nn_family` links two pairs of historical great earthquakes decades apart (1657 into 1751, 1975 into 1960); reported, not patched.
- The NN mixture threshold takes 5–15 % of background events as clustered on synthetic catalogues; the test records the bias. The 5 % recovery test passes for NN only with a gap threshold.
- The declustered completeness tables move the historical steps up to 80 years earlier (the rate rule is one-sided); they are reported, never used.
- `gr.rates` stops at Mw 9.7 (`MTOP`); the tapered interface lines carry about 6 % of their moment above. `model/interface/if_mfd.py` uses its own grid past `MTOP`, so S1 is fine; any other caller must do the same.
- `run_pad.py` rows have no bootstrap, covariance or branch columns.
- A process pool with numpy needs `OMP_NUM_THREADS=1`.

## Uncommitted (fits 16f, pad, arc figure, closing edits)
```
git add psha_chile8/fits/run.py psha_chile8/fits/run_declustered.py psha_chile8/fits/run_pad.py psha_chile8/fits/FITS.md psha_chile8/fits/DECLUSTER.md psha_chile8/fits/figs psha_chile8/fits/tables/*_2026-11-16f*.csv psha_chile8/DECISIONS.md psha_chile8/CURRENT.md psha_chile8/DATA.md psha_chile8/WORKLOG.md psha_chile8/handoffs/2026-11-16_FITS_close.md
git commit -m "Fits 2026-11-16f: interface Mmax from the catalogue; Mmax pad 0.0 / 0.4 (ML rows); arc diagnostic figure; FITS handoff and current-pointer fixes in DECISIONS"
```
DECISIONS, CURRENT, DATA and WORKLOG also hold other sessions' edits; check `git diff` on them first.
