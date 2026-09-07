"""Phase 10 Experiment 1: Standard Baseline Analysis Across 6 Physical Conditions.

Evaluates the complete BB84 simulator across six standard transmission regimes:
1. Ideal Channel (No Eve, No Noise)
2. Eve Intercept-Resend (Full Eavesdropping, p_eve = 1.0)
3. Bit-Flip Noise (Pauli-X error, p = 0.05)
4. Phase-Flip Noise (Pauli-Z error, p = 0.05)
5. Depolarizing Noise (Isotropic decoherence, lambda = 0.05)
6. Compound Eve + Noise (p_eve = 0.50, lambda = 0.05)

Outputs:
- Machine-readable CSV trial data to results/phase10/data/baseline_trials.csv
- Machine-readable aggregated summary to results/phase10/data/baseline_summary.csv
- Terminal summary table of mean QBER, std, 95% Wilson CI, key rates, and acceptance rates.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import List

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


def run_baseline_analysis(
    total_signals: int = 1500,
    number_of_trials: int = 10,
    master_seed: int = 1001,
    output_dir: str = "results/phase10/data",
) -> List[AggregatedExperimentResult]:
    """Execute repeated simulation trials across six standard physical channel conditions.

    Args:
        total_signals: Number of quantum signals per trial.
        number_of_trials: Number of independent trials per condition.
        master_seed: Experiment master seed for reproducible PRNG streams.
        output_dir: Directory where CSV results are saved.

    Returns:
        List of AggregatedExperimentResult objects for all conditions.
    """
    print("=" * 110)
    print("       PHASE 10 EXPERIMENT 1: STANDARD CHANNEL BASELINE ANALYSIS")
    print("=" * 110)
    print(f"Signals per Trial:      {total_signals:,}")
    print(f"Trials per Condition:   {number_of_trials}")
    print(f"Master PRNG Seed:       {master_seed}")
    print(f"Data Output Directory:  {output_dir}\n")

    condition_specs = [
        ("Ideal Channel", False, 0.0, "none", 0.0),
        ("Eve Intercept-Resend", True, 1.0, "none", 0.0),
        ("Bit-Flip Noise (5%)", False, 0.0, "bit_flip", 0.05),
        ("Phase-Flip Noise (5%)", False, 0.0, "phase_flip", 0.05),
        ("Depolarizing Noise (5%)", False, 0.0, "depolarizing", 0.05),
        ("Eve + Depol Noise", True, 0.50, "depolarizing", 0.05),
    ]

    aggregated_results: List[AggregatedExperimentResult] = []
    all_trials: List[TrialResult] = []

    header = (
        f"{'Condition':<24} | {'Mean QBER':<11} | {'95% Wilson CI':<17} | "
        f"{'Sift Ratio':<10} | {'Final Key':<10} | {'Key Rate':<9} | {'Accept':<7} | {'Match'}"
    )
    print(header)
    print("-" * len(header))

    for idx, (name, eve_en, eve_p, noise_mod, noise_p) in enumerate(condition_specs):
        cfg = ExperimentConfig(
            condition_name=name,
            total_signals=total_signals,
            number_of_trials=number_of_trials,
            master_seed=master_seed + idx * 100,
            eve_enabled=eve_en,
            eve_probability=eve_p,
            noise_model=noise_mod,
            noise_probability=noise_p,
            block_size=16,
            test_sample_fraction=0.20,
            qber_acceptance_threshold=0.11,
            reconciliation_passes=4,
        )

        agg = run_experiment(cfg)
        aggregated_results.append(agg)
        all_trials.extend(agg.trials)

        ci_str = f"[{agg.pooled_wilson_ci[0]:.2%}, {agg.pooled_wilson_ci[1]:.2%}]"
        match_str = f"{agg.key_agreement_rate:.0%}" if agg.acceptance_rate > 0 else "N/A"

        row = (
            f"{name:<24} | {f'{agg.qber_stats.mean:.2%} ± {agg.qber_stats.std:.2%}':<11} | "
            f"{ci_str:<17} | {f'{agg.mean_sifting_ratio:.2%}':<10} | "
            f"{f'{agg.final_key_length_stats.mean:.0f} bits':<10} | "
            f"{f'{agg.final_key_rate_stats.mean:.2%}':<9} | "
            f"{f'{agg.acceptance_rate:.0%}':<7} | {match_str}"
        )
        print(row)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    trials_file = out_path / "baseline_trials.csv"
    summary_file = out_path / "baseline_summary.csv"

    save_trials_to_csv(all_trials, trials_file)
    save_aggregated_to_csv(aggregated_results, summary_file)

    print("-" * len(header))
    print(f"\n[✓] Saved {len(all_trials)} trial records to:  {trials_file}")
    print(f"[✓] Saved {len(aggregated_results)} condition summaries to: {summary_file}\n")

    return aggregated_results


if __name__ == "__main__":
    run_baseline_analysis()
