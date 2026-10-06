# Crustal fault branches: the five MFD shapes release the slip-rate moment at the bin centres, the
# three Mmax modes, the seismogenic-depth override and the 45-branch tree.

import math
from types import SimpleNamespace

import numpy as np
import pytest

from lib import cfg, gr


@pytest.fixture
def c(paths):
    from crustal import config
    return cfg.load(config, {})


def fault(L=60.0, lsd=20.0, m_obs=7.1, b=0.9):
    return SimpleNamespace(id="t", L=L, dip=60.0, usd=0.0, lsd=lsd, slip=1.0, b=b, rake=90.0, m_obs=m_obs)


def target(r, phi, c):
    w = (r.lsd - r.usd) / math.sin(math.radians(r.dip))
    return phi * c.MU * r.L * 1e3 * w * 1e3 * r.slip * 1e-3


@pytest.mark.parametrize("L,m_obs", [(60.0, 7.1), (12.0, 6.3), (3.0, 6.1), (300.0, 7.8)])
def test_every_shape_releases_the_slip_rate_moment(c, L, m_obs):
    from crustal import s03_faults as f3
    r = fault(L, m_obs=m_obs)
    for mm in c.MMAX:
        mx = f3.mmax_of(r, mm, c)
        for k in c.MFD:
            rt = f3.mfd(r, 0.8, mx, k, c)
            ctr = c.FAULT_MMIN + c.DM * (np.arange(len(rt)) + 0.5)
            assert abs((rt * gr.m0(ctr, c.M0_C)).sum() / target(r, 0.8, c) - 1) < 1e-9, (k, mm)
            assert (rt >= 0).all() and abs(ctr[0] - (c.FAULT_MMIN + c.DM / 2)) < 1e-9


def test_shapes_differ_in_the_expected_way(c):
    from crustal import s03_faults as f3
    r = fault()
    rt = {k: f3.mfd(r, 0.8, 7.25, k, c) for k in c.MFD}
    assert rt["al1"][-1] > rt["al2"][-1] > rt["al3"][-1]            # jump, finite, zero slope at Mmax
    assert rt["yc"][-5:].std() / rt["yc"][-5:].mean() < 1e-9          # characteristic box of 0.5
    assert rt["yc"][-1] > rt["al2"][-1] and len(rt["tap"]) > len(rt["al2"])
    assert rt["al3"].sum() > rt["al2"].sum() > rt["al1"].sum()        # same moment, more small events with less at Mmax


def test_youngs_coppersmith_falls_back_to_al2_on_small_faults(c):
    from crustal import s03_faults as f3
    r = fault(3.0, m_obs=6.1)
    assert np.allclose(f3.mfd(r, 0.8, 6.55, "yc", c), f3.mfd(r, 0.8, 6.55, "al2", c))


def test_moment_at_edges_releases_19_percent_more(c):
    from crustal import s03_faults as f3
    r = fault()
    c.M0_AT_EDGE = True
    rt = f3.mfd(r, 0.8, 7.25, "al2", c)
    ctr = c.FAULT_MMIN + c.DM * (np.arange(len(rt)) + 0.5)
    assert abs((rt * gr.m0(ctr, c.M0_C)).sum() / target(r, 0.8, c) - 10 ** (1.5 * c.DM / 2)) < 1e-6


def test_mmax_modes(c):
    from crustal import s03_faults as f3
    from openquake.hazardlib.scalerel.leonard2014 import Leonard2014_Interplate
    from openquake.hazardlib.scalerel.wc1994 import WC1994
    r = fault()
    area = r.L * (r.lsd - r.usd) / math.sin(math.radians(r.dip))
    assert f3.mmax_of(r, "mobs", c) == pytest.approx(7.35)
    lo = c.FAULT_MMIN + c.DM / 2
    for mode, msr in (("mwc", WC1994()), ("mleo", Leonard2014_Interplate())):
        m = msr.get_median_mag(area, r.rake)
        assert f3.mmax_of(r, mode, c) == pytest.approx(lo + c.DM * math.ceil(round((m - lo) / c.DM, 6)))


def test_tree_has_45_weighted_branches_plus_hyb_at_zero(c):
    from crustal import s03_faults as f3
    b = list(f3.branches(c))
    assert len(b) == 54 and abs(sum(x[-1] for x in b) - 1) < 1e-12
    assert sum(1 for x in b if x[-1] > 0) == 45 and all(x[-1] == 0 for x in b if x[3] == "hyb")
    assert {x[1] for x in b} == {0.6, 0.8, 1.0}


def synth_faults():
    import pandas as pd
    from crustal import s03_faults as f3

    def fault(id, x0, y0, x1, y1, slip=1.0, mo=7.0, rake=90.0, dip=60.0):
        xy = [(x0, y0), (x1, y1)]
        return {"id": id, "name": id, "coords": xy, "L": f3.length_km(xy), "dip": dip, "dip_az": None, "usd": 0.0, "lsd": 20.0,
                "slip": slip, "m_obs": mo, "b": 0.9, "rake": rake, "flipped": False}
    # A then B collinear with a 3 km gap (a pair); P parallel to A (no pair); R a reversed-direction
    # strand after B (opposite dip side, no pair); Z isolated without max_mag
    return pd.DataFrame([fault("A", -72.0, -42.0, -72.0, -41.6, 2.0), fault("B", -72.0, -41.573, -72.0, -41.2, 1.0),
                         fault("P", -71.95, -42.0, -71.95, -41.6), fault("R", -72.0, -40.8, -72.0, -41.17),
                         fault("Z", -70.5, -43.0, -70.5, -42.7, 0.5, mo=float("nan"))])


def test_pairs_join_only_extending_traces_on_the_same_dip_side(c):
    from crustal import s03_faults as f3
    df = synth_faults()
    assert [(df.id[i], df.id[j]) for i, j in f3.pairs(df, c)] == [("A", "B")]
    c.LINK_STRIKE = 1.0
    assert f3.pairs(df, c) == [(0, 1)]
    df.loc[1, "rake"] = 0.0
    assert f3.pairs(df, c) == []


def test_missing_max_mag_uses_leonard_in_the_observed_branch(c):
    from crustal import s03_faults as f3
    z = synth_faults().iloc[4]
    assert f3.mmax_of(z, "mobs", c) == f3.mmax_of(z, "mleo", c)


@pytest.mark.parametrize("f", [0.0, 0.5])
def test_written_branches_conserve_the_moment_with_and_without_pairs(c, tmp_path, f):
    from crustal import s03_faults as f3
    from lib import nrml
    c.FAULT_F = f
    tab, pt = f3.write(synth_faults(), c, tmp_path)
    assert len(tab) == 55 and np.allclose(tab["moment_ratio"], 1.0, atol=1e-9)
    assert set(tab["n_sources"]) == ({5} if f == 0 else {6})
    txt = (tmp_path / "faults__phi080__mobs__al2.xml").read_text()
    assert ('id="A:B"' in txt) == (f > 0)
    if f > 0:
        assert pt["pair"].unique().tolist() == ["A:B"] and (pt["mmax_pair"] > pt["mmax_members"]).all()
        cen, r, _ = nrml.mfd_rates(tmp_path / "faults__phi080__mobs__al2.xml")
        assert r.sum() > 0


def test_source_ids_are_valid_for_openquake(c, tmp_path):
    import re
    from crustal import s03_faults as f3
    c.FAULT_F = 0.5
    f3.write(synth_faults(), c, tmp_path)
    ids = re.findall(r'<simpleFaultSource id="([^"]+)"', (tmp_path / "faults__phi080__mobs__al2.xml").read_text())
    assert ids and all(re.fullmatch(r"[\w\-_:]+", i) for i in ids), ids
    from openquake.hazardlib import valid
    for i in ids:
        valid.source_id(i)


def test_pair_mfd_starts_above_the_larger_member_mmax(c, tmp_path):
    from crustal import s03_faults as f3
    from lib import nrml
    c.FAULT_F = 0.5
    f3.write(synth_faults(), c, tmp_path)
    txt = (tmp_path / "faults__phi080__mobs__al2.xml").read_text()
    pair = txt[txt.index('id="A:B"'):]
    pair = pair[:pair.index("</simpleFaultSource>")]
    cen, r, _ = nrml.mfd_rates(pair + "</simpleFaultSource>")
    assert cen[0] > 7.25 and (r > 0).all()


def test_single_factor_variants_keep_the_weights_summing_to_one(paths):
    import run
    from variants import VARIANTS
    for v in [k for k in VARIANTS["crustal"] if k.startswith("only_")]:
        cc = run.config("crustal", VARIANTS["crustal"][v])
        for d, w in (("PHI", sum(x[1] for x in cc.PHI.values())), ("MMAX", sum(cc.MMAX.values())), ("MFD", sum(cc.MFD.values()))):
            assert abs(w - 1) < 1e-12, (v, d)
    assert run.config("crustal", VARIANTS["crustal"]["depth30"]).FAULT_DEPTH == (0.0, 30.0)
    assert run.config("crustal", VARIANTS["crustal"]["patagonia_own"]).B_SOURCE == {}


def test_tornado_rows_have_variants_and_axes(paths):
    from hazard import logic_tree as lt
    from variants import VARIANTS
    for fam, rows in lt.TORN.items():
        for r, e in rows.items():
            assert e[0] in VARIANTS[fam], (fam, r, e[0])
    in_axes = {(f, r) for f, _, rs, *_ in lt.AXES_T for r in rs}
    defined = {(f, r) for f, rows in lt.TORN.items() for r in rows if r != "ref"} | {(f, f"gmm_{k}") for f in lt.GMM_T for k in lt.GMM_T[f]}
    assert defined <= in_axes and {r for r in in_axes if r[0] != "all"} <= defined
    assert all(s in ("A", "B", "C") for *_, s, _, _ in lt.AXES_T)
