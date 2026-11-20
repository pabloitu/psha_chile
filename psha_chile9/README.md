# psha_chile9

Probabilistic seismic hazard model for Chile: catalogue, earthquake statistics, interface, in-slab and crustal sources, ground motion, hazard.

- How the work is organised: `CLAUDE.md` (sessions), `orchestration/` (plan, status, decisions, questions, session files).
- Code: `src/psha9/`, one sub-package per stage. Settings: `config/` (YAML).
- Inputs: `data/raw/` (never edited) and `data/raw/shapes/` (polygons and lines edited by hand, GeoJSON).
- Outputs: `runs/<stage>/<id>/`, each with `run.yaml` (date, runs read, settings used).
- Figures: `figures/paper`, `supplement`, `presentation`; check figures inside each run; trials in `trials/`.
- Environment (D-ENV-01), from the repo folder:
  - new, exact versions: `mamba create -n psha9 --file psha9-linux64.lock`, then `mamba activate psha9 && pip install -e . --no-deps`
  - after changing `environment.yml`: `mamba env create -f environment.yml`, the same pip line, then `conda list --explicit --md5 > psha9-linux64.lock` and commit the lock
- Two machines: `./sync.sh pull <host>` when you start, `./sync.sh push <host>` when you stop (data, runs, refs, figure outputs, trials; code goes through git).
