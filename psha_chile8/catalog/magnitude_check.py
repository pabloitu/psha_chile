"""Acceptance tests and figures of the A5 magnitudes (task brief A5, tests 1 to 9).

Reads the outputs of magnitude.py, refits what the tests need (held-out fits, the alternatives of the sensitivity
table), and writes merged/mw_tests_<date>.csv, merged/mw_sensitivity_<date>.csv, merged/mw_synthetic_<date>.csv
and the figures in figs/magnitude/. A failed test is reported, nothing is tuned here.
"""
import csv
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numba as nb
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import chi2

import magnitude as G
from match import SRC, OUT, FROZEN, tsec, year

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import palette  # noqa: E402

# settings
RUN = G.RUN
FIG = HERE / "figs" / "magnitude"
SLAB = HERE.parents[1] / "data" / "slab_2.0"
XLSX = Path.home() / "Downloads" / "srl-2025449_supplement.xlsx"
CACHE = HERE / "cache"
DM = 0.1
FLOORS = np.round(np.arange(4.7, 5.81, 0.1), 1)
SHOW = np.round(np.arange(4.3, 6.01, 0.1), 1)
B_RANGE = 0.2
B_PER = [(2011, "2011 to today"), (1976, "1976 to today")]
PER = [(1976, 1990), (1990, 2000), (2000, 2011), (2011, 2100)]
RATE_M, RATE_TOL = [5.0, 5.5], 0.15
FIT_HI, FIT_LO = 6.5, [5.0, 5.3]
BAND = 0.95
FAMS = {"all": None, "interface band": "interface band", "in slab": "in slab", "crustal shallow": "above slab, shallow"}
Y0, MMIN_DECL = 1964, 3.5
MAIN = ["ISC mb", "NEIC mb", "GUC ML", "SJA ML", "ISC MS", "NEIC MS"]
NAME = {"GUC ML": "CSN ML", "SJA ML": "INPRES ML"}
REG = ["GUC Mwr", "CSN web Mw", "NEIC Mwr"]
IND_BINS, IND_FROM, IND_TOL, IND_N = np.round(np.arange(4.0, 5.51, 0.25), 2), 4.5, 0.1, 20
HIST = np.round(np.arange(4.3, 5.61, 0.1), 1)
HIST_FROM, HIST_Z = 4.5, 3.0
OLD_PER = (1964, 1976)
N_GLS = 300
BOX = (-58.0, -15.5, -80.0, -60.0)
SYN = {"a": 0.5, "b": 0.9, "sx": 0.20, "sy": 0.08, "floor": 5.3, "width": 0.1, "n": 200000, "rep": 20, "m0": 3.5}
SYN_X = np.round(np.arange(3.5, 6.51, 0.25), 2)
FWD_FIG = ["ISC mb", "NEIC mb", "GUC ML"]


# statistics
@nb.njit(cache=True)
def gk(t, la, lo, m):
    """Gardner and Knopoff (1974) windows; t in days; True for dependent events."""
    n = len(t)
    order = np.argsort(-m)
    dep = np.zeros(n, np.bool_)
    ts = np.argsort(t)
    tsorted = t[ts]
    for i in order:
        if dep[i]:
            continue
        M = m[i]
        T = 10 ** (0.032 * M + 2.7389) if M >= 6.5 else 10 ** (0.5409 * M - 0.547)
        L = 10 ** (0.1238 * M + 0.983)
        j0 = np.searchsorted(tsorted, t[i])
        j1 = np.searchsorted(tsorted, t[i] + T)
        for jj in range(j0, j1):
            j = ts[jj]
            if j == i or dep[j] or m[j] > M:
                continue
            p1, p2 = np.radians(la[i]), np.radians(la[j])
            a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo[j] - lo[i]) / 2) ** 2
            if 2 * 6371.0 * np.arcsin(np.sqrt(min(a, 1.0))) <= L:
                dep[j] = True
    return dep


def aki(m, mc):
    k = m >= mc - 1e-9
    return np.log10(np.e) / (m[k].mean() - (mc - DM / 2)) if k.sum() >= 2 else np.nan


def trunc_b(m, lo, hi):
    """b of a Gutenberg–Richter law doubly truncated to [lo, hi), binned magnitudes (bin centres)."""
    x = m[(m >= lo - 1e-9) & (m < hi - 1e-9)]
    c = np.round(np.arange(lo, hi - 1e-9, DM), 2)
    f = lambda beta: np.sum(c * np.exp(-beta * c)) / np.exp(-beta * c).sum() - x.mean()
    try:
        return (brentq(f, 0.01, 10) / np.log(10), len(x)) if len(x) >= 20 else (np.nan, len(x))
    except ValueError:
        return np.nan, len(x)


def band(n, p=BAND):
    """Interval of the Poisson mean that is compatible with an observed count n (Garwood)."""
    return (chi2.ppf((1 - p) / 2, 2 * n) / 2 if n else 0.0), chi2.ppf((1 + p) / 2, 2 * n + 2) / 2


def family(e):
    """Depth proxy classes of X1 on the provisional A3 depth: Slab2 top s and thickness th at the epicentre;
    shallow above the slab (z < 30 and z < s - 15), interface band (|z - s| <= 15, s < 60), in slab (down to
    s + th). An event without depth has no class."""
    from scipy.interpolate import RegularGridInterpolator
    g = {}
    for k in ("dep", "thk"):
        a = pd.read_csv(SLAB / f"sam_slab2_{k}_02.23.18.xyz", header=None, names=["x", "y", "z"])
        z = a.pivot(index="y", columns="x", values="z")
        g[k] = RegularGridInterpolator((z.index.to_numpy(), z.columns.to_numpy()), z.to_numpy(), bounds_error=False)
    p = np.c_[e.lat.to_numpy(float), np.mod(e.lon.to_numpy(float), 360)]
    s, th, z = -g["dep"](p), g["thk"](p), e.z.to_numpy(float)
    th = np.where(np.isfinite(th), th, 40.0)
    m = np.isfinite(z) & np.isfinite(s)
    out = np.full(len(e), None, object)
    band_ = m & (np.abs(z - s) <= 15) & (s < 60)
    out[m & ~band_ & (z >= s - 15) & (z <= s + th)] = "in slab"
    out[band_] = "interface band"
    out[m & (z < 30) & (z < s - 15)] = "above slab, shallow"
    return out


def tests123(name, mw, c, t_end):
    """
    Tests 1 to 3 on one catalogue.

    mw : magnitudes; c : table with t [s], yr, lat, lon and cls (None for no families)

    Returns rows test, catalogue, subset, quantity, value, limit, passed.
    """
    m = np.round(np.asarray(mw, float) + 1e-9, 1)
    yr, t = c.yr.to_numpy(float), c.t.to_numpy(float) / 86400.0
    ok = np.isfinite(m) & np.isfinite(t) & (yr >= Y0)
    dep = np.zeros(len(m), bool)
    k = ok & (m >= MMIN_DECL)
    dep[k] = gk(t[k], c.lat.to_numpy(float)[k], c.lon.to_numpy(float)[k], m[k])
    rows = []
    add = lambda test, sub, q, v, lim=None, p=None: rows.append({"test": test, "catalogue": name, "subset": sub, "quantity": q,
                                                                 "value": v, "limit": lim, "passed": p})
    for decl in (False, True):
        tag = "declustered" if decl else "full"
        keep = ok & ~(dep & decl)
        for y0, lab in B_PER:
            x = m[keep & (yr >= y0)]
            b = np.array([aki(x, f) for f in SHOW])
            for f, v in zip(SHOW, b):
                add(1, f"{lab}, {tag}", f"b at {f:.1f}", v)
            r = float(np.ptp(b[np.isin(SHOW, FLOORS)]))
            add(1, f"{lab}, {tag}", f"b range {FLOORS[0]}–{FLOORS[-1]}", r, f"<= {B_RANGE}", r <= B_RANGE)
        for fam, cls in FAMS.items():
            if cls and c.cls.isna().all():
                continue
            x = m[keep & (yr >= PER[0][0]) & ((c.cls.to_numpy() == cls) if cls else True)]
            for lo in FIT_LO:
                b, n = trunc_b(x, lo, FIT_HI)
                p7 = n * 10 ** (-b * (7.0 - lo)) / (1 - 10 ** (-b * (FIT_HI - lo)))
                for q, pred, obs in (("N >= 7", p7, int((x >= 7.0 - 1e-9).sum())),
                                     ("N 6.5–7", p7 * (10 ** (0.5 * b) - 1), int(((x >= 6.5 - 1e-9) & (x < 7.0 - 1e-9)).sum()))):
                    lo_, hi_ = band(obs)
                    sub = f"{fam}, {tag}, fit from {lo}"
                    add(3, sub, f"{q} observed", obs)
                    add(3, sub, f"{q} predicted", pred, f"{lo_:.1f} to {hi_:.1f}", bool(lo_ <= pred <= hi_) if np.isfinite(pred) else None)
                add(3, f"{fam}, {tag}, fit from {lo}", "b of the fit", b)
    keep = ok & ~dep
    for q in RATE_M:
        r = np.array([(keep & (yr >= a) & (yr < b) & (m >= q - 1e-9)).sum() / (min(b, t_end) - a) for a, b in PER])
        for (a, b), v in zip(PER, r):
            add(2, "declustered", f"rate M >= {q}, {a}–{'today' if b > 2090 else b - 1}", v)
        d = float(np.abs(r / r.mean() - 1).max())
        add(2, "declustered", f"rate M >= {q}, largest departure from the mean", d, f"<= {RATE_TOL}" if q == 5.5 else None,
            (d <= RATE_TOL) if q == 5.5 else None)
    a, b = OLD_PER
    for q in RATE_M:
        add(6, "declustered", f"rate M >= {q}, {a}–{b - 1}", (keep & (yr >= a) & (yr < b) & (m >= q - 1e-9)).sum() / (b - a))
    return pd.DataFrame(rows), dep


def headline(T, name):
    """The numbers of tests 1 to 3 that go into the summary and sensitivity tables."""
    x = T[T.catalogue == name]
    v = lambda test, sub, q: x[(x.test == test) & (x.subset == sub) & (x.quantity == q)].value.astype(float).squeeze()
    r = {"catalogue": name}
    for _, lab in B_PER:
        for tag in ("full", "declustered"):
            r[f"b range {lab}, {tag}"] = v(1, f"{lab}, {tag}", f"b range {FLOORS[0]}–{FLOORS[-1]}")
    r["rate M>=5.5 departure"] = v(2, "declustered", "rate M >= 5.5, largest departure from the mean")
    r["rate M>=5.0 departure"] = v(2, "declustered", "rate M >= 5.0, largest departure from the mean")
    for lo in FIT_LO:
        for q in ("N >= 7", "N 6.5–7"):
            for tag in ("full", "declustered"):
                s = f"all, {tag}, fit from {lo}"
                r[f"{q} pred/obs, {tag}, from {lo}"] = f"{v(3, s, q + ' predicted'):.1f} / {int(v(3, s, q + ' observed'))}"
    p = x[x.passed.notna() & x.subset.str.startswith(("all", "declustered", "2011", "1976"))]
    p = p[~p.passed.astype(bool)]
    r["failed (all events)"] = "; ".join(f"T{a} {b}: {c}" for a, b, c in zip(p.test, p.subset, p.quantity)) or "none"
    return r


# catalogues
class Data:
    """Inputs and the fits of the run, with the alternatives of the sensitivity table built on demand."""

    def __init__(self):
        self.e, self.M, self.rm = G.load()
        self.e["cls"] = family(self.e)
        self.t_end = float(self.e.yr.max())
        self.R, self.tab, self.W = G.reference(self.M)
        self.F = G.relations(self.M, self.R, self.e, quiet=True)
        self.prio = [s for s in (G.PRIORITY or G.priority(self.F)) if s in self.F]
        self.P = G.proxies(self.e, self.M, self.F, self.prio)
        self.mw = G.assign(self.e, self.M, self.R, self.F, self.rm, self.prio, P=self.P)
        if G.COMBINE == "mean":
            self.mw = gls_mean(self, self.mw)
        sh = self.tab[self.tab.sd.notna()].set_index("member")["shift"].fillna(0.0)
        self.reg = pd.Series(G.first([(c, (self.W[c] + sh[c]).to_numpy()) for c in REG])[0], index=self.W.index)

    def variant(self, gcmt_first=False, old=G.OLD, mean=None, judge=None, last=False, lower=None, corr=True, **kw):
        ref = gcmt_first or lower is not None
        R = G.reference(self.M, gcmt_first, lower or G.LOWER)[0] if ref else self.R
        F = G.relations(self.M, R, self.e, quiet=True, boot=0, **kw) if (kw or ref) else self.F
        prio = [s for s in self.prio if s in F]
        if last:
            prio = sorted(prio, key=lambda s: bool(re.match(G.NOT_BELOW, s)))
        judge = judge or G.JUDGE
        P = G.proxies(self.e, self.M, F, prio, judge) if (F is not self.F or judge != G.JUDGE) else self.P
        mw = G.assign(self.e, self.M, R, F, self.rm, prio, old=old, P=P, judge=judge)
        mean = (G.COMBINE == "mean") if mean is None else mean
        return G.combine(self.e, R, F, P, prio, mw, corr) if mean else mw

    def pairs(self, sc):
        p = self.M[self.M.scale == sc].join(self.R, on="event_id", how="inner", rsuffix="_ref")
        return p.join(self.e.set_index("event_id")[["yr", "z"]], on="event_id").dropna(subset=["yr"])


def gls_mean(D, mw):
    return G.combine(D.e, D.R, D.F, D.P, D.prio, mw)


def others():
    """Cabello's own catalogue and Candia and Macedo (2026), cut to the box of our sources."""
    out = {}
    c = pd.read_csv(SRC / f"cabello_{FROZEN}_events.csv", usecols=["src_id", "time", "lat", "lon"], dtype={"src_id": str}).drop_duplicates("src_id")
    m = pd.read_csv(SRC / f"cabello_{FROZEN}_mags.csv", dtype={"src_id": str})
    c["mw"] = c.src_id.map(m[m.agency == "cabello"].drop_duplicates("src_id").set_index("src_id").mag)
    c["t"], c["cls"] = tsec(c.time), None
    c["yr"] = year(c.t)
    out["Cabello et al. (2025)"] = c
    f = CACHE / "candia_macedo.csv"
    if not f.exists() and XLSX.exists():
        CACHE.mkdir(exist_ok=True)
        read_xlsx(XLSX, f)
    if f.exists():
        c = pd.read_csv(f, low_memory=False)
        c = c[c.GK != 1].copy()
        c["t"] = tsec(c.time.str.replace("Z", ""))
        c["yr"] = year(c.t)
        c["cls"] = c.mech.map({"IF": "interface band", "SL": "in slab", "SC": "above slab, shallow"})
        out["Candia and Macedo (2026)"] = c
    box = lambda d: d[(d.lat >= BOX[0]) & (d.lat <= BOX[1]) & (d.lon >= BOX[2]) & (d.lon <= BOX[3])].reset_index(drop=True)
    return {k: box(v) for k, v in out.items()}


def read_xlsx(src, out, sheet="sheet2"):
    """The catalogue sheet of the Candia and Macedo supplement as csv (plain xml read; the file is 250 000 rows)."""
    N = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    z = zipfile.ZipFile(src)
    ss = []
    for _, el in ET.iterparse(z.open("xl/sharedStrings.xml")):
        if el.tag == N + "si":
            ss.append("".join(t.text or "" for t in el.iter(N + "t")))
            el.clear()
    col = lambda r: sum((ord(ch) - 64) * 26 ** i for i, ch in enumerate(reversed(re.match(r"[A-Z]+", r).group()))) - 1
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        for _, el in ET.iterparse(z.open(f"xl/worksheets/{sheet}.xml")):
            if el.tag == N + "row":
                row = {}
                for c in el.findall(N + "c"):
                    v = c.find(N + "v")
                    if v is None:
                        t = c.find(N + "is")
                        row[col(c.get("r"))] = "".join(x.text or "" for x in t.iter(N + "t")) if t is not None else ""
                    else:
                        row[col(c.get("r"))] = ss[int(v.text)] if c.get("t") == "s" else v.text
                if row:
                    w.writerow([row.get(i, "") for i in range(max(row) + 1)])
                el.clear()


# tests 4 to 6 and 9
def independent(D):
    """Test 4: converted value minus the regional Mw of the event (GUC Mwr, CSN web Mw, NEIC Mwr, shifted as in
    the reference) on pairs held out of the fit (time blocks, form and split of the chosen relation), per 0.25
    bin of the regional Mw."""
    rows = []
    for sc in MAIN:
        p, r = D.pairs(sc), D.F[sc]
        x, y, yr, z = (p[c].to_numpy(float) for c in ("mag", "y", "yr", "z"))
        o = np.argsort(yr, kind="stable")
        fo = np.empty(len(p), int)
        fo[o] = np.arange(len(p)) * G.NFOLD // len(p)
        g, sy = G.groups(r["split"], z, yr), float(np.sqrt(np.mean(p.sig ** 2)))
        conv = np.full(len(p), np.nan)
        for i in range(G.NFOLD):
            for q in np.unique(g):
                a, b = (fo != i) & (g == q), (fo == i) & (g == q)
                if a.sum() >= G.N_LINE and b.any():
                    conv[b] = G.conv(G.fit_inv(y[a], x[a], sy, r["form"]), x[b])[0]
        yr_ = p.event_id.map(D.reg).to_numpy(float)
        k = np.isfinite(yr_) & np.isfinite(conv)
        for lo, hi in zip(IND_BINS[:-1], IND_BINS[1:]):
            kb = k & (yr_ >= lo) & (yr_ < hi)
            med = float(np.median((conv - yr_)[kb])) if kb.sum() >= IND_N else np.nan
            use = lo >= IND_FROM - 1e-9 and np.isfinite(med)
            rows.append({"test": 4, "catalogue": "this study", "subset": sc, "quantity": f"median converted − regional Mw, {lo}–{hi} (n = {kb.sum()})",
                         "value": med, "limit": f"|.| <= {IND_TOL}" if use else None, "passed": bool(abs(med) <= IND_TOL) if use else None,
                         "lo": lo, "n": int(kb.sum())})
    return pd.DataFrame(rows)


def histogram(D, mw=None, name="this study"):
    """Test 5: events per 0.1 bin per period. Measure: each bin against the geometric mean g of its two
    neighbours (what a smooth distribution gives), z = (n - g) / sqrt(1.5 g) (Poisson error of n and of g); a
    comb or a heap shows as |z| above HIST_Z for bins from HIST_FROM."""
    m, yr = (D.mw if mw is None else mw).mw.to_numpy(float), D.e.yr.to_numpy()
    rows, H = [], {}
    for a, b in PER:
        n = np.array([((np.abs(m - q) < 1e-6) & (yr >= a) & (yr < b)).sum() for q in HIST])
        lab = f"{a}–{'today' if b > 2090 else b - 1}"
        H[lab] = n
        gm = np.sqrt(n[:-2] * n[2:])
        zz = (n[1:-1] - gm) / np.sqrt(1.5 * np.maximum(gm, 1))
        k = HIST[1:-1] >= HIST_FROM - 1e-9
        i = int(np.argmax(np.abs(zz[k])))
        rows.append({"test": 5, "catalogue": name, "subset": lab, "quantity": f"largest |z| of a bin against its neighbours, at {HIST[1:-1][k][i]:.1f}",
                     "value": float(np.abs(zz[k]).max()), "limit": f"<= {HIST_Z}", "passed": bool(np.abs(zz[k]).max() <= HIST_Z)})
        rows.append({"test": 5, "catalogue": name, "subset": lab, "quantity": "largest and smallest ratio of neighbouring bins n(m + 0.1) / n(m)",
                     "value": f"{(n[1:] / n[:-1])[HIST[:-1] >= HIST_FROM - 1e-9].max():.2f} / {(n[1:] / n[:-1])[HIST[:-1] >= HIST_FROM - 1e-9].min():.2f}"})
    return pd.DataFrame(rows), pd.DataFrame(H, index=HIST)


def old_period(D):
    """Test 6: ISC-GEM Mw against the first eligible converted scale on the same events of 1964–1975."""
    yr = D.e.yr.to_numpy()
    own = np.full(len(D.e), np.nan)
    for s in D.prio[::-1]:
        k = D.P[s].ok.to_numpy()
        own[k] = D.P[s].raw.to_numpy()[k]
    gem = D.e.event_id.map(D.M[D.M.scale == "ISC-GEM Mw"].set_index("event_id").mag).to_numpy(float)
    k = (yr >= OLD_PER[0]) & (yr < OLD_PER[1]) & np.isfinite(gem) & np.isfinite(own)
    rows = [{"test": 6, "catalogue": "this study", "subset": f"ISC-GEM {lo}–{lo + 0.5}", "quantity": f"median converted − ISC-GEM (n = {kb.sum()})",
             "value": float(np.median((own - gem)[kb])) if kb.sum() >= 10 else np.nan}
            for lo in (5.0, 5.5, 6.0, 6.5) for kb in [k & (gem >= lo) & (gem < lo + 0.5)]]
    return pd.DataFrame(rows), pd.DataFrame({"gem": gem[k], "own": own[k]})


def synthetic(seed=0):
    """
    Test 9: bias of the converted Mw of five regression methods on a Gutenberg–Richter population (b = 1) with
    native = a + b m + N(0, sx) and reference = m + N(0, sy).

    Cases: every event paired; pairs above a floor on the measured Mw; the same floor on the true size.
    Bias = converted Mw minus (native - a) / b at the native values SYN_X, mean over SYN['rep'] populations.
    """
    a, b, sx, sy = SYN["a"], SYN["b"], SYN["sx"], SYN["sy"]
    eta = sy ** 2 / sx ** 2
    fw = lambda x, y, e: G.fit_fwd(x, y, 1.0, np.sqrt(e))
    meth = {"forward least squares": lambda x, y: G.fit_fwd(x, y, 1.0, 1e3),
            "forward orthogonal (η = 1)": lambda x, y: fw(x, y, 1.0),
            "forward chi-square, correct η": lambda x, y: fw(x, y, eta),
            "forward chi-square, η × 2": lambda x, y: fw(x, y, 2 * eta),
            "forward chi-square, η / 2": lambda x, y: fw(x, y, eta / 2),
            "inverse, plain": lambda x, y: G.fit_inv(y, x, 0.0),
            "inverse, slope corrected": lambda x, y: G.fit_inv(y, x, sy)}
    g = np.random.default_rng(seed)
    acc = {}
    for _ in range(SYN["rep"]):
        m = SYN["m0"] + g.exponential(1 / np.log(10), SYN["n"])
        x, y = a + b * m + g.normal(0, sx, len(m)), m + g.normal(0, sy, len(m))
        u = g.random(len(m))
        sel = {"every event paired": np.ones(len(m), bool),
               f"reference above Mw {SYN['floor']} (measured)": u < 1 / (1 + np.exp(-(y - SYN["floor"]) / SYN["width"])),
               f"reference above Mw {SYN['floor']} (true size)": u < 1 / (1 + np.exp(-(m - SYN["floor"]) / SYN["width"]))}
        for case, k in sel.items():
            for nm, f in meth.items():
                acc.setdefault((case, nm), []).append(G.conv(f(x[k], y[k]), SYN_X)[0] - (SYN_X - a) / b)
    return pd.DataFrame([{"case": c, "method": nm, **{f"{v:.2f}": d for v, d in zip(SYN_X, np.mean(r, axis=0).round(3))}}
                         for (c, nm), r in acc.items()])


# figures
def new(nr, nc, w, h, **kw):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    palette.apply()
    return plt.subplots(nr, nc, figsize=(w, h), layout="constrained", squeeze=False, **kw)


def save(fig, name):
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)


C = palette.SERIES


def fig_offsets(D):
    fig, ax = new(1, 2, 14, 5.2, sharey=True)
    t = D.tab[D.tab.against == G.WFAM[0]]
    b = t[t.sd.isna() & (t.n >= G.NBIN)]
    names = {G.GC: "GCMT", "GUC Mwr": "CSN regional Mw", "CSN web Mw": "CSN Mw (web catalogue)", "NEIC Mwr": "USGS regional Mw",
             "GFZ Mw": "GFZ Mw", "CSN Mww": "CSN W-phase Mw"}
    for i, (c, lab) in enumerate(names.items()):
        x = b[b.member == c]
        ax[0, 0].errorbar((x.lo + x.hi) / 2 + 0.012 * (i - 2.5), x["mean"], 2 * x.se, color=C[i], marker="o", ms=5, lw=1.4, capsize=2,
                          label=f"{lab} ({int(t[(t.member == c) & t.sd.notna()].n.iloc[0])} events)")
    ax[0, 0].axhline(0, color="0.5", lw=0.8)
    ax[0, 0].axvline(G.M_HI, color="0.5", lw=0.8, ls="--")
    ax[0, 0].set_xlabel("mean of the two Mw")
    ax[0, 0].set_ylabel("Mw of the catalogue − USGS W-phase Mw")
    ax[0, 0].set_title("Each measured Mw against the USGS W-phase Mw")
    ax[0, 0].legend(ncol=2, loc="upper right")
    g = D.W[G.GC].to_numpy()
    comp = D.e.event_id.map(D.R.y[D.R.scale != G.GC]).reindex(D.e.index)
    w = D.W.join(D.R[D.R.scale != G.GC].y.rename("w"), how="inner")[[G.GC, "w"]].dropna()
    for lo, hi in zip(np.arange(4.75, 6.49, 0.25), np.arange(5.0, 6.51, 0.25)):
        k = (w[G.GC] >= lo) & (w[G.GC] < hi)
        if k.sum() >= G.NBIN:
            d = (w[G.GC] - w.w)[k]
            ax[0, 1].errorbar((lo + hi) / 2, d.mean(), 2 * d.std() / np.sqrt(len(d)), color=C[0], marker="o", ms=6, capsize=2)
            ax[0, 1].text((lo + hi) / 2, d.mean() + 2 * d.std() / np.sqrt(len(d)) + 0.008, f"{len(d)}", ha="center", fontsize=9, color="0.4")
    r = D.tab[D.tab.against.str.contains("line in")]
    if len(r):
        x = np.linspace(4.75, G.M_HI, 50)
        ax[0, 1].plot(x, np.clip(r["mean"].iloc[0] + r["shift"].iloc[0] * (x - r.lo.iloc[0]), 0, None), color=C[1], lw=2,
                      label="correction applied to a GCMT value that stands alone")
        ax[0, 1].legend(loc="lower left")
    ax[0, 1].axhline(0, color="0.5", lw=0.8)
    ax[0, 1].axvline(G.M_HI, color="0.5", lw=0.8, ls="--")
    ax[0, 1].text(G.M_HI, 0.97, " GCMT first from 5.4", transform=ax[0, 1].get_xaxis_transform(), va="top", fontsize=10)
    ax[0, 1].set_xlabel("GCMT Mw")
    ax[0, 1].set_title("GCMT against the other measured Mw, after their shifts")
    save(fig, "offsets")


def draw_rel(a, f, c, lw=2.2, ls="-", lab=None, lo=3.5, hi=7.5):
    y = np.linspace(lo, hi, 200)
    a.plot(G.pl(f["p"], y), y, color=c, lw=lw, ls=ls, label=lab)


def fig_relations(D):
    fig, ax = new(2, 3, 14, 9.5, sharex=True, sharey=True)
    for a, sc in zip(ax.ravel(), MAIN):
        p, r = D.pairs(sc), D.F[sc]
        x, y, yr, z = (p[c].to_numpy(float) for c in ("mag", "y", "yr", "z"))
        g = G.groups(r["split"], z, yr)
        sy = float(np.sqrt(np.mean(p.sig ** 2)))
        a.plot([3, 8], [3, 8], color="0.6", lw=0.9, ls=":")
        for i, q in enumerate(np.unique(g)):
            a.scatter(x[g == q], y[g == q], s=3, color=C[i], alpha=0.12, lw=0, rasterized=True)
        for form, ls in (("linear", "--"), ("hinge", "-.")):
            if (form, "none") != (r["form"], r["split"]):
                draw_rel(a, G.fit_inv(y, x, sy, form), "0.35", 1.0, ls, f"not chosen: {'straight line' if form == 'linear' else 'line with bend'}, no split")
        for i, (q, f) in enumerate(r["parts"].items()):
            draw_rel(a, f, C[i], lab="chosen" + ("" if q == "all" else f": {q}"))
        a.set_title(f"{NAME.get(sc, sc)} ({len(p):,} pairs)")
        a.legend(loc="upper left", fontsize=8.5)
        a.set_xlim(3.4, 7.6)
        a.set_ylim(3.4, 8.0)
    for a in ax[-1]:
        a.set_xlabel("native magnitude")
    for a in ax[:, 0]:
        a.set_ylabel("reference Mw")
    fig.suptitle("Conversion relations of the main scales: native magnitude regressed on the reference Mw and inverted", x=0.01, ha="left")
    save(fig, "relations")


def fig_forward(D):
    fig, ax = new(2, len(FWD_FIG), 15, 10, sharex=True, sharey=True)
    for j, sc in enumerate(FWD_FIG):
        p, r = D.pairs(sc), D.F[sc]
        x, y, yr, z = (p[c].to_numpy(float) for c in ("mag", "y", "yr", "z"))
        g = G.groups(r["split"], z, yr)
        sy = float(np.sqrt(np.mean(p.sig ** 2)))
        for i in range(2):
            a = ax[i, j]
            qs = list(r["parts"])
            if i >= len(qs):
                a.set_visible(False)
                ax[0, j].set_xlabel("native magnitude")
                ax[0, j].tick_params(labelbottom=True)
                continue
            k, f = g == qs[i], r["parts"][qs[i]]
            a.scatter(x[k], y[k], s=4, color="0.45", alpha=0.15, lw=0, rasterized=True)
            a.plot([3, 8], [3, 8], color="0.5", lw=1.0, ls=":", label="1:1")
            fw = G.fit_fwd(x[k], y[k], np.sqrt(max(f["s"] ** 2 - (f["p"][1] * sy) ** 2, 0.05 ** 2)), sy)
            draw_rel(a, fw, C[1], lab="forward chi-square fit (Mw on native)")
            draw_rel(a, f, C[0], lab="chosen inverse fit (native on Mw, inverted)")
            v = np.array([4.5])
            a.set_title(f"{NAME.get(sc, sc)}{'' if qs[i] == 'all' else ', ' + qs[i] + (' (≤ 50 km)' if qs[i] == 'shallow' else ' (> 50 km)' if qs[i] == 'deep' else '')}"
                        f" ({k.sum():,} pairs)\nMw at native 4.5: forward {G.conv(fw, v)[0][0]:.2f}, inverse {G.conv(f, v)[0][0]:.2f}")
            a.set_xlim(3.4, 7.2)
            a.set_ylim(3.4, 7.6)
            if i == len(qs) - 1:
                a.set_xlabel("native magnitude")
            if j == 0:
                a.set_ylabel("reference Mw")
    ax[0, 0].legend(loc="upper left")
    fig.suptitle("Forward chi-square fit and the chosen inverse fit on the same pairs", x=0.01, ha="left")
    save(fig, "forward_inverse")


def coverage(D):
    """Share of the events with a native value of a main scale that have a reference Mw, per 0.1 native bin."""
    has = D.e.event_id.isin(D.R.index).to_numpy()
    yr = D.e.yr.to_numpy()
    rows = []
    for sc in MAIN:
        x = D.P[sc].x.to_numpy()
        for lab, k in (("1976 to today", yr >= 1976), ("2011 to today", yr >= 2011)):
            b = np.round(x[k & np.isfinite(x)] + 1e-9, 1)
            h = has[k & np.isfinite(x)]
            for q in np.round(np.arange(3.5, 6.51, 0.1), 1):
                kb = np.abs(b - q) < 1e-6
                rows.append({"scale": sc, "period": lab, "native": q, "n": int(kb.sum()), "share": float(h[kb].mean()) if kb.sum() >= 10 else np.nan})
    return pd.DataFrame(rows)


def fig_coverage(cov):
    fig, ax = new(1, 2, 14, 5.4, sharey=True)
    for a, (lab, g) in zip(ax[0], cov.groupby("period")):
        for i, sc in enumerate(MAIN):
            x = g[g.scale == sc]
            a.plot(x.native, x.share, color=C[i], lw=1.8, marker="o", ms=3, label=NAME.get(sc, sc))
        a.set_title(f"Events with a measured Mw, by native magnitude ({lab})")
        a.set_xlabel("native magnitude (0.1 bins)")
        a.set_ylim(0, 1.02)
    ax[0, 0].set_ylabel("share of events with a reference Mw")
    ax[0, 0].legend(ncol=2, loc="upper left")
    save(fig, "coverage")


def fig_b(T, names, file, title):
    fig, ax = new(1, 4, 17, 4.6, sharey=True)
    subs = [f"{lab}, {tag}" for _, lab in B_PER for tag in ("full", "declustered")]
    for a, s in zip(ax[0], subs):
        for i, nm in enumerate(names):
            x = T[(T.test == 1) & (T.catalogue == nm) & (T.subset == s) & T.quantity.str.startswith("b at")]
            a.plot(SHOW, x.value.astype(float), color=C[i], lw=2.4 if i == 0 else 1.5, label=nm)
        a.axvspan(FLOORS[0], FLOORS[-1], color="0.95", lw=0)
        a.axhline(1.0, color="0.6", lw=0.7)
        a.set_title(s)
        a.set_xlabel("lowest magnitude fitted")
        a.set_ylim(0.5, 1.8)
    ax[0, 0].set_ylabel("b")
    ax[0, -1].legend(loc="upper right")
    fig.suptitle(title, x=0.01, ha="left")
    save(fig, file)


def rate_axis(a, T, names, q):
    lab = [f"{x}–{'today' if y > 2090 else y - 1}" for x, y in PER]
    for i, nm in enumerate(names):
        x = T[(T.test == 2) & (T.catalogue == nm) & T.quantity.str.startswith(f"rate M >= {q},") & ~T.quantity.str.contains("departure")]
        a.plot(range(len(lab)), x.value.astype(float), color=C[i], lw=2.4 if i == 0 else 1.5, marker="o", label=nm)
        if i == 0:
            v = x.value.astype(float).mean()
            a.axhspan(v * (1 - RATE_TOL), v * (1 + RATE_TOL), color="0.93", lw=0)
    a.set_xticks(range(len(lab)), lab)
    a.set_ylabel("events per year (declustered)")
    a.set_title(f"Rate of M ≥ {q}")
    a.set_ylim(0, None)


def large_axis(a, T, names, q="N >= 7"):
    k = 0
    ticks = []
    for i, nm in enumerate(names):
        for tag in ("full", "declustered"):
            for lo in FIT_LO:
                s = f"all, {tag}, fit from {lo}"
                x = T[(T.test == 3) & (T.catalogue == nm) & (T.subset == s)].set_index("quantity").value
                obs, pred = float(x[f"{q} observed"]), float(x[f"{q} predicted"])
                l, h = band(int(obs))
                a.plot([k, k], [l / obs, h / obs], color="0.75", lw=6, solid_capstyle="butt")
                a.plot(k, pred / obs, "o" if tag == "full" else "s", color=C[i], ms=8)
                ticks.append(f"{lo}\n{'all' if tag == 'full' else 'decl.'}")
                k += 1
        k += 0.6
    a.axhline(1, color="0.4", lw=0.8)
    a.set_xticks([t for i in range(len(names)) for t in np.arange(4) + i * 4.6], ticks, fontsize=9)
    a.set_ylabel("predicted / observed")
    a.set_ylim(0, 1.8)


def fig_tests(D, T, H, G6, ind):
    own = ["this study"]
    fig_b(T, own, "test1_b_floor", "Test 1: b against the lowest magnitude fitted (grey: the range that must stay within 0.2)")
    fig, ax = new(1, 2, 12, 4.6)
    for a, q in zip(ax[0], RATE_M):
        rate_axis(a, T, own, q)
    x = T[(T.test == 6) & T.quantity.str.startswith("rate")]
    for a, q in zip(ax[0], RATE_M):
        v = float(x[x.quantity.str.startswith(f"rate M >= {q}")].value.iloc[0])
        a.plot(-1, v, "D", color=C[3], ms=8)
        a.set_xticks(range(-1, len(PER)), [f"{OLD_PER[0]}–{OLD_PER[1] - 1}"] + [t.get_text() for t in a.get_xticklabels()])
    fig.suptitle("Test 2: declustered rates per period (grey: ± 15 % of the mean of 1976 to today; diamond: 1964–1975, test 6)", x=0.01, ha="left")
    save(fig, "test2_rates")
    fig, ax = new(1, 2, 15, 5.2, sharey=True)
    for a, q in zip(ax[0], ("N 6.5–7", "N >= 7")):
        k = 0
        lab = []
        for i, fam in enumerate(FAMS):
            for tag in ("full", "declustered"):
                for lo in FIT_LO:
                    x = T[(T.test == 3) & (T.catalogue == "this study") & (T.subset == f"{fam}, {tag}, fit from {lo}")].set_index("quantity").value
                    obs, pred = float(x[f"{q} observed"]), float(x[f"{q} predicted"])
                    l, h = band(int(obs))
                    a.plot([k, k], [l, h], color="0.78", lw=7, solid_capstyle="butt")
                    a.plot([k - 0.3, k + 0.3], [obs, obs], color="0.2", lw=1.5)
                    a.plot(k, pred, "o" if tag == "full" else "s", color=C[i], ms=8)
                    lab.append(f"{lo}\n{'all' if tag == 'full' else 'decl.'}")
                    k += 1
            a.text(k - 2.5, 0.97, fam, transform=a.get_xaxis_transform(), ha="center", va="top")
            k += 0.6
        a.set_xticks([t for i in range(len(FAMS)) for t in np.arange(4) + i * 4.6], lab, fontsize=9)
        a.set_yscale("log")
        a.set_title(f"Mw {'6.5–7.0' if q == 'N 6.5–7' else '≥ 7'}")
    ax[0, 0].set_ylabel("events, 1976 to today")
    fig.suptitle("Test 3: Gutenberg–Richter law fitted on Mw 5.0 (5.3) to 6.5 and extended to the large events: predicted (symbols), "
                 "observed (line) and the Poisson band of the observed count", x=0.01, ha="left")
    save(fig, "test3_large_events")
    fig, ax = new(1, 1, 9, 5)
    for i, sc in enumerate(MAIN):
        x = ind[(ind.subset == sc) & (ind.n >= IND_N)]
        ax[0, 0].plot(x.lo + 0.125, x.value, color=C[i], marker="o", lw=1.6, label=NAME.get(sc, sc))
    ax[0, 0].axhspan(-IND_TOL, IND_TOL, color="0.94", lw=0)
    ax[0, 0].axvline(IND_FROM, color="0.5", lw=0.8, ls="--")
    ax[0, 0].axhline(0, color="0.5", lw=0.8)
    ax[0, 0].set_xlabel("regional Mw")
    ax[0, 0].set_ylabel("converted Mw − regional Mw (median)")
    ax[0, 0].set_title("Test 4: converted values against regional Mw on events held out of the fit")
    ax[0, 0].legend(ncol=2)
    save(fig, "test4_independent")
    fig, ax = new(1, len(PER), 17, 4.4)
    for a, c in zip(ax[0], H.columns):
        a.bar(H.index, H[c], width=0.085, color=C[0])
        a.set_yscale("log")
        a.set_title(c)
        a.set_xlabel("Mw (0.1 bins)")
    ax[0, 0].set_ylabel("events")
    fig.suptitle("Test 5: events per 0.1 bin of Mw", x=0.01, ha="left")
    save(fig, "test5_histogram")
    fig, ax = new(1, 1, 6.5, 6)
    ax[0, 0].scatter(G6.gem, G6.own, s=12, color=C[0], alpha=0.5, lw=0)
    ax[0, 0].plot([4.8, 8], [4.8, 8], color="0.5", lw=0.9, ls=":")
    ax[0, 0].set_xlabel("ISC-GEM Mw")
    ax[0, 0].set_ylabel("Mw converted with our relations")
    ax[0, 0].set_title(f"Test 6: {OLD_PER[0]}–{OLD_PER[1] - 1}, the same events ({len(G6)})")
    save(fig, "test6_1964_1975")


def fig_compare(T, names):
    fig, ax = new(1, 4, 19, 5)
    for i, nm in enumerate(names):
        x = T[(T.test == 1) & (T.catalogue == nm) & (T.subset == "2011 to today, declustered") & T.quantity.str.startswith("b at")]
        ax[0, 0].plot(SHOW, x.value.astype(float), color=C[i], lw=2.4 if i == 0 else 1.6, label=nm)
    ax[0, 0].axhline(1, color="0.6", lw=0.7)
    ax[0, 0].set_xlabel("lowest magnitude fitted")
    ax[0, 0].set_ylabel("b (2011 to today, declustered)")
    ax[0, 0].set_title("b against the fit floor")
    ax[0, 0].set_ylim(0.5, 1.8)
    ax[0, 0].legend()
    rate_axis(ax[0, 1], T, names, 5.0)
    rate_axis(ax[0, 2], T, names, 5.5)
    large_axis(ax[0, 3], T, names)
    ax[0, 3].set_title("M ≥ 7 since 1976: predicted from Mw 5.0 (5.3)–6.5 over observed")
    save(fig, "test7_comparison")


def fig_synthetic(S):
    cases = list(dict.fromkeys(S.case))
    fig, ax = new(1, len(cases), 17, 5.2, sharey=True)
    x = [float(c) for c in S.columns[2:]]
    for a, case in zip(ax[0], cases):
        for i, (_, r) in enumerate(S[S.case == case].iterrows()):
            a.plot(x, r.iloc[2:].astype(float), color=C[i], lw=2.4 if "inverse" in r.method else 1.4,
                   ls="--" if "η ×" in r.method or "η /" in r.method else "-", label=r.method)
        a.axhline(0, color="0.5", lw=0.8)
        a.set_title(case)
        a.set_xlabel("native magnitude")
        a.set_ylim(-0.3, 0.6)
    ax[0, 0].set_ylabel("converted Mw − true relation")
    ax[0, 0].legend(loc="upper right", fontsize=9)
    fig.suptitle("Test 9: bias of the converted Mw on a synthetic Gutenberg–Richter population (b = 1, native σ 0.20, reference σ 0.08)",
                 x=0.01, ha="left")
    save(fig, "test9_synthetic")


def main():
    D = Data()
    c = D.e[["t", "yr", "lat", "lon", "cls"]]
    T, dep = tests123("this study", D.mw.mw, c, D.t_end)
    ind = independent(D)
    T5, H = histogram(D)
    T6, G6 = old_period(D)
    oth = others()
    T7 = [tests123(k, v.mw, v, D.t_end)[0] for k, v in oth.items()]
    if "Candia and Macedo (2026)" not in oth:
        print("Candia and Macedo supplement not on disk: comparison skipped")
    var = {"(a) GCMT first at all magnitudes": dict(gcmt_first=True),
           "(b) weighted mean of the converted scales, with their correlations": dict(mean=True),
           "(b) inverse-variance mean of the converted scales": dict(mean=True, corr=False),
           "(c) straight lines only": dict(forms=("linear",)),
           "(d) Centennial before ISC-GEM": dict(old=G.OLD[::-1]),
           "(e) no slope correction": dict(sy=0.0), "(e) slope correction with σ 0.15": dict(sy=0.15),
           "(f) forward chi-square regression": dict(method="fwd"),
           "(g) surface-wave scales only where their own value reaches Mw 5": dict(judge="own"),
           "(g) surface-wave scales only where another scale reaches Mw 5": dict(judge="other"),
           "(i) GCMT below 5.4 lowered by one step per bin": dict(lower="step"),
           "(i) GCMT below 5.4 not lowered": dict(lower="none"),
           "(h) those scales after all others": dict(last=True)}
    T8, hz = [], {"this study": T5}
    for k, kw in var.items():
        v = D.variant(**kw)
        T8.append(tests123(k, v.mw, c, D.t_end)[0])
        hz[k] = histogram(D, v, k)[0]
        print("variant", k, flush=True)
    T8 = pd.concat(T8, ignore_index=True)
    S = synthetic()
    cov = coverage(D)
    allT = pd.concat([T, ind.drop(columns=["lo", "n"]), T5, T6] + T7 + [T8.assign(test=8)], ignore_index=True)
    allT["value"] = [round(v, 4) if isinstance(v, float) else v for v in allT.value]
    sens = pd.DataFrame([headline(T, "this study")] + [headline(T8, k) for k in var] + [headline(x, k) for x, k in zip(T7, oth)])
    files = {OUT / f"mw_tests_{RUN}.csv": allT, OUT / f"mw_sensitivity_{RUN}.csv": sens, OUT / f"mw_synthetic_{RUN}.csv": S,
             OUT / f"mw_histogram_{RUN}.csv": H.reset_index(names="mw"), OUT / f"mw_coverage_{RUN}.csv": cov}
    z = {k: v[v.passed.notna()] for k, v in hz.items()}
    sens["histogram, largest |z|"] = sens.catalogue.map({k: f"{v.value.max():.1f} ({v.subset[v.value.idxmax()]})" for k, v in z.items()})
    for f, d in files.items():
        d.to_csv(f, index=False)
    G.manifest(files)
    fig_offsets(D)
    fig_relations(D)
    fig_forward(D)
    fig_coverage(cov)
    fig_tests(D, allT, H, G6, ind)
    fig_compare(allT, ["this study"] + list(oth))
    fig_synthetic(S)
    pd.set_option("display.width", 250, "display.max_columns", 40, "display.max_rows", 400, "display.max_colwidth", 90)
    print(sens.T.to_string())
    p = allT[allT.passed.notna() & (allT.catalogue == "this study") & (allT.test != 8)]
    print(p.groupby("test").passed.agg(lambda v: f"{int(v.astype(bool).sum())} of {len(v)} pass").to_string())
    print(p[~p.passed.astype(bool)][["test", "subset", "quantity", "value", "limit"]].to_string())
    print(S.to_string())
    print(T6.to_string())


if __name__ == "__main__":
    main()
