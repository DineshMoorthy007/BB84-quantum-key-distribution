"""Unit tests for the BB84 quantum primitives module."""

import math
import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
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

SQRT2_INV = 1.0 / math.sqrt(2.0)
EXPECTED_0 = Statevector([1.0 + 0.0j, 0.0 + 0.0j])
EXPECTED_1 = Statevector([0.0 + 0.0j, 1.0 + 0.0j])
EXPECTED_PLUS = Statevector([SQRT2_INV + 0.0j, SQRT2_INV + 0.0j])
EXPECTED_MINUS = Statevector([SQRT2_INV + 0.0j, -SQRT2_INV + 0.0j])


class TestStatePreparation:
    """Test quantum state preparation across Z and X bases."""

    def test_prepare_state_0(self) -> None:
        """Verify |0> state preparation."""
        qc = prepare_state_0()
        assert qc.num_qubits == 1
        assert qc.num_clbits == 0
        sv = get_statevector(qc)
        assert statevectors_are_equivalent(sv, EXPECTED_0)

    def test_prepare_state_1(self) -> None:
        """Verify |1> state preparation."""
        qc = prepare_state_1()
        assert qc.num_qubits == 1
        sv = get_statevector(qc)
        assert statevectors_are_equivalent(sv, EXPECTED_1)

    def test_prepare_state_plus(self) -> None:
        """Verify |+> state preparation."""
        qc = prepare_state_plus()
        assert qc.num_qubits == 1
        sv = get_statevector(qc)
        assert statevectors_are_equivalent(sv, EXPECTED_PLUS)

    def test_prepare_state_minus(self) -> None:
        """Verify |-> state preparation."""
        qc = prepare_state_minus()
        assert qc.num_qubits == 1
        sv = get_statevector(qc)
        assert statevectors_are_equivalent(sv, EXPECTED_MINUS)

    def test_prepare_state_dispatch_z_basis(self) -> None:
        """Verify prepare_state dispatch for Z basis."""
        qc_0 = prepare_state(0, "Z")
        qc_1 = prepare_state(1, "Z")
        assert statevectors_are_equivalent(get_statevector(qc_0), EXPECTED_0)
        assert statevectors_are_equivalent(get_statevector(qc_1), EXPECTED_1)

    def test_prepare_state_dispatch_x_basis(self) -> None:
        """Verify prepare_state dispatch for X basis."""
        qc_plus = prepare_state(0, "X")
        qc_minus = prepare_state(1, "X")
        assert statevectors_are_equivalent(get_statevector(qc_plus), EXPECTED_PLUS)
        assert statevectors_are_equivalent(get_statevector(qc_minus), EXPECTED_MINUS)

    def test_statevector_global_phase_invariance(self) -> None:
        """Verify statevectors_are_equivalent accounts for global phase."""
        phase = np.exp(1j * 0.75)
        sv_phased = EXPECTED_PLUS * phase
        assert statevectors_are_equivalent(sv_phased, EXPECTED_PLUS)
        assert not statevectors_are_equivalent(EXPECTED_PLUS, EXPECTED_MINUS)


class TestValidation:
    """Test validation of bits and bases."""

    def test_validate_bit_valid(self) -> None:
        """Verify valid bits (0, 1) return expected int."""
        assert validate_bit(0) == 0
        assert validate_bit(1) == 1

    def test_validate_bit_invalid_values(self) -> None:
        """Verify invalid bit values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid bit value"):
            validate_bit(2)
        with pytest.raises(ValueError, match="Invalid bit value"):
            validate_bit(-1)

    def test_validate_bit_invalid_types(self) -> None:
        """Verify non-integer bit types (including booleans) raise TypeError."""
        with pytest.raises(TypeError, match="Bit must be an integer"):
            validate_bit(True)
        with pytest.raises(TypeError, match="Bit must be an integer"):
            validate_bit(False)
        with pytest.raises(TypeError, match="Bit must be an integer"):
            validate_bit("0")
        with pytest.raises(TypeError, match="Bit must be an integer"):
            validate_bit(1.0)

    def test_validate_basis_valid(self) -> None:
        """Verify valid bases return normalized uppercase string."""
        assert validate_basis("Z") == "Z"
        assert validate_basis("z") == "Z"
        assert validate_basis("X") == "X"
        assert validate_basis("x ") == "X"

    def test_validate_basis_invalid_values(self) -> None:
        """Verify invalid basis values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid basis"):
            validate_basis("Y")
        with pytest.raises(ValueError, match="Invalid basis"):
            validate_basis("H")
        with pytest.raises(ValueError, match="Invalid basis"):
            validate_basis("")

    def test_validate_basis_invalid_types(self) -> None:
        """Verify non-string basis types raise TypeError."""
        with pytest.raises(TypeError, match="Basis must be a string"):
            validate_basis(1)
        with pytest.raises(TypeError, match="Basis must be a string"):
            validate_basis(None)


class TestMeasurement:
    """Statistical and functional tests for projective measurements."""

    SHOTS = 2000
    SEED = 42

    def test_measure_z_single_shot(self) -> None:
        """Verify single shot returns an integer bit."""
        qc = prepare_state_0()
        res = measure_z_basis(qc, shots=1, seed=self.SEED)
        assert res in (0, 1)
        assert isinstance(res, int)

    def test_circuit_immutability_during_measurement(self) -> None:
        """Verify measuring does not mutate or add clbits to original circuit."""
        qc = prepare_state_plus()
        original_ops = len(qc.data)
        original_clbits = qc.num_clbits

        measure_z_basis(qc, shots=1)
        assert len(qc.data) == original_ops
        assert qc.num_clbits == original_clbits

        measure_x_basis(qc, shots=1)
        assert len(qc.data) == original_ops
        assert qc.num_clbits == original_clbits

    def test_measure_z_basis_state_0(self) -> None:
        """Z-basis |0> measurement produces ~100% zeros."""
        qc = prepare_state_0()
        outcomes = measure_z_basis(qc, shots=self.SHOTS, seed=self.SEED)
        assert isinstance(outcomes, list)
        assert len(outcomes) == self.SHOTS
        assert sum(outcomes) == 0  # 100% zeros

    def test_measure_z_basis_state_1(self) -> None:
        """Z-basis |1> measurement produces ~100% ones."""
        qc = prepare_state_1()
        outcomes = measure_z_basis(qc, shots=self.SHOTS, seed=self.SEED)
        assert isinstance(outcomes, list)
        assert len(outcomes) == self.SHOTS
        assert sum(outcomes) == self.SHOTS  # 100% ones

    def test_measure_x_basis_state_plus(self) -> None:
        """X-basis |+> measurement produces ~100% zeros."""
        qc = prepare_state_plus()
        outcomes = measure_x_basis(qc, shots=self.SHOTS, seed=self.SEED)
        assert isinstance(outcomes, list)
        assert sum(outcomes) == 0  # 100% zeros

    def test_measure_x_basis_state_minus(self) -> None:
        """X-basis |-> measurement produces ~100% ones."""
        qc = prepare_state_minus()
        outcomes = measure_x_basis(qc, shots=self.SHOTS, seed=self.SEED)
        assert isinstance(outcomes, list)
        assert sum(outcomes) == self.SHOTS  # 100% ones

    def test_measure_z_basis_on_plus_state(self) -> None:
        """X-basis |+> measured in Z basis produces ~50% zeros and 50% ones."""
        qc = prepare_state_plus()
        outcomes = measure_z_basis(qc, shots=self.SHOTS, seed=self.SEED)
        ones_count = sum(outcomes)
        p_ones = ones_count / self.SHOTS
        # 50% expectation with 3 sigma tolerance ~ [0.46, 0.54]
        assert 0.45 <= p_ones <= 0.55

    def test_measure_z_basis_on_minus_state(self) -> None:
        """X-basis |-> measured in Z basis produces ~50% zeros and 50% ones."""
        qc = prepare_state_minus()
        outcomes = measure_z_basis(qc, shots=self.SHOTS, seed=self.SEED)
        ones_count = sum(outcomes)
        p_ones = ones_count / self.SHOTS
        assert 0.45 <= p_ones <= 0.55

    def test_measure_x_basis_on_0_state(self) -> None:
        """Z-basis |0> measured in X basis produces ~50% zeros and 50% ones."""
        qc = prepare_state_0()
        outcomes = measure_x_basis(qc, shots=self.SHOTS, seed=self.SEED)
        ones_count = sum(outcomes)
        p_ones = ones_count / self.SHOTS
        assert 0.45 <= p_ones <= 0.55

    def test_measure_x_basis_on_1_state(self) -> None:
        """Z-basis |1> measured in X basis produces ~50% zeros and 50% ones."""
        qc = prepare_state_1()
        outcomes = measure_x_basis(qc, shots=self.SHOTS, seed=self.SEED)
        ones_count = sum(outcomes)
        p_ones = ones_count / self.SHOTS
        assert 0.45 <= p_ones <= 0.55

    def test_measure_state_unified_wrapper(self) -> None:
        """Verify measure_state delegates correctly to Z and X measurements."""
        qc_z = prepare_state_1()
        assert measure_state(qc_z, "Z", shots=1, seed=self.SEED) == 1

        qc_x = prepare_state_minus()
        assert measure_state(qc_x, "X", shots=1, seed=self.SEED) == 1

    def test_invalid_shots_raises_error(self) -> None:
        """Verify non-positive shots raise ValueError."""
        qc = prepare_state_0()
        with pytest.raises(ValueError, match="shots must be a positive integer"):
            measure_z_basis(qc, shots=0)
        with pytest.raises(ValueError, match="shots must be a positive integer"):
            measure_x_basis(qc, shots=-5)
