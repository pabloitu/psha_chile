#!/usr/bin/env bash
# One-off (16 Nov): the crustal tree in two parts, after resume.sh has finished
cd /data/PyCharmProjects/psha_chile/psha_chile8
while pgrep -f "hazard/jobs/resume.sh" >/dev/null; do sleep 10; done
ONLY="f_cr_tree_a f_cr_tree_b" bash hazard/run_all.sh
