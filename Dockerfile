# ── Stage 1: builder ─────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: runtime ────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="Morris Darren Babu"
LABEL description="LLM Fuzz Monitor — AI-driven fuzz-testing toolkit"

# Install git (needed for cloning test repositories)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

WORKDIR /workspace
COPY config/ /workspace/config/

# Non-root user for security
RUN groupadd -r fuzzuser && useradd -r -g fuzzuser fuzzuser
RUN mkdir -p /workspace/experiments /workspace/results && \
    chown -R fuzzuser:fuzzuser /workspace
USER fuzzuser

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["llm-fuzz-monitor"]
CMD ["--help"]
