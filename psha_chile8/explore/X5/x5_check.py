"""X5: every scoring model through every test. Tests: (1) literature classes, (2) mechanisms hidden, (3) classes of
Riedel-Hornig et al. (2026) from local depths, (4) reliability of the scores, (5) synthetic catalogues with known
classes, (6) thrusts far from the slab and other mechanisms on it. Writes tables/x5_*.csv."""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import x5_lib as X
import x5_models as M
import x5_riedel as R
import x5_synth as Y

pd.set_option("display.width", 250, "display.max_columns", 40, "display.max_rows", 300)
CL = ["interface", "in-slab", "crustal"]
# second reference from the Riedel-Hornig depths: interface where their depth lies within LOOSE km of the Slab2 surface
# (the range of the thrust-like events in their depths) and the mechanism, if any, is thrust-like
LOOSE = (-5.0, 15.0)


def brier3(P, y):
    return float(np.mean(((P - np.eye(3)[y]) ** 2).sum(1)))


def ece(p, o, edges=(0.2, 0.4, 0.6, 0.8)):
    """Mean gap between the score and the observed share, over score bins weighted by their size."""
    b = np.digitize(p, edges)
    return float(sum((b == i).mean() * abs(p[b == i].mean() - o[b == i].mean()) for i in range(len(edges) + 1) if (b == i).any()))


def auc(o, p):
    return float(roc_auc_score(o, p)) if 0 < o.sum() < len(o) else np.nan


c, g = X.load()
g = g.join(R.match(g))
x, S, m = M.scores(g)
_, S0, _ = M.scores(g, use_mech=False)
hint = x.hint.map({k: i for i, k in enumerate(CL)}).to_numpy(float)
rc = x.r_cls.map({k: i for i, k in enumerate(CL)}).to_numpy(float)
hm, d, mw = x.kag.notna().to_numpy(), x.d.to_numpy(), x.mw.to_numpy()
thr = (x.kag <= 30).to_numpy()
ell = (x.em <= 1).to_numpy()
d_r = (x.r_z - X.C.slab_at(x.r_lon.fillna(x.lon), x.r_lat.fillna(x.lat))[0]).to_numpy()
loose = ((d_r >= LOOSE[0]) & (d_r <= LOOSE[1]) & (thr | ~hm)).astype(float)
best = x.depth_src.isin(X.BEST).to_numpy()
print("events", len(x), "| mechanism", int(hm.sum()), "| literature", int(np.isfinite(hint).sum()), "| Riedel-Hornig class", int(np.isfinite(rc).sum()),
      "(of them without mechanism", int((np.isfinite(rc) & ~hm).sum()), ", Mw < 5.5", int((np.isfinite(rc) & (mw < 5.45)).sum()), ")")

rows = []
for nm, P in S.items():
    P0, r = S0[nm], {"model": nm}
    q = np.isfinite(hint)
    y = hint[q].astype(int)
    r.update({"1 literature: events": int(q.sum()), "1 right": int((np.argmax(P[q], 1) == y).sum()), "1 Brier (3 classes)": brier3(P[q], y),
              "1 mean score of the true class": float(P[q][np.arange(q.sum()), y].mean())})
    r.update({"2 mechanisms hidden: events": int(hm.sum()), "2 Brier (interface)": float(np.mean((P0[hm, 0] - thr[hm]) ** 2)),
              "2 summed score / thrust-like": float(P0[hm, 0].sum() / thr[hm].sum()), "2 AUC": auc(thr[hm], P0[hm, 0]),
              "2 calibration gap": ece(P0[hm, 0], thr[hm])})
    r.update({"2m the same against the ellipse: Brier (interface)": float(np.mean((P0[hm, 0] - ell[hm]) ** 2)),
              "2m summed score / inside the ellipse": float(P0[hm, 0].sum() / ell[hm].sum()), "2m AUC": auc(ell[hm], P0[hm, 0])})
    for tag, q in (("3 Riedel-Hornig, all", np.isfinite(rc)), ("3b Riedel-Hornig, no mechanism", np.isfinite(rc) & ~hm),
                   ("3c Riedel-Hornig, with mechanism", np.isfinite(rc) & hm)):
        y = rc[q].astype(int)
        r.update({f"{tag}: events": int(q.sum()), f"{tag}: right": int((np.argmax(P[q], 1) == y).sum()), f"{tag}: Brier (3 classes)": brier3(P[q], y),
                  f"{tag}: summed interface / their interface": float(P[q, 0].sum() / (y == 0).sum()), f"{tag}: AUC interface": auc(y == 0, P[q, 0]),
                  f"{tag}: calibration gap": ece(P[q, 0], (y == 0).astype(float))})
    for tag, q in (("3d Riedel-Hornig depth within −5 to +15 km, all", np.isfinite(rc)), ("3e the same, no mechanism", np.isfinite(rc) & ~hm)):
        r.update({f"{tag}: interface events": int(loose[q].sum()), f"{tag}: Brier (interface)": float(np.mean((P[q, 0] - loose[q]) ** 2)),
                  f"{tag}: summed interface / reference": float(P[q, 0].sum() / loose[q].sum()), f"{tag}: AUC": auc(loose[q], P[q, 0]),
                  f"{tag}: calibration gap": ece(P[q, 0], loose[q])})
    q = hm & thr & (np.abs(d) > 20)
    r["6 thrust-like, > 20 km from the slab: interface score"] = float(P[q, 0].mean())
    r["6 other mechanism, within 5 km: interface score"] = float(P[hm & ~thr & (np.abs(d) <= 5), 0].mean())
    for lim in (5, 15):
        q = hm & ~ell & (np.abs(d) <= lim)
        r.update({f"6m outside the ellipse, within {lim} km of the slab: events": int(q.sum()), f"6m outside the ellipse, within {lim} km: mean interface score": float(P[q, 0].mean()),
                  f"6m outside the ellipse, within {lim} km: summed interface": float(P[q, 0].sum())})
    q = hm & ell & (np.abs(d) > 20)
    r["6m inside the ellipse, > 20 km from the slab: interface score"] = float(P[q, 0].mean())
    r.update({f"sum {k}": float(P[:, j].sum()) for j, k in enumerate(CL)})
    r["sum interface, Mw ≥ 5.5"] = float(P[mw >= 5.45, 0].sum())
    r["events with a score ≥ 0.8"] = int((P.max(1) >= 0.8).sum())
    rows.append(r)

# 5 synthetic catalogues
syn = {}
for sc, (err, to) in Y.SCEN.items():
    acc = {nm: [] for nm in S}
    for seed in range(3):
        ys, truth = Y.make(x, err, to, seed)
        xs, Ss, _ = M.scores(ys)
        truth, ys = pd.Series(truth, index=ys.index).loc[xs.index].to_numpy(), xs
        for nm, P in Ss.items():
            acc[nm].append((float((np.argmax(P, 1) == truth).mean()), brier3(P, truth), float(P[:, 0].sum() / (truth == 0).sum()),
                            float(P[:, 1].sum() / (truth == 1).sum()), float(P[:, 2].sum() / (truth == 2).sum()),
                            float(P[(truth != 0) & (ys.kag <= 30).to_numpy(), 0].mean()),
                            float(P[(truth != 0) & (ys.em > 1).to_numpy(), 0].sum() / (truth == 0).sum())))
    syn[sc] = {nm: np.mean(v, 0) for nm, v in acc.items()}
for r in rows:
    for sc in syn:
        v = syn[sc][r["model"]]
        r.update({f"5 synthetic, {sc}: right": v[0], f"5 synthetic, {sc}: Brier": v[1], f"5 synthetic, {sc}: interface total / true": v[2],
                  f"5 synthetic, {sc}: in-slab total / true": v[3], f"5 synthetic, {sc}: crustal total / true": v[4],
                  f"5 synthetic, {sc}: interface score of thrust-like non-interface events": v[5],
                  f"5 synthetic, {sc}: interface weight on non-interface events outside the ellipse / true interface": v[6]})
t = pd.DataFrame(rows).set_index("model").T
t.to_csv(X.TAB / "x5_diagnostics.csv")
print(t.round(3).to_string())

# confusion against Riedel-Hornig, per model (summed scores by their class)
q = np.isfinite(rc)
cf = pd.concat({nm: pd.DataFrame(P[q], columns=CL).groupby(np.array(CL)[rc[q].astype(int)]).sum().assign(events=pd.Series(np.array(CL)[rc[q].astype(int)]).value_counts())
                for nm, P in S.items()}).round(1)
cf.to_csv(X.TAB / "x5_riedel_confusion.csv")
print(cf.to_string())

# reliability (test 4): depth-only interface score against the mechanism, and full score against Riedel-Hornig
rel = []
for nm in S:
    for tag, p, o in (("mechanism hidden, against thrust-like", S0[nm][hm, 0], thr[hm].astype(float)), ("against Riedel-Hornig interface", S[nm][q, 0], (rc[q] == 0).astype(float))):
        b = np.digitize(p, [0.2, 0.4, 0.6, 0.8])
        for i, lab in enumerate(["0–0.2", "0.2–0.4", "0.4–0.6", "0.6–0.8", "0.8–1"]):
            k = b == i
            rel.append({"model": nm, "test": tag, "score": lab, "events": int(k.sum()), "mean score": p[k].mean() if k.any() else np.nan,
                        "observed share": o[k].mean() if k.any() else np.nan})
rel = pd.DataFrame(rel).round(3)
rel.to_csv(X.TAB / "x5_reliability.csv", index=False)
print(rel[rel.test.str.startswith("against")].pivot(index="score", columns="model", values=["events", "observed share"]).to_string())

# literature and far thrusts, event by event
q = np.isfinite(hint)
lit = x[q][["time", "mw", "z", "sig", "d", "kag", "hint", "r_cls", "r_z"]].round(1)
far = hm & thr & (np.abs(d) > 20)
ft = x[far][["time", "mw", "z", "sig", "depth_src", "top", "d", "kag", "hint", "r_cls", "r_z"]].round(1)
buf = hm & ~ell & (np.abs(d) <= 15)
bt = x[buf][["time", "lat", "lon", "mw", "z", "sig", "depth_src", "top", "d", "kag", "sw", "tw", "em", "hint", "r_cls", "r_z"]].round(2)
for nm, P in S.items():
    lit[nm.split()[0]] = [" / ".join(f"{v:.2f}" for v in p) for p in P[q]]
    ft[nm.split()[0]] = P[far, 0].round(2)
    bt[nm.split()[0]] = P[buf, 0].round(2)
lit.to_csv(X.TAB / "x5_literature.csv", index=False)
ft.sort_values("mw", ascending=False).to_csv(X.TAB / "x5_thrust_far.csv", index=False)
bt = bt.join(c.loc[bt.index, ["strike1", "dip1", "rake1"]]).sort_values("mw", ascending=False)
bt.to_csv(X.TAB / "x5_buffer_other.csv", index=False)
print("outside the ellipse, within 15 km of the slab:", int(buf.sum()))
print(bt.head(25).to_string())
print("thrust-like > 20 km from the slab:", int(far.sum()), "| with a Riedel-Hornig class:", ft.r_cls.value_counts().to_dict())
print(ft[ft.r_cls.notna()].to_string())

# where the events sit in the Riedel-Hornig depths, by mechanism
q = np.isfinite(rc)
kind = np.where(~hm, "no mechanism", np.where(thr, "thrust-like", "other mechanism"))
pos = pd.crosstab(pd.cut(d_r[q], [-80, -15, -5, 0, 5, 10, 15, 25, 120]), [kind[q], np.array(CL)[rc[q].astype(int)]])
pos.to_csv(X.TAB / "x5_riedel_position.csv")
print(pos.to_string())
rs0 = lambda v: 1.4826 * np.median(np.abs(v - np.median(v)))
for nm_, k_ in (("thrust-like", q & hm & thr), ("other mechanism", q & hm & ~thr), ("no mechanism", q & ~hm)):
    print(nm_, int(k_.sum()), "| Riedel-Hornig depth − slab: median", round(float(np.median(d_r[k_])), 1), "scatter", round(float(rs0(d_r[k_])), 1),
          "| our depth − slab: median", round(float(np.median(d[k_])), 1), "scatter", round(float(rs0(d[k_])), 1))

# depth check against Riedel-Hornig
rs = lambda v: 1.4826 * np.median(np.abs(v - np.median(v)))
y = g[X.m45(g) & g.known.to_numpy() & g.r_z.notna().to_numpy()]
y = y.assign(dz=y.z - y.r_z, shallow=np.where(y.top <= 50, "slab top ≤ 50 km", "deeper or no slab"))
dp = y.groupby(["shallow", "depth_src"]).agg(events=("dz", "size"), median=("dz", "median"), scatter=("dz", rs), our_sigma=("sig", "median"),
                                             their_sigma=("r_sig", "median")).round(1)
dp = dp[dp.events >= 10]
dp.to_csv(X.TAB / "x5_riedel_depths.csv")
print(dp.to_string())
print("mixture:", m.mu.round(1), m.s.round(1), m.pi.round(3))
