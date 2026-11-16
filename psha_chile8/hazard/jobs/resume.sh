#!/usr/bin/env bash
# One-off (16 Nov): finish the runner stopped during t_if_cut (calc 537), then the new order with t_cr_ref first
cd /data/PyCharmProjects/psha_chile/psha_chile8
export PATH=/data/miniforge3/envs/psha_renta/bin:$PATH
while kill -0 960806 2>/dev/null; do sleep 5; done
t1=$(date +%s); t0=$(date -d "2026-11-16 07:25:09" +%s)
if grep -q "Stored" hazard/jobs/t_if_cut/oq.log && ! grep -q "Traceback" hazard/jobs/t_if_cut/oq.log; then
python - <<PY
import json
p = "hazard/jobs/t_if_cut/build.json"; d = json.load(open(p)); d["calc_id"], d["run_time_s"] = 537, $((t1 - t0))
json.dump(d, open(p, "w"), indent=1, ensure_ascii=False); print("== t_if_cut\n   calc 537, $((t1 - t0)) s")
PY
fi
jobs=$(python -c "from hazard import jobs as J; print(' '.join(['t_cr_ref'] + J.S5A + [j for j in J.S5B if j != 't_cr_ref']))")
ONLY="$jobs" bash hazard/run_all.sh
