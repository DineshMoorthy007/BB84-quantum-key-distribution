"""Unit tests for the controlled classical bit error injection module."""

import pytest

from src.error_injection import inject_classical_bit_errors


class TestErrorInjection:
    """Test suite for diagnostic classical bit-flip injection."""

    def test_original_key_immutability(self) -> None:
        """Requirement 1: Original input key is never modified."""
        original = [1, 0, 1, 1, 0, 0, 1]
        copy_original = list(original)

        modified = inject_classical_bit_errors(original, error_rate=0.5, seed=42)

        assert original == copy_original
        assert original is not modified

    def test_output_length_preservation(self) -> None:
        """Requirement 2: Output sequence length strictly matches input length."""
        for n in [0, 1, 15, 100]:
            key = [0, 1] * (n // 2) + ([0] if n % 2 else [])
            res = inject_classical_bit_errors(key, error_rate=0.2, seed=42)
            assert len(res) == n

    def test_output_contains_only_valid_bits(self) -> None:
        """Requirement 3: Output contains strictly binary integers (0 or 1)."""
        key = [0, 1, 0, 0, 1, 1] * 10
        res = inject_classical_bit_errors(key, error_rate=0.4, seed=123)
        for b in res:
            assert b in (0, 1)
            assert isinstance(b, int)
            assert not isinstance(b, bool)

    def test_invalid_error_rates_rejected(self) -> None:
        """Requirement 4: Error rates outside [0.0, 1.0] or non-numeric types raise errors."""
        key = [0, 1, 0, 1]
        with pytest.raises(ValueError, match="range"):
            inject_classical_bit_errors(key, error_rate=-0.01)

        with pytest.raises(ValueError, match="range"):
            inject_classical_bit_errors(key, error_rate=1.05)

        with pytest.raises(TypeError, match="float or int"):
            inject_classical_bit_errors(key, error_rate="0.1")  # type: ignore

        with pytest.raises(TypeError, match="float or int"):
            inject_classical_bit_errors(key, error_rate=True)  # type: ignore

    def test_reproducibility_with_seed(self) -> None:
        """Requirement 5: Same random seed produces identical error patterns."""
        key = [0, 1, 1, 0, 1, 0, 0, 1] * 20
        res_1 = inject_classical_bit_errors(key, error_rate=0.15, seed=777)
        res_2 = inject_classical_bit_errors(key, error_rate=0.15, seed=777)
        res_diff = inject_classical_bit_errors(key, error_rate=0.15, seed=888)

        assert res_1 == res_2
        assert res_1 != res_diff

    def test_statistical_convergence_on_large_samples(self) -> None:
        """Requirement 6: Large samples follow the requested error rate within tolerance."""
        sample_size = 10000
        target_rate = 0.10  # 10% error rate
        key = [0] * sample_size  # All zeros for straightforward counting

        flipped_key = inject_classical_bit_errors(key, error_rate=target_rate, seed=42)
        observed_errors = sum(flipped_key)
        observed_rate = observed_errors / sample_size

        # With 10,000 trials, std dev = sqrt(0.10 * 0.90 / 10000) = 0.003
        # 3-sigma tolerance: [0.091, 0.109]
        assert 0.085 <= observed_rate <= 0.115

    def test_zero_and_one_error_rates(self) -> None:
        """Verify boundary error rates: 0.0 flips no bits, 1.0 flips all bits."""
        key = [0, 1, 0, 1, 1, 0]

        res_zero = inject_classical_bit_errors(key, error_rate=0.0)
        assert res_zero == key

        res_full = inject_classical_bit_errors(key, error_rate=1.0)
        assert res_full == [1, 0, 1, 0, 0, 1]

    def test_invalid_key_elements_rejected(self) -> None:
        """Verify non-binary key elements are rejected."""
        with pytest.raises(ValueError, match="Invalid bit"):
            inject_classical_bit_errors([0, 2, 1], error_rate=0.1)

        with pytest.raises(TypeError, match="must be an integer"):
            inject_classical_bit_errors([0, True, 1], error_rate=0.1)
