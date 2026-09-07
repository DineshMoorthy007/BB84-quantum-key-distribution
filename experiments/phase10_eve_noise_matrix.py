"""Phase 10 Experiment 5: Compound Eve + Noise Interaction Matrix (5x5 Parameter Grid).

Evaluates the non-linear interaction between active eavesdropping (Eve intercept-resend)
and physical channel noise (Depolarizing decoherence) across a 5x5 parameter matrix:
- Eve probability p_eve:    [0.00, 0.25, 0.50, 0.75, 1.00]
- Noise probability p_depol: [0.00, 0.05, 0.10, 0.15, 0.20]

Measures and records for each (p_eve, p_noise) pair:
- Mean QBER and standard deviation
- Protocol acceptance rate
- Mean distilled final secret key rate
- Parity leakage

Outputs:
- results/phase10/data/eve_noise_matrix_trials.csv
- results/phase10/data/eve_noise_matrix_summary.csv
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


def run_eve_noise_matrix(
    total_signals: int = 1000,
    trials_per_cell: int = 5,
    noise_model: str = "depolarizing",
    master_seed: int = 5005,
    output_dir: str = "results/phase10/data",
) -> List[AggregatedExperimentResult]:
    """Execute 5x5 matrix sweep of Eve interception probability vs. physical noise.

    Args:
        total_signals: Quantum signals per trial.
        trials_per_cell: Trials per matrix cell.
        noise_model: Noise model to combine with Eve ('depolarizing').
        master_seed: Master PRNG seed.
        output_dir: Directory where CSV files are saved.

    Returns:
        List of AggregatedExperimentResult objects for all 25 cells.
    """
    print("=" * 110)
    print("       PHASE 10 EXPERIMENT 5: EVE + NOISE 5x5 COMPOUND INTERACTION MATRIX")
    print("=" * 110)
    print(f"Signals per Trial:      {total_signals:,}")
    print(f"Trials per Grid Cell:   {trials_per_cell}")
    print(f"Noise Channel Model:    {noise_model}")
    print(f"Master PRNG Seed:       {master_seed}")
    print(f"Data Output Directory:  {output_dir}\n")

    eve_probs = [0.00, 0.25, 0.50, 0.75, 1.00]
    noise_probs = [0.00, 0.05, 0.10, 0.15, 0.20]

    all_trials: List[TrialResult] = []
    aggregated_results: List[AggregatedExperimentResult] = []
    matrix_summary_rows = []

    header = (
        f"{'p_eve':<7} | {'p_noise':<8} | {'Measured QBER':<14} | "
        f"{'95% Wilson CI':<17} | {'Acceptance':<10} | {'Final Key Rate':<14} | {'Decision'}"
    )
    print(header)
    print("-" * len(header))

    step = 0
    for p_eve in eve_probs:
        for p_noise in noise_probs:
            label = f"Eve_{p_eve:.2f}_Noise_{p_noise:.2f}"
            cfg = ExperimentConfig(
                condition_name=label,
                total_signals=total_signals,
                number_of_trials=trials_per_cell,
                master_seed=master_seed + step * 41,
                eve_enabled=p_eve > 0.0,
                eve_probability=p_eve,
                noise_model=noise_model if p_noise > 0.0 else "none",
                noise_probability=p_noise,
                block_size=16,
                test_sample_fraction=0.20,
                qber_acceptance_threshold=0.11,
                reconciliation_passes=4,
            )

            agg = run_experiment(cfg)
            aggregated_results.append(agg)
            all_trials.extend(agg.trials)

            ci_str = f"[{agg.pooled_wilson_ci[0]:.2%}, {agg.pooled_wilson_ci[1]:.2%}]"
            dec_str = "ACCEPTED" if agg.acceptance_rate > 0.5 else "ABORTED"

            row = (
                f"{p_eve:<7.2f} | {p_noise:<8.2f} | {f'{agg.qber_stats.mean:.2%} ± {agg.qber_stats.std:.2%}':<14} | "
                f"{ci_str:<17} | {f'{agg.acceptance_rate:.0%}':<10} | "
                f"{f'{agg.final_key_rate_stats.mean:.2%}':<14} | {dec_str}"
            )
            print(row)

            matrix_summary_rows.append({
                "eve_probability": p_eve,
                "noise_probability": p_noise,
                "noise_model": noise_model,
                "qber_mean": agg.qber_stats.mean,
                "qber_std": agg.qber_stats.std,
                "qber_median": agg.qber_stats.median,
                "acceptance_rate": agg.acceptance_rate,
                "final_key_rate_mean": agg.final_key_rate_stats.mean,
                "final_key_length_mean": agg.final_key_length_stats.mean,
                "leakage_mean": agg.reconciliation_leakage_stats.mean,
                "pooled_ci_lower": agg.pooled_wilson_ci[0],
                "pooled_ci_upper": agg.pooled_wilson_ci[1],
            })
            step += 1

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    trials_file = out_path / "eve_noise_matrix_trials.csv"
    summary_file = out_path / "eve_noise_matrix_summary.csv"

    save_trials_to_csv(all_trials, trials_file)

    with open(summary_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "eve_probability",
            "noise_probability",
            "noise_model",
            "qber_mean",
            "qber_std",
            "qber_median",
            "acceptance_rate",
            "final_key_rate_mean",
            "final_key_length_mean",
            "leakage_mean",
            "pooled_ci_lower",
            "pooled_ci_upper",
        ])
        writer.writeheader()
        for r in matrix_summary_rows:
            writer.writerow(r)

    print("-" * len(header))
    print(f"\n[✓] Saved {len(all_trials)} trial records to:  {trials_file}")
    print(f"[✓] Saved {len(matrix_summary_rows)} grid summaries to: {summary_file}\n")

    return aggregated_results


if __name__ == "__main__":
    run_eve_noise_matrix()
