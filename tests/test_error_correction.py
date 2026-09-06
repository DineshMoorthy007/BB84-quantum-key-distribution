"""Unit tests for information reconciliation (error correction) module."""

from __future__ import annotations

import pytest

from src.error_correction import (
    ReconciliationResult,
    calculate_parity,
    compare_parities,
    locate_error_binary_search,
    reconcile_keys,
)


class TestErrorCorrection:
    """Test suite for parity-based reconciliation and binary search."""

    def test_parity_calculation(self):
        """Verify single-bit parity calculation: even -> 0, odd -> 1."""
        assert calculate_parity([0, 0, 0, 0]) == 0
        assert calculate_parity([1, 1, 0, 0]) == 0
        assert calculate_parity([1, 0, 0, 0]) == 1
        assert calculate_parity([1, 1, 1, 0]) == 1
        assert calculate_parity([1, 1, 1, 1]) == 0

    def test_compare_parities(self):
        """Verify parity comparison function."""
        assert compare_parities(0, 0) is True
        assert compare_parities(1, 1) is True
        assert compare_parities(0, 1) is False
        assert compare_parities(1, 0) is False

    def test_binary_search_localization_single_error(self):
        """Verify binary search accurately identifies the exact index of an error in a block."""
        block_len = 16
        alice_block = [0] * block_len
        # Error located at index 7
        target_error_idx = 7
        bob_block = [0] * block_len
        bob_block[target_error_idx] = 1

        identified_idx, leakage = locate_error_binary_search(
            alice_key=alice_block,
            bob_key=bob_block,
            start_idx=0,
            end_idx=block_len,
        )

        assert identified_idx == target_error_idx
        # For a block of 16, binary search takes log2(16) = 4 parity checks
        assert leakage == 4

    def test_identical_keys_unchanged(self):
        """Verify identical keys remain completely unchanged with 0 corrections."""
        alice_key = [1, 0, 1, 1, 0, 0, 1, 0] * 8
        bob_key = list(alice_key)

        res = reconcile_keys(alice_key, bob_key, block_size=16, num_passes=1)

        assert res.is_matching is True
        assert res.num_corrected_bits == 0
        assert res.corrected_bob_key == alice_key
        assert res.residual_error_count == 0
        assert res.residual_qber == 0.0
        assert res.reconciliation_leakage_bits > 0  # Block parities were verified

    def test_single_error_corrected(self):
        """Verify a single error in a key is correctly found and inverted in Bob's key."""
        alice_key = [0, 1, 1, 0, 1, 0, 0, 1] * 4  # 32 bits
        bob_key = list(alice_key)
        # Introduce single error at index 11
        bob_key[11] ^= 1

        res = reconcile_keys(alice_key, bob_key, block_size=16, num_passes=1)

        assert res.is_matching is True
        assert res.num_corrected_bits == 1
        assert res.corrected_bob_key == alice_key
        assert res.corrected_bob_key[11] == alice_key[11]

    def test_multiple_errors_in_distinct_blocks_corrected(self):
        """Verify multiple errors located in separate blocks are all successfully corrected."""
        # 4 blocks of size 16 = 64 bits
        alice_key = [0, 1] * 32
        bob_key = list(alice_key)
        # Error in block 0 (idx 5), block 1 (idx 20), block 3 (idx 55)
        bob_key[5] ^= 1
        bob_key[20] ^= 1
        bob_key[55] ^= 1

        res = reconcile_keys(alice_key, bob_key, block_size=16, num_passes=1)

        assert res.is_matching is True
        assert res.num_corrected_bits == 3
        assert res.corrected_bob_key == alice_key

    def test_multi_pass_shuffling_corrects_paired_errors(self):
        """Verify multi-pass reconciliation with shuffling resolves paired errors in the same block."""
        # 32 bits, block_size=16. Place TWO errors in block 0: indices 2 and 6.
        # Single pass would see matching parity (two bit flips cancel in modulo 2 parity).
        # Multi-pass with permutation disperses them so pass 2 catches them!
        alice_key = [0, 1] * 16
        bob_key = list(alice_key)
        bob_key[2] ^= 1
        bob_key[6] ^= 1

        # 1 pass fails on even errors in same block
        res_1pass = reconcile_keys(alice_key, bob_key, block_size=16, num_passes=1)
        assert res_1pass.is_matching is False

        # Multi-pass (2 passes) resolves them
        res_2pass = reconcile_keys(alice_key, bob_key, block_size=16, num_passes=3, seed=42)
        assert res_2pass.is_matching is True
        assert res_2pass.num_corrected_bits >= 2
        assert res_2pass.corrected_bob_key == alice_key

    def test_bob_key_not_simply_overwritten(self):
        """Verify Bob's key is genuinely modified through binary search bit-flips."""
        # If Bob has 1 error, exactly that 1 bit in Bob's list must be flipped
        alice_key = [0, 0, 0, 0, 0, 0, 0, 0]
        bob_key = [0, 0, 0, 1, 0, 0, 0, 0]

        res = reconcile_keys(alice_key, bob_key, block_size=8, num_passes=1)
        assert res.num_corrected_bits == 1
        assert res.corrected_bob_key[3] == 0

    def test_validation(self):
        """Verify parameter validation."""
        with pytest.raises(ValueError):
            reconcile_keys([0, 1], [0, 1, 0])
        with pytest.raises(ValueError):
            reconcile_keys([], [])
        with pytest.raises(ValueError):
            reconcile_keys([0, 1], [0, 1], block_size=0)
        with pytest.raises(ValueError):
            reconcile_keys([0, 1], [0, 1], num_passes=-1)
