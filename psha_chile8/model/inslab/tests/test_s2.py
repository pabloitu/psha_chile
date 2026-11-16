import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

T = Path(__file__).resolve().parent
sys.path[:0] = [str(T.parent), str(T)]
import build as B  # noqa: E402
import ref_kernels as RK  # noqa: E402
import is_smooth as S  # noqa: E402

BUILT = (B.NR / "branches.json").exists()
built = pytest.mark.skipif(not BUILT, reason="run build.py first")


def random_events(n=60, seed=4):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"lon": rng.uniform(-71, -68, n), "lat": rng.uniform(-24, -20, n), "w": rng.uniform(0.3, 1, n)})


def small_grid():
    lo, la = np.meshgrid(np.arange(-72.0, -67.0, 0.1), np.arange(-25.0, -19.0, 0.1))
    return pd.DataFrame({"lon": lo.ravel(), "lat": la.ravel()})


# kernel: the port against both codes
def test_kernel_port_agrees_with_both_codes():
    e, g = random_events(), small_grid()
    for n in (1, 5, 25):
        h = S.bandwidth(e.lon, e.lat, n)
        h7 = RK.psha_kernel(e.lon.to_numpy(), e.lat.to_numpy(), n, 5.0)
        hs = RK.ssm_adaptive_radii(e, n=n, min_km=5.0)
        assert np.allclose(h, h7, rtol=1e-7) and np.allclose(h, hs, rtol=1e-7)
        f = S.field(e.lon, e.lat, e.w, h, g.lon, g.lat)
        f7 = RK.psha_field(e.lon.to_numpy(), e.lat.to_numpy(), e.w.to_numpy(), h7, g.lon.to_numpy(), g.lat.to_numpy(), 1.5, 500.0)
        fs = RK.ssm_compute(e, g, e.w.to_numpy(), hs)
        assert np.allclose(f, f7, rtol=1e-9, atol=0) and np.allclose(f, fs, rtol=1e-9, atol=0)


def test_field_keeps_the_weight_of_every_event_and_floor():
    e, g = random_events(), small_grid()
    f = S.field(e.lon, e.lat, e.w, S.bandwidth(e.lon, e.lat, 5), g.lon, g.lat)
    assert abs(f.sum() / e.w.sum() - 1) < 1e-12
    assert (S.bandwidth([-70.0, -70.0001], [-22.0, -22.0], 1) == 5.0).all()
    assert (S.bandwidth([-70.0], [-22.0], 25) == 5.0).all()


def test_calibration_prefers_the_kernel_that_fits_the_test_events():
    rng = np.random.default_rng(1)
    g = small_grid()
    # clustered events: train and test from the same tight clusters; a narrow kernel must score better
    c = np.array([[-70.5, -21.0], [-69.0, -23.0], [-68.2, -20.5]])
    k = rng.integers(0, 3, 400)
    x = pd.DataFrame({"lon": c[k, 0] + rng.normal(0, 0.05, 400), "lat": c[k, 1] + rng.normal(0, 0.05, 400), "w": 1.0})
    s = dict(S.calibrate(x.iloc[:300], x.iloc[300:], g.lon.to_numpy(), g.lat.to_numpy(), (5, 100)))
    assert s[5] > s[100]
    p = np.full(10, 0.1)
    assert S.loglik(p, np.r_[np.full(5, 2.0), np.zeros(5)]) == pytest.approx(-10.0)
    assert S.first_max([1, 3, 5, 10, 100], [-20, -2, -1, -3, 0]) == 5
    assert S.first_max([100, 1, 3], [5, 0, -1]) == 1 and S.first_max([1, 3], [-1, 0]) == 3
    assert S.loglik(np.r_[np.full(5, 0.2), np.zeros(5)], np.r_[np.full(5, 2.0), np.zeros(5)]) == pytest.approx(-10 + 10 * np.log(2.0))


# MFD convention
def test_min_mag_is_the_first_bin_centre_and_bins_are_line_differences():
    F = B.fits()
    for (c, sh), r in F.items():
        f, cc, n = B.mfd(r)
        assert cc[0] == pytest.approx(5.5) and r.m_lo == pytest.approx(4.95)
        assert n.sum() == pytest.approx(f["rate"] * B.G.surv(f, 5.45), rel=1e-9)
        assert np.cumsum(n[::-1])[::-1] == pytest.approx(f["rate"] * B.G.surv(f, cc - B.G.DM / 2), rel=1e-9)
        assert cc[-1] == (pytest.approx(r.mmax) if sh == "trunc" else pytest.approx(r.mmax + 0.2))
        # moments at the bin centres
        assert float((n * B.G.moment(cc)).sum()) == pytest.approx(float((n * 10 ** (1.5 * cc + 9.05)).sum()))


def test_ab_variants_sit_at_the_percentiles_of_the_controlling_rate():
    F = B.fits()
    for (c, sh), r in F.items():
        f0 = B.mfd(r)[0]
        lo, hi = B.mfd(r, "p05")[0], B.mfd(r, "p95")[0]
        mc = min(B.AB_M, r.mmax - 0.3)
        C = np.array([[r.var_a, r.cov_ab], [r.cov_ab, r.var_b]])
        v = np.array([1.0, -(mc - B.G.DM / 2)])
        sd = np.sqrt(v @ C @ v)
        N = lambda f: f["rate"] * B.G.surv(f, mc - B.G.DM / 2)
        # exact for the tapered line; for the cut line the pair is the open-line pair of fits/run.py, and the cut
        # term 0.3 below Mmax narrows the spread by 7-9 %
        tol = 2e-3 if sh == "taper" else 0.1
        assert np.log10(N(lo) / N(f0)) == pytest.approx(-1.645 * sd, rel=tol)
        assert np.log10(N(hi) / N(f0)) == pytest.approx(1.645 * sd, rel=tol)


# checks on the built model
@built
def test_patterns_sum_to_one_on_their_domain():
    s = pd.read_csv(B.TAB / f"pattern_sums_{B.DATE}.csv")
    assert np.allclose(s.domain_sum, 1.0, atol=1e-9) and (s.outside == 0).all()


@built
def test_summed_rates_reproduce_the_fits_at_every_bin_edge():
    e = pd.read_csv(B.TAB / f"edge_check_{B.DATE}.csv")
    assert len(e) == len(B.CLASSES) * len(B.DECL) * len(B.SHAPES) * len(B.AB)
    assert (e.max_rel < 1e-3).all()
    # the same from the written file of the nest (rates as written, 5 significant digits)
    f = B.NR / "is_nest_nn_trunc_ml_l3.xml"
    rates = np.array([[float(x) for x in s.split()] for s in re.findall(r"<occurRates>([^<]+)</occurRates>", f.read_text())]).sum(0)
    r = B.fits()[("jujuy_nest", "trunc")]
    fit, cc, _ = B.mfd(r)
    lst = np.cumsum(rates[::-1])[::-1]
    assert np.allclose(lst, fit["rate"] * B.G.surv(fit, cc - B.G.DM / 2), rtol=1e-3)


@built
def test_depth_weights_sum_to_one_and_hypocentres_inside_the_zone():
    g = B.cells()
    for ly in B.LAYERS:
        h, w = B.hypo(g, ly)
        assert np.allclose(w.sum(1), 1.0, atol=1e-9) and (w > 0).all()
        assert ((h >= g.usd.to_numpy()[:, None]) & (h <= g.lsd.to_numpy()[:, None])).all()
    txt = (B.NR / "is_nest_gk_taper_ml_l3.xml").read_text()
    for blk in re.findall(r"<hypoDepthDist>(.*?)</hypoDepthDist>", txt):
        assert sum(float(p) for p in re.findall(r'probability="([\d.]+)"', blk)) == pytest.approx(1.0, abs=1e-9)


@built
def test_branch_sets_weights_sum_to_one():
    j = json.loads((B.NR / "branches.json").read_text())
    br = pd.DataFrame(j["branches"])
    assert br.weight.sum() == pytest.approx(1.0)
    assert sum(j["factors"]["decl"].values()) == pytest.approx(1.0) and sum(j["factors"]["ab"].values()) == pytest.approx(1.0)
    assert len(br) == len(B.DECL) * len(B.SHAPES) * len(B.AB) * len(B.LAYERS)
    for b in br.itertuples():
        assert all((B.NR / f).exists() for f in b.files)


@built
def test_nest_sources_only_inside_its_region():
    for f in B.NR.glob("is_nest_*_l1.xml"):
        p = np.array([[float(v) for v in s.split()] for s in re.findall(r"<gml:pos>([^<]+)</gml:pos>", f.read_text())])
        assert len(p) and (B.nest_r(p[:, 0], p[:, 1]) <= B.NEST["radius_deg"] + 1e-9).all()


def test_pattern_events_carry_their_completeness_year():
    ev = B.events()
    e = ev[ev.comp]
    yc = np.select([e.mw >= m - 1e-6 for m, _ in sorted(B.TABLE, reverse=True)], [y for _, y in sorted(B.TABLE, reverse=True)])
    assert (e.yc.to_numpy() == yc).all() and (e.t >= e.yc).all() and (ev[~ev.comp].t < ev[~ev.comp].yc).all()
