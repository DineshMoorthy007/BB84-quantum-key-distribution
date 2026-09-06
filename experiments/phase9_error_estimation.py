"""Experiment 1: Error Estimation (Parameter Estimation).

Demonstrates the first classical post-processing stage of BB84:
1. Sifted key generation between Alice and Bob.
2. Random sampling of test positions without replacement.
3. Public comparison of disclosed test bits over the classical channel.
4. Calculation of estimated QBER.
5. Permanent removal of disclosed test bits from both keys.
"""

from __future__ import annotations

import os
import sys

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.alice import Alice
from src.bob import Bob
from src.error_estimation import estimate_error_rate
from src.key_sifting import sift_from_alice_and_bob
from src.quantum_channel import QuantumChannel
from noise.bit_flip import BitFlipNoise


def run_error_estimation_experiment(
    num_signals: int = 2000,
    noise_rate: float = 0.06,
    sample_fraction: float = 0.25,
    seed: int = 42,
) -> None:
    """Demonstrate parameter estimation on noisy sifted keys.

    Args:
        num_signals: Number of quantum signals transmitted.
        noise_rate: Noise rate injected via BitFlipNoise.
        sample_fraction: Fraction of sifted key disclosed for parameter testing.
        seed: Random seed for reproducibility.
    """
    print("=" * 76)
    print("       PHASE 9 EXPERIMENT 1: ERROR (PARAMETER) ESTIMATION DEMONSTRATION")
    print("=" * 76)
    print(f"Total Signals:    {num_signals}")
    print(f"Channel Noise:    BitFlipNoise(p = {noise_rate:.2f})")
    print(f"Sample Fraction:  {sample_fraction:.1%} of sifted key\n")

    # 1. Quantum transmission and sifting
    alice = Alice(number_of_qubits=num_signals, seed=seed)
    bob = Bob(seed=seed + 1)
    channel = QuantumChannel(noise=BitFlipNoise(probability=noise_rate, seed=seed + 2))

    transmitted = channel.transmit(alice.get_quantum_signals())
    bob.receive_and_measure(transmitted)

    sifted = sift_from_alice_and_bob(alice, bob)
    print(f"[1] Sifted Key Length: {sifted.sifted_key_length} bits (Alice & Bob shared)")

    # 2. Parameter Estimation
    est_res = estimate_error_rate(
        alice_sifted_key=sifted.alice_sifted_key,
        bob_sifted_key=sifted.bob_sifted_key,
        sample_fraction=sample_fraction,
        seed=seed + 3,
    )

    print("\n[2] Parameter Estimation Outcome:")
    print(f"  - Disclosed Test Bits:      {est_res.num_test_bits} positions ({sample_fraction:.1%})")
    print(f"  - Discrepancies in Sample:  {est_res.num_test_errors} bit errors")
    print(f"  - Estimated Channel QBER:   {est_res.estimated_qber_percentage:.2f}%")
    print(f"  - Sample Disclosed Positions (first 10): {est_res.test_positions[:10]}...")

    # 3. Key Pruning
    print("\n[3] Classical Security Pruning:")
    print(f"  - Disclosed bits permanently discarded from remaining key.")
    print(f"  - Remaining Undisclosed Key Length: {est_res.remaining_key_length} bits")
    print(f"  - Preservation: {est_res.remaining_key_length} + {est_res.num_test_bits} = {sifted.sifted_key_length}")

    print("\n" + "=" * 76)
    print("Conclusion: Error estimation provides an unbiased estimate of channel QBER")
    print("while strictly preserving the privacy of the remaining undisclosed key bits.")
    print("=" * 76)


if __name__ == "__main__":
    run_error_estimation_experiment()
