#!/usr/bin/env bash
# The whole campaign in one go: source models and OpenQuake jobs
# (hazard/run_all.sh, skipping what is already done), then every table and
# figure, then the report tree outputs/report/<site>/ with report.md.
# A failing figure script is reported at the end and does not stop the rest.
#   conda activate psha_renta; cd psha_chile5
#   bash run_report.sh            full campaign, ~2.5 h
#   SMOKE=1 bash run_report.sh    two cities, a few jobs, ~15 min
cd "$(dirname "$0")"
python check_completeness.py || { echo "check_completeness.py failed"; exit 1; }
bash hazard/run_all.sh || echo "run_all.sh reported failed jobs; continuing with what is done"
failed=""
for s in interface/check_convention.py intraslab/check_rates.py intraslab/sections.py intraslab/depth_profile.py \
         hazard/post.py hazard/tornado.py hazard/disagg.py hazard/fig_intraslab.py \
         hazard/fig_gmm.py hazard/gmm_check.py hazard/figures.py hazard/report.py; do
    echo "== $s"
    python "$s" || failed="$failed $s"
done
if [ -n "$failed" ]; then echo "failed scripts:$failed"; exit 1; fi
