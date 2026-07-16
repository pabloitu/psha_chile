# build_ssm_logictree.py
"""
Assemble the source-model logic tree for the full SSM. All source model
files and the logic tree itself are assumed to live in the same directory,
so uncertaintyModel entries are bare filenames.

A component is a list of (branch_id, files, weight) alternatives; the tree
is the cartesian product over components. Fixed sources form a single
alternative with weight 1, so they appear in every branch. For now only
six alternatives for the crustal-fault component: the four slip-rate
recurrence models, the crustalfaults.xml-convention reference, and a
no-faults baseline. When the subduction interface gets its own
alternatives, replace its filename in FIXED with a branched component.
"""

import itertools
from pathlib import Path

import create_faults_slip_moment as cm

FIXED = ["subduction_interface_sources.xml",
         "ssm_intraslab_point_sources.xml",
         "ssm_crustal_point_sources.xml"]


def components():
    w = 1.0 / 6.0
    faults = [(bid, [fname], w) for bid, fname, *_ in cm.branches()]
    faults.append(("reference", ["crustal_faults_reference.xml"], w))
    faults.append(("nofaults", [], w))
    return [[("", FIXED, 1.0)], faults]


def write_logic_tree(comps, lt_path):
    """Write the sourceModel logic tree as the product of all components.

    Parameters
    ----------
    comps : list
        One entry per SSM component, each a list of
        (branch_id, files, weight) alternatives.
    lt_path : str or Path
        Output NRML file. Source models are referenced by bare
        filename, assumed to end up next to this file.
    """
    lt_path = Path(lt_path)
    lt_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<nrml xmlns:gml="http://www.opengis.net/gml"',
        '      xmlns="http://openquake.org/xmlns/nrml/0.4">',
        '    <logicTree logicTreeID="lt_ssm">',
        '        <logicTreeBranchingLevel branchingLevelID="bl1">',
        '            <logicTreeBranchSet uncertaintyType="sourceModel"',
        '                                branchSetID="bs_ssm">',
    ]

    n, wsum = 0, 0.0
    for combo in itertools.product(*comps):
        bid = "_".join(i for i, *_ in combo if i) or "b1"
        w = 1.0
        files = []
        for _, fl, wi in combo:
            w *= wi
            files += fl
        models = "\n".join(f'                        {f}' for f in files)
        lines += [
            f'                <logicTreeBranch branchID="{bid}">',
            '                    <uncertaintyModel>',
            models,
            '                    </uncertaintyModel>',
            f'                    <uncertaintyWeight>{w}</uncertaintyWeight>',
            '                </logicTreeBranch>',
        ]
        n += 1
        wsum += w

    lines += [
        '            </logicTreeBranchSet>',
        '        </logicTreeBranchingLevel>',
        '    </logicTree>',
        '</nrml>',
        '',
    ]
    lt_path.write_text("\n".join(lines))
    print(f"wrote {lt_path.resolve()}: {n} branches, total weight {wsum}")


if __name__ == "__main__":
    write_logic_tree(components(), "ssm_logictree.xml")