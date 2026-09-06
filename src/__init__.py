"""BB84 Quantum Key Distribution Simulator.

Core source package for quantum state preparation, measurement,
and protocol execution.
"""

from .config import BB84Config, NoiseModelType

__all__ = ["BB84Config", "NoiseModelType"]
