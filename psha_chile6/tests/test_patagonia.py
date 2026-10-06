# Antarctic interface (s04b): trench line, plane geometry, area, moment and the written source.

import json
from types import SimpleNamespace

import numpy as np
import pytest

from interface import s04b_patagonia as p
from interface.s00_geometry import area
from lib import gr, nrml


@pytest.fixture
def line(tmp_path):
    xy = [[-76.0 + 0.01 * i, -52.0 + 0.64 * i] for i in range(11)]          # about 7 deg of nearly straight line, 11 vertices
    f = tmp_path / "t.geojson"
    f.write_text(json.dumps({"features": [{"properties": {"Name": "AN\\SA"}, "geometry": {"type": "LineString", "coordinates": xy}},
                                          {"properties": {"Name": "SC/AN"}, "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}}]}))
    return f


def test_trench_line_runs_south_to_north_and_is_resampled(line):
    lon, lat = p.trench_line(line, "AN\\SA", -45.6, 10.0)
    assert lat[0] == pytest.approx(-52.0) and lat[-1] == pytest.approx(-45.6)
    d = p.hav(lon[:-1], lat[:-1], lon[1:], lat[1:])
    assert d.std() / d.mean() < 0.02 and abs(d.mean() - 10.0) < 0.5


def test_trench_line_is_cut_at_the_northern_latitude_and_accepts_reversed_input(line, tmp_path):
    lon, lat = p.trench_line(line, "AN\\SA", -47.0, 10.0)
    assert lat[-1] == pytest.approx(-47.0) and lat[0] == pytest.approx(-52.0)
    g = json.loads(line.read_text())
    g["features"][0]["geometry"]["coordinates"].reverse()
    r = tmp_path / "r.geojson"
    r.write_text(json.dumps(g))
    lon2, lat2 = p.trench_line(r, "AN\\SA", -47.0, 10.0)
    assert np.allclose(lat, lat2) and np.allclose(lon, lon2)


def test_plane_dips_east_with_the_asked_depths_and_dip(line):
    lon, lat = p.trench_line(line, "AN\\SA", -45.6, 10.0)
    e = p.locked_edges(lon, lat, 30.0, 5.0, 10.0, 50.0, 10)
    assert e.shape == (10, len(lon), 3)
    assert np.allclose(e[0, :, 2], 10.0) and np.allclose(e[-1, :, 2], 50.0)
    assert (e[0, :, 0] > lon).all() and (e[-1, :, 0] > e[0, :, 0]).all()
    k = len(lon) // 2
    dx = float(p.hav(e[0, k, 0], e[0, k, 1], e[-1, k, 0], e[-1, k, 1]))
    assert abs(np.degrees(np.arctan2(40.0, dx)) - 30.0) < 0.5                    # 40 km deeper over dx km along the dip


def test_area_is_length_times_width(line):
    lon, lat = p.trench_line(line, "AN\\SA", -45.6, 5.0)
    e = p.locked_edges(lon, lat, 30.0, 5.0, 10.0, 50.0, 10)
    length = float(p.hav(lon[:-1], lat[:-1], lon[1:], lat[1:]).sum())
    assert abs(area(e) / (length * 40.0 / np.sin(np.radians(30.0))) - 1) < 0.01


def test_maximum_magnitude_from_the_area():
    assert p.mmax_area(58000.0) == 8.5 and p.mmax_area(10 ** 4.0) == round((4 + 3.292) / 0.949, 1)


@pytest.mark.parametrize("form", p.FORMS)
def test_written_source_releases_the_geodetic_moment(line, form):
    lon, lat = p.trench_line(line, "AN\\SA", -45.6, 10.0)
    e = p.locked_edges(lon, lat, 30.0, 5.0, 10.0, 50.0, 10)
    a, b, mmax = area(e), 0.85, 8.5
    c = SimpleNamespace(MMIN_HAZ=5.5, M0_C=9.05, CORNER=9.6, BIN_W=0.1, TRT="Subduction Interface", MSR="StrasserInterface", ASPECT=1.0, RAKE=90.0)
    m0 = 0.5 * 30e9 * a * 1e6 * 0.018
    pat = {"lam": {f: m0 / gr.mpr(f, b, 5.5, mmax, 9.05, corner=9.6) for f in p.FORMS}, "b": b, "mmax": mmax, "m0_rate": m0, "edges": e.tolist()}
    cen, r, _ = nrml.mfd_rates(p.source(c, pat, form, "pat"))
    assert abs((r * gr.m0(cen, 9.05)).sum() / m0 - 1) < 0.005
    assert abs(cen[0] - 5.5) < 1e-9 and abs(cen[-1] - mmax) < 1e-9


def test_real_trench_gives_an_area_near_sixty_thousand_km2(paths):
    from interface import config as ic
    if not ic.PAT_TRENCH.exists():
        pytest.skip("no PB2002 trench file")
    lon, lat = p.trench_line(ic.PAT_TRENCH, ic.PAT_NAME, ic.PAT_LAT_NORTH, ic.PAT_STEP_KM)
    a = area(p.locked_edges(lon, lat, ic.PAT_DIP, ic.PAT_Z_TRENCH, ic.PAT_Z_TOP, ic.PAT_Z_BOTTOM, ic.N_EDGES))
    assert lat.max() == pytest.approx(ic.PAT_LAT_NORTH) and lat.min() < -52.0 and 5.0e4 < a < 6.5e4


def test_s05_adds_the_antarctic_source_to_every_branch_file(tmp_path, line):
    import pandas as pd
    import builtchecks as bc
    from interface import config, s05_sources
    from lib import cfg
    c = cfg.load(config, {"PATAGONIA": True, "PAT_TRENCH": line})
    c.OUT = tmp_path
    lon, lat = p.trench_line(line, "AN\\SA", -45.6, 10.0)
    full = p.locked_edges(lon, lat, 30.0, 5.0, 10.0, 50.0, 10)
    (tmp_path / "geometry").mkdir()
    geo = {k: {"edges": full.round(5).tolist()} for k in [c.FULL_ID] + c.SEG_IDS}
    (tmp_path / "geometry" / "edges.json").write_text(json.dumps(geo))
    rows = []
    for geom, sids, wg in (("segmented", c.SEG_IDS, 0.5), ("non_segmented", [c.FULL_ID], 0.5)):
        for rate, chi, wr in (("seismic", "-", 0.25), ("geodetic", "lo", 0.0625), ("geodetic", "mid", 0.125), ("geodetic", "hi", 0.0625)):
            for form in ("tgr", "tapered"):
                for sid in sids:
                    lam = 0.5 / len(sids)
                    rows.append({"geom": geom, "seg": sid, "form": form, "rate": rate, "chi": chi, "b": 0.9, "mmax": 9.0, "lam": lam,
                                 "m0_rate": lam * gr.mpr(form, 0.9, c.MMIN_HAZ, 9.0, c.M0_C, corner=c.CORNER),
                                 "N7.0": lam * float(gr.cum(form, 0.9, c.MMIN_HAZ, 9.0, 7.0, c.M0_C, c.CORNER)),
                                 "N8.0": lam * float(gr.cum(form, 0.9, c.MMIN_HAZ, 9.0, 8.0, c.M0_C, c.CORNER)),
                                 "weight": wg * (1.0 if form == "tapered" else 0.0) * wr * 2})
    (tmp_path / "rates").mkdir()
    bp = pd.DataFrame(rows)
    bp.to_csv(tmp_path / "rates" / "branches.csv", index=False)
    m0 = 0.5 * 30e9 * area(full) * 1e6 * 0.018
    pat = {"lam": {f: m0 / gr.mpr(f, 0.85, c.MMIN_HAZ, 8.5, c.M0_C, corner=c.CORNER) for f in p.FORMS}, "b": 0.85, "mmax": 8.5, "m0_rate": m0, "edges": full.round(5).tolist()}
    pat["N7"] = {f: pat["lam"][f] * float(gr.cum(f, 0.85, c.MMIN_HAZ, 8.5, 7.0, c.M0_C, c.CORNER)) for f in p.FORMS}
    pat["N8"] = {f: pat["lam"][f] * float(gr.cum(f, 0.85, c.MMIN_HAZ, 8.5, 8.0, c.M0_C, c.CORNER)) for f in p.FORMS}
    (tmp_path / "patagonia").mkdir()
    (tmp_path / "patagonia" / "patagonia.json").write_text(json.dumps(pat))
    s05_sources.main(c)
    files = sorted((tmp_path / "nrml").glob("sub__*.xml"))
    assert len(files) == 16 and all("patagonia_" in f.read_text() for f in files)
    t = bc.interface_vs_table(tmp_path / "nrml", bp, c.M0_C, c.MMIN_HAZ, pat)
    assert not bc.worst(t), t.round(5).to_string()
    assert "N7" in bc.worst(bc.interface_vs_table(tmp_path / "nrml", bp, c.M0_C, c.MMIN_HAZ, None))
