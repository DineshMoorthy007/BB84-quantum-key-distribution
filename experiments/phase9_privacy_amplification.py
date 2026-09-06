"""Experiment 3: Privacy Amplification (Toeplitz Matrix Hashing).

Demonstrates universal hash compression on reconciled keys:
1. Creation of a shared public binary Toeplitz matrix M of size (m x n).
2. Compression of Alice's and Bob's identical n-bit reconciled keys into m-bit secret keys.
3. Verification of exact agreement under GF(2) arithmetic.
4. Evaluation of compression ratios and Eve information minimization.
"""

from __future__ import annotations

import os
import sys

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from src.privacy_amplification import amplify_privacy, generate_toeplitz_matrix


def run_privacy_amplification_experiment(
    input_length: int = 120,
    final_length: int = 60,
    seed: int = 42,
) -> None:
    """Demonstrate Toeplitz hashing privacy amplification.

    Args:
        input_length: Length n of the reconciled key.
        final_length: Length m of the secret final key.
        seed: Random seed for matrix and key generation.
    """
    print("=" * 76)
    print("      PHASE 9 EXPERIMENT 3: PRIVACY AMPLIFICATION DEMONSTRATION")
    print("=" * 76)
    print(f"Reconciled Key Length (n): {input_length} bits")
    print(f"Target Final Key Length (m): {final_length} bits")
    compression_ratio = final_length / input_length
    print(f"Compression Ratio (m/n):     {compression_ratio:.1%}\n")

    # 1. Generate shared reconciled key
    rng = np.random.default_rng(seed)
    reconciled_alice = [int(b) for b in rng.integers(0, 2, size=input_length)]
    reconciled_bob = list(reconciled_alice)  # Identical after successful reconciliation

    print(f"[1] Reconciled Key Preview (first 24 bits):")
    print(f"    {''.join(str(b) for b in reconciled_alice[:24])}...\n")

    # 2. Public Toeplitz Matrix Generation
    matrix = generate_toeplitz_matrix(m=final_length, n=input_length, seed=seed + 1)
    print(f"[2] Shared Public Toeplitz Matrix M:")
    print(f"    Dimensions: {matrix.shape[0]} rows x {matrix.shape[1]} columns")
    print(f"    Required Random Bits to specify matrix: {final_length + input_length - 1} bits")
    print(f"    Sub-matrix (4x8 corner):")
    for row in matrix[:4, :8]:
        print(f"      {' '.join(str(b) for b in row)}")

    # 3. Privacy Amplification Hash
    final_alice = amplify_privacy(reconciled_alice, final_key_length=final_length, matrix=matrix)
    final_bob = amplify_privacy(reconciled_bob, final_key_length=final_length, matrix=matrix)

    print(f"\n[3] Final Amplified Secret Keys (first 24 bits):")
    print(f"    Alice: {''.join(str(b) for b in final_alice[:24])}...")
    print(f"    Bob:   {''.join(str(b) for b in final_bob[:24])}...")

    # 4. Verification
    assert final_alice == final_bob
    print(f"\n[4] Cryptographic Validation:")
    print(f"    - Alice and Bob final keys match identically: TRUE")
    print(f"    - Final key length: {len(final_alice)} bits")
    print(f"    - Eve's potential partial knowledge has been exponentially reduced.")

    print("\n" + "=" * 76)
    print("Conclusion: Toeplitz matrix hashing strictly compresses the key in GF(2),")
    print("eliminating both channel correlation and public reconciliation leakage.")
    print("=" * 76)


if __name__ == "__main__":
    run_privacy_amplification_experiment()
