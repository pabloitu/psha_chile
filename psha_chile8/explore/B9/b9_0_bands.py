"""B9 sensitivity input: the classes with an interface band of ± 10 and ± 20 km. classify.py (the frozen copy) is run
with those settings on the frozen locations and magnitudes; nothing is written under catalog/. Writes
cache/bands.pkl with one set of class weights per band."""
import sys
import time

import numpy as np
import pandas as pd

import b9_lib as L

# catalog/classify.py is identical to the frozen copy, whose relative data paths do not resolve from frozen/
CODE = L.ROOT / "catalog"
BANDS = [10.0, 15.0, 20.0]


def run():
    sys.path.insert(0, str(CODE))
    import classify as C
    c = pd.read_csv(L.ROOT / "catalog/merged/catalog_2026-11-14b.csv", low_memory=False)
    d = L.load()
    out = pd.DataFrame(dict(event_id=d.event_id))
    for w in BANDS:
        g, o, tab = C.run(c, w=w)
        o = o.set_index("event_id").reindex(d.event_id)
        for k, (wc, s, v) in L.CLASSES.items():
            out[f"W_{k}_{w:.0f}"] = (o[wc] * (1 if s is None else (o[s] == v))).to_numpy()
        print(w, flush=True)
    for k in L.CLASSES:
        print(k, "max difference of the ± 15 km rerun to the frozen weights", float(np.abs(out[f"W_{k}_15"] - d["W_" + k].to_numpy()).max()))
    out.to_pickle(L.CACHE / "bands.pkl")


if __name__ == "__main__":
    t0 = time.time()
    run()
    print(f"{time.time() - t0:.0f} s")
