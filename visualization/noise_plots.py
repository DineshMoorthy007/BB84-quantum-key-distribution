"""Visualization module for Phase 8 Quantum Noise experiments.

Provides plotting functions for:
1. QBER comparison between noise models at a fixed noise rate (bar chart).
2. Parametric noise probability sweep across Bit-Flip, Phase-Flip, and Depolarizing models.
3. Basis-dependent phase noise impact (Z-basis vs X-basis).
4. Eve vs Noise composition analysis (4 operational conditions).
5. Statistical distribution and variability (mean QBER with error bars).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence
import matplotlib.pyplot as plt
import numpy as np


def plot_noise_model_comparison(
    comparison_data: Dict[str, Dict[str, Any]],
    output_path: str = "results/phase8_noise_comparison.png",
) -> str:
    """Plot bar chart comparing QBER across different noise models at a fixed rate.

    Args:
        comparison_data: Dict mapping model name to metrics dict containing
            'probability', 'qber_pct', 'sifted_length', 'error_count'.
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    models = list(comparison_data.keys())
    qber_vals = [comparison_data[m]["qber_pct"] for m in models]
    err_counts = [comparison_data[m]["error_count"] for m in models]
    sift_lens = [comparison_data[m]["sifted_length"] for m in models]

    fig, ax = plt.subplots(figsize=(9, 6))
    x = range(len(models))
    width = 0.45

    bars = ax.bar(x, qber_vals, width, edgecolor="black", alpha=0.85)

    ax.set_ylabel("Quantum Bit Error Rate (QBER %)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Quantum Noise Comparison: Error Rate Across Channels in BB84",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(models, fontsize=11, fontweight="bold")
    ax.set_ylim(0, max(15.0, max(qber_vals) + 4.0))
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    # Annotate bars
    for bar, m, err, sift in zip(bars, models, err_counts, sift_lens):
        height = bar.get_height()
        prob = comparison_data[m]["probability"]
        ax.annotate(
            f"{height:.2f}%\n(p={prob:.2f})\n{err}/{sift}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def plot_noise_rate_sweep(
    probabilities: Sequence[float],
    sweep_results: Dict[str, Sequence[float]],
    output_path: str = "results/phase8_noise_sweep.png",
) -> str:
    """Plot QBER as a function of noise probability for multiple noise channels.

    Args:
        probabilities: Sequence of tested noise parameters.
        sweep_results: Dict mapping model name to list of observed QBER percentages.
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    for name, qber_vals in sweep_results.items():
        ax.plot(
            probabilities,
            qber_vals,
            marker="o",
            linewidth=2,
            label=name,
        )

    # Reference standard QKD threshold line
    ax.axhline(
        11.0,
        linestyle="--",
        linewidth=1.5,
        color="red",
        label="Shor-Preskill Security Threshold (11.0%)",
    )

    ax.set_xlabel(r"Noise Parameter ($p$ / $\lambda$)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Observed QBER (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "QBER Scaling as a Function of Quantum Channel Noise Parameter",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", frameon=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def plot_phase_noise_basis_dependence(
    probabilities: Sequence[float],
    z_qber: Sequence[float],
    x_qber: Sequence[float],
    combined_qber: Sequence[float],
    output_path: str = "results/phase8_phase_noise_basis.png",
) -> str:
    """Plot basis-dependent QBER under phase-flip noise (Z-basis vs X-basis).

    Args:
        probabilities: Sequence of phase-flip probabilities tested.
        z_qber: QBER percentages on Z-basis sifted signals.
        x_qber: QBER percentages on X-basis sifted signals.
        combined_qber: Overall sifted QBER across both bases.
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(
        probabilities,
        z_qber,
        marker="s",
        linewidth=2,
        label="Z-Basis Transmissions (Immune to Phase Noise)",
    )
    ax.plot(
        probabilities,
        x_qber,
        marker="^",
        linewidth=2,
        label="X-Basis Transmissions (Inverted by Phase Noise)",
    )
    ax.plot(
        probabilities,
        combined_qber,
        marker="o",
        linestyle="--",
        linewidth=2,
        label="BB84 Total Sifted QBER (~ p / 2)",
    )

    ax.set_xlabel("Phase-Flip Probability ($p$)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Observed QBER (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Basis-Dependent Quantum Behavior Under Phase-Flip Noise",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(-1.0, max(35.0, max(x_qber) + 5.0))
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", frameon=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def plot_eve_vs_noise_composition(
    conditions_data: Dict[str, float],
    output_path: str = "results/phase8_eve_vs_noise.png",
) -> str:
    """Plot bar chart comparing No Eve + Ideal, Eve + Ideal, No Eve + Noise, Eve + Noise.

    Args:
        conditions_data: Dict mapping condition name to observed QBER percentage.
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    conditions = list(conditions_data.keys())
    qber_vals = [conditions_data[c] for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(conditions))
    width = 0.5

    bars = ax.bar(x, qber_vals, width, edgecolor="black", alpha=0.85)

    ax.axhline(
        11.0,
        linestyle="--",
        linewidth=1.5,
        color="red",
        label="Security Abort Threshold (11.0%)",
    )
    ax.axhline(
        25.0,
        linestyle=":",
        linewidth=1.5,
        color="purple",
        label="Theoretical Full Intercept-Resend (25.0%)",
    )

    ax.set_ylabel("Quantum Bit Error Rate (QBER %)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Physical Channel Analysis: Eavesdropping vs. Environmental Noise",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(conditions, fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(38.0, max(qber_vals) + 5.0))
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", frameon=True)

    # Annotate bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.2f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def plot_noise_statistics_distribution(
    stats_data: Dict[str, Dict[str, float]],
    output_path: str = "results/phase8_statistics.png",
) -> str:
    """Plot mean QBER with error bars (min, max, std deviation) across repeated trials.

    Args:
        stats_data: Dict mapping model name to stats dict with 'mean', 'std', 'min', 'max'.
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    models = list(stats_data.keys())
    means = [stats_data[m]["mean"] for m in models]
    stds = [stats_data[m]["std"] for m in models]
    mins = [stats_data[m]["min"] for m in models]
    maxs = [stats_data[m]["max"] for m in models]

    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.arange(len(models))

    # Error bar using standard deviation
    ax.bar(
        x,
        means,
        yerr=stds,
        capsize=8,
        width=0.45,
        edgecolor="black",
        alpha=0.85,
        label=r"Mean QBER $\pm 1\sigma$",
    )

    # Scatter min and max points
    ax.scatter(x, mins, marker="v", s=60, color="darkblue", zorder=5, label="Min QBER")
    ax.scatter(x, maxs, marker="^", s=60, color="darkred", zorder=5, label="Max QBER")

    ax.set_ylabel("Quantum Bit Error Rate (QBER %)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Statistical Variability of QBER Across Repeated Stochastic Simulations",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(models, fontsize=11, fontweight="bold")
    ax.set_ylim(0, max(20.0, max(maxs) + 5.0))
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", frameon=True)

    for i, m in enumerate(models):
        mean_v = means[i]
        std_v = stds[i]
        ax.annotate(
            f"{mean_v:.2f}% ± {std_v:.2f}%",
            xy=(i, mean_v),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)
