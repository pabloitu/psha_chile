"""Helpers of chaf.py and fagnano.py: scaling relations, grouping of strands, moment balance of the rates."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import chaf as C
import fagnano as F


def test_mags():
    # 50 km x 20 km strike-slip: WC94 3.98 + 1.02 log A, Leonard 2014 log A + 3.99
    wc, le = C.mags(50.0, 0.0)
    assert wc == pytest.approx(3.98 + 1.02 * 3.0)
    assert le == pytest.approx(3.0 + 3.99)


def test_groups():
    import geopandas as gpd
    g = [LineString([(-70, -30.0), (-70, -30.1)]), LineString([(-70, -30.13), (-70, -30.2)]),
         LineString([(-70, -30.3), (-70, -30.4)]), LineString([(-70, -30.13), (-70, -30.2)])]
    ch = gpd.GeoDataFrame({"F_system": ["A", "A", "A", "B"]}, geometry=g, crs="EPSG:4326")
    lab = C.groups(ch)
    # 3.3 km gap joins, 11 km gap does not, another system does not
    assert lab[0] == lab[1] and lab[2] != lab[1] and lab[3] != lab[1]


def test_rake():
    assert C.rake(["Normal-Sinistral", "Normal", None]) == -90.0
    assert C.rake([None]) is None


def test_moment_balance():
    m, r = F.rates(100.0, 7.4, 1.0, 5.0)
    mo = F.PSI * F.MU * 100e3 * F.WIDTH * 1e3 * 5e-3
    assert (r * 10 ** (1.5 * m + 9.05)).sum() == pytest.approx(mo)
    assert m[0] == pytest.approx(6.05) and m[-1] == pytest.approx(7.35)
    assert np.all(np.diff(r) < 0)
