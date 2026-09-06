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

---

## 2.5 Phase 6 — QBER Analysis

The QBER module (`src/qber.py`) provides quantitative error estimation across sifted keys, establishing the experimental baseline for the BB84 simulator.

### 1. Definition and Meaning of QBER
The **Quantum Bit Error Rate (QBER)** is the fundamental metric of channel disturbance and transmission fidelity in quantum key distribution. It represents the ratio of discrepant bit positions to the total number of compared sifted bits:
$$\text{QBER} = \frac{\sum_{i=0}^{n-1} |a_i^{\text{sifted}} - b_i^{\text{sifted}}|}{n}$$
where $n = |K^{\text{sifted}}|$.

### 2. Why QBER Operates Exclusively on Sifted Keys
QBER must only be computed after classical basis reconciliation has discarded all mismatched-basis signals. Calculating error rates on raw signals prior to sifting would yield an artificial $\approx 25\%$ error floor caused by quantum measurement randomness in conjugate bases.

### 3. Sifted Key Comparison Methodology
Alice and Bob's sifted keys are compared position-by-position. For every matched position $i \in \{0, \dots, n-1\}$:
- Agreement: $a_i^{\text{sifted}} = b_i^{\text{sifted}} \implies \text{matching\_bits} \mathrel{+}= 1$
- Discrepancy: $a_i^{\text{sifted}} \neq b_i^{\text{sifted}} \implies \text{error\_count} \mathrel{+}= 1$, index recorded in `error_indices`

### 4. Conceptual Distinction: Basis Mismatch vs. Bit Error
In quantum cryptography, basis mismatch and bit error are fundamentally distinct phenomena:
- **Basis Mismatch** ($b_{A, i} \neq b_{B, i}$): Occurs because Alice and Bob choose measurement bases independently. It is an expected consequence of quantum mechanics and is discarded during sifting. It is **not** an error.
- **Bit Error** ($b_{A, i} = b_{B, i}$, but $a_i \neq r_i$): A discrepancy occurring at an aligned basis position. True bit errors arise from channel noise, detector dark counts, or eavesdropping disturbances.

### 5. Why the Ideal Channel Produces Zero QBER
In an ideal, noiseless quantum channel without eavesdropping:
- Every photon is prepared in an exact eigenstate of its basis ($|0\rangle, |1\rangle, |+\rangle, |-\rangle$).
- The state propagates unperturbed through `QuantumChannel`.
- Bob measures along the exact same basis, projecting onto the prepared eigenstate with probability $1.0$.
Consequently, in an unperturbed simulation, $\text{QBER} = 0.00\%$, establishing the required experimental baseline.

### 6. Why Physical QKD Systems Exhibit Nonzero QBER
In practical implementations, real hardware inherently suffers from:
- Single-photon detector dark counts and timing jitter.
- Optical fiber attenuation, polarization drift, and phase decoherence.
- Imperfect state preparation (multi-photon emissions from attenuated lasers).
Standard commercial QKD systems typically exhibit an optical baseline QBER between $1\%$ and $4\%$.

### 7. Why QBER Alone is Not a Complete Security Proof
While QBER is the primary trigger for eavesdropping detection:
- An observed $\text{QBER} < 11\%$ indicates that error correction and privacy amplification can asymptotically extract a secret key under the Shor-Preskill / CSS proof framework.
- However, QBER alone does not account for finite-key statistical fluctuations, side-channel vulnerabilities, multi-photon pulse splitting attacks (PNS), or Trojan-horse attacks. Numerical simulations model physical observables but do not constitute a formal mathematical security proof.

### 8. The Importance of Statistical Sample Size
The observed QBER on a finite sample is a random variable following a binomial distribution. By the Law of Large Numbers, the sample variance scales as $\sigma \propto 1/\sqrt{N_{\text{sifted}}}$. For small sample sizes (e.g., $N=100$), random statistical fluctuations can exceed $2\%$, risking false alarms or undetected eavesdropping. Reliable threshold evaluation requires large sample sizes ($N \ge 1,000$ to $10,000$ bits) or rigorous finite-key confidence bounds.

---

### Classical Error Injection for Validation

Implemented in `src/error_injection.py`:
- **Diagnostic Purpose**: A classical utility designed exclusively to validate the QBER calculation and statistical estimation routines by injecting controlled independent bit flips into a copy of Bob's sifted key at rate $p \in [0.0, 1.0]$.
- **Architectural Boundary**: This is **NOT** a quantum noise model. It operates purely on classical integer arrays and does not alter quantum circuits or state vectors. Physical quantum noise channels are implemented separately in later phases.

---

## 2.6 Phase 7 — Eve Intercept-Resend Attack

The eavesdropping module (`src/eve.py`) implements a genuine quantum intercept-resend attack operating on physical quantum carriers within the transmission channel.

### 1. What an Intercept-Resend Attack Is
In an intercept-resend attack, an eavesdropper (**Eve**) taps the quantum transmission medium between Alice and Bob:
1. Eve intercepts Alice's transmitted single-qubit quantum state before it reaches Bob.
2. Eve performs a projective measurement on the intercepted carrier.
3. Using the measured classical outcome and her chosen basis, Eve prepares a brand new quantum state.
4. Eve forwards this replacement quantum state over the channel to Bob.

### 2. Why Eve Must Measure the Quantum State
By the **No-Cloning Theorem** (Wootters & Zurek, 1982; Dieks, 1982), an unknown, non-orthogonal quantum state cannot be duplicated into an identical copy:
$$U |\psi\rangle |e\rangle \neq |\psi\rangle |\psi\rangle \quad \forall |\psi\rangle$$
Eve cannot make a backup copy of Alice's photon, forward the original to Bob unperturbed, and measure her copy later when bases are announced. To extract any classical information from the flying qubit during transit, Eve is fundamentally forced to perform an immediate quantum measurement.

### 3. Why Eve Cannot Know Alice's Basis in Advance
Alice's basis choices are strictly private classical data stored locally at Alice's station. Alice reveals her basis sequence only during classical basis reconciliation in Phase 5, which occurs **strictly after** Bob has already received and measured all quantum carriers. During transit, Eve faces equal prior probabilities:
$$P(B_A = Z) = P(B_A = X) = \frac{1}{2}$$
Eve has no physical means of anticipating Alice's basis and must guess her measurement basis independently at random.

### 4. Why Measuring in the Wrong Basis Disturbs the State
Quantum mechanics enforces Heisenberg's Uncertainty Principle and Bohr's Complementarity Principle. The computational basis ($Z = \{|0\rangle, |1\rangle\}$) and Hadamard basis ($X = \{|+\rangle, |-\rangle\}$) are **mutually unbiased bases (MUBs)**:
$$|\langle z_i | x_j \rangle|^2 = \frac{1}{2} \quad \forall i, j \in \{0, 1\}$$
If Alice prepares $|0\rangle$ (a $Z$-basis eigenstate) and Eve measures along the $X$-basis:
- The measurement projects the state into either $|+\rangle$ or $|-\rangle$ with equal probability $1/2$.
- The original quantum state is irreversibly disturbed; all phase and identity memory of $|0\rangle$ is erased.

### 5. Why Eve Prepares a Replacement State
Because projective quantum measurement is destructive (or absorbs the single photon in optical channels), Eve must resend a physical quantum carrier forward to Bob; otherwise, the absence of photons would cause complete detector absence at Bob's station. Eve prepares an eigenstate matching her own measurement outcome ($r_E \in \{0, 1\}$) and basis ($B_E \in \{Z, X\}$):
- If Eve measured $0$ in $Z$, she sends $|0\rangle$.
- If Eve measured $1$ in $Z$, she sends $|1\rangle$.
- If Eve measured $0$ in $X$, she sends $|+\rangle$.
- If Eve measured $1$ in $X$, she sends $|-\rangle$.

### 6. Why Alice and Bob Observe Additional Errors
When Alice and Bob later reconcile bases, they retain only trials where their bases coincided ($B_A = B_B$). In an unperturbed channel, Bob's outcome always agrees with Alice's prepared bit. However, when Eve intercepts and chooses the **wrong basis** ($B_E \neq B_A$):
- Eve replaces Alice's eigenstate with an eigenstate of the conjugate basis.
- When Bob measures this replacement in his basis (which matches Alice's $B_B = B_A$), he is measuring a state that is in an equal superposition with respect to his detector.
- Bob obtains an erroneous bit with probability $1/2$.

### 7. Theoretical QBER Under Full Intercept-Resend (25%)
For an ideal BB84 system subject to a full intercept-resend attack ($p_{\text{eve}} = 1.0$), the mathematical error probability on sifted key bits is:
$$P(\text{Eve chooses wrong basis}) = P(B_E \neq B_A) = \frac{1}{2}$$
$$P(\text{Bob error} \mid \text{wrong Eve basis}) = \frac{1}{2}$$
$$P(\text{Bob error} \mid \text{matching Eve basis}) = 0$$
Applying the Law of Total Probability to the sifted key ($B_A = B_B$):
$$\text{QBER} = P(B_E = B_A) \times 0 + P(B_E \neq B_A) \times P(\text{error} \mid B_E \neq B_A) = \frac{1}{2} \times 0 + \frac{1}{2} \times \frac{1}{2} = \frac{1}{4} = 25\%$$
Under partial interception with probability $p \in [0.0, 1.0]$:
$$\text{QBER}(p) = p \times 25.0\%$$
Because standard QKD abort thresholds are typically set between $8\%$ and $11\%$ (Shor-Preskill bound $\approx 11.0\%$), a full intercept-resend attack ($25\% \gg 11\%$) is detected with certainty.

### 8. Statistical Fluctuations in Experimental Simulations
The theoretical $25\%$ QBER represents the infinite-sample mathematical expectation:
$$\mathbb{E}[\text{QBER}] = 0.25$$
In finite simulations, the observed QBER is an empirical average of independent Bernoulli trials. By the Central Limit Theorem:
$$\sigma_{\text{QBER}} = \sqrt{\frac{0.25 \times 0.75}{N_{\text{sifted}}}} = \frac{\sqrt{3/16}}{\sqrt{N_{\text{sifted}}}} \approx \frac{0.433}{\sqrt{N_{\text{sifted}}}}$$
- For $N=500$ signals ($N_{\text{sifted}} \approx 250$), $\sigma \approx 2.74\%$, leading to observed values between $21\%$ and $29\%$.
- For $N=10,000$ signals ($N_{\text{sifted}} \approx 5,000$), $\sigma \approx 0.61\%$, tightly clustering between $24.0\%$ and $26.0\%$.
Our simulator does not hardcode $25\%$; the error rate emerges purely from simulating individual quantum state measurements.

### 9. Eavesdropping-Induced Errors vs. Channel Noise
- **Eavesdropping Disturbances**: Stem from state projection when measuring non-orthogonal quantum states without prior basis knowledge. Eve's disturbance is inherently coupled to the information she extracts.
- **Environmental Channel Noise**: Arises from thermal fluctuations, fiber polarization drift, decoherence, or optical attenuation. Channel noise corrupts states without any intelligent eavesdropper gaining information.
- **Security Implications**: Because Alice and Bob cannot distinguish whether an error originated from Eve or environmental noise, QKD protocols conservatively attribute **all** observed QBER to Eve, guaranteeing information-theoretic security.

> [!NOTE]
> **Idealized Scenario**:
> This analysis assumes an individual, memoryless intercept-resend attack against single-photon states. Advanced collective or coherent quantum attacks (e.g., using quantum memory and entangling probes) are more sophisticated, but the fundamental principle—that non-orthogonal states cannot be measured without disturbance—underpins all QKD security proofs.

---

## 2.7 Phase 8 — Quantum Noise

The quantum noise package (`noise/`) models physical environmental perturbations acting directly on single-qubit quantum states within `QuantumChannel`.

### 1. Why Real Quantum Channels are Noisy
In optical fiber or free-space telecommunications, physical quantum carriers inevitably interact with their ambient environment:
- **Thermal Fluctuations & Mechanical Vibrations**: Induce random optical birefringence, rotating qubit polarization.
- **Material Dispersion & Attenuation**: Causes photon loss and phase jitter.
- **Detector Dark Counts & Inefficiencies**: Introduce spurious measurement clicks.
Consequently, real-world QKD transmissions always exhibit an intrinsic baseline error rate (typically $1\%$ to $4\%$).

### 2. Difference Between Classical Error Injection and Quantum Noise
A fundamental conceptual distinction in this simulator:
```text
Classical Validation Error (Phase 6):
[Alice Sifted Key]  ----------------------------> [Bob Sifted Key]
                                                      ↓
                                           [Flip Classical Integer Bit]

Quantum Channel Noise (Phase 8):
|ψ⟩ (Alice State) -> [Quantum Channel] -> [Quantum Noise Operator] -> |ψ'⟩ -> [Bob Detector] -> Measured Bit
```
- **Classical Error Injection (`src/error_injection.py`)**: A diagnostic testing utility operating on post-measurement integer bit arrays (`0` and `1`). It tests the statistical arithmetic of the QBER module.
- **Quantum Noise (`noise/`)**: Physical quantum channels that operate on single-qubit density matrices and `QuantumCircuit` state representations prior to projective measurement.

### 3. Bit-Flip Noise (Pauli-$X$)
A bit-flip error models an environmental interaction that inverts computational basis states:
$$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad X|0\rangle = |1\rangle, \quad X|1\rangle = |0\rangle$$
With probability $p$, the channel applies a Pauli-$X$ gate; with probability $1-p$, the state passes unchanged.
- **Basis Asymmetry**: $X$ inverts $|0\rangle \leftrightarrow |1\rangle$ in the $Z$-basis. However, in the $X$-basis, $|+\rangle$ and $|-\rangle$ are eigenvectors of $X$: $X|+\rangle = |+\rangle$ and $X|-\rangle = -|-\rangle$ (global phase). Thus, bit-flip noise induces zero bit errors on $X$-basis transmissions, yielding an overall BB84 QBER of $\approx p/2$.

### 4. Phase-Flip Noise (Pauli-$Z$)
A phase-flip error introduces a relative phase shift of $\pi$ between computational basis components:
$$Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}, \quad Z|0\rangle = |0\rangle, \quad Z|1\rangle = -|1\rangle$$
With probability $p$, the channel applies a Pauli-$Z$ gate; with probability $1-p$, the state passes unchanged.

### 5. Why Phase Errors are Basis-Dependent
Phase flips illustrate the principle of quantum complementarity:
- **In the $Z$-Basis**: $Z|0\rangle = |0\rangle$, while $Z|1\rangle = -|1\rangle = e^{i\pi}|1\rangle$. Because global phase factors do not alter projective measurement probabilities ($|\langle 1 | (-|1\rangle)|^2 = 1$), measurements in the $Z$-basis are **completely immune** to phase-flip noise! Observed QBER in the $Z$-basis is strictly $0\%$.
- **In the $X$-Basis**: $Z|+\rangle = |-\rangle$ and $Z|-\rangle = |+\rangle$. Phase noise inverts the $X$-basis eigenstates, converting bit $0 \leftrightarrow 1$. Observed QBER in the $X$-basis equals the noise probability $p$.
- **BB84 Sifted Key**: With $50\%$ of sifted bits measured in $Z$ and $50\%$ in $X$, the average observed QBER is $p/2$.

### 6. Depolarizing Noise (Qiskit Standard Parameterization)
Depolarizing noise models isotropic state degradation towards the maximally mixed state $I/2$.
Adhering to Qiskit Aer's standard `depolarizing_error(lambda, 1)`:
$$\mathcal{E}(\rho) = (1 - \lambda)\rho + \lambda \frac{I}{2} = \left(1 - \frac{3\lambda}{4}\right)\rho + \frac{\lambda}{4}\Big(X\rho X + Y\rho Y + Z\rho Z\Big)$$
Operational probabilities:
- Identity ($I$): $P(I) = 1 - \frac{3\lambda}{4}$
- Pauli-$X$: $P(X) = \frac{\lambda}{4}$
- Pauli-$Y$: $P(Y) = \frac{\lambda}{4}$
- Pauli-$Z$: $P(Z) = \frac{\lambda}{4}$
In both $Z$ and $X$ bases, exactly two of the three Pauli errors induce bit flips ($X$ and $Y$ in $Z$-basis; $Z$ and $Y$ in $X$-basis). Hence, the expected QBER is $\frac{\lambda}{4} + \frac{\lambda}{4} = \frac{\lambda}{2} = 50\% \times \lambda$. Complete depolarization ($\lambda = 1.0$) yields $50\%$ QBER (pure random guessing).

### 7. Why Noise Causes Nonzero QBER
In an ideal channel, state fidelity is $1.0$, producing zero bit errors on matched bases. When quantum noise operators (Pauli $X, Y, Z$) perturb the transmitted states, Bob's measurement basis no longer aligns with the disturbed state's eigenbasis, introducing bit errors into the sifted key.

### 8. Eve-Induced Errors vs. Noise-Induced Errors
- **Eve's Disturbance**: Stem from quantum measurement projection when Eve guesses the wrong basis ($P = 1/2$). Eve's errors are coupled to classical information extraction.
- **Environmental Noise**: Arises from unitary perturbations or random thermal entanglements without any classical information leakage to a third party.

### 9. Why QBER Alone Cannot Distinguish Eve from Channel Noise
Alice and Bob observe only one physical classical observable during sifting: the rate of bit mismatches (QBER).
A measured QBER of $6\%$ could result from:
- A partial eavesdropping attack ($p_{\text{eve}} \approx 24\%$, since $0.24 \times 25\% = 6\%$).
- An unintercepted channel with $12\%$ depolarizing noise ($\lambda / 2 = 6\%$).
- A combination of minor eavesdropping and minor channel noise.
Because Alice and Bob cannot physically discern the origin of errors from QBER alone, information-theoretic security proofs mandate the **worst-case assumption**: all observed QBER is attributed to Eve. If $\text{QBER} > 11\%$ (Shor-Preskill threshold), the protocol aborts immediately.

### 10. Importance of Statistical Repetition
Quantum state preparation, noise application, and measurement are stochastic processes governed by binomial statistics. A single finite trial will fluctuate around the mathematical expectation by $\sigma \approx \sqrt{p(1-p)/N_{\text{sifted}}}$. Multiple independent Monte Carlo repetitions are necessary to characterize mean behavior and experimental variance.

---

## 2.8 Phase 9 — Classical Post-Processing (Error Estimation, Reconciliation & Privacy Amplification)

The classical post-processing layer converts raw sifted keys into identical, information-theoretically secure cryptographic secret keys:
```text
Sifted Keys (Alice & Bob)
         ↓
1. Error Estimation (Disclose test bits, calculate QBER, discard test bits)
         ↓
2. Security Threshold Decision (Accept if QBER <= 11%, else Abort)
         ↓
3. Information Reconciliation (Parity-based error correction & leakage tracking)
         ↓
4. Privacy Amplification (Toeplitz matrix hashing in GF(2))
         ↓
Final Distilled Secret Key (Identical & Unconditionally Secure)
```

### 1. Parameter Estimation
Parameter estimation allows Alice and Bob to infer the Quantum Bit Error Rate (QBER) of the transmission channel without measuring or compromising the entire key:
- **Sampling Subset**: Alice and Bob choose a random subset of bit positions $K_{\text{test}} \subset \{0, \dots, n-1\}$ of size $k$.
- **Why Bits Must Be Revealed**: To compute the exact error count, the values at $K_{\text{test}}$ are publicly exchanged over the classical channel.
- **Permanent Removal**: Because the test bits have been publicly broadcast over the classical channel, they are completely exposed to Eve. Therefore, Alice and Bob **must permanently discard** all disclosed test bits from both keys prior to subsequent post-processing.
- **Unbiased Estimate**: The observed error fraction $\widehat{\text{QBER}} = \frac{e_{\text{test}}}{k}$ serves as an unbiased statistical estimator of channel fidelity.

### 2. Security Decision (Acceptance vs. Rejection)
Alice and Bob compare $\widehat{\text{QBER}}$ against an asymptotic security threshold (e.g., the Shor-Preskill bound $\approx 11.0\%$ for BB84 with one-way classical processing):
- **If $\widehat{\text{QBER}} \le 11.0\%$**: The correlation between Alice and Bob exceeds Eve's potential mutual information. The run is **ACCEPTED**, proceeding to reconciliation and privacy amplification.
- **If $\widehat{\text{QBER}} > 11.0\%$**: Eavesdropping or channel degradation is excessive. Error correction and privacy amplification cannot guarantee a positive secret key rate. The protocol **ABORTS** immediately; no key is issued.

### 3. Information Reconciliation (Parity-Based Error Correction)
Reconciliation corrects discrepancies between Alice's and Bob's remaining keys:
- **Block Parity Checking**: Keys are partitioned into blocks. For each block, Alice sends the 1-bit parity $P = \sum b_i \pmod 2$.
- **Interactive Binary Search**: If parities disagree, an odd number of discrepancies exists. Alice and Bob bisect the block and exchange sub-block parities until a single discordant bit index is isolated.
- **In-Place Correction**: Bob flips his corresponding bit in-place ($b_i \oplus 1$). Bob's key is genuinely corrected through algorithmic localization rather than by replacing Bob's key with Alice's key.
- **Multi-Pass Permutations**: Because blocks with an even number of errors exhibit identical parity, multiple passes with deterministic pseudo-random shuffling are used to disperse paired errors across different blocks.

### 4. Public Information Leakage
Every parity bit announced over the classical channel reveals linear constraints to Eve:
$$\text{Reconciliation Leakage} = \sum (\text{Block Parities}) + \sum (\text{Binary Search Parities})$$
This leaked information compromises key secrecy unless explicitly compensated for during privacy amplification.

### 5. Privacy Amplification & Toeplitz Hashing
Privacy amplification compresses the $n$-bit reconciled key into an $m$-bit final key ($m < n$) using universal hashing:
- **Leftover Hash Lemma**: By hashing with a 2-universal family, Eve's mutual information about the final key is reduced to an exponentially negligible fraction $2^{-s}$.
- **Toeplitz Matrix**: A random binary matrix $M \in \{0, 1\}^{m \times n}$ where each descending diagonal is constant ($M_{i, j} = t_{i - j}$).
- **Binary Arithmetic in $\text{GF}(2)$**:
  $$K_{\text{final}} = (M \cdot K_{\text{reconciled}}) \pmod 2$$
  The operation is computed strictly modulo 2 with zero floating-point representation.
- **Identical Matrix**: Alice and Bob use the same public random seed to generate $M$, ensuring that identical reconciled inputs produce identical final secret keys.

### 6. Limitations & Academic Scope Notice
> [!IMPORTANT]
> **Academic Scope Notice**:
> This simulator demonstrates the conceptual workflow of BB84 classical post-processing. It is not a production-grade QKD implementation and does not provide a formal composable security proof.
> 
> In a real-world commercial QKD deployment:
> - The classical channel must be authenticated using unconditional MACs (e.g., Wegman-Carter authentication).
> - Rigorous finite-key security bounds (e.g., Renner's smooth min-entropy framework) must be evaluated to account for statistical fluctuations.
> - High-efficiency error correction algorithms such as multi-dimensional LDPC or full Cascade with backtracking are used.

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
