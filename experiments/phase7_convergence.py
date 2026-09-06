"""Experiment 3: Statistical Convergence of Intercept-Resend QBER.

Demonstrates that the observed QBER under a full intercept-resend attack (p=1.0)
statistically converges to the theoretical expectation of 25.0% as the number of
transmitted signals increases across multiple orders of magnitude.

Signal counts evaluated:
[100, 500, 1000, 5000, 10000, 20000]

Outputs:
- Terminal table recording signal count, sifted key length, error count, and QBER.
- Convergence line plot saved to results/phase7_convergence.png.
"""

from __future__ import annotations

import os
import sys
from typing import List, Sequence

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
from visualization.eve_plots import plot_statistical_convergence


def run_convergence_experiment(
    signal_counts: Sequence[int] = (100, 500, 1000, 5000, 10000, 20000),
    seed: int = 42,
) -> None:
    """Run convergence evaluation across increasing signal counts.

    Args:
        signal_counts: Sequence of sample sizes to simulate.
        seed: Random seed for reproducible trials.
    """
    print("=" * 82)
    print("       PHASE 7 EXPERIMENT 3: STATISTICAL CONVERGENCE OF INTERCEPT-RESEND QBER")
    print("=" * 82)
    print("Theoretical Target: QBER = 25.00% (p_wrong_basis=0.5, p_error|wrong=0.5)\n")

    header = (
        f"{'Signals (N)':<12} | {'Sifted Key':<11} | {'Errors':<8} | "
        f"{'Observed QBER':<14} | {'Deviation from 25%':<18}"
    )
    print(header)
    print("-" * len(header))

    recorded_counts: List[int] = []
    recorded_qbers: List[float] = []

    for idx, count in enumerate(signal_counts):
        # Progressively execute each sample size
        seed_iter = seed + idx * 100
        alice = Alice(number_of_qubits=count, seed=seed_iter)
        bob = Bob(seed=seed_iter + 1)
        eve = Eve(seed=seed_iter + 2, interception_probability=1.0)
        channel = QuantumChannel(eve=eve)

        signals = alice.get_quantum_signals()
        received = channel.transmit(signals)
        bob.receive_and_measure(received)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_res = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        delta = qber_res.qber_percentage - 25.0
        sign = "+" if delta >= 0 else ""
        delta_str = f"{sign}{delta:.2f}%"

        row = (
            f"{count:<12} | {sifted.sifted_key_length:<11} | {qber_res.error_count:<8} | "
            f"{f'{qber_res.qber_percentage:.2f}%':<14} | {delta_str:<18}"
        )
        print(row)

        recorded_counts.append(count)
        recorded_qbers.append(qber_res.qber_percentage)

    print("=" * 82)

    # -------------------------------------------------------------
    # VISUALIZATION
    # -------------------------------------------------------------
    img_path = plot_statistical_convergence(
        signal_counts=recorded_counts,
        qber_values=recorded_qbers,
    )
    print(f"\n[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_convergence_experiment()
