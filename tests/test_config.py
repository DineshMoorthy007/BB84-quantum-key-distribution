"""Unit tests for the BB84 simulation configuration module."""

import pytest
from src.config import BB84Config, NoiseModelType


def test_default_config() -> None:
    """Verify default configuration parameters."""
    cfg = BB84Config()
    assert cfg.num_qubits == 100
    assert cfg.random_seed is None
    assert cfg.shots == 1
    assert cfg.eavesdropping_enabled is False
    assert cfg.noise_model == "none"
    assert cfg.noise_probability == 0.0


def test_custom_config() -> None:
    """Verify custom configuration initialization."""
    cfg = BB84Config(
        num_qubits=500,
        random_seed=42,
        shots=1,
        eavesdropping_enabled=True,
        noise_model=NoiseModelType.DEPOLARIZING,
        noise_probability=0.05,
    )
    assert cfg.num_qubits == 500
    assert cfg.random_seed == 42
    assert cfg.shots == 1
    assert cfg.eavesdropping_enabled is True
    assert cfg.noise_model == "depolarizing"
    assert cfg.noise_probability == 0.05


def test_invalid_qubits() -> None:
    """Verify validation on invalid qubit count."""
    with pytest.raises(ValueError, match="num_qubits must be a positive integer"):
        BB84Config(num_qubits=0)

    with pytest.raises(ValueError, match="num_qubits must be a positive integer"):
        BB84Config(num_qubits=-10)


def test_invalid_noise_probability() -> None:
    """Verify validation on invalid noise probability."""
    with pytest.raises(ValueError, match="noise_probability must be in the range"):
        BB84Config(noise_probability=1.5)

    with pytest.raises(ValueError, match="noise_probability must be in the range"):
        BB84Config(noise_probability=-0.1)


def test_invalid_noise_model() -> None:
    """Verify validation on unknown noise model."""
    with pytest.raises(ValueError, match="Unknown noise_model"):
        BB84Config(noise_model="invalid_channel")


def test_dict_serialization() -> None:
    """Verify conversion to and from dictionary."""
    original = BB84Config(
        num_qubits=250,
        random_seed=1234,
        shots=1,
        eavesdropping_enabled=True,
        noise_model="bit_flip",
        noise_probability=0.02,
    )
    serialized = original.to_dict()
    restored = BB84Config.from_dict(serialized)
    assert original == restored
