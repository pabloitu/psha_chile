# Intraslab Smoothed-Seismicity Source Model (`ssm_intraslab`)

Builds the in-slab (Wadati-Benioff) seismic source model for the Chile PSHA: a
per-class smoothed-seismicity model over the subducting slab, written as
OpenQuake point sources with slab-geometry depths. Standalone copy of the
crustal pipeline with no fault handoff (the slab has no mapped faults).

---

## Quick start

Configured in `ssm_config.py` (module-level constants only). Run in order:

```bash
python s00_mc.py            # per-class Mc(t) plots -> fill COMPLETENESS by hand
# edit ssm_config.COMPLETENESS from the s00 figures, then:
python s01_build_ssm.py     # per-class smoothing + superposition -> ssm_mfd_grid.csv
python s02_build_sm.py      # grid -> ssm_intraslab_point_sources.xml (slab depths)
```

There is **no fault buffer / cap step** — the slab has no fault sources, so the
crustal `s02_fault_buffers`/`s03_cap` stages don't exist here and `s02` is the
point-source builder directly.

### Dependencies
Same as crustal: `numpy<2`, pandas, matplotlib, geopandas, shapely, pyproj,
rasterio, seismostats, openquake.hazardlib (numba, fiona). Plus the slab-depth
grid (`cat_paths.slab_depth`) for hypocentre depths.

---

## Files

| File | Role |
|------|------|
| `ssm_config.py` | All paths + parameters (intraslab). |
| `ssm_lib.py` | Shared primitives — **identical copy** of the crustal `ssm_lib.py`. Keep in sync manually. |
| `s00_mc.py` | Per-class Mc(t). |
| `s01_build_ssm.py` | Per-class Weichert + smoothing + superposition. |
| `s02_build_sm.py` | Grid -> point-source NRML with slab-geometry depths. |

Outputs go to `ssm_intraslab_outputs/`.

---

## Scientific decisions

### Classes and superposition
Two classes — **`intra_slab`** (shallower Wadati-Benioff seismicity) and
**`slab_deep`** (deeper cluster) — are smoothed separately, each from its own
declustered catalog with its own Weichert (a, b) and Mmax, then superposed
per-bin (same "option B" as the crustal model).

Why separate them: the previous single-model version pooled both under one
national (a, b). The two populations have **different b-values** (deeper slab
seismicity is typically flatter) and different Mmax, so a pooled fit is wrong
for both. Splitting and superposing gives each its correct MFD while keeping
the combined field continuous. The deep cluster is also spatially distinct, so
the superposition is clean.

### Completeness, b-value, kernel, rate anchoring
Identical methodology to the crustal model (see `README_ssm_crustal.md`):

- Completeness set by hand per class in `COMPLETENESS` from `s00_mc.py`
  (cumulative-from-present KS Mc). The upstream `mc_window`/`tc_years` stamps
  are ignored.
- b from Weichert (1980) ML on the per-class steps, bootstrap `b_err`.
  `B_SOURCE` borrows b for thin classes (e.g. `slab_deep` from `intra_slab`
  if the deep catalog is sparse).
- Rate anchored at the first complete magnitude, not `MC_MIN_FIT`.
- Helmstetter adaptive kernel; `N_NEIGHBORS = 25` (wider than the crustal 15,
  reflecting the sparser, more diffuse slab seismicity).

Note: the slab classes historically **dominated** the national Mc estimate
(tens of thousands of events), so their own per-class completeness curves
should be well-behaved — but estimate them per class anyway rather than
inheriting national values.

### Depths — the key difference from the crustal model
Crustal sources use a constant hypocentre depth. Intraslab sources take the
**depth of the nearest slab-geometry node** plus an offset, so each point
source sits on the modelled slab surface. This is why `s02_build_sm.py` needs
the slab-depth CSV (`cat_paths.slab_depth`) and uses a subduction MSR
(StrasserIntraslab) and TRT `"Subduction IntraSlab"`. Cells with no slab node
within the search radius are skipped and reported.

### min_mag convention (fixed)
`EvenlyDiscretizedMFD.min_mag` is the first bin **centre**; the grid columns
are bin **edges**. The builder uses `min_mag = edges[0] + dM/2`. The original
intraslab builder used `edges[0]`, shifting every source 0.05 magnitude low —
any hazard computed before this fix used the shifted convention. Ensure the
crustal `s04` uses the same convention so the two components are consistent.

---

## Relationship to the crustal pipeline

This is a **standalone copy**, not an import, so it can be run and modified
independently. The trade-off: `ssm_lib.py` is duplicated. If you fix a bug in
one `ssm_lib.py`, apply it to the other (or symlink them). All the crustal
library fixes (ragged bins, rate anchoring, event-weight NaN guard, bootstrap
b_err, KS-not-MAXC Mc, usable-window clipping) are already present in this
copy.

The intraslab NRML (`ssm_intraslab_point_sources.xml`) is one of the source
files in the hazard logic tree, combined with the interface and crustal
sources.