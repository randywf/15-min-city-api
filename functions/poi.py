from typing import List
import httpx
from .overpass_models import OverpassResponse, OverpassElement

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

async def fetch_overpass_data(query: str) -> List[OverpassElement]:
    """Send Overpass QL to the Overpass API and return the list of elements."""
    data = {"data": query}  # form field 'data'

    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.post(OVERPASS_URL, data=data)

    if response.status_code != 200:
        raise RuntimeError(
            f"Overpass error {response.status_code}: {response.text[:200]}"
        )

    json_data = response.json()
    parsed = OverpassResponse.model_validate(json_data)
    return parsed.elements

PARK_POLYGON_COORDS = "51.968 7.625 51.970 7.635 51.965 7.638 51.963 7.628 51.968 7.625"

async def get_cafes_in_park_polygon() -> list[OverpassElement]:
    cafe_query = f"""
        [out:json][timeout:25];
        node
            ["amenity"="cafe"]
            (poly:"{PARK_POLYGON_COORDS}");
        out geom;
    """

    print("Running Query for Cafes within Polygon...")
    cafes = await fetch_overpass_data(cafe_query)
    print(f"Found {len(cafes)} cafes in the polygon area.")

    for cafe in cafes[:5]:
        name = cafe.tags.name or "Unnamed Cafe"
        print(f"  - {name} at {cafe.lat}, {cafe.lon}")

    return cafes