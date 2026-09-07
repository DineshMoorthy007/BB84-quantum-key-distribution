"""Phase 10 Visualization: Statistical Distributions and Basis Asymmetry Plots.

Generates:
1. QBER Distribution Boxplots across 4 representative physical regimes.
2. Basis-Dependent Noise Comparison (Z-basis vs. X-basis QBER) demonstrating quantum eigenbasis asymmetry.

Inputs:
- results/phase10/data/statistical_analysis_trials.csv
- results/phase10/data/basis_noise_analysis_summary.csv

Outputs:
- results/phase10/figures/qber_distributions.png
- results/phase10/figures/basis_noise_comparison.png
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
import sys
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def plot_qber_distributions(
    csv_path: str = "results/phase10/data/statistical_analysis_trials.csv",
    output_path: str = "results/phase10/figures/qber_distributions.png",
) -> str:
    """Generate multi-regime distribution boxplots with overlaid trial data points."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    regime_qbers: Dict[str, List[float]] = {}

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cond = row["condition_name"]
            if cond not in regime_qbers:
                regime_qbers[cond] = []
            regime_qbers[cond].append(float(row["estimated_qber"]) * 100.0)

    labels = list(regime_qbers.keys())
    data = [regime_qbers[k] for k in labels]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)

    # Boxplot
    bp = ax.boxplot(
        data,
        tick_labels=labels,
        patch_artist=True,
        widths=0.45,
        boxprops=dict(facecolor="#e0e7ff", color="#4338ca", linewidth=1.5),
        whiskerprops=dict(color="#4338ca", linewidth=1.5),
        capprops=dict(color="#4338ca", linewidth=1.5),
        medianprops=dict(color="#dc2626", linewidth=2.0),
    )

    # Overlay jittered scatter points
    for idx, points in enumerate(data, start=1):
        x = np.random.normal(idx, 0.04, size=len(points))
        ax.scatter(x, points, alpha=0.6, color="#1e293b", s=25, zorder=3)

    # 11% security threshold
    ax.axhline(11.0, color="#dc2626", linestyle="--", linewidth=1.8, label="Security Threshold (11.0%)")

    ax.set_ylabel("Estimated QBER (%)", fontsize=12, fontweight="bold")
    ax.set_title("Phase 10: Empirical QBER Sampling Distributions Across Physical Regimes", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", framealpha=0.9)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def plot_basis_dependent_noise(
    csv_path: str = "results/phase10/data/basis_noise_analysis_summary.csv",
    output_path: str = "results/phase10/figures/basis_noise_comparison.png",
) -> str:
    """Generate grouped bar chart comparing Z-basis vs. X-basis QBER across noise channels."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    conditions: List[str] = []
    z_qbers: List[float] = []
    x_qbers: List[float] = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conditions.append(row["condition_name"])
            z_qbers.append(float(row["mean_z_basis_qber"]) * 100.0)
            x_qbers.append(float(row["mean_x_basis_qber"]) * 100.0)

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)
    x = np.arange(len(conditions))
    width = 0.35

    rects1 = ax.bar(x - width / 2, z_qbers, width, label="Z-Basis (|0⟩, |1⟩)", color="#3b82f6", edgecolor="#1e293b", alpha=0.85)
    rects2 = ax.bar(x + width / 2, x_qbers, width, label="X-Basis (|+⟩, |–⟩)", color="#8b5cf6", edgecolor="#1e293b", alpha=0.85)

    ax.set_ylabel("Measured QBER (%)", fontsize=12, fontweight="bold")
    ax.set_title("Phase 10: Basis-Dependent Noise Asymmetry in BB84 Single-Qubit Channels", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(15.0, max(max(z_qbers), max(x_qbers)) + 4.0))
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.9)

    # Bar annotations
    for rects in [rects1, rects2]:
        for rect in rects:
            h = rect.get_height()
            ax.annotate(
                f"{h:.1f}%",
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def main() -> None:
    """Run all statistical and basis visualization routines."""
    plot_qber_distributions()
    plot_basis_dependent_noise()


if __name__ == "__main__":
    main()
