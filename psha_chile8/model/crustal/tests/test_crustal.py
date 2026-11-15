# Kernel, calibration score, fault branches, background lists and the join of model/crustal.
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import smooth as S  # noqa: E402
import faults as F  # noqa: E402
import background as BG  # noqa: E402
import join as J  # noqa: E402

SSM = Path("/data/PyCharmProjects/smoothed_seismicity")


def grid(lo=(-72, -68), la=(-35, -31), step=0.1):
    x, y = np.meshgrid(np.arange(*lo, step), np.arange(*la, step))
    return x.ravel(), y.ravel()


def test_bandwidth_is_the_distance_to_the_nth_neighbour_with_a_floor():
    lon = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
    h = S.radii(lon, np.zeros(5), 2, 1.0)
    assert abs(h[0] - S.hav(0.0, 0, 0.2, 0)) < 1e-9 and abs(h[2] - S.hav(0.2, 0, 0.3, 0)) < 1e-9
    assert (S.radii(lon, np.zeros(5), 2, 50.0) == 50.0).all()


def test_field_keeps_the_weight_of_every_event():
    gl, ga = grid()
    rng = np.random.default_rng(0)
    el, ea, w = rng.uniform(-71, -69, 15), rng.uniform(-34, -32, 15), rng.uniform(0.2, 1, 15)
    f = S.field(S.dist(el, ea, gl, ga), w, S.radii(el, ea, 3))
    assert abs(f.sum() / w.sum() - 1) < 1e-12


@pytest.mark.skipif(not SSM.exists(), reason="smoothed_seismicity not on this machine")
def test_field_equals_compute_ssm_of_smoothed_seismicity():
    import pandas as pd
    sys.path.insert(0, str(SSM))
    from ssm.smoothing import adaptive_radii, compute_ssm
    gl, ga = grid()
    rng = np.random.default_rng(1)
    ev = pd.DataFrame({"lon": rng.uniform(-71.5, -68.5, 40), "lat": rng.uniform(-34.5, -31.5, 40)})
    w = rng.uniform(0.1, 1, 40)
    for n in (1, 5, 25):
        h = adaptive_radii(ev, n=n, min_km=5.0)
        assert np.allclose(h, S.radii(ev.lon, ev.lat, n), rtol=1e-12)
        a = compute_ssm(ev, pd.DataFrame({"lon": gl, "lat": ga}), weights=w, radii=h, max_dist_km=500.0, power=1.5)
        b = S.field(S.dist(ev.lon, ev.lat, gl, ga), w, h)
        assert np.allclose(a, b, rtol=1e-10, atol=1e-15)


def test_test_events_outside_the_grid_do_not_count():
    gl, ga = grid()
    i = S.cells(gl, ga, np.array([-70.0, -60.0]), np.array([-33.0, -33.0]))
    assert i[0] >= 0 and i[1] == -1
    ll = S.loglik(np.ones(gl.size), i, np.array([1.0, 1.0]))
    assert abs(ll - (np.log(1 / gl.size) - 1)) < 1e-12


def test_score_prefers_the_kernel_of_the_generating_pattern():
    gl, ga = grid()
    rng = np.random.default_rng(2)
    c = rng.uniform([-71.5, -34.5], [-68.5, -31.5], (8, 2))
    pts = lambda n: c[rng.integers(0, 8, n)] + rng.normal(0, 0.05, (n, 2))
    tr, ts = pts(300), pts(150)
    sc = dict(S.calibrate((tr[:, 0], tr[:, 1], np.ones(300)), (ts[:, 0], ts[:, 1], np.ones(150)), gl, ga, (5, 100)))
    assert sc[5] > sc[100]


def test_every_shape_returns_its_target_moment_and_mmax_on_the_grid():
    for p, z, k in F.BR:
        r, mx, mo = F.branch(60.0, 72.0, 90.0, 0.5, 0.98, z, p, k)
        assert abs(F.moment(r) / mo - 1) < 1e-9
        assert abs(mo - p * F.R.MU * 60e3 * z / math.sin(math.radians(72)) * 1e3 * 0.5e-3) < 1e-6 * mo
        assert abs((mx - F.R.MMIN) / F.R.DM - round((mx - F.R.MMIN) / F.R.DM)) < 1e-9


def test_branch_mean_is_rates_source():
    r = np.array([F.branch(120.0, 85.0, 180.0, 3.0, 1.0, z, p, k)[0] for p, z, k in F.BR])
    assert np.allclose(F.W @ r, F.R.source(120.0, 85.0, 180.0, 3.0, 1.0)[0], rtol=1e-12)
    assert abs(F.W.sum() - 1) < 1e-12


def test_fagnano_is_one_system_source_in_the_files():
    fs = sorted((HERE / "nrml").glob("cr_flt_*_psi080_z20_al2.xml"))
    if not fs:
        pytest.skip("fault files not built")
    for f in fs:
        t = f.read_text()
        assert t.count('id="f_MF_system"') == 1
        for seg in ("CL-056b", "CL-056c", "AR-0056a", "MASCSN-721", "MASCSN-726"):
            assert f'id="f_{seg}"' not in t


@pytest.mark.parametrize("shape", BG.SHAPES)
def test_background_lists_give_the_fit(shape):
    for c in BG.CLASSES:
        m, r = BG.mfd(c, shape)
        row = BG.fit(c, shape)["row"]
        assert abs(m[0] - BG.MMIN) < 1e-9 and np.allclose(np.diff(m), 0.1)
        for M, k in ((5.0, "N5"), (6.0, "N6"), (7.0, "N7")):
            assert abs(r[m >= M - 1e-6].sum() / row[k] - 1) < 2e-3
        if shape == "trunc":
            assert abs(m[-1] - BG.CLASSES[c]["mmax"]) < 1e-9
        else:
            assert abs(m[-1] - BG.CLASSES[c]["mmax"] - 0.2) < 1e-9
            assert abs(r.sum() / row["N5"] - 1) < 1e-6


def test_join_keeps_the_fit_below_6_and_never_goes_negative():
    fit = 10 ** (4.0 - J.CENTRES)
    flt = np.where(J.CENTRES >= 6.0, 3 * 10 ** (4.0 - J.CENTRES), 0.0) * (J.CENTRES < 6.6)
    bg = J.background(fit, flt)
    lo = J.CENTRES < 5.95
    assert np.allclose(bg[lo], fit[lo]) and (bg >= 0).all()
    up = flt > 0
    assert np.all((bg + flt)[up] >= fit[up])
    assert (bg[J.CENTRES >= 5.95] == 0).all()


def test_background_stays_zero_above_the_first_bin_the_faults_fill():
    fit = 10 ** (4.0 - J.CENTRES)
    flt = np.where((J.CENTRES >= 6.0) & (J.CENTRES < 7.0), 0.5 * fit, 0.0) + np.where(np.abs(J.CENTRES - 7.0) < 0.01, 2 * fit, 0.0)
    bg = J.background(fit, flt)
    m = J.CENTRES
    assert np.allclose(bg[(m >= 5.95) & (m < 6.95)], 0.5 * fit[(m >= 5.95) & (m < 6.95)])
    assert (bg[m >= 6.95] == 0).all()


def test_class_maximum_variant_keeps_the_moment_of_every_branch():
    for p, z, k in F.BR:
        r0, m0, mo0 = F.branch(45.0, 80.0, 180.0, 3.0, 1.0, z, p, k)
        r1, m1, mo1 = F.branch(45.0, 80.0, 180.0, 3.0, 1.0, z, p, k, mx=F.CLASS_MMAX["arc"])
        assert m1 == F.CLASS_MMAX["arc"] and m1 > m0
        assert abs(F.moment(r1) / F.moment(r0) - 1) < 1e-9 and F.n_ge(r1, 6.0) < F.n_ge(r0, 6.0)


def test_fault_files_use_leonard_scaling():
    fs = sorted((HERE / "nrml").glob("cr_flt_A_psi080_z20_al2.xml"))
    if not fs:
        pytest.skip("fault files not built")
    t = fs[0].read_text()
    assert "<magScaleRel>Leonard2014_Interplate</magScaleRel>" in t and "WC1994" not in t
