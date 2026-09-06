"""Integration tests for Quantum Channel noise models in the BB84 protocol.

Tests full pipeline integrations:
1. Ideal channel without noise -> QBER is 0.0%.
2. Bit-flip noise (p=0.10) -> QBER increases significantly (~10%).
3. Phase-flip noise (p=0.20) -> Affects X-basis states, overall QBER ~ p/2 = 10%.
4. Depolarizing noise -> Increasing lambda leads to higher observed QBER.
5. Eve without noise -> Phase 7 behavior preserved (~25% QBER).
6. Eve + Noise composition -> Combined physical disturbances act in order
   (Alice -> Channel -> Eve -> Noise -> Bob), producing expected composite QBER.
"""

from __future__ import annotations

import pytest

from noise.bit_flip import BitFlipNoise
from noise.depolarizing import DepolarizingNoise
from noise.phase_flip import PhaseFlipNoise
from src.alice import Alice
from src.bob import Bob
from src.eve import Eve
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel


class TestNoiseIntegration:
    """Integration test suite for quantum noise channels in BB84 pipeline."""

    def test_ideal_channel_zero_qber(self):
        """Test 1: Ideal channel with no noise produces strictly 0% QBER."""
        n_signals = 600
        alice = Alice(number_of_qubits=n_signals, seed=42)
        bob = Bob(seed=43)
        channel = QuantumChannel(noise=None)

        transmitted = channel.transmit(alice.get_quantum_signals())
        bob.receive_and_measure(transmitted)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        assert qber_result.error_count == 0
        assert qber_result.qber == 0.0

    def test_bit_flip_noise_pipeline(self):
        """Test 2: Bit-flip noise with p=0.10 elevates QBER.

        In BB84, X flips bits in Z-basis but leaves X-basis eigenstates unchanged.
        Thus, overall sifted QBER is expected to be ~ p / 2 = 5.0%.
        """
        n_signals = 2500
        alice = Alice(number_of_qubits=n_signals, seed=10)
        bob = Bob(seed=11)
        noise = BitFlipNoise(probability=0.10, seed=12)
        channel = QuantumChannel(noise=noise)

        transmitted = channel.transmit(alice.get_quantum_signals())
        bob.receive_and_measure(transmitted)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        # Expected QBER for p=0.10 is ~ p/2 = 5% (tolerance [3%, 8%])
        assert 0.03 <= qber_result.qber <= 0.08
        assert qber_result.error_count > 0

    def test_phase_flip_noise_pipeline(self):
        """Test 3: Phase-flip noise with p=0.20 induces errors primarily in X-basis.

        Overall BB84 QBER is expected to be ~ p/2 = 10%.
        """
        n_signals = 2500
        alice = Alice(number_of_qubits=n_signals, seed=20)
        bob = Bob(seed=21)
        noise = PhaseFlipNoise(probability=0.20, seed=22)
        channel = QuantumChannel(noise=noise)

        transmitted = channel.transmit(alice.get_quantum_signals())
        bob.receive_and_measure(transmitted)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        # Theoretical QBER = 20% / 2 = 10% (tolerance [7%, 13%])
        assert 0.07 <= qber_result.qber <= 0.13

    def test_depolarizing_noise_scaling(self):
        """Test 4: Higher depolarization rates produce higher observed QBER."""
        n_signals = 1500

        # Low noise: lambda = 0.05 -> expected QBER = 2.5%
        alice1 = Alice(number_of_qubits=n_signals, seed=30)
        bob1 = Bob(seed=31)
        channel1 = QuantumChannel(noise=DepolarizingNoise(probability=0.05, seed=32))
        bob1.receive_and_measure(channel1.transmit(alice1.get_quantum_signals()))
        sifted1 = sift_from_alice_and_bob(alice1, bob1)
        qber1 = calculate_qber(sifted1.alice_sifted_key, sifted1.bob_sifted_key)

        # High noise: lambda = 0.30 -> expected QBER = 15.0%
        alice2 = Alice(number_of_qubits=n_signals, seed=30)
        bob2 = Bob(seed=31)
        channel2 = QuantumChannel(noise=DepolarizingNoise(probability=0.30, seed=33))
        bob2.receive_and_measure(channel2.transmit(alice2.get_quantum_signals()))
        sifted2 = sift_from_alice_and_bob(alice2, bob2)
        qber2 = calculate_qber(sifted2.alice_sifted_key, sifted2.bob_sifted_key)

        assert qber2.qber > qber1.qber
        assert 0.01 <= qber1.qber <= 0.05
        assert 0.10 <= qber2.qber <= 0.20

    def test_eve_without_noise_preserved(self):
        """Test 5: Eve without noise maintains Phase 7 ~25% QBER expectation."""
        n_signals = 2500
        alice = Alice(number_of_qubits=n_signals, seed=40)
        bob = Bob(seed=41)
        eve = Eve(seed=42, interception_probability=1.0)
        channel = QuantumChannel(eve=eve, noise=None)

        transmitted = channel.transmit(alice.get_quantum_signals())
        bob.receive_and_measure(transmitted)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        assert 0.20 <= qber_result.qber <= 0.30

    def test_eve_plus_noise_combined(self):
        """Test 6: Eve (p=1.0) + BitFlip noise (p=0.10) combined composition.

        Flow: Alice -> Channel -> Eve -> Noise -> Bob.
        Both physical phenomena contribute to errors.
        """
        n_signals = 2500
        alice = Alice(number_of_qubits=n_signals, seed=50)
        bob = Bob(seed=51)
        eve = Eve(seed=52, interception_probability=1.0)
        noise = BitFlipNoise(probability=0.10, seed=53)

        channel = QuantumChannel(eve=eve, noise=noise)
        transmitted = channel.transmit(alice.get_quantum_signals())
        bob.receive_and_measure(transmitted)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        # Eve alone introduces ~25% QBER. Added noise alters the error rate.
        # Combined QBER is expected around ~28-32%.
        assert qber_result.qber > 0.22
        assert qber_result.error_count > 0
