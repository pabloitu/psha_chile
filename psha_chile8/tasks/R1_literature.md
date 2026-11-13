# Task R1: literature review of the catalog references

Read first: `CLAUDE.md`, `DECISIONS.md` (Catalog, Classification), `catalog/PREFERENCES.md`, `REFERENCES.md`, `refs/catalogs/txt/INDEX.md`.

## Goal

One file, `psha_chile8/catalog/LITERATURE.md`, holding everything from the 44 papers in `refs/catalogs/` that the catalog rebuild (A2–A8) needs, so nobody has to reopen the PDFs for routine questions. Work from the text files in `refs/catalogs/txt/`. Open the PDF page as an image only where a table or equation is garbled in the text.

## Groups (one parallel helper per group is fine)

1. **Source catalogues:** engdahl_villasenor_2002, storchak_etal_2013, storchak_etal_2015, digiacomo_etal_2014, bondar_etal_2015, digiacomo_etal_2015, digiacomo_etal_2018, storchak_etal_2017, digiacomo_etal_2016, weston_etal_2018, engdahl_etal_1998, dziewonski_etal_1981, ekstrom_etal_2012
2. **Chilean catalogues and networks:** cabello_etal_2025, potin_etal_2024, barrientos_csn_2018, riquelme_etal_2018, riedel-hornig_etal_2026, sippl_etal_2023, munchmeyer_etal_2020
3. **Historical:** ruiz_madariaga_2018, lomnitz_2004, giesecki_2004, albini_etal_2014, albini_etal_2013 (South America / Chile parts only)
4. **Magnitude homogenization:** castellaro_etal_2006, lolli_gasperini_2012, lolli_etal_2014, lolli_etal_2023, weatherill_etal_2016, scordilis_2006, gasperini_etal_2013, hanks_kanamori_1979, poulos_etal_2019, leyton_etal_2009
5. **Slab and double seismic zone:** comte_etal_1999, rietbrock_waldhauser_2004, dorbath_etal_2008, marot_etal_2013, sippl_etal_2018, lu_etal_2021, hernandez-soto_etal_2026, hayes_etal_2018, leyton_etal_2009b

## Card per paper

```
### <author year>: <short title>
- Ref: full citation, DOI (from page 1)
- What it is: 1–2 lines
- Use for us: which step (A2 sources, A3 matching, A4 preferences, A5 magnitudes, A6 large events, A7 classification) and why
- Coverage: time, area, magnitude thresholds, completeness as stated
- Methods: location / depth / magnitude procedure, in a few lines
- Numbers to keep: thresholds, relations with coefficients and validity range, uncertainties, counts (each with "p. N")
- Chile specifics: events, regions, values about Chile
- Known problems / caveats stated by the authors
```

Keep cards short (10–25 lines). Copy numbers and coefficients exactly, with the PDF page (`p. N` = the `=== page N ===` marker). Paraphrase text; no long quotes. Where a value comes from the OCR'd Table 1 of engdahl_villasenor_2002, or from the garbled old texts (comte 1999, dziewonski 1981, hanks 1979), mark it "(check PDF)".

## Synthesis (after the cards, in the same file)

1. **Source order.** Per period and property of `catalog/PREFERENCES.md`: what the papers say about quality (location accuracy, depth reliability, magnitude type and homogeneity). Evidence for the two open questions there (Centennial vs ISC-GEM magnitudes 1904–1999; events below the global thresholds before 1982). Facts and their pages, no decisions.
2. **Magnitude homogenization.** The candidate methods (OLS, GOR / chi-square, curvilinear models, proxy-Mw composition as in ISC-GEM), what each paper found about their biases, and the relations available for each native scale we will have (ISC mb, NEIC mb, Ms, CSN ML / Mc / Mw, Md, CERESIS magnitudes), with validity ranges. End with 2–3 candidate approaches for A5 and what each needs from our data. No choice.
3. **Depths.** How each source fixes or flags depths, default values mentioned, depth quality classes (EHB L1–L3), what is said about historical depths.
4. **Double seismic zone.** Per study: latitude range, depth range of each plane, plane separation, where the planes merge, data used. A table, then where along Chile a DSZ is documented and where not. Input for A7.
5. **Large events.** Where Ruiz and Madariaga (2018), Lomnitz (2004), Cabello (2025) and Engdahl and Villaseñor (2002) disagree on magnitude, date or location of a Chilean event, list them.
6. **Open points.** Anything a paper says that contradicts our DECISIONS or LEARNINGS, or that we must verify.

## Also

- Update `REFERENCES.md`: file names as they are in `refs/catalogs/`, DOIs from page 1 (remove "DOI to check" where confirmed), tick the pdf column, add engdahl_villasenor_2002 and giesecki_2004 (Giesecke 2004, CERESIS), and correct any wrong citation details.
- Do not read or write outside `psha_chile8/` and `refs/catalogs/`. No git commands. No web searches: the texts are the source.

## Done when

`LITERATURE.md` has a card for every paper in the index and the six synthesis sections; `REFERENCES.md` is updated; the WORKLOG entry lists papers that were hard to read and anything surprising for our decisions.
