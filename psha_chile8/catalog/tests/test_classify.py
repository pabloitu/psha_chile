import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import classify as C


def frame(**kw):
    n = len(next(iter(kw.values())))
    d = {"z": np.full(n, 30.0), "sig": np.full(n, 5.0), "top": np.full(n, 30.0), "thk": np.full(n, 70.0), "unc": np.full(n, 10.0),
         "sea": np.zeros(n, bool), "south": np.zeros(n, bool), "pat": np.zeros(n, bool), "an": np.zeros(n, bool),
         "zone": np.full(n, "forearc"), "mech_kind": np.full(n, "none"), "hint": np.full(n, None, object),
         "zrej": np.full(n, np.nan), "nrej": np.zeros(n), "lon": np.full(n, -72.0), "lat": np.full(n, -33.0), "mw": np.full(n, 5.0),
         "yr": np.full(n, 2000.0), "in_domain": np.ones(n, bool)}
    d.update({k: np.asarray(v) for k, v in kw.items()})
    g = pd.DataFrame(d)
    g["known"] = g.z.notna()
    g["sig"] = g.sig.where(g.known)
    return g


def w(g, **kw):
    return C.classify(g, **{"w": "unc", "mech": "add", "hard": 0.8, **kw})[0]


def test_on_the_surface_with_a_thrust_is_interface():
    o = w(frame(z=[30.0, 55.0, np.nan, 30.0], top=[30.0, 30.0, 30.0, 60.0], mech_kind=["thrust"] * 4))
    assert o.cls.tolist()[:3] == ["interface"] * 3 and o.rule.tolist()[:3] == ["thrust"] * 3
    assert o.cls[3] == "crustal" and o.rule[3] == "depth"
    o = w(frame(z=[30.0, 55.0]), mech="exclude")
    assert o.cls.tolist() == ["interface", "in-slab"] and o.rule[0] == "depth"


def test_on_the_surface_with_a_normal_mechanism_is_split_without_interface():
    o = w(frame(z=[30.0], mech_kind=["other"]))
    assert o.cls[0] == "split" and o.w_interface[0] == 0 and abs(o.w_crustal[0] - 0.5) < 1e-3 and abs(o.w_inslab[0] - 0.5) < 1e-3
    assert o.n_candidates[0] == 2


def test_far_below_is_inslab_also_below_the_plate():
    o = w(frame(z=[70.0, 130.0]))
    assert o.cls.tolist() == ["in-slab", "in-slab"] and o.w_inslab.tolist() == [1.0, 1.0]


def test_near_the_edge_of_the_band_is_split_by_the_depth_error():
    o = w(frame(z=[32.0], sig=[10.0]))
    assert o.cls[0] == "split" and o.rule[0] == "depth_split"
    assert abs(o[C.COLS].sum(axis=1)[0] - 1) < 1e-3 and o.w_interface[0] > o.w_inslab[0] > o.w_crustal[0] > 0


def test_west_of_the_trench_without_depth_is_outer_rise():
    o = w(frame(z=[np.nan], sea=[True]))
    assert o.cls[0] == "outer rise" and o.w_outer_rise[0] == 1


def test_above_a_deep_slab():
    o = w(frame(z=[20.0, 60.0], top=[100.0, 100.0], zone=["arc", "arc"]))
    assert o.cls.tolist() == ["crustal", "in-slab"]


def test_no_slab():
    o = w(frame(z=[20.0, 80.0, np.nan], top=[np.nan] * 3))
    assert o.cls.tolist() == ["crustal", "unclassified", "crustal"] and o.rule.tolist() == ["no_slab", "no_slab_deep", "nodepth_no_slab"]


def test_no_depth_takes_the_shares_of_its_bin():
    z = [30.0] * 20 + [80.0] * 12 + [5.0] * 8 + [np.nan, np.nan] + [30.0] * 40
    lat = [-33.0] * 42 + [-20.0] * 40
    g = frame(z=z, lat=lat, mech_kind=["none"] * 41 + ["other"] + ["none"] * 40)
    o, tab = C.classify(g, mech="add", hard=0.8)
    assert o.rule[40] == "nodepth_share" and o.cls[40] == "split"
    assert np.allclose(o.loc[40, C.COLS[:3]].to_numpy(float), [0.5, 0.3, 0.2], atol=1e-3)
    # another mechanism than a thrust: no interface, the rest renormalised
    assert np.allclose(o.loc[41, C.COLS[:3]].to_numpy(float), [0.0, 0.6, 0.4], atol=1e-3)
    t = tab[(tab.slab_top == C.TOP_LAB[0]) & (tab.lat == C.LAT_LAB[2])]
    assert t.n.tolist() == [40, 0] and t.borrowed.tolist() == ["", "magnitude"]


def test_thin_bin_borrows_magnitude_then_latitude():
    g = frame(z=[30.0] * 20 + [80.0] * 20 + [np.nan], lat=[-33.0] * 20 + [-27.0] * 20 + [-33.0], mw=[5.0] * 40 + [6.0])
    o, tab = C.classify(g, mech="add", hard=0.8)
    assert np.allclose(o.loc[40, C.COLS[:3]].to_numpy(float), [0.5, 0.5, 0.0], atol=1e-3)
    t = tab[(tab.slab_top == C.TOP_LAB[0]) & (tab.lat == C.LAT_LAB[2]) & (tab.mag == C.MAG_LAB[1])].iloc[0]
    assert t.borrowed == "magnitude and latitude" and t.n_used == 40


def test_deep_defaults_over_a_deep_slab_are_inslab():
    g = frame(z=[np.nan, np.nan, np.nan] + [90.0] * 30, top=[90.0] * 33, zrej=[70.0, 33.0, 100.0] + [np.nan] * 30, nrej=[2, 2, 0] + [0] * 30)
    o = w(g)
    assert o.rule.tolist()[:3] == ["nodepth_deep", "nodepth_share", "nodepth_share"] and o.w_inslab[0] == 1


def test_literature_class_overrides_and_keeps_the_rule_class():
    o = w(frame(z=[70.0, np.nan], hint=["interface", "in-slab"]))
    assert o.cls.tolist() == ["interface", "in-slab"] and o.rule.tolist() == ["hint", "hint"]
    assert o.cls_auto.tolist() == ["in-slab", "split"] and o.a_inslab[0] == 1


def test_hardening():
    g = frame(z=[30.0, 30.0], sig=[5.0, 9.0])
    assert w(g).w_interface.tolist()[0] == 1 and w(g).cls[1] == "split"
    assert w(g, hard=0.7).cls.tolist() == ["interface", "interface"]
    assert w(g, hard=None).cls.tolist() == ["split", "split"]
    p = w(g, hard=None).w_interface
    assert abs(p[0] - 0.9545) < 1e-3 and abs(p[1] - 0.7335) < 1e-3


def test_band_width_and_interface_limit():
    g = frame(z=[42.0, 58.0], top=[30.0, 58.0])
    assert w(g, w=10.0).w_interface[0] < 0.5 < w(g, w=20.0).w_interface[0]
    assert w(g).cls[1] == "in-slab" and w(g, if_top=60.0).w_interface[1] > 0.9
    assert w(frame(z=[30.0], unc=[np.nan])).W[0] == C.W_NONE


def test_mechanism_modes():
    g = frame(z=[30.0, 60.0], mech_kind=["other", "thrust"])
    assert w(g, mech="none").cls.tolist() == ["interface", "in-slab"]
    assert w(g, mech="add").cls.tolist() == ["split", "interface"]


def test_subclasses_and_the_jujuy_nest():
    g = frame(z=[200.0, 200.0, 140.0, 60.0, 5.0, 5.0], top=[190.0, 190.0, 130.0, 45.0, 100.0, np.nan],
              lon=[-66.9, -65.0, -66.9, -72.0, -70.0, -72.0], lat=[-24.0, -24.0, -24.0, -33.0, -33.0, -50.0],
              zone=["backarc", "backarc", "backarc", "forearc", "arc", "forearc"], pat=[False] * 5 + [True])
    o = w(g)
    s = C.subs(g, o)
    assert s.sub_inslab.tolist() == ["jujuy_nest", "intraslab_intermediate", "intraslab_intermediate", "intraslab_shallow", "", ""]
    assert s.sub_crustal.tolist()[4:] == ["arc", "patagonia"] and s.sub_interface.tolist() == [""] * 6
    # a split event carries the sub-class of each family
    g = frame(z=[32.0], sig=[10.0])
    assert C.subs(g, w(g)).iloc[0].tolist() == ["interface", "intraslab_shallow", "forearc"]


def test_antarctic_interface():
    g = frame(z=[20.0, np.nan], top=[np.nan, np.nan], south=[True, True], pat=[True, True], an=[True, False], lat=[-50.0, -50.0])
    o = w(g)
    assert o.cls.tolist() == ["interface", "crustal"] and C.subs(g, o).sub_interface[0] == "antarctic_interface"


def test_assigned_depth_is_not_used_by_the_rules():
    g = frame(z=[np.nan, np.nan, np.nan, 20.0], top=[5.0, 80.0, 30.0, 30.0], hint=["interface", "in-slab", "crustal", "interface"])
    o = w(g)
    a = C.assigned(g, o)
    assert a.depth_assigned.tolist()[:2] == [10.0, 80.0 + C.SLAB_FRAC * 70.0] and a.depth_assigned[2:].isna().all()
    assert a.depth_assigned_sigma.tolist()[:2] == [C.SIG_ASSIGNED] * 2
    # a catalogue that carries the assigned depth is classified as if it had none
    c = pd.DataFrame({"event_id": ["a"], "time": ["2000-01-01T00:00:00.000"], "lon": [-72.0], "lat": [-33.0], "mw": [6.0], "depth": [35.0],
                      "depth_sigma": [20.0], "depth_kind": ["assigned"], "depth_src": ["assigned"], "offshore": [False], "in_domain": [True],
                      "strike1": [np.nan], "dip1": [np.nan], "rake1": [np.nan], "strike2": [np.nan], "dip2": [np.nan], "rake2": [np.nan]})
    q = C.geometry(c, rej=pd.DataFrame({"min": [], "count": []}))
    assert not q.known[0] and np.isnan(q.z[0])


def test_weights_add_to_one():
    g = np.random.default_rng(0)
    n = 400
    f = frame(z=np.where(g.random(n) < 0.2, np.nan, g.uniform(0, 150, n)), top=np.where(g.random(n) < 0.1, np.nan, g.uniform(5, 150, n)),
              sig=g.uniform(5, 20, n), mech_kind=g.choice(["none", "thrust", "other"], n), sea=g.random(n) < 0.05, mw=g.uniform(4.5, 7, n),
              lat=g.uniform(-45, -18, n), em=np.where(g.random(n) < 0.5, np.nan, g.uniform(0, 4, n)))
    for kw in ({}, {"w": 15.0}, {"hard": None}, {"mech": "ellipse"}, {"mech": "ellipse", "hard": None}, {"if_top": 60.0}):
        o = w(f, **kw)
        assert np.allclose(o[C.COLS].sum(axis=1), 1, atol=2e-4) and (o[C.COLS] >= 0).all().all()


def test_thrust_on_the_plate_contact():
    m = pd.DataFrame({"strike1": [10.0, 10.0, 100.0], "dip1": [20.0, 20.0, 80.0], "rake1": [90.0, -90.0, 0.0],
                      "strike2": [190.0, 190.0, 190.0], "dip2": [70.0, 70.0, 90.0], "rake2": [90.0, -90.0, 170.0]})
    assert C.on_contact(m, np.full(3, 5.0), np.full(3, 22.0)).tolist() == [True, False, False]


def test_depth_error_does_not_reach_above_the_ground():
    # slab top at 10 km, band from 2 to 18 km: an event at 4 km with σ 10 km is not half crustal
    o = w(frame(z=[4.0], top=[10.0], unc=[8.0], sig=[10.0]), hard=None)
    assert o.w_crustal[0] < 0.15 and o.w_interface[0] > 0.6


def test_default_band_is_fixed():
    g = frame(z=[46.0], sig=[5.0])
    o = C.classify(g, mech="add", hard=0.8)[0]
    assert o.W[0] == C.W == 15.0 and o.cls[0] == "split" and w(g).cls[0] == "in-slab"


def test_misfit_to_the_interface_mechanism():
    # slab plane strike 10, dip 20; upper plate moving up dip (azimuth 280)
    s, d, k = [10.0, 190.0, 10.0, 10.0, 10.0, 100.0], [20.0, 70.0, 20.0, 40.0, 20.0, 90.0], [90.0, 90.0, 135.0, 90.0, -90.0, 0.0]
    m = C.skew(s, d, k, np.full(6, 10.0), np.full(6, 20.0), az=280.0)
    # the mechanism itself and its other nodal plane; slip turned by 45°; plane tilted by 20°; reversed slip
    assert np.allclose(m[:5], [0, 0, 1, 1, 4], atol=1e-6) and m[5] > 1.5
    # the same from either nodal plane of an oblique mechanism
    assert np.allclose(C.skew([10.0, 234.0953], [30.0, 67.4790], [50.0, 110.3606], [10.0] * 2, [20.0] * 2)[0],
                       C.skew([10.0, 234.0953], [30.0, 67.4790], [50.0, 110.3606], [10.0] * 2, [20.0] * 2)[1], atol=1e-2)


def test_scores_by_depth():
    z, s, top = np.array([30.0, 70.0, 5.0, 32.0]), np.array([5.0, 5.0, 5.0, 10.0]), np.full(4, 30.0)
    Q = C.by_depth(z, s, top, np.full(4, 15.0), np.ones(4))
    assert np.allclose(Q.sum(1), 1) and (Q >= 0).all()
    assert Q[0, 0] > 0.95 and Q[1, 1] > 0.99 and Q[2, 2] > Q[2, 0] and Q[3, 0] > Q[3, 1] > 0
    assert np.allclose(C.by_depth(z, s, top, np.full(4, 15.0), np.zeros(4))[:, 0], 0)


def test_mechanism_inside_and_outside_the_ellipse():
    g = frame(z=[32.0] * 4 + [60.0], sig=[10.0] * 5, em=[np.nan, 0.5, 1.25, 2.0, 0.2])
    o = C.classify(g, hard=None)[0]
    p = o.w_interface
    assert p[1] > p[0] > p[2] == p[3] == 0
    assert abs(p[1] / (1 - p[1]) - C.LR * p[0] / (1 - p[0])) < 0.05
    # a mechanism inside the ellipse does not decide alone
    assert p[4] < 0.5 and o.w_inslab[4] > 0.5
    assert o.n_candidates.tolist()[:4] == [3, 3, 2, 2]


def test_no_depth_with_a_mechanism():
    z = [30.0] * 20 + [80.0] * 12 + [5.0] * 8 + [np.nan] * 3
    g = frame(z=z, em=[np.nan] * 40 + [np.nan, 0.5, 2.0])
    o = C.classify(g)[0]
    assert (o.rule[40:] == "nodepth_share").all() and o.w_interface[41] > o.w_interface[40] > o.w_interface[42] == 0
