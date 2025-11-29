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
    Returns a dictionary with the destinations and isochrones.
    """
    point = Point(longitude, latitude)
    network = load_transport_network("muenster")
    isochrones = Isochrones(
        transport_network=network,
        origins=point,
        isochrones=[time],
        point_grid_resolution=100,
        point_grid_sample_ratio=1.0,
        transport_modes=[MODE_TO_R5PY_TRANSPORT_MODE[mode]]
    )

    # Create convex hull of destinations
    multi = MultiPoint(isochrones.destinations.geometry)
    hull: BaseGeometry = multi.convex_hull

    # Ensure we have a Polygon
    if not isinstance(hull, Polygon):
        # Convert Point or LineString to small Polygon
        hull = hull.buffer(0.001)

    # Extract exterior coordinates and format as 'lat lon lat lon ...'
    coord_string = " ".join(f"{lat:.6f} {lon:.6f}" for lon, lat in hull.exterior.coords)
    return coord_string

