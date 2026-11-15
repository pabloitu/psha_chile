"""Tests of task GM1: flatfile parsing, scores, the event split, one GMM against a direct hazardlib call, the merge of
duplicate flatfile entries."""
import numpy as np
import pandas as pd
import pytest

import records as B
import residuals as R
import scores as S


def test_vector_fields():
    v = B.vec("['0.01'; '0.05'; '-999'; '1']")
    assert np.allclose(v[[0, 1, 3]], [0.01, 0.05, 1.0]) and np.isnan(v[2])
    assert np.isnan(B.vec(-999)).all()
    assert B.ztor_nodes("[-34.5 -72.8 6.4000]; [-34.6 -72.6 10.2]") == pytest.approx(6.4)


def test_llh_standard_normal():
    x = np.random.default_rng(0).standard_normal(200_000)
    assert S.llh(x, 0.0, 1.0) == pytest.approx(0.5 * np.log2(2 * np.pi * np.e), abs=0.01)
    assert abs(S.llh(x, 0.0, 1.0) - 2.05) < 0.01


def test_edr_perfect_below_biased_and_kappa_one():
    rng = np.random.default_rng(1)
    mu = rng.uniform(-6, 0, 20_000)
    obs = mu + 0.6 * rng.standard_normal(len(mu))
    sig = np.full(len(mu), 0.6)
    e0 = S.edr(obs, mu, sig)
    e1 = S.edr(obs, mu - 0.5, sig)
    assert e0[2] < e1[2]
    assert e0[1] == pytest.approx(1.0, abs=0.01)
    # a model whose medians scale wrongly has κ > 1
    assert S.edr(obs, 1.5 * mu, sig)[1] > 1.2


def test_event_split_recovers_tau_phi():
    rng = np.random.default_rng(2)
    n_ev, n_rec, tau, phi = 400, 12, 0.45, 0.6
    ev = np.repeat(np.arange(n_ev), n_rec)
    r = 0.2 + tau * rng.standard_normal(n_ev)[ev] + phi * rng.standard_normal(len(ev))
    c, t, p = R.mixed(r, ev)
    assert c == pytest.approx(0.2, abs=0.06)
    assert t == pytest.approx(tau, abs=0.04) and p == pytest.approx(phi, abs=0.02)
    db, dw, _ = R.split(r - 0.2, ev, np.full(len(ev), tau), np.full(len(ev), phi))
    e = pd.Series(db).groupby(ev).first()
    assert e.std() == pytest.approx(tau * np.sqrt(n_rec * tau ** 2 / (n_rec * tau ** 2 + phi ** 2)), rel=0.1)
    assert np.std(dw) == pytest.approx(phi * np.sqrt(1 - 1 / n_rec), rel=0.05)


def test_gmm_against_hazardlib():
    from openquake.hazardlib import const
    from openquake.hazardlib.imt import PGA, SA
    s = '[ParkerEtAl2020SInter]\nregion = "SA"\nsaturation_region = "SA_S"'
    d = pd.DataFrame(dict(record_id=["a", "b", "c"], event_id=["e1", "e1", "e2"], mw=[6.0, 6.0, 8.0],
                          rrup=[40.0, 120.0, 90.0], vs30=[350.0, 760.0, 500.0], PGA=[0.1, 0.02, 0.3],
                          **{"SA(1.0)": [0.05, 0.01, 0.2]}))
    mu, sig, tau, phi = R.evaluate(R.gsim(s), d, ["PGA", "SA(1.0)"])
    g = R.gsim(s)
    ctx = np.recarray(3, dtype=[("mag", float), ("rrup", float), ("vs30", float)])
    ctx.mag, ctx.rrup, ctx.vs30 = d.mw, d.rrup, d.vs30
    m, sg, t, p = (np.zeros((2, 3)) for _ in range(4))
    g.compute(ctx, [PGA(), SA(1.0)], m, sg, t, p)
    assert np.allclose(mu, m) and np.allclose(sig, sg) and np.allclose(tau, t) and np.allclose(phi, p)
    res = R.residuals(d, [("P", "Parker", s)], ["PGA", "SA(1.0)"])
    assert np.allclose(res[res.imt == "PGA"].r, np.log(d.PGA) - m[0])
    assert const.StdDev.INTER_EVENT in g.DEFINED_FOR_STANDARD_DEVIATION_TYPES


@pytest.mark.skipif(not (B.TAB / f"records_{B.DATE}.csv").exists(), reason="record table not built")
def test_duplicate_merge():
    r = pd.read_csv(B.TAB / f"records_{B.DATE}.csv", dtype={"ff_event_id": str})
    g = r[r.event_id == "cl20140403024315"]
    assert set(g.ff_event_id) <= {"20140403024315", "20140403024815"}
    assert g.station.is_unique
    p = pd.read_csv(B.TAB / "duplicate_pairs.csv", dtype={"EventID": str})
    assert {"20140403024315", "20140403024815"} <= set(p.EventID)
    # stations recorded in both entries are taken from the entry closest to the catalogue origin (024315)
    rec = pd.read_csv(B.F_REC, usecols=["EventID", "StationID"], dtype={"EventID": str})
    a = set(rec[rec.EventID == "20140403024315"].StationID)
    b = set(rec[rec.EventID == "20140403024815"].StationID)
    both = a & b
    assert len(both) == 20
    assert (g[g.station.isin(both)].ff_event_id == "20140403024315").all()
