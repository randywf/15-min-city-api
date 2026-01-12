import sys
sys.argv.append(["--max-memory", "99%"]) # Before r5py for performance

from geojson import GeoJSON
from typing import Literal
from pathlib import Path
from r5py import Isochrones, TransportNetwork, TransportMode
from shapely.geometry import Point, MultiPoint, mapping
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import Polygon

# Type alias for modes
Mode = Literal["walk", "bike", "car"]


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


def load_transport_network(region: str) -> TransportNetwork:
    region_dir = DATA_DIR / region

    # Find the first .osm.pbf file in the folder
    files = list(region_dir.glob("*.osm.pbf"))
    if not files:
        raise FileNotFoundError(f"No .osm.pbf file found for region '{region}'")

    return TransportNetwork(files[0])


def calculate_isochrone(
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
    point = Point(longitude, latitude)
    network = load_transport_network("muenster")
    time_minutes = time / 60
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
    return mapping(multi_point.convex_hull)


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
            time=test_time
        )

        print("Isochrone GeoJSON:")
        print(json.dumps(geojson_polygon, indent=2))
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
