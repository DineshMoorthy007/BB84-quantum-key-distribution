"""Phase 10 Experiment 2: Eve Interception Probability Sweep.

Investigates experimentally how varying Eve's interception probability p_eve from 0.0 to 1.0
affects observed QBER, acceptance rate, and distilled secret-key length.

Compares empirical QBER against the theoretical reference curve:
    QBER_theory(p_eve) = p_eve * 25.0%

Outputs:
- Machine-readable trial records to results/phase10/data/eve_probability_trials.csv
- Machine-readable summary data to results/phase10/data/eve_probability_summary.csv
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import List
import numpy as np

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.experiment_framework import (
    AggregatedExperimentResult,
    ExperimentConfig,
    TrialResult,
    run_experiment,
    save_aggregated_to_csv,
    save_trials_to_csv,
)


def run_eve_probability_sweep(
    total_signals: int = 1200,
    trials_per_point: int = 8,
    master_seed: int = 2002,
    output_dir: str = "results/phase10/data",
) -> List[AggregatedExperimentResult]:
    """Sweep Eve interception probability p_eve in [0.0, 1.0] across multiple independent trials.

    Args:
        total_signals: Quantum signals per trial.
        trials_per_point: Independent trials per probability value.
        master_seed: Experiment master seed.
        output_dir: Directory where CSV files are saved.

    Returns:
        List of AggregatedExperimentResult objects for each sweep point.
    """
    print("=" * 105)
    print("       PHASE 10 EXPERIMENT 2: EVE INTERCEPTION PROBABILITY SWEEP (0.0 to 1.0)")
    print("=" * 105)
    print(f"Signals per Trial:      {total_signals:,}")
    print(f"Trials per Point:       {trials_per_point}")
    print(f"Master PRNG Seed:       {master_seed}")
    print(f"Data Output Directory:  {output_dir}\n")

    p_eve_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    header = (
        f"{'p_eve':<7} | {'Measured QBER':<14} | {'Theory QBER':<11} | "
        f"{'Residual':<10} | {'95% Wilson CI':<17} | {'Acceptance':<10} | {'Final Key Rate'}"
    )
    print(header)
    print("-" * len(header))

    aggregated_results: List[AggregatedExperimentResult] = []
    all_trials: List[TrialResult] = []

    for idx, p_eve in enumerate(p_eve_values):
        cfg = ExperimentConfig(
            condition_name=f"Eve_p_{p_eve:.1f}",
            total_signals=total_signals,
            number_of_trials=trials_per_point,
            master_seed=master_seed + idx * 77,
            eve_enabled=p_eve > 0.0,
            eve_probability=p_eve,
            noise_model="none",
            noise_probability=0.0,
            block_size=16,
            test_sample_fraction=0.20,
            qber_acceptance_threshold=0.11,
            reconciliation_passes=4,
        )

        agg = run_experiment(cfg)
        aggregated_results.append(agg)
        all_trials.extend(agg.trials)

        measured_qber = agg.qber_stats.mean
        theory_qber = p_eve * 0.25
        residual = measured_qber - theory_qber
        ci_str = f"[{agg.pooled_wilson_ci[0]:.2%}, {agg.pooled_wilson_ci[1]:.2%}]"

        row = (
            f"{p_eve:<7.1f} | {f'{measured_qber:.2%} ± {agg.qber_stats.std:.2%}':<14} | "
            f"{f'{theory_qber:.2%}':<11} | {f'{residual:+.2%}':<10} | "
            f"{ci_str:<17} | {f'{agg.acceptance_rate:.0%}':<10} | "
            f"{f'{agg.final_key_rate_stats.mean:.2%}'}"
        )
        print(row)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    trials_file = out_path / "eve_probability_trials.csv"
    summary_file = out_path / "eve_probability_summary.csv"

    save_trials_to_csv(all_trials, trials_file)
    save_aggregated_to_csv(aggregated_results, summary_file)

    print("-" * len(header))
    print(f"\n[✓] Saved {len(all_trials)} trial records to:  {trials_file}")
    print(f"[✓] Saved {len(aggregated_results)} sweep summaries to: {summary_file}\n")

    return aggregated_results


if __name__ == "__main__":
    run_eve_probability_sweep()
