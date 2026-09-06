"""Experiment 1: No-Eve vs Full-Eve (Intercept-Resend) comparison.

Compares an ideal BB84 quantum transmission against a full intercept-resend attack
(interception_probability = 1.0) under identical protocol conditions.

Outputs:
- Terminal report with total signals, sifted key lengths, error counts, QBER, and Eve stats.
- Visual comparison bar chart saved to results/phase7_eve_comparison.png.
"""

from __future__ import annotations

import os
import sys

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
from visualization.eve_plots import plot_no_eve_vs_eve_comparison


def run_eve_comparison(num_signals: int = 4000, seed: int = 42) -> None:
    """Execute comparative benchmark between No-Eve and Full-Eve conditions.

    Args:
        num_signals: Number of quantum signals transmitted per condition.
        seed: Base random seed for reproducibility.
    """
    print("=" * 72)
    print("       PHASE 7 EXPERIMENT 1: NO-EVE VS. FULL-EVE BENCHMARK")
    print("=" * 72)
    print(f"Total Signals Transmitted per Condition: {num_signals}")
    print(f"Base Seed: {seed}\n")

    # -------------------------------------------------------------
    # CONDITION A: NO EVE (Ideal Quantum Channel)
    # -------------------------------------------------------------
    print("[1/2] Executing Condition A: No Eve (Ideal Channel)...")
    alice_a = Alice(number_of_qubits=num_signals, seed=seed)
    bob_a = Bob(seed=seed + 1)
    channel_a = QuantumChannel()  # No Eve attached

    signals_a = alice_a.get_quantum_signals()
    received_a = channel_a.transmit(signals_a)
    bob_a.receive_and_measure(received_a)

    sifted_a = sift_from_alice_and_bob(alice_a, bob_a)
    qber_a = calculate_qber(sifted_a.alice_sifted_key, sifted_a.bob_sifted_key)

    # -------------------------------------------------------------
    # CONDITION B: FULL EVE (Intercept-Resend, p = 1.0)
    # -------------------------------------------------------------
    print("[2/2] Executing Condition B: Full Eve (p = 1.0 Intercept-Resend)...")
    alice_b = Alice(number_of_qubits=num_signals, seed=seed)
    bob_b = Bob(seed=seed + 1)
    eve_b = Eve(seed=seed + 2, interception_probability=1.0)
    channel_b = QuantumChannel(eve=eve_b)

    signals_b = alice_b.get_quantum_signals()
    received_b = channel_b.transmit(signals_b)
    bob_b.receive_and_measure(received_b)

    sifted_b = sift_from_alice_and_bob(alice_b, bob_b)
    qber_b = calculate_qber(sifted_b.alice_sifted_key, sifted_b.bob_sifted_key)

    # Eve statistics
    eve_z_bases = sum(1 for b in eve_b.bases if b == "Z")
    eve_x_bases = sum(1 for b in eve_b.bases if b == "X")

    # -------------------------------------------------------------
    # REPORT
    # -------------------------------------------------------------
    print("\n" + "=" * 72)
    print("                         SUMMARY RESULTS")
    print("=" * 72)
    header = f"{'Condition':<15} | {'Signals':<8} | {'Sifted Key':<11} | {'Errors':<7} | {'QBER (%)':<10} | {'Status'}"
    print(header)
    print("-" * len(header))

    row_a = (
        f"{'No Eve':<15} | {num_signals:<8} | {sifted_a.sifted_key_length:<11} | "
        f"{qber_a.error_count:<7} | {qber_a.qber_percentage:<9.2f}% | "
        f"{'SECURE (Ideal)'}"
    )
    row_b = (
        f"{'Full Eve (100%)':<15} | {num_signals:<8} | {sifted_b.sifted_key_length:<11} | "
        f"{qber_b.error_count:<7} | {qber_b.qber_percentage:<9.2f}% | "
        f"{'COMPROMISED (Eve Detected)'}"
    )
    print(row_a)
    print(row_b)
    print("=" * 72)

    print("\nEve Interception Statistics:")
    print(f"  - Intercepted Signals: {eve_b.intercepted_count} / {num_signals} ({eve_b.intercepted_count / num_signals:.1%})")
    print(f"  - Eve Z-basis measurements: {eve_z_bases} ({eve_z_bases / num_signals:.1%})")
    print(f"  - Eve X-basis measurements: {eve_x_bases} ({eve_x_bases / num_signals:.1%})")
    print(f"  - Theoretical Intercept-Resend QBER: 25.00%")
    print(f"  - Observed Intercept-Resend QBER:    {qber_b.qber_percentage:.2f}%\n")

    # -------------------------------------------------------------
    # VISUALIZATION
    # -------------------------------------------------------------
    plot_data = {
        "No Eve": {
            "qber_pct": qber_a.qber_percentage,
            "sifted_length": sifted_a.sifted_key_length,
            "error_count": qber_a.error_count,
        },
        "Full Eve": {
            "qber_pct": qber_b.qber_percentage,
            "sifted_length": sifted_b.sifted_key_length,
            "error_count": qber_b.error_count,
        },
    }
    img_path = plot_no_eve_vs_eve_comparison(plot_data)
    print(f"[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_eve_comparison()
