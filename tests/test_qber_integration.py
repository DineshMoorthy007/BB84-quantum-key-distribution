"""Integration tests for the complete Alice -> Channel -> Bob -> Sifting -> QBER pipeline."""

import pytest

from src.alice import Alice
from src.bob import Bob
from src.error_injection import inject_classical_bit_errors
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel


class TestQBERIntegrationPipeline:
    """Integration test suite for the end-to-end QBER workflow."""

    def test_ideal_channel_zero_qber(self) -> None:
        """Verify that an ideal transmission pipeline yields strictly 0.0% QBER.

        Pipeline:
            Alice -> QuantumChannel -> Bob -> Sifting -> QBER
        """
        n_signals = 500
        alice = Alice(number_of_qubits=n_signals, seed=42)
        channel = QuantumChannel()
        bob = Bob(seed=99)

        # 1. Quantum transmission
        transmitted = channel.transmit(alice.get_quantum_signals())

        # 2. Bob measurement
        bob.receive_and_measure(transmitted)

        # 3. Basis reconciliation & Key sifting
        sifting_result = sift_from_alice_and_bob(alice, bob)

        assert sifting_result.total_signals == n_signals
        assert sifting_result.sifted_key_length > 0
        # Expected ~50% sifting ratio
        assert 0.40 <= sifting_result.sifting_ratio <= 0.60

        # 4. Sifted keys must match identically in ideal channel
        assert sifting_result.alice_sifted_key == sifting_result.bob_sifted_key

        # 5. QBER calculation
        qber_result = calculate_qber(
            sifting_result.alice_sifted_key,
            sifting_result.bob_sifted_key,
        )

        assert qber_result.compared_bits == sifting_result.sifted_key_length
        assert qber_result.error_count == 0
        assert qber_result.error_indices == []
        assert qber_result.matching_bits == sifting_result.sifted_key_length
        assert qber_result.qber == 0.0
        assert qber_result.qber_percentage == 0.0

    def test_qber_with_controlled_error_injection(self) -> None:
        """Verify that injecting classical bit errors into Bob's sifted key

        is accurately measured by calculate_qber.
        """
        n_signals = 2000
        alice = Alice(number_of_qubits=n_signals, seed=123)
        channel = QuantumChannel()
        bob = Bob(seed=456)

        transmitted = channel.transmit(alice.get_quantum_signals())
        bob.receive_and_measure(transmitted)
        sifting_result = sift_from_alice_and_bob(alice, bob)

        # Inject controlled 10% classical errors into a copy of Bob's sifted key
        target_error_rate = 0.10
        corrupted_bob_key = inject_classical_bit_errors(
            sifting_result.bob_sifted_key,
            error_rate=target_error_rate,
            seed=789,
        )

        qber_result = calculate_qber(
            sifting_result.alice_sifted_key,
            corrupted_bob_key,
        )

        # Measured QBER should be close to 0.10 within statistical bounds
        assert 0.08 <= qber_result.qber <= 0.12
        assert qber_result.error_count == len(qber_result.error_indices)
        assert qber_result.compared_bits == sifting_result.sifted_key_length
