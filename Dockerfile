FROM python:3.12-slim

# Install system dependencies (Java for r5py, Postgres client, and geospatial libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jdk-headless \
    postgresql-client \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Help Python packages find GDAL
ENV GDAL_CONFIG=/usr/bin/gdal-config

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN uv sync --frozen --no-cache