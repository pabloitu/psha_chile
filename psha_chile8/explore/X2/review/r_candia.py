"""Our checks on the Candia and Macedo (2026) catalogue; run r_candia_read.py first."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[1] / "X1"))
import x2_eval as xe, x2_fit as xf, x1_stats as xs
pd.set_option("display.width", 220)
X2 = HERE.parent
c = pd.read_csv(X2 / "cache" / "candia_macedo.csv", low_memory=False)
c["tt"] = pd.to_datetime(c.time, utc=True, errors="coerce", format="ISO8601")
c = c[c.tt.notna() & (c.GK != 1)].copy()
c["yr"] = c.tt.dt.year + c.tt.dt.dayofyear / 366
c["t"] = (c.tt - pd.Timestamp("1900-01-01", tz="UTC")).dt.total_seconds()
c["cls"] = c.mech.map({"IF": "interface band", "SL": "in slab", "SC": "above slab, shallow"})
c = c.reset_index(drop=True)
# own catalogue, same box
L, W, R, a = xf.load()
F = json.load(open(X2 / "cache" / "fits_x2.json"))["inv-lin W"]
own = xf.build(F, W, R, a, L, "W", "wmean").mw.to_numpy()
box = lambda la, lo: (la <= -15) & (la >= -60) & (lo >= -80) & (lo <= -60)
ko = box(a.lat.to_numpy(), a.lon.to_numpy())
kc = box(c.lat.to_numpy(), c.lon.to_numpy())
sets = [("Candia-Macedo", np.where(kc, c.mw.to_numpy(float), np.nan), c),
        ("own INV-W linear mean", np.where(ko, own, np.nan), a)]
B, Lg, Rt = xe.stats(sets)
for v in ("Candia-Macedo", "own INV-W linear mean"):
    g = Lg[(Lg.variant == v) & (Lg.period == "1976–2026") & (Lg.fit_from == 5.0)]
    print(v, "\n", g[["declust", "family", "b_fit", "n_fit", "N7_pred", "N7_obs", "N6.5–7_pred", "N6.5–7_obs"]].round(2).to_string())
    b = B[(B.variant == v) & B.declust & (B.family == "all")].pivot_table(index="period", columns="floor", values="b")
    print(b.loc[:, 4.5:5.8].round(2).to_string())
print(Rt[Rt.declust].round(1).to_string())
# FMD per 0.1 in 1976-1999 and 2011-2026
for y0, y1 in ((1976, 2000), (2011, 2027)):
    for nm, mv, at in sets:
        k = (at.yr.to_numpy() >= y0) & (at.yr.to_numpy() < y1) & np.isfinite(mv)
        h = np.round(mv[k] / 0.1) * 0.1
        print(nm, y0, y1, {f"{q:.1f}": int((np.abs(h - q) < 1e-6).sum()) for q in np.arange(4.3, 6.05, 0.1)})
# event matching M>=4.8, 1976+
cc = c[kc & (c.yr >= 1976) & (c.mw >= 4.6)]
ao = a[ko & (a.yr >= 1976)].assign(mw=own[ko & (a.yr.to_numpy() >= 1976)])
ao = ao[ao.mw >= 4.3].sort_values("t")
ts = ao.t.to_numpy()
rows = []
for i, r in cc.iterrows():
    j0, j1 = np.searchsorted(ts, [r.t - 30, r.t + 30])
    if j1 <= j0:
        rows.append((i, np.nan, np.nan)); continue
    s = ao.iloc[j0:j1]
    d = 111.2 * np.hypot(s.lat - r.lat, (s.lon - r.lon) * np.cos(np.radians(r.lat)))
    k = d < 100
    if not k.any():
        rows.append((i, np.nan, np.nan)); continue
    q = s[k].iloc[np.argmin(np.abs(s[k].t - r.t))]
    rows.append((i, q.mw, q.name))
m = pd.DataFrame(rows, columns=["i", "own", "ev"]).set_index("i")
cc = cc.join(m)
print("matched", cc.own.notna().mean().round(3), "of", len(cc))
cc["d"] = cc.mw - cc.own
cc["src"] = cc.agency + " " + cc.magtype
for lo in (4.6, 5.0, 5.5, 6.0, 6.5, 7.0):
    k = (cc.mw >= lo) & (cc.mw < lo + 0.5)
    print(f"their Mw {lo}-{lo+.5}: median theirs-ours {cc.d[k].median():+.2f} n={k.sum()} unmatched {cc.own[k].isna().sum()}")
print(cc[(cc.mw >= 4.6) & (cc.mw < 5.5)].groupby("src").d.agg(["median", "count"]).query("count>=50").round(2).to_string())
dup = cc[cc.ev.notna()].groupby("ev").size()
print("our events matched by >1 retained C-M event (retained duplicates):", int((dup > 1).sum()))
x = cc[cc.ev.isin(dup[dup > 1].index) & (cc.mw >= 6)].sort_values("t")[["time", "agency", "magtype", "mw", "lat", "lon", "mech"]]
print(x.head(30).to_string())
