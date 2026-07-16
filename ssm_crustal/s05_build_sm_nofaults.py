# s05_build_sm_nofaults.py
# Baseline source model: point sources from the UNCAPPED s01 grid, i.e. the
# smoothed model keeps M up to each class's own Mmax everywhere, with no
# fault handoff. Thin wrapper around s04 so both models share one builder
# (same depths, cells, MFD conventions) -> any hazard difference against the
# fault model is attributable to the merger alone.
#
# Hazard branches:
#   with faults : SM_XML          + the fault XMLs
#   baseline    : SM_XML_BASELINE alone
#
# Run after s01 (s02/s03 are not needed for this model).

from __future__ import annotations

import ssm_config as C
from s04_build_sm import create_crustal_point_source_model, PointSourceModelConfig


def main():
    # 1) the uncapped grid written by s01: no cells were capped, so every
    #    cell keeps its full class MFD, including inside the fault buffers
    if not C.SSM_GRID.exists():
        raise FileNotFoundError(f"[main] {C.SSM_GRID} not found: run s01 first")
    print(f"[main] BASELINE (no faults): {C.SSM_GRID} -> {C.SM_XML_BASELINE}")

    # 2) same builder as s04: constant crustal depths, one PointSource per
    #    non-empty cell, MFD consistency check, NRML out
    create_crustal_point_source_model(
        ssm_mfd_csv=C.SSM_GRID,
        xml_out=C.SM_XML_BASELINE,
        depth_plot_png=C.FIG / "sm_point_depths_nofaults.png",
        cfg=PointSourceModelConfig(),
    )


if __name__ == "__main__":
    main()