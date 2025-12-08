import json
import toml
from fastapi import FastAPI, Query, HTTPException
from functions.reachability import Mode, calculate_isochrone, MODES, TIME_DEFAULT
from functions.overpass_models import OverpassElement
from functions.poi import get_amenities_in_polygon
from typing import List, Literal
from fastapi.middleware.cors import CORSMiddleware


# Define a polygon around a park (example coordinates)
DEFAULT_POLYGON = "51.968 7.625 51.970 7.635 51.965 7.638 51.963 7.628 51.968 7.625"

# Loading project information from pyproject.toml
pyproject = toml.load("pyproject.toml")
project = pyproject.get("project", {})
title = project.get("name", "API")
description = project.get("description", "")
version = project.get("version", "")

app = FastAPI(
    title=title,
    description=description,
    version=version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/reachability")
def get_reachability(
    longitude: float,
    latitude: float,
    mode: Mode = Query(default=MODES[0]),
    time: int = Query(default=TIME_DEFAULT),
):
    return calculate_isochrone(longitude, latitude, mode, time)


@app.get("/poi", response_model=List[OverpassElement])
async def amenities_in_polygon(
    polygon: str = Query(
        DEFAULT_POLYGON,
        description="Polygon-Koordinaten für Overpass. Wenn leer, wird ein Default verwendet.",
    )
):
    """
    Return amenities for the given polygon area.
    Optional: /poi?polygon=51.96 7.62 51.97 7.63 ...
    Wenn kein polygon angegeben wird → Default wird benutzt.
    """

    amenities = await get_amenities_in_polygon(polygon)
    return amenities


@app.get("/point_to_poi")
async def point_to_poi(
    longitude: float = Query(..., description="Longitude of the center point"),
    latitude: float = Query(..., description="Latitude of the center point"),
    mode: Literal["walk", "bike", "car"] = Query(
        "walk", description="Isochrone mode: walk, bike, or car"
    ),
    time: int = Query(600, description="Isochrone time in seconds"),
):
    """
    Returns a dictionary with:
    - amenities: list of POIs
    - score: numeric score
    - polygon: generated isochrone polygonW
    """

    # Compute polygon from lon/lat and mode
    polygon = calculate_isochrone(longitude, latitude, mode, time)

    # Convert polygon to string format
    polygon_string = " ".join(
        f"{lat:.6f} {lon:.6f}" for lon, lat in polygon["coordinates"][0]
    )

    # Query amenities inside the generated polygon
    amenities = await get_amenities_in_polygon(polygon_string)

    # Example scoring logic
    score = len(amenities)  # TODO: Change this to some meaningful metric

    return {"amenities": amenities, "score": score, "polygon": polygon}
