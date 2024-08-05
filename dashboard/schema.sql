DROP TABLE IF EXISTS versions;

CREATE TABLE versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sequencescape_version TEXT NOT NULL,
    sequencescape_url TEXT NOT NULL,
    limber_version TEXT NOT NULL,
    limber_url TEXT NOT NULL
);
