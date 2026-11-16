"""Rupture-set comparison (S3, 16 Nov): strict UCERF3 scenarios of the Liquine-Ofqui faults of database A per depth,
jump distance and main-only / all traces. Writes tables/rupset_compare_<DATE>.csv and tables/rupsets_A_<DATE>.pkl."""
import pickle, time
import numpy as np, pandas as pd, geopandas as gpd
import faults as F, multifault as MF, rupset as R
gpd.options.io_engine = "fiona"
s, _, _ = F.load("A")
sysn = gpd.read_file(F.DBS["A"]["file"]).set_index("fid")["system"]
sl = s[s.fid.map(sysn).eq(MF.LOFS).to_numpy()].reset_index(drop=True)
rows, keep = [], {}
for z in (10.0, 20.0):
    for jk in (5.0, 10.0, 15.0):
        for tag, mo in (("main", True), ("all", False)):
            R.JUMP_KM = jk
            t0 = time.time()
            rups, sub = R.ruptures(sl, z, main_only=mo)
            sm = R.summary(sl, rups, sub, z)
            sc = R.scenarios(rups)
            W = z / np.sin(np.radians(sl.dip.to_numpy()))
            A = np.array([float((sl.L.to_numpy()[list(r["faults"])] * W[list(r["faults"])]).sum()) for r in sc]) if sc else np.array([])
            mw = np.array([F.R.on_grid(F.R.leonard(a, 180.0)) for a in A]) if sc else np.array([])
            cap = F.CLASS_MMAX["arc"]
            rows.append(dict(depth=z, jump=jk, traces=tag, **{k: v for k, v in sm.items() if k != "depth"},
                             mmax=float(mw.max()) if sc else np.nan, above_cap=int((mw > cap + 1e-9).sum()) if sc else 0,
                             scen_over_cap_km=float(sl.L.to_numpy()[list(sc[int(np.argmax(A))]["faults"])].sum()) if sc and (mw > cap).any() else 0.0,
                             seconds=round(time.time() - t0, 1)))
            keep[(z, jk, tag)] = dict(sub=sub, sc=sc, mw=mw, rups=rups)
            print(rows[-1], flush=True)
t = pd.DataFrame(rows)
t.to_csv("/data/PyCharmProjects/psha_chile/psha_chile8/model/crustal/tables/rupset_compare_2026-11-16e.csv", index=False)
pickle.dump(dict(sl=sl, keep=keep), open("/data/PyCharmProjects/psha_chile/psha_chile8/model/crustal/tables/rupsets_A_2026-11-16e.pkl", "wb"))
