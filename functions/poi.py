from typing import List
import httpx
from .overpass_models import OverpassResponse, OverpassElement
from enum import Enum

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
    "Send Overpass QL to the Overpass API and return the list of elements."
    data = {"data": query}  # form field 'data'

    async with httpx.AsyncClient(timeout=50.0) as client:
        response = await client.post(OVERPASS_URL, data=data)

    if response.status_code != 200:
        raise RuntimeError(
            f"Overpass error {response.status_code}: {response.text[:200]}"
        )

    json_data = response.json()
    parsed = OverpassResponse.model_validate(json_data)
    return parsed.elements

# Define a polygon around a park (example coordinates)
PARK_POLYGON_COORDS = "51.968 7.625 51.970 7.635 51.965 7.638 51.963 7.628 51.968 7.625"

async def get_amenities_in_park_polygon() -> list[OverpassElement]:
    amenity_regex = "|".join(a.value for a in Amenity)

    query = f"""
    [out:json][timeout:50];

    node
      ["amenity"~"^({amenity_regex})$"]
      (poly:"{PARK_POLYGON_COORDS}");

    out geom;
    """

    print("Overpass query:")
    print(query)

    elements = await fetch_overpass_data(query)
    print(f"Found: {len(elements)} amenities")

    return elements