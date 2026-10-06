# NRML writing: sources are valid XML, branch weights close, the written rates read back, and the
# chained source-model tree has one branch set per family (OpenQuake allows 183 branches per set).

import xml.etree.ElementTree as ET

import numpy as np
import pytest

from lib import gr, nrml


def pt(i, trt):
    return nrml.point(f"p{i}", -70.0, -30.0, 0, 30, 15, trt, nrml.mfd([1e-3, 5e-4], 6.0, 0.1), "WC1994", 1.0, [(1.0, 0, 90, 90)])


def test_point_and_complex_fault_sources_are_well_formed(tmp_path):
    inc, e = gr.inc(0.5, "tapered", 0.9, 5.5, 9.0, 0.1, corner=9.6)
    edges = [[(-72, -35, 10), (-72, -34, 10)], [(-71, -35, 50), (-71, -34, 50)]]
    nrml.model(tmp_path / "m.xml", "m", [pt(0, "Active Shallow Crust"), nrml.complex_fault("a", edges, "Subduction Interface", nrml.mfd(inc, 5.5, 0.1), "StrasserInterface", 1.0, 90.0)])
    root = ET.parse(tmp_path / "m.xml").getroot()
    assert [x.tag.split("}")[1] for x in root[0]] == ["pointSource", "complexFaultSource"]


def test_mfd_rates_read_back_what_was_written(tmp_path):
    inc, e = gr.inc(0.8, "tapered", 0.92, 5.5, 9.5, 0.1, corner=9.6)
    nrml.model(tmp_path / "m.xml", "m", [nrml.complex_fault("a", [[(-72, -35, 10), (-72, -34, 10)], [(-71, -35, 50), (-71, -34, 50)]], "Subduction Interface", nrml.mfd(inc, 5.5, 0.1), "StrasserInterface", 1.0, 90.0)])
    c, r, dm = nrml.mfd_rates(tmp_path / "m.xml")
    assert np.allclose(c, gr.mid(e, 0.1)) and np.allclose(r, inc, rtol=1e-7)
    for x in (7.0, 8.0):
        assert abs(r[c >= x - 1e-9].sum() / (0.8 * float(gr.cum("tapered", 0.92, 5.5, 9.5, x, corner=9.6))) - 1) < 1e-6


def test_rates_of_two_sources_add(tmp_path):
    nrml.model(tmp_path / "m.xml", "m", [pt(0, "A"), pt(1, "A")])
    c, r, _ = nrml.mfd_rates(tmp_path / "m.xml")
    assert np.allclose(r, [2e-3, 1e-3])


def test_logic_tree_levels_weights_and_ids(tmp_path):
    lv = [[(f"if-{k}", ["a.xml"], 1 / 7) for k in range(7)], [("is", ["b.xml"], 1.0)]]
    nrml.logic_tree_levels(tmp_path / "lt.xml", lv)
    root = ET.parse(tmp_path / "lt.xml").getroot()
    sets = root.findall(".//{*}logicTreeBranchSet")
    assert [s.get("uncertaintyType") for s in sets] == ["sourceModel", "extendModel"]
    assert abs(sum(float(w.text) for w in sets[0].iter() if w.tag.endswith("uncertaintyWeight")) - 1) < 1e-9
    with pytest.raises(ValueError):
        nrml.logic_tree_levels(tmp_path / "bad.xml", [[("a", ["a.xml"], 0.4)]])


def test_chained_levels_parse_in_openquake_and_the_flat_tree_does_not(tmp_path):
    lt = pytest.importorskip("openquake.hazardlib.logictree")
    (tmp_path / "src").mkdir()
    levels = []
    for fam, trt, n in (("if", "Subduction Interface", 48), ("is", "Subduction IntraSlab", 1), ("cr", "Active Shallow Crust", 12)):
        rows = []
        for k in range(n):
            f = tmp_path / "src" / f"{fam}{k}.xml"
            nrml.model(f, "m", [nrml.point(f"{fam}{k}", -70.0, -30.0, 0, 30, 15, trt, nrml.mfd([1e-3], 6.0, 0.1), "WC1994", 1.0, [(1.0, 0, 90, 90)])])
            rows.append((f"{fam}-{k}", [f"src/{fam}{k}.xml"], 1 / n))
        levels.append(rows)
    nrml.logic_tree_levels(tmp_path / "levels.xml", levels)
    t = lt.SourceModelLogicTree(str(tmp_path / "levels.xml"))
    assert t.get_num_paths() == 48 * 12
    flat = [(f"x{i}", ["src/if0.xml", "src/cr0.xml"], 1 / 576) for i in range(576)]
    nrml.logic_tree(tmp_path / "flat.xml", flat)
    with pytest.raises(Exception, match="too many branches"):
        lt.SourceModelLogicTree(str(tmp_path / "flat.xml"))
