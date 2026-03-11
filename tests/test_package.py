"""Tests for the top-level llm_fuzz_monitor package."""

import llm_fuzz_monitor


class TestPackageMetadata:
    def test_version_defined(self):
        assert hasattr(llm_fuzz_monitor, "__version__")
        assert isinstance(llm_fuzz_monitor.__version__, str)

    def test_version_format(self):
        parts = llm_fuzz_monitor.__version__.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_all_exports(self):
        assert hasattr(llm_fuzz_monitor, "__all__")
        assert len(llm_fuzz_monitor.__all__) > 0

    def test_lazy_import_session_status(self):
        """Lazy import: accessing a core model should work."""
        cls = llm_fuzz_monitor.SessionStatus
        assert cls.RUNNING.value == "running"

    def test_lazy_import_llm_provider(self):
        cls = llm_fuzz_monitor.LLMProvider
        assert cls.OLLAMA.value == "ollama"

    def test_lazy_import_unknown_raises(self):
        import pytest

        with pytest.raises(AttributeError):
            _ = llm_fuzz_monitor.NoSuchSymbol
