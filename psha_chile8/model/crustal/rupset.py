"""Rupture set by the UCERF3 plausibility rules (Milner et al. 2013, Appendix T) on fault subsections, and its
reduction to whole-fault scenarios for the SHERIFS partition (Pablo, 16 Nov).

Faults are cut into subsections of SUB_KM (5 km, fixed for every depth branch; Pablo, 16 Nov: the subsection is a
resolution for the path rules only, so both depth branches share one connectivity). A
rupture is a path of subsections: along one fault a contiguous run in one direction; between faults a jump from the
subsection where the two faults are closest (within JUMP_KM) onto the closest subsection of the next fault, from where
the run continues in one of its two directions; each fault at most once; at least MIN_SUBS subsections of each
fault. Filters: azimuth change at a jump (between the last subsection run on one fault and the first on the next)
<= AZ_JUNCTION; azimuth change from the first to the last subsection <= AZ_TOTAL; cumulative azimuth change along the
path <= AZ_CUM; cumulative rake change <= RAKE_CUM. The Coulomb filter is not applied. For a sinistral fault joining
a dextral one the azimuth is reversed (Appendix T).

Strict rule (Pablo): a linked rupture is kept only if it uses every member fault entirely (every subsection of each
member). Kept ruptures are merged to whole-fault scenarios (the set of member faults), so the area that sets the
magnitude is the area that ruptured and the SHERIFS budgets are charged on the faults that slipped.
"""
import math

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import LineString
from shapely.ops import nearest_points, transform

# settings (UCERF3 Table T1 unless noted)
JUMP_KM = 15.0
AZ_JUNCTION, AZ_TOTAL, AZ_CUM, RAKE_CUM = 60.0, 60.0, 560.0, 180.0
MIN_SUBS = 2
SUB_KM = 5.0
MIN_SR = 1.0

TO = Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True).transform
BACK = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True).transform


def adiff(a, b):
    return (b - a + 180.0) % 360.0 - 180.0


def subsections(s, z):
    """
    Subsections of every fault: the trace (UTM 19S) cut into n = max(1, round(L / SUB_KM)) equal pieces (z unused,
    kept for the call signature).

    Returns
    -------
    DataFrame
        fault (index in s), k (position along the fault), x0, y0, x1, y1 (UTM m), az (azimuth of the piece, degrees),
        L (km), geom (LineString in UTM).
    """
    rows = []
    for i, q in s.iterrows():
        g = transform(TO, LineString(q.trace))
        n = max(1, int(round(g.length / 1e3 / SUB_KM)))
        br = np.linspace(0, g.length, n + 1)
        for k in range(n):
            a, b = g.interpolate(br[k]), g.interpolate(br[k + 1])
            pts = [a] + [g.interpolate(d) for d in np.linspace(br[k], br[k + 1], 8)[1:-1]] + [b]
            piece = LineString([(p.x, p.y) for p in pts])
            az = (math.degrees(math.atan2(b.x - a.x, b.y - a.y))) % 360.0
            rows.append(dict(fault=i, k=k, x0=a.x, y0=a.y, x1=b.x, y1=b.y, az=az, L=piece.length / 1e3, geom=piece))
    return pd.DataFrame(rows)


def jumps(s, sub, main):
    """
    Closest subsection pair of every pair of faults within JUMP_KM, both faults main (or MIN_SR 0).

    Returns
    -------
    dict (i, j) -> (subsection index on i, subsection index on j, distance km); both directions.
    """
    g = {i: transform(TO, LineString(s.trace[i])) for i in s.index}
    out = {}
    idx = {i: sub.index[sub.fault == i].to_numpy() for i in s.index}
    for a in s.index:
        for b in s.index:
            if a >= b or not (main[a] and main[b]):
                continue
            d = g[a].distance(g[b]) / 1e3
            if d > JUMP_KM:
                continue
            best = None
            for ia in idx[a]:
                for ib in idx[b]:
                    dd = sub.geom[ia].distance(sub.geom[ib]) / 1e3
                    if best is None or dd < best[2]:
                        best = (ia, ib, dd)
            out[(a, b)] = best
            out[(b, a)] = (best[1], best[0], best[2])
    return out


def runs(sub, fault, start, direction):
    """Subsection indices of a fault from `start` in `direction` (+1 toward larger k, -1 toward smaller)."""
    ks = sub[sub.fault == fault].sort_values("k")
    idx = ks.index.to_numpy()
    k0 = int(np.where(idx == start)[0][0])
    return idx[k0:] if direction > 0 else idx[k0::-1]


def az_of(sub, idx, direction):
    """Azimuth along a run of subsections in the direction travelled."""
    return (sub.az[idx] + (0.0 if direction > 0 else 180.0)) % 360.0


def ruptures(s, z, main_only=True):
    """
    Every multi-fault rupture (2+ faults) allowed by the UCERF3 rules.

    Returns
    -------
    list of dict
        faults (tuple, in order), subs (tuple of subsection indices along the path), full (bool: every member used
        entirely), L (km), az_total, az_cum, rake_cum.
    sub : DataFrame of subsections.
    """
    sub = subsections(s, z)
    main = (s.sr >= MIN_SR).to_numpy() if main_only else np.ones(len(s), bool)
    main = pd.Series(main, index=s.index)
    jp = jumps(s, sub, main)
    nb = {}
    for (a, b), v in jp.items():
        nb.setdefault(a, []).append((b, v))
    nsub = sub.groupby("fault").size()
    rake = s.rake.to_dict()
    # sinistral: rake within 45 degrees of 0 (Aki and Richards); dextral: within 45 degrees of 180
    sin = {i: abs(adiff(0.0, r)) <= 45.0 for i, r in rake.items()}
    out = []

    def walk(faults, subs, az_first, az_last, cum, rk, last_full):
        i = faults[-1]
        for j, (ia, ib, d) in nb.get(i, []):
            if j in faults:
                continue
            # the jump leaves fault i at subsection ia: the run on i must end there
            if subs[-1] != ia:
                continue
            for direction in (1, -1):
                run = runs(sub, j, ib, direction)
                if len(run) < MIN_SUBS:
                    continue
                az_j = az_of(sub, run[0], direction)
                if sin[i] != sin[j]:
                    az_j = (az_j + 180.0) % 360.0
                dj = abs(adiff(az_last, az_j))
                if dj > AZ_JUNCTION:
                    continue
                # azimuth change inside the run on j
                azs = [az_of(sub, r, direction) for r in run]
                inner = sum(abs(adiff(azs[t], azs[t + 1])) for t in range(len(azs) - 1))
                c2 = cum + dj + inner
                r2 = rk + abs(adiff(rake[i], rake[j]))
                if c2 > AZ_CUM or r2 > RAKE_CUM:
                    continue
                for stop in range(MIN_SUBS, len(run) + 1):
                    part = run[:stop]
                    az_end = az_of(sub, part[-1], direction)
                    if abs(adiff(az_first, az_end)) > AZ_TOTAL:
                        continue
                    full = last_full and stop == nsub[j]
                    f2, s2 = faults + [j], subs + list(part)
                    out.append(dict(faults=tuple(f2), subs=tuple(s2), full=full, L=float(sub.L[list(s2)].sum()),
                                    az_total=abs(adiff(az_first, az_end)), az_cum=c2, rake_cum=r2))
                    walk(f2, s2, az_first, az_end, c2, r2, full)

    for i in s.index:
        if not main[i]:
            continue
        idx = sub.index[sub.fault == i].to_numpy()
        for direction in (1, -1):
            for start in idx:
                run = runs(sub, i, start, direction)
                if len(run) < MIN_SUBS:
                    continue
                # a first fault may be partial only at its start; strict: it is full when start is its first subsection
                for stop in range(MIN_SUBS, len(run) + 1):
                    part = run[:stop]
                    az0, az1 = az_of(sub, part[0], direction), az_of(sub, part[-1], direction)
                    azs = [az_of(sub, r, direction) for r in part]
                    inner = sum(abs(adiff(azs[t], azs[t + 1])) for t in range(len(azs) - 1))
                    full = stop == nsub[i] and len(part) == nsub[i]
                    walk([i], list(part), az0, az1, inner, 0.0, full)
    uniq = {}
    for r in out:
        key = (r["faults"], r["subs"])
        uniq.setdefault(key, r)
    return list(uniq.values()), sub


def scenarios(rups):
    """Whole-fault scenarios of the strict ruptures: unique sets of member faults, with the longest path kept."""
    best = {}
    for r in rups:
        if not r["full"]:
            continue
        k = frozenset(r["faults"])
        if k not in best or r["L"] > best[k]["L"]:
            best[k] = r
    return list(best.values())


def summary(s, rups, sub, z):
    """Counts and extents per rule: all ruptures, strict ones, scenarios; longest path and largest scenario."""
    sc = scenarios(rups)
    L_all = max((r["L"] for r in rups), default=0.0)
    L_sc = max((float(s.L[list(r["faults"])].sum()) for r in sc), default=0.0)
    return dict(depth=z, subsections=len(sub), ruptures=len(rups), strict=sum(r["full"] for r in rups),
                scenarios=len(sc), max_faults=max((len(r["faults"]) for r in sc), default=0),
                longest_path_km=L_all, longest_scenario_km=L_sc)
