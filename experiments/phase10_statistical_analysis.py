"""Phase 10 Experiment 6: Multi-Trial Statistical Distributions and Variance Analysis.

Performs high-repetition statistical evaluations across core physical regimes:
1. Ideal Channel (Noiseless Baseline)
2. Low Environmental Noise (Depolarizing lambda = 0.02)
3. Moderate Environmental Noise (Depolarizing lambda = 0.04)
4. Active Eavesdropper (Full Eve Intercept-Resend p_eve = 1.00)

Calculates across 30 independent trials per regime:
- QBER mean, median, variance, standard deviation, minimum, maximum
- Final Secret Key Rate mean, std, median, variance
- Sifting ratio distribution and variance
- Reconciliation leakage statistics
- Acceptance probability (P_accept) and Final-Key Agreement Probability (P_match)
- 95% Wilson confidence intervals

Outputs:
- results/phase10/data/statistical_analysis_trials.csv
- results/phase10/data/statistical_analysis_summary.csv
"""

from __future__ import annotations

import csv
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
    save_trials_to_csv,
)


def run_statistical_analysis(
    total_signals: int = 1200,
    number_of_trials: int = 30,
    master_seed: int = 6006,
    output_dir: str = "results/phase10/data",
) -> List[AggregatedExperimentResult]:
    """Execute high-repetition statistical trials across 4 representative physical regimes.

    Args:
        total_signals: Quantum signals per trial.
        number_of_trials: Repetitions per regime (default 30).
        master_seed: Experiment master seed.
        output_dir: Directory where CSV files are saved.

    Returns:
        List of AggregatedExperimentResult objects.
    """
    print("=" * 115)
    print("       PHASE 10 EXPERIMENT 6: MULTI-TRIAL STATISTICAL DISTRIBUTIONS & VARIANCE ANALYSIS")
    print("=" * 115)
    print(f"Signals per Trial:      {total_signals:,}")
    print(f"Repetitions per Regime: {number_of_trials}")
    print(f"Master PRNG Seed:       {master_seed}")
    print(f"Data Output Directory:  {output_dir}\n")

    regimes = [
        ("Ideal Channel", False, 0.0, "none", 0.0),
        ("Low Noise (2% Depol)", False, 0.0, "depolarizing", 0.02),
        ("Moderate Noise (4% Depol)", False, 0.0, "depolarizing", 0.04),
        ("Full Eve (100% Intercept)", True, 1.0, "none", 0.0),
    ]

    all_trials: List[TrialResult] = []
    aggregated_results: List[AggregatedExperimentResult] = []
    stat_summary_rows = []

    header = (
        f"{'Regime':<26} | {'Mean QBER':<10} | {'Median':<8} | {'Std Dev':<9} | "
        f"{'Variance':<10} | {'[Min, Max]':<15} | {'P(Accept)':<9} | {'P(Match)'}"
    )
    print(header)
    print("-" * len(header))

    for idx, (label, eve_en, eve_p, noise_mod, noise_p) in enumerate(regimes):
        cfg = ExperimentConfig(
            condition_name=label,
            total_signals=total_signals,
            number_of_trials=number_of_trials,
            master_seed=master_seed + idx * 137,
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

        qs = agg.qber_stats
        p_match_str = f"{agg.key_agreement_rate:.0%}" if agg.acceptance_rate > 0 else "N/A"
        min_max_str = f"[{qs.min:.2%}, {qs.max:.2%}]"

        row = (
            f"{label:<26} | {f'{qs.mean:.2%}':<10} | {f'{qs.median:.2%}':<8} | {f'{qs.std:.2%}':<9} | "
            f"{f'{qs.variance:.6f}':<10} | {min_max_str:<15} | {f'{agg.acceptance_rate:.0%}':<9} | {p_match_str}"
        )
        print(row)

        stat_summary_rows.append({
            "regime": label,
            "total_signals": total_signals,
            "trials_count": number_of_trials,
            "qber_mean": qs.mean,
            "qber_median": qs.median,
            "qber_std": qs.std,
            "qber_variance": qs.variance,
            "qber_min": qs.min,
            "qber_max": qs.max,
            "key_rate_mean": agg.final_key_rate_stats.mean,
            "key_rate_std": agg.final_key_rate_stats.std,
            "key_rate_median": agg.final_key_rate_stats.median,
            "key_rate_variance": agg.final_key_rate_stats.variance,
            "acceptance_probability": agg.acceptance_rate,
            "key_agreement_probability": agg.key_agreement_rate,
            "pooled_ci_lower": agg.pooled_wilson_ci[0],
            "pooled_ci_upper": agg.pooled_wilson_ci[1],
        })

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    trials_file = out_path / "statistical_analysis_trials.csv"
    summary_file = out_path / "statistical_analysis_summary.csv"

    save_trials_to_csv(all_trials, trials_file)

    with open(summary_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "regime",
            "total_signals",
            "trials_count",
            "qber_mean",
            "qber_median",
            "qber_std",
            "qber_variance",
            "qber_min",
            "qber_max",
            "key_rate_mean",
            "key_rate_std",
            "key_rate_median",
            "key_rate_variance",
            "acceptance_probability",
            "key_agreement_probability",
            "pooled_ci_lower",
            "pooled_ci_upper",
        ])
        writer.writeheader()
        for r in stat_summary_rows:
            writer.writerow(r)

    print("-" * len(header))
    print(f"\n[✓] Saved {len(all_trials)} trial records to:  {trials_file}")
    print(f"[✓] Saved {len(stat_summary_rows)} statistical summaries to: {summary_file}\n")

    return aggregated_results


if __name__ == "__main__":
    run_statistical_analysis()
