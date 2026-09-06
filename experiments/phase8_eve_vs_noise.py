"""Experiment 4: Eavesdropping vs. Environmental Quantum Noise.

Compares 4 fundamental physical transmission regimes:
1. No Eve + Ideal Channel (Noiseless Baseline)
2. Eve + Ideal Channel (Pure Eavesdropping Disturbance)
3. No Eve + Noisy Channel (Environmental Noise without Eavesdropping)
4. Eve + Noisy Channel (Compound Eavesdropping + Noise Degradation)

Outputs:
- Comparative bar plot saved to results/phase8_eve_vs_noise.png.
- Detailed analysis explaining why QBER alone cannot uniquely discriminate Eve from environmental noise.
"""

from __future__ import annotations

import os
import sys
from typing import Dict

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from noise.depolarizing import DepolarizingNoise
from src.alice import Alice
from src.bob import Bob
from src.eve import Eve
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel
from visualization.noise_plots import plot_eve_vs_noise_composition


def run_eve_vs_noise_experiment(
    signals_per_condition: int = 4000,
    depol_rate: float = 0.08,
    seed: int = 300,
) -> None:
    """Benchmark the four operational conditions of the physical channel.

    Args:
        signals_per_condition: Number of transmitted quantum signals per condition.
        depol_rate: Depolarization parameter for the noisy channel conditions.
        seed: Base random seed for reproducible runs.
    """
    print("=" * 84)
    print("        PHASE 8 EXPERIMENT 4: EAVESDROPPING VS. QUANTUM CHANNEL NOISE")
    print("=" * 84)
    print(f"Signals Transmitted per Condition: {signals_per_condition}")
    print(f"Depolarizing Noise Rate:           {depol_rate:.2f}")
    print(f"Base Random Seed:                  {seed}\n")

    conditions = [
        ("No Eve + Ideal", False, False),
        ("Eve + Ideal", True, False),
        ("No Eve + Noise", False, True),
        ("Eve + Noise", True, True),
    ]

    header = (
        f"{'Condition':<18} | {'Signals':<8} | {'Sifted Key':<11} | "
        f"{'Errors':<8} | {'QBER (%)':<10} | {'Security Assessment'}"
    )
    print(header)
    print("-" * len(header))

    plot_data: Dict[str, float] = {}

    for idx, (label, use_eve, use_noise) in enumerate(conditions):
        seed_iter = seed + idx * 50
        eve_inst = Eve(seed=seed_iter + 2, interception_probability=1.0) if use_eve else None
        noise_inst = (
            DepolarizingNoise(probability=depol_rate, seed=seed_iter + 3) if use_noise else None
        )

        alice = Alice(number_of_qubits=signals_per_condition, seed=seed_iter)
        bob = Bob(seed=seed_iter + 1)
        channel = QuantumChannel(eve=eve_inst, noise=noise_inst)

        signals = alice.get_quantum_signals()
        received = channel.transmit(signals)
        bob.receive_and_measure(received)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_res = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        # Standard QKD security assessment
        if qber_res.qber_percentage <= 11.0:
            status = "SECURE (< 11% threshold)"
        else:
            status = "ABORT (> 11% threshold)"

        row = (
            f"{label:<18} | {signals_per_condition:<8} | {sifted.sifted_key_length:<11} | "
            f"{qber_res.error_count:<8} | {qber_res.qber_percentage:<10.2f} | {status}"
        )
        print(row)

        plot_data[label] = qber_res.qber_percentage

    print("=" * 84)
    print("\nCryptographic Implication:")
    print("  Alice and Bob observe only classical bit errors in their sifted keys.")
    print("  They CANNOT physically distinguish whether an observed error originated from")
    print("  Eve's measurement or thermal/depolarizing noise in the optical fiber.")
    print("  Conservative QKD security proofs must assume ALL errors are caused by Eve.")

    # Visualization
    img_path = plot_eve_vs_noise_composition(plot_data)
    print(f"\n[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_eve_vs_noise_experiment()
