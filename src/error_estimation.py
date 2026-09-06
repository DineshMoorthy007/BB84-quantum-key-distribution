"""Error estimation (parameter estimation) module for BB84 classical post-processing.

In the BB84 protocol, Alice and Bob must estimate the Quantum Bit Error Rate (QBER)
introduced by quantum channel noise or potential eavesdropping without compromising
the security of the entire sifted key.

Protocol Principles:
1. Alice and Bob publicly disclose a small, randomly chosen subset of their sifted key positions.
2. They compare their bit values at these sample positions over the authenticated classical channel.
3. The fraction of mismatched sample bits yields an unbiased statistical estimate of the channel QBER.
4. IMPORTANT: All disclosed sample bits are permanently discarded from both keys to prevent
   information leakage to Eve.
5. The remaining undisturbed bits form the reconciled key candidate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple, Union
import numpy as np


@dataclass(frozen=True)
class ErrorEstimationResult:
    """Encapsulates the outcome of the error parameter estimation process.

    Attributes:
        estimated_qber: The fraction of mismatched test bits (0.0 to 1.0).
        estimated_qber_percentage: The estimated QBER expressed as a percentage (0.0% to 100.0%).
        test_positions: Sorted indices of the disclosed test bits.
        num_test_bits: Total count of disclosed test positions.
        num_test_errors: Number of bit discrepancies observed among test positions.
        remaining_alice_key: Alice's sifted key after removing all disclosed test positions.
        remaining_bob_key: Bob's sifted key after removing all disclosed test positions.
        remaining_key_length: Length of the remaining undisclosed key.
        initial_key_length: Original length of the sifted key prior to sampling.
    """

    estimated_qber: float
    estimated_qber_percentage: float
    test_positions: List[int]
    num_test_bits: int
    num_test_errors: int
    remaining_alice_key: List[int]
    remaining_bob_key: List[int]
    remaining_key_length: int
    initial_key_length: int


def _validate_binary_sequence(seq: Sequence[Any], name: str) -> List[int]:
    """Validate that a sequence contains only binary integers (0 or 1).

    Args:
        seq: Sequence to validate.
        name: Parameter name for informative error messages.

    Returns:
        List of integer bits.

    Raises:
        TypeError: If sequence elements are not valid integer types.
        ValueError: If sequence elements are not 0 or 1.
    """
    if not isinstance(seq, (list, tuple, np.ndarray)):
        raise TypeError(f"{name} must be a sequence, got {type(seq).__name__}")

    int_bits: List[int] = []
    for idx, bit in enumerate(seq):
        if isinstance(bit, bool) or not isinstance(bit, (int, np.integer)):
            raise TypeError(
                f"Element at index {idx} in {name} must be an integer, got {type(bit).__name__}"
            )
        if bit not in (0, 1):
            raise ValueError(
                f"Element at index {idx} in {name} must be 0 or 1, got {bit}"
            )
        int_bits.append(int(bit))
    return int_bits


def estimate_error_rate(
    alice_sifted_key: Sequence[int],
    bob_sifted_key: Sequence[int],
    sample_size: Optional[int] = None,
    sample_fraction: Optional[float] = None,
    seed: Optional[int] = None,
) -> ErrorEstimationResult:
    """Perform parameter estimation on sifted keys by publicly sampling a subset of positions.

    Randomly selects positions without replacement, compares bit values at these positions,
    computes estimated QBER, and permanently strips disclosed test positions from both keys.

    Args:
        alice_sifted_key: Alice's sifted key bits.
        bob_sifted_key: Bob's sifted key bits.
        sample_size: Exact count of bits to sample for testing (mutually exclusive with sample_fraction).
        sample_fraction: Fraction of sifted key to sample in (0.0, 1.0] (mutually exclusive with sample_size).
        seed: Optional integer random seed for reproducible sampling.

    Returns:
        ErrorEstimationResult containing estimation statistics and pruned remaining keys.

    Raises:
        TypeError: If inputs have invalid types.
        ValueError: If key lengths differ, keys are empty, or sampling parameters are invalid.
    """
    alice_bits = _validate_binary_sequence(alice_sifted_key, "alice_sifted_key")
    bob_bits = _validate_binary_sequence(bob_sifted_key, "bob_sifted_key")

    if len(alice_bits) != len(bob_bits):
        raise ValueError(
            f"Key length mismatch: Alice has {len(alice_bits)} bits, Bob has {len(bob_bits)} bits."
        )

    n = len(alice_bits)
    if n == 0:
        raise ValueError("Cannot perform error estimation on empty sifted keys.")

    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

    # Determine k = sample_size
    if sample_size is not None and sample_fraction is not None:
        raise ValueError("Specify either sample_size or sample_fraction, not both.")

    if sample_size is None and sample_fraction is None:
        # Default sampling: 20% of sifted key or at least 1 bit
        sample_fraction = 0.20

    if sample_fraction is not None:
        if isinstance(sample_fraction, bool) or not isinstance(sample_fraction, (int, float)):
            raise TypeError(
                f"sample_fraction must be a float, got {type(sample_fraction).__name__}"
            )
        if not (0.0 < float(sample_fraction) <= 1.0):
            raise ValueError(
                f"sample_fraction must be in (0.0, 1.0], got {sample_fraction}"
            )
        k = max(1, int(round(n * float(sample_fraction))))
    else:
        assert sample_size is not None
        if isinstance(sample_size, bool) or not isinstance(sample_size, int):
            raise TypeError(f"sample_size must be an integer, got {type(sample_size).__name__}")
        if sample_size <= 0:
            raise ValueError(f"sample_size must be a positive integer, got {sample_size}")
        if sample_size > n:
            raise ValueError(
                f"sample_size ({sample_size}) cannot exceed key length ({n})."
            )
        k = sample_size

    # Randomly select k positions without replacement using local RNG
    rng = np.random.default_rng(seed)
    chosen_positions = sorted(int(pos) for pos in rng.choice(n, size=k, replace=False))
    chosen_set = set(chosen_positions)

    # Compare disclosed test bits
    test_errors = 0
    for pos in chosen_positions:
        if alice_bits[pos] != bob_bits[pos]:
            test_errors += 1

    estimated_qber = float(test_errors / k) if k > 0 else 0.0

    # Prune disclosed positions from remaining keys
    remaining_alice = [alice_bits[i] for i in range(n) if i not in chosen_set]
    remaining_bob = [bob_bits[i] for i in range(n) if i not in chosen_set]

    return ErrorEstimationResult(
        estimated_qber=estimated_qber,
        estimated_qber_percentage=estimated_qber * 100.0,
        test_positions=chosen_positions,
        num_test_bits=k,
        num_test_errors=test_errors,
        remaining_alice_key=remaining_alice,
        remaining_bob_key=remaining_bob,
        remaining_key_length=len(remaining_alice),
        initial_key_length=n,
    )
