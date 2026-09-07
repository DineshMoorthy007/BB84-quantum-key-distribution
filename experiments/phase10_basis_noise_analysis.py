"""Phase 10 Experiment 4: Basis-Dependent Noise Analysis (Z-basis vs. X-basis QBER).

Investigates experimentally whether quantum noise channels exhibit basis-dependent asymmetries:
1. Bit-Flip Noise (Pauli-X): Inverts computational basis |0> <-> |1>, but leaves Hadamard |+>, |-> invariant.
2. Phase-Flip Noise (Pauli-Z): Leaves computational basis |0>, |1> invariant, but inverts Hadamard |+> <-> |->.
3. Depolarizing Noise: Isotropic degradation affecting computational and Hadamard bases symmetrically.

Empirically measures and compares:
- Z-basis sifted key error rate (QBER_Z)
- X-basis sifted key error rate (QBER_X)
- Total sifted key error rate (QBER_total)

Outputs:
- results/phase10/data/basis_noise_analysis_trials.csv
- results/phase10/data/basis_noise_analysis_summary.csv
"""

from __future__ import annotations

import csv
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
    save_trials_to_csv,
)


def run_basis_noise_analysis(
    total_signals: int = 2000,
    number_of_trials: int = 10,
    noise_probability: float = 0.10,
    master_seed: int = 4004,
    output_dir: str = "results/phase10/data",
) -> List[AggregatedExperimentResult]:
    """Execute basis-resolved error analysis across Bit-Flip, Phase-Flip, and Depolarizing channels.

    Args:
        total_signals: Number of quantum carriers sent per trial.
        number_of_trials: Number of independent trials per noise model.
        noise_probability: Noise activation strength (p = 0.10).
        master_seed: Experiment master seed.
        output_dir: Output directory for CSV datasets.

    Returns:
        List of AggregatedExperimentResult objects.
    """
    print("=" * 110)
    print("       PHASE 10 EXPERIMENT 4: BASIS-DEPENDENT QUANTUM NOISE ANALYSIS (Z vs X BASIS)")
    print("=" * 110)
    print(f"Signals per Trial:      {total_signals:,}")
    print(f"Trials per Model:       {number_of_trials}")
    print(f"Noise Parameter (p):    {noise_probability:.2f}")
    print(f"Master PRNG Seed:       {master_seed}")
    print(f"Data Output Directory:  {output_dir}\n")

    models = [
        ("Bit-Flip Noise (10%)", "bit_flip"),
        ("Phase-Flip Noise (10%)", "phase_flip"),
        ("Depolarizing Noise (10%)", "depolarizing"),
    ]

    header = (
        f"{'Noise Channel':<25} | {'Z-Basis QBER':<14} | {'X-Basis QBER':<14} | "
        f"{'Overall QBER':<14} | {'Asymmetry (Z - X)':<18} | {'Physical Behavior'}"
    )
    print(header)
    print("-" * len(header))

    aggregated_results: List[AggregatedExperimentResult] = []
    all_trials: List[TrialResult] = []
    basis_summary_rows = []

    for idx, (label, model_name) in enumerate(models):
        cfg = ExperimentConfig(
            condition_name=label,
            total_signals=total_signals,
            number_of_trials=number_of_trials,
            master_seed=master_seed + idx * 89,
            eve_enabled=False,
            noise_model=model_name,
            noise_probability=noise_probability,
            block_size=16,
            test_sample_fraction=0.20,
            qber_acceptance_threshold=0.15,
            reconciliation_passes=4,
        )

        agg = run_experiment(cfg)
        aggregated_results.append(agg)
        all_trials.extend(agg.trials)

        mean_z = agg.mean_z_basis_qber
        mean_x = agg.mean_x_basis_qber
        mean_total = agg.actual_qber_stats.mean
        asymmetry = mean_z - mean_x

        if model_name == "bit_flip":
            behavior = "Z-vulnerable, X-immune"
        elif model_name == "phase_flip":
            behavior = "X-vulnerable, Z-immune"
        else:
            behavior = "Isotropic (Symmetric)"

        row = (
            f"{label:<25} | {f'{mean_z:.2%}':<14} | {f'{mean_x:.2%}':<14} | "
            f"{f'{mean_total:.2%}':<14} | {f'{asymmetry:+.2%}':<18} | {behavior}"
        )
        print(row)

        basis_summary_rows.append({
            "condition_name": label,
            "noise_model": model_name,
            "noise_probability": noise_probability,
            "mean_z_basis_qber": mean_z,
            "mean_x_basis_qber": mean_x,
            "overall_qber_mean": mean_total,
            "asymmetry_z_minus_x": asymmetry,
            "interpretation": behavior,
        })

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    trials_file = out_path / "basis_noise_analysis_trials.csv"
    summary_file = out_path / "basis_noise_analysis_summary.csv"

    save_trials_to_csv(all_trials, trials_file)

    with open(summary_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "condition_name",
            "noise_model",
            "noise_probability",
            "mean_z_basis_qber",
            "mean_x_basis_qber",
            "overall_qber_mean",
            "asymmetry_z_minus_x",
            "interpretation",
        ])
        writer.writeheader()
        for r in basis_summary_rows:
            writer.writerow(r)

    print("-" * len(header))
    print(f"\n[✓] Saved {len(all_trials)} trial records to:  {trials_file}")
    print(f"[✓] Saved {len(basis_summary_rows)} basis summaries to: {summary_file}\n")

    return aggregated_results


if __name__ == "__main__":
    run_basis_noise_analysis()
