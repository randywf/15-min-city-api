import os
import sys
from pathlib import Path
import logging
import psycopg2
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

POSTGRES_CONNECTION_STRING = os.getenv("DATABASE_URL")

SQL_DIR = Path(__file__).parent / "sql"
SQL_FILES = SQL_DIR.glob("*.sql")


def create_schema():
    """
    Creates the schema in the database.
    """
    with psycopg2.connect(POSTGRES_CONNECTION_STRING) as conn:
        with conn.cursor() as cursor:
            for sql_file in SQL_FILES:
                logger.info(f"Executing {sql_file}")
                with open(sql_file, "r") as file:
                    cursor.execute(file.read())
            conn.commit()


if __name__ == "__main__":
    logger.info("Creating schema")
    create_schema()
    logger.info("Schema created")
