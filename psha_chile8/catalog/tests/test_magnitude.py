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
    """rows: per event a dict scale -> value (key yr for the year, key gem for the ISC-GEM flag)."""
    e = pd.DataFrame({"event_id": [f"e{i}" for i in range(len(rows))], "yr": [r.get("yr", 2015.0) for r in rows],
                      "z": 20.0, "lat": -33.0, "lon": -72.0})
    M = pd.DataFrame([{"event_id": f"e{i}", "scale": k, "mag": v, "err": np.nan, "src": "isc", "src_id": str(i),
                       "agency": k.split()[-2], "mag_type": k.split()[-1], "note": "preferred" if k.startswith("Cent ") else f"q=B s={r['gem']}" if k == "ISC-GEM Mw" and "gem" in r else None}
                      for i, r in enumerate(rows) for k, v in r.items() if k not in ("yr", "gem")])
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
                   {"Cabello Mw": 7.4, "yr": 1850.0}, {"MOS mb": 4.4}, {"PAS MS": 6.0, "yr": 1930.0},
                   {"ISC-GEM Mw": 7.1, "Cent ABE1 mB": 7.5, "yr": 1959.0}, {"ISC-GEM Mw": 6.4, "Cent ISC mb": 6.0, "yr": 1970.0},
                   {"Cent ABE1 Ms": 7.0, "Cent P&S Mw": 7.3, "yr": 1930.0},
                   {"ISC-GEM Mw": 7.1, "Cent ABE1 mB": 7.5, "yr": 1959.0, "gem": "d"},
                   {"ISC-GEM Mw": 7.7, "Cent P&S Mw": 7.2, "yr": 1960.0, "gem": "d"},
                   {"ISC-GEM Mw": 6.0, "Cent ABE1 Ms": 6.9, "yr": 1970.0, "gem": "p"}, {"ISC-GEM Mw": 6.2, "yr": 1950.0, "gem": "p"}])
    e.loc[11, "z"] = 100.0
    R = G.reference(M)[0]
    rm = pd.DataFrame([{"event_id": "e1", "src_id": "X 2010", "mag": 6.2, "sig": 0.2, "note": "6.2", "flags": ""}])
    w = G.assign(e, M, R, F, RM, ["ISC MS", "ISC mb", "MOS mb"], judge="own")
    assert w.mw_kind.tolist() == ["direct", "direct", "none", "proxy", "proxy", "centennial", "centennial", "proxy", "cabello",
                                  "none", "none", "centennial", "iscgem", "centennial", "iscgem", "centennial", "centennial", "iscgem"]
    assert w.mw.tolist()[14:] == [7.1, 7.2, round(G.MS_DG15(6.9) + 1e-9, 1), 6.2]
    assert w["flags"].tolist()[14:] == ["", "", "converted_from_ms", "iscgem_proxy"]
    assert w.mw_type.tolist()[:2] == ["Mww", "Mw"] and w.mw.tolist()[:2] == [5.1, 6.0]
    assert abs((4.64 + 1.0) / 1.2 - 4.7) < 1e-9 and w["flags"][2] == "no_mw"
    assert w.mw_type[3] == "mb" and w.mw_type[4] == "MS" and w.relation_id[4] == "ISC MS"
    assert abs(w.mw_raw[5] - G.MS_DG15(6.9)) < 1e-3 and abs(w.mw_raw[6] - G.MS_DG15(6.9)) < 1e-3 and "converted_from_ms" in w["flags"][6]
    assert abs(w.mw_raw[11] - (2.4 * 7.5 + 10.0 - 16.1) / 1.5) < 1e-3 and w["flags"][11] == "converted_from_mb" and w.mw_sigma[11] == G.SIG_MB
    assert abs(G.MB_A82(7.5, False) - (2.4 * 7.5 + 9.6 - 16.1) / 1.5) < 1e-9 and w.mw[12] == 6.4 and w.mw[13] == 7.3 and w.mw_type[13] == "Mw"
    assert w.mw_type[7] == "mb" and w.mw[8] == 7.4 and w.mw_sigma[8] == G.SIG_CAB
    assert abs(w.mw_raw[4] - (5.6 + 1.0) / 1.2) < 1e-3 and abs(w.mw[4] - w.mw_raw[4]) < 0.1 and w.native_value[4] == 5.6
    rm = pd.DataFrame([{"event_id": i, "src_id": "X", "mag": 6.2, "sig": 0.2, "note": "6.2", "flags": ""} for i in ("e1", "e4", "e15")])
    swap = G.assign(e, M, R, F, rm, ["ISC MS", "ISC mb"], old=[G.OLD[i] for i in (1, 0, 3, 2)], judge="own")
    assert swap.mw_kind[5] == "iscgem" and swap.mw[5] == 6.5 and swap.mw_kind[15] == "rm18" and swap.mw[15] == 6.2
    assert swap.mw_kind[1] == "direct" and swap.mw[1] == 6.0 and swap.mw_kind[4] == "rm18" and swap.mw_src_id[4] == "X"
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


def test_a6_corrections_only_accepted_rows(tmp_path):
    d = pd.DataFrame({"event_id": ["a", "b", "c"], "mw": [7.0, 6.5, 6.0], "mw_sigma": [0.2, 0.2, 0.2], "mw_kind": "iscgem", "mw_src": "iscgem",
                      "depth": [np.nan, 30.0, 10.0], "depth_sigma": np.nan, "depth_kind": ["unknown", "measured", "measured"],
                      "flags": ["", "x", ""]})
    o = pd.DataFrame([["a", "mw", 7.0, 7.7, 0.1, "ref", "p. 1", "why", "accepted"], ["b", "mw", 6.5, 6.9, 0.1, "ref", "p. 1", "why", "proposed"],
                      ["a", "depth", "", 15, 5, "ref", "p. 2", "why", "accepted"], ["b", "class_hint", "", "in-slab", "", "ref", "", "why", "accepted"],
                      ["zz", "mw", 5.0, 6.0, "", "ref", "", "not in the table", "accepted"]],
                     columns=["event_id", "property", "old_value", "new_value", "sigma", "reference", "page", "reason", "status"])
    f = tmp_path / "o.csv"
    o.to_csv(f, index=False)
    w, n = G.overrides(d, {"mw": "mw", "depth": "depth", "class_hint": "a6_class_hint"}, f=f)
    assert n == 3 and w.mw.tolist() == [7.7, 6.5, 6.0] and w.mw_sigma[0] == 0.1 and w.mw_kind.tolist() == ["a6", "iscgem", "iscgem"] and w.mw_src.tolist() == ["a6", "iscgem", "iscgem"]
    assert w.depth[0] == 15 and w.depth_sigma[0] == 5 and w.depth_kind[0] == "measured" and w["flags"].tolist() == ["a6_mw;a6_depth", "x;a6_class_hint", ""]
    assert w.a6_class_hint.tolist()[1] == "in-slab" and w.a6_class_hint.isna().sum() == 2
    o["status"] = "proposed"
    o.to_csv(f, index=False)
    w, n = G.overrides(d, {"mw": "mw", "depth": "depth", "class_hint": "a6_class_hint"}, f=f)
    assert n == 0 and w.equals(d)
    assert G.overrides(d, {"mw": "mw"}, f=tmp_path / "none.csv")[1] == 0


def test_a6_epicentre_sets_the_location_source(tmp_path):
    d = pd.DataFrame({"event_id": ["a", "b"], "lon": [-72.5, -71.0], "lat": [-45.5, -30.0], "loc_src": ["cent_ehb", "isc"],
                      "flags": ["", ""]})
    o = pd.DataFrame([["a", "lon", -72.5, -72.9, "", "ref", "p. 1", "why", "accepted"], ["a", "lat", -45.5, -45.7, "", "ref", "p. 1", "why", "accepted"]],
                     columns=["event_id", "property", "old_value", "new_value", "sigma", "reference", "page", "reason", "status"])
    f = tmp_path / "o.csv"
    o.to_csv(f, index=False)
    w, n = G.overrides(d, {"lon": "lon", "lat": "lat"}, f=f)
    assert n == 2 and w.loc_src.tolist() == ["a6", "isc"] and w.lon[0] == -72.9 and w.lat[0] == -45.7


def test_guc_mw_comes_last_and_is_not_a_fitting_pair():
    e, M = events([{"GUC MW": 6.0, "GCMT Mw": 5.39}, {"GUC MW": 5.0, "CSN Mww": 4.8}, {"GUC MW": 5.0}, {"GUC MW": 5.2, "ISC mb": 5.0},
                   {"NEIC Mww": 5.2, "ISC mb": 5.1}])
    R = G.reference(M)[0].reindex(e.event_id)
    assert R.scale.tolist() == ["GCMT Mw", "CSN Mww", "GUC MW", "GUC MW", "NEIC Mww"]
    assert R.fit.tolist() == [True, True, False, False, True]


def test_relations_leave_out_pairs_below_the_floor_and_guc_mw_pairs():
    g = np.random.default_rng(5)
    y = np.round(g.uniform(3.0, 6.5, 900), 1)
    rows = [{"NEIC Mww": a, "ISC mb": round(0.5 + 0.9 * a + g.normal(0, 0.1), 1)} for a in y]
    rows += [{"GUC MW": 5.0, "ISC mb": 9.0} for _ in range(200)]
    e, M = events(rows)
    R = G.reference(M)[0]
    F = G.relations(M, R, e, quiet=True, boot=0, forms=("linear",))
    assert F["ISC mb"]["n"] == int((y >= G.FIT_MIN).sum())
    assert G.relations(M, R, e, quiet=True, boot=0, forms=("linear",), floor=None)["ISC mb"]["n"] == 900


def test_a6_mechanism_sets_the_mechanism_source(tmp_path):
    d = pd.DataFrame({"event_id": ["a"], "strike1": [10.0], "dip1": [17.0], "rake1": [140.0], "mech_src": ["ISC-GEM literature"],
                      "flags": [""]})
    o = pd.DataFrame([["a", k, "", v, "", "ref", "p. 1", "why", "accepted"] for k, v in (("strike1", 7), ("dip1", 12), ("rake1", 105))],
                     columns=["event_id", "property", "old_value", "new_value", "sigma", "reference", "page", "reason", "status"])
    f = tmp_path / "o.csv"
    o.to_csv(f, index=False)
    w, n = G.overrides(d, {k: k for k in ("strike1", "dip1", "rake1")}, f=f)
    assert n == 3 and (w.strike1[0], w.dip1[0], w.rake1[0]) == (7, 12, 105) and w.mech_src[0] == "a6"



def test_merges_rule_and_a6_rows(tmp_path):
    A3 = G.A3
    pd.DataFrame({"src_id": ["1", "2", "3"], "agency": ["NEIC", "IDC", "ISC"], "prime": [True, True, True]}).to_csv(
        tmp_path / f"isc_{G.FROZEN}_events.csv", index=False)
    pd.DataFrame({"event_id": ["full", "copy", "far", "rev", "dup"],
                  "time": ["2025-01-01T00:00:00", "2025-01-01T00:00:03", "2025-01-01T00:05:00", "2025-01-01T00:00:04",
                           "2020-01-01T00:00:00"],
                  "lon": [-71.0, -71.6, -71.0, -71.05, -70.0], "lat": [-30.0, -30.3, -30.0, -30.0, -30.0]}).to_csv(
        tmp_path / f"events_{A3}.csv", index=False)
    pd.DataFrame({"event_id": ["full", "full", "copy", "far", "rev", "dup"], "src": ["isc", "csn", "isc", "isc", "isc", "comcat"],
                  "src_id": ["1", "c1", "2", "2", "3", "u1"]}).to_csv(tmp_path / f"links_{A3}.csv", index=False)
    o = pd.DataFrame([["dup", "full", "ref", "why", "accepted"]], columns=["event_id", "into", "reference", "reason", "status"])
    o.to_csv(tmp_path / "o.csv", index=False)
    m = G.merges(out=tmp_path, d=tmp_path, f=tmp_path / "o.csv")
    assert m.set_index("event_id").into.to_dict() == {"dup": "full", "copy": "full"}
    L = pd.read_csv(tmp_path / f"links_{A3}.csv", dtype=str)
    e = pd.read_csv(tmp_path / f"events_{A3}.csv")
    L2, e2 = G.merged(L, e, m)
    assert (L2.event_id == "full").sum() == 3 and sorted(e2.event_id) == ["far", "full", "rev"]
    assert sorted(L2[L2.event_id == "full"].src) == ["comcat", "csn", "isc"]


def test_depth3_groups_split_below_the_nest_top():
    g = G.groups("depth3", np.array([10.0, 120.0, 200.0, np.nan]), np.zeros(4))
    assert g.tolist() == ["shallow", "deep", f"below {G.ZNEST:.0f} km", "shallow"]
    assert ("linear", "depth3") in G.candidates("GUC ML", G.N_ALL) and ("linear", "depth3") not in G.candidates("GUC ML", G.N_ALL - 1)
