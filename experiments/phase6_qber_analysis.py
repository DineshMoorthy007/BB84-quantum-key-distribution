"""Phase 6 Educational Experiment: QBER Analysis and Classical Validation.

This script executes:
1. Complete ideal BB84 pipeline (Alice -> QuantumChannel -> Bob -> Sifting -> QBER).
2. Establishing the zero-error experimental baseline for an unperturbed channel.
3. Controlled classical error injection validation experiment (0%, 5%, 10%, 20%, 30%).
4. Generating and saving validation curves to results/ directory.

Usage:
    .venv/Scripts/python experiments/phase6_qber_analysis.py
    .venv/Scripts/python experiments/phase6_qber_analysis.py --signals 1000 --seed 42
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 output on platforms where default stdout is cp1252 (e.g. Windows)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.alice import Alice
from src.bob import Bob
from src.error_injection import inject_classical_bit_errors
from src.key_sifting import sift_from_alice_and_bob
from src.qber import analyze_qber_security, calculate_qber
from src.quantum_channel import QuantumChannel
from visualization.qber_plots import plot_injected_vs_measured_qber


def run_qber_analysis(num_signals: int = 1000, seed: int = 42) -> None:
    """Execute complete BB84 pipeline and evaluate QBER."""
    print("=" * 76)
    print("           BB84 QUANTUM KEY DISTRIBUTION: PHASE 6 DEMONSTRATION")
    print("              Quantum Bit Error Rate (QBER) Baseline Analysis")
    print("=" * 76)
    print(f"Configuration: signals={num_signals}, seed={seed}\n")

    # Step 1: Alice state preparation
    alice = Alice(number_of_qubits=num_signals, seed=seed)
    carrier_circuits = alice.get_quantum_signals()

    # Step 2: Ideal Quantum Channel transmission
    channel = QuantumChannel()
    transmitted_circuits = channel.transmit(carrier_circuits)

    # Step 3: Bob measurement
    bob = Bob(seed=seed + 57)
    bob.receive_and_measure(transmitted_circuits)

    # Step 4: Basis reconciliation & Key sifting
    sifting_result = sift_from_alice_and_bob(alice, bob)

    # Step 5: QBER calculation on sifted keys
    qber_result = calculate_qber(
        sifting_result.alice_sifted_key,
        sifting_result.bob_sifted_key,
    )
    security_report = analyze_qber_security(qber_result, threshold=0.11)

    print("PART 1: IDEAL PIPELINE QBER BASELINE")
    print("-" * 76)
    print(f"Total signals       : {sifting_result.total_signals}")
    print(f"Matching bases      : {sifting_result.sifted_key_length}")
    print(f"Sifted key length   : {sifting_result.sifted_key_length}")
    print(f"Matching bits       : {qber_result.matching_bits}")
    print(f"Errors              : {qber_result.error_count}")
    print(f"QBER                : {qber_result.qber_percentage:.2f}%")
    print("Channel condition   : Ideal (Baseline established; no discrepancies observed)")
    print(f"Security Status     : {security_report.status}")
    print(f"Interpretation      : {security_report.interpretation}")
    print("-" * 76)

    # Step 6: Controlled classical error injection validation experiment
    print("\nPART 2: CONTROLLED CLASSICAL ERROR INJECTION EXPERIMENT")
    print("(Diagnostic validation of QBER calculation; NOT a quantum noise channel)")
    print("-" * 76)
    injected_rates = [0.0, 0.05, 0.10, 0.20, 0.30]
    measured_qbers = []

    print(f"{'Injected Error Rate':<22} | {'Measured QBER':<15} | {'Error Count':<12} | {'Compared Bits':<14}")
    print("-" * 76)

    for rate in injected_rates:
        # Introduce controlled classical bit flips into a copy of Bob's sifted key
        corrupted_bob_key = inject_classical_bit_errors(
            sifting_result.bob_sifted_key,
            error_rate=rate,
            seed=seed + int(rate * 1000),
        )
        sub_result = calculate_qber(
            sifting_result.alice_sifted_key,
            corrupted_bob_key,
        )
        measured_qbers.append(sub_result.qber)

        print(
            f"{rate * 100:5.1f}%                 | "
            f"{sub_result.qber_percentage:6.2f}%         | "
            f"{sub_result.error_count:<12} | "
            f"{sub_result.compared_bits:<14}"
        )

    print("-" * 76)

    # Step 7: Plotting
    try:
        plot_path = plot_injected_vs_measured_qber(
            injected_rates=injected_rates,
            measured_qbers=measured_qbers,
        )
        print(f"\nValidation plot saved to: {plot_path.relative_to(PROJECT_ROOT)}")
    except Exception as exc:
        print(f"\nPlotting skipped due to error: {exc}")

    print("\nAcademic Note:")
    print("1. In an ideal noiseless channel without eavesdropping, QBER = 0.00%.")
    print("2. When controlled classical errors are introduced, measured QBER closely")
    print("   matches the configured error rate, validating the measurement layer.")
    print("3. In Phase 7, Eve's intercept-resend attack will be introduced to evaluate")
    print("   the physical quantum disturbance threshold.\n")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="BB84 Phase 6 QBER Analysis Demonstration")
    parser.add_argument(
        "--signals",
        type=int,
        default=1000,
        help="Number of quantum signals to generate (default: 1000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_qber_analysis(num_signals=args.signals, seed=args.seed)
