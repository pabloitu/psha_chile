# Report of a classification change: the previous catalog.csv against the new
# one (same events, same magnitudes). Prints the moved events by rule and
# magnitude, the M >= 6.5 movers, the family and class counts before and after,
# the crustal events deeper than CRUSTAL_MAX_Z kept by hand (remark, override),
# and draws sections through the given latitude bands with the moved events
# ringed (their old class annotated).
# usage: python -m cat_handler_2.tools.reclass_report old_catalog.csv [new_catalog.csv] [lat_bands]
#   lat_bands e.g. "-18,-24;-28,-33" (default: those two)

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

from cat_handler_2 import check as K
from cat_handler_2 import config as C

OUT = C.OUT / "check"
KEY = ["id", "time_iso", "mag", "latitude", "longitude", "depth", "depth_status"]


def main(old_path, new_path=None, bands="-18,-24;-28,-33"):
    OUT.mkdir(parents=True, exist_ok=True)
    o = pd.read_csv(old_path, dtype={"id": str}, low_memory=False)
    n = pd.read_csv(new_path or C.OUT / "catalog.csv", dtype={"id": str}, low_memory=False)
    fam = {c: f for f, cs in C.FAMILIES.items() for c in cs}
    for d in (o, n):
        d["family"] = d["class"].map(fam).fillna("excluded")
    j = n.merge(o[["id", "class", "cls_rule", "family"]], on="id", suffixes=("", "_old"), how="left")
    j["z"] = pd.to_numeric(j["depth"], errors="coerce")
    known = ~j["depth_status"].isin(C.UNKNOWN_DEPTH) & j["z"].notna()
    j["why"] = np.where(known & (j["z"] > C.CRUSTAL_MAX_Z), f"real depth > {C.CRUSTAL_MAX_Z:.0f} km",
                        np.where(~known, "unknown depth", "other"))
    mv = j[j["class"] != j["class_old"]]
    t = [f"# reclassification: {old_path} -> {new_path or C.OUT / 'catalog.csv'}",
         f"events {len(n)} (old {len(o)}, in both {j['class_old'].notna().sum()}); class changed: {len(mv)}", ""]
    t += ["## moved events, old class -> new class (all / M >= 5.5 / M >= 7), by cause"]
    for why, s in mv.groupby("why"):
        t.append(f"### {why}: {len(s)}")
        g = s.groupby(["class_old", "class"]).agg(n=("id", "size"), n55=("mag", lambda m: int((m >= 5.5).sum())),
                                                 n7=("mag", lambda m: int((m >= 7).sum())), rules=("cls_rule", lambda r: ", ".join(f"{k} {v}" for k, v in r.value_counts().items())))
        t += [g.sort_values("n", ascending=False).to_string(), ""]
    big = mv[mv["mag"] >= 6.5].sort_values("mag", ascending=False)
    t += ["## M >= 6.5 events that changed class",
          big[KEY + ["slab_top", "class_old", "class", "cls_rule", "why"]].to_string(index=False), ""]
    for m0 in (5.5, 7.0):
        a, b = o[o["mag"] >= m0], n[n["mag"] >= m0]
        cf = pd.concat([a["family"].value_counts().rename("old"), b["family"].value_counts().rename("new")], axis=1).fillna(0).astype(int)
        cc = pd.concat([a["class"].value_counts().rename("old"), b["class"].value_counts().rename("new")], axis=1).fillna(0).astype(int)
        t += [f"## counts at M >= {m0}: families", cf.to_string(), "", f"## counts at M >= {m0}: classes", cc.to_string(), ""]
    ex = j[(j["family"] == "crustal") & known & (j["z"] > C.CRUSTAL_MAX_Z)]
    t += [f"## crustal events deeper than {C.CRUSTAL_MAX_Z:.0f} km kept by hand ({len(ex)}): remark = Cabello 'Crustal', override = class_overrides.csv",
          ex[KEY + ["slab_top", "class", "cls_rule", "general_remarks"]].sort_values("depth", ascending=False).to_string(index=False), ""]
    (OUT / "reclass.txt").write_text("\n".join(t) + "\n")
    mv[KEY + ["slab_top", "class_old", "cls_rule_old", "class", "cls_rule", "why"]].sort_values("mag", ascending=False).to_csv(
        OUT / "reclass_moved.csv", index=False)
    print("\n".join(t))

    ts = [tt for tt in K.transects() if any(lo >= tt["lat0"] >= hi for lo, hi in
                                           (sorted(map(float, b.split(",")), reverse=True) for b in bands.split(";")))]
    old_cls = dict(zip(mv["id"], mv["class_old"]))
    with PdfPages(OUT / "reclass_sections.pdf") as pdf:
        for tt in ts:
            x, y = K.proj(tt, n["longitude"].to_numpy(), n["latitude"].to_numpy())
            x0, x1 = C.SECTION_X[tt["fam"]]
            m = (np.abs(y) <= tt["half"]) & (x >= x0) & (x <= x1) & (n["mag"].to_numpy() >= 5.5)
            e = n[m].assign(x=x[m])
            fig, a = plt.subplots(figsize=(15, 7))
            sl, _ = K.K.slab()
            sx, sy = K.proj(tt, sl["lon"].to_numpy(), sl["lat"].to_numpy())
            sm = (np.abs(sy) <= tt["half"]) & (sx >= x0) & (sx <= x1)
            if sm.any():
                gg = sl[sm].assign(x=sx[sm]).groupby(pd.cut(sx[sm], np.arange(x0, x1 + 10, 10)), observed=True).agg(
                    x=("x", "median"), top=("dep", "median"), thk=("thk", "median"))
                a.fill_between(gg["x"], gg["top"], gg["top"] + gg["thk"], color="0.5", alpha=0.2, lw=0, label="plate")
                a.plot(gg["x"], gg["top"], "k-", lw=1)
            a.axhline(C.CRUSTAL_MAX_Z, color="tab:brown", lw=0.8, ls=":", label=f"CRUSTAL_MAX_Z {C.CRUSTAL_MAX_Z:.0f} km")
            unk = e["depth_status"].isin(C.UNKNOWN_DEPTH).to_numpy()
            for c, (col, zo) in K.STYLE.items():
                kk = (e["class"] == c).to_numpy()
                if kk.any():
                    a.scatter(e["x"][kk & ~unk], e["depth"][kk & ~unk], s=14 * (e["mag"][kk & ~unk] - 4.5) ** 2, c=col, alpha=0.7, lw=0, label=f"{c} ({kk.sum()})")
                    a.scatter(e["x"][kk & unk], e["depth"][kk & unk], s=14 * (e["mag"][kk & unk] - 4.5) ** 2, facecolors="none", edgecolors=col, lw=0.8)
            mm = e["id"].isin(old_cls).to_numpy()
            a.scatter(e["x"][mm], e["depth"][mm], s=90, facecolors="none", edgecolors="k", lw=1.2, label=f"class changed ({mm.sum()})")
            for _, r in e[mm].iterrows():
                a.annotate(f"{r['time_iso'][:4]} M{r['mag']:.1f}\\n{old_cls[r['id']]} -> {r['class']}", (r["x"], r["depth"]), fontsize=6,
                           xytext=(4, 4), textcoords="offset points")
            a.set(xlim=(x0, x1), ylim=(300, -5), xlabel="km from the trench", ylabel="depth (km)",
                  title=f"{tt['label']}: {tt['fam']} trench at {tt['lat0']:.1f} deg, M >= 5.5; hollow: depth unknown; ringed: class changed")
            a.legend(fontsize=7, ncol=4, loc="lower left")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
    print(f"-> {OUT / 'reclass.txt'}, reclass_moved.csv, reclass_sections.pdf ({len(ts)} pages)")


if __name__ == "__main__":
    main(*sys.argv[1:4])