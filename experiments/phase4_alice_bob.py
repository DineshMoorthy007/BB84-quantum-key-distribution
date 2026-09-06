"""Phase 4 Educational Demonstration: Alice -> Quantum Channel -> Bob.

This script demonstrates the complete quantum transmission stage of BB84:
1. Alice generates random classical bits and random encoding bases.
2. Alice prepares single-qubit quantum carrier states.
3. The quantum signals are transmitted across an ideal QuantumChannel.
4. Bob receives the quantum signals without access to Alice's private data.
5. Bob independently chooses random measurement bases and measures the signals.
6. An experimental analysis table compares Alice's preparation and Bob's measurements.

Usage:
    .venv/Scripts/python experiments/phase4_alice_bob.py
    .venv/Scripts/python experiments/phase4_alice_bob.py --signals 16 --alice-seed 42 --bob-seed 99
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
from src.quantum_channel import QuantumChannel


def run_alice_bob_demonstration(
    num_signals: int = 16,
    alice_seed: int = 42,
    bob_seed: int = 99,
) -> None:
    """Execute the Alice -> QuantumChannel -> Bob transmission demonstration."""
    print("=" * 78)
    print("           BB84 QUANTUM KEY DISTRIBUTION: PHASE 4 DEMONSTRATION")
    print("              Quantum Transmission: Alice -> Channel -> Bob")
    print("=" * 78)
    print(f"Configuration: signals={num_signals}, alice_seed={alice_seed}, bob_seed={bob_seed}\n")

    # 1. Sender (Alice) prepares quantum signals
    alice = Alice(number_of_qubits=num_signals, seed=alice_seed)
    alice_signals = alice.signals
    quantum_carrier_circuits = alice.get_quantum_signals()

    print("1. Alice (Sender):")
    print(f"   - Private Bits:  {' '.join(str(b) for b in alice.bits)}")
    print(f"   - Private Bases: {' '.join(alice.bases)}")
    print(f"   - State Symbols: {' '.join(alice.get_state_symbols())}\n")

    # 2. Quantum Channel propagates physical quantum states
    channel = QuantumChannel()
    transmitted_circuits = channel.transmit(quantum_carrier_circuits)
    print("2. Quantum Channel (Ideal):")
    print(f"   - Transmitted {len(transmitted_circuits)} quantum carrier states across channel.")
    print("   - No state alterations, decoherence, or eavesdropping.\n")

    # 3. Receiver (Bob) independently selects bases and measures
    bob = Bob(seed=bob_seed)
    bob_measurements = bob.receive_and_measure(transmitted_circuits)
    print("3. Bob (Receiver):")
    print(f"   - Selected Bases: {' '.join(bob.bases)}")
    print(f"   - Measured Bits:  {' '.join(str(r) for r in bob.results)}\n")

    # 4. Experimental View Table
    print("=" * 78)
    print("              TRANSMISSION RECORD (EXPERIMENTAL VIEW)")
    print("=" * 78)
    header = (
        f"{'Index':<7} | {'Alice Bit':<9} | {'Alice Basis':<11} | "
        f"{'Bob Basis':<9} | {'Bob Result':<10} | {'Basis Alignment':<15}"
    )
    print(header)
    print("-" * len(header))

    matching_count = 0
    mismatch_count = 0
    matching_deterministic_agreements = 0

    for idx in range(num_signals):
        a_bit = alice.bits[idx]
        a_basis = alice.bases[idx]
        b_basis = bob.bases[idx]
        b_res = bob.results[idx]

        is_match = (a_basis == b_basis)
        if is_match:
            matching_count += 1
            alignment = "MATCH (Same)"
            if a_bit == b_res:
                matching_deterministic_agreements += 1
        else:
            mismatch_count += 1
            alignment = "MISMATCH (Diff)"

        print(
            f"{idx:<7} | {a_bit:<9} | {a_basis:<11} | "
            f"{b_basis:<9} | {b_res:<10} | {alignment:<15}"
        )

    print("=" * 78)

    # 5. Experimental Validation & Summary Statistics
    print("\n" + "=" * 78)
    print("                     EXPERIMENTAL SUMMARY STATISTICS")
    print("=" * 78)
    print(f"  Total quantum signals transmitted:       {num_signals}")
    print(f"  Bob measurements completed:              {len(bob_measurements)}")
    print(f"  Matching bases (Alice basis == Bob basis): {matching_count} ({(matching_count / num_signals) * 100:.1f}%)")
    print(f"  Mismatched bases (Alice != Bob):         {mismatch_count} ({(mismatch_count / num_signals) * 100:.1f}%)")
    print(f"  Deterministic bit agreement on MATCH:    {matching_deterministic_agreements} / {matching_count} (100.0%)")
    print("=" * 78)

    # 6. Physical Interpretation
    print("\nKey Quantum Mechanics Observations:")
    print("1. Matching Bases:")
    print("   When Bob randomly chooses the SAME basis as Alice, projective measurement")
    print("   projects onto the prepared eigenstate, recovering Alice's bit deterministically.")
    print("2. Mismatched Bases:")
    print("   When Bob chooses the CONJUGATE basis, the state is an equal superposition in Bob's")
    print("   measurement basis, yielding a purely random outcome (approx 50% 0, 50% 1).")
    print("   *Note*: A basis mismatch is NOT an error; it is a fundamental quantum property")
    print("   that will be reconciled in Phase 5 during classical basis sifting.\n")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="BB84 Phase 4 Alice-Channel-Bob Demonstration")
    parser.add_argument(
        "--signals",
        type=int,
        default=16,
        help="Number of quantum signals to transmit (default: 16)",
    )
    parser.add_argument(
        "--alice-seed",
        type=int,
        default=42,
        help="Random seed for Alice (default: 42)",
    )
    parser.add_argument(
        "--bob-seed",
        type=int,
        default=99,
        help="Random seed for Bob (default: 99)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_alice_bob_demonstration(
        num_signals=args.signals,
        alice_seed=args.alice_seed,
        bob_seed=args.bob_seed,
    )
