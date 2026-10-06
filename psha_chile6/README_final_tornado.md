# psha_chile6 final sensitivity run: what changed, how to run, what to send back

1 October 2026. Last modification of psha_chile6 before psha_chile7.

## Decisions applied

| item | setting |
|---|---|
| fault aseismic coefficient | 0.6 / 0.8 / 1.0 (0.25 / 0.5 / 0.25) |
| fault MFD | AL-I, AL-II, AL-III, YC characteristic, tapered (0.2 each); AL-II is the truncated GR, so tgr is not a sixth shape |
| fault Mmax | observed + 0.2 / WC1994 area / Leonard 2014 area (1/3 each) |
| fault seismogenic depth | 20 km for every fault (reference); 10 and 30 km in the tornado |
| fault moment | balanced at the bin centres (`M0_AT_EDGE = False`); the old setting released 19 % more than the slip rate |
| background | buffer 5 km, hypocentre 10 km |
| in-slab nodal planes | N-S strike, 60 dipping west normal and 30 dipping east reverse |
| interface | 6.6 cm/yr, Antarctic source on (chi 0.5, dip 30, 10-50 km), no Antarctic rows |
| cities | 14: the ten plus Hornopiren, Puerto Williams, Calama, La Serena |
| GMM | GMM_FINAL (4 per subduction region, Parker SA_S), no sigma_mu_epsilon |
| distances | interface 600, in-slab 500, crust 300 km |

Fault tree: 3 x 3 x 5 = 45 branches x 4 GMMs = 180 crustal realizations; the full-tree product is
192 x 4 x 180 = 138 240, still enumerated exactly.

## How the fault MFD shapes are built (crustal/s03_faults.py, `shape` and `mfd`)

All five start as a shape between the first bin (6.05) and the Mmax bin, then are scaled so that
sum(rate x M0(centre)) = phi mu L W slip. Cumulative forms with Delta = top - m (top = Mmax + 0.05):

- AL-I: exp(b' Delta): exponential with a jump at Mmax (a characteristic spike in the last bin)
- AL-II: exp(b' Delta) - 1: exponential falling to zero at Mmax = the truncated GR
- AL-III: exp(b' Delta) - 1 - b' Delta: zero slope at Mmax
- YC: exponential below top - 0.5 and a box of width 0.5 whose density is the exponential one
  magnitude unit below the box (Youngs and Coppersmith 1985); AL-II where Mmax < 6.65
- tapered: OpenQuake TaperedGRMFD, corner Mmax, extended by TAPER_PAD 0.5

b' = b ln 10 with the fault's b (database b_val, 0.8 if missing). Tests: tests/test_faults.py.

## Leonard

OpenQuake's `Leonard2014_Interplate` is Leonard (2010, 2014) for crustal faults in active (plate
boundary) regions, as opposed to `Leonard2014_SCR` for stable continental regions. "Interplate" is
Leonard's word for the tectonic setting, not the subduction interface. Used for the fault Mmax from
the area (mode mleo) and, in one tornado row, as the fault rupture scaling.

## Run

```
cp -r ~/Downloads/psha_chile6_final_tornado/* .
pytest -q -m "not built" 2>&1 | tail -3        # about 92 passed
python hazard/mmax_check.py                    # closure and corner (uses the last interface build)
TORNADO=1 python hazard/build.py 2>&1 | grep -c "run:"   # builds the 79 jobs, prints how many will run
TORNADO=1 bash hazard/run_all.sh               # 79 jobs, 14 cities; the three references first
TORNADO=1 python hazard/tornado_final.py
```

The crustal build rewrites the fault branches (45 files), so the first crustal job rebuilds everything
crustal. Expect roughly 1-2.5 minutes per job: 2-4 hours.

After the run, the final-tree tornado on the PRELIM tree needs a rerun of its crustal job (the fault
tree changed): `PRELIM=1 bash hazard/run_all.sh`, then `PRELIM=1 python hazard/tornado_tree.py`.

## Outputs (outputs/hazard/rock800_tornado/_tornado/)

| file | content |
|---|---|
| summary.txt | reference PGA per city; axes ranked by their largest range with set (A/B/C), city and verdict; missing rows |
| tornado.csv, bars.csv | every row and city; lo / hi / range per axis |
| t_<city>.png | collaborator figure, every axis |
| t_overview.png | collaborator heat map, every axis x city |
| paper_<city>.png | presentation figure (16:9), set C only, paper labels |
| paper_overview.png | presentation heat map, set C |

Sets: A = fixed by a statistical or physical criterion (shown to the collaborators as tested), B =
collaborator figure only, C = candidates for the paper figure.

## Send back

1. `summary.txt` (whole file).
2. `bars.csv`.
3. The printout of `mmax_check.py`.
4. `paper_overview.png` and `t_overview.png`, plus `paper_` figures of two or three cities.
5. Any job marked FAILED in `run_all.sh`, with the error from its `oq.log`.
