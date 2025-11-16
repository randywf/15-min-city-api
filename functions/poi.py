from functions.reachability import calculate_isochrone
from geojson import Point, Polygon

POIS = [
    {"name": "Central Grocery", "type": "grocery", "longitude": -73.97, "latitude": 40.77},
    {"name": "City Bank", "type": "bank", "longitude": -73.98, "latitude": 40.76},
    {"name": "Coffee Shop", "type": "cafe", "longitude": -73.99, "latitude": 40.78},
]

def get_poi(longitude: float, latitude: float, mode: str = "walk", time: int = 900, poi_type: str = None):
    polygon: Polygon = calculate_isochrone(longitude, latitude, mode, time)["isochrone"]
    
    # For now, just return all POIs (ignore polygon)
    filtered_pois = [poi for poi in POIS if poi_type is None or poi["type"] == poi_type]
    
    return {"poi": filtered_pois}