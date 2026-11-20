"""T8: nodal planes per class from the catalogue mechanisms and the class of every crustal cell, ported from
psha_chile8 model/mechanisms/npd.py (D-CR-04, D-CR-05, D-IS-07).

Each mechanism is typed by the plunges of its P, T and B axes (Frohlich 1992). Per class and type one representative
plane and its auxiliary, each at half the type's weight; types below a share are dropped. A class with too few
weighted mechanisms takes the mechanism of its dominant fault system.
"""
import json

import numpy as np
import pandas as pd
import shapely

from .gr import CFG

P = CFG["planes"]
TYPES = ["normal", "reverse", "strike-slip", "oblique"]


def vectors(strike, dip, rake):
    """Unit normal and slip of a nodal plane (Aki and Richards; x north, y east, z down)."""
    f, d, r = np.radians(strike), np.radians(dip), np.radians(rake)
    n = np.stack([-np.sin(d) * np.sin(f), np.sin(d) * np.cos(f), -np.cos(d)], -1)
    s = np.stack([np.cos(r) * np.cos(f) + np.cos(d) * np.sin(r) * np.sin(f),
                  np.cos(r) * np.sin(f) - np.cos(d) * np.sin(r) * np.cos(f), -np.sin(d) * np.sin(r)], -1)
    return n, s


def plane(n, s):
    """Strike, dip and rake of the plane with normal n and slip s (inverse of vectors)."""
    n, s = np.atleast_2d(n).astype(float), np.atleast_2d(s).astype(float)
    up = n[:, 2] > 0
    n[up], s[up] = -n[up], -s[up]
    dip = np.degrees(np.arccos(np.clip(-n[:, 2], -1, 1)))
    f = np.arctan2(-n[:, 0], n[:, 1])
    sd = np.hypot(n[:, 0], n[:, 1])
    cr = s[:, 0] * np.cos(f) + s[:, 1] * np.sin(f)
    sr = -s[:, 2] / np.where(sd > 1e-9, sd, 1.0)
    return np.degrees(f) % 360, dip, np.degrees(np.arctan2(sr, cr))


def axes(strike, dip, rake):
    n, s = vectors(strike, dip, rake)
    return (n - s) / np.sqrt(2), (n + s) / np.sqrt(2), np.cross(n, s)


def plunges(strike, dip, rake):
    """Plunges (degrees) of P, T and B, one row per mechanism."""
    return np.stack([np.degrees(np.arcsin(np.clip(np.abs(v[..., 2]), 0, 1))) for v in axes(strike, dip, rake)], -1)


def kind(pl, oblique=True):
    """
    Frohlich (1992) type from the (P, T, B) plunges: reverse if T > 50°, strike-slip if B > 60°, normal if P > 60°.

    The rest is oblique; with oblique False it takes the type of its largest plunge.
    """
    lim = P["limits"]
    k = np.array(TYPES[:3], dtype=object)[np.argmax(pl, -1)]
    firm = (pl[:, 1] > lim["reverse"]) | (pl[:, 2] > lim["strike-slip"]) | (pl[:, 0] > lim["normal"])
    if oblique:
        k[~firm] = "oblique"
    return k, ~firm


def ternary(pl):
    """Frohlich (1992) / Kaverina et al. (1996) ternary coordinates from the (P, T, B) plunges."""
    p, t, b = np.radians(pl).T
    z = np.arctan2(np.sin(t), np.sin(p)) - np.pi / 4
    c = np.radians(35.26)
    den = np.sin(c) * np.sin(b) + np.cos(c) * np.cos(b) * np.cos(z)
    return np.cos(b) * np.sin(z) / den, (np.cos(c) * np.sin(b) - np.sin(c) * np.cos(b) * np.cos(z)) / den


def representative(e):
    """
    Representative mechanism of one type from its events (strike1..rake1, weight w): the best double couple of the
    summed moment tensor (Kostrov 1974, not read), each event at unit moment times its class weight, so the plane
    sits in the middle of the type's cluster. Returns the two nodal planes, the shallower-dipping first.
    """
    n, s = vectors(e.strike1.to_numpy(float), e.dip1.to_numpy(float), e.rake1.to_numpy(float))
    m = np.einsum("i,ij,ik->jk", e.w.to_numpy(), n, s)
    v = np.linalg.eigh(m + m.T)[1]
    p, t = v[:, 0], v[:, -1]
    a = [tuple(float(x[0]) for x in plane((t + p) / np.sqrt(2), (t - p) / np.sqrt(2))),
         tuple(float(x[0]) for x in plane((t - p) / np.sqrt(2), (t + p) / np.sqrt(2)))]
    return sorted(a, key=lambda q: q[1])


def aux(m):
    n, s = vectors(*m)
    a = plane(s, n)
    return float(a[0][0]), float(a[1][0]), float(a[2][0])


def rnd(x, step=5.0):
    return step * np.round(np.asarray(x, float) / step)


def shares(e):
    w = e.groupby("kind").w.sum().reindex(TYPES, fill_value=0.0)
    return (w / w.sum()).to_dict() if w.sum() > 0 else dict.fromkeys(TYPES, np.nan)


def rows(e, c):
    """Rows of one class: types below the minimum share dropped, the rest renormalised to 0.01, both planes at half
    the type weight, angles to 5°."""
    sh = shares(e)
    top = sorted(sh, key=sh.get, reverse=True)[:P["max_types"]]
    keep = {k: v for k, v in sh.items() if v >= P["min_share"] and k in top}
    tot = sum(keep.values())
    tw = {k: round(v / tot, 2) for k, v in keep.items()}
    big = max(tw, key=tw.get)
    tw[big] = round(1 - sum(v for k, v in tw.items() if k != big), 2)
    out = []
    for k, v in tw.items():
        for st, dp, rk in representative(e[e.kind == k]):
            out.append(dict(cls=c, kind=k, strike=rnd(st) % 360, dip=min(max(rnd(dp), 5.0), 90.0),
                            rake=rnd(rk) if rnd(rk) > -180 else 180.0, weight=round(v / 2, 3)))
    return out


def fault_rows(c):
    m = tuple(P["fault"][c]["plane"])
    k = kind(plunges(*np.array([m], float).T))[0][0]
    return [dict(cls=c, kind=k, strike=m[0], dip=m[1], rake=m[2], weight=1.0)]


def pick(rows, c):
    """
    One plane per type (Pablo, 20 Nov): the plane chosen for the class and type in `pick`, at the full type weight,
    with the Kagan angle to the type's representative mechanism of this run.
    """
    out = []
    for k in dict.fromkeys(r["kind"] for r in rows):
        r = [x for x in rows if x["kind"] == k]
        m = tuple(P["pick"][c][k])
        out.append(dict(cls=c, kind=k, strike=m[0], dip=m[1], rake=m[2], weight=round(2 * r[0]["weight"], 2),
                        kagan=round(kagan(m, (r[0]["strike"], r[0]["dip"], r[0]["rake"])), 1)))
    return out


def events(d, fam, tables):
    """
    Events with a mechanism, one row per class with weight > 0, flagged `inside` the completeness table of the
    class (stats-02).
    """
    d = d[d.mech_src.notna() & d.strike1.notna()].copy()
    pl = plunges(d.strike1.to_numpy(float), d.dip1.to_numpy(float), d.rake1.to_numpy(float))
    d["pP"], d["pT"], d["pB"] = pl.T
    d["x"], d["y"] = ternary(pl)
    out = []
    for c, f in fam.items():
        q = d[d["W_" + c] > 0].copy()
        q["cls"], q["family"], q["w"] = c, f, q["W_" + c]
        tb = sorted(tables[c])
        yr = np.full(len(q), np.inf)
        for mf, y in tb:
            yr[q.mw.to_numpy() >= mf - 1e-6] = y
        q["inside"] = q.t.to_numpy() >= yr
        out.append(q)
    return pd.concat(out, ignore_index=True)


def table(ev, oblique, fallback=True):
    """
    Nodal-plane table per class and the counts, type shares and dropped types behind it.

    oblique : dict family -> bool, oblique as a type of its own; fallback : classes below `min_n` weighted
    mechanisms take their fault mechanism (else their own).
    """
    ins = ev[ev.inside].copy()
    out, pairs, cnt, sh = [], [], [], []
    for c, q in ins.groupby("cls", sort=False):
        q = q.copy()
        q["kind"], q["obl"] = kind(q[["pP", "pT", "pB"]].to_numpy(), oblique[q.family.iat[0]])
        own = q.w.sum() >= P["min_n"] or not fallback or c not in P["fault"]
        cnt.append(dict(cls=c, n=len(q), w=round(q.w.sum(), 1), oblique=round(q.w[q.obl].sum(), 1),
                        source="own" if own else P["fault"][c]["name"]))
        s = shares(q)
        sh.append(dict(cls=c, w=round(q.w.sum(), 1), **{k: round(v, 3) for k, v in s.items()}))
        r = rows(q, c)
        pairs += r
        out += (pick(r, c) if c in P.get("pick", {}) else r) if own else fault_rows(c)
    return pd.DataFrame(out), pd.DataFrame(cnt), pd.DataFrame(sh), pd.DataFrame(pairs)


def kagan(a, b):
    """Kagan angle (degrees) between two double couples, each given by one nodal plane."""
    def frame(m):
        p, t, _ = axes(*m)
        p, t = p.reshape(3), t.reshape(3)
        return np.stack([t, p, np.cross(t, p)])
    r = frame(b) @ frame(a).T
    c = max((np.trace(np.diag(s) @ r) - 1) / 2 for s in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)))
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def cells(dat):
    """
    Class of every crustal cell (D-CR-04): the share of the cell's area in each class polygon, and the class that
    holds the cell centre (the largest share where the centre falls on no polygon).
    """
    g = pd.read_csv(dat / "crustal_grid.csv")
    pol = {f["properties"]["cls"]: shapely.geometry.shape(f["geometry"]) for f in json.loads((dat / "crustal_classes.geojson").read_text())["features"]}
    h = P["cell"] / 2
    box = shapely.box(g.lon - h, g.lat - h, g.lon + h, g.lat + h)
    a = shapely.area(box)
    for c, p in pol.items():
        g[c] = np.round(shapely.area(shapely.intersection(box, p)) / a, 4)
    hold = np.full(len(g), "", dtype=object)
    for c, p in pol.items():
        hold[shapely.contains_xy(p, g.lon, g.lat)] = c
    big = g[list(pol)].idxmax(axis=1).to_numpy()
    g["cls"] = np.where(hold == "", big, hold)
    return g
