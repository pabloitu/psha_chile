# The classified catalog and the grids the models read: format, conventions and consistency with
# the configs. These tests fail when a new catalog changes something the source models assume.

import numpy as np
import pytest

pytestmark = pytest.mark.data


def on_grid(m, d=0.1):
    m = np.asarray(m, float)
    return np.abs(m / d - np.round(m / d)) < 1e-6


def test_rows_parse_and_ids_are_unique(catalog, paths):
    from lib import cat
    assert catalog["id"].is_unique
    assert len(cat.load(paths.CATALOG)) == len(catalog)
    assert catalog[["longitude", "latitude", "mag"]].notna().all().all()


def test_ranges_are_plausible(catalog):
    assert catalog["mag"].between(3.9, 9.6).all()
    assert catalog["depth"].dropna().between(-10, 700).all() and catalog["depth"].isna().sum() <= 5
    assert catalog["longitude"].between(-95, -50).all() and catalog["latitude"].between(-60, -10).all()


def test_year_column_is_the_calendar_year_of_the_date(catalog):
    # the models do not read it: lib.cat.load recomputes the decimal year from time_iso
    from lib import cat
    y = np.array([cat.decyear(str(s)) for s in catalog["time_iso"]])
    assert (np.floor(y) == catalog["year"].to_numpy()).all()


def test_magnitudes_are_on_the_grid_the_bin_convention_assumes(catalog):
    from lib import gr
    share = on_grid(catalog["mag"]).mean()
    assert gr.HALF == (0.05 if share > 0.99 else 0.0), f"{100 * share:.2f} % of the magnitudes are on the 0.1 grid; gr.HALF = {gr.HALF}"


def test_rounding_is_to_the_nearest_tenth(catalog):
    # GCMT and ISC-GEM events carry their native Mw (two decimals): the catalog magnitude is its nearest 0.1, ties up
    k = catalog["mag_src"].isin(["GCMT", "ISC-GEM"]) & catalog["Mw_native"].notna()
    d = catalog.loc[k, "Mw_native"] - catalog.loc[k, "mag"]
    assert (d.abs() <= 0.0501).mean() > 0.93 and abs(d.mean()) < 0.02
    t = catalog[k & (np.abs((catalog["Mw_native"] * 100).round() % 10 - 5) < 1e-9)]
    assert ((t["mag"] - t["Mw_native"]).round(3) == 0.05).mean() > 0.9


def test_catalog_magnitude_is_cabello_except_overrides(catalog):
    d = catalog[(catalog["mag"] - catalog["mag_cabello"]).abs() > 1e-9]
    assert set(d["mag_src"]) <= {"override"} and len(d) < 40


def test_families_and_classes_agree_with_params(catalog, paths):
    got = catalog.groupby("family")["class"].unique().apply(set).to_dict()
    assert {k: v for k, v in got.items() if k in paths.FAMILIES} == {k: set(v) for k, v in paths.FAMILIES.items()}
    assert set(got) - set(paths.FAMILIES) <= {"excluded"}


def test_observation_end_is_the_same_for_every_family(catalog, paths):
    from lib import cat
    df = cat.load(paths.CATALOG)
    last = [df[df["class"].isin(c)]["year"].max() for k, c in paths.FAMILIES.items() if k != "excluded"]
    assert df["year"].max() > 2022.9 and max(last) - min(last) < 0.05


def test_interface_classes_respect_the_segment_and_patagonia_limits(catalog):
    from interface import config as ic
    s, p = catalog[catalog["class"] == "slab_interface"], catalog[catalog["class"] == "patagonia_interface"]
    assert s["latitude"].min() > ic.SEG_BOUNDS[0] - 0.01
    assert p["latitude"].max() < -46.0 and p["latitude"].min() > -58.0


def test_mmax_of_the_segments_covers_the_catalog(catalog):
    import pandas as pd
    from interface import config as ic
    s = catalog[catalog["class"] == "slab_interface"]
    s = s[s["latitude"].between(ic.SEG_BOUNDS[0], ic.SEG_BOUNDS[-1])]
    seg = pd.cut(s["latitude"], ic.SEG_BOUNDS, labels=ic.SEG_IDS, right=False)
    top = s.groupby(seg, observed=True)["mag"].max()
    for k in ic.SEG_IDS:
        assert top[k] <= ic.MMAX[k] + 1e-9, (k, top[k], ic.MMAX[k])
    assert s["mag"].max() <= max(ic.MMAX.values()) + 1e-9


def slab_nodes(paths):
    import pandas as pd
    f = next((p for p in (paths.SLAB_XYZ, paths.SLAB_STR) if p.exists()), None)
    if f is None:
        pytest.skip("no Slab2 grid")
    s = pd.read_csv(f, header=None, names=["lon", "lat", "v"]).dropna()
    return s


def test_slab2_ends_where_the_segments_end(paths):
    from interface import config as ic
    s = slab_nodes(paths)
    assert abs(s["lat"].min() - ic.SEG_BOUNDS[0]) < 0.1, "Slab2 coverage and the southern segment limit differ"
    assert np.isclose(np.diff(np.sort(s["lat"].unique())).min(), 0.05, atol=1e-6)


def test_pb2002_antarctic_trench_input(paths):
    import json
    f = next(iter((paths.REPO / "data" / "shapefiles").glob("*antarctic*trench*.geojson")), None)
    if f is None:
        pytest.skip("no PB2002 trench file")
    g = json.loads(f.read_text())
    an = next(x for x in g["features"] if x["properties"].get("Name") == "AN\\SA")
    xy = np.array(an["geometry"]["coordinates"])
    assert xy[:, 1].max() > -45.8 and xy[:, 1].min() < -52.0
    d = np.hypot(np.diff(xy[:, 0]) * np.cos(np.radians(xy[:-1, 1])), np.diff(xy[:, 1])) * 111.2
    assert abs(d.sum() / 731 - 1) < 0.05 and len(xy) < 20, "the trench line is coarse: densify before building a source"
