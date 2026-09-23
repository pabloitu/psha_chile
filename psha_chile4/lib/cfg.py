import hashlib
import json
from pathlib import Path
from types import SimpleNamespace


def load(mod, over=None):
    """
    Build a run configuration from a config module plus overrides.

    Parameters
    ----------
    mod : module
        Config module with upper-case constants, including OUT_ROOT.
    over : dict, optional
        Constant -> value. Unknown keys raise, so a typo in a variant
        cannot silently run the reference.

    Returns
    -------
    SimpleNamespace
        Constants, plus TAG, OUT and FIG for this override set.
    """
    over = dict(over or {})
    c = SimpleNamespace(**{k: getattr(mod, k) for k in dir(mod) if k.isupper()})
    bad = [k for k in over if not hasattr(c, k)]
    if bad:
        raise KeyError(f"unknown keys for {mod.__name__}: {bad}")
    for k, v in over.items():
        setattr(c, k, v)
    c.TAG = tag(over)
    c.OUT = Path(c.OUT_ROOT) / c.TAG
    c.FIG = c.OUT / "figures"
    return c


def tag(over):
    if not over:
        return "ref"
    s = "_".join(f"{k.lower()}-{v}" for k, v in sorted(over.items()))
    s = "".join(ch if ch.isalnum() or ch in "-_." else "" for ch in s)
    return s if len(s) <= 60 else "v" + hashlib.sha1(s.encode()).hexdigest()[:10]


def as_dict(c):
    return json.loads(json.dumps({k: v for k, v in vars(c).items()
                                  if k.isupper() and k not in ("OUT", "FIG", "TAG")},
                                 default=str))


def snapshot(c, step, extra=None):
    """Record the settings and the finished step in OUT/config.json."""
    c.OUT.mkdir(parents=True, exist_ok=True)
    p = c.OUT / "config.json"
    d = json.loads(p.read_text()) if p.exists() else {}
    if d.get("config") != as_dict(c):
        d = {}
    d["config"] = as_dict(c)
    d.setdefault("steps", {})[step] = True
    if extra:
        d.setdefault("info", {}).update(extra)
    p.write_text(json.dumps(d, indent=1))


def stale(c, steps):
    """True if a step is missing or the outputs were built with other settings."""
    p = c.OUT / "config.json"
    if not p.exists():
        return True
    d = json.loads(p.read_text())
    return d.get("config") != as_dict(c) or not all(d.get("steps", {}).get(s) for s in steps)
