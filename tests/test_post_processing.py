"""Unit tests for the end-to-end post-processing pipeline."""

from __future__ import annotations

import pytest

from src.post_processing import PostProcessingResult, run_post_processing_pipeline


class TestPostProcessingPipeline:
    """Test suite for complete classical post-processing workflow."""

    def test_ideal_noiseless_keys_pipeline(self):
        """Verify noiseless identical keys pass estimation, reconcile cleanly, and match after PA."""
        key_len = 100
        alice_key = [1, 0, 1, 1, 0, 0, 1, 0] * (key_len // 8) + [1, 0, 1, 0]
        bob_key = list(alice_key)

        res = run_post_processing_pipeline(
            alice_sifted_key=alice_key,
            bob_sifted_key=bob_key,
            sample_fraction=0.20,
            qber_threshold=0.11,
            block_size=16,
            final_key_length=40,
            estimation_seed=42,
            privacy_seed=99,
        )

        assert res.is_accepted is True
        assert res.estimated_qber == 0.0
        assert res.num_test_errors == 0
        assert res.num_corrected_bits == 0
        assert res.reconciliation_matched is True
        assert res.keys_match is True
        assert res.final_key_length == 40
        assert res.final_alice_key is not None
        assert res.final_bob_key is not None
        assert res.final_alice_key == res.final_bob_key
        assert len(res.final_alice_key) == 40

    def test_noisy_keys_reconciliation_and_privacy_amplification(self):
        """Verify noisy keys with small error rate are corrected and result in identical secret keys."""
        key_len = 160
        alice_key = [0, 1, 1, 0, 1, 0, 0, 1] * 20
        bob_key = list(alice_key)

        # Inject 3 errors into Bob's key
        bob_key[15] ^= 1
        bob_key[45] ^= 1
        bob_key[95] ^= 1

        res = run_post_processing_pipeline(
            alice_sifted_key=alice_key,
            bob_sifted_key=bob_key,
            sample_fraction=0.20,
            qber_threshold=0.11,
            block_size=16,
            final_key_length=50,
            estimation_seed=10,
            reconciliation_seed=20,
            privacy_seed=30,
        )

        assert res.is_accepted is True
        assert res.final_key_length == 50
        assert res.keys_match is True
        assert res.final_alice_key == res.final_bob_key

    def test_high_qber_causes_rejection(self):
        """Verify estimated QBER exceeding threshold aborts key generation."""
        key_len = 100
        alice_key = [0] * key_len
        # 25% errors (as under Eve intercept-resend)
        bob_key = [1 if i % 4 == 0 else 0 for i in range(key_len)]

        res = run_post_processing_pipeline(
            alice_sifted_key=alice_key,
            bob_sifted_key=bob_key,
            sample_fraction=0.20,
            qber_threshold=0.11,
            estimation_seed=42,
        )

        assert res.is_accepted is False
        assert res.estimated_qber > 0.11
        assert res.final_alice_key is None
        assert res.final_bob_key is None
        assert res.final_key_length == 0
        assert res.rejection_reason is not None
        assert "exceeds security threshold" in res.rejection_reason

    def test_final_key_is_shorter_than_reconciled_key(self):
        """Verify privacy amplification compresses key length (m < n)."""
        alice_key = [1, 0] * 80  # 160 bits
        bob_key = list(alice_key)

        res = run_post_processing_pipeline(
            alice_sifted_key=alice_key,
            bob_sifted_key=bob_key,
            sample_fraction=0.20,
            qber_threshold=0.11,
            estimation_seed=1,
            privacy_seed=2,
        )

        assert res.is_accepted is True
        assert res.final_key_length < res.reconciled_key_length
        assert res.keys_match is True

    def test_deterministic_seeds_reproducible(self):
        """Verify deterministic seeds produce identical post-processing results."""
        alice_key = [0, 1, 1, 0] * 25
        bob_key = list(alice_key)

        res1 = run_post_processing_pipeline(
            alice_sifted_key=alice_key,
            bob_sifted_key=bob_key,
            sample_fraction=0.20,
            qber_threshold=0.11,
            final_key_length=30,
            estimation_seed=123,
            privacy_seed=456,
        )
        res2 = run_post_processing_pipeline(
            alice_sifted_key=alice_key,
            bob_sifted_key=bob_key,
            sample_fraction=0.20,
            qber_threshold=0.11,
            final_key_length=30,
            estimation_seed=123,
            privacy_seed=456,
        )

        assert res1.final_alice_key == res2.final_alice_key
        assert res1.final_bob_key == res2.final_bob_key
        assert res1.estimated_qber == res2.estimated_qber
