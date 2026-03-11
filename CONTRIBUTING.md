# Contributing to LLM Fuzz Monitor

Thank you for considering a contribution! This document explains how to get
started.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/DARREN-2000/llm-integration.git
cd llm-integration

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev extras
pip install -r requirements-dev.txt
pip install -e ".[dev,perf]"
```

## Code Style

This project uses **Ruff** for linting and formatting:

```bash
make lint      # check for issues
make format    # auto-format
```

## Running Tests

```bash
make test          # unit tests
make test-cov      # with coverage report
```

## Pull Request Checklist

- [ ] All new code has tests
- [ ] `make lint` passes without errors
- [ ] `make test` passes
- [ ] Documentation is updated if behaviour changed

## Reporting Bugs

Open an issue with:

1. Steps to reproduce
2. Expected behaviour
3. Actual behaviour
4. Python version and OS

## Architecture Overview

See [`docs/architecture.md`](docs/architecture.md) for a description of the
package layout and key design decisions.
