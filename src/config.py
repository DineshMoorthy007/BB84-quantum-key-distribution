"""Configuration module for the BB84 Quantum Key Distribution Simulator.

This module provides structured, validated configuration parameters for
running BB84 protocol simulations, noise models, and eavesdropping experiments.

Academic Note:
    Numerical simulations model quantum state preparation, channel transmission,
    and projective measurement under discrete noise and intercept-resend conditions.
    This simulator does NOT constitute a formal mathematical security proof
    of QKD security under universal composability frameworks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class NoiseModelType(str, Enum):
    """Supported quantum noise models for the simulation channel."""

    NONE = "none"
    DEPOLARIZING = "depolarizing"
    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    BIT_PHASE_FLIP = "bit_phase_flip"


@dataclass(frozen=True)
class BB84Config:
    """Configuration settings for BB84 QKD simulation runs.

    Attributes:
        num_qubits: Total number of quantum bits (photons) prepared and sent by Alice.
            Must be a positive integer.
        random_seed: Seed for pseudo-random number generators (NumPy and Qiskit)
            ensuring experimental reproducibility. None for non-deterministic execution.
        shots: Number of measurement shots per circuit execution. In standard single-photon
            BB84, each photon is measured once (shots=1).
        eavesdropping_enabled: Flag indicating whether an intercept-resend eavesdropper (Eve)
            is present in the quantum channel.
        noise_model: Type of quantum noise to simulate along the quantum channel.
            Defaults to NoiseModelType.NONE.
        noise_probability: Error rate parameter p ∈ [0.0, 1.0] for the chosen noise channel.
    """

    num_qubits: int = 100
    random_seed: Optional[int] = None
    shots: int = 1
    eavesdropping_enabled: bool = False
    noise_model: Optional[str] = NoiseModelType.NONE.value
    noise_probability: float = 0.0

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if not isinstance(self.num_qubits, int) or self.num_qubits <= 0:
            raise ValueError(f"num_qubits must be a positive integer, got {self.num_qubits}")

        if self.random_seed is not None and not isinstance(self.random_seed, int):
            raise ValueError(f"random_seed must be an integer or None, got {type(self.random_seed).__name__}")

        if not isinstance(self.shots, int) or self.shots <= 0:
            raise ValueError(f"shots must be a positive integer, got {self.shots}")

        if not isinstance(self.eavesdropping_enabled, bool):
            raise ValueError(
                f"eavesdropping_enabled must be a boolean, got {type(self.eavesdropping_enabled).__name__}"
            )

        if not (0.0 <= self.noise_probability <= 1.0):
            raise ValueError(
                f"noise_probability must be in the range [0.0, 1.0], got {self.noise_probability}"
            )

        # Normalize noise model string/enum
        if self.noise_model is not None:
            model_val = self.noise_model.value if isinstance(self.noise_model, Enum) else str(self.noise_model).lower()
            valid_models = {m.value for m in NoiseModelType}
            if model_val not in valid_models:
                raise ValueError(
                    f"Unknown noise_model '{self.noise_model}'. Valid options are: {sorted(valid_models)}"
                )
            # Use object.__setattr__ because frozen=True
            object.__setattr__(self, "noise_model", model_val)
        else:
            object.__setattr__(self, "noise_model", NoiseModelType.NONE.value)

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration parameters as a dictionary for logging and metadata."""
        return {
            "num_qubits": self.num_qubits,
            "random_seed": self.random_seed,
            "shots": self.shots,
            "eavesdropping_enabled": self.eavesdropping_enabled,
            "noise_model": self.noise_model,
            "noise_probability": self.noise_probability,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BB84Config:
        """Instantiate configuration from a dictionary."""
        return cls(
            num_qubits=data.get("num_qubits", 100),
            random_seed=data.get("random_seed"),
            shots=data.get("shots", 1),
            eavesdropping_enabled=data.get("eavesdropping_enabled", False),
            noise_model=data.get("noise_model", NoiseModelType.NONE.value),
            noise_probability=float(data.get("noise_probability", 0.0)),
        )
