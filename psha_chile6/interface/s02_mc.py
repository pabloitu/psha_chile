# KS completeness per MC_WINDOWS on the undeclustered interface catalog.
# The output is a proposal: read the figure, then edit config.COMPLETENESS.
# Outputs: mc/windows.csv, mc/proposal.txt, figures/s02_mc.png

import numpy as np

from lib import cat, cfg, gr, mc
from interface import config


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "mc"
    od.mkdir(parents=True, exist_ok=True)

    df = cat.load(c.CAT)
    t_end = c.T_END or float(df["year"].max())
    wins = [(y0, y1 if y1 else int(np.ceil(t_end))) for y0, y1 in c.MC_WINDOWS]
    t = mc.outliers(mc.table(df, wins, c), c.MC_OUTLIER_DROP)
    steps = mc.propose(t)
    t.to_csv(od / "windows.csv", index=False)
    print(t.to_string(index=False))

    _, msg = gr.audit(df, steps, t_end)
    txt = ["# proposal from s02; compare with config.COMPLETENESS",
           f"# current:  {c.COMPLETENESS}", f"COMPLETENESS = {steps}"] + [f"# audit: {m}" for m in msg]
    (od / "proposal.txt").write_text("\n".join(txt) + "\n")
    print("\n".join(txt))
    mc.fig(df, t, steps, t_end, c.FIG / "s02_mc.png", "interface Mc")
    cfg.snapshot(c, "s02")


if __name__ == "__main__":
    main()
