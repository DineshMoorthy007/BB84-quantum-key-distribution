"""Quantum Channel abstraction for the BB84 protocol.

This module models the physical transmission medium connecting Alice to Bob.
In Phase 4, the channel represents an ideal, noiseless quantum channel.
In Phase 7, the channel supports optional eavesdropping interception (Eve)
executing an intercept-resend attack.
In Phase 8, the channel supports optional quantum noise models (BitFlip, PhaseFlip,
Depolarizing) acting directly on quantum carrier states.

Composition Architecture:
    Alice (Transmitter)
         ↓
    QuantumChannel (Input)
         ↓
    [Eve: Intercept-Resend Attack] (Optional, if attached)
         ↓
    [Quantum Noise Channel] (Optional, if attached: BitFlip, PhaseFlip, Depolarizing)
         ↓
    Bob (Receiver)

When both Eve and noise are active:
    1. Alice emits quantum carrier photons into the channel.
    2. Eve intercepts the in-flight photons, measures them, and resends replacement photons.
    3. The resent replacement photons propagate through the environmental noise channel.
    4. Bob receives and measures the corrupted replacement states.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence
from qiskit import QuantumCircuit


class QuantumChannel:
    """Quantum communication channel.

    Transmits single-qubit quantum states from sender to receiver.
    Supports optional eavesdropping interception (Eve) and quantum noise channels.
    """

    def __init__(
        self,
        eve: Optional[Any] = None,
        noise: Optional[Any] = None,
    ) -> None:
        """Initialize quantum channel with optional eavesdropper and noise model.

        Args:
            eve: Optional Eve instance to intercept transmissions.
            noise: Optional QuantumNoiseModel instance to apply physical noise.
        """
        self._eve: Optional[Any] = eve
        self._noise: Optional[Any] = noise

    @property
    def eve(self) -> Optional[Any]:
        """Return the attached eavesdropper instance, if any."""
        return self._eve

    @eve.setter
    def eve(self, value: Optional[Any]) -> None:
        """Set or update the attached eavesdropper."""
        self._eve = value

    @property
    def noise(self) -> Optional[Any]:
        """Return the attached quantum noise model, if any."""
        return self._noise

    @noise.setter
    def noise(self, value: Optional[Any]) -> None:
        """Set or update the attached quantum noise model."""
        self._noise = value

    def attach_eve(self, eve: Any) -> None:
        """Attach an active eavesdropper to intercept transmissions."""
        self._eve = eve

    def detach_eve(self) -> None:
        """Detach any active eavesdropper from the channel."""
        self._eve = None

    def attach_noise(self, noise: Any) -> None:
        """Attach a quantum noise model to the channel."""
        self._noise = noise

    def detach_noise(self) -> None:
        """Detach any active noise model from the channel."""
        self._noise = None

    def transmit_single(
        self,
        circuit: QuantumCircuit,
        eve: Optional[Any] = None,
        noise: Optional[Any] = None,
    ) -> QuantumCircuit:
        """Transmit a single quantum circuit through the channel.

        Order of operations:
            Input -> (Eve Interception) -> (Quantum Noise) -> Output

        Args:
            circuit: The quantum circuit arriving at the channel input.
            eve: Optional override Eve instance for this transmission.
            noise: Optional override noise model for this transmission.

        Returns:
            A new QuantumCircuit representing the state arriving at Bob.
        """
        active_eve = eve if eve is not None else self._eve
        active_noise = noise if noise is not None else self._noise

        curr_circuit = circuit.copy()

        # Step 1: Eve intercepts and resends if active
        if active_eve is not None:
            curr_circuit, _ = active_eve.intercept_signal(curr_circuit)

        # Step 2: Physical quantum noise acts on the state in transit
        if active_noise is not None:
            curr_circuit = active_noise.apply(curr_circuit)

        return curr_circuit

    def transmit(
        self,
        circuits: Sequence[QuantumCircuit],
        eve: Optional[Any] = None,
        noise: Optional[Any] = None,
    ) -> List[QuantumCircuit]:
        """Transmit a batch of quantum circuits through the channel.

        Order of operations:
            Alice Signals -> [Eve] -> [Noise] -> Bob Signals

        Args:
            circuits: Sequence of quantum circuits to transmit.
            eve: Optional override Eve instance for this transmission.
            noise: Optional override noise model for this transmission.

        Returns:
            List of transmitted quantum circuits ready for Bob.
        """
        active_eve = eve if eve is not None else self._eve
        active_noise = noise if noise is not None else self._noise

        # Step 1: Eve intercepts and resends
        if active_eve is not None:
            intermediate_circuits, _ = active_eve.intercept_signals(circuits)
        else:
            intermediate_circuits = [qc.copy() for qc in circuits]

        # Step 2: Physical quantum noise acts on all circuits in transit
        if active_noise is not None:
            return active_noise.apply_batch(intermediate_circuits)

        return intermediate_circuits
