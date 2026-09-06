"""Visualization module for Phase 7 Eve intercept-resend attack experiments.

Provides plotting functions for:
1. No-Eve vs Full-Eve QBER comparison (bar chart).
2. Interception probability sweep vs observed QBER (with theoretical expectation curve).
3. Statistical convergence of QBER toward theoretical 25% expectation as signal count increases.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence
import matplotlib.pyplot as plt


def plot_no_eve_vs_eve_comparison(
    comparison_data: Dict[str, Dict[str, Any]],
    output_path: str = "results/phase7_eve_comparison.png",
) -> str:
    """Plot bar chart comparing No-Eve vs Full-Eve conditions.

    Args:
        comparison_data: Dictionary mapping condition name ('No Eve', 'Full Eve')
            to metrics dict containing 'qber_pct', 'sifted_length', 'error_count'.
        output_path: Path where plot image will be saved.

    Returns:
        Absolute path to the saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    conditions = list(comparison_data.keys())
    qber_values = [comparison_data[c]["qber_pct"] for c in conditions]
    sifted_lens = [comparison_data[c]["sifted_length"] for c in conditions]
    error_counts = [comparison_data[c]["error_count"] for c in conditions]

    fig, ax1 = plt.subplots(figsize=(8, 6))

    x = range(len(conditions))
    width = 0.4

    bars = ax1.bar(
        x,
        qber_values,
        width,
        color=["#2ecc71", "#e74c3c"],
        edgecolor="black",
        linewidth=1.2,
        alpha=0.85,
    )

    # Theoretical line at 25%
    ax1.axhline(
        25.0,
        color="#c0392b",
        linestyle="--",
        linewidth=1.5,
        label="Theoretical Intercept-Resend QBER (25.0%)",
    )

    ax1.set_ylabel("Quantum Bit Error Rate (QBER %)", fontsize=12, fontweight="bold")
    ax1.set_title(
        "BB84 Eavesdropping Detection: No Eve vs. Full Intercept-Resend Eve",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(conditions, fontsize=11, fontweight="bold")
    ax1.set_ylim(0, max(30.0, max(qber_values) + 5.0))
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left", frameon=True)

    # Annotate bars
    for bar, c in zip(bars, conditions):
        height = bar.get_height()
        sift_len = comparison_data[c]["sifted_length"]
        err_cnt = comparison_data[c]["error_count"]
        ax1.annotate(
            f"{height:.2f}%\n({err_cnt} errors / {sift_len} sifted)",
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


def plot_interception_probability_sweep(
    probabilities: Sequence[float],
    qber_values: Sequence[float],
    intercepted_counts: Optional[Sequence[int]] = None,
    total_signals: Optional[int] = None,
    output_path: str = "results/phase7_eve_probability.png",
) -> str:
    """Plot QBER vs Eve Interception Probability alongside theoretical expectation.

    Theory: QBER(p) = p * 0.25 (since P(wrong basis)=0.5, P(error|wrong)=0.5).

    Args:
        probabilities: Sequence of configured interception probabilities in [0.0, 1.0].
        qber_values: Observed QBER values (as percentages or fractions).
        intercepted_counts: Optional sequence of actual intercepted signal counts.
        total_signals: Optional total signals per trial.
        output_path: Path where plot image will be saved.

    Returns:
        Absolute path to the saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Normalize to percentages if given as fraction <= 1.0
    qber_pcts = [q * 100.0 if q <= 1.0 and max(qber_values) <= 1.0 else q for q in qber_values]

    fig, ax = plt.subplots(figsize=(9, 6))

    # Theoretical line: QBER = p * 25%
    p_line = [p * 0.01 for p in range(0, 101)]
    theory_line = [p * 25.0 for p in p_line]

    ax.plot(
        p_line,
        theory_line,
        color="#34495e",
        linestyle="--",
        linewidth=2,
        label=r"Theoretical Expectation: $\mathrm{QBER} = p \times 25\%$",
    )

    # Simulated data points
    ax.plot(
        probabilities,
        qber_pcts,
        marker="o",
        markersize=8,
        color="#e74c3c",
        linewidth=2,
        label="Simulated Intercept-Resend Attack",
    )

    # Threshold line
    ax.axhline(
        11.0,
        color="#d35400",
        linestyle=":",
        linewidth=1.5,
        label="Standard Security Threshold (11.0%)",
    )

    ax.set_xlabel("Eve Interception Probability ($p$)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Observed QBER (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "QBER as a Function of Eve Interception Probability (BB84)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-1.0, max(30.0, max(qber_pcts) + 5.0))
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", frameon=True)

    # Annotate points
    for p, q in zip(probabilities, qber_pcts):
        ax.annotate(
            f"{q:.2f}%",
            xy=(p, q),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def plot_statistical_convergence(
    signal_counts: Sequence[int],
    qber_values: Sequence[float],
    output_path: str = "results/phase7_convergence.png",
) -> str:
    """Plot convergence of observed QBER toward theoretical 25% with increasing sample size.

    Args:
        signal_counts: Sequence of signal counts tested (e.g. 100, 500, 1000, ...).
        qber_values: Measured QBER percentages.
        output_path: Path where plot image will be saved.

    Returns:
        Absolute path to the saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    qber_pcts = [q * 100.0 if q <= 1.0 and max(qber_values) <= 1.0 else q for q in qber_values]

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.axhline(
        25.0,
        color="#27ae60",
        linestyle="--",
        linewidth=2,
        label="Theoretical Value (25.0%)",
    )

    # Semi-transparent error band around 25%
    ax.axhspan(24.0, 26.0, color="#2ecc71", alpha=0.15, label=r"$\pm 1\%$ Convergence Window")

    ax.plot(
        signal_counts,
        qber_pcts,
        marker="s",
        markersize=7,
        color="#2980b9",
        linewidth=2,
        label="Simulated QBER",
    )

    ax.set_xscale("log")
    ax.set_xlabel("Number of Transmitted Signals (Log Scale)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Measured QBER (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Statistical Convergence of QBER Under Full Intercept-Resend Attack",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(15.0, 35.0)
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True)

    # Annotate points
    for n, q in zip(signal_counts, qber_pcts):
        ax.annotate(
            f"{q:.2f}%\n(N={n})",
            xy=(n, q),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)
