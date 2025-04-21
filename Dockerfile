# → 1) Start from slim Python
FROM python:3.13-slim

# → 2) Install curl (to fetch uv) and git if you need it
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# → 3) Install uv (Rust‑based) into ~/.local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Make sure uv is on the PATH
ENV PATH="/root/.local/bin:${PATH}"

# → 4) Copy just your lockfiles first (cacheable layer)
WORKDIR /app
COPY pyproject.toml ./

# → 5) Sync dependencies (creates and populates a venv)
RUN uv sync

# → 6) Copy the rest of your app
COPY . .

# → 7) Expose and run
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

