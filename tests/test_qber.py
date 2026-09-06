"""Unit tests for the QBER calculation and analysis module."""

import pytest

from src.qber import QBERResult, analyze_qber_security, calculate_qber


class TestQBERCalculation:
    """Test suite for QBER calculation on sifted keys."""

    def test_identical_keys(self) -> None:
        """Test 1: Identical keys produce zero errors and 0.0 QBER."""
        alice = [1, 0, 1, 0, 1, 0]
        bob = [1, 0, 1, 0, 1, 0]

        res = calculate_qber(alice, bob)

        assert res.compared_bits == 6
        assert res.error_count == 0
        assert res.error_indices == []
        assert res.matching_bits == 6
        assert res.qber == 0.0
        assert res.qber_percentage == 0.0

    def test_one_error(self) -> None:
        """Test 2: Single differing bit produces error_count=1, qber=1/6."""
        alice = [1, 0, 1, 0, 1, 0]
        bob = [1, 0, 1, 1, 1, 0]  # Disagrees at index 3

        res = calculate_qber(alice, bob)

        assert res.compared_bits == 6
        assert res.error_count == 1
        assert res.error_indices == [3]
        assert res.matching_bits == 5
        assert pytest.approx(res.qber, rel=1e-6) == 1.0 / 6.0
        assert pytest.approx(res.qber_percentage, rel=1e-6) == (1.0 / 6.0) * 100.0

    def test_multiple_errors(self) -> None:
        """Test 3: Multiple known error positions."""
        alice = [1, 0, 1, 1, 0]
        bob = [1, 0, 0, 1, 1]  # Differ at indices 2 and 4

        res = calculate_qber(alice, bob)

        assert res.compared_bits == 5
        assert res.error_count == 2
        assert res.error_indices == [2, 4]
        assert res.matching_bits == 3
        assert pytest.approx(res.qber) == 0.4
        assert pytest.approx(res.qber_percentage) == 40.0

    def test_all_bits_different(self) -> None:
        """Test 4: Completely inverted keys produce 100% QBER."""
        alice = [0, 0, 0, 0]
        bob = [1, 1, 1, 1]

        res = calculate_qber(alice, bob)

        assert res.compared_bits == 4
        assert res.error_count == 4
        assert res.error_indices == [0, 1, 2, 3]
        assert res.matching_bits == 0
        assert res.qber == 1.0
        assert res.qber_percentage == 100.0

    def test_empty_key_handling(self) -> None:
        """Test 5: Empty input keys raise ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate QBER on empty sifted keys"):
            calculate_qber([], [])

        with pytest.raises(ValueError, match="Cannot calculate QBER on empty sifted keys"):
            calculate_qber([1, 0], [])

    def test_different_key_lengths(self) -> None:
        """Test 6: Unequal key lengths raise ValueError."""
        with pytest.raises(ValueError, match="Key length mismatch"):
            calculate_qber([1, 0, 1, 0, 1], [1, 0, 1])

        with pytest.raises(ValueError, match="Key length mismatch"):
            calculate_qber([0], [0, 1])

    def test_invalid_values(self) -> None:
        """Test 7: Reject values other than binary 0 and 1."""
        with pytest.raises(ValueError, match="Invalid Alice sifted bit"):
            calculate_qber([2, 0], [0, 0])

        with pytest.raises(ValueError, match="Invalid Bob sifted bit"):
            calculate_qber([1, 0], [1, -1])

        with pytest.raises(TypeError, match="must be an integer"):
            calculate_qber([True, 0], [1, 0])

        with pytest.raises(TypeError, match="must be an integer"):
            calculate_qber([1, 0], ["1", 0])

    def test_error_index_ordering(self) -> None:
        """Test 8: Error indices are strictly returned in ascending order."""
        alice = [1, 0, 1, 0, 1, 0, 1, 0]
        bob = [0, 0, 0, 0, 0, 0, 0, 0]  # Differ at odd positions: 0, 2, 4, 6

        res = calculate_qber(alice, bob)

        assert res.error_indices == [0, 2, 4, 6]
        assert res.error_indices == sorted(res.error_indices)

    def test_qber_percentage(self) -> None:
        """Test 9: Verify percentage conversion accuracy."""
        res = QBERResult(
            alice_key_length=8,
            bob_key_length=8,
            compared_bits=8,
            error_count=1,
            error_indices=[2],
            qber=0.125,
            matching_bits=7,
        )
        assert pytest.approx(res.qber_percentage) == 12.50

    def test_security_report_threshold(self) -> None:
        """Test 10: Security report evaluates low and high error rates."""
        low_qber_res = QBERResult(100, 100, 100, 3, [1, 2, 3], 0.03, 97)
        report_low = analyze_qber_security(low_qber_res, threshold=0.11)
        assert report_low.status == "LOW ERROR RATE"
        assert "within the academic threshold" in report_low.interpretation
        assert "NOT constitute a formal mathematical security proof" in report_low.security_disclaimer

        high_qber_res = QBERResult(100, 100, 100, 25, list(range(25)), 0.25, 75)
        report_high = analyze_qber_security(high_qber_res, threshold=0.11)
        assert report_high.status == "HIGH ERROR RATE"
        assert "exceeds the academic threshold" in report_high.interpretation
