"""X2 inputs: the X1 baseline events with every native magnitude, references, RM18, Cabello and per-scale errors."""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "X1"))
import x1_io as io  # noqa: E402
import x1_mag as xm  # noqa: E402

CACHE = HERE / "cache"
CACHE.mkdir(exist_ok=True)


def run():
    T0 = time.time()
    o = io.load("origins", dtype={"sid": str})
    lab = io.load("labels")["baseline"].to_numpy()
    L = xm.long_table(o, lab)
    attrs = xm.event_attrs("baseline")
    attrs = attrs[~attrs.index.duplicated()]
    W = xm.wide(L, L.scale.unique())
    R, off = xm.refs(W)
    rm18 = pd.read_csv(io.TAB / "t1_rm18_matches.csv")
    rm18 = rm18[(rm18["where"] == "event") & rm18.rm_mw.notna()]
    rep = io.load("events_baseline").set_index("ev").rep
    rm = pd.Series({int(lab[int(rep[int(r.ev)])]): r.rm_mw for _, r in rm18.iterrows()}, name="rm")
    cab = xm.cabello_on_events(o, lab).rename("cab")
    cab = cab[~cab.index.duplicated()]
    sig, _ = xm.errors(W)
    t = o.groupby(lab).t.min()
    L.to_csv(CACHE / "L.csv.gz", index=False)
    a = attrs[["lat", "lon", "z", "unk", "cls", "slab", "yr", "setting"]].copy()
    a["t"] = t.reindex(a.index).to_numpy()
    a.to_csv(CACHE / "attrs.csv.gz")
    R.join(rm, how="outer").join(cab, how="outer").to_csv(CACHE / "refs.csv.gz")
    pd.Series(sig).to_csv(CACHE / "sig.csv", header=["sigma"])
    print("prep", len(L), len(a), round(time.time() - T0), flush=True)


if __name__ == "__main__":
    run()
