"""Eve (Eavesdropper) intercept-resend attack module for the BB84 protocol.

This module models an active quantum eavesdropper performing an intercept-resend attack.
For each quantum carrier state transmitted across the channel:
1. Eve probabilistically intercepts the quantum carrier photon.
2. If intercepted, Eve selects a random measurement basis ('Z' or 'X') without knowing
   Alice's basis choice.
3. Eve performs projective quantum measurement along her selected basis, obtaining a
   classical bit outcome (0 or 1).
4. Eve prepares a brand NEW single-qubit quantum state corresponding to her measured bit
   and basis choice.
5. Eve resends this replacement quantum carrier state forward to Bob.

Academic Principles:
    - No-Cloning Theorem (Wootters & Zurek, 1982): Eve cannot clone unknown non-orthogonal
      quantum states. She is compelled to perform a projective measurement.
    - Heisenberg Uncertainty & Complementarity: Measuring in the wrong basis irrevocably
      disturbs the quantum state, projecting it into an eigenstate of Eve's basis.
    - Theoretical Error Rate:
        P(Eve chooses wrong basis) = 1/2
        P(Bob error | wrong Eve basis) = 1/2
        Expected QBER under full intercept-resend = (1/2) * (1/2) = 1/4 = 25.0%.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple
import numpy as np
from qiskit import QuantumCircuit

from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    measure_state,
    prepare_state,
    validate_basis,
)


@dataclass(frozen=True)
class EveInterceptionRecord:
    """Record of an eavesdropping event for a single transmitted signal.

    Attributes:
        index: Sequence index of the signal.
        intercepted: Boolean indicating whether Eve intercepted this specific signal.
        basis: Measurement basis chosen by Eve ('Z' or 'X'), or None if not intercepted.
        result: Classical bit outcome obtained by Eve (0 or 1), or None if not intercepted.
        resent_circuit: The quantum circuit forwarded towards Bob (new state if intercepted,
            or clean copy of original if bypassed).
    """

    index: int
    intercepted: bool
    basis: Optional[str]
    result: Optional[int]
    resent_circuit: QuantumCircuit


class Eve:
    """Active quantum eavesdropper executing an intercept-resend attack.

    Interception operates directly on quantum carrier states (circuits).
    No classical bit-flipping shortcut is used.

    Attributes:
        interception_probability: Probability p in [0.0, 1.0] that any individual
            signal is intercepted.
        seed: Optional random seed for local reproducible pseudo-random generation.
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        interception_probability: float = 1.0,
    ) -> None:
        """Initialize Eve with configuration parameters.

        Args:
            seed: Optional integer random seed for reproducibility.
            interception_probability: Probability of intercepting each signal (0.0 to 1.0).

        Raises:
            TypeError: If parameters have invalid types.
            ValueError: If interception_probability is outside [0.0, 1.0].
        """
        if isinstance(interception_probability, bool) or not isinstance(
            interception_probability, (int, float)
        ):
            raise TypeError(
                f"interception_probability must be a float, got {type(interception_probability).__name__}"
            )
        if not (0.0 <= interception_probability <= 1.0):
            raise ValueError(
                f"interception_probability must be in [0.0, 1.0], got {interception_probability}"
            )

        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

        self._seed: Optional[int] = seed
        self._interception_probability: float = float(interception_probability)
        self._rng: np.random.Generator = np.random.default_rng(seed)

        self._records: List[EveInterceptionRecord] = []

    @property
    def seed(self) -> Optional[int]:
        """Return Eve's random seed."""
        return self._seed

    @property
    def interception_probability(self) -> float:
        """Return the configured interception probability."""
        return self._interception_probability

    @property
    def records(self) -> List[EveInterceptionRecord]:
        """Return all interception records from the most recent attack."""
        return list(self._records)

    @property
    def intercepted_count(self) -> int:
        """Return total number of intercepted signals in the most recent attack."""
        return sum(1 for r in self._records if r.intercepted)

    @property
    def bases(self) -> List[Optional[str]]:
        """Return Eve's chosen bases for each signal (None if unintercepted)."""
        return [r.basis for r in self._records]

    @property
    def results(self) -> List[Optional[int]]:
        """Return Eve's classical measurement results for each signal."""
        return [r.result for r in self._records]

    def generate_basis(self) -> str:
        """Independently select a random measurement basis ('Z' or 'X').

        Returns:
            Basis string ('Z' or 'X').
        """
        return str(self._rng.choice([COMPUTATIONAL_BASIS, HADAMARD_BASIS]))

    def generate_bases(self, count: int) -> List[str]:
        """Generate a sequence of random measurement bases.

        Args:
            count: Number of bases to generate.

        Returns:
            List of basis strings of length count.
        """
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValueError(f"count must be a positive integer, got {count}")
        raw = self._rng.choice([COMPUTATIONAL_BASIS, HADAMARD_BASIS], size=count)
        return [str(b) for b in raw]

    def intercept_signal(
        self,
        circuit: QuantumCircuit,
        index: int = 0,
    ) -> Tuple[QuantumCircuit, EveInterceptionRecord]:
        """Intercept and process a single quantum carrier circuit.

        If intercepted:
            1. Chooses random basis.
            2. Performs projective measurement on incoming state.
            3. Prepares brand new quantum circuit encoding measured bit in chosen basis.
        If bypassed:
            Returns an unmodified copy of the incoming circuit.

        Args:
            circuit: Single-qubit QuantumCircuit arriving at Eve's interceptor.
            index: Sequential position index of the signal.

        Returns:
            Tuple of (resent_quantum_circuit, interception_record).
        """
        should_intercept = (
            self._interception_probability == 1.0
            or (self._interception_probability > 0.0 and self._rng.random() < self._interception_probability)
        )

        if not should_intercept:
            resent_qc = circuit.copy()
            record = EveInterceptionRecord(
                index=index,
                intercepted=False,
                basis=None,
                result=None,
                resent_circuit=resent_qc,
            )
            return resent_qc, record

        # 1. Eve chooses a basis
        eve_basis = self.generate_basis()

        # 2. Eve measures incoming circuit in her chosen basis
        meas_seed = int(self._rng.integers(0, 2**31 - 1)) if self._seed is not None else None
        outcome = measure_state(circuit, basis=eve_basis, shots=1, seed=meas_seed)
        outcome_bit = int(outcome)

        # 3. Eve prepares a BRAND NEW replacement quantum state
        resent_qc = prepare_state(bit=outcome_bit, basis=eve_basis)

        record = EveInterceptionRecord(
            index=index,
            intercepted=True,
            basis=eve_basis,
            result=outcome_bit,
            resent_circuit=resent_qc,
        )
        return resent_qc, record

    def intercept_signals(
        self,
        circuits: Sequence[QuantumCircuit],
    ) -> Tuple[List[QuantumCircuit], List[EveInterceptionRecord]]:
        """Intercept a batch of quantum signals in transit across the channel.

        Args:
            circuits: Sequence of single-qubit QuantumCircuit objects.

        Returns:
            Tuple of (list_of_resent_circuits, list_of_interception_records).
        """
        resent_circuits: List[QuantumCircuit] = []
        records: List[EveInterceptionRecord] = []

        for idx, qc in enumerate(circuits):
            resent_qc, rec = self.intercept_signal(qc, index=idx)
            resent_circuits.append(resent_qc)
            records.append(rec)

        self._records = records
        return resent_circuits, records
