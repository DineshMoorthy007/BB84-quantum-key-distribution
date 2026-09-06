"""Experiment 5: Statistical Variability of Quantum Noise.

Evaluates stochastic fluctuations across multiple independent simulation trials
(Monte Carlo repetitions) for each quantum noise channel:
- Bit-Flip Noise (p = 0.10)
- Phase-Flip Noise (p = 0.10)
- Depolarizing Noise (lambda = 0.10)

Calculates:
- Mean QBER
- Standard Deviation (sigma)
- Minimum QBER
- Maximum QBER

Outputs:
- Terminal statistical summary table.
- Error bar plot saved to results/phase8_statistics.png.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List
import numpy as np

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from noise.bit_flip import BitFlipNoise
from noise.depolarizing import DepolarizingNoise
from noise.phase_flip import PhaseFlipNoise
from src.alice import Alice
from src.bob import Bob
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel
from visualization.noise_plots import plot_noise_statistics_distribution


def run_statistics_experiment(
    signals_per_trial: int = 2000,
    noise_rate: float = 0.10,
    repetitions: int = 10,
    seed: int = 400,
) -> None:
    """Execute repeated stochastic trials across noise models.

    Args:
        signals_per_trial: Number of transmitted quantum signals per trial.
        noise_rate: Configured noise rate parameter.
        repetitions: Number of repeated runs per noise channel.
        seed: Base random seed.
    """
    print("=" * 86)
    print("        PHASE 8 EXPERIMENT 5: STATISTICAL VARIABILITY OF QUANTUM NOISE")
    print("=" * 86)
    print(f"Signals per Trial: {signals_per_trial}")
    print(f"Noise Parameter:   {noise_rate:.2f}")
    print(f"Repetitions:       {repetitions} runs per noise channel\n")

    models = [
        ("Bit-Flip (p=0.10)", BitFlipNoise),
        ("Phase-Flip (p=0.10)", PhaseFlipNoise),
        ("Depolarizing (p=0.10)", DepolarizingNoise),
    ]

    stats_summary: Dict[str, Dict[str, float]] = {}

    header = (
        f"{'Noise Model':<24} | {'Mean QBER':<11} | {'Std Dev (σ)':<12} | "
        f"{'Min QBER':<10} | {'Max QBER':<10}"
    )
    print(header)
    print("-" * len(header))

    for model_name, model_cls in models:
        qber_runs: List[float] = []

        for rep in range(repetitions):
            rep_seed = seed + rep * 17
            noise = model_cls(probability=noise_rate, seed=rep_seed + 2)

            alice = Alice(number_of_qubits=signals_per_trial, seed=rep_seed)
            bob = Bob(seed=rep_seed + 1)
            channel = QuantumChannel(noise=noise)

            signals = alice.get_quantum_signals()
            received = channel.transmit(signals)
            bob.receive_and_measure(received)

            sifted = sift_from_alice_and_bob(alice, bob)
            qber_res = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)
            qber_runs.append(qber_res.qber_percentage)

        arr = np.array(qber_runs)
        mean_v = float(np.mean(arr))
        std_v = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        min_v = float(np.min(arr))
        max_v = float(np.max(arr))

        stats_summary[model_name] = {
            "mean": mean_v,
            "std": std_v,
            "min": min_v,
            "max": max_v,
        }

        row = (
            f"{model_name:<24} | {f'{mean_v:.2f}%':<11} | {f'{std_v:.2f}%':<12} | "
            f"{f'{min_v:.2f}%':<10} | {f'{max_v:.2f}%':<10}"
        )
        print(row)

    print("=" * 86)

    # Visualization
    img_path = plot_noise_statistics_distribution(stats_summary)
    print(f"\n[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_statistics_experiment()
