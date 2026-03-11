"""Shared pytest fixtures for the llm_fuzz_monitor test suite."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> Path:
    """Return a temporary directory suitable for storage tests."""
    d = tmp_path / "data"
    d.mkdir()
    return d


@pytest.fixture()
def sample_llm_interaction():
    """Return kwargs for constructing an LLMInteraction."""
    from llm_fuzz_monitor.core.models import LLMProvider

    return dict(
        interaction_id="",
        session_id="test-session-001",
        timestamp="",
        llm_provider=LLMProvider.OLLAMA,
        llm_model="deepseek-coder:33b",
        llm_endpoint="http://localhost:11434",
        prompt_type="fuzz_driver_generation",
        prompt_text="Generate a fuzz driver for zlib inflate",
        response_text='#include <zlib.h>\nint LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) { return 0; }',
        prompt_tokens=120,
        response_tokens=85,
        total_tokens=205,
        response_time_ms=1450.5,
    )


@pytest.fixture()
def sample_c_code() -> str:
    """A small C fuzz driver for analysis tests."""
    return """\
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;

    char *buf = (char *)malloc(size + 1);
    if (!buf) return 0;

    memcpy(buf, data, size);
    buf[size] = '\\0';

    // Process the buffer
    int result = 0;
    for (size_t i = 0; i < size; i++) {
        result += buf[i];
    }

    free(buf);
    return 0;
}
"""


@pytest.fixture()
def sample_vulnerable_c_code() -> str:
    """C code with deliberate security issues for vuln-analyser tests."""
    return """\
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void process_input(char *user_input) {
    char buffer[64];
    strcpy(buffer, user_input);          /* buffer overflow */
    sprintf(buffer, "%s_suffix", user_input); /* format string */
    system(user_input);                  /* command injection */
}
"""
