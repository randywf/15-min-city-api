import argparse
import asyncio
import logging
import os
import geojson
import pyproj
from shapely.geometry import Polygon, Point
from sqlalchemy import create_engine, Engine, text
import geopandas as gpd
from pathlib import Path
import sys
from functions.poi import get_amenities_in_polygon
from dotenv import load_dotenv

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

load_dotenv()

SOURCE_CRS = pyproj.CRS("EPSG:25832")
TARGET_CRS = pyproj.CRS("EPSG:4326")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POSTGRES_CONNECTION_STRING = os.getenv("DATABASE_URL")


def load_muenster_boundary() -> Polygon:
    """

    :return: Polygon of the relevant city, Muenster.
    """
    logger.info("Loading Münster boundary")

    with open(
        root_dir / "data" / "muenster" / "muenster_administrative_boundary.geojson"
    ) as f:
        boundary = geojson.load(f)

    return Polygon(boundary["features"][0]["geometry"]["coordinates"][0][0])


def reproject_polygon(polygon: Polygon) -> Polygon:
    """
    Reproject a polygon from its boundary to a EPSG:4326 CRS.
    :param polygon: Polygon to reproject.
    :return: Reprojected polygon.
    """
    logger.info("Reprojecting boundary to EPSG:4326")

    transformer = pyproj.Transformer.from_crs(
        SOURCE_CRS, TARGET_CRS, always_xy=True
    )

    transformed_coords = [
        transformer.transform(x, y) for x, y in polygon.exterior.coords
    ]

    return Polygon(transformed_coords)


def polygon_to_overpass_string(polygon: Polygon) -> str:
    """
    Overpass requires non-standard-Format of data.
    :param polygon: Polygon.
    :return: Overpass string.
    """
    # Overpass expects "lat lon lat lon ..."
    return " ".join(
        f"{lat:.6f} {lon:.6f}"
        for lon, lat in polygon.exterior.coords[:-1]
    )


async def get_amenities_from_overpass(boundary: Polygon) -> list[dict]:
    """
    In order to being able to process distance and further filtering, aswell as simply storing mostly static data.

    :param boundary: Polygon-Boundary where the POIs are being fetched for.
    :return: List of amenity POIs in the area.
    """
    logger.info("Downloading amenities for full boundary")

    coords = polygon_to_overpass_string(boundary)
    amenities = await get_amenities_in_polygon(coords)

    logger.info(f"Found {len(amenities)} amenities")

    return [
        {
            "id": amenity.id,
            "geometry": Point(amenity.lon, amenity.lat),
            "name": amenity.tags.name,
            "amenity": amenity.tags.amenity,
            "cuisine": amenity.tags.cuisine,
        }
        for amenity in amenities
    ]


def transfer_amenities_to_database(amenities: list[dict], engine: Engine):
    """
    Transfers amenities into database.
    :param amenities: List of amenities.
    :param engine: SQLAlchemy engine.
    """
    logger.info("Transferring amenities to database")

    df = gpd.GeoDataFrame(amenities, geometry="geometry", crs="EPSG:4326")

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

    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(
                upsert_sql,
                {
                    "id": row.id,
                    "geom": row.geometry.wkt,
                    "name": row.name,
                    "amenity": row.amenity,
                    "cuisine": row.cuisine,
                },
            )

    logger.info("Amenities transferred successfully")


def has_amenities_data(engine: Engine) -> bool:
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT EXISTS (SELECT 1 FROM amenities)")
        ).scalar()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    engine = create_engine(POSTGRES_CONNECTION_STRING)

    if not args.update and has_amenities_data(engine):
        logger.info("Amenities already present — skipping")
        sys.exit(0)

    boundary = load_muenster_boundary()
    boundary = reproject_polygon(boundary)

    amenities = asyncio.run(get_amenities_from_overpass(boundary))
    transfer_amenities_to_database(amenities, engine)
