import json
import toml
from fastapi import FastAPI, Query
from functions.reachability import Mode, calculate_isochrone, MODES, TIME_DEFAULT

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
def endpoint_b():
    return  # run_func_b()
