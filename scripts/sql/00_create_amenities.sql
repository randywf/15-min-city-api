BEGIN;

CREATE TABLE IF NOT EXISTS amenities (
    id BIGINT PRIMARY KEY,
    geometry GEOMETRY(Point, 4326) NOT NULL,
    name TEXT,
    amenity TEXT,
    cuisine TEXT
);

CREATE INDEX IF NOT EXISTS idx_amenities_geometry ON amenities USING GIST (geometry);

COMMIT;