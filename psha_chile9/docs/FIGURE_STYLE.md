# FIGURE_STYLE

Every figure rule in one place. Merged on 18 Nov from psha_chile8 `FIGURE_STYLE.md`, `fits/FIGURE_STYLE_fmd.md`, `hazard/FIGURE_STYLE_tornado.md` and the Figures decisions.

## Tools
- `psha9.common.plots`: the house look. It holds the pituPLOTS palettes (copied), `darkgrid(ax)` (grey background, white grid, no spines), `apply(size=…)` for the Ubuntu font and sizes, the map helpers, and the class colours and names. pituPLOTS itself is not used.
- `CLASS_COLOR` and `CLASS_NAME` give one colour and one display name per class; `FAMILY_COLOR` gives one colour per family for figures that mix families; `BAND` colours magnitude bands; `SERIES` colours other series.
- Never put code names (`intraslab_shallow`, `w_crustal`) in labels or legends.
- Static figures: PNG, plus PDF for paper and supplement.

## Look (every figure)
- No titles. A short tag in a corner (city, unit) is fine.
- Few labels; concise axis labels with units; comfortable margins; minimal tick marks.
- No text boxes or arrows with notes inside the figure: explanations go in the caption.
- Large events drawn on top of small ones; markers sized by magnitude.
- Short legends, in one row below the axes, or in a white box without an edge.
- Statistics and hazard plots: `darkgrid` background.
- Comparisons: curves (or the same figure) against a baseline, not tables alone.

## Colours
- **Classes:** interface steel blue (Antarctic light steel blue); in-slab dark red (shallow lighter, Jujuy nest darker); crustal forearc yellow, arc olive, backarc yellow-green, Patagonia brown; outer rise violet. Events of other classes grey when one class is the subject.
- **Families in mixed figures:** `FAMILY_COLOR` (crustal: the arc olive).
- **Magnitude band M ≥ 7:** red, #c0141c.

## Maps and sections
- **Catalogue maps:**
  - Mercator on the domain without the far-west outer rise and the Scotia events (76.5° W, 56° S);
  - a north and a south panel side by side;
  - events sized by area, 3.5 times per magnitude unit from 2 pt² at Mw 4.5, 55 % opaque;
  - the gray basemap (`data/raw/basemaps/basemap_chile_gray/basemap_gray.tif`).
- **Sections:**
  - perpendicular to the Nazca trench, landward extent capped at 400 km, near-proportional depth-to-distance axes;
  - only events of M ≥ 7 labelled;
  - Slab2 top and the 50 / 100 / 200 km contours where useful.
- **Grids and cells:** drawn as a mesh, not as markers (markers leave white seams).

## Frequency–magnitude panels
- **Cumulative:** observed rate at and above each magnitude (filled points, white edge) and the fit (solid line). Each bin's rate is its count over its own observation time, summed from the top.
- **Incremental:** observed rate per 0.1 bin (open points) and the fit (dashed, smooth in the bin centre, not steps); empty bins not drawn.
- **Uncertainty:**
  - 95 % band of the fit (2.5–97.5 % of the bootstrap of b, rate, corner) around each line, in the line's tone;
  - Poisson 1σ (16–84 %) on the incremental points, as thin pale lines without caps;
  - no bars on cumulative points;
  - no predictive band.
- **Completeness:** each step of the unit's table as a thin dashed grey vertical line at its magnitude edge, with its year written vertically at the top (5 pt).
- **Named events not in the fit:** open circles at their Mw near the bottom, with name and year (5 pt); legend "Named event, not in the fit".
- **No** Mw ≥ 7 band in these panels.
- **Colours:** two tones of the class colour (cumulative × 0.72, incremental + 38 % towards white); several catalogues in one panel: one colour each, cumulative only.
- **Text:**
  - tag: unit name, then $b = 0.94 \pm 0.02$ ("(family)" when b comes from the family) and $M_\mathrm{max}$;
  - x "$M_\mathrm{w}$" with integer ticks, y "Annual rate" on a log scale;
  - axis labels on the outer panels only;
  - legend 6–6.5 pt: Cumulative, Incremental, 95 % confidence, Poisson 1σ, Completeness year;
  - diagnostics such as $N(M \geq 7)$ only in comparison figures.
- **Layouts:**
  - page width 17.5 cm, text 6–7 pt;
  - interface figure 2 × 3 (margin first, then the segments north to south; the sixth cell holds the legend and a map of the segment sources);
  - class figure 2 × 4 (in-slab top row, crustal below); one y and one x range per figure.

## Tornado
- **Reduced tornado (slides):**
  - vertical bars, one column per level, ordered by the change of the total PGA 475 yr; levels ≥ 1 % only, at most 18;
  - thick bar: change over all tectonic settings; pale thin bar behind it: within the tectonic setting;
  - black dots: every branch, the reference at 0 and labelled; hollow diamond: the equal-weight average of the level;
  - grey ±5 % band, black zero line; a branch below the lowest computed level drawn at that bound with "(below … g)".
- **Labels:** branch labels on every level shown, spread so they never overlap, with grey leader lines. Level names say what changes, prefixed IF ·, IS ·, CR ·. Branch names short (full / GK74 / NN; tapered / truncated; ML / 5th / 95th; single-fault / multi-fault; GEM / CSN; GMM-CSN, never MASCSN).
- **Fonts and size** (`apply(size=16)`): city 22, y label 18, level names 16 (slanted 50°), legend 14, branch labels 11. About 1.15 in per column + 2.5 in wide, 9.5 in high.
- **Full tornado (review):** every level, horizontal bars, grouped interface → in-slab → crustal, ordered inside each group. x capped at ±40 % with an arrow and the value beyond it; 13 in wide, 0.52 in per row.
- **Matrix:** cities north to south as rows, levels as grouped columns; cell = largest |change| of the total (%), Reds capped at 30, value written; one panel only.
- **Tried and not used:** two bars side by side; a bracket for the family range; outline bars; separate "GMM alone" axes; italic reference labels in boxes.

## Hazard curves and shares
- **Curves per city:**
  - one 16:9 slide figure per city (12 × 6.75 in) and a 4 × 4 grid for the report;
  - PGA (g) against annual probability of exceedance, both log, x 0.005–3 g, y 1e-5–0.2;
  - family references in family colours, total in black;
  - a band per family from the envelope of its tornado branches, alpha 0.3, the total band grey;
  - 475-yr line black dashed with "10% in 50 yr"; the total PGA 475 marked with its value.
- **Shares of the tectonic settings:**
  - one 100 % stacked horizontal bar per city, north to south;
  - values inside segments ≥ 6 %;
  - vertical grid at 0 / 25 / 50 / 75 / 100 % only;
  - legend as coloured squares above;
  - the total PGA 475 at the right of each bar.

  This is the model for other summary bar figures.

## Presentation figures
- 16:9; larger fonts (as the tornado and the city curves); the same look and colours as the paper figures.
