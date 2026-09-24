# Decluster the interface catalog with every DC_METHODS window.
# Outputs: decluster/cat_dc_{method}.csv, summary.csv, removed_large.csv,
#          input.json, figures/s01_decluster.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cat, cfg, dc
from interface import config


def main(c=None):
    c = c or cfg.load(config)
    od = c.OUT / "decluster"
    od.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)

    df = cat.load(c.CAT)
    fp = cat.fingerprint(c.CAT, df)
    (od / "input.json").write_text(json.dumps(fp, indent=1))
    print(json.dumps(fp))

    summ, revs, per_yr = [], [], {}
    yr = np.arange(c.DC_FROM_YEAR, int(df["year"].max()) + 2)
    for m in c.DC_METHODS:
        out, rev = dc.run(df, m, c.DC_FS, c.DC_FROM_YEAR, c.DC_KEEP_IDS, c.DC_MPROT)
        main_ = out[out["is_mainshock"]]
        main_.drop(columns=["year"]).to_csv(od / f"cat_dc_{m}.csv", index=False)
        revs.append(rev)
        summ.append({"method": m, "n_in": len(out), "n_main": len(main_),
                     "frac_removed": round(1 - len(main_) / len(out), 3),
                     "n_M7_main": int((main_["mag"] >= 7).sum()), "n_M7_removed": len(rev)})
        per_yr[m] = np.histogram(main_["year"], bins=yr)[0]
        if m == c.DC_METHOD and "id" in out.columns:
            for i, label in c.WATCH_IDS.items():
                hit = out[out["id"].astype(str) == str(i)]
                state = ("absent" if not len(hit) else
                         "kept" if hit["is_mainshock"].iloc[0] else "removed")
                print(f"[watch] {i} {label}: {state}")

    pd.DataFrame(summ).to_csv(od / "summary.csv", index=False)
    rev = pd.concat(revs, ignore_index=True)
    rev.to_csv(od / "removed_large.csv", index=False)
    print(pd.DataFrame(summ).to_string(index=False))
    if len(rev):
        print(rev[rev["method"] == c.DC_METHOD].to_string(index=False))

    n_in = np.histogram(df["year"], bins=yr)[0]
    f, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    a1.semilogy(yr[:-1], np.maximum(n_in, 0.5), "k", drawstyle="steps-post", label="input")
    for m in c.DC_METHODS:
        lw = 2 if m == c.DC_METHOD else 1
        a1.semilogy(yr[:-1], np.maximum(per_yr[m], 0.5), drawstyle="steps-post", lw=lw, label=m)
        a2.plot(yr[:-1], np.where(n_in > 0, 1 - per_yr[m] / np.maximum(n_in, 1), 0),
                drawstyle="steps-post", lw=lw)
    a1.legend(fontsize=8)
    a1.set_ylabel("events/yr")
    a2.set_ylabel("fraction removed")
    a2.set_xlabel("year")
    f.tight_layout()
    f.savefig(c.FIG / "s01_decluster.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s01", {"input": fp})


if __name__ == "__main__":
    main()
