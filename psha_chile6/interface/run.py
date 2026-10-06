# Build source models. Edit the settings below and run this file
# (PyCharm run button, or python run.py from psha_chile5/).
# Outputs land in outputs/<model>/<tag>/, tag derived from the overrides.
#
# Steps are cached one by one. A step depends on the config keys its script
# reads (found by scanning the script for c.KEY) plus those of the steps before
# it; the hash of those values is recorded in config.json. A step whose hash is
# unchanged is skipped, and a step already built with the same hash in another
# folder of the model (usually ref) is copied from there instead of rerun, so a
# variant that only changes a late step does not redo the declustering.

import hashlib
import importlib
import json
import re
import shutil

from lib import cfg
from variants import VARIANTS

# settings
MODEL = "intraslab"
RUN = ["ref"]           # variant names from variants.py, or ["all"]
SET = {}                # extra overrides on top of each variant, e.g. {"Z_BOTTOM": 60.0}
STEPS = None            # None = missing steps only; or e.g. ["s02"], ["s03", "s04"]
FORCE = False           # rerun the selected steps even if done

MODELS = {"interface": ["s00_geometry", "s01_decluster", "s02_mc", "s03_ab", "s04_rates", "s05_sources"],
          "intraslab": ["s00_decluster", "s01_mc", "s02_ssm", "s03_sources"],
          "crustal": ["s00_decluster", "s01_mc", "s02_ssm", "s03_faults", "s04_sources"]}
OPTIONAL = {"s02_mc", "s01_mc"}
REPLACE = {"CLASSES"}       # dict parameters replaced by an override instead of merged
# folders under outputs/<model>/<tag>/ that each step writes; copied when a step is reused
OUTS = {"interface": {"s00": ["geometry"], "s01": ["decluster"], "s02": ["mc"], "s03": ["ab"],
                      "s04": ["rates"], "s05": ["nrml"]},
        "intraslab": {"s00": ["decluster"], "s01": ["mc"], "s02": ["ssm"], "s03": ["nrml"]},
        "crustal": {"s00": ["decluster"], "s01": ["mc"], "s02": ["ssm"], "s03": ["faults", "nrml"],
                    "s04": ["nrml"]}}


def keys(model, step):
    """Config keys the step script reads (c.KEY in its source)."""
    src = importlib.import_module(f"{model}.{step}").__file__
    return set(re.findall(r"\bc\.([A-Z][A-Z0-9_]*)", open(src).read())) - {"OUT", "FIG", "TAG"}


def hashes(model, c, names):
    """Step -> hash of the config values it and the steps before it depend on."""
    d, out, seen = cfg.as_dict(c), {}, set()
    for s in names:
        seen |= keys(model, s)
        out[s.split("_")[0]] = hashlib.sha1(json.dumps({k: d.get(k) for k in sorted(seen)},
                                                       sort_keys=True).encode()).hexdigest()[:12]
    return out


def donor(c, step, h):
    """Another folder of the model whose step was built with the same hash, or None."""
    root = c.OUT_ROOT
    for p in sorted(root.glob("*/config.json")) if root.exists() else []:
        if p.parent == c.OUT:
            continue
        try:
            if json.loads(p.read_text()).get("steps", {}).get(step) == h:
                return p.parent
        except (json.JSONDecodeError, OSError):
            pass
    return None


def copy_step(model, src, dst, step):
    for sub in OUTS[model][step]:
        if (src / sub).exists():
            shutil.rmtree(dst / sub, ignore_errors=True)
            shutil.copytree(src / sub, dst / sub)
    if (src / "figures").exists():
        (dst / "figures").mkdir(parents=True, exist_ok=True)
        for f in (src / "figures").glob(f"{step}_*"):
            shutil.copy(f, dst / "figures" / f.name)


def config(model, over):
    """The run configuration of a model for one override set, without building."""
    mod = importlib.import_module(f"{model}.config")
    o = {}
    for k, v in over.items():
        d = getattr(mod, k, None)
        if isinstance(d, dict) and isinstance(v, dict) and k not in REPLACE:
            v = {**d, **v}
        elif isinstance(d, float) and isinstance(v, int):
            v = float(v)
        o[k] = v
    return cfg.load(mod, o)


def build(model, over, steps=None, force=False):
    """
    Run a model's steps for one override set.

    Dict overrides are merged into the config dict (except REPLACE) and ints
    are cast to float where the config value is float, so equal settings
    share a folder. Without steps, optional steps are skipped and each
    remaining step runs only if its hash changed and no other folder has it.
    """
    c = config(model, over)
    names = MODELS[model]
    todo = [s for s in names if s.split("_")[0] in steps] if steps else [s for s in names if s not in OPTIONAL]
    hs = hashes(model, c, [s for s in names if s not in OPTIONAL])
    p = c.OUT / "config.json"
    done = json.loads(p.read_text()).get("steps", {}) if p.exists() and not force else {}
    plan = []
    for s in todo:
        k = s.split("_")[0]
        h = hs.get(k)
        if h is None or steps:
            plan.append((s, "run"))
        elif done.get(k) == h:
            plan.append((s, "done"))
        else:
            plan.append((s, donor(c, k, h) or "run"))
    print(f"[{model}/{c.TAG}] " + " ".join(f"{s.split('_')[0]}:{'ok' if a == 'done' else 'run' if a == 'run' else 'copy'}"
                                        for s, a in plan))
    for s, a in plan:
        k = s.split("_")[0]
        if a == "done":
            continue
        if a == "run":
            importlib.import_module(f"{model}.{s}").main(c)
        else:
            copy_step(model, a, c.OUT, k)
        if k in hs:
            cfg.snapshot(c, k, value=hs[k])
    return c


def main():
    vs = VARIANTS[MODEL]
    names = list(vs) if RUN == ["all"] else RUN
    bad = [n for n in names if n not in vs]
    if bad:
        raise KeyError(f"unknown variants for {MODEL}: {bad}; available: {list(vs)}")
    for n in names:
        build(MODEL, {**vs[n], **SET}, STEPS, FORCE)


if __name__ == "__main__":
    main()
