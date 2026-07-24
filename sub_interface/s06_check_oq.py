# s06_check_oq.py
# Optional validation of the s05 NRMLs against openquake (the only script
# in this pipeline that imports it). Parses every model and builds each
# source's complex fault surface once — this runs OQ's edge/mesh geometry
# checks (check_fault_data) WITHOUT enumerating ruptures, which is what
# made sourcewriter take minutes per source. Full rupture validation
# happens anyway when the job runs.

from openquake.hazardlib import nrml
from openquake.hazardlib.sourceconverter import SourceConverter
from openquake.hazardlib.geo.surface.complex_fault import ComplexFaultSurface

import sub_config as C

SRC_DIR = C.OUT_DIR / "hazard" / "src"


def main():
    conv = SourceConverter(investigation_time=C.INV_TIME,
                           rupture_mesh_spacing=C.RUPT_MESH,
                           complex_fault_mesh_spacing=C.RUPT_MESH,
                           width_of_mfd_bin=C.BIN_W)
    files = sorted(SRC_DIR.glob("sub_int__*.xml"))
    if not files:
        raise SystemExit(f"no models in {SRC_DIR} — run s05 first")
    bad = 0
    for f in files:
        sm = nrml.to_python(str(f), conv)
        for grp in sm.src_groups:
            for src in grp:
                try:
                    surf = ComplexFaultSurface.from_fault_data(src.edges,
                                                               C.RUPT_MESH)
                    n = surf.mesh.lons.size
                    print(f"{f.name} :: {src.source_id}: surface ok "
                          f"({n} mesh pts)")
                except Exception as e:
                    bad += 1
                    print(f"{f.name} :: {src.source_id}: FAILED — {e}")
    if bad:
        raise SystemExit(f"{bad} sources failed surface validation")
    print(f"\nall sources in {len(files)} models passed")


if __name__ == "__main__":
    main()