import httpx
from .overpass_models import OverpassResponse, OverpassElement
from enum import Enum
import asyncio
from shapely.geometry import Polygon, Point
from sqlalchemy import text, Engine
from typing import List, Union, Dict, Any

# Define a polygon around a park (example coordinates)
PARK_POLYGON_COORDS = "51.968 7.625 51.970 7.635 51.965 7.638 51.963 7.628 51.968 7.625"


class Amenity(Enum):
    # --- Mobility ---
    BICYCLE_PARKING = "bicycle_parking"
    PARKING = "parking"
    FUEL = "fuel"

    # --- Health ---
    CLINIC = "clinic"
    HOSPITAL = "hospital"
    PHARMACY = "pharmacy"

    # --- Education & Culture ---
    SCHOOL = "school"
    LIBRARY = "library"
    THEATRE = "theatre"
    CINEMA = "cinema"

    # --- Religious Places ---
    CHURCH = "place_of_worship:christian"
    MOSQUE = "place_of_worship:islamic"
    BUDDHIST_TEMPLE = "place_of_worship:buddhist"
    HINDU_TEMPLE = "place_of_worship:hindu"
    SYNAGOGUE = "place_of_worship:jewish"

    # --- Food & Drinks ---
    RESTAURANT = "restaurant"
    BAR = "bar"
    BBQ = "bbq"
    BIERGARTEN = "biergarten"
    CAFE = "cafe"
    FAST_FOOD = "fast_food"
    FOOD_COURT = "food_court"
    ICE_CREAM = "ice_cream"
    PUB = "pub"

    # --- Other ---
    TOILETS = "toilets"


AMENITY_CATEGORIES = {
    "mobility": {
        "rank": 10,
        "amenities": [
            Amenity.BICYCLE_PARKING,
            Amenity.PARKING,
            Amenity.FUEL,
        ],
    },
    "health": {
        "rank": 20,
        "amenities": [
            Amenity.CLINIC,
            Amenity.HOSPITAL,
            Amenity.PHARMACY,
        ],
    },
    "education_and_culture": {
        "rank": 30,
        "amenities": [
            Amenity.SCHOOL,
            Amenity.LIBRARY,
            Amenity.THEATRE,
            Amenity.CINEMA,
        ],
    },
    "religious_places": {
        "rank": 40,
        "amenities": [
            Amenity.CHURCH,
            Amenity.MOSQUE,
            Amenity.BUDDHIST_TEMPLE,
            Amenity.HINDU_TEMPLE,
            Amenity.SYNAGOGUE,
        ],
    },
    "food_and_drinks": {
        "rank": 50,
        "amenities": [
            Amenity.RESTAURANT,
            Amenity.BAR,
            Amenity.BBQ,
            Amenity.BIERGARTEN,
            Amenity.CAFE,
            Amenity.FAST_FOOD,
            Amenity.FOOD_COURT,
            Amenity.ICE_CREAM,
            Amenity.PUB,
        ],
    },
    "other": {
        "rank": 99,
        "amenities": [
            Amenity.TOILETS,
        ],
    },
}



OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def build_default_amenity_state() -> Dict[str, Any]:
    """
    Returns a frontend-ready amenity state structure.
    """
    state: Dict[str, Any] = {}

    for category, cfg in AMENITY_CATEGORIES.items():
        state[category] = {
            "rank": cfg["rank"],
            "enabled": True,
            "amenities": {
                amenity.value: {"enabled": True}
                for amenity in cfg["amenities"]
            },
        }

    return state

def extract_enabled_amenities(state: dict) -> list[str]:
    enabled = []

    for category in state.values():
        if not category.get("enabled", False):
            continue

        for amenity, cfg in category["amenities"].items():
            if cfg.get("enabled", False):
                enabled.append(amenity)

    return enabled


async def fetch_overpass_data(query: str) -> List[OverpassElement]:
    """Send Overpass QL to the Overpass API (with retry strategy)."""

    max_timeout_retries = 4
    max_rate_limit_retries = 4
    timeout_delay_seconds = 2
    rate_limit_delay_seconds = 60

    num_timeouts = 0
    num_rate_limits = 0
    while (
        num_timeouts < max_timeout_retries and num_rate_limits < max_rate_limit_retries
    ):
        try:
            print(f"➡️ Attempt {num_timeouts + num_rate_limits + 1}...")

            async with httpx.AsyncClient(timeout=50.0) as client:
                response = await client.post(OVERPASS_URL, data={"data": query})

            # Check HTTP status
            if response.status_code == 200:
                # Success → parse and return
                json_data = response.json()
                parsed = OverpassResponse.model_validate(json_data)
                return parsed.elements
            elif response.status_code == 504:
                print(
                    f"⚠️ Overpass Timeout (504). Retrying in {timeout_delay_seconds}s..."
                )
                await asyncio.sleep(timeout_delay_seconds)
                timeout_delay_seconds *= 2
                num_timeouts += 1
            elif response.status_code == 429:
                print(
                    f"⚠️ Overpass Rate Limit Exceeded (429). Retrying in {rate_limit_delay_seconds}s..."
                )
                await asyncio.sleep(rate_limit_delay_seconds)
                rate_limit_delay_seconds *= 2
                num_rate_limits += 1
            else:
                # Any other error → no retry, raise
                raise RuntimeError(
                    f"❌ Overpass error {response.status_code}: {response.text[:200]}"
                )

        except (httpx.ConnectError, httpx.ReadTimeout):
            # Retry for network errors
            print(f"⚠️ Network error. Retrying in {timeout_delay_seconds}s...")
            await asyncio.sleep(timeout_delay_seconds)
            timeout_delay_seconds *= 2
            num_timeouts += 1

    # If all retries failed, raise error:
    raise RuntimeError(
        f"❌ All {num_timeouts + num_rate_limits} retry attempts failed for Overpass query."
    )



async def get_amenities_in_polygon_postgres(
    engine: Engine,
    polygon: Polygon,
    query_point: Point,
    amenity_state: dict,
):
    enabled_amenities = extract_enabled_amenities(amenity_state)

    if not enabled_amenities:
        return []

    polygon_wkt = polygon.wkt
    lon, lat = query_point.x, query_point.y

    sql = text("""
               WITH ranked AS (SELECT id,
                                      name,
                                      amenity,
                                      cuisine,
                                      geometry,
                                      ST_Distance(
                                              geometry::geography,
                                              ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                                      ) AS         distance,
                                      ROW_NUMBER() OVER (
                    PARTITION BY amenity
                    ORDER BY geometry <-> ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                ) AS rn
                               FROM amenities
                               WHERE amenity = ANY (:enabled_amenities)
                                 AND ST_Within(
                                       geometry,
                                       ST_GeomFromText(:polygon_wkt, 4326)
                                     ))
               SELECT id,
                      name,
                      amenity,
                      cuisine,
                      ST_Y(geometry) AS lat,
                      ST_X(geometry) AS lon,
                      distance
               FROM ranked
               WHERE rn <= 2
               ORDER BY amenity, distance;
               """)

    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {
                "lon": lon,
                "lat": lat,
                "polygon_wkt": polygon_wkt,
                "enabled_amenities": enabled_amenities,
            }
        )

        return result.mappings().all()



async def get_amenities_in_polygon(polygon: str) -> list[OverpassElement]:
    """
    Get amenities in a polygon.
    Args:
        polygon: The polygon to get amenities in (format: "lat lon lat lon ...").
    Returns:
        A list of Overpass elements.
    """
    amenity_regex = "|".join(a.value for a in Amenity)

    query = f"""
    [out:json][timeout:80];

    node
      ["amenity"~"^({amenity_regex})$"]
      (poly:"{polygon}");

    out geom;
    """

    print("Overpass query:")
    print(query)

    elements = await fetch_overpass_data(query)
    print(f"Found: {len(elements)} amenities")

    return elements

def get_all_pois_postgres(engine: Engine):
    """
    Get all pois for heatmap
    :param engine:
    :return:
    """
    sql = text("""
        SELECT
            id,
            name,
            amenity,
            cuisine,
            ST_Y(geometry) AS lat,
            ST_X(geometry) AS lon
        FROM amenities
        ORDER BY amenity, name;
    """)

    with engine.connect() as conn:
        result = conn.execute(sql)
        return result.mappings().all()
