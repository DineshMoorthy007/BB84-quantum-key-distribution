"""Unit tests for Phase 8 Quantum Noise models.

Tests cover:
- Bit-flip noise model (p=0, p=1, stochastic sampling, Pauli-X action)
- Phase-flip noise model (p=0, p=1, stochastic sampling, Pauli-Z action)
- Depolarizing noise model (p=0, p=1, Qiskit standard parameterization)
- Basis-dependent quantum behavior (phase flip on Z vs X basis)
- Parameter validation (p in [0.0, 1.0], type checking)
- Seed reproducibility across stochastic runs
"""

from __future__ import annotations

import pytest
import numpy as np
from qiskit import QuantumCircuit

from noise.base import QuantumNoiseModel
from noise.bit_flip import BitFlipNoise
from noise.phase_flip import PhaseFlipNoise
from noise.depolarizing import DepolarizingNoise
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


class TestNoiseParameterValidation:
    """Test parameter validation across all quantum noise models."""

    @pytest.mark.parametrize(
        "model_cls",
        [BitFlipNoise, PhaseFlipNoise, DepolarizingNoise],
    )
    def test_invalid_probability_range(self, model_cls):
        """Verify negative probabilities and probabilities > 1.0 are rejected."""
        with pytest.raises(ValueError):
            model_cls(probability=-0.01)
        with pytest.raises(ValueError):
            model_cls(probability=1.01)
        with pytest.raises(ValueError):
            model_cls(probability=-5.0)

    @pytest.mark.parametrize(
        "model_cls",
        [BitFlipNoise, PhaseFlipNoise, DepolarizingNoise],
    )
    def test_invalid_probability_type(self, model_cls):
        """Verify non-float/int types are rejected."""
        with pytest.raises(TypeError):
            model_cls(probability="0.5")  # type: ignore
        with pytest.raises(TypeError):
            model_cls(probability=True)  # type: ignore
        with pytest.raises(TypeError):
            model_cls(seed="42")  # type: ignore
        with pytest.raises(TypeError):
            model_cls(seed=True)  # type: ignore


class TestBitFlipNoise:
    """Test BitFlipNoise model behavior."""

    def test_bit_flip_p_zero_identity(self):
        """Verify p=0 leaves quantum state completely unchanged."""
        noise = BitFlipNoise(probability=0.0)
        qc0 = prepare_state_0()
        noisy_qc = noise.apply(qc0)
        assert statevectors_are_equivalent(get_statevector(qc0), get_statevector(noisy_qc))

    def test_bit_flip_p_one_deterministic_x(self):
        """Verify p=1 deterministically applies Pauli-X (|0> -> |1>, |1> -> |0>)."""
        noise = BitFlipNoise(probability=1.0)

        # |0> -> |1>
        qc0 = prepare_state_0()
        noisy0 = noise.apply(qc0)
        assert measure_state(noisy0, basis="Z", shots=1, seed=42) == 1

        # |1> -> |0>
        qc1 = prepare_state_1()
        noisy1 = noise.apply(qc1)
        assert measure_state(noisy1, basis="Z", shots=1, seed=42) == 0

    def test_bit_flip_stochastic_frequency(self):
        """Verify intermediate probability p=0.3 produces ~30% bit flips."""
        p = 0.30
        noise = BitFlipNoise(probability=p, seed=123)
        trials = 1000
        flips = 0

        for _ in range(trials):
            qc = prepare_state_0()
            noisy = noise.apply(qc)
            if measure_state(noisy, basis="Z", shots=1) == 1:
                flips += 1

        ratio = flips / trials
        assert 0.25 <= ratio <= 0.35

    def test_bit_flip_seed_reproducibility(self):
        """Verify fixed seed yields identical stochastic sequence."""
        noise1 = BitFlipNoise(probability=0.4, seed=999)
        noise2 = BitFlipNoise(probability=0.4, seed=999)

        circuits = [prepare_state_0() for _ in range(50)]
        noisy1 = noise1.apply_batch(circuits)
        noisy2 = noise2.apply_batch(circuits)

        res1 = [measure_state(c, basis="Z", shots=1, seed=10) for c in noisy1]
        res2 = [measure_state(c, basis="Z", shots=1, seed=10) for c in noisy2]
        assert res1 == res2


class TestPhaseFlipNoise:
    """Test PhaseFlipNoise model behavior and basis-dependence."""

    def test_phase_flip_p_zero_identity(self):
        """Verify p=0 leaves quantum state completely unchanged."""
        noise = PhaseFlipNoise(probability=0.0)
        qc_plus = prepare_state_plus()
        noisy_plus = noise.apply(qc_plus)
        assert statevectors_are_equivalent(get_statevector(qc_plus), get_statevector(noisy_plus))

    def test_phase_flip_p_one_deterministic_z(self):
        """Verify p=1 deterministically applies Pauli-Z."""
        noise = PhaseFlipNoise(probability=1.0)

        # |+> -> |->
        qc_plus = prepare_state_plus()
        noisy_plus = noise.apply(qc_plus)
        assert measure_state(noisy_plus, basis="X", shots=1, seed=42) == 1

        # |-> -> |+>
        qc_minus = prepare_state_minus()
        noisy_minus = noise.apply(qc_minus)
        assert measure_state(noisy_minus, basis="X", shots=1, seed=42) == 0

    def test_phase_flip_basis_dependence_z_basis_immunity(self):
        """Fundamental quantum test: Phase flip on Z-basis eigenstates has NO classical effect!

        Z|0> = |0>
        Z|1> = -|1> (global phase change only, exp(i*pi) = -1)
        Both states yield deterministic 0 and 1 measurements in the Z basis.
        """
        noise = PhaseFlipNoise(probability=1.0)

        # Apply Z to |0>
        qc0 = prepare_state_0()
        noisy0 = noise.apply(qc0)
        assert measure_state(noisy0, basis="Z", shots=1, seed=1) == 0
        assert statevectors_are_equivalent(get_statevector(qc0), get_statevector(noisy0))

        # Apply Z to |1>
        qc1 = prepare_state_1()
        noisy1 = noise.apply(qc1)
        assert measure_state(noisy1, basis="Z", shots=1, seed=1) == 1
        assert statevectors_are_equivalent(get_statevector(qc1), get_statevector(noisy1))

    def test_phase_flip_basis_dependence_x_basis_inversion(self):
        """Fundamental quantum test: Phase flip on X-basis eigenstates flips the state (|0> <-> |1> in X basis)."""
        noise = PhaseFlipNoise(probability=1.0)

        qc_plus = prepare_state_plus()
        noisy_plus = noise.apply(qc_plus)
        # Originally |+> gave 0 in X basis; now it gives 1
        assert measure_state(noisy_plus, basis="X", shots=1, seed=2) == 1

        qc_minus = prepare_state_minus()
        noisy_minus = noise.apply(qc_minus)
        # Originally |-> gave 1 in X basis; now it gives 0
        assert measure_state(noisy_minus, basis="X", shots=1, seed=2) == 0


class TestDepolarizingNoise:
    """Test DepolarizingNoise model and Qiskit Aer parameterization."""

    def test_depolarizing_p_zero_identity(self):
        """Verify p=0 (lambda=0) acts as exact identity channel."""
        noise = DepolarizingNoise(probability=0.0)
        qc = prepare_state_0()
        noisy = noise.apply(qc)
        assert statevectors_are_equivalent(get_statevector(qc), get_statevector(noisy))

    def test_depolarizing_qiskit_probabilities(self):
        """Verify internal probabilities match Qiskit depolarizing_error parameterization.

        P(I) = 1 - 3*lambda/4, P(X) = P(Y) = P(Z) = lambda/4
        """
        lam = 0.20
        noise = DepolarizingNoise(probability=lam)
        probs = noise.pauli_probabilities
        np.testing.assert_allclose(probs[0], 1.0 - 0.75 * lam)
        np.testing.assert_allclose(probs[1], 0.25 * lam)
        np.testing.assert_allclose(probs[2], 0.25 * lam)
        np.testing.assert_allclose(probs[3], 0.25 * lam)

    def test_depolarizing_p_one_maximally_mixed(self):
        """Verify p=1.0 (complete depolarization) yields ~50% error rate in both bases."""
        noise = DepolarizingNoise(probability=1.0, seed=42)
        shots = 1000

        # In Z-basis: measuring |0> after complete depolarization gives 50/50
        outcomes_z = []
        for _ in range(shots):
            qc = prepare_state_0()
            noisy = noise.apply(qc)
            outcomes_z.append(measure_state(noisy, basis="Z", shots=1))

        error_rate_z = outcomes_z.count(1) / shots
        assert 0.44 <= error_rate_z <= 0.56

        # In X-basis: measuring |+> after complete depolarization gives 50/50
        outcomes_x = []
        for _ in range(shots):
            qc = prepare_state_plus()
            noisy = noise.apply(qc)
            outcomes_x.append(measure_state(noisy, basis="X", shots=1))

        error_rate_x = outcomes_x.count(1) / shots
        assert 0.44 <= error_rate_x <= 0.56
