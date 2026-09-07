"""Privacy amplification module using Toeplitz matrix hashing for BB84.

In Quantum Key Distribution, even after basis reconciliation and information reconciliation,
an eavesdropper (Eve) may possess partial information about the shared key resulting from:
1. Partial intercepts or coherent probe measurements.
2. Classical parity information leaked over the public channel during information reconciliation.

Privacy Amplification Mechanism:
Privacy amplification applies a random hash function chosen from a 2-Universal hash family
to compress the n-bit reconciled key into a shorter m-bit final key (where m < n).
By the Leftover Hash Lemma (Impagliazzo et al., 1989; Bennett et al., 1995), if the compression
ratio accounts for Eve's maximum Renyi information and public leakage:
    m <= n * (1 - h2(QBER)) - leakage - s
the resulting m-bit secret key is statistically indistinguishable from a purely uniform random
distribution, reducing Eve's mutual information to an exponentially small security parameter 2^(-s).

Toeplitz Hashing:
A Toeplitz matrix M in {0, 1}^(m x n) is defined by constant values along each descending diagonal:
    M[i, j] = t_{i - j}
It requires only (m + n - 1) random bits to specify.
The hash multiplication is computed strictly under GF(2) (binary arithmetic modulo 2):
    y = (M * x) mod 2
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence
import numpy as np

from src.error_estimation import _validate_binary_sequence


def generate_toeplitz_matrix(
    m: int,
    n: int,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Generate a random binary Toeplitz matrix of dimensions m x n.

    A Toeplitz matrix satisfies M[i, j] = t_{i - j}.
    It is uniquely characterized by its first row (n elements) and first column (m elements),
    sharing the top-left element M[0, 0], requiring m + n - 1 random bits.

    Args:
        m: Number of rows (desired final hash key length). Must be >= 1.
        n: Number of columns (input reconciled key length). Must be >= m.
        seed: Optional random seed for reproducible public matrix generation.

    Returns:
        2D numpy array of shape (m, n) with dtype np.int8 containing 0s and 1s.

    Raises:
        TypeError: If m or n is not an integer.
        ValueError: If m <= 0, n <= 0, or m > n.
    """
    if isinstance(m, bool) or not isinstance(m, (int, np.integer)):
        raise TypeError(f"Row dimension m must be an integer, got {type(m).__name__}")
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)):
        raise TypeError(f"Column dimension n must be an integer, got {type(n).__name__}")

    m_int = int(m)
    n_int = int(n)

    if m_int <= 0:
        raise ValueError(f"Target key length m must be positive, got {m_int}")
    if n_int <= 0:
        raise ValueError(f"Input key length n must be positive, got {n_int}")
    if m_int > n_int:
        raise ValueError(
            f"Target length m ({m_int}) cannot exceed input length n ({n_int})."
        )

    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise TypeError(f"seed must be an integer or None, got {type(seed).__name__}")

    rng = np.random.default_rng(seed)

    # We need m + n - 1 random binary bits:
    # First row: elements M[0, 0] ... M[0, n-1] (n bits)
    # First col: elements M[1, 0] ... M[m-1, 0] (m - 1 bits)
    random_bits = rng.integers(0, 2, size=m_int + n_int - 1, dtype=np.int8)

    # Layout:
    # Let random_bits[0 : m] represent the first column reversed (or top-left downwards):
    # Standard Toeplitz indexing: M[i, j] = seq[i - j + (n - 1)]
    # where seq has length m + n - 1.
    # When i=0, j=0..n-1: index goes from n-1 down to 0 (first row).
    # When j=0, i=0..m-1: index goes from n-1 up to m+n-2 (first col).
    # Vectorized Toeplitz indexing: M[i, j] = random_bits[i - j + (n - 1)]
    idx_matrix = (
        np.arange(m_int, dtype=np.int32)[:, None]
        - np.arange(n_int, dtype=np.int32)[None, :]
        + (n_int - 1)
    )
    return random_bits[idx_matrix]


def amplify_privacy(
    key: Sequence[int],
    final_key_length: int,
    seed: Optional[int] = None,
    matrix: Optional[np.ndarray] = None,
) -> List[int]:
    """Compress a reconciled binary key into a secret key via Toeplitz matrix multiplication modulo 2.

    Computes:
        final_key = (M * key) mod 2
    using strictly binary integer arithmetic (GF(2)), with zero floating point representation.

    Args:
        key: Binary input sequence (reconciled key) of length n.
        final_key_length: Desired secret key length m (must satisfy 1 <= m <= n).
        seed: Optional seed to generate the shared public Toeplitz matrix.
        matrix: Optional precomputed (m x n) binary Toeplitz matrix.

    Returns:
        List of binary integers (0 or 1) of length final_key_length.

    Raises:
        TypeError: If inputs have invalid types.
        ValueError: If key is invalid or dimensions are inconsistent.
    """
    key_bits = _validate_binary_sequence(key, "key")
    n = len(key_bits)

    if isinstance(final_key_length, bool) or not isinstance(
        final_key_length, (int, np.integer)
    ):
        raise TypeError(
            f"final_key_length must be an integer, got {type(final_key_length).__name__}"
        )

    m = int(final_key_length)
    if m <= 0:
        raise ValueError(f"final_key_length must be positive, got {m}")
    if m > n:
        raise ValueError(
            f"final_key_length ({m}) cannot exceed reconciled key length ({n})."
        )

    if matrix is not None:
        if not isinstance(matrix, np.ndarray):
            raise TypeError(f"matrix must be a numpy ndarray, got {type(matrix).__name__}")
        if matrix.shape != (m, n):
            raise ValueError(
                f"Matrix shape {matrix.shape} does not match expected ({m}, {n})."
            )
        toeplitz_mat = matrix.astype(np.int8)
    else:
        toeplitz_mat = generate_toeplitz_matrix(m=m, n=n, seed=seed)

    # Perform matrix multiplication modulo 2: y = (M @ x) % 2
    x_vec = np.array(key_bits, dtype=np.int8)

    # Integer bitwise dot product modulo 2
    # (toeplitz_mat @ x_vec) % 2
    result_vec = np.bitwise_and(toeplitz_mat, x_vec).sum(axis=1) % 2

    return [int(b) for b in result_vec]
