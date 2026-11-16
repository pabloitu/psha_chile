# Logic-tree writers (from psha_chile7 lib/nrml.py): source tree with one level per family plus the interface
# scaling level, and the GMM tree with one branch set per tectonic region

HEAD = ('<?xml version="1.0" encoding="utf-8"?>\n'
        '<nrml xmlns:gml="http://www.opengis.net/gml" xmlns="http://openquake.org/xmlns/nrml/0.4">\n')


def weights(ws):
    """Weights as written (12 decimals), the last one taking the rounding, so OpenQuake sees a sum of 1."""
    if abs(sum(ws) - 1.0) > 1e-6:
        raise ValueError(f"weights sum to {sum(ws)}")
    out = [f"{w:.12f}" for w in ws[:-1]]
    return out + [f"{1.0 - sum(float(x) for x in out):.12f}"]


def source_tree(path, levels, msr=None, msr_trt="Subduction Interface"):
    """
    Source-model logic tree.

    Parameters
    ----------
    path : output file
    levels : list of branch lists [(branch_id, [files], weight)], the first a sourceModel set, the others
        extendModel (each adds its files to the path); at most 183 branches per set
    msr : {branch_id: (scaling relation, weight)} or None; a setMSRAbsolute level applied to msr_trt only
    """
    xml = []
    for k, br in enumerate(levels):
        if len(br) > 183:
            raise ValueError(f"level {k} has {len(br)} branches (OpenQuake limit 183)")
        ws = weights([b[2] for b in br])
        rows = "".join(f'<logicTreeBranch branchID="{b}"><uncertaintyModel>{" ".join(fs)}</uncertaintyModel>'
                       f"<uncertaintyWeight>{w}</uncertaintyWeight></logicTreeBranch>\n"
                       for (b, fs, _), w in zip(br, ws))
        ut = "sourceModel" if k == 0 else "extendModel"
        xml.append(f'<logicTreeBranchingLevel branchingLevelID="bl{k + 1}">\n'
                   f'<logicTreeBranchSet uncertaintyType="{ut}" branchSetID="bs{k + 1}">\n{rows}'
                   "</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n")
    if msr:
        ws = weights([w for _, w in msr.values()])
        rows = "".join(f'<logicTreeBranch branchID="{b}"><uncertaintyModel>{m}</uncertaintyModel>'
                       f"<uncertaintyWeight>{w}</uncertaintyWeight></logicTreeBranch>\n"
                       for (b, (m, _)), w in zip(msr.items(), ws))
        xml.append(f'<logicTreeBranchingLevel branchingLevelID="bl{len(levels) + 1}">\n'
                   f'<logicTreeBranchSet uncertaintyType="setMSRAbsolute" branchSetID="bs_msr" '
                   f'applyToTectonicRegionType="{msr_trt}">\n{rows}'
                   "</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n")
    path.write_text(HEAD + '<logicTree logicTreeID="lt_source">\n' + "".join(xml) + "</logicTree>\n</nrml>\n")


def trt_id(trt):
    return {"Subduction Interface": "sinter", "Subduction IntraSlab": "sslab",
            "Active Shallow Crust": "asc"}.get(trt, "".join(c for c in trt.lower() if c.isalnum()))


def gmm_tree(path, gmm):
    """GMM tree; gmm {trt: [(gsim text as in OpenQuake, weight)]}; branch ids <trt id>_g<i>_<class name>."""
    lv = []
    for i, (trt, rows) in enumerate(gmm.items()):
        ws = weights([w for _, w in rows])
        br = "".join(f'<logicTreeBranch branchID="{trt_id(trt)}_g{k}_{g.split("]")[0].strip("[")}">'
                     f"<uncertaintyModel>{g}</uncertaintyModel><uncertaintyWeight>{w}</uncertaintyWeight>"
                     "</logicTreeBranch>\n" for k, ((g, _), w) in enumerate(zip(rows, ws)))
        lv.append(f'<logicTreeBranchingLevel branchingLevelID="gl{i}">\n'
                  f'<logicTreeBranchSet uncertaintyType="gmpeModel" branchSetID="gs{i}" '
                  f'applyToTectonicRegionType="{trt}">\n{br}</logicTreeBranchSet>\n</logicTreeBranchingLevel>\n')
    path.write_text(HEAD + '<logicTree logicTreeID="lt_gmm">\n' + "".join(lv) + "</logicTree>\n</nrml>\n")
