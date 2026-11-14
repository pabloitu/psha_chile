"""X5: how the Kagan angle to a thrust on the Slab2 plane grows when one parameter of the mechanism moves away."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import x5_lib as X

sys.path.insert(0, str(X.ROOT))
from palette import CLASS_COLOR  # noqa: E402

S, D, R = 10.0, 20.0, 90.0
CUT = 35.0
OUT = Path(__file__).parent / "figs" / "scheme_kagan.png"
# name, strike, dip, rake
EX = [("conjugate plane", 190, 70, 90), ("oblique slip, rake 110", 10, 20, 110), ("dip 45 instead of 20", 10, 45, 90),
      ("strike 30° off", 40, 20, 90), ("steep thrust, dip 60", 10, 60, 90), ("backthrust", 190, 20, 90),
      ("steep normal, dip 60", 10, 60, -90), ("normal on the slab plane", 10, 20, -90), ("strike-slip", 10, 90, 0)]


def kag(s, d, r):
    s, d, r = (np.atleast_1d(np.asarray(v, float)) for v in (s, d, r))
    n = max(len(s), len(d), len(r))
    s, d, r = (np.broadcast_to(v, n) for v in (s, d, r))
    return X.kagan(s, d, r, np.full(n, S), np.full(n, D), np.full(n, R))


def main():
    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, ax = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1.1, 1.0]})

    a = ax[0]
    x = np.linspace(0, 90, 181)
    a.plot(x, kag(S, D, R + x), color="#08306b", lw=6, alpha=0.5, label="rake turned away from 90°")
    a.plot(x[x <= 70], kag(S, D + x[x <= 70], R), color=CLASS_COLOR["intraslab_shallow"], lw=3, ls="--", label="dip steeper than Slab2")
    a.plot(x, kag(S + x, D, R), color=CLASS_COLOR["forearc"], lw=2, ls=":", label="strike turned away from Slab2")
    a.plot(x[x <= 70], kag(S + x[x <= 70], D + x[x <= 70], R + x[x <= 70]), color="k", lw=2,
           label="all three turned together")
    a.axhline(CUT, color="k", ls="--", lw=1.2)
    a.text(1, CUT + 1.5, f"cut {CUT:.0f}°: below, interface possible", fontsize=10)
    a.set(xlim=(0, 90), ylim=(0, 120), xlabel="Change (°)", ylabel="Kagan angle to the interface thrust (°)",
          title="1. Each degree of change counts once")
    a.legend(loc="upper left", frameon=False, fontsize=10, bbox_to_anchor=(0, 0.93))

    a = ax[1]
    v = np.array([kag(s, d, r)[0] for _, s, d, r in EX])
    y = np.arange(len(EX))
    a.barh(y, v, color=np.where(v <= CUT, CLASS_COLOR["interface"], "0.6"), height=0.6)
    for i in y:
        a.text(v[i] + 2, i, f"{v[i]:.0f}°", va="center", fontsize=10)
    a.axvline(CUT, color="k", ls="--", lw=1.2)
    a.set_yticks(y, [e[0] for e in EX])
    a.set(xlim=(0, 120), ylim=(len(EX) - 0.5, -0.5), xlabel="Kagan angle (°)", title="2. Example mechanisms")

    f.suptitle(f"Kagan angle to a thrust on the Slab2 plane (strike {S:.0f}°, dip {D:.0f}°, rake {R:.0f}°)", fontsize=13)
    f.tight_layout(rect=(0, 0, 1, 0.95))
    f.savefig(OUT, dpi=160)
    print(dict(zip([e[0] for e in EX], v.round(1))))


if __name__ == "__main__":
    main()
