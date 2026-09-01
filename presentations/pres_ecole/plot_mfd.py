import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style(
    "darkgrid",
    {
        "ytick.left": True,
        "xtick.bottom": True,
        "axes.facecolor": ".9",
        "font.family": "Ubuntu",
    },
)

def tiny_mfd_plot(
    a=5.0,
    b=1.0,
    m_min=4.0,
    m_max=8.0,      # this is M_max (truncation magnitude)
    m_corner=7.6,
    fname="mfd.png",
):
    """
    Tiny magnitude–frequency distribution plot (log-y) showing:
      - Gutenberg–Richter (GR)
      - Truncated GR (at M_max)
      - Tapered GR (corner M_c)
    """
    # Extend magnitude range beyond M_max so GR visibly continues
    m_end = m_max + 0.5
    m = np.linspace(m_min, m_end, 100)

    # Base GR: log10 N = a - b M  ->  N(M >= m)
    N_gr = 10.0 ** (a - b * m)

    # Truncated GR: same shape, but zero beyond M_max
    N_tr = N_gr.copy()
    N_tr[m > m_max] = np.nan

    # Tapered GR: exponential taper beyond m_corner (illustrative)
    alpha = 1.5
    taper = np.exp(-10.0 ** (alpha * (m - m_corner)))
    N_tap = N_gr * taper

    # Small horizontal offsets to separate curves visually
    dx = 0.05
    m_gr = m - dx
    m_tr = m
    m_tap = m + dx

    fig, ax = plt.subplots(figsize=(6, 4))

    # Curves
    line_gr,   = ax.plot(m_gr,  N_gr,  "-",  label="GR",           linewidth=1.2)
    line_tr,   = ax.plot(m_tr,  N_tr,  "--", label="Truncated GR", linewidth=1.2)
    line_tap,  = ax.plot(m_tap, N_tap, ".",  label="Tapered GR",   markersize=3, linewidth=0)

    # Log y-axis
    ax.set_yscale("log")

    # Axes labels (bigger)
    ax.set_xlabel("Magnitude $M$", fontsize=10)
    ax.set_ylabel(r"$N(M \geq m)$", fontsize=10)

    ax.set_xlim(m_min - 0.1, m_end + 0.1)

    # Reasonable y-limits
    all_vals = np.concatenate([
        N_gr[np.isfinite(N_gr) & (N_gr > 0)],
        N_tr[np.isfinite(N_tr) & (N_tr > 0)],
        N_tap[np.isfinite(N_tap) & (N_tap > 0)],
    ])
    ymin = 1e-4
    ymax = all_vals.max() * 2.0
    ax.set_ylim(ymin, ymax)

    # Tick style (slightly larger)
    ax.tick_params(which="major", axis="y", length=8, color="gray", width=0.5, labelsize=8)
    ax.tick_params(which="minor", axis="y", length=4, color="gray", width=0.5)
    ax.tick_params(which="major", axis="x", length=5, color="gray", width=0.5, labelsize=8)

    ax.grid(axis="y", which="major", linewidth=1)
    ax.grid(axis="y", which="minor", linewidth=0.4)
    ax.grid(axis="x", which="major", linewidth=1)
    ax.grid(axis="x", which="minor", linewidth=0.4)

    # Text annotations for a, b, Mmax, Mcorner
    ax.text(
        0.08, 0.96,
        rf"$\leftarrow\, a={a:.1f}$ (intercept)",
        transform=ax.transAxes,
        va="top", ha="left", fontsize=9,
    )


    # Show b as the slope: annotate along the GR line
    # Pick two magnitudes in the linear region for the arrow
    m1 = m_min + 0.5
    m2 = m1 + 0.8
    # Evaluate GR at those points
    y1 = 10.0 ** (a - b * m1)
    y2 = 10.0 ** (a - b * m2)

    ax.annotate(
        r"slope $=-b$",
        xy=(m2, y2),
        xytext=(m2 + 0.4, y2 * 3),
        textcoords="data",
        fontsize=9,
        arrowprops=dict(arrowstyle="->", lw=0.8, color="black"),
        ha="left", va="bottom",
    )

    # Mark M_max with a vertical line
    ax.axvline(m_max, color="black", linestyle=":", linewidth=0.8)
    ax.text(
        m_max, 0.8,
        r"$M_{\max}$",
        rotation=90,
        va="bottom", ha="center",
        fontsize=9,
        backgroundcolor="white",
    )

    ax.axvline(m_corner, color="black", linestyle=":", linewidth=0.8)
    ax.text(
        m_corner, 0.8,
        r"$M_{c}$",
        rotation=90,
        va="bottom", ha="center",
        fontsize=9,
        backgroundcolor="white",
    )
    # Compact legend
    ax.legend(fontsize=7, loc="lower left", frameon=False)

    fig.tight_layout()
    fig.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    tiny_mfd_plot()
