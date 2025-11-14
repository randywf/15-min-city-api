from geojson import Polygon
from typing import Literal

# Type alias for modes
Mode = Literal["walk", "bike", "car"]


# Constants
MODES: list[Mode] = ["walk", "bike", "car"]
TIME_DEFAULT = 900


def calculate_isochrone(
    longitude: float,
    latitude: float,
    mode: Mode,
    time: int,
) -> dict[str, Polygon]:
    """
    Calculate the isochrone for a given longitude and latitude.
    """
    placeholder_polygon = Polygon(
        [
            [longitude + 0.01, latitude + 0.01],
            [longitude + 0.01, latitude - 0.01],
            [longitude - 0.01, latitude - 0.01],
            [longitude - 0.01, latitude + 0.01],
            [longitude + 0.01, latitude + 0.01],
        ]
    )
    return {"isochrone": placeholder_polygon}
