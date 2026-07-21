# ...existing code...
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def rbf_from_distance(r, sigma=1.0, ell=0.45):
    return sigma**2 * np.exp(-0.5 * (r / ell) ** 2)


def matern12_from_distance(r, sigma=1.0, ell=0.45):
    # Matérn nu = 1/2 (exponential kernel)
    return sigma**2 * np.exp(-r / ell)


def matern52_from_distance(r, sigma=1.0, ell=0.45):
    # Matérn nu = 5/2
    a = np.sqrt(5.0) * r / ell
    return sigma**2 * (1.0 + a + (a**2) / 3.0) * np.exp(-a)


def covariance_from_distance(x, kernel_fn, **kwargs):
    r = np.abs(x[:, None] - x[None, :])
    return kernel_fn(r, **kwargs)


def draw_gp_prior_samples(x, kernel_fn, n_samples=6, seed=7, jitter=1e-10, **kwargs):
    rng = np.random.default_rng(seed)
    K = covariance_from_distance(x, kernel_fn, **kwargs)
    K = K + jitter * np.eye(len(x))
    L = np.linalg.cholesky(K)
    z = rng.standard_normal((len(x), n_samples))
    return L @ z


def setup_thesis_style():
    plt.rcParams.update(
        {
            # Target final print size: avoid oversized canvas that shrinks text in LaTeX
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 10,
            "legend.fontsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "font.family": "serif",
            "mathtext.fontset": "cm",
            "axes.grid": True,
            "grid.alpha": 0.22,
            "grid.linestyle": "--",
            "grid.linewidth": 0.6,
            # Enable only if full LaTeX is installed:
            # "text.usetex": True,
        }
    )


def main():
    setup_thesis_style()

    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    x = np.linspace(-1.5, 1.5, 260)
    r = np.linspace(0.0, 2.5, 400)

    # --- FIGURE 1: Kernel & Prior Comparison ---
    kernels = [
        ("RBF", rbf_from_distance, {"sigma": 1.0, "ell": 0.45},
         r"$k(r)=\sigma^2\exp\!\left(-\frac{r^2}{2\ell^2}\right)$"),
        ("Matérn 1/2", matern12_from_distance, {"sigma": 1.0, "ell": 0.45},
         r"$k(r)=\sigma^2\exp\!\left(-\frac{r}{\ell}\right)$"),
        ("Matérn 5/2", matern52_from_distance, {"sigma": 1.0, "ell": 0.45},
         r"$k(r)=\sigma^2\left(1+\frac{\sqrt{5}\,r}{\ell}+\frac{5r^2}{3\ell^2}\right)\exp\!\left(-\frac{\sqrt{5}\,r}{\ell}\right)$"),
    ]

    fig, axes = plt.subplots(3, 2, figsize=(6.4, 9.0))
    fig.subplots_adjust(hspace=0.42, wspace=0.28, top=0.96)

    for i, (name, kfun, pars, formula) in enumerate(kernels):
        ax_k = axes[i, 0]
        ax_k.plot(r, kfun(r, **pars), color="black", lw=1.8)
        ax_k.set_xlim(r.min(), r.max())
        ax_k.set_ylim(-0.05, 1.05)
        ax_k.set_xlabel(r"$r=|x-x'|$")
        ax_k.set_ylabel(r"$k(r)$")
        ax_k.set_title(f"{name} kernel")
        ax_k.text(
            0.98, 0.92, formula,
            ha="right", va="top", transform=ax_k.transAxes,
            bbox=dict(facecolor="white", edgecolor="0.8", alpha=0.9, boxstyle="round,pad=0.22"),
        )

        ax_s = axes[i, 1]
        samples = draw_gp_prior_samples(x, kfun, n_samples=6, seed=10 + i, **pars)
        for j in range(samples.shape[1]):
            ax_s.plot(x, samples[:, j], lw=1.2)
        ax_s.axhline(0.0, color="k", lw=0.8, alpha=0.6)
        ax_s.set_xlim(x.min(), x.max())
        ax_s.set_xlabel(r"$x$")
        ax_s.set_ylabel(r"$f(x)$")
        ax_s.set_title(f"{name} GP prior realizations")

    pdf_path = out_dir / "gp_kernels_priors.pdf"
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved:\n- {pdf_path}")

    # --- FIGURE 2: RBF under different lengthscales ---
    lengthscales = [0.15, 0.45, 1.35]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # Clean, standard color palette

    fig2, axes2 = plt.subplots(1, 2, figsize=(6.4, 3.2))
    fig2.subplots_adjust(wspace=0.28, bottom=0.18, top=0.88)

    ax_k2 = axes2[0]
    ax_s2 = axes2[1]

    for ell, color in zip(lengthscales, colors):
        # Left subplot: Covariance curves
        ax_k2.plot(
            r,
            rbf_from_distance(r, sigma=1.0, ell=ell),
            label=f"$\\ell = {ell}$",
            color=color,
            lw=1.8,
        )

        # Right subplot: Prior realizations (2 samples per lengthscale for visual clarity)
        samples = draw_gp_prior_samples(
            x, rbf_from_distance, n_samples=2, seed=42, sigma=1.0, ell=ell
        )
        for j in range(samples.shape[1]):
            # Assign label only to the first line to prevent duplicate legends
            lbl = f"$\\ell = {ell}$" if j == 0 else None
            ls = "-" if j == 0 else "--"
            ax_s2.plot(x, samples[:, j], color=color, lw=1.2, linestyle=ls, label=lbl)

    # Formatting left subplot
    ax_k2.set_xlim(r.min(), r.max())
    ax_k2.set_ylim(-0.05, 1.05)
    ax_k2.set_xlabel(r"$r=|x-x'|$")
    ax_k2.set_ylabel(r"$k(r)$")
    ax_k2.set_title("RBF kernel for varying $\\ell$")
    ax_k2.legend(loc="upper right")

    # Formatting right subplot
    ax_s2.axhline(0.0, color="k", lw=0.8, alpha=0.6)
    ax_s2.set_xlim(x.min(), x.max())
    ax_s2.set_xlabel(r"$x$")
    ax_s2.set_ylabel(r"$f(x)$")
    ax_s2.set_title("RBF GP prior realizations")
    ax_s2.legend(loc="upper right")

    pdf_path2 = out_dir / "rbf_lengthscales.pdf"
    fig2.savefig(pdf_path2, bbox_inches="tight")
    plt.close(fig2)
    print(f"- {pdf_path2}")


if __name__ == "__main__":
    main()