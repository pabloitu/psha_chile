import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import x3_gccel as x3  # noqa: E402


def test_stat():
    s = x3.stat([1.0, 2.0, 3.0, -10.0, np.nan])
    assert s["n"] == 4 and s["med"] == 1.5
    assert np.isclose(s["rsd"], 1.4826)
    assert np.isclose(s["mean_abs"], 4.0)


def test_window_scale():
    assert list(x3.fac(np.array([5.9, 6.0, 7.2, 8.5, np.nan]))) == [1.0, 1.5, 2.0, 3.0, 1.0]


def test_link_one_to_one():
    # two GCCEL events 3 s apart, one baseline event near both: only the closer links; a far event does not link
    g = pd.DataFrame({"src_id": ["a", "b", "c"], "t": [1000.0, 1003.0, 5000.0], "lat": [-30.0, -30.0, -30.0],
                      "lon": [-71.0, -71.0, -71.0], "m": [4.0, 4.0, 4.0]})
    o = pd.DataFrame({"t": [1000.5, 1000.6, 9000.0], "lat": [-30.05, -30.04, -30.0], "lon": [-71.0, -71.0, -71.0],
                      "mmax": [4.2, 4.1, 4.0]})
    lab = np.array([7, 7, 9])
    r = x3.link(g, o, lab)
    assert r.ev.tolist()[0] == 7 and np.isnan(r.ev.iloc[1]) and np.isnan(r.ev.iloc[2])
    assert r.why.tolist() == ["linked", "candidate taken by another GCCEL event",
                              "no origin within 120 s / 450 km"]


def test_link_scales_with_magnitude():
    # 70 km apart: outside 50 km at M 5, inside the doubled window at M 7
    g = pd.DataFrame({"src_id": ["a"], "t": [0.0], "lat": [-30.0], "lon": [-71.0], "m": [5.0]})
    o = pd.DataFrame({"t": [1.0], "lat": [-30.0 - 70 / 111.195], "lon": [-71.0], "mmax": [5.0]})
    assert x3.link(g, o, np.array([1])).why.iloc[0] == "nearest origin outside the baseline window"
    assert x3.link(g.assign(m=7.0), o, np.array([1])).ev.iloc[0] == 1
