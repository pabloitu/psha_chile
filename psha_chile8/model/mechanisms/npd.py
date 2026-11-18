"""Nodal-plane distributions per class from the catalogue mechanisms (plan B14).

Each mechanism is typed from the plunges of its P, T and B axes (Frohlich 1992); an oblique event goes to the type of
its largest plunge. Per class and type: one representative plane (axial circular mean strike on the plane dipping in
the mean direction, weighted median dip and rake) and its auxiliary plane, each at half the type's weight. Events
inside the completeness table of the fits of each class (run.table_of), counted with their class weight. A class with fewer than MIN_N weighted
mechanisms takes the mechanism of its dominant fault system (FAULT). Writes npd_<DATE>.csv, tables/ and figs/ (ternary with the representative mechanisms, beach balls).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "fits")]
import gr as G  # noqa: E402
import run as R  # noqa: E402

# settings
DATE = "2026-11-18"
CAT = ROOT / "catalog/frozen/2026-11-17g/catalog_2026-11-17g.csv"
# the table of the fits per class (run.table_of: in-slab from 1964, crustal from 1976)
TABLE = ROOT / "fits/tables/table_2026-11-18.csv"
# earlier table that the moves are reported against
PREV = "2026-11-16d"
TYPES = ("normal", "reverse", "strike-slip")
# Frohlich (1992): reverse if the T plunge > 50°, strike-slip if B > 60°, normal if P > 60°
LIMITS = {"reverse": 50.0, "strike-slip": 60.0, "normal": 60.0}
# types below this share are dropped and the rest renormalised (Pablo, 16 Nov; 0.05 on 15 Nov)
MIN_SHARE = 0.10
PREV_MIN_SHARE = 0.10
LAT_NS = -30.0
OLD = {"inslab": [(180, 60, -90, 0.5), (0, 30, 90, 0.5)], "crustal": [(0, 60, 90, 0.5), (180, 60, 90, 0.5)]}

FAMILY = {"inslab": ("intraslab_shallow", "intraslab_intermediate", "jujuy_nest"),
          "crustal": ("forearc", "arc", "backarc", "patagonia")}
CLASSES = [c for f in FAMILY.values() for c in f]
# below MIN_N weighted mechanisms a class is not pooled: it takes the mechanism of its dominant fault system, from the
# traces of data/faults/faults_2026-11-15.gpkg (length-weighted axial strike, median dip), rounded to 5° (Pablo, 16 Nov)
MIN_N = 15
FAULT = {"backarc": (10.0, 40.0, 90.0),     # Precordillera thrusts in the crustal grid: strike 9°, dip 37.5°, east
         "patagonia": (110.0, 90.0, 0.0)}   # Magallanes–Fagnano main trace: strike 111°, vertical, left-lateral


def vectors(strike, dip, rake):
    """Unit normal and slip of a nodal plane (Aki and Richards; x north, y east, z down; normal upward)."""
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
    sd = np.sqrt(n[:, 0] ** 2 + n[:, 1] ** 2)
    cr = s[:, 0] * np.cos(f) + s[:, 1] * np.sin(f)
    sr = -s[:, 2] / np.where(sd > 1e-9, sd, 1.0)
    return np.degrees(f) % 360, dip, np.degrees(np.arctan2(sr, cr))


def axes(strike, dip, rake):
    """P, T and B axes (unit vectors) of the double couple of one nodal plane."""
    n, s = vectors(strike, dip, rake)
    return (n - s) / np.sqrt(2), (n + s) / np.sqrt(2), np.cross(n, s)


def plunge(v):
    return np.degrees(np.arcsin(np.clip(np.abs(v[..., 2]), 0, 1)))


def kind(strike, dip, rake):
    """Frohlich (1992) type of each mechanism and whether it was oblique (typed by its largest plunge)."""
    p, t, b = (plunge(v) for v in axes(strike, dip, rake))
    pl = np.stack([p, t, b], -1)
    k = np.array(TYPES, dtype=object)[np.argmax(pl, -1)]
    firm = (t > LIMITS["reverse"]) | (b > LIMITS["strike-slip"]) | (p > LIMITS["normal"])
    return k, ~firm, pl


def ternary(pl):
    """Frohlich (1992) / Kaverina et al. (1996) ternary coordinates from the (P, T, B) plunges in degrees."""
    p, t, b = np.radians(pl).T
    z = np.arctan2(np.sin(t), np.sin(p)) - np.pi / 4
    c = np.radians(35.26)
    den = np.sin(c) * np.sin(b) + np.cos(c) * np.cos(b) * np.cos(z)
    return np.cos(b) * np.sin(z) / den, (np.cos(c) * np.sin(b) - np.sin(c) * np.cos(b) * np.cos(z)) / den


def wmedian(x, w):
    i = np.argsort(x)
    c = np.cumsum(w[i])
    return float(x[i][np.searchsorted(c, c[-1] / 2)])


def representative(e):
    """Representative plane of one type from its events (columns strike1..rake2 and w).

    The mean P and T axes (principal axes of the weighted orientation tensors) give a mean double couple; its
    first plane picks, in every event, the nodal plane with the closer normal. On those planes: axial circular
    mean strike, taken on the side that dips in the mean dip direction, weighted median dip, weighted median rake
    (unwrapped about the circular mean). Returns the plane and its auxiliary plane, (strike, dip, rake) each.
    """
    w = e.w.to_numpy()
    n1, s1 = vectors(e.strike1.to_numpy(), e.dip1.to_numpy(), e.rake1.to_numpy())
    n2, s2 = vectors(e.strike2.to_numpy(), e.dip2.to_numpy(), e.rake2.to_numpy())
    p, t = (n1 - s1) / np.sqrt(2), (n1 + s1) / np.sqrt(2)
    pm = np.linalg.eigh(np.einsum("i,ij,ik->jk", w, p, p))[1][:, -1]
    tm = np.linalg.eigh(np.einsum("i,ij,ik->jk", w, t, t))[1][:, -1]
    tm = tm - (tm @ pm) * pm
    tm /= np.linalg.norm(tm)
    na = (tm + pm) / np.sqrt(2)
    one = np.abs(n1 @ na) >= np.abs(n2 @ na)
    f = np.where(one, e.strike1, e.strike2)
    d = np.where(one, e.dip1, e.dip2)
    r = np.where(one, e.rake1, e.rake2)
    fr = np.radians(f)
    ax = np.degrees(np.arctan2((w * np.sin(2 * fr)).sum(), (w * np.cos(2 * fr)).sum())) / 2
    dd = np.degrees(np.arctan2((w * np.sin(fr + np.pi / 2)).sum(), (w * np.cos(fr + np.pi / 2)).sum()))
    st = ax % 360 if np.cos(np.radians(ax + 90 - dd)) >= 0 else (ax + 180) % 360
    rr = np.radians(r)
    rm = np.degrees(np.arctan2((w * np.sin(rr)).sum(), (w * np.cos(rr)).sum()))
    rk = (wmedian((r - rm + 180) % 360 - 180, w) + rm + 180) % 360 - 180
    dp = wmedian(d, w)
    n, s = vectors(st, dp, rk)
    a = plane(s, n)
    return (st, dp, rk), (float(a[0][0]), float(a[1][0]), float(a[2][0]))


def rnd(x, step=5.0):
    return step * np.round(np.asarray(x, float) / step)


def entries(e, shares):
    """Rows (strike, dip, rake, weight) of one class: types below MIN_SHARE dropped, both planes at half weight."""
    keep = {k: v for k, v in shares.items() if v >= MIN_SHARE}
    tot = sum(keep.values())
    tw = {k: round(v / tot, 2) for k, v in keep.items()}
    big = max(tw, key=tw.get)
    tw[big] = round(1 - sum(v for k, v in tw.items() if k != big), 2)
    rows = []
    for k, v in tw.items():
        for st, dp, rk in representative(e[e.kind == k]):
            rows.append((k, rnd(st) % 360, min(max(rnd(dp), 5.0), 90.0), rnd(rk) if rnd(rk) > -180 else 180.0,
                         round(v / 2, 3)))
    return rows


def load():
    """Events with a mechanism inside the completeness table, one row per class with weight > 0."""
    a = G.load(CAT, mlow=4.5)
    te = G.tend(a)
    d = a[a.mech_src.notna()].copy()
    tb = pd.read_csv(TABLE)
    tb = list(zip(tb.mw_from, tb.complete_since))
    d["kind"], d["oblique"], pl = kind(d.strike1.to_numpy(), d.dip1.to_numpy(), d.rake1.to_numpy())
    d["pP"], d["pT"], d["pB"] = pl.T
    d["x"], d["y"] = ternary(pl)
    ev = []
    for c in CLASSES:
        q = d[d["W_" + c] > 0].copy()
        q["cls"], q["w"] = c, q["W_" + c]
        yr, _ = G.table_years(R.table_of(c, tb), te)
        q["inside"] = q.t.to_numpy() >= yr[np.clip(G.kbin(q.mw), 0, yr.size - 1)]
        ev.append(q)
    return pd.concat(ev, ignore_index=True)


def shares(e):
    w = e.groupby("kind").w.sum().reindex(TYPES, fill_value=0.0)
    return (w / w.sum()).to_dict() if w.sum() > 0 else dict.fromkeys(TYPES, np.nan)


def run():
    ev = load()
    ins = ev[ev.inside]
    cnt, sh, rows, drop = [], [], [], []
    for c in CLASSES:
        a, i = ev[ev.cls == c], ins[ins.cls == c]
        own = i.w.sum() >= MIN_N
        cnt.append(dict(cls=c, n_all=len(a), w_all=round(a.w.sum(), 1), n_inside=len(i), w_inside=round(i.w.sum(), 1),
                        oblique=round(i.w[i.oblique].sum(), 1), source=c if own else "fault"))
        for part, q in (("all", i), ("north", i[i.lat >= LAT_NS]), ("south", i[i.lat < LAT_NS])):
            sh.append(dict(cls=c, part=part, w=round(q.w.sum(), 1), **{k: round(v, 3) for k, v in shares(q).items()}))
        if own:
            rows += [(c, *r[1:]) for r in entries(i, shares(i))]
            drop += [dict(cls=c, kind=k, share=v) for k, v in shares(i).items() if 0 < v < MIN_SHARE]
        else:
            n, s = vectors(*FAULT[c])
            aux = [float(x[0]) for x in plane(s, n)]
            rows += [(c, *FAULT[c], 0.5), (c, rnd(aux[0]) % 360, rnd(aux[1]), rnd(aux[2]), 0.5)]
    for f, cl in FAMILY.items():
        q = ins[ins.cls.isin(cl)]
        sh.append(dict(cls=f, part="all", w=round(q.w.sum(), 1), **{k: round(v, 3) for k, v in shares(q).items()}))
    npd = pd.DataFrame(rows, columns=["class", "strike", "dip", "rake", "weight"])
    npd.to_csv(HERE / f"npd_{DATE}.csv", index=False)
    (HERE / "tables").mkdir(exist_ok=True)
    pd.DataFrame(cnt).to_csv(HERE / f"tables/counts_{DATE}.csv", index=False)
    pd.DataFrame(sh).to_csv(HERE / f"tables/shares_{DATE}.csv", index=False)
    pd.DataFrame(drop, columns=["cls", "kind", "share"]).to_csv(HERE / f"tables/dropped_{DATE}.csv", index=False)
    figure(ins, npd)
    balls(npd)
    moved()
    print(pd.DataFrame(cnt).to_string(), pd.DataFrame(sh).to_string(), npd.to_string(), pd.DataFrame(drop).to_string(),
          sep="\n\n")
    print("\noblique (events, all classes, inside):", int(ins.drop_duplicates("event_id").oblique.sum()), "of",
          ins.event_id.nunique())


def kagan(a, b):
    """Kagan angle (degrees) between two double couples, each given by one nodal plane (strike, dip, rake)."""
    def frame(m):
        p, t, _ = axes(*m)
        p, t = p.reshape(3), t.reshape(3)
        return np.stack([t, p, np.cross(t, p)])
    r = frame(b) @ frame(a).T
    c = max((np.trace(np.diag(s) @ r) - 1) / 2 for s in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)))
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def moved():
    """Type weights and representative mechanisms of this table against the table of PREV, per class and type."""
    out = []
    t0, t1 = (pd.read_csv(HERE / f"npd_{x}.csv") for x in (PREV, DATE))
    # rows come in pairs, in the order of TYPES, for the types kept in the shares of the class (or of the pooled
    # family); a fault mechanism is one pair, typed from its plane
    for t, x, lim in ((t0, PREV, PREV_MIN_SHARE), (t1, DATE, MIN_SHARE)):
        sh = pd.read_csv(HERE / f"tables/shares_{x}.csv").query("part == 'all'").set_index("cls")
        src = pd.read_csv(HERE / f"tables/counts_{x}.csv").set_index("cls").source
        k = []
        for c in t["class"].drop_duplicates():
            if src[c] == "fault":
                k += [kind(*np.array([t[t["class"] == c].iloc[0, 1:4]], float).T)[0][0]] * 2
            else:
                r = sh.loc[src[c].replace(" (pooled)", "")]
                k += [y for y in TYPES if r[y] >= lim for _ in (0, 1)]
        t["kind"] = k
    for c in CLASSES:
        for k in TYPES:
            a, b = (t[(t["class"] == c) & (t.kind == k)] for t in (t0, t1))
            out.append(dict(cls=c, kind=k, w_prev=round(a.weight.sum(), 3), w_now=round(b.weight.sum(), 3),
                            plane_prev="/".join(f"{x:.0f}" for x in a.iloc[0, 1:4]) if len(a) else "",
                            plane_now="/".join(f"{x:.0f}" for x in b.iloc[0, 1:4]) if len(b) else "",
                            kagan=round(kagan(tuple(a.iloc[0, 1:4]), tuple(b.iloc[0, 1:4])), 1) if len(a) and len(b)
                            else np.nan))
    m = pd.DataFrame(out)
    m.to_csv(HERE / f"tables/moved_{DATE}.csv", index=False)
    print(m.to_string())


def figure(ins, npd):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import palette as P
    P.apply()
    corner = {"reverse": (1.2247, -0.7071), "normal": (-1.2247, -0.7071), "strike-slip": (0.0, 1.4142)}
    fig, axs = plt.subplots(2, 4, figsize=(15, 7.6), layout="constrained")
    for ax, c in zip(axs.flat, CLASSES + [None]):
        ax.set_aspect("equal")
        ax.axis("off")
        if c is None:
            for m in (5, 6, 7, 8):
                ax.scatter([], [], s=(m - 4.2) ** 3 * 6, color="0.5", alpha=0.6, label=str(m))
            ax.scatter([], [], marker="*", s=260, color="0.7", edgecolor="0.1", lw=0.9, label="representative\nmechanism\n(weight)")
            ax.legend(loc="center", title="Mw", labelspacing=1.4, borderpad=1)
            continue
        q = ins[ins.cls == c].sort_values("mw")
        # boundaries of the Frohlich classes
        g = np.linspace(0, np.pi / 2, 200)
        for i, k in enumerate(TYPES):
            cl = np.cos(np.radians(LIMITS[k]))
            pl = np.zeros((g.size, 3))
            pl[:, i] = LIMITS[k]
            pl[:, [j for j in range(3) if j != i]] = np.degrees(np.arcsin(cl * np.stack([np.cos(g), np.sin(g)], -1)))
            x, y = ternary(pl)
            ax.plot(x, y, color="0.75", lw=0.8, zorder=1)
        tri = np.array([corner["normal"], corner["reverse"], corner["strike-slip"], corner["normal"]])
        ax.plot(*tri.T, color="0.4", lw=0.9, zorder=1)
        ax.scatter(q.x, q.y, s=(q.mw - 4.2) ** 3 * 6, color=P.CLASS_COLOR[c], alpha=0.25 + 0.5 * q.w,
                   edgecolor="white", lw=0.3, zorder=2)
        r = npd[npd["class"] == c].iloc[::2]
        fx, fy = ternary(kind(r.strike.to_numpy(), r.dip.to_numpy(), r.rake.to_numpy())[2])
        ax.scatter(fx, fy, marker="*", s=120 + 500 * 2 * r.weight.to_numpy(), color=P.CLASS_COLOR[c], edgecolor="0.1", lw=0.9, zorder=3)
        for x, y, w in zip(fx, fy, 2 * r.weight.to_numpy()):
            ax.text(x + 0.09, y + 0.06, f"{w:.2f}", fontsize=8, color="0.15", zorder=4)
        for k, (x, y) in corner.items():
            ax.text(x, y + (0.1 if k == "strike-slip" else -0.12), k, ha="center", va="bottom" if k == "strike-slip" else "top",
                    fontsize=10, color="0.3")
        ax.set_xlim(-1.45, 1.45)
        ax.set_ylim(-0.95, 1.65)
        ax.set_title(P.CLASS_NAME[c], loc="center", fontsize=12)
        ax.text(-1.4, 1.55, f"{q.w.sum():.0f} by weight", ha="left", fontsize=9, color="0.4")
    (HERE / "figs").mkdir(exist_ok=True)
    fig.savefig(HERE / "figs/ternary.png", dpi=150)
    fig.savefig(HERE / f"figs/ternary_{DATE}.png", dpi=150)


def balls(npd):
    """Representative mechanisms as beach balls, one per type (first plane of each pair), sized by the type weight."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from obspy.imaging.beachball import beach
    import palette as P
    P.apply()
    fig, axs = plt.subplots(2, 4, figsize=(10, 4.6))
    for r, cl in enumerate((FAMILY["inslab"], FAMILY["crustal"])):
        for k, a in enumerate(axs[r]):
            a.set_xlim(0, 3.3)
            a.set_ylim(0, 1.5)
            a.set_aspect("equal")
            a.axis("off")
            if k >= len(cl):
                continue
            q = npd[npd["class"] == cl[k]].iloc[::2]
            a.set_title(P.CLASS_NAME[cl[k]], fontsize=9)
            for i, m in enumerate(q.itertuples()):
                x = 0.55 + 1.1 * i
                a.add_collection(beach((m.strike, m.dip, m.rake), xy=(x, 0.95), width=0.35 + 0.55 * (2 * m.weight) ** 0.5,
                                       facecolor=P.CLASS_COLOR[cl[k]], linewidth=0.6))
                a.text(x, 0.2, f"{m.strike:.0f}/{m.dip:.0f}/{m.rake:.0f}\nw {2 * m.weight:.2f}", ha="center", va="center", fontsize=6.5)
    fig.tight_layout()
    fig.savefig(HERE / f"figs/beachballs_{DATE}.png", dpi=200)


if __name__ == "__main__":
    run()
