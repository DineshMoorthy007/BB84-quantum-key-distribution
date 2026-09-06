# BB84 Quantum Key Distribution Protocol

## 1. Introduction

Proposed in 1984 by Charles H. Bennett and Gilles Brassard, the **BB84 protocol** is the first quantum cryptographic protocol. It enables two communicating parties, traditionally designated **Alice** (sender) and **Bob** (receiver), to establish a shared, secret random key over an insecure quantum channel and an authenticated public classical channel.

Security relies on the fundamental laws of quantum mechanics—specifically, the **no-cloning theorem** (Wootters & Zurek, 1982) and the disturbance induced by projective measurement on non-orthogonal quantum states (Heisenberg uncertainty).

---

## 2. Mathematical Foundations and Bases

The protocol employs four quantum states spanning two mutually unbiased bases (MUBs) in a two-dimensional Hilbert space $\mathcal{H}_2$:

### Computational Basis ($Z$-basis)
$$\{|0\rangle, |1\rangle\}$$
$$\sigma_z |0\rangle = +1|0\rangle, \quad \sigma_z |1\rangle = -1|1\rangle$$

- Bit 0: $|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}$
- Bit 1: $|1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$

### Diagonal / Hadamard Basis ($X$-basis)
$$\{|+\rangle, |-\rangle\}$$
$$\sigma_x |+\rangle = +1|+\rangle, \quad \sigma_x |-\rangle = -1|-\rangle$$

- Bit 0: $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = H|0\rangle$
- Bit 1: $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = H|1\rangle$

### Mutual Unbiasedness
For any state $|\psi_Z\rangle \in Z$ and $|\phi_X\rangle \in X$:
$$|\langle \psi_Z | \phi_X \rangle|^2 = \frac{1}{2}$$

A measurement in the wrong basis yields an outcome completely uncorrelated with the prepared state, producing uniform randomness ($50\%$ probability for each eigenvalue).

---

## 3. Protocol Execution Steps

1. **State Preparation (Alice)**:
   - Alice generates a random bit sequence $A_{\text{raw}} \in \{0, 1\}^N$.
   - Alice chooses a random basis sequence $B_A \in \{Z, X\}^N$.
   - Alice prepares $N$ independent single-photon states according to her bit and basis choices.

2. **Quantum Transmission**:
   - Alice transmits the prepared qubits across the quantum channel to Bob.

3. **Measurement (Bob)**:
   - For each incoming photon, Bob selects a measurement basis $B_B \in \{Z, X\}^N$ uniformly at random.
   - Bob performs projective measurement along his chosen basis, recording measured outcomes as $B_{\text{raw}} \in \{0, 1\}^N$.

4. **Basis Reconciliation (Sifting)**:
   - Over the public classical channel, Alice and Bob announce their basis sequences $B_A$ and $B_B$ (never their bit values).
   - They retain only the indices $i$ where $B_A[i] = B_B[i]$.
   - Under uniform random selection, approximately $50\%$ of transmitted bits are retained, forming the **sifted key**.

5. **Error Estimation (QBER)**:
   - Alice and Bob publicly compare a randomly sampled subset of their sifted keys ($k$ test bits).
   - The Quantum Bit Error Rate (QBER) is evaluated:
     $$\text{QBER} = \frac{\text{Number of Discrepant Test Bits}}{k}$$
   - If $\text{QBER} < \text{Threshold}$ (typically $\approx 11\%$ for unconditional security bounds under one-way classical post-processing), they proceed to post-processing.
   - Otherwise, the channel is considered compromised or excessively noisy, and the key is aborted.

6. **Post-Processing (Reconciliation & Privacy Amplification)**:
   - Information reconciliation corrects remaining errors in the unannounced key bits (e.g., Cascade or LDPC).
   - Privacy amplification applies universal hash functions to shrink the key, eliminating any partial information leaked to Eve or through public error correction.

---

## 4. Eavesdropping: Intercept-Resend Attack

Under an **intercept-resend** attack:
- An eavesdropper (**Eve**) intercepts each qubit in transit.
- Eve chooses a basis $B_E \in \{Z, X\}$ at random and measures the qubit.
- Eve prepares a new qubit in the state corresponding to her measurement result and forwards it to Bob.

### Error Analysis on Sifted Bits:
- Alice and Bob match bases with probability $P(B_A = B_B) = 1/2$.
- When $B_A = B_B$:
  - Eve chose the correct basis ($B_E = B_A$) with probability $1/2$. No error is introduced: Bob's result matches Alice's with probability $1$.
  - Eve chose the wrong basis ($B_E \neq B_A$) with probability $1/2$. The re-prepared state is an equal superposition in Bob's basis. Bob obtains the wrong bit with probability $1/2$.
- Overall error rate on sifted keys under full intercept-resend:
  $$\text{QBER}_{\text{Eve}} = P(B_E \neq B_A) \times P(\text{Error} \mid B_E \neq B_A) = \frac{1}{2} \times \frac{1}{2} = \frac{1}{4} = 25\%$$

Any intercept-resend attack introduces a detectable $25\%$ error rate into the sifted key in an otherwise ideal channel.

---

## 5. Security & Academic Scope

> [!NOTE]
> **Academic Scope Notice**:
> This simulator models quantum state vectors, unitary evolutions, quantum channel noise operators, and projective measurements.
> While it accurately reproduces empirical error rates and statistical quantum mechanics:
> - It does **not** provide a formal mathematical security proof against coherent/collective attacks in the finite-key regime.
> - Security threshold calculations (e.g., $11\%$ Shor-Preskill bound) are simulated numerically to demonstrate principles of quantum cryptography.
