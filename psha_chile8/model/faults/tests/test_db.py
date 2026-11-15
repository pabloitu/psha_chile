"""The clean fault database of D16 (data/faults/faults_<DATE>.gpkg) and the helpers that build it."""
import sys
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db as D
import geo

AREA = D.AREA + ["upp_sd", "low_sd", "len_st", "az_tr", "slip_rate", "rup_type", "id_seg", "id_flt", "dips"]


@pytest.fixture(scope="module")
def f():
    import geopandas as gpd
    p = D.OUT.with_suffix(".gpkg")
    if not p.exists():
        pytest.skip("run db.py first")
    return gpd.read_file(p, layer="faults")


def test_complete(f):
    assert f.geometry.notna().all() and (~f.geometry.is_empty).all()
    assert f.dip.between(0, 90, inclusive="right").all()
    assert (f.dip_dir.notna() | f.vertical.astype(bool)).all()
    assert f.kin.notna().all() and f.rake.notna().all()
    assert (f.sr > 0).all() and f.sr_kind.isin(["measured", "range", "class"]).all()
    assert (f["length"] > 0).all()
    assert f.fid.is_unique


def test_no_area_fields(f):
    assert not set(AREA) & set(f.columns)


def test_lengths(f):
    L = f.geometry.apply(geo.length)
    assert np.allclose(f["length"], L, rtol=0.01)


def test_sources(f):
    for c in ("src", "kin_src", "dip_src", "sr_src", "z_src", "sys_src"):
        assert f[c].notna().all() and (f[c] != "").all(), c


def test_length_known():
    # one degree of latitude on WGS84 near 33 S is 110.9 km
    assert geo.length(LineString([(-70, -33.5), (-70, -32.5)])) == pytest.approx(110.9, abs=0.1)


def test_near():
    a = LineString([(-70, -33.0), (-70, -33.2)])
    b = LineString([(-70.01, -33.1), (-70.01, -33.5)])
    # b is 0.93 km east of a; half of a lies beside b, plus the reach of 2 km round the end of b
    L = geo.length(a)
    assert geo.near(a, b, 2.0) == pytest.approx(0.5 + np.sqrt(2.0 ** 2 - 0.93 ** 2) / L, abs=0.01)
    assert geo.near(a, b, 0.5) == 0.0


def test_bounds():
    assert D.bounds("0.1-1") == (0.1, 1.0)
    assert D.bounds("0.3 0.5") == (0.3, 0.5)
    assert D.bounds("45a60") == (45.0, 60.0)
    assert D.bounds("0.4") == (0.4, 0.4)
    assert D.bounds(None) is None


def test_curated():
    import geopandas as gpd
    import curate as C
    p = C.OUT.with_suffix(".shp")
    if not p.exists():
        pytest.skip("run curate.py first")
    f = gpd.read_file(p)
    assert f.geometry.notna().all() and f.fid.is_unique
    assert np.allclose(f["length"], f.geometry.apply(geo.length), rtol=0.01)
    k = f.system == "Magallanes–Fagnano"
    assert k.any() and (f.sr[k] == C.FAGNANO_SR[0]).all()
