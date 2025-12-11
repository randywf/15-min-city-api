from typing import List
import httpx
from .overpass_models import OverpassResponse, OverpassElement
from enum import Enum
import asyncio

# Define a polygon around a park (example coordinates)
PARK_POLYGON_COORDS = "51.968 7.625 51.970 7.635 51.965 7.638 51.963 7.628 51.968 7.625"


class Amenity(Enum):
    # --- Mobility ---
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

class Shop(Enum):
    SUPERMARKET = "supermarket"
    BAKERY = "bakery"



OVERPASS_URL = "https://overpass-api.de/api/interpreter"


async def fetch_overpass_data(query: str) -> List[OverpassElement]:
    """Send Overpass QL to the Overpass API (with retry strategy)."""

    max_retries = 4
    delay_seconds = 2  # start delay (will increase)

    for attempt in range(1, max_retries + 1):
        try:
            print(f"➡️ Attempt {attempt}...")

            async with httpx.AsyncClient(timeout=50.0) as client:
                response = await client.post(OVERPASS_URL, data={"data": query})

            # Check HTTP status
            if response.status_code == 200:
                # Success → parse and return
                json_data = response.json()
                parsed = OverpassResponse.model_validate(json_data)
                return parsed.elements

            # Retry only if Overpass timed out
            elif response.status_code == 504:
                print(f"⚠️ Overpass Timeout (504). Retrying in {delay_seconds}s...")
            else:
                # Any other error → no retry, raise
                raise RuntimeError(
                    f"❌ Overpass error {response.status_code}: {response.text[:200]}"
                )

        except (httpx.ConnectError, httpx.ReadTimeout):
            # Retry for network errors
            print(f"⚠️ Network error. Retrying in {delay_seconds}s...")

        # Wait before next retry
        await asyncio.sleep(delay_seconds)
        delay_seconds *= 2  # exponential backoff

    # If all retries failed, raise error:
    raise RuntimeError(
        f"❌ All {max_retries} retry attempts failed for Overpass query."
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
    shop_regex = "|".join(s.value for s in Shop)

    query = f"""
    [out:json][timeout:80];

    (
      node
        ["amenity"~"^({amenity_regex})$"]
        (poly:"{polygon}");
      node
        ["shop"~"^({shop_regex})$"]
        (poly:"{polygon}");
    );

    out geom;
    """

    print("Overpass query:")
    print(query)

    elements = await fetch_overpass_data(query)
    print(f"Found: {len(elements)} amenities")

    return elements
