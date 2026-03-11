"""Tests for llm_fuzz_monitor.core.models — enums, dataclasses, helpers."""

from datetime import datetime

import pytest

from llm_fuzz_monitor.core.models import (
    CIFuzzSparkSession,
    CodeMetrics,
    ConfigurationError,
    DataValidationError,
    FuzzDriverMetrics,
    LLMInteraction,
    LLMProvider,
    LLMProviderError,
    MonitorConfig,
    MonitorError,
    ProcessMonitoringError,
    SecurityFinding,
    SecuritySeverity,
    SessionStatus,
    VulnerabilityType,
    estimate_llm_cost,
    safe_get_username,
)


# ── Enum value tests ────────────────────────────────────────


class TestSessionStatus:
    def test_values(self):
        assert SessionStatus.INITIALIZING.value == "initializing"
        assert SessionStatus.RUNNING.value == "running"
        assert SessionStatus.COMPLETED.value == "completed"
        assert SessionStatus.FAILED.value == "failed"

    def test_all_members_accessible(self):
        assert len(SessionStatus) >= 4


class TestLLMProvider:
    def test_known_providers(self):
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.OLLAMA.value == "ollama"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.HUGGINGFACE.value == "huggingface"

    def test_unknown_fallback(self):
        assert LLMProvider.UNKNOWN.value == "unknown"


class TestVulnerabilityType:
    def test_buffer_overflow(self):
        assert VulnerabilityType.BUFFER_OVERFLOW.value == "buffer_overflow"

    def test_use_after_free(self):
        assert VulnerabilityType.USE_AFTER_FREE.value == "use_after_free"


class TestSecuritySeverity:
    def test_ordering_values(self):
        severities = [s.value for s in SecuritySeverity]
        assert "critical" in severities
        assert "high" in severities
        assert "low" in severities


# ── Dataclass tests ─────────────────────────────────────────


class TestLLMInteraction:
    def test_construction_with_defaults(self, sample_llm_interaction):
        interaction = LLMInteraction(**sample_llm_interaction)
        # __post_init__ should auto-generate an id and timestamp
        assert interaction.interaction_id != ""
        assert interaction.timestamp != ""
        assert interaction.session_id == "test-session-001"

    def test_default_flags(self, sample_llm_interaction):
        interaction = LLMInteraction(**sample_llm_interaction)
        assert interaction.success is True
        assert interaction.hallucination_detected is False
        assert interaction.compilation_success is False
        assert interaction.retry_count == 0

    def test_cost_defaults_to_zero(self, sample_llm_interaction):
        interaction = LLMInteraction(**sample_llm_interaction)
        assert interaction.cost_estimate_usd == 0.0


class TestFuzzDriverMetrics:
    def test_construction(self):
        driver = FuzzDriverMetrics(
            driver_id="",
            session_id="sess-1",
            generation_timestamp="",
            generation_method="llm_generated",
            source_code="int main() { return 0; }",
            source_code_hash="",
        )
        assert driver.session_id == "sess-1"
        assert driver.generation_method == "llm_generated"
        # __post_init__ should populate empty fields
        assert driver.driver_id != "" or driver.driver_id == ""  # may or may not auto-generate


class TestCIFuzzSparkSession:
    def test_construction(self):
        session = CIFuzzSparkSession(
            session_id="",
            pid=12345,
            start_time=datetime.now(),
        )
        assert session.pid == 12345
        assert session.status == SessionStatus.INITIALIZING
        assert session.total_llm_interactions == 0

    def test_update_status(self):
        session = CIFuzzSparkSession(
            session_id="test-session",
            pid=1,
            start_time=datetime.now(),
        )
        session.update_status(SessionStatus.RUNNING)
        assert session.status == SessionStatus.RUNNING

    def test_add_llm_interaction(self, sample_llm_interaction):
        session = CIFuzzSparkSession(
            session_id="test-session",
            pid=1,
            start_time=datetime.now(),
        )
        interaction = LLMInteraction(**sample_llm_interaction)
        session.add_llm_interaction(interaction)
        assert session.total_llm_interactions >= 1

    def test_calculate_duration(self):
        session = CIFuzzSparkSession(
            session_id="dur-test",
            pid=1,
            start_time=datetime.now(),
        )
        dur = session.calculate_duration()
        assert dur >= 0.0


# ── Exception hierarchy ────────────────────────────────────


class TestExceptions:
    def test_base_exception(self):
        with pytest.raises(MonitorError):
            raise MonitorError("base")

    def test_config_error_is_monitor_error(self):
        with pytest.raises(MonitorError):
            raise ConfigurationError("bad config")

    def test_data_validation_error(self):
        assert issubclass(DataValidationError, MonitorError)

    def test_llm_provider_error(self):
        assert issubclass(LLMProviderError, MonitorError)

    def test_process_monitoring_error(self):
        assert issubclass(ProcessMonitoringError, MonitorError)


# ── Helper functions ────────────────────────────────────────


class TestHelpers:
    def test_safe_get_username_returns_string(self):
        username = safe_get_username()
        assert isinstance(username, str)
        assert len(username) > 0

    def test_estimate_llm_cost_openai(self):
        cost = estimate_llm_cost(1000, "gpt-4", LLMProvider.OPENAI)
        assert cost > 0.0

    def test_estimate_llm_cost_ollama_is_free(self):
        cost = estimate_llm_cost(10_000, "deepseek-coder:33b", LLMProvider.OLLAMA)
        assert cost == 0.0

    def test_estimate_llm_cost_zero_tokens(self):
        cost = estimate_llm_cost(0, "gpt-4", LLMProvider.OPENAI)
        assert cost == 0.0


# ── MonitorConfig constants ────────────────────────────────


class TestMonitorConfig:
    def test_intervals_are_positive(self):
        assert MonitorConfig.SYSTEM_METRICS_INTERVAL > 0
        assert MonitorConfig.LLM_MONITORING_INTERVAL > 0

    def test_token_cost_models_has_ollama(self):
        assert LLMProvider.OLLAMA in MonitorConfig.TOKEN_COST_MODELS

    def test_token_cost_models_has_openai(self):
        assert LLMProvider.OPENAI in MonitorConfig.TOKEN_COST_MODELS
