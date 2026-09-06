"""Experiment 2: Quantum Noise Parameter Sweep.

Sweeps the physical noise parameter across:
[0.00, 0.01, 0.05, 0.10, 0.20, 0.30]
for all three quantum noise models:
- Bit-Flip Noise (Pauli-X)
- Phase-Flip Noise (Pauli-Z)
- Depolarizing Noise (Qiskit Standard)

Outputs:
- Comparative multi-line scaling plot saved to results/phase8_noise_sweep.png.
- Detailed terminal report comparing QBER evolution.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Sequence

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from noise.bit_flip import BitFlipNoise
from noise.depolarizing import DepolarizingNoise
from noise.phase_flip import PhaseFlipNoise
from src.alice import Alice
from src.bob import Bob
from src.key_sifting import sift_from_alice_and_bob
from src.qber import calculate_qber
from src.quantum_channel import QuantumChannel
from visualization.noise_plots import plot_noise_rate_sweep


def run_noise_sweep_experiment(
    signals_per_trial: int = 3000,
    probabilities: Sequence[float] = (0.00, 0.01, 0.05, 0.10, 0.20, 0.30),
    seed: int = 100,
) -> None:
    """Run parametric sweep across noise channels and probabilities.

    Args:
        signals_per_trial: Number of transmitted quantum signals per trial.
        probabilities: Sequence of noise parameters to evaluate.
        seed: Base random seed for reproducibility.
    """
    print("=" * 82)
    print("         PHASE 8 EXPERIMENT 2: QUANTUM NOISE PARAMETER SWEEP")
    print("=" * 82)
    print(f"Signals per Trial: {signals_per_trial}")
    print(f"Probabilities Evaluated: {list(probabilities)}\n")

    models = [
        ("Bit-Flip", BitFlipNoise),
        ("Phase-Flip", PhaseFlipNoise),
        ("Depolarizing", DepolarizingNoise),
    ]

    sweep_results: Dict[str, List[float]] = {name: [] for name, _ in models}

    for name, model_cls in models:
        print(f"\n--- Evaluating Noise Model: {name} ---")
        header = f"{'Probability':<12} | {'Sifted Key':<11} | {'Errors':<8} | {'QBER (%)':<10}"
        print(header)
        print("-" * len(header))

        for idx, prob in enumerate(probabilities):
            seed_iter = seed + idx * 10
            noise_inst = model_cls(probability=prob, seed=seed_iter + 2) if prob > 0.0 else None

            alice = Alice(number_of_qubits=signals_per_trial, seed=seed_iter)
            bob = Bob(seed=seed_iter + 1)
            channel = QuantumChannel(noise=noise_inst)

            signals = alice.get_quantum_signals()
            received = channel.transmit(signals)
            bob.receive_and_measure(received)

            sifted = sift_from_alice_and_bob(alice, bob)
            qber_res = calculate_qber(sifted.alice_sifted_key, sifted.bob_sifted_key)

            row = (
                f"{prob:<12.2f} | {sifted.sifted_key_length:<11} | "
                f"{qber_res.error_count:<8} | {qber_res.qber_percentage:<10.2f}"
            )
            print(row)

            sweep_results[name].append(qber_res.qber_percentage)

    print("\n" + "=" * 82)

    # Visualization
    img_path = plot_noise_rate_sweep(
        probabilities=probabilities,
        sweep_results=sweep_results,
    )
    print(f"[Plot Generated]: {img_path}\n")


if __name__ == "__main__":
    run_noise_sweep_experiment()
