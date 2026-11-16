# Branch tables hazard/branches_<family>.csv: every branch id of the family (as in branches.json and, prefixed, in the
# job source trees) with its choices and tree weight; the interface scaling level as rows of its own.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import pandas as pd

from hazard import config as hc

COLS = {"interface": {"geometry": "geometry", "rate": "rate", "chi": "coupling", "ab": "(a, b)", "b_option": "b option",
                      "shape": "shape", "convention": "declustering"},
        "inslab": {"layers": "layers", "decl": "pattern", "ab": "(a, b)", "shape": "shape"}}


def table(fam):
    fa = hc.FAMILIES[fam]
    b = json.loads((fa["dir"] / "branches.json").read_text())["branches"]
    d = pd.DataFrame([{"level": "source", "id": x["id"], "job_id": f"{fa['short']}_{x['id']}",
                       **{v: x.get(k) for k, v in COLS[fam].items()}, "weight": x["weight"],
                       "files": " ".join(x.get("files", [x.get("file")]))} for x in b])
    if fam == "interface":
        d["scaling"] = "level"
        m = pd.DataFrame([{"level": "scaling", "id": k, "job_id": k, "scaling": v[0], "weight": v[1]}
                          for k, v in hc.MSR.items()])
        d = pd.concat([d, m], ignore_index=True)
    return d


if __name__ == "__main__":
    for f in hc.FAMILIES:
        t = table(f)
        t.to_csv(hc.HERE / f"branches_{f}.csv", index=False)
        print(f, len(t), "rows")
