import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import x4b_classify as X  # noqa: E402
import x4b_compare as C  # noqa: E402


def frame(**kw):
    n = len(next(iter(kw.values())))
    d = {"z": np.full(n, 30.0), "sig": np.full(n, 5.0), "known": np.ones(n, bool), "top": np.full(n, 30.0), "thk": np.full(n, 70.0),
         "sea": np.zeros(n, bool), "pat": np.zeros(n, bool), "zone": np.full(n, "forearc"), "mech": np.zeros(n, bool),
         "ifl": np.zeros(n, bool)}
    d.update({k: np.asarray(v) for k, v in kw.items()})
    return pd.DataFrame(d)


def test_band_width():
    g = frame(z=[30.0, 42.0, 48.0, 55.0, 12.0])
    assert list(X.classify(g, w=10)[0]) == ["interface", "in-slab", "in-slab", "in-slab", "crustal forearc"]
    assert list(X.classify(g, w=15)[0]) == ["interface", "interface", "in-slab", "in-slab", "crustal forearc"]
    assert list(X.classify(g, w=20)[0]) == ["interface", "interface", "interface", "in-slab", "interface"]


def test_sigma_widens_the_band():
    g = frame(z=[48.0, 48.0], sig=[2.0, 4.0])
    assert list(X.classify(g, w=15, sig=False)[0]) == ["in-slab", "in-slab"]
    assert list(X.classify(g, w=15, sig=True)[0]) == ["in-slab", "interface"]


def test_mechanism():
    # in the band with a mechanism that is not a thrust on the interface: out of the interface, by side of the top
    g = frame(z=[35.0, 25.0, 52.0, 52.0], mech=[True, True, True, True], ifl=[False, False, True, False])
    assert list(X.classify(g, mech=True)[0]) == ["in-slab", "crustal forearc", "interface", "in-slab"]
    assert list(X.classify(g, mech=False)[0]) == ["interface", "interface", "in-slab", "in-slab"]


def test_deep_slab_has_no_interface():
    g = frame(z=[70.0, 60.0, 30.0, 58.0], top=[70.0, 80.0, 80.0, 80.0], zone=["forearc", "arc", "arc", "arc"])
    assert list(X.classify(g)[0]) == ["in-slab", "unclassified", "crustal arc", "unclassified"]


def test_below_slab():
    g = frame(z=[120.0], top=[30.0], thk=[70.0], sig=[10.0])
    assert X.classify(g, below="in-slab")[0][0] == "in-slab"
    assert X.classify(g, below="unclassified")[0][0] == "below slab"
    assert X.classify(frame(z=[105.0], sig=[10.0]), sig=True, below="unclassified")[0][0] == "in-slab"


def test_position_and_unknown_depth():
    g = frame(z=[np.nan, np.nan, 20.0, 20.0, 20.0, np.nan], known=[False, False, True, True, True, False],
              sea=[False, True, True, False, False, False], pat=[False, False, False, True, False, False],
              top=[30.0, 30.0, 30.0, np.nan, np.nan, 30.0], zone=["forearc"] * 4 + ["backarc", "forearc"],
              mech=[False] * 5 + [True], ifl=[False] * 5 + [True])
    assert list(X.classify(g)[0]) == ["unknown depth", "outer rise", "outer rise", "crustal Patagonia", "crustal backarc", "interface"]
    assert X.classify(g, mech=False)[0][5] == "unknown depth"


def test_interface_like():
    # slab striking north and dipping 20 east; a thrust on that plane, the same plane with normal slip, a steep plane
    m = pd.DataFrame({"strike1": [5.0, 5.0, 5.0], "dip1": [22.0, 22.0, 80.0], "rake1": [95.0, -90.0, 90.0],
                      "strike2": [180.0, 180.0, 185.0], "dip2": [68.0, 68.0, 80.0], "rake2": [88.0, -90.0, -90.0]})
    assert list(X.interface_like(m, np.full(3, 0.0), np.full(3, 20.0))) == [True, False, False]


def test_p_interface():
    g = frame(z=[30.0, 45.0, 90.0], sig=[5.0, 5.0, 5.0])
    p = X.p_interface(g, 15.0)
    assert p[0] > 0.99 and abs(p[1] - 0.5) < 0.01 and p[2] < 1e-6


def test_sub():
    g = pd.DataFrame({"lon": [-71.0, -70.0, -66.9, -66.9, -66.9, -71.0], "lat": [-30.0, -30.0, -24.0, -24.0, -24.0, -30.0],
                      "z": [45.0, 100.0, 200.0, 120.0, np.nan, 20.0], "known": [True, True, True, True, False, True],
                      "top": [30.0, 90.0, 190.0, 190.0, 190.0, 30.0]})
    out = X.sub(g, ["in-slab"] * 5 + ["interface"])
    assert list(out) == ["intraslab_shallow", "intraslab_intermediate", "jujuy_nest", "intraslab_intermediate", "intraslab_intermediate", ""]


def test_rm18(tmp_path):
    f = tmp_path / "rm.csv"
    pd.DataFrame({"event_id": ["a", "b", "c", "d"], "rm_class": ["interface", "intraslab", "crustal", "unknown"]}).to_csv(f, index=False)
    g = pd.DataFrame({"event_id": ["a", "b", "c", "d", "e"], "pat": [False] * 5, "zone": ["forearc", "forearc", "arc", "arc", "arc"]})
    c, k = X.rm18(g, np.array(["in-slab", "unknown depth", "in-slab", "interface", "interface"], object), f)
    assert list(c) == ["interface", "in-slab", "crustal arc", "interface", "interface"] and list(k) == [True, True, True, False, False]


def test_match_one_to_one():
    t = np.array([4e9, 4e9 + 5, 4e9 + 500])
    la, lo = np.full(3, -30.0), np.full(3, -71.0)
    j = C.match(t, la, lo, np.array([4e9 + 1, 4e9 + 400]), np.array([-30.1, -30.0]), np.array([-71.0, -71.0]))
    assert list(j) == [0, -1, -1]
    assert np.isclose(C.tsec(["1900-01-01T00:01:00.000", "1513-01-01T00:00:00Z"])[0], 60.0)
