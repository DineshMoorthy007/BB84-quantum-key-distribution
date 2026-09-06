"""Alice (Sender) component for the BB84 Quantum Key Distribution protocol.

This module implements Alice's responsibilities in BB84:
1. Generating a sequence of independent, uniformly distributed classical bits.
2. Generating a sequence of independent, uniformly distributed BB84 bases ('Z' or 'X').
3. Encoding each bit into its corresponding quantum state using Phase 2 quantum primitives.
4. Preserving Alice's private classical records (bits and bases) for post-transmission sifting.
5. Providing an isolated quantum transmission interface for the quantum channel / Bob.

Academic Note:
    Alice's bits and bases constitute private classical information. In BB84,
    Alice only transmits quantum carrier states over the quantum channel during
    the quantum exchange phase. Basis reconciliation occurs only after Bob has
    measured the received photons.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Union
import numpy as np
from qiskit import QuantumCircuit

from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    prepare_state,
    validate_basis,
    validate_bit,
)


@dataclass(frozen=True)
class BB84Signal:
    """Represents a single BB84 quantum signal prepared by Alice.

    Attributes:
        index: Sequential position of the signal in the transmission stream.
        circuit: Single-qubit QuantumCircuit prepared in the target quantum state.
        bit: Alice's private classical bit (0 or 1).
        basis: Alice's private measurement basis ('Z' or 'X').
    """

    index: int
    circuit: QuantumCircuit
    bit: int
    basis: str

    @property
    def state_symbol(self) -> str:
        """Return the standard Dirac bra-ket notation for the prepared state."""
        if self.basis == COMPUTATIONAL_BASIS:
            return "|0>" if self.bit == 0 else "|1>"
        else:
            return "|+>" if self.bit == 0 else "|->"

    def get_quantum_circuit(self) -> QuantumCircuit:
        """Return a copy of the quantum circuit for transmission across the channel."""
        return self.circuit.copy()


class Alice:
    """Alice (Sender) in the BB84 Quantum Key Distribution protocol.

    Alice prepares raw key bits, selects random encoding bases, and produces
    quantum state circuits for transmission over a quantum channel.

    Attributes:
        number_of_qubits: Total number of quantum bits / signals to prepare.
        seed: Optional random seed for reproducible pseudo-random generation.
    """

    def __init__(
        self,
        number_of_qubits: int = 100,
        seed: Optional[int] = None,
        num_qubits: Optional[int] = None,
    ) -> None:
        """Initialize Alice with configuration parameters.

        Args:
            number_of_qubits: Number of quantum bits to generate (must be > 0).
            seed: Optional random seed for local RNG reproducibility.
            num_qubits: Optional alias for number_of_qubits.

        Raises:
            TypeError: If number_of_qubits or seed has an invalid type.
            ValueError: If number_of_qubits is <= 0.
        """
        n_qubits = num_qubits if num_qubits is not None else number_of_qubits

        if isinstance(n_qubits, bool) or not isinstance(n_qubits, int):
            raise TypeError(f"number_of_qubits must be an integer, got {type(n_qubits).__name__}")
        if n_qubits <= 0:
            raise ValueError(f"number_of_qubits must be a positive integer, got {n_qubits}")

        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

        self._number_of_qubits: int = n_qubits
        self._seed: Optional[int] = seed
        self._rng: np.random.Generator = np.random.default_rng(seed)

        self._bits: Optional[List[int]] = None
        self._bases: Optional[List[str]] = None
        self._signals: Optional[List[BB84Signal]] = None

    @property
    def number_of_qubits(self) -> int:
        """Return the configured number of qubits."""
        return self._number_of_qubits

    @property
    def seed(self) -> Optional[int]:
        """Return the random seed used by Alice."""
        return self._seed

    @property
    def bits(self) -> List[int]:
        """Return Alice's private sequence of classical bits."""
        if self._bits is None:
            self.generate_bits()
        return list(self._bits)  # Return shallow copy to prevent external mutation

    @property
    def bases(self) -> List[str]:
        """Return Alice's private sequence of encoding bases."""
        if self._bases is None:
            self.generate_bases()
        return list(self._bases)

    @property
    def signals(self) -> List[BB84Signal]:
        """Return Alice's prepared BB84 signals."""
        if self._signals is None:
            self.prepare_signals()
        return list(self._signals)

    def generate_bits(self) -> List[int]:
        """Generate a random sequence of classical bits (0 or 1).

        Uses Alice's local random generator.

        Returns:
            List of integers (0 or 1) of length number_of_qubits.
        """
        raw_bits = self._rng.integers(0, 2, size=self._number_of_qubits)
        self._bits = [int(b) for b in raw_bits]
        # Invalidate previously computed signals if bits changed
        self._signals = None
        return list(self._bits)

    def generate_bases(self) -> List[str]:
        """Generate a random sequence of BB84 bases ('Z' or 'X').

        Uses Alice's local random generator.

        Returns:
            List of basis strings ('Z' or 'X') of length number_of_qubits.
        """
        raw_bases = self._rng.choice(
            [COMPUTATIONAL_BASIS, HADAMARD_BASIS], size=self._number_of_qubits
        )
        self._bases = [str(b) for b in raw_bases]
        # Invalidate previously computed signals if bases changed
        self._signals = None
        return list(self._bases)

    def encode(
        self,
        bits: Optional[Sequence[int]] = None,
        bases: Optional[Sequence[str]] = None,
    ) -> List[BB84Signal]:
        """Encode bit/basis pairs into corresponding quantum circuits.

        Reuses the fundamental quantum state preparation primitive
        `src.quantum_primitives.prepare_state`.

        Mapping:
            - bit=0, basis='Z' -> |0>
            - bit=1, basis='Z' -> |1>
            - bit=0, basis='X' -> |+>
            - bit=1, basis='X' -> |->

        Args:
            bits: Optional explicit bits sequence (defaults to self.bits).
            bases: Optional explicit bases sequence (defaults to self.bases).

        Returns:
            List of BB84Signal objects.

        Raises:
            ValueError: If bits and bases have mismatched lengths.
        """
        target_bits = list(bits) if bits is not None else self.bits
        target_bases = list(bases) if bases is not None else self.bases

        if len(target_bits) != len(target_bases):
            raise ValueError(
                f"Length mismatch: {len(target_bits)} bits vs {len(target_bases)} bases."
            )

        # Validate elements
        for b in target_bits:
            validate_bit(b)
        for base in target_bases:
            validate_basis(base)

        signals: List[BB84Signal] = []
        for idx, (bit, basis) in enumerate(zip(target_bits, target_bases)):
            circuit = prepare_state(bit, basis)
            signals.append(
                BB84Signal(
                    index=idx,
                    circuit=circuit,
                    bit=bit,
                    basis=basis,
                )
            )

        if bits is not None:
            self._bits = target_bits
        if bases is not None:
            self._bases = target_bases
        self._signals = signals
        return list(self._signals)

    def prepare_signals(self) -> List[BB84Signal]:
        """Coordinate full signal preparation (generate bits, bases, and quantum circuits).

        Returns:
            List of BB84Signal objects of length number_of_qubits.
        """
        if self._bits is None:
            self.generate_bits()
        if self._bases is None:
            self.generate_bases()
        return self.encode()

    def get_quantum_signals(self) -> List[QuantumCircuit]:
        """Provide transmitted quantum circuits for the quantum channel.

        This interface only exposes the physical quantum states (QuantumCircuit objects)
        to the channel and Bob, keeping Alice's classical bits and basis choices
        strictly private.

        Returns:
            List of independent QuantumCircuit objects ready for transmission.
        """
        return [sig.get_quantum_circuit() for sig in self.signals]

    def get_state_symbols(self) -> List[str]:
        """Return the list of state symbols (e.g. '|0>', '|+>') for all prepared signals."""
        return [sig.state_symbol for sig in self.signals]
