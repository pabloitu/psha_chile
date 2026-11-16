# Kernel, calibration score, fault branches, background lists and the join of model/crustal.
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
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
    fs = sorted((HERE / "nrml" / "2026-11-16g").glob("cr_seg_*_psi080_t20_al2.xml"))
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
            assert np.isclose(r[m >= M - 1e-6].sum(), row[k], rtol=2e-3, atol=6e-6)
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
    fs = sorted((HERE / "nrml" / "2026-11-16g").glob("cr_seg_A_psi080_t20_al2.xml"))
    if not fs:
        pytest.skip("fault files not built")
    t = fs[0].read_text()
    assert "<magScaleRel>Leonard2014_Interplate</magScaleRel>" in t and "WC1994" not in t


def test_sherifs_partition_spends_every_budget_as_earthquakes_or_nms():
    import multifault as M
    A = np.array([40.0, 60.0, 30.0]) * 10.0 * 1e6
    mx = [F.R.on_grid(F.R.leonard(a / 1e6, 180.0)) for a in A]
    src = [dict(members=(i,), area=A[i], lo=F.R.MMIN, hi=mx[i]) for i in range(3)]
    src.append(dict(members=(0, 1, 2), area=A.sum(), lo=round(max(mx) + F.R.DM, 2), hi=F.R.on_grid(F.R.leonard(A.sum() / 1e6, 180.0))))
    bud = {0: 3.0, 1: 2.0, 2: 1.0}
    rate, nms = M.partition(src, bud, 1.0, np.random.default_rng(3))
    m = F.R.MMIN + F.R.DM * np.arange(F.NB)
    mo = (rate * F.R.m0(m)[None, :]).sum() + sum(F.R.MU * A[f] * nms[f] * 1e-3 for f in bud)
    assert abs(mo / sum(F.R.MU * A[f] * bud[f] * 1e-3 for f in bud) - 1) < 1e-9
    assert rate[3].sum() > 0


def test_chain_above_the_class_mmax_is_dropped():
    import pandas as pd
    import multifault as M
    s = pd.DataFrame(dict(L=[300.0, 300.0], dip=[90.0, 90.0], rake=[180.0, 180.0], cls=["arc", "arc"]))
    src, mx = M.sources(s, [(0, 1)], 20.0)
    assert len(src) == 2 and F.R.on_grid(F.R.leonard(12000.0, 180.0)) > F.CLASS_MMAX["arc"]


def test_no_fault_source_lies_wholly_outside_the_grid():
    g = pd.read_csv(F.GRID)
    s, rr, _ = F.load("A")
    assert len(s) == rr.shape[0]
    for t in s.trace:
        t = np.asarray(t)
        assert (S.cells(g.lon.to_numpy(), g.lat.to_numpy(), t[:, 0], t[:, 1]) >= 0).any()
    assert not s.fid.isin(["AR-0025a", "AR-0027a", "AR-0027b"]).any() and s.system.sum() == 1


def test_nodal_plane_mix_sums_to_one():
    nd = BG.npds()
    for w in (np.array([1.0, 0, 0, 0]), np.array([0.2, 0.3, 0.4, 0.1]), np.array([1e-9, 5.0, 0, 0])):
        p = BG.mix(w, nd)
        assert sum(int(round(float(a) * 1e4)) for a, *_ in p) == 10000


def test_tree_weights_and_files():
    import json
    NR = HERE / "nrml" / "2026-11-16g"
    f = NR / "branches.json"
    if not f.exists():
        pytest.skip("files not built")
    br = json.loads(f.read_text())
    assert abs(sum(b["weight"] for b in br["tree"]) - 1) < 1e-9
    for b in br["tree"] + [x for r in br["tornado"].values() for x in r["branches"]]:
        for x in b["files"]:
            assert (NR / x).exists(), x
    for r in br["tornado"].values():
        assert abs(sum(b["weight"] for b in r["branches"]) - 1) < 1e-9


def test_multi_fault_rates_read_back():
    t = HERE / "tables" / "oqcheck_2026-11-16g.csv"
    if not t.exists():
        pytest.skip("check not run")
    x = pd.read_csv(t)
    assert x.N.notna().all() and x.N_oq.notna().all()
    assert (np.abs(x.N - x.N_oq) / x.N).max() < 1e-4
    assert x.source.str.startswith("mf_").any()


def test_section_ids_are_unique_across_files():
    import re
    NR = HERE / "nrml" / "2026-11-16g"
    fs = sorted(NR.glob("cr_sections_*.xml"))
    if not fs:
        pytest.skip("files not built")
    ids = [i for f in fs for i in re.findall(r'<section id="([^"]+)"', f.read_text())]
    assert len(ids) == len(set(ids))


def test_strict_ucerf3_ruptures_are_single_paths_of_whole_faults():
    import pandas as pd
    import rupset as R
    # three faults in a line with a gap of 3 km, and one parallel strand 4 km to the side
    tr = lambda x0, y0, x1, y1: [(x0, y0), (x1, y1)]
    s = pd.DataFrame(dict(trace=[tr(-72.0, -40.0, -72.0, -39.7), tr(-72.0, -39.67, -72.0, -39.4), tr(-72.0, -39.37, -72.0, -39.1),
                                 tr(-71.95, -39.9, -71.95, -39.6)],
                          sr=[3.0] * 4, rake=[180.0] * 4, dip=[90.0] * 4, L=[33.4, 30.0, 30.0, 33.4]))
    R.JUMP_KM = 5.0
    rups, sub = R.ruptures(s, 10.0, main_only=True)
    sc = R.scenarios(rups)
    for r in rups:
        f = sub.fault.to_numpy()[list(r["subs"])]
        assert len(set(r["faults"])) == len(r["faults"])
        for q in r["faults"]:
            k = np.where(f == q)[0]
            assert np.all(np.diff(k) == 1)
    assert any(set(r["faults"]) == {0, 1, 2} for r in sc)
    for r in sc:
        assert r["full"] and all(sub.fault.eq(q).sum() == sum(1 for x in r["subs"] if sub.fault[x] == q) for q in r["faults"])
