# create_crustal_fault_source_model.py
"""
Build an OpenQuake simple-fault source model (NRML) from a fault shapefile,
balancing each fault's GR a-value against its tectonic moment rate
Mdot = mu * L * W * slip * chi.

Depths can come from the shapefile (usd/lsd fields) or from a uniform zone
depth (usd=0, lsd=20 km), which is the convention used to build the original
crustalfaults.xml from the SARA database.

Requires: openquake.engine, pyshp, numpy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import math

import numpy as np
import shapefile

from openquake.hazardlib.geo.line import Line
from openquake.hazardlib.geo.point import Point
from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
from openquake.hazardlib.scalerel.wc1994 import WC1994
from openquake.hazardlib.source.simple_fault import SimpleFaultSource
from openquake.hazardlib.sourcewriter import write_source_model
from openquake.hazardlib.tom import PoissonTOM


# Fagnano/Magallanes segments carry zeroed attributes in the shapefile.
# Values recovered from the reference NRML (crustalfaults.xml); the 5
# segments absent there inherit mmax from the sibling closest in length.
FAGNANO_COMMON = {"usd": 0.0, "lsd": 20.0, "dip": 87.0, "min_mag": 6.05, "b_val": 1.0}

FAGNANO_OVERRIDES = {
    "CL-056b": {"max_mag": 7.85, "rake": -45.0},
    "CL-056c": {"max_mag": 7.35, "rake": -45.0},
    "CL-056d": {"max_mag": 7.05, "rake": -45.0},
    "CL-056e": {"max_mag": 7.05, "rake": -45.0},
    "CL-056f": {"max_mag": 6.85, "rake": -45.0},
    "CL-056g": {"max_mag": 6.85, "rake": -45.0},
    "CL-056h": {"max_mag": 6.95, "rake": -45.0},
    "CL-056i": {"max_mag": 6.85, "rake": -45.0},
    "CL-056j": {"max_mag": 6.95, "rake": -45.0},
    "AR-0056a": {"max_mag": 7.85, "rake": 0.0},
    "AR-0056b": {"max_mag": 6.85, "rake": 0.0},
    "AR-0056d": {"max_mag": 6.85, "rake": 0.0},
    "AR-0056g": {"max_mag": 6.85, "rake": 0.0},
}

RAKE_BY_RUP = {
    "reverse": 90.0,
    "normal": -90.0,
    "dextral": 180.0,
    "sinistral": 0.0,
    "dextral-reverse": 135.0,
    "sinistral-reverse": 45.0,
    "dextral-normal": -135.0,
    "sinistral-normal": -45.0,
}


@dataclass
class FaultModelConfig:
    """Configuration for the crustal simple-fault source model."""

    trt: str = "Active Shallow Crust"
    rupture_mesh_spacing: float = 2.0
    rupture_aspect_ratio: float = 2.0
    msr_class: type = WC1994
    bin_width: float = 0.1

    # moment-balance physics
    shear_modulus: float = 30e9
    coupling: float = 1.0
    slip_unit: str = "mm/yr"
    mw_c1: float = 1.5
    mw_c2: float = 9.1

    investigation_time: float = 1.0
    default_b: float = 1.0
    default_rake: float = 90.0

    # depth_mode: 'shapefile' uses the usd/lsd fields per fault;
    # 'zone' uses the uniform depths below, as in the original crustalfaults.xml
    depth_mode: str = "shapefile"
    zone_usd: float = 0.0
    zone_lsd: float = 20.0

    # lower magnitude bound for the GR; the original model used 6.05, so the
    # slip-derived moment is distributed over the same range. None keeps the
    # shapefile min_mag.
    min_mag_floor: float | None = 6.05

    # mmax_mode: 'shapefile' uses the max_mag field; 'geometric' computes the
    # median magnitude from the rupture area via the MSR, as the original
    # crustalfaults.xml did. Result is rounded up to a bin edge above min_mag.
    mmax_mode: str = "shapefile"

    fields: Dict[str, str] = field(default_factory=lambda: {
        "id": "id_seg",
        "name": "name",
        "dip": "dip",
        "rup_type": "rup_type",
        "usd": "usd",
        "lsd": "lsd",
        "min_mag": "min_mag",
        "max_mag": "max_mag",
        "b_val": "b_val",
        "slip": "slip_rate",
    })


def haversine_length_km(coords):
    R = 6371.0

    def seg(p1, p2):
        lon1, lat1 = map(math.radians, p1)
        lon2, lat2 = map(math.radians, p2)
        h = (math.sin((lat2 - lat1) / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
        return 2 * R * math.asin(math.sqrt(h))

    return sum(seg(coords[i], coords[i + 1]) for i in range(len(coords) - 1))


def tectonic_moment_rate(L_km, usd, lsd, dip, slip, cfg):
    """Tectonic moment rate (N·m/yr) of a planar fault, Mdot = mu*L*W*slip*chi."""
    slip_m = slip * 1e-3 if cfg.slip_unit == "mm/yr" else slip
    if lsd <= usd:
        raise ValueError("non-positive seismogenic thickness")
    W_km = (lsd - usd) / math.sin(math.radians(dip))
    return cfg.shear_modulus * (L_km * 1e3) * (W_km * 1e3) * slip_m * cfg.coupling


def a_cum_from_moment_rate(mdot, b, m_min, m_max, cfg):
    """Cumulative GR a whose truncated-GR moment integral equals mdot."""
    k = cfg.mw_c1 - b
    if abs(k) < 1e-8:
        raise ValueError("b too close to mw_c1")
    term = 10.0 ** (k * m_max) - 10.0 ** (k * m_min)
    return (math.log10(mdot) + math.log10(k) - math.log10(b)
            - math.log10(term) - cfg.mw_c2)


def calibrate_a_incr(mdot, b, m_min, m_max, cfg):
    """Incremental a such that the binned TruncatedGRMFD releases exactly mdot.

    Starts from the analytic continuous-integral a and applies one log10
    correction for OpenQuake's bin placement and max_mag rounding, which
    otherwise leave the discretized MFD short of the target moment.
    """
    a0 = a_cum_from_moment_rate(mdot, b, m_min, m_max, cfg)
    a0 += math.log10(1.0 - 10.0 ** (-b * cfg.bin_width))
    mfd = TruncatedGRMFD(min_mag=m_min, max_mag=m_max,
                         bin_width=cfg.bin_width, a_val=a0, b_val=b)
    m0 = sum(r * 10.0 ** (cfg.mw_c1 * m + cfg.mw_c2)
             for m, r in mfd.get_annual_occurrence_rates())
    return a0 + math.log10(mdot / m0)


def build_fault_sources(shp_path, cfg=None):
    """Build moment-balanced SimpleFaultSource objects from a fault shapefile.

    Parameters
    ----------
    shp_path : str or Path
        Fault shapefile (polyline traces + attribute table).
    cfg : FaultModelConfig, optional

    Returns
    -------
    list of SimpleFaultSource
    """
    cfg = cfg or FaultModelConfig()
    f = cfg.fields

    r = shapefile.Reader(str(shp_path), encoding="latin-1")
    names = [fl[0] for fl in r.fields[1:]]

    def num(rec, key, default=None):
        v = rec[names.index(key)]
        return default if v in (None, "") else float(v)

    msr = cfg.msr_class()
    tom = PoissonTOM(cfg.investigation_time)
    sources, skipped = [], []

    for i, (sh, rec) in enumerate(zip(r.shapes(), r.records())):
        sid = str(rec[names.index(f["id"])]).strip() or f"flt_{i:04d}"
        coords = [(float(x), float(y)) for x, y in sh.points]
        if len(coords) < 2:
            skipped.append(f"{sid}: <2 trace points")
            continue

        dip = num(rec, f["dip"])
        usd = num(rec, f["usd"])
        lsd = num(rec, f["lsd"])
        m_min = num(rec, f["min_mag"])
        m_max = num(rec, f["max_mag"])
        b = num(rec, f["b_val"], cfg.default_b)
        slip = num(rec, f["slip"])
        rake = RAKE_BY_RUP.get(
            str(rec[names.index(f["rup_type"])]).strip().lower(), cfg.default_rake)

        if sid in FAGNANO_OVERRIDES:
            ov = {**FAGNANO_COMMON, **FAGNANO_OVERRIDES[sid]}
            dip, usd, lsd = ov["dip"], ov["usd"], ov["lsd"]
            m_min, m_max, b = ov["min_mag"], ov["max_mag"], ov["b_val"]
            rake = ov["rake"]

        if cfg.depth_mode == "zone":
            usd, lsd = cfg.zone_usd, cfg.zone_lsd

        if cfg.min_mag_floor is not None:
            m_min = cfg.min_mag_floor

        if None in (dip, usd, lsd, slip) or m_min is None:
            skipped.append(f"{sid}: missing attribute")
            continue
        if slip <= 0 or lsd <= usd:
            skipped.append(f"{sid}: invalid geometry/slip")
            continue

        L = haversine_length_km(coords)

        if cfg.mmax_mode == "geometric":
            area = L * (lsd - usd) / math.sin(math.radians(dip))
            mw = msr.get_median_mag(area, rake)
            m_max = m_min + cfg.bin_width * math.ceil((mw - m_min) / cfg.bin_width)
        if m_max is None or m_max <= m_min:
            skipped.append(f"{sid}: invalid max_mag")
            continue
        mdot = tectonic_moment_rate(L, usd, lsd, dip, slip, cfg)
        a = calibrate_a_incr(mdot, b, m_min, m_max, cfg)

        mfd = TruncatedGRMFD(min_mag=m_min, max_mag=m_max,
                             bin_width=cfg.bin_width, a_val=a, b_val=b)
        name = str(rec[names.index(f["name"])]).strip() or sid
        sources.append(SimpleFaultSource(
            source_id=sid,
            name=name,
            tectonic_region_type=cfg.trt,
            mfd=mfd,
            rupture_mesh_spacing=cfg.rupture_mesh_spacing,
            magnitude_scaling_relationship=msr,
            rupture_aspect_ratio=cfg.rupture_aspect_ratio,
            temporal_occurrence_model=tom,
            upper_seismogenic_depth=usd,
            lower_seismogenic_depth=lsd,
            fault_trace=Line([Point(lon, lat) for lon, lat in coords]),
            dip=dip,
            rake=rake,
        ))

    print(f"built {len(sources)} sources, skipped {len(skipped)} (depth_mode={cfg.depth_mode})")
    for s in skipped:
        print("  skip", s)
    return sources


def create_crustal_fault_source_model(shp_path, xml_out, cfg=None):
    cfg = cfg or FaultModelConfig()
    sources = build_fault_sources(shp_path, cfg)
    xml_out = Path(xml_out)
    xml_out.parent.mkdir(parents=True, exist_ok=True)
    write_source_model(
        dest=str(xml_out),
        sources_or_groups=sources,
        name=f"Crustal moment-balanced faults (depth={cfg.depth_mode})",
        investigation_time=cfg.investigation_time,
    )
    print(f"wrote {xml_out}")
    return sources


def compare_rates(xml_new, xml_old, bin_width=0.1, mesh=2.0):
    """Compare annual rates between two NRML fault models.

    Prints total and per-fault rate ratios plus cumulative N(>=M) at a few
    thresholds. Faults are matched by source_id.
    """
    from openquake.hazardlib.nrml import to_python
    from openquake.hazardlib.sourceconverter import SourceConverter

    conv = SourceConverter(investigation_time=1.0, rupture_mesh_spacing=mesh,
                           width_of_mfd_bin=bin_width)
    new = {s.source_id: s for g in to_python(str(xml_new), conv) for s in g}
    old = {s.source_id: s for g in to_python(str(xml_old), conv) for s in g}

    def rates(d):
        out = []
        for s in d.values():
            out += s.mfd.get_annual_occurrence_rates()
        return out

    def n_ge(pairs, m):
        return sum(r for mm, r in pairs if mm >= m)

    rn, ro = rates(new), rates(old)
    print(f"\nrate comparison: {Path(xml_new).name} ({len(new)} src) vs "
          f"{Path(xml_old).name} ({len(old)} src)")
    for m in (5.0, 6.05, 6.5, 7.0, 7.5):
        a, b = n_ge(rn, m), n_ge(ro, m)
        ratio = a / b if b > 0 else float("inf")
        print(f"  N(M>={m:4.2f})  new={a:.4e}  old={b:.4e}  ratio={ratio:.3f}")

    common = sorted(set(new) & set(old))
    rr = []
    for sid in common:
        a = sum(r for _, r in new[sid].mfd.get_annual_occurrence_rates())
        b = sum(r for _, r in old[sid].mfd.get_annual_occurrence_rates())
        if b > 0:
            rr.append(a / b)
    rr = np.array(rr)
    print(f"  per-fault total-rate ratio over {len(rr)} common faults: "
          f"median={np.median(rr):.3f}  [{rr.min():.2f}, {rr.max():.2f}]")
    extra = sorted(set(new) - set(old))
    if extra:
        print(f"  faults only in new model: {len(extra)}")


if __name__ == "__main__":
    shp = Path("../data/active_faults/crustal_faults_chile_updated.shp")
    old_xml = Path("crustalfaults.xml")

    for depth in ("shapefile", "zone"):
        for mmax in ("shapefile", "geometric"):
            cfg = FaultModelConfig(depth_mode=depth, mmax_mode=mmax)
            out = Path(f"crustal_faults_{depth}_{mmax}mmax.xml")
            create_crustal_fault_source_model(shp, out, cfg)
            compare_rates(out, old_xml)
            print()