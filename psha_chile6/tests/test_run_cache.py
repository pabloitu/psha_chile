# The step cache of run.py: a step reruns when its config, its code or its input files change.

import pytest


@pytest.fixture
def setup(paths):
    import run
    names = [s for s in run.MODELS["crustal"] if s not in run.OPTIONAL]
    return run, run.config("crustal", {}), names


def test_hashes_are_stable_and_follow_the_config(setup):
    run, c, names = setup
    h = run.hashes("crustal", c, names)
    assert h == run.hashes("crustal", c, names)
    h2 = run.hashes("crustal", run.config("crustal", {"MMIN_FIT": 4.7}), names)
    assert h2["s00"] == h["s00"] and h2["s02"] != h["s02"]


def test_hashes_follow_the_code(setup, monkeypatch):
    run, c, names = setup
    h = run.hashes("crustal", c, names)
    monkeypatch.setattr(run, "code", lambda model, step: "changed" + step)
    assert all(run.hashes("crustal", c, names)[k] != h[k] for k in h)


def test_hashes_follow_the_input_files(setup, monkeypatch):
    run, c, names = setup
    h = run.hashes("crustal", c, names)
    monkeypatch.setattr(run, "files", lambda c: {"catalog.csv": "another content"})
    assert all(run.hashes("crustal", c, names)[k] != h[k] for k in h)
