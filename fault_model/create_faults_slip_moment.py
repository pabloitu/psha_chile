# create_model_nmin.py
"""
Crustal-fault source models with activity rates from slip-rate recurrence
models (approach 1 / "Nmin variation" of Arroyo-Solorzano et al. 2025,
their Table 3), replacing the moment-balanced tgr/tap MFDs:

  al1  Anderson & Luco (1983) eq. I.10   (truncated exponential)
  al2  Anderson & Luco (1983) eq. II.9   (rate -> 0 at Mmax, linear taper)
  al3  Anderson & Luco (1983) eq. III.9  (rate -> 0 at Mmax, quadratic taper)
  yc   Youngs & Coppersmith (1985) eq. 11 (moment-balanced exponential)

Computations use the OpenQuake hmtk implementations (AndersonLucoAreaMmax,
YoungsCoppersmithExponential). Inputs per fault come from the shapefile as
in create_model.py: slip_rate (mm/yr, scaled by phi), upp_sd/low_sd, dip,
b_val, and the Mmax branch (mobs/mgeo). One NRML source model is written
per rate model, with incremental rates; for now this is the only branching
level (phi and mmax fixed in main).

Note: hmtk uses log10(M0) = 1.5 M + 9.05 (Hanks & Kanamori) internally,
vs 9.1 elsewhere in this project; diagnostics here use 9.05.
"""

from __future__ import annotations

import math
from pathlib import Path

from openquake.hazardlib.geo.line import Line
from openquake.hazardlib.geo.point import Point
from openquake.hazardlib.mfd.evenly_discretized import EvenlyDiscretizedMFD
from openquake.hazardlib.scalerel.wc1994 import WC1994
from openquake.hazardlib.source.simple_fault import SimpleFaultSource
from openquake.hazardlib.sourcewriter import write_source_model
from openquake.hazardlib.tom import PoissonTOM
from openquake.hmtk.faults.mfd.anderson_luco_area_mmax import AndersonLucoAreaMmax
from openquake.hmtk.faults.mfd.youngs_coppersmith import YoungsCoppersmithExponential

from create_model import Config, read_faults, get_mmax, moment_rate

# rate-model branching level: (hmtk A&L type or None for YC, weight)
RATE = {
    "al1": ("First", 0.25),
    "al2": ("Second", 0.25),
    "al3": ("Third", 0.25),
    "yc": (None, 0.25),
}

DISP_LENGTH_RATIO = 1.25e-5
MO_C2 = 9.05


def nmin_mfd(flt, phi, mmax, kind, cfg):
    """Incremental MFD from a slip-rate recurrence model.

    Parameters
    ----------
    flt : dict
        Fault record from read_faults.
    phi : float
        Seismic coefficient scaling the slip rate.
    mmax : float
        Mmax branch value (bin center).
    kind : str
        One of RATE: 'al1', 'al2', 'al3' (Anderson & Luco 1983,
        eqs. I.10/II.9/III.9) or 'yc' (Youngs & Coppersmith 1985).
    cfg : Config

    Returns
    -------
    EvenlyDiscretizedMFD
        Bin centers from cfg.min_mag to mmax.
    """
    if flt["b"] >= 1.5:
        raise ValueError(f"{flt['id']}: b={flt['b']} >= 1.5, invalid for A&L/YC")

    conf = {
        "Model_Type": RATE[kind][0],
        "Model_Weight": 1.0,
        "MFD_spacing": cfg.bin_width,
        "Minimum_Magnitude": cfg.min_mag,
        "Maximum_Magnitude": mmax,
        "Maximum_Magnitude_Uncertainty": None,
        "b_value": [flt["b"], 0.0],
    }
    slip = phi * flt["slip"]
    W = (flt["lsd"] - flt["usd"]) / math.sin(math.radians(flt["dip"]))
    mu_gpa = cfg.shear_modulus / 1e9

    if kind == "yc":
        model = YoungsCoppersmithExponential()
        model.setUp(conf)
        model.mmax = mmax
        m0, bw, rates = model.get_mfd(slip, flt["L"] * W, shear_modulus=mu_gpa)
    else:
        model = AndersonLucoAreaMmax()
        model.setUp(conf)
        model.mmax = mmax
        m0, bw, rates = model.get_mfd(slip, W, shear_modulus=mu_gpa,
                                      disp_length_ratio=DISP_LENGTH_RATIO)

    rates = [max(r, 0.0) for r in rates]
    return EvenlyDiscretizedMFD(min_mag=m0, bin_width=bw, occurrence_rates=rates)


def build_sources(faults, phi, mmax_mode, kind, cfg):
    msr = WC1994()
    tom = PoissonTOM(cfg.investigation_time)
    out = []
    for flt in faults:
        mmax = get_mmax(flt, mmax_mode, msr, cfg)
        mfd = nmin_mfd(flt, phi, mmax, kind, cfg)
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


def summary(sources, target_mdot):
    n, m0 = 0.0, 0.0
    for s in sources:
        for m, r in s.mfd.get_annual_occurrence_rates():
            n += r
            m0 += r * 10.0 ** (1.5 * m + MO_C2)
    return n, m0 / target_mdot


def branches():
    """Yield (branch_id, filename, kind, weight) for the rate-model level."""
    for kind, (_, w) in RATE.items():
        yield kind, f"crustal_faults_{kind}.xml", kind, w


def main(shp_path, out_dir, phi=1.0, mmax_mode="mgeo", cfg=None):
    cfg = cfg or Config()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    faults = read_faults(shp_path, cfg)
    target = sum(moment_rate(f, phi, cfg) for f in faults)

    for bid, fname, kind, w in branches():
        srcs = build_sources(faults, phi, mmax_mode, kind, cfg)
        write_source_model(
            dest=str((out_dir / fname).resolve()),
            sources_or_groups=srcs,
            name=f"Crustal faults {bid} (phi={phi}, {mmax_mode})",
            investigation_time=cfg.investigation_time,
        )
        n, mr = summary(srcs, target)
        print(f"{bid}: {len(srcs)} sources, w={w}, "
              f"N(>={cfg.min_mag})={n:.4f}/yr, moment ratio={mr:.3f}")


if __name__ == "__main__":
    main(shp_path="../data/active_faults/crustal_faults_chile_updated.shp",
         out_dir=".")