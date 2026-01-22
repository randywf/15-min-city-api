import os
import sys
import logging
import time
from contextlib import contextmanager

from sqlalchemy import Engine, text

sys.argv.append(["--max-memory", "99%"])  # Before r5py for performance

from geojson import GeoJSON
from typing import Literal
from pathlib import Path
from r5py import Isochrones, TransportNetwork, TransportMode
from shapely.geometry import Point, MultiPoint, mapping
import json
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import Polygon
import pyrosm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type alias for modes
Mode = Literal["walk", "bike", "car"]

ISOCHRONE_TTL = "1 day"  # PostgreSQL interval
# Constants
MODES: list[Mode] = ["walk", "bike", "car"]
TIME_DEFAULT = 15

# Map modes to r5py transport modes
MODE_TO_R5PY_TRANSPORT_MODE: dict[Mode, TransportMode] = {
    "walk": TransportMode.WALK,
    "bike": TransportMode.BICYCLE,
    "car": TransportMode.CAR,
}

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

DEBUG_TIMING = os.getenv("DEBUG_TIMING", "false").lower() == "true"


@contextmanager
def timer(label: str):
    if not DEBUG_TIMING:
        yield
        return
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        logger.info(f"[TIMING] {label}: {end - start:.3f} seconds")


def load_transport_network(region: str) -> TransportNetwork:
    region_dir = DATA_DIR / region

    # Find the first .osm.pbf file in the folder
    files = list(region_dir.glob("*.osm.pbf"))
    if not files:
        raise FileNotFoundError(f"No .osm.pbf file found for region '{region}'")

    logger.info(f"Loading from file: {files[0]}")
    return TransportNetwork(files[0])


def calculate_isochrone(
    engine: Engine,
    longitude: float,
    latitude: float,
    mode: Mode,
    time: int,
) -> GeoJSON:
    """
    Calculate the isochrone for a given longitude and latitude.
    Returns a GeoJSON object with the isochrone polygon.
    Args:
        longitude: The longitude of the point.
        latitude: The latitude of the point.
        mode: The mode of transport.
        time: The time in seconds.
    Returns:
        A GeoJSON object with the isochrone polygon.
    """
    time_minutes = time / 60
    point = Point(longitude, latitude)

    # Try to load from DB for caching
    with timer("load_isochrone_from_db"):
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT ST_AsGeoJSON(geom) AS geojson
                    FROM isochrones
                    WHERE
                        mode = :mode
                        AND time_seconds = :time
                        AND ST_Equals(
                            origin,
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                        )
                        AND created_at >= now() - INTERVAL :ttl
                    LIMIT 1
                """
                ),
                {
                    "mode": mode,
                    "time": time,
                    "lon": longitude,
                    "lat": latitude,
                    "ttl": ISOCHRONE_TTL,
                },
            ).fetchone()

            if result:
                return json.loads(result.geojson)

    # Calculate, if not existing.
    with timer("load_transport_network"):
        network = load_transport_network("muenster")

    # Sanity check that the time is not too short.
    if time_minutes < 1:
        logger.warning(f"Time is too short: {time_minutes} minutes")
        geojson = {"type": "Polygon", "coordinates": []}
    else:
        with timer("calculate_isochrone"):
            try:
                isochrones = Isochrones(
                    transport_network=network,
                    origins=point,
                    isochrones=[time_minutes],
                    point_grid_resolution=100,
                    point_grid_sample_ratio=0.3,
                    transport_modes=[MODE_TO_R5PY_TRANSPORT_MODE[mode]],
                )
                # Create convex hull of destinations
                multi_point = MultiPoint(isochrones.destinations.geometry)
                hull = multi_point.convex_hull
                # If empty geometry, return an empty geojson polygon.
                if hull.is_empty:
                    geojson = {"type": "Polygon", "coordinates": []}
                else:
                    geojson = mapping(hull)
            except AttributeError:
                # This usually occurs when it can't find the transport network.
                # Return an empty geojson polygon.
                geojson = {"type": "Polygon", "coordinates": []}

    with timer("save_to_db"):
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO isochrones (
                        mode,
                        time_seconds,
                        origin,
                        geom,
                        created_at
                    )
                    VALUES (
                        :mode,
                        :time,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                        ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326),
                        now()
                    )
                    ON CONFLICT (mode, time_seconds, origin)
                    DO UPDATE SET
                        geom = EXCLUDED.geom,
                        created_at = now()
                """
                ),
                {
                    "mode": mode,
                    "time": time,
                    "lon": longitude,
                    "lat": latitude,
                    "geom": json.dumps(geojson),
                },
            )

    return geojson


if __name__ == "__main__":
    import json

    # Example test values
    test_longitude = 7.625  # Münster city center longitude
    test_latitude = 51.962  # Münster city center latitude
    test_mode: Mode = "walk"  # can be "walk", "bike", or "car"
    test_time = 900  # 15 minutes in seconds

    try:
        geojson_polygon = calculate_isochrone(
            longitude=test_longitude,
            latitude=test_latitude,
            mode=test_mode,
            time=test_time,
        )

        print("Isochrone GeoJSON:")
        print(json.dumps(geojson_polygon, indent=2))
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
