# X1 figures

One line per figure in `figs/`: file, the question it answers. PNG, 200 dpi.

## Tier 1, matching (A3)

- `figs/t1_events_per_year.png`: Events per year with any native M ≥ 4.5 for the baseline, its neighbours and the tightest and widest grid corners, and the difference to the baseline.
- `figs/t1_grid_heatmap.png`: Probable splits, probable false merges and M ≥ 4.5 event counts over the time × distance window grid, for both source orders and two scalings.
- `figs/t1_hotspot_maps.png`: Hot-spot sequences (Maule, Illapel, Iquique, Arauco 2011) coloured by event label for the baseline and its two neighbours.
- `figs/t1_rm18_table.png`: RM18 events with their matched baseline event (or Cabello row before 1904) and the sources in that event.
- `figs/t1_window_calibration.png`: Δt, Δepicentre and Δdepth distributions of known same-event pairs per source pair, with the 95th / 99th percentile levels.
- `figs/t1_window_p99_period_mag.png`: 99th percentile of the epicentre difference of known pairs by period and by magnitude band, per source pair.

## Tier 2, location and depth (A4)

- `figs/t2_class_changes.png`: Events changing depth-proxy class against L-a, per 2° latitude band, for each location-priority variant (M ≥ 4.5 and M ≥ 5.5).
- `figs/t2_depth_spikes.png`: Depth histograms per source / agency with the automatically detected default-depth spikes (k = 5).
- `figs/t2_dz_vs_lat.png`: Depth differences against ISC-EHB L1 by latitude per source, coloured by L1 depth.
- `figs/t2_potin_vs_ehb_maps.png`: Median epicentre offset and depth difference per 1° cell, Potin against ISC-EHB L1 and L2.
- `figs/t2_sections.png`: Trench-perpendicular sections at six latitudes: Potin, ISC-EHB L1/L2 and ComCat depths against the Slab2 top and bottom (50 km strip either side).

## Tier 3, magnitudes (A5)

- `figs/t3_checks.png`: mb saturation against Lolli 2023; Potin codes against ISC / GUC in time; CSN Ml→Mlv switch; heaping of native values and the effect of dithering; NEIC Ms before / after 2013.
- `figs/t3_dmw_variants.png`: Distributions of Mw differences of variants M1–M8 against M0 per period.
- `figs/t3_fmd_variants.png`: Cumulative frequency–magnitude distributions per period for M0–M8.
- `figs/t3_mww_vs_gcmt.png`: GCMT Mw minus CSN and USGS Mww / Mwr against their own magnitude, with medians per 0.2 unit.
- `figs/t3_pairs_fits.png`: Native magnitude against GCMT Mw per scale with our linear / quadratic / exponential fits (chi-square with TC errors and OLS), the published relations and the 1:1 line.
- `figs/t3_residuals_time.png`: Residuals of the preferred unsplit chi-square fit against time per scale, by depth class.
- `figs/t3_tc_sigma.png`: Triple-collocation measurement error per magnitude scale (median and IQR over triples with ≥ 100 shared events).
- `figs/t3_type_year_raster.png`: Magnitude type × year raster of the frozen source tables (60 most used agency / type pairs).

## Tier 4, preview of B9

- `figs/t4_b_vs_floor.png`: b against fit floor per family for selected Mw variants, the spread over all combinations (grey) and b-positive.
- `figs/t4_large_events.png`: Fitted against observed N(≥ 7) and N(≥ 8) since 1904 per family and Mw variant, full and declustered.
- `figs/t4_tornado.png`: Tornado per family: range of Δb and of the N(≥ 6) ratio for each upstream choice changed one at a time.

## Tier 5, preview of A7

- `figs/t5_dslab_histograms.png`: Histograms of the slab-normal distance below the Slab2 top per 1° band and depth range, Potin events.
- `figs/t5_sections_dslab.png`: Trench-normal sections at six latitudes, Potin events coloured by distance below the Slab2 top.
- `figs/t5_two_plane_strip.png`: Latitude × depth range: bands where a two-component Gaussian mixture of the distance below the slab top beats one component (BIC), per dataset.

## Deeper pass

- `figs/t6_censoring_m9.png`: GCMT match share per native value, converted-Mw histograms and b(floor) for M0, M2, M6 and M9 (fit above the censoring cut).
- `figs/t6_potin_flat_slab.png`: Potin minus ISC-EHB L1 depth against depth in three latitude bands, and depth below the Slab2 top at 30–33°S for both catalogs.
- `figs/t6_two_plane_exclusions.png`: Two-plane test for Potin events with no exclusion, excluding cells with a slab top shallower than 50 km, and excluding events within 10 km of the slab top.
