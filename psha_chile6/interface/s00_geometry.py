# Locked interface from Slab2 between Z_TOP and Z_BOTTOM, cut at SEG_BOUNDS
# with shared boundary nodes, true 3D areas.
# Outputs: geometry/edges.json, geometry/areas.csv, figures/s00_*.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cfg
from interface import config

R = 6371.0


def load_slab(path):
    df = pd.read_csv(path, header=None, names=["lon", "lat", "depth"])
    df["lon"] = np.where(df["lon"] > 180, df["lon"] - 360, df["lon"])
    df["depth"] = -df["depth"]
    return df[np.isfinite(df["depth"])].reset_index(drop=True)


def lon_at(lon, dep, z):
    for i in range(len(dep) - 1):
        d1, d2 = dep[i], dep[i + 1]
        if min(d1, d2) <= z <= max(d1, d2):
            return float(lon[i]) if d1 == d2 else float(lon[i] + (z - d1) / (d2 - d1) * (lon[i + 1] - lon[i]))
    return None


def build(df, c):
    """
    Down-dip edges of the locked interface.

    Per sampled latitude the top node sits at max(Z_TOP, shallowest slab)
    and the bottom node at min(Z_BOTTOM, deepest slab); N_EDGES nodes are
    spaced linearly between them.

    Returns
    -------
    ndarray (N_EDGES, n_lat, 3)
        lon, lat, depth; edge 0 is the top, latitudes south to north.
    """
    df = df[df["lat"].between(c.SEG_BOUNDS[0], c.SEG_BOUNDS[-1])]
    lats = np.sort(df["lat"].unique())
    keep = [lats[0]]
    for la in lats[1:]:
        if la - keep[-1] >= c.LAT_STEP - 1e-6:
            keep.append(la)
    rows = []
    for la in keep:
        g = df[df["lat"] == la].sort_values("lon")
        lon, dep = g["lon"].to_numpy(), g["depth"].to_numpy()
        if len(lon) < 2 or dep.max() < c.MIN_SLAB_DEPTH:
            continue
        zt, zb = max(c.Z_TOP, dep.min()), min(c.Z_BOTTOM, dep.max())
        lt, lb = lon_at(lon, dep, zt), lon_at(lon, dep, zb)
        if lt is not None and lb is not None:
            rows.append((la, lt, lb, zt, zb))
    if len(rows) < 3:
        raise RuntimeError(f"only {len(rows)} usable latitudes")
    la, lt, lb, zt, zb = map(np.asarray, zip(*rows))
    e = np.empty((c.N_EDGES, len(la), 3))
    for i, t in enumerate(np.linspace(0, 1, c.N_EDGES)):
        e[i, :, 0] = lt + t * (lb - lt)
        e[i, :, 1] = la
        e[i, :, 2] = zt + t * (zb - zt)
    return e


def cut(e, lo, hi):
    """Slice to [lo, hi] with interpolated nodes at the exact cut latitudes."""
    lats = e[0, :, 1]
    out = []
    for edge in e:
        pts = []
        for la in (lo, hi):
            la = min(max(la, lats[0]), lats[-1])
            j = int(np.searchsorted(lats, la))
            if j == 0 or lats[j - 1] == la:
                p = edge[max(j - 1, 0)].copy()
            else:
                p = edge[j - 1] + (la - lats[j - 1]) / (lats[j] - lats[j - 1]) * (edge[j] - edge[j - 1])
            pts.append(p)
        mid = edge[(lats > lo + 1e-9) & (lats < hi - 1e-9)]
        out.append(np.vstack([pts[0], mid, pts[1]]))
    return out


def area(edges):
    """Area (km2) of the surface between consecutive edges, ECEF triangles."""
    def xyz(p):
        lon, lat, r = np.radians(p[:, 0]), np.radians(p[:, 1]), R - p[:, 2]
        return np.column_stack([r * np.cos(lat) * np.cos(lon), r * np.cos(lat) * np.sin(lon),
                                r * np.sin(lat)])
    a = 0.0
    for e1, e2 in zip(edges[:-1], edges[1:]):
        p, q = xyz(np.asarray(e1)), xyz(np.asarray(e2))
        u = np.cross(p[1:] - p[:-1], q[:-1] - p[:-1])
        v = np.cross(p[1:] - q[:-1], q[1:] - q[:-1])
        a += 0.5 * (np.linalg.norm(u, axis=1).sum() + np.linalg.norm(v, axis=1).sum())
    return a


def main(c=None):
    c = c or cfg.load(config)
    gd = c.OUT / "geometry"
    gd.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)

    df = load_slab(c.SLAB_XYZ)
    e = build(df, c)
    geo = {c.FULL_ID: {"lat": [c.SEG_BOUNDS[0], c.SEG_BOUNDS[-1]], "area_km2": area(e),
                       "edges": e.round(5).tolist()}}
    for sid, lo, hi in zip(c.SEG_IDS, c.SEG_BOUNDS[:-1], c.SEG_BOUNDS[1:]):
        s = cut(e, lo, hi)
        geo[sid] = {"lat": [lo, hi], "area_km2": area(s), "edges": [x.round(5).tolist() for x in s]}
    (gd / "edges.json").write_text(json.dumps(geo))

    tab = pd.DataFrame([{"seg": k, "lat_min": v["lat"][0], "lat_max": v["lat"][1],
                         "area_km2": round(v["area_km2"], 1)} for k, v in geo.items()])
    tab.to_csv(gd / "areas.csv", index=False)
    ratio = sum(geo[s]["area_km2"] for s in c.SEG_IDS) / geo[c.FULL_ID]["area_km2"]
    print(tab.to_string(index=False))
    print(f"area closure sum(segments)/full = {ratio:.6f}")
    if abs(ratio - 1) > 1e-3:
        raise RuntimeError("segment areas do not close")

    f, (a1, a2) = plt.subplots(1, 2, figsize=(11, 9), gridspec_kw={"width_ratios": [2, 1]})
    piv = df[df["lat"].between(c.SEG_BOUNDS[0] - 1, c.SEG_BOUNDS[-1] + 1)].pivot_table(
        index="lat", columns="lon", values="depth")
    a1.pcolormesh(piv.columns, piv.index, piv.values, shading="auto", cmap="viridis_r")
    for i, sid in enumerate(c.SEG_IDS):
        for ed in geo[sid]["edges"]:
            ed = np.asarray(ed)
            a1.plot(ed[:, 0], ed[:, 1], f"C{i}", lw=0.7)
            a2.plot(ed[:, 1], ed[:, 2], f"C{i}", lw=0.7)
        a1.text(ed[:, 0].mean() + 1.5, np.mean(geo[sid]["lat"]),
                f"{sid}\n{geo[sid]['area_km2']:.0f} km2", color=f"C{i}", fontsize=8)
    for b in c.SEG_BOUNDS:
        a1.axhline(b, color="k", ls="--", lw=0.8)
    a1.set_xlabel("lon")
    a1.set_ylabel("lat")
    a2.invert_yaxis()
    a2.set_xlabel("lat")
    a2.set_ylabel("depth km")
    f.suptitle(f"locked interface {c.Z_TOP:.0f}-{c.Z_BOTTOM:.0f} km")
    f.tight_layout()
    f.savefig(c.FIG / "s00_geometry.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s00")


if __name__ == "__main__":
    main()
