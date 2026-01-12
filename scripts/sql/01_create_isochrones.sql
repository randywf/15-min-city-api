BEGIN;

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS isochrones (
    id BIGSERIAL PRIMARY KEY,

    mode TEXT NOT NULL,
    time_seconds INTEGER NOT NULL,

    origin GEOMETRY(Point, 4326) NOT NULL,
    geom GEOMETRY(Polygon, 4326) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT isochrones_unique
        UNIQUE (mode, time_seconds, origin)
);

CREATE INDEX IF NOT EXISTS idx_isochrones_origin
    ON isochrones
    USING GIST (origin);

CREATE INDEX IF NOT EXISTS idx_isochrones_geom
    ON isochrones
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_isochrones_created_at
    ON isochrones (created_at);


COMMIT;