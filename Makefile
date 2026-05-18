# ── LLM Fuzz Monitor ─────────────────────────────────────────
.PHONY: help install dev lint test test-cov build clean docker-build docker-up demo-up demo-down

PYTHON  ?= python3
PIP     ?= pip

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────
install: ## Install production dependencies
	$(PIP) install -r requirements.txt

dev: ## Install dev dependencies + package in editable mode
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e ".[dev,perf]"

# ── Quality ──────────────────────────────────────────────────
lint: ## Run linters (ruff)
	$(PYTHON) -m ruff check llm_fuzz_monitor/ tests/

format: ## Auto-format code
	$(PYTHON) -m ruff format llm_fuzz_monitor/ tests/

typecheck: ## Run mypy type checking
	$(PYTHON) -m mypy llm_fuzz_monitor/

# ── Testing ──────────────────────────────────────────────────
test: ## Run unit tests
	$(PYTHON) -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ --cov=llm_fuzz_monitor --cov-report=term-missing --cov-report=html

# ── Build ────────────────────────────────────────────────────
build: ## Build distribution packages
	$(PYTHON) -m build

clean: ## Remove build artefacts
	rm -rf build/ dist/ *.egg-info .pytest_cache htmlcov .coverage .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ── Docker ───────────────────────────────────────────────────
docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start services (Ollama + monitor)
	docker compose up -d

docker-down: ## Stop services
	docker compose down

demo-up: ## Start free local demo stack (CPU-friendly)
	docker compose -f docker-compose.demo.yml up -d

demo-down: ## Stop free local demo stack
	docker compose -f docker-compose.demo.yml down
