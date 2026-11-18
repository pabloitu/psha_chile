# Branch tables hazard/branches_<family>.csv: every branch of the final tree of the family (tree.json; prefixed in the
# job source trees) with its choices and tree weight; the interface scaling level as rows of its own.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from hazard import config as hc
from hazard import jobs as J

COLS = {"interface": {"geometry": "geometry", "rate": "rate", "chi": "coupling", "ab": "(a, b)", "b_option": "b option",
                      "shape": "shape", "convention": "declustering"},
        "inslab": {"rate": "declustering", "ab": "(a, b)"},
        "crustal": {"system": "fault linkage", "fault_pad": "fault Mmax pad", "psi": "ψ", "shape": "fault MFD",
                    "splays": "LOFS secondary traces"}}


def table(fam):
    fa = hc.FAMILIES[fam]
    t = J.manifests(fam)[0]
    b = t.get("branches") or t["paths"]
    d = pd.DataFrame([{"level": "source", "id": x["id"], "job_id": f"{fa['short']}_{x['id']}",
                       **{v: (x["branches"] if fam == "crustal" else x).get(k) for k, v in COLS[fam].items()},
                       "weight": x["weight"], "files": " ".join(x.get("files", [x.get("file")]))} for x in b])
    if fam == "interface":
        d["scaling"] = "level"
        m = pd.DataFrame([{"level": "scaling", "id": k, "job_id": k, "scaling": hc.MSR[k][0], "weight": w}
                          for k, w in J.TREE_MSR.items()])
        d = pd.concat([d, m], ignore_index=True)
    return d


if __name__ == "__main__":
    for f in hc.FAMILIES:
        t = table(f)
        t.to_csv(hc.HERE / f"branches_{f}.csv", index=False)
        print(f, len(t), "rows")
