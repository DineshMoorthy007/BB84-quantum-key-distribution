"""Information reconciliation (error correction) module for BB84 post-processing.

In Quantum Key Distribution, the sifted keys held by Alice and Bob contain a small
number of discrepancies caused by channel noise or potential eavesdropping.
Information reconciliation is the classical interactive protocol where Alice and Bob
eliminate these discrepancies over the public authenticated classical channel.

Protocol Mechanism:
1. Block Parity Comparison:
   Alice and Bob partition their remaining keys into blocks of size `block_size`.
   For each block, Alice announces her block parity:
       P_A = sum(alice_block) mod 2
   Bob compares this with his block parity:
       P_B = sum(bob_block) mod 2
   Each announced block parity leaks 1 bit of public information.

2. Binary Search Error Localization:
   When P_A != P_B, an odd number of discrepancies exists in that block.
   Alice and Bob perform an interactive binary search (dichotomic search):
   - Alice discloses the parity of the left sub-block (+1 bit of leakage).
   - Bob computes the parity of his corresponding left sub-block.
   - If parities differ, the search recurses on the left half.
   - If parities match, the discrepancy lies in the right half, so the search recurses right.
   - When a sub-block of size 1 is reached, the erroneous position is uniquely identified.
   - Bob flips his corresponding bit: bob_key[err_pos] ^= 1.

3. Multi-Pass Permutation (Educational Cascade-Style):
   Because an even number of errors within the same block has matching parity (P_A == P_B),
   a single pass cannot detect even error pairs. By performing optional subsequent passes
   with deterministic pseudo-random shuffling, errors are redistributed into separate blocks,
   enabling thorough reconciliation.

Educational Limitations Notice:
   This module implements a simplified educational parity-based reconciliation protocol.
   It models public parity disclosure and leakage tracking. It is NOT a full production
   Cascade, Winnow, or LDPC implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple
import numpy as np

from src.error_estimation import _validate_binary_sequence


@dataclass(frozen=True)
class ReconciliationResult:
    """Encapsulates the outcome and statistics of information reconciliation.

    Attributes:
        corrected_alice_key: Alice's key after reconciliation (unchanged reference).
        corrected_bob_key: Bob's key after in-place parity-guided bit corrections.
        original_key_length: Number of bits subjected to reconciliation.
        block_size: Configured block size for parity partitioning.
        num_blocks: Total number of blocks processed per pass.
        num_passes: Number of reconciliation passes executed.
        num_parity_comparisons: Total block-level parity comparisons performed.
        num_corrected_bits: Total number of erroneous bits identified and flipped in Bob's key.
        reconciliation_leakage_bits: Total count of parity bits disclosed publicly over the classical channel.
        is_matching: Boolean indicating whether Alice's and Bob's keys match identically.
        residual_error_count: Number of remaining bit discrepancies (0 if matching).
        residual_qber: Residual error rate after reconciliation.
    """

    corrected_alice_key: List[int]
    corrected_bob_key: List[int]
    original_key_length: int
    block_size: int
    num_blocks: int
    num_passes: int
    num_parity_comparisons: int
    num_corrected_bits: int
    reconciliation_leakage_bits: int
    is_matching: bool
    residual_error_count: int
    residual_qber: float


def calculate_parity(bits: Sequence[int]) -> int:
    """Calculate the single-bit parity (sum modulo 2) of a binary sequence.

    Args:
        bits: Sequence of binary integers (0 or 1).

    Returns:
        0 if the sum of bits is even, 1 if odd.
    """
    return sum(bits) % 2


def compare_parities(parity_alice: int, parity_bob: int) -> bool:
    """Compare two single-bit parities.

    Args:
        parity_alice: Alice's calculated parity (0 or 1).
        parity_bob: Bob's calculated parity (0 or 1).

    Returns:
        True if parities are identical, False if they differ.
    """
    return parity_alice == parity_bob


def locate_error_binary_search(
    alice_key: Sequence[int],
    bob_key: Sequence[int],
    start_idx: int,
    end_idx: int,
) -> Tuple[int, int]:
    """Interactively locate a single error within a block using binary search.

    Conceptually models Alice disclosing the parity of sub-blocks over the
    public channel until an individual bit index is isolated.

    Args:
        alice_key: Alice's binary key sequence.
        bob_key: Bob's binary key sequence.
        start_idx: Starting index of the discordant block (inclusive).
        end_idx: Ending index of the discordant block (exclusive).

    Returns:
        Tuple of (identified_error_index, public_parity_bits_disclosed).
    """
    current_start = start_idx
    current_end = end_idx
    leakage = 0

    while (current_end - current_start) > 1:
        mid = current_start + (current_end - current_start) // 2

        # Alice computes and publicly announces the parity of the left sub-block
        left_parity_alice = calculate_parity(alice_key[current_start:mid])
        leakage += 1  # 1 bit of public classical disclosure

        # Bob computes the parity of his corresponding left sub-block
        left_parity_bob = calculate_parity(bob_key[current_start:mid])

        if left_parity_alice != left_parity_bob:
            # Discrepancy lies in the left half
            current_end = mid
        else:
            # Discrepancy lies in the right half
            current_start = mid

    # Now current_end - current_start == 1, exactly one bit index isolated
    return current_start, leakage


def correct_bit(key: List[int], index: int) -> None:
    """Invert (correct) the bit at the specified index in-place.

    Args:
        key: Mutable list of binary bits.
        index: Position to invert (0 -> 1, 1 -> 0).
    """
    key[index] ^= 1


def reconcile_keys(
    alice_key: Sequence[int],
    bob_key: Sequence[int],
    block_size: int = 16,
    num_passes: int = 2,
    seed: Optional[int] = None,
) -> ReconciliationResult:
    """Reconcile Alice's and Bob's keys using parity-based error correction.

    Operates by dividing keys into blocks, comparing parities over the public
    channel, localizing discrepancies via binary search, and directly inverting
    the erroneous bits in Bob's key.

    Bob's key is genuinely modified through the algorithmic binary search;
    Alice's key is never simply copied onto Bob's key.

    Args:
        alice_key: Alice's binary key sequence.
        bob_key: Bob's binary key sequence.
        block_size: Size of contiguous blocks for parity checks (must be >= 1).
        num_passes: Number of reconciliation passes (with shuffling for pass >= 2).
        seed: Optional random seed for reproducible multi-pass shuffling.

    Returns:
        ReconciliationResult with corrected keys, leakage statistics, and match status.

    Raises:
        TypeError: If inputs have invalid types.
        ValueError: If key lengths differ, keys are empty, or block_size is invalid.
    """
    alice_bits = _validate_binary_sequence(alice_key, "alice_key")
    bob_bits = _validate_binary_sequence(bob_key, "bob_key")

    if len(alice_bits) != len(bob_bits):
        raise ValueError(
            f"Key length mismatch: Alice has {len(alice_bits)} bits, Bob has {len(bob_bits)} bits."
        )

    n = len(alice_bits)
    if n == 0:
        raise ValueError("Cannot reconcile empty keys.")

    if isinstance(block_size, bool) or not isinstance(block_size, int) or block_size <= 0:
        raise ValueError(f"block_size must be a positive integer, got {block_size}")

    if isinstance(num_passes, bool) or not isinstance(num_passes, int) or num_passes <= 0:
        raise ValueError(f"num_passes must be a positive integer, got {num_passes}")

    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

    # Initialize Bob's working key copy (Alice's key is reference and immutable)
    working_bob = list(bob_bits)
    total_comparisons = 0
    total_corrections = 0
    total_leakage = 0

    rng = np.random.default_rng(seed)

    for pass_idx in range(num_passes):
        # In pass 0: process original key order.
        # In subsequent passes: apply shared pseudo-random permutation to disperse paired errors.
        if pass_idx == 0:
            perm = list(range(n))
            inv_perm = list(range(n))
        else:
            perm = list(rng.permutation(n))
            inv_perm = [0] * n
            for i, p in enumerate(perm):
                inv_perm[p] = i

        perm_alice = [alice_bits[p] for p in perm]
        perm_bob = [working_bob[p] for p in perm]

        # Divide into blocks
        current_block_size = max(1, min(n, block_size))

        num_blocks = (n + current_block_size - 1) // current_block_size

        for b_idx in range(num_blocks):
            start = b_idx * current_block_size
            end = min(n, start + current_block_size)

            alice_block = perm_alice[start:end]
            bob_block = perm_bob[start:end]

            # 1. Compare block parities
            parity_a = calculate_parity(alice_block)
            parity_b = calculate_parity(bob_block)
            total_comparisons += 1
            total_leakage += 1  # Alice publicly announces block parity

            # 2. If parities mismatch, localize and correct an error
            if not compare_parities(parity_a, parity_b):
                err_pos, bin_leakage = locate_error_binary_search(
                    alice_key=perm_alice,
                    bob_key=perm_bob,
                    start_idx=start,
                    end_idx=end,
                )
                total_leakage += bin_leakage
                correct_bit(perm_bob, err_pos)
                total_corrections += 1

        # Un-permute Bob's key back to original indexing
        working_bob = [perm_bob[inv_perm[i]] for i in range(n)]

        # Early exit if keys already match perfectly
        if working_bob == alice_bits:
            break

    # Calculate final matching statistics
    residual_errors = sum(1 for a, b in zip(alice_bits, working_bob) if a != b)
    residual_qber = residual_errors / n
    is_matching = residual_errors == 0

    return ReconciliationResult(
        corrected_alice_key=list(alice_bits),
        corrected_bob_key=working_bob,
        original_key_length=n,
        block_size=block_size,
        num_blocks=(n + block_size - 1) // block_size,
        num_passes=pass_idx + 1,
        num_parity_comparisons=total_comparisons,
        num_corrected_bits=total_corrections,
        reconciliation_leakage_bits=total_leakage,
        is_matching=is_matching,
        residual_error_count=residual_errors,
        residual_qber=residual_qber,
    )
