"""End-to-end Classical Post-Processing Pipeline for the BB84 Protocol.

Coordinates the complete post-transmission stages of BB84:
1. Error Estimation: Random sampling of test bits to estimate channel QBER.
2. Security Decision: Abort if estimated QBER exceeds the security threshold.
3. Information Reconciliation: Interactive parity-based error correction.
4. Privacy Amplification: Toeplitz matrix compression to eliminate Eve's information.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, List, Optional, Sequence, Tuple
import numpy as np

from src.error_correction import ReconciliationResult, reconcile_keys
from src.error_estimation import ErrorEstimationResult, estimate_error_rate
from src.privacy_amplification import amplify_privacy, generate_toeplitz_matrix


def binary_entropy(p: float) -> float:
    """Calculate the binary Shannon entropy h2(p) = -p*log2(p) - (1-p)*log2(1-p).

    Args:
        p: Probability in [0.0, 1.0].

    Returns:
        Entropy value in [0.0, 1.0].
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


@dataclass(frozen=True)
class PostProcessingResult:
    """Encapsulates the complete results of the BB84 classical post-processing pipeline.

    Attributes:
        initial_sifted_length: Number of sifted bits arriving at post-processing.
        num_test_bits: Number of bits sacrificed during error estimation.
        num_test_errors: Number of bit discrepancies discovered during testing.
        estimated_qber: Unbiased QBER estimate derived from test bits.
        qber_threshold: Configured security cutoff threshold.
        is_accepted: True if estimated QBER <= qber_threshold, False otherwise.
        remaining_key_length: Key length after removing sacrificed test bits.
        num_corrected_bits: Errors corrected in Bob's key during reconciliation.
        reconciliation_leakage_bits: Public parity bits disclosed during reconciliation.
        reconciled_key_length: Length of the key after successful reconciliation.
        final_key_length: Length of the final amplified secret key (0 if aborted).
        final_alice_key: Final secret key held by Alice (None if aborted).
        final_bob_key: Final secret key held by Bob (None if aborted).
        keys_match: Boolean indicating whether Alice's and Bob's final keys are identical.
        reconciliation_matched: Boolean indicating whether reconciled keys matched prior to hash.
        rejection_reason: Descriptive message if aborted, None if accepted.
    """

    initial_sifted_length: int
    num_test_bits: int
    num_test_errors: int
    estimated_qber: float
    qber_threshold: float
    is_accepted: bool
    remaining_key_length: int
    num_corrected_bits: int
    reconciliation_leakage_bits: int
    reconciled_key_length: int
    final_key_length: int
    final_alice_key: Optional[List[int]]
    final_bob_key: Optional[List[int]]
    keys_match: bool
    reconciliation_matched: bool
    rejection_reason: Optional[str]


def run_post_processing_pipeline(
    alice_sifted_key: Sequence[int],
    bob_sifted_key: Sequence[int],
    sample_size: Optional[int] = None,
    sample_fraction: Optional[float] = 0.20,
    qber_threshold: float = 0.11,
    block_size: int = 16,
    reconciliation_passes: int = 4,
    final_key_length: Optional[int] = None,
    estimation_seed: Optional[int] = None,
    reconciliation_seed: Optional[int] = None,
    privacy_seed: Optional[int] = None,
) -> PostProcessingResult:
    """Execute the full classical post-processing pipeline for BB84.

    Pipeline Steps:
    1. Error Estimation: Samples a subset of sifted keys to estimate QBER.
    2. Threshold Check: If estimated QBER > qber_threshold, the run is rejected.
    3. Information Reconciliation: Corrects discrepancies in Bob's key.
    4. Privacy Amplification: Compresses both keys using identical Toeplitz hashing.

    Args:
        alice_sifted_key: Alice's sifted key sequence.
        bob_sifted_key: Bob's sifted key sequence.
        sample_size: Number of test bits to disclose.
        sample_fraction: Fraction of sifted key to test (default 0.20).
        qber_threshold: Security threshold (default 0.11, Shor-Preskill limit).
        block_size: Parity block size for reconciliation.
        reconciliation_passes: Number of reconciliation passes with permutation (default 4).
        final_key_length: Desired final secret key length (auto-calculated if None).
        estimation_seed: Random seed for test-bit sampling.
        reconciliation_seed: Random seed for error-correction permutations.
        privacy_seed: Random seed for the shared public Toeplitz matrix.

    Returns:
        PostProcessingResult documenting statistics and resulting secret keys.
    """
    initial_len = len(alice_sifted_key)

    # 1. Error Estimation
    estimation_res: ErrorEstimationResult = estimate_error_rate(
        alice_sifted_key=alice_sifted_key,
        bob_sifted_key=bob_sifted_key,
        sample_size=sample_size,
        sample_fraction=sample_fraction,
        seed=estimation_seed,
    )

    est_qber = estimation_res.estimated_qber
    rem_alice = estimation_res.remaining_alice_key
    rem_bob = estimation_res.remaining_bob_key
    rem_len = estimation_res.remaining_key_length

    # 2. Security / Acceptance Decision
    if est_qber > qber_threshold:
        reason = (
            f"Estimated QBER ({est_qber:.2%}) exceeds security threshold ({qber_threshold:.2%}). "
            "Eavesdropping or severe noise detected. Key generation aborted."
        )
        return PostProcessingResult(
            initial_sifted_length=initial_len,
            num_test_bits=estimation_res.num_test_bits,
            num_test_errors=estimation_res.num_test_errors,
            estimated_qber=est_qber,
            qber_threshold=qber_threshold,
            is_accepted=False,
            remaining_key_length=rem_len,
            num_corrected_bits=0,
            reconciliation_leakage_bits=0,
            reconciled_key_length=0,
            final_key_length=0,
            final_alice_key=None,
            final_bob_key=None,
            keys_match=False,
            reconciliation_matched=False,
            rejection_reason=reason,
        )

    # 3. Information Reconciliation
    recon_res: ReconciliationResult = reconcile_keys(
        alice_key=rem_alice,
        bob_key=rem_bob,
        block_size=block_size,
        num_passes=reconciliation_passes,
        seed=reconciliation_seed,
    )

    reconciled_alice = recon_res.corrected_alice_key
    reconciled_bob = recon_res.corrected_bob_key
    reconciled_len = len(reconciled_alice)
    recon_matched = recon_res.is_matching

    if not recon_matched:
        reason = (
            f"Information reconciliation could not resolve all errors ({recon_res.residual_error_count} residual errors). "
            "Key agreement failed; aborting."
        )
        return PostProcessingResult(
            initial_sifted_length=initial_len,
            num_test_bits=estimation_res.num_test_bits,
            num_test_errors=estimation_res.num_test_errors,
            estimated_qber=est_qber,
            qber_threshold=qber_threshold,
            is_accepted=False,
            remaining_key_length=rem_len,
            num_corrected_bits=recon_res.num_corrected_bits,
            reconciliation_leakage_bits=recon_res.reconciliation_leakage_bits,
            reconciled_key_length=reconciled_len,
            final_key_length=0,
            final_alice_key=None,
            final_bob_key=None,
            keys_match=False,
            reconciliation_matched=False,
            rejection_reason=reason,
        )

    # 4. Determine Target Final Secret Key Length
    if final_key_length is not None:
        target_m = final_key_length
    else:
        # Information-theoretic compression accounting for QBER and reconciliation leakage:
        # m ≈ n * (1 - 2*h2(QBER)) - leakage (asymptotic bound)
        h2 = binary_entropy(est_qber)
        theoretical_m = int(reconciled_len * (1.0 - 2.0 * h2) - recon_res.reconciliation_leakage_bits * 0.5)
        # Bounded educational target: at least 1 bit, at most 80% of reconciled length
        target_m = max(1, min(int(reconciled_len * 0.75), theoretical_m))

    if target_m > reconciled_len:
        target_m = reconciled_len

    # 5. Privacy Amplification (Toeplitz Hashing)
    # Alice and Bob generate the identical Toeplitz matrix from shared public seed
    shared_toeplitz = generate_toeplitz_matrix(m=target_m, n=reconciled_len, seed=privacy_seed)

    final_alice = amplify_privacy(reconciled_alice, final_key_length=target_m, matrix=shared_toeplitz)
    final_bob = amplify_privacy(reconciled_bob, final_key_length=target_m, matrix=shared_toeplitz)

    final_match = final_alice == final_bob

    return PostProcessingResult(
        initial_sifted_length=initial_len,
        num_test_bits=estimation_res.num_test_bits,
        num_test_errors=estimation_res.num_test_errors,
        estimated_qber=est_qber,
        qber_threshold=qber_threshold,
        is_accepted=True,
        remaining_key_length=rem_len,
        num_corrected_bits=recon_res.num_corrected_bits,
        reconciliation_leakage_bits=recon_res.reconciliation_leakage_bits,
        reconciled_key_length=reconciled_len,
        final_key_length=target_m,
        final_alice_key=final_alice,
        final_bob_key=final_bob,
        keys_match=final_match,
        reconciliation_matched=recon_matched,
        rejection_reason=None,
    )
