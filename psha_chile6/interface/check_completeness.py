# Completeness ensemble. Every approved completeness table (interface; in-slab
# intra_slab and slab_deep) is perturbed: the Mc of every step shifted by
# DM_SHIFTS and the start year of every step but the oldest by YR_SHIFTS. Each
# table is refitted (Weichert, same floor, same declustered catalog as the
# reference) and the (b, N(>=M_REF)) cloud is compared with the reference fit
# and its +/- 1 sigma_b. The two tables at the ends of the cloud (lowest and
# highest N(>=M_REF), the magnitude that controls the hazard) are written to
# outputs/completeness/<model>.json; variants mc_lo and mc_hi read them.
# Run before hazard/run_all.sh (run_report.sh does).
# Outputs: outputs/completeness/{interface,intraslab}.json, ensemble.csv, ensemble.png

import itertools
import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
import run
from lib import cat, gr
from variants import VARIANTS

# settings
DM_SHIFTS = [-0.2, -0.1, 0.0, 0.1, 0.2]
YR_SHIFTS = [-5, 0, 5]
M_REF = {"interface": 8.0, "intra_slab": 7.0, "slab_deep": 7.0}
N_BOOT = 100                 # bootstrap resamples for sigma_b
OUT = paths.OUT / "completeness"


def shift(steps, dm, dy):
    """Completeness table with every Mc shifted by dm and every start year but the oldest by dy."""
    y0 = min(y for _, y in steps)
    return [(round(m + dm, 2), y if y == y0 else y + dy) for m, y in steps]


def fit_interface(c, steps):
    from interface.s03_ab import load_dc, t_end
    df, te = load_dc(c), t_end(c)
    comp = df[gr.complete(df, steps)]
    w = gr.weichert(comp["mag"], steps, te, c.MMIN_FIT, c.DM, N_BOOT)
    return w


def fit_inslab(c, k, steps):
    te = c.T_END or json.loads((c.OUT / "decluster" / "input.json").read_text())["t_end"]
    s = cat.load(c.OUT / "decluster" / f"cat_dc_{k}_{c.DC_METHOD}.csv", bbox=c.BBOX)
    comp = s[gr.complete(s, steps)]
    floor = c.MMIN_FIT_BY_CLASS.get(k, c.MMIN_FIT)
    return gr.weichert(comp["mag"], steps, te, max(floor, min(x[0] for x in steps)), c.DM, N_BOOT)


def ensemble(name, ref_steps, fitter, m_ref):
    rows = []
    for dm, dy in itertools.product(DM_SHIFTS, YR_SHIFTS):
        st = shift(ref_steps, dm, dy)
        w = fitter(st)
        if not np.isfinite(w["b"]):
            continue
        n = w["rate"] * 10 ** (-w["b"] * (m_ref - w["mmin"]))
        rows.append({"set": name, "dm": dm, "dy": dy, "b": w["b"], "b_err": w["b_err"], "n_fit": w["n"],
                     "a": np.log10(w["rate"]) + w["b"] * w["mmin"], f"N{m_ref}": n, "steps": json.dumps(st)})
    t = pd.DataFrame(rows)
    ref = t[(t["dm"] == 0) & (t["dy"] == 0)].iloc[0]
    col = f"N{m_ref}"
    lo, hi = t.loc[t[col].idxmin()], t.loc[t[col].idxmax()]
    print(f"{name}: b {ref['b']:.3f} +/- {ref['b_err']:.3f}, N(>={m_ref}) {ref[col]:.4f}/yr; ensemble b "
          f"{t['b'].min():.3f}-{t['b'].max():.3f}, N {t[col].min():.4f}-{t[col].max():.4f} "
          f"(x{t[col].min() / ref[col]:.2f} to x{t[col].max() / ref[col]:.2f})")
    return t, ref, json.loads(lo["steps"]), json.loads(hi["steps"])


def plot(ax, t, ref, m_ref, title):
    col = f"N{m_ref}"
    sc = ax.scatter(t["b"], t[col], c=t["dm"], cmap="coolwarm", s=18 + 10 * (t["dy"] - t["dy"].min()),
                    edgecolor="k", lw=0.3)
    ax.errorbar(ref["b"], ref[col], xerr=ref["b_err"], fmt="k*", ms=12, capsize=3, label="reference +/- sigma_b")
    ax.set_yscale("log")
    ax.set_xlabel("b")
    ax.set_ylabel(f"N(>={m_ref}) per yr")
    ax.set_title(title, fontsize=9)
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=7)
    return sc


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ci = run.build("interface", VARIANTS["interface"]["mmin55"])
    t, ref, lo, hi = ensemble("interface", ci.COMPLETENESS, lambda st: fit_interface(ci, st), M_REF["interface"])
    (OUT / "interface.json").write_text(json.dumps({"lo": lo, "hi": hi, "ref": ci.COMPLETENESS}))
    tabs = {"interface": (t, ref, M_REF["interface"])}

    cs = run.build("intraslab", VARIANTS["intraslab"]["ref"])
    picks = {"lo": dict(cs.COMPLETENESS), "hi": dict(cs.COMPLETENESS)}
    for k in ("intra_slab", "slab_deep"):
        t, ref, lo, hi = ensemble(k, cs.COMPLETENESS[k], lambda st, k=k: fit_inslab(cs, k, st), M_REF[k])
        picks["lo"][k], picks["hi"][k] = lo, hi
        tabs[k] = (t, ref, M_REF[k])
    picks["ref"] = cs.COMPLETENESS
    (OUT / "intraslab.json").write_text(json.dumps(picks))

    pd.concat([x[0] for x in tabs.values()], ignore_index=True).to_csv(OUT / "ensemble.csv", index=False)
    f, axs = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, (k, (t, ref, m)) in zip(axs, tabs.items()):
        sc = plot(ax, t, ref, m, k)
    f.colorbar(sc, ax=axs, label="Mc shift", shrink=0.8)
    f.suptitle(f"completeness ensemble: Mc {DM_SHIFTS[0]:+g} to {DM_SHIFTS[-1]:+g}, start years "
               f"{YR_SHIFTS[0]:+d} to {YR_SHIFTS[-1]:+d} (marker size)", fontsize=10)
    f.savefig(OUT / "ensemble.png", dpi=300, bbox_inches="tight")
    plt.close(f)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
