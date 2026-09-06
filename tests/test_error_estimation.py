"""Unit tests for error estimation (parameter estimation) module."""

from __future__ import annotations

import pytest

from src.error_estimation import ErrorEstimationResult, estimate_error_rate


class TestErrorEstimation:
    """Test suite for error parameter estimation."""

    def test_identical_keys_zero_qber(self):
        """Verify identical keys yield 0.0% estimated QBER."""
        alice_key = [0, 1, 1, 0, 1, 0, 0, 1] * 10
        bob_key = list(alice_key)

        res = estimate_error_rate(alice_key, bob_key, sample_fraction=0.25, seed=42)

        assert res.estimated_qber == 0.0
        assert res.num_test_errors == 0
        assert res.num_test_bits == 20
        assert res.remaining_key_length == 60
        assert len(res.remaining_alice_key) == 60
        assert len(res.remaining_bob_key) == 60
        assert res.remaining_alice_key == res.remaining_bob_key

    def test_known_error_pattern(self):
        """Verify known discrepancies in sampled test bits yield exact expected QBER."""
        # 10 bits: Alice = all 0s, Bob has error at index 0 and index 2
        alice_key = [0] * 10
        bob_key = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0]

        # Use sample_size=4 with fixed seed
        res = estimate_error_rate(alice_key, bob_key, sample_size=4, seed=123)

        assert res.num_test_bits == 4
        # Verify calculation matches exact discrepancies at chosen positions
        expected_errors = sum(1 for p in res.test_positions if alice_key[p] != bob_key[p])
        assert res.num_test_errors == expected_errors
        assert res.estimated_qber == expected_errors / 4.0

    def test_disclosed_bits_removed_from_remaining_keys(self):
        """Verify disclosed test bits are strictly pruned from remaining keys."""
        alice_key = [1, 0, 1, 1, 0, 0, 1, 0]
        bob_key = [1, 0, 1, 1, 0, 0, 1, 0]

        res = estimate_error_rate(alice_key, bob_key, sample_size=3, seed=99)

        assert len(res.test_positions) == 3
        assert len(res.remaining_alice_key) == 5
        assert len(res.remaining_bob_key) == 5

        # Confirm no test position remained in key
        remaining_indices = [i for i in range(len(alice_key)) if i not in res.test_positions]
        expected_remaining = [alice_key[i] for i in remaining_indices]
        assert res.remaining_alice_key == expected_remaining

    def test_seed_reproducibility(self):
        """Verify identical seed yields identical test positions and estimates."""
        alice_key = [0, 1] * 50
        bob_key = [0, 1] * 50

        res1 = estimate_error_rate(alice_key, bob_key, sample_size=20, seed=777)
        res2 = estimate_error_rate(alice_key, bob_key, sample_size=20, seed=777)

        assert res1.test_positions == res2.test_positions
        assert res1.remaining_alice_key == res2.remaining_alice_key

    def test_different_seeds_differ(self):
        """Verify different seeds yield different sampled positions."""
        alice_key = [0, 1] * 50
        bob_key = [0, 1] * 50

        res1 = estimate_error_rate(alice_key, bob_key, sample_size=20, seed=1)
        res2 = estimate_error_rate(alice_key, bob_key, sample_size=20, seed=2)

        assert res1.test_positions != res2.test_positions

    def test_validation_non_binary_values(self):
        """Verify invalid key bit values are rejected."""
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 2], [0, 1, 0])
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0], [0, -1, 0])
        with pytest.raises(TypeError):
            estimate_error_rate(["0", "1"], ["0", "1"])  # type: ignore
        with pytest.raises(TypeError):
            estimate_error_rate([True, False], [False, True])  # type: ignore

    def test_validation_length_mismatch(self):
        """Verify key length mismatch raises ValueError."""
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0], [0, 1])

    def test_validation_empty_keys(self):
        """Verify empty keys raise ValueError."""
        with pytest.raises(ValueError):
            estimate_error_rate([], [])

    def test_validation_sample_size_and_fraction(self):
        """Verify invalid sample sizes and fractions raise appropriate errors."""
        # Mutually exclusive
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0, 1], [0, 1, 0, 1], sample_size=2, sample_fraction=0.5)

        # Sample size > length
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0, 1], [0, 1, 0, 1], sample_size=10)

        # Sample size <= 0
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0, 1], [0, 1, 0, 1], sample_size=0)
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0, 1], [0, 1, 0, 1], sample_size=-2)

        # Sample fraction out of (0, 1]
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0, 1], [0, 1, 0, 1], sample_fraction=0.0)
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0, 1], [0, 1, 0, 1], sample_fraction=1.5)
        with pytest.raises(ValueError):
            estimate_error_rate([0, 1, 0, 1], [0, 1, 0, 1], sample_fraction=-0.1)
