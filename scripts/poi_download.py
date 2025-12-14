import asyncio
import logging
import math
import os
import geojson
import pyproj
from shapely.geometry import Polygon, Point
from sqlalchemy import create_engine
import geopandas as gpd

# Add the project root to the Python path
from pathlib import Path
import sys

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
from functions.poi import get_amenities_in_polygon

# Load environment variables
from dotenv import load_dotenv

load_dotenv()
POSTGIS_USERNAME = os.getenv("POSTGIS_USERNAME")
POSTGIS_PASSWORD = os.getenv("POSTGIS_PASSWORD")
POSTGIS_DATABASE = os.getenv("POSTGIS_DATABASE")
POSTGIS_HOST = os.getenv("POSTGIS_HOST")
POSTGIS_PORT = os.getenv("POSTGIS_PORT")

SECTION_SIZE = 2000
SOURCE_CRS = pyproj.CRS("EPSG:25832")
TARGET_CRS = pyproj.CRS("EPSG:4326")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_muenster_boundary():
    # Open the muenster administrative boundary geojson and convert to a polygon
    muenster_boundary = geojson.load(
        open(
            root_dir / "data" / "muenster" / "muenster_administrative_boundary.geojson"
        )
    )
    muenster_boundary_polygon = Polygon(
        muenster_boundary["features"][0]["geometry"]["coordinates"][0][0]
    )
    return muenster_boundary_polygon


def divide_boundary_into_sections(muenster_boundary_polygon: Polygon):
    # Divide the muenster boundary into 1000x1000 meter sections
    min_x, min_y, max_x, max_y = muenster_boundary_polygon.bounds
    boundary_sections = []
    for x in range(int(math.floor(min_x)), int(math.ceil(max_x)), 1000):
        for y in range(int(math.floor(min_y)), int(math.ceil(max_y)), 1000):
            square_polygon = Polygon(
                [(x, y), (x + 1000, y), (x + 1000, y + 1000), (x, y + 1000)]
            )
            if muenster_boundary_polygon.contains(square_polygon):
                # Clip the square polygon to the muenster boundary polygon
                clipped_polygon = square_polygon.intersection(muenster_boundary_polygon)
                boundary_sections.append(clipped_polygon)
    return boundary_sections


async def download_amenities(boundary_sections: list[Polygon]):
    # Download amenity POIs for each boundary section
    all_amenities = []
    for i, section in enumerate(boundary_sections):
        logger.info(
            f"Downloading amenities for section {i+1} of {len(boundary_sections)}"
        )
        exterior_coords = zip(
            section.exterior.coords.xy[0][:-1], section.exterior.coords.xy[1][:-1]
        )
        coords = " ".join(f"{lat:.6f} {lon:.6f}" for lon, lat in exterior_coords)
        amenities = await get_amenities_in_polygon(coords)
        # Flatten the amenity object, convert lat/lon to point geometry
        flattened = [
            {
                "id": amenity.id,
                "geometry": Point(amenity.lon, amenity.lat),
                "name": amenity.tags.name,
                "amenity": amenity.tags.amenity,
                "cuisine": amenity.tags.cuisine,
            }
            for amenity in amenities
        ]
        all_amenities.extend(flattened)

    return all_amenities


async def main():
    logger.info("Loading muenster boundary polygon")
    muenster_boundary_polygon = load_muenster_boundary()

    logger.info("Dividing muenster boundary into sections")
    boundary_sections = divide_boundary_into_sections(muenster_boundary_polygon)

    # Reproject the boundary sections to lon/lat
    logger.info("Reprojecting boundary sections to lon/lat")
    transformer = pyproj.Transformer.from_crs(SOURCE_CRS, TARGET_CRS, always_xy=True)
    transformed_boundary_sections = []
    for i, section in enumerate(boundary_sections):
        logger.info(f"Reprojecting boundary section {i+1} of {len(boundary_sections)}")
        coords = zip(section.exterior.coords.xy[0], section.exterior.coords.xy[1])
        transformed_coords = [transformer.transform(x, y) for x, y in coords]
        section = Polygon(transformed_coords)
        transformed_boundary_sections.append(section)

    logger.info("Downloading amenities")
    all_amenities = await download_amenities(transformed_boundary_sections)
    logger.info(f"Downloaded {len(all_amenities)} amenities")

    # Connect to the database
    logger.info("Connecting to database")
    conn_str = f"postgresql://{POSTGIS_USERNAME}:{POSTGIS_PASSWORD}@{POSTGIS_HOST}:{POSTGIS_PORT}/{POSTGIS_DATABASE}"
    engine = create_engine(conn_str)
    logger.info("Database connected")

    # Create a geopandas dataframe to transfer amenities to the database
    amenities_df = gpd.GeoDataFrame(all_amenities, geometry="geometry")
    logger.info("Transferring amenities to database")
    amenities_df.to_postgis(name="amenities", con=engine, if_exists="replace")
    logger.info("Amenities transferred to database")


if __name__ == "__main__":
    asyncio.run(main())
