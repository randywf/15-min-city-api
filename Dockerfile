FROM python:3.12-slim

# Install Java for r5py
RUN apt-get update && apt-get install -y \
    openjdk-21-jdk-headless \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache