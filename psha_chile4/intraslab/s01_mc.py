# KS completeness per class on regular windows. Output is a proposal:
# read the figures, then edit config.COMPLETENESS.
# Outputs: mc/windows.csv, mc/proposal.txt, figures/s01_mc_{class}.png

import json

import pandas as pd

from lib import cat, cfg, gr, mc
from intraslab import config
from intraslab.s00_decluster import load


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "mc"
    od.mkdir(parents=True, exist_ok=True)
    te = c.T_END or json.loads((c.OUT / "decluster" / "input.json").read_text())["t_end"]
    df, _ = load(c)

    tabs, props, txt = [], {}, ["# proposal from s01; compare with config.COMPLETENESS"]
    for k in c.CLASSES:
        s = (cat.load(c.OUT / "decluster" / f"cat_dc_{k}_{c.DC_METHOD}.csv")
             if c.MC_ON_DECLUSTERED else df[df["class"] == k])
        y0 = c.HIST_CUTOFF_BY_CLASS.get(k, c.HIST_CUTOFF) or s["year"].min()
        wins = mc.regular(y0, te, c.WINDOW_YEARS_BY_CLASS.get(k, c.WINDOW_YEARS))
        t = mc.outliers(mc.table(s, wins, c), c.MC_OUTLIER_DROP)
        props[k] = mc.propose(t)
        tabs.append(t.assign(**{"class": k}))
        _, msg = gr.audit(s, props[k], te)
        txt += [f"# {k} current: {c.COMPLETENESS.get(k)}"] + [f"# {k} audit: {m}" for m in msg]
        mc.fig(s, t, props[k], te, c.FIG / f"s01_mc_{k}.png", f"{k} Mc")
        print(f"{k}: {props[k]}")
    txt.append("COMPLETENESS = {\n" + "".join(f"    {k!r}: {v},\n" for k, v in props.items()) + "}")
    pd.concat(tabs).to_csv(od / "windows.csv", index=False)
    (od / "proposal.txt").write_text("\n".join(txt) + "\n")
    print("\n".join(txt))
    cfg.snapshot(c, "s01")


if __name__ == "__main__":
    main()
