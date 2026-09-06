"""BB84 Quantum Key Distribution Simulator.

Core source package for quantum state preparation, measurement,
and protocol execution.
"""

from .alice import Alice, BB84Signal
from .bob import Bob, BobMeasurement
from .config import BB84Config, NoiseModelType
from .quantum_channel import QuantumChannel
from .quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    VALID_BASES,
    VALID_BITS,
    create_qubit_circuit,
    get_statevector,
    measure_state,
    measure_x_basis,
    measure_z_basis,
    prepare_state,
    prepare_state_0,
    prepare_state_1,
    prepare_state_minus,
    prepare_state_plus,
    statevectors_are_equivalent,
    validate_basis,
    validate_bit,
)

__all__ = [
    "Alice",
    "BB84Signal",
    "Bob",
    "BobMeasurement",
    "QuantumChannel",
    "BB84Config",
    "NoiseModelType",
    "COMPUTATIONAL_BASIS",
    "HADAMARD_BASIS",
    "VALID_BASES",
    "VALID_BITS",
    "create_qubit_circuit",
    "prepare_state_0",
    "prepare_state_1",
    "prepare_state_plus",
    "prepare_state_minus",
    "prepare_state",
    "get_statevector",
    "statevectors_are_equivalent",
    "measure_z_basis",
    "measure_x_basis",
    "measure_state",
    "validate_bit",
    "validate_basis",
]



