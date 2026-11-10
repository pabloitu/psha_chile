import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import read as r

D = Path(__file__).resolve().parent / "data"


def run(name):
    return getattr(r, name)(D / ("isc" if name == "csn_isc" else name))


@pytest.mark.parametrize("name", [s for s in r.RUN])
def test_columns(name):
    ev, mg, mc = run(name)
    for t, cols in ((ev, r.EV), (mg, r.MG), (mc, r.MC)):
        assert list(t.columns[:len(cols)]) == cols
        assert (t.src == name).all()
    assert len(ev) or len(mc)
    assert set(mg.src_id) <= set(ev.src_id) or name == "comcat_mt"


def test_gcmt_maule():
    ev, mg, mc = run("gcmt")
    assert set(ev.src_id) == {"C201002270634A"}
    c = ev[ev.prime].iloc[0]
    assert (c.lat, c.lon, c.depth, c.depth_quality, c.depth_fixed) == (-35.98, -73.15, 23.2, "FREE", False)
    assert c.time == "2010-02-27T06:35:14.500"
    m = mc.iloc[0]
    assert m.m0 == pytest.approx(1.858e22)
    assert m.mw == 8.78
    assert (m.strike1, m.dip1, m.rake1, m.strike2, m.dip2, m.rake2) == (19, 18, 116, 172, 74, 82)
    assert m.mrr == pytest.approx(1.04e22)
    assert set(zip(mg.agency, mg.mag_type)) == {("PDEW", "Ms"), ("GCMT", "Mw")}


def test_isc_all_origins_and_magnitudes():
    ev, mg, _ = run("isc")
    assert ev.groupby("src_id").prime.sum().eq(1).all()
    assert {"ISC", "IDC", "NEIC", "GUC"} <= set(ev.agency)
    p = ev[ev.prime & (ev.src_id == "16114735")].iloc[0]
    assert (p.agency, p.depth, p.depth_fixed) == ("ISC", 25.0, True)
    assert p.lon_err == pytest.approx(18.6975)
    m = mg[(mg.src_id == "16114735") & (mg.agency == "ISC") & (mg.mag_type == "mb")].iloc[0]
    assert (m.mag, m.mag_err, m.n_sta) == (4.19, 0.1, 8)


def test_csn_isc_is_guc_inside_isc():
    ev, mg, _ = run("csn_isc")
    assert (ev.agency == "GUC").all() and (mg.agency == "GUC").all()
    assert list(zip(mg.mag_type, mg.mag)) == [("ML", 4.7)]


def test_iscehb_quality():
    ev, mg, _ = run("iscehb")
    assert list(ev.depth_quality) == ["L1", "L1"]
    assert not ev.depth_fixed.any()
    assert ev.depth.tolist() == [99.1, 32.7]
    assert ("GCMT", "MW") in set(zip(mg.agency, mg.mag_type))


def test_comcat():
    ev, mg, _ = run("comcat")
    assert len(ev) == 5 and ev.src_id.is_unique
    assert (mg.mag_type == "mb").all()
    assert ev.time.iloc[0] == "2010-03-01T00:01:11.670"


def test_comcat_mt_keeps_every_product():
    _, _, mc = run("comcat_mt")
    assert len(mc) == 5
    assert mc.code.str.startswith(("moment-tensor:", "focal-mechanism:")).all()
    t = mc[mc.code.str.endswith("_M_US")].iloc[0]
    assert t.m0 == pytest.approx(5.3e17) and t.strike1 == 318


def test_centennial():
    ev, mg, _ = run("centennial")
    assert len(ev) == 3
    e = ev.iloc[2]
    assert (e.agency, e.depth_quality, e.depth_fixed, e.depth) == ("EHB", "DEQ", False, 113.6)
    assert (mg.note == "preferred").sum() == 3
    assert set(mg.mag_type) >= {"Ms", "mB"}


def test_potin():
    ev, mg, _ = run("potin")
    assert len(ev) == 7 and len(mg) == 2
    assert ev.time.iloc[0] == "1982-01-08T00:32:52.05"
    assert list(mg.mag) == [4.9, 7.0] and (mg.mag_type == "ww").all()


def test_cabello_keeps_native_and_final():
    ev, mg, mc = run("cabello")
    assert ev.time.iloc[0] == "1513-01-01T00:00:00.00"
    g = mg[mg.src_id == "3201"]
    assert set(zip(g.mag_type, g.mag)) == {("Mw", 6.87), ("Mb", 6.0), ("magnitude", 6.9)}
    assert mc.m0.iloc[0] == pytest.approx(2.55e19)


def test_rm2018_keeps_text():
    ev, mg, _ = run("rm2018")
    assert ev.time.tolist()[:3] == ["1543", "1615", "1751-05-25"]
    m = mg.set_index("src_id")
    assert np.isnan(m.loc["Tarapaca 1543", "mag"]) and m.loc["Tarapaca 1543", "note"] == ">7.7"
    assert m.loc["Maule 2010", "mag"] == 8.8


def test_iscgem():
    ev, mg, mc = run("iscgem")
    assert set(ev.src_id) == {"718362", "14340585"}
    m = mc.set_index("src_id").loc["14340585"]
    assert m.m0 == pytest.approx(1.86e22) and m.mrp == pytest.approx(-1.52e22) and m.strike2 == 172
    assert ev.set_index("src_id").loc["14340585", "depth_quality"] == "A"
    assert mg.set_index("src_id").loc["14340585", "note"] == "q=A s=d"


def test_write_and_manifest(tmp_path, monkeypatch):
    raw = tmp_path / "raw" / "potin"
    raw.mkdir(parents=True)
    (raw / "fetch.json").write_text(json.dumps(dict(query="q", downloaded="2026-11-10")))
    monkeypatch.setattr(r, "RAW", tmp_path / "raw")
    r.write("potin", run("potin"), tmp_path)
    r.write("potin", run("potin"), tmp_path)
    m = pd.read_csv(tmp_path / "MANIFEST.csv")
    assert list(m.file) == ["potin_2026-11-10_events.csv", "potin_2026-11-10_mags.csv"]
    assert list(m.rows) == [7, 2] and m.sha256.str.len().eq(64).all()


def test_inbox_drops_outside():
    ev = pd.DataFrame(dict(src_id=["a", "a", "b"], lat=[-30, 10, 40], lon=[-70, 0, 20]))
    mg = pd.DataFrame(dict(src_id=["a", "b"], mag=[5, 6]))
    e, m = r.inbox(ev, mg)
    assert list(e.src_id) == ["a", "a"] and list(m.src_id) == ["a"]


def test_csn_day_page():
    ev, mg, _ = run("csn")
    assert len(ev) == 17 and ev.src_id.is_unique
    e = ev.set_index("src_id").loc["2024/01/221233"]
    assert (e.time, e.lat, e.lon, e.depth, e.felt) == ("2024-01-15T05:17:41", -22.776, -68.394, 106.0, True)
    assert ev.felt.sum() == 1
    assert mg.set_index("src_id").loc["2024/01/221233", ["mag", "mag_type"]].tolist() == [4.9, "Mw"]
    assert set(mg.mag_type) == {"Ml", "Mw"}


def test_check_flags_problems():
    assert all(not r.check(*run(s)) for s in r.RUN if s != "rm2018")
    assert r.check(*run("rm2018")) == ["3 preferred origins without lat or lon"]
    ev, mg, mc = run("comcat")
    ev = pd.concat([ev, ev.iloc[[0]].assign(origin_id="x", depth=900.0)])
    mg = pd.concat([mg, mg.iloc[[0]].assign(src_id="ghost", mag=12.0)])
    assert r.check(ev, mg, mc) == ["1 events without exactly one preferred origin", "1 depths outside −10–800 km",
                                   "1 magnitudes without their event", "1 magnitudes outside −2–10"]
