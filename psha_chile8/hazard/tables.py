# Tables for REPORT_S5a: every job with its calc id, run time and realizations (hazard/out/jobs.csv), and the
# reference PGA 475 yr per city per family and combined (hazard/out/ref_pga475.csv)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import numpy as np
import pandas as pd

from hazard import combine, post
from hazard import config as hc
from hazard import jobs as J

POE = 0.002105

if __name__ == "__main__":
    rows = []
    for n in J.JOBS:
        p = hc.JOBS_DIR / n / "build.json"
        d = json.loads(p.read_text()) if p.exists() else {}
        rows.append({"job": n, "families": " ".join(d.get("families", [])), "calc_id": d.get("calc_id"),
                     "run_time_s": d.get("run_time_s"), "n_realizations": d.get("n_realizations"),
                     "skip": J.JOBS[n].get("skip", "")})
    t = pd.DataFrame(rows)
    hc.OUT.mkdir(parents=True, exist_ok=True)
    t.to_csv(hc.OUT / "jobs.csv", index=False)
    done = t[t.calc_id.notna()]
    print(f"{len(done)} jobs with a calc, {done.run_time_s.sum() / 3600:.2f} h")

    ref = {"interface": "t_if_ref", "in-slab": "t_is_ref", "crustal": "t_cr_ref"}
    m = {}
    for k, j in ref.items():
        try:
            r = post.load(j)
            m[k], lv = post.mean(r), r["imtls"]["PGA"]
        except SystemExit:
            pass
    out = pd.DataFrame(index=list(hc.CITIES))
    for k, v in m.items():
        out[k] = [post.iml(c, lv, POE) for c in v]
    for name, fs in (("interface + in-slab", ["interface", "in-slab"]), ("all three", list(m))):
        if set(fs) <= set(m) and (name != "all three" or len(m) == 3):
            tot = 1 - np.exp(-sum(combine.rate(m[f]) for f in fs))
            out[name] = [post.iml(c, lv, POE) for c in tot]
    out.index.name = "site"
    out.to_csv(hc.OUT / "ref_pga475.csv", float_format="%.3f")
    print(out.round(3).to_string())
