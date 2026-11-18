# CAT to FITS and IS, 18 Nov: deep-focus events (next catalogue, not 17g)

## What changed
- `catalog/classify.py`: an in-slab event with a measured depth below 300 km, outside the Jujuy nest, takes the sub-class `deep_focus` (`classify.DEEP`; Frohlich 2006). Not run: the frozen catalogue 17g still labels these events `intraslab_intermediate`. It acts at the next run of `classify.py` (DECISIONS › Classification).
- In 17g, inside the domain: 14 events of Mw ≥ 4.5 at 300–422 km under southern Bolivia (65–66° W, 17–22° S), 6 of Mw ≥ 5, 3 of Mw ≥ 6 (2019-03-15 6.4 at 372 km, 2008-10-12 6.2 at 353 km, 2003-07-27 6.0 at 345 km). 1946-08-28 (574 km) and 1947-01-29 (566 km) are outside the domain (63° W) and reach no fit.

## For FITS
- `gr.CLASSES` picks `intraslab_intermediate` by name, so `deep_focus` events drop out of every fit once the catalogue is rerun. Until then, on 17g: `depth > 300` among the intermediate events is the same set.
- `decluster.FAMILY` uses `w_inslab` for the in-slab family, so deep-focus events stay in the declustering pool; harmless for the fits.

## For IS
- `model/inslab/run.py` keeps every in-slab event except the Jujuy nest for the spatial pattern (line 82). Add `sub_inslab != "deep_focus"` there (or `depth <= 300` on 17g) so deep-focus events do not enter the in-slab pattern. Not edited by CAT.
