"""Quantum Bit Error Rate (QBER) calculation and analysis module for BB84.

This module provides classical post-processing functions to evaluate error rates
strictly on sifted keys produced after basis reconciliation.

Definitions:
    QBER = (number of differing sifted bits) / (total number of compared sifted bits)

Academic Principle:
    QBER measures bit discrepancies between Alice's and Bob's sifted keys.
    It operates exclusively on positions where basis choices matched.
    Mismatched-basis events are filtered out during sifting and are NOT errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Sequence


VALID_BITS: tuple[int, int] = (0, 1)


@dataclass(frozen=True)
class QBERResult:
    """Encapsulates the measurement results of a sifted-key QBER evaluation.

    Attributes:
        alice_key_length: Number of bits in Alice's sifted key.
        bob_key_length: Number of bits in Bob's sifted key.
        compared_bits: Total number of aligned sifted bits compared.
        error_count: Number of bit positions where Alice and Bob disagreed.
        error_indices: Ascending list of 0-based indices with differing bits.
        qber: Quantum Bit Error Rate as a canonical float in [0.0, 1.0].
        matching_bits: Number of bit positions where Alice and Bob agreed.
    """

    alice_key_length: int
    bob_key_length: int
    compared_bits: int
    error_count: int
    error_indices: List[int]
    qber: float
    matching_bits: int

    @property
    def qber_percentage(self) -> float:
        """Return QBER expressed as a percentage in [0.0, 100.0]."""
        return self.qber * 100.0


@dataclass(frozen=True)
class QBERSecurityReport:
    """Higher-level security interpretation of an observed QBER measurement.

    Attributes:
        qber_result: The underlying QBER calculation.
        threshold: The reference error threshold (e.g., 0.11 for asymptotic Shor-Preskill).
        status: High-level classification ('LOW ERROR RATE' or 'HIGH ERROR RATE').
        interpretation: Descriptive assessment of the observed error rate.
        security_disclaimer: Explicit disclaimer clarifying that threshold comparison
            is experimental and not a formal cryptographic security proof.
    """

    qber_result: QBERResult
    threshold: float
    status: str
    interpretation: str
    security_disclaimer: str


def _validate_bit(bit: Any, index: int, party: str) -> int:
    """Validate that a key element is a binary integer (0 or 1)."""
    if isinstance(bit, bool) or not isinstance(bit, int):
        raise TypeError(
            f"{party} sifted key element at index {index} must be an integer, got {type(bit).__name__}: {bit!r}"
        )
    if bit not in VALID_BITS:
        raise ValueError(
            f"Invalid {party} sifted bit at index {index}: {bit}. Expected 0 or 1."
        )
    return bit


def calculate_qber(
    alice_sifted_key: Sequence[int],
    bob_sifted_key: Sequence[int],
) -> QBERResult:
    """Calculate the Quantum Bit Error Rate (QBER) between two sifted keys.

    Compares Alice's and Bob's sifted keys position-by-position, identifying
    differing bit positions and evaluating the canonical error rate.

    Args:
        alice_sifted_key: Alice's sifted key bits (sequence of 0s and 1s).
        bob_sifted_key: Bob's sifted key bits (sequence of 0s and 1s).

    Returns:
        QBERResult dataclass detailing error counts, indices, and the QBER value.

    Raises:
        ValueError: If either key is empty or if lengths differ.
        TypeError: If key elements are not valid binary integers.
    """
    n_alice = len(alice_sifted_key)
    n_bob = len(bob_sifted_key)

    if n_alice == 0 or n_bob == 0:
        raise ValueError("Cannot calculate QBER on empty sifted keys.")

    if n_alice != n_bob:
        raise ValueError(
            f"Key length mismatch: Alice has {n_alice} bits, Bob has {n_bob} bits."
        )

    # Validate elements and compare
    error_indices: List[int] = []
    matching_bits = 0

    for idx in range(n_alice):
        a_bit = _validate_bit(alice_sifted_key[idx], idx, "Alice")
        b_bit = _validate_bit(bob_sifted_key[idx], idx, "Bob")

        if a_bit != b_bit:
            error_indices.append(idx)
        else:
            matching_bits += 1

    error_count = len(error_indices)
    qber = error_count / n_alice

    return QBERResult(
        alice_key_length=n_alice,
        bob_key_length=n_bob,
        compared_bits=n_alice,
        error_count=error_count,
        error_indices=error_indices,
        qber=qber,
        matching_bits=matching_bits,
    )


def analyze_qber_security(
    qber_result: QBERResult,
    threshold: float = 0.11,
) -> QBERSecurityReport:
    """Provide a higher-level experimental security interpretation of observed QBER.

    Compares the observed QBER against an academic baseline threshold (defaulting to
    the classical 11% Shor-Preskill asymptotic bound for one-way post-processing).

    Args:
        qber_result: Evaluated QBERResult from sifted key comparison.
        threshold: Security threshold fraction (0.0 <= threshold <= 1.0). Default 0.11.

    Returns:
        QBERSecurityReport providing classification and educational context.

    Raises:
        ValueError: If threshold is outside [0.0, 1.0].
    """
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"threshold must be in range [0.0, 1.0], got {threshold}")

    if qber_result.qber <= threshold:
        status = "LOW ERROR RATE"
        interpretation = (
            f"Observed QBER ({qber_result.qber_percentage:.2f}%) is within the academic "
            f"threshold ({threshold * 100:.1f}%). Key reconciliation and privacy amplification "
            f"are theoretically feasible under standard one-way error correction bounds."
        )
    else:
        status = "HIGH ERROR RATE"
        interpretation = (
            f"Observed QBER ({qber_result.qber_percentage:.2f}%) exceeds the academic "
            f"threshold ({threshold * 100:.1f}%). In a physical QKD system, this error level "
            f"exceeds distillable secret-key capacity, indicating substantial noise or eavesdropping."
        )

    disclaimer = (
        "Academic Notice: This threshold assessment is an experimental comparison based "
        "on asymptotic security bounds (e.g., Shor-Preskill / CSS code bounds). It does "
        "NOT constitute a formal mathematical security proof against general attacks or "
        "finite-key effects."
    )

    return QBERSecurityReport(
        qber_result=qber_result,
        threshold=threshold,
        status=status,
        interpretation=interpretation,
        security_disclaimer=disclaimer,
    )
