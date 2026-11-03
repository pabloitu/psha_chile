# Classification of the frozen catalog_base.csv: counts, hand decisions, depth and latitude limits,
# known large events. Fails when a change of params.py, class_overrides.csv or classify.py moves events.
# Run from the repo root: python -m pytest cat_handler_2/tests -q

import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cat_handler_2 import classify
from cat_handler_2 import config as C

FROZEN = Path(os.environ.get("CAT_FROZEN", C.OUT / "frozen" / "2026-11-03"))

CLASS = {"slab_interface": 17584, "slab_deep": 15662, "intra_slab": 3869, "unresolved": 3514, "deep_nest": 3249,
         "forearc": 2294, "outer_rise": 1415, "backarc": 901, "intraarc": 856, "deep_unknown": 789,
         "patagonia_interface": 41, "patagonia_crustal": 36, "unclassified": 1}
RULE = {"band_nomech": 14233, "arc_slab": 8548, "deep_slab": 6889, "band_intraslab": 3743, "nest": 3249,
        "unk_deep": 2617, "unk_nomech": 2418, "band_forearc": 2030, "outer_rise": 1412, "backarc": 901, "cone": 880,
        "arc_crustal": 853, "deep_mid": 762, "arc_below": 415, "below": 374, "deep_forearc": 252, "deep_above": 224,
        "band_mech": 142, "pat_deep": 58, "unk_cone": 44, "pat_interface": 41, "no_slab_deep": 39, "pat_crustal": 32,
        "override": 14, "unk_mech": 14, "remark": 12, "arc_noslab": 5, "unk_normal": 4, "pat_outer": 3,
        "pre_year": 2, "no_slab": 1}
FAM = {"in-slab": 22780, "interface": 17625, "excluded": 5718, "crustal": 4088}
FAM55 = {"in-slab": 1073, "interface": 1028, "excluded": 448, "crustal": 128}

# id: (class, rule); rule None for hand decisions
EVENTS = {"890": ("slab_interface", "unk_cone"),      # Valdivia 1960 M9.5
          "83388": ("slab_interface", "cone"),        # Maule 2010
          "135106": ("slab_interface", "cone"),       # Iquique 2014
          "145193": ("slab_interface", "cone"),       # Illapel 2015
          "69131": ("slab_interface", "cone"),        # Tocopilla 2007
          "157950": ("slab_interface", None),         # Chiloe 2016
          "24": ("intra_slab", None),                 # Santiago 1647
          "678": ("patagonia_crustal", None),         # Tierra del Fuego 1949 M8.0
          "159": ("patagonia_crustal", None),         # Magallanes 1879
          "196": ("patagonia_crustal", None),         # Magallanes 1907
          "3030": ("patagonia_crustal", None)}        # Tierra del Fuego 1970


@pytest.fixture(scope="module")
def built():
    f = FROZEN / "catalog_base.csv"
    if not f.exists():
        pytest.skip(f"no {f}")
    return classify.build(f)


@pytest.fixture(scope="module")
def ev(built):
    return built[0].set_index("id", drop=False)


def counts(s):
    return {k: int(v) for k, v in s.value_counts().items()}


def test_counts_per_class(ev):
    assert counts(ev["class"]) == CLASS


def test_counts_per_rule(ev):
    assert counts(ev["cls_rule"]) == RULE


def test_counts_per_family(ev):
    assert counts(ev["family"]) == FAM
    assert counts(ev.loc[ev["mag"] >= 5.5, "family"]) == FAM55


def test_families_cover_params(ev):
    fam = {c: f for f, cs in C.FAMILIES.items() for c in cs}
    assert set(ev["class"]) - set(fam) == {"outer_rise", "deep_unknown", "unresolved"}
    assert (ev["family"] == ev["class"].map(fam).fillna("excluded")).all()


def test_class_overrides_land_in_their_class(built, ev):
    o = pd.read_csv(C.CLASS_OVERRIDES, dtype=str)
    assert len(o) == 14 and built[1]["overrides"]["ids_not_found"] == []
    got = ev.loc[o["id"]]
    assert (got["class"].to_numpy() == o["class"].to_numpy()).all()
    assert (got["cls_rule"] == "override").all()


def test_crustal_needs_a_real_depth_within_the_cap(ev):
    cr = ev[ev["family"] == "crustal"]
    z = pd.to_numeric(cr["depth"], errors="coerce")
    bad = cr[cr["depth_status"].isin(C.UNKNOWN_DEPTH) | ~(z <= C.CRUSTAL_MAX_Z)]
    assert set(bad["cls_rule"]) <= {"remark", "override"}
    assert len(bad) == 10


def test_unknown_depth_never_crustal_by_rule(ev):
    u = ev[ev["depth_status"].isin(C.UNKNOWN_DEPTH) & ~ev["cls_rule"].isin(["remark", "override"])]
    assert not (u["family"] == "crustal").any()


def test_nothing_north_of_the_limit(ev):
    assert (ev["latitude"] <= C.LAT_MAX).all()


@pytest.mark.parametrize("i", list(EVENTS))
def test_known_events(ev, i):
    cls, rule = EVENTS[i]
    assert ev.loc[i, "class"] == cls
    assert ev.loc[i, "cls_rule"] == (rule or "override")


def test_frozen_catalog_is_this_build(ev):
    f = FROZEN / "catalog.csv"
    if not f.exists():
        pytest.skip(f"no {f}")
    cat = pd.read_csv(f, dtype={"id": str}, usecols=["id", "class", "cls_rule", "family"]).set_index("id")
    assert cat.index.equals(ev.index)
    assert (cat[["class", "cls_rule", "family"]].to_numpy() == ev[["class", "cls_rule", "family"]].to_numpy()).all()
