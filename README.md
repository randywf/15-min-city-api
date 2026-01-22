<a id="readme-top"></a>

<div align="center">
 <h1>Welcome to the backend repository for the 15-Minute City application</h1>

<br />
<div align="center">
  <p align="center">
    <img src="image/logo_15min.png" alt="15-min-city" width="300"/>
  </p>
</div>

  

  <p align="center">
    An application to explore the city of Münster and find your ideal location!
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    &middot;
    <a href="https://github.com/othneildrew/Best-README-Template/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/othneildrew/Best-README-Template/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

## Contributors

<p align="center">
  <a href="https://github.com/Hex-commits">
    <img src="https://avatars.githubusercontent.com/Hex-commits?s=120" width="80" alt="Jan-Philipp Wegmeyer"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/randywf">
    <img src="https://avatars.githubusercontent.com/randywf?s=120" width="80" alt="Randy Flores"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/pmunding">
    <img src="https://avatars.githubusercontent.com/pmunding?s=120" width="80" alt="Philipp Mundinger"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/nimesh7814">
    <img src="https://avatars.githubusercontent.com/nimesh7814?s=120" width="80" alt="Nimesh Akalanka"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/laurenfissel11-ux">
    <img src="https://avatars.githubusercontent.com/laurenfissel11-ux?s=120" width="80" alt="Lauren"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/Aadilwaris">
     <img src="https://avatars.githubusercontent.com/Aadilwaris?s=120" width="80" alt="Adil Waris"/>
  </a>
</p>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

### Built With

![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Isochrone](https://img.shields.io/badge/Isochrone-Routing-green)
![Stack Overflow](https://img.shields.io/badge/StackOverflow-Used-orange)

## Description of the application

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

   Or using uvicorn directly:
   ```sh
   uvicorn app:app --reload
   ```

Note: You'll need a PostgreSQL/PostGIS database running separately.

## Services

The Docker setup includes:

- **API** (port 8000): FastAPI application
- **PostGIS** (port 5432): PostgreSQL with PostGIS extension
- **pgAdmin** (port 5050): Database administration interface
  - Email: admin@admin.de
  - Password: admin

Once started, the API will be available at:

| Service                         | URL                           |
|---------------------------------|-------------------------------|
| API Root                        | http://localhost:8000         |
| Interactive API Docs (Swagger)  | http://localhost:8000/docs    |
| Alternative API Docs (ReDoc)    | http://localhost:8000/redoc   |

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
```

<hr>

<div align="center" style="font-size: 0.85em; color: #666; line-height: 1.6;">

© 2026 <strong>15-min-city</strong><br>
<strong>Course:</strong> Geoinformation in Society<br>
<strong>Responsible:</strong> Contact contributors<br>
<strong>Date:</strong> 02.02.2026<br>
<strong>University of Münster</strong>

</div>
