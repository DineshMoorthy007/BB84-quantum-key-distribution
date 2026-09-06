"""Phase-flip quantum noise model for BB84 simulation.

A phase-flip error models physical environmental processes that introduce a relative
phase shift of pi between computational basis states:
    |0> -> |0>
    |1> -> -|1>
This operation corresponds to the Pauli-Z quantum operator:
    Z = [[1,  0],
         [0, -1]]

Quantum Basis-Dependence:
    - Computational (Z) Basis:
        Z |0> = |0>
        Z |1> = -|1> = exp(i*pi) |1> (global phase change).
        Since global phase has no observable consequence, Z-basis measurements
        remain completely unaffected! QBER in Z-basis is 0%.
    - Hadamard (X) Basis:
        Z |+> = Z (|0> + |1>)/sqrt(2) = (|0> - |1>)/sqrt(2) = |->
        Z |-> = Z (|0> - |1>)/sqrt(2) = (|0> + |1>)/sqrt(2) = |+>
        The eigenstates are completely inverted! Measuring in X-basis flips the bit.
    - BB84 Sifted Key:
        Because Alice and Bob randomly use Z and X with equal probability,
        overall QBER is p / 2.
"""

from __future__ import annotations

from typing import Optional
from qiskit import QuantumCircuit

from noise.base import QuantumNoiseModel


class PhaseFlipNoise(QuantumNoiseModel):
    """Phase-flip quantum noise channel.

    Applies a Pauli-Z gate with probability p directly to the quantum circuit.
    Demonstrates fundamental quantum complementarity and basis-dependent observables.
    """

    @property
    def name(self) -> str:
        """Return descriptive model name."""
        return "Phase-Flip Noise (Pauli-Z)"

    def apply(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply phase-flip noise to a single-qubit quantum circuit.

        Args:
            circuit: Input single-qubit QuantumCircuit.

        Returns:
            New QuantumCircuit with Pauli-Z applied if noise triggered.
        """
        noisy_qc = circuit.copy()

        # Edge case optimization: p=0.0 applies nothing
        if self._probability == 0.0:
            return noisy_qc

        # Deterministic edge case p=1.0 or stochastic sampling
        trigger_error = (
            self._probability == 1.0
            or self._rng.random() < self._probability
        )

        if trigger_error:
            noisy_qc.z(0)

        return noisy_qc
