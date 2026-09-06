"""Controlled classical bit error injection module for BB84 validation.

This module provides a testing utility to inject independent classical bit flips
into a binary key sequence at a specified error probability.

Academic & Architectural Notice:
    This is a purely CLASSICAL diagnostic tool intended solely for verifying
    the QBER calculation and testing statistical estimation routines.
    It is NOT a quantum noise model (such as Pauli-X or depolarizing channels)
    and does NOT operate on quantum state vectors or physical quantum channels.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence
import numpy as np


VALID_BITS: tuple[int, int] = (0, 1)


def inject_classical_bit_errors(
    key: Sequence[int],
    error_rate: float,
    seed: Optional[int] = None,
) -> List[int]:
    """Inject controlled classical bit flips into a copy of a binary key sequence.

    Each bit in the key is independently flipped (0 -> 1, 1 -> 0) with probability
    `error_rate`. The original input sequence is never mutated.

    Args:
        key: Input sequence of binary bits (0s and 1s).
        error_rate: Probability of bit flip per bit (0.0 <= error_rate <= 1.0).
        seed: Optional random seed for reproducible pseudo-random generation.

    Returns:
        A new list of integers with injected bit flips.

    Raises:
        ValueError: If error_rate is outside [0.0, 1.0] or if key elements are invalid.
        TypeError: If error_rate or key elements have invalid data types.
    """
    if isinstance(error_rate, bool) or not isinstance(error_rate, (int, float)):
        raise TypeError(f"error_rate must be a float or int, got {type(error_rate).__name__}")
    if not (0.0 <= error_rate <= 1.0):
        raise ValueError(f"error_rate must be in the range [0.0, 1.0], got {error_rate}")

    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

    # Validate elements without modifying original
    validated_key: List[int] = []
    for idx, bit in enumerate(key):
        if isinstance(bit, bool) or not isinstance(bit, int):
            raise TypeError(f"Key element at index {idx} must be an integer, got {type(bit).__name__}: {bit!r}")
        if bit not in VALID_BITS:
            raise ValueError(f"Invalid bit at index {idx}: {bit}. Expected 0 or 1.")
        validated_key.append(bit)

    if not validated_key:
        return []

    # If error_rate is exactly 0.0, return copy unchanged
    if error_rate == 0.0:
        return list(validated_key)

    rng = np.random.default_rng(seed)
    random_draws = rng.random(size=len(validated_key))

    modified_key: List[int] = []
    for bit, draw in zip(validated_key, random_draws):
        if draw < error_rate:
            # Flip bit: 0 -> 1, 1 -> 0
            modified_key.append(1 - bit)
        else:
            modified_key.append(bit)

    return modified_key
