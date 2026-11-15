"""D16b: MASCSN restoration, database B and the fault MFDs of rates.py."""
import sys
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dbB
import faultquake as F
import geo
import mascsn as M
import rates as R


def test_faultquake_moment():
    # FaultQuake truncated GR releases M0(Mmax) / Tmean at its points, with slope b
    m, r = F.rates(7.0, 500.0, 0.9)
    assert m[0] == pytest.approx(6.0) and m[-1] == pytest.approx(7.0)
    assert (r * F.m0(m)).sum() == pytest.approx(F.m0(7.0) / 500.0)
    assert -np.polyfit(m, np.log10(r), 1)[0] == pytest.approx(0.9, abs=0.02)


def test_faultquake_cap():
    # above the aspect-ratio length the recurrence no longer depends on the fault length
    t1 = F.tmean(7.0, 7.0, 80.0, 90.0, 12.0, "WC94-S")
    t2 = F.tmean(7.0, 7.0, 160.0, 90.0, 12.0, "WC94-S")
    assert t1 == t2 and F.lar("WC94-S", 12.0) == pytest.approx(28.672, abs=1e-3)


@pytest.fixture(scope="module")
def pub():
    s = M.read(M.SCC1)
    return s.set_index("id")


def test_published_is_faultquake(pub):
    # every published source: M0(Mmax) / moment rate is a whole number of years, and FaultQuake rebuilds the rates
    for x in pub.itertuples():
        m = x.m0 + 0.1 * np.arange(len(x.rates))
        t = F.m0(m[-1]) / (x.rates * F.m0(m)).sum()
        assert abs(t - round(t)) < 1e-6
        b = -np.polyfit(m, np.log10(x.rates), 1)[0] if len(m) > 1 else 1.0
        assert np.allclose(F.rates(round(m[-1], 1), round(t), b)[1], x.rates, rtol=1e-9)


def test_forward_rio_cuervo(pub):
    # Rio Cuervo (id 100): FaultQuake with WC94-S, 12 km and 7 mm/yr gives the published Mmax and rates
    x = pub.loc[100]
    L = geo.length(x.geometry)
    mx = F.mmax("WC94-S", L, x.dip, 12.0)
    tm = F.tmean(mx, 7.0, L, x.dip, 12.0, "WC94-S")
    assert mx == pytest.approx(7.0)
    assert np.allclose(F.rates(mx, tm, 0.88)[1], x.rates, rtol=1e-3)


def test_minmag_is_bin_centre():
    from openquake.hazardlib.mfd import EvenlyDiscretizedMFD
    f = EvenlyDiscretizedMFD(6.0, 0.1, [1.0, 0.5])
    assert [m for m, _ in f.get_annual_occurrence_rates()] == pytest.approx([6.0, 6.1])


@pytest.mark.parametrize("kind", R.SHAPES)
@pytest.mark.parametrize("mmax", [6.0, 6.3, 7.0, 8.0])
def test_shapes_moment(kind, mmax):
    c, r = R.mfd(kind, 1.0, mmax, 1e17)
    assert (r * R.m0(c)).sum() == pytest.approx(1e17)
    assert c[0] == pytest.approx(R.MMIN) and (r >= 0).all()
    if kind != "tap":
        assert c[-1] == pytest.approx(mmax)


def test_on_grid():
    assert R.on_grid(6.94) == pytest.approx(6.9)
    assert R.on_grid(6.96) == pytest.approx(7.0)
    assert R.on_grid(5.7) == pytest.approx(6.0)


def test_source_moment():
    r, m10, m20 = R.source(50.0, 90.0, 180.0, 1.0, 1.0)
    want = 0.8 * R.MU * 50e3 * (0.5 * 10e3 + 0.5 * 20e3) * 1e-3
    assert R.moment(r) == pytest.approx(want, rel=1e-6)
    assert m10 < m20


def test_kin():
    assert dbB.kin(90.0) == "reverse" and dbB.kin(-88.0) == "normal" and dbB.kin(180.0) == "dextral"
    assert dbB.kin(-5.0) == "sinistral" and dbB.kin(135.0) == "dextral-reverse"


@pytest.fixture(scope="module")
def b():
    import geopandas as gpd
    p = dbB.OUT.with_suffix(".gpkg")
    if not p.exists():
        pytest.skip("run dbB.py first")
    return gpd.read_file(p, layer="faults")


def test_once(b):
    assert b.fid.is_unique
    ids = b.mascsn_id.dropna()
    assert ids.is_unique
    assert b.gem_id.dropna().is_unique


def test_no_overlap(b):
    # no MASCSN trace and GEM trace overlap (within 5 km over more than half of either), and no exact copies
    m, g = b[b.src == "MASCSN26"], b[b.src != "MASCSN26"]
    tm = geo.tree(m.geometry.union_all())
    assert max(geo.near(x, tm, dbB.OVER_KM) for x in g.geometry) <= dbB.OVER_FRAC
    for x in m.geometry:
        assert geo.near(x, geo.tree(g.geometry.union_all()), dbB.OVER_KM) <= dbB.OVER_FRAC
    assert not any(b.geometry[i].equals(b.geometry[j]) for i in range(len(b)) for j in range(i + 1, len(b)))


def test_complete(b):
    assert (b.system.fillna("").ne("") | (b.sys_src == "none")).all()
    for c in ("fid", "sys_src", "name", "kin", "rake", "kin_src", "dip", "dip_src", "sr", "sr_kind", "sr_src",
              "z_top", "z_bot", "z_src", "length", "src", "src_ref"):
        assert b[c].notna().all(), c
    for c in ("sys_src", "kin_src", "dip_src", "sr_src", "z_src", "src", "src_ref"):
        assert (b[c] != "").all(), c
    assert (b.dip_dir.notna() | b.vertical.astype(bool)).all()
    assert (b.sr > 0).all() and (b["length"] > 0).all()
    assert np.allclose(b["length"], b.geometry.apply(geo.length), rtol=0.01)
    m = b[b.src == "MASCSN26"]
    assert m[["mmax_mascsn", "b_mascsn", "mo_mascsn", "sr_mascsn", "t_fq", "tmean_fq"]].notna().all().all()
    assert m.t_fq.astype(float).between(5, 40).all() and (m.tmean_fq.astype(float) % 1 == 0).all()


def test_fagnano_border(b):
    f = b[b.system == "Magallanes–Fagnano"]
    for r in f.itertuples():
        x0, _, x1, _ = r.geometry.bounds
        assert (x1 <= dbB.db.BORDER + 1e-6) if r.src == "MASCSN26" else (x0 >= dbB.db.BORDER - 1e-6)
    assert (f[f.sr_kind == "measured"].sr == 5.9).all()


def test_source_fixed_moment():
    # a fixed moment (MASCSN budget) is taken as given in both depth branches, times the mean psi
    r, _, _ = R.source(80.0, 90.0, 180.0, 0.0, 1.0, fixed=2e17, Lsr=0.0)
    assert R.moment(r) == pytest.approx(0.8 * 2e17, rel=1e-6)


def test_budget_capped():
    # the MASCSN budget of a capped trace does not grow with its length
    import pandas as pd
    import compare
    x = pd.DataFrame({"t_fq": [12.0, 12.0], "dip": [90.0, 90.0], "sr": [7.0, 7.0], "length": [60.0, 120.0],
                      "scr_fq": ["WC94-S", "WC94-S"]})
    assert compare.budget(x.iloc[:1]) == pytest.approx(compare.budget(x.iloc[1:]))
