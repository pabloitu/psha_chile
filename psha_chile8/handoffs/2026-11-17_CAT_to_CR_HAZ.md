# CAT to CR and HAZ, 17 Nov: final catalogue and class colours

## For CR (crustal)
- The final catalogue is `catalog/frozen/2026-11-17f/` (CURRENT.md); rebuild when FITS has refitted on it.
- 1952-06-11 San Juan (Mw 6.8) is now crustal (MASCSN26 p. 117); Las Melosas 1958 is Mw 6.8 (was 6.3); Pichilemu 2010-03-11 15:06 is crustal at Mw 6.2.
- Pablo, 17 Nov: 1879-02-02 Magallanes (Ms 7–7.5, Mw 7.0 in the catalogue, Patagonia; Lomnitz 2004; MASCSN26 p. 121) is too big to ignore in the crustal source model; the Magallanes–Fagnano sources should account for it next to the 1949 doublet.
- The focal-mechanism map (`catalog/fig_mechanisms.py`) leaves room for a fault legend in the southern panel; faults are to be added there.

## For HAZ (and every figure)
- `palette.CLASS` holds the class colours (Pablo, 17 Nov; DECISIONS › Figures): interface steel blue, in-slab dark red, crustal forearc yellow / arc olive / backarc yellow-green / Patagonia brown, outer rise violet. `palette.FAMILY_COLOR` gives one colour per family for figures that mix families.
- `hazard/shares.py`, `trees.py`, `tornado_alt.py`, `tornado_final.py`, `tornado_prelim.py`, `tornado_trial.py` colour the families with `CLASS_COLOR["interface"]`, `["intraslab_intermediate"]`, `["forearc"]`; they should read `palette.FAMILY_COLOR["interface"]`, `["inslab"]`, `["crustal"]` instead. Not edited by CAT.
- `palette.BAND`: M ≥ 7 is red (#c0141c).
