"""Experiment 2: Eve Interception Probability Sweep.

Investigates QBER behavior as Eve's interception probability varies across:
[0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0].

Outputs:
- Formatted tabular data of interception rates, sifted key lengths, and measured QBER.
- Scatter and line plot saved to results/phase7_eve_probability.png.
"""

from __future__ import annotations

import os
import sys
from typing import List

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.alice import Alice
from src.bob import Bob
from src.eve import Eve
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel
from visualization.eve_plots import plot_interception_probability_sweep


def run_eve_probability_experiment(
    signals_per_prob: int = 3000,
    probabilities: Sequence[float] = (0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0),
    base_seed: int = 100,
) -> None:
    """Execute interception probability sweep and record QBER statistics.

    Args:
        signals_per_prob: Number of transmitted quantum signals per probability level.
        probabilities: Sequence of interception probabilities to evaluate.
        base_seed: Base seed for reproducible runs.
    """
    print("=" * 78)
    print("      PHASE 7 EXPERIMENT 2: EVE INTERCEPTION PROBABILITY SWEEP")
    print("=" * 78)
    print(f"Signals per Probability: {signals_per_prob}")
    print(f"Probabilities Evaluated: {list(probabilities)}\n")

    header = (
        f"{'p (Target)':<10} | {'Intercepted':<14} | {'Sifted Key':<11} | "
        f"{'Errors':<8} | {'QBER (%)':<10} | {'Theory (%)'}"
    )
    print(header)
    print("-" * len(header))

    recorded_probs: List[float] = []
    recorded_qbers: List[float] = []
    recorded_intercepted: List[int] = []

    for idx, prob in enumerate(probabilities):
        # Deterministic seed progression per trial
        seed_alice = base_seed + idx * 10
        seed_bob = base_seed + idx * 10 + 1
        seed_eve = base_seed + idx * 10 + 2

        alice = Alice(number_of_qubits=signals_per_prob, seed=seed_alice)
        bob = Bob(seed=seed_bob)
        eve = Eve(seed=seed_eve, interception_probability=prob)
        channel = QuantumChannel(eve=eve)

        signals = alice.get_quantum_signals()
        received = channel.transmit(signals)
        bob.receive_and_measure(received)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_res = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        theory_qber = prob * 25.0
        actual_ratio = eve.intercepted_count / signals_per_prob

        row = (
            f"{prob:<10.2f} | {f'{eve.intercepted_count} ({actual_ratio:.1%})':<14} | "
            f"{sifted.sifted_key_length:<11} | {qber_res.error_count:<8} | "
            f"{qber_res.qber_percentage:<10.2f} | {theory_qber:.2f}%"
        )
        print(row)

        recorded_probs.append(prob)
        recorded_qbers.append(qber_res.qber_percentage)
        recorded_intercepted.append(eve.intercepted_count)

    print("=" * 78)

    # -------------------------------------------------------------
    # VISUALIZATION
    # -------------------------------------------------------------
    img_path = plot_interception_probability_sweep(
        probabilities=recorded_probs,
        qber_values=recorded_qbers,
        intercepted_counts=recorded_intercepted,
        total_signals=signals_per_prob,
    )
    print(f"\n[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_eve_probability_experiment()
