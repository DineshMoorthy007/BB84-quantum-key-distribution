"""Unit and integration tests for BB84 basis reconciliation and key sifting."""

import pytest

from src.alice import Alice
from src.bob import Bob
from src.key_sifting import (
    SiftingResult,
    reconcile_bases,
    sift_from_alice_and_bob,
    sift_keys,
)
from src.quantum_channel import QuantumChannel


class TestBasisReconciliationAndSifting:
    """Test suite for classical post-processing in BB84."""

    def test_all_bases_match(self) -> None:
        """Test 1: When all bases match, all positions are retained."""
        alice_bits = [0, 1, 0, 1]
        alice_bases = ["Z", "Z", "Z", "Z"]
        bob_bases = ["Z", "Z", "Z", "Z"]
        bob_results = [0, 1, 0, 1]

        result = sift_keys(alice_bits, alice_bases, bob_bases, bob_results)

        assert result.total_signals == 4
        assert result.matching_indices == [0, 1, 2, 3]
        assert result.discarded_indices == []
        assert result.alice_sifted_key == [0, 1, 0, 1]
        assert result.bob_sifted_key == [0, 1, 0, 1]
        assert result.sifted_key_length == 4
        assert result.sifting_ratio == 1.0

    def test_no_bases_match(self) -> None:
        """Test 2: When no bases match, no positions are retained."""
        alice_bits = [1, 0, 1, 0]
        alice_bases = ["Z", "Z", "Z", "Z"]
        bob_bases = ["X", "X", "X", "X"]
        bob_results = [0, 1, 0, 1]

        result = sift_keys(alice_bits, alice_bases, bob_bases, bob_results)

        assert result.total_signals == 4
        assert result.matching_indices == []
        assert result.discarded_indices == [0, 1, 2, 3]
        assert result.alice_sifted_key == []
        assert result.bob_sifted_key == []
        assert result.sifted_key_length == 0
        assert result.sifting_ratio == 0.0

    def test_partial_matching(self) -> None:
        """Test 3: Mixture of matching and mismatching bases."""
        alice_bases = ["X", "Z", "X", "X", "Z", "Z", "X", "Z"]
        bob_bases = ["Z", "Z", "X", "X", "X", "Z", "Z", "Z"]

        matching, discarded = reconcile_bases(alice_bases, bob_bases)

        assert matching == [1, 2, 3, 5, 7]
        assert discarded == [0, 4, 6]

    def test_sifted_key_correctness(self) -> None:
        """Test 4: Verify only matching positions are included in the sifted keys."""
        alice_bits = [1, 0, 1, 1, 0, 0, 1, 0]
        alice_bases = ["X", "Z", "X", "X", "Z", "Z", "X", "Z"]
        bob_bases = ["Z", "Z", "X", "X", "X", "Z", "Z", "Z"]
        bob_results = [0, 0, 1, 1, 1, 0, 0, 0]

        result = sift_keys(alice_bits, alice_bases, bob_bases, bob_results)

        # Matching indices: 1, 2, 3, 5, 7
        assert result.matching_indices == [1, 2, 3, 5, 7]
        assert result.alice_sifted_key == [0, 1, 1, 0, 0]
        assert result.bob_sifted_key == [0, 1, 1, 0, 0]
        assert result.sifted_key_length == 5

    def test_ordering_preserved(self) -> None:
        """Test 5: Retained bits remain in their original chronological order."""
        alice_bits = [1, 0, 1, 0, 1, 0, 1]
        alice_bases = ["Z", "X", "Z", "X", "Z", "X", "Z"]
        bob_bases = ["X", "X", "X", "X", "Z", "Z", "Z"]
        bob_results = [0, 0, 1, 0, 1, 1, 1]

        # Matching indices: 1 (X==X), 3 (X==X), 4 (Z==Z), 6 (Z==Z)
        result = sift_keys(alice_bits, alice_bases, bob_bases, bob_results)

        assert result.matching_indices == [1, 3, 4, 6]
        assert result.alice_sifted_key == [
            alice_bits[1],
            alice_bits[3],
            alice_bits[4],
            alice_bits[6],
        ]
        assert result.bob_sifted_key == [
            bob_results[1],
            bob_results[3],
            bob_results[4],
            bob_results[6],
        ]

    def test_sifting_ratio(self) -> None:
        """Test 6: Sifting ratio = matching positions / total positions."""
        alice_bits = [0] * 10
        alice_bases = ["Z"] * 6 + ["X"] * 4
        bob_bases = ["Z"] * 6 + ["Z"] * 4  # Matches on first 6
        bob_results = [0] * 10

        result = sift_keys(alice_bits, alice_bases, bob_bases, bob_results)

        assert result.total_signals == 10
        assert result.sifted_key_length == 6
        assert result.sifting_ratio == 0.6

    def test_length_validation(self) -> None:
        """Test 7: Mismatched input lengths raise ValueError."""
        with pytest.raises(ValueError, match="Length mismatch"):
            sift_keys([0, 1], ["Z", "Z", "Z"], ["Z", "Z"], [0, 1])

        with pytest.raises(ValueError, match="Length mismatch"):
            sift_keys([0, 1], ["Z", "Z"], ["Z", "Z", "X"], [0, 1])

        with pytest.raises(ValueError, match="Length mismatch"):
            sift_keys([0, 1], ["Z", "Z"], ["Z", "Z"], [0])

    def test_invalid_bit_validation(self) -> None:
        """Test 8: Invalid bit values raise ValueError or TypeError."""
        with pytest.raises(ValueError, match="Invalid alice_bit"):
            sift_keys([2, 0], ["Z", "Z"], ["Z", "Z"], [0, 0])

        with pytest.raises(TypeError, match="must be an integer"):
            sift_keys([True, 0], ["Z", "Z"], ["Z", "Z"], [0, 0])

        with pytest.raises(TypeError, match="must be an integer"):
            sift_keys(["0", 0], ["Z", "Z"], ["Z", "Z"], [0, 0])

    def test_invalid_basis_validation(self) -> None:
        """Test 9: Invalid basis values raise ValueError or TypeError."""
        with pytest.raises(ValueError, match="Invalid alice_basis"):
            sift_keys([0, 1], ["Y", "Z"], ["Z", "Z"], [0, 1])

        with pytest.raises(ValueError, match="Invalid bob_basis"):
            sift_keys([0, 1], ["Z", "Z"], ["Z", "H"], [0, 1])

        with pytest.raises(TypeError, match="must be a string"):
            sift_keys([0, 1], [1, "Z"], ["Z", "Z"], [0, 1])

    def test_bob_result_validation(self) -> None:
        """Test 10: Invalid Bob measurement results raise ValueError or TypeError."""
        with pytest.raises(ValueError, match="Invalid bob_result"):
            sift_keys([0, 1], ["Z", "Z"], ["Z", "Z"], [0, -1])

        with pytest.raises(TypeError, match="must be an integer"):
            sift_keys([0, 1], ["Z", "Z"], ["Z", "Z"], [0, False])

    def test_identical_sifted_keys_in_ideal_case(self) -> None:
        """Test 11: End-to-end Alice -> Channel -> Bob in ideal conditions yields

        100% identical sifted keys on matching basis positions.
        """
        alice = Alice(number_of_qubits=100, seed=42)
        channel = QuantumChannel()
        bob = Bob(seed=99)

        transmitted = channel.transmit(alice.get_quantum_signals())
        bob.receive_and_measure(transmitted)

        result = sift_from_alice_and_bob(alice, bob)

        assert result.total_signals == 100
        assert result.sifted_key_length > 0
        # In ideal channel, Alice's sifted key and Bob's sifted key are IDENTICAL
        assert result.alice_sifted_key == result.bob_sifted_key
        # Check agreement for every matched position
        for idx, (a_k, b_k) in enumerate(
            zip(result.alice_sifted_key, result.bob_sifted_key)
        ):
            assert a_k == b_k

    def test_empty_input_handling(self) -> None:
        """Test 12: Empty input sequences raise a clear ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            sift_keys([], [], [], [])

        with pytest.raises(ValueError, match="cannot be empty"):
            reconcile_bases([], [])
