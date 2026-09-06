"""Depolarizing quantum noise model for BB84 simulation.

Depolarizing noise models the isotropic degradation of a quantum state due to
random interactions with the environment. It transforms any single-qubit state
towards the maximally mixed state I / 2.

Qiskit Parameterization:
    In accordance with Qiskit Aer's standard depolarizing_error(param, num_qubits=1),
    the single-qubit channel is parameterized by lambda in [0.0, 1.0]:
        E(rho) = (1 - lambda) * rho + lambda * Tr[rho] * (I / 2)

    In terms of single-qubit Pauli operators {I, X, Y, Z}:
        E(rho) = (1 - 3*lambda/4) * rho + (lambda/4) * (X*rho*X + Y*rho*Y + Z*rho*Z)

    Operational Probabilities:
        P(I) = 1 - 3*lambda/4
        P(X) = lambda/4
        P(Y) = lambda/4
        P(Z) = lambda/4

    Sifted QBER Implication:
        - In Z-basis: X and Y induce errors -> P(error) = P(X) + P(Y) = lambda / 2
        - In X-basis: Z and Y induce errors -> P(error) = P(Z) + P(Y) = lambda / 2
        - Expected BB84 QBER = lambda / 2 = 50% * lambda
        - When lambda = 1.0 (complete depolarization): QBER = 50.0% (random guess).
"""

from __future__ import annotations

from typing import Optional
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer.noise import depolarizing_error

from noise.base import QuantumNoiseModel


class DepolarizingNoise(QuantumNoiseModel):
    """Depolarizing quantum noise channel.

    Adopts Qiskit's standard depolarizing_error(lambda, 1) parameterization.
    Randomly applies Pauli operations {I, X, Y, Z} according to Qiskit's exact channel weights.
    """

    def __init__(
        self,
        probability: float = 0.0,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize depolarizing noise model.

        Args:
            probability: Depolarization parameter lambda in [0.0, 1.0].
            seed: Optional integer seed for reproducibility.
        """
        super().__init__(probability=probability, seed=seed)

        # Precompute Pauli probabilities adhering to Qiskit Aer's depolarizing_error specification
        lam = self._probability
        p_i = 1.0 - 0.75 * lam
        p_x = 0.25 * lam
        p_y = 0.25 * lam
        p_z = 0.25 * lam

        # Normalization guard against floating point inaccuracies
        total = p_i + p_x + p_y + p_z
        self._pauli_probs = np.array([p_i, p_x, p_y, p_z]) / total

    @property
    def name(self) -> str:
        """Return descriptive model name."""
        return "Depolarizing Noise (Qiskit Standard)"

    @property
    def pauli_probabilities(self) -> np.ndarray:
        """Return array of [P(I), P(X), P(Y), P(Z)] channel probabilities."""
        return self._pauli_probs.copy()

    def apply(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply single-qubit depolarizing noise to circuit.

        Args:
            circuit: Input single-qubit QuantumCircuit.

        Returns:
            New QuantumCircuit after applying sampled Pauli operator {I, X, Y, Z}.
        """
        noisy_qc = circuit.copy()

        # Edge case optimization: lambda = 0.0 is exact identity
        if self._probability == 0.0:
            return noisy_qc

        # Sample Pauli operator according to Qiskit depolarizing weights: 0: I, 1: X, 2: Y, 3: Z
        choice = self._rng.choice(4, p=self._pauli_probs)

        if choice == 1:
            noisy_qc.x(0)
        elif choice == 2:
            noisy_qc.y(0)
        elif choice == 3:
            noisy_qc.z(0)
        # choice == 0 corresponds to Identity (no operation)

        return noisy_qc
