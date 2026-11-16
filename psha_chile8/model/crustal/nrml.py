"""NRML 0.4 written as text (as model/interface/nrml.py, from psha_chile7/lib/nrml.py); OpenQuake validates it when a
job reads it."""
import re

import numpy as np

HEAD = '<?xml version="1.0" encoding="utf-8"?>\n<nrml xmlns:gml="http://www.opengis.net/gml" xmlns="http://openquake.org/xmlns/nrml/0.4">\n'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sid(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)


def mfd(m0, r):
    """Incremental MFD; m0 the first bin centre."""
    return (f'<incrementalMFD minMag="{m0:.2f}" binWidth="0.10"><occurRates>' + " ".join(f"{x:.5e}" for x in r)
            + "</occurRates></incrementalMFD>")


def point(i, lon, lat, usd, lsd, hypo, trt, mfd_xml, msr, aspect, npd):
    """npd: list of (probability, strike, dip, rake)."""
    nps = "".join(f'<nodalPlane probability="{p}" strike="{s}" dip="{d}" rake="{r}"/>' for p, s, d, r in npd)
    return (f'<pointSource id="{i}" name="{i}" tectonicRegion="{trt}"><pointGeometry><gml:Point><gml:pos>{lon:.4f} '
            f"{lat:.4f}</gml:pos></gml:Point><upperSeismoDepth>{usd:.1f}</upperSeismoDepth><lowerSeismoDepth>{lsd:.1f}"
            f"</lowerSeismoDepth></pointGeometry><magScaleRel>{msr}</magScaleRel><ruptAspectRatio>{aspect}</ruptAspectRatio>"
            f'{mfd_xml}<nodalPlaneDist>{nps}</nodalPlaneDist><hypoDepthDist><hypoDepth probability="1.0" depth="{hypo:.1f}"/>'
            "</hypoDepthDist></pointSource>\n")


def simple_fault(i, name, trace, usd, lsd, dip, rake, trt, mfd_xml, msr, aspect):
    """trace: [(lon, lat), ...] with the fault dipping to its right."""
    pos = " ".join(f"{x:.5f} {y:.5f}" for x, y in trace)
    nm = "".join(ch for ch in str(name) if ch not in '<>&"')
    return (f'<simpleFaultSource id="{i}" name="{nm}" tectonicRegion="{trt}"><simpleFaultGeometry><gml:LineString>'
            f"<gml:posList>{pos}</gml:posList></gml:LineString><dip>{dip:.1f}</dip><upperSeismoDepth>{usd:.1f}"
            f"</upperSeismoDepth><lowerSeismoDepth>{lsd:.1f}</lowerSeismoDepth></simpleFaultGeometry><magScaleRel>{msr}"
            f"</magScaleRel><ruptAspectRatio>{aspect}</ruptAspectRatio>{mfd_xml}<rake>{rake:.1f}</rake></simpleFaultSource>\n")


def model(path, name, srcs, itime=None, trt="Active Shallow Crust"):
    """Source model; with itime (sources with occurrence probabilities) NRML 0.5 with one source group, which carries
    the investigation time OpenQuake checks against the job."""
    if not itime:
        write(path, HEAD + f'<sourceModel name="{name}">\n' + "".join(srcs) + "</sourceModel>\n</nrml>\n")
        return
    h = HEAD.replace("nrml/0.4", "nrml/0.5")
    write(path, h + f'<sourceModel name="{name}" investigation_time="{itime:.1f}">\n<sourceGroup name="{trt}" '
          f'tectonicRegion="{trt}">\n' + "".join(srcs) + "</sourceGroup>\n</sourceModel>\n</nrml>\n")


def planes(trace, lsd, dip):
    """Planar surfaces of a fault from the surface to lsd km, one per trace segment, dipping to the right of the
    trace: [(top_left, top_right, bottom_left, bottom_right), ...] as (lon, lat, depth)."""
    from openquake.hazardlib.geo.geodetic import azimuth, point_at
    h = lsd / np.tan(np.radians(dip)) if dip < 89.99 else 0.0
    out = []
    for (x0, y0), (x1, y1) in zip(trace[:-1], trace[1:]):
        if abs(x1 - x0) + abs(y1 - y0) < 1e-6:
            continue
        az = (azimuth(x0, y0, x1, y1) + 90.0) % 360.0
        b0, b1 = point_at(x0, y0, az, h), point_at(x1, y1, az, h)
        out.append(((x0, y0, 0.0), (x1, y1, 0.0), (b0[0], b0[1], lsd), (b1[0], b1[1], lsd)))
    return out


def sections(path, name, secs):
    """Geometry model of fault sections: secs is [(section id, planes)]."""
    tag = ("topLeft", "topRight", "bottomLeft", "bottomRight")
    s = []
    for i, pl in secs:
        ps = "".join("<planarSurface>" + "".join(f'<{k} lon="{p[0]:.5f}" lat="{p[1]:.5f}" depth="{p[2]:.3f}"/>'
                                                 for k, p in zip(tag, q)) + "</planarSurface>" for q in pl)
        s.append(f'<section id="{i}">{ps}</section>\n')
    write(path, HEAD.replace("nrml/0.4", "nrml/0.5") + f'<geometryModel name="{name}">\n' + "".join(s) + "</geometryModel>\n</nrml>\n")


def multi_fault(i, name, trt, rups):
    """Multi-fault source: rups is [(magnitude, [section ids], rake, yearly rate)]; Poisson occurrence probabilities
    of 0 and 1 events in one year (investigation time of the model 1 yr)."""
    s = []
    for m, idx, rake, r in rups:
        p0 = np.exp(-r)
        s.append(f'<multiPlanesRupture probs_occur="{p0:.10f} {1 - p0:.10e}"><magnitude>{m:.2f}</magnitude>'
                 f'<sectionIndexes indexes="{",".join(idx)}"/><rake>{rake:.1f}</rake></multiPlanesRupture>\n')
    return f'<multiFaultSource id="{i}" name="{name}" tectonicRegion="{trt}">\n' + "".join(s) + "</multiFaultSource>\n"


def logic_tree(path, levels, ltid="lt_crustal"):
    """
    Source-model logic tree, one branching level per entry of levels: (uncertainty type, [(branch id, value,
    weight), ...]). The first level is sourceModel, later ones extendModel (adds the files of the branch to the model).
    The last branch of a set takes the rounding of the weights.
    """
    xml = []
    for k, (ut, brs) in enumerate(levels):
        if abs(sum(w for *_, w in brs) - 1) > 1e-9:
            raise ValueError(f"weights of level {k + 1} do not sum to 1")
        acc, s = 0.0, []
        for j, (bid, v, w) in enumerate(brs):
            ws = f"{1 - acc:.12f}" if j == len(brs) - 1 else f"{w:.12f}"
            acc += float(ws)
            v = " ".join(v) if isinstance(v, (list, tuple)) else v
            s.append(f'<logicTreeBranch branchID="{bid}"><uncertaintyModel>{v}</uncertaintyModel>'
                     f"<uncertaintyWeight>{ws}</uncertaintyWeight></logicTreeBranch>\n")
        xml.append(f'<logicTreeBranchingLevel branchingLevelID="bl{k + 1}">\n<logicTreeBranchSet uncertaintyType="{ut}" '
                   f'branchSetID="bs{k + 1}">\n' + "".join(s) + "</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n")
    write(path, HEAD + f'<logicTree logicTreeID="{ltid}">\n' + "".join(xml) + "</logicTree>\n</nrml>\n")


def gmm_tree(path, trt, gsim):
    write(path, HEAD + '<logicTree logicTreeID="lt_gmm">\n<logicTreeBranchingLevel branchingLevelID="gl1">\n'
          f'<logicTreeBranchSet uncertaintyType="gmpeModel" branchSetID="gs1" applyToTectonicRegionType="{trt}">\n'
          f'<logicTreeBranch branchID="g1"><uncertaintyModel>{gsim}</uncertaintyModel>'
          "<uncertaintyWeight>1.0</uncertaintyWeight></logicTreeBranch>\n"
          "</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n</logicTree>\n</nrml>\n")
