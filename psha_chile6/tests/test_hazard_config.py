# Settings of the hazard trees: cities, output tree and the maximum distance per tectonic region.

import importlib
import json

import pytest


def reload(monkeypatch, **env):
    for k in ("SMOKE", "PRELIM", "FINAL", "LEVEL2"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    from hazard import config as hc, logic_tree as lt
    importlib.reload(hc)
    importlib.reload(lt)
    return hc, lt


@pytest.fixture
def restore(paths):
    yield
    from hazard import config as hc, logic_tree as lt
    importlib.reload(hc)
    importlib.reload(lt)


def test_level2_has_the_ten_cities_its_own_tree_and_the_family_and_joint_jobs(paths, monkeypatch, restore):
    hc, lt = reload(monkeypatch, LEVEL2="1")
    assert list(hc.CITIES) == list(hc.CITIES_LEVEL2) and len(hc.CITIES) == 10
    assert {"hornopiren", "puerto_williams"} <= set(hc.CITIES)
    assert hc.OUT_ROOT.name.endswith("_level2")
    assert {"c_if_final", "c_is_final", "c_cr_final", "c_all_final_sample", "c_all_small"} <= set(lt.BUILD)


def test_prelim_final_and_tornado_have_the_fourteen_cities(paths, monkeypatch, restore):
    for env in ("PRELIM", "FINAL", "TORNADO"):
        hc, lt = reload(monkeypatch, **{env: "1"})
        assert len(hc.CITIES) == 14 and list(hc.CITIES)[-4:] == ["hornopiren", "puerto_williams", "calama", "la_serena"]
    assert hc.OUT_ROOT.name.endswith("_tornado") and lt.BUILD == lt.TORNADO_JOBS and lt.BUILD[:3] == ["t_if_ref", "t_is_ref", "t_cr_ref"]


def test_distances_per_region_are_written_to_the_job(paths, monkeypatch, restore):
    hc, lt = reload(monkeypatch, LEVEL2="1")
    from hazard import build
    lt.SAMPLES_JOB, lt.CALC_JOB, lt.DISAGG_JOB, lt.TRUNC_JOB = 0, {}, {}, None
    md = lambda trts: [x for x in build.job(None, "t", {}, trts).splitlines() if x.startswith("maximum_distance")][0].split("=", 1)[1]
    d = json.loads(md(list(hc.MAX_DIST_TRT) + ["Subduction IntraSlab"]))
    assert d == {"default": 500.0, **hc.MAX_DIST_TRT} and d["Subduction Interface"] > d["Active Shallow Crust"]
    # a family job names only its own type (OpenQuake rejects types absent from the job's GMM tree)
    assert json.loads(md(["Subduction Interface"])) == {"default": 500.0, "Subduction Interface": 600.0}
    assert md(["Subduction IntraSlab"]).strip() == "500.0"


def test_campaign_settings_stay_a_single_distance(paths, monkeypatch, restore):
    hc, lt = reload(monkeypatch)
    from hazard import build
    lt.SAMPLES_JOB, lt.CALC_JOB, lt.DISAGG_JOB, lt.TRUNC_JOB = 0, {}, {}, None
    assert hc.MAX_DIST_TRT == {} and "maximum_distance = 400.0" in build.job(None, "t", {})
