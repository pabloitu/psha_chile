# hazard/check_tree.py on synthetic family and joint jobs whose truth is known: it must pass a
# correct joint tree (also stored as float32), report a mislabelled one as a pairing problem only,
# and fail a joint tree that is not the product of the families.

import itertools

import numpy as np
import pandas as pd
import pytest

LV = np.logspace(np.log10(0.005), np.log10(3), 30)
S = 3


def family(rng, nr, scale, gcol, names, pre):
    a = np.exp(rng.normal(0, 0.4, (S, nr)))
    c = 1 - np.exp(-scale * a[:, :, None, None] * (LV / 0.1) ** -2.2)
    w = rng.random(nr)
    gm = [names[i % len(names)] for i in range(nr)]
    return {"curves": c, "w": w / w.sum(), "imtls": {"PGA": LV}, "names": ["a", "b", "c"], "src": np.array([f"{pre}-v-b{i // len(names)}" for i in range(nr)]),
            "axes": pd.DataFrame({gcol: gm})}


def build(rng):
    f = [family(rng, 8, 1.5e-3, "gmm:sinter", ["A", "B", "C", "D"], "if"), family(rng, 4, 1e-3, "gmm:sslab", ["E", "F", "G", "H"], "is"),
         family(rng, 8, 2e-4, "gmm:asc", ["I", "J", "K", "L"], "cr")]
    rows = list(itertools.product(range(8), range(4), range(8)))
    c = np.stack([1 - (1 - f[0]["curves"][:, a]) * (1 - f[1]["curves"][:, b]) * (1 - f[2]["curves"][:, k]) for a, b, k in rows], axis=1)
    w = np.array([f[0]["w"][a] * f[1]["w"][b] * f[2]["w"][k] for a, b, k in rows])
    j = {"curves": c, "w": w, "imtls": {"PGA": LV}, "names": ["a", "b", "c"],
         "src": np.array([f"{f[0]['src'][a]}_x_{f[1]['src'][b]}_x_{f[2]['src'][k]}" for a, b, k in rows]),
         "axes": pd.DataFrame({"gmm:sinter": [f[0]["axes"]["gmm:sinter"][a] for a, _, _ in rows], "gmm:sslab": [f[1]["axes"]["gmm:sslab"][b] for _, b, _ in rows],
                               "gmm:asc": [f[2]["axes"]["gmm:asc"][k] for _, _, k in rows]})}
    return f, j


def run(monkeypatch, f, j):
    from hazard import check_tree as ct, post
    db = {"c_all_small": j, "c_if_small": f[0], "c_is_final": f[1], "c_cr_small": f[2]}
    monkeypatch.setattr(post, "load", lambda job, *a, **k: db[job])
    out = []
    res = ct.level1(out)
    return res, ct.TOL, "\n".join(out)


def test_correct_joint_tree_passes_also_as_float32(paths, monkeypatch):
    f, j = build(np.random.default_rng(0))
    for dtype in (np.float64, np.float32):
        j2 = {**j, "curves": j["curves"].astype(dtype)}
        f2 = [{**x, "curves": x["curves"].astype(dtype)} for x in f]
        res, tol, _ = run(monkeypatch, f2, j2)
        assert all(res[k] < tol[k] for k in res), (dtype, res)


def test_mislabelled_realizations_are_a_pairing_problem_only(paths, monkeypatch):
    f, j = build(np.random.default_rng(1))
    p = np.random.default_rng(2).permutation(len(j["w"]))
    j2 = {**j, "src": j["src"][p], "axes": j["axes"].iloc[p].reset_index(drop=True)}       # labels shuffled, curves and weights kept
    res, tol, txt = run(monkeypatch, f, j2)
    assert res["paired"] > 0.01 and res["partner"] < tol["partner"] and res["quantiles"] < tol["quantiles"] and res["mean"] < tol["mean"], (res, txt)


def test_a_joint_tree_that_is_not_the_product_fails(paths, monkeypatch):
    f, j = build(np.random.default_rng(3))
    c = j["curves"].copy()
    c[:, :64] *= 1.3                                                  # a family's curves wrong in a quarter of the realizations
    res, tol, _ = run(monkeypatch, f, {**j, "curves": np.clip(c, 0, 1)})
    assert res["partner"] > tol["partner"] and res["quantiles"] > tol["quantiles"] and res["mean"] > tol["mean"], res


def test_level_two_is_skipped_when_its_jobs_are_not_built(paths, tmp_path, monkeypatch):
    from hazard import check_tree as ct, config as hc
    monkeypatch.setattr(hc, "OUT_ROOT", tmp_path)
    out = []
    assert ct.level2(out) == {} and "skipped" in out[0]


def test_level_two_passes_a_sampled_joint_job_and_flags_a_biased_one(paths, tmp_path, monkeypatch):
    from hazard import check_tree as ct, config as hc, post
    f, j = build(np.random.default_rng(4))
    idx = np.random.default_rng(5).choice(len(j["w"]), 2000, p=j["w"])
    s = {**j, "curves": j["curves"][:, idx], "w": np.full(2000, 1 / 2000)}
    for job in ("c_if_final", "c_is_final", "c_cr_final", "c_all_final_sample"):
        (tmp_path / job).mkdir()
        (tmp_path / job / "build.json").write_text("{}")
    monkeypatch.setattr(hc, "OUT_ROOT", tmp_path)
    for sampled, ok in ((s, True), ({**s, "curves": np.clip(s["curves"] * 1.5, 0, 1)}, False)):
        db = {"c_if_final": f[0], "c_is_final": f[1], "c_cr_final": f[2], "c_all_final_sample": sampled}
        monkeypatch.setattr(post, "load", lambda job, *a, **k: db[job])
        out = []
        worst = ct.level2(out)
        txt = "\n".join(out)
        assert ("LEVEL 2: PASS" in txt) == ok, txt
        assert "share interface" in txt
