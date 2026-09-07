"""Phase 10 Visualization: Distilled Secret Key Rate and Acceptance Dynamics.

Generates:
1. Final Secret Key Rate vs. Eve Interception Probability.
2. Final Secret Key Rate vs. Noise Probability across noise models.
3. Protocol Acceptance Rate comparison curves.

Inputs:
- results/phase10/data/eve_probability_summary.csv
- results/phase10/data/noise_sweep_summary.csv

Outputs:
- results/phase10/figures/key_rate_vs_eve.png
- results/phase10/figures/key_rate_vs_noise.png
- results/phase10/figures/acceptance_rates.png
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


def plot_key_rate_vs_eve(
    csv_path: str = "results/phase10/data/eve_probability_summary.csv",
    output_path: str = "results/phase10/figures/key_rate_vs_eve.png",
) -> str:
    """Plot final secret key rate as a function of Eve's interception probability."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    p_eves: List[float] = []
    key_rates: List[float] = []
    key_stds: List[float] = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p_eves.append(float(row["eve_probability"]))
            key_rates.append(float(row["final_key_rate_mean"]) * 100.0)
            key_stds.append(float(row["final_key_rate_std"]) * 100.0)

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)

    ax.plot(p_eves, key_rates, "o-", color="#10b981", linewidth=2.0, markersize=6, label=r"Final Key Rate ($R_{\text{secret}} = L_{\text{final}} / N_{\text{signals}}$)")
    ax.fill_between(
        p_eves,
        np.maximum(0.0, np.array(key_rates) - np.array(key_stds)),
        np.array(key_rates) + np.array(key_stds),
        color="#10b981",
        alpha=0.2,
        label=r"$\pm 1$ Standard Deviation",
    )

    # Vertical threshold line where eavesdropping exceeds 11% cutoff (~ p_eve = 44%)
    ax.axvline(0.44, color="#ef4444", linestyle="--", linewidth=1.8, label=r"Cutoff Threshold ($p_{\text{eve}} \approx 44\%$)")

    ax.set_xlabel(r"Eve Interception Probability ($p_{\text{eve}}$)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Final Secret Key Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("Phase 10: Secret Key Rate Suppression under Intercept-Resend Attack", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-1.0, 35.0)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.9)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def plot_key_rate_vs_noise(
    csv_path: str = "results/phase10/data/noise_sweep_summary.csv",
    output_path: str = "results/phase10/figures/key_rate_vs_noise.png",
) -> str:
    """Plot final secret key rate across Bit-Flip, Phase-Flip, and Depolarizing channels."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    model_data: Dict[str, Dict[str, List[float]]] = {
        "bit_flip": {"p": [], "rate": []},
        "phase_flip": {"p": [], "rate": []},
        "depolarizing": {"p": [], "rate": []},
    }

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = row["noise_model"]
            if m in model_data:
                model_data[m]["p"].append(float(row["noise_probability"]))
                model_data[m]["rate"].append(float(row["final_key_rate_mean"]) * 100.0)

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)
    colors = {"bit_flip": "#3b82f6", "phase_flip": "#8b5cf6", "depolarizing": "#f59e0b"}
    labels = {"bit_flip": "Bit-Flip Channel", "phase_flip": "Phase-Flip Channel", "depolarizing": "Depolarizing Channel"}

    for m, d in model_data.items():
        if d["p"]:
            ax.plot(d["p"], d["rate"], "o-", color=colors[m], linewidth=1.8, markersize=5, label=labels[m])

    ax.set_xlabel("Physical Quantum Noise Probability (p)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Final Secret Key Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("Phase 10: Secret Key Rate vs. Quantum Decoherence Noise", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(-0.005, 0.205)
    ax.set_ylim(-1.0, 35.0)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.9)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def plot_acceptance_rates(
    eve_csv: str = "results/phase10/data/eve_probability_summary.csv",
    noise_csv: str = "results/phase10/data/noise_sweep_summary.csv",
    output_path: str = "results/phase10/figures/acceptance_rates.png",
) -> str:
    """Plot protocol acceptance probability curves under increasing eavesdropping and noise."""
    if not os.path.exists(eve_csv) or not os.path.exists(noise_csv):
        raise FileNotFoundError("Missing input CSV datasets.")

    p_eves: List[float] = []
    eve_accept: List[float] = []
    with open(eve_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p_eves.append(float(row["eve_probability"]))
            eve_accept.append(float(row["acceptance_rate"]) * 100.0)

    depol_p: List[float] = []
    depol_accept: List[float] = []
    with open(noise_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["noise_model"] == "depolarizing":
                depol_p.append(float(row["noise_probability"]))
                depol_accept.append(float(row["acceptance_rate"]) * 100.0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=200)

    # Subplot 1: Acceptance vs Eve
    ax1.plot(p_eves, eve_accept, "s-", color="#ef4444", linewidth=2.0, markersize=6)
    ax1.set_xlabel(r"Eve Interception Probability ($p_{\text{eve}}$)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Protocol Acceptance Rate (%)", fontsize=11, fontweight="bold")
    ax1.set_title("Acceptance vs. Eavesdropping", fontsize=12, fontweight="bold")
    ax1.set_xlim(-0.02, 1.02)
    ax1.set_ylim(-5.0, 105.0)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Subplot 2: Acceptance vs Noise
    ax2.plot(depol_p, depol_accept, "o-", color="#f59e0b", linewidth=2.0, markersize=6)
    ax2.set_xlabel("Depolarizing Noise Probability (λ)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Protocol Acceptance Rate (%)", fontsize=11, fontweight="bold")
    ax2.set_title("Acceptance vs. Quantum Noise", fontsize=12, fontweight="bold")
    ax2.set_xlim(-0.005, 0.205)
    ax2.set_ylim(-5.0, 105.0)
    ax2.grid(True, linestyle=":", alpha=0.6)

    fig.suptitle("Phase 10: Security Abort Threshold Enforcement (QBER ≤ 11.0%)", fontsize=14, fontweight="bold", y=1.02)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def main() -> None:
    """Run all key rate and acceptance visualization routines."""
    plot_key_rate_vs_eve()
    plot_key_rate_vs_noise()
    plot_acceptance_rates()


if __name__ == "__main__":
    main()
