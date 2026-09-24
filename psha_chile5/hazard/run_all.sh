#!/usr/bin/env bash
# Build every job in logic_tree.BUILD and run them one after another in
# OpenQuake, storing each calc id in the job's build.json. Jobs whose inputs did
# not change keep their calc id and are skipped; FORCE=1 reruns them. A failed
# job is reported and the others continue. SMOKE=1 runs logic_tree.SMOKE on two
# cities into its own output tree.
#   conda activate psha_renta; cd psha_chile5; bash hazard/run_all.sh
set -e
cd "$(dirname "$0")/.."
root=$(python -c "from hazard import config as hc; print(hc.OUT_ROOT)")
jobs=$(python -c "from hazard import logic_tree as lt, config as hc; print(' '.join(lt.SMOKE if hc.SMOKE else lt.BUILD))")
python - <<PY
from hazard import logic_tree as lt, config as hc, build
lt.BUILD = lt.SMOKE if hc.SMOKE else lt.BUILD
build.main()
PY
failed=""
for d in $jobs; do
    j=$root/$d
    done_id=$(python -c "import json; print(json.load(open('$j/build.json')).get('calc_id') or '')")
    if [ -n "$done_id" ] && [ -z "$FORCE" ]; then echo "== $d: calc $done_id, unchanged"; continue; fi
    echo "== $d  $(date +%H:%M)"
    ex=$(python -c "import json; print('--exports csv' if json.load(open('$j/build.json')).get('disagg') else '')")
    (cd "$j" && oq engine --run job.ini $ex > oq.log 2>&1) || true
    grep -E "ERROR|Stored" "$j/oq.log" | tail -3
    id=$(grep -oE "#[0-9]+ " "$j/oq.log" | tail -1 | tr -d '# ')
    if [ -z "$id" ] || grep -q "ERROR\|Traceback" "$j/oq.log"; then
        echo "   FAILED, see $j/oq.log"; failed="$failed $d"; continue
    fi
    python - "$j/build.json" "$id" <<'PY'
import json, sys
p, cid = sys.argv[1], int(sys.argv[2])
d = json.load(open(p)); d["calc_id"] = cid; json.dump(d, open(p, "w"), indent=1)
print(f"   calc {cid} -> {p}")
PY
done
if [ -n "$failed" ]; then echo "failed jobs:$failed"; exit 1; fi
