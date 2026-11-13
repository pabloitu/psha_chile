"""X4 figure: why the surface-wave scales have no magnitude limit, and what the smooth GCMT correction did."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import palette  # noqa: E402

# settings
TAB, FIG = HERE / "tables", HERE / "figs"
RUN = HERE.parents[1] / "catalog" / "merged" / "mw_histogram_2026-11-11.csv"
RULES = {"1": "used only if its own\nvalue reaches Mw 5\n(second run)", "2": "used only if another\nscale reaches Mw 5", "4": "not used",
         "3": "no limit,\nshallow events,\nfirst scale (this run)", "7": "no limit,\nshallow events,\nweighted mean"}
PERIOD = "2000–2010"


def main():
    palette.apply()
    C = palette.SERIES
    FIG.mkdir(exist_ok=True)
    b = pd.read_csv(TAB / "x4_blind.csv")
    b = b[(b.by == "count") & (b.bin == ">= 5.0")]
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.2), layout="constrained")
    x = np.arange(len(RULES))
    for i, (s, lab) in enumerate((("six agencies", "ISC, NEIC, CSN, INPRES"), ("all agencies", "all agencies"))):
        v = [100 * (b[(b.set == s) & b.rule.str.startswith(r)]["converted − measured"].iloc[0] - 1) for r in RULES]
        ax[0].bar(x + 0.2 * (2 * i - 1), v, 0.38, color=C[i], label=lab)
    ax[0].axhline(0, color="0.3", lw=0.8)
    ax[0].set_xticks(x, RULES.values(), fontsize=9)
    ax[0].set_ylabel("events at Mw ≥ 5, converted against measured (%)")
    ax[0].set_title("Rules for the surface-wave magnitudes on events with a measured Mw")
    ax[0].legend()
    old, new = pd.read_csv(TAB / "x4_histogram_rule1.csv"), pd.read_csv(RUN)
    k = (old.mw >= 4.75) & (old.mw <= 5.65)
    ax[1].step(old.mw[k], old[PERIOD][k], where="mid", color=C[1], lw=2, label="second run: step correction of GCMT, limit at Mw 5")
    ax[1].step(new.mw[k], new[PERIOD][k], where="mid", color=C[0], lw=2.4, label="this run: smooth correction, no limit")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("Mw (0.1 bins)")
    ax[1].set_ylabel(f"events, {PERIOD}")
    ax[1].set_title(f"Magnitude histogram of {PERIOD}")
    ax[1].legend()
    fig.savefig(FIG / "x4_rule_choice.png", dpi=200)


if __name__ == "__main__":
    main()
