"""Statistical evaluation and confidence interval module for BB84 QKD.

Provides rigorous statistical metrics, descriptive statistics, and
binomial proportion confidence intervals (specifically the Wilson score interval)
for experimental QBER and secret key rate measurements.

Academic Principle:
    Error rate estimation in BB84 is fundamentally a Bernoulli sampling process.
    The normal approximation interval (Wald interval) p̂ ± z*sqrt(p̂(1-p̂)/n) severely
    under-covers near boundary conditions (p ≈ 0 or p ≈ 1) and for finite sample sizes.
    The Wilson score interval provides superior coverage probability across all
    error rate regimes without degenerating at zero error rate.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Sequence, Tuple
import numpy as np


@dataclass(frozen=True)
class DescriptiveStats:
    """Descriptive summary statistics for numerical measurement sequences.

    Attributes:
        count: Number of observations.
        mean: Sample mean.
        std: Sample standard deviation (Bessel-corrected, ddof=1 if n > 1).
        variance: Sample variance (ddof=1 if n > 1).
        median: Sample median (50th percentile).
        min: Minimum observed value.
        max: Maximum observed value.
    """

    count: int
    mean: float
    std: float
    variance: float
    median: float
    min: float
    max: float

    def to_dict(self) -> dict[str, float]:
        """Convert statistics to dictionary representation."""
        return {
            "count": float(self.count),
            "mean": self.mean,
            "std": self.std,
            "variance": self.variance,
            "median": self.median,
            "min": self.min,
            "max": self.max,
        }


def wilson_score_interval(
    errors: int,
    total_trials: int,
    confidence: float = 0.95,
) -> Tuple[float, float]:
    """Calculate the Wilson score confidence interval for a binomial proportion.

    Given e bit errors observed out of n tested bits, computes the asymmetric
    two-sided (1 - alpha) confidence interval [lower, upper].

    Formula:
        p̂ = e / n
        denominator = 1 + z^2 / n
        center = (p̂ + z^2 / (2n)) / denominator
        margin = (z * sqrt(p̂(1-p̂)/n + z^2 / (4n^2))) / denominator
        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)

    Args:
        errors: Number of bit errors (successes/discrepancies), must be >= 0 and <= total_trials.
        total_trials: Total number of sampled bits (trials), must be >= 0.
        confidence: Confidence level in (0.0, 1.0), defaults to 0.95.

    Returns:
        Tuple of (lower_bound, upper_bound) in [0.0, 1.0].

    Raises:
        ValueError: If parameters are outside valid numerical ranges.
    """
    if total_trials < 0:
        raise ValueError(f"total_trials must be non-negative, got {total_trials}")
    if errors < 0:
        raise ValueError(f"errors must be non-negative, got {errors}")
    if errors > total_trials:
        raise ValueError(f"errors ({errors}) cannot exceed total_trials ({total_trials})")
    if not (0.0 < confidence < 1.0):
        raise ValueError(f"confidence must be in (0.0, 1.0), got {confidence}")

    if total_trials == 0:
        return 0.0, 0.0

    # Determine z critical value for standard confidence levels
    # Supports common levels with high-precision constants, fallback to approx
    if math.isclose(confidence, 0.95, abs_tol=1e-4):
        z = 1.959963984540054
    elif math.isclose(confidence, 0.99, abs_tol=1e-4):
        z = 2.5758293035489004
    elif math.isclose(confidence, 0.90, abs_tol=1e-4):
        z = 1.6448536269514722
    else:
        # Generic quantile approximation via Hastings-like rational formula for normal inverse
        alpha = 1.0 - confidence
        p = 1.0 - alpha / 2.0
        # Winitzki / Beasley-Springer rational approximation for Probit
        t = math.sqrt(-2.0 * math.log(1.0 - p))
        c0 = 2.515517
        c1 = 0.802853
        c2 = 0.010328
        d1 = 1.432788
        d2 = 0.189269
        d3 = 0.001308
        z = t - ((c2 * t + c1) * t + c0) / (((d3 * t + d2) * t + d1) * t + 1.0)

    p_hat = errors / total_trials
    z_sq = z * z
    n = float(total_trials)

    denominator = 1.0 + z_sq / n
    center = (p_hat + z_sq / (2.0 * n)) / denominator
    spread = (z * math.sqrt((p_hat * (1.0 - p_hat) / n) + (z_sq / (4.0 * n * n)))) / denominator

    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)

    if errors == 0:
        lower = 0.0
    if errors == total_trials:
        upper = 1.0

    return lower, upper


def compute_descriptive_stats(values: Sequence[float]) -> DescriptiveStats:
    """Calculate sample descriptive statistics for a sequence of floating-point values.

    Args:
        values: Sequence of numerical values.

    Returns:
        DescriptiveStats dataclass with count, mean, std, variance, median, min, max.

    Raises:
        ValueError: If values sequence is empty.
    """
    if not values:
        raise ValueError("Cannot calculate descriptive statistics for an empty sequence.")

    arr = np.asarray(values, dtype=np.float64)
    n = len(arr)

    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))

    if n > 1:
        var_val = float(np.var(arr, ddof=1))
        std_val = float(np.std(arr, ddof=1))
    else:
        var_val = 0.0
        std_val = 0.0

    return DescriptiveStats(
        count=n,
        mean=mean_val,
        std=std_val,
        variance=var_val,
        median=median_val,
        min=min_val,
        max=max_val,
    )
