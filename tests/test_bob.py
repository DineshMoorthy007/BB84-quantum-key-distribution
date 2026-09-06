"""Unit and integration tests for Bob (Receiver) and the Quantum Channel in BB84."""

import pytest
from qiskit.quantum_info import Statevector

from src.alice import Alice
from src.bob import Bob, BobMeasurement
from src.quantum_channel import QuantumChannel
from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    get_statevector,
    prepare_state_0,
    prepare_state_1,
    prepare_state_minus,
    prepare_state_plus,
    statevectors_are_equivalent,
)


class TestBobBasisGeneration:
    """Test Bob's independent basis generation and reproducibility."""

    def test_number_of_bases(self) -> None:
        """Test 1: For N incoming signals, len(bob.bases) == N."""
        bob = Bob(seed=42)
        for n in [1, 10, 50, 100]:
            bases = bob.generate_bases(n)
            assert len(bases) == n
            assert len(bob.bases) == n

    def test_valid_bases(self) -> None:
        """Test 2: All Bob bases must be 'X' or 'Z'."""
        bob = Bob(seed=123)
        bases = bob.generate_bases(200)
        for b in bases:
            assert b in (COMPUTATIONAL_BASIS, HADAMARD_BASIS)

    def test_reproducibility(self) -> None:
        """Test 3: Two Bob instances with same seed produce identical basis sequences."""
        bob_1 = Bob(seed=42)
        bob_2 = Bob(seed=42)
        bases_1 = bob_1.generate_bases(50)
        bases_2 = bob_2.generate_bases(50)
        assert bases_1 == bases_2

    def test_different_seed_behavior(self) -> None:
        """Test 4: Different seeds normally produce different basis sequences."""
        bob_a = Bob(seed=101)
        bob_b = Bob(seed=202)
        bases_a = bob_a.generate_bases(100)
        bases_b = bob_b.generate_bases(100)
        assert bases_a != bases_b

    def test_invalid_num_signals(self) -> None:
        """Verify validation on invalid num_signals."""
        bob = Bob()
        with pytest.raises(ValueError, match="positive integer"):
            bob.generate_bases(0)
        with pytest.raises(ValueError, match="positive integer"):
            bob.generate_bases(-5)
        with pytest.raises(TypeError, match="integer"):
            bob.generate_bases("10")  # type: ignore


class TestBobMeasurements:
    """Test deterministic and probabilistic projective measurements by Bob."""

    def test_z_basis_deterministic_zero(self) -> None:
        """Test 5: Prepare |0> and measure in Z -> always 0."""
        bob = Bob(seed=42)
        qc = prepare_state_0()
        for _ in range(50):
            meas = bob.measure_signal(qc, basis=COMPUTATIONAL_BASIS)
            assert meas.result == 0
            assert meas.basis == COMPUTATIONAL_BASIS

    def test_z_basis_deterministic_one(self) -> None:
        """Test 6: Prepare |1> and measure in Z -> always 1."""
        bob = Bob(seed=42)
        qc = prepare_state_1()
        for _ in range(50):
            meas = bob.measure_signal(qc, basis=COMPUTATIONAL_BASIS)
            assert meas.result == 1
            assert meas.basis == COMPUTATIONAL_BASIS

    def test_x_basis_deterministic_zero(self) -> None:
        """Test 7: Prepare |+> and measure in X -> always 0."""
        bob = Bob(seed=42)
        qc = prepare_state_plus()
        for _ in range(50):
            meas = bob.measure_signal(qc, basis=HADAMARD_BASIS)
            assert meas.result == 0
            assert meas.basis == HADAMARD_BASIS

    def test_x_basis_deterministic_one(self) -> None:
        """Test 8: Prepare |-> and measure in X -> always 1."""
        bob = Bob(seed=42)
        qc = prepare_state_minus()
        for _ in range(50):
            meas = bob.measure_signal(qc, basis=HADAMARD_BASIS)
            assert meas.result == 1
            assert meas.basis == HADAMARD_BASIS

    def test_mismatched_basis_behavior(self) -> None:
        """Test 9: |+> and |-> measured in Z produce ~50% zeros and ~50% ones."""
        n_trials = 1000
        bob = Bob(seed=12345)

        # 1. |+> measured in Z
        qc_plus = prepare_state_plus()
        plus_signals = [qc_plus for _ in range(n_trials)]
        meas_plus = bob.receive_and_measure(
            plus_signals, bases=[COMPUTATIONAL_BASIS] * n_trials
        )
        results_plus = [m.result for m in meas_plus]
        p_ones_plus = sum(results_plus) / n_trials
        assert 0.45 <= p_ones_plus <= 0.55

        # 2. |-> measured in Z
        qc_minus = prepare_state_minus()
        minus_signals = [qc_minus for _ in range(n_trials)]
        meas_minus = bob.receive_and_measure(
            minus_signals, bases=[COMPUTATIONAL_BASIS] * n_trials
        )
        results_minus = [m.result for m in meas_minus]
        p_ones_minus = sum(results_minus) / n_trials
        assert 0.45 <= p_ones_minus <= 0.55


class TestQuantumChannel:
    """Test quantum channel preservation."""

    def test_quantum_channel_preservation(self) -> None:
        """Test 10: Ideal QuantumChannel transmits a signal without modifying its quantum state."""
        channel = QuantumChannel()
        circuits = [
            prepare_state_0(),
            prepare_state_1(),
            prepare_state_plus(),
            prepare_state_minus(),
        ]
        transmitted = channel.transmit(circuits)

        assert len(transmitted) == len(circuits)
        for orig, trans in zip(circuits, transmitted):
            sv_orig = get_statevector(orig)
            sv_trans = get_statevector(trans)
            assert statevectors_are_equivalent(sv_orig, sv_trans)
            # Ensure physical copy rather than identical object reference
            assert orig is not trans


class TestAliceChannelBobIntegration:
    """Test 11: End-to-end Alice -> Channel -> Bob transmission flow."""

    def test_end_to_end_transmission(self) -> None:
        """Verify complete pipeline transmission:

        - Alice generates N signals
        - Channel transmits N signals
        - Bob receives N signals
        - Bob generates N measurement bases
        - Bob produces N measurement results
        - Matching bases deterministically yield identical bits in ideal channel
        """
        n = 100
        alice = Alice(number_of_qubits=n, seed=42)
        channel = QuantumChannel()
        bob = Bob(seed=99)

        # 1. Alice prepares signals and extracts quantum circuits
        alice_signals = alice.signals
        quantum_circuits = alice.get_quantum_signals()
        assert len(quantum_circuits) == n

        # 2. Channel transmits signals
        transmitted_circuits = channel.transmit(quantum_circuits)
        assert len(transmitted_circuits) == n

        # 3. Bob receives and measures
        measurements = bob.receive_and_measure(transmitted_circuits)
        assert len(measurements) == n
        assert len(bob.bases) == n
        assert len(bob.results) == n

        # 4. Consistency check: For matching bases, Alice's bit == Bob's result
        matching_count = 0
        for i in range(n):
            alice_bit = alice.bits[i]
            alice_basis = alice.bases[i]
            bob_basis = bob.bases[i]
            bob_result = bob.results[i]

            assert measurements[i].index == i
            assert measurements[i].basis == bob_basis
            assert measurements[i].result == bob_result

            if alice_basis == bob_basis:
                matching_count += 1
                assert bob_result == alice_bit, (
                    f"Mismatch on matching basis at index {i}: "
                    f"Alice({alice_bit}, {alice_basis}) vs Bob({bob_result}, {bob_basis})"
                )

        # With 100 qubits, probability of matching bases is ~50%
        assert matching_count > 30

    def test_bob_measurement_validation(self) -> None:
        """Verify BobMeasurement dataclass validates its fields."""
        with pytest.raises(ValueError, match="non-negative integer"):
            BobMeasurement(index=-1, basis="Z", result=0)

        with pytest.raises(ValueError, match="Invalid basis"):
            BobMeasurement(index=0, basis="Y", result=0)

        with pytest.raises(ValueError, match="binary integer"):
            BobMeasurement(index=0, basis="Z", result=2)
