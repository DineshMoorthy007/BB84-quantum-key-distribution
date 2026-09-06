# BB84 Quantum Key Distribution Simulator

A research-oriented software platform for simulating and experimentally analyzing the BB84 Quantum Key Distribution (QKD) protocol.

## Objective

The project aims to demonstrate how quantum mechanics can be used for secure key distribution and how eavesdropping can be detected through quantum measurement disturbances.

## Planned Features

* BB84 quantum key distribution
* Alice and Bob key generation
* Quantum state preparation
* Z-basis and X-basis encoding
* Quantum measurement
* Basis reconciliation
* Key sifting
* QBER calculation
* Intercept-resend eavesdropping
* Quantum noise simulation
* Eavesdropping detection
* Statistical experiment analysis
* Data visualization
* Privacy amplification
* Optional execution on real quantum hardware

## Technology Stack

* Python
* Qiskit
* Qiskit Aer
* NumPy
* Pandas
* Matplotlib
* Pytest
* Git/GitHub

## Current Implementation Status

- Phase 1 — Project architecture ✓
- Phase 2 — Quantum primitives ✓
- Phase 3 — Alice ✓
- Phase 4 — Bob and quantum channel ✓
- Phase 5 — Basis reconciliation and key sifting ✓
- Phase 6 — QBER analysis ✓
- Phase 7 — Eve intercept-resend attack ✓
- Phase 8 — Quantum noise and noisy channel ✓

## Project Status

- [x] **Phase 1** — Environment, project architecture, and configuration setup completed.
- [x] **Phase 2** — Fundamental quantum primitives completed (state preparation for |0>, |1>, |+>, |->, projective Z and X basis measurements, statevector analysis, and comprehensive unit tests).
- [x] **Phase 3** — Alice (Sender) component completed (random bit & basis generation, state encoding into `BB84Signal`, private classical state encapsulation, and unit tests).
- [x] **Phase 4** — Bob (Receiver) component & quantum channel transmission completed (independent random basis selection, projective measurement, Alice-to-Bob signal transmission, and integration tests).
- [x] **Phase 5** — Classical basis reconciliation & key sifting completed (public basis comparison, matched-basis key filtering, sifting ratio analysis, and unit tests).
- [x] **Phase 6** — Quantum Bit Error Rate (QBER) analysis & security baseline completed (sifted key comparison, diagnostic classical error injection, convergence statistics, and validation plots).
- [x] **Phase 7** — Eve (Eavesdropper) intercept-resend attack completed. The simulator models an intercept-resend eavesdropping attack at the quantum-state level and experimentally evaluates its effect on QBER.
- [x] **Phase 8** — Quantum noise and noisy channel completed. Implemented quantum state-level noise models (Bit-Flip, Phase-Flip, and Depolarizing channels adhering to Qiskit Aer's specification) with integrated channel composition supporting independent Eve + Noise experimentation.
- [ ] **Phase 9** — Classical Post-Processing: Error Correction & Privacy Amplification (upcoming).

## Project Structure

```text
bb84-quantum-key-distribution/
├── docs/            # Protocol documentation and theoretical background
├── experiments/     # Parametric study, benchmarks, and demonstration scripts
├── hardware/        # Real quantum device connectors (Qiskit Runtime)
├── noise/           # Quantum channel noise models (depolarizing, bit/phase-flip)
├── results/         # Output artifacts (simulation logs, datasets, plots)
├── simulator/       # Qiskit Aer backend and circuit execution managers
├── src/             # Core protocol logic (Alice, Bob, Eve, Channel, Sifting, QBER, Error Injection)
├── tests/           # Automated pytest test suites
└── visualization/   # Decoupled plotting routines (Matplotlib)
```

## Running the Demonstrations

Execute the phase-specific educational demonstration scripts:

```bash
# Phase 2 — Quantum Primitives Demonstration
.venv\Scripts\python experiments/phase2_quantum_primitives.py

# Phase 3 — Alice (Sender) Demonstration
.venv\Scripts\python experiments/phase3_alice.py --signals 10 --seed 42

# Phase 4 — Alice -> QuantumChannel -> Bob Transmission Demonstration
.venv\Scripts\python experiments/phase4_alice_bob.py --signals 16 --alice-seed 42 --bob-seed 99

# Phase 5 — Basis Reconciliation & Key Sifting Demonstration
.venv\Scripts\python experiments/phase5_key_sifting.py --signals 1000 --seed-alice 42 --seed-bob 99

# Phase 6 — QBER Baseline Analysis & Controlled Classical Error Experiment
.venv\Scripts\python experiments/phase6_qber_analysis.py --signals 1000 --seed 42

# Phase 6 — QBER Statistical Convergence Study
.venv\Scripts\python experiments/phase6_statistics.py --error-rate 0.10 --seed 42

# Phase 7 — Experiment 1: No-Eve vs Full-Eve Benchmark
.venv\Scripts\python experiments/phase7_eve_comparison.py

# Phase 7 — Experiment 2: Eve Interception Probability Sweep
.venv\Scripts\python experiments/phase7_eve_probability.py

# Phase 7 — Experiment 3: Statistical Convergence of Intercept-Resend QBER
.venv\Scripts\python experiments/phase7_convergence.py

# Phase 8 — Experiment 1: Quantum Noise Model Comparison
.venv\Scripts\python experiments/phase8_noise_comparison.py

# Phase 8 — Experiment 2: Quantum Noise Parameter Sweep
.venv\Scripts\python experiments/phase8_noise_sweep.py

# Phase 8 — Experiment 3: Basis-Dependent Phase Noise Investigation
.venv\Scripts\python experiments/phase8_phase_noise_basis.py

# Phase 8 — Experiment 4: Eavesdropping vs. Environmental Quantum Noise
.venv\Scripts\python experiments/phase8_eve_vs_noise.py

# Phase 8 — Experiment 5: Statistical Variability of Quantum Noise
.venv\Scripts\python experiments/phase8_statistics.py
```





## Running Tests

Run the full automated test suite using the virtual environment:

```bash
# Windows
.venv\Scripts\pytest -v

# Linux / macOS
source .venv/bin/activate && pytest -v
```

## Research Direction

The project experimentally investigates the relationship between eavesdropping, quantum noise, and Quantum Bit Error Rate (QBER) in the BB84 protocol.


