#!/usr/bin/env bash
# S1 of CONTEXT_sources.md: the three reference source models rebuilt on
# catalog.csv, their family-only jobs (logic_tree.BUILD), then the comparison
# with psha_chile5 in outputs/s1/.
#   conda activate psha_renta; cd psha_chile6; bash run_s1.sh
set -eo pipefail
cd "$(dirname "$0")"
python - <<PY
import run
from variants import VARIANTS
for m, v in (("interface", "mmin55"), ("intraslab", "ref"), ("crustal", "ref")):
    run.build(m, VARIANTS[m][v])
PY
bash hazard/run_all.sh
python -c "from intraslab import check_rates; check_rates.main('ref')" > outputs/check_rates_ref.txt
python check_catalog.py | tee outputs/check_catalog.txt
python hazard/catalog_effect.py | tee outputs/catalog_effect.txt
