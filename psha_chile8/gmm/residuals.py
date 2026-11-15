"""GMM evaluation and residuals (task GM1, step 3): total, between- and within-event residuals in ln units, τ and φ
estimated from the data, trends against Mw, Rrup, depth and Vs30."""
import numpy as np
import pandas as pd

from scores import mde

IMT_PERIOD = {"PGA": 0.0, "SA(0.2)": 0.2, "SA(1.0)": 1.0}
# record-table column for each context field OpenQuake may ask for
FIELD = {"mag": "mw", "rake": "rake", "dip": "dip", "ztor": "ztor", "width": "width", "hypo_depth": "hypo_depth",
         "hypo_lat": "hypo_lat", "hypo_lon": "hypo_lon", "rrup": "rrup", "rjb": "rjb", "rhypo": "rhypo",
         "repi": "repi", "rvolc": "rvolc", "vs30": "vs30", "vs30measured": "vs30measured", "backarc": "backarc",
         "soiltype": "soiltype", "lon": "sta_lon", "lat": "sta_lat", "z1pt0": None, "z2pt5": None}


def gsim(s):
    from openquake.hazardlib import valid
    return valid.gsim(s)


def usable(g, d):
    """Records a GMM can be evaluated on: Idini et al. (2017) needs a soil type."""
    return (d.soiltype > 0).to_numpy() if "soiltype" in g.REQUIRES_SITES_PARAMETERS else np.ones(len(d), bool)


def evaluate(g, d, imts):
    """Median (ln g), total σ, τ and φ of GMM g on the records d, arrays of shape (len(imts), len(d)).
    One context holds all records; each event is one rupture."""
    from openquake.hazardlib.contexts import simple_cmaker
    cm = simple_cmaker([g], list(imts))
    ctx = cm.new_ctx(len(d))
    for k in ctx.dtype.names:
        if k in ("src_id", "occurrence_rate"):
            continue
        if k == "sids":
            ctx[k] = np.arange(len(d))
        elif k == "rup_id":
            ctx[k] = pd.factorize(d.event_id)[0]
        elif k in ("z1pt0", "z2pt5"):
            ctx[k] = -999.0
        elif k in FIELD:
            ctx[k] = d[FIELD[k]].to_numpy()
        else:
            raise KeyError(f"{g.__class__.__name__} needs {k}")
    ms = cm.get_mean_stds([ctx])[:, 0]
    return ms[0], ms[1], ms[2], ms[3]


def split(r, ev, tau, phi):
    """Between- and within-event residuals with the model's τ and φ (Abrahamson & Youngs 1992):
    δB_e = τ² Σr / (n τ² + φ²), δW = r − δB_e. τ² and φ² are the event means of the record values."""
    f = pd.DataFrame({"e": ev, "r": r, "t2": tau ** 2, "p2": phi ** 2})
    g = f.groupby("e").agg(s=("r", "sum"), n=("r", "size"), t2=("t2", "mean"), p2=("p2", "mean"))
    g["db"] = g.t2 * g.s / (g.n * g.t2 + g.p2)
    db = f.e.map(g.db).to_numpy()
    return db, r - db, g


def mixed(r, ev):
    """Random intercept per event fitted by maximum likelihood: bias c, τ and φ of the data.
    Closed-form likelihood of the one-way model, maximised over (τ, φ) with c profiled out."""
    from scipy.optimize import minimize
    f = pd.DataFrame({"e": ev, "r": r})
    g = f.groupby("e").r
    n, s, ss = g.size().to_numpy(float), g.sum().to_numpy(), g.apply(lambda x: (x ** 2).sum()).to_numpy()
    N = n.sum()

    def nll(p, out=False):
        t2, p2 = np.exp(2 * p)
        w = n / (p2 + n * t2)
        c = (w * s / n).sum() / w.sum()
        sc, ssc = s - n * c, ss - 2 * c * s + n * c ** 2
        q = (ssc - t2 * sc ** 2 / (p2 + n * t2)) / p2
        ll = -0.5 * ((N - len(n)) * np.log(p2) + np.log(p2 + n * t2).sum() + q.sum() + N * np.log(2 * np.pi))
        return (c, np.sqrt(t2), np.sqrt(p2)) if out else -ll

    x = minimize(nll, np.log([0.4, 0.6]), method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-8)).x
    return nll(x, out=True)


def binned(x, y, edges):
    """Mean of y and its standard error per bin of x; slope of a straight line with its standard error."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    b = np.digitize(x, edges) - 1
    rows = []
    for k in range(len(edges) - 1):
        v = y[b == k]
        if len(v) >= 3:
            rows.append(dict(lo=edges[k], hi=edges[k + 1], x=x[b == k].mean(), mean=v.mean(),
                             se=v.std(ddof=1) / np.sqrt(len(v)), n=len(v)))
    A = np.c_[np.ones(len(x)), x]
    c, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    s2 = ((y - A @ c) ** 2).sum() / max(len(x) - 2, 1)
    se = np.sqrt(s2 * np.linalg.inv(A.T @ A)[1, 1])
    return pd.DataFrame(rows), c[1], se


def residuals(d, cands, imts):
    """Residuals of every candidate GMM on the records d of one class, long format: one row per record, GMM and
    intensity measure; records where the measure is not usable or the GMM cannot be evaluated are left out."""
    out = []
    for key, name, s in cands:
        g = gsim(s)
        ok = usable(g, d)
        dd = d[ok]
        mu, sig, tau, phi = evaluate(g, dd, imts)
        for m, imt in enumerate(imts):
            obs = np.log(dd[imt].to_numpy())
            use = np.isfinite(obs) & np.isfinite(mu[m])
            r = obs[use] - mu[m][use]
            f = pd.DataFrame({"record_id": dd.record_id.to_numpy()[use], "event_id": dd.event_id.to_numpy()[use],
                              "gmm": key, "imt": imt, "obs": obs[use], "mu": mu[m][use], "sig": sig[m][use],
                              "tau": tau[m][use], "phi": phi[m][use], "r": r})
            f["z"] = f.r / f.sig
            f["mde"] = mde(f.obs.to_numpy(), f.mu.to_numpy(), f.sig.to_numpy())
            if (f.tau > 0).all():
                db, dw, _ = split(f.r.to_numpy(), f.event_id.to_numpy(), f.tau.to_numpy(), f.phi.to_numpy())
                f["db"], f["dw"] = db, dw
                f["zb"], f["zw"] = db / f.tau, dw / f.phi
            else:
                f["db"] = f["dw"] = f["zb"] = f["zw"] = np.nan
            out.append(f)
    return pd.concat(out, ignore_index=True)


def summary(res):
    """N, mean and σ of z, bias, model and data τ and φ per GMM and intensity measure."""
    rows = []
    for (k, imt), f in res.groupby(["gmm", "imt"], sort=False):
        c, t, p = mixed(f.r.to_numpy(), f.event_id.to_numpy())
        rows.append(dict(gmm=k, imt=imt, n_rec=len(f), n_ev=f.event_id.nunique(), z_mean=f.z.mean(),
                         z_sd=f.z.std(), bias=f.r.mean(), bias_ml=c, sig_model=np.sqrt((f.sig ** 2).mean()),
                         tau_model=np.sqrt((f.tau ** 2).mean()) if (f.tau > 0).all() else np.nan,
                         phi_model=np.sqrt((f.phi ** 2).mean()) if (f.tau > 0).all() else np.nan,
                         tau_data=t, phi_data=p, sig_data=np.hypot(t, p)))
    return pd.DataFrame(rows)


TREND = {"mw": np.arange(5.0, 9.01, 0.5), "hypo_depth": np.array([0, 20, 40, 60, 80, 100, 125, 150, 200]),
         "rrup": np.array([0, 25, 50, 75, 100, 150, 200, 250, 300]),
         "vs30": np.array([100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2500])}


def trends(res, d):
    """Binned means and slopes: event terms (δB, or the event mean of r) against Mw and depth, δW (or r) against
    Rrup and Vs30."""
    rows, bins = [], []
    rec = d.set_index("record_id")
    for (k, imt), f in res.groupby(["gmm", "imt"], sort=False):
        f = f.join(rec[["mw", "hypo_depth", "rrup", "vs30"]], on="record_id")
        split_ok = f.db.notna().all()
        ev = f.groupby("event_id").agg(mw=("mw", "first"), hypo_depth=("hypo_depth", "first"),
                                       y=("db" if split_ok else "r", "first" if split_ok else "mean"))
        w = f.dw if split_ok else f.r
        for x, xs, ys, lab in [("mw", ev.mw, ev.y, "event"), ("hypo_depth", ev.hypo_depth, ev.y, "event"),
                               ("rrup", f.rrup, w, "within"), ("vs30", f.vs30, w, "within")]:
            b, s, se = binned(xs, ys, TREND[x])
            rows.append(dict(gmm=k, imt=imt, x=x, term=("δB" if split_ok else "event mean r") if lab == "event"
                             else ("δW" if split_ok else "r"), slope=s, slope_se=se, n=len(ys)))
            bins.append(b.assign(gmm=k, imt=imt, var=x))
    return pd.DataFrame(rows), pd.concat(bins, ignore_index=True)
