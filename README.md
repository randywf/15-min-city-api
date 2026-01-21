# 15-Min City API

API for calculating 15-minute city accessibility metrics using isochrones and POI analysis.

## Prerequisites

- Docker and Docker Compose
- Java 11+ (required for r5py routing engine)
- OSM network data (automatically downloaded by `init.sh`)

**Note**: Java 11+ is essential for the r5py routing engine. Ensure it's installed on your system before running the application.

## Initial Setup

Before first run, initialize the project and download OSM network data:

```sh
./init.sh
```

This script will:
- Install UV and sync dependencies
- Download the OSM road network data for Münster from Geofabrik
- Store the data in `./data/muenster/`

The road network files are not stored in Git due to their size, so this initialization step is required.

## Quick Start

### Using Docker (Recommended)

The project includes a `run.py` script for easy management of Docker containers:

```sh
# Development mode (with hot reload and debugging support)
python run.py dev

# Production mode
python run.py prod

# Stop containers
python run.py down

# View logs
python run.py logs

# Rebuild containers
python run.py build
```

### Development Mode

Development mode includes:
- **Hot reload**: Code changes automatically restart the server
- **Debug support**: Remote debugging with VS Code
- **Performance timing**: Detailed timing logs for bottleneck analysis

To use the debugger:

1. Start the containers in dev mode:
   ```sh
   python run.py dev
   ```

2. In VS Code, press `F5` or select "Python: Remote Attach" from the debug menu

3. Set breakpoints in your code and debug normally

The debugger connects on port `5678` and maps your local workspace to `/app` in the container.

### Production Mode

Production mode runs without hot reload or debugging overhead:

```sh
python run.py prod
```

### Manual Docker Compose

If you prefer to use docker-compose directly:

```sh
# Development mode
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up

# Production mode
docker-compose up

# Stop containers
docker-compose down
```

## Local Development (Without Docker)

### Installation

1. Install UV:
   ```sh
   pip install uv
   ```

2. Sync dependencies:
   ```sh
   uv sync
   ```

3. Start the development server:
   ```sh
   uv run fastapi dev app.py
   ```

Note: You'll need a PostgreSQL/PostGIS database running separately.

## Services

The Docker setup includes:

- **API** (port 8000): FastAPI application
- **PostGIS** (port 5432): PostgreSQL with PostGIS extension
- **pgAdmin** (port 5050): Database administration interface
  - Email: admin@admin.de
  - Password: admin

## Database Setup

The database schema and POI data are automatically initialized on first run. To manually update:

```sh
# From within the container
docker exec my_app uv run python scripts/create_schema.py
docker exec my_app uv run python scripts/poi_download.py --update
```

## Configuration

Environment variables can be set in `docker-compose.yaml` or `docker-compose.dev.yaml`:

- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG_TIMING`: Enable performance timing logs (dev mode only)
- `JAVA_TOOL_OPTIONS`: JVM memory settings for r5py

## Project Structure

```
├── app.py                 # FastAPI application
├── functions/             # Core functionality
│   ├── poi.py            # Point of Interest queries
│   ├── reachability.py   # Isochrone calculations
│   └── scoring.py        # Accessibility scoring
├── scripts/              # Database and data management
│   ├── create_schema.py  # Database schema setup
│   └── poi_download.py   # POI data download
├── data/                 # OSM data and boundaries
└── docker-compose*.yaml  # Container orchestration 
