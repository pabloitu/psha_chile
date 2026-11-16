#!/usr/bin/env bash
# Build the jobs of hazard/jobs.py (RUN order: references, family trees, rows, check jobs) and run them one after
# another in OpenQuake; calc id and wall time go into each job's build.json. Unchanged jobs keep their calc id and
# are skipped (FORCE=1 reruns them). Before each job it waits while another OpenQuake job is executing (S2, S3).
# A failed job is listed and the others continue. Ported from psha_chile7 hazard/run_all.sh.
#   bash psha_chile8/hazard/run_all.sh            (ONLY="t_if_ref t_is_ref" for a subset)
cd "$(dirname "$0")/.."
export PATH=/data/miniforge3/envs/psha_renta/bin:$PATH
export PYTHONPATH=/data/PyCharmProjects/psha_renta/oq-engine
ONLY=${ONLY:-}
jobs=${ONLY:-$(python -c "from hazard import jobs as J; print(' '.join(J.RUN))")}
python -c "from hazard import build; build.main('$jobs'.split())" || exit 1
failed=""
for d in $jobs; do
    j=hazard/jobs/$d
    cid=$(python -c "import json; print(json.load(open('$j/build.json')).get('calc_id') or '')")
    if [ -n "$cid" ] && [ -z "$FORCE" ]; then echo "== $d: calc $cid, unchanged"; continue; fi
    while oq engine --lhc 2>/dev/null | grep -q "executing"; do echo "   waiting: another job is executing"; sleep 60; done
    echo "== $d  $(date '+%F %T')"
    t0=$(date +%s)
    (cd "$j" && oq engine --run job.ini > oq.log 2>&1)
    t1=$(date +%s)
    id=$(grep -oE "#[0-9]+ " "$j/oq.log" | tail -1 | tr -d "# ")
    if [ -z "$id" ] || grep -q "Traceback\|\[ERROR\]" "$j/oq.log"; then
        echo "   FAILED after $((t1 - t0)) s, see $j/oq.log"; failed="$failed $d"; continue
    fi
    python - "$j/build.json" "$id" "$((t1 - t0))" <<'PY'
import json, sys
p, cid, t = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = json.load(open(p)); d["calc_id"], d["run_time_s"] = cid, t
json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
print(f"   calc {cid}, {t} s")
PY
done
if [ -n "$failed" ]; then echo "failed jobs:$failed"; exit 1; fi
