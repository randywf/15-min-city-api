import asyncio
import logging
import math
import os
import geojson
import pyproj
from shapely.geometry import Polygon, Point
from sqlalchemy import create_engine, Engine, text
import geopandas as gpd

# Add the project root to the Python path
from pathlib import Path
import sys

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
from functions.poi import get_amenities_in_polygon

# Load environment variables
from dotenv import load_dotenv

SECTION_SIZE = 2000
SOURCE_CRS = pyproj.CRS("EPSG:25832")
TARGET_CRS = pyproj.CRS("EPSG:4326")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POSTGRES_CONNECTION_STRING = os.getenv("DATABASE_URL")


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
    # Divide the muenster boundary into SECTION_SIZE x SECTION_SIZE meter ections
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


def transfer_amenities_to_database(amenities: list[dict], engine: Engine):
    # Create a geopandas dataframe to transfer amenities to the database
    amenities_df = gpd.GeoDataFrame(amenities, geometry="geometry")
    logger.info("Transferring amenities to database")

    with engine.connect() as conn:
        for _, row in amenities_df.iterrows():
            # Convert geometry to WKT for PostGIS
            geom_wkt = row.geometry.wkt

            upsert_sql = text(
                """
                INSERT INTO amenities (id, geometry, name, amenity, cuisine)
                VALUES (:id, ST_GeomFromText(:geom, 4326), :name, :amenity, :cuisine)
                ON CONFLICT (id) 
                DO UPDATE SET
                    geometry = EXCLUDED.geometry,
                    name = EXCLUDED.name,
                    amenity = EXCLUDED.amenity,
                    cuisine = EXCLUDED.cuisine
            """
            )

            conn.execute(
                upsert_sql,
                {
                    "id": row.get("id"),
                    "geom": geom_wkt,
                    "name": row.get("name"),
                    "amenity": row.get("amenity"),
                    "cuisine": row.get("cuisine"),
                },
            )
        conn.commit()

    logger.info("Amenities transferred to database")


if __name__ == "__main__":
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
    all_amenities = asyncio.run(download_amenities(transformed_boundary_sections))
    logger.info(f"Downloaded {len(all_amenities)} amenities")

    # Connect to the database
    logger.info("Connecting to database")
    engine = create_engine(POSTGRES_CONNECTION_STRING)
    logger.info("Database connected")

    # Transfer amenities to the database
    logger.info("Transferring amenities to database")
    transfer_amenities_to_database(all_amenities, engine)
    logger.info("Amenities transferred to database")
