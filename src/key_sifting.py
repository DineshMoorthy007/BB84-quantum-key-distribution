"""Classical basis reconciliation and key sifting module for BB84.

This module implements the classical post-processing phase of the BB84 protocol:
1. Public basis comparison (basis reconciliation) between Alice and Bob.
2. Filtering transmitted bits to retain only indices where Alice and Bob selected identical bases.
3. Constructing Alice's and Bob's sifted keys.
4. Calculating sifting efficiency (sifting ratio).

Academic Note:
    During basis reconciliation, Alice and Bob exchange ONLY their basis choices
    ('Z' or 'X') over an authenticated public classical channel. Their raw bit values
    and measurement results are NEVER transmitted over the classical channel.
    Discarding mismatched bases is a direct consequence of quantum complementarity:
    measurements in conjugate bases yield completely uncorrelated, random outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Sequence, Tuple


VALID_BASES: tuple[str, str] = ("Z", "X")
VALID_BITS: tuple[int, int] = (0, 1)


@dataclass(frozen=True)
class SiftingResult:
    """Encapsulates the output of the BB84 basis reconciliation and key sifting process.

    Attributes:
        matching_indices: Sorted list of indices where Alice's and Bob's bases matched.
        discarded_indices: Sorted list of indices where Alice's and Bob's bases differed.
        alice_sifted_key: Alice's sifted key bits corresponding to matching indices.
        bob_sifted_key: Bob's sifted key bits corresponding to matching indices.
        total_signals: Total number of signals submitted for sifting.
        sifted_key_length: Number of surviving bits in the sifted key.
        sifting_ratio: Fraction of total signals retained (matching_positions / total_signals).
    """

    matching_indices: List[int]
    discarded_indices: List[int]
    alice_sifted_key: List[int]
    bob_sifted_key: List[int]
    total_signals: int
    sifted_key_length: int
    sifting_ratio: float


def validate_bit_value(bit: Any, name: str = "bit") -> int:
    """Validate a classical binary bit value.

    Args:
        bit: Value to check.
        name: Variable name for descriptive error messaging.

    Returns:
        Integer bit (0 or 1).

    Raises:
        TypeError: If bit is a boolean or not an integer.
        ValueError: If bit is not 0 or 1.
    """
    if isinstance(bit, bool) or not isinstance(bit, int):
        raise TypeError(f"{name} must be an integer, got {type(bit).__name__}: {bit!r}")
    if bit not in VALID_BITS:
        raise ValueError(f"Invalid {name} value: {bit}. Expected 0 or 1.")
    return bit


def validate_basis_value(basis: Any, name: str = "basis") -> str:
    """Validate a measurement basis string.

    Args:
        basis: Basis value to check.
        name: Variable name for descriptive error messaging.

    Returns:
        Normalized uppercase basis string ('Z' or 'X').

    Raises:
        TypeError: If basis is not a string.
        ValueError: If basis is not 'Z' or 'X'.
    """
    if not isinstance(basis, str):
        raise TypeError(f"{name} must be a string, got {type(basis).__name__}: {basis!r}")
    normalized = basis.strip().upper()
    if normalized not in VALID_BASES:
        raise ValueError(f"Invalid {name}: {basis!r}. Supported bases are 'Z' and 'X'.")
    return normalized


def reconcile_bases(
    alice_bases: Sequence[str],
    bob_bases: Sequence[str],
) -> Tuple[List[int], List[int]]:
    """Publicly compare Alice's and Bob's basis choices to identify matching positions.

    Args:
        alice_bases: Sequence of Alice's basis choices.
        bob_bases: Sequence of Bob's basis choices.

    Returns:
        A tuple of (matching_indices, discarded_indices).

    Raises:
        ValueError: If sequences have unequal lengths or are empty.
        TypeError: If elements are not valid basis strings.
    """
    if len(alice_bases) == 0:
        raise ValueError("Input basis sequences cannot be empty.")
    if len(alice_bases) != len(bob_bases):
        raise ValueError(
            f"Basis length mismatch: Alice has {len(alice_bases)} bases, Bob has {len(bob_bases)} bases."
        )

    norm_alice = [validate_basis_value(b, "alice_basis") for b in alice_bases]
    norm_bob = [validate_basis_value(b, "bob_basis") for b in bob_bases]

    matching_indices: List[int] = []
    discarded_indices: List[int] = []

    for idx, (a_basis, b_basis) in enumerate(zip(norm_alice, norm_bob)):
        if a_basis == b_basis:
            matching_indices.append(idx)
        else:
            discarded_indices.append(idx)

    return matching_indices, discarded_indices


def sift_keys(
    alice_bits: Sequence[int],
    alice_bases: Sequence[str],
    bob_bases: Sequence[str],
    bob_results: Sequence[int],
) -> SiftingResult:
    """Execute basis reconciliation and key sifting on classical signal records.

    Filters Alice's raw bits and Bob's measurement results, retaining only positions
    where their measurement bases coincided.

    Args:
        alice_bits: Alice's prepared classical bit sequence.
        alice_bases: Alice's encoding basis sequence.
        bob_bases: Bob's measurement basis sequence.
        bob_results: Bob's raw classical measurement outcomes.

    Returns:
        SiftingResult containing matching/discarded indices, sifted keys, and sifting ratio.

    Raises:
        ValueError: If sequences are empty, have mismatched lengths, or contain invalid values.
        TypeError: If elements have invalid data types.
    """
    n = len(alice_bits)
    if n == 0:
        raise ValueError("Input signal sequences cannot be empty.")

    if len(alice_bases) != n or len(bob_bases) != n or len(bob_results) != n:
        raise ValueError(
            f"Length mismatch among input sequences: "
            f"alice_bits={len(alice_bits)}, alice_bases={len(alice_bases)}, "
            f"bob_bases={len(bob_bases)}, bob_results={len(bob_results)}."
        )

    # Validate elements
    valid_alice_bits = [validate_bit_value(b, "alice_bit") for b in alice_bits]
    valid_bob_results = [validate_bit_value(r, "bob_result") for r in bob_results]

    matching_indices, discarded_indices = reconcile_bases(alice_bases, bob_bases)

    alice_sifted = [valid_alice_bits[i] for i in matching_indices]
    bob_sifted = [valid_bob_results[i] for i in matching_indices]

    sifted_len = len(matching_indices)
    ratio = sifted_len / n if n > 0 else 0.0

    return SiftingResult(
        matching_indices=matching_indices,
        discarded_indices=discarded_indices,
        alice_sifted_key=alice_sifted,
        bob_sifted_key=bob_sifted,
        total_signals=n,
        sifted_key_length=sifted_len,
        sifting_ratio=ratio,
    )


def sift_from_alice_and_bob(alice: Any, bob: Any) -> SiftingResult:
    """Convenience coordinator to sift keys from completed Alice and Bob instances.

    Extracts classical records generated during protocol execution and delegates
    to `sift_keys`.

    Args:
        alice: Instance of Alice containing `bits` and `bases`.
        bob: Instance of Bob containing `bases` and `results`.

    Returns:
        SiftingResult from the reconciled transmission.
    """
    return sift_keys(
        alice_bits=alice.bits,
        alice_bases=alice.bases,
        bob_bases=bob.bases,
        bob_results=bob.results,
    )
