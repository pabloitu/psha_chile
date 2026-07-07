# create_crustal_fault_source_model.py
"""
Build the crustal-fault branch of the SSM logic tree from the fault
shapefile (crustal_faults_chile_updated.shp).

Each fault carries a GR-type MFD whose total moment release matches the
tectonic moment rate Mdot = phi * mu * L * W * slip_rate, with depths taken
from the upp_sd/low_sd fields. Branches:

  phi   0.5 (0.25) | 0.75 (0.50) | 1.0 (0.25)
  mmax  observed max_mag + 0.2 (0.5) | WC1994 geometric + 0.2 (0.5)
  mfd   truncated GR (0.5) | tapered GR (0.5)

All 12 combinations are written as NRML source models with incremental
(evenly discretized) rates. The SSM logic tree combining these with the
other tectonic sources is built separately by build_ssm_logictree.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import shapefile

from openquake.hazardlib.geo.line import Line
from openquake.hazardlib.geo.point import Point
from openquake.hazardlib.mfd.evenly_discretized import EvenlyDiscretizedMFD
from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
from openquake.hazardlib.mfd.tapered_gr_mfd import TaperedGRMFD
from openquake.hazardlib.scalerel.wc1994 import WC1994
from openquake.hazardlib.source.simple_fault import SimpleFaultSource
from openquake.hazardlib.sourcewriter import write_source_model
from openquake.hazardlib.tom import PoissonTOM

# logic tree branches: value/weight per branching level
PHI = {"phi050": (0.50, 0.25), "phi075": (0.75, 0.50), "phi100": (1.00, 0.25)}
MMAX = {"mobs": 0.5, "mgeo": 0.5}
MFD = {"tgr": 0.5, "tap": 0.5}

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
class Config:
    trt: str = "Active Shallow Crust"
    mesh_spacing: float = 2.0
    aspect_ratio: float = 2.0
    bin_width: float = 0.1
    investigation_time: float = 1.0

    shear_modulus: float = 30e9
    mw_c1: float = 1.5
    mw_c2: float = 9.1

    min_mag: float = 6.05
    mmax_add: float = 0.2
    taper_pad: float = 0.5
    default_b: float = 1.0
    default_rake: float = 90.0

    fields: dict = field(default_factory=lambda: {
        "id": "id_seg",
        "name": "name",
        "dip": "dip",
        "rup_type": "rup_type",
        "usd": "upp_sd",
        "lsd": "low_sd",
        "max_mag": "max_mag",
        "b_val": "b_val",
        "slip": "slip_rate",
    })


def fault_length_km(coords):
    R = 6371.0

    def seg(p1, p2):
        lon1, lat1 = map(math.radians, p1)
        lon2, lat2 = map(math.radians, p2)
        h = (math.sin((lat2 - lat1) / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
        return 2 * R * math.asin(math.sqrt(h))

    return sum(seg(coords[i], coords[i + 1]) for i in range(len(coords) - 1))


def read_faults(shp_path, cfg):
    """Read fault traces and attributes from the shapefile.

    Parameters
    ----------
    shp_path : str or Path
        Fault shapefile with polyline traces and the attribute fields
        listed in ``cfg.fields``.
    cfg : Config

    Returns
    -------
    list of dict
        One record per usable fault: id, name, coords, L, dip, rake,
        usd, lsd, slip, b, m_obs.
    """
    r = shapefile.Reader(str(shp_path), encoding="latin-1")
    names = [fl[0] for fl in r.fields[1:]]
    f = cfg.fields

    def num(rec, key, default=None):
        v = rec[names.index(key)]
        return default if v in (None, "") else float(v)

    faults, skipped = [], []
    for i, (sh, rec) in enumerate(zip(r.shapes(), r.records())):
        sid = str(rec[names.index(f["id"])]).strip() or f"flt_{i:04d}"
        coords = [(float(x), float(y)) for x, y in sh.points]
        if len(coords) < 2:
            skipped.append(f"{sid}: <2 trace points")
            continue

        dip = num(rec, f["dip"])
        usd = num(rec, f["usd"])
        lsd = num(rec, f["lsd"])
        slip = num(rec, f["slip"])
        m_obs = num(rec, f["max_mag"])
        b = num(rec, f["b_val"]) or cfg.default_b
        rake = RAKE_BY_RUP.get(
            str(rec[names.index(f["rup_type"])]).strip().lower(), cfg.default_rake)

        if None in (dip, usd, lsd, slip, m_obs):
            skipped.append(f"{sid}: missing attribute")
            continue
        if slip <= 0 or lsd <= usd or not 0 < dip <= 90:
            skipped.append(f"{sid}: invalid geometry/slip")
            continue
        if m_obs <= cfg.min_mag:
            skipped.append(f"{sid}: max_mag {m_obs} <= min_mag")
            continue

        faults.append(dict(
            id=sid,
            name=str(rec[names.index(f["name"])]).strip() or sid,
            coords=coords, L=fault_length_km(coords),
            dip=dip, rake=rake, usd=usd, lsd=lsd,
            slip=slip, b=b, m_obs=m_obs,
        ))

    print(f"read {len(faults)} faults, skipped {len(skipped)}")
    for s in skipped:
        print("  skip", s)
    return faults


def moment_rate(flt, phi, cfg):
    W = (flt["lsd"] - flt["usd"]) / math.sin(math.radians(flt["dip"]))
    return phi * cfg.shear_modulus * flt["L"] * 1e3 * W * 1e3 * flt["slip"] * 1e-3


def get_mmax(flt, mode, msr, cfg):
    if mode == "mobs":
        mmax = flt["m_obs"] + cfg.mmax_add
    else:
        W = (flt["lsd"] - flt["usd"]) / math.sin(math.radians(flt["dip"]))
        mmax = msr.get_median_mag(flt["L"] * W, flt["rake"]) + cfg.mmax_add
    n = math.ceil(round((mmax - cfg.min_mag) / cfg.bin_width, 6))
    return cfg.min_mag + cfg.bin_width * max(n, 1)


def balanced_mfd(mdot, b, m_max, kind, cfg):
    """Incremental MFD whose discrete moment release equals mdot.

    Builds a truncated or tapered GR with a placeholder a-value, then
    rescales the bin rates so that sum(rate * Mo(m)) == mdot. For the
    tapered form the corner magnitude is m_max and the discretization
    extends taper_pad above it.

    Parameters
    ----------
    mdot : float
        Target moment rate in N·m/yr.
    b : float
        GR b-value.
    m_max : float
        Mmax branch value (truncation or corner magnitude).
    kind : str
        'tgr' or 'tap'.
    cfg : Config

    Returns
    -------
    EvenlyDiscretizedMFD
    """
    if kind == "tgr":
        mfd = TruncatedGRMFD(min_mag=cfg.min_mag, max_mag=m_max,
                             bin_width=cfg.bin_width, a_val=4.0, b_val=b)
    else:
        mfd = TaperedGRMFD(min_mag=cfg.min_mag, max_mag=m_max + cfg.taper_pad,
                           corner_mag=m_max, bin_width=cfg.bin_width,
                           a_val=4.0, b_val=b, c_val=cfg.mw_c2)

    mags, rates = zip(*mfd.get_annual_occurrence_rates())
    m0 = sum(r * 10.0 ** (cfg.mw_c1 * m + cfg.mw_c2) for m, r in zip(mags, rates))
    k = mdot / m0
    return EvenlyDiscretizedMFD(min_mag=mags[0], bin_width=cfg.bin_width,
                                occurrence_rates=[r * k for r in rates])


def build_sources(faults, phi, mmax_mode, mfd_kind, cfg):
    msr = WC1994()
    tom = PoissonTOM(cfg.investigation_time)
    out = []
    for flt in faults:
        mdot = moment_rate(flt, phi, cfg)
        mmax = get_mmax(flt, mmax_mode, msr, cfg)
        mfd = balanced_mfd(mdot, flt["b"], mmax, mfd_kind, cfg)
        out.append(SimpleFaultSource(
            source_id=flt["id"],
            name=flt["name"],
            tectonic_region_type=cfg.trt,
            mfd=mfd,
            rupture_mesh_spacing=cfg.mesh_spacing,
            magnitude_scaling_relationship=msr,
            rupture_aspect_ratio=cfg.aspect_ratio,
            temporal_occurrence_model=tom,
            upper_seismogenic_depth=flt["usd"],
            lower_seismogenic_depth=flt["lsd"],
            fault_trace=Line([Point(lon, lat) for lon, lat in flt["coords"]]),
            dip=flt["dip"],
            rake=flt["rake"],
        ))
    return out


def total_moment(sources, cfg):
    return sum(r * 10.0 ** (cfg.mw_c1 * m + cfg.mw_c2)
               for s in sources for m, r in s.mfd.get_annual_occurrence_rates())


def branches():
    """Yield (branch_id, filename, phi, mmax_mode, mfd_kind, weight) tuples."""
    for pid, (phi, w_phi) in PHI.items():
        for mid, w_mmax in MMAX.items():
            for kid, w_mfd in MFD.items():
                bid = f"{pid}_{mid}_{kid}"
                yield bid, f"crustal_faults_{bid}.xml", phi, mid, kid, w_phi * w_mmax * w_mfd


def main(shp_path, out_dir, cfg=None):
    cfg = cfg or Config()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    faults = read_faults(shp_path, cfg)

    for bid, fname, phi, mid, kid, w in branches():
        target = sum(moment_rate(f, phi, cfg) for f in faults)
        srcs = build_sources(faults, phi, mid, kid, cfg)
        write_source_model(
            dest=str(out_dir / fname),
            sources_or_groups=srcs,
            name=f"Crustal faults {bid}",
            investigation_time=cfg.investigation_time,
        )
        print(f"{bid}: {len(srcs)} sources, w={w}, "
              f"moment ratio={total_moment(srcs, cfg) / target:.6f}")


if __name__ == "__main__":
    main(shp_path="../data/active_faults/crustal_faults_chile_updated.shp",
         out_dir="out/crustal_faults")