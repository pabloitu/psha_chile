# checks/check_baseline_vs_faults.py
# Compare the no-fault baseline (uncapped SSM) with the fault model
# (capped SSM + fault sources), nationally and inside the fault buffers.
# This is the source-model-level statement of what the fault merger does,
# before any hazard calculation.
#
# Run from ssm_3/ after s01, s02, s03 and both s04 runs:
#   python -m checks.check_baseline_vs_faults

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import ssm_config as C
from s02_fault_buffers import load_union, cell_mask
from s03_cap_ssm_mmax import bin_cols
from check_fault_ssm_merger import read_fault_mfds, fault_bin_edges

FAULT_XML = Path("../fault_model/crustal_faults_phi100_mgeo_tgr.xml")


def grid_mfd(csv: Path, mask=None) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv)
    cols = bin_cols(df)
    edges = np.array([lo for _, lo, _ in cols] + [cols[-1][2]])
    sel = df if mask is None else df[mask]
    return edges, sel[[c for c, _, _ in cols]].to_numpy().sum(axis=0)


def fault_rates(edges: np.ndarray) -> np.ndarray:
    out = np.zeros(len(edges) - 1)
    if not FAULT_XML.exists():
        print(f"[fault_rates] {FAULT_XML.resolve()} not found")
        return out
    dm = edges[1] - edges[0]
    for f in read_fault_mfds(FAULT_XML):
        fe = fault_bin_edges(f)
        for k, r in enumerate(f["rates"]):
            i = int(round((fe[k] - edges[0]) / dm))
            if 0 <= i < len(out):
                out[i] += r
    return out


def cum(e, r):
    return e[:-1], np.cumsum(r[::-1])[::-1]


def main():
    # 1) baseline = uncapped s01 grid; fault model = capped s03 grid + faults
    e, r_base = grid_mfd(C.SSM_GRID)
    _, r_cap = grid_mfd(C.SSM_GRID_CAPPED)
    r_f = fault_rates(e)
    r_fault_model = r_cap + r_f

    # 2) same, restricted to the fault buffers (where the two models differ)
    union = load_union(C.BUFFERS_UNION)
    df = pd.read_csv(C.SSM_GRID)
    inside = cell_mask(df["lon"].to_numpy(), df["lat"].to_numpy(), union)
    _, r_base_in = grid_mfd(C.SSM_GRID, inside)
    _, r_cap_in = grid_mfd(C.SSM_GRID_CAPPED, inside)
    r_fault_in = r_cap_in + r_f          # all faults sit inside their buffers

    # 3) sanity: outside the buffers the two models must be identical
    _, r_base_out = grid_mfd(C.SSM_GRID, ~inside)
    _, r_cap_out = grid_mfd(C.SSM_GRID_CAPPED, ~inside)
    d = np.abs(r_base_out - r_cap_out).max()
    print(f"[check] max |baseline - fault model| outside buffers = {d:.3e} "
          f"-> {'PASS' if d < 1e-12 * max(r_base_out.max(), 1e-300) else 'FAIL'}")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for A, (rb, rf, ttl) in zip(ax, [
            (r_base, r_fault_model, "national"),
            (r_base_in, r_fault_in, "inside fault buffers")]):
        for r, lab, st in [(rb, "baseline (no faults)",
                            dict(color="steelblue", lw=2)),
                           (rf, "with faults (capped + faults)",
                            dict(color="darkorange", lw=2))]:
            x, y = cum(e, np.asarray(r))
            m = y > 0
            A.step(x[m], y[m], where="post", label=lab, **st)
        A.axvline(C.CAP_MAG, color="k", lw=0.8, ls=":")
        A.set_yscale("log")
        A.set_xlabel("M")
        A.set_ylabel("cumulative N(>=M) (/yr)")
        A.set_title(ttl)
        A.grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    fig.suptitle("no-fault baseline vs fault model")
    fig.tight_layout()
    png = C.OUT / "merger_checks" / "baseline_vs_faults.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[main] wrote {png}")

    # 4) the numbers for the paper: ratio at CAP_MAG and above
    rows = []
    for m in (C.CAP_MAG, 6.5, 7.0):
        i = e[:-1] >= m - 1e-9
        b_nat, f_nat = r_base[i].sum(), r_fault_model[i].sum()
        b_in, f_in = r_base_in[i].sum(), r_fault_in[i].sum()
        rows.append({"M>=": m, "baseline_nat": b_nat, "faults_nat": f_nat,
                     "ratio_nat": f_nat / b_nat if b_nat else np.nan,
                     "baseline_buf": b_in, "faults_buf": f_in,
                     "ratio_buf": f_in / b_in if b_in else np.nan})
    out = pd.DataFrame(rows)
    out.to_csv(C.OUT / "merger_checks" / "baseline_vs_faults.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()