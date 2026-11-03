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

CLASS = {"slab_interface": 17600, "slab_deep": 15682, "intra_slab": 3869, "unresolved": 3479, "deep_nest": 3249,
         "forearc": 2293, "outer_rise": 1416, "backarc": 901, "intraarc": 858, "deep_unknown": 789,
         "patagonia_interface": 41, "patagonia_crustal": 36, "unclassified": 1}
RULE = {"band_nomech": 14233, "arc_slab": 8548, "deep_slab": 6889, "band_intraslab": 3743, "nest": 3249,
        "unk_deep": 2583, "unk_nomech": 2434, "band_forearc": 2029, "outer_rise": 1413, "backarc": 901, "cone": 879,
        "arc_crustal": 853, "deep_mid": 762, "arc_below": 415, "below": 374, "deep_forearc": 252, "deep_above": 224,
        "band_mech": 142, "pat_deep": 58, "unk_cone": 44, "pat_interface": 41, "no_slab_deep": 38, "pat_crustal": 32,
        "override": 37, "unk_mech": 14, "remark": 12, "arc_noslab": 5, "unk_normal": 4, "pat_outer": 3,
        "pre_year": 2, "no_slab": 1}
FAM = {"in-slab": 22800, "interface": 17641, "excluded": 5684, "crustal": 4089}
FAM55 = {"in-slab": 1093, "interface": 1044, "excluded": 414, "crustal": 129}

# id: (class, rule); rule None for hand decisions
EVENTS = {"890": ("slab_interface", "unk_cone"),      # Valdivia 1960 M9.5
          "83388": ("slab_interface", "cone"),        # Maule 2010
          "135106": ("slab_interface", "cone"),       # Iquique 2014
          "145193": ("slab_interface", "cone"),       # Illapel 2015
          "69131": ("slab_interface", "cone"),        # Tocopilla 2007
          "251": ("slab_interface", "unk_nomech"),    # 1920 M7.4, default depth before 1964
          "459": ("unresolved", "unk_deep"),          # 1933, ISC 100 km default: not interface
          "157950": ("slab_interface", None),         # Chiloe 2016
          "24": ("intra_slab", None),                 # Santiago 1647
          "28033": ("slab_deep", None),               # Punitaqui 1997
          "96048": ("slab_interface", None),          # Arauco 2011
          "922": ("intraarc", None),                  # Aysen 1960 slow event
          "add:pica1768": ("slab_deep", None),
          "141": ("slab_deep", None),                 # Calama 1870
          "112": ("intraarc", None),                  # Cajon del Maipo 1850
          "186": ("slab_deep", None),                 # 1905 near Santiago, group A
          "389": ("unresolved", "unk_deep"),          # 1930 San Juan belt, left unresolved
          "add:valdivia1960fs": ("slab_interface", "unk_nomech"),
          "add:maule2010or": ("outer_rise", "outer_rise"),
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
    assert len(o) == 37 and built[1]["overrides"]["ids_not_found"] == []
    got = ev.loc[o["id"]]
    assert (got["class"].to_numpy() == o["class"].to_numpy()).all()
    assert (got["cls_rule"] == "override").all()


def test_crustal_needs_a_real_depth_within_the_cap(ev):
    cr = ev[ev["family"] == "crustal"]
    z = pd.to_numeric(cr["depth"], errors="coerce")
    bad = cr[cr["depth_status"].isin(C.UNKNOWN_DEPTH) | ~(z <= C.CRUSTAL_MAX_Z)]
    assert set(bad["cls_rule"]) <= {"remark", "override"}
    assert len(bad) == 12


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


def test_magnitudes_of_the_paper(ev):
    # overrides.csv mag rows, matched through the merged ids of each event
    o = pd.read_csv(C.OVERRIDES, dtype=str).query("field == 'mag'")
    own = {m: i for i, d in zip(ev["id"], ev["dup_ids"].fillna("")) for m in [i, *d.split(";")] if m}
    got = ev.loc[o["id"].map(own), "mag"].to_numpy()
    assert np.allclose(got, o["value"].astype(float).to_numpy())


def test_frozen_catalog_is_this_build(ev):
    f = FROZEN / "catalog.csv"
    if not f.exists():
        pytest.skip(f"no {f}")
    cat = pd.read_csv(f, dtype={"id": str}, usecols=["id", "class", "cls_rule", "family"]).set_index("id")
    assert cat.index.equals(ev.index)
    assert (cat[["class", "cls_rule", "family"]].to_numpy() == ev[["class", "cls_rule", "family"]].to_numpy()).all()
