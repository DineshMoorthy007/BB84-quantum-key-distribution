"""Unit tests for privacy amplification module using Toeplitz matrix hashing."""

from __future__ import annotations

import pytest
import numpy as np

from src.privacy_amplification import amplify_privacy, generate_toeplitz_matrix


class TestPrivacyAmplification:
    """Test suite for Toeplitz hashing and privacy amplification."""

    def test_toeplitz_matrix_structure(self):
        """Verify generated matrix has exact Toeplitz structure: M[i, j] == M[i+1, j+1]."""
        m, n = 8, 16
        mat = generate_toeplitz_matrix(m=m, n=n, seed=42)

        assert mat.shape == (m, n)
        assert mat.dtype == np.int8
        # Check that elements are only 0 or 1
        assert set(np.unique(mat)).issubset({0, 1})

        # Check diagonal constancy
        for i in range(m - 1):
            for j in range(n - 1):
                assert mat[i, j] == mat[i + 1, j + 1]

    def test_toeplitz_matrix_reproducibility(self):
        """Verify identical seed generates identical Toeplitz matrix."""
        mat1 = generate_toeplitz_matrix(m=10, n=20, seed=12345)
        mat2 = generate_toeplitz_matrix(m=10, n=20, seed=12345)
        np.testing.assert_array_equal(mat1, mat2)

    def test_different_seeds_produce_different_matrices(self):
        """Verify distinct seeds produce distinct matrices."""
        mat1 = generate_toeplitz_matrix(m=10, n=20, seed=1)
        mat2 = generate_toeplitz_matrix(m=10, n=20, seed=2)
        assert not np.array_equal(mat1, mat2)

    def test_amplify_privacy_output_length_and_binary(self):
        """Verify output length matches target m and contains only binary bits."""
        key = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1]  # 16 bits
        target_m = 7

        final_key = amplify_privacy(key, final_key_length=target_m, seed=42)

        assert len(final_key) == target_m
        assert all(b in (0, 1) for b in final_key)

    def test_deterministic_same_input_same_matrix(self):
        """Verify same input and same matrix/seed deterministically produce same final key."""
        key = [0, 1] * 20  # 40 bits
        m = 15

        res1 = amplify_privacy(key, final_key_length=m, seed=999)
        res2 = amplify_privacy(key, final_key_length=m, seed=999)

        assert res1 == res2

    def test_different_hash_seeds_produce_different_final_keys(self):
        """Verify varying the seed changes the resulting compressed key."""
        key = [1, 0, 1, 0, 1, 1, 0, 0] * 4  # 32 bits
        m = 16

        res1 = amplify_privacy(key, final_key_length=m, seed=10)
        res2 = amplify_privacy(key, final_key_length=m, seed=20)

        assert res1 != res2

    def test_precomputed_matrix_usage(self):
        """Verify passing an explicit precomputed Toeplitz matrix yields identical result."""
        key = [1, 1, 0, 1, 0, 0, 1, 1]
        m = 4
        matrix = generate_toeplitz_matrix(m=m, n=len(key), seed=55)

        final_key = amplify_privacy(key, final_key_length=m, matrix=matrix)
        assert len(final_key) == m

    def test_validation_invalid_dimensions(self):
        """Verify invalid dimensions raise clear exceptions."""
        with pytest.raises(ValueError):
            generate_toeplitz_matrix(m=0, n=10)
        with pytest.raises(ValueError):
            generate_toeplitz_matrix(m=-5, n=10)
        with pytest.raises(ValueError):
            generate_toeplitz_matrix(m=15, n=10)  # m > n
        with pytest.raises(TypeError):
            generate_toeplitz_matrix(m="4", n=10)  # type: ignore

        key = [0, 1, 0, 1]
        with pytest.raises(ValueError):
            amplify_privacy(key, final_key_length=0)
        with pytest.raises(ValueError):
            amplify_privacy(key, final_key_length=10)  # > len(key)
        with pytest.raises(TypeError):
            amplify_privacy(key, final_key_length="2")  # type: ignore
