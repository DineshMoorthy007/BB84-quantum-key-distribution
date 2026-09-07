"""BB84 Quantum Key Distribution Simulator.

Core source package for quantum state preparation, measurement,
and protocol execution.
"""

from .alice import Alice, BB84Signal
from .bob import Bob, BobMeasurement
from .config import BB84Config, NoiseModelType
from .error_correction import ReconciliationResult, reconcile_keys
from .error_estimation import ErrorEstimationResult, estimate_error_rate
from .error_injection import inject_classical_bit_errors
from .eve import Eve, EveInterceptionRecord
from .key_sifting import SiftingResult, reconcile_bases, sift_from_alice_and_bob, sift_keys
from .post_processing import PostProcessingResult, run_post_processing_pipeline
from .privacy_amplification import amplify_privacy, generate_toeplitz_matrix
from .qber import QBERResult, QBERSecurityReport, analyze_qber_security, calculate_qber
from .quantum_channel import QuantumChannel
from .quantum_primitives import (
    COMPUTATIONAL_BASIS,
    HADAMARD_BASIS,
    VALID_BASES,
    VALID_BITS,
    create_qubit_circuit,
    get_statevector,
    measure_state,
    measure_x_basis,
    measure_z_basis,
    prepare_state,
    prepare_state_0,
    prepare_state_1,
    prepare_state_minus,
    prepare_state_plus,
    statevectors_are_equivalent,
    validate_basis,
    validate_bit,
)

from .experiment_framework import (
    AggregatedExperimentResult,
    ExperimentConfig,
    TrialResult,
    derive_trial_seeds,
    load_trials_from_csv,
    run_experiment,
    run_single_trial,
    save_aggregated_to_csv,
    save_trials_to_csv,
)
from .statistics import (
    DescriptiveStats,
    compute_descriptive_stats,
    wilson_score_interval,
)

__all__ = [
    "Alice",
    "BB84Signal",
    "Bob",
    "BobMeasurement",
    "Eve",
    "EveInterceptionRecord",
    "QuantumChannel",
    "SiftingResult",
    "reconcile_bases",
    "sift_keys",
    "ErrorEstimationResult",
    "estimate_error_rate",
    "ReconciliationResult",
    "reconcile_keys",
    "generate_toeplitz_matrix",
    "amplify_privacy",
    "PostProcessingResult",
    "run_post_processing_pipeline",
    "QBERResult",
    "QBERSecurityReport",
    "calculate_qber",
    "analyze_qber_security",
    "inject_classical_bit_errors",
    "BB84Config",
    "NoiseModelType",
    "COMPUTATIONAL_BASIS",
    "HADAMARD_BASIS",
    "VALID_BASES",
    "VALID_BITS",
    "create_qubit_circuit",
    "prepare_state_0",
    "prepare_state_1",
    "prepare_state_plus",
    "prepare_state_minus",
    "prepare_state",
    "get_statevector",
    "statevectors_are_equivalent",
    "measure_z_basis",
    "measure_x_basis",
    "measure_state",
    "validate_bit",
    "validate_basis",
    "DescriptiveStats",
    "compute_descriptive_stats",
    "wilson_score_interval",
    "ExperimentConfig",
    "TrialResult",
    "AggregatedExperimentResult",
    "derive_trial_seeds",
    "run_single_trial",
    "run_experiment",
    "save_trials_to_csv",
    "save_aggregated_to_csv",
    "load_trials_from_csv",
]






