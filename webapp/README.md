# Web Dashboard

This directory contains a production-oriented static dashboard for visualizing `LLM Fuzz Monitor` session outputs.

## Features

- Pure static frontend (HTML/CSS/JS), suitable for GitHub Pages
- Safe DOM rendering for uploaded JSON data
- KPI cards for high-level metrics
- Provider distribution bars
- Session table with filtering and sorting
- Sample dataset for immediate preview

## Data format

The app accepts uploaded `.json` files with either:

1. **single session object**
2. **array of sessions**

Required session keys:

- `session_id`
- `llm_provider`
- `llm_model`
- `status`
- `fuzz_drivers_generated`
- `security_vulnerabilities_found`
- `total_duration_ms`
- `estimated_cost_usd`
- `total_tokens_consumed`
- `total_api_calls`

## Local run

```bash
cd webapp
python3 -m http.server 8080
```

Open: `http://localhost:8080`

## GitHub Pages deployment

Workflow: `.github/workflows/pages.yml`

Deployment behavior:

- auto-deploy on `main` pushes touching web docs/assets
- manual deploy available via `workflow_dispatch`

Repository setting required:

- **Settings → Pages → Build and deployment → Source = GitHub Actions**

Expected site URL:

- `https://darren-2000.github.io/LLM-Fuzzing-Monitor-Dashboard/`

## Media

- Overview screenshot: `../docs/media/webapp-overview.png`
- Filtered screenshot: `../docs/media/webapp-filtered-openai.png`
- Demo GIF 1: `../docs/media/webapp-demo.gif`
- Demo GIF 2: `../docs/media/webapp-filters-demo.gif`
