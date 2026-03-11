# Architecture

This document describes the high-level design of **LLM Fuzz Monitor**.

## Package Layout

```
llm_fuzz_monitor/
├── __init__.py              # Package root — lazy imports
├── core/
│   ├── __init__.py
│   └── models.py            # Data models, enums, config, exceptions
├── storage/
│   ├── __init__.py
│   └── manager.py           # Thread-safe storage, compression, SQLite
├── analysis/
│   ├── __init__.py
│   └── engines.py           # Hallucination / quality / vuln analysers
├── cli/
│   ├── __init__.py
│   └── main.py              # Rich CLI, log parsers, process monitor
└── experiments/
    ├── __init__.py
    ├── runner.py             # Automated experiment orchestration
    └── monitor.py            # Daemon / entry-point script
```

## Data Flow

```
                    ┌──────────────┐
  Repositories ──►  │ Experiment   │
  (C/C++ repos)     │  Runner      │
                    └──────┬───────┘
                           │  clones repo, invokes CI Fuzz w/ LLM
                           ▼
                    ┌──────────────┐
                    │ LLM Provider │  Ollama / OpenAI / Anthropic / …
                    │  Manager     │
                    └──────┬───────┘
                           │  generated fuzz drivers
                           ▼
               ┌───────────────────────┐
               │   Analysis Engines    │
               │  ┌─────────────────┐  │
               │  │ Hallucination   │  │
               │  │ Detector        │  │
               │  ├─────────────────┤  │
               │  │ Code Quality    │  │
               │  │ Analyser        │  │
               │  ├─────────────────┤  │
               │  │ Vulnerability   │  │
               │  │ Analyser        │  │
               │  └─────────────────┘  │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │   Storage Manager     │
               │  (JSON / CSV / SQLite │
               │   + LZ4 compression)  │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │   CLI / Dashboard     │
               │  (Rich tables, logs,  │
               │   export to HTML)     │
               └───────────────────────┘
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Lazy imports** in `__init__.py` | Keeps `import llm_fuzz_monitor` fast; heavy deps load on demand. |
| **Abstract base class** for analysers | New analysers can be plugged in without changing existing code. |
| **Provider abstraction** for LLMs | Swap between Ollama, OpenAI, Anthropic, etc. via config. |
| **Thread-safe storage** with `portalocker` | Experiments run in parallel threads; file I/O must be safe. |
| **YAML configuration** | Human-readable, easy to version-control, supports comments. |
| **Optional heavy deps** (`scipy`, `openai`, …) | Core features work without cloud SDKs; install extras as needed. |

## Supported LLM Providers

| Provider | Transport | Auth |
|---|---|---|
| Ollama | HTTP REST | None (local) |
| OpenAI | HTTP REST | API key |
| Anthropic | HTTP REST | API key |
| HuggingFace Inference | HTTP REST | API token |
| LocalAI | HTTP REST | None (local) |

## Log Parsers

The CLI ships with parsers for eight fuzzer / compiler log formats:

1. **AFL** — `execs_done`, `paths_total`, crashes
2. **LibFuzzer** — `#N INITED`, `exec/s`, coverage
3. **HonggFuzz** — iterations, speed, unique crashes
4. **CI Fuzz** — structured JSON output
5. **LLM output** — token counts, generation time
6. **Compiler** — error / warning extraction
7. **Coverage** — `gcov` / `lcov` percentage parsing
8. **Crash** — ASAN / MSAN / UBSAN reports
