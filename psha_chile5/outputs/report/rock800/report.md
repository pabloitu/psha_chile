# psha_chile5 sensitivity campaign, site rock800 (Vs30 800, Z1.0 40 m, Z2.5 0.6 km)

Cities: iquique, antofagasta, copiapo, valparaiso, santiago_centro, santiago_penalolen, concepcion, pucon, puerto_montt, puerto_aysen. Return periods: 475, 2475 yr. Truncation 3.0.


## 1. Inputs: catalog, classification, completeness, declustering

![sections through the classified catalog](01_inputs/01_sections_map.png)

*sections through the classified catalog* (01_inputs/01_sections_map.png)

![trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth](01_inputs/02_section_antofagasta.png)

*trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth* (01_inputs/02_section_antofagasta.png)

![trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth](01_inputs/03_section_concepcion.png)

*trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth* (01_inputs/03_section_concepcion.png)

![trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth](01_inputs/04_section_iquique.png)

*trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth* (01_inputs/04_section_iquique.png)

![trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth](01_inputs/05_section_santiago_centro.png)

*trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth* (01_inputs/05_section_santiago_centro.png)

![trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth](01_inputs/06_section_valparaiso.png)

*trench-normal section: classified events, Slab2 top and bottom, model hypocentre and lower depth* (01_inputs/06_section_valparaiso.png)

![in-slab classes: catalog and declustering](01_inputs/07_s00_classes.png)

*in-slab classes: catalog and declustering* (01_inputs/07_s00_classes.png)

![crustal classes: catalog and declustering](01_inputs/08_s00_classes.png)

*crustal classes: catalog and declustering* (01_inputs/08_s00_classes.png)

![interface: declustering](01_inputs/09_s01_decluster.png)

*interface: declustering* (01_inputs/09_s01_decluster.png)

- table: in-slab declustering per class and method (01_inputs/10_summary.csv)

- table: crustal declustering per class and method (01_inputs/11_summary.csv)


## 2. Interface source model

![interface geometry: segments and areas from Slab2](02_interface/01_s00_geometry.png)

*interface geometry: segments and areas from Slab2* (02_interface/01_s00_geometry.png)

![b-value against the fit floor](02_interface/02_s03_b_stability.png)

*b-value against the fit floor* (02_interface/02_s03_b_stability.png)

![observed and fitted MFD per segment](02_interface/03_s03_mfd.png)

*observed and fitted MFD per segment* (02_interface/03_s03_mfd.png)

![branch MFDs and moment closure](02_interface/04_s04_mfd.png)

*branch MFDs and moment closure* (02_interface/04_s04_mfd.png)

- table: a, b and rates per segment and estimator (02_interface/05_compare.csv)

- table: seismic vs geodetic moment per segment (02_interface/06_closure.csv)

- table: rate branches (02_interface/07_branches.csv)


## 3. In-slab source model

![b-value fit per class against the fit floor](03_inslab/01_s02_fit_deep_nest.png)

*b-value fit per class against the fit floor* (03_inslab/01_s02_fit_deep_nest.png)

![b-value fit per class against the fit floor](03_inslab/02_s02_fit_intra_slab.png)

*b-value fit per class against the fit floor* (03_inslab/02_s02_fit_intra_slab.png)

![b-value fit per class against the fit floor](03_inslab/03_s02_fit_slab_deep.png)

*b-value fit per class against the fit floor* (03_inslab/03_s02_fit_slab_deep.png)

![smoothed rate per class](03_inslab/04_s02_maps.png)

*smoothed rate per class* (03_inslab/04_s02_maps.png)

![source depths](03_inslab/05_s03_depths.png)

*source depths* (03_inslab/05_s03_depths.png)

![depth of the in-slab events below the Slab2 top](03_inslab/06_depth_profile.png)

*depth of the in-slab events below the Slab2 top* (03_inslab/06_depth_profile.png)

- table: quantiles of depth below the top, per class and region (03_inslab/07_depth_profile.csv)

- table: class parameters: b, rates, Mmax, kernel (03_inslab/08_classes.csv)


## 4. Crustal source model

![b-value fit per class](04_crustal/01_s02_fit_forearc.png)

*b-value fit per class* (04_crustal/01_s02_fit_forearc.png)

![b-value fit per class](04_crustal/02_s02_fit_intraarc.png)

*b-value fit per class* (04_crustal/02_s02_fit_intraarc.png)

![b-value fit per class](04_crustal/03_s02_fit_unclassified.png)

*b-value fit per class* (04_crustal/03_s02_fit_unclassified.png)

![smoothed background rate](04_crustal/04_s02_maps.png)

*smoothed background rate* (04_crustal/04_s02_maps.png)

![background cap and faults](04_crustal/05_s04_cap.png)

*background cap and faults* (04_crustal/05_s04_cap.png)

- table: class parameters (04_crustal/06_classes.csv)

- table: fault branches (04_crustal/07_branches.csv)


## 5. Ground-motion models

![in-slab GMMs: depth and magnitude scaling of the median](05_gmm/01_g1_depth_mag.png)

*in-slab GMMs: depth and magnitude scaling of the median* (05_gmm/01_g1_depth_mag.png)

![in-slab GMMs: median against hypocentre depth](05_gmm/02_g4_depth.png)

*in-slab GMMs: median against hypocentre depth* (05_gmm/02_g4_depth.png)

![controlling scenarios from the disaggregation: median, +/-1 sigma, epsilon to the city PGA](05_gmm/03_g2_scenarios.png)

*controlling scenarios from the disaggregation: median, +/-1 sigma, epsilon to the city PGA* (05_gmm/03_g2_scenarios.png)

![attenuation of the controlling scenarios](05_gmm/04_g3_attenuation.png)

*attenuation of the controlling scenarios* (05_gmm/04_g3_attenuation.png)

- table: median, sigma and epsilon per GMM and scenario (05_gmm/05_gmm_scenarios.csv)


## 6. Reference hazard

![source model](06_reference/01_f03_sources.png)

*source model* (06_reference/01_f03_sources.png)

![sources below the cities](06_reference/02_f04_sections.png)

*sources below the cities* (06_reference/02_f04_sections.png)

![mean hazard curves per city, families and 16-84 % band](06_reference/03_f01_curves.png)

*mean hazard curves per city, families and 16-84 % band* (06_reference/03_f01_curves.png, data 06_reference/03_f01_curves.csv)

![hazard curves per domain, in-slab classes separated](06_reference/04_f01b_curves_domains.png)

*hazard curves per domain, in-slab classes separated* (06_reference/04_f01b_curves_domains.png, data 06_reference/04_f01b_curves_domains.csv)

![share of the exceedance rate per source](06_reference/05_f02_contrib.png)

*share of the exceedance rate per source* (06_reference/05_f02_contrib.png)

- table: PGA and shares per city (06_reference/06_contributions.csv)

- table: shares with the in-slab classes (06_reference/07_contributions.csv)

![full-model curve per city with source branches](06_reference/08_antofagasta_PGA.png)

*full-model curve per city with source branches* (06_reference/08_antofagasta_PGA.png)

![full-model curve per city with source branches](06_reference/09_concepcion_PGA.png)

*full-model curve per city with source branches* (06_reference/09_concepcion_PGA.png)

![full-model curve per city with source branches](06_reference/10_copiapo_PGA.png)

*full-model curve per city with source branches* (06_reference/10_copiapo_PGA.png)

![full-model curve per city with source branches](06_reference/11_iquique_PGA.png)

*full-model curve per city with source branches* (06_reference/11_iquique_PGA.png)

![full-model curve per city with source branches](06_reference/12_pucon_PGA.png)

*full-model curve per city with source branches* (06_reference/12_pucon_PGA.png)

![full-model curve per city with source branches](06_reference/13_puerto_aysen_PGA.png)

*full-model curve per city with source branches* (06_reference/13_puerto_aysen_PGA.png)

![full-model curve per city with source branches](06_reference/14_puerto_montt_PGA.png)

*full-model curve per city with source branches* (06_reference/14_puerto_montt_PGA.png)

![full-model curve per city with source branches](06_reference/15_santiago_centro_PGA.png)

*full-model curve per city with source branches* (06_reference/15_santiago_centro_PGA.png)

![full-model curve per city with source branches](06_reference/16_santiago_penalolen_PGA.png)

*full-model curve per city with source branches* (06_reference/16_santiago_penalolen_PGA.png)

![full-model curve per city with source branches](06_reference/17_valparaiso_PGA.png)

*full-model curve per city with source branches* (06_reference/17_valparaiso_PGA.png)

- table: PGA per city at the target PoEs, mean and quantiles (06_reference/18_imls.csv)

![contribution by tectonic region, mean M and R](06_reference/19_disagg_trt_2475.png)

*contribution by tectonic region, mean M and R* (06_reference/19_disagg_trt_2475.png)

![contribution by tectonic region, mean M and R](06_reference/20_disagg_trt_475.png)

*contribution by tectonic region, mean M and R* (06_reference/20_disagg_trt_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/21_disagg_antofagasta_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/21_disagg_antofagasta_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/22_disagg_concepcion_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/22_disagg_concepcion_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/23_disagg_copiapo_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/23_disagg_copiapo_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/24_disagg_iquique_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/24_disagg_iquique_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/25_disagg_pucon_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/25_disagg_pucon_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/26_disagg_puerto_aysen_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/26_disagg_puerto_aysen_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/27_disagg_puerto_montt_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/27_disagg_puerto_montt_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/28_disagg_santiago_centro_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/28_disagg_santiago_centro_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/29_disagg_santiago_penalolen_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/29_disagg_santiago_penalolen_475.png)

![disaggregation M-R-epsilon, 475 yr](06_reference/30_disagg_valparaiso_475.png)

*disaggregation M-R-epsilon, 475 yr* (06_reference/30_disagg_valparaiso_475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/31_disagg_antofagasta_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/31_disagg_antofagasta_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/32_disagg_concepcion_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/32_disagg_concepcion_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/33_disagg_copiapo_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/33_disagg_copiapo_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/34_disagg_iquique_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/34_disagg_iquique_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/35_disagg_pucon_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/35_disagg_pucon_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/36_disagg_puerto_aysen_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/36_disagg_puerto_aysen_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/37_disagg_puerto_montt_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/37_disagg_puerto_montt_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/38_disagg_santiago_centro_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/38_disagg_santiago_centro_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/39_disagg_santiago_penalolen_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/39_disagg_santiago_penalolen_2475.png)

![disaggregation M-R-epsilon, 2475 yr](06_reference/40_disagg_valparaiso_2475.png)

*disaggregation M-R-epsilon, 2475 yr* (06_reference/40_disagg_valparaiso_2475.png)

- table: mean M, R, epsilon and shares per city (06_reference/41_disagg_summary.csv)

- table: mean M, R, epsilon per source type (06_reference/42_disagg_trt_summary.csv)


iml_total by return_period (06_contributions.csv)

| site | 475 | 2475 |
|---|---|---|
| antofagasta | 1.39 | 2.66 |
| concepcion | 1.42 | 2.67 |
| copiapo | 1.07 | 2.07 |
| iquique | 1.2 | 2.27 |
| pucon | 0.54 | 0.97 |
| puerto_aysen | 0.48 | 0.87 |
| puerto_montt | 0.63 | 1.31 |
| santiago_centro | 0.88 | 1.66 |
| santiago_penalolen | 0.81 | 1.51 |
| valparaiso | 1.51 | 2.82 |


## 7. Sensitivity

![largest change per axis and city](07_sensitivity/01_overview_PGA.png)

*largest change per axis and city* (07_sensitivity/01_overview_PGA.png)

![tornado per city](07_sensitivity/02_tornado_antofagasta_PGA.png)

*tornado per city* (07_sensitivity/02_tornado_antofagasta_PGA.png)

![tornado per city](07_sensitivity/03_tornado_concepcion_PGA.png)

*tornado per city* (07_sensitivity/03_tornado_concepcion_PGA.png)

![tornado per city](07_sensitivity/04_tornado_copiapo_PGA.png)

*tornado per city* (07_sensitivity/04_tornado_copiapo_PGA.png)

![tornado per city](07_sensitivity/05_tornado_iquique_PGA.png)

*tornado per city* (07_sensitivity/05_tornado_iquique_PGA.png)

![tornado per city](07_sensitivity/06_tornado_pucon_PGA.png)

*tornado per city* (07_sensitivity/06_tornado_pucon_PGA.png)

![tornado per city](07_sensitivity/07_tornado_puerto_aysen_PGA.png)

*tornado per city* (07_sensitivity/07_tornado_puerto_aysen_PGA.png)

![tornado per city](07_sensitivity/08_tornado_puerto_montt_PGA.png)

*tornado per city* (07_sensitivity/08_tornado_puerto_montt_PGA.png)

![tornado per city](07_sensitivity/09_tornado_santiago_centro_PGA.png)

*tornado per city* (07_sensitivity/09_tornado_santiago_centro_PGA.png)

![tornado per city](07_sensitivity/10_tornado_santiago_penalolen_PGA.png)

*tornado per city* (07_sensitivity/10_tornado_santiago_penalolen_PGA.png)

![tornado per city](07_sensitivity/11_tornado_valparaiso_PGA.png)

*tornado per city* (07_sensitivity/11_tornado_valparaiso_PGA.png)

![single GMM against the tree: PGA](07_sensitivity/12_fig_gmm_pga.png)

*single GMM against the tree: PGA* (07_sensitivity/12_fig_gmm_pga.png)

![single GMM against the tree: in-slab share](07_sensitivity/13_fig_gmm_share.png)

*single GMM against the tree: in-slab share* (07_sensitivity/13_fig_gmm_share.png)

![in-slab classes: summed vs class-cut smoothing](07_sensitivity/14_fig_intraslab_split.png)

*in-slab classes: summed vs class-cut smoothing* (07_sensitivity/14_fig_intraslab_split.png)

![PGA against truncation level](07_sensitivity/15_f05_truncation.png)

*PGA against truncation level* (07_sensitivity/15_f05_truncation.png)

![hazard curves per city, declustered vs full catalog](07_sensitivity/16_f06_declustering.png)

*hazard curves per city, declustered vs full catalog* (07_sensitivity/16_f06_declustering.png, data 07_sensitivity/16_f06_declustering.csv)

![epsilon distribution by source type](07_sensitivity/17_disagg_eps.png)

*epsilon distribution by source type* (07_sensitivity/17_disagg_eps.png)

- table: range per axis, city and return period (07_sensitivity/18_bars.csv)

- table: every row (07_sensitivity/19_tornado.csv)

- table: PGA and shares per split (07_sensitivity/20_summary.csv)


range by site (18_bars.csv)

| family | axis | antofagasta | concepcion | copiapo | iquique | pucon | puerto_aysen | puerto_montt | santiago_centro | santiago_penalolen | valparaiso |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | classification tolerance -5 / +5 km, all families | 6.16 | 3.25 | 3.81 | 5.94 | 1.37 | 1.6 | 8.96 | 2.77 | 2.42 | 8.08 |
| all | default-depth events to interface, all families | 0.49 | 0.65 | 0.22 | 0.59 | 0.15 | 0.01 | 0.46 | 0.53 | 0.5 | 0.62 |
| all | no declustering, all families | 14.28 | 8.94 | 14.69 | 8.27 | 11.94 | 8.09 | 20.47 | 13.76 | 12.88 | 7.73 |
| all | numerics: mesh 5 km, point-source distance 100 km | 1.14 | 0.48 | 0.62 | 0.82 | 0.88 | 4.24 | 0.28 | 1.87 | 1.16 | 1.13 |
| all | truncation 2.0 | 17.49 | 18.57 | 17.12 | 18.22 | 17.86 | 9.77 | 14.07 | 18.28 | 18.27 | 18.74 |
| all | truncation 2.5 / 4.0 | 9.96 | 10.66 | 9.21 | 11.67 | 10.64 | 5.22 | 7.0 | 10.61 | 11.36 | 11.26 |
| crustal | GMM (single vs tree) | 0.06 | 0.09 | 0.32 | 0.38 | 10.86 | 23.29 | 1.31 | 1.06 | 1.2 | 0.08 |
| crustal | background Mmax 7.5 | 0.01 | 0.03 | 0.08 | 0.03 | 0.07 | 0.12 | 0.24 | 0.18 | 0.12 | 0.02 |
| crustal | buffer margin 0 / 20 km | 0.07 | 0.0 | 0.0 | 0.12 | 1.61 | 2.09 | 0.2 | 0.89 | 0.82 | 0.06 |
| crustal | cap and fault Mmin 6.5 | 0.01 | 0.0 | 0.0 | 0.07 | 3.55 | 14.35 | 0.0 | 0.22 | 0.25 | 0.02 |
| crustal | classification tolerance -5 / +5 km | 0.01 | 0.04 | 0.04 | 0.0 | 0.08 | 0.01 | 0.15 | 0.02 | 0.01 | 0.02 |
| crustal | declustering | 0.0 | 0.0 | 0.01 | 0.0 | 0.02 | 0.79 | 0.01 | 0.02 | 0.04 | 0.0 |
| crustal | default-depth events to interface | 0.0 | 0.0 | 0.01 | 0.0 | 0.01 | 0.01 | 0.01 | 0.02 | 0.01 | 0.0 |
| crustal | faults vs no faults | 0.05 | 0.0 | 0.0 | 0.44 | 12.07 | 53.54 | 0.02 | 0.59 | 0.24 | 0.06 |
| crustal | no declustering (full catalog) | 0.0 | 0.03 | 0.03 | 0.01 | 0.25 | 8.87 | 0.09 | 0.02 | 0.12 | 0.0 |
| interface | GMM (single vs tree) | 22.7 | 19.64 | 19.55 | 12.59 | 9.94 | 1.68 | 21.07 | 11.12 | 9.28 | 17.36 |
| interface | MFD: tapered | 2.21 | 2.16 | 2.68 | 1.12 | 1.48 | 0.21 | 3.11 | 2.02 | 1.71 | 2.3 |
| interface | MMIN_HAZ 6.5 | 0.1 | 0.09 | 0.1 | 0.06 | 0.05 | 0.01 | 0.15 | 0.07 | 0.05 | 0.08 |
| interface | Z_BOTTOM 40 / 60 km | 7.91 | 10.22 | 7.54 | 5.79 | 8.94 | 0.39 | 5.5 | 6.43 | 7.53 | 10.2 |
| interface | Z_TOP 10 km | 3.51 | 2.82 | 4.35 | 1.63 | 2.44 | 0.29 | 5.22 | 2.32 | 2.02 | 4.83 |
| interface | b: fit floor 5.4 / 6.0 | 10.19 | 9.31 | 10.97 | 5.65 | 5.67 | 0.89 | 15.35 | 7.74 | 6.65 | 9.13 |
| interface | classification tolerance -5 / +5 km | 1.51 | 1.17 | 1.21 | 0.95 | 0.6 | 0.1 | 2.4 | 0.79 | 0.65 | 1.05 |
| interface | completeness table, ends of the ensemble | 6.23 | 5.55 | 6.33 | 3.52 | 3.19 | 0.51 | 9.58 | 4.36 | 3.71 | 5.38 |
| interface | declustering | 2.04 | 1.93 | 2.37 | 1.09 | 1.29 | 0.2 | 3.04 | 1.73 | 1.46 | 1.98 |
| interface | default-depth events to interface | 0.18 | 0.18 | 0.23 | 0.1 | 0.14 | 0.02 | 0.26 | 0.18 | 0.15 | 0.19 |
| interface | full 16-branch tree | 2.03 | 2.02 | 5.92 | 4.3 | 1.57 | 1.35 | 1.98 | 2.25 | 2.24 | 2.03 |
| interface | geometry: segmented | 16.78 | 7.66 | 20.79 | 6.53 | 6.02 | 1.58 | 8.12 | 6.65 | 6.33 | 6.82 |
| interface | keep 1962 / 1998 events | 0.81 | 0.72 | 0.82 | 0.46 | 0.42 | 0.07 | 1.25 | 0.57 | 0.47 | 0.7 |
| interface | no declustering (full catalog) | 11.21 | 10.33 | 13.32 | 5.94 | 7.07 | 1.05 | 17.0 | 9.39 | 8.32 | 10.53 |
| interface | rate: geodetic (mid) | 2.09 | 1.82 | 2.0 | 1.22 | 1.0 | 0.16 | 3.17 | 1.34 | 1.11 | 1.72 |
| interface | rupture aspect ratio 1.5 / 2 / 3 | 5.56 | 5.85 | 1.95 | 3.86 | 0.88 | 0.09 | 4.42 | 0.52 | 0.34 | 3.75 |
| interface | rupture scaling: Allen & Hayes | 0.68 | 3.32 | 3.59 | 0.73 | 2.06 | 0.35 | 2.73 | 4.21 | 3.85 | 4.57 |
| intraslab | GMM (single vs tree) | 21.07 | 20.06 | 27.56 | 41.86 | 20.62 | 0.2 | 9.38 | 37.7 | 38.85 | 22.21 |
| intraslab | Mmax pad 0 / 0.4 | 4.34 | 4.32 | 4.72 | 6.94 | 4.1 | 0.1 | 1.8 | 6.5 | 7.02 | 5.2 |
| intraslab | class domain cut at 50 km | 0.89 | 3.78 | 2.17 | 1.69 | 3.86 | 0.03 | 2.71 | 1.83 | 1.61 | 1.48 |
| intraslab | classification tolerance -5 / +5 km | 7.73 | 4.4 | 4.87 | 6.91 | 1.2 | 1.62 | 9.94 | 3.41 | 2.96 | 9.12 |
| intraslab | completeness table, ends of the ensemble | 4.15 | 0.9 | 4.65 | 2.86 | 5.98 | 0.05 | 3.41 | 4.21 | 4.37 | 11.93 |
| intraslab | declustering | 1.89 | 0.32 | 0.83 | 2.72 | 2.78 | 0.06 | 2.2 | 3.27 | 3.4 | 1.22 |
| intraslab | default-depth events to interface | 0.67 | 0.47 | 0.11 | 0.68 | 0.03 | 0.02 | 0.19 | 0.68 | 0.64 | 0.81 |
| intraslab | depths by slab-top regime, not thickness fraction | 0.25 | 0.55 | 0.29 | 0.81 | 1.44 | 0.03 | 0.98 | 1.49 | 1.67 | 0.3 |
| intraslab | intra_slab b: floor 5.5 / 5.8 | 0.69 | 2.8 | 4.41 | 4.49 | 1.03 | 0.05 | 1.79 | 3.25 | 2.97 | 4.92 |
| intraslab | kernel gaussian / cut-off 200 km | 1.24 | 3.76 | 0.9 | 2.17 | 2.49 | 0.09 | 1.21 | 0.22 | 0.28 | 1.92 |
| intraslab | no declustering (full catalog) | 2.76 | 1.87 | 1.56 | 2.33 | 4.58 | 0.08 | 3.49 | 4.07 | 4.79 | 3.51 |
| intraslab | pattern from all complete events / + calibrated kernel | 2.1 | 3.94 | 2.89 | 2.67 | 3.14 | 0.12 | 3.06 | 2.49 | 2.22 | 2.14 |
| intraslab | previous geometry: top + 7.5 km, depth-rule band | 3.03 | 2.09 | 1.72 | 4.61 | 1.18 | 0.04 | 0.55 | 3.71 | 4.0 | 3.17 |
| intraslab | rupture aspect ratio 2 | 0.33 | 0.47 | 0.83 | 1.37 | 0.16 | 0.0 | 0.1 | 0.49 | 0.45 | 0.36 |
| intraslab | rupture dip 45 / 90 | 2.57 | 2.62 | 1.8 | 4.7 | 2.29 | 0.06 | 0.96 | 4.35 | 4.8 | 3.37 |
| intraslab | rupture scaling: Allen & Hayes | 1.73 | 1.77 | 1.88 | 3.07 | 1.38 | 0.03 | 0.65 | 2.5 | 2.79 | 2.24 |
| intraslab | slab_deep b: floor 5.7 / 6.0 | 1.8 | 0.83 | 3.64 | 3.2 | 2.61 | 0.03 | 0.99 | 4.03 | 5.29 | 0.82 |
| intraslab | smoothing neighbours 10 / 50 | 1.53 | 5.37 | 2.24 | 2.03 | 2.48 | 0.09 | 3.14 | 2.56 | 2.32 | 1.6 |
| intraslab | sources from M5.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |


## 8. Model against the catalog

![in-slab rate near each city, model vs catalog](08_checks/01_check_rates.png)

*in-slab rate near each city, model vs catalog* (08_checks/01_check_rates.png)

![in-slab rate by depth and magnitude](08_checks/02_fig_intraslab_rates.png)

*in-slab rate by depth and magnitude* (08_checks/02_fig_intraslab_rates.png)

- table: model / catalog N(>=M) within 150 km (08_checks/03_rates.csv)

- table: model and catalog shares per depth band (08_checks/04_depth.csv)

- table: model / catalog per city for the classification, completeness, catalog and smoothing variants (08_checks/05_rates_compare.csv)

![completeness ensemble: b and N(>=M_ref) for perturbed tables, reference +/- sigma_b](08_checks/06_ensemble.png)

*completeness ensemble: b and N(>=M_ref) for perturbed tables, reference +/- sigma_b* (08_checks/06_ensemble.png, data 08_checks/06_ensemble.csv)

- table: completeness ensemble, every table and fit (08_checks/07_ensemble.csv)

![interface fitted vs observed rates, declustered and full catalog](08_checks/08_convention.png)

*interface fitted vs observed rates, declustered and full catalog* (08_checks/08_convention.png, data 08_checks/08_convention.csv)

- table: fitted / observed N(>=M), declustered and full catalog (08_checks/09_convention.csv)

- table: kernel cross-validation scores per class and setting (08_checks/10_kernel_cv.csv)


## 9. Manifest

93 hazard jobs, 93 with a calc id (manifest.csv).


## Missing inputs

- /data/PyCharmProjects/psha_chile/psha_chile5/outputs/interface/mmin_haz-5.5/figures/s02_mc.png
