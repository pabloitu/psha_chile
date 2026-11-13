import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import magnitude as G


def gr_pairs(n=40000, a=0.3, b=0.9, sx=0.2, sy=0.08, seed=0):
    g = np.random.default_rng(seed)
    m = 4.0 + g.exponential(1 / np.log(10), n)
    return m, a + b * m + g.normal(0, sx, n), m + g.normal(0, sy, n), g


def line(a, b, s=0.2, sy=0.1, lo=3.5, hi=6.5):
    f = {"p": (a + b * G.KREF, b, b, G.KREF), "s": s, "sy": sy, "n": 1000, "xmin": lo, "xmax": hi}
    return {"scale": "", "form": "linear", "split": "none", "parts": {"all": f}, "sigma": 0.2, "cv": {}}


def events(rows):
    """rows: per event a dict scale -> value (key yr for the year)."""
    e = pd.DataFrame({"event_id": [f"e{i}" for i in range(len(rows))], "yr": [r.get("yr", 2015.0) for r in rows],
                      "z": 20.0, "lat": -33.0, "lon": -72.0})
    M = pd.DataFrame([{"event_id": f"e{i}", "scale": k, "mag": v, "err": np.nan, "src": "isc", "src_id": str(i),
                       "agency": k.split()[-2], "mag_type": k.split()[-1], "note": None}
                      for i, r in enumerate(rows) for k, v in r.items() if k != "yr"])
    return e, M


RM = pd.DataFrame(columns=["event_id", "src_id", "mag", "sig", "note", "flags"])


# regression
def test_inverse_recovers_relation_under_reference_floor():
    m, x, y, g = gr_pairs()
    k = g.random(len(y)) < 1 / (1 + np.exp(-(y - 5.3) / 0.1))
    f = G.fit_inv(y[k], x[k], 0.08)
    true = (np.array([4.0, 4.5, 5.0]) - 0.3) / 0.9
    assert abs(f["p"][1] - 0.9) < 0.04
    assert np.abs(G.conv(f, np.array([4.0, 4.5, 5.0]))[0] - true).max() < 0.08


def test_forward_fit_fails_under_reference_floor():
    m, x, y, g = gr_pairs()
    k = y >= 5.3
    b, a = np.polyfit(x[k], y[k], 1)
    assert a + b * 4.5 - (4.5 - 0.3) / 0.9 > 0.2
    f = G.fit_fwd(x[k], y[k], 0.2, 0.08)
    assert G.conv(f, np.array([4.5]))[0][0] - (4.5 - 0.3) / 0.9 > 0.03


def test_forward_chisquare_exact_without_selection():
    m, x, y, g = gr_pairs()
    f = G.fit_fwd(x, y, 0.2, 0.08)
    assert abs(G.conv(f, np.array([4.5]))[0][0] - (4.5 - 0.3) / 0.9) < 0.02


def test_hinge_reduces_to_line_on_linear_data():
    g = np.random.default_rng(1)
    y = g.uniform(4.0, 7.0, 6000)
    x = 0.5 + 0.9 * y + g.normal(0, 0.15, len(y))
    a, b = G.fit_inv(y, x, 0.0, "linear"), G.fit_inv(y, x, 0.0, "hinge")
    v = np.arange(3.5, 7.01, 0.5)
    assert b["p"][2] <= b["p"][1]
    assert np.abs(G.conv(a, v)[0] - G.conv(b, v)[0]).max() < 0.05


def test_hinge_recovers_saturation():
    g = np.random.default_rng(1)
    y = g.uniform(4.5, 7.5, 5000)
    x = np.where(y < 6.0, y, 6.0 + 0.4 * (y - 6.0)) + g.normal(0, 0.1, len(y))
    a, b1, b2, k = G.fit_inv(y, x, 0.0, "hinge")["p"]
    assert abs(k - 6.0) < 0.15 and abs(b1 - 1.0) < 0.05 and abs(b2 - 0.4) < 0.05


def test_selection_prefers_line_on_linear_data_and_hinge_on_saturating():
    g = np.random.default_rng(2)
    y = g.uniform(4.5, 7.5, 3000)
    yr, z = g.uniform(1980, 2020, len(y)), g.uniform(0, 100, len(y))
    lin = G.fit_scale("X mb", 0.5 + 0.9 * y + g.normal(0, 0.2, len(y)), y, yr, z, 0.0, boot=0)
    sat = G.fit_scale("X mb", np.where(y < 6, y, 6 + 0.4 * (y - 6)) + g.normal(0, 0.2, len(y)), y, yr, z, 0.0, boot=0)
    assert (lin["form"], lin["split"]) == ("linear", "none") and (sat["form"], sat["split"]) == ("hinge", "none")
    few = G.fit_scale("X mb", (0.5 + 0.9 * y)[:60], y[:60], yr[:60], z[:60], 0.0, boot=0)
    assert few["form"] == "linear" and not few["cv"]


def test_sigma_without_the_reference_error():
    m, x, y, g = gr_pairs(sx=0.2, sy=0.10)
    f = G.fit_inv(y, x, 0.10)
    assert abs(G.conv(f, np.array([5.0]))[1][0] - 0.2 / 0.9) < 0.01
    assert f["s"] / f["p"][1] > G.conv(f, np.array([5.0]))[1][0]


def test_sigma_grows_outside_the_range():
    r = line(0.3, 0.9)
    y, s, _, out = G.convert(r, np.array([5.0, 7.5, 2.5]), np.full(3, 20.0), np.full(3, 2000.0))
    assert out.tolist() == [False, True, True] and np.allclose(s[1:] - s[0], G.GROW * 1.0)


# dithering
def test_dither_keeps_the_mean_and_removes_the_comb():
    g = np.random.default_rng(3)
    x = np.round(4.0 + g.exponential(1 / np.log(10), 60000), 1)
    e, M = events([{"ISC mb": v} for v in x])
    d = G.proxies(e, M, {"ISC mb": line(1.2, 0.75)})["ISC mb"]
    comb, flat = np.round(d.raw + 1e-9, 1), np.round(d.y + 1e-9, 1)
    assert abs(d.y.mean() - d.raw.mean()) < 0.002
    n = lambda v: np.array([(np.abs(v - q) < 1e-6).sum() for q in np.arange(4.0, 5.01, 0.1)])
    assert (n(comb) == 0).any() and (n(flat) > 0).all()
    r = n(flat)[1:] / n(flat)[:-1]
    assert r.max() < 1.0 and r.min() > 0.6
    again = G.proxies(e, M, {"ISC mb": line(1.2, 0.75)})["ISC mb"]
    assert (again.y == d.y).all()


# reference and hierarchy
def test_reference_order():
    e, M = events([{"GCMT Mw": 5.2, "NEIC Mww": 5.1}, {"GCMT Mw": 6.0, "NEIC Mww": 6.0}, {"GCMT Mw": 5.2},
                   {"NEIC Mwr": 5.0, "GFZ Mw": 5.2}, {"GCMT Mw": 4.9, "CSN Mww": 4.8}, {"GCMT Mw": 5.2, "CSN Mww": 5.1},
                   {"CSN Mww": 4.8, "GUC Mwr": 4.6}])
    R = G.reference(M)[0].reindex(e.event_id)
    assert R.scale.tolist() == ["NEIC Mww", "GCMT Mw", "GCMT Mw", "NEIC Mwr", "GCMT Mw", "CSN Mww", "GUC Mwr"]
    assert R.y.tolist()[:2] == [5.1, 6.0] and R.flag.tolist()[2] == "gcmt_lowered" and R.flag.tolist()[1] == ""
    assert R.sig.tolist()[:2] == [G.SY["W"], G.SY["G"]]
    first = G.reference(M, gcmt_first=True)[0].reindex(e.event_id)
    assert first.scale.tolist()[0] == "GCMT Mw" and first.y.tolist()[0] == 5.2


def test_csn_regional_mw_far_from_the_other_moment_magnitudes_left_out():
    e, M = events([{"GUC Mwr": 5.1, "NEIC Mwr": 4.6}, {"GUC Mwr": 5.1, "NEIC Mwr": 4.9}, {"CSN web Mw": 5.7, "NEIC Mwb": 5.2},
                   {"GUC Mwr": 5.2, "GCMT Mw": 5.2, "NEIC Mwr": 4.6}, {"GUC Mwr": 5.3},
                   {"GUC Mwr": 5.2, "GCMT Mw": 4.7, "NEIC Mwr": 4.6}])
    o = G.outliers(M)
    assert o.event_id.tolist() == [e.event_id[i] for i in (0, 2, 5)] and o.dropped.tolist() == [False, False, True]
    R = G.reference(M)[0].reindex(e.event_id)
    assert R.scale.tolist() == ["GUC Mwr", "GUC Mwr", "CSN web Mw", "GUC Mwr", "GUC Mwr", "NEIC Mwr"]


def test_offsets_constant_for_a_flat_member():
    g = np.random.default_rng(4)
    v = np.round(g.uniform(4.5, 6.5, 600), 1)
    e, M = events([{"NEIC Mww": a, "NEIC Mwr": round(a - 0.1 + g.normal(0, 0.05), 1), "GCMT Mw": a + 0.1 * (a < 5.0)} for a in v])
    R, tab, W = G.reference(M)
    t = tab[(tab.member == "NEIC Mwr") & tab.flat.notna()].iloc[0]
    assert t.flat and abs(t["shift"] - 0.10) < 0.02
    low = tab[tab.against.str.startswith("W family")]
    assert abs(low["shift"].iloc[0] + 0.1) < 0.03


def test_one_mw_per_event():
    F = {"ISC MS": line(-1.0, 1.2), "ISC mb": line(0.3, 0.9, s=0.3), "MOS mb": line(0.3, 0.9)}
    e, M = events([{"GCMT Mw": 5.2, "NEIC Mww": 5.1, "ISC mb": 5.4}, {"GCMT Mw": 6.0, "NEIC Mww": 6.0},
                   {"ISC MS": 4.64}, {"ISC MS": 4.64, "ISC mb": 4.5}, {"ISC MS": 5.6, "ISC mb": 5.0},
                   {"ISC-GEM Mw": 6.5, "Cent ABE1 Ms": 6.9, "ISC mb": 6.0, "yr": 1970.0},
                   {"Cent ABE1 Ms": 6.9, "ISC mb": 6.0, "yr": 1970.0}, {"ISC-GEM Mw": 6.5, "ISC mb": 6.0, "yr": 1980.0},
                   {"Cabello Mw": 7.4, "yr": 1850.0}, {"MOS mb": 4.4}, {"PAS MS": 6.0, "yr": 1930.0}])
    R = G.reference(M)[0]
    rm = pd.DataFrame([{"event_id": "e1", "src_id": "X 2010", "mag": 6.2, "sig": 0.2, "note": "6.2", "flags": ""}])
    w = G.assign(e, M, R, F, RM, ["ISC MS", "ISC mb", "MOS mb"], judge="own")
    assert w.mw_kind.tolist() == ["direct", "direct", "none", "proxy", "proxy", "iscgem", "centennial", "proxy", "cabello",
                                  "none", "none"]
    assert w.mw_type.tolist()[:2] == ["Mww", "Mw"] and w.mw.tolist()[:2] == [5.1, 6.0]
    assert abs((4.64 + 1.0) / 1.2 - 4.7) < 1e-9 and w["flags"][2] == "no_mw"
    assert w.mw_type[3] == "mb" and w.mw_type[4] == "MS" and w.relation_id[4] == "ISC MS"
    assert w.mw[5] == 6.5 and abs(w.mw_raw[6] - G.MS_DG15(6.9)) < 1e-3 and "converted_from_ms" in w["flags"][6]
    assert w.mw_type[7] == "mb" and w.mw[8] == 7.4 and w.mw_sigma[8] == G.SIG_CAB
    assert abs(w.mw_raw[4] - (5.6 + 1.0) / 1.2) < 1e-3 and abs(w.mw[4] - w.mw_raw[4]) < 0.1 and w.native_value[4] == 5.6
    swap = G.assign(e, M, R, F, rm, ["ISC MS", "ISC mb"], old=["Centennial", "ISC-GEM"], judge="own")
    assert swap.mw_kind[5] == "centennial" and swap.mw_kind[1] == "rm18" and swap.mw[1] == 6.2 and swap.mw_src_id[1] == "X 2010"
    assert set(w.columns) == {"event_id", "mw", "mw_sigma", "mw_kind", "mw_src", "mw_src_id", "mw_agency", "mw_type",
                              "native_value", "relation_id", "mw_raw", "flags"}


def test_priority_keeps_the_mb_family_together():
    F = {"ISC mb": {"sigma": 0.24}, "NEIC mb": {"sigma": 0.21}, "GUC ML": {"sigma": 0.23}, "ISC MS": {"sigma": 0.15},
         "CSN Ml": {"sigma": 0.23, "via": "GUC ML"}}
    assert G.priority(F) == ["ISC MS", "ISC mb", "NEIC mb", "GUC ML", "CSN Ml"]


def test_rm18_notes():
    L = pd.DataFrame({"event_id": list("abcdef"), "src": "rm2018", "src_id": ["Tarapaca 1543", "Arica 1615", "Concepcion 1751",
                                                                              "Taltal 1909", "Illapel 1880", "Arica 1987"]})
    r = G.rm18(G.SRC, L).set_index("event_id").loc[list("abcdef")]
    assert r.mag.round(2).tolist() == [7.7, 7.7, 9.0, 7.0, 7.5, 7.2]
    assert r["flags"].tolist() == ["rm18_bound", "rm18_range", "rm18_approx", "rm18_approx;rm18_ms", "", "rm18_ms"]
    assert r.sig["e"] == G.SIG_RM and abs(r.sig["b"] - 0.2) < 1e-9 and r.sig["a"] > G.SIG_RM


def test_coda_before_1990_left_out_and_copies_skipped():
    e, M, rm = G.load()
    yr = M.event_id.map(e.set_index("event_id").yr)
    old = M[(yr < G.CODA_BEFORE) & M.agency.isin(G.CODA_AG)]
    assert not old.mag_type.str.lower().isin(G.CODA).any() and len(old)
    assert not M.src.isin(["potin", "gccel", "iscehb", "csn_isc"]).any()
    assert not M.duplicated(["event_id", "scale"]).any()


# surface-wave rule, mean of the scales, GCMT line
def test_surface_wave_scale_by_depth_not_by_size():
    F = {"ISC MS": line(-1.0, 1.2), "ISC mb": line(0.3, 0.9, s=0.3)}
    e, M = events([{"ISC MS": 4.64, "ISC mb": 4.5}, {"ISC MS": 5.6, "ISC mb": 5.0}, {"ISC MS": 5.6, "ISC mb": 5.0}, {"ISC MS": 5.6}])
    e["z"] = [20.0, 20.0, 90.0, np.nan]
    w = G.assign(e, M, G.reference(M)[0], F, RM, ["ISC MS", "ISC mb"], judge="depth")
    assert w.mw_type.tolist() == ["MS", "MS", "mb", "MS"]
    own = G.assign(e, M, G.reference(M)[0], F, RM, ["ISC MS", "ISC mb"], judge="own")
    assert own.mw_type.tolist() == ["mb", "MS", "MS", "MS"]


def test_mean_of_the_scales():
    F = {"ISC MS": {**line(-1.0, 1.2, s=0.12), "n": 1000}, "ISC mb": {**line(0.3, 0.9, s=0.36), "n": 1000}, "X mb": {**line(0.3, 0.9), "n": 50}}
    e, M = events([{"ISC MS": 5.0, "ISC mb": 5.0}, {"ISC mb": 5.0}, {"ISC MS": 5.0, "ISC mb": 5.0}, {"X mb": 5.0}])
    e["z"] = [20.0, 20.0, 90.0, 20.0]
    prio, R = ["ISC MS", "ISC mb", "X mb"], G.reference(M)[0]
    P = G.proxies(e, M, F, prio, "depth")
    one = G.assign(e, M, R, F, RM, prio, P=P, judge="depth")
    w = G.combine(e, R, F, P, prio, one)
    a, b = P["ISC MS"], P["ISC mb"]
    wa, wb = 1 / a.s[0] ** 2, 1 / b.s[0] ** 2
    assert abs(w.mw_raw[0] - (wa * a.raw[0] + wb * b.raw[0]) / (wa + wb)) < 2e-3
    assert abs(w.mw_sigma[0] - 1 / np.sqrt(wa + wb)) < 2e-3 and w.mw_sigma[0] < one.mw_sigma[0]
    assert "mean_of_scales" in w["flags"][0] and w["flags"][1] == "" and w.mw_raw[1] == one.mw_raw[1]
    assert abs(w.mw_raw[2] - b.raw[2]) < 2e-3 and w.mw_raw[3] == one.mw_raw[3]


def test_gcmt_line_is_continuous_and_keeps_the_order():
    g = np.random.default_rng(5)
    v = g.uniform(4.6, 6.4, 3000)
    rows = [{"GCMT Mw": round(a + max(0.2 * (5.4 - a), 0) + g.normal(0, 0.03), 2), "NEIC Mww": round(a, 2)} for a in v]
    rows += [{"GCMT Mw": a} for a in np.round(np.arange(4.8, 5.6, 0.01), 2)]
    e, M = events(rows)
    R, tab, _ = G.reference(M, lower="ramp0")
    y = R.y.reindex(e.event_id[3000:]).to_numpy()
    x = np.round(np.arange(4.8, 5.6, 0.01), 2)
    assert abs(tab["shift"].iloc[-1] + 0.25) < 0.03
    assert (np.diff(y) > 0).all() and np.diff(y).max() < 0.02
    assert np.allclose(y[x >= G.M_HI], x[x >= G.M_HI]) and abs((x - y)[0] - 0.25 * 0.6) < 0.03
    step = G.reference(M, lower="step")[0].y.reindex(e.event_id[3000:]).to_numpy()
    assert np.diff(step).max() > 0.02
