# Read a finished job from the OpenQuake datastore (ported from psha_chile7 hazard/post.py: load, wquant, iml).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, "/data/PyCharmProjects/psha_renta/oq-engine")

import json

import numpy as np

from hazard import config as hc


def load(job, calc_id=None):
    """
    Curves, realization weights and branch paths of one job.

    Returns
    -------
    dict
        curves (sites, rlzs, imts, levels) in the order of hc.CITIES, w (rlzs), imtls, names, src (source path per
        rlz, tuple of branch ids), gmm ({trt: GMM as OpenQuake writes it} per rlz), info (build.json), calc_id, time.
    """
    from openquake.commonlib.datastore import read
    hd = hc.JOBS_DIR / job
    info = json.loads((hd / "build.json").read_text())
    cid = calc_id or info.get("calc_id")
    if cid is None:
        raise SystemExit(f"{job}: no calc_id in {hd / 'build.json'}")
    ds = read(int(cid))
    if ds["oqparam"].description != info["description"]:
        raise SystemExit(f"{job}: calc {cid} is '{ds['oqparam'].description}', build is '{info['description']}'")
    lt = ds["full_lt"]
    rl = sorted(lt.get_realizations(), key=lambda x: x.ordinal)
    trts = list(lt.gsim_lt.values)
    c = ds["hcurves-rlzs"][:][:, [x.ordinal for x in rl]]
    st = ds["hcurves-stats"][:] if "hcurves-stats" in ds else None
    lon, lat = ds["sitecol"].lons, ds["sitecol"].lats
    r = {"imtls": {k: np.asarray(v) for k, v in ds["oqparam"].imtls.items()}, "info": info, "calc_id": int(cid)}
    w = np.array([x.weight[-1] if np.ndim(x.weight) else x.weight for x in rl], float)
    r["w"] = w / w.sum()
    r["src"] = [tuple(x.sm_lt_path) for x in rl]
    r["gmm"] = [dict(zip(trts, [str(g) for g in x.gsim_rlz.value])) for x in rl]
    ds.close()
    if st is not None:
        m = np.einsum("r,srml->sml", r["w"], c)
        ok = st[:, 0] > 1e-8
        err = float(np.max(np.abs(m[ok] / st[:, 0][ok] - 1))) if ok.any() else 0.0
        if err > 1e-3:
            raise RuntimeError(f"{job}: realization mean and OpenQuake mean differ by {err:.1e}")
        r["mean_check"] = err
    xy = np.array(list(hc.CITIES.values()))
    i = [int(np.argmin(np.hypot(lon - x, lat - y))) for x, y in xy]
    if max(np.hypot(lon[i] - xy[:, 0], lat[i] - xy[:, 1])) > 0.01:
        raise SystemExit(f"{job}: calc {cid} sites do not match hc.CITIES")
    r["curves"] = c[i].astype(float)
    r["names"] = list(hc.CITIES)
    return r


def mean(r, imt="PGA"):
    m = list(r["imtls"]).index(imt)
    return np.einsum("r,srl->sl", r["w"], r["curves"][:, :, m, :])


def wquant(c, w, q):
    """Weighted quantiles across realizations; c (rlzs, levels)."""
    o = np.argsort(c, axis=0)
    cs = np.cumsum(w[o], axis=0) - 0.5 * w[o]
    s = np.take_along_axis(c, o, axis=0)
    return np.array([[np.interp(qq, cs[:, j], s[:, j]) for j in range(c.shape[1])] for qq in q])


def iml(curve, lv, poe):
    """Ground motion at probability poe, log-log interpolation; NaN outside the curve."""
    ok = curve > 0
    if ok.sum() < 2 or not curve[ok].min() <= poe <= curve[ok].max():
        return np.nan
    return float(np.exp(np.interp(np.log(poe), np.log(curve[ok][::-1]), np.log(lv[ok][::-1]))))
