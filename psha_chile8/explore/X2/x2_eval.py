"""X2 checks: is the homogenized Mw consistent across scales, sizes and periods? b against fit floor, large events
predicted from 5.0–6.5, agreement of converted proxies with each other and with regional moment magnitudes,
rate stability across network changes."""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "X1"))
import x1_io as io  # noqa: E402
import x1_mag as xm  # noqa: E402
import x1_stats as xs  # noqa: E402
import x2_fit as xf  # noqa: E402

CACHE, TAB, FIG = HERE / "cache", HERE / "tables", HERE / "figs"
FIG.mkdir(exist_ok=True)

# settings
PER = [(1976, 2000, "1976–1999"), (2000, 2011, "2000–2010"), (2011, 2027, "2011–2026")]
RATE_PER = [(1976, 1990), (1990, 2000), (2000, 2011), (2011, 2027)]
FLOORS = np.round(np.arange(4.3, 6.01, 0.1), 1)
FIT = (5.0, 6.5)
FAMS = {"all": None, "interface band": "interface band", "in slab": "in slab", "crustal shallow": "above slab, shallow"}
MAIN = ["ISC mb", "NEIC mb", "VAO mb", "BJI mB", "MOS mb", "ISC MS", "GUC ML", "SJA ML", "SJA MW", "GUC MD", "GUC md"]
SHOW = ["X1 M0", "X1 M2 linear", "Cabello", "INV-G", "INV-G mean", "INV-W", "INV-W mean", "INV-G linear",
        "INV-W linear", "INV-W linear mean"]
REG = ["GUC Mwr", "CSN web Mw", "NEIC Mwr"]
DM = 0.1


def savefig(fig, name, caption):
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    with open(CACHE / "figlog.tsv", "a") as f:
        f.write(f"{name}.png\t{caption}\n")


def catalogs():
    """Variants on the X1 baseline events, plus Cabello's own catalogue on its own events (its values matched to our
    events miss or under-rate most large events, so the matched M7 of X1 is not used here)."""
    a = pd.read_csv(CACHE / "attrs.csv.gz", index_col=0)
    M = pd.read_csv(CACHE / "mw_x2.csv.gz")
    M = M[M.variant != "Cabello"].pivot_table(index="ev", columns="variant", values="mw").reindex(a.index)
    c = io.events("cabello")
    cm = io.mags("cabello")
    c["mw"] = c.src_id.map(cm[cm.agency == "cabello"].set_index("src_id").mag)
    c["yr"] = io.year(c.t.to_numpy())
    c["cls"] = None
    sets = [(v, M[v].to_numpy(), a) for v in M.columns]
    sets.append(("Cabello", c.mw.to_numpy(float), c[["yr", "t", "lat", "lon", "cls"]]))
    return a, M, sets


def trunc_b(m, lo, hi):
    """b of a GR doubly truncated to [lo, hi) for binned magnitudes (bin centres)."""
    from scipy.optimize import brentq
    x = m[(m >= lo - 1e-9) & (m < hi - 1e-9)]
    if len(x) < 20:
        return np.nan, len(x)
    c = np.round(np.arange(lo, hi - 1e-9, DM), 2)
    mean = x.mean()

    def f(beta):
        w = np.exp(-beta * c)
        return np.sum(c * w) / w.sum() - mean
    try:
        return brentq(f, 0.01, 10) / np.log(10), len(x)
    except ValueError:
        return np.nan, len(x)


def stats(sets):
    rows, large, rates = [], [], []
    for v, mv, a in sets:
        t = a.t.to_numpy() / 86400.0
        m = np.round(mv / DM) * DM
        ok = np.isfinite(m) & (a.yr.to_numpy() >= 1976)
        dep = np.zeros(len(m), bool)
        k = ok & (m >= 3.5)
        dep[k] = xs.gk_flags(t[k], a.lat.to_numpy()[k], a.lon.to_numpy()[k], m[k])
        for decl in (False, True):
            keep = ok & (~dep if decl else True)
            for fam, cls in FAMS.items():
                if cls and a.cls.isna().all():
                    continue
                kf = keep & ((a.cls.to_numpy() == cls) if cls else True)
                for y0, y1, pn in PER + [(1976, 2027, "1976–2026")]:
                    kk = kf & (a.yr.to_numpy() >= y0) & (a.yr.to_numpy() < y1)
                    x = m[kk]
                    for fl in FLOORS:
                        rows.append({"variant": v, "declust": decl, "family": fam, "period": pn, "floor": fl,
                                     "b": xs.aki(x, fl), "n": int((x >= fl - 1e-9).sum())})
                    for lo in (4.5, 5.0, 5.3):
                        b, n = trunc_b(x, lo, FIT[1])
                        n7 = (x >= 7.0 - 1e-9).sum()
                        n65 = ((x >= 6.5 - 1e-9) & (x < 7.0 - 1e-9)).sum()
                        pred = n * 10 ** (-b * (7.0 - lo)) / (1 - 10 ** (-b * (FIT[1] - lo))) if np.isfinite(b) else np.nan
                        p65 = pred * (10 ** (b * 0.5) - 1) if np.isfinite(b) else np.nan
                        large.append({"variant": v, "declust": decl, "family": fam, "period": pn, "fit_from": lo,
                                      "b_fit": b, "n_fit": n, "N7_pred": pred, "N7_obs": int(n7),
                                      "N6.5–7_pred": p65, "N6.5–7_obs": int(n65)})
            for q in (4.5, 5.0, 5.5):
                r = {"variant": v, "declust": decl, "M": q}
                for y0, y1 in RATE_PER:
                    kk = keep & (a.yr.to_numpy() >= y0) & (a.yr.to_numpy() < y1) & (m >= q - 1e-9)
                    r[f"{y0}–{y1 - 1}"] = kk.sum() / (y1 - y0)
                rates.append(r)
        print("stats", v, flush=True)
    return pd.DataFrame(rows), pd.DataFrame(large), pd.DataFrame(rates)


# per-scale converted values for the consistency checks
def proxies(a):
    L, W, R, _ = xf.load()
    fits = json.load(open(CACHE / "fits_x2.json"))
    out = {}
    for key, nm in (("inv G", "INV-G"), ("inv W", "INV-W"), ("trunc G", "TRUNC-G"), ("inv-lin G", "INV-G linear"),
                    ("inv-lin W", "INV-W linear")):
        Y = {}
        for f in fits[key]:
            if f["scale"] not in MAIN:
                continue
            x = W[f["scale"]].to_numpy(float)
            k = np.isfinite(x)
            y = np.full(len(x), np.nan)
            y[k] = xf.convert(f, x[k], a.z.to_numpy(float)[k])[0]
            Y[f["scale"]] = y
        out[nm] = pd.DataFrame(Y, index=a.index)
    F1 = json.load(open(HERE.parent / "X1" / "cache" / "fits.json"))["baseline"]
    at = a.copy()
    Y = {}
    for sc in MAIN:
        fr = xm.choose_fit(F1, sc, "CSQ η(TC) + eq. error")
        if fr is None or sc not in W:
            continue
        x = W[sc].to_numpy(float)
        k = np.isfinite(x)
        y = np.full(len(x), np.nan)
        y[k] = xm.predict(fr, x[k], a.index.to_numpy()[k], at)[0]
        Y[sc] = y
    out["X1 M0"] = pd.DataFrame(Y, index=a.index)
    reg, _ = wref(W)
    return out, reg, W


def wref(W):
    off = json.load(open(TAB / "x2_wref_offsets.json"))
    y = pd.Series(np.nan, index=W.index)
    for c in REG:
        if c in W:
            y = y.fillna(W[c] + off.get(c, 0.0))
    return y, off


def consistency(P, reg, W):
    """Median difference between converted scales on the same events, and against regional moment magnitudes,
    binned by the mean of the two values."""
    bins = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0]
    rows = []
    direct = W[["GCMT Mw", "NEIC Mww", "CSN Mww"]].notna().any(axis=1).to_numpy()
    for nm, Y in P.items():
        cols = [c for c in MAIN if c in Y]
        for i, c1 in enumerate(cols):
            for c2 in cols[i + 1:]:
                k = Y[c1].notna() & Y[c2].notna()
                if k.sum() < 50:
                    continue
                mm = (Y[c1][k] + Y[c2][k]) / 2
                d = Y[c1][k] - Y[c2][k]
                for lo, hi in zip(bins[:-1], bins[1:]):
                    kb = (mm >= lo) & (mm < hi)
                    if kb.sum() >= 20:
                        rows.append({"variant": nm, "check": "scale pair", "a": c1, "b": c2, "bin": f"{lo}–{hi}",
                                     "lo": lo, "n": int(kb.sum()), "median": float(d[kb].median())})
        for c in cols:
            for nd in (False, True):
                k = Y[c].notna() & reg.notna() & ((~direct) if nd else True)
                mm = reg[k]
                d = Y[c][k] - reg[k]
                for lo, hi in zip(bins[:-1], bins[1:]):
                    kb = (mm >= lo) & (mm < hi)
                    if kb.sum() >= 20:
                        rows.append({"variant": nm, "check": "vs regional Mw" + (" (no direct Mw)" if nd else ""),
                                     "a": c, "b": "regional Mw", "bin": f"{lo}–{hi}", "lo": lo, "n": int(kb.sum()),
                                     "median": float(d[kb].median())})
    return pd.DataFrame(rows)


def scores(B, Lg, Rt, C):
    """One row per variant: the headline numbers."""
    out = []
    for v in SHOW:
        r = {"variant": v}
        for decl in (False, True):
            tag = "decl" if decl else "full"
            b = B[(B.variant == v) & (B.declust == decl) & (B.family == "all") & (B.period == "2011–2026")]
            bb = b.set_index("floor").b
            r[f"b 4.5 {tag}"] = bb.get(4.5)
            r[f"b 5.0 {tag}"] = bb.get(5.0)
            r[f"b 5.5 {tag}"] = bb.get(5.5)
            r[f"b range 4.7–5.8 {tag} 2011–26"] = float(bb.loc[4.7:5.8].max() - bb.loc[4.7:5.8].min())
            g = Lg[(Lg.variant == v) & (Lg.declust == decl) & (Lg.family == "all") & (Lg.period == "1976–2026")
                   & (Lg.fit_from == 5.0)]
            if len(g):
                r[f"N7 pred/obs {tag}"] = float(g.N7_pred.iloc[0] / g.N7_obs.iloc[0])
                r[f"b 5.0–6.5 {tag}"] = float(g.b_fit.iloc[0])
        q = Rt[(Rt.variant == v) & Rt.declust & (Rt.M == 5.0)]
        if len(q):
            x = q.iloc[0][[c for c in q.columns if "–" in c]].astype(float)
            r["rate M≥5 decl cv"] = float(x.std() / x.mean())
        c = C[(C.variant == v) & (C.check == "scale pair") & (C.lo >= 4.0) & (C.lo < 6.0)]
        if len(c):
            r["pair |median| mean"] = float(c["median"].abs().mean())
        c = C[(C.variant == v) & (C.check == "vs regional Mw (no direct Mw)") & (C.lo >= 3.5) & (C.lo < 5.5)]
        if len(c):
            r["vs regional |median| mean"] = float(c["median"].abs().mean())
        out.append(r)
    return pd.DataFrame(out)


# figures
def fig_bfloor(plt, B):
    fams = ["all", "interface band", "in slab"]
    fig, ax = plt.subplots(len(fams), len(PER), figsize=(16, 12), layout="constrained", sharex=True, sharey=True)
    for i, fam in enumerate(fams):
        for j, (_, _, pn) in enumerate(PER):
            a_ = ax[i, j]
            for c, v in enumerate(SHOW):
                x = B[(B.variant == v) & B.declust & (B.family == fam) & (B.period == pn)]
                x = x[x.n >= 50]
                a_.plot(x.floor, x.b, color=io.palette.SERIES[c % len(io.palette.SERIES)],
                        lw=2.4 if v in ("INV-W linear mean", "X1 M0", "Cabello") else 1.0,
                        ls="--" if v in ("X1 M0", "Cabello") else "-", label=v)
            a_.axhline(1.0, color="0.7", lw=0.7)
            a_.set_ylim(0.5, 2.0)
            if i == 0:
                a_.set_title(pn, fontsize=11)
            if j == 0:
                a_.set_ylabel(f"{fam}\nb (declustered)")
            if i == len(fams) - 1:
                a_.set_xlabel("lowest magnitude fitted")
    ax[0, -1].legend(fontsize=8, ncol=2)
    fig.suptitle("Does b stay put when the fit floor drops? A consistent Mw gives a flat line above completeness",
                 x=0.01, ha="left")
    savefig(fig, "x2_b_vs_floor", "Aki b against the lowest magnitude fitted, per period and family, declustered, "
            "for the X2 conversions, X1 M0 and Cabello")


def fig_large(plt, Lg):
    fams = ["all", "interface band", "in slab"]
    fig, ax = plt.subplots(1, len(fams), figsize=(17, 6), layout="constrained", sharey=True)
    for a_, fam in zip(ax, fams):
        for c, v in enumerate(SHOW):
            for d, mk in ((False, "o"), (True, "s")):
                g = Lg[(Lg.variant == v) & (Lg.declust == d) & (Lg.family == fam) & (Lg.period == "1976–2026")
                       & (Lg.fit_from == 5.0)]
                if len(g):
                    a_.scatter(g.N7_pred / g.N7_obs, c, marker=mk, s=50, color=io.palette.SERIES[c % 10],
                               edgecolor="k" if d else "none", lw=0.6)
        a_.axvline(1, color="0.4", lw=0.8)
        a_.axvspan(0.67, 1.5, color="0.92", zorder=0)
        a_.set_xscale("log")
        a_.set_xlim(0.05, 3)
        a_.set_title(fam, fontsize=11)
        a_.set_xlabel("predicted / observed N(M ≥ 7), 1976–2026")
    ax[0].set_yticks(range(len(SHOW)), SHOW)
    ax[0].invert_yaxis()
    fig.suptitle("Does a GR fitted on Mw 5.0–6.5 predict the M ≥ 7 events? Circles all events, squares declustered",
                 x=0.01, ha="left")
    savefig(fig, "x2_large_events", "Ratio of predicted to observed N(M ≥ 7) 1976–2026 from a truncated GR fitted "
            "on Mw 5.0–6.5, per variant and family")


def fig_fmd(plt, a, M, sets):
    fig, ax = plt.subplots(1, len(PER), figsize=(18, 6), layout="constrained", sharey=True)
    g = np.round(np.arange(3.5, 9.0, DM), 1)
    for a_, (y0, y1, pn) in zip(ax, PER):
        for c, (v, mv, at) in enumerate([q for q in sets if q[0] in SHOW]):
            k = (at.yr.to_numpy() >= y0) & (at.yr.to_numpy() < y1)
            x = np.round(mv[k][np.isfinite(mv[k])] / DM) * DM
            n = np.array([(np.abs(x - q) < 1e-6).sum() for q in g])
            a_.semilogy(g, np.where(n > 0, n, np.nan), color=io.palette.SERIES[c % 10],
                        lw=2.2 if v in ("INV-W linear mean", "X1 M0", "Cabello") else 0.9,
                        ls="--" if v in ("X1 M0", "Cabello") else "-", label=v, drawstyle="steps-mid")
        k = (a.yr >= y0) & (a.yr < y1)
        ref = (np.abs(np.round(M["INV-G"][k].dropna() / DM) * DM - 6.0) < 1e-6).sum()
        a_.semilogy(g, ref * 10 ** (-(g - 6.0)), color="0.5", lw=0.8, ls=":", label="b = 1")
        a_.set_xlim(3.5, 8.5)
        a_.set_title(pn, fontsize=11)
        a_.set_xlabel("Mw (0.1 bins)")
    ax[0].set_ylabel("events per bin")
    ax[-1].legend(fontsize=8)
    fig.suptitle("Where do converted events pile up? Incremental counts per 0.1 bin", x=0.01, ha="left")
    savefig(fig, "x2_fmd", "Incremental magnitude–frequency distributions per period for each variant")


def fig_consistency(plt, C):
    fig, ax = plt.subplots(1, 2, figsize=(16, 6), layout="constrained")
    vs = ["X1 M0", "INV-G", "INV-W", "TRUNC-G", "INV-G linear", "INV-W linear"]
    for c, v in enumerate(vs):
        x = C[(C.variant == v) & (C.check == "vs regional Mw (no direct Mw)")]
        g = x.groupby("lo")["median"].agg(lambda s: np.median(s))
        ax[0].plot(g.index + 0.25, g.values, "o-", color=io.palette.SERIES[c], label=v)
        y = C[(C.variant == v) & (C.check == "scale pair")]
        g2 = y.groupby("lo")["median"].agg(lambda s: np.mean(np.abs(s)))
        ax[1].plot(g2.index + 0.25, g2.values, "o-", color=io.palette.SERIES[c], label=v)
    ax[0].axhline(0, color="0.5", lw=0.8)
    ax[0].set_xlabel("regional Mw")
    ax[0].set_ylabel("converted − regional Mw (median over scales)")
    ax[0].set_title("Against regional moment magnitudes, events without GCMT or Mww", fontsize=11)
    ax[1].set_xlabel("mean of the two converted values")
    ax[1].set_ylabel("mean |median difference| over scale pairs")
    ax[1].set_title("Between converted scales on the same events", fontsize=11)
    ax[1].legend(fontsize=9)
    fig.suptitle("Do the converted scales agree with each other and with an independent Mw below the GCMT floor?",
                 x=0.01, ha="left")
    savefig(fig, "x2_consistency", "Converted proxies against regional moment magnitudes (GUC Mwr, CSN Mw, NEIC Mwr) "
            "and against each other, per variant")


def fig_relations(plt):
    L, W, R, a = xf.load()
    fits = json.load(open(CACHE / "fits_x2.json"))
    F1 = json.load(open(HERE.parent / "X1" / "cache" / "fits.json"))["baseline"]
    scs = ["ISC mb", "NEIC mb", "GUC ML", "ISC MS"]
    fig, ax = plt.subplots(1, len(scs), figsize=(20, 5.8), layout="constrained")
    for a_, sc in zip(ax, scs):
        k = W[sc].notna() & W["GCMT Mw"].notna()
        x, y = W.loc[k, sc].to_numpy(float), W.loc[k, "GCMT Mw"].to_numpy(float)
        a_.scatter(x, y, s=3, color="0.75", lw=0, rasterized=True)
        for lo in np.arange(3.5, 7.0, 0.25):
            kk = (x >= lo) & (x < lo + 0.25)
            if kk.sum() >= 10:
                a_.plot(lo + 0.125, np.median(y[kk]), "v", color="k", ms=5)
            kk = (y >= lo) & (y < lo + 0.25)
            if kk.sum() >= 10:
                a_.plot(np.median(x[kk]), lo + 0.125, ">", color="#c0392b", ms=5)
        g = np.linspace(3.0, 7.5, 200)
        za = np.full(len(g), 20.0)
        for c, (key, nm) in enumerate((("inv G", "INV-G"), ("inv W", "INV-W"), ("trunc G", "TRUNC-G"),
                                       ("inv-lin W", "INV-W linear"))):
            f = next((f for f in fits[key] if f["scale"] == sc), None)
            if f:
                a_.plot(g, xf.convert(f, g, za)[0], color=io.palette.SERIES[c + 3], lw=2, label=nm)
        fr = xm.choose_fit(F1, sc, "CSQ η(TC) + eq. error")
        if fr:
            at = pd.DataFrame({"z": za, "yr": 2005.0}, index=np.arange(len(g)))
            a_.plot(g, xm.predict(fr, g, at.index.to_numpy(), at)[0], color="k", ls="--", lw=1.5, label="X1 M0")
        for nm, f in xm.PUB.get(sc, {}).items():
            a_.plot(g, f(g), color="0.4", lw=0.8, ls=":")
        a_.plot(g, g, color="0.85", lw=0.8)
        a_.set_xlim(3.3, 7.3)
        a_.set_ylim(4.0, 8.5)
        a_.set_title(f"{sc} ({len(x)} GCMT pairs)", fontsize=11)
        a_.set_xlabel(sc)
    ax[0].set_ylabel("Mw")
    ax[0].legend(fontsize=9, loc="upper left")
    fig.suptitle("Why the low end bends: black ▼ median Mw per native bin (biased by the GCMT floor), red ▶ median "
                 "native per Mw bin (unbiased); dotted: published", x=0.01, ha="left")
    savefig(fig, "x2_relations", "Conversion relations for four scales: X1 forward chi-square against the inverse "
            "(native on Mw) and truncated fits, with binned medians in both directions")


def run():
    T0 = time.time()
    a, M, sets = catalogs()
    B, Lg, Rt = stats(sets)
    B.to_csv(TAB / "x2_b_vs_floor.csv", index=False)
    Lg.to_csv(TAB / "x2_large_events.csv", index=False)
    Rt.to_csv(TAB / "x2_rates.csv", index=False)
    print("stats", round(time.time() - T0), flush=True)
    P, reg, W = proxies(a)
    C = consistency(P, reg, W)
    C.to_csv(TAB / "x2_consistency.csv", index=False)
    stability()
    S = scores(B, Lg, Rt, C)
    S.to_csv(TAB / "x2_scores.csv", index=False)
    print(S.round(3).T.to_string())
    plt = io.fig_setup()
    for f, args in ((fig_bfloor, (B,)), (fig_large, (Lg,)), (fig_fmd, (a, M, sets)), (fig_consistency, (C,)),
                    (fig_relations, ())):
        try:
            f(plt, *args)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            with open(CACHE / "failures.log", "a") as fh:
                fh.write(f"{f.__name__}: {e!r}\n")
    print("done", round(time.time() - T0), flush=True)



def stability():
    """Inverse linear fits per period (does the native–Mw relation drift?) and with other errors assumed for Mw."""
    L, W, R, a = xf.load()
    rows = []
    for sc in ["ISC mb", "NEIC mb", "ISC MS", "GUC ML", "MOS mb", "VAO mb"]:
        for ref, y_ref in (("G", W["GCMT Mw"]), ("W", xf.wref(W)[0])):
            k = W[sc].notna() & y_ref.notna() & (y_ref < 6.0)
            for (y0, y1, pn) in [(1964, 1990, "1976–1989"), (1990, 2000, "1990–1999"), (2000, 2011, "2000–2010"),
                                 (2011, 2027, "2011–2026"), (1900, 2100, "all")]:
                kk = k & (a.yr >= y0) & (a.yr < y1)
                if kk.sum() < 40:
                    continue
                for sy in ((0.0, xf.SY[ref], 0.15) if pn == "all" else (xf.SY[ref],)):
                    f = xf.fit_inv(y_ref[kk].to_numpy(float), W.loc[kk, sc].to_numpy(float), sy, "linear")
                    yy = xf.conv_inv(f, np.array([4.0, 4.5, 5.0, 5.5]))[0]
                    rows.append({"scale": sc, "ref": ref, "period": pn, "sy": sy, "n": int(kk.sum()), "slope": f["p"][1],
                                 "Mw at 4.0": yy[0], "Mw at 4.5": yy[1], "Mw at 5.0": yy[2], "Mw at 5.5": yy[3]})
    t = pd.DataFrame(rows)
    t.to_csv(TAB / "x2_stability.csv", index=False)
    return t


if __name__ == "__main__":
    run()
