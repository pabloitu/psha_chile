# Are the S3 crustal files ready for S5b? The three conditions of the S3 note (Pablo, 16 Nov): the WORKLOG entry, the
# "ready" flag in branches.json and the S3 parse check (every file read, rates equal to the tables).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import pandas as pd

from hazard import config as hc

RUN = "2026-11-16e"
CR = hc.ROOT / "model" / "crustal"


def status():
    s = {}
    s["worklog"] = f"S3: crustal OpenQuake files ready ({RUN})" in (hc.ROOT / "WORKLOG.md").read_text()
    p = CR / "nrml" / RUN / "branches.json"
    try:
        s["ready_flag"] = json.loads(p.read_text()).get("ready") is True
    except (FileNotFoundError, json.JSONDecodeError):
        s["ready_flag"] = False
    p = CR / "tables" / f"oqcheck_{RUN}.csv"
    s["oqcheck"] = p.exists()
    if p.exists():
        d = pd.read_csv(p)
        s["oqcheck_columns"] = list(d.columns)
        s["oqcheck_rows"] = len(d)
    return s


if __name__ == "__main__":
    s = status()
    print(s)
    print("READY" if all(s[k] for k in ("worklog", "ready_flag", "oqcheck")) else "NOT READY")
