"""Experiment 1: Quantum Noise Model Comparison.

Compares transmission fidelity across 4 channel environments:
1. Ideal Channel (p = 0.00)
2. Bit-Flip Noise (p = 0.05)
3. Phase-Flip Noise (p = 0.05)
4. Depolarizing Noise (p = 0.05)

Outputs:
- Formatted terminal table reporting noise model, probability, signals, sifted key, errors, and QBER.
- Bar chart saved to results/phase8_noise_comparison.png.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Any

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
from visualization.noise_plots import plot_noise_model_comparison


def run_noise_comparison_experiment(
    signals_per_trial: int = 4000,
    noise_param: float = 0.05,
    seed: int = 42,
) -> None:
    """Run comparative benchmark across all implemented quantum noise channels.

    Args:
        signals_per_trial: Number of transmitted quantum signals per condition.
        noise_param: Physical noise parameter for the noisy channels.
        seed: Base random seed for reproducibility.
    """
    print("=" * 80)
    print("        PHASE 8 EXPERIMENT 1: QUANTUM NOISE MODEL COMPARISON")
    print("=" * 80)
    print(f"Total Signals Transmitted per Condition: {signals_per_trial}")
    print(f"Noise Parameter for Noisy Models:       {noise_param:.2f}")
    print(f"Base Seed:                              {seed}\n")

    configurations = [
        ("None (Ideal)", None, 0.0),
        ("Bit-Flip", BitFlipNoise(probability=noise_param, seed=seed + 1), noise_param),
        ("Phase-Flip", PhaseFlipNoise(probability=noise_param, seed=seed + 2), noise_param),
        ("Depolarizing", DepolarizingNoise(probability=noise_param, seed=seed + 3), noise_param),
    ]

    header = (
        f"{'Noise Model':<16} | {'Probability':<11} | {'Signals':<8} | "
        f"{'Sifted Key':<11} | {'Errors':<8} | {'QBER (%)':<10}"
    )
    print(header)
    print("-" * len(header))

    plot_data: Dict[str, Dict[str, Any]] = {}

    for idx, (label, noise_model, prob) in enumerate(configurations):
        alice = Alice(number_of_qubits=signals_per_trial, seed=seed + idx * 10)
        bob = Bob(seed=seed + idx * 10 + 1)
        channel = QuantumChannel(noise=noise_model)

        signals = alice.get_quantum_signals()
        received = channel.transmit(signals)
        bob.receive_and_measure(received)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_res = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        row = (
            f"{label:<16} | {prob:<11.2f} | {signals_per_trial:<8} | "
            f"{sifted.sifted_key_length:<11} | {qber_res.error_count:<8} | "
            f"{qber_res.qber_percentage:<10.2f}"
        )
        print(row)

        plot_data[label] = {
            "probability": prob,
            "qber_pct": qber_res.qber_percentage,
            "sifted_length": sifted.sifted_key_length,
            "error_count": qber_res.error_count,
        }

    print("=" * 80)

    # Visualization
    img_path = plot_noise_model_comparison(plot_data)
    print(f"\n[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_noise_comparison_experiment()
