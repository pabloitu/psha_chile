# s01_mc.py
# Completeness per slab class on the UNDECLUSTERED classified catalog
# (detection is a network property; declustered catalogs inherit the
# algorithm's deletions as fake incompleteness). Regular windows: one
# historical block 1513 -> REGULAR_FROM, then WINDOW_YEARS steps — no
# hand-drawn epoch list to drift. KS per window (fast settings), per
# class, in parallel. The proposal is pasted BY HAND into
# ssm_config.COMPLETENESS after reading the figures.
# Outputs: <OUT>/mc/mc_windows.csv, completeness_proposal.txt
#          <OUT>/figures/s01_magtime_{class}.png
#
# requires in ssm_config (in addition to s00's keys):
#   WINDOW_YEARS = 10; REGULAR_FROM = 1900; HIST_START_YEAR = 1513
#   DELTA_M = 0.1; MC_P_VALUE = 0.1; MC_MIN_EVENTS = 50
#   MC_B_FIXED = 1.0; MC_KS_N = 2500; MC_MAX_SAMPLE = 3000
#   MC_HIST_FLOOR = 7.5

from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from seismostats.analysis.estimate_mc import estimate_mc_ks

import ssm_config as C
from s00_decluster import load_classified

MC_DIR = C.OUT_DIR / "mc"


def build_windows(y_max):
    edges = list(range(C.REGULAR_FROM, int(y_max) + 1, C.WINDOW_YEARS))
    if int(y_max) + 1 - edges[-1] < C.WINDOW_YEARS / 2 and len(edges) > 1:
        edges.pop()
    ys = [C.HIST_START_YEAR] + edges + [int(np.ceil(y_max))]
    return list(zip(ys[:-1], ys[1:]))


def mc_one(mags):
    mags = np.round(np.round(mags / C.DELTA_M) * C.DELTA_M, 6)
    if C.MC_MAX_SAMPLE and len(mags) > C.MC_MAX_SAMPLE:
        mags = np.random.default_rng(42).choice(mags, C.MC_MAX_SAMPLE,
                                                replace=False)
    vals, cnt = np.unique(mags, return_counts=True)
    m0 = max(vals[np.argmax(cnt)] - 0.2, vals[0])
    mcs = np.round(np.arange(m0, vals[-1] - 0.5, C.DELTA_M), 6)
    mc, _ = estimate_mc_ks(mags, delta_m=C.DELTA_M, mcs_test=mcs,
                           p_value_pass=C.MC_P_VALUE, b_value=C.MC_B_FIXED,
                           n=C.MC_KS_N)
    return mc


def _win_job(args):
    cl, y0, y1, m = args
    if len(m) < C.MC_MIN_EVENTS:
        return (cl, y0, y1, len(m), C.MC_HIST_FLOOR, "floor")
    mc = mc_one(m)
    return (cl, y0, y1, len(m),
            mc if mc is not None else np.nan,
            "ks" if mc is not None else "ks_failed")


def propose_steps(tab):
    """
    Cumulative-from-present: magnitude M is complete since the earliest
    window from which Mc <= M holds through to present (reverse running
    max over window Mc).
    """
    t = tab.dropna(subset=["mc"]).sort_values("y0")
    mc_eff = np.maximum.accumulate(t["mc"].to_numpy()[::-1])[::-1]
    steps, last = [], None
    for y0, mc in zip(t["y0"], mc_eff):
        if mc != last:
            steps.append((round(float(mc), 1), int(y0)))
            last = mc
    return steps


def audit_steps(steps, df, y_end, label):
    steps = sorted(steps)
    prev = None
    for i, (mc, y0) in enumerate(steps):
        hi = steps[i + 1][0] if i + 1 < len(steps) else 11.0
        n = ((df["mag"] >= mc) & (df["mag"] < hi) & (df["year"] >= y0)).sum()
        r = n / (y_end - y0 + 1) / max(hi - mc, C.DELTA_M)
        if prev is not None and r > 1.3 * prev:
            print(f"[audit:{label}] band {mc}-{hi} rate density rises "
                  f"{prev:.3g} -> {r:.3g} (>30%)")
        prev = r


def main():
    MC_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_classified()
    y_end = float(np.ceil(df["year"].max()))

    jobs, proposal, tabs = [], {}, {}
    for cl in C.CLASSES:
        cat = df[df["class"] == cl]
        for y0, y1 in build_windows(cat["year"].max()):
            m = cat[(cat["year"] >= y0) & (cat["year"] < y1)]["mag"].to_numpy()
            jobs.append((cl, y0, y1, m))
        # the mmax guard input: catches the next 1575-style intruder here,
        # not in the hazard maps
        top = cat.nlargest(5, "mag")
        print(f"[top events] {cl}: "
              + ", ".join(f"M{r.mag:.1f}@{r.year:.0f}(z{r.depth:.0f})"
                          for r in top.itertuples()))

    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(_win_job, jobs))
    tab = pd.DataFrame(rows, columns=["class", "y0", "y1", "n", "mc", "how"])
    tab.to_csv(MC_DIR / "mc_windows.csv", index=False)

    txt = ["# PROPOSAL from s01_mc — read figures/s01_magtime_*.png, edit,",
           "# then paste into ssm_config.COMPLETENESS. Steps: (Mc, since_year).",
           "COMPLETENESS = {"]
    for cl in C.CLASSES:
        t = tab[tab["class"] == cl]
        tabs[cl] = t
        steps = propose_steps(t)
        cat = df[df["class"] == cl]
        audit_steps(steps, cat, y_end, cl)
        proposal[cl] = steps
        txt.append(f'    "{cl}": {steps},')
        print(f"{cl}: {steps}")
    txt.append("}")
    (MC_DIR / "completeness_proposal.txt").write_text("\n".join(txt) + "\n")

    for cl in C.CLASSES:
        cat = df[df["class"] == cl]
        t = tabs[cl]
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(cat["year"], cat["mag"], ".", ms=2, alpha=0.3, color="gray")
        for _, r in t.iterrows():
            if np.isfinite(r["mc"]):
                ls = "-" if r["how"] == "ks" else ":"
                ax.hlines(r["mc"], r["y0"], r["y1"], color="crimson",
                          ls=ls, lw=2)
            ax.axvline(r["y0"], color="k", lw=0.3, alpha=0.3)
        ax.set_xlabel("year")
        ax.set_ylabel("M")
        ax.set_ylim(3.5, 10)
        ax.set_title(f"{cl}: Mc per {C.WINDOW_YEARS}-yr window "
                     "(solid=KS, dotted=floor)")
        fig.tight_layout()
        fig.savefig(C.FIG_DIR / f"s01_magtime_{cl}.png", dpi=200)
        plt.close(fig)

    print(f"wrote {MC_DIR}")


if __name__ == "__main__":
    main()