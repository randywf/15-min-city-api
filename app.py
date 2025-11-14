from fastapi import FastAPI
from functions.reachability import Mode, calculate_isochrone

app = FastAPI()


@app.get("/reachability")
def get_reachability(
    longitude: float, latitude: float, mode: Mode = None, time: int = None
):
    return calculate_isochrone(longitude, latitude, mode, time)


@app.get("/poi")
def endpoint_b():
    return  # run_func_b()
