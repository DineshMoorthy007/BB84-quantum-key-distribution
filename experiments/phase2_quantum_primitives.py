"""Phase 2 Educational Demonstration: Quantum Primitives in BB84.

This script demonstrates quantum state preparation, circuit representation,
statevector amplitudes, and projective measurements in both computational (Z)
and Hadamard (X) bases for all four BB84 states.

Usage:
    .venv/Scripts/python experiments/phase2_quantum_primitives.py
"""

from __future__ import annotations

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

from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    get_statevector,
    measure_x_basis,
    measure_z_basis,
    prepare_state,
)

DEMO_STATES = [
    {
        "bit": 0,
        "basis": COMPUTATIONAL_BASIS,
        "symbol": "|0>",
        "description": "Computational basis bit 0 (ground state)",
    },
    {
        "bit": 1,
        "basis": COMPUTATIONAL_BASIS,
        "symbol": "|1>",
        "description": "Computational basis bit 1 (excited state)",
    },
    {
        "bit": 0,
        "basis": HADAMARD_BASIS,
        "symbol": "|+>",
        "description": "Hadamard basis bit 0: (|0> + |1>)/sqrt(2)",
    },
    {
        "bit": 1,
        "basis": HADAMARD_BASIS,
        "symbol": "|->",
        "description": "Hadamard basis bit 1: (|0> - |1>)/sqrt(2)",
    },
]


def run_demonstration(shots: int = 1000, seed: int = 42) -> None:
    """Run educational demonstration for the four BB84 states."""
    print("=" * 72)
    print("       BB84 QUANTUM KEY DISTRIBUTION: PHASE 2 DEMONSTRATION")
    print("                Fundamental Quantum Primitives")
    print("=" * 72)
    print(f"Simulation parameters: shots={shots}, seed={seed}\n")

    summary_rows = []

    for idx, item in enumerate(DEMO_STATES, start=1):
        bit = item["bit"]
        basis = item["basis"]
        symbol = item["symbol"]
        desc = item["description"]

        print(f"[{idx}/4] Preparing State: {symbol} (bit={bit}, basis='{basis}')")
        print(f"     Description: {desc}")

        # 1. Prepare quantum circuit
        circuit = prepare_state(bit, basis)

        # 2. Display circuit
        print("     Quantum Circuit:")
        circuit_diagram = str(circuit.draw(output="text"))
        for line in circuit_diagram.splitlines():
            print(f"       {line}")

        # 3. Statevector inspection
        sv = get_statevector(circuit)
        amplitudes = [complex(round(c.real, 4), round(c.imag, 4)) for c in sv.data]
        print(f"     Statevector Amplitudes: {amplitudes}")

        # 4. Measure in Z basis
        z_outcomes = measure_z_basis(circuit, shots=shots, seed=seed)
        z_zeros = z_outcomes.count(0) if isinstance(z_outcomes, list) else (1 if z_outcomes == 0 else 0)
        z_ones = shots - z_zeros
        p_z_zero = (z_zeros / shots) * 100.0
        p_z_one = (z_ones / shots) * 100.0

        # 5. Measure in X basis
        x_outcomes = measure_x_basis(circuit, shots=shots, seed=seed)
        x_zeros = x_outcomes.count(0) if isinstance(x_outcomes, list) else (1 if x_outcomes == 0 else 0)
        x_ones = shots - x_zeros
        p_x_zero = (x_zeros / shots) * 100.0
        p_x_one = (x_ones / shots) * 100.0

        print("     Measurement Statistics:")
        print(f"       Measured in Z-basis: 0 -> {p_z_zero:5.1f}% | 1 -> {p_z_one:5.1f}%")
        print(f"       Measured in X-basis: 0 -> {p_x_zero:5.1f}% | 1 -> {p_x_one:5.1f}%")

        # 6. Interpretation
        print("     Interpretation:")
        if basis == COMPUTATIONAL_BASIS:
            print(f"       - Z-basis is MATCHING basis: deterministic bit {bit} ({100.0 if bit == 0 else 0.0:.0f}% zeros).")
            print("       - X-basis is CONJUGATE basis: maximum uncertainty (~50% 0, ~50% 1).")
        else:
            print("       - Z-basis is CONJUGATE basis: maximum uncertainty (~50% 0, ~50% 1).")
            print(f"       - X-basis is MATCHING basis: deterministic bit {bit} ({100.0 if bit == 0 else 0.0:.0f}% zeros).")
        print("-" * 72)

        summary_rows.append((symbol, f"bit={bit}, basis={basis}", f"{p_z_zero:.1f}% 0 / {p_z_one:.1f}% 1", f"{p_x_zero:.1f}% 0 / {p_x_one:.1f}% 1"))

    # Summary Table
    print("\n" + "=" * 72)
    print("                           SUMMARY TABLE")
    print("=" * 72)
    header = f"{'State':<8} | {'Encoding':<18} | {'Z-Measurement (0/1)':<21} | {'X-Measurement (0/1)':<21}"
    print(header)
    print("-" * len(header))
    for sym, enc, z_res, x_res in summary_rows:
        print(f"{sym:<8} | {enc:<18} | {z_res:<21} | {x_res:<21}")
    print("=" * 72)
    print("\nKey Quantum Finding for BB84:")
    print("When sender (Alice) and receiver (Bob) measure in the SAME basis,")
    print("outcomes are strictly correlated (0% error under ideal conditions).")
    print("When measured in the OPPOSITE basis, outcomes are purely random (50% error),")
    print("which is the physical mechanism enabling eavesdropping detection.\n")


if __name__ == "__main__":
    run_demonstration()
