"""Experiment 2: Information Reconciliation (Error Correction).

Demonstrates the interactive parity-based error reconciliation protocol:
1. Generation of an Alice key and Bob key with known controlled bit errors.
2. Partitioning into parity blocks.
3. Block parity computation and comparison.
4. Interactive binary search to pinpoint each discrepancy.
5. In-place correction of Bob's key.
6. Public classical leakage quantification.
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
from src.error_correction import reconcile_keys


def run_error_correction_experiment(
    key_length: int = 128,
    error_indices: Sequence[int] = (7, 25, 59, 83, 115),
    block_size: int = 16,
    seed: int = 42,
) -> None:
    """Run interactive reconciliation on keys with specific injected discrepancies.

    Args:
        key_length: Length of keys to reconcile.
        error_indices: Positions in Bob's key where bit errors are introduced.
        block_size: Size of blocks for parity checks.
        seed: Random seed for key generation.
    """
    print("=" * 76)
    print("     PHASE 9 EXPERIMENT 2: INFORMATION RECONCILIATION DEMONSTRATION")
    print("=" * 76)
    print(f"Key Length:   {key_length} bits")
    print(f"Block Size:   {block_size} bits per block")
    print(f"Injected Discrepancies at Positions: {list(error_indices)}\n")

    # 1. Generate Alice's key and Bob's key with injected discrepancies
    rng = np.random.default_rng(seed)
    alice_key = [int(b) for b in rng.integers(0, 2, size=key_length)]
    bob_key = list(alice_key)

    for idx in error_indices:
        bob_key[idx] ^= 1

    pre_errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
    print(f"[1] Pre-Reconciliation Discrepancies: {pre_errors} bits ({pre_errors / key_length:.2%})")

    # 2. Run Reconciliation
    print("\n[2] Executing Parity-Based Information Reconciliation...")
    recon_res = reconcile_keys(
        alice_key=alice_key,
        bob_key=bob_key,
        block_size=block_size,
        num_passes=2,
        seed=seed + 10,
    )

    print(f"  - Blocks Evaluated per Pass: {recon_res.num_blocks}")
    print(f"  - Total Parity Comparisons:  {recon_res.num_parity_comparisons}")
    print(f"  - Bits Corrected in Bob Key: {recon_res.num_corrected_bits}")
    print(f"  - Public Parity Leakage:     {recon_res.reconciliation_leakage_bits} bits disclosed")
    print(f"  - Final Keys Matching:       {recon_res.is_matching}")
    print(f"  - Residual Error Count:      {recon_res.residual_error_count}")

    # 3. Validation
    print("\n[3] Verification of Key Agreement:")
    assert recon_res.is_matching is True
    assert recon_res.corrected_bob_key == alice_key
    print(f"  Success: All {pre_errors} discrepancies successfully located and inverted!")
    print(f"  Bob's key is now 100% identical to Alice's reference key.")

    print("\n" + "=" * 76)
    print("Conclusion: Information reconciliation eliminates channel discrepancies")
    print("at the cost of disclosing parity bits, which must be subtracted during")
    print("subsequent privacy amplification.")
    print("=" * 76)


if __name__ == "__main__":
    run_error_correction_experiment()
