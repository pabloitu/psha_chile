# b and rate per segment and full margin from the declustered catalog and
# the approved COMPLETENESS. Weichert and Kijko-Smit side by side.
# Outputs: ab/ab.json, ab/compare.csv, ab/decluster_sensitivity.csv,
#          ab/b_stability.csv, figures/s03_b_stability.png, figures/s03_mfd.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cat, cfg, gr
from interface import config


def load_dc(c, method=None):
    df = cat.load(c.OUT / "decluster" / f"cat_dc_{method or c.DC_METHOD}.csv")
    df = df[df["latitude"].between(c.SEG_BOUNDS[0], c.SEG_BOUNDS[-1])].copy()
    df["seg"] = pd.cut(df["latitude"], bins=c.SEG_BOUNDS, labels=c.SEG_IDS, right=False)
    return df.reset_index(drop=True)


def t_end(c):
    if c.T_END:
        return float(c.T_END)
    return json.loads((c.OUT / "decluster" / "input.json").read_text())["years"][1]


def subsets(df, c):
    yield c.FULL_ID, df
    for s in c.SEG_IDS:
        yield s, df[df["seg"] == s]


def fit(sub, c, te, floor=None, nboot=0):
    """Weichert and Kijko-Smit on the complete part of one subset."""
    floor = c.MMIN_FIT if floor is None else floor
    comp = sub[gr.complete(sub, c.COMPLETENESS)]
    w = gr.weichert(comp["mag"], c.COMPLETENESS, te, floor, c.DM, nboot)
    bk, rk = gr.kijko_smit(comp, c.COMPLETENESS, te, floor, c.DM)
    r = {"n": w["n"], "mmax_obs": float(sub["mag"].max()),
         "weichert": {"b": w["b"], "b_err": w["b_err"],
                      "rate_mmin": w["rate"] * 10 ** (-w["b"] * (c.MMIN_HAZ - floor))},
         "kijko_smit": {"b": bk, "b_err": np.nan,
                        "rate_mmin": rk * 10 ** (-bk * (c.MMIN_HAZ - floor))}}
    for e in ("weichert", "kijko_smit"):
        r[e]["a"] = np.log10(r[e]["rate_mmin"]) + r[e]["b"] * c.MMIN_HAZ
    return r, comp


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "ab"
    od.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)
    te = t_end(c)
    df = load_dc(c)
    print(f"{len(df)} mainshocks in span, t_end {te:.2f}, steps {c.COMPLETENESS}")

    res, rows, comps = {}, [], {}
    for sid, sub in subsets(df, c):
        r, comps[sid] = fit(sub, c, te, nboot=c.N_BOOT)
        res[sid] = r
        for e in ("weichert", "kijko_smit"):
            x = r[e]
            rows.append({"seg": sid, "est": e, "n": r["n"], "b": x["b"], "b_err": x["b_err"],
                         "a": x["a"], **{f"M{m}": x["rate_mmin"] * 10 ** (-x["b"] * (m - c.MMIN_HAZ))
                                         for m in c.REF_MAGS}})
        obs = gr.obs_cum(comps[sid], c.COMPLETENESS, te, np.array(c.REF_MAGS))
        rows.append({"seg": sid, "est": "observed", "n": r["n"],
                     **{f"M{m}": o for m, o in zip(c.REF_MAGS, obs)}})
        if r["weichert"]["b_err"] > c.B_ERR_WARN:
            print(f"[warn] {sid}: b_err {r['weichert']['b_err']:.3f}")
    tab = pd.DataFrame(rows)
    tab.round(5).to_csv(od / "compare.csv", index=False)
    print(tab.round(4).to_string(index=False))
    meta = {"dc_method": c.DC_METHOD, "estimator": c.AB_ESTIMATOR, "t_end": te,
            "mmin_fit": c.MMIN_FIT, "mmin_haz": c.MMIN_HAZ, "completeness": c.COMPLETENESS}
    (od / "ab.json").write_text(json.dumps({"meta": meta, "segments": res}, indent=1, default=float))

    sens = []
    for m in c.DC_METHODS:
        d = load_dc(c, m)
        for sid, sub in subsets(d, c):
            r, _ = fit(sub, c, te)
            w = r["weichert"]
            sens.append({"method": m, "seg": sid, "n": r["n"], "b": w["b"],
                         "M7.5": w["rate_mmin"] * 10 ** (-w["b"] * (7.5 - c.MMIN_HAZ))})
    sens = pd.DataFrame(sens)
    sens.round(5).to_csv(od / "decluster_sensitivity.csv", index=False)
    print(sens.pivot(index="seg", columns="method", values="b").round(3).to_string())

    floors = np.round(np.arange(min(s[0] for s in c.COMPLETENESS), c.MMIN_HAZ + 0.01, 0.1), 1)
    stab = []
    for sid, sub in subsets(df, c):
        for fl in floors:
            r, _ = fit(sub, c, te, fl)
            stab.append({"seg": sid, "floor": fl, "b_w": r["weichert"]["b"],
                         "b_ks": r["kijko_smit"]["b"]})
    stab = pd.DataFrame(stab)
    stab.round(4).to_csv(od / "b_stability.csv", index=False)
    f, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, col in zip(axs, ("b_w", "b_ks")):
        for sid, g in stab.groupby("seg", sort=False):
            ax.plot(g["floor"], g[col], "o-", ms=3, lw=2 if sid == c.FULL_ID else 1, label=sid)
        ax.axvline(c.MMIN_FIT, color="crimson", ls="--", lw=0.8)
        ax.set_xlabel("fit floor")
        ax.set_title("weichert" if col == "b_w" else "kijko_smit")
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("b")
    axs[0].legend(fontsize=7)
    f.tight_layout()
    f.savefig(c.FIG / "s03_b_stability.png", dpi=200)
    plt.close(f)

    ids = [c.FULL_ID] + c.SEG_IDS
    f, axs = plt.subplots(1, len(ids), figsize=(3.2 * len(ids), 4), sharey=True)
    for ax, sid in zip(axs, ids):
        g = np.arange(min(s[0] for s in c.COMPLETENESS), comps[sid]["mag"].max() + 0.05, 0.1)
        ax.semilogy(g, np.maximum(gr.obs_cum(comps[sid], c.COMPLETENESS, te, g), 1e-6), "k.", ms=4)
        for e, col in (("weichert", "C0"), ("kijko_smit", "C3")):
            x = res[sid][e]
            ax.semilogy(g, x["rate_mmin"] * 10 ** (-x["b"] * (g - c.MMIN_HAZ)), col,
                        label=f"{e} b={x['b']:.2f}")
        ax.axvline(c.MMIN_FIT, color="gray", lw=0.5, ls="--")
        ax.set_ylim(1e-5, 1e3)
        ax.set_title(f"{sid} (n={res[sid]['n']})", fontsize=9)
        ax.set_xlabel("M")
        ax.legend(fontsize=6)
    axs[0].set_ylabel("N(>=M)/yr")
    f.tight_layout()
    f.savefig(c.FIG / "s03_mfd.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s03")


if __name__ == "__main__":
    main()
