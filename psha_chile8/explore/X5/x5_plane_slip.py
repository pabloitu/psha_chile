"""X5: the mechanism test split in two, plane misfit (best nodal plane against the Slab2 plane) and slip misfit (slip
on that plane, seen on the map, against the plate convergence azimuth), against the single Kagan angle."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import x5_lib as X
import x5_models as M

sys.path.insert(0, str(X.ROOT))
from palette import CLASS_COLOR  # noqa: E402

AZ = 257.0
OUT = Path(__file__).parent / "figs" / "plane_slip.png"


def nu(s, d, k):
    s, d, k = np.radians(s), np.radians(d), np.radians(k)
    n = np.stack([-np.sin(d) * np.sin(s), np.sin(d) * np.cos(s), -np.cos(d)], -1)
    u = np.stack([np.cos(k) * np.cos(s) + np.cos(d) * np.sin(k) * np.sin(s),
                  np.cos(k) * np.sin(s) - np.cos(d) * np.sin(k) * np.cos(s), -np.sin(k) * np.sin(d)], -1)
    return n, u


def ang(a, b):
    return np.degrees(np.arccos(np.clip((a * b).sum(-1), -1, 1)))


def split(s, d, k, ss, sd, az=AZ):
    """
    Plane and slip misfit of mechanisms to the interface at their epicentres.

    Parameters
    ----------
    s, d, k : array
        Strike, dip and rake of one nodal plane of each event (degrees).
    ss, sd : array
        Slab2 strike and dip at the epicentre.
    az : float
        Azimuth of the motion of the upper plate relative to the Nazca plate (degrees).

    Returns
    -------
    pl : angle between the closer nodal plane and the Slab2 plane.
    sv : angle on the map between the horizontal part of the slip on that plane (upper plate) and the convergence.
    s90 : the same against a pure thrust (slip straight up the slab dip).
    """
    n, u = nu(s, d, k)
    N, U = nu(ss, sd, np.full(len(ss), 90.0))
    out = []
    for a, b in ((n, u), (u, n)):
        sg = np.sign((a * N).sum(-1))[:, None]
        a, b = a * sg, b * sg
        dz = np.abs((np.degrees(np.arctan2(b[:, 1], b[:, 0])) - az + 180) % 360 - 180)
        out.append((ang(a, N), dz, ang(b, U)))
    p = out[0][0] <= out[1][0]
    return tuple(np.where(p, out[0][j], out[1][j]) for j in range(3))


def main():
    c, g = X.load()
    k = M.subset(g)
    x, cc = g[k], c.loc[g.index[k]]
    hm = cc.strike1.notna().to_numpy() & np.isfinite(x.kag.to_numpy())
    x, cc = x[hm], cc[hm]
    pl, sv, _ = split(*(cc[q].to_numpy(float) for q in ("strike1", "dip1", "rake1")), x.sstr.to_numpy(float), x.dip.to_numpy(float))
    d = np.abs((x.z - x.top).to_numpy())
    h = x.hint.astype(str).to_numpy()

    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, a = plt.subplots(figsize=(8.5, 7.5))
    o = np.argsort(-d)
    sc = a.scatter(pl[o], sv[o], c=np.minimum(d[o], 40), cmap="viridis_r", s=14, alpha=0.8, lw=0)
    for cl, mk in (("interface", "o"), ("crustal", "s")):
        q = h == cl
        a.scatter(pl[q], sv[q], s=90, facecolor="none", edgecolor=CLASS_COLOR["interface" if cl == "interface" else "forearc"],
                  lw=2, marker=mk, label=f"literature {cl}")
    t = np.linspace(0, np.pi / 2, 100)
    a.plot(35 * np.cos(t), 35 * np.sin(t), color="k", ls="--", lw=1.3, label="Kagan 35° (approx.)")
    a.plot([20, 20, 0], [0, 45, 45], color="k", lw=1.8, label="plane ≤ 20°, slip ≤ 45°")
    a.set(xlim=(0, 90), ylim=(0, 180), xlabel="Plane misfit to Slab2 (°)", ylabel="Slip azimuth misfit to plate convergence (°)",
          title=f"{len(x)} mechanisms over the shallow slab")
    f.colorbar(sc, ax=a, label="|depth − slab top| (km)", shrink=0.8)
    a.legend(loc="upper right", frameon=False, fontsize=10)
    f.tight_layout()
    f.savefig(OUT, dpi=160)
    for P, V in ((25, 45), (20, 45), (25, 30), (30, 60)):
        q = (pl <= P) & (sv <= V)
        print(P, V, "pass", q.sum(), "| Kagan<=35", (x.kag <= 35).sum(), "| both", (q & (x.kag <= 35).to_numpy()).sum())


if __name__ == "__main__":
    main()
