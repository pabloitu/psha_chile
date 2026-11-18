# psha_chile9

Probabilistic seismic hazard model for Chile: catalogue, earthquake statistics, interface, in-slab and crustal sources, ground motion, hazard.

- How the work is organised: `CLAUDE.md` (sessions), `orchestration/` (plan, status, decisions, questions, session files).
- Code: `src/psha9/`, one sub-package per stage. Settings: `config/` (YAML).
- Inputs: `data/raw/` (never edited) and `data/raw/shapes/` (polygons and lines edited by hand, GeoJSON).
- Outputs: `runs/<stage>/<id>/`, each with `run.yaml` (date, runs read, settings used).
- Figures: `figures/paper`, `supplement`, `presentation`; check figures inside each run; trials in `trials/`.
- Environment: `conda env create -f environment.yml`, then `pip install -e .`
- Two machines: `./sync.sh pull <host>` when you start, `./sync.sh push <host>` when you stop (data, runs, refs, figure outputs, trials; code goes through git).
