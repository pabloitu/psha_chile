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


def test_final_trees_read_tree_json_and_rows_read_tornado_json():
    for f, (s, _) in J.FAM.items():
        t, r = J.manifests(f)
        assert J.JOBS[f"f_{s}_tree"][f] == J.tree(f) and sum(J.tree(f).values()) == pytest.approx(1)
        assert J.JOBS[f"g_{s}_tree"]["sites"] == "grid" and J.JOBS[f"f_{s}_tree"]["poes"] == hc.POES_FINAL
        rows = {x["id"] for x in r["rows"] if x["against"] is not None}
        assert len([n for n, v in J.ROWS.items() if v[0] == f and "GMM" not in v[1]]) == len(rows)
    assert J.JOBS["f_if_tree"]["msr"] == J.TREE_MSR


def test_grid_blocks_give_the_fractiles_of_the_whole(monkeypatch, tmp_path):
    from hazard import grid, post
    rng = np.random.default_rng(5)
    xy = np.c_[np.linspace(-72, -70, 7), np.linspace(-40, -30, 7)]
    db = {j: {"curves": fam(rng, nr, sc, ns=7)[0], "w": fam(rng, nr, sc, ns=7)[1], "lonlat": xy,
              "imtls": {"PGA": LV}} for j, nr, sc in (("g_if_tree", 6, 1e-3), ("g_is_tree", 3, 5e-4), ("g_cr_tree", 4, 2e-4))}
    monkeypatch.setattr(post, "load", lambda job, *a, **k: db[job])
    monkeypatch.setattr(hc, "OUT", tmp_path)
    monkeypatch.setattr(grid, "BLOCK", 3)
    out = grid.main()
    q = combine.fractiles([(d["curves"], d["w"]) for d in db.values()], grid.Q, n=grid.N)[:, :, 0]
    assert np.allclose(out["q50_475"], grid.pga(q[1], LV, grid.RP[475]), equal_nan=True)
    m = combine.mean([(d["curves"], d["w"]) for d in db.values()])[:, 0]
    assert np.allclose(out["mean_475"], grid.pga(m, LV, grid.RP[475]), equal_nan=True)


def test_rebin_keeps_the_total_rate_and_centres_the_bins():
    from hazard import speed
    s = '<incrementalMFD minMag="5.50" binWidth="0.10">\n <occurRates>1.0 0.5 0.25 0.125 0.0625</occurRates>'
    o = speed.rebin(s, 2)
    assert 'minMag="5.550" binWidth="0.20"' in o
    r = np.array(o.split("<occurRates>")[1].split("<")[0].split(), float)
    assert np.allclose(r, [1.5, 0.375, 0.0625]) and r.sum() == pytest.approx(1.9375)


def test_a_pulled_datastore_reads_like_the_local_calc(monkeypatch, tmp_path):
    import json, shutil
    from hazard import post
    info = json.loads((hc.JOBS_DIR / "t_is_ref" / "build.json").read_text())
    f = Path.home() / "oqdata" / f"calc_{info.get('calc_id')}.hdf5"
    if not f.exists():
        pytest.skip("no local calc for t_is_ref")
    a = post.load("t_is_ref")
    (tmp_path / "t_is_ref").mkdir()
    (tmp_path / "t_is_ref" / "build.json").write_text(json.dumps({**info, "calc_id": 99999, "datastore": str(f)}))
    monkeypatch.setattr(hc, "JOBS_DIR", tmp_path)
    b = post.load("t_is_ref")
    assert np.allclose(a["curves"], b["curves"]) and np.allclose(a["w"], b["w"])
