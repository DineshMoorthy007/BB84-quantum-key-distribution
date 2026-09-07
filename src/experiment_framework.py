"""Reusable Experimentation Framework for Phase 10 BB84 Evaluation.

Provides structured experiment configuration, hierarchical deterministic seed derivation,
single-trial and batch execution engines, basis-dependent error profiling,
Wilson confidence bounds, and machine-readable CSV serialization.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import numpy as np

from noise.base import QuantumNoiseModel
from noise.bit_flip import BitFlipNoise
from noise.depolarizing import DepolarizingNoise
from noise.phase_flip import PhaseFlipNoise
from src.alice import Alice
from src.bob import Bob
from src.eve import Eve
from src.key_sifting import SiftingResult, sift_from_alice_and_bob
from src.post_processing import PostProcessingResult, run_post_processing_pipeline
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel
from src.statistics import (
    DescriptiveStats,
    compute_descriptive_stats,
    wilson_score_interval,
)


@dataclass(frozen=True)
class ExperimentConfig:
    """Standardized configuration for BB84 experimental simulations.

    Attributes:
        condition_name: Descriptive label for the experimental condition.
        total_signals: Number of quantum carriers sent by Alice per trial.
        number_of_trials: Number of independent simulation trials.
        master_seed: Master integer seed for deterministic hierarchical seed derivation.
        eve_enabled: Whether Eve intercepts carriers in transit.
        eve_probability: Interception probability p_eve ∈ [0.0, 1.0].
        noise_model: Noise type ('none', 'bit_flip', 'phase_flip', 'depolarizing').
        noise_probability: Physical noise channel parameter p ∈ [0.0, 1.0].
        block_size: Parity block size for information reconciliation.
        test_sample_fraction: Fraction of sifted key sacrificed for error estimation.
        qber_acceptance_threshold: Security abort cutoff (default 0.11).
        reconciliation_passes: Number of multi-pass permutations for error correction.
        final_key_length: Target final secret key length, or None for information-theoretic sizing.
    """

    condition_name: str = "Standard"
    total_signals: int = 2000
    number_of_trials: int = 10
    master_seed: int = 42
    eve_enabled: bool = False
    eve_probability: float = 1.0
    noise_model: str = "none"
    noise_probability: float = 0.0
    block_size: int = 16
    test_sample_fraction: float = 0.20
    qber_acceptance_threshold: float = 0.11
    reconciliation_passes: int = 4
    final_key_length: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.total_signals <= 0:
            raise ValueError(f"total_signals must be positive, got {self.total_signals}")
        if self.number_of_trials <= 0:
            raise ValueError(f"number_of_trials must be positive, got {self.number_of_trials}")
        if not (0.0 <= self.eve_probability <= 1.0):
            raise ValueError(f"eve_probability must be in [0.0, 1.0], got {self.eve_probability}")
        if not (0.0 <= self.noise_probability <= 1.0):
            raise ValueError(f"noise_probability must be in [0.0, 1.0], got {self.noise_probability}")
        if not (0.0 < self.test_sample_fraction < 1.0):
            raise ValueError(f"test_sample_fraction must be in (0.0, 1.0), got {self.test_sample_fraction}")
        if not (0.0 <= self.qber_acceptance_threshold <= 1.0):
            raise ValueError(
                f"qber_acceptance_threshold must be in [0.0, 1.0], got {self.qber_acceptance_threshold}"
            )
        if self.block_size <= 1:
            raise ValueError(f"block_size must be >= 2, got {self.block_size}")
        if self.reconciliation_passes <= 0:
            raise ValueError(f"reconciliation_passes must be positive, got {self.reconciliation_passes}")

        valid_noise = {"none", "bit_flip", "phase_flip", "depolarizing"}
        if self.noise_model.lower() not in valid_noise:
            raise ValueError(f"Invalid noise_model '{self.noise_model}'. Must be one of {sorted(valid_noise)}")


@dataclass(frozen=True)
class TrialResult:
    """Comprehensive measurement record for a single BB84 simulation trial."""

    trial_index: int
    condition_name: str
    total_signals: int
    sifted_key_length: int
    sifting_ratio: float
    test_bits: int
    estimated_qber: float
    actual_qber: float
    estimated_error_count: int
    actual_error_count: int
    corrected_bits: int
    reconciliation_leakage: int
    reconciled_key_length: int
    final_key_length: int
    final_key_rate: float
    compression_ratio: float
    accepted: bool
    final_keys_match: bool
    reconciliation_matched: bool
    z_basis_sifted_length: int
    z_basis_qber: float
    x_basis_sifted_length: int
    x_basis_qber: float
    qber_ci_lower: float
    qber_ci_upper: float


@dataclass(frozen=True)
class AggregatedExperimentResult:
    """Aggregated statistical summary across multiple independent simulation trials."""

    config: ExperimentConfig
    trials: List[TrialResult]
    num_trials: int
    acceptance_rate: float
    key_agreement_rate: float
    mean_sifting_ratio: float
    qber_stats: DescriptiveStats
    actual_qber_stats: DescriptiveStats
    final_key_length_stats: DescriptiveStats
    final_key_rate_stats: DescriptiveStats
    reconciliation_leakage_stats: DescriptiveStats
    mean_z_basis_qber: float
    mean_x_basis_qber: float
    pooled_wilson_ci: Tuple[float, float]


def derive_trial_seeds(master_seed: int, trial_index: int) -> Tuple[int, int, int, int, int, int, int]:
    """Derive isolated, deterministic PRNG seeds for each component of a simulation trial.

    Uses NumPy's SeedSequence to generate 7 independent 32-bit integer seeds from (master_seed, trial_index):
    1. Alice seed
    2. Bob seed
    3. Eve seed
    4. Noise channel seed
    5. Error estimation sampling seed
    6. Information reconciliation permutation seed
    7. Privacy amplification Toeplitz seed

    Args:
        master_seed: Experiment-wide master seed.
        trial_index: Index of the current trial.

    Returns:
        Tuple of 7 independent positive integers.
    """
    ss = np.random.SeedSequence([master_seed, trial_index])
    generated = ss.generate_state(7, dtype=np.uint32)
    return tuple(int(s) for s in generated)  # type: ignore[return-value]


def create_noise_instance(noise_model: str, probability: float, seed: int) -> Optional[QuantumNoiseModel]:
    """Instantiate a QuantumNoise channel according to configuration.

    Args:
        noise_model: Noise type ('none', 'bit_flip', 'phase_flip', 'depolarizing').
        probability: Physical error parameter p ∈ [0.0, 1.0].
        seed: Component random seed.

    Returns:
        Configured QuantumNoise object or None if 'none' or probability is zero.
    """
    model = noise_model.lower()
    if model == "none" or probability <= 0.0:
        return None
    elif model == "bit_flip":
        return BitFlipNoise(probability=probability, seed=seed)
    elif model == "phase_flip":
        return PhaseFlipNoise(probability=probability, seed=seed)
    elif model == "depolarizing":
        return DepolarizingNoise(probability=probability, seed=seed)
    else:
        raise ValueError(f"Unknown noise model '{noise_model}'")


def run_single_trial(config: ExperimentConfig, trial_index: int) -> TrialResult:
    """Execute a single end-to-end BB84 trial under the specified configuration.

    Args:
        config: Experiment configuration parameters.
        trial_index: 0-based index of this trial.

    Returns:
        TrialResult recording all transmission, sifting, error, and post-processing metrics.
    """
    seeds = derive_trial_seeds(config.master_seed, trial_index)
    alice_seed, bob_seed, eve_seed, noise_seed, est_seed, rec_seed, priv_seed = seeds

    # 1. Instantiate Channel Components
    eve_inst = (
        Eve(seed=eve_seed, interception_probability=config.eve_probability)
        if config.eve_enabled and config.eve_probability > 0.0
        else None
    )
    noise_inst = create_noise_instance(
        config.noise_model, config.noise_probability, seed=noise_seed
    )

    alice = Alice(number_of_qubits=config.total_signals, seed=alice_seed)
    bob = Bob(seed=bob_seed)
    channel = QuantumChannel(eve=eve_inst, noise=noise_inst)

    # 2. Quantum Carrier Transmission
    signals = alice.get_quantum_signals()
    transmitted_signals = channel.transmit(signals)
    bob.receive_and_measure(transmitted_signals)

    # 3. Classical Basis Reconciliation & Key Sifting
    sifted: SiftingResult = sift_from_alice_and_bob(alice, bob)
    alice_sifted = sifted.alice_sifted_key
    bob_sifted = sifted.bob_sifted_key
    sifted_len = sifted.sifted_key_length
    sifting_ratio = sifted.sifting_ratio

    # 4. Ground-Truth Sifted Error Calculation (before pruning)
    ground_truth_qber_res = calculate_qber(alice_sifted, bob_sifted)
    actual_qber = ground_truth_qber_res.qber
    actual_error_count = ground_truth_qber_res.error_count

    # 5. Basis-Dependent Error Profiling (Z vs X)
    alice_bases = alice.bases
    z_alice_bits: List[int] = []
    z_bob_bits: List[int] = []
    x_alice_bits: List[int] = []
    x_bob_bits: List[int] = []

    for i, match_idx in enumerate(sifted.matching_indices):
        basis = alice_bases[match_idx]
        if basis == "Z":
            z_alice_bits.append(alice_sifted[i])
            z_bob_bits.append(bob_sifted[i])
        elif basis == "X":
            x_alice_bits.append(alice_sifted[i])
            x_bob_bits.append(bob_sifted[i])

    z_qber = calculate_qber(z_alice_bits, z_bob_bits).qber if z_alice_bits else 0.0
    x_qber = calculate_qber(x_alice_bits, x_bob_bits).qber if x_alice_bits else 0.0

    # 6. Classical Post-Processing Pipeline
    post_res: PostProcessingResult = run_post_processing_pipeline(
        alice_sifted_key=alice_sifted,
        bob_sifted_key=bob_sifted,
        sample_fraction=config.test_sample_fraction,
        qber_threshold=config.qber_acceptance_threshold,
        block_size=config.block_size,
        reconciliation_passes=config.reconciliation_passes,
        final_key_length=config.final_key_length,
        estimation_seed=est_seed,
        reconciliation_seed=rec_seed,
        privacy_seed=priv_seed,
    )

    # 7. Confidence Interval on Estimated QBER
    ci_lower, ci_upper = wilson_score_interval(
        errors=post_res.num_test_errors,
        total_trials=post_res.num_test_bits,
        confidence=0.95,
    )

    final_rate = post_res.final_key_length / float(config.total_signals)
    comp_ratio = (
        post_res.final_key_length / float(post_res.reconciled_key_length)
        if post_res.reconciled_key_length > 0
        else 0.0
    )

    return TrialResult(
        trial_index=trial_index,
        condition_name=config.condition_name,
        total_signals=config.total_signals,
        sifted_key_length=sifted_len,
        sifting_ratio=sifting_ratio,
        test_bits=post_res.num_test_bits,
        estimated_qber=post_res.estimated_qber,
        actual_qber=actual_qber,
        estimated_error_count=post_res.num_test_errors,
        actual_error_count=actual_error_count,
        corrected_bits=post_res.num_corrected_bits,
        reconciliation_leakage=post_res.reconciliation_leakage_bits,
        reconciled_key_length=post_res.reconciled_key_length,
        final_key_length=post_res.final_key_length,
        final_key_rate=final_rate,
        compression_ratio=comp_ratio,
        accepted=post_res.is_accepted,
        final_keys_match=post_res.keys_match,
        reconciliation_matched=post_res.reconciliation_matched,
        z_basis_sifted_length=len(z_alice_bits),
        z_basis_qber=z_qber,
        x_basis_sifted_length=len(x_alice_bits),
        x_basis_qber=x_qber,
        qber_ci_lower=ci_lower,
        qber_ci_upper=ci_upper,
    )


def run_experiment(config: ExperimentConfig) -> AggregatedExperimentResult:
    """Execute all trials for a given configuration and compute aggregate statistics.

    Args:
        config: Standard experiment configuration.

    Returns:
        AggregatedExperimentResult summarizing statistical performance across all trials.
    """
    trials = [run_single_trial(config, t_idx) for t_idx in range(config.number_of_trials)]

    n = len(trials)
    accepted_count = sum(1 for t in trials if t.accepted)
    accepted_trials = [t for t in trials if t.accepted]
    matched_count = sum(1 for t in accepted_trials if t.final_keys_match)

    acceptance_rate = accepted_count / float(n)
    key_agreement_rate = (matched_count / float(accepted_count)) if accepted_count > 0 else 0.0

    qber_stats = compute_descriptive_stats([t.estimated_qber for t in trials])
    actual_qber_stats = compute_descriptive_stats([t.actual_qber for t in trials])
    key_len_stats = compute_descriptive_stats([float(t.final_key_length) for t in trials])
    key_rate_stats = compute_descriptive_stats([t.final_key_rate for t in trials])
    leakage_stats = compute_descriptive_stats([float(t.reconciliation_leakage) for t in trials])

    mean_sift_ratio = float(np.mean([t.sifting_ratio for t in trials]))
    mean_z_qber = float(np.mean([t.z_basis_qber for t in trials]))
    mean_x_qber = float(np.mean([t.x_basis_qber for t in trials]))

    # Pooled Wilson CI across all test samples
    total_test_errors = sum(t.estimated_error_count for t in trials)
    total_test_bits = sum(t.test_bits for t in trials)
    pooled_ci = wilson_score_interval(total_test_errors, total_test_bits, confidence=0.95)

    return AggregatedExperimentResult(
        config=config,
        trials=trials,
        num_trials=n,
        acceptance_rate=acceptance_rate,
        key_agreement_rate=key_agreement_rate,
        mean_sifting_ratio=mean_sift_ratio,
        qber_stats=qber_stats,
        actual_qber_stats=actual_qber_stats,
        final_key_length_stats=key_len_stats,
        final_key_rate_stats=key_rate_stats,
        reconciliation_leakage_stats=leakage_stats,
        mean_z_basis_qber=mean_z_qber,
        mean_x_basis_qber=mean_x_qber,
        pooled_wilson_ci=pooled_ci,
    )


def save_trials_to_csv(trials: Sequence[TrialResult], file_path: str | Path) -> None:
    """Save raw trial measurement results to a CSV file.

    Args:
        trials: Sequence of TrialResult records.
        file_path: Target CSV file path.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "trial_index",
        "condition_name",
        "total_signals",
        "sifted_key_length",
        "sifting_ratio",
        "test_bits",
        "estimated_qber",
        "actual_qber",
        "estimated_error_count",
        "actual_error_count",
        "corrected_bits",
        "reconciliation_leakage",
        "reconciled_key_length",
        "final_key_length",
        "final_key_rate",
        "compression_ratio",
        "accepted",
        "final_keys_match",
        "reconciliation_matched",
        "z_basis_sifted_length",
        "z_basis_qber",
        "x_basis_sifted_length",
        "x_basis_qber",
        "qber_ci_lower",
        "qber_ci_upper",
    ]

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for t in trials:
            writer.writerow(asdict(t))


def load_trials_from_csv(file_path: str | Path) -> List[Dict[str, Any]]:
    """Load trial records from a CSV file into structured dictionaries.

    Args:
        file_path: Path to the CSV file.

    Returns:
        List of dictionaries with converted data types.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    records: List[Dict[str, Any]] = []
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record: Dict[str, Any] = {
                "trial_index": int(row["trial_index"]),
                "condition_name": row["condition_name"],
                "total_signals": int(row["total_signals"]),
                "sifted_key_length": int(row["sifted_key_length"]),
                "sifting_ratio": float(row["sifting_ratio"]),
                "test_bits": int(row["test_bits"]),
                "estimated_qber": float(row["estimated_qber"]),
                "actual_qber": float(row["actual_qber"]),
                "estimated_error_count": int(row["estimated_error_count"]),
                "actual_error_count": int(row["actual_error_count"]),
                "corrected_bits": int(row["corrected_bits"]),
                "reconciliation_leakage": int(row["reconciliation_leakage"]),
                "reconciled_key_length": int(row["reconciled_key_length"]),
                "final_key_length": int(row["final_key_length"]),
                "final_key_rate": float(row["final_key_rate"]),
                "compression_ratio": float(row["compression_ratio"]),
                "accepted": row["accepted"].strip().lower() in ("true", "1"),
                "final_keys_match": row["final_keys_match"].strip().lower() in ("true", "1"),
                "reconciliation_matched": row["reconciliation_matched"].strip().lower() in ("true", "1"),
                "z_basis_sifted_length": int(row["z_basis_sifted_length"]),
                "z_basis_qber": float(row["z_basis_qber"]),
                "x_basis_sifted_length": int(row["x_basis_sifted_length"]),
                "x_basis_qber": float(row["x_basis_qber"]),
                "qber_ci_lower": float(row["qber_ci_lower"]),
                "qber_ci_upper": float(row["qber_ci_upper"]),
            }
            records.append(record)

    return records


def save_aggregated_to_csv(
    results: Sequence[AggregatedExperimentResult], file_path: str | Path
) -> None:
    """Save aggregated condition summary metrics to CSV.

    Args:
        results: Sequence of AggregatedExperimentResult objects.
        file_path: Output CSV file path.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "condition_name",
        "total_signals",
        "num_trials",
        "master_seed",
        "eve_enabled",
        "eve_probability",
        "noise_model",
        "noise_probability",
        "acceptance_rate",
        "key_agreement_rate",
        "mean_sifting_ratio",
        "qber_mean",
        "qber_std",
        "qber_median",
        "qber_min",
        "qber_max",
        "actual_qber_mean",
        "actual_qber_std",
        "final_key_length_mean",
        "final_key_length_std",
        "final_key_rate_mean",
        "final_key_rate_std",
        "leakage_mean",
        "mean_z_basis_qber",
        "mean_x_basis_qber",
        "pooled_ci_lower",
        "pooled_ci_upper",
    ]

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            cfg = r.config
            row = {
                "condition_name": cfg.condition_name,
                "total_signals": cfg.total_signals,
                "num_trials": r.num_trials,
                "master_seed": cfg.master_seed,
                "eve_enabled": cfg.eve_enabled,
                "eve_probability": cfg.eve_probability,
                "noise_model": cfg.noise_model,
                "noise_probability": cfg.noise_probability,
                "acceptance_rate": r.acceptance_rate,
                "key_agreement_rate": r.key_agreement_rate,
                "mean_sifting_ratio": r.mean_sifting_ratio,
                "qber_mean": r.qber_stats.mean,
                "qber_std": r.qber_stats.std,
                "qber_median": r.qber_stats.median,
                "qber_min": r.qber_stats.min,
                "qber_max": r.qber_stats.max,
                "actual_qber_mean": r.actual_qber_stats.mean,
                "actual_qber_std": r.actual_qber_stats.std,
                "final_key_length_mean": r.final_key_length_stats.mean,
                "final_key_length_std": r.final_key_length_stats.std,
                "final_key_rate_mean": r.final_key_rate_stats.mean,
                "final_key_rate_std": r.final_key_rate_stats.std,
                "leakage_mean": r.reconciliation_leakage_stats.mean,
                "mean_z_basis_qber": r.mean_z_basis_qber,
                "mean_x_basis_qber": r.mean_x_basis_qber,
                "pooled_ci_lower": r.pooled_wilson_ci[0],
                "pooled_ci_upper": r.pooled_wilson_ci[1],
            }
            writer.writerow(row)
