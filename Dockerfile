FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Create the database schema.
RUN uv run python scripts/create_schema.py

# Download the amenities.
RUN uv run python scripts/poi_download.py

# Run the application.
CMD ["uv", "run", "fastapi", "run", "app.py", "--port", "80", "--host", "0.0.0.0"]