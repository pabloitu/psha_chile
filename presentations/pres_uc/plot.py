import numpy as np
import matplotlib.pyplot as plt
from math import factorial
import seaborn as sns
sns.set_style("darkgrid", {"ytick.left": True, 'xtick.bottom': True,"axes.facecolor": ".9", 'font.family': 'Ubuntu'})

def tiny_poisson_plot(lam=0.5, fname="poisson.png"):
    """
    Make a tiny Poisson PMF plot (λ=lam) and save as a PDF,
    suitable to overlay on other figures.
    """
    # Support (0..5 is plenty for λ=0.5)
    k = np.arange(0, 6)
    pmf = np.exp(-lam) * lam**k / np.array([factorial(int(ki)) for ki in k])

    fig, ax = plt.subplots(figsize=(3.0, 2.4))  # small figure

    # "Stem" look: vertical lines + markers (no Axes.stem, so no API issues)
    ax.vlines(k, 0, pmf, linewidth=1.0)
    ax.plot(k, pmf, "o", markersize=4)

    ax.set_ylim(0, pmf.max() * 1.2)
    ax.set_xticks(k)
    ax.set_xlabel(r"$k$", fontsize=8)
    ax.set_ylabel(r"$P(N=k)$", fontsize=8)
    ax.set_title(fr"Poisson($\mu={lam}$)", fontsize=9)

    ax.tick_params(which='major', axis='y', length=8, color='gray', width=0.5)
    ax.tick_params(which='minor', axis='y', length=4, color='gray', width=0.5)
    ax.grid(axis='y', which='major', linewidth=1)
    ax.grid(axis='y', which='minor', linewidth=0.4)

    ax.grid(axis='x', which='major', linewidth=1)
    ax.grid(axis='x', which='minor', linewidth=0.4)

    fig.tight_layout()
    # fig.patch.set_alpha(0.0)  # transparent background for overlay

    fig.savefig(fname, dpi=200, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    tiny_poisson_plot(0.1)
