# checks/check_branch_scan.py
# N-test scan over the fault logic-tree branches: for every crustal fault XML,
# compare the expected count of M >= CAP_MAG inside the fault buffers with the
# observed declustered count over the completeness window. Produces the table
# that says which branches the data bracket.

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import ssm_config as C
from s02_fault_buffers import load_union, cell_mask
from check_fault_ssm_merger import (read_fault_mfds, load_crustal_catalog,
                                           CheckConfig)

FAULT_XML_GLOB = "../fault_model/crustal_faults_*.xml"
COMPLETENESS_YEAR = 1950


def poisson_tails(n_obs: int, lam: float) -> tuple[float, float]:
    if lam > 500:
        return np.nan, np.nan
    cdf = sum(math.exp(-lam) * lam ** k / math.factorial(k)
              for k in range(n_obs + 1))
    pmf = math.exp(-lam) * lam ** n_obs / math.factorial(n_obs)
    return cdf, 1.0 - cdf + pmf


def main():
    # 1) observed: declustered crustal mainshocks M >= CAP_MAG inside the
    #    fault buffers, since COMPLETENESS_YEAR
    union = load_union(C.BUFFERS_UNION)
    cat = load_crustal_catalog(CheckConfig())
    cat["year"] = pd.to_datetime(cat["time_iso"], utc=True,
                                 errors="coerce").dt.year
    sel = cat[(cat["mag"] >= C.CAP_MAG) & (cat["year"] >= COMPLETENESS_YEAR)]
    inside = cell_mask(sel["longitude"].to_numpy(), sel["latitude"].to_numpy(),
                       union)
    n_obs = int(inside.sum())
    years = pd.Timestamp.now().year - COMPLETENESS_YEAR
    print(f"[branch_scan] observed {n_obs} events M>={C.CAP_MAG} inside buffers "
          f"in {years} yr")

    # 2) expected: every branch XML in turn
    rows = []
    for xml in sorted(Path().glob(FAULT_XML_GLOB)):
        faults = read_fault_mfds(xml)
        lam_yr = sum(float(f["rates"].sum()) for f in faults)
        lam = lam_yr * years
        p_le, p_ge = poisson_tails(n_obs, lam)
        rows.append({"branch": xml.stem, "n_sources": len(faults),
                     "rate_per_yr": lam_yr, "expected": lam, "observed": n_obs,
                     "obs_over_exp": n_obs / lam if lam > 0 else np.nan,
                     "p_le_obs": p_le, "p_ge_obs": p_ge})

    # 3) the table: branches with obs/exp near 1 are the ones the data support
    df = pd.DataFrame(rows).sort_values("obs_over_exp")
    out = C.OUT / "merger_checks" / "branch_scan.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"[branch_scan] wrote {out}")


if __name__ == "__main__":
    main()
