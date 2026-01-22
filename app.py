import json
import toml
from fastapi import FastAPI, Query, HTTPException, Body
from shapely import Point, Polygon
from shapely.geometry import shape

from functions.reachability import Mode, calculate_isochrone, MODES, TIME_DEFAULT
from functions.overpass_models import OverpassElement
from functions.poi import (
    get_amenities_in_polygon,
    get_amenities_in_polygon_postgres,
    build_default_amenity_state,
    get_all_pois_postgres,
)
from typing import List, Literal, Any
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Engine

from functions.scoring import calculate_score

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
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_db_engine() -> Engine:
    return create_engine(
        "postgresql+psycopg2://admin:admin@postgis:5432/gisdb",
        echo=False,
        future=True,
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

@app.get("/amenities")
async def get_amenities():
    """
       Returns an ordered list with all amenities.:
       - amenities: list of POIs
       Function to get predived/preordered list of all amenities.
       Important to be able to request amenities_ordered_by_relevance in point_to_poi endpoint.
       """
    return build_default_amenity_state()


@app.get("/heatmap_pois")
def get_heatmap_pois():
    """
       Returns an ordered list with all amenities.:
       - amenities: list of POIs
       """
    engine = create_db_engine()
    return get_all_pois_postgres(engine)

@app.post("/point_to_poi")
async def point_to_poi(
    longitude: float = Query(..., description="Longitude of the center point"),
    latitude: float = Query(..., description="Latitude of the center point"),
    mode: Literal["walk", "bike", "car"] = Query(
        "walk", description="Isochrone mode: walk, bike, or car"
    ),
    time: int = Query(600, description="Isochrone time in seconds"),
    amenity_ordered_by_relevance: Any = Body(
        default=build_default_amenity_state(),
        description="Ordered amenity relevance (highest priority first)",
    )
    ,
):
    """
    Returns a dictionary with:
    - amenities: list of POIs
    - score: numeric score
    - polygon: generated isochrone polygonW
    """

    if isinstance(amenity_ordered_by_relevance, str):
        amenity_ordered_by_relevance = json.loads(amenity_ordered_by_relevance)

    engine = create_db_engine()
    # Compute polygon from lon/lat and mode
    polygon = calculate_isochrone(engine, longitude, latitude, mode, time)

    query_point = Point(longitude, latitude)

    # Query amenities inside the generated polygon
    def geojson_to_polygon(geojson: dict[str, Any]) -> Polygon:
        geom = shape(geojson)

        if not isinstance(geom, Polygon):
            raise TypeError(f"Expected Polygon, got {geom.geom_type}")

        return geom

    amenities = await get_amenities_in_polygon_postgres(
        engine,
        geojson_to_polygon(polygon),
        query_point,
        amenity_state=amenity_ordered_by_relevance,
    )  # TODO: Add the filter here aswell.

    # Scoring logic call
    max_distance = max(a["distance"] for a in amenities) if amenities else 1

    score = calculate_score(
        amenities=amenities,
        amenity_state=amenity_ordered_by_relevance,
        max_distance=max_distance,
    )

    return {"amenities": amenities, "score": score, "polygon": polygon}
