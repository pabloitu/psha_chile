# Tornado figure: style agreed with Pablo (16 Nov 2026)

Producing script: `hazard/tornado_prelim.py` (one figure per city, `hazard/out/tornado_prelim/<city>.png` and `.csv`). Reads `hazard/out/tornado/tornado.csv` (written by `hazard/tornado_final.py`) and the GMM-set jobs. Reuse it as the template for any figure of this kind.

## Layout
- **Bars and order:**
  - Vertical bars, one column per tornado axis (a "level" of the logic tree), ordered from the left by the largest change of the total PGA 475 yr.
  - Only the axes that change the total by ≥ 1 % are shown, at most 18.
- **Thick bar:** the change over **all tectonic settings**: the family's change combined in rate space with the references of the other families.
- **Pale thin bar behind it:** the change **within tectonic setting**, i.e. the family alone. This is the legend pair agreed after several tries: "total hazard" and "family alone" were confusing.
- **Black dots:** every branch, the reference included. The reference is drawn at 0 like any other branch and labelled with its value (e.g. "with faults: yes", "15 km", "GEM", "multi-fault"). The interface scaling axis has no reference label: its reference is the three relations at 1/3.
- **Hollow diamond, thin dark edge:** the **average** of the axis. The hazard curves of its branches and its reference are averaged with equal weights, then PGA 475 is read. For a GMM axis it is the set as a whole.
- **GMM axes:** one per set and tectonic setting (GMM-1R, GMM-FIT, GMM-CSN, GMM-GEM). The branches are the single models of the set, read from the realizations of the set job; no single-GMM jobs are needed. There is no separate "GMM alone" axis.
- **Grey band ±5 %:** the branch rule. A black zero line.
- **Below the lowest level:** a branch whose total falls below the lowest computed level (0.005 g) is drawn at that bound and labelled "(below 0.005 g)", never at 0.

## Labels
- **Branch labels:**
  - placed on every axis shown (up to 18), to the right of the column;
  - spread vertically so they never overlap, each with a thin grey leader line to its dot;
  - rows that coincide share one label.
- **Axis names:**
  - prefix IF ·, IS ·, CR ·; the colour also gives the family;
  - names that say what changes: segmentation, rate model, geodetic coupling χ, (a, b) uncertainty, b per segment, MFD shape, declustering, rupture scaling, GMM truncation, spatial pattern, with faults, fault database, fault linkage, max. jump distance, aseismic coefficient ψ, seismogenic thickness, LOFS secondary traces, class Mmax pad, fault Mmax pad, background rates, background MFD.
- **Branch names:** short.
  - full / GK74 / NN; tapered / truncated; ML / 5th / 95th; own / shared / whole-margin b; 2.5σ / 3σ / 4σ;
  - single-fault / multi-fault (not "segmented", which the interface uses);
  - GEM / CSN / CSN-Ṁ₀ for the fault databases; GMM-CSN, never MASCSN, in labels.
  - GMM model names short: AG20, Parker, Kuehn, Montalva17, Zhao16, Youngs97, Idini17, BCHydro, ASK14, …
- **No figure title.** The city name sits in the upper-left corner of the axes.

## Fonts and look
- **Fonts** (`palette.apply(size=16)`): city 22, y label 18, axis names 16 (slanted 50°), legend 14, branch labels 11.
- **Look:**
  - pituPLOTS `darkgrid`;
  - family colours from `palette.CLASS_COLOR` (interface, in-slab intermediate, crustal forearc);
  - Ubuntu font;
  - legend in one row below the axes.
- **Size:** width about 1.15 in per column + 2.5 in, height 9.5 in, 170 dpi.

## Iterations that did not work (avoid)
- Two bars side by side (family alone and combined): hard to read.
- A bracket for the family-alone range: it reads as an error bar.
- An outline bar: busy where the outlines are wide.
- Separate "GMM alone" and "GMM set" axes: confusing; one axis per set is clearer.
- A white diamond only on GMM axes: draw the average on every axis instead.
- Reference labels in italics with a white box: write the reference as a normal branch.

## Full tornado for review (`hazard/tornado_full.py`, agreed 16 Nov)
- Every level, none left out; horizontal bars, levels as rows, grouped interface → in-slab → crustal (coloured square and bold group name), each group ordered by the change of the total.
- Same marks as the slide figure; branch labels above each bar, spread along x with leader lines; level names in dark text.
- x axis capped at ±40 %: a bar beyond it ends in an arrow at the edge with its value written inside the axes ("within" for the pale bar).
- Size 13 in wide, 0.52 in per row; fonts: city 22, group 16, level names 13, branch labels 9.5, legend 13; PNG and PDF.

## Matrix (`hazard/tornado_matrix.py`)
- Cities north to south as rows; levels as columns grouped interface → in-slab → crustal under coloured bands, each group ordered by the mean over the cities.
- Cell = largest |change| of the total PGA 475 yr (all tectonic settings) over the branches of the level (%), Reds capped at 30, value written. One panel only: no "within tectonic setting" matrix (Pablo, 16 Nov).

## Which figure for what (Pablo, 16 Nov)
- **Reduced tornado** (`tornado_prelim.py`, slides): vertical bars, levels ordered by their impact on the total over all tectonic settings, mixed across families; levels below 1 % left out, at most 18; branch labels on every axis shown.
- **Full tornado** (`tornado_full.py`, review with co-authors): every level, horizontal bars, grouped by tectonic setting (interface → in-slab → crustal), ordered by impact inside each group. Produce it for all cities once the model is final.
- **Matrix** (`tornado_matrix.py`): cities × levels, grouped by tectonic setting like the full tornado, total change only.
- All three use the same level and branch names, family colours and the "all tectonic settings / within tectonic setting" wording.

## Hazard curves per city (`hazard/curves_city.py`, 16 Nov)
- One slide figure per city (16:9, 12 × 6.75 in; title 24, axis labels 18, ticks 15, legend 15 outside on the right, PGA 475 value in a white box) and a 4 × 4 grid of all cities for the report (legend in the empty cells): PGA (g) against annual probability of exceedance, both log; x 0.005–3 g, y 1e-5–0.2.
- House style (as psha_chile7 `hazard/post.py` and the other psha_chile8 figures): pituPLOTS `darkgrid` (grey background, white major and minor grid, no spines), axis labels "PGA $[g]$" and "Probability of exceedance - 1 year", city as a left-aligned title, legend in a white box without edge.
- Family reference curves in the family colours (lw 2); total of the three references in black (lw 2.4).
- Epistemic spread from the tornado: a band per family = envelope of every tornado branch of that family (source rows, single GMMs of each set, truncation), alpha 0.3 as the psha_chile7 envelopes; the total band = envelope of every branch of every family combined with the references of the other two, grey.
- 475-yr line black dashed (lw 0.8) with "10% in 50 yr" at the left, as psha_chile7; the total PGA 475 marked with a dot and its value in g.

## Contribution of the tectonic settings (`hazard/shares_bar.py`, 16 Nov)
- One 100 % stacked horizontal bar per city, north to south from the top; share = annual rate of each family over the total rate at the total PGA 475 yr of the references.
- Family colours, thin light gaps between segments, values (%) written inside segments ≥ 6 % (white on blue and red, dark on yellow).
- pituPLOTS `darkgrid` background with vertical grid lines only at 0 / 25 / 50 / 75 / 100 %, no tick marks; legend as coloured squares with names above the bars; the total PGA 475 yr written at the right of each bar, small grey column headers.
- Pablo (16 Nov): few ticks, effort on a clean, stylish look; use this as the model for other summary bar figures.

## House style for every hazard figure (Pablo, 16 Nov)
- Start from the pituPLOTS look used across psha_chile8 and psha_chile7: `darkgrid(ax)` on every axes, Ubuntu font, `palette` colours and display names, legends in a white box without edge or outside below the axes. Keep tick marks minimal and make the figure clean; do not invent a separate look.
