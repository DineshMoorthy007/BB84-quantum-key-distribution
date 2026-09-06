"""Quantum noise models and channel error simulation package for BB84.

This package provides quantum state-level noise channels:
- QuantumNoiseModel: Abstract base class defining the noise model interface.
- BitFlipNoise: Pauli-X channel inverting computational basis states.
- PhaseFlipNoise: Pauli-Z channel inducing basis-dependent phase errors.
- DepolarizingNoise: Isotropic decoherence channel adhering to Qiskit Aer's parameterization.
"""

from .base import QuantumNoiseModel
from .bit_flip import BitFlipNoise
from .depolarizing import DepolarizingNoise
from .phase_flip import PhaseFlipNoise

__all__ = [
    "QuantumNoiseModel",
    "BitFlipNoise",
    "PhaseFlipNoise",
    "DepolarizingNoise",
]
