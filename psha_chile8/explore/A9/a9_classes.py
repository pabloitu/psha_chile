import numpy as np, pandas as pd
import classify as C

c = pd.read_csv("merged/catalog_2026-11-14c.csv", low_memory=False)
fz = pd.read_csv("merged/classes_2026-11-14c.csv")
o = pd.read_csv("overrides_A6.csv")
h = o[(o.status == "accepted") & (o.property == "class_hint")].set_index("event_id").new_value
c["a6_class_hint"] = c.event_id.map(h).where(c.event_id.isin(h.index), c.a6_class_hint)
g, out, tab = C.run(c)
print("hints", len(h), "| events changed by the hints:", (np.abs(out[C.COLS].to_numpy() - fz[C.COLS].to_numpy()).max(1) > 1e-9).sum())
yr = c.time.str[:4].astype(int).to_numpy()
nd = (out.rule == "nodepth_share") & (out.w_crustal > 0) & (out.w_crustal < 1)

def drop(t, k):
    t = t.copy()
    r = t.loc[k, ["w_interface", "w_inslab"]].sum(1)
    for q in ("w_interface", "w_inslab"):
        t.loc[k, q] = (t.loc[k, q] / r).round(4)
    t.loc[k, "w_crustal"], t.loc[k, "sub_crustal"] = 0.0, ""
    t.loc[k, "rule"] = "nodepth_share_pre1900"
    return t

k = (nd & (yr < 1900) & (g.top <= C.IF_TOP)).to_numpy()
new = drop(out, k)
new["cls"] = np.where(k, np.where(new[C.COLS].max(1) >= 1 - 1e-9, np.array(C.CLS)[new[C.COLS].to_numpy().argmax(1)], "split"), new.cls)
print("sum to 1:", np.abs(new[C.COLS].sum(1) - 1).max().round(5))
new[C.FIELDS].to_csv("merged/classes_2026-11-16_test.csv", index=False)
dom = c.in_domain.to_numpy()
def tab_(a, b, lab):
    print("\n" + lab)
    for m in (4.5, 6, 7):
        q = dom & (c.mw.to_numpy() >= m)
        d = (b[C.COLS[:3]].to_numpy() - a[C.COLS[:3]].to_numpy())[q].sum(0)
        ch = (np.abs(b[C.COLS].to_numpy() - a[C.COLS].to_numpy()).max(1) > 1e-9) & q
        cr = a.w_crustal[ch].groupby(a.sub_crustal[ch]).sum().round(2).to_dict()
        print(f"Mw >= {m}: events {ch.sum()}, interface {d[0]:+.2f}, in-slab {d[1]:+.2f}, crustal {d[2]:+.2f}  from {cr}")
tab_(fz, out.reset_index(drop=True), "frozen -> new hints")
tab_(out, new, "new hints -> pre-1900 rule (test file)")
tab_(fz, new.reset_index(drop=True), "frozen -> test file")
tab_(out, drop(out, nd.to_numpy()), "for comparison: option (b), every split no-depth event")
q = dom & (c.mw.to_numpy() >= 7) & (new.rule == "nodepth_share").to_numpy() & (new.w_crustal > 0).to_numpy()
print("\nleft, Mw >= 7 split no-depth with crustal share:", q.sum(), new.w_crustal[q].groupby(new.sub_crustal[q]).agg(["count", "sum"]).round(2).to_dict())
d = new[dom & (c.mw.to_numpy() >= 4.5)]
print("totals test:", d[C.COLS].sum().round(1).to_dict())
print(d.w_crustal.groupby(d.sub_crustal).sum().round(1).to_dict())
