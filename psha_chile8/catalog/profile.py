"""One profile figure per frozen source catalog: figs/profile/<name>.png (plan A2).

Events per year by magnitude band (largest magnitude the source reports for the event;
for a mechanism-only source, Mw from M0 where the source gives no Mw: figure only),
magnitude types through time, depth histogram of the preferred origins (1 km bins,
log counts, so default depths stand out), and a map of the download box.
"""
import sys
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import palette as pal
from fetch import BOX

# settings
RUN = ["comcat", "comcat_mt", "isc", "csn_isc", "csn", "iscehb", "iscgem", "gcmt", "centennial", "potin", "cabello",
       "rm2018"]
SRC = HERE / "sources"
FIGS = HERE / "figs" / "profile"
NTYPES = 14
TITLE = {"comcat": "USGS ComCat", "comcat_mt": "ComCat moment tensors", "isc": "ISC Bulletin",
         "csn_isc": "CSN solutions in the ISC Bulletin", "csn": "CSN catalogue (sismologia.cl)", "iscehb": "ISC-EHB",
         "iscgem": "ISC-GEM", "gcmt": "GCMT",
         "centennial": "Centennial catalogue", "potin": "Potin et al. (2024)", "cabello": "Cabello et al. (2025)",
         "rm2018": "Ruiz and Madariaga (2018)"}


def latest(name, kind):
    fs = sorted(SRC.glob(f"{name}_????-??-??_{kind}.csv"))
    return pd.read_csv(fs[-1], dtype={"src_id": str}, low_memory=False) if fs else None


def band(m):
    b = pd.cut(m, [-9, 4, 5, 6, 7, 99], right=False, labels=list(pal.BAND)[:5]).astype(object)
    return b.where(m.notna(), "no magnitude")


def profile(name, ev, mg, mc=None):
    """Draw the four panels for one source and save figs/profile/<name>.png."""
    pal.apply()
    ev = ev[ev.prime.astype(str) == "True"].copy()
    ev["year"] = ev.time.astype(str).str[:4].astype(int)
    if mg is None or mg.empty:
        mw = mc.mw.fillna(2 / 3 * (np.log10(mc.m0.where(mc.m0 > 0)) - 9.1)) if mc is not None else None
        mg = pd.DataFrame(dict(src_id=mc.src_id, agency=mc.agency, mag_type="Mw", mag=mw)) if mc is not None \
            else pd.DataFrame(columns=["src_id", "agency", "mag_type", "mag"])
    ev["m"] = ev.src_id.map(mg.groupby("src_id").mag.max())
    ev["band"] = band(ev.m)
    fig = plt.figure(figsize=(15, 10))
    g = fig.add_gridspec(2, 3, width_ratios=[1.25, 1.25, 1], hspace=0.32, wspace=0.3)

    a = fig.add_subplot(g[0, :2])
    n = ev.groupby(["year", "band"]).size().unstack(fill_value=0).reindex(columns=list(pal.BAND), fill_value=0)
    n = n.reindex(range(ev.year.min(), ev.year.max() + 1), fill_value=0)
    bot = np.zeros(len(n))
    for b in pal.BAND:
        if n[b].sum():
            a.bar(n.index, n[b], bottom=bot, width=1, color=pal.BAND[b], ec="0.4" if b == "no magnitude" else "none",
                  lw=0.3, label=f"{b} ({n[b].sum():,})")
            bot += n[b].values
    a.set_yscale("symlog", linthresh=10)
    a.set_ylabel("events per year")
    a.legend(ncol=3, loc="upper left")
    a.set_title(f"{TITLE.get(name, name)}: {len(ev):,} events, {ev.year.min()}–{ev.year.max()}")

    b_ = fig.add_subplot(g[1, :2], sharex=a)
    t = mg.merge(ev[["src_id", "year"]], on="src_id")
    t["k"] = t.agency.fillna("?").astype(str) + " " + t.mag_type.fillna("?").astype(str)
    top = t.k.value_counts().index[:NTYPES][::-1]
    c = t[t.k.isin(top)].groupby(["k", "year"]).size()
    for i, k in enumerate(top):
        y = c[k]
        b_.scatter(y.index, np.full(len(y), i), s=4 + 40 * np.log10(y.values) / max(1, np.log10(c.max())),
                   color=pal.SERIES[i % len(pal.SERIES)], lw=0)
    b_.set_yticks(range(len(top)), [f"{k}  ({(t.k == k).sum():,})" for k in top])
    b_.set_xlabel("year")
    b_.set_title(f"magnitude types by agency ({t.k.nunique()} in all, {len(top)} most frequent shown)")
    b_.spines["left"].set_visible(False)
    b_.tick_params(axis="y", length=0)

    d = fig.add_subplot(g[0, 2])
    z = ev.depth.dropna()
    if len(z):
        bins = np.arange(np.floor(z.min()), max(z.max(), 1) + 2)
        fx = ev.depth_fixed.astype(str).str.lower()
        for lab, sel, col in (("free or not flagged", ~fx.isin(["true"]), pal.SERIES[0]),
                              ("flagged fixed", fx.isin(["true"]), pal.SERIES[1])):
            if sel.any():
                d.hist(ev.depth[sel].dropna(), bins=bins, color=col, alpha=0.85, label=lab, histtype="stepfilled")
        d.set_yscale("log")
        d.set_xlabel("depth (km)")
        d.set_ylabel("events per 1 km")
        d.legend()
        s = z.round(1).value_counts()
        d.set_title("depth: most frequent " + ", ".join(f"{v:g}" for v in s.index[:4]) + " km")
    else:
        d.set_axis_off()

    m = fig.add_subplot(g[1, 2], projection=ccrs.PlateCarree())
    m.set_extent([BOX["lon0"], BOX["lon1"], BOX["lat0"], BOX["lat1"]], ccrs.PlateCarree())
    m.add_feature(cf.LAND.with_scale("50m"), color="0.93")
    m.add_feature(cf.COASTLINE.with_scale("50m"), lw=0.4, ec="0.4")
    m.add_feature(cf.BORDERS.with_scale("50m"), lw=0.3, ec="0.6")
    e = ev.dropna(subset=["lon", "lat"]).sort_values("m", na_position="first")
    for b in ["no magnitude"] + list(pal.BAND)[:5]:
        s = e[e.band == b]
        m.scatter(s.lon, s.lat, s=1 if b in ("M < 4", "no magnitude") else 4 + 6 * list(pal.BAND).index(b),
                  color=pal.BAND[b] if b != "no magnitude" else "0.5", lw=0, transform=ccrs.PlateCarree())
    gl = m.gridlines(draw_labels=True, lw=0.2, color="0.7")
    gl.top_labels = gl.right_labels = False
    m.set_title("preferred origins")

    FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGS / f"{name}.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    for s in RUN:
        ev, mg, mc = (latest(s, k) for k in ("events", "mags", "mechs"))
        if s == "comcat_mt" and mc is not None and latest("comcat", "events") is not None:
            ev = latest("comcat", "events")
            ev = ev[ev.src_id.isin(mc.src_id)]
        if ev is None:
            print(f"{s}: no frozen tables, skipped")
            continue
        print(f"== {s}")
        profile(s, ev, mg, mc)
