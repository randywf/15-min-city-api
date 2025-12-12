import geojson
import os
from shapely.geometry import Polygon
from sqlalchemy import create_engine
import geopandas as gpd

# Add the project root to the Python path
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from functions.poi import get_amenities_in_polygon

# Load environment variables
from dotenv import load_dotenv

load_dotenv()
POSTGIS_USERNAME = os.getenv("POSTGIS_USERNAME")
POSTGIS_PASSWORD = os.getenv("POSTGIS_PASSWORD")
POSTGIS_DATABASE = os.getenv("POSTGIS_DATABASE")
POSTGIS_HOST = os.getenv("POSTGIS_HOST")
POSTGIS_PORT = os.getenv("POSTGIS_PORT")

# Open the muenster administrative boundary geojson and convert to a polygon
muenster_boundary = geojson.load(open("data/muenster/muenster_boundary.geojson"))
muenster_boundary_polygon = Polygon(muenster_boundary["geometry"]["coordinates"][0])

# Divide the muenster boundary into 1000x1000 meter sections
min_x, min_y, max_x, max_y = muenster_boundary_polygon.bounds
boundary_sections = []
for x in range(min_x, max_x, 1000):
    for y in range(min_y, max_y, 1000):
        square_polygon = Polygon(
            [(x, y), (x + 1000, y), (x + 1000, y + 1000), (x, y + 1000)]
        )
        if muenster_boundary_polygon.contains(square_polygon):
            # Clip the square polygon to the muenster boundary polygon
            clipped_polygon = square_polygon.intersection(muenster_boundary_polygon)
            boundary_sections.append(clipped_polygon)

# Connect to the database
conn_str = f"postgresql://{POSTGIS_USERNAME}:{POSTGIS_PASSWORD}@{POSTGIS_HOST}:{POSTGIS_PORT}/{POSTGIS_DATABASE}"
engine = create_engine(conn_str)

# Download amenity POIs for each boundary section
all_amenities = []
for section in boundary_sections:
    amenities = get_amenities_in_polygon(section)
    all_amenities.extend(amenities)

# Create a geopandas dataframe to transfer amenities to the database
amenities_df = gpd.GeoDataFrame(all_amenities, geometry="geometry")
amenities_df.to_postgis(name="amenities", con=engine, if_exists="replace")
