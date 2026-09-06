"""Unit tests for Eve (Eavesdropper) intercept-resend attack in Phase 7.

Tests cover:
- Eve basis generation (length, valid bases)
- Reproducibility across identical random seeds
- Eve measurement in matching bases
- Wrong-basis probabilistic measurement behavior (50/50 outcomes)
- Resent-state correctness and quantum state equivalence
- Confirmation that Eve constructs new quantum states rather than passing through
- Interception probability modes: 0.0 (no interception), 1.0 (full), and 0.5 (partial)
"""

from __future__ import annotations

import pytest
import numpy as np
from qiskit import QuantumCircuit

from src.eve import Eve, EveInterceptionRecord
from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    get_statevector,
    measure_state,
    prepare_state,
    prepare_state_0,
    prepare_state_1,
    prepare_state_plus,
    prepare_state_minus,
    statevectors_are_equivalent,
)
from src.quantum_channel import QuantumChannel


class TestEveBasisGeneration:
    """Test 1 & 2: Eve basis generation and reproducibility."""

    def test_basis_generation_length_and_values(self):
        """Test 1: Verify N generated bases have correct length and values in {'Z', 'X'}."""
        eve = Eve(seed=42)
        n = 200
        bases = eve.generate_bases(n)
        assert len(bases) == n
        assert all(b in ("Z", "X") for b in bases)
        assert "Z" in bases
        assert "X" in bases

    def test_single_basis_generation(self):
        """Verify single basis generation returns a valid basis string."""
        eve = Eve(seed=123)
        for _ in range(20):
            b = eve.generate_basis()
            assert b in ("Z", "X")

    def test_reproducibility_same_seed(self):
        """Test 2: Verify same seed yields identical basis sequence."""
        eve1 = Eve(seed=999)
        eve2 = Eve(seed=999)
        bases1 = eve1.generate_bases(100)
        bases2 = eve2.generate_bases(100)
        assert bases1 == bases2

    def test_different_seeds_differ(self):
        """Verify different seeds produce different sequences."""
        eve1 = Eve(seed=1)
        eve2 = Eve(seed=2)
        bases1 = eve1.generate_bases(100)
        bases2 = eve2.generate_bases(100)
        assert bases1 != bases2

    def test_invalid_parameters(self):
        """Verify parameter validation for Eve initialization and basis generation."""
        with pytest.raises(ValueError):
            Eve(interception_probability=-0.1)
        with pytest.raises(ValueError):
            Eve(interception_probability=1.1)
        with pytest.raises(TypeError):
            Eve(interception_probability="high")  # type: ignore
        with pytest.raises(TypeError):
            Eve(seed="seed123")  # type: ignore

        eve = Eve()
        with pytest.raises(ValueError):
            eve.generate_bases(0)
        with pytest.raises(ValueError):
            eve.generate_bases(-10)


class TestEveMatchingBasisMeasurement:
    """Test 3: Eve measurement in matching basis yields deterministic results."""

    @pytest.mark.parametrize(
        "prep_func,basis,expected_bit",
        [
            (prepare_state_0, COMPUTATIONAL_BASIS, 0),
            (prepare_state_1, COMPUTATIONAL_BASIS, 1),
            (prepare_state_plus, HADAMARD_BASIS, 0),
            (prepare_state_minus, HADAMARD_BASIS, 1),
        ],
    )
    def test_matching_basis_measurement(self, prep_func, basis, expected_bit):
        """Verify measuring an eigenstate in its own basis yields deterministic eigenvalue."""
        for shot in range(20):
            qc = prep_func()
            outcome = measure_state(qc, basis=basis, shots=1, seed=100 + shot)
            assert outcome == expected_bit


class TestEveWrongBasisMeasurement:
    """Test 4: Eve measurement in wrong (conjugate) basis is probabilistic (50/50)."""

    def test_plus_measured_in_z_basis(self):
        """Verify |+> measured in Z yields ~50% 0 and ~50% 1."""
        shots = 1000
        outcomes = []
        for i in range(shots):
            qc = prepare_state_plus()
            outcomes.append(measure_state(qc, basis="Z", shots=1, seed=1000 + i))
        p0 = outcomes.count(0) / shots
        p1 = outcomes.count(1) / shots
        assert 0.44 <= p0 <= 0.56
        assert 0.44 <= p1 <= 0.56

    def test_minus_measured_in_z_basis(self):
        """Verify |-> measured in Z yields ~50% 0 and ~50% 1."""
        shots = 1000
        outcomes = []
        for i in range(shots):
            qc = prepare_state_minus()
            outcomes.append(measure_state(qc, basis="Z", shots=1, seed=2000 + i))
        p0 = outcomes.count(0) / shots
        p1 = outcomes.count(1) / shots
        assert 0.44 <= p0 <= 0.56
        assert 0.44 <= p1 <= 0.56

    def test_zero_measured_in_x_basis(self):
        """Verify |0> measured in X yields ~50% 0 and ~50% 1."""
        shots = 1000
        outcomes = []
        for i in range(shots):
            qc = prepare_state_0()
            outcomes.append(measure_state(qc, basis="X", shots=1, seed=3000 + i))
        p0 = outcomes.count(0) / shots
        p1 = outcomes.count(1) / shots
        assert 0.44 <= p0 <= 0.56
        assert 0.44 <= p1 <= 0.56


class TestEveResentStateCorrectness:
    """Test 5 & 6: Resent state correctness and state reconstruction verification."""

    @pytest.mark.parametrize(
        "bit,basis,target_func",
        [
            (0, "Z", prepare_state_0),
            (1, "Z", prepare_state_1),
            (0, "X", prepare_state_plus),
            (1, "X", prepare_state_minus),
        ],
    )
    def test_resent_state_quantum_equivalence(self, bit, basis, target_func):
        """Test 5: Resent state prepared by Eve matches target statevector."""
        resent_qc = prepare_state(bit=bit, basis=basis)
        target_qc = target_func()
        assert statevectors_are_equivalent(
            get_statevector(resent_qc), get_statevector(target_qc)
        )

    def test_new_state_is_constructed(self):
        """Test 6: Verify Eve constructs replacement quantum signal rather than returning original."""
        eve = Eve(seed=42, interception_probability=1.0)
        orig_qc = prepare_state_0()

        resent_qc, record = eve.intercept_signal(orig_qc, index=0)

        # Confirm different Python object instance
        assert resent_qc is not orig_qc
        assert record.intercepted is True
        assert record.basis in ("Z", "X")
        assert record.result in (0, 1)

        # Verify quantum behavior: measuring resent_qc in Eve's chosen basis gives Eve's bit with certainty
        verification_meas = measure_state(resent_qc, basis=record.basis, shots=1, seed=777)
        assert verification_meas == record.result


class TestInterceptionProbabilities:
    """Test 7, 8, 9: Interception probability behaviors (0.0, 1.0, 0.5)."""

    def test_no_interception_prob_zero(self):
        """Test 7: eve_probability = 0.0 -> no signals intercepted, original states preserved."""
        eve = Eve(seed=42, interception_probability=0.0)
        circuits = [prepare_state(0, "Z"), prepare_state(1, "X"), prepare_state(1, "Z")]
        resent, records = eve.intercept_signals(circuits)

        assert len(resent) == 3
        assert len(records) == 3
        assert eve.intercepted_count == 0
        assert all(not r.intercepted for r in records)
        assert all(r.basis is None for r in records)
        assert all(r.result is None for r in records)

        # Check quantum states are unmodified copies
        for orig, res in zip(circuits, resent):
            assert statevectors_are_equivalent(
                get_statevector(orig), get_statevector(res)
            )

    def test_full_interception_prob_one(self):
        """Test 8: eve_probability = 1.0 -> 100% of signals intercepted and measured."""
        eve = Eve(seed=42, interception_probability=1.0)
        n = 100
        circuits = [prepare_state(0, "Z") for _ in range(n)]
        resent, records = eve.intercept_signals(circuits)

        assert len(resent) == n
        assert eve.intercepted_count == n
        assert all(r.intercepted for r in records)
        assert all(r.basis in ("Z", "X") for r in records)
        assert all(r.result in (0, 1) for r in records)

    def test_partial_interception_prob_half(self):
        """Test 9: eve_probability = 0.5 -> statistically ~50% intercepted for large sample."""
        n = 1000
        eve = Eve(seed=12345, interception_probability=0.5)
        circuits = [prepare_state(0, "Z") for _ in range(n)]
        _, records = eve.intercept_signals(circuits)

        intercepted_count = sum(1 for r in records if r.intercepted)
        intercepted_ratio = intercepted_count / n

        # Statistical tolerance: with N=1000 and p=0.5, std = sqrt(1000*0.25) ~ 15.8
        # 3 sigma range is ~ [45%, 55%]
        assert 0.43 <= intercepted_ratio <= 0.57
