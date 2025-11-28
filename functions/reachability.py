from geojson import GeoJSON
from typing import Literal
from pathlib import Path
from r5py import Isochrones, TransportNetwork, TransportMode
from shapely.geometry import Point, MultiPoint, mapping

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

# Global transport network
# TODO: Find a better way to handle this for multiple regions
_base_dir = Path(__file__).parent.parent
muenster_transport_network = TransportNetwork(
    _base_dir / "data" / "muenster" / "muenster-regbez-251127.osm.pbf"
)


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
    isochrones = Isochrones(
        transport_network=muenster_transport_network,
        origins=point,
        isochrones=[time],
        point_grid_resolution=100,
        point_grid_sample_ratio=1.0,
        transport_modes=[MODE_TO_R5PY_TRANSPORT_MODE[mode]],
    )

    multi_point = MultiPoint(isochrones.destinations.geometry)
    return mapping(multi_point.convex_hull)
