"""Quantum primitives for the BB84 Quantum Key Distribution protocol.

This module implements the fundamental quantum states, preparation circuits,
and projective measurement operators across the two mutually unbiased bases
used in BB84: the computational (Z) basis and the Hadamard (X) basis.

Academic Foundations:
    - Computational Basis (|0>, |1>): Eigenstates of the Pauli-Z operator (sigma_z).
    - Hadamard Basis (|+>, |->): Eigenstates of the Pauli-X operator (sigma_x),
      where |+> = (|0> + |1>) / sqrt(2) and |-> = (|0> - |1>) / sqrt(2).
    - Mutual Unbiasedness: |<psi_z | phi_x>|^2 = 1/2 for all basis pairs.

Security Disclaimer:
    These quantum primitives model projective measurements and state evolutions.
    This implementation serves for experimental simulation and educational analysis,
    and does not constitute a formal mathematical proof of quantum security.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union
import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

# Basis definitions
COMPUTATIONAL_BASIS: str = "Z"
HADAMARD_BASIS: str = "X"
VALID_BASES: tuple[str, str] = (COMPUTATIONAL_BASIS, HADAMARD_BASIS)
VALID_BITS: tuple[int, int] = (0, 1)


def validate_bit(bit: Any) -> int:
    """Validate that the input is a valid classical bit (0 or 1).

    Args:
        bit: Bit value to validate.

    Returns:
        The validated integer bit (0 or 1).

    Raises:
        TypeError: If bit is a boolean or not an integer.
        ValueError: If bit is not in {0, 1}.
    """
    if isinstance(bit, bool) or not isinstance(bit, int):
        raise TypeError(f"Bit must be an integer (0 or 1), got {type(bit).__name__}: {bit!r}")
    if bit not in VALID_BITS:
        raise ValueError(f"Invalid bit value: {bit}. Expected 0 or 1.")
    return bit


def validate_basis(basis: Any) -> str:
    """Validate and normalize the quantum measurement basis.

    Args:
        basis: The basis name ('Z' for computational, 'X' for Hadamard).

    Returns:
        The uppercase normalized basis string ('Z' or 'X').

    Raises:
        TypeError: If basis is not a string.
        ValueError: If basis is not 'Z' or 'X'.
    """
    if not isinstance(basis, str):
        raise TypeError(f"Basis must be a string, got {type(basis).__name__}: {basis!r}")

    normalized = basis.strip().upper()
    if normalized not in VALID_BASES:
        raise ValueError(
            f"Invalid basis: {basis!r}. Supported bases are 'Z' (computational) and 'X' (Hadamard)."
        )
    return normalized


def create_qubit_circuit(name: Optional[str] = None) -> QuantumCircuit:
    """Create a single-qubit quantum circuit initialized in |0>.

    Args:
        name: Optional descriptive label for the circuit.

    Returns:
        QuantumCircuit containing 1 qubit.
    """
    return QuantumCircuit(1, name=name)


def prepare_state_0(circuit: Optional[QuantumCircuit] = None) -> QuantumCircuit:
    """Prepare the computational basis state |0> (bit 0 in Z basis).

    In standard quantum circuit semantics, qubits initialize in state |0>.
    No gate operations are applied.

    Args:
        circuit: Optional existing single-qubit circuit to populate.

    Returns:
        QuantumCircuit with qubit in state |0>.
    """
    qc = create_qubit_circuit(name="state_0") if circuit is None else circuit
    return qc


def prepare_state_1(circuit: Optional[QuantumCircuit] = None) -> QuantumCircuit:
    """Prepare the computational basis state |1> (bit 1 in Z basis).

    Applies a Pauli-X (NOT) gate: X|0> = |1>.

    Args:
        circuit: Optional existing single-qubit circuit to populate.

    Returns:
        QuantumCircuit with qubit in state |1>.
    """
    qc = create_qubit_circuit(name="state_1") if circuit is None else circuit
    qc.x(0)
    return qc


def prepare_state_plus(circuit: Optional[QuantumCircuit] = None) -> QuantumCircuit:
    """Prepare the Hadamard basis state |+> (bit 0 in X basis).

    Applies a Hadamard (H) gate: H|0> = (|0> + |1>) / sqrt(2) = |+>.

    Args:
        circuit: Optional existing single-qubit circuit to populate.

    Returns:
        QuantumCircuit with qubit in state |+>.
    """
    qc = create_qubit_circuit(name="state_plus") if circuit is None else circuit
    qc.h(0)
    return qc


def prepare_state_minus(circuit: Optional[QuantumCircuit] = None) -> QuantumCircuit:
    """Prepare the Hadamard basis state |-> (bit 1 in X basis).

    Applies a Pauli-X gate followed by a Hadamard gate:
        |0> --[X]--> |1> --[H]--> (|0> - |1>) / sqrt(2) = |->.

    Args:
        circuit: Optional existing single-qubit circuit to populate.

    Returns:
        QuantumCircuit with qubit in state |->.
    """
    qc = create_qubit_circuit(name="state_minus") if circuit is None else circuit
    qc.x(0)
    qc.h(0)
    return qc


def prepare_state(bit: int, basis: str) -> QuantumCircuit:
    """Prepare a BB84 single-qubit quantum state from a bit and basis choice.

    State Mapping:
        - bit=0, basis="Z" -> |0>
        - bit=1, basis="Z" -> |1>
        - bit=0, basis="X" -> |+>
        - bit=1, basis="X" -> |->

    Args:
        bit: Classical bit to encode (0 or 1).
        basis: Basis in which to encode ('Z' or 'X').

    Returns:
        QuantumCircuit prepared in the corresponding quantum state.

    Raises:
        TypeError: If bit or basis has invalid type.
        ValueError: If bit or basis has unsupported value.
    """
    valid_b = validate_bit(bit)
    valid_basis = validate_basis(basis)

    if valid_basis == COMPUTATIONAL_BASIS:
        return prepare_state_0() if valid_b == 0 else prepare_state_1()
    else:  # HADAMARD_BASIS
        return prepare_state_plus() if valid_b == 0 else prepare_state_minus()


def get_statevector(circuit: QuantumCircuit) -> Statevector:
    """Compute the statevector of a prepared single-qubit circuit.

    Used for educational inspection and formal mathematical validation.
    The input circuit should not contain classical measurement gates.

    Args:
        circuit: Pure state preparation circuit without measurements.

    Returns:
        Qiskit Statevector instance representing the quantum state.
    """
    return Statevector(circuit)


def statevectors_are_equivalent(
    sv1: Statevector | Sequence[complex] | np.ndarray,
    sv2: Statevector | Sequence[complex] | np.ndarray,
    atol: float = 1e-7,
) -> bool:
    """Verify whether two statevectors represent the same quantum state up to global phase.

    Two pure states |psi> and |phi> are physically identical iff |psi> = e^(i theta) |phi>.

    Args:
        sv1: First statevector or array of complex amplitudes.
        sv2: Second statevector or array of complex amplitudes.
        atol: Absolute tolerance for numeric comparison.

    Returns:
        True if the states are physically equivalent up to a global phase factor.
    """
    s1 = sv1 if isinstance(sv1, Statevector) else Statevector(sv1)
    s2 = sv2 if isinstance(sv2, Statevector) else Statevector(sv2)
    return s1.equiv(s2, atol=atol)


def measure_z_basis(
    circuit: QuantumCircuit,
    shots: int = 1,
    seed: Optional[int] = None,
) -> Union[int, List[int]]:
    """Measure a single qubit in the computational (Z) basis {|0>, |1>}.

    Performs a standard projective measurement along sigma_z.
    The input circuit is copied and not modified in-place.

    Args:
        circuit: Single-qubit state circuit to measure.
        shots: Number of measurement repetitions (default 1).
        seed: Random seed for simulator execution to ensure reproducibility.

    Returns:
        A single classical bit (0 or 1) if shots == 1, or a list of outcomes if shots > 1.

    Raises:
        ValueError: If shots < 1.
    """
    if shots < 1:
        raise ValueError(f"shots must be a positive integer, got {shots}")

    meas_circuit = circuit.copy()
    if meas_circuit.num_clbits == 0:
        meas_circuit.add_register(ClassicalRegister(1, "c"))
    meas_circuit.measure(0, 0)

    backend = AerSimulator()
    job = backend.run(meas_circuit, shots=shots, seed_simulator=seed, memory=True)
    memory = job.result().get_memory()
    outcomes = [int(val) for val in memory]

    return outcomes[0] if shots == 1 else outcomes


def measure_x_basis(
    circuit: QuantumCircuit,
    shots: int = 1,
    seed: Optional[int] = None,
) -> Union[int, List[int]]:
    """Measure a single qubit in the Hadamard (X) basis {|+>, |->}.

    Physical measurement instruments project onto the computational basis {|0>, |1>}.
    To measure in the X basis, a Hadamard gate (H) is applied prior to measurement,
    mapping:
        |+> --[H]--> |0>  (eigenvalue +1, bit 0)
        |-> --[H]--> |1>  (eigenvalue -1, bit 1)

    The input circuit is copied and not modified in-place.

    Args:
        circuit: Single-qubit state circuit to measure.
        shots: Number of measurement repetitions (default 1).
        seed: Random seed for simulator execution to ensure reproducibility.

    Returns:
        A single classical bit (0 or 1) if shots == 1, or a list of outcomes if shots > 1.

    Raises:
        ValueError: If shots < 1.
    """
    if shots < 1:
        raise ValueError(f"shots must be a positive integer, got {shots}")

    meas_circuit = circuit.copy()
    if meas_circuit.num_clbits == 0:
        meas_circuit.add_register(ClassicalRegister(1, "c"))

    # Basis transformation to diagonal basis
    meas_circuit.h(0)
    meas_circuit.measure(0, 0)

    backend = AerSimulator()
    job = backend.run(meas_circuit, shots=shots, seed_simulator=seed, memory=True)
    memory = job.result().get_memory()
    outcomes = [int(val) for val in memory]

    return outcomes[0] if shots == 1 else outcomes


def measure_state(
    circuit: QuantumCircuit,
    basis: str,
    shots: int = 1,
    seed: Optional[int] = None,
) -> Union[int, List[int]]:
    """Measure a single qubit in the specified BB84 basis ('Z' or 'X').

    Args:
        circuit: Single-qubit state circuit.
        basis: Target measurement basis ('Z' or 'X').
        shots: Number of measurement repetitions (default 1).
        seed: Random seed for simulator reproducibility.

    Returns:
        A single classical bit (0 or 1) if shots == 1, or a list of outcomes if shots > 1.

    Raises:
        TypeError: If basis is not a string.
        ValueError: If basis is not 'Z' or 'X', or shots < 1.
    """
    valid_basis = validate_basis(basis)
    if valid_basis == COMPUTATIONAL_BASIS:
        return measure_z_basis(circuit, shots=shots, seed=seed)
    else:
        return measure_x_basis(circuit, shots=shots, seed=seed)
