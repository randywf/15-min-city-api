from typing import List
import httpx
from .overpass_models import OverpassResponse, OverpassElement
from enum import Enum
import asyncio

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


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


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
