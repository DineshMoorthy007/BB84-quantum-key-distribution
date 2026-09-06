"""Bob (Receiver) component for the BB84 Quantum Key Distribution protocol.

This module implements Bob's responsibilities in BB84:
1. Independently generating random measurement bases ('Z' or 'X') without knowing Alice's choices.
2. Receiving transmitted quantum signals from the quantum channel.
3. Measuring each incoming quantum signal along Bob's selected basis.
4. Storing Bob's private measurement outcomes and basis associations.

Academic Note:
    Bob receives only quantum carrier states (photons) across the quantum channel.
    Bob does not possess or inspect Alice's original bits or bases during measurement.
    Basis comparison and reconciliation occur only during classical post-processing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence
import numpy as np
from qiskit import QuantumCircuit

from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    measure_state,
    validate_basis,
)


@dataclass(frozen=True)
class BobMeasurement:
    """Encapsulates a single measurement outcome obtained by Bob.

    Attributes:
        index: Sequential position of the received signal.
        basis: Bob's chosen measurement basis ('Z' or 'X').
        result: Classical measurement outcome (0 or 1).
    """

    index: int
    basis: str
    result: int

    def __post_init__(self) -> None:
        """Validate measurement outcome fields."""
        if not isinstance(self.index, int) or self.index < 0:
            raise ValueError(f"index must be a non-negative integer, got {self.index}")
        if not isinstance(self.basis, str):
            raise TypeError(f"basis must be a string, got {type(self.basis).__name__}")
        validate_basis(self.basis)
        if self.result not in (0, 1) or isinstance(self.result, bool):
            raise ValueError(f"result must be a binary integer (0 or 1), got {self.result}")


class Bob:
    """Bob (Receiver) in the BB84 protocol.

    Independently selects measurement bases, measures received quantum signals,
    and preserves his classical measurement results.

    Attributes:
        seed: Optional random seed for reproducible basis generation and measurement.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialize Bob with an optional random seed.

        Args:
            seed: Optional integer seed for local reproducible random number generation.

        Raises:
            TypeError: If seed is not an integer or None.
        """
        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

        self._seed: Optional[int] = seed
        self._rng: np.random.Generator = np.random.default_rng(seed)

        self._bases: Optional[List[str]] = None
        self._measurements: Optional[List[BobMeasurement]] = None

    @property
    def seed(self) -> Optional[int]:
        """Return Bob's random seed."""
        return self._seed

    @property
    def bases(self) -> List[str]:
        """Return Bob's selected measurement bases."""
        if self._bases is None:
            return []
        return list(self._bases)

    @property
    def measurements(self) -> List[BobMeasurement]:
        """Return Bob's recorded measurement results."""
        if self._measurements is None:
            return []
        return list(self._measurements)

    @property
    def results(self) -> List[int]:
        """Return the sequence of Bob's raw measured classical bits."""
        if self._measurements is None:
            return []
        return [m.result for m in self._measurements]

    def generate_bases(self, num_signals: int) -> List[str]:
        """Generate a random sequence of measurement bases ('Z' or 'X').

        Uses Bob's local random generator independently of Alice.

        Args:
            num_signals: Number of bases to generate (must be > 0).

        Returns:
            List of basis strings ('Z' or 'X') of length num_signals.

        Raises:
            TypeError: If num_signals is not an integer.
            ValueError: If num_signals <= 0.
        """
        if isinstance(num_signals, bool) or not isinstance(num_signals, int):
            raise TypeError(f"num_signals must be an integer, got {type(num_signals).__name__}")
        if num_signals <= 0:
            raise ValueError(f"num_signals must be a positive integer, got {num_signals}")

        raw_bases = self._rng.choice(
            [COMPUTATIONAL_BASIS, HADAMARD_BASIS], size=num_signals
        )
        self._bases = [str(b) for b in raw_bases]
        return list(self._bases)

    def measure_signal(
        self,
        circuit: QuantumCircuit,
        basis: str,
        index: int = 0,
    ) -> BobMeasurement:
        """Measure a single incoming quantum circuit in a specified basis.

        Args:
            circuit: Single-qubit quantum circuit to measure.
            basis: Measurement basis ('Z' or 'X').
            index: Sequence index of the signal.

        Returns:
            A BobMeasurement object recording index, basis, and classical outcome bit.
        """
        norm_basis = validate_basis(basis)
        meas_seed = int(self._rng.integers(0, 2**31 - 1)) if self._seed is not None else None
        outcome = measure_state(circuit, basis=norm_basis, shots=1, seed=meas_seed)
        return BobMeasurement(index=index, basis=norm_basis, result=int(outcome))

    def receive_and_measure(
        self,
        signals: Sequence[QuantumCircuit],
        bases: Optional[Sequence[str]] = None,
    ) -> List[BobMeasurement]:
        """Receive a sequence of quantum signals and measure each in Bob's chosen basis.

        If bases are not supplied, Bob generates them randomly for the incoming batch.

        Args:
            signals: Sequence of single-qubit QuantumCircuit objects.
            bases: Optional pre-determined basis sequence (must match signals count).

        Returns:
            List of BobMeasurement objects containing index, basis, and measured bit.

        Raises:
            ValueError: If signals is empty or if bases count does not match signals count.
        """
        if not signals:
            raise ValueError("signals sequence cannot be empty.")

        n = len(signals)
        if bases is not None:
            if len(bases) != n:
                raise ValueError(
                    f"Bases count ({len(bases)}) must match signals count ({n})."
                )
            target_bases = [validate_basis(b) for b in bases]
            self._bases = target_bases
        else:
            target_bases = self.generate_bases(n)

        measurements: List[BobMeasurement] = []
        for idx, (circuit, basis) in enumerate(zip(signals, target_bases)):
            meas = self.measure_signal(circuit, basis, index=idx)
            measurements.append(meas)

        self._measurements = measurements
        return list(self._measurements)
