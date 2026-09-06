"""Phase 6 Educational Experiment: Statistical Convergence of QBER.

This script studies how sample size affects QBER measurement accuracy:
1. Evaluates QBER across sample sizes (100, 500, 1,000, 5,000, 10,000 bits).
2. Applies a fixed controlled error probability (e.g. 10.0%).
3. Illustrates the Law of Large Numbers and statistical variance reduction.
4. Generates and saves a statistical convergence plot to results/.

Usage:
    .venv/Scripts/python experiments/phase6_statistics.py
    .venv/Scripts/python experiments/phase6_statistics.py --error-rate 0.10 --seed 42
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 output on platforms where default stdout is cp1252 (e.g. Windows)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from src.error_injection import inject_classical_bit_errors
from src.qber import calculate_qber
from visualization.qber_plots import plot_qber_convergence


def run_statistics_experiment(
    error_rate: float = 0.10,
    seed: int = 42,
) -> None:
    """Execute the statistical convergence experiment across multiple key lengths."""
    sample_sizes = [100, 500, 1000, 5000, 10000]
    measured_qbers = []

    print("=" * 80)
    print("           BB84 QUANTUM KEY DISTRIBUTION: PHASE 6 STATISTICS")
    print("                 Statistical Convergence of QBER Estimation")
    print("=" * 80)
    print(f"Target Controlled Error Rate: {error_rate * 100:.1f}% | Random Seed: {seed}\n")

    print(
        f"{'Sample Size (Bits)':<20} | {'Error Count':<13} | "
        f"{'Measured QBER':<15} | {'Deviation from Target':<22}"
    )
    print("-" * 80)

    rng = np.random.default_rng(seed)

    for size in sample_sizes:
        # Generate clean synthetic Alice key of length `size`
        alice_key = [int(b) for b in rng.integers(0, 2, size=size)]

        # Bob receives key with controlled classical bit flips
        corrupted_bob_key = inject_classical_bit_errors(
            alice_key,
            error_rate=error_rate,
            seed=int(rng.integers(0, 2**31 - 1)),
        )

        qber_result = calculate_qber(alice_key, corrupted_bob_key)
        measured_qbers.append(qber_result.qber)

        deviation = qber_result.qber - error_rate
        deviation_str = f"{deviation * 100:+.2f}%"

        print(
            f"{size:<20} | "
            f"{qber_result.error_count:<13} | "
            f"{qber_result.qber_percentage:6.2f}%         | "
            f"{deviation_str:<22}"
        )

    print("-" * 80)

    # Generate convergence plot
    try:
        plot_path = plot_qber_convergence(
            sample_sizes=sample_sizes,
            measured_qbers=measured_qbers,
            target_error_rate=error_rate,
        )
        print(f"\nConvergence plot saved to: {plot_path.relative_to(PROJECT_ROOT)}")
    except Exception as exc:
        print(f"\nPlotting skipped due to error: {exc}")

    print("\nStatistical Observations:")
    print("1. Small sample sizes (e.g. 100 bits) exhibit noticeable Poisson / binomial fluctuations.")
    print("2. As sample size grows to 5,000 and 10,000 bits, variance shrinks rapidly as O(1/√N).")
    print("3. In practical QKD systems, sufficiently large sample sizes (or statistical confidence bounds)")
    print("   are required to avoid false alarms or underestimating eavesdropper presence.\n")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="BB84 Phase 6 Statistical Convergence Experiment")
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.10,
        help="Target error rate for validation (default: 0.10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_statistics_experiment(error_rate=args.error_rate, seed=args.seed)
