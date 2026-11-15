"""X1: figures index from the figure log (one line per figure, last caption wins), with file sizes."""
import pandas as pd

import x1_io as io

# settings
OUT = io.HERE / "figures_index.md"
TIER = {"t1": "Tier 1, matching (A3)", "t2": "Tier 2, location and depth (A4)", "t3": "Tier 3, magnitudes (A5)",
        "t4": "Tier 4, preview of B9", "t5": "Tier 5, preview of A7", "t6": "Deeper pass"}

if __name__ == "__main__":
    f = pd.read_csv(io.CACHE / "figlog.tsv", sep="\t", header=None, names=["file", "q"]).drop_duplicates("file", keep="last")
    f = f[f.file.map(lambda x: (io.FIG / x).exists())].sort_values("file")
    lines = ["# X1 figures", "", "One line per figure in `figs/`: file, the question it answers. PNG, 200 dpi.", ""]
    for t, g in f.groupby(f.file.str[:2]):
        lines += [f"## {TIER.get(t, t)}", ""] + [f"- `figs/{r.file}`: {r.q}." for r in g.itertuples()] + [""]
    OUT.write_text("\n".join(lines))
    print(len(f), "figures")
