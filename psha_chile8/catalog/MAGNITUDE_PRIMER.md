# Magnitudes: a primer for A5

What the magnitude types are, which catalog carries which, and what "homogenizing to Mw" means. Read this before `LITERATURE.md` section 2. Numbers here are rounded and only illustrative.

## 1. Why there are so many magnitudes

A magnitude is the logarithm of an amplitude, corrected for distance. Each type measures a different wave, at a different period, with different instruments. So each type "sees" a different part of the earthquake, and they disagree, mostly at small and large sizes.

**Mw (moment magnitude)** is different: it comes from the seismic moment M0 = rigidity × fault area × slip, so it measures the size of the rupture itself. It does not saturate and it is what the hazard model uses (ground-motion models, magnitude-frequency distributions, moment balance). Every other magnitude has to be turned into Mw.

**Saturation**: amplitude-based magnitudes stop growing above some size, because the measured wave period is shorter than the rupture duration. Then a bigger earthquake gives about the same value.

## 2. The types

| type | what is measured | distance | grows with Mw up to about | notes |
|---|---|---|---|---|
| **ML** (local, "Richter") | largest S-wave amplitude, period ≈ 0.1–1 s | < ~600 km | 6.5 | needs a regional distance correction; each network has its own |
| **Mc / Md** (coda / duration) | length of the shaking record | local | 5 | cheap, used for small events; poorly tied to Mw |
| **mb** (body wave) | P-wave amplitude, period ≈ 1 s | 20–100° (teleseismic) | 5.5–6 | NEIC and ISC compute it differently; IDC mb runs ~0.5 higher |
| **mB** (broadband body wave) | P-wave, longer periods | teleseismic | ~7.5 | used by Abe for old deep events |
| **Ms** (surface wave) | Rayleigh-wave amplitude, period ≈ 20 s | teleseismic | ~8 | only for shallow events (< 60–70 km) |
| **Mw** | seismic moment from waveform inversion | any | no saturation | GCMT, W-phase (Mww), spectral (Brune) |
| **proxy Mw** | an Mw computed from another type by a conversion | – | as the parent type | what ISC-GEM gives before 1976 |
| **historical M** | damage area, felt area, tsunami | – | – | Ms-like estimates, ±0.5 (CERESIS, Lomnitz) |

## 3. Which catalog carries which

| catalog | per event | types inside |
|---|---|---|
| Cabello (we use before 1904) | one value | historical CERESIS magnitudes, Ms-like, taken as Mw |
| Centennial (1900–1999) | one value, copied from other catalogs | Mw from Pacheco & Sykes or Harvard; Ms (Abe, Gutenberg-Richter); mB (Abe) for deep events |
| ISC-GEM (1904–) | one Mw with uncertainty | direct Mw (GCMT or literature), else a proxy from its own recomputed Ms or mb |
| ISC Bulletin | many values | ISC's own mb and Ms, plus every agency's: NEIC mb / Ms / Mw, CSN (code GUC) ML / Mw, IDC mb / Ms, others |
| ComCat (USGS) | one preferred value | type varies: mb, Ms, Mww, Mwc, ML from regional networks |
| GCMT (1976–) | Mw | complete above about Mw 5.3–5.5 before 2004, 5.0 after |
| Potin (CSN, 1982 – 2020-07) | one value, type changes in time | coda Mc to ~2009, ML from 2000, spectral Mw 1995–2016, W-phase Mww from 2014 |
| CSN (2020-07 –) | one value | ML for small events, Mww for larger ones |

Consequence: in any period, the magnitudes we hold are a mix of types. The mix changes with time (CSN from coda to ML to Mww; NEIC changed Ms in 2013) and with size (small events ML or mb, large ones Mw).

## 4. Converting a type to Mw

A conversion is a relation Mw = f(native magnitude), fitted on **pairs**: earthquakes that have both the native value and a trusted Mw (usually GCMT). Five things decide whether it is right.

1. **Both values have errors.** Ordinary least squares (OLS) treats the native value as exact. Because it is not, OLS flattens the line: converted small events come out too large, large ones too small. That changes b (by 20–40 % in tests). Orthogonal regression (GOR) and chi-square regression (CSQ) allow errors on both axes. They need the ratio of the two error sizes, η. The night run of 4 Nov estimated these errors by *triple collocation*: three agencies measuring the same earthquakes let you separate each one's scatter.
2. **The relation is not a straight line.** Saturation bends it at the top; at the bottom some scales run flat. So the forms used are curves (an exponential) or two straight segments joined at a break.
3. **Few pairs at small sizes.** GCMT has few events below Mw 5–5.5 and may run high there. A relation fitted mostly above 5 and used down to 3.5 is an extrapolation. This is the hard part for us: most of our events are M 3.5–5, and no reliable Mw reference exists there (CSN and USGS Mw differ by ~0.3 at M 4–5).
4. **Selection of the pairs.** Pairs must be matched by time and distance only. Choosing pairs that already agree in magnitude, or cutting on one of the two values, biases the line.
5. **Place, depth and time.** Teleseismic conversions run high in subduction zones on average; local ML depends on the network's calibration and on depth; an agency's procedure can change in a given year. So a relation may need to be split by depth or period.

## 5. One Mw per event

Many events end with several candidate Mw (direct, and proxies from mb, Ms, ML). Two ways to choose:
- **priority**: take the best type available (direct Mw, then Ms proxy, then mb proxy, ...), as ISC-GEM does;
- **weighted mean**: average all proxies, weighting each by its uncertainty. Studies found this gives a more stable b.

Either way, keep each event's uncertainty, and *dither* (spread each value randomly within its 0.1 rounding bin) so that conversions with slope < 1 do not stack values into some bins.

## 6. How we know a conversion works

- Converted values agree with GCMT where GCMT is complete (M ≥ ~5.5).
- Different agencies agree for the same earthquakes after conversion.
- b-value stays the same when the fit floor is raised (a wrong conversion makes b drift with the floor).
- Event rates per magnitude band stay steady across periods where the network did not change.

## 7. The three candidate approaches, in plain words

1. **Take published relations** (e.g. Lolli et al. 2023 for ISC and NEIC mb and Ms). Fast and citable; not calibrated for Chile; nothing for CSN ML, Mc, Md.
2. **Fit our own Chilean relations**, one per agency and type, with orthogonal or chi-square regression. Best fit to our data; needs enough pairs, and the small-size reference problem remains.
3. **Chain**: convert a local type to a teleseismic one first (e.g. CSN ML → mb), then to Mw. Uses many more pairs; but errors and saturation of the middle step carry through. The 4 Nov night run found that ML → NEIC mb → Mw inherits the mb saturation and failed validation.

## 8. What went wrong before (for context)

Cabello's file used Chilean relations from OLS-type fits, applied one relation per type across all sizes, did not follow its own published NEIC mb relation (+0.3 too high), did not handle ISC mb saturation, and passed coda, duration and unspecified magnitudes through as Mw. The 4 Nov night run repaired the worst of it on Cabello's file; we now rebuild from the native magnitudes instead.
