# Catalog literature

Everything from the 44 papers in `refs/catalogs/` that the catalog rebuild (A2–A8) needs, so the PDFs need not be reopened for routine questions. Written in R1 (`tasks/R1_literature.md`), 10 Nov 2026, from the text files in `refs/catalogs/txt/`.
- **Pages:** `p. N` is the PDF page index, the `=== page N ===` marker in the text file, not the journal page.
- **Paraphrase:** numbers and coefficients are copied exactly; the text is paraphrased.
- **"(check PDF)":** marks values taken from the garbled old OCR (dziewonski_etal_1981) or not verified on the page image. Values from comte_etal_1999 and hanks_kanamori_1979 were checked on the page images. The Chilean rows of the engdahl_villasenor_2002 Table 1 were checked against the images (synthesis section 5).
- **Citations:** in `REFERENCES.md`.

Steps: A2 sources, A3 matching, A4 preferences, A5 magnitudes, A6 large events, A7 classification.

## Cards: Source catalogues

### Engdahl and Villaseñor 2002: Global Seismicity 1900–1999 (Centennial catalogue)
- Ref: Engdahl, E.R. and Villaseñor, A. (2002). Global seismicity: 1900–1999. In: International Handbook of Earthquake and Engineering Seismology, Vol. 81A, Chapter 41, pp. 665–690, Academic Press (IASPEI). ISBN 0-12-440652-1. No DOI on p. 1.
- What it is: compiled global catalogue of the 20th century (CENT.CAT; M ≥ 7 subset CENT7.CAT = Table 1), hypocentres relocated with EHB where digital phase data exist, one magnitude per event taken from other catalogues.
- Use for us: A2 (the "Centennial" source in the Ruiz order), A4 (location source per period), A5/Q1 (magnitudes are not recomputed; source and type per event in "mdo"/"sc"), A6 (Table 1 Chilean M ≥ 7 events, notes section 5).
- Coverage: 1900–1999, global. Selection cut-off 6.5 for 1900–1963 and 5.5 for 1964–1999 (p. 6, p. 23). Complete to MS 6.5 in 1930–1963, MS 5.5 in 1964–1999, MS 7.0 for the whole century (p. 6); for the historical period the catalogue is complete only to 7.0 (p. 23).
- Methods: hierarchical merge of catalogues (G&R 1954 for 1904–1952, Abe and Noguchi before 1904, Abe, B&D, P&S, Rothé, Utsu mainly for magnitudes) (p. 1). EHB relocation (ak135, pP/pwP/sP) only where digital phases exist: 1918–1942 and 1956–1999 (p. 23). ISS 1953–1963 only processed M ≥ 6; BCIS not digitised, not used (p. 2).
- Magnitude rule (p. 3): Mw if M0 available; h ≤ 60 km without M0: MS, then mB, then mb; h > 60 km without M0: mB then mb. MS is the reference scale; corrections are used only for selection and completeness, listed magnitudes are uncorrected originals (p. 5).
- Numbers to keep: MGR, B&D, Rothé and Pasadena (pre-1960) are reduced by 0.2 for selection (p. 5). Fig. 1 residuals vs Abe MS: P&S Mw 0.01 ± 0.21 (N 614); MGR 0.18 ± 0.22 (N 291); B&D 0.20 ± 0.26 (N 695); Rothé 0.22 ± 0.23 (N 61); Pasadena < 1960 0.20 ± 0.22 (N 59); Pasadena > 1959 0.04 ± 0.24 (N 44) (p. 4). Mw ≈ MS above ~6.5, Mw > MS below (p. 5). Harvard Mw available for most events MS > ~5.4, 1976–1999 (p. 3). Harvard M0 converted to an empirical MS (Ekström and Dziewonski 1988) for selection (p. 23). Mw = 2/3 log M0 − 10.7 (p. 22, p. 24). Table 2 rates: M ≥ 7.0 16 /yr, M ≥ 7.5 4 /yr, M ≥ 8.0 0.7 /yr (p. 23).
- Depth flags (Appendix 1, p. 24): isol HEQ origin and hypocentre fixed, DEQ depth free, LEQ depth fixed by program, FEQ depth fixed by Engdahl from independent information, XEQ poor solution; asol open-azimuth classes A–F (1900–1963), blank/Z (1964–1999). Table 1 itself does not print isol.
- Chile specifics: 106 Table 1 rows in 15–60°S, 64–82°W (synthesis section 5; all 106 checked against the page images, R1). Named: Valparaíso 1906 Mw 8.5, Chile 1922 Mw 8.7, 1928 Mw 7.7, Chillán 1939 Mw 7.7, 1949 mB 7.1, Great Chilean 1960 Mw 9.6, 1965 mB 7.4, 1971 Mw 7.8, 1985 Mw 8.0, 1995 Mw 8.0 (pp. 7–21) (check PDF). 1939 Chillán and 1943 (30.75°S) are not EHB relocated and have no depth.
- Known problems: historical locations of variable quality; depth errors may remain large outside the relocated years and before 1930 (p. 23). EHB cannot fully remove slab-related bias, up to several tens of km (p. 3). Rate excess 1940–1960 likely from MGR still too high after −0.2 (p. 23). Correction of 0.2 called an oversimplification (p. 5). Table 1 text is OCR of a scanned table.

### Storchak et al. 2013: Public release of the ISC-GEM catalogue (1900–2009)
- Ref: Storchak, D.A., Di Giacomo, D., Bondár, I., Engdahl, E.R., Harris, J., Lee, W.H.K., Villaseñor, A., Bormann, P. (2013). Public Release of the ISC–GEM Global Instrumental Earthquake Catalogue (1900–2009). Seismological Research Letters 84(5), 810–815. doi: 10.1785/0220130034
- What it is: short release note of ISC-GEM V1 (about 20,000 events, 1900–2009) with uniform relocation and Mw (direct or proxy).
- Use for us: A2 sources (what V1 contains, cut-offs); A4/A5 (Mw direct vs proxy, Ms preferred over mb for proxies). Superseded in detail by the PEPI 239 papers below.
- Coverage: 1900–1917 Ms ≥ 7.5 worldwide plus a few tens of smaller shallow events in stable continental areas; 1918–1959 Ms ≥ 6¼; 1960–2009 Ms ≥ 5.5 (p. 1). Cut-offs dictated by delivery time and funding (p. 1).
- Methods: two-stage relocation: EHB depths (surface reflections, station patch corrections), then new ISC locator with depth fixed to EHB, ak135, correlated errors (p. 2). Mw from GCMT (1976–2009) or literature M0 (1900–1979); otherwise proxy Mw from recomputed Ms and mb; Ms preferred if available, mb used for deep events (p. 2, p. 4).
- Numbers to keep: ~270,000 arrival times and ~110,000 amplitudes/periods from 85 high-quality station bulletins; ~620,000 ISS arrival times 1918–1959; ~1900 arrival times Gutenberg notepads/ISA 1904–1912; ~3800 BAAS 1913–1917; M0/Mw for 971 events from 1127 articles (p. 2). Global completeness "from Mw 5.6 before 1964 to Mw 6.4 after" as printed (p. 4; looks reversed, see notes). Rates of Mw > 7.5–7.6 best assessed over the whole window (p. 4).
- Chile specifics: Fig. 1 maps ISC-GEM events of Central and South America (p. 2). No event values.
- Known problems / caveats: regional completeness hard to assess with so few events (p. 4); dip in the magnitude-frequency curve at large M attributed to 110 years being too short (p. 4).

### Storchak et al. 2015: ISC-GEM catalogue introduction
- Ref: Storchak, D.A., Di Giacomo, D., Engdahl, E.R., Harris, J., Bondár, I., Lee, W.H.K., Bormann, P., Villaseñor, A. (2015). The ISC-GEM Global Instrumental Earthquake Catalogue (1900–2009): Introduction. Physics of the Earth and Planetary Interiors 239, 48–63. DOI 10.1016/j.pepi.2014.06.009
- What it is: introduction to the PEPI 239 special issue; history of networks, magnitude scales and bulletins; overview of V1.
- Use for us: A2 (catalogue structure: main + supplementary, d/p flags, quality A–D); A4/A5 (magnitude composition, why Mw); background on ISS/BCIS/ISC/NEIC bulletins.
- Coverage: Table 1 cut-offs (Ms): 1900–1917 7.5 (plus a few tens of smaller shallow events in stable continental areas), 1918–1959 6¼, 1960–2009 5.5 (p. 8). ~20,000 events (p. 1).
- Methods: as Bondár et al. 2015 (EHB depth then ISC locator, ak135; p. 9); Mw "d" (GCMT 1976–2009 or literature 1900–1979) or "p" (proxy from Ms/mb, Di Giacomo et al. 2015b) (p. 10).
- Numbers to keep: ~1,000,000 arrival times and 110,000 amplitudes added; M0/Mw for 967 events from 1127 articles (p. 8). ISS 1953–1963 processed only M ≥ 6 events; BCIS fills smaller ones (p. 7). ISC Bulletin ~5 million events, 125 million arrivals, ~19.5 thousand stations (p. 7–8). Expected ~350 events/yr with M > 5.5 worldwide (p. 12). Lowest cut-off 5.5 from 1960 possible because ISC Bulletin + GCMT data were electronic (p. 8).
- Chile specifics: 1960 Chile and 1964 Alaska exposed mb saturation (p. 7) and motivated Mw (p. 2). Long-serving South American stations: LPA La Plata (Argentina) 56 years and LPZ San Calixto (Bolivia) 45 years of surface-wave amplitudes (Table 4, p. 12). GEOFON first stage included Chile (p. 5). Jesuit stations in South America important early on (p. 4).
- Known problems / caveats: hypocentre quality in the first half of the 20th century inferior; sparse networks gave multiple local minima, resolved using damage/tsunami/surface rupture or by preferring locations inside known seismic zones (p. 11). Users must check d/p type and A–D flags (p. 11). Completeness varies by region (p. 12).

### Di Giacomo et al. 2014 (printed PEPI 239, 2015): ISC-GEM I. Data collection
- Ref: Di Giacomo, D., Harris, J., Villaseñor, A., Storchak, D.A., Engdahl, E.R., Lee, W.H.K., and the Data Entry Team (2015). ISC-GEM: Global Instrumental Earthquake Catalogue (1900–2009), I. Data collection from early instrumental seismological bulletins. Physics of the Earth and Planetary Interiors 239, 14–24 (available online 20 June 2014). DOI 10.1016/j.pepi.2014.06.003
- What it is: description of the digitising of arrival times (1904–1959) and amplitude-period data (1904–1977) for ISC-GEM.
- Use for us: A2 (what underlying data exist per period; why pre-1960 small events are absent); Q2 background.
- Coverage: search cut-offs 1900–1917 Ms ≥ 7.5 plus selected stable-continental shallow events with Ms 6.5–7.5; 1918–1959 Ms ≥ 6¼; 1960–2009 Ms ≥ 5.5 (p. 2). Initial pre-1976 selection used all magnitude types (many single-station) from an expanded Centennial catalogue; Ms reference type before GCMT (p. 2).
- Methods: OCR of ISS (1918–1959), manual entry of BAAS, Gutenberg notepads, ISA, station bulletins; JMA 1923–1970 parsed (p. 3–7).
- Numbers to keep: from 1976 selection cut-off Mw 5.6 (Ms 5.5) from GCMT, or Mw proxy from Ms or mb via Bormann et al. (2009) relations; cut-off lowered to Mw 5.5 for 1964–1977 because of larger uncertainty (p. 2). Table 1 data availability before the project: no body-wave arrivals before 1960; no surface-wave amplitudes before 1971; WWSSN SP amplitudes 1964–1970 (p. 2). 67 events / 1900 arrivals 1904–1912 (p. 3); 45 events / ~3800 arrivals BAAS (p. 4); >620,000 ISS picks from 850 stations (p. 7); ~270,000 JMA picks from ~230 stations (p. 7); >110,000 amplitude phases 1904–1970, of which 100,000 surface-wave (80,000 horizontal, 20,000 vertical) (p. 9); 30,000 Soviet + 4000 each UPP/KIR surface-wave amplitudes 1971–1977 (p. 9); magnitudes for >4600 relocated events 1904–1970 (p. 9). Conclusion states thresholds ≥7.5 to 1917, ≥6.25 1918–1959, >5.5 from 1960 (p. 9).
- Chile specifics: LPZ (San Calixto, Bolivia) and RIV singled out as key southern-hemisphere stations operating almost continuously (p. 9). Large gaps in southern hemisphere (p. 9).
- Known problems / caveats: 1900–1903 too few data, hypocentres from Abe and Noguchi (p. 9); BCIS (1930–1971) not digitised (p. 10); many Central European bulletins omitted or partial, so events with 3–5 station magnitudes may be poorly constrained, which matters where Ms/mb is the proxy basis (p. 10).

### Bondár et al. 2015: ISC-GEM II. Location and seismicity patterns
- Ref: Bondár, I., Engdahl, E.R., Villaseñor, A., Harris, J., Storchak, D. (2015). ISC-GEM: Global Instrumental Earthquake Catalogue (1900–2009), II. Location and seismicity patterns. Physics of the Earth and Planetary Interiors 239, 2–13. DOI 10.1016/j.pepi.2014.06.002
- What it is: the ISC-GEM relocation method (EHB depth, then ISC locator with fixed depth), uncertainties and before/after comparisons.
- Use for us: A3 (expected location shifts vs older catalogues), A4 (ISC-GEM epicentre/depth quality per period), A7 (depth reliability; which depths are fixed to tectonic setting).
- Coverage: 18,809 events 1900–2009 (p. 1, p. 10; 18,808 on p. 8). Cut-offs as above, stable-continental events Ms ≥ 6.5 before 1918 (p. 2).
- Methods: initial location by ISC locator (1904–1963) or ISC prime (1964–2009); EHB depth with depth phases (pP, sP, pwP), probabilistic re-identification, bounce-point topography/bathymetry from smoothed ETOPO1; then ISC locator with depth fixed to EHB (p. 4–6). Depth phases manually scrutinised for every event (p. 4).
- Numbers to keep: EHB depth normally needs ≥ 5 corroborating depth phases (p. 4). pwP not computed for bounce-point water depth ≤ 1.5 km (p. 5). Large complex events: depth set to USGS/NEIC broadband depths (p. 6). Events without usable depth phases: nominal depth from well-constrained neighbours in the same tectonic setting, using subduction cross-sections w.r.t. arc centre of curvature (p. 6); about one-third of events have no depth-phase information (p. 10). 65% have depth-phase-stacking depths (p. 6). Depth uncertainty: stacking uncertainty, else median absolute deviation of the ISC default-depth grid cell (typically < 15 km), else nominal 25 km (p. 7). Median EHB–ISC epicentre difference 9 km, 90% < 20 km (p. 6). Median origin-time uncertainty 0.25 s, median 90% ellipse area 105 km² (p. 7). Most accurate: SGAP < 120° and eccentricity < 0.75, or GT5 candidate: 14,517 of 19,711; 12,570 also with stacking depth (p. 8). Unreliable: SGAP ≥ 270° or nsta ≤ 5 → Supplementary (45 events) (p. 8). Supplementary 903 = 858 without magnitude + 45 poor locations (p. 8, p. 10). Before/after: median 10 km, 90% < 25 km; 90% of depth changes within ±20 km (p. 9). Median SGAP levels off at ~45° (p. 9). All events 1903–1930 reviewed manually (p. 10).
- Chile specifics: none beyond global maps (Fig. 7, p. 8) showing Andean slab.
- Known problems / caveats: events with depth fixed to tectonic setting or poor geometry never get best quality flags (p. 10); small risk that intraplate events get interplate depths (p. 10); pP inside source-time function of large shallow events (p. 5); pre-ISC-GEM depths often fixed to the surface (p. 10).

### Di Giacomo et al. 2015: ISC-GEM III. Ms, mb, proxy Mw, composition, completeness
- Ref: Di Giacomo, D., Bondár, I., Storchak, D.A., Engdahl, E.R., Bormann, P., Harris, J. (2015). ISC-GEM: Global Instrumental Earthquake Catalogue (1900–2009), III. Re-computed MS and mb, proxy MW, final magnitude composition and completeness assessment. Physics of the Earth and Planetary Interiors 239, 33–47. DOI 10.1016/j.pepi.2014.06.005
- What it is: recomputation of Ms and mb, derivation of the ISC-GEM proxy-Mw relations, magnitude priority, Mc per period.
- Use for us: A5 (the proxy relations behind every ISC-GEM "p" Mw before 1976; benchmark for our own Ms/mb→Mw), A4 (Mw priority), Q1 (ISC-GEM vs Centennial-type compiled magnitudes), Q2 (Mc per period).
- Coverage: cut-offs ≥7.5 (+ continental ≥6.5) to 1917, ≥6.25 1918–1959, ≥5.5 1960–2009 (p. 2); Section 8 lists "Ms ≥ 5.5 or Mw ≥ 5.6" for 1960–2009 (p. 13). Cut-off ≠ completeness (p. 2).
- Methods: Ms (IASPEI, Vaněk et al. calibration), reading Ms = (Msz+Msh)/2, station Ms = median of readings, network Ms = 20% alpha-trimmed median, SMAD uncertainty, ≥ 3 stations (p. 2–3); mb IASPEI 2013 formula, 20°≤Δ≤100°, T < 3 s (p. 6). Exponential non-linear least squares (R) for proxies; GOR shown for comparison; 90/10 training/validation split by histogram equalisation (p. 7–8).
- Numbers to keep:
  - Ms→Mw (Eq. 1): Mw = exp(−0.222 + 0.233 Ms) + 2.863; s.e. of a, b, c = 0.043, 0.004, 0.056 (p. 8, verified on page image). Training N = 15723 (Fig. 10 legend, p. 8). Caution below magnitude 5 (p. 9). Proxy uncertainty: Ms 6.0 or 8.0 ± 0.15 → 0.23 or 0.36 (p. 9). Validation median(true − proxy) 0.01, SMAD 0.13 (exp) vs 0.15 (GOR) (p. 9).
  - Ms GOR bilinear: Mw = 0.67 Ms + 2.13 for Ms ≤ 6.47; Mw = 1.10 Ms − 0.67 for Ms > 6.47 (p. 8, verified).
  - mb→Mw (Eq. 2): Mw = exp(−4.664 + 0.859 mb) + 4.555; s.e. 0.085, 0.012, 0.017 (p. 10, verified). GOR: Mw = 1.38 mb − 1.79 (p. 10). Training N = 27634 (Fig. 14, p. 10). Exp fits medians for 4.6 < mb < 6.5 (p. 10). Use with caution mb > 6.8 and mb < 5; only 13 ISC-GEM events needed mb proxies with 6.5 < mb < 6.8 (p. 10). Proxy uncertainty: mb 5.5 or 6.6 ± 0.1 → 0.18 or 0.4 (p. 10). Validation median −0.02 ± 0.25 (exp), −0.01 ± 0.34 (GOR) (p. 10).
  - Compared relations quoted: Scordilis 2006 Mw = 0.67 Ms + 2.07 (3.0–6.1), 0.99 Ms + 0.08 (6.2–8.2); Das et al. 2011 Mw = 0.67 Ms + 2.12 (3.0–6.1), 1.06 Ms − 0.38 (6.2–8.4); Scordilis Mw = 0.85 mb + 1.03 (3.5–6.2); Das et al. mb = 0.61 Mw + 1.94 (3.8–6.5) (p. 9–10).
  - Priority: 1 GCMT Mw; 2 literature Mw; 3 proxy from recomputed Ms; 4 proxy from recomputed mb (p. 10). GCMT 1976–2009 plus intermediate-depth 1962–1975 (p. 1, p. 12). Literature: 967 M0 values 1904–1978 (p. 12).
  - Ms only if depth − depth uncertainty ≤ 60 km (p. 3). 84 pre-1971 events with 2-station Ms (p. 3). Pre-1971 distance 2°–180°, T 5–60 s; modern Δ < 20° and T < 10 s excluded (p. 3).
  - Ms(ISC-GEM) vs G&R ~0.2 systematic difference, 10 outliers > 1 unit; Abe Ms fits well, adopted for 10 events 1900–1903 (p. 5).
  - 12,205 events 1976–2009, 1234 without direct Mw (p. 12). Deep events without direct Mw absent from main catalogue up to 1963 (except two in 1956, 1957) (p. 12). ~60% of Supplementary deeper than 60 km (p. 12).
  - Mc (max curvature, Fig. 23, values read from the figure, p. 14): 1900–1917 ≈ 7.55; 1918–1939 ≈ 6.35; 1940–1954 ≈ 6.5; 1955–1963 ≈ 6.15; 1964–1970 ≈ 5.65; 1971–1977 ≈ 5.6; 1978–2009 ≈ 5.6. Abstract: complete to Mw 5.6 from 1964; early period 7.5 to 6.2 (p. 1).
- Chile specifics: 1960 Valdivia Mw 9.6 proxy from Ms strongly underestimated (Ms saturation) (Fig. 13, p. 9); only four events with Ms 8–8.5 used for proxies (p. 9). LPZ good-quality Ms station, LPA less reliable (p. 4).
- Known problems / caveats: Ms–Mw non-linear; bilinear introduces discontinuity (p. 7); mb saturates above Mw ≈ 6 (p. 9); proxy has no seismic-moment reliability (p. 12); 5.3 ≤ mb ≤ 5.5 excess before 1979 from conservative selection (Fig. 8, p. 7).

### Di Giacomo et al. 2018: ISC-GEM after the Extension Project (V5, 1904–2014)
- Ref: Di Giacomo, D., Engdahl, E.R., Storchak, D.A. (2018). The ISC-GEM Earthquake Catalogue (1904–2014): status after the Extension Project. Earth System Science Data 10, 1877–1899. https://doi.org/10.5194/essd-10-1877-2018 (data: https://doi.org/10.31905/D808B825)
- What it is: V5 (released 27 Feb 2018): pre-1960 events below the V1 cut-offs added where station data allow, 2010–2014 added, 1900–1903 dropped.
- Use for us: A2 (V5 contents, quality flags), Q2 (which pre-1960 small events exist and how selected), A4/A5 (magnitude flags, composition), A7 (depth flags and default depths pre-1960).
- Coverage: 1904–2014, 35,225 events, 7126 in Supplementary (~93% pre-1960) (p. 16). V1 cut-offs restated as 7.5 for 1900–1918 (plus continental ≥ 6.5), 6.25 1918–1959, 5.5 1960–2009 (p. 1). Extension: pre-1960 events selected by station data (teleseismic arrivals and ≥ 2–3 amplitude stations), not by magnitude, because ~60% had no initial magnitude (p. 4, p. 6). 2010–2014 by magnitude ≥ 5.5 (p. 15).
- Methods: same as V1 (Bondár et al. 2015; Di Giacomo et al. 2015a) (p. 3). Ms with ≥ 3 stations, or 2 specially selected stations agreeing within 0.3 m.u. (uncertainty set 0.5) (p. 8).
- Numbers to keep: Quality flags (Table 1, p. 4): location A = SGAP < 120 and ecc < 0.75 or GTCAND; B = SGAP < 160; C other; D manual. Depth A = depth phases or GTCAND or station within 10 km; B = > 2 stations within 150 km; C other; D manual. Magnitude A = GCMT; B = literature or proxy from well-constrained Ms (> 4 stations, Ms 5.5–7.5, unc ≤ 0.2); C = literature or proxy from poorly constrained Ms or from mb; D = no magnitude, proxy unc > 0.7, or proxy from Ms < 5. 1920–1959: 11,572 of 19,341 extension events relocated (p. 6); flags Table 2 loc A/B/C/D 1744/3315/6431/83, depth 1886/479/9208/0 (p. 6); 6575 Ms recomputed, 2304 with Ms < 5.5, 80 with Ms ≥ 6.5 missing from V1; 276 two-station Ms (p. 8); magnitude flags B/C/D 3030/2824/5719 (p. 9). Median location change ~100 km (1920s) to ~20 km (late 1950s) (p. 6). 1904–1919: 1110 of 1935 accepted (p. 13); median NDEFSTA 6–16, SGAP 201–310° (p. 13); 927 Ms, 137 < 5.5, 306 ≥ 6.5, 12 > 7.5 (p. 14). 2010–2014: 2347 GCMT Mw, 248 proxies (p. 15). V5 composition: 45.72% GCMT, 42.85% Ms proxy, 8.1% mb proxy, 3.33% literature (p. 17). Mc: predigital annual 5.7–6.8; since 1964 5.5–5.7 (p. 17). Revised pre-1960 Ms: ~97% within ±0.3 of V1 (p. 16).
- Chile specifics: LPZ (San Calixto) one of few non-European amplitude contributors (p. 5). Cites Lange et al. 2017 (Chiloé 2016) and Ye et al. 2016 (Illapel 2015) as users (p. 2), no event values.
- Known problems / caveats: about half of extension events lack depth phases → default depth from tectonic setting/nearby events (p. 6); for 9418 (p. 6; 9417 in Fig. 8 caption, p. 8) previous depths unknown/zero. Intermediate and deep events strongly under-represented before 1950s–1960s (p. 17–18). Mc fluctuations (WWII, early 1960s, late 1970s) must be checked before rate studies (p. 17). Magnitude uncertainty much larger before 1976 (Fig. 26, p. 18–20).

### Storchak et al. 2017: Rebuild of the ISC Bulletin, part 1: 1964–1979
- Ref: Storchak, D.A., Harris, J., Brown, L., Lieser, K., Shumba, B., Verney, R., Di Giacomo, D., Korger, E.I.M. (2017). Rebuild of the Bulletin of the International Seismological Centre (ISC), part 1: 1964–1979. Geoscience Letters 4:32. https://doi.org/10.1186/s40562-017-0098-z
- What it is: reprocessing of the 1964–1979 ISC Bulletin with ak135, the new ISC locator, cleaned phases and recomputed mb/Ms.
- Use for us: A2/Q2 (ISC Bulletin as source for 1964–1981 events below ISC-GEM thresholds), A3 (rebuilt locations changed), A5 (ISC mb/Ms definitions in rebuilt bulletin), A7 (ISC default depths).
- Coverage: 1964–1979; 172,071 events (p. 8).
- Methods: removed ~11,500 poorly constrained/phantom events (single solution < 3 stations, out-of-area solutions, ~7900 LAO-only) (p. 3); relocated events with ≥ 4 station reports and max Δ > 20° (or 10–20° with > 1 country) (p. 6); otherwise best local agency hypocentre is prime (p. 6).
- Numbers to keep: default depth: most common among well-recorded events in each 1×1° cell, else 10 or 35 km per Flinn–Engdahl region (p. 7). Many cases switched from JB default 33 km to 10 km (step at ~20 km depth difference) (p. 9). mb, Ms = median of station values, SMAD on alpha-trimmed set, ≥ 3 stations required; Ms dropped/added when depth crosses 60 km (p. 7). ~68,000 new events, 255 new stations, 814,695 new phases (+10%), ~2700 new Ms (p. 1, p. 5). Corrected ~30,000 minute, ~1000 hour, 138 day errors (p. 4). 98% of events moved < 100 km, 90% < 40 km, 70% < 20 km; 460 events > 300 km (max 3740 km); 205 depth changes > 300 km (max 634 km) (p. 9). 4855 events lost their magnitude (mb from < 3 stations) (p. 9). ISC did not compute its own Ms until 1978 (Prague formula) (p. 9). ~25% of events analyst-reviewed (p. 8).
- Chile specifics: none.
- Known problems / caveats: only "with issues" events reviewed (≥ 50 km shift, large depth/OT change) (p. 7); 1980–2010 still to be rebuilt at time of writing (p. 12).

### Di Giacomo and Storchak 2016: Preferred magnitudes in the ISC Bulletin
- Ref: Di Giacomo, D., Storchak, D.A. (2016). A scheme to set preferred magnitudes in the ISC Bulletin. Journal of Seismology 20, 555–567. DOI 10.1007/s10950-015-9543-7
- What it is: rules to choose one preferred value per magnitude type and one "best-suited (prime)" magnitude per ISC Bulletin event.
- Use for us: A4/A5 (if we take magnitudes from the ISC Bulletin for Q2 events, which value to pick and in what order).
- Coverage: designed on 2011–2012 bulletins (p. 3).
- Methods / numbers to keep: Ms and mb: before ISC review prefer NEIC, MOS, IDC (global), then regional agencies with ≥ 3 teleseismic (Δ > 20°) stations; after ISC review only ISC-recomputed Ms/mb, and only if > 3 and with teleseismic data from ≥ 2 stations beyond 30° (p. 7). ISC filters: mb 21–100°, T < 3 s; Ms 20–160°, T 10–60 s; no Ms if depth > 60 km (p. 7). Mw: GCMT, then NEIC, then documented regional agencies (p. 8). ML, MD, mb(LG): sum of four scores: |agency − event median| (4 if ≤ 0.25 … 0 if > 1.0), close-network stations within 300 km (4 if > 20 … 0 if < 3), NSTA (5 if ≥ 40, 4 15–40, 3 10–15, printed "5" for 5–10 (likely typo for 2), 1 3–5, 0 < 3), uncertainty (4 ≤ 0.2 … 0 > 0.9 or missing) (p. 9–10, NSTA table checked on page image). JMA magnitude always preferred when present (p. 8). Prime magnitude order: Mw > Ms > mb > local (MJMA, ML, mb(LG), MD); mB would go between Ms and mb if adopted (p. 11). ME from NEIC output but never prime (p. 12). Excluded: BJI Ms7, Mwp, IDC mb1, mb1mx, mbtmp, MS1, ms1mx, M, MG (p. 11).
- Chile specifics: none.
- Known problems / caveats: scores tuned to current bulletin contents and may change (p. 10); non-preferred values not necessarily worse (p. 10); a scheme proposal "to implement", i.e. not yet operational at writing (p. 1, p. 12).

### Weston et al. 2018: ISC-EHB reconstruction
- Ref: Weston, J., Engdahl, E.R., Harris, J., Di Giacomo, D. and Storchak, D.A. (2018). ISC-EHB: reconstruction of a robust earthquake data set. Geophys. J. Int. 214, 474–484. doi:10.1093/gji/ggy155.
- What it is: EHB procedure reapplied to the reviewed ISC Bulletin, 2000–2013, with automatic and manual depth review in subduction cross-sections; introduces depth quality classes L1–L3.
- Use for us: A4/A7 (depth quality per event; default depths to recognise), A3 (depth offsets vs GCMT, ISC, USGS broadband).
- Coverage: 2000–2013 in this paper (1964–1999 and 2014+ to follow, p. 10). Selection: > 25 teleseismic (> 28°) stations, secondary teleseismic azimuthal gap < 180°, ISC prime magnitude > 3.75 (p. 2). Global M > ~5.5 events usually included (p. 5).
- Methods: EHB with ak135; first round fixes depths to ISC, then defaults and prior knowledge, then free depth; second round resets weak depths; manual cross-section review (840 sections, 89 regions) (p. 2–5).
- Default/fixed depths (p. 3): ridge or open ocean 10 km; within 55 km of trenches or volcanoes, or known shallow-seismicity regions, 15 km; priority of external depths USGS broadband > ISC-GEM > published studies; second review: < 3 defining depth phases and depth error > 5 km → 10 km (ridge/ocean) or 15 km (continental, trench, volcanic), or external depth; remaining events with a GCMT solution set to the GCMT depth. Manual fixes usually in 10 km increments (p. 4). Large aftershock sequences set to neighbours' depths, class L3 (p. 5).
- L1–L3 (p. 4): L1 free depth, error < 5 km and ≥ 3 defining depth phases, or fixed depth well constrained by depth phases or USGS broadband. L2 free depth, error < 5 km with < 3 depth phases, or free depth error 5–15 km, or fixed to GCMT depth. L3 free depth error > 15 km, or fixed from nearby seismicity or tectonics.
- Numbers to keep: 69,655 selected, 69,027 kept; 30,720 free, 38,307 fixed; L1 18,570, L2 21,589, L3 28,868; median formal depth error L1 1.65 km, L2 4.23 km (p. 5). L1 vs GCMT −0.8 ± 8.5 km (8335), vs USGS broadband 4.2 ± 5.1 km (866), vs ISC −2.4 ± 7.3 km (18,295) (p. 8). GT mislocation 11.0 ± 5.4 km (150 events) (p. 7). L1 relative depth uncertainty probably ≤ 15 km (2σ) (p. 7–8). Magnitudes not recomputed: ISC mb, ISC Ms, GCMT Mw (p. 5); Table 1 counts mb only 29,852; mb+Ms+Mw 17,034; mb+Ms 16,993; mb+Mw 5141 (p. 4).
- Chile specifics: South American margin split into regions incl. Chile North, Chile Central, Chile South (p. 6); Fig. 9 Peru–Chile border cross-sections (p. 7).
- Known problems: formal depth error ignores lateral heterogeneity (relative, not absolute) (p. 7); ISC depths overestimated for shallow events (p. 8); GCMT default depths 12 or 15 km produce a lineation, ISC-EHB deeper (p. 6); GCMT deeper for intermediate and deep events (p. 6); subduction-zone bias remains with a 1-D model (p. 6).

### Engdahl et al. 1998: EHB global teleseismic relocation
- Ref: Engdahl, E.R., van der Hilst, R. and Buland, R. (1998). Global teleseismic earthquake relocation with improved travel times and procedures for depth determination. Bull. Seismol. Soc. Am. 88(3), 722–743. No DOI on p. 1.
- What it is: the original EHB algorithm and catalogue; nearly 100,000 teleseismically well-constrained events 1964–1995 from ISC + NEIC phases (p. 1).
- Use for us: A2/A4 (EHB is the relocation behind Centennial, ISC-GEM, ISC-EHB), A3 (expected epicentre/depth shifts vs ISC, NEIC, CMT), A7 (depth reliability, depth phases in subduction zones).
- Coverage: 1964–1995; complete to about Mw 5.2 (p. 1, p. 8). Generic M = Mw, else Ms (> 4.7), else mb (p. 8).
- Methods: ak135; P, S (excluding > 100° P, > 80° S), PKiKP (> 110°), PKPdf, depth phases pP, pwP, sP (excluding < 30°) (p. 3). Depth phases reidentified statistically (random association by prior probabilities) (p. 6–7). Ellipticity, bounce-point bathymetry (ETOPO5 smoothed 20′), patch station corrections (437 patches 5°×5°) (p. 3–5). Selection: ≥ 10 teleseismic first arrivals and teleseismic open azimuth < 180° (p. 3, p. 7).
- Numbers to keep: residual cut-offs 7.5 s regional, 3.5 s teleseismic (p. 3); no pwP if bounce-point water < 1.5 km (p. 4); pwP read as pP with 4 km water and no regional P → depth overestimated by about 50 km (p. 3); phase priors water < 1.5 km pP 0.60, sP 0.22, pwP 0, PcP 0.18; ≥ 1.5 km pP 0.26, sP 0.15, pwP 0.40, PcP 0.19 (p. 6); weights 1.0 (0.1 s precision), 0.7 (1 s), × 0.25 for teleseismic S (p. 7); 85 % free-depth solutions (p. 7); M = 4.6 + 0.0047 N if no magnitude, N teleseismic stations (p. 8); log10 NM = 9.5 − 1.1 M (p. 8). EHB depth uncertainty ±10 to 15 km (p. 21). Test-event mislocation 9.4 ± 5.7 km (p. 19).
- Table 2 (p. 12), median ± spread, all depths: epicentre shift vs ISC 7.6 ± 5.5 km, vs CMT 32.7 ± 21.3 km; depth shift vs ISC −1.7 ± 11.8, BBD 1.2 ± 5.3, MT 1.6 ± 11.4, CMT 1.2 ± 13.1 km; CMT > 300 km −5.5 ± 10.7 km.
- Chile specifics: BANJO and SEDA 1994 arrivals included (p. 2). Fig. 11 cross-sections Peru, Arica bend (15–23°S), northern Chile flat slab: EHB (≥ 5 depth phases) gives sharper WBZ than ISC (p. 16–17). Latin America relocation vectors coherent only over small regions, no clear link to slab geometry (p. 12); large SW-ward shifts in Arica attributed to North American station dominance and patch corrections (p. 16).
- Known problems: poor solutions = epicentre error > 35 km, or depth not constrained to ≤ 15 km without depth phases (unless fixed from waveforms or seismicity) (p. 7). ISC fixes depths at 10, 15, 33 km when unconstrained (p. 14). Large shallow complex events: pP inside the P source-time function (p. 19). Remaining slab bias needs a 3-D model (p. 19).

### Dziewonski et al. 1981: CMT method
- Ref: Dziewonski, A.M., Chou, T.-A. and Woodhouse, J.H. (1981). Determination of earthquake source parameters from waveform data for studies of global and regional seismicity. J. Geophys. Res. 86(B4), 2825–2852. No DOI printed on p. 1 (publisher banner: 10.1029/JB086iB04p02825). Text is garbled old OCR; values below (check PDF).
- What it is: the founding centroid-moment-tensor paper; joint inversion of moment tensor and centroid (lat, lon, depth, time) from long-period body waves (p. 1).
- Use for us: A2/A5 background for GCMT (centroid vs hypocentre; why GCMT depths and epicentres differ from EHB/ISC).
- Coverage: 25 events: 14 (1977–1979, mostly W and S Pacific, two in South America, one South Atlantic) plus 11 of the Sumba 1977 sequence (p. 22) (check PDF).
- Methods: SRO/ASRO long-period data, T > 45 s, normal-mode synthetics for model 1066B, attenuation FSQMK (p. 3–5); start from PDE/ISC hypocentre, iterate moment tensor and centroid perturbations (p. 2–4).
- Numbers to keep: usable range roughly magnitude 5.5 to 7.5–8.0 (p. 1); moments analysed 5 × 10^24 to 8 × 10^26 dyn cm (p. 20); SRO saturates for moments above 5 × 10^27 dyn cm (p. 20); kernel library suggested every 10 km depth, 0–700 km (p. 21); Sumba aftershock depths fixed at 33 km, a Bouvet event fixed at 10 km, others fixed at 20 km (p. 14, p. 22, p. 24) (check PDF). 5 of 11 intermediate/deep events with ε 0.16–0.28 (p. 22).
- Chile specifics: none identified in the text; the two South American events of Table 4 not legible in the OCR (check PDF).
- Known problems: absolute locations exploratory, location changes sometimes excessive with poor coverage (p. 23); centroid depths shift systematically shallower than PDE, especially for shallow events (p. 23); origin-time shifts positive, related to source duration (p. 23); shallow-source Mrθ, Mrφ poorly resolved below ~10 km depth (p. 5).

### Ekström et al. 2012: GCMT project 2004–2010
- Ref: Ekström, G., Nettles, M. and Dziewoński, A.M. (2012). The global CMT project 2004–2010: Centroid-moment tensors for 13,017 earthquakes. Phys. Earth Planet. Inter. 200–201, 1–9. doi:10.1016/j.pepi.2012.04.002.
- What it is: GCMT methods update (intermediate-period surface waves from 2004) and catalogue summary 2004–2010.
- Use for us: A5 (GCMT Mw is the homogenisation reference: thresholds per period, completeness), A4 (mechanisms, centroid depth constraints), A6 (Maule 2010, Tocopilla 2007, Tarapacá 2005 centroids).
- Coverage: catalogue starts 1976 (p. 1). 1976: only events with reported mb ≥ 6.0 or MS ≥ 6.0 analysed; median Mw falls 5.7 to 5.4 in 1977–2003; about 5.2 in 2004–2010 (p. 5, p. 7). Completeness: linear down to Mw 5.0 for 2004–2010; slope break near Mw 5.3–5.4 for 1976–2003 (p. 7); previous completeness level Mw 5.4 (p. 8). Selection: any reported magnitude ≥ 4.8 (p. 2).
- Methods: body waves, mantle waves (> 135 s, from 1981), intermediate-period surface waves (from 2004) (p. 2). Filters and weights by Mw: mantle waves zero below M 5.5, full above 6.5; body and surface waves full below 6.5, none above 7.5 (p. 3). Lateral heterogeneity: M84C, then SH8/U4L8 since July 1991 (p. 2). Starting hypocentres mainly NEIC; since 2006 also surface-wave detections (Ekström 2006); 222 events located only by surface waves (p. 2). Deviatoric constraint (no isotropic part) (p. 5).
- Depth fixing (p. 5): minimum allowed centroid depth 12 km (source fixed at 12 km when the inversion goes shallower); unstable depths fixed at the reported hypocentral depth or a depth suited to the region. (Default 15 km, 10 km in 1981–1985: Engdahl et al. 1998 p. 12.)
- Numbers to keep: half duration t = 1.05 × 10^−8 M0^(1/3) (s, dyne-cm) (p. 5, eq. 1); boxcar moment-rate before 2004, triangle from 2004 (p. 5); 13,017 solutions 2004–2010 (p. 5); 38 events Mw ≥ 7.5 in Table 1 (p. 6); Sumatra 2004 standard CMT M0 4.01 × 10^29 vs multiple-source 1.17 × 10^30 dyne-cm (p. 7).
- Chile specifics: Maule 2010 Mw 8.8, second largest 1976–2010, centroid time shift 58.9 s, half duration 60 s, periods > 200 s (p. 7–8). Table 1 (p. 6): #5 2005-06-13, #22 2007-11-14, #34 2010-02-27 (notes section 5; signs lost in text).
- Known problems: Mw definition from M0 not written in this paper. Point-source CMT underestimates the size of very long ruptures (Sumatra) (p. 7). Weaker events (near 5.0) from surface-wave-only locations, often southern oceans (p. 2).

## Cards: Chilean catalogues and networks

### Cabello et al. 2025: Integrated Seismic Catalog for Chile from 1513 to 2022
- Ref: Cabello, C., Montalva, G., Leyton, F. (2025). Integrated Seismic Catalog for Chile from 1513 to 2022. Journal of South American Earth Sciences 164, 105639. DOI 10.1016/j.jsames.2025.105639 (p. 1). Data: Zenodo 10.5281/zenodo.15443140 (p. 13).
- What it is: merge of ISC-GEM, ISC, USGS (NEIC-ANSS ComCat), GCMT, CERESIS-GEM and "CSN-improved" for 57–14°S, 75–64°W, with Chile-specific regressions of each native scale to GCMT Mw (p. 1–3).
- Use for us: A2 (sources, counts), A5 (relations, and what was converted vs. passed through), A6 (pre-1900 events only from CERESIS; modified magnitudes), A3 (matching windows).
- Coverage (Table 1, p. 3): USGS 1906–2022 (m, mb, Md, ML, MS, Mw; 52,752 ev), CERESIS 1513–1963 (Mw; 1,031), ISC 1902–2022 (mb, Mw, MS, ML, Md, m; 206,861), ISC-GEM 1906–2019 (Mw; 3,166), CSN-improved 2000–2022 (ML, Mc, mb, MS, Mw, Mww; 131,047), GCMT 1971–2022 (MS, mb, Mw; 2,564). Final 229,866 events, Mw 0.2–9.5, depth 0–750 km (p. 6). Final records per catalogue (Table 5, p. 9): GCMT 2,564; CSN-improved 127,859; CERESIS 710; ISC-GEM 965; USGS 28,670; ISC 69,099. No magnitude or depth filtering of input catalogues (p. 3).
- Methods: regression pairs matched with 10 km / 1 min windows (p. 3); merging of catalogues with 50 km / 10 min and a priority (hierarchy) matrix by catalogue and scale (Table 4, p. 8); within-catalogue duplicates removed by hand (p. 5). Regressions: 75/25 % train/test split repeated 1000 times plus 1000 bootstrap resamples; the fitting method (OLS or orthogonal) is not stated (p. 3). Hypocentres kept from the preferred catalogue, not recomputed (p. 1, 10). CSN-improved locations replaced by Potin et al. (2024) where origin time identical to the second ("Relocated_Potin", p. 7–8).
- Numbers to keep, Table 3 (p. 8, verified on page image):
  - I ML CSN-improved, depth ≤50 km: Mw(GCMT) = 0.80(±0.05)·"Mw(CSN-improved)" + 1.15(±0.26), 4.5<Mw<6.5.
  - II ML CSN-improved, depth >50 km: Mw = 0.94(±0.03)·x + 0.30(±0.17), 4.5<Mw<6.5. (Both I and II print the predictor as "Mw(CSN-improved)" although the Mag 1 column says ML.)
  - III Ms CSN-USGS-GCMT pooled: Mw = 0.74(±0.02)·Ms + 1.60(±0.10), 4.5<Mw<6.4.
  - IV mb CSN-USGS-GCMT pooled: Mw = 1.04(±0.04)·mb − 0.02(±0.19), 4.5<Mw<6.5.
  - V Ms ISC (taken from OpenQuake oq-mbtk, not fitted): Mw = exp(−0.22 + 0.23·Ms(ISC)) + 2.86 (±0.2).
  - VI mb ISC: Mw = 0.87(±0.05)·mb + 0.75(±0.25), 4.5<Mw<6.5.
  - VII Mw CSN-improved: Mw = 0.92(±0.02)·Mw(CSN) + 0.43(±0.11) (no range printed).
  - VIII Mw USGS: Mw = 0.94(±0.01)·Mw(USGS) + 0.35(±0.06), 4.5<Mw<6.5.
  - IX Ms GCMT: Mw = 0.84(±0.01)·Ms + 1(±0.07), 4.5<Mw<7.3.  X mb GCMT: Mw = 1.03(±0.03)·mb + 0(±0.13), 4.5<Mw<7.0.
- Simplifications stated (p. 3): Mw(ISC-GEM) ≡ Mw(GCMT); ML(CSN), ML(USGS), ML(ISC) treated as one scale; Mc, Md, m have no reliable regression and are taken as Mw (mostly <5). Table 6 (p. 10): magnitudes outside each equation's range, above or below, are taken as Mw unchanged.
- Residuals (Table 2, p. 6): ML-Mw RMS ≤50 km 0.0707 (Bastías & Montalva 2016) vs 0.0591 (this work); >50 km 0.0345 vs 0.0239; Ms-Mw Scordilis06 0.0693 (Ms ≤6.1) / 0.0385 (Mw >6.1) vs 0.0621; mb-Mw OQ 2.461 vs 2.366. Eq. 1 is a mean of squares (named ECM/RMS).
- Completeness (max curvature, 3 bands 1513–1960, 1960–2000, 2000–2022; p. 8): north (15–25°S) Mc 6.2 → 2.7; centre (25–35°S) 6.8 → 3.2; south (35–45°S) 6.8 → 3.0.
- Chile specifics: 1730-07-08 CERESIS Mw 8.74 replaced by Mw 9.1–9.3 (Carvajal et al. 2017); 1835, 1928, 1939 magnitudes recalculated (Text S1 of the supplement, values not in the paper), flagged "Magnitude changed" (p. 7). Three CERESIS events with day 0 set to day 1, "Date_changed" (Table 8, p. 10). Missing depths (mostly pre-1960) assigned from Slab2.0, flagged "original depth:" (p. 7). 13 events tagged crustal from literature (Table 7, p. 10).
- Caveats by authors: location/depth heterogeneity kept from sources; historical uncertainties; Slab2 depths may be wrong for crustal events; Md/Mc/m not converted (affects Mw<5 and b-value); hierarchy is subjective (p. 10). No pre-1900 method other than taking CERESIS Mw as given (plus the four replaced values).

### Potin et al. 2024: A revised Chilean seismic catalog from 1982 to mid-2020
- Ref: Potin, B., Ruiz, S., Aden-Antoniow, F., Madariaga, R., Barrientos, S. (2024). A Revised Chilean Seismic Catalog from 1982 to Mid-2020. Seismological Research Letters 96(1), 484–498 (January 2025 issue, online 4 Sept 2024). DOI 10.1785/0220240047 (p. 1). Journal page = marker + 483.
- What it is: cleaned and 3D-relocated CSN analyst catalogue 1982–mid-2020, with Mc/b-value maps and HDBSCAN cluster list. Data: catalogue Zenodo 10.5281/zenodo.13146436, picks 10.5281/zenodo.13173435, 3D models 10.5281/zenodo.13146424 (p. 13).
- Use for us: A2/A4 (preferred source 1982–2020-07), A5 (CSN magnitude types by period), A3 (event IDs/times for Cabello's relocation link), A7 (depth quality).
- Coverage: 1982–mid-2020, 18–46°S relocation (p. 3); mostly ML ≥ 3.0 events; CSN only processes M>3.0 or felt (p. 1–2). Only 310 events 44–46°S (p. 4). Jan–Sep 2000 data permanently lost (p. 4).
- Methods: quality filter ≥3 stations, ≥5 arrivals, ≥2 stations with both P and S; duplicates removed by comparing arrival times; outlier picks via Wadati-like diagram and O−C analysis (p. 2). Original CSN: no readings beyond 400 km, regional 1D tabular models (p. 1). Relocation in one of six 3D tomography models (each ~8° latitude, 4° overlap), velocities, locations and station corrections inverted jointly (Araujo et al. 2021 approach, INSIGHT code); start from smoothed CSN 1D models; 40 km smoothing length; inversion cells 6×6×3 km, forward grid 1.5 km cubes (p. 3).
- Numbers to keep: final 118,004 events, 1,102,293 P and 933,669 S arrivals; filter removed 117,489 P and 78,354 S arrivals (p. 2). Mc of CSN catalogue fluctuates spatially 2.5–4.0 (maps from 2010 to "mid-2022" as printed, 40 km radius nodes, ≥100 events, 100 subsets of 90 %; p. 5–7). Magnitude threshold stable ~2.5 for all Chile since 2019 (p. 5).
- Magnitude types by period (p. 4): coda magnitude (Mc) by SSN until 2002, ML afterwards; ML on average 0.25 lower than Mc during the overlap years; since mid-2000s Brune-spectral Mw for M>6.0 (sometimes down to 4.5); since 2015 W-phase Mww systematically for M > ~4.5. Threshold raised after Maule 2010, Iquique 2014, Illapel 2015; lowered ~1 yr in 2011 in central Chile (p. 4–5).
- Network history (p. 2–4): IPOC incorporated from 2006; 2013 CSN transformation after Maule, real-time new stations finished end 2014; before 2002 network limited to central Chile; coverage stable since 2001 (central), 2007 (north), 2012 (central-north); no significant network change since 2015.
- Chile specifics: low seismicity near 26°S is a coverage artefact (p. 4). 46 clusters <65 km plus 2 deep Jujuy clusters >200 km (Table 1, p. 10–12).
- Caveats: no depth uncertainties given (catalogue gives RMS per event, p. 3); horizontal depth alignments before 2012 at 150 km (31.5°S) and 15 km (33°S) from tabular models; flat slab not visible at 33°S; events east of the Andes poorly located in depth (p. 5, 13). Conclusion says the magnitude scale was "homogenized" (p. 13) but no method or relation is given in the paper.

### Barrientos and CSN Team 2018: The seismic network of Chile
- Ref: Barrientos, S., and National Seismological Center (CSN) Team (2018). The Seismic Network of Chile. Seismological Research Letters 89(2A), 467–474. DOI 10.1785/0220160195 (p. 1). Journal page = marker + 466.
- What it is: description of CSN network history and the post-2013 real-time broadband/strong-motion/GNSS network.
- Use for us: A2 (network periods behind completeness changes), A6/A7 (seismogenic zones, large-event list with magnitudes).
- Coverage: Fig. 2 seismicity from SISRA (1900–1981), USGS (1982–1999), CSN (2000–2016) (p. 2).
- Network history: first countrywide network after the 1906 earthquake by Montessus de Ballore: one first-order station in Santiago, four second-order stations ~800 km apart (Wiechert 200 kg), 29 Agamennone seismoscopes (p. 3). CSN started March 2013 as continuation of the Seismological Service (p. 3). Mandate: 65 real-time BB + strong-motion stations and 130 GNSS (abstract) / 65 multiparametric + 63 new GNSS (p. 3); 297 offline accelerographs (2 %g trigger) transferred 2015–2016 (p. 3). Network codes: C1 new (65 stations), C pre-2013 (p. 3). 10 GRO stations 2011–2012; 7 more stations in 2017; Fig. 3: 105 multiparametric stations incl. 20 IPOC (CX), 10 GRO, 3 GSN, 2 GEOSCOPE; 128 GNSS (p. 3–4). Station spacing ~80–90 km (p. 4). Denser arrays: IPOC north ~10 yr, metropolitan central Chile ~20 yr (p. 5). Software: EarlyBird, SeisComP, SEISAN; solutions within 5 and 20 min (p. 6).
- Numbers to keep: design target detection M ≥3.5 countrywide; Mc ≈3.5 from G-R for 2013–2016 with aftershocks kept; b 0.78 (2014) to 0.95 (2015); ~10 events M>6.5 in three years (p. 4). GNSS detection of interface events mostly above M6.5 offshore, >7.2 in darker zones (Fig. 7, p. 6).
- Chile specifics: interface ruptures to 45–53 km depth; M~8 return 80–130 yr per region, ~12 yr country-wide (p. 1). Intermediate-depth 60–200 km; M~8 events at 80–100 km all extensional; downdip-compressional events at 60–70 km near coast (p. 2). Shallow crustal 0–20 km examples (p. 2). Outer-rise extension events (p. 3).
- Caveats: no magnitude types or relations stated; magnitudes quoted as "M" (Illapel 2015 given as M 8.4 on p. 1, 3, 5 and M 8.3 on p. 5, 7).

### Riquelme et al. 2018: W-phase real-time implementation and network expansion in Chile
- Ref: Riquelme, S., Medina, M., Bravo, F., Barrientos, S., Campos, J., Cisternas, A. (2018). W-Phase Real-Time Implementation and Network Expansion from 2012 to 2017: The Experience in Chile. Seismological Research Letters 89(6), 2237–2248. DOI 10.1785/0220180146 (p. 1). Journal page = marker + 2236.
- What it is: CSN W-phase CMT (Mww) operations since 2011, with comparison to USGS WCMT and GCMT.
- Use for us: A5 (CSN Mww as an Mw source and its threshold over time), A6 (large-event Mw/centroids), A2 (BB station counts by year).
- Coverage: >300 events since 2011 (p. 1, 4); threshold moved from Mww 6.5 with 36 BB stations in 2012 to 4.8 with 106 stations (p. 1, 10).
- Methods: triggered for M ≥5.0 from Earthworm or analyst SEISAN solutions; hypocentre as initial centroid; half-duration from preliminary ML via TH = TD = 1.2×10^-8 M0^(1/3); grid search in time (4 s) and space (0.4°); stations 5–50° (180 s fixed window 5–12°, Tp to Tp+15Δ beyond); for preliminary M 4.8–5.5 minimum distance 1.5–2.0°; PREM Green's functions; inversions at 5–30 min after OT (p. 3, 5).
- Numbers to keep: BB stations 36 in 2010; 37 → 49 after CSN creation 2013; 106 by 2017 (p. 4). Events per year <20 before 2014, ~90 now (p. 4). Mww 5–5.5 mechanisms not well constrained (p. 5). Fig. 5 (p. 5, image checked): CSN Mww vs USGS WCMT and GCMT mostly within ±0.2, few outliers beyond ±0.5; no regression given.
- Chile specifics: see notes section 5 (Maule, Iquique and aftershock, Illapel, Melinka).
- Caveats: Illapel text reports M0 5.71×10^28 dyn·cm with Mw 8.36 and the same strike/dip/rake as the Iquique aftershock (p. 9), apparently a copy error (see notes 6).

### Riedel-Hornig et al. 2026: Seismicity catalogue of the entire Chilean margin (18–56°S) from an automated approach
- Ref: Riedel-Hornig, M., Sippl, C., Tassara, A., Ruiz, S., Potin, B., Puente, J. (2026). Seismicity catalogue of the entire Chilean margin (18 to 56° S) from an automated approach. Earth System Science Data 18, 1–16. DOI 10.5194/essd-18-1-2026 (p. 1). Data: Zenodo 10.5281/zenodo.15284376 (p. 13).
- What it is: deep-learning catalogue 2017–2021 (EQTransformer/INSTANCE, PyOcto, NonLinLoc in Potin 3D model, HypoDD) with a fixed station set for time homogeneity (p. 1–3).
- Use for us: A7 (interface/intraslab/crustal classes, DSZ extent 18–35°S, Slab2 misfit), A2 (comparison with CSN completeness), A3 not useful (small events).
- Coverage: main catalogue 18–43°S, 621,917 events; secondary 39–55°S with 1D model (Ammirati et al. 2024), 12,933 events (p. 4, 6–7).
- Methods: event = ≥8 picks with ≥4 stations having P and S; duplicates in segment overlaps <10 s, <0.5°, ≤50 km depth plus shared picks; pick removal >2σ or |res| >2 s (p. 3–4). ML from horizontal max amplitudes after Hutton & Boore (1987) with Bormann (2012) attenuation; no ML for VC-dominated events (p. 4). Classes: outer rise (west of trench +0.25°), interplate (within a margin of Slab2 down to 60 km; margin = mean depth error in 0.25° cells, 2.5–10 km), intraslab, crustal (above Tassara & Echaurren 2012 Moho), not classified (p. 4).
- Numbers to keep: classes 5,099 outer rise, 66,284 interplate, 65,136 crustal, 459,208 intraslab (>70 %) (p. 4). Mean NLL errors 4.8 km lon, 2.2 km lat, 6.1 km depth; onshore generally <5 km (p. 5). Mc global 2 (max curvature) but 2.5 taken as representative; local <1.5 (Santiago) to 4 (network edge); secondary Mc 3 (p. 5–7). Poor coverage 24–27°S and 41–43°S (p. 5).
- Comparison with CSN/Potin (p. 8): CSN/Potin Mc 3–4 over most of Chile vs 2.5; ~10 times fewer events per year; only geometries and clusters compared, not individual events or magnitudes. No magnitude offset between their ML and CSN magnitudes is reported in the main text (magnitude stability in time in Fig. S21, p. 8). Potin's catalogue described as 1985–2020 on p. 8 and 1982–2020 in Fig. 8 caption.
- Chile specifics: Valparaíso 2017 Mw 6.7, Coquimbo 2019 Mw 6.7, Atacama 2020 Mw 6.9, Rio Loa Mw 6.2 (p. 2, 8). Almost all seismicity 44–50°S crustal (p. 7, 12).
- Caveats: misclassification from Slab2/Moho errors and narrow channel; intraslab tops deeper than Slab2 below 100 km; adding Argentinian INPRES picks (2018, 2,598 matched events) moved events east of central Chile shallower, i.e. eastern hypocentres systematically too deep without Argentine stations (p. 12–13).

### Sippl et al. 2023: The Northern Chile forearc constrained by 15 years of permanent seismic monitoring
- Ref: Sippl, C., Schurr, B., Münchmeyer, J., Barrientos, S., Oncken, O. (2023). The Northern Chile forearc constrained by 15 years of permanent seismic monitoring. Journal of South American Earth Sciences 126, 104326. DOI 10.1016/j.jsames.2023.104326 (p. 1).
- What it is: review plus extended IPOC catalogue 2007–2021 (>180,000 events) for ~18.3–23.5°S (p. 1–2).
- Use for us: A7 (interface vs upper/lower DSZ plane vs intermediate-depth cluster geometry, class definitions), A6 (historical and instrumental large events in northern Chile).
- Coverage: IPOC permanent monitoring since late 2006; 28 BB stations now (p. 4). Catalogue 182,847 events (p. 5).
- Methods: STA/LTA trigger, MPX and spicker pickers, double-difference relocation (Sippl et al. 2018); location uncertainties <5 km inside the network (p. 4–5). Magnitudes from Münchmeyer et al. (2020) (p. 5). Classes relative to the Sippl 2018 slab model: UP, P1 interface, P2 upper DSZ plane, P3 lower DSZ plane, ID intermediate-depth, NN; UP now restricted to depth <60 km; new class MI mining (<15 km from a mapped mine and depth <15 km) (p. 5).
- Numbers to keep: ID 116,027, P2 8,103, P3 5,182 (129,312 intraslab), P1 15,162, UP 30,371 of which 16,927 MI (p. 5). Mc 2.7 (Hainzl et al. 2019) (p. 20–21). Interface dip ~20°, reaching >60 km east of coast (p. 11); megathrust ~500 km along strike, ~150 km downdip to 60 km (p. 5). DSZ facts in notes section 4.
- Chile specifics: see notes section 5 (1543, 1615, pre-1768, 1871, 1877, 1967, 1995, 2005, 2007, 2014, Aroma, Pica, Rio Loa).
- Caveats: offshore, P1/UP/P2 hard to separate; deep UP vs P1 ambiguous 20.5–21.5°S (p. 11); intraslab rate decrease 2014–2021 mostly a detection change (p. 20); events outside the network have larger errors; Jujuy cluster removed (p. 19). Outer-rise events present in CSN (21–22.5°S) but not in IPOC (p. 18).

### Münchmeyer et al. 2020: Low uncertainty multifeature magnitude estimation, North Chile
- Ref: Münchmeyer, J., Bindi, D., Sippl, C., Leser, U., Tilmann, F. (2020). Low uncertainty multifeature magnitude estimation with 3-D corrections and boosting tree regression: application to North Chile. Geophysical Journal International 220, 142–159. DOI 10.1093/gji/ggz416 (p. 1). Journal page = marker + 141.
- What it is: calibrated magnitudes (ML-like Wood–Anderson and MA peak displacement) for the IPOC catalogue 2007–2014 using 2D distance-depth corrections, 3D station source-path terms and boosting trees.
- Use for us: A5 only indirectly (magnitude type of IPOC/Sippl catalogues, calibrated to GCMT Mw 5–6); A2 (what "magnitude" means in Sippl 2023).
- Coverage: Sippl et al. (2018) catalogue, 101,601 events (96,185 used), magnitudes <2 to 7.7, Mc for ML ~2.8 (p. 2–3); 31 stations, ~1,100,000 P and ~650,000 S picks (+450,000 predicted S) (p. 3).
- Methods: 110 features; Y − M = Φ(r, depth) + L_s(hypocentre) + B_s + ε (Eq. 1, p. 4); grid 50 distances 20–500 km × 20 depths 10–200 km (p. 4, Table B1 p. 15); calibration to 114 GCMT events with Mw 5.0–6.0 (of 155), weight λ_Mw = 0.1 (p. 5). Final catalogue values: non-boosting estimates for M>6.0, boosting for M<5.5, linear blend 5.5–6.0 (p. 13).
- Numbers to keep: single-station RMSE displacement NE 0.196 full corrections vs 0.237 for 1D hypocentral distance (Table 3, p. 9); boosting reduces to 0.103 (Table 2, p. 9). Wood–Anderson magnitude scales 1:1 with MA below 6.0 and saturates above (p. 7), saturation above M~6.5 vs Mw (p. 8); velocity and acceleration scales saturate and overestimate small events (p. 8). Energy vs ML ~4:3 below 2.0 (p. 8). Station-bias uncertainty <0.01 (p. 10).
- Caveats: scales only matched to Mw inside 5–6; no conversion relation to Mw outside that range is given; not compared with CSN magnitudes.

## Cards: Historical

### Ruiz and Madariaga 2018: Historical and recent large megathrust earthquakes in Chile
- Ref: Ruiz, S., Madariaga, R., 2018. Historical and recent large megathrust earthquakes in Chile. Tectonophysics 733, 37–56 (Review Article). DOI 10.1016/j.tecto.2018.01.015 (p. 1).
- What it is: review that re-reads historical chronicles (1543–1900) and recent large events by zone (North, North-Central, Central, South-Central) and assigns each large interplate event an along-dip domain (A near trench, B middle, C deep interface; Lay et al. 2012 notation) (p. 2, p. 7).
- Use for us: A6 (authority for Mw and class of large events; Table 1 Mw and domain for 18 events, Table 2 three giant events), A7 (interface / intraslab / outer-rise / shallow-crustal labels in Figs. 4–7), A2 (recommends Centennial catalogue for large events up to ~2010, p. 15).
- Coverage: Chile 18–46°S, 1420/1543–2017; Table 1 "Mw ~8.0" events since 1900 (p. 16); Table 2 trans-Pacific tsunamigenic events since 1900 (p. 16); Figs. 4–7 "main earthquakes since 1900" (pp. 6, 8, 10, 13).
- Methods: no new computations; Mw taken from cited studies (Beck et al. 1998, Pacheco and Sykes 1992, Okal 2005, Cifuentes 1989, etc.); domain from slip models, tsunami size, damage. Historical magnitudes discussed against Lomnitz (1970, 2004), Comte and Pardo (1991), Kausel (1986), Abe (1979).
- Numbers to keep: generic historical relation M = 1.62 log L + 4.44, L = length of isoseismal VIII (Dorbath et al. 1990) (p. 5); Centennial catalogue complete for M > 6.0 only after 1960, completeness magnitude close to 6 (p. 15, Fig. 8); USGS 1980–2017 G-R slope close to b = 1 for M < 7, excess of M 8–9 events (p. 15); CSN completeness in northern Chile ML ~3.5 (p. 5); giant events have Mw at least 8.4, rate about two per century (p. 16); recurrence of giant events ~400 yr in Central/South Chile (p. 14); Mw ~8 recurrence 80–100 yr (p. 16).
- Chile specifics: full event list in notes section 5 (Table 1, Table 2, text and figure labels with pages). Intraslab intermediate-depth: Calama 1950 Mw ~8.0 and Tarapacá 2005 Mw 7.8 at ~100 km (p. 5); Chillán 1939 Mw 7.8 (p. 9); La Ligua 1965 Mw 7.4, Punitaqui 1997 Mw 7.1 (p. 11); 1927 Mw 7.2 and 1945 Mw 7.1 (p. 9); historical 1647 and (proposed) 1786 intraslab (p. 16).
- Known problems / caveats: authors say pre-1960 mechanism classification is not possible from catalogues (p. 15); historical catalogues biased by seismic-gap ideas (p. 1). Internal inconsistencies found in the text (see notes section 6): 1918 date (4 vs 18 December), 1983 date and Mw (4 November Mw 7.4 in Table 1 vs 4 October Mw 7.7 in text and Fig. 5), 1995 date (30 vs 31 July), Taltal 1966 domain (B in Table 1 vs "deeper part of plate interface" in text), "1768" vs "1786", "5 October 1959" Copiapó (probably 1859), "1985" for Antofagasta 1995 and "1996" for Taltal 1966 (pp. 7, 9, 16).

### Lomnitz 2004: Major Earthquakes of Chile: A Historical Survey, 1535–1960
- Ref: Lomnitz, C., 2004. Major earthquakes of Chile: a historical survey, 1535–1960. Seismological Research Letters 75 (3), 368–378. No DOI on p. 1.
- What it is: update of Lomnitz (1970) with Table 1 of 41 major Chilean events 1535–1960 (date, local time, location, magnitude, notes) (p. 2, pp. 3–8).
- Use for us: A6 (historical magnitudes, dates, times for pre-1960 large events; contrast with Ruiz and Madariaga 2018), A2 (it is the Ms source for 30 GHEC events, Albini et al. 2014 p. 11), A3 (local vs GMT times for 1906–1960).
- Coverage: Chile 1535–1960; shallow to intermediate shocks only; completeness threshold around Ms 7.5; not complete for smaller or deep events; list stops in 1960 because catalogues are adequate afterwards (p. 8).
- Methods: magnitudes are Ms estimates from coseismic effects and felt-area size compared with recent shocks of known magnitude, following Kawasumi (1951) (p. 2); instrumental Ms after 1900 refer to Engdahl and Villaseñor (2003) (p. 8); magnitudes slightly revised from 1970 values (p. 8).
- Numbers to keep: 41 events (p. 2); uncertainty in some cases ±0.5 magnitude, not estimated better than half a unit (p. 8); completeness Ms 7.5 (p. 8); epicentres may be off by a degree or so, older magnitudes may be underestimated (p. 10); 1960 moments 1.9 and 3.2 x 10^23 N m, Mw 9.6, rupture ~1000 km (p. 8); 1939 and 1953 Chillán focal depth 60 km (p. 7).
- Chile specifics: every event listed in notes section 5. Times are local; GMT given for 1906–1960 (e.g. 1906 16 August 8:40 PM = 00:40 GMT; 1922 10 November 11:33 PM = 04:32 GMT; 1939 24 January 11:32 PM = 03:32 GMT 25 January) (pp. 6–7).
- Known problems / caveats: 1939 Chillán was a normal event in the Nazca plate (p. 10); not all events are subduction events (p. 10); 1562 might have been a storm (p. 3); 1687 may be 1688 (p. 4); 1715 is a southern-Peru (Moquegua) event and 1868 epicentre near Islay, Peru (pp. 4, 6); 1960 magnitude quoted between 8.3 and 9.6 (p. 7); mainshock and foreshock magnitudes for 1906–1960 are G-R / Richter values (8.6, 8.4, 8.3), not Mw.

### Giesecke et al. 2004: The CERESIS earthquake catalogue and database of the Andean Region
- Ref: Giesecke, A., Gómez Capera, A.A., Leschiutta, I., Migliorini, E., Rodriguez Valverde, L., 2004. The CERESIS earthquake catalogue and database of the Andean Region: background, characteristics and examples of use. Annals of Geophysics 47 (2/3), 421–435. No DOI on p. 1. (File name "giesecki_2004".)
- What it is: history and description of the CERESIS (1985, SISRA project) catalogue and intensity database, plus a Boxer (Gasperini et al. 1999) test on 37 South American crustal events (pp. 1–12).
- Use for us: A2 (what CERESIS contains for Chile), A5 (CERESIS magnitude is Ms; Boxer Mw generally smaller than CERESIS Ms), A6 only marginally (no Chilean event processed).
- Coverage: regional catalogue 1471–1985 (p. 4); intensity database 16 318 IDP for 3183 events, 1471–1985, nine countries (p. 7); Chile 1730–1977, 61 earthquakes, 816 IDP (Table I, p. 7); Chile I0 ≥ 8: 1730–1976, 13 earthquakes, 382 IDP, 330 used (Table III, p. 9).
- Methods: national groups entered hypocentres in common formats; regional coordinator L. Ocola; catalogue edited by Askew and Algermissen (p. 3–4). Chilean catalogue (CERESIS vol. 5) documented mainly by Greve (1964), Lomnitz (1970), Kausel (1979a, b) (p. 5). Bolivian part compiled to 1981 with USGS and ISC data (p. 5). Record format: header line with Ye Da Ho Mi Se, ILat ILon (intensity epicentre), MLat MLon, Dph, Ms, I0, Ne (Table II, p. 7). Intensities in MM or MSK; duplicate records for uncertain intensities (7/8 gives two records) (p. 8).
- Numbers to keep: Boxer Mw minus CERESIS Ms from −1.4 to +1.8 in Table V, generally negative ("Boxer Mw smaller than Ms") (p. 10–11); Boxer selection removed 89 events with < 10 IDP, 45 with depth > 30 km, 18 offshore, 11 subduction, 1 incoherent; 37 processed (Table IV, p. 9–10).
- Chile specifics: Chilean subduction events 1730, 1751, 1822, 1868, 1877, 1928, 1966 excluded from the Boxer study (p. 9–10); 1868 and 1877 intensity localities lack coordinates (p. 5); no Chilean event in Table V.
- Known problems / caveats: the paper gives no magnitude-type list beyond the Ms column, no depth rules and no completeness statement; "free" or round depths are not discussed (our known issue cannot be checked here). National catalogues lost interest in the 1990s (p. 2).

### Albini et al. 2014: The Global Earthquake History
- Ref: Albini, P., Musson, R.M.W., Rovida, A., Locati, M., Gomez Capera, A.A., Viganò, D., 2014. The Global Earthquake History. Earthquake Spectra 30 (2), 607–624. DOI 10.1193/122013EQS297 (p. 1).
- What it is: journal summary of the GEM GEH project: archive GHEA (239 studies, 3175 records, 994 earthquakes) and catalogue GHEC v1.0 (825 events, 1000–1903, Mw ≥ 7, lowered to 6.5) (pp. 1–8).
- Use for us: A2 (pre-1904 global source; for Chile its magnitudes come from Lomnitz 2004), A5 (Ms taken as Mw without conversion).
- Coverage: 1000–1903; threshold Mw 7, lowered to Mw 6.5 (6.0 in Sub-Saharan Africa, Australia) (p. 8); 715 events M ≥ 7 (p. 8).
- Methods: expert selection of one preferred study per event (65 cases with different studies for epicentre and magnitude); 169 archive events dropped because selected study gave M < 7 (p. 8). Magnitude hierarchy Mw, then Ms, then other; Ms and (shallow) MJMA treated as equivalent to Mw for M 6.5–8; no conversion (p. 13).
- Numbers to keep: 825 events from 87 sources (p. 8); location uncertainty available for 188 (23%) (p. 9); 75% without depth (p. 9); magnitude types 47.9% Mw, 38.9% Ms, 12.6% MJMA, 0.6% unspecified (p. 15); Table 1 totals 825 epicentres, 395 Mw, 321 Ms, 104 MJMA, 5 M (p. 12).
- Chile specifics: Lomnitz (2004) supplies 30 Ms values and no epicentres (Table 1, p. 11); CERESIS (1995) 46 epicentres, 14 Ms (Central and South America) (p. 10, checked on PDF); Engdahl and Villaseñor (2002) 32 epicentres, 13 Mw, 15 Ms, 2 MJMA (global) (p. 11); ISC-GEM (2012) 4 Mw (p. 11); Dorbath et al. (1990) 2 Mw (p. 11).
- Known problems / caveats: epicentre of a large subduction event is a convenience point; uncertainty should equal source dimensions (p. 9); deep events only recognised from modern seismicity distribution (p. 13).

### Albini et al. 2013: Global Historical Earthquake Archive and Catalogue (1000–1903)
- Ref: Albini, P., Musson, R.M.W., Gomez Capera, A.A., Locati, M., Rovida, A., Stucchi, M., Viganò, D., 2013. Global Historical Earthquake Archive and Catalogue (1000–1903). GEM Technical Report 2013-01 V1.0.0, 202 pp., GEM Foundation, Pavia. No DOI on p. 1; doi 10.13117/GEM.GEGD.TR2013.01 on p. 4.
- What it is: full report behind Albini et al. (2014): archive contents by region, catalogue rules, format, completeness, IT (pp. 15–150).
- Use for us: A2 (GHEC as pre-1904 source and what it holds for Chile), A5 (no magnitude conversion), A4 (Chile pre-1904 parameters are Lomnitz 2004 magnitudes with epicentres from another source).
- Coverage: 1000–1903, Mw ≥ 7, threshold lowered to 6.7 or 6.5 Mw (6.0 Sub-Saharan Africa, Australia) (p. 114); meant to match the GEM instrumental catalogue starting 1904 at Mw ≥ 7 (p. 112).
- Methods: epicentres from the selected source (mostly area of strongest effects; 39 Bakun-Wentworth, 19 Gasperini/Boxer); after 1897 some circum-Pacific epicentres instrumental (p. 115). Depth from source when given (p. 116). Magnitude hierarchy Mw > Ms > other, Ms ≈ Mw for 6.5–8, no conversion (p. 116). Format fields EpDet and MDet (bx, bw, int, cat, instr) and MType (w, s, jma, blank) (Table 1.10, p. 130).
- Numbers to keep: 182 magnitudes with uncertainty 0.1–1.0 (p. 118); 188 location uncertainties (p. 115); Table 1.8 Mw 395, Ms 321, MJMA 104, unspec. 5 (p. 117); subduction rupture-length relation Mw = 1.61 log L + 4.53 (inverted Blaser et al. 2010, log L = −2.81 + 0.62 Mw) and Mw = 4.441 + 0.846 log A (Strasser et al. 2010), used for Indonesia (p. 98); completeness test: Centennial events Mw ≥ 7, depth ≤ 40 km, 1960–1999, in 40-yr windows stepped by 5 yr (p. 132).
- Chile specifics: Lomnitz (2004) is the most comprehensive Chilean overview, updated "without new investigation", 41 events (p. 50); Lomnitz (2004) gives 32 records in GHEA (p. 29) and 30 Ms values in GHEC (p. 127); Udías et al. (2012) 4 records (1647, 1657, 1730, 1751) (p. 35); CERESIS (1985) MDPs: 80 South American earthquakes, 1062 MDPs, 71 usable in demo (p. 37); CERESIS 1868 Arica appears twice with two epicentres (p. 49); South America completeness: stable rate per 40 yr from the late 16th century but far below the modern rate (modern ~34 per 40 yr, historical peaks ~18, read from Fig. 4.6) (p. 135).
- Known problems / caveats: "not much recent historical investigation" for Peru, Chile, Argentina (p. 49); deep and intermediate events incomplete for the whole historical period (p. 131); only the CERESIS catalogue, not its intensity database, has been updated since 1985 (p. 113, p. 185).

## Cards: Magnitude homogenization

### Castellaro et al. 2006: Regression problems for magnitudes
- Ref: Castellaro, S., Mulargia, F. & Kagan, Y.Y. (2006). Regression problems for magnitudes. Geophys. J. Int. 165, 913–930. doi:10.1111/j.1365-246X.2006.02955.x
- What it is: simulation study of OLS (SR), inverse OLS (ISR) and general orthogonal regression (GOR, Fuller 1987) for magnitude conversion, with an Italian application and the effect on G-R b-values.
- Use for us: A5 (choice of regression method, role of η, b-value bias from conversion).
- Coverage: Italy 1981–1996; 109 Ms–Mw, 121 ML–Mw, 204 mb–Mw pairs (p. 2 Table 2, p. 3).
- Methods: GOR slope eq. 9, intercept eq. 10, errors eqs 11–18 (p. 4); 10³ simulations of 50 (x, y) pairs with η = 25, 4, 1, 0.25, normal / exponential / lognormal data and errors (p. 5); non-parametric Kendall-tau (Sen 1968) slope test (p. 14–16).
- Numbers to keep: per-scale σ (events with ≥3 stations): Ms 0.28, ML 0.22, mb 0.37, Mw 0.18 (p. 2 Table 2); so η = 0.41 (Ms), 0.67 (ML), 0.24 (mb) (p. 11–12 Figs 10–12).
- GOR relations (p. 13 Table 3, y = α + βx): Mw = 1.445 (±0.175) + 0.765 (±0.035) Ms; Mw = 0.770 (±0.159) + 0.890 (±0.033) ML; Mw = −1.272 (±0.271) + 1.291 (±0.046) mb. Reduced-magnitude (M − 4.5) versions: Ms: GOR 0.426 + 0.765, SR 0.465 + 0.673, ISR Ms″ = −0.466 + 1.190 Mw″ (p. 11 Fig. 10); ML: GOR 0.283 + 0.890, SR 0.301 + 0.813, ISR −0.451 + 1.04 (p. 12 Fig. 11); mb: GOR 0.037 + 1.291, SR 0.137 + 0.971, ISR −0.014 + 0.737 (p. 12 Fig. 12).
- Kendall-tau slope 95% ranges: 0.574 < β(Mw–Ms) < 0.827, 0.770 < β(Mw–ML) < 0.937, 0.690 < β(Mw–mb) < 1.600; for mb with tied values averaged 1.01 < β < 1.29, which excludes the SR slope and includes GOR (p. 16 Table 5, eqs 32–34).
- Synthetic example (η = 0.67, b ≈ 1): for m1 = 6.0, SR gives 5.70, ISR 6.24, GOR 6.00 (p. 11 Fig. 8); with a 4.5 threshold SR 5.79, ISR 6.46, GOR 6.18 (p. 11–12 Fig. 9). OLS errors from +0.1 to −0.3 (p. 13); up to 0.3–0.4 (p. 1).
- b-value bias from SR conversion 20–40% (p. 17); b table: η = 0.25 true 1.141, after SR 1.399, after GOR 1.069 (p. 16 Table 4).
- Bias findings: SR fine only if η ≫ 1 with normal data; SR biased low "a few per cent" even at η = 25 for exponential data (p. 5); GOR ≥ SR in all cases; setting η = 1 when true η = 0.25 still beats SR, but η = 1 when true η = 25 gives wrong slopes (p. 5, p. 10 Fig. 7). GOR needs η to at least an order of magnitude (p. 5, p. 13). GOR lies between SR and 1/ISR slopes; with η < 1 (mb) GOR is close to ISR (p. 13). Chi-square regression (Stromeyer et al. 2004) gives β(Mw–Ms) = 0.769 vs GOR 0.765 (p. 13).
- Mw definition: Mw = 2/3 log10 M0 − C, M0 in N m; Hanks & Kanamori imply C = 6 + 1/30, paper uses C = 6.0 (p. 2 eq. 3).
- Chile specifics: none.
- Caveats: Italian data sets are small; magnitude errors shift a-value by σ² term (eq. 21, p. 14), so older, noisier periods look more active (p. 17).

### Lolli and Gasperini 2012: comparison among general orthogonal regression methods
- Ref: Lolli, B. & Gasperini, P. (2012). A comparison among general orthogonal regression methods applied to earthquake magnitude conversions. Geophys. J. Int. 190, 1135–1151. doi:10.1111/j.1365-246X.2012.05530.x
- What it is: analytic and numerical comparison of chi-square regression (CSQ, Stromeyer et al. 2004), GOR (Fuller 1987) and weighted total least squares (WLS, Krystek & Anton 2007) when only η is known.
- Use for us: A5 (CSQ = GOR = WLS for linear models with constant η; how to compute uncertainties).
- Coverage: three Mw–Mw test sets: GCMT vs NEIC 4193 events (global), GCMT vs RCMT 256 (Euro-Med), RCMT vs TDMT 42 (Italy) (p. 11). Authors stress these are tests, not calibrations (p. 11).
- Methods: CSQ slope eq. 14 identical to GOR eq. 23 (p. 3–4); WLS minimised numerically in slope angle (p. 6); covariance normalised by χ²/(N−2) (eqs 22, 56); bootstrap 1000 replicates (p. 13).
- Numbers to keep (GCMT = a·NEIC + b, p. 7 Table 1): η = 0.0001: a 1.056187, b −0.304120; η = 1: a 1.012353, b −0.045202; η = 10 000: a 0.969338, b 0.208876; OLS-DIR: a 0.969330, b 0.208924 (σa ≈ 0.0045–0.0049).
- GCMT vs RCMT (p. 9 Table 2): η = 1: a 0.936659, b 0.355168; OLS-DIR 0.913570, 0.475008. RCMT vs TDMT (p. 12 Table 3): η = 1: 0.958963, 0.398238.
- Coefficients of the three methods agree to the 5th–6th digit; GOR formal σ up to ~4.5–5% larger than CSQ and ~1% larger than WLS (p. 13, p. 15).
- Formal σ ≈ 5% below bootstrap for the large set (p. 13); for the 256 set 10% (η < 1) to 25% (η > 1) below; for the 42 set 10% below (η < 1) to 20–30% above (η ≥ 1) (p. 15).
- Recommendation: GOR simplest when only η known; CSQ/WLS better when each observation's uncertainty is known, e.g. merged catalogues with different η (p. 15).
- Chile specifics: none.
- Caveats: linear models only; results sensitive to η: slope moves from 1.056 to 0.969 across η range for the same data (p. 7).

### Lolli et al. 2014: Empirical conversion between teleseismic magnitudes (mb, Ms) and Mw
- Ref: Lolli, B., Gasperini, P. & Vannucci, G. (2014). Empirical conversion between teleseismic magnitudes (mb and Ms) and moment magnitude (Mw) at the Global, Euro-Mediterranean and Italian scale. Geophys. J. Int. 199, 805–828. doi:10.1093/gji/ggu264
- What it is: CSQ regressions of ISC-recomputed Ms and mb against merged moment-tensor Mw, with curvilinear models (exponential EXP; circularly connected bilinear CBL for Ms; reversed CBL-R for mb).
- Use for us: A5 (ISC Ms/mb → Mw relations with uncertainties; incompleteness bias of global Mw at low M; Ms and mb uncertainty model).
- Coverage: ISC Bulletin 1964–2010, effective from 1976 (GCMT start); only Ms/mb from ≥3 stations (p. 4). GBL: 19 475 Ms pairs (3.3 ≤ Ms ≤ 8.7) (p. 7), 30 326 mb pairs (3.6 ≤ mb ≤ 7.2) (p. 10). MED (25–60°N, 20°W–50°E): 1200 Ms, 1673 mb; ITA: 233 Ms, 468 mb (p. 8–11).
- Methods: reference Mw = GCMT + NEIC (+0.05 shift) globally, plus RCMT, ETHZ (−0.05), TDMT (+0.20) regionally; GCMT dropped if another source gives Mw < 5.4, NEIC dropped if > 7.0; inverse-variance mean when several (p. 5). Matching 10 s, 20 km (p. 5). Mw = 2/3 (log10 M0 − 9.1) (p. 2 eq. 1). EXP: Mw = exp(a + b x) + c (p. 3 eq. 2).
- Uncertainties: station σ from ISC SMAD (σ = 1.4826 e): Ms 0.33, mb 0.36 (2009–2010) and 0.41 from 1970–2008 station data; adopted 0.33 and 0.41 (p. 5). Regional term σG from 10° cell residuals: Ms 0.077, mb 0.207 (p. 7 Table 1); total σ = sqrt(σ̄²/n + σG²) (p. 7 eq. 8); resized σG GBL: Ms 0.14, mb 0.23 (p. 8 Table 2).
- EXP coefficients (p. 9 Table 3): Ms GBL a −0.109 ± 0.047, b 0.229 ± 0.005, c 2.586 ± 0.065, σw 0.1462; Ms MED 2.133 ± 0.343, 0.063 ± 0.017, −6.205 ± 3.013; mb GBL 0.741 ± 0.170, 0.210 ± 0.017, −0.785 ± 0.520, σw 0.3326; mb MED 0.719 ± 0.329, 0.212 ± 0.034, −0.737 ± 0.938.
- CBL Ms (p. 10 Table 4): GBL low slope 0.560 ± 0.005, b 2.582, Ms_low 4.24, Ms_up 7.17; MED 0.701 ± 0.008, 1.853, 5.25–7.01. CBL-R mb (p. 13 Table 5, Δ fixed 2): GBL high slope 1.609 ± 0.018, b −3.031, mb_low 3.57, mb_up 6.04; with Δ = 3 slope 2.071 ± 0.041.
- Final recommendation, global (p. 18 eqs 12–13): Mw = exp(2.133 + 0.063 Ms) − 6.205 for Ms ≤ 5.5; Mw = exp(−0.109 + 0.229 Ms) + 2.586 for Ms > 5.5; Mw = exp(0.741 + 0.210 mb) − 0.785. Global mb eq. usable at MED/ITA scale (p. 19).
- Proxy uncertainties 0.10–0.25 (Ms) and 0.20–0.45 (mb) (p. 12); average σ̄ Ms 0.16, mb 0.24 for GBL (p. 15 Table 6). If Ms and mb both exist: inverse-variance weighted mean (p. 13 eqs 10–11).
- Findings: GBL Ms curve overestimates Mw by up to 0.5 at Ms 3.5 because global MT catalogues lack Mw < 5.0–5.5 (Mw 5.0 ↔ Ms ≈ 4.3) (p. 9, p. 16); GEM/ISC-GEM OLS EXP (a −0.22, b 0.23, c 4.86) deviates 0.3–0.4 at large Ms, partly rounding of b (0.2349 vs 0.23) (p. 8); for mb, OLS curve of Storchak et al. follows the tail at low mb, CSQ tends to Mw = mb (p. 10). mb slope reaches ~2 only near mb 7.2 (EXP slopes 1.993 GBL, 2.005 MED at mb 7.2) (p. 12).
- Chile specifics: 10° residual map: teleseismic proxies overestimate observed Mw (negative residuals) in continental shields and subduction zones; underestimate at mid-ocean ridges (p. 6 Fig. 2).
- Caveats: report coefficients with extra digits, coefficients are correlated (p. 8); MED Ms "undersaturation" above Ms 7 based on 6 events (p. 17); ITA box in text has lat/lon swapped (p. 4).

### Lolli et al. 2023: Homogenization of magnitudes of the ISC Bulletin
- Ref: Lolli, B., Randazzo, D., Vannucci, G., Biondini, E. & Gasperini, P. (2023). Homogenization of magnitudes of the ISC Bulletin. Geophys. J. Int. 234, 1771–1785. doi:10.1093/gji/ggad164
- What it is: update of Lolli et al. (2014) with ISC data to 2020 plus agency-specific Ms/mb → Mw relations (NEIC, IDC, BJI, MOS) for the unreviewed ISC period; near-real-time Mw catalogue 1964–2022.
- Use for us: A5 (current ISC relations; agency differences; NEIC Ms_20; IDC mb bias), A2/Q2 (ISC Bulletin completeness changes).
- Coverage: reviewed ISC 1964–2020 (downloaded Dec 2022); agencies 2005–2022; GBL and MED. No South American agency was calibrated (only NEIC, IDC, BJI, MOS had enough data; BJI/MOS sole providers for < 1% of events) (p. 3).
- Methods: reference MWREF: GCMT (shift 0, σ 0.07–0.10, discard if other Mw < 5.4), NEIC (+0.05, discard > 7.0), RCMT, ETHZ (−0.05), TDMT (+0.20), GFZ (+0.05); σ 0.10 before 1995, 0.07 after (p. 2–3 Table 1). Matching 10 s / 20 km; ≥3 stations; Ms only for depth < 50 km (p. 3–4). CSQ with σ = sqrt(σ̄²/n + σG²), σ̄ Ms 0.33, mb 0.41 (p. 4 eqs 4–5).
- σG (GBL Ms / mb): ISC 1964–2020 0.14 / 0.23; NEIC 0.13 / 0.20; IDC 0.09 / 0.24; BJI 0.21 / 0.21; MOS 0.17 / 0.20 (p. 4 Table 2).
- ISC EXP, GBL 1964–2020 (p. 6 Table 3): Ms (N 34 188) a −0.137 ± 0.032, b 0.229 ± 0.003, c 2.673 ± 0.041, σr 0.138; mb (N 48 498) a 0.082 ± 0.098, b 0.266 ± 0.011, c 1.039 ± 0.184, σr 0.293. MED 1964–2020: Ms (2842) 3.052 ± 0.399, 0.029 ± 0.010, −19.05 ± 8.496; mb (3871) 1.111 ± 0.198, 0.165 ± 0.018, −1.852 ± 0.742. Split 1964–2010 / 2011–2020 also listed; mb 2011–2020: 1.512, 0.128, −3.434.
- ISC CBL/CBL-R (p. 6 Table 4): Ms GBL slope 0.531 ± 0.003, b 2.726, Δ 1.641, MI 5.81; Ms MED 0.682 ± 0.005, 1.960, MI 6.17; mb GBL 1.390 ± 0.011, −1.942 ± 0.063, MI 4.98; mb MED 1.650 ± 0.068, −3.578, MI 5.50.
- Agency EXP, GBL (p. 8 Table 5): NEIC Ms_20 (2013–2022, N 3383) 1.108 ± 0.180, 0.124 ± 0.013, −0.246 ± 0.653; NEIC mb (2005–2022, N 33 773) 0.948 ± 0.117, 0.179 ± 0.011, −1.240 ± 0.402, σr 0.262; IDC Ms (25 995) 1.088, 0.124, 0.0128; IDC mb (34 584) −0.734 ± 0.166, 0.405 ± 0.023, 2.136 ± 0.184; BJI mb −1.542, 0.500, 2.612; MOS mb 1.080, 0.174, −2.177. CBL/CBL-R (p. 8 Table 6): NEIC Ms slope 0.724, MI 6.41; NEIC mb 1.508 ± 0.018, −2.780 ± 0.106, MI 5.47.
- Findings: ISC mb ≈ Mw for mb < 4–4.5, saturates for mb > 5–5.5 (p. 2); NEIC mb less saturated than ISC at high M and closer to Mw = mb at low M (p. 5); IDC mb exceeds ISC mb by 0.5–0.7 (narrow 1.5 s filter on first 5 s of P) (p. 5–6, p. 13); IDC Ms departs from Mw = Ms only below Ms ≈ 7 (p. 5); BJI Ms uses constant 3.5 instead of 3.3 (p. 6); MOS mb 0.2–0.3 below ISC (p. 7). NEIC Ms labelled Ms_20 from 2013 (p. 3). GBL Ms relation biased below Ms 5.5 by missing Mw < 5.0 and GCMT overestimation < 5.4, so MED coefficients used for ISC and IDC Ms < 5.5 and for IDC mb (p. 5, p. 8, p. 13). Ms transition ≈ 6.1–6.2 (p. 13).
- Proxy error: σ²Mw = exp(2a + 2bx)(σa² + x²σb² + b²σx² + 2x cov(a,b)) + 2exp(a + bx)(cov(a,c) + x cov(b,c)) + σc² (p. 8 eq. 6); ISC mb 5.5 with σmb 0.10 → σMw 0.13, with 0.40 → 0.50 (p. 8).
- Catalogue: ~645 000 events 1964–2020 + ~68 000 2021–2022 (p. 9); Mc 4.8, b 1.055 ± 0.003 (1964–2022); jump in rates ~1995; Mc 4.3, b 1.042 ± 0.002 (1995–2022) (p. 10); 2021–2022 b 1.128 ± 0.006, Mc 4.2, mostly IDC proxies (p. 10, p. 12 Table 7).
- Chile specifics: none.
- Caveats: CBL-R Δ not resolvable (fixed 2); several MED/agency fits unstable (e.g. MOS mb CBL-R σ 42.79) (p. 6, p. 8); reviewer questioned omission of equation error (p. 4).

### Weatherill et al. 2016: Exploring earthquake databases for magnitude-homogeneous catalogues
- Ref: Weatherill, G.A., Pagani, M. & Garcia, J. (2016). Exploring earthquake databases for the creation of magnitude-homogeneous catalogues: tools for application on a regional and global scale. Geophys. J. Int. 206, 1652–1676. doi:10.1093/gji/ggw232
- What it is: GEM open-source toolkit (duplicate finding, agency/magnitude queries, ODR regression, hierarchical selection/conversion) and an extended global Mw catalogue (562 840 events).
- Use for us: A3 (duplicate windows, any/all criteria), A4 (origin and magnitude hierarchy), A5 (global agency-specific conversions, error propagation).
- Coverage: 1900–2013; sources: ISC-GEM v3.0 (24 375 events), ISC Reviewed (535 066, M ≥ 3.0), NEIC (330 942, 10 282 with Mw), EHB (137 146), GCMT 1976–2013 (40 514), Pacheco & Sykes (1992), NIED (p. 13). No South American agency (GUC, SAN, CSN) is analysed; regional example is Sub-Saharan Africa (p. 8–12).
- Methods: ODR (Boggs et al. 1987, ODRPACK) with unit weights on both variables (p. 6–7); model σ a posteriori (p. 7 eq. 7); propagated σ_M* = sqrt(σ² + (∂f/∂M)² σM²) (p. 4 eq. 1); GCMT Mw taken without error (p. 14). Duplicates: 60 s, ~110 km (p. 21).
- Mw–Mw (p. 14): GCMT = 0.248 + 0.964 NIED (1906 events, 4.3–9.1, σ 0.11) eq. 8; GCMT = 1.021 (±0.003) NEIC − 0.091 (±0.017), σ 0.105 (5789 events, 4.5–9.0) eq. 9; robust for shallow/deep split.
- ISC Ms (p. 15, 17 343 pairs): Mw = 0.616 (±0.002) Ms + 2.369 (±0.010) for Ms ≤ 6.0 (σ 0.147); 0.994 (±0.009) Ms + 0.100 for Ms > 6.0 (σ 0.174) (eq. 13). Break 6.47: 0.636 Ms + 2.276 (σ 0.151) / 1.147 Ms − 1.031 (σ 0.194) (eq. 14). Di Giacomo et al. (2015) for comparison: EXP Mw = exp(−0.222 + 0.233 Ms) + 2.863; GOR bilinear 0.67 Ms + 2.13 (≤ 6.47), 1.10 Ms − 0.67 (> 6.47) (p. 14 eqs 11–12). DG15 EXP overestimates Mw for Ms < 4.0 (p. 15).
- NEIC Ms (p. 16): ISC Ms = 1.007 NEIC Ms − 0.050 (σ 0.158, 14 241); ISC Ms = 0.985 NEIC Msz + 0.082 (12 851); Mw = 0.723 (±0.004) Ms_NEIC + 1.798 (≤ 6.47, σ 0.159), 1.005 Ms_NEIC − 0.026 (> 6.47, σ 0.187) (eq. 19); Msz: 0.707 Msz + 1.933 (σ 0.179), 0.950 Msz + 0.359 (σ 0.204) (eq. 20).
- mb (p. 17–18): DG15 EXP Mw = exp(−4.664 + 0.859 mb) + 4.555 and GOR linear Mw = 1.38 mb − 1.79 (eqs 21–22); new ISC (22 105 pairs) EXP exp(−6.373 + 1.182 mb) + 4.577 (σ 0.319) and linear Mw = 1.084 (±0.005) mb_ISC − 0.142 (±0.028) (σ 0.317) (eqs 23–24); mb_ISC = 1.044 mb_NEIC − 0.331 (σ 0.224, 270 934 events) (eq. 25); Mw = 1.159 (±0.005) mb_NEIC − 0.659 (±0.026) (σ 0.283, 23 207 pairs) (eq. 27). Linear preferred over EXP for mb; NEIC mb preferred over ISC mb because of lower σ (p. 18, p. 21).
- Hierarchy (p. 20 Table 1): origin ISC-GEM > EHB > ISC > NEIC > GCMT > PS; magnitude ISC-GEM Mw > GCMT Mw > NEIC Mw > NIED Mw > ISC Ms > NEIC Ms > NEIC Msz > NEIC mb > ISC mb > PS Ms (PS Ms taken as Mw for 7–8, σ 0.2, p. 18).
- Completeness (global, p. 22 Table 2): Mw ≥ 7.5 from 1900, 7.0 from 1920, 6.75 from 1925, 6.0 from 1950, 5.5 from 1960, 5.0 from 1964, 4.5 from 1978, 3.5 from 2000; rate jumps 1970/71, 1977/78, 1992 unexplained (p. 22).
- Chile specifics: none.
- Caveats: depth dependence of mb–Ms expected; separate deep events where data allow (p. 4); "strawman" catalogue, not a local calibration (p. 12); text says "eqs (24) and (19)" for Ms preference although Table 1 uses eq. 13 for ISC Ms (p. 20); ISC Ms pair period printed "1900 to 1913" (p. 15).

### Scordilis 2006: Empirical global relations converting Ms and mb to moment magnitude
- Ref: Scordilis, E.M. (2006). Empirical global relations converting MS and mb to moment magnitude. J. Seismol. 10, 225–236. doi:10.1007/s10950-006-9012-4
- What it is: global OLS relations ISC/NEIC Ms and mb vs HRVD (GCMT) Mw; widely used (Poulos 2019 alternative set).
- Use for us: A5 (reference OLS relations; ISC–NEIC equivalence).
- Coverage: 20 407 events with Mw 3.1–8.4, 1976-01-01 to 2003-05-31 (20 196 HRVD + 212 USGS) (p. 1, p. 3); mb: 284 157 ISC and 229 375 NEIC values 1965–2003; Ms: 56 184 ISC (1978–2003) and 32 464 NEIC (1968–2003) (p. 4).
- Methods: least squares (OLS, Mw dependent) (p. 4); Mw = 2/3 log M0 − 10.7 (dyn cm) (p. 2 eq. 9); Prague Ms (p. 2 eq. 5), Ms depth ≤ 60 km by definition (p. 2).
- Numbers to keep: Mw_HRVD = 1.00 (±0.01) Mw_USGS + 0.04 (±0.09), 5.0 ≤ Mw ≤ 8.2, σ 0.11, n 3756 (p. 3 eq. 10).
- Ms_NEIC = 0.99 (±0.003) Ms_ISC + 0.05 (±0.02), h < 70 km, σ 0.16, n 25 960 (p. 4 eq. 11); deep 0.98 Ms + 0.07, n 65 (eq. 12); all depths σ 0.16, n 26 025 (p. 5 eq. 13).
- Mw = 0.67 (±0.005) Ms + 2.07 (±0.03), 3.0 ≤ Ms ≤ 6.1, σ 0.17, n 23 921 (p. 5 eq. 14); Mw = 0.99 (±0.02) Ms + 0.08 (±0.13), 6.2 ≤ Ms ≤ 8.2, σ 0.20, n 2382 (eq. 15); shallow h < 70 km; break at Ms 6.2 (p. 6 Fig. 4).
- mb_ISC = 1.02 (±0.003) mb_NEIC − 0.18 (±0.01), 2.5 ≤ mb_NEIC ≤ 7.3, σ 0.20, n 215 163 (p. 7 eq. 21); Mw = 0.85 (±0.04) mb + 1.03 (±0.23), 3.5 ≤ mb ≤ 6.2, σ 0.29, n 39 784 (ISC and NEIC mb pooled) (p. 7 eq. 22); data poor below mb 4.5; saturation above mb 6.2 (Mw > 6.3) (p. 7–9).
- Older relations quoted: mB = 1.5 mb − 2.2 (Abe 1981), mb_ISC = 0.46 Ms + 2.74 (Karnik 1973) (p. 2); Karnik MSK relations eqs 16–20 (p. 6).
- Chile specifics: none.
- Caveats: OLS only (Weatherill 2016 p. 14 notes this); no global ML relation possible (WA magnification issues) (p. 8–10); relations for large-scale studies only, regional relations needed (p. 10).

### Gasperini et al. 2013: Empirical calibration of local magnitude data sets versus Mw in Italy
- Ref: Gasperini, P., Lolli, B. & Vannucci, G. (2013). Empirical Calibration of Local Magnitude Data Sets Versus Moment Magnitude in Italy. Bull. Seismol. Soc. Am. 103(4), 2227–2246. doi:10.1785/0120120356
- What it is: CSQ calibration of 10 Italian ML / MD / Ma data sets (1981–2010) against merged MT Mw, with a trial-and-error method to set magnitude uncertainties; homogenized Mw catalogue.
- Use for us: A5 (template for calibrating a national network's ML, Md against Mw; offset-only conversions; uncertainty resizing; merging several proxies).
- Coverage: Italy 1981–2010; Mw 3.0–6.9 reference (p. 3); final catalogue 157 086 events, 120 482 with Mw (p. 11).
- Methods: IMW: GCMT, NEIC (+0.05), RCMT, ETHZ (−0.05), TDMT (+0.20), discard rules as Lolli 2014 (p. 5–6); Mw σ 0.07 (0.13 TDMT), 0.10 before 1997/1995 (p. 6–7, Table 2). Matching 10 s / 15 km for regressions (p. 7), 1 min / 100 km for catalogue merging (p. 11). Uncertainty resizing until σ_a priori = sqrt(Σ(b²σx² + σy²)/N) matches σ_empirical (p. 6 eqs 6–7).
- Numbers to keep (p. 7 Table 3): CSTI ML shift 0.15 ± 0.05; CSTI MD Mw = 1.129 MD − 0.303; CSTI Ma 1.116 Ma − 0.232; CSI ML shift 0.26 ± 0.02; CSI MD shift 0.38 ± 0.08; BSI ML shift 0.08 ± 0.03; BSI MD 1.456 MD − 1.472; ISIDE ML 1.066 ML − 0.164; ISIDE MD 1.718 MD − 1.905 (combined via ML).
- Resized magnitude σ 0.15–0.29 (p. 6 Table 2); Mw proxy σ: ML ~0.16–0.24; MD up to 0.45 (ISIDE) and 0.39–0.55 (BSI) (p. 7–10).
- MD formulas: Lee et al. (1972) a −0.87, b 2, c 0.00175; Console et al. (1989) c 0.082; Gasperini (2002) MD = 2.515 log Ts − 2.122; Castello et al. (2007) MD = 2.49 log Ts − 2.31 (p. 4–5 eqs 2–5).
- Findings: WA-based ML scale 1:1 with Mw but underestimate it by 0.1–0.2 (p. 1, p. 14); OLS literature slopes 0.6–0.8 (p. 2 Table 1); MD generally not 1:1 and underestimated; Console MD overestimates small and underestimates large events (p. 14); ISIDE ML slope 1.07 ± 0.03 from Hutton & Boore −log A0 (p. 8); validity ranges were extended down to M ~1.0 without constraint (p. 10). Weighted mean of ML, MD, Ma proxies preferred (p. 10–11).
- Chile specifics: none.
- Caveats: conclusion lists CSI ML shift 0.23 (p. 14) while Table 3 gives 0.26 and text 0.24 ± 0.02 (p. 7, p. 9).

### Hanks and Kanamori 1979: A moment magnitude scale
- Ref: Hanks, T.C. & Kanamori, H. (1979). A Moment Magnitude Scale. J. Geophys. Res. 84(B5), 2348–2350. No DOI on p. 1 (paper number 9B0059).
- What it is: definition of the moment magnitude M from the coincidence of log M0–ML, –Ms and –Mw relations.
- Use for us: A5 (definition of the target scale; constant convention).
- Coverage: southern California 1918–1973 and large California events 1857–1906 (p. 2 Tables 1–2).
- Methods: Es = (Δσ/2μ) M0 ≈ M0/(2 × 10⁴) (eqs 1–2) with log Es = 1.5 Ms + 11.8 (eq. 3) → log M0 = 1.5 Mw + 16.1 (eq. 4) (p. 1).
- Numbers to keep (verified on PDF page images p. 1–2): M = (2/3) log M0 − 10.7, M0 in dyn cm (p. 2 eq. 7, abstract p. 1); valid for 3 ≲ ML ≲ 7, 5 ≲ Ms ≲ 7½, Mw ≳ 7½ (p. 1–2). Supporting: log M0 = 1.5 Ms + (16.1 ± 0.1) for 5 ≲ Ms ≲ 7½ (Purcaru & Berckhemer) (p. 1 eq. 5); log M0 = 1.5 ML + 16.0 for 3 ≲ ML ≲ 7 (Thatcher & Hanks) (p. 2 eq. 6).
- In N m: M = (2/3) log M0 − 6.033 (derived; Castellaro 2006 p. 2 gives C = 6 + 1/30), vs IASPEI (2/3)(log M0 − 9.1) = (2/3) log M0 − 6.067 (Lolli 2014 p. 2); difference 0.033.
- Notes: ML, Ms and mb saturate (mb near 7, Ms near 8.3, ML near 7) (p. 1); coda-duration magnitudes tied to ML should follow eq. 6 but this needs verification with M0–duration data (p. 2).
- Chile specifics: none.
- Caveats: old OCR text is garbled; equations above were read from the PDF page images.

### Poulos et al. 2019: Updated recurrence model for Chilean subduction seismicity
- Ref: Poulos, A., Monsalve, M., Zamora, N. & de la Llera, J.C. (2019). An Updated Recurrence Model for Chilean Subduction Seismicity and Statistical Validation of Its Poisson Nature. Bull. Seismol. Soc. Am. 109(1), 66–74. doi:10.1785/0120170160
- What it is: Mw-based G-R model for 3 interface and 4 intraslab zones of Chile with declustering and Poisson tests; includes Chilean Ms, ML, mb → Mw relations.
- Use for us: A5 (Chile-fitted relations, sensitivity of rates to conversion choice), A7 (interface/intraslab depth split), comparison for rates.
- Coverage: ISC Bulletin and USGS ComCat 1900–present (accessed Sept 2018), ComCat preferred when in both (p. 2, p. 8); Mw ≥ 5 complete since 1974 (Stepp 1972) (p. 2); non-instrumental catalogues discarded (p. 2).
- Methods: Mw = c + d M, "orthogonal least-squares" (Castellaro & Bormann 2007), η not stated (p. 2). Declustering Gardner–Knopoff with Knopoff et al. (1982) windows: d ≤ Cdist·3^(m−7), |Δt| ≤ Ctime·3^(m−7), Cdist 100 km, Ctime 130 days (p. 2–3 eqs 1–2). G-R by Weichert (1980) (p. 4).
- Numbers to keep (p. 2 Table 1, checked on PDF page): Ms: c 0.585, d 0.935 (sc 0.073, sd 0.013, n 1115); ML: c 0.676, d 0.899 (0.200, 0.037, n 891); mb: c −1.005, d 1.227 (0.092, 0.017, n 1716).
- Zones: interface trench to 60 km depth; intraslab 60 to ~160 km; geometry from Slab1.0 (Hayes et al. 2012); N–S divisions as Martin (1990) and Leyton et al. (2009) (p. 3).
- G-R (p. 4 Table 2): interface zones 1–3: 1042 events, a 5.55, b 0.86; intraslab 4–7: 1429 events, a 6.48, b 1.02.
- Sensitivity (p. 5 Table 3, Knopoff declustering): Scordilis/Núñez relations: a 8.03, b 1.23, 4073 events Mw ≥ 5; this study: a 6.35, b 0.94, 2471 events. Difference driven by events without Mw and mb 4.67–4.90 (minimum mb reaching Mw 5 with Scordilis vs this study) (p. 5). Núñez (2014) used for ML in the alternative set (p. 5).
- Chile specifics: zone 5 Poisson-inconsistent because aftershocks of 2010 Mw 8.8 Maule were not removed (p. 6); Leyton et al. (2009) rates one order higher (p. 4, p. 8).
- Caveats: agency of Ms, ML, mb and source of Mw in the pairs not stated; single linear relation for mb and Ms over the whole range (no saturation or slope break); crustal events excluded (p. 3, p. 8).

### Leyton et al. 2009: Preliminary re-evaluation of PSHA in Chile, Arica to Taitao
- Ref: Leyton, F., Ruiz, S. & Sepúlveda, S.A. (2009). Preliminary re-evaluation of probabilistic seismic hazard assessment in Chile: from Arica to Taitao Peninsula. Adv. Geosci. 22, 147–153. No DOI on p. 1 (www.adv-geosci.net/22/147/2009/).
- What it is: Chile PSHA (18–45°S) for interplate thrust and intermediate-depth intraplate sources, catalogue homogenized to Ms.
- Use for us: A5 (Chilean relations between Ms and mb, ML, Mw; note the target scale is Ms), A2 (catalogues used), comparison with Poulos 2019.
- Coverage: SISRA (to 1982, updated to 2005), NEIC 1973–Dec 2008, ISC 1906–Jan 2007 (p. 2); 18–45°S; zones Z1–Z7 after Martin (1990) updated with Gudmundsson & Sambridge (1998) (p. 2).
- Methods: least squares (Menke 1989) with Ms as dependent variable, events having Ms and another magnitude (p. 2); declustering Reasenberg (1985); completeness Stepp; G-R by Weichert (1980), Mc by maximum curvature (p. 2–3).
- Numbers to keep (p. 3 Table 1, checked on PDF page; Ms = α·mag + β ± σ): mb: α 1.322, β −1.949, σ 0.1914, r 0.7914, n 730; ML: 1.137, −0.808, 0.3625, 0.8919, 268; Mw: 1.127, −1.197, 0.0559, 0.9242, 258.
- Mmax: Ms 8.5 interplate, Ms 8.0 intraplate (p. 3). G-R (Log N = a − b Ms) (p. 5 Table 2): Z1 4.89/0.63, Z2 5.65/0.75, Z3 4.62/0.70, Z4 6.43/1.08, Z5 5.20/0.68, Z6 5.37/0.82, Z7 5.94/0.94.
- Chile specifics: interplate depths 15–50 km, intraplate > 50 km (p. 1); Z5 (northern intraslab) highly productive, PGA > 0.8 g at 18–25°S (p. 4); south (~36–46°S) lowest PGA due to long return periods in Valdivia 1960 rupture area (p. 4).
- Caveats: agency of each magnitude type not stated; σ column called "estimated error" (meaning unclear; 0.0559 for Mw looks small); OLS with error-affected predictor; crustal sources excluded (p. 5).

## Cards: Slab and double seismic zone

### Comte et al. 1999: A double-layered seismic zone in Arica, northern Chile
- Ref: Comte, D., Dorbath, L., Pardo, M., Monfret, T., Haessler, H., Rivera, L., Frogneux, M., Glass, B., Meneses, C. (1999). A double-layered seismic zone in Arica, northern Chile. Geophys. Res. Lett., 26(13), 1965–1968. No DOI printed on p. 1 (paper number 1999GL900447; DOI 10.1029/1999GL900447 from the download banner, p. 2).
- What it is: first DSZ in the Nazca slab defined by a real separation of hypocentres (not by focal mechanisms), from local microseismicity at the Arica elbow.
- Use for us: A7 (where a DSZ exists; depth range and plane separation at ~18–19.5°S).
- Coverage: Arica region, map ~18–19.4°S, 72–69°W (Fig. 1, p. 2); permanent 9-station telemetric network since Dec 1994 (~3900 events) plus temporary network of 18 vertical + 10 three-component digital + 6 analog stations, Jun–Aug 1996 (~1000 events) (p. 1, verified on image). No magnitudes given.
- Methods: HYPOINVERSE with trial depths 0–250 km every 10 km (p. 1); joint 3D velocity inversion and relocation of 4480 events, 3083 stable and well constrained (p. 2, verified on image); 1D vs 3D epicentre change < 2–3 km, depth change < 5 km (p. 2, verified). Single-event first-motion focal mechanisms. Three profiles P1–P3 along N77°E, half-width 20 km (p. 2).
- Numbers to keep (all verified on image): below 100 km a single zone ~10 km thick, nearly planar to 150 km, dipping ~30° E; second parallel zone 20–25 km beneath (perpendicular distance), fewer events, thickness ~10 km (p. 2, abstract p. 1). DSZ "between about 100 to 150 km" depth (p. 3). Interplate contact average dip ~20° at 25–50 km (p. 2). Slab age 84 My, convergence ~8.3 cm/yr, N77°E (p. 3).
- Chile specifics: clear two-layer separation only around the Arica elbow (abstract p. 1); Comte & Suárez (1994) DSZ to the south was based on focal mechanisms only (p. 1); teleseismic studies found no clear DSZ (p. 2–3).
- Focal mechanisms: wide variability in both layers, opposite polarities for neighbouring events at the same depth; compressional and tensional events at almost the same depth (pp. 2–3).
- Caveats: DSZ seen mainly with microseismicity, so it depends on the magnitude threshold (p. 3); mechanism variability may not represent the regional stress (p. 3); poor coverage oceanward of the network (p. 2).

### Rietbrock and Waldhauser 2004: A narrowly spaced double-seismic zone in the subducting Nazca plate
- Ref: Rietbrock, A., Waldhauser, F. (2004). A narrowly spaced double-seismic zone in the subducting Nazca plate. Geophys. Res. Lett., 31, L10608. doi:10.1029/2004GL019610 (p. 1).
- What it is: double-difference relocation of ANCORP'96 intermediate-depth events near 22°S showing two bands only ~9 km apart.
- Use for us: A7 (DSZ geometry at 22°S; a DSZ narrower than any catalogue depth error).
- Coverage: ANCORP 1996 array, 20–23°S, Dec 1996–Feb 1997, 1050 local events ML 1.0–4.7; selected box 21.5–22.2°S with 240 events ML 1.3–4.7 (p. 1, p. 2).
- Methods: manual P and S picks, 3D tomography locations (Rietbrock & Haberland 2001), then hypoDD with catalogue and cross-correlation differential times (events < 15 km apart) (pp. 1–2); 3D vs 1D model difference < 1 km on average (p. 2); relative errors ~0.3 km (bootstrap and LSQ) (p. 3); absolute location uncertainty 3–5 km (p. 3).
- Numbers to keep: 238 of 240 relocated (p. 3); two bands separated by 8–10 km (p. 3), "about 9 km" (p. 1); depth range 80–130 km (p. 1); ~5 km wide low-activity zone between bands (p. 3); the 3D-located seismicity is a 16 km wide band without resolved internal structure before DD (p. 1); top of upper band matches the Nazca reflector imaged at 80–85 km to the west (p. 3); oceanic crust ~8 km thick (p. 3); sub-vertical structures connecting the bands at 105–115 km (p. 4).
- Interpretation: upper band at top of oceanic crust, lower band in uppermost oceanic mantle; cannot rule out continental mantle / lower oceanic crust, but rules out both bands in the crust (p. 3).
- Focal mechanisms: first-motion solutions for events with M > 2.5 (text says Mw, Fig. 3 caption ML) predominantly extensional in both bands; upper band P axes normal to slab, T axes in many slab-parallel directions; lower band T axes predominantly down-dip (p. 3, p. 2).
- Magnitudes: more and smaller events in the crust, fewer and larger in the mantle; higher share of ML ≥ 2.5 in lower band (p. 3).
- Caveats: three-month data period may not give a representative magnitude distribution (p. 3); Comte & Suárez (1994) DSZ near 24°S (separation > 20 km, from mechanisms) not supported by later data (Rudloff 1998) (p. 1).

### Dorbath et al. 2008: Double seismic zone of the Nazca plate in northern Chile
- Ref: Dorbath, C., Gerbault, M., Carlier, G., Guiraud, M. (2008). Double seismic zone of the Nazca plate in northern Chile: High-resolution velocity structure, petrological implications, and thermomechanical modeling. Geochem. Geophys. Geosyst., 9, Q07006. doi:10.1029/2008GC002020 (p. 1).
- What it is: tomoDD double-difference tomography of the Arica 1996 data set (same data as Comte et al. 1999) plus petrological and thermomechanical modelling of the DSZ.
- Use for us: A7 (DSZ depth range and separation at Arica, best-located events).
- Coverage: temporary network Jun–Aug 1996, between the Peruvian border and 19°20'S, 24 vertical + 10 three-component stations plus 9 permanent (43 stations); permanent-network data Jan 1996–Dec 1997 (p. 3). Grid origin 18°S, 69°W, rotated N77°E, nodes every 10 km to 160 km (p. 3). No magnitudes given.
- Methods: 2052 events kept with > 10 readings incl. 2 S, nearest station < depth, RMS < 0.25 s, gap < 300°, conditioning < 100 (p. 3); ~36,000 absolute times (55% P), 171,000 differential times, max inter-event distance 10 km (p. 3); tomoDD LSQR, condition number 40–50 (p. 3).
- Numbers to keep: DSZ at 80–140 km, the two planes 20 km apart (p. 1, p. 5, p. 22); both planes 5–10 km thick (p. 5); upper plane 80–130 km (p. 7) and lower plane characterised down to 130 km (p. 8); Table 1 (p. 6): upper plane Vp 7.7, Vs 4.6, Vp/Vs 1.67; in between 8.5 / 4.5 / 1.89; lower plane 7.4 / 4.7 / 1.57. Slab age 50 Ma, rate 84 mm/a (p. 2).
- Focal mechanisms: 45 solutions, 41 in upper plane, 4 in lower plane; strong variability as in Comte et al. (1999); lower plane has both tensional and compressional mechanisms; no reliable mechanism between the planes (p. 7).
- Chile specifics (review, p. 2–3): Comte & Suárez (1994), 20–24°S, 80–150 km, two families of opposite mechanisms ~15 km apart; PISCO'94 gave no DSZ evidence (Graeber & Asch 1999); Comte et al. (1999) 18.5–19.5°S, > 100 km, 20–25 km; Rietbrock & Waldhauser (2004) 22°S, 9 km, 80–130 km.
- Model results: DSZ contours an inner-slab compressional zone around the 400°C (±50°C) isotherm (p. 1); lower plane predicted on the neutral plane ~20 km below slab top (p. 18), model distance closer to 15 km (p. 19).
- Caveats: velocity values cannot be matched by a single mineral assemblage (p. 8); thermomechanical model is short (2 Ma) and simplified (p. 19).

### Marot et al. 2013: A double seismic zone in the subducting Juan Fernandez Ridge (32°S)
- Ref: Marot, M., Monfret, T., Pardo, M., Ranalli, G., Nolet, G. (2013). A double seismic zone in the subducting Juan Fernandez Ridge of the Nazca Plate (32°S), central Chile. J. Geophys. Res. Solid Earth, 118, 3462–3475. doi:10.1002/jgrb.50240 (p. 1).
- What it is: first DSZ reported in central Chile, above the Pampean flat slab along the JFR track, with focal mechanisms and stress tensors per plane and depth.
- Use for us: A7 (DSZ in 29.5–32.5°S, shallow onset at 50 km, merging at 100–120 km; where it ends to the south).
- Coverage: OVA99 (Ovalle, 30–32°S, 72–70°W, mid-Nov 1999 to mid-Jan 2000, 37 short-period stations, 0.5 < Ml < 5.5) (p. 4); CHARSME (mid-Nov 2002 to Mar 2003, 29 broadband) plus 15 permanent U. Chile stations (p. 4). Number of DSZ events not stated.
- Methods: manual P and S picks; 17-layer 1D VELEST model, Vp/Vs 1.76 (p. 4); Ml calibrated to stay close to ISC Mw (p. 4); selection: errors ≤ 10 km horizontal and ≤ 5 km depth (Fig. 1b), plus ≥ 10 phases with ≥ 2 S and RMS ≤ 0.6 s (Fig. 3) (p. 4); hypoDD tried, no significant change (p. 4). FOCMEC first-motion mechanisms with ≥ 9 polarities (p. 4).
- Numbers to keep: DSZ clear at 30.5–32.5°S, possibly 29.5–30.5°S (poor coverage), questionable at ~33°S (p. 4); total ~300 km along strike (p. 8, p. 12). LP begins at 50 km below the interface; some events below the trench axis at ~25–40 km (p. 4); LP merges with UP at ~100–120 km where the slab turns flat (p. 4, p. 12); maximum interplane distance 20–25 km (p. 4) (Table 1, p. 3, lists width 30 km for this study). Mean Ml UP 2.3 (±0.9), LP 2.4 (±0.6) (p. 4). Convergence 6.7 ± 0.2 cm/a N78°, slab age 33–38 Ma at trench (p. 3).
- Focal mechanisms: 1065 for the region; 13 UP and 23 LP reliable on the 31.2–32.2°S profile (p. 4, Table 2 p. 8, Ml 1.0–3.2); UP 70% normal / 30% reverse, LP 80% normal / ~20% reverse (p. 4); no partition by plane, partition by depth: compression above 60–70 km, extension parallel to convergence below (pp. 4–7, p. 12). "Type III" DSZ (p. 2, p. 12).
- Caveats: hypocentre uncertainty 15 km in Fig. 1b profile (p. 2); DSZ not detectable in the EHB catalogue (p. 10); few mechanisms per group for stress tensors (p. 7); abstract says the LP "merges with the lower plane" (should read upper plane) (p. 1).

### Sippl et al. 2018: Seismicity structure of the northern Chile forearc from >100,000 double-difference relocated hypocenters
- Ref: Sippl, C., Schurr, B., Asch, G., Kummerow, J. (2018). Seismicity structure of the northern Chile forearc from >100,000 double-difference relocated hypocenters. J. Geophys. Res. Solid Earth, 123, 4063–4087. https://doi.org/10.1002/2017JB015384 (p. 1).
- What it is: automatic IPOC catalogue 2007–2014 with 101,601 DD-relocated events; maps interface, upper plane, lower plane, a 25 km thick intermediate-depth cluster and upper-plate seismicity.
- Use for us: A7 (main source for DSZ geometry 19–24°S and for classification thresholds by distance to slab top); A2/A3 (a local catalogue for 2007–2014, ML down to < 2).
- Coverage: IPOC plus CSN, GEOFON and selected temporary stations, 2007–2014, ~19–24°S (p. 3); classified area 19–23.6°S, 70.8–68°W (Table 1, p. 8); ML (Hutton & Boore 1987) (pp. 3–4); Mc 2.7–2.9, majority M 2–3 (p. 5); abstract Mc ~2.8 (p. 1).
- Methods: STA/LTA detection, automatic P and S pickers, ≥ 8 picks (p. 3); 1,200,404 P and 688,904 S picks, mean uncertainty 0.11 s and 0.37 s (p. 4); VELEST (Graeber & Asch 1999 1D), simul2000 2D model from 3,886 events 20.5–23°S (p. 4); hypoDD in 11 overlapping E-W swaths with catalogue and cross-correlation times; only events in clusters > 100 kept (p. 5). NonLinLoc absolute errors < 5 km inside the network, larger offshore and east/west (p. 5); relative errors 1–2 km (p. 5).
- Numbers to keep: own slab-top model: 4th-order polynomial fit to 2,954 hand-picked points (p. 6). Classes (Table 1, p. 8): P1 interface ±3 km of slab top (±10 km W of 70.8°W); P2 upper plane 3–16 km below; P3 lower plane > 16 km below; UP > 3 km above; ID cluster ±30 km of slab top east of 69.1°W (S of 21°S) or 69.6°W (N of 21°S). Histogram maxima at 0, 6–8 and 25–27 km below slab top (p. 9). Interface seismicity ends at 50–55 km (p. 1, p. 12). Upper plane 6–8 km below interface, continuous along strike, to 80–90 km (p. 13). Lower plane 25–27 km below slab top, discontinuous (p. 13). Dip ~20° (p. 1). At 80–90 km the space between planes becomes active: cluster 20–25 km thick (p. 13), 80–120 km (p. 1), ~80–140 km (p. 21); ends at ~110 km north of 21°S (p. 13). Deeper isolated clusters 150–250 km south of ~21°S (p. 14). Intraslab ~60% of all events (p. 5). Plane widths < 5 km (p. 18). Slab age ~46 Ma, 68 mm/yr N76°E (pp. 2–3).
- Chile specifics: lower plane clearest at 21–21.6°S (sections D–E), nearly absent in northern sections A–C, short segments in the south F–H (p. 13, p. 19); possible link to subducted Iquique Ridge (p. 20). Upper-plate seismicity down to the interface at 21–21.6°S, mostly ML < 3.5 (p. 1, p. 15). Mining blasts removed by time-of-day filter (12–21 h local) for upper-plate class (p. 9).
- Caveats: offshore depths poor (Iquique aftershocks assumed on interface) (p. 9); slab polynomial underestimates short-wavelength curvature (p. 9); lower plane b-value difference not tested rigorously (p. 13). No focal mechanisms.

### Lu et al. 2021: Seismic imaging of the double seismic zone in the subducting slab in Northern Chile
- Ref: Lu, P., Zhang, H., Gao, L., Comte, D. (2021). Seismic imaging of the double seismic zone in the subducting slab in Northern Chile. Earthquake Research Advances, 1, 100003. https://doi.org/10.1016/j.eqrea.2021.100003 (p. 1).
- What it is: regional tomoDD Vp, Vs, Vp/Vs model with relocated hypocentres in the Pisagua region; DSZ planes read from relocated seismicity.
- Use for us: A7 (DSZ depth range at 18–20°S, from a long 1990–2013 data set).
- Coverage: Pisagua region 19–20°S (p. 2); profiles at 18.3, 18.9, 19.2, 19.8°S (p. 3); 9832 events, 244 short-period stations, 1990–2013 (data from Comte et al. 2016) (p. 2). No magnitudes given.
- Methods: 89,315 P and 85,790 S absolute times; pairs 5–30 km apart, ≤ 800 km event–station; 1,483,813 P and 1,365,567 S differential times (p. 2); grid 0.3° lat, 0.1° lon, 10 km depth; 15 iterations; RMS 0.364 s to 0.155 s (p. 3); good resolution 20–120 km depth (p. 3).
- Numbers to keep: DSZ at ~50–140 km depth, interval ~20 km (abstract, p. 1); 15–20 km (conclusions, p. 8). Upper zone ~30 to ~140 km; lower zone starts ~50 km and extends to ~140 km (p. 4). Northern two sections: sparse shallow lower-zone events and more events down to 100 km; southern two: lower zone concentrated at 50–75 km, sparse after 75 km, more again from ~110 to ~140 km (p. 5). Lower zone 20–30 km below the oceanic crust (p. 8). Upper zone Vp 7.8–8.0, Vs 4.4–4.5, Vp/Vs ~1.85–1.9 above ~90 km; below 90 km Vp ~8.2, Vs ~4.8, Vp/Vs ~1.75–1.76 (p. 1, p. 5); lower zone Vp/Vs 1.65–1.7 (p. 5, p. 8). Slab age 50 Ma, 8.4 cm/yr (p. 2).
- Focal mechanisms: none of its own; cites Comte & Suárez (1994) down-dip tension upper / compression lower (p. 2).
- Caveats: plane separation quoted differently in abstract and conclusions (~20 vs 15–20 km); no quality criteria for the relocated events reported; earthquakes shown only along profiles.

### Hernández-Soto et al. 2026: Structure of the North-Central Chile subduction zone from local earthquake tomography
- Ref: Hernández-Soto, N., Sippl, C., Miller, M., Lange, D., Tilmann, F., González-Vidal, D., Baez, J. C., Socquet, A., Moreno, M. (2026). Structure of the North-Central Chile subduction zone from local earthquake tomography. J. Geophys. Res. Solid Earth, 131, e2025JB032183. https://doi.org/10.1029/2025JB032183 (p. 1).
- What it is: 3D Vp and Vp/Vs tomography of the Atacama segment with a machine-learning catalogue; describes interface, upper and lower intraslab planes.
- Use for us: A7 (DSZ in 24.5–29.2°S, along-strike patchiness, Copiapó Ridge); A2 (dense local catalogue 2020–2022).
- Coverage: ~24.5–29.2°S, ~72–69°W; Nov 2020–Dec 2022; updated González-Vidal et al. (2023) catalogue with 33,748 events, 507,037 P and 458,002 S picks, 104 stations (ANILLO Y6, ISTerre XZ, CSN C/C1, IPOC, GSN) (pp. 4–5); conclusions say ~18 months of observation (p. 19). No magnitudes given.
- Methods: EQTransformer picks, PyOcto association (p. 5); VELEST minimum 1D from 457 events (p. 6); 2D/3D SIMUL2023 with 8,804 events (RMS ≤ 1.5 s, > 25 arrivals with ≥ 10 S-P, gap < 260°), mining-area and near-trench events removed (p. 6); final RMS 0.098 s (p. 7); 3D absolute relocation (RMS 0.25 to 0.12 s) then hypoDD in 1D model (RMS 0.093 s) (p. 7); checkerboards 10–100 km (p. 7).
- Numbers to keep: interface seismicity at 20–40 km depth (p. 11); second plane ~7–8 km below the interface, near the oceanic Moho, densest beneath active interface (p. 11); third plane ≥ 20 km below the interface, only in some profiles (P7, P9, P11, P13, P16), most visible at > 70 km (p. 11); ~20 km spacing between shallowest and deepest planes (p. 11). Oceanic crust disappears at 70–100 km, shallower to the south (p. 13). Persistent band of deep intraslab seismicity at the subducted Copiapó Ridge (~27°S, profiles P10–P13), not seen at Taltal Ridge (~25.5°S) (p. 2, p. 14). Plate age 40–50 Ma (S to N), 65–67 mm/yr (p. 2).
- Chile specifics: Mw 5.9 steep normal-faulting event of 4 Apr 2023 ~20 km below the interface (from Warwel et al. 2025) (p. 4); double Benioff zones generally not resolved in routine global catalogues (p. 4); own slab surface differs significantly from Slab2 (p. 19).
- Caveats: 10 km vertical node spacing (p. 13); offshore resolution limited (p. 19). No focal mechanisms.

### Hayes et al. 2018: Slab2, a comprehensive subduction zone geometry model
- Ref: Hayes, G. P., Moore, G. L., Portner, D. E., Hearne, M., Flamme, H., Furtney, M., Smoczyk, G. M. (2018). Slab2, a comprehensive subduction zone geometry model. Science, 362, 58–61. No DOI on p. 1 (10.1126/science.aat4723 printed on p. 4 and p. 5); data doi 10.5066/F7PV6JNV (p. 4).
- What it is: global 3D slab-surface model for all active subduction zones, successor of Slab1.0.
- Use for us: A7 (slab-top reference to compute an event's distance from the slab; South America model "sam").
- Coverage: all seismically active subduction zones, trench to deepest slab expression; > 24 million km² of slab (p. 1).
- Methods: input data: active-source profiles, receiver functions, local/regional catalogues and relocations, tomography (p. 2); global catalogues ComCat, EHB, GCMT (p. 4). Slab depth modelled at grid nodes, then interpolated to a 3D surface (no 2D-to-3D iteration as in Slab1.0) (p. 2); a filtered slab-related catalogue is built per zone (p. 2). Details are in the supplement (ref. 15), not in our file.
- What the model gives (as stated in the main text): slab surface geometry; seismogenic zone limits Ss, Sd as 10th and 90th percentiles of a double-normal fit to thrust-event depths; width Sw; mean interface dip, strike, rake (p. 2, Table 1 p. 3). Thickness, dip, strike and uncertainty grids are not described in the main text (supplement not available here).
- Numbers to keep: Table 1 (p. 3) South America "sam": n = 1370, Ss 11 km, Sd 45 km, Sw 118 km, dip 15°, strike 356°, rake 85°, Mmax 9.5. Global Sd ~37 km (Izu-Bonin) to ~54 km (Kuril); Sw ~70 to ~195 km, average ~115 km, ~30% larger than older estimates (p. 4).
- Chile specifics: tomography lets Slab2 resolve the aseismic deep slab beneath southern Chile and the S Peru flat slab (p. 2); southern Chile has a narrow seismogenic zone (Sw ~100 km) yet hosted M9+ (p. 4).
- Caveats: Sw computed only for slabs with > 50 thrust events (p. 4); local studies find their slab top differs from Slab2 (Hernández-Soto et al. 2026, p. 19).

### Leyton et al. 2009b: Intraplate and interplate earthquakes in Chilean subduction zone
- Ref: Leyton, F., Ruiz, J., Campos, J., Kausel, E. (2009). Intraplate and interplate earthquakes in Chilean subduction zone: A theoretical and observational comparison. Phys. Earth Planet. Inter., 175, 37–46. doi:10.1016/j.pepi.2008.03.017 (p. 1).
- What it is: comparison of source parameters (M0, f0, Es, apparent stress) of interplate thrust and intermediate-depth intraplate events in central Chile, plus synthetic seismograms.
- Use for us: A7 (classification rule used for Chile: depth and distance from trench); A6 (list of large intraslab events with depths); hazard relevance of intraslab events.
- Coverage: central Chile, Nov 1999–Jan 2006, magnitudes 3.5–6.5, located with the Chilean Seismological Network, regional records 50–600 km (p. 2). Small interplate events 32.6–37.3°S (Table 1, p. 2); small intraplate 32.7–39.4°S, depths 69–164 km (Table 2, p. 2).
- Methods: Brune spectral fits for M0, f0, Q (p. 4); radiated energy after Boatwright (p. 4); apparent stress from Es/M0 after Wyss & Brune 1968 (Eq. 7, rigidity symbol lost in the text extraction) (p. 5); frequency-wavenumber synthetics with source at 65 km, 200 km from trench, strike 0°, dip 80°, rake ±90° (pp. 6–7).
- Classification rule: interplate contact down to 45–50 km depth and up to 200 km from the trench (~100 km from the coast) (p. 2); interplate events at 15–50 km depth, intraplate events with continental epicentres and depth > 50 km (p. 1).
- Numbers to keep: σa ~90 bar intraplate vs ~30 bar interplate (p. 1); intraplate events have larger f0 and Es at given M0 (p. 9); counts: 24 small + 13 CMT interplate (Table 4, p. 6), 22 small + 7 CMT intraplate (Table 5, p. 7).
- Chile specifics: tensional intraplate events Antofagasta 1950 Ms 8.0 (90 km), Chillán 1939 Ms 7.8 (80 km), Santiago 1945 Ms 7.1 (70 km), La Ligua 1965 Ms 7.1 (abstract) or 7.5 (p. 1, 70 km), Taltal 1965 Ms 6.9, Tocopilla 1970 Ms 6.5, Tarapacá 2005 Mw 7.8, Punitaqui 1997 Mw 7.1 (58 km) (p. 1).
- Caveats: misclassification of small events by location errors, accretionary-prism events in the interplate group (p. 2, p. 8); no event rates or magnitude-frequency comparison; Table 1 "interplate" list includes events at ~69°W and 13–19 km depth (codes 10, 11) and one at 53.8 km (code 17) (p. 2).


## Synthesis

Facts from the cards, with the paper and page. Short names: EV02 Engdahl and Villaseñor 2002; S13, S15, S17 Storchak 2013, 2015, 2017; DG14, DG15, DG16, DG18 Di Giacomo 2014, 2015, 2016, 2018; B15 Bondár 2015; W18 Weston 2018; E98 Engdahl 1998; E12 Ekström 2012; D81 Dziewonski 1981; RM18 Ruiz and Madariaga 2018; L04 Lomnitz 2004; G04 Giesecke 2004; A13, A14 Albini 2013, 2014; C25 Cabello 2025; P24 Potin 2024; B18 Barrientos 2018; R18 Riquelme 2018; RH26 Riedel-Hornig 2026; S18, S23 Sippl 2018, 2023; M20 Münchmeyer 2020; C06 Castellaro 2006; LG12 Lolli and Gasperini 2012; L14, L23 Lolli 2014, 2023; W16 Weatherill 2016; S06 Scordilis 2006; G13 Gasperini 2013; HK79 Hanks and Kanamori 1979; P19 Poulos 2019; Ley09 Leyton 2009 (Adv. Geosci.); Ley09b Leyton 2009 (PEPI).

### 1. Source order

Per period of `catalog/PREFERENCES.md`.

**Before 1904.**
- Magnitudes: CERESIS carries Ms only (G04 p. 7, p. 11). C25 takes CERESIS Mw as given and changes four events (1730 to Mw 9.1–9.3; 1835, 1928, 1939 only in its supplement) (C25 p. 7). GHEC uses Lomnitz's Ms estimates for Chile (30 events) and treats Ms as Mw for M 6.5–8 without conversion (A14 p. 11, p. 13; A13 p. 116, p. 127). L04 magnitudes are felt-area Ms estimates (Kawasumi method), ±0.5 in some cases (L04 p. 2, p. 8).
- Location: L04 epicentres may be off by a degree or so (p. 10). Coverage is better at 32–39°S than north or south, and the north is in Peruvian or Bolivian sources before 1879–1880 (L04 p. 2).
- Completeness: L04 is complete only near Ms 7.5 for 1535–1960, not for smaller or deep shocks (p. 8). In GHEC, South American completeness for shallow Mw ≥ 7 is stable from the late 16th century but well below the modern rate. Deep and intermediate events are incomplete throughout (A13 p. 131, p. 135).
- Depth: 75 % of GHEC events have no depth (A13 p. 116). C25 fills missing depths from Slab2 and warns that pre-1900 events may be too shallow (C25 p. 6–7, p. 10).
- Global catalogues: EV02 has 1900–1903 events at M ≥ 7, located by Abe, with no depth (EV02 Table 1 p. 7). ISC-GEM V5 dropped its ten 1900–1903 events and starts in 1904 (DG18 p. 9).

**1904–1963.**
- Location, Centennial: EHB relocation only for 1918–1942 and 1956–1999. Elsewhere the epicentre is the G&R, Abe, ISS or P&S value, often at whole or half degrees and without depth (EV02 p. 23, Table 1). For Chile this means 1904–1917 and 1943–1955 are not relocated, including 1939 Chillán, 1943 Illapel and the 1949 Magallanes pair (Table 1 pp. 7–15).
- Location, ISC-GEM: every event relocated (B15 p. 1), with phases digitised from the early bulletins (DG14). Median shift from the earlier location 10 km, 90 % < 25 km, largest in the first three decades (B15 p. 9–10). All 1903–1930 events reviewed by hand (B15 p. 10). In the extension, median shifts are about 100 km in the 1920s and about 20 km in the late 1950s (DG18 p. 6). So ISC-GEM has a relocated epicentre where the Centennial has only a catalogue value.
- Magnitude, Centennial: not recomputed. One value per event taken from other catalogues; preference Mw (from M0) > MS > mB > mb for h ≤ 60 km, and Mw > mB > mb for h > 60 km (EV02 p. 3). For Chile before 1976 the values are Pacheco and Sykes (1992) Mw for shallow events, and Abe mB (ABE1) for intermediate-depth events and some 35 km events (Table 1). The −0.2 correction of G&R, B&D, Rothé and Pasadena is used only for selection, not applied to the listed value (EV02 p. 5). EV02 calls its magnitudes very heterogeneous (p. 3).
- Magnitude, ISC-GEM: one Mw per event. Direct Mw comes from GCMT or from the literature (967 events 1904–1978). Otherwise a proxy from recomputed Ms (median of ≥ 3 stations, 20 % trimmed) or mb, in the order GCMT > literature > Ms proxy > mb proxy (DG15 p. 1–3, p. 10, p. 12). Recomputed Ms agrees with Abe and is about 0.2 below G&R (DG15 p. 4–5).
- Deep events: before 1964, deep events without a direct Mw are not in the ISC-GEM main catalogue, because there is no Ms for h > 60 km and almost no mb (DG15 p. 12).
- Thresholds: Centennial selects M 6.5 before 1964 and is complete to MS 7.0 over the century and MS 6.5 for 1930–1963 (EV02 p. 6, p. 23). ISC-GEM V1 cut-offs were Ms 7.5 (1900–1917) and 6.25 (1918–1959), applied to pre-existing magnitudes, so a recomputed M can fall below the cut-off (DG15 p. 2). Completeness from DG15 Fig. 23 (read from the figure, p. 14): ≈ 7.55 for 1900–1917, 6.35 for 1918–1939, 6.5 for 1940–1954, 6.15 for 1955–1963.
- RM18 recommends the Centennial for large Chilean events up to about 2010, because ISC and USGS put 1922 Atacama at 70 km and some near the border. They also note the Centennial misplaces a January 1922 event (RM18 p. 15).

**1964–1975.**
- Global catalogues: Centennial selects M ≥ 5.5 and is complete to MS 5.5 (EV02 p. 6, p. 23). ISC-GEM is complete to Mw 5.6 from 1964 (DG15 p. 1, p. 14) and lowered its selection to Mw 5.5 for 1964–1977 (DG14 p. 2). S13 p. 4 prints the opposite ("Mw 5.6 before 1964, 6.4 after"; see open points).
- EHB: 1964–1995, complete to about Mw 5.2. Median epicentre shift against ISC 7.6 ± 5.5 km; depth uncertainty ±10–15 km (E98 p. 1, p. 12, p. 21).
- ISC-EHB: L1–L3 depth classes. The paper itself covers 2000–2013; 1964–1999 was to be redone (W18 p. 10). ISC-GEM closely replicates ISC-EHB at M ≥ 5.5 (W18 p. 1).
- ISC Bulletin rebuild for 1964–1979: ak135 relocation, mb and Ms only from ≥ 3 stations, about 68 000 new events (S17 p. 7, p. 12). Before the rebuild, ISC network magnitudes were means over all stations and could rest on a single station (DG15 p. 5). The ISC computed its own Ms only from 1978 (S17 p. 9).
- Magnitude: Centennial still compiles P&S Mw and Abe mB; HRV Mw from 1976 (Table 1).

**1976–1981.**
- GCMT reported only mb ≥ 6.0 or MS ≥ 6.0 in 1976. The median Mw falls from 5.7 to 5.4 over 1977–2003, and completeness breaks near Mw 5.3–5.4 before 2004 (E12 p. 5, p. 7). Station count was 10–15 in 1976 (E12 p. 2).
- CMT epicentres are centroids. Their discrepancy with hypocentres grows as M0 decreases; CMT minus EHB epicentre 32.7 ± 21.3 km (E98 p. 12, p. 16).

**1982 – 2020-07-16.**
- P24: 3-D relocation of the CSN analyst catalogue. The raw CSN has 1-D tabular-model depth artefacts, with alignments at 150 km (31.5°S) and 15 km (33°S) before 2012 (P24 p. 1, p. 5, p. 13). No per-event depth uncertainty is given in the paper (RMS only, p. 3).
- CSN network history: limited to central Chile before 2002; stable coverage since 2001 (central), 2007 (north) and 2012 (central-north). CSN created in 2013, real-time network complete at the end of 2014, no major change since 2015 (P24 p. 2–4). Broadband stations: 36 in 2010, 49 in 2013, 106 by 2017 (R18 p. 4). CSN data for Jan–Sep 2000 are lost (P24 p. 4).
- Magnitude types in time: coda Mc to 2002, then ML; Brune-spectral Mw from the mid-2000s for M > 6; W-phase Mww systematic from 2015 for M > ~4.5 (P24 p. 4). P24 says it homogenized magnitudes but gives no method; the only coefficient is ML ≈ Mc − 0.25 (P24 p. 4, p. 13). CSN Mww agrees with USGS and GCMT within about ±0.2 (R18 p. 5).
- Completeness: CSN Mc 2.5–4.0 in space over 2010–2020, raised after Maule, Iquique and Illapel (P24 p. 4, p. 7). CSN Mc ~3.5 for 2013–2016 (B18 p. 4).
- RM18 calls the USGS, ISC and CSN catalogues since 1980 very similar (p. 15).

**2020-07-16 – today.**
- CSN Mc about 2.5 since 2019 (P24 p. 5). W-phase threshold Mww 6.5 in 2012 and 4.8 in 2017 (R18 p. 1, p. 10).
- RH26 (automatic catalogue, 2017–2021, 18–56°S): Mc 2.5 (3 in the south) against 3–4 for CSN/Potin. Mean errors 4.8 / 2.2 / 6.1 km in lon / lat / depth; eastern hypocentres too deep without Argentine stations (RH26 p. 5–8, p. 12–13). No magnitude offset against CSN is reported in the main text.

**Evidence for Q1 (Centennial vs ISC-GEM magnitude, 1904–1999).**
- Centennial magnitudes are compiled, not measured: about 20 magnitude types from many sources, against 4 Mw types in ISC-GEM (S13 Fig. 6 p. 5; DG15 Fig. 19 p. 12). For Chile before 1976 they are P&S Mw or Abe mB/MS, uncorrected (EV02 p. 3, p. 5, Table 1).
- EV02 Fig. 1 residuals against Abe MS: P&S Mw +0.01 ± 0.21 (N 614); MGR +0.18 ± 0.22; B&D +0.20 ± 0.26; Pasadena before 1960 +0.20 ± 0.22 (EV02 p. 4). P&S and Abe are consistent with Harvard Mw (p. 23).
- ISC-GEM recomputed Ms and mb from amplitudes and converted them with exponential fits to GCMT (DG15 p. 8, p. 10). The ISC-GEM authors recommend their Ms and mb as the new reference, especially Ms before 1971 (DG15 p. 14).
- Biases of the ISC-GEM proxies: they are OLS fits on GCMT data that thin out below Mw 5–5.5. L14 and L23 find such fits overestimate Mw at low M (L14 p. 8–10; L23 p. 1–2). W16 finds the DG15 exponential overestimates Mw for Ms < 4 (W16 p. 15). Above Ms ~5.5 the curves agree within about 0.1, which covers the ISC-GEM range for Chile (L14 p. 8).
- Teleseismic proxies overestimate Mw on average in subduction zones (L14 p. 6, Fig. 2). This applies to ISC-GEM proxies for Chile, not to P&S Mw.
- Before 1964, Chilean intermediate-depth events (e.g. 1950 Calama mB 7.7, 1965 La Ligua mB 7.4 in EV02 Table 1) carry Abe mB in the Centennial. In ISC-GEM they appear only if a literature Mw exists (DG15 p. 12).

**Evidence for Q2 (events below the global thresholds before 1982).**
- None of the global catalogues holds them by construction: Centennial selects at 6.5 and 5.5 (EV02 p. 23); ISC-GEM V1 at 6.25 and 5.5 (S15 p. 8). The ISC-GEM extension adds pre-1960 events below 6.25 only where station data allow, mostly in Europe and the North Atlantic (DG18 p. 8, p. 14). W16 notes that ISC-GEM excludes 4.5 ≤ Mw ≤ 5.5 (W16 p. 2).
- For 1964–1979, the rebuilt ISC Bulletin is the comprehensive source. Its mb and Ms come from ≥ 3 stations; contributed agency magnitudes are heterogeneous (S17 p. 7, p. 12; L14 p. 4; L23 p. 2).
- Completeness statements for Chile: Mw ≥ 5 complete since 1974 from ISC + ComCat (Stepp; P19 p. 2). The Centennial is complete for M > 6 only after 1960, and misses 6 < M < 7 events early in the century (RM18 p. 15, Fig. 8). C25 completeness bands go from 6.2–6.8 (1513–1960) to 2.7–3.2 (2000–2022) (C25 p. 8).
- C25 filled pre-1982 small events from ISC (from 1902) and USGS (from 1906); ISC contributes many intermediate-depth events (C25 p. 3, p. 6). B18 used SISRA for 1900–1981 (p. 2). W16 global merged completeness: Mw 6.0 from 1950, 5.5 from 1960, 5.0 from 1964, 4.5 from 1978 (W16 p. 22, Table 2).

### 2. Magnitude homogenization

**Methods and their biases.**
- OLS (Mw on native) assumes an error-free predictor. That fails for magnitudes: σ(Mw) 0.05–0.15 against 0.2–0.3 for native scales (C06 p. 1–3; L14 p. 2). Conversion bias is +0.1 to −0.3, up to 0.3–0.4 (C06 p. 1, p. 13); b-value bias 20–40 % (C06 p. 17). Errors in the native magnitude raise the a-value, so noisier old periods look more active (C06 p. 14, p. 17).
- GOR needs the variance ratio η = σ²(Mw)/σ²(native) within an order of magnitude, and is never worse than OLS in the simulations. With η < 1 (mb against Mw) it is close to inverse OLS. η = 1 still beats OLS when the true η is 0.25, but not when it is 25 (C06 p. 5, p. 13).
- Chi-square (CSQ), GOR and WLS give identical coefficients for linear models with constant η. Their formal σ differ by ≤ 5 % and are 5–30 % off the bootstrap σ (LG12 p. 13, p. 15). CSQ takes per-event σ and non-linear forms (L23 p. 2). With σ(Mw) ≈ 0.1 and σ(mb) 0.2–0.4, CSQ ≈ inverse OLS of mb on Mw (L23 p. 5).
- ODR in W16 uses unit weights, i.e. η = 1 (W16 p. 7).
- Curvilinear forms: exponential Mw = exp(a + b·x) + c (L14 p. 3; DG15), connected bilinear CBL / CBL-R (L14 p. 3–4; L23), piecewise linear (W16 p. 7). The exponential flattens at low M and steepens without bound at high M (L14 p. 3; W16 p. 15). Observed Ms breaks: 6.2 (S06 p. 6), 6.0–6.1 (W16 p. 15), 6.47 (DG15), MI 5.81 / 6.17 (L23 p. 6). mb ≈ Mw below mb 4–4.5 and saturates above 5–5.5 (L23 p. 2).
- Incompleteness bias: global moment-tensor catalogues hold few Mw < 5–5.5. Fits on such data overestimate Mw at low Ms by up to 0.5 (at Ms 3.5) and lower the low-M slope (L14 p. 9–10, p. 16). The remedy used is Euro-Mediterranean coefficients for Ms ≤ 5.5 (L14 p. 18; L23 p. 8). The check of a conversion is the stability of b against the cut-off, plus completeness-rate plots (L14 p. 14–18; L23 p. 9–10).
- Proxy-Mw composition (ISC-GEM): direct Mw where available, else proxy by priority (DG15 p. 10). L14 and G13 instead combine all proxies of an event by an inverse-variance weighted mean, σ = 1/√Σ(1/σi²); G13 found this gives a more stable b than choosing one type (L14 p. 13; G13 p. 10–11).
- Uncertainty: proxy σ 0.10–0.25 from Ms and 0.20–0.45 from mb (L14 p. 12). ISC mb 5.5 ± 0.40 gives σMw 0.50 (L23 p. 8). DG15 projects Ms 6.0 / 8.0 ± 0.15 to 0.23 / 0.36, and mb 5.5 / 6.6 ± 0.1 to 0.18 / 0.4 (p. 9–10).
- Reference scale: Mw = (2/3) log M0 − 10.7 (dyn·cm), valid for 3 ≲ ML ≲ 7, 5 ≲ Ms ≲ 7½ and Mw ≳ 7½ (HK79 p. 1–2, checked on the image). The IASPEI form (2/3)(log M0 − 9.1) in N·m is 0.033 lower (L14 p. 2). EV02 uses −10.7 (p. 22); E12 gives no formula. GCMT Mw < 5.4 may be overestimated, and NEIC Mw > 7.0 underestimated (L14 p. 5; L23 p. 2). Agency Mw shifts: NEIC +0.05, GFZ +0.05 (L23 Table 1 p. 3). GCMT = 1.021·NEIC − 0.091, σ 0.105 (W16 p. 14).

**Relations per native scale** (y = Mw; validity and page).

| native | relation | method, data | range | source |
|---|---|---|---|---|
| ISC mb | exp(0.082 + 0.266 mb) + 1.039 | CSQ exp., global, 1964–2020, N 48 498, σr 0.293 | as data | L23 p. 6 |
| ISC mb | 1.390 mb − 1.942 above MI 4.98, Mw = mb below | CSQ CBL-R, global | | L23 p. 6 |
| ISC mb | exp(0.741 + 0.210 mb) − 0.785 | CSQ exp., global, N 30 326 | 3.6–7.2 | L14 p. 18 |
| ISC mb | exp(−4.664 + 0.859 mb) + 4.555 | OLS exp., GCMT 1976–2009, N 27 634 | medians 4.6–6.5; caution < 5, > 6.8 | DG15 p. 10 |
| ISC mb | 1.38 mb − 1.79 | GOR (not adopted) | | DG15 p. 10 |
| ISC mb | 1.084 mb − 0.142; exp(−6.373 + 1.182 mb) + 4.577 | ODR (η = 1), 22 105 pairs | | W16 p. 18 |
| ISC+NEIC mb | 0.85 mb + 1.03, σ 0.29 | OLS | 3.5–6.2 | S06 p. 7 |
| NEIC mb | exp(0.948 + 0.179 mb) − 1.240; CBL-R 1.508 mb − 2.780 above MI 5.47 | CSQ, 2005–2022, N 33 773 | | L23 p. 8 |
| NEIC mb | 1.159 mb − 0.659, σ 0.283 | ODR, 23 207 pairs | | W16 p. 18 |
| ISC vs NEIC mb | mb_ISC = 1.044 mb_NEIC − 0.331; = 1.02 mb_NEIC − 0.18 | ODR; OLS | 2.5–7.3 (S06) | W16 p. 18; S06 p. 7 |
| ISC Ms | exp(−0.137 + 0.229 Ms) + 2.673 | CSQ exp., global, N 34 188 | depth < 50 km | L23 p. 6 |
| ISC Ms | exp(2.133 + 0.063 Ms) − 6.205 (Ms ≤ 5.5); exp(−0.109 + 0.229 Ms) + 2.586 (Ms > 5.5) | CSQ, MED below 5.5 | | L14 p. 18 |
| ISC-GEM Ms | exp(−0.222 + 0.233 Ms) + 2.863 | OLS exp., N 15 723 | caution < 5 | DG15 p. 8 |
| ISC-GEM Ms | 0.67 Ms + 2.13 (≤ 6.47); 1.10 Ms − 0.67 (> 6.47) | GOR (not adopted) | | DG15 p. 8 |
| ISC Ms | 0.616 Ms + 2.369 (≤ 6.0); 0.994 Ms + 0.100 | ODR | | W16 p. 15 |
| Ms | 0.67 Ms + 2.07 (3.0–6.1); 0.99 Ms + 0.08 (6.2–8.2) | OLS, h < 70 km | | S06 p. 5 |
| NEIC Ms | 0.723 Ms + 1.798 (≤ 6.47); 1.005 Ms − 0.026 | ODR | | W16 p. 16 |
| NEIC Ms_20 (from 2013) | exp(1.108 + 0.124 Ms) − 0.246 | CSQ | | L23 p. 8 |
| Chile ML | 0.676 + 0.899 ML (n 891) | orthogonal, η and agency not stated | | P19 p. 2 |
| Chile Ms | 0.585 + 0.935 Ms (n 1115) | as above | | P19 p. 2 |
| Chile mb | −1.005 + 1.227 mb (n 1716) | as above, linear over the full range | | P19 p. 2 |
| Chile, to Ms | Ms = 1.322 mb − 1.949 (730); Ms = 1.137 ML − 0.808 (268); Ms = 1.127 Mw − 1.197 (258) | OLS, Ms dependent | | Ley09 p. 3 |
| CSN ML | 0.80 ML + 1.15 (≤ 50 km); 0.94 ML + 0.30 (> 50 km) | method not named | 4.5–6.5 | C25 p. 8 |
| CSN/USGS/GCMT Ms, mb | 0.74 Ms + 1.60 (4.5–6.4); 1.04 mb − 0.02 (4.5–6.5) | pooled | | C25 p. 8 |
| ISC mb (C25) | 0.87 mb + 0.75 | | 4.5–6.5 | C25 p. 8 |
| GCMT Ms, mb (C25) | 0.84 Ms + 1 (4.5–7.3); 1.03 mb + 0 (4.5–7.0) | | | C25 p. 8 |
| CSN, USGS Mw (C25) | 0.92 Mw + 0.43; 0.94 Mw + 0.35 (4.5–6.5) | | | C25 p. 8 |
| CSN Mc → ML | ML ≈ Mc − 0.25 (average, no regression) | | | P24 p. 4 |
| Italy ML, MD | WA ML 1:1 but 0.08–0.26 below Mw; MD slopes 1.13–1.72 | CSQ | | G13 p. 7, p. 14 |

- CSN Mw / Mww: agrees with GCMT within about ±0.2 (R18 p. 5); no relation given.
- Md, Mc: no Chilean calibration in any paper. C25 takes Mc, Md and m as Mw unchanged, and also any native value outside an equation's range (C25 p. 3, p. 10).
- CERESIS: magnitudes are Ms (G04 p. 7); GHEC and C25 take them as Mw (A13 p. 116; C25 p. 7). Boxer intensity Mw is mostly smaller than CERESIS Ms, by −1.4 to +1.8 (G04 p. 11, not Chilean events).
- No paper calibrates a South American agency (GUC, SAN, CSN) except P19 and Ley09, and neither names the agency (L23, W16).
- Evaluated by us (notes, not in the papers): at mb 5.0, Mw = 5.14 (L23 ISC), 5.21 (L14 ISC), 5.25 (DG15), 5.08 (L23 NEIC), 5.14 (W16 NEIC), 5.28 (S06), 5.13 (P19). At Ms 6.0, Mw = 6.12 (L23), 6.10 (DG15), 6.09 (S06), 6.20 (P19). From L23 ISC: mb − Mw ≈ −0.19 at Mw 5.5 and ≈ −0.43 at Mw 6.5.

**Candidate approaches for A5** (no choice).
1. **Published agency-specific relations as they are.** ISC mb and Ms with L23 (CSQ curvilinear, MED below Ms 5.5), NEIC mb, Ms and Ms_20 with L23 or W16, DG15 where consistency with ISC-GEM matters. Proxies of one event combined by inverse-variance mean; GCMT Mw wherever it exists. Needs: value, type and author per magnitude (ISC-recomputed or contributed; NEIC Ms, Ms_20 or Msz; IDC apart), station count, depth (Ms only shallow), and residuals against GCMT on Chilean pairs to test the subduction-zone overestimate (L14 p. 6). Leaves CSN ML, Md and Mc uncovered.
2. **Chile-specific calibration against GCMT Mw.** CSQ or GOR per agency and type (ISC mb, ISC Ms, NEIC mb, CSN ML, Mc, Md, Mw), curvilinear for mb and Ms, linear or offset for ML. η estimated; σ resized until the a priori σ equals the empirical one (G13, L14). Possibly split by depth class and by network period; bootstrap uncertainties (LG12). Needs: pairs matched by time and distance only, enough pairs below Mw 5–5.5 (where GCMT is incomplete and may run high), per-event σ or station counts, the CSN magnitude-type history (P24 p. 4), and a comparison with P19 and Ley09. Validated by b against the cut-off and completeness-rate plots.
3. **Chained conversion.** Local scale → teleseismic scale with many overlaps (e.g. CSN ML → ISC or NEIC mb, Mc → ML), then a global relation to Mw, with covariances combined (G13 App. C). Offsets where the slope is 1. Needs: large overlap sets covering a wider magnitude range than the Mw pairs, the covariance of each link, and a per-period, per-agency rule for which chain applies (W16-style hierarchy). Same b-value validation.

### 3. Depths

| source | how depth is set or flagged | defaults and fixed values | quality info |
|---|---|---|---|
| Centennial | EHB where relocated (1918–1942, 1956–1999); otherwise the source value, often blank (EV02 p. 23, Table 1) | Table 1 repeats 35, 25 and 15 km (check PDF); isol codes HEQ / DEQ / LEQ / FEQ / XEQ in CENT.CAT, not printed in Table 1 (EV02 p. 24) | 1939 Chillán and 1943 Illapel have no depth |
| EHB | pP, pwP, sP with bounce-point bathymetry; no pwP if water < 1.5 km; statistical phase association (E98 p. 3–7) | poor if depth error > 15 km without depth phases (E98 p. 7); 85 % free | ±10–15 km; EHB − ISC −1.7 ± 11.8 km; EHB − CMT 1.2 ± 13.1 km (E98 p. 12, p. 21) |
| ISC-EHB | depth phases; else external depth USGS broadband > ISC-GEM > studies > GCMT (W18 p. 3) | 10 km ridge or open ocean; 15 km within 55 km of trench or volcano, or in shallow regions; manual fixes in 10 km steps; aftershocks set to neighbours (W18 p. 3–5) | L1: free, error < 5 km, ≥ 3 depth phases (or fixed by phases or broadband); L2: free, error < 5 km with < 3 phases, or 5–15 km, or fixed at the GCMT depth; L3: error > 15 km or fixed from seismicity or tectonics (W18 p. 4). L1 median error 1.65 km, L2 4.23 km; ISC-EHB − GCMT −0.8 ± 8.5 km (W18 p. 5, p. 8) |
| ISC-GEM | EHB depth when ≥ 5 corroborating depth phases, checked by hand; large complex shallow events at the USGS broadband depth (B15 p. 4–6) | about a third have no usable phases; nominal depth from well-constrained neighbours in the same setting, using subduction cross-sections. No fixed number (15 or 35 km) stated (B15 p. 6, p. 10) | uncertainty from stacking, else the cell MAD (< 15 km), else 25 km (B15 p. 7). Flags A–D (DG18 Table 1 p. 4); 1904–1919 depth flags A/B/C 6 / 2 / 1102 (DG18 p. 14) |
| ISC Bulletin (rebuilt) | free where constrained | most common depth in the 1° cell, else 10 or 35 km per Flinn–Engdahl region; many old 33 km became 10 km (S17 p. 7, p. 9) | 205 events moved > 300 km because of different defaults in subduction zones (S17 p. 9) |
| ISC (pre-rebuild) | – | 10, 15, 33 km when unconstrained (E98 p. 14) | – |
| GCMT | centroid depth from the inversion | minimum 12 km, fixed at 12 when shallower; unstable depths fixed at the hypocentre or a regional value (E12 p. 5). Harvard default 15 km, 10 km in 1981–1985 (E98 p. 12). D81 study: some at 10, 20, 33 km (check PDF) | Table 1 rows at 12.0 km with no σ are fixed (E12 p. 6) |
| CSN / Potin | 1-D tabular models (raw CSN); 3-D relocation (P24) | raw CSN alignments at 150 km (31.5°S) and 15 km (33°S) before 2012; eastern events poorly located in depth (P24 p. 5, p. 13) | no per-event depth error in P24 |
| RH26 | NonLinLoc | – | depth error mean 6.1 km; too deep in the east (p. 5, p. 12–13) |
| Cabello | source depth kept; missing depths from Slab2, flagged "original depth:" (C25 p. 6–7) | 13 literature crustal events kept at the source depth | pre-1900 may be too shallow (p. 10) |
| CERESIS | Dph field (G04 p. 7) | no rule given | – |
| GHEC | 75 % without depth; depth often assigned from modern seismicity (A13 p. 116) | – | – |

Historical depths in the papers: 1939 Chillán 60 km (L04 p. 7, p. 10), 80–100 km (B18 p. 2), 80 km (Ley09b p. 1). 1953 Chillán 60 km (L04 p. 7). 1922 Atacama put at 70 km by G&R, ISC and USGS, considered wrong (RM18 p. 8, p. 15). 1960 nucleation possibly 30–40 km (L04 p. 10). Before 1960, mechanisms cannot separate interface, intraslab and crustal events (RM18 p. 15).

Depth limits relevant to A7: interface seismicity ends at 50–55 km in northern Chile (S18 p. 1, p. 12). Slab2 for South America: Ss 11 km, Sd 45 km (Hayes p. 3). Ley09b and P19: interplate 15–50 km, intraplate > 50 km; P19 uses trench to 60 km and 60 to ~160 km (Ley09b p. 1; P19 p. 3). RH26 stops its interface class at 60 km, where the DSZ planes leave the interface (p. 4). Intraslab tops lie deeper than Slab2 below ~100 km (RH26 p. 12).

### 4. Double seismic zone

| study | latitude (longitude) | data | upper plane | lower plane | separation | merge or end | mechanisms |
|---|---|---|---|---|---|---|---|
| Comte et al. 1999 | ~18–19.4°S, 72–69°W | Arica permanent (9 sta, ~3900 ev) + temporary Jun–Aug 1996 (~1000 ev); 3-D joint inversion, 3083 well constrained (pp. 1–2) | single zone ~10 km thick above 100 km, to 150 km, dip ~30° (p. 2) | 20–25 km beneath, ~10 km thick (p. 2) | 20–25 km (p. 2) | DSZ at ~100–150 km (p. 3) | mixed in both planes (pp. 2–3) |
| Dorbath et al. 2008 | Peru border to 19°20′S | same Arica network + permanent 1996–1997, 2052 events, tomoDD (p. 3) | 80–130 km, in oceanic crust (p. 7, p. 22) | to 130 km, in mantle (p. 8, p. 22) | 20 km; planes 5–10 km thick (p. 5) | DSZ 80–140 km (p. 1) | 41 upper, 4 lower; both T and C (p. 7) |
| Lu et al. 2021 | 19–20°S (profiles 18.3–19.8°S) | 9832 events, 244 stations, 1990–2013, tomoDD (p. 2) | ~30–140 km (p. 4) | ~50–140 km, 20–30 km below oceanic crust (p. 4, p. 8) | ~20 km (p. 1); 15–20 km (p. 8) | DSZ 50–140 km (p. 1) | not given |
| Sippl et al. 2018 | 19–23.6°S | IPOC + CSN + temporary, 2007–2014, 101 601 events, hypoDD (pp. 3–5) | 6–8 km below the slab top, from the interface to 80–90 km (p. 9, p. 13) | 25–27 km below the slab top (p. 13) | ~19–20 km | both absorbed into one 20–25 km thick cluster at 80–90 km; cluster 80–120 km, ends ~110 km north of 21°S (p. 1, p. 13) | not given; lower plane higher b (p. 13) |
| Sippl et al. 2023 | ~18.3–23.5°S | IPOC 2007–2021 | above ~90 km; compressive at shallow depth, downdip extension from ~60–65 km (p. 20, p. 24) | from ~45–50 km at 21°S (p. 19, p. 24) | ~20 km (p. 19) | no DSZ below ~90 km; 25–30 km thick cluster instead; sharp transition (p. 19, p. 22) | lower plane and cluster downdip extension (p. 20, p. 24) |
| Rietbrock and Waldhauser 2004 | 21.5–22.2°S | ANCORP Dec 1996–Feb 1997, 238 hypoDD events (pp. 1, 3) | top of oceanic crust, from ~80–85 km (p. 3) | uppermost mantle (p. 3) | 8–10 km, ~5 km quiet gap (p. 3) | 80–130 km (p. 1) | extension in both (p. 3) |
| Hernández-Soto et al. 2026 | 24.5–29.2°S | 104 stations, Nov 2020–Dec 2022, 33 748 events, hypoDD (pp. 4–7) | ~7–8 km below the interface (p. 11) | ≥ 20 km below the interface, mostly > 70 km (p. 11) | ~20 km (p. 11) | not stated; oceanic crust vanishes at 70–100 km (p. 13) | Mw 5.9 normal event 4 Apr 2023 in lower plane (p. 4) |
| Marot et al. 2013 | 30.5–32.5°S clear, 29.5–30.5°S possible | OVA99 1999–2000 + CHARSME 2002–2003; VELEST (p. 4) | from the interface; 13 mechanisms at 52–75 km (p. 8) | from 50 km (p. 4) | up to 20–25 km (p. 4); 30 km in Table 1 (p. 3) | merge at ~100–120 km at the flat-slab hinge (p. 4, p. 12) | upper 70 % normal, lower 80 % normal; compression above 60–70 km (p. 4, p. 12) |
| Riedel-Hornig et al. 2026 | 18–35°S | automatic catalogue 2017–2021 | – | – | not given | – | – |

Where along Chile:
- **18–19.5°S (Arica):** documented at ~80–150 km, 20–25 km apart (Comte p. 2–3; Dorbath p. 1, p. 5). North of 18.5°S the planes stay distinguishable inside the deep cluster (S23 p. 19).
- **18.3–19.8°S (Pisagua):** documented at ~50–140 km, 15–20 km apart (Lu p. 1, p. 4, p. 8).
- **19–21°S (Iquique):** lower plane nearly absent (S18 sections A–C, p. 13); very faint north of 20°S (S23 p. 19). This conflicts with Lu at the same latitudes.
- **20.5–22°S:** clearest; the lower plane reaches far updip, to ~45 km at 21°S (S18 p. 13, p. 19; S23 p. 19, p. 24). At 21.5–22.2°S, Rietbrock and Waldhauser find planes 8–10 km apart at 80–130 km, inside the depth range where S18 sees one cluster.
- **22–23.6°S:** lower plane only in short segments (S18 p. 13); intraslab rates decay south of 22°S (S23 p. 19). A DSZ at 20–24°S proposed from mechanisms (Comte and Suárez 1994) was not found by PISCO'94 or Rudloff 1998 (Dorbath p. 2; Rietbrock p. 1).
- **23.6–24.5°S:** no study.
- **24.5–29.2°S (Atacama):** lower plane in some profiles only, mostly > 70 km; strongest at the Copiapó Ridge (~27°S), absent at the Taltal Ridge (~25.5°S) (Hernández-Soto p. 11, p. 14). RH26 and other studies they cite report a DSZ at 23–30°S (RH26 p. 11).
- **29.5–32.5°S (flat slab, Juan Fernández Ridge):** documented from 50 km down to 100–120 km, 20–25 km apart (Marot p. 4, p. 12).
- **33°S and south:** questionable at 33°S and none reported south of 32.5°S (Marot p. 4, p. 8, citing Campos 2002 and Haberland 2009). RH26 see a DSZ along most of 18–35°S in cross-sections, without numbers (p. 4–5, p. 11). No paper documents a DSZ south of about 35°S.

For A7:
- Depth envelope: the lower plane starts at ~45–50 km (Marot, Lu, S23) or right below the end of interface seismicity (S18), and ends or merges at 80–150 km.
- Separation 15–27 km in every study except Rietbrock and Waldhauser (8–10 km). The upper plane lies 6–8 km below the slab top (S18) and cannot be told from the interface with catalogue depths.
- Mechanisms do not identify the plane: both T and C appear in both planes (Comte, Dorbath), or extension in both (Rietbrock, Marot).
- Global catalogues do not resolve the DSZ (Hernández-Soto p. 4; Marot p. 10 for EHB).

### 5. Large events

Where Ruiz and Madariaga (RM18), Lomnitz (L04), Cabello (C25) and Engdahl and Villaseñor (EV02) disagree on a Chilean event's magnitude, date or location.
- **EV02 values:** from Table 1. All 106 Chilean rows (15–60°S, 64–82°W) were checked field by field against the page images (rendered at 250 dpi and rotated) and match the OCR. No Chilean row is missing from the OCR text, so EV02 values below carry no "(check PDF)".
- **RM18 locations:** read off its figures (about ±0.1°).
- **L04 dates:** local time; GMT where L04 prints it.
- **C25:** the paper prints parameters only for a few events (Tables 7 and 8, the 1730 change); its other values are in the catalogue file, not in the text.

**1900 onwards** (EV02 time UTC; M with type and source code).

| event | RM18 | L04 | EV02 | C25 / others | disagreement |
|---|---|---|---|---|---|
| 1906 Valparaíso | 17 Aug, Mw 8.2, C-B, 32.9S 71.45W (p. 16, Fig. 6) | 16 Aug 8:40 PM (00:40 GMT 17 Aug), 8.6 (G-R) (p. 6) | 1906-08-17 00:40, −33.00 −72.00, no depth, Mw 8.5 P&S (p. 7) | B18: M 8+ (p. 3) | Mw 8.2 against 8.5–8.6; RM18 rejects 8.6 (p. 11) |
| 1918 Copiapó | Table 1: 4 Dec, Mw 7.8, probably C; text: 18 Dec (p. 9, p. 16) | 18 Dec 7:44 AM, 7–7.5, tsunami at Caldera (p. 7) | 1918-12-04 11:47:39, −27.27 −73.46, 25 km, Mw 7.5 P&S (p. 10); no 18 Dec row | – | possibly two events (4 Dec offshore, 18 Dec Copiapó); RM18 mixes the dates; M 7.0–7.8 |
| 1922 Atacama | 11 Nov, Mw ~8.5, 28.55S 70.75W (p. 16, Fig. 5) | 10 Nov 11:33 PM (04:32 GMT 11 Nov), 8.4 (Richter) (p. 7) | 1922-11-11 04:32:45.2, −28.55 −70.75, 35 km, Mw 8.7 P&S (p. 10) | G-R 8.3 at 70 km (RM18 p. 8) | Mw 8.5 against 8.7; depth 35 km (EV02) against 70 km (G-R, ISC, USGS) |
| 1928 Talca | 1 Dec, Mw 7.7, C (p. 16) | 1 Dec 12:06 AM (04:06 GMT), 8.4 (Richter) (p. 7) | 1928-12-01 04:06:15.2, −35.09 −71.68, 35 km, Mw 7.7 P&S (p. 11) | C25 recalculated, value only in its supplement (p. 7) | L04 0.7 higher |
| 1939 Chillán | 24 Jan, Mw 7.8, intraslab (p. 9) | 24 Jan 11:32 PM (03:32 GMT 25 Jan), 8.3, 60 km (pp. 7, 10) | 1939-01-25 03:32:00, −36.20 −72.20, no depth, Mw 7.7 P&S, not relocated (p. 13) | B18: M 7.8, 80–100 km (p. 2); Ley09b: Ms 7.8, 80 km (p. 1); C25 recalculated (supplement) | M 7.7–8.3; depth 60, 80 or 80–100 km, none in EV02 |
| 1943 Illapel | 6 Apr, Mw 7.9, B (pp. 11, 16) | 6 Apr 12:07 PM (16:07 GMT), 8.3 (p. 7) | 1943-04-06 16:07:15, −30.75 −72.00, no depth, Mw 8.2 P&S, G&R location (p. 14) | – | Mw 7.9 (Beck et al.) against 8.2–8.3 |
| 1945 central Chile | Mw 7.1, intraslab (p. 9) | – | 1945-09-13 11:17:11, −33.25 −70.50, 100 km, mB 7.0 ABE1 (p. 14) | Ley09b: Ms 7.1, 70 km (p. 1) | mB 7.0 against Mw 7.1; depth 70 or 100 km |
| 1927 "Mendoza" | Mw 7.2, intraslab, ~32.45S 69.7W (Fig. 6) | – | 1927-04-14 06:23:30.3, −32.48 −69.68, 35 km, mB 7.2 ABE1 (p. 11) | – | intraslab class against EV02 depth 35 km |
| 1949 Magallanes | – | 17 Dec 11:06 AM (15:06 GMT), 7.5 (p. 7) | 1949-12-17 06:53:30 and 15:07:55, both −54.00 −71.00, Mw 7.8 P&S (p. 15) | B18: two M ~7.7, 8 h apart (p. 2) | L04 has one shock, 7.5; EV02 two at 7.8 |
| 1950 Calama | Mw ~8.0, intraslab ~100 km, ~24.15S 67.85W (p. 5, Fig. 4) | – | 1950-12-09 21:38:48, −23.50 −67.50, 100 km, mB 7.7 ABE1 (p. 15) | B18: M 8.0 (p. 2); Ley09b: Ms 8.0, 90 km (p. 1) | mB 7.7 against Mw/Ms 8.0; ~0.65° apart |
| 1953 Chillán | – | 6 May 1:18 PM (17:18 GMT), 7.5, 60 km (p. 7) | 1953-05-06 17:16:50, −36.50 −72.60, 64 km, mB 7.5 ABE1, ISS location (p. 16) | – | consistent |
| 1958 Las Melosas | Mw 6.3, crustal, ~33.85S 70.2W (Fig. 6) | – | below M 7 | C25: 04-09-1958, −33.832 −59.958, 15 km, Mw 6.8 (p. 10); B18: M 6.9, < 10 km (p. 2) | Mw 6.3 against 6.8–6.9; C25 longitude ~10° east of the valley |
| 1960-05-21 Concepción | Mw 8.1, C, 10:02:52, 37.17S 72.96W (p. 14) | 21 May 6:02 AM, M 7.9 (p. 7) | 1960-05-21 10:02:54.1, −37.83 −73.38, 12 km, Mw 8.2 P&S (p. 16) | – | EV02 epicentre ~0.7° south of RM18 (Cifuentes); M 7.9–8.2 |
| 1960-05-22 foreshock | Ms 7.8 (p. 14) | 2:56 PM, M 7.9 (p. 7) | 1960-05-22 18:56:04.0, −38.15 −72.98, 35 km, Mw 7.9 P&S (p. 16) | – | 0.1 |
| 1960 Valdivia | 22 May, Mw 9.5, ~37.6S 74.0W (p. 16, Fig. 6) | 3:11 PM (19:11 GMT), 8.3–9.6, reference Mw 9.6 (pp. 7–8) | 1960-05-22 19:11:17.5, −38.29 −73.05, 35 km, Mw 9.6 P&S (p. 16) | P24, B18, Ley09b: Mw 9.5 | Mw 9.5 against 9.6 |
| 1960-06-06 Aysén | slow event, Mw 7.7, probably LOFZ (p. 14) | – | 1960-06-06 05:55:49.1, −45.70 −73.50, 15 km, Mw 7.2 P&S (p. 16) | C25: −45.785 −72.889, 15 km, Mw 7.7, crustal (p. 10); R18: Mw 7.7 (p. 2) | Mw 7.7 against 7.2; ~0.4° apart |
| 1965 La Ligua | 28 Mar, Mw 7.4, intraslab, ~32.4S 71.2W (p. 11) | – | 1965-03-28 16:33:16.7, −32.49 −71.21, 71 km, mB 7.4 ABE1 (p. 17) | Ley09b: Ms 7.1 (abstract) or 7.5 (intro), 70 km (p. 1) | type mB in EV02; Ley09b inconsistent |
| 1966 Taltal | 28 Dec, Mw 7.7, B in Table 1, C in text (pp. 9, 16) | – | 1966-12-28 08:18:07.2, −25.50 −70.66, 30 km, Mw 7.7 P&S (p. 17) | – | class only |
| 1967 Tocopilla | 21 Dec, Mw 7.4, C (p. 16) | – | 1967-12-21 02:25:24.7, −21.86 −69.95, 45 km, Mw 7.4 P&S (p. 17) | S23: M 7.4, > 40 km (p. 11) | none |
| 1971 La Ligua | 9 Jul, Mw 7.8, C (p. 16) | – | 1971-07-09 03:03:19.8, −32.56 −71.08, 59 km, Mw 7.8 P&S (p. 18) | – | none (EV02 depth 59 km for an interface event) |
| 1975 Arauco | 14 Oct, Mw 7.7, C (p. 16) | – | 1975-05-10 14:27:43.6, −38.21 −73.00, 30 km, Mw 7.7 P&S (p. 19); no Chilean M ≥ 7 in Oct 1975 | – | date: 14 Oct against 10 May |
| 1981 outer rise | 16 Oct, Mw 7.2 (p. 11) | – | 1981-10-16 03:25:43.1, −33.20 −73.05, 32 km, Mw 7.1 HRV (p. 20) | – | 0.1 |
| 1983 Copiapó | Table 1: 4 Nov, Mw 7.4; text: 4 Oct, Mw 7.7 (pp. 9, 16) | – | 1983-10-04 18:52:15.8, −26.54 −70.50, 24 km, Mw 7.7 HRV (p. 20) | – | RM18 Table 1 date and Mw |
| 1985 Valparaíso | 3 Mar, Mw 8.0 (p. 16) | – | 1985-03-03 22:47:08.4, −33.14 −71.76, 35 km, Mw 8.0 HRV (p. 20) | P24 8.0 | none |
| 1987 Antofagasta | 5 Mar, Mw 7.6 (p. 9) | – | 1987-03-05 09:17:05.1, −24.40 −70.10, 46 km, Mw 7.6 HRV (p. 20) | – | none |
| 1995 Antofagasta | 30 Jul in Table 1, 31 Jul in text, Mw 8.0 (pp. 9, 16) | – | 1995-07-30 05:11:24.5, −23.34 −70.26, 41 km, Mw 8.0 HRV (p. 21) | S23: Mw 8.1 (p. 12) | RM18 text date; Mw 8.0 / 8.1 |
| 1997 Punitaqui | Mw 7.1, intraslab (p. 11) | – | 1997-10-15 01:03:35.2, −30.89 −71.15, 62 km, Mw 7.1 HRV (p. 22) | Ley09b: 58 km (p. 1) | none |
| 2005 Tarapacá | 13 Jun, Mw 7.8, intraslab ~100 km (p. 5) | – | – | E12: centroid 94.5 km, M0 5.3 × 10²⁷ → Mw ≈ 7.8 (p. 6); B18: M 7.7 (p. 2) | 7.7 / 7.8 |
| 2007 Tocopilla | 14 Nov, Mw 7.8, C (p. 16) | – | – | E12: M0 4.8 × 10²⁷ → Mw ≈ 7.7, 37.6 km (p. 6); P24 7.7; S23 7.8 | 7.7 / 7.8 |
| 2014 Iquique | 1 Apr, Mw 8.2, B (p. 16) | – | – | S23 and P24 figures 8.1; R18 8.2 | 8.1 / 8.2 |
| 2014 Iquique aftershock | 3 Apr, Mw 7.7, C (p. 16) | – | – | R18 7.7; B18, S23 7.6 | 7.6 / 7.7 |
| 2015 Illapel | 16 Sep, Mw 8.3 (p. 16) | – | – | R18 8.36 (its M0 gives 8.44); B18 8.4 and 8.3 | see open points |

The other RM18 Table 1 and Table 2 events (2010 Maule Mw 8.8, 2012 Constitución 7.2, 2016 Chiloé 7.6) agree with the values in P24, E12 and R18. The two Taltal events RM18 calls "Ms close to 7 (Centennial)" (1909-06-08, 1936-07-13) are Mw 7.2 and 7.1 P&S in EV02 (pp. 8, 12). EV02 also has shallow M ≥ 7 events that RM18 does not discuss, with mB as the magnitude: 1918-05-20 −28.90 −71.89 mB 7.6, 1934-03-01 −40.92 −72.88 mB 7.3, 1939-04-18 −27.14 −70.71 mB 7.3 (pp. 10–13).

**Before 1900** (RM18 against L04; C25 printed values only where given).

| event | RM18 | L04 | note |
|---|---|---|---|
| 1647 Santiago | most probable historical intraslab intermediate-depth event (p. 16) | 13 May, ~8, crustal source (range fault or San Ramón) (p. 3) | RM18 cites L04 for an interpretation L04 does not make |
| 1730 | megathrust > 600 km, M > 9.0 (pp. 4, 11) | 8 Jul, 8.5–9 (p. 4) | C25: CERESIS Mw 8.74 replaced by 9.1–9.3 (p. 7) |
| 1751 | M ~9.0 (p. 9) | 25 May, 8.5 (p. 4) | 0.5 |
| 1819 Copiapó | "probably smaller" than L04's 8.5 (p. 9) | 3, 4, 11 Apr, 8.5 (p. 5) | – |
| 1837 | larger than 8, ~500 km (p. 14) | 7 Nov, 8 (p. 5) | RM18 cites Abe Mt 9¼ |
| 1859 / "1959" Copiapó | "5 October 1959", ~7 (p. 9) | 5 Oct 1859, 7.5 (p. 6) | RM18 year probably a typo |
| 1877 | giant; cites Lomnitz (1970) 8–8.5, Abe Mt 9.0, Kausel 8.9, Comte and Pardo 8.7 (p. 7) | 9 May, 8 (p. 6) | L04 (2004) gives 8, not 8–8.5 |
| 1768 / 1786 Pica | proposed intraslab; > 7.7 (Comte and Pardo) (pp. 1, 6–7, 16) | not listed | year inconsistent inside RM18 |
| 1604, 1639 | – | 1604 Arica 24 Nov, 8–8.5 (p. 3); no 1639 | C25 Table 8 moved both to 01-12 with the same Mw 7.37 and near-identical epicentres (p. 10) |
| 1615, 1880 | cite Lomnitz 7.5 (pp. 6, 11) | 7.5 (pp. 3, 6) | agree |
| 1868 | "Southern Perú" megathrust (Fig. 1) | Arica 13 Aug, 8.5, epicentre near Islay (p. 6) | S23: Mw 8.5–8.8 (p. 6); CERESIS has it twice, with two epicentres (A13 p. 49) |

### 6. Open points

Against DECISIONS, LEARNINGS and PREFERENCES:
- **DSZ "possibly only in the intermediate-depth slab" (DECISIONS, Classification).** In 19–24°S the two planes are separate only above ~80–90 km. The lower plane starts at ~45–50 km and both merge into one cluster at 80–120 km (S18 p. 13; S23 p. 19, p. 24). In central Chile the lower plane starts at 50 km and merges at 100–120 km (Marot p. 4). So the DSZ overlaps the shallow in-slab range (slab top < 50 km), the case DECISIONS keeps open. It is documented only north of ~32.5–35°S, and the lower plane is patchy along strike.
- **Separation of the planes against catalogue depth errors.** About 20 km, against ±10–15 km for EHB (E98 p. 21) and 25 km nominal for ISC-GEM depths without phases (B15 p. 7). Only local catalogues resolve the planes (Hernández-Soto p. 4; Marot p. 10). Potin gives no per-event depth error.
- **In-slab Mmax candidates (DECISIONS, In-slab).**
  - "Santiago 1647 M8.4": L04 gives ~8 and suggests a crustal source (range fault in the coastal batholith or San Ramón) (L04 p. 3). RM18 calls 1647 the most probable historical intraslab event and cites L04 for it (RM18 p. 16).
  - "Pica 1768": RM18 writes 1768 in sections 3.1.3 and 3.1.5.1 but 1786 in the abstract and p. 16. L04 lists neither year (it has Copiapó 1796).
  - 1939 Chillán: Mw 7.8 (RM18 p. 9), 8.3 (L04 p. 7), Mw 7.7 P&S (EV02 Table 1, check PDF), Ms 7.8 (Ley09b p. 1).
- **Large intra-arc event (DECISIONS, Crustal: Kanamori > 7.5, Aysén 1960?).** RM18 p. 14 and R18 p. 2 describe a 1960 Aysén slow event, Mw 7.7 (Kanamori and Rivera 2017), probably on the Liquiñe-Ofqui fault. C25 Table 7 lists 1960-06-06, 45.785°S 72.889°W, 15 km, Mw 7.7 as crustal (C25 p. 10). EV02 Table 1 lists 1960-06-06 05:55:49.1, 45.70°S 73.50°W, 15 km, Mw 7.2 P&S (check PDF). The event exists; its Mw is 7.7 from long-period data against 7.2 in P&S.
- **Cabello's mb conversion (LEARNINGS).** The paper prints Mw = 1.04·mb − 0.02 (pooled CSN-USGS-GCMT) and 1.03·mb + 0 (GCMT); no 1.03·mb + 0.28 (C25 p. 8). At mb 5, the published NEIC mb relations give Mw 5.08–5.14 (L23 p. 8; W16 p. 18), against 5.43 from the line found in the file. This confirms that the file departs from both the paper and the literature.
- **Cabello pass-through.** Mc, Md and m at any size, and any native magnitude outside an equation's range, go into C25 as Mw unchanged (C25 p. 3, p. 10). This is wider than the LEARNINGS line ("Md, Mc and unspecified m are taken as Mw").
- **ISC mb saturation (LEARNINGS "−0.4 at Mw 5.5–6.5").** From L23 ISC (p. 6), mb − Mw ≈ −0.19 at Mw 5.5 and −0.43 at Mw 6.5. The −0.4 holds near 6.5 only.
- **Default depths (LEARNINGS).**
  - "ISC-GEM 15–35 km" is not stated in any ISC-GEM paper: B15 describes setting-based nominal depths, and S17 gives ISC defaults of 10 / 35 km plus cell depths. Check in the files (depth flag C, no depth phases).
  - Additional defaults to flag: GCMT 10 km in 1981–1985 (E98 p. 12) and the 12 km floor (E12 p. 5); ISC-EHB 10 / 15 km and fixes in 10 km steps (W18 p. 3–4); pre-rebuild ISC 10 / 15 / 33 km (E98 p. 14).
  - Centennial Table 1 shows repeated 35, 25 and 15 km (check against the isol flags in CENT.CAT).
- **Dates of large events (LEARNINGS).**
  - Arauco 1975: RM18 Table 1 gives 14 October 1975 (p. 16). EV02 Table 1 has 1975-05-10 14:27:43.6, 38.21°S 73.00°W, 30 km, Mw 7.7 (p. 19, checked on the image) and no Chilean M ≥ 7 event in October 1975.
  - Mejillones 1994: RM18 gives 12 October 1994, Mw 6.2 (p. 9).
  - Copiapó: RM18 p. 9 writes "5 October 1959"; L04 has 5 October 1859, M 7.5 (p. 6). cat_handler_2 DECISIONS 30 checked a "Copiapó 1959" against this paper; the paper value is probably a typo for 1859.
- **RM18 Table 1 against its own text.**
  - 1918 Copiapó: 4 Dec in Table 1, 18 Dec in the text; L04 and EV02 give 18 Dec and 4 Dec respectively.
  - 1983 Copiapó: Table 1 4 Nov, Mw 7.4; text 4 Oct, Mw 7.7 (P&S), Centennial location.
  - 1995 Antofagasta: 30 July in Table 1, 31 July in the text.
  - 1966 Taltal: domain B in Table 1, deeper interface (C) in the text.
  - Typos "1985" for 1995 and "1996" for 1966 on p. 7.
  - Since PREFERENCES takes Mw and class from RM18, these need one reading each in A6.
- **Riquelme Illapel 2015.** M0 5.71 × 10²⁸ dyn·cm gives Mw 8.44 with HK79, not the stated 8.36. The strike, dip and rake (346 / 11.2 / 99.0) repeat the Iquique aftershock's (R18 p. 9). Do not take Illapel from R18.
- **Completeness statement reversed in S13.** S13 p. 4 prints "Mw 5.6 before 1964 to Mw 6.4 after". DG15 (p. 1, p. 14) and DG18 (p. 17) give 5.6 from 1964 and ≥ 6.15 before. PREFERENCES section 3 follows DG15, correctly.
- **PREFERENCES 1904–1963, epicentre "Centennial, then ISC-GEM".** The Centennial is not relocated for 1904–1917 and 1943–1955 (EV02 p. 23), while ISC-GEM relocated every event (B15 p. 1). For those years the Centennial epicentre is a G&R, Abe or ISS value without depth.
- **Q1 framing (PREFERENCES section 4).** The Centennial's pre-1976 Chilean "Mw" are P&S (1992) values, and intermediate-depth events carry Abe mB, not Mw (EV02 Table 1). Before 1964, ISC-GEM lacks deep events that have no literature Mw (DG15 p. 12).
- **Mw definition.** HK79 uses −10.7 (dyn·cm); the IASPEI form is 0.033 lower (L14 p. 2). Check which constant GCMT, ComCat, CSN and ISC-GEM use before mixing them.
- **GCMT as the reference (DECISIONS, Catalog).** GCMT Mw < 5.4 may be overestimated (L23 p. 2; L14 p. 5). Teleseismic proxies overestimate Mw in subduction zones on average (L14 p. 6). A Chile calibration on GCMT pairs below ~5.4 inherits the first.
- **Slab2 thickness (DECISIONS, In-slab: depths from Slab2 top and thickness).** Thickness, dip and uncertainty grids are described only in the Slab2 supplement (doi 10.5066/F7PV6JNV), not in our refs. Hernández-Soto (p. 19) and RH26 (p. 12) find intraslab seismicity deeper than Slab2 below ~100 km, or locally different.
- **CSN completeness gap.** CSN data for Jan–Sep 2000 are permanently lost (P24 p. 4). Only 310 events at 44–46°S in 1982–2020, and a low rate near 26°S is a coverage artefact (P24 p. 4).
- **Potin's magnitude.** No conversion is documented; the catalogue mixes Mc (to 2002), ML, Brune Mw and Mww (P24 p. 4). Its codes `W` and `ww` (WORKLOG A2) are presumably the Brune Mw and the W-phase Mww; the paper does not give the codes.
- **Potin dates.** The Mc maps are described as 2010 to "mid-2022" although the catalogue ends in mid-2020 (P24 p. 5). RH26 quote Potin as 1985–2020 (p. 8).
- **Cabello matching rule.** CSN locations are replaced by Potin's only when the origin times match to the second (C25 p. 7–8). This is irrelevant to us after 1900, except as a warning for A3.
- **EV02 Table 1.** The 106 Chilean rows match the page images. Rows elsewhere in the world remain OCR (see `refs/catalogs/txt/INDEX.md`).
