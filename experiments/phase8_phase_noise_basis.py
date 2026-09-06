"""Experiment 3: Basis-Dependent Phase Noise Investigation.

Demonstrates that Pauli-Z phase-flip noise has radically different observable
consequences depending on the encoding basis:
1. Computational (Z) Basis:
   Z|0> = |0>, Z|1> = -|1> = exp(i*pi)|1>.
   Because global phase has no observable consequence on projective measurements,
   phase-flip noise produces 0.0% QBER on Z-basis transmissions!
2. Hadamard (X) Basis:
   Z|+> = |->, Z|-> = |+>.
   Phase-flip noise directly inverts the basis eigenstates, converting bits 0 <-> 1.
   QBER on X-basis transmissions equals the noise probability p!
3. BB84 Overall:
   Because bases are chosen with equal 50% probability, overall QBER is p / 2.

Outputs:
- Terminal table comparing Z-basis QBER vs X-basis QBER across multiple noise rates.
- Plot saved to results/phase8_phase_noise_basis.png.
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

from noise.phase_flip import PhaseFlipNoise
from src.alice import Alice
from src.bob import Bob
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel
from visualization.noise_plots import plot_phase_noise_basis_dependence


def run_phase_noise_basis_experiment(
    signals_per_trial: int = 4000,
    probabilities: Sequence[float] = (0.00, 0.05, 0.10, 0.20, 0.30),
    seed: int = 200,
) -> None:
    """Evaluate basis-dependent error rates under phase-flip noise.

    Args:
        signals_per_trial: Number of transmitted quantum signals per probability.
        probabilities: Sequence of phase-flip probabilities to evaluate.
        seed: Base random seed.
    """
    print("=" * 86)
    print("      PHASE 8 EXPERIMENT 3: BASIS-DEPENDENT QUANTUM BEHAVIOR OF PHASE NOISE")
    print("=" * 86)
    print("Physical Principle:")
    print("  - Z-basis eigenstates {|0>, |1>} are eigenvectors of Pauli-Z (Immune to bit errors).")
    print("  - X-basis eigenstates {|+>, |->} are inverted by Pauli-Z (Maximal bit errors).\n")

    header = (
        f"{'Phase Noise p':<14} | {'Z-Basis QBER':<14} | {'X-Basis QBER':<14} | "
        f"{'Total BB84 QBER':<16} | {'Theoretical (~p/2)'}"
    )
    print(header)
    print("-" * len(header))

    z_qber_list: List[float] = []
    x_qber_list: List[float] = []
    total_qber_list: List[float] = []

    for idx, p in enumerate(probabilities):
        seed_iter = seed + idx * 20
        noise = PhaseFlipNoise(probability=p, seed=seed_iter + 2) if p > 0.0 else None

        alice = Alice(number_of_qubits=signals_per_trial, seed=seed_iter)
        bob = Bob(seed=seed_iter + 1)
        channel = QuantumChannel(noise=noise)

        signals = alice.get_quantum_signals()
        received = channel.transmit(signals)
        bob.receive_and_measure(received)

        sifted = sift_from_alice_and_bob(alice, bob)

        # Separate sifted bits by basis
        alice_z_bits, bob_z_bits = [], []
        alice_x_bits, bob_x_bits = [], []

        for orig_idx, a_bit, b_bit in zip(
            sifted.matching_indices, sifted.alice_sifted_key, sifted.bob_sifted_key
        ):
            basis = alice.bases[orig_idx]
            if basis == "Z":
                alice_z_bits.append(a_bit)
                bob_z_bits.append(b_bit)
            elif basis == "X":
                alice_x_bits.append(a_bit)
                bob_x_bits.append(b_bit)

        qber_total = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key).qber_percentage
        qber_z = calculate_qber(alice_z_bits, bob_z_bits).qber_percentage if alice_z_bits else 0.0
        qber_x = calculate_qber(alice_x_bits, bob_x_bits).qber_percentage if alice_x_bits else 0.0

        theory_total = (p / 2.0) * 100.0

        row = (
            f"{p:<14.2f} | {f'{qber_z:.2f}%':<14} | {f'{qber_x:.2f}%':<14} | "
            f"{f'{qber_total:.2f}%':<16} | {theory_total:.2f}%"
        )
        print(row)

        z_qber_list.append(qber_z)
        x_qber_list.append(qber_x)
        total_qber_list.append(qber_total)

    print("=" * 86)
    print("\nConclusion: Phase noise demonstrates that quantum channel errors are fundamentally")
    print("state-dependent and cannot be accurately represented by classical bit flipping.")

    # Visualization
    img_path = plot_phase_noise_basis_dependence(
        probabilities=probabilities,
        z_qber=z_qber_list,
        x_qber=x_qber_list,
        combined_qber=total_qber_list,
    )
    print(f"\n[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_phase_noise_basis_experiment()
