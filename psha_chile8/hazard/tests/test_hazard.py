"""S5a hazard code: exact combination of families, check_tree on synthetic jobs, logic-tree writers, job list."""
import itertools
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from hazard import combine, nrml  # noqa: E402
from hazard import config as hc  # noqa: E402
from hazard import jobs as J  # noqa: E402

LV = np.logspace(np.log10(0.005), np.log10(3), 30)
Q = (0.05, 0.5, 0.95)


def fam(rng, nr, scale, ns=2):
    a = np.exp(rng.normal(0, 0.3, (ns, nr)))
    w = rng.random(nr)
    return 1 - np.exp(-scale * a[:, :, None, None] * (LV / 0.1) ** -2.0), w / w.sum()


def joint(parts):
    idx = list(itertools.product(*[range(len(p[1])) for p in parts]))
    w = np.array([np.prod([parts[k][1][i] for k, i in enumerate(ix)]) for ix in idx])
    c = np.stack([1 - np.prod([1 - parts[k][0][:, i] for k, i in enumerate(ix)], axis=0) for ix in idx], axis=1)
    return c, w


def test_mean_is_the_enumerated_mean():
    rng = np.random.default_rng(0)
    parts = [fam(rng, 5, 1e-3), fam(rng, 3, 5e-4)]
    c, w = joint(parts)
    assert np.allclose(combine.mean(parts)[:, 0], np.einsum("r,srl->sl", w, c[:, :, 0]), rtol=1e-12)


def test_exact_quantiles_equal_the_weighted_quantiles_of_the_joint_tree():
    rng = np.random.default_rng(1)
    parts = [fam(rng, 5, 1e-3), fam(rng, 3, 5e-4)]
    c, w = joint(parts)
    e = combine.exact(parts, Q)
    for s in range(2):
        o = np.argsort(c[s, :, 0, :], axis=0)
        cs = np.cumsum(w[o], axis=0) - 0.5 * w[o]
        for k, q in enumerate(Q):
            ref = [np.interp(q, cs[:, l], np.take_along_axis(c[s, :, 0, :], o, 0)[:, l]) for l in range(len(LV))]
            assert np.allclose(e[k, s, 0], ref, rtol=1e-10)


def test_monte_carlo_is_within_noise_of_exact():
    rng = np.random.default_rng(2)
    parts = [fam(rng, 20, 1e-3), fam(rng, 4, 5e-4), fam(rng, 12, 2e-4)]
    e, m = combine.exact(parts, Q), combine.fractiles(parts, Q, n=30000)
    ok = (combine.mean(parts) > 1e-4) & (combine.mean(parts) < 1e-2)
    assert np.abs(m[:, ok] / e[:, ok] - 1).max() < 0.03


def synthetic(rng, broken=False):
    S = 3

    def one(nr, scale, src, gm, trt):
        a = np.exp(rng.normal(0, 0.4, (S, nr)))
        w = rng.random(nr)
        return {"curves": 1 - np.exp(-scale * a[:, :, None, None] * (LV / 0.1) ** -2.2), "w": w / w.sum(),
                "imtls": {"PGA": LV}, "names": list("abc"), "src": src, "gmm": [{trt: g} for g in gm]}
    src_i = [(f"if_b{i}", f"msr_{m}") for i in range(2) for m in "xyz" for _ in range(4)]
    gm_i = [f"gi{k}" for _ in range(6) for k in range(4)]
    fi = one(24, 1.5e-3, src_i, gm_i, "Subduction Interface")
    src_s = [(f"is_b{i}",) for i in range(2) for _ in range(4)]
    fs = one(8, 1e-3, src_s, [f"gs{k}" for _ in range(2) for k in range(4)], "Subduction IntraSlab")
    rows = list(itertools.product(range(24), range(8)))
    c = np.stack([1 - (1 - fi["curves"][:, a]) * (1 - fs["curves"][:, b]) for a, b in rows], axis=1)
    if broken:
        c = c * 1.01
    w = np.array([fi["w"][a] * fs["w"][b] for a, b in rows])
    src = [(fi["src"][a][0], fs["src"][b][0], fi["src"][a][1]) for a, b in rows]
    gm = [{"Subduction Interface": gm_i[a], "Subduction IntraSlab": fs["gmm"][b]["Subduction IntraSlab"]} for a, b in rows]
    j = {"curves": c, "w": w, "imtls": {"PGA": LV}, "names": list("abc"), "src": src, "gmm": gm}
    return {"c_all_small": j, "c_if_small": fi, "c_is_small": fs}


@pytest.mark.parametrize("case,ok", [({}, True), ({"broken": True}, False)])
def test_check_tree_passes_a_true_joint_tree_and_fails_a_wrong_one(monkeypatch, tmp_path, case, ok):
    from hazard import check_tree as ct, post
    db = synthetic(np.random.default_rng(3), **case)
    monkeypatch.setattr(post, "load", lambda job, *a, **k: db[job])
    monkeypatch.setattr(hc, "OUT", tmp_path)
    res, bad = ct.main()
    assert (not bad) == ok


def test_source_tree_weights_and_msr_level(tmp_path):
    p = tmp_path / "lt.xml"
    nrml.source_tree(p, [[("if_a", ["a.xml"], 1 / 3), ("if_b", ["b.xml"], 2 / 3)], [("is_c", ["c.xml", "d.xml"], 1.0)]],
                     {k: v for k, v in hc.MSR.items()})
    t = ET.parse(p).getroot()
    ns = {"n": "http://openquake.org/xmlns/nrml/0.4"}
    sets = t.findall(".//n:logicTreeBranchSet", ns)
    assert [s.get("uncertaintyType") for s in sets] == ["sourceModel", "extendModel", "setMSRAbsolute"]
    assert sets[2].get("applyToTectonicRegionType") == "Subduction Interface"
    for s in sets:
        assert sum(float(x.text) for x in s.findall(".//n:uncertaintyWeight", ns)) == pytest.approx(1, abs=1e-12)


def test_jobs_name_existing_branches_and_stay_small():
    from hazard import build
    for n, job in J.JOBS.items():
        for f in hc.FAMILIES:
            if f in job:
                assert set(job[f]) <= set(build.branches(f)), n
                assert sum(job[f].values()) == pytest.approx(1)
    assert sum(J.JOBS["f_if_tree"]["interface"].values()) == pytest.approx(1)
    assert len(J.JOBS["f_if_tree"]["interface"]) * len(hc.MSR) * 4 < 2000
    for n, (fam, ax, lab, base) in J.ROWS.items():
        assert base is None or base in J.JOBS
    assert all(n in J.JOBS and "skip" not in J.JOBS[n] for n in J.RUN)


def test_tree_parts_mix_to_the_weighted_mean(monkeypatch):
    from hazard import trees, post
    rng = np.random.default_rng(4)
    parts = {"pa": fam(rng, 5, 1e-3), "pb": fam(rng, 3, 2e-3)}
    db = {k: {"curves": c, "w": w, "calc_id": 1, "imtls": {"PGA": LV}} for k, (c, w) in parts.items()}
    monkeypatch.setattr(post, "load", lambda job, *a, **k: db[job])
    monkeypatch.setattr(J, "TREE_PARTS", {"t": ["pa", "pb"]})
    monkeypatch.setitem(J.JOBS, "pa", {"part": 0.75})
    monkeypatch.setitem(J.JOBS, "pb", {"part": 0.25})
    r = trees.load("t")
    m = np.einsum("r,srml->sml", r["w"], r["curves"])
    ref = sum(J.JOBS[k]["part"] * np.einsum("r,srml->sml", d["w"], d["curves"]) for k, d in db.items())
    assert np.allclose(m, ref, rtol=1e-12)
    assert r["w"].sum() == pytest.approx(1)
