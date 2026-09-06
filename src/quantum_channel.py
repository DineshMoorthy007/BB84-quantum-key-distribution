"""Quantum Channel abstraction for the BB84 protocol.

This module models the physical transmission medium connecting Alice to Bob.
In Phase 4, the channel represents an ideal, noiseless quantum channel that
transmits quantum circuits without introducing decoherence, loss, or eavesdropping.

Architecture:
    Alice -> QuantumChannel.transmit() -> Bob

Design Extensibility:
    Future phases can extend this channel with:
    - Eavesdropper interception (Eve)
    - Channel noise models (depolarizing, bit-flip, phase-flip)
    - Transmission losses and attenuation
    without modifying Alice or Bob's interfaces.
"""

from __future__ import annotations

from typing import List, Sequence
from qiskit import QuantumCircuit


class QuantumChannel:
    """Ideal quantum communication channel.

    Transmits single-qubit quantum states from sender to receiver.
    In the ideal regime, incoming quantum circuits are faithfully propagated.
    """

    def __init__(self) -> None:
        """Initialize an ideal quantum channel."""
        pass

    def transmit_single(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Transmit a single quantum circuit through the channel.

        Args:
            circuit: The quantum circuit arriving at the channel input.

        Returns:
            A clean copy of the transmitted quantum circuit.
        """
        return circuit.copy()

    def transmit(self, circuits: Sequence[QuantumCircuit]) -> List[QuantumCircuit]:
        """Transmit a batch of quantum circuits through the channel.

        Args:
            circuits: Sequence of quantum circuits to transmit.

        Returns:
            List of transmitted quantum circuits ready for Bob.
        """
        return [self.transmit_single(qc) for qc in circuits]
