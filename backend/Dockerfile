FROM python:3.12-slim

WORKDIR /app

# System deps (keep minimal; add build-essential later only if needed)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install uv (recommended official install script)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Make uv available in PATH (install script puts it in /root/.local/bin)
ENV PATH="/root/.local/bin:${PATH}"

# Copy dependency manifest first to leverage Docker layer caching
COPY pyproject.toml /app/pyproject.toml

# Create venv + install deps (no project package build needed)
RUN uv venv && uv sync

# Now copy the application code
COPY app /app/app

# Ensure we use the venv Python by default
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]