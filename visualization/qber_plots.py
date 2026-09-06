"""Visualization routines for QBER analysis in the BB84 simulator.

Provides decoupled plotting functions built on Matplotlib to illustrate:
1. Injected error rate vs. measured QBER validation curves.
2. Sample size vs. measured QBER statistical convergence.

Academic Note:
    Visualizations consume numerical outputs from classical post-processing
    experiments and save high-resolution figures to the `results/` directory.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Sequence
import matplotlib
# Use headless non-interactive backend
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def ensure_results_dir() -> Path:
    """Ensure that the results directory exists and return its absolute Path."""
    results_dir = Path(__file__).resolve().parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def plot_injected_vs_measured_qber(
    injected_rates: Sequence[float],
    measured_qbers: Sequence[float],
    title: str = "Classical Error Injection vs Measured QBER",
    save_filename: str = "qber_injected_vs_measured.png",
) -> Path:
    """Plot the validation curve comparing injected error rates against measured QBER.

    Args:
        injected_rates: Sequence of configured classical error rates (e.g. [0.0, 0.05, ...]).
        measured_qbers: Sequence of observed QBER values from calculate_qber.
        title: Plot title.
        save_filename: Output image filename inside results/.

    Returns:
        Path to the saved plot image.
    """
    results_dir = ensure_results_dir()
    output_path = results_dir / save_filename

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

    # Reference ideal line: y = x
    max_rate = max(max(injected_rates), max(measured_qbers), 0.35)
    line_x = np.linspace(0, max_rate * 1.05, 100)
    ax.plot(
        line_x * 100,
        line_x * 100,
        linestyle="--",
        color="#7f8c8d",
        label="Ideal Linear Expectation ($QBER = p$)",
        linewidth=1.5,
    )

    # Measured points
    injected_pct = [r * 100 for r in injected_rates]
    measured_pct = [q * 100 for q in measured_qbers]
    ax.scatter(
        injected_pct,
        measured_pct,
        color="#2980b9",
        s=70,
        zorder=5,
        label="Measured QBER Data Points",
    )
    ax.plot(
        injected_pct,
        measured_pct,
        color="#2980b9",
        linestyle="-",
        linewidth=2,
        alpha=0.8,
    )

    # 11% academic threshold reference line
    ax.axhline(
        11.0,
        color="#c0392b",
        linestyle=":",
        linewidth=1.5,
        label="Academic Security Threshold (~11% Shor-Preskill)",
    )

    ax.set_xlabel("Injected Error Rate (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Measured QBER (%)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", framealpha=0.9)
    plt.tight_layout()

    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def plot_qber_convergence(
    sample_sizes: Sequence[int],
    measured_qbers: Sequence[float],
    target_error_rate: float,
    title: str = "QBER Statistical Convergence vs Sifted Key Length",
    save_filename: str = "qber_statistical_convergence.png",
) -> Path:
    """Plot QBER measurement convergence across increasing sifted key sample sizes.

    Args:
        sample_sizes: Sequence of sample sizes (number of compared bits).
        measured_qbers: Sequence of observed QBER values.
        target_error_rate: The underlying target error probability.
        title: Plot title.
        save_filename: Output image filename inside results/.

    Returns:
        Path to the saved plot image.
    """
    results_dir = ensure_results_dir()
    output_path = results_dir / save_filename

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

    target_pct = target_error_rate * 100
    ax.axhline(
        target_pct,
        color="#27ae60",
        linestyle="--",
        linewidth=1.8,
        label=f"True Target Error Rate ({target_pct:.1f}%)",
    )

    measured_pct = [q * 100 for q in measured_qbers]
    ax.plot(
        sample_sizes,
        measured_pct,
        marker="o",
        color="#8e44ad",
        linewidth=2,
        markersize=6,
        label="Observed Sample QBER",
    )

    ax.set_xscale("log")
    ax.set_xlabel("Compared Sifted Key Length (Sample Size, Log Scale)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Measured QBER (%)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9)
    plt.tight_layout()

    fig.savefig(output_path)
    plt.close(fig)
    return output_path
