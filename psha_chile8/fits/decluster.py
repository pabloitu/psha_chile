"""Declustered catalogues (plan B12): Gardner and Knopoff (1974) windows and the nearest-neighbour method of Zaliapin
and Ben-Zion (2013), moved from explore/B9/b9_2_decluster.py.

Settings of B9: Gardner-Knopoff with the windows of van Stiphout et al. (2012), largest event first, foreshock window
equal to the aftershock window; nearest neighbour with b 1, d_f 1.6, the threshold of log10 eta from a two-Gaussian
mixture of the events from 1964. All classes together, Mw >= 4.5, the whole span. Variants: Gardner-Knopoff per class
family (the family of the largest class weight of an event), nearest neighbour with the hypocentral distance (depth
difference 0 where a depth is unknown), and nearest neighbour per class family keeping the largest event of each
cluster (B12: Gardner–Knopoff and nearest neighbour as two options of one factor, both per family).

Writes catalog/declustered/<method>_<DATE>.csv (and <method>_m35_<DATE>.csv, the same from Mw 3.5, for the
completeness rule): event_id of the frozen catalogue, mainshock flag, cluster (event_id of the mainshock of the
cluster; the event itself for a mainshock); the nearest-neighbour files also the parent and log10 eta.
"""
from pathlib import Path

import numpy as np
import pandas as pd

import gr as G

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "catalog/declustered"

# settings
DATE = "2026-11-16e"
MMIN, M35 = 4.5, 3.5
FS = 1.0
NN = dict(b=1.0, df=1.6, since=1964)
FAMILY = {"interface": "w_interface", "in-slab": "w_inslab", "crustal": "w_crustal", "other": "w_outer_rise",
          "unclassified": "w_unclassified"}
METHODS = {"gk": dict(kind="gk"), "gk_family": dict(kind="gk", family=True), "nn": dict(kind="nn"),
           "nn_depth": dict(kind="nn", depth=True), "nn_family": dict(kind="nn", family=True, largest=True)}


def km(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def gk_window(m):
    """Gardner and Knopoff (1974) windows as fitted by van Stiphout et al. (2012): km, days."""
    d = 10 ** (0.1238 * m + 0.983)
    tt = np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))
    return d, tt


def gardner_knopoff(t, lon, lat, m, fs=FS, group=None):
    """Window method, largest event first; the foreshock window is fs times the aftershock window.

    Returns the mainshock flag and the index of the mainshock of every event (its own index for a mainshock). With
    `group`, an event only removes events of its own group."""
    n = t.size
    main, done, cl = np.ones(n, bool), np.zeros(n, bool), np.arange(n)
    g = np.zeros(n, int) if group is None else np.asarray(group)
    for i in np.argsort(-m, kind="stable"):
        if done[i]:
            continue
        d, tt = gk_window(m[i])
        dt = (t - t[i]) * 365.25
        near = (dt <= tt) & (dt >= -fs * tt) & ~done & (g == g[i])
        near[i] = False
        j = np.where(near)[0]
        j = j[km(lon[i], lat[i], lon[j], lat[j]) <= d]
        main[j], done[j], cl[j] = False, True, i
        done[i] = True
    return main, cl


def nearest_neighbour(t, lon, lat, m, z=None, b=NN["b"], df=NN["df"]):
    """Zaliapin and Ben-Zion (2013): nearest-neighbour proximity eta of every event (t in years, time order) and the
    index of its parent; distances in km, at least 1 km; z depths (NaN unknown) give hypocentral distances."""
    n = t.size
    eta, par = np.full(n, np.inf), np.full(n, -1)
    for j in range(1, n):
        r = km(lon[j], lat[j], lon[:j], lat[:j])
        if z is not None:
            r = np.sqrt(r ** 2 + np.nan_to_num(z[j] - z[:j]) ** 2)
        e = np.maximum(t[j] - t[:j], 1e-7) * np.maximum(r, 1.0) ** df * 10 ** (-b * m[:j])
        i = np.argmin(e)
        eta[j], par[j] = e[i], i
    return eta, par


def nn_threshold(eta):
    """Threshold of log10 eta between the clustered and the background mode (two-Gaussian mixture, equal posterior)."""
    from sklearn.mixture import GaussianMixture
    x = np.log10(eta[np.isfinite(eta)]).reshape(-1, 1)
    g = GaussianMixture(2, random_state=0, n_init=3).fit(x)
    lo, hi = np.sort(g.means_.ravel())
    xs = np.linspace(lo, hi, 2000).reshape(-1, 1)
    p = g.predict_proba(xs)[:, np.argmin(g.means_.ravel())]
    return float(xs[np.argmin(np.abs(p - 0.5)), 0])


def nn_clusters(eta, par, thr, m=None):
    """Mainshock flag and the mainshock of the cluster of every event. A cluster is a tree of links below the
    threshold; its first event stays (as in the method), or with magnitudes m its largest event (first on ties)."""
    link = np.log10(eta) < thr
    root = np.arange(eta.size)
    for j in range(eta.size):
        if link[j]:
            root[j] = root[par[j]]
    if m is None:
        return ~link, root
    best = np.arange(eta.size)
    for j in range(eta.size):
        if m[j] > m[best[root[j]]]:
            best[root[j]] = j
    cl = best[root]
    return cl == np.arange(eta.size), cl


def decluster(d, kind, family=False, depth=False, largest=False):
    """One method on a catalogue in time order (columns t, lon, lat, mw, depth and the family weights).

    family: run inside each class family (the family of the largest class weight); for nn the proximities are
    computed inside each family and one threshold is fitted on all of them. largest: the largest event of a
    nearest-neighbour cluster stays instead of the first.
    Returns a frame with the mainshock flag, the index of the cluster's mainshock and, for nn, parent and log10 eta."""
    t, lon, lat, m = (d[c].to_numpy(float) for c in ("t", "lon", "lat", "mw"))
    grp = np.argmax(d[list(FAMILY.values())].to_numpy(), 1) if family else np.zeros(t.size, int)
    if kind == "gk":
        main, cl = gardner_knopoff(t, lon, lat, m, FS, grp if family else None)
        return pd.DataFrame(dict(mainshock=main, cl=cl))
    z = d.depth.to_numpy(float) if depth else None
    eta, par = np.full(t.size, np.inf), np.full(t.size, -1)
    for g in np.unique(grp):
        i = np.where(grp == g)[0]
        e, p = nearest_neighbour(t[i], lon[i], lat[i], m[i], None if z is None else z[i])
        eta[i], par[i] = e, np.where(p >= 0, i[np.maximum(p, 0)], -1)
    thr = nn_threshold(eta[t >= NN["since"]])
    main, root = nn_clusters(eta, par, thr, m if largest else None)
    x = pd.DataFrame(dict(mainshock=main, cl=root, parent=par, log10_eta=np.log10(eta)))
    x.attrs["thr"] = thr
    return x


def one(a):
    name, mmin = a
    d = G.load(mlow=mmin)
    x = decluster(d, **METHODS[name])
    ids = d.event_id.to_numpy()
    o = pd.DataFrame(dict(event_id=ids, mw=d.mw, mainshock=x.mainshock, cluster=ids[x.cl]))
    if "parent" in x:
        o["parent"] = np.where(x.parent >= 0, ids[np.maximum(x.parent, 0)], "")
        o["log10_eta"] = x.log10_eta.round(3)
    o.attrs["thr"] = x.attrs.get("thr")
    return name, mmin, o


def run(mmins=(MMIN, M35)):
    """Every method on the frozen catalogue from each magnitude of mmins (the files from M35 are for the completeness
    rule, which reads the shape of the distribution from Mw 3.5)."""
    from multiprocessing import Pool
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(len(METHODS) * len(mmins)) as p:
        res = p.map(one, [(k, mm) for mm in mmins for k in METHODS])
    for name, mm, o in res:
        o.to_csv(OUT / (f"{name}_{DATE}.csv" if mm == MMIN else f"{name}_m{mm * 10:.0f}_{DATE}.csv"), index=False)
        thr = f", log10 eta threshold {o.attrs['thr']:.2f}" if o.attrs.get("thr") is not None else ""
        print(f"{name} from Mw {mm}: {len(o)} events, {o.mainshock.sum()} mainshocks ({o.mainshock.mean():.1%}){thr}")
    return {(n, mm): o for n, mm, o in res}


if __name__ == "__main__":
    run()
