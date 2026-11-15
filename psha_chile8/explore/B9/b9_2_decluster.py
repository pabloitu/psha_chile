"""B9: declustering flags for the events of Mw >= 4.5. Gardner and Knopoff (1974) windows and the nearest-neighbour
method of Zaliapin and Ben-Zion (2013). Run on all classes together. Writes cache/decluster.pkl."""
import time

import numpy as np
import pandas as pd

import b9_lib as L

FS = 1.0
NN_B, NN_DF = 1.0, 1.6
NN_FROM = 1964


def run():
    d = L.load()
    t, lon, lat, m = (d[c].to_numpy() for c in ("t", "lon", "lat", "mw"))
    out = pd.DataFrame(dict(event_id=d.event_id))
    out["gk"] = L.gardner_knopoff(t, lon, lat, m, FS)
    out["gk_fs0"] = L.gardner_knopoff(t, lon, lat, m, 0.0)
    eta, T, R, par = L.nearest_neighbour(t, lon, lat, m, NN_B, NN_DF)
    thr = L.nn_threshold(eta[t >= NN_FROM])
    out["eta"], out["nn_T"], out["nn_R"], out["nn_parent"] = eta, T, R, par
    # background = no close parent; the first event of a cluster stays, as in the method, not the largest
    out["nn"] = ~(np.log10(eta) < thr)
    out.attrs["thr"] = thr
    out.to_pickle(L.CACHE / "decluster.pkl")
    print(f"log10 eta threshold {thr:.2f}; kept gk {out.gk.mean():.3f}, gk_fs0 {out.gk_fs0.mean():.3f}, nn {out.nn.mean():.3f}")


if __name__ == "__main__":
    t0 = time.time()
    run()
    print(f"{time.time() - t0:.0f} s")
