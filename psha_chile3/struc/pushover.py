import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

g = 9.81  # m/s^2


# ---------------------------------------------------------
# 1. Read UHS file (as stored from your hazard script)
# ---------------------------------------------------------

def read_uhs_file(fname):
    """
    Read UHS from a file like 'Iquique_uhs_values.txt':

    # Uniform Hazard Spectrum (10% in 50 yr) for Iquique
    # IM_label    value
    PGA        2.345678e-01
    SA(0.1)    3.456789e-01
    SA(0.2)    ...

    Returns
    -------
    periods : np.ndarray
        Periods T [s] (PGA is treated as T=0).
    Sa_g : np.ndarray
        Spectral accelerations in g, same order as periods.
    """
    periods = []
    Sa_g = []

    with open(fname, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tokens = line.split()
            label = tokens[0]
            val = float(tokens[1])

            if label == "PGA":
                T = 0.0
            elif label.startswith("SA(") and label.endswith(")"):
                # SA(0.2) -> 0.2
                inside = label[3:-1]
                T = float(inside)
            else:
                continue

            periods.append(T)
            Sa_g.append(val)

    periods = np.array(periods, dtype=float)
    Sa_g = np.array(Sa_g, dtype=float)

    # Sort by period, just in case
    idx = np.argsort(periods)
    return periods[idx], Sa_g[idx]


# ---------------------------------------------------------
# 2. Simple bilinear SDOF pushover capacity
# ---------------------------------------------------------

def build_bilinear_capacity(T1=0.5, dy=0.02, alpha=0.05, m_eff=1.0,
                            Sd_max=0.20, n_points=200):
    """
    Build a simple SDOF bilinear capacity curve in ADRS form.

    Parameters
    ----------
    T1 : float
        Effective period of SDOF [s].
    dy : float
        Yield displacement [m].
    alpha : float
        Post-yield stiffness ratio (0 = perfectly plastic, small positive = hardening).
    m_eff : float
        Effective mass (arbitrary scaling; only Sa shape matters).
    Sd_max : float
        Max spectral displacement to plot [m].
    n_points : int
        Number of points along the capacity curve.

    Returns
    -------
    Sd_cap : np.ndarray
        Spectral displacement [m].
    Sa_cap : np.ndarray
        Spectral acceleration [g].
    """
    omega1 = 2 * np.pi / T1
    k_el = m_eff * omega1**2    # elastic stiffness
    Fy = k_el * dy              # yield force
    k_post = alpha * k_el       # post-yield stiffness

    Sd_cap = np.linspace(0.0, Sd_max, n_points)
    Sa_cap = np.empty_like(Sd_cap)

    elastic = Sd_cap <= dy
    plastic = Sd_cap > dy

    # Sa = F / (m*g)
    Sa_cap[elastic] = (k_el * Sd_cap[elastic]) / (m_eff * g)
    Sa_cap[plastic] = (Fy + k_post * (Sd_cap[plastic] - dy)) / (m_eff * g)

    return Sd_cap, Sa_cap


# ---------------------------------------------------------
# 3. Main: build ADRS and pushover, and plot together
# ---------------------------------------------------------

def main():
    # ---------- Read UHS (Iquique) ----------
        # ---------- Read UHS (Iquique) ----------
    uhs_file = "Iquique_uhs_values.txt"  # adjust if needed
    T_uhs, Sa_g_uhs = read_uhs_file(uhs_file)

    # Convert to ADRS: Sa (g) vs Sd (m)
    mask = T_uhs > 0.0
    T_pos = T_uhs[mask]
    Sa_g_pos = Sa_g_uhs[mask]

    omega = 2 * np.pi / T_pos
    Sa_mps2 = Sa_g_pos * g
    Sd_m = Sa_mps2 / (omega ** 2)  # [m]

    # ---------- Simple SDOF pushover capacity ----------
    # Reasonable example: T1 ~ 0.5 s, yield disp 2 cm, 5% post-yield hardening
    T1 = 0.5
    dy = 0.02  # m
    alpha = 0.05

    # >>> NEW: extend capacity at least a bit beyond max demand displacement
    Sd_max_demand = Sd_m.max()
    Sd_max_cap = max(0.20,
                     1.2 * Sd_max_demand)  # 20% margin over demand (or 0.20 m minimum)

    Sd_cap, Sa_cap = build_bilinear_capacity(
        T1=T1, dy=dy, alpha=alpha,
        m_eff=1.0, Sd_max=Sd_max_cap, n_points=200
    )

    # ---------- Find an approximate "performance point" ----------
    # Interpolate demand Sa at capacity Sd range, and find where |capacity - demand| is minimal.
    Sd_common = Sd_cap.copy()
    # Limit common Sd to demand range
    Sd_max_demand = Sd_m.max()
    mask_common = Sd_common <= Sd_max_demand
    Sd_common = Sd_common[mask_common]

    if len(Sd_common) > 0:
        Sa_demand_interp = np.interp(Sd_common, Sd_m, Sa_g_pos)
        Sa_capacity_interp = np.interp(Sd_common, Sd_cap, Sa_cap)
        diff = Sa_capacity_interp - Sa_demand_interp
        idx_pp = np.argmin(np.abs(diff))
        Sd_pp = Sd_common[idx_pp]
        Sa_pp = Sa_capacity_interp[idx_pp]
    else:
        Sd_pp = None
        Sa_pp = None

    # ---------- Plot in your usual style ----------
    sns.set_style(
        "darkgrid",
        {
            "ytick.left": True,
            "xtick.bottom": True,
            "axes.facecolor": ".9",
            "font.family": "Ubuntu",
        },
    )

    fig, ax = plt.subplots(figsize=(5.0, 4.0))

    # Demand (Iquique UHS) in ADRS
    ax.plot(Sd_m, Sa_g_pos, "o-", color="steelblue",
            label="Iquique UHS (10% en 50 yr)")

    # Capacity (SDOF pushover)
    ax.plot(Sd_cap, Sa_cap, "-", color="darkred", linewidth=2,
            label="SDOF capacidad pushover")

    # Performance point, if found
    if Sd_pp is not None and Sa_pp is not None:
        ax.scatter(Sd_pp, Sa_pp, color="black", zorder=5)
        ax.text(Sd_pp, Sa_pp, "  performance point",
                va="bottom", ha="left", fontsize=8)

    ax.set_xlabel(r"Desplazamiento espectral $S_d$ [m]", fontsize=10)
    ax.set_ylabel(r"Aceleración Espectral $S_a$ [g]", fontsize=10)
    ax.set_title("ADRS: Capacidad Pushover vs  UHS Iquique", fontsize=11)

    # Tick + grid styling like your hazard plots
    ax.tick_params(which="major", axis="y", length=8, color="gray", width=0.5)
    ax.tick_params(which="minor", axis="y", length=4, color="gray", width=0.5)
    ax.tick_params(which="major", axis="x", length=5, color="gray", width=0.5)

    ax.grid(axis="y", which="major", linewidth=1)
    ax.grid(axis="y", which="minor", linewidth=0.4)
    ax.grid(axis="x", which="major", linewidth=1)
    ax.grid(axis="x", which="minor", linewidth=0.4)

    ax.legend(loc="best", frameon=True)

    fig.tight_layout()
    fig.savefig("Iquique_ADRS_pushover.png",
                dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
