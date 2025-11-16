import json
import toml
from fastapi import FastAPI, Query
from functions.reachability import Mode, calculate_isochrone, MODES, TIME_DEFAULT
from functions.poi import get_poi

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


@app.get("/reachability")
def get_reachability(
    longitude: float,
    latitude: float,
    mode: Mode = Query(default=MODES[0]),
    time: int = Query(default=TIME_DEFAULT),
):
    return calculate_isochrone(longitude, latitude, mode, time)


@app.get("/poi")
def poi_endpoint(
    longitude: float,
    latitude: float,
    mode: str = Query(default="walk"),
    time: int = Query(default=900),
    poi_type: str = Query(default=None),
):
    return get_poi(longitude, latitude, mode, time, poi_type)