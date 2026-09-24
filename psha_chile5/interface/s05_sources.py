# One NRML per interface end branch and the branch table the hazard runner
# turns into a logic tree. Each source's MFD moment is checked against s04.
# Outputs: nrml/sub__{geom}__{rate}__{form}.xml, nrml/branches.json

import json

import numpy as np
import pandas as pd

from lib import cfg, gr, nrml
from interface import config

RATES = [("seismic", "-", "seis"), ("geodetic", "lo", "geo_lo"),
         ("geodetic", "mid", "geo_mid"), ("geodetic", "hi", "geo_hi")]


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "nrml"
    od.mkdir(parents=True, exist_ok=True)
    bp = pd.read_csv(c.OUT / "rates" / "branches.csv", keep_default_na=False)
    geo = json.loads((c.OUT / "geometry" / "edges.json").read_text())

    out = []
    for geom, gt in (("segmented", "seg"), ("non_segmented", "full")):
        for rate, chi, rt in RATES:
            for form in ("tgr", "tapered"):
                sub = bp[(bp["geom"] == geom) & (bp["rate"] == rate)
                         & (bp["chi"] == chi) & (bp["form"] == form)]
                if not len(sub):
                    raise RuntimeError(f"no rows for {geom}/{rate}/{chi}/{form}")
                bid = f"{gt}__{rt}__{form}"
                srcs = []
                for r in sub.itertuples():
                    inc, e = gr.inc(r.lam, form, r.b, c.MMIN_HAZ, r.mmax, c.BIN_W, c.M0_C)
                    mom = (inc * gr.m0(e[:-1] + c.BIN_W / 2, c.M0_C)).sum()
                    if abs(mom / r.m0_rate - 1) > 0.03:
                        raise RuntimeError(f"{bid}/{r.seg}: MFD moment {mom:.3e} vs {r.m0_rate:.3e}")
                    edges = [[tuple(p) for p in ed] for ed in geo[r.seg]["edges"]]
                    srcs.append(nrml.complex_fault(f"{r.seg}_{bid}", edges, c.TRT,
                                                   nrml.mfd(inc, c.MMIN_HAZ, c.BIN_W),
                                                   c.MSR, c.ASPECT, c.RAKE))
                fn = f"sub__{bid}.xml"
                nrml.model(od / fn, f"interface {bid}", srcs)
                out.append({"id": bid, "file": fn, "weight": float(sub["weight"].iloc[0])})
    if abs(sum(b["weight"] for b in out) - 1) > 1e-6:
        raise RuntimeError("interface branch weights do not sum to 1")
    (od / "branches.json").write_text(json.dumps(out, indent=1))
    print(pd.DataFrame(out).to_string(index=False))
    cfg.snapshot(c, "s05")


if __name__ == "__main__":
    main()
