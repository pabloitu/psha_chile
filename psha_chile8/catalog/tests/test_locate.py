import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import locate as G

NONE = pd.DataFrame(columns=["src", "agency", "period", "depth", "value", "how"])
EAST = lambda lon, lat: np.asarray(lon, float) > -69.0
SEA = lambda lon, lat: np.asarray(lon, float) < -72.0


def case(recs, yr=2010.0, dflt=NONE, qual={}):
    """One event from records (key, lat, lon, z, fixed)."""
    src = {"ehb1": "iscehb", "ehb2": "iscehb", "ehb3": "iscehb", "cent_ehb": "centennial"}
    R = pd.DataFrame([{"event_id": "e", "key": k, "src": src.get(k, k), "src_id": f"{k}1", "origin_id": f"{k}1",
                       "agency": {"comcat": "us", "isc": "ISC", "iscgem": "ISC-GEM"}.get(k, k), "t": 3.4e9 + i, "yr": yr, "lat": la,
                       "lon": lo, "z": z, "fixed": fx, "quality": qual.get(k)} for i, (k, la, lo, z, fx) in enumerate(recs)])
    e = pd.DataFrame({"event_id": ["e"], "yr": [yr]})
    return G.build(e, R, dflt, back=EAST, off=SEA)[0].iloc[0]


def test_inside_the_network_the_local_catalogue_is_first():
    r = case([("potin", -33.0, -71.5, 40.0, False), ("isc", -33.1, -71.4, 35.0, False), ("comcat", -33.1, -71.3, 30.0, False)])
    assert r.inside_network and r.loc_src == "potin" and r.depth_src == "potin" and r.depth == 40.0 and r.loc_src_id == "potin1"
    r = case([("csn", -33.0, -71.5, 40.0, False), ("gccel", -33.05, -71.5, 44.0, False)], yr=2021.0)
    assert r.loc_src == "csn"


def test_outside_the_network_the_global_sources_are_first():
    for la, lo in ((-17.0, -71.0), (-50.0, -74.0), (-31.5, -68.0)):
        r = case([("potin", la, lo, 40.0, False), ("isc", la, lo + 0.1, 35.0, False), ("ehb2", la, lo + 0.2, 33.0, False)])
        assert not r.inside_network and r.loc_src == "ehb2" and r.depth_src == "ehb2"
    r = case([("potin", -50.0, -74.0, 40.0, False)])
    assert r.loc_src == "potin" and not r.inside_network


def test_distant_event_mislocated_by_the_local_network():
    r = case([("potin", -30.0, -71.0, 60.0, False), ("isc", -22.0, -66.0, 200.0, False)])
    assert not r.inside_network and r.loc_src == "isc" and r.depth == 200.0
    r = case([("potin", -30.0, -68.9, 60.0, False), ("isc", -30.1, -69.2, 50.0, False)])
    assert r.inside_network and r.loc_src == "potin"


def test_local_record_far_from_the_teleseismic_members_not_used():
    r = case([("potin", -38.0, -73.0, 5.0, False), ("isc", -38.0, -73.7, 22.0, False), ("comcat", -38.1, -73.8, 25.0, False)])
    assert not r.inside_network and r.loc_src == "isc" and r.depth == 22.0
    r = case([("potin", -38.0, -73.0, 5.0, False), ("isc", -38.0, -73.7, 22.0, False), ("comcat", -38.1, -73.2, 25.0, False)])
    assert r.inside_network and r.loc_src == "potin"


def test_offshore_depth_from_gccel_and_ehb_before_the_local_catalogue():
    r = case([("potin", -33.0, -72.5, 2.0, False), ("ehb2", -33.1, -72.4, 21.0, False), ("isc", -33.1, -72.4, 30.0, False)])
    assert r.inside_network and r.offshore and r.loc_src == "potin" and r.depth_src == "ehb2" and r.depth == 21.0
    r = case([("potin", -33.0, -72.5, 32.0, False), ("isc", -33.1, -72.4, 30.0, False)])
    assert r.depth_src == "potin"
    r = case([("potin", -33.0, -71.5, 40.0, False), ("ehb1", -33.1, -71.4, 48.0, False)])
    assert not r.offshore and r.depth_src == "potin"


def test_fixed_ehb_depths():
    r = case([("ehb1", -19.0, -70.0, 69.7, True), ("isc", -19.1, -70.0, 19.0, False)])
    assert r.depth_src == "ehb1" and r.depth == 69.7 and r.depth_kind == "measured"
    r = case([("ehb2", -19.0, -70.0, 19.9, True), ("isc", -19.1, -70.0, 41.0, False)])
    assert r.loc_src == "ehb2" and r.depth_src == "isc"
    r = case([("ehb2", -19.0, -70.0, 19.9, True), ("isc", -19.1, -70.0, 35.0, True)])
    assert r.depth_kind == "unknown"


def test_before_1982_the_local_catalogue_is_not_first():
    r = case([("potin", -33.0, -71.5, 40.0, False), ("isc", -33.1, -71.4, 35.0, False)], yr=1981.5)
    assert not r.inside_network and r.loc_src == "isc"


def test_fixed_depth_skipped_for_a_later_measured_one():
    r = case([("potin", -50.0, -74.0, 20.0, False), ("isc", -50.0, -74.1, 33.0, True), ("comcat", -50.1, -74.0, 27.0, False)])
    assert r.loc_src == "isc" and r.depth_src == "comcat" and r.depth == 27.0 and r.depth_kind == "measured"
    assert "depth_from_another_source" in r["flags"] and "loc_src_depth_not_measured" in r["flags"] and r.depth_of_loc_src == 33.0
    r = case([("ehb3", -50.0, -74.0, 15.0, False), ("gcmt", -50.0, -74.1, 22.0, False)])
    assert r.loc_src == "ehb3" and r.depth_src == "gcmt"


def test_all_depths_fixed_gives_unknown():
    r = case([("isc", -50.0, -74.0, 35.0, True), ("comcat", -50.0, -74.1, 10.0, True), ("gccel", -50.0, -74.0, 12.0, True)])
    assert r.depth_kind == "unknown" and np.isnan(r.depth) and np.isnan(r.depth_sigma) and "depth_unknown" in r["flags"]
    assert r.loc_src == "gccel" and r.depth_of_loc_src == 12.0


def test_default_bin_recognised():
    g = np.random.default_rng(0)
    z = np.r_[g.uniform(0, 200, 5000), np.full(400, 33.0)]
    allo = pd.DataFrame({"src": "comcat", "agency": "us", "z": z, "yr": 2005.0})
    d = G.defaults(allo)
    a = d[(d.period == "all") & (d.how == "spike")]
    assert a.depth.tolist() == [33] and a.value.tolist() == [33.0]
    assert {10, 35} <= set(d[(d.src == "comcat") & (d.how == "documented")].depth)
    r = case([("comcat", -50.0, -74.0, 33.0, False), ("isc", -50.0, -74.0, 41.0, False)], dflt=d)
    assert r.loc_src == "isc"
    r = case([("comcat", -50.0, -74.0, 33.0, False), ("potin", -50.0, -74.0, 41.0, False)], dflt=d)
    assert r.loc_src == "comcat" and r.depth_src == "potin"
    r = case([("comcat", -50.0, -74.0, 33.4, False)], dflt=d)
    assert r.depth_kind == "measured" and r.depth == 33.4


def test_gcmt_centroid_never_chosen():
    e, R, allo = G.records()
    g = R[R.src == "gcmt"]
    assert len(g) > 2000 and not g.origin_id.str.endswith("_hyp").eq(False).any() and (g.key == "gcmt").all()
    assert (allo.agency == "GCMT centroid").sum() > 2000


def test_old_events():
    r = case([("cent_ehb", -33.0, -72.0, 30.0, False), ("iscgem", -33.2, -72.1, 25.0, False), ("isc", -33.5, -72.0, 0.0, False)], yr=1928.0)
    assert r.loc_src == "cent_ehb"
    r = case([("centennial", -33.0, -72.0, 0.0, False), ("iscgem", -33.2, -72.1, 27.3, False)], yr=1950.0, qual={"iscgem": "C"})
    assert r.loc_src == "iscgem" and r.depth_kind == "unknown"
    r = case([("centennial", -33.0, -72.0, 0.0, False), ("iscgem", -33.2, -72.1, 25.0, False)], yr=1950.0, qual={"iscgem": "A"})
    assert r.depth == 25.0 and r.depth_sigma == G.SIG_OLD
    r = case([("iscgem", -33.2, -72.1, 27.3, False), ("isc", -33.2, -72.1, 31.0, False), ("comcat", -33.2, -72.1, 27.3, False)], yr=1950.0)
    assert r.depth_kind == "unknown"
    r = case([("cabello", -33.0, -72.0, 30.0, False), ("centennial", -33.2, -72.1, 27.0, False)], yr=1880.0, qual={"centennial": "DEQ d"})
    assert r.loc_src == "cabello" and r.depth_src == "centennial"
    r = case([("cabello", -33.0, -72.0, 30.0, False)], yr=1880.0)
    assert r.depth_kind == "unknown"


def test_sigma_and_offshore_floor_and_domain():
    r = case([("ehb1", -50.0, -74.0, 40.0, False)])
    assert r.offshore and r.depth_sigma == G.SIG_OFF and "sigma_offshore_floor" in r["flags"]
    r = case([("ehb1", -30.0, -70.0, 40.0, False)])
    assert r.depth_sigma == G.SIG_MIN and not r.offshore and r.in_domain
    r = case([("potin", -30.0, -70.0, 120.0, False)])
    assert r.depth_sigma > G.SIG_MIN
    r = case([("cent_ehb", -16.0, -70.0, 121.0, False)], yr=1930.0, qual={"cent_ehb": "DEQ"})
    assert not r.in_domain and "sigma_largest_of_range" in r["flags"]


def test_maule_moment_check():
    m = pd.DataFrame({"mrr": [9.836e21], "mtt": [4.929e20], "mpp": [-1.033e22], "mrt": [9.52e20], "mrp": [-2.011e22], "mtp": [-1.413e21]})
    assert abs(G.tensor_m0(m)[0] / 2.257e22 - 1) < 0.01
    R = pd.DataFrame({"event_id": ["maule"], "src": ["comcat"], "src_id": ["official20100227063411530_30"]})
    r = G.mechanisms(R).iloc[0]
    assert r.mech_src == "ComCat duputel" and abs(r.mech_mw - 8.8) < 0.06 and r.mech_flag == ""
    c = pd.read_csv(G.SRC / f"comcat_mt_{G.FROZEN}_mechs.csv")
    w = c[c.code.str.endswith("20100227063411530_22_C_WCMT")]
    assert abs(float(w.m0.iloc[0]) / G.tensor_m0(w).iloc[0] - 1) > G.M0_TOL

