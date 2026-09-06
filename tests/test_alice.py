"""Unit tests for the Alice (Sender) module in BB84."""

import math
import pytest
from qiskit.quantum_info import Statevector

from src.alice import Alice, BB84Signal
from src.quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    get_statevector,
    statevectors_are_equivalent,
)

SQRT2_INV = 1.0 / math.sqrt(2.0)
EXPECTED_0 = Statevector([1.0 + 0.0j, 0.0 + 0.0j])
EXPECTED_1 = Statevector([0.0 + 0.0j, 1.0 + 0.0j])
EXPECTED_PLUS = Statevector([SQRT2_INV + 0.0j, SQRT2_INV + 0.0j])
EXPECTED_MINUS = Statevector([SQRT2_INV + 0.0j, -SQRT2_INV + 0.0j])


class TestAliceCore:
    """Test suite for Alice's classical bit and basis generation."""

    def test_number_of_generated_bits(self) -> None:
        """Test 1: For N requested signals, len(bits) == N."""
        for n in [1, 5, 20, 100]:
            alice = Alice(number_of_qubits=n, seed=42)
            bits = alice.generate_bits()
            assert len(bits) == n
            assert len(alice.bits) == n

    def test_valid_bit_values(self) -> None:
        """Test 2: Every generated bit must be either 0 or 1."""
        alice = Alice(number_of_qubits=200, seed=123)
        bits = alice.generate_bits()
        for bit in bits:
            assert bit in (0, 1)
            assert isinstance(bit, int)

    def test_number_of_bases(self) -> None:
        """Test 3: For N signals, len(bases) == N."""
        for n in [1, 10, 50]:
            alice = Alice(number_of_qubits=n, seed=42)
            bases = alice.generate_bases()
            assert len(bases) == n
            assert len(alice.bases) == n

    def test_valid_bases(self) -> None:
        """Test 4: Every basis must be 'Z' or 'X'."""
        alice = Alice(number_of_qubits=200, seed=999)
        bases = alice.generate_bases()
        for basis in bases:
            assert basis in (COMPUTATIONAL_BASIS, HADAMARD_BASIS)

    def test_reproducibility_same_seed(self) -> None:
        """Test 5: Two Alice instances with same seed produce identical bits and bases."""
        alice_1 = Alice(number_of_qubits=50, seed=42)
        alice_2 = Alice(number_of_qubits=50, seed=42)

        assert alice_1.bits == alice_2.bits
        assert alice_1.bases == alice_2.bases

    def test_different_seeds_produce_different_sequences(self) -> None:
        """Test 6: Different seeds produce distinct sequences."""
        alice_a = Alice(number_of_qubits=100, seed=101)
        alice_b = Alice(number_of_qubits=100, seed=202)

        # With 100 random bits and bases, identical sequence chance is 2^(-100)
        assert alice_a.bits != alice_b.bits or alice_a.bases != alice_b.bases

    def test_state_encoding_all_four_combinations(self) -> None:
        """Test 7: Verify all 4 bit/basis combinations map to expected quantum states."""
        alice = Alice(number_of_qubits=4)
        explicit_bits = [0, 1, 0, 1]
        explicit_bases = [
            COMPUTATIONAL_BASIS,
            COMPUTATIONAL_BASIS,
            HADAMARD_BASIS,
            HADAMARD_BASIS,
        ]
        signals = alice.encode(bits=explicit_bits, bases=explicit_bases)

        assert len(signals) == 4
        # (0, Z) -> |0>
        assert statevectors_are_equivalent(get_statevector(signals[0].circuit), EXPECTED_0)
        assert signals[0].state_symbol == "|0>"

        # (1, Z) -> |1>
        assert statevectors_are_equivalent(get_statevector(signals[1].circuit), EXPECTED_1)
        assert signals[1].state_symbol == "|1>"

        # (0, X) -> |+>
        assert statevectors_are_equivalent(get_statevector(signals[2].circuit), EXPECTED_PLUS)
        assert signals[2].state_symbol == "|+>"

        # (1, X) -> |->
        assert statevectors_are_equivalent(get_statevector(signals[3].circuit), EXPECTED_MINUS)
        assert signals[3].state_symbol == "|->"

    def test_number_of_quantum_signals(self) -> None:
        """Test 8: For N generated bits, N quantum signals must be produced."""
        for n in [1, 8, 25]:
            alice = Alice(number_of_qubits=n, seed=7)
            signals = alice.prepare_signals()
            assert len(signals) == n
            assert len(alice.signals) == n

    def test_classical_quantum_consistency(self) -> None:
        """Test 9: For every signal, signal[i].bit == bits[i], signal[i].basis == bases[i],

        and quantum state matches.
        """
        alice = Alice(number_of_qubits=30, seed=42)
        signals = alice.signals
        bits = alice.bits
        bases = alice.bases

        expected_map = {
            (0, COMPUTATIONAL_BASIS): EXPECTED_0,
            (1, COMPUTATIONAL_BASIS): EXPECTED_1,
            (0, HADAMARD_BASIS): EXPECTED_PLUS,
            (1, HADAMARD_BASIS): EXPECTED_MINUS,
        }

        for i, sig in enumerate(signals):
            assert sig.index == i
            assert sig.bit == bits[i]
            assert sig.basis == bases[i]
            expected_sv = expected_map[(sig.bit, sig.basis)]
            actual_sv = get_statevector(sig.circuit)
            assert statevectors_are_equivalent(actual_sv, expected_sv)

    def test_invalid_input_validation(self) -> None:
        """Test 10: Appropriate exceptions for invalid parameters."""
        with pytest.raises(ValueError, match="positive integer"):
            Alice(number_of_qubits=0)

        with pytest.raises(ValueError, match="positive integer"):
            Alice(number_of_qubits=-10)

        with pytest.raises(TypeError, match="integer"):
            Alice(number_of_qubits="10")  # type: ignore

        with pytest.raises(TypeError, match="integer"):
            Alice(number_of_qubits=True)  # type: ignore

        with pytest.raises(TypeError, match="seed must be an integer"):
            Alice(number_of_qubits=10, seed="seed42")  # type: ignore

    def test_quantum_signals_isolation(self) -> None:
        """Verify get_quantum_signals exports pure quantum circuits without leaking private data."""
        alice = Alice(number_of_qubits=5, seed=42)
        circuits = alice.get_quantum_signals()
        assert len(circuits) == 5
        for qc in circuits:
            assert qc.num_qubits == 1
            # Circuits should have no measurement or classical registers attached
            assert qc.num_clbits == 0

    def test_encode_length_mismatch_raises_error(self) -> None:
        """Verify encode() raises error on length mismatch."""
        alice = Alice(number_of_qubits=5)
        with pytest.raises(ValueError, match="Length mismatch"):
            alice.encode(bits=[0, 1], bases=["Z", "Z", "X"])
