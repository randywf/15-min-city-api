FROM python:3.12-slim

# Install system dependencies: Java 11 + GDAL + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    gdal-bin \
    libgdal-dev \
    proj-bin \
    proj-data \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal


# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN rm uv.lock && uv lock && uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app.py", "--port", "80", "--host", "0.0.0.0"]