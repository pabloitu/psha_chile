"""Cut the small real samples of test_match.py from the frozen source tables (run once from catalog/)."""
import shutil
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import match as M

# settings
WIN = [("2010-02-27T06:00", "2010-02-27T07:40"), ("2015-09-16T22:30", "2015-09-17T00:00"),
       ("2014-04-01T23:30", "2014-04-02T00:50"), ("2014-04-03T02:30", "2014-04-03T03:30"),
       ("2011-01-02T20:00", "2011-01-02T21:00"), ("1912-12-07T00:00", "1912-12-08T00:00"),
       ("1960-05-22T00:00", "1960-05-23T00:00"), ("2009-10-05T13:00", "2009-10-05T14:00"),
       ("1994-12-10T00:00", "1994-12-11T00:00"), ("1994-10-12T00:00", "1994-10-13T00:00"),
       ("2025-04-18T00:00", "2025-04-18T00:30")]

for s in M.SOURCES:
    f = M.SRC / f"{s}_{M.DATES.get(s, M.FROZEN)}_events.csv"
    if not f.exists() or s == "cabello":
        continue
    e = pd.read_csv(f, dtype=str)
    t = M.tsec(e.time)
    ok = pd.Series(False, index=e.index)
    for a, b in WIN:
        ok |= (t >= M.tsec([a])[0]) & (t < M.tsec([b])[0])
    e = e[e.src_id.isin(e.src_id[ok])]
    m = pd.read_csv(str(f).replace("_events", "_mags"), dtype=str)
    e.to_csv(HERE / f.name, index=False)
    m[m.src_id.isin(e.src_id)].to_csv(HERE / f.name.replace("_events", "_mags"), index=False)
    print(s, len(e))
for k in ("events", "mags"):
    shutil.copy(M.SRC / f"rm2018_{M.FROZEN}_{k}.csv", HERE)
shutil.copy(M.OUT / f"windows_{M.RUN}.csv", HERE / "windows.csv")
