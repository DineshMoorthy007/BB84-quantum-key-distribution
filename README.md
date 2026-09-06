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

## Project Status

- [x] **Phase 1** — Environment, project architecture, and configuration setup completed.
- [x] **Phase 2** — Fundamental quantum primitives completed (state preparation for |0>, |1>, |+>, |->, projective Z and X basis measurements, statevector analysis, and comprehensive unit tests).
- [x] **Phase 3** — Alice (Sender) component completed (random bit & basis generation, state encoding into `BB84Signal`, private classical state encapsulation, and unit tests).
- [x] **Phase 4** — Bob (Receiver) component & quantum channel transmission completed (independent random basis selection, projective measurement, Alice-to-Bob signal transmission, and integration tests).
- [ ] **Phase 5** — Classical basis reconciliation & key sifting (upcoming).

## Project Structure

```text
bb84-quantum-key-distribution/
├── docs/            # Protocol documentation and theoretical background
├── experiments/     # Parametric study, benchmarks, and demonstration scripts
├── hardware/        # Real quantum device connectors (Qiskit Runtime)
├── noise/           # Quantum channel noise models (depolarizing, bit/phase-flip)
├── results/         # Output artifacts (simulation logs, datasets, plots)
├── simulator/       # Qiskit Aer backend and circuit execution managers
├── src/             # Core protocol logic (Alice, Bob, QuantumChannel, primitives, config)
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


