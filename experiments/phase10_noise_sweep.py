"""Phase 10 Experiment 3: Physical Quantum Noise Sweep Across Three Noise Models.

Sweeps noise probability p from 0.00 to 0.20 in increments of 0.02 independently for:
1. Bit-Flip Noise (Pauli-X Channel)
2. Phase-Flip Noise (Pauli-Z Channel)
3. Depolarizing Noise (Isotropic Quantum Channel via Qiskit Aer)

Records empirical QBER, standard deviation, final secret key rate, and acceptance rates.
Compares measured QBER to theoretical references:
- Bit-flip: QBER_theory = p / 2
- Phase-flip: QBER_theory = p / 2
- Depolarizing: QBER_theory = lambda / 2

Outputs:
- results/phase10/data/noise_sweep_trials.csv
- results/phase10/data/noise_sweep_summary.csv
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


def run_noise_sweep(
    total_signals: int = 1000,
    trials_per_point: int = 6,
    master_seed: int = 3003,
    output_dir: str = "results/phase10/data",
) -> List[AggregatedExperimentResult]:
    """Execute noise sweeps across bit-flip, phase-flip, and depolarizing channels.

    Args:
        total_signals: Quantum signals per trial.
        trials_per_point: Trials per probability setting.
        master_seed: Experiment master seed.
        output_dir: Directory where CSV files are saved.

    Returns:
        List of AggregatedExperimentResult objects across all models and sweep points.
    """
    print("=" * 110)
    print("       PHASE 10 EXPERIMENT 3: QUANTUM NOISE SWEEPS (BIT-FLIP, PHASE-FLIP, DEPOLARIZING)")
    print("=" * 110)
    print(f"Signals per Trial:      {total_signals:,}")
    print(f"Trials per Point:       {trials_per_point}")
    print(f"Master PRNG Seed:       {master_seed}")
    print(f"Data Output Directory:  {output_dir}\n")

    noise_models = ["bit_flip", "phase_flip", "depolarizing"]
    noise_probs = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]

    all_trials: List[TrialResult] = []
    aggregated_results: List[AggregatedExperimentResult] = []

    header = (
        f"{'Model':<14} | {'Noise p':<7} | {'Measured QBER':<14} | "
        f"{'Theory QBER':<11} | {'Residual':<9} | {'Final Key Rate':<14} | {'Acceptance'}"
    )
    print(header)
    print("-" * len(header))

    step_idx = 0
    for model in noise_models:
        for p in noise_probs:
            cfg = ExperimentConfig(
                condition_name=f"{model}_p_{p:.2f}",
                total_signals=total_signals,
                number_of_trials=trials_per_point,
                master_seed=master_seed + step_idx * 53,
                eve_enabled=False,
                noise_model=model,
                noise_probability=p,
                block_size=16,
                test_sample_fraction=0.20,
                qber_acceptance_threshold=0.11,
                reconciliation_passes=4,
            )

            agg = run_experiment(cfg)
            aggregated_results.append(agg)
            all_trials.extend(agg.trials)

            measured_qber = agg.qber_stats.mean
            # For single-qubit BB84, random basis choice means:
            # - Bit flip inverts Z, leaves X invariant -> average error is p/2
            # - Phase flip inverts X, leaves Z invariant -> average error is p/2
            # - Depolarizing parameter lambda has error probability lambda/2
            theory_qber = p * 0.5
            residual = measured_qber - theory_qber

            row = (
                f"{model:<14} | {p:<7.2f} | {f'{measured_qber:.2%} ± {agg.qber_stats.std:.2%}':<14} | "
                f"{f'{theory_qber:.2%}':<11} | {f'{residual:+.2%}':<9} | "
                f"{f'{agg.final_key_rate_stats.mean:.2%}':<14} | {f'{agg.acceptance_rate:.0%}'}"
            )
            print(row)
            step_idx += 1
        print("-" * len(header))

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    trials_file = out_path / "noise_sweep_trials.csv"
    summary_file = out_path / "noise_sweep_summary.csv"

    save_trials_to_csv(all_trials, trials_file)
    save_aggregated_to_csv(aggregated_results, summary_file)

    print(f"\n[✓] Saved {len(all_trials)} trial records to:  {trials_file}")
    print(f"[✓] Saved {len(aggregated_results)} sweep summaries to: {summary_file}\n")

    return aggregated_results


if __name__ == "__main__":
    run_noise_sweep()
