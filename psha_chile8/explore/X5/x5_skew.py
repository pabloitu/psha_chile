"""X5: a skewed Kagan angle. The rotation from the interface mechanism to an event is split into a swing (tilt of the
fault plane) and a twist (turn of the slip about the plane normal), each scaled by its own tolerance."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import x5_lib as X
import x5_models as M
import x5_plane_slip as P

TOL = (20.0, 45.0)
AZ = P.AZ
OUT = Path(__file__).parent / "figs" / "skew_kagan.png"

sys.path.insert(0, str(X.ROOT))
from palette import CLASS_COLOR  # noqa: E402


def frames(s, d, k):
    n, u = P.nu(s, d, k)
    return [(n, u), (-n, -u), (u, n), (-u, -n)]


def skew(s, d, k, ss, sd, tol=TOL, az=AZ, norm=2):
    """
    Skewed Kagan measure of mechanisms against the interface at their epicentres.

    The interface mechanism has the Slab2 plane and slips along the plate convergence projected on that plane. For
    each of the four equivalent descriptions of the double couple, the rotation to the interface is split into a swing
    of the plane normal and a twist about it; the measure is the smallest scaled size of the pair.

    Parameters
    ----------
    s, d, k : array
        Strike, dip, rake of one nodal plane (degrees).
    ss, sd : array
        Slab2 strike and dip at the epicentre.
    tol : (float, float)
        Tolerances of swing and twist (degrees).
    norm : 2 or np.inf
        2 gives an ellipse in (swing, twist), inf a box.

    Returns
    -------
    m : array, scaled measure (interface possible where m <= 1).
    sw, tw : array, swing and twist (degrees) of the description that gives m.
    """
    N, _ = P.nu(ss, sd, np.full(len(ss), 90.0))
    h = np.stack([np.full(len(ss), np.cos(np.radians(az))), np.full(len(ss), np.sin(np.radians(az))), np.zeros(len(ss))], -1)
    V = h - (h * N).sum(-1, keepdims=True) * N
    V /= np.linalg.norm(V, axis=-1, keepdims=True)
    best = np.full((3, len(ss)), np.inf)
    for a, b in frames(s, d, k):
        sw = P.ang(a, N)
        ax = np.cross(a, N)
        ln = np.linalg.norm(ax, axis=-1, keepdims=True)
        ax = np.where(ln > 1e-9, ax / np.maximum(ln, 1e-12), 0.0)
        t = np.radians(sw)[:, None]
        b2 = b * np.cos(t) + np.cross(ax, b) * np.sin(t) + ax * (ax * b).sum(-1, keepdims=True) * (1 - np.cos(t))
        tw = P.ang(b2, V)
        z = np.c_[sw / tol[0], tw / tol[1]]
        m = np.linalg.norm(z, ord=norm, axis=1)
        q = m < best[0]
        best[:, q] = np.vstack([m, sw, tw])[:, q]
    return best


def main():
    c, g = X.load()
    k = M.subset(g)
    x, cc = g[k], c.loc[g.index[k]]
    hm = cc.strike1.notna().to_numpy() & np.isfinite(x.kag.to_numpy())
    x, cc = x[hm], cc[hm]
    a = [cc[q].to_numpy(float) for q in ("strike1", "dip1", "rake1")]
    ss, sd = x.sstr.to_numpy(float), x.dip.to_numpy(float)
    pl, sv, _ = P.split(*a, ss, sd)
    box = (pl <= TOL[0]) & (sv <= TOL[1])
    m2, sw, tw = skew(*a, ss, sd)
    mi = skew(*a, ss, sd, norm=np.inf)[0]
    iso = skew(*a, ss, sd, tol=(1.0, 1.0))[0]
    kv = X.kagan(*a, ss, sd, np.full(len(ss), 90.0))
    print("events", len(x))
    print("swing = plane misfit: max diff", np.abs(sw - pl)[np.isfinite(sw)].max().round(2))
    print("box test pass", box.sum(), "| skewed, box norm pass", (mi <= 1).sum(), "disagree", ((mi <= 1) != box).sum())
    print("skewed, ellipse pass", (m2 <= 1).sum(), "disagree with box", ((m2 <= 1) != box).sum())
    print("isotropic version (equal weights, convergence reference) vs Kagan to convergence-free thrust: corr",
          np.corrcoef(iso, kv)[0, 1].round(3))
    h = x.hint.astype(str).to_numpy()
    for cl in ("interface", "crustal"):
        q = h == cl
        print(cl, "skewed ellipse m:", np.sort(m2[q]).round(2))
    d = np.abs((x.z - x.top).to_numpy())
    best = x.depth_src.isin(X.BEST).to_numpy()
    for nm, q in (("ellipse pass", m2 <= 1), ("ellipse fail", m2 > 1), ("Kagan<=35 pass", kv <= 35)):
        print(nm, q.sum(), "best depths within 10 km of slab:", np.round((d[q & best] <= 10).mean(), 2), "n", (q & best).sum())

    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, ax = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1.15, 1.0]})
    a = ax[0]
    o = np.argsort(-d)
    sc = a.scatter(sw[o], tw[o], c=np.minimum(d[o], 40), cmap="viridis_r", s=13, alpha=0.8, lw=0)
    q = h == "interface"
    a.scatter(sw[q], tw[q], s=90, facecolor="none", edgecolor=CLASS_COLOR["interface"], lw=2, label="literature interface")
    q = h == "crustal"
    a.scatter(sw[q], tw[q], s=90, facecolor="none", edgecolor=CLASS_COLOR["forearc"], lw=2, marker="s", label="literature crustal")
    e = np.linspace(0, np.pi / 2, 100)
    a.plot(TOL[0] * np.cos(e), TOL[1] * np.sin(e), color="k", lw=2.2, label=f"skewed: swing/{TOL[0]:.0f}° and twist/{TOL[1]:.0f}°, m = 1")
    a.plot([TOL[0], TOL[0], 0], [0, TOL[1], TOL[1]], color="k", lw=1, ls=":", label="box: plane and slip tests apart")
    a.plot(35 * np.cos(e), 35 * np.sin(e), color="0.4", lw=1.3, ls="--", label="equal weights (Kagan-like), 35°")
    a.set(xlim=(0, 90), ylim=(0, 180), xlabel="Swing: tilt of the fault plane from Slab2 (°)",
          ylabel="Twist: turn of the slip from convergence, in the plane (°)", title="1. The rotation split in two")
    a.legend(loc="upper right", frameon=False, fontsize=9.5)
    f.colorbar(sc, ax=a, label="|depth − slab top| (km)", shrink=0.8)
    a = ax[1]
    bins = np.r_[np.linspace(0, 5, 26), 20]
    for nm, q, col in (("within 10 km of the slab", best & (d <= 10), CLASS_COLOR["interface"]),
                       ("more than 20 km away", best & (d > 20), CLASS_COLOR["intraslab_shallow"])):
        a.hist(np.minimum(m2[q], 5), bins=bins[:-1], histtype="step", lw=2.2, color=col, density=True, label=f"{nm} ({q.sum()})")
    a.axvline(1, color="k", lw=1.2)
    a.text(1.08, a.get_ylim()[1] * 0.92, "m = 1", fontsize=10)
    a.set(xlim=(0, 5), xlabel="Skewed measure m (5 = 5 or more)", ylabel="Share of events (density)",
          title="2. Events with the best depths")
    a.legend(frameon=False, fontsize=10)
    f.tight_layout()
    f.savefig(OUT, dpi=160)


if __name__ == "__main__":
    main()
