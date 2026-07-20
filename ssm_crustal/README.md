# Crustal Smoothed-Seismicity + Fault Source Model (`ssm_crustal`)

Builds the crustal seismic source model for the Chile PSHA: a per-class
smoothed-seismicity model (SSM) merged with active-fault sources through a
magnitude handoff. Produces OpenQuake point-source NRML for both the
with-faults model and a no-fault baseline.

---

## Quick start

Everything is configured in `ssm_config.py` (module-level constants only —
no argparse). Edit it, then run the numbered scripts in order:

```bash
python s00_mc.py               # per-class Mc(t) plots -> fill COMPLETENESS by hand
# edit ssm_config.COMPLETENESS from the s00 figures, then:
python s01_build_ssm.py        # per-class smoothing + superposition -> ssm_mfd_grid.csv
python s02_fault_buffers.py    # fault buffer polygons -> fault_buffers_union.geojson
python s03_cap_ssm_mmax.py     # cap Mmax inside buffers -> ssm_mfd_grid_capped.csv
python s04_build_sm.py         # FAULT model  -> ssm_crustal_point_sources.xml
python s05_build_sm_nofaults.py# BASELINE     -> ssm_crustal_point_sources_nofaults.xml
```

Diagnostics (after the relevant step; need `checks/__init__.py`):

```bash
python -m checks.check_domain_mfd          # zone MFD: catalog vs bg vs faults vs merged
python -m checks.check_fault_ssm_merger    # handoff, moment closure, N-test, maps
python -m checks.check_branch_scan         # N-test per fault branch -> phi-weight table
python -m checks.check_baseline_vs_faults  # baseline vs fault model
```

### Dependencies
`numpy<2` (hazardlib breaks on numpy 2), pandas, matplotlib, geopandas,
shapely, pyproj, rasterio, seismostats (for Mc/KS), openquake.hazardlib
(needs numba, fiona).

---

## Files

| File | Role |
|------|------|
| `ssm_config.py` | All paths + parameters. Edit here only. |
| `ssm_lib.py` | Shared primitives: catalog io, completeness, Weichert, kernels, truncated-GR binning, grid/raster io, figures. No paths/params. |
| `s00_mc.py` | Per-class magnitude of completeness Mc(t). |
| `s01_build_ssm.py` | Per-class Weichert (a,b) + adaptive-kernel smoothing + superposition. |
| `s02_fault_buffers.py` | Down-dip-aware fault buffer polygons. |
| `s03_cap_ssm_mmax.py` | Cap smoothed Mmax inside buffers (the handoff). |
| `s04_build_sm.py` | Capped grid -> point-source NRML (with faults). |
| `s05_build_sm_nofaults.py` | Uncapped grid -> point-source NRML (baseline). Thin wrapper over s04. |
| `checks/` | Diagnostics (see below). |

Outputs go to `ssm_crustal_outputs/` (grids, geojson, NRML, `figures/`,
`ssm_class_summary.csv`).

---

## Scientific decisions

### Classes and superposition
Seismicity is split into four tectonic classes — **forearc, intraarc,
backarc, unclassified** (the last = southern Patagonia only, region-boxed) —
each smoothed from its **own declustered mainshock catalog** and scaled by its
**own Weichert (a, b) and Mmax**. The total SSM is the **per-bin sum** of the
class fields ("option B" superposition).

Why superposition instead of hard zonal polygons (ESHM20 TECTO style): class
membership is a property of *events*, not grid cells. An event near a class
boundary spreads its smoothing kernel across it, so the summed field is
**continuous** — no rate discontinuity along the forearc/intraarc boundary,
which runs the length of the country near population centers. Each cell's MFD
is a mixture of the overlapping class contributions, which is physically
correct near boundaries and converges to the pure class MFD away from them.

### Declustering
Catalogs are declustered **per class**, not jointly. This deliberately retains
megathrust-triggered crustal events (Pichilemu 2010, Aysén 2007) as
independent crustal hazard rather than removing them as aftershocks of the
subduction sequence. This deviates from GEM practice (which declusters
crustal+interface+shallow-slab jointly) and is a modeling choice worth stating
explicitly in the paper: the forearc/intraarc correlation with megathrusts is
out of scope, and those events carry real hazard.

### Completeness (Mc) — do this carefully
Completeness is set **by hand per class** in `COMPLETENESS` as `(Mc, since_year)`
steps, read off `s00_mc.py` figures. The `mc_window`/`tc_years` columns stamped
on the catalog by the upstream pipeline are **ignored** — they are per-epoch,
nationally-estimated stamps (Mc of the time window each event fell in), not a
magnitude→period step function, and misreading them produced wrong b-values.

`s00_mc.py` estimates Mc on `[t, present]` for a range of start years t
(cumulative-from-present), so each Mc maps directly to a `since_year`. It uses
the **KS estimator** (SeismoStats, fixed b=1), not MAXC: MAXC takes the
histogram mode, which on a cumulative window is dominated by recent low-Mc
events and returns a flat, too-low Mc that hides the completeness history.

Sanity rule: band-rate **density** must decrease with magnitude (Gutenberg-
Richter). `completeness_audit` (printed by s01) warns if `rate_per_yr_per_mag`
rises with M — that means a `since_year` is too early. Fix the table until the
audit is clean before trusting any b or rate.

### b-value estimation
b comes from **Weichert (1980)** maximum likelihood on the per-class
completeness steps, so historical large events count with their long windows
and modern small events with their short ones. `b_err` is a **nonparametric
bootstrap** (200 resamples), not the optimistic `b/sqrt(N)` — it reflects
reliance on sparse historical windows.

Thin classes (backarc ~80 events, Patagonia ~50) cannot support a stable b.
They **borrow** b from a data-rich class via `B_SOURCE` (shape only — the
activity rate stays local). `B_SOURCE` accepts a single donor class or a list
(b fit on the pooled catalog of several classes). This is the ESHM20 logic of
estimating b at the tectonic-domain scale and activity at the class scale.
`B_ERR_WARN` (default 0.15) flags classes whose own b is too uncertain to
trust.

### Rate anchoring
The Weichert activity rate is anchored at the **first magnitude with complete
data**, which for some classes is above `MC_MIN_FIT` (e.g. backarc Mc 5.3 vs
MC_MIN_FIT 5.0). Anchoring at MC_MIN_FIT and extrapolating down would inflate
the class rate — this was a real bug, now fixed.

### Smoothing kernel
Helmstetter-style adaptive kernel: each event's smoothing distance is the
distance to its k-th nearest neighbour (`N_NEIGHBORS`), floored at
`MIN_KERNEL_KM`, with a `1/(r^2+d^2)^p` kernel. Each event carries a rate
weight `1/T(M) * 10^(b(Mc(M)-mc_min))` from the same completeness table used
for the fit, so historical events stand in for the smaller events their epoch
missed. Distances are great-circle (haversine). The kernel gives the **spatial
shape**; Weichert gives the **rate and slope**; the two are combined so the
absolute weight level cancels and only the relative spatial pattern survives.

### Fault handoff (the merger)
Inside **down-dip-aware fault buffer polygons**, the smoothed Mmax is capped at
`CAP_MAG = 6.0`; the fault model owns M ≥ 6.0 there, the background owns
M < 6.0. Outside buffers the background keeps its full class Mmax.

- **Buffer geometry** (from UCERF3): the surface projection of the dipping
  plane, `(lsd-usd)/tan(dip)` wide on the dip-direction side (parsed from the
  shapefile `dip_dir`, cardinal strings supported) plus `BUFFER_MARGIN_KM`.
  Vertical faults get a symmetric trace buffer. Overlapping polygons are
  dissolved with `unary_union`; a cell is capped if its center is inside.
- **Truncation rule** (from ESHM20, not UCERF3 rate attribution): a simple
  cap, no redistribution. Background last bin center 5.95 (edge 6.0), fault
  first bin center 6.05 — clean handoff, no shared bin, no hole.

### Baseline (no faults)
`s05` builds the same point sources from the **uncapped** s01 grid, so the
smoothed model keeps M up to each class Mmax everywhere. This is the honest
no-fault baseline: same kernel, (a,b), cells and depths as the fault run, so
any hazard difference is attributable to the merger alone. **Do not use the
capped grid as a no-fault model** — it has a hole (no M≥6 inside buffers with
nothing to replace it).

### Key findings (for interpretation)
- The fault model **over-predicts** observed M≥6 crustal seismicity inside
  buffers (phi=1 corner branch: expected ~56 events since 1950 vs 8 observed).
  It is an upper envelope; the data pull toward low seismic-coupling (phi) or
  high Mmax, concentrated on the LOFZ. Use the N-test (`check_branch_scan`) as
  the empirical anchor for the phi weights — but anchor phi from independent
  geodetic coupling data, don't calibrate to the test and then present the
  test as validation (circular).
- ~83% of moderate crustal events (M≥5.5) fall outside fault buffers,
  justifying full-Mmax background outside buffers.
- The handoff jump (background→faults at M6) is expected and matches ESHM20's
  hybrid-vs-area-source behaviour; its magnitude is inflated by the phi=1
  corner and the GR MFD shape.

---

## Diagnostics reference

| Check | Answers |
|-------|---------|
| `check_domain_mfd` | Is the merged model consistent with a zone's observed MFD? (catalog vs uncapped/capped background vs faults vs merged, per polygon) |
| `check_fault_ssm_merger` | Is the handoff clean? Rate conservation outside buffers, MFD continuity at M6, moment closure per region, event attribution, N-test, removed-rate map. |
| `check_branch_scan` | Which fault branches do the data support? N-test (obs/expected M≥6) per fault XML. |
| `check_baseline_vs_faults` | What does the merger change? Baseline vs fault model, national + inside buffers, asserts identity outside buffers. |

`moment_closure.csv`: rows with `Mo_fault/Mo_removed < 1` = the fault budget
doesn't cover the background moment the cap removed there → hazard drops
locally; investigate the slip rate or buffer width.