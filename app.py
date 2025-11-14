import json
import toml
from fastapi import FastAPI
from functions.reachability import Mode, calculate_isochrone

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
    longitude: float, latitude: float, mode: Mode = None, time: int = None
):
    return calculate_isochrone(longitude, latitude, mode, time)


@app.get("/poi")
def endpoint_b():
    return  # run_func_b()
