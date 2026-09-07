"""Phase 10 Visualization: 2D Heatmaps for Compound Eve + Noise Parameter Grid.

Generates:
1. 2D Heatmap of Quantum Bit Error Rate (QBER %) across the 5x5 parameter grid of
   Eve Interception Probability vs. Physical Noise Probability.
2. 2D Heatmap of Final Distilled Secret Key Rate (%) across the same parameter grid.

Inputs:
- results/phase10/data/eve_noise_matrix_summary.csv

Outputs:
- results/phase10/figures/eve_noise_heatmap.png
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
import sys
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def plot_eve_noise_heatmaps(
    csv_path: str = "results/phase10/data/eve_noise_matrix_summary.csv",
    output_path: str = "results/phase10/figures/eve_noise_heatmap.png",
) -> str:
    """Generate dual 2D heatmaps illustrating QBER and final secret key rate across the parameter space."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required CSV dataset: {csv_path}")

    eve_vals_set = set()
    noise_vals_set = set()
    data_map: Dict[Tuple[float, float], Dict[str, float]] = {}

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p_eve = float(row["eve_probability"])
            p_noise = float(row["noise_probability"])
            eve_vals_set.add(p_eve)
            noise_vals_set.add(p_noise)
            data_map[(p_eve, p_noise)] = {
                "qber": float(row["qber_mean"]) * 100.0,
                "key_rate": float(row["final_key_rate_mean"]) * 100.0,
            }

    eve_vals = sorted(list(eve_vals_set))
    noise_vals = sorted(list(noise_vals_set))

    qber_grid = np.zeros((len(eve_vals), len(noise_vals)))
    rate_grid = np.zeros((len(eve_vals), len(noise_vals)))

    for i, p_eve in enumerate(eve_vals):
        for j, p_noise in enumerate(noise_vals):
            metrics = data_map.get((p_eve, p_noise), {"qber": 0.0, "key_rate": 0.0})
            qber_grid[i, j] = metrics["qber"]
            rate_grid[i, j] = metrics["key_rate"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=200)

    # 1. QBER Heatmap
    im1 = ax1.imshow(qber_grid, cmap="YlOrRd", origin="lower", aspect="auto", vmin=0, vmax=35)
    cbar1 = fig.colorbar(im1, ax=ax1)
    cbar1.set_label("Measured QBER (%)", fontsize=10, fontweight="bold")

    ax1.set_xticks(range(len(noise_vals)))
    ax1.set_xticklabels([f"{p:.2f}" for p in noise_vals], fontsize=10)
    ax1.set_yticks(range(len(eve_vals)))
    ax1.set_yticklabels([f"{p:.2f}" for p in eve_vals], fontsize=10)
    ax1.set_xlabel("Depolarizing Noise (λ)", fontsize=11, fontweight="bold")
    ax1.set_ylabel(r"Eve Interception Probability ($p_{\text{eve}}$)", fontsize=11, fontweight="bold")
    ax1.set_title("Compound QBER Grid (%)", fontsize=12, fontweight="bold")

    # Annotate QBER values
    for i in range(len(eve_vals)):
        for j in range(len(noise_vals)):
            val = qber_grid[i, j]
            color = "white" if val > 18.0 else "black"
            ax1.text(j, i, f"{val:.1f}%", ha="center", va="center", color=color, fontsize=10, fontweight="bold")

    # 2. Secret Key Rate Heatmap
    im2 = ax2.imshow(rate_grid, cmap="Blues", origin="lower", aspect="auto", vmin=0, vmax=30)
    cbar2 = fig.colorbar(im2, ax=ax2)
    cbar2.set_label("Final Secret Key Rate (%)", fontsize=10, fontweight="bold")

    ax2.set_xticks(range(len(noise_vals)))
    ax2.set_xticklabels([f"{p:.2f}" for p in noise_vals], fontsize=10)
    ax2.set_yticks(range(len(eve_vals)))
    ax2.set_yticklabels([f"{p:.2f}" for p in eve_vals], fontsize=10)
    ax2.set_xlabel("Depolarizing Noise (λ)", fontsize=11, fontweight="bold")
    ax2.set_ylabel(r"Eve Interception Probability ($p_{\text{eve}}$)", fontsize=11, fontweight="bold")
    ax2.set_title("Final Secret Key Rate Grid (%)", fontsize=12, fontweight="bold")

    # Annotate Key Rate values
    for i in range(len(eve_vals)):
        for j in range(len(noise_vals)):
            val = rate_grid[i, j]
            color = "white" if val > 15.0 else "black"
            ax2.text(j, i, f"{val:.1f}%", ha="center", va="center", color=color, fontsize=10, fontweight="bold")

    fig.suptitle("Phase 10: Compound Eavesdropping and Quantum Decoherence 5x5 Matrix", fontsize=14, fontweight="bold", y=0.98)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[✓] Saved figure: {output_path}")
    return output_path


def main() -> None:
    """Run heatmap visualization routine."""
    plot_eve_noise_heatmaps()


if __name__ == "__main__":
    main()
