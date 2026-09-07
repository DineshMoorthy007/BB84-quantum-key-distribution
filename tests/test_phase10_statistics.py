"""Unit tests for Phase 10 statistical analysis and Wilson confidence intervals."""

import math
import pytest

from src.statistics import (
    DescriptiveStats,
    compute_descriptive_stats,
    wilson_score_interval,
)


class TestWilsonScoreInterval:
    """Tests for the Wilson score confidence interval calculation."""

    def test_zero_errors_boundary(self) -> None:
        """Test interval when zero errors are observed."""
        lower, upper = wilson_score_interval(errors=0, total_trials=100, confidence=0.95)
        assert lower == 0.0
        # Wilson interval with 0/100 should have a strictly positive upper bound
        assert 0.0 < upper < 0.05
        # Analytical check: with e=0, upper = z^2 / (n + z^2) where z≈1.96, so ~3.84/103.84 ≈ 0.037
        expected_upper = (1.959964**2) / (100.0 + 1.959964**2)
        assert math.isclose(upper, expected_upper, rel_tol=1e-3)

    def test_all_errors_boundary(self) -> None:
        """Test interval when 100% of tested bits are errors."""
        lower, upper = wilson_score_interval(errors=100, total_trials=100, confidence=0.95)
        assert upper == 1.0
        assert 0.95 < lower < 1.0

    def test_symmetric_case(self) -> None:
        """Test interval when error rate is 50%."""
        lower, upper = wilson_score_interval(errors=50, total_trials=100, confidence=0.95)
        # Should be symmetric around 0.5
        center = (lower + upper) / 2.0
        assert math.isclose(center, 0.5, abs_tol=1e-5)
        assert 0.40 < lower < 0.45
        assert 0.55 < upper < 0.60

    def test_zero_trials(self) -> None:
        """Test zero sample size returns (0.0, 0.0)."""
        lower, upper = wilson_score_interval(errors=0, total_trials=0, confidence=0.95)
        assert lower == 0.0
        assert upper == 0.0

    def test_confidence_levels(self) -> None:
        """Test that wider confidence levels produce wider intervals."""
        low_90, up_90 = wilson_score_interval(errors=10, total_trials=100, confidence=0.90)
        low_95, up_95 = wilson_score_interval(errors=10, total_trials=100, confidence=0.95)
        low_99, up_99 = wilson_score_interval(errors=10, total_trials=100, confidence=0.99)

        width_90 = up_90 - low_90
        width_95 = up_95 - low_95
        width_99 = up_99 - low_99

        assert width_90 < width_95 < width_99

    def test_invalid_parameters_raise_value_error(self) -> None:
        """Test parameter validation checks."""
        with pytest.raises(ValueError, match="total_trials must be non-negative"):
            wilson_score_interval(errors=0, total_trials=-1)

        with pytest.raises(ValueError, match="errors must be non-negative"):
            wilson_score_interval(errors=-1, total_trials=10)

        with pytest.raises(ValueError, match="errors .* cannot exceed total_trials"):
            wilson_score_interval(errors=15, total_trials=10)

        with pytest.raises(ValueError, match="confidence must be in"):
            wilson_score_interval(errors=5, total_trials=10, confidence=1.5)


class TestDescriptiveStats:
    """Tests for sample descriptive statistics computation."""

    def test_empty_sequence_raises_value_error(self) -> None:
        """Test that empty sequences raise ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate descriptive statistics for an empty sequence"):
            compute_descriptive_stats([])

    def test_single_element_sequence(self) -> None:
        """Test single element has zero variance and std."""
        stats = compute_descriptive_stats([42.0])
        assert stats.count == 1
        assert stats.mean == 42.0
        assert stats.std == 0.0
        assert stats.variance == 0.0
        assert stats.median == 42.0
        assert stats.min == 42.0
        assert stats.max == 42.0

    def test_known_numerical_values(self) -> None:
        """Test standard sequence with known sample statistics."""
        data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        stats = compute_descriptive_stats(data)

        assert stats.count == 8
        assert stats.mean == 5.0
        assert stats.median == 4.5
        assert stats.min == 2.0
        assert stats.max == 9.0
        # Sample variance for this sequence is 4.5714... and sample std is 2.138...
        assert math.isclose(stats.variance, 32.0 / 7.0, rel_tol=1e-5)
        assert math.isclose(stats.std, math.sqrt(32.0 / 7.0), rel_tol=1e-5)

    def test_to_dict_representation(self) -> None:
        """Test conversion to dictionary."""
        stats = compute_descriptive_stats([1.0, 2.0, 3.0])
        d = stats.to_dict()
        assert d["count"] == 3.0
        assert d["mean"] == 2.0
        assert "std" in d
        assert "variance" in d
        assert "median" in d
        assert "min" in d
        assert "max" in d
