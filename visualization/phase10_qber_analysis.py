"""Phase 10 Visualization: Quantum Bit Error Rate (QBER) Benchmark Plots.

Generates:
1. QBER by Condition bar chart with 95% Wilson score confidence intervals and Shor-Preskill threshold line.
2. QBER vs. Eve Interception Probability scatter/line with theoretical expectation reference.
3. QBER vs. Noise Probability across Bit-Flip, Phase-Flip, and Depolarizing channels with theoretical curves.

Inputs:
- results/phase10/data/baseline_summary.csv
- results/phase10/data/eve_probability_summary.csv
- results/phase10/data/noise_sweep_summary.csv

Outputs:
- results/phase10/figures/qber_by_condition.png
- results/phase10/figures/qber_vs_eve.png
- results/phase10/figures/qber_vs_noise.png
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
import sys
from typing import Any, Dict, List
import matplotlib.pyplot as plt
import numpy as np

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def plot_qber_by_condition(
    csv_path: str = "results/phase10/data/baseline_summary.csv",
    output_path: str = "results/phase10/figures/qber_by_condition.png",
) -> str:
    """Generate bar chart comparing mean QBER with 95% Wilson confidence intervals across conditions."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    conditions: List[str] = []
    means: List[float] = []
    stds: List[float] = []
    ci_lowers: List[float] = []
    ci_uppers: List[float] = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conditions.append(row["condition_name"])
            mean = float(row["qber_mean"]) * 100.0
            std = float(row["qber_std"]) * 100.0
            ci_l = float(row["pooled_ci_lower"]) * 100.0
            ci_u = float(row["pooled_ci_upper"]) * 100.0
            means.append(mean)
            stds.append(std)
            ci_lowers.append(mean - ci_l)
            ci_uppers.append(ci_u - mean)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    x = np.arange(len(conditions))
    width = 0.55

    # Color palette: green for safe (<11%), red for high error (>=11%)
    colors = ["#22c55e" if m <= 11.0 else "#ef4444" for m in means]

    yerr = [ci_lowers, ci_uppers]
    bars = ax.bar(x, means, width, yerr=yerr, capsize=6, color=colors, edgecolor="#1e293b", alpha=0.85)

    # Shor-Preskill security threshold line at 11.0%
    ax.axhline(11.0, color="#dc2626", linestyle="--", linewidth=1.8, label="Security Threshold (11.0%)")

    ax.set_ylabel("Measured QBER (%)", fontsize=12, fontweight="bold")
    ax.set_title("Phase 10: Quantum Bit Error Rate by Channel Condition (with 95% Wilson CI)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=25, ha="right", fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(35.0, max(means) + 6.0))
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", framealpha=0.9)

    for bar, m in zip(bars, means):
        height = bar.get_height()
        ax.annotate(
            f"{m:.2f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 7),
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


def plot_qber_vs_eve_probability(
    csv_path: str = "results/phase10/data/eve_probability_summary.csv",
    output_path: str = "results/phase10/figures/qber_vs_eve.png",
) -> str:
    """Plot measured QBER vs. Eve interception probability alongside the theoretical reference curve."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    p_eves: List[float] = []
    qber_means: List[float] = []
    qber_stds: List[float] = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p_eves.append(float(row["eve_probability"]))
            qber_means.append(float(row["qber_mean"]) * 100.0)
            qber_stds.append(float(row["qber_std"]) * 100.0)

    p_arr = np.array(p_eves)
    m_arr = np.array(qber_means)
    std_arr = np.array(qber_stds)

    fig, ax = plt.subplots(figsize=(9, 6), dpi=200)

    # Theoretical line: QBER = p_eve * 25%
    p_dense = np.linspace(0.0, 1.0, 100)
    theory_dense = p_dense * 25.0
    ax.plot(p_dense, theory_dense, color="#6366f1", linestyle="--", linewidth=2.0, label=r"Theoretical Bound: $\text{QBER} = p_{\text{eve}} \times 25.0\%$")

    # Security cutoff line
    ax.axhline(11.0, color="#dc2626", linestyle=":", linewidth=1.8, label="Security Abort Threshold (11.0%)")

    # Empirical measurements
    ax.errorbar(
        p_arr,
        m_arr,
        yerr=std_arr,
        fmt="o",
        color="#0ea5e9",
        ecolor="#0284c7",
        elinewidth=1.8,
        capsize=4,
        markersize=6,
        label=r"Simulation Measurement (Mean $\pm$ Std)",
    )

    ax.set_xlabel(r"Eve Interception Probability ($p_{\text{eve}}$)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Quantum Bit Error Rate (QBER %)", fontsize=12, fontweight="bold")
    ax.set_title("Phase 10: Eavesdropping Impact — QBER vs. Eve Interception Probability", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-1.0, 30.0)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", framealpha=0.9)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def plot_qber_vs_noise_sweep(
    csv_path: str = "results/phase10/data/noise_sweep_summary.csv",
    output_path: str = "results/phase10/figures/qber_vs_noise.png",
) -> str:
    """Plot measured QBER vs. noise parameter p across bit-flip, phase-flip, and depolarizing channels."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    model_data: Dict[str, Dict[str, List[float]]] = {
        "bit_flip": {"p": [], "qber": [], "std": []},
        "phase_flip": {"p": [], "qber": [], "std": []},
        "depolarizing": {"p": [], "qber": [], "std": []},
    }

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row["noise_model"]
            if model in model_data:
                model_data[model]["p"].append(float(row["noise_probability"]))
                model_data[model]["qber"].append(float(row["qber_mean"]) * 100.0)
                model_data[model]["std"].append(float(row["qber_std"]) * 100.0)

    fig, ax = plt.subplots(figsize=(9, 6), dpi=200)

    styles = {
        "bit_flip": {"color": "#3b82f6", "label": "Bit-Flip (Pauli-X)", "marker": "s"},
        "phase_flip": {"color": "#8b5cf6", "label": "Phase-Flip (Pauli-Z)", "marker": "^"},
        "depolarizing": {"color": "#f59e0b", "label": "Depolarizing (Isotropic)", "marker": "o"},
    }

    for model, d in model_data.items():
        if d["p"]:
            ax.errorbar(
                d["p"],
                d["qber"],
                yerr=d["std"],
                fmt=styles[model]["marker"] + "-",
                color=styles[model]["color"],
                ecolor=styles[model]["color"],
                elinewidth=1.5,
                capsize=3,
                markersize=5,
                label=f"{styles[model]['label']} (Empirical)",
            )

    # Theoretical line: average QBER = p / 2
    p_theory = np.linspace(0.0, 0.20, 100)
    ax.plot(p_theory, p_theory * 50.0, color="#64748b", linestyle="--", linewidth=1.8, label=r"Theoretical Reference: $\text{QBER} = p / 2$")

    # Security cutoff line
    ax.axhline(11.0, color="#dc2626", linestyle=":", linewidth=1.8, label="Security Abort Threshold (11.0%)")

    ax.set_xlabel("Physical Quantum Noise Probability (p)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Quantum Bit Error Rate (QBER %)", fontsize=12, fontweight="bold")
    ax.set_title("Phase 10: Quantum Decoherence Impact — QBER vs. Noise Strength", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(-0.005, 0.205)
    ax.set_ylim(-0.5, 15.0)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", framealpha=0.9)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def main() -> None:
    """Run all QBER visualization routines."""
    plot_qber_by_condition()
    plot_qber_vs_eve_probability()
    plot_qber_vs_noise_sweep()


if __name__ == "__main__":
    main()
