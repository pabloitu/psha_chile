# s02_mc.py
# Completeness analysis of the UNDECLUSTERED interface catalog — detection
# is a network property; estimating Mc on a declustered catalog inherits
# artifacts of the declustering (small events deleted by the algorithm in
# cascade years masquerade as incompleteness).
#   - input contract report (guard against silent upstream re-runs)
#   - KS-based Mc per fixed time window on the FULL interface catalog only
#     (completeness is a network property; segments enter at the rate step)
# Outputs: outputs/mc/mc_windows.csv, completeness_proposal.txt,
#          figures/s02_magtime.png

import datetime
import hashlib
import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from seismostats.analysis.estimate_mc import estimate_mc_ks

import sub_config as C

MC_DIR = C.OUT_DIR / "mc"


def _decyear(s):
    # pandas Timestamp bottoms out at 1677; the catalog starts 1513,
    # so decimal years are parsed from the ISO string directly
    try:
        y, mo, d = int(s[:4]), int(s[5:7]), int(s[8:10])
        doy = datetime.date(y, mo, d).timetuple().tm_yday
        return y + (doy - 1) / 365.25
    except (ValueError, TypeError):
        return np.nan


def load_catalog(path):
    df = pd.read_csv(path)
    df["year"] = [_decyear(str(s)) for s in df["time_iso"]]
    df = df[np.isfinite(df["year"]) & df["mag"].notna()].copy()
    return df.sort_values("year").reset_index(drop=True)


def contract_report(df, path):
    """
    Fingerprint of the input catalog. If the handler is re-run upstream,
    this makes the change visible instead of silent.
    """
    rep = {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()[:16],
        "n_events": int(len(df)),
        "y_min": round(float(df["year"].min()), 2),
        "y_max": round(float(df["year"].max()), 2),
        "mag_min": float(df["mag"].min()), "mag_max": float(df["mag"].max()),
        "n_pre1900": int((df["year"] < 1900).sum()),
        "n_m75": int((df["mag"] >= 7.5).sum()),
    }
    print(json.dumps(rep, indent=2))
    return rep


def mc_per_window(mags):
    mags = np.round(np.round(mags / C.DELTA_M) * C.DELTA_M, 6)
    mc, info = estimate_mc_ks(
        mags, delta_m=C.DELTA_M, p_value_pass=C.MC_P_VALUE,
        b_value=C.MC_B_FIXED,
    )
    return mc


def window_table(df, label):
    """
    KS Mc per fixed window for one catalog subset.

    Windows with fewer than MC_MIN_EVENTS events get Mc = MC_HIST_FLOOR
    (flagged, not estimated): the historical windows only contain great
    earthquakes and the KS test is meaningless there.
    """
    rows = []
    for t0, t1 in C.MC_WINDOWS:
        y0 = int(t0[:4])
        y1 = int(t1[:4]) if t1 else float(np.ceil(df["year"].max()))
        m = df[(df["year"] >= y0) & (df["year"] < y1)]["mag"].to_numpy()
        if len(m) < C.MC_MIN_EVENTS:
            rows.append((label, y0, y1, len(m), C.MC_HIST_FLOOR, "floor"))
            continue
        mc = mc_per_window(m)
        how = "ks" if mc is not None else "ks_failed"
        if mc is None:
            mc = np.nan
        rows.append((label, y0, y1, len(m), mc, how))
    return pd.DataFrame(rows, columns=["seg", "y0", "y1", "n", "mc", "how"])


def propose_steps(tab):
    """
    Cumulative-from-present completeness: magnitude M is complete since the
    earliest window from which Mc <= M holds through to present. Equivalent
    to a reverse running max over window Mc.
    """
    t = tab.dropna(subset=["mc"]).sort_values("y0")
    mc_eff = np.maximum.accumulate(t["mc"].to_numpy()[::-1])[::-1]
    steps, last = [], None
    for y0, mc in zip(t["y0"], mc_eff):
        if mc != last:
            steps.append((round(float(mc), 1), int(y0)))
            last = mc
    return steps


def audit_steps(steps, df, label):
    """
    Band-rate density check: annual rate per unit magnitude must not
    increase with M (GR). Warns, does not fail — the table is a proposal.
    """
    steps = sorted(steps)  # ascending Mc = later steps cover older windows
    ok = True
    for i, (mc, y0) in enumerate(steps):
        hi = steps[i + 1][0] if i + 1 < len(steps) else 11.0
        t_obs = C.PRESENT_YEAR - y0 + 1
        n = ((df["mag"] >= mc) & (df["mag"] < hi) & (df["year"] >= y0)).sum()
        r = n / t_obs / max(hi - mc, C.DELTA_M)
        if i and r > 1.3 * prev_r:
            print(f"[audit:{label}] band {mc}-{hi} rate density rises "
                  f"{prev_r:.3g} -> {r:.3g} (>30%)")
            ok = False
        prev_r = r
    return ok


def plot_magtime(df, tabs, fname):
    segs = list(tabs)
    fig, axes = plt.subplots(len(segs), 1, figsize=(9, 2.6 * len(segs)),
                             sharex=True)
    axes = np.atleast_1d(axes)
    for ax, sid in zip(axes, segs):
        sub = df if sid == C.FULL_ID else df[df["seg"] == sid]
        ax.plot(sub["year"], sub["mag"], ".", ms=2, alpha=0.3, color="gray")
        t = tabs[sid]
        for _, r in t.iterrows():
            if np.isfinite(r["mc"]):
                ls = "-" if r["how"] == "ks" else ":"
                ax.hlines(r["mc"], r["y0"], r["y1"], color="crimson", ls=ls,
                          lw=2)
        for y in [w[0][:4] for w in C.MC_WINDOWS]:
            ax.axvline(int(y), color="k", lw=0.3, alpha=0.3)
        ax.set_ylabel(sid, fontsize=8)
        ax.set_ylim(3.5, 10)
    axes[-1].set_xlabel("year")
    axes[0].set_title("Mc per window (solid=KS, dotted=floor/low-N)")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / fname, dpi=200)


def main():
    MC_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_catalog(C.CAT_INTERFACE)
    rep = contract_report(df, C.CAT_INTERFACE)
    tab = window_table(df, C.FULL_ID)
    tabs = {C.FULL_ID: tab}
    steps = propose_steps(tab)
    audit_steps(steps, df, C.FULL_ID)
    proposal = {C.FULL_ID: steps}
    print(f"full-catalog steps (apply to all segments at the rate step): {steps}")

    pd.concat(tabs.values()).to_csv(MC_DIR / "mc_windows.csv", index=False)

    txt = ["# PROPOSAL from s02 — read figures/s02_magtime.png, edit, then",
           "# paste into sub_config.COMPLETENESS. Steps are (Mc, since_year).",
           f"# input: {rep['sha256']} n={rep['n_events']}",
           f"COMPLETENESS = {steps}"]
    (MC_DIR / "completeness_proposal.txt").write_text("\n".join(txt) + "\n")
    print(f"wrote {MC_DIR / 'completeness_proposal.txt'}")

    plot_magtime(df, tabs, "s02_magtime.png")


if __name__ == "__main__":
    main()