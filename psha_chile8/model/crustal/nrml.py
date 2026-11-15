"""NRML 0.4 written as text (as model/interface/nrml.py, from psha_chile7/lib/nrml.py); OpenQuake validates it when a
job reads it."""
import re

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


def model(path, name, srcs):
    write(path, HEAD + f'<sourceModel name="{name}">\n' + "".join(srcs) + "</sourceModel>\n</nrml>\n")


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
