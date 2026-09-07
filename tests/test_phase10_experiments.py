"""Unit tests for Phase 10 experiment framework, execution, and CSV handling."""

from pathlib import Path
import pytest

from src.experiment_framework import (
    AggregatedExperimentResult,
    ExperimentConfig,
    TrialResult,
    derive_trial_seeds,
    load_trials_from_csv,
    run_experiment,
    run_single_trial,
    save_aggregated_to_csv,
    save_trials_to_csv,
)


class TestExperimentConfig:
    """Tests for ExperimentConfig validation."""

    def test_default_config_valid(self) -> None:
        """Test default config creates successfully."""
        cfg = ExperimentConfig()
        assert cfg.total_signals == 2000
        assert cfg.number_of_trials == 10
        assert cfg.master_seed == 42
        assert cfg.eve_enabled is False
        assert cfg.noise_model == "none"

    def test_invalid_parameters_raise(self) -> None:
        """Test invalid parameters raise ValueError."""
        with pytest.raises(ValueError, match="total_signals must be positive"):
            ExperimentConfig(total_signals=0)

        with pytest.raises(ValueError, match="number_of_trials must be positive"):
            ExperimentConfig(number_of_trials=-1)

        with pytest.raises(ValueError, match="eve_probability must be in"):
            ExperimentConfig(eve_probability=1.5)

        with pytest.raises(ValueError, match="noise_probability must be in"):
            ExperimentConfig(noise_probability=-0.1)

        with pytest.raises(ValueError, match="test_sample_fraction must be in"):
            ExperimentConfig(test_sample_fraction=1.0)

        with pytest.raises(ValueError, match="Invalid noise_model"):
            ExperimentConfig(noise_model="invalid_noise")


class TestDeterministicSeedDerivation:
    """Tests for hierarchical isolated seed generation."""

    def test_identical_seed_reproducibility(self) -> None:
        """Test that same master seed and trial produce identical derived seeds."""
        seeds_1 = derive_trial_seeds(master_seed=12345, trial_index=0)
        seeds_2 = derive_trial_seeds(master_seed=12345, trial_index=0)
        assert seeds_1 == seeds_2
        assert len(seeds_1) == 7

    def test_distinct_trials_produce_different_seeds(self) -> None:
        """Test that different trial indices produce distinct seed tuples."""
        seeds_trial_0 = derive_trial_seeds(master_seed=12345, trial_index=0)
        seeds_trial_1 = derive_trial_seeds(master_seed=12345, trial_index=1)
        assert seeds_trial_0 != seeds_trial_1

    def test_distinct_master_seeds(self) -> None:
        """Test that different master seeds produce distinct seeds."""
        seeds_a = derive_trial_seeds(master_seed=100, trial_index=0)
        seeds_b = derive_trial_seeds(master_seed=200, trial_index=0)
        assert seeds_a != seeds_b


class TestTrialExecution:
    """Tests for single trial and batch experiment execution."""

    def test_ideal_channel_trial(self) -> None:
        """Test ideal channel produces 0% QBER, accepted status, and matching keys."""
        cfg = ExperimentConfig(
            condition_name="Ideal Test",
            total_signals=400,
            number_of_trials=1,
            master_seed=777,
            eve_enabled=False,
            noise_model="none",
        )
        res = run_single_trial(cfg, trial_index=0)

        assert res.total_signals == 400
        assert 150 < res.sifted_key_length < 250  # ~50% sifting ratio
        assert 0.40 < res.sifting_ratio < 0.60
        assert res.actual_qber == 0.0
        assert res.estimated_qber == 0.0
        assert res.actual_error_count == 0
        assert res.accepted is True
        assert res.final_keys_match is True
        assert res.final_key_length > 0
        assert res.final_key_rate > 0.0

    def test_eve_full_intercept_resend_trial(self) -> None:
        """Test full intercept-resend attack triggers high QBER and abort."""
        cfg = ExperimentConfig(
            condition_name="Full Eve Test",
            total_signals=500,
            number_of_trials=1,
            master_seed=888,
            eve_enabled=True,
            eve_probability=1.0,
            noise_model="none",
            qber_acceptance_threshold=0.11,
        )
        res = run_single_trial(cfg, trial_index=0)

        assert res.actual_qber > 0.15
        assert res.estimated_qber > 0.15
        assert res.accepted is False
        assert res.final_key_length == 0
        assert res.final_key_rate == 0.0

    def test_batch_experiment_aggregation(self) -> None:
        """Test running a small batch of 2 trials."""
        cfg = ExperimentConfig(
            condition_name="Batch Test",
            total_signals=300,
            number_of_trials=2,
            master_seed=999,
        )
        agg: AggregatedExperimentResult = run_experiment(cfg)

        assert agg.num_trials == 2
        assert len(agg.trials) == 2
        assert agg.acceptance_rate == 1.0
        assert agg.key_agreement_rate == 1.0
        assert 0.40 < agg.mean_sifting_ratio < 0.60
        assert agg.qber_stats.count == 2
        assert agg.qber_stats.mean == 0.0
        assert agg.final_key_rate_stats.mean > 0.0


class TestCSVIngestion:
    """Tests for CSV serialization and round-trip reloading."""

    def test_trials_csv_round_trip(self, tmp_path: Path) -> None:
        """Test saving TrialResult records to CSV and loading them back."""
        cfg = ExperimentConfig(
            condition_name="CSV Test",
            total_signals=200,
            number_of_trials=2,
            master_seed=123,
        )
        t0 = run_single_trial(cfg, trial_index=0)
        t1 = run_single_trial(cfg, trial_index=1)

        csv_file = tmp_path / "trials.csv"
        save_trials_to_csv([t0, t1], csv_file)

        assert csv_file.exists()

        records = load_trials_from_csv(csv_file)
        assert len(records) == 2
        assert records[0]["trial_index"] == 0
        assert records[0]["condition_name"] == "CSV Test"
        assert records[0]["total_signals"] == 200
        assert isinstance(records[0]["sifted_key_length"], int)
        assert isinstance(records[0]["estimated_qber"], float)
        assert isinstance(records[0]["accepted"], bool)

    def test_aggregated_csv_save(self, tmp_path: Path) -> None:
        """Test saving AggregatedExperimentResult to CSV."""
        cfg = ExperimentConfig(
            condition_name="Agg CSV Test",
            total_signals=200,
            number_of_trials=2,
            master_seed=456,
        )
        agg = run_experiment(cfg)

        csv_file = tmp_path / "aggregated.csv"
        save_aggregated_to_csv([agg], csv_file)

        assert csv_file.exists()
        content = csv_file.read_text(encoding="utf-8")
        assert "Agg CSV Test" in content
        assert "acceptance_rate" in content
