"""Integration tests for Eve intercept-resend attack in BB84 protocol.

Tests the full pipeline:
Alice -> QuantumChannel -> (Eve) -> Bob -> Basis Reconciliation -> Sifting -> QBER

Verifies:
1. No Eve (eavesdropping disabled) -> QBER is 0.0 (ideal channel).
2. Full intercept-resend (eve_probability = 1.0) -> QBER significantly > 0,
   statistically clustered around the theoretical 25% expectation.
3. Partial intercept-resend (eve_probability = 0.5) -> QBER intermediate (~12.5%).
4. Alice and Bob remain completely unaware of Eve's presence; their protocols
   run identically regardless of whether Eve is intercepting.
"""

from __future__ import annotations

import pytest

from src.alice import Alice
from src.bob import Bob
from src.eve import Eve
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel


class TestEveIntegration:
    """Integration test suite for intercept-resend eavesdropping pipeline."""

    def test_ideal_channel_without_eve_zero_qber(self):
        """Verify standard Alice -> Channel -> Bob without Eve yields 0% QBER."""
        alice = Alice(number_of_qubits=500, seed=42)
        bob = Bob(seed=43)
        channel = QuantumChannel()

        signals = alice.get_quantum_signals()
        received_circuits = channel.transmit(signals)
        bob.receive_and_measure(received_circuits)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        assert qber_result.error_count == 0
        assert qber_result.qber == 0.0

    def test_full_intercept_resend_qber_approaches_25_percent(self):
        """Verify full intercept-resend (p=1.0) causes QBER to approach theoretical 25%."""
        n_signals = 3000
        alice = Alice(number_of_qubits=n_signals, seed=101)
        bob = Bob(seed=102)
        eve = Eve(seed=103, interception_probability=1.0)
        channel = QuantumChannel()

        # Alice -> Channel (with Eve attached) -> Bob
        signals = alice.get_quantum_signals()
        received_circuits = channel.transmit(signals, eve=eve)
        bob.receive_and_measure(received_circuits)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        # Verify Eve intercepted 100% of signals
        assert eve.intercepted_count == n_signals

        # Sifted key length should be roughly 50% of signals
        assert 1300 <= sifted.sifted_key_length <= 1700

        # Theoretical QBER = 25%. Expected std err for N~1500 is sqrt(0.25*0.75/1500) ~ 1.1%
        # Tolerance of [20%, 30%] is over 4 sigma, highly robust.
        assert 0.20 <= qber_result.qber <= 0.30
        assert qber_result.error_count > 0

    def test_partial_intercept_resend_intermediate_qber(self):
        """Verify partial intercept-resend (p=0.5) yields intermediate QBER (~12.5%)."""
        n_signals = 3000
        alice = Alice(number_of_qubits=n_signals, seed=201)
        bob = Bob(seed=202)
        eve = Eve(seed=203, interception_probability=0.5)
        channel = QuantumChannel(eve=eve)

        signals = alice.get_quantum_signals()
        received_circuits = channel.transmit(signals)
        bob.receive_and_measure(received_circuits)

        sifted = sift_from_alice_and_bob(alice, bob)
        qber_result = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

        # Intercepted count should be around 50%
        intercepted_ratio = eve.intercepted_count / n_signals
        assert 0.45 <= intercepted_ratio <= 0.55

        # Theoretical QBER for p=0.5 is 0.5 * 25% = 12.5%
        # Tolerance [8%, 18%]
        assert 0.08 <= qber_result.qber <= 0.18

    def test_channel_attach_and_detach_eve(self):
        """Verify QuantumChannel dynamically supports attaching and detaching Eve."""
        channel = QuantumChannel()
        assert channel.eve is None

        eve = Eve(seed=301, interception_probability=1.0)
        channel.attach_eve(eve)
        assert channel.eve is eve

        # Transmit with Eve attached
        alice = Alice(number_of_qubits=100, seed=302)
        signals = alice.get_quantum_signals()
        received = channel.transmit(signals)
        assert len(received) == 100
        assert eve.intercepted_count == 100

        # Detach Eve
        channel.detach_eve()
        assert channel.eve is None
        alice2 = Alice(number_of_qubits=50, seed=303)
        signals2 = alice2.get_quantum_signals()
        received2 = channel.transmit(signals2)
        assert len(received2) == 50
