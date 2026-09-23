# NRML 0.4 written as text, then indented: no openquake import, the engine
# validates at run time.

import xml.etree.ElementTree as ET

NS = "http://openquake.org/xmlns/nrml/0.4"
ET.register_namespace("", NS)
ET.register_namespace("gml", "http://www.opengis.net/gml")

HEAD = ('<?xml version="1.0" encoding="utf-8"?>\n'
        '<nrml xmlns:gml="http://www.opengis.net/gml" '
        'xmlns="http://openquake.org/xmlns/nrml/0.4">\n')


def write(path, text):
    """Indent with 4 spaces and write; element text (posList, occurRates, gsim arguments) is kept as is."""
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.fromstring(text.encode())
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def mfd(rates, mmin, dm):
    """Incremental MFD; minMag is the first bin centre."""
    r = " ".join(f"{x:.8e}" for x in rates)
    return (f'<incrementalMFD minMag="{mmin + dm / 2:.4f}" binWidth="{dm}">'
            f"<occurRates>{r}</occurRates></incrementalMFD>")


def complex_fault(sid, edges, trt, mfd_xml, msr, aspect, rake):
    """edges: list of node lists [(lon, lat, depth_km), ...], top edge first."""
    kinds = ["faultTopEdge"] + ["intermediateEdge"] * (len(edges) - 2) + ["faultBottomEdge"]
    geo = "".join(f"<{k}><gml:LineString><gml:posList>"
                  + " ".join(f"{x:.5f} {y:.5f} {z:.3f}" for x, y, z in e)
                  + f"</gml:posList></gml:LineString></{k}>\n"
                  for e, k in zip(edges, kinds))
    return (f'<complexFaultSource id="{sid}" name="{sid}" tectonicRegion="{trt}">\n'
            f"<complexFaultGeometry>\n{geo}</complexFaultGeometry>\n"
            f"<magScaleRel>{msr}</magScaleRel><ruptAspectRatio>{aspect}</ruptAspectRatio>\n"
            f"{mfd_xml}\n<rake>{rake}</rake>\n</complexFaultSource>\n")


def simple_fault(sid, name, trace, usd, lsd, dip, rake, trt, mfd_xml, msr, aspect):
    """trace: [(lon, lat), ...] with the fault dipping to the right (Aki & Richards)."""
    pos = " ".join(f"{x:.5f} {y:.5f}" for x, y in trace)
    nm = "".join(ch for ch in str(name) if ch not in '<>&"')
    return (f'<simpleFaultSource id="{sid}" name="{nm}" tectonicRegion="{trt}">'
            f"<simpleFaultGeometry><gml:LineString><gml:posList>{pos}</gml:posList></gml:LineString>"
            f"<dip>{dip}</dip><upperSeismoDepth>{usd}</upperSeismoDepth>"
            f"<lowerSeismoDepth>{lsd}</lowerSeismoDepth></simpleFaultGeometry>"
            f"<magScaleRel>{msr}</magScaleRel><ruptAspectRatio>{aspect}</ruptAspectRatio>"
            f"{mfd_xml}<rake>{rake}</rake></simpleFaultSource>\n")


def point(sid, lon, lat, usd, lsd, hypo, trt, mfd_xml, msr, aspect, npd):
    """npd: list of (probability, strike, dip, rake)."""
    nps = "".join(f'<nodalPlane probability="{p}" strike="{s}" dip="{d}" rake="{r}"/>'
                  for p, s, d, r in npd)
    return (f'<pointSource id="{sid}" name="{sid}" tectonicRegion="{trt}">'
            f"<pointGeometry><gml:Point><gml:pos>{lon:.4f} {lat:.4f}</gml:pos></gml:Point>"
            f"<upperSeismoDepth>{usd:.2f}</upperSeismoDepth>"
            f"<lowerSeismoDepth>{lsd:.2f}</lowerSeismoDepth></pointGeometry>"
            f"<magScaleRel>{msr}</magScaleRel><ruptAspectRatio>{aspect}</ruptAspectRatio>"
            f"{mfd_xml}<nodalPlaneDist>{nps}</nodalPlaneDist>"
            f'<hypoDepthDist><hypoDepth probability="1.0" depth="{hypo:.2f}"/></hypoDepthDist>'
            f"</pointSource>\n")


def model(path, name, srcs):
    write(path, HEAD + f'<sourceModel name="{name}">\n' + "".join(srcs) + "</sourceModel>\n</nrml>\n")


def logic_tree(path, branches):
    """
    Source-model logic tree with one branch set.

    branches: list of (branch_id, [files relative to the tree], weight).
    Weights are written to 12 decimals; the last branch absorbs rounding.
    """
    if abs(sum(w for _, _, w in branches) - 1.0) > 1e-6:
        raise ValueError("branch weights do not sum to 1")
    acc, xml = 0.0, []
    for i, (bid, files, w) in enumerate(branches):
        ws = f"{1.0 - acc:.12f}" if i == len(branches) - 1 else f"{w:.12f}"
        acc += float(ws)
        fl = "".join(f"\n{' ' * 24}{f}" for f in files) + f"\n{' ' * 20}"
        xml.append(f'<logicTreeBranch branchID="{bid}"><uncertaintyModel>'
                   f'{fl}</uncertaintyModel>'
                   f"<uncertaintyWeight>{ws}</uncertaintyWeight></logicTreeBranch>\n")
    write(path, HEAD + '<logicTree logicTreeID="lt_source">\n'
                    '<logicTreeBranchingLevel branchingLevelID="bl1">\n'
                    '<logicTreeBranchSet uncertaintyType="sourceModel" branchSetID="bs1">\n'
                    + "".join(xml)
                    + "</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n</logicTree>\n</nrml>\n")


def trt_id(trt):
    return {"Subduction Interface": "sinter", "Subduction IntraSlab": "sslab",
            "Active Shallow Crust": "asc", "Stable Shallow Crust": "ssc"}.get(
        trt, "".join(ch for ch in trt.lower() if ch.isalnum()))


def gmm_tree(path, gmm):
    """
    Ground-motion logic tree, one branch set per tectonic region.

    gmm: {trt: [(gsim, weight, {argument: value}), ...]}. Branch IDs are
    <trt id>__<gsim>, which post-processing uses to group realizations.
    """
    lv = []
    for i, (trt, rows) in enumerate(gmm.items()):
        if abs(sum(w for _, w, _ in rows) - 1.0) > 1e-6:
            raise ValueError(f"GMM weights for {trt} do not sum to 1")
        br = []
        for g, w, kw in rows:
            args = "".join(f"\n{k} = {v!r}".replace("'", '"') for k, v in kw.items())
            br.append(f'<logicTreeBranch branchID="{trt_id(trt)}__{g}">'
                      f"<uncertaintyModel>[{g}]{args}</uncertaintyModel>"
                      f"<uncertaintyWeight>{w}</uncertaintyWeight></logicTreeBranch>\n")
        lv.append(f'<logicTreeBranchingLevel branchingLevelID="gl{i}">\n'
                  f'<logicTreeBranchSet uncertaintyType="gmpeModel" branchSetID="gs{i}" '
                  f'applyToTectonicRegionType="{trt}">\n' + "".join(br)
                  + "</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n")
    write(path, HEAD + '<logicTree logicTreeID="lt_gmm">\n' + "".join(lv) + "</logicTree>\n</nrml>\n")