# Family trees f_if_tree, f_is_tree and f_cr_tree (when it has run): mean and 16 / 50 / 84 % curves at the 14 cities,
# and their combination (exact enumeration, hazard/combine.py); without f_cr_tree marked "without the crustal family".
# Outputs in hazard/out/trees/: curves.csv, pga475.csv, curves.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pituplots.style.axes import darkgrid

import palette
from hazard import combine, post
from hazard import config as hc
from hazard import jobs as J

OUT = hc.OUT / "trees"
IMT = "PGA"
POE = 0.002105
Q = (0.16, 0.5, 0.84)
JOBS = {"interface": "f_if_tree", "in-slab": "f_is_tree", "crustal": "f_cr_tree"}
COL = {"interface": palette.CLASS_COLOR["interface"], "in-slab": palette.CLASS_COLOR["intraslab_intermediate"],
       "crustal": palette.CLASS_COLOR["forearc"], "all": "0.15"}


def load(job):
    """A tree job, or the mixture of its parts (jobs.TREE_PARTS): realizations pooled, weights times the part weight."""
    if job not in J.TREE_PARTS:
        return post.load(job)
    rs = [post.load(p) for p in J.TREE_PARTS[job]]
    w = np.concatenate([r["w"] * J.JOBS[p]["part"] for r, p in zip(rs, J.TREE_PARTS[job])])
    return {**rs[0], "curves": np.concatenate([r["curves"] for r in rs], axis=1), "w": w / w.sum(),
            "calc_id": "+".join(str(r["calc_id"]) for r in rs)}


def stats():
    """Mean and quantile curves (sites, levels) per family and combined; returns (dict, levels, calc info)."""
    parts, out, info = [], {}, {}
    for k, j in JOBS.items():
        try:
            r = load(j)
        except (SystemExit, FileNotFoundError) as e:
            print(f"[skip] {k}: {e}")
            continue
        m = list(r["imtls"]).index(IMT)
        c = r["curves"][:, :, m, :]
        lv = r["imtls"][IMT]
        q = np.array([post.wquant(c[s], r["w"], Q) for s in range(c.shape[0])]).transpose(1, 0, 2)
        out[k] = {"mean": np.einsum("r,srl->sl", r["w"], c), **{f"q{100 * x:g}": q[i] for i, x in enumerate(Q)}}
        parts.append((r["curves"][:, :, [m], :], r["w"]))
        info[k] = (r["calc_id"], len(r["w"]))
    fams = list(out)
    for n in sorted({2, len(parts)}):
        ex = combine.quantiles(parts[:n], Q)
        out[" + ".join(fams[:n])] = {"mean": combine.mean(parts[:n])[:, 0],
                                     **{f"q{100 * x:g}": ex[i, :, 0] for i, x in enumerate(Q)}}
    return out, lv, info


def main():
    palette.apply()
    OUT.mkdir(parents=True, exist_ok=True)
    st, lv, info = stats()
    both = list(st)[-1]
    two = "interface + in-slab"
    note = "" if "crustal" in st else "without the crustal family"
    rows, tab = [], []
    for k, d in st.items():
        for s, name in enumerate(hc.CITIES):
            for j, l in enumerate(lv):
                rows.append({"model": k, "site": name, "iml": l, **{c: v[s, j] for c, v in d.items()}})
            tab.append({"model": k, "site": name, **{c: post.iml(v[s], lv, POE) for c, v in d.items()}})
    pd.DataFrame(rows).to_csv(OUT / "curves.csv", index=False)
    t = pd.DataFrame(tab)
    t.to_csv(OUT / "pga475.csv", index=False, float_format="%.4f")
    w = t.pivot(index="site", columns="model", values="mean").reindex(list(hc.CITIES))
    print(f"PGA 475 yr (g), mean of the family trees{', ' + note if note else ''}; calcs {info}")
    print(w.round(3).to_string())

    fig, axs = plt.subplots(4, 4, figsize=(16, 15), sharex=True, sharey=True, layout="constrained")
    for ax, (s, name) in zip(axs.flat, enumerate(hc.CITIES)):
        for k, d in st.items():
            if k == two and two != both:
                ax.plot(lv, d["mean"][s], color=COL["all"], lw=1.2, ls="--", label=k)
                continue
            c = COL["all"] if k == both else COL[k]
            ax.fill_between(lv, d["q16"][s], d["q84"][s], color=c, alpha=0.18, lw=0)
            ax.plot(lv, d["mean"][s], color=c, lw=1.8, label=k)
        ax.axhline(POE, color="k", lw=0.7, ls="--")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(1e-2, 3)
        ax.set_ylim(1e-5, 1)
        darkgrid(ax)
        ax.text(0.97, 0.95, name, transform=ax.transAxes, ha="right", va="top", fontsize=12)
    for ax in axs.flat[len(hc.CITIES):]:
        ax.axis("off")
    for ax in axs[-1]:
        ax.set_xlabel(f"{IMT} (g)")
    for ax in axs[:, 0]:
        ax.set_ylabel("annual PoE")
    axs.flat[len(hc.CITIES)].legend(*axs.flat[0].get_legend_handles_labels(), loc="center", title=
                                    "mean and 16–84 %" + (f"\n{note}" if note else ""), frameon=False)
    fig.savefig(OUT / "curves.png", dpi=200, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
