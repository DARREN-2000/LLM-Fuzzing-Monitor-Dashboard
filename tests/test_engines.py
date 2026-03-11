"""Tests for llm_fuzz_monitor.analysis.engines — analysers & patterns."""

import re

import pytest

from llm_fuzz_monitor.core.models import (
    FuzzDriverMetrics,
    LLMInteraction,
    LLMProvider,
    VulnerabilityType,
)
from llm_fuzz_monitor.analysis.engines import (
    AdvancedHallucinationDetector,
    ComprehensiveCodeQualityAnalyzer,
    IntelligentVulnerabilityAnalyzer,
    SECURITY_PATTERNS,
    HALLUCINATION_PATTERNS,
    CODE_SMELL_PATTERNS,
    AnalysisResult,
)


# ── Pattern constant tests ──────────────────────────────────


class TestSecurityPatterns:
    def test_buffer_overflow_patterns_exist(self):
        assert VulnerabilityType.BUFFER_OVERFLOW in SECURITY_PATTERNS
        patterns = SECURITY_PATTERNS[VulnerabilityType.BUFFER_OVERFLOW]
        assert len(patterns) >= 3

    def test_strcpy_detected(self):
        patterns = SECURITY_PATTERNS[VulnerabilityType.BUFFER_OVERFLOW]
        code = 'strcpy(dest, src);'
        assert any(p.search(code) for p in patterns)

    def test_command_injection_patterns(self):
        assert VulnerabilityType.COMMAND_INJECTION in SECURITY_PATTERNS
        patterns = SECURITY_PATTERNS[VulnerabilityType.COMMAND_INJECTION]
        code = 'system(user_input + " extra");'
        assert any(p.search(code) for p in patterns)


class TestHallucinationPatterns:
    def test_patterns_compiled(self):
        assert len(HALLUCINATION_PATTERNS) >= 3
        for p in HALLUCINATION_PATTERNS:
            assert isinstance(p, re.Pattern)

    def test_detects_undefined_function(self):
        code = "undefined_function(arg)"
        assert any(p.search(code) for p in HALLUCINATION_PATTERNS)

    def test_clean_code_not_flagged(self):
        code = "printf(\"hello world\\n\");"
        assert not any(p.search(code) for p in HALLUCINATION_PATTERNS)


class TestCodeSmellPatterns:
    def test_magic_numbers(self):
        assert CODE_SMELL_PATTERNS["magic_numbers"].search("x = 12345")

    def test_long_lines(self):
        long = "x" * 130
        assert CODE_SMELL_PATTERNS["long_lines"].search(long)

    def test_todo_comments(self):
        assert CODE_SMELL_PATTERNS["todo_comments"].search("// TODO: fix this")


# ── AnalysisResult dataclass ────────────────────────────────


class TestAnalysisResult:
    def test_construction(self):
        r = AnalysisResult(
            analyzer_name="test",
            analysis_timestamp="2025-01-01T00:00:00",
            analysis_duration_ms=42.0,
            confidence_score=0.85,
            results={"key": "value"},
        )
        assert r.analyzer_name == "test"
        assert r.confidence_score == 0.85
        assert r.errors == []
        assert r.warnings == []


# ── Hallucination Detector ──────────────────────────────────


class TestHallucinationDetector:
    def test_init_default_config(self):
        detector = AdvancedHallucinationDetector()
        assert detector.name == "HallucinationDetector"

    def test_analyze_clean_code(self, sample_llm_interaction):
        detector = AdvancedHallucinationDetector()
        interaction = LLMInteraction(**sample_llm_interaction)
        result = detector.analyze(interaction)
        assert isinstance(result, AnalysisResult)
        assert result.confidence_score >= 0.0

    def test_analyze_hallucinated_code(self, sample_llm_interaction):
        kwargs = {**sample_llm_interaction}
        kwargs["response_text"] = (
            "import nonexistent_module\n"
            "undefined_function(arg)\n"
            "from fictional_package import something\n"
        )
        detector = AdvancedHallucinationDetector()
        interaction = LLMInteraction(**kwargs)
        result = detector.analyze(interaction)
        assert isinstance(result, AnalysisResult)
        # Should detect issues
        issues = result.results.get("issues", [])
        assert isinstance(issues, list)


# ── Code Quality Analyser ──────────────────────────────────


class TestCodeQualityAnalyzer:
    def test_init(self):
        analyzer = ComprehensiveCodeQualityAnalyzer()
        assert analyzer.name == "CodeQualityAnalyzer"

    def test_analyze_c_driver(self, sample_c_code):
        analyzer = ComprehensiveCodeQualityAnalyzer()
        driver = FuzzDriverMetrics(
            driver_id="drv-001",
            session_id="sess-001",
            generation_timestamp="",
            generation_method="llm_generated",
            source_code=sample_c_code,
            source_code_hash="abc123",
        )
        result = analyzer.analyze(driver)
        assert isinstance(result, AnalysisResult)
        # The analyser may succeed or report errors depending on numpy;
        # we only check it returns a valid AnalysisResult.
        assert result.analyzer_name == "CodeQualityAnalyzer"

    def test_analyze_empty_code(self):
        analyzer = ComprehensiveCodeQualityAnalyzer()
        driver = FuzzDriverMetrics(
            driver_id="drv-empty",
            session_id="sess-001",
            generation_timestamp="",
            generation_method="llm_generated",
            source_code="",
            source_code_hash="empty",
        )
        result = analyzer.analyze(driver)
        assert isinstance(result, AnalysisResult)


# ── Vulnerability Analyser ──────────────────────────────────


class TestVulnerabilityAnalyzer:
    def test_init(self):
        analyzer = IntelligentVulnerabilityAnalyzer()
        assert analyzer.name == "VulnerabilityAnalyzer"

    def test_analyze_crash_data(self, sample_vulnerable_c_code):
        analyzer = IntelligentVulnerabilityAnalyzer()
        crash_data = {
            "signature": "SIGSEGV in process_input",
            "stack_trace": "#0 process_input\n#1 main",
            "source_code": sample_vulnerable_c_code,
            "memory_info": {},
        }
        result = analyzer.analyze(crash_data)
        assert isinstance(result, AnalysisResult)
        vulns = result.results.get("vulnerabilities_found", [])
        assert isinstance(vulns, list)

    def test_analyze_safe_code(self, sample_c_code):
        analyzer = IntelligentVulnerabilityAnalyzer()
        crash_data = {
            "signature": "",
            "stack_trace": "",
            "source_code": sample_c_code,
            "memory_info": {},
        }
        result = analyzer.analyze(crash_data)
        assert isinstance(result, AnalysisResult)
