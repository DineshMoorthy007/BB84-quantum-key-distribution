"""Experiment 4: Complete End-to-End BB84 Classical Post-Processing Pipeline.

Runs the complete quantum-to-classical BB84 protocol across 4 physical conditions:
1. Ideal Channel (Noiseless Baseline)
2. Eve Intercept-Resend (Eavesdropping Attack)
3. Quantum Noise (Depolarizing Environmental Noise)
4. Eve + Quantum Noise (Compound Degradation)

Full Workflow:
Alice Signals
  ↓
QuantumChannel (with Eve/Noise)
  ↓
Bob Measurement
  ↓
Basis Reconciliation & Key Sifting
  ↓
Error Estimation (Parameter Testing & Disclosed Bits Removal)
  ↓
Security Cutoff Threshold (Accept / Abort)
  ↓
Information Reconciliation (Parity-Based Error Correction)
  ↓
Privacy Amplification (Toeplitz Hashing in GF(2))
  ↓
Final Distilled Secret Key

Outputs:
- Terminal summary table of all pipeline stages.
- Visualizations saved to results/phase9_sifted_vs_final.png and results/phase9_end_to_end.png.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from noise.depolarizing import DepolarizingNoise
from src.alice import Alice
from src.bob import Bob
from src.eve import Eve
from src.key_sifting import sift_from_alice_and_bob
from src.post_processing import PostProcessingResult, run_post_processing_pipeline
from src.quantum_channel import QuantumChannel
from visualization.post_processing_plots import (
    plot_end_to_end_summary,
    plot_sifted_vs_final_key_lengths,
)


def run_end_to_end_post_processing_experiment(
    signals_per_condition: int = 3000,
    depol_rate: float = 0.04,
    qber_threshold: float = 0.11,
    seed: int = 500,
) -> None:
    """Execute end-to-end post-processing across all physical transmission regimes.

    Args:
        signals_per_condition: Total quantum carriers emitted per trial.
        depol_rate: Noise rate for the noisy channel configurations.
        qber_threshold: Security abort threshold (Shor-Preskill bound = 11.0%).
        seed: Base random seed for reproducible runs.
    """
    print("=" * 96)
    print("      PHASE 9 EXPERIMENT 4: FULL END-TO-END BB84 CLASSICAL POST-PROCESSING BENCHMARK")
    print("=" * 96)
    print(f"Signals per Condition:   {signals_per_condition}")
    print(f"Depolarization Rate:     {depol_rate:.2f}")
    print(f"Security Threshold:      {qber_threshold:.1%}\n")

    conditions = [
        ("Ideal Channel", False, False),
        ("Quantum Noise (4%)", False, True),
        ("Eve Attack (100%)", True, False),
        ("Eve + Noise", True, True),
    ]

    header = (
        f"{'Condition':<20} | {'Sifted':<7} | {'Test Bits':<9} | {'Est. QBER':<10} | "
        f"{'Corrected':<9} | {'Leakage':<8} | {'Final Key':<9} | {'Decision':<8} | {'Match'}"
    )
    print(header)
    print("-" * len(header))

    summary_records: Dict[str, Dict[str, Any]] = {}
    cond_names: List[str] = []
    sifted_lens: List[int] = []
    final_lens: List[int] = []

    for idx, (label, use_eve, use_noise) in enumerate(conditions):
        seed_iter = seed + idx * 50

        eve_inst = Eve(seed=seed_iter + 2, interception_probability=1.0) if use_eve else None
        noise_inst = (
            DepolarizingNoise(probability=depol_rate, seed=seed_iter + 3) if use_noise else None
        )

        alice = Alice(number_of_qubits=signals_per_condition, seed=seed_iter)
        bob = Bob(seed=seed_iter + 1)
        channel = QuantumChannel(eve=eve_inst, noise=noise_inst)

        # 1. Quantum transmission
        signals = alice.get_quantum_signals()
        received = channel.transmit(signals)
        bob.receive_and_measure(received)

        # 2. Key Sifting
        sifted = sift_from_alice_and_bob(alice, bob)

        # 3. Complete Classical Post-Processing Pipeline
        post_res: PostProcessingResult = run_post_processing_pipeline(
            alice_sifted_key=sifted.alice_sifted_key,
            bob_sifted_key=sifted.bob_sifted_key,
            sample_fraction=0.20,
            qber_threshold=qber_threshold,
            block_size=16,
            reconciliation_passes=4,
            estimation_seed=seed_iter + 4,
            reconciliation_seed=seed_iter + 5,
            privacy_seed=seed_iter + 6,
        )

        decision_str = "ACCEPTED" if post_res.is_accepted else "ABORTED"
        match_str = str(post_res.keys_match) if post_res.is_accepted else "N/A"

        row = (
            f"{label:<20} | {post_res.initial_sifted_length:<7} | "
            f"{post_res.num_test_bits:<9} | {f'{post_res.estimated_qber:.2%}':<10} | "
            f"{post_res.num_corrected_bits:<9} | {post_res.reconciliation_leakage_bits:<8} | "
            f"{post_res.final_key_length:<9} | {decision_str:<8} | {match_str}"
        )
        print(row)

        summary_records[label] = {
            "estimated_qber_pct": post_res.estimated_qber * 100.0,
            "final_key_len": post_res.final_key_length,
            "is_accepted": post_res.is_accepted,
            "leakage": post_res.reconciliation_leakage_bits,
        }
        cond_names.append(label)
        sifted_lens.append(post_res.initial_sifted_length)
        final_lens.append(post_res.final_key_length)

    print("=" * 96)
    print("\nOperational Takeaways:")
    print("  1. Under Ideal Channel & Minor Noise, QBER < 11%: keys are reconciled,")
    print("     compressed via Toeplitz hashing, and Alice/Bob hold IDENTICAL secret keys.")
    print("  2. Under Eve Intercept-Resend & Eve+Noise, QBER > 11%: the post-processing")
    print("     pipeline detects excessive disturbance, ABORTS, and prevents compromised key usage.")

    # Visualizations
    p1 = plot_sifted_vs_final_key_lengths(cond_names, sifted_lens, final_lens)
    p2 = plot_end_to_end_summary(summary_records)
    print(f"\n[Plots Generated]:\n  - {p1}\n  - {p2}\n")


if __name__ == "__main__":
    run_end_to_end_post_processing_experiment()
