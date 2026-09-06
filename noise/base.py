"""Abstract base class for quantum channel noise models.

In the BB84 protocol, physical quantum transmission channels inherently suffer
from decoherence, attenuation, and environmental perturbations.
Quantum noise models in this package act directly on single-qubit quantum states
(represented as Qiskit QuantumCircuit objects) before detection/measurement,
faithfully capturing quantum physical disturbances without modifying classical data.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Sequence
import numpy as np
from qiskit import QuantumCircuit


class QuantumNoiseModel(ABC):
    """Abstract base class for single-qubit quantum noise channels.

    All noise models operate directly on QuantumCircuit instances prior
    to measurement, preserving the physical distinction between quantum
    state evolution and classical measurement outcomes.

    Attributes:
        probability: Noise activation parameter in [0.0, 1.0].
        seed: Optional random seed for reproducible stochastic simulations.
    """

    def __init__(
        self,
        probability: float = 0.0,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize quantum noise model.

        Args:
            probability: Probability p of noise occurrence in [0.0, 1.0].
            seed: Optional integer seed for local reproducible random state.

        Raises:
            TypeError: If probability or seed has an invalid type.
            ValueError: If probability is outside [0.0, 1.0].
        """
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise TypeError(
                f"probability must be a float, got {type(probability).__name__}"
            )
        if not (0.0 <= float(probability) <= 1.0):
            raise ValueError(
                f"probability must be in [0.0, 1.0], got {probability}"
            )

        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

        self._probability: float = float(probability)
        self._seed: Optional[int] = seed
        self._rng: np.random.Generator = np.random.default_rng(seed)

    @property
    def probability(self) -> float:
        """Return configured noise occurrence probability."""
        return self._probability

    @property
    def seed(self) -> Optional[int]:
        """Return local random seed."""
        return self._seed

    @property
    @abstractmethod
    def name(self) -> str:
        """Return descriptive name of the noise model."""
        pass

    @abstractmethod
    def apply(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply the quantum noise channel to a single quantum circuit.

        Must return a new or modified QuantumCircuit representing the
        corrupted quantum carrier state.

        Args:
            circuit: Single-qubit QuantumCircuit arriving at noise channel.

        Returns:
            QuantumCircuit after stochastic noise application.
        """
        pass

    def apply_batch(self, circuits: Sequence[QuantumCircuit]) -> List[QuantumCircuit]:
        """Apply the quantum noise channel to a batch of quantum circuits.

        Args:
            circuits: Sequence of single-qubit QuantumCircuit objects.

        Returns:
            List of noisy QuantumCircuit objects.
        """
        return [self.apply(qc) for qc in circuits]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(probability={self._probability}, seed={self._seed})"
