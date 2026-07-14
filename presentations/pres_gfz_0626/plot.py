import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from math import factorial
import seaborn as sns
sns.set_style("darkgrid", {"ytick.left": True, 'xtick.bottom': True, "axes.facecolor": ".9", 'font.family': 'Ubuntu'})


def _style_axes(ax, k):
    ax.set_xticks(k)
    ax.set_xlabel(r"$k$", fontsize=8)
    ax.set_ylabel(r"$P(N=k)$", fontsize=8)
    ax.tick_params(which='major', axis='y', length=8, color='gray', width=0.5)
    ax.tick_params(which='minor', axis='y', length=4, color='gray', width=0.5)
    ax.grid(axis='y', which='major', linewidth=1)
    ax.grid(axis='y', which='minor', linewidth=0.4)
    ax.grid(axis='x', which='major', linewidth=1)
    ax.grid(axis='x', which='minor', linewidth=0.4)


def poisson_pmf(k, lam):
    return np.exp(-lam) * lam**k / np.array([factorial(int(ki)) for ki in k])


def nb_params(lam, alpha, Q=1.0):
    tau = 1. / alpha * lam ** Q
    theta = tau / (tau + lam)
    return tau, theta


def poisson_plot(lam, kmax, ymax, fname="poisson.png"):
    k = np.arange(0, kmax + 1)
    pmf = poisson_pmf(k, lam)

    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    ax.vlines(k, 0, pmf, linewidth=1.0)
    ax.plot(k, pmf, "o", markersize=4)
    ax.set_title(fr"Poisson($\mu={lam}$): Var$={lam:.1f}$", fontsize=9)
    _style_axes(ax, k)
    ax.set_ylim(0, ymax)

    fig.tight_layout()
    fig.savefig(fname, dpi=200, bbox_inches="tight")
    plt.close(fig)


def nb_plot(lam, alpha, kmax, ymax, Q=1.0, fname="nbinom.png"):
    k = np.arange(0, kmax + 1)
    tau, theta = nb_params(lam, alpha, Q)
    pmf = st.nbinom.pmf(k, tau, theta)
    var = lam + lam ** 2 / tau

    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    ax.vlines(k, 0, pmf, linewidth=1.0, color="C1")
    ax.plot(k, pmf, "o", markersize=4, color="C1")
    ax.set_title(fr"NB($\mu={lam}$, $\alpha={alpha}$): Var$={var:.1f}$", fontsize=9)
    _style_axes(ax, k)
    ax.set_ylim(0, ymax)

    fig.tight_layout()
    fig.savefig(fname, dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    lam = 5.0
    alpha = 10
    kmax = 20
    Q = 1.0

    k = np.arange(0, kmax + 1)
    tau, theta = nb_params(lam, alpha, Q)
    ymax = max(poisson_pmf(k, lam).max(), st.nbinom.pmf(k, tau, theta).max()) * 1.2

    poisson_plot(lam, kmax, ymax)
    nb_plot(lam, alpha, kmax, ymax, Q)