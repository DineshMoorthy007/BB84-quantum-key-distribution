# Experiments Module

## Purpose

The `experiments/` directory houses runnable benchmark scripts and parametric studies for evaluating the BB84 protocol under diverse experimental conditions.

## Planned Experiment Scenarios

1. **Baseline Ideal Transmission**: Key reconciliation, sifting efficiency (~50%), and QBER = 0 in a lossless, noise-free channel without Eve.
2. **Intercept-Resend Eavesdropping**: Examining theoretical and empirical QBER (~25% in sifted keys) when Eve measures Alice's qubits in randomly chosen bases and resends them.
3. **Quantum Noise Characterization**: Sweeping error probabilities ($p \in [0, 0.3]$) for depolarizing, bit-flip, and phase-flip noise models to establish the baseline error floor.
4. **Distinction Analysis (Eve vs. Noise)**: Multi-parameter sweeps to evaluate error detection thresholds and determine whether a noisy channel can mask an eavesdropper.
5. **Key Sifting and Scalability**: Analyzing key generation rates as a function of transmitted qubit block size ($N$).

## Guidelines

- All experiments must consume `BB84Config` from `src.config`.
- Experiments must accept explicit random seeds to ensure full scientific reproducibility.
- Raw and processed simulation data will be persisted to the `results/` directory (e.g., CSV/JSON).
