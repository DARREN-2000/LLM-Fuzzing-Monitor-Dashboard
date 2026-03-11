"""
LLM Fuzz Monitor — AI-Driven Fuzz-Testing Toolkit
===================================================

A comprehensive toolkit for integrating Large Language Models (LLMs)
into automated fuzz-testing workflows.  It benchmarks LLM-generated
fuzz drivers, detects hallucinations, analyses code quality and
security vulnerabilities, and orchestrates experiments across dozens
of open-source C/C++ repositories.

Version: 3.0.0
License: MIT
"""

__version__ = "3.0.0"
__author__ = "Morris Darren Babu"

# Lazy imports — heavy dependencies are loaded only when the
# corresponding sub-package is actually used.  This keeps
# `import llm_fuzz_monitor` fast.

__all__ = [
    # core models
    "CIFuzzSparkSession",
    "LLMInteraction",
    "FuzzDriverMetrics",
    "SessionStatus",
    "LLMProvider",
    "VulnerabilityType",
    "SecuritySeverity",
    "MonitorConfig",
    # storage
    "AdvancedTextDataManager",
    # analysis
    "AdvancedHallucinationDetector",
    "ComprehensiveCodeQualityAnalyzer",
    "IntelligentVulnerabilityAnalyzer",
    "LLMProviderManager",
    "PerformanceAnalyzer",
]


def __getattr__(name: str):
    """Lazy import public symbols on first access."""
    _core_names = {
        "CIFuzzSparkSession", "LLMInteraction", "FuzzDriverMetrics",
        "SessionStatus", "LLMProvider", "VulnerabilityType",
        "SecuritySeverity", "MonitorConfig", "CodeMetrics",
        "SecurityFinding", "ProjectAnalysis", "SystemMetrics",
        "HistoricalAnalysisResult", "MonitorError",
        "ConfigurationError", "DataValidationError",
        "LLMProviderError", "ProcessMonitoringError",
    }
    _storage_names = {"AdvancedTextDataManager", "ConcurrentSessionManager"}
    _analysis_names = {
        "AdvancedHallucinationDetector", "ComprehensiveCodeQualityAnalyzer",
        "IntelligentVulnerabilityAnalyzer", "LLMProviderManager",
        "PerformanceAnalyzer",
    }

    if name in _core_names:
        from .core import models as _m  # noqa: F811
        return getattr(_m, name)
    if name in _storage_names:
        from .storage import manager as _s  # noqa: F811
        return getattr(_s, name)
    if name in _analysis_names:
        from .analysis import engines as _a  # noqa: F811
        return getattr(_a, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
