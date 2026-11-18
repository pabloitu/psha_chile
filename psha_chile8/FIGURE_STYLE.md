# FIGURE_STYLE: how figures look in psha_chile8

One place for the figure rules, gathered on 17 Nov from CLAUDE.md, DECISIONS (Figures), `hazard/FIGURE_STYLE_tornado.md` and Pablo's stated preferences. Kind-specific details stay in their own files (tornado: `hazard/FIGURE_STYLE_tornado.md`).

## Tools
- Draw with pituPLOTS (installed editable in `psha_renta`; record its commit in the WORKLOG entry of the run).
- `palette.py` at the repo root: `apply(size=...)` sets the Ubuntu font and sizes; `CLASS_COLOR` and `CLASS_NAME` give one colour and one display name per class; `BAND` colours magnitude bands and `SERIES` gives colours for other series, the same in catalogue, fit and hazard figures. Never put code names (`intraslab_shallow`, `w_crustal`) in legends or labels.
- Statistics plots: pituPLOTS `darkgrid` (gray background).
- Maps: the gray basemap `data/basemaps/basemap_chile_gray/basemap_gray.tif`.
- Static figures (PNG, and PDF for the paper), not HTML viewers, unless a brief asks.

## Look
- No figure titles: the slide or caption carries the message. A short tag in a corner (city, unit) is fine.
- Few labels, concise axis labels with units, comfortable margins. No text boxes or arrows with notes.
- Large events drawn on top of small ones; markers scaled by magnitude.
- Legends short; one row below the axes when there are several entries.
- Comparisons: hazard curves (or the same figure) against a baseline, rather than tables alone.

## Maps and sections
- Sections perpendicular to the Nazca trench (`data/shapefiles/sam_nazca_trench.shp`), landward extent capped at 400 km, near-proportional depth-to-distance axes; only events of M ≥ 7 labelled. Slab2 top and the 50 / 100 / 200 km contours where useful.
- Classes coloured by `palette.CLASS_COLOR`; events of other classes grey when one class is the subject.

## Where figures live
- Figure code reads only frozen outputs (`CURRENT.md`) and never computes model results.
- Trials and one-off comparisons: `drafts/<idea>/` (not committed).
- Figures of a section's report: that section's `figs/` (dated subfolder per run).
- Paper and supplement figures: listed in `FIGURES.md` with their script; when a draft is chosen it becomes one script in the code style of CLAUDE.md.
- Catalogue: the paper and supplement figures are written by their scripts straight into `catalog/FIGURES/<type>/` (`maps`, `magnitudes`, `rules`), one place to find them; checks and test figures stay in `catalog/figs/`. A new catalogue figure for the paper goes into the fitting type folder (or a new one) and gets its `FIGURES.md` row.
- A figure copied from elsewhere (a report, an older deck) stays as it is unless Pablo asks.
- Before rerunning a script that overwrites figures, copy the previous ones to a dated subfolder.

## Kind-specific styles
- Tornado per city, full tornado, matrix: `hazard/FIGURE_STYLE_tornado.md`.
