"""Bit-flip quantum noise model for BB84 simulation.

A bit-flip error models physical environmental processes that invert the
computational basis states:
    |0> -> |1>
    |1> -> |0>
This operation corresponds to the Pauli-X quantum operator:
    X = [[0, 1],
         [1, 0]]

Mathematical Operation:
    With probability p:   apply Pauli-X gate to the quantum carrier qubit.
    With probability 1-p: leave the quantum state unchanged (Identity).
"""

from __future__ import annotations

from typing import Optional
from qiskit import QuantumCircuit

from noise.base import QuantumNoiseModel


class BitFlipNoise(QuantumNoiseModel):
    """Bit-flip quantum noise channel.

    Applies a Pauli-X gate with probability p directly to the quantum circuit.
    """

    @property
    def name(self) -> str:
        """Return descriptive model name."""
        return "Bit-Flip Noise (Pauli-X)"

    def apply(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply bit-flip noise to a single-qubit quantum circuit.

        Args:
            circuit: Input single-qubit QuantumCircuit.

        Returns:
            New QuantumCircuit with Pauli-X applied if noise triggered.
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
            noisy_qc.x(0)

        return noisy_qc
