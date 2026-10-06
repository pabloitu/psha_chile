# In-slab smoothing, event by event, for one built variant (s02 must have run). Uses
# the same events, weights and kernel as s02 (kernel settings and b from
# ssm/classes.csv, so a cross-validated kernel is read as chosen):
#   the pattern weight per completeness step (with SMOOTH_EVENTS "complete" an event
#   weighs 10^(b (Mc of its step - fit floor)) / T of its step, whatever its own M);
#   bandwidth per latitude band; the events with the largest pattern weight;
#   where the rate of each latitude band comes from (source band -> receiving band,
#   % of the receiving band's rate); the events that feed the rate within R_KM of
#   each city. With "old" as second argument the psha_chile5 build of the same
#   variant is read instead (psha_chile5 is not written to).
# Outputs: outputs/intraslab/<tag>/check/kernel[_old]/*.csv, kernel_weights.png
#   python intraslab/kernel_check.py ref [old]

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paths
import run
from lib import cat, gr, smooth
from lib.dc import hav
from variants import VARIANTS
from hazard import config as hc
from intraslab.s02_ssm import domain, fit, pattern

# settings
VARIANT = "ref"
CLASSES = ["intra_slab", "slab_deep"]
BANDS = [-17.0, -24.0, -30.0, -36.0, -42.0, -47.0]
R_KM = 150.0
TOP = 8


def main(variant=VARIANT, tree="new"):
    c = run.config("intraslab", VARIANTS["intraslab"][variant])
    src = paths.PREV / "outputs" / "intraslab" / c.TAG if tree == "old" else c.OUT
    od = c.OUT / "check" / ("kernel_old" if tree == "old" else "kernel")
    od.mkdir(parents=True, exist_ok=True)
    te = c.T_END or json.loads((src / "decluster" / "input.json").read_text())["t_end"]
    info = pd.read_csv(src / "ssm" / "classes.csv").set_index("class")
    cells = domain(c)
    glon, glat = cells["lon"].to_numpy(), cells["lat"].to_numpy()
    lab = [f"{-a:.0f}-{-b:.0f}S" for a, b in zip(BANDS[:-1], BANDS[1:])]
    band = lambda la: pd.cut(-np.asarray(la), [-x for x in BANDS], labels=lab)
    gb = np.asarray(band(glat))
    near = {k: hav(x, y, glon, glat) <= R_KM for k, (x, y) in hc.CITIES.items()}

    tops, flows, feeds, hs, figs, steps_tab = [], [], [], [], [], []
    for k in CLASSES:
        s = cat.load(src / "decluster" / f"cat_dc_{k}_{c.DC_METHOD}.csv", bbox=c.BBOX)
        pc = cat.load(src / "decluster" / f"cat_dc_{k}_{getattr(c, 'PATTERN_DC', c.DC_METHOD)}.csv", bbox=c.BBOX)
        r = info.loc[k]
        b = r["b_used"]
        w = fit(k, s, c, te)
        ev, wt = pattern(k, pc, w, b, c, te)
        kp = {"MIN_KERNEL_KM": c.MIN_KERNEL_KM, "KERNEL_POWER": c.KERNEL_POWER, **c.KERNEL_BY_CLASS.get(k, {})}
        nn, dmax, kind = int(r["n_neighbors"]), float(r["max_dist_km"]), r["kernel"]
        elon, elat = ev["longitude"].to_numpy(), ev["latitude"].to_numpy()
        h = smooth.kernel(elon, elat, nn, kp["MIN_KERNEL_KM"])
        eb = np.asarray(band(elat))
        print(f"\n{k}: {len(ev)} pattern events ({c.SMOOTH_EVENTS}, M>={ev['mag'].min():.1f}), kernel {kind}, {nn} neighbours, "
              f"cut-off {dmax:g} km, b {b:.3f}")

        # each event's kernel over the cells, as s02 normalizes it
        to_band = np.zeros((len(ev), len(lab)))
        to_city = np.zeros((len(ev), len(near)))
        for i in range(len(ev)):
            d = hav(elon[i], elat[i], glon, glat)
            m = d <= dmax
            kk = np.exp(-d[m] ** 2 / (2 * h[i] ** 2)) if kind == "gauss" else 1.0 / (d[m] ** 2 + h[i] ** 2) ** kp["KERNEL_POWER"]
            f = np.zeros(len(glon))
            f[m] = kk / kk.sum() * wt[i]
            to_band[i] = [f[gb == x].sum() for x in lab]
            to_city[i] = [f[v].sum() for v in near.values()]

        e = ev.assign(w=wt, share=100 * wt / wt.sum(), h_km=h, band=eb)
        st = gr.mc_of(e["mag"].to_numpy(), c.COMPLETENESS[k])
        g = e.assign(step=st, since=gr.since(e["mag"].to_numpy(), c.COMPLETENESS[k])).groupby(["step", "since"])
        g = g.agg(n=("w", "size"), w_event=("w", "first"), share_pct=("share", "sum")).reset_index()
        g["w_event_rel"] = g["w_event"] / g["w_event"].min()
        steps_tab.append(g.drop(columns="w_event").assign(**{"class": k}))
        hs.append(e.groupby("band", observed=True).agg(n=("w", "size"), h_med=("h_km", "median"),
                                                       w_pct=("share", "sum")).reset_index().assign(**{"class": k}))
        t = e.nlargest(TOP, "w")[["time_iso", "mag", "longitude", "latitude", "depth", "h_km", "share"]]
        tops.append(t.assign(**{"class": k}))
        fl = pd.DataFrame(to_band, columns=lab).groupby(eb, observed=True).sum()
        flows.append((100 * fl / fl.sum()).assign(**{"class": k}))
        for j, city in enumerate(near):
            tot = to_city[:, j].sum()
            if tot <= 0:
                continue
            o = np.argsort(to_city[:, j])[::-1][:3]
            feeds.append({"class": k, "site": city, "rate_share_of_class_pct": 100 * tot / wt.sum(),
                          **{f"ev{q + 1}": f"M{ev.loc[i, 'mag']:.1f} {ev.loc[i, 'time_iso'][:4]} "
                                           f"{ev.loc[i, 'latitude']:.1f} ({100 * to_city[i, j] / tot:.0f}%)"
                             for q, i in enumerate(o)},
                          "n_events_for_50pct": int(np.searchsorted(np.cumsum(np.sort(to_city[:, j])[::-1]), tot / 2)) + 1})
        figs.append((k, e))

    hs, tops, feeds, stp = pd.concat(hs), pd.concat(tops), pd.DataFrame(feeds), pd.concat(steps_tab)
    stp.to_csv(od / "steps.csv", index=False)
    print("\npattern weight per completeness step: events in the step, weight of one event relative to the "
          "lightest step, % of the class pattern")
    print(stp.round(2).to_string(index=False))
    fl = pd.concat(flows)
    hs.to_csv(od / "bandwidth.csv", index=False)
    tops.to_csv(od / "top_events.csv", index=False)
    fl.to_csv(od / "flow.csv")
    feeds.to_csv(od / "city_feeds.csv", index=False)
    print("\nbandwidth and pattern weight per latitude band (w_pct = % of the class pattern)")
    print(hs.round(1).to_string(index=False))
    print(f"\nevents with the largest pattern weight (share = % of the class pattern)")
    print(tops.round(2).to_string(index=False))
    print("\nwhere each band's rate comes from: rows = band of the events, columns = band of the cells, "
          "% of the column")
    print(fl.round(1).to_string())
    print(f"\nrate within {R_KM:g} km of each city: share of the class rate, the three events that feed it most, "
          "and how many events make half of it")
    print(feeds.round(1).to_string(index=False))

    f, axs = plt.subplots(1, len(figs), figsize=(4.5 * len(figs), 9), sharey=True, squeeze=False)
    for ax, (k, e) in zip(axs[0], figs):
        sc = ax.scatter(e["longitude"], e["latitude"], s=3 + 3000 * e["w"] / e["w"].max() * 0.1, c=np.log10(e["h_km"]),
                        cmap="viridis", alpha=0.6, lw=0)
        for city, (x, y) in hc.CITIES.items():
            ax.plot(x, y, "k^", ms=5)
            ax.annotate(city.replace("_", " "), (x, y), fontsize=6, xytext=(3, 2), textcoords="offset points")
        ax.set_title(f"{k}: size = pattern weight, colour = log10 bandwidth km", fontsize=8)
        ax.set_aspect("equal")
        f.colorbar(sc, ax=ax, shrink=0.4)
    f.tight_layout()
    f.savefig(od / "kernel_weights.png", dpi=300)
    plt.close(f)
    print(f"\nwrote {od} ({tree} tree)")


if __name__ == "__main__":
    main(*(sys.argv[1:3] if len(sys.argv) > 1 else [VARIANT]))
