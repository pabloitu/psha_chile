"""A9: events along the Liquiñe–Ofqui fault system (LOFS) on the frozen catalogue, with the agencies that located them,
their depths, mechanisms and class weights; all reported epicentres of the large old events. Two maps: the southern end
and the whole system. Run from catalog/ with PYTHONPATH=.:.."""
import cartopy.io.shapereader as shp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import rasterio.windows
import shapely
import shapely.ops
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from obspy.imaging.beachball import beach

import classify as C
import palette as PAL

CAT = C.HERE / "frozen" / "2026-11-16e" / "catalog_2026-11-16e.csv"
BASE = C.REPO / "data" / "basemaps" / "basemap_chile_gray" / "basemap_gray.tif"
FAULTS = C.HERE.parent / "data" / "faults" / "faults_gem_extra_2026-11-15.shp"
ISC = C.HERE / "sources" / "isc_2026-11-10_events.csv"
OUT = C.HERE / "figs" / "classify"
MAPS = {"lofs_south": dict(box=(-76.0, -71.0, -48.2, -43.6), mmin=3.0, size=(16.0, 13.0), lab=(5.5, 5.0), k=1.0),
        "lofs_full": dict(box=(-76.0, -70.3, -48.2, -37.8), mmin=4.0, size=(16.0, 22.0), lab=(5.7, 5.2), k=0.7)}
# intra-arc events (crustal weight > 0, sub-class arc) are coloured by depth, the rest grey; SPLIT edge for weights
# shared with another class, thick black edge without a measured depth
SPLIT = "#e66101"
# events with a label: intra-arc events within NEAR km of a LOFS trace, Mw >= lab[0] (lab[1] with a mechanism);
# every reported epicentre for those of Mw >= MALT before 1964
NEAR, MALT = 50.0, 6.8
ZMAX = 60.0
AGENCY = {"potin": "Potin", "csn": "CSN", "isc": "ISC", "ehb1": "ISC-EHB", "ehb2": "ISC-EHB", "iscgem": "ISC-GEM",
          "gccel": "GCCEL", "cent_ehb": "Centennial", "comcat": "ComCat", "cabello": "Cabello", "csn_isc": "CSN (ISC)",
          "gcmt": "GCMT", "a6": "A6", "assigned": "assigned"}
CMAP = plt.get_cmap("viridis_r")


def size(mw, k=1.0):
    return k * 4 * 10 ** (0.5 * (np.asarray(mw, float) - 3))


def lofs():
    r = list(shp.Reader(str(FAULTS)).records())
    return [q.geometry for q in r if "Liqui" in str(q.attributes["system"])], [q.geometry for q in r if "Liqui" not in str(q.attributes["system"])]


def events(box, mmin, lab):
    c = pd.read_csv(CAT, low_memory=False)
    c = c[c.lon.between(box[0] - 0.5, box[1] + 0.5) & c.lat.between(box[2] - 0.3, box[3] + 0.3) & (c.mw >= mmin)].copy()
    lf = shapely.ops.transform(lambda a, b: C.utm(np.asarray(a), np.asarray(b)), shapely.union_all(lofs()[0]))
    c["dl"] = shapely.distance(shapely.points(*C.utm(c.lon.to_numpy(), c.lat.to_numpy())), lf) / 1e3
    w = c[C.COLS].to_numpy()
    c["split"] = w.max(1) < 1 - 1e-9
    mech = c.strike1.notna()
    c["arc"] = (c.w_crustal > 0) & (c.sub_crustal == "arc")
    c["lab"] = c.arc & (c.dl <= NEAR) & ((c.mw >= lab[0]) | (mech & (c.mw >= lab[1]))) & \
        c.lon.between(*box[:2]) & c.lat.between(*box[2:])
    return c.sort_values("mw")


def origins(ids):
    """Every epicentre the ISC Bulletin lists for these events (event id of the catalogue -> rows agency, lon, lat)."""
    import locate
    R = locate.records()[1]
    k = R[R.event_id.isin(ids) & (R.key == "isc")][["event_id", "src_id"]].drop_duplicates().astype(str)
    s = pd.read_csv(ISC, low_memory=False, dtype={"src_id": str})
    s = s[s.src_id.isin(k.src_id)].merge(k, on="src_id")
    g = pd.read_csv(C.HERE / "sources" / "iscgem_2026-11-10_events.csv", low_memory=False, dtype={"src_id": str})
    g = g[g.src_id.isin(k.src_id)].merge(k, on="src_id").assign(agency="ISC-GEM")
    return pd.concat([s, g])[["event_id", "agency", "lon", "lat", "depth"]].drop_duplicates(["event_id", "agency", "lon", "lat"])


def caption(r):
    z = f"z {r.depth:.0f} km ({AGENCY.get(r.depth_src, r.depth_src)})" if np.isfinite(r.depth) else "z unknown"
    w = ", ".join(f"{n} {getattr(r, q):.2f}" for n, q in (("IF", "w_interface"), ("IS", "w_inslab"), ("CR", "w_crustal"),
                                                           ("OR", "w_outer_rise")) if getattr(r, q) > 0)
    cl = f"crustal {r.sub_crustal}" if not r.split else w
    mech = f" · FM {r.mech_src}" if isinstance(r.mech_src, str) else ""
    loc = AGENCY.get(r.loc_src, r.loc_src)
    if "a6_lon" in str(r.loc_flags):
        o = pd.read_csv(C.HERE / "overrides_A6.csv")
        ref = o[(o.event_id == r.event_id) & (o.property == "lon") & (o.status == "accepted")].reference.iloc[0]
        loc = f"{ref.split(' (')[0].split(' v')[0]} (A6; was {loc})"
    return f"{r.time[:10]}  Mw {r.mw:.1f}{mech}\nloc {loc} · {z}\n{cl}"


def draw(name, box, mmin, size_in, lab, k=1.0):
    PAL.apply(13)
    c = events(box, mmin, lab)
    fig, ax = plt.subplots(figsize=size_in)
    with rasterio.open(BASE) as src:
        win = rasterio.windows.from_bounds(box[0], box[2], box[1], box[3], src.transform)
        img = src.read(window=win, boundless=True)
    ax.imshow(np.moveaxis(img, 0, -1), extent=(box[0], box[1], box[2], box[3]), interpolation="bilinear", zorder=0)
    ins, out = lofs()
    for gs, col, lw, z in ((out, "0.35", 0.9, 1), (ins, "#7a1f1f", 1.6, 2)):
        for g in gs:
            for p in shapely.get_parts(g):
                ax.plot(*np.asarray(p.coords).T, color=col, lw=lw, zorder=z, solid_capstyle="round")
    o = c[~c.arc]
    ax.scatter(o.lon, o.lat, s=size(o.mw, k), c="0.45", edgecolors="0.15", linewidths=0.4 * k ** 0.5, alpha=0.4, zorder=3)
    a = c[c.arc]
    z = a.depth.to_numpy(float)
    nd = ~np.isfinite(z)
    col = np.where(nd[:, None], (1.0, 1.0, 1.0, 1.0), CMAP(Normalize(0, ZMAX)(np.nan_to_num(z))))
    ec = np.where(a.split.to_numpy()[:, None], np.array(plt.matplotlib.colors.to_rgba(SPLIT)), (0.05, 0.05, 0.05, 1))
    lw = np.where(a.split | nd, 2.0, 0.6) * k ** 0.5
    ax.scatter(a.lon, a.lat, s=size(a.mw, k), c=col, edgecolors=ec, linewidths=lw, alpha=0.72, zorder=4)
    col = pd.Series(list(col), index=a.index)
    # every reported epicentre of the large old events
    big = c[c.lab & (c.mw >= MALT) & (c.time < "1964")]
    alt = origins(big.event_id)
    for r in big.itertuples():
        for a in alt[alt.event_id == r.event_id].itertuples():
            if (abs(a.lon - r.lon) < 1e-3 and abs(a.lat - r.lat) < 1e-3) or ("a6_lon" in str(r.loc_flags) and a.agency == "CENT"):
                continue
            ax.plot([r.lon, a.lon], [r.lat, a.lat], color="k", lw=0.8, ls=":", zorder=5)
            ax.scatter(a.lon, a.lat, marker="D", s=46, facecolor="white", edgecolor="k", lw=1.0, zorder=6)
            ax.annotate(a.agency, (a.lon, a.lat), xytext=(5, -4), textcoords="offset points", fontsize=9.5, zorder=7,
                        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
    # callouts outside the map: events west of the system on the left, east of it on the right, by latitude
    from matplotlib.patches import ConnectionPatch
    lab = c[c.lab].copy()
    pts = sorted((p[1], p[0]) for g in ins for q in shapely.get_parts(g) for p in q.coords)
    lab["side"] = np.where(lab.lon < np.interp(lab.lat, *zip(*pts)) - 0.05, 0, 1)
    ax.set_xlim(box[:2])
    ax.set_ylim(box[2:])
    asp = 1 / np.cos(np.radians(np.mean(box[2:])))
    ax.set_aspect(asp)
    fig.canvas.draw()
    pos = ax.get_position()
    W, H = fig.get_size_inches()
    bh = 0.55 / (H * pos.height)
    bw = bh * H * pos.height / (W * pos.width)
    for side, y in lab.groupby("side"):
        y = y.sort_values("lat", ascending=False)
        ys = np.linspace(0.97, 0.03, len(y)) if len(y) > 1 else [(y.lat.iloc[0] - box[2]) / (box[3] - box[2])]
        xb = -0.13 if side == 0 else 1.04
        for r, yb in zip(y.itertuples(), ys):
            ax.add_artist(ConnectionPatch((r.lon, r.lat), (xb + (bw if side == 0 else 0), yb), "data", ax.transAxes,
                                          color="k", lw=0.7, shrinkA=np.sqrt(size(r.mw, k)) / 2 + 1, zorder=8))
            ia = ax.inset_axes([xb, yb - bh / 2, bw, bh])
            ia.set_axis_off()
            ia.set_xlim(-1.05, 1.05)
            ia.set_ylim(-1.05, 1.05)
            ia.set_aspect("equal")
            if np.isfinite(r.strike1):
                ia.add_collection(beach((r.strike1, r.dip1, r.rake1), xy=(0, 0), width=2, linewidth=0.8,
                                        facecolor="#7a1f1f", edgecolor="k"))
            else:
                ia.scatter(0, 0, s=60, facecolor=col[r.Index], edgecolor=SPLIT if r.split else "k",
                           lw=2.0 if r.split or not np.isfinite(r.depth) else 0.7)
            tx = xb - 0.01 if side == 0 else xb + bw + 0.01
            ax.text(tx, yb, caption(r), transform=ax.transAxes, ha="right" if side == 0 else "left", va="center",
                    fontsize=9.5, linespacing=1.15, clip_on=False)
    ax.xaxis.set_major_formatter(lambda v, _: f"{-v:.0f}° W")
    ax.yaxis.set_major_formatter(lambda v, _: f"{-v:.0f}° S")
    ax.tick_params(top=True, right=True, labeltop=True, labelleft=False, labelbottom=True)
    for s in ax.spines.values():
        s.set_visible(True)
    ax.set_title(f"Intra-arc events along the Liquiñe–Ofqui fault system: catalogue {CAT.stem.split('_')[1]}, Mw ≥ {mmin:.1f}", pad=30)
    for v in ax.get_yticks():
        if box[2] < v < box[3]:
            ax.text(0.01, (v - box[2]) / (box[3] - box[2]), f"{-v:.0f}° S", transform=ax.transAxes, fontsize=11,
                    va="center", color="0.15", bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7), zorder=11)
    # legend
    hs = [Line2D([], [], color="#7a1f1f", lw=1.8, label="LOFS traces (GEM, D16)"),
          Line2D([], [], color="0.35", lw=1.0, label="other faults"),
          Line2D([], [], ls="", marker="o", ms=10, mfc=CMAP(0.35), mec="k", mew=0.6, label="intra-arc, measured depth (colour)"),
          Line2D([], [], ls="", marker="o", ms=10, mfc="white", mec="k", mew=2.0, label="intra-arc, no measured depth"),
          Line2D([], [], ls="", marker="o", ms=10, mfc=CMAP(0.35), mec=SPLIT, mew=2.0, label="intra-arc, weight shared with another class"),
          Line2D([], [], ls="", marker="o", ms=10, mfc="0.45", mec="0.15", alpha=0.6, label="other classes"),
          Line2D([], [], ls="", marker="D", ms=7, mfc="white", mec="k", label="other reported epicentre")]
    hs += [Line2D([], [], ls="", marker="o", ms=np.sqrt(size(m, k)), mfc="none", mec="k", label=f"Mw {m}") for m in (5, 6, 7)]
    leg = ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, -0.045), bbox_transform=ax.transAxes, ncol=3, fontsize=10.5, frameon=False,
                    columnspacing=1.2, handletextpad=0.4)
    leg.set_zorder(20)
    sm = plt.cm.ScalarMappable(norm=Normalize(0, ZMAX), cmap=CMAP)
    cb = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.022, pad=0.17, extend="max", shrink=0.45)
    cb.set_label("reported depth (km)")
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    t = c[c.lab].sort_values("lat")[["event_id", "time", "mw", "lon", "lat", "depth", "depth_src", "loc_src", "mech_src",
                                     "strike1", "dip1", "rake1"] + C.COLS[:4] + ["sub_crustal", "rule", "dl"]]
    t.round(3).to_csv(C.HERE.parent / "explore" / "A9" / f"{name}_events.csv", index=False)
    alt.to_csv(C.HERE.parent / "explore" / "A9" / f"{name}_origins.csv", index=False)
    return t, alt


if __name__ == "__main__":
    import sys
    for k in sys.argv[1:] or MAPS:
        m = MAPS[k]
        t, alt = draw(k, m["box"], m["mmin"], m["size"], m["lab"], m["k"])
        print(k, len(t), "labelled")
