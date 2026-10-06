# Where the classified in-slab events sit inside the plate: depth below the
# Slab2 top (dz) and as a fraction of the Slab2 thickness (dz / thk), per
# class and latitude band. Same geometry and nearest-node lookup as the
# catalog classifier. The quantiles are the basis for the hypocentral depth
# distribution and the lower seismogenic depth of s03.
# Outputs: outputs/intraslab/ref/check/depth_profile.csv, figures/depth_profile.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cat, cfg, smooth
from intraslab import config

# settings
CLASSES = ["intra_slab", "slab_deep"]
LAT_BANDS = [(-26.0, -17.0, "north"), (-36.0, -26.0, "centre"), (-47.0, -36.0, "south")]
MMIN = 4.5                          # events used, M >= MMIN
MAXDIST_KM = 15.0                   # slab node within this distance of the epicentre (classifier value)
Q = [0.05, 0.25, 0.5, 0.75, 0.95]
DZ_BINS = np.arange(-20.0, 81.0, 5.0)


def main():
    c = cfg.load(config)
    od, fd = c.OUT / "check", c.OUT / "figures"
    od.mkdir(parents=True, exist_ok=True)
    fd.mkdir(parents=True, exist_ok=True)
    ev = cat.load(c.CAT, cls=CLASSES, bbox=c.BBOX)
    ev = ev[ev["mag"] >= MMIN].reset_index(drop=True)
    lon, lat = ev["longitude"].to_numpy(), ev["latitude"].to_numpy()
    top, d = smooth.slab_top(lon, lat, c.SLAB_XYZ)
    thk, _ = smooth.slab_node(lon, lat, c.SLAB_THK)
    ok = d <= MAXDIST_KM
    ev = ev[ok].assign(top=top[ok], thk=thk[ok])
    ev["dz"] = ev["depth"] - ev["top"]
    ev["fz"] = ev["dz"] / ev["thk"]
    ev["band"] = pd.cut(ev["latitude"], [b[0] for b in LAT_BANDS[::-1]] + [LAT_BANDS[0][1]],
                        labels=[b[2] for b in LAT_BANDS[::-1]])
    print(f"{len(ev)} events M>={MMIN} of {CLASSES} with a slab node within {MAXDIST_KM:g} km")

    rows = []
    for (k, b), g in ev.groupby(["class", "band"], observed=True):
        r = {"class": k, "band": b, "n": len(g), "thk_med": g["thk"].median()}
        r.update({f"dz_q{int(100 * q):02d}": g["dz"].quantile(q) for q in Q})
        r.update({f"fz_q{int(100 * q):02d}": g["fz"].quantile(q) for q in Q})
        rows.append(r)
    for k, g in ev.groupby("class"):
        r = {"class": k, "band": "all", "n": len(g), "thk_med": g["thk"].median()}
        r.update({f"dz_q{int(100 * q):02d}": g["dz"].quantile(q) for q in Q})
        r.update({f"fz_q{int(100 * q):02d}": g["fz"].quantile(q) for q in Q})
        rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(od / "depth_profile.csv", index=False)
    print(t.round(2).to_string(index=False))

    # figure: dz histograms per class and band, and dz against latitude
    f, axs = plt.subplots(1, len(CLASSES) + 1, figsize=(4.2 * (len(CLASSES) + 1), 4.2))
    for ax, k in zip(axs, CLASSES):
        for i, (_, _, b) in enumerate(LAT_BANDS):
            g = ev[(ev["class"] == k) & (ev["band"] == b)]
            if len(g):
                ax.hist(g["dz"], DZ_BINS, histtype="step", lw=1.6, color=f"C{i}", density=True,
                        label=f"{b}, n {len(g)}")
        ax.axvline(0, color="k", lw=0.7)
        ax.axvline(7.5, color="0.5", lw=0.8, ls=":")
        ax.set_xlabel("depth below Slab2 top km")
        ax.set_title(k, fontsize=9)
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("density")
    for i, k in enumerate(CLASSES):
        g = ev[ev["class"] == k]
        axs[-1].scatter(g["latitude"], g["dz"], s=2, alpha=0.4, color=f"C{i + 3}", label=k)
    axs[-1].axhline(0, color="k", lw=0.7)
    axs[-1].set_xlabel("latitude")
    axs[-1].set_ylabel("depth below Slab2 top km")
    axs[-1].invert_yaxis()
    axs[-1].legend(fontsize=7, markerscale=4)
    axs[-1].grid(alpha=0.3)
    f.suptitle(f"in-slab events M>={MMIN} relative to the Slab2 top; dotted = current offset 7.5 km", fontsize=10)
    f.tight_layout()
    f.savefig(fd / "depth_profile.png", dpi=300)
    plt.close(f)
    print(f"\nwrote {od / 'depth_profile.csv'} and {fd / 'depth_profile.png'}")


if __name__ == "__main__":
    main()