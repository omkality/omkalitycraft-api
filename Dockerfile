FROM python:3.14.2-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl

WORKDIR /backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

RUN uv sync --only-group api --no-editable --frozen
