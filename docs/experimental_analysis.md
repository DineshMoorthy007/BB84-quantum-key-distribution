# Phase 10: Comprehensive Experimental Analysis and Security Evaluation

---

## 1. Experimental Methodology

This document presents the empirical benchmark results, statistical evaluations, and security interpretations of the complete **BB84 Quantum Key Distribution (QKD)** simulation framework developed in Phases 1 through 9.

### Experimental Workflow
The simulation and analysis workflow operates on a strict pipeline:
$$\text{Experiment Script} \longrightarrow \text{Machine-Readable CSV Datasets} \longrightarrow \text{Visualization Engine} \longrightarrow \text{Vectorized Figures}$$

Every reported numerical value originates from actual quantum circuit simulations using Qiskit and Qiskit Aer. Theoretical reference curves are computed independently for scientific comparison and are never hardcoded into simulation routines.

---

## 2. Experimental Conditions

The simulation framework evaluates eight distinct physical operational conditions across quantum transmission and classical post-processing:

| Condition Code | Description | Eavesdropping ($p_{\text{eve}}$) | Physical Quantum Noise Model | Noise Strength ($p$ or $\lambda$) |
| :---: | :--- | :---: | :---: | :---: |
| **A** | **Ideal Channel** | $0.00$ (Disabled) | None | $0.00$ |
| **B** | **Eve Only** | $1.00$ (Full Intercept) | None | $0.00$ |
| **C** | **Bit-Flip Noise** | $0.00$ (Disabled) | Pauli-$X$ Channel | $0.05$ |
| **D** | **Phase-Flip Noise** | $0.00$ (Disabled) | Pauli-$Z$ Channel | $0.05$ |
| **E** | **Depolarizing Noise** | $0.00$ (Disabled) | Qiskit Aer Isotropic Channel | $0.05$ |
| **F** | **Eve + Bit-Flip Noise** | $0.50$ | Pauli-$X$ Channel | $0.05$ |
| **G** | **Eve + Phase-Flip Noise**| $0.50$ | Pauli-$Z$ Channel | $0.05$ |
| **H** | **Eve + Depol Noise** | $0.50$ | Qiskit Aer Isotropic Channel | $0.05$ |

---

## 3. Metrics

For every simulation run, the framework collects 16 standard metrics defined as follows:

1. **Total Signals ($N$)**: Total single-photon quantum states prepared and emitted by Alice.
2. **Sifted Key Length ($L_{\text{sifted}}$)**: Number of positions where Alice's and Bob's basis selections coincided ($B_A = B_B$).
3. **Sifting Ratio ($R_{\text{sift}}$)**:
   $$R_{\text{sift}} = \frac{L_{\text{sifted}}}{N} \approx 50\%$$
4. **Test Bits ($k$)**: Number of bits sacrificed without replacement for parameter estimation ($k = \lfloor f_{\text{sample}} \times L_{\text{sifted}} \rfloor$).
5. **Estimated QBER ($\widehat{Q}$)**:
   $$\widehat{Q} = \frac{e_{\text{test}}}{k}$$
6. **Actual QBER ($Q_{\text{actual}}$)**: Ground-truth bit error rate across the entire sifted key before test bit disclosure.
7. **Estimated Error Count ($e_{\text{test}}$)**: Disclosed bit disagreements.
8. **Actual Error Count ($e_{\text{actual}}$)**: Total bit disagreements across the sifted key.
9. **Corrected Bits**: Bit corrections applied to Bob's key during information reconciliation.
10. **Reconciliation Leakage ($\text{leakage}$)**: Public parity bits exchanged during interactive bisection.
11. **Reconciled Key Length ($L_{\text{rec}}$)**: Length of remaining key post-reconciliation ($L_{\text{rec}} = L_{\text{sifted}} - k$).
12. **Final Secret Key Length ($m$)**: Distilled key length after universal Toeplitz hashing ($m = 0$ if aborted).
13. **Final Secret Key Rate ($R_{\text{secret}}$)**:
   $$R_{\text{secret}} = \frac{m}{N}$$
14. **Compression Ratio**: Ratio of final secret key length to reconciled key length ($m / L_{\text{rec}}$).
15. **Accepted**: Boolean flag indicating whether $\widehat{Q} \le Q_{\text{threshold}}$ (where $Q_{\text{threshold}} = 11.0\%$).
16. **Final Keys Match**: Boolean verifying $K_{\text{Alice}} = K_{\text{Bob}}$ for all distilled bits.

---

## 4. Statistical Methodology

### Wilson Score Confidence Intervals
Because error estimation samples discrete Bernoulli trials, the normal (Wald) approximation interval severely under-covers when error counts are small or sample sizes are finite. The framework calculates two-sided $95\%$ Wilson score confidence intervals:

$$\widehat{p} = \frac{e}{n}, \quad z \approx 1.95996$$
$$\text{CI}_{95\%} = \frac{\widehat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\widehat{p}(1-\widehat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

Boundary properties:
- When $e = 0$, the interval yields $[0.0, \frac{z^2}{n + z^2}]$ rather than degenerating to zero width.
- When $e = n$, the interval upper bound strictly clamps to $1.0$.

### Sample Descriptive Statistics
Across multi-trial batches, the framework computes Bessel-corrected sample standard deviations ($s = \sqrt{\frac{1}{M-1} \sum (x_i - \bar{x})^2}$), variance, median, and dynamic range $[\min, \max]$.

---

## 5. Eve Eavesdropping Analysis

In an intercept-resend attack, Eve measures flying qubits in randomly chosen bases ($Z$ or $X$) and re-prepares replacements.

### Theoretical Prediction
When Alice and Bob select the same basis, Eve chooses the same basis with probability $1/2$ (introducing no disturbance) and the conjugate basis with probability $1/2$. In the conjugate basis, state projection causes Bob to measure an incorrect bit with probability $1/2$. Therefore, the expected asymptotic QBER is:
$$Q_{\text{theory}}(p_{\text{eve}}) = p_{\text{eve}} \times \left(\frac{1}{2} \times 0 + \frac{1}{2} \times \frac{1}{2}\right) = p_{\text{eve}} \times 25.0\%$$

### Empirical Sweep Results (11 Points, $M = 8$ Trials Each)

| Eve Probability ($p_{\text{eve}}$) | Measured QBER ($\pm \sigma$) | Theoretical Reference | Residual | 95% Wilson CI | Acceptance Rate | Final Key Rate |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.00** | $0.00\% \pm 0.00\%$ | $0.00\%$ | $+0.00\%$ | $[0.00\%, 0.40\%]$ | **100%** | **29.78%** |
| **0.10** | $1.90\% \pm 1.30\%$ | $2.50\%$ | $-0.60\%$ | $[1.19\%, 2.95\%]$ | **100%** | **24.88%** |
| **0.20** | $4.82\% \pm 2.03\%$ | $5.00\%$ | $-0.18\%$ | $[3.65\%, 6.40\%]$ | **88%** | **8.23%** |
| **0.30** | $8.52\% \pm 2.78\%$ | $7.50\%$ | $+1.02\%$ | $[6.91\%, 10.46\%]$ | **62%** | **0.27%** |
| **0.40** | $9.65\% \pm 2.03\%$ | $10.00\%$ | $-0.35\%$ | $[7.95\%, 11.69\%]$ | **38%** | **0.03%** |
| **0.50** | $12.87\% \pm 3.23\%$ | $12.50\%$ | $+0.37\%$ | $[10.92\%, 15.16\%]$ | **0% (Aborted)** | **0.00%** |
| **0.60** | $13.57\% \pm 3.25\%$ | $15.00\%$ | $-1.43\%$ | $[11.52\%, 15.83\%]$ | **0% (Aborted)** | **0.00%** |
| **0.70** | $19.52\% \pm 4.55\%$ | $17.50\%$ | $+2.02\%$ | $[17.12\%, 22.16\%]$ | **0% (Aborted)** | **0.00%** |
| **0.80** | $20.44\% \pm 2.98\%$ | $20.00\%$ | $+0.44\%$ | $[17.99\%, 23.13\%]$ | **0% (Aborted)** | **0.00%** |
| **0.90** | $21.35\% \pm 4.07\%$ | $22.50\%$ | $-1.15\%$ | $[18.82\%, 23.98\%]$ | **0% (Aborted)** | **0.00%** |
| **1.00** | $23.96\% \pm 4.41\%$ | $25.00\%$ | $-1.04\%$ | $[21.38\%, 26.79\%]$ | **0% (Aborted)** | **0.00%** |

### Observations
1. **Linear Empirical Scaling**: Measured QBER closely tracks the $25.0\%$ theoretical slope ($R^2 > 0.99$).
2. **Threshold Cutoff**: At $p_{\text{eve}} = 0.44$, the theoretical error rate crosses $11.0\%$. In simulation, acceptance drops sharply from $88\%$ at $p_{\text{eve}}=0.20$ to $0\%$ at $p_{\text{eve}} \ge 0.50$.
3. **No Hardcoded Clamping**: Residual deviations ($\approx \pm 1.0\%$) reflect genuine statistical sampling variance.

---

## 6. Quantum Noise Analysis & Channel Comparison

Environmental decoherence was swept from $p = 0.00$ to $0.20$ across three fundamental physical models.

### Theoretical Predictions
- **Bit-Flip (Pauli-$X$)**: Inverts computational basis ($|0\rangle \leftrightarrow |1\rangle$), leaves Hadamard basis invariant ($X|+\rangle = |+\rangle$, $X|-\rangle = -|-\rangle$). With random basis selection ($50\%$), overall $\text{QBER} = p / 2$.
- **Phase-Flip (Pauli-$Z$)**: Leaves computational basis invariant ($Z|0\rangle = |0\rangle$, $Z|1\rangle = -|1\rangle$), inverts Hadamard basis ($|+\rangle \leftrightarrow |-\rangle$). With random basis selection ($50\%$), overall $\text{QBER} = p / 2$.
- **Depolarizing**: Isotropic channel $\mathcal{E}(\rho) = (1-\lambda)\rho + \lambda \frac{I}{2}$. In Qiskit Aer, $P(X) = P(Y) = P(Z) = \lambda / 4$. The error probability on any basis is $\lambda / 4 + \lambda / 4 = \lambda / 2$.

### Basis Asymmetry Experiment ($p = 0.10, N = 2,000$ Signals, $M = 10$ Trials)

| Noise Model | Measured $Z$-Basis QBER | Measured $X$-Basis QBER | Overall QBER | Asymmetry ($Q_Z - Q_X$) | Physical Mechanism |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Bit-Flip ($p=0.10$)** | **9.02%** | **0.00%** | **4.53%** | **+9.02%** | Bit-flip inverts $Z$; Hadamard states are eigenstates of $X$. |
| **Phase-Flip ($p=0.10$)** | **0.00%** | **10.28%** | **5.14%** | **-10.28%** | Phase-flip inverts $X$; Computational states are eigenstates of $Z$. |
| **Depolarizing ($\lambda=0.10$)** | **5.04%** | **5.16%** | **5.11%** | **-0.12%** | Isotropic decoherence distributes errors symmetrically. |

---

## 7. Compound Eve + Noise Interaction Analysis

The simulation matrix ($5 \times 5$ grid of $p_{\text{eve}} \in [0.0, 1.0] \times \lambda \in [0.0, 0.20]$) demonstrates that eavesdropping and environmental noise compound non-linearly:

$$Q_{\text{combined}} \approx Q_{\text{eve}} + Q_{\text{noise}} - 2 Q_{\text{eve}} Q_{\text{noise}}$$

### Key Matrix Findings
- **Clean Channel ($\lambda = 0.00, p_{\text{eve}} = 0.00$)**: $0.00\%$ QBER $\to 100\%$ acceptance $\to 29.08\%$ secret key rate.
- **Benign Environmental Noise ($\lambda = 0.05, p_{\text{eve}} = 0.00$)**: $1.63\%$ QBER $\to 100\%$ acceptance $\to 23.78\%$ secret key rate.
- **Weak Eavesdropping + Noise ($p_{\text{eve}} = 0.25, \lambda = 0.05$)**: $7.41\%$ QBER $\to 100\%$ acceptance $\to 3.18\%$ secret key rate.
- **Critical Threshold Crossing**: Once combined error exceeds $11.0\%$ (e.g., $p_{\text{eve}} = 0.25, \lambda = 0.10 \implies Q = 13.07\%$), acceptance collapses to $20\%$ and drops to $0\%$ thereafter, preventing key leakage.

---

## 8. Key Generation & Classical Post-Processing Pipeline

The post-processing stage compresses raw transmission into secret key material through four successive filters:

$$\text{Raw Signals } (N) \xrightarrow{\text{Key Sifting}} \text{Sifted Key } (L_{\text{sifted}} \approx 0.5 N) \xrightarrow{\text{Error Estimation}} \text{Remaining Key } (L_{\text{rec}} = 0.8 L_{\text{sifted}}) \xrightarrow{\text{Privacy Amplification}} \text{Secret Key } (m)$$

### Information Reconciliation
- Interactive block parity exchange identifies blocks with odd parity and bisects them via binary search.
- Multi-pass permutation ($4$ passes) resolves error pairs that cancel in single-block parity.
- Public parity exchange is tracked precisely: under $2\%$ QBER, reconciliation leaks $\approx 70 - 100$ classical bits per 1,000 signals.

### Privacy Amplification
- Compresses the reconciled key using an $m \times n$ binary Toeplitz matrix under $\text{GF}(2)$ arithmetic:
  $$K_{\text{secret}} = (M_{\text{Toeplitz}} \cdot K_{\text{reconciled}}) \pmod 2$$
- Sizing bound:
  $$m \le n \cdot (1 - 2 h_2(\widehat{Q})) - \text{leakage}_{\text{parity}}$$
- Across all accepted runs, Alice and Bob achieve **100% final secret key identity** ($K_{\text{Alice}} = K_{\text{Bob}}$).

---

## 9. Security Interpretation & Shor-Preskill Threshold

### Why QBER is an Essential Indicator
In BB84, legitimate parties have no direct physical observation of the transmission medium. The Quantum Bit Error Rate (QBER) serves as the primary diagnostic observable. By the No-Cloning Theorem, any eavesdropper attempting to gain information necessarily perturbs the carrier states, translating quantum measurement disturbance into observable classical bit errors.

### The Problem of Indistinguishability
A fundamental principle demonstrated by our simulations is that **QBER alone cannot identify the physical cause of errors**:
- An observed QBER of $5.0\%$ could be caused by an environmental depolarizing noise rate of $\lambda = 0.10$ with **no eavesdropper present**.
- The same $5.0\%$ QBER could be caused by an eavesdropper intercepting $p_{\text{eve}} = 0.20$ of the carriers in an otherwise **noiseless channel**.

Because Alice and Bob cannot distinguish benign channel decoherence from malicious interception, conservative QKD protocols must make the worst-case assumption: **all observed errors are attributed entirely to Eve**.

### Security Threshold
Under one-way classical post-processing, the asymptotic Shor-Preskill security bound establishes that secret key distillation is mathematically possible only when:
$$\text{QBER} < 11.0\%$$
Above this threshold, Eve's potential mutual information exceeds the mutual information between Alice and Bob, making it impossible to distill secret bits via privacy amplification. Our simulator strictly aborts key generation whenever estimated QBER exceeds $11.0\%$.

---

## 10. Limitations & Academic Scope

1. **Simulated Environment**: Qiskit Aer simulates single-photon statevectors and projective measurements. It does not model fiber chromatic dispersion, dark count rates in avalanche photodiodes (APDs), or dead-time pulse stacking.
2. **Finite-Key Effects**: In production QKD, finite-sample fluctuations require smooth min-entropy estimators and composable security parameters ($\epsilon_{\text{sec}}, \epsilon_{\text{corr}}$).
3. **Classical Channel Authentication**: We assume public classical discussions (basis announcements, parity exchanges) occur over an authenticated channel. In commercial systems, this requires information-theoretic Wegman-Carter MACs.
4. **Not a Formal Proof**: This simulator accurately demonstrates physical principles, error statistics, and algorithmic post-processing, but does not constitute a formal composable mathematical security proof.

---

## 11. Reproducibility & Master-Seed Hierarchy

To ensure scientific reproducibility, all experimental runs derive deterministic, non-overlapping random streams from a master integer seed using NumPy's `SeedSequence`:

$$\text{Master Seed } S \longrightarrow \text{SeedSequence}(S, \text{trial\_idx}) \longrightarrow \begin{cases} \text{seed}_{\text{Alice}} \\ \text{seed}_{\text{Bob}} \\ \text{seed}_{\text{Eve}} \\ \text{seed}_{\text{Noise}} \\ \text{seed}_{\text{Estimation}} \\ \text{seed}_{\text{Reconciliation}} \\ \text{seed}_{\text{Privacy}} \end{cases}$$

Re-running any experiment script with the identical configuration and master seed reproduces bit-for-bit identical CSV measurement records.
