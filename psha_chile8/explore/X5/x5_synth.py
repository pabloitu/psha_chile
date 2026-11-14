"""X5: synthetic catalogues with known classes, built on the real events over the shallow slab (their slab tops, depth
errors, Slab2 uncertainties and which of them have a mechanism), to see what each scoring model recovers."""
import numpy as np

# true shares of interface, in-slab, crustal; interface half-thickness; in-slab depth scale below the surface
SHARES, IF_SD, SLAB_SCALE, SLAB_MIN, CRUST_MIN = (0.60, 0.30, 0.10), 2.0, 12.0, 2.0, 2.0
# share of thrust-like mechanisms (Kagan angle up to 30°) among interface events
THRUST_IF = 0.88
# scenarios: factor on the depth and slab errors, share of thrust-like mechanisms among in-slab and crustal events
SCEN = {"errors as catalogued": (1.0, 0.15), "errors 0.7 of the catalogued": (0.7, 0.15), "more in-slab and crustal thrusts (30 %)": (1.0, 0.30)}


def make(x, err=1.0, thrust_other=0.15, seed=0):
    """
    Synthetic copy of the events x (rows of geometry over the shallow slab with a measured depth).

    The true slab top is the Slab2 value; the true class is drawn from SHARES; the true position is on the surface
    (interface), below it (in-slab) or above it (crustal). The catalogue then sees the slab with an error of
    err × the Slab2 uncertainty and the depth with an error of err × the event's σ. Events that have a mechanism in
    the real catalogue get one: thrust-like with probability THRUST_IF if interface and thrust_other otherwise, the
    mechanism (Kagan angle and skewed measure) taken from a real event of that kind.

    Returns the frame (same columns as x) and the true class (0 interface, 1 in-slab, 2 crustal).
    """
    r = np.random.default_rng(seed)
    n = len(x)
    top, sig, unc = x.top.to_numpy(float), x.sig.to_numpy(float), np.nan_to_num(x.unc.to_numpy(float), nan=12.0)
    c = r.choice(3, n, p=SHARES)
    d = np.select([c == 0, c == 1], [r.normal(0, IF_SD, n), SLAB_MIN + r.exponential(SLAB_SCALE, n)],
                  -r.uniform(CRUST_MIN, np.maximum(top, CRUST_MIN + 1)))
    z = np.maximum(top + d, 0.5)
    top_o = np.maximum(top + r.normal(0, err * unc), 1.0)
    z_o = np.maximum(z + r.normal(0, err * sig), 0.0)
    kr = x.kag.to_numpy(float)
    has = np.isfinite(kr)
    lo, hi = np.flatnonzero(has & (kr <= 30)), np.flatnonzero(has & (kr > 30))
    th = r.random(n) < np.where(c == 0, THRUST_IF, thrust_other)
    i = np.where(th, r.choice(lo, n), r.choice(hi, n))
    kag = np.where(has, kr[i], np.nan)
    y = x.copy()
    y["z"], y["top"], y["d"], y["kag"], y["hint"], y["known"] = z_o, top_o, z_o - top_o, kag, None, True
    for q in ("em", "sw", "tw"):
        y[q] = np.where(has, x[q].to_numpy(float)[i], np.nan)
    y["mech_kind"] = np.where(has, np.where(kag <= 30, "thrust", "other"), "none")
    return y, c
