"""Visualization module for Phase 9 BB84 classical post-processing experiments.

Provides plotting functions for:
1. Sifted key length vs. final secret key length comparison.
2. Estimated QBER under different channel environments (Ideal, Noise, Eve, Eve+Noise).
3. Reconciliation leakage and final secret key length vs. QBER.
4. Acceptance vs. Rejection decision boundary under varying QBER conditions.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence
import matplotlib.pyplot as plt
import numpy as np


def plot_sifted_vs_final_key_lengths(
    conditions: Sequence[str],
    sifted_lengths: Sequence[int],
    final_lengths: Sequence[int],
    output_path: str = "results/phase9_sifted_vs_final.png",
) -> str:
    """Plot bar chart comparing initial sifted key length against final secret key length.

    Args:
        conditions: Labels for evaluated conditions.
        sifted_lengths: Sequence of sifted key lengths.
        final_lengths: Sequence of final secret key lengths (0 if rejected).
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.arange(len(conditions))
    width = 0.35

    bars1 = ax.bar(x - width / 2, sifted_lengths, width, label="Sifted Key Length", alpha=0.85)
    bars2 = ax.bar(x + width / 2, final_lengths, width, label="Final Secret Key Length", alpha=0.85)

    ax.set_ylabel("Key Length (bits)", fontsize=12, fontweight="bold")
    ax.set_title(
        "BB84 Post-Processing: Sifted vs. Final Secret Key Lengths",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(conditions, fontsize=10, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True)

    # Annotate bars
    for bar in list(bars1) + list(bars2):
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"{height}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def plot_end_to_end_summary(
    summary_data: Dict[str, Dict[str, Any]],
    output_path: str = "results/phase9_end_to_end.png",
) -> str:
    """Plot multi-panel figure summarizing estimated QBER and final secret key extraction.

    Args:
        summary_data: Dict mapping condition name to metrics dict containing
            'estimated_qber_pct', 'final_key_len', 'is_accepted', 'leakage'.
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    conditions = list(summary_data.keys())
    qber_vals = [summary_data[c]["estimated_qber_pct"] for c in conditions]
    final_lens = [summary_data[c]["final_key_len"] for c in conditions]
    accepted_flags = [summary_data[c]["is_accepted"] for c in conditions]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    x = np.arange(len(conditions))
    width = 0.5

    # Panel 1: Estimated QBER vs Threshold
    bars1 = ax1.bar(x, qber_vals, width, alpha=0.85)
    ax1.axhline(11.0, color="red", linestyle="--", linewidth=1.5, label="Threshold (11.0%)")
    ax1.set_ylabel("Estimated QBER (%)", fontsize=11, fontweight="bold")
    ax1.set_title("Parameter Estimation (QBER)", fontsize=12, fontweight="bold")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(conditions, rotation=15, ha="right", fontsize=9, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left")

    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(
            f"{height:.2f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # Panel 2: Final Secret Key Lengths & Decision Status
    bars2 = ax2.bar(x, final_lens, width, alpha=0.85)
    ax2.set_ylabel("Final Secret Key Length (bits)", fontsize=11, fontweight="bold")
    ax2.set_title("Extracted Secret Key & Security Status", fontsize=12, fontweight="bold")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(conditions, rotation=15, ha="right", fontsize=9, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.6)

    for bar, acc in zip(bars2, accepted_flags):
        height = bar.get_height()
        status_str = "ACCEPTED" if acc else "ABORTED"
        ax2.annotate(
            f"{height} bits\n[{status_str}]",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def plot_reconciliation_and_compression(
    qber_values: Sequence[float],
    leakage_bits: Sequence[int],
    final_key_lengths: Sequence[int],
    output_path: str = "results/phase9_leakage_and_compression.png",
) -> str:
    """Plot reconciliation leakage and final key length scaling as a function of QBER.

    Args:
        qber_values: Sequence of tested QBER percentages.
        leakage_bits: Number of public parity bits leaked during reconciliation.
        final_key_lengths: Final secret key length achieved after privacy amplification.
        output_path: Path where figure will be saved.

    Returns:
        Absolute path to saved figure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(9, 6))

    ax1.plot(qber_values, leakage_bits, marker="s", linewidth=2, label="Reconciliation Leakage (bits)")
    ax1.set_xlabel("Estimated QBER (%)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Public Parity Leakage (bits)", fontsize=12, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.6)

    ax2 = ax1.twinx()
    ax2.plot(qber_values, final_key_lengths, marker="o", linestyle="--", linewidth=2, label="Final Key Length (bits)")
    ax2.set_ylabel("Final Secret Key Length (bits)", fontsize=12, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    plt.title("Impact of QBER on Reconciliation Leakage & Secret Key Compression", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)
