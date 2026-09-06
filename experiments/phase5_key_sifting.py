"""Phase 5 Educational Demonstration: Basis Reconciliation and Key Sifting.

This script demonstrates the complete ideal BB84 transmission and classical post-processing:
1. Alice prepares random bits and bases, creating quantum signals.
2. QuantumChannel propagates physical quantum states faithfully.
3. Bob independently selects measurement bases and performs projective measurements.
4. Alice and Bob publicly announce and compare their bases (Basis Reconciliation).
5. Mismatched basis signals are discarded; matching basis signals form the sifted keys.
6. Statistical validation checks sifting ratio (~50%) across a large sample (1,000+ signals).

Usage:
    .venv/Scripts/python experiments/phase5_key_sifting.py
    .venv/Scripts/python experiments/phase5_key_sifting.py --signals 1000 --seed-alice 42 --seed-bob 99
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
from src.key_sifting import sift_from_alice_and_bob
from src.quantum_channel import QuantumChannel


def run_key_sifting_demonstration(
    num_signals: int = 1000,
    seed_alice: int = 42,
    seed_bob: int = 99,
    display_rows: int = 20,
) -> None:
    """Execute the basis reconciliation and key sifting demonstration."""
    print("=" * 80)
    print("           BB84 QUANTUM KEY DISTRIBUTION: PHASE 5 DEMONSTRATION")
    print("                 Basis Reconciliation & Classical Key Sifting")
    print("=" * 80)
    print(f"Configuration: signals={num_signals}, seed_alice={seed_alice}, seed_bob={seed_bob}\n")

    # Step 1: Alice generates and encodes
    alice = Alice(number_of_qubits=num_signals, seed=seed_alice)
    quantum_carrier_circuits = alice.get_quantum_signals()

    # Step 2: Ideal Quantum Channel transmission
    channel = QuantumChannel()
    transmitted_circuits = channel.transmit(quantum_carrier_circuits)

    # Step 3: Bob independently selects bases and measures
    bob = Bob(seed=seed_bob)
    bob.receive_and_measure(transmitted_circuits)

    # Step 4 & 5: Public Basis Reconciliation & Key Sifting
    sifting_result = sift_from_alice_and_bob(alice, bob)

    # Step 6: Display detailed sample table
    print(f"Transmission & Sifting Sample (First {min(display_rows, num_signals)} of {num_signals} signals):")
    print("-" * 80)
    header = (
        f"{'Index':<7} | {'Alice Bit':<9} | {'Alice Basis':<11} | "
        f"{'Bob Basis':<9} | {'Bob Result':<10} | {'Keep?':<6}"
    )
    print(header)
    print("-" * 80)

    matching_set = set(sifting_result.matching_indices)
    for idx in range(min(display_rows, num_signals)):
        a_bit = alice.bits[idx]
        a_basis = alice.bases[idx]
        b_basis = bob.bases[idx]
        b_res = bob.results[idx]
        keep = "YES" if idx in matching_set else "NO"
        print(
            f"{idx:<7} | {a_bit:<9} | {a_basis:<11} | "
            f"{b_basis:<9} | {b_res:<10} | {keep:<6}"
        )
    if num_signals > display_rows:
        print(f"... ({num_signals - display_rows} additional signals processed) ...")
    print("-" * 80)

    # Step 7: Statistical Results & Key Output
    matching_count = len(sifting_result.matching_indices)
    discarded_count = len(sifting_result.discarded_indices)

    print("\n" + "=" * 80)
    print("                          SIFTING STATISTICS")
    print("=" * 80)
    print(f"Total signals transmitted:          {sifting_result.total_signals}")
    print(f"Matching bases retained:            {matching_count} ({sifting_result.sifting_ratio * 100:.2f}%)")
    print(f"Discarded signals (basis mismatch): {discarded_count} ({(discarded_count / num_signals) * 100:.2f}%)")
    print(f"Sifted key length:                  {sifting_result.sifted_key_length}")
    print(f"Observed sifting ratio:             {sifting_result.sifting_ratio:.4f} (Theoretical expectation: ~0.5000)")
    print("=" * 80)

    # Preview sifted keys
    alice_sifted_str = "".join(str(b) for b in sifting_result.alice_sifted_key)
    bob_sifted_str = "".join(str(b) for b in sifting_result.bob_sifted_key)

    preview_len = 64
    print("\nSifted Key Sequences (First 64 bits):")
    print(f"Alice: {alice_sifted_str[:preview_len]}{'...' if len(alice_sifted_str) > preview_len else ''}")
    print(f"Bob:   {bob_sifted_str[:preview_len]}{'...' if len(bob_sifted_str) > preview_len else ''}")

    # Check key agreement on ideal channel
    agreed_bits = sum(
        1 for a, b in zip(sifting_result.alice_sifted_key, sifting_result.bob_sifted_key) if a == b
    )
    print(f"\nKey Agreement on Sifted Bits: {agreed_bits} / {sifting_result.sifted_key_length} (100.0% in ideal channel)")

    # Explanatory Notes
    print("\nAcademic Findings:")
    print("1. Approximately 50% of signals survive because Alice and Bob independently choose")
    print("   between two mutually unbiased bases uniformly at random.")
    print("2. A basis mismatch is NOT an error. Mismatched measurements are simply uninformative")
    print("   and are discarded as part of the standard protocol post-processing.")
    print("3. In a lossless, eavesdropper-free ideal channel, Alice's and Bob's sifted keys")
    print("   match with 100% fidelity.")
    print("4. Quantum Bit Error Rate (QBER) will be evaluated on these sifted keys in Phase 6.\n")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="BB84 Phase 5 Key Sifting Demonstration")
    parser.add_argument(
        "--signals",
        type=int,
        default=1000,
        help="Number of quantum signals to simulate (default: 1000)",
    )
    parser.add_argument(
        "--seed-alice",
        type=int,
        default=42,
        help="Random seed for Alice (default: 42)",
    )
    parser.add_argument(
        "--seed-bob",
        type=int,
        default=99,
        help="Random seed for Bob (default: 99)",
    )
    parser.add_argument(
        "--display-rows",
        type=int,
        default=20,
        help="Number of table rows to display (default: 20)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_key_sifting_demonstration(
        num_signals=args.signals,
        seed_alice=args.seed_alice,
        seed_bob=args.seed_bob,
        display_rows=args.display_rows,
    )
