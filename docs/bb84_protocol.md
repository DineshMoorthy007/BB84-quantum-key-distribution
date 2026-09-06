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

## 2.1 Phase 2 — Quantum Primitives

This section details the fundamental quantum-mechanical building blocks implemented in `src/quantum_primitives.py`.

### 1. Qubit
A **qubit** (quantum bit) is the fundamental unit of quantum information, formalized as a normalized state vector $|\psi\rangle$ in a two-dimensional complex Hilbert space $\mathbb{C}^2$:
$$|\psi\rangle = \alpha |0\rangle + \beta |1\rangle, \quad \alpha, \beta \in \mathbb{C}, \quad |\alpha|^2 + |\beta|^2 = 1$$
Unlike a classical bit which is strictly $0$ or $1$, a qubit can exist in a linear combination of basis states prior to measurement.

### 2. Computational ($Z$) Basis
The computational basis comprises the orthonormal eigenstates $\{|0\rangle, |1\rangle\}$ of the Pauli-$Z$ operator ($\sigma_z$):
$$\sigma_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}, \quad |0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad |1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$$
In BB84, bit `0` maps to $|0\rangle$ and bit `1` maps to $|1\rangle$.

### 3. Hadamard ($X$) Basis
The diagonal or Hadamard basis comprises the orthonormal eigenstates $\{|+\rangle, |-\rangle\}$ of the Pauli-$X$ operator ($\sigma_x$):
$$\sigma_x = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad |+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \quad |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$$
In BB84, bit `0` in the $X$-basis maps to $|+\rangle$ and bit `1` maps to $|-\rangle$.

### 4. Superposition
**Superposition** is the linear combination of multiple quantum states with complex probability amplitudes. The Hadamard states $|+\rangle$ and $|-\rangle$ are coherent, equal superpositions of the computational basis states $|0\rangle$ and $|1\rangle$ with definite relative phases ($0$ and $\pi$ respectively).

### 5. Quantum Logic Gates
- **Pauli-$X$ Gate (NOT Gate)**:
  Flips computational basis states: $X|0\rangle = |1\rangle$ and $X|1\rangle = |0\rangle$. Used to prepare bit `1` in the $Z$-basis, and as the precursor for preparing $|-\rangle$.
  $$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$$
- **Hadamard ($H$) Gate**:
  Creates and inverts equal superpositions:
  $$H|0\rangle = |+\rangle, \quad H|1\rangle = |-\rangle, \quad H|+\rangle = |0\rangle, \quad H|-\rangle = |1\rangle$$
  $$H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$
  The $H$ gate bridges the computational and diagonal bases, acting as both state preparer and measurement basis rotator.

### 6. Quantum Measurement
Measurement in quantum mechanics is non-unitary and projective (von Neumann measurement). When measuring along an observable $M = \sum_m m P_m$:
- The probability of obtaining eigenvalue $m$ is $P(m) = \langle \psi | P_m | \psi \rangle$.
- Post-measurement, the state irreversibly collapses to the projector subspace: $|\psi'\rangle = \frac{P_m |\psi\rangle}{\sqrt{P(m)}}$.

### 7. Why BB84 Uses Two Bases
If Alice and Bob communicated using only a single basis (e.g., $Z$), an eavesdropper could measure every photon in $Z$, record the bit without disturbance, and resend the state undetected. By introducing two **mutually unbiased bases** ($Z$ and $X$), Alice and Bob force Eve to guess the basis. Because non-orthogonal quantum states cannot be cloned or distinguished with certainty, measurement in the wrong basis inevitably alters the state.

### 8. Probabilistic Outcomes in the Wrong Basis
Because the $Z$ and $X$ bases are mutually unbiased:
$$|\langle 0 | + \rangle|^2 = |\langle 0 | - \rangle|^2 = |\langle 1 | + \rangle|^2 = |\langle 1 | - \rangle|^2 = \frac{1}{2}$$
When a state prepared in one basis is measured in the conjugate basis (e.g., measuring $|+\rangle$ in the $Z$-basis), the outcome is fundamentally non-deterministic: either eigenvalue ($0$ or $1$) occurs with exactly $50\%$ probability. This mathematical property is what produces the telltale $25\%$ error rate when an eavesdropper intercepts and resends in randomly chosen bases.

---

## 2.2 Phase 3 — Alice

The Alice component (`src/alice.py`) implements the sender role in the BB84 protocol, executing the quantum state preparation stage.

### 1. Why Alice Generates Random Bits
The ultimate goal of QKD is to establish a shared one-time pad or symmetric encryption key. A cryptographic key must possess maximum information entropy ($H(K) = |K|$); any deterministic pattern or predictability allows an adversary to infer key bits without measuring photons. Alice therefore generates uniformly distributed, uncorrelated binary values $a_i \in \{0, 1\}$.

### 2. Why Alice Randomly Selects Between X and Z Bases
Alice independently and uniformly chooses a basis $b_{A, i} \in \{Z, X\}$ for each bit. Random basis selection ensures that an eavesdropper cannot know in advance which basis was used to prepare any given photon. Because the two bases are mutually unbiased, an eavesdropper measuring in the wrong basis inevitably induces quantum state collapse and introduces detectable errors ($25\%$ QBER).

### 3. How the Bit + Basis Pair Determines the Quantum State
Each bit $a_i$ is mapped to a quantum state $|\psi_i\rangle$ according to Alice's basis choice $b_{A, i}$:
- $(0, Z) \to |0\rangle$: Ground computational state
- $(1, Z) \to |1\rangle$: Excited computational state (via Pauli-$X$)
- $(0, X) \to |+\rangle$: Symmetric superposition (via Hadamard $H$)
- $(1, X) \to |-\rangle$: Anti-symmetric superposition (via $X$ then $H$)

### 4. Why Alice Must Keep Her Bits and Bases Private
Alice's classical sequences are her strictly guarded private state:
- If Alice revealed her **bits** prematurely, no quantum transmission would be secret.
- If Alice revealed her **bases** prior to Bob's measurement, an eavesdropper monitoring the classical channel could intercept the photon, measure in the known basis with $0\%$ error, and forward the unperturbed state to Bob completely undetected.
Alice only reveals her basis choices during the **classical basis reconciliation stage**, after Bob confirms receipt and measurement of all transmitted qubits.

### 5. Why Randomness is Fundamental in BB84
Randomness is required at two levels:
1. **Bit entropy**: Ensures the final shared key is cryptographically secure and incompressible.
2. **Basis unpredictability**: Prevents side-channel basis prediction by Eve. Pseudo-random generators must use independent, reproducible local seeds for scientific analysis, while production QKD relies on Quantum Random Number Generators (QRNGs).

### 6. Connection to the Bob Component
The Alice module encapsulates private classical information while exposing a clean quantum transmission interface:
- **Transmitted Data**: A list of independent `QuantumCircuit` carrier objects sent through the quantum channel.
- **Shielded Data**: Alice's internal bit array $A_{\text{raw}}$ and basis array $B_A$ remain sealed.
In Phase 4, Bob receives these quantum circuits, generates his own independent random basis sequence $B_B$, performs projective measurements along $B_B$, and records his measured outcomes $B_{\text{raw}}$ without having seen Alice's bases.

---

## 2.3 Phase 4 — Bob and Quantum Transmission

The Bob component (`src/bob.py`) and Quantum Channel (`src/quantum_channel.py`) establish the receiver and transmission layers of BB84.

### 1. Independent Basis Selection by Bob
Bob independently selects a random measurement basis $b_{B, i} \in \{Z, X\}$ for every incoming quantum carrier. Like Alice, Bob uses a local, reproducible pseudo-random number generator, guaranteeing that basis choices are uncorrelated between sender and receiver.

### 2. Information Asymmetry (Bob Operates Blind)
Bob possesses no prior knowledge of Alice's basis choices or bit values. The transmission of quantum states occurs before any classical communication regarding bases. This chronological separation is vital: if Bob knew the bases in advance, an eavesdropper listening to the classical channel could also discover them.

### 3. Projective Measurement Along Bob's Basis
Upon receiving each single-qubit quantum state from the channel, Bob performs a projective quantum measurement along his chosen basis:
- If $b_B = Z$: Measurement is performed in the computational basis $\{|0\rangle, |1\rangle\}$.
- If $b_B = X$: A Hadamard rotation $H$ is applied immediately before measurement, transforming $\{|+\rangle, |-\rangle\}$ onto $\{|0\rangle, |1\rangle\}$.
Bob records only the sequential index $i$, basis $b_{B, i}$, and classical outcome $r_i \in \{0, 1\}$ in an isolated `BobMeasurement` record.

### 4. Deterministic Bit Recovery on Matching Bases
In an ideal, noiseless channel without eavesdropping:
- When $b_A = Z$ and $b_B = Z$:
  - Alice sends $|0\rangle \implies$ Bob measures $0$ with probability $1.0$.
  - Alice sends $|1\rangle \implies$ Bob measures $1$ with probability $1.0$.
- When $b_A = X$ and $b_B = X$:
  - Alice sends $|+\rangle \implies$ Bob rotates $H|+\rangle = |0\rangle \implies$ measures $0$ with probability $1.0$.
  - Alice sends $|-\rangle \implies$ Bob rotates $H|-\rangle = |1\rangle \implies$ measures $1$ with probability $1.0$.
Whenever Alice and Bob select the same basis ($b_A = b_B$), their classical bits are strictly identical.

### 5. Probabilistic Outcomes on Mismatched Bases
When Alice and Bob select conjugate bases ($b_A \neq b_B$):
- Alice sends a $Z$-eigenstate ($|0\rangle$ or $|1\rangle$), and Bob measures in $X$. The state in Bob's basis is an equal superposition $\frac{|+\rangle \pm |-\rangle}{\sqrt{2}}$, yielding outcome $0$ or $1$ each with $50\%$ probability.
- Alice sends an $X$-eigenstate ($|+\rangle$ or $|-\rangle$), and Bob measures in $Z$. The state is $\frac{|0\rangle \pm |1\rangle}{\sqrt{2}}$, yielding outcome $0$ or $1$ each with $50\%$ probability.
*Crucial Principle*: A basis mismatch is **not** an error or transmission fault; it is an intrinsic consequence of quantum complementarity and mutual unbiasedness.

### 6. Architectural Role of the Quantum Channel
The `QuantumChannel` abstraction completely decouples physical transmission from sender and receiver logic:
- Alice produces quantum circuits and pushes them into `QuantumChannel.transmit()`.
- The channel propagates physical states and returns copies to Bob.
- This design cleanly encapsulates physical effects: future phases will introduce eavesdropper tapping (Eve) and channel noise channels directly into `QuantumChannel` without modifying either `Alice` or `Bob`.

### 7. Why Basis Reconciliation Must Happen Later
Alice and Bob cannot reconcile their bases until after all quantum signals have arrived and been measured. Announcing bases during quantum transmission would allow an eavesdropper to measure in the correct basis without inducing disturbance. Only once the quantum channel transmission is finalized do Alice and Bob publicly announce their basis sequences over an authenticated classical channel.

### 8. Why QBER Cannot Be Calculated Before Sifting
Quantum Bit Error Rate (QBER) measures transmission fidelity and eavesdropping disturbance, defined as the error rate on **matched-basis** transmissions. Across all raw signals, approximately $50\%$ have mismatched bases which inherently disagree half the time (introducing an artificial $25\%$ raw discrepancy). Calculating error rates before discarding mismatched bases produces meaningless statistics. True QBER estimation requires identifying matched-basis indices during basis sifting in Phase 5.

---

## 2.4 Phase 5 — Basis Reconciliation and Key Sifting

The key sifting module (`src/key_sifting.py`) implements classical basis reconciliation, establishing shared raw keys between Alice and Bob.

### 1. Why Alice and Bob Compare Bases
Alice and Bob independently select random bases ($Z$ or $X$) for each photon. Quantum measurement in the conjugate basis yields purely random outcomes ($50\%$ probability of matching Alice's bit). To distill a correlated key, they publicly announce their basis sequences $B_A$ and $B_B$ over an authenticated classical channel and determine which positions were measured in the same basis ($b_{A, i} = b_{B, i}$).

### 2. Why Bit Values Are Never Announced
Revealing classical bit values over the public channel would destroy cryptographic secrecy. An eavesdropper monitoring the channel would instantly learn the key. Alice and Bob announce **only** the basis names (`"Z"` or `"X"`), never their bits or measured outcomes ($0$ or $1$).

### 3. Why Mismatched Bases Are Discarded
When Alice and Bob select different bases (e.g., Alice encodes in $Z$ and Bob measures in $X$), the measurement is a projective projection onto an equal superposition. The outcome carries zero mutual information regarding Alice's prepared bit. Discarding these positions is mandatory to remove unaligned, uninformative data.

> [!IMPORTANT]
> **Basis Mismatch vs. Bit Error**:
> A basis mismatch is **not** a bit error. A mismatch is an expected physical byproduct of independent, random basis selection. True bit errors occur only at indices where bases **matched** but the measured bit disagrees with the prepared bit.

### 4. Survival Rate (The 50% Sifting Ratio)
Because Alice and Bob select between two bases uniformly and independently:
$$P(b_{A, i} = b_{B, i}) = P(Z, Z) + P(X, X) = \left(\frac{1}{2} \times \frac{1}{2}\right) + \left(\frac{1}{2} \times \frac{1}{2}\right) = \frac{1}{2} = 50\%$$
Over a sufficiently large transmission (e.g., $N \ge 1000$ signals), the observed sifting ratio:
$$\text{Sifting Ratio} = \frac{|\text{Matching Indices}|}{N} \approx 0.50$$
approximately half the transmitted signals survive basis sifting.

### 5. Definition of the Sifted Key
The **sifted key** is the sub-sequence of bits retained by Alice ($K_A^{\text{sifted}}$) and Bob ($K_B^{\text{sifted}}$) at the matching basis positions $\{i \mid b_{A, i} = b_{B, i}\}$:
$$K_A^{\text{sifted}} = \{a_i \mid b_{A, i} = b_{B, i}\}, \quad K_B^{\text{sifted}} = \{r_i \mid b_{A, i} = b_{B, i}\}$$
In an ideal, noiseless channel without eavesdropping, $K_A^{\text{sifted}} = K_B^{\text{sifted}}$ with $100\%$ fidelity.

### 6. Why Sifted Keys Are Not Yet Final Secure Keys
The sifted key is an intermediate stage, not the final secret key:
- **Imperfections & Noise**: Real physical channels introduce thermal noise, detector dark counts, and fiber birefringence, causing bit errors even on matched bases.
- **Potential Eavesdropping**: An eavesdropper intercepting signals introduces errors into the sifted key.
- **Information Leakage**: Post-processing error correction leaks parity bits to the public channel.
Therefore, the sifted key must undergo error rate testing (QBER), information reconciliation, and privacy amplification before becoming a secure cryptographic key.

### 7. Why QBER is Evaluated After Sifting
Evaluating error rates on unsifted signals would conflate basis mismatch randomness ($50\%$ disagreement on half the signals) with actual channel noise and eavesdropping disturbance. True Quantum Bit Error Rate (QBER) is strictly defined over the **sifted key**:
$$\text{QBER} = \frac{1}{|K^{\text{sifted}}|} \sum_{j} (K_{A, j}^{\text{sifted}} \oplus K_{B, j}^{\text{sifted}})$$
Evaluating QBER on sifted keys will be implemented in Phase 6.

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
