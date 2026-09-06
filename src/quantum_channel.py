"""Quantum Channel abstraction for the BB84 protocol.

This module models the physical transmission medium connecting Alice to Bob.
In Phase 4, the channel represents an ideal, noiseless quantum channel.
In Phase 7, the channel supports optional eavesdropping interception (Eve)
executing an intercept-resend attack.

Architecture:
    Path 1 (Ideal / No Eve):
        Alice -> QuantumChannel.transmit() -> Bob

    Path 2 (Eve Enabled):
        Alice -> QuantumChannel.transmit(..., eve=Eve()) -> Bob
        (or Alice -> Channel -> Eve -> Channel -> Bob)
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence
from qiskit import QuantumCircuit


class QuantumChannel:
    """Quantum communication channel.

    Transmits single-qubit quantum states from sender to receiver.
    In the absence of an eavesdropper, incoming circuits propagate unperturbed.
    If an eavesdropper (Eve) is attached or provided, signals undergo
    quantum interception and state replacement prior to reaching the receiver.
    """

    def __init__(self, eve: Optional[Any] = None) -> None:
        """Initialize quantum channel with optional eavesdropper.

        Args:
            eve: Optional Eve instance to tap the channel.
        """
        self._eve: Optional[Any] = eve

    @property
    def eve(self) -> Optional[Any]:
        """Return the attached eavesdropper instance, if any."""
        return self._eve

    @eve.setter
    def eve(self, value: Optional[Any]) -> None:
        """Set or update the attached eavesdropper."""
        self._eve = value

    def attach_eve(self, eve: Any) -> None:
        """Attach an active eavesdropper to intercept transmissions."""
        self._eve = eve

    def detach_eve(self) -> None:
        """Detach any active eavesdropper from the channel."""
        self._eve = None

    def transmit_single(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Transmit a single quantum circuit through the channel.

        Args:
            circuit: The quantum circuit arriving at the channel input.

        Returns:
            A clean copy of the transmitted quantum circuit (or Eve's resent state).
        """
        if self._eve is not None:
            resent_qc, _ = self._eve.intercept_signal(circuit)
            return resent_qc
        return circuit.copy()

    def transmit(
        self,
        circuits: Sequence[QuantumCircuit],
        eve: Optional[Any] = None,
    ) -> List[QuantumCircuit]:
        """Transmit a batch of quantum circuits through the channel.

        Args:
            circuits: Sequence of quantum circuits to transmit.
            eve: Optional override Eve instance for this transmission.

        Returns:
            List of transmitted quantum circuits ready for Bob.
        """
        active_eve = eve if eve is not None else self._eve
        if active_eve is not None:
            resent_circuits, _ = active_eve.intercept_signals(circuits)
            return resent_circuits
        return [self.transmit_single(qc) for qc in circuits]
