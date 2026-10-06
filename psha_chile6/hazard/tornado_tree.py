# Tornado of the final logic tree, from the stored realizations of the family
# jobs (c_if_final, c_is_final, c_cr_final; PRELIM=1 or FINAL=1). For every branch
# axis and value the family's curve is replaced by the weighted mean over the
# realizations with that value; the families combine in rate space as in
# hazard/combine.py. Effect = PGA at the target PoE of that combination against the
# full-tree mean. Coupling is measured inside the geodetic half of the interface tree.
#   pt_axes.csv          site, family, axis, value, weight, iml, rel_pct
#   pt_bars.csv          lo, hi, range per site and axis; verdict: range >= 5 % at some city, GMM axes always
#   pt_tornado_<city>.png   bars per axis, one dot per value
#   pt_overview.png      largest |change| per axis and city
# Outputs: outputs/hazard/rock800_prelim/_tornado_tree/. Run: PRELIM=1 python hazard/tornado_tree.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
from hazard import config as hc
from hazard import post
from hazard.gmm_final import SHORT, stem

OUT = hc.OUT_ROOT / "_tornado_tree"
FAM = {"interface": "c_if_final", "in-slab": "c_is_final", "crustal": "c_cr_final"}
IMT = "PGA"
POE = 0.002105
MIN = 5.0
NAME = {"if:ab": "(a, b): 5th / ML / 95th", "if:catalog": "rate convention: full / declustered", "if:geometry": "geometry: full / segmented",
        "if:rate_type": "rate: seismic / geodetic", "if:coupling": "coupling (geodetic branches)",
        "gmm:sinter": "GMM interface", "gmm:sslab": "GMM in-slab", "gmm:asc": "GMM crustal",
        "cr:phi": "fault aseismic coefficient", "cr:mmax": "fault Mmax", "cr:mfd": "fault MFD"}
FVAL = {"phi060": "0.6", "phi080": "0.8", "phi100": "1.0", "mobs": "observed", "mwc": "WC94", "mleo": "Leonard",
        "al1": "AL-I", "al2": "AL-II", "al3": "AL-III", "yc": "YC", "tap": "tapered"}
VAL = {"geo_lo": "lo", "geo_mid": "mid", "geo_hi": "hi"}


def axes_of(k, r):
    """Axis table of a family: branch value per realization, with the derived interface axes."""
    ax = r["axes"].copy()
    if k == "interface" and "if:variant" in ax:
        v = ax["if:variant"]
        ax["if:catalog"] = np.where(v.str.endswith("_gk74") | (v == "c_rate_gk74"), "declustered", "full")
        ax["if:ab"] = v.str.replace("c_rate_gk74", "mmin55").str.replace("_gk74", "").map(
            {"c_ab_p05": "5th", "mmin55": "ML", "c_ab_p95": "95th"})
        ax = ax.drop(columns="if:variant")
    if k == "interface" and "if:rate" in ax:
        ax["if:rate_type"] = np.where(ax["if:rate"] == "seis", "seismic", "geodetic")
        ax["if:coupling"] = ax["if:rate"].str.replace("geo_", "", regex=False).where(ax["if:rate"] != "seis")
        ax = ax.drop(columns="if:rate")
    return ax[[c for c in ax.columns if ax[c].nunique() > 1]]


def main():
    post.set_style()
    OUT.mkdir(parents=True, exist_ok=True)
    fam = {k: post.load(j) for k, j in FAM.items()}
    names = fam["interface"]["names"]
    lv = fam["interface"]["imtls"][IMT]
    mi = {k: list(r["imtls"]).index(IMT) for k, r in fam.items()}
    mean = {k: np.einsum("r,srl->sl", r["w"], r["curves"][:, :, mi[k], :]) for k, r in fam.items()}
    rate = lambda p: -np.log(1 - np.clip(p, 0, 1 - 1e-12))
    rows = []
    for k, r in fam.items():
        ax = axes_of(k, r)
        others = sum(rate(mean[g]) for g in fam if g != k)
        c = r["curves"][:, :, mi[k], :]
        for col in ax.columns:
            base = ax["if:rate_type"].eq("geodetic").to_numpy() if col == "if:coupling" else np.ones(len(ax), bool)
            for v in ax[col].dropna().unique():
                m = (ax[col] == v).to_numpy() & base
                for s, name in enumerate(names):
                    x = post.iml(1 - np.exp(-(others[s] + rate(r["w"][m] @ c[s, m] / r["w"][m].sum()))), lv, POE)
                    x0 = post.iml(1 - np.exp(-(others[s] + rate(r["w"][base] @ c[s, base] / r["w"][base].sum()))), lv, POE)
                    lab = SHORT[stem(v)] if col.startswith("gmm:") else {**VAL, **FVAL}.get(v, v)
                    rows.append({"site": name, "family": k, "axis": NAME.get(col, col), "value": lab,
                                 "weight": r["w"][m].sum() / r["w"][base].sum(), "iml": x, "rel_pct": 100 * (x / x0 - 1)})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "pt_axes.csv", index=False)
    b = t.groupby(["site", "family", "axis"], sort=False)["rel_pct"].agg(lo="min", hi="max").reset_index()
    b["range"] = b["hi"] - b["lo"]
    b["amax"] = np.maximum(-b["lo"], b["hi"])
    b["verdict"] = np.where(b.groupby(["family", "axis"])["range"].transform("max") >= MIN, "branch", "could be fixed")
    b.loc[b["axis"].str.startswith("GMM"), "verdict"] = "branch (GMM)"
    b.to_csv(OUT / "pt_bars.csv", index=False)
    print(b.groupby(["family", "axis"], sort=False).agg(range_max=("range", "max"), amax=("amax", "max"),
                                                         city=("range", lambda x: b.loc[x.idxmax(), "site"]),
                                                         verdict=("verdict", "first")).round(1).to_string())

    col = paths.palette.FAMILY
    for name in names:
        g = b[b["site"] == name].sort_values("range")
        f, ax = plt.subplots(figsize=(16, 9))
        for i, (_, r) in enumerate(g.iterrows()):
            ax.barh(i, r["hi"] - r["lo"], left=r["lo"], height=0.55, color=col[r["family"]], alpha=0.75)
            q = t[(t["site"] == name) & (t["family"] == r["family"]) & (t["axis"] == r["axis"])]
            for x, h in q.groupby(q["rel_pct"].round(1)):
                ax.plot(h["rel_pct"].mean(), i, "o", color="k", ms=5)
                ax.annotate(", ".join(v.split()[0] for v in h["value"]), (h["rel_pct"].mean(), i), xytext=(0, 9),
                            textcoords="offset points", ha="center", fontsize=10)
        ax.set_xlim(min(g["lo"].min() * 1.2, -MIN) - 1, max(g["hi"].max() * 1.2, MIN) + 1)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvspan(-MIN, MIN, color="0.5", alpha=0.15, lw=0)
        ax.set_yticks(range(len(g)))
        ax.set_yticklabels(g["axis"], fontsize=12)
        ax.set_xlabel(f"Change of {IMT} 475 yr against the tree mean $[\\%]$", fontsize=14)
        ax.set_title(f"{name.replace('_', ' ').title()}: branch axes of the final tree", fontsize=16)
        ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.75) for c in (col["interface"], col["in-slab"], col["crustal"])],
                  labels=["interface", "in-slab", "crustal"], loc="lower right", frameon=True)
        f.savefig(OUT / f"pt_tornado_{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
        plt.close(f)

    m = b.pivot_table(index="axis", columns="site", values="amax").reindex(columns=names)
    m = m.loc[m.max(axis=1).sort_values(ascending=False).index]
    f, ax = plt.subplots(figsize=(16, 9))
    im = ax.imshow(m.to_numpy(), cmap="Reds", vmin=0, vmax=max(20.0, np.nanmax(m.to_numpy())), aspect="auto")
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.iat[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=11, color="white" if v > 15 else "black")
    ax.grid(False)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([n.replace("_", " ") for n in names], rotation=45, ha="right", fontsize=12)
    ax.set_yticks(range(len(m)))
    ax.set_yticklabels(m.index, fontsize=12)
    ax.set_title(f"Largest change of {IMT} 475 yr per branch axis $[\\%]$", fontsize=16)
    f.colorbar(im, ax=ax, shrink=0.7)
    f.savefig(OUT / "pt_overview.png", dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(f)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
